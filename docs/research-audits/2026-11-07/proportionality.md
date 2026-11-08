# Proportionality and pruning audit: reconciled synthesis

2026-11-07. This reconciles two independent seat reports on one brief. Seat 1 was Fable 5.1 and seat 2 was Opus 5.5. An Opus 5.5 synthesis seat merged them and re-checked against the repo every claim that was disputed or that a recommendation rests on. Both seat reports are reproduced verbatim in the appendices.

**Brief.** Ed's advisor says the project over-engineers simple measurements. The lead keeps blinding and preregistered-estimator fidelity, and treats every other guard as negotiable (a lean redesign is OK). The audit looks for guards, checks, review rounds and code paths whose cost exceeds the protection they give.

**Heads read.**
- `lane/2026-11-06-v4-r1-integrated@e901eb2a4`: R0 host code, R1 runtime and driver, `run_night`, the v4 kit, LEAD-RULINGS-1/2.
- `lane/2026-11-05-align-pilot10-benign@5f817856b`: the measurement lane R0 runs from (#692 merged). `e901eb2a4` contains it.
- `main@bd7a3efcd`: the Block-5 tooling, `RUN_STATE.md` items 178-202, `CANONICAL.md`, `docs/process/gate_policy.md`.
- The R0 record branches `records/2026-11-0{6,7}-align-r0-v4*`. Only the status fields of each `docs/align/r0/*/report.json` were read.

**Blinding.** The synthesis seat did not list or open any path under `/Users/edr/jw-b5-*`, `/Users/edr/night-*`, `night-custody`, `night-archive` or any `restricted/` directory. No Block-5 estimate, contrast or verdict was read or inferred. One Block-5 record was read: `docs/run_reports/2026-11-07-b5-release-hold-trace.md`, which is structure-only by construction. Only its defect labels and code locations are cited here.

**Method limits.** The synthesis seat ran no tests, loaded no model weights and opened no external source. Test wall times appear only in the seats' own reports (appendices).

**State when this was written (16:55 PST, 11-07).** R0 re-run 8 had not launched; it is planned for 17:15 PST or later (item 201). Nothing here changes that launch.

---

## 1. Executive summary

1. **The seats agree on their top two prunes.**
   - R0's per-process CPU-contention refusal caused 4 of R0's 8 stops and protected no reported or blinded quantity.
   - The W1 High Power restore stack accounts for 10 of the 11 HIGH/MEDIUM review findings in R1 rounds 6-8. By the reviewers' own words it cannot admit bad data.
   - The seats differ only on how far to cut. Section 8 gives the ruling.
2. **R0 has run 8 times with 8 stops and no pass.**
   - Over about 33 h it used 8,824 s (2.45 h) of Mac time, the sum of the eight `report.json` `total_seconds`.
   - The stops were: 1 launcher bug, 3 defects in R0's own checks or harness, and 4 contention refusals. None found a fault in the hardware, the model artifact or the sensors.
   - `ladder` and `long-decode` never ran. `ladder` produces `R0.reasoning_effort`, the only R0 output R1's kit needs.
3. **New finding: the cheapest unblock was ruled but cannot be launched.** The lead's ruling R0-L1 (item 196 (2), about 03:00 PST 11-07) authorised a non-SMC R0 run "in the next clean gap", which would produce the ladder rung without touching the contention-sensitive SMC step.
   - The sanctioned headless launcher writes a fixed runner spec carrying only `--config` and `--output` (`scripts/launch_align_r0.py:201-202@bd7a3efcd`). It cannot pass `--checks` or `--keep-going`.
   - `RUN_STATE.md` records no attempt at that run. The 06:15-11:05 gap went unused (item 195 :1246).
4. **R1's own code does not use R0's refusal.** On a grep of `r1_runtime.py`, `align_r1_rehearsal.py`, `align_r1_runtime.py`, `thermal_gates.py` and `run_night.py` at `e901eb2a4`, none references `NotQuiet`, `CpuQuietProbe`, `QuietGuard` or prewindow's CPU limit. The R1 runtime calls only `smc_enumeration.rank`, not `collect` or `require_quiet` (`r1_runtime.py:280-290`).
   - One caveat: `run_night.py` runs `prewindow_check.sh` on its `DIAGNOSTIC_NO_PACK` derivation-admission path (:4606-4617, :3861). Whether an R1 night's plan reaches that path was not traced.
   - R1's OS-load rule is ruling 8: redo a segment when the CPU-load journal exceeds 0.5 cores for 60 s in a row, and refuse the night only after two redos (`align_r1_rehearsal.py:157-159, 872-873, 1064, 1107`).
   - None of R0's four contention refusals came near that bar. This partly answers item 202 (4).
5. **Block 5 is already lean, and its comparator earned its cost.**
   - On dry-j the release comparator held with 1,001 failing rows. The blind trace attributed them to six defects: one in L9, three in the recompute, one in the comparator's mapping, and one (D5) still undecided.
   - What remains to prune is mass, not ceremony:
     - per-PR CI time on the heavy audit's tests (about 21-23 % of CI CPU);
     - round-named test modules;
     - two retired paths, to delete after the release.
6. **The process cost is larger than the code cost.**
   - Executing reviews, cold passes and Sol critiques are applied above what `gate_policy.md` requires, on code that has never run on hardware.
   - Full-suite CI of 2-3 h is the merge gate on the measurement lane.
   - The doctrine "physics refuses; everything else is a flag" is enforced mechanically only on the HAZARD_PACK path. No R0 or R1 module is inside its scan.

## 2. Decisions needed from the lead

1. **R0 contention (rank 1).**
   - Make the CPU-contention branch of `QuietGuard.check` a recorded flag for every non-SMC check.
   - For SMC, replace the 0.05 CPU-s/s `NotQuiet` with R1's ruling-8 rule: redo the SMC stage once on more than 0.5 cores sustained for 60 s, then flag and proceed.
   - Keep the armed-window, LaunchAgent, chain and custody refusals.
   - Also decide whether this lands before or after re-run 8. Re-run 8 is on unchanged code.
2. **The R0 launcher (rank 2).** Approve a small tooling change so `launch_align_r0.py` passes `--checks` and `--keep-going` through to the runner, and make `--keep-going` the default for R0 desk runs.
   - That makes R0-L1's composition launchable headless.
   - Under gate policy rule 2 it needs CI and its own regression test only.
   - If re-run 8 is refused by contention again, the composition path in item 196 (3) already completes R0 without a live SMC re-run, once this lands.
3. **W1 power mode.**
   - Option A: rule now that W1 runs in Automatic whatever R1's A-B-A shows, and keep the A-B-A as an R1 diagnostic. Protocol v4 is an unregistered draft (`pilot_protocol_v4.md:3`), and High Power adoption rests on n = 1 per condition (`CHAIR.md:322`).
   - Option B: keep adoption conditional.
   - Under A, the W1 High Power arming path is deleted after R1. Under B, it is simplified only if R1 adopts High Power.
   - **Either way, freeze the stack now:** no further desk round. A new finding on it is recorded, not fixed, unless it can admit bad data.
4. **The review-round rule.** Apply `gate_policy.md` as written:
   - rule 2 for tooling;
   - rule 3's two executing seats, launched together, count as the cold pass;
   - Sol critiques are advisory.
   - Add one rule: after one number-bearing review round, a measurement component gets no further desk round until it has run once on hardware.
   - Also decide whether to revive or delete rule 9's pruning tally. It appears in two comparator build reports and nowhere in the ALIGN records.
5. **The measurement-lane merge gate.** Gate on `scripts/quick_suite.py --tier touched` plus `tests/align`. Run the full suite after the merge, without blocking, and revert on red.
6. **Ruling 1(f) and the 1(e) fallback.** The kit is expected to refuse W1 at about 20 tok/s (R7-2, R8-8). Choose one:
   - (a) Pre-commit now that the kit applies the protocol's named fallback order (`pilot_protocol_v4.md:610`) mechanically and records the step taken. The duty bar already has this mechanism (`DUTY_FALLBACK_STEPS`, `align_v4_kit.py:176`).
   - (b) Keep the post-R1 ruling, but book the lead's time for the morning after R1, so the round-trip does not cost a night.
7. **An INCONCLUSIVE designed-start-state segment.** Today any INCONCLUSIVE calibration segment refuses W1, and the remedy is a full 15-25 h R1 re-run (`align_v4_kit.py:194-208`). Choose between:
   - (a) U5 recorded as INCONCLUSIVE, a verdict the kit already admits (`U5_VERDICTS`, :171);
   - (b) a patch night that re-runs only the missing segments against a fresh soak;
   - (c) the status quo.
   - A step-d INCONCLUSIVE stays a refusal under every option.
8. **R1's `window_max_s`.** Set one generous constant that covers the all-retries case (90,663 s or more), and stop re-deriving the worst-case table every round.
   - Separately, the no-redo R1 night (56,207 s) is now 11,567 s longer than W1's window cap (44,640 s). Whether a 15.6-25 h rehearsal is proportionate to a 12.4 h window is a design question for the window council.
9. **Block-5 heavy-audit tests.**
   - Run `tests/b5_analysis` only on changes to its paths, plus nightly, not on every PR.
   - Answer DLE-2's open point: if the block-6 heavy audit has not finished, is the release held or labelled provisional?
10. **Ownership and blast radius.**
    - Name the owner of each pruning PR. Ranks 1-3 touch the measurement path (the magistrate's lane and the R0 launcher) and should be separate, reviewed PRs, not part of the R1 arm.
    - Before the measurement lane merges back to `main`, name who reviews the R1 lane's changes to `run_night` interrupt and lock semantics. Those paths also run BYTES, HAZARD_PACK and TRANSACTION_PACK nights (R8-1, D8-1).
11. **Item 181's escalation rule.** Narrow "a third consecutive failure of the same check goes to Ed" (`RUN_STATE.md:1566`) to science changes and irreversible data actions. For readiness checks it fired once (item 194), and Ed answered "go" two minutes later.

## 3. Findings

Each finding states what the guard protects, what it has actually caught, what removing or simplifying it would risk, and the recommendation. "Seats" says which seat raised it.

### 3.1 High: costs measurement-Mac hours now

**F1. R0's per-process CPU-contention refusal.** Seats: both (rank 1 in each).
- **Where.** `QuietGuard.check` raises `Refused("contaminating CPU contention")` at `joulewise/align/r0_host.py:270-274@e901eb2a4`. The SMC `CpuQuietProbe` raises `NotQuiet` at `joulewise/align/apple/smc_enumeration.py:213@e901eb2a4`, and the runner turns that into `fail` (exit 3, `r0_host.py:486@5f817856b`). Both judge 0.05 CPU-s/s per contaminant over at least 30 s (`joulewise/prewindow.py:5, 31`; `contention.py:111`). Before #691, `QuietGuard` judged a single `ps` `%CPU` snapshot, about every 15 s (item 189: 101 receipts in 905 s).
- **What it protects.** Nominally, R0's data quality. In practice:
  - The model checks (load, generated, memory, ladder, long-decode) produce token or memory properties that background CPU does not change.
  - The SMC picks are labelled `selection_status: PROVISIONAL` (`r0_host.py:512@e901eb2a4`), and R1 re-selects on its own capture with the same classifier (item 196 (A)).
  - R0 is "a readiness check, not the energy measurement" (item 192, `RUN_STATE.md:1389`).
- **What it caught.** Four stops (R0 attempts 4-7; section 4). None found a defect, and none protected a reported or blinded number.
  - Two were single-snapshot artefacts: the photoanalysisd respawn burst of about 0.6 CPU-s (item 188), and mdworker_shared at a decayed 6.0 % (item 189).
  - Attempt 5 also hit the SMC probe's host-aggregate bar of 0.05, which the idle Mac exceeded in 8 of 12 calls (item 190 :1416). That bar was then made journaled, not judged.
  - Two were scheduled macOS jobs, each over 35.9 s (items 193, 194):
    - softwareupdated at 0.0704 CPU-s/s, with a host aggregate of 0.364;
    - the 00:00 `/tmp` cleaner's `find` at 0.0786.
- **What it cost.**
  - PR #691's build and review rounds, with the Mac idle from 18:05 until the 22:32 re-launch on 11-06. Ed asked why the MBP was idle (item 192 :1387).
  - Two timing-only re-launches.
  - One escalation wait (item 194).
  - The clean-gap scheduling rule, and Ed's visit to change OS settings (items 200-201).
  - Each SMC refusal discarded 1,310-1,520 s of capture, including the whole 900 s load.
- **Risk if simplified.** A heavy, sustained contaminant during the SMC capture could skew a provisional pick. The flag records it, R1 re-selects on its own capture, and R1's ruling-8 rule (0.5 cores sustained for 60 s) is the project's own reviewed bar for the same physics on a heavier step.
- **Recommendation: simplify** (decision 1).
  - Flag CPU contention on every non-SMC check.
  - On SMC, use the ruling-8 rule with one redo, then flag.
  - Keep `r0_host.py:236-268`: the armed window, the loaded night LaunchAgent, the indeterminate LaunchAgent census, the chain or custody census.
  - Then drop the clean-gap rule for R0.
  - Open (both seats): nobody has derived how much contention, for how long and in which phase moves a key's τ or its last-60 s baseline. Until someone does, 0.05 CPU-s/s is a convention.

**F2. The headless launcher cannot run R0-L1's subset or `--keep-going`.** Seat: synthesis (found while checking seat 2's rank 4).
- **Where.** `scripts/launch_align_r0.py:187-202@bd7a3efcd` writes `runner.json` as `[python, align_r0_checks.py, --config, CONFIG, --output, OUT]`. The runner reads its check list and `keep_going` only from argv (`joulewise/align/r0_runner.py:109, 285-293, 330@5f817856b`). `configs/align/v4/r0_desk.json` has no key for either.
- **What it blocks.**
  - R0-L1 (item 196 (2), `RUN_STATE.md:1133`) authorised `--checks host,disk,load,template,generated,memory,ladder,long-decode` "in the next clean gap", on `e1a91226e`, with no new code. That run would have produced the ladder rung.
  - Item 196 (3) then completes R0 by composition with re-run 7's capture, evaluated offline under the amended classifier.
  - `RUN_STATE.md` records no attempt. The later pointers (item 195, 06:20 and 08:45; item 198) schedule a full R0 at 17:15, and the 06:15-11:05 gap was missed (:1246).
  - The record does not say why the subset run was not made. This finding states only that the sanctioned launch path cannot make it.
- **Risk if fixed.** None to data: it is the same runner, and the prerequisite gates still apply under `--keep-going` (`r0_runner.py:238, 293`).
- **Recommendation: fix now** (decision 2). This is gate policy rule 2: CI and a regression test.

**F3. R0 stops at its first failure, and SMC precedes the ladder.** Seats: 2 (rank 4). Corrected in part (section 9).
- `keep_going=False` is the default (`r0_runner.py:109@5f817856b`).
- Since #692 (D3), SMC runs first (`:112`). Before #692 it ran after `memory` (`CHECKS`, `:21`). Either way, `ladder` follows SMC.
- Before #692 an SMC `inconclusive` also stopped R0 (`r0_runner.py:22-23@e1a91226e`). Since #692 only `pass` and `inconclusive` proceed (`:22-26@5f817856b`), so a `NotQuiet` fail still stops it.
- **Caught.** Fail-fast hid each next defect behind the previous one. Attempt 2's load failure hid attempt 3's prompt defect.
- **Derived counterfactual.** Attempts 5-8 passed every non-SMC check they reached (`report.json` of `rerun4` through `rerun7`). With F1 and F3 in place, attempt 5 (17:50 on 11-06) would have run the ladder. This counterfactual is derived from the records, not measured.
- **Recommendation: simplify.** Default `--keep-going` for desk runs, and run the ladder independently of SMC. This depends on F2.

**F4. Full-suite CI as the merge gate on the measurement lane.** Seat: 2 (rank 5).
- "Shard 5 takes about 2-3 h on this lane because of BYTES archive tests" (`RUN_STATE.md:1260`). "Shards take 20 min to 2 h 16 min" (:1424).
- #692's CI ran from about 06:20 to 08:45 on 11-07, and the 06:15-11:05 gap was missed (:1246). The review rounds that ran until 06:20 contributed too.
- No recorded catch on any R0 fix PR.
- **Risk if simplified.** A cross-module break lands on the lane and is caught after the merge.
- **Recommendation: simplify** (decision 5). `scripts/quick_suite.py` already has the touched tier (`:63, :105`).

### 3.2 Medium: costs lead and builder hours

**F5. The W1-under-High-Power host-restore stack.** Seats: both (seat 1 rank 2, "simplify"; seat 2 rank 2, "delete or park").
- **What it is.**
  - A host-level marker and a night lock (flock), with the lock fd inherited through `pass_fds` and retaken before any restore.
  - Proofs that the chain's process group and the driver's descendants have terminated.
  - `_CHAIN_TERMINATION_UNPROVEN`, which defers the close on any unproven termination.
  - A latched signal handler and a 10 s close deferral, with the runtime watchdog armed on the first held signal.
  - Dead-man, J4 and session-start restores.
  - A fixed production host-state directory, with `HostStateOverrideRefused`.
  - A launchd census in `install`.
- **The rulings behind it.** R5-6, R6-7, R7-4 to R7-8, R7-10, R7-11, R7-14, R8-1 to R8-3, R8-5 and D8-1, D8-2, D8-4, D8-5: 18 of LEAD-RULINGS-2's 48.
  - R7-9 is a doc correction to the window comparison, and R8-4 and D8-3 are worst-case arithmetic; none is counted here.
  - R8-1's chain termination on interrupt is counted, though it also closes a general supervision gap.
- **Size.**
  - About 1,300-1,500 production lines, not all of them High Power: `powermode.py` 515, the `run_night.py` delta over `main` 555 (5,797 against 5,242), `align_v4_session.py` 357, and the driver's `_descendants`/`_stop_tree`/`_terminate`/`PowerModeGuard` block at `align_r1_rehearsal.py:215-495`.
  - About 2,300 test lines in modules named for it: `test_r1_round6_power` 409, `round7_power` 550, `round7_install` 149, `round7_close_deferral` 107, `round8` 609, `round8_exec_review` 324, `test_v4_powermode_record` 138.
- **What it protects.**
  - The host left in AC powermode 2 after a crashed W1 High Power night. Without the stack, the next admission already refuses on the observed mode and needs one `sudo -n pmset -c powermode 0` (R5-6, LEAD-RULINGS-2 :93).
  - No restore under a surviving chain. A night whose chain survives is already aborted: "No data is admitted in that case" (R8-2, :516-520).
  - The R1 chain's zsh EXIT trap runs `pmset 0` "without lock or proof, overriding an R8-1 deferral" anyway (D8-4, :659-663).
- **What it caught.** Only desk findings on its own previous rounds.
  - After round 5, 10 of the 11 HIGH/MEDIUM findings are High Power, signal or lock findings. The one exception is round-6 cold MEDIUM-1 (U5 predecessors). This was verified on the round-6 to round-8 review documents.
  - Round-7 exec MEDIUM-1 and round-8 exec MEDIUM-1 were regressions introduced by the previous fix.
  - The reviewers: "Neither can admit bad data" (`2026-11-07-r1-round7-executing-review.md:11`). "Neither can admit bad data, and neither is on the ALIGN W1 or R1 path as wired today" (`…round8-executing-review.md:13`).
  - Nothing has fired in the field: R1 has not run.
- **What it costs beyond code.**
  - Four rulings rounds.
  - Changed interrupt semantics in the shared `run_night`. R8-1 "covers the HAZARD_PACK chain too". One round-8 fix briefly made a TRANSACTION_PACK night unstoppable by signals, which D8-1 then repaired.
- **Adoption is uncertain.** High Power is adopted only if t_decline(B) ≥ 1.25 × max(A1, A2) (`pilot_protocol_v4.md:625`), on n = 1 per condition (`CHAIR.md:322`).
- **Recommendation: freeze now; cut after R1** (decision 3).
  - Do not delete before R1. The R1 driver's `PowerModeGuard` runs the A-B-A's High Power leg, and an arm-path PR on the eve of R1 risks more than it saves.
  - After R1, if High Power is not adopted or the lead rules W1 Automatic, delete the W1 High Power arming path.
  - If it is adopted, simplify to: the `sudo -n -l` rule check; the marker written before `pmset 2`; restore in `finally` with the R7-7 read-back; the admission read-back refusal; session-start restore of a leftover marker; and R8-1's group termination on interrupt.
  - Delete: `HostLock` and `pass_fds`, retake-before-restore, the descendant census, `_CHAIN_TERMINATION_UNPROVEN` and its defer branches, the 10 s deferral and its watchdog coupling, and `HostStateOverrideRefused` marking.
  - Keep R8-2's paragraph as the documented limit.

**F6. Review rounds on code that has never run on hardware, and the gate policy as applied.** Seats: both.
- **Volume.**
  - 120 commits on the R1 lane over `5f817856b`, from 11-05 16:42 to 11-07 10:35: 6 on 11-05, 77 on 11-06, 37 on 11-07.
  - 29,529 lines added: 11,188 tests, 7,504 docs, the rest code and configs.
  - 21 review documents dated 11-05 to 11-07 (3,786 lines). Eleven of them are R1 integration or round reviews (2,070 lines), from 11-06 11:46 to 11-07 07:51.
  - A 1,399-line integration report, and 48 rulings across rounds 5-9.
- **Yield.**
  - Rounds 4-5 found real number-bearing defects: U5 and β_T contamination, a turnless replay passing U5 falsely, and an uninformative duty bar.
  - After round 5 the findings are almost all High Power (F5).
  - The lead's summary of the round-5 cold pass was "R1 can be armed" (item 191, `RUN_STATE.md:1400`). The cold pass's own verdict was "no BLOCKER, no HIGH. Three MEDIUM, six LOW".
  - Seat 2 reports that the pre-R0 reviews (WP7, WP8) foresaw none of R0's 8 field failures, and one adjacent. The synthesis seat did not re-tally that.
  - R5-5 did foresee the 100 ms coverage tolerance (LEAD-RULINGS-2 :74, written about 19:49 on 11-06). It was dispositioned "fails closed", and R0 hit it at attempt 8 on another lane.
- **The policy as written.**
  - Rule 2: tooling and orchestration that cannot change a number get "CI and the change's own regression test. One reviewer only if the author asks" (`gate_policy.md:26-27`).
  - Rule 3 covers number-bearing code and the agent census, stand-down and arm checks: two executing reviews launched together, which "count as both the independent review and any cold pass" (:28-34).
- **The policy as applied.**
  - #684, a one-line launcher fix, got a Sonnet executing review and CI (item 178, `RUN_STATE.md:1593`).
  - #687, a prompt string, got a Sol executing review, a Fable cold pass with a live model run, and about 2.5 h of CI (item 186).
  - #691 went through several build rounds plus executing reviews, cold passes and a Sol critique (items 189-192).
  - Each R1 round added an executing review, a cold pass and Sol critiques.
- **Rule 9's tally** (`:46-47`) appears in `.codex-report/RC-CMP-5.md:154` and `RC-CMP-6.md:121`. It appears in no R0 or R1 record, review document or `RUN_STATE.md` item.
- **Recommendation: simplify** (decision 4). R0 blocked R1 throughout, so these rounds did not delay a measurement, but they occupied the lead and the builders for most of 11-06 and 11-07.

**F7. The ruling 1(f) refusal is expected to fire, and then to be overruled.** Seat: 1 (rank 3).
- "1(f) will likely refuse W1 … until the lead rules on the ruling 1(e) fallback (R6-3: no code fallback)" (LEAD-RULINGS-2 :363).
- "Ruling 1(f) likely refusing W1 at about 20 tok/s is expected: the 1(e) fallback is ruled by the lead after the R1 night, on its numbers" (R8-8, :593). Item 202 (7) repeats this.
- The fallback order is already named: S6 joint tuning with δ_slow ≤ 2.0 °C, then idle 450 s after D, then 4-bit, then screen-only (`pilot_protocol_v4.md:610`).
- **Protects.** A worst-case D member fitting inside T_dead. That is a real bound: a member cut at 1,800 s loses its bundle.
- **Risk.** A mechanical fallback would apply a design change (4-bit, screen-only) without a look. Steps 1-2 are tuning; steps 3-4 change what W1 measures.
- **Recommendation** (decision 6): either encode steps 1-2 as mechanical and keep 3-4 as lead steps, or keep the ruling post-R1 and book the lead's time for it. Keep the G0_cap_W1 derivation; it is physics from re-run 7.

**F8. Any INCONCLUSIVE calibration segment refuses W1.** Seats: both (seat 1 rank 10, seat 2 rank 6).
- `align_v4_kit.py:194-208@e901eb2a4`. The remedy named in the refusal is a full R1 re-run.
- G0 settling at 840-1,040 s against the old 600 s cap (LEAD-RULINGS-2 :319) makes a timeout plausible. R7-2 raised R1's cap to 1,200 s.
- **Risk.** U5 and β_T from two points instead of three.
- **Recommendation: simplify** (decision 7). Step-d stays a refusal.

**F9. The R1 worst-case table is re-derived every round, and R1 is now longer than W1.** Seats: both.
- The no-redo case went 44,487 → 46,887 → 54,343 → 56,207 s across R6-8, R7-2, R8-4 and D8-3 (:345-361, :632-657). Every R6-2 retry plus the batch wait is 90,663 s. Item 202 already accepts a cut beyond that.
- W1's `window_cap_s` (44,640 s) is 11,567 s below R1's no-redo case (D8-3).
- **Recommendation** (decision 8): one constant of 90,663 s or more; keep the batch-window wait (`:980`), which waits rather than refuses.

**F10. The doctrine is not mechanised for ALIGN, and the shared code has a blast radius.** Seats: both.
- `configs/gates/hazard_refusals.json:12` carries "physics refuses; everything else is a flag" (Ed, 2026-10-05), and D-161 (`docs/decision_log.md:207`) carries the threat-model prune.
- The refusal census scans 123 modules at `e901eb2a4`. From `joulewise/align` only `apple/powermode.py` is in scope; three other align modules are listed as `not_scanned` with reasons. `r0_host.py`, `smc_enumeration.py`, `align_r1_rehearsal.py` and `align_v4_kit.py` are outside the scan. That is how R0's contention refusals were added without a doctrine check.
- **Recommendation.** Before the measurement lane merges to `main`, either extend the census to the R0/R1 entry points or record the doctrine as a review question for refusals on those paths. Review the `run_night` interrupt changes for non-ALIGN nights (decision 10).

**F11. Item 181's third-failure escalation.** Seat: 1 (rank 8).
- `RUN_STATE.md:1566`. It fired once on R0 contention: mail at 00:06, Ed's "go" at 00:08 (item 194).
- It carries no decision content for readiness checks (decision 11).

### 3.3 Low: mass and legibility

**F12. The heavy L9 audit's tests on every PR.** Seat: 2 (rank 10).
- `tests/b5_analysis` holds 41,734 lines and 1,707 tests.
- In `scripts/test_timings.json@bd7a3efcd` (hosted medians, recorded 10-05 and updated 10-30) they weigh 62.6 CPU-minutes: 22.7 % of the 276 non-exclusive minutes, or 20.8 % if the two exclusive modules are counted.
- Under DLE-2 the heavy pipeline is a once-per-block audit, off the critical path (`DEVIATION-LOG.md:155-156`), while "engineering-only speedups … continue on `lane/2026-11-06-b5-under-90`" (:200-212).
- **Recommendation** (decision 9): run them on a path filter plus nightly; stop the speedup work; freeze at `b5/analysis-r3`.

**F13. `artifact_schema_invalid` collapses binding causes.** Seat: 1 (rank 11).
- Only ten floor-binding reason codes are surfaced (`inputs.py:594-626` per the trace). Every other binding problem becomes the bare word, which is what held D5 (`2026-11-07-b5-release-hold-trace.md:61-71`).
- **Recommendation.** Surface every binding reason code, but only after D5 is decided, or as part of D5's fix if that touches the same code. It is number-bearing L9 code under a release hold, so it takes rule 3's gates and a cited rebind.

**F14. Test modules named for review rounds.** Seats: both. Consolidate them by subject when they are next touched.
- ALIGN: `tests/align/test_r1_round5_exec_review` to `test_r1_round8_exec_review`, about 3,450 lines.
- Block 5: `test_rc_cmp7` to `test_rc_cmp11`, `test_round3`, `test_review_fixes`, `test_auditfix`, `test_vdl_sol_hunt*`.

**F15. The D-188 equivalence comparator** (`tools/b5_equivalence/compare_b5_results.py`, 2,145 lines; `test_result_equivalence.py`, 1,914 lines). Seats: both.
- It found r2 EQUIVALENT to r1 on real data (item 196) and the composite-digest difference that #643 fixed (item 165).
- Retire it at the block-5 release (care audit row 17).

**F16. `run_b5_analysis.py --mode release` and the release-mode half of `dry_run.py`.** Seats: both. They differ on timing.
- **Where.**
  - `run_b5_analysis.py:100`.
  - In `dry_run.py`: `release_difference` :177, `require_release_equality` :206, `_released_input_difference` :1792, and the mode branches at :368 and :2273-2278.
  - `tests/b5_analysis/test_release_equality.py`.
  - Possibly `resume.py` (501 lines; seat 2).
- **Status.** `CANONICAL.md:47` lists `--mode release` as replaced by DLE-1's `release_b5.py`, calling it "now optional audit work". `release_b5.py` imports no repository code (:4).
- **Recommendation.** Delete in the post-release prune (item 201, phase 2), not during the D5 hold.

**F17. The R0 launch ceremony.** Seat: 2 (rank 13).
- The steps: a manual fast-forward, the desk-fence tests, hw.model, venv, Spotlight STOP/CONT, preflight, battery float and stopping the Codex adapter (items 194, 195).
- Spotlight STOP/CONT is now a no-op, because indexing is off (item 201).
- Fold the checks into `launch_align_r0.py preflight`, together with F2.

### 3.4 Keep, with the evidence that earned it

- **Block-5 release comparator and bars** (`scripts/release_b5.py`, bars pinned at :58; `compare_b5_recompute.py`).
  - It caught D1 in L9: the code read `battery_available` where the record has `battery_term_available`, and a fixture with the same wrong key hid it. The key is now corrected at `disclosures.py:696@bd7a3efcd`.
  - It caught D2-D4 in the recompute and D6 in the comparator mapping, all before unblinding (trace §0).
- **The refusal registry**: 196 tooling codes and 2 outcome codes, of which 22 are named in `RUN_STATE.md`, `docs/run_reports` or `docs/analysis/b5`. A mention is not a firing. It has no runtime cost. Do not prune codes that have never fired.
- **Agent and occupancy censuses.** Items 158, 67 and 78 recorded refused or aborted windows, and item 177 caught an orphan Codex daemon before R0.
- **Battery float.**
- **R0's model-load, load-reference, generated and classifier verdicts.**
  - The classifier's placeholder rejection came from #692's redesign. That redesign followed two reviewers re-ranking the journal of an inconclusive run (item 195), not a refusal.
- **R1:**
  - alias groups: TCMb and TVD0 were identical in re-run 7;
  - the precool/retry/INCONCLUSIVE design;
  - the soak-reference consume check;
  - the batch-window wait;
  - the external-volume census;
  - kit `--check`;
  - the WP18 fixtures. Their tool refused once, on its own defect (item 194).
- **The R9-2 kit re-derivation and the lead's changed-pick receipt, both unchanged** (section 8, item 4).
- **Block 5:** blinding layers, seal pins, the step-0 census, the lean recompute, and the float-token scan in `release_b5.py`.

## 4. Case study: R0, eight stops and no pass

Sources: `RUN_STATE.md@bd7a3efcd` items 178-202, and each attempt's `report.json` on `records/2026-11-0{6,7}-align-r0-v4*`. Start times come from the records' UTC stamps, converted to PST.

| # | Record (`docs/align/r0/…`) | Start (PST) | Ran (s) | Stopped at | Cause | Class |
|--:|---|---|--:|---|---|---|
| 1 | `2026-11-06` | 11-06 ~08:05 | 21 | `model-load` fail | the launcher resolved `--python-bin` through the venv symlink to bare Homebrew Python, which has no mlx (item 178) | launcher bug |
| 2 | `2026-11-06-rerun` | 09:03 | 76 | `load` fail | an absolute NLL bar of 3.0 is invalid for D; upstream HF fp32 also scores 11.06 (items 182, 184) | R0 check defect |
| 3 | `2026-11-06-rerun2` | 14:34 | 160 | `generated` inconclusive | the echo prompt stated 6 calls where 16 were needed (item 186) | R0 harness defect |
| 4 | `2026-11-07-rerun3` | 17:33 | 158 | `generated` refused | a photoanalysisd respawn burst (about 0.6 CPU-s) read as 34 % on one `ps` snapshot (item 188) | contention: snapshot artefact |
| 5 | `2026-11-07-rerun4` | 17:50 | 905 | `smc` refused | mdworker_shared at a decayed 6.0 %; also the SMC probe's host-aggregate 0.05 bar, 0.035-0.112 on the idle Mac (items 189, 190) | contention: snapshot artefact and an unpassable bar |
| 6 | `2026-11-07-rerun5` | 22:32 | 2,246 | `smc` fail (`NotQuiet`) after 1,310 s | the softwareupdated 23:09 scan at 0.0704 CPU-s/s over 35.9 s (item 193) | contention: scheduled OS job |
| 7 | `2026-11-07-rerun6` | 23:18 | 2,470 | `smc` fail (`NotQuiet`) after 1,520 s | the 00:00 `/tmp` cleaner's `find` at 0.0786 CPU-s/s (item 194) | contention: scheduled OS job |
| 8 | `2026-11-07-rerun7` | 11-07 00:11 | 2,789 | `smc` inconclusive | `thermal.Coverage`'s 100 ms tolerance, "no derivation", discarded about half the reads (item 195) | R0 check defect |

**Totals.**
- 8,824 s of R0 execution (the sum of `total_seconds`; 2 h 27 min) over about 33 h, from about 08:05 on 11-06 to the planned 17:15 on 11-07. The Mac was doing R0 about 7 % of that time.
- No attempt reached `ladder` or `long-decode`.

**What the stops found.**
- *Defects in our code (attempts 1, 2, 3, 8).*
  - Real, and the cheapest checks found them.
  - Three were R0's own checks being wrong (2, 3, 8). Each cost a fix lane with 2-3 model seats and 1-2.5 h of CI.
  - Attempt 8's constant had "no derivation". The 10-17 charge forbids exactly that: "no silly numbers" (`docs/process_traces/2026-10-17-magistrate-52d50d1f/reg-gate-charge.md:27`, per seat 1).
- *Contention (attempts 4-7).* No defect. Section 3.1, F1.
- *The science catch.* With the coverage fixed, attempt 8's picks were power-gated `Tg*` placeholders on an unsettled baseline. Two reviewers found that by re-executing the journal (item 195, Opus HIGH and Fable F1).
  - The seats framed this differently: seat 2 credits the classifier's verdict, seat 1 credits reading.
  - The record supports seat 1. The `inconclusive` came from the coverage bug, and merging only the coverage fix "would turn a wrong-reason inconclusive into a pass with physically wrong picks" (item 195).
  - The classifier now rejects placeholders (#692 D1), so it is worth keeping (section 3.4).

**What R1 would have done with the same contention.** Ruling 8 redoes a segment on more than 0.5 cores sustained for 60 s.
- Attempt 4: a burst of about 0.6 CPU-s.
- Attempt 5: mdworker at a decayed 6 %, with host aggregates up to 0.112.
- Attempt 6: 0.07 per process, with a 35.9 s host aggregate of 0.364.
- Attempt 7: 0.079 per process.
- None reaches 0.5 cores for 60 s, so none would have triggered R1's redo. (Item 202 (4) still asks the magistrate to confirm this from the code, including `run_night`'s path; see the caveat in section 1, item 4.)

## 5. Which refusals fired in practice

| Subsystem | Fired | Protected a reported number or the blinding |
|---|---|---|
| R0 (8 attempts) | 4 contention refusals; 3 R0 check or harness defects; 1 launcher bug | 0 |
| R0 escalation rule (item 181) | once (item 194); Ed answered "go" in 2 min | 0 |
| R1 driver, runtime and High Power stack | 0: never run on hardware. `night_refused_ac_powermode` and `night_refused_host_lock_error` appear in no record | n/a |
| v4 kit `--check` | blocks by design on `R0.reasoning_effort` and the four R1 leaves (item 202 (2)) | n/a (by design) |
| WP18 fixture tool | once, on its own seed-index defect (item 194) | the refusal was a bug; the fixtures it binds are registered input |
| Block-5 dry runs | tooling refusals and incidents in attempts A-E and dry-h to dry-k (care audit row 22; items 95, 103, 108-109, 165) | a step-0 blinding false positive (attempt A), on the safe side |
| Block-5 release check (dry-j) | comparator hold: 1,001 rows in 11 families, 6 defects | **yes**: D1 (L9), D2-D4 (recompute), D6 (comparator) |

## 6. Ranked prune list

Ranked by Mac hours or lead/builder hours returned per unit of protection given up. No row touches blinding or a preregistered estimator.

| Rank | Prune | Returns | Gives up | Seats | Decision |
|--:|---|---|---|---|---|
| 1 | R0 CPU contention becomes a flag; SMC uses ruling 8's redo once (`r0_host.py:270-274`; `smc_enumeration.py:213`) | attempts 4-7 class: re-launches, PR-round idle, escalations | nothing reported; contamination is recorded, and R1 re-selects | both | 1 |
| 2 | The launcher passes `--checks` and `--keep-going`; desk runs default to keep-going (`launch_align_r0.py:201-202`; `r0_runner.py:109`) | R0-L1 becomes runnable; one slot surfaces all defects | minutes of a later check on a stack with a known failure | synthesis + 2 | 2 |
| 3 | Freeze the High Power stack now; after R1, delete the W1 path (not adopted / Automatic) or simplify it (adopted) | about 1,300-1,500 code and about 2,300 test lines; the stream that produced 10 of 11 late findings | automatic restore after a SIGKILL (one manual `pmset` line, fail-closed) | both | 3 |
| 4 | Gate policy as written; no desk round after one number-bearing round until a hardware run; Sol advisory | about half the lead/builder hours per round | some LOW findings reach hardware first | both | 4 |
| 5 | Measurement-lane merge gate: touched tier + `tests/align`; full suite post-merge | 1-3 h per PR on the lane | a cross-module break caught post-merge | 2 | 5 |
| 6 | 1(f): pre-commit mechanical fallback steps 1-2, or schedule the lead step | one post-R1 round-trip | nothing; the step taken is recorded | 1 | 6 |
| 7 | A designed-start INCONCLUSIVE becomes U5 INCONCLUSIVE (or a patch night), not a W1 refusal | a second 15-25 h R1 night | β_T on two points, recorded | both | 7 |
| 8 | One `window_max_s` constant (90,663 s or more); stop per-round tables | a ruling, a build and a test per round | a tighter bound | both | 8 |
| 9 | `tests/b5_analysis` on a path filter plus nightly; stop heavy-pipeline speedups | about 21-23 % of CI CPU on every PR | audit drift caught nightly, not per PR | 2 | 9 |
| 10 | Narrow item 181's third-failure rule to science changes | one Ed wait per occurrence | nothing | 1 | 11 |
| 11 | Fold the R0 launch ceremony into `launch_align_r0.py preflight` | magistrate tokens and hand steps | nothing | 2 | with 2 |
| 12 | Surface every floor-binding reason code behind `artifact_schema_invalid` (after D5) | a blind trace round per firing | nothing | 1 | engineering |
| 13 | Consolidate round-named test modules by subject, when touched | legibility; some CI time | duplicate pins, kept once | both | engineering |
| 14 | Retire `tools/b5_equivalence` at the block-5 release | 2,145 + 1,914 lines | nothing after the release | both | engineering |
| 15 | Delete `--mode release`, the release-mode half of `dry_run.py` and `test_release_equality.py` (and `--resume`, if unused) in the post-release prune | dead paths in a 2,301-line driver | nothing; DLE-1 replaced it | both (timing differed) | engineering |
| — | **Not pruned:** the kit's R9-2 re-derivation and the lead's changed-pick receipt (section 8, item 4) | — | — | split | — |

## 7. Measurements

Lines counted with `wc -l` at the named heads. The two seats used different subsystem boundaries; both are given where they differ.

| Subsystem | Code (lines) | Tests (lines) | Notes |
|---|---:|---:|---|
| R0 desk: `joulewise/align/r0*.py`, `smc_enumeration.py`, `scripts/align_r0_checks.py`, `scripts/align_smc_enumerate.py` @`e901eb2a4` | 3,175 | 4,636 (18 modules) | seat 1's wider boundary (+ `thermal.py`, `prewindow.py`, `contention.py`): 4,569 code, about 5,100 tests |
| R1 runtime and driver: `r1_runtime*.py`, `align_r1_runtime.py`, `align_r1_rehearsal.py`, R1 chain | 4,271 | — | `align_r1_rehearsal.py` has 81 refusal sites (seat 1) |
| v4 kit `align_v4_kit.py` | 1,340 | `test_v4_kit` 1,772 | |
| High Power and host state | about 1,300-1,500 | about 2,300 in named modules | F5 |
| `run_night.py` | 5,797 (`main`: 5,242) | — | shared by every campaign |
| Round-named ALIGN tests (`test_r1_round*`) | — | about 3,450 (11 modules) | 3,758 including `test_pilot2_round1` |
| All `tests/align` @`e901eb2a4` | — | 52,426 | |
| R1 lane over `5f817856b` | +29,529 lines (11,188 tests, 7,504 docs) | | 120 commits |
| Block-5 `joulewise/b5_analysis/**` @`bd7a3efcd` | 9,385 | `tests/b5_analysis` 41,734 | `dry_run.py` 2,301; `resume.py` 501 |
| `release_b5.py` / `independent_recompute_b5.py` / `compare_b5_recompute.py` / `compare_b5_results.py` | 506 / 3,255 / 4,105 / 2,145 | `tests/independent_recompute` 9,687 (seat 1) | |
| Block-5 total (seat 1) | 19,537 | 67,161 (2,814 tests) | ratio 3.4 : 1 |
| LEAD-RULINGS-2 | 734 lines, 48 rulings | | |

## 8. Where the seats disagreed, and the ruling

1. **R0 stop classes.**
   - Seat 1: 1 launcher bug, 3 check defects, 4 contention refusals.
   - Seat 2: 3 real defects, 2 miscalibrated guards, 3 immaterial contention.
   - The difference is labelling. Seat 2 splits attempt 5 into its per-process part and the aggregate bar, and calls the NLL bar a "miscalibrated guard" where seat 1 calls it a "check defect".
   - **Ruling:** 1 launcher bug, 3 R0 check or harness defects, 4 contention refusals. Attempt 5 also exposed an unpassable aggregate bar.
2. **Attempt 8: a correct refusal or a bug?**
   - Seat 2: "correct and valuable". Seat 1: "check defect (underived constant)".
   - **Ruling: seat 1**, with seat 2's point kept. The stop was the coverage bug. The placeholder catch came from reviewers re-executing the journal (item 195). The classifier that now rejects placeholders is worth keeping.
3. **The High Power stack.**
   - Seat 1: simplify now to a keep-list. Seat 2: delete or park, or rule W1 Automatic.
   - **Ruling:** freeze now and cut after R1 (F5). Seat 2 is right that the cut should wait on the A-B-A or a ruling. Seat 1's keep-list is the target if High Power is adopted.
   - Deleting before R1 is rejected: the R1 driver's `PowerModeGuard` runs the A-B-A's High Power leg, and an arm-path PR on the eve of R1 would need the same review rounds this audit wants to stop.
   - R8-1's group termination on interrupt stays in every outcome (seat 2), because it closes an unsupervised-chain gap for all nights.
4. **The kit's changed-pick checks.**
   - Seat 1: delete the lead's `thermometry.lead_verification` receipt (`align_v4_kit.py:262-267`) as redundant with R9-2.
   - Seat 2: drop R9-2's re-derivation and keep the schema and `rule` checks.
   - **Ruling: neither.**
     - R9-2 re-derives `band_c` and `S7` from the *recorded* `noise_c` and `recovery_s` with the runtime's functions (LEAD-RULINGS-2 :705-728). That is an arithmetic consistency check, not a re-derivation from the journal. So the receipt, a judgment that the changed picks are physically sensible, is not redundant.
     - R9-2 costs no runtime and is built and tested.
     - The receipt costs one line, in a sitting the lead already has after R1 (the 1(e) ruling and the R1 leaves).
     - Changing either would cost an arm-path PR and save no hours.
5. **When to delete `--mode release`.**
   - Seat 1: now. Seat 2: at the block-6 boundary.
   - **Ruling:** in the post-release prune. Not during the D5 hold: the heavy pipeline is the audit, and churn in `dry_run.py` under a hold adds review for no gain.
6. **SMC under contention.**
   - Seat 1: flag. Seat 2: R1's ruling-8 redo, or flag.
   - **Ruling:** ruling 8 with one redo, then flag. It keeps one reviewed rule across R0 and R1, and it would not have fired on any recorded R0 refusal.
7. **Review-round counts.**
   - Seat 1: six rounds in about 36 h. Seat 2: 9 rounds in about 31 h.
   - Both depend on where counting starts. Section 3.2, F6, replaces them with commit and document timestamps.

## 9. Claims corrected or dropped

**Corrected.**
- **Seat 2's "191 registered tooling codes".** The registry holds 196 tooling codes and 2 outcome codes (`configs/analysis/b5/dry_run_refusal_classes.json`). Seat 1's count of 22 codes named in records was reproduced exactly.
- **Seat 2: rule 9's tally "appears in no session record".** It appears in `.codex-report/RC-CMP-5.md:154` and `RC-CMP-6.md:121`, and in none of the ALIGN records.
- **Seat 1: L9's wrong key "at `disclosures.py:696@bd7a3efcd`".** On `bd7a3efcd` that line already reads `battery_term_available`, and the fixture is corrected. The wrong key was the state of the traced commit.
- **Seat 1's "21 review documents".** The count is right, but only 11 of the 21 are R1 reviews (2,070 lines). The rest are R0 and WP reviews.
- **Seat 1: "the round-5 cold pass already said 'R1 can be armed'".** That is the lead's summary in item 191 (`RUN_STATE.md:1400`). The cold pass's verdict was "no BLOCKER, no HIGH. Three MEDIUM, six LOW".
- **Seat 2's "SMC-first ordering" as the reason the ladder never ran.** SMC-first exists only since #692 (`5f817856b`). Attempts 1-8 ran SMC after `memory`, and the ladder followed SMC in both orders. Before #692 an SMC `inconclusive` also stopped R0.
- **Seat 2's "22.7 % of CI".** Correct against the 276 non-exclusive CPU-minutes. With the two exclusive modules it is 20.8 % of 301 minutes. The timings are hosted medians from 10-05 and 10-30.
- **Start times.** Seat 1's 23:20 and 00:15 are the items' approximate launch times. The records give 23:18:54 and 00:11:31 PST. R0 Mac time is 8,824 s (seat 1), not 8,825 s (seat 2's rounding).
- **Seat 2's "15 of 28 unique HIGH/MEDIUM findings" (rounds 4-8).** Rounds 6-8 were verified: 10 of the 11 findings after round 5 are High Power, signal or lock findings. Rounds 4-5 were not re-tallied, so the 15/28 figure is seat 2's.

**Dropped as not verified by the synthesis seat** (each remains in the appendices):
- **Test wall times.** Seat 1's live tails, and seat 2's 747 s total and per-module times. The synthesis seat ran no tests. Seat 2's timing table was in a session scratchpad, not a durable path.
- **Seat 2's import closure** of about 180 files and 220k lines, and its 38 MB of fixtures.
- **Seat 2's counterfactual** "15-20 h of Mac idle avoidable". Section 4 gives a narrower counterfactual derived from the records.
- **Seat 1's physics estimate** that 7 % of a core for half a minute is "a few tens of joules against … tens of kilojoules" and "does not move a heatsink key's tau". No derivation is on record. It stays an open question (F1).
- **Exact build and review counts for #691** (seat 2: 3 Sol builds, 2 Opus, 3 Fable). These were not re-counted; items 189-192 are cited instead.
- **Seat 2's pre-R0 "0 of 8 foreseen".** It was not re-tallied, and it is attributed to seat 2 where it is used.

## 10. Evidence index

All repo paths are at the named commits.

- **`RUN_STATE.md@bd7a3efcd`.**
  - Items 202 (:1045), 201 (:1069), 200 (:1084), 199 (:1095), 198 (:1101) and 197 (:1113; r3 dry run 1 h 40 min at :1124).
  - Item 196 (:1130; R0-L1 (2) at :1133). Item 195 (:1154; gap missed at :1246; CI at :1260).
  - Items 194 (:1280), 193 (:1326), 192 (:1355; idle at :1387; "readiness check" at :1389), 191 (:1395; "can be armed" at :1400) and 190 (:1411; aggregate at :1416; shards at :1424).
  - Items 189 (:1444), 188 (:1458), 186 (:1486), 182 (:1548), 181 (:1558; third-failure rule at :1566) and 178 (:1591; #684 at :1593).
- **R0 records.** `records/2026-11-06-align-r0-v4`, `-rerun` and `-rerun2`, and `records/2026-11-07-align-r0-v4-rerun3` to `-rerun7`: `docs/align/r0/*/report.json` (`status`, `stopped_after`, `total_seconds`, `checks[].status`).
- **`e901eb2a4` code.**
  - `joulewise/align/r0_host.py:236-274` (refusals at :238, :268, :274) and :512 (`PROVISIONAL`).
  - `joulewise/align/apple/smc_enumeration.py:83-213` (`NotQuiet` at :213).
  - `joulewise/prewindow.py:5, 31`; `joulewise/hazards/contention.py:111`.
  - `scripts/align_r1_rehearsal.py:157-159, 215-495, 872-873, 980, 1064, 1107, 1314`.
  - `scripts/align_v4_kit.py:170-176, 179-306 (194-208, 262-267), 355, 469, 527`.
  - `joulewise/align/apple/r1_runtime.py:280-290` (`classify_step` calls `rank` only).
- **`5f817856b` and `e1a91226e` code.** `joulewise/align/r0_runner.py:21-26, 109, 112, 185, 238, 261, 285-293, 330@5f817856b`; `r0_runner.py:21-23@e1a91226e`; `r0_host.py:486, 491@5f817856b`.
- **`main@bd7a3efcd`.**
  - `scripts/launch_align_r0.py:187-202, 249-279`; `scripts/quick_suite.py:63, 105`; `scripts/test_timings.json`.
  - `docs/process/gate_policy.md:26-34, 46-47`; `CANONICAL.md:1-6, 47`.
  - `docs/analysis/b5/DEVIATION-LOG.md:150-212`; `docs/run_reports/2026-11-07-b5-release-hold-trace.md:1-36, 61-71`; `docs/decision_log.md:207`.
  - `scripts/run_b5_analysis.py:100`; `joulewise/b5_analysis/dry_run.py:177, 206, 368, 1792, 2273-2278`; `joulewise/b5_analysis/disclosures.py:696`.
  - `scripts/release_b5.py:4, 58`; `configs/analysis/b5/dry_run_refusal_classes.json`; `.codex-report/RC-CMP-5.md:154`, `RC-CMP-6.md:121`.
- **Docs at `e901eb2a4`.**
  - `docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-2.md`: R5-5 :74; R5-6 :81-93; R6-3 :199-209; R6-7 :236-264; physics input :319; R7-2 :341-365; R7-4 to R7-14 :375-469; R8-1 :489-512; R8-2 :516-520; R8-8 :591-593; D8-1 :605; D8-2 :613; D8-3 :632-657; D8-4 :659-663; R9-2 :705-728.
  - `docs/align/council-2026-11-06-v4-review/CHAIR.md:322`; `docs/align/pilot_protocol_v4.md:3, 610, 625`.
  - `docs/align/reviews/2026-11-06-r1-round5-cold-pass.md:3`; `2026-11-07-r1-round6-*`; `2026-11-07-r1-round7-executing-review.md:7-13`; `2026-11-07-r1-round8-executing-review.md:13-16`.
  - `configs/gates/hazard_refusals.json:12` and `scan` (`not_scanned`).
- **Seat 1's durable copy.** `docs/run_reports/2026-11-07-proportionality-prune-audit-fable.md` on `audit/2026-11-07-proportionality-prune-fable` (`0e06755ef`).

No external sources were used.

---

## Appendix A: seat 1 report (Fable 5.1), verbatim

The seat's TOP and OPEN lists and its report follow exactly as delivered to the synthesis. The headings below this line are the seat's own.

**TOP**

["R0 has stopped 8 times in 8 runs with no pass (RUN_STATE items 178-202 @bd7a3efcd): 3 stops were defects in R0's own checks, 1 a launcher bug, 4 were quiet-guard contention refusals (2 on single-snapshot %CPU artefacts, 2 on scheduled macOS jobs at ~0.07 CPU-s/s for 36 s). Total R0 Mac time 8,824 s (2.5 h) over ~33 h elapsed (~7 % utilisation). No stop found a hardware, artifact or sensor fault; the one science catch (placeholder sensor picks) came from reviewers reading an inconclusive run's journal. Under Ed's codified doctrine 'physics refuses; everything else is a flag' (configs/gates/hazard_refusals.json:12), R0's CPU-contention refusals (r0_host.py:270-275, smc_enumeration.py:213 @e901eb2a4) should be flags. Rank-1 prune.","About a third of the 48 R1 rulings in LEAD-RULINGS-2 (R5-6, R6-7, R7-4..R7-11, R7-14, R8-1..R8-3, D8-1, D8-2, D8-4, D8-5) build a High Power restore mechanism (host marker, flock via pass_fds, retake-before-restore, process-tree termination proofs, signal latching, 10 s deferral). Its marginal protection over marker + finally-restore + admission read-back refusal is operator convenience, not data: R8-2 records no data is admitted in the uncovered case and D8-4 records the R1 chain's zsh trap runs pmset 0 without lock anyway. ~1,500 code + ~2,000 test lines, four review rounds, for a mode whose W1 adoption is still conditional on R1's A-B-A legs. Rank-2 prune: simplify.","The kit's ruling 1(f) refusal (align_v4_kit.py:469-537 @e901eb2a4) is a gate its own builders expect to fail: R7-2 and R8-8 record that at ~20 tok/s it will refuse W1 even at the B_D floor until the lead rules on the 1(e) fallback. A refusal scheduled to be overruled is a round-trip, not protection. Pre-rule 1(e) now (blind by construction) and make 1(f) a recorded fit.","The Block-5 release comparator (scripts/release_b5.py, compare_b5_recompute.py, 1e-6 bars pinned at release_b5.py:58 @bd7a3efcd) earned its cost: on dry-j it held with 1,001 failing rows in 11 families, traced blind to six defects, one in L9 (disclosures.py:696 wrong key, hidden by a fixture with the same wrong key), three in the recompute, one in the comparator mapping, one undecided (docs/run_reports/2026-11-07-b5-release-hold-trace.md). Keep.","Dead code left by DLE-1: scripts/run_b5_analysis.py --mode release (:100) and the release-mode half of joulewise/b5_analysis/dry_run.py (:177-213, :353-368, :388, :510-520) plus tests/b5_analysis/test_release_equality.py are listed as 'replaced' in CANONICAL.md but still on main. Delete under the repo's own prune rule.","Redundant human receipt: align_v4_kit.py:262-269 still requires thermometry.lead_verification when R1 changes the picks, although R9-2's rederive_r1_pick_s7 (:355, called at :591) re-derives S6/S7 with the runtime's own functions so the driver and kit cannot disagree. Delete the receipt requirement.","Measurements: R0 4,569 code / ~5,100 test lines; R1/W1 ~7,170 code / ~10,200 test lines (3,453 test lines in modules named after review rounds); Block-5 19,537 code / 67,161 test lines (2,814 tests, 3.4:1). R1 process: 120 commits in 3 days, 21 review docs (3,786 lines), 1,399-line integration report, 48 rulings over rounds 4-9; the round-5 cold pass already said 'R1 can be armed'. 22 of 198 Block-5 refusal codes have ever appeared in a record. Live tails: 8 modules run, all OK (e.g. test_v4_kit 116, test_r1_rehearsal 73, test_r0_host 54, test_release_b5 27, test_comparator 28).","The R1 night's no-redo worst case (56,207 s, D8-3 table) now exceeds W1's 44,640 s window cap by 11,567 s; the rehearsal is longer than the window it rehearses, and the bound was re-derived four times under four rulings (44,487 -> 46,887 -> 54,343 -> 56,207 s). Compute once with a margin."]

**OPEN**

["Is the R0 SMC capture's sensitivity to CPU contention derivable (how much, how long, in which phase moves a heatsink key's tau or the last-60 s baseline)? Without that number the 0.05 CPU-s/s x 30 s rule is a convention, which the doctrine says is a flag.","Does W1 under High Power survive R1's A-B-A adoption test (>= 25 % longer t_decline)? If not, the High Power machinery is dead code for W1 and rank 2 becomes a deletion rather than a simplification.","Release-hold defect D5 (artifact_schema_invalid on both GAMMA contrasts): which side is wrong is still undecided by the binding probe; the release is held by a refusal whose message does not name its cause. No value was read or inferred.","Is a 15.6-25 h R1 rehearsal (no-redo worst case 56,207 s; all retries + batch wait 90,663 s) proportionate to a 44,640 s W1 window? A council question outside this audit's remit.","Who owns the pruning PRs? Ranks 1 and 2 change arm-path code on the magistrate's measurement lane and should land as separately reviewed PRs, not as part of the R1 arm; the other seat's report should be reconciled with this one before any PR opens."]

**Report**

# Proportionality and pruning audit: ALIGN v4 R0/R1/W1 machinery and the Block-5 analysis/release tooling

2026-11-07. Fable 5.1 seat (one of two independent seats on this brief). Reading-only audit of two heads:

- **R1 lane**: `lane/2026-11-06-v4-r1-integrated@e901eb2a4` (R0 host code, R1 runtime and rehearsal driver, `run_night`, the v4 kit, LEAD-RULINGS-1/2).
- **main**: `bd7a3efcd` (`joulewise/b5_analysis`, `scripts/run_b5_analysis.py`, `scripts/release_b5.py`, `scripts/independent_recompute_b5.py`, `RUN_STATE.md` items 178-202).

**Durable copy.** Committed as `docs/run_reports/2026-11-07-proportionality-prune-audit-fable.md` on branch `audit/2026-11-07-proportionality-prune-fable` (`0e06755ef`, pushed to origin mpmdw/JouleWise; no PR opened). Worktrees `jw-wt/fable-prune-r1` and `jw-wt/fable-prune-main` were removed afterwards.

**Blinding statement.** No path under `/Users/edr/jw-b5-*`, `/Users/edr/night-*`, `night-custody`, `night-archive` or any `restricted/` directory was listed or opened. No Block-5 estimate, contrast or verdict was read or inferred; the one Block-5 record cited (`docs/run_reports/2026-11-07-b5-release-hold-trace.md`) is itself structure-only by construction. Eight test modules were run once each, one module per process, under `nice -n 19 taskpolicy -b` with `TMPDIR=/private/tmp/jwburn-fable-prune`, with no model weights. No external source was opened, so none is cited.

**Frame.** Ed's advisor says the project over-engineers simple measurements. The lead keeps blinding and preregistered-estimator fidelity and treats every other guard as negotiable. Ed's own doctrine, already codified for the Block-5 hazard path, is the yardstick used here: *"physics refuses; everything else is a flag"* (`configs/gates/hazard_refusals.json:12` at `bd7a3efcd`; D-161, `docs/decision_log.md:207`: custody mechanisms whose only defended-against actor is the trusted operator "are over-engineering").

## 0. Headline findings

1. **R0 has stopped eight times in eight runs and has never passed** (11-06 08:10 to 11-07 17:15 PST, about 33 h). The eight stops ran for 8,824 s of Mac time in total, about 2.5 h, so the measurement Mac was doing R0 about 7 % of the elapsed time. Three stops were defects in R0's *own checks* (an NLL limit invalid for the model; a prompt that stated the wrong call count; a 100 ms coverage tolerance with no derivation that discarded half the readings). One was a launcher bug. **Four were quiet-guard contention refusals**, two on single-snapshot `%CPU` artefacts and two on scheduled macOS jobs running at about 0.07 CPU-s/s for 36 s during a 1,800 s thermal capture. **No stop found a fault in the hardware, the model artifact or the thermal sensors.** The one scientifically valuable finding of the week (R0's thermal picks would have been power-gated placeholders) came from two reviewers reading the journal of an *inconclusive* run, not from a refusal (section 3).
2. **About a third of the 48 R1 rulings in LEAD-RULINGS-2 (R5-6, R6-7, R7-4 to R7-11, R7-14, R8-1 to R8-3, D8-1, D8-2, D8-4, D8-5) build a High Power restore mechanism** (host marker, flock inherited through `pass_fds`, retake-before-restore, process-group termination proofs with pid+start-time identity and pipe-holder checks, signal latching, a 10 s deferral and a watchdog arming rule). What it protects over the simple design (marker before `pmset 2`; restore in `finally`; admission refuses when the observed mode is not the plan's; a leftover marker restored at the next session start) is operator convenience after a crash, not data: R8-2 records that no data is admitted in the uncovered case, and R7-14/D8-4 record that the R1 chain's zsh trap runs `pmset 0` without any lock anyway. It cost four review rounds, about 1,500 lines of code and about 2,000 lines of tests, for a mode (W1 under High Power) whose adoption is still conditional on R1's A-B-A legs. **Simplify** (section 4, rank 2).
3. **The kit's ruling 1(f) refusal is a gate its own builders expect to fail.** R7-2 and R8-8 record that at about 20 tok/s the fit does not hold even at the B_D floor, so the kit "will likely refuse W1 until the lead rules on the ruling 1(e) fallback". A refusal that is expected to fire and then be overruled is a scheduled round-trip, not protection. **Pre-rule 1(e) now** (a design choice that does not depend on R1's numbers), or make 1(f) a recorded disclosure (rank 3).
4. **The Block-5 comparator earned its cost.** Running `scripts/release_b5.py` on the dry-j custody held the release with 1,001 failing rows in 11 families; the blind, structure-only trace attributed every row to six defects: one in L9 (a wrong key, hidden by a fixture with the same wrong key), three in the recompute, one in the comparator's mapping, and one still undecided (`docs/run_reports/2026-11-07-b5-release-hold-trace.md`). That is a guard catching real bugs on both sides before unblinding, at a cost of minutes. **Keep** (section 5).
5. **The Block-5 heavy pipeline has already been proportionality-audited** (`docs/run_reports/2026-11-06-b5-care-audit.md`, 26 layers, 12 ranked cuts; DLE-0 to DLE-2 adopted, DLE-3 to DLE-5 not adopted). The r3 dry run took 1 h 40 min against r1's about 37 h (RUN_STATE item 197). This audit does not repeat that table. The remaining prunes are code that DLE-1 made dead (`run_b5_analysis.py --mode release` and the release-mode half of `dry_run.py`), one refusal word that collapses dozens of causes into one (`artifact_schema_invalid`), and 51,000 lines of tests organised by review round rather than by subject.
6. **The review-round process itself is the largest unmeasured cost.** R1 has had six rounds (4 to 9) in about 36 hours: 120 commits on the lane (6 on 11-05, 77 on 11-06, 37 on 11-07), 21 review documents (3,786 lines), a 1,399-line integration report and 48 rulings. Each round is an executing review plus a cold pass plus an advisory Sol critique, then two builder lanes each with its own Sol critique, then integration and a Sol event audit. The round-5 cold pass said "R1 can be armed" (RUN_STATE item 191); four more rounds followed before e901eb2a4. R0 blocked R1 the whole time, so those rounds did not delay a measurement, but they occupied the lead and the builders for about 30 hours.

## 1. Measurements: lines of code and tests per subsystem

Counted with `wc -l` and `grep -c 'def test_'`. Test tails are from one live run of each module at background priority (section 1.4).

### 1.1 ALIGN v4 R0 (lane `e901eb2a4`)

| Part | Code (lines) | Tests (lines / `def test_`) |
|---|---:|---|
| `joulewise/align/r0_host.py` (QuietGuard, inventory, disk, SMC receipt) | 608 | `tests/align/test_r0_host.py` 1,012 / 54 |
| `r0.py`, `r0_runner.py`, `r0_step.py`, `r0_mlx.py`, `scripts/align_r0_checks.py` | 1,534 | `test_r0_checks` 493 / 30; `test_r0_load_reference` 585 / 34; `test_r0_load_reference_adversarial` 144; `test_r0_step` 201; `test_r0_mlx` 189; `test_r0_mlx_native` 69; `test_r0_integration` 74; `test_r0_progress` 80; `test_r0_dispositions` 89; `test_r0_scheduling` 261; `test_r0_documentation` 48 |
| SMC classifier: `apple/smc_enumeration.py`, `apple/thermal.py`, `scripts/align_smc_enumerate.py` | 1,311 | `test_smc_quiet` 551; `test_smc_classifier_v4` 496; `test_smc_selection` 150; `test_smc_native` 42; `test_smc_gpu` 47; `test_thermal_coverage` 105; `tests/hazards/test_smc_enumeration` 268; `tests/hazards/test_smc` 239 |
| Shared quiet guard: `joulewise/prewindow.py`, `joulewise/hazards/contention.py` | 1,116 | (covered by the above and the hazards suite) |
| **R0 total** | **4,569** | **about 5,100 lines** |

`scripts/launch_align_r0.py` lives on `main`, not on this lane (CANONICAL.md), and is not counted.

### 1.2 ALIGN v4 R1 / W1 (lane `e901eb2a4`)

| Part | Code (lines) | Tests (lines / `def test_`) |
|---|---:|---|
| `joulewise/align/apple/r1_runtime.py` + `r1_runtime_contract.py` + `scripts/align_r1_runtime.py` | 2,313 | `test_r1_runtime` 875 / 33; `test_r1_runtime_e2e` 123; `test_r1_runtime_contract` 140; `test_r1_inventory` 315 / 14 |
| `scripts/align_r1_rehearsal.py` (driver) + `night_chains/align_r1_rehearsal.zsh` + `configs/align/v4/r1_runtime.json` | 2,030 | `test_r1_rehearsal` 1,588 / 73 |
| `scripts/align_v4_kit.py` | 1,340 | `test_v4_kit` 1,772 / 116; `test_v4_prequal` 444 / 33; `test_v4_wp18_fixtures` 295 / 11; `test_v4_w1_plan` 219; `test_v4_w1_synthetic` 188; `test_v4_estimands` 135; `test_v4_verify_d_pins` 62 |
| High Power / host state: `joulewise/align/apple/powermode.py`, `scripts/align_v4_session.py`, `scripts/run_night.py` delta vs `main` (+615 of 5,797) | 1,487 | `test_run_night` delta +440 (of 7,419 / 318); `test_v4_powermode_record` 138 / 9 |
| Round-named test modules (`test_r1_round5_exec_review` … `test_r1_round8_exec_review`, `test_r1_round7_close_deferral`, `test_r1_round6_lows`) | — | 3,453 / 155 |
| **R1/W1 total** | **about 7,170** (+756 shared `thermal_gates.py`) | **about 10,200 lines** |

Refusal sites (`grep -c 'Refusal(\|Refused(\|night_refused'`): `align_r1_rehearsal.py` 81, `run_night.py` 69, `r1_runtime.py` 27, `r0_host.py` 19, `powermode.py` 10. The kit raises `ValueError` instead (about 60 `raise` sites in `check_r1_evidence`, `require_ready`, `check_r1_budget_and_policy`).

Process volume for R1 rounds 4-9: LEAD-RULINGS-2 734 lines, 48 numbered rulings; `docs/align/reviews/` 21 documents dated 11-05 to 11-07, 3,786 lines; `docs/run_reports/2026-11-06-align-v4-r1-integration.md` 1,399 lines; 120 commits since the merge-base with `lane/2026-11-05-align-pilot10-benign` (`5f817856b`).

### 1.3 Block-5 analysis and release tooling (`main@bd7a3efcd`)

| Part | Code (lines) | Tests (lines / `def test_`) |
|---|---:|---|
| `joulewise/b5_analysis/**` (18 modules; `dry_run.py` 2,301, `disclosures.py` 1,379, `phase_timing.py` 1,276) | 9,385 | `tests/b5_analysis/**` 41,734 / 1,707 |
| `scripts/run_b5_analysis.py` | 141 | (in the above) |
| `scripts/release_b5.py` (DLE-1) | 506 | `tests/independent_recompute/test_release_b5.py` 433 |
| `scripts/independent_recompute_b5.py` | 3,255 | `tests/independent_recompute/**` 9,687 / 456 (incl. the above) |
| `scripts/compare_b5_recompute.py` (comparator) | 4,105 | (in the above) |
| `tools/b5_equivalence/compare_b5_results.py` (D-188 gate) | 2,145 | `test_result_equivalence` 1,914 (in `tests/b5_analysis`) |
| Top-level `tests/test_b5_*.py`, `test_harvest_b5_*.py`, `test_size_b5_window.py`, `test_write_b5_identity_pins.py` | — | 15,740 / 651 |
| **Block-5 total** | **19,537** | **67,161 / 2,814** (ratio 3.4 : 1) |

Refusal vocabulary: `configs/analysis/b5/dry_run_refusal_classes.json` holds 196 tooling codes and 2 outcome codes. Of the 198, **22** are named in `RUN_STATE.md`, `docs/run_reports/*.md` or `docs/analysis/b5/*.md` (section 6).

### 1.4 Live test tails (this audit, one module per process, `nice -n 19 taskpolicy -b`)

| Module | Result |
|---|---|
| `tests.align.test_r0_host` | Ran 54 in 61.1 s, OK (skipped=1) |
| `tests.align.test_v4_kit` | Ran 116 in 14.5 s, OK |
| `tests.align.test_r1_rehearsal` | Ran 73 in 9.9 s, OK |
| `tests.align.test_r1_runtime` | Ran 33 in 100.5 s, OK |
| `tests.align.test_r1_round8` | Ran 21 in 32.5 s, OK |
| `tests.align.test_v4_prequal` | OK (skipped=3) |
| `tests.independent_recompute.test_release_b5` | Ran 27 in 19.0 s, OK |
| `tests.independent_recompute.test_comparator` | Ran 28 in 28.0 s, OK |

Harness note: `python3 -P -m unittest tests.…` fails with `No module named 'tests'` from a plain worktree, because `-P` drops the working directory from `sys.path`. The integration report recommends `-P` for reviewer seats; that holds only with `PYTHONPATH` set or a `cd` that survives the call.

## 2. What a refusal is for

A refusal is worth its cost when all three hold: (i) the condition it detects would corrupt a *reported* number or the blinding, (ii) nothing downstream would catch it, and (iii) the cost of a false refusal (a rerun, a review round, an escalation) is smaller than the expected harm. Ed's doctrine compresses this to "physics refuses; everything else is a flag". The tables below apply it.

## 3. Case study: R0, eight stops and no pass

Sources: `RUN_STATE.md` items 178-202 (`bd7a3efcd`, lines 1045-1600), the record branches they cite, and the code at `e901eb2a4`.

| # | Record dir | Launched (PST) | Ran | Stopped at | Cause | Class | What it cost |
|--:|---|---|--:|---|---|---|---|
| 0 | `2026-11-06` | 11-06 08:10 | 21 s | `model-load` FAIL | `launch_align_r0.py` resolved `--python-bin` through the venv symlink to the bare Homebrew interpreter (no mlx) | our launcher bug | PR #684 (Sonnet executing review, CI 20 jobs) |
| 1 | `2026-11-06-rerun` | 09:03 | 76 s | `load` FAIL (NLL 11.04 vs limit 3.0) | the absolute-NLL check was invalid for D: upstream Qwen3.8-27B in HF fp32 also scores 11.06 on those ids | **check defect** (false refusal) | escalation to Ed; off-Mac diagnosis lane; PR #686 redesign to reference-equivalence (executing review, Fable cold pass, CI 30 jobs); R0 held about 5.5 h (items 182-185) |
| 2 | `2026-11-06-rerun2` | 14:34 | 160 s | `generated` inconclusive | R0's own echo prompt stated 6 calls where 16 were needed; D asked whether to continue | **check defect** (R0 harness) | PR #687 (Sol executing review, Fable cold pass with a live seed-95 run, CI about 2.5 h); about 3 h (item 186) |
| 3 | `2026-11-07-rerun3` | 17:33 | 158 s | census refusal mid-`generated` | `photoanalysisd` respawn start-up burst (about 0.6 CPU-s) read as 34 % on one `ps` snapshot | **guard artefact** (single-snapshot `%CPU`) | `kill -STOP photoanalysisd`; relaunch 17:52 (item 188) |
| 4 | `2026-11-07-rerun4` | 17:50 | 905 s | census refusal at the start of `smc` | `mdworker_shared` 0.6 s old at 6.0 % decayed `%CPU`; separately the SMC `CpuQuietProbe`'s hard-coded host-aggregate limit of 0.05, which the idle Mac exceeded in 8 of 12 lead probes | **guard design** | PR #691: three Sol builds, two Opus executing reviews, three Fable cold passes, a Sol critique, 14 adversarial tests; measurement Mac idle 18:05-22:35 (about 4.5 h); Ed asked why the MBP was idle (items 189-192) |
| 5 | `2026-11-07-rerun5` | 22:32 | 2,246 s | `smc` exit 3 `NotQuiet` after 1,310 s of a 1,800 s capture | `softwareupdated` 23:09 scan at 0.070 CPU-s/s and `duetexpertd` at 0.067 over 35.9 s, against 0.05 | real but trivial OS job | timing re-launch (item 193) |
| 6 | `2026-11-07-rerun6` | 23:20 | 2,470 s | `smc` exit 3 `NotQuiet` after 1,520 s | midnight `com.apple.tmp_cleaner` `find` at 0.079 and `fseventsd` at 0.070 CPU-s/s over 35.9 s | real but trivial OS job | third-in-a-row rule: mailed Ed and waited; Ed answered "go" two minutes later; `/private/tmp` pruned from about 79,000 to 3,900 entries (items 194, 201) |
| 7 | `2026-11-07-rerun7` | 11-07 00:15 | 2,789 s | `smc` inconclusive: every one of 403 keys rejected for "insufficient phase coverage" | `thermal.Coverage` fills a 1 s cell only when a reading's midpoint is within 100 ms of the grid; readings start 80-150 ms late and a 403-key read takes 86 ms; "the 100 ms value carries no derivation" | **check defect** (underived constant) | fix lane; two blind cold passes found the *fixed* picks were placeholder series; three blind fresh designs, reconciliation D1-D6, four build/review rounds, Errata 1-5, PR #692 merged 08:45; R0 held about 17 h (item 195) |
| 8 | (re-run 8) | 17:15 planned | — | — | — | — | item 201: after the 17:09 scan, in the 17:15-23:05 gap |

Mac time spent inside R0 over the eight stops: 8,824 s (2 h 27 min). Elapsed: about 33 h.

**What the stops found, by class.**

- *Check defects (runs 1, 2, 7).* Three of eight stops were R0's own checks being wrong. Each cost a fix lane with two or three model seats and a CI run of 1-2.5 h on this lane (items 186, 190, 195). The run-7 defect was a constant with "no derivation", exactly the kind of number the 2026-10-17 charge forbids ("no silly numbers: every value or bar carries a derivation", `docs/process_traces/2026-10-17-magistrate-52d50d1f/reg-gate-charge.md:27`).
- *Guard artefacts (runs 3, 4).* The guard judged one `ps` `%CPU` snapshot (`prewindow.busy_contaminants`, `joulewise/prewindow.py:23`, limit 5 %, `:5`). With about 100 samples per R0 and `mdworker_shared` respawning every 2-7 minutes, an unchanged re-run "would very likely be refused again" (item 189). The lead's own ruling in item 189 then made the SMC probe's host aggregate "journaled and flagged, not judged": the doctrine applied to half the guard.
- *Real but trivial contention (runs 5, 6).* After PR #691 the guard judges CPU-seconds per second over at least 30 s (`r0_host.py:147-166`, `prewindow.INTERVAL_S` = 30, `CPU_LIMIT_PERCENT` = 5.0). Both refusals were about 0.07 CPU-s/s for 36 s, during the *recovery* phase of a capture whose purpose is to classify temperature keys by their time constants under a 900 s GPU load. Seven per cent of one core for half a minute is a few tens of joules against a load of tens of kilojoules; it does not move a heatsink key's tau. Each refusal threw away 1,300-1,500 s of capture and the whole 900 s load. The remedy adopted was timing (item 193) and a `/tmp` prune (item 201). No design change was made to the refusal itself.
- *Launcher bug (run 0).* Caught by the cheapest check; nothing to prune.

**What the refusals protected.** R0 is "selection data, not R1, thermal validation or an arm authorization" (`docs/align/r0_desk_runbook.md:4-5`) and "a readiness check, not the energy measurement" (RUN_STATE item 192). Its outputs are a reasoning-effort rung, provisional sensor picks (`r0_host.py:513`, `selection_status: PROVISIONAL`) that R1 re-selects on its own capture, a B7 verdict and a peak-memory number. None is a reported quantity, none is blinded. Under the doctrine, every R0 refusal except "a measurement window is armed / a chain is running / the host is not the measurement Mac" is a flag.

**The one science catch came from reading, not refusing.** Run 7's inconclusive result, once the coverage bug was fixed in a diagnostic re-rank, still selected `Tg*` keys reading a fixed -2.75 °C placeholder and a `TaRT` still cooling through idle (item 195). That finding produced the D1-D6 classifier redesign and R7-2's 1,200 s G0 cap. It was found by two reviewers looking at the journal of a run the guard had already passed through (run 7 had no contention refusal). Refusals bought nothing here; a recorded capture did.

**Escalation rule.** Item 181's "third consecutive failure of the same check goes to Ed" fired once (item 194). Ed replied "go" in two minutes. The rule exists for science changes; applied to R0 contention it is a wait with no decision content.

**Recommendations for R0 (ranks 1, 5, 8 in section 7).**

1. `QuietGuard.check` keeps refusing on an armed window, a loaded night LaunchAgent, a running chain or a failed custody census (`r0_host.py:236-269`); the CPU-contention branch (`:270-275`) becomes a recorded flag with the contaminant list, and `CpuQuietProbe`'s `NotQuiet` on CPU (`smc_enumeration.py:213`) likewise, with the per-phase contaminant record carried into the classifier's per-key flags (the D3 design already flags an unsettled baseline rather than refusing). Expected effect: runs 3-6 would have completed; run 7 would have been the second R0, not the eighth.
2. Pre-qualify off-Mac what Ed's standing principle names (item 183): `load` reference equivalence, `generated`, `template` and the D-pin inventory can run on the Air against the same artifact bytes; R0 on the Mac keeps `host`, `host-identity`, `disk`, `memory`, `smc`, `ladder`, `long-decode`.
3. Review gates for R0 fixes: one executing review plus the quick CI tier. Run 2's prompt-string fix had a Sol executing review, a Fable cold pass with a live model run, and a 2.5 h CI (item 186).
4. Narrow item 181's escalation rule to science changes and irreversible data actions; drop "third consecutive failure of the same check" for readiness checks.

## 4. ALIGN v4 R1 / W1 machinery, guard by guard

R1 has not run on hardware, so no field refusals exist. "Caught" means caught in review or tests; "would risk" is the harm if the guard were removed.

| # | Guard / code path (at `e901eb2a4`) | Protects | Has caught | Removing or simplifying would risk | Recommendation |
|--:|---|---|---|---|---|
| 1 | **High Power host marker + host night lock + termination proofs.** `powermode.py` (`HostLock` :189, `restore_owed` :272, `admit_ac_powermode` :358, `HostStateOverrideRefused` :97); `align_r1_rehearsal.py` `PowerModeGuard.restore` :393-468, `_terminate` :262-339, `_stop_tree` :237, `_descendants` :215; `run_night.py` `_CHAIN_TERMINATION_UNPROVEN`, `_stop_chain_on_interrupt`, `_terminate_process_group`; rulings R5-6, R6-7, R7-4 to R7-11, R7-14, R8-1 to R8-3, D8-1, D8-2, D8-4, D8-5 | The host left at `powermode 2` after a crashed W1 High-Power night, restored automatically on every exit path | Review-on-review only: R7-4's handler "held only before the chain spawned" (corrected by R8-1); Sol F1-F8 critiques per round. Nothing in the field | A crash leaves mode 2. The next admission *already refuses* on the observed mode (R5-6: "The next night then refuses on the mode alone (fails closed) and needs a manual `sudo -n pmset -c powermode 0`"). A restore under a surviving orphan can only affect an *aborted* night: "No data is admitted in that case" (R8-2). And the R1 chain's zsh EXIT trap runs `pmset 0` "without lock or proof, overriding an R8-1 deferral" (D8-4) | **Simplify.** Keep: `sudo -n -l` rule check; marker written before `pmset 2`; restore in `finally` with the R7-7 read-back; admission read-back refusal; session-start restore of a leftover marker. Delete: `HostLock` and `pass_fds`, retake-before-restore, `_terminate`'s descendant census and `_stop_tree`, pid+start-time identity, pipe-holder proofs, `_CHAIN_TERMINATION_UNPROVEN` and its defer branches, the 10 s signal deferral and its watchdog-arming coupling, `HostStateOverrideRefused` production marking. Keep R8-2's paragraph as the documented limit. Saves about 1,500 code lines, about 2,000 test lines, and the review surface that produced 16 rulings |
| 2 | **Ruling 1(f) fit and G0_cap_W1 derivation.** `align_v4_kit.py` `ruling_1f_fit` :469, `max_fitting_b_d` :527, `w1_g0_cap` :419; rulings R5-4, R6-3, R7-2, R7-12, R8-8 | A worst-case D member fitting under the 1,800 s member cap | Nothing yet. Builders: "1(f) will likely refuse W1 … until the lead rules on the ruling 1(e) fallback (R6-3: no code fallback)" (LEAD-RULINGS-2 :362-365); R8-8 confirms this is "expected" | A D member killed at 1,800 s by the runner would lose its bundle (a real bound) | **Decide 1(e) now, blind** (it is the fallback *order*, independent of R1's values), and encode it so the kit records "1(f) does not fit at B_D; applying 1(e) step k" instead of refusing. Keep the G0_cap_W1 derivation (physics from re-run 7) |
| 3 | **R1 night worst-case table**, `night_worst_case_s` :1314, `segment_bounds` :138, `rearmed_member_bound_s` :126; recomputed under R6-8, R7-2, R8-4, D8-3 (44,487 → 46,887 → 54,343 → 56,207 s) | `window_max_s` for the R1 plan | Each recompute found the previous bound too tight | A night cut by the wall-clock deadline in the all-caps case | **Simplify.** Compute once with a stated margin, record it, stop re-deriving per ruling. The number is a reservation (protocol v4 :653). Even the no-redo case (56,207 s, 15.6 h) exceeds W1's 44,640 s cap by 11,567 s: the R1 night is longer than the window it rehearses |
| 4 | **Kit re-derivation of R1 evidence.** `check_r1_evidence` :179-306; `check_r1_budget_and_policy` :539; `check_duty_bar_consistency` :381; `rederive_r1_pick_s7` :355; `check_r1_fast_band` :331 | A hand-edited or stale `r1_slots` reaching W1's frozen inputs | In tests (mutation checks per round, 116 kit tests) | Silent divergence between the driver's record and the kit's inputs | **Keep**, with one deletion: `thermometry.lead_verification` for changed picks (:262-269) is redundant with R9-2's `rederive_r1_pick_s7` (:355, called at :591), which re-derives S6/S7 with the runtime's own functions. A human receipt protecting a value the kit recomputes is ceremony |
| 5 | **Inconclusive-segment refusal** (R6-2, R7-3; kit :191-203) | beta_T / U5 having all three designed points; step-d slots existing | Nothing yet | W1 sized from a partial R1 | **Keep for step-d. Flag for a designed start state**: one missing U5 point makes U5 INCONCLUSIVE, already a recorded verdict the kit admits (`U5_VERDICTS`); refusing W1 on it forces a second 15 h night for one calibration point |
| 6 | **WP18 fixtures as a hard W1 prerequisite** (R5-8; `validate_wp18_fixtures` :859, `check_wp18_turn_contents` :844) | X/Y `max_turns` and token-id fixtures tied to pilot-7 bytes | One refusal, on the tool's own defect (item 194); fixed R6-8 / Sol F7 | Wrong X/Y turn caps in W1 | **Keep.** One-time, minutes, binds registered inputs |
| 7 | **Alias groups** (R7-13, R8-6, R9-1): `r1_runtime.alias_groups` :448; kit :226-247 | `s_fast`/`s_slow` independence | Physics input from re-run 7: TCMb and TVD0 identical in all 1,800 rows | Two "sensors" that are one | **Keep.** Cheap, grounded in observed data |
| 8 | **Precool / retry / INCONCLUSIVE instead of night refusal** (R5-3, R6-2, R7-12) | A night not lost at hour 10 to one G0 timeout | Design review | A full re-run for a transient | **Keep.** The right direction: refusals became recorded results |
| 9 | **Soak-reference consume check**, `_check_soak_reference_consumed` :1548 (R5-1, R6-1) | Gated runs gated against the same R as W1 | Design review | An uninformative duty bar | **Keep** |
| 10 | **Batch-window avoidance**, `wait_outside_os_batch` :980 (ruling 8) | Quiet segments not overlapping the 11:45-13:15 batch | Unknown; adds up to 5,400 s per night | Contention during a quiet segment | **Keep** (it waits; it does not refuse) |
| 11 | **Review-round structure** (exec review + cold pass + Sol critique → rulings → two builder lanes each with a Sol critique → integration → Sol event audit) | Correctness of unrun code | Real bugs in prior rounds (R7-4 → R8-1; R7-9's false window claim) | A night driver bug that aborts the night | **Simplify.** One executing review plus one cold pass per round; Sol critiques advisory, never a gate (R5-9 F1 and the #691 REJECT were triaged to nothing). Stop the round when the cold pass says "can be armed" (round 5); later findings become post-R1 fixes unless they touch the arm path |
| 12 | **`configs/gates/hazard_refusals.json` allowlist** (3,286 lines, 2,796 sites; `tests/hazards/test_refusal_allowlist.py`) | Every new HAZARD_PACK refusal classified PHYSICS / NUMBER_INTEGRITY / INTERNAL | R8-1, D8-1, D8-2 each had to allowlist a re-raise site | Unclassified refusals creeping in | **Keep.** It is the mechanised form of the advisor's request. Extend the *doctrine* to the align lane, where R0's refusals live outside it |

## 5. Block-5 analysis and release tooling (delta over the care audit)

The care audit of 2026-11-06 ("CARE") already inventoried 26 guard layers with wall costs and 12 ranked cuts. The lead adopted DLE-0, DLE-1 and DLE-2; DLE-3 to DLE-5 are "not adopted for now" (`docs/analysis/b5/DEVIATION-LOG.md`). This section adds only what CARE did not have.

| # | Guard / code path (at `bd7a3efcd`) | Protects | Has caught | Removing would risk | Recommendation |
|--:|---|---|---|---|---|
| 1 | **Release comparator at 1e-6** (`scripts/release_b5.py` stages (a)-(c), bars pinned by SHA-256 at :58; `compare_b5_recompute.py`; `recompute_bars.json`) | The printed numbers agree between two independent programs; blinding (structure-only verdict) | **Yes, on real data.** The dry-j release check held: 1,001 failing rows, 11 families, traced blind to six defects: D1 L9 reads `battery_available` where the record has `battery_term_available` (`disclosures.py:696`; fixture at `test_disclosures.py:380` had the same wrong key); D2 recompute reads attempt-1 idle telemetry; D3 recompute coverage gap; D4 recompute membership; D5 undecided (floor binding); D6 comparator mapping of NEG-8 terms | Unblinding with a known bug on one side | **Keep.** The clearest positive evidence in the audit. Cost: minutes per run |
| 2 | **`run_b5_analysis.py --mode release`** and the release-mode half of `dry_run.py` (`release_difference` :177, `require_release_equality` :206, mode branches :353-368, :388, :510-520; `tests/b5_analysis/test_release_equality.py`) | The PLAN §3.2 second heavy run | Never run on real data; DLE-1 replaced it on 2026-11-06 | Nothing: CANONICAL.md lists it as *replaced* | **Delete** under the repo's own rule ("superseded tools are deleted from `main`"). Keep the record-validator branch only if a historical record with `release_difference` must still validate |
| 3 | **`artifact_schema_invalid` as a bare refusal word** (`analysis_engine/__init__.py:413-455`, `inputs.py:594-626` per the trace: ten binding codes surfaced, every other binding problem collapses into the bare word) | A floor cell with bad evidence never serves a number | Fired on dry-j (D5) and could not be diagnosed without a probe script and a second blind round | A fabricated floor (D-173) | **Simplify the message, not the guard.** Surface every binding reason code |
| 4 | **Test corpus organised by review round** (`test_rc_cmp7` … `test_rc_cmp11`, `test_round3`, `test_review_fixes`, `test_auditfix`, `test_vdl_sol_hunt`/`_hunt2`/`_hunt3`, `test_vdl_sol_w2`, `test_s10_chain_defects`, `test_small_fixes`; `tests/align/test_r1_round5_exec_review` … `test_r1_round8_exec_review`) | Regression coverage | They pass | Losing a regression test | **Consolidate by subject**, delete duplicates, keep failing-first tests. CI shards on these lanes take 1-3 h (items 190, 195) |
| 5 | **D-188 equivalence comparator** (`tools/b5_equivalence/compare_b5_results.py` 2,145; `test_result_equivalence.py` 1,914) | A restructured heavy pipeline equals the r1 oracle | Yes: r2 EQUIVALENT to r1 on real data (item 196) | Nothing after release | **Keep until the block-5 release, then delete** (CARE row 17) |
| 6 | **Refusal registry** (196 tooling + 2 outcome codes) | Tooling vs outcome separation (blinding) | 22 of 198 codes have ever appeared in a record | Blinding leak on an unclassified refusal | **Keep.** Zero runtime cost; do not prune never-fired codes |
| 7 | **120 s refit deadline** (CARE row 9, DLE-5 not adopted) | Host safety at collection; converted to a tooling refusal in analysis | Fired in synthetic runs; forbids co-scheduling | A load-dependent non-reproducible number | **Re-open DLE-5 after block-5 release.** Moot on the critical path once the recompute is production (DLE-2) |

## 6. Which refusals have fired in practice

| Subsystem | Fired | Protected a reported number or blinding |
|---|---|---|
| R0 (8 runs) | 8 stops: 4 contention refusals, 3 check defects, 1 launcher bug | 0 |
| R1 driver / runtime | 0 (never run on hardware) | — |
| v4 kit `--check` | Blocks by design on `R0.reasoning_effort` and the four R1 leaves (item 202 (2)); the WP18 tool refused once on its own defect (item 194) | the WP18 bind is registered input; the refusal itself was a bug |
| Block-5 dry runs | Attempts A-E, dry-h, dry-i, dry-j, dry-k each ended or re-ran on a tooling refusal or incident (CARE row 22): the 120 s deadline in synthetic runs, `reader_record_not_structure_only` false positive at attempt A, attempt D's ENOSPC, attempt B's unmerged checkout | the blinding scan (a false positive, on the right side) |
| Block-5 release check (dry-j) | Comparator hold: 1,001 rows, 6 defects | **yes**: D1 (L9), D2-D4 (recompute), D6 (comparator) |

Refusal codes from `dry_run_refusal_classes.json` that appear in `RUN_STATE.md`, `docs/run_reports/` or `docs/analysis/b5/` (22 of 198): `calibration_deadline_observer_unavailable`, `calibration_wall_deadline_fired`, `custody_path_invalid`, `dry_run_record_invalid`, `dry_run_record_missing_or_incomplete`, `excluded_reference_in_screen`, `exclusions_roster_mismatch`, `extraction_cell_r3_refusal`, `extraction_cell_tooling_refusal`, `extraction_report_malformed`, `harvest_checkout_not_clean`, `harvest_record_not_the_indexed_one`, `kept_units_below_minimum`, `kept_units_required`, `reader_record_not_structure_only`, `release_digest_differs_from_dry_run`, `results_fill_path_refused`, `seal_pins_invalid`, `sensitivity_changed_bound_independent_value`, `whole_window_verdict_conflict`, `whole_window_verdict_provenance_invalid`, `window_index_invalid`. (A mention is not a firing; restricted logs were not read.)

## 7. Ranked prune list

Ranked by expected measurement-Mac hours or lead/builder hours returned per unit of protection given up. Blinding and preregistered estimators are untouched by every row.

| Rank | Prune | Returns | Gives up | Who rules |
|--:|---|---|---|---|
| 1 | **R0 contention refusals become flags** (`r0_host.py:270-275`; `smc_enumeration.py:213`); keep the armed-window / chain / custody refusals | Runs 3-6 (four re-launches, PR #691's 4.5 h of idle Mac, one Ed wait); every future scheduled-job refusal | Nothing reported: R0 is selection data with provisional picks; contamination is recorded and visible to R1 | Lead (engineering); classify under the 10-05 doctrine |
| 2 | **Simplify High Power restore to marker + finally-restore + read-back + admission refusal + session-start restore**; delete `HostLock`/`pass_fds`/retake, process-tree proofs, `_CHAIN_TERMINATION_UNPROVEN`, the 10 s deferral coupling | About 1,500 code + 2,000 test lines; the review surface that produced 16 rulings in four rounds | Automatic restore after a SIGKILL; the operator runs one `pmset` line, which R5-6 already documents as the fail-closed path | Lead (engineering); W1 under High Power is still conditional on R1's A-B-A |
| 3 | **Rule 1(e) now and make 1(f) a recorded fit with the fallback applied**, not a refusal | One predicted lead round-trip after R1, i.e. the night between R1 and W1 | Nothing: the kit still records the fit and the step taken | Lead (design); blind to R1's numbers by construction |
| 4 | **Delete `--mode release` and the release-mode half of `dry_run.py`** plus `test_release_equality.py` | A dead path in a 2,301-line driver | Nothing: DLE-1 and CANONICAL.md already retired it | Lead (engineering), same PR updates CANONICAL.md |
| 5 | **Pre-qualify R0's `load`, `generated`, `template` and D-pin inventory off-Mac** (item 183) | The Mac-side R0 shrinks to host/disk/memory/smc/ladder/long-decode | Nothing: same bytes, same code | Magistrate (item 181) with a lead kit |
| 6 | **Delete `thermometry.lead_verification` for changed picks** (kit :262-269), redundant with R9-2's re-derivation | One lead receipt per changed-pick R1 | Nothing: the kit recomputes S6/S7 itself | Lead (engineering) |
| 7 | **Review rounds: exec + one cold pass; Sol critiques advisory, never a gate; stop at "can be armed"** | About half the lead/builder hours per round | Some LOW findings reach hardware instead of review; they become post-R1 fixes | Lead (process) |
| 8 | **R0 fix gates: one executing review + quick CI tier**; narrow item 181's third-failure escalation to science changes | 1-2.5 h CI and one or two seats per R0 fix; one Ed wait | A reviewer's catch on a prompt string | Lead (process) |
| 9 | **Compute the R1 worst case once with a margin**; stop re-deriving per ruling | One ruling + builder + test update per round | A tighter bound | Lead (engineering) |
| 10 | **A designed-start-state INCONCLUSIVE flags U5 INCONCLUSIVE instead of refusing W1** (step-d stays a refusal) | A second 15 h R1 night for one calibration point | beta_T from two points instead of three, recorded as such | Lead (design) |
| 11 | **Surface every floor-binding reason code behind `artifact_schema_invalid`** | A blind trace round per firing | Nothing | Lead (engineering), cited rebind of L9 |
| 12 | **Consolidate round-named test modules by subject** | CI shard time on lanes (1-3 h today); legibility of coverage | Duplicated regression tests, kept once | Lead (engineering), no deadline |
| 13 | **Retire `tools/b5_equivalence` at the block-5 release** (CARE row 17) | 2,145 + 1,914 lines | Nothing after release | Lead (engineering) |
| — | **Keep unchanged**: the comparator and bars; blinding layers; the refusal registry; the step-0 census; alias groups; precool/retry INCONCLUSIVE design; soak-reference consume; the hazard refusal allowlist; the WP18 fixtures; the kit's evidence binding (minus rank 6) | — | — | — |

## 8. Open questions

1. **Is the R0 SMC capture's contention sensitivity derivable?** Nobody has written down how much CPU contention, for how long, in which phase, shifts a heatsink key's tau or the last-60 s baseline. Until that number exists, the 0.05 CPU-s/s × 30 s rule is a convention, and the doctrine says a convention is a flag.
2. **Does W1 under High Power survive R1?** If the A-B-A legs do not adopt it (≥ 25 % longer t_decline), the whole High Power path is dead code for W1 and rank 2 becomes a deletion rather than a simplification.
3. **D5 on the release hold.** Which side is wrong (L9's floor binding or the producing tooling) is still undecided by the probe. Until it is, the block-5 release is held by a refusal whose message does not name its cause (rank 11). Nothing here reads or infers its value.
4. **The R1 night is longer than W1.** The no-redo worst case (56,207 s) exceeds the W1 window cap (44,640 s) by 3.2 h. Whether a 15.6-25 h rehearsal is proportionate to the window it rehearses is a council question, outside this audit's remit, but the number should be in front of them.
5. **Who owns the pruning PRs?** Every row in section 7 touches a frozen or reviewed lane. Ranks 1 and 2 change arm-path code and should land as one reviewed PR each, not as part of the arm.

## 9. Evidence index

Repo paths are at the named commits. No external sources were opened.

- `RUN_STATE.md@bd7a3efcd`: items 202 (:1045), 201 (:1069), 200 (:1084), 199 (:1095), 198 (:1101), 196 (:1129), 195 (:1154), 194 (:1280), 193 (:1326), 192 (:1355), 189 (:1444), 188 (:1458), 186 (:1486), 185 (:1500), 182 (:1548), 180 (:1570); items 178-202 span lines 1045-1600.
- `docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-2.md@e901eb2a4`: R5-6 :81-93; R6-7 :236-264; R7-2 :341-365; R7-5 :385-395; R7-14 :465-469; R8-1 :489-512; R8-2 :516-520; R8-8 :591-593; D8-3 table :638-655; D8-4 :659-663; R9-2 :705-728. `LEAD-RULINGS-1.md@e901eb2a4` (L1-L3).
- `docs/align/r1_runtime_contract.md@e901eb2a4`; `docs/align/pilot_protocol_v4.md@e901eb2a4` :644-700; `docs/align/r0_desk_runbook.md@e901eb2a4` :1-20.
- `joulewise/align/r0_host.py@e901eb2a4`: `QuietGuard` :67-282 (`check` :214-282; contention refusal :270-275; window/chain/custody refusals :236-269); SMC receipt :493-609 (`PROVISIONAL` :513).
- `joulewise/align/apple/smc_enumeration.py@e901eb2a4`: `NotQuiet` :83, `CpuQuietProbe` :87-220 (CPU refusal :213; aggregate flag :141, :153). `joulewise/prewindow.py@e901eb2a4` :5-6, :23, :31. `joulewise/hazards/contention.py@e901eb2a4` :101-103. `joulewise/align/r0_runner.py@e901eb2a4` :21, :112, :259-261.
- `scripts/align_r1_rehearsal.py@e901eb2a4`: constants :44-80, :159; `_descendants` :215, `_stop_tree` :237, `_terminate` :262, `PowerModeGuard` :360-495, `phase_plan` :495-540, `wait_outside_os_batch` :980, `night_worst_case_s` :1314, `_check_soak_reference_consumed` :1548.
- `joulewise/align/apple/powermode.py@e901eb2a4`: :97, :189, :272, :358, :460, :500.
- `scripts/align_v4_kit.py@e901eb2a4`: `check_r1_evidence` :179-306 (:191-203, :226-247, :262-269); `rederive_r1_pick_s7` :355 (called :591); :381; :419; :469; :527; :539; `require_ready` :637-704; :859.
- `configs/gates/hazard_refusals.json@bd7a3efcd` :1-20 (doctrine :12). `docs/decision_log.md@bd7a3efcd` :207 (D-161). `docs/process_traces/2026-10-17-magistrate-52d50d1f/reg-gate-charge.md@e901eb2a4` :27. `CANONICAL.md@bd7a3efcd`.
- `docs/run_reports/2026-11-06-b5-care-audit.md@bd7a3efcd`; `docs/analysis/b5/DEVIATION-LOG.md@bd7a3efcd`; `docs/run_reports/2026-11-07-b5-release-hold-trace.md@bd7a3efcd`.
- `scripts/release_b5.py@bd7a3efcd` :58, :76, :270, :340, :360, :428. `scripts/run_b5_analysis.py@bd7a3efcd` :100. `joulewise/b5_analysis/dry_run.py@bd7a3efcd` :177-213, :353-368, :388, :510-520. `configs/analysis/b5/dry_run_refusal_classes.json@bd7a3efcd`; `configs/analysis/b5/recompute_bars.json@bd7a3efcd`.
- Line counts: `wc -l` over the paths in section 1 at the two commits; test counts: `grep -c '^\s*def test_'`; live tails in section 1.4.

---

## Appendix B: seat 2 report (Opus 5.5), verbatim

The seat's TOP and OPEN lists and its report follow exactly as delivered to the synthesis. The headings below this line are the seat's own.

**TOP**

["R0's per-process 0.05 CPU-s/s contention refusal (QuietGuard on every check, plus the SMC CpuQuietProbe NotQuiet) stopped 4 of the 8 R0 attempts (re-runs 3-6). It required PR #691 (3 Sol builds, about 8 reviews) and the clean-gap scheduling rule, yet it protects no R0 output: the model checks are token and memory properties, and the SMC picks are PROVISIONAL (protocol v4:238-240; r0_host.py:491). R1's own rule is about 10x looser (0.5 cores for 60 s, then redo; align_r1_rehearsal.py:157-158). Simplify: flag it, or apply R1's ruling-8 redo to SMC only, and drop the clean-gap rule.","R0 case study: 33.2 h elapsed, 2.45 h of R0 execution, about 30.5 h of idle Mac. Of the 8 stops, 3 were real defects (launcher, prompt, classifier), 2 were miscalibrated guards (absolute NLL 3.0; an aggregate bar the idle Mac could not pass) and 3 were immaterial contention. Because of fail-fast plus SMC-first ordering, the ladder (which produces R0.reasoning_effort, the only R0 output R1 needs) has never run. Default to --keep-going and decouple the ladder from SMC.","The W1-under-High-Power host-restore stack (R5-6, R6-7, R7-4..11, R8-1..5, D8-1..5) is about 1,300 production lines and about 2,500 test lines. It accounts for 15 of the 28 unique HIGH/MEDIUM findings in R1 review rounds 4-8, and 10 of the 11 after round 5, including 2 regressions caused by its own fixes. The reviewers state 'neither can admit bad data'. It guards against a manual pmset restore that the admission read-back already makes fail-closed, and it changed run_night's shared interrupt semantics for every night class. Park it until R1 actually adopts High Power, or rule that W1 runs Automatic regardless.","Desk review rounds on code never run on hardware have low yield. The pre-R0 reviews foresaw 0 of the 8 field failures (1 adjacent). R1 has had 9 review rounds in about 31 h, added about 29.5k lines, and has zero hardware runs. gate_policy.md rule 2 (no mandatory review for code that cannot change a number) is not being applied, and rule 9's pruning tally appears in no session record.","Full-suite CI on the measurement lane takes 2-3 h per PR, mostly unrelated BYTES archive tests. That contributed to missing the 11-07 06:15 R0 gap (about 8.5 h more idle). Gate on the touched tier plus tests/align, and run the full suite post-merge.","Block 5 is already lean (DLE-1 release_b5.py at 506 lines; DLE-2 lean recompute production; r3 dry run 1 h 40 min against 37 h). What remains: freeze the heavy L9 audit (9.5k lines, import closure of about 220k lines, 41.7k test lines taking 22.7% of per-PR CI CPU) and run its tests only on path changes or nightly; delete the D-188 comparator (about 4k lines) at the release; delete --resume and --mode release at the block-6 boundary; consolidate about 6.6k lines of round-named tests.","Root pattern: 'fails closed' is treated as a free disposition, although on a 3-4 h or 15 h hardware slot each closed failure costs a slot plus a fix-and-review cycle. Ed's 10-05 doctrine ('physics refuses; everything else is a flag') is enforced only for the HAZARD_PACK scan list. joulewise/align is unscanned except powermode.py, which is how refusal creep entered R0."]

**OPEN**

["Will the lead rule that W1 runs in Automatic mode whatever R1's A-B-A says, keeping the A-B-A as a diagnostic? That would let the whole W1 High Power arming path be deleted rather than parked. Protocol v4 is an unregistered draft, and CHAIR 14 notes adoption rests on n = 1.","Should R0's SMC stage stop gating altogether, given that R1 re-selects on its own full-inventory capture with the same classifier (R0-L1)? R1's soak currently journals only R0's keys, so R0's picks are still used to configure R1.","If R0 re-run 8 is refused by contention in SMC again, does the lead accept running the non-SMC checks plus the offline thermometry composition (item 196), or relaxing the contention rule first?","DLE-2 open point: block 6's heavy audit is the only first-derivation check of anchors, fits and verdicts. Is a release held, or labelled provisional, if the audit has not finished? And is the heavy pipeline worth keeping at all, versus a smaller second derivation of those judgments?","Who reviews the blast radius of the R1 lane's run_night interrupt and lock semantics on BYTES and HAZARD nights when the measurement lane is merged back to main?","Should the R1 kit allow a patch night that re-runs only INCONCLUSIVE calibration segments, or U5 on 2 of 3 points, instead of a full 15-17 h R1 re-run?","Revive gate_policy rule 9's per-session pruning tally, or delete the rule? It has never been applied.","The Fable seat audited the same brief separately. Where its rankings differ from these (especially on the High Power stack and the B5 heavy-audit retention), the lead should reconcile them."]

**Report**

# Proportionality and pruning audit: Opus seat (2026-11-07)

**Scope.** I read the ALIGN v4 R0/R1/W1 machinery on `lane/2026-11-06-v4-r1-integrated@e901eb2a4`, with the measurement lane `lane/2026-11-05-align-pilot10-benign@5f817856b` as its base, and the Block-5 analysis and release tooling on `origin/main@bd7a3efcd`.

**Method.**
- Static reading, line counts, and an AST import-closure count.
- The `RUN_STATE.md` items and the R0 record branches `origin/records/2026-11-0[67]-align-r0-v4*` (their `report.json` files).
- The R1 review documents, LEAD-RULINGS-1 and -2, and the 2026-11-06 B5 care audit.
- 24 ALIGN test modules, run one per process under `nice -n 19 taskpolicy -b`, with TMPDIR and `JOULEWISE_HOST_STATE_DIR` under `/private/tmp/jwburn-opusprune`. No model weights were loaded.

**Blinding.** Nothing under `/Users/edr/jw-b5-*`, `night-*`, night-custody, night-archive or any `restricted/` directory was opened. No B5 outcome-bearing content was read or inferred. B5 items are cited by tooling state only.

**Housekeeping.** Both worktrees (`jw-wt/opus-prune-r1`, `jw-wt/opus-prune-main`) and the TMPDIR were removed. The timing table is kept at `/private/tmp/claude-501/-Users-edr-code-CapstoneProject-JouleWise/1544c617-26c5-454f-8287-04b93bf8aa23/scratchpad/opus-prune-test-timings.tsv`.

---

## 0. Headline

1. **The worst cost-to-protection ratio is R0's CPU-contention refusal.** It is a 0.05 CPU-s/s per-process bar, taken from the energy-window quiet rule and applied to a desk readiness check.
   - It stopped **4 of the 8 R0 attempts** (re-runs 3-6, i.e. runs 4-7).
   - It required PR #691: 3 Sol build rounds and about 8 reviews.
   - It forced the "clean gap" scheduling rule. Through the scheduling rule and the review gates it accounts for most of about 30 h of idle Mac time. Of the 33 h since R0 first launched, R0 has executed only about 2.45 h.
   - It protected no R0 output. Load, generated, memory, ladder and long-decode produce token counts or memory figures that background CPU cannot change.
   - SMC picks are labelled **PROVISIONAL** in code and protocol, because R1 re-selects.
   - R1's own contention rule is about 10x looser: 0.5 cores sustained 60 s, redo the segment (`scripts/align_r1_rehearsal.py:157-158` @e901eb2a4).
   - It violates Ed's standing doctrine "physics refuses; everything else is a flag" (`configs/gates/hazard_refusals.json:12` @e901eb2a4).
2. **The W1-under-High-Power host-restore stack costs most and protects least in R1.** This is R5-6, R6-7, R7-4..R7-11, R8-1..R8-5 and D8-1..D8-5.
   - **Size:** about 1,300 production lines across `powermode.py`, `run_night.py`, the R1 driver, the runtime and `align_v4_session.py`, plus about 2,500 test lines.
   - **Review share:** it accounts for 15 of the 28 unique HIGH/MEDIUM findings in R1 review rounds 4-8, and 10 of the 11 after round 5. Two of those findings were regressions introduced by the previous round's own fixes.
   - **The reviewers' own assessment:** "Neither can admit bad data". The round-8 review adds "neither is on the ALIGN W1 or R1 path as wired today" (`docs/align/reviews/2026-11-07-r1-round7-executing-review.md:11`, `…round8-executing-review.md:13` @e901eb2a4).
   - **What it buys:** it avoids a manual `pmset -c powermode 0` and one refused night after a SIGKILL. The admission read-back already fails closed (`LEAD-RULINGS-2.md:93`).
   - **What it costs:** it pushed new interrupt semantics into the shared `run_night` path that BYTES and HAZARD nights also use. One round-8 fix briefly made a TRANSACTION_PACK night unstoppable by signals (D8-1).
   - **Adoption is uncertain.** High Power is adopted only if the R1 A-B-A passes, with n = 1 per condition (CHAIR 14, 16).
3. **Desk review rounds on code that has never run on hardware have low yield.**
   - The pre-R0 reviews (WP7 executing review with three sub-reviewers, and the WP8 Fable cold pass) foresaw **0 of the 8 field failures**. One finding was adjacent.
   - R1 has had 9 rounds in about 31 h and **zero hardware runs**.
   - Rounds 4-5 found real number-bearing defects (U5 and β_T contamination, a turnless replay that falsely passed). After that the rounds reviewed the High Power stack and the previous round's fixes.
4. **R0 failed fast, so the one output R1 actually needs has never been produced.** That output is `R0.reasoning_effort`, which the ladder writes. It has not been reached in 8 attempts.
   - `keep_going=False` is the default (`joulewise/align/r0_runner.py:109,185` @5f817856b).
   - Since #692, SMC runs first (`:112`), and an SMC `fail` (NotQuiet) still stops the run (`r0_host.py:486` @5f817856b; only `pass`/`inconclusive` are accepted at `r0_runner.py:22-26`).
5. **The existing gate policy is not being applied, and its feedback loop never ran.**
   - `docs/process/gate_policy.md:26` (bd7a3efcd) says tooling and orchestration code that cannot change a number gets "CI and the change's own regression test. One reviewer only if the author asks."
   - In practice a one-line launcher fix (#684), a prompt-string fix (#687) and the whole High Power stack each got executing reviews plus cold passes plus 2-3 h of full CI.
   - Rule 9's per-session pruning tally (`:46`) appears in no session record. `rg caught_number` finds only the policy and the 10-27 audit.
6. **Block 5 has already absorbed most of the proportionality work.** DLE-1 adopted the lean release (`release_b5.py`, 506 lines). DLE-2 made the lean recompute production for blocks 6 and later. The r3 dry run takes 1 h 40 min against about 37 h for r1. What remains is mass, not ceremony:
   - The heavy L9 pipeline is now an audit. It is 9.5k lines with a static import closure of about 180 files and 220k lines, and its tests are 41.7k lines (1,707 tests, 38 MB of fixtures). Those tests still run on every PR: 62.6 of 276 CPU-minutes, 22.7 % of CI.
   - The D-188 equivalence comparator (2,145 lines plus 1,914 test lines) ends its job at the release.
   - About 6.6k lines of round-named tests should be consolidated.

---

## 1. Ranked prune list

Rank combines cost removed with protection lost. "Fired" means it fired in practice, with a citation.

| # | Item | What it protects | Fired in practice? | Cost today | Risk if removed or simplified | Recommendation |
|---|---|---|---|---|---|---|
| **1** | **R0 per-process CPU-contention refusal.** QuietGuard `_cpu_interval` on every check every 15 s (`joulewise/align/r0_host.py:66-282` @e901eb2a4). The SMC `CpuQuietProbe` NotQuiet, which exits 3 and becomes `fail` (`r0_host.py:486` @5f817856b). Both judge 0.05 CPU-s/s per contaminant (`joulewise/prewindow.py:5,31`). | Nominally R0 data quality. Real exposure: only SMC τ/t63 estimates, and those picks are PROVISIONAL (`docs/align/pilot_protocol_v4.md:238-240`; `r0_host.py:491` `selection_status: PROVISIONAL`). | **Yes, 4 of 8 stops.** Re-run 3: photoanalysisd burst (RS item 188, `RUN_STATE.md:1458`). Re-run 4: mdworker plus an aggregate bar that was "above 0.05 in 8 of 12 calls" on an idle Mac (item 189, `:1444-1450`). Re-run 5: softwareupdated scan at 0.0704 (item 193, `:1326-1334`). Re-run 6: `/tmp` cleaner at 0.0786 (item 194, `:1280-1287`). None was a defect. | #691 took 3 Sol builds, 2 Opus executing reviews (ADMIT), 3 Fable cold passes (ADMIT), then a laptop executing review, a cold review and a Sol critique (items 190, 192). It produced the clean-gap rule, which lost the 06:15 gap on 11-07 (`:1246`), and the timing-only relaunch ceremony. About 4.5 h of the Mac idle behind #691 alone (`:1387`, "Ed asked why the MBP is idle"). | A sustained heavy contaminant during the SMC capture could skew a provisional pick. The flag records it, and R1 re-selects on its own capture. | **Simplify.** (a) Remove the contention refusal from every non-SMC check, and keep the occupancy census (armed night, agent, other chain) only at check boundaries. (b) For SMC, adopt R1's ruling-8 rule (redo the stage on 0.5 cores sustained 60 s, at most once) or journal and flag only. (c) Then drop the clean-gap scheduling rule for R0. **Lead (engineering).** It changes no registered quantity. |
| **2** | **The W1-under-High-Power host-restore stack.** Host marker plus `night.lock`; `pass_fds` lock inheritance (R7-5); retake-before-restore; unproven-termination deferral (D8-2); signal latch; dead-man, J4 and session-start restores; install launchd census (R7-6); `HostStateOverrideRefused` (R7-10). Lives in `joulewise/align/apple/powermode.py` (515 lines), `scripts/run_night.py` (about 250 added lines: `_admit/_close/_restore_owed/_take_host_lock` at :4068-4344, plus interrupt termination at :1041), `align_r1_rehearsal.py` (`PowerModeGuard` :360, `_terminate` :262, `_stop_tree` :237), `r1_runtime.py` (`close_managed_session` :143, `Termination` :945, `stop_powermetrics_descendants` :1021) and `align_v4_session.py` (`install` :201). | Two things. No exit leaves the host at AC powermode 2. No restore happens under a chain that is still measuring. | **Never on hardware** (R1 has not run). `night_refused_ac_powermode` and `night_refused_host_lock_error` have zero mentions in the records. Every finding was desk-found. | About 1,300 production lines. Tests: `test_r1_round6_power` 409, `round7_power` 550, `round7_install` 149, `round7_close_deferral` 107, `round8` 609, `round8_exec_review` 324, `v4_powermode_record` 138, plus parts of the round-6 and round-7 executing-review tests. Those modules take about 214 s of the 747 s ALIGN test wall I measured. Three review rounds over about 9 h (11-06 23:23 to 11-07 08:04). A 56 KB contract doc. Two fix-induced regressions. A blast radius into the shared `run_night` (R8-1 covers the HAZARD_PACK chain too). | After a SIGKILL or power loss in a W1 High Power night, the host stays at mode 2 until the next activation. The next night then refuses on the admission read-back, which already fails closed (`LEAD-RULINGS-2.md:93`). A restore under a surviving chain affects only a night that has already aborted, whose data is never admitted (D8-4, `:659`). | **Delete or park** the W1-under-High-Power arming path until R1 actually adopts High Power. Keep: the admission read-back refusal; a best-effort `pmset 0` in the night's `finally`; the R1 chain EXIT trap (already unconditional per D8-4); and R8-1's "terminate the chain group on interrupt" (general supervision, small). Better still, rule now that **W1 runs Automatic whatever the A-B-A says**, and record the A-B-A as an R1 diagnostic (CHAIR 14: adoption rests on n = 1). **Lead (design).** Protocol v4 is "DRAFT SKELETON — PROVISIONAL; not registered" (`pilot_protocol_v4.md:3`), and power mode is not an item-181 escalation class. |
| **3** | **Review rounds on hardware-unrun, non-number code.** R1 rounds 6-8; the per-fix executing review plus cold pass on R0 tooling. | Defects before the first run. | Pre-R0 reviews: 0 of 8 field failures foreseen (WP7, `docs/align/reviews/2026-11-06-wp7-executing-review-pr682.md`; WP8). One was adjacent: WP7's MEDIUM on `generated` strictness. One foreseen R1 risk, the 100 ms coverage tolerance (R5-5, `LEAD-RULINGS-2.md:64-80`), was dispositioned "fails closed, check on the first R1 night". It then cost R0 re-run 7 and #692. | R1: 9 rounds in about 31 h. 120 commits and about 29.5k lines on top of the measurement lane (+9,662 code, +11,188 tests, +7,504 docs). | Defects in infra code surface on the first night instead of at the desk. R0's history says they do anyway. | **Simplify.** Apply `gate_policy.md` rule 2 as written. Add a rule: after one number-bearing review round, no further desk round on a measurement component until it has run once on hardware. Revive rule 9's tally or delete it. **Lead (process).** |
| **4** | **R0 fail-fast plus SMC-first ordering** (`r0_runner.py:109,112,185` @5f817856b). | Not running later checks on a broken stack. | Every run stopped at its first failure. Ladder and long-decode **never ran** (all 8 `report.json` files on the records branches). | One defect found per 3-4 h slot. Re-run 1's load fail hid re-run 2's prompt defect, and so on. | A later check runs on a stack with a known earlier failure, at the cost of some wasted minutes. Prerequisite gates still apply under `--keep-going` (`:293`). | **Simplify.** Default `--keep-going` for R0 desk runs. Run ladder and long-decode independently of SMC (SMC as a diagnostic stage, or last). **Lead (engineering).** |
| **5** | **Full-suite CI as the merge gate on the measurement lane.** | Cross-module regressions. | CI catches exist, but none on the R0 fixes are recorded. | "Shard 5 takes about 2-3 h on this lane because of BYTES archive tests" (`RUN_STATE.md:1260`). "The lane's CI takes about 2.5 h" (item 186). "Shards take 20 min to 2 h 16 min" (`:1424`). It contributed to missing the 06:15-11:05 gap on 11-07 (`:1246`). The next usable gap was 17:15, about 8.5 h later. | A cross-module break lands on the lane and is caught post-merge within hours. Measurement-lane code is isolated from main. | **Simplify.** Gate on `scripts/quick_suite.py --tier touched` plus `tests/align`. Run the full suite post-merge or nightly as non-blocking, and revert on red. **Lead (engineering).** |
| **6** | **The kit refuses W1 on any INCONCLUSIVE R1 calibration segment** (`scripts/align_v4_kit.py:194-208` @e901eb2a4). The remedy is a full R1 re-run. | U5 and β_T get all three designed start-state points. | Not yet; R1 has not run. The physics input says G0 settles at 840-1,040 s against the 600-1,200 s caps (`LEAD-RULINGS-2.md` Round 7 physics input), so a timeout is plausible. | A full 56,207-61,607 s night re-run (item 202, `RUN_STATE.md:1055`) for one missing segment. | U5 with two points is weaker. A patch night must re-check the soak reference. | **Simplify.** Allow a patch night that re-runs only the INCONCLUSIVE segments against a fresh soak, or U5 on 2 of 3 points with a recorded flag. **Lead (design).** |
| **7** | **Worst-case night-length tables recomputed to 4 decimals every round** (R6-8, R7-9, R8-4, D8-3; `night_worst_case_s` and `segment_bounds`). | Sizing the R1 `window_max_s` and the batch-window admission. | n/a | A table in every round, plus a test per table (`test_r1_round7_science.G0TimeoutTests`). Item 202 already accepts a cut beyond 90,663 s. | A generous `window_max_s` could, in theory, let a stuck night run long. The member deadmen bound that anyway. | **Simplify.** Fix `window_max_s` at a generous constant (for example 24 h). Keep the batch-window wait; drop the per-round tables. **Lead.** |
| **8** | **Kit re-derivations that import the runtime's own functions** (R9-2 `rederive_r1_pick_s7`, `check_duty_bar_consistency`; `align_v4_kit.py:355,381`). | A hand-edited or stale `r1_slots`. | No | Code and tests, at about 0 runtime. | Tampering is out of the threat model (D-161: "tamper-EVIDENT … not tamper-PROOF"). Staleness is covered by the `rule` and schema version check. | **Simplify.** Keep the schema and `rule` checks; drop re-derivation through identical functions. Low priority. |
| **9** | **Round-named regression tests.** ALIGN: `tests/align/test_r1_round{5..8}*` (11 files, 3,453 lines, 145 tests). B5: `tests/independent_recompute/test_rc_cmp{7..11}`, `test_round3`, `test_review_fixes`, `test_auditfix` (4,714 lines, 206 tests). `tests/b5_analysis/test_vdl_sol_hunt*` and `_w2` (1,895 lines, 63 tests). | Regressions of review findings. | They pass. | Maintenance load. Overlapping fixtures. Hard to see what behaviour is pinned (for example R7-4's signal tests were partly superseded by R8-1). | Losing a pin during consolidation. | **Simplify when touched.** Fold them into behaviour-named modules; delete pins of superseded behaviour. Low urgency. |
| **10** | **B5: the heavy L9 pipeline on per-PR CI, and further speedup work on it.** `tests/b5_analysis` (41,734 lines, 1,707 tests, 38 MB fixtures) takes 62.6 of 276 CPU-minutes in `scripts/test_timings.json` @bd7a3efcd. Speedups continue on `lane/2026-11-06-b5-under-90` (`docs/analysis/b5/DEVIATION-LOG.md:200-212`). | That the audit pipeline keeps working. | The tests catch drift only when `joulewise/b5_analysis/**` changes. | 22.7 % of CI on every PR, repo-wide. Agent time on a path that is now off the critical path (DLE-2 item 3, `DEVIATION-LOG.md:155`). | The audit breaks silently between blocks. Mitigated by running its tests on a path filter, on a tag, or nightly. | **Simplify.** Freeze at `b5/analysis-r3`. Run `tests/b5_analysis` only when its paths change, plus nightly. Stop speedup work. Keep the pipeline itself as the block-6 audit (DLE-2's open point: it is the only first-derivation check of anchors, fits and verdicts, `:188`). **Lead (engineering).** |
| **11** | **B5: D-188 equivalence comparator** (`tools/b5_equivalence/compare_b5_results.py`, 2,145 lines; `tests/b5_analysis/test_result_equivalence.py`, 1,914 lines, 98 tests). | That the restructured r2/r3 pipeline equals the r1 oracle. | Yes. It found the composite-digest difference that #643 fixed (RS item 165). | About 4k lines; minutes per use. | None after the release. D-188 says "the reference stays the oracle until the block-5 release" (care audit row 17, `docs/run_reports/2026-11-06-b5-care-audit.md:80`). | **Delete at the B5 release.** Keep it until then. |
| **12** | **B5: `--resume` (`joulewise/b5_analysis/resume.py`, 501 lines, plus 742 test lines) and `--mode release`** (`scripts/run_b5_analysis.py:18`; `dry_run.py:2136-2273`). | Losing a 27-37 h run; a second heavy determinism run. | Resume: no recorded use in the items read. Release mode: superseded by DLE-1 (`CANONICAL.md:47`). | Code and tests. | Losing a 1 h 40 min run now costs 1 h 40 min. | **Delete at the block-6 boundary**, or keep frozen. Low priority. |
| **13** | **R0 launch ceremony.** Manual canonical fast-forward, desk-fence tests, hw.model, RAM, venv print, Spotlight STOP/CONT check, preflight, battery float, stopping the Codex adapter (items 176, 195). | That the launch environment is what was approved. | The launch-time agent census caught an orphan Codex app-server (item 177). Spotlight STOP/CONT is now a no-op because indexing is off (item 201). | Magistrate tokens on every launch; error-prone hand steps. | Little, if folded into code. | **Simplify.** Fold the checks into `scripts/launch_align_r0.py preflight`. Drop the Spotlight step once indexing stays off. |

Not on the list, because they earn their cost (section 6):
- R0's model-load, load-reference, generated and classifier verdicts;
- the agent and occupancy census;
- the battery float check;
- the external-volume census;
- the batch-window wait;
- R1 science checks of the round-4/5 kind;
- B5 blinding layers, seal pins, the step-0 census, the lean recompute, the comparator and `release_b5.py`.

---

## 2. Case study: R0's history (8 stops; re-run 8 is due at or after 17:15 PST on 11-07)

Source: `RUN_STATE.md` @bd7a3efcd, items 176-202. Each attempt's `report.json` on `origin/records/2026-11-0[67]-align-r0-v4*`. I read the status, `stopped_after`, `total_seconds` and census-receipt counts.

| Run | Start (PST) | Record | Stopped at (wall) | Cause | Guard class | Was the stop right? | Fix and its gates | Mac idle until the next launch |
|---|---|---|---|---|---|---|---|---|
| 1 | 11-06 08:05 | `records/2026-11-06-align-r0-v4` | model-load **fail** (21 s) | Launcher `Path.resolve()` ran the bare Homebrew python, which has no mlx (item 178) | crash, not a guard | Real defect | #684 (one line): Sonnet executing review, CI 20/20, gate ledger | about 1 h |
| 2 | 09:03 | `…-rerun` | load **fail** (76 s) | Absolute NLL ≤ 3.0 is invalid for D. Upstream HF fp32 also scores 11.06 (items 182, 184) | miscalibrated guard | **False refusal** (the diagnosis was valuable) | #686 reference equivalence; HF diagnosis lane; executing review, Fable cold pass, CI on 30 jobs, merge-gate doc; mail to Ed | about 5.5 h |
| 3 | 14:34 | `…-rerun2` | generated **inconclusive** (160 s) | The echo prompt did not state the call count (item 186) | harness defect | Real (our fixture) | #687, a prompt string: Sol executing review, Fable cold pass (M1/L1/L2), merge-gate doc, about 2.5 h of CI | about 3 h |
| 4 | 17:33 | `…-rerun3` | QuietGuard **refused** mid-`generated` (158 s) | photoanalysisd respawn burst (about 0.6 CPU-s) on a single %CPU snapshot (item 188) | contention | True contention, **zero effect** on a token check | SIGSTOP photoanalysisd | 14 min |
| 5 | 17:50 | `…-rerun4` | QuietGuard **refused** at the start of smc (905 s, 101 census receipts) | An mdworker spawn. Also the SMC probe's host-aggregate bar of 0.05, which "on the idle Mac was 0.035-0.112, above 0.05 in 8 of 12 calls" (items 189, 190) | contention | The aggregate bar was **unpassable**; the per-process part was trivial | #691: 3 Sol builds, Opus executing reviews ×2, Fable cold passes ×3; then a laptop executing review, a cold review and a Sol critique; CI | about 4.5 h |
| 6 | 22:32 | `…-rerun5` | smc NotQuiet → **fail** (2,246 s) | softwareupdated 6-hourly scan, 0.0704 CPU-s/s for 36 s (item 193) | contention | "real, measured contention" but immaterial to a 900 s full-load step | timing only | 9 min |
| 7 | 23:18 | `…-rerun6` | smc NotQuiet → **fail** (2,470 s) | 00:00 `/tmp` cleaner, `find` at 0.0786 (item 194) | contention | Same | Third consecutive failure, so mail to Ed; "go"; timing | 11 min |
| 8 | 11-07 00:11 | `…-rerun7` | smc **inconclusive** (2,789 s) | `Coverage` 100 ms tolerance threw away about half the reads. With that fixed, the picks were power-gated placeholders on an unsettled baseline (item 195) | classifier | **Correct and valuable**: it prevented physically wrong picks | #692: 2-seat consult, 3 fresh designs, reconciliation, build, cold passes ×2, deltas ×2, an Erratum-4 Sol round plus delta, Erratum 5; 2-3 h of CI; merged 08:45; missed the 06:15 gap | about 16.3 h (to 17:15) |

**Totals.**
- Elapsed from 08:05 on 11-06 to 17:15 on 11-07: about 33.2 h.
- R0 executed 8,825 s, about 2.45 h. The Mac sat idle about 30.5 h.
- Of the 8 stops: 3 found real defects in our code or harness (runs 1, 3, 8); 2 were miscalibrated guards (run 2, and run 5's aggregate bar); 3 were true but immaterial contention (runs 4, 6, 7, plus the per-process part of run 5).
- The only output R1 consumes, `R0.reasoning_effort`, has not been produced: the ladder never ran.

**Counterfactual (an estimate, not measured).** With rules 1, 4 and 5 above:
- Runs 4-7 would not have stopped.
- Run 5's SMC capture at 17:50 would have reached the classifier, so run 8's coverage defect would have surfaced at about 18:40 on 11-06 instead of 00:58 on 11-07.
- #691 would not have been needed for R0. Its background-sampler deferral is already marked "required before W1, not for R0" (item 192).
- `--keep-going` would have run `generated` (run 3's defect) in run 2's slot.
- Touched-tier CI would have allowed a launch at about 06:30 on 11-07.
- My estimate is that 15-20 h of Mac idle could have been avoided, with R0 done on the morning of 11-07.

**Pattern.**
- Each guard was locally defensible. It was ported from the energy-window rules, or added "fail closed".
- Nobody asked what output it protects. "Fails closed" was accepted as a free disposition.
- On a measurement Mac where a run takes 3-4 h, every fail-closed stop costs a slot plus a fix-and-review cycle.
- The doctrine that already answers this ("physics refuses; everything else is a flag", 2026-10-05) is enforced mechanically only for the HAZARD_PACK scan list. `joulewise/align/**` is not scanned except `powermode.py` (`configs/gates/hazard_refusals.json` `scan.modules`). That is how refusal creep entered R0 unchecked.

---

## 3. ALIGN R1/W1 machinery

### 3.1 Review-round yield (R1 integration line, rounds 4-9; review docs @e901eb2a4)

| Round (11-06/07) | Reviews | Science or estimand findings | Ops (fail-closed cost) | High Power / signal / lock | Doc |
|---|---|---|---|---|---|
| 4 (13:35-18:22) | executing, Fable cold | exec HIGH-1 (an incomplete planning-turn energy enters β_T/U5); exec HIGH-2 (a turnless replay gives a false U5 PASS); cold HIGH-2 (a warm self-reference makes the duty bar uninformative); exec M2 = cold M2 (B_D and policy unbound) | exec M1, M4; cold M3 | exec M3 | cold M1 |
| 5 (19:46-22:02) | cold, executing, Sol critiques | cold M3 (changed picks); exec M2 (the duty bar's G0 is not W1's); exec M5 (1(f) decode rate) | exec M1 | cold M1, M2; exec M3, M4 | |
| 6 (23:23-02:43) | cold, executing | cold M1 (U5 pair predecessors) | | exec M1-M4 | |
| 7 (03:42-05:49) | cold, executing | | | cold M1; exec M1, M2, M4 (M3 = cold M1) | |
| 8 (06:18-08:04) | executing, Sol critique | | | exec M1 (introduced by the round-8 Sol latch fix); exec M2 (exposed by that fix) | |
| 9 (10:35) | integration-driven | R9-1, R9-2 (classifier fidelity) | | | |

**Unique HIGH/MEDIUM findings across rounds 4-8:** 8 science, 4 ops, 15 High Power/signal/lock, 1 doc. After round 5 the split is 1 science and 10 High Power. The science catches in rounds 4-5 were real and number-bearing; that is the review type to keep. The High Power stream did not converge: each round's fix created the next round's findings (round-7 exec M1, round-8 exec M1 and M2).

### 3.2 Size (e901eb2a4)

| Subsystem | Production lines | Test lines / tests | Notes |
|---|---|---|---|
| R0 desk (`r0*.py`, `smc_enumeration.py`, scripts) | 3,175 | 4,799 / 265 | Plus the launcher on main: `scripts/launch_align_r0.py` (306) and `run_align_r0_launchagent.sh` (91) |
| R1 runtime, driver, powermode, chain | 4,839 | 6,882 / 287 | 3,453 lines and 145 tests are round-named |
| v4 kit, session, prequal, W1 tools | 4,324 | 3,721 / 218 | `align_v4_kit.py` 1,340 lines, 109 raise sites |
| `run_night.py` (shared by every campaign) | 5,797 (main: 5,242) | 7,587 / 325 | 101 raise sites |
| Thermal gates and desk | 1,871 | 1,641 / 86 | |
| R1-lane docs (rulings, contract, protocol, R1 reviews, integration report) | 6,246 doc lines | | Contract 56 KB; LEAD-RULINGS-2 85 KB; integration report 102 KB |

Measured test wall (Air, background QoS, 24 modules, all passing): **747 s** in total. The largest were:
- `test_r1_runtime_e2e` 160 s
- `test_r1_runtime` 139 s
- `test_smc_classifier_v4` 72 s
- `test_r1_round8` 58 s
- `test_r0_host` 49 s
- `test_r1_round8_exec_review` 45 s
- `test_r1_round7_power` 44 s

The round-named and powermode modules alone took 214 s.

### 3.3 The High Power stack: protection against cost

- **The failure it prevents.** A W1 night under mode 2 dies without its close, and the host stays at 2. Without the stack, the next night's admission reads the mode and refuses (`night_refused_ac_powermode`). That fails closed and needs one `sudo -n pmset -c powermode 0` (R5-6 builder report, `LEAD-RULINGS-2.md:93`).
- **Its second purpose.** No restore under a surviving chain. Such a chain belongs to a night that has already aborted, and its data is never admitted (D8-4).
- **The R1 chain already bypasses it.** The R1 chain's zsh EXIT trap runs `pmset 0` without the lock or proof anyway (D8-4, `:659`). So for R1 the elaborate deferral protects only the driver's own restore.
- **Adoption is a coin flip on n = 1.** High Power is adopted only if t_decline(B) ≥ 1.25 × max(A1, A2) and the A legs agree within 25 % (CHAIR 16). Otherwise everything W1-side is dormant.
- **Keep:** the admission read-back; a close-time best-effort restore; R8-1's process-group termination on interrupt (it closes a real unsupervised-chain gap); the R1 EXIT trap.
- **Delete or park:** the host lock and `pass_fds` inheritance; retake proofs; ownership semantics; dead-man, J4 and session-start restores; `HostStateOverrideRefused`; the install launchd census specific to High Power; the descendant-identity tree proof in the R1 driver.

### 3.4 Other R1 guards

| Guard | Verdict | Why |
|---|---|---|
| Ruling 8 OS-load redo (0.5 cores sustained 60 s, 2 redos; `align_r1_rehearsal.py:157-159,878-911,1050-1107`) | **Keep** | Proportionate, and the model R0 should copy. |
| Batch-window wait 11:45-13:15 (`:94,980`) | **Keep** | Backed by the 12:53 maintenance cost (RS item 17). |
| Kit `--check` regenerate-and-compare | **Keep** | Cheap; catches stale kits. |
| R6-2 G0-timeout retry, then INCONCLUSIVE | **Keep**, but see prune item 6 | |
| External-volume census (ruling 20) | **Keep** | The SSD-on-bus rule. |
| `night_worst_case_s` per-round tables | **Simplify** (item 7) | |
| Kit re-derivation via runtime functions | **Simplify** (item 8) | |

---

## 4. Block-5 analysis and release tooling (origin/main @bd7a3efcd)

| Component | Production lines | Static import closure | Tests | Status |
|---|---|---|---|---|
| Heavy L9 (`joulewise/b5_analysis/**` plus `scripts/run_b5_analysis.py`) | 9,526 | about 180 files, about 220k lines (upper bound: includes lazy imports such as `arm_readiness`, `run_campaign`, `whole_window`) | 41,734 lines / 1,707 tests; 38 MB fixtures | Audit-only from block 6 (DLE-2, `DEVIATION-LOG.md:140-198`) |
| Lean recompute (`scripts/independent_recompute_b5.py`) | 3,255 | 1 file, standard library | shared below | Production from block 6; coverage additions owed (`LEAN-COVERAGE-AUDIT.md`) |
| Comparator (`scripts/compare_b5_recompute.py`) | 4,105 (larger than what it checks) | 1 file | 9,687 lines / 456 tests for recompute, comparator and release together; 4,714 lines / 206 tests are round-named | RC-CMP-1 to -11. The false-agreement class went to Ed on its third appearance (RS items 97, 99); RC-CMP-9 made it structural |
| Release (`scripts/release_b5.py`) | 506 | 1 file | `test_release_b5` 27 tests | DLE-1. Holds on one structural cause under blind probe (RS item 197) |
| D-188 equivalence (`tools/b5_equivalence/`) | 2,145 | 1 file | 1,914 lines / 98 tests | Retire at the release |

**Refusals fired in practice (tooling only):**
- attempt A: a step-0 false positive, `reader_record_not_structure_only` (RS item 95; care audit row 21);
- attempt B: step-4 classifier stops, ruled tooling (items 103, 126-133). This led to L9-STEP4-1, -2 and -3: the classifier was made total;
- step 5: the origin-containment check forced merge-then-fetch (items 108-109);
- attempt D: ENOSPC after 18.5 h. That was harness, not a guard (item 165);
- attempt E and candidate 1: step 9b `unclassified_refusal`, leading to D-189 and D-190 (item 165);
- the release check hold (item 197).

That is roughly 5-6 of the 191 registered tooling codes. Each fire was a genuine tooling defect the R3 loop is meant to surface. The registry is cheap: **keep**.

**What the care audit already settled.** It inventoried 26 layers (`docs/run_reports/2026-11-06-b5-care-audit.md:58-89`).
- Adopted: DLE-0 (no results cold gate), DLE-1 (lean release) and DLE-2 (lean production).
- Not adopted: its drafts DLE-3/4/5. They are moot because the heavy pipeline is off the critical path (`DEVIATION-LOG.md:200-212`).
- The log's own DLE-3 (analysis r3) brought the dry run to 1 h 40 min.

**What is left to prune:** items 10, 11, 12 and part of item 9 in section 1. Do **not** touch:
- blinding (care audit row 21: about 0 cost, with an incident record);
- seal pins (row 15);
- the step-0 census (row 14);
- the recompute plus comparator release condition;
- the float-token scan in `release_b5.py`.

---

## 5. Process findings (cross-cutting)

1. **"Fails closed" is used as a free disposition.**
   - Examples: R5-5's coverage risk, R6-7's consequence note, R7-5's orphan acceptance and D8-6.
   - On a Mac where a run takes 3-4 h, or a night 15 h, a closed failure costs a slot plus a fix cycle.
   - Proposed rule: a fail-closed disposition must state the expected cost in slots, and it is allowed only for physics or number integrity, per the 10-05 doctrine.
2. **Cross-lane propagation failed.** The R1 lane foresaw the 100 ms `Coverage` tolerance on 11-06 at about 19:00 (R5-5). R0 hit it at 00:58 on 11-07 on another lane.
   - Cheap fix: when a review flags a shared-module hazard (here `thermal.Coverage`), it opens an item on every lane that imports that module.
3. **The gate policy is over-applied, and its self-pruning tally is dead.** `gate_policy.md:26` (rule 2) and `:46` (rule 9). See prune item 3.
4. **Shared-code blast radius.** The R1 High Power work changed `run_night`'s interrupt semantics for every night class (R8-1: "covers the HAZARD_PACK chain too"). D8-1 then had to repair a TRANSACTION_PACK signal swallow that a round-8 fix created. Merging the measurement lane back to main will carry this.
5. **Hardware first.** Every R0 defect that mattered came from running. R1 should arm as soon as R0 passes; item 202 already allows this. Freeze non-number desk review on R1 until its first night's report exists.

---

## 6. Keep list (with the evidence that earned it)

- **Agent and occupancy census.** Item 158 (arm refused, agent present); item 67 (BY-H2 refused at t0); item 78 (night aborted, agent present); item 177 (an orphan Codex daemon caught before R0).
- **Battery float.** Pilot 10 battery top-ups (item 175); `night_refused_battery_float` appears in records.
- **R0 model-load, load-reference, generated and SMC classifier verdicts.** Runs 1, 2, 3 and 8 all found real problems. The classifier's refusal prevented placeholder picks (item 195, Opus HIGH on #692).
- **The WP18 fixture tool's refusals.** They caught a real seed-index bug (item 194).
- **R1 science review of the round-4/5 kind.** U5 and β_T contamination; a false U5 PASS.
- **R1 ruling-8 redo, the batch-window wait, the external-volume census, kit `--check`.**
- **B5:** blinding layers, seal pins, the step-0 census, the lean recompute and comparator, `release_b5.py`, the refusal registry and R3 loop, the kept-unit tripwires, the checkout and custody preflights.
- **`run_night` window deadline and process-group termination.** This includes R8-1's interrupt termination, which is general supervision.

---

## 7. Evidence index (all repo paths at the named commits)

**RUN_STATE.md @bd7a3efcd**
- :1045 item 202 (R1 kit, worst case at :1055)
- :1130 item 196 (R0-L1, PROVISIONAL)
- :1154-1279 item 195 (run 8, #692 rounds; gap missed at :1246; CI at :1260)
- :1280 item 194
- :1326 item 193
- :1355-1395 item 192 (#691 reviews; the Mac idle at :1387)
- :1411 and :1444 items 190 and 189
- :1458 item 188
- :1486 item 186
- :1548 item 182
- :1558 item 181 (escalation classes)
- :1591 item 178
- :1002 item 165
- :1124-1125 item 197 (r3 1 h 40 min; release hold)

**ALIGN code @e901eb2a4**
- `joulewise/align/r0_host.py:66` (QuietGuard)
- `scripts/align_r1_rehearsal.py:157-159,878,1050-1107`
- `scripts/align_v4_kit.py:179-300`
- `joulewise/align/apple/powermode.py`
- `scripts/run_night.py:1041,4068-4344,5031`
- `docs/align/pilot_protocol_v4.md:3,238-240`
- `docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-2.md:81,93,236,385,489,613,659`
- `docs/align/reviews/2026-11-07-r1-round7-executing-review.md:7-14`
- `docs/align/reviews/2026-11-07-r1-round8-executing-review.md:13-16`
- `docs/align/reviews/2026-11-06-wp7-executing-review-pr682.md`
- `configs/gates/hazard_refusals.json:12`
- `joulewise/prewindow.py:5,31`

**Measurement lane @5f817856b**
- `joulewise/align/r0_runner.py:22-26,109,112,185`
- `joulewise/align/r0_host.py:486,491`

**R0 records:** `origin/records/2026-11-06-align-r0-v4{,-rerun,-rerun2}` and `origin/records/2026-11-07-align-r0-v4-rerun{3..7}`, `docs/align/r0/*/report.json`.

**Main @bd7a3efcd**
- `docs/process/gate_policy.md:26,28,35,46`
- `CANONICAL.md:47-50`
- `docs/run_reports/2026-11-06-b5-care-audit.md:58-89`
- `docs/analysis/b5/DEVIATION-LOG.md:140-212`
- `scripts/test_timings.json`
- `scripts/release_b5.py`, `scripts/run_b5_analysis.py:18`

No external sources were used.
