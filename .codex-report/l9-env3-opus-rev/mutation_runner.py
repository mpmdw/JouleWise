"""Run one mutant (or 'BASELINE'): install mutated whole_window in-process, run the seat's
test file and the reviewer checks; print a one-line JSON verdict."""
import io, json, sys, types, unittest
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
from mutants import MUTANTS
name = sys.argv[1]
src = (ROOT / "joulewise/whole_window.py").read_text(encoding="utf-8")
if name != "BASELINE":
    for old, new in MUTANTS[name]:
        assert src.count(old) == 1, (name, src.count(old))
        src = src.replace(old, new)
import joulewise
mod = types.ModuleType("joulewise.whole_window")
mod.__file__ = str(ROOT / "joulewise/whole_window.py")
sys.modules["joulewise.whole_window"] = mod
exec(compile(src, str(ROOT / "joulewise/whole_window.py"), "exec"), mod.__dict__)
joulewise.whole_window = mod
import reviewer_checks
checks = reviewer_checks.run_all(mod)
stream = io.StringIO()
suite = unittest.defaultTestLoader.loadTestsFromName("tests.test_whole_window_inverted_corner_clamp")
res = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
failed = [str(t[0]).split(" ")[0] for t in res.failures + res.errors]
seat_killed = not res.wasSuccessful()
rev_killed = [k for k, (ok, _m) in checks.items() if not ok]
print(json.dumps({"mutant": name, "seat_tests_run": res.testsRun, "seat_killed": seat_killed, "seat_failed": failed,
                  "reviewer_killed_by": rev_killed, "reviewer_msgs": {k: m for k, (ok, m) in checks.items() if not ok},
                  "killed": seat_killed or bool(rev_killed)}))
