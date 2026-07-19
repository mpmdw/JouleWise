# 2026-07-19 — Post-D-077 suite re-calibration window: 32 strict-valid bundles, guard live-validated, three probe defects fixed on live hardware

Ed-directed quiet window (granted ~2026-07-18 22:45 local, extended by Ed
mid-window). Executed against merged main `62f219d` (PR #77) with the D-077
production policy `configs/campaign_policies/quiet_mac_p2_production.json`
(`--arm-quiet-mode`, per-run idle admission `on_fail: abort`, cooldown v2).
All evidence in `runs_recal_20260718/` (sibling runs root chosen because the
frozen config run_ids collide with the retained 07-17 bundles in `runs/`).

## Deviation record

The standing rule forbids [QUIET-MAC] measurements while an agent session is
active. Ed explicitly directed this session to run the campaign ("run the
quiet mac tests... ill leave the laptop still", then "keep going!" after a
mid-window return). Mitigations: the campaign ran as a detached background
process with the lead session silent between launch checkpoints; the D-077
admission gate arbitrated environment quality per member. The gate's two
honest aborts (below) are direct evidence the arbitration worked.

## What was measured (all Qwen2.5-1.5B-4bit MLX, powermetrics backend)

- `p2015-neg8-reference-start` — window-start NEG-8 reference cell.
- Suite-ABBA comparative blocks b01–b05 — ALL FIVE complete (20 members,
  ~65 s each; b01–b02 in tranche 1, b03–b05 in tranche 2 after the b03
  re-stage).
- Suite-absolute block 06 — complete (10 members).
- `p2015-neg8-reference-end` — window-end NEG-8 reference cell.

**32/32 live bundles strict-valid** (`validate-bundle --strict`, lead-run).
Members carry the standard short-suite-window claim-evidence flags
(cadence/clock/sample-count) familiar from the 07-17 corpus; claim
adjudication remains P2-037's job. Backup: `scripts/backup_runs.sh` →
`~/JouleWise-backup/runs`, exit 0.

Retained non-member evidence (quarantined, never deleted):
- `rejected_attempt3/p2015-neg8-reference-start` — admission abort caused by
  probe defect 3 (below).
- `superseded_partial_b03/` — b03's first pass (3 succeeded + 1 admission
  abort when Ed returned mid-capture and the display woke). The re-run
  b03 block supersedes it for comparative use; the succeeded members remain
  valid absolute-cell evidence.

## The guard worked — twice

1. Member `p2015-df-cmp-abba-su-b03-a2` (first pass) aborted with
   `display became or remained awake during idle admission` at the exact
   moment Ed returned and woke the machine. Fail-closed, evidenced, no
   silent contamination — this is the D-077 design doing its job on real
   hardware.
2. The window's first NEG-8 attempt aborted on the same guard when the
   guard's own probe was defective (defect 3) — fail-closed even when the
   failure was ours.

## Three probe defects found and fixed live (macOS 26.5, Mac15,9)

All three were previously flagged `live_validation_provisional`; this window
was their first true live validation, and all three fixes are themselves
live-validated by the successful campaign plus pinned regressions
(`tests/test_environment.py`, 31 tests; pinned probe-call count updated in
`tests/test_controller.py`).

1. **`pmset -g` low-power key**: macOS 26.5 emits tri-state `powermode`
   (0 automatic / 1 low / 2 high), not `lowpowermode`. The probe returned
   None → `critical_unknown_fail_closed` rejected every preflight.
2. **`systemstate` Graphics never drops**: on macOS 26.5 a display-only
   sleep keeps `Graphics` in Current System Capabilities, so the capability
   heuristic can never prove displays asleep. Authoritative per-display
   `system_profiler` `spdisplays_asleep` evidence now wins when complete;
   partial/absent evidence stays fail-closed `any_awake`. (Definitive live
   observation: `Display Asleep: Yes` while `Graphics` persisted.)
3. **Guard observation lacked display inventory**: the lightweight per-run
   admission observation ran `systemstate` without the profiler, so with
   defect 2 every idle admission aborted `display became or remained awake`.
   The observation now carries the display-inventory probe (runs between
   captures, never inside a measured window).

Also during the window: the false "display refuses to sleep" hypothesis was
disproven (`pmset displaysleepnow` works; the belief came from defect 2's
non-discriminating probes). Ed's accidental `displaysleep 0` on AC power is
real but only affects idle darkening; restore with
`sudo pmset -c displaysleep 10` (needs Ed's sudo). One genuinely unexplained
display wake (23:09:52, no HID, no assertion, no log entry) remains an open
curiosity, made harmless by the admission guard.

## Session tooling (same night, pre-window)

- PR #77 (D-077 fix rounds 3–8) merged by Ed's direction; merged-main suite
  `Ran 1746 tests, OK (skipped=12)` lead-run.
- `~/.local/bin/codex-run-v3` patched (Ed-requested): one bounded
  auto-resume recovery for the xhigh review-genre null-final-message defect
  (4/4 manual-recovery precedent); backup at `codex-run-v3.bak-20260718`;
  wrapper's own test suite 148/149 on both patched and backup versions (the
  one failure pre-exists the patch).

## Tranche 3 (overnight, same night): optional blocks 08 + 09 closed

A second bracketed mini-window in `runs_recal2_20260719/` (fresh runs root;
frozen run_ids would collide with tranche 1–2), same production policy and
arming, launched after the canonical suite gate on the probe-fix head:

- NEG-8 start — 1/1.
- Block 08 long-request absolute — **20/20 succeeded** (~62 s each). This
  closes the documented gap "Optional block 08 was not run, so no
  long-prompt or long-decode request floor exists" (07-17 floors report).
- Block 09 short-prefill ABBA — **40/40 succeeded**.
- NEG-8 end — 1/1.

**62/62 bundles strict-valid** (single-process lead validation);
`backup_runs.sh` reported 63 artifact dir(s) backed up to
`~/JouleWise-backup/runs`, exit 0. Combined with tranches 1–2 the night
produced **94 strict-valid measurement bundles** across two bracketed
windows, zero contaminated members admitted, two honest guard aborts, and
zero admission failures after the probe fixes.

## Open follow-ups

- Comparative/absolute floor re-extraction from this corpus (P2-015
  analysis; supersedes the caveated 07-17 suite cells) — next session or
  delegated extraction job.
- Probe-fix commit lands as branch + PR (in flight this session).
- Optional blocks 08/09/10 and the remaining floors cells stay queued.
- `displaysleep` restore + the codex-run-v3 stale test 61 remain Ed-side.
