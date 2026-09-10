# Cold-gate ruling — packet 69: seat S3's generation-row ceiling clause, and the isolation harness rule

Judge: cold Fable adjudicator (Claude Fable 5.1), single non-interactive foreground session, convened 2026-09-10 under rule 11.
Trust anchors verified: worktree detached at `58d4696b`; packet digest (`00-PACKET.md` + exhibit A) `1563495784febe46…` matches; S3 branch
`origin/feat/2026-09-10-epoch-s3-acceptance-validator` resolves to `93799321`.

## Contamination disclosure

This session started with no loop context and read only what the packet allows: `00-PACKET.md`, exhibits A–D, the S3 branch's
`joulewise/calibration_bracketing.py` (rows, completeness function, acceptance-bound tail, statistics comparison), two test bodies on that branch
(the D2 naming test and the live-prefix fixture), `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`, `docs/decision_log.md` at
D-125/D-126, and `docs/process_traces/2026-08-07-u2-coldgate/Q1Q13-REMAND-CONSULT.md`. It did not read RUN_STATE, TASK_QUEUE, `docs/process/`,
any other process trace, `.claude/`, or any CLAUDE file. The session harness injected a memory index and global instruction text before the
packet arrived; those carry project doctrine and status pointers (merge rules, checkpoints, an "isolating counterfactual" vocabulary already in
use), and I cannot un-see them. None of them state a position on this packet's two questions, and nothing below relies on them. Every factual
claim about code or artifacts below was executed or read in this session; anything I could not run is marked NOT EXECUTED. No edits, no git
writes, no background work; /Users/edr/night-custody and the rehearsal checkout untouched.

## Q1 — the relation a registered generation row must satisfy

### Terms

- **Own Q99** (`prediction_99_two_draw_s` on the row): the 99 % two-draw prediction computed from this generation's own corpus. The row copy
  is cross-checked against the artifact's `source_statistics` at `:928-929`, so it is bound to the artifact's number.
- **Ceiling in force** (`operatives.maximum_budgetable_drift_s` on the row): the largest drift this generation will ever budget. Cross-checked
  against the artifact's `ratified_operatives` at `:942`.
- **Predecessor ceiling**: the ceiling in force of the generation this one was derived FROM under the envelope rule. This number exists in no
  field today. D-125 cl.2 (consult §2) defines the envelope as `C_g = max(C_{g-1}, Q99_g)`: the successor's ceiling is the larger of the
  predecessor's ceiling and its own Q99, so it can never fall.
- **Screen** (`operatives.bracket_screen_s`): the drift below which a window passes without spending budget.

### Finding on the clause under ruling

The HEAD clause requires `inherited == ceiling == own Q99` and `screen < ceiling`. I confirm delta 68 D1 by execution (probe 3): the only input
the `ceiling == own Q99` term refuses on its own is a row whose ceiling sits above its own Q99, and under D-125 that is exactly a legitimate
successor whose inherited ceiling won the max. A clause whose sole isolating refusal is a licensed input is a wrong clause, not an under-tested one.

But delta 68's recommended relaxation, option (i) `ceiling >= own Q99`, is also wrong, and worse in the direction that matters. Probe 3 shows
it ADMITS both envelope violations: a successor whose ceiling fell below its predecessor's (`P=0.0095, Q=0.008, C=0.009`) and a successor whose
ceiling was invented above both predecessor and own Q99 (`P=0.0085, Q=0.008, C=0.009`). An inequality against the row's own Q99 cannot enforce
"never falls", because the quantity it must never fall below is the predecessor's ceiling, and the row does not carry it. D-125 cl.2 is an
exact equation, and only an exact equation transcribes it.

Option (ii), keying the equality on `screen_rule == range_equals_screen`, is the wrong axis: the screen rule governs how the screen is derived,
and refuter 65 §3 already shows a successor may legitimately register `range_equals_screen` while still inheriting a ceiling. The ceiling
relation is a function of lineage position, not of the screen rule.

### Ruled relation (option iii)

1. `inherited_ceiling_s` is retired. In every issued row it duplicates the ceiling in force (probe 2, probe 1: no issued artifact carries the
   string `inherited`), and a copy of a number carries no fence. Its name also misdescribes the value: today's rows store their OWN ceiling
   under a name that says "inherited".
2. The row instead carries **`predecessor_ceiling_s`**: the predecessor's ceiling in force as a Decimal string, or `None` for a generation
   that was not derived under the envelope rule. The key stays in `_GENERATION_ROW_REQUIRED_KEYS` so a future row cannot omit it and fall
   back. Both rows registered today (`_D102_N19_DERIVATION`, `_D102_N17_DERIVATION`) set it to `None`: the n19 genesis has no predecessor, and
   the anchor-v3 lineage (r3–r6) is a re-derivation whose ceiling is its own Q99 and is BELOW n19's, so registering n19's ceiling as its
   predecessor would refuse it, correctly, because it is not an envelope successor of n19. `None` is the truthful registration.
3. The clause: **the ceiling in force equals the own Q99 when there is no predecessor, and equals `max(predecessor ceiling, own Q99)` when
   there is one; the screen is strictly below the ceiling in every case.** The strict `screen < ceiling` half is universal and stays exactly as
   written (D-126 cl.3, consult §5 `cap > 0`); together with the existing `screen + excess == maximum` at `:967` it gives `cap == ceiling − screen`
   and `cap > 0`.
4. For (a) existing generations (`import_only`, predecessor `None`) the relation collapses to `ceiling == own Q99`, which all six issued
   artifacts satisfy today (probe 2). For (b) a D-125 envelope successor (`import_plus_live`, predecessor set) it pins the ceiling to one
   value. Prefix mode is not consulted by the relation; today the two axes coincide, but they are different facts.

**Code shape, one line** (replacing `ceiling != drift or drift != prediction` at `:355-356`, with `ceiling` renamed to `predecessor` and
`_decimal(None)` returning `None` treated as "absent", not as malformed):

```python
or drift != (prediction if predecessor is None else max(predecessor, prediction))
```

with `screen is None or not screen < drift` retained unchanged. (`_decimal` must distinguish an absent predecessor from an unparseable one:
`predecessor_ceiling_s is None` is absent; a present string that fails to parse still refuses.)

**Isolating counterfactuals** (an input this clause refuses that no other check refuses; artifact and row moved together so the `:928` and
`:942` comparisons pass; screen `0.006` so `screen < ceiling` passes; excess retuned so `:967` passes):

- Envelope: `predecessor_ceiling_s = "0.0095"`, own Q99 `0.008` (row and `source_statistics`), ceiling `0.009` (row and `ratified_operatives`)
  → refused ONLY here: the ceiling fell below its predecessor's. Deleting the clause admits it; option (i) admits it too (probe 3).
- Envelope, other direction: `predecessor_ceiling_s = "0.0085"`, own Q99 `0.008`, ceiling `0.009` → refused only here: headroom invented above
  both inputs.
- Genesis: `predecessor_ceiling_s = None`, own Q99 `0.008`, ceiling `0.009` → refused only here: a genesis ceiling that is not its corpus Q99.
- Admit control that the HEAD clause wrongly refuses: `predecessor_ceiling_s = "0.009"`, own Q99 `0.008`, ceiling `0.009` → admitted (probe 3).

The naming test must move the artifact WITH the row for each case (the `retuned` helper in
`test_generation_row_refuses_a_screen_at_or_above_its_ceiling` already does this); a row-only move is refused upstream at `:928`/`:942` and
proves nothing about this clause. That is the D2 defect, and this test shape cures it.

Out of scope, noted for S4: when the envelope screen rule lands, the screen gets the same shape (`predecessor_screen_s`, `S_g = max(S_{g-1},
Q95_g)`), and the natural second binding is `predecessor_ceiling_s == <predecessor row>.operatives.maximum_budgetable_drift_s` looked up by
the artifact's `derivation_notes.predecessor.acceptance_id`. Neither is required by this ruling; no successor is registered.

Constraints honoured: the six artifacts are untouched and load through the collapsed relation byte-identically (probe 2 evaluates the exact
strings); the change is one term in one clause plus a field rename and two `None` values; no successor data is registered.

## Q2 — the harness rule: ADOPT AS AMENDED (subject to Ed's veto)

Delta 68 §7 names the right trigger but the wrong unit. The masked-counterfactual signature recurred four times because cuts were COMPOUND:
the seat's M18 deleted both equalities together and was "killed" by the `inherited` subtest, which never exercised the second equality. The
refuter's X2 cut one term and survived. The rule that catches the class is atomicity plus isolation, and it applies whether or not a fence was
added this round; the "fence added upstream" case is where it is most often violated, so it is named as the mandatory re-cut trigger.

Exact wording for the adversarial-review doctrine:

> **Isolation rule.** A *clause* is one boolean term of a refusal condition. A *fence* is any check that refuses an input before a later check
> sees it. (1) Every clause a diff adds or changes is named by a test whose counterfactual is refused by that clause ALONE: with that single
> term deleted and every other line intact, the test fails. A cut that deletes two terms at once discharges nothing. (2) A diff that adds or
> moves a fence re-cuts, one term at a time, every existing clause downstream of that fence whose counterfactual passes through it, and shows
> each still flips on its own deletion; a fence that now refuses a downstream clause's counterfactual means that counterfactual must be re-cut
> to one the fence admits. (3) The delta re-audit of a fix round re-runs the seat's whole sweep at one term per cut, with `Ran N ≥ 1` parsed
> from the runner and source bytes restored and hash-asserted; a surviving atomic cut is `should_fix`, never a nit, because a term nothing can
> isolate is either dead or unruled. (4) When a clause's only isolating counterfactual is an input a ruling licenses, the finding routes to the
> clause, not to the test; if no ruling states the clause, it goes to the cold gate before round three.

Amendments relative to §7 as proposed: the unit is the atomic term (§7 said "counterfactual", which let compound cuts pass); clause (4) is
new and is the lesson of this packet; "re-runs the WHOLE mutation sweep" is kept but bounded to the seat's sweep plus the fence-downstream
re-cuts, not every clause in the module.

## Executed probes (all read-only, foreground, this session)

1. `git rev-parse HEAD` → `58d4696b`; `git rev-parse origin/feat/2026-09-10-epoch-s3-acceptance-validator` → `93799321`;
   `cat 00-PACKET.md exhibit-A-delta-68.md | shasum -a 256` → `1563495784febe46…` (matches the packet digest).
   `grep -l inherited configs/calibration/calibration_acceptance_*.json` → no match across the 6 artifacts (the field is registry-only).
2. `git show <S3>:joulewise/calibration_bracketing.py | sed -n '300,400p'` (clause at `:348-358`, `screen_rule` fence `:384`);
   `sed -n '895,975p'` (row-vs-artifact prediction comparison `:928-929`, operatives comparison `:942`, `screen + excess == maximum` `:967`);
   `grep -n prediction_99_two_draw_s` → `:241,264,288,350,928` only, so the Q99 is compared, never recomputed, and a row+artifact move reaches
   the clause unmasked. Artifact `ratified_operatives` and `source_statistics` for r6 read: ceiling `0.010164834757777545` == own Q99, screen
   `0.009724`. Decimal evaluation of the ruled relation with predecessor `None` on the n19 and n17 rows → `True`, `True`; HEAD clause → same.
3. `python3` Decimal table (screen `0.006`), columns = ruled / HEAD / option (i):
   legit successor `P=0.009 Q=0.008 C=0.009` → True / **False** / True;
   ceiling fell `P=0.0095 Q=0.008 C=0.009` → False / False / **True**;
   ceiling invented `P=0.0085 Q=0.008 C=0.009` → False / False / **True**;
   own Q99 dominates `P=0.0085 Q=0.009 C=0.009` → True / True / True;
   ceiling below own Q99 `P=0.0085 Q=0.0095 C=0.009` → False / False / False.
   X2 masking reproduced arithmetically: the D2 test's row-only move (`0.009` → `0.010164834757777545`) is unequal to the artifact's
   statistic, so `:928` refuses it with the clause deleted.
4. `git show <S3>:tests/test_calibration_bracketing.py` at `:3565-3615` (D2 test and the `retuned` helper) and `:2945-2985` (live-prefix
   fixture). `sed -n '8166,8215p' docs/decision_log.md` and consult `:97,105,140-165` read; exhibit D is a faithful copy.
5. NOT EXECUTED: the test suite, the seat's or the refuter's mutation harnesses, and the delta's `/tmp/dr_f3_probe.py`. The arithmetic
   above stands in for them at the clause level only.
