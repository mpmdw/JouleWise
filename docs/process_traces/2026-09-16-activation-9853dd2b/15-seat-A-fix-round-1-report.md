```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Fixed F1–F3 and added counterfactual regressions; 230-test suite passes; quick tier retains a reproduced baseline AXI failure.",
  "workspace": {"base_requested":"376dd35f859c69bcd17f2f8c06c6d397e67817a6","base_mode":"exact","head_start":"376dd35f859c69bcd17f2f8c06c6d397e67817a6","head_end":"376dd35f859c69bcd17f2f8c06c6d397e67817a6","upstream_end":"376dd35f859c69bcd17f2f8c06c6d397e67817a6","branch":"feat/2026-09-16-reserve-hang-core"},
  "pathspec": ["docs/contracts/calibration_ledger_append.md","joulewise/calibration_ledger.py","scripts/validate_powermetrics_fiducial.py","tests/test_authentication_io.py","tests/test_calibration_custody_worker.py","tests/test_validate_powermetrics_fiducial_derivation_only.py"],
  "unowned_dirty": [],
  "verdict": {"implementation":"implemented","acceptance":"pending_verification"},
  "verification": [
    {"id":"V1","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -k ordinary_abandon -k BoundedBackupDiagnosticTests tests.test_validate_powermetrics_fiducial_derivation_only tests.test_calibration_custody_worker","cwd":"/tmp/rh-core-fix1-base","observed":{"result":"fail","exit_code":1,"tail":["----------------------------------------------------------------------","Ran 6 tests in 4.616s","","FAILED (failures=5)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=5\\)"}},
    {"id":"V2","kind":"suite","cmd":"set -o pipefail; TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_exits tests.test_calibration_ledger_custody tests.test_calibration_custody_worker tests.test_validate_powermetrics_fiducial_derivation_only tests.test_calibration_ledger tests.test_authentication_io 2>&1 | tee /tmp/rh-core-fix1-suite-final.log | tail -4","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 230 tests in 623.464s","","OK (skipped=1)","KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=1\\)"}},
    {"id":"V3","kind":"suite","cmd":"set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 scripts/quick_suite.py --tier quick --workers 4 2>&1 | tee /tmp/rh-core-fix1-quick.log | tail -5","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["PASS tests.test_ssh_transport seconds=0.235","STALE WEIGHT tests.test_ssh_transport seconds=0.235 weight=0.001 ratio=235.14","PASS tests.test_reauthor_clean seconds=43.487","STALE WEIGHT tests.test_reauthor_clean seconds=43.487 weight=0.334 ratio=130.20","QUICK SUMMARY tier=quick modules=153 excluded=83 failures=1 seconds=106.139 result=FAIL"]},"expected":{"exit_code":0,"tail_regex":"result=PASS"}},
    {"id":"V4","kind":"build","cmd":"PYTHONPYCACHEPREFIX=/tmp/rh-core-pycache python3 -m compileall -q scripts joulewise; result=$?; echo rc=$result; exit $result","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["rc=0"]},"expected":{"exit_code":0,"tail_regex":"rc=0"}},
    {"id":"V5","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_axi_controller_events","cwd":"/tmp/rh-core-fix1-base","observed":{"result":"fail","exit_code":1,"tail":["----------------------------------------------------------------------","Ran 7 tests in 15.072s","","FAILED (failures=2)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V6","kind":"inspection","cmd":"git status --short && git diff --stat && git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[" M docs/contracts/calibration_ledger_append.md"," M joulewise/calibration_ledger.py"," M scripts/validate_powermetrics_fiducial.py"," M tests/test_authentication_io.py"," M tests/test_calibration_custody_worker.py"," M tests/test_validate_powermetrics_fiducial_derivation_only.py"," docs/contracts/calibration_ledger_append.md        |  8 +-"," joulewise/calibration_ledger.py                    |  3 +"," scripts/validate_powermetrics_fiducial.py          |  9 ++-"," tests/test_authentication_io.py                    | 16 ++--"," tests/test_calibration_custody_worker.py           | 89 ++++++++++++++++++++--"," ...lidate_powermetrics_fiducial_derivation_only.py | 88 +++++++++++++++++++++"," 6 files changed, 191 insertions(+), 22 deletions(-)"]},"expected":{"exit_code":0,"tail_regex":"6 files changed"}}
  ],
  "flags": [{"id":"ENV1","kind":"environment","level":"nonblocking","text":"Quick tier fails only tests.test_axi_controller_events: two assertions following 'campaign start identity unavailable'. Both reproduce at 376dd35f.","needs":"Lead rerun of quick tier in the normal process-identity environment."}]
}
```

## Change

- F1: Ordinary abandonment checks expiry after hashing and forwards the same deadline to finalization. Two expiry regressions preserve ledger/pin bytes and add no intent; a positive control appends an abandoned receipt.
- F2: All three bounded disabled-backup shortcuts emit the exact diagnostic once. State, public hashing, and public snapshot tests prohibit custody filesystem access and worker invocation.
- F3: Glossed “reaps” and “PID” at first use. Refreshed only the eight authentication-guard line numbers.

Append audit in [the writer](/Users/edr/code/JouleWise-wt-rh-core/scripts/validate_powermetrics_fiducial.py):

| Line / call | Verdict |
|---|---|
| 1526 `repair_calibration_ledger` | Immediate caller expiry check; synchronous recovery. |
| 1591 `claim_bracket_session_slot` | Checked; deadline forwarded. |
| 1609 `append_pending_receipt` | Checked; deadline forwarded. |
| 1628 `abort_bracket_session` | Synchronous cleanup; no custody pass. |
| 1639 `finalize_attempt_receipt` | Fixed: checked and forwarded. |
| 1680 `finalize_bracket_session_slot` | Checked; deadline forwarded. |
| 1713 `abort_bracket_session` | Terminal cleanup after finalization; no new custody pass. |
| 1737 `finalize_attempt_receipt` | Checked; deadline forwarded. |

[Reservation line 344](/Users/edr/code/JouleWise-wt-rh-core/scripts/reserve_calibration_window_bracket.py:344) forwards the deadline to `append_bracket_session_receipt`. All five custody-verifying ledger append functions check immediately before `_locked_append`. Neither CLI directly calls an intent writer or `_locked_append`.

No workspace Git metadata writes; commits remain lead-owned. Six scoped files remain uncommitted; final source digests match the frozen test input. No bytecode or unowned changes.

## Verification notes

The counterfactual copy restored all six changed files using read-only `git show 376dd35f:<path>`, then overlaid only the six added tests. Both F1 expiry cases and all three F2 diagnostic cases failed; the positive control passed. Failing assertions:

`AssertionError: None != <RefusalCode.LEDGER_CUSTODY_TIMEOUT: 'calibration_ledger_custody_timeout'> : expired abandonment appended ['append-intent', 'finalization']; ledger_changed=True`

`AssertionError: '' != 'custody_backup_roots_disabled: /Users/edr[85 chars]ic\n'`

The first combined run had one failure: `0.20019454199064057 not less than 0.2` in the existing spawn test. Replaced its sleep race with a blocked-launch barrier and a 2-second liveness backstop, retaining late-child reaping assertions; the final combined rerun passed.

Quick tier remains red only for the two baseline AXI failures documented above. No early return.