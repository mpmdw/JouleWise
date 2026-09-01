# Cold gate #3 — Packet A verdict

Cold Fable seat, fresh session, read-only. Read in the packet's order: `59-COLD-GATE-3-packet.md`, `45b-RULING-dependence-delta.md`, `48d-COLD-GATE-2-verdict-40b-45b.md` §Packet 2, the round-3 brief (§A.1), `53-terra-fix-dep-3.md`, `58-opus-delta-dependence-3.md`, then on the worktree `/Users/edr/code/JouleWise-wt-dependence` @ `8de7a9d7`: `docs/paper/round7/dependence-sensitivity.md` (119 lines), `scripts/dependence_sensitivity.py` (464), `tests/test_dependence_sensitivity.py` (1105). Nothing edited; all mutations on a `cp -r` copy under `scratchpad/cg3a/wt`, restored with `git checkout` after each case.

## Reproduced-survivor evidence

Baseline on the copy, then six of the eight survivors (three prose, two digest-regeneration, one binding), then the allowed-set measurement.

```
$ cd scratchpad/cg3a/wt && git log --oneline -1
8de7a9d7 DEPENDENCE fix round 3 (terra xhigh, report 53, …)
$ ls joulewise/estimators.py joulewise/claims.py
ls: joulewise/claims.py: No such file or directory
ls: joulewise/estimators.py: No such file or directory
$ python3 -m unittest tests.test_dependence_sensitivity
Ran 19 tests in 3.876s
OK
MUTATION_TABLE zero survivors: sheet-number=0, command=0, draft-anchor=0, refusal-delete-add=0
```

Each mutation was applied with a Python `str.replace` asserting exactly one occurrence, then the suite run, then the two files restored:

| Case | Mutation (sheet line) | Result |
|---|---|---|
| M8 | `:81` "The floor gate passes, but the direction gate fails" → "The floor gate fails, but the direction gate passes" | `Ran 19 tests … OK` — SURVIVES |
| M10 | `:93` "The gates agree in this invented example." → "The gates disagree…" | `Ran 19 tests … OK` — SURVIVES |
| N11 | `:13` "The **floor gate** is the strict check" → "non-strict check" | `Ran 19 tests … OK` — SURVIVES |
| N12 | `:9` "(a pure number, for example 2.262)" → `2.776`, then `SHEET_NUMERIC_TOKEN_SHA256` regenerated (`d5756c7a…`) | `Ran 19 tests … OK` — SURVIVES |
| N16 | `:13` `` `joulewise/claims.py:362-375` `` → `226-256`, digest regenerated (`a36d6564…`) | `Ran 19 tests … OK` — SURVIVES |
| P2 | all 32 values of `REFUSAL_SOURCE_SITES` (test `:303-336`) → `"main"` | `Ran 19 tests … OK` — SURVIVES |

Allowed-set measurement for rule 2's backstop (`_source_bound_sheet_numbers`, test `:379-412`):

```
allowed set size: 1309 | unique sheet tokens: 120 | unmatched: set()
'2.776' allowed? True | '4' allowed? True | '256' allowed? True
```

So the delta report's central facts hold: the prose outcome words are free, rule 2 is a stored snapshot whose backstop admits every payload float at every precision 0–15 (hence `2.776`, `4`, `256` are all "bound"), and rule 4's binding is name-existence only.

## 1. Is the four-round signature real? Structural cause

**Real.** The failing certifications are report 14 (round 0, original), 26 (round 1), 45 (round 2), 58 (round 3) — four in a row. Each fixer report certified exactly the surfaces its brief enumerated and the next audit found the adjacent one: constants (26) → doc/script delta list (45's predecessor, cold gate 32) → CLI line, draft anchors, table cells, meta-test direction (45) → prose outcome words, fingerprint, name-existence binding (58). Round 3 is the sharpest instance: the brief stated a RULE ("stdout must contain the outcome the surrounding prose claims", "every number … matched to a rendered field"), and the fixer implemented it as a hash→literal map (`DOCUMENTED_COMMAND_OUTCOMES`, test `:226-229`) plus a stored SHA-256 (`:230`), then wrote the acceptance mutation table as a test of five hand-picked mutations that prints its own "zero survivors" line (`:1053-1100`). The "sheet-number" mutation in that table is a tautology (a digest of altered text differs).

**Structural cause, one sentence:** the sheet is hand-authored and the tests try to check it afterwards, so the surface to cover is open-ended (every shape of number, word, command, and citation a writer can type) while every acceptance so far — including round 3's "rule" — was satisfiable by a finite list of assertions over the shapes already noticed, and a fixer optimising to a self-run acceptance binds exactly those shapes and no more.

Two halves, both must change: (a) authoring direction (checking free prose after the fact never closes), and (b) self-graded acceptance (the fixer chose the mutations that certified the round).

## 2. Mechanism: render + byte-equality — right core, insufficient alone

**What a rendered sheet does to prose.** If the template is a Markdown file with slot placeholders and the prose paragraphs are written in it verbatim, the rendered output is identical prose — Ed's standard is unaffected, because the reader sees the same sentences with the same numbers. What would break the standard is a template held as Python string literals (this sheet is LaTeX-dense: `n_{\mathrm{eff}}`, `\hat\rho`, `\(…\)`) — `str.format`/f-string braces collide with LaTeX braces and would force `{{ }}` doubling through every formula. That is a maintainability and readability hazard, so the interface below fixes the slot syntax.

**Does byte-equality make the sheet unmaintainable?** No, provided the template is the authoring surface and the `.md` carries a GENERATED header. A hand edit to the `.md` fails one test with a one-command cure (`--render-sheet > sheet.md`). The repo already does exactly this (`scripts/build_capstone.py`: `GENERATED_HEADER`, `--check` drift mode, `scripts/build_capstone.py:31,318`), so it is house practice, not a new invention.

**Is there a narrower fix?** "Bind outcome words via payload booleans and drop the fingerprint" closes M8/N6/M10/M11 (four of the eight). It does NOT close N12/N13/N16 — those numbers (`:9`, `:11`, `:13`, `:41`, `:49`, `:51`) are held by the fingerprint alone, and dropping it frees them entirely unless each is bound by a new assertion: `2.262` ← model-1 `t_critical_95`, `ν=9` ← `degrees_of_freedom`, `V=2.600391` ← `ar1_variance_inflation_factor(10, 0.5)`, `0.025` ← α/2, … That is round 5 as enumerated, and the signature predicts its result: the delta seat finds the one the fixer did not list. The narrower fix closes the instance, not the class.

**What closes the class.** Generation flips the audit question from "did the tests cover every claim in the document?" (open-ended; only adversarial mutation testing answers it) to "does the template contain any hand-typed value?" — which a lint answers mechanically: after removing slots, the template may contain no digit tokens except a closed allowlist of identifier SHAPES (never values). A fixer cannot leave a number free without the lint failing. That property is what none of rounds 1–3 had.

**What is still free under each option.**
- Round 5 enumerated: whatever the brief-writer omits — unbounded; the signature repeats.
- Byte-equality alone (magistrate's line as written): (i) slot MIS-WIRING — `${halving_se_repeat}` placed in the AR(1) paragraph re-renders to a sheet byte-equal to itself; nothing fails; (ii) hand-typed literals in the template; (iii) template prose meaning. The signature would fire a fifth time, on the template.
- Byte-equality + template lint + retained round-3 cross-direction assertions (my ruling): (i) closed by the lint; (ii) closed by keeping `test_every_worked_example_number_is_rendered_from_output_or_input_constant` (test `:872-1007`, real, per-model) as the independent wiring check, extended to outcome words; (iii) STILL FREE: the meaning of explanatory prose — "strict" (N11), "because the decision interval contains zero", definitions, glosses. This surface is not closable by any test and belongs to the pedagogy pass. It must be named in the acceptance as the declared residual so no seat "discovers" it as a survivor.

### Ruling: RESHAPE — interface decided (the fixer implements shape, does not choose it)

1. **Template file** `docs/paper/round7/dependence-sensitivity.md.in`: the current sheet's prose verbatim, with every number, outcome word, command line, stdout fragment, draft-anchor line number, and code citation replaced by a `string.Template` slot `${name}`. Rationale: `$` occurs nowhere in the sheet; LaTeX braces are untouched. The template is the ONLY authoring surface; WRITE_SCOPE adds it.
2. **Renderer** `scripts/dependence_sensitivity.py --render-sheet` (stdout) and `--check-sheet` (exit 2 on drift, mirroring `build_capstone.py --check`). Rendered `.md` begins `<!-- GENERATED by scripts/dependence_sensitivity.py --render-sheet from dependence-sensitivity.md.in; DO NOT EDIT. -->`. Rendering uses `Template.substitute` (not `safe_substitute`): a missing slot refuses.
3. **Slot dictionary** — every value pre-formatted as a string by the script: payload numbers at declared precision (6 dp; p 9 dp; x 12 dp; ν int); inputs and the ten-delta list from the constants; derived values the script computes (V and n_eff at ρ=0.5/0.9, α/2, 1−α/2); outcome words per model (`passes`/`fails`, table cells `pass`/`fail`) from the payload booleans; the two command lines built from the constants; for each command, the renderer EXECUTES it via `subprocess` and emits the agreement word (`agree`/`disagree`) and the quoted stdout fragment from the actual output; draft-anchor line numbers DERIVED by locating the quoted sentence in the frozen `draft-v1.md` (quote is the source in the template; refuse unless found exactly once); code citations resolved by AST — `two_sided_student_t_p_value`, `student_t_quantile`, `_beta_continued_fraction` (replaces "lines 49–115"), `_ci_t_critical` (replaces `estimators.py:226`), `evaluate_claim` (replaces `claims.py:362-375`), rendered as `` `name` (`path`, line N) ``; `generate_configs.py` field names checked to exist in that file at render time; the H30 paragraph read verbatim from `retensing-plan.md` as one slot.
4. **Template lint test**: template with slots removed and math spans (`\(…\)`, `\[…\]`) excised must contain no `\d` except tokens matching a closed allowlist of identifier shapes stated in the test (`DS-SENS-0\d`, `PG-SENS-0\d`, `DS-\d\d`, `PG-\d\d`, `_v5`, `SHA-256`, `UTF-8`, `H30`, `95%`, `95/95`, `A/B/B/A`, `AR\(1\)`, `Table \d`); inside math spans any `=\s*-?\d` is forbidden except the sum-limit shape `_\{[a-z]=\d\}` (so `ν=9`, `V=2.600391`, `\alpha=0.05` must be slots; `1/2`, `B_{i1}`, `1-k/n` may stay). The delta seat's review of the allowlist has one criterion: shapes only, never values.
5. **Tests kept / changed / deleted**: KEEP rule 1 execution, but bind the claimed outcome to the sheet: every command block is followed by a paragraph containing at least one backticked stdout fragment, and each fragment must appear in that command's stdout (the `--example` paragraph gains `renders "direction_gate_outcomes_agree": true`). KEEP rule 3, rule 5, and the round-3 per-model number assertions, extended to outcome words. FIX rule 4's binding half: run each refusal case in-process, catch the exception, and assert the innermost frame whose filename is the script has `co_name == REFUSAL_SOURCE_SITES[name]`; the fixer measures and corrects the map (at least `ar1_nonfinite_rho` → `_finite_number`; argparse cases as measured). NEW: byte-equality test; template lint; renderer-refusal test (mock a missing function/anchor). DELETE `SHEET_NUMERIC_TOKEN_SHA256`, its test, `SHEET_SOURCE_LOCATION_OR_IDENTIFIER_NUMBERS`, and `test_mutation_table_has_zero_survivors_across_all_four_surfaces` with its printed line. Drop `tests.test_paper_terms_lint` from this stream's verify line (F9 is correct: it lints other files).
6. **Acceptance is delta-seat-owned.** The fixer pastes its test run only. The delta seat runs ITS OWN mutation list on a copy, over the TEMPLATE and wiring, not the `.md`: type a value into the template (digit; `2.262`) → lint fails; swap two slot names between models and re-render → per-model assertion fails; replace an outcome-word slot with the literal and flip the payload input → assertion fails; retype a citation path → lint fails; corrupt a draft quote → renderer refuses; any byte change to the `.md` → byte-equality fails (one probe suffices). Declared residual: template prose meaning — held by the pedagogy pass, not by a test.

Why the signature will not repeat: the free surface moves from "any shape a writer can type into a document" to "digits and outcome words in a template outside slots", which is decidable by the lint; and the acceptance is no longer chosen by the party being graded.

## 3. The two wrong citation paths (`:11`, `:13`)

**Part of the round, not a bench edit.** The interface above replaces both citations with AST-resolved slots (`_ci_t_critical` at its def line 224; `evaluate_claim`, def 257–414), so a bench edit to the `.md` would be overwritten by the first render and would collide with the fixer's WRITE_SCOPE while the round is open. The delta report's own sub-claim about these citations is off by two lines (see Missed 3), which is precisely the drift the slot cures. Stopgap only if the round slips past a day: the magistrate may correct the two path strings in the `.md` in one commit with no test change.

## 4. Seats

Corrected history first (see Missed 2): fixers were terra (round 1, `19-terra-fix-07-dependence`, manifest model `gpt-5.6-terra`), luna (round 2, 37), terra (round 3, 53); delta seats Sol (26), Sol (45), Opus (58). Terra produced two of the three failing rounds; luna produced the `tr` defect. Sol has never fixed on this stream.

- **Fixer: Sol xhigh** (cross-component renderer + test design = xhigh trigger; default tier, no fast mode). Brief carries the interface above verbatim and states that the acceptance is not the fixer's to run.
- **Delta (contract + mutation): Opus 5**, re-running its own M/N/P table on the new shape plus the wiring probes in item 6 — continuity with the survivor list is an asset for a delta re-audit, and it is a different family from the fixer.
- **Pedagogy pass: fresh Fable**, over the TEMPLATE only (first-use test, Ed's writing standard) — the template is a new authoring surface and 58's three pedagogy findings (`I_x` gloss, "quantile", "rejects") land there. Dictated-fills pattern; it does not rule on the tests.
- Cold gate again only if a mandatory trigger fires; a fifth failure of the same signature is a STOP, not a round 6.

## 5. Missed

1. **Packet round chain is mislabelled.** "reports 26 → 32 → 45 → 53" mixes kinds: 32 is a cold-gate ruling and 53 is the round-3 FIXER report. The four failing certifications are 14 (round 0) → 26 → 45 → 58. The count is right; the labels are not.
2. **Seat history in 45b is false and propagated.** 45b:24 says "round 1 Sol, round 2 luna — terra has not touched this stream"; round 1 was terra (`19-terra-fix-07-dependence.md`, manifest `"model":"gpt-5.6-terra"`). Terra was therefore chosen for round 3 on a wrong premise. The brief to this seat ("Sol wrote rounds 1-2, luna audited round 2") is also inverted: luna wrote round 2, Sol audited rounds 1 and 2.
3. **Delta F3 sub-claim is wrong by two lines.** 58 says "`estimators.py:226` is `return round(student_t_quantile(0.975, df), 3)`"; on the branch (and main) that return is `:228`; `:226` is a comment inside `_ci_t_critical` (def `:224`). The path finding stands; the line claim does not — inside the very finding that condemns unpinned line numbers.
4. **Magistrate's proposal as written would re-fire the signature.** "The ONE test asserts byte-equality" leaves slot mis-wiring and hand-typed template literals free (§2). The template lint and the retained cross-direction assertions are the load-bearing additions, not decoration.
5. **"Rule 4 stays as a test" understates the defect.** Its binding half is a name-existence check (P2 reproduced: all 32 sites → `"main"`, suite green); it must change shape (traceback frame check), not merely stay.
6. **Terra's V1 tail is not a certification** (delta F5 is right, and the packet does not say so): the "22 tests" are 19 + 3 `paper_terms_lint` tests that lint `draft-v1.md` and `retensing-plan.md`, not this sheet; the `MUTATION_TABLE zero survivors` line is printed by a test of five fixer-chosen mutations, one a tautology. Reports quoting a self-printed acceptance line should be treated as uncorroborated per rule 9 (never self-grade).
7. **Delta N10** (`KEY_FROZEN` gloss deletable) is a content regression no test can hold; under the reshape it is the pedagogy pass's item, and should be filed there rather than left implying a missing test.
8. **Not in the delta's table but implied by it:** the "direction gate passes only when both endpoints…" definition at `:35` and the strict/non-strict wording at `:13` remain free under EVERY option, including this ruling — stated here so it is a declared residual, not a fifth-round "survivor".

VERDICT-A: RESHAPE