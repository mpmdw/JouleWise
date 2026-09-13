```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"No blocker found; current-draft facts and replay census survive, but frozen-v1 extraction regresses and one lexicon home remains wrong.","workspace":{"base_requested":"482a0cc4","base_mode":"descendant","head_start":"e3285e67d6b616b020b95eaf1caf2e8089f240ff","head_end":"e3285e67d6b616b020b95eaf1caf2e8089f240ff","upstream_end":"c53d4227f2c175fc16220e4114d79de4555bc032","branch":null},"pathspec":[],"unowned_dirty":["docs/process_traces/2026-09-12-paper-n/13-fix-round-1-astra-report.manifest.jsonl","docs/process_traces/2026-09-12-paper-n/19-fix-round-2-astra-report.manifest.jsonl"],"verdict":{"findings":[{"id":"R2-1","severity":"should_fix","path":"scripts/check_paper_replay_fence.py","line":174,"summary":"The new subtraction anchor breaks extraction of the supported frozen v1 draft."},{"id":"R2-2","severity":"should_fix","path":"docs/paper/round7/built-terms-lexicon.md","line":23,"summary":"The synchronized grouped row puts reservation plan in A.4 although its first gloss is now in Section 2."}],"same_signature":true},"verification":[{"id":"V1","kind":"lint","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B docs/paper/fill-rehearsal/select_outcome_branches.py --check-rendered docs/paper/draft-v2-skeleton.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["METHODS_DIAGNOSTIC validated; abstract_words=245, limit=250"]},"expected":{"exit_code":0,"tail_regex":"abstract_words=245, limit=250"}},{"id":"V2","kind":"lint","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B scripts/check_paper_replay_fence.py --literals-only","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["LITERALS 22 extracted from /Users/edr/code/JouleWise-wt-paper-n-ref/docs/paper/draft-v2-skeleton.md","INTERNAL MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"INTERNAL MISMATCHES 0"}},{"id":"V3","kind":"lint","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B scripts/check_paper_round7_artifacts.py --literals-only","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["R7F PLACED 0/4","R7F LITERALS-ONLY COMPARED 412 / MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"COMPARED 412 / MISMATCHES 0"}},{"id":"V4","kind":"lint","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B docs/paper/build/check_markdown.py docs/paper/draft-v2-skeleton.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Hard defects: 0","Exit: 0"]},"expected":{"exit_code":0,"tail_regex":"Exit: 0"}},{"id":"V5","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v tests.test_paper_first_use_ledger tests.test_paper_successor_migration tests.test_select_outcome_branches tests.test_d165_rationale_census tests.test_paper_comparison_placements tests.test_paper_build","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 62 tests in 24.167s","","OK (skipped=2)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V6","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_terms_lint","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 16 tests in 2.508s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V7","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_replay_fence tests.test_check_paper_replay_fence","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 22 tests in 21.543s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V8","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B scripts/check_paper_replay_fence.py --repository-root . --corpus-root /Users/edr/code/JouleWise","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["MEMBER 20260722T145535-e941c821","COMPARED 43","MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"MISMATCHES 0"}},{"id":"V9","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_round7_artifacts","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 69 tests in 497.770s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V10","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B scripts/check_paper_round7_artifacts.py --repository-root . --corpus-root /Users/edr/code/JouleWise","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["R7F PLACED 0/4","R7F COMPARED 415 / MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"COMPARED 415 / MISMATCHES 0"}},{"id":"V11","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_first_use_ledger tests.test_paper_terms_lint tests.test_paper_replay_fence tests.test_check_paper_replay_fence tests.test_paper_round7_artifacts tests.test_paper_successor_migration tests.test_select_outcome_branches tests.test_d165_rationale_census tests.test_paper_comparison_placements tests.test_paper_rendering tests.test_paper_build","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 175 tests in 548.199s","","OK (skipped=2)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V12","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B scripts/check_paper_replay_fence.py --corpus-root /Users/edr/code/JouleWise","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["MEMBER 20260722T145535-e941c821","COMPARED 43","MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"MISMATCHES 0"}},{"id":"V13","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B scripts/check_paper_replay_fence.py --draft docs/paper/draft-v1.md --literals-only","cwd":".","observed":{"result":"fail","exit_code":2,"tail":["FENCE EXTRACTION FAILED: residual subtraction: expected exactly one anchor match, found 0"]},"expected":{"exit_code":0,"tail_regex":"INTERNAL MISMATCHES 0"}}],"flags":[{"id":"REPEAT","kind":"lead_ruling","level":"nonblocking","text":"R2-2 repeats record 17 DELTA-2: the protected lexicon disagrees with the prose's actual definition home.","needs":"Lead: apply the repeated-signature consult gate before the next fix/merge decision."},{"id":"BUILD","kind":"verification_gap","level":"nonblocking","text":"Two optional build tests skipped because markdown-it-py is absent; build_paper.py was never run.","needs":"Lead-owned rendering/final verification."}]}
```

## Findings

**No blocker found. Two should-fix findings; no nits.** The envelope is 6,566 UTF-8 bytes.

Confirmed detached HEAD `e3285e67d6b616b020b95eaf1caf2e8089f240ff`. Both `482a0cc4` and `dbe6c675` are ancestors. The requested delta contains 10 files, 1,042 insertions and 75 deletions, including intermediate review records; the draft itself has 53 insertions and 48 deletions.

Record 19 was absent from this checkout. I read the runner report at `/Users/edr/code/JouleWise-wt-paper-n/docs/process_traces/2026-09-12-paper-n/19-fix-round-2-astra-report.md`. No repository files changed during this review.

### R2-1 — Should fix: the F7 regex replacement breaks frozen-v1 support

New [checker line 174](/Users/edr/code/JouleWise-wt-paper-n-ref/scripts/check_paper_replay_fence.py:174):

> `r"Subtracting the two printed bounds gives "`

The same function explicitly supports “Historical submission and the frozen v1 prose,” but the replacement accepts only the new subtraction wording. The committed v1 draft retains the old wording.

I loaded each revision’s checker and corresponding committed drafts directly from Git, without creating files:

```text
482a0cc4 docs/paper/draft-v2-skeleton.md EXTRACTED 22
482a0cc4 docs/paper/draft-v1.md EXTRACTED 22
HEAD docs/paper/draft-v2-skeleton.md EXTRACTED 22
HEAD docs/paper/draft-v1.md FenceError residual subtraction: expected exactly one anchor match, found 0
REPLAY_LITERALS_IDENTICAL 22 True
```

The direct v1 CLI also exits **2**; its exact command and tail are V13 above. The existing legacy-heading test changes only the heading of the current draft, so it misses this regression.

**Minimal cure:** accept either complete subtraction prefix while retaining the exactly-one-match check. Add a regression that extracts the actual committed `draft-v1.md`, alongside the current draft.

### R2-2 — Should fix: one synchronized lexicon home is still wrong

New [lexicon line 23](/Users/edr/code/JouleWise-wt-paper-n-ref/docs/paper/round7/built-terms-lexicon.md:23):

> `| declared machine state / instrument-validation manifest / reservation plan / calibration ledger / calibration-acceptance file | A.4 |`

But new draft line 142 already builds one member of that row:

> “the frozen reservation plan (the file naming reserved collection slots)”

The first-use ledger correctly retains this grouped row’s §2 home and explicitly mentions the newly added reserved-slot gloss. The successor lexicon and its protected tuple instead assign the entire group to A.4. Record 19 acknowledges the §2 gloss but nevertheless marks E/H2 DONE.

**Minimal cure:** preserve the existing row count and specify the split homes within this row: reservation plan in §2; the remaining named constructions in A.4. Update the protected tuple accordingly.

**Same-signature statements:** Against records 02/04 alone, **no exact repeat identified** for these two defects. Across both rounds, **YES**: R2-2 repeats **record 17 DELTA-2**, the protected lexicon disagreeing with actual definition placement. This is the explicit consult trigger; the lead should apply that gate before another fix/merge decision.

### Record 17 closure

| Finding | Verdict | Current passage and reason |
|---|---|---|
| DELTA-1 | **CURED** | Draft 157: “A pre/post difference above the threshold indicates a change in the compound calibration allowance; it does not distinguish a change in fitted edge response from a change in clock-placement uncertainty.” Matches A.3.6’s maximum-excursion-plus-anchor composition; representativeness and empirical-coverage qualifications remain. |
| DELTA-2 | **NOT CURED** | Lexicon 23 still assigns “reservation plan” to “A.4,” despite its new §2 gloss quoted above. The other six changed rows are synchronized. |
| DELTA-3 | **CURED** | Draft 1405: “In production, form \(d_j^-\) and \(d_j^+\) using `math.fsum`”; 1414: “with the final addition also evaluated using `math.fsum`.” Both match `dominance_closeout.py:597–614`. |

### F1–F10 closure

Locations below refer to the current draft. F7 distinguishes the successful prose correction from its associated checker regression.

| Finding | Quoted cured passage | Verdict | Reason |
|---|---|---|---|
| F1 | 300–301: “in \([-a,a]\), and move the start and end independently in \([-(b+w),b+w]\)”; 317: “\(E^L=E-h\) and \(E^U=E+h\)” | **CURED** | Read `reduce.py:2148–2268` and `floor_extraction.py:2100–2117`. Domains, breakpoint evaluation, refusal and symmetrization agree. |
| F2 | 402: “`nextafter(start+b, +∞) < nextafter(end−b, −∞)`”; 438–439: “`effective_clock_anchor_bound_s`” and “`wall_minus_monotonic_span_s`” | **CURED** | Matches `floor_extraction.py:376–389,2430–2494`; the local residual call sets the shared calibration term to zero. |
| F3 | 1197: “In exact arithmetic, no point of C can have loss below LB(C)”; 1206: “no independently established directed-rounding containment guarantee” | **CURED** | Analytic containment remains distinguished from floating-point execution. |
| F4 | 127: “For adjacent phases sharing the moved boundary…”; “the historical phase windows have separately stamped endpoints and may leave a gap” | **CURED** | Conservation is conditioned on the required shared-boundary geometry. |
| F5 | 86: “in the fit’s model-defined accepted region”; §4: “rectangular model’s switch-on and switch-off times”; 1158: “fixed central portion”; 1153: “possible uncommanded GPU activity”; 817–818: “gain was not independently checked”; 915: “outcomes differed”; 716–717: “depends on alignment as well as record width” | **CURED** | All seven original sites retain their qualifications; no new physical-validation or causal overclaim found in this delta. |
| F6 | 157: “registered independent, equal-variance normal-model design convention”; 155: “Prospective claim use separately refuses…”; 1253–1256: “predecessor members were excluded because no single affine wall-versus-monotonic rate reconciles their stamp rectangles…” | **CURED** | Selection/exclusions match the acceptance JSON; admission distinction matches `uncertainty_evidence.py:840–844`. DELTA-1 is now cured. |
| F7 | 550: “Subtracting the two printed bounds gives \(0.030067931757111657-0.0011349971959968978=0.0289329345611147592\) s; the separately retained largest pulse residual is recorded in the source artifact (Appendix A.3.6).” | **REGRESSED — checker only** | Prose now correctly distinguishes the quantities, and current-draft extraction is unchanged. The accompanying regex breaks supported frozen-v1 extraction: R2-1. |
| F8 | 1411–1414 define padded \(q_j\), ending “using `math.fsum`”; 1415–1418 name `dominance_closeout.py`, `detection_floor.py`, and “unpadded illustrative widths” | **CURED** | Padding, outward steps, implementation roles and illustrative-table qualification match the implementation. |
| F9 | 848: “JouleWise applies timing analysis…” and “Whole-request agreement…alone does not determine…”; 863: “JouleWise calculates timing sensitivity of assigned phase energies.” | **CURED** | All three original claims remain narrowed. |
| F10 | 146: “resting power \(P_{\mathrm{rest}}\)”; 157: “retained SD operand”; 298: “window’s operative timing bound” | **CURED** | Power and timing notation remain distinct; the retained SD is no longer called unrounded. |

### New-sentence evidence audit

The first column uses the round-1 contract IDs requested in the brief; round-2 additions are identified separately. Quotes reproduce the relevant introduced sentences or clauses, with line wrapping normalized.

**No novel quantitative digit entered the main text.** Existing numerical occurrences and section/citation identifiers are distinguished, following record 12’s rule permitting numbers already printed elsewhere in the draft.

| Item | Current quotation | Support and digit assessment |
|---|---|---|
| A1/A2 | 18, 39: “This paper specifies the sensitivity calculation and demonstrates it on synthetic inputs; it reports no sensitivity ratio on measured inference data.” | Supported by §3’s synthetic calculations and §4’s historical diagnostics. No digits. |
| A2 | 39, 820: “The raw captures behind the historical numbers are retained by the project and are not released; the synthetic examples are the only fully reproducible part.” | Consistent with §7’s release limitation. No digits. |
| C6 | 144: “a rectangle is rejected only when a mathematical lower bound proves in exact arithmetic that none of it can pass”; 1206: “The implemented floating-point search has no independently established directed-rounding containment guarantee.” | Matches A.3.5’s analytic argument and implementation qualification. No new digit. |
| C7 | 157: “the two-draw rule is the registered independent, equal-variance normal-model design convention” | States the assumptions behind the retained calculation. Existing operands remain unchanged. |
| C7 | 157: “Interpreting this threshold as an instrument screen is conditional on the retained corpus being representative, which has not been tested; empirical 99% coverage has not been established.” | Consistent with the selected corpus and absence of a coverage validation. `99%` already existed. |
| C7 / round-2 H1 | 157: “A pre/post difference above the threshold indicates a change in the compound calibration allowance; it does not distinguish a change in fitted edge response from a change in clock-placement uncertainty.” | Supported by A.3.6’s compound bound. No digits. |
| C7 | 155: “Prospective claim use separately refuses active or unknown automatic network-time correction; historical evidence with correction ON or unknown is restricted to diagnostic use.” | Matches `uncertainty_evidence.py:840–844`. No digits. |
| C7 | 1250–1256: “The selection is valid protocol-v3 captures before the excluded Window-B judged pair, from the exact identity epoch specified by that file, re-derived from primary bytes under the current rate-aware anchor. Two predecessor members were excluded because no single affine wall-versus-monotonic rate reconciles their stamp rectangles with their native whole-second labels inside the fixed model-departure allowance; these are not an unrestricted sample of captures.” | Checked against the acceptance file’s selection and two excluded-member records. Appendix text; no new main-text number. |
| D1 | 299–306: “Shift the whole trace by a common displacement in \([-a,a]\), and move the start and end independently in \([-(b+w),b+w]\).” “At each endpoint-movement corner, evaluate the common trace displacement at its domain endpoints, zero, and every in-domain record-edge/window-edge coincidence…” “Refuse if the trace does not cover every required shifted window or a moved window ends before it starts.” | Matches the named reducer domain, corner scanner and refusal. No novel digit. |
| D1 | 310–317: “The floor consumes a symmetric interval, not those potentially asymmetric raw extrema”; “the floor inputs are \(E^L=E-h\) and \(E^U=E+h\)” | Matches `floor_extraction.py:2100–2117`. |
| D1 | 401–403: “require strict noncollapse: `nextafter(start+b, +∞) < nextafter(end−b, −∞)` for each member; in exact arithmetic its duration must exceed \(2b\). Refuse otherwise.” | Matches the strict code predicate. Existing `2` reused. |
| D2 | 380: “R asks how much the bound grows when every run’s edges move independently; R_cm asks how much it grows when one direction of energy allowance is applied to every block at once and each block’s own edges then move to their worst local corner.” | Consistent with the following shared-energy-sign/local-corner construction. No digits. |
| D2 | 431–432: “The main-text illustration uses this unpadded formula; Appendix A.3.10 defines the padded production value of \(q_j\) used in the same sign enumeration.” | Supported by A.3.10 and `dominance_closeout.py:596–617`. Subsection identifier only. |
| E1 | 127: “For adjacent phases sharing the moved boundary, the request total does not change: energy removed from one phase is added to the other; the historical phase windows have separately stamped endpoints and may leave a gap.” | Correct qualification of the schematic and historical geometry. No digits. |
| E4 | 1195: “On the retained capture, σ sat at its 1-mW floor while plateau scatter was of order a watt around the fitted pulse height, vastly larger than σ.” | A.3.5:1151 reports zero baseline MAD and σ=`0.001 W`; Table A3:1309 repeats σ, and plateau rows 1325–1332 show watt-scale deviations. |
| E4 / round-2 B4 | 822–824: “On the retained capture, σ sat at its 1-mW floor despite much larger plateau scatter; the accepted region is therefore a tolerance set whose width depends on the 5% loss tolerance and the 1-mW noise floor of Appendix A.3.5, which were not varied.” | Matches σ’s floor and `Λ = Loss* + max(1.0, 0.05 · Loss*)`. Existing `1` and `5%` retained; no new value. |
| E5 | 826–831: “The 59 of 59 onsets late and 49 of 59 offsets early form a one-directional pattern. GPU start latency after the command and sampler window stamping are two candidate explanations; neither was tested. With no tested explanation to support a correction, no correction is applied. The symmetric \(\pm b\) domain therefore includes the bias and is wider on the side the bias does not occupy.” | Counts match §4. **Both candidate explanations explicitly remain untested.** Existing counts reused. |
| E6 / round-2 G3 | 657–660: “A per-edge allowance of a few tens of milliseconds, as in the Section 2 example (Section 2's worked example, not a measured window bound), amounts across both edges to more than half of the 1.5B median and roughly a quarter of the 7B median.” | Synthetic origin is explicit. `2×38.724/136.5 = 0.5673846…`; `2×38.724/281.5 = 0.2751261…`. Both worded comparisons are reasonable; no new numeric fraction is printed. |
| E6 | 660–662: “The three-record minimum guards only against a split supported by two straddling averages, not against a timing envelope comparable to the phase energy.” | Consistent with the support rule and separate energy-sensitivity calculation. No digits. |
| F2 | 857: “cross-checks sufficiently long sampled-power integrals against the GPU's own hardware energy counter on the same telemetry interface [13]. JouleWise lacks that counter cross-check.” | Consistent with record 08’s source excerpts; no independent-instrument claim. Citation unchanged. |
| F2 | 859: “Its disclosed method in the published paper does not specify the boundary events, alignment rule, repetition and variance protocol, idle baseline (power with no workload), or external validation needed to reconstruct a phase-attribution error budget.” | Properly scopes the absence claim to the examined paper; record 08 supplies the prior evidence. No quantitative digit. |
| F3 | 848: “JouleWise applies timing analysis to phase-resolved `powermetrics` inference on Apple Silicon.” “Whole-request agreement with an external wall meter alone does not determine the software trace’s phase split.” | Consistent with the specified method and phase-allocation distinction. No digits. |
| F3 | 863: “JouleWise calculates timing sensitivity of assigned phase energies.” | Describes the calculation without claiming measured inference transfer. No digits. |
| Round-2 A1 | 108: “The absolute floor is built from centered repeat energies, the comparative floor from same-model block differences, and a science contrast is a difference between two models; Section 3 gives each construction. For each block, the difference is mean B energy minus mean A energy.” | Matches §3 and the four-member difference formula in §2. Section identifier only. |
| Round-2 A2 | 313–315: “the registered joint-interpolation allowance, the extra half-width charged when a record's power must be interpolated between reported averages rather than held flat; it is zero for the native interval-average records used here.” | `reduce.py:554–555` returns zero for admitted positive-duration native-support windows; `floor_extraction.py:2114–2117` adds the joint allowance to the raw-envelope half-width. No digits. |
| Round-2 G1 | 517–519: “The cell floor is the final gate value for assigned-energy differences in a cell after the publication safeguards of Section P.3…” | Agrees with the linked protocol’s final gate. No new quantitative value. |

The added median, MAD, fingerprint, provenance, idle-baseline and disaggregated-inference glosses introduce no quantitative value. The Huber gloss agrees with the quadratic/linear behavior described by A.3.5.

### Literal preservation

Every retained quantitative literal examined below is byte-identical. Repeated literals are grouped by affected passage; paired line groups correspond in order. The census includes whole paragraphs intersected by the diff, exceeding the changed-line-only scope.

| Literal(s) | Old line(s) | New line(s) | Result |
|---|---:|---:|---|
| `59`, `49`, `37`, `50`, `13`, `33`, `17`; both full Qwen2.5 model names | 21–27 | 21–27 | SAME |
| `500` | 86 | 91 | SAME |
| `24`, `59`, `4096` twice, `16`, `100`, `4.5` | 135 | 142 | SAME |
| `59` in detector admission | 137 | 144 | SAME |
| `1.4826`, `0.001` | 140–141 | 147–148 | SAME |
| `5`, `0`, `6`, `7` in quiet-record example | 141–142 | 148–149 | SAME |
| `10`, `4`, `5` in signal/loss examples | 143 | 150 | SAME |
| `0.5`, `0.499`, `0.500`, `0.75` | 144–145 | 151–152 | SAME |
| `17`, `99%`, `0.995`, `16`, `0.5%`, `1`, `2` in calibration calculation | 150 | 157 | SAME |
| `2.460856`, `2.460856207694636` | 150 | 157 | SAME |
| `3`, `2.92078162242509999197` | 150 | 157 | SAME |
| `10`, `10.164834757777545`, `10.164835` | 150 | 157 | SAME |
| `9.723589288793850`, `9.724` | 150 | 157 | SAME |
| `25`, `29`, `4`, `38.724` | 150 | 157 | SAME |
| Formula indices/constants `1`, `2`; corner cap `16` | 314–330 | 320–336 | SAME |
| `59`, `122{,}859` | 544 | 550 | SAME |
| `0.0011349971959968978` | 544 | 550 | SAME |
| `0.030067931757111657` | 544 | 550 | SAME |
| `0.0289329345611147592` | 544 | 550 | SAME |
| `26.625`, `27.625` | 544 | 550 | SAME |
| `1784757381.2856488`, `1784757382.293089`, `1970` | 544 | 550 | SAME |
| `0.02544938965763524`, `0.02893293456111476` | 544 | 550 | SAME |
| `-0.008607394549133255`, `-0.005308621075866744` | 544 | 550 | SAME |
| `+0.027`, `-0.007`; “tenth” | 544 | 550 | SAME |
| `0–58`, `59` | 574, 576–577 | 580, 583–584 | SAME |
| `+13.0`, `−5.5` | 579 | 586 | SAME |
| `9`, `+27` | 582 | 589 | SAME |
| `28.93293456111476`, `1.1349971959968978`, `30.067931757111657` | 585–587 | 591–593 | SAME |
| `0.5`-ms grid | 588 | 594 | SAME |
| `1.5B`, `7B`; `10`, `40`, `37`, `50`, `13`, `33`, `17` | 635–661 | 641–667 | SAME |
| `0.2815`, `0.1365`, `120.9` | 649–650 | 655–656 | SAME |
| `0.121034145`, `0.121`, `406`, `120.9186` | 684–686 | 689–691 | SAME |
| `5.9508`, `1`, `0.25`, `0.75`, `405` | 688–691 | 693–696 | SAME |
| `120.9224`, `5.8949` | 693 | 698 | SAME |
| `0.000001`, `100`, `405`, `0.0000004` | 696–698 | 701–703 | SAME |
| `37`, `50`, `13`, `1.5B` in source-map paragraph | 742–744 | 747–749 | SAME |
| `1`-mW, `5%` | 817–819 | 822–824 | SAME |
| Four outward steps, `out_4`; “eight” sign cases | 1402–1415 | 1407–1420 | SAME |

The explicit presentation changes are **`R ≥ 2 test` → `doubling test`** in the abstract, prescribed by N-10, and **`Table 4` → `Table A4`**, prescribed by B5. The threshold remains `R≥2` in §3; the table label is an identifier. Neither changes a numerical result. No retained literal was rounded or replaced.

Section/citation numbers, corpus names, registry identifiers and `SHA-256` remain identifiers, as in record 02’s census. The newly repeated `A.3.10` locator already existed in the draft.

The retained rounded readings remain correct:

```text
old 150 -> new 157: about 3 (retained as 2.92078162242509999197 for byte-exact replay)
old 150 -> new 157: about 10 ms (retained as 10.164834757777545 ms for byte-exact replay)
old 530 -> new 536: about 1 µs (retained as 0.0000010000000000000002 s for byte-exact replay)
old 788 -> new 791: about 30 ms (retained as 0.030067931757111657 s for byte-exact replay)
NEW_MAIN_NUMERIC_LEXEMES []
```

F7 extraction, identical before and after:

```text
subtraction_minuend 0.030067931757111657
subtraction_subtrahend 0.0011349971959968978
subtraction_result 0.0289329345611147592
REPLAY_LITERALS_IDENTICAL 22 True
```

### Seven-row lexicon synchronization

| Changed row | Stated home | Actual first build | Verdict |
|---|---|---|---|
| powermetrics | Abstract | Draft 12 | MATCH |
| cell floor | §3 | 517–519 | MATCH |
| Point/corner values and independent-edge ratio | §3 | 195–204 | MATCH |
| Energy-allowance/shared/local signs | §3 | 382–385 | MATCH |
| Machine-state/manifest/reservation-plan/ledger/acceptance-file group | A.4 | Reservation plan: §2, 142; remaining named constructions: A.4, 1444 | **MISMATCH: R2-2** |
| mint | A.4 | 1444 | MATCH |
| Measured contrast/custody/Figure P1 | Protocol P.3 / §7 | Protocol’s decision-gate construction; draft 885–886 for custody | MATCH |

The draft-v1 generated base was not changed. The row count remains unchanged.

### Moves, HTML comments and retired locators

The original B1, B3, C1 and D2 moved spans had **no attached HTML comments**. Their round-1 placements survive this delta:

| Item | Round-1 → round-2 location | Verification |
|---|---|---|
| B1 component/ratio construction | 188 onward → 195 onward | Preserved in §3; this round removes the duplicate floor-definition block and inserts the prescribed introductory gloss. |
| B3 synthetic enclosure | 179 → 186 | Paragraph byte-identical. |
| C1 integrity sentences | 1439 → 1444 | Original removed sentences remain a byte-identical substring, including identifiers. |
| D2 padding/sign table | 1360 onward → 1365 onward | Remains in A.3.10; only the authorized `math.fsum` wording and Table A4 label change. |

All 15 HTML comment occurrences remain byte-identical and in the same order:

```text
1 -> 1
32 -> 32
541 -> 547
542 -> 548
545 -> 551
546 -> 552
547 -> 553
779 -> 782
788 -> 791
804 -> 807
815 -> 818
830 -> 835
915 -> 920
941 -> 946
1475 -> 1480
HTML_COMMENTS 15 15 BYTE_IDENTICAL True
```

The last mapping preserves `[FILL:PE-01]`. The moved §5 raw-capture sentence had no attached comment; the existing limitation-source comment remains with the First/Second/Third discussion.

I extracted the census checker’s complete retired-site list, translated its token boundaries/wildcards to grep ERE patterns, and supplied them on stdin:

```text
RETIRED SITES 228
grep -E -c -f /dev/stdin docs/paper/draft-v2-skeleton.md
0
grep exit 1
```

Exit 1 is the expected no-match result. Both round-7 checks independently pass the retirement census.

### Verification tails and seat comparison

V1–V11 reproduce the substantive census §3 checks, using the user-required `python3 -B`; `PYTHONDONTWRITEBYTECODE=1` also protects subprocess imports. The explicit corpus variant was used where the census offers alternatives. V12 is the separately requested direct replay. Every exact command and tail is pasted in the envelope.

Additional Markdown output:

```text
Images checked: 9
Missing images: 0
Heading-level jumps: 0
Tables checked: 6
Broken table rows: 0
Hard defects: 0
Exit: 0
```

| Check | Seat’s before | Seat’s after | This audit |
|---|---|---|---|
| Replay fence | `COMPARED 43`; `MISMATCHES 0` | Same | Same |
| Round-7 literals | `R7F PLACED 0/4`; `R7F LITERALS-ONLY COMPARED 412 / MISMATCHES 0` | Same | Same |
| Round-7 full replay | `R7F PLACED 0/4`; `R7F COMPARED 415 / MISMATCHES 0` | Same | Same |
| Paper aggregate | — | 175 tests, two optional skips | 175 tests, two optional skips |
| Actual frozen-v1 extraction | Not reported | Not reported | **Fails: R2-1** |

Final `git diff --check` and `git diff --exit-code` passed. HEAD and the two pre-existing untracked manifests were unchanged. Next exact step: lead adjudication of R2-1/R2-2 and the repeated-signature consult gate.

## Residual risk

- Two optional build tests skipped because `markdown-it-py` is absent. The prohibited build script was never run; rendered layout remains lead-owned.
- This was a delta audit and retained-byte replay, not live hardware validation, pulse-to-inference validation or an empirical coverage study.
- Related-work checks used the draft and retained record-08 source evidence; no new literature audit was performed.