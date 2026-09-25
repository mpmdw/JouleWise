The review is finished. Nothing in the lane stops the merge. But one design problem in `pack` should be dealt with before the first registered (claim-bearing) night.

**Verdict:** safe to merge as one PR. Two fixes should come first or alongside the merge: register the new test modules' run times with CI, and add `RecursionError` to the packer's exception handling. The ordering problem (R6-1 below) gates the first registered night, not the merge.

## (1) Row 6: things a claim-bearing night could trip on

**R6-1 — should_fix; blocker for the first registered night unless the reducer controls for it.** `pack` runs difficulty levels 4–5 in the second half of the night for both models (`joulewise/scored_packer.py:365-382`). It fills buckets with a first-fit loop that goes level by level, so levels 1–3 take the early envelopes and levels 4–5 get pushed later. On the headline difficulty axis, that means level differences get mixed up with anything that drifts over the night (heat soak, ambient temperature). Nothing in the contract checks where a level falls in the night. The only drift check (`drift_lever_slots`) compares the two models against each other within a level. Every test fixture gives both models the same speed and sets `budget_j=1e4`, so nothing exercises this.
- Witness: `/tmp/278ebc9e/ocr/lever_probe.py`, run at n=20, block_size=4, cap=12, symmetric speeds. Mean envelope index by level: 8B model `{1:4, 2:4, 3:4, 4:14, 5:14}`, 1.7B model `{1:5, 2:5, 3:5, 4:15, 5:15}`, out of 20 envelopes.
- The same probe with the 8B model 3× slower (predictions 3.0 vs 1.0, worst 6 vs 2, cap 24) gives a planned lever of `{1:1, 2:1, 3:7, 4:7, 5:12}`. With the 8B model 2× slower it is `{…, 4:7, 5:7}`. In registered mode that is a legal input that `pack` refuses with `inv_28` whenever `max_gap < 12`. A lever near 0–1 is possible: envelopes only need to hold one model each, so an ABBA order would keep the two models' means close.
- The strict 8B/1.7B alternation (`:376-380`) also sets a floor of about 1 on the lever even when both models run at the same speed.
- Cure: the contract says the search is the implementation's choice (§3.1 step 4), so this is within the lane's latitude. Order parents so every level's mean position sits near the middle of the night (for example, rotate the level order in each bucket), and fill buckets for the two models in a balanced order. Add a fixture where the models run at different speeds and a check that level position is not tied to night position. If the lead would rather handle this in the reducer (for example, envelope index as a covariate), write that down before arming the night. No rosters exist yet, so changing the arrangement costs nothing now.

**R6-2 — should_fix, as an obligation on the runner (not a packer bug).** Every `requeue_overrun` call replays the whole night's history (`:414`). During replay, each `_seal` → `_structure` does a linear search through all placements for every observation (`:244`), so the total cost grows roughly with the cube of the number of events.
- Sol's measurement was 1.42 s for the last call at 131 events and 90 s in total. This is already recorded as a known cost.
- The part not recorded anywhere: if the runner calls `requeue_overrun` between envelopes on the measured machine, that CPU burst lands in the next envelope's energy unless it finishes inside `offset_s`/`guard_s`.
- Cures:
  - The runner (A292) must call it outside envelope interiors, or budget for it.
  - A one-line index cut: `{(bid, ix): p}` built once in `_structure` instead of `next(...)` inside the loop.

**R6-3 — nit (runner obligation).** `verify_executed_roster` refuses any roster with a loaded envelope that was never reported (`:494`, as ruled in FT-13). A night cut short (census failure, window ran out) can still be reduced: the runner reports each remaining envelope as all `not_started`. An event with no culprit makes every block a terminal `unattributed_overrun`, so no new envelopes are created. A292 should write this down as the close-out procedure. Otherwise a truncated night throws away every window it captured.

**Checked and clean:**
- Decision table and effects match contract §3.2.
- Capacity sums are added in the same order in `_eligible`, `_structure` and the `pack` buckets, so floating-point results agree.
- Culprit limits (1 and 2) can be reached by legal histories.
- A block's placements never share an envelope index, so the `(block_id, envelope_index)` placement key is unique.
- The packer and the checker agree on the executed lever, including partially counted parents (ruled in A291-POP-1).
- The same history replayed twice gives the same digests (Sol's V2).

## (2) Row 8: overbuild and whether it merges as one PR

- **Merge-ability: yes, one PR.** The lane is self-contained: 665 production lines, and nothing outside the lane imports the scored modules yet. The `D docs/process_traces/2026-09-24-interactive-4b/17-structural-consult-fable.md` line in `git diff origin/main e3769062` is not a real deletion. `origin/main` moved to `25cde215` after the branch's merge-base (`2bfcc7bb`), and that commit is docs-only. Merge or rebase before opening the PR so the diff doesn't show a false −40.
- **should_fix — CI cost.** None of the six new test modules is in `scripts/test_timings.json`, so `quick_suite` leaves them out as "unknown weight" and the hosted shards get the conservative placeholder weight.
  - Forgery module: 585 s, from the gate evidence.
  - Stress module: over 6 minutes. My timing run was stopped at about 7 minutes without finishing.
  - Fuzz module: 51 s. `test_scored_packer` takes about 7 s per test for a single-test invocation, because `setUpClass` builds 8 cases each time.
  - Together that is at least 17 minutes of new suite time against a shard target of about 14 minutes.
  - Cure: add the timings, then either declare the forgery module and the 300×2 stress run as exclusive/split, or put the exhaustive campaigns behind an environment flag. The campaigns are the 1,868-roster legal corpus, the 121 pairs and the 1,331 triples in `test_scored_ownership_forgery.py:126-236`, and `test_seeded_300_registration_sequences`. Keep the named regressions, `test_named_seal_regressions` and the edge-coverage tests in the ordinary tier. Both campaigns have already served as gate evidence; running them on every push adds no new evidence.
- **nit — duplicated mutation operators.** `tests/test_scored_packer_fuzz.py:42-125` (op1–op10) and `tests/scored_ownership_generator.py` (about 11 operators) are two parallel families that overlap in purpose: `op5_remove_single`/`drop_single`, `op6_flip_superseded`/`flip_superseded`, `op3_drop_terminal`/`drop_terminal_entry`. The generator versions are the cleaner ones; for example, `drop_single` removes every reference to the block, while `op5` only pops it from the list. Merging the two families is a follow-up job, not a reason to hold the merge, because both backed separate gates.
- **Not overbuild:** the 865-line independent checker (the contract requires it), the oracle (60 lines) and the case generator (119 lines). No dead code in the production modules: every private helper is reached.

## (3) The two open lens items

- **RecursionError — fix before merge; it's a one-line change.** The input doesn't matter under the D-161 threat model: only an adversary can supply deep nesting, and `json.loads` fails first on such input anyway. What matters is that the typed-refusal contract is "raises only `PackingRefusal`". A292's reducer will be written against that, and there's a fuzz test named `test_a_entry_points_return_or_raise_packing_refusal`.
  - The problem is wider than the `sha256` field. Witness `/tmp/278ebc9e/ocr/rec.py` prints `sha256 RecursionError` and `item RecursionError`: 1,200 levels of nesting in `blocks[0].items[0]` escapes the same way. Validating only the `sha256` field, as the lens proposed, would not cure it.
  - Cure: add `RecursionError` to the except tuples at `scored_packer.py:293` and `:170`, and map it to `inv_52`. `_digest` already runs inside that `try`, and `requeue_overrun` goes through `_seal` first, so both entry points are covered.
  - Re-gate cost: this only touches the exception path, so it cannot change a legal roster or any digest. Re-running the two named seal tests and the fuzz module (about 1 minute) is enough, not the whole gate.
- **`-> dict` on `_ownership` (`:70`) — put it in the same commit if the RecursionError fix goes in, otherwise a follow-up.** It is literally what the ruling says and has no effect on behaviour.

All probes ran from `/tmp/278ebc9e/ocr/`, and the worktree was left untouched. I read the round-3 texts 85/95 and the mutation-kill (100b) and forger (104/106) reports only as far as the two lens reports cite them; I didn't re-run their evidence.
