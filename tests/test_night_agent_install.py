"""Transactional installer instrument (D10).

The fake is a subprocess, never a wrapper around real launchctl. Its marker
files are the liveness oracle; query diagnostics and mutator return codes are
independent of those files. These tests characterize the instrument and pin the
system-Python package imports required by the uninstall entrypoint.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


LABELS = ("com.joulewise.night", "com.joulewise.night.deadman")


FAKE_LAUNCHCTL_SOURCE = r'''
import json
import sys
import time
from pathlib import Path

root = Path(__file__).parent
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

if action == "print":
    fault = directive.get("fault")
    if fault == "hang":
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

    def invoke(self, action, label, uid=None, timeout=5):
        domain = "gui/" + str(os.getuid() if uid is None else uid)
        args = ([domain, str(self.root / (label + ".plist"))]
                if action == "bootstrap" else [domain + "/" + label])
        return subprocess.run([str(self.executable), action] + args,
                              capture_output=True, text=True, timeout=timeout,
                              check=False)


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
                        self.assertEqual(loaded, self.fake.loaded(label))
                        self.assertEqual(not loaded, self.fake.loaded(other))
                        self.assertEqual(before + 1, len(self.fake.calls()))
            self.fake.directive(label, "print")

    def test_hung_queries_are_logged_and_preserve_actual_state(self):
        for label in LABELS:
            for loaded in (False, True):
                with self.subTest(label=label, loaded=loaded):
                    self.fake.set_loaded(label, loaded)
                    self.fake.directive(label, "print", fault="hang", hang_s=30)
                    before = len(self.fake.calls())
                    with self.assertRaises(subprocess.TimeoutExpired):
                        self.fake.invoke("print", label, timeout=1)
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


if __name__ == "__main__":
    unittest.main()
