# Successor preparation checklist (frozen inputs remain read-only)

The current operating mode is `METHODS_DIAGNOSTIC`: the selector validates and
copies `docs/paper/draft-v2-skeleton.md` unchanged. It supplies no empirical
values. See [current selector guidance](../fill-rehearsal/branch-selection.md).
The registry's Submission disposition overrides its historical fill tables.
`RETIRED_FALLBACK` rows have no submission placement or rendering permission.
TR-01 is a fixed transfer limitation; DS-34 remains an unissued locator hold.
Prospective counts are design requirements, not observed counts.

Migration preparation does not constitute empirical fill. Successor operations
are PENDING adopted S1/S6 contracts and live campaign-fill adjudication.
The [migration inventory](successor-migration-inventory.md) records unresolved
semantic targets and the reconciliation gate. Neither the parked
[structural sheet](structural-edits.md) nor the [retensing plan](retensing-plan.md)
is an executable batch plan. Their 2026-08-31 worklist (3 blockers / 13
should-fixes) requires live adjudication before any real text substitution.
`docs/paper/draft-v1.md` and retained evidence are read-only.

## Current desk operation

1. Validate/copy the methods/diagnostic successor using only
   `--outcome METHODS_DIAGNOSTIC`; use a new output outside frozen inputs.
2. Preserve the historical headline, fixed transfer limitation, diagnostic
   era labels, and synthetic labels. Keep the prospective protocol separate.
3. Run the named migration regression module for this preparation:
   `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_successor_migration`.
   This desk acceptance does not run external-corpus replay or collect data.

## Future batch gates — pending, in order

1. **Authority and fresh successor copy.** Reconcile adopted S1/S6 outputs with
   every inventory disposition before final closure. Record their exact paths,
   commits and hashes. The lead names the clean source commit and successor;
   create a fresh working copy in a new, non-overwritten custody directory.
   Never edit the frozen draft. A copied frozen draft is not automatically the
   successor selected by the current contracts.
2. **Complete supplier and placement checks.** Census all active placements,
   omissions and repeated physical sites against the adopted contracts. Exclude
   retired rows; resolve missing suppliers with STOP_FILL. Eventual empirical
   suppliers must use D-173 `joulewise.paper_custody.open_paper_input` under
   [paper supply custody](../../contracts/paper_supply_custody.md): role and runs
   root only, clean-Git supply map, validator-replayed frozen verified objects.
   Receipts corroborate; they do not authorize. A projection, fixture, proposed
   count or manually supplied digest cannot stand in for authenticated evidence.
3. **Input/output hashes and replacement ledger.** Before each authorized batch,
   record SHA-256 of the input working copy, adopted contracts, supplier inputs,
   renderer and template. Every replacement ledger entry names row, semantic
   target, exact before/after text, physical placement, supplier field and hash,
   units, rounding, era, adjudication and omission/refusal if applicable. Record
   output SHA-256 and ledger SHA-256; require consecutive batch hashes to join.
   No unledgered change is accepted. Keep the frozen source hash unchanged.
4. **Preserved historical replay fences.** The eventual live fill session runs
   `scripts/check_paper_replay_fence.py` before and after each batch and retains
   `COMPARED 43` / `MISMATCHES 0`. Preserve the round-7 artifact fence
   `scripts/check_paper_round7_artifacts.py`, its input identities, mandatory DX
   diagnostic standing sentence, marker ownership and placement census. Historical
   zero-placement expectations are 184 full comparisons (181 literals-only);
   the old 16-marker batch expected 200 full comparisons. These are historical
   contracts, not a new successor placement count. S6 must reconcile successor
   placements and expected tails explicitly; literals-only cannot replace full
   replay. Preserve mismatches, refusals, exact commands and outputs in custody.
   Missing external corpus means STOP_FILL, never an inferred green fence.
5. **Assembled-paper first-use and Abstract checks.** Audit the whole assembled
   article in reading order, including captions, tables and appendices, then
   the prospective supplement. Rebuild first-use locations against the read-only
   lexicon and audit ledger; test constructions at the earliest actual use,
   not the old paragraph anchor. Check operands, units, signs, sampling units,
   thresholds, figure encodings and synthetic labels from the inventory.
   Re-run `select_outcome_branches.py --check-rendered` on the final methods
   copy and require an Abstract of at most 250 words. A future different paper
   needs an adopted validator contract; relaxing today's guard is not a fill.
6. **Closure.** Require complete supplier/placement agreement, no retired fills,
   preserved replay evidence, matched hashes and replacement ledger, final
   first-use and Abstract results, and lead adjudication of every inventory row.
   Counts such as 34/36, 37/39, 53 placements, 35 pending rows and the 32-row
   dominance record belonged to the frozen workflow; rederive the successor
   census instead of importing them. Real text substitution remains pending
   live fill adjudication even after preparation checks pass.

## Retained replay environment note

**2026-09-08 addendum — ICLOUD-BACKUP-PROBE-01.** The replay fence and both
round-7 producers use the following optional backup-discovery policy.
`JOULEWISE_BACKUP_ROOTS` is an `os.pathsep`-separated list of optional
backup roots; an empty value disables all backup roots. If unset, it defaults
to `/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup`.
Each (root, call) has one cumulative 2 s budget for `is_dir` and both globs.
An unresponsive or responsive-but-slow root exceeding that budget is skipped:
it contributes zero candidates and emits a `backup_root_unavailable` stderr
line. This replaces the prior unbounded hang. Retained artifacts are byte-pinned;
a skip fails closed at the pin check if no matching candidate remains. This
policy grants no desk replay gate.
