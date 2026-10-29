VERDICT: ACCEPT_WITH_FIXES

# RC-CMP7-FABLE-REV: delta review of RC-CMP-7 (`1134bbf58..c372211bf`)

Seat RC-CMP7-FABLE-REV, Fable 5.1, cloud, synthetic only; no real block-5/6/BYTES data opened or searched for.
Branch `review/2026-10-29-rc-cmp7-fable-rev` at `c372211bf`. `/usr/bin/python3.13`, `TMPDIR=/tmp/claude-0/rcfable`
(outside the checkout, no float-like token). Evidence in `.codex-report/rc-cmp7-fable-rev/`. I designed the input
gate in the consult; I read this round against that design as a fresh reader. Producer code (`origin/main`
`disclosures.py`, `sensitivity.py`, `bracket.py`, `kept_units.py`, `dry_run.py`, `dominance_closeout.py`) and the
recompute were read as data only.

**Summary.** G7, F2 and F3 hold under every executed witness: every one-sided drop or add of a run is DISAGREE
(answer 1), every claim word the fixture prints refuses when wrong, the registered block ids and numerator fields
route, the real-shape census passes the line gate, and the suite is green (`suite.out`: `Ran 303 tests` /
`OK (skipped=18)`). One F2-class route survives: the two window claim rows (`below_screen_bound/below`,
`neg8_screen/decision`) exist only when L9 prints the line, so a wrong NEG-8 screen word relabelled
`adapter_continuity`, or either line dropped, exits 0 (F1). The fix is four lines and is demonstrated. Nothing
found changes the readiness run's outcome on a sound window.

## Findings (ranked)

**F1 (MEDIUM, fix in this round). A window claim word is compared only if L9 prints its line, so a wrong word
exits 0 by relabel or omission.** `scripts/compare_b5_recompute.py:1436-1441`: `if "below_screen_bound" in
claims:` and `if "neg8_screen" in claims:`. The row's existence is read from the checked document, which is the
value-derived route G7 forbids for keys. `adapter_continuity` has the same producer key set as `neg8_screen`
(`:617`, `:628`, both `("decision",)`), and its word is a `HARVEST_WORDS` exemption (`:1842`), so the line gate
admits the relabel. `probes.out`:
- F2.a control, `neg8_screen` passed on both sides: `exit=0`, row `('passed', 'passed', 'AGREE')`.
- F2.b L9 prints `failed`: `exit=2 refused=step11_unmapped_fill`, `row_disagrees` (the word is compared when present).
- **F2.c the `failed` line relabelled `adapter_continuity`: `exit=0 fails={}`.**
- **F2.d `neg8_screen` line dropped, recompute holds a screen decision: `exit=0`.**
- **F2.e `below_screen_bound` line dropped, recompute holds `b_op`: `exit=0`.**
- The relabel sweep in `probes.py` (every fixture line into every word whose producer key set admits it, 58
  gate-passing relabels) exits 0 in 43 cases, all harmless: bare sentences among bare words, and `stored_status`
  into `cells/reported_cell` (exempt on both ends). F2.c is masked there only because the sweep's base carries a
  `battery_temperature_sentence` line, whose `neg8` leaf binds to the `neg8_screen` row (`no_row` when the row is
  gone); the producer prints that line only when a stage is flagged (`disclosures.py:1064-1068`), so the mask is
  not there on every window.
- Fix: key both rows on the registered packs. The producer prints both lines on every window unconditionally
  (`disclosures.py:1100` and `_reference_lines` `:952`, called per pack at `:1093`), and the recompute holds
  `b_op_s` and `neg8.screen_decision` for every pack (`independent_recompute_b5.py:935`). `patch_demo.py` does it on
  a scratch copy (`patch_demo.out`): control `exit=0`; F2.b `exit=2`; F2.c, F2.d, F2.e `exit=1 fails={'outcome_word': 1}`.
  The base fixture then needs a NEG-8 result and a `neg8_screen` line per pack (as `with_neg8` builds), and
  `neg8_screen` belongs in `COMPARED_LINES` of `test_rc_cmp7.py`.

**F2 (LOW). The two by-construction booleans accept a printed `False`.** `:1862-1865` exempts
`mean_and_half_width_equal_primary` and `bound_independent_values_equal_primary` as strings or booleans. The
producer can only print `True` (`sensitivity.py:291-304`, `:338-346` refuse otherwise), so a `False` is a wrong
word that exits 0: F2.g, both words, record and block-line copy, `exit=0 fails={}`. Fix: one `c.exact` row each
against the constant `True` (or derive them from the compared values as `equals_primary` is).

**F3 (LOW, carried from RC-CMP6-FABLE-REV F3, outside this brief).** `Custody.step_ok` (`:331`) still has no caller.

**Notes (no fix required).**
- The recompute's `screen_decision` is the harvest's own re-screen word (`independent_recompute_b5.py:935`), not a
  re-derivation; the `neg8_screen` row checks L9's copy against the recompute's copy of one stored input. The bound
  terms behind it are compared numerically.
- `widened` is derived by `b_sens != b_op` (`:1220-1221`) where the producer uses `>` (`sensitivity.py:279`); equivalent,
  since `b_sens = max(b_op, B_max)` (`bracket.py:384-387`).
- `equals_primary` and `not_below_primary` are derived with `==` and `>=` over the recompute's own values
  (`:1234-1237`, `:1277-1280`) where the producer compares canonical digests (`sensitivity.py:56-59`); a one-ulp
  difference between the recompute's primary and sensitivity values where L9's are identical would over-refuse,
  never under-refuse. RC-CMP-7 OPEN ISSUE 1 stands.
- `DESCRIPTIVE_STATUS` (`:1658`) leaves the descriptive lines' `computed`/`one_quad`/`not_computable` words
  uncompared; they are a function of `n`, which is compared, and the recompute prints no such word. Optional.
- On the recompute's side `selected` is the stored exclusions' `kept_units` filtered by `members_excluded`
  (`independent_recompute_b5.py:966-1004`), not an independent selection; the independent check is
  `exclusions_rederivation` (status compared at `:1624-1627`) and the fill's `kept_units` rows (`:1162`).

## Answers

**1. G7 source.** Not literally faithful: the kept-units record is L9's step-2 output. In effect it is faithful
to the amendment's purpose, because the key set is the union of three maps (`c.pairs` at `:781`: L9's re-reduced
files, the kept-units universe, the recompute's selected members) and a key absent from any side is a
`routing_id` DISAGREE, with the kept set bound to the recompute's exclusions by `exclusions_sha256` (`:777`) and
to its re-derivation by `exclusions_rederivation` (`:1627`). Executed (`probes.out`, G7):
- L9 wrongly drops a run (kept-units omits it, no re-reduced file, recompute selects it): G7.a `exit=1`, row
  `(None, 'run/alpha/run-a', 'DISAGREE')`. This is the union behaviour RUN_STATE item 114 asks both reviewers to
  confirm: **confirmed**.
- L9 wrongly adds a registered science run neither side holds: G7.c `exit=1`, row `(None, None, 'DISAGREE')`.
  Recompute member absent while L9 keeps and re-reduces: G7.f `exit=1`. Malformed record (`cells` a list): G7.d
  `exit=1` (the run is still a key through the other sides). A unit's `run_ids` as a string: G7.e fail-closed.
- **Compared nowhere with exit 0: only the joint drop.** Kept-units omits the run, no re-reduced file, and the
  recompute marks it unselected (G7.b) or lacks the member (G7.b2): `exit=0`. Both sides take the run out through
  the same stored `derived/exclusions.json`; when the recompute's re-derivation of that file disagrees, G7.b3
  `exit=1 fails={'exclusions_rederivation': 1}`. So the residual is a science run the stored exclusions drop and
  the recompute's re-derivation agrees to drop. That is the residual item 114 names.
- Science/* from the sealed plan trees: G7.g (universe patched to the trees' science ids) gives
  `routing_id: 281` DISAGREEs, 280 with both sides `None`, and 840 energy rows. On a real window every science run
  the exclusions legitimately remove would DISAGREE the same way, unless the universe subtracts the exclusions,
  and those are a harvest output, not a sealed source. "science/* minus the agreed exclusions" is what the kept-units
  universe plus the `exclusions_rederivation` and `kept_units` rows already establish, so the plan trees alone
  are not usably stricter. NEEDS_RULING 1: the kept-units universe stands. A cheap tightening is to admit only
  `science` roles in `step_2_universe` (`:811`, today `(None, "science")`); it closes only a kept run both sides
  agree on that the plan tree does not register, at the cost of moving the fixtures off `run-a`.

**2. Categorical words.** Every claim word the fixture prints is compared exactly when present, and refuses when
wrong: outcome, direction, ceiling (`:1077-1081`), branch and licensed (`:943-947`, rule `licensed iff branch A`
matches `dominance_closeout.py:2038-2039`), ratio status (`:957-958`), p42 status and code (`:1270-1272`, words
match `sensitivity.py:292`), widened, `equals_primary`, `not_below_primary`, `outcome_equals_primary`, below,
NEG-8 decision, member `plausible` (rule matches `disclosures.py:653`) and `battery_term_available`.
`test_wrong_categorical_word_in_its_own_line_disagrees` and F2.b execute the wrong-word cases. What can still
exit 0: the two window words by relabel or omission (F1) and the two by-construction booleans (F2).
`HARVEST_WORDS` exemptions checked one by one (`:1841-1843`, `:1887-1890`): stored verdict status and conditions,
adapter continuity, tripwires, reference parity, ledger prefix result, `writer_excluded_all_removed`, attempt
verdicts and cause keys, `harvest_once`, re-harvest accounts; the recompute re-derives none of them (its only
`tripwire` is its own flag name, `independent_recompute_b5.py:2468`), so each is correctly exempt, except that
`adapter_continuity`'s key set makes it F1's landing word.

**3. Value-derived routes.** The line word still selects a leaf's path (`step()` `:240`); that is by design and
now gated by `LINE_KEYS`. The gate-passing relabels are the same-key-set pairs (`neg8_screen`/`adapter_continuity`;
`anchor_bound`/`host_cpu`; `physics_counts`/`battery_counts`; the three `sensitivity_*` record lines; bare
sentences) and the sweep shows only the first moves a compared word. The surviving value-derived route is the
*existence* of a comparison keyed on a line word (F1). The ratio text label (`:1960`) and the `loo_magnitude`
`block_number` digit remain as disclosed (OPEN ISSUES 3 and 6); a mislabel there refuses `no_row`, never exits 0.

**4. Over-refusal.** None found. Suite 303 OK. `line_gate_census.out`: all 324 real-shape numeric leaf paths
RC-CMP-4 printed (25 section/word pairs) pass the line gate's word and key tables with 0 violations. The
producer's `_item` calls (AST dump of `disclosures.py`, 70 calls plus the two dict lines) match `LINE_KEYS` by
section, word and key set, including the conditional keys: every keyed word always carries at least one of its keys
(`machine_summary` keeps `model`, `magnitude_ratio` keeps `contrast_id`, a `no_archive` `attempt_history` keeps
`pack`, a zero `flag_count` keeps `code` and `blinding`, `dominance_ratio` keeps `cell_id`), so `line_keys_absent`
cannot fire on a sound window. `exclusions_sha256` is the digest of the same `derived/exclusions.json` bytes on both
sides (`kept_units.py:425`; `independent_recompute_b5.py:692`, `:700`). Not verifiable here: the real window's
string and boolean leaves, the meter lines (`battery_term_available` is `battery_available` from the meter record on
L9's side and `battery is not None` on the recompute's, `:1818`), and the ulp question in the notes. The full-size
synthetic run at this head remains the readiness gate (RC-CMP-7 OPEN ISSUE 1).

## Evidence (`.codex-report/rc-cmp7-fable-rev/`)

- `suite.out`: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/claude-0/rcfable python3.13 -m unittest discover -s tests/independent_recompute -t .` at `c372211bf`.
- `probes.py`, `probes.out`: G7.0-G7.g, F2.a-F2.g, the gate-passing relabel sweep (run from the checkout root with the same environment).
- `line_gate_census.py`, `line_gate_census.out`, `rc-cmp-4-paths.txt`: the real-shape path census through `LINE_KEYS`.
- `patch_demo.py`, `patch_demo.out`: the F1 fix on a scratch copy of the comparator (no production edit).

## Pruning tally (gate policy rule 9)

| gate | ran | caught_number | caught_session_refusal | evidence |
|---|---|---|---|---|
| suite at `c372211bf` | yes | no | no | `suite.out`, 303 OK |
| G7 probes (one-sided drop/add, joint drop, science/* counterfactual) | yes | no (every one-sided case DISAGREEs) | no | `probes.out` G7 |
| F2 probes and relabel sweep | yes | no (a wrong word, not a number) | yes (F1: F2.c, F2.d, F2.e exit 0) | `probes.out` F2 |
| real-shape line-gate census | yes | no | no (0 of 324 violate) | `line_gate_census.out` |
