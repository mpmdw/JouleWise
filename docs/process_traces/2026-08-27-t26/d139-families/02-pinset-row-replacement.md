# The corrected `_v3` histsem pinset row — derivation and proof

**Status: VERIFICATION MATERIAL ONLY (D-161).** Ed does not hand-edit the pinset
again. Stream S14's reviewed `--refresh-row` lane on the pinset builder produces
the actual edit; this file is the independently derived answer that lane's output
is checked against. If the lane emits a row that differs from the block below in
any byte, one of the two is wrong and the difference is the finding.

Derived at branch head `d8f7e6a1` (Ed's two-line pin edit), in
`/Users/edr/code/JouleWise-wt-s8-d139-families`.

## 1. The refusal

`python scripts/verify_receipt_histsem.py --repository-root . --require-published`

```json
{
  "detail": "post-authoring delta differs from the governed per-pack envelope",
  "reason_codes": [
    "histsem_post_authoring_delta_unexpected"
  ],
  "schema_version": "joulewise.receipt_histsem_verification.v1",
  "status": "REFUSE"
}
```

Ed's edit was correct and was not the problem: `current_pack_sha256` now matches
the recomputed tree digest, so that check passes and the verifier moves on to the
next one and refuses there. A pinset row is a conjunction — fixing one member
only reveals the next stale member.

## 2. What is actually stale — measured, not asserted

The scope note called the cure "re-derive that one row's `current_pack_sha256`".
That was wrong, and the magistrate's correction — "it is the whole row" — is the
right posture for anyone applying it. The measurement is narrower than either
statement: comparing the pinned row against the values the verifier's own code
path computes, **exactly one field differs, by exactly one string.**

`post_authoring_delta.modified` is pinned as

```json
["plan_tree.json", "plan_tree.sha256"]
```

and `joulewise/arm_readiness.py:_histsem_delta` now computes

```json
["generate_configs.py", "plan_tree.json", "plan_tree.sha256"]
```

because W-10 modified the gamma generator, which lives inside the pack root, and
`_histsem_delta` diffs the whole pack path from the row's `head_commit` to `HEAD`.
`generate_configs.py` sorts first, so the new entry is the array's first element.

Every other field is unchanged and must stay unchanged — `historical_pack_sha256`
and `head_commit` above all, since they name the pre-authoring coordinate this row
exists to bind. `plan_sha256` and `plan_tree_sha256` are also untouched: W-10 did
not regenerate any `_v3` pack file, it only edited the generator that emits the
`_v4` successor.

That the code-level envelope permits this is not an accident.
`_HISTSEM_ALLOWED_MODIFICATIONS` (`joulewise/arm_readiness.py`) names
`generate_configs.py` explicitly — a post-authoring generator edit is an
anticipated, admissible change. What the mechanism requires is that the row be
re-derived to record it, so the change is declared rather than silent.

## 3. How the row was derived

Not by hand. `_histsem_delta(repository, pack_path, head_commit)` — the same
function the verifier calls at the comparison site — was invoked directly with the
row's own `pack_path` and `head_commit`, and its return value was substituted into
a deep copy of the row.

## 4. Proof

**(a) In-memory row substitution.** `verify_receipt_histsem_pack` accepts
`_pinset_rows`, so the corrected row was verified without writing the file:

```
VERIFY WITH CORRECTED ROW: PASS  receipts=11  advisories=[]
fields that differ from the committed row: post_authoring_delta   (only)
```

**(b) Scratch clone, outside the worktree.** `/private/tmp/s8-pinset-proof`, a
fresh clone at `d8f7e6a1`, with the one-line insert applied to the pinset and
`PINSET_SHA256` updated:

```
scripts/verify_receipt_histsem.py --repository-root . --require-published
  overall status: PASS, pack_count: 9
  all nine packs PASS, receipts=11 each, advisories=[] each

python -m pytest tests/test_receipt_histsem.py -q
  39 passed, 1 skipped, 150 subtests passed in 187.88s
```

The worktree's own pinset was never written.

## 5. The corrected row, verbatim

Lines **328–489** of `configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json`
become the 163 lines below (the object's own `    {` … `    },` bounds included).

```json
    {
      "current_pack_sha256": "6986bb496aed2b2b0329f79e1c2877ff4cb0ab537ca1be26ff7b7d65bb121d0a",
      "freeze_receipt": {
        "path": "arm_readiness.freeze.receipts/freeze-0003.json",
        "sha256": "f32bd3a8e4dbd04bc5b1635818ba34394984d1d201d16f02efc21f0b01f31c73"
      },
      "head_commit": "1d3873bb7a37e9363202429f14587c85a0b4efc0",
      "historical_pack_sha256": "07dff08b32006a0fc4be4c2f853a8284c19924fcf241edf0773faad1731a9ce2",
      "pack_id": "d117_contrast_qwen25_1p5b_vs_7b_v3",
      "pack_path": "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3",
      "plan_sha256": "56ed0e534f102ad6e0a1da12a4e2f9856ce4fe17e9d8af546bf2323f9d70bcb5",
      "plan_tree_sha256": "788f1a20bc5a22f073539e2d0b4df5ffd0b3e82d8b78015c7e668c0cbda8b5a7",
      "post_authoring_delta": {
        "added": [
          "arm_readiness.evidence/evidence-acceptance-owner.json",
          "arm_readiness.evidence/evidence-acceptance-owner.json.sha256",
          "arm_readiness.evidence/evidence-doctrine-pin.json",
          "arm_readiness.evidence/evidence-doctrine-pin.json.sha256",
          "arm_readiness.evidence/evidence-estimator-identity.json",
          "arm_readiness.evidence/evidence-estimator-identity.json.sha256",
          "arm_readiness.evidence/evidence-mint-trust.json",
          "arm_readiness.evidence/evidence-mint-trust.json.sha256",
          "arm_readiness.evidence/evidence-multicell-mint.json",
          "arm_readiness.evidence/evidence-multicell-mint.json.sha256",
          "arm_readiness.evidence/evidence-pack-authentication.json",
          "arm_readiness.evidence/evidence-pack-authentication.json.sha256",
          "arm_readiness.evidence/evidence-pack-family.json",
          "arm_readiness.evidence/evidence-pack-family.json.sha256",
          "arm_readiness.evidence/evidence-reason-code-coverage.json",
          "arm_readiness.evidence/evidence-reason-code-coverage.json.sha256",
          "arm_readiness.evidence/evidence-receipt-oracle.json",
          "arm_readiness.evidence/evidence-receipt-oracle.json.sha256",
          "arm_readiness.evidence/evidence-recovery-ledger-test.json",
          "arm_readiness.evidence/evidence-recovery-ledger-test.json.sha256",
          "arm_readiness.evidence/evidence-three-window-regression.json",
          "arm_readiness.evidence/evidence-three-window-regression.json.sha256",
          "arm_readiness.freeze.receipts/freeze-0003.json",
          "arm_readiness.freeze.receipts/freeze-0003.json.sha256",
          "arm_readiness.sources/acceptance-owner.json",
          "arm_readiness.sources/doctrine-pin.json",
          "arm_readiness.sources/estimator-identity.json",
          "arm_readiness.sources/mint-trust.json",
          "arm_readiness.sources/multicell-mint.json",
          "arm_readiness.sources/pack-authentication.json",
          "arm_readiness.sources/pack-family.json",
          "arm_readiness.sources/reason-code-coverage.json",
          "arm_readiness.sources/receipt-oracle.json",
          "arm_readiness.sources/recovery-ledger-test.json",
          "arm_readiness.sources/three-window-regression.json",
          "identity_pin_projection.receipts/projection-0001.json",
          "identity_pin_projection.receipts/projection-0001.sha256"
        ],
        "deleted": [],
        "modified": [
          "generate_configs.py",
          "plan_tree.json",
          "plan_tree.sha256"
        ]
      },
      "published_anchor": "docs/process/ed-s5-mint-decision-2026-08-19.md:78-84",
      "receipt_count": 11,
      "receipts": [
        {
          "evidence_id": "freeze-acceptance-owner-v1",
          "namespace": "PACK",
          "path": "arm_readiness.evidence/evidence-acceptance-owner.json",
          "receipt_kind": "ACCEPTANCE_OWNER",
          "schema_version": "joulewise.arm_readiness_evidence_receipt.v1",
          "sha256": "a38a22674ae03f244b2aab2fe8870fc0b670b069b11e326e7a8a8b78ac64eabd",
          "status": "PASS"
        },
        {
          "evidence_id": "freeze-doctrine-pin-v1",
          "namespace": "PACK",
          "path": "arm_readiness.evidence/evidence-doctrine-pin.json",
          "receipt_kind": "DOCTRINE_PIN",
          "schema_version": "joulewise.arm_readiness_evidence_receipt.v1",
          "sha256": "560be4354293cbf68de0e93b1d1ed39dec788f9e77d59f42467999c5713de6ec",
          "status": "PASS"
        },
        {
          "evidence_id": "freeze-estimator-identity-v1",
          "namespace": "PACK",
          "path": "arm_readiness.evidence/evidence-estimator-identity.json",
          "receipt_kind": "ESTIMATOR_IDENTITY",
          "schema_version": "joulewise.arm_readiness_evidence_receipt.v1",
          "sha256": "40366c608dd707fb0902984a0bc76137eafb1154a994c97edde4868574ef733b",
          "status": "PASS"
        },
        {
          "evidence_id": "freeze-mint-trust-v1",
          "namespace": "PACK",
          "path": "arm_readiness.evidence/evidence-mint-trust.json",
          "receipt_kind": "MINT_TRUST",
          "schema_version": "joulewise.arm_readiness_evidence_receipt.v1",
          "sha256": "202b34f9b28cac1d3e7644f9554e117ec7d4628406656c070082a0efeb006a5c",
          "status": "PASS"
        },
        {
          "evidence_id": "freeze-multicell-mint-v1",
          "namespace": "PACK",
          "path": "arm_readiness.evidence/evidence-multicell-mint.json",
          "receipt_kind": "MULTICELL_MINT",
          "schema_version": "joulewise.arm_readiness_evidence_receipt.v1",
          "sha256": "809e0576312f020095467d8afd8d67c561743ff1deb02ce3333a1a6bec78bc98",
          "status": "PASS"
        },
        {
          "evidence_id": "freeze-pack-authentication-v1",
          "namespace": "PACK",
          "path": "arm_readiness.evidence/evidence-pack-authentication.json",
          "receipt_kind": "PACK_AUTHENTICATION",
          "schema_version": "joulewise.arm_readiness_evidence_receipt.v1",
          "sha256": "5d8e49302b24ac6d5d4f9702e866a62c1d74fef16c9ab56bb86bb53f23c2bff8",
          "status": "PASS"
        },
        {
          "evidence_id": "freeze-pack-family-v1",
          "namespace": "PACK",
          "path": "arm_readiness.evidence/evidence-pack-family.json",
          "receipt_kind": "PACK_FAMILY",
          "schema_version": "joulewise.arm_readiness_evidence_receipt.v1",
          "sha256": "5f20272a7b1182c1bde0fb654ae45646e5ffd61d33c159b16d9328c7c465a108",
          "status": "PASS"
        },
        {
          "evidence_id": "freeze-reason-code-coverage-v1",
          "namespace": "PACK",
          "path": "arm_readiness.evidence/evidence-reason-code-coverage.json",
          "receipt_kind": "REASON_CODE_COVERAGE",
          "schema_version": "joulewise.arm_readiness_evidence_receipt.v1",
          "sha256": "5edec12940f174c1ea5df772c63bf20785e9dd30b0dffd29089b4fad5cea5228",
          "status": "PASS"
        },
        {
          "evidence_id": "freeze-receipt-oracle-v1",
          "namespace": "PACK",
          "path": "arm_readiness.evidence/evidence-receipt-oracle.json",
          "receipt_kind": "RECEIPT_ORACLE",
          "schema_version": "joulewise.arm_readiness_evidence_receipt.v1",
          "sha256": "8f3baad75e8ea9a28c27300977f1f4e12c62ad06af8542451531362d04faa833",
          "status": "PASS"
        },
        {
          "evidence_id": "freeze-recovery-ledger-test-v1",
          "namespace": "PACK",
          "path": "arm_readiness.evidence/evidence-recovery-ledger-test.json",
          "receipt_kind": "RECOVERY_LEDGER_TEST",
          "schema_version": "joulewise.arm_readiness_evidence_receipt.v1",
          "sha256": "d284ce389f2ee1c017cfcd607efac4b7775baedb675f41965d86b0f4c0338792",
          "status": "PASS"
        },
        {
          "evidence_id": "freeze-three-window-regression-v1",
          "namespace": "PACK",
          "path": "arm_readiness.evidence/evidence-three-window-regression.json",
          "receipt_kind": "THREE_WINDOW_REGRESSION",
          "schema_version": "joulewise.arm_readiness_evidence_receipt.v1",
          "sha256": "d84ce26e685e9f86e717670d2487bdd6c41cb04766f7abb2fe3f3e02ab2147dd",
          "status": "PASS"
        }
      ]
    },
```

## 6. The minimal edit, if it is ever applied by hand

The full-row replacement above and this one-line insert produce identical bytes.
In a web editor the insert is far less error-prone:

- **Insert one line after line 381** (`        "modified": [`), i.e. immediately
  before the existing `          "plan_tree.json",` on line 382:

```
          "generate_configs.py",
```

Ten leading spaces, matching its siblings. Nothing else in the file changes.

Resulting whole-file SHA-256:

```
3e513c535e3095bab44b53c029961aeb54baf1875df2bddd663e679482b38543
```

so `tests/test_receipt_histsem.py:42` `PINSET_SHA256` becomes that value,
replacing `a9de4ce60c8691ea49ff502f93f61bf6ffcb9d79ef59d1798ab07b50c4368329`.
Recompute rather than copy if the pinset changes again for any other reason.

## 7. Other literals affected — exactly one

`PINSET_SHA256` is the **only** 64-hex literal in `tests/test_receipt_histsem.py`
(line 42), and it is the only place in the repository outside the pinset itself
that pins the pinset's bytes. Everything else in that module builds its fixtures
dynamically; the test at `:1588` even calls `readiness._histsem_delta` to derive
its own expected delta rather than hard-coding one, so it tracks the code and
needs no update. No per-row expectations, receipt counts, or path lists are
hard-coded against the gamma `_v3` row.

## 8. Cross-check for the S14 lane

When `--refresh-row` runs against the `_v3` row, its output should match section 5
byte-for-byte and the refreshed file should hash to the section 6 digest. Two
independent derivations agreeing is the check; a mismatch means one of them is
wrong and neither should be applied until it is explained.
