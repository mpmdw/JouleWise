# Window close-out — window_metrologyB_20260801 (§12 record)

- Window ID: window_metrologyB_20260801 — metrology REMAINDER window
  (frozen plans per D-096: full null ladder -> claim C2; clean
  single-root additivity 24/24 -> C4; long_holds Part A -> C5).
  Magistrate-operated solo; Ed's §5A done ~23:00 PT 2026-07-31 (network
  time OFF, AC, 140 W Anker PD — instrument identity "pd charger").
- Collection under repo main @ d1498f9 (metrology_v1 suite mainline).
  Campaign policy sha256 b0d7b228…65efd. Plan root
  /Users/edr/JouleWise-window-plans/window_metrologyB_20260801; chains:
  original 2a334f64…09d5f, continue 040a6dd0…, continue2 73421d8e…,
  salvage 4a2b248e… (all §10 shape: pin window pre-cal, re-run §5B).
- LAUNCH ARC (three pre-launch/launch events BEFORE the member arc):
  (a) Launch 1 (00:57 PT) aborted at the §5B gate: pre-cal ×2
  `clock_anchor_unresolved` / `native_intersection_empty`, zero members;
  attempts preserved (20260801T010113-e859f3aa b 0.412 all pulses
  SNR~39k; 20260801T010805-ff3fdc88 pulses undetected). Escalation
  trigger fired (same signature as window A's post-cal attempt 1) ->
  bounded Sol xhigh consult (report: consult_anchor_v2.md, session
  693609a9 scratchpad). Consult findings ACCEPTED: the anchor is
  knife-edge by construction (pass/fail margins ±1.4 ms; unmodeled
  wall/monotonic rate ~−12 ppm ≈ 2.3 ms/capture exceeds every margin —
  DESK-LANE anchor-design item); bird (iCloud sync of window A's
  10.4 GB banked corpus, observed 99% CPU) recorded as PLAUSIBLE
  trigger + objective preflight violation, NOT confirmed root cause;
  TM exonerated (no destinations configured — the prep script's "TM
  RUNNING" line is a process-residency false proxy, which also taints
  window A's failure-#3 "TM-consistent" attribution).
  (b) Predeclared relaunch (recorded in operator log 09:15Z): frozen
  chain unchanged, its built-in calibration attempt+retry pair as the
  budget, NIGHT CLOSES if the calibration gate aborts; the two §5B
  aborts do NOT consume the member salvage budget; bird SIGSTOP under
  full lifecycle custody (identity pid/lstart recorded, state T
  double-verified, fail-safe CONT trap, post-window identity check,
  cloudd/fileproviderd added to launcher holds, no Mobile Documents
  access while stopped).
  (c) Launch 2 (01:37 PT, bird stopped): pre-cal PASSED FIRST ATTEMPT
  (20260801T014059-8c3bfe9e, b_fiducial 0.032787 s, §5B screen passed).
- bird LIFECYCLE: STOPped for every measurement segment; identity
  (pid 1077, lstart Jul 13) UNCHANGED across the whole window; CONTed
  by the launcher trap after each chain exit and re-STOPped at each
  re-arm; final CONT 13:52Z after measurement_complete. (The launcher's
  "identity DEVIATION" log lines are a comparison-string false positive:
  the captured row includes the state column, S at capture vs T later;
  pid+lstart identical throughout.)
- Calibrations (consumed): pre 20260801T014059-8c3bfe9e (b_fiducial
  0.032786870825707914 s, §5B PASSED, single attempt). Post
  20260801T064830-c76f5d1c (b_fiducial 0.0350400833260715 s, single
  attempt, no retries, no deviation needed). Fiducial-bound difference
  ~2.3 ms vs the 10 ms bracket policy — the governed verdict owns the
  §8 ruling.
- COLLECTED AND BANKED (backup both roots to iCloud
  JouleWise-backup/window_metrologyB_20260801 + _bound): NEG-8 bound
  corpus 12/12 + dual-family bound minted in-window (no bound-root
  failures); start triplet 3/3; **null_o0128 COMPLETE**;
  **null_o0512 COMPLETE 24/24** (incl. b04-b2 rerun); midpoint;
  additivity 23/24 (r01–r07 ×3 shapes + p0512o0512-r08 +
  p0128o2048-r08; p2048o0128-r08 failed twice, see below); end triplet
  3/3. NOT collected (move to the next window): null_o2048 (C2's third
  stage), long_holds 01_holds, additivity p2048o0128-r08 remainder.
- MEMBER FAILURES (three; salvage close per the ratified rule):
  1. mtnull-o0512-b04-b2 ~04:29 PT — idle admission failure
     (cpu_busy_ratio_p95_exceeded, 98 s). Intruder observed LIVE
     post-abort: mobileassetd 59–92% CPU + softwareupdated (overnight
     software-update asset machinery; same ~04:29 clock time as window
     A's failure #3 the prior night). Quarantined …113258Z; RERUN CLEAN
     in continuation-1; supersession recorded ONCE post-window
     (entry 3896c5ed…, selected = continuation-1 occurrence).
  2. mtadd-p2048o0128-r08 ~06:13 PT — idle admission failure (96.9 s,
     same signature); additivity stood 23/24; intruder not observed
     live (quiet by the 06:16 sample). Quarantined …131705Z.
  3. mtadd-p2048o0128-r08 rerun ~06:23 PT — SAME slot, SAME signature,
     97.9 s, machine otherwise quiet. CAUSE NAMED (timing-matched,
     recorded honestly): the OPERATING SESSION'S OWN OUTPUT STREAMING —
     the member's idle gate coincided exactly with the magistrate
     session streaming its post-arm status message (claude 12–18% CPU +
     Terminal rendering); failures #1/#2 occurred while the session was
     silent. DOCTRINE LESSON: "zero tool calls during measurement" is
     INSUFFICIENT — the session must not stream output while any idle
     gate can be sampling; arm-time messages must be one line.
     Second occurrence quarantined …133315Z; NO supersession (slot
     never replaced — dangling occurrence, window A r08 precedent).
- THIRD-FAILURE RULE FIRED -> salvage close: end triplet + post-cal
  only, both clean (13:37–13:52Z); measurement_complete 13:52:00Z.
- Whole-window verdict: **FAILED** (governed run 06:54–07:19 PT, row
  appended, 70-bundle basis; recorder-then-verdict order preserved).
  NOT the predicted failure shape: the §8 instrument bracket **PASSED**
  (drift 0.002253 s vs 10 ms policy, pre+post both formed — the
  post-cal was consumed correctly), the dangling r08 was NOT excluded,
  and the recorded supersession was NOT consumed. Conditions:
  `whole_window_campaign_membership_unresolved` (with
  `source_campaign_manifests` EMPTY — the verdict resolved ZERO
  campaign manifests despite a populated campaign_manifests/ dir that
  the supersession recorder had consumed an hour earlier),
  `environment_admission_missing`, and a failed NEG-8 bracket
  (`neg8_bracket_missing`, `neg8_bracket_reference_invalid`,
  `neg8_drift_bound_stale` — the bound was minted in-window at 02:22 PT,
  so "stale" needs the machinery adjudication too).
- MAGISTRATE RULING AT RECORDING: the FAILED verdict STANDS as issued —
  no reinterpretation. Both metrology windows now carry FAILED verdicts
  with DISTINCT condition sets (A: dangling-occurrence exclusion +
  bracket refusal; B: manifest-resolution/membership + NEG-8 bracket
  evaluation). The desk-lane adjudication covers: (a) dangling
  quarantined-without-replacement occurrences, (b) deviation-retry
  post-cal selection (A), (c) manifest/membership resolution +
  supersession consumption + NEG-8 bracket evaluation over multi-chain
  salvage windows (B). Collections are banked and intact; nothing here
  invalidates the bundles themselves.
- NO extraction/claims from this window: C2/C4 consumption follows the
  D-095 chain and must record the D-093 raw-vs-validated scan plus the
  D-088 cl.3(c) bench scan at consumption time.
- Network time: still OFF (Ed's §5A) — **Ed: restore after reading
  (`sudo systemsetup -setusingnetworktime on`)**.
- STATUS: SALVAGE-CLOSED under the third-failure rule. Headline
  collection wins: null ladder 2 of 3 stages COMPLETE (o0128 + o0512 —
  C2 progress), additivity 23/24 single-root (C4 near-complete; window
  A's 21/24 corroborates), references + bound + bracket all clean.
  Remainder (null_o2048, holds, one additivity slot) moves to a third
  metrology window.
