# Cold-gate ruling: paper S2 reported-energy cell semantics (Fable, 2026-09-08)

**Contamination disclosure:** launch context held the global `~/.claude/CLAUDE.md`, the memory index (one-line pointers only), and a git-status snapshot. I read no RUN_STATE, AGENTS, repo CLAUDE, memory body, or doctrine. Read: packet (sha256 verified), exhibit A, and only the files the packet names, at head e241e0b7. Probes were foreground; no bundle was reduced or extracted (none exist on this head).

## 1. Q1 mean_basis / ordered_members — rule (a)

**Estimand.** The arithmetic mean of the reducer's gross phase energy (`gross_energy_j`, reduce.py:601) over every admitted bundle in the complete preregistered ordered universe of the cell, each bundle weighted equally.

**Universe.** Per phase cell: the ten absolute repeats plus the forty null A/B/B/A members (10 blocks × 4), in collection order, as the v5 pack fixes them (generate_configs.py:590-619; `A_equals_B` :733; `same_prompt_for_all_floor_members` :964). This is D-123 cl.1's "same 50 members" (decision_log.md:7990-7993). The absolute component alone (n=10) is exactly the substitution the registry forbids (registry :378-381).

**Admission.** Only the frozen extractor admission codes (`CELL_REFUSAL_CODES`, floor_extraction.py:184-200) exclude a member; no exclusion by value (methodology :323-326, outliers never dropped). Ordered members come from the extraction spec's `cells[].members[].{slot,bundle_id}` (floor_extraction.py:1046-1075) and are inventoried at issuance (custody :290-293).

**Independence unit.** The bundle (one run). Admission does not establish independence (protocol :80-82); the registration states this, retains order, and defers dependence to X17 (custody :481-482). `N_bundles` = admitted count; the artifact also states universe size 50.

**Registration text.** "reported_mean_j = mean over admitted members of the cell's full ordered 50-member universe (10 absolute + 40 null-ABBA), equal weight per bundle, metric gross_energy_j; exclusion only by registered admission code; independence unit = bundle, assumed, order retained."

**Mutation.** s = 1 J: absolute-only gives N = 10 and half-width 2.262/√10 = 0.715 J; ruled basis gives N = 50 and 0.286 J (repo `student_t_critical_95`). N and both endpoints change.

## 2. Q2 interval_composition — rule (a), in the protocol's registered form

**Estimand.** Endpoints = mean ∓ (h + B): h is the Student-t 95% half-width of the mean, t_{n−1}·s/√n (methodology :321, settled); B is the sum over deterministic-bound kinds of each kind's average across the same admitted members (protocol :349-363, the "decision interval" construction; D-083 addendum's symmetric widening, decision_log.md:10963-10966).

**Kinds.** Interpolation-edge (zero for native interval-average records), idle-power drift (zero for gross), clock-anchor movement, whole-window drift allowance (protocol :358-363). A kind whose recorded bound is absent refuses the cell; it is never taken as zero.

**Excluded.** The D-078 ~1 J attribution limit is not composed in; it publishes as the labelled floor beside the cell, a separate mandatory role (D-078 addendum, decision_log.md:10945-10948). The partial-record enclosure is "reported, never composed" (:10951-10953). `detection_floor.py:879` is a prediction term for a new observation and is rejected as authority.

**Rejected (b).** Corner extrema recompute s at every joint endpoint choice (protocol :221-222): nonlinear, non-auditable, equal to (a) only in the mean term.

**Registration text.** "lower/upper = mean ∓ (t_{n−1,0.975}·s/√n + Σ_kind mean_members(bound_kind)); artifact records n, s, h, each kind term and B separately; attribution floor published adjacent, not composed."

**Mutation.** n = 50, s = 1 J: h = 0.286 J; prediction term would be 2.041 J. With B = 0.25 J the ruled endpoints sit at ±0.536 J; measurement-only at ±0.286 J.

## 3. Q3 per_token_aggregation — rule sum(E_i)/sum(T_i)

**Estimand.** The ratio of total admitted gross phase energy to total observed tokens over the identical admitted set from ruling 1, equal to mean energy per request divided by mean observed tokens; it reconciles with the request mean, which mean(E_i/T_i) does not.

**Denominator provenance.** Decode: `workload_observed.output_token_count` with `token_count_source == "server_usage"`, or runtime token events; `config_fallback` and `stream_chunk_fallback` yield no denominator (reduce.py:3736-3752, settled). Prefill: observed prompt count = `workload_observed.token_count − output_token_count` (bundle_read.py:1018-1022), cross-checked by strict admission against the tokenize and prefill `prompt_tokens` surfaces (:1037-1041); never the configured `prompt_tokens` (generate_configs.py:585).

**Missing/zero.** Any admitted member lacking an observed positive T_i refuses the per-token cell (STOP_FILL). Dropping the member is forbidden: it would fork the universe from ruling 1.

**Registration text.** "J_per_token = Σ E_i / Σ T_i over ruling-1 admitted members; T_i source ∈ {server_usage, runtime_observed} recorded per member; prefill T_i = observed total − observed output; any absent T_i refuses the cell."

**Mutation.** E = (10, 10) J, T = (100, 200): ratio 0.0667 J/token; mean of ratios 0.075 J/token. A configured 512 replacing an observed 480 shifts the value 6.7% and looks plausible.

## 4. F5 — extraction spec prerequisite

The frozen extraction specification is a prerequisite for producing numbers and N, not for registering the estimands. The spec schema (`joulewise.detection_floor_extraction_spec.v1`, floor_extraction.py:150) already fixes the ordered member join, so S2 registers against cell role and member structure now, under the supply map's pending role (supply_map.json:3-10). Ordering fence: the registration digest must predate the spec path's first existence; the gate refuses otherwise. No production digests in this lane (exhibit A F5, sustained).

## Failure-mode test

Yes: an absolute-only mean, a measurement-only or prediction-term endpoint, and a configured-count denominator each pass plausibility. Guards: N and universe size published and replayed against the ordered inventory; artifact carries h, B, and kind terms so upper − lower = 2(h + B) is recomputable; per-member denominator source recorded and gated to the allowed set.

**NOT EXECUTED:** no extractor or reducer run; whether the v5 pack records a whole-window drift bound is unverified.

**Verdict: adopt 1(a), 2(a) in protocol form, 3 ratio estimator, F5 register-now/produce-later; S2 installs the three registrations before any spec or bundle exists.**
