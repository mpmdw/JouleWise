```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"findings","completion":"complete","summary":"All accepted round-3 paper fixes implemented; 42 final tests and 43-value replay pass. Interrupted baseline sequencing error is disclosed.","workspace":{"base_requested":"f00a2dde","base_mode":"exact","head_start":"f00a2dde6caffa8e8d8209e109c093d6ee21dc54","head_end":"f00a2dde6caffa8e8d8209e109c093d6ee21dc54","upstream_end":"f00a2dde6caffa8e8d8209e109c093d6ee21dc54","branch":"feat/2026-09-05-paper-m"},"pathspec":["docs/paper/draft-v2-skeleton.md","docs/paper/figures/README.md","docs/paper/figures/build_mechanism_figures.py","docs/paper/figures/figA4_clock_polygon.svg","docs/paper/figures/figA4_shared_signs.svg","docs/paper/figures/figA5_clock_polygon.svg","docs/paper/figures/figA5_shared_signs.svg","docs/paper/figures/figA_partial_record_enclosure.json","docs/paper/figures/figA_partial_record_enclosure.svg","docs/paper/protocol/first-use-audit-ledger.md","docs/paper/protocol/prospective-comparison-protocol.md","docs/paper/results-fill-registry.md","docs/process_traces/2026-09-05-paper-m/10-fix-round-3-report.md","tests/test_paper_first_use_ledger.py","tests/test_paper_terms_lint.py"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"ready"},"verification":[{"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 11 tests in 2.413s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_terms_lint","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 16 tests in 2.759s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_select_outcome_branches","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 5 tests in 0.608s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_replay_fence","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 10 tests in 26.666s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V5","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 scripts/check_paper_replay_fence.py --corpus-root /Users/edr/code/JouleWise","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["MEMBER 20260722T145535-e941c821","COMPARED 43","MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"COMPARED 43\\nMISMATCHES 0$"}},{"id":"V6","kind":"lint","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 docs/paper/fill-rehearsal/select_outcome_branches.py --check-rendered docs/paper/draft-v2-skeleton.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["METHODS_DIAGNOSTIC validated; abstract_words=246, limit=250"]},"expected":{"exit_code":0,"tail_regex":"METHODS_DIAGNOSTIC validated; abstract_words=246, limit=250$"}},{"id":"B0","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 scripts/check_paper_replay_fence.py --corpus-root /Users/edr/code/JouleWise","cwd":".","observed":{"result":"fail","exit_code":130,"tail":["KeyboardInterrupt"]},"expected":{"exit_code":0,"tail_regex":"COMPARED 43\\nMISMATCHES 0$"}}],"flags":[{"id":"F1","kind":"verification_gap","level":"nonblocking","text":"During baseline preflight the standalone checker was mistakenly started before the replay-test process exited. The checker was interrupted (B0, exit 130); baseline replay tests passed and the checker was rerun successfully. Final V1–V5 ran strictly one at a time with the required corpus root, all green.","needs":"Lead should note the procedural deviation during final review."}]}
```

## Change

Applied only the accepted findings in `09-recheck-opus.md` and F1–F3 in `08-delta-round-2-astra.md`. Intake found no active stop card; the clean checkout exactly matched the requested branch and base. The explicit task selects agent-compatible paper work and overrides discovery-suite and lead-owned bookkeeping instructions. No commit, agent launcher, delegation, hardware measurement, or out-of-scope repository write occurred.

The following are current line numbers. A = `docs/paper/draft-v2-skeleton.md`; R = `docs/paper/results-fill-registry.md`; L = `docs/paper/protocol/first-use-audit-ledger.md`; P = `docs/paper/protocol/prospective-comparison-protocol.md`. Each row records finding → line → old → new.

| Finding | Current line / surface | Old | New |
|---|---|---|---|
| NF1 | A:568 | “retained historical sources in Section 4” within Section 4 | “retained historical sources below” |
| NF2, results | A:698 | “two records per bundle failed the count discipline for the 1.5B stack; three passed … three or four passed for 7B” | “Phases with only two overlapping records failed the three-record minimum: 37 of the 50 1.5B phases and none of the 50 7B phases, which overlapped three or four records each.” |
| NF2, Conclusion | A:936 | Repeated garbled “records … failed the count discipline” sentence | Phases fail the established **three-record minimum**, with the same explicit 37/50 1.5B and zero/50 7B qualification. No “count discipline” survives. |
| NF3 | A:692; R:1019–1020 | 7B passing counts without its duration mechanism | Prefill-duration medians **0.2815 s (7B)** and **0.1365 s (1.5B)**, individually bound by **DG-143** and **DG-144**, compared with the **120.9-ms** a10 record-width median. Longer phases leave more room for a complete middle record; duration alone does not establish overlap count. |
| NF3, width provenance | R:682 | DG-071 specified only the existing four-decimal display | Adds the active comparison’s one-decimal rounding of the same 120.9186-ms median to 120.9 ms. Its a10 source is explicit; no 7B record-width statistic is invented. |
| B4 residue | `docs/paper/figures/figA_partial_record_enclosure.svg`:2,6; A:1413 | Accessible title “SYNTHETIC P1”, visible title “Figure A1 · SYNTHETIC P1”, circular P1 gloss | Both titles use **SYNTHETIC**; the circular gloss is removed. |
| B4 reproduction | A:1452; R:961; figures README; A1 JSON:4 | Direct producer command would recreate the old label and its SVG hash | Printed A.6 command calls the unchanged numerical producer, removes its internal label from the two SVG titles, and fingerprints the displayed SVG. README and PE-01 disclose that presentation step. JSON changes only `figure.sha256`, to `39d113f80956b59e476c7989380fd814163c12a39ffee7b67930bfe869c967d5`. |
| NF4 | A:910 | “ten … forty … 50” | “10 … 40 … 50” |
| NF5 | Article A4/A5 image targets; figures builder:67,81; README:16–17; R:988 | Figure A4 loads `figA5_shared_signs.svg`; A5 loads `figA4_clock_polygon.svg` | Byte-identical renames to `figA4_shared_signs.svg` and `figA5_clock_polygon.svg`; article targets, builder destinations, README, and registry agree. |
| NF6 | A:841 | Comment says “Section 2 record definition” | “Section 1 record definition” |
| NF7 | A:9 | Abstract has 246/250 words | Abstract bytes unchanged: **246/250, four words of headroom**. This is informational, not a request to add words. |
| NF8 | A:46 | “parts” becomes “phases” without an explicit bridge | “Prompt processing and token generation are this paper’s two phases.” |
| NF9 | A:331,392; nine consequential L homes | One subsection over all of Section 3 | Adds “Moving edges and enumerating endpoints” and “Combining shared movements and local widths”; rebinds only ledger homes whose first uses fall under those headings. |
| Astra F1 | A:684,752 | “Accordingly, 37 failed”; “In r03 … two records fail the three-record cutoff” | “Accordingly, in this 1.5B population, 37 failed”; “In the 1.5B run r03 … this phase fails the three-record minimum.” |
| Astra F2, models | L:221–222; A:1053 | “The model” in Conclusion certified an affine clock relation “immediately below” | Separate `model/stack` row for the named Qwen populations and `The clock model` row explicitly bound to **A.3.3**; the appendix label now names that clock sense. |
| Astra F2, intervals | L:154–157; P:349 | Combined measurement/decision/deterministic row located at benchmark analyzer-duration usage | Splits analyzer reporting duration from the **statistical measurement interval** in **P.3**, whose first explicit definition is labelled accordingly. Separate decision-interval and deterministic-bound rows give their actual first homes and P.3 definition/disposition. |
| Astra F2, record support | L:153,178 | First “not resolvable” meant below-floor energy; other row sent that sense to article Section 4 | First use means insufficient three-record support; distinct cell-floor sense points to **protocol P.3**. |
| Astra F2, local width | L:135 | “Section 4 constructs the local half-width” | “Section 3 constructs the local half-width” |
| Astra F3 | R:19,1044 | Active census ends at DG-134, retiring DG-135–142 by implication | Active range extends through **DG-144**, including all eight accepted two-arm rows and both new median rows. Existing retired empirical comparison placements remain retired. |

Existing ledger and terms regression modules now check the selected semantic distinctions, qualified failure sentences, renamed figure targets, removal of the artwork label, new median suppliers, active census, and A1 regeneration. Selector and replay-fence code/tests required no changes.

The primary artifact at `/Users/edr/code/JouleWise/docs/process_traces/2026-08-09-prefill-phase-proof/results.json` is byte-identical to the tracked copy and hashes to `e93c1d9c9ccff764cb6c64379cc3551c710e63b38b5314569d89662d2b88d8b1`. The extended terms regression recomputes medians from the 50 per-bundle duration fields in each stack, then compares them to summaries and registry rows:

| Stack | Per-bundle median = artifact summary (s) | Article |
|---|---|---|
| 7B | 0.28151941299438477 | 0.2815 s |
| 1.5B | 0.13650262355804443 | 0.1365 s |

Exact final module/checker tails are pasted in V1–V5 above: **11 + 16 + 5 + 10 = 42 tests**, then **43 comparisons, zero mismatches**. V6 is direct selector validation. Additional read-only inspection intercepted `Path.write_text` in memory, verified all eight mechanism-builder SVG strings, executed the printed A.6 replay body and compared both outputs, checked rename bytes against HEAD, and parsed every article SVG link. Its literal output was:

```text
READER_FILLS 0
EMPIRICAL_BRANCHES 0
HIDDEN_PE01 1
Terms inventoried: 265; FAILS: 0.
ABSTRACT_BYTES_UNCHANGED
MECHANISM_SVGS_IDENTICAL 8
A1_ARTICLE_REPLAY_IDENTICAL 2
A4_A5_RENAMES_BYTE_IDENTICAL
ARTICLE_SVG_LINKS_XML_OK
```

Next exact step: lead reviews the uncommitted scoped diff and this report, including the disclosed preflight sequencing deviation, then owns final acceptance. No commit was made.

## Verification notes

Initial baseline modules passed (11, 16, 5, 10 tests). I misread an unfinished replay-test poll as completion and started the standalone checker too soon. I interrupted that checker with Ctrl-C; B0 records its `KeyboardInterrupt` and exit 130. A process-list inspection was sandbox-denied; no bypass was attempted. The replay-test process exited successfully, and a subsequent standalone baseline checker passed 43/43. This was a real violation of requested preflight sequencing, not a scientific test failure, and is not hidden by later green results.

After the final small wrapping and registry-table correction, V1–V5 ran in one sequential orchestration loop that awaited each process’s exit before starting the next. Every command used `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise` and disabled bytecode writes. No discovery suite or additional test module ran. These are retained-artifact and synthetic checks, not live hardware validation.

