# D-117 Step-6 Confirmation Table Contract

This document is the ONE normative home for
`joulewise.d117_step6_confirmation_table.v1`. The marker and receipt
historical-semantics contracts reference this contract; neither defines a
second confirmation artifact or schema.

Authority is the 2026-08-22 family-marker magistrate ruling and D-151
conditions 2 and 7. The table is a custody-external authenticator. Its path
must never enter an irrelevant-path, changed-set, transaction-output, or any
other allowlist. Adding an authenticator path to an allowlist is a D-151
fixed-point tripwire, not an amendment lane.

## Acyclic digest graph

There are exactly two immutable consumers:

- marker bytes `M`, with digest `hM`;
- the successor histsem pinset bytes `S`, with digest `hS`.

The final table bytes `C` contain `hM` in `family_publication` and `hS` in
`successor_pinset`. Ed confirms the digest `hC` over those exact final bytes.
The only edges are `C → M` and `C → S`; neither `M` nor `S` names `C`, so the
graph is acyclic. The marker binds this table's contract identifier and the
required decision `YES`, never the table path, digest, or event time.

## Encoding and sidecar

The artifact uses strict D-134 canonical JSON: UTF-8, duplicate-key refusal,
finite JSON values, lexicographically sorted object keys, two-space indent,
and one trailing newline. Its adjacent sidecar is exact GNU SHA-256 form:

```text
<64 lowercase hex><two spaces>d117_step6_confirmation_table_v4.json\n
```

The table contains no self-digest and no timestamp. Event time belongs in the
immutable transaction transcript. Before Ed is asked, the producer renders
the final bytes including the literal proposed `YES`, computes `hC`, and
presents both. Ed's yes names `hC`; publication promotes the same bytes
without mutation.

## Exact schema

Every object below is exact-key. Integers reject booleans. Digests are 64
lowercase hexadecimal characters and Git object IDs are 40 lowercase
hexadecimal characters.

```json
{
  "confirmation": {
    "authority": "ED",
    "decision": "YES",
    "statement": "I confirm these exact D-117 v4 step-6 bytes."
  },
  "family_id": "d117-v4",
  "family_publication": {
    "marker": {
      "path": "d117_family_publication_v4.json",
      "schema_version": "joulewise.d117_family_publication_marker.v1",
      "sha256": "<hM>"
    },
    "members": [
      {
        "freeze_receipt_sha256": "<sha256>",
        "pack_id": "d117_floor_qwen25_1p5b_v4",
        "pack_sha256": "<sha256>",
        "profile": "ALPHA"
      },
      {
        "freeze_receipt_sha256": "<sha256>",
        "pack_id": "d117_floor_qwen25_7b_v4",
        "pack_sha256": "<sha256>",
        "profile": "BETA"
      },
      {
        "freeze_receipt_sha256": "<sha256>",
        "pack_id": "d117_contrast_qwen25_1p5b_vs_7b_v4",
        "pack_sha256": "<sha256>",
        "profile": "GAMMA"
      }
    ]
  },
  "git": {
    "head_commit": "<publication HEAD>",
    "head_tree_oid": "<tree of publication HEAD>"
  },
  "registry": {
    "path": "configs/arm_readiness/d117_row_registry_v2.json",
    "registry_id": "d117-row-registry-v2",
    "schema_version": "joulewise.arm_readiness_row_registry.v2",
    "sha256": "<registry sha256>"
  },
  "schema_version": "joulewise.d117_step6_confirmation_table.v1",
  "successor_pinset": {
    "fact_count": "<nonnegative integer>",
    "pack_count": 3,
    "path": "configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json",
    "receipt_count": 33,
    "schema_version": "joulewise.receipt_histsem_pinset.v1",
    "sha256": "<hS>"
  },
  "table_kind": "D117_STEP6_CONFIRMATION",
  "transaction_id": "<nonempty transaction identifier>"
}
```

The `family_publication.members` array order is exactly ALPHA, BETA, GAMMA.
Its four visible fields per row must equal the immutable marker. The marker
consumer validates the entire table and the `C → M` edge.

The `successor_pinset` section names the code-enumerated successor path,
schema, whole-file digest, and recomputed counts. The changed-set/histsem
consumer validates the entire table and the `C → S` edge. `pack_count` is
exactly three and `receipt_count` is exactly 33 for the `_v4` family; the
fact count is recomputed from the 33 receipts.

### Where the `C → S` edge is enforced

The R1 changed-set gate (`validate_r1_evidence_lifecycle` in
`joulewise/arm_readiness.py`) computes the set of repository paths that changed
between an evidence receipt's derivation commit and the reviewed HEAD, then
subtracts the registry's `irrelevant_path_allowlist`. The successor pinset path
is one of the 112 allowlist entries, but it is subtracted on a *condition*
rather than on membership alone. The allowlist entries carrying that condition
are named by the code constant `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS`, which
currently holds exactly the successor pinset path.

For such a path the gate subtracts it only when all of the following hold:

1. a step-6 confirmation table path was supplied to the gate (the arm, freeze,
   verification, and marker-replay entry points pass the same custody path they
   already pass to the family-publication gate);
2. that file and its `.sha256` sidecar are present, readable, canonical, and
   mutually consistent;
3. the file validates against this contract in full;
4. its `successor_pinset.path` equals the path under test; and
5. the SHA-256 of the bytes **committed at the reviewed HEAD** for that path
   equals `successor_pinset.sha256`.

If any one of those fails, the path stays in the relevant set and the gate
refuses with the pre-existing `DEPENDENCY_CHANGED_SET` role — no new refusal
code is introduced (D-151 condition 1e). Worked consequence: once fixation
commits the minted pinset, an arm whose evidence predates that commit passes
only while the committed bytes still hash to the digest Ed signed; any later
rewrite of that file — benign or hostile — turns every such arm into a
`DEPENDENCY_CHANGED_SET` refusal until Ed signs a new table.

## Candidate and publication lanes

Candidate verification may prove marker-intrinsic and pinset-intrinsic
bindings without `C`. It must report `gate_admissible: false`,
`publication_authorized: false`, and the consulted `origin/main` OID. The S-0
clone deliberately forges that ref, so a candidate PASS is
forged-`origin/main`-conditional and must never be reported as published
green.

Publication, scheduler pre-arm, and T-0 require `C`, its sidecar, the literal
Ed `YES`, strict four-way equality of publication head, HEAD, local main and
origin/main, a clean tree, and semantic replay. Absence, mutation, unknown
keys, wrong section bindings, or any attempt to substitute separately
confirmed family/pinset records refuses publication.
