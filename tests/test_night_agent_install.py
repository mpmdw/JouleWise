"""Transactional installer instrument (D10).

The fake is a subprocess, never a wrapper around real launchctl. Its marker
files track physical job state; its query outcomes determine whether absence
is proven. UNKNOWN requires retention even without a marker. These tests
characterize the instrument and pin the system-Python package imports required
by the uninstall entrypoint.

D10 must-die amendment (lt-31 F1): delete the retained-prior refusal.
"""

import contextlib
import hashlib
import json
import os
import signal
import time
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


LABELS = ("com.joulewise.night", "com.joulewise.night.deadman")
# A normal interpreter startup must not become an injected UNKNOWN under load.
# Keep intentional hangs well beyond this deadline, including in product cells.
FAKE_TIMEOUT = 5
FAKE_HANG_SECONDS = 30


@contextlib.contextmanager
def fixture_process(command, **kwargs):
    """Own the fixture's entire process group, including interrupted adapters."""
    with subprocess.Popen(command, start_new_session=True, **kwargs) as child:
        try:
            yield child
        finally:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.wait(timeout=10)
            # Grandchildren are reaped by their parent or the OS after its exit.
            # Do not let a late fake write race the next cell or root cleanup.
            deadline = time.monotonic() + 10
            while True:
                try:
                    os.killpg(child.pid, 0)
                except ProcessLookupError:
                    break
                if time.monotonic() >= deadline:
                    raise AssertionError("fixture process group survived cleanup")
                time.sleep(0.01)


def run_fixture_process(command, *, timeout=60, **kwargs):
    with fixture_process(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         **kwargs) as child:
        stdout, stderr = child.communicate(timeout=timeout)
        return subprocess.CompletedProcess(command, child.returncode, stdout, stderr)


FAKE_LAUNCHCTL_SOURCE = r'''
import json
import os
import signal
import sys
import time
from pathlib import Path

root = Path(__file__).parent
with (root / "child-masks.jsonl").open("a") as stream:
    stream.write(json.dumps(sorted(signal.pthread_sigmask(signal.SIG_BLOCK, ()))) + "\n")
args = sys.argv[1:]
with (root / "calls.log").open("a", encoding="utf-8") as stream:
    stream.write(" ".join(args) + "\n")
action = args[0]
if action == "bootstrap":
    uid = args[1].split("/")[1]
    label = Path(args[2]).name
    if label.endswith(".plist"):
        label = label[:-6]
elif action in ("bootout", "print"):
    _, uid, label = args[1].split("/", 2)
else:
    print("unsupported fake launchctl action", file=sys.stderr)
    sys.exit(64)

if action == "bootout" and (root / "plist-expectations.json").exists():
    expected = json.loads((root / "plist-expectations.json").read_text())
    observed = {path: Path(path).is_file() for path in expected}
    with (root / "bootout-plists.jsonl").open("a") as stream:
        stream.write(json.dumps({"label": label, "files": observed}) + "\n")
    assert observed == expected, "bootout_before_remove: both plists must survive every bootout"

marker = root / (label + ".loaded")
directives = json.loads((root / "directives.json").read_text(encoding="utf-8"))
directive = directives.get(label, {}).get(action, {})
# Per-operation sequences let a test distinguish admission from verification
# and rollback queries without rewriting executable source.
counter = root / (label + "." + action + ".count")
index = int(counter.read_text()) if counter.exists() else 0
counter.write_text(str(index + 1))
if isinstance(directive, list):
    directive = directive[min(index, len(directive) - 1)] if directive else {}

if directive.get("delay_s"):
    time.sleep(directive["delay_s"])

if action == "print":
    fault = directive.get("fault")
    # Record the fake's query outcome independently of the engine's classifier.
    # A missing marker is not absence evidence when the query itself fails.
    kind = ("LOADED" if fault == "0-with-junk-stderr" else
            "UNKNOWN" if fault in ("hang", 9, 64, 112, "113-with-wrong-label") else
            "LOADED" if marker.exists() else "ABSENT")
    with (root / "queries.jsonl").open("a") as stream:
        stream.write(json.dumps({"label": label, "kind": kind}) + "\n")
    if fault == "hang":
        # One process: no shell/sleep grandchild can outlive the adapter kill.
        ready = root / "hang-ready.tmp"
        ready.write_text(str(os.getpid()))
        ready.replace(root / "hang-ready")
        if "late_clock_file" in directive:
            time.sleep(1)
            Path(directive["late_clock_file"]).write_text(str(directive["late_clock"]))
        time.sleep(directive.get("hang_s", 30))
    elif fault in (9, 64, 112):
        print("injected query error " + str(fault), file=sys.stderr)
        sys.exit(fault)
    elif fault == "113-with-wrong-label":
        print('Bad request.\nCould not find service "wrong.' + label +
              '" in domain for user gui: ' + uid, file=sys.stderr)
        sys.exit(113)
    elif fault == "0-with-junk-stderr":
        print("gui/" + uid + "/" + label + " = {\n}")
        print("injected junk diagnostic", file=sys.stderr)
        sys.exit(0)
    if marker.exists():
        print("gui/" + uid + "/" + label + " = {\n}")
        sys.exit(0)
    print('Bad request.\nCould not find service "' + label +
          '" in domain for user gui: ' + uid, file=sys.stderr)
    sys.exit(113)

# Effect and return code are deliberately separate. In particular, failure
# may load a service and successful bootout may leave a live service behind.
effect = directive.get("loaded", action == "bootstrap")
if effect:
    marker.touch()
elif marker.exists():
    marker.unlink()
if action == "bootstrap" and "probe_receipt" in directive:
    Path(directive["receipt_path"]).write_text(json.dumps(directive["probe_receipt"]))
    Path(directive["receipt_path"] + ".process.json").write_text(json.dumps(
        {"launchd_label": label, "chain_pgid": 999999, "driver_pid": 999998}))
if "clock_file" in directive:
    Path(directive["clock_file"]).write_text(str(directive["clock"]))
if directive.get("signal"):
    os.kill(os.getppid(), getattr(signal, "SIG" + directive["signal"]))
if directive.get("hang_s"):
    time.sleep(directive["hang_s"])
sys.stdout.write(directive.get("stdout", ""))
sys.stderr.write(directive.get("stderr", ""))
sys.exit(directive.get("rc", 0))
'''


class FakeLaunchctl:
    """File-backed subprocess fixture; directives are keyed by label and verb."""

    def __init__(self, root, python=sys.executable):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.executable = self.root / "launchctl-fake"
        self.log = self.root / "calls.log"
        self.directives_path = self.root / "directives.json"
        self.directives_path.write_text("{}", encoding="utf-8")
        self.executable.write_text("#!" + str(python) + "\n" + FAKE_LAUNCHCTL_SOURCE,
                                   encoding="utf-8")
        self.executable.chmod(0o755)

    def directive(self, label, action, **values):
        self.sequence(label, action, values)

    def expect_plists(self, directory, *, uninstall=False):
        paths = [Path(directory) / (label + ".plist") for label in LABELS]
        # D7 permits repeated uninstall after both files are already absent.
        # Freeze the starting presence there; a fresh install must publish both.
        expected = {str(path): path.is_file() if uninstall else True for path in paths}
        (self.root / "plist-expectations.json").write_text(json.dumps(expected))
        (self.root / "bootout-plists.jsonl").write_text("")
        return expected

    def sequence(self, label, action, values):
        directives = json.loads(self.directives_path.read_text(encoding="utf-8"))
        directives.setdefault(label, {})[action] = values
        self.directives_path.write_text(json.dumps(directives), encoding="utf-8")
        counter = self.root / (label + "." + action + ".count")
        if counter.exists():
            counter.unlink()

    def marker(self, label):
        return self.root / (label + ".loaded")

    def set_loaded(self, label, loaded):
        path = self.marker(label)
        if loaded:
            path.touch()
        elif path.exists():
            path.unlink()

    def loaded(self, label):
        """Read the stub's state directly, without executing its print verb."""
        return self.marker(label).exists()

    def calls(self):
        return self.log.read_text().splitlines() if self.log.exists() else []

    def queries(self):
        path = self.root / "queries.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def invoke(self, action, label, uid=None, timeout=5):
        domain = "gui/" + str(os.getuid() if uid is None else uid)
        args = ([domain, str(self.root / (label + ".plist"))]
                if action == "bootstrap" else [domain + "/" + label])
        return run_fixture_process([str(self.executable), action] + args,
                                   text=True, timeout=timeout)


class FakeLaunchctlTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="iw-txn-instrument-", dir="/tmp")
        self.addCleanup(temporary.cleanup)
        self.fake = FakeLaunchctl(Path(temporary.name) / "fake")

    def test_exact_loaded_and_absent_wire_signatures(self):
        # These are pinned wire signatures, not a live OS probe.
        for label in LABELS:
            for loaded in (False, True):
                with self.subTest(label=label, loaded=loaded):
                    self.fake.set_loaded(label, loaded)
                    observed = self.fake.invoke("print", label, uid=501)
                    expected = ((0, "gui/501/" + label + " = {\n}\n", "") if loaded
                                else (113, "", 'Bad request.\nCould not find service "' +
                                      label + '" in domain for user gui: 501\n'))
                    self.assertEqual(expected, (observed.returncode, observed.stdout,
                                                observed.stderr))
                    self.assertEqual({"label": label, "kind": "LOADED" if loaded else "ABSENT"},
                                     self.fake.queries()[-1])
                    self.assertEqual(loaded, self.fake.loaded(label))
        self.assertEqual(["print gui/501/" + label for label in LABELS for _ in range(2)],
                         self.fake.calls())

    def test_query_fault_product_preserves_actual_state(self):
        for label in LABELS:
            other = next(item for item in LABELS if item != label)
            for loaded in (False, True):
                for fault in (9, 64, 112, "113-with-wrong-label", "0-with-junk-stderr"):
                    with self.subTest(label=label, loaded=loaded, fault=fault):
                        self.fake.set_loaded(label, loaded)
                        self.fake.set_loaded(other, not loaded)
                        self.fake.directive(label, "print", fault=fault)
                        before = len(self.fake.calls())
                        observed = self.fake.invoke("print", label)
                        if isinstance(fault, int):
                            expected = (fault, "", "injected query error " + str(fault) + "\n")
                        elif fault == "113-with-wrong-label":
                            expected = (113, "", 'Bad request.\nCould not find service "wrong.' +
                                        label + '" in domain for user gui: ' + str(os.getuid()) + "\n")
                        else:
                            expected = (0, "gui/" + str(os.getuid()) + "/" + label +
                                        " = {\n}\n", "injected junk diagnostic\n")
                        self.assertEqual(expected, (observed.returncode, observed.stdout,
                                                    observed.stderr))
                        self.assertEqual({"label": label, "kind": "LOADED"
                                          if fault == "0-with-junk-stderr" else "UNKNOWN"},
                                         self.fake.queries()[-1])
                        self.assertEqual(loaded, self.fake.loaded(label))
                        self.assertEqual(not loaded, self.fake.loaded(other))
                        self.assertEqual(before + 1, len(self.fake.calls()))
            self.fake.directive(label, "print")

    def test_hung_queries_are_logged_and_preserve_actual_state(self):
        for label in LABELS:
            for loaded in (False, True):
                with self.subTest(label=label, loaded=loaded):
                    self.fake.set_loaded(label, loaded)
                    self.fake.directive(label, "print", fault="hang", hang_s=FAKE_HANG_SECONDS)
                    before = len(self.fake.calls())
                    with self.assertRaises(subprocess.TimeoutExpired):
                        self.fake.invoke("print", label, timeout=FAKE_TIMEOUT)
                    self.assertEqual(loaded, self.fake.loaded(label))
                    self.assertEqual(before + 1, len(self.fake.calls()))

    def test_mutator_product_separates_return_code_from_effect(self):
        for label in LABELS:
            other = next(item for item in LABELS if item != label)
            for action in ("bootstrap", "bootout"):
                for initially_loaded in (False, True):
                    for rc in (0, 5):
                        for effect in (False, True):
                            with self.subTest(label=label, action=action,
                                              initial=initially_loaded, rc=rc, effect=effect):
                                self.fake.set_loaded(label, initially_loaded)
                                self.fake.set_loaded(other, not initially_loaded)
                                self.fake.directive(label, action, rc=rc, loaded=effect,
                                                    stdout="out\n", stderr="diagnostic\n")
                                before = len(self.fake.calls())
                                observed = self.fake.invoke(action, label)
                                self.assertEqual((rc, "out\n", "diagnostic\n"),
                                                 (observed.returncode, observed.stdout, observed.stderr))
                                self.assertEqual(effect, self.fake.loaded(label))
                                self.assertEqual(not initially_loaded, self.fake.loaded(other))
                                self.assertEqual(before + 1, len(self.fake.calls()))

    def test_per_label_query_sequences_distinguish_admission_and_verification(self):
        label, other = LABELS
        self.fake.sequence(label, "print", [{}, {"fault": 9}, {"fault": 112}])
        self.assertEqual([113, 9, 112, 112],
                         [self.fake.invoke("print", label).returncode for _ in range(4)])
        self.assertEqual(113, self.fake.invoke("print", other).returncode)
        self.assertFalse(any(self.fake.loaded(item) for item in LABELS))


class SystemPythonImportTests(unittest.TestCase):
    @unittest.skipUnless(Path("/usr/bin/python3").is_file(), "requires system Python")
    def test_package_import_requires_only_stdlib_and_package_on_system_python(self):
        """Pin the package initialization required by uninstall's -m entrypoint.

        -S disables site initialization and both user and global site packages.
        The origin check also catches dependencies imported from the checkout or
        from a path added by package initialization itself. Running the import
        under the system interpreter catches incompatible syntax and APIs.
        """
        repo = Path(__file__).resolve().parents[1]
        script = r'''
import json
from pathlib import Path
import sys
import sysconfig

repo = Path(sys.argv[1]).resolve()
stdlib = {Path(sysconfig.get_path(name)).resolve()
          for name in ("stdlib", "platstdlib")}
allowed = stdlib | {repo / "joulewise"}
sys.path.insert(0, str(repo))
import joulewise

unexpected = {}
for name, module in tuple(sys.modules.items()):
    origin = getattr(module, "__file__", None)
    if origin is None:
        continue  # Built-in and frozen modules have no filesystem dependency.
    path = Path(origin).resolve()
    if (not any(path == root or root in path.parents for root in allowed)
            or "site-packages" in path.parts or "dist-packages" in path.parts):
        unexpected[name] = str(path)
assert not unexpected, unexpected
assert "site" not in sys.modules
assert "scripts.run_night" not in sys.modules
print(json.dumps({"version": list(sys.version_info[:3]),
                  "package_modules": sorted(name for name in sys.modules
                                            if name == "joulewise"
                                            or name.startswith("joulewise."))}))
'''
        with tempfile.TemporaryDirectory(prefix="iw-txn-system-python-", dir="/tmp") as root:
            completed = subprocess.run(
                ["/usr/bin/python3", "-B", "-S", "-c", script, str(repo)],
                cwd=root,
                env={"PATH": "/usr/bin:/bin", "HOME": root,
                     "PYTHONPATH": str(repo), "PYTHONNOUSERSITE": "1",
                     "PYTHONDONTWRITEBYTECODE": "1", "TMPDIR": "/tmp"},
                capture_output=True, text=True, timeout=30, check=False)
        self.assertEqual(0, completed.returncode, completed.stderr)
        evidence = json.loads(completed.stdout)
        self.assertIn("joulewise", evidence["package_modules"])
        self.assertIn("joulewise.schemas", evidence["package_modules"])

# Old test name -> transaction cell / retained integration assertion. FIX-3..10
# also have owning driver/watchdog assertions; those modules are replayed intact.
FIX_MAPPING = {
    "FIX-1 test_span_close_120101_during_bootout_or_first_bootstrap_rolls_back": "test_span_close_120101_during_first_bootstrap_rolls_back; success-path bootout abolished by D5",
    "FIX-A test_commit_gate_one_boundary": "DEADMAN_LOADED x past_selected",
    "FIX-A test_commit_gate_two_boundaries": "test_commit_crosses_two_boundaries",
    "FIX-A test_commit_gate_plan_cutoff_first": "VERIFIED x past_install",
    "FIX-A test_commit_gate_selected_close_first": "VERIFIED x past_selected",
    "FIX-A test_commit_gate_exactly_at_close": "VERIFIED x exactly_close",
    "FIX-2 test_teardown_failure_matrix": "STATE_PRODUCT x FAULT_PRODUCT x prior/new",
    "FIX-2 test_failed_bootstrap_restores_overwritten_plist_bytes": "NIGHT_LOADED x FAILED x prior",
    "FIX-2 test_teardown_is_idempotent_after_restoring_prior_plists": "test_teardown_reentry_preserves_restored_priors",
    "FIX-2 test_teardown_retains_plists_when_only_one_label_stays_loaded": "test_retention_product",
    "FIX-3 test_schedule_missing_malformed_fields_and_unrepresentable_windows_refuse": "unchanged tests.test_run_night owning assertion",
    "FIX-4 test_window_10_to_400_holds_unsafe_through_installed_and_discovered_plans": "unchanged tests.test_magistrate_watchdog owning assertion",
    "FIX-5 test_installer_refuses_132017_t0_instead_of_rendering_1320": "retained integration assertion",
    "FIX-5 test_installer_refuses_first_20261101_0130_occurrence": "retained integration assertion (both folds)",
    "FIX-6 test_schedule_rejects_dst_inverted_and_overlapping_resolved_spans": "unchanged tests.test_run_night owning assertion",
    "FIX-7 test_now_exactly_span_open_is_accepted_and_exactly_close_is_refused": "retained integration assertion; driver/watchdog boundary assertions unchanged",
    "FIX-8 docs same-day recipe assertions": "lead-owned D9 documentation excluded by R3",
    "FIX-9 docs adoption wording assertions": "lead-owned D9 documentation excluded by R3",
    "FIX-10 docs refusal inventory assertions": "lead-owned D9 documentation excluded by R3",
    "test_term_during_first_restore_preserves_both_priors_and_original_status": "test_repeated_signals_during_restore",
    "test_render_only_second_render_failure_preserves_preloaded_labels": "test_render_product",
    "test_render_only_success_preserves_preloaded_labels": "test_render_product",
    "test_success_removes_backup_without_teardown": "COMMITTED x FAILED (stdout)",
    "test_backup_removal_failure_after_commit_gate_preserves_verified_arm": "test_committed_cleanup_baseexception_preserves_arm",
    "test_clock_advancing_during_backup_removal_preserves_verified_arm": "test_control_clock_advances_during_cleanup",
    "test_uninstall_retains_plists_when_bootout_leaves_loaded_labels": "test_retention_product (uninstall)",
    "test_deadman_only_preloaded_refuses_install_without_bootstraps": "test_occupancy_product",
}

STATE_PRODUCT = ("PARSED", "VALIDATED", "ADMITTED", "STAGED", "PUBLISHED",
                 "NIGHT_LOADED", "DEADMAN_LOADED", "VERIFIED", "COMMITTED",
                 "SUCCESS", "REFUSED", "ROLLED_BACK", "RETAINED")
FAULT_PRODUCT = ("FAILED", "UNKNOWN", "INT", "TERM", "HUP", "exactly_close",
                 "past_selected", "past_install", "render_PermissionError", "restore_IOError",
                 "BrokenPipeError_at_shutdown")


def unreachable_reason(state, fault):
    if state in ("SUCCESS", "REFUSED", "ROLLED_BACK", "RETAINED"):
        return "terminal result: no next transaction operation"
    if fault == "BrokenPipeError_at_shutdown" and state != "COMMITTED":
        return "the success line is written only after COMMITTED"
    if fault == "render_PermissionError" and state != "STAGED":
        return "rendering occurs only in STAGED, before PUBLISHED"
    if fault == "restore_IOError" and state not in ("STAGED", "PUBLISHED", "NIGHT_LOADED", "DEADMAN_LOADED", "VERIFIED"):
        return "this state's teardown never restores a plist"
    if fault == "UNKNOWN" and state in ("PARSED", "ADMITTED", "STAGED", "VERIFIED", "COMMITTED"):
        return "no launchctl query/mutation in this state (filesystem/clock errors are FAILED)"
    return None


# Explicit Cartesian census, including every omitted cell and its reason.
UNREACHABLE_CELLS = {(state, fault): unreachable_reason(state, fault)
                     for state in STATE_PRODUCT for fault in FAULT_PRODUCT
                     if unreachable_reason(state, fault) is not None}


class TransactionFixture:
    """A real filesystem, stateful subprocess adapter and a valid fence plan."""
    def __init__(self, root, priors=False):
        from datetime import datetime
        from types import SimpleNamespace
        from joulewise import night_agent_install as engine
        from tests.test_install_night_agent import InstallNightAgentTests, REPO_ROOT
        self.root = Path(root).resolve()
        # Use the existing v3 plan producer without running any driver or Git.
        producer = InstallNightAgentTests()
        producer.root = self.root
        producer.plan_counter = 0
        producer.repo_head = "a" * 40
        producer.measurement_head = "b" * 40
        producer.measurement_root = self.root / "measurement"
        self.now = datetime(2026, 9, 15, 12).timestamp()
        self.plan_path = producer._write_plan(t0_epoch_s=self.now + 86400,
                                             authored_epoch_s=self.now - 60)
        self.plan = SimpleNamespace(**json.loads(self.plan_path.read_text()))
        self.fake = FakeLaunchctl(self.root / "fake")
        self.directory = self.root / "LaunchAgents"
        self.directory.mkdir()
        self.prior = {}
        self.prior_mtime = 1_600_000_000_123_456_789
        if priors:
            import plistlib
            self.prior_plan_path = producer._write_plan(
                plan_id="prior-install-night-agent-test", t0_epoch_s=self.now + 86400,
                authored_epoch_s=self.now - 60)
            for label in LABELS:
                path = self.directory / (label + ".plist")
                payload = plistlib.dumps({"Label": label, "ProgramArguments":
                    [sys.executable, "prior-run_night.py", "--plan", str(self.prior_plan_path)]})
                path.write_bytes(payload)
                path.chmod(0o640)
                os.utime(path, ns=(self.prior_mtime, self.prior_mtime))
                self.prior[label] = (payload, self.prior_mtime)
        self.clock_file = self.root / "clock"
        self.clock_file.write_text(str(self.now))
        self.template = (REPO_ROOT / "configs/launchd/com.joulewise.night.plist.template").read_text()

    def run(self, **options):
        self.options = options
        self.call_start = len(self.fake.calls())
        self.query_start = len(self.fake.queries())
        self.bootout_files = self.fake.expect_plists(
            self.directory, uninstall=options.get("uninstall", False))
        self.before = {label: (path.read_bytes(), path.stat().st_mtime_ns)
                       for label in LABELS
                       if (path := self.directory / (label + ".plist")).exists()}
        (self.root / "trace.json").write_text(json.dumps({"states": [], "commits": []}))
        options_path = self.root / "options.json"
        options_path.write_text(json.dumps(options))
        command = [options.get("interpreter", sys.executable), "-B", "-c",
            "from tests.test_night_agent_install import run_transaction_cell; "
            "import sys; sys.exit(run_transaction_cell(sys.argv[1]))", str(self.root)]
        kwargs = dict(cwd=Path(__file__).resolve().parents[1], text=True,
                      env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TMPDIR="/tmp"))
        if options.get("fault") != "BrokenPipeError_at_shutdown":
            return run_fixture_process(command, **kwargs)
        import time
        with fixture_process(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs) as child:
            try:
                deadline = time.monotonic() + 10
                while not (self.root / "stdout-ready").exists():
                    if child.poll() is not None or time.monotonic() >= deadline:
                        raise AssertionError("child never reached verified publication")
                    time.sleep(0.01)
                # Close the real reader after both bootstrap effects, before
                # the success line. The child handshake eliminates a sleep race.
                assert all(self.fake.loaded(label) for label in LABELS)
                child.stdout.close()
                (self.root / "stdout-closed").touch()
                child.wait(timeout=10)
                return subprocess.CompletedProcess(command, child.returncode, "", child.stderr.read())
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait()


def run_transaction_cell(root):
    """Executed in a child: real signal delivery cannot kill the test runner."""
    import signal
    from types import SimpleNamespace
    from joulewise import night_agent_install as engine
    root = Path(root).resolve()
    options = json.loads((root / "options.json").read_text())
    labels = LABELS
    plan_path = Path(options.get("plan_path", root / "custody/night_plan.json"))
    plan = SimpleNamespace(**json.loads(plan_path.read_text()))
    now = float((root / "clock").read_text())
    def clock():
        return float((root / "clock").read_text())
    directory = root / "LaunchAgents"
    render = options.get("render", False)
    target = engine.Target.for_mode(root / "real-LaunchAgents" if render else directory,
                                    directory if render else None, labels=labels)
    adapter = engine.NullAdapter(target) if render else engine.LaunchctlAdapter(
        target, str(root / "fake/launchctl-fake"), timeout=FAKE_TIMEOUT)
    REPO_ROOT = Path(__file__).resolve().parents[1]
    cutoff = now + (60 if options.get("fault") == "past_install" else 120)
    selected = now + (120 if options.get("fault") == "past_install" else 60)
    prepared = engine.Prepared(plan, plan_path, REPO_ROOT, sys.executable,
        (REPO_ROOT / "configs/launchd/com.joulewise.night.plist.template").read_text(),
        "/bin/true", "/usr/bin:/bin", {"t0_epoch_s": plan.t0_epoch_s,
         "install_close_epoch_s": cutoff, "deadman_epoch_s": plan.t0_epoch_s + 3600,
         "night_calendar": {"Month": 9, "Day": 16, "Hour": 12, "Minute": 0},
         "deadman_calendar": {"Hour": 15, "Minute": 0}}, lambda day: [(now - 60, selected)])
    # Reopen the instrument without resetting its directives or counters.
    fake = object.__new__(FakeLaunchctl)
    fake.root = root / "fake"
    fake.executable = fake.root / "launchctl-fake"
    fake.log = fake.root / "calls.log"
    fake.directives_path = fake.root / "directives.json"
    machine = engine.Transaction(adapter, lambda: prepared, clock=clock)
    trace = {"states": [], "commits": []}
    def save_trace():
        (root / "trace.json").write_text(json.dumps(trace))
    original_commit = machine._commit
    def commit():
        record = {"now": clock(), "selected": machine.selected_span_close,
                  "cutoff": prepared.schedule["install_close_epoch_s"], "passed": False}
        trace["commits"].append(record)
        try:
            if options.get("commit_refusal"):
                raise engine.Refused(2, "commit predicate refusal witness")
            result = original_commit()
            enter(engine.State.COMMITTED, transition=False)
            return result
        finally:
            record["passed"] = machine.state is engine.State.COMMITTED
            save_trace()
    machine._commit = commit
    state, fault = options.get("state"), options.get("fault")
    if state == "COMMITTED" and fault == "FAILED":
        # Arm the output fault BEFORE run(), independently of when COMMITTED
        # is entered. Otherwise moving that transition after print moves the
        # fault with it and makes the must-die mutation survive vacuously.
        original_say = machine._say
        def failed_say(message, error=False):
            if not error:
                raise BrokenPipeError("stdout witness")
            return original_say(message, error=error)
        machine._say = failed_say
    original_enter = machine._enter
    def enter(value, transition=True):
        if transition:
            original_enter(value)
        trace["states"].append(value.name)
        save_trace()
        if value is engine.State.VERIFIED and fault == "BrokenPipeError_at_shutdown":
            import time
            (root / "stdout-ready").touch()
            deadline = time.monotonic() + 10
            while not (root / "stdout-closed").exists():
                if time.monotonic() >= deadline:
                    raise AssertionError("parent never closed stdout")
                time.sleep(0.01)
        if value is engine.State.PUBLISHED and options.get("prebootstrap_unknown"):
            fake.set_loaded(labels[1], True)
            fake.directive(labels[1], "print", fault=9)
            raise engine.Refused(1, "publication witness")
        if value.name != state:
            return
        if fault in ("INT", "TERM", "HUP"):
            os.kill(os.getpid(), getattr(signal, "SIG" + fault))
        elif fault in ("exactly_close", "past_selected", "past_install"):
            (root / "clock").write_text(str(min(cutoff, selected) + (fault != "exactly_close")))
        elif fault == "render_PermissionError":
            original_render = prepared.render
            def failed_render(items, require_published=True):
                iterator = iter(original_render(items, require_published=require_published))
                yield next(iterator)
                raise PermissionError("second render witness")
            prepared.render = failed_render
        elif fault == "restore_IOError":
            def failed_restore(label, proof):
                raise OSError("restore witness")
            target.restore_prior = failed_restore
            if state == "STAGED":
                original_stage = target.stage
                def failed_stage():
                    original_stage()
                    raise engine.Refused(3, "rollback for restore fault")
                target.stage = failed_stage
            else:
                raise engine.Refused(3, "rollback for restore fault")
        elif fault in ("FAILED", "UNKNOWN"):
            if state == "VALIDATED":
                fake.directive(labels[0], "print", fault=9 if fault == "FAILED" else "hang", hang_s=FAKE_HANG_SECONDS)
            elif state in ("PUBLISHED", "NIGHT_LOADED", "DEADMAN_LOADED"):
                label = labels[1] if state == "DEADMAN_LOADED" else labels[0]
                fake.directive(label, "bootstrap", rc=5 if fault == "FAILED" else 0,
                               loaded=True, hang_s=FAKE_HANG_SECONDS if fault == "UNKNOWN" else 0)
            elif state == "COMMITTED":
                pass  # Output fault was armed before the state transition.
            else:
                raise engine.Refused(2 if state == "PARSED" else 1, "operation witness")
    machine._enter = enter
    if state == "PARSED":
        def validate():
            enter(engine.State.PARSED)
            return prepared
        machine.validate = validate
    if options.get("verification_unknown"):
        fake.sequence(labels[0], "print", [{}, {"fault": 9}, {}])
    if options.get("cleanup_clock"):
        original_cleanup = target.discard_priors
        def cleanup():
            (root / "clock").write_text(str(now + 9999))
            original_cleanup()
        target.discard_priors = cleanup
    if options.get("cleanup_baseexception"):
        def failed_cleanup():
            raise KeyboardInterrupt("cleanup witness")
        target.discard_priors = failed_cleanup
    if options.get("restore_signals"):
        original_restore = target.restore_prior
        def restore(label, proof):
            for number in engine.SIGNALS:
                os.kill(os.getpid(), number)
            original_restore(label, proof)
        target.restore_prior = restore
        fake.directive(labels[1], "bootstrap", rc=1, loaded=True)
    if options.get("cross_two"):
        fake.directive(labels[1], "bootstrap", clock_file=str(root / "clock"), clock=now + 121)
    if options.get("bootstrap_signal"):
        fake.directive(options["signal_label"], "bootstrap", loaded=True,
                       signal=options["bootstrap_signal"])
    if options.get("signal_seam"):
        return run_signal_cell(machine, prepared, fake, root, options, trace, save_trace)
    if options.get("uninstall"):
        return engine.uninstall(adapter)
    code = machine.run()
    if options.get("repeat_teardown"):
        calls = fake.calls()
        machine._unwind()
        assert calls == fake.calls(), "terminal teardown must not call launchctl again"
    (root / "result.json").write_text(json.dumps({"state": machine.state.name, "rc": code}))
    return code


def run_signal_cell(machine, prepared, fake, root, options, trace, save_trace):
    """Synchronous OS delivery at named seams in the real engine, in a child."""
    from unittest import mock
    from joulewise import night_agent_install as e
    seam, number = options["signal_seam"], options.get("signal_number", signal.SIGTERM)
    adapter, target = machine.adapter, machine.target
    entry_mask = signal.pthread_sigmask(signal.SIG_BLOCK, ())
    saved = {n: signal.getsignal(n) for n in e.SIGNALS}
    events, hits, teardowns = [], [], []

    def hit(name):
        if seam == name and not hits:
            hits.append(name)
            os.kill(os.getpid(), number)
            if options.get("two_signals"):
                os.kill(os.getpid(), signal.SIGHUP)

    def wrap(obj, name, before=None, after=None):
        original = getattr(obj, name)
        def call(*args, **kwargs):
            if before:
                before(*args, **kwargs)
            result = original(*args, **kwargs)
            if after:
                after(*args, **kwargs)
            return result
        setattr(obj, name, call)

    if seam == "pre_handlers":
        # Explicit inherited defaults make this startup boundary reproducible
        # even when the surrounding test launcher inherited SIG_IGN.
        for n in e.SIGNALS:
            signal.signal(n, signal.SIG_DFL)
        wrap(machine.shield, "install", before=lambda: hit("pre_handlers"))
    wrap(machine, "validate", before=lambda: hit("validate"))
    wrap(machine, "_enter", before=lambda state: hit("enter_" + state.name),
         after=lambda state: hit("after_" + state.name))
    render = prepared.render
    def rendering(labels, require_published=True):
        for index, item in enumerate(render(labels, require_published=require_published), 1):
            hit("write_before_" + str(index))
            yield item
    prepared.render = rendering
    for verb in ("write_plist", "bootstrap", "print", "bootout"):
        original = getattr(adapter, verb)
        def call(label, *args, verb=verb, original=original):
            index = str(LABELS.index(label) + 1)
            prefix = "verify" if verb == "print" and not teardowns and machine.state in (
                e.State.NIGHT_LOADED, e.State.DEADMAN_LOADED) else verb
            hit(prefix + "_before_" + index)
            events.append(prefix + "_" + index)
            helper = None
            if seam == "pep475" and verb == "bootstrap" and index == "1":
                # The helper signals this parent during the fake's 1.2 s syscall.
                fake.directive(label, verb, delay_s=1.2)
                helper = subprocess.Popen([sys.executable, "-B", "-c",
                    "import os,signal,time; time.sleep(0.3); os.kill(%d, %d)" %
                    (os.getpid(), number)])
            try:
                result = original(label, *args)
            finally:
                if helper is not None:
                    helper.wait(timeout=5)
            if helper is not None:
                hits.append(seam)
                assert result.kind is e.Kind.SUCCEEDED, result
                assert machine.shield.signalled == 128 + number
                events.append("pep475_outcome_returned")
            hit(prefix + "_after_" + index)
            return result
        setattr(adapter, verb, call)

    # Commit clock read and the precise post-poll/pre-assignment latch seam.
    wrap(machine, "clock", before=lambda: hit("clock") if machine.state is e.State.VERIFIED else None)
    wrap(machine, "_poll", after=lambda: hit("post_latch") if machine.state is e.State.VERIFIED else None)
    wrap(machine, "_say", before=lambda message, error=False: hit("pins") if not error else None,
         after=lambda message, error=False: hit("post_pins") if not error else None)
    wrap(machine, "_warn", before=lambda message: hit("warning"))
    wrap(machine, "_unwind", before=lambda: hit("unwind"))
    wrap(machine, "_teardown", before=lambda: (teardowns.append(machine.state.name), hit("teardown")))
    wrap(target, "remove_plist", before=lambda label, proof: hit("remove_" + str(LABELS.index(label) + 1)))
    wrap(machine.shield, "quiesce", before=lambda: hit("quiesce"), after=lambda: hit("post_quiesce"))
    if (seam in ("warning", "unwind", "teardown", "bootout_before_1", "bootout_before_2")
            and not options.get("warning_case")) or options.get("refusal"):
        wrap(machine, "_commit", before=lambda: (_ for _ in ()).throw(e.Refused(3, "seam refusal")))
    warning_case = options.get("warning_case")
    if warning_case:
        if warning_case != "stdout":
            fake.directive(LABELS[1], "bootstrap", rc=1, loaded=True)
        if warning_case == "retained":
            fake.directive(LABELS[0], "bootout", loaded=True)
        elif warning_case == "restore":
            target.restore_prior = mock.Mock(side_effect=OSError("restore witness"))
        elif warning_case == "teardown":
            def failed_teardown():
                teardowns.append(machine.state.name)
                raise OSError("teardown witness")
            machine._teardown = failed_teardown
        elif warning_case == "stdout":
            wrap(machine, "_say", before=lambda message, error=False:
                 (_ for _ in ()).throw(OSError("stdout witness")) if not error else None)
        # Inject only at the terminal warning, not the initial bootstrap refusal.
        warn = machine._warn
        def terminal_warning(message):
            if "failed to bootstrap" in message:
                return  # The tested warning is emitted by teardown.
            return warn(message)
        machine._warn = terminal_warning

    real_signal = signal.signal
    def quiesce_signal(n, handler):
        if handler is signal.SIG_IGN:
            hit("quiesce_signal_" + str(int(n)))
        return real_signal(n, handler)

    with mock.patch.object(signal, "signal", quiesce_signal):
        if options.get("uninstall"):
            code = e.uninstall(adapter, shield=machine.shield)
        elif options.get("cli"):
            # Exercise main's actual handler lifetime, parser and handoff, using
            # only this fixture target and the supplied fake executable.
            def transaction(adapter_arg, validate, **kwargs):
                machine.shield = kwargs["shield"]
                return machine
            wrap(machine, "run", after=lambda: hit("run_return"))
            parse = e.argparse.ArgumentParser.parse_args
            def parsing(parser, argv):
                hit("parse")
                return parse(parser, argv)
            with mock.patch.object(e, "Transaction", side_effect=transaction), \
                 mock.patch.object(e.Target, "for_mode", return_value=target), \
                 mock.patch.object(e.argparse.ArgumentParser, "parse_args", parsing):
                code = e.main(["--plan", str(root / "custody/night_plan.json"),
                               "--launchctl-bin", str(fake.executable)])
            hit("main_return")
        else:
            code = machine.run()
        hit("run_return")
    report = {"state": machine.state.name, "rc": code, "hits": hits,
              "events": events, "teardown_calls": len(teardowns),
              "signalled": machine.shield.signalled,
              "ignored": [signal.getsignal(n) is signal.SIG_IGN for n in e.SIGNALS],
              "mask_unchanged": signal.pthread_sigmask(signal.SIG_BLOCK, ()) == entry_mask}
    # Only in-process callers restore; CLI probes leave dispositions alone.
    if not options.get("cli"):
        machine.shield.release()
        machine.shield.release()
        report["restored"] = saved == {n: signal.getsignal(n) for n in e.SIGNALS}
    (root / "signal-report.json").write_text(json.dumps(report))
    (root / "result.json").write_text(json.dumps({"state": machine.state.name, "rc": code}))
    save_trace()
    return code


class TransactionTests(unittest.TestCase):
    def fixture(self, priors=False):
        temporary = tempfile.TemporaryDirectory(prefix="iw-txn-matrix-", dir="/tmp")
        self.addCleanup(temporary.cleanup)
        fixture = TransactionFixture(temporary.name, priors)
        self.assertEqual(fixture.now, float(fixture.clock_file.read_text()))
        return fixture

    @contextlib.contextmanager
    def cell(self, priors=False):
        # SubTest does not run TestCase cleanups until the entire product ends.
        with tempfile.TemporaryDirectory(prefix="iw-txn-cell-", dir="/tmp") as root:
            fixture = TransactionFixture(root, priors)
            self.assertEqual(fixture.now, float(fixture.clock_file.read_text()))
            yield fixture

    def assert_tuple(self, fixture, result, rc, loaded, files, *, fence_directory=None,
                     sidecars=None):
        """Every cell checks state, files, fence, teardown, diagnostics and recovery.

        Bootout checks cover all post-bootstrap rollback/retention cells and
        each uninstall; earlier refusals, render and commit require no bootout.
        D7's repeated uninstall explicitly preserves already-absent files.
        """
        from datetime import datetime
        from scripts import magistrate_watchdog as wd
        actual_loaded = tuple(label for label in LABELS if fixture.fake.loaded(label))
        actual_files = {}
        for label in LABELS:
            path = fixture.directory / (label + ".plist")
            actual_files[label] = (path.read_bytes(), path.stat().st_mtime_ns) if path.exists() else None
        try:
            fence = wd.installed_agent_fence(datetime.fromtimestamp(fixture.plan.t0_epoch_s).astimezone(),
                                            wd.Storage(fixture.root), launch_agents_dir=fence_directory or fixture.directory)
        except ValueError as exc:
            fence = "UNREADABLE:" + str(exc)  # The production consumer holds on unreadable evidence.
        self.assertFalse(actual_loaded and fence is None, (result.returncode, actual_loaded, actual_files, fence))
        self.assertEqual(rc, result.returncode, result.stderr)
        self.assertEqual(tuple(loaded), actual_loaded)
        for label in LABELS:
            observed = actual_files[label]
            if files == "prior":
                self.assertEqual(fixture.prior.get(label), observed)
                if observed:
                    self.assertEqual(0o640, (fixture.directory / (label + ".plist")).stat().st_mode & 0o777)
            elif files == "published":
                import plistlib
                self.assertIsNotNone(observed)
                self.assertIn(str(fixture.plan_path), plistlib.loads(observed[0])["ProgramArguments"])
                self.assertNotEqual(fixture.prior.get(label), observed)
            elif files == "retained":
                self.assertIsNotNone(observed)
            else:
                self.fail("unknown file expectation")
        expected_plan = (fixture.plan.plan_id if fence_directory is not None or files == "published"
                         else "prior-install-night-agent-test" if fixture.prior else None)
        self.assertEqual("; ".join(["installed_plan:" + expected_plan] * len(LABELS))
                         if expected_plan else None, fence)

        options = fixture.options
        trace = json.loads((fixture.root / "trace.json").read_text())
        self.assertLessEqual(len(trace["commits"]), 1, "the commit predicate is evaluated at most once")
        calls = fixture.fake.calls()[fixture.call_start:]
        states = trace["states"]
        uninstall_mode = options.get("uninstall", False)
        needs_bootout = uninstall_mode or (rc != 0 and any(
            state in ("NIGHT_LOADED", "DEADMAN_LOADED", "VERIFIED") for state in states)
            and not options.get("render"))
        sequence = [f"{action} gui/{os.getuid()}/{label}"
                    for action in ("bootout", "print") for label in LABELS]
        bootouts = [call for call in calls if call.startswith("bootout ")]
        observations = [json.loads(line) for line in
                        (fixture.fake.root / "bootout-plists.jsonl").read_text().splitlines()]
        if needs_bootout:
            self.assertEqual(sequence, calls[-4:], "both bootouts must precede both absence queries")
            self.assertEqual(1, sum(calls[i:i + 4] == sequence for i in range(len(calls) - 3)),
                             "exactly one complete teardown per invocation")
            self.assertEqual(sequence[:2], bootouts)
            self.assertEqual([{"label": label, "files": fixture.bootout_files} for label in LABELS],
                             observations, "the fake must inspect both files at EVERY bootout")
        else:
            self.assertEqual([], bootouts)
            self.assertEqual([], observations)

        retained_lines = [line for line in result.stderr.splitlines() if "retained plists:" in line]
        queries = fixture.fake.queries()[fixture.query_start:]
        outcomes = {query["label"]: query["kind"] for query in queries}
        unresolved = tuple(label for label in LABELS if outcomes.get(label) in ("LOADED", "UNKNOWN"))
        if rc == 4:
            self.assertEqual(set(LABELS), set(outcomes), "retention must query both labels")
            self.assertTrue(unresolved, "retention requires a LOADED or UNKNOWN query outcome")
            paths = " ".join(str(fixture.directory / (label + ".plist")) for label in LABELS)
            if uninstall_mode:
                expected = "uninstall: still loaded after bootout: {}; retained plists: {}".format(
                    " ".join(unresolved), paths)
                self.assertEqual(fixture.before, actual_files, "uninstall retention must preserve both files")
            else:
                expected = "teardown: {}; retained plists: {}".format(
                    "; ".join(f"{label} loaded={int(label in unresolved)}" for label in LABELS), paths)
            self.assertEqual([expected], retained_lines, "exact retained diagnostic, emitted once")
            self.assertTrue(all(actual_files.values()), "retention must keep BOTH published plists")
        else:
            self.assertEqual([], retained_lines)

        # Ordinary rollback and successful cleanup leave only the two plists
        # (or an empty directory), never a .prior, .tmp, or backup directory.
        recovery_retained = (options.get("fault") == "restore_IOError" or rc == 4
                             or options.get("cleanup_baseexception"))
        extras = {path.name for path in fixture.directory.iterdir()
                  if path.name not in {label + ".plist" for label in LABELS}}
        if sidecars is not None:
            self.assertEqual(set(sidecars), extras)
            for name, expected in sidecars.items():
                prior = fixture.directory / name
                self.assertEqual(expected, (prior.read_bytes(), prior.stat().st_mtime_ns))
        elif recovery_retained and fixture.prior and not uninstall_mode:
            self.assertEqual({label + ".plist.prior" for label in LABELS}, extras)
            for label in LABELS:
                prior = fixture.directory / (label + ".plist.prior")
                self.assertEqual(fixture.prior[label], (prior.read_bytes(), prior.stat().st_mtime_ns))
        else:
            self.assertEqual(set(), extras, "no leaked backup, sidecar or temporary publication")

        if rc == 0:
            if uninstall_mode:
                # D7's sole success exception: no commit gate, both absence
                # queries after bootout, both labels absent and files removed.
                self.assertEqual([], trace["commits"])
                self.assertEqual((), actual_loaded)
                self.assertEqual(dict.fromkeys(LABELS, "ABSENT"), outcomes)
                self.assertEqual(dict.fromkeys(LABELS), actual_files)
                self.assertEqual(sequence, calls)
            else:
                self.assertEqual(1, len(trace["commits"]), "exit 0 requires the single commit predicate")
                gate = trace["commits"][0]
                self.assertTrue(gate["passed"])
                self.assertLess(gate["now"], min(gate["selected"], gate["cutoff"]))
                self.assertEqual(1, states.count("COMMITTED"))
        return actual_files, fence

    def test_zero_exit_routes_require_commit_or_verified_uninstall(self):
        import ast
        from joulewise import night_agent_install as engine
        tree = ast.parse(Path(engine.__file__).read_text())
        zero_returns = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                        for child in ast.walk(node) if isinstance(child, ast.Return)
                        and isinstance(child.value, ast.Constant) and child.value.value == 0]
        self.assertEqual(["uninstall", "main"], zero_returns,
                         "only verified uninstall and the separate access probe return zero directly")
        main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
        probe_branch = next(node for node in ast.walk(main) if isinstance(node, ast.If)
                            and ast.unparse(node.test) == "args.launchd_probe")
        self.assertEqual("launchd_probe", probe_branch.body[-2].value.func.id)
        self.assertEqual("return 0", ast.unparse(probe_branch.body[-1]))
        teardown = next(node for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef) and node.name == "_teardown")
        zero_assignments = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                            and any(isinstance(target, ast.Attribute) and target.attr == "result"
                                    for item in node.targets for target in ast.walk(item))
                            and any(isinstance(value, ast.Constant) and value.value == 0
                                    for value in ast.walk(node.value))]
        self.assertEqual(1, len(zero_assignments))
        branch = teardown.body[0]
        self.assertEqual("self.state is State.COMMITTED", ast.unparse(branch.test))
        self.assertIn(zero_assignments[0], branch.body)
        for render in (False, True):
            fixture = self.fixture(True)
            self.assert_tuple(fixture, fixture.run(render=render, commit_refusal=True), 2, (), "prior")
        fixture = self.fixture()
        self.assert_tuple(fixture, fixture.run(), 0, LABELS, "published")
        self.assert_tuple(fixture, fixture.run(uninstall=True, commit_refusal=True), 0, (), "prior")

    def test_state_fault_product(self):
        import signal
        executed = set()
        for state in STATE_PRODUCT:
            for fault in FAULT_PRODUCT:
                if (state, fault) in UNREACHABLE_CELLS:
                    self.assertTrue(UNREACHABLE_CELLS[state, fault])
                    continue
                executed.add((state, fault))
                for priors in (False, True):
                    with self.subTest(state=state, fault=fault, priors=priors):
                        fixture = self.fixture(priors)
                        result = fixture.run(state=state, fault=fault)
                        if state == "COMMITTED":
                            rc, loaded, files = 0, LABELS, "published"
                        elif fault in ("INT", "TERM", "HUP"):
                            number = getattr(signal, "SIG" + fault)
                            rc = 128 + number
                            loaded, files = (), "prior"
                        elif fault.startswith("past_") or fault == "exactly_close":
                            rc, loaded, files = 2, (), "prior"
                        elif fault == "restore_IOError":
                            rc, loaded = 1, ()
                            files = "published" if state not in ("STAGED",) else "prior"
                        elif fault == "render_PermissionError":
                            rc, loaded, files = 1, (), "prior"
                        elif state in ("VALIDATED", "PUBLISHED", "NIGHT_LOADED", "DEADMAN_LOADED"):
                            rc, loaded, files = 3, (), "prior"
                        else:
                            rc, loaded, files = (2 if state == "PARSED" else 1), (), "prior"
                        self.assert_tuple(fixture, result, rc, loaded, files)
                        calls = fixture.fake.calls()
                        if rc == 0:
                            self.assertFalse(any(call.startswith("bootout ") for call in calls))
                        if fault == "BrokenPipeError_at_shutdown":
                            self.assertNotIn("Exception ignored", result.stderr)
                            self.assertFalse(list(fixture.directory.glob("*.prior")))
                        if state in ("STAGED", "PUBLISHED") and fault not in ("FAILED", "UNKNOWN", "exactly_close", "past_selected", "past_install"):
                            self.assertFalse(any(call.startswith("bootout ") for call in calls))
        self.assertEqual(len(STATE_PRODUCT) * len(FAULT_PRODUCT), len(executed) + len(UNREACHABLE_CELLS))

    def test_int_cells_with_inherited_sigign(self):
        import signal
        previous = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            for state in STATE_PRODUCT[:STATE_PRODUCT.index("COMMITTED")]:
                for priors in (False, True):
                    with self.subTest(state=state, priors=priors):
                        fixture = self.fixture(priors)
                        result = fixture.run(state=state, fault="INT")
                        self.assert_tuple(fixture, result, 130, (), "prior")
                        self.assertIs(signal.SIG_IGN, signal.getsignal(signal.SIGINT))
        finally:
            signal.signal(signal.SIGINT, previous)

    def test_shell_dangling_option_values_refuse_without_effects(self):
        from tests.test_install_night_agent import SCRIPT_PATH
        for flag in ("--plan", "--python", "--render-only", "--launchctl-bin"):
            with self.subTest(flag=flag):
                fixture = self.fixture(True)
                home = fixture.root / "home"
                home.mkdir()

                def snapshot():
                    return {str(path.relative_to(fixture.root)):
                            (path.stat().st_mode, path.stat().st_mtime_ns,
                             path.read_bytes() if path.is_file() else None)
                            for path in fixture.root.rglob("*")}

                before = snapshot()
                result = subprocess.run(
                    ["/bin/zsh", str(SCRIPT_PATH), "--plan", str(fixture.plan_path),
                     "--python", sys.executable, "--render-only", str(fixture.directory),
                     "--launchctl-bin", str(fixture.fake.executable), flag],
                    env=dict(os.environ, HOME=str(home), PYTHONDONTWRITEBYTECODE="1", TMPDIR="/tmp"),
                    capture_output=True, text=True, timeout=15)
                self.assertEqual(2, result.returncode, result.stderr)
                self.assertEqual("", result.stdout)
                self.assertRegex(
                    result.stderr, r"\Ausage: [^\n]+ --plan PLAN\.json \[--python ABS_PATH\] "
                    r"\[--launchd-probe\] \[--probe-timeout-s S\] \[--probe-max-age-s S\] "
                    r"\[--hour H\] \[--minute M\] "
                    r"\[--uninstall\] \[--render-only DIR\] \[--launchctl-bin PATH\]\n\Z")
                self.assertEqual([], fixture.fake.calls())
                self.assertEqual(before, snapshot())

    def test_slow_admission_query_reaches_commit_refusal(self):
        # The former 0.75s deadline refused at VALIDATED under scheduling load.
        with self.cell() as fixture:
            fixture.fake.sequence(LABELS[0], "print", [{"delay_s": 1}, {}, {}])
            result = fixture.run(cross_two=True)
            trace = json.loads((fixture.root / "trace.json").read_text())
            self.assertIn("ADMITTED", trace["states"], result.stderr)
            self.assertEqual("VERIFIED", trace["states"][-1], result.stderr)
            self.assertEqual(1, len(trace["commits"]))
            self.assertIn("install_span_closed", result.stderr)
            self.assert_tuple(fixture, result, 2, (), "prior")

    def test_hung_grandchild_cannot_write_clock_into_next_cell(self):
        with self.cell() as first:
            first.fake.directive(LABELS[0], "print", fault="hang",
                                 late_clock_file=str(first.clock_file),
                                 late_clock=first.now + 9999)
            command = [str(first.fake.executable), "print",
                       "gui/{}/{}".format(os.getuid(), LABELS[0])]
            # Model an interrupted transaction with a still-running fake child.
            wrapper = [sys.executable, "-B", "-c",
                       "import subprocess,sys,time; subprocess.Popen(sys.argv[1:]); time.sleep(30)"]
            with fixture_process(wrapper + command, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE) as parent:
                deadline = time.monotonic() + 10
                while not (first.fake.root / "hang-ready").exists():
                    self.assertIsNone(parent.poll(), "fake wrapper exited before handshake")
                    self.assertLess(time.monotonic(), deadline, "fake never started hanging")
                    time.sleep(0.01)
                ready = time.monotonic()
                fake_pid = int((first.fake.root / "hang-ready").read_text())
            self.assertIsNotNone(parent.returncode)
            with self.assertRaises(ProcessLookupError):
                os.kill(fake_pid, 0)
            stopped_clock = first.clock_file.read_text()
            with self.cell() as second:
                self.assertNotEqual(first.root, second.root)
                self.assertNotEqual(first.clock_file, second.clock_file)
                # Cross the fake's delayed-write deadline before admission.
                time.sleep(max(0, ready + 1.1 - time.monotonic()))
                self.assertEqual(stopped_clock, first.clock_file.read_text())
                self.assertEqual(second.now, float(second.clock_file.read_text()))
                result = second.run()
                trace = json.loads((second.root / "trace.json").read_text())
                self.assertIn("ADMITTED", trace["states"], result.stderr)
                self.assert_tuple(second, result, 0, LABELS, "published")

    def test_retention_product(self):
        self.retention_product(marker_loaded=True,
                               faults=(None, 9, 64, 112, "113-with-wrong-label", "hang"))

    def test_absent_unknown_retention_product(self):
        # Successful bootout removes both markers, but a failed query still
        # cannot authorize rollback restoration or uninstall deletion (D2).
        self.retention_product(marker_loaded=False,
                               faults=(9, 64, 112, "113-with-wrong-label", "hang"))

    def retention_product(self, *, marker_loaded, faults):
        for entry in ("bootstrap_failure", "commit_refusal"):
            # Uninstall has no commit gate; keep its existing product once.
            for uninstall_mode in ((False, True) if entry == "bootstrap_failure" else (False,)):
                for retained_labels in (LABELS[:1], LABELS[1:], LABELS):
                    for fault in faults:
                        for priors in (False, True):
                            with self.subTest(entry=entry, uninstall=uninstall_mode, labels=retained_labels,
                                              fault=fault, priors=priors, marker_loaded=marker_loaded), self.cell(priors) as fixture:
                                if uninstall_mode:
                                    # Begin from a complete successful publication.
                                    self.assert_tuple(fixture, fixture.run(), 0, LABELS, "published")
                                for label in retained_labels:
                                    fixture.fake.directive(label, "bootout", rc=0, loaded=marker_loaded)
                                    if fault is not None:
                                        successful_queries = (0 if uninstall_mode else
                                                              2 if entry == "commit_refusal" else 1)
                                        fixture.fake.sequence(label, "print", [{}] * successful_queries +
                                                              [{"fault": fault, "hang_s": FAKE_HANG_SECONDS}])
                                if not uninstall_mode and entry == "bootstrap_failure":
                                    fixture.fake.directive(LABELS[1], "bootstrap", rc=1, loaded=True)
                                before = {item: (fixture.directory / (item + ".plist")).read_bytes()
                                          for item in LABELS} if uninstall_mode else None
                                result = fixture.run(uninstall=uninstall_mode, cross_two=entry == "commit_refusal")
                                if entry == "commit_refusal":
                                    trace = json.loads((fixture.root / "trace.json").read_text())
                                    self.assertEqual("VERIFIED", trace["states"][-1], result.stderr)
                                    self.assertEqual(1, len(trace["commits"]))
                                    gate = trace["commits"][0]
                                    self.assertFalse(gate["passed"])
                                    self.assertGreaterEqual(gate["now"], gate["selected"])
                                    self.assertIn("install_span_closed", result.stderr)
                                self.assertEqual(
                                    [{"label": label, "kind": ("UNKNOWN" if fault is not None else "LOADED")
                                      if label in retained_labels else "ABSENT"} for label in LABELS],
                                    fixture.fake.queries()[-2:])
                                self.assert_tuple(fixture, result, 4,
                                                  retained_labels if marker_loaded else (), "published")
                                unknown_labels = [line.split()[1] for line in result.stderr.splitlines()
                                                  if line.startswith("liveness_unknown: ")]
                                self.assertCountEqual(retained_labels if fault is not None else (),
                                                      unknown_labels)
                                if before:
                                    for item in LABELS:
                                        self.assertEqual(before[item], (fixture.directory / (item + ".plist")).read_bytes())
                                if priors and not uninstall_mode:
                                    for item in LABELS:
                                        prior = fixture.directory / (item + ".plist.prior")
                                        self.assertEqual(fixture.prior[item], (prior.read_bytes(), prior.stat().st_mtime_ns))

    def test_retained_prior_refuses_without_writes(self):
        fixture = self.fixture()
        sidecar = fixture.directory / (LABELS[0] + ".plist.prior")
        payload = b"retained prior plist bytes\n"
        sidecar.write_bytes(payload)
        os.utime(sidecar, ns=(fixture.prior_mtime, fixture.prior_mtime))
        directory_mtime = fixture.directory.stat().st_mtime_ns

        result = fixture.run()

        self.assert_tuple(fixture, result, 3, (), "prior",
                          sidecars={sidecar.name: (payload, fixture.prior_mtime)})
        self.assertEqual("retained prior plist: {}; re-run --uninstall\n".format(sidecar),
                         result.stderr)
        self.assertEqual("", result.stdout)
        self.assertEqual([], fixture.fake.calls())
        self.assertEqual(directory_mtime, fixture.directory.stat().st_mtime_ns)
        self.assertFalse((Path(fixture.plan.custody_root) / "night").exists())

    def test_occupancy_product(self):
        for label in LABELS:
            for fault in (None, 9, 64, 112, "113-with-wrong-label", "hang", "0-with-junk-stderr"):
                with self.subTest(label=label, fault=fault):
                    fixture = self.fixture(True)
                    fixture.fake.set_loaded(label, True)
                    if fault:
                        fixture.fake.directive(label, "print", fault=fault, hang_s=FAKE_HANG_SECONDS)
                    result = fixture.run()
                    self.assert_tuple(fixture, result, 3, (label,), "prior")
                    self.assertIn("night_agent_already_loaded", result.stderr)
                    if fault and fault != "0-with-junk-stderr":
                        self.assertIn("state=unknown", result.stderr)
                    self.assertTrue(all(line.startswith("print ") for line in fixture.fake.calls()))

    def test_render_product(self):
        import plistlib
        for failure in (False, True):
            for priors in (False, True):
                with self.subTest(failure=failure, priors=priors):
                    fixture = self.fixture(priors)
                    # Loaded jobs belong to a DIFFERENT target (R4). The fence
                    # reads that launchd directory, never the render directory.
                    live = fixture.root / "real-LaunchAgents"
                    live.mkdir()
                    before = {}
                    for label in LABELS:
                        path = live / (label + ".plist")
                        path.write_bytes(plistlib.dumps({"Label": label, "ProgramArguments":
                            ["run_night.py", "--plan", str(fixture.plan_path)]}))
                        before[label] = (path.read_bytes(), path.stat().st_mtime_ns)
                        fixture.fake.set_loaded(label, True)
                    result = fixture.run(render=True, state="STAGED" if failure else None,
                                         fault="render_PermissionError" if failure else None)
                    self.assert_tuple(fixture, result, 1 if failure else 0, LABELS,
                                      "prior" if failure else "published", fence_directory=live)
                    for label in LABELS:
                        path = live / (label + ".plist")
                        self.assertEqual(before[label], (path.read_bytes(), path.stat().st_mtime_ns))
                    self.assertEqual([], fixture.fake.calls())

    def test_staged_render_names_future_published_plan(self):
        import plistlib
        fixture = self.fixture()
        staged = fixture.root / "staging/night_plan.json"
        staged.parent.mkdir()
        fixture.plan_path.rename(staged)
        result = fixture.run(render=True, plan_path=str(staged))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(2, len(list(fixture.directory.glob("*.plist"))))
        for label in LABELS:
            payload = plistlib.loads((fixture.directory / (label + ".plist")).read_bytes())
            argv = payload["ProgramArguments"]
            self.assertEqual(str(fixture.plan_path), argv[argv.index("--plan") + 1])
            self.assertNotIn(str(staged), argv)
        self.assertTrue(staged.is_file())
        self.assertFalse(fixture.plan_path.exists())
        self.assertEqual([], fixture.fake.calls())

    def test_real_install_refuses_staged_plan_at_transaction_admission(self):
        fixture = self.fixture()
        staged = fixture.root / "staged-plan.json"
        fixture.plan_path.rename(staged)
        result = fixture.run(plan_path=str(staged))
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("plan_outside_custody_root", result.stderr)
        self.assertEqual([], list(fixture.directory.iterdir()))
        self.assertFalse((fixture.root / "custody/night").exists())
        self.assertTrue(all(call.startswith("print ") for call in fixture.fake.calls()))

    def test_published_and_staged_admission_keep_all_timing_checks(self):
        from joulewise import night_agent_install as engine
        fixture = self.fixture()
        for require_published in (True, False):
            plan_path = fixture.plan_path if require_published else fixture.root / "staged.json"
            for reason, t0, close, spans in (
                ("plan_t0_in_the_past", 90, 150, [(0, 200)]),
                ("install_span_closed", 200, 100, [(0, 200)]),
                ("install_outside_span", 200, 150, [(0, 100), (101, 200)]),
                (None, 200, 150, [(0, 200)]),
            ):
                with self.subTest(require_published=require_published, reason=reason):
                    prepared = engine.Prepared(fixture.plan, plan_path, fixture.root,
                        sys.executable, fixture.template, "/bin/true", "/usr/bin:/bin",
                        {"t0_epoch_s": t0, "install_close_epoch_s": close, "deadman_epoch_s": 300},
                        lambda day: spans)
                    if reason:
                        with self.assertRaises(engine.Refused) as raised:
                            prepared.admit(100, require_published=require_published)
                        self.assertIn(reason, str(raised.exception))
                    else:
                        self.assertEqual(200, prepared.admit(100, require_published=require_published))
                        if not require_published:
                            with self.assertRaises(engine.Refused) as raised:
                                prepared.admit(100)
                            self.assertIn("plan_outside_custody_root", str(raised.exception))

    def test_verification_unknown_is_not_loaded(self):
        fixture = self.fixture(True)
        self.assert_tuple(fixture, fixture.run(verification_unknown=True), 3, (), "prior")

    def test_prebootstrap_unknown_retains_both_publications(self):
        for priors in (False, True):
            fixture = self.fixture(priors)
            result = fixture.run(prebootstrap_unknown=True)
            self.assert_tuple(fixture, result, 4, (LABELS[1],), "published")
            self.assertIn("liveness_unknown: " + LABELS[1], result.stderr)
            self.assertFalse(any(call.startswith("bootout ") for call in fixture.fake.calls()))

    def test_uninstall_records_repeated_signals_through_absence_and_deletion(self):
        fixture = self.fixture()
        self.assert_tuple(fixture, fixture.run(), 0, LABELS, "published")
        for label, number in zip(LABELS, ("TERM", "HUP")):
            fixture.fake.directive(label, "bootout", signal=number)
        self.assert_tuple(fixture, fixture.run(uninstall=True), 0, (), "prior")

    def test_control_clock_advances_during_cleanup(self):
        fixture = self.fixture(True)
        result = fixture.run(cleanup_clock=True)
        self.assert_tuple(fixture, result, 0, LABELS, "published")
        self.assertGreater(float(fixture.clock_file.read_text()), fixture.now + 120)
        self.assertFalse(any(line.startswith("bootout ") for line in fixture.fake.calls()))

    def test_committed_cleanup_baseexception_preserves_arm(self):
        fixture = self.fixture(True)
        result = fixture.run(cleanup_baseexception=True)
        self.assert_tuple(fixture, result, 0, LABELS, "published")
        self.assertIn("warning: prior sidecars not removed: cleanup witness", result.stderr)
        self.assertIn("validated pins:", result.stdout)
        for label in LABELS:
            prior = fixture.directory / (label + ".plist.prior")
            self.assertEqual(fixture.prior[label], (prior.read_bytes(), prior.stat().st_mtime_ns))
        self.assertFalse(any(line.startswith("bootout ") for line in fixture.fake.calls()))

    def test_committed_stdout_failure_preserves_arm(self):
        for priors in (False, True):
            fixture = self.fixture(priors)
            result = fixture.run(state="COMMITTED", fault="FAILED")
            self.assert_tuple(fixture, result, 0, LABELS, "published")
            self.assertFalse(any(line.startswith("bootout ") for line in fixture.fake.calls()))

    def test_committed_closed_stdout_preserves_arm_through_shutdown(self):
        for priors in (False, True):
            with self.subTest(priors=priors):
                fixture = self.fixture(priors)
                result = fixture.run(state="COMMITTED", fault="BrokenPipeError_at_shutdown")
                self.assert_tuple(fixture, result, 0, LABELS, "published")
                self.assertNotIn("Exception ignored", result.stderr)
                self.assertFalse(list(fixture.directory.glob("*.prior")))
                self.assertFalse(any(line.startswith("bootout ") for line in fixture.fake.calls()))

    def test_commit_crosses_two_boundaries(self):
        fixture = self.fixture()
        self.assert_tuple(fixture, fixture.run(cross_two=True), 2, (), "prior")

    def test_repeated_signals_during_restore(self):
        fixture = self.fixture(True)
        self.assert_tuple(fixture, fixture.run(restore_signals=True), 3, (), "prior")

    def test_signals_after_bootstrap_effect_restore_both_plists(self):
        import signal
        for label in LABELS:
            for name in ("INT", "TERM", "HUP"):
                for priors in (False, True):
                    with self.subTest(label=label, signal=name, priors=priors):
                        fixture = self.fixture(priors)
                        result = fixture.run(bootstrap_signal=name, signal_label=label)
                        self.assert_tuple(fixture, result, 128 + getattr(signal, "SIG" + name), (), "prior")

    def test_uninstall_is_rerunnable(self):
        fixture = self.fixture()
        self.assert_tuple(fixture, fixture.run(), 0, LABELS, "published")
        for _ in range(2):
            self.assert_tuple(fixture, fixture.run(uninstall=True), 0, (), "prior")

    def test_teardown_reentry_preserves_restored_priors(self):
        fixture = self.fixture(True)
        result = fixture.run(state="DEADMAN_LOADED", fault="FAILED", repeat_teardown=True)
        self.assert_tuple(fixture, result, 3, (), "prior")
        self.assertEqual(2, sum(line.startswith("bootout ") for line in fixture.fake.calls()))


class RecordPollTests(unittest.TestCase):
    """Fable cells 1–13 and Opus's latch, PEP 475 and child-mask witnesses."""
    fixture = TransactionTests.fixture
    cell = TransactionTests.cell
    assert_tuple = TransactionTests.assert_tuple

    def signal_cell(self, seam, number=signal.SIGTERM, priors=True, **options):
        fixture = self.fixture(priors)
        interpreter = os.environ.get("JOULEWISE_SIGNAL_TEST_PYTHON", sys.executable)
        options.setdefault("interpreter", interpreter)
        fixture.fake.executable.write_text("#!" + interpreter + "\n" + FAKE_LAUNCHCTL_SOURCE)
        if options.get("uninstall"):
            installed = fixture.run(interpreter=interpreter)
            self.assert_tuple(fixture, installed, 0, LABELS, "published")
        result = fixture.run(signal_seam=seam, signal_number=number, **options)
        self.assertGreaterEqual(result.returncode, 0, result.stderr)
        report = json.loads((fixture.root / "signal-report.json").read_text())
        self.assertEqual([seam], report["hits"], (result.stderr, report))
        self.assertEqual([True] * 3, report["ignored"])
        self.assertTrue(report["mask_unchanged"])
        if not options.get("cli"):
            self.assertTrue(report["restored"])
        self.assertEqual(0 if options.get("uninstall") else 1, report["teardown_calls"])
        masks = [json.loads(line) for line in
                 (fixture.fake.root / "child-masks.jsonl").read_text().splitlines()] if fixture.fake.calls() else []
        self.assertTrue(all(mask == [] for mask in masks), masks)
        return fixture, result, report

    def test_named_seam_signal_product(self):
        early = ("validate", "enter_VALIDATED", "after_VALIDATED", "enter_ADMITTED",
                 "after_ADMITTED", "enter_STAGED")
        rollback = ("after_STAGED", "write_before_1", "write_plist_after_1",
                    "write_before_2", "write_plist_after_2", "enter_PUBLISHED",
                    "after_PUBLISHED", "enter_NIGHT_LOADED", "after_NIGHT_LOADED", "bootstrap_before_1",
                    "bootstrap_after_1", "enter_DEADMAN_LOADED", "after_DEADMAN_LOADED", "bootstrap_before_2",
                    "bootstrap_after_2", "verify_before_1", "verify_after_1",
                    "verify_before_2", "verify_after_2", "enter_VERIFIED",
                    "after_VERIFIED", "clock")
        completed = ("post_latch", "pins", "post_pins", "quiesce", "post_quiesce",
                     "run_return") + tuple("quiesce_signal_" + str(int(n)) for n in signal_signals())
        refusal = ("warning", "unwind", "teardown", "bootout_before_1", "bootout_before_2")
        for seam in early + rollback + completed + refusal:
            for number in signal_signals():
                with self.subTest(seam=seam, number=number):
                    f, result, report = self.signal_cell(seam, number)
                    rc = 0 if seam in completed else 3 if seam in refusal else 128 + number
                    self.assert_tuple(f, result, rc, LABELS if rc == 0 else (),
                                      "published" if rc == 0 else "prior")
                    self.assertEqual("SUCCESS" if rc == 0 else "REFUSED" if seam in early
                                     else "ROLLED_BACK", report["state"])
                    if rc == 0:
                        self.assertIn("validated pins:", result.stdout)
                    forbidden = {"write_before_1": "write_plist_1", "write_before_2": "write_plist_2",
                                 "enter_NIGHT_LOADED": "bootstrap_1",
                                 "enter_DEADMAN_LOADED": "bootstrap_2",
                                 "after_NIGHT_LOADED": "bootstrap_1",
                                 "after_DEADMAN_LOADED": "bootstrap_2",
                                 "bootstrap_after_1": "bootstrap_2",
                                 "bootstrap_after_2": "verify_1", "verify_after_1": "verify_2"}
                    if seam in forbidden:
                        self.assertNotIn(forbidden[seam], report["events"])

    def test_two_distinct_signals_first_wins(self):
        f, result, report = self.signal_cell("write_before_2", two_signals=True)
        self.assert_tuple(f, result, 143, (), "prior")
        self.assertEqual(143, report["signalled"])

    def test_pep475_call_returns_outcome_then_poll_rolls_back(self):
        f, result, report = self.signal_cell("pep475")
        self.assert_tuple(f, result, 143, (), "prior")
        self.assertIn("pep475_outcome_returned", report["events"])
        self.assertNotIn("InterruptedError", result.stderr)

    def test_child_mask_after_signal_is_empty(self):
        f, result, _ = self.signal_cell("bootstrap_after_1")
        self.assert_tuple(f, result, 143, (), "prior")
        self.assertTrue(any(call.startswith("bootout ") for call in f.fake.calls()))

    def test_completed_warning_codes_stand(self):
        for case, code in (("retained", 4), ("restore", 1), ("teardown", 1), ("stdout", 0)):
            with self.subTest(case=case):
                f, result, report = self.signal_cell("warning", warning_case=case)
                self.assertEqual(code, result.returncode, result.stderr)
                self.assertEqual("SUCCESS" if code == 0 else "RETAINED", report["state"])
                self.assertEqual(143, report["signalled"])
                self.assertEqual(tuple(LABELS) if case in ("teardown", "stdout") else
                                 (LABELS[0],) if case == "retained" else (),
                                 tuple(label for label in LABELS if f.fake.loaded(label)))
                if case == "teardown":
                    self.assertIn("teardown failed; retained: OSError: teardown witness", result.stderr)

    def test_cli_completion_and_parse_cells(self):
        for seam, refusal in (("run_return", False), ("run_return", True), ("pins", False),
                              ("main_return", False), ("main_return", True), ("parse", False)):
            with self.subTest(seam=seam, refusal=refusal):
                f, result, _ = self.signal_cell(seam, cli=True, refusal=refusal)
                code = 3 if refusal else 143 if seam == "parse" else 0
                self.assert_tuple(f, result, code, LABELS if code == 0 else (),
                                  "published" if code == 0 else "prior")

    def test_uninstall_seam_signal_product(self):
        for seam in ("bootout_before_1", "bootout_after_1", "bootout_before_2", "bootout_after_2",
                     "print_before_1", "print_after_1", "print_before_2", "print_after_2",
                     "remove_1", "remove_2", "quiesce", "post_quiesce"):
            for number in signal_signals():
                with self.subTest(seam=seam, number=number):
                    f, result, _ = self.signal_cell(seam, number, priors=False, uninstall=True)
                    self.assert_tuple(f, result, 0, (), "prior")

    def test_module_contains_no_mask_call(self):
        from joulewise import night_agent_install as e
        result = subprocess.run(["grep", "-c", "pthread_sigmask", e.__file__],
                                capture_output=True, text=True)
        self.assertEqual((1, "0\n"), (result.returncode, result.stdout))

    def test_pre_handler_boundary_has_no_effects(self):
        interpreter = os.environ.get("JOULEWISE_SIGNAL_TEST_PYTHON", sys.executable)
        for number in signal_signals():
            with self.subTest(number=number):
                f = self.fixture(True)
                result = f.run(signal_seam="pre_handlers", signal_number=number,
                               interpreter=interpreter)
                self.assert_tuple(f, result, -number, (), "prior")
                self.assertEqual([], f.fake.calls())


def signal_signals():
    return (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)


class SignalTestCase(unittest.TestCase):
    def setUp(self):
        from unittest import mock
        from joulewise import night_agent_install as engine
        self.shields = []
        install = engine.Shield.install
        def track(shield):
            if shield not in self.shields:
                self.shields.append(shield)
            return install(shield)
        patch = mock.patch.object(engine.Shield, "install", track)
        patch.start()
        self.addCleanup(patch.stop)

    def tearDown(self):
        for shield in reversed(self.shields):
            shield.release()


class CapabilityTests(SignalTestCase):
    def setUp(self):
        super().setUp()
        from joulewise import night_agent_install as engine
        self.engine = engine
        temporary = tempfile.TemporaryDirectory(prefix="iw-txn-capability-", dir="/tmp")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.fake = FakeLaunchctl(self.root / "fake")
        self.target = engine.Target.for_mode(self.root / "LaunchAgents")
        self.target.directory.mkdir()
        self.adapter = engine.LaunchctlAdapter(self.target, str(self.fake.executable), timeout=FAKE_TIMEOUT)

    def _signal_machine(self, refusal=False):
        import io
        from types import SimpleNamespace
        from unittest import mock
        e = self.engine
        prepared = SimpleNamespace(admit=lambda now, require_published=True: 60,
            schedule={"install_close_epoch_s": 60},
            custody_night=self.root / "night", pins="pins",
            render=lambda labels, require_published=True: ((label, b"published") for label in labels))
        if refusal:
            prepared.render = mock.Mock(side_effect=e.Refused(3, "render refused"))
        return e.Transaction(self.adapter, lambda: prepared, clock=lambda: 10,
                             stdout=io.StringIO(), stderr=io.StringIO())

    def test_in_process_release_restores_exact_dispositions_and_mask(self):
        e = self.engine
        original = {n: signal.getsignal(n) for n in e.SIGNALS}
        original_mask = signal.pthread_sigmask(signal.SIG_BLOCK, ())
        expected_mask = original_mask | {signal.SIGUSR1}
        callbacks = {n: (lambda number, frame: None) for n in e.SIGNALS}
        try:
            for n, callback in callbacks.items():
                signal.signal(n, callback)
            signal.pthread_sigmask(signal.SIG_SETMASK, expected_mask)
            machine = self._signal_machine(refusal=True)
            self.assertEqual(3, machine.run())
            self.assertTrue(all(signal.getsignal(n) is signal.SIG_IGN for n in e.SIGNALS))
            self.assertEqual(expected_mask, signal.pthread_sigmask(signal.SIG_BLOCK, ()))
            machine.shield.release()
            machine.shield.release()
            self.assertEqual(callbacks, {n: signal.getsignal(n) for n in e.SIGNALS})
            self.assertEqual(expected_mask, signal.pthread_sigmask(signal.SIG_BLOCK, ()))
        finally:
            for n, handler in original.items():
                signal.signal(n, handler)
            signal.pthread_sigmask(signal.SIG_SETMASK, original_mask)

    def test_only_poll_raises_signalled(self):
        shield = self.engine.Shield()
        shield.install()
        os.kill(os.getpid(), signal.SIGTERM)
        os.kill(os.getpid(), signal.SIGHUP)
        self.assertEqual(143, shield.signalled)
        with self.assertRaises(self.engine.Signalled) as raised:
            shield.poll()
        self.assertEqual(143, raised.exception.code)
        shield.quiesce()

    def test_liveness_signature_product(self):
        e = self.engine
        for label in LABELS:
            for loaded in (False, True):
                for fault in (None, 9, 64, 112, "113-with-wrong-label", "0-with-junk-stderr", "hang"):
                    with self.subTest(label=label, loaded=loaded, fault=fault):
                        self.fake.set_loaded(label, loaded)
                        self.fake.directive(label, "print", fault=fault, hang_s=FAKE_HANG_SECONDS)
                        value = self.adapter.print(label)
                        expected = (e.Kind.LOADED if fault == "0-with-junk-stderr" or (fault is None and loaded)
                                    else e.Kind.ABSENT if fault is None else e.Kind.UNKNOWN)
                        self.assertIsInstance(value, e.Outcome)
                        self.assertIs(expected, value.kind)
                        if expected is e.Kind.ABSENT:
                            self.assertIsInstance(self.adapter.require_absent(label), e.Absent)
                        else:
                            with self.assertRaises(e.NotAbsent):
                                self.adapter.require_absent(label)
                        with self.assertRaises(TypeError):
                            bool(value)

    def test_decode_oserror_timeout_and_wrong_uid_are_unknown(self):
        from unittest import mock
        e = self.engine
        for error in (OSError("query witness"), UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid"),
                      subprocess.TimeoutExpired("query", 0.1)):
            with mock.patch.object(e.subprocess, "run", side_effect=error):
                self.assertIs(e.Kind.UNKNOWN, self.adapter.print(LABELS[0]).kind)
        for diagnostic in ('Could not find service "{}" in domain for user gui: 999999'.format(LABELS[0]),
                           'prefix Could not find service "{}" in domain for user gui: {}'.format(LABELS[0], os.getuid())):
            with mock.patch.object(e.subprocess, "run", return_value=subprocess.CompletedProcess([], 113, "", diagnostic)):
                self.assertIs(e.Kind.UNKNOWN, self.adapter.print(LABELS[0]).kind)

    def test_proof_is_required_bound_and_invalidated(self):
        e = self.engine
        self.target.stage()
        for label in LABELS:
            self.assertIs(e.Kind.SUCCEEDED, self.adapter.write_plist(label, b"published").kind)
        proof = self.adapter.require_absent(LABELS[0])
        for label, token in ((LABELS[0], None), (LABELS[1], proof)):
            for method in (self.target.remove_plist, self.target.restore_prior):
                with self.subTest(method=method.__name__, label=label):
                    with self.assertRaises(TypeError):
                        method(label, token)
                    self.assertTrue(self.target.path(label).exists())
        self.adapter.bootstrap(LABELS[0])
        with self.assertRaises(TypeError):
            self.target.remove_plist(LABELS[0], proof)
        self.assertTrue(self.target.path(LABELS[0]).exists())
        with self.assertRaises(TypeError):
            e.Absent(self.target, LABELS[0], 0, object())

    def test_target_modes_are_constructor_facts(self):
        e = self.engine
        with self.assertRaises(e.Refused):
            e.Target.for_mode(self.root, self.root)
        alias = self.root / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(e.Refused):
            e.Target.for_mode(self.root, alias)
        with self.assertRaises(TypeError):
            e.LaunchdTarget(self.root, LABELS, object())
        render = e.Target.for_mode(self.root / "launch", self.root / "render")
        with self.assertRaises(TypeError):
            e.LaunchctlAdapter(render)
        with self.assertRaises(TypeError):
            e.NullAdapter(self.target)
        null = e.NullAdapter(render)
        for name in ("print", "bootstrap", "bootout", "require_absent"):
            with self.assertRaises(TypeError):
                getattr(null, name)(LABELS[0])
        render.stage()
        self.assertIs(e.Kind.SUCCEEDED, null.write_plist(LABELS[0], b"rendered").kind)
        render.remove_plist(LABELS[0], None)
        self.assertFalse(render.path(LABELS[0]).exists())

    def test_restoration_requires_proof_even_with_an_existing_prior(self):
        label = LABELS[0]
        self.target.path(label).write_bytes(b"prior bytes")
        self.target.stage()
        self.adapter.write_plist(label, b"published bytes")
        proof = self.adapter.require_absent(label)
        # Invalidate that proof with an actual launchd mutation, with both
        # publications present as required by the adapter's capability.
        self.adapter.write_plist(LABELS[1], b"other")
        self.adapter.bootstrap(label)
        for token in (None, proof):
            with self.assertRaises(TypeError):
                self.target.restore_prior(label, token)
            self.assertEqual(b"published bytes", self.target.path(label).read_bytes())

    def test_render_cli_empty_value_refuses_before_target_construction(self):
        import io
        from unittest import mock
        for mode in ([], ["--uninstall"]):
            with self.subTest(mode=mode):
                stderr = io.StringIO()
                with mock.patch("sys.stderr", stderr), \
                     mock.patch.object(self.engine.Target, "for_mode") as construct:
                    with self.assertRaises(SystemExit) as raised:
                        self.engine.main(["--plan", str(self.root / "unused.json"),
                                          "--render-only", ""] + mode)
                self.assertEqual(2, raised.exception.code)
                self.assertRegex(stderr.getvalue(), r"\Ausage: .*\[--render-only DIR\]")
                construct.assert_not_called()
                self.assertEqual([], self.fake.calls())
                self.assertEqual([], list(self.target.directory.iterdir()))

    def test_render_cli_constructs_null_adapter_before_plan_validation(self):
        plan = self.root / "invalid-plan.json"
        plan.write_text("{}")
        result = subprocess.run([sys.executable, "-B", "-m", "joulewise.night_agent_install",
            "--render-only", str(self.root / "render"), "--plan", str(plan),
            "--launchctl-bin", str(self.root / "does-not-exist")],
            cwd=Path(__file__).resolve().parents[1],
            env=dict(os.environ, HOME=str(self.root / "home")),
            capture_output=True, text=True, timeout=10)
        self.assertEqual(3, result.returncode, result.stderr)
        self.assertIn("night_plan_malformed", result.stderr)
        self.assertFalse((self.root / "render").exists())
        self.assertEqual([], self.fake.calls())

    def test_unsupported_destinations_refuse_without_write(self):
        for symlink in (False, True):
            path = self.target.path(LABELS[0])
            if symlink:
                path.symlink_to(self.root / "missing")
            else:
                path.mkdir()
            with self.assertRaises(self.engine.Refused):
                self.target.validate()
            self.assertEqual([], list(self.target.directory.glob("*.prior")))
            if symlink:
                path.unlink()
            else:
                path.rmdir()

    def test_one_label_verified_bootout_is_supported(self):
        e = self.engine
        target = e.Target.for_mode(self.root / "one", labels=(LABELS[0],))
        target.directory.mkdir()
        adapter = e.LaunchctlAdapter(target, str(self.fake.executable))
        adapter.write_plist(LABELS[0], b"one")
        adapter.bootstrap(LABELS[0])
        proofs, unresolved = e.verified_bootout(adapter, target.labels)
        self.assertEqual({}, unresolved)
        target.remove_plist(LABELS[0], proofs[LABELS[0]])
        self.assertFalse(target.path(LABELS[0]).exists())

    @unittest.skipUnless(Path("/usr/bin/python3").is_file(), "requires system Python")
    def test_system_python_uninstall_exec_with_stripped_environment(self):
        repo = Path(__file__).resolve().parents[1]
        home = self.root / "home"
        directory = home / "Library/LaunchAgents"
        directory.mkdir(parents=True)
        for label in LABELS:
            (directory / (label + ".plist")).write_bytes(b"prior")
            self.fake.set_loaded(label, True)
        plan = self.root / "night_plan.json"
        plan.write_text('{"invalid_pins": true}')
        for _ in range(2):
            result = subprocess.run(["/usr/bin/python3", "-B", "-S", "-m",
                "joulewise.night_agent_install", "--uninstall", "--plan", str(plan),
                "--python", "/missing/venv/python", "--launchctl-bin", str(self.fake.executable)],
                cwd=repo, env={"HOME": str(home), "PATH": "/usr/bin:/bin", "TMPDIR": "/tmp"},
                capture_output=True, text=True, timeout=10)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("--python ignored on uninstall\n", result.stderr)
            self.assertEqual([], list(directory.glob("*.plist")))
            self.assertFalse(any(self.fake.loaded(label) for label in LABELS))


class LaunchdAccessProbeTests(unittest.TestCase):
    def setUp(self):
        from types import SimpleNamespace
        from tests.test_run_night import NightProbeTests, write_matching_probe_receipt
        from joulewise import night_agent_install as engine
        self.engine = engine
        self.fixture = NightProbeTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.fake = FakeLaunchctl(self.root / "fake-launchctl")
        self.prepared = SimpleNamespace(plan=self.fixture.plan, plan_path=self.fixture.plan_path,
            repo=Path(__file__).resolve().parents[1], python=sys.executable,
            courier_path="/usr/bin:/bin:/usr/sbin:/sbin")
        receipt_path = write_matching_probe_receipt(self.fixture.plan_path)
        self.receipt = json.loads(receipt_path.read_text())
        self.receipt.update(chain_pgid=999999, driver_pid=999998)
        self.pending = receipt_path.with_name("night_probe_receipt.pending.json")
        self.label = engine.probe_label(self.fixture.plan.plan_id)
        self.fake.directive(self.label, "bootstrap", probe_receipt=self.receipt,
                            receipt_path=str(self.pending))

    def test_temporary_launchd_job_bootstraps_boots_out_and_censuses_group(self):
        from unittest import mock
        real_run = subprocess.run
        censuses = []
        def runner(argv, **kwargs):
            if argv[0] == "/usr/bin/pgrep":
                censuses.append(argv)
                return subprocess.CompletedProcess(argv, 1, "", "")
            return real_run(argv, **kwargs)
        with mock.patch.object(self.engine.subprocess, "run", side_effect=runner), \
             mock.patch.object(self.engine.os, "killpg", side_effect=ProcessLookupError), \
             contextlib.redirect_stdout(__import__('io').StringIO()):
            record = self.engine.launchd_probe(self.prepared, str(self.fake.executable),
                                               self.engine.Shield(), timeout_s=0.5)
        self.assertEqual("ok", record["outcome"])
        self.assertTrue(self.fixture.receipt.exists())
        self.assertFalse(self.pending.exists())
        self.assertTrue(any(line.startswith("bootstrap ") and self.label in line for line in self.fake.calls()))
        self.assertIn("bootout gui/{}/{}".format(os.getuid(), self.label), self.fake.calls())
        self.assertFalse(self.fake.loaded(self.label))
        self.assertTrue(any("-g" in command and "999999" in command for command in censuses))
        self.assertTrue(any(__import__("re").escape(self.label) in command[-1] for command in censuses))
        self.assertFalse(list(self.root.glob("night-probe-job-*")))
        self.assertFalse(list(self.root.rglob("chain.started")))

    def test_failed_probe_receipt_still_boots_out_and_refuses(self):
        from unittest import mock
        real_run = subprocess.run
        self.receipt["outcome"] = "refused"
        self.fake.directive(self.label, "bootstrap", probe_receipt=self.receipt,
                            receipt_path=str(self.pending))
        def runner(argv, **kwargs):
            if argv[0] == "/usr/bin/pgrep":
                return subprocess.CompletedProcess(argv, 1, "", "")
            return real_run(argv, **kwargs)
        with mock.patch.object(self.engine.subprocess, "run", side_effect=runner), \
             mock.patch.object(self.engine.os, "killpg", side_effect=ProcessLookupError):
            with self.assertRaisesRegex(self.engine.Refused, "outcome") as caught:
                self.engine.launchd_probe(self.prepared, str(self.fake.executable), self.engine.Shield(), timeout_s=0.2)
        self.assertEqual(2, caught.exception.code)
        self.assertFalse(self.fake.loaded(self.label))
        self.assertFalse(self.fixture.receipt.exists())

    def test_cleanup_refusal_reports_the_failure_it_interrupted(self):
        """The finally block fails closed WITHOUT discarding the diagnostic."""
        import itertools
        from unittest import mock
        # Bootstrap publishes no receipt (the wait loop times out) and bootout
        # leaves the service loaded (the absence proof fails in the finally).
        self.fake.directive(self.label, "bootstrap")
        self.fake.directive(self.label, "bootout", loaded=True)
        clock = itertools.count(0.0, 5.0)  # only launchd_probe reads this clock
        with mock.patch.object(self.engine.time, "monotonic", side_effect=lambda: next(clock)):
            with self.assertRaises(self.engine.Refused) as caught:
                self.engine.launchd_probe(self.prepared, str(self.fake.executable),
                                          self.engine.Shield(), timeout_s=0.5)
        self.assertEqual(2, caught.exception.code)
        self.assertIn("probe bootout absence unproven", str(caught.exception))
        self.assertIn("probe receipt timeout", str(caught.exception))
        self.assertIsInstance(caught.exception.__cause__, self.engine.Refused)
        self.assertIn("probe receipt timeout", str(caught.exception.__cause__))
        self.assertFalse(self.fixture.receipt.exists())

    def test_survivor_or_unknown_census_refuses(self):
        from unittest import mock
        for rc, stdout in ((0, "4321 probe-worker\n"), (3, "")):
            with self.subTest(rc=rc), mock.patch.object(self.engine.subprocess, "run",
                    return_value=subprocess.CompletedProcess([], rc, stdout, "census fixture")):
                with self.assertRaisesRegex(self.engine.Refused, "survivor or unknown"):
                    self.engine.probe_process_census(self.label, self.fixture.plan_path, {"chain_pgid": 12345})


class EvidenceRenderOnlyTests(unittest.TestCase):
    def setUp(self):
        from tests.test_gen_evidence_night import EvidenceFixture
        from scripts import gen_evidence_night
        from joulewise import night_agent_install
        self.engine = night_agent_install
        self.f = EvidenceFixture()
        self.addCleanup(self.f.close)
        self.f.prepare_installer()
        self.staged = self.f.root / "staged.json"
        os.replace(self.f.plan_path, self.staged)
        gen_evidence_night.generate(self.staged)

    def render(self, plan_path):
        import io
        from unittest.mock import patch
        calls = []
        run = subprocess.run
        def recorded(argv, *args, **kwargs):
            calls.append(list(map(str, argv)))
            self.assertNotIn(self.f.plan.chain_path, calls[-1], "render-only executed the evidence chain")
            return run(argv, *args, **kwargs)
        output, errors = io.StringIO(), io.StringIO()
        with self.f.installer_environment(), patch.object(subprocess, "run", side_effect=recorded), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            result = self.engine.main(["--plan", str(plan_path), "--python", sys.executable,
                                       "--render-only", str(self.f.root / "rendered")])
        self.assertFalse(any(self.f.plan.chain_path in argv for argv in calls),
                         "render-only executed the evidence chain")
        return result, output.getvalue(), errors.getvalue()

    def test_staged_and_published_render_hash_same_bytes_without_chain_execution(self):
        chain = Path(self.f.plan.chain_path)
        manifest = chain.with_name("evidence_manifest.json")
        expected = {str(path): "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in (self.staged.absolute(), manifest)}
        self.assertFalse(self.f.plan_path.exists())
        result, output, errors = self.render(self.staged)
        self.assertEqual(result, 0, errors)
        records = [json.loads(line) for line in output.splitlines() if line.startswith("{")]
        self.assertIn({"payload_kind": "quiet_predicate_evidence", "chain_sha256": hashlib.sha256(chain.read_bytes()).hexdigest(),
                       "input_digests": expected}, records)
        os.replace(self.staged, self.f.plan_path)
        expected[str(self.f.plan_path.resolve())] = expected.pop(str(self.staged.resolve()))
        result, output, errors = self.render(self.f.plan_path)
        self.assertEqual(result, 0, errors)
        records = [json.loads(line) for line in output.splitlines() if line.startswith("{")]
        self.assertIn({"payload_kind": "quiet_predicate_evidence", "chain_sha256": hashlib.sha256(chain.read_bytes()).hexdigest(),
                       "input_digests": expected}, records)

        bindings = self.engine.evidence_probe_bindings(self.f.plan, self.f.plan_path, sys.executable)
        self.assertEqual(expected, bindings["input_digests"])

    def reseal_wrapper(self, text):
        Path(self.f.plan.chain_path).write_text(text)
        Path(self.f.plan.chain_sha256_path).write_text(hashlib.sha256(text.encode()).hexdigest() + "\n")

    def test_wrong_published_literal_refuses_before_plists(self):
        chain = Path(self.f.plan.chain_path)
        self.reseal_wrapper(chain.read_text().replace(str(self.f.plan_path),
                                                    str(self.f.root / "other-custody/night_plan.json")))
        result, output, errors = self.render(self.staged)
        self.assertEqual(result, 2, errors)
        self.assertIn("evidence plan path mismatch", errors)
        self.assertNotIn('"input_digests"', output)
        self.assertFalse((self.f.root / "rendered").exists())

    def test_ambiguous_payload_refuses_before_legacy_inspection(self):
        from unittest.mock import patch
        original = Path(self.f.plan.chain_path).read_text()
        for extra in ("export NIGHT_PAYLOAD_KIND=quiet_predicate_evidence\n",
                      "export CALIBRATION_LEDGER=/tmp/ledger\n"):
            with self.subTest(extra=extra):
                self.reseal_wrapper(original + extra)
                with patch.object(self.engine, "reservation_input_digests") as legacy:
                    result, output, errors = self.render(self.staged)
                legacy.assert_not_called()
                self.assertEqual(result, 2, errors)
                self.assertIn("ambiguous night payload declaration:", errors)
                self.assertNotIn('"input_digests"', output)
                self.assertFalse((self.f.root / "rendered").exists())

    def test_render_keeps_admission_refusals(self):
        from joulewise.night_gate import PLAN_MAX_AGE_S
        original = json.loads(self.staged.read_text())
        cases = (({"t0_epoch_s": (int(time.time()) // 60 - 1) * 60}, "plan_t0_in_the_past"),
                 ({"authored_epoch_s": time.time() - PLAN_MAX_AGE_S - 60}, "night_plan_stale"),
                 ({"measurement_head": "0" * 40}, "measurement checkout HEAD"),
                 ({}, "existing night records"))
        for changes, reason in cases:
            with self.subTest(reason=reason):
                self.staged.write_text(json.dumps(dict(original, **changes)))
                if not changes:
                    night = self.f.custody / "night"
                    night.mkdir(exist_ok=True)
                    (night / "result.json").write_text("{}")
                result, output, errors = self.render(self.staged)
                self.assertIn(result, (2, 3), errors)
                self.assertIn(reason, errors)
                self.assertNotIn('"input_digests"', output)
                self.assertFalse((self.f.root / "rendered").exists())

    def test_two_renders_into_one_directory_are_byte_identical(self):
        result, output, errors = self.render(self.staged)
        self.assertEqual(result, 0, errors)
        paths = list((self.f.root / "rendered").glob("*.plist"))
        self.assertEqual(len(paths), 3)
        before = {path: path.read_bytes() for path in paths}
        result, again, errors = self.render(self.staged)
        self.assertEqual(result, 0, errors)
        self.assertEqual(output, again)
        self.assertEqual(before, {path: path.read_bytes() for path in paths})

    def test_missing_or_unreadable_manifest_is_typed_refusal(self):
        from unittest.mock import patch
        manifest = Path(self.f.plan.chain_path).with_name("evidence_manifest.json")
        original = manifest.read_bytes()
        read_bytes = Path.read_bytes
        def unreadable(path):
            if path == manifest:
                raise PermissionError("fixture unreadable manifest")
            return read_bytes(path)
        for missing in (True, False):
            with self.subTest(missing=missing):
                if missing:
                    manifest.unlink()
                    result, output, errors = self.render(self.staged)
                    manifest.write_bytes(original)
                else:
                    with patch.object(Path, "read_bytes", unreadable):
                        result, output, errors = self.render(self.staged)
                self.assertEqual(result, 2, errors)
                self.assertIn("evidence manifest verification failed:", errors)
                self.assertNotIn('"input_digests"', output)
                self.assertFalse((self.f.root / "rendered").exists())

    def test_dirty_tracked_source_and_registration_refuse_render(self):
        from joulewise import quiet_predicate_campaign as campaign
        for name in (campaign.HARNESS_PATHS[0], campaign.PROTOCOL_PATH):
            with self.subTest(name=name):
                path = self.f.repo / name
                original = path.read_bytes()
                path.write_bytes(original + b"\n")
                result, output, errors = self.render(self.staged)
                path.write_bytes(original)
                self.assertEqual(result, 2, errors)
                self.assertNotIn('"input_digests"', output)
                self.assertFalse((self.f.root / "rendered").exists())

    def test_staged_probe_and_install_still_refuse_after_render(self):
        from types import SimpleNamespace
        result, output, errors = self.render(self.staged)
        self.assertEqual(result, 0, errors)
        for probe in (False, True):
            with self.subTest(probe=probe), self.f.installer_environment():
                args = SimpleNamespace(plan=self.staged, python=sys.executable,
                                       render_only=None, launchd_probe=probe)
                with self.assertRaisesRegex(self.engine.Refused, "plan_outside_custody_root"):
                    self.engine.validate_install(args, Path(__file__).resolve().parents[1])
        self.assertFalse(self.f.plan_path.exists())

    def test_wrong_chain_sidecar_refuses_render(self):
        Path(self.f.plan.chain_sha256_path).write_text("0" * 64 + "\n")
        result, output, errors = self.render(self.staged)
        self.assertEqual(result, 2)
        self.assertIn("chain_sha256 mismatch", errors)
        self.assertNotIn('"input_digests"', output)
        self.assertFalse((self.f.root / "rendered").exists())

    def test_wrong_manifest_digest_refuses_render(self):
        Path(self.f.plan.chain_path).with_name("evidence_manifest.json").write_text("{}\n")
        result, output, errors = self.render(self.staged)
        self.assertNotEqual(result, 0)
        self.assertIn("manifest_sha256 mismatch", errors)
        self.assertNotIn('"input_digests"', output)

    def test_registration_without_chain_binding_refuses_render(self):
        from unittest.mock import patch
        from joulewise import night_gate
        with patch.dict(night_gate.RULED_REGISTRATIONS,
                        {night_gate.QPE01_PILOT_REGISTRATION_SHA256: {"binds_chain": False}}):
            result, output, errors = self.render(self.staged)
        self.assertEqual(result, 2)
        self.assertIn("registration is not a chain-bound ruled registration", errors)
        self.assertNotIn('"input_digests"', output)


    def test_missing_chain_sidecar_refuses_render_typed(self):
        Path(self.f.plan.chain_sha256_path).unlink()
        result, output, errors = self.render(self.staged)
        self.assertEqual(result, 2)
        self.assertIn("chain_sha256 sidecar unreadable", errors)
        self.assertNotIn('"input_digests"', output)

    def test_undecodable_evidence_wrapper_refuses_before_legacy_inspection(self):
        """A corrupt byte anywhere — including on the payload marker itself — must
        not route the wrapper to the branch that executes it (Opus 12 #1, fresh
        eyes 17 F1). The render harness asserts the chain never ran."""
        wrapper = Path(self.f.plan.chain_path)
        for corruption in (lambda raw: raw + b"\n# \xff\xfe corrupt\n",
                           lambda raw: raw.replace(b"NIGHT_PAYLOAD_KIND", b"NIGHT_PAYLOAD_KIN\xff")):
            with self.subTest(corruption=corruption.__code__.co_firstlineno):
                sealed = wrapper.read_bytes()
                try:
                    wrapper.write_bytes(corruption(sealed))
                    result, output, errors = self.render(self.staged)
                finally:
                    wrapper.write_bytes(sealed)
                self.assertEqual(result, 2, errors)
                self.assertIn("night wrapper is not valid UTF-8", errors)
                self.assertNotIn('"input_digests"', output)

    def test_stray_refusal_documents_refuse_admission(self):
        """Every refusal document the driver reports from existence alone refuses
        admission (refuter 10 F1; fresh eyes 17 F2: the driver's glob, not a list)."""
        night = self.f.custody / "night"
        night.mkdir(exist_ok=True)
        for name in ("calibration-refusal.json", "refusal-01.json", "calibration-refusal.json.4242.json"):
            with self.subTest(name=name):
                (night / name).write_text("{}\n")
                try:
                    result, output, errors = self.render(self.staged)
                finally:
                    (night / name).unlink()
                self.assertEqual(result, 3, errors)
                self.assertIn("existing night records: " + name, errors)


class EvidencePlanPublicationTests(unittest.TestCase):
    def setUp(self):
        from tests.test_gen_evidence_night import EvidenceFixture
        from scripts import gen_evidence_night
        from joulewise import night_agent_install
        self.engine = night_agent_install
        self.f = EvidenceFixture()
        self.addCleanup(self.f.close)
        self.staged = self.f.root / "staging" / "night_plan.json"
        self.staged.parent.mkdir()
        os.replace(self.f.plan_path, self.staged)
        gen_evidence_night.generate(self.staged)

    def test_staged_render_then_atomic_publication_passes_bindings(self):
        raw = self.staged.read_bytes()
        os.replace(self.staged, self.f.plan_path)
        self.assertFalse(self.staged.exists())
        self.assertEqual(self.f.plan_path.read_bytes(), raw)
        bindings = self.engine.evidence_probe_bindings(self.f.plan, self.f.plan_path, sys.executable)
        self.assertEqual(bindings["plan_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(bindings["input_digests"][str(self.f.plan_path)],
                         "sha256:" + hashlib.sha256(raw).hexdigest())

    def test_staged_plan_refused_before_publication(self):
        self.assertFalse(self.f.plan_path.exists())
        with self.assertRaisesRegex(ValueError, "^evidence plan not at its published path$"):
            self.engine.evidence_probe_bindings(self.f.plan, self.staged, sys.executable)

    def test_symlinked_custody_root_passes_with_literal_and_resolved_plan_paths(self):
        # Opus 90 S1 / refuter 89 R1 / fresh-eyes 92 R1: the installer hands the
        # probe the RESOLVED published path while the wrapper seals the literal
        # (unresolved) one; identity is compared resolved, so BOTH spellings of
        # the same inode pass. The alias is built explicitly (a symlink inside
        # the fixture) so the test does not depend on the host's /tmp layout.
        from dataclasses import replace
        from scripts import gen_evidence_night
        link = self.f.root / "custody-link"
        link.symlink_to(self.f.custody)
        plan = replace(self.f.plan, custody_root=str(link),
                       chain_path=str(link / "chain.zsh"), chain_sha256_path=str(link / "chain.zsh.sha256"))
        for path in (Path(self.f.plan.chain_path), Path(self.f.plan.chain_sha256_path),
                     Path(self.f.plan.chain_path).with_name("evidence_manifest.json"),
                     Path(self.f.plan.chain_path + ".chain-source.sha256")):
            path.unlink(missing_ok=True)
        from joulewise.night_plan_writer import night_plan_json_bytes
        self.staged.write_bytes(night_plan_json_bytes(plan))
        gen_evidence_night.generate(self.staged)
        literal = link / "night_plan.json"
        os.replace(self.staged, literal)
        resolved = literal.resolve()
        self.assertNotEqual(str(resolved), str(literal))
        self.assertEqual(resolved, self.f.custody.resolve() / "night_plan.json")
        for spelling in (literal, resolved):
            bindings = self.engine.evidence_probe_bindings(plan, spelling, sys.executable)
            self.assertEqual(bindings["plan_sha256"], hashlib.sha256(literal.read_bytes()).hexdigest())
        chain = Path(plan.chain_path).read_text()
        from joulewise import night_gate
        self.assertEqual(night_gate.chain_literal(chain, "EVIDENCE_PLAN_PATH"), str(literal))


class EvidenceProbeReceiptTests(unittest.TestCase):
    def setUp(self):
        from tests.test_gen_evidence_night import EvidenceFixture
        from scripts import gen_evidence_night
        from joulewise import night_agent_install
        from types import SimpleNamespace
        self.engine = night_agent_install
        self.f = EvidenceFixture()
        self.addCleanup(self.f.close)
        gen_evidence_night.generate(self.f.plan_path)
        self.prepared = SimpleNamespace(plan=self.f.plan, plan_path=self.f.plan_path, python=sys.executable)
        bindings = self.engine.evidence_probe_bindings(self.f.plan, self.f.plan_path, sys.executable)
        self.receipt = dict(bindings, schema='joulewise.night_evidence_probe_receipt.v1', outcome='ok', refusal_code=None,
            started_epoch_s=time.time()-1, finished_epoch_s=time.time(), verify_only=True, collect_started=False,
            load_started=False, cleanup_proven=True, launchd_label=self.engine.probe_label(self.f.plan.plan_id),
            verify_stdout=['VERIFY_ONLY_OK manifest='+bindings['manifest_sha256']])
        self.path = self.f.custody / 'night_probe_receipt.json'

    def validate(self, value=None):
        self.path.write_text(json.dumps(self.receipt if value is None else value))
        return self.engine.validate_probe_receipt(self.prepared)

    def test_all_bound_fields_are_rederived_and_custody_keys_forbidden(self):
        self.assertEqual(self.validate(), self.receipt)
        for key in ('plan_sha256', 'measurement_head', 'chain_sha256', 'chain_source_sha256', 'manifest_sha256',
                    'manifest_digests', 'harness_digests', 'registration_sha256', 'registration_label',
                    'driver_python', 'chain_python', 'powermetrics_path', 'input_digests', 'launchd_label', 'verify_stdout'):
            with self.subTest(key=key):
                with self.assertRaises(self.engine.Refused):
                    self.validate({**self.receipt, key: 'forged'})
        for key in ('custody_budget_s', 'custody_elapsed_s', 'observations'):
            with self.assertRaisesRegex(self.engine.Refused, 'custody fields'):
                self.validate({**self.receipt, key: 0})
        for change in ({'outcome':'refused'}, {'refusal_code':'error'}, {'verify_only':1}, {'collect_started':True},
                       {'load_started':True}, {'cleanup_proven':False}, {'finished_epoch_s':time.time()-21601},
                       {'finished_epoch_s':time.time()+61}, {'finished_epoch_s':True}, {'started_epoch_s':-1}):
            with self.assertRaises(self.engine.Refused):
                self.validate({**self.receipt, **change})

    def test_mtime_staleness_and_kind_mismatch_refuse(self):
        self.validate()
        os.utime(self.path, (time.time()-21601, time.time()-21601))
        with self.assertRaisesRegex(self.engine.Refused, 'mtime stale'):
            self.engine.validate_probe_receipt(self.prepared)
        with self.assertRaisesRegex(self.engine.Refused, 'kind does not match'):
            self.validate({**self.receipt, 'schema':'joulewise.night_probe_receipt.v1'})
        Path(self.f.plan.chain_path).write_text('# calibration\n')
        with self.assertRaisesRegex(self.engine.Refused, 'kind does not match'):
            self.validate()

    def test_dispatch_ambiguity_and_changed_tracked_file_refuse(self):
        chain = Path(self.f.plan.chain_path)
        original = chain.read_text()
        for extra in ('export NIGHT_PAYLOAD_KIND=quiet_predicate_evidence\n', 'export CALIBRATION_LEDGER=/tmp/x\n'):
            chain.write_text(original+extra)
            with self.assertRaisesRegex(self.engine.Refused, 'probe payload kind ambiguous'):
                self.validate()
        chain.write_text(original)
        target = self.f.repo / 'scripts/sample_quiet_predicate_evidence.py'
        target.write_text(target.read_text()+'\n# modified\n')
        with self.assertRaisesRegex(self.engine.Refused, 'measurement_head'):
            self.validate()

    def test_wrapper_manifest_registration_and_sidecar_authentication_refuse_tampering(self):
        from unittest import mock
        from joulewise import night_gate
        chain = Path(self.f.plan.chain_path)
        original = chain.read_bytes()
        sidecar = Path(self.f.plan.chain_sha256_path)
        original_sidecar = sidecar.read_bytes()
        manifest = chain.with_name('evidence_manifest.json')
        manifest_bytes = manifest.read_bytes()
        for field, replacement in (('EVIDENCE_CHAIN_SOURCE_SHA256','0'*64), ('EVIDENCE_MANIFEST_SHA256','0'*64),
                                   ('EVIDENCE_PLAN_PATH','/tmp/substituted-plan.json')):
            with self.subTest(field=field):
                lines=original.decode().splitlines()
                lines=[f"export {field}='{replacement}'" if line.startswith('export '+field+'=') else line for line in lines]
                chain.write_text('\n'.join(lines)+'\n')
                sidecar.write_text(self.engine._digest(chain)+'  '+chain.name+'\n')
                with self.assertRaises(ValueError):
                    self.engine.evidence_probe_bindings(self.f.plan,self.f.plan_path,sys.executable)
        chain.write_bytes(original)
        sidecar.write_text('0'*64+'\n')
        with self.assertRaisesRegex(ValueError,'chain_sha256'):
            self.engine.evidence_probe_bindings(self.f.plan,self.f.plan_path,sys.executable)
        sidecar.write_bytes(original_sidecar)
        manifest.write_bytes(manifest_bytes+b' ')
        with self.assertRaisesRegex(ValueError,'manifest_sha256'):
            self.engine.evidence_probe_bindings(self.f.plan,self.f.plan_path,sys.executable)
        manifest.write_bytes(manifest_bytes)
        with mock.patch.dict(night_gate.RULED_REGISTRATIONS, {}, clear=True):
            with self.assertRaisesRegex(ValueError,'ruled registration'):
                self.engine.evidence_probe_bindings(self.f.plan,self.f.plan_path,sys.executable)



if __name__ == "__main__":
    unittest.main()
