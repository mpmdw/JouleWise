# Magistrate activation 39cdeb12 (Opus 5.5, headless, 2026-10-31 from 01:22 PDT)

No pending watchdog notices. No unread mail from Ed. Open directives unchanged (#587 and the standing older ones). Nothing armed; no `com.joulewise.night*` label loaded or on disk; BYTES loop `DONE`; canonical root equal to `origin/main` (`877e91f36`).

## BY-THERM-LINES on the real BYTES archives (item 154 (2))
- Tool: `scripts/bytes_thermal_lines.py` from a detached checkout of `4e29114ea` (`origin/codex/2026-10-28-by-therm-lines`), worktree `/Users/edr/code/jw-wt/therm-lines-39cd`; `/opt/homebrew/bin/python3.13`, no `JW_B5_SYNTHETIC_ONLY`. Every record states `producing_commit` `4e29114ea…`, `producing_tree_dirty: false`.
- Inputs: the counting session of each pack, `ARCHIVE=/Users/edr/night-b6/sessions/<session>/archive`. Pass 2 (`hull-p2`): r2-bytes-s1-p2, s2-p2, s3-p2, s4-p2, s5-p2, r2-bytes-s6-p2-n3. Pass 1 (`request-end-p1`): r2-bytes-s1-p1, r1-bytes-s2-p1, s3-p1, s4-p1, s5-p1, r2-bytes-s6-p1.
- No `--export`: each session's `export/<pack>/` holds only the calibration CSV while BYTES is blinded. When the stage-1 export exists, the analysis must either re-run the line with `--export` into a new output directory or confirm that its CSV codes agree with the transformed acceptance (the tool refuses on disagreement).
- Outputs: `/Users/edr/night-archive/bytes-thermal-lines-39cd/{hull-p2,request-end-p1}/<session>/` (new directory each), with stdout records `<session>.stdout` beside them. All 12 rc 0; `verify` prints `view verified` for all 12.
- Results (exclusion codes and run ids only; no measurement value was read):
  - **s5-p2 hull line:** 23 Llama-70B science members gain `thermal.os_level_nonzero` (13 units). Status `evaluated`; `records.thermal_view_changed` false.
  - **s5-p1 request-end line:** 10 Llama-70B science members lose `thermal.os_level_nonzero` (7 members, 6 units restored; the rest keep other codes). The count matches the registration's forcing problem ("ten science members").
  - Every other pack, both passes: `equals registered line`, no changes.
  - Notices are only `reference.unchanged` (25 per session); no untrusted-journal, missing-span or replay-disagreement notice.
  - Direction check: the hull line only adds and the request-end line only removes, as the registration's monotonicity statement (§21 R1a) requires.
- Stdout sha256: s1-p2 `ebfb1898…`, s2-p2 `9d3d8dd4…`, s3-p2 `2a28ee1a…`, s4-p2 `5028b90e…`, s5-p2 `197699f3…`, s6-p2-n3 `9d7b93b4…`; s1-p1 `9f36710e…`, s2-p1 `c4c37ce0…`, s3-p1 `5d351759…`, s4-p1 `b6852394…`, s5-p1 `aaa29eee…`, s6-p1 `d1230cc5…`.

## Housekeeping
- Worktrees removed (clean, head on origin): `jw-wt/rec-39206674`, `jw-wt/rec-4e748ac1`, `jw-wt/int416` (its four `.scratch-416*` dirs copied first to `~/night-archive/forward-20261021/seat-scratch/int416/`, 221 MB). `jw-wt/af-f2-f3` kept: 7 uncommitted paths.

## Pruning tally
- BY-THERM-LINES `verify`: ran on 12 views, caught nothing.
- Cross-check of the s5-p1 change count against the registration's stated ten: agreed; caught nothing.
