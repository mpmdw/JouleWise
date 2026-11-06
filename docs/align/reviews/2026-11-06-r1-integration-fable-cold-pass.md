# Cold final pass: ALIGN v4 R1 integration head (2026-11-06)

**Verdict: no BLOCKER. One HIGH stays open (carried from the executing review, confirmed). Five new MEDIUMs, five carried MEDIUMs confirmed still open, nine LOWs.** The two HIGH fixes on the lane are real: each of their tests fails on the pre-fix head. Every targeted module and the WP22 full dry run pass on this head. Nothing on this head can corrupt a measurement on its own; the residual risks are (1) a crash during the High Power leg leaving the host at powermode 2 until the next R1 night, and (2) the driver hard-killing the WP15 runtime on the first signal, which can leave runtime-side custody half-written.

Reviewer: Fable 5.1, cold (no prior context on this work). Target: `lane/2026-11-06-v4-r1-integrated@c5cc2d521` versus `origin/lane/2026-11-05-align-pilot10-benign@f3af22b94`. The benign head is content-identical to the merge base `fc83cfe1d` (its one extra commit is the PR #682 merge with an empty tree diff), so the 28-commit, 72-file diff is the whole integration. The council documents carried on the lane (`CHAIR.md`, `LEAD-RULINGS-1.md`) are byte-identical to `lane/2026-11-06-align-v4-design-council@3b3b2a971`.

Nothing restricted was opened, no weights were loaded, nothing ran on the measurement Mac. Every test ran as `nice -n 19 taskpolicy -b /private/tmp/jwsol/venv-both/bin/python` with `TMPDIR=/private/tmp/jwwf-tmp`, in a worktree under `jw-wt/`. I changed no code; the two scratch probes below ran against copies or in-process shims and the worktree was verified clean afterwards.

## What I read

- The full diff of the 72 files, with line-level reading of `scripts/align_r1_rehearsal.py`, `scripts/night_chains/align_r1_rehearsal.zsh`, `joulewise/align/apple/{powermode,r1_runtime_contract,thermal_gates,workload,thermal_desk,stop_precedence,xml_tool_calls,endpoint,campaign,diagnostics,pilot_analysis}.py`, `scripts/align_v4_kit.py`, `scripts/align_v4_session.py`, `scripts/align_v4_thermal_desk.py`, `scripts/validate_align_v4_w1_plan.py`, the regenerated kit files (r1_slots, order manifests, e05/e17/e18) and `docs/align/r1_runtime_contract.md`.
- `CHAIR.md`, `LEAD-RULINGS-1.md`, the executing review and the R1 integration run report.
- Supporting code the claims depend on: `joulewise/bundle.py` (`RunBundleWriter.create`), `joulewise/controller.py` (`_prepare_suite_manifest_for_new_bundle`), `joulewise/environment.py` (`_parse_pmset`), `joulewise/align/apple/thermal.py` (`Sidecar` private attributes used by `_collector_fault`), CPython 3.13.18's `subprocess.run`.

## What I executed

| Check | Result |
|---|---|
| `tests.align.{test_r1_rehearsal, test_r1_runtime_contract}` | 32 + 8 = **40 tests OK** (matches the review's 29 + 3 + 8) |
| `test_v4_kit` 38, `test_v4_w1_plan` 10, `test_thermal_gate` 39, `test_thermal_desk` 24, `test_v4_powermode_record` 7, `test_window_reference_custody` 4, `test_stop_precedence` 4, `test_xml_tool_calls` 22, `test_history_rendering` 11 (2 skipped), `test_v4_estimands` 14, `test_r0_dispositions` 3, `test_attribution_holds` 6, `test_pilot4` 18 (1 skipped), `test_apple_endpoint` 9, `test_r0_checks`, `test_thermal_sidecar` 9 | **all rc=0, OK** |
| `JW_WP22_FULL=1 tests.align.test_v4_w1_synthetic` | **Ran 18 tests in 128.5 s, OK (expected failures=2)**, as claimed |
| Fail-without-fix, driver and chain from `bb878f3b5` copied over the head (then restored; `git status` clean): `test_gated_d_runs_must_arm_the_step_d_t_dead` | **FAILED** (`AssertionError: 0 != 3`) |
| same: `test_zsh_chain_signal_burst_still_restores_automatic` | **FAILED** (`'2' != '0'`: host left in High Power) |
| same: `test_signal_burst_cannot_interrupt_the_automatic_restore` | the test *process* dies with the uncaught `KeyboardInterrupt` (rc 130) before unittest can report. That is the defect manifesting, but note that on the pre-fix driver this test kills the runner rather than reporting a failure. |
| `scripts/align_v4_kit.py --check` | fails closed on exactly the 13 placeholders the run report lists |
| `scripts/validate_align_v4_w1_plan.py` on the committed template | `REFUSED: refused PENDING_R1 placeholder(s): ...` (rc 2), fail-closed |
| `git diff f3af22b94 HEAD -- configs/campaigns/align_pilot_v3` | empty: v3 kit bytes unchanged |
| Probe A (scratch, in-process): a driver-style one-shot handler around `r1._run()` with a runtime that traps TERM and needs 1 s to write its terminal record; TERM sent to driver and runtime | the record is **never written**; the runtime's own child is orphaned. See MEDIUM-1. |
| Contrast deadman arithmetic | (1750 − 516.5751274713251) / 1.13544 = 1086.30 s, as the kit comment says |

## Findings

### HIGH

**HIGH-1 (OPEN, carried from the executing review's HIGH-3; confirmed).** A crash, SIGKILL or power loss during the B leg leaves the AC profile at `powermode 2` until the next *R1* night.
- `scripts/night_chains/align_r1_rehearsal.zsh:37-39` is the only reader of `$MEASUREMENT_ROOT/.align-r1-high-power`; `scripts/align_r1_rehearsal.py:111-119` unlinks it only after a successful restore (correct), and `:137-142` writes it before `pmset -c powermode 2` (correct).
- `joulewise/environment.py:603-609` maps only `lowpowermode 0|1` to `low_power_mode`; `powermode 2` is recorded, not refused, so every other campaign's generic physics gate admits a host left in High Power.
- `pmset -c` writes the persistent AC profile, so the setting survives a reboot.
- ALIGN v4 itself is protected at arm (`scripts/align_v4_kit.py:443-446`) and at the desk (`:432-440`). The exposure is every non-ALIGN night between an R1 crash and the next R1 night, plus any ALIGN W1/D night armed by an operator who skipped the runbook step. The runbook step in the executing review (confirm `AC Power: powermode 0` after any R1 night without a terminal `r1_result.json`) is adequate for the rehearsal; a `run_night` admission check on the declared AC powermode is the right fix before the D-series.

### MEDIUM

**MEDIUM-1 (new): the driver SIGKILLs the WP15 runtime on the first signal, so the runtime gets no grace to close its own custody.**
- `scripts/align_r1_rehearsal.py:83-84` runs every segment through `subprocess.run(..., capture_output=True)`. `:551-560`'s one-shot handler raises `KeyboardInterrupt` inside that call. CPython 3.13's `subprocess.run` handles any exception from `communicate()` with `process.kill()` (SIGKILL) before re-raising; I read the source in the pinned venv.
- Probe A confirms it: under the run_night TERM path (TERM to the group) the runtime receives TERM and the driver's SIGKILL within the same instant; a TERM trap that needs 1 s never completes and the runtime's grandchildren survive as orphans.
- Consequence: the runtime that owns the SMC sidecar, the thermal journal and the segment's output directory cannot write a terminal record, cannot stop a root-owned `powermetrics` it may have started under `sudo` (a non-root `killpg` cannot signal it), and leaves `--output DIR` half-written. The driver's Automatic restore is unaffected (HIGH-1 fix holds), so this is a bad-state and custody-integrity risk, not a powermode risk.
- `docs/align/r1_runtime_contract.md` says nothing about the runtime's obligations on TERM, nor about the driver's kill policy.
- Recommendation: on the first signal, TERM the runtime, wait a bounded period (≤ 20 s, inside run_night's 30 s), then KILL; state in the contract what the runtime must do on TERM and that `DIR` may be incomplete after an abort.

**MEDIUM-2 (new): after a G0 that did not release, H holds are suppressed but G1 is still a blind full-cap wait every turn.**
- `joulewise/align/apple/thermal_gates.py:379-387` (`holds_suppressed`) and `joulewise/align/apple/endpoint.py:311` stop H holds once `episode_reference is None` after a G0 (WP8 F2).
- But `workload.py:518-519` still calls `wait('G1')` each turn, and in `thermal_gates.py:484` a G1 with no episode reference sets `unobserved = True`, so `good` is never true, `limit` is the full `turn_cap_s` (`:531`), and the outcome is `'unobserved'`, which the workload treats as "continue".
- So a member already excluded as X2 spends up to `turns × turn_cap_s` (≤ 900 s at 300 s) of its T_dead idling in G1. No measurement is affected (the member is excluded either way), but it burns Mac wall time and is one of the mechanisms behind the synthetic window's "X2 becomes X7" (run report F2). This is a ruling-1 budget matter. The same reasoning that suppresses H should suppress G1, or the member should stop at G0 timeout.

**MEDIUM-3 (disclosed in the run report; needs the lead's recorded decision before W1): `episode.malformed_tool_call` is a new exclusion class for the 30B JSON path, and the `unsupported_tool_call_format` narrowing leaves the refused-XML-call case (ruling 2(d)) only partly closed.**
- `workload.py:525-530` flags any turn whose endpoint flags carry `malformed_tool_call:` and no budget cut, on both paths; `pilot_analysis.py:178` and `thermal_desk.py:624-627` exclude it. The anchor configs are byte-identical to `83e2dac59` (test passes), but the runtime now applies an exclusion pilots 4-10 did not. One anchor lost reduces U4's df (already 2 at D3; ruling 6); one contrast run lost makes the arm's verdict INCONCLUSIVE (FD:446).
- On the XML (D) path, a call refused as `unsupported_tool_call_format` (`xml_tool_calls.py:183-186`) sets no episode flag, so that trajectory continues with no call and no exclusion. The run report's reason (the marker heuristic fires on ordinary JSON/prose) is sound for the JSON path; for D the only backstop is FD 658's zero-unsupported gate at qualification.
- Not a code defect; a registration decision that must be written down (protocol v4) before W1's desk is read.

**MEDIUM-4 (ruling 22 divergence): `docs/align/pilot_protocol_v4.md` is not on this head.**
- Ruling 22: "land the WP20 draft with PENDING sections before R1, so R1's slot fills land in a document." The draft exists on `lane/2026-11-06-sol-v4-wp20-protocol` (`docs/align/pilot_protocol_v4.md`), which is not an ancestor of `c5cc2d521`. R1's slot record therefore has no protocol document to land in, and the MEDIUM-3 decision has nowhere registered to go. Process item; blocks W1 registration rather than R1 execution.

**MEDIUM-5 (ruling 7 divergence, small): arm checks the AC powermode but records nothing.**
- `scripts/align_v4_session.py:54-62`: `install` reads `pmset -g custom`, compares against `runtime_requirements.ac_powermode` and refuses on mismatch, but neither the observed value nor the pmset text goes into the session/arm record. Ruling 7: "Every arm and every bundle records it." Bundles do (`workload.py:439`, `:813-829`); the arm does not. Cheap to add.

**Carried from the executing review, confirmed still open by reading:**
- M-1 load-journal completeness: `align_r1_rehearsal.py:373-381` requires only a non-empty list.
- M-2 L1 not evaluated in the driver: `:624` records `max_r1_tail_s`; nothing computes `l1_t_dead` or the member fit on the R1 record.
- M-3 kit does not bind r1_slots evidence: `align_v4_kit.py:107-131` reads only `ac_powermode` and `max_r1_tail_s`; `source`, `slots.I_D`, `duty_bar.pass` and `u5.verdict` are not checked, so a `"R1 synthetic rehearsal"` record or a failed duty bar without a recorded fallback admits.
- M-4 ruling 4(b) battery outputs have no contract field.
- M-5 external-volume state is neither refused nor recorded in R1.

### LOW

1. `scripts/align_v4_kit.py:432-440` `validate_powermode_members` treats expected `None` and observed `None` as a match. Only `require_ready:113` and `arm_powermode_check` keep a null-powermode kit from the desk. Refuse expected ∉ {0, 2} there too.
2. `scripts/align_r1_rehearsal.py:541` `output.mkdir(exist_ok=False)` sits before the `try`: a rerun into an existing `$NIGHT_DIR/align-r1` dies with a traceback and writes no `r1_result.json`. The guard was never entered, so there is no High Power exposure; the chain's EXIT trap still restores.
3. `scripts/night_chains/align_r1_rehearsal.zsh:46` passes `--runtime "$ALIGN_R1_RUNTIME"` as one argv element; the contract doc calls it an "operator-pinned argv". A runtime that needs an interpreter must be a wrapper executable. Say so in one place.
4. `workload.py:439` + `powermode.py:31` (`timeout=10`): the per-episode `pmset -g custom` read sits between G0 release and `start`. A transient failure records `value: None`, which the desk treats as a mismatch and fails the window-level `ac_powermode_members` check. Fail-closed, but one flaky read costs a window check; a single retry would be cheap.
5. `thermal_desk.py:177-186`: a custody-invalid member is re-attributed with `intervals: []`, so its printed owned energy omits every hold. It is excluded from calibration, and `thermal_exclusions` still counts it for U1 with its real intervals, which is the right side to err on; label the energy as re-attributed.
6. `scripts/align_v4_kit.py:44` comment still says "the late replay remains ordinal 18"; after ruling 1(g) the replay is 17 and 18 is the development member (the code, README and tests are right).
7. Executing-review LOWs 1-3 confirmed: the A-B-A leg wait bound assumes 1,800 + 600 s; `t_decline_s: true` is accepted as 1 s; "A legs ∞, B finite" is reported inconclusive where ruling 16 reads not-adopt (both leave Automatic).
8. `align_r1_rehearsal.py:404-431`: the batch window is built from `datetime.now().astimezone()`, a fixed-offset tzinfo, so on a DST transition day the 11:45-13:15 boundaries are off by an hour. The next transition is March 2027; no R1/W1 exposure.
9. Window-reference custody (`align_v4_kit.py:191-193` digest of `BenchmarkConfig.from_mapping(config).to_dict()` → `bundle.py:963-966` `config.json`): the test exercises the real writer, and I confirmed `controller.py:337-368` passes the config through unchanged when there is no `suite_manifest_ref` (the v4 configs have none). The binding is sound. Note that any future launcher-side config override would refuse every consumer from ordinal 6 on (window loss, not corruption).

## Council rulings: what is on the head

| Ruling | Status on `c5cc2d521` |
|---|---|
| 1(a) phase consumption print, 1(b) bank/benign gated run, 1(c) cooldown to soak or 1,500 s with recovery curve, 1(d) duty bar pre-declared, 1(e) fallback order | in the driver (`:44-54`, `:38-42`, `:173`, `:335-361`) |
| 1(f) as restated by L1 | kit asserts T_dead and the member fit (`align_v4_kit.py:132-176`); W1 validator asserts it; driver does not evaluate it (carried M-2) |
| 1(g) swap 17/18 | roster, tags, `replay_of`, `fit_roster` and both e17/e18 configs regenerated consistently |
| 6 U5 with L2 (c = 1.0, σ_pair floor 2.97 J, PASS/FAIL/INCONCLUSIVE) | `:303-326`; releases checked against R + offset ± δ_slow and β_T fitted on measured temperatures |
| 7 powermode pin, arm refusal, bundle record, desk `instrument_ok` | present; arm does not *record* (MEDIUM-5); host-level recovery open (HIGH-1) |
| 8 batch window, load journal, redo, detrended soak | present for quiet segments; journal completeness unchecked (carried M-1) |
| 16 A-B-A after release, 1.25× and 25 % thresholds, timeout → inconclusive | `:227-244`, `:586-603` |
| 21 R0 dispositions print | `scripts/align_r0_dispositions.py` present; R0 scope, not reviewed in depth here |
| 22 protocol v4 draft before R1 | **absent** (MEDIUM-4) |
| 4(a)/20 W1 arm rules (battery, external volume) | not on this head; they block W1, not R1 |

## Claims in the executing review

Every claim I could check holds: the test counts, the WP22 result, both fail-without-fix tests (with the caveat on the in-process burst test above), kit `--check` and the validator failing closed, the v3 byte freeze, the marker-before-High ordering, the AC-key read-back per leg, two redos then refusal, U5 constants, the single deadman armed at G0 entry (`workload.py:429-434`, `:448`) and the contrast deadman value. HIGH-3 and MEDIUM-1..5 are correctly described as open.

## Verdict for the R1 arm item

Admit for the rehearsal with the executing review's runbook step for HIGH-1. Before W1: MEDIUM-1 (kill policy in the driver and contract), MEDIUM-3 recorded as a registration decision, MEDIUM-4 (land protocol v4), and the carried M-3 (bind r1_slots evidence in the kit). MEDIUM-2 and the LOWs are cleanups.
