```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"No blocker found; numerical literals and mechanical pins survive, with two should-fix issues and one numerical-wording nit.","workspace":{"base_requested":"dbe6c675","base_mode":"descendant","head_start":"482a0cc49995aba94f923956af60c547fde538c6","head_end":"482a0cc49995aba94f923956af60c547fde538c6","upstream_end":"c53d4227f2c175fc16220e4114d79de4555bc032","branch":null},"pathspec":[],"unowned_dirty":["docs/process_traces/2026-09-12-paper-n/13-fix-round-1-astra-report.manifest.jsonl","docs/process_traces/2026-09-12-paper-n/13-fix-round-1-astra-report.md"],"verdict":{"findings":[{"id":"DELTA-1","severity":"should_fix","summary":"The new pre/post interpretation attributes a compound bound change specifically to fitted sampler response.","path":"docs/paper/draft-v2-skeleton.md","line":150},{"id":"DELTA-2","severity":"should_fix","summary":"Moved definitions leave the protected successor lexicon naming obsolete first-use homes.","path":"docs/paper/draft-v2-skeleton.md","line":1439},{"id":"DELTA-3","severity":"nit","summary":"The new padding recipe calls rounded math.fsum operations exact floating summation.","path":"docs/paper/draft-v2-skeleton.md","line":1400}]},"verification":[{"id":"V1","kind":"lint","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B docs/paper/fill-rehearsal/select_outcome_branches.py --check-rendered docs/paper/draft-v2-skeleton.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["METHODS_DIAGNOSTIC validated; abstract_words=238, limit=250"]},"expected":{"exit_code":0,"tail_regex":"METHODS_DIAGNOSTIC validated; abstract_words=238, limit=250"}},{"id":"V2","kind":"lint","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B scripts/check_paper_replay_fence.py --literals-only","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["LITERALS 22 extracted from /Users/edr/code/JouleWise-wt-paper-n-ref/docs/paper/draft-v2-skeleton.md","INTERNAL MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"INTERNAL MISMATCHES 0"}},{"id":"V3","kind":"lint","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B scripts/check_paper_round7_artifacts.py --literals-only","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["R7F PLACED 0/4","R7F LITERALS-ONLY COMPARED 412 / MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"R7F LITERALS-ONLY COMPARED 412 / MISMATCHES 0"}},{"id":"V4","kind":"lint","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B docs/paper/build/check_markdown.py docs/paper/draft-v2-skeleton.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Hard defects: 0","Exit: 0"]},"expected":{"exit_code":0,"tail_regex":"Exit: 0"}},{"id":"V5","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_first_use_ledger tests.test_paper_successor_migration tests.test_select_outcome_branches tests.test_d165_rationale_census tests.test_paper_comparison_placements tests.test_paper_build","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 62 tests in 23.357s","","OK (skipped=2)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=2\\)"}},{"id":"V6","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_terms_lint","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 16 tests in 2.414s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V7","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_replay_fence tests.test_check_paper_replay_fence","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 22 tests in 21.104s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V8","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B scripts/check_paper_replay_fence.py --repository-root . --corpus-root /Users/edr/code/JouleWise","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["MEMBER 20260722T145535-e941c821","COMPARED 43","MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"MISMATCHES 0"}},{"id":"V9","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_round7_artifacts","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 69 tests in 480.801s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V10","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B scripts/check_paper_round7_artifacts.py --repository-root . --corpus-root /Users/edr/code/JouleWise","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["R7F PLACED 0/4","R7F COMPARED 415 / MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"R7F COMPARED 415 / MISMATCHES 0"}},{"id":"V11","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_first_use_ledger tests.test_paper_terms_lint tests.test_paper_replay_fence tests.test_check_paper_replay_fence tests.test_paper_round7_artifacts tests.test_paper_successor_migration tests.test_select_outcome_branches tests.test_d165_rationale_census tests.test_paper_comparison_placements tests.test_paper_rendering tests.test_paper_build","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 175 tests in 529.566s","","OK (skipped=2)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=2\\)"}}],"flags":[{"id":"R1","kind":"verification_gap","level":"nonblocking","text":"Two optional build tests skip because markdown-it-py is absent; the prohibited build script was not run.","needs":"Lead bench rendering and visual verification."},{"id":"R2","kind":"baseline_drift","level":"nonblocking","text":"origin/main is c53d4227; this audit remains anchored to the explicitly requested dbe6c675.","needs":""}]}
```

## Findings

**No blocker found.** No quantitative literal was changed, no novel quantitative value entered the main text, and every executed paper check passed.

Confirmed head:

```text
482a0cc4 Paper-N fix round 1: clarify scope and timing-domain limitations (advisor-readiness pass; abstract 238 words; literals byte-identical; pins updated per census)
```

The requested base-to-head diff contains 22 files, 3029 insertions and 279 deletions, including the review/process records. This session modified no files.

### DELTA-1 — Should fix: the new pre/post interpretation excludes a contributing uncertainty term

New draft line 150:

> “A pre/post difference above the threshold would indicate a change in the sampler's fitted edge response across the window.”

Appendix A.3.6, line 1216, defines:

```text
B_fiducial = max over the 118 edge excursions  +  B_anchor
```

The difference can therefore increase through the clock-anchor allowance even when the fitted edge excursions are unchanged. The new sentence attributes more specifically than this compound statistic supports.

**Minimal cure:**

> “A pre/post difference above the threshold indicates a change in the compound calibration allowance; it does not distinguish a change in fitted edge response from a change in clock-placement uncertainty.”

Keep the following representativeness and empirical-coverage qualifications.

### DELTA-2 — Should fix: relocated definitions leave protected lexicon homes stale

New draft lines 194–196:

> “This **moved-edge limit** is called the **independent-edge corner bound**. Their quotient, \(U_{\mathrm{corner}}/U_{\mathrm{point}}\), is the **independent-edge ratio**…”

New appendix line 1439:

> “Under the current mint—the analysis run that issues the paper's fixed results…”

But `docs/paper/round7/built-terms-lexicon.md` still places the point/corner definitions in **§1** at line 19 and `mint` in **§2** at line 24. They now occur in **§3** and **A.4**, respectively. Its machine-state/manifest row also retains §2, and its floor terminology still describes the removed distinction.

The lexicon-protection test passes because it protects the unchanged stale rows; it does not establish their agreement with the relocated prose. The seat correctly reported this as NOT DONE.

**Minimal cure:** update the affected successor rows and their protected tuple under census L7. Preserve unrelated historical/generated rows.

### DELTA-3 — Nit: “exact floating summation” overstates the operation

New lines 1400 and 1409:

> “In production, form \(d_j^-\) and \(d_j^+\) with exact floating summation…”

> “…with the final addition also evaluated by exact floating summation.”

`joulewise/dominance_closeout.py:597–614` uses `math.fsum`, returning a rounded binary64 result. For example, summing the exactly representable inputs `1.0` and `2**-53` returns `1.0`; the exact mathematical sum differs by `2**-53`.

The padding formula and outward steps otherwise match the implementation.

**Minimal cure:** replace both occurrences with “using `math.fsum`.”

### F1–F10 closure

Locations refer to the new draft. “REGRESSED” follows the brief’s rule that an otherwise successful cure introducing an inaccuracy receives that verdict.

| Original finding | Cured or surviving passage | Verdict | Reason |
|---|---|---|---|
| F1 | 296–311: “in \([-a,a]\)… \([-(b+w),b+w]\)” and “the floor inputs are \(E^L=E-h\) and \(E^U=E+h\)” | **CURED** | Matches `reduce.py:2148–2268` and `floor_extraction.py:2100–2117`: independent endpoint corners, common-shift breakpoints, coverage refusal, and symmetrized energy inputs. Native-support interpolation is zero at `reduce.py:554–555`. |
| F2 | 394–398: “require strict noncollapse: `nextafter(start+b, +∞) < nextafter(end−b, −∞)`”; 431–435 name `effective_clock_anchor_bound_s` and `wall_minus_monotonic_span_s` | **CURED** | Matches `floor_extraction.py:376–389,2416–2494`; shared calibration is zero for the local residual calculation. |
| F3 | 1192: “In exact arithmetic, no point of C can have loss below LB(C)”; 1200: “no independently established directed-rounding containment guarantee” | **CURED** | Analytic containment is distinguished from floating-point execution; historical values remain intact. |
| F4 | 120: “For adjacent phases sharing the moved boundary…” and “the historical phase windows have separately stamped endpoints and may leave a gap” | **CURED** | The conservation statement now names its required geometry. |
| F5 | 81: “in the fit’s model-defined accepted regions”; 564: “rectangular model’s switch-on and switch-off times”; 1153: “fixed central portion”; 1148: “possible uncommanded GPU activity”; 814–815: “gain was not independently checked”; 658–659 and 910: “outcomes differed”; 711–712: “depends on alignment as well as record width” | **CURED** | All seven named sites received the requested qualification. DELTA-1 repeats the over-attribution class elsewhere. |
| F6 | 150: “registered independent, equal-variance normal-model design convention”; 148: “Prospective claim use separately refuses…”; 1245–1252 supply selection and exclusions | **REGRESSED** | The original selection, assumptions and admission gaps are closed, but the added physical interpretation introduces DELTA-1. |
| F7 | 544: “Therefore the largest pulse residual before the anchor term is…” | **NOT CURED** | The entire worked paragraph remains byte-identical. It still misnames the printed subtraction, contrary to A.3.6:1220. The seat explicitly deferred it under the worked-line/R6 pin. |
| F8 | 1406–1409 define padded \(q_j\); 1410–1413 distinguish implementation roles and unpadded illustration | **REGRESSED — wording only** | Padding, subsequent outward steps and source roles are correct; “exact floating summation” introduces DELTA-3. No numerical regression found. |
| F9 | 843: “JouleWise applies timing analysis…” and “Whole-request agreement…alone does not determine…”; 858: “calculates timing sensitivity of assigned phase energies” | **CURED** | All three claims are narrowed as prescribed. |
| F10 | 139: “resting power \(P_{\mathrm{rest}}\)”; 150: “retained SD operand” | **CURED** | Resting power and the operative timing bound are distinguished, including appendix formulas; the SD precision label is corrected. |

F7’s minimal eventual cure remains the original report’s distinction between **subtracting printed bounds** and the **separately retained largest residual**, with every existing literal preserved. It is a surviving baseline issue, not a new delta finding.

### New-sentence evidence audit

There are **new occurrences of existing numerals**, as the contract permits, but **no novel quantitative value** in the main text. The new `A.3.10` locator is a subsection identifier. Rounded readings are checked below.

| Contract item | New passage, quoted | Evidence/support and digit assessment |
|---|---|---|
| A1/A2 | 16, 37: “This paper specifies the sensitivity calculation and demonstrates it on synthetic inputs; it reports no sensitivity ratio on measured inference data.” | Supported by the synthetic calculations in §3 and historical-only results in §4. No digits in the sentence. |
| A2 | 37, 777: “The raw captures behind the historical numbers are retained under project custody and are not released; the synthetic examples are the only fully reproducible part.” | Consistent with §7’s existing release/custody limitation and synthetic replay. No digits. |
| C6 | 137: “a rectangle is rejected only when a mathematical lower bound proves in exact arithmetic that none of it can pass” | Supported by A.3.5’s analytic lower-bound construction. No new numerical value. |
| C6 | 1200: “The implemented floating-point search has no independently established directed-rounding containment guarantee.” | Accurately discloses original F3’s implementation limitation. No digits. |
| C7 | 150: “the two-draw rule is the registered independent, equal-variance normal-model design convention” | Supplies the missing assumptions without claiming empirical coverage. Existing operands retained. |
| C7 | 150: “Interpreting this threshold as an instrument screen is conditional on the retained corpus being representative, which has not been tested; empirical 99% coverage has not been established.” | Consistent with the selected corpus and absence of validation. `99%` already appears on the same old line 208. |
| C7 | 150: “A pre/post difference above the threshold would indicate a change in the sampler's fitted edge response across the window.” | **Not sufficiently supported:** DELTA-1. No digits. |
| C7 | 148: “Prospective claim use separately refuses active or unknown automatic network-time correction; historical evidence with correction ON or unknown is restricted to diagnostic use.” | Matches the distinction in `uncertainty_evidence.py:840–844`. No digits. |
| C7 | 1245–1251: “The selection is valid protocol-v3 captures before the excluded Window-B judged pair, from the exact identity epoch specified by that file, re-derived from primary bytes under the current rate-aware anchor. Two predecessor members were excluded because no single affine wall-versus-monotonic rate reconciles their stamp rectangles with their native whole-second labels inside the fixed model-departure allowance; these are not an unrestricted sample of captures.” | Matches S17’s `derivation_corpus.selection` and both `excluded_predecessor_members`. Appendix addition; no new main-text number. |
| D1 | 295–302: “Shift the whole trace by a common displacement in \([-a,a]\), and move the start and end independently in \([-(b+w),b+w]\)… evaluate the common trace displacement at its domain endpoints, zero, and every in-domain record-edge/window-edge coincidence… Refuse if the trace does not cover every required shifted window or a moved window ends before it starts.” | Matches the named reducer construction and refusal. No novel numeral. |
| D1 | 305–313: “The floor consumes a symmetric interval, not those potentially asymmetric raw extrema” and “For native interval-average records the joint-interpolation term is zero” | Matches extraction and interpolation code cited in F1 closure. No novel numeral. |
| D1 | 396–397: “require strict noncollapse… in exact arithmetic its duration must exceed \(2b\)” | Matches the strict code predicate. `2` was already present throughout §3. |
| D2 | 374: “R asks how much the bound grows when every run’s edges move independently; R_cm asks how much it grows when one direction of energy allowance is applied to every block at once and each block’s own edges then move to their worst local corner.” | Consistent with the following shared-sign/local-width construction and its explicit denial of a shared physical-time replay. No digits. |
| D2 | 425–426: “The main-text illustration uses this unpadded formula; Appendix A.3.10 defines the padded production value of \(q_j\) used in the same sign enumeration.” | Supported by the retained fixture and `dominance_closeout.py:562–617`. New subsection locator only. The appendix’s “exact” wording needs DELTA-3. |
| E1 | 120: “For adjacent phases sharing the moved boundary, the request total does not change… the historical phase windows have separately stamped endpoints and may leave a gap.” | Correct for adjacent windows; consistent with the retained geometry and protocol gap distinction. No new quantity. |
| E4 | 1190: “On the retained capture, σ sat at its 1-mW floor while plateau scatter was of order a watt around the fitted pulse height, vastly larger than σ.” | **Supported.** A.3.5:1146 states zero baseline MAD and σ=`0.001 W`; Table A3:1304 repeats σ, while its plateau rows differ from fitted height by roughly watt-scale amounts. |
| E4 | 1190, repeated at 817–819: “The accepted region is therefore a tolerance set whose width depends on the 5% and 1-mW constants, which were not varied.” | Consistent with `Λ = Loss* + max(1.0, 0.05·Loss*)` and the scale floor. `5%` restates the existing `0.05`; `1 mW` already appeared in A.3.5. No novel quantity. |
| E5 | 821–826: “The 59 of 59 onsets late and 49 of 59 offsets early form a one-directional pattern. GPU start latency after the command and sampler window stamping are two candidate explanations; neither was tested. With no tested explanation to support a correction, no correction is applied. The symmetric \(\pm b\) domain therefore includes the bias and is wider on the side the bias does not occupy.” | Counts match §4 and DX-012/013. **Both explanations explicitly remain untested.** The symmetric-domain consequence describes the retained directional pattern, not a validated inference correction. Existing count literals reused. |
| E6 | 651–656: “A per-edge allowance of a few tens of milliseconds, as in the Section 2 example, amounts across both edges to more than half of the 1.5B median and roughly a quarter of the 7B median. The three-record minimum guards only against a split supported by two straddling averages, not against a timing envelope comparable to the phase energy.” | Supported: using the §2 example, `2×38.724/136.5 ≈ 0.5674` and `2×38.724/281.5 ≈ 0.2751`. No new numeric fraction is printed in the draft; model labels already exist. |
| F2 | 852: “cross-checks sufficiently long sampled-power integrals against the GPU's own hardware energy counter on the same telemetry interface [13]” | Supported by existing citation [13] and record 08, claim K. Removes the unsupported independence claim. Citation identifier unchanged. |
| F2 | 854: “Its disclosed method in the published paper does not specify the boundary events, alignment rule, repetition and variance protocol, idle baseline, or external validation needed to reconstruct a phase-attribution error budget.” | Properly limits the absence claim to the source examined in record 08, claims C–G. No new quantitative digit. |
| F3 | 843: “JouleWise applies timing analysis to phase-resolved `powermetrics` inference on Apple Silicon.” | Supported as a description of the specified method; no measured-inference ratio implied. No digits. |
| F3 | 843: “Whole-request agreement with an external wall meter alone does not determine the software trace’s phase split.” | Supported by the distinction between total energy and allocation already developed in §§1–3. No digits. |
| F3 | 858: “JouleWise calculates timing sensitivity of assigned phase energies.” | Consistent with the synthetic demonstrations and stated scope. No digits. |

### Literal preservation table

Old lines are at `dbe6c675`; new lines are at `482a0cc4`. Repeated literals sharing a passage are grouped. This covers edited lines and explicitly relocated passages; identifiers, citation numbers and unchanged paragraphs merely shifted by earlier edits are not treated as new quantitative claims.

| Literal(s) | Old line(s) | New line(s) | Result |
|---|---:|---:|---|
| `59`, `49` | 25–26 | 21–22 | SAME |
| `37`, `50` | 28 | 24 | SAME |
| `13` | 29 | 26 | SAME |
| `50`, `33`, `17` | 30–31 | 27 | SAME |
| `Qwen2.5-1.5B-Instruct-4bit`, `Qwen2.5-7B-Instruct-4bit` | 28, 30 | 24, 26 | SAME |
| `0.9`, `100` | 65 | 179 | SAME |
| `10`, `9`, `±10` | 66 | 180 | SAME |
| `8.8`, `9.2` | 67 | 181 | SAME |
| `8`, `10`, `8` | 69 | 183 | SAME |
| `0`, `1` | 70 | 184 | SAME |
| `0.010`, `30`, `0.30` | 176 | 120 | SAME |
| `0.010` — additional Figure 1 explanation | 176, 185 | 122, 129 | SAME, reused |
| `24`, `59`, `4096×4096`, `16`, `100`, `4.5` | 191 | 135 | SAME |
| `59` in detector description | 204 | 137 | SAME |
| `1.4826`, `0.001` | 194 | 140 | SAME |
| `5`, `5`, `0`, `0.001` | 195 | 141 | SAME |
| `6`, `7`, `5` | 196 | 142 | SAME |
| `10`, `10`; loss examples `4`, `10`, `5`, `10` | 197–198 | 143 | SAME |
| `0.5`, `0.499`, `0.500`, `0.75` | 199–200 | 144–145 | SAME |
| `17`, `99`, `0.995`, `16`, `0.5`, `2` | 208 | 150 | SAME |
| `2.460856`, `2.460856207694636` | 208 | 150 | SAME |
| `2.92078162242509999197` | 208 | 150 | SAME |
| `10.164834757777545`, `10.164835` | 208 | 150 | SAME |
| `9.723589288793850`, `9.724` | 208 | 150 | SAME |
| `25`, `29`, `4`, `38.724` | 208 | 150 | SAME |
| `2^n`; index numerals `1`, `2`, `3`, `4`, denominator `2` | 335, 458 | 314, 439 | SAME |
| `64`, `64`, `1.0` | 425 | 1363 | SAME |
| `(-1/2,+1/2,+1/2,-1/2)` | 429 | 1367 | SAME |
| `1`; `64`, `1.0`, `2`; `64`, `64`; `1`; `1/2` | 434–440 | 1372–1378 | SAME |
| `103.06152807459057` | 441–442, 445 | 1379–1380, 1383 | SAME |
| `64`, `2^{-53}`, `7.322962010973595`, `10^{-13}` | 445 | 1383 | SAME |
| `1`, `51.7925236532` | 506 | 1389 | SAME |
| `51.4297001503`, `51.6016978076`, `51.2991345381` | 507 | 1390 | SAME |
| `103.06152807459057`, `2`, `51.4136529737` | 508 | 1391 | SAME |
| `51.3521324018`, `51.3994292387`, `51.7540189975` | 509 | 1392 | SAME |
| `102.95961680584864` | 510–511 | 1393–1394 | SAME |
| `1970` | 574 | 530 | SAME |
| `0.0000010000000000000002` | 578–582 | 534–538; additional reading at 530 | SAME |
| `59`, `122,859`, `0.0011349971959968978`, `0.030067931757111657`, `0.0289329345611147592` | 588 | 544 | SAME |
| `26.625`, `27.625`, `1784757381.2856488`, `1784757382.293089`, `1970` | 588 | 544 | SAME |
| `0.02544938965763524`, `0.02893293456111476`, `-0.008607394549133255`, `-0.005308621075866744`, `+0.027`, `-0.007` | 588 | 544 | SAME |
| `59` in fitted-edge explanation | 608 | 564 | SAME |
| `9`, `+27` | 626 | 582 | SAME |
| `1.5B`, `7B` in new median comparison | 693 | 649, 653 | SAME, reused |
| `37` in replacement overlap explanation | 683–684 | 712 | SAME, reused |
| `0.030067931757111657` | 825 | 788 | SAME |
| `59`, `49` in new directional-pattern paragraph | 641 | 821 | SAME, reused |
| `95%`, `±1.5%` | 884 | 858 | SAME |
| `37`, `50`, `1.5B`, `7B` in deleted conclusion repetition | 937–938 | retained at 907–909 | SAME values; duplicate occurrence deleted under E8 |
| `1.4826`, `0.001` | 1172 | 1144 | SAME |
| `1.4826`, `1`, `0`, `0.0`, `0.001` | 1174 | 1146 | SAME |
| `5.0`, `5`, `2` | 1176 | 1148 | SAME |
| `0.25` in all inset occurrences | 1181 | 1153 | SAME |
| `10`, `0`, `40.6667`, `40 666.7`, `1784757336.5528765`, `0.27` | 1182 | 1154 | SAME |
| `0` in overlap formula; `0.5` in significance rule | 1188, 1211 | 1160, 1183 | SAME |
| `−0.75`, `0.75`, exponent `²` | 1218 | 1190 | SAME |
| `1` mW; `0.05` expressed as `5%` | 1174, 1216 | 817–819, 1190 | Existing quantities reused; percentage conversion correct |
| `0` in cell lower bound | 1220 | 1192 | SAME |
| `−0.75`, `0.75`, `²`, `10⁻⁴`, `1.5`, `14`, `1.5/2¹⁴`, `9.16·10⁻⁵`, `28` | 1221 | 1193 | SAME |
| `120` | 1263 | 1237 | SAME |
| `1784757336.5526073`, `0` | 1322 | 1303 | SAME |
| `0.001`, `42.5514` | 1323 | 1304 | SAME |

All eight moved Table 4 rows retain every sign and numeric literal:

| Literals, in original column order | Old line | New line | Result |
|---|---:|---:|---|
| `-1; -1; -1; -0.0957229360; -0.3437328112; -0.2197278736; 0.1753694646; 2.9487587953` | 535 | 1423 | SAME |
| `-1; -1; 1; -0.0957229360; -0.0723775195; -0.0840502277; 0.0165077023; 0.3409366257` | 536 | 1424 | SAME |
| `-1; 1; -1; 0.0014355703; -0.3437328112; -0.1711486204; 0.2440709032; 3.9692844226` | 537 | 1425 | SAME |
| `-1; 1; 1; 0.0014355703; -0.0723775195; -0.0354709746; 0.0521937363; 0.8476894571` | 538 | 1426 | SAME |
| `1; -1; -1; 0.4278157324; 0.8868870158; 0.6573513741; 0.3246124176; 5.7088426776` | 539 | 1427 | SAME |
| `1; -1; 1; 0.4278157324; 1.1582423076; 0.7930290200; 0.5164895845; 8.8304376431` | 540 | 1428 | SAME |
| `1; 1; -1; 0.5249742387; 0.8868870158; 0.7059306273; 0.2559109789; 4.6883170503` | 541 | 1429 | SAME |
| `1; 1; 1; 0.5249742387; 1.1582423076; 0.8416082731; 0.4477881458; 7.8099120158` | 542 | 1430 | SAME |
| `(+1,−1,+1); 0.4278157324; 1.1582423076; 8.8304376431; 8.8304376433` | 544–546 | 1432–1434 | SAME |

Additional whole-byte assertions passed for old/new:

- Worked paragraph: **588 → 544**.
- Stamp table and caption: **576–584 → 532–540**.
- Sign table and following arithmetic: **533–548 → 1421–1436**.

The four rounded readings retain their original operands and are arithmetically correct:

| Retained literal | Reading |
|---|---|
| `2.92078162242509999197` | about `3` |
| `10.164834757777545 ms` | about `10 ms` |
| `0.030067931757111657 s` | about `30 ms` |
| `0.0000010000000000000002 s` | about `1 µs` |

### Moves, comments and retired locators

**B1, B3, C1 and D2 had no attached HTML comments in their original moved spans.** Thus none was detached or lost during those moves. C1’s removed integrity sentences, from “Each capture carries…” through the calibration-acceptance sentence, survive as an exact byte substring at new line 1439.

The entire draft retains **15/15 HTML comment occurrences byte-identically**, with zero additions or losses:

```text
1 -> 1
36,943 -> 32,915
585 -> 541
586 -> 542
589 -> 545
590 -> 546
591 -> 547
816 -> 779
825 -> 788
841 -> 804
852 -> 815
856 -> 830
969 -> 941
1415 -> 1475
```

The final mapping preserves the exact `[FILL:PE-01]` comment. Source comments remain beside their corresponding passages.

I extracted all 228 retired sites through the census checker’s `_retired_sites` function and supplied their token/wildcard patterns to `grep -E -c -f /dev/stdin`:

```text
RETIRED SITES 228
grep -E -c -f /dev/stdin docs/paper/draft-v2-skeleton.md
0
grep exit 1
```

Exit 1 is grep’s expected **no matches** result. Both literal-only and full round-7 checks independently pass the retirement census.

### Verification tails and seat comparison

V1–V11 cover census §3’s fast checks, every named unit-test subset, both direct corpus replays, and the aggregate. The mandated `python3 -B` replaces the census’s `$PY`; bytecode suppression also propagates to subprocesses. No corpus-skipping alternative was used.

**Correction to the V9 command field above:** its executed command was:

```bash
PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_round7_artifacts
```

Exact tails:

```text
V1
METHODS_DIAGNOSTIC validated; abstract_words=238, limit=250

V2
LITERALS 22 extracted from /Users/edr/code/JouleWise-wt-paper-n-ref/docs/paper/draft-v2-skeleton.md
INTERNAL MISMATCHES 0

V3
R7F PLACED 0/4
R7F LITERALS-ONLY COMPARED 412 / MISMATCHES 0

V4
Hard defects: 0
Exit: 0

V5
Ran 62 tests in 23.357s

OK (skipped=2)

V6
Ran 16 tests in 2.414s

OK

V7
Ran 22 tests in 21.104s

OK

V8
MEMBER 20260722T145535-e941c821
COMPARED 43
MISMATCHES 0

V9
Ran 69 tests in 480.801s

OK

V10
R7F PLACED 0/4
R7F COMPARED 415 / MISMATCHES 0

V11
Ran 175 tests in 529.566s

OK (skipped=2)
```

| Census | Seat before/after or reported result | Re-audit |
|---|---|---|
| Replay fence | Before **43 / 0**; after **43 / 0** | **43 / 0**, same member |
| Round-7 literals | **412 / 0**, placed **0/4** | **412 / 0**, placed **0/4** |
| Round-7 full replay | **415 / 0** | **415 / 0** |
| Aggregate | **175 tests**, two skips | **175 tests**, same two skips |
| Abstract | **238 words** | **238 words** |

**Same-signature statement: YES.** DELTA-1 repeats original 02/F5’s class of attributing a physical mechanism more specifically than the statistic supports. DELTA-3 repeats 02/F3’s numerical-guarantee class at another site, at wording-nit severity. The original F7 also survives at its original site; it is not a new-site recurrence.

Next exact step: lead adjudication of DELTA-1–3, synchronization of the deferred lexicon, and a ruling on the still-pinned F7 wording before bench rendering.

## Residual risk

Two optional build tests skipped because `markdown-it-py` is absent. The prohibited paper build script was never run; rendered layout remains for lead verification.

These checks establish retained-byte replay and draft consistency. They do not establish hardware transfer to inference, energy-counter gain accuracy, or empirical coverage.