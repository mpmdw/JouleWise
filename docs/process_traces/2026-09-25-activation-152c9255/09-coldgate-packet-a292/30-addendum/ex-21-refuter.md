# Contract-lens refuter report: A292 synthesis (ex-30) and its §P proposals

**Seat:** Opus 5.5 contract-lens refuter, working blind to the Fable judge. I read only; I ran no tests and started no subagents.
**Packet:** `00-charge.md`, sha256 `99d9cbdd…d57d25e858`. I recomputed the hash and it matches.

**Bottom line:** two proposals cannot be executed as written (P-S7 and P-S3), ten more need their text corrected, and three of the "Agreed by all three" items do not match their sources.

---

## BLOCKER

### B1. P-S7 contradicts the gated A291 re-run obligation. "Refuse" is not the no-new-rule option.

**Evidence.**
- The A291 contract rules that `captured_window_keys` is «the set of `(block_id, attempt)` keys the reducer has windows for; A292 supplies it» (89:379).
- A window counts only when it is live **and** in that set (89:387). Spread is decided «from the finished roster and the set of captured window keys» (15/10:41; 89:389).
- INV-26 (executed spread) and INV-45 (executed lever) are PROVISIONAL witnesses of form (b), a recorded value at `R` (89:560, 89:572; the forms are at 89:407).
- A292 «re-runs every A291 `reduce`-column witness at the real entry as mandatory rows» (15/10:47; kernel acceptance summary).
- Three A291 witnesses deliberately omit a **live** key and assert a flag, not a refusal:
  - `tests/test_scored_packer.py:278-302`, `test_checker_executed_voided_attempt_counterexample`: "Its voided attempt is captured; the live attempt is not", then `assertTrue(spread_exceeded[cell])`.
  - `tests/test_scored_packer.py:318-342`, `test_executed_partly_counted_parent_position`: it removes a live single key and asserts lever 1.6.
  - `tests/test_scored_packer_fuzz.py:130-132,153,169`: a 75 % sample over **all** placement keys.

**Why this blocks.** Under P-S7 every one of these refuses at the real `reduce`, so the mandatory re-run rows cannot pass. ex-30 notices only one of them (ex-30:149) and proposes *replacing* it. Replacing a witness is not re-running it.

P-S7's reason ("a typed `window_missing` outcome would be a new science rule") is half the picture. The ruled A291 surface already disposes of a live key with no window: the window is not counted and the cell is flagged. Refusing *amends that ruled consumer obligation*. It may still be the right call, but only as an explicit amendment.

P-S7 also says "the cure for a lost capture is recapture". That is false today. K25 says: «Until the code lane's gate ratifies this text, `_seal` refuses these paths and no K22 or S8 recapture roster can be produced» (07d:810). The real cost is the whole night.

**Corrected P-S7 text:**
> P-S7. `reduce` refuses (`missing_live_window`) when any live placement key `(block_id, attempt)` lacks a window. This AMENDS 15/10 Q16 for the A291 witnesses whose `captured_window_keys` omit a live key (`test_scored_packer.py::test_checker_executed_voided_attempt_counterexample`, `::test_executed_partly_counted_parent_position`, `test_scored_packer_fuzz.py` `_keys`). At the real `reduce` their ruled outcome is `ReductionRefusal("missing_live_window")`, asserted by name. INV-26 and INV-45 form-(b) rows at `R` are re-witnessed through `reduce` with terminal-driven fixtures in which every live key is captured. `executed_status` keeps accepting partial key sets (the A291 surface is unchanged), and `reduce` passes it exactly the set of live keys. Until K25 is ratified, a refused night is lost whole; no recapture exists.

### B2. P-S3 cannot be executed: vocabulary drawn from the runner module omits the normal end-of-answer value, and it invents a science rule for runtime failures.

**Where `stop_reason` is actually set** (`joulewise/adapters/mlx_runtime.py`):

| Line | Value set | When |
|---|---|---|
| :568 | `"runtime_failed"` | Default; kept if prompt preparation or `_generate` raises |
| :590 | `"malformed"` | Fatal prompt-closure problem |
| :611 | `generation.stop_condition` | Normal generation; the value comes from :895-900 (below) |
| :624 | `"length"` | Overwrites the above on non-`fixed_budget_exact` items when `emitted == planned_output_tokens` |

At :895-900, `generation.stop_condition` is `"requested_tokens_emitted"` if `output_tokens == max_tokens`, otherwise `last_finish_reason or "stream_exhausted"`. `last_finish_reason` is whatever mlx_lm returns as `response.finish_reason` (:822-824). That vocabulary is open and lives outside this module. The normal end-token value `"stop"` is **not a literal anywhere in `mlx_runtime.py`**.

Line :338 is not an emit site: it is output-policy metadata. ex-30:52 cites it as one.

**Consequences.**
- A constant "pinned by a test against that module's emit sites" comes out as {runtime_failed, malformed, requested_tokens_emitted, stream_exhausted, length}. Every row that ends on the end token then refuses as `row_stop_reason_unknown`, so every night refuses. The other outcome is that the harness seat guesses.
- The cap class on the scored path is only `"length"`. `"requested_tokens_emitted"` survives only on `fixed_budget_exact`, which is not a scored policy.
- P-S3's last bullet ("runtime failures are scored outcomes") counts an infrastructure fault as a wrong answer. K3 rules only capped and malformed attempts as incorrect (07d:262-263). "Malformed" there is an answer-parse outcome, not the runner's `malformed` value.

**Corrected P-S3 text:**
> P-S3. `STOP_REASONS = {"stop": False, "length": True}`, where the value means "cap class". This is the K3 wording «end token vs "length"» (07d:262-263). Any other value, including `runtime_failed`, `malformed`, `stream_exhausted` and `requested_tokens_emitted`, refuses the reduction with `row_stop_reason_unknown`. A row refuses with `row_cap_disagreement` unless `STOP_REASONS[stop_reason] == (generated_tokens >= cap_tokens[arm])`. It is a runner-lane obligation (a CARRIED non-field row) to map mlx_lm finish reasons onto {stop, length} and never to emit a scored row for a runtime failure. No runtime failure is ever counted as incorrect; any change to that goes to HEADLINE-AP5M-AMENDMENT-01.

---

## MATERIAL

### M1. The defect-1 cure contradicts K17 and the kernel.

The ruled text is «recorded on the terminal refusal as `gross_j`» (45/10:79; 07d:746; kernel summary). The adopted cure (ex-30:197) removes `gross_j` from terminal records.

Only `ceiling_violation` is under K17, and it is always a one-item single (`scored_packer.py:444-449`), so its record can carry `gross_j` without any double counting. There is also a case nobody covered: an `unattributed_overrun` created by `not_started` never ran, so it can have no window. Two edges produce this: no-culprit `not_started` (:437) and whole-block `not_started` (:433; 15/10:25).

**Corrected text:**
> A `ceiling_violation` terminal record carries `gross_j` (number, or `null` if its window is absent; P-S8). `unattributed_overrun` records carry `window_key: [block_id, attempt]` and no `gross_j`. `terminal_windows[block_id:attempt]` holds that window once. A window whose key's observation status is `not_started` refuses (`window_not_started`). A window for a `cut_off`/`completed` `unattributed_overrun` key is optional.

### M2. P-S1's reason is false, and the recomputation must be spelled out.

**What the runner holds at capture.** Under FT-9 (15/21:74), when envelope *k* starts the runner holds the roster returned by `requeue_overrun` for the last reported loaded envelope below *k*.

**Why it is recoverable without a new replay.** Each event stores the digest of the roster after that event (`scored_packer.py:309,466`), and the verifier's replay already checks every one (`:485`). An envelope's contents are fixed before it runs, because new placements only go to envelopes above the reporting one (`_eligible`, `:334`). So the in-force digest can be read straight off the checked roster.

**Why the stated reason fails.** Those stored event digests are inside the final sealed roster. Anyone holding that roster can stamp any window with its in-force digest after the night. The in-force stamp therefore evidences FT-9 exactly as little as a final stamp does. The valid reasons are that it is *stampable at capture* (the final digest is not) and that it binds a window to the plan in force for its envelope (the root digest does not).

**Corrected text:**
> `in_force(k) = max((e for e in roster["events"] if e["envelope_index"] < k), key=envelope_index)["sha256"]`, else `roster["registered_sha256"]`. Each window and each row stamps `in_force(envelope_index of its placement)`. A mismatch refuses (`window_binding` / `row_binding`). This is a consistency binding, not evidence of FT-9; FT-9 stays a runner-lane obligation with no reducer witness.

### M3. The K24 paired drop is missed by all three seats; the agreed `cap_bound` denominator is wrong.

K24: a problem with no counted attempt for either model «contributes to neither model's energy nor correct count nor n for that cell» (07d:196). Step 3 repeats «dropped from both models» (07d:268-270). No seat and no proposal applies this to counts. The "Agreed" item "over counted rows only" (ex-30:90) counts per model.

**Flip example.** An 8B cell has 10 counted rows, 2 of them capped: 2/10 is not cap-bound. Now one uncapped 8B item's 1.7B partner is a `ceiling_violation`. Under K24 the cell has n = 9, and 2/9 = 22.2 % is cap-bound.

**Corrected text:**
> A cell's `n`, `n_correct` and `n_capped` range over K24-paired items: items with a counted attempt for **both** models at that level. `cap_bound = n_capped / n > CAP_BOUND_FRACTION`, or `null` when `n == 0`. Items dropped under K24 are listed per cell with the partner model's terminal type. Counted rows stay in the output unfiltered, but cell counts use the paired set.

### M4. The per-window anchor bound is omitted from the schema and from the deferred list.

K11's operative text: `anchor_{j,w}` is «window w's reducer field `energy_bound_terms_j.E_clock_anchor_shift_bound_j`; a counted window without a bounded value is refused (`anchor_energy_envelope_unrecorded`)» (07d:640). This needs no registration key, so the reason used to defer `below_floor` does not apply.

**Corrected text:**
> Windows carry `energy_bound_terms_j: {"E_clock_anchor_shift_bound_j": finite number ≥ 0}`. A counted window with this missing or non-finite refuses (`anchor_energy_envelope_unrecorded`). Answer to D2: without this field A292 is not claim-bearing.

### M5. P-S13 weakens oracle independence.

"Imports no `joulewise` **reducer internals**" (ex-30:192) is weaker than three sources:
- 45/10:31 Q2(4): «imports nothing from the packer».
- The R7 item agreed by all three (ex-30:144): no `joulewise` imports.
- The checker precedent: «No production module is imported» (`tests/scored_roster_checker.py:3`).

An oracle that calls `scored_packer.executed_status` shares the spread and drift code with `reduce`, so a bug there shows up identically in both and the differential test cannot see it.

**Corrected text:**
> `tests/scored_reduce_checker.py` imports no `joulewise` module. Registration values come from the mapping `g`. It may import `tests.scored_roster_checker`. An AST test enforces this.

### M6. The differential test degenerates under P-S7.

With 50 or more live keys per night and a drop rate drawn from 0–25 %, (1−r)^50 is close to zero for any r above about 5 %. Almost every night therefore refuses, and the counted path (sums, caps, cells) is barely compared.

**Corrected text:**
> ≥ 200 generated nights with every live window present, compared field for field; plus ≥ 50 nights each with exactly one live window dropped at a seeded position, where both implementations must refuse `missing_live_window`.

### M7. No row-completeness rules, and P-S4 passes rows through unchecked.

ex-30 gives completeness rules for windows only. The kernel partition needs row rules too.

**Corrected text:**
> Exactly one row per (model, item) at its live placement: missing refuses (`missing_live_row`); duplicate `(item_id, block_id, attempt)` refuses (`duplicate_row`); a key that is no placement of that item refuses (`row_unknown_key`); a row at a `not_started` key refuses (`row_not_started`). Rows at voided attempts are optional, at most one per key, and go through the same schema and binding checks; they are emitted as `superseded_rows`, not "verbatim".

### M8. The mutation sweeps are left out of the gate design.

The gate criterion's closed path list includes `reduce`, and it requires that «the operand, boundary and guard-deletion sweeps kill every mutant» (45/21:56). §P names no sweep. The boundary sweep is exactly what tests `≥` in the cap test and `>` in `cap_bound`.

**Corrected text:**
> Add to the RED harness a named `test_scored_reduce_mutation_sweeps` covering operand collapse, `>`↔`>=`, and guard deletion over `joulewise/scored_reduce.py`. Every mutant is killed.

### M9. P-S9: `generated_tokens > cap` should refuse, as an evidence failure.

Three things rest on the cap never being exceeded:
- `worst()` = cap × s/token + prefill (`scored_registration.py:99-102`);
- the registered inequality derived worst case ≤ `ceiling_s` ≤ capacity (`:153-154`);
- the packer's single-stage culprit and `ceiling_violation` decisions (`scored_packer.py:246,428`).

An over-cap row means those decisions may have been manufactured or missed, and a counted NE/NR status would then be wrong. The ruled `≥` defines the label; it does not make the row admissible.

**Corrected text:**
> `generated_tokens > cap_tokens[arm]` refuses (`row_tokens_over_cap`).

---

## NIT

- **N1. Where the witness patches the constant.** "Imported by name" plus "patches the module attribute" (ex-30:91) contradict each other: after `from joulewise.scored_registration import CAP_BOUND_FRACTION`, patching `scored_registration.CAP_BOUND_FRACTION` does not reach the reducer. Text: "The reducer reads `sr.CAP_BOUND_FRACTION` at call time; the witness uses `patch.object(sr, "CAP_BOUND_FRACTION", …)`; a scan finds no `0.2` literal in `scored_reduce.py`."
- **N2. P-S5 disjointness is too narrow.** Check against **every** `PackingRefusal` and `RegistrationRefusal` code literal, not only `inv_*`. The packer also uses `report_order`, `unreported_envelope`, `stale_derived`, `spread_minima`, `invalid_elapsed`, `culprit_limit`, and others.
- **N3. Wrong emit-site citation.** ex-30:52 should cite `mlx_runtime.py:568,590,611(:895-900),624`, not :338.
- **N4. INV-13 wording.** The ruling reads «item rows carry `retry_stage`» (89:491). Output item rows should carry `retry_stage` taken from `placement["stage"]` of the counted attempt; `retry_stage_counts` per cell is derived from that.
- **N5. FT-5 count unit.** The per-cell `unattributed_overrun` count should be in items (terminal records), stated as such.
- **N6. "Do not read the oracle" is instruction-only.** RED-run tracebacks print oracle source lines. Record this as a known limit.

---

## Check of the "Agreed by all three" items

| Item | Result |
|---|---|
| R1: first statement is `verify_executed_roster` (15/10:47) | Verified |
| R1: binding keys (kernel) | Verified |
| R1: duplicate or unknown window key refuses | Verified |
| R1: own exception class | Verified |
| R1: block energy summed once per window | Verified |
| R2: `unreported_envelope` in the verifier (`scored_packer.py:494`) | Verified; it fires after `_seal` and replay |
| R3: `cap_bound` "over counted rows only" | **Fails.** K24 pairing; see M3 |
| R3: constant "imported by name" plus "patch the module attribute" | **Fails as worded**; see N1 |
| R4: shape, null-lever rule, and partly counted parents contribute positions (`scored_packer.py:150-157`) | Verified |
| R5 | Verified |
| R6 | Verified |
| R7: "no `joulewise` imports" | Verified as a source, but **§P departs from it**; see M5 |

**Also found:**
- The claim "`floor_gate_j` not in `REGISTRATION_KEYS`" is true, but `floor_j` is present (`scored_registration.py:28`). AP-5M v4 removed `floor_j` (07d:841), so the registration still carries a superseded field; it is CARRIED to A293 per 45/10:40.
- The defect-1 fact is verified (`:445-449`).
- The defect-2 citation is verified (08:13; 89:491).
- The FT-5 citation is verified (15/21:66).
