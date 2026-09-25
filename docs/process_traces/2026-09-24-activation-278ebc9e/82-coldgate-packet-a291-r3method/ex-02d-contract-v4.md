# 02d — A291 (HEADLINE-PACKER-RECUT-01): contract v4, self-contained

Installed 2026-09-24 by the contract-drafting seat (Opus 5.5) for the magistrate of activation a65fb4fa.

This file replaces 02c and is SELF-CONTAINED: an independent checker must be implementable from this file alone, and no key set, type, constant or schema is delegated to 02b, 02c, the AP-5M text or code. It installs:
- ruling 10;
- the addendum's final texts FT-1..FT-14;
- record 25 as amended by record 29;
- record 29's findings F2, F3, F6, F7 and F8.

Where the texts left me a choice, I have marked it in §10. None is made silently.

---

## 0. Conventions

### 0.1 Precedence

When texts conflict, the earlier item in this list wins:
1. the addendum's §3 final texts FT-n;
2. ruling-10 texts the addendum did not amend;
3. 45/21 §7;
4. 45/10;
5. 21/10;
6. 08.

Records 25 and 29 are the magistrate's representation rulings. They bind only where they fix a wire format, a name or the location of a check. Record 29 prevails over 25.

### 0.2 Sources

`«…»` marks a verbatim quote. `c:<file>:<line>` cites commit `c0998fdb`, cited only as the origin of a carried-over definition; the checker seat never reads that code. All paths are relative to `docs/process_traces/`.

| Key | File |
|---|---|
| [FT-n] | `2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md` §3 |
| [Qn] | `2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md` §1 |
| [RD-n] | `2026-09-24-activation-a65fb4fa/25-a291-residual-details-rulings.md` |
| [29 Fn] | `2026-09-24-activation-a65fb4fa/29-a291-v3-installation-rulings.md` |
| [13] | `2026-09-24-activation-a65fb4fa/13-a291-contract-synthesis-and-rulings.md` |
| [45/21] | `2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md` |
| [45/10] | `…/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md` |
| [21/10] | `…/21-coldgate-packet-a281/10-coldgate-fable-ruling.md` |
| [08] | `2026-09-23-activation-d8cc9c0a/08-a281-round1-synthesis-and-rulings.md` |
| [19] | `2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md` |

### 0.3 JSON value types used below

- **int:** a JSON integer, never a bool.
- **number:** a finite int or float, never a bool, never NaN or ±Inf.
- **str:** a JSON string; "non-empty str" excludes `""`.
- **hex64:** a str of exactly 64 characters from `0123456789abcdef` (c:scored_registration.py:54-57).
- **null:** JSON `null`.
- **Lists** keep their order; order is significant wherever §3 fixes it.

### 0.4 Glossary

- **Parent.** A block created by `pack`; its `parent_block_id` is null.
- **Single.** A one-item block created by a split. Its `parent_block_id` is its parent's id.
- **Cell.** A pair (model id, level).
- **Placement.** One scheduling of one block attempt into one envelope (§2.6).
- **Live placement.** A placement is live when its `block_id` is in its envelope's `blocks` list. **Voided** means the id is in that envelope's `voided_block_ids` list.
- **Terminal item.** An item with a `terminal_refusals` entry. A **terminal block** is one all of whose items are terminal.
- **Non-terminal parent.** «A "non-terminal parent" is a parent none of whose items has a terminal refusal. A parent "occupies" the envelopes of its and its singles' LIVE placements only; voided placements do not count.» [RD-5]
- **Reported envelope.** An envelope whose `observations` is not null. **Root roster:** «A root roster is one with `events == []`.» [FT-4]

---

## 1. Constants and derived quantities

### 1.1 Module constants

«Constants: levels, merge_order, min_correct 3, holm_m 5, both spread minima 5, cap_bound_fraction 0.20, retry_stages» [45/10 §Q3], «Module constants pinned by `schema`; one test asserts equality to the AP-5M text.» [45/10 §Q3]

| Constant | Value | A291 status | Value source |
|---|---|---|---|
| `LEVELS` | `[1, 2, 3, 4, 5]` | CONSUMED | c:scored_registration.py:111; 45/10 §Q3 |
| `RETRY_STAGES` | `["initial", "whole_block", "single_problem", "single_retry", "ceiling_violation"]` | CONSUMED | c:scored_registration.py:26 |
| `EDGES` | the eleven edges of §1.3 | CONSUMED | FT-1 |
| `MIN_PARENT_BLOCKS` | `5` | CONSUMED | 45/10 §Q3 ("both spread minima 5") |
| `MIN_ENVELOPES` | `5` | CONSUMED | same |
| `MERGE_ORDER` | `[[5, 4], [4, 3], [1, 2], [2, 3]]` | CARRIED → A293 | c:scored_registration.py:27. AP-5M draft wording: «5 into 4 ("4–5"), then into 3; 1 into 2 ("1–2"), then into 3» (see §10 X-8) |
| `MIN_CORRECT` | `3` | CARRIED → A293 | 45/10 §Q3 |
| `HOLM_M` | `5` | CARRIED → A293 | 45/10 §Q3 |
| `CAP_BOUND_FRACTION` | `0.20` | CARRIED → A292 | 45/10 §Q3 |
| `REGISTRATION_SCHEMA` | `"joulewise.scored_registration.v2"` | CONSUMED (identity) | 13 (OP-33) |
| `ROSTER_SCHEMA` | `"joulewise.scored_roster.v3"` | recorded constant | 13 (OP-33) |

There is no factor-2 constant: «factor 2 is not a ruled constant and 02b §5's row for it is deleted.» [FT-2]

### 1.2 Derived quantities (let `g` be the registration mapping and `a = g["arm"]`)

- `cap := g["interior_s"] − g["guard_s"]`. This is the capacity (c:scored_registration.py:129).
- `worst(m) := g["cap_tokens"][a] * g["s_per_token_upper"][m][a] + g["prefill_s"][m][a]`. The derived worst case per item, evaluated in exactly this operation order (c:scored_registration.py:157).
- `n := len(g["item_ids_by_level"]["1"])`. «Every level's item list has the same length `n`; `n_per_level := n`; unequal lengths are refused (`unequal_level_sizes`).» [Q3]
- `bpc := ceil(n / g["block_size"][a])`. «Blocks per cell := `ceil(n / block_size[arm])`.» [Q3]
- `max_gap := g["budget_j"] / (g["delta_upper_j_per_block_slot"] * bpc)` (c:scored_registration.py:170; 45/10 §Q3 «Formula at `scored_registration.py:169-170` becomes the definition; the field is removed.»). It is undefined when either input is null.
- `canon(v) := json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")` and `canon_sha(v) := hashlib.sha256(canon(v)).hexdigest()` (c:scored_registration.py:96, 179; c:scored_packer.py:27-32). `ensure_ascii` keeps Python's default (`True`). Numbers are hashed exactly as accepted, with no coercion (13, OP-07).
- `Bound(b)`: «Bound(b) := `predicted_s` when the block's stage is `initial` or `whole_block`, else the item's derived worst case.» [addendum §3]
- **Culprit:** «An observation is a culprit iff its `elapsed_s` is a number and `elapsed_s > Bound(block)`, at any stage; `not_started` is never a culprit.» [FT-1]

### 1.3 Edges and the thirteen closed paths

«Closed edge list: the nine edges of (G) plus `single_problem→unattributed_overrun` and `single_retry→unattributed_overrun` (eleven edges, thirteen paths).» [FT-1]

| Path | Meaning |
|---|---|
| `P` | `pack` |
| `E1` | initial→whole_block |
| `E2` | initial→reschedule |
| `E3` | initial→unattributed_overrun |
| `E4` | whole_block→single_problem |
| `E5` | whole_block→unattributed_overrun |
| `E6` | single_problem→single_retry |
| `E7` | single_problem→reschedule |
| `E8` | single_retry→ceiling_violation |
| `E9` | single_retry→reschedule |
| `E10` | single_problem→unattributed_overrun |
| `E11` | single_retry→unattributed_overrun |
| `R` | `reduce` |

`E1`–`E11` are all `requeue_overrun`. A `reschedule` edge leaves the stage unchanged.

---

## 2. Data contract (exact key sets)

### 2.1 Registration mapping: 29 keys, exact

Missing or unknown keys are refused (c:scored_registration.py:92-93). The mapping must be canonical JSON: `canon(g)` succeeds (c:scored_registration.py:94-98).

| Key | Type / domain | Source |
|---|---|---|
| `schema` | str `== REGISTRATION_SCHEMA` | 13 OP-33 |
| `mode` | `"pilot"` \| `"registered"` | c:…:104 |
| `registration_id`, `plan_id`, `scorer_id` | non-empty str | c:…:99-100 |
| `arm` | non-empty str, a key of `arm_to_family` | c:…:133 |
| `arm_to_family` | non-empty object, non-empty str → non-empty str | c:…:132-137 |
| `role_to_model_id` | object with exactly the keys `"8B"` and `"1.7B"`; values non-empty str and distinct | c:…:138-143 |
| `sizing_receipt_sha256` | hex64, or null only when `mode == "pilot"` | c:…:106-110 |
| `predictions_sha256` | hex64, or null only when `mode == "pilot"` | 45/10 §Q3 |
| `alpha` | number, `0 < alpha ≤ 1` | c:…:123-125 |
| `n_boot` | int ≥ 1 | c:…:121 |
| `seed` | int ≥ 0 | c:…:121-122 |
| `floor_j`, `anchor_j` | number ≥ 0 | c:…:123 |
| `cap_tokens`, `block_size` | object with key set exactly `{arm}`; value int ≥ 1 | Q17; c:…:145-148 |
| `item_ids_by_level` | object with key set exactly `{"1","2","3","4","5"}`; each value a list of non-empty str; all ids distinct across all levels; all lists of equal length `n ≥ 1` | Q2; Q3; c:scored_packer.py:229-232 |
| `envelope_s`, `interior_s`, `pitch_s` | number > 0 | c:…:123-124 |
| `offset_s`, `guard_s` | number ≥ 0 | c:…:123-124 |
| `s_per_token_upper`, `ceiling_s` | object whose key set is the two model ids; each value an object with key set exactly `{arm}` and value number > 0 | Q17; c:…:149-154 |
| `prefill_s` | as above, value number ≥ 0 | Q17; c:…:149-154 |
| `delta_upper_j_per_block_slot` | number > 0, or null only when pilot | c:…:160-166 |
| `budget_j` | number ≥ 0, or null only when pilot | c:…:160-166 |
| `declared_sensitivities` | non-empty list of non-empty str | c:…:173-176 |

**Coherence:**
- `offset_s + interior_s ≤ envelope_s` (c:…:127-128).
- `pitch_s ≥ envelope_s` (c:…:130-131).
- For both models, `worst(m) ≤ ceiling_s[m][arm] ≤ cap` (Q17).

**Ruled registration refusal codes:** `item_ids_by_level_keys` (Q2), `unequal_level_sizes` (Q3), `unselected_arm_entry` (Q17). Other domain failures use `inv_51` (§5).

`registration_sha256 := canon_sha(g)`, taken over the whole mapping.

### 2.2 `predicted_decode_s` (the argument to `pack`, `verify_executed_roster` and `executed_status`)

- An object whose key set is exactly the two model ids.
- Each value is an object whose key set is exactly the registered item ids.
- Each value is a number `v` with `0 < v ≤ worst(m)`.

«`pack` refuses any item above its derived worst case (P4)»; «Extra predictions are refused, not ignored (Sol 34 (d)).» [45/10 §Q3]

### 2.3 Roster top level: 14 keys, exact

| Key | Type | Rule / source |
|---|---|---|
| `schema` | str `== ROSTER_SCHEMA` | 13 |
| `registration_sha256` | hex64 `== canon_sha(g)` | 45/10 §Q2 |
| `claim_ready` | bool | pilot ⇒ false (21/10 D4; INV-05) |
| `item_set_sha256` | hex64 `== canon_sha(FLAT)`, where `FLAT` = the ids of level "1" in list order, then "2", …, "5", as one flat list | 45/10 §Q3; 13 F02 |
| `n_per_level` | int `== n` | Q3 |
| `blocks` | list[Block] | §2.4; order: §10 X-1 |
| `envelopes` | list[Envelope], with `envelopes[i]["index"] == i` | §2.5; INV-17 |
| `placements` | list[Placement], append-only | RD-3 |
| `terminal_refusals` | list[TerminalRefusal] | §2.8; order: §10 X-1 |
| `events` | list[Event], append-only | §2.7 |
| `drift_lever_slots` | object with key set `{"1",…,"5"}`, value number or null | INV-27 |
| `planned_spread_shortfall` | object with exactly ten keys `"{model_id}:{level}"`, value bool | FT-7 |
| `registered_sha256` | hex64 | §2.9 |
| `sha256` | hex64 | §2.9 |

«The roster carries no `models` key.» [FT-6] There are no `drift_exceeded` or `spread_exceeded` keys: those are executed values (§4.2).

### 2.4 Block: 11 keys, exact

| Key | Type | Rule |
|---|---|---|
| `block_id` | str | Parent: `"{model_id}:{arm}:{level}:{k}"`. Single: `"{parent_id}:single:{j}"` (Q4(ii)) |
| `model` | str | one of the two model ids |
| `level` | int | in `LEVELS` |
| `items` | list[str] | Parent: the Q4(i) slice. Single: `[parent.items[j]]` |
| `predicted_item_s` | list[number] | aligned with `items`. Parent: `[p[model][i] for i in items]`. Single: see §10 X-3 |
| `predicted_s` | number | Parent: `sum(predicted_item_s)` in item order (c:scored_packer.py:239-240). Single: `worst(model)` (45/21 §7(T)) |
| `attempt` | int ≥ 0 | the `attempt` of the block's latest placement (Q11) |
| `retry_stage` | str in `RETRY_STAGES` | §3.3; RD-14 |
| `parent_block_id` | str \| null | null if and only if the block is a parent (08 F2(a)) |
| `superseded` | bool | true if and only if the block is a `whole_block` retry that was split (§3.3) |
| `late` | bool | «A block's `late` is true iff its latest observation is `completed` with `elapsed_s > Bound(block)`» [FT-1]. False when it has no observation |

### 2.5 Envelope: 6 keys, exact

| Key | Type | Rule |
|---|---|---|
| `index` | int | its list position (INV-17) |
| `model` | str | one of the two model ids |
| `kind` | `"loaded"` \| `"idle_slot"` | 08 F1 |
| `blocks` | list[str] | live block ids in execution order. «An envelope's `blocks` list is its execution order; every placement appends to it» [FT-3] |
| `voided_block_ids` | list[str] | voided ids; order per §10 X-1 |
| `observations` | list[RecordedObservation] \| null | null means not yet run (FT-13); recorded observations carry `decision` (RD-11) |

Consistency: `set(blocks) ∪ set(voided_block_ids)` equals the set of `block_id`s of the placements with this `envelope_index`, and the two lists are disjoint and free of duplicates.

### 2.6 Placement: 5 keys, exact (13 F06; RD-3)

`block_id` str, `attempt` int, `stage` in `{"initial","whole_block","single_problem","single_retry"}`, `reserved_s` number, `envelope_index` int.

- `(block_id, envelope_index)` is unique.
- «The roster keeps a top-level `placements` list, append-only, holding every placement ever made, pack-time included. Pack-time placements come first, ordered by envelope index ascending and then by position in that envelope's `blocks` list.» [RD-3]
- Event-made placements follow, in creation order.

### 2.7 Observation and Event

- **Input observation:** exactly `block_id`, `status`, `elapsed_s` (FT-8).
- **RecordedObservation:** exactly `block_id`, `status`, `elapsed_s`, `decision`.
  - `status ∈ {"completed","cut_off","not_started"}`.
  - `elapsed_s`: «`elapsed_s` for `completed` and `cut_off` is a finite JSON number > 0; `not_started` carries `elapsed_s: null`.» [Q19]
  - Decision vocabulary: «The decision vocabulary is exactly `{keep, advance, split, reschedule, unattributed_overrun}`. The edge `single_retry → ceiling_violation` is decision `advance`, and its terminal refusal has type `ceiling_violation`. No `ceiling_violation` decision exists.» [RD-9]
- **Event:** exactly `envelope_index` (int), `block_ids` (list[str]), `observations` (list[RecordedObservation]), `placements` (list[int]), `sha256` (hex64).
  - «An Event carries `envelope_index` (FT-8) and `block_ids`: the reporting envelope's `blocks` list in execution order at the call.» [RD-1]
  - «`Event.placements` is a list of integer indices into the roster's top-level `placements` list, in creation order. There are no embedded copies.» [RD-2]
  - `observations[i].block_id == block_ids[i]`.

### 2.8 TerminalRefusal: 7 keys, exact

| Key | Type | Rule |
|---|---|---|
| `type` | `"ceiling_violation"` \| `"unattributed_overrun"` | never a refusal code (29 F7) |
| `block_id` | str | |
| `attempt` | int | the attempt of that block's voided placement |
| `parent_block_id` | str \| null | |
| `item_id` | str | |
| `model` | str | |
| `level` | int | |

There is one entry per item (13 OP-25), and `(model, item_id)` is unique.

### 2.9 Digest chain

- `PRE(r)` is `r` with three things removed: the top-level `sha256`, the top-level `registered_sha256`, and each `events[k]["sha256"]`. Then `r["sha256"] := canon_sha(PRE(r))`. These are 13's rules, confirmed by Q20: «The preimage rule, `event.sha256` = resulting roster digest, root `registered_sha256 == sha256`, uniform re-pack assertion, `parent_sha256` dropped: confirmed» [Q20]
- Root: `registered_sha256 == sha256`.
- Every descendant carries the root's `sha256` as `registered_sha256`.
- `events[k]["sha256"]` equals the `sha256` of the roster that the k-th call returned.

---

## 3. Normative behaviour, assembled from the ruled texts

### 3.1 `pack(registration, predicted_decode_s)`

1. **Parents.** «(i) For each level, in registered item order, parents are the consecutive slices `items[k·b:(k+1)·b]`, `b = block_size[arm]`, `k = 0,1,…`. (ii) Parent id `"{model_id}:{arm}:{level}:{k}"`; single id `"{parent_id}:single:{j}"`, `j` the item's zero-based position in the parent.» [Q4] «When `n mod block_size[arm] ≠ 0` the last slice of each level is shorter and is a parent block in every count (M8, drift, spread).» [Q3]
   - Each model gets the same slices.
   - Each parent has `attempt 0`, `retry_stage "initial"`, `superseded false`, `late false` and `parent_block_id null`.
2. **Model order.** «(iii) The model order everywhere (iteration, idle assignment, tie-breaks) is by role, derived from `registration.role_to_model_id`: the `"8B"`-role model first, the `"1.7B"`-role model second, never the mapping's insertion order.» [FT-6]
3. **Initial reservation.** «An `initial` placement has `reserved_s = predicted_s = Σ predicted_item_s` and `Σ reserved_s ≤ capacity` per envelope.» [Q11]
4. **Arrangement.** The packer's search places parents into loaded envelopes and inserts idle slots, subject to INV-14, INV-17, INV-20, INV-24, INV-25 and INV-41. The search itself is the implementation's; the checker checks only its invariants.
   - «One `idle_slot` is inserted iff both models have an odd envelope count; it is assigned to the `"1.7B"`-role model (`c:scored_packer.py:66, 113` under Q4(iii) ordering). Balance is the search objective; the checkable rule is the recorded `drift_lever_slots[level]`, ≤ `max_gap` at `pack` in registered mode.» [Q14]
5. **Refusals.**
   - Minima (INV-25, INV-49).
   - «`pack` in registered mode refuses a planned lever > `max_gap` (21/10 D5b).» [Q12]
   - Predictions (INV-07, INV-08).
6. **Output.**
   - `events == []`; `registered_sha256 == sha256`.
   - Derived fields computed per §3.4.
   - `claim_ready` is false in pilot mode.

### 3.2 `requeue_overrun(registration, roster, envelope_index, observations)`

«`requeue_overrun(registration, roster, envelope_index, observations)` takes observations carrying only `block_id`, `status`, `elapsed_s`; it derives every `decision` and placement.» [FT-8]

**Preconditions (each is a typed refusal):**
- The input is sealed.
- «`requeue_overrun` refuses (`report_order`) unless the reporting index is the lowest `loaded` envelope with `observations is None`.» [FT-13]
- «Events carry strictly increasing `envelope_index`; `requeue_overrun` refuses (`report_order`) a reporting index ≤ the last event's.» [Q10]
- The observations list the reporting envelope's `blocks` exactly, in order (INV-29).
- `elapsed_s` is valid (Q19).
- Order: «Within one event the observations, in the envelope's `blocks` order, consist of zero or more `completed`, then at most one `cut_off`, then only `not_started`; the seal refuses (`invalid_observation_order`) otherwise.» [FT-14]
- Physics guard: «The seal refuses (`invalid_elapsed`) an event whose Σ `elapsed_s` over its observations exceeds `interior_s`.» [FT-12]

**Decisions.**

«In one `requeue_overrun` call: a culprit `completed` at the `initial` or `whole_block` stage keeps its window with decision `keep`; a culprit single, completed or not, advances (`single_problem`→`single_retry`, `single_retry`→`ceiling_violation`); an uncompleted culprit parent advances (`initial`→`whole_block`); a `whole_block` `cut_off` splits. Every other uncompleted or `not_started` block, at any stage, is rescheduled without advancing iff the event's observations contain at least one culprit at any stage; if they contain none, each such block becomes the typed terminal state `unattributed_overrun`, one `terminal_refusals` entry per item, and the call never raises.» [FT-1]

«For a `whole_block` placement (always alone): `completed` → decision `keep`; `late := elapsed_s > predicted_s`; a late completion is a culprit with no mates. `cut_off` at any `elapsed_s > 0` → decision `split` (edge whole_block→single_problem); `elapsed_s` is recorded. `not_started` → decision `unattributed_overrun` (edge whole_block→unattributed_overrun), one `terminal_refusals` entry per item, `elapsed_s` absent (JSON `null`).» [Q5]

«A completed single with `elapsed_s ≤ worst` → decision `keep`, `late: false`. A completed single with `elapsed_s > worst` → decision `advance` exactly as an uncompleted culprit» [Q6]

These texts combine into one table. Here `s` is the block's `retry_stage` before the call, and `anyc` means "the event holds at least one culprit".

| status | s | culprit? | decision |
|---|---|---|---|
| completed | initial / whole_block | any | `keep` |
| completed | single_problem / single_retry | no | `keep` |
| completed | single_problem / single_retry | yes | `advance` |
| cut_off / not_started | initial | yes | `advance` |
| cut_off | whole_block | — | `split` |
| not_started | whole_block | — | `unattributed_overrun` |
| cut_off / not_started | single_problem / single_retry | yes | `advance` |
| cut_off / not_started | any, not culprit, not whole_block | no | `reschedule` if `anyc`, else `unattributed_overrun` |

**Effects.** Each block is processed in the order of `block_ids` (FT-3). Every decision except `keep` moves the id from the reporting envelope's `blocks` to its `voided_block_ids`.

| Decision (edge) | Effect |
|---|---|
| `keep` | The block stays live. `late` per FT-1. |
| `advance`, initial→whole_block | The stage becomes `whole_block`. The block gets a new placement in a NEW envelope appended at `len(envelopes)`, with `attempt + 1` and `reserved_s = min(Σ over items of worst(model), cap)` (45/21 §7(W): «`reserved_s = min(Σ item derived worst cases, capacity)`; `predicted_s` is unchanged»). |
| `advance`, single_problem→single_retry | The stage becomes `single_retry`. The block gets a placement at the lowest eligible index (§3.5), else a new envelope, with `attempt + 1` and `reserved_s = worst(model)`. |
| `advance`, single_retry→ceiling_violation | The stage becomes `ceiling_violation`. There is no placement and no increment (Q11). One `terminal_refusals` entry of type `ceiling_violation`. |
| `reschedule` | The stage is unchanged. The block gets a placement at the lowest eligible index, else a new envelope, with `attempt + 1` and the previous `reserved_s` (Q11). |
| `split` | `superseded := true`; the stage stays `whole_block` (§10 X-2). For each `j` ascending, the single `"{id}:single:{j}"` is appended to `blocks`, with `items [items[j]]`, `predicted_s = reserved_s = worst(model)`, `retry_stage single_problem`, `late false`, `superseded false`, and `attempt = parent's latest attempt + 1` (Q11). It is placed at the lowest eligible index, else in a new envelope. |
| `unattributed_overrun` | The stage is unchanged (RD-14). No placement. One `terminal_refusals` entry per item. |

Supporting texts:
- «The completed culprit single's `block_id` moves from the reporting envelope's `blocks` to its `voided_block_ids`; the voided window key is (`block_id`, that placement's `attempt`); `reduce` counts a window only when its `(block_id, attempt)` is a live placement.» [FT-11]
- «Reschedules, the singles created by a split, and advancing singles each take the lowest eligible index under Q9, else a new envelope appended at index `len(envelopes)`; a `whole_block` advance always takes a new envelope. Within one event, placements are made in the order of the reporting envelope's pre-call `blocks` list, and a split's singles in ascending `j`; each placement updates eligibility for the next.» [FT-3]
- A new envelope is `{index: len(envelopes), model: block.model, kind: "loaded", blocks: [], voided_block_ids: [], observations: null}`.

**Finish.**
1. Set `envelopes[envelope_index].observations` to the recorded observations.
2. Recompute the §3.4 derived fields.
3. Append `{envelope_index, block_ids, observations (recorded), placements, sha256}`.
4. Keep `registered_sha256` unchanged.
5. Seal.

«`requeue_overrun` recomputes and records» the planned lever «and never refuses on it» (Q12; read with FT-7's «Ruling 10 Q12 reads `drift_lever_slots[level]` (the PLANNED lever, 02b §2.3) wherever it wrote `planned_drift_lever_slots`.»).

### 3.3 Stage and attempt bookkeeping

«`attempt` is 0 at the initial placement and rises by exactly 1 per placement of that block; a terminal `ceiling_violation` or `unattributed_overrun` decision creates no placement and does not increment. A single's first placement has `attempt = parent's latest attempt + 1`; all singles of one parent share that value (= 2 when the parent was never rescheduled, `c:scored_packer.py:333`). Window key = `(block_id, attempt)`.» [Q11]

«A block that ends in `unattributed_overrun` keeps its last `retry_stage` unchanged. Its terminal state is represented only by its items' `terminal_refusals` entries. Stage legality treats a terminal refusal as the end of the block's history.» [RD-14]

### 3.4 Derived roster fields, recomputed at every `pack` and `requeue_overrun` exit

**`drift_lever_slots[level]`, the planned lever.**
- «The PLANNED position of a parent at a `requeue_overrun` exit is the item-weighted mean of the envelope indices of the live (not voided, not terminal) placements holding its items, as 02b proposed. A parent with no live placement has no planned position and is excluded.» [RD-4]
- At `pack`: «At pack time every item of a parent sits in one envelope, so its position is that envelope's index.» [45/10 §Q4]
- The lever is `|mean over 8B-role parents − mean over 1.7B-role parents|` of the planned positions. The summation order is §10 X-4.
- «When a model has zero non-terminal parents at a level, `drift_lever_slots[level]` is `null` and no drift refusal or record applies.» [FT-10]

**`planned_spread_shortfall`.** «`planned_spread_shortfall` is a derived roster key (02b §2.3 gains the row): an object whose key set is exactly the ten cells `"{model_id}:{level}"` with `level` a decimal string `"1"`…`"5"`, every value a bool, never absent; true iff that cell's non-terminal parents number fewer than five or occupy fewer than five distinct envelopes. It is recomputed at every `pack` and `requeue_overrun` exit; `_seal` asserts at every run that the stored object equals the recomputation (`stale_derived`); `pack` refuses (`spread_minima`) when any value would be true.» [FT-7]

### 3.5 Eligibility

«Eligibility of an existing envelope `e` for a placement made by the event reporting envelope `r`: `e.index > r.index` and `e.index > max reported index` (Q10); `e.observations is None`; `e.kind == "loaded"`; `e` holds no `whole_block` placement; `e.model == block.model`; after placement M8-by-parent (no two parents of one cell in `e`) and `Σ reserved_s ≤ capacity` (live and voided placements) hold.» [Q9]

«An innocent initial-stage block is rescheduled with its previous `reserved_s` into the first eligible envelope under Q9, else a fresh one.» [Q8] «(X)'s 'a rescheduled parent the seal cannot place' is retained but unreachable (a fresh envelope always exists).» [Q8]

### 3.6 A291 public entry points after capture

- «A291 ships `verify_executed_roster(registration, roster, predicted_decode_s)` = `_seal` on the input, the `registered_sha256` re-pack assertion, and event replay with per-event digest equality (Q20). A291's `reduce`-column witnesses run against it and are recorded PROVISIONAL. A292's `reduce` calls it as its first statement (AST-asserted); A292's gate re-runs every A291 `reduce`-column witness at the real entry as mandatory rows. A291 may not describe the `reduce` column as closed.» [Q16]
- Replay: «Replay: `reduce` recomputes `root = pack(registration, predicted_decode_s)`, asserts `root["sha256"] == registered_sha256`, then for each `k` calls `requeue_overrun(registration, roster_{k−1}, events[k].envelope_index, events[k].observations without decision)` and asserts that the re-derived decisions and placements equal the recorded ones and that the returned roster's `sha256` equals `events[k].sha256`; finally it asserts the replayed roster equals its input roster field for field. `_seal` remains the sole caller of `_digest`; replay compares digests it never computes.» [FT-8]
- «FT-13's `unreported_envelope` is enforced inside `verify_executed_roster` (A291), because it is a property of the roster.» [RD-7] «`reduce` refuses (`unreported_envelope`) a roster with any `loaded` envelope whose `observations is None`.» [FT-13]
- `verify_executed_roster` returns `None` or raises (RD-6).
- `executed_status(registration, roster, predicted_decode_s, captured_window_keys)` «passes `predicted_decode_s` unchanged to `verify_executed_roster` as its first statement.» [29 F2] It then returns the executed values of §4.2. `captured_window_keys` is «the set of `(block_id, attempt)` keys the reducer has windows for; A292 supplies it. Its witnesses carry the same PROVISIONAL status as the reduce column (Q16).» [RD-6]

---

## 4. Executed values (computed after capture, never stored in the roster)

### 4.1 Counting

- A window counts only when «its `(block_id, attempt)` is a live placement» [FT-11] and it is in `captured_window_keys`.
- A **counted parent** is a parent every item of which has a counted window. For a split parent, each item's counted window belongs to its single.
- Spread: «A cell is spread-exceeded when its executed roster holds fewer than five parent blocks whose every item has a counted window, or fewer than five distinct envelopes holding them,» [45/10 §Q4] «`spread_exceeded` is decided once, at `reduce` entry, from the finished roster and the set of captured window keys.» [Q13]
- Executed position: «A parent's position is the item-weighted mean of the envelope indices of its executed windows: each item contributes the index of the envelope in which its counted attempt was captured. Voided attempts and idle slots contribute nothing.» [45/10 §Q4]
- Drift: «At `reduce` entry the executed lever is computed from counted windows (45/10 §Q4 position rule); if it exceeds `max_gap` the level carries `drift_exceeded: true`, its numbers are reported, and A293 reports it NR(`drift_exceeded`) until a registered recapture.» [Q12] «When a model has zero counted parents at a level, the executed lever for that level is `null` and `drift_exceeded` is not set; that cell is `spread_exceeded` (0 < 5) under (X).» [FT-10]

### 4.2 Return shape of `executed_status` and of the checker's `check_executed`

The shape is proposed in §10 X-5; it is not ruled:
- `{"spread_exceeded": {cell: bool} (ten keys as FT-7), "executed_drift_lever_slots": {"1".."5": number | null}, "drift_exceeded": {"1".."5": bool}}`;
- `drift_exceeded` is `false` when the lever is null;
- in pilot mode, `max_gap` may be undefined; then every `drift_exceeded` is false.

---

## 5. Invariant matrix, with codes

### 5.1 Witness rules (gating)

- «No invariant row/path cell may be `n/a`. Where no natural witness exists, use entry injection (a violating roster fed to the path) or exit injection (an internal step patched to emit the violation). Any residual `n/a` is a cold-gate exception, not a lens review.» [Q15]
- «For every (row, path) cell the witness form follows the row's ruled consequence on that path: (a) refusal: a violating input on that path is refused with the typed refusal; (b) recorded value: a violating input on that path reaches the exit and the recorded value equals the ruled value (e.g. `planned_spread_shortfall[cell] == true`, `drift_lever_slots[level] > max_gap`), and a mutant that suppresses or alters the record is killed; (c) root-only refusal (the five-parent/five-envelope minima): on `pack` form (a); on every `requeue_overrun` path form (b), the shortfall introduced by the event or by entry injection of a non-root roster in shortfall; at `reduce` the (b) form against `verify_executed_roster` (PROVISIONAL per Q16). The seal refuses the minima (`spread_minima`) only when `events == []`, at whichever entry or exit it runs. No cell is `n/a`.» [FT-4]
- The gate matrix is exactly the 13 paths of §1.3.

**Additional non-gating test set.** «The all-`keep` `requeue_overrun` call gets an ADDITIONAL, NON-GATING test set; the (G) matrix stays exactly thirteen paths (FT-1, FT-4).» [29 F4] Every checker-evaluable row gets one violating roster reached through an all-`keep` report.

### 5.2 Codes and `Violation`

- «There is one exact `Violation` field set: `Violation(inv_id: str, code: str, detail: str)`.» [29 F7]
- `inv_id` is the row id exactly as headed below, for example `"INV-35"` or `"INV-33/43"`.
- Codes: a ruled code where a ruling names one; otherwise the row id in lower case (RD-10), for example `inv_17`. Lettered sub-rules and the composite row use the forms F7 lists.
- «`unattributed_overrun` appears there only as a terminal-refusal TYPE: it is never a refusal code, and the FT-1 no-culprit outcome never raises.» [29 F7]
- The seal's typed refusals use the same codes.

### 5.3 Rows

Column **F** is the witness form: (a) refusal, (b) recorded value, (c) root-only refusal. **Chk** says whether the checker can evaluate the row: "yes", or NC (not checker-evaluable, with the reason in §6).

#### A. Identity and digests

**INV-01 registration binding** (F: a; Chk: yes; code `inv_01`)
- Ruled text: «Identity fields (`schema`, `registration_id`, `plan_id`) are CONSUMED: their witness is that a roster sealed under the old digest is refused by every consumer under the new registration.» [45/10 §Q2]
- Predicate: `r.registration_sha256 == canon_sha(g)`.

**INV-02 roster self-digest** (F: a; Chk: yes; code `inv_02`)
- Predicate: `r.sha256 == canon_sha(PRE(r))` (§2.9).

**INV-03 exact roster key sets; no copies** (F: a; Chk: yes; code `inv_03`)
- Ruled text: «no roster copies of registered values» [45/21 §7(S)]; «The roster carries no `models` key.» [FT-6]
- Predicate: every roster record has exactly its §2 key set.

**INV-04 derived identity fields; equal level sizes** (F: a; Chk: yes; codes `unequal_level_sizes`, `inv_04`)
- Ruled text: «`item_set_sha256 := canonical_json_sha256([ids in level order])` is a derived roster field.» [45/10 §Q3]
- Predicate: `item_set_sha256` and `n_per_level` equal their §2.3 derivations, and the lists are of equal length (Q3).

**INV-05 claim readiness** (F: a; Chk: yes; code `inv_05`)
- Ruled text: «`mode = pilot` objects may emit only rosters flagged `claim_ready: false`; every consumer refuses a non-claim-ready roster outside pilot mode.» [21/10 §Q2 D4]
- Predicate, two clauses (13 F03):
  - pilot implies `claim_ready == false`;
  - at the `requeue_overrun` and `reduce` entry, non-pilot mode with `claim_ready == false` is refused.

#### B. Registration and predictions

**INV-06 selected arm; coherence** (F: a; Chk: yes; codes `unselected_arm_entry`, `inv_06`)
- Ruled text: «`cap_tokens` and `block_size` have key set `{arm}`; `s_per_token_upper`, `prefill_s`, `ceiling_s` have inner key set `{arm}` for each model. Any other key is refused (`unselected_arm_entry`). The coherence inequality `worst ≤ ceiling_s ≤ interior_s − guard_s` is checked on the selected arm; `ceiling_s` stays CARRIED (runner).» [Q17]

**INV-07 prediction domain** (F: a; Chk: yes; code `inv_07`)
- Predicate: §2.2. The same bound holds on every parent's `predicted_item_s`.

**INV-08 prediction digest** (F: a; Chk: yes; code `inv_08`)
- Ruled text: «Add registration field `predictions_sha256` (pilot-nullable, required in registered mode)»; «refuses when `canonical_json_sha256(predicted_decode_s restricted to the registered items)` ≠ `predictions_sha256`» [45/10 §Q3]
- Predicate: when the field is not null, `canon_sha(PRED(r)) == g.predictions_sha256`. `PRED(r) = {parent.model: {item: v}}` is built from each parent's `items` and `predicted_item_s` (13 OP-08). At `pack`, the digest is computed on `p`.

**INV-51 registration domain** (F: a; Chk: yes; code `inv_51`; row id assigned by the seat, §10 X-6)
- Predicate: §2.1 key set, types and coherence, other than the clauses owned by INV-04, INV-06 and INV-09.

#### C. Items, blocks, parents

**INV-09 level keys and item identity** (F: a; Chk: yes; codes `item_ids_by_level_keys`, `inv_09`)
- Ruled text: «`item_ids_by_level` is a mapping whose key set is exactly `{"1","2","3","4","5"}` (strings). Any other key set, including integer keys, is refused by `Registration.from_mapping` with the typed refusal `item_ids_by_level_keys`. No normalisation.» [Q2]

**INV-10 block formation and pairing** (F: a; Chk: yes; code `inv_10`)
- Ruled texts: Q4 (i), (ii) (§3.1), and «(iv) The checker tests membership equality across models and the parent relation (13 F05) AND these three rules.» [Q4]
- Predicate: for each model and level, the parents are exactly the slices with exactly the ids of §3.1.

**INV-11 item conservation** (F: a; Chk: yes; code `inv_11`)
- Ruled text: «item conservation (per model, every registered item is in exactly one block that is neither superseded nor terminal, and that block is in exactly one envelope, or is in exactly one terminal refusal and no envelope)» [45/21 §7(S)]
- Predicate: for every (model, item), exactly one of these holds:
  - (a) exactly one block containing the item has `superseded == false`, is not terminal, and has its id in exactly one envelope's `blocks`;
  - (b) exactly one `terminal_refusals` entry names the item, and no block containing it is in any envelope's `blocks`.

**INV-12 parent relation** (F: a; Chk: yes; code `inv_12`)
- Ruled text: «Pairing survives a split: singles carry `parent_block_id`, and the estimator pairs on the parent (Opus B2).» [08 F2(a)]
- Predicate:
  - A single has one item. Its parent exists, has the same model and level, contains the item at position `j` (matching its id), and is `superseded`.
  - A superseded parent's singles partition its items.

**INV-13** — moved to A292 (item rows carry `retry_stage`). It is not a checker row.

**INV-50 model order by role** (F: a; Chk: partly; code `inv_50`)
- Ruled text: FT-6 (§3.1).
- Checker predicate (29 F3): the `idle_slot` has the `"1.7B"`-role model (Q14). Every roster list whose order is set by model iteration puts the `"8B"`-role model first (§10 X-1 fixes which lists these are).
- The insertion-order permutation witness (a registration with `role_to_model_id` keys reordered packs the identical roster) needs `pack`. It is NC, and runs in the implementer's suite.

#### D. Envelopes, reporting, placement

**INV-14 model homogeneity** (F: a; Chk: yes; code `inv_14`)
- Ruled text: «envelope model homogeneity» [45/21 §7(S)]
- Predicate: every placement in envelope `e` is of a block with `model == e.model`.

**INV-15 empty-envelope legality** (F: a; Chk: yes; code `inv_15`)
- Ruled text: «An envelope with no active block is legal iff its `kind` is `idle_slot` or its `voided_block_ids` is non-empty; `_seal` refuses any other empty envelope.» [45/21 §7(E)]

**INV-16 idle slots** (F: a; Chk: yes; code `inv_16`)
- Ruled text: «An empty slot is captured as a full-length envelope with its model worker loaded and idle, and is labelled `kind: "idle_slot"` in the roster.» [08 F1]; «`idle_slot` envelopes are never reported.» [FT-13]
- Predicate: an idle slot has `blocks == []` and `voided_block_ids == []`, keeps `observations` null, and receives no placement.

**INV-17 grid** (F: a; Chk: yes; code `inv_17`)
- Ruled text: «on a fixed-pitch grid in which idle slots are grid positions» [08 F1]
- Predicate: `envelopes[i].index == i` for all `i` (13 OP-27).

**INV-18 fixed envelopes; placement above the reporter; report order** (F: a; Chk: yes; codes `report_order`, `inv_18`)
- Ruled texts: «An envelope is fixed once an observation is recorded on it; a retry or reschedule is placed only at an index above the reporting envelope's.» [45/21 §7(E)]; «Every placement created by event `k` has `envelope_index > events[k].envelope_index`. The seal checks both on every roster.» [Q10]

**INV-46 report completeness** (F: a; Chk: yes; codes `report_order`, `unreported_envelope`, `inv_46`)
- Ruled text: «Every `loaded` envelope that has run is reported by one `requeue_overrun` call, in index order, including envelopes in which every block completed; `idle_slot` envelopes are never reported.» [FT-13]
- Predicate: the event indices are exactly the reported loaded envelopes; they form the lowest-index prefix of the loaded envelopes; and at `R` none is unreported.

**INV-19 no reuse after split** (F: a; Chk: yes; code `inv_19`)
- Ruled text: «The split stage never reuses the whole-block retry's envelope.» [45/21 §7(E)]

**INV-34 eligibility and placement order** (F: a; Chk: yes; code `inv_34`)
- Ruled texts: Q9, Q8, FT-3 (§3.2, §3.5).
- Predicate: every event placement's target equals the §3.5 re-derivation, made in the FT-3 order.

#### E. Capacity and reservations

**INV-20 capacity** (F: a; Chk: yes; code `inv_20`)
- Ruled text: «capacity by `reserved_s`» [45/21 §7(S)]
- Predicate: for each envelope, `Σ reserved_s ≤ cap` over its live and voided placements (13 OP-21).

**INV-21 initial and reschedule reservation** (F: a; Chk: yes; code `inv_21`)
- Ruled texts: Q11 (§3.1 step 3); «A `reschedule` placement keeps the block's previous `reserved_s`.» [Q11]

**INV-22 whole-block retry** (F: a; Chk: yes; code `inv_22`)
- Ruled text: «The whole-block retry is scheduled alone in a fresh envelope with `reserved_s = min(Σ item derived worst cases, capacity)`; `predicted_s` is unchanged.» [45/21 §7(W)]
- Predicate:
  - `reserved_s` is as §3.2;
  - the block's `predicted_s` is still `sum(predicted_item_s)`;
  - its envelope was appended by that event and holds no other placement.

**INV-23 single reservation** (F: a; Chk: yes; code `inv_23`)
- Ruled text: «Each single is packed at `reserved_s = predicted_s = the item's derived worst case`.» [45/21 §7(T)]

#### F. Spread

**INV-24 M8 by parent** (F: a; Chk: yes; code `inv_24`)
- Ruled text: «No two parent blocks of one cell share an envelope at any stage, initial or retry.» [45/10 §Q4]
- The checker must accept: «Pieces of one parent may share an envelope with each other and with blocks of other cells of the same model, within capacity.» [45/10 §Q4]

**INV-25 minima, root-only** (F: c; Chk: yes; code `spread_minima`)
- Ruled text: «The five-parent/five-envelope minima are a refusal only at `pack` (root roster). At `requeue_overrun` exits the seal checks M8-by-parent (no two parents of one cell share an envelope) and records, never refuses, a planned shortfall as `planned_spread_shortfall[cell]: true`.» [Q13]

**INV-49 `planned_spread_shortfall`** (F: b, plus (a) for staleness; Chk: yes; codes `stale_derived`, `spread_minima`)
- Ruled text: FT-7 (§3.4). The terms are defined by RD-5.

**INV-26 executed spread** (F: b at `R`, PROVISIONAL; Chk: yes, via `check_executed`; code `inv_26`)
- Ruled texts: §4.1.

#### G. Drift and balance

**INV-27 planned lever** (F: b; Chk: yes; code `inv_27`)
- Operative rule (29 F6): `requeue_overrun` recomputes and records `drift_lever_slots[level]` and never refuses on it (Q12 read under FT-7), with the planned position of RD-4 and the null rule of FT-10 (§3.4).
- Predicate: equality with the checker's recomputation (§10 X-4).

**INV-28 pack drift refusal** (F: a at `P`; b on requeue paths; Chk: yes; code `inv_28`)
- Ruled text: «`pack` in registered mode refuses a planned lever > `max_gap` (21/10 D5b).» [Q12]

**INV-45 executed lever and `drift_exceeded`** (F: b at `R`, PROVISIONAL; Chk: yes, via `check_executed`; code `inv_45`)
- Ruled texts: Q12 and FT-10 (§4.1).

**INV-41 idle insertion and balance** (F: a; Chk: yes; code `inv_41`)
- Ruled text: Q14 (§3.1 step 4).
- Predicate: the root roster has exactly one idle slot iff both models' loaded-envelope counts are odd, and that slot has the `"1.7B"`-role model.

#### H. Observations and decisions

**INV-29 observation record** (F: a; Chk: yes; codes `invalid_elapsed`, `inv_29`)
- Ruled text: «A block cut off before consuming time is reported `not_started`. Zero or negative elapsed is refused (`invalid_elapsed`).» [Q19]
- Predicate:
  - `event.block_ids` equals the pre-call `blocks` of the reporting envelope;
  - there is one observation per id, in order;
  - statuses and `elapsed_s` follow §2.7;
  - the envelope's `observations` equals the event's.

**INV-47 observation order** (F: a; Chk: yes; code `invalid_observation_order`)
- Ruled text: FT-14 (§3.2).

**INV-48 physics guard** (F: a; Chk: yes; code `invalid_elapsed`)
- Ruled text: FT-12 (§3.2).

**INV-30 decisions and `late`** (F: a; Chk: yes; code `inv_30`)
- Ruled texts: FT-1 and Q5 (§3.2).
- Predicate: every recorded `decision` and every block's `late` equals the §3.2 re-derivation.

**INV-31 innocent initial-stage placement** (F: a; Chk: yes; code `inv_31`)
- Ruled text: Q8 (§3.5).

**INV-32 whole-block outcomes** (F: a; Chk: yes; code `inv_32`)
- Ruled text: Q5 (§3.2).
- Predicate: split effects as §3.2.

**INV-33/43 single outcomes** (F: a; Chk: yes; code `inv_33_43`)
- Ruled texts: «its completed attempt is listed in the roster's voided attempts and its window `(block_id, attempt)` is excluded by `reduce` by rule, the event is a culprit event for its envelope-mates, and it consumes one of the item's two culprit events.» [Q6]; FT-11.

**INV-35 culprit linkage and limits** (F: a; Chk: yes; codes (a) `reschedule_without_culprit`, (b) `culprit_limit`, (c) `inv_35c` — see §10 X-7)
- Ruled texts: «INV-35(a): every `reschedule` decision, at any stage, sits in an event whose observations contain a culprit; the seal refuses (`reschedule_without_culprit`) otherwise.» [FT-1] «Each parent has at most one culprit observation at the `initial` stage and each single item at most two culprit observations across all events; the seal refuses (`culprit_limit`) a roster violating either. Within one event the count of `reschedule` decisions is at most the number of blocks in the reporting envelope minus one; the total over a roster is therefore finite.» [FT-2]
- Clause (c) is a seal refusal: «FT-2's per-event count (INV-35(c)) is a seal refusal with code `inv_35c`.» [RD-10]

**INV-36 stage legality and attempts** (F: a; Chk: yes; code `inv_36`)
- Ruled texts: «stage legality (each block's `retry_stage` history follows the closed edge list in (G))» [45/21 §7(S)], with the list of §1.3; Q11 and RD-14 (§3.3).
- Predicate:
  - every non-`keep` decision is one of the eleven edges from the block's stage at that event;
  - a root holds only `initial` placements with `attempt 0`;
  - attempts follow Q11.

**INV-37 typed terminals** (F: a; Chk: yes; code `inv_37`)
- Ruled text: «The single-problem stage is terminal: one single-problem retry, then the item is flagged `ceiling_violation`, a typed refusal for that item, recorded and never silently dropped (Opus S5).» [08 F2(c)]
- Predicate: §2.8. `(block_id, attempt)` names a voided placement of a block containing the item.

#### I. Replay, structure, constants

**INV-38 event log and digest chain** (F: a; Chk: yes; code `inv_38`)
- Ruled text: «The roster carries an append-only `events` list, one entry per `requeue_overrun` call (block id, observations, resulting `sha256`).» [45/21 §7(R)] (block ids per RD-1)
- Predicate:
  - `events[-1].sha256 == r.sha256`;
  - root: `registered_sha256 == sha256`;
  - on a transition: append-only, and `registered_sha256` unchanged;
  - per-event digests and the root digest as reconstructed by the checker (§6; needs §10 X-1 and X-4).

**INV-39 re-pack equality** (F: a; Chk: **NC**; code `inv_39`)
- Ruled text: FT-8 and Q16 (§3.6).
- This is the one ROSTER row the checker cannot evaluate: re-pack equality needs `pack`. The replay's re-derivations are covered by INV-30 to INV-38 in the checker.

**INV-40 seal placement** (F: a; Chk: NC, implementation structure; code `inv_40`)
- Ruled text: «`_seal(registration, roster)` runs on the input at the entry of `requeue_overrun` and `reduce` and at every public exit of `pack` and `requeue_overrun`.» [45/21 §7(S)] Plus FT-8's sole-caller sentence (§3.6).

**INV-44 constant sweep** (F: a; Chk: NC, implementation structure; code `inv_44`)
- Ruled texts: «Constants are patched at their module attribute; a scan finds no literal duplicate.» [45/21 §7(G)]; «CARRIED additions: `merge_order`, `min_correct`, `holm_m` → A293 (estimator; the lane 45/10 §Q2 calls 'A281b estimator'); `cap_bound_fraction` → A292 (reducer, the M3 cap-bound label). Each is a module constant pinned by `schema` and asserted equal to the AP-5M value by one A291 test; each is a mandatory CONSUMED row in its consumer lane's gate.» [Q1]

**INV-52 roster record types** (F: a; Chk: yes; code `inv_52`; row id assigned by the seat, §10 X-6)
- Predicate: every §2.3–§2.8 value has its stated type and domain.

---

## 6. Checker interface

**Module and imports.** `tests/scored_roster_checker.py`, as record 28 sets it. It uses the stdlib only. It never imports `joulewise.scored_packer`, `joulewise.scored_registration`, `joulewise.scored_reduce` or anything in `joulewise`, and it carries its own `canon`/`canon_sha` (§1.2).

```python
@dataclass(frozen=True)
class Violation:
    inv_id: str
    code: str
    detail: str

def check_registration(registration) -> list[Violation]            # INV-04 (sizes), 06, 09, 51
def check_roster(registration, roster, predicted_decode_s) -> list[Violation]
def check_transition(registration, before, after, predicted_decode_s) -> list[Violation]
def check_executed(registration, roster, predicted_decode_s, captured_window_keys) -> dict  # §4.2
```

**Behaviour.** The functions are pure and never raise.

- **`check_roster`** evaluates every "Chk: yes" row. For INV-38 it reconstructs the root and each intermediate roster from the final roster:
  - the root envelopes are those holding pack-time placements (RD-3), plus the idle slots;
  - it then re-applies §3.2 per event, recomputes §3.4, and compares digests.
- **`check_transition`** checks the append-only, fixedness and report-order clauses (INV-18, INV-38, INV-46).
- **NOT_CHECKABLE.**
  - INV-39 (re-pack) is the one roster row.
  - INV-40 and INV-44 are properties of implementation source.
  - INV-50's permutation clause needs `pack`.
  - INV-13 is moved.

**Stress run.**
1. Seeded `pack`.
2. Gapless, in-order reports of every loaded envelope, with random legal observations.
3. `check_roster` on every roster, and `check_transition` on every call.
4. At the end, compare `executed_status` with `check_executed` for random `captured_window_keys`.

The expected result is zero violations.

## 7. CARRIED, CONSUMED and obligation table

| Field / constant / duty | Status | Consumer | Source |
|---|---|---|---|
| `schema`, `registration_id`, `plan_id` | CONSUMED (identity) | INV-01 | 45/10 §Q2 |
| `mode` | CONSUMED | INV-05, INV-08, INV-28 | |
| `arm` | CONSUMED | ids, `worst`, `bpc` | |
| `role_to_model_id` | CONSUMED | INV-10, INV-14, INV-50 | |
| `cap_tokens`, `s_per_token_upper`, `prefill_s` | CONSUMED | `worst` | Q17 |
| `block_size` | CONSUMED | INV-10, `bpc` | |
| `item_ids_by_level` | CONSUMED | INV-04, INV-09, INV-10, INV-11 | 45/10 §Q3 |
| `interior_s`, `guard_s` | CONSUMED | `cap`, FT-12 | |
| `delta_upper_j_per_block_slot`, `budget_j` | CONSUMED | `max_gap` | 21/10 D5b |
| `predictions_sha256` | CONSUMED | INV-08 | 45/10 §Q3 |
| `alpha`, `n_boot`, `seed`, `floor_j`, `anchor_j`, `declared_sensitivities`, `arm_to_family` | CARRIED | A293 estimator | 45/10 §Q2 |
| `sizing_receipt_sha256` | CARRIED | scored-night arm gate (runner lane) | 45/10 §Q2 |
| `ceiling_s` | CARRIED | runner, kill timeout | 45/10 §Q2; Q17 |
| `scorer_id` | CARRIED | A292 and the runner | 45/10 §Q2 |
| `envelope_s`, `offset_s`, `pitch_s` | CARRIED | runner lane | 45/21 §7(G) |
| `MERGE_ORDER`, `MIN_CORRECT`, `HOLM_M` | CARRIED constant | A293 | Q1 |
| `CAP_BOUND_FRACTION` | CARRIED constant | A292 | Q1 |
| `LEVELS`, `RETRY_STAGES`, `EDGES`, `MIN_PARENT_BLOCKS`, `MIN_ENVELOPES` | CONSUMED constant | §1.1 | |
| Runner sequencing | obligation | «Runner lane: envelope `r+1` does not start until `requeue_overrun` for `r` has returned and its roster is loaded; if it cannot, the runner reports `r+1` with every block `not_started`.» | FT-9 |

«Every CARRIED row is a mandatory CONSUMED row in its consumer lane's gate.» [45/21 §7(G)]

## 8. R11, precedence, and items for other lanes

**R11.** «R11 is refuter text; B26 is a seat brief, outside the ruled precedence chain (charge §"What this gate rules"; charter §7: narrative is argument). It did not bind. It binds from this ruling forward through Q12's text.» [Q18]

**Precedence (A293).**
- «Precedence extends (P): NE(`ceiling_violation`) > NR; a level with both `spread_exceeded` and `drift_exceeded` is NR with both reasons recorded.» [Q12]
- «A level any of whose cells holds an `unattributed_overrun` refusal is NR(`unattributed_overrun`) unless NE(`ceiling_violation`) applies to that level; NR reasons accumulate and every applicable reason is recorded.» [FT-5]
- «When a level carries both NE(`ceiling_violation`) for a group and `spread_exceeded`, NE(`ceiling_violation`) takes precedence in the A281b total table and `spread_exceeded: true` is recorded alongside; a level with `spread_exceeded` and no NE is NR(`spread_exceeded`).» [45/21 §7(P)]

**A292:**
- item rows carry `retry_stage` (08 F2(b));
- `reduce` calls `verify_executed_roster` first and re-runs the `R` witnesses (Q16);
- windows are counted only for live placements (FT-11);
- a terminal window is recorded as `gross_j` and never summed (45/10 §Q5 F3);
- `cap_bound_fraction` is consumed there (Q1).

**For the Fable final pass (29 F5):** «block ids and `planned_spread_shortfall` keys are unambiguous only while model ids contain no `:`.» No domain restriction is added. RD-13 is dropped.

## 9. Coverage

- **Ruling 10.**
  - Q1 → INV-44, §1.1, §7.
  - Q2 → INV-09.
  - Q3 → §1.2, INV-04, INV-10.
  - Q4 → §3.1, INV-10, INV-12 (Q4(iii) → FT-6).
  - Q5 → §3.2, INV-32.
  - Q6 → §3.2, INV-33/43.
  - Q7 → superseded by FT-1.
  - Q8 → §3.5, INV-31.
  - Q9 → §3.5, INV-34.
  - Q10 → §3.2, INV-18.
  - Q11 → §3.1, §3.3, INV-21, INV-36.
  - Q12 → §3.1, §3.2, §4.1, §8, INV-27, INV-28, INV-45.
  - Q13 → §4.1, INV-25, INV-26.
  - Q14 → §3.1, INV-41.
  - Q15 → §5.1.
  - Q16 → §3.6, INV-39.
  - Q17 → §2.1, INV-06.
  - Q18 → §8.
  - Q19 → §2.7, INV-29.
  - Q20 → §2.9, INV-02, INV-38 (replay amendment → FT-8).
- **Addendum final texts.**
  - FT-1 → §1.2, §1.3, §3.2, INV-30, INV-35.
  - FT-2 → INV-35, §1.1.
  - FT-3 → §2.5, §3.2, INV-34.
  - FT-4 → §0.4, §5.1, INV-25.
  - FT-5 → §8.
  - FT-6 → §2.3, §3.1, INV-03, INV-50.
  - FT-7 → §3.2, §3.4, INV-27, INV-49.
  - FT-8 → §2.7, §3.2, §3.6, INV-39.
  - FT-9 → §7.
  - FT-10 → §3.4, §4.1.
  - FT-11 → §3.2, §4.1, INV-33/43.
  - FT-12 → §3.2, INV-48.
  - FT-13 → §2.5, §3.2, §3.6, INV-46.
  - FT-14 → §3.2, INV-47.
- **Record 25.** RD-1 → §2.7; RD-2 → §2.7; RD-3 → §2.6; RD-4 → §3.4; RD-5 → §0.4; RD-6 → §3.6 as amended by 29 F2; RD-7 → §3.6; RD-9 → §2.7; RD-10 → §5.2; RD-11 → §2.5; RD-12 → §5.2; RD-14 → §3.3.
  - RD-8 → retracted (29 F4), now a non-gating set in §5.1.
  - RD-13 → dropped (29 F5), §8.
- **Record 29.** F1 → this file; F2 → §3.6; F3 → INV-50; F4 → §5.1; F5 → §8; F6 → INV-27, §8; F7 → §5.2 and codes; F8 → §1.2.

## 10. Residual open details (choices this file had to make or could not make; none silent)

- **X-1. List orders.** These are needed for the checker's reconstruction of intermediate rosters (INV-38) and for INV-50's "8B first".
  - Unruled: the order of `roster.blocks` at `pack`, and the append order of `voided_block_ids` and `terminal_refusals` within one event.
  - Proposal: `blocks` at pack ordered by level ascending, then role order, then `k` (c:scored_packer.py:225-246), with singles appended at split in `j` order. `voided_block_ids` appended in `block_ids` order. `terminal_refusals` appended in `block_ids` order, then item order.
  - Nothing is installed.
- **X-2. `retry_stage` of a split parent.** Unruled. Proposal: it stays `whole_block` (c:scored_packer.py:314-320); the parent is marked by `superseded`. Installed in §3.2 as a proposal only.
- **X-3. A single's `predicted_item_s`.** Unruled. Proposal: `[parent.predicted_item_s[j]]` (c:scored_packer.py:332). Not installed.
- **X-4. Float evaluation order.** Needed for bit-exact reconstruction of intermediate digests. Proposal:
  - the parent `predicted_s` is `sum()` in item order;
  - the whole-block Σ worst is `sum(worst(m) for each item)`;
  - a planned position is `sum(indices in item order) / count`;
  - a per-model mean is taken over parents in `roster.blocks` order.
  
  Alternatively, rule that the checker compares recomputed levers with `isclose(rel_tol=1e-9)` and does not reconstruct intermediate digests.
- **X-5. `executed_status` return shape.** RD-6 says «per-level `spread_exceeded`», but 45/10 §Q4 and FT-10 make it a CELL property. §4.2 proposes cell keys and key names, and `false` for FT-10's "not set". FT-10 also reads "zero counted parents" (fully counted) for the null condition while positions exist for partly counted parents; §4.1 installs both texts literally. Confirm.
- **X-6. New row ids.** INV-51 (registration domain) and INV-52 (roster types) are seat-assigned, so every §2 rule has a row and a code. `inv_id` strings are the headings as written ("INV-33/43").
- **X-7. INV-35 codes.** 29 F7 lists `inv_35a`/`inv_35b`/`inv_35c` for the lettered sub-rules, but also says «ruled codes where the rulings name one». FT-1 and FT-2 name `reschedule_without_culprit` and `culprit_limit`, so §5.3 uses those for (a) and (b) and uses `inv_35c` for (c). Confirm.
- **X-8. The constants' AP-5M anchor.** The AP-5M text is not yet adopted (gate packet 30 pending), so the §1.1 values come from 45/10 §Q3 and c0998fdb. The Q1 equality test binds to the adopted AP-5M text once it lands. `MERGE_ORDER`'s list encoding is c0998fdb's.
- **X-9. "The one row".** 29 F1 names INV-39 as the one row the checker cannot evaluate. INV-40 and INV-44 are also not checker-evaluable (they are properties of implementation source), and so is INV-50's permutation clause. They are listed as NC with that reason.
- **X-10. Brief 28.** It tells the checker to parse INV ids from 02c. It needs repointing to 02d. Not my file.

## 11. Change log vs 02c

1. Self-contained. Inlined here: the registration key set, types and domains (§2.1); the prediction map (§2.2); every roster record schema (§2.3–2.8); the digest chain (§2.9); constants with values (§1.1); derived quantities (§1.2); the full decision and effect procedure (§3); the executed-value rules (§4); and the full CONSUMED/CARRIED/obligation table (§7). Previously these were delegated to 02b, the AP-5M text or c0998fdb.
2. Record 25 installed: Event `block_ids` (RD-1), index `placements` (RD-2), the top-level `placements` order (RD-3), planned position (RD-4), non-terminal and occupy (RD-5), `executed_status` (RD-6 + 29 F2), `unreported_envelope` in `verify_executed_roster` (RD-7), decision vocabulary (RD-9), codes (RD-10), recorded observations carrying `decision` (RD-11), `Violation` (RD-12), terminal stage (RD-14).
3. RD-8 became a non-gating all-`keep` test set; the gate stays at 13 paths (29 F4). RD-13 was dropped, with a note for the Fable final pass (29 F5).
4. INV-50 now checks role order directly (29 F3). INV-27's operative sentence uses `drift_lever_slots` only; §8 carries Q12's full precedence sentence (29 F6). There is one `Violation(inv_id, code, detail)` and a code on every row (29 F7). Q3's blocks-per-cell sentence was added (29 F8).
5. New rows INV-51 and INV-52 (X-6). INV-39 is marked as the one checker-NC roster row, and INV-40, INV-44 and INV-50's clause are marked NC with reasons.
6. Removed: the `ceiling_violation` decision value (RD-9), and every "as in 02b" delegation.
