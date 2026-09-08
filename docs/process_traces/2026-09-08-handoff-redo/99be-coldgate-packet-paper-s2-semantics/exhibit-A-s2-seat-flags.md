# Exhibit A — S2 seat NEEDS_RULING flags (gpt-6-astra high, 2026-09-08), verbatim

## F2 (blocking)
mean_basis and ordered_members remain unresolved. docs/decision_log.md:7990 authorizes the same 50 members; docs/paper/results-fill-registry.md:378 explicitly leaves the admitted basis undefined and :381 forbids substituting the absolute floor mean. Alternatives for adjudication: equal weighting of admitted individual bundles from the complete preregistered universe, or an explicitly registered aggregation respecting component/block grouping. Neither exact weighting nor exclusion behavior is established by these sources.

NEEDS: Specify the exact ordered bundle universe, admission/exclusion rule, weighting and independence unit. Recommendation: issue an explicit prospective registration; do not substitute a floor component. Blocks numerical means and bundle counts.

## F3 (blocking)
interval_composition remains unresolved. docs/contracts/measurement_methodology.md:321 specifies Student-t 95% mean intervals, but docs/paper/results-fill-registry.md:379 leaves fully composed mean endpoints undefined. Alternatives for adjudication: a mean sampling interval widened by a governed aggregate attribution/drift enclosure, or extrema of the complete mean-interval calculation over the governed admissible set. joulewise/detection_floor.py:879 instead computes a prediction term using sqrt(1+1/n), which is not authority for a reported-mean interval.

NEEDS: Specify the sampling unit, attribution/drift composition, dependence treatment and endpoint algorithm. Recommendation: retain the settled Student-t requirement and explicitly rule the enclosure composition. Blocks endpoint calculation and plausible-but-incorrect endpoint regressions.

## F4 (blocking)
per_token_aggregation remains unresolved. docs/paper/results-fill-registry.md:388 requires observed prompt-token provenance for prefill and :393 observed output-token provenance for decode. joulewise/reduce.py:3742 excludes configured output-token fallback as a denominator. Alternatives for adjudication: sum(E_i)/sum(T_i), or mean(E_i/T_i); these differ for unequal observed counts.

NEEDS: Choose aggregation and missing/zero-count treatment, and bind observed counts to the same admitted members and request boundary. Recommendation: preserve observed-token provenance and explicitly register the estimand. Blocks per-token outputs and fabricated-denominator replay.

## F5 (blocking)
The pending production extraction-spec path named by configs/paper_supply/supply_map.json does not exist on this head. The four CP-X05 bindings identify output targets but do not establish the frozen extraction specification or production members.

NEEDS: Identify the adopted frozen specification and its exact member joins through D-173 map roles; do not create measurement inputs or production digests in this lane.
