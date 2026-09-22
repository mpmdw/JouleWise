# Record 03 — RETAINED-ROOT-REFUSAL-CLASS-01 fix round 3 under the cold gate (activation ce7c57a9)

Branch `fix/2026-09-21-retained-root-terminal-markers`; previous head `af85b38a` (round 2); base
main `9e0a4995`; main at this record `ecefd46a` (already merged in at `bd671744`). This record is
committed together with the round-3 change (the commit that adds it is the round-3 head) so the
kernel's `latest_report` pointer resolves at every commit of the candidate.

## §1 Why a gate, not round 3 on the lead's own judgment

Both delta re-audits (record 02 exhibits A1 on `bd671744`, A2 on `af85b38a`) found no blocker and
seven should-fix/nit findings, and both reported the same defect class recurring across rounds 1
and 2: documentation contradicting the rule it sits beside, and ruled text copied with a latent
defect. Two consecutive rounds failing with one signature is the standing escalation trigger, and
curing A1-F1 would have been a second fix round on the same defect (round-1 Sol F1). The
magistrate therefore assembled packet 02 and convened a cold Fable judge paired with an Opus
contract-lens refuter (both detached, ~15 min). Their outputs are sealed in packet 02
(`10-coldgate-fable-ruling.md`, `11-opus-contract-refuter.md`).

## §2 The ruling, and where the refuter diverged (magistrate synthesis)

Judge Q1: disposition (a), one fix round at the lead's bench under a binding structural change —
the fixing seat authors no new prose (every changed documentation sentence is copied from the
ruling), the manual re-implementation is deleted, every rule-stating sentence is probed before the
round closes, and there is no round 4 (a same-signature finding returns the lane to the gate).
All seven findings land in the one merge candidate. The refuter's answer was the same shape,
labelled (c) ("gate-supplied prose only"), with the same MUST list.

Divergences, decided by the magistrate:

| Q | judge | refuter | taken |
|---|---|---|---|
| Q2 handbook text | dated correction inside the ruled passage, `descendants()` walk, argv wait | its own wording with inline flag glosses | judge's text verbatim (the gate that ruled the passage corrected it; the refuter's glosses are the same facts) |
| Q3 ruled sentence | restore `refusal-N.json` verbatim + one glossing sentence right after | spell the globs inside the parenthetical | judge's: the ruled sentence is verbatim and `N` is glossed by the next sentence (first-use test met) |
| Q4 reason string | `…plan span inactive at observation time (scripts/magistrate_watchdog.plan_span_active)`, assigned only after the span rule ran | `…plan span inactive (scripts/…)` | judge's |
| Q6 A1-F2 regression | interpreter-independent (patched parser), plus one raw deep-JSON run on the driver's interpreter | raw deep-JSON plan | judge's (3.14's decoder converts the overflow to `JSONDecodeError`; the bench ran the raw plan on 3.13 and 3.14 below) |
| Q6 A1-F3 regression | trailing slash and `night/..` spellings; no symlink (safe_path refuses) | symlink component | judge's |
| Q7 | Sol delta (high) + a pedagogy lens (Opus or blind Fable) | Sol delta + contract lens | both lenses in one second seat: a blind Fable seat carrying the writing standard, checking first-use and every rule sentence against code by executed probe |

Refuter findings outside the packet: N-1 (contract item 1's dirty-tree refusal string, D-183
paragraph from PR #378) — registered as kernel row `CANONICAL-REFUSAL-STRINGS-01` (A265), not fixed
here; N-2/N-3 (unglossed "every process", "plan span", "older sibling plan") — recorded here for
the pedagogy seat, not authored into the docs by the magistrate (structural rule 1).

## §3 The change (files, and the ruling text each carries)

| file | change | ruling |
|---|---|---|
| `docs/process/NIGHT_HANDBACK.md` | ruled pre-check passage replaced by the corrected passage (`pgrep -flP`, recursive `descendants()`, argv-based wait) | Q2 |
| `docs/contracts/evidence_night_entry.md` item 4 | ruled sentence restored verbatim (`refusal-N.json`); the naming sentence added after "Otherwise it is UNKNOWN and refuses."; the certification sentence replaced | Q3, Q4 |
| `docs/phase_2/derivation_night_runbook.md` §0.7 | zsh loop and its Source paragraph replaced by the read-only `retained_roots` call and the new Source paragraph | Q5 |
| `joulewise/evidence_night.py` | retained reason assigned only in the `else:` after `plan_span_active` returned False; `RecursionError` added to the except tuple | Q4, Q6 |
| `tests/test_evidence_night.py` | two pinned strings updated; three regressions (pre-span reason; patched-parser `RecursionError` → UNKNOWN + persisted failing record; realpath-equal spellings) | Q4, Q6 |
| `docs/process/state_kernel.json`, `TASK_QUEUE.md`, `RUN_STATE.md`, `tests/test_gen_state.py` | A230 retired to the Completed Queue Items table with A263 (delivered in this PR, never a live row); A264 and A265 registered; `latest_report` → this record; regions regenerated; ID oracle 221 − 1 + 2 = 222 | Q6 A2-F1 |

The ruled texts were extracted from the ruling file by script (`/tmp/magistrate-ce7c57a9/round3.py`:
blockquotes under each Q, re-wrapped at 79 columns, no words changed), not re-typed.

## §4 Executed evidence (bench, this worktree, 23:5x PDT 2026-09-21; python3 = 3.14.7)

Focused module run after the edits (nine tests: the six the seats ran plus the three regressions):

```
Ran 9 tests in 9.563s
OK
```

Kernel: `python3 -B scripts/gen_state.py` rc 0 (regions regenerated), then `--check` rc 0; `tests.test_gen_state`: `Ran 44 tests — OK`.

Mutation replays on package copies under `/private/tmp` (five tests: the span fence, the three regressions, the harvested-roots test; baseline PASS):

| mutation | result | failing assertion |
|---|---|---|
| m8 drop `realpath` (string compare) | KILLED | `test_custody_root_spellings_equal_under_realpath_classify_alike` (spelling `/` and `/night/..`): `'UNKNOWN' != 'ACTIVE'` |
| m12 retained reason `None` | KILLED | `test_retained_reason_names_the_span_rule_and_holds_before_the_span`: `('retained', None) != ('retained', 'terminal record present; plan span inact…')` |
| m14 `RecursionError` dropped from the tuple | KILLED | `test_deep_json_plan_is_unknown_and_the_failing_check_record_persists`: `RecursionError: maximum recursion depth exceeded` escapes |
| m15 reason reverted to "plan span over", assigned before the span rule | KILLED | `test_retained_reason_names_the_span_rule…`: `('ret…span over') != ('ret…span inactive at observation time (scripts/mag…ve)')` |

Ruled probes (each names the sentence it makes true):

- Q2 (handbook: `pgrep -flP` shows argv; `descendants()` reaches every depth; the tree empties):
  ```
  root=53476 child=53477
  pgrep -flP root:
    53477 zsh -c sleep 25 & wait
  descendants(root): 53477 53480
  pgrep -P child (one level): 53480
  TERM 53477,53480
  after TERM, descendants(root): []
  ```
- Q5 (runbook one-liner is the binding classifier: a symlinked `night/` refuses the whole read; numbered refusals list every marker):
  ```
  rootC evidence: [".../rootC/night/refusal-123.json", ".../rootC/night/refusal-7.json"]
  with rootB (symlinked night/): Refused: symlink/path collision: /private/tmp/r3probe-53472/night-custody/rootB/night/courier.sent
  ```
  (rootA/rootC carried `{}` plans, so they read UNKNOWN `plan unreadable: PlanError`; the probe targets the symlink refusal and the evidence list.)
- Q6 A1-F2 (raw deep-JSON plan `"[" * 100000` with a terminal record, new code):
  ```
  3.13.1 UNKNOWN plan unreadable: RecursionError: maximum recursion depth exc
  3.14.7 UNKNOWN plan unreadable: JSONDecodeError: Expecting value: line 1 co
  ```
  The driver runs under the pinned Python 3.13 (NIGHT-INTERPRETER-PIN-01); before this round the 3.13 call escaped (record 02 exhibit A1 V4, judge P1).
- Q4 (pre-span retained reason): pinned by `test_retained_reason_names_the_span_rule_and_holds_before_the_span` at `t0 − 7200` (passes above; m12/m15 killed).
- Q3 (`refusal-7.json` counts): pinned by the harvested-roots test and record 02 exhibit A2 V4; the naming sentence cites `scripts/run_night.py:273` (`{index:02d}`) and `:282` (`refusal-[0-9]*.json`), both read at this head.

Whole-module run (`tests.test_evidence_night`, all tests) on the round-3 working tree: see §5.

## §5 Whole-module tail, replay, and the two seats

Whole module on the round-3 working tree (python3 3.14.7):

```
Ran 103 tests in 178.495s

OK
```

The af85b38a full replay started by record 01 §2 was stopped at 32 min (superseded by this head; its result would not have been row 9's integration-tree evidence). Row 9 is the full sharded replay plus the quick tier on THIS head, and rows 4/5/10 are the two round-3 seats (Sol delta re-audit, high; blind Fable pedagogy-and-contract lens), all launched detached after this commit; their outcomes go to record 05 on the bookkeeping branch, never into this file.
