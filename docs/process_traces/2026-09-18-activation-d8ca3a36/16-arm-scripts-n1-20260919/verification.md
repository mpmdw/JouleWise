# Implementation verification — 2026-09-18

Workspace HEAD at intake: `1907b53870f5db8878ec4c93723c701ef6ea6ffe`;
branch `arm/2026-09-19-n1-prep`; initial worktree clean. The baseline's
canonical self-digest, computed without its `manifest_sha256` field, matched
the supplied `sha256:997b0723c5f8a4d6769d9c7c18f6ff50b26a56acef2321646a826a97f393a333`.
No arm script or Python evidence helper was executed. No live custody,
clone, staging, LaunchAgent, launchctl, mail, sudo or measurement action was
performed. Source inspection used only this worktree and its Git metadata.

## Exact verification commands

All commands below use the repository root as cwd. The shell syntax and
Python compilation commands passed (rc 0). Compilation's local bytecode
was removed from the allowed artifact directory afterward.

```zsh
for script in docs/process_traces/2026-09-18-activation-d8ca3a36/16-arm-scripts-n1-20260919/*.zsh; do zsh -n "$script" || exit; done
python3 -B -m py_compile docs/process_traces/2026-09-18-activation-d8ca3a36/16-arm-scripts-n1-20260919/step4a-successor-evidence.py
rg -l production_custody_inventory tests
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_rehearse_t0_unattended tests.test_arm_retry
git diff --check
```

The inventory search returned `tests/test_rehearse_t0_unattended.py`.
The focused test command passed: 39 tests, zero failures/errors, `OK`.
`git diff --check` passed. These are fixture tests, not live evidence.

The required delegated-seat touched suite was invoked exactly as follows;
its complete selections, exclusions, timings, failures and replay commands
are retained in `quick-suite.txt` (the completed `.log` captures were
renamed to `.txt` so Git does not ignore them; the commands below remain
the exact commands executed).

```zsh
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/quick_suite.py --tier touched --since 1907b53870f5db8878ec4c93723c701ef6ea6ffe --workers 2 > docs/process_traces/2026-09-18-activation-d8ca3a36/16-arm-scripts-n1-20260919/quick-suite.log 2>&1
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/quick_suite.py --module tests.test_axi_controller_events > docs/process_traces/2026-09-18-activation-d8ca3a36/16-arm-scripts-n1-20260919/axi-replay.log 2>&1
PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'import os; from joulewise.measurement_liveness import observe_identity; print(observe_identity(os.getpid()))'
/bin/ps -p $$ -o lstart=
```

The isolated controller replay failed the same two tests (7 tests total):
`test_campaign_prebundle_process_failure_retains_identity_receipt_and_row`
and `test_campaign_zero_exit_without_finalized_bundle_is_dispatch_failure`.
Both observed exit 2 instead of expected 1 after
`error: campaign start identity unavailable`. The read-only identity probe
returned `Identity(state='UNKNOWN', start_time=None)`; the direct ps check
was denied with `operation not permitted: /bin/ps` (rc 127). No permission
bypass or out-of-scope production/test fix was attempted.

The touched tier also found a directly relevant inventory pin that the
requested lowercase filename search does not find (the test uses the
`readiness.PRODUCTION_CUSTODY_INVENTORY` constant). Exact isolated replay:

```zsh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_arm_readiness_schemas.ProductionCustodyResolverTests.test_shipped_inventory_pins_all_four_retained_deployments
```

It fails at `tests/test_arm_readiness_schemas.py:1711`: `7 != 8`, rc 1.
The next assertion pins the exact deployment-id/root mapping, which also
needs the new 09-19 entry. **NEEDS_SCOPE:** add
`tests/test_arm_readiness_schemas.py` to the write allowlist so the expected
count can become eight and the expected map can include the new clone.
That file is untouched. All independent script and document work is done;
S8's all-inventory-tests-green requirement is blocked on that expansion.

The full canonical suite was not run: this is a bench-script/documentation
package with no production module changes, scripts must not be executed by
this seat, and the delegated workflow assigns full-suite/live verification
to the lead. The targeted tests and required touched tier cover this seat's
verification; their limitations remain explicit.

## Static inspection

Seven zsh files passed syntax checks. All nine embedded Python heredocs
were compiled with Python's `compile(..., 'exec')`, never evaluated.
Every zsh step sources its sibling env, every cd is guarded, and no script
contains a temporary-directory path. The 09-17 notice-body generator is
byte-identical to the desk block. Baseline comparisons proved the entire
handback prefix (including recovery, R1, D-182 and arm-census policy), the
scientific decision rule, Purpose's census block, all prior Executed
history, and the standing tail beginning `Then loop under D-181` unchanged.
Only current-night coordinates are substituted in Where / Next lane.

The inventory parses as JSON and its new row has exactly the predecessor
field set, with `pending-arm` in notes. Source checks confirmed the staged
render uses the future published plan path, so step 5's complete installed
versus rendered ProgramArguments comparison is valid.

The old pre-registration re-pin instruction is retained verbatim, with a
factual note that PR #355 already performed the re-pin. Other unchanged
rule discrepancies and the missing 09-17 inventory row are recorded in
README-sequence.md. The helper cannot supply a successor count absent a
magistrate's explicit evidence file and underlying review.

## Lease attribution ruling required

Exact checker invocation:

```zsh
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/bridge scope-check --baseline .codex-bridge/baselines/arm-prep-n1-20260919-d8ca3a36.json --expect-digest sha256:997b0723c5f8a4d6769d9c7c18f6ff50b26a56acef2321646a826a97f393a333 --scope docs/process_traces/2026-09-18-activation-d8ca3a36/16-arm-scripts-n1-20260919:subtree docs/process/NIGHT_HANDBACK.md configs/production_custody_inventory.json --lease-id lease-71090f0edbb041b588fb68bf1d77f3f5 > docs/process_traces/2026-09-18-activation-d8ca3a36/16-arm-scripts-n1-20260919/scope-check.json
```

Result: rc 4, `ATTRIBUTION_INDETERMINATE`, reason `no_governing_lease`;
every reported path is `in_scope`, HEAD unchanged. The local acquire event
for the supplied lease id exists, but its script-directory entry is
`match: exact` with literal `/**` appended. The checker expects a subtree
entry for that allowlist. No lease metadata was modified.

**NEEDS_RULING:** the lead must reconcile the runner's literal wildcard
lease with the prompt's subtree authority and rerun its attribution check.
Changing the declared scope to an exact literal would incorrectly exclude
the scripts; changing lead-owned lease metadata from this seat is outside
scope. Recommendation: repair/reconcile the runner-side scope encoding,
preserving this failed check, before accepting the handback.

## Final touched-suite result

`QUICK SUMMARY tier=touched modules=161 excluded=77 failures=3 seconds=945.119 result=FAIL`
(rc 1). These are three failing modules, four failing test cases:

- `tests.test_axi_controller_events`: the two process-identity failures
  reproduced in `axi-replay.txt` as described above.
- `tests.test_arm_readiness_schemas`: the out-of-scope seven-entry inventory
  pin, independently reproduced as described above.
- `tests.test_night_agent_install`: 57 tests, one failure at line 1865 in
  `LaunchdAccessProbeTests.test_cleanup_refusal_reports_the_failure_it_interrupted`.
  Expected the mocked bootout refusal; observed `probe process census
  survivor or unknown: sysmon request failed with error: sysmond service not
  found` / `pgrep: Cannot get process list`. Its launchctl is a fake; the
  unmocked process census is unavailable in this sandbox. The remaining
  56 installer tests passed. No full-module replay was repeated.

All started verification processes completed before handback. Final
acceptance remains blocked by the inventory-test scope request and the
runner lease's literal-wildcard encoding. No out-of-scope path was edited,
no script was run, and HEAD remains the requested base.
