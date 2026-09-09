# Cold-gate packet: paper S2 — the three statistical semantics of the reported-energy cells

Assembled mechanically by the interactive magistrate at 2026-09-08 ~13:00 PDT. Rule-11 trigger: design-bearing
statistical choices that determine the paper's headline reported-energy numbers (the four CP-X05 cells:
1.7B/8B × prefill/decode, each with mean, lower/upper endpoint, per-token value, count). Checkout = paper integration
head e241e0b7. The S2 seat (exhibit A) refused to choose these by convenience and returned them as rulings, correctly.

## The three questions (each with the seat's alternatives; the judge may add a better-evidenced third)
Q1 `mean_basis` / `ordered_members`: which exact ordered bundle universe, admission/exclusion rule, weighting and
independence unit defines the reported mean per cell? Evidence: docs/decision_log.md ~:7990 (the same 50 members
authorized); docs/paper/results-fill-registry.md ~:378 (admitted basis explicitly undefined), ~:381 (forbids
substituting the absolute floor mean); docs/contracts/paper_supply_custody.md ~:283/:290 (exact ordered members, all
strict-bundle inputs). Alternatives: (a) equal weighting of admitted individual bundles from the complete
preregistered universe; (b) an explicitly registered aggregation respecting component/block grouping.
Q2 `interval_composition`: what are the reported mean's endpoints? Evidence: docs/contracts/measurement_methodology.md
~:321 (Student-t 95% mean intervals settled); registry ~:379 (fully composed endpoints undefined);
joulewise/detection_floor.py ~:879 (a PREDICTION term with sqrt(1+1/n), NOT authority for a reported-mean interval);
the D-078 attribution limit (~1 J instrument attribution floor, published labelled) and any drift enclosure the
protocol registers (docs/paper/protocol/prospective-comparison-protocol.md). Alternatives: (a) Student-t mean
sampling interval widened by a governed aggregate attribution/drift enclosure; (b) extrema of the complete
mean-interval calculation over the governed admissible set.
Q3 `per_token_aggregation`: sum(E_i)/sum(T_i) or mean(E_i/T_i), with what missing/zero-count treatment, and bound
to which observed-token provenance? Evidence: registry ~:388 (observed prompt-token provenance for prefill), ~:393
(observed output-token provenance for decode); joulewise/reduce.py ~:3742 (configured output-token fallback excluded
as a denominator); the S6 rendering contract's per-token token families (docs/contracts/paper_comparison_rendering.md).

## Charge
For Q1–Q3 rule ONE alternative each (or a better one you can ground), stating: the estimand in one sentence a
metrology reviewer would accept; the file:line authority that already settles any part of it; the exact
registration text S2 must install (prospective, before any production number exists); the independence unit; the
mutation case that distinguishes your choice from the rejected alternative (a number that changes). State the
failure-mode test: can a plausible-looking mean/endpoint/per-token value pass validation while computed on the wrong
universe, the wrong composition, or a fabricated denominator? Also answer exhibit A's F5: is the frozen extraction
specification (the supply-map's pending extraction-spec path, absent on this head) a prerequisite for registering
the estimands, or only for producing numbers? Write NOT EXECUTED for anything you cannot verify. Write the ruling to
./coldgate-packet-s2/10-coldgate-fable-ruling.md (under 900 words, three numbered rulings + F5, one-line verdict last).
