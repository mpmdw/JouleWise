"""Test-only tripwire for accidental host commands (not a security sandbox)."""

from contextlib import contextmanager
import atexit
import functools
import inspect
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest
import uuid


class HostCommandRefused(RuntimeError):
    pass


REFUSALS = []
_DENIED = {"sudo", "systemsetup", "pmset", "caffeinate", "shutdown", "nvram"}
_LAUNCH_WRITES = {"bootstrap", "bootout", "load", "unload", "kickstart", "enable", "disable", "remove"}
# Transparent wrappers run their trailing argument vector as a command (cold review F-3).
_WRAPPERS = {"nohup", "nice", "timeout", "gtimeout", "time", "command", "exec", "builtin", "xargs",
             "stdbuf", "arch", "sandbox-exec", "chroot", "doas", "su", "watch"}
_LAUNCH_EXEC = {"asuser", "bsexec"}
# Shell grouping and substitution open a new simple command (cold review F-3).
_SHELL_OPENERS = ("$(", "`", "(", ")", "{", "}")
_originals = []
_expected = set()
_active_test = None
_report = None
_environment = {}


def _names(value):
    value = os.fsdecode(value)
    # Only command paths are resolved; arguments and custody paths are never opened.
    return {os.path.basename(value), os.path.basename(os.path.realpath(value))}


def simple_commands(command):
    """Tokenize shell command lists without executing or expanding anything."""
    command = os.fsdecode(command)
    for opener in _SHELL_OPENERS:
        command = command.replace(opener, " ; ")
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = "#"
    part = []
    try:
        for token in lexer:
            if token and all(c in ";&|\n" for c in token):
                if part:
                    yield part
                part = []
            else:
                part.append(token)
    except ValueError:
        # A malformed shell command still must not reach a known host executable.
        if part:
            yield part
        return
    if part:
        yield part


def classify(command, *, shell=False, executable=None):
    """Return (basename, argv) refusals; pure classification, no subprocesses."""
    if isinstance(command, (str, bytes)):
        parts = list(simple_commands(command)) if shell else [[os.fsdecode(command)]]
    else:
        parts = [[os.fsdecode(item) for item in command]]
    found = classify([executable]) if shell and executable is not None else []
    for raw in parts:
        argv = list(raw)
        while shell and argv and "=" in argv[0] and not argv[0].startswith(("/", "-")):
            argv.pop(0)
        if not argv:
            if executable is None:
                continue
            argv = [os.fsdecode(executable)]
        names = _names(argv[0])
        if executable is not None and not shell:
            names |= _names(executable)
        if "env" in names:
            rest = argv[1:]
            while rest:
                if rest[0] in ("-u", "--unset", "-C", "--chdir"):
                    rest = rest[2:]
                elif rest[0].startswith("-") or "=" in rest[0]:
                    rest = rest[1:]
                else:
                    break
            found.extend(classify(rest))
            continue
        if names & _WRAPPERS:
            # Classify every trailing suffix: wrapper options are skipped without parsing them.
            for index in range(1, len(argv)):
                inner = classify(argv[index:])
                if inner:
                    found.extend(inner)
                    break
            continue
        denied = sorted(names & _DENIED)
        if denied:
            found.append((denied[0], raw))
        elif "launchctl" in names and len(argv) > 1 and argv[1] in _LAUNCH_WRITES:
            found.append(("launchctl", raw))
        elif "launchctl" in names and len(argv) > 3 and argv[1] in _LAUNCH_EXEC:
            found.extend(classify(argv[3:]))
        elif names & {"networksetup", "scutil"} and any(a.startswith(("-set", "--set")) for a in argv[1:]):
            found.append((sorted(names & {"networksetup", "scutil"})[0], raw))
        elif names & {"sh", "zsh", "bash", "dash", "ksh"}:
            for index, arg in enumerate(argv[1:], 1):
                if arg.startswith("-") and "c" in arg and index + 1 < len(argv):
                    found.extend(classify(argv[index + 1], shell=True))
                    break
    return found


def _check(command, **kwargs):
    found = classify(command, **kwargs)
    if not found:
        return
    frame = inspect.currentframe().f_back
    while frame and frame.f_code.co_filename == __file__:
        frame = frame.f_back
    caller = None if frame is None else {
        "file": frame.f_code.co_filename, "function": frame.f_code.co_name,
        "line": frame.f_lineno,
    }
    argv = [os.fsdecode(command)] if isinstance(command, (str, bytes)) else [os.fsdecode(a) for a in command]
    for name, _simple_argv in found:
        record = {"id": uuid.uuid4().hex, "pid": os.getpid(), "command": name,
                  "argv": argv[:6], "test_id": _active_test, "caller": caller}
        REFUSALS.append(record)
        # One append/write per record also works for concurrent child interpreters.
        fd = os.open(_report, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        try:
            os.write(fd, (json.dumps(record) + "\n").encode())
        finally:
            os.close(fd)
    raise HostCommandRefused("test host command refused: " + ", ".join(n for n, _ in found))


def _snapshot():
    return len(REFUSALS), os.path.getsize(_report)


def _since(snapshot):
    start, offset = snapshot
    records = {r["id"]: r for r in REFUSALS[start:]}
    with open(_report, encoding="utf-8") as stream:
        stream.seek(offset)
        for line in stream:
            record = json.loads(line)
            records[record["id"]] = record
    return [r for r in records.values() if r["id"] not in _expected]


@contextmanager
def expect_refusals():
    """Only the guard's own witnesses may acknowledge deliberate refusals."""
    module = inspect.currentframe().f_back
    # contextlib enters generator contexts on behalf of the actual caller.
    while module and module.f_globals.get("__name__") in (__name__, "contextlib"):
        module = module.f_back
    if module is None or module.f_globals.get("__name__") not in {
        "tests.test_host_command_guard", "test_host_command_guard",
    } or Path(module.f_code.co_filename).resolve() != Path(__file__).with_name("test_host_command_guard.py").resolve():
        raise RuntimeError("expect_refusals is reserved for tests.test_host_command_guard")
    snapshot = _snapshot()
    records = []
    try:
        yield records
    except HostCommandRefused:
        pass
    finally:
        records.extend(_since(snapshot))
        _expected.update(r["id"] for r in records)


def _replace(owner, name, replacement):
    _originals.append((owner, name, getattr(owner, name)))
    setattr(owner, name, replacement)


def _invoke(original, *args, **kwargs):
    return original(*args, **kwargs)


def install():
    global _report
    if _originals:
        return
    for key in ("PYTHONPATH", "JW_TEST_HOST_GUARD_REPORT"):
        _environment[key] = os.environ.get(key)
    _report = os.environ.get("JW_TEST_HOST_GUARD_REPORT")
    if not _report:
        fd, _report = tempfile.mkstemp(prefix="jw-test-host-guard-", suffix=".jsonl")
        os.close(fd)
        owned = _report
        atexit.register(lambda: os.path.exists(owned) and os.unlink(owned))
    os.environ["JW_TEST_HOST_GUARD_REPORT"] = _report
    site = str(Path(__file__).with_name("_host_guard_site"))
    paths = os.environ.get("PYTHONPATH", "").split(os.pathsep)
    os.environ["PYTHONPATH"] = os.pathsep.join([site] + [p for p in paths if p and p != site])

    original_init = subprocess.Popen.__init__

    @functools.wraps(original_init)
    def popen_init(self, args, *positional, **kwargs):
        # Bind positionals too: executable and shell need not be keyword arguments.
        bound = inspect.signature(original_init).bind(self, args, *positional, **kwargs)
        _check(args, shell=bound.arguments.get("shell", False),
               executable=bound.arguments.get("executable"))
        original_init(self, args, *positional, **kwargs)

    _replace(subprocess.Popen, "__init__", popen_init)
    for name in ("system", "posix_spawn", "posix_spawnp", "execl", "execle", "execlp", "execlpe", "execv", "execve", "execvp", "execvpe"):
        if not hasattr(os, name):
            continue
        original = getattr(os, name)

        def make_wrapper(name, original):
            @functools.wraps(original)
            def guarded(*args, **kwargs):
                if name == "system":
                    _check(args[0] if args else kwargs["command"], shell=True)
                else:
                    executable = args[0] if args else kwargs.get("path", kwargs.get("file"))
                    argv = args[1] if len(args) > 1 else kwargs.get("argv")
                    if name.startswith("execl"):
                        argv = args[1:-1] if name.endswith("e") else args[1:]
                    _check(argv, executable=executable)
                return _invoke(original, *args, **kwargs)
            return guarded

        _replace(os, name, make_wrapper(name, original))

    original_run = unittest.TestCase.run

    @functools.wraps(original_run)
    def run(test, result=None):
        global _active_test
        if result is None:
            result = test.defaultTestResult()
        previous, _active_test = _active_test, test.id()
        snapshot = _snapshot()
        try:
            return original_run(test, result)
        finally:
            records = _since(snapshot)
            _active_test = previous
            if records:
                details = "; ".join(f"{r['command']} {r['argv']} ({r['caller']})" for r in records)
                error = AssertionError("host command guard recorded refusal(s): " + details)
                result.addFailure(test, (AssertionError, error, None))

    _replace(unittest.TestCase, "run", run)


def uninstall():
    """For guard unit tests only; ordinary tests must never disable the tripwire."""
    caller = inspect.currentframe().f_back
    if caller.f_globals.get("__name__") not in {
        "tests.test_host_command_guard", "test_host_command_guard",
    } or Path(caller.f_code.co_filename).resolve() != Path(__file__).with_name("test_host_command_guard.py").resolve():
        raise RuntimeError("uninstall is reserved for tests.test_host_command_guard")
    while _originals:
        owner, name, original = _originals.pop()
        setattr(owner, name, original)
    for key, value in _environment.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
