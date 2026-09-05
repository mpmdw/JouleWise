```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"Selected A overstates physical attribution, misstates current computations/workloads, and cannot be filled by collection alone.","workspace":{"base_requested":"cc56a9a7","base_mode":"exact","head_start":"cc56a9a76c4d43f8dcf7fb9f4a6d424ae1dd9136","head_end":"cc56a9a76c4d43f8dcf7fb9f4a6d424ae1dd9136","upstream_end":"cc56a9a76c4d43f8dcf7fb9f4a6d424ae1dd9136","branch":null},"pathspec":["docs/process_traces/2026-09-04-peer-audit/03-paper-vs-code.md"],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"blocker"},{"id":"F2","severity":"blocker"},{"id":"F3","severity":"blocker"},{"id":"F4","severity":"blocker"},{"id":"F5","severity":"blocker"},{"id":"F6","severity":"should_fix"},{"id":"F7","severity":"should_fix"},{"id":"F8","severity":"should_fix"},{"id":"F9","severity":"should_fix"},{"id":"F10","severity":"should_fix"}]},"verification":[{"id":"V1","kind":"smoke","cmd":"python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output /private/tmp/jw-peer-audit-03-selected-A.md --outcome A","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["selected A: transfer_slots=3, failed_component_slots=0, verdict_slots=4, refusal_reason_slots=1, abstract_words=200"]},"expected":{"exit_code":0,"tail_regex":"selected A:.*abstract_words=200"}},{"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 10 tests in 1.720s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V3","kind":"inspection","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_paper_round7_artifacts.py --literals-only","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["R7F PLACED 0/16","R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"}},{"id":"V4","kind":"inspection","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nfrom types import SimpleNamespace\nfrom joulewise.reduce import TracePoint, Window, _integrate, _interpolation_joint_edge_bound_j\nfrom joulewise.analysis_engine.inputs import governed_stochastic_variance\nfrom joulewise.detection_floor import absolute_false_effect_floor\nfrom joulewise.aggregate import student_t_critical_95\ncurve = [TracePoint(t=0.1, power_w=30.0, support_start_s=0.0, support_end_s=0.1)]\nprint('interval_clip_J=%.6f' % _integrate(curve, 0, 0.04))\nprint('interval_interpolation_bound_J=%.6f' % _interpolation_joint_edge_bound_j(curve, Window(0, 0.04)))\nprint('phase_stochastic_terms=%r' % (governed_stochastic_variance(SimpleNamespace(summary={}), {'name':'phase_energy_j','phase':'decode'}),))\nfloor = absolute_false_effect_floor([8,9,10,11,12], admissible_half_widths_j=[0]*5)\nprint('t_df4=%.6f floor_example_J=%.6f' % (student_t_critical_95(4), floor.unguarded_floor_j))\nprint('same_30W_interval_actual_prefill_J=0.000000_or_3.000000')\nPY","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["interval_clip_J=1.200000","interval_interpolation_bound_J=0.000000","phase_stochastic_terms=((), ())","t_df4=2.776000 floor_example_J=4.808173","same_30W_interval_actual_prefill_J=0.000000_or_3.000000"]},"expected":{"exit_code":0,"tail_regex":"t_df4=2.776000 floor_example_J=4.808173"}}],"flags":[{"id":"L1","kind":"verification_gap","level":"nonblocking","text":"No raw-corpus or hardware replay. V3 checks retained artifacts only; V4 is constructed arithmetic.","needs":"Lead must separately verify any evidence promoted into the submitted paper."},{"id":"L2","kind":"residual_risk","level":"nonblocking","text":"Submission forecasts are conditional. Paper/code repairs were not authorized writes.","needs":"Choose the paper's supported claim boundary before spending the remaining week."}]}
```

## Findings

Audit of detached `cc56a9a7`, 2026-09-04. **P** = `docs/paper/draft-v2-skeleton.md`; **R** = `docs/paper/results-fill-registry.md`. **FG** = `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py`; **CG** = `configs/campaigns/d117_contrast_v5/generate_configs.py`. Citations use original file lines. Rank: defensibility, then cost (excluding quiet-window retries). Evidence and advice are separated.

V1 produced and I read the selected-A copy, `/private/tmp/jw-peer-audit-03-selected-A.md`, SHA-256 `6a9059048bbdeda0c3606896c6f9d9ea64af6d8884770509eaad5f7756021892`. Selection only changes three branch groups (`select_outcome_branches.py:11,147-169`); it does not authenticate results. Section 4 alternatives and the author ledger survive. References/Availability are empty (P:1368-1379,1403-1406).

### F1 — The bound is on assigned counter energy, not physical phase-energy error (blocker; narrowing: half a day)

**Wrong.** “JouleWise makes a false phase-energy difference measurable before using that limit to judge a model comparison” (P:1387) overstates the measurand. The calculation integrates interval-average power held constant (`joulewise/reduce.py:167-180`). Moving its edge bounds the *assignment's* sensitivity; it does not identify physical power within a record, even with exact timestamps.

Use the paper's 100-ms, 30-W record and 40-ms boundary (P:470-477). A physical trace at 75 W for the first 40 ms and zero afterward assigns 3 J to prefill; zero then 50 W for the final 60 ms assigns 0 J. Both yield the same 30-W record average and exact edge. Code assigns 1.2 J to both (V4). A stipulated ±10-ms edge sweep gives 0.9–1.5 J, covering neither physical extreme. This analytic example limits physical interpretation, not conditional arithmetic.

Similarly, the pulse enclosure covers a chosen loss region, `Loss* + max(1, .05 Loss*)` (`joulewise/powermetrics_fiducial.py:854-869`; P:1632-1639), not a statistically validated inference-edge confidence region. P:1666 correctly says the capture maximum is not an out-of-sample guarantee; that qualification must travel with the headline.

**Different choice / rewrite.** Replace the quoted sentence with: “JouleWise measures how phase-energy assignments from macOS interval-average power records change under a specified set of timing perturbations.” Add: “These bounds depend on the within-record power model and on transferring pulse-derived timing allowances to inference; they do not establish absolute physical phase-energy accuracy.” Prefer title: “JouleWise: Timing Sensitivity of Phase-Energy Assignments on Apple Silicon.”

A JouleSort-informed reviewer will ask which boundary the joule denotes and what validates it. P:1192-1207 admits no external gain check. The proposed counter/wall-meter ratio (P:1332-1338) combines counter gain with different component boundaries and conversion losses. Replace “This tests whole-request gain” with “This tests the relationship between reported processor energy and whole-machine input energy under the specified loads.” Do not add a meter project this week.

### F2 — The headline depends on an unperformed transfer check with conflicting rules (blocker; narrowing: 1–2 hours)

**Wrong.** Exact selected-A sentence: “A later check placed about 500 ms of no work between the two request parts; it [FILL:TR-01].” (P:29.) Yet P:1298-1301 says it has not run and “It is a proposed design, not yet a runnable protocol: its sleep actuation, command-stamp method, and fitted-edge selection remain to be fixed.” R:920 names no issued schema field or result token.

P:873 makes physical dominance conditional on transfer; P:1178-1180 says an exceedance withdraws transfer; P:1324-1326 says there is **no acceptance threshold** and the paper will not label pass/failure. R:920 compares against the session's bound, while P:1321-1323 uses the historical 0.030067931757111657-s capture. These procedures conflict.

“Apply the detector that Section 2 defines for commanded pulse edges, without modification” (P:1313-1315) is not executable as stated: it fits positive, roughly one-second rectangular pulses with interior-plateau and signal checks (P:1598-1604); the proposed object is a half-second negative gap inside variable inference. Sign treatment, baseline, eligible edges and refusals still need definition.

**Different choice / rewrite.** Replace the abstract sentence with “Transfer of the pulse-derived timing allowance to inference was not tested.” Replace the headline implication at P:1145 with “The twelve ratios describe sensitivity under the specified timing model; physical interpretation remains conditional on unperformed inference-boundary validation.” Remove mandatory TR-01 result dependency. If funded, transfer first needs a runnable protocol and contemporaneous acceptance predicate. An unperformed check is not an observed Refusal.

### F3 — Floor and contrast workloads differ, and null blocks are misidentified (blocker; disclosure: hours; validation: uncertain)

**Wrong.** P:136-140 counts components using “the repeated measurements of one model and the four-run comparison of two models.” Floor packs actually declare `same_condition_repeat_and_null_abba_alias` and `A_equals_B` (FG:795-822). These estimate false effects with one model on both sides. Separate two-model blocks supply the demonstration.

The floor uses only `prompt_index = 0`, `prompt_count: 1` (FG:1030-1034). The contrast cycles through eight prompts (CG:1380-1381,1541-1545). Ten blocks therefore weight prompts 1 and 2 twice as heavily as prompts 3–8. P:152-163 supplies an eight-prompt hash but neither assignment. P:712-713 promises a floor for “exactly the phase, workload, model, hardware, software, and power-measurement boundary being tested.” A shared profile name does not validate transfer of the first prompt's timing/energy floor to seven other waveforms. Intentional grouping does not prove conservatism.

**Different choice / rewrites.** Replace the component explanation with “For each model and phase, we derive one bound from repeated runs and one from identical-condition A/B/B/A blocks; separately collected two-model blocks supply the demonstration contrast.” Add after P:163: “Floor calibration uses the first prompt. Ten demonstration blocks cycle through eight prompts, repeating the first two; their mean weights those prompts twice.” Add: “Applying the first-prompt floor to other prompts is an unvalidated workload-transfer assumption.”

Prefer one identical prompt for floor/demonstration, with plans regenerated before collection. Otherwise establish per-prompt floor applicability; do not discard blocks retrospectively.

### F4 — The printed methods do not match the current phase path (blocker; half a day)

**Wrong: interpolation.** “The calculation assigns power there from the straight line joining those samples, moves the start and end through their allowed neighboring-sample gaps, and retains the largest resulting energy change.” (P:840-843.) Native interval traces integrate rectangles and return zero interpolation bounds (`joulewise/reduce.py:167-180,515-520,541-555`; V4). This sentence describes the point-sample fallback. Replace it with “For native interval-average records, the reducer integrates constant reported power over the overlap duration; its interpolation-bound term is zero. Timing uncertainty enters through separately recomputed boundary envelopes.”

**Wrong: stochastic terms.** P:771-786 sums variances over gross request, idle-subtracted request, gross prefill and gross decode “energy terms.” Actual dispatch is for one requested metric: `governed_stochastic_variance` returns no terms except for `energy_request_j`; its nonempty term is `E_idle_mean_j2` (`joulewise/analysis_engine/inputs.py:3668-3715`). The ABBA builder divides summed member variances by four and assumes `independent_run` with `covariance_ab=None` (`joulewise/analysis_engine/__init__.py:611-627`). It does not combine four energy observables into a phase contrast. V4 confirms `phase_stochastic_terms=((), ())` in this dispatch.

Replace P:771-780 with: “For the gross phase-energy contrasts used here, the current builder supplies no additional stochastic metrology variance, so the stochastic standard error is the standard error of the block differences. Timing and other deterministic allowances are propagated separately.” P:803's stipulated 0.2-J metrology standard error is valid synthetic arithmetic, but not this production phase path.

**Wrong: numerical convention.** P:547-549 uses `t_.975,4=2.776445`, obtaining 4.808944 J. Code's table uses 2.776 (`joulewise/aggregate.py:41-50`), obtaining **4.808173 J** (V4). P:686 correctly uses a rounded lookup for another example. Generate examples from the declared code convention.

### F5 — Successful collection alone cannot fill selected A (blocker; minimal output work: 1–2 days)

**Wrong.** Selected A requires DS-32 and PG-08 (P:29,1145,1387); R:885,894 says their display tokens are missing. The renderer still uses `1p5B`/`7B` (`scripts/render_results_fills.py:759,967-970`). Both published decode floors lead deliberately to `_supplier_unknown("[B_decode_claim_J]")` (972-978); one passing window leads to a missing mean (979-988). R:964-967 acknowledges the v5 vocabulary gap. New data will not fix it.

P:985's exact sentence is “The decode sizing sum and signed clearance are omitted: the claim-side bound and one-cell/two-quantity rendering are unresolved (registry row DS-28).” But P:856-861 defines plain clearance as `abs(estimate)-floor`, and R:378-379 supplies it. The undefined claim-side-bound column is already removed (P:988-993). Do not keep this useful quantity blocked by an abandoned sizing sum.

**Different choice.** Render authenticated v5 estimates, intervals, armwise floors, gates and reasons for both phases and all twelve ratios. Remove undefined means/sums; preserve authentication.

**Supplier audit and one-week forecast.** Schema, issuer and collected value are distinct. This forecast is conditional, not knowledge of future outcomes.

| Rows / claims | Existing supplier and evidence | Submission forecast / action |
|---|---|---|
| V5-ID-001/002, V5-WL-001–004 | Panel/generators, R:144-149 | Design inputs available now. Print four-bit format, prompt assignment, EOS suppression and versions, not only hashes. |
| V5-G2A-001, V5-WL-005, `[PREFILL_LENGTH]` | `scripts/select_g2a_prefill_length.py:98-110` emits `collection_prefill_tokens`; `scripts/issue_g2a_prefill_prompt_pin.py` exists | Needs probes and issued selection/pin (R:150-151). Plausibly fillable early; no rung can be guessed. P:1110's “tested” is premature. |
| DS-11/15/19/23, eight R, four comparative R_cm, four absolute N/A placements | `joulewise/detection_floor.py:919-972`; `joulewise/dominance_closeout.py:445-565,585-709`; R:167-263 | Algorithms built, live values unissued. Two floor windows and close-out are critical path. N/A is a defined disposition, not a measured ratio. |
| DS-25/26/27; clearance part of DS-28 | Estimate/decision interval/armwise maximum fields at R:372-380; current analysis code | Numerics built. Need production contrast plus v5 rendering. Plain clearance does not require an extra claim-side bound. |
| DS-30/31/32, DS-33, PG-01/02/04/06/07/08 | Generic contrast engine exists; exact display bindings absent (R:883-894,930) | **Stay STOP_FILL without explicit rendering work, even if collection succeeds.** Likely repairable as a small task tomorrow. |
| DS-09/10/12,13/14/16,17/18/20,21/22/24 | Twenty underlying mean/interval/per-token/count tokens have no D-123 basis/schema (R:340-359,862-877,931) | **Plan to cut.** Measurements cannot define the population, interval or denominator. Floor counts are not mean-basis counts. |
| DS-29, PG-05; bound-dependent sums; worst-case counterpart token | Explicitly absent at R:377,381,398,882,891 | **Cut.** Do not rename `deterministic_bounds.total` to invent the missing registered quantity. |
| DS-02/03/05/06; all characterization numeric/outcome families | Specification fields exist (R:400-464). No issuer for `rows.linearity`/`request_slope_j_per_token` found in `joulewise/` or `scripts/`; renderer:917-942 stops | **Expected empty in current campaign.** P:260-264,366-369 says it will not issue them and lacks varied-output data. Two limit derivations remain proposed (R:443,449). |
| TR-01 | Named task, no schema/token (R:920); not runnable (P:1298-1301) | **Expected empty unless it displaces other work.** Narrow the headline, F2. |
| OB-01 / OR-01 | Close-out/window/claim records named, list/reason rendering absent (R:919,921) | Conditional branches, not ordinary A numeric slots. Build failure rendering too; never invent a stop reason at the desk. |
| DS-34 | No issued repository/archive/digest locator set (R:887); independent rebuild open (P:1272-1281,1412) | **Empty until release work occurs.** A download link and independent re-reduction are separate achievements. |
| DG-002–043,102–128: clock/pulse/corpus arithmetic | Retained R4/S17, paths R:553-568; bindings R:577-617,699-725 | Registered historical suppliers. Raw replay unavailable here; appendix occurrences are not all replay-fenced. Keep historical standing and declared rounding. |
| DG-044–066,099–101: old floors/ratios/counts | Historical A10/NR suppliers, R:558-564,619-641 | Registered historical values, not new v5 floors. Remove repeated old ratios if they distract from the actual result. |
| DG-067–075: 37/50,13/50, duration/support/width/spacing | `docs/process_traces/2026-08-09-prefill-phase-proof/results.json`; `docs/paper/round7/dg071-dg075-statistics.json`; R:642-650 | Existing descriptive evidence. It supports a narrow historical statement, despite the paper saying no claim rests on it. |
| DX-001–027: excursion and anchor correction | Retained JSON/scripts/Figure 4, R:738-785; V3:181 comparisons, zero mismatches | Available diagnostic material. **Zero of sixteen registered result placements appears in the draft.** |
| New worked examples, design thresholds | Section 4 formulas, fixed source constants and `tests/fixtures/fcm_r4_real_blocks/measured_pair.json` (P:699) | Label synthetic/design rather than measured. Not all new examples have individual DG rows; V4 proves one printed example disagrees with current code. |

Cut unbuilt means, transfer claims and unused characterization; implement required v5 outputs. Live ratio outcomes remain unknown.

### F6 — Characterization describes validation this campaign will not perform (should_fix; cut: hours)

**Wrong.** “Instrument characterization asks four physical questions before any campaign result may rely on the instrument.” (P:248-249.) But P:260-262 says it will not apply three calculations or issue reports; the fourth has no varied-output inputs. P:416-424 repeats four omissions. The opening states an unmet validation prerequisite.

P:367 describes five null test blocks, optionally five comparator-building blocks, and 512-token prefill. The current generator schedules ten null blocks and ten repeats per phase (FG:66,1339-1428); selected prefill remains G2-a-dependent (R:150). This unused characterization design is not the production floor design. Floor-building nulls cannot independently validate the floor derived from themselves (P:265-267).

**Different choice / rewrite.** Replace the opening with “This study characterizes pulse-edge timing and record support; it does not independently validate floor coverage, workload linearity, phase invariance, or drift containment.” Cut P:269-414's unused ladder/40-energy exposition and P:416-424's omission sentences from the main article. Keep the actual calibration-null calculation, observed n and limits of its evidence. Retiring the empirical small-difference challenge (R:829-833) does not establish detection probability. Call the floor an operational screening threshold; do not build the entire characterization system this week.

### F7 — Ratio, coverage and drift language exceeds the stated models (should_fix; half a day)

**Wrong: interpretation.** “In plain terms, both ratios ask whether uncertainty about where a phase starts or ends is at least as large as the ordinary variation already present in the repeated measurements.” (P:130-132.) Ratios of worst-case bounds quantify possible enlargement, not actual error magnitude/frequency. Replace with “Both ratios measure enlargement under specified perturbation sets; they do not estimate how often or how strongly those errors occur.” Retain the predeclared twofold rule as an operational criterion.

**Wrong: common mode.** “the absolute formula first subtracts the cell mean, so a uniform shared shift cancels from every residual.” (P:681-682.) Uniform **joule** offsets cancel; common **time** shifts need not. Moving an edge 10 ms on 20-W and 40-W records changes energies by 0.2 and 0.4 J, leaving unequal residual changes. N/A is a replay choice, not a physical proof. Replace with “A uniform additive energy offset cancels from absolute residuals. This analysis does not implement an absolute common-time-shift replay.”

Comparative code applies `delta + shared_sign * shared_width + local_sign * local_width` (`joulewise/dominance_closeout.py:278-333,683-700`). The magnitude comes from per-block extrema, symmetrized and widened. Sharing that **energy-envelope sign** across blocks is not globally re-integrating one physical time shift: extrema can occur at different shifts, and time sensitivities can have opposing signs. Replace P:29's “when the same timing error moved together across each group of four comparison runs” with “under a second calculation retaining a shared sign for block-level energy allowances.” Claim physical common-time robustness only after actually replaying that physical perturbation.

**Wrong: error guarantee.** Holm “keeps the chance of any false direction claim across the pair at 0.05” (P:764-767) requires valid p-values. P:1209-1216 admits unquantified dependence; adding variance does not automatically justify nine t degrees of freedom. P:527-528's “two-sided 95% prediction amount for one further observation” likewise needs independent normal observations. Rewrite: “We apply Holm at nominal family-wise level 0.05 to two model-based tests; error control depends on their distributional and dependence assumptions.” Apply sensitivity to collected blocks, not only the synthetic fixture.

**Wrong: time balance.** “The order gives the two A runs and the two B runs the same average position in time, which cancels steady linear drift” (P:498-501) assumes equal elapsed-time midpoint sums. P:940 correctly says runtimes/cooldowns can break equality. Move that qualification to first mention, including P:206-207. Reference excursion (P:729-741) is an empirical allowance, not a deterministic bound on arbitrary unobserved excursions between references.

### F8 — Text-alone reproduction is overstated (should_fix; supplement: one day)

**Wrong.** P:1433 says the appendix is precise enough to rebuild “from this text alone” and “Everything below is stated as the code executes it.” Additional gaps:

| Mechanism | Gap and smallest repair |
|---|---|
| Clock feasible set | Equations are unusually explicit (P:1485-1571), but input-refusal checks and diagnostic search are exported (P:1496,1546). Distinguish reproducing the bound from byte-identical diagnostics/refusal. |
| Pulse schedule | P:187 says “gaps stepping through powers of two.” Actual P:1478 schedule is `1.5 + van_der_Corput_base2(k)`: 2.0,1.75,2.25… seconds. Replace the phrase with “a fixed base-two van der Corput schedule varies the gaps.” |
| Pulse point fit | “The repository artifact guide states the tie-break rule.” (P:1627.) Include first-minimum in grid order (`joulewise/powermetrics_fiducial.py:812-826`). |
| Accepted-region termination | P:1670 exports work constants. State 165,000 rectangles/capture and 120 s, plus refusal on either limit (`joulewise/powermetrics_fiducial.py:88-92`). Time-budget refusal depends on execution speed. |
| Floor corners | P:555-563 suggests raw lower/upper member energies. Code enumerates symmetric `point ± half_width` boxes (`joulewise/detection_floor.py:895-915`). Define symmetrization and reduction of four members into one block interval before enumeration; n counts blocks for comparative floors. |
| Shared/local replay | “remaining local clock and edge uncertainty” (P:653) has no complete input construction. P:627-649 omits additional outward rounding of width/final sum (`joulewise/dominance_closeout.py:327-331`). Supply the local-width rule and rounding if exact replay is promised. |
| Claim gates | State actual per-metric uncertainty terms (F4), interval confidence level, expected positive B−A direction (CG:2464-2466), and **max of both models' floors** (R:375-376), not a mysterious single `F_cell`. |
| Fresh workload | P:149-165's hashes omit prompt assignment (F3), actual four-bit model format, EOS suppression and software versions. R:10-14 and CG:1535-1545 contain relevant inputs. Print a configuration table and release the prompt file. |
| Transfer/characterization | Actuation, eligible populations or issuance are incomplete (F2/F6). Label as proposed, not executable empirical protocol. |

**Different choice / rewrite.** Replace P:1433's first sentence with “This appendix specifies the scientific models; the versioned implementation and released inputs supply the complete executable protocol.” Release the inputs and one replay command. If text-alone reproduction remains required, include omitted rules and have an independent reader implement a small example from the appendix.

### F9 — The first-use pass is not a sentence-level audit (should_fix; edit while cutting: half a day)

**Wrong.** P:1725 allows a gloss in the same **paragraph**; the test enforces paragraph/table-row scope (`tests/test_paper_first_use_ledger.py:49-51`). V2 passes, but P:2006's “Terms inventoried: 268; FAILS: 0” does not establish sentence-unit readability. P:1726's vocabulary exemptions are editorial choices.

Sentence-level late/unbuilt inventory follows. Quotes are exact fragments of the cited sentence; the remedy identifies missing or later meaning. Same-sentence glosses count. SI, algebra and advisor-level statistics are assumed. Remove the author ledger, which cannot retroactively define the article.

| Late word(s) | First offending sentence anchor | Later arrival / cure |
|---|---|---|
| output tokens | “generating output tokens” (P:29) | Never defines token as a small text unit; do so in this sentence. |
| required calculation / false difference / limit | “then recalculated the largest false difference after every allowed movement” (P:29) | Absolute spread versus null comparison arrives P:100-109, and is confused by F3. Name the two null quantities or narrow the abstract. |
| runtime | “The runtime-recorded time between those parts is the phase edge.” (P:55-56) | Define software executing the model. |
| unified memory | “128 GB of unified memory” (P:68-69) | Capacity is not a definition. Say CPU/GPU share it; put details in configuration table. |
| software stack | “another machine, software stack, workload, or power sampler” (P:70-72) | Say operating system and model-execution software; name versions. |
| GPU | “command timestamps for GPU pulses” (P:74-76) | Expansion is next sentence. Expand graphics processing unit here. |
| wall clock | “the computer's wall clock and its monotonic clock” (P:87-90) | Monotonic is glossed; wall clock's epoch meaning arrives P:225. Add calendar-time clock. |
| lower-or-upper edge choice | “every lower-or-upper edge position allowed” (P:111-113) | Continuous admissible positions have not yet become corner extrema. Point explicitly to Section 4's endpoint calculation. |
| tokenizer / tokenizer.json | “Both conditions use the same `tokenizer.json` SHA-256” (P:155-160) | No tokenizer gloss. Say text-to-token mapping. |
| chain-of-thought output | “Qwen3's optional chain-of-thought output is switched off” (P:160) | Jargon explains jargon. Say optional intermediate reasoning text. |
| CPU / neural-engine | “CPU, GPU, and neural-engine average power” (P:177) | Expand CPU and explain the dedicated neural-network accelerator; these channels define the measurand. |
| calibration ledger / pins / genesis test fixture | “pins in the calibration ledger's session record”; “retained genesis test fixture” (P:187) | Internal names lack scientific referents. Delete these sentences or say fingerprinted calibration-input record; fixture means fixed example input. |
| frozen | “the frozen reservation plan” (P:187) | “Fixed and fingerprinted before collection” comes two sentences later. Move it up or remove the paragraph. |
| warm-up pulses | “After three warm-up pulses, which are discarded” (P:187) | Purpose arrives P:1579. Add that they bring GPU to operating state. |
| onset / offset | “moving the onset and offset separately” (P:189) | Start/stop inferable, but commanded versus fitted distinction comes later. Use fitted start/stop times here. |
| native power records | “whole-second label embedded in the native power records” (P:191) | Original sampler output/format arrives P:1439. Add original, unparsed. |
| stage | “a stage must satisfy before its first run is measured” (P:197-198) | Definition P:201 is two sentences later. Move it before entry check. |
| mean idle power | “removes the mean idle power multiplied by run duration” (P:208-209) | Formula exists; idle population and weighting do not. Specify interval/statistic or cut unused metric. |
| residual, now meaning time | “largest pulse residual before the anchor term” (P:239) | Lag defined P:225; residual later means energy too. Name fitted-time-minus-command-time residual here. |
| timing half-width | “the bundle's allowed timing half-width” (P:272-274) | Energy residual is being compared with an ambiguously time-valued width; late gloss P:366. Say energy allowance induced by timing uncertainty, in joules. |
| phase rate / cadence ratio | “fixed multiple of the phase rate” (P:347-349) | Denominator formula never built. Give exact rate statistic and units. |
| clean reference | “one-and-one-tenth times the clean reference” (P:359-361) | Previously reference energy, now power. Name admitted idle power statistic. |
| nominal thermal pressure | “and nominal thermal pressure” (P:361-362) | Say operating-system status category; it is not calibrated temperature. |
| fixed least-squares weights | “its slope is a fixed weighted sum” (P:375-376) | No weight formula. Supply `(x_i-xbar)/sum(x_j-xbar)^2` if keeping this unused method. |
| guarded calculation | “Under the retired guarded calculation” (P:587-590) | Unguarded is earlier defined, but historical/current operands remain ambiguous. Specify same historical multiplicative guard on both. |
| member-envelope | “The member-envelope integral sum is” (P:629-631) | Formula follows, physical referent missing: union of allowed integration windows. |
| fixture | “A retained two-block fixture makes the replay checkable” (P:684) | Earlier unglossed use P:187. Say fixed example inputs and identify measured-derived versus synthetic standing. |
| Holm step-down correction | “share one two-sided Holm step-down correction” (P:764-767) | Algorithm arrives P:819. Add ordered two-test adjustment and local pointer; qualify F7. |
| gross repetition term | “the gross repetition term is left out” (P:775-776) | No such particular input constructed; production phase path does not supply it. Remove via F4. |
| AR(1) | “its separately estimated AR(1) model” (P:814-815) | Serial correlation gloss present, first-order model/formula absent. P:1238-1242 remains verbal. Name model and equation in sensitivity supplement. |
| processor-state / powered-down ratio | “complete processor-state and power records” (P:932) | Explain reported time fractions and their observation window. |
| telemetry | “Missing or malformed CPU, GPU, or power telemetry” (P:933) | Replace with recorded processor and power measurements. |
| diagnostic only / claim-bearing | “diagnostic only, never claim-bearing” (P:934) | Earlier use also lacks precise scope; P:1078's eventual no-claim gloss contradicts the descriptive result. Say excluded from prospective model comparison. |
| quarantine / occurrence / append-only replacement record | “an occupied retry slot moves to retained quarantine” (P:944) | Say failed attempts retained separately with records linking retries; move filesystem language to guide. |
| tamper-evident | “tamper-evident for the operator's own benefit” (P:948) | Intent is not mechanism. Say hash checks reveal inconsistent file changes. |
| token IDs | “selected prompt text and token IDs” (P:973-974) | Requires missing tokenizer gloss. Say integer identifiers actually supplied to model. |
| quantization | “model revision, or quantization” (P:1418) | Never specifies reduced-precision weights in article. Give actual four-bit format. |
| accepted-region | “pulse-fit (accepted-region) algorithm” (P:1433) | Region idea is earlier, actual loss meaning arrives P:1632. Say edge pairs within declared fit tolerance. |
| fence / mx.eval | “with a fence after each (`mx.eval`)” (P:1478) | Define waiting for queued GPU computation to finish. |
| exactified | “the resulting float is then exactified” (P:1502) | Say converted to the exact rational value of that stored float. |
| baseline classifier | “make the baseline classifier … report them as uncommanded plateaus” (P:1579; ellipsis marks omitted pointer) | Rule arrives P:1594. Say later uncommanded-high-power test. |
| Huber loss | “The objective is the Huber loss of the standardised residuals” (P:1606-1608) | Definition after formula P:1612. Add quadratic near zero, linear for large residuals in naming sentence. |
| 95/95 | “not a ‘95/95’ population-coverage bound” (P:1666) | Decode as 95% of future errors with 95% confidence, or cut shorthand. |

**Different choice.** Shorten instead of adding glossary machinery. Delete “Do not soften, combine, or mechanically retensor these sentences” (P:869), unused outcome forms, and the author ledger (P:1722-2006).

### F10 — Strong empirical material is absent while submission essentials remain empty (should_fix; 1–2 days)

**Wrong.** All four inserted figures are schematics (P:181/183,219/221,894/896,1022/1024). Measured Figure 4 exists and passes mark checks, yet V3 says `R7F PLACED 0/16`. Numbered citations have no reference entries (P:1346-1366,1403-1406); Availability is empty and independent re-reduction expressly unavailable (P:1368-1379,1412). A sound narrow result still needs references and evidence.

“These data are non-claim-bearing, meaning no paper claim rests on them” (P:1078-1079) follows an empirical conclusion about 37/50 phases. Replace with “These historical data support only the descriptive record-support result for this population and do not supply the prospective Qwen3 comparison.” Also fix “none of it supports a claim” (P:239). Diagnostics support scoped observations.

**Different choice: the three figures that must exist.** Move flowcharts to supplement. No synthetic substitutes for missing measurements.

| Figure | Required content and suppliers | Acceptance test |
|---|---|---|
| **1. What is observed, what is assumed?** | Real pulse trace with interval-average rectangles, command stamps, fitted edge regions and residuals; separate clearly illustrative inference-boundary panel showing energy reassignment and within-bin ambiguity. Registered capture at R:553-556 and `round7/excursion-decomposition.json` support it; obtain released raw records for waveform. Separate GPU calibration from summed processor inference. | Each real mark maps to record/field; time units close; caption separates observations, fitted model and illustration. Never depict an instantaneous physical waveform as recovered from averages. |
| **2. What supports the timing allowance?** | Promote `figures/fig4_edge_excursions.svg`: all 59 onset and 59 offset results, regions, zero line and maximum. Distinguish pulse excursion, anchor addition and bracket allowance. Optional anchor-correction inset: 12 derived, 3 refused, one control failure (R:779-784). | V3's 118 mark checks pass; caption says historical current-method re-derivation, one capture, dependent edges, sample maximum, no future coverage guarantee. |
| **3. What result changes the conclusion?** | With production: four-cell point/corner bounds in joules, all twelve ratios against 2; two model contrasts with full decision intervals and ±armwise floor bands. Suppliers R:167-263,372-380 plus minimal v5 bindings. Without production: replace entire panel with historical 37/50 versus 13/50 record support and real two-record example (DG-067–075), and remove Outcome A claims. | Recompute all marks from authenticated inputs; include failures/refusals and prompt weights; distinguish ratio passage from model direction. Fallback makes no prospective dominance/model claim. |

Prefer calibration, conditional timing sensitivity and a limited demonstration or historical record-support paper. Cut unused validation/governance.

## Residual risk

No measurement checkout, night custody, LaunchAgent, hardware or other model session was accessed. The raw-capture path was absent inside this worktree, not necessarily in lead custody. V3 is literals-only. Full pulse replay, floor-authentication validation, external-reference verification and final PDF inspection remain outside coverage. No discovery suite ran; only this report was written.

The five actions I would take first tomorrow morning:

1. **Freeze the supported claim and paper route.** Choose counter-assignment sensitivity unless completed transfer evidence supports more; choose production demonstration or historical fallback. **Acceptance:** title, abstract, results and conclusion agree; no unperformed experiment appears in past tense; physical and assigned joules are distinguished.
2. **Correct the experiment and methods on one page.** Show same-model null versus two-model blocks, prompt weights, armwise floor maximum, interval integration, actual stochastic terms and t lookup. **Acceptance:** a trace through cited code reproduces V4 and the ten-block prompt schedule with no contradictory sentence elsewhere.
3. **Build minimal v5 success/failure rendering.** Bind two contrasts and required ratios; remove undefined means/bounds/sums. **Acceptance:** isolated synthetic all-pass, below-two, missing-contrast and zero-denominator inputs render without placeholders/invention; the same path accepts authenticated measurement outputs. Fixtures stay labelled synthetic.
4. **Assemble the three figures and cut unperformed validation.** Promote existing excursions and choose the result panel actually supported. **Acceptance:** every empirical mark has a supplier/units; no prospective panel is fabricated; unused characterization omissions and author ledger disappear.
5. **Reserve time for collection, release and advisor reading, with a fixed fallback deadline.** Lead controls clean quiet collection, then packages exact evidence and performs fresh-directory re-derivation. **Acceptance:** another reader can locate all citations and reproduce each quantitative result or declared refusal; final paper has no FILL tokens or empty References/Availability and makes no claim beyond completed validation.
