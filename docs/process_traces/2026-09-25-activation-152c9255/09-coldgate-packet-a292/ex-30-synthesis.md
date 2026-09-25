# 07/30 — A292 reducer design: synthesis of three blind seats (Sol 6.0, Astra 6, Opus 5.5) with magistrate proposals

Comparison drafted by an Opus 5.5 subagent (disputed facts verified, no policy chosen); proposals in §P by the magistrate (Opus 5.5, activation 152c9255). Seats: [03-seat-sol](03-seat-sol.md), [03-seat-astra](03-seat-astra.md), [03-seat-opus](03-seat-opus.md). Paths are relative to the repo at `75d04e9e`. I verified every disputed fact and pick no policy.

Cited files: **45/10** = `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md`, **45/21** = its sibling `21-coldgate-fable-addendum-ruling.md`; **15/10** = `docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md`, **15/21** = its `20-addendum/21-coldgate-fable-addendum-ruling.md`; **89** = `docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md`; **07d** = `docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md` (AP-5M v4, the analysis plan); **kernel** = `docs/process/state_kernel.json`.

## Terms (built before use)

- **Registered item.** A (model, MATH problem) pair fixed before the night. **Cell.** A (model, level) pair: two models ("8B" and "1.7B" roles) × five levels = ten cells, keyed `"{model_id}:{level}"`.
- **Envelope.** A fixed-length power-capture slot running one model, numbered 0, 1, 2 …; `loaded` or `idle_slot`. **Block.** Items of one model and level run back to back in one envelope. **Parent.** A block from the initial packing; after an overrun it can split into one-item **singles** that keep `parent_block_id`.
- **Placement.** `(block_id, attempt, stage, reserved_s, envelope_index)`: this attempt of this block runs in this envelope; `attempt` starts at 0, +1 per new placement (15/10:37). **Observation.** The runner's per-block report: `completed`, `cut_off` (envelope ended first) or `not_started`, with elapsed time.
- **Roster.** The packer's JSON schedule (`joulewise/scored_packer.py:176-188`); `pack` makes the root, and after each envelope `requeue_overrun` appends one **event** and re-plans.
- **Sealed roster.** One `verify_executed_roster` accepts (`scored_packer.py:491-495`): digests check, re-packing reproduces the root digest `registered_sha256`, and replaying every event reproduces the input field for field. The **final digest** is `roster["sha256"]` after the last event.
- **Live / voided attempt.** Live: its `block_id` is still in its envelope's `blocks`; only live windows count (15/21:78). Voided: moved to `voided_block_ids` on retry, split, reschedule or terminal (`scored_packer.py:442-443`).
- **Capture window.** Gross joules for one `(block_id, attempt)`, per block, never per item. **Score row.** The scorer's verdict on one item.
- **Terminal refusal.** A roster record for an item never to be counted; two types: `ceiling_violation` (a single overran its derived worst case on its last retry, falsifying a registered bound) and `unattributed_overrun` (an envelope overran with no culprit block). One record per item (`scored_packer.py:444-449`), so a multi-item block's items share one key. A terminal type is never a **refusal code** (89:417); a refusal code means `reduce` raises with `.code` and returns nothing.
- **Fully counted parent.** A parent every item of which has a counted window.
- **Executed spread.** A cell is `spread_exceeded` with fewer than 5 fully counted parents or fewer than 5 distinct envelopes holding them (45/10:71; 45/21:58). Example: 10 items at block size 2 = 5 parents; one lost live window leaves 4, so the flag is true.
- **Executed drift.** A parent's position = mean envelope index of its counted items; a level's lever = |mean 8B parent position − mean 1.7B parent position|; `drift_exceeded` = lever > registered `max_gap`. Lever is null when either model has zero fully counted parents (15/21:76); partly counted parents still add positions (`scored_packer.py:137-157`). Example (`tests/test_scored_packer.py:318-340`): |6.6 − 5| = 1.6.
- **Cap hit.** `generated_tokens ≥ cap_tokens[arm]`. A capped attempt counts as incorrect even when its answer parses (07d:544, rule K3).
- **The M3 label.** `CAP_BOUND_FRACTION = 0.20` (`joulewise/scored_registration.py:25`): a cell with **more than** 20 % capped attempts is labelled "cap-bound" (07d:251,553-558; from item M3 of consult 19). 2 of 10 is not; 3 of 10 is.
- **NE / NR.** Statuses the estimator lane A293 (older name "A281b") assigns: NE = not estimable (`ceiling_violation`); NR = not resolved (spread, drift, `unattributed_overrun`, …).
- **CARRIED / CONSUMED.** A CARRIED constant is handed to a consumer lane, whose gate needs a test where changing it changes the output (the CONSUMED witness). **PROVISIONAL witness.** An A291 `reduce`-column test run only against a helper; A292 re-runs it through real `reduce` (15/10:47).
- **Oracle.** An independently written checker.

## R1 — Schemas and refusal vocabulary

**Agreed by all three (Sol R1, Astra R1, Opus R1):**
- `reduce(registration, roster, predicted_decode_s, <rows>, <windows>)`; its first statement is `verify_executed_roster(registration, roster, predicted_decode_s)`, checked by an AST test. `PackingRefusal` passes through unchanged.
- Exact key sets, checked types (`bool` is not an int). Rows and windows carry `registration_sha256 == registration.digest` and a roster digest. Rows also carry `scorer_id == registration.scorer_id`.
- Windows arrive as a list. A duplicate `(block_id, attempt)` refuses, and so does a key that matches no placement.
- Own exception class with `.code`; no new `inv_*` numbers; terminal types stay records, never codes.
- Block energy is summed once per counted window, never once per item.

**Splits**

**S1. Which roster digest rows and windows carry.**
- Sol and Astra: the final `roster["sha256"]`.
- Opus: the "in-force" digest (root, advanced by every event with a lower `envelope_index`). Decisive facts: the final digest does not exist at capture time, so a later stamp proves nothing; only an in-force stamp evidences runner rule FT-9 (15/21:74).
- *Verified:* no ruling names the digest; only "both the registration and roster digests" (kernel:3832; 45/10:59). Opus's timing fact is correct (events arrive in index order, 15/21:82); Astra concedes the same risk.
- *Options:* final (simplest; stamped after the run), root (stampable at capture; identical on every record), in-force (stampable; evidences FT-9; runner must hold the per-envelope roster).

**S2. Row contents, and where the K3 rule is applied.**
- Sol and Astra: rows copy `model_id, arm, level, retry_stage, parent_block_id, prompt_tokens`, plus final `outcome` ∈ {correct, incorrect, malformed, truncated} and a `truncated` bool, each cross-checked against the roster.
- Opus: no copies ("derive-not-copy", 45/10:25); raw `scorer_match` and `extracted_answer`; reducer derives `correct = scorer_match and not capped`.
- *Verified:* K3: "The parsed text is kept for a sensitivity analysis" (07d:544). Only Opus's row carries it; K3 does not make the reducer the keeper.

**S3. The `stop_reason` vocabulary.**
- Sol: any nonempty string. The cap is checked through `truncated` only.
- Astra and Opus: `stop_reason` ∈ {`stop`, `length`}, with the rule `(stop_reason == "length") == capped`.
- *Verified, and each side is partly right:*
  - No ruling fixes a vocabulary (Sol). The MLX runner emits `runtime_failed`, `malformed`, `length` and stop conditions like `requested_tokens_emitted` (`joulewise/adapters/mlx_runtime.py:338,568,590,611,624`), which the Astra/Opus rule refuses; Opus sends their typing to the runner lane.
  - K3's gloss: "a row whose `stop_reason` disagrees with the token-count test is refused by the reducer" (07d:546-547). Sol's design never tests `stop_reason`, so it does not enforce that clause.

**S4. Rows for voided (superseded) attempts.**
- Sol and Astra: refuse rows not matching a live placement. Opus: pass them through verbatim as `superseded_rows`.
- *Verified:* K24: "Every superseded attempt's answer and tokens are recorded and never used", plus `attempt_divergence` disclosure (07d:196). It names no recorder; if A292 refuses them, another component must record them.

**S5. Base class of the refusal exception.**
- Sol and Opus: `ReductionRefusal(ValueError)`. Astra: `ReductionRefusal(PackingRefusal)`.
- *My check:* under Astra's choice `assertRaises(PackingRefusal)` also catches reducer refusals, so a re-run A291 witness asserting only the class could pass wrongly. Opus adds a code-set disjointness test.

**S6. Output and window shape.** None of these is ruled.
- Sol: `counted_rows`, `counted_windows`, `excluded_windows`, `terminal_refusals`, `cells` (with `cap_hit_fraction`), `executed_status`. Astra adds a per-placement `attempts` ledger with `window_present`, `levels` with `evidence_status` (S11), and `accuracy`.
- Opus: `items`, `parents` (`g_j`, `k`), `cells` (`retry_stage_counts`, `mean_envelope_index`), `levels`, `uncounted_windows`, `superseded_rows`, output `sha256`; no ratios. Its windows add `envelope_index`, `bundle_sha256`, and `gross_j > 0` (others `≥ 0`).

## R2 — Window completeness

**Agreed by all three:**
- Only live keys enter sums and positions; voided and terminal windows are kept but excluded by rule (15/21:78; kernel:3832). Voided windows are optional (the draft's "all active windows" rule is not inherited). A `not_started` window refuses. `unreported_envelope` fires first, in the verifier (`scored_packer.py:494`). `executed_status` gets only accepted live keys.

**Splits**

**S7. A missing live window.**
- Sol and Astra: refuse the whole reduction. Their fact is the kernel's partition rule: "Every registered item is exactly one counted row or typed terminal refusal" (kernel:3832).
- Opus: no refusal; typed outcome `window_missing`, and spread/drift flag the cell. Facts: `executed_status` takes captured keys as input (89:379); spread is decided "from … the set of captured window keys" (15/10:41) "for any reason after capture" (45/21:58).
- *Verified:* Opus's quotes are accurate, but the causes listed at 45/21:58 (`ceiling_violation`, `unattributed_overrun`, unplaceable reschedule) exclude a missing window; `window_missing` is neither terminal type (89:417), so it breaks the kernel partition as written; AP-5M's NR list lacks it (07d:286). Yet AP-5M v4 **already** has an uncounted live window, `below_floor` ("the window is not counted", 07d:266), so "every live window counts" ends once the floor gate lands.
- *Options:* refuse (one lost capture voids the reduction; cure is recapture; nothing silent) or typed outcome (good cells survive; needs a ruled outcome type plus an AP-5M NR reason via HEADLINE-AP5M-AMENDMENT-01, else a silent drop).

**S8. A missing `ceiling_violation` window.**
- Sol and Astra: required; absence refuses (Astra: "a new completeness ruling"). Opus: optional; energy null.
- *Verified:* the ruled text is conditional: "A window for a terminal ceiling_violation attempt **is accepted**, recorded … never enters a cell sum" (45/10:79; K17 at 07d:746). Nothing mandates it; Astra's label is correct, and Sol's citation supports acceptance, not a requirement.
- *Options:* required (measured joules on every falsified bound; refuses a night whose one capture failed) or optional (disclosure only).

## R3 — Cap policy

**Agreed by all three:**
- Sealed v4 only; no parameter, flag or registration field selects semantics. v5 needs new registration, roster and reducer schemas and a new RED gate; the v5 draft is "PROPOSAL ONLY", splits thinking-cap hits from answer-allowance hits, uses (model, level, budget) cells, and says "A291 contract v5 is OPEN" (`docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:3,41,53`).
- `capped = generated_tokens >= cap_tokens[arm]`, and a capped item is never counted correct.
- `cap_bound = n_capped / n_counted > CAP_BOUND_FRACTION`, per cell, over counted rows only.
- Constant imported by name; the witness patches the module attribute and the label flips. Boundaries: 2 of 10 false, 3 of 10 true.

**Splits**

**S9. `generated_tokens > cap`.**
- Opus: refuse (`tokens_over_cap`); the worst case `cap × s_per_token_upper + prefill_s` (`scored_registration.py:99-102`) assumes the cap is never exceeded. Astra: explicitly capped; Sol: implicitly.
- *Verified:* Opus's fact is correct and the MLX runner stops at the cap (`mlx_runtime.py:623-624`), but the ruled `≥` admits `>` as capped (07d:549). Refusing is a new rule.

**S10. `cap_bound` when a cell has zero counted rows.** Sol and Astra: `false`. Opus: `null`. No ruling covers it.

**Only one seat (verified): Opus.** AP-5M v4 contains reducer rules that the merged code cannot carry yet:
- `below_floor` needs `floor_gate_j`, which is not in `REGISTRATION_KEYS` (`scored_registration.py:28`; 07d:266).
- K24's counted-attempt rule and `attempt_divergence` (07d:196).
- `night_exhausted` and per-night levers (07d:801). The seal refuses these until K25 is ratified (07d:810,1324-1325).

Opus: v1 has no registered-mode claim path until these are ruled in.

## R4 — Executed spread and drift

**Agreed by all three:**
- Affirm the merged `executed_status` shape (proposed at 89:393-398): `spread_exceeded` over ten cells; `executed_drift_lever_slots` and `drift_exceeded` over five levels; null lever or null `max_gap` gives `false`. Spread is per cell, drift per level; RD-6's "per-level" wording loses (89:788).
- Partly counted parents contribute positions. The lever is null when either model has zero fully counted parents (tested at `tests/test_scored_packer.py:318`).
- The output reports the counts behind each flag.

**Split S11. Level-level spread and status in the A292 output.**
- Astra: emits `levels[].spread_exceeded` (OR of two cells), `reasons`, `evidence_status` ∈ {clear, NR, NE} ("not an A293 verdict"). Sol and Opus: A293 owns precedence; A292 emits no per-level spread flag.
- *Verified:* precedence is ruled to the estimator. NE wins "in the A281b total table" (45/21:60); "A293 reports it NR" (15/10:39); group status is an estimator step (07d:286).
- *Options:* Astra's adds a second precedence implementation the oracle must check; omitting it keeps one owner.

**Only one seat (verified):**
- Astra: FT-5 makes `unattributed_overrun` an independent NR reason even when spread passes (15/21:66). The scout's map omitted it.
- Opus: new, unruled `internal_disagreement` refusal when the reducer's own counts contradict `executed_status` (exit-injection witness).
- Opus: record `mean_envelope_index` per cell for the R6-1 rule. That rule is "PROPOSED, unratified" (`docs/process_traces/2026-09-24-activation-278ebc9e/117-coldgate-packet-a291-finalpass/20-coldgate-fable-finalpass-ruling.md:63`).

## R5 — INV-12

**Agreed by all three:**
- No dependency on the INV-12 reconcile lane. No assertion rests on the checker's stricter INV-12 clause (`docs/process_traces/2026-09-24-activation-278ebc9e/82-coldgate-packet-a291-r3method/30-addendum/21-coldgate-fable-r4-addendum-ruling.md:63`).
- The verifier is not weakened; all PROVISIONAL witnesses re-run at the real entry.

*Verified:* Opus's probe P4 showed that a forged single `predicted_item_s` is refused by replay with `inv_38`. The code confirms it: replay rebuilds singles from the parent (`scored_packer.py:453`) and then compares the whole roster (`:488`).

**Split S12. Witness form.** Opus pins `code in {"inv_12", "inv_38"}`; Astra records the actual code, never asserting `inv_12`; Sol keeps it out of RED assertions. All are neutral to the INV-12 lane's outcome.

## R6 — Stopped draft `c0998fdb`

**Agreed by all three:** untrusted source of test inputs only; copy no code; derive every expectation fresh. The kernel says it "is not accepted" (kernel:3861). Defects: obsolete `_verify_roster`; obsolete fields `arm`, `origin_attempt`, `ceiling_violation`, stored `drift_exceeded`; plain-string refusals; no `scorer_id` or digests.

**Only Opus (internal inconsistency):** R6 gives draft line ranges for the harness seat to mine; R7 says that seat is "never shown c0998fdb as code". Both standing means passing extracted cases as prose.

## R7 — Delegation

**Agreed by all three:**
- Harness seat: tests + independent oracle (no `joulewise` imports); implementation seat: `["joulewise/scored_reduce.py"]`; RED committed first, tests failing individually. The oracle is needed: `tests/scored_roster_checker.py:794-865` checks rosters, not rows or energy sums.

**Split S13. Independence mechanics.**
- Astra: the implementation seat may not read harness or oracle source. Opus: a differential test over ≥ 200 generated nights with 0–25 % seeded live-window drops (`generate_case` exists, `tests/scored_case_generator.py:99`). Sol: no "OPEN code" placeholders. Nit: oracle file names differ (`scored_reduce_checker.py` / `scored_reducer_checker.py` / `scored_reduction_oracle.py`).

**Only one seat (verified): Astra.** The packer's partial-parent witness removes a **live** key (`tests/test_scored_packer.py:337`). If S7 goes to "refuse", that input fails at `reduce`, and a terminal-degradation fixture is needed in its place.

## Defects only one seat found (verified)

1. **Per-item terminal energy counts a block's joules several times (found by Astra).** `unattributed_overrun` writes one record per item, all sharing one `(block_id, attempt)` (`scored_packer.py:445-449`; 15/10:25,29).
   A cut-off multi-item initial block with no culprit has a window and becomes `unattributed_overrun`; Sol's (terminal record + `gross_j`) and Opus's (`terminal_gross_j` per item) designs repeat its joules on every item. `ceiling_violation` is safe: only one-item singles reach it (`:444`).
2. **INV-13 moved to A292 (found by Opus).** The ruling reads «`retry_stage` is on every item row and flows into cells» (`docs/process_traces/2026-09-23-activation-d8cc9c0a/08-a281-round1-synthesis-and-rulings.md:13`; the move is at 89:491). Sol and Astra carry `retry_stage` on rows but never into cells. Only Opus's `retry_stage_counts` does.
3. **K3's `stop_reason` refusal is missing from Sol's design** (07d:546-547). See S3.

Split count: **13** (S1–S13).

## §P — Magistrate proposals (argument for the cold judge, not authority)

Principle: implement what the sealed v4 rulings say; where they are silent, choose the option that fails closed or discloses, and never invent a science rule. Anything that would be a new science rule goes to HEADLINE-AP5M-AMENDMENT-01.

- **P-S1 (roster digest): the in-force digest (Opus).**
  - Each window and each row carries the digest of the roster in force at its envelope's capture: the root, advanced by every event with a lower `envelope_index`.
  - The reducer recomputes that digest by replay and refuses a mismatch (`window_binding`/`row_binding`).
  - Reason: it is the only stamp that can exist at capture time and still evidence FT-9. A final digest stamped after the run proves nothing about capture.
- **P-S2 (row contents): derive, do not copy (Opus; 45/10:25).**
  - Rows carry identity (`registration_sha256`, in-force `roster_sha256`, `scorer_id`, `item_id`, `block_id`, `attempt`) plus the raw scorer outputs (`scorer_match`, `extracted_answer`, `generated_tokens`, `prompt_tokens`, `stop_reason`).
  - The reducer derives model, arm, level, stage and parent from the roster, and derives `correct = scorer_match and not capped` (K3). `extracted_answer` is kept for K3's sensitivity analysis.
- **P-S3 (`stop_reason`):**
  - Enumerate the runner's emitted vocabulary from `joulewise/adapters/mlx_runtime.py` into one reducer constant, pinned by a test against that module's emit sites.
  - Unknown values refuse with `row_stop_reason_unknown`.
  - The cap-class subset (the values the runner emits when it stops at the token cap) must agree with the token test, else `row_cap_disagreement` (K3, 07d:546-547).
  - Rows whose `stop_reason` is a runtime failure are scored outcomes of their placement, never silently dropped.
- **P-S4:** voided attempts' rows pass through verbatim as `superseded_rows`, never used in any sum (K24, 07d:196).
- **P-S5:** `ReductionRefusal(ValueError)` with `.code`, plus a test that the reducer's code set is disjoint from the packer's `inv_*` codes.
- **P-S6 (output):** Sol's minimal shape plus only the additions that accepted defects force:
  - `superseded_rows`;
  - `terminal_windows` (defect 1);
  - `retry_stage_counts` per cell (defect 2, INV-13);
  - a per-cell count of `unattributed_overrun` terminals (the FT-5 input to A293);
  - an output `sha256`.
  No ratios beyond `cap_bound`.
- **P-S7 (missing live window): refuse the reduction with `missing_live_window` (Sol, Astra).** The kernel partition rule is ruled; a typed `window_missing` outcome would be a new science rule. The cure for a lost capture is recapture. `below_floor` (AP-5M v4) enters only when `floor_gate_j` becomes a registration key through HEADLINE-AP5M-AMENDMENT-01, and it will be a ruled typed outcome at that time.
- **P-S8 (missing ceiling window): optional (Opus; Astra's label is correct).** The ruled text is conditional ("is accepted", 45/10:79). If absent, the terminal carries `gross_j: null`, disclosed.
- **P-S9 (`generated_tokens > cap`): capped, per the ruled `≥` (07d:549), plus a typed diagnostic count `tokens_over_cap` in the cell.** Opus's refusal would be a new rule. The judge may prefer it, because a runner exceeding the cap breaks the worst-case bound assumption.
- **P-S10:** `cap_bound: null` for a cell with zero counted rows (unknown, not false).
- **P-S11:** no level status in A292 output; A293 is the single owner of NE/NR precedence (45/21:60; 15/10:39).
- **P-S12:** Astra's form: record the actual refusal code, and never assert `inv_12`.
- **P-S13 (independence):**
  - harness seat `WRITE_SCOPE: ["tests/test_scored_reduce.py", "tests/scored_reduce_checker.py"]`, where the oracle imports no `joulewise` reducer internals;
  - implementation seat `WRITE_SCOPE: ["joulewise/scored_reduce.py"]`; it may RUN the harness but is instructed not to read the oracle source (Astra);
  - a differential test over ≥ 200 generated nights from `tests/scored_case_generator.py` with 0–25 % seeded live-window drops (Opus). Under P-S7, a dropped live window must refuse in both implementations;
  - no OPEN-code placeholders: every code is fixed by the ruling before RED (Sol).
- **Defects adopted:**
  - (1) terminal energy is recorded once per `(block_id, attempt)` in `terminal_windows`, and per-item terminal records reference that key, never a copy of `gross_j`;
  - (2) `retry_stage` flows into cells;
  - (3) K3 is enforced per P-S3;
  - Astra's partial-parent fixture is replaced by a terminal-degradation fixture under P-S7.
  - Opus's `internal_disagreement` refusal is adopted as implementation-level fail-closed consistency: the reducer's own counts must match `executed_status`.
- **Deferred, not implemented:** `below_floor`, K24's `attempt_divergence` disclosure, `night_exhausted` and per-night levers (all need registration keys that the seal refuses until K25 and the AP-5M amendment); `mean_envelope_index` for the unratified R6-1 rule. These are recorded for HEADLINE-AP5M-AMENDMENT-01.
