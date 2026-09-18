```json
{
  "schema":"claude-codex-report/v1",
  "genre":"implementation",
  "status":"clean",
  "completion":"complete",
  "summary":"Addressed all contract and execution findings; nine authorized files remain unstaged. No commits or early return.",
  "workspace":{"base_requested":"649eefd2","base_mode":"exact","head_start":"649eefd2c9c19c5af48381da217bee7ee73af465","head_end":"649eefd2c9c19c5af48381da217bee7ee73af465","upstream_end":"6ea6ecf1012fca20bc091e1e2f131be5004f74c4","branch":"feat/2026-09-17-night-gate-quiet-admission"},
  "pathspec":["docs/contracts/night_quiet_admission.md","joulewise/night_gate.py","scripts/gen_derivation_night.py","scripts/run_night.py","tests/test_arm_retry.py","tests/test_gen_derivation_night.py","tests/test_night_gate.py","tests/test_quiet_admission.py","tests/test_run_night.py"],
  "unowned_dirty":[],
  "verdict":{"implementation":"implemented","acceptance":"ready"},
  "verification":[
    {"id":"V1","kind":"suite","cmd":"set -o pipefail\nTMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_gate tests.test_quiet_admission tests.test_night_plan_writer tests.test_arm_retry tests.test_run_night tests.test_gen_derivation_night 2>&1 | tee /tmp/jw-fix2-focused-final.log | tail -4","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 321 tests in 51.698s","","OK (skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=9\\)"}},
    {"id":"V2","kind":"build","cmd":"PYTHONPYCACHEPREFIX=/tmp/jw-compile python3 -m compileall -q scripts joulewise; echo rc=$?","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["rc=0"]},"expected":{"exit_code":0,"tail_regex":"rc=0"}},
    {"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_derivation_night.py --check; echo rc=$?","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS generated derivation-night wrapper region matches","rc=0"]},"expected":{"exit_code":0,"tail_regex":"PASS generated derivation-night wrapper region matches"}},
    {"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/jw_fix2_counterfactuals.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS 14 assertion kills; unmodified generator HEAD control passes; no watchdog kills"]},"expected":{"exit_code":0,"tail_regex":"PASS 14 assertion kills"}},
    {"id":"V5","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_gen_derivation_night.QuietPlanGeneratorTests 2>&1 | tail -4","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 4 tests in 0.236s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V6","kind":"inspection","cmd":"git diff --stat\ngit status --short","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[" docs/contracts/night_quiet_admission.md |  24 ++--"," joulewise/night_gate.py                 |   7 +-"," scripts/gen_derivation_night.py         |  11 +-"," scripts/run_night.py                    |  13 ++-"," tests/test_arm_retry.py                 |  14 +++"," tests/test_gen_derivation_night.py      |  53 +++++++--"," tests/test_night_gate.py                |  29 +++++"," tests/test_quiet_admission.py           |  33 ++++++"," tests/test_run_night.py                 | 201 +++++++++++++++++++++++++++++++-"," 9 files changed, 348 insertions(+), 37 deletions(-)"," M docs/contracts/night_quiet_admission.md"," M joulewise/night_gate.py"," M scripts/gen_derivation_night.py"," M scripts/run_night.py"," M tests/test_arm_retry.py"," M tests/test_gen_derivation_night.py"," M tests/test_night_gate.py"," M tests/test_quiet_admission.py"," M tests/test_run_night.py"]},"expected":{"exit_code":0,"tail_regex":"9 files changed"}},
    {"id":"V7","kind":"inspection","cmd":"git diff --check\ngit diff --cached --name-only","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags":[]
}
```

## Change

- **C-F3:** Journal rerun protection applies only to v4. `test_legacy_write_once_tuple_matches_base` compares the legacy tuple with `a90ab4e8`; `test_v2_existing_quiet_journal_reaches_legacy_evaluator` proves the counterexample proceeds. A companion verifies v4 still refuses.
- **C-F2:** Failed or empty boot observations yield `night_probe_error` in v4 only. `test_v4_failed_or_empty_boot_probe_is_probe_error` covers both; `test_changed_boot_identity_is_terminal_boot_clock` preserves the different-UUID refusal. The legacy byte-comparison regression now includes identical injected boot failures.
- **C-F1:** Moved definitions into an ordered Terms section immediately after the introduction. First-use inspection is below.
- **E-F1:** Regression 3 exercises all ten specified daemons and an arbitrary name, asserting each contributes its full CPU delta.
- **E-F2:** Regression 4 now tests stale `%CPU` 90 with zero delta and `%CPU` 0 with a large delta.
- **E-F3:** Regression 6 directly checks distinct parser identities for PID reuse and excludes a delta across them.
- **E-F4:** Regression 8 exercises downstream driver timing at GO offsets 0 and 540, checks all four derived boundaries and the bind deadline, and checks expiry after three samples followed by a hang. Late-start and rollback companions have bounded fake clocks and assert bind expiry.
- **E-F5:** Both predecessor-digest and same-candidate-history digest cases are now inside regression 9.
- **E-F6:** `ready()` explicitly polls with zero timeout. Regression 10 uses a real indefinitely sleeping worker, checks readiness within 50 ms, observes census evaluation during the hang, verifies expiry, and proves reaping.
- **E-F7:** Complete generator fixtures now exercise both bounds and their accepted boundary. Authoring refuses insufficient runway or window with `GenerationRefusal`, including malformed v4 templates; it no longer silently extends the template’s window.

| Term | Definition line | First-use line |
|---|---:|---:|
| t0 | 13 | 13 |
| GO | 14 | 14 |
| Bind window/allocation | 15 | 15 |
| Sample interval | 16 | 16 |
| Consecutive quiet samples | 17 | 17 |
| Busy-core equivalent | 18 | 18 |
| Observer | 19 | 19 |
| Terminal/WAIT | 20 | 20 |
| Attribution | 21 | 21 |
| Cutoff authority | 22 | 22 |

## Verification notes

Counterfactuals used `/tmp` copies of `649eefd2` with the new tests. Exact failing assertions included:

```text
C-F3:
AssertionError: Tuples differ: ('rec[88 chars]tarted', 'chain.exited', 'courier.json', 'quiet_samples.jsonl') != ('rec[88 chars]tarted', 'chain.exited', 'courier.json')
AssertionError: RuntimeError not raised

C-F2:
AssertionError: 'night_refused_boot_clock' != 'night_probe_error'

E-F6 join() mutant:
AssertionError: True is not false : ready() blocked beyond 50 ms on a real hung worker

E-F7 runway mutant 21a:
AssertionError: GenerationRefusal not raised

E-F7 window mutant 21b:
AssertionError: GenerationRefusal not raised
```

For C-F3, the missing `RuntimeError` means the evaluator sentinel was never reached.

The supplied HEAD already used non-blocking readiness and rejected both `build_spec` bounds. Those execution findings were test-strength defects on that HEAD; the unmodified generator control passes. Undersized-window authoring did reproduce a real pre-fix failure.

All targeted mutants now fail by assertions, including 05/14 without watchdog termination. An initial full run exposed my overly strict census pickup assertion; it now allows the supervisor’s bounded 50 ms pickup tick. The final generator exception wrapping also passed the four-test rerun. Detailed counterfactual logs are in `/tmp/jw-fix2-evidence/`.