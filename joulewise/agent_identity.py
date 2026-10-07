"""Which agent-census hits are agent processes: one matcher for every census site.

The agent census (``night_gate.AGENT_CENSUS_ARGV``, ``hazards.arm.AGENT_CENSUS_ARGV``)
is ``pgrep -a -lf '[c]odex|[c]laude'``: a regular expression over every
process's whole command line, including the caller's own ancestors (``-a``;
without it Darwin pgrep drops them, and an agent session that launched the
census was invisible: dry-records F1, 2026-10-07).  That list is a superset.  Any id or path that
contains one of the substrings (``b5-gamma-attempt3`` before the T3 prune, a custody root under
``.claude``) puts the window's own ``python``, ``zsh`` and ``run_campaign``
processes on it, and the census then stopped the window for a string (Opus
triple audit F3, 2026-10-07).

This module decides each listed process by what the kernel says it is running:

* **Executable identity.**  The kernel's executable path for the pid
  (``proc_pidpath`` on Darwin, ``/proc/<pid>/exe`` on Linux) and the process
  name (``argv[0]``).  A process is an agent when either basename starts with
  ``claude`` or ``codex`` (``codex``, ``codex-code-mode-host``, the ChatGPT
  app's bundled ``codex``, the Claude app), or when the executable sits in a
  ``claude/versions/<version>`` or ``codex/versions/<version>`` install (the
  Claude Code native binary is ``~/.local/share/claude/versions/2.1.289``).
* **JavaScript runtimes.**  When the executable or process name is a
  JavaScript/TypeScript runtime (a basename starting with ``node``, ``bun`` or
  ``deno``, so ``node22`` and ``bun-1.1`` count), the agent's own code is a
  script the runtime loads, so the runtime's arguments are read, but never
  parsed: the process is an agent when any argument contains a path component
  or word that starts with ``claude`` or ``codex``.  Arguments are cut into
  components at ``/``, ``\\``, whitespace, quotes, brackets and ``= , ; : +``,
  so this covers an npm package directory (``@anthropic-ai/claude-code``,
  ``@openai/codex``), an install directory (``claude/versions``), a launcher
  (``node .../node_modules/.bin/codex mcp-server``), an ``npm exec`` title
  (``npm exec @openai/codex@0.153.3 ...``) and inline code (``-e
  "require('@openai/codex')"``), wherever the argument stands: an option
  value, the script, or after it.  Earlier versions parsed the runtime's
  options to find the script and twice read an option's value as the script
  (Sol delta audit A4, ``--require <preload>``; delta audit 2 R1,
  ``--trace-require-module all``), which made a real agent read as no agent.
  Reading every argument cannot make that mistake.  A runtime that names no
  agent but runs code the command line does not name (a script on standard
  input, ``-``; inline code, ``-e``, ``-p``, ``--eval``, ``--print``,
  ``eval``) is undecided and stays a hit.  Any other runtime is not an agent.
  This rule can over-match only runtime processes; the window runs ``zsh``,
  ``python`` and system tools, never a JavaScript runtime.
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

# T3 Code is no longer an agent control plane (Ed, 2026-10-07: "I've abandoned all t3 integration as a control plane so you can prune all that out").
AGENT_PREFIXES = ("claude", "codex")
AGENT_INSTALL_DIRS = ("claude", "codex")
SCRIPT_INTERPRETERS = ("node", "bun", "deno")
# Runtime arguments that run code no argument names: a script on standard
# input, inline code (node/bun ``-e``/``-p``/``-pe``, ``--eval``, ``--print``;
# ``deno eval``).
UNNAMED_CODE_ARGS = frozenset({"-", "-e", "-p", "-pe", "--eval", "--print", "eval"})
UNNAMED_CODE_PREFIXES = ("--eval=", "--print=")
_COMPONENT_SPLIT = re.compile(r"""[/\\\s'"`()\[\]{}=,;:+]+""")
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


def _interpreter(names: set[str]) -> bool:
    return any(name.startswith(SCRIPT_INTERPRETERS) for name in names)


def _names_agent(text: str) -> bool:
    """True when a path component or word of ``text`` starts with ``claude`` or ``codex``."""

    return any(_agent_name(part) for part in _COMPONENT_SPLIT.split(text.lower()))


def _unnamed_code(arg: str) -> bool:
    return arg in UNNAMED_CODE_ARGS or arg.startswith(UNNAMED_CODE_PREFIXES)


def identify(executable: str | None, argv: tuple[str, ...] | None) -> str:
    """``agent``, ``not_agent`` or ``undecided`` for one process (see module doc).

    ``undecided`` is a JavaScript runtime that names no agent but runs code no
    argument names (a script on standard input, inline code); the census keeps
    it as a hit.
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
    if not argv or not _interpreter({_basename(executable), _basename(argv[0])}):
        return "not_agent"
    # argv[0] is read too: ``npm exec`` retitles its node process with the package it runs.
    if any(_names_agent(arg) for arg in argv):
        return "agent"
    return "undecided" if any(_unnamed_code(arg) for arg in argv[1:]) else "not_agent"


def is_agent(executable: str | None, argv: tuple[str, ...] | None) -> bool:
    """True unless the process is decided not to be an agent (undecided counts)."""

    return identify(executable, argv) != "not_agent"


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
