# 74a — COLD GATE #4 (dependence): second fix round on W2a

Fresh Fable instance over a mechanically assembled packet (terra 74, the r6 test, the magistrate's bench r7 `2fe7370e`, replay result). Verdict RATIFY WITH AMENDMENT: r7 killed the literal but pushed it one frame up (a literal at the `sheet_slots` threading site and a stdout-sniffed word both survived). Amendment landed at the bench as `6e03a5c5` (r7b); the magistrate replayed (e) and (c2) on a scratch copy — both killed, 29 tests OK. Council-log note: the r6 brief's cure sentence was the cause (Q3) — the brief lacked the word 'counterfactual' and a required call site. Verbatim:

---

# Cold-gate ruling: DEP W2a, second fix round (r7 @ 2fe7370e, branch head 06500aad)

Worktree verified clean at 06500aad; all mutations run on a scratch copy, script restored byte-identical after each.

## Q1 — Does r7 structurally kill W2a?

Partly. r7's test (`tests/test_dependence_sensitivity.py:1317-1334`) calls `_execute_sheet_command` with synthetic agree/disagree payloads and asserts the third return value, so it kills a literal in the `return` at `scripts/dependence_sensitivity.py:446`. But it does not kill every single-site variant of the word derivation, because its synthetic payload has one key and no decoy tokens. Battery on the copy (`python3 -m unittest tests.test_dependence_sensitivity`, tracked sheet byte-identical / `--check-sheet` rc 0 in every SURVIVED row):

| Mutation | Result |
|---|---|
| (a) `:446` -> `"agree"` literal | KILLED — `test_agreement_word_is_derived_from_the_command_payload_not_a_literal` |
| (b) `:446` -> `"agree" if agreement is not False else "disagree"`, `:441-442` guard deleted (naive) | KILLED, but SPURIOUSLY: 3 failures (`test_rendered_sheet_is_byte_equal…`, `test_tail_replay_formula…`, `test_renderer_refuses…`) all caused by deleting two lines shifting the AST line-citation slots (`:502-503`), not by word logic |
| (b') same, line-count preserved (`if False: pass`) | SURVIVED — 27 OK. No test exercises the non-boolean guard at `:441` (grep "non-boolean" in tests: zero hits) |
| (c1) `:446` -> `"agree" if "true" in fragment else "disagree"` | SURVIVED — but this is an EQUIVALENT mutant: `fragment` (`:443`) is a pure function of `agreement`, so no test can or should kill it |
| (c2) `:446` -> `"agree" if "true" in completed.stdout else "disagree"` | SURVIVED — a REAL latent defect: both real payloads carry 4 `true` and 4 `false` tokens, so a disagreeing example would render "agree"; r7's one-key payload cannot see it |
| (d) `:438` -> `agreement = True` | KILLED — 6 errors + 1 failure (fragment guard at `:444` raises on the disagreement command) |

So r7 kills the mutation as literally named (W2a) but leaves one non-equivalent sibling at the same site (c2) and the guard-deletion variant (b') alive.

## Q2 — Is r7 an honest test of the production path?

No: it tests the private helper only. `sheet_slots()` does thread the value (`:506-508` unpacks `example_agreement_word`; `:589` puts it in the slot), but nothing pins that threading. Mutation (e) replacing `:589` with `"example_agreement_word": "agree"` SURVIVED (27 OK, `--check-sheet` rc 0, sheet byte-identical); so did (f) `_gate_table(True) and "agree"`. The r6 test (`:1271-1315`) reads the tracked document and the r7 test reads the helper; the only tests touching `sheet_slots()` (`:1137`, `:1170`, `:1247`) check citations, slot-name closure, and `correlation_abs_limit`, never the agreement word. terra's F1 prescription explicitly said "against freshly rendered output or `sheet_slots()`"; r7 chose neither. W2a, read as the defect class ("a literal in the render path passes while today's example agrees"), is therefore NOT closed — the literal has merely been pushed one frame up.

## Q3 — Was the r6 brief the cause?

Yes, one sentence: "assert the rendered word equals the word implied by the example payload" is satisfied by comparing the tracked document to today's (agreeing) payload, which is exactly what Sol wrote at `:1271-1315`, and that assertion is provably incapable of distinguishing a derived word from a literal "agree" while the example agrees — the brief lacked the word "counterfactual" and a required call site (`sheet_slots()`/`render_sheet()`), so the fix round failed by construction, not by execution.

## Q4 — VERDICT

**VERDICT: RATIFY WITH AMENDMENT.** Keep the r7 test (it is correct and kills (a)/(d)); add the following test, prototyped and verified on the copy (unmutated suite 28/29 OK; kills (a), (c2), (e), and (f); (b') killed by the second addition):

```python
def test_sheet_slots_threads_a_disagreeing_example_word_through_the_production_path(self) -> None:
    _, disagreement_command = dependence_sensitivity._sheet_commands()
    with patch.object(dependence_sensitivity, "_sheet_commands",
                      return_value=(disagreement_command, disagreement_command)):
        slots = dependence_sensitivity.sheet_slots(TEMPLATE.read_text(encoding="utf-8"))
    self.assertEqual(slots["example_agreement_word"], "disagree")
    self.assertEqual(slots["example_stdout_fragment"], '"direction_gate_outcomes_agree": false')
```

This swaps the REAL disagreement command (payload `direction_gate_outcomes_agree: false`, verified) into the example seat, so the full production path runs with a disagreeing payload and decoy `true` tokens, no synthetic schema needed. Should-fix (not blocking): add a 5-line guard test feeding `{"comparison": {"direction_gate_outcomes_agree": 0}}` to `_execute_sheet_command` and asserting `SheetRenderError` matching "non-boolean"; verified it kills (b'). Amendment goes in `tests/test_dependence_sensitivity.py` only; no script change.

**PR readiness:** on the evidence I saw, the branch is green but NOT ready for PR until the amendment lands, because a survivor of the same class the cold gate was convened for (e at `:589`) is still alive. Re-run on the worktree at 06500aad (clean, `git status --short` empty):

```
Ran 27 tests in 3.127s
OK
check-sheet rc=0
render cmp rc=0        # --render-sheet | cmp docs/paper/round7/dependence-sensitivity.md
```

Cosmetic: the 06500aad commit message says "25 tests OK"; the suite at that head has 27. Fix the count in the PR body, not by rewriting history.

Scratch artefacts: `/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/coldgate-dep-copy/{mutate.py,tests/test_dependence_sensitivity.py}` (the copy's test file contains both proposed tests, ready to lift).