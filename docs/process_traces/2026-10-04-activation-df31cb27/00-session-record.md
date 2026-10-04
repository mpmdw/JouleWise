# Activation df31cb27 (headless magistrate, Opus 5.5), 2026-10-04 12:13 PDT

Launch: notice_pending = [`transition-1720-hold_census`, "production census non-empty inside plan
span", epoch 1791119222 (06:07 PDT)]. The census line it fired on (watchdog `events.jsonl`
sequence 1719) is the `b3w1` driver itself (`scripts/run_night.py run --plan
/Users/edr/night-custody/d117-g2a-prefill-probe-20261004T1305Z/night_plan.json`, pid 96605), so the
watchdog held as designed. No unread owner mail (`from:claude2.glaring610@passmail.net is:unread`,
all threads: none). Open directives are the standing #405-#422 set; no new instruction, no NO. No
standdown.request.

## Step: HANDOFF step 3, harvest `b3w1` (plan `d117-g2a-prefill-probe-20261004T1305Z`)

Driver result `GO`, chain exit 0 (started 06:26 after the clean dwell, ended 09:42 PDT), census
hits none. Recipe `docs/process_traces/2026-10-03-design-block3/40-g2a-b3-arm-recipe.md` §6,
unedited (clone at H `abe759d3`, harvest time reached, result and courier files present). Harvest
`~/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z/harvest.json` sha256
`e7636ebbdf5383683e2c16359284766282ec1dd4b6d57f604b7b149552ff2242`: verdict **RECOVER**, cause codes
`[calibration_ledger_baseline_missing]`, `capture_made` true, pin advance pending operator commit
(terminal pin sha256 `d399ed06…aa98`). No member lists a problem, and every member's
`clock_anchor_status` is `bounded`, so the §7 mechanical END STATE trigger does not fire. Night
agents uninstalled (rc 0). Canonical root fast-forwarded `abe759d3` → `a6c7f9cf` after the
uninstall (no `com.joulewise.night*` label loaded, no night plist on disk).

## Cause: a harvest tooling defect (bracket ledger view built from the wrong baseline)

This is the first G2-a window whose bracket session finalized; block 2's windows all stopped at
`bracket_incomplete`, so the harvest's bracket path never ran before. `calibration_bracketing.py`
(~2208-2220) requires the ledger snapshot's baseline to equal the acceptance artifact's
`ledger_cutoff`. The acceptance in force (`calibration_acceptance_d079_v2_n24_25g83_r2`, sha
`f949f511…3660`) has cutoff sequence 376. `scripts/harvest_g2a_window.py` (~150-167) builds the
snapshot with the window's seed head (392, from the frozen `calibration_plan.json`) as baseline, so
the decision refuses before judging the brackets. Every other caller (`joulewise/whole_window.py`,
`scripts/run_campaign.py`, and `scripts/generate_g2a_probe_inputs.py`'s own ledger authentication)
uses the cutoff. Registration §6 judges the brackets "against the acceptance in force", so this is
a code-agrees-with-text fix (§11), carried by an ordinary gated PR, and §12 (ii) lets H′ differ by it.

Cause named from the cause code, the bracket binding and code reading only. No bracket assessment
value, count or summary was read.

## R3 in flight

- Email to Ed (state change plus the pending notice): Gmail `1a10864bf5d23001`, accepted, so
  `notice.ack` was written for this activation.
- Fix seat: Sol 6.1 xhigh, brief `10-sol-fix-brief.md`, worktree `/Users/edr/code/JouleWise-wt-df31-fix`,
  branch `fix/2026-10-04-g2a-b3w1-bracket-baseline`, report `/Users/edr/night-archive/df31-sol-fix-report.md`.
- Then: a Sol executing review in a separate worktree, the whole suite, CI, a Fable cold final pass
  (harvest code decides the verdict), and the merge. After that, a seal-record H′ extension listing
  the fix under (ii), a re-harvest of this window into a fresh archive
  `~/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2` from a checkout at the merged
  head (block-2 precedent: the `-r2` re-harvests after #461/#463), records landed with the pin
  advance, and then recipe §7 by the re-harvest's verdict.

## PR #467 gates

- Fix seat (Sol 6.1 xhigh): [11](11-sol-fix-report.md). Implemented and tested (188 OK, 1 skip). Its sandbox could not write the linked worktree's git metadata, so the lead committed `96747ff0`. The seat's real-data bracket replay returned no tooling refusal code; its outcome is kept out of the PR body (block blinded).
- Executing review (Sol 6.1 high, separate worktree): [12](12-sol-executing-review.md), **FAIL**, with one finding. F1 (MAJOR): with zero valid members, the bracket decision returns only `instrument_calibration_bracket_missing` and the bracket view's refusal codes were lost. Six mutation probes, all killed.
- F1 **fixed** by the lead in `92a3661d`: the bracket view's refusal reasons are unioned, first, into the decision's reasons for a finalized session. A regression test was added; deleting the line fails it. Delta check (Sol 6.1 high): [13](13-sol-delta-check.md), **PASS**.
- Cold Fable final pass at `92a3661d` (fresh worktree, no loop context; a first launch died on a missing `timeout` binary and was relaunched): [21](21-fable-final-pass.md), **PASS**, no BLOCKER or MAJOR. Dispositions:
  - M1 (a non-baseline refusal in the third view is a RECOVER cause, not REFUSED): rejected as intended. It is requirement 4 of the brief; the verdict is never SELECT, and the pin advance re-authenticates.
  - M2 (the decision reloads the default acceptance itself): rejected. Safe, because the loader authenticates against the code-pinned registry, and a divergent cutoff fails closed.
  - N3 (no harvest-level test drives the real decision to `passed` with a non-zero cutoff): deferred to lane `G2A-ATTACH-GUARD-TESTS-01` (tests only).
  - N4 (the union runs only for finalized sessions): rejected. The verdict is RECOVER either way.
  - N5 (the `acceptance is None` clause survives mutation, ending REFUSED with another code): deferred to lane `G2A-ATTACH-GUARD-TESTS-01`.
  - N6 (the acceptance binding also refuses non-finalized windows): rejected. It matches `check_harvest_inputs`.
- Fable also checked that the 1305Z clone's ledger carries the cutoff digest at sequence 376.

## Merge, re-harvest, verdict

- CI green on `ad96bed4` (15/15, gate-ledger included); PR #467 merged `18100c46` (= H′ 1).
- First trial re-harvest (from the fix worktree into `/tmp`) REFUSED with `harvest_frozen_input_authentication_failed`. The input check reported `calibration_ledger_head_uncommitted`: the first harvest had written its pin advance into the measurement clone's `configs/calibration/calibration_ledger_head.json`, as designed (`needs_operator_commit`). Block 2 never hit this because its first harvests refused before writing a pin. Those bytes equal the archive's `derived/terminal-pin.json` (`d399ed06…aa98`). A copy was preserved at `~/night-archive/df31-preserved/`, and the clone's file was restored to its committed bytes (`git checkout --` on that one file; the clone's HEAD stayed `abe759d3`). The second trial gave SELECT.
- Re-harvest (recipe §6 from a detached worktree at `18100c46`, `--read-only-sources`, fresh root): `~/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2/harvest.json` sha256 `8fca2228d66b8acbe06c128b50ecc8bd5579f8fde859dd04ad7bf9d6e5a9e814`, **verdict SELECT**, no cause codes, `capture_made` true. Selection record `derived/selection.json` sha256 `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`. Terminal ledger sha256 `6ee89e5a…530e`. Pin advance 392 → 402 (`d399ed06…aa98`). The clone stayed clean.
- Pinned files at `18100c46` against the seal table: fifteen unchanged; `scripts/harvest_g2a_window.py` changed by #467 (`0d8bc127…47ff`). Recorded as seal record 52 `## H′ 1 pins`.
- Landing (branch `harvest/d117-g2a-prefill-probe-20261004T1305Z-r2`):
  - the pin advance;
  - `windows/d117-g2a-prefill-probe-20261004T1305Z/` with `harvest.json` (r2), `harvest-r1-recover.json`, `SHA256SUMS` and `selection.json`;
  - the seal record entry;
  - the desk-day seat brief `40-desk-day-seat-brief.md`.

## Step 4 by verdict: SELECT → block 3 complete

Per recipe §7: email Ed once (paths and shas), then launch a design seat (RUN_STATE item 7) for the desk day. Brief: `40-desk-day-seat-brief.md`; state: `~/night-archive/desk-day-v5/`; launcher: `docs/process_traces/2026-10-02-interactive/launch-seat.sh` (opus). The selected rung is not typed here; the seat reads `selection.json`.
- Pin- and seal-sensitive tests on the landing branch (24 modules that read the ledger head pin, seal record 52 or registration_block3): Ran 1044 tests, OK (skipped=4).
- PR #468 (light tier) CI green 15/15 on `583c0284`; merged `4ea04a18`. Canonical root fast-forwarded to `4ea04a18` (no night label loaded, no night plist).
- Desk-day seat launched: pid 70182, log `~/night-archive/desk-day-v5/seat-1791151006.log`. Email to Ed (block 3 complete, paths and shas, seat launched): Gmail `1a108ebde5ce2b0a`.

## Gates and checks that ran (pruning rule)

- **Harvest custody and verdict** (`harvest_g2a_window.py`): its first run caught nothing real. It mis-refused on its own bug, which only the real window exposed.
- **Sol executing review: caught F1.** With zero valid members, the refusal cause code was lost. That is a cause-code fidelity defect, and it bears on how a RECOVER is named.
- **Fable final pass:** PASS, minor notes only.
- **Trial re-harvest before the real one: caught the uncommitted-pin refusal.** It cost a `/tmp` run instead of a real archive root.
- **Pin-sensitive local tests (1044) and CI:** green; no catch.
- **Watchdog hold_census:** held as designed during the window.
