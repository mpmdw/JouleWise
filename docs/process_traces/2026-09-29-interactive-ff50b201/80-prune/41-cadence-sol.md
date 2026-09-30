```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"CADENCE-AUDIT: fixed spacing and serial ceremony dominate elapsed time; estimator cap and clock corrections halved derivation yield.",
  "workspace":{"base_requested":"main","base_mode":"exact","head_start":"32ff901374024defa97fc3d137c5a699423676e7","head_end":"32ff901374024defa97fc3d137c5a699423676e7","upstream_end":"32ff901374024defa97fc3d137c5a699423676e7","branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"findings":[{"id":"F1","severity":"should_fix","title":"Calendar spacing lacks a measured recovery justification in the inspected records"},{"id":"F2","severity":"should_fix","title":"Estimator cap and network-time corrections caused all twelve derivation losses"},{"id":"F3","severity":"should_fix","title":"Repeated full harvest gates and supervisor ceremony serialize collection"},{"id":"F4","severity":"should_fix","title":"Harvest admission, diagnostic retention and issued claim authority are different endpoints"}]},
  "verification":[{"id":"V1","kind":"inspection","cmd":"git status --short --branch","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)"]},"expected":{"exit_code":0,"tail_regex":"^## HEAD \\(no branch\\)$"}},{"id":"V2","kind":"inspection","cmd":"git rev-parse HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["32ff901374024defa97fc3d137c5a699423676e7"]},"expected":{"exit_code":0,"tail_regex":"^32ff901374024defa97fc3d137c5a699423676e7$"}}],
  "flags":[{"id":"R1","kind":"verification_gap","level":"nonblocking","text":"Some phase boundaries survive only as commit timestamps or approximate narrative times; these are marked estimates. No new measurements or tests were run.","needs":""}]
}
```

CADENCE-AUDIT

## Findings

**F1 — Six-hour spacing is policy.** The registration requires it, but the inspected records provide no measured thermal, battery or clock recovery requiring six hours. Change it prospectively; the existing W1/W2 registration remains fixed.

**F2 — The losses have identifiable causes.** W1/W2 attempted 24 captures and retained 12: eight estimator-cap failures and four clock failures attributed to network-time corrections. Improving scheduling alone does not cure these losses.

**F3 — Routine collection is serialized behind development ceremony.** The two harvest commits spent approximately 77 and 73 minutes reaching main, including full suites, review lenses and cold final passes. Reuse reviewed machinery and keep per-window checks executable.

**F4 — “Admitted number on main” needs three separate counters.** W1/W2 harvest pins and battery verdicts reached main; the issued 25G83 calibration did not. The pilot retained diagnostic envelopes, but its quiet-machine result was inconclusive or contaminated, and both results pushes failed.

Times below are PDT. **E** means estimate or commit-time proxy, not a measured task duration. Parallel phases overlap; do not sum their rows.

| Phase | W1 | W2 | 09-22 qpe01 pilot |
|---|---|---|---|
| Decision / registration edits | Shared earliest located Rev-5 draft commit: **09-25 05:56:26**; seal 13:55:26: **479 min E** | Same prospective registration | First preparation located at **01:36**; earlier decision time unlocated |
| Brief / arm-script preparation | 09-25 14:02:56 brief → 15:38 scripts: **95 min E**; battery amendment committed 17:21 | Scripts adapted by 09-27 03:22:31; separate preparation duration unrecorded | After first harvest, clock/start-drift repairs and gates; 10:02 activation → 20:00 second preparation: **598 min elapsed**, mixed work |
| Required machinery / readiness | Battery-verdict machinery merged ≈09-26 08:25; development continues overnight | W1 pin must first merge | A267/A269 transaction merged 15:50; replay machinery merged 16:45; feeder correction merged 17:37 |
| Interactive-session obstruction | Observed 08:30; gone 22:13: **823 min E** | S1 child had to finish before publication; attributable delay not separately timed | Fresh-supervisor refusal at ≈20:00 caused handoff to next activation |
| Fresh supervisor | Unblocked 22:13 → arming activation 22:34: **21 min elapsed** | Existing 03:05 activation performs arm | 20:05 exit → 20:08:07 successor: **≈3 min E** |
| Pre-arm triple audit #416 | **Not performed:** explicitly removed as W1 prerequisite on 09-25 | **Not performed:** belongs after issuance and pipeline freeze | Not a recorded pilot gate |
| Arm steps 0–3 | 22:34 → arm packet committed 23:09:03: **35 min E**, including stale-ledger/script repairs and three approval exchanges | W1 merge 04:26:35 → packet 04:29:40: **3.1 min E** | First check 01:59:40–42; second check 20:10:35, notice/veto/install through 20:12:53 |
| Cold Fable arm gate / lens | Packet 23:09:03 → notice 23:14:55: **≤5.9 min E**; Fable ARM and Opus ARM, overlapping | Packet 04:29:40 → notice 04:36:39: **≤7.0 min E**; same two lenses | Second replay cold gate **19:51–19:57: 6 min**; no distinct per-arm Fable gate recorded |
| Arm notice email | Accepted **23:14:55** | Accepted **04:36:39** | First ≈02:00; second ≈20:11:30 |
| Notice → publication | Published **23:15:47.31: 0.87 min**; verified armed 23:16:40 | Published **05:54:46.39: 78.1 min** | First 02:01:16–20; second 20:12:28, **≈1 min** after notice |
| Publication → t0 | →09-27 **00:30: 74.2 min** | →**09:00: 185.2 min** | First →02:17: **15.7 min**; second →21:00: **47.5 min** |
| Network-time OFF / OFF settle | **Absent; network time remained ON** | **Absent; network time remained ON** | First OFF precondition absent; second OFF **21:00:01.77**, then shared settle |
| Quiet settle | 00:30:03–00:40:03: **10 min** | 09:00:05–09:10:05: **10 min** | **10 min** each; no additional separate OFF wait recorded |
| Capture span | d01 00:40:03 → d12 end 02:33:41: **113.6 min** | 09:10:05 →11:03:44: **113.7 min** | First ≈02:27–04:27: **120 min**; second ≈21:10–23:13:51: **123.8 min** |
| Chain / driver verdict | GO **02:33:42**; whole driver span **123.7 min** | GO **11:03:45**; whole driver span **123.7 min** | First GO 04:27:11.85; second GO 23:13:52.76; chains **130.2 / 133.8 min** |
| Results publication / courier | Push 02:33:50; courier **02:34:46** | Push 11:03:53; courier **11:05:03** | Both pushes failed: twelve raw files each >100 MB; courier **04:31 / 23:19** |
| Courier → harvest | →03:05 activation: **30.3 min** | →11:38 harvest: **33 min E** | →04:59 / 23:41 preservation: **≈28 / 22 min E** |
| Preservation / uninstall / verdict | 03:05 → pin/verdict commit **03:09:42: 4.7 min E**; admitted by record 03:11:51 | Harvest 11:38 → commit **11:39:30: 1.5 min E**; admitted by record 11:41:49 | First copy 04:59:28–35, uninstall 04:59:32; second copy ≈23:41, uninstall 23:42:02 |
| Harvest PR lenses | Brief 03:13:52 → reports 03:21:03: **7.2 min E** | Brief 11:42:24 → reports 11:59:54: **17.5 min E** | Diagnostic harvest records; no successful results-harvest PR recorded |
| Harvest cold final pass | Charge 03:21:03 → recorded ruling 03:32:49: **11.8 min E** | Charge 12:00:23 → recorded ruling 12:09:32: **9.2 min E** | First diagnosis received blind Fable confirmation; separately timed duration unavailable |
| Suite / hosted gates / merge | Interpreter failures required rerun; PR **#432 merged 04:26:35**, `a71a5e79`; commit→main **76.9 min** | Suite **≈68 min** under contention; PR **#434 merged 12:52:25**, `b69c39eb`; commit→main **72.9 min** | Records committed 05:09 / 23:55; raw-results publication remained blocked |
| Issued-number endpoint | Together with W2, supplies 12 candidate members | Custody repair #436 merged **16:23**; candidate produced **16:25:42–16:26:39**; science gates followed; D-138 later stopped, **unmerged** | No admitted quiet-machine claim number |

Timeline sources: [W1 arm record](/Users/edr/code/JouleWise-wt-cadence-ff50b201/docs/process_traces/2026-09-26-activation-22784e38/00-activation-record.md), [W1 harvest/W2 arm](/Users/edr/code/JouleWise-wt-cadence-ff50b201/docs/process_traces/2026-09-27-activation-3ba66eeb/00-activation-record.md), [W2 harvest](/Users/edr/code/JouleWise-wt-cadence-ff50b201/docs/process_traces/2026-09-27-activation-77b1bee2/00-activation-record.md), [issuance record](/Users/edr/code/JouleWise-wt-cadence-ff50b201/docs/process_traces/2026-09-27-activation-d528efb2/00-activation-record.md).
Pilot sources: [first arm](/Users/edr/code/JouleWise-wt-cadence-ff50b201/docs/process_traces/2026-09-22-activation-dc2237d5/01-first-live-arm.md), [first harvest](/Users/edr/code/JouleWise-wt-cadence-ff50b201/docs/process_traces/2026-09-22-activation-22666c9f/01-qpe01-pilot-n1-20260922-0217-harvest-record.md), [second arm](/Users/edr/code/JouleWise-wt-cadence-ff50b201/docs/process_traces/2026-09-22-activation-ca45291d/01-arm-record-qpe01-pilot-n1-20260922-2100.md), [second harvest](/Users/edr/code/JouleWise-wt-cadence-ff50b201/docs/process_traces/2026-09-22-activation-a022aecc/01-qpe01-pilot-n1-20260922-2100-harvest-record.md).
I also read the live W1/W2 custody plans, driver logs, chain logs and all 24 `instrument_evidence.json` files. The four named activation records matched the requested bookkeeping worktree byte-for-byte at inspection.

**POLICY waits, ranked by observed or bounded minutes potentially saved.** Savings overlap; development fixes are not recurring window costs.

| Rank | Wait / possible saving | Protection and relationship to numbers | Smallest science-preserving rule |
|---|---|---|---|
| 1 | Interactive-session obstruction: **823 min observed** | Prevents agent contamination; touches measured power. Presence-only refusal also catches dormant sessions. | Arrange closure before readiness; use authorized teardown of owned sessions. Keep capture agent-free. |
| 2 | Registered inter-window gap: **360 min/window** | Provides separated sampling occasions; potentially touches dependence assumptions. No six-hour recovery measurement found. | Prospectively register consecutive windows, preserve order/count rules, check correlation and drift. |
| 3 | Reserved t0 waits: **W1 74.2; W2 185.2 min**; reducible excess **≈64 / 175 min E** above existing 10-min install floor | Scheduling/handback, not measured recovery. | Prepare successors early; schedule at earliest safe readiness boundary. Spacing savings overlap W2’s wait. |
| 4 | Zero-capture refusal hold: formerly **up to ≈155 min** for these plans | Prevents overlapping agents and hidden captures; touches numbers only if work actually began. | A234 already releases proved terminal zero-capture refusals; trigger recovery on proof, not nominal window end. |
| 5 | Full harvest gates: **76.9 / 72.9 min elapsed** | Pin/verdict accuracy touches numbers; full code regression suite on generated state adds little per-window coverage. | Deterministic raw-byte validation, one independent numerical replay, focused state checks; full suite/lenses after relevant code changes. |
| 6 | Slot idle slack: **≈70 min/window** | Registration calls cadence a physical barrier, but no measured minimum recovery establishing 600-s pitch was located. | **No immediate claimed saving:** test adaptive recovery prospectively; retain pitch until evidence supports shortening it. |
| 7 | Completed-chain hold: **≈30–33 min after courier** | Ensures driver/capture cleanup and delivery; fixed residual span does not improve a completed number. | Release successful windows on terminal result, proven process exit, sealed evidence and delivery. |
| 8 | Watchdog backoff: **2–60 min generic; 15–120 min usage, plus ≤2 min jitter** | Service/resource recovery, not instrument physics. | Retry on recovered availability; never block an already prepared, safe measurement behind an agent quota timer. |
| 9 | Fresh-supervisor relaunch / clean-exit pad: **≈3–6 min**, sometimes repeated | Prevents stale runner behavior; indirectly touches numbers. | Reload/revalidate relevant code identity; restart once after relevant code changes. |
| 10 | Notice / retry timers: **0-min notice minimum; 1-min retry minimum** | Owner veto and attempt bookkeeping; no physical recovery measurement. | Accepted notification plus current veto check; retry when cause and cleanup are proved clear. |

**Retry, spacing and stop rules — executable locations and minimum replacements.**

- **Same-candidate retry:** [`arm_retry.py:26`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/joulewise/arm_retry.py:26), `:174–186`: only idle interactive obstruction, notice mismatch, watchdog uncertainty or positively proved transport failure; unchanged candidate, unpublished/restored state, **60 s between attempts**. Replace timer with cleared cause plus completed cleanup; retain bindings.
- **A212/A234 successor/refusal-cost gap:** [`magistrate_watchdog.py:801`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/scripts/magistrate_watchdog.py:801), `:845`, `:1508`; [`arm_retry.py:251`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/joulewise/arm_retry.py:251), `:294`: delivered matching refusal, no chain/capture/reservation evidence, empty censuses, release latch, one fresh successor, **60 s**. Remaining recovery cost includes polling, harvest, cleanup and new preparation.
- **Forty-minute planner floor:** [`evidence_night.py:101`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/joulewise/evidence_night.py:101), `:421`: `next` and explicit t0 require **≥2,400 s** lead. This prevents a genuinely immediate successor despite early release. Replace with measured preparation/install allowance plus applicable quiet dwell.
- **Six-hour spacing/replacements:** [`preregistration:612`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:612), `:662`: W1/W2 and battery-replacement neighbors; arm records implement six hours after window end. Replace only prospectively with recovery-based starts and explicit sampling-dependence treatment.
- **“No window within y hours”:** no additional universal prohibition found in inspected executable paths. [`run_night.py:100`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/scripts/run_night.py:100) allows installation **00:00–24:00**; [`arm_retry.py:339`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/joulewise/arm_retry.py:339) states no delay after successful harvest. Six-/24-hour freshness ceilings are expiry rules, not mandatory gaps.
- **Install/fence ladder:** [`run_night.py:98`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/scripts/run_night.py:98), [`magistrate_watchdog.py:90`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/scripts/magistrate_watchdog.py:90): install before t0−10; REQUEST/TERM/KILL at −8/−6/−5. Keep enforced teardown; replace fixed surplus with proven agent absence and completed dwell.
- **Backoff / five-minute relaunch:** [`magistrate_watchdog.py:99`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/scripts/magistrate_watchdog.py:99), `:1442`, `:1845`; launchd recovery tick is **300 s**. These are policy. Make lifecycle recovery event-driven; retain throttling for actual service failures.
- **Courier/dead-man holds:** [`run_night.py:74`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/scripts/run_night.py:74), `:89–91`; [`magistrate_watchdog.py:788`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/scripts/magistrate_watchdog.py:788): completion = t0+window+300; delivery retries **60/180/600 s**; dead-man grace **3,600 s**, missing-delivery lock **900 s**. Keep failure recovery bounds; do not spend them after proved successful completion.
- **Started/consumed attempt refusal:** [`launch_window.py:285`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/scripts/launch_window.py:285), [`night_gate.py:1042`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/joulewise/night_gate.py:1042): no retry of consumed capability; same-boot restriction is within that pack custody namespace. Preserve failed attempts; permit a distinct preregistered successor after terminal cleanup, without rebooting merely to reset bookkeeping.
- **Scientific stop lines:** preregistration `:612`: median cadence **>150 ms**, W1 valid count **<6**, issuance **n<12**, W3 only if W1+W2 count **<12**; `:662`: one battery replacement. These protect instrument regime and inference. Preserve them; never top up because a B value disappoints.
- **Post-capture daemon abort:** [`arm_retry.py:62`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/joulewise/arm_retry.py:62): two consecutive contaminated envelopes; successor authority differs from zero-capture recovery. Preserve captured evidence and use a separately authorized replacement rule.

**PHYSICS waits and the numbers supporting them.**

- **Quiet state / settling:** ten-minute untouched-idle rationale comes from idle-triggered daemons; the recorded XProtect failure involved **94% CPU**. [`prewindow_check.sh:37`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/scripts/prewindow_check.sh:37) requires **600 s continuous clean dwell**, resets on contamination, polls every 30 s. The 45-min timeout is policy, not required dwell.
- **Agent-load decay:** runbook `:1595–1618` models one-minute load excess retaining **0.674% after 300 s**; gate **2.0**. This supports teardown/quiet observation, not six-hour spacing. The model is not a measured guarantee.
- **Clock state:** W1/W2 losses include **52.0, 5.8 and 35.9 ms** wall/monotonic spans against **5 ms**; W1-d01 also had infeasible fit. Disable network time and attest correction-free captures. Future H5’s **600-s OFF interval** can share the quiet settle; no additive OFF wait occurred in these derivations.
- **Battery float:** preregistration `:650–664`: AC connected, not charging, **|current|≤200 mA**, reading age **≤180 s**. W1 had 23 endpoint readings at 0 mA and one −11 mA; W2 all 0. Wait until this predicate passes; no fixed float duration is justified.
- **Cooldown:** [`controller.py:2475`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/joulewise/controller.py:2475), [`schemas.py:505`](/Users/edr/code/JouleWise-wt-cadence-ff50b201/joulewise/schemas.py:505): default **30-s sustained window**, ≥80% evidence coverage, idle power ≤110% of reference, nominal thermal state; **300-s cap**. Anchor validation protects the reference number. Release on measured recovery; these campaign defaults were not an extra W1/W2 inter-window cooldown.
- **Capture duration:** protocol v3 requires **59 one-second pulses**, specified gaps and baselines; actual sampler spans were **196.78–196.81 s**. Pilot envelopes require **600 s**, with **480-s interiors**. These lengths define the observations and cannot be shortened as scheduling cleanup.
- **Duration prescriptions without measured lower bounds:** 600-s derivation pitch leaves roughly six minutes after each writer finishes; separate legacy 180-s clock/launch settle can duplicate chain settle. Their numerical minimum remains unproved in inspected evidence.

**Yield and productive machine time.**

| Window | Attempted / retained | Losses / scientific standing |
|---|---:|---|
| W1 | **12 / 6** | Cap: d02,d03,d09; clock: d01,d08,d11 |
| W2 | **12 / 6** | Cap: d02,d06,d08,d11,d12; clock: d07 |
| Pilot 02:17 | **12 / 2** | Seven unresolved anchors; three incomplete interior-support exclusions; zero retained pairs, INCONCLUSIVE |
| Pilot 21:00 | **12 / 12 mechanically** | Entire run had `fseventsd` ≈1 busy core; envelope 1 also heavy `mediaanalysisd`; PROVISIONAL/non-idle-machine diagnostic, no quiet-machine sizing claim |

W1/W2 admitted sampler time totals **2,361.53 s =39.36 min**: **15.9%** of their combined ≈247.4-min driver spans, or **12.7%** of the two reserved 155-min spans.
From W1’s arming activation at 09-26 22:34 through W2’s main merge, elapsed time was **858.42 min**: admitted recording occupied **4.59%**.
From the earliest located Rev-5 draft commit through that merge, elapsed time was **3,295.98 min E**: **1.19%** admitted recording. This includes development, obstruction and other work; it is wall time, not CPU utilization.
The 21:00 pilot’s retained interiors total **96 min**, about **71.7%** of its chain, but productive quiet-machine admitted time is **zero**. Raw preservation succeeded despite failed Git publication.

**Fastest defensible prospective cadence on the dedicated Mac.**

1. Queue consecutive windows at any hour. Keep **12 captures, 600-s initial settle and 600-s pitch** initially: measured duration ≈124 min; conservative programmed runway **128 min** using the existing 480-s final-capture budget.
2. With roughly 10–15 min for completed delivery, automated harvest/install and handback, target **≈140–145 min start-to-start**, around **ten complete windows / 120 attempted captures per 24 h**. This is an engineering estimate, not demonstrated throughput.
3. Between windows require physics only: no surviving capture/agent processes, nominal thermal/recovered idle power, battery float, network time OFF and a clean dwell. Record custody and numerical validation automatically; no calendar gap.
4. Perform registration/design review, full suites, cold code gates and #416 system audit once per relevant frozen code/protocol change. Per window retain raw-byte authentication, battery/clock/cadence verdicts, fixed-count rules, independent arithmetic checking and an operational veto.
5. At the observed 8.5-h start spacing, sustained rate is **≈33.9 attempted /16.9 retained per day E**, before serial ceremony. Faster cadence alone projects **60 retained/day** at present yield; NTP cure alone **80**; cap cure alone **100**; both **120**, all fresh-window estimates.
6. Do not call 120/day claim-usable yet: cap resizing/runtime, OFF-state behavior and closer-window dependence need validation and prospective registration. Existing invalid captures remain excluded. Shorter pitch could improve throughput further, but this audit cannot establish its safe minimum.

Six-line owner summary:
Your dedicated Mac can collect during the day as well as overnight.
The six-hour gap has no measured recovery justification in these records.
W1/W2 lost half their captures: eight to computation limits, four to clock corrections.
Keep the pulse protocol, clean dwell, battery checks and measured cooldown.
Automate harvest checks and review unchanged machinery once per relevant change.
Target about 120 attempts/day; 120 admitted/day is a validation target, not an achieved result.

## Residual risk

Exact start/end times for every individual preparation, review and hosted-CI phase are not preserved; estimates above expose that limitation.
The issuance record itself flags conflicting approximate email/commit times; no precise issuance-stop duration is asserted.
No shorter-cadence experiment, new hardware validation or canonical suite was run. The worktree remained clean and unchanged.