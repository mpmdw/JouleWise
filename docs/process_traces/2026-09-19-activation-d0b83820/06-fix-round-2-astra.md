```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented the prescribed test-only changes and executed bench acceptance; NEEDS_RULING because the mandated liveness floor still fails correct code under complete scheduler starvation.",
  "workspace": {
    "base_requested": "3df43458",
    "base_mode": "exact",
    "head_start": "3df434586d846b31ebbcd5a02edb0ad5f0cda266",
    "head_end": "3df434586d846b31ebbcd5a02edb0ad5f0cda266",
    "upstream_end": "3df434586d846b31ebbcd5a02edb0ad5f0cda266",
    "branch": "feat/2026-09-18-quiet-predicate-evidence-harness"
  },
  "pathspec": ["tests/test_sample_quiet_predicate_evidence.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_sample_quiet_predicate_evidence.LoadTests.test_late_initial_scheduling_never_catches_up tests.test_sample_quiet_predicate_evidence.LoadTests.test_preempted_burn_exits_on_the_wall_deadline -v",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 2 tests in 0.001s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "/usr/bin/time -p env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_sample_quiet_predicate_evidence -v",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 43 tests in 5.352s", "OK", "real 5.74", "user 3.05", "sys 0.17"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 43 tests[\\s\\S]*OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "/usr/bin/time -p env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_sample_quiet_predicate_evidence -v",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 43 tests in 5.380s", "OK", "real 5.78", "user 3.05", "sys 0.18"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 43 tests[\\s\\S]*OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/quiet-d5-t1-round2/run_acceptance.py real",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 3.709s", "OK", "Ran 1 test in 3.701s", "OK", "Ran 1 test in 3.708s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/quiet-d5-t1-round2/run_acceptance.py mutations",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "cores: Ran 43 tests in 1.632s; FAILED (failures=1); child exit 1",
          "alignment: Ran 43 tests in 5.396s; FAILED (failures=2); child exit 1",
          "observer: Ran 43 tests in 5.175s; FAILED (failures=1); child exit 1",
          "clock: Ran 43 tests in 5.172s; FAILED (failures=1); child exit 1",
          "catchup-capped: Ran 43 tests in 5.246s; FAILED (failures=2); child exit 1",
          "burn-noop: Ran 43 tests in 5.360s; OK; child exit 0"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "All six child suites fail; burn-noop survival must instead be reported"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/quiet-d5-t1-round2/probe_assertions.py clock",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["FAILED (failures=2)", "DIAGNOSTIC clock tests 1 failures 2 errors 0"]},
      "expected": {"exit_code": 1, "tail_regex": "DIAGNOSTIC clock tests 1 failures 2 errors 0"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/quiet-d5-t1-round2/probe_assertions.py catchup-capped",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["FAILED (failures=4)", "DIAGNOSTIC catchup-capped tests 1 failures 4 errors 0"]},
      "expected": {"exit_code": 1, "tail_regex": "DIAGNOSTIC catchup-capped tests 1 failures 4 errors 0"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/quiet-d5-t1-round2/probe_starvation.py StarvationProbe -v",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["AssertionError: 0 not greater than 0.0 : no CPU burned: the real burn profile did no work", "Ran 1 test in 0.002s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "git diff --check && git diff --stat && git status --porcelain && git diff --numstat && git rev-parse HEAD '@{upstream}'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["1 file changed, 56 insertions(+), 15 deletions(-)", " M tests/test_sample_quiet_predicate_evidence.py", "3df434586d846b31ebbcd5a02edb0ad5f0cda266", "3df434586d846b31ebbcd5a02edb0ad5f0cda266"]},
      "expected": {"exit_code": 0, "tail_regex": "tests/test_sample_quiet_predicate_evidence.py"}
    },
    {
      "id": "V10",
      "kind": "inspection",
      "cmd": "shasum -a 256 scripts/sample_quiet_predicate_evidence.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["ac7feecf0fbda8a21adc5aff6fe3b0c6a17da647c093d5dd83738def7cc254d9  scripts/sample_quiet_predicate_evidence.py"]},
      "expected": {"exit_code": 0, "tail_regex": "^ac7feecf0fbda8a21adc5aff6fe3b0c6a17da647c093d5dd83738def7cc254d9"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: the verbatim liveness assertion at tests/test_sample_quiet_predicate_evidence.py:640 fails a correct worker first scheduled at 3.001 s for start=0, duration=3. Both requested defect signatures survive at this zero-service boundary.",
      "needs": "Rule whether to remove or condition the real-load liveness floor, or explicitly accept its scheduler-service assumption. The prescribed block remains unchanged."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "burn-noop survives all 43 tests. No assertion kills it: the controller's loop itself accrues thread CPU. Reported without an unauthorized fix, as instructed.",
      "needs": "Disposition of the uncovered real burn-profile behavior."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Record 10's preempted wake_late_s < .001 pin contradicts correct executed values of approximately .005 and .010. Retained record 11's < .05 pin under the explicit precedence instruction; other stricter pins pass.",
      "needs": ""
    },
    {
      "id": "F4",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Initial scratch mutation copies omitted scripts/run_night.py, causing four import errors and one unrelated collection failure per suite. Added the dependency and reran all six; corrected runs have zero errors. Initial logs retained separately.",
      "needs": ""
    }
  ]
}
```

## Change

Installed record 01a §3’s assertion block verbatim, bracketed `load()` with child rusage, added the fixed startup allowance, and replaced the delivery comment. Added both deterministic regressions and `FakeClock.ratio`, incorporating the compatible stricter pins.

No commit, production edit, power collection, or canonical-root write occurred. Production bytes match HEAD and the starting SHA-256.

## Verification notes

**NEEDS_RULING — F1, blocker.** At `tests/test_sample_quiet_predicate_evidence.py:640`, `claimed_s > 0` still assumes scheduler delivery. Counterfactual input: the correct worker first resumes at **3.001 s**, after its **3 s** window. The deterministic probe executes unchanged `load_worker` with a fake clock; it returns `periods=[]` without error. Feeding that result through the actual test fails the mandated assertion.

Both requested same-signature answers are **FOUND**:

- “real-load assertion fails on correct code under scheduler starvation”: zero-service witness above.
- “assertion keyed to a quantity starvation destroys”: the liveness floor uses `claimed_s`, which that starvation reduces to zero.

The two original, partial-starvation witnesses now pass.

**Ruling question:** should the real-load liveness floor be removed/conditioned, or should this test explicitly assume some scheduler service? Recommendation: remove the unconditional delivery floor and preserve the kernel ceiling; address burn-profile behavior with an independent deterministic assertion under a revised brief. Acceptance closure is blocked; the authorized implementation and requested bench runs are complete.

**F2, should_fix — surviving mutation.** Counterfactual: `burn_profile` returns `lambda count: None` at `scripts/sample_quiet_predicate_evidence.py:767`. All 43 tests pass. The assertion at `tests/test_sample_quiet_predicate_evidence.py:640` measures CPU accounting, including loop overhead, rather than proving that the burn function performed work.

**F3, should_fix — conflicting pin, resolved as instructed.** With `FakeClock.ratio=100`, correct rows have wake lateness approximately `[.005, 0, 0, 0, .010, .010]`. Thus record 10’s `< .001` pin would fail correct code. At `tests/test_sample_quiet_predicate_evidence.py:679`, record 11’s `< .05` remains. No numbers were averaged.

Three real-load measurements, using an otherwise unchanged scratch test with one diagnostic print:

| Run | `charged_s` | `claimed_s` | Difference | Wall time |
|---|---:|---:|---:|---:|
| 1 | 0.643595000 | 0.300128209 | 0.343466791 | 4.113 s |
| 2 | 0.634655000 | 0.300176333 | 0.334478667 | 4.109 s |
| 3 | 0.642103000 | 0.300162583 | 0.341940417 | 4.120 s |

Mutation results below count the corrected scratch runs; every suite ran 43 tests with **zero errors**.

| Mutation | Failures | Failing assertions |
|---|---:|---|
| `cores` | 1 | Real-load pre-launch share guard, `.1` versus `1.0`; propagated through `report["error"]` |
| `alignment` | 2 | `test_absolute_anchor_endpoints_reject_known_arrival_offset`; `test_real_production_rate_anchor_and_clock_step_refusal` |
| `observer` | 1 | `test_observer_cost_includes_known_reaped_child_delta`: `.2` versus `.9` |
| `clock` | 1 | Real-load liveness: `0.0 > 0.0` fails |
| `catchup-capped` | 2 | Late-start total: `.30002` versus `.1`; preempted work-budget ceiling: `.09495 > .050000001` |
| `burn-noop` | 0 | None |

Supplemental diagnostics continued past failed assertions using scratch-only subtests:

- `clock`: **2 failures**, liveness at line 640 and kernel ceiling at line 646: **3.195601 > .92 CPU-s**.
- `catchup-capped`: **4 failures**, total CPU pin at line 658, work-budget ceiling at 662, per-period CPU ceiling at 663, and overshoot ceiling at 666. The per-period witness was **.25002 > .050100001 CPU-s**.

The three archived substitution patterns matched the rebased source exactly; no manual adaptation was needed. The capped catch-up substitution accumulates entitlement through the current boundary, subtracts previously consumed CPU, and caps entitlement at `share × duration`.

Command execution accounting:

- Read-only intake used `pwd`, `git status`, `git log -1`, `cat`, `sed`, `rg`, and `rg --files` across the four requested records, mutation records, repository gates, protocol, orchestration, and affected code. No nested `AGENTS.md` was found.
- Inline `python -B` commands executed the initial deterministic probe, scoped edit, archived-mutant comparison, scratch-copy preparation, dependency repair, and final integrity assertions. These completed successfully.
- V1–V4 executed the focused regressions, module twice, and three isolated real-load runs.
- V5 executed twice: the initial incomplete-copy attempt was discarded for acceptance; the repaired-copy attempt produced the mutation table above.
- V6–V7 executed the supplemental assertion diagnostics.
- The starvation probe first ran without a selector, discovering eight tests: seven passed and the starvation witness failed. V8 then isolated that witness.
- V9–V10 and the inline integrity check confirmed the verbatim block, absence of diagnostic prints, unchanged production bytes, and exclusive scoped diff.
- Repository-wide discovery, hosted CI, independent delta re-audit, and PR/merge gates were **not executed**. This handoff covers the requested focused bench acceptance; the ruling remains unresolved.

Scripts, exact subprocess command records, and logs are retained under [/tmp/quiet-d5-t1-round2](/tmp/quiet-d5-t1-round2). Initial invalid-copy logs are under `incomplete-copy-attempt/`.

## Residual risk

The fixed startup allowance remains `0.5` as directed; observed kernel-minus-worker differences were approximately `0.334–0.343 s`. These bench passes do not establish scheduler-independent liveness or burn-profile coverage.

Next exact step: the lead rules on F1 and dispositions F2 before delta re-audit round 3.