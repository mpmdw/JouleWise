# 08d — Installer rounds 6 → 6b → 6c (magistrate b0ae8462, 2026-09-15 22:25 PDT)

- Round 6 `6d4c2fc0`: F1 (shell `_given`-flag forwarding + module empty-value refusal), F2(a)(c), F3 docs (report 08).
- Round 6b `4114349a`: cold-gate ruling 10 as synthesised in packet 06 record 13 — `raised_once` handler, `while True`
  signal-safe block, outer `except Signalled` in `run()` with `resolved`, guaranteed restoration with dispositions
  restored BEFORE the mask; two flags ruled (report 08b).
- Round 6c `efdaed87`: teardown exceptions contained in `_unwind` (RETAINED, exit 1, warning
  `teardown failed; retained: <type>: <message>`); uninstall's inline cleanup already guarded (report 08c). The seat's
  full-module run under heavy load showed two `test_retention_product` cells (commit_refusal × hang / rc9) ending at
  VALIDATED instead of VERIFIED, green on focused replay → round 6d (root cause, tests only, running) before the PR;
  cold-gate Q5 execution lens (real signals, both interpreters) and the delta re-audit of rounds 6–6c are running in
  parallel on `efdaed87`.
