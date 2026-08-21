```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"Make an unambiguous pinset-path absence at HEAD return to ordinary readiness; receipt-shape tripwires are unsound eligibility classifiers.","workspace":{"base_requested":"99a2b99","base_mode":"exact","head_start":"99a2b997a60c34e2e966c53c978486f9e075f4bb","head_end":"99a2b997a60c34e2e966c53c978486f9e075f4bb","upstream_end":"99a2b997a60c34e2e966c53c978486f9e075f4bb","branch":"impl/receipt-histsem"},"pathspec":[],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"blocker","title":"The v1 receipt-shape tripwire violates the pinset-only eligibility rule","evidence":"The focused T-0 fixture fails before ordinary readiness with histsem_pinset_absent; the canonical run has 16 failures and one error with the same substitution.","recommendation":"On an unambiguous absent-at-HEAD diagnostic, return. Retain refusal for every other git-show failure and determine engagement only from a successfully read, validated HEAD pinset."}]},"verification":[{"id":"V1","kind":"test","cmd":"python3 -m unittest -v tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_arm_consumes_volatile_receipts_within_short_horizon","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 1 test in 2.618s","FAILED (failures=1)"]},"expected":{"exit_code":0,"tail_regex":"Ran 1 test .*\\n\\nOK"}},{"id":"V2","kind":"inspection","cmd":"git status --short --branch && git rev-parse HEAD && git rev-parse --abbrev-ref HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["## impl/receipt-histsem...origin/impl/receipt-histsem","99a2b997a60c34e2e966c53c978486f9e075f4bb","impl/receipt-histsem"]},"expected":{"exit_code":0,"tail_regex":"impl/receipt-histsem"}}],"flags":[{"id":"F1","kind":"residual_risk","level":"nonblocking","text":"Without a HEAD pinset, an in-library call cannot distinguish a synthetic/pre-governance repository from a repository whose committed pinset was removed.","needs":"Keep committed pinset mutation/deletion detection in the byte-pin and changed-set CI controls, and document this boundary."}]}
```

## Findings

### F1 — blocker: return on pinset absence at HEAD

Recommend one design: an unambiguous `git show HEAD:<pinset>` path-absent result must return to ordinary readiness. Do not add an eleven-`freeze-*` tripwire.

The three meaningful states are:

- Successful HEAD read: validate the pinset; only `(pack_id, pack_path)` membership engages histsem. Receipt contents never decide engagement or disengagement.
- Exact path-absent-at-HEAD diagnostic: return. This is an explicit no-governance answer, not an operational lookup failure.
- Any other nonzero Git result: refuse, as today.

Exact code shape in `_gate_receipt_histsem`:

    if code != 0:
        if _histsem_pinset_path_absent_at_head(_stderr):
            return
        raise HistoricalSemanticsError(
            "histsem_history_unavailable",
            "committed receipt-histsem pinset lookup failed",
        )

Delete `_histsem_has_legacy_v1_receipt`; it has no sound role. Keep `_histsem_pinset_path_absent_at_head` to distinguish an explicit absence from Git/object-store failure.

The focused failing T-0 test creates and commits a synthetic Git pack, authors valid volatile evidence, and expects `PASS`; it instead gets `histsem_pinset_absent`. The canonical log shows the same masking in the expiry tests (expected `readiness_record_expired`) and all three integration profiles (expected `PASS`), plus an error where the ordinary refusal receipt was never written.

An exact eleven-row inventory is not justified: it again makes receipt content determine eligibility, can falsely classify a synthetic fixture that reproduces that shape, and can be bypassed by deleting or changing the inventory along with the pinset. It is neither sound nor load-bearing compared with the committed byte-pin and changed-set controls.

Round-2 regressions:

- Keep `test_gate_refuses_when_governed_clone_object_store_is_unreadable`.
- Adjust `test_committed_pinset_deletion_refuses_before_arm_custody` to assert that the library gate returns on an absent HEAD path; retain deletion detection in the CI byte-pin/changed-set tests instead.
- Adjust `test_synthetic_pack_without_pinset_or_legacy_receipts_stays_ordinary` to include a well-formed v1 T-0 receipt and assert the ordinary path’s expected result. The existing short-horizon T-0 test is a suitable integrated regression.
- Keep the round-1 worktree-deletion check: HEAD membership still engages the gate, and the later filesystem pinset read refuses rather than letting deletion disengage it.

Replace the contract’s current “Eligibility lookup is fail-closed…” paragraph with:

> Eligibility is based only on a successful `git show HEAD:<pinset>` read: after canonical validation, membership of `(pack_id, pack_path)` engages the gate and a membership miss returns normally. An unambiguous result that the pinset path does not exist in `HEAD` also returns to ordinary readiness; it is an absence-of-governance answer, not a `histsem_pinset_absent` refusal. In that state the library must not inspect receipt schemas, names, counts, or inventories. Any other failure to obtain the HEAD pinset refuses, and an invalid HEAD pinset refuses. The HEAD read prevents worktree pinset deletion from disengaging a pack whose HEAD row exists. Committed pinset mutation or deletion is owned by the byte-pin and changed-set CI controls. Residual: absent a HEAD pinset, the library cannot distinguish a synthetic/pre-governance repository from a history whose pinset was removed.

## Residual risk

A committed deletion can reach an ordinary-readiness library call before CI rejects it. That is unavoidable without an external immutable governance anchor; a receipt-based heuristic does not close it and breaks legitimate synthetic repositories.