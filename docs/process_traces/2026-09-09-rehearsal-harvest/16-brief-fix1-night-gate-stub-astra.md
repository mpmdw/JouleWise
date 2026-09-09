WRITE_SCOPE: ["joulewise/night_gate.py","tests/test_night_gate.py","tests/test_run_night.py","docs/contracts/pack_night_go_receipt.md"]
SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Fix round 1 — NIGHT-GATE-STUB-CHAIN-01 (gpt-6-astra, medium, genre implementation)

You are on branch fix/2026-09-09-night-gate-stub-chain at bb7090e2 (your worktree). The Opus contract review
/Users/edr/code/JouleWise-wt-magistrate-1ef89702/docs/process_traces/2026-09-09-rehearsal-harvest/10-ref-stub-opus-contract-review.md
(read S1, S2, S3, N1 there) is triaged by the magistrate as follows. Dispositions are dictated; do not widen.

S1 (ACCEPT) — in `evaluate_night`, the C5 `measured["detail"]` sentence for the REHEARSAL_STUB branch must not claim a chain check.
Closure shape: on the stub branch set the detail to exactly
`"window, plan freshness, and measurement HEAD passed; chain identity not evaluated (driver substitutes the built-in stub)"`;
the non-stub detail string stays byte-identical. Pin the stub string with an assertEqual in
`test_rehearsal_stub_does_not_read_missing_chain_or_sidecar`, and pin the unchanged non-stub string in an existing or new
DIAGNOSTIC_NO_PACK green-receipt test.
N1 (ACCEPT) — keep `chain_path` and `chain_sha256_path` in the stub's C5 `measured` (values from the plan) alongside
`chain_sha256: None`, `expected_chain_sha256: None`, `chain_stub: "built_in_stub_by_design"`; assert both keys in the stub test.
Evidence list for the stub stays as it is (no chain citations).
S3 (ACCEPT) — add a subtest/test: a REHEARSAL_STUB plan evaluated against a plain `FakeProbeSource(chain_digest="0" * 64)` (chain
present, sidecar deliberately mismatched — the same source shape that makes `make_plan()` refuse `night_chain_digest_mismatch` in
the existing sidecar tests) still yields REHEARSAL_ONLY, refusal None, and neither chain path in `read_calls`. Counterfactual to
state in your report: an implementation that reads the chain when it exists would fail this test with night_chain_digest_mismatch.
S2 (ACCEPT, LAST STEP) — the diff displaced §9 traceability pins in docs/contracts/pack_night_go_receipt.md. After all code/test edits
above are final, repin mechanically using the 99gj method: parse every pin matching
`` `([A-Za-z0-9_./-]+\.(?:py|sh|json|md)):(\d+)(?:[–-](\d+))?` `` optionally followed by `` (`symbol`) `` whose file is one of
joulewise/night_gate.py, scripts/run_night.py, tests/test_night_gate.py, tests/test_run_night.py; for symbol pins relocate to the
symbol's DEFINITION line at your final head; for bare line/range pins identify the described code by content at the OLD line
(as of 83ab38ed: use `git show 83ab38ed:<file>`) and relocate; rows explicitly recorded "at <sha>" are frozen — do not touch;
anything you cannot relocate unambiguously stays as is and is listed as unresolved. Report counts: total pins in those four files,
repinned (old → new, symbol), frozen, unresolved. Opus listed eleven known-displaced pins at contract lines ~236, 853, 858, 861,
952, 1025 — those must all be resolved.
S4, N2, N3, N4 — NO CHANGE (magistrate records S4 in the harvest record; the rest are accepted as-is).

Acceptance: `python3 -m unittest tests.test_night_gate tests.test_run_night tests.test_docs_freshness tests.test_gen_state` to a
log with rc (named modules only, never discover). `git diff --check`. No `git commit`. Header < 8192 bytes; genre implementation
verdict keys; body = per-item closure + counterfactual + the exact test tails with rc + the repin table.
