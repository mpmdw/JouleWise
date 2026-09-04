```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"Claim falsified: 5 blockers, 3 should-fixes, and 2 nits; selectors/tests pass, but the branches fail first-use and result-completeness bars.","workspace":{"base_requested":"46fbf46d267a1971602a77f0ccfeafdcb29284a6","base_mode":"exact","head_start":"46fbf46d267a1971602a77f0ccfeafdcb29284a6","head_end":"46fbf46d267a1971602a77f0ccfeafdcb29284a6","upstream_end":"46fbf46d267a1971602a77f0ccfeafdcb29284a6","branch":"feat/2026-09-02-paper-g"},"pathspec":[],"unowned_dirty":[],"verdict":{"counts":{"blocker":5,"should_fix":3,"nit":2},"findings":[{"id":"F1","severity":"blocker","line":"draft-v2-skeleton.md:29,35,41"},{"id":"F2","severity":"blocker","line":"draft-v2-skeleton.md:29,35,1209,1215"},{"id":"F3","severity":"blocker","line":"draft-v2-skeleton.md:35,975,1215"},{"id":"F4","severity":"blocker","line":"draft-v2-skeleton.md:41,981-983,1221"},{"id":"F5","severity":"blocker","line":"draft-v2-skeleton.md:967,975,983,1209,1215,1221"},{"id":"F6","severity":"should_fix","line":"draft-v2-skeleton.md:967,975,983"},{"id":"F7","severity":"should_fix","line":"draft-v2-skeleton.md:27,33,39,963,971,979,1207,1213,1219"},{"id":"F8","severity":"should_fix","line":"draft-v2-skeleton.md:1544-1667"},{"id":"F9","severity":"nit","line":"draft-v2-skeleton.md:967,975,983"},{"id":"F10","severity":"nit","line":"select_outcome_branches.py:53"}]},"verification":[{"id":"V1","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_paper*'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 68 tests in 633.308s","","OK (skipped=3)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=3\\)"}},{"id":"V2","kind":"smoke","cmd":"python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output $TMPDIR/sel-{A,B,REFUSAL}.md --outcome {A,B,REFUSAL}","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["A/B/REFUSAL selected; each markers=0, labels=0"]},"expected":{"exit_code":0,"tail_regex":"markers=0.*labels=0"}},{"id":"V3","kind":"inspection","cmd":"git -C /Users/edr/code/JouleWise-wt-paper-g diff main --stat && git -C /Users/edr/code/JouleWise-wt-paper-g status --short","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["5 files changed, 456 insertions(+), 69 deletions(-)","status --short: empty"]},"expected":{"exit_code":0,"tail_regex":"status --short: empty"}}],"flags":[{"id":"F1","kind":"environment","level":"nonblocking","text":"Managed writer rejected the requested external /private/tmp report path.","needs":"Consume the complete fallback report below."},{"id":"F2","kind":"lead_ruling","level":"nonblocking","text":"Section-4 Refusal uses missing/unauthenticated/zero-denominator ratios; retensing Outcome C/H04 instead use excluded windows or absent verdicts.","needs":"Choose one predicate and synchronize Section 4, Outcome C, H04, H27-H29, and selector prose."}]}
```

## Report body (fallback)

# REFUTE-G — pedagogy lens

Verdict: **BLOCKER 5 / SHOULD-FIX 3 / NIT 2**.

## Findings

| ID | Severity | Falsifying evidence and cure |
|---|---|---|
| F1 | BLOCKER | Abstract lines 29/35/41 first-use “commanded graphics-processor pulses,” “uninterrupted collection,” “edge behavior,” “largest spurious difference,” “recorded edge,” shared four-run timing, overlap sufficiency, and internal fields before their builds at 49-87, 116-136, 367-576, 925-950, and 1014-1018. Cure: gloss physically in place. |
| F2 | BLOCKER | A/B only say the Qwen pair “exercised/demonstrates” the rule. Main required its decision in Abstract and Conclusion; DS-32/PG-08 remain verdict rows at registry 882/891. Cure: print both authenticated verdicts; Refusal must print its actual reason. |
| F3 | BLOCKER | Main:800 says “Every required ratio was authenticated and evaluable” and “report each failed component”; plan:24 says “states which component failed.” Lines 35/975/1215 omit authentication and name no failure. Cure: add predicates and component-specific result slots. |
| F4 | BLOCKER | Main:802-804 binds Refusal to missing/unauthenticated/zero denominator; plan:26/H27-C:393 bind excluded windows or absent verdicts. Lines 41/983/1221 print no affected arm or reason. Heading 981 also differs from H04-C:101. Cure: ruling plus synchronized predicate/reason. |
| F5 | BLOCKER | Main:994-995 requires whether the inserted-gap check supported transfer. A/B merely remain conditional; Refusal declares transfer untested although the independent check may pass. No fill/selector state exists. Cure: add a transfer-result slot independent of A/B/Refusal. |
| F6 | SHOULD-FIX | Lines 967/975/983 never build “characterize the named workload boundary” or pre-collection “size the comparison.” Line 975’s repeats-can’t-“repair” claim and 983’s refusal-established practice claim are absent from H27. Cure: define operations and limit claims to the governing forms. |
| F7 | SHOULD-FIX | Brief:12 says match main:788-808 exactly, whose labels include predicates. Nine blocks use one-word labels and the selector hard-codes them. Cure: retain/remove the full governed labels mechanically. |
| F8 | SHOULD-FIX | Ledger 1544-1667 still treats Introduction as first use and inventories none of the new Abstract vocabulary; 68 tests pass despite F1. Cure: test each selected draft’s real reading order. |
| F9 | NIT | Section 7 uses DG-050/051/052, registry 622-624’s Section-3 rows, although dedicated DG-099/100/101 rows exist at 671-673. Values agree. Cure: use dedicated rows. |
| F10 | NIT | Selector line 53 inserts one newline and strips the rest; selected paragraphs directly touch the next heading. Cure: insert two newlines. |

## First-use table

`S` = same-use gloss; `B` = earlier body build; `L` = later, invalid for Abstract.

| Term | First use | Build | Grade |
|---|---:|---:|:---:|
| physical ambiguity | 29/35/41 | S | P |
| power sample | 29/35/41 | S: averages over time | P |
| span of time | 29/35/41 | ordinary | P |
| commanded graphics-processor pulses | 29/35/41 | L126 | F |
| uninterrupted collection | 29/35/41 | L65/126 | F |
| pulse-derived limit | 29/35/41 | S | P |
| edge behavior | 29/35/41 | L991-1002 | F |
| group with same work…power definition | 29/35 | S; scope incomplete | P* |
| largest spurious difference | 29/35 | L384-477 | F |
| recorded edge | 29/35 | L49-56/400 | F |
| permitted edge movement | 29/35 | S | P |
| repeated measurements | 29/35 | audience vocabulary | P |
| twice the first | 29 | S operands | P |
| timing error common to four-run comparison | 29/35 | L496-569 | F |
| moved together | 29/35 | S | P |
| decision rule | 29/35 | S after colon | P |
| direction | 29/35/41 | ordinary signed result | P |
| full range after uncertainties | 29/35 | S | P |
| direction fixed before collection | 29/35 | S | P |
| short-input diagnostic records | 29/35/41 | L925-950 | F |
| overlapping power samples | 29/35/41 | L925-936 | F |
| too few / enough | 29/35/41 | L925-950: 3/5 rules | F |
| internal processor-power fields | 29/35/41 | L116/1014 | F |
| quotient | 35 | S: second/first | P |
| twofold boundary contribution | 35/41 or 965 | S/B378-474 | P |
| component | B35 | L384-406 | F(B) |
| verified against source | R41 | L479-482 | F |
| repeated-measurement limit of zero | R41 | L400-477 | F |
| fixed rule | R41 | S predicates | P |
| opposite / evaluated opposite | R41/1221 | NONE | F |
| A heading: twofold contribution | 965 | B378-474 | P |
| B heading: below-two ratio | 973 | B463-477 | P |
| Refusal heading: unevaluable | 981 | B765-767 | P* |
| independent-edge ratio | 463; branch 967+ | S formula/cutoff | P |
| shared-error ratio | 568; branch 967+ | S replay/formula | P |
| configuration cell | 967/975/983 | B75/384 | P |
| point-only component | 334; branch 967+ | B334/400 | P |
| named workload boundary | 967/975/983 | NONE | F |
| characterize boundary | 967/975/983 | NONE | F |
| size comparison against bound | 967/975 | NONE | F |
| inserted-gap check | 759; branch 967+ | S | P |
| non-claim measurements | 967/975/983 | B333-343 + S | P |
| campaign result | 334 | ordinary contrast | P |
| repair a below-two result | 975 | NONE | F |
| usable configuration cell | 983/1221 | B384/400 | P |
| recorded reason / incomplete evidence | 983 | B810-831 | P |
| clock placement | 1209/1215/1221 | B65-73 | P |
| false phase-energy difference | 77 | B75-87/367 | P |
| repeat-to-repeat variation | Conclusion | B386/666 | P |
| comparative ratio/shared movement | Conclusion | B496-576 | P |
| minimum overlap rule | Conclusion | B925-950 | P |
| internal-counter configuration | Conclusion | B116/1004 | P |
| model-size scaling law | 967/975/983 | B89-105 | P |

`P*` passes first-use only; F1/F4/F6 identify semantic drift.

## Branch completeness

| Section | A | B | Refusal |
|---|---|---|---|
| Abstract | NO/PARTIAL: verdict and names absent | NO: auth, failed components, verdict absent | NO: operands/reason absent; plan conflict |
| Section 7 | NO/PARTIAL: transfer result absent | NO: failures promised, not reported | NO: H27-C drift; extra practice claim |
| Conclusion | NO/PARTIAL: verdict/transfer absent | NO: failures/verdict/transfer absent | NO: reason absent; transfer overclaim |

Semantic anchor: A’s “second limit was at least twice the first” preserves main A’s doubling. B does not preserve “Every required ratio was authenticated and evaluable.” Refusal’s “absent…unverified…zero denominator” preserves Section 4 but not plan Outcome C.

## Replication bar: selected Abstract only

| Branch | Physical ambiguity | Compared quantities | Criterion | Conclusion |
|---|---|---|---|---|
| A | PASS | broad PASS | PASS | FAIL: pair verdict/configuration absent |
| B | PASS | broad PASS | PASS | FAIL: components/pair verdict absent |
| Refusal | PASS | FAIL | PASS | FAIL: actual arm/reason absent |

## Flagged-item grades

1. **UPHOLD:** H04-C wording differs; Section 4’s broader Refusal currently binds, exposing a required ruling.
2. **UPHOLD:** one-word labels violate brief:12/main:788-808.
3. **UPHOLD:** DS-32/PG-08 omission is F2 BLOCKER.
4. **OVERTURN:** D belongs only where the null row is discussed—plan:28,545-557 and branch-selection:36-42 route it to Sections 4/6.

## Executed evidence

- Selectors: A/B/REFUSAL exit 0; each leaves zero labels and zero branch markers.
- Nine paragraphs: 27 marker occurrences; unique DG-050/051/052/067/068/069, all numeric registry rows. No other DS/PG/D-1xx/V5-ID/kernel/seat/`_v5` shorthand.
- Suite tail:

```text
............
----------------------------------------------------------------------
Ran 68 tests in 633.308s

OK (skipped=3)
```

- `git diff main --stat`: 5 files, 456 insertions, 69 deletions. `git status --short`: empty; HEAD/upstream unchanged.
- Seat-table delta: its sentence-grouped rows provide no first-use/build line pairs and mark every row PASS. It omits or grades differently every `F` row above, notably pulses/window/edge behavior, recorded edge, shared replay, overlap criterion, internal fields, authentication, denominator, named-boundary operations, “repair,” and “evaluated opposite.”

## Residual risk

The green suite validates selector/ledger structure, not the prose’s semantic first-use order. No live or quiet-machine work was performed.