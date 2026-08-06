# Window C Readiness and Operator Checklist

**Current verdict: NO-GO.** Window C should not be scheduled yet. The science configurations are largely prepared, but the issued calibration acceptance artifact, final Window C/D split, numerical analysis gates, extraction specification, and launcher-verified readiness record are still missing.

A clean Window C can complete an important portion of the instrument characterization. It cannot complete the full A+ characterization by itself: the prepared non-micro-delta science already requires about 3.64 hours before calibrations, references, stage settles, and the required 20% failure margin. Between-session stability also requires at least three independent sessions or days.

Status below is as inspected on 2026-08-06.

## 1. BEFORE the night — desk freeze

### What is already prepared

| Item | Status | Prepared material |
|---|---|---|
| Collection protocol | **READY** | `docs/phase_2/window_runbook.md`: two calibrations, fresh 12-member bound corpus, start/mid/end references, per-stage arm and re-probe, one verdict, backup before extraction. |
| Environment policy | **READY** | AC/external power, low-power mode off, displays asleep, screensaver disengaged, nominal thermal pressure, CPU admission, known adapter wattage. |
| Linearity membership | **READY and frozen** | 40 fresh members: prompt 128; output 128/256/512/1024/2048; eight observations per level. Plan SHA-256 `ac67019d…7166f3`. Estimated science time: 62.1 min. |
| Null-ladder membership | **READY and frozen** | 60 fresh members: output 128/512/2048; five A/B/B/A blocks per magnitude, 20 members per magnitude. A and B are identical aliases. Plan SHA-256 `7f75f73a…017da`. Estimated science time: 93.6 min. |
| Additivity membership | **READY and frozen** | 24 fresh members: prompt/output shapes 2048/128, 512/512, and 128/2048; eight members per shape. Each bundle supplies prefill, decode, and request energy. Plan SHA-256 `4c63bf9e…44133`. Estimated science time: 37.6 min. |
| Long-hold membership | **READY and frozen** | Three sustained 4096-output members plus 120/300/600-second extended-idle members. Plan SHA-256 `34af9db7…a8f2`. Estimated science time: 25.3 min. |
| Existing plan integrity | **READY** | All four sidecar hashes match their plan files. |
| ABBA calculation | **READY** | Within each block, compare the mean of the two inner B observations with the mean of the two outer A observations. ABBA reduces linear drift but does not replace the window drift allowance. |
| Hardware supply | **PREVIOUSLY PROVEN; RE-PROBE AT T-0** | The 140 W Anker supply was later observed at 28 V × 4.99 A, “pd charger,” 140 W negotiated. The earlier 70 W mismatch is historical, but the night still requires a fresh observation. |
| Repository checkout | **CLEAN NOW, NOT FINAL** | `main` and `origin/main` are at `6fddd50`; working tree clean. This cannot yet be the measurement pin because required calibration-acceptance work remains unfinished. |

All recollections must be fresh occurrences under the new Window C/D roots. Nothing from the retired Window B corpus may enter membership, calibration, reference, floor, or extraction bases.

### What must still be completed

- [ ] **Issue the production calibration-acceptance artifact.** The current file is explicitly `schema_fixture_unissued`, with a genesis ledger cutoff and `claim_eligible: false`. Complete its consumer implementation, exact-byte review, issuance, ledger/head-pin binding, and production-path verification.

- [ ] **Complete the corrected floor re-mint chain.** Require validator-clean, end-to-end evidence using the issued acceptance artifact before spending a collection night.

- [ ] **Choose and freeze the C/D split.** List every stage in exactly one window. Do not leave “spillover if time permits”; optional in-night membership is forbidden.

- [ ] **Finish the micro-delta plan.** The only generated material is a 20-member `k0064` placeholder marked `draft_pending_slope`. The paper requires predicted effects near 0.5×, 1×, 1.5×, and 3× the floor in both directions, while the current suite README speaks of three slots. Resolve that mismatch, choose the exact token increments from the preregistration slope, generate every run ID, counterbalance direction, ratify the plan, and freeze its digest.

- [ ] **Freeze the exact comparison definitions.** At minimum:

  - Linearity: gross request energy and decode energy versus runtime-observed output count, with the regression and residual calculation fixed.
  - Null ladder: identical-condition ABBA deltas at all three magnitudes.
  - Empirical floor: signed micro-deltas at every frozen floor multiple, in both directions.
  - Additivity: prefill plus decode versus enclosing request energy, with setup/gap treatment fixed.
  - Causal invariance: prefill energy versus output length while prompt tokens are fixed. The existing additivity shapes do not themselves hold prompt length fixed; either prospectively extract prefill from the fixed-prompt linearity ramp or author an additional fixed-prompt stage.
  - Drift/settling: start/mid/end trajectory plus the exact recovery comparison for the 180-second convention.
  - Stability: the exact calibration, null, and floor cells repeated in each eligible session.

- [ ] **Freeze numerical scientific acceptance rules.** The current campaign plans contain no non-null `comparisons`, `acceptance`, `analysis`, or `extraction` sections. Before collection, specify:

  - linearity lack-of-fit and residual criteria;
  - the null interval-to-floor rule;
  - which micro-delta levels must be refused and which must resolve;
  - the additivity tolerance and causal-invariance slope bound;
  - the thermal/reference recovery band supporting or revising 180 seconds;
  - the between-session stability rule and eligible identity-matched sessions.

  Do not choose these after seeing Window C outcomes.

- [ ] **Author the composite extraction specification.** It must name every expected cell, metric, member or ABBA block, condition family, minimum count, comparison orientation, drift allowance, and exact passing verdict basis. It must use only fresh Window C occurrences.

- [ ] **Freeze the calibration retry matrix.** Record these exact existing rules:

  - calibration-only `clock_anchor_unresolved`: at most one settled retry for the pre calibration and at most one for the post calibration;
  - member-level clock-anchor retry: zero;
  - non-clock post-calibration retry: zero;
  - pre-calibration level-screen cause-removal retry: enter an exact integer in the plan; the current material does not select one;
  - manual or outcome-driven retry: zero;
  - third failure on the same cause: close the window.

- [ ] **Assemble the plan root outside both runs roots.** It must contain:

  ```text
  WINDOW_PLAN_ROOT/
  ├── window.env
  ├── before_midpoint_stages.txt
  ├── after_midpoint_stages.txt
  ├── extraction_spec.json
  ├── waivers.json
  ├── retry_policy.json
  ├── analysis_acceptance.json
  ├── readiness-record.json
  └── window-chain.zsh
  ```

- [ ] **Set exact fresh paths.** Fill the date; do not leave placeholders at review:

  ```text
  WINDOW_ID=window_metrologyC_YYYYMMDD
  RUNS_ROOT=/Users/edr/code/JouleWise/runs_window_metrologyC_YYYYMMDD
  BOUND_RUNS_ROOT=/Users/edr/code/JouleWise/runs_window_metrologyC_YYYYMMDD_bound
  CUSTODY_ROOT=/Users/edr/JouleWise-window-custody/window_metrologyC_YYYYMMDD
  CLAIM_BACKUP_DEST=.../window_metrologyC_YYYYMMDD/claim
  BOUND_BACKUP_DEST=.../window_metrologyC_YYYYMMDD/bound
  ```

- [ ] **Set `waivers.json` to exactly `[]`.** The launch and verdict commands must not pass a waiver argument.

- [ ] **Pin the final code revision.** Require reviewed, merged `main`, clean checkout, exact `git rev-parse HEAD`, policy hash, issued acceptance-artifact digest, ledger-head pin, plan-tree digest, and launcher digest.

- [ ] **Run desk verification unpiped.** Require the canonical suite plus focused campaign/config, strict-validation, calibration, bound-mint, verdict, backup, and extraction checks. Save exit codes in the readiness record.

- [ ] **Validate and dry-run every stage against its intended root.** Include the bound corpus, all three reference stages, every science stage, and both prospective windows. Resolve every doctor warning rather than casually acknowledging it.

- [ ] **Prove the negative gates.** The frozen head must still refuse an awake or saver-active display, unresolved clock anchor, and missing or temporally invalid environment admission.

- [ ] **Verify model and config availability offline.** Models, tokenizer, configs, scripts, and the virtual environment must be cached and loadable without downloads during the window.

- [ ] **Create one reviewed readiness record.** It must bind the plan digest, issued calibration artifact, ledger head, clean code revision, empty waiver list, exact roots, backup destinations, dry-run results, environment preflight contract, and retry matrix.

- [ ] **Make the ordinary launcher verify that record.** `scripts/prewindow_check.sh` is useful but currently does not by itself bind the complete frozen-plan record. Until the launcher mechanically verifies it, the start fence is not satisfied.

### Frozen operational thresholds

These values are already defined, but the final chain must consume the issued artifact mechanically rather than trusting copied literals:

| Gate | Required result |
|---|---|
| Wall-versus-monotonic span | No more than `0.005 s` per member. |
| Pre-calibration fiducial | `b_fiducial_s <= 0.033558756679900`. |
| Clean calibration-bracket drift | No more than `0.010818 s`. |
| Budgetable ordinary excess | At most `0.001275166090593858 s`, for maximum drift `0.012093166090593858 s`; identified systematic defects are never budgeted. |
| Bound freshness | Minted from all 12 bound members inside this window; maximum age `86400 s`; exact OS, supply, and calibration identities must match. |
| Environment | AC and externally connected, low-power mode off, all online displays asleep, screensaver disengaged, thermal pressure nominal. |
| CPU admission | At least 30 samples; busy-ratio p95 no more than `0.5`; combined processor power p95 no more than `1.0 W`. |
| Stage failure behavior | `--max-failures 1`; only a preregistered recovery may relaunch a stage. |
| Whole window | Exactly one ordinary verdict over the exact occurrence set; `status: passed`; both energy-family screens and allowances authenticated. |

### One night versus multiple sessions

The prepared C1, C2, C4, and C5 science totals about **218.6 minutes before** two calibrations, the 12-member bound corpus, seven references, stage settles, arming, and failure margin. Therefore the full set cannot fit one compliant 2–4-hour window.

A defensible starting split is:

| Session | Candidate frozen contents | Result available if the window passes |
|---|---|---|
| **Window C** | Linearity; additivity; middle null rung; sustained-hold Part A. Add extended-idle Part B only if the measured dry-run budget still retains 20% margin. | Full linearity; additivity; causal invariance if fixed-prompt prefill extraction is authored; one null magnitude; within-window drift trajectory; partial or full settling evidence depending on Part B; stability session 1. |
| **Window D** | Remaining null rungs; finalized micro-delta slots; any deferred settling stage; exact repeat cells. | Full null ladder; empirical floor verification; completed settling evidence; stability session 2. |
| **Third session/day** | Same preregistered calibration, null, and floor repeat cells under matched recorded identity. | Minimum three-session between-session stability result. |

This split is a candidate, not permission to launch. Final packing must come from dry-run timings. If Window D cannot retain the 20% margin, move a complete preregistered stage to the third session; never compress settles or remove references.

Window B cannot count toward any replacement result. A prior session may count toward stability only if it is prospectively named, verdict-passed, exact-cell compatible, and identity-authenticated. Otherwise plan three new sessions.

## 2. AT the machine — Ed’s T-0 gate and run

Every line is binary. Any unknown, warning, or missing evidence means **NO-GO**.

### T-0 physical and machine gate

- [ ] **PASS — reviewed readiness record verifies without exception.**  
  Evidence: `$WINDOW_PLAN_ROOT/readiness-record.json` and launcher exit `0`.

- [ ] **PASS — final checkout equals the pinned commit and is clean.**  
  Evidence: `$CUSTODY_ROOT/t0/git-state.txt`.

- [ ] **PASS — approved 140 W Anker adapter and approved cable are connected.** The live observation must report external AC, “pd charger,” and 140 W negotiated; a recurrence of 70 W is NO-GO.  
  Evidence: `$CUSTODY_ROOT/t0/power-identity.json`.

- [ ] **PASS — power policy is `ac_high_power`, low-power mode is off, and the supply is not changed after this point.**  
  Evidence: `$CUSTODY_ROOT/t0/environment-preflight.json`.

- [ ] **PASS — system time is correct against an independent source before disabling synchronization.**  
  Evidence: clock-offset line in `$CUSTODY_ROOT/t0/clock-pin.txt`.

- [ ] **PASS — prior automatic-network-time state is recorded, network time is disabled, and the machine settles for 180 seconds.**  
  Evidence: `systemsetup` output and timestamps in `$CUSTODY_ROOT/t0/clock-pin.txt`.

- [ ] **PASS — Time Machine, updates, indexing, downloads, and cloud uploads have finished or are paused.**  
  Evidence: `$CUSTODY_ROOT/t0/process-census.txt`.

- [ ] **PASS — the Mac has been untouched and idle for at least ten minutes so idle-triggered maintenance can drain.** This is in addition to stage settles.  
  Evidence: start/end timestamps plus clean pre-window checks in `$CUSTODY_ROOT/t0/prewindow-check.log`.

- [ ] **PASS — no contaminating process exceeds the preflight limits and overall load is acceptable.**  
  Evidence: `scripts/prewindow_check.sh --wait ...` exit `0` and captured output.

- [ ] **PASS — passwordless `powermetrics` works.**  
  Evidence: `sudo -n /usr/bin/powermetrics ...` exit `0` in the preflight log.

- [ ] **PASS — at least the frozen minimum disk headroom is available, both backup destinations exist, and their capacity is sufficient for both roots.**  
  Evidence: `$CUSTODY_ROOT/t0/storage.txt`.

- [ ] **PASS — all models and configs load locally without downloads.**  
  Evidence: desk dry-run receipt bound by the readiness record.

- [ ] **PASS — all online displays are asleep; the screensaver is disengaged; persistent screensaver/display settings were not modified as part of the window.**  
  Evidence: `scripts/quiet_mac_prep.sh` log and post-arm probe.

- [ ] **PASS — thermal pressure is nominal.**  
  Evidence: preflight environment record.

- [ ] **PASS — Claude, Codex, t3, browser automation, browsers, periodic monitors, log tails, and other output-streaming sessions are closed.** An installed-but-inactive quiet guard does not satisfy this.  
  Evidence: independent process census with zero agent, t3, browser-automation, campaign, and watcher survivors.

- [ ] **PASS — cloud-sync custody is safe.** If `bird` is absent, record absence. If present, record PID plus process start time, verify state `T` twice, hold its launchers as prescribed, install a fail-safe `CONT` trap, and do not access Mobile Documents while it is stopped.  
  Evidence: `$CUSTODY_ROOT/t0/bird-custody.log`.

- [ ] **PASS — everyone nearby has been told not to touch the Mac, displays, lid, charger, or cable.**  
  Evidence: operator initials and timestamp in the T-0 record.

### Launch and automatic run

- [ ] **Launch exactly once from the ordinary guarded foreground shell:**

  ```sh
  caffeinate -is /bin/zsh "$WINDOW_PLAN_ROOT/window-chain.zsh" "$WINDOW_PLAN_ROOT"
  ```

  Evidence: `chain_start` in `$CUSTODY_ROOT/operator_logs/window-chain.log`.

- [ ] **After arming, send at most the one-line arm message and stop all operator output.** Do not tail logs or wake the display.

- [ ] **Pre calibration completes under protocol v3.** If its sole failure is `clock_anchor_unresolved`, the chain may settle and retry once. Any other failure follows the frozen retry matrix.  
  Evidence: both attempt directories, if two exist, and the pre-calibration log.

- [ ] **Pre-calibration level screen passes before member 1.**  
  Evidence: `pre_calibration_screen=passed` and the recorded fiducial value.

- [ ] **Twelve fresh bound-corpus members collect under the pre calibration.**  
  Evidence: bound-root campaign log and exact 12-member manifest.

- [ ] **The dual-family bound mints inside this window.**  
  Evidence: `$BOUND_RUNS_ROOT/neg8-drift-bound.json`.

- [ ] **Start reference triplet completes.**  
  Evidence: three exact start-reference occurrences in the claim log.

- [ ] **All frozen pre-midpoint science stages complete in their listed order.**  
  Evidence: `stage_start`/`stage_end` pairs and campaign manifests.

- [ ] **Midpoint reference completes.**  
  Evidence: its exact occurrence in the claim log.

- [ ] **All frozen post-midpoint stages complete in their listed order.**  
  Evidence: `stage_start`/`stage_end` pairs and campaign manifests.

- [ ] **End reference triplet completes.**  
  Evidence: three exact end-reference occurrences in the claim log.

- [ ] **Post calibration completes after the final member with at least the required post-window dwell.** Its only automatic retry is one settled retry for sole-reason `clock_anchor_unresolved`.  
  Evidence: post-calibration directory and log.

- [ ] **Every campaign invocation performs the 20-second display arm and a fresh environment re-probe.** The desk prep result is not a certificate for later stages.  
  Evidence: per-stage logs and per-bundle environment-admission records.

- [ ] **Adapter wattage remains stable from first admission through post capture.**  
  Evidence: per-observation adapter records and eventual verdict.

- [ ] **The chain records `measurement_complete`.**  
  Evidence: final timestamp in `window-chain.log`.

### Automatic stop rules

- [ ] A display wake, screensaver engagement, CPU-admission failure, operator touch, or unknown environment state loses the affected occurrence. Never use an environment override.

- [ ] A member-level clock-anchor failure is preserved and quarantined; there is no member-level anchor retry.

- [ ] A pre-calibration level failure ends the attempt before member 1. Relaunch only after a named cause was removed and only within the frozen cause-removal retry count.

- [ ] A supply or cable identity change ends the entire window.

- [ ] The third failure on the same cause closes the window.

- [ ] No threshold, waiver, membership, stage order, analysis rule, or retry policy is changed during the night.

## 3. AFTER the night — authentication, verdict, backup, extraction, and figures

### Immediate close-out

- [ ] **Wake the display only after `measurement_complete`.**

- [ ] **Finalize every calibration-ledger reservation.** No pending, abandoned-without-disposition, malformed, or conflicting observation may remain.

- [ ] **Update and commit the exact ledger-head pin before claim evaluation.** Do not evaluate between ledger advancement and the committed pin.

- [ ] **Authenticate the calibration bracket.** Require:

  - valid protocol-v3 pre and post artifacts;
  - pre before the first science member and post after the last;
  - both under the claim root’s `instrument_validation/`;
  - exact acceptance epoch and issued-artifact match;
  - same OS build, power policy, instrument identity, cadence, and estimator;
  - operative use of the larger bound;
  - clean or mechanically budgeted drift under the issued rules.

- [ ] **Authenticate the fresh bound.** Require all 12 exact members, same-window mint time, both energy families, 86400-second freshness field, and exact OS/supply/calibration bindings.

- [ ] **Record each permitted supersession exactly once before the verdict.** Two present occurrences or duplicate supersession records refuse. Do not plan on salvage to rescue a fresh window.

- [ ] **Emit exactly one ordinary whole-window verdict:**

  ```sh
  .venv/bin/python scripts/run_campaign.py \
    --whole-window-verdict \
    --runs-dir "$RUNS_ROOT" \
    --log "$RUNS_ROOT/campaign_log.jsonl" \
    --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json \
    --neg8-drift-bound "$BOUND_RUNS_ROOT/neg8-drift-bound.json"
  ```

- [ ] **Require `status: passed`.** Record the evaluation-basis SHA-256, exact member-occurrence set, calibration bracket, policy hash, both family screens, both drift allowances, admitted CPU state, and stable adapter continuity.

- [ ] **Back up both immutable roots and require exit code 0 for each.** Record separate source, destination, start/end timestamps, and exit status for the claim root and bound root. Leave both sources unchanged.

- [ ] **Release any stopped cloud-sync process through the fail-safe cleanup and verify process identity before backup.**

- [ ] **Restore automatic network time after the verdict and successful backups.** Record restoration time and confirm the state is on.

- [ ] **Run exact-basis governed extraction.** Use an absolute runs root, the frozen extraction spec, the passing evaluation-basis SHA-256, and bundle hashing:

  ```sh
  .venv/bin/python scripts/extract_detection_floors.py \
    --runs-root "$RUNS_ROOT" \
    --spec "$WINDOW_PLAN_ROOT/extraction_spec.json" \
    --out "$CUSTODY_ROOT/window-c-extraction.json" \
    --evaluation-basis-sha256 "$WHOLE_WINDOW_BASIS_SHA256" \
    --hash-bundles
  ```

- [ ] **Require extraction exit 0 and exact membership.** Require `all_cells_extractable: true`, no specification-membership or idle-admission refusal, matching drift allowances, no fallback-anchor or mock member, and an explicit disposition for every planned occurrence.

- [ ] **Keep extraction and consuming analysis in the same lead-controlled custody session while the standalone-floor binding limitation remains open.**

- [ ] **Complete the close-out record.** Include code/policy/plan hashes; window times; supply identity; every calibration attempt; bound members and freshness; seven references; both allowances; verdict basis; failure/quarantine/supersession inventory; both backup results; extraction result; clock disable/restore times; and counts by distinct bundle ID.

If any required result fails, preserve all evidence and report the strongest lower status earned. Do not call the window claim-bearing.

### Desk analysis and required C-iv figures

Every figure must identify the physical Mac, OS version/build, runtime and library versions, model artifact hash, quantization, tokenizer, sampler and output policy, configured and realized batch/concurrency, measurement boundary, and telemetry backend.

| Figure | Exact output |
|---|---|
| **Linearity** | Observed output count versus gross request energy and decode energy; fitted slopes and intervals; residual panel; tested range clearly limited to 128–2048 tokens. |
| **Null ladder** | ABBA delta and interval at each short/mid/long magnitude; zero line and the matching decision envelope; state whether false contrasts remain contained as magnitude grows. |
| **Empirical floor** | Predicted floor multiple versus observed signed delta and interval for every frozen level and both directions; label each result `refused`, `resolved`, or `failed expected behavior`. |
| **Additivity** | Prefill-plus-decode versus enclosing request energy with identity line; residual/setup/gap accounting by shape. |
| **Causal invariance** | Prefill energy versus later output length at fixed prompt length; slope and frozen equivalence/acceptance band. A nonzero result narrows the phase claim. |
| **Drift and settling** | Start/mid/end reference trajectory with published allowance; long-hold and post-transition thermal/admission recovery against the 180-second convention. Show midpoint curvature rather than reporting endpoints alone. |
| **Between-session stability** | At least three identity-matched sessions/days showing calibration bounds, repeated null blocks, and repeated floor cells. State whether the declared freshness/reuse rule holds or each session needs a new floor. |

## Known failure modes and their preventive checks

| Prior failure | Exact prevention before launch | If it appears |
|---|---|---|
| **Screensaver/display contamination** | Run `quiet_mac_prep.sh`; require explicit all-displays-asleep and screensaver-disengaged evidence; retain `--arm-quiet-mode --arm-countdown-s 20` on every stage; prove the awake/saver negative tests still refuse. | Lose the occurrence, preserve it, remove the cause, and follow only the frozen recovery. Never override admission. |
| **Clock-anchor failure** | Verify the wall clock first; disable network time; settle 180 seconds; require the 5 ms gate; freeze zero member-level anchor retries and one calibration-only clock retry. | Preserve and quarantine a failed member and stop the stage. Do not hand-retry it. |
| **Environment-admission binding failure** | Fresh roots; exact campaign manifests and log; arm-time preflight on every invocation; valid before/after observations; negative test for missing or temporally invalid evidence. | Refuse the occurrence or entire basis as machinery directs. Never replace authenticated binding with a directory scan. |
| **Out-of-family pre calibration** | Drain idle maintenance; verify quiet state; use the issued level screen before member 1; freeze the cause-removal retry count. | Abort before science. Retry only after naming and removing a cause; never rerun until lucky. |
| **140 W charger negotiating 70 W** | Re-probe negotiated voltage/current/wattage immediately before launch and bind it in the readiness record. | NO-GO. Repair cable/port/supply state outside the window. |
| **Agent or terminal output during idle admission** | Close Claude, Codex, t3, browsers, watchers, and tails; independent census; one-line arm message; no streaming afterward. | Treat the affected occurrence as contaminated. |
| **Idle maintenance starts after launch** | At least ten untouched minutes plus consecutive clean pre-window checks before the chain. | Preserve the refusal; wait for the named process to finish; follow only the frozen recovery. |
| **Outcome-driven calibration retry** | Freeze retry counts and reasons; retain every attempt; chain screens the pre calibration automatically. | End the attempt when no named removable cause exists. |
| **Membership or verdict shopping** | Freeze exact members and comparisons; one ordinary verdict; explicit passing-basis SHA in extraction. | Stop on any conflict. Never append a semantically different verdict over the same basis. |

## Provenance appendix

- Collection procedure, physical preparation, custody, ABBA, verdict, backup, and extraction: `docs/phase_2/window_runbook.md`.
- Fresh-claim reset, no-Window-B rule, readiness preconditions, and hard start fence: `docs/decision_log.md`, D-113 clauses 7–9.
- Frozen metrology campaign vocabulary and four frozen plans: `docs/decision_log.md`, D-096.
- Calibration screens, drift limits, and acceptance-artifact chain: D-079, D-102, D-109, and `configs/calibration/calibration_acceptance_d079_v2.json`.
- Window failure history and zero-streaming rule: D-098/D-099 and `docs/run_reports/2026-08-01-metrology-window-b.md`.
- Third-failure closure: D-087.
- Current Window C task and start dependencies: `TASK_QUEUE.md` and `/tasks/MET-WINDOW-C-01` in `docs/process/state_kernel.json`.
- A+ characterization outputs: `docs/paper/draft-v1.md` §6 and `docs/phase_2/detection_floor.md`.
- Current claim state, including mandatory recollection of C1/C2/C4/C5: `CLAIMS_STATUS.md` §3.