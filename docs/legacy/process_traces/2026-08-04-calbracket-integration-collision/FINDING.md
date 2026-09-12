# Integration collision: D-109's mint threading vs the byte-frozen generalized-mint interface guard

Found 2026-08-04 ~01:15 by the lead while gating the CAL-BRACKET review
branch (`impl/cal-bracket-d079` @ `c2f81d4`). **Its PR CI is RED and the
branch was NOT merged.** Neither tree is defective in isolation; the
collision exists only on the merge ref.

## Mechanically proven diagnosis

Integration tree composed at the bench (`git worktree add --detach` at
`main`, then `git merge impl/cal-bracket-d079` — merged cleanly, no
conflicts), then the failing module run with a writable TMPDIR:

`tests.test_mint_floor_artifact_generalized` → **Ran 18, FAILED
(failures=4, errors=6)**. All ten failures cite ONE cause (14
occurrences of the message):

> byte-frozen mint core interface drift: mint_floor_artifact signature
> expected (…, consumption_semantics_id: 'str | None' = None) ->
> 'Mapping[str, Any]', observed (…, consumption_semantics_id:
> 'str | None' = None, **calibration_ledger_snapshot:
> 'CalibrationLedgerSnapshot | None' = None**) -> 'Mapping[str, Any]'

- **Branch side (legitimate):** D-109's implementation commit `8383113`
  added the `calibration_ledger_snapshot` parameter to
  `mint_floor_artifact` (and to `_authenticated_consumption_summaries`
  and `_authenticate_component`). This is REQUIRED by D-109 R1.4 —
  "threads ONE immutable ledger snapshot through every consumer path" —
  and the delta re-audit verified that threading as correct.
- **Main side (legitimate):** `scripts/mint_floor_artifact_generalized.py`
  (MINT-GENERALIZE-01) holds a byte-frozen expectation of the core mint
  signature and refuses loudly on any drift. The guard is working as
  designed: it forced a human to notice an interface change to claim
  machinery.

## Why every prior check missed it

`scripts/mint_floor_artifact_generalized.py` and
`tests/test_mint_floor_artifact_generalized.py` DO NOT EXIST in the
branch tree (the branch is based on `a14d1fe`, which predates them). So
those tests could not run in the branch's own suites, in the delegated
verification, or in the lead's independent replay — all three ran the
branch tree, where the module is absent. Only the merge ref has both.
**This is the exact failure class the standing "integration tree before
any merge wave" rule exists for**, and it is the first time that rule
has caught something here rather than merely being observed.

## Why the lead did NOT fix it overnight

Updating the frozen expectation is the mechanically obvious move and is
probably correct — but it is design-bearing on CLAIM-MINTING machinery:

1. One casualty is `test_mint1_full_path_is_byte_identical_to_byte_frozen_core`.
   The guard protects byte-identical mint replay — the very property
   established empirically on 2026-08-03 (Q1 byte-compare,
   `docs/process_traces/2026-08-03-q1-remint-bytecompare/`). Whether
   threading a new parameter through the core changes replay byte
   identity is a question that must be ANSWERED, not assumed.
2. D-110 made mint #1 non-claim-bearing precisely because mint
   machinery had been trusted without the calibration allowance being
   right. Re-minting is gated on this row landing. Quietly relaxing a
   mint interface guard on the way to that landing is the wrong shape.
3. MINT-GENERALIZE-01 remains open with lead-reserved live mint steps.

## Recommended shape (successor's first decision; not yet ruled)

1. Update the byte-frozen expectation in
   `scripts/mint_floor_artifact_generalized.py` to the new signature,
   as a deliberate, reviewed interface amendment — with a test pinning
   the NEW signature and a note recording why it changed (D-109 R1.4
   snapshot threading).
2. **Answer the byte-identity question with evidence, not argument:**
   re-run the pinned mint-1 replay byte-compare on the integration
   tree. If the artifact/statement digests still reproduce
   byte-identically, the amendment is safe and the record says so; if
   they do not, that is a genuine finding and the merge waits on a gate.
3. Verify `test_core_signature_drift_refuses_loudly` still fails on a
   synthetic drift after the expectation is updated — the guard must
   keep its teeth.
4. Then re-run the integration tree's full suite, push, and merge on a
   green PR CI.

Reproduce the integration tree with:

```sh
git worktree add --detach <scratch>/integ-calbracket main
cd <scratch>/integ-calbracket && git merge impl/cal-bracket-d079
TMPDIR=<writable> .venv/bin/python -B -m unittest tests.test_mint_floor_artifact_generalized
```

## Process finding (for the council log)

The lead's rule-1 replay ran in the BRANCH tree, which cannot execute
tests that exist only on main. A lead replay should run on the
INTEGRATION tree (main + branch) whenever the branch is behind main, or
it verifies a tree that will never be merged. This is a real gap in how
the lead has been discharging rule 1, not a one-off — and it was caught
only because CI tests the merge ref.

Separately: the same CI run initially failed on a docs-freshness pin
because the lead's own README handoff banner copied two volatile
literals (an orchestration model name and a PR number) into a current
section. Fixed by rewording. That test class has now caught the lead
twice; the banner-writing habit should default to naming no models and
no PR numbers.
