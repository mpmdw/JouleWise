# REFUTE-F — PEDAGOGY lens (Sol xhigh read-only + bridge replay)

Object: `feat/2026-09-02-paper-f` @ 4cb31a75 vs main 33290b8b, worktree `/Users/edr/code/JouleWise-wt-paper-f`. Sol run key `20260904T022624Z-21470-sol-out` (gpt-5.6-sol, xhigh, `CODEX_SERVICE_TIER=default`, sandbox read-only, `WRITE_SCOPE: []`); final message `$TMPDIR/refuter-F/sol-out.md`. Every row below was re-read by me in reader order; Sol's verdicts were adjudicated, not copied. No writes under any checkout; probes under `$TMPDIR/refuter-F/probes`.

## A. 24-row verdicts (line = HEAD 4cb31a75)

| # | Line | Verdict | Evidence |
|--:|--:|---|---|
| 1 | 128 | SHOULD-FIX | "each run (member) of a block" — "block" defined in the NEXT sentence (:128-129). Swap the two sentences. |
| 2 | 129-132 | HOLDS | block, sign, shared/local built in words. |
| 3 | 147 | HOLDS | chain-of-thought gloss. |
| 4 | 174 | HOLDS (pedagogy) | "declared machine state, meaning…"; "frozen means…". NIT: "the frozen plan" — "plan" first appears here, unintroduced. (Fact-lens dispute in 02-refuter is out of my lens.) |
| 5 | 176 | FAILS | "checks defined in Appendix A.3.5", "limits defined in Appendix A.3.7" — pointers only, no plain-words gloss; ledger :1627 mislabels this "glossed-at-first-use". |
| 6 | 178 | HOLDS | endpoint, four constraints, four allowances in words; A.3.3 pointer is supplementary. |
| 7 | 180 | HOLDS | |
| 8 | 184-185 | FAILS | "entry check (the admission gate of Section 5)": "admitted/admission" is built at :244 (§3), later; gloss = forward pointer + unbuilt term. "admission gate" existed in base only in the Fig. 2 caption (:177); the cure added a prose use. |
| 9 | 184-187 | HOLDS | "drift" plain English. |
| 10 | 194-196 | HOLDS, NIT | "mean idle power" is plain English; procedure arrives :894. Sol's "blocker" rejected. |
| 11 | 174 | HOLDS | |
| 12 | 267-268 | HOLDS | code names gone (grep). |
| 13 | 317-318 | HOLDS | |
| 14 | 324-325 | HOLDS (pedagogy) | surviving sentence reads cleanly. Fact-lens (02-refuter B1) disputes the deletion — not adjudicated here. |
| 15 | 235-252, 336-341 | FAILS | §3 still asks four questions (:235-244) and builds workload-response (:247-251) + null-test interval (:253-270) calculations; table answers two. Seat's own F1. :1211-1213 "workload levels" is Appendix reader text, still unlisted. |
| 16 | 399-405 | SHOULD-FIX | "retired calculation" named, explained next sentence (ok); "after a fixed widening factor" never built (widened by what, how much?). "point-only value" is built at :256, fine. |
| 17 | 551-553 | HOLDS | |
| 18 | 741-743 | HOLDS | |
| 19 | 806-810 | FAILS | kind list glosses with "joint movement of interpolation edges" — "interpolation" occurs nowhere earlier (grep: first hit :808). |
| 20 | 102-105 | HOLDS | NIT: "power counter" audience vocabulary. |
| 21 | 123-126, 538 | HOLDS | `U_edge` grep empty; `\mathrm{corner}` :538 is after §1 home. |
| 22 | 118-121 | HOLDS, SHOULD-FIX readability | see §C. |
| 23 | 846 | FAILS | "Figure 3 shows…" but no `![Figure 3…](…)` embed exists (only Fig 1 :168, Fig 2 :206); SVG on disk is not in the paper. The cure replaced an honest build marker with a dangling reference. |
| 24 | §6 | N/A | §6 sha256 `638a3046e7c91b97` identical base/HEAD. |

## B. Matcher probes (`PAPER_FIRST_USE_DRAFT` scratch copies, injected in §1 after :105; CAUGHT = test FAILED)

| Form | Injected | Result |
|---|---|---|
| line-wrap split compound | `The entry` ⏎ `check is applied` | **MISSED** |
| hyphen line-wrap | `close-` ⏎ `out artifact` | **MISSED** |
| derivational noun | `Admission of a bundle` (ledger "admitted") | **MISSED** |
| verb form | `We freeze the plan` (ledger "frozen") | **MISSED** |
| en-dash compound | `close–out artifact` | **MISSED** |
| bare adjective | `is resolvable` (ledger "not resolvable") | **MISSED** |
| modifier inserted | `idle-subtracted request energy` | **MISSED** |
| possessive plural | `reference runs'` | CAUGHT |
| capitalized hyphenated | `Entry-Check` | CAUGHT |
| spaced compound | `null test blocks` | CAUGHT |
| singular | `reference run` | CAUGHT |
| backticked / table cell | `` `close-out artifact` `` / `\| close-out artifact \|` | CAUGHT |
| spaced plural | `deterministic bound kinds` | CAUGHT |
| heading (Sol) | `### Entry check` | MISSED (by design, skipped) |
| `$U_{\rm point}$` (Sol) | | MISSED but contrived: draft has 0 `$`-math uses |

Real-prose proof of the wrap gap: scanning HEAD with paragraph-joined text finds `:475-476` "before the later small-sample ⏎ multiplier" — a forward reference in "Comparing…" before the term's ledger home; invisible to old and new matchers; pre-existing in base. Real-prose proof of the derivational gap: row 8 above (":185 admission" vs ":244 admitted") passes the ledger.

## C. Scope paragraph + naming bridge

§4 :679-682: "the safeguards used to publish the final **resolution bound**… The final resolution bound is called the **cell floor** in the artifacts." §1 :118-121 states the same relation (resolution bound = detection floor; final value after §4 safeguards = cell floor). Semantics HOLD; lexicon row agrees. Parsability: the subject "Its resolution bound" is separated from its verb by a 20-word interruption that carries its own "is" ("…its final value… is what the artifacts call the cell floor—is the largest…"). SHOULD-FIX: two sentences — define the bound, then "This bound is also called the **detection floor**; its final value, after the safeguards of Section 4, is what the artifacts call the **cell floor**." (bold terms stay on one physical line). Scope paragraph HOLDS.

## D. Severity-tiered findings

BLOCKER (cure does not cure, per charge criterion)
- P-B1 row 23 `:846` — asserted figure not in the Markdown. Fix: embed `figures/fig3_decision_gates.svg` with a caption.
- P-B2 row 15 `:235-270` vs table `:336-341` — orphaned questions/calculations; needs the ruling the seat requested (F1 options i–iii).
- P-B3 row 8 `:185` — gloss via unbuilt "admission gate". Fix: "the **entry check**, the pass/fail checks on recorded machine state that a stage must satisfy before its first run is measured (Section 5)".
- P-B4 row 5 `:176` — appendix pointers in place of glosses; also ledger status mislabel `:1627`.
- P-B5 row 19 `:808` — "interpolation edges" unbuilt.
- P-B6 matcher `tests/test_paper_first_use_ledger.py:143-145` — per-physical-line search misses wrapped compounds; real instance `:475-476`. Fix: match on paragraph-joined text with a line map.

SHOULD-FIX
- row 1 `:128` sentence order; row 16 `:404` "widening factor"; row 22 `:118-121` split appositive.
- matcher: derivational/verb forms (admission/admitted, freeze/frozen), en-dash, inserted modifiers, bare adjective — add stem alternatives to the ledger rows rather than a stemmer.

NIT: row 4 "plan"; row 10/18 "mean idle power"; row 20 "power counter"; headings skipped by design; Sol S1 (`$`-math) contrived.

## E. Executed evidence

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger
Ran 5 tests in 1.091s  OK
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_paper*'
Ran 70 tests in 611.617s  OK (skipped=3)
```
Sol's own: ledger `Ran 5 OK`; `test_paper_build FAILED (errors=3)` = read-only sandbox cannot mkdtemp (environmental; my replay above passes). Worktree `git status` clean at 4cb31a75 before/after probes.

## F. Process notes

- Sol wrapper exit rc=77 `SCOPE_VIOLATION/failed_preserved` is a FALSE POSITIVE: the flagged path `docs/process_traces/2026-09-02-paper-f/02-refuter-fact-regression.md` is commit 62e60c73 (Ed R, 19:37:35, the Opus fact/regression refuter's report) landing on the branch mid-run; Sol ran read-only with `head_end` = 4cb31a75. The worktree HEAD is now 62e60c73; the reviewed object is unchanged. Concurrent seats committing to a branch under an audited run will keep tripping this check.
- Sol's envelope was valid and final (`claude-codex-report/v1`, status findings, completion partial). Sol tiered 9 rows "blocker"; I rejected rows 1, 10, 16, 18 downward with reasons in table A.
- Cross-lens: 02-refuter (fact lens) disputes cures 4 and 14 on factual grounds; my HOLDS on those rows are pedagogy-only.
