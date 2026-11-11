"""Test-only tripwire for accidental host commands (not a security sandbox)."""

# Child interpreters load this module through sitecustomize at startup, so only what every child needs is
# imported here; the rest is imported where it is used (startup cost; tests.test_b5_driver_p3's meter race).
from contextlib import contextmanager
import functools
import os
import subprocess
import sys


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


_REFUSED_ABSOLUTE = r"/(?:[\w.+-]+/)*(?:sudo|systemsetup|pmset|caffeinate|shutdown|nvram|launchctl|networksetup|scutil)\b"


def _temp_roots():
    import tempfile
    roots = {tempfile.gettempdir(), "/tmp", "/private/tmp", "/var/folders", "/private/var/folders",
             os.environ.get("TMPDIR") or ""}
    return {os.path.realpath(r) for r in roots if r}


def _is_temp_fake(value, path=None):
    """A test's own fake (e.g. a fake ``sudo`` placed on PATH) lives in a temp directory.

    Bare names are resolved through the PATH the child will see; the REAL path must be inside a
    temp root, so a symlink from a temp dir to /usr/bin/sudo is still refused.
    """
    value = os.fsdecode(value)
    import shutil
    found = value if os.sep in value else shutil.which(value, path=path if path is not None else os.environ.get("PATH"))
    if not found or not os.path.isfile(found):
        return False
    real = os.path.realpath(found)
    if not any(real.startswith(root.rstrip(os.sep) + os.sep) for root in _temp_roots()):
        return False
    # A fake that itself names a refused command by absolute path (e.g. `exec /usr/bin/sudo "$@"`)
    # would reach the host through a shell the guard cannot see: it is not treated as a fake.
    try:
        with open(real, "rb") as stream:
            text = stream.read(1 << 20).decode("latin-1")
    except OSError:
        return False
    import re
    return re.search(_REFUSED_ABSOLUTE, text) is None


def _names(value):
    value = os.fsdecode(value)
    # Only command paths are resolved; arguments and custody paths are never opened.
    return {os.path.basename(value), os.path.basename(os.path.realpath(value))}


def simple_commands(command):
    """Tokenize shell command lists without executing or expanding anything."""
    command = os.fsdecode(command)
    for opener in _SHELL_OPENERS:
        command = command.replace(opener, " ; ")
    import shlex
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


def classify(command, *, shell=False, executable=None, path=None):
    """Return (basename, argv) refusals; pure classification, no subprocesses."""
    if isinstance(command, (str, bytes)):
        parts = list(simple_commands(command)) if shell else [[os.fsdecode(command)]]
    else:
        parts = [[os.fsdecode(item) for item in command]]
    found = classify([executable], path=path) if shell and executable is not None else []
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
            found.extend(classify(rest, path=path))
            continue
        if names & _WRAPPERS:
            # Classify every trailing suffix: wrapper options are skipped without parsing them.
            for index in range(1, len(argv)):
                inner = classify(argv[index:], path=path)
                if inner:
                    found.extend(inner)
                    break
            continue
        denied = sorted(names & _DENIED)
        if (denied or "launchctl" in names or names & {"networksetup", "scutil"}) and _is_temp_fake(
                executable if executable is not None and not shell else argv[0], path):
            continue  # the test's own fake executable, resolved inside a temp directory
        if denied:
            found.append((denied[0], raw))
        elif "launchctl" in names and len(argv) > 1 and argv[1] in _LAUNCH_WRITES:
            found.append(("launchctl", raw))
        elif "launchctl" in names and len(argv) > 3 and argv[1] in _LAUNCH_EXEC:
            found.extend(classify(argv[3:], path=path))
        elif names & {"networksetup", "scutil"} and any(a.startswith(("-set", "--set")) for a in argv[1:]):
            found.append((sorted(names & {"networksetup", "scutil"})[0], raw))
        elif names & {"sh", "zsh", "bash", "dash", "ksh"}:
            for index, arg in enumerate(argv[1:], 1):
                if arg.startswith("-") and "c" in arg and index + 1 < len(argv):
                    found.extend(classify(argv[index + 1], shell=True, path=path))
                    break
    return found


def _check(command, **kwargs):
    found = classify(command, **kwargs)
    if not found:
        return
    frame = sys._getframe(1)
    while frame and frame.f_code.co_filename == __file__:
        frame = frame.f_back
    caller = None if frame is None else {
        "file": frame.f_code.co_filename, "function": frame.f_code.co_name,
        "line": frame.f_lineno,
    }
    argv = [os.fsdecode(command)] if isinstance(command, (str, bytes)) else [os.fsdecode(a) for a in command]
    for name, _simple_argv in found:
        import json
        record = {"id": os.urandom(16).hex(), "pid": os.getpid(), "command": name,
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
            import json
            record = json.loads(line)
            records[record["id"]] = record
    return [r for r in records.values() if r["id"] not in _expected]


@contextmanager
def expect_refusals():
    """Only the guard's own witnesses may acknowledge deliberate refusals."""
    from pathlib import Path
    module = sys._getframe(1)
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
        _install_unittest_hook()
        return
    for key in ("PYTHONPATH", "JW_TEST_HOST_GUARD_REPORT"):
        _environment[key] = os.environ.get(key)
    _report = os.environ.get("JW_TEST_HOST_GUARD_REPORT")
    if not _report:
        import atexit
        import tempfile
        fd, _report = tempfile.mkstemp(prefix="jw-test-host-guard-", suffix=".jsonl")
        os.close(fd)
        owned = _report
        atexit.register(lambda: os.path.exists(owned) and os.unlink(owned))
    os.environ["JW_TEST_HOST_GUARD_REPORT"] = _report
    site = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_host_guard_site")
    paths = os.environ.get("PYTHONPATH", "").split(os.pathsep)
    os.environ["PYTHONPATH"] = os.pathsep.join([site] + [p for p in paths if p and p != site])

    original_init = subprocess.Popen.__init__

    @functools.wraps(original_init)
    def popen_init(self, args, *positional, **kwargs):
        # Positionals too: Popen(args, bufsize, executable, stdin, stdout, stderr, preexec_fn, close_fds,
        # shell, cwd, env, ...); executable, shell and env need not be keyword arguments.
        def given(name, index, default=None):
            return kwargs[name] if name in kwargs else (positional[index] if len(positional) > index else default)
        env = given("env", 9)
        _check(args, shell=given("shell", 7, False), executable=given("executable", 1),
               path=None if env is None else env.get("PATH", env.get(b"PATH")))
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

    _install_unittest_hook()


def _install_unittest_hook():
    """Per-test failure. Installed once unittest is loaded (a startup child gets it when it imports tests)."""
    if "unittest" not in sys.modules or any(name == "run" for _owner, name, _o in _originals):
        return
    import unittest
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
    from pathlib import Path
    caller = sys._getframe(1)
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
