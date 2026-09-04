```json
{
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "file": "joulewise/reported_phase_energy.py:24",
        "text": "The builder labels an invented fixture-only document as joulewise.detection_floor_extraction.v1, but the real floor_extraction.extract_cells producer emits a different shape and no producer emits reported_phase_energy_source.v1. The supplier therefore has no authenticated production input path.",
        "counterfactual": "The real extraction shape at joulewise/floor_extraction.py:3070-3117 has no artifact_id, campaign_role, outcome, or reported_energy_cells and fails here, while the self-hashed synthetic shape at tests/test_reported_phase_energy.py:210-217 is accepted.",
        "cure_shape": "Either version and land a governed upstream producer/validator for the new member projection, or consume the actual authenticated extraction/bundle surfaces; add an integration test using bytes emitted by the ruling-named producer. Do not reuse the existing extraction schema tag for a different wire."
      },
      {
        "id": "B2",
        "severity": "blocker",
        "file": "joulewise/reported_phase_energy.py:597",
        "text": "The per-token result requires one uniform token_count_source, directly contradicting R1 Q-R1-4's instruction not to require denominator uniformity beyond per-member authentication and count checks.",
        "counterfactual": "An otherwise valid 50-member decode fixture with member 1 sourced from server_usage and members 2-50 from runtime_observed builds an issued gross cell but sets per_token=null and projects STOP_FILL. The landing test codifies that wrong refusal at tests/test_reported_phase_energy.py:445-447.",
        "cure_shape": "Accept any per-member mix of the two allowed authenticated sources. Remove the single-source gate and represent aggregate provenance without pretending a uniform source (for example, omit the aggregate source or use a closed set/list)."
      },
      {
        "id": "B3",
        "severity": "blocker",
        "file": "joulewise/reported_phase_energy.py:1071",
        "text": "The renderer silently collapses multiple artifacts for one campaign_role with last-write-wins dictionary construction, violating the one-artifact-per-role contract and making a paper value depend on caller order.",
        "counterfactual": "Two independently valid alpha artifacts with distinct IDs and decode means 102.55 and 112.55 project 112.55 in order [a1,a2,beta] and 102.55 in order [a2,a1,beta], instead of refusing alpha.",
        "cure_shape": "Census artifacts by role before selection; require exactly one valid artifact per role and STOP_FILL that role on duplicate/conflicting candidates. Add both orderings to the acceptance table."
      },
      {
        "id": "S1",
        "severity": "should_fix",
        "file": "joulewise/reported_phase_energy.py:305",
        "text": "Cell refusal fabricates four all-zero SHA-256 custody values when authenticated member digests are absent. Those placeholders pass artifact validation as if they were authenticated digests.",
        "counterfactual": "Removing bundle_sha256, summary_sha256, metadata_sha256, and whole_window_evaluation_basis_sha256 from one report member yields a validator-clean refused artifact containing four zero digests.",
        "cure_shape": "Never default authenticated custody fields. Make unavailable refusal custody explicitly nullable with a governed reason, or escalate to artifact refusal if the custody-rich wire requires those digests."
      },
      {
        "id": "S2",
        "severity": "should_fix",
        "file": "tests/test_reported_phase_energy.py:483",
        "text": "The bulk mutation loop does not establish field-specific acceptance behavior: every mutation leaves artifact_id stale, so the outer content-address check masks inner validation, and the selected keys omit emitted mean/interval/per-token/member-energy boundary fields.",
        "counterfactual": "After re-addressing each mutated artifact, 754 of 757 digest occurrences remain validator-clean because they are only syntax-checked references. Independent resealed boundary mutations do exercise arithmetic relations, but the committed acceptance test does not perform that proof.",
        "cure_shape": "Mutate and reseal one occurrence of every digest, census, outcome/status, and boundary field; where a parent digest needs source bytes, validate against those bytes rather than relying on the artifact's self-hash. Assert the expected named relation/refusal for each case."
      }
    ]
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The D-123 supplier is not landable: its production source wire is unproduced, mixed authenticated denominator sources are wrongly refused, duplicate roles select by order, and refusal custody defaults digests.",
  "workspace": {
    "base_requested": "6b6c1a9f",
    "base_mode": "exact",
    "head_start": "6b6c1a9f0f0a6da03c60b7ca732feb1cf3d4a016",
    "head_end": "6b6c1a9f0f0a6da03c60b7ca732feb1cf3d4a016",
    "upstream_end": "6b6c1a9f0f0a6da03c60b7ca732feb1cf3d4a016",
    "branch": "feat/2026-09-04-d123-reported-mean"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-d123-supplier/02-refuter-execution.md"
  ],
  "unowned_dirty": [],
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_reported_phase_energy",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 8.625s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test.*OK"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 13 tests in 2.722s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 13 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_floor_qwen3_v5_generate tests.test_floor_extraction",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 181 tests in 12.075s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 181 tests.*OK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check origin/main..HEAD -- docs/paper/results-fill-registry.md docs/process_traces/2026-09-04-d123-supplier/01-seat-landing-report.md joulewise/reported_phase_energy.py scripts/build_reported_phase_energy.py tests/fixtures/reported_phase_energy/preexisting_floor_output.json tests/fixtures/reported_phase_energy/two_pack_source.json tests/test_reported_phase_energy.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical whole suite was not run because the prompt's preflight rule restricts execution to the named modules.",
      "needs": "Run the canonical suite only after the lead opens that gate."
    }
  ]
}
```

## Findings

### B1 — No authenticated producer emits the accepted source wire

The source schema occurs only in the new builder and CLI. The established extraction producer returns the object at `joulewise/floor_extraction.py:3070-3117`; it cannot satisfy the checks at `joulewise/reported_phase_energy.py:663-718`. Green producer/extraction tests therefore do not establish an end-to-end supplier path.

### B2 — Mixed authenticated denominator sources are refused

R1 accepts `runtime_observed` and `server_usage` per member and expressly rejects an extra uniformity requirement. The `len(denominator_sources) == 1` gate and its `runtime_token_denominator_ambiguous` branch add exactly that forbidden requirement.

### B3 — Duplicate roles select different paper values by order

The role dictionary overwrites earlier entries without a cardinality check. Both counterfactual alpha artifacts validate and have distinct content addresses, yet reversing them reverses the projected value.

### S1 — Refusal custody invents digest values

All-zero strings are syntactically valid SHA-256 values, so the validator cannot distinguish the defaults from authenticated custody. STOP_FILL protects the numeric cell but does not make fabricated provenance acceptable.

### S2 — The committed mutation gauntlet is content-hash-masked and incomplete

The test proves that changing addressed content without changing its address is rejected. It does not prove that each inner authenticated relation refuses after a legitimate re-address, and it omits multiple emitted boundary fields from its mutation inventory.

The registry comparison against `origin/main` was clean: only DS-09, DS-10, DS-12, DS-13, DS-14, DS-16, DS-17, DS-18, DS-20, DS-21, DS-22, and DS-24 changed; DS-11, DS-15, DS-19, and DS-23 were byte-identical. The amended rows changed bindings/fill-state/provenance exactly in the R1 domain; no numeric value or digest was introduced or altered outside the ruling.

## Residual risk

Fixtures only; no live or quiet-machine measurement was attempted. Floor noninterference is demonstrated against the retained preexisting fixture bytes, not a production campaign run.
