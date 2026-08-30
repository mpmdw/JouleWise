# Cold-gate ruling — D-166 R-2 prefill rule: margin reading and ladder (2026-08-30)

## §0 Seat and contamination disclosure

Cold Fable instance (claude-fable-5), fresh session, no loop context. Context
given to me: the launcher prompt (which named the reading order, the questions,
and the binding decision principles) and this repository's standing CLAUDE.md /
CLAUDE.local.md / memory files. I read, in order: `00-PACKET.md`; the D-166
ruling trace `04-MAGISTRATE-RULING.md` plus the margin-bearing lines of all
three seat files; the projection
`docs/paper/round7/prefill-resolvability-projection.md` and a structural
spot-check of the `.json` (both from branch
`paper/prefill-resolvability-projection` via `git show`, no checkout);
`joulewise/window_duration_margins.py:791-806` and `:1085-1099`;
`joulewise/reduce.py:105-120`; decision-log rows D-122/D-164/D-165/D-166; and
the PR #241 generator
(`configs/campaigns/d117_contrast_v5/generate_configs.py` on
`origin/feat/v5-ladder-prep`) at its prefill-refusal and candidate-set sites.
I read no other loop trace and consulted no other agent.

Packet claims verified at their cited sites before use:

- D-166 index-row text is verbatim as quoted (decision_log.md row D-166).
- R-2 source text is verbatim: "the shortest of {512, 1024, 2048} tokens whose
  small-model members show ≥ 3 overlapping records with margin (≥ 5) in every
  shakedown member" (04-MAGISTRATE-RULING.md, R-2).
- `sample_count_margin = overlapping_power_interval_count − MIN_PHASE_SAMPLES`
  (window_duration_margins.py:801-803), `MIN_PHASE_SAMPLES = 3`
  (reduce.py:116), and the equality is schema-enforced — a receipt with
  `margin != count − 3` is rejected (window_duration_margins.py:1091-1093).
- The projection's numbers match the packet's §3 summary (1,127 bundles;
  gapless tiling, max inter-record gap 2.4e-7 s; count = floor(D/S)+1
  validated on all 7 measured groups; 1127/1127 label agreement claimed;
  period stats p99 = 127.59 ms confirmed in the JSON's `periods_used`).
- Measured Qwen2.5 single-item minima: 512 → 3, 1024 → 3, 2048 → 6,
  4096 → 10 (projection §6/§9); 512-as-suite-item fails 211/650.
- D-122 sizing rationale as packeted (~5 J practical bar; 256-token
  projection ~11.62 J).
- The generator refusal cited by Q3 exists verbatim:
  `prefill_length_unresolved: D-166 requires the G2 shakedown result; no
  default or placeholder length is permitted`, followed by a hard-coded
  candidate check `prefill_length not in {512, 1024, 2048}`.
- Seat usage of "margin": Sol counted margin against three ("four or more
  gives one-record margin", 01-sol-seat.md:53); Opus used it qualitatively —
  4–5 records at 2048 "passes with margin" (02-opus-seat.md:83, :202); the
  Fable seat called 2–3 records at p256 "marginal" (03-fable-seat.md:41).

## §1 Verdicts

### Q1 — Reading B binds: "margin ≥ 5" means overlapping-record count ≥ 5 per member. RULED.

Derivation, in decreasing order of weight:

1. **Internal coherence of the ruled instrument.** R-2's own evidentiary
   basis, cited inside the ruling ("Opus's 0/20 at p128 and Fable's 2–3 at
   p256 stand as the reason p256 is dead"), came from seats whose highest
   projection at the ladder's top rung was 4–5 records at 2048
   (02-opus-seat.md:83) — and Opus called that a PASS "with margin." Under
   reading A (count ≥ 8) every rung of the ladder the magistrate ruled was
   already dead on the projections in front of the magistrate at ruling time.
   A reading under which the ruled selection procedure is facially
   unsatisfiable on its own cited evidence is not the binding reading; no
   seat, in any file, ever wrote a number implying count ≥ 8.
2. **Sentence structure.** "≥ 3 overlapping records with margin (≥ 5)": under
   reading B the "≥ 3" clause does real work — it names the reducer's
   physical floor (the rule), and the parenthetical strengthens it to the
   pre-registered safety floor of 5, i.e. 5 = 3 + 2. Under reading A the
   "≥ 3" clause does no work whatsoever (count ≥ 8 makes it dead text). A
   parse that leaves half the sentence with no function loses to one that
   gives every clause a job.
3. **The physics derivation the paper needs.** Records tile at ~112–129 ms
   (p99 127.59 ms). The reducer refuses below 3 records; 3 is the physical
   rule, not a choice. A guaranteed count of 5 buys, concretely: (a) at
   least 3 fully-interior records, so the majority of the energy integral
   rests on complete records with only the 2 edge records partial; (b) a
   whole-record safety of 2 against the two count-reducing events the corpus
   actually exhibits — adverse tile alignment (worth −1 versus typical, per
   the guaranteed/typical spread in projection §8) and a merged record from
   dropped samples (the 460.7 ms tail in §4). "Why 5?" answers: floor 3
   plus 2 records of measured-failure-mode safety. "Why 8?" answers nothing —
   the number 8 appears nowhere in any seat, ruling, or measurement, and a
   hostile reviewer asking for its derivation gets silence. The rule is
   stronger justified from the physics than from the repo's field
   convention, and the decision principles bind me to that preference.
4. **What reading A had going for it, and why it loses.** The repository's
   only machine-checked quantity named "margin" is `sample_count_margin`
   (count − 3), and Sol's seat used that convention. This is real textual
   support — and it is exactly why the bare word must not survive into the
   pre-registration (see Q3): the two conventions are reconciled by stating
   the rule as a COUNT. In field terms the binding rule is
   `sample_count_margin ≥ 2`. Reading A's convention is kept for the field;
   reading B's number is recognized as the count floor the ruling set.

Consequence: the projection's §9 contingency column "Under reading B" is the
operative one — the ruled ladder has exactly one surviving rung (2048) on
retained evidence.

### Q2 — AMEND: extend the ladder to {512, 1024, 2048, 4096}; the selection rule is otherwise unchanged; the exhausted-ladder branch is stated, not implied. RULED.

The rule as amended: **the `_v5` prefill length is the shortest of
512/1024/2048/4096 prompt tokens at which every small-model G2-shakedown
member's prefill phase shows an overlapping-power-record count ≥ 5
(`sample_count_margin` ≥ 2), counts taken from the production reducer; if no
rung clears, the prefill arm is collected at 4096 and the reducer's
`not_resolvable_sample_count` refusal is printed as that contrast's result,
with the Holm family frozen at m = 2.**

Derivation:

1. **The ruled ladder reproduces reviewer finding D1 at its top rung.** Under
   the binding reading, retained evidence leaves one survivor: 2048 (measured
   Qwen2.5 minimum count 6; projected guaranteed 5 at the assumed 1.133×
   slowdown). Its speed headroom is ~10% — projection §10 shows 2048 clears
   count ≥ 5 down to 0.91× and no further. The sensitivity runs one way, and
   a Qwen3 prefill faster than Qwen2.5's is plausible for a newer
   architecture. A ladder whose only viable rung sits 10% from failure is
   "designed to land ON the resolvability threshold" — the exact defect D1
   indicted in the p256 arm — moved up the ladder rather than removed.
2. **4096 is the only length with measured margin, and it is nearly free.**
   164 retained phases, minimum count 10, margin +7; Qwen3 would need to be
   ~2.2× FASTER than Qwen2.5 to fail count ≥ 5 there. Cost: ~21 s of added
   generation across 40 members ((1.12 − 0.59 s) × 40 ≈ 21 s — arithmetic
   checked) in a window budgeted in hours.
3. **D-122's sizing rationale says longer helps, on every stated axis.** The
   prefill delta must clear the ~5 J practical bar with margin; energy grows
   with prompt length (256-token projection ~11.6 J, longer lengths well
   clear), and the anchor-envelope edge-term ratio shrinks as phase energy
   grows. Nothing in the record identifies a scientific cost to a longer
   prefill arm; the estimand ("energy to prefill this pinned L-token prompt")
   is equally well-posed at any rung.
4. **The amendment fixes the rule, not the outcome.** G2 measures the real
   Qwen3 counts before selection executes; extending the ladder changes what
   the measurement MAY select, never what it does select. "Shortest that
   clears" is retained — it keeps the arm as close to a typical request
   length as the instrument permits and forecloses the post-hoc charge of
   maximizing the effect size. No free parameter is added: one rung and one
   stated refusal branch.
5. **Alternatives rejected.** (a) *Ladder stands as ruled*: leaves the
   refusal branch one plausible speed difference away, for an
   instrument-design reason knowable now — D1 again. (b) *Fix 4096
   outright*: abandons the measured-selection design D-166 established and
   forfeits the shorter lengths the shakedown may prove fine; it also
   answers "why 4096?" with "we liked the margin" instead of "the
   pre-registered rule selected it." (c) *Reading A / floor 8*: kills every
   ruled rung on retained evidence and forces 4096 unconditionally through
   the back door — a threshold chosen to force an outcome is the opposite of
   a defensible rule. (d) *Lower the floor below 5*: removes the safety
   factor whose absence D1 indicted; the floor's derivation (3 + 2, §1.Q1.3)
   is the paper's defense and is not to be traded for rungs.
6. **Vacuous-satisfaction hole, closed.** "Count ≥ 5 in every member" is
   vacuously TRUE over a rung with zero members. The selection must refuse
   to evaluate any rung with no small-model members at that length in the G2
   record; an unevaluable rung cannot be selected. (The minimum member count
   per rung is a G2 runbook parameter the magistrate should fix before the
   shakedown — I flag it in §3 rather than legislate a number ruled nowhere.)
7. **Decided ≠ done (implementation clauses, named).** The amendment binds
   code: the PR #241 generator's candidate check
   (`configs/campaigns/d117_contrast_v5/generate_configs.py`, the
   `prefill_length not in {512, 1024, 2048}` guard immediately after the
   `prefill_length_unresolved` refusal) must become
   `{512, 1024, 2048, 4096}`, and the `prefill_length_unresolved` refusal —
   which is correct and stays — should cite D-166-as-amended. The
   dedicated prefill floor cells in both floor packs must accept the same
   four-rung outcome space.

### Q3 — Amended, so both deliverables follow. RULED.

The exact replacement sentence is in §2. The `_v5` generator's
pre-registration object (the post-G2 prompt pin / selection record) must
encode, numerically and without the bare word "margin" as a threshold:

1. `ladder_prompt_tokens = [512, 1024, 2048, 4096]` — ordered, closed set.
2. `min_overlapping_power_interval_count = 5` — the binding floor, stated as
   a count.
3. `min_phase_samples_pinned = 3` and the derived
   `sample_count_margin_floor = 2`, with a validity check that
   `min_overlapping_power_interval_count − min_phase_samples_pinned =
   sample_count_margin_floor`; a future change to the reducer constant then
   breaks the object loudly instead of silently moving the rule.
4. The selection rule as an expression over the G2 record: selected length =
   the shortest rung r in the ladder such that the rung is evaluable (≥ 1
   small-model member at r; runbook minimum applies) and
   min over those members of `overlapping_power_interval_count` ≥ 5 — counts
   read from the production reducer's `summary_metrics.json` (the pipeline
   the projection validated 1127/1127 against raw bytes), never recomputed.
5. The shakedown binding: G2 corpus identity plus per-member SHA-256s of
   `events.jsonl` and `power_trace.csv` for every member the selection read,
   and per-member `{phase start, phase end, count, sample_count_margin}` —
   all fields the bundle format already carries (projection §12; nothing new
   to build).
6. The exhausted-ladder branch, literally: if no rung clears, `prefill_length
   = 4096`, arm collected, `not_resolvable_sample_count` printed as the
   prefill contrast's result, Holm family frozen at m = 2 (the denominator
   never shrinks to reward the failure).
7. The existing fail-closed behavior retained: the generator refuses to
   finalize while `prefill_length` is unresolved
   (`prefill_length_unresolved`), and refuses any length outside the
   four-rung ladder.
8. `selection_authority` upgraded from free text to the pair
   {G2 record path/ids, this ruling's trace path} so the pin names what
   selected the number.

## §2 Exact replacement text

Replace, in the `docs/decision_log.md` D-166 index row, the clause:

> `_v5` prefill length fixed from the G2 shakedown record (shortest of
> 512/1024/2048 with ≥3 overlapping records, margin ≥5, in every small-model
> member), pre-registered before the mint.

with:

> `_v5` prefill length fixed from the G2 shakedown record: the shortest of
> 512/1024/2048/4096 prompt tokens at which every small-model shakedown
> member's prefill phase shows an overlapping-power-record count ≥ 5
> (equivalently `sample_count_margin` ≥ 2 against the reducer floor
> `MIN_PHASE_SAMPLES` = 3 — the floor is the physical rule, the +2 the
> pre-registered safety factor against adverse record alignment and merged
> records; a rung with no small-model members is unevaluable and cannot be
> selected); if no rung clears, the prefill arm is collected at 4096 and the
> reducer's `not_resolvable_sample_count` refusal is printed as that
> contrast's result, Holm family frozen at m = 2; pre-registered before the
> mint. [AMENDED by cold gate 2026-08-30
> (`docs/process_traces/2026-08-30-prefill-margin-coldgate/01-COLD-RULING.md`):
> "margin ≥5" disambiguated to count ≥ 5; ladder extended to 4096; refusal
> branch made explicit.]

The same disambiguation applies wherever the ruled sentence is quoted (the
R-2 text in `04-MAGISTRATE-RULING.md` stays untouched as the historical
record; the projection's §2 NEEDS-RULING is answered by this document).

## §3 What I could not verify

1. I did not rerun `scripts/paper_prefill_resolvability_projection.py` or
   open raw bundle bytes; I rely on the projection's self-reported hash
   discipline and its 1127/1127 reducer-label agreement, which I verified is
   claimed and internally consistent, not reproduced.
2. The 1.133× Qwen3 slowdown is, by the projection's own statement, an
   assumption with no measurement behind it; nothing I read measures Qwen3
   prefill on this machine. My Q2 ruling deliberately does not rest on it
   (the amendment is justified by the one-sided sensitivity, not the point
   estimate).
3. The consult-seat anomalies (the 4.39× energy-ratio-as-duration misuse; the
   nonexistence of any 256-token bundle) are consistent with the seat files
   I read, but I did not independently recheck the underlying energy tables.
4. PR #245's review state — I read the projection from its branch, not the
   PR thread.
5. **Open item for the magistrate (flagged, not ruled):** nothing I read
   fixes the G2 shakedown's member count per rung. "Every member" over 1
   member is weak evidence; the runbook (D-162 G2) should fix a minimum —
   I suggest ≥ 3 small-model members per rung — before the shakedown, and
   the pre-registration object should record the count actually observed.
6. The floor packs' dedicated prefill cells (Opus seat's rename
   `prefill_p256` → `prefill_p<L>` across both packs) — I did not audit
   those config sites; §1.Q2.7 names the obligation, the refuter should
   check the sites.
