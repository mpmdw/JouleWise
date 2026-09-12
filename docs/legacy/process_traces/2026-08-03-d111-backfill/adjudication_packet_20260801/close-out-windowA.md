# Window close-out — window_metrologyA_20260731 (§12 record)

- Window ID: window_metrologyA_20260731 — metrology suite window A
  (frozen plans per D-096, `freeze_status: frozen_before_measurement`;
  campaigns: linearity_ramp -> claim C1, additivity_shapes -> C4,
  null_ladder + long_holds planned but moved to window B under the
  salvage close). Magistrate-operated solo, Ed §5A done 2026-07-31
  (network time OFF, AC).
- Collection ran under repo main (metrology_v1 suite mainline via
  PR #90/#91). Campaign policy sha256
  b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd.
  Chain sha 2a334f64…09d5f; original launch 2026-07-31T23:13:48Z;
  measurement_complete 2026-08-01T04:55Z (salvage shape) via
  continuation-3 (all continuations reuse the window pre-cal and re-ran
  the §5B screen, §10 shape).
- Calibrations: pre 20260731T161713-b8b08280 (b_fiducial
  0.030972654450356962 s, §5B screen PASSED, single attempt). Post-cal
  attempt 1 FAILED (mixed reasons: clock_anchor_unresolved +
  not_all_pulses_detected + pulse_detection_incomplete; PRESERVED as
  20260731T214355-126fc2ab). RECORDED DEVIATION (a10 precedent, runbook
  §10 post-a10 discipline): ONE settled retry, all attempts preserved,
  earliest-valid-causal consumption, no outcome selection — retry VALID
  as 20260731T215120-fa1e9cda (b_fiducial 0.045804 s). Expected bracket
  drift ~15 ms vs the 10.818 ms screen: §8 BUDGETABLE case (pre-cal
  level screen passed); the governed whole-window verdict owns that
  ruling — nothing was hand-applied.
- NEG-8 bound corpus: 12/12 usable at final state (r05 via
  continuation-1 rerun) + dual-family bound minted in-window
  (bound-mint.log, 2026-07-31T17:07 PT) BEFORE science stages.
- Collected and BANKED (backup done, both roots, iCloud
  JouleWise-backup/window_metrologyA_20260731 + _bound): start triplet
  3/3; **linearity_ramp 40/40 COMPLETE** (claim C1's campaign);
  midpoint; additivity 21/24 at final state (verdict basis: r01–r07 ×
  3 shapes; missing = p0512o0512-r08 quarantined + the two other r08
  shapes never collected after the salvage close; r06 rerun clean in
  continuation-2; the checkpoint's "23/24" figure was a miscount); end
  triplet 3/3. NOT collected (moved to window B): null_ladder
  02_null_o0512 (and the other null stages), long_holds 01_holds,
  additivity r08 remainder.
- FAILURES (three, all §10-handled, slots quarantined, cause named each
  time; THIRD-FAILURE RULE fired -> salvage close, ratified precedent):
  1. neg8-refcorpus-r05 ~23:37Z — CPU admission failure; transient
     intruder consistent with loginwindow lock-screen transition after
     operator walk-away (r04 duration stretched 133 s). Quarantined
     …233726Z; continuation-1.
  2. mtadd-p0512o0512-r06 ~03:39Z — operator walk-in woke display;
     environment admission refused the run in 15.8 s (guard worked as
     designed). Quarantined …034419Z; continuation-2 rerun clean.
  3. mtadd-p0512o0512-r08 ~04:29Z — cpu_busy + environment admission;
     transient daemon burst, TM-consistent; HID idle 38 min so NOT
     operator. Quarantined …042921Z. Salvage close: end triplet +
     post-cal only.
- SUPERSESSIONS: recorded ONCE each, AFTER stopping the premature
  verdict run (recorder-then-verdict order is mandatory — learned this
  window): claim root mtadd-p0512o0512-r06 (selected = continuation-2
  occurrence); bound root neg8-refcorpus-r05.
- Whole-window verdict: **FAILED** (governed run emitted 2026-08-01
  00:26–00:47 PT, after both supersessions were recorded; row appended
  to campaign_log.jsonl, 68-bundle basis). Conditions:
  (1) `whole_window_bundle_invalid` + `environment_admission_failed` —
  the manifest-declared occurrence mtadd-p0512o0512-r08 (failure #3,
  quarantined, NEVER rerun under the salvage close) dangles with no
  superseding occurrence; the machinery excluded it
  ("path does not exist") and failed the window. First time the verdict
  has evaluated a quarantined-without-replacement slot.
  (2) `instrument_calibration_bracket_missing` — bracket pre AND post
  both null: the selector refused to form a bracket; the failed
  post-cal attempt (126fc2ab) is the earliest-after-window candidate
  and the recorded deviation's earliest-valid-causal retry
  (fa1e9cda) was not consumed by the governed selector. The §8
  BUDGETABLE expectation never got evaluated.
  Sub-checks: neg8_bracket PASSED, adapter_wattage_continuity STABLE.
- MAGISTRATE RULING AT RECORDING: the FAILED verdict STANDS as issued —
  no reinterpretation (mandatory cold-gate trigger territory). Whether
  the governed machinery mis-rules the salvage shape (dangling
  quarantined occurrence; deviation post-cal selection) is a desk-lane
  adjudication item (audit + cold gate if any override is proposed).
  Until then window A is NOT evidence-bearing; the collected corpora
  remain banked and intact.
- Power identity: 140 W ANKER PD charger (instrument-visible
  "pd charger"/140.0). CORRECTION: prior docs' "Apple" charger label
  was cosmetic — the physical unit is the Anker; instrument identity
  fields were always "pd charger" and are unaffected.
- Backup (§11 order, BEFORE consumption): both roots verified present
  in iCloud JouleWise-backup (claim + bound), sources unchanged.
- NO extraction/claims from this window yet: C1 consumption follows the
  D-095 chain (gauntlet commit 3 -> MANIFEST-CONTRAST v3 -> multi-cell
  mint) and MUST record the D-093 raw-vs-validated scan (at recording
  time tonight: claim root 1/1, bound root 1/1) plus the D-088 cl.3(c)
  bench scan.
- Network time: RESTORED by Ed at wrap 2026-07-31 (confirmed; no action
  owed). Re-disabled 2026-08-01 for window B's §5A — restore reminder
  lives in window B's close-out, not here.
- STATUS: SALVAGE-CLOSED under the third-failure rule; whole-window
  verdict FAILED (see above), so the window is NOT evidence-bearing
  pending the desk-lane adjudication of the two machinery questions.
  Collection facts unchanged: linearity 40/40 (C1's campaign) and
  additivity 21/24 banked; window B re-collects a clean single-root
  additivity 24/24 per plan, which is now the primary additivity path
  rather than mere corroboration.
