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

The adjacent `.sha256` sidecar is **transport integrity only, never
authentication**. It is computed from the same bytes it accompanies, so a
producer who forges `C` can trivially produce a matching sidecar. The sidecar
detects truncation or corruption in transit and provides a cheap early
refusal; it does not establish that the bytes are the bytes Ed confirmed.

The authenticator of record is `hC = SHA256(C)`, supplied **out of band** by
the operator to every consumer through its explicit
`expected-confirmation-digest` input. “Out of band” means that the expected
digest comes from transaction custody independently of the repository path
being checked, rather than from `C` or its sidecar. A consumer that is not
given `hC` refuses: it performs no changed-set subtraction and authorizes no
publication. The standing source of `hC` is transaction custody, out of band, for
the life of the evidence; no repository path ever holds `hC`. The D-151
fixation commit pins `hS` — the successor pinset's own digest — which is
a durable archival byte pin, not a source of `hC` and not the
authenticator the C→S edge consults (amended per D-153 A5; the prior
sentence confused `hC` with `hS` and was enforced by no code).

`hC` must never be stored at a repository path that the changed-set allowlist
could name while the window is open. Under D-151's fixed-point rule, putting an
authenticator inside the set it authenticates is a tripwire event, not an
amendment lane: the repository bytes could then replace both the subject and
its alleged authenticator together.

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
2. the operator supplied `hC` separately through the consumer's explicit
   `expected-confirmation-digest` input;
3. that expected digest is exactly 64 lowercase hexadecimal characters;
4. that file and its `.sha256` sidecar are present, readable, canonical, and
   mutually consistent (the sidecar check is transport integrity only);
5. the SHA-256 of the exact table bytes equals the out-of-band `hC`;
6. only after that equality succeeds, the file validates against this contract
   in full;
7. its `successor_pinset.path` equals the path under test; and
8. the SHA-256 of the bytes **committed at the reviewed HEAD** for that path
   equals `successor_pinset.sha256`.

If any one of those fails, the path stays in the relevant set and the gate
refuses with the pre-existing `DEPENDENCY_CHANGED_SET` role — no new refusal
code is introduced (D-151 condition 1e). The same authenticated table input is
required at the marker/publication boundary; there absence maps to
`confirmation_missing`, while a malformed or unequal expected digest maps to
`confirmation_mismatch`. Worked consequence: once fixation commits the minted
pinset, an arm whose evidence predates that commit passes only while (a) the
table bytes hash to the operator-supplied `hC` and (b) the committed pinset
bytes still hash to the digest inside that authenticated table. Any later
rewrite of either file refuses until the operator supplies a newly confirmed
out-of-band digest.

### Where the `C → S` edge is *not* enforced: marker build

The four entry points named above are exhaustive. Marker **build** is not one
of them, and its absence is structural rather than an omission.

Freeze-receipt authentication shares the successor-relative/legacy-absolute location doctrine in [`receipt_histsem_verifier.md`](receipt_histsem_verifier.md) § “Archival location rule”.

The forcing problem is the acyclicity argument at the top of this document,
read forwards. The final table bytes `C` contain the marker digest `hM`, so `C`
cannot be rendered until the marker bytes `M` exist. A marker build therefore
runs at a moment when no table exists for any head. But the R1 changed-set gate
that the build replays for each family member reaches the digest-conditional
allowlist path as soon as the successor pinset has been minted into the changed
set, and that gate demands `C`. Requiring at build time an artifact whose only
lawful construction happens after build time is exactly the cycle this contract
says does not exist, and it made the build refuse at every post-mint head.

At the marker-build entry point the condition is therefore **suppressed, and
the suppression is disclosed**. Concretely:

- Both build phases (`candidate` and `publication`) pass the changed-set gate a
  deferral ledger (`R1ConditionalDeferral` in `joulewise/arm_readiness.py`)
  instead of a table. A digest-conditional path in the changed set is subtracted
  without evaluating the condition, and is recorded in that ledger.
- The built marker carries the ledger verbatim in a required, exact-key
  `conditional_paths_deferred` object: the fixed gate identifier
  `R1_DIGEST_CONDITIONAL`, the sorted `deferred_paths` list, and
  `enforced_at_entry_points` — the same four entry points enumerated above. An
  empty `deferred_paths` list is the positive statement that nothing was
  deferred, which is why the field is never absent.
- Only paths named by `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS` may appear in
  `deferred_paths`. The marker validator rejects anything else, so the field
  cannot be used to claim the changed-set gate was waived for an arbitrary path.
- The **candidate lane** of marker replay is the same evaluation re-run without
  a table — by the same construction, no table can exist for a candidate marker
  either — so it defers identically, rebuilds the ledger, and refuses the marker
  if what it rebuilds differs from what the marker published.
- Supplying a deferral together with a table or an expected digest is a caller
  contradiction and refuses `DEPENDENCY_CHANGED_SET`. The build lane and the
  enforcing lanes are mutually exclusive; no call site can be in both.

#### Recorded waiver: the required key was added under the `.v1` schema id

Adding a required key to an exact-key schema would ordinarily force the schema
id to `.v2`. It does not here, by ruling, and the reason is recorded rather than
left implicit (magistrate ruling on the S0-O2 refuter round, PR #184).

`conditional_paths_deferred` was added under
`joulewise.d117_family_publication_marker.v1`, whose key set is now exactly
fourteen. **No thirteen-key marker was ever successfully built** — the S0-O2
defect prevented the builder from instantiating one at any post-mint head — so
no persisted artifact changes meaning under the wider key set. A thirteen-key
document presented to the validator refuses at the exact-key check, which is the
intended fail-closed behaviour and not a compatibility break. The id advances to
`.v2` only on the next semantic change to an **instantiated** shape.

#### Accepted residual: the disclosure is verified, not self-proving

The disclosure is a statement the builder makes about its own evaluation, so it
cannot prove itself. Two mechanisms bound the residual, and it is recorded as
defence in depth rather than closed (refuter round, PR #184): a build that
truncated the disclosure to `[]` is caught at the mandatory candidate-replay
gate, which rebuilds the ledger from its own evaluation and refuses any marker
whose published disclosure it did not reproduce; and a post-build tamper of the
field refuses through the `C → M` byte binding, because the step-6 table names
`hM` over the exact marker bytes.

Nothing about arm, freeze, verification, or the publication/pre-arm/T-0 lanes of
marker replay changes. Those four still supply `C` and `hC` and still refuse
without them; a deferral is never passed on those paths. The C → S edge is
enforced later, not dropped, and the marker bytes say so on their face.

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
