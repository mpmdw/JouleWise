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
