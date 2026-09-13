```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"blocked","completion":"partial","summary":"Round-two edits and acceptance checks are complete; the required commit is blocked by read-only Git metadata.","workspace":{"base_requested":"482a0cc49995aba94f923956af60c547fde538c6","base_mode":"descendant","head_start":"73f7ac9f73c169aed0b1bf02d7f256c8db8c329e","head_end":"73f7ac9f73c169aed0b1bf02d7f256c8db8c329e","upstream_end":"c53d4227f2c175fc16220e4114d79de4555bc032","branch":"feat/2026-09-12-paper-n"},"pathspec":["docs/paper/draft-v2-skeleton.md","docs/paper/protocol/first-use-audit-ledger.md","docs/paper/round7/built-terms-lexicon.md","tests/test_paper_first_use_ledger.py","tests/fixtures/d165_rationale_allowlist.json","scripts/check_paper_replay_fence.py"],"unowned_dirty":["docs/process_traces/2026-09-12-paper-n/02-review-fact-astra-report.manifest.jsonl","docs/process_traces/2026-09-12-paper-n/10-kernel-stale-rows-astra-report.manifest.jsonl","docs/process_traces/2026-09-12-paper-n/17-delta-fact-astra-report.manifest.jsonl"],"verdict":{"implementation":"implemented","acceptance":"ready"},"verification":[{"id":"V1","kind":"lint","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B docs/paper/fill-rehearsal/select_outcome_branches.py --check-rendered docs/paper/draft-v2-skeleton.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["METHODS_DIAGNOSTIC validated; abstract_words=245, limit=250"]},"expected":{"exit_code":0,"tail_regex":"abstract_words=245, limit=250"}},{"id":"V2","kind":"lint","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B scripts/check_paper_replay_fence.py --literals-only","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["LITERALS 22 extracted from /Users/edr/code/JouleWise-wt-paper-n/docs/paper/draft-v2-skeleton.md","INTERNAL MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"INTERNAL MISMATCHES 0"}},{"id":"V3","kind":"lint","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B scripts/check_paper_round7_artifacts.py --literals-only","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["R7F PLACED 0/4","R7F LITERALS-ONLY COMPARED 412 / MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"R7F LITERALS-ONLY COMPARED 412 / MISMATCHES 0"}},{"id":"V4","kind":"lint","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B docs/paper/build/check_markdown.py docs/paper/draft-v2-skeleton.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Hard defects: 0","Exit: 0"]},"expected":{"exit_code":0,"tail_regex":"Exit: 0"}},{"id":"V5","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_first_use_ledger tests.test_paper_successor_migration tests.test_select_outcome_branches tests.test_d165_rationale_census tests.test_paper_comparison_placements tests.test_paper_build","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 62 tests in 23.207s","","OK (skipped=2)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=2\\)"}},{"id":"V6","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_terms_lint","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 16 tests in 2.376s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V7","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_replay_fence tests.test_check_paper_replay_fence","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 22 tests in 20.940s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V8","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B scripts/check_paper_replay_fence.py --repository-root . --corpus-root /Users/edr/code/JouleWise","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["MEMBER 20260722T145535-e941c821","COMPARED 43","MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"MISMATCHES 0"}},{"id":"V9","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_round7_artifacts","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 69 tests in 479.615s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V10","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B scripts/check_paper_round7_artifacts.py --repository-root . --corpus-root /Users/edr/code/JouleWise","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["R7F PLACED 0/4","R7F COMPARED 415 / MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"R7F COMPARED 415 / MISMATCHES 0"}},{"id":"V11","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_first_use_ledger tests.test_paper_terms_lint tests.test_paper_replay_fence tests.test_check_paper_replay_fence tests.test_paper_round7_artifacts tests.test_paper_successor_migration tests.test_select_outcome_branches tests.test_d165_rationale_census tests.test_paper_comparison_placements tests.test_paper_rendering tests.test_paper_build","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 175 tests in 528.662s","","OK (skipped=2)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=2\\)"}},{"id":"V12","kind":"inspection","cmd":"python3 -B /private/tmp/paper-n-round2-first-use.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["COUNTS {\"HEADING-GLOSS\": 1, \"OK\": 158, \"OUTSIDE\": 139, \"TABLE-GLOSS\": 3, \"VOCAB\": 13}"]},"expected":{"exit_code":0,"tail_regex":"COUNTS.*\"OK\": 158"}},{"id":"V13","kind":"other","cmd":"git add -- docs/paper/draft-v2-skeleton.md docs/paper/protocol/first-use-audit-ledger.md docs/paper/round7/built-terms-lexicon.md tests/test_paper_first_use_ledger.py tests/fixtures/d165_rationale_allowlist.json scripts/check_paper_replay_fence.py","cwd":".","observed":{"result":"fail","exit_code":128,"tail":["fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-paper-n/index.lock': Operation not permitted"]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[{"id":"F1","kind":"environment","level":"blocking","text":"The sandbox denied the linked-worktree index.lock write. Nothing was staged and no commit was created; no bypass was attempted.","needs":"Lead: stage only the six pathspec files and create the single requested Paper-N fix round 2 commit."},{"id":"F2","kind":"verification_gap","level":"nonblocking","text":"Two optional build tests skipped because markdown-it-py is absent. The prohibited paper build script was not run.","needs":"Lead bench rendering and final verification."}]}
```

## Change

All requested text fixes are implemented and verified. **The single commit remains uncreated because the sandbox denied Git’s `index.lock` write.** The six changed files remain unstaged; the three pre-existing dirty manifests were preserved.

The structural pass also cured surviving early uses: “project custody” became “by the project” in the §1 and §5 honesty sentences, leaving the custody definition at §7; the table’s new block-difference use received a plain calculation; and measurement windows, reservation plan, median, median absolute deviation, SHA-256, provenance, idle baseline, and disaggregated inference received needed first-use explanations.

| ID | Disposition | Implementation / pin |
|---|---|---|
| A1 | DONE-WITH-PIN-EDIT | Prescribed sentence below estimand table; duplicate §3 block deleted; A/B/B/A opener retained. Block-difference ledger home moved to §1. |
| A2 | DONE | Joint-interpolation allowance defined; zero-native-record explanation consistent. Half-width ledger disposition corrected. |
| B1 | DONE-WITH-PIN-EDIT | “Accepted region” throughout; §1 first-use gloss and §2 construction; merged synonymous ledger rows, count 263 → 262; updated gloss pin. |
| B2 | DONE | Explicit protocol referent. §1 remains unlinked because selector and terms lint require exactly one protocol link. |
| B3 | DONE-WITH-PIN-EDIT | Detection-threshold wording; surviving resolution-bound ledger home moved to protocol P.3. |
| B4 | DONE | §5 identifies the loss tolerance and noise floor with Appendix A.3.5. |
| B5 | DONE | Table A4 and Figure A4’s appendix pointer; no remaining Table 4 reference in draft. |
| B6 | DONE-WITH-PIN-EDIT | Loss-tolerance wording; accepted-region gloss pin updated. |
| B7 | DONE-WITH-PIN-EDIT | Introduction split; custody gloss removed; early named uses cured; custody ledger home → §7. |
| B8 | DONE | Actual axis label and fitted-edge-minus-command definition in caption. |
| N-1 | DONE | Huber gloss added. |
| N-2 | DONE | §4 retained apposition removed. |
| N-3 | DONE-WITH-PIN-EDIT | Custody definition retained only at §7; early uses removed and ledger re-homed. |
| N-4 | DONE | Figure 2 refers to Section 2’s accepted region without repeating its definition. |
| N-5 | DONE-WITH-PIN-EDIT | “Derived below as \(q_j\)”; required-gloss tuple updated. |
| N-6 | DONE | Blank line before subsection heading. |
| N-7 | DONE | `identifiable` receives the prescribed label explanation. |
| N-8 | DONE | Raw-capture sentence follows Third; custody wording also cured under the structural rule. |
| N-9 | DONE | “Operative timing bound.” |
| N-10 | DONE | Abstract uses “Section 3’s doubling test.” |
| D | DONE-WITH-PIN-EDIT | Definition moved beside method; sampler named once; sampler ledger homes → Abstract; **245 words**. |
| E | DONE-WITH-PIN-EDIT | Seven successor rows synchronized; four protected tuple entries updated; no lexicon rows added. |
| F | DONE-WITH-PIN-EDIT | Prescribed source-artifact fallback; extraction regex updated. No wording pin exists in `test_check_paper_replay_fence.py`, so that file required no edit. |
| G1 | DONE-WITH-PIN-EDIT | Final-gate definition; cell-floor gloss pin and ledger updated. |
| G2 | DONE | Requested table row preserved verbatim. |
| G3 | DONE | Explicit synthetic-origin parenthesis added. |
| H1 | DONE | Compound-calibration interpretation; representativeness and coverage sentences retained. |
| H2 | DONE-WITH-PIN-EDIT | Same synchronization as E. |
| H3 | DONE | Both A.3.10 occurrences now say “using `math.fsum`.” |
| Structural rule | DONE | Independent census: 262 ledger entries, 45 bold terms, seven additional moved-text terms; zero LATE/NEVER rows. |
| Requested commit | NOT DONE | Git staging denied by filesystem sandbox. |

Record 17’s fact correction governs H1 and the interpolation allowance. Record 16’s wording governs the associated pedagogy cures.

Successor-lexicon changes:

| Row | Old home → new home |
|---|---|
| powermetrics | §1 → Abstract |
| Former resolution-bound / detection-floor / cell-floor distinction | §1 → §3; row now names cell floor and retires the distinction |
| \(U_{\mathrm{point}}\), \(U_{\mathrm{corner}}\), point-only value, moved-edge limit, independent-edge ratio | §1 → §3 |
| Energy-allowance / shared / local signs | §1 → §3 |
| Declared machine state / manifest / reservation plan / calibration ledger / acceptance file | §2 → A.4; §2 still introduces and now glosses the reservation plan |
| mint | §2 → A.4 |
| Measured contrast / custody / former Figure 3 | §4 → protocol P.3 / §7; successor figure referent corrected to Figure P1 |

The generated draft-v1 lexicon base is byte-identical.

## Verification notes

All required paper tests passed, including the corpus-backed replay classes. The repository-wide discovery suite was not run: this is paper prose and checker tooling work, covered by the requested 175-test aggregate and direct replays. Two optional build tests skipped because `markdown-it-py` is absent; `build_paper.py` was never run.

Before/after census:

| Check | Before | After |
|---|---|---|
| Replay fence | `COMPARED 43` / `MISMATCHES 0` | `COMPARED 43` / `MISMATCHES 0` |
| Round-seven literals | `R7F PLACED 0/4`; `R7F LITERALS-ONLY COMPARED 412 / MISMATCHES 0` | Same |
| Round-seven full replay | `R7F PLACED 0/4`; `R7F COMPARED 415 / MISMATCHES 0` | Same |

Additional preservation checks:

```text
HTML_COMMENTS 15/15 BYTE_IDENTICAL
NEW_NUMERIC_LEXEMES 0
LEXICON_ROWS_UNCHANGED; GENERATED_BASE_BYTE_IDENTICAL
WORKED_PARAGRAPH_ONLY_F7_SENTENCE_CHANGED
REPLAY_LITERALS_IDENTICAL 22
FIRST_USE_LATE 0
FIRST_USE_NEVER 0
```

Both headline strings remain verbatim, exactly once. The complete worked paragraph differs only in F7’s authorized sentence. Its extracted subtraction remains:

```text
subtraction_minuend 0.030067931757111657
subtraction_subtrahend 0.0011349971959968978
subtraction_result 0.0289329345611147592
```

No comments belonged to the deleted §3 block or removed §1/§4 glosses. The abstract source comment remains with its paragraph. The §5 source comment belongs to the First/Second/Third discussion and remains there; the moved raw-capture sentence had no attached comment.

Remaining uses of terms affected by moves or deletions, in final main-text line numbers:

| Term | Definition | Every remaining use site |
|---|---:|---|
| Absolute floor | 108 | 104, 108; immediate table gloss prescribed by A1 |
| Comparative floor | 108 | 105, 108; same table gloss |
| Science contrast | 108 | 106, 108, 205; same table gloss precedes later prose |
| Floor source | 108 | 195 |
| Accepted region | 86 | 86, 144, 589, 590, 823 |
| Fitted onsets/offsets | 16 | 16, 22, 81, 144, 570, 583, 584, 902, 903 |
| Custody | 885 | 885 |
| Operative timing bound | 157 | 157, 298, 409 |
| Energy-allowance sign | 382 | 382, 387 |
| Retained | 28 | 28, 39, 157, 201, 353, 406, 410, 473, 491, 530, 536, 546, 550, 558, 565, 591, 605, 643, 648, 657, 665, 688, 690, 722, 745, 756, 766, 790, 791, 794, 820, 822, 885, 915, 918 |

The last row includes ordinary mathematical uses of “retained”; every site follows the abstract’s explanation.

The independent census below resolves manually identified definition anchors against the final text and mechanically searches inflected, possessive, hyphenated, and wrapped uses. It does not use the ledger test’s first-occurrence implementation. “Definition” is the beginning of the defining sentence or construction. **TABLE** denotes A1’s explicitly prescribed immediately following table gloss; **HEADING** denotes a heading explained in its first body paragraph; **VOCAB** denotes ordinary/audience vocabulary in the encountered sense. **OUTSIDE** means absent from the abstract and §1–§8, rather than used without definition.

[Replay script](/private/tmp/paper-n-round2-first-use.py), [definition anchors](/private/tmp/paper-n-round2-definition-anchors.json), and [complete machine output](/private/tmp/paper-n-round2-first-use-table.txt) are temporary inspection artifacts outside the worktree.

| Ledger term | First use | Definition | Result |
|---|---:|---:|---|
| commanded graphics-processor pulses | 82 | 82 | OK |
| pulse-derived limit | 88 | 85 | OK |
| interval-overlap allocation / interval-overlap-assigned phase energy | 52 | 51 | OK |
| held-average reconstruction | 56 | 56 | OK |
| timing envelope | 55 | 55 | OK |
| synthetic enclosure diagnostic | 186 | 186 | OK |
| component | 195 | 195 | OK |
| permitted edge movement | 195 | 195 | OK |
| independent-edge ratio / four-run comparison | 203 | 202 | OK |
| moved-edge limit / independent-edge corner bound / point-only value | 198 | 197 | OK |
| prompt processing / prefill | 12 | 12 | OK |
| token generation / decode | 13 | 13 | OK |
| phase boundary | 47 | 45 | OK |
| powermetrics | 12 | 12 | OK |
| sampler | 12 | 12 | OK |
| token | 13 | 13 | OK |
| Apple M3 Max / 128 GB unified memory | 64 | 64 | OK |
| sampling record | 41 | 41 | OK |
| integrated energy | 54 | 54 | OK |
| power-measurement boundary | 96 | 95 | OK |
| \(U_{\mathrm{point}}\) / \(U_{\mathrm{corner}}\) | 197 | 197 | OK |
| A/B/B/A block | 105 | 105 | OK |
| energy-allowance sign | 382 | 382 | OK |
| bracketed readings | 74 | 70 | OK |
| repeatability / repetition / random scatter | 127 | — | VOCAB |
| systematic reassignment | 127 | 52 | OK |
| science window / measurement window | 28 | 28 | OK |
| SHA-256 / SHA-256 fingerprint | 374 | 374 | OK |
| phase reduction | 113 | 112 | OK |
| measurement refusal | 115 | 114 | OK |
| declared machine state / instrument-validation manifest / reservation plan / calibration ledger / calibration-acceptance file | 142 | 142 | OK |
| frozen | 142 | 142 | OK |
| signal, fit, range, trace-coverage, and completeness checks / shared search-work limits | 144 | 144 | OK |
| first-record endpoint | 155 | 155 | OK |
| calibration-acceptance rule | 157 | 157 | OK |
| entry check | 164 | 164 | OK |
| reference runs | 166 | 164 | OK |
| warm-up pulses | 142 | 142 | OK |
| base-two varied-gap schedule | 142 | 142 | OK |
| sampler cadence | 142 | — | VOCAB |
| quiet trace | 142 | 142 | OK |
| resting GPU power / pulse height / plateau / pulse plateau | 144 | 144 | OK |
| trace-coverage | 144 | 144 | OK |
| accepted capture bound / capture bound | 144 | 85 | OK |
| clock-anchor bound | 87 | 87 | OK |
| complete / completeness | 144 | — | VOCAB |
| refused / refuses | 142 | — | VOCAB |
| wall clock / monotonic clock | 71 | 70 | OK |
| straight-line clock mappings / rate-aware model | 155 | 70 | OK |
| missing / malformed | 155 | — | VOCAB |
| unbounded | 155 | 155 | OK |
| Student-\(t\) | 157 | 157 | OK |
| 99% quantile / \(t_{0.995,16}\) | 157 | 157 | OK |
| degrees of freedom | 157 | — | VOCAB |
| sample standard deviation / prediction amount | 157 | 157 | OK |
| two-draw rule | 157 | 157 | OK |
| corpus range | 157 | — | VOCAB |
| ROUND_HALF_EVEN / nearest microsecond | 157 | 157 | OK |
| minimum allowance / operative timing bound / \(B_{\mathrm{fiducial}}\) / \(b\) | 157 | 157 | OK |
| stage / block member | 161 | 161 | OK |
| members | 168 | 167 | OK |
| A/B/B/A order / block difference | 108 | 108 | OK |
| whole-window allowance / energy family | 173 | 173 | OK |
| onset lag / offset lag / pulse residual | 536 | 536 | OK |
| record clipping / clip a record | 177 | 177 | OK |
| configuration cell / cell | 95 | 95 | OK |
| false-difference components / false-difference | 197 | 105 | OK |
| admitted | 162 | 162 | OK |
| independent unit | 242 | 241 | OK |
| absolute component / comparative component | 219 | 218 | OK |
| admitted energy | 238 | 237 | OK |
| independent units | 242 | 241 | OK |
| point-only unguarded value / unguarded | 236 | 234 | OK |
| independent-edge ratio \(R\) / dominates | 367 | 365 | OK |
| threshold / exact equality | 148 | — | VOCAB |
| authentication / evaluation | 867 | — | VOCAB |
| registered rounding / registered | 15 | 15 | OK |
| reintegrate | 406 | 406 | OK |
| onset set / offset set / zero-shift value | 412 | 406 | OK |
| shared lower and upper energy swings | 416 | 416 | OK |
| binary64 / member-envelope integral sum | 739 | — | VOCAB |
| local sign | 384 | 384 | OK |
| local half-width / shared sign | 384 | 384 | OK |
| half-width | 311 | 309 | OK |
| \(R_{cm}\), including plain `R_cm` | 380 | 380 | OK |
| shared-energy-sign/local-corner sensitivity diagnostic / shared-energy-sign/local-corner ratio | 390 | 380 | OK |
| two-block fixture / Student-\(t\) critical | 473 | 473 | OK |
| cell floor | 517 | 517 | OK |
| small-sample multiplier / \(g(n)\) | 240 | 234 | OK |
| not resolvable | 636 | 635 | OK |
| measurement interval | 865 | — | VOCAB |
| request total | 60 | 60 | OK |
| MLX | 65 | 65 | OK |
| inserted-gap check | 91 | 91 | OK |
| fail-closed | 529 | 527 | OK |
| idle baseline / nearest-rank p95 | 859 | 859 | OK |
| third-party provenance / provenance | 756 | 755 | OK |
| record support / positive overlap / overlap count | 119 | 119 | OK |
| interquartile range / IQR | 692 | 692 | OK |
| resolvability / not_resolvable_sample_count | 635 | 634 | OK |
| record width | 621 | 620 | OK |
| diagnostic-era | 557 | 557 | OK |
| three-record minimum | 25 | 24 | OK |
| fitted edge time / command time | 536 | 536 | OK |
| Running Average Power Limit / RAPL | 848 | 848 | OK |
| NVIDIA Management Library / NVML | 850 | 850 | OK |
| large-language model / LLM | 852 | 854 | HEADING |
| minimum-detectable-effect / pre-registration | 869 | 869 | OK |
| disaggregated inference / disaggregation | 871 | 871 | OK |
| re-derivation / fresh collection | 558 | 557 | OK |
| run bundle | 884 | — | VOCAB |
| Clock stamps / paired stamp | 527 | 70 | OK |
| Commanded pulses | 142 | 82 | OK |
| fiducial | 157 | 82 | OK |
| model/stack | 665 | 642 | OK |
| median absolute deviation / robust scale | 147 | 147 | OK |
| detected | 550 | — | VOCAB |
| custody | 885 | 885 | OK |
| GPU / fitted onsets and offsets | 16 | 16 | OK |
| best-fit lag | 536 | 536 | OK |
| accepted region | 86 | 86 | OK |
| medians | 146 | 146 | OK |
| source map | 499 | 499 | OK |

Every remaining ledger entry was also searched; these 139 entries have no use in the audited main text:

| Ledger term | First use | Definition | Result |
|---|---:|---:|---|
| decision rule | — | — | OUTSIDE |
| twofold boundary contribution | — | — | OUTSIDE |
| twelve required ratios | — | — | OUTSIDE |
| reasoning disabled | — | — | OUTSIDE |
| applied chat-template | — | — | OUTSIDE |
| greedy generation | — | — | OUTSIDE |
| mint | — | — | OUTSIDE |
| gross energy / idle-subtracted energy | — | — | OUTSIDE |
| curvature | — | — | OUTSIDE |
| reference-trajectory excursion / issued repeatability bound | — | — | OUTSIDE |
| leaking dependence across the phase boundary | — | — | OUTSIDE |
| floor packs / contrast pack | — | — | OUTSIDE |
| Workload response | — | — | OUTSIDE |
| Identical-condition null | — | — | OUTSIDE |
| workload-response slope | — | — | OUTSIDE |
| workload level | — | — | OUTSIDE |
| workload magnitude | — | — | OUTSIDE |
| per-token conversion | — | — | OUTSIDE |
| fitted residual | — | — | OUTSIDE |
| null-test blocks | — | — | OUTSIDE |
| interval of allowed differences | — | — | OUTSIDE |
| mean interval | — | — | OUTSIDE |
| resolution band | — | — | OUTSIDE |
| floor band | — | — | OUTSIDE |
| unphased gap | — | — | OUTSIDE |
| shared session timing term | — | — | OUTSIDE |
| member-local timing | — | — | OUTSIDE |
| timing flags | — | — | OUTSIDE |
| sampling flags / cadence ratio | — | — | OUTSIDE |
| package power | — | — | OUTSIDE |
| reference roles | — | — | OUTSIDE |
| passing cooldown exit | — | — | OUTSIDE |
| ulp | — | — | OUTSIDE |
| resolution bound | — | — | OUTSIDE |
| directional comparison / directional comparisons | — | — | OUTSIDE |
| Holm step-down correction / raw probability | — | — | OUTSIDE |
| repeat standard error | — | — | OUTSIDE |
| total standard error | — | — | OUTSIDE |
| null hypothesis / tail area | — | — | OUTSIDE |
| effective sample size / \(n_{\mathrm{eff}}\) | — | — | OUTSIDE |
| AR(1) model | — | — | OUTSIDE |
| serially correlated | — | — | OUTSIDE |
| decision-interval sign check / direction gate | — | — | OUTSIDE |
| magnitude check / direction check | — | — | OUTSIDE |
| statistical measurement interval | — | — | OUTSIDE |
| decision interval | — | — | OUTSIDE |
| deterministic bound | — | — | OUTSIDE |
| deterministic-bound kinds / interpolation edge | — | — | OUTSIDE |
| close-out artifact | — | — | OUTSIDE |
| signed clearance or shortfall | — | — | OUTSIDE |
| Figure P1 | — | — | OUTSIDE |
| measured admission rules / admit a stage | — | — | OUTSIDE |
| cooldown rule | — | — | OUTSIDE |
| window closes | — | — | OUTSIDE |
| measured contrast | — | — | OUTSIDE |
| first-order balance | — | — | OUTSIDE |
| quarantine / append-only | — | — | OUTSIDE |
| tamper-evident / tamper-proof / trusted operator | — | — | OUTSIDE |
| freeze receipt / freeze receipts | — | — | OUTSIDE |
| prospective demonstration | — | — | OUTSIDE |
| reducer | — | — | OUTSIDE |
| variance multiplier | — | — | OUTSIDE |
| within-arm variation | — | — | OUTSIDE |
| external-meter study | — | — | OUTSIDE |
| not presently open to independent re-reduction | — | — | OUTSIDE |
| release manifest | — | — | OUTSIDE |
| full-history checkout / third-party dependencies | — | — | OUTSIDE |
| admission predicates | — | — | OUTSIDE |
| strict validation | — | — | OUTSIDE |
| scientific binding | — | — | OUTSIDE |
| whole-window verdict / floor extraction / claim verdict | — | — | OUTSIDE |
| clock-anchor estimator / pulse-fit (accepted-region) algorithm | — | — | OUTSIDE |
| exact floating summation | — | — | OUTSIDE |
| ppm | — | — | OUTSIDE |
| The instrument and its records | — | — | OUTSIDE |
| property-list | — | — | OUTSIDE |
| interval aggregate | — | — | OUTSIDE |
| cumulative counter | — | — | OUTSIDE |
| combined power | — | — | OUTSIDE |
| record energy | — | — | OUTSIDE |
| Cumulative elapsed time | — | — | OUTSIDE |
| Trace intervals | — | — | OUTSIDE |
| rollover | — | — | OUTSIDE |
| van der Corput sequence | — | — | OUTSIDE |
| 59 measured pulses | — | — | OUTSIDE |
| end of record 0 | — | — | OUTSIDE |
| set membership | — | — | OUTSIDE |
| The clock model | — | — | OUTSIDE |
| affine | — | — | OUTSIDE |
| Model condition (stated because the containment claim depends on it) | — | — | OUTSIDE |
| Inputs and their admission checks | — | — | OUTSIDE |
| Wall-minus-monotonic span | — | — | OUTSIDE |
| Numeric-padding check | — | — | OUTSIDE |
| Stamp constraints | — | — | OUTSIDE |
| Native-label constraints | — | — | OUTSIDE |
| Causal constraints, and the two symbols k_pre and k_parse | — | — | OUTSIDE |
| k_pre equals e_0 minus one resolution unit r_pre | — | — | OUTSIDE |
| Eliminating α | — | — | OUTSIDE |
| Fourier–Motzkin elimination | — | — | OUTSIDE |
| The feasible set and the solver | — | — | OUTSIDE |
| Seidel-type | — | — | OUTSIDE |
| linear programme / infeasible | — | — | OUTSIDE |
| first-parse lag | — | — | OUTSIDE |
| Composing the bound | — | — | OUTSIDE |
| admissible | — | — | OUTSIDE |
| Anchoring | — | — | OUTSIDE |
| Reading the pulses | — | — | OUTSIDE |
| Trimming warm-ups | — | — | OUTSIDE |
| warm-up pulses do not participate in the baseline set and are never fitted | — | — | OUTSIDE |
| Authenticating the executed schedule | — | — | OUTSIDE |
| Baseline set and robust scale / baseline set | — | — | OUTSIDE |
| MAD | — | — | OUTSIDE |
| Spurious-plateau check on the baseline set / spurious plateau | — | — | OUTSIDE |
| nonconvergent | — | — | OUTSIDE |
| Per-pulse fit | — | — | OUTSIDE |
| Local set | — | — | OUTSIDE |
| Interior set | — | — | OUTSIDE |
| robust SNR | — | — | OUTSIDE |
| Edge coverage | — | — | OUTSIDE |
| The model and the objective | — | — | OUTSIDE |
| Huber loss | — | — | OUTSIDE |
| The search (constrained coordinate descent) | — | — | OUTSIDE |
| argmin | — | — | OUTSIDE |
| Significance | — | — | OUTSIDE |
| Shift limit | — | — | OUTSIDE |
| The set of acceptable edge pairs / loss limit | — | — | OUTSIDE |
| Cell lower bound | — | — | OUTSIDE |
| monotone | — | — | OUTSIDE |
| interval branch-and-bound / region’s enclosure | — | — | OUTSIDE |
| bisect | — | — | OUTSIDE |
| depth-first | — | — | OUTSIDE |
| Projection | — | — | OUTSIDE |
| Widening by stamp uncertainty | — | — | OUTSIDE |
| worst excursion | — | — | OUTSIDE |
| observed sample maximum | — | — | OUTSIDE |
| percentile | — | — | OUTSIDE |
| Origin of the 120 s work clock | — | — | OUTSIDE |
| matching refusal / reproduced result | — | — | OUTSIDE |
| typed custody-read interface / supply map | — | — | OUTSIDE |

Separate bold-term pass:

| Bold term | First use, including earlier plain uses | Definition | Result |
|---|---:|---:|---|
| phase boundary | 47 | 45 | OK |
| interval-overlap allocation | 52 | 51 | OK |
| timing envelope | 55 | 55 | OK |
| held-average reconstruction | 56 | 56 | OK |
| Commanded graphics-processor pulses | 82 | 82 | OK |
| clock-anchor bound | 87 | 87 | OK |
| pulse-derived limit | 88 | 85 | OK |
| inserted-gap check | 91 | 91 | OK |
| configuration cell | 95 | 95 | OK |
| cell | 95 | 95 | OK |
| Frozen | 142 | 142 | OK |
| first-record endpoint | 155 | 155 | OK |
| calibration-acceptance rule | 157 | 157 | OK |
| minimum allowance | 157 | 157 | OK |
| operative timing bound | 157 | 157 | OK |
| stage | 161 | 161 | OK |
| admitted | 162 | 162 | OK |
| entry check | 164 | 164 | OK |
| reference runs | 166 | 164 | OK |
| members | 168 | 167 | OK |
| synthetic enclosure diagnostic | 186 | 186 | OK |
| point-only value | 198 | 197 | OK |
| moved-edge limit | 201 | 197 | OK |
| independent-edge corner bound | 202 | 197 | OK |
| independent-edge ratio | 203 | 202 | OK |
| absolute component | 219 | 218 | OK |
| comparative component | 220 | 218 | OK |
| point-only unguarded value | 236 | 234 | OK |
| admitted energy | 238 | 237 | OK |
| small-sample multiplier | 240 | 234 | OK |
| independent units | 242 | 241 | OK |
| dominates | 367 | 365 | OK |
| authenticated | 373 | 373 | OK |
| energy-allowance sign | 382 | 382 | OK |
| shared-energy-sign/local-corner sensitivity diagnostic | 390 | 380 | OK |
| shared-energy-sign/local-corner ratio | 461 | 380 | OK |
| cell floor | 517 | 517 | OK |
| best-fit lag | 536 | 536 | OK |
| record width | 621 | 620 | OK |
| positive overlap | 623 | 622 | OK |
| overlap count | 627 | 627 | OK |
| record support | 119 | 119 | OK |
| resolvability | 635 | 634 | OK |
| not resolvable | 636 | 635 | OK |
| Custody | 885 | 885 | OK |

Additional moved-text terms:

| Term | First use | Definition | Result |
|---|---:|---:|---|
| absolute floor | 104 | 108 | TABLE |
| comparative floor | 105 | 108 | TABLE |
| science contrast | 106 | 108 | TABLE |
| floor source | 195 | 108 | OK |
| registered joint-interpolation allowance | 313 | 313 | OK |
| Huber | 150 | 150 | OK |
| retained | 28 | 28 | OK |

Requested whole-worktree `git diff --stat`:

```text
 docs/paper/draft-v2-skeleton.md                    | 101 +++++++++++----------
 docs/paper/protocol/first-use-audit-ledger.md      |  21 ++---
 docs/paper/round7/built-terms-lexicon.md           |  14 +--
 .../02-review-fact-astra-report.manifest.jsonl     |   1 +
 ...0-kernel-stale-rows-astra-report.manifest.jsonl |   1 +
 scripts/check_paper_replay_fence.py                |   2 +-
 tests/fixtures/d165_rationale_allowlist.json       |   2 +-
 tests/test_paper_first_use_ledger.py               |  14 +--
 8 files changed, 81 insertions(+), 75 deletions(-)
```

Session-owned changes only:

```text
 docs/paper/draft-v2-skeleton.md               | 101 ++++++++++++++------------
 docs/paper/protocol/first-use-audit-ledger.md |  21 +++---
 docs/paper/round7/built-terms-lexicon.md      |  14 ++--
 scripts/check_paper_replay_fence.py           |   2 +-
 tests/fixtures/d165_rationale_allowlist.json  |   2 +-
 tests/test_paper_first_use_ledger.py          |  14 ++--
 6 files changed, 79 insertions(+), 75 deletions(-)
```

## Residual risk

Rendered layout remains for the lead’s bench check. No hardware measurement or paper build was performed.

The exact remaining step, from this worktree in the lead’s writable Git environment, is:

```bash
git add -- \
  docs/paper/draft-v2-skeleton.md \
  docs/paper/protocol/first-use-audit-ledger.md \
  docs/paper/round7/built-terms-lexicon.md \
  tests/test_paper_first_use_ledger.py \
  tests/fixtures/d165_rationale_allowlist.json \
  scripts/check_paper_replay_fence.py

git commit -m "Paper-N fix round 2: repair first-use definitions and replay provenance"
```

The filesystem sandbox rejected staging at `/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-paper-n/index.lock`. HEAD therefore remains `73f7ac9f73c169aed0b1bf02d7f256c8db8c329e`.