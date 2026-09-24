# 02c — A291 (HEADLINE-PACKER-RECUT-01): contract v3, as ruled

Installed 2026-09-24 by the contract-drafting seat (Opus 5.5) for the magistrate of activation a65fb4fa. This file completely replaces 02b. The checker seat and the implementer are briefed from this file alone.

This is INSTALLATION of dictated text. Every former `PENDING-GATE` item now carries the ruled text, quoted verbatim, with its source. Where a ruled text leaves a representation detail open, this file does not choose; §8 lists the question.

## 0. Conventions

### Precedence

When texts conflict, the earlier item in this list wins:
1. addendum §3 FT texts;
2. ruling-10 texts the addendum did not amend;
3. 45/21 §7;
4. 45/10;
5. 21/10;
6. 08.

Records 13 and 09 are representation authority only where 13 ruled.

### Source keys

`«…»` is verbatim. `c:<file>:<line>` means commit `c0998fdb`. Paths below are relative to `docs/process_traces/`.

| Key | File |
|---|---|
| [FT-n] | `2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md` §3 |
| [Qn] | `2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md` §1 |
| [A-n] | the same addendum, §1 |
| [45/21], [45/10], [21/10], [21/11], [08] | the prior rulings under `2026-09-23-activation-d8cc9c0a/` (full paths in 02b §0) |
| [19] | `2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md` |
| [13] | `2026-09-24-activation-a65fb4fa/13-a291-contract-synthesis-and-rulings.md` |

### Row tags

- **Ruled.** Every clause of the row is ruled text.
- **R[13].** A representation choice ruled by record 13.
- **RD-n.** A residual open detail, listed in §8. It is not chosen here.

### Culprit and Bound

«Bound(b) := `predicted_s` when the block's stage is `initial` or `whole_block`, else the item's derived worst case.» [addendum §3]

«An observation is a culprit iff its `elapsed_s` is a number and `elapsed_s > Bound(block)`, at any stage; `not_started` is never a culprit.» [FT-1]

### The thirteen closed paths

«Closed edge list: the nine edges of (G) plus `single_problem→unattributed_overrun` and `single_retry→unattributed_overrun` (eleven edges, thirteen paths).» [FT-1]

| Code | Path |
|---|---|
| `P` | `pack` |
| `E1` | `requeue_overrun`: initial→whole_block |
| `E2` | `requeue_overrun`: initial→reschedule |
| `E3` | `requeue_overrun`: initial→unattributed_overrun |
| `E4` | `requeue_overrun`: whole_block→single_problem |
| `E5` | `requeue_overrun`: whole_block→unattributed_overrun |
| `E6` | `requeue_overrun`: single_problem→single_retry |
| `E7` | `requeue_overrun`: single_problem→reschedule |
| `E8` | `requeue_overrun`: single_retry→ceiling_violation |
| `E9` | `requeue_overrun`: single_retry→reschedule |
| `E10` | `requeue_overrun`: single_problem→unattributed_overrun |
| `E11` | `requeue_overrun`: single_retry→unattributed_overrun |
| `R` | `reduce` |

A `requeue_overrun` call whose decisions are all `keep` takes no edge (RD-8).

### Witness rules

- «No invariant row/path cell may be `n/a`. Where no natural witness exists, use entry injection (a violating roster fed to the path) or exit injection (an internal step patched to emit the violation). Any residual `n/a` is a cold-gate exception, not a lens review.» [Q15]
- «A root roster is one with `events == []`. For every (row, path) cell the witness form follows the row's ruled consequence on that path: (a) refusal: a violating input on that path is refused with the typed refusal; (b) recorded value: a violating input on that path reaches the exit and the recorded value equals the ruled value (e.g. `planned_spread_shortfall[cell] == true`, `drift_lever_slots[level] > max_gap`), and a mutant that suppresses or alters the record is killed; (c) root-only refusal (the five-parent/five-envelope minima): on `pack` form (a); on every `requeue_overrun` path form (b), the shortfall introduced by the event or by entry injection of a non-root roster in shortfall; at `reduce` the (b) form against `verify_executed_roster` (PROVISIONAL per Q16). The seal refuses the minima (`spread_minima`) only when `events == []`, at whichever entry or exit it runs. No cell is `n/a`.» [FT-4]

Every row below carries a **Form** tag:
- (a) refusal, with its typed code where one is ruled (RD-10 otherwise);
- (b) recorded value;
- (c) root-only refusal.

Every row needs witnesses on all 13 paths. The `R` column is PROVISIONAL (Q16; see INV-39).

### Definitions (carried from 02b; unchanged unless tagged)

- `cap := interior_s − guard_s`.
- `worst(m) := cap_tokens[arm] × s_per_token_upper[m][arm] + prefill_s[m][arm]` (c:scored_registration.py:157).
- `n := n_per_level`.
- `bpc := ceil(n / block_size[arm])`.
- `max_gap := budget_j / (delta_upper_j_per_block_slot × bpc)` (c:scored_registration.py:169-170).
- `canon_sha(v) := sha256(json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()`. Numbers are hashed as accepted (R[13] OP-07).
- `LEVELS = [1..5]`.
- `RETRY_STAGES = ["initial","whole_block","single_problem","single_retry","ceiling_violation"]`.
- `MIN_PARENT_BLOCKS = MIN_ENVELOPES = 5`.
- **Placement:** §2.5 (R[13] F06). A placement is **live** when its `block_id` is in its envelope's `blocks`.
- **Planned position:** the 02b definition, the item-weighted mean envelope index of the live placements holding a parent's non-terminal items. It is unconfirmed after a requeue (RD-4).
- **Executed position:** «A parent's position is the item-weighted mean of the envelope indices of its executed windows: each item contributes the index of the envelope in which its counted attempt was captured. Voided attempts and idle slots contribute nothing.» [45/10 §Q4]

---

## 1. Invariant matrix

### A. Identity and digests

**INV-01 registration binding** (ruled). «Identity fields (`schema`, `registration_id`, `plan_id`) are CONSUMED: their witness is that a roster sealed under the old digest is refused by every consumer under the new registration.» [45/10 §Q2]
- Pred: `r.registration_sha256 == canon_sha(g)`.
- Form: (a).

**INV-02 roster self-digest** (ruled; preimage confirmed Q20). «The preimage rule, `event.sha256` = resulting roster digest, root `registered_sha256 == sha256`, uniform re-pack assertion, `parent_sha256` dropped: confirmed» [Q20]
- Pred: `r.sha256 == canon_sha(PRE(r))`. `PRE(r)` is `r` without the top-level `sha256`, the top-level `registered_sha256`, and every `events[k].sha256` (§2.7).
- Form: (a).

**INV-03 no copies; no `models` key** (ruled). «no roster copies of registered values» [45/21 §7(S)]; «The roster carries no `models` key.» [FT-6]
- Pred: every record's key set is exactly its §2 key set. No c0998fdb copy key appears: `models`, `arm`, `block_size`, `interior_s`, `guard_s`, `cap_tokens_by_arm`, `envelope_s`, `offset_s`, `pitch_s`, `capacity_s`, `levels`.
- Allowed: the roster's `schema`; the derived fields `claim_ready`, `item_set_sha256`, `n_per_level`, `drift_lever_slots` and `planned_spread_shortfall`; and `model`/`level` on records.
- Form: (a).

**INV-04 derived identity fields; equal level sizes** (ruled). «`item_set_sha256 := canonical_json_sha256([ids in level order])` is a derived roster field.» [45/10 §Q3]; «Every level's item list has the same length `n`; `n_per_level := n`; unequal lengths are refused (`unequal_level_sizes`).» [Q3]
- Pred: `r.item_set_sha256 == canon_sha(FLAT(g))` (the flat id list in level order, R[13] F02) and `r.n_per_level == n`.
- The registration refuses unequal lengths.
- Form: (a); `unequal_level_sizes`.

**INV-05 claim readiness** (ruled). «`mode = pilot` objects may emit only rosters flagged `claim_ready: false`; every consumer refuses a non-claim-ready roster outside pilot mode.» [21/10 §Q2 D4]
- Pred (a), producer: pilot mode implies `claim_ready == false`.
- Pred (b), consumer: at the `requeue_overrun` and `reduce` entry, non-pilot mode with `claim_ready == false` is refused.
- Form: (a).

### B. Registration and predictions

**INV-06 selected arm; worst-case ordering** (ruled). «`cap_tokens` and `block_size` have key set `{arm}`; `s_per_token_upper`, `prefill_s`, `ceiling_s` have inner key set `{arm}` for each model. Any other key is refused (`unselected_arm_entry`). The coherence inequality `worst ≤ ceiling_s ≤ interior_s − guard_s` is checked on the selected arm; `ceiling_s` stays CARRIED (runner).» [Q17]
- Pred: the key sets are as stated, and `worst(m) ≤ ceiling_s[m][arm] ≤ cap` for both models.
- Form: (a); `unselected_arm_entry`.

**INV-07 prediction domain** (ruled). «`pack` refuses any item above its derived worst case (P4)»; «Extra predictions are refused, not ignored (Sol 34 (d)).» [45/10 §Q3]
- Pred:
  - `set(p)` is exactly the two model ids;
  - `set(p[m])` is exactly the registered items;
  - each value is a finite JSON number, not a bool, with `0 < v ≤ worst(m)`;
  - the same bound holds on every parent's `predicted_item_s`.
- Form: (a).

**INV-08 prediction digest** (ruled). «Add registration field `predictions_sha256` (pilot-nullable, required in registered mode)»; «refuses when `canonical_json_sha256(predicted_decode_s restricted to the registered items)` ≠ `predictions_sha256`» [45/10 §Q3]
- Pred: registered mode requires the field to be non-null. When it is non-null, `canon_sha(PRED(r)) == g.predictions_sha256`, with `PRED(r)` rebuilt from the parents (R[13] OP-08). At `pack`, the check is on `p`.
- Form: (a).

### C. Items, blocks, parents

**INV-09 level keys and item identity** (ruled). «`item_ids_by_level` is a mapping whose key set is exactly `{"1","2","3","4","5"}` (strings). Any other key set, including integer keys, is refused by `Registration.from_mapping` with the typed refusal `item_ids_by_level_keys`. No normalisation.» [Q2]
- Pred: the key set is as stated; item ids are non-empty and globally distinct; each block's `level` is an int in LEVELS and its items belong to that level.
- Form: (a); `item_ids_by_level_keys`.

**INV-10 block formation and pairing** (ruled). «(i) For each level, in registered item order, parents are the consecutive slices `items[k·b:(k+1)·b]`, `b = block_size[arm]`, `k = 0,1,…`. (ii) Parent id `"{model_id}:{arm}:{level}:{k}"`; single id `"{parent_id}:single:{j}"`, `j` the item's zero-based position in the parent.» and «(iv) The checker tests membership equality across models and the parent relation (13 F05) AND these three rules.» [Q4]
- Also ruled: «When `n mod block_size[arm] ≠ 0` the last slice of each level is shorter and is a parent block in every count (M8, drift, spread).» [Q3]
- Pred: for each model, the parents are exactly those slices with exactly those ids. Membership is therefore equal across models.
- Form: (a).

**INV-11 item conservation** (ruled). «item conservation (per model, every registered item is in exactly one block that is neither superseded nor terminal, and that block is in exactly one envelope, or is in exactly one terminal refusal and no envelope)» [45/21 §7(S)]
- Pred: as in 02b.
- Form: (a).

**INV-12 parent relation** (ruled). «Pairing survives a split: singles carry `parent_block_id`, and the estimator pairs on the parent (Opus B2).» [08 F2(a)]; Q4(ii) above.
- Pred: `parent_block_id is None` if and only if the block is a parent.
- A single has one item. Its parent has the same model and level, contains that item, and is `superseded`. The singles of a parent partition its items. The single ids follow Q4(ii).
- Form: (a).

**INV-50 model order** (ruled). «(iii) The model order everywhere (iteration, idle assignment, tie-breaks) is by role, derived from `registration.role_to_model_id`: the `"8B"`-role model first, the `"1.7B"`-role model second, never the mapping's insertion order.» [FT-6]
- Pred: `pack` output is invariant under reordering the `role_to_model_id` mapping.
- Exit-injection witness: iteration in insertion order yields a different roster.
- Form: (a).

**INV-13** — moved to A292 (item rows carry `retry_stage`), per 02b.

### D. Envelopes, reporting and placement

**INV-14 model homogeneity** (ruled). «envelope model homogeneity» [45/21 §7(S)]
- Pred: every placement in `e` names a block of `e.model`.
- Form: (a).

**INV-15 empty-envelope legality** (ruled). «An envelope with no active block is legal iff its `kind` is `idle_slot` or its `voided_block_ids` is non-empty; `_seal` refuses any other empty envelope.» [45/21 §7(E)]
- Form: (a).

**INV-16 idle slots** (ruled). «An empty slot is captured as a full-length envelope with its model worker loaded and idle, and is labelled `kind: "idle_slot"` in the roster.» [08 F1]; «`e.kind == "loaded"`» among the Q9 eligibility conditions; «`idle_slot` envelopes are never reported.» [FT-13]
- Pred: an idle slot has `blocks == []` and `voided_block_ids == []`, has `observations is None` always, and receives no placement.
- Form: (a).

**INV-17 grid** (ruled; R[13] OP-27). «on a fixed-pitch grid in which idle slots are grid positions» [08 F1]
- Pred: the envelope indices are `0..N−1`, in list order.
- Form: (a).

**INV-18 fixed envelopes; placement above the reporter; report order** (ruled). «An envelope is fixed once an observation is recorded on it; a retry or reschedule is placed only at an index above the reporting envelope's.» [45/21 §7(E)]; «Events carry strictly increasing `envelope_index`; `requeue_overrun` refuses (`report_order`) a reporting index ≤ the last event's. Every placement created by event `k` has `envelope_index > events[k].envelope_index`. The seal checks both on every roster.» [Q10]
- Pred:
  - event `envelope_index` values strictly increase;
  - every placement listed in `events[k].placements` is above `events[k].envelope_index`;
  - on a transition, envelopes observed in `before` are unchanged in `after`.
- Form: (a); `report_order`.

**INV-46 report completeness** (ruled; new, A13(i)). «Every `loaded` envelope that has run is reported by one `requeue_overrun` call, in index order, including envelopes in which every block completed; `idle_slot` envelopes are never reported. `requeue_overrun` refuses (`report_order`) unless the reporting index is the lowest `loaded` envelope with `observations is None`. `observations is None` therefore means not yet run. `reduce` refuses (`unreported_envelope`) a roster with any `loaded` envelope whose `observations is None`.» [FT-13]
- Pred:
  - the set of `events[k].envelope_index` equals the set of loaded envelopes with non-null `observations`;
  - those envelopes form a prefix of the loaded envelopes in index order;
  - at `R`, no loaded envelope has `observations is None`.
- Form: (a); `report_order` and `unreported_envelope`. Where `unreported_envelope` is enforced is RD-7.

**INV-19 no reuse after split** (ruled). «The split stage never reuses the whole-block retry's envelope.» [45/21 §7(E)]
- Form: (a).

**INV-34 eligibility and placement order** (ruled). «Eligibility of an existing envelope `e` for a placement made by the event reporting envelope `r`: `e.index > r.index` and `e.index > max reported index` (Q10); `e.observations is None`; `e.kind == "loaded"`; `e` holds no `whole_block` placement; `e.model == block.model`; after placement M8-by-parent (no two parents of one cell in `e`) and `Σ reserved_s ≤ capacity` (live and voided placements) hold.» [Q9]; «Reschedules, the singles created by a split, and advancing singles each take the lowest eligible index under Q9, else a new envelope appended at index `len(envelopes)`; a `whole_block` advance always takes a new envelope. Within one event, placements are made in the order of the reporting envelope's pre-call `blocks` list, and a split's singles in ascending `j`; each placement updates eligibility for the next. An envelope's `blocks` list is its execution order; every placement appends to it; the event's `placements` list is in creation order.» [FT-3]
- Pred: the checker re-derives each placement target of each event, in the stated order, and requires equality.
- Form: (a).

### E. Capacity and reservations

**INV-20 capacity** (ruled; R[13] OP-21). «capacity by `reserved_s`» [45/21 §7(S)]
- Pred: `Σ reserved_s ≤ cap` over the live and voided placements of each envelope.
- Form: (a).

**INV-21 initial and reschedule reservations** (ruled). «An `initial` placement has `reserved_s = predicted_s = Σ predicted_item_s` and `Σ reserved_s ≤ capacity` per envelope. A `reschedule` placement keeps the block's previous `reserved_s`.» [Q11]
- Form: (a).

**INV-22 whole-block retry** (ruled). «The whole-block retry is scheduled alone in a fresh envelope with `reserved_s = min(Σ item derived worst cases, capacity)`; `predicted_s` is unchanged.» [45/21 §7(W)]; «a `whole_block` advance always takes a new envelope» [FT-3]
- Pred: as in 02b. The placement is alone in an envelope that its event appended.
- Form: (a).

**INV-23 single reservation** (ruled). «Each single is packed at `reserved_s = predicted_s = the item's derived worst case`.» [45/21 §7(T)]
- Form: (a).

### F. Spread

**INV-24 M8 by parent** (ruled). «No two parent blocks of one cell share an envelope at any stage, initial or retry.» [45/10 §Q4]
- The checker must ACCEPT sibling sharing: «Pieces of one parent may share an envelope with each other and with blocks of other cells of the same model, within capacity.» [45/10 §Q4]
- Form: (a).

**INV-25 planned minima: root-only refusal** (ruled). «The five-parent/five-envelope minima are a refusal only at `pack` (root roster). At `requeue_overrun` exits the seal checks M8-by-parent (no two parents of one cell share an envelope) and records, never refuses, a planned shortfall as `planned_spread_shortfall[cell]: true`.» [Q13]; FT-4 (c) above.
- Pred: when `events == []`, every cell has ≥ 5 parents in ≥ 5 distinct envelopes.
- Form: (c); `spread_minima`.

**INV-49 `planned_spread_shortfall`** (ruled; new). «`planned_spread_shortfall` is a derived roster key (02b §2.3 gains the row): an object whose key set is exactly the ten cells `"{model_id}:{level}"` with `level` a decimal string `"1"`…`"5"`, every value a bool, never absent; true iff that cell's non-terminal parents number fewer than five or occupy fewer than five distinct envelopes. It is recomputed at every `pack` and `requeue_overrun` exit; `_seal` asserts at every run that the stored object equals the recomputation (`stale_derived`); `pack` refuses (`spread_minima`) when any value would be true.» [FT-7]
- "Non-terminal parent" and "occupy" are RD-5.
- Form: (b), with `stale_derived` as (a).

**INV-26 executed spread** (ruled). «`spread_exceeded` is decided once, at `reduce` entry, from the finished roster and the set of captured window keys.» [Q13]; «A cell is spread-exceeded when its executed roster holds fewer than five parent blocks whose every item has a counted window, or fewer than five distinct envelopes holding them,» [45/10 §Q4]; «`reduce` counts a window only when its `(block_id, attempt)` is a live placement.» [FT-11]
- Where the value is carried, and its input signature, are RD-6.
- Form: (b) at `R` (PROVISIONAL).

### G. Drift and balance

**INV-27 planned lever** (ruled). «`requeue_overrun` recomputes and records `planned_drift_lever_slots[level]` and never refuses on it.» [Q12], read per «Ruling 10 Q12 reads `drift_lever_slots[level]` (the PLANNED lever, 02b §2.3) wherever it wrote `planned_drift_lever_slots`.» [FT-7]; «When a model has zero non-terminal parents at a level, `drift_lever_slots[level]` is `null` and no drift refusal or record applies.» [FT-10]
- Pred: the stored value equals the recomputation over planned positions (RD-4), compared with `isclose(rel_tol=1e-9)`, or is null per FT-10.
- Form: (b).

**INV-28 pack drift refusal** (ruled). «`pack` in registered mode refuses a planned lever > `max_gap` (21/10 D5b).» [Q12]
- Form: (a) at `P`; (b) on the requeue paths (FT-4 example).

**INV-45 executed lever and `drift_exceeded`** (ruled). «At `reduce` entry the executed lever is computed from counted windows (45/10 §Q4 position rule); if it exceeds `max_gap` the level carries `drift_exceeded: true`, its numbers are reported, and A293 reports it NR(`drift_exceeded`) until a registered recapture.» [Q12]; «When a model has zero counted parents at a level, the executed lever for that level is `null` and `drift_exceeded` is not set; that cell is `spread_exceeded` (0 < 5) under (X).» [FT-10]
- Where the value is carried is RD-6.
- Form: (b) at `R` (PROVISIONAL).

**INV-41 idle insertion and balance** (ruled). «One `idle_slot` is inserted iff both models have an odd envelope count; it is assigned to the `"1.7B"`-role model (`c:scored_packer.py:66, 113` under Q4(iii) ordering). Balance is the search objective; the checkable rule is the recorded `drift_lever_slots[level]`, ≤ `max_gap` at `pack` in registered mode.» [Q14]
- Pred: the root roster has exactly one idle slot iff both models' loaded-envelope counts are odd, and that slot has the 1.7B-role model. The drift rule is INV-27/28.
- Form: (a).

### H. Observations and decisions

**INV-29 observation record** (ruled). «`elapsed_s` for `completed` and `cut_off` is a finite JSON number > 0; `not_started` carries `elapsed_s: null`. A block cut off before consuming time is reported `not_started`. Zero or negative elapsed is refused (`invalid_elapsed`).» [Q19]; «`requeue_overrun(registration, roster, envelope_index, observations)` takes observations carrying only `block_id`, `status`, `elapsed_s`; it derives every `decision` and placement.» [FT-8]
- Pred: the observations cover the reporting envelope's pre-call `blocks` exactly, one each. `status ∈ {completed, cut_off, not_started}`. `elapsed_s` is as ruled. Each recorded observation carries the derived `decision` (vocabulary RD-9).
- Form: (a); `invalid_elapsed`.

**INV-47 observation order** (ruled; new, A13(ii)). «Within one event the observations, in the envelope's `blocks` order, consist of zero or more `completed`, then at most one `cut_off`, then only `not_started`; the seal refuses (`invalid_observation_order`) otherwise.» [FT-14]
- Form: (a); `invalid_observation_order`.

**INV-48 physics guard** (ruled; new). «The seal refuses (`invalid_elapsed`) an event whose Σ `elapsed_s` over its observations exceeds `interior_s`.» [FT-12]
- Form: (a); `invalid_elapsed`.

**INV-30 decisions, culprits, no-culprit outcome, `late`** (ruled). «In one `requeue_overrun` call: a culprit `completed` at the `initial` or `whole_block` stage keeps its window with decision `keep`; a culprit single, completed or not, advances (`single_problem`→`single_retry`, `single_retry`→`ceiling_violation`); an uncompleted culprit parent advances (`initial`→`whole_block`); a `whole_block` `cut_off` splits. Every other uncompleted or `not_started` block, at any stage, is rescheduled without advancing iff the event's observations contain at least one culprit at any stage; if they contain none, each such block becomes the typed terminal state `unattributed_overrun`, one `terminal_refusals` entry per item, and the call never raises.» [FT-1]; «A block's `late` is true iff its latest observation is `completed` with `elapsed_s > Bound(block)`; for a culprit single that completed, `late` is true on the block while its completed attempt is voided (FT-11).» [FT-1]
- Pred: the checker re-derives every decision and every `late` value from the observations and requires equality with the recorded values.
- Form: (a).

**INV-31 innocent initial-stage placement** (ruled). «An innocent initial-stage block is rescheduled with its previous `reserved_s` into the first eligible envelope under Q9, else a fresh one.» and «(X)'s 'a rescheduled parent the seal cannot place' is retained but unreachable (a fresh envelope always exists).» [Q8]. The seal sentence of Q8 is superseded by FT-1 (INV-35(a)).
- Form: (a).

**INV-32 whole-block outcomes** (ruled). «For a `whole_block` placement (always alone): `completed` → decision `keep`; `late := elapsed_s > predicted_s`; a late completion is a culprit with no mates. `cut_off` at any `elapsed_s > 0` → decision `split` (edge whole_block→single_problem); `elapsed_s` is recorded. `not_started` → decision `unattributed_overrun` (edge whole_block→unattributed_overrun), one `terminal_refusals` entry per item, `elapsed_s` absent (JSON `null`). The (W) sentence 'If it holds none, every uncompleted or not-started block becomes … unattributed_overrun' applies to a whole-block retry only in its `not_started` case.» [Q5]
- A split: the `whole_block` block is `superseded`, and its singles are placed per FT-3 with the INV-36 attempt rule.
- Form: (a).

**INV-33/43 single outcomes** (ruled). «A completed single with `elapsed_s ≤ worst` → decision `keep`, `late: false`. A completed single with `elapsed_s > worst` → decision `advance` exactly as an uncompleted culprit: its stage advances (`single_problem`→`single_retry`, or `single_retry`→`ceiling_violation`), its completed attempt is listed in the roster's voided attempts and its window `(block_id, attempt)` is excluded by `reduce` by rule, the event is a culprit event for its envelope-mates, and it consumes one of the item's two culprit events. A terminal attempt's window follows 45/10 F3 (recorded as `gross_j` on the refusal, never in a cell sum).» [Q6]; «The completed culprit single's `block_id` moves from the reporting envelope's `blocks` to its `voided_block_ids`; the voided window key is (`block_id`, that placement's `attempt`); `reduce` counts a window only when its `(block_id, attempt)` is a live placement.» [FT-11]
- Form: (a).

**INV-35 culprit linkage and limits** (ruled). «INV-35(a): every `reschedule` decision, at any stage, sits in an event whose observations contain a culprit; the seal refuses (`reschedule_without_culprit`) otherwise.» [FT-1]; «Each parent has at most one culprit observation at the `initial` stage and each single item at most two culprit observations across all events; the seal refuses (`culprit_limit`) a roster violating either. Within one event the count of `reschedule` decisions is at most the number of blocks in the reporting envelope minus one; the total over a roster is therefore finite. No numeric cap on total reschedules applies; factor 2 is not a ruled constant and 02b §5's row for it is deleted.» [FT-2]
- Pred: (a), (b) as quoted. (c) per event, `reschedule` decisions ≤ `len(pre-call blocks) − 1`. Whether (c) has a refusal code is RD-10.
- Form: (a); `reschedule_without_culprit`, `culprit_limit`.

**INV-36 stage legality and attempts** (ruled).
- Stage legality: «stage legality (each block's `retry_stage` history follows the closed edge list in (G))» [45/21 §7(S)], with the list amended by FT-1.
- Attempts: «`attempt` is 0 at the initial placement and rises by exactly 1 per placement of that block; a terminal `ceiling_violation` or `unattributed_overrun` decision creates no placement and does not increment. A single's first placement has `attempt = parent's latest attempt + 1`; all singles of one parent share that value (= 2 when the parent was never rescheduled, `c:scored_packer.py:333`). Window key = `(block_id, attempt)`.» [Q11]
- Pred: each non-`keep` decision maps to one of the eleven edges from the block's stage at that event. `retry_stage ∈ RETRY_STAGES`. A root roster holds only `initial` placements with attempt 0. Attempts follow Q11.
- Form: (a).

**INV-37 typed terminals** (ruled). «The single-problem stage is terminal: one single-problem retry, then the item is flagged `ceiling_violation`, a typed refusal for that item, recorded and never silently dropped (Opus S5).» [08 F2(c)]
- Pred: `type ∈ {"ceiling_violation","unattributed_overrun"}`, one entry per item, `(model, item_id)` unique, and `(block_id, attempt)` names a voided placement of a block containing the item (R[13] OP-25).
- Form: (a).

### I. Replay, seal and constants

**INV-38 event log** (ruled). «The roster carries an append-only `events` list, one entry per `requeue_overrun` call (block id, observations, resulting `sha256`).» [45/21 §7(R)]
- Pred:
  - `events[-1].sha256 == r.sha256`;
  - a root has `registered_sha256 == sha256`;
  - on a transition, `after.events[:-1] == before.events` with exactly one event appended, and `registered_sha256` is unchanged.
- The meaning of the event's "block id" is RD-1.
- Form: (a).

**INV-39 replay at `reduce`; `verify_executed_roster`** (ruled). «`requeue_overrun(registration, roster, envelope_index, observations)` takes observations carrying only `block_id`, `status`, `elapsed_s`; it derives every `decision` and placement. Replay: `reduce` recomputes `root = pack(registration, predicted_decode_s)`, asserts `root["sha256"] == registered_sha256`, then for each `k` calls `requeue_overrun(registration, roster_{k−1}, events[k].envelope_index, events[k].observations without decision)` and asserts that the re-derived decisions and placements equal the recorded ones and that the returned roster's `sha256` equals `events[k].sha256`; finally it asserts the replayed roster equals its input roster field for field. `_seal` remains the sole caller of `_digest`; replay compares digests it never computes.» [FT-8]; «A291 ships `verify_executed_roster(registration, roster, predicted_decode_s)` = `_seal` on the input, the `registered_sha256` re-pack assertion, and event replay with per-event digest equality (Q20). A291's `reduce`-column witnesses run against it and are recorded PROVISIONAL. A292's `reduce` calls it as its first statement (AST-asserted); A292's gate re-runs every A291 `reduce`-column witness at the real entry as mandatory rows. A291 may not describe the `reduce` column as closed.» [Q16]
- The checker cannot evaluate replay (no `pack` import). It is covered by the seal and `verify_executed_roster`.
- Form: (a).

**INV-40 seal placement** (ruled). «`_seal(registration, roster)` runs on the input at the entry of `requeue_overrun` and `reduce` and at every public exit of `pack` and `requeue_overrun`.» [45/21 §7(S)]
- Witness per path: deleting that path's seal call lets an injected violation through. An AST test checks the "sole caller of `_digest`" clause (FT-8).

**INV-44 constant sweep** (ruled). «Constants are patched at their module attribute; a scan finds no literal duplicate.» [45/21 §7(G)]; «CARRIED additions: `merge_order`, `min_correct`, `holm_m` → A293 (estimator; the lane 45/10 §Q2 calls 'A281b estimator'); `cap_bound_fraction` → A292 (reducer, the M3 cap-bound label). Each is a module constant pinned by `schema` and asserted equal to the AP-5M value by one A291 test; each is a mandatory CONSUMED row in its consumer lane's gate.» [Q1]
- Pred: each §4 constant equals its AP-5M value and is patched at its module attribute, and a scan finds no literal duplicate.
- Form: (a).

---

## 2. Data contract

### 2.1 Registration mapping

Every key and type is as in 02b §2.1, with these ruled changes:
- `item_ids_by_level`: the key set is exactly `{"1","2","3","4","5"}`, each list the same length `n` (Q2, Q3).
- `cap_tokens`, `block_size`: key set `{arm}`. `s_per_token_upper`, `prefill_s`, `ceiling_s`: the inner key set is `{arm}` (Q17).

Ruled registration refusal codes: `item_ids_by_level_keys`, `unequal_level_sizes`, `unselected_arm_entry`.

### 2.2 `predicted_decode_s`

As in 02b: `{model_id: {item_id: number}}`, exact.

### 2.3 Roster top level (exact key set)

| Key | Type | Source |
|---|---|---|
| `schema` | `"joulewise.scored_roster.v3"` | R[13] |
| `registration_sha256` | sha256 hex | 45/10 §Q2(1) |
| `claim_ready` | bool | 21/10 D4 |
| `item_set_sha256` | sha256 hex (flat preimage) | 45/10 §Q3 |
| `n_per_level` | int | Q3 |
| `blocks` | list[Block] | |
| `envelopes` | list[Envelope] | |
| `placements` | list[Placement] | R[13] F06 (RD-3) |
| `terminal_refusals` | list[TerminalRefusal] | |
| `events` | list[Event] | 45/21 §7(R) |
| `drift_lever_slots` | `{"1".."5": number \| null}` (planned) | Q12, FT-7, FT-10 |
| `planned_spread_shortfall` | `{"{model_id}:{level}": bool}`, exactly ten keys | FT-7 |
| `registered_sha256` | sha256 hex | Q20 |
| `sha256` | sha256 hex | Q20 |

There is no `models` key (FT-6), and no `drift_exceeded` or `spread_exceeded` key: those are executed values (Q12, Q13; RD-6).

### 2.4 Block

As in 02b §2.4, with ids and slicing now ruled (Q4). Keys: `block_id`, `model`, `level`, `items`, `predicted_item_s`, `predicted_s`, `attempt` (Q11), `retry_stage`, `parent_block_id`, `superseded`, `late` (FT-1).

### 2.5 Envelope, Placement, Observation

- **Envelope** (as in 02b): `index`, `model`, `kind`, `blocks` (execution order; placements append, FT-3), `voided_block_ids` (FT-11), `observations` (null means not yet run, FT-13). Whether it carries `decision` is RD-11.
- **Placement** (R[13] F06): `block_id`, `attempt`, `stage`, `reserved_s`, `envelope_index`.
- **Observation, as input** (FT-8): `block_id`, `status`, `elapsed_s`.
- **Observation, as recorded:** the input keys plus `decision`. FT-8 replays «events[k].observations without decision». The vocabulary is RD-9.

### 2.6 Event and TerminalRefusal

- **Event:** `envelope_index` (Q10), `observations` (recorded form), `placements` (creation order, FT-3; its form is RD-2), `sha256` (Q20). The 45/21 (R) "block id" is RD-1.
- **TerminalRefusal:** as in 02b, with `attempt`, per R[13] OP-25.

### 2.7 Digest chain and replay

- `PRE(r)` and the root rule are as in 02b §2.7, confirmed by Q20.
- `event.sha256` equals the resulting roster's `sha256`.
- Replay follows FT-8 (INV-39). Q20's own replay amendment is superseded by FT-8.

---

## 3. Public API and checker interface

### A291 public functions

- `pack(registration, predicted_decode_s)`.
- `requeue_overrun(registration, roster, envelope_index, observations)` (FT-8).
- `verify_executed_roster(registration, roster, predicted_decode_s)` (Q16).

Every exit and entry is sealed (INV-40).

### Checker

Module `tests/support/scored_roster_checker.py`. It uses the stdlib only and imports nothing from `joulewise`. It carries its own `canon_sha`.

```python
def check_roster(registration, roster, predicted_decode_s) -> list[Violation]
def check_transition(registration, before, after, predicted_decode_s) -> list[Violation]
def check_executed(registration, roster, captured) -> dict   # signature: RD-6
```

- **`check_roster`** covers every row except the transition clauses of INV-18/38, INV-26, INV-39, INV-40, INV-44 and INV-45. It re-derives every decision (INV-30 to INV-36) and every placement target (INV-34) from the recorded observations, using the ruled order (FT-3).
- **`check_transition`** checks append-only events, envelope fixedness, and report order (INV-18, INV-38, INV-46).
- **Stress run:** seeded `pack` → gapless in-order reports of every loaded envelope with random legal observations (FT-13, FT-14, Q19, FT-12) → final `check_executed`. The expected result is zero violations.
- **`Violation`:** `(inv, where, detail)`. Whether it also carries the ruled refusal code is RD-12.

---

## 4. CARRIED list, obligations and constants

| Row | Kind | Consumer / rule | Source |
|---|---|---|---|
| `alpha`, `n_boot`, `seed`, `floor_j`, `anchor_j`, `declared_sensitivities`, `arm_to_family` | field | A293 | 45/10 §Q2 |
| `sizing_receipt_sha256` | field | scored-night arm gate | 45/10 §Q2 |
| `ceiling_s` | field | runner (kill timeout) | 45/10 §Q2; Q17 |
| `scorer_id` | field | A292, runner | 45/10 §Q2 |
| `envelope_s`, `offset_s`, `pitch_s` | field | runner lane | 45/21 §7(G) |
| `merge_order`, `min_correct` (3), `holm_m` (5) | constant | A293 | Q1 |
| `cap_bound_fraction` (0.20) | constant | A292 | Q1 |
| Runner sequencing | obligation, not a field | «Runner lane: envelope `r+1` does not start until `requeue_overrun` for `r` has returned and its roster is loaded; if it cannot, the runner reports `r+1` with every block `not_started`.» | FT-9 |

- **CONSUMED fields:** as in 02b §5, with `cap_tokens`, `block_size`, `s_per_token_upper` and `prefill_s` restricted to the selected arm (Q17).
- **CONSUMED constants:** `LEVELS`; `RETRY_STAGES` and the eleven-edge list; `MIN_PARENT_BLOCKS`, `MIN_ENVELOPES` (5).
- **Deleted:** the "factor 2" row (FT-2).
- «Every CARRIED row is a mandatory CONSUMED row in its consumer lane's gate.» [45/21 §7(G)]

## 5. Status of R11

«R11 is refuter text; B26 is a seat brief, outside the ruled precedence chain (charge §"What this gate rules"; charter §7: narrative is argument). It did not bind. It binds from this ruling forward through Q12's text.» [Q18]

Every citation of R11 or B26 G3 as authority is replaced by Q12 (INV-45; ruling 10 §2 M4).

## 6. Out of A291 scope (consumer lanes)

| Ruled item | Source | Lane |
|---|---|---|
| Item rows carry `retry_stage` (was INV-13) | 08 F2(b) | A292 |
| `reduce` calls `verify_executed_roster` first (AST); re-runs every A291 `R` witness | Q16 | A292 |
| Window counted only for a live `(block_id, attempt)`; terminal window as `gross_j` | FT-11; Q6; 45/10 F3 | A292 |
| `cap_bound_fraction` consumed | Q1 | A292 |
| NR(`drift_exceeded`); NE(`ceiling_violation`) > NR; both NR reasons recorded | Q12 | A293 |
| «A level any of whose cells holds an `unattributed_overrun` refusal is NR(`unattributed_overrun`) unless NE(`ceiling_violation`) applies to that level; NR reasons accumulate and every applicable reason is recorded.» | FT-5 | A293 |
| `merge_order`, `min_correct`, `holm_m` consumed | Q1 | A293 |
| Runner sequencing | FT-9 | runner lane |

## 7. Coverage map

| Ruled text | Installed in |
|---|---|
| Q1 | INV-44; §4 constants rows; §6 |
| Q2 | INV-09; §2.1 |
| Q3 | INV-04; INV-10; §2.1 |
| Q4 (i), (ii), (iv) | INV-10; INV-12; §2.4 |
| Q4 (iii) | superseded by FT-6 → INV-50 |
| Q5 | INV-32 |
| Q6 | INV-33/43; §6 (terminal window) |
| Q7 | superseded by FT-1 (edges → §0 paths; INV-30; INV-35(a); INV-36) |
| Q8 | INV-31 (sentences 1 and 3); sentence 2 superseded by FT-1 → INV-35(a) |
| Q9 | INV-34 (eligibility); last sentence superseded by FT-3 → INV-34 |
| Q10 | INV-18 |
| Q11 | INV-21; INV-36 |
| Q12 | INV-27 (name per FT-7); INV-28; INV-45; §6 (precedence) |
| Q13 | INV-25; INV-26; INV-49 |
| Q14 | INV-41 |
| Q15 | §0 witness rules |
| Q16 | INV-39; §3; §6 |
| Q17 | INV-06; §2.1; §4 |
| Q18 | §5 |
| Q19 | INV-29 |
| Q20 | INV-02; INV-38; §2.7 (its replay amendment superseded by FT-8 → INV-39) |
| FT-1 | §0 (culprit, paths); INV-30; INV-35(a); INV-36 |
| FT-2 | INV-35 (b), (c); §4 (factor 2 deleted) |
| FT-3 | INV-34; INV-22; §2.5; §2.6 |
| FT-4 | §0 witness rules; INV-25; INV-28 |
| FT-5 | §6 |
| FT-6 | INV-50; INV-03 |
| FT-7 | INV-27; INV-49; §2.3 |
| FT-8 | INV-29; INV-39; §2.5; §3 |
| FT-9 | §4 |
| FT-10 | INV-27; INV-45 |
| FT-11 | INV-33/43; INV-26; §6 |
| FT-12 | INV-48 |
| FT-13 | INV-46; INV-16 |
| FT-14 | INV-47 |

Coverage: all 20 ruling-10 questions and all 14 FT texts are installed or explicitly superseded.

## 8. Residual open details (not chosen; for the magistrate)

- **RD-1.** 45/21 (R) lists "block id" in each event, but FT-8's `requeue_overrun` takes no block id. Does an Event carry `block_id`, and if so, which one? (02b's unratified pick was the first id of the pre-call `blocks`.)
- **RD-2.** FT-3 says «the event's `placements` list is in creation order». Is it a list of indices into roster `placements`, or of embedded Placement records?
- **RD-3.** Does the roster keep a top-level `placements` list (13 F06) in addition to each event's list? If so, are pack-time placements in it, and in what order?
- **RD-4.** What is a parent's PLANNED position after a requeue, used for `drift_lever_slots` at `requeue_overrun` exits? Is it 02b's item-weighted mean over live placements of non-terminal items, or something else?
- **RD-5.** FT-7/FT-10 use "non-terminal parents". Is that a parent none of whose items is terminal, or one with at least one non-terminal item? Which envelopes does a parent "occupy": the live placements of it and its singles, or voided ones too?
- **RD-6.** Where are the executed values (`spread_exceeded`, executed lever, `drift_exceeded`) returned: `verify_executed_roster`, `reduce`'s output, or a checker function? Where do "the captured window keys" come from? `verify_executed_roster(registration, roster, predicted_decode_s)` takes no windows.
- **RD-7.** FT-13's `unreported_envelope`: is it enforced inside `verify_executed_roster` (A291) or by `reduce` itself (A292)?
- **RD-8.** Does a `requeue_overrun` call whose decisions are all `keep` (a clean report, now required by FT-13) need witness cells? It is not one of the thirteen paths.
- **RD-9.** Is the decision vocabulary exactly `{keep, advance, split, reschedule, unattributed_overrun}`? Q6 names `advance` for single_retry→ceiling_violation; 02b also had a `ceiling_violation` decision.
- **RD-10.** What are the typed refusal codes for rules the rulings name no code for? Those rules are M8, capacity, homogeneity, conservation, stage legality, eligibility, replay mismatches and the rest. Is FT-2's per-event count (INV-35(c)) a seal refusal, and with what code?
- **RD-11.** Does `envelope.observations` carry `decision`, or only the input keys?
- **RD-12.** Does the checker's `Violation` also carry the ruled refusal code?
- **RD-13.** Model ids containing `:` make block ids and `planned_spread_shortfall` keys ambiguous. Should the registration refuse them?
- **RD-14.** What `retry_stage` does a block ending in `unattributed_overrun` carry? It is not a stage. The candidate is its last stage, unchanged.
