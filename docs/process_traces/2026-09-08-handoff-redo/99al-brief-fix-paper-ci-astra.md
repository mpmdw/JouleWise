WRITE_SCOPE: ["docs/paper/round7/fill-checklist.md","tests/fixtures/d165_rationale_allowlist.json"]

# Fix round — PR #301 (paper S1+S6+S7) CI red (gpt-6-astra, medium, genre implementation)
Head 83f61672 on int/2026-09-08-paper-s1-s6-s7. Two failure families, both caused by S7's rewrite of
docs/paper/round7/fill-checklist.md and S1's insertions in docs/paper/results-fill-registry.md:
1. tests/test_paper_round7_artifacts.py `_checklist_standing_sentence` (line ~1292) splits the checklist on the exact
   marker "  The mandatory standing sentence is:\n\n" and reads the following blockquote (lines prefixed "  > ") up to
   the next blank line; four TypedArtifactCliTests error with IndexError because S7 removed that block. CURE: restore
   the block VERBATIM from `git show main:docs/paper/round7/fill-checklist.md` lines 35–43 (the R7F sentence, the DX
   prose-region sentence, the marker line and the quoted sentence with the exact two-space + "> " prefixes and the
   curly quotes) inside the "Preserved historical replay fences" item of the new checklist, as its own indented
   paragraph immediately after the sentence that names the mandatory DX diagnostic standing sentence. Do not change
   the wording of the sentence by one character; do not restore any other pre-S7 text; keep S7's guidance intact.
2. tests/test_d165_rationale_census.py: `allowlist_keys` raises "Stale allowlist entries" for eleven (file, line,
   term) keys in tests/fixtures/d165_rationale_allowlist.json — five `common-time` entries in
   docs/paper/results-fill-registry.md (lines 264–297 shifted by S1's insertions) and six in fill-checklist.md
   (lines 63, 143, 207–231; the occurrences may no longer exist after S7). CURE: for each stale entry, locate the
   SAME retained occurrence at its new line (registry: same sentence, shifted) and update the line; for checklist
   entries whose occurrence S7 removed, DELETE the entry (do not re-add retired rationale to satisfy the allowlist).
   If the restored standing-sentence block re-introduces an allowlisted term, add the entry with the ORIGINAL
   reason text copied from the deleted entry. Keep the JSON formatting/ordering conventions of the file.
Acceptance (rc-gated to a log, never piped): `PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest tests.test_paper_round7_artifacts tests.test_d165_rationale_census tests.test_paper_successor_migration tests.test_docs_freshness`;
`git diff --check`; no commit; header < 8192 bytes; report per finding: what moved where, with before/after line numbers.
