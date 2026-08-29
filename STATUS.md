# S14 stream status — feat/pinset-refresh-row-lane (D-161 reviewed refresh lane)

- DONE: rounds 1-2 + FIX-1..6 + bench cure of S14-F1 (identity-based write fence) and S14-F2 (write-intent guard); PR #228 open. Pinset bytes UNCHANGED (PINSET_SHA256 literal untouched).
- NEXT: Sol high read-only delta check over the bench diff -> push -> CI foreground -> magistrate review. Do NOT merge; do NOT run the lane against the real `_v3` row here (S8 does that on #209).
- Scratch: /private/tmp/claude-501/-Users-edr-code-JouleWise/5ce660ee-d53f-472d-98bc-e236206db99d/scratchpad/s14 (impl.prompt.md, impl.md report).
- S8 commands (after this PR merges, on #209 rebased onto main; both must be pushed first — the lane refuses an unpublished HEAD):
  FIRST reset Ed's two hand-edited files to main's bytes (`git checkout origin/main -- configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json tests/test_receipt_histsem.py`, re-apply any S8 test edits), then:
  `python scripts/refresh_receipt_histsem_pinset.py --repository-root . --refresh-row d117_contrast_qwen25_1p5b_vs_7b_v3 --print-pinset-sha256 --write-test-pin tests/test_receipt_histsem.py`   (expected pinset SHA 3e513c53…8543; floor _v3 rows are current)
  `python scripts/refresh_receipt_histsem_pinset.py --repository-root . --refresh-tool-sidecars`   (expect 4x "already current")
  then `python scripts/verify_receipt_histsem.py --repository-root . --require-published` must PASS; commit pinset + test pin + sidecars together.
