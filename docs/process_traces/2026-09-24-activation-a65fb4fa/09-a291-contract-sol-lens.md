```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All 40 invariants and 34 open points reviewed; several predicates and the roster representation need correction or a cold-gate ruling.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "3aaacb6ad8a94f3e59cfb0469f839765861e0a90",
    "head_end": "3aaacb6ad8a94f3e59cfb0469f839765861e0a90",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"F01","severity":"blocker","inv":"INV-03"},
      {"id":"F02","severity":"blocker","inv":"INV-04"},
      {"id":"F03","severity":"blocker","inv":"INV-05"},
      {"id":"F04","severity":"blocker","inv":"INV-09"},
      {"id":"F05","severity":"blocker","inv":"INV-10, INV-12"},
      {"id":"F06","severity":"blocker","inv":"INV-20, INV-22"},
      {"id":"F07","severity":"blocker","inv":"INV-26"},
      {"id":"F08","severity":"blocker","inv":"INV-35"},
      {"id":"F09","severity":"blocker","inv":"INV-38"},
      {"id":"F10","severity":"blocker","inv":"INV-39"},
      {"id":"F11","severity":"should_fix","inv":"INV-06, INV-19, INV-25, INV-40"},
      {"id":"F12","severity":"should_fix","inv":"INV-13, INV-17, INV-21, INV-36"},
      {"id":"F13","severity":"should_fix","inv":"INV-27, INV-28"},
      {"id":"F14","severity":"should_fix","inv":"INV-29, INV-30, INV-31, INV-32, INV-33, INV-34"},
      {"id":"F15","severity":"should_fix","inv":"missing invariants and gate rows"},
      {"id":"F16","severity":"should_fix","inv":"data contract"}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"inspection",
      "cmd":"git status --short --branch && git rev-parse HEAD",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","3aaacb6ad8a94f3e59cfb0469f839765861e0a90"]},
      "expected":{"exit_code":0,"tail_regex":"## HEAD \\(no branch\\).*3aaacb6ad8a94f3e59cfb0469f839765861e0a90"}
    }
  ],
  "flags": [
    {
      "id":"G1",
      "kind":"lead_ruling",
      "level":"blocking",
      "text":"OP-01 exposes a closed-list scope conflict; OP-14 exposes conflicting whole-block transitions. Several other semantic picks require a cold gate.",
      "needs":"Obtain written cold-gate answers before freezing the matrix or checker."
    }
  ]
}
```

## Findings

Citation keys: **D** = [record 02](/Users/edr/code/wt-a65fb4fa-lens/docs/process_traces/2026-09-24-activation-a65fb4fa/02-a291-invariant-matrix-and-roster-contract.md); **A** = [45/21 addendum](/Users/edr/code/wt-a65fb4fa-lens/docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md); **B** = [45/10 ruling](/Users/edr/code/wt-a65fb4fa-lens/docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md); **C** = [21/10 ruling](/Users/edr/code/wt-a65fb4fa-lens/docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/10-coldgate-fable-ruling.md); **H** = [08 rulings](/Users/edr/code/wt-a65fb4fa-lens/docs/process_traces/2026-09-23-activation-d8cc9c0a/08-a281-round1-synthesis-and-rulings.md). Line references below use these file keys.

### L1 — invariant defects

I checked the text inside `«…»` against its cited source for **INV-01–INV-40**. All quoted fragments are verbatim. The defects are in predicates, scope, and path witnesses.

- **F01 — INV-03, BLOCKER.** “No key at any level” named like a Registration key rejects the roster’s required `schema` key. It also substitutes a name ban for the ruled ban on *copies of values*. **Fix:** retain exact roster key sets; prohibit fields that duplicate registered values, while allowing the roster’s own schema and ruled derived fields. D:30–35, 325–338; A:52; B:30.

- **F02 — INV-04, BLOCKER.** OP-04 chooses a nested list for `item_set_sha256`, while the ruled preimage is `[ids in level order]`. That changes the digest and refuses a roster using the ruled preimage. **Fix:** specify the flat, level-ordered ID list; seek a cold ruling before using a nested preimage. D:38–39, 459; B:53.

- **F03 — INV-05, BLOCKER.** Equality to `(mode == "registered")` requires every registered roster to be claim-ready. The ruling expressly requires pilot rosters to be false and consumers to refuse non-claim-ready rosters outside pilot; it does not require registered-mode producers to emit only true. **Fix:** check the pilot implication at production and the consumer refusal separately. D:41–42; C:66.

- **F04 — INV-09, BLOCKER.** The predicate compares Registration’s string keys `"1".."5"` with `LEVELS = [1,2,3,4,5]`; as written, it fails every valid registration. **Fix:** compare to `{str(level) for level in LEVELS}` and use integer levels only in block records. D:69–76, 281, 299; H:24.

- **F05 — INV-10 and INV-12, BLOCKER.** Identical membership across models and parent identity do not rule consecutive slicing, ordered tuple equality, or either exact `block_id` format. Those checker requirements would refuse other paired partitions and IDs. **Fix:** make membership equality and parent relationships the invariant; move slicing and ID syntax to an expressly approved representation contract. D:78–79, 88–95; B:69; H:12.

- **F06 — INV-20 and INV-22, BLOCKER.** A parent retains one block ID when its whole-block retry changes `reserved_s`. The same block remains in the first envelope’s `voided_block_ids`; summing its new reservation there mischecks the capacity that actually ran. INV-22 also applies “alone” to that earlier, possibly shared envelope. **Fix:** record reservation, stage, and attempt per *placement*; apply “alone” only to the fresh whole-block-retry placement, and check each envelope against its historical reservations. D:131–143, 348–359, 370–372; A:44, 52; B:56.

- **F07 — INV-26, BLOCKER.** “Every item has a counted window” becomes “no item has a terminal refusal”; OP-24 expressly counts a pending block as a future counted window. A pending item is not a counted capture. **Fix:** derive executed minima from actual counted-attempt evidence, keep planned minima distinct, and define when `spread_exceeded` can first be final. D:155–163, 475–477; B:69–71; A:58.

- **F08 — INV-35, BLOCKER.** The aggregate count omits both ruled premises: each innocent reschedule must have a culprit event in its envelope, and each item has at most two culprit events. A roster can meet the aggregate bound while violating either premise. **Fix:** check causal linkage and the per-item limit, then the aggregate limit. Add the corresponding single-stage paths, including a culprit advancing on E6 or E8 while a mate reschedules. D:218–219; A:48.

- **F09 — INV-38, BLOCKER.** The proposed event `sha256` is a digest with that field set to null, not the ruled *resulting* `sha256`; the top digest then includes the event and differs. **Fix:** establish a non-circular digest encoding under which `event.sha256` equals the resulting roster digest, or obtain an amendment that names a different event digest. Check the equality on each transition. D:240–245, 470–472, 401–404; A:54.

- **F10 — INV-39, BLOCKER.** The contract permits a root roster with `registered_sha256 = null`, while the unqualified ruling says `reduce` asserts that field equals the digest of `pack(...)`. The draft’s proposed root exception is a new rule. **Fix:** either make `reduce` reject roots and remove the root R witness, or obtain a cold-gate exception defining root reduction. D:248–249, 337, 401–403, 473; A:54.

- **F11 — path coverage, MATERIAL.** INV-06 declares all requeue edges inapplicable because registration was previously validated; that does not supply the executed witness demanded for each magistrate row. INV-19 omits E8 although its post-split roster still contains the relevant history. INV-25 calls for R on a root while the root-replay contract conflicts as above. INV-40 offers call-site mutants rather than witnesses across P, E1–E9, R. **Fix:** provide an executed violating witness on every closed path, including entry/exit injection where needed; send any proposed `n/a` exception through a cold gate. D:46–48, 126–127, 155–156, 251–252, 503–505; A:56.

- **F12 — representation and scope, MATERIAL.** INV-13 quotes a requirement on reducer *item rows* but checks only a packer Block. Move the row obligation to A292 and retain block-stage checks under INV-36. INV-17 permits skipped indices despite the ruled fixed-pitch grid with idle positions; require contiguous represented capture positions or rule the meaning of a gap. INV-21 turns an expressly unruled initial reservation into a magistrate invariant. INV-36 similarly makes exact attempt increments and a particular root representation mandatory without a quoted rule. **Fix:** rule these choices before making them acceptance predicates. D:97–98, 115–116, 134, 221–228; H:7–9, 13; A:56.

- **F13 — drift, MATERIAL.** INV-27’s `pos` uses a currently scheduled active block even when no counted attempt has been captured; the quoted definition uses the envelope of the *counted attempt*. INV-28 takes registered-mode refusal at pack and post-capture flag-only behavior largely from stopped code, while the authoritative texts rule a bound and a parent-unit seal check without settling that after-capture consequence. **Fix:** separate planned pack positions from counted executed positions, and cold-rule post-capture refusal versus recorded status before making either a checker predicate. D:167–176, 279–280, 492–498; B:73, 82; C:70; A:52.

- **F14 — observations and transitions, MATERIAL.** INV-29 requires strictly positive elapsed seconds although (W)/(N) say “elapsed seconds” without that boundary; decide whether an immediate cut-off can be zero. INV-30 covers only initial blocks despite (W) naming whole-block blocks; INV-31 and INV-32 leave the (W)/(T) conflict to OP-14 instead of defining a checkable whole-block decision. INV-33 imposes INV-34’s *reschedule* placement on an advancing culprit, while (N) applies that placement to “any other” uncompleted single. The draft’s OP-15 also says a completed single both keeps and voids its window. **Fix:** rule those boundaries and whole-block transitions; add a separate completed-single outcome and advancement-placement predicate. D:180–216, 485; A:44–48.

### L2 — missing ruled invariants

- **F15 — missing rows, MATERIAL.** There is no row for the packer’s per-cell ordering/balance requirement, only index validity and a drift threshold. H:9 rules equal mean envelope index as the ordering invariant; D:115–116, 167–176 address different properties. State how the later registered tolerance changes that earlier invariant before testing an ordering objective.

- **F15 — missing whole-block and single outcome rows, MATERIAL.** (W) requires completed whole-block blocks to keep their window, with `late: true` and culprit status above prediction; INV-30 explicitly leaves the whole-block stage open. (N) distinguishes advancing singles from “any other uncompleted or not-started” singles, but no row states what happens to a completed single at or below its bound. Add mechanically checkable rows after OP-14/15 are ruled. D:188–195, 205–216; A:44–48.

- **F15 — missing gate obligations, MATERIAL.** No invariant/field row accounts for all ruled constants in the closed CONSUMED/CARRIED sweep, their AP-5M values, module-attribute patching, and the no-literal-duplicate scan. The proposed field table itself says several constants have no home. Add explicit rows or obtain the OP-01 CARRIED amendment. D:310–313, 447–449, 516–541; B:52; A:56.

### L3 — data contract

- **F16, BLOCKER:** §2.0 and §2.4 need an attempt/placement record for historical `reserved_s`; one mutable Block cannot describe both the initial and whole-block captures. D:273–280, 348–359, 370–372; A:44, 52.
- **F16, BLOCKER:** §2.6–2.7’s `event.sha256` derivation contradicts “resulting `sha256`,” and the root-null `registered_sha256` requires an unruled `reduce` exception. D:384–404; A:54.
- **F16, MATERIAL:** §2.0’s active-envelope `pos` and §2.3’s proposed `spread_exceeded` map cannot establish a *counted* window for pending items. Define the executed evidence and its handoff at reducer entry. D:279–280, 334–337, 475–477; B:71, 73; A:52, 58.
- **F16, MATERIAL:** §2.2’s `float`-only predictions refuse integer JSON seconds allowed by the stopped registration’s numeric domain without a ruling to narrow it. Preserve the exact accepted numeric representation for digest reconstruction, or cold-rule float-only input. D:278, 317–319, 462; B:58.
- **F16, MATERIAL:** §2.1’s exact per-arm maps retain values for unselected arms whose only cited use is validation-only coherence. The closed CARRIED list has no home for them. Resolve OP-30 in the gate and field rows. D:298–305, 465, 525–530; A:56.

The four keys singled out by A:65—`late`, `reserved_s`, observations, and `events`—are present in §2.3–2.6 (D:333, 354, 359, 372, 386–390). Their **derivation and history**, rather than their omission, cause the findings above.

### L4 — picks on every open point

**R** means representation-only; **S** means the choice adds to, weakens, or reinterprets a ruling and needs a cold gate. AGREE/DISAGREE compares my pick with the draft’s.

| OP | Class | Position and reason |
|---|---|---|
| 01 | S | **AGREE.** Add the downstream constants to a ruled CARRIED list; the current closed list cannot cover them on A291 paths. D:447–449; A:56; B:52. |
| 02 | R | **AGREE.** Remove single-valued Registration fields and pin module constants to schema. D:457; B:52. |
| 03 | S | **AGREE, subject to ruling.** String JSON keys make serialization stable, but refusing integer in-memory keys narrows accepted input. D:458; B:53. |
| 04 | S | **DISAGREE.** Use a flat ordered ID list; nested lists change the ruled digest preimage. D:459; B:53. |
| 05 | S | **AGREE.** Equal level lengths fit the singular `n_per_level`; a short final block still counts, but both are acceptance choices to write explicitly. D:460; B:53, 69. |
| 06 | S | **AGREE as a proposed new contract.** Consecutive slicing and ID syntax make replay deterministic but are not implied by paired membership. D:461; B:69; A:54. |
| 07 | S | **DISAGREE.** Accept finite JSON numeric seconds while retaining their canonical numeric form; rejecting integers strengthens the input rule. D:462; B:58. |
| 08 | R | **AGREE.** Rebuild the prediction map from initial parents retained in the roster and compare its digest. D:463; B:58; A:52. |
| 09 | R | **AGREE.** Once extra models and items are refused, hashing the whole exact map is equivalent to hashing its registered restriction. D:464; B:58. |
| 10 | R | **AGREE.** Keep derived `claim_ready`; it is an expressly ruled flag, not a copied Registration value. Keep the narrower producer/consumer checks from F03. D:450–451; C:66; B:30. |
| 11 | R | **AGREE.** Put `late` on the block and decisions in recorded observations/events, provided attempt history remains reconstructible. D:469; A:20, 44, 54. |
| 12 | S | **DISAGREE.** The null-field preimage is not the resulting roster digest. Define a non-circular resulting-digest encoding before freezing events. D:470–472; A:54. |
| 13 | S | **DISAGREE on the root exception.** Dropping redundant `parent_sha256` is fine; root-null plus root reduction changes the unconditional replay assertion. D:473; A:54. |
| 14 | S | **AGREE provisionally.** `cut_off` splits under (T); `not_started` follows (W)’s no-culprit terminal route. The within-prediction cut-off still conflicts with (W), so this cannot be final without a judge. D:452–453; A:44, 46. |
| 15 | S | **DISAGREE.** A completed single above worst case advances under (N); its prior attempt cannot simultaneously be a kept counted window and a voided retry window. Rule which evidence is retained. D:485; A:48. |
| 16 | S | **DISAGREE.** An accepted innocent reschedule without a culprit violates (N)’s causal bound immediately; waiting for the aggregate limit does not cure it. Seek an explicit fault outcome/edge. D:486; A:48, 56. |
| 17 | S | **AGREE provisionally.** Apply later eligible placement to initial-stage innocents, but its lack of a bound and its effect on (X) need a ruling. D:487; A:44, 58. |
| 18 | S | **AGREE.** Keep observed envelopes fixed, idle captures idle, and whole-block retries alone; the eligible-target rule should be stated explicitly. D:488; A:44, 50; H:7. |
| 19 | S | **DISAGREE.** Enforce fixed observed envelopes and placement above each reporting envelope; strict event-index order adds a refusal absent from (E). D:489; A:50. |
| 20 | R | **AGREE.** Count distinct singles created so far across the roster at seal time. D:490; A:48. |
| 21 | R | **AGREE on the capacity basis.** Count historical active and voided placements using each placement’s reservation; a current block value is insufficient. D:474; A:52. |
| 22 | S | **AGREE provisionally.** Initial `reserved_s = predicted_s` matches stopped packing but is an unruled acceptance rule. D:491; B:30; A:44. |
| 23 | S | **DISAGREE.** Keep the ruled counted-attempt position; distinguish a planning estimate from executed drift. Post-capture flag versus refusal needs a ruling from these authorities. D:492–498; B:73; C:70; A:52. |
| 24 | S | **DISAGREE.** A pending block is not a counted window. Count fully evidenced parents and distinct capture envelopes at the appropriate completed stage. D:475–477; B:71; A:58. |
| 25 | R | **AGREE.** Per-item typed refusals and an attempt key support completeness and the terminal-window join. D:478; A:44; B:79. |
| 26 | S | **AGREE provisionally.** The stopped insertion rule is deterministic, but the particular idle-worker model and balance policy are not ruled. D:479; H:7–9. |
| 27 | R | **AGREE.** Consecutive indices encode represented fixed-pitch capture positions, including idle positions. D:480; H:7–9. |
| 28 | S | **DISAGREE.** (G) literally asks for an executed violating witness for every magistrate row on every closed path. An `n/a` escape requires amendment; use entry/exit injection where feasible. D:503–505; A:56. |
| 29 | S | **DISAGREE.** A helper may be useful, but its test cannot substitute for an executed witness at the actual `reduce` entry named in (S)/(G). D:506; A:52, 56. |
| 30 | S | **AGREE with the selected-arm restriction as a proposal.** Otherwise unselected-arm entries need a new ruled CARRIED home; registration validation alone cannot establish consumption. D:465; A:56. |
| 31 | R | **DISAGREE.** Do not put unruled plausibility warnings in the independent contract checker’s output; keep optional diagnostics outside its violation result. D:499, 425–436; A:56. |
| 32 | R | **AGREE.** `tests/support/` preserves checker independence; checking registration coherence independently is useful. D:507, 410–428; A:56. |
| 33 | R | **AGREE.** The proposed schema bumps distinguish changed wire formats, subject to ordinary schema pinning. D:481; B:52. |
| 34 | S | **DISAGREE that R11 binds from the listed authorities alone.** The refuter asked for an after-capture status; obtain or cite the adopting ruling before using `drift_exceeded` as acceptance. D:508, 260; C:70; A:52. |

### L5 — the three flagged inconsistencies

- **OP-01: genuine conflict.** The ruled constants include estimator/reducer constants, while A:56 requires every ruled constant to be CONSUMED on the A291 closed paths or be in a closed CARRIED list that omits them; D:447–449 identifies the gap. **Cold question:** “Must `merge_order`, `min_correct`, `holm_m`, and `cap_bound_fraction` be added to CARRIED with named consumer lanes, or are constants outside A291’s modules exempt from this A291 sweep?”

- **OP-10: not a genuine conflict.** C:66 explicitly requires the derived `claim_ready` flag; B:30 prohibits roster *copies* of registered values. A derived Boolean is not a copy of `mode`, although D:33’s name ban wrongly treats it as one. **Clarifying question, if desired:** “Does ‘no roster copies’ allow the explicitly ruled derived `claim_ready` flag?” The answer should be yes. D:450–451.

- **OP-14: genuine conflict.** For a whole-block `cut_off` within prediction, A:44 directs a no-culprit uncompleted block to `unattributed_overrun`, while A:46 says a whole-block retry advances to split whenever its attempt did not complete. `not_started` also collides with the split clause’s demand for recorded elapsed time. **Cold question:** “For a whole-block retry reported `cut_off` at or below prediction, and for `not_started`, which edge wins—`whole_block→single_problem` or `whole_block→unattributed_overrun`—and what elapsed value, if any, is recorded?” D:452–453.

## Residual risk

This was a read-only contract review. I inspected the pinned text and stopped code; I did not execute a checker, mutate a roster, or validate a future implementation. The worktree remained clean at the same detached HEAD.