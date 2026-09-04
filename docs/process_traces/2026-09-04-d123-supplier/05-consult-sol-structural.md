```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The repeat is caused by a self-sealed caller projection with no authenticated value-origin relation, compounded by a mutation oracle that stops at the outer issuance mismatch; R1-5 must be made producer-explicit.",
  "workspace": {
    "base_requested": "b413873d4b313644264cb2e8ab98c390837632a5",
    "base_mode": "exact",
    "head_start": "b413873d4b313644264cb2e8ab98c390837632a5",
    "head_end": "b413873d4b313644264cb2e8ab98c390837632a5",
    "upstream_end": "b413873d4b313644264cb2e8ab98c390837632a5",
    "branch": "feat/2026-09-04-d123-reported-mean"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-d123-supplier/05-consult-sol-structural.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "r1_is_source": "YES: R1-5 is abstract about value-origin authentication, not facially self-contradictory; the detailed adopted design is unrealizable as written because it calls point values authenticated without naming any parent that emits them.",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "file": "joulewise/reported_phase_energy.py:332-416",
        "text": "The source producer authenticates an unrelated extraction report but accepts, self-hashes, and copies the caller's numeric reported-energy projection; issuance therefore certifies the same untrusted child it rebuilds from.",
        "cure": "Make the projection producer-only and deterministically derive it from authenticated member bytes under an amended R1-5 value-origin clause."
      },
      {
        "id": "S2",
        "severity": "should_fix",
        "file": "tests/test_reported_phase_energy.py:729-795",
        "text": "The mutation census calls the composite issuer and asserts generic StopFill, so artifact/source inequality at reported_phase_energy.py:1292-1295 masks every inner relation.",
        "cure": "Test the owning derivation validator directly and assert its exact named mismatch after all child and envelope hashes are resealed."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "nl -ba joulewise/reported_phase_energy.py | sed -n '332,416p;1267,1295p'; nl -ba tests/test_reported_phase_energy.py | sed -n '212,246p;729,795p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "   793\t                            \"beta\": _source_bytes(sources[1]),",
          "   794\t                        },",
          "   795\t                    )"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "795.*\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --no-index --check /dev/null docs/process_traces/2026-09-04-d123-supplier/05-consult-sol-structural.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": []
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "R1-5 does not define which authenticated producer creates the member numeric projection or the equality that makes its values issued.",
      "needs": "Replace R1-5 with the producer-explicit clause below before fix round 2."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No tests were run: the executed delta re-audit already demonstrates both signatures, and this structural consult required source inspection only.",
      "needs": "Run the one proposed regression with the implementation cure."
    }
  ]
}
```

## Findings

### B1 — blocker — Q1/Q2: the trust chain has no value-producing root

The repeated signature is not “one missing check”; it is a self-sealed shadow wire. `_SOURCE_MATERIAL_KEYS` admits `reported_energy_projection` (`joulewise/reported_phase_energy.py:148-175`), `_validated_source_wrappers` authenticates the real extraction report but checks the projection only for its own hash, role/report digest, and three-cell census (`:332-379`), and `build_reported_phase_energy_source` then copies that caller document unchanged (`:382-416`). `build_reported_phase_energy` consumes the copied cells as its numeric truth (`:808-869`), and issuance merely rebuilds from that same source and compares the result (`:1285-1298`); content addressing proves internal consistency, not that the values came from governed evidence.

The fixture mirrors the defect: `_source_material_from_blueprint` loads one production-shaped extraction report but independently invents each role's member points, envelopes, denominators, and projection (`tests/test_reported_phase_energy.py:152-246`). Thus the delta re-audit's two different numeric projections over identical report bytes are structurally allowed, regardless of how many downstream IDs are resealed.

R1 itself is the source at the contract altitude. Its binding Q-R1-5 says, “Sol's custody-rich wire with explicit `campaign_role`; no `rendered` object; the paper renderer owns formatting” (`docs/process_traces/2026-09-04-paper-i/06-magistrate-contract-rulings.md:10`), while the preamble merely requires “authenticated, issued fields” (`:3`); neither names the producer that authenticates numeric member values or a relation to its evidence. This is abstract/underspecified rather than facially self-contradictory, but the detailed adopted design exposes the contradiction in realization: it lists only spec/report/G2-a/prompt-pin input references (`02-consult-sol-contracts.md:141-164`) and later calls the otherwise parentless `point_j` values “authenticated” (`:211`). D-123 does not cure that gap: it freezes the procedure and same 50-member universe, not an issuance path (`docs/decision_log.md:7987-7993`).

Replace R1-5 verbatim with:

> **Q-R1-5 REPLACEMENT:** `joulewise.reported_phase_energy_projection.v1` is the output of one deterministic production producer and is never caller-supplied source material. The producer MUST validate the frozen extraction spec and the authenticated bundle, summary, metadata, whole-window-evaluation-basis, G2-a, and prompt-pin bytes for the exact ordered `reported_energy_cells[].members` universe, and MUST derive every member identity, custody digest, phase-energy point, envelope endpoint, and runtime denominator from those bytes; a content address, a copied digest, or an issuance rebuilt from the same caller document is not authentication. The existing `joulewise.detection_floor_extraction.v1` report MAY gate shared-corpus admission and floor noninterference but MUST NOT authenticate any reported-energy field it does not emit. `joulewise.reported_phase_energy.v1` and its issuance MUST be rebuilt from that producer output and compared at the owning parent/value derivation relation before any outer artifact or issuance equality check; any mismatch returns `STOP_FILL` at the refusal scope set by Q-R1-3. The artifact remains one custody-rich content-addressed artifact per `campaign_role`, carries no `rendered` object, and the paper renderer alone formats issued numbers.

### S2 — should_fix — Q1: the test asks the wrong layer

The expanded loop reseals each artifact, then calls `build_reported_phase_energy_issuance` and accepts any `StopFill` (`tests/test_reported_phase_energy.py:729-795`). The issuer first rebuilds the expected artifact from the unchanged source and rejects whole-object inequality at `joulewise/reported_phase_energy.py:1292-1295`; therefore no mutation proves its named digest, arithmetic, or custody relation. This is the same outer-gate masking signature as round 0, with a larger mutation inventory.

### Q3 — class-ending cure and its one test

Remove `reported_energy_projection` from source-material input. A production projector must use the same authenticated member-byte loaders/consumption session as extraction, emit the projection deterministically, and expose a validator that recomputes the complete projection from those parent bytes before comparing it; source/artifact/issuance construction may consume only that generated output. This converts every numeric field from “caller claim plus self-hash” to a function of a trusted parent vector and gives mutations an owning relation below the envelope gate.

Add exactly one regression: `test_fixed_authenticated_parents_determine_one_reported_energy_projection`. It must run the production projector on a fixed authenticated parent set, then alter one member point and its dependent envelope/means/per-token values in the child and recompute every child, source, artifact, and issuance hash; calling the projection/parent relation validator directly must return exactly `reported_energy_projection_derivation_mismatch`, not generic `StopFill` or `issuance_artifact_source_mismatch`, and rerunning the producer on the unchanged parents must reproduce the original projection bytes. A whole-projection recomputation makes that one counterfactual bite every child field and simultaneously ends B1/F1 and the S2 masking class.

### Q4 — ruling row (4 sentences)

R1 supplier remains **NOT LANDABLE**: execution B1/contract F1 and execution S2 repeat unchanged. The structural defect is a self-sealed caller projection that the source producer copies, while the test observes only the earlier issuance-envelope mismatch. Amend R1-5 with the replacement clause above, then make the projection producer-only and derived from authenticated member bytes. Land only when `test_fixed_authenticated_parents_determine_one_reported_energy_projection` kills a fully resealed contradictory child at the named derivation relation.

## Residual risk

The exact existing authenticated loader to reuse is an implementation choice for fix round 2; this consult does not authorize or validate that code. No live or quiet-machine evidence was used, and no claim value is issued.
