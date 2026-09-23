# 02 — Seat report: ruling 21 condition C3, the bench-replay driver amendment

Seat: implementation seat for activation a022aecc, 2026-09-22/23 PDT. Worktree
`JouleWise-wt-c3-a022aecc`, branch `feat/2026-09-22-replay-driver-fidelity-rule`,
based at `91f80870`. No bench was run, nothing was armed, no `sudo`, no
measurement, nothing under `~/night-custody` was read or written, and the
canonical checkout was touched only by the read-only `git worktree add`.

## What condition C3 required

Cold gate #3 ruling 21 §Q3
(`docs/process_traces/2026-09-22-activation-59857fe5/08-coldgate-packet-a267-merge-transaction/21-coldgate-fable-replay-verdict-ruling.md`):

> (C3) the driver amendment (fidelity rule replacing X2; session bar reported
> at 2 s, not 0.5 s) MAY follow the arm, but MUST land before any later replay
> artifact is offered, and its PR must show `verdict()` re-run on this very
> JSON producing PASS — no bench run needed.

## Diff summary

`scripts/bench_replay_start_drift.py`

- `SESSION_BAR_S` 0.5 → **2.0**, with the comment rewritten to ruling 21 §Q1:
  the 0.5 s bench bar binds the CHAIN-level figure only, the session figure is
  reported per slot and assessed against the night's own 2 s rule (A269 ruling
  10 amendment A1), and the struck 0.5 s session bar is named as the lead
  convention it was. The ESCALATE status is unchanged — it now splits against
  2 s.
- `ADMISSIBLE_SLOT` reduced to `(("collector_exit", 0), ("cleanup_proven", True))`.
  The `anchor_status == "bounded"` / `interior_complete_support` pair (the
  lead's "X2") is removed from per-slot admission, with the comment rewritten
  to say why X2 is unsatisfiable by a faithful replay and where its purpose
  now lives.
- `SMOKE_EXEMPT_FIELDS` unchanged in value; its comment now says what the
  exemption switches off after the amendment — the two ruled RULES taken over
  those fields, (4) fidelity and (5) the floor — and that nothing else is
  exempt.
- New module constants: `ARCHIVED_V31_BOUNDED = frozenset({2,5,6,8,9,11,12})`
  with the A269 record 01 step 10 citation (executed at `447fd6bf`) in its
  comment; `WORST_SKIPPED_TAIL_S = 2.3` with the A269 exhibit C citation
  (`end-postparse` max 2.291 s); `RULED_ADMISSIBILITY_TEXT`, the ruling's
  "Admissibility rule" block quoted verbatim.
- New pure functions: `fidelity(rows, archived_bounded=ARCHIVED_V31_BOUNDED)`
  returns the table rows, the tally string, and the `admitting` / `refusing`
  index lists; `tail_budget(rows, protocol, worst_skipped_tail_s=...)` returns
  the max tail, the gap, the budget and `fits`, with a statement carrying the
  figures. Both are hit directly by tests.
- `verdict()` now applies the six ruled clauses. New FAIL causes: an
  ADMITTING-direction slot (recorded in `slot_defects` as well, so it reaches
  the statement and the artifact by the ordinary route); an unmet
  bounded-with-interior FLOOR; a skipped-tail budget that does not fit the
  gap. The FAIL statement's LEADING clause is the rule that actually fired, in
  the order bar-not-shown → admitting → floor → tail budget → per-slot
  admissibility; `DEFECT_SLOT_CLAUSE_CAP` behaviour is unchanged. PASS and
  ESCALATE statements now carry the fidelity tally, the floor slots, the tail
  budget with its figures and the session figure against the 2 s rule. New
  keys: `fidelity`, `fidelity_applied`, `admitting_direction_slots`,
  `refusing_direction_slots`, `bounded_interior_slots`,
  `bounded_interior_floor_met`, `tail_budget`, `ruled_admissibility`.
- `markdown()` prints, in the Verdict section, the fidelity tally with both
  direction lists, the floor, and the tail-budget line with figures; adds an
  `## Anchor fidelity vs the archived v3.1 class` section (slot | replay
  `anchor_status` | `anchor_detail` | archived class | direction, plus the
  tally and the budget line); and adds an `## Ruled admissibility (cold ruling
  21, 2026-09-22)` section carrying `RULED_ADMISSIBILITY_TEXT` as a blockquote
  with the ruling's path. Under `--smoke` the fidelity section is omitted and
  the verdict section says rules (4) and (5) were NOT APPLIED.
- Module docstring gains a `THE RULED ADMISSIBILITY RULE` paragraph naming the
  ruling path, what X2 was, why it is unsatisfiable, and the six clauses.

`tests/test_bench_replay_start_drift.py` — new, 7 tests (below).

`tests/test_quiet_predicate_campaign.py` — the six `BenchReplayFailClosedTests`
that encoded X1/X2 amended to the ruled rule, plus two shared fixtures:
`PROTOCOL` (the full protocol's `envelopes`/`slot_pitch_s`/`envelope_s`, since
rule (6) needs the gap) and `bench_slot(index, **overrides)`, which gives a row
the ARCHIVED night's anchor class for that slot — a fixture making every slot
`bounded`, as the old ones did, is now five admitting-direction mismatches
rather than a clean run. `test_X1…escalates` → `…_over_the_night_rule_escalates`
(2.4 s escalates; 0.608 s, the executed replay's own slot 1, passes);
`test_X2…` → `test_X2_a_run_whose_finalisation_tail_never_ran_is_not_admissible`
(the lens's defect is now caught by the run-level floor, and one unresolved
slot is a reported refusing-direction mismatch, not a defect); `test_D2`
session figures moved over the 2 s rule; `test_D3`'s twenty-four clauses now
come from `collector_exit` + `cleanup_proven` on twelve slots, the statement
shape under test unchanged.

## `verdict()` re-run on `24-bench-replay.json` (ruling 21 C3)

Command, run from the worktree root at the head below:

```
python3 -B -c "import json,sys; sys.path.insert(0,'.'); from scripts import bench_replay_start_drift as bench; r=json.load(open('docs/process_traces/2026-09-22-activation-59857fe5/24-bench-replay.json')); v=bench.verdict(r['slots'], r['protocol']); print(json.dumps(v, indent=2, sort_keys=True))"
```

Status line:

```
"status": "PASS"
```

Statement, verbatim:

```
max(chain start_drift_s) = 0.352 s <= 0.5 s over 12/12 slots; anchor-class fidelity 10/12 match; admitting-direction 0; refusing-direction 2; bounded with complete interior support on slots [2, 5, 6, 11, 12]; max tail_s 8.410 s + 2.3 s worst skipped tail = 10.710 s < the 20 s inter-slot gap; max(session start_drift_s) = 0.608 s <= 2.0 s, the night's rule
```

Full output, verbatim (the `fidelity.table` rows are elided to the two that
are not `match`; every other key is complete and unedited):

```json
{
  "admitting_direction_slots": [],
  "bar_s": 0.5,
  "bounded_interior_floor_met": true,
  "bounded_interior_slots": [2, 5, 6, 11, 12],
  "escalate_chain_pass_session_fail": false,
  "fidelity": {
    "admitting": [],
    "archived_bounded": [2, 5, 6, 8, 9, 11, 12],
    "matched": 10,
    "refusing": [8, 9],
    "slots": 12,
    "table": [
      … slots 1-7, 10-12: direction "match" …
      {
        "anchor_detail": "affine_clock_residual_exceeded",
        "anchor_status": "unknown",
        "archived_class": "bounded",
        "direction": "refusing",
        "index": 8,
        "replay_class": "unresolved"
      },
      {
        "anchor_detail": "affine_clock_residual_exceeded",
        "anchor_status": "unknown",
        "archived_class": "bounded",
        "direction": "refusing",
        "index": 9,
        "replay_class": "unresolved"
      }
    ],
    "tally": "10/12 match; admitting-direction 0; refusing-direction 2"
  },
  "fidelity_applied": true,
  "max_chain_start_drift_s": 0.3523999589961022,
  "max_session_start_drift_s": 0.6078682499937713,
  "refusing_direction_slots": [8, 9],
  "ruled_admissibility": "Admissibility (cold ruling 21, 2026-09-22). …",
  "session_bar_exceeded": false,
  "session_bar_s": 2.0,
  "session_slots_over_bar": [],
  "slot_defects": [],
  "slots_expected": 12,
  "slots_missing_chain_drift": [],
  "slots_over_bar": [],
  "slots_recorded": 12,
  "smoke_exempt_fields": [],
  "statement": "max(chain start_drift_s) = 0.352 s <= 0.5 s over 12/12 slots; anchor-class fidelity 10/12 match; admitting-direction 0; refusing-direction 2; bounded with complete interior support on slots [2, 5, 6, 11, 12]; max tail_s 8.410 s + 2.3 s worst skipped tail = 10.710 s < the 20 s inter-slot gap; max(session start_drift_s) = 0.608 s <= 2.0 s, the night's rule",
  "status": "PASS",
  "tail_budget": {
    "budget_s": 10.70979604201857,
    "fits": true,
    "gap_s": 20,
    "max_tail_s": 8.40979604201857,
    "statement": "max tail_s 8.410 s + 2.3 s worst skipped tail = 10.710 s < the 20 s inter-slot gap",
    "worst_skipped_tail_s": 2.3
  }
}
```

The unabridged 157-line output is reproducible from the command above at this
head; the elision is the twelve-row `fidelity.table`, whose ten `match` rows
are printed in full by `markdown()` in any artifact this driver writes.

## Tests

New module `tests/test_bench_replay_start_drift.py`:

| test | rule under test |
| --- | --- |
| (a) `…executed_2026_09_22_replay_passes_the_ruled_rule` | C3 itself: the tracked JSON's own twelve rows → PASS; 0.352 s chain max, 0.608 s session max under 2 s, fidelity 10/12 with admitting 0 and refusing [8, 9], floor [2, 5, 6, 11, 12], 8.410 + 2.3 = 10.710 < 20; plus the artifact carrying the ruled text, the fidelity table and the budget line |
| (b) `…slot_resolving_what_the_archive_refused_voids_the_run` | (4) admitting direction: envelope 01 returned `bounded` → FAIL, `admitting_direction_slots == [1]`, the defect naming the slot, the statement leading with it; counterfactual run passes |
| (c) `…run_with_no_resolved_anchor_anywhere_fails_the_floor` | (5): no defect per slot, FAIL on the floor; a `bounded` slot without complete interior support does not satisfy it; one slot with both does |
| (d) `…tail_that_would_not_fit_the_gap…` | (6): 17.700 + 2.3 = 20.000 ≥ 20 → FAIL; 17.699 passes; a protocol stating no gap FAILS rather than skipping the rule |
| (e) `…session_figure_is_assessed_against_the_nights_two_second_rule` | Q1: 2.1 s → ESCALATE; 0.608 s → PASS (the behaviour that changed); the struck 0.5 s bar reproduced as an explicit-argument counterfactual |
| (f) `…smoke_does_not_have_rules_four_and_five_applied_to_it` | the smoke exemption: (4) and (5) not applied, (6) and the attestation states still are |
| `…archived_class_constant_is_the_one_the_ruling_cites` | the constant, the worst-skipped-tail figure, the trimmed `ADMISSIBLE_SLOT`, the ruling file's existence, and `fidelity()` as a pure function of an arbitrary archived set |

Each of the seven fails on the pre-amendment driver. Executed: with
`git show HEAD:scripts/bench_replay_start_drift.py` restored over the amended
file, `python3 -B -m unittest tests.test_bench_replay_start_drift` gave
`FAILED (failures=2, errors=5)` — (a) and (e) as assertion failures, the other
five as `KeyError` on the verdict keys the amendment introduces.

Commands and results at this head:

```
python3 -B -m unittest tests.test_bench_replay_start_drift          → Ran 7 tests, OK
python3 -B -m unittest tests.test_quiet_predicate_campaign          → Ran 128 tests, OK
python3 -B -m unittest tests.test_shard_tests tests.test_docs_freshness → Ran 35 tests, OK
python3 -m compileall -q joulewise tests scripts/bench_replay_start_drift.py → clean
python3 -B scripts/shard_tests.py --workers 8 --split               → see below
```

The repository documents no "quick tier": `pyproject.toml` has no test
configuration, there is no Makefile, and CI runs the whole suite through
`scripts/shard_tests.py` in a six-way matrix. The full suite was therefore run
locally through that same runner, eight workers with `--split`:

```
WORKERS SUMMARY shards=8 modules=250 tests=6868 failures=0 errors=0 skipped=109 failed_shards=none result=PASS
31:07.55 total wall
```

No linter is configured in this repository: `pyproject.toml` declares only
`build-system`, `project` and `setuptools.packages.find`, there is no ruff /
black / mypy / flake8 config file, and `.github/workflows/ci.yml` runs no lint
step — `compileall` is the closest thing CI has, and it is run above.

## Deviations from the brief, and why

1. **The brief expected the driver's existing tests to live in
   `tests/test_bench_replay_start_drift.py`.** They live in
   `tests/test_quiet_predicate_campaign.py::BenchReplayFailClosedTests`. The
   new module was created as instructed, and the six existing tests that
   encoded the struck conventions X1 and X2 were amended in place rather than
   moved (moving them would have made the diff unreadable for review).
2. **`RULED_ADMISSIBILITY_TEXT` omits the ruling's closing sentence** —
   "Driver output: status FAIL, statement quoted verbatim above, retained as
   issued." That sentence describes artifact 24's own pre-amendment output,
   not the rule, and reproducing it in every future artifact would be false.
   Everything through "…lead conventions, not ruled bars" is verbatim. The
   `## Ruled admissibility` section says, outside the quote, that the driver
   now implements (1)–(6) and that the two named conventions were removed from
   it by condition C3.
3. **Rule (6) is applied under `--smoke` too**, though (4) and (5) are not.
   The gap is a property of whichever protocol ran and both protocols state
   one (20 s full, 20 s smoke), so there is no reason to exempt it; the brief
   exempted only (4) and (5).
4. **A protocol that states no `slot_pitch_s`/`envelope_s` FAILS rule (6)**
   rather than skipping it, and `tail_budget()` says why in its statement. A
   silently-unassessed ruled rule is the defect class this lane exists to
   prevent; the cost is that the existing tests had to start passing a
   protocol with the two figures, which they now do via `self.PROTOCOL`.

## Open questions for the magistrate

1. **`scripts/test_timings.json` has no entry for the new test module.** It is
   not required — `shard_tests.discover_test_modules()` finds the module and
   the packer gives an unmeasured module the median measured weight — and I
   did not invent a number for a map whose provenance is a measured CI run.
   If the map is refreshed on its own cadence, nothing is needed.
2. **Artifact 24 and addendum 24b are untouched**, as ruling 21 §C1 requires
   ("nothing in artifact 24 is edited or relabelled"). 24b records that the
   amendment "follows the arm in its own PR, which must show `verdict()`
   re-run on this very JSON producing PASS"; whether 24b now gains a pointer
   to this branch's PR is the magistrate's call, not the seat's.
3. **No PR was opened and nothing was pushed**, per the brief.
