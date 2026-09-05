# Blind Fable seat — answers to 05-consult-questions.md (2026-09-04)

(File name at authoring: 06-consult-fable-blind.md in the blind worktree; archived here as 12 per the consult numbering. The seat wrote to the fallback name because its $OUT variable was unset.)

Seat: blind, single session, foreground only. Auto-loaded before reading anything: `~/.claude/CLAUDE.md`,
repo `CLAUDE.md`, memory index `MEMORY.md`. Not read: CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md,
state_kernel.json, PROJECT_STATUS.md. `$OUT` was unset in this environment; written here.
Head: worktree at 5e416c47 (audits taken at cc56a9a7, bench at f4c812b4; none of the cited code moved).
Every witness below was re-executed this session; tails are pasted verbatim.

## Q1 ESTIMAND — AGREE (the P1 witness is correct). Remedy (a). Enclosure belongs in reduce.py.

Executed:
```
P1 point=9.000 interp=0.000 env=[8.800,9.200]
P1 nonneg partial-record enclosure=[8.000,10.000]
```
Code: `_integrate` multiplies each record's reported average by its overlap (`joulewise/reduce.py:167-180`);
both interpolation terms return 0.0 for interval traces (`reduce.py:515-520,554-555`); the corner envelope
moves window edges over the same held-average curve (`reduce.py:2148-2161` docstring, `2225-2245`). The
contract declares overlap clipping the point estimand (`docs/contracts/run_bundle_layout.md:805`), so the
reducer is faithful to its estimand; the break is the paper calling the envelope physical containment.
`phase_identifiability` (`reduce.py:2995-3008`) is a sample-count test and must not be called identifiability.

Not decorative: at 100 ms cadence and ~10 W the enclosure is ±1 J on a 1 s phase, the same order as the
D-078 ~1 J attribution limit and wider than the timing envelope. A reviewer will find this in minutes.

(b) is not available this week: within-record power shape is exactly what the sampler does not record; any
allocation model is an assumption presented as a bound. Choose (a) and say so in the abstract.

Where: a NEW additive reducer field (`phase_partial_record_enclosure_j: {lower, upper, straddling_records,
straddling_energy_j}`) — the reducer owns trace+windows, strict validation re-derives the reducer
(`joulewise/cli.py:468`) so the field is custody-checked for free, and floor extraction can carry it without a
second overlap implementation. Diagnostic only; frozen point/envelope untouched. Cost: half a Sol day with
the P1 curve as the oracle test, plus a golden bump. A desk script is second-best (second implementation,
outside the custody seam); use it only if the reducer version is frozen for the transaction.

## Q2 D-165 COMMON MODE — PARTLY: wrong substitute (both directions), cancellation ruling wrong, coordinates NOT retained. Rebuild.

Executed (issued rule vs exact shared-onset/shared-offset grid replay, same inputs):
```
P2 alternating onset slopes, offset flat: point=1.0000 issued_shared_sign R=1.500000 passes=False | exact R=2.250368 passes=True
same-sign onset slopes, offset flat:      issued R=1.500000 | exact R=1.500000
equal edge powers (onset +0.5, offset -0.5): issued R=2.000000 | exact R=2.000000
mixed magnitudes same sign:               issued R=2.350221 | exact R=2.350221
trials=3000 issued_pass_exact_fail=5 issued_fail_exact_pass=68 agree=2927
worst issued-over-exact example (R_issued, R_exact)=(2.008, 1.800)
```
So: when every block's edge sensitivities share a sign structure the two replays coincide; when they differ
the substitute errs both ways, including issuing R_cm ≥ 2 where a true shared edge shift gives < 2. It is not
a conservative surrogate. Mechanism: `split_common_mode_block_width` sums each block's onset and offset
extremes taken on its own grid (`dominance_closeout.py:313-331`); the replay then applies ONE sign to those
magnitudes (`683-700`). Sign and coordinate of the producing shift are discarded.

Absolute cancellation (`dominance_closeout.py:51-55`; `configs/campaigns/d117_contrast_v5/generate_configs.py:514-519`):
wrong as stated. `absolute_false_effect_floor` centres on the member mean (`detection_floor.py:919-928`); a
shared time shift δ moves member i by δ·(P_i(end) − P_i(start)), which cancels only when that edge-power
difference is equal across members. What cancels exactly is a shared ENERGY offset, which no registered
mechanism produces. Correct disposition: "not replayed", never "cancels exactly".

Timing coordinates: NO. Grids are per block, built from that block's own record support edges relative to
its window (`floor_extraction.py:2487-2503`); only the J values are retained (`339-344, 472-473, 636-637`)
and `COMMON_MODE_INPUT_FIELDS` (`dominance_closeout.py:56-66`) carries no shift coordinate. A cross-block
shared replay cannot be rebuilt from the sidecar. But raw bundles are retained and the contrast callable
already takes `(onset_s, offset_s)` (`floor_extraction.py:2525-2534`); overlap integration is additive, so
contrast(δon, δoff) = zp + [onset(δon) − zp] + [offset(δoff) − zp] exactly. The shared replay is one loop
over a COMMON grid (union of every block's breakpoints within ±B) maximising the comparative floor over
(δon, δoff); the floor is convex on each linear piece, so breakpoints suffice.

Remedy: REBUILD at extraction, as a second rule id beside `d165_shared_sign_local_corner_replay.v1` (do not
rewrite the wire; nothing is collected yet). Cost ≈ one Sol day + a P2-shaped oracle covering both sign
structures + gauntlet. Relabel alone leaves the abstract's second headline sentence ("moved together across
each group of four", P:29) unsupported; if the day is refused, cut that sentence and call R_cm a
registered shared-sign sensitivity. Either way delete the cancellation sentence (P:681-682).

## Q3 F+B METADATA — AGREE.

Executed: `two_gate outcome=direction_supported claim_ready=True (6 < 5+4)`. `attribution_single_count_discipline`
emits `effective_clearable_effect_formula="floor_j + claim_side_bound_j"` (`detection_floor.py:348-362`);
`evaluate_claim` tests |estimate| > floor and zero-exclusion of both intervals as separate conjuncts
(`analysis_engine/claims.py:336-375`); the decision interval is widened by the deterministic total
(`estimators.py:482-485`). D-083 itself says the sum is descriptive and enforcement is two gates
(`docs/decision_log.md:5315-5327`), so the metadata's "non-removable composition rule" contradicts D-083's own
enforcement clause. Add `planning_sizing_formula` and mark the old key deprecated rather than renaming (the
rule_id is on the wire); keep `both_terms_required` (it forbids deleting the claim-side bound as a
double count, which is right). D-083 addendum by date. No additive gate. Cost: one hour plus goldens.

## Q4 FLOOR PROMPT vs CONTRAST PROMPTS — AGREE it is a mismatch; choose CONTRAST ON PROMPT 0.

Verified: floor `rule_id ruling-171a-floor-index-zero.v1`, `prompt_index = 0`, `prompt_count 1`
(`configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:1031-1034`); contrast
`(block_number − 1) mod prompt_count`, `d166_block_prompt_cycle.v1` (`d117_contrast_v5/generate_configs.py:1380-1381,1541-1545`).
The prompt count is loaded from the pinned workload file (CG:911); I verified the rule, not the count of eight.
I found no "D-164 mirror rule" in the decision log (`grep mirror` hits only R-014 weight mirroring); the
operative rule is 171a, so 171a is what a floor-side change re-rules, not D-164.

Stronger defensible paper: one exact workload for floor and contrast. Contrast on prompt 0 satisfies
P:712-713 literally, keeps the absolute floor a same-condition repeat floor (cycling prompts through the
repeat arm would absorb prompt-to-prompt variation into the point floor and make R_abs a prompt-variance
test, not a timing-versus-repeat test), and changes ONE generator. The paper claims "the tested workloads",
never eight-prompt generality. Re-pin: contrast plan tree, decode suite census (CG:1487-1498), pack
digests, D-166 dated addendum; ≈ half a Sol day + gauntlet. Regenerating both floor packs costs two
generators, two packs, a 171a amendment, and changes what the absolute floor measures. Disclosure-only is
acceptable only if collection cannot slip a day; then P:712-713 must be cut and the transfer stated as an
assumption. Prefill arm unaffected (single G2-a pinned prompt).

## Q5 TRANSFER — AGREE: withdraw the TR-01 dependency now; a runnable protocol is not a this-week item.

Code: no inserted-gap code exists (`grep -rl TRANSFER-FIDUCIAL|inserted_gap joulewise scripts` → none; no
sleep hook in `adapters/mlx_runtime.py`). The detector admits only a POSITIVE plateau ≥ 10 W over baseline
(`powermetrics_fiducial.py:71,768,896`) inside a commanded pulse of 0.8–1.2 s (`95-96`, interior inset at
`749-756`); a 500 ms negative gap fails on sign and duration. "Without modification" (P:1313) is false in
code. Runnable means: inverted-pulse detector variant, MLX sleep actuation with command stamps, an
acceptance predicate ratified BEFORE the window (P:1177 and P:1324 currently contradict), one quiet window
with Ed away, an evidence supplier, and the gauntlet — 2–3 desk days on the critical path. Do: abstract
sentence → "Transfer of the pulse-derived timing allowance to inference was not tested"; P:1145 → conditional
wording (03-F2's text is fine); R:920 → WITHDRAWN_THIS_SUBMISSION (row kept). Write the one-line predicate
anyway (max|r_e| ≤ B_session supports transfer; else withdraw) so any late window is reportable as an
appendix diagnostic without post-hoc rule choice.

## Q6 SCOPE FREEZE

- Whole-window stop receipt: enables OR-01 "before comparison" only. The authenticated window-admission
  outcome already exists (R:921). Render OR-01 from it; PARK a new receipt family.
- Claim non-issuance receipt: OR-01 at claim stage / DS-32, PG-08 refusal branch. Same rule: `evaluate_claim`
  output is already an authenticated record; PARK the design unless it is the only way to render Outcome C.
- AUTH allowlist guard: PARK (already parked after three same-signature rounds; enables no paper surface).
- D-173 custody seam: KEEP, narrowed. It closes 02-F3/P3 (renderer publishes an unlabeled fixture with
  "operative floor is published"). Minimum: seam module + five refs + renderer refuses non-seam input and
  prints the fixture label. Not three mutation legs per family this week. Acceptance: P3 rerun prints
  SYNTHETIC or refuses.
- Kernel rows, skill-distill packet: PARK (bookkeeping; no figure).
- LINEAGE relocatable: PARK (post-hoc convenience; live launch refuses relocation anyway; DS-34 is separate).
- MODULARITY: landed byte-parity; nothing further. PARK follow-ups.
- What the paper needs and is NOT on this list: Q1 enclosure field, Q2 shared-edge replay, G2-a prefill pin,
  v5 renderer bindings (DS-30–33, PG rows; 03-F5), legacy-L1 cure, Figure 2 from `fig4_edge_excursions.svg`,
  References/Availability. That is the whole queue.

## Q7 LEGACY L1 — accept RETIREMENT from publication routes; the "voided demonstration" shape only if it prints no joule.

Verified: `LEGACY_LABEL` (`scripts/build_capstone.py:34`) is emitted by `generate_results_page` (`179-210`),
which still writes "idle-subtracted request energy (primary basis)" (`208-209`) against README:71, and
`--check` passes (`330-340`); `docs/report_src/chapters/07_results.md:6` includes the page. Acceptable shape:
(1) producer change, not markdown (regeneration undoes markdown edits); (2) generated page carries zero joule
values and no T1; first line names the D-078 void; (3) "primary" never describes idle-subtracted energy;
(4) keep F1/analysis files as history, unreferenced; (5) one `--check` regression asserting no `_j_` column
and no "primary basis". Reject any shape that keeps Table T1 under a "voided" caption — README:59 says the
values must not be quoted, and a table with a caveat quotes them. Drop "manual review" from the label; it
reads as an admission grade.

## Where I differ from the auditors

02-F2 implies the shared-sign replay is merely semantically off; it is anti-conservative in ~0.2% of random
sign-mixed sets and matches exactly whenever sign structures agree — the rebuild is a day, so rebuild.
03-F3 prefers regenerating the floor packs; I prefer contrast-on-prompt-0 for the absolute-floor reason
above. Q6's receipt lanes: both audits say freeze scope; I say render OR-01 from records that already exist.
