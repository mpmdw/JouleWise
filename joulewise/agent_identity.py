"""Which agent-census hits are agent processes: one matcher for every census site.

The agent census (``night_gate.AGENT_CENSUS_ARGV``, ``hazards.arm.AGENT_CENSUS_ARGV``)
is ``pgrep -a -lf '[c]odex|[c]laude|[t]3'``: a regular expression over every
process's whole command line, including the caller's own ancestors (``-a``;
without it Darwin pgrep drops them, and an agent session that launched the
census was invisible: dry-records F1, 2026-10-07).  That list is a superset.  Any id or path that
contains one of the three substrings (``b5-gamma-attempt3``, a custody root under
``.claude``) puts the window's own ``python``, ``zsh`` and ``run_campaign``
processes on it, and the census then stopped the window for a string (Opus
triple audit F3, 2026-10-07).

This module decides each listed process by what the kernel says it is running,
never by its arguments:

* **Executable identity.**  The kernel's executable path for the pid
  (``proc_pidpath`` on Darwin, ``/proc/<pid>/exe`` on Linux) and the process
  name (``argv[0]``).  A process is an agent when either basename starts with
  ``claude`` or ``codex`` (``codex``, ``codex-code-mode-host``, the ChatGPT
  app's bundled ``codex``, the Claude app), starts with ``t3 code`` or
  ``t3code`` (the T3 Code app and its helpers), when the executable sits in a
  ``claude/versions/<version>`` or ``codex/versions/<version>`` install (the
  Claude Code native binary is ``~/.local/share/claude/versions/2.1.289``), or
  when it is a script interpreter (``node``, ``bun``, ``deno``) whose script is
  named ``claude*`` or ``codex*`` (``node /opt/homebrew/bin/codex exec``) or
  whose own arguments (options, their values, inline code, the script) name an
  agent's npm package directory
  (``node .../node_modules/@anthropic-ai/claude-code/cli.js``, ``@openai/codex*``,
  ``claude-code``).  The interpreter's options are parsed, so a preload or
  loader value is never read as the script (Sol delta audit A4); a launch that
  cannot be parsed with confidence is undecided and stays a hit.
* **The caller's own tree.**  With ``own_tree_root`` set, a listed process
  whose parent chain reaches that pid, or whose process group is led by such a
  process, is the window itself and is ignored whatever it runs.  The tree
  runs downward only: the root's ancestors (the agent session or shell that
  launched it, launchd) are not in it and are decided by executable identity
  like any other listed process, so an agent that launched the window stays a
  hit and a shell running ``chain.zsh`` from an ``attempt3`` path does not.

A listed line is decided only when the live process's argument vector, joined
as pgrep joins it, equals the line's text: that proves the line is that pid and
not a reused pid or a line the probe never produced.  A line that cannot be
decided (the process exited, its arguments cannot be read, a stand-in probe
in a test) stays a hit: the census never drops a line it could not identify.

The result keeps the exact text of every kept line and records every ignored
line with its pid, executable and reason, so a census journal shows what was
seen and why it did not count.
"""

from __future__ import annotations

import ctypes
import ctypes.util
import os
import re
import struct
import sys
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Callable

AGENT_PREFIXES = ("claude", "codex", "t3 code", "t3code")
AGENT_INSTALL_DIRS = ("claude", "codex")
SCRIPT_INTERPRETERS = ("node", "bun", "deno")
# An agent's npm package, as a directory of the interpreter's script path
# (cold pass 2 N5): ``node .../@anthropic-ai/claude-code/cli.js`` runs Claude
# Code by its real path, whose basename (``cli.js``) is no agent name.  A
# scope matches only with a package named for its agent; ``claude-code`` also
# matches unscoped.
AGENT_PACKAGE_SCOPES = {"@anthropic-ai": ("claude",), "@openai": ("codex",)}
AGENT_PACKAGE_DIRS = ("claude-code",)
_PID_PREFIX = re.compile(r"([0-9]+) ")


@dataclass(frozen=True)
class ProcessInfo:
    pid: int
    ppid: int | None
    pgid: int | None
    executable: str | None
    argv: tuple[str, ...] | None


@dataclass
class CensusFilter:
    """The decided census: ``kept_text`` is the agent (or undecided) lines verbatim."""

    kept_text: str
    kept: list[dict[str, object]] = field(default_factory=list)
    ignored: list[dict[str, object]] = field(default_factory=list)

    def note(self) -> str:
        """One line for the probe's stderr naming every ignored process."""

        if not self.ignored:
            return ""
        shown = "; ".join(f"pid {item['pid']} {item['reason']} executable={item['executable']}"
                          for item in self.ignored[:20])
        more = f"; … (+{len(self.ignored) - 20} more)" if len(self.ignored) > 20 else ""
        return (f"agent census: {len(self.ignored)} listed process(es) ignored by executable "
                f"identity or own tree: {shown}{more}")


def _basename(text: str | None) -> str:
    return PurePosixPath(text).name.lower() if text else ""


def _agent_name(name: str) -> bool:
    return bool(name) and name.startswith(AGENT_PREFIXES)


# Interpreter launches (Sol delta audit A4, 2026-10-07).  ``node --require
# /tmp/preload.cjs .../@anthropic-ai/claude-code/cli.js`` used to read the
# preload file as the script, so a real Claude Code process read as no agent.
# The interpreter's own arguments are now parsed: an option in the value set
# takes the next argv element as its value (``--option=value`` is always one
# element); an option the flag rules know takes none.  Any other option written
# without ``=`` may or may not consume the next element, so the launch cannot be
# read with confidence and stays undecided (a hit).
_VALUE_OPTIONS = {
    "node": frozenset({
        "-r", "--require", "--import", "--loader", "--experimental-loader", "-C", "--conditions",
        "--inspect-port", "--debug-port", "--env-file", "--env-file-if-exists", "--input-type", "--title",
        "--disable-warning", "--watch-path", "--stack-trace-limit", "--max-http-header-size",
        "--openssl-config", "--icu-data-dir", "--redirect-warnings", "--diagnostic-dir", "--report-dir",
        "--report-directory", "--report-filename", "--report-signal", "--unhandled-rejections",
        "--dns-result-order", "--experimental-config-file", "--localstorage-file",
        "--trace-event-categories", "--trace-event-file-pattern", "--cpu-prof-dir", "--cpu-prof-name",
        "--heap-prof-dir", "--heap-prof-name", "--test-reporter", "--test-reporter-destination",
        "--test-name-pattern", "--secure-heap", "--secure-heap-min", "--heapsnapshot-signal",
        "--max-old-space-size", "--max-semi-space-size", "--stack-size", "--run",
    }),
    "bun": frozenset({
        "-r", "--preload", "--cwd", "-c", "--config", "--env-file", "--tsconfig-override", "-d", "--define",
        "-l", "--loader", "--conditions", "--main-fields", "--extension-order", "--jsx-factory",
        "--jsx-fragment", "--jsx-import-source", "--port", "--elide-lines", "--filter", "-F",
    }),
    "deno": frozenset({
        "-c", "--config", "--import-map", "--location", "--seed", "--cert", "--ext", "-L", "--log-level",
        "--preload",
    }),
}
# Options whose value is inline code: there is no script file to name.
_EVAL_OPTIONS = {"node": frozenset({"-e", "--eval", "-p", "--print"}),
                 "bun": frozenset({"-e", "--eval", "-p", "--print"}),
                 "deno": frozenset()}
# A first positional that names a subcommand, not a script (``bun run x.js``,
# ``bunx``/``bun x <package>``, ``deno run x.ts``); ``deno eval`` takes code.
_SUBCOMMANDS = {"node": frozenset(), "bun": frozenset({"run", "x", "exec"}),
                "deno": frozenset({"run", "x", "eval"})}
_FLAG_OPTIONS = frozenset({
    "-i", "--interactive", "-c", "--check", "--watch", "--test", "--frozen-intrinsics", "--pending-deprecation",
    "--throw-deprecation", "--abort-on-uncaught-exception", "--jitless", "--use-strict", "--zero-fill-buffers",
    "--force-fips", "--prof", "--cpu-prof", "--heap-prof", "--insecure-http-parser", "--v8-options", "-v",
    "--version", "-h", "--help", "-A", "-q", "--quiet", "-r", "--reload", "--hot", "--smol", "--bun",
    "--silent", "--cached-only", "--frozen", "--lock", "--inspect", "--inspect-brk", "--inspect-wait",
    "--preserve-symlinks", "--preserve-symlinks-main", "--deprecation", "--warnings", "--node-memory-debug",
})
_FLAG_PREFIXES = ("--no-", "--experimental-", "--trace-", "--expose-", "--enable-", "--harmony",
                  "--allow-", "--deny-", "--unstable")
_COMPONENT_SPLIT = re.compile(r"""[/\\\s'"`()=,;:]+""")


def _interpreter_kind(names: set[str]) -> str | None:
    for kind in SCRIPT_INTERPRETERS:
        if any(name.startswith(kind) for name in names):
            return kind
    return None


def _flag_option(arg: str) -> bool:
    return arg in _FLAG_OPTIONS or arg.startswith(_FLAG_PREFIXES)


def _interpreter_launch(kind: str, args: tuple[str, ...]) -> tuple[str, list[str]]:
    """How the interpreter was launched, and its own arguments up to the script.

    The form is ``script`` (the region's last element is the script), ``eval``
    (inline code, no script file), ``none`` (options only) or ``unparsed``.
    """

    values, evals, subcommands = _VALUE_OPTIONS[kind], _EVAL_OPTIONS[kind], _SUBCOMMANDS[kind]
    region: list[str] = []
    index, subcommand_seen = 0, False
    while index < len(args):
        arg = args[index]
        region.append(arg)
        if arg == "--":
            if index + 1 < len(args):
                region.append(args[index + 1])
                return "script", region
            return "none", region
        if arg == "-":
            return "unparsed", region  # the script is read from standard input
        if arg.startswith("-"):
            name = arg.split("=", 1)[0]
            if name in evals:
                if "=" not in arg and index + 1 < len(args):
                    region.append(args[index + 1])
                return "eval", region
            if "=" in arg and name.startswith("--"):
                index += 1
            elif arg in values:
                if index + 1 < len(args):
                    region.append(args[index + 1])
                index += 2
            elif _flag_option(arg):
                index += 1
            else:
                return "unparsed", region
            continue
        if not subcommand_seen and arg in subcommands:
            subcommand_seen = True
            if kind == "deno" and arg == "eval":
                region.extend(args[index + 1:index + 2])
                return "eval", region
            index += 1
            continue
        return "script", region
    return "none", region


def _mentions_agent_package(text: str) -> bool:
    """True when any path component sequence in ``text`` is an agent's npm package."""

    parts = [part for part in _COMPONENT_SPLIT.split(text.lower()) if part]
    for index, part in enumerate(parts):
        if part in AGENT_PACKAGE_DIRS:
            return True
        prefixes = AGENT_PACKAGE_SCOPES.get(part)
        if prefixes and index + 1 < len(parts) and parts[index + 1].startswith(prefixes):
            return True
    return False


def identify(executable: str | None, argv: tuple[str, ...] | None) -> str:
    """``agent``, ``not_agent`` or ``undecided`` for one process (see module doc).

    ``undecided`` is an interpreter launch that cannot be read with confidence
    (an unknown option, inline code, a script on standard input); the census
    keeps it as a hit.
    """

    if _agent_name(_basename(executable)):
        return "agent"
    if argv and _agent_name(_basename(argv[0])):
        return "agent"
    if executable:
        parts = [part.lower() for part in PurePosixPath(executable).parts]
        for index in range(len(parts) - 2):
            if parts[index] in AGENT_INSTALL_DIRS and parts[index + 1] == "versions":
                return "agent"
    kind = _interpreter_kind({_basename(executable)} | ({_basename(argv[0])} if argv else set()))
    if not argv or kind is None:
        return "not_agent"
    form, region = _interpreter_launch(kind, tuple(argv[1:]))
    # An agent package anywhere among the interpreter's own arguments (a
    # preload, a loader, inline code, the script) is an agent.
    if any(_mentions_agent_package(token) for token in region):
        return "agent"
    if form == "script":
        script = region[-1]
        return "agent" if _agent_name(_basename(script)) or _agent_package_script(script) else "not_agent"
    return "not_agent" if form == "none" else "undecided"


def is_agent(executable: str | None, argv: tuple[str, ...] | None) -> bool:
    """True unless the process is decided not to be an agent (undecided counts)."""

    return identify(executable, argv) != "not_agent"


def _agent_package_script(script: str) -> bool:
    """True when a directory of ``script`` is an agent's npm package (``@anthropic-ai/claude-code``)."""

    parts = [part.lower() for part in PurePosixPath(script).parts[:-1]]
    for index, part in enumerate(parts):
        if part in AGENT_PACKAGE_DIRS:
            return True
        prefixes = AGENT_PACKAGE_SCOPES.get(part)
        if prefixes and index + 1 < len(parts) and parts[index + 1].startswith(prefixes):
            return True
    return False


# --- kernel reads -----------------------------------------------------------


class _ShortBSDInfo(ctypes.Structure):  # <sys/proc_info.h> struct proc_bsdshortinfo
    _fields_ = [("pid", ctypes.c_uint32), ("ppid", ctypes.c_uint32), ("pgid", ctypes.c_uint32),
                ("status", ctypes.c_uint32), ("comm", ctypes.c_char * 16), ("flags", ctypes.c_uint32),
                ("uid", ctypes.c_uint32), ("gid", ctypes.c_uint32), ("ruid", ctypes.c_uint32),
                ("rgid", ctypes.c_uint32), ("svuid", ctypes.c_uint32), ("svgid", ctypes.c_uint32),
                ("rfu", ctypes.c_uint32)]


_PROC_PIDT_SHORTBSDINFO = 13
_CTL_KERN, _KERN_PROCARGS2 = 1, 49
_libproc = None
_libc = None


def _darwin_libs():
    global _libproc, _libc
    if _libproc is None:
        _libproc = ctypes.CDLL(ctypes.util.find_library("proc"), use_errno=True)
        _libc = ctypes.CDLL(None, use_errno=True)
    return _libproc, _libc


def _darwin_argv(libc, pid: int) -> tuple[str, ...] | None:
    mib = (ctypes.c_int * 3)(_CTL_KERN, _KERN_PROCARGS2, pid)
    size = ctypes.c_size_t(0)
    if libc.sysctl(mib, 3, None, ctypes.byref(size), None, 0) != 0 or size.value < 4:
        return None
    buffer = ctypes.create_string_buffer(size.value)
    if libc.sysctl(mib, 3, buffer, ctypes.byref(size), None, 0) != 0:
        return None
    raw = buffer.raw[:size.value]
    argc = struct.unpack_from("i", raw)[0]
    end = raw.find(b"\0", 4)
    if end < 0:
        return None
    position = end
    while position < len(raw) and raw[position] == 0:
        position += 1
    argv = []
    for _ in range(argc):
        stop = raw.find(b"\0", position)
        if stop < 0:
            return None
        argv.append(raw[position:stop].decode("utf-8", errors="surrogateescape"))
        position = stop + 1
    return tuple(argv)


def _darwin_inspect(pid: int) -> ProcessInfo | None:
    try:
        libproc, libc = _darwin_libs()
    except OSError:
        return None
    info = _ShortBSDInfo()
    if libproc.proc_pidinfo(pid, _PROC_PIDT_SHORTBSDINFO, 0, ctypes.byref(info),
                            ctypes.sizeof(info)) != ctypes.sizeof(info):
        return None
    path = ctypes.create_string_buffer(4096)
    length = libproc.proc_pidpath(pid, path, 4096)
    executable = path.raw[:length].decode("utf-8", errors="surrogateescape") if length > 0 else None
    return ProcessInfo(pid, int(info.ppid), int(info.pgid), executable, _darwin_argv(libc, pid))


def _linux_inspect(pid: int) -> ProcessInfo | None:
    base = f"/proc/{pid}"
    try:
        with open(f"{base}/stat", "rb") as handle:
            stat = handle.read().decode("utf-8", errors="surrogateescape")
    except OSError:
        return None
    fields = stat[stat.rfind(")") + 2:].split()
    try:
        ppid, pgid = int(fields[1]), int(fields[2])
    except (IndexError, ValueError):
        ppid = pgid = None
    try:
        executable = os.readlink(f"{base}/exe")
    except OSError:
        executable = None
    try:
        with open(f"{base}/cmdline", "rb") as handle:
            raw = handle.read()
        argv = tuple(item.decode("utf-8", errors="surrogateescape") for item in raw.split(b"\0")[:-1])
    except OSError:
        argv = None
    return ProcessInfo(pid, ppid, pgid, executable, argv)


def inspect(pid: int) -> ProcessInfo | None:
    """The kernel's view of one pid, or None when it cannot be read (gone, foreign, unsupported)."""

    try:
        if sys.platform == "darwin":
            return _darwin_inspect(pid)
        if sys.platform.startswith("linux"):
            return _linux_inspect(pid)
    except Exception:  # noqa: BLE001 - an unreadable process is undecided, never a crash
        return None
    return None


# --- the census filter ------------------------------------------------------


def in_tree(pid: int, root: int, inspector: Callable[[int], ProcessInfo | None] = inspect,
            info: ProcessInfo | None = None) -> bool:
    """True when ``pid`` is ``root``, descends from it, or its group is led by such a process."""

    def descends(start: int, first: ProcessInfo | None) -> bool:
        candidate, current, seen = start, first, set()
        while candidate > 1 and candidate not in seen:
            if candidate == root:
                return True
            seen.add(candidate)
            current = current if current is not None and current.pid == candidate else inspector(candidate)
            if current is None or current.ppid is None:
                return False
            candidate, current = current.ppid, None
        return candidate == root

    if descends(pid, info):
        return True
    info = info if info is not None else inspector(pid)
    if info is not None and info.pgid and info.pgid != pid and info.pgid > 1:
        return descends(info.pgid, None)
    return False


def filter_census(stdout: str, *, own_tree_root: int | None = None,
                  inspector: Callable[[int], ProcessInfo | None] = inspect) -> CensusFilter:
    """Split ``pgrep -lf`` output into agent (or undecided) lines and ignored lines.

    pgrep prints ``<pid> <argv joined by spaces>`` and an argument may contain
    newlines, so a record can span lines.  A record is decided only when the
    live pid's joined argv equals the text after ``<pid> `` up to a line end;
    everything else is kept line by line, as before.
    """

    kept_chunks: list[str] = []
    result = CensusFilter("")
    position = 0
    while position < len(stdout):
        match = _PID_PREFIX.match(stdout, position)
        if match:
            pid = int(match.group(1))
            info = inspector(pid)
            if info is not None and info.argv:
                body = " ".join(info.argv)
                start = match.end()
                stop = start + len(body)
                if stdout.startswith(body, start) and (stop == len(stdout) or stdout[stop] == "\n"):
                    record_end = stop + 1 if stop < len(stdout) else stop
                    record = stdout[position:record_end]
                    entry = {"pid": pid, "executable": info.executable,
                             "process_name": info.argv[0] if info.argv else None}
                    verdict = identify(info.executable, info.argv)
                    if own_tree_root is not None and in_tree(pid, own_tree_root, inspector, info):
                        result.ignored.append({**entry, "reason": "own_tree"})
                    elif verdict != "not_agent":
                        result.kept.append({**entry, "reason": "agent_executable" if verdict == "agent"
                                            else "undecided_launch"})
                        kept_chunks.append(record)
                    else:
                        result.ignored.append({**entry, "reason": "not_agent_executable"})
                    position = record_end
                    continue
        newline = stdout.find("\n", position)
        line_end = len(stdout) if newline < 0 else newline + 1
        line = stdout[position:line_end]
        if line.strip():
            kept_chunks.append(line)
            result.kept.append({"pid": int(match.group(1)) if match else None, "executable": None,
                                "process_name": None, "reason": "undecided"})
        position = line_end
    result.kept_text = "".join(kept_chunks)
    return result
