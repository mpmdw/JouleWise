"""Run one test module and write its outcome IDs as JSON (S1-REGRESSION-01 §7.3 check 8).

Usage: python3 -B run_module_ids.py <dotted.module> <out.json>
Run from the worktree root. Records every test id with outcome ok/skip/fail/error/xfail/xpass.
"""
import json
import os
import sys
import time
import unittest


class _Recorder(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcomes = {}

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes[test.id()] = "ok"

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcomes[test.id()] = "skip"

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.outcomes[test.id()] = "fail"

    def addError(self, test, err):
        super().addError(test, err)
        self.outcomes[test.id()] = "error"

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.outcomes[test.id()] = "xfail"

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.outcomes[test.id()] = "xpass"

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            kind = "fail" if issubclass(err[0], test.failureException) else "error"
            self.outcomes[subtest.id()] = kind


def main():
    module, out = sys.argv[1], sys.argv[2]
    sys.path.insert(0, os.getcwd())  # like `python -m unittest` from the worktree root
    start = time.time()
    suite = unittest.defaultTestLoader.loadTestsFromName(module)
    runner = unittest.TextTestRunner(stream=sys.stderr, verbosity=1, resultclass=_Recorder)
    result = runner.run(suite)
    counts = {}
    for outcome in result.outcomes.values():
        counts[outcome] = counts.get(outcome, 0) + 1
    with open(out, "w") as fh:
        json.dump({"module": module, "tests_run": result.testsRun, "counts": counts,
                   "outcomes": result.outcomes, "seconds": round(time.time() - start, 3)},
                  fh, indent=1, sort_keys=True)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
