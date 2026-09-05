# Magistrate contract rulings — paper suppliers R1–R4 (2026-09-04)

Inputs: scout 01; three-seat consult (Sol 02, Opus 03, blind Fable 02-blind); adjudication packet 05; the D-165 renderer refuters (docs/process_traces/2026-09-04-d165-renderer/02-refuter-*.md). Packet recommendations are ADOPTED except where amended below. Nothing here issues a value; every supplier renders only authenticated, issued fields and returns STOP_FILL otherwise.

## R1 — `joulewise.reported_phase_energy.v1` (DS-09..DS-24)
- Q-R1-1 ADOPTED (Sol, amended): one content-addressed artifact per `campaign_role` (alpha, beta); the member universe is the generator-frozen ordered 50-member set per cell (`reducer="arithmetic_mean_over_fixed_member_universe.v1"`, `expected_n=50`); no post-data shrinkage.
- Q-R1-2 AMENDED: the supplier's `interval.composition_rule` is a registered rule ID. Rule `composed_member_envelope_mean.v1` (lower = mean of member lower endpoints, upper = mean of member upper endpoints — Sol) is the DEFAULT the seat implements now. The packet's proposal (`… ± t95·s(point)/√50 ± one authenticated window allowance`) is registered as `composed_member_envelope_mean_t95_window.v1`, a PROPOSED pre-collection rule that goes before a cold gate before any `_v5` collection consumes it (it changes a claim-bearing interval; the magistrate does not adopt statistical composition rules alone). The seat implements both behind the rule ID with tests; the registry rows name which rule each placement binds to (default now).
- Q-R1-3 ADOPTED: three refusal levels (artifact / cell / per-token companion).
- Q-R1-4 ADOPTED: ratio of sums over the same fixed members; runtime-observed or `server_usage` denominators only; prefill four-surface equality; decode output count 512 (D-166).
- Q-R1-5 ADOPTED: Sol's custody-rich wire with explicit `campaign_role`; no `rendered` object; the paper renderer owns formatting.
- Registry amendment (in the seat's scope): DS-09..24 rows bind to the new fields; the stale "basis undefined" text is corrected to cite the generator-frozen universe.

## R2 — gamma claim renderer, `claim_side_bound`, prefill token family (DS-28..33, PG-01..08)
- Q-R2-1 ADOPTED: B is the named `E_clock_anchor_shift_bound_j` contrast term (D-078/D-083); the artifact guide sentence saying otherwise is amended by this ruling (cite it in the registry row).
- Q-R2-2 ADOPTED: required sibling `claim_side_bound` in `joulewise.claim_verdicts.v2`; v1 unchanged; the producer emits v2 from now on with a v1 compatibility path only for reading.
- Q-R2-3 ADOPTED: Sol's full symmetric family; DS-28/PG-04 bind to `S_*_joint_J` (= F + B) plus signed sizing clearance, never floor-only clearance.
- Q-R2-4 ADOPTED: Sol's branches with Fable's concise surface; the two registered Refusal sentences and D-166's 3/4-count sentence byte-exact.

## R3 — `joulewise.transfer_fiducial_result.v1` and TR-01
- Q-R3-1..3 ADOPTED: content-addressed projection over the reviewed capture; public names `largest_composed_edge_residual_bound_s` vs `pulse_derived_timing_bound_s` with the raw-interval witness and `b_fiducial_s` source binding; enum `supported|not_supported|not_evaluated`; token `[TRANSFER_FIDUCIAL_RESULT]`; six-decimal seconds; every sentence begins "Diagnostic only:"; nine byte-identical sites.
- Fence: the capture producer lives on the unreviewed branch d67ee56c and is NOT adopted here; the renderer binds only to the projection schema and a fixture. Accepting the capture is a separate gate.

## R4 — D-165 outcome renderer (OB-01, OR-01), from the refuter findings
- B1: the registry must carry the exact professor-facing rendering strings BEFORE the renderer's acceptance test can compare against them. The seat's fix round registers them in OB-01/OR-01 (rows amended in scope), derived from paper-G's branch-selection rules: OB-01 = the list of below-two components in registered order with cell and component names; OR-01 = "before comparison: <model> — <issued stop reason>" or "at close-out: <issued reason>; affected: <components or 'none recorded'>". The test compares against the registered bytes.
- F1: before-comparison stops are read from governed source bytes (the whole-window admission artifact and its validator result), never from a caller-authored dict.
- F2: no caller `precedence` channel. The registered stage order applies: a before-comparison stop wins over a close-out stop; a single-stage input renders without any precedence input; a two-stage input renders the before-comparison stage and records the close-out reason as secondary.
- F3: the at-close-out reason is the top-level authenticated refusal reason; affected components come from ratio records when present, else "none recorded"; a top-level source/census refusal renders without requiring a matching ratio record.
- F4: a `_v5` identity gate (fixed Qwen3-1.7B / Qwen3-8B pair and revisions from the authenticated manifest) precedes any fill; a Qwen2.5 manifest returns STOP_FILL with reason `identity_not_v5`. Fixtures switch to the Qwen3 identity.

## Seats
R1 → D123-REPORTED-MEAN-SUPPLIER-01; R2 → GAMMA-CLAIM-RENDERER-01; R3 → TRANSFER-RESULT-RENDERER-01; R4 → D165-OUTCOME-RENDERER-01 fix round 1. All Sol xhigh, fixtures only, no measurement values; each acceptance test as the packet's agreed parts state; refuter pair + Opus counter-review before any merge.
