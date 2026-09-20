```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"findings","completion":"complete","summary":"D1-D5 landed.","workspace":{"base_requested":"c72a7ae7","base_mode":"exact","head_start":"c72a7ae7","head_end":"c72a7ae7","upstream_end":"0959e613","branch":"fix/2026-09-19-installer-render-only-evidence"},"pathspec":["joulewise/night_agent_install.py","joulewise/night_gate.py","tests/test_night_agent_install.py","tests/test_gen_evidence_night.py","tests/test_install_night_agent.py","tests/test_night_gate.py","tests/test_evidence_arm_sequence.py"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"pending_verification"},"verification":[],"flags":[{"id":"F1","kind":"verification_gap","level":"nonblocking","text":"Census/timeout.","needs":"Replay"}]}
```

## Change

| Delta | Status | Implementation and regression |
|---|---|---|
| D1 | Landed | Render checks the sealed published-path literal without resolving it. Printed `input_digests` match published probe bindings; `chain_sha256` is separate. Advisory-only comment added. A resealed wrapper naming another custody root refuses before plist writes. |
| D2 | Landed | Ambiguous declarations raise `Refused(2)` instead of entering legacy inspection. Duplicate, mixed, and unknown declarations are covered. Legacy subprocess failures become typed reservation-inspection refusals. Binary/unavailable-chain fallback remains. |
| D3 | Landed | Relative registration paths are joined to `measurement_root`. The evidence gate regression changes cwd to `/tmp`, performs real file reads, restores cwd, and asserts GO. Existing registration-reader fixtures follow the new path rule. |
| D4 | Landed | `EvidenceArmSequenceTests.test_staged_arm_reaches_install_render` exercises generation, staged rendering, publication, real bindings, real supervisor/verify-only chain, receipt admission, published rendering, and install validation. It checks sealed bytes, digests, PIDs, and plist topology. Render spies reject chain, launchctl, or courier execution. |
| D5 | Landed | Covers expired t0, stale plans, wrong measurement HEAD, existing results, exactly one calibration argv-only execution, repeated byte-identical rendering, missing/unreadable manifests, tracked-input mutations, and staged probe/install refusal after successful rendering. Calibration golden stdout remains covered. |

The composed test launches the supervisor through the fixture interpreter. Only `_probe_group_absent` is stubbed; supervisor cleanup logic, receipt production, bindings, manifest verification, and rendering execute normally. Its docstring explains both historical counterfactuals.

All seven changed paths are authorized. No commits or pushes. `git diff --check` passes.

## Verification notes

The final requested run passed **161 tests in 111.454s**, exit **0**:

```sh
set -o pipefail
PATH=/Users/edr/code/JouleWise/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=$PWD python3 -m unittest tests.test_night_agent_install.EvidenceRenderOnlyTests tests.test_gen_evidence_night tests.test_evidence_arm_sequence tests.test_night_gate tests.test_install_night_agent -v 2>&1 | tee /tmp/renderonly-r2-requested-final.log | tail -20
```

An earlier run exposed two old registration-fixture expectations; those were corrected before the complete successful rerun.

The touched runner has no exclusion option. To honor the paper-build prohibition, its selection was filtered in memory; no runner file was modified:

```sh
set -o pipefail
PATH=/Users/edr/code/JouleWise/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=$PWD python3 -c '
from scripts import quick_suite as q
original = q.select_modules
def without_paper(*args, **kwargs):
    selected, excluded = original(*args, **kwargs)
    selected.pop("tests.test_paper_build", None)
    excluded["tests.test_paper_build"] = "user prohibition: paper-build tests"
    return selected, excluded
q.select_modules = without_paper
raise SystemExit(q.main())
' --tier touched --since 010ff2e0 --workers 4 2>&1 | tee /tmp/renderonly-r2-touched.log | tail -20
```

Exit **1**; tail:

```text
test_zero_exit_routes_require_commit_or_verified_uninstall (test_night_agent_install.TransactionTests.test_zero_exit_routes_require_commit_or_verified_uninstall) ... ok

======================================================================
FAIL: test_cleanup_refusal_reports_the_failure_it_interrupted (test_night_agent_install.LaunchdAccessProbeTests.test_cleanup_refusal_reports_the_failure_it_interrupted)
The finally block fails closed WITHOUT discarding the diagnostic.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-fix-renderonly/tests/test_night_agent_install.py", line 1866, in test_cleanup_refusal_reports_the_failure_it_interrupted
    self.assertIn("probe bootout absence unproven", str(caught.exception))
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'probe bootout absence unproven' not found in 'probe process census survivor or unknown:  sysmon request failed with error: sysmond service not found\npgrep: Cannot get process list\n'

----------------------------------------------------------------------
Ran 75 tests in 940.502s

FAILED (failures=1)
MODULE FAIL tests.test_night_agent_install tests=75 failures=1 errors=0 skipped=0 seconds=940.502
SHARD SUMMARY index=1/1 modules=1 tests=75 failures=1 errors=0 skipped=0 result=FAIL
RERUN /Users/edr/code/JouleWise/.venv/bin/python3 /Users/edr/code/JouleWise-wt-fix-renderonly/scripts/quick_suite.py --module tests.test_night_agent_install
QUICK SUMMARY tier=touched modules=172 excluded=71 failures=3 seconds=943.806 result=FAIL
```

The three failing modules were:

- **`test_night_agent_install`:** only the named environmental sysmond/census failure above.
- **`test_axi_controller_events`:** two campaign tests returned 2 instead of 1. Direct fixture replay reported `campaign start identity unavailable`; the underlying `/bin/ps` call independently raised `PermissionError: Operation not permitted`.
- **`test_run_night`:** `test_blocked_journal_never_blocks_deadline_or_grants_go` exceeded its eight-second watchdog. Unlike round 1, it also failed in isolated replay:

```sh
PATH=/Users/edr/code/JouleWise/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=$PWD python3 -m unittest tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go -v
```

Replay result: **1 test, 8.008s, one failure**. No changes were made to that test or driver.

Full logs: [requested tests](/tmp/renderonly-r2-requested-final.log), [touched tier](/tmp/renderonly-r2-touched.log), [watchdog replay](/tmp/renderonly-r2-watchdog-replay.log).

## Residual risk

Acceptance remains pending the lead’s replay of the census-dependent failures outside the sandbox and adjudication of the persistent watchdog timeout. Next step: review the seven-file diff, then replay those three failing modules. The arm-sequence evidence is fixture validation, not live launchd or hardware validation.