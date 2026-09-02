All checks complete. Here is the delta re-audit.

---

# DELTA RE-AUDIT — dependence-sensitivity fix round 3 (`8de7a9d7`, contract lens)

Read-only. Nothing edited in the worktree; all mutation work done on the copy at `.../scratchpad/dep-mut/`, restored after every case.

## 1. Sub-rule implementation — real or fake

| Rule | Test implementing it | Real / fake | Evidence |
|---|---|---|---|
| **1** — every fenced/indented command extracted + executed verbatim | `test_every_documented_command_executes_verbatim_with_its_claimed_outcome` via `_extract_sheet_commands` / `_assert_documented_command_fixture` (`tests/test_dependence_sensitivity.py:328-388`, `:848`) | **Extraction real, claim-binding FAKE** | My own `grep -nE '^ {4,}\S'` finds exactly 2 command lines (sheet `:95`, `:99`); no fenced blocks exist (fenced branch is dead code). I imported the helper: it returns exactly those 2, verbatim, and `subprocess(shell=True, cwd=REPO_ROOT)` really runs them. **But** the "outcome the surrounding prose claims" is a hard-coded string in `DOCUMENTED_COMMAND_OUTCOMES` (`:222-225`) keyed by command hash — the sheet's prose is never read. See survivors M10/M11. Extraction is also confined to `^ {4}\S`; an inline-backtick or 8-space-indented command is invisible to it (P3/P4). |
| **2** — every numeric token bound to a rendered field or declared constant | `test_every_sheet_numeric_token_is_source_bound_by_the_fixture_rule` (`:975`) | **STORED SNAPSHOT + very permissive backstop** | `SHEET_NUMERIC_TOKEN_SHA256` (`:229`) is a *stored* digest of the token stream, not derived at test time. The anti-snapshot backstop is `set(tokens) - _source_bound_sheet_numbers(payload)`, but that allowed set has **1309 members** (every payload float re-rendered at precisions 0–15, `abs()`, plus a 24-entry hand allowlist) against 120 unique sheet tokens. I confirmed by measurement: 86 distinct 6-dp renderings are legal; the sheet uses ~40. Changing a number to another legal rendering *and* regenerating the digest passes — survivors N12, N13, N16. |
| **3** — draft anchors resolved against the frozen draft's sentence text | `test_every_draft_line_anchor_resolves_in_the_frozen_draft` via `_assert_placement_anchor_fixture` (`:390-403`, `:857`) | **Real** (with a 40-char horizon) | It does open `docs/paper/draft-v1.md` and assert `draft_lines[n-1].startswith(quote[:40])`, not mere existence. Verified by hand: draft `:285` = `Table 3. Prospective contrast decisions. …` ✓, draft `:294` = `**Limitation 1 is an untested load-regime transfer.**` ✓. Weakness: only the first 40 characters are checked; anything past char 40 of a quote is held only by the stored `PLACEMENT_ANCHORS` tuple (`:226-231`). |
| **4** — refusal set exact both ways + each row binds to a source site | `test_refusal_row_set_is_exact_and_every_row_binds_to_a_source_site` via `_assert_refusal_row_fixture` (`:405-419`, `:860`) | **Set check real; "binds to a source site" FAKE** | The two-way set equality is genuine (`frozenset(names) == MANDATED_REFUSAL_ROW_NAMES` *and* `set(REFUSAL_SOURCE_SITES) == MANDATED…`) — M18/M19 both fail. The binding half is `assertIn(site, {FunctionDef names in the script})`: it only asserts the string *is the name of some function*. Rewriting **every** entry of `REFUSAL_SOURCE_SITES` to `"main"` leaves the suite green (P2). |
| **5** — every bracketed ten-number list equals `EXAMPLE_BLOCK_DELTAS_J` | `test_every_bracketed_ten_number_list_equals_the_example_constant` (`:850`) | **Real** | Regex finds exactly 2 lists (sheet `:75`, `:99`); asserts count == 2 and each `== EXAMPLE_BLOCK_DELTAS_J`. M6/M6b both fail on it. |

I also traced whether the `REFUSAL_SOURCE_SITES` *content* is honest (independent of enforcement), using a `sys.settrace` hook capturing the first exception-raise frame inside `scripts/dependence_sensitivity.py`: **28/32 exact**. Of the 4 apparent mismatches, `infinite_interval`/`infinite_decision_interval` resolve to `<genexpr>` inside the claimed function and `caller_alpha` surfaces argparse's error at `main` — probe artifacts. One genuine mis-attribution: `ar1_nonfinite_rho` is claimed as `_ar1_variance_terms` but raises in `_finite_number` (called from `ar1_variance_inflation_factor`, a name absent from the map).

## 2. Mutation table (re-run by me, on the copy)

Baseline on the copy: 19 tests, OK.

| # | Mutation | Failing test(s) |
|---|---|---|
| M1 | table cell digit `:89` `10.000000`→`10.000001` | `…numeric_token…`, `…worked_example_number…` |
| M2 | prose digit `:81` `0.442719`→`0.442718` | `…numeric_token…`, `…worked_example_number…`, `…golden_every_documented_intermediate` |
| M3 | command digit `:99` `--floor 3.5`→`3.6` | `…documented_command_executes_verbatim…`, `…numeric_token…` |
| M4 | flag value `:99` `--se-metrology 0.2`→`0.3` | `…documented_command_executes_verbatim…`, `…numeric_token…` |
| M6 / M6b | bracketed-list digit at `:75` / inside the `:99` command | `…bracketed_ten_number_list…` (+2 / +2 more) |
| M7 | `:101` `"…agree": false`→`true` | `…golden_every_documented_intermediate` (legacy `assertIn`, not rule 1) |
| M12/M13/M14/M20 | source line refs `166→167`, `226→227`, `375→376`, `194→195` | `…numeric_token…` only (digest) |
| M15/M16/M17 | `:49` `min(n-1,·)`→`min(n-2,·)`; `:41` ν=9→4; `:9` `2.262`→`2.776` | `…numeric_token…` only (digest) |
| M18 / M19 | delete a refusal row / add a fake one | `…refusal_row_set_is_exact…` |
| M21–M24 | AR(1) term, `V=2.600391`, `64-character`, H30 `118` | digest (+ fragment test where applicable) |
| N1/N2/N3 | draft anchor `285→286`, `294→293`, one row `294→295` | `…draft_line_anchor_resolves…`, `…numeric_token…` |
| N4/N5 | anchor quote text corrupted | `…draft_line_anchor_resolves…` (via the stored tuple) |
| N7/N8/N9 | delete Missed-4 clause / delete `I_x` gloss / swap Holm 0.025↔0.05 | caught |
| N15 | `:79` ρ̂ `0.300000`→`0.500000` + digest regenerated | `…worked_example_number…`, `…golden…` |
| **M8** | **`:81` "floor gate passes, but the direction gate fails" → "floor gate fails, but the direction gate passes"** | **SURVIVOR** |
| **N6** | **`:83` and `:85` "The floor gate passes and the direction gate fails." → inverted (both lines)** | **SURVIVOR** |
| **M10** | **`:93` "The gates agree in this invented example." → "The gates disagree…"** | **SURVIVOR** |
| **M11** | **`:101` "registered-composition direction screen passing while the AR(1) and halving screens fail" → inverted** | **SURVIVOR** |
| **N11** | **`:13` "The floor gate is the **strict** check" → "non-strict check"** | **SURVIVOR** |
| **N12** | **`:9` `2.262`→`2.776` with `SHEET_NUMERIC_TOKEN_SHA256` regenerated** | **SURVIVOR** |
| **N13** | **`:41` `\nu=9`→`\nu=4` with the digest regenerated** | **SURVIVOR** |
| **N16** | **`:13` `claims.py:362-375`→`226-256` with the digest regenerated** | **SURVIVOR** |
| **P1/P2** | **one / all `REFUSAL_SOURCE_SITES` values repointed to a different existing function** | **SURVIVOR** |
| N10 | delete the `KEY_FROZEN` gloss sentence | SURVIVOR (no rule claims this surface) |
| P3/P4 | add a NEW inline-backtick / 8-space-indented command with a false claim | caught **incidentally** by rule 5 + the digest, **not** by rule 1 |

## 3. Command replay (mine, `sed -n 'Np' … | bash`, both inspected first — read-only, stdout to a file)

| Line | Command | Exit | stdout | Prose claim | Match? |
|---|---|---|---|---|---|
| `:95` | `python3 scripts/dependence_sensitivity.py --example` | **0** | `"direction_gate_outcomes_agree": true` (out line 215) | `:93` "The gates agree in this invented example." | ✓ |
| `:99` | `… --block-deltas '[5.0, 7.6, …, 3.2]' --floor 3.5 --se-metrology 0.2 --deterministic-bound-total 3.5` | **0** | `"direction_gate_outcomes_agree": false`; `independent_blocks` floor=T dir=T, `ar1_estimated_rho` dir=F, `fixed_effective_n_halving` dir=F | `:101` "registered-composition direction screen passing while the AR(1) and halving screens fail, and renders `"direction_gate_outcomes_agree": false`" | ✓ |

A1 cure (ii) landed: the `grep|cut|tr` pipeline is gone and the literal list is passed. The round-2 `tr -d '\140'` defect is cured.

## 4. Content cures

| Cure | Check | Result |
|---|---|---|
| C1 x values | Recomputed x = ν/(ν+t²) from the artifact: `0.078307034361`, `0.057315253936`, `0.064651302005` | ✓ all three exact to 1e-15 |
| C1 formula | Fed the **printed 12-dp x** through `I_x(ν/2, 1/2)`: 2.81375968e-06 / 1.25621376e-03 / 1.60248416e-03 vs sheet `0.000002814` / `0.001256214` / `0.001602484` | ✓ match at the sheet's 9 dp — the replay claim is true |
| C1 independence | Reproduced all three p-values by **Simpson quadrature of the Student-t density** (400 000 panels, `math` only — no repo CF, no scipy): `2.81375996e-06`, `1.25621349e-03`, `1.60248396e-03` | ✓ |
| C1 routine names at HEAD | `two_sided_student_t_p_value` at `joulewise/analysis_engine/distributions.py:166` ✓; `student_t_quantile` at `:131` ✓; `critical = round(student_t_quantile…, 3)` at `scripts/dependence_sensitivity.py:194` ✓ (all AST- or line-pinned by the test) | ✓ |
| C1 Lentz span | "lines 49–115": `_beta_continued_fraction` is **`def` at :48** (49 is its docstring) and ends before `_regularized_incomplete_beta` at `:89`; 115 sits inside `_student_t_survival_nonnegative` (110–121) | loose; **unpinned** (49/115 are allowlist-only) |
| A2 anchor | draft `:294` = `**Limitation 1 is an untested load-regime transfer.**`; `:292` is `## 7. Discussion and limitations` | ✓ correctly moved to 294 in all four rows |
| Missed 2 | `:11` no longer cites 1859/2578; cites `family_alpha` and the `multiplicity` block's `method`/`alpha`/`m` — verified at `generate_configs.py:1859` and `:2576-2581` (`method: "holm"`, `alpha: 0.05`, `m: 2`) | ✓ (but no test reads that file) |
| Missed 4 | `:81` "The printed 2.262000 is the three-decimal 2.262 quantile rendered at six decimal places; that three-decimal value … entered the half-width" — matches `scripts/dependence_sensitivity.py:194` | ✓ |
| Worked-example arithmetic | Recomputed sum 50.000000, mean 5.000000, Σdev² 17.640000, s 1.400000, num 4.320000, den 14.400000, ρ̂ 0.300000, nine AR(1) terms, Σterms 0.367347, V 1.734695, n_eff 5.764703 — all from the raw deltas | ✓ every one matches the sheet |
| **Citation paths** | `:11` `joulewise/estimators.py:226` and `:13` `joulewise/claims.py:362-375` — **neither file exists** | ✗ **wrong** (see F3) |

## 5. Findings

**BLOCKERS**

- **F1 — the prose that states gate outcomes is unbound (survivors M8, N6, N11).** The three table cells at `:89-91` get an exact `assertEqual(cells, expected_cells)`; the three prose sentences at `:81`/`:83`/`:85` asserting the *same* outcomes get only `assertIn` of numeric renderings, so the words "passes"/"fails" are free. So is the gate *definition* at `:13` ("strict check" → "non-strict check" is green). This is the round's own failure signature repeating one surface over: the enumerated cells certified, the adjacent un-enumerated prose free.
- **F2 — rule 1's claim half is not implemented (survivors M10, M11).** THE RULE says stdout "must contain the outcome **the surrounding prose claims**." The implementation maps *command hash → a string typed into the test file*; it never reads the sheet's prose. `:93` and `:101` can be inverted with the suite green. That `:101`'s `false`→`true` (M7) *is* caught is luck: a legacy `assertIn('"direction_gate_outcomes_agree": false', document)` at `tests/test_dependence_sensitivity.py:604` happens to exist. There is no counterpart for the `--example` command.
- **F3 — two source citations in the sheet do not resolve.** `docs/paper/round7/dependence-sensitivity.md:11` cites `joulewise/estimators.py:226` and `:13` cites `joulewise/claims.py:362-375`. `find` confirms neither path exists; the files are `joulewise/analysis_engine/estimators.py` and `joulewise/analysis_engine/claims.py` — the paths the *same sheet* uses correctly at `:35` and `:37`, and the paths cold gate 48d used. The line numbers are right *inside* the analysis_engine files (`estimators.py:226` is `return round(student_t_quantile(0.975, df), 3)`; `claims.py:362-375` is the direction/multiplicity outcome block), so this is a dropped `analysis_engine/` path segment. Introduced in fix round 2 (`35716229`, `git log -S`), inherited here, inside WRITE_SCOPE, and left unbound (N16 survivor).
- **F4 — rule 2 is a stored fingerprint, not a binding (survivors N12, N13, N16).** With the fingerprint regenerated alongside the sheet — the exact workflow a future editor will use — `2.262`→`2.776` at `:9`, `ν=9`→`ν=4` at `:41`, and a wholesale rewrite of the `claims.py` line range all pass. The `unmatched` backstop cannot stop them: the allowed set is 1309 strings wide. The uncovered regions are the Terms section (`:9`, `:11`, `:13`) and the Fixed-procedure section (`:41`, `:49`, `:51`) — every number there is held **only** by the snapshot.
- **F5 — the suite's own printed certification is not one.** `test_mutation_table_has_zero_survivors_across_all_four_surfaces` (`:952-1004`) prints `MUTATION_TABLE zero survivors: sheet-number=0, command=0, draft-anchor=0, refusal-delete-add=0` — and terra's report V1 quotes that line as its tail. It runs five hand-picked in-process mutations, of which the "sheet-number" case is a tautology (a SHA-256 of altered text differs). It tests neither the `unmatched` surface, nor rule 5, nor any prose claim. The printed line reads as a certification of four surfaces and is not one.

**SHOULD-FIX**

- **F6** — rule 4's binding half is decorative: `assertIn(site, function_names)` (P1/P2 green). Repointing every row to `"main"` passes. The map's *content* is 28/32 accurate under a settrace probe; only `ar1_nonfinite_rho` is genuinely mis-attributed (raises in `_finite_number`, not `_ar1_variance_terms`). Fix: assert the raise site, e.g. via a settrace/AST check that the row's expected message literal occurs inside the named function.
- **F7** — rule 1's extraction is `^ {4}\S` plus fenced blocks only; a command in inline backticks or at 8-space indent is never extracted (P3/P4 were caught by rule 5 and the digest, incidentally). The sheet already writes identifiers in inline backticks, so this is a live shape.
- **F8** — rule 3 verifies only `quote[:40]` against the draft; the rest of each anchor sentence is held by the stored `PLACEMENT_ANCHORS` tuple. `Table 3. Prospective contrast decisions.` is exactly 40 chars so it is fully checked; `**Limitation 1 is an untested load-regime transfer.**` is checked only through `…load-regim`.
- **F9** — `tests.test_paper_terms_lint` lints `docs/paper/round7/retensing-plan.md`, **not** this sheet (`tests/test_paper_terms_lint.py:14`). Pairing it in the verify line implies coverage that does not exist.
- **F10** — citation residue: `distributions.py` "lines 49–115" starts one line after the `def` at `:48` and ends mid-`_student_t_survival_nonnegative`; 49/115 are allowlisted, never pinned. Cold gate 48d §81 already ruled that unpinned line numbers in a frozen-doc citation drift.

**PEDAGOGY (first-use test)** — three failures, with the glosses I would dictate:

1. **`I_x` / "regularized incomplete beta function" (`:37`).** The gloss defines the term by another undefined one: "the fraction of a **Beta(ν/2, 1/2) distribution's** probability lying below x." A reader who does not already know the Beta distribution cannot replicate. Dictate: *"…where I_x(a, b) is the regularized incomplete beta function: take the curve y = u^(a−1)(1−u)^(b−1) over u from 0 to 1, and report the area under it from 0 to x as a fraction of its total area. Here a = ν/2 and b = 1/2. Every standard statistics library provides it (SciPy: `scipy.special.betainc(a, b, x)`; R: `pbeta(x, a, b)`)."* The named call is what makes the sentence's "a library that evaluates this function" replicable rather than gestural.
2. **"quantile" (`:37`, `:81`).** Enters unglossed as a synonym for the already-built "critical value" (`:9`). Dictate at first use: *"the quantile — the cutoff value below which the stated fraction of the distribution lies; the 0.975 quantile is the critical value defined above."*
3. **"rejects" / "rejection" (`:11`, `:13`).** Does technical work with no gloss. Dictate at `:11`: *"to reject means to declare that comparison's difference is not zero at the compared threshold."*

`KEY_FROZEN`, `VALUE_UNISSUED`, "insertion anchor" (all `:109`) and Holm (`:11`) are correctly glossed at first use and precede every later use — verified by first-occurrence line numbers. C3 and C2 are satisfied.

## 6. Bench

```
$ python3 -m unittest tests.test_dependence_sensitivity tests.test_paper_terms_lint
......................
Ran 22 tests in 4.414s
OK
MUTATION_TABLE zero survivors: sheet-number=0, command=0, draft-anchor=0, refusal-delete-add=0

$ git diff --check     → clean (no output)
$ git status --short   → clean (no output; the round is committed at 8de7a9d7)
```

## 7. Assessment

Round 3 is a real advance on rounds 1–2: the `:97` command defect is genuinely cured and now replays, the A2 anchor is correct, all C1 arithmetic verifies independently (I reproduced every p-value by quadrature without the repo's code), and rules 3 and 5 are honestly implemented. But the round did what the previous three did — it certified the surfaces THE RULE enumerated (numbers, commands, anchors, refusal rows) and left the surface next to them free. That surface is **the sheet's prose claims**: the words that say what a gate did, what a command shows, and what a definition requires. Eight survivors, five of them in that class. Rule 2 is a fingerprint rather than a binding, and rule 4's binding half is a name-existence check. Plus one factually wrong pair of citations sitting in the sheet at `:11` and `:13`.

VERDICT: REFUTE