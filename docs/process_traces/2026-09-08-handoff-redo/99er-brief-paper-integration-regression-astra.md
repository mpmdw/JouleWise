WRITE_SCOPE: ["tests/test_paper_round7_artifacts.py"]

# Paper integration — pin the malformed-history refusals (gpt-6-astra, medium, genre implementation)
Branch int/2026-09-08-paper-s2-s3-s7 at 21331ac9. The Opus integration review at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99eq-integration-review-paper-opus.md finding 6: scripts/check_paper_round7_artifacts.py ~:266–278 now selects dated
retirement notes by marker with a `len(cells) in (5, 6, 7)` shape heuristic; the regression at
tests/test_paper_round7_artifacts.py ~:372 pins only the proposal-skip and DS-09 detection. Add ONE regression (or two
subcases) asserting `RegistryError` on (a) an undated historical retirement row and (b) a double-dated historical row,
built from a real DS-09-shaped row so a future widened heuristic or an 8-column historical table cannot silently
disable the refusal; do not touch the checker. Acceptance (rc-gated; named modules ONLY, never discover/shard; env
JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise): tests.test_paper_round7_artifacts; git diff --check;
no commit; header < 8192 bytes; report the two counterfactuals executed against the checker.
