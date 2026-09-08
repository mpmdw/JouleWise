WRITE_SCOPE: ["scripts/paper_excursion_decomposition.py","scripts/paper_anchor_correction_quantified.py","scripts/check_paper_replay_fence.py","docs/paper/results-fill-registry.md","docs/paper/round7/fill-checklist.md","docs/paper/fill-rehearsal-2026-08-27.md","docs/guides/tutorial-replicate-the-calibration-bound.md","tests/test_paper_excursion_decomposition.py","tests/test_paper_round7_artifacts.py","tests/test_paper_replay_fence.py"]

# Fix-round brief — ICLOUD-BACKUP-PROBE-01, Opus contract-refuter findings (gpt-6-astra, medium)

HEAD = c3488fb8 on fix/2026-09-08-icloud-backup-probe. Astra execution refuter: clean. Opus contract refuter (trace
47): LAND-WITH-FIXES. Cure C1, C2, C3 (required); C4, C5 (cheap, do them); C6, C7 optional. Findings verbatim:

C1 should-fix — `docs/paper/results-fill-registry.md:778,781`: provenance chain broken by the re-pin. XS now reads
"supersedes 8733ff03… from 49b258d2, #240" but the digest actually superseded is `12d0293b…`, which now appears
nowhere in the registry. AS reads `3f4f4f12… (b36d1e85, #272; …)` — that commit/PR landed `e3e4355c…`, so the
parenthetical attributes the NEW bytes to a commit that does not contain them. Both prior re-pins recorded the
superseded digest explicitly. Cure: each pin line records the new digest, the dated 2026-09-08 ICLOUD-BACKUP-PROBE-01
note, and "supersedes <immediately-previous digest> (its commit/PR)" exactly in the established form; keep the
older lineage text after it.

C2 should-fix — `JOULEWISE_BACKUP_ROOTS` and the 2 s budget are documented only in code: absent from all three
USAGE docstrings, from `docs/paper/round7/fill-checklist.md:171`, `docs/paper/fill-rehearsal-2026-08-27.md:190`,
`docs/guides/tutorial-replicate-the-calibration-bound.md:125`, and the registry note. Cure: document the knob
(os.pathsep list; empty = no backup roots; default = the iCloud path), the per-root 2 s budget, and the failure
mode (an unresponsive or slow root contributes zero candidates with a `backup_root_unavailable` stderr line) in
each USAGE docstring and in those three docs by dated addendum lines (do not rewrite historical rehearsal records;
append).

C3 should-fix — the budget is per (root, call) covering `is_dir` + both globs cumulatively; a responsive-but-slow
root (> 2 s total) now yields zero candidates where it previously matched. Real behaviour change; document it with
C2 (state plainly that a slow backup root is skipped, that retained artifacts are byte-pinned so a skip fails
closed at the pin check, and that the prior behaviour was an unbounded hang).

C4 nit — `paper_excursion_decomposition.py:172` (and the two copies): `return result[0]` raises IndexError if the
worker raises anything other than OSError, contradicting "contributes no candidates". Cure: treat any worker
exception as unavailable (reason=worker_error) — keep the three copies verbatim-identical.
C5 nit — no test asserts byte-identity of the three helper copies. Cure: one test that extracts the helper block
(between its "Kept verbatim in all three" marker and `return result[0]`/the new final line) from each script and
asserts the three sha256 are equal.
C6/C7 optional (unreachable os_error branch; import order).

IMPORTANT sequencing: editing the docstrings changes the producers' bytes, so the XS and AS pins must be recomputed
AFTER all script edits (sha256 of the final file bytes) and written per C1; then run the complete round-7 module
with `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise` (never skip the golden replay) and report byte-identity of XD, F4,
AQ. Acceptance = `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest
tests.test_paper_excursion_decomposition tests.test_paper_replay_fence tests.test_paper_round7_artifacts` to a
log with rc. Never touch the real iCloud path; never the repository-wide suite; no `git commit`; header < 8192
bytes; genre implementation verdict keys; body = per-finding cure, the final pin lines verbatim, acceptance rc.
