# 2026-08-01 — Metrology window B: collected + salvage-closed; both metrology verdicts FAILED as-issued

Session: 2026-08-01 00:30–07:30 PT, Fable magistrate solo (Ed's §5A done
~23:00 PT 2026-07-31; 11-hour runway). Repo main `d1498f9` → `20f0007`.

## Outcome in one paragraph

`window_metrologyB_20260801` collected its core payload across three
launches and closed as salvage under the third-failure rule:
NEG-8 bound corpus 12/12 + in-window bound mint, references 7/7,
**null_o0128 and null_o0512 complete** (claim C2, 2 of 3 stages),
**additivity 23/24 single-root** (C4), clean calibration bracket
(2.25 ms drift vs 10 ms policy). Both metrology windows' whole-window
verdicts **FAILED and stand as issued** — with *distinct* condition
sets that are machinery questions over salvage-shaped windows, not
physics problems. Collections are banked to iCloud (72+13 bundles,
verified rc=0). A three-part machinery adjudication is the next desk
item; the remainder (null_o2048, long_holds, one additivity slot) moves
to a third metrology window.

## Window A verdict (emitted first, 00:26–00:47 PT): FAILED

The in-flight verdict from the prior checkpoint survived the session
boundary and completed. Conditions: `whole_window_bundle_invalid` +
`environment_admission_failed` (the quarantined-never-replaced
`mtadd-p0512o0512-r08` occurrence dangles — first
quarantined-without-replacement slot the machinery has ever evaluated)
and `instrument_calibration_bracket_missing` (bracket pre AND post
null: the selector refused to form a bracket rather than consuming the
recorded-deviation retry post-cal; the §8 budgetable case was never
evaluated). `neg8_bracket` passed; adapter continuity stable. The
close-out (custody root) also corrects two checkpoint errors:
additivity was 21/24 at final state (not 23/24), and the charger is a
140 W Anker PD (instrument identity "pd charger"; the "Apple" label was
cosmetic).

## Window B launch arc

1. **Launch 1 (00:57 PT) — §5B gate abort.** Pre-cal failed twice with
   `clock_anchor_unresolved` / `native_intersection_empty`; zero
   members; both attempts preserved. Same signature as window A's
   post-cal attempt 1 → the standing escalation trigger fired → bounded
   Sol xhigh root-cause consult instead of a third blind attempt.
2. **The consult** (read-only, one round) confirmed the structural
   finding and refuted the lead's mechanism: the anchor is
   **knife-edge by construction** — tonight's pass/fail margins were
   +0.86/+1.41 ms (passes) vs −0.25/−0.26/−0.51 ms (failures) at 197 s
   capture length, the lead's "cadence drift rates" were
   quantization-confounded, and the *unmodeled* controller
   wall/monotonic rate (~−12 ppm ≈ 2.3 ms per capture) exceeds every
   margin. That is an instrument-design finding (rate-aware anchor
   mapping is now a desk/paper item). **Time Machine was exonerated**
   (`tmutil destinationinfo`: no destinations configured — the prep
   script's "TM RUNNING" line only detects process residency, which
   also taints window A's failure-#3 "TM-consistent" attribution).
   `bird` (iCloud sync, observed 99% CPU uploading window A's 10.4 GB
   backup) is recorded as **plausible trigger and objective preflight
   violation** — not confirmed root cause.
3. **Launch 2 (01:37 PT)** ran under the consult-hardened
   **bird-SIGSTOP protocol** (identity custody pid/lstart, state T
   double-verified, fail-safe CONT trap on all exit paths, post-window
   identity check, cloudd/fileproviderd launcher holds, no Mobile
   Documents access while stopped) with a predeclared budget: frozen
   chain unchanged, its built-in calibration retry pair, night closes
   if the calibration gate aborts. **Pre-cal passed first attempt**
   (b_fiducial 0.032787 s).
4. **Member failures** (three → salvage): #1 `mtnull-o0512-b04-b2`
   (04:29 PT, idle admission; intruder observed live post-abort:
   mobileassetd 59–92% + softwareupdated — same ~04:29 clock time as
   window A's #3 the prior night); rerun clean in continuation-1;
   supersession recorded once post-window (entry `3896c5ed…`).
   #2 `mtadd-p2048o0128-r08` (06:13 PT, same signature, additivity at
   23/24). #3 the same slot on rerun (06:23 PT, identical signature on
   a quiet machine): cause named honestly — **the operating session's
   own output streaming** during the member's idle gate (claude 12–18%
   CPU + Terminal rendering; failures #1/#2 occurred while the session
   was silent). Doctrine lesson recorded: zero tool calls is
   insufficient; zero streaming during idle-gate exposure, one-line
   arm messages.
5. **Salvage close (06:34–06:52 PT):** end triplet 3/3 + post-cal
   single-attempt clean → `measurement_complete` 13:52Z.

## Window B verdict (06:54–07:19 PT): FAILED — a different machinery shape

Recorder-then-verdict order preserved. The §8 bracket **PASSED**
(drift 0.002253 s, pre+post formed — the predicted window A bracket
problem did NOT recur), but: `source_campaign_manifests` resolved
EMPTY over the four-chain-segment window (despite a populated
`campaign_manifests/` dir the supersession recorder consumed an hour
earlier), the recorded supersession was not consumed, the dangling r08
was not excluded, and the NEG-8 bracket evaluated
missing/reference-invalid/**stale** against a bound minted in-window.
Conditions as issued: `whole_window_campaign_membership_unresolved`,
`environment_admission_missing`, `neg8_bracket_missing`,
`neg8_bracket_reference_invalid`, `neg8_drift_bound_stale`.

## The adjudication this hands the desk (three question groups)

(a) Dangling quarantined-without-replacement occurrences in
salvage-closed windows (A excluded-and-failed on it; B did not exclude
it). (b) Deviation-retry post-cal selection (A refused; B formed).
(c) Window B's manifest/membership resolution + supersession
consumption + NEG-8 bracket evaluation over multi-chain salvage
windows. Contract lens: independent audit → cold gate if any override
of the as-issued verdicts is proposed. Nothing invalidates the bundles.

## Records

- Close-outs (custody): `~/JouleWise-window-custody/window_metrologyA_20260731/close-out.md`,
  `~/JouleWise-window-custody/window_metrologyB_20260801/close-out.md`
- Consult report: session scratchpad `693609a9…/scratchpad/consult_anchor_v2.md`
- Checkpoint: `RUN_STATE.md` @ `20f0007`
- New standing doc this session: `CLAIMS_STATUS.md` (root) — single home
  for claim validity state.
- Owed to the bookkeeping batch: D-098/D-099 decision-log entries,
  council-log addendum (the consult), kernel refresh, queue row for
  metrology window C, consistency sweep.
