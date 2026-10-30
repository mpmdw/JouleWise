VERDICT: ACCEPT_WITH_FIXES

# RC-CMP9-FABLE-REV: delta review of RC-CMP-9 (`0d317afd4..f9f86869e`)

Seat RC-CMP9-FABLE-REV, Fable 5.1, cloud, synthetic only; no real block-5/6/BYTES data opened or searched for.
Branch `review/2026-10-30-rc-cmp9-fable-rev` at `f9f86869e`. `/usr/bin/python3.13`, `TMPDIR=/tmp/rcnine_fable/tmp`
(outside the checkout, no float-like token). Evidence in `.codex-report/rc-cmp9-fable-rev/`. Producers on
`origin/main` (`b5_analysis/{disclosures,sensitivity,bracket,dry_run}.py`, `analysis_engine/{artifact,__init__}.py`,
`results_fill_adapter.py`, `dominance_closeout.py`, `scripts/build_results_fill_input.py`) exported with `git show`
and read as text only. Reviews read: my RC-CMP8-FABLE-REV and `review/2026-10-29-rc-cmp8-opus-rev`.

**Summary.** The walk I recommended is implemented as specified and every RC-CMP-9 claim I re-executed holds:
`Ran 362 tests` / `OK (skipped=18)` / exit 0 (`suite.out`); my deletion sweep gives exactly the report's 4982 / 735 /
11 (`sweep.out`, `classify_prior.out`); Opus's `probe_cmp8.py` at this head: confirm 0 exit-0 of 50, joint2 and loo
all non-zero, relabel 4081 tried and 0 exit 0 (`opus_probe.out`); my RC-CMP-8 probes S1.a/c and S1.l-n exit 1,
G7 unchanged (`probes_prior.out`). The table is a function of the seven pinned registry files and the literal
constants alone (`closure.out`), every entry is keyed by the registry or a constant, every registered condition is
read on both sides, every selector and closed list fails closed, and 20 of 20 producer mutations break a pin
(`pins.out`). **No check's existence, key or route depends on what one side printed.** What remains is fail-closed:
value rows built outside their registered condition over-refuse when both sides refuse (F1), and three verdict-only
words are required as keys but bound to nothing (F2). No false pass found.

## Findings (ranked)

**F1 (MEDIUM, fix). Two registered conditions over-refuse when false on both sides, outside the table.** The table
switches its conditional entries off correctly (0 `expected/` rows DISAGREE in every case), but the family rows are
built unconditionally and compare `None` against `None`:
- `floor_computed` false on both sides (the extraction cell prints no floor and no `floor_composition` line, the
  recompute's `floors/<key>` is `below_minimum`, `independent_recompute_b5.py:1175`): `compare_floors`
  (`scripts/compare_b5_recompute.py:1710-1722`) emits 13 `floor_j` and 2 `count` rows `(None, None)`, exit 2
  (`probes.out` P3; unwidened `probes_extra.out` X3).
- `ratio_computable` false on both sides (bare `magnitude_ratio` line, `disclosures.py:522`; recompute ratio `None`):
  `compare_disclosures` (`:2439-2443`) emits 3 `descriptive_ratio` rows `(None, None)`, exit 1 (P4, X4).
- `reported_computed` false on both sides: 17 rows, exit 2 (P1, X1, X5). This one the report declares (OPEN ISSUE 1).
The one-sided cases are all non-zero with table rows named (P2.a/b, P3.a/b, P4.a/b). Fix: build the value rows of a
conditional family under the same `condition_holds` the table uses; when both sides refuse, compare the status
words and build no value rows (the same fix closes OPEN ISSUES 1 and 2).

**F2 (LOW). The verdict's kept-sampling words are required as keys and bound nowhere.** `sampling/kept_n = 5`
against `n = 9` exits 0 (P6.b); `sampling/removed_block_ids = []` exits 0 (P6.a; sweep: its member deleted exits 0);
the not-kept block's `included = null` exits 0 (P7.a). The fill's copies are bound (`COVERAGE` `:2760`,
`registered_block_ids` `:1904`); the engine forbids all three (`artifact.py:1887`, `:2061`). Fix: compare the
verdict's `kept_n` to the recompute's `n`, its `removed_block_ids` by position with `registered_block_ids`, and
require `_BLOCK_KEYS` (`artifact.py:200-206`) on each `bundle_blocks/blocks` item (the table requires the list only).

**F3 (LOW). One pin precondition is unpinned.** `FILL_SHAPE`'s 10 extended contrast keys and gamma's
`finalized_manifest`, `floor_artifact`, `exclusions_sha256` print only when the adapter runs extended
(`results_fill_adapter.py:99`: `any(value is not None for value in (finalized_manifest_raw, floor_artifact_raw, …))`).
Block 5 passes both (`scripts/build_results_fill_input.py:86-87`), but `test_fill_shape` pins the build script's
campaign keys only. A build script that stopped passing them would make the table over-refuse with pins green.
Fix: `assertIn("finalized_manifest_raw=manifest_raw", build)` and the floor line.

**F4 (NOTE, carried).** `Custody.step_ok` has no caller (F6). The fill's identity pins are IDENTITY-uncovered by
rule: `finalized_manifest/file_sha256 = "9"*64` exits 0 (P8) although `REGISTRY_PINS[MANIFEST]` is the registered
digest of the same file; binding it is cheap but outside this round's class.

## Answers

**1. Sweep.** `sweep.py` (the RC-CMP-8 walk, run in parallel, identical output format): 4982 single deletions over
every L9 input and the recompute on the producer-complete base (1933 at `0d317afd4`; the fixture grew), exits
`{1: 1606, 2: 2641, 0: 735}` (831 exit 0 before). My RC-CMP-8 classifier (`classify_prior.out`): 724 declared, **11
producer-unconditional** (297 before), each declared in RC-CMP-9: `flag_count` ×3 and `machine_absent` ×3
(NEEDS_RULING 4), `attempt_count/causes/0` ×3 (NEEDS_RULING 3), the recompute's own `battery_assist/<cid>/status` ×2.
A fresh class-by-class classification against this report's declared classes (`classify.py`, `classify.out`): 735 →
**0 UNDECLARED** (514 text/label/restricted; 124 verdict-only engine internals; 21 + 14 kept-units record fields;
18 recompute unread fields; 12 estimator internals; 7 limitations/reason codes; 2 identity pins; 21 NEEDS_RULING
3/4; 2 verdict `removed_block_ids` members). `sweep_groups.out` lists the 90 path groups. The declared verdict-only
items are F2.

**2. Constructors.** `constructors.md`: the 29 table families with the key source of each L9 locator and recompute
item, and the 17 row-constructor sites outside the table. Output-derived existence in the table: **none**; the five
condition kinds read both sides and switch a check on, never off (P2, P3.a/b, P4.a/b, P11.b). The one selector read
from printed text (`@ratio`, `:1060`) fails closed: an `R` line retexted `R_cm` is MISSING for its entry and
`unexpected/` for the other, exit 2 (P5.a/b). Closed lists: unregistered id refuses (P12.a/b), duplicate refuses
(P10.a/b), invented word refuses (P9.a), joint leave-one-out drop DISAGREEs (P11.a). The two output-keyed universes
left are the ones the report names: the run family (G7.b/b2 exit 0, bound by `exclusions_rederivation`, G7.b3 exit 1)
and the machine lines (NEEDS_RULING 2, `TABLE_CONDITIONAL_LINES` `:1047`); `load_correlated_*` lines are
producer-conditional and uncovered by the LOAD_LINE rule (P9.b exit 0, by design).

**3. Completeness.** `census.py` resolves every table locator's nested key paths for the 59 disclosure line words
against the producer's `_item` calls, with `**` expansions and dict-valued keywords resolved from the producer's
builders (the test covers literal keywords one level deep only): **0 over-refusal risks, 0 gaps, 0 unresolved**
(`census.out`); the 23 producer words outside the table are each printed under a producer branch (conditional lines)
or are the sensitivity rows' variable word, which is pinned. The fill, verdict and sensitivity shapes are pinned
literal-for-literal (`ProducerPinTests`), and the sweep is the empirical census of the rest: every deletion of a
required nested key exits non-zero. The table's unconditional output equals the producer's for this registry up to
the declared items (NEEDS_RULING 3/4, machine lines) and the per-block keys of `bundle_blocks/blocks/*` (F2).
Pins: `pins.py` mutates each producer in memory (a key added or removed from `_ESTIMATOR_KEYS`, `_LOO_ROW_KEYS`,
the adapter's row, extended keys, gamma, the build script's campaign, the record's sections, `_cell_values`,
`_reported_values`, `BMax`, the closeout census text, battery codes, trigger keys, the tripwire tuple, the arm-gate
count; a line renamed; a line made conditional; a literal keyword added): **20 of 20 caught**, each by the pin that
names that source (`pins.out`). The pins read the right sources (artifact literal sets; `adapt_claim_verdicts` row,
`target.update`, `output["gamma"]`; `produce_disclosures` result, `_cell_values`, `FIXED_SENTENCES`, `_ruling_lines`,
`_monitor_lines`, `_trigger_values`; `sensitivity_pass` and its three builders; `bracket.BMax`; `dominance_closeout`
census strings; `campaigns[pack]`). The one unpinned precondition is F3.

**4. Over-refusal.** `with_neg8 + with_references + with_sensitivity`, widened and unwidened: exit 0, 1346 rows,
**0 non-AGREE**, 250 active table entries (256 less the not-kept block's 2 rows and the 4 refused variants) (P13).
Each registered condition false on both sides, widened and unwidened: `loo_block_kept` passes (the base's block 1);
`reported_computed`, `floor_computed`, `ratio_computable` over-refuse outside the table (F1; the table passes in each);
`cross_window` (phase n < 2) not exercised: n < 3 breaks the leave-one-out rows first (OPEN ISSUE 3). RC-CMP-8's
S3.b/S3.c still exit 2/1 (OPEN ISSUE 2, declared). `REGISTERED_SOURCES` is closed (`closure.out`): the registry reads
exactly the seven pinned files, which are the seven named `configs/campaigns` entries; `analysed_windows.json` is
named and never read; `expected_checks` and the six helpers it reaches read only module constants and its one
`registry` argument; all 39 `add(` sites are inside `expected_checks`; two independently loaded registries give
equal tables of 256 entries.

**5. Closed?** **Yes**, for every check the comparator makes. No table entry, row constructor, selector or route
exists, is keyed, or is routed by what one side printed: the registry and the literal constants key every check,
every conditional entry's registered condition is read on both sides and any one-sided omission is DISAGREE, the one
text selector and the closed lists fail closed, and the per-leaf coverage is bounded by the table's claims
(`not_in_table`). The evidence is answers 1-4 plus Opus's 4081 identity relabels with 0 exit 0 and my 661 gate-passing
relabels with 9 exit 0, all `machine_absent` (a bare sentence) into another bare word (`probes_prior.out`). The two
universes the report itself puts outside the table are the design questions for Ed, as RC-CMP-9 states: the
whole-machine member and summary lines (paired over three sides, a three-way omission passes; registering them needs
the plan trees' metered members per window) and the step-2 run family (G7 joint drop, bound only by
`exclusions_rederivation`). Neither is a defect the comparator can close from a registered source it has today.

## Evidence (`.codex-report/rc-cmp9-fable-rev/`)

- `suite.out`: the brief's command at `f9f86869e`, `Ran 362 tests` / `OK (skipped=18)` / exit 0 (497 s).
- `sweep.py`, `sweep.out`, `sweep_groups.out`: answer 1; `classify.py`, `classify.out` (this head's declared classes),
  `classify_prior.out` (the RC-CMP-8 classifier).
- `probes.py`, `probes.out`; `probes_extra.py`, `probes_extra.out` (unwidened; the recompute's bare status word):
  P0-P13, X1-X5.
- `probes_prior.out`: my RC-CMP-8 `probes.py` (on `review/2026-10-29-rc-cmp8-fable-rev`) re-run at this head.
- `opus_probe.out`: Opus's `probe_cmp8.py confirm | joint2 | loo | relabel` at this head (`PYTHONPATH` = checkout).
- `pins.py`, `pins.out`: 20 producer mutations against the pins. `closure.py`, `closure.out`: answer 4.
- `census.py`, `census.out`: answer 3 (`python3.13 census.py <origin/main disclosures.py exported as text>`).
- `constructors.md`: answer 2.

## Pruning tally (gate policy rule 9)

| gate | ran | caught_number | caught_session_refusal | evidence |
|---|---|---|---|---|
| suite at `f9f86869e` | yes | no | no | `suite.out`, 362 OK |
| RC-CMP-8 probes re-run (mine S1-S3, Opus confirm/joint2/loo/relabel) | yes | no | no (every RC-CMP-9 claim confirmed) | `probes_prior.out`, `opus_probe.out` |
| single-leaf deletion sweep + fresh classification | yes | no | no (0 undeclared) | `sweep.out`, `classify.out` |
| conditional entries: both-sides-false and one-sided | yes | no | yes (F1: exit 2/1 on a sound window) | `probes.out` P1-P4, `probes_extra.out` |
| selectors, closed lists, duplicates, joint drops | yes | no | no (all fail closed) | `probes.out` P5, P9-P12 |
| verdict-only words (keys required, values unbound) | yes | yes (P6.b `kept_n` 5 vs 9 exit 0) | no | `probes.out` P6-P8 |
| nested-key census, pin mutations, source closure | yes | no | no (F3 is a pin gap, not a refusal) | `census.out`, `pins.out`, `closure.out` |
