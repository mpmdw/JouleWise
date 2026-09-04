```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The three seats converge on a positive exact-set guard and salvage; five magistrate choices remain, including the authority root, freeze-ID input, placeholder totality, mutation proof, and decision-log form.",
  "workspace": {
    "base_requested": "7a978f36",
    "base_mode": "exact",
    "head_start": "7a978f362cefc24296da261a1eeb6e1eabb87b8f",
    "head_end": "7a978f362cefc24296da261a1eeb6e1eabb87b8f",
    "upstream_end": "7a978f362cefc24296da261a1eeb6e1eabb87b8f",
    "branch": "feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/12-adjudication-packet-design.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "SALVAGE WITH A TOTAL CODE-OWNED DERIVATION",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "text": "The current equality check is conditional on both a Mapping successor roster and one registry id, so future ids and unresolved placeholders can carry unexplained paths."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "text": "A per-profile freeze-receipt input is needed to keep the derivation total across real and fixture lifecycle records without reintroducing an identity gate."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "text": "Promoting D-151 V-1(vii) from recorded dissent to operative cross-transaction mechanism needs a new open decision entry installed through the implementation task."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && git rev-parse @{upstream} && git branch --show-current",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "7a978f362cefc24296da261a1eeb6e1eabb87b8f",
          "7a978f362cefc24296da261a1eeb6e1eabb87b8f",
          "feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^7a978f362cefc24296da261a1eeb6e1eabb87b8f\\n7a978f362cefc24296da261a1eeb6e1eabb87b8f\\nfeat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'import json,pathlib; p=pathlib.Path(\"docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/12-adjudication-packet-design.md\"); s=p.read_text(encoding=\"utf-8\"); raw=s[8:s.index(chr(10)+chr(96)*3+chr(10),8)]; json.loads(raw); assert len(raw.encode(\"utf-8\")) <= 8192; assert len(s.encode(\"utf-8\")) < 25000; print(\"report contract: valid JSON, UTF-8, envelope <=8192 bytes, file <25 KB\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "report contract: valid JSON, UTF-8, envelope <=8192 bytes, file <25 KB"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^report contract: valid JSON, UTF-8, envelope <=8192 bytes, file <25 KB$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check -- docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/12-adjudication-packet-design.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "test \"$(git status --porcelain=v1)\" = \"?? docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/12-adjudication-packet-design.md\" && echo 'scope: only adjudication packet modified'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scope: only adjudication packet modified"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^scope: only adjudication packet modified$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Five design choices require magistrate adoption before implementation resumes.",
      "needs": "Answer Q1-Q5 and install the new decision entry as open (installs via AUTHENTICATOR-ALLOWLIST-GUARD-01)."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No tests were run by explicit preflight instruction; all evidence in this packet is direct source and contract inspection.",
      "needs": "The implementation seat must run the ruled focused modules and mutation probes."
    }
  ]
}
```

## Findings

### F1 — blocker — two independent applicability predicates still open the set

At `7a978f36`, exact equality is reached only when `successor_pack_ids` is a
`Mapping` **and** `registry_id == "d117-r1-lifecycle-v1"`
(`joulewise/arm_readiness.py:1935-1962`). Thus a fresh nonempty id bypasses the
guard, and Opus's fourth escape is also real: under `require_resolved=False`, an
`ED_RESERVED:*` roster skips the block and the final unresolved check
(`joulewise/arm_readiness.py:2051-2059`). Any adopted design must be total over
both dimensions; removing only the id conjunct is insufficient.

### F2 — should_fix — freeze identity must become a governed derivation input

The 112 paths include one PASS freeze receipt and sidecar per profile, but the
current derivation hard-codes `freeze-0004` (`joulewise/arm_readiness.py:1698-1704`).
The lifecycle fixtures validly rotate this to `freeze-0001`, `-0002`, or `-0004`
(`tests/test_arm_readiness_lifecycle.py:121-163`), which is why a single rendered
output digest could not apply across records. The lifecycle schema is exact-key
(`joulewise/arm_readiness.py:628-634,1914-1921`), so the clean input is a new
exact three-profile `successor_freeze_receipt_ids` map and a lifecycle schema
bump. A singular receipt id silently assumes the three chains can never diverge.

### F3 — should_fix — the mechanism is a new decision, not a historical edit

D-151 records V-1(vii) as dissent, not the adopted mechanism
(`docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md:112-115`).
Making it the total rule across future lifecycle records changes operative form,
versioning, inputs, and acceptance. D-170 requires such an implementation-bearing
decision to remain `open (installs via <TASK-ID>)` until producer regression
evidence lands (`docs/decision_log.md:10519-10527`).

## Side-by-side seat comparison

| Issue | Sol 09 | Opus 10 | Blind Fable 11 | Consensus |
|---|---|---|---|---|
| Closed-set location | Versioned canonical JSON contract; code maps lifecycle schema to `(path, sha256)`. | Frozen in-code `_R1_IRRELEVANT_PATH_SPEC` plus an in-code digest. | One in-code constant block; no manifest or digest. | **DIFFER** on location/authentication. All reject a runtime-extensible registry. |
| Closed-set contents | 3 profiles; 11 slugs; 8 explicit path families and closed proof handlers; 112 paths. | Same 3 profiles, 11 stems, 8 families, 112 paths. | Same bytes grouped as 5 families: 37/profile plus chain-tail pinset = 112. | **AGREE** on exact current contents and count; grouping differs only editorially. |
| Derivation signature / inputs | `derive_r1_irrelevant_path_manifest(repository, *, anchor_commit, expected_row_registry_sha256)`; Git-load registry and schema-selected spec; return paths plus provenance digests. | `_r1_derive_irrelevant_paths(*, successor_pack_ids, freeze_receipt_ordinals, spec=...) -> tuple`; registry id absent; `ED_RESERVED` returns `()`. | `r1_governed_artifact_manifest(successor_policy) -> tuple`; pack ids plus one `pass_freeze_receipt_id`; explicit resolved/reserved branches. | **DIFFER**. All exclude registry id and candidate allowlist as inputs. |
| Refusal codes | No new code; registry/spec/input/equality failures use `readiness_row_registry_mismatch`; changed-path/proof failures retain owners. | No new code; fixed stems `ALLOWLIST_NOT_DERIVED`, `ALLOWLIST_SPEC_DIGEST`, `ALLOWLIST_INPUTS_UNRESOLVED`. | No new code; registry mismatch with resolved and placeholder messages. | **AGREE** on no new code; **DIFFER** on message taxonomy and spec-digest refusal. |
| One acceptance test | Fresh lifecycle id + one extra path; equality mutation must make it red. | Fresh id test; M1 restore id gate, M2 disable equality; separate unresolved test kills M3. | One `subTest` method over four ids/rosters; M1 disable equality and M2 restore id gate. | **DIFFER**. Neither 09 nor 11 kills the fourth placeholder escape; 10 needs a second test. |
| Salvage vs rebuild | Salvage exact-set core; replace authority root and delete id gate/output pin. | Salvage; four deletions plus fixture derivation. | Salvage; delete output pin/id gate and repair fixtures. | **AGREE: SALVAGE**, not rebuild. |
| Decision-log need | New decision, initially open. | New decision; magistrate authority required. | Dated D-151 addendum, then done. | **DIFFER** on new entry vs addendum; all require a recorded ruling. |

## Verified contract collision map

Every row below was inspected at `7a978f36`; `VERIFIED` means the cited bytes
exist at those coordinates, not that a ruling has already selected an option.

| Contract / lifecycle fact | VERIFIED file:line | Consequence for adjudication |
|---|---|---|
| D-151 condition 7 forbids every authenticator path and routes failures to V-1(vii). | `docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md:92-96`; index anchor `docs/decision_log.md:10278-10292`. | All three positive-dual designs comply. Any registry-id, resolvedness, generation, or name-classification opt-in conflicts. |
| D-151 fixes the current value at 112, with the exact successor pinset as the conditional 112th entry; closed chain enumeration stays. | `docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md:41-50,88-102`; `docs/contracts/receipt_histsem_verifier.md:15-36,310-326`. | Preserve the allowlist entries byte-for-byte; use the code-enumerated chain tail, never a glob. |
| The conditional pinset remains proof-gated, not admitted by membership alone. | `docs/contracts/d117_step6_confirmation_table.md:177-205`; `joulewise/arm_readiness.py:2947-2962,4701-4756,4812-4852`. | The new equality guard must not weaken `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS` or C→S enforcement. |
| D-161 keeps fail-closed evidence, pre-registration, and plausible operator-mistake guards, while pruning deliberate-only/self-authentication cost. | `docs/process_traces/2026-08-27-t26/threat-model-prune/04-MAGISTRATE-RULING.md:8-16,39-52`; `docs/decision_log.md:10390-10401`. | Total exact equality stays. An external spec digest or same-module spec hash is not needed as authority: code and the spec change together, and both are outside subtraction. |
| D-157 makes post-mint semantic correction a new family generation. | `docs/process_traces/2026-08-27-t26/holm-m-consult/04-MAGISTRATE-RULING.md:32-38,70-78`; index `docs/decision_log.md:10358-10364`. | Add the lifecycle field/schema before the governed family mint. If a pack has already bound the old registry bytes, do not retrofit it. |
| The row-registry digest is embedded into the plan reference, and freeze consumption requires exact equality. | `joulewise/arm_readiness.py:4265-4283,4327-4336,7233-7236`. | A registry schema/key edit changes governed bytes; the implementation must first prove the target family is not already minted at its baseline or return `NEEDS_RULING` for a new generation. |
| The lifecycle schema and successor policy are exact-key and placeholders are registered states. | `joulewise/arm_readiness.py:68-70,609-675,1718-1746,1914-1954,2051-2059`; tracked values `configs/arm_readiness/d117_row_registry_v2.json:516-536`. | A new receipt-id key requires `.v2`; resolved/reserved mixed states must refuse, while the fully reserved state derives `()` and requires an empty candidate. |
| Lifecycle validation is presently a pure in-memory boundary used by policy, evidence, and synthetic consumers. | `joulewise/arm_readiness.py:2063-2090,2093-2116,4785-4796,4942-4948`; `joulewise/arm_readiness_evidence.py:2646-2654,2690-2697`. | Sol's repository/anchor API would force a broad caller rewrite and make synthetic validation depend on Git. Prefer the full `successor_policy` object as the pure input. |
| Family publication independently hard-codes `freeze-0004`. | `joulewise/arm_readiness.py:11300-11317,11344-11347`. | If receipt ids move into lifecycle policy, marker replay must read the same profile-specific value; leaving this literal creates two authorities. |
| Family-marker validation hard-codes the current lifecycle registry id fail-closed. | `joulewise/arm_readiness.py:10908-10931`. | Do not bump `registry_id` in this mission. The new exact-set guard must ignore it, while the independent marker contract may continue pinning the current production identity. |
| D-157 R-2 requires mint-path refusal with a registered reason. | `docs/process_traces/2026-08-27-t26/holm-m-consult/04-MAGISTRATE-RULING.md:56-68`; registry coverage `joulewise/arm_readiness.py:1982-2048`. | Reuse `readiness_row_registry_mismatch`; a new reason code would create avoidable vocabulary and pack-evidence work. |

## Decision questions

1. **Where is the authority root?**
   - 09: external versioned JSON, schema-selected and digest-pinned.
   - 10: in-code spec plus same-module digest.
   - 11: in-code constants, no digest.
   - **Recommendation:** adopt 11's code home, with 10's explicit eight-family
     structure. Code is outside the subtraction set and already visible to the
     changed-set gate. Reject both self-authenticating digest layers and reject a
     data-driven `proof_handler` dispatcher; existing proof paths remain owners.

2. **How does the derivation name the PASS freeze paths?**
   - 09: freeze identity lives in the lifecycle-schema-selected external spec.
   - 10: new per-profile ordinal map in `successor_policy`, schema `.v2`.
   - 11: one new PASS receipt id, or a temporary code constant.
   - **Recommendation:** add exact-key `successor_freeze_receipt_ids` as
     `{ALPHA,BETA,GAMMA} -> "freeze-<4+ digits>"`, bump only
     `R1_LIFECYCLE_REGISTRY_SCHEMA` to `.v2`, keep both registry ids and the outer
     row-registry schema unchanged, and make `_family_member` consume the same
     per-profile value. This avoids an unjustified synchronized-chain invariant.

3. **What is total behavior for unresolved records?**
   - 09: validates a resolved three-profile record; placeholder behavior is not
     pinned.
   - 10: any reserved derivation input returns `()`.
   - 11: exactly two branches, resolved map or reserved placeholder.
   - **Recommendation:** exactly two valid states: both derivation fields are
     exact three-profile maps and derive 112 paths, or both are `ED_RESERVED:*`
     and derive `()`. Any mixed state refuses. Candidate equality is unconditional,
     so the reserved state accepts only `[]`. This explicitly closes escape four.

4. **What single regression and mutations prove closure?**
   - 09: fresh-id extra-path test; equality mutation.
   - 10: fresh-id test with id/equality mutations plus a companion placeholder
     test for the fourth escape.
   - 11: one four-case `subTest` method with id/equality mutations, but no
     placeholder case.
   - **Recommendation:** replace the current acceptance method with one method,
     `test_allowlist_derivation_is_total_across_id_and_placeholder_state`, having
     two biting subtests: (A) fresh id + extra path refuses; (B) fully reserved
     record + nonempty candidate under `require_resolved=False` refuses. Require
     three recorded kills: restore the old two-conjunct gate; disable resolved
     equality; delete reserved-empty equality. The same one method must go red for
     each mutation.

5. **How is the policy change recorded?**
   - 09/10: new decision, initially open until installed.
   - 11: dated D-151 addendum marked done.
   - **Recommendation:** new D-number, status `open (installs via
     AUTHENTICATOR-ALLOWLIST-GUARD-01)`, pointing back to D-151 without rewriting
     its historical verdict. Adopt only after the production clause map and all
     three mutation kills land, per D-170.

## Ruling-ready agreed text

> **AUTHENTICATOR-ALLOWLIST-GUARD-01 — positive, total exact-set guard.**
> D-151 condition 7 remains controlling and is installed through its positive
> dual: `freeze_evidence_lifecycle.irrelevant_path_allowlist` is a serialized
> candidate and MUST equal the paths derived from the closed governed-artifact
> families for every lifecycle registry identity and every valid resolvedness
> state. Registry id is metadata and MUST NOT select, disable, or vary the
> derivation. The current result remains exactly 112 paths: for each of ALPHA,
> BETA, and GAMMA, the eleven governed source records, eleven evidence receipts,
> eleven receipt sidecars, one profile-selected PASS freeze receipt and sidecar,
> and plan tree and sidecar, plus the code-enumerated successor histsem pinset
> chain tail. No allowlist entry is added or removed. The conditional pinset
> remains subject to the existing C→S proof; membership never forgives failed
> authentication or replay.
>
> The closed family templates and eleven stems live once in
> `joulewise/arm_readiness.py`, outside the subtraction set, without a separate
> manifest digest or proof-handler dispatcher. The pure derivation consumes the
> lifecycle `successor_policy`: exact per-profile `successor_pack_ids` and exact
> per-profile `successor_freeze_receipt_ids`. Both mapped fields derive the 112
> paths; both `ED_RESERVED:*` fields derive the empty tuple and require an empty
> candidate; mixed states refuse. The lifecycle schema advances to `.v2`; the
> lifecycle registry id, outer row-registry schema/id, and family-marker schema
> do not change. Family-marker replay reads the same profile-selected freeze id.
>
> All derivation, input-state, and candidate-equality failures reuse
> `readiness_row_registry_mismatch`, with stable tokens
> `ALLOWLIST_NOT_DERIVED` or `ALLOWLIST_INPUTS_UNRESOLVED`; changed-set and
> artifact-proof failures retain their existing owning refusals. Salvage the
> present template expansion, exact comparison, 112 candidate entries,
> conditional pinset gate, and removal of the authenticator decorator/registry.
> Delete the registry-id and `Mapping` applicability gate, the rendered-output
> provenance schema/digest, and fixture-side string substitution. Fixture
> registries call the production derivation.

### Implementation-seat WRITE_SCOPE (exhaustive)

```json
[
  "joulewise/arm_readiness.py",
  "configs/arm_readiness/d117_row_registry_v2.json",
  "tests/test_arm_readiness_schemas.py",
  "tests/test_arm_readiness_lifecycle.py",
  "tests/test_arm_readiness_evidence.py",
  "tests/test_family_marker.py",
  "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/13-implementation-report.md"
]
```

Lead-owned prerequisite outside that seat: create the new decision-log entry in
`docs/decision_log.md` with status `open (installs via
AUTHENTICATOR-ALLOWLIST-GUARD-01)` and put its exact `file:line` clauses in the
implementation brief's D-170 clause map. The implementation seat must return
`NEEDS_RULING` before editing if its baseline contains a governed pack or marker
already bound to the old registry digest.

## Residual risk

No tests were run by instruction. This head contains no committed `_v5` pack
trees, so the registry-field recommendation is compatible with the inspected
repository state; transaction-external marker custody was not inspected. The
lead must re-check that no governed family has been minted against the old
registry digest at the implementation baseline. The magistrate may also choose
to keep `freeze-0004` code-constant for the current family, but that would defer,
not solve, the lifecycle-input problem that caused the identity gate.
