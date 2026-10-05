# Block-4 lane X8 (Sol 6.1 xhigh): restore the sealed prewindow script (X6 P1) and close the 40 fixture and registration failures (X6 S1)

Worktree: /Users/edr/code/JouleWise-wt-dd5-x8 (branch `lane/2026-10-05-b4-x8` at bda1c180 = PR #483 head with origin/main merged, which now includes #481 and #482). Scratch /tmp/dd5-x8/ only. Leave changes uncommitted; never push. No sudo, launchctl, powermetrics or Metal. Never touch the four pinned estimator files.

## 1. P1 (lead ruling, binding)

`scripts/prewindow_check.sh` is pinned by the sealed Revision-6 registration (`prewindow_check_sha256`). `scripts/issue_calibration_acceptance_generation.py:1481` also checks the dwell script's sha256 against that pin. Restore the file byte-identical to origin/main (`git show origin/main:scripts/prewindow_check.sh`). Move the two behaviours the X1 lane put in it into the T-0 caller:

- the CPU-based maintenance census (`joulewise/prewindow.py`, ruling 1.15);
- report-only load average at T-0 (memo A-F6).

The T-0 path (`scripts/capture_t0_step.py:418` and `:621`, `joulewise/arm_readiness_evidence_t0.py:948`) must stop running `prewindow_check.sh` for its dwell. It runs a T-0 dwell of its own, `joulewise/prewindow.py --t0-wait` or a small new script; choose the smaller design. The T-0 dwell has the same clean-dwell semantics and caps as the shell script (read them from it). It uses the CPU census, and it records the load average without vetoing on it. The T-0 evidence pins that dwell's script/module sha256 and its frozen command instead of the shell script's. The night path (`scripts/run_night.py:3609`) keeps calling the sealed shell script unchanged. Remove the `JOULEWISE_PREWINDOW_T0_CPU_ADMISSION` environment switch. `tests.test_revision6_seal` must pass. Update `tests/test_prewindow_check.py` and `tests/test_capture_t0_step.py` accordingly.

## 2. S1: the 40 failures in `/Users/edr/night-archive/desk-day-v5/x6-triage.md`

Work the rows classified "Stale fixture" (roots, plan schema, clock inputs, started record, battery time), "Stale assertion" and "Registration" (paper supply receipt, git fixture helper, read replay, classified writer IO, battery consumers, battery primitive). Row 42 (sealed pin) is item 1. Rows 25, 26 and 62 (watchdog) are closed: the lead ran them outside the sandbox and they pass 9/9 at bda1c180 and at main, so they were a sandbox artefact. Do not touch them.

Rules:

- Fix shared fixtures to the current production contract: independent roots, chain-pin context, `receipt_class`, residual frequency and authenticated sizing inputs, the current `chain.started` shape, and a battery reading consistent with the synthetic wall time.
- Do not relax a production validator to make a fixture pass. If a test's expected refusal changed only in order (row 39), assert the refusal that is now reached, and say why the earlier refusal is still covered elsewhere or add a test that reaches it.
- Registrations must be honest and exact, without widening exemptions:
  - read-replay rows name the call, the function and the ordinal;
  - shifted IO sites are listed by their new exact location;
  - battery consumers are registered under the raw-boundary semantics policy;
  - the four git initialisers go through the shared helper.
- `configs/paper_supply/supply_map.json`: regenerate the receipt digests with the repository's own generator, if one exists (find it). Do not hand-edit a digest. If no generator exists, FLAG this item with the exact digests you computed and how you computed them. Keep every acceptance validator unchanged.
- Since bda1c180 merges #481 and #482, first rerun all 44 listed IDs (excluding 25/26/62) at this head, plus `tests.test_controller_battery_float tests.test_controller_g2b_attachment tests.test_v5_pack_regen`, and report any new failure in the same table form.

Report a table: test ID → classification → change → final result. Finish in this turn; FLAG what you cannot close.

WRITE_SCOPE: ["scripts/prewindow_check.sh", "joulewise/prewindow.py", "scripts/t0_prewindow_dwell.py", "scripts/capture_t0_step.py", "joulewise/arm_readiness_evidence_t0.py", "joulewise/arm_readiness.py", "tests/test_prewindow_check.py", "tests/test_capture_t0_step.py", "tests/test_arm_readiness.py", "tests/test_arm_readiness_lifecycle.py", "tests/test_arm_readiness_evidence_t0.py", "tests/test_arm_readiness_integration.py", "tests/test_night_agent_install.py", "tests/test_install_night_agent.py", "tests/test_launch_window.py", "tests/test_launch_window_realization_recheck.py", "tests/test_bracket_binding_cli.py", "tests/test_v5_block4_x1.py", "tests/test_v5_block4_x2.py", "tests/test_v5_s1_desk_closeout.py", "tests/test_v5_s1_qualification.py", "tests/fixtures/custody_read_replay_allowlist.json", "tests/test_authentication_io.py", "tests/test_battery_float_consumers.py", "configs/paper_supply/supply_map.json", "tests/test_paper_custody.py", "tests/test_paper_rendering.py", "tests/test_custody_mode_inventory.py", "tests/fixtures/epoch_bootstrap/**", "tests/test_revision6_seal.py"]
