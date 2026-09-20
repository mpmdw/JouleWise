```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"findings","completion":"complete","summary":"Implemented.","workspace":{"base_requested":"010ff2e0","base_mode":"exact","head_start":"010ff2e0","head_end":"010ff2e0","upstream_end":"0959e613","branch":"fix/2026-09-19-installer-render-only-evidence"},"pathspec":["joulewise/night_agent_install.py","tests/test_night_agent_install.py","tests/test_gen_evidence_night.py","tests/test_install_night_agent.py"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"pending_verification"},"verification":[{"id":"V1","kind":"lint","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[]}
```

## Change

Evidence render-only now dispatches by payload kind, verifies the wrapper sidecar, sealed manifest, and chain-bound registration, then prints hashes of the supplied plan, wrapper, and manifest without invoking the chain. `verify_manifest` does not require the published plan path.

Staged and published plans produce identical digest values; the plan’s dictionary key follows its actual location. Calibration output is byte-pinned by a regression, and its retained branch is AST-identical to the original. Unknown payloads retain legacy inspection behavior.

Seven focused regressions pass, covering publication, no chain invocation, refusal preservation, calibration output, and unknown payloads. The no-chain regression fails against the original `validate_install`. The end-to-end fixture exercises generation → staged installer render → atomic publication → probe bindings → published installer render.

**Same-signature audit, final file lines:**

| Site | Finding and evidence reachability |
|---|---|
| `joulewise/night_agent_install.py:1171` | Original calibration-source existence check remains inside the legacy render branch. Evidence render bypasses it. |
| `joulewise/night_agent_install.py:760–770` | Ledger, pin, and source reads in calibration probe bindings are mandatory reads, not existence-based dispatch. Evidence install/probe routes around them through payload-kind checks. |
| `scripts/run_night.py:619` | Reservation argv discovery includes existing files. Evidence install/render/probe bypasses this calibration helper; night run, uninstall, and courier do not call it. |
| `scripts/run_night.py:626` | Adjacent existence check for `calibration-refusal.json`. Evidence night-run result preparation reaches it at line 3198. Evidence probe dispatch bypasses it; install/uninstall do not reach it. |
| `scripts/run_night.py:281` | Adjacent glob-based discovery includes calibration refusal artifacts. Evidence night completion and courier inventory reach it, including the refusal-presence decision at line 1342. |
| `scripts/install_night_agent.sh` | No ledger, pin, or calibration-source existence dispatch. |
| `scripts/night_courier.py` | Absent at this head. Courier implementation is in `scripts/run_night.py`, audited above. |

No other ledger/pin/calibration-source existence selector was found.

## Verification notes

All commands ran from this worktree using the requested interpreter, with `PYTHONDONTWRITEBYTECODE=1` and worktree-local `R7F_CORPUS_ROOT`.

Requested six-module command, exit **1**:

```sh
set -o pipefail
PATH=/Users/edr/code/JouleWise/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=$PWD python3 -m unittest tests.test_night_agent_install tests.test_install_night_agent tests.test_gen_evidence_night tests.test_run_night tests.test_quiet_predicate_campaign tests.test_night_gate -v 2>&1 | tee /tmp/renderonly-six.log | tail -25
```

Tail:

```text
T3: prose must not steer an operator back to the scientific pre-registration. ... ok

======================================================================
FAIL: test_cleanup_refusal_reports_the_failure_it_interrupted (tests.test_night_agent_install.LaunchdAccessProbeTests.test_cleanup_refusal_reports_the_failure_it_interrupted)
The finally block fails closed WITHOUT discarding the diagnostic.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-fix-renderonly/tests/test_night_agent_install.py", line 1866, in test_cleanup_refusal_reports_the_failure_it_interrupted
    self.assertIn("probe bootout absence unproven", str(caught.exception))
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'probe bootout absence unproven' not found in 'probe process census survivor or unknown:  sysmon request failed with error: sysmond service not found\npgrep: Cannot get process list\n'

======================================================================
FAIL: test_staged_installer_render_publication_probe_bindings_and_published_render (tests.test_gen_evidence_night.EvidenceGeneratorTests.test_staged_installer_render_publication_probe_bindings_and_published_render)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-fix-renderonly/tests/test_gen_evidence_night.py", line 211, in test_staged_installer_render_publication_probe_bindings_and_published_render
    self.assertEqual(list((self.f.custody / "night").iterdir()), [])
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: True is not false

----------------------------------------------------------------------
Ran 461 tests in 996.717s

FAILED (failures=2, skipped=9)
```

The E2E failure came from an earlier, already-loaded assertion incorrectly requiring the custody directory to be absent. Existing rendering creates it empty. The corrected assertion passed standalone, in the seven-test focused run, and in the complete generator module under the final touched tier. The traceback displays updated source alongside the earlier loaded assertion.

Requested quick tier, exit **1**:

```sh
PATH=/Users/edr/code/JouleWise/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=$PWD python3 scripts/quick_suite.py --tier quick --workers 4
```

```text
PASS tests.test_reauthor_clean seconds=33.607
STALE WEIGHT tests.test_reauthor_clean seconds=33.607 weight=0.334 ratio=100.62
PASS tests.test_calibration_ledger_custody seconds=50.533
STALE WEIGHT tests.test_calibration_ledger_custody seconds=50.533 weight=1.080 ratio=46.79
QUICK SUMMARY tier=quick modules=153 excluded=89 failures=1 seconds=102.352 result=FAIL
```

Repository-required final touched tier, exit **1**:

```sh
PATH=/Users/edr/code/JouleWise/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=$PWD python3 scripts/quick_suite.py --tier touched --since 010ff2e0 --workers 4
```

```text
MODULE FAIL tests.test_night_agent_install tests=68 failures=1 errors=0 skipped=0 seconds=743.769
SHARD SUMMARY index=1/1 modules=1 tests=68 failures=1 errors=0 skipped=0 result=FAIL
RERUN /Users/edr/code/JouleWise/.venv/bin/python3 /Users/edr/code/JouleWise-wt-fix-renderonly/scripts/quick_suite.py --module tests.test_night_agent_install
QUICK SUMMARY tier=touched modules=168 excluded=74 failures=3 seconds=745.906 result=FAIL
```

Remaining failures:

- **Environmental `/bin/ps` restriction:** independently confirmed `PermissionError: Operation not permitted`. Affects `tests.test_axi_controller_events.AxiControllerEventTests.test_campaign_prebundle_process_failure_retains_identity_receipt_and_row` and `test_campaign_zero_exit_without_finalized_bundle_is_dispatch_failure`.
- **Environmental process census:** `LaunchdAccessProbeTests.test_cleanup_refusal_reports_the_failure_it_interrupted` receives `pgrep: Cannot get process list`; reproduced separately.
- **Watchdog timing:** `tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go` exceeded eight seconds in the touched tier, but passed standalone and in the six-module run.

The final touched tier passed the complete installer CLI, evidence generator, evidence campaign, and derivation-only fiducial modules. Canonical discovery was not run because the repository explicitly excludes canonical-checkout-dependent modules from delegated seats.

## Residual risk

Lead verification remains pending because the suites are not fully green. `origin/main` advanced to `0959e613` during testing; local HEAD stayed at `010ff2e0`. No commits or pushes were made.

Next step: lead review of the four-file diff, then replay the census-dependent failures in the lead-controlled environment before committing by pathspec.