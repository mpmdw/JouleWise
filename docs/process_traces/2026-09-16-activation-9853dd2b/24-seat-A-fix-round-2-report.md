```json
{
  "schema":"claude-codex-report/v1",
  "genre":"implementation",
  "status":"findings",
  "completion":"complete",
  "summary":"Killed M3 and M1 with real-process regressions; added strict pre-reserve mode. All 96 requested tests pass; quick tier retains baseline AXI failures.",
  "workspace":{"base_requested":"308600e36f038b255796d638fdf65c2886739e47","base_mode":"exact","head_start":"308600e36f038b255796d638fdf65c2886739e47","head_end":"308600e36f038b255796d638fdf65c2886739e47","upstream_end":"308600e36f038b255796d638fdf65c2886739e47","branch":"feat/2026-09-16-reserve-hang-core"},
  "pathspec":["docs/contracts/calibration_ledger_append.md","scripts/reserve_calibration_window_bracket.py","tests/calibration_exits_fixtures/custody_hang.py","tests/test_calibration_custody_worker.py","tests/test_calibration_ledger_custody.py"],
  "unowned_dirty":[],
  "verdict":{"implementation":"implemented","acceptance":"pending_verification"},
  "verification":[
    {"id":"M3","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_custody_worker.CustodyWorkerTests.test_protocol_requires_exact_request_complete_response_and_normal_exit tests.test_calibration_custody_worker.CustodyWorkerTests.test_valid_worker_cannot_inherit_parent_writable_descriptor","cwd":"/tmp/rh-core-fix2-m3","observed":{"result":"fail","exit_code":1,"tail":["----------------------------------------------------------------------","Ran 2 tests in 0.244s","","FAILED (failures=8)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=8\\)"}},
    {"id":"M1","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_ledger_custody.ReservationCustodyDeadlineTests.test_successful_custody_then_expiry_at_reservation_append_boundary","cwd":"/tmp/rh-core-fix2-m1","observed":{"result":"fail","exit_code":1,"tail":["----------------------------------------------------------------------","Ran 1 test in 3.088s","","FAILED (failures=1)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=1\\)"}},
    {"id":"X3_BASE","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_ledger_custody.StrictReservationReadinessTests","cwd":"/tmp/rh-core-fix2-base","observed":{"result":"fail","exit_code":1,"tail":["----------------------------------------------------------------------","Ran 4 tests in 5.409s","","FAILED (failures=4)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=4\\)"}},
    {"id":"HEAD_KILLS","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -k protocol_requires_exact -k valid_worker_cannot_inherit -k successful_custody_then_expiry -k StrictReservationReadinessTests tests.test_calibration_custody_worker tests.test_calibration_ledger_custody","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 7 tests in 9.093s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"FOCUSED","kind":"suite","cmd":"set -o pipefail; TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_ledger_custody tests.test_calibration_custody_worker tests.test_validate_powermetrics_fiducial_derivation_only tests.test_authentication_io 2>&1 | tee /tmp/rh-core-fix2-suite.log | tail -4","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 96 tests in 132.196s","","OK","KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"QUICK","kind":"suite","cmd":"set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 scripts/quick_suite.py --tier quick --workers 4 2>&1 | tee /tmp/rh-core-fix2-quick.log | tail -5","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["PASS tests.test_calibration_ledger_custody seconds=36.994","STALE WEIGHT tests.test_calibration_ledger_custody seconds=36.994 weight=1.080 ratio=34.25","PASS tests.test_reauthor_clean seconds=36.478","STALE WEIGHT tests.test_reauthor_clean seconds=36.478 weight=0.334 ratio=109.22","QUICK SUMMARY tier=quick modules=153 excluded=83 failures=1 seconds=97.742 result=FAIL"]},"expected":{"exit_code":0,"tail_regex":"result=PASS"}},
    {"id":"BUILD","kind":"build","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -k generated_contract_projection_and_runbook_anchors_are_fresh tests.test_calibration_exits && PYTHONPYCACHEPREFIX=/tmp/rh-core-fix2-pycache python3 -m compileall -q scripts joulewise; result=$?; echo rc=$result; exit $result","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 0.001s","","OK","rc=0"]},"expected":{"exit_code":0,"tail_regex":"rc=0"}},
    {"id":"AXI_BASE","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_axi_controller_events","cwd":"/tmp/rh-core-fix2-base","observed":{"result":"fail","exit_code":1,"tail":["----------------------------------------------------------------------","Ran 7 tests in 21.296s","","FAILED (failures=2)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"SCOPE","kind":"inspection","cmd":"git status --short && git diff --stat && git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[" M docs/contracts/calibration_ledger_append.md"," M scripts/reserve_calibration_window_bracket.py"," M tests/calibration_exits_fixtures/custody_hang.py"," M tests/test_calibration_custody_worker.py"," M tests/test_calibration_ledger_custody.py"," docs/contracts/calibration_ledger_append.md      |  15 +++"," scripts/reserve_calibration_window_bracket.py    |  26 +++-"," tests/calibration_exits_fixtures/custody_hang.py |  38 ++++++"," tests/test_calibration_custody_worker.py         |  61 ++++++++-"," tests/test_calibration_ledger_custody.py         | 157 ++++++++++++++++++++++-"," 5 files changed, 289 insertions(+), 8 deletions(-)"]},"expected":{"exit_code":0,"tail_regex":"5 files changed"}}
  ],
  "flags":[{"id":"ENV1","kind":"environment","level":"nonblocking","text":"Quick tier fails only tests.test_axi_controller_events: two campaign-identity assertions also fail on the 308600e3 base copy.","needs":"Lead rerun in the normal process-identity environment."}]
}
```

## Change

- **X1:** Launch assertions now run on the test thread. A real worker bootstrap attempts to write through an explicitly inheritable parent descriptor before processing a valid request. Scratch bytes remain unchanged with descriptor closure.
- **X2:** A real reservation CLI probe completes custody verification, then expires the deadline during receipt preparation. It verifies timeout refusal and unchanged ledger/pin bytes. No production changes were needed for X1 or X2.
- **X3:** Added `--pre-reserve-strict`, implied by `--verify-only`. Blocked readiness refuses before retry or recovery. Strict success emits readiness diagnostics first; verify-only therefore emits two JSON records. Legacy execution still permits recovery/resumption.

Five scoped files remain uncommitted for the lead. Source digests remained frozen during verification; no bytecode or workspace Git metadata writes.

## Verification notes

Separate temporary copies applied M3 and M1. The X3 copy restored the CLI from `308600e3` using read-only `git show`. Its tests reach the old retry behavior instead of failing on an unknown flag.

Executed failing assertions:

- M3: `AssertionError: False is not True`
- M3 descriptor probe: `AssertionError: b'CHILD INHERITED WRITER FD' != b'parent-only bytes' : real worker inherited the parent's writable descriptor`
- M1: `AssertionError: 0 != 2 : late expiry returned 0; appended_events=['append-intent', 'bracket-session-open']`
- X3 interrupted claim: `AssertionError: 0 != 2 : strict refusal missing: exit=0, ledger_changed=True`

Quick-tier AXI failures reproduce on the base with `campaign start identity unavailable`. No early return.