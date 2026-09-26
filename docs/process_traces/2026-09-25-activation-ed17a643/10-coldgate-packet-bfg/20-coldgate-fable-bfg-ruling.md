# Cold-gate ruling — BATTERY-FLOAT-01 (directive #421): design, split, registration addendum

Judge: Claude Fable 5.1 (`claude-fable-5-1`), cold, single foreground session, worktree `JouleWise-wt-ed17a643-cg-judge` at HEAD `6b769d98`, code identical to `origin/main` = `c6814dd8` (`git diff --name-only origin/main HEAD` lists only `docs/` files and `RUN_STATE.md`, none opened except the packet). Session 2026-09-25 14:31–14:44 PDT. No background tasks, subagents, watchers, `sudo`, `launchctl`, `powermetrics`, installer or model inference were run. Only this file was written.

## 0. Contamination disclosure (everything loaded besides the packet)

Loaded without my choosing, by the harness: the global `~/.claude/CLAUDE.md` (multi-model orchestration and writing-standard rules), the project `CLAUDE.md` (Codex bridge notes), and the auto-memory index `MEMORY.md` (one-line pointers per memory, including loop-context titles such as checkpoints and directives). I opened no memory file, no `RUN_STATE.md`, no `TASK_QUEUE.md`, no council log, no run report, and no `docs/process_traces` file outside this packet except the two the exhibits cite by path (below). A system reminder supplied the git status and the five most recent commit subjects.

Loaded by me, all read-only:

- `docs/process/coldgate_charter.md` (digest below).
- The six exhibits (digests below).
- Code at `origin/main` `c6814dd8`: `joulewise/night_gate.py` (169-170, 195-300, 334, 600-640, 653-680, 780-810, 1461-1670, 1785-1870, 1986, 2020-2062), `joulewise/adapters/powermetrics.py` (50-70), `joulewise/calibration_bracketing.py` (200-215, 690-710, 1535-1640, 1960-1975, `_binding_evidence_authentic`), `scripts/validate_powermetrics_fiducial.py` (388-402, 1705-1725, 1892-1922, 2150-2330, 2440-2460, 2560-2700, `_sampler_lifetime`), `joulewise/arm_retry.py` (15-45, 200-250, 275-290, 335-345), `joulewise/evidence_night.py` (1067-1112, 1320-1400, 1750-1790), `joulewise/environment.py` (210-220, 255-262, 360-375, 865-890, 506-513), `joulewise/arm_readiness_evidence_t0.py` (100-110, 1835-1850), `scripts/issue_calibration_acceptance_generation.py` (170-220, 895-965, 1055-1085, 1118-1145, 1345-1360, def list), `joulewise/scored_reduce.py` (80-115, 140-165), `scripts/night_chains/calibration_derivation_only.zsh` (240-280), `joulewise/bundle_read.py` (176, 265-280, 766), `joulewise/reduce.py` (2650-2670), `joulewise/night_agent_install.py` (1160-1170, 1370-1376), `scripts/run_night.py` (2286-2287, 2796-2801, 3050-3066, 3090-3125), `scripts/calibration_cadence_report.py` (40-50), `joulewise/controller.py` (855-870, 1218-1280, 2060-2070, 2118-2126), `scripts/sample_quiet_predicate_evidence.py` (1025-1030, 1064-1100, 1160-1165, 1198-1205, 1460-1465), `joulewise/quiet_predicate_campaign.py` (1130-1145, 1668-1680), `joulewise/environment_admission.py` (40-60), `scripts/run_campaign.py` (4368-4376, 5066-5074), `scripts/issue_epoch_continuation.py` (90-100), `joulewise/calibration_ledger.py` (133-146, 269-277, 286-312, 2370-2415, 2822-2840, 2964-2970, 2971-3045, def names at 3083 and 3174), `joulewise/calibration_custody_worker.py` (45-95), `joulewise/powermetrics_fiducial.py` (1366-1406, one grep inside `verify_stored_evidence_physics`), `joulewise/night_kinds.py` (24-70), `scripts/gen_derivation_night.py` (75-90, 555-580), `tests/test_night_gate.py` (1285-1345), grep hits listed in §2.
- `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` lines 140-175 and 565-640 plus a heading grep; its `origin/main` digest and placeholder count. `configs/calibration/observation_dispositions.json` (first 40 lines). `configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json` digest only.
- `docs/decision_log.md` line 228 and lines 11959-12035 (the D-182 entry both seats cite as controlling).
- Cited by ex-03 (path-cited, other worktree, read-only): `/Users/edr/code/JouleWise-wt-817355d2-w1arm/docs/process_traces/2026-09-25-activation-817355d2/10-w1-arm/scripts/README-sequence.md` lines 84-96 and `arm-env.zsh` lines 30-59 (the `battery_gate` function). These files are uncommitted there and absent from `origin/main`.
- Cited by ex-00 (#420): `/tmp/4b-osaudit/battery.jsonl` (78 lines, first 3 and last 25) and the directory listing of `/tmp/4b-osaudit/` (filenames only; nothing else opened).
- Live, allowed by the charge: `ioreg -r -c AppleSmartBattery` (twice, filtered), `ioreg -r -c AppleSmartBattery -d 1` (once), `pmset -g batt` (once), `gh pr view 418 --json ...` (metadata only).

## 1. Charter and exhibit verification (before the merits)

Charter: expected sha256 `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` (source: the charge file `00-charge.md` §Charter pin; the operator prompt supplied no separate value, which I record as a limitation of independence). Observed by `shasum -a 256 docs/process/coldgate_charter.md`: `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`. MATCH.

Exhibits: `shasum -a 256` over the six files in the packet directory reproduced every digest in the charge's manifest exactly (ex-00 `3b03310a…`, ex-01 `95ae7189…`, ex-02-seat-astra `2dc90dd3…`, ex-02-seat-sol `39e63e8f…`, ex-03 `1927fbe9…`, ex-30 `9497c832…`). MATCH.

`origin/main` resolves to `c6814dd891db361156c45434490342a3e1dd9da3` (merge of PR #414), as the charge states.

## 2. Packet hygiene

No defect that impairs a question. Notes:

- The seat brief (ex-01) says `environment.py:215/:259 records is_charging from pmset`. Verified false in the direction Astra states: `pmset -g batt` is parsed at `environment.py:255-262` for other fields; `is_charging` is populated from `ioreg -r -c AppleSmartBattery -d 1` at `environment.py:366-372` and `:868-885`, and no `InstantAmperage` parser exists anywhere in `joulewise/` or `scripts/` (grep). Immaterial to the questions; recorded so the brief is not reused as fact.
- ex-03 asserts a harvest rule over a per-slot `is_charging` that does not exist (its own F2). Its arm scripts are uncommitted in another worktree, so their content is not at `origin/main`; I read the cited lines only to rule on the procedural gate (§7, item 8).
- ex-30's physical narrative ("at 80 % the charger carried no charging current") is unverified and not load-bearing. The logger data it summarises are consistent with `/tmp/4b-osaudit/battery.jsonl` (3586 mA at 83 % → 739 mA at 100 %, still `IsCharging=Yes`, at 14:33 PDT).
- B3 is compound (addendum need, S2, count handling, landing); each part is decided separately below.
- The only cited authority outside the registration text is D-182 (`docs/decision_log.md:11959-12035`), read and applied. No conflict of authority.

## 3. B1 — design: verification of the load-bearing claims, then A1–A8

### 3.1 Verified facts (file:line at `c6814dd8`)

| # | Claim | Verified | Result |
|---|---|---|---|
| V1 | C3 reads `pmset -g batt` and requires only `"AC Power"` in stdout; raw stored as `ac_power_raw` | `night_gate.py:169`, `:1488-1505` | TRUE. Live `pmset -g batt` today prints `Now drawing from 'AC Power'` while `IsCharging = Yes`, so C3 passes a charging machine. |
| V2 | Reason registries are fixed sets; condition ids fixed C1–C5 | `night_gate.py:203-221` (`NIGHT_GATE_REASON_CODES`), `:229-246` (driver set, overlap check), `:250-260` (`ORDER`), `:301` (`_CONDITION_IDS`), `:1986` (receipt codes), `:2020-2021` (exactly C1–C5) | TRUE. A new C6 would fail receipt validation; a new code must be added to the frozenset. `measured` is a free object (`:2044-2045`), so raw ioreg text fits in C3 without schema change. |
| V3 | `_check_machine` serves both t0 and the arm check | `evaluate_night` → `_check_machine` at `:1856`; `evaluate_dynamic_hard` → `_check_machine(..., legacy_load=False)` at `:1811`; driver calls at `run_night.py:2286-2287, 2796-2801, 3050, 3066` | TRUE. One insertion right after the AC check covers every t0/arm path that goes through the night gate. Probe argv is unconstrained (`_run`, `:653-680`), so a new `IOREG_BATTERY_ARGV` works with the existing `Probes` injection; `tests/test_night_gate.py:1320-1330` asserts the exact probe sequence and must be updated. |
| V4 | `SAMPLERS` sits in a pinned estimator-code path | `powermetrics.py:58`; `ESTIMATOR_CODE_PATHS` at `calibration_bracketing.py:206-211` includes `joulewise/adapters/powermetrics.py`; `_current_estimator_code_sha256` hashes whole file bytes `:696-706`; the writer refuses `acceptance_artifact_stale` on mismatch `validate_powermetrics_fiducial.py:396-400` | TRUE. Adding `battery` to `SAMPLERS` moves a pinned digest. Do not. |
| V5 | Derivation writer sampler lifetime and hashing | raw dir created `:2228`; `_sampler_lifetime` spawn `:2297`; `sampling_stopped` → `_terminate_powermetrics` → `AFTER_SAMPLER_TEARDOWN` `:2449-2452`; `instrument_evidence(... artifact_sha256={3 names})` `:2568-2581`; evidence written `:2606-2610`; manifest `artifacts` = 3 names + plist `:2612-2624`; ledger finalize `:2645-2650` | TRUE as to positions. **But** see F-1: the two inventories are exact-set-checked elsewhere, and the ledger row hashes only `GOVERNED_ARTIFACTS`. |
| V6 | Writer is not itself digest-pinned | grep `validate_powermetrics_fiducial` in `calibration_bracketing.py`, `calibration_ledger.py`, the registration, `night_kinds.py`: no hits | TRUE. The chain is pinned (Revision 3), the writer is not; the chain invokes the writer at `calibration_derivation_only.zsh:251-262` and treats rc 0/1 as finalized, any other rc as `slot_refused` with the session OPEN (`:268-278`). |
| V7 | Issuer dry run and `_select_members` skip non-valid slots | `registration_dry_run` `:175`; skip at `:214-216`; `_select_members` `:1061`, skip at `:1076-1077`; called from `_prepare_candidate` at `:1351-1353` after the powermetrics-pin check | TRUE. A battery-confounded ordinary-invalid slot is invisible to both today. |
| V8 | `_read_member_evidence` authenticates only `manifest.json` and `instrument_evidence.json` against the ledger row | `:902-941` | TRUE. Raw battery bytes must be authenticated through a digest carried INSIDE `instrument_evidence.json`. |
| V9 | Scored reducer `_check_window` authenticates nothing behind `bundle_sha256` | `scored_reduce.py:91-109` (`_hex(w["bundle_sha256"])` only); `reduce` at `:145` takes caller-supplied `capture_windows`; no production caller (grep: only `tests/test_scored_reduce.py`) | TRUE. |
| V10 | Arm check runs machine predicates only for flagged kinds | `evidence_night.check` `:1335-1395`: `machine_quiet` and `corecaptured` run only when `NIGHT_KINDS[kind].non_observer_at_arm_and_t0` / `corecaptured_at_arm_and_t0`; a derivation kind is not the `quiet_predicate_evidence` kind | TRUE. A battery check placed inside those branches would skip W1. It must sit outside them. |
| V11 | `publish_install` reaches `os.replace` after other work; successor claim created just before | `evidence_night.py:1760-1783` | TRUE. A fresh read belongs after `successor_check` and before `_create_successor_claim`/`os.replace`. |
| V12 | Direct installer route | `night_agent_install.validate_install` `:1166`, invoked at `:1373`; `arm_retry.py:339` text: "Direct install_night_agent.sh performs no successor check; a follow-up lane owns that route" | TRUE. |
| V13 | Transaction-pack t0 power row | `arm_readiness_evidence_t0._derive_power` `:1839-1850` reads `pmset -g batt`, requires `AC Power` | TRUE. |
| V14 | Zero-capture successor set | `arm_retry.py:21-25` `ZERO_CAPTURE_MACHINE_REFUSALS`; `terminal_zero_capture_refusal` `:204-244`; `COLD_GATE_CODES` explicit table `:33-45`; D-182 text `decision_log.md:11979-11984` lists the machine-state classes | TRUE. D-182's enumerated classes do not name battery state; adding the code to the frozenset is an extension of D-182's list that Ed's directive #421 ("failure postpones the arm") supports, and the addendum text below records it. |
| V15 | Ledger disposition vocabulary is closed | `validate_powermetrics_fiducial.py:1707-1712` (`invalid_evidence_disposition` ∈ {None, CLOCK_ANCHOR_UNRESOLVED, DETECTION_NONCONVERGENT}); `instrument_evidence` refuses unregistered projection dispositions `powermetrics_fiducial.py:1391-1396` | TRUE. Battery confounding must NOT be a new ledger disposition; it is a window-level verdict the consumer computes from authenticated evidence. |
| V16 | Registration text | Revision 1 "Membership", "Exclusions", "Stopping" at `preregistration…rev1.md:156-175`; Revision 5 `:600-614`: "Every valid resolved member is retained", the 150 ms cadence stop and the "<6 valid of 12" stop, "No B-based exclusion or outcome-driven top-up", "Rules are fixed here before capture" | TRUE. |
| V17 | Revision 5 state at `origin/main` | file digest `977e3c9b…`; placeholder grep count 1; PR #418 (`feat/2026-09-25-rev5-seal`, "Seal registration Revision 5 launch-context pins at PR-L merge 9b750bf3 (A-R5a-1)") is OPEN, `mergeCommit: null` | TRUE: Revision 5 is unsealed at `origin/main`; the seal is PR #418. |
| V18 | Live battery | 14:33 PDT: `ExternalConnected = Yes`, `IsCharging = Yes`, `InstantAmperage = 739`, `Amperage = 739`, `Voltage = 12956`, `Temperature = 3038`, `FullyCharged = No`, `CurrentCapacity = 100`, `AppleRawCurrentCapacity = 7516`; ≈14:38: `InstantAmperage = 488`, `Amperage = 488`, `UpdateTime = 1790372265`. Exactly one AppleSmartBattery object; each of `"IsCharging"`, `"InstantAmperage"`, `"ExternalConnected"`, `"Amperage"` occurs exactly once in the full (undepth-limited) output; `"AppleRawExternalConnected"` also exists, so the parser must match the quoted key. | Float NOT OBSERVED this session: the pack is still in finishing charge at 100 %. |

Executed evidence: every row above was produced by `sed -n`/`grep` on the worktree files, `shasum -a 256`, `ioreg`, `pmset`, `gh pr view`, in this session.

### 3.2 Findings (severity independent of verdict)

- **F-1 (MATERIAL) — A4's placement of the battery digests breaks a custody authenticator and gains no ledger coverage.** Both seats and A4 say: add `raw/battery_float.*` to `instrument_evidence.json.artifact_sha256` and `manifest.json.artifacts`. Verified: `calibration_ledger.py:3027` requires `set(manifest_artifacts) == set(MANIFEST_BOUND_ARTIFACTS)` and `:3036` requires `set(evidence_artifacts) == set(EVIDENCE_BOUND_ARTIFACTS)` (constants `:133-146`) inside `_inspect_historical_candidate` (`:2971`), used by `_discover_historical_candidates` (`:3083`) and `prepare_historical_import` (`:3174`). A bundle carrying an extra inventory entry becomes unimportable on that path ("manifest artifact hash mismatch"). The live issuance path (`_read_member_evidence`, `_load_calibration_candidate_unbounded` at `calibration_bracketing.py:1621-1629`) checks named entries only and would tolerate the extra keys, so this is not a W1 blocker, but it is a latent custody defect. Separately, the ledger row's `artifact_sha256` comes from `ledger.artifact_hashes`, which hashes only `GOVERNED_ARTIFACTS` (`:286-312`, worker `:45-56`), so the raw battery files are never covered by the row no matter which inventory names them. **Cure (ruled):** leave both inventories byte-for-byte as today; add one top-level key `battery_float` to `instrument_evidence.json` (sibling keys are tolerated by design; the writer already adds `derivation_only`, `screen_basis`, `clock_anchor`, and `_classify_capture`'s comment at `:2585-2589` relies on it) carrying, per observation, `raw_stdout_sha256` plus the verbatim matched property lines and parsed values; write the raw stdout to `raw/battery_float.pre.ioreg` and `raw/battery_float.post.ioreg`. Coverage chain: ledger row → `instrument_evidence.json` sha256 → `battery_float.*.raw_stdout_sha256` → raw bytes. The consumer authenticates that chain. Add a pin-regression test that `manifest.artifacts` and `instrument_evidence.artifact_sha256` key sets are unchanged.
- **F-2 (MATERIAL) — A5 omits the first harvest consumer Revision 5 names.** Revision 5 (`:612`) orders the harvest: cadence report on raw plists FIRST, then the count-only dry run. Astra names `calibration_cadence_report.report_window` (`:44`); Sol and the synthesis do not. **Cure:** the battery window verdict runs before the cadence report and before the dry run, in one harvest entry point; `report_window` itself calls the validator so a direct call cannot skip it (its output on a confounded window is labelled diagnostic).
- **F-3 (MATERIAL) — A2's arm-side sites are under-specified.** (i) In `evidence_night.check` the battery check must be unconditional, outside the `NIGHT_KINDS` row-flag branches (`:1370-1395`), otherwise W1 (a derivation kind) skips it (V10). (ii) The direct-install route `night_agent_install.validate_install` (`:1166`) must carry the same predicate (V12); the synthesis dropped Astra's site 4. (iii) `arm_readiness_evidence_t0._derive_power` (`:1839`) gets the predicate for transaction packs (both seats agree; synthesis silent).
- **F-4 (MATERIAL) — refusal-code vocabulary must be one.** Sol: `night_refused_battery_float`; Astra: `night_refused_battery_not_float` + `night_battery_probe_error`. Ruled in §7: exactly one new code, `night_refused_battery_float`, for a successfully observed predicate failure; a failed, timed-out, malformed, duplicate or missing observation is the existing `night_probe_error` at the probe's position (matches `night_gate.py:248-250` and `_probe_refusal`). Only `night_refused_battery_float` joins `ZERO_CAPTURE_MACHINE_REFUSALS`; `night_probe_error` stays ineligible as today.
- **F-5 (MATERIAL, B6) — the coulomb counter closes most of the "between brackets" gap for free.** `AppleRawCurrentCapacity` (mAh, integer) is in every ioreg read. Over a slot, `ΔQ = post − pre` is the net charge into the pack between the two brackets, which two point samples of `InstantAmperage` cannot see. Under #421 §2 ("anything germane… is mandatory") this is mandatory once it costs nothing extra. **Ruled:** each observation also records `AppleRawCurrentCapacity`, `Amperage`, `Voltage`, `Temperature`, `FullyCharged`, `UpdateTime`; the harvest predicate adds `|ΔQ_mAh| ≤ ceil(0.2 A × (t_post − t_pre)/3600 s) + 1` (the +1 is gauge resolution; for a ≈480 s slot the allowance is 28 mAh, the same 200 mA bound expressed as an integral). Worked example: pre 7516 mAh, post 7541 mAh, 485 s apart → ΔQ = 25 ≤ 27+1 → passes the integral screen (25 mAh in 485 s is 186 mA average).
- **F-6 (MATERIAL, W1 prerequisite, B6) — a battery logger is running on the measurement machine.** `/tmp/4b-osaudit/battery-log.sh` samples every 30 s (78 rows by 14:33; #420 says until ≈15:30 PDT). Derivation kinds do not run the non-observer predicate (V10), so the census will not catch a shell loop. It must be proven dead before W1 arms (see §7 prerequisites).
- **F-7 (NIT) — `Amperage` vs `InstantAmperage`.** Both were equal on both live reads. The predicate is on `InstantAmperage` as #421 fixes it; `Amperage` is recorded, not gated. Do not substitute one for the other (Sol is right).
- **F-8 (NIT) — the procedural gate in the uncommitted arm scripts** (`arm-env.zsh:30-59`, other worktree) matches the quoted key, requires exactly one occurrence, converts unsigned 64-bit, exits 3 on failure. It is adequate as the stopgap #421 §1 demands until the code gate lands, with one gap: it does not record `AppleRawCurrentCapacity`. Its README "HARVEST CHECK" over `is_charging` is void (ex-03 F2) and is replaced by this ruling.
- **F-9 (NIT) — perturbation.** `ioreg -r -c AppleSmartBattery` is a user-space registry query of a few tens of milliseconds; at t0/arm no sampler exists; in the writer the brackets sit before `_sampler_lifetime` spawn (`:2297`) and after `AFTER_SAMPLER_TEARDOWN` (`:2452`), outside the measured interval, and the raw-file writes happen there too. No path touches the sampler's live window. During-slot polling stays out (A7 affirmed).

### 3.3 Verdicts on A1–A8

- **A1 AFFIRM**, with the parser rules fixed in §7.1.
- **A2 AFFIRM as amended** by F-3 and F-4 (unconditional in `check`; fresh read before `_create_successor_claim`/`os.replace`; `validate_install`; `_derive_power`; one code).
- **A3 AFFIRM** (V4).
- **A4 AFFIRM as amended** by F-1 (placement) and F-5 (fields).
- **A5 AFFIRM as amended** by F-2 (cadence report first) and this clarification: the validator evaluates every slot of every session in the registration that has a custody directory or a finalized ledger row, whatever its disposition; a declared slot the window never reached (`window_exhausted`) has no bracket obligation.
- **A6 AFFIRM** (V9 for the scored boundary; controller and envelope sites as the seats cite; not W1-blocking, see B2).
- **A7 AFFIRM as amended** by F-5: no polling, and the integral screen is added, with the residual limit disclosed (a charge-then-discharge excursion that nets to ≤ 28 mAh inside a slot is invisible; its thermal input is bounded by the same order as 200 mA sustained).
- **A8 AFFIRM**: `protocol_v3.json` unchanged; a prospective addendum is required before W1 (B3).

Bypass audit (charge B1, "any caller that could bypass the consumer"): the consumer must be called from `registration_dry_run` (`:175`, inside the `terminal` branch before the per-slot loop), `_prepare_candidate` before `_select_members` (`:1351`), `_load_calibration_candidate_unbounded` (`calibration_bracketing.py:1542`), `evaluate_calibration_bracket` (`:1965`, whole-session), `calibration_cadence_report.report_window` (`:44`), and `issue_epoch_continuation` (`:95`) if it remains callable for new sessions. With those six, every path that reads a derivation B or counts a derivation slot at `c6814dd8` passes through the validator. I found no other reader of `finalized_slots` that reaches a B value.

## 4. B2 — split (S1 against P1)

**AFFIRM P1 (two PRs by window kind), REJECT Sol's split by layer, REJECT Astra's single vertical PR as the W1 gate**, with two binding clauses:

1. **BFG-D** (A1, A2 as amended, A4 as amended, A5 as amended, the six consumers of §3.3, tests of §7.6) must be merged to `main` before W1 may arm. Its t0/arm admission is universal (it sits in `_check_machine`, `evidence_night.check`, `publish_install`, `validate_install`, `_derive_power`), so every window kind is admission-gated from BFG-D onward.
2. **BFG-S** (A6: quiet-envelope brackets and `summarize`/`pilot_summary` consumers; controller brackets and `BundleReader.metadata()`/`reduce_bundle` consumer; the scored reducer's authenticated window evidence) must be merged before any non-derivation window (quiet-predicate evidence, controller/scored bundle, transaction pack) may arm. It is a registered obligation of the lane, not a discretionary follow-up; BATTERY-FLOAT-GATE-01 closes only when both have merged, and the BFG-D PR body must say it does not close the lane.

Reason: Sol's admission-first PR would leave a window between merges in which an admitted night has no harvest evidence, and W1 needs both layers anyway; Astra's single PR holds W1 for controller and scored code W1 never executes. P1 makes every window that runs fully covered without holding W1 on unexercised code.

## 5. B3 — registration

**Addendum needed: AFFIRM.** Revision 1's "Membership" retains every valid resolved observation and its "Exclusions" clause registers exactly three outcome-independent mechanisms (`:156-171`); Revision 5 says "Every valid resolved member is retained" and fixes the count stops (`:612`). A whole-window battery exclusion is a fourth mechanism and changes count handling; #421's harvest rule cannot be applied to W1 without registering it before capture.

**S2: AFFIRM P2's one bounded replacement; REJECT Astra's halt-by-default.** The confound is decided from instrument state alone, before the cadence report, the dry run, or any B is read, so a replacement cannot select on outcome; halting would spend a council round to reach the same rule. The bound (one replacement, then stop) is an anti-spiral rule against a persistent charging misconfiguration.

**Count handling (ruled):** a confounded window contributes nothing to any rule of the registration: not to the "<6 valid of 12" stop, not to the 150 ms cadence stop (its cadence report is produced and disclosed as a diagnostic), not to n, not to W3's trigger. Its ledger rows are retained; its B values are never read by the issuer (the validator runs before `_select_members`); the window's identity, the failing slots, their raw digests and reasons go into the harvest record and the next notice.

**Landing (ruled):** PR #418 merges as ruled (sealing A-R5a-1). The addendum lands afterwards as its own labelled amendment **A-R5b** appended below the sealed Revision 5 text, never editing sealed words, with a `docs/decision_log.md` entry, and the whole-file digest after A-R5b is the one pinned in the W1 notice and arm material. Sequencing is P5's.

**Text of A-R5b** (replaces P2's text; issue verbatim):

> # Revision 5 — Amendment A-R5b (2026-09-25): battery float (directive #421)
>
> Revision 5 above is sealed; not one word of it is edited here. This amendment adds one outcome-independent, mechanism-named exclusion decided from instrument state alone, and the rules that follow from it. It authorizes no window and licenses no measurement.
>
> **Predicate.** A battery-float observation is one run of `/usr/sbin/ioreg -r -c AppleSmartBattery` whose raw standard output is retained. It PASSES when exactly one AppleSmartBattery object is present and, read from that object's top-level properties, `ExternalConnected = Yes`, `IsCharging = No`, and `|InstantAmperage| ≤ 200 mA`, where a printed value at or above 2^63 is read as that value minus 2^64 (two's complement; example: `18446744073709551458` reads −158 mA). A missing, duplicated, malformed or unreadable property, a failed or timed-out probe, or more than one object is not a pass. `Amperage` is recorded but never substituted for `InstantAmperage`. Each observation also records `AppleRawCurrentCapacity` (mAh), `Amperage`, `Voltage`, `Temperature`, `FullyCharged` and `UpdateTime`.
>
> **Admission.** A window is admitted only if the predicate passes at the arm check, again immediately before publication, and again at t0 inside the night gate's C3 row (refusal code `night_refused_battery_float`; probe failures are `night_probe_error`). A t0 or arm refusal with zero capture is a machine-state refusal under D-182: it licenses one new-plan successor on D-182's terms and is never a same-plan retry and never waived.
>
> **Per-slot evidence.** Every derivation slot records one observation immediately before its sampler is spawned and one immediately after the sampler is torn down, on every exit path the writer controls. The raw bytes are retained under the slot's custody as `raw/battery_float.pre.ioreg` and `raw/battery_float.post.ioreg`; their SHA-256 digests, the verbatim property lines and the parsed values are recorded under the key `battery_float` in the hashed `instrument_evidence.json`. The registered protocol, chain digest, sampler set and estimator-code pins are unchanged.
>
> **Window verdict.** Before the cadence report, before the count-only dry run and before any B value is read, every slot of the window that has a custody directory or a finalized ledger row, whatever its disposition, is checked: both observations must be present, authenticated against the recorded digests, re-parsed from the raw bytes, and must pass the predicate; and `|AppleRawCurrentCapacity_post − AppleRawCurrentCapacity_pre| ≤ ceil(0.2 A × (t_post − t_pre) / 3600 s) + 1 mAh`. One slot failing the predicate or the charge-delta bound makes the whole window `battery_float_confounded`; one slot with a missing, unparseable or unauthenticated observation makes it `battery_float_evidence_missing`. Either verdict is final for that window. A declared slot the window never reached (`window_exhausted`) carries no obligation.
>
> **Consequences.** A confounded window is retained and disclosed. None of its slots is a member; none counts toward the "fewer than 6 valid of 12" stop, the 150 ms cadence stop (its cadence report is produced as a diagnostic only), n, or W3's trigger; its B values are not read. The harvest record and the next arm notice name the window, the failing slots, the raw digests and the reasons.
>
> **Replacement.** A confounded window is replaced once by a fresh window of the same kind under the same protocol, at least 6 h after the confounded window's start, because the verdict is decided from instrument state alone and before any B or disposition is read, so replacement cannot select on outcome. A second consecutive confounded window stops the epoch and returns to council. No other top-up is permitted.
>
> **Disclosure.** Two observations bound the slot's endpoints and its net charge; a charge-then-discharge excursion netting to within the charge-delta bound inside one slot is not detectable by this rule and is disclosed as a limitation. The 200 mA bound is a screen of thermal state for powermetrics-only windows; it is not an energy bound for a wall-meter window (see WALL-METER-GAIN-01).

## 6. B4 — threshold physics (P3)

**AFFIRM P3 as amended.** For powermetrics-only windows 200 mA is an adequate gross screen: powermetrics integrates on-SoC rails (`cpu_power,gpu_power,ane_power`), through which charge current does not pass, so the only coupling is thermal. Pack heating at 0.2 A is I²R ≈ 0.04 A² × ≈0.1 Ω ≈ 4 mW against ≈1.2 W plus charger-converter loss at the 3.5 A seen at 12:30 today; the 600 s settle and the existing thermal gate (`night_gate.py:1556-1585`) remain in force above it. The integral screen of F-5 is added so the bound also holds between brackets.

Before any wall-meter window, P3's "tighter bound" is **insufficient as stated**; it must be an ENERGY bound. At 12.95 V, 200 mA is 2.59 W, 1.24 kJ over a 480 s capture, three orders above the ≈1 J attribution floor. A current screen small enough to matter (≈5 J / (12.95 V × 480 s) ≈ 0.8 mA) is below the gauge's integer-mA reporting and its noise; and the coulomb counter's 1 mAh step is 46.6 J. Ruled: no wall-meter window is claim-bearing until WALL-METER-GAIN-01 registers, with this arithmetic, a bound on the battery's net energy over the capture (from a measured float-current distribution, an external shunt, or a labelled floor), not a point-sample current screen.

## 7. Battery-float rulings (final texts)

### 7.1 Predicate and parser
- Probe: `("/usr/sbin/ioreg", "-r", "-c", "AppleSmartBattery")`, no shell, bounded timeout (10 s), raw stdout retained as bytes.
- Exactly one object (`+-o` line count = 1); each of `"ExternalConnected"`, `"IsCharging"`, `"InstantAmperage"` matched by the QUOTED key at the top-level property indentation, exactly once each; `"AppleRawExternalConnected"` must not match. Booleans `Yes|No`; integer decimal lexeme kept as a string; signed = n − 2^64 if n ≥ 2^63, else n; reject n ≥ 2^64 or n < −2^63.
- PASS iff external_connected ∧ ¬is_charging ∧ −200 ≤ signed_mA ≤ 200. Boundaries: ±200 pass, ±201 fail.
- Also parsed and recorded, never gated at t0/arm: `Amperage`, `Voltage`, `Temperature`, `FullyCharged`, `AppleRawCurrentCapacity`, `UpdateTime`.
- One shared module (`joulewise/battery_float.py`) owns probe, parse, predicate, record schema and replay validation; nothing re-implements them.

### 7.2 Refusal codes
- `night_refused_battery_float`: added to `NIGHT_GATE_REASON_CODES`, to `ORDER` immediately after `night_refused_not_quiet`, to `arm_retry.COLD_GATE_CODES` with an explanation ending "Zero-capture successor route per D-182", and to `ZERO_CAPTURE_MACHINE_REFUSALS`.
- Probe/parse failure: existing `night_probe_error` via `_probe_refusal` (never eligible for the successor route).
- Harvest verdicts: `battery_float_confounded`, `battery_float_evidence_missing` (strings in the validator's result; refusal reasons in the issuer's `PrepareRefusal`).

### 7.3 Insertion sites per PR
BFG-D: `night_gate._check_machine` after the AC check (`:1505`), storing `rows["C3"].measured["battery_float"]` (raw stdout, lexemes, parsed, verdict) on both `legacy_load` branches; `evidence_night.check` as an unconditional `inspect("battery_float", …)` before the kind-flagged branches; `evidence_night.publish_install` after `successor_check` and before `_create_successor_claim`/`os.replace`, journaled in the attempt directory; `night_agent_install.validate_install`; `arm_readiness_evidence_t0._derive_power`; writer brackets at `validate_powermetrics_fiducial.py` after `:2228` (raw dir exists) and before `:2297` (spawn), and after `:2452` (teardown), the post observation also attempted in `finalize_abandoned`; consumers per §3.3.
BFG-S: `sample_quiet_predicate_evidence.collect` brackets and `summarize`/`quiet_predicate_campaign.pilot_summary`; `controller._run_lifecycle` brackets (before `_stage_idle_baseline`, after `_stage_idle_drift_sentinel`, never inside `sampling_started`…`sampling_stopped`) with `metadata.json.battery_float` and raw files in the bundle; `BundleReader.metadata()` validation so `reduce_bundle` fails closed; `scored_reduce.reduce` taking authenticated window evidence (input-contract change, prospective).

### 7.4 Record schema (`battery_float`, one per observation; the slot record holds `pre` and `post`)
`schema` (`joulewise.battery_float.v1`), `policy_id` (`bfg-01`), `limit_ma` (200), `phase` (`arm_check|publish_install|t0|slot_pre|slot_post|…`), `plan_id`/`session_id`/`slot`/`attempt_id` where applicable, `wall_time_s`, `monotonic_before_ns`, `monotonic_after_ns`, `argv`, `exit_code`, `timed_out`, `stderr`, `raw_stdout_sha256`, `raw_path` (custody-relative, slots only), `object_count`, `property_lines` (the verbatim matched lines), `external_connected_raw`, `is_charging_raw`, `instant_amperage_raw`, `external_connected`, `is_charging`, `instant_amperage_ma`, `amperage_ma`, `voltage_mv`, `temperature_raw`, `fully_charged`, `apple_raw_current_capacity_mah`, `update_time_s`, `passed`, `reasons`.

### 7.5 Consumers
One `validate_window(session_or_window) → {"status": "pass"|"battery_float_confounded"|"battery_float_evidence_missing", "slots": […]}` that re-reads raw bytes, authenticates `raw_stdout_sha256` against the hashed evidence, re-parses, applies the predicate and the charge-delta bound, over every slot with custody or a finalized row. Called from the six sites in §3.3 (BFG-D) and the BFG-S sites in §7.3. It never trusts a stored `passed`.

### 7.6 Test obligations (defect-shaped, production call sites)
1. Real-format fixture captured from this machine today (the `IsCharging = Yes`, `InstantAmperage = 739` output) through `night_gate.evaluate_night` and `evaluate_dynamic_hard` via `Probes` injection: refusal `night_refused_battery_float`, C3 `measured.battery_float` holds the raw text, no GO; update the exact probe-sequence assertion at `tests/test_night_gate.py:1320-1330`.
2. Parser on byte strings: `18446744073709551458` → −158 pass; +200/−200 pass; +201/−201 fail; `IsCharging = Yes` with 0 mA fails; missing, duplicate, `Amperage`-only, two objects, truncated output → probe error; `AppleRawExternalConnected` must not satisfy the `ExternalConnected` match.
3. `evidence_night.check` on a derivation-kind candidate refuses on a charging fixture (proves the check is outside the kind flags); `publish_install` with a fresh charging observation creates no successor claim and does not rename.
4. `terminal_zero_capture_refusal` accepts `night_refused_battery_float` with proven zero-capture facts and rejects it after capture and rejects `night_probe_error`.
5. Writer run under the logical test clock produces both raw files and the `battery_float` key; `manifest.artifacts` and `instrument_evidence.artifact_sha256` key sets are byte-identical to today's (pin regression), as are `SAMPLERS`, `protocol_v3.json`, the four `ESTIMATOR_CODE_PATHS` digests and the chain digest.
6. A finalized ordinary-invalid slot whose `post` observation shows `IsCharging = Yes`: `registration_dry_run` reports the window confounded and counts nothing; `_prepare_candidate` refuses before `_select_members`; `report_window` labels its output diagnostic; a tampered raw file fails authentication in `_load_calibration_candidate_unbounded`.
7. Charge-delta: pre 7516 / post 7600 mAh over 480 s → confounded even with both point predicates passing.
8. A writer crash before the post observation leaves `battery_float_evidence_missing`, never pass.

### 7.7 W1 arm prerequisites, in order
1. PR #418 merges (Revision 5 sealed, placeholder count 0).
2. BFG-D merges to `main` under the full gate.
3. A-R5b lands as its own labelled amendment with a decision-log entry; the new whole-file digest is the one in the W1 notice.
4. The `/tmp/4b-osaudit/battery-log.sh` logger is proven dead (`pgrep -fl battery-log` empty) and its JSONL archived; no other periodic sampler runs.
5. The battery has reached float: two `ioreg` reads ≥ 5 min apart with `IsCharging = No` and `|InstantAmperage| ≤ 200`; the raw values go in the arm record (first-ever observation of float on this machine; NOT OBSERVED this session).
6. The procedural gate in the arm scripts (C9) runs at discovery and immediately before publication in addition to the code gate, until BFG-D is proven on a real receipt.
7. W1 uses the n1 frozen calibration plan `configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json`, sha256 `9ab4776f3c416284d6d01a5a49587eedcdfbcb8ef61428cdc1046e9b9d74a072`, byte-pinned in the notice (B5).

## 8. B5 — W1 frozen calibration plan (P4)

**AFFIRM P4.** `gen_derivation_night.py:564-571` reads the frozen plan only for its `plan_id`; neither the chain (`calibration_derivation_only.zsh`) nor `run_night.py` passes a calibration plan to the writer (grep: no `calibration_plan` reference in either), so the file is lineage identity, not a measurement input. Nothing in Revision 5 names a different plan; changing it would add a second difference from n1/n2 for no registered reason. Pin its digest (above) in the notice.

## 9. B6 — what the seats and synthesis all missed

F-1 (inventory exact-set checks and the ledger's fixed governed set), F-2 (cadence report is the first harvest consumer), F-5 (the coulomb counter gives an integral screen for free), F-6 (the live 30 s logger must be dead before W1), and the wall-meter arithmetic in §6 (a current screen cannot be an energy bound at this instrument's resolution). One observation for Ed, not a rule: under the 80 % limit the pack sat idle above its limit; under 100 % any dip triggers a top-up (the 09-23 −439 mA reading and today's afternoon show both directions), so the 100 % setting makes confounded windows more likely. The gate handles either setting; the choice is Ed's; whichever is chosen is now recorded per slot.

## 10. Disagreements with the lead's labelled disposition

- ex-30 A4 as written: amended (F-1).
- ex-30 A5: amended (F-2, all-slots clarification).
- ex-30 A2: amended (F-3, F-4).
- ex-30 P2: replaced by the A-R5b text in §5 (adds the charge-delta bound, the all-slots rule, the diagnostic cadence clause, the "verdict is final" clause, and the DISCLOSURE paragraph).
- ex-30 P3: amended (energy bound, not current screen, for wall-meter windows).
- ex-30 P1, P4, P5: affirmed as written.

Where I am silent, I concur.

## 11. Plain summary for Ed (8 lines)

1. Your battery rule is sound and is now written so it can be built without further choices; it changes no registered number and no sampler.
2. One PR (BFG-D) must merge before W1: the t0/arm refusal, a before/after battery reading on every slot, and a harvest check no caller can skip. A second PR covers the other window kinds and must merge before any of those run.
3. The seats' hashing plan would have broken a custody importer; the fix is to record the battery digests inside the already-hashed evidence file.
4. A short registration amendment (A-R5b, text above) is required before W1, landing after the seal PR #418; a confounded window is thrown out whole and replaced once, then the epoch stops.
5. Extra for free: the gauge's mAh counter is read before and after each slot, so charging between the two readings is caught too.
6. 200 mA is fine for powermetrics windows; it is nowhere near an energy bound for the wall meter, which needs its own arithmetic before any wall-meter claim.
7. The battery is still in finishing charge at 100 % (739 → 488 mA over five minutes); nobody has yet seen it float, so W1 waits for two clean readings.
8. The 30-second battery logger in /tmp must be stopped before W1 arms.
