# Block-4 lane C round 2: L10-A ruling

Worktree: /Users/edr/code/JouleWise-wt-dd5-b4harv (round 1 committed by the lead as 201b1c1c). Round-1 report: /Users/edr/night-archive/desk-day-v5/sol-b4c.md. Scratch /tmp/dd5-b4c2/ only.

Lead ruling on your F1: correct the recipe, not the finalizer. L10-A finalizes against the complete STAGED scratch copy, so `--output-dir "$L10_A_STAGING_ROOT"` (the staging custody root, which the finalizer requires: `joulewise/analysis_manifest_v3.py:4072`) writes nothing into source custody. Change `docs/process/v5-l10-rehearsal-phase.md` §L10-A (:405) to that, with a dated one-line note naming the reason (finalizer requires output_dir == custody_root; the old `analysis-output` subdirectory produced `analysis_finalization_noncanonical` before member-cover validation). Keep every other argument and the before/after floor and tree-hash assertions. Update `scripts/harvest_v5_g2b_window.py` to run the corrected command, drop the `needs_ruling` path, and require exactly `{analysis_finalization_member_cover_mismatch}` against the real finalizer fixture; add a test that the OLD output-dir yields `analysis_finalization_noncanonical` and is recorded as FAIL (not as the expected singleton), and that staging-root outputs never touch the source custody tree (tree hash equal).

Your F2 (courier blindness) goes to lane B; do not edit `scripts/run_night.py`. Your harvester must still fail closed if a public artifact it writes would carry a metric; keep that.

Verify your focused tests (+ `tests/test_check_window_provenance*.py` if they exist). Do not start the canonical full suite (the lead runs it). No background processes. Finish in this turn.

WRITE_SCOPE: ["scripts/harvest_v5_pack_rehearsal.py", "scripts/harvest_v5_g2b_window.py", "joulewise/v5_qualification.py", "tests/test_harvest_v5_pack_rehearsal.py", "tests/test_harvest_v5_g2b_window.py", "tests/fixtures/v5_qualification_harvest/**", "docs/process/v5-l10-rehearsal-phase.md"]
