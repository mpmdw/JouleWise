# S14 stream status — feat/pinset-refresh-row-lane (D-161 reviewed refresh lane)

- DONE (WIP, Sol round 1 in flight): scripts/refresh_receipt_histsem_pinset.py (+ .sha256), tests in tests/test_receipt_histsem.py, contract amendment in docs/contracts/receipt_histsem_verifier.md. Pinset bytes UNCHANGED on this branch (PINSET_SHA256 literal untouched).
- NEXT: (1) Sol round 2 = R-1 addendum: `--refresh-tool-sidecars` for the four custody-tool sidecars (tests/test_family_marker.py:788-794); (2) audit -> two refuters -> delta re-audit; (3) rebase on origin/main, push, PR, CI. Do NOT merge; do NOT run the lane against the real `_v3` row here (S8 does that on #209).
- Scratch: /private/tmp/claude-501/-Users-edr-code-JouleWise/5ce660ee-d53f-472d-98bc-e236206db99d/scratchpad/s14 (impl.prompt.md, impl.md report).
- S8 commands (after this PR merges, on #209 rebased onto main; both must be pushed first — the lane refuses an unpublished HEAD):
  `python scripts/refresh_receipt_histsem_pinset.py --repository-root . --refresh-row d117_contrast_qwen25_1p5b_vs_7b_v3 --refresh-row d117_floor_qwen25_1p5b_v3 --refresh-row d117_floor_qwen25_7b_v3 --write-test-pin tests/test_receipt_histsem.py`
  `python scripts/refresh_receipt_histsem_pinset.py --repository-root . --refresh-tool-sidecars`   (once round 2 lands)
  then `python scripts/verify_receipt_histsem.py --repository-root . --require-published` must PASS; commit pinset + test pin + sidecars together.
