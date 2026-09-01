# Round-7 structural-edits and plan-fix implementation record

- Date: 2026-08-31
- Genre: implementation
- Worker: Codex delegated from Claude Fable magistrate T28; hop depth exhausted
- Frozen input: `docs/paper/draft-v1.md`, read-only, SHA-256 `939dfa23730a22d35e02154d7aa7904f396364d55c128e6715c72b849eaf39ab`
- Exhaustive write scope: `docs/paper/round7/structural-edits.md`, `docs/paper/round7/retensing-plan.md`, and this record

## Outcome

D-1 and D-2 are implemented. The new structural sheet builds the registered full-floor ratio `R`, the comparative shared/local replay `R_cm`, the twofold threshold and its reason, the pilot-only worked example, the A/B/B/A sign convention, both retired fixed-256 survivors, the surviving conclusion criterion, and every `_v4` survivor named by D-1. The plan fixes every plan-local blocker and all 15 should-fixes accepted by the pedagogy adjudication.

The only unresolved authority is the exact Methods home of the ruled subtitle-branch sentence. Structural row S04 and plan block H48 supply the sentence and mark its placement before draft line 187 as **PROPOSED**. The lead must accept or relocate that sentence before substitution. No placement authority was invented.

## Authorities applied

- `05-ADJUDICATION-DISPOSITION.md` D-1 and D-2.
- `04-pedagogy-adjudication-opus.md`, including every exact R/BL/SF defect.
- `docs/decision_log.md` D-165 body and R-5 completion; D-166 as amended in its binding index row; D-164's `_v4`-never-collected statement.
- `06-COLD-GATE-RULING.md` R-1, R-2, and R-4.
- `configs/campaigns/d117_contrast_v5/generate_configs.py`: the registered shared/local split, one common shared sign, per-block local signs, full comparative corner re-evaluation, and ratio read-back.
- `docs/paper/results-fill-registry.md`: exact `_v5`, `[PREFILL_LENGTH]`, `R`, `R_cm`, `not_applicable`, and refusal-token vocabulary.

## Per-blocker disposition map

| ID | Fix location | Disposition |
|---|---|---|
| R1 | structural S01, S02, S08 | Replaces bare exceedance with full-floor `R`, builds `>= 2` and exact equality, explains the safety factor, labels 10.92/5.92/7.02 as pilot evidence, and removes the surviving conclusion criterion. |
| R2 | structural S03 | Reconstructs shared and local widths, enumerates one shared sign across blocks plus independent local signs, re-evaluates the full comparative floor, defines `R_cm`, states withdrawal, and explains absolute cancellation. |
| BL-3 | plan Item 10 A/B | Carries the complete-bound-after-corners divided by complete-point-bound clause before reporting either quotient. |
| BL-4 | structural S05; aligned plan H39 | Expands A/B/B/A, defines `A_1`, `B_1`, `B_2`, and `A_2`, preserves the formula, and states that a positive result means B used more energy. |
| BL-5 | plan H21 A/B/C | Defines each per-token denominator as the runtime-observed count and glosses the requested runtime count and library-reported count that may not replace it. |
| BL-6 | plan H14 A/B/C | Defines the Qwen3 chat template as the fixed input-formatting rule and “thinking disabled” as switching off the optional reasoning-output mode. |
| BL-7 | plan H02 | Marks every branch superseded by Item 10, exactly as H10, so no meta-prose is inserted. |
| BL-8 | plan H48; structural S04 | Supplies the exact Methods sentence. Its proposed home after S03 and before line 187 is explicitly non-authoritative pending lead ruling. |
| BL-9 | structural S06, S07 | Replaces `fixed-p256` and the “256-token prefill arm” with the four-length G2-a vocabulary while preserving `UNRESOLVED-UNTIL-G2A`. |
| BL-10 | structural S09, S10, S11; plan H28 | Makes Discussion, Future Work, and both consecutive Conclusion paragraphs consistently `_v5`. |

## Per-should-fix disposition map

| ID | Fix location | Disposition |
|---|---|---|
| SF-1 | H06 | Glosses “registered” at Abstract first use as fixed before collection. |
| SF-2 | H22; structural S03 | Names shared timing error and its energy displacement, states the uniform-displacement idealization, and gives the exact cancellation mechanism. |
| SF-3 | H15, H46 | Explains five as a two-record safety margin above three, moves the no-clearing-length fallback out of refusal semantics, and glosses the literal refusal string as a five-record design minimum. |
| SF-4 | H20, H21, H26 | Restores definitions of Gross J/request, per-token, sizing, signed-clearance, and floor-gate columns before stating why values are absent. |
| SF-5 | H23 | Restores the point-estimate column definition as the mean of ten block differences before its value/absence. |
| SF-6 | H41, H44 | Names Appendix A.3.1 before “worked record” and rounds body-prose figures. |
| SF-7 | H31, H43 | Moves both additions into prose after Table 1 and explicitly forbids insertion inside table cells. |
| SF-8 | H32 | Splits the mechanism into readable sentences, removes camera-ready process prose, and preserves the same-session/same-manifest operative rule. |
| SF-9 | H34, H35 | Retains an explicit pulse-to-inference caveat at both points where calibration is applied. |
| SF-10 | H40 | Defines *direction unresolved*: the magnitude clears the floor, the interval does not settle direction, and no claim is made. |
| SF-11 | H18–H26 | Retenses the substituted §6 analysis and table-result sentences consistently in the past. |
| SF-12 | H26, H46 | Defines F as the applicable cell floor and B as the separately registered claim-side bound. |
| SF-13 | H45 | Replaces `real_prompts_v1` in the paper table with the prompt set and execution policy in plain words. |
| SF-14 | H15, H46 | Replaces unglossed rung/count-floor prose with ordered lengths, the 5-versus-3 rationale, and a plain explanation of the mandated literal refusal. |
| SF-15 | H26 | Removes the future-conditional “when its authenticated outcome issues”; no outcome is reported because no authenticated artifact issued it. |

## Frozen-quote grep verification

Command:

```sh
quote_index=0; rc=0; while IFS= read -r quote; do quote_index=$((quote_index + 1)); if match=$(rg -nF -- "$quote" docs/paper/draft-v1.md); then draft_line=${match%%:*}; printf 'PASS quote-%02d draft-line=%s\n' "$quote_index" "$draft_line"; else printf 'FAIL quote-%02d\n' "$quote_index"; rc=1; fi; done < <(awk '/^> /{quote=$0; sub(/^> /,"",quote); print quote}' docs/paper/round7/structural-edits.md); exit "$rc"
```

Observed list:

```text
PASS quote-01 draft-line=21   # S01
PASS quote-02 draft-line=185  # S02
PASS quote-03 draft-line=187  # S03 anchor
PASS quote-04 draft-line=187  # S04 anchor
PASS quote-05 draft-line=55   # S05 passage 1
PASS quote-06 draft-line=57   # S05 passage 2
PASS quote-07 draft-line=198  # S06
PASS quote-08 draft-line=260  # S07
PASS quote-09 draft-line=356  # S08
PASS quote-10 draft-line=294  # S09
PASS quote-11 draft-line=314  # S10
PASS quote-12 draft-line=358  # S11
```

Exit code: `0`.

## Verification

### Required first-use lint

```sh
/Users/edr/code/JouleWise/.venv/bin/python scripts/paper_terms_lint.py lint --draft docs/paper/draft-v1.md --plan docs/paper/round7/retensing-plan.md --lexicon docs/paper/round7/built-terms-lexicon.md
```

Observed tail:

```text
0 finding(s) across 94 sentence(s)
```

Exit code: `0`.

### Required unit tests

```sh
python3 -m unittest tests.test_paper_terms_lint tests.test_docs_freshness
```

Observed tail:

```text
.........
----------------------------------------------------------------------
Ran 9 tests in 0.730s

OK
```

Exit code: `0`.

### Scoped whitespace check

```sh
git diff --check -- docs/paper/round7/retensing-plan.md && ! rg -n '[ \t]+$' docs/paper/round7/structural-edits.md docs/process_traces/2026-08-31-registry-v5/06-structural-round-record.md
```

Observed output: empty. Exit code: `0`.

## Scope and workspace

No file outside the three-path exhaustive `WRITE_SCOPE` was modified. The frozen draft, registry, generator, lexicon, lint script, tests, run state, task queue, and project-status files remained read-only. No commit was created.

## Next exact step

The lead rules or relocates the PROPOSED S04/H48 Methods placement, then submits `structural-edits.md` and `retensing-plan.md` together to one fresh pedagogy seat. If that seat fails them, the standing disposition requires a cold instance before any further writer round.

---

## Placement ratification (magistrate, 2026-08-31)

The PROPOSED Methods placement for the D-165 subtitle-branch-rule sentence —
after the shared/local replay construction and before frozen draft line 187 —
is RATIFIED: that is the first point where every term the sentence uses has
been built. The structural sheet's row is binding as written.
