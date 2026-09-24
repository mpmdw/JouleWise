# 21 — Cold Fable addendum ruling, A291-CONTRACT-01 (A1–A13)

Judge: Claude Fable 5.1, fresh session, worktree `JouleWise-wt-coldgate-a65fb4fa-r2` at `c2c2e47e`. Code cited at `c0998fdb` (`c:<file>:<line>`). Written 2026-09-24 01:37–01:55 PDT.

## 0. Disclosure, pins, method

Auto-loaded before I acted: `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, the memory index `MEMORY.md` (pointers only). None used; no memory file, RUN_STATE, TASK_QUEUE, council log, run report or trace outside this packet directory was opened. Read: charter, `00-charge.md`, ex-10, ex-11, ex-00 §1, ex-45-21 §7–8, ex-02b (INV-03, 15, 24–28, 35–37, §2.3–2.7, §5), ex-45-10 (§Q4 position rule, F3), and `c0998fdb` via `git archive` at `/tmp/cg-add-c0998fdb`.

Validator run 1 (charter `…5d82`, the deliberate typo): `REFUSE`, reason `charter_trusted_observed_mismatch`, rc 2. Run 2: expected charter `099de884…5d81`, expected packet `c8f09f4f…6d53`; observed both equal; `PASS`, rc 0; seven exhibits, every observed digest equal to the manifest. Method: `shasum -a 256` reproduced both values.

Executed probes: `/tmp/cg-add-c0998fdb/probe/addendum_sim.py` (mine, literal application of Q7/Q8/(W) and the (N) arithmetic) and the refuter's `/tmp/ref-a291-c0998fdb/probe/ruled_text_sim.py` (re-run). Both reproduce R1 case 1 (`A:single:0 → unattributed_overrun` while B is a late culprit), R1 case 2 ((W) reschedules B, Q8 seal sees no initial-stage culprit → raise) and R2 (cumulative 3, 6, 8, 10 against a bound of 8; per-item culprit events A 2, B 2, C 0, D 0). Mixed-stage envelopes are reachable: Q9's ruled eligibility list has no stage clause, so envelope 41 (holding parent B) admits `A:single:0`. Nothing NOT EXECUTED.

Culprit, as used throughout: an observation whose `elapsed_s` is a number greater than its block's bound, `predicted_s` at the `initial` and `whole_block` stages, the derived worst case for singles. Final texts are numbered FT-1…FT-14 in §3; §1 gives the verdict and the deciding evidence only.

## 1. Rulings A1–A13

**A1 — ACCEPT R1, BLOCKER stands; text rewritten (FT-1).** Deciding: both executed cases above; (W) «provided the envelope holds a culprit» has no stage restriction, so Q7's parenthetical and Q8's stage-local seal each contradict the standing text on a reachable roster. Q8's finiteness argument survives without stage locality (see A2). Cure: one stage-agnostic culprit predicate, one no-culprit outcome for every uncompleted block, one seal check.

**A2 — ACCEPT R2, MATERIAL; text rewritten (FT-2).** Deciding: the executed arithmetic. (N)'s inference «each innocent reschedule is caused by one culprit event … so the total is at most 2 × singles» is invalid because one culprit event reschedules every other block in the envelope; the roster is legal under 45/10 §Q4 (siblings may share) and Q9. The last sentence of (N) is superseded by this addendum, expressly presented (charge A2), not reinterpreted. Factor 2 is not a constant; 02b §5's «Factor 2 of (N)» row is deleted. Finiteness: culprit events are ≤ 1 per parent (initial stage; a `whole_block` retry is alone and reschedules nothing) plus ≤ 2 per single item, and each reschedules ≤ (blocks in the envelope − 1).

**A3 — ACCEPT R3, MATERIAL; text (FT-3).** Deciding: Q9's sentence omits split-created singles; `c:scored_packer.py:273-284` appends them to a retry tail, merging while capacity allows, which is the same net behaviour as lowest-eligible-else-fresh once each placement updates eligibility. One placement rule for all moved work (ruling 10 Q8's own principle). Order within an event and execution order inside an envelope are ruled as the refuter proposes; a `whole_block` advance always creates a fresh envelope ((W) «alone in a fresh envelope») and that envelope is ineligible for every later placement (Q9).

**A4 — ACCEPT R4 in part, MATERIAL; text rewritten (FT-4).** The refuter's second sentence is unbuildable: a root roster has only `initial` placements (02b INV-36 «A root roster has only initial placements»), so it cannot exercise a single-stage edge. Cure: the witness form follows the row's ruled consequence on that path (refusal / recorded value / root-only refusal), and «(root roster)» is defined as `events == []`.

**A5 — ACCEPT R5, MATERIAL; text (FT-5).** Deciding: (W) «its cell is unresolved until a registered recapture» versus Q12's extension of (P), which names only `ceiling_violation`, `spread_exceeded`, `drift_exceeded`; the eight-parent counter-example resolves a level (W) forbids resolving. NR, not NE: the item may be recaptured.

**A6 — ACCEPT R6, MATERIAL; text (FT-6).** Deciding: 02b INV-03 line 94 lists `models` among the forbidden copy keys and §2.3's exact key set has none; Q4(iii) named `roster.models`. Order is derived from `registration.role_to_model_id` by role.

**A7 — ACCEPT R7, amended, MATERIAL; text (FT-7).** `drift_lever_slots` is the planned lever (02b §2.3; 21/10 D5b); Q12's `planned_drift_lever_slots` is a naming error. `planned_spread_shortfall` becomes a derived roster key with an exact ten-cell key set, always present, recomputed at every seal run (the refuter's "recomputed at every seal exit" leaves the entry check unstated).

**A8 — ACCEPT R8, MATERIAL; text (FT-8).** Deciding: a replay that applies recorded decisions accepts a forged `keep` on an over-worst single with consistent digests; Q20 left the choice open. `requeue_overrun` takes observations without `decision`, so replay needs no stripping step and never calls `_digest`.

**A9 — ACCEPT R9, MATERIAL, as a runner-lane obligation row, not a CARRIED field row; text (FT-9).** (G)'s CARRIED list holds registration fields and constants; a sequencing duty is an obligation. Under A13(i) below, `observations is None` means "not yet run", so the scheduler side is also closed: a report is refused unless it is the lowest unreported loaded envelope.

**A10 — ACCEPT R10, NIT; text (FT-10),** extended to the planned lever, whose 02b type already admits `null`.

**A11 — ACCEPT R11, NIT; text (FT-11).**

**A12 — YES, MATERIAL (the refuter under-tiered it); text (FT-12).** A report whose elapsed sum exceeds the window's interior is not evidence of anything: the capture cannot cover the work. The bound is not microscopic: the runner cuts work off at capacity = `interior_s − guard_s`, so a legitimate sum has `guard_s` of headroom. Same class as Q19's `invalid_elapsed`.

**A13 — three further silent choices, all MATERIAL; texts (FT-13, FT-14, and the `late` rule inside FT-1).**
(i) Which envelopes are reported. ex-00 §1 glosses `requeue_overrun` as called «after an envelope in which work ran over», which leaves a clean or completed-late envelope unreported and makes `observations is None` ambiguous between "ran clean" and "not yet run", the very state Q10's high-water mark was added to patch. Ruled: every loaded envelope that has run is reported, in index order, without gaps; `reduce` refuses an unreported loaded envelope. This makes 45/21 A2's hazard unrepresentable and makes "finished roster" (Q13) exact.
(ii) Observation order within an envelope. Sequential execution allows only completed*, then ≤ 1 cut_off, then only not_started; a checker fed `[not_started, completed]` has no rule.
(iii) `late` for a single. Q6 says `late: false` for `≤ worst` and is silent for the advancing completed single; the block key is one bool. Ruled: `late` = latest observation is `completed` with `elapsed_s` > bound.

## 2. Findings, tiered

- **BLOCKER B1** (A1): stage-local culprit texts; cured by FT-1.
- **MATERIAL M1** (A2) false (N) bound; **M2** (A3) placements; **M3** (A4) witness forms; **M4** (A5) NR(`unattributed_overrun`); **M5** (A6) `models` key; **M6** (A7) key names; **M7** (A8) replay re-derivation; **M8** (A9) runner sequencing; **M9** (A12) physics guard; **M10** (A13 i) report completeness; **M11** (A13 ii) observation order; **M12** (A13 iii) `late` for singles.
- **NIT N1** (A10), **N2** (A11), **N3**: ruling 10 Q7's edge count "eleven edges; thirteen paths" stands; the 02b §5 factor-2 row is deleted (A2).

Disagreement with ruling 10: Q7, Q8, Q9, Q12, Q13, Q15, Q20 amended; Q4(iii) corrected; Q6 completed (FT-11). With the refuter: A4 second sentence (unbuildable), A7 (entry check), A9 (row kind), A12 (tier). Packet hygiene: adequate; both probes re-executed; the refuter's quotations of ruling 10 match the sealed file. No question REFUSED.

## 3. Final texts (paste verbatim into the checker and implementer briefs)

These supersede the corresponding ruling-10 texts and the last sentence of 45/21 §7 (N). Bound(b) := `predicted_s` when the block's stage is `initial` or `whole_block`, else the item's derived worst case.

**FT-1 (culprits, no-culprit outcome, `late`; replaces ruling 10 Q7 and the Q8 seal sentence; INV-35(a)).** "An observation is a culprit iff its `elapsed_s` is a number and `elapsed_s > Bound(block)`, at any stage; `not_started` is never a culprit. In one `requeue_overrun` call: a culprit `completed` at the `initial` or `whole_block` stage keeps its window with decision `keep`; a culprit single, completed or not, advances (`single_problem`→`single_retry`, `single_retry`→`ceiling_violation`); an uncompleted culprit parent advances (`initial`→`whole_block`); a `whole_block` `cut_off` splits. Every other uncompleted or `not_started` block, at any stage, is rescheduled without advancing iff the event's observations contain at least one culprit at any stage; if they contain none, each such block becomes the typed terminal state `unattributed_overrun`, one `terminal_refusals` entry per item, and the call never raises. Closed edge list: the nine edges of (G) plus `single_problem→unattributed_overrun` and `single_retry→unattributed_overrun` (eleven edges, thirteen paths). INV-35(a): every `reschedule` decision, at any stage, sits in an event whose observations contain a culprit; the seal refuses (`reschedule_without_culprit`) otherwise. A block's `late` is true iff its latest observation is `completed` with `elapsed_s > Bound(block)`; for a culprit single that completed, `late` is true on the block while its completed attempt is voided (FT-11)."

**FT-2 (replaces the last sentence of (N); INV-35(b),(c)).** "Each parent has at most one culprit observation at the `initial` stage and each single item at most two culprit observations across all events; the seal refuses (`culprit_limit`) a roster violating either. Within one event the count of `reschedule` decisions is at most the number of blocks in the reporting envelope minus one; the total over a roster is therefore finite. No numeric cap on total reschedules applies; factor 2 is not a ruled constant and 02b §5's row for it is deleted."

**FT-3 (placement; replaces the last sentence of ruling 10 Q9).** "Reschedules, the singles created by a split, and advancing singles each take the lowest eligible index under Q9, else a new envelope appended at index `len(envelopes)`; a `whole_block` advance always takes a new envelope. Within one event, placements are made in the order of the reporting envelope's pre-call `blocks` list, and a split's singles in ascending `j`; each placement updates eligibility for the next. An envelope's `blocks` list is its execution order; every placement appends to it; the event's `placements` list is in creation order."

**FT-4 (appended to ruling 10 Q15).** "A root roster is one with `events == []`. For every (row, path) cell the witness form follows the row's ruled consequence on that path: (a) refusal: a violating input on that path is refused with the typed refusal; (b) recorded value: a violating input on that path reaches the exit and the recorded value equals the ruled value (e.g. `planned_spread_shortfall[cell] == true`, `drift_lever_slots[level] > max_gap`), and a mutant that suppresses or alters the record is killed; (c) root-only refusal (the five-parent/five-envelope minima): on `pack` form (a); on every `requeue_overrun` path form (b), the shortfall introduced by the event or by entry injection of a non-root roster in shortfall; at `reduce` the (b) form against `verify_executed_roster` (PROVISIONAL per Q16). The seal refuses the minima (`spread_minima`) only when `events == []`, at whichever entry or exit it runs. No cell is `n/a`."

**FT-5 (appended to ruling 10 Q12's precedence sentence).** "A level any of whose cells holds an `unattributed_overrun` refusal is NR(`unattributed_overrun`) unless NE(`ceiling_violation`) applies to that level; NR reasons accumulate and every applicable reason is recorded."

**FT-6 (replaces ruling 10 Q4(iii)).** "(iii) The model order everywhere (iteration, idle assignment, tie-breaks) is by role, derived from `registration.role_to_model_id`: the `"8B"`-role model first, the `"1.7B"`-role model second, never the mapping's insertion order. The roster carries no `models` key."

**FT-7 (key names).** "Ruling 10 Q12 reads `drift_lever_slots[level]` (the PLANNED lever, 02b §2.3) wherever it wrote `planned_drift_lever_slots`. `planned_spread_shortfall` is a derived roster key (02b §2.3 gains the row): an object whose key set is exactly the ten cells `"{model_id}:{level}"` with `level` a decimal string `"1"`…`"5"`, every value a bool, never absent; true iff that cell's non-terminal parents number fewer than five or occupy fewer than five distinct envelopes. It is recomputed at every `pack` and `requeue_overrun` exit; `_seal` asserts at every run that the stored object equals the recomputation (`stale_derived`); `pack` refuses (`spread_minima`) when any value would be true."

**FT-8 (replaces ruling 10 Q20's replay amendment).** "`requeue_overrun(registration, roster, envelope_index, observations)` takes observations carrying only `block_id`, `status`, `elapsed_s`; it derives every `decision` and placement. Replay: `reduce` recomputes `root = pack(registration, predicted_decode_s)`, asserts `root["sha256"] == registered_sha256`, then for each `k` calls `requeue_overrun(registration, roster_{k−1}, events[k].envelope_index, events[k].observations without decision)` and asserts that the re-derived decisions and placements equal the recorded ones and that the returned roster's `sha256` equals `events[k].sha256`; finally it asserts the replayed roster equals its input roster field for field. `_seal` remains the sole caller of `_digest`; replay compares digests it never computes."

**FT-9 (runner-lane obligation row, added to the CARRIED list as a non-field row).** "Runner lane: envelope `r+1` does not start until `requeue_overrun` for `r` has returned and its roster is loaded; if it cannot, the runner reports `r+1` with every block `not_started`."

**FT-10 (appended to ruling 10 Q12 and Q14).** "When a model has zero counted parents at a level, the executed lever for that level is `null` and `drift_exceeded` is not set; that cell is `spread_exceeded` (0 < 5) under (X). When a model has zero non-terminal parents at a level, `drift_lever_slots[level]` is `null` and no drift refusal or record applies."

**FT-11 (appended to ruling 10 Q6).** "The completed culprit single's `block_id` moves from the reporting envelope's `blocks` to its `voided_block_ids`; the voided window key is (`block_id`, that placement's `attempt`); `reduce` counts a window only when its `(block_id, attempt)` is a live placement."

**FT-12 (physics guard, seal).** "The seal refuses (`invalid_elapsed`) an event whose Σ `elapsed_s` over its observations exceeds `interior_s`."

**FT-13 (report completeness; extends ruling 10 Q10).** "Every `loaded` envelope that has run is reported by one `requeue_overrun` call, in index order, including envelopes in which every block completed; `idle_slot` envelopes are never reported. `requeue_overrun` refuses (`report_order`) unless the reporting index is the lowest `loaded` envelope with `observations is None`. `observations is None` therefore means not yet run. `reduce` refuses (`unreported_envelope`) a roster with any `loaded` envelope whose `observations is None`."

**FT-14 (observation order, seal).** "Within one event the observations, in the envelope's `blocks` order, consist of zero or more `completed`, then at most one `cut_off`, then only `not_started`; the seal refuses (`invalid_observation_order`) otherwise."
