```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "No blocker found. Headline numbers match their registered historical populations; reproducibility rules and several metrological claims need correction.",
  "workspace": {
    "base_requested": "dbe6c675",
    "base_mode": "exact",
    "head_start": "dbe6c675db09622b098eb5040122734c95ff41fa",
    "head_end": "dbe6c675db09622b098eb5040122734c95ff41fa",
    "upstream_end": "dbe6c675db09622b098eb5040122734c95ff41fa",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "blockers": 0,
    "findings": [
      {"id":"F1","severity":"should_fix","summary":"Independent-edge calculation omits the timing-domain construction and symmetric energy-interval construction."},
      {"id":"F2","severity":"should_fix","summary":"Shared/local replay omits its noncollapse precondition and the member-local timing-domain definition."},
      {"id":"F3","severity":"should_fix","summary":"Pulse-region numerical containment is stated more strongly than the floating-point implementation establishes."},
      {"id":"F4","severity":"should_fix","summary":"Conservation across a shared phase boundary needs qualification for separately recorded phase endpoints and gaps."},
      {"id":"F5","severity":"should_fix","summary":"Several physical-validation, edge-location and causal statements exceed their supporting evidence."},
      {"id":"F6","severity":"should_fix","summary":"Calibration exposition omits corpus selection and statistical assumptions and conflates clock estimation with network-time admission."},
      {"id":"F7","severity":"should_fix","summary":"Section 4 labels subtraction of printed bounds as the retained pulse residual, contradicting Appendix A.3.6."},
      {"id":"F8","severity":"should_fix","summary":"Shared-sign source map names the wrong implementation module and does not distinguish padded production widths from unpadded illustration widths."},
      {"id":"F9","severity":"should_fix","summary":"Related-work novelty and validation statements need narrower wording."},
      {"id":"F10","severity":"nit","summary":"The symbol b changes dimensions, and a retained rounded SD operand is called unrounded."}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"suite",
      "cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest tests.test_paper_replay_fence tests.test_paper_round7_artifacts tests.test_paper_first_use_ledger",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 90 tests in 481.854s","OK"]},
      "expected":{"exit_code":0,"tail_regex":"Ran 90 tests in .*s\\s+OK"}
    },
    {
      "id":"V2",
      "kind":"inspection",
      "cmd":"python3 -B -c 'import json,runpy; from pathlib import Path; a=runpy.run_path(\"docs/paper/figures/reproduce_worked_examples.py\")[\"synthetic\"](); b=json.loads(Path(\"docs/paper/figures/worked-examples.json\").read_text())[\"synthetic\"]; assert json.loads(json.dumps(a)) == b; print(\"SYNTHETIC PAYLOAD MATCH: all registered fields\")'",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["SYNTHETIC PAYLOAD MATCH: all registered fields"]},
      "expected":{"exit_code":0,"tail_regex":"SYNTHETIC PAYLOAD MATCH: all registered fields"}
    },
    {
      "id":"V3",
      "kind":"inspection",
      "cmd":"git status --short --branch && git rev-parse HEAD && git rev-parse origin/main && git diff --stat",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","dbe6c675db09622b098eb5040122734c95ff41fa","dbe6c675db09622b098eb5040122734c95ff41fa"]},
      "expected":{"exit_code":0,"tail_regex":"## HEAD \\(no branch\\)\\s+dbe6c675db09622b098eb5040122734c95ff41fa\\s+dbe6c675db09622b098eb5040122734c95ff41fa"}
    }
  ],
  "flags": [
    {
      "id":"R1",
      "kind":"environment",
      "level":"nonblocking",
      "text":"No runner-owned output pathname was supplied in the visible brief. The complete report is returned here; no report file or repository file was written.",
      "needs":"Runner to persist this response at its external report path."
    }
  ]
}
```

## Findings

**No blocker found.** All headline counts and median durations match the registry and the stated historical populations. The material issues concern specification completeness and the strength of particular sentences.

Locations below refer to `docs/paper/draft-v2-skeleton.md` at the reviewed commit.

### F1 — Should fix: specify the independent-edge calculation’s inputs

**§3:333–335:**

> “Each admitted repeat energy has lower and upper values obtained by moving its phase boundaries through the permitted timing domain. For the absolute component, enumerate the \(2^n\) lower/upper choices for the n repeat energies.”

A reader cannot reconstruct those lower and upper values from §2–§3 and A.3 alone. The missing steps are:

- The member’s own clock-anchor displacement, the shared calibration allowance, and the member’s wall-minus-monotonic edge span are distinct inputs. Their domains and composition are not given here.
- For interval-average traces, the common trace displacement requires record-edge/window-edge breakpoints as well as domain endpoints. Merely evaluating lower/upper **timing** coordinates can miss an interior energy extremum.
- The extraction implementation symmetrizes the resulting energy envelope about the admitted point. In `joulewise/floor_extraction.py:2100`, it takes the larger displacement from the point to either endpoint, includes the recorded maximum displacement, and adds the registered joint-interpolation term. The floor then consumes point ± half-width. The text can instead be read as consuming the raw, potentially asymmetric extrema.

**Minimal cure:** insert the member-domain construction and define the actual floor-input endpoints explicitly. Distinguish the raw integration envelope from the symmetric interval consumed by the floor. State the breakpoint rule and the refusal when the required trace coverage is absent. This documents the existing method; it requires no new analysis or experiment.

The convexity argument at §3:345–349 is consistent once the input box has been defined.

### F2 — Should fix: state the shared/local replay’s domain

**§3:398–406:**

> “Reintegrate the four retained power traces after moving all four phase starts by the same shift while holding their ends fixed.”

**§3:451–455:**

> “Next set the shared calibration-pulse timing movement to zero and, for each of the four block members, recompute phase energy from the same power trace while moving only that member's remaining local clock and edge uncertainty.”

Two necessary rules are missing:

1. **Strict noncollapse.** Each member must satisfy `nextafter(start+b, +∞) < nextafter(end−b, −∞)`. In exact arithmetic this requires duration > \(2b\). The implementation refuses outside that domain; it does not evaluate the displayed separable construction for arbitrary short windows. See `joulewise/floor_extraction.py:376` and `joulewise/dominance_closeout.py:870`.
2. **Local widths.** “Remaining local clock and edge uncertainty” is not a numerical domain. The implementation uses the member’s `effective_clock_anchor_bound_s` for the common trace displacement and its `wall_minus_monotonic_span_s` for independent endpoint movements, with the shared fiducial term set to zero. It then takes the largest absolute energy displacement. See `joulewise/floor_extraction.py:2478` and `joulewise/reduce.py:2150`.

**Minimal cure:** state those two rules immediately before their respective calculations. Also state the required nonnegative interval-support trace and coverage conditions. The three-record rule is already explained in §4:669–678; a cross-reference suffices where that separate admission rule is needed.

### F3 — Should fix: distinguish the analytic enclosure proof from floating-point execution

**§2:204:**

> “After finding the best pair, it encloses every pair close enough to that fit: a rectangle is rejected only when a mathematical lower bound proves that none of it can pass, and every surviving rectangle is split to a fixed resolution.”

**A.3.5:1220:**

> “No point of C can have loss below LB(C), because each term is the smallest Huber value its interval can attain anywhere in C.”

**A.3.5:1221:**

> “Because a cell is discarded only on a rigorous lower bound and retained cells are kept whole, every accepted point is inside some retained cell — including points between resolution cells.”

These are valid analytic statements under exact arithmetic. The implemented lower-bound routine uses ordinary floating-point operations and `total +=`, without a downward-rounding enclosure. Its residual expression also differs in operation order from the point-loss expression.

A read-only calculation found this singleton-cell witness using the existing functions:

| Input/result | Value |
|---|---:|
| Interval | [0, 0.1] s |
| Commanded pulse | [0, 1] s |
| Both shift intervals | [0, 0] s |
| Observed power | 40.644297511918104 W |
| Amplitude | 38.16879467373651 W |
| Baseline / σ | 0 W / 0.001 W |
| `_pulse_loss` | 3328.6468048542483 |
| `_pulse_loss_cell_lower_bound` | 3328.646804854253 |
| Computed “lower bound” minus point loss | \(4.547473508864641\times10^{-12}\) |

This demonstrates that the floating-point routine does not preserve the stated inequality unconditionally. It does **not** demonstrate loss of a region in the historical capture.

**Minimal cure:** qualify the proof as an exact-arithmetic property and disclose that the implemented floating-point search has no independently established directed-rounding containment guarantee. Preserve the reported historical values.

### F4 — Should fix: qualify shared-boundary conservation

**Abstract:16–17:**

> “Moving the dividing time, the phase boundary, reallocates energy without changing the request total.”

**§2:176:**

> “The request total does not change: energy removed from one phase is added to the other.”

**§1:44–48** defines two phases separated by one runtime-recorded boundary. The historical source, however, retains separate prefill-end and decode-start events. For r03, NR records:

- prefill end: `1784978933.3887181`;
- decode start: `1784978933.388722`;
- intervening gap: `3.814697265625` µs.

Protocol P.2:150–155 expressly recognizes an unphased gap.

The conservation statement is correct for two adjacent windows sharing the moved boundary. It is not a complete description of independently recorded endpoints: energy removed from prefill need not be assigned to decode.

**Minimal cure:** write “For adjacent phases sharing the moved boundary…” before the reassignment statement, and briefly distinguish that schematic from the separately stamped historical phase windows and their possible gap. The reported overlap counts do not need changing.

### F5 — Should fix: narrow physical-validation and causal wording

| Location and sentence | Stronger reading | Minimal cure |
|---|---|---|
| §1:95–97: “The largest displacement between the commanded times and every edge position allowed by the pulse records, plus the **clock-anchor bound**—the uncertainty in placing the power record on wall-clock time—is the **pulse-derived limit**.” | The records themselves delimit all possible physical edge positions. | Replace “allowed by the pulse records” with “in the fit’s model-defined accepted regions.” |
| §4:608: “Onsets switch work on; offsets switch it off.” | Fitted transitions are observed physical actuation times. | “Fitted onsets and offsets are the rectangular model’s switch-on and switch-off times.” |
| A.3.5:1181: “**Interior set**: intervals in L with start ≥ on + 0.25 and end ≤ off − 0.25 … — the part of the plateau that no plausible edge smear reaches.” | The selected interior is guaranteed uncontaminated by edge movement. | End with “the fixed central portion used to estimate amplitude.” Accepted fitted shifts can approach 0.5 s, and the accepted-region search extends to 0.75 s; neither supports the 0.25-s guarantee. |
| A.3.5:1176: “Any spurious plateau invalidates the capture — it means the GPU did work when nothing was commanded, and a fit could not distinguish that from instrument timing.” | Threshold exceedance establishes the physical cause. | “Any spurious plateau invalidates the capture because it is treated as possible uncommanded GPU activity that the fit cannot distinguish from instrument timing.” |
| §5:848–852: “We report joules rather than counter-internal units because watts integrated over seconds give an interpretable energy quantity, while the unmeasured gain means that quantity is validated only on the counter's reported scale.” | Some independent validation of the energy scale occurred. | Replace the final clause with “the quantity remains expressed on the counter’s reported scale, whose gain was not independently checked.” |
| §4:697–698: “Record identifiability depended on the model/stack in these retained populations.” §8:936: “Record identifiability depended on the model/stack.” | A model/stack effect has been established, rather than a difference between historical populations. | “Record-support outcomes differed between the retained model/stack populations.” |
| §4:750–751: “Alignment, not width alone, therefore denies the third overlap in most phases of the Qwen2.5-1.5B-Instruct-4bit population.” | The population-wide failure mechanism has been separated into alignment and width effects. The displayed geometry establishes examples, not that decomposition for all 37 failures. | “The overlap count depends on alignment as well as record width; 37 phases had only two overlaps.” |

The abstract, §4:599–605 and §8:923–926 clearly identify historical re-analysis. I found no sentence implying that this capture was recollected. The explicit pulse-to-inference limitations are consistent across those sections.

The comparisons of counts and durations do not assert an energy comparison. The “depended” wording above is the remaining causal ambiguity.

### F6 — Should fix: complete the calibration selection and admission description

**§2:208:**

> “The frozen calibration-acceptance rule … derives two constants from its retained 17-capture corpus.”

**A.3.8:1267–1271:**

> “These are the 17 per-capture \(b_{\mathrm{fiducial}}\) bounds used by the n17 acceptance generation, not pre/post differences.”

The table makes recomputation from those selected values possible, but does not state how the corpus was selected. S17’s `derivation_corpus.selection` specifies valid protocol-v3 captures before the excluded Window-B judged pair, the exact identity epoch, current-anchor re-derivation, and exclusion of two predecessor members whose stamp rectangles admit no single affine wall rate.

**Minimal cure:** add that selection rule beside the table, including the two exclusions and their criterion. Do not describe the 17 as an unrestricted sample of captures.

**§2:208:**

> “…the two-draw rule—two fresh capture bounds are drawn, and the spread of their difference is \(\sqrt{2}\) times one capture's spread…”

That equality needs independent, equal-variance draws; use of the Student-\(t\) predictive rule also needs its distributional assumptions. The text describes the quantile but leaves those assumptions implicit.

**Minimal cure:** identify this as the registered independent, equal-variance normal-model design convention, without claiming empirically established 99% coverage.

**§2:206:**

> “It refuses … active automatic network-time correction…”

A.3.3 supplies no network-time input or corresponding arithmetic check. The estimator accepts stamps and records; prospective claim admission separately requires authenticated network-time-OFF evidence. The distinction is explicit in `joulewise/uncertainty_evidence.py:840–844`.

**Minimal cure:** attribute network-time refusal to prospective admission, not the clock estimator, and state how ON/unknown historical evidence is restricted to diagnostic use.

Other requested calibration details are present: onset/offset objective, fixed amplitude, grids, tie rule, loss tolerance, margins, schedule, projection resolution, traversal, budget and capture-validity checks.

### F7 — Should fix: distinguish printed subtraction from the stored residual

**§4:588:**

> “Therefore the largest pulse residual before the anchor term is \(0.030067931757111657-0.0011349971959968978=0.0289329345611147592\) s.”

**A.3.6:1246:**

> “That difference is what the two published numbers give when subtracted; it is not itself the value the code retains for the worst edge excursion, which is computed and stored separately.”

The appendix correctly distinguishes the quantities. DG-030 supplies the decimal subtraction; DG-042 supplies the retained endpoint maximum, `0.02893293456111476` s.

**Minimal cure:** replace the first sentence with “Subtracting the two printed bounds gives … s; the separately retained largest pulse residual is … s.” This is a provenance/definition correction, not a physically meaningful change in magnitude.

### F8 — Should fix: correct the shared-sign source map and padding instructions

**§3:521–524:**

> “Source map: `tests/fixtures/fcm_r4_real_blocks/measured_pair.json` contains `blocks` with each point difference, onset/offset extrema and local member residual; `joulewise/detection_floor.py` implements the shared/local enumeration.”

The shared-sign/local-corner enumeration is in `joulewise/dominance_closeout.py`, function `replay_common_mode_dominance`. `detection_floor.py` supplies the underlying complete floor formula; its legacy two-shared-edge callable is not this replay.

**Minimal cure:** name those two roles separately.

**§3:434–437** applies the pad and four outward steps to the excursion endpoints, but **§3:418 and 466** continue to use \(q_j\) without specifying its padded replacement. Production also rounds outward after taking the endpoint maximum and after adding the zero-point discrepancy.

The worked-example producer intentionally uses unpadded illustration widths:

| Block | Illustration \(q_j\) | Production shared width |
|---|---:|---:|
| 1 | 0.2617693341820697 | 0.2617693341828027 |
| 2 | 0.615309913527021 | 0.6153099135277539 |

**Minimal cure:** define the padded \(q_j\) used in production, including the subsequent outward steps, and state that the displayed sign table uses the unpadded illustrative formula. Its printed precision is unaffected.

### F9 — Should fix: narrow three related-work claims

**§6:869:**

> “For phase-resolved `powermetrics` inference on Apple Silicon, JouleWise opens the complementary time axis: where in time a counter places the energy it reports.”

The same paragraph credits Khan with lag alignment, temporal correlation, granularity and timestamps; §6:871 credits Hähnel with explicit edge alignment. “Opens” can therefore imply a novelty claim contradicted by the article’s own account.

**Minimal cure:** “JouleWise applies timing analysis to phase-resolved `powermetrics` inference on Apple Silicon.”

**§6:869:**

> “Those studies establish how to validate counter gain; an external wall meter still cannot determine how a software trace should divide a correct total between prompt processing and token generation.”

The categorical inability is stronger than the supported statement about whole-request agreement.

**Minimal cure:** “Whole-request agreement with an external wall meter alone does not determine the software trace’s phase split.”

**§6:884:**

> “JouleWise inherits that boundary discipline rather than replacing it: JouleSort names the synchronization problem at whole-run scale; JouleWise measures its consequence at phase scale.”

The retained empirical timing result concerns GPU pulses; inference transfer and phase-accounting characterization were not performed.

**Minimal cure:** replace the final clause with “JouleWise calculates timing sensitivity of assigned phase energies.”

From the text itself, I found no definite citation-ID/title/year mismatch in §6 versus §9. The named works map consistently to their reference entries. Source-of-record verification remains with the separate seat.

### F10 — Nit: notation and precision labels

- **§2:193** defines baseline power \(b\), in watts; **§2:208** reuses \(b\) for the operative timing bound, in seconds. **A.3.5:1171** again uses \(b\) for baseline power. The formulas are distinguishable by context, but the same symbol does not retain its meaning. **Minimal cure:** use \(b_{\text{base}}\) and \(b_{\text{win}}\), or explicitly declare their local scopes.
- **§2:208** calls `2.460856207694636` ms “unrounded.” S17 labels the corresponding seconds value `sample_sd_presentation_s`, rounded half-even to \(10^{-18}\) s. **Minimal cure:** call it the “retained SD operand.” The stated downstream calculation matches the registered binary64 rule.

### Number-trace table

The census includes quantitative numerals and spelled-out counts. Repeated values are consolidated with their locations. Digits embedded solely in section numbers, reference IDs, filenames, hashes, schema names and `binary64` are identifiers, following the registry’s own distinction at lines 729–732. Model names are included because they determine population scope.

In tuple rows, values and registry IDs correspond in the listed order. **NO ROW** for a definition or illustrative count does not mean fabricated measurement evidence.

Artifact abbreviations:

- **C:** `/Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/instrument_evidence.json`
- **E:** the same capture’s `events.jsonl`
- **P:** the same capture’s `raw/powermetrics.plist`
- **R4:** `docs/process_traces/2026-08-19-refreeze-execution/r6-issuance/r4-derivation.json`, member `20260722T145535-e941c821`
- **XD:** `docs/paper/round7/excursion-decomposition.json`
- **NR:** `docs/process_traces/2026-08-09-prefill-phase-proof/results.json`
- **ST:** `docs/paper/round7/dg071-dg075-statistics.json` and `.md`
- **WEX:** `docs/paper/figures/worked-examples.json`
- **R03E/R03P:** `/Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/{events.jsonl,power_trace.csv}`
- **R08E/R08P:** corresponding files under `p2015-df-ph-decode-abs-r08`

#### Abstract, population counts, discussion and conclusion

| Numeral / quantity | Section:line | Registry row → cited artifact | Assessment |
|---|---|---|---|
| 59 positive fitted onsets, of 59 | Abstract:25–26; §4:608–611,620,641; §8:923 | DX-012 → XD, onset `count_positive/count` | MATCH: one historical current-method pulse replay |
| 49 negative fitted offsets, of 59 | Abstract:26; §4:609,641; §8:924 | DX-013 → XD, offset `count_negative/count` | MATCH: same capture |
| 59 offset values | §4:609,611,621 | DX-013 → XD, offset `count` | MATCH |
| One historical pulse capture | Abstract:25; §4:572–574,599–600,611,617; §5:799–800; §8:923–925 | DX-001 → XD, named capture | MATCH |
| Qwen2.5-1.5B-Instruct-4bit / 1.5B | Abstract:28; §4:680,684,693,699,751–752,783; §5:801; §8:932–933,937 | DG-140 → NR, model names and per-bundle identity | MATCH |
| Qwen2.5-7B-Instruct-4bit / 7B | Abstract:30; §4:689,693,695,700; §5:802; §8:934–935,938 | DG-139 → NR, model names and per-bundle identity | MATCH |
| 37 failures | Abstract:28; §4:683–685,699,781; §8:933,937 | DG-067 → NR, 1.5B `resolvability.not_resolvable_sample_count` | MATCH |
| 50-member 1.5B denominator | Abstract:28; §4:681,683–684,699,781; §8:933,937 | DG-066/068 → NR, 1.5B `bundle_count` | MATCH: 10 a10 + 40 Window-C bundles |
| 13 passes | Abstract:29; §4:684–685,781; §8:934 | DG-069 → NR, 1.5B `resolvability.identifiable` | MATCH |
| Two overlapping records in the 37 phases | Abstract:29; §4:683,699,784; §8:933,937 | DG-072/076 → NR, 1.5B overlap histogram | MATCH |
| Three overlapping records in the 13 phases | Abstract:30; §4:684,784; §8:934 | DG-073/077 → NR, 1.5B overlap histogram | MATCH |
| Three-record minimum | Abstract:29; §4:669–677,685,699,705,717,744,755,784; §8:934,937 | DG-073 → NR, `minimum_samples`; NR method minimum | MATCH: chosen record-support cutoff, not precision validation |
| 50-member 7B population | Abstract:30; §4:690,700; §8:935,938 | DG-135 → NR, 7B `bundle_count` and custody membership | MATCH |
| All 50 7B phases pass | Abstract:30; §4:690–691; §5:802 (“throughout”); §8:935 | DG-136 → NR, 7B `resolvability.identifiable` | MATCH |
| 33 phases overlap three records | Abstract:31; §4:691–692; §8:935 | DG-137 → NR, 7B overlap histogram `"3"` | MATCH |
| 17 phases overlap four records | Abstract:31; §4:692; §8:935 | DG-138 → NR, 7B overlap histogram `"4"` | MATCH |
| None/zero of 50 7B phases fail | §4:700; §8:938 | DG-135/136 → NR; derive 50−50 | MATCH |
| Three or four overlaps for every 7B phase | §4:700; §8:938 | DG-137/138 → NR | MATCH |
| 10 a10 bundles | §4:681 | DG-141 → NR, exact root and distinct members | MATCH |
| 40 Window-C bundles | §4:682 | DG-142 → NR, exact root and distinct members | MATCH |
| 0.2815 s, 7B median prefill | §4:693 | DG-143 → NR; `0.28151941299438477`, rounded to four decimals | MATCH |
| 0.1365 s, 1.5B median prefill | §4:693 | DG-144 → NR; `0.13650262355804443`, rounded to four decimals | MATCH |
| 120.9 ms median record width | §4:694 | DG-071 → ST, same r03 median rounded to one decimal | MATCH: explicitly a10 example, not a 7B/population-wide median |
| 0.030067931757111657 s pulse-derived limit | §5:825 | DG-027 → R4, `b_fiducial_v3_s` | MATCH: explicitly not an inference-error bound |
| Two-block synthetic fixture | §8:939 | SYN-01 → retained fixture and WEX synthetic blocks | MATCH: synthetic, no hardware claim |
| One machine / computer | Abstract:33; §5:827; §8:940 | No dedicated numerical row; C/NR contain machine bindings | NO ROW for this contextual cardinality |
| Two phase types / first output token | Abstract:13–14 | No diagnostic result row; phase definition | NO ROW: method definition |
| Three counter channels | §5:837–840 | No dedicated numerical row; C/P and A.3.1 specify CPU/GPU/ANE | NO ROW: instrument/method definition |

#### Historical clock table and pulse arithmetic

| Numeral / quantity | Section:line | Registry row → cited artifact | Assessment |
|---|---|---|---|
| 1784757335.502742; 458736.4081875; 458736.408188666; 0.0000010000000000000002 | §4:578 | DG-002/003/004/005 → C, `pre_spawn` fields | MATCH |
| 1784757336.604396; 458737.509839458; 458737.509840291; 0.0000010000000000000002 | §4:579 | DG-006/007/008/009 → C, `first_parse` fields | MATCH |
| 1784757337.0900722; 458737.995513416; 458737.995514666; 0.0000010000000000000002 | §4:580 | DG-010/011/012/013 → C, `sampling_started` fields | MATCH |
| 1784757533.877846; 458934.782846541; 458934.782848041; 0.0000010000000000000002 | §4:581 | DG-014/015/016/017 → C, `sampling_stopped` fields | MATCH |
| 1784757533.8891652; 458934.794166; 458934.7941665; 0.0000010000000000000002 | §4:582 | DG-018/019/020/021 → C, `post_parse` fields | MATCH |
| Five paired clock readings | §4:584 | DG-002–021 → C, five named stamps | MATCH |
| Two reported clock resolutions | §4:584 | DG-022/023 → C, wall and monotonic resolution fields | MATCH |
| \(1.0000000000000002\times10^{-6}\) s wall resolution | §4:584 | DG-022 → C | MATCH |
| \(4.166666666666666\times10^{-8}\) s monotonic resolution | §4:584 | DG-023 → C | MATCH |
| 1970 epoch origin | §4:574,584,588 | No dedicated row; Unix-epoch convention for cited stamps | NO ROW: coordinate convention |
| Three warm-up pulses | §4:574 | No dedicated DG/DX value row; E and A.3.2/A.3.4 specify them | NO ROW: supported protocol count |
| 59 detected pulses | §4:588 | DG-024 → R4, replay P+E | MATCH |
| 122,859 evaluated rectangles | §4:588 | DG-025 → R4, `projection_evaluated_cell_count` | MATCH |
| 0.0011349971959968978 s local anchor; repeated subtraction operand | §4:588 | DG-026/029 → R4, `anchor_v3.effective_clock_anchor_bound_s` | MATCH |
| 0.030067931757111657 s capture bound; repeated subtraction operand | §4:588 | DG-027/028 → R4, `b_fiducial_v3_s` | MATCH |
| 0.0289329345611147592 s subtraction result | §4:588 | DG-030 → exact decimal subtraction of R4 printed operands | **MISMATCH in wording:** arithmetic matches; “largest pulse residual” does not match the row’s subtraction scope. F7 |
| Tenth commanded pulse / index 9 | §4:588,626,643 | DG-031 → maximal pulse from P+E+C replay | MATCH: ordinal and zero-based index agree |
| 26.625 s planned on-offset | §4:588 | DG-032 → E, tenth on-event planned offset | MATCH: schedule coordinate, not observed onset |
| 27.625 s planned off-offset | §4:588 | DG-033 → E, tenth off-event planned offset | MATCH |
| 1784757381.2856488 s on-command stamp | §4:588 | DG-034 → E, tenth on-event stamp | MATCH |
| 1784757382.293089 s off-command stamp | §4:588 | DG-035 → E, tenth off-event stamp | MATCH |
| 0.02544938965763524 s onset lower endpoint | §4:588 | DG-036 → current-method P+E+C replay | MATCH |
| 0.02893293456111476 s onset upper endpoint | §4:588 | DG-037 → current-method P+E+C replay | MATCH |
| −0.008607394549133255 s offset lower endpoint | §4:588 | DG-038 → current-method P+E+C replay | MATCH |
| −0.005308621075866744 s offset upper endpoint | §4:588 | DG-039 → current-method P+E+C replay | MATCH |
| +0.027 s best-fit onset | §4:588 | DG-040 → current-method replay, three-decimal rendering | MATCH |
| −0.007 s best-fit offset | §4:588 | DG-041 → current-method replay, three-decimal rendering | MATCH |
| 0.02893293456111476 s retained residual maximum | §4:588 | DG-042 → max absolute DG-036–039 endpoint | MATCH |
| July 2026 | §4:599 | DX-001 → XD capture identity; DG-002 → C epoch | MATCH: historical capture date |
| Eight positive offsets; two zero offsets | §4:609–610,642 | DX-001 plus registry:829–831 explicit binding → XD offset `count_positive/count_zero` | MATCH: 49+8+2=59 |
| 118 fitted edges | §4:611 | DX-001/012/013 → XD; 59+59 | MATCH: dependent edges, not 118 captures |
| +13.0 ms onset median | §4:610,623 | DX-010 → XD onset median | MATCH |
| −5.5 ms offset median | §4:611,623 | DX-011 → XD offset median | MATCH |
| Pulse indices 0–58 | §4:618 | DX-001/003 → XD `per_pulse`, registered SVG | MATCH |
| Zero commanded-lag line | §4:621–622 | DX-003 → SVG, bound to XD | MATCH: defined reference coordinate |
| +27 ms best-fit onset at index 9 | §4:626 | DG-040/031 → replay; DX-001/003 → XD/SVG | MATCH |
| 28.93293456111476 ms endpoint displacement | §4:629 | DG-037/042 → replay, seconds-to-ms conversion | MATCH |
| 1.1349971959968978 ms anchor allowance | §4:630 | DG-026 → R4, seconds-to-ms conversion | MATCH |
| 30.067931757111657 ms capture bound | §4:631 | DG-027 → R4, seconds-to-ms conversion | MATCH |
| 0.5-ms fitted-lag grid | §4:632–633 | No dedicated value row; `FIT_FINE_STEP_S=0.0005` in the pinned pulse-fit implementation | NO ROW: supported algorithm constant |

#### Record-width statistics and concrete geometry

| Numeral / quantity | Section:line | Registry row → cited artifact | Assessment |
|---|---|---|---|
| 0.121034145 s r03 prefill duration | §4:723 | DG-070 → NR r03 boundary; R03E | MATCH: nine-decimal binary64 duration rendering |
| 0.121 s rounded duration | §4:723,741 | DG-074 → NR r03 duration, three-decimal rendering | MATCH |
| 406 sampling records | §4:724 | DG-071 → ST, all retained r03 records | MATCH |
| 120.9186 ms width median | §4:725 | DG-071 → ST | MATCH |
| 5.9508 ms width IQR | §4:727 | DG-071 → ST | MATCH |
| \(n-1\), zero-based quantile positions; p=0.25 and 0.75 | §4:728–729 | DG-071/075 → cited ST Markdown method | MATCH: exact-decimal type-7 calculation |
| Four decimal places, ties to even | §4:729 | DG-071/075 → ST rendering rule | MATCH |
| 405 consecutive unique-timestamp differences | §4:730–731 | DG-075 → ST | MATCH |
| 120.9224 ms spacing median | §4:732 | DG-075 → ST | MATCH |
| 5.8949 ms spacing IQR | §4:732 | DG-075 → ST | MATCH |
| 0.000001 s endpoint-continuity tolerance | §4:735 | DG-071/075 → cited ST Markdown method | MATCH: acceptance tolerance, not measured gap |
| 100 of 405 nonzero boundaries | §4:736–737 | DG-071/075 → ST header and tiling method | MATCH |
| 0.0000004 s largest gap | §4:737 | DG-071/075 → ST | MATCH: absolute endpoint discrepancy |
| One whole middle record; two boundary records | §4:670–672,744–749 | No separate numeric row; geometric explanation of DG-073 cutoff | NO ROW: geometric/design statement |
| Two/three records in the illustrative Figure 3 rows | §4:712–718 | No dedicated numerical result row for these schematic counts | NO ROW: explicitly illustrative, no measured durations |
| One retained example run | §4:721 | DG-070/071 → named r03 member and ST | MATCH |
| 1784978933 s origin; phase [0.267684, 0.3887181] | §4:753 | DG-131 → R03E/R03P, NR, WEX geometry[0] | MATCH |
| Records [0.1945653, 0.3210495] and [0.3210495, 0.434475] | §4:754 | DG-131 → R03P/WEX | MATCH |
| Overlaps 0.0533655 and 0.0676686 s | §4:755 | DG-131 → Decimal overlap calculation | MATCH |
| Zero overlap in adjacent r03 records | §4:756 | DG-131 → WEX geometry[0] | MATCH |
| Three-overlap r08 example | §4:757 | DG-132 → NR/WEX geometry[1] | MATCH |
| 1784981672 s origin; phase [0.671041, 0.807431] | §4:757–758 | DG-132 → R08E/R08P, NR, WEX | MATCH |
| Zero-based record indexing | §4:761 | DG-131/132 → WEX record indices | MATCH |
| r03: 364; 0.0726435; 0.1945655; 0 | §4:763 | DG-131 → R03P/WEX | MATCH |
| r03: 365; 0.1945653; 0.3210495; 0.0533655 | §4:764 | DG-131 → R03P/WEX | MATCH |
| r03: 366; 0.3210495; 0.434475; 0.0676686 | §4:765 | DG-131 → R03P/WEX | MATCH |
| r03: 367; 0.434475; 0.5463145; 0 | §4:766 | DG-131 → R03P/WEX | MATCH |
| r08: 360; 0.4395304; 0.5621388; 0 | §4:767 | DG-132 → R08P/WEX | MATCH |
| r08: 361; 0.5621388; 0.6849675; 0.0139265 | §4:768 | DG-132 → R08P/WEX | MATCH |
| r08: 362; 0.6849675; 0.799845; 0.1148775 | §4:769 | DG-132 → R08P/WEX | MATCH |
| r08: 363; 0.799845; 0.9133315; 0.007586 | §4:770 | DG-132 → R08P/WEX | MATCH |
| r08: 364; 0.9133313; 1.0261726; 0 | §4:771 | DG-132 → R08P/WEX | MATCH |
| Each bundle occurs once | §4:788 | DG-135/141/142 → NR member identities | MATCH: independently recounted 50 distinct members per population |

The NR per-bundle recount reproduced `{2:37, 3:13}` for 1.5B and `{3:33, 4:17}` for 7B, together with the registered medians and 10/40 membership split. XD, NR and WEX hashes matched their registry pins.

Across abstract ↔ §4 ↔ §5 ↔ §8, the counts, phase descriptions and record-support verdicts agree. `identifiable` is the artifact’s pass label; §4 expressly limits its meaning to the chosen record-support criterion. It does not conflict numerically with “passed” or “resolvable.” The substantive cross-section discrepancies are F4 and F7, with the notation issue in F10.

## Residual risk

- The 90 orientation tests passed, including retained-corpus replay. They establish their pinned comparisons, not physical pulse-to-inference transfer, gain accuracy or statistical coverage.
- The population inspection independently recounted the issued per-bundle records; it did not rerun the entire original 100-bundle raw-to-CSV audit.
- The floating-point witness in F3 establishes a limitation of the unconditional numerical claim, not a demonstrated error in the published historical enclosure.
- Bibliography review was limited to internal citation consistency, as requested. No source-of-record verification or new experiment was performed.

No files changed. The next step is lead adjudication of F1–F10 and persistence of this report at the runner’s external path.