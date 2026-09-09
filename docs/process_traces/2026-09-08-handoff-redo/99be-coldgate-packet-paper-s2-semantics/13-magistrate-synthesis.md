# Magistrate synthesis — S2 reported-energy semantics (interactive magistrate, 2026-09-08 ~13:40 PDT)

Three seats on packet sha 8c119bcb… at e241e0b7: cold Fable (10), Opus contract lens (11), Astra consult (12).
Unanimous: Q3 = ratio of totals on runtime-observed counts; F5 = register now, numbers only after the frozen
extraction spec exists. Q1 unanimous on the POINT ESTIMATE (equal weight over the complete ordered 50-member
universe; Astra's 0.2·mean(r)+0.8·mean(b) is algebraically the same number). Splits resolved:

1. Q1 admission (Opus governs, stricter and already registered): the v5 generators register
   `arithmetic_mean_over_fixed_member_universe.v1`, `expected_n: 50`, `missing_or_invalid_member: refuse_reported_mean`
   (generate_configs.py ~:2081–2087 / 8b ~:2119; pinned by tests/test_d117_floor_qwen25_1p5b_plan.py ~:1260). There is
   NO post-collection admission filter: any absent/invalid member refuses the cell; never a 49-member mean; `[N_bundles]`
   renders `expected_n`. The judge's "exclusion only by admission code" is narrowed to this.
2. Q1 independence unit (Opus + Astra, protocol :465–467 authority): 20 units per cell — 10 absolute repeats and 10
   complete A/B/B/A blocks — never the 50 bundles (the judge's n=50 is REJECTED: null members of one block are not
   independent draws).
3. Q2 stochastic half (Astra's variance formula governs; judge/Opus composition shape governs): because the point
   estimate is the stratified mix m = 0.2·mean(r) + 0.8·mean(b), its sampling variance is V = 0.2²·s_r²/10 +
   0.8²·s_b²/10 (Astra 12 §F2); the pooled s/√20 form the other seats wrote weights units equally in the variance but
   not in the mean and is REJECTED. Reference ν = 9 (conservative; the smaller stratum's df). Half-width h =
   t(0.975, 9)·√V. Mutation: with s_r ≠ s_b the pooled and stratified half-widths differ.
4. Q2 deterministic half (judge + Opus govern; Astra's Cartesian-product envelope is REJECTED as non-auditable and
   unregistered): endpoints = m ∓ (h + B), B = Σ over registered deterministic-bound kinds of each kind's average across
   the same members (protocol :349–364; the same construction estimators.py ~:483–486 already gates the claim decision
   interval); a kind whose recorded bound is absent REFUSES the cell (never zero); the D-078 ~1 J attribution limit is
   published as the labelled floor BESIDE the cell, never composed; detection_floor.py ~:879's sqrt(1+1/n) prediction
   term is excluded by name. The artifact records n, s_r, s_b, V, h, every kind term and B so that upper − lower =
   2(h + B) is recomputable.
5. Q3 (unanimous + Opus's object): per_token = ΣE_i/ΣT_i over exactly the 50 members of §1; a NEW sibling
   `phase_ratio_estimand` object (form ratio_of_totals, numerator gross_phase_energy_j, phase, denominator ∈
   {runtime_observed_prompt_tokens, runtime_observed_output_tokens}, tokenizer/output-policy scope) with the same
   exact-key, fail-closed validator discipline as the existing ratio estimand, which is NOT loosened; prefill T_i =
   observed total − observed output, cross-checked across the four surfaces (bundle_read.py ~:1005–1045); any absent,
   zero, malformed or fallback-sourced denominator REFUSES the per-token value without dropping members or touching the
   energy mean.
6. F5 (unanimous, Opus's corollary adopted): the registrations are installed NOW in the generators that emit the
   frozen extraction spec (both v5 packs) AND in the S2 contract; a doc-only registration is not a pre-registration.
   The absent `extraction_spec.json` blocks numbers, not estimands; the registration digest must predate the spec's
   first existence (judge §4 ordering fence).
7. Standing caveats (Opus): the X5 rows are RETIRED_FALLBACK under D-174 — these registrations restore no placement;
   every registration binds a `cell_id` (three reported cells per model: decode, prefill-p42, prefill-p512), never the
   word "prefill"; the paper's prefill cell is G2-a's `[PREFILL_LENGTH]`.
8. Seat F1 (launch-baseline anchors): RULED superseded for runner-owned lanes — codex-run-v3 snapshots its own
   baseline and records head_start/head_end in the envelope; BASELINE_MANIFEST/DIGEST are a bridge-protocol v1.1
   requirement the wrapper does not yet emit; follow-up BRIDGE-BASELINE-ANCHORS-01 (wrapper emits the header fragment).

Decision-log entry D-179 records 1–7. S2 seat relaunched (Astra high) with this synthesis; scope extended to the
two v5 generators, their plan test, and docs/decision_log.md.
