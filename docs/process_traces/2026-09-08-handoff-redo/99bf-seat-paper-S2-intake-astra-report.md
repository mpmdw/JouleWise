```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "none",
  "summary": "NEEDS_RULING: completed read-only intake; missing launch baseline anchors block writes, and reported-energy statistical semantics remain unresolved.",
  "workspace": {
    "base_requested": "e241e0b7",
    "base_mode": "exact",
    "head_start": "e241e0b79c353302401fc160884ab1d9ef4c6265",
    "head_end": "e241e0b79c353302401fc160884ab1d9ef4c6265",
    "upstream_end": null,
    "branch": "feat/2026-09-08-paper-S2"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "no_change",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --exit-code; git ls-files --others --exclude-standard",
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
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_reported_energy > /private/tmp/paper-S2-reported-energy.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": null,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The prompt supplies no BASELINE_MANIFEST or BASELINE_DIGEST. docs/contracts/bridge_protocol.md:45, :47, :574 and :601 require an immutable launch baseline and prompt-supplied anchors before workspace writes. No baseline or lease authority was inferred.",
      "needs": "Resume with the governing launch baseline manifest and digest, or an explicit ruling superseding this requirement for the runner-owned lane."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "mean_basis and ordered_members remain unresolved. docs/decision_log.md:7990 authorizes the same 50 members; docs/paper/results-fill-registry.md:378 explicitly leaves the admitted basis undefined and :381 forbids substituting the absolute floor mean. Alternatives for adjudication: equal weighting of admitted individual bundles from the complete preregistered universe, or an explicitly registered aggregation respecting component/block grouping. Neither exact weighting nor exclusion behavior is established by these sources.",
      "needs": "Specify the exact ordered bundle universe, admission/exclusion rule, weighting and independence unit. Recommendation: issue an explicit prospective registration; do not substitute a floor component. Blocks numerical means and bundle counts."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "interval_composition remains unresolved. docs/contracts/measurement_methodology.md:321 specifies Student-t 95% mean intervals, but docs/paper/results-fill-registry.md:379 leaves fully composed mean endpoints undefined. Alternatives for adjudication: a mean sampling interval widened by a governed aggregate attribution/drift enclosure, or extrema of the complete mean-interval calculation over the governed admissible set. joulewise/detection_floor.py:879 instead computes a prediction term using sqrt(1+1/n), which is not authority for a reported-mean interval.",
      "needs": "Specify the sampling unit, attribution/drift composition, dependence treatment and endpoint algorithm. Recommendation: retain the settled Student-t requirement and explicitly rule the enclosure composition. Blocks endpoint calculation and plausible-but-incorrect endpoint regressions."
    },
    {
      "id": "F4",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "per_token_aggregation remains unresolved. docs/paper/results-fill-registry.md:388 requires observed prompt-token provenance for prefill and :393 observed output-token provenance for decode. joulewise/reduce.py:3742 excludes configured output-token fallback as a denominator. Alternatives for adjudication: sum(E_i)/sum(T_i), or mean(E_i/T_i); these differ for unequal observed counts.",
      "needs": "Choose aggregation and missing/zero-count treatment, and bind observed counts to the same admitted members and request boundary. Recommendation: preserve observed-token provenance and explicitly register the estimand. Blocks per-token outputs and fabricated-denominator replay."
    },
    {
      "id": "F5",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The pending production extraction-spec path named by configs/paper_supply/supply_map.json does not exist on this head. The four CP-X05 bindings identify output targets but do not establish the frozen extraction specification or production members.",
      "needs": "Identify the adopted frozen specification and its exact member joins through D-173 map roles; do not create measurement inputs or production digests in this lane."
    },
    {
      "id": "F6",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "No implementation or synthetic regression module was created. Acceptance was not run; no acceptance log or numeric synthetic control exists.",
      "needs": "After resolving F1, implement independent authorized checks. Resolve F2-F5 before numerical replay and production-gate registration."
    }
  ]
}
```

## Change

No files changed and no commit was made. Deliverable findings:

| Deliverable | Inspection result |
|---|---|
| Four cells / twenty outputs | Targets are `CP-X05-1p7b-prefill`, `CP-X05-8b-prefill`, `CP-X05-1p7b-decode`, and `CP-X05-8b-decode` at `docs/contracts/paper_comparison_placements.md:71`. Each requires mean, lower endpoint, upper endpoint, per-token value and count. |
| Distinct projection | `joulewise/paper_rendering.py:41` reads an invented report field. The closed report key set at `joulewise/floor_extraction.py:1454` excludes it. A separate projection is required. |
| Custody and provenance | `docs/contracts/paper_supply_custody.md:290` requires owner-validator replay, exact ordered membership and every consumed strict-bundle input. Implementation remains blocked. |
| Source census | The extension point is `joulewise/paper_custody.py:729`; new projection validators must enter this census. |
| Non-issuing fixtures | Production energy remains absent from `_ISSUANCE_GATES` at `joulewise/paper_custody.py:655`. No registration or digest changes were made. |

## Verification notes

All requested mutation regressions remain **unexecuted**, with these required counterfactuals:

| Mutation | Required biting check |
|---|---|
| Omitted, duplicated or reordered member | Compare against the complete authenticated ordered universe; plausible mean must not rescue it. |
| Swapped model or phase | Reject disagreement with registered cell identity and member provenance. |
| Stale prompt pin | Reject disagreement with authenticated selection and frozen prompt bindings. |
| Incorrect interval endpoint | Recompute the ruled composition; checking endpoint ordering alone is insufficient. |
| Fabricated token denominator | Reconstruct observed counts from authenticated members under the ruled aggregation. |
| Count copied from a floor component | Derive count from the ruled admitted universe rather than trusting the reported count. |

The complete independently calculated numeric control is blocked by the unresolved statistical choices.

The write stop comes specifically from `docs/contracts/bridge_protocol.md:601`: “The prompt MUST provide `BASE_HEAD`, `BASELINE_MANIFEST`, and `BASELINE_DIGEST`.” The next step is a resumed lead prompt supplying those anchors and the bounded statistical rulings above.