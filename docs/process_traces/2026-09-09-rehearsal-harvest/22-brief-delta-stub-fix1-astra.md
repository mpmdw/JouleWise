SESSION_MODE: delegated
WRITE_SCOPE: []
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Delta re-audit — NIGHT-GATE-STUB-CHAIN-01 fix round 1, bb7090e2 → 5db38b5816bce05b67cabfe3eb621bf2b22aa3e6 (gpt-6-astra, medium, genre review, read-only)

Opus contract review (read): /Users/edr/code/JouleWise-wt-magistrate-1ef89702/docs/process_traces/2026-09-09-rehearsal-harvest/10-ref-stub-opus-contract-review.md
Fix brief (dictated closures): .../16-brief-fix1-night-gate-stub-astra.md; seat report: .../17-seat-fix1-night-gate-stub-astra-report.md.
Audit ONLY `git diff bb7090e2..5db38b5816bce05b67cabfe3eb621bf2b22aa3e6`:
1. S1: the stub detail string equals the dictated sentence byte-for-byte; the non-stub string is byte-identical to bb7090e2; both pinned by
   assertEqual in tests.
2. N1: stub C5 measured carries chain_path/chain_sha256_path from the plan; evidence list unchanged (no chain citations).
3. S3: the new present-but-mismatched test — run it against the bb7090e2 gate (import `git show bb7090e2:joulewise/night_gate.py` as an
   alternate module, as the earlier execution refuter did) and confirm it PASSES there too (it should: bb7090e2 already skipped the read) —
   then confirm it would FAIL against a gate that reads the chain when present: monkeypatch the head module so the stub branch is bypassed
   (e.g. temporarily evaluate with receipt_class check inverted in an in-memory copy) and show the night_chain_digest_mismatch failure.
4. S2 repin: for every pin in docs/contracts/pack_night_go_receipt.md naming joulewise/night_gate.py, scripts/run_night.py,
   tests/test_night_gate.py or tests/test_run_night.py — symbol pins must land on the symbol's definition line at this head (report
   counts); for the 38 bare line/range pins, sample at least 10 (include contract lines ~236 and ~1025) and confirm the described code is at
   the new line by content, comparing with 83ab38ed. Confirm no pin naming any OTHER file changed in the diff (`git diff` restricted to
   lines mentioning other paths must be empty).
5. Same-signature statement (a claim/pin/test that does not do what it says): "same signature: none" or name it.
Read-only; no edits. Report claude-codex-report/v1, genre review, header < 8192 bytes; body = disposition per item with command tails.
