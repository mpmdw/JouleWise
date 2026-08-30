# Estate 11 — HALT at §1.1 (anchor-map re-check)

**Estate:** 11, cut 2. **BASE** `0438566b43e8848b8712b63270bbf857e5b76013`
(newest `main` head with a completed/success CI run — run `33330773736`, 19:24:17Z —
and the first such head containing BOTH PR #209 (merge `4ea105b0`) and PR #228).
**Halted at:** runsheet r4 §1.1, third block, the anchor-map re-check.
**Transcript:** `e11-2/s0-clone-proof-r4/custody/transcripts/005-anchor-map.json`
(status `REFUSE`, `matched: 4/15`); block log `032-anchor-map-verbatim.log`
(`S-0 STOP: anchor map drifted at BASE; see 005`, rc 1).

The runsheet's own rule for this block: *"Any mismatch is a precondition defect:
stop, re-derive the map on main through the ordinary review lane, and restart
from a fresh estate."* The estate stopped there and did not enter the
transaction. Nothing was minted, no pack was materialised, no freeze ran.

## Classification: PROCEDURE DRIFT — the estate-11 delta is INCOMPLETE

Not an instrument defect: the code at BASE is healthy and every mismatch traces
to a reviewed, deliberate change on `main`. Not an environment defect: the clone,
venv, BASE gate and delta sidecar all passed.

The estate-11 delta (`docs/process_traces/2026-08-27-t26/d139-families/01-estate-11-delta.md`)
carries three streams' deltas — W-10's mint-path predicate, D-154 R-3's
`--measurement-checkout` declaration, and the S3 D6 builder-digest re-pin. It
does **not** carry PR #228's effect on the anchor map, and PR #228 renamed one of
the two symbol anchors r5 added.

### The eleven mismatches, split by kind

**(a) Ten are pure line drift** — every one of these anchors still exists under
its pinned name and pinned text; only its line number moved. The delta already
anticipates this class ("every anchor below is position-dependent … re-derive
them at the reviewed head") and supplies no obstacle to re-deriving them. Derived
mechanically by name at BASE (`031-anchor-derivation-cut2.json`):

| Anchor (owner) | Delta claim | Derived at BASE | Shift |
|---|---|---|---|
| `EvidenceLifecycleError` | 1050 | 1060 | +10 |
| `validate_registry` (statement) | 2025 | 2035 | +10 |
| `_gate_receipt_histsem` | 3753 | 4026 | +273 |
| `_r1_changed_paths` | 4229 | 4534 | +305 |
| `validate_r1_evidence_lifecycle` (statement) | 4426 | 4731 | +305 |
| `_admit_bound_analysis_manifest` | 4966 | 5271 | +305 |
| `_authenticate_generic_evidence_item` | 5504 | 5841 | +337 |
| `_load_freeze_reference` | 6570 | 7113 | +543 |
| `generate_freeze_receipt` | 6844 | 7390 | +546 |
| `generate_freeze_receipt` (statement) | 6885 | 7439 | +554 |
| `test_verifier_cli_refusal_is_canonical_and_exit_two` | 220 | 283 | +63 |

All eleven derived lines match their pinned text exactly. The five anchors the
delta left at r4 coordinates (`identity_pins.py:1826`, the three script `_parser`
/ `parse_args` anchors) are unmoved and matched.

**(b) One is NOT recoverable by re-deriving a number**, and this is the halt:

```
tests/test_receipt_histsem.py:160  symbol  test_pinset_is_byte_pinned_and_has_no_update_lane
  -> NO definition of that name exists anywhere in the file at BASE
```

PR #228 (`1f046cd9`, merged 2026-08-29) **renamed** it:

```
test_pinset_is_byte_pinned_and_has_no_update_lane
  ->  test_pinset_is_byte_pinned_and_has_no_unreviewed_update_lane      (lines 200-229)
```

The rename is substantive, not cosmetic. #228 installed a *reviewed refresh lane*
for the histsem pinset (`ReceiptHistsemRefreshLaneTests`, ~20 new tests from line
885). The old pin asserted the pinset had **no update lane at all**; the pinset
now has one, so the assertion had to narrow to **no *unreviewed* update lane**.
Choosing which invariant the runsheet pins is a review-lane decision about what
the instrument asserts, not a coordinate the operator may silently re-derive —
which is why this halts rather than being carried.

This is the anchor map doing exactly the job r5 added it for (Opus F13): a symbol
anchor failing **by name** on a shift no line-number check could see.

### Two other r4 coordinates the same PR invalidated (found while deriving; not
themselves gate failures, because no mechanical check reads them)

- §0.3 pinned-mechanics map: `PINSET` is `tests/test_receipt_histsem.py:32` and
  `PINSET_SHA256` is `:33` in r4. At BASE they are **`:44` and `:45`**.
- §0.3 cites the two test methods at `:160-166` and `:220-238`. At BASE the
  renamed method is **`:200-229`** and the verifier method is **`:283-301`**.
- §1.1's immutable line-audit range `'tests/test_receipt_histsem.py 30,33p;160,166p;220,238p'`
  is stale in all three of its ranges and must be re-derived with the rest.

The §1.1 line audit would **not** have caught any of this: it asserts only that
its extract is non-empty, which is the precise blind spot F13 recorded.

## What the estate-11 delta needs before estate 12

1. Re-derive all 16 anchors at whatever head estate 12 runs (they move on nearly
   every merge to `arm_readiness.py` — +554 lines at the far end in three days).
   Pin them by symbol, and treat the numbers as derived-at-cut, never as text.
2. Rule on anchor #14: adopt `test_pinset_is_byte_pinned_and_has_no_unreviewed_update_lane`
   as the pinned symbol, and update the §0.3 prose that describes it as asserting
   "no update lane" — the pinset now has a reviewed one.
3. Re-derive the §0.3 immutable-audit range list for `arm_readiness.py` as well.
   The delta's replacement list (`…4966,5058p;5309,5358p;…`) was derived at the
   T26 head and is already stale by +305…+554 at BASE.
4. Carry PR #228 into the delta explicitly. The delta's own append-discipline
   note names two co-owning streams; #228 is a third that touched pinned surface
   and never appended a section.
