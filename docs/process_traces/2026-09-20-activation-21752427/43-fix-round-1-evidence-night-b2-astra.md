```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"findings","completion":"partial","summary":"D1-D8 fixed; requested checks pass; canonical incomplete.","workspace":{"base_requested":"798bced1","base_mode":"exact","head_start":"798bced1","head_end":"798bced1","upstream_end":"798bced1","branch":"feat/2026-09-20-evidence-night-b2"},"pathspec":["joulewise/evidence_night.py","tests/test_evidence_night.py","docs/contracts/evidence_night_entry.md","docs/process/NIGHT_HANDBACK.md"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"pending_verification"},"verification":[],"flags":[{"id":"F1","kind":"environment","level":"nonblocking","text":"Canonical interrupted after process-identity failures.","needs":"Rerun at bench."}]}
```

## Change

Implemented all eight closures. No commits; HEAD and upstream remain unchanged. Only the four authorized paths changed.

| Closure | Implementation and regression proof | `798bced1` → fixed |
|---|---|---|
| D1 | Shared veto observer runs immediately before publication; preserves earlier verdict and records the second observation per attempt. New directive, STOP, standdown, NO, and unreadable directives refuse. Composition asserts the second record. | FAIL → PASS |
| D2 | Valid non-owner issues recorded without veto; malformed issues refuse. Owner-only scope, unread comments, and query limit documented. | FAIL → PASS |
| D3 | Missing, non-directory, or symlink magistrate root refuses. | FAIL → PASS |
| D4 | Production provenance recorded; rehearsal veto evidence cannot authorize real launchctl. | FAIL → PASS |
| D5 | `notice.txt` contains only the sendable body, beginning with check provenance. Stdout headers are separate; rerun bytes remain identical. | FAIL → PASS |
| D6 | Notice must be strictly newer than every sealed artifact and `check.json`. | FAIL → PASS |
| D7 | Baselines belong to individual attempts; verification selects only the newest attempt. Malformed earlier and legacy baselines remain untouched. | FAIL → PASS |
| D8 | Missing-record error names `notice`; injection fixture asserts no marker file; handbook clause added. | FAIL → PASS |

The non-owner-counts-as-veto mutant was **KILLED**.

Requested verification tails, all exit 0:

```text
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_night
Ran 87 tests in 250.326s
OK

PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.11 -B -m unittest tests.test_evidence_night
Ran 87 tests in 225.478s
OK

PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_arm_sequence tests.test_arm_retry tests.test_night_gate
Ran 108 tests in 5.168s
OK
```

The untouched base module suite also passed: `Ran 79 tests in 219.846s / OK`.

Counterfactual replay loaded the base module entirely in memory, without checkout changes:

```python
import contextlib, io, subprocess, types, unittest
from tests import test_evidence_night as t

fixed = t.entry
names = [n for n in dir(t.LifecycleTests)
         if n.startswith("test_d") and n[6:7].isdigit()]
names += ["test_notice_refreshes_draft_and_prints_plain_text"]

for label, source in [
    ("798bced1", subprocess.check_output(
        ["git", "show", "798bced1:joulewise/evidence_night.py"], text=True)),
    ("fixed", None),
]:
    if source is not None:
        t.entry = types.ModuleType("base_evidence_night")
        exec(compile(source, "798bced1:joulewise/evidence_night.py", "exec"),
             t.entry.__dict__)
    else:
        t.entry = fixed
    for name in names:
        sink = io.StringIO()
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            result = unittest.TextTestRunner(stream=sink).run(
                unittest.TestSuite([t.LifecycleTests(name)]))
        assert result.wasSuccessful() == (label == "fixed"), sink.getvalue()
        print(label, name, "PASS" if result.wasSuccessful() else "FAIL")
```

Protected handbook regions were compared directly with `798bced1`:

```text
Executed→EOF                  4c71305c61b0a8e3fea6b8fb9ec8b871 UNCHANGED
ARM-RETRY-POLICY lines 68–144  fc6e3a97a4a5c7a650264f9facb7eed8 UNCHANGED
```

`git diff --check` passed. Final stat:

```text
 docs/contracts/evidence_night_entry.md |  80 ++++++++---
 docs/process/NIGHT_HANDBACK.md         |   9 +-
 joulewise/evidence_night.py            | 173 ++++++++++++++--------
 tests/test_evidence_night.py           | 255 +++++++++++++++++++++++++++++----
 4 files changed, 403 insertions(+), 114 deletions(-)
```

## Verification notes

After the full module runs started, three tests received counterfactual cleanup/assertion-order adjustments. Those final tests were rerun on both interpreters: `Ran 3 tests in 3.342s / OK` and `Ran 3 tests in 3.170s / OK`.

The additional canonical command was **interrupted, exit 130**:

```text
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest discover -s tests
```

It showed four failure markers accompanied by `error: campaign start identity unavailable`. Sandbox probes independently returned `operation not permitted: ps` and `pgrep: Cannot get process list`. No final unittest summary was produced; shutdown also reported unavailable Metal hardware. See the [canonical log](/tmp/b2-canonical.log). The known supervision-watchdog case was not investigated.

## Residual risk

Evidence remains fixture-based and PROVISIONAL. Next: lead reviews the four-file diff and reruns the canonical suite where process identity is observable.