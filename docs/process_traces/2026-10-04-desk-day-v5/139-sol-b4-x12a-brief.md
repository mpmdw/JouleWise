# Block-4 lane X12a (Sol 6.1 xhigh): harvest-side cures from the second cold pass (addendum F items 3, 4, 5, 7, 8c)

Worktree: /Users/edr/code/JouleWise-wt-dd5-x12a (branch `lane/2026-10-05-b4-x12a` at the integration head named in the worktree). Scratch /tmp/dd5-x12a/ only. Leave changes uncommitted; never push. No sudo, launchctl, powermetrics, systemsetup or Metal. Never touch the four pinned estimator files. Lane X12b edits `joulewise/v5_qualification.py` in parallel, in the sizing-binding path check around lines 470-480. Keep your edits in that file to the history and harvest functions.

Read the cold pass `/Users/edr/night-archive/desk-day-v5/fable-int2.md` (B3, M1, M2, L1; its reproducers are in `/tmp/dd5-fable-int2/test_history.py`). Then read ruling 76 addendum F on `origin/design/2026-10-04-v5-qualification-block` (`docs/process_traces/2026-10-04-desk-day-v5/76-r1-fold-ruling.md`, last section). Implement:

1. **B3 / F.3.** The G2-b harvest (`scripts/harvest_v5_g2b_window.py:~641`) and the desk close-out (`scripts/v5_s1_desk_closeout.py:~172`) read the network-time OFF receipt under the pack plan id, the frozen calibration identity, exactly as `scripts/capture_t0_step.py:302, 772` writes it. Add a composed test: a full G2-b harvest and a desk close-out of an attempt whose night plan id differs from the pack plan id. The fixture writes the receipt through the real capture writer, not by hand. The test must fail at the base and pass after the fix.
2. **M1 / F.4.** In `attempt_history` (`joulewise/v5_qualification.py:~201, 295-316`), evaluate the fresh-`s1` and `s2` rules against the nearest non-NULL predecessor.
   - After `s1` RECOVER(tooling) and then `s2` NULL, the next attempt may be `s2` again, and a fresh `s1` is refused.
   - NULL `s2` records count toward nothing.
   - Copy the cold pass's four-line matrix into tests; it must now produce the ruled outcomes.
3. **M2 / F.5.** When an attempt's original `harvest.json` is REFUSED and an identical-bytes `reharvest-N/harvest.json` exists, `checked_history(..., replay=True)` counts the newest re-harvest's verdict.
   - The re-harvest is authenticated as the same source bytes: use the existing re-harvest source census.
   - The pointer still names the original. The original is kept.
   - Tests: REFUSED, then a re-harvest NULL, then a fresh `s1` allowed; REFUSED, then a re-harvest RECOVER(tooling), then `s2` allowed; a re-harvest of different bytes refuses.
4. **L1 / F.7.** `scripts/restore_v5_null_reservation.py` (around 197-200): the replay authenticates the pin bytes recorded in the restore record (path plus sha256 at restore time), not the live pin file. Test: the pin file advances after the restore, and the history replay of the restored attempt still passes.

Run `tests.test_v5_block4_x7 tests.test_v5_block4_x2 tests.test_harvest_v5_g2b_window tests.test_harvest_v5_qualification tests.test_v5_s1_desk_closeout tests.test_v5_s1_qualification tests.test_v5_qualification_plan` plus your new tests. Watchdog `BindSupervisionProcessTests` timing failures in the sandbox are a known artefact. Finish in this turn.

WRITE_SCOPE: ["scripts/harvest_v5_g2b_window.py", "scripts/v5_s1_desk_closeout.py", "joulewise/v5_qualification.py", "scripts/restore_v5_null_reservation.py", "scripts/harvest_v5_qualification.py", "tests/test_v5_block4_x12a.py", "tests/test_v5_block4_x7.py", "tests/test_harvest_v5_g2b_window.py", "tests/test_v5_s1_desk_closeout.py", "tests/fixtures/v5_qualification/**", "tests/fixtures/v5_qualification_harvest/**"]
