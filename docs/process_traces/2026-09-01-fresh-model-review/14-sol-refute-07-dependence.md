```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REFUTE: four contract blockers permit non-registered intervals, alpha, sample counts, or suppliers to be presented as registered results.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "head_end": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "upstream_end": null,
    "branch": "feat/2026-09-01-dependence"
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/paper/round7/dependence-sensitivity.md",
    "scripts/dependence_sensitivity.py",
    "tests/test_dependence_sensitivity.py"
  ],
  "verdict": {
    "decision": "REFUTE",
    "findings": [
      {"id":"F1","severity":"blocker","file_line":"docs/paper/round7/dependence-sensitivity.md:21","title":"Sampling-only intervals are mislabeled and gated as the registered model"},
      {"id":"F2","severity":"blocker","file_line":"scripts/dependence_sensitivity.py:145","title":"The registered alpha is caller-selectable"},
      {"id":"F3","severity":"blocker","file_line":"scripts/dependence_sensitivity.py:71","title":"Non-ten-block inputs can emit registered gate outcomes"},
      {"id":"F4","severity":"blocker","file_line":"docs/paper/round7/dependence-sensitivity.md:123","title":"The proposed registry consumers belong to fully composed primary results"},
      {"id":"F5","severity":"should_fix","file_line":"docs/paper/round7/dependence-sensitivity.md:66","title":"Holm boundary equality is unspecified"},
      {"id":"F6","severity":"should_fix","file_line":"docs/paper/round7/dependence-sensitivity.md:62","title":"Effective-n halving is not a worst case"},
      {"id":"F7","severity":"should_fix","file_line":"docs/paper/round7/dependence-sensitivity.md:76","title":"The calibration replacement competes with the approved H30 wording"},
      {"id":"F8","severity":"should_fix","file_line":"docs/paper/round7/dependence-sensitivity.md:1","title":"Terms of art fail the first-use pedagogy standard"},
      {"id":"F9","severity":"should_fix","file_line":"tests/test_dependence_sensitivity.py:18","title":"Most fail-closed guards and worked intermediates are mutation-unprotected"}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_dependence_sensitivity",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 6 tests in 0.567s","OK"]},
      "expected":{"exit_code":0,"tail_regex":"Ran 6 tests.*OK"}
    },
    {
      "id":"V2",
      "kind":"other",
      "cmd":"python3 -c 'from joulewise.aggregate import student_t_critical_95; from joulewise.analysis_engine.distributions import student_t_quantile; [print(df, format(student_t_critical_95(df), \".3f\"), format(round(student_t_quantile(0.975, df), 3), \".3f\"), \"MATCH\" if student_t_critical_95(df)==round(student_t_quantile(0.975, df), 3) else \"MISMATCH\") for df in range(1,10)]'",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["1 12.706 12.706 MATCH","9 2.262 2.262 MATCH"]},
      "expected":{"exit_code":0,"tail_regex":"9 2\\.262 2\\.262 MATCH"}
    },
    {
      "id":"V3",
      "kind":"smoke",
      "cmd":"python3 -c 'import subprocess,sys; cases=[\"[1,2,3,4]\",\"[1,2,NaN,4,5]\",\"[1,1,1,1,1]\",\"[-1,1,-1,1,-1,1,-1,1,-1,1]\",\"[0,1,2,3,4]\"]; ps=[subprocess.run([sys.executable,\"scripts/dependence_sensitivity.py\",\"--block-deltas\",x,\"--floor\",\"1\",\"--alpha\",\"0.05\"],capture_output=True,text=True) for x in cases]; print([(p.returncode,p.stdout==\"\") for p in ps]); raise SystemExit(0 if all(p.returncode!=0 and p.stdout==\"\" for p in ps) else 1)'",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["[(2, True), (2, True), (2, True), (2, True), (2, True)]"]},
      "expected":{"exit_code":0,"tail_regex":"\\[\\(2, True\\), \\(2, True\\), \\(2, True\\), \\(2, True\\), \\(2, True\\)\\]"}
    },
    {
      "id":"V4",
      "kind":"other",
      "cmd":"python3 -c 'import math,statistics as st; x=[7.456660508865,5.631869605023,6.945943923885,4.707358851097,5.876049545908,4.075489246075,5.082017947228,3.378380063429,4.019575803654,2.826654504835]; m=st.fmean(x); c=[v-m for v in x]; s=st.stdev(x); r=sum(c[i]*c[i-1] for i in range(1,10))/sum(v*v for v in c[:-1]); q=[(1-k/10)*r**k for k in range(1,10)]; V=1+2*sum(q); print(f\"sum={sum(x):.6f} mean={m:.6f} ss={sum(v*v for v in c):.6f} s={s:.6f} rho={r:.6f} V={V:.6f} neff={10/V:.6f} nu={min(9,math.floor(10/V)-1)}\")'",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["sum=50.000000 mean=5.000000 ss=20.250000 s=1.500000 rho=0.300000 V=1.734695 neff=5.764703 nu=4"]},
      "expected":{"exit_code":0,"tail_regex":"rho=0\\.300000 V=1\\.734695 neff=5\\.764703 nu=4"}
    },
    {
      "id":"V5",
      "kind":"smoke",
      "cmd":"python3 -c 'from scripts.dependence_sensitivity import EXAMPLE_BLOCK_DELTAS_J,analyze_deltas; r=analyze_deltas(EXAMPLE_BLOCK_DELTAS_J,floor_j=3.5,alpha=.10); print(r[\"input\"][\"alpha\"],r[\"models\"][\"independent_blocks\"][\"t_critical\"],r[\"models\"][\"independent_blocks\"][\"interval_j\"])'; python3 -c 'from scripts.dependence_sensitivity import analyze_deltas; r=analyze_deltas([6,5,4,5,5],floor_j=1,alpha=.05); print(r[\"summary\"][\"n_blocks\"],r[\"models\"][\"independent_blocks\"][\"direction_gate\"][\"passes\"])'",
      "cwd":".",
      "observed":{"result":"fail","exit_code":0,"tail":["0.1 1.833 {'lower': 4.130531757336597, 'upper': 5.869468242663202}","5 True"]},
      "expected":{"exit_code":1,"tail_regex":"registered alpha or fixed-n refusal"}
    }
  ],
  "flags": [
    {
      "id":"FL1",
      "kind":"verification_gap",
      "level":"nonblocking",
      "text":"The canonical full suite and live campaign path were not run; this was a focused read-only review and measurement was expressly prohibited.",
      "needs":""
    }
  ]
}
```

## Findings

1. **F1 — BLOCKER — sampling-only intervals are presented as registered direction-gate intervals.**  
   File: [dependence-sensitivity.md:21](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:21), [dependence-sensitivity.md:39](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:39), [dependence-sensitivity.md:64](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:64), [dependence-sensitivity.md:70](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:70), [dependence_sensitivity.py:139](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:139), [dependence_sensitivity.py:242](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:242).

   Registered rule: the estimator combines repeat and stochastic-metrology variance, then widens the metrology-aware interval by every deterministic bound ([estimators.py:465](/Users/edr/code/JouleWise-wt-dependence/joulewise/analysis_engine/estimators.py:465), [estimators.py:470](/Users/edr/code/JouleWise-wt-dependence/joulewise/analysis_engine/estimators.py:470), [estimators.py:483](/Users/edr/code/JouleWise-wt-dependence/joulewise/analysis_engine/estimators.py:483)). Direction support requires both the metrology-aware and decision intervals to avoid zero, plus Holm rejection ([claims.py:362](/Users/edr/code/JouleWise-wt-dependence/joulewise/analysis_engine/claims.py:362), [claims.py:371](/Users/edr/code/JouleWise-wt-dependence/joulewise/analysis_engine/claims.py:371)). The registry likewise names the fully composed interval ([results-fill-registry.md:820](/Users/edr/code/JouleWise-wt-dependence/docs/paper/results-fill-registry.md:820), [results-fill-registry.md:829](/Users/edr/code/JouleWise-wt-dependence/docs/paper/results-fill-registry.md:829)).

   Concrete failure: the worked repeat-only interval is `[3.927039, 6.072961]` and the script prints `direction_gate.passes=true`. With zero stochastic metrology but a registered deterministic total of 4 J, the registered decision interval is `[-0.072961, 10.072961]` and direction fails. Line 72 could nevertheless print “registered … passed.” Its raw p-values are also based on repeat-only SE, whereas the registered raw p uses `SE_total`.

   Minimal fix: ingest the authenticated stochastic-metrology variance and deterministic totals; for each sensitivity model compute `SE_total = hypot(SE_repeat_model, SE_metrology)`, form the metrology-aware and decision intervals, and apply direction to those registered intervals. Otherwise remove every “registered gate,” gate outcome, disagreement sentence, and Holm-use claim from this sampling-only calculator.

2. **F2 — BLOCKER — the fixed registered alpha is caller-selectable.**  
   File: [dependence_sensitivity.py:145](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:145), [dependence_sensitivity.py:192](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:192), [dependence_sensitivity.py:287](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:287).

   Registered rule: `_v5` freezes Holm, \(m=2\), and \(\alpha=0.05\) ([generate_configs.py:1857](/Users/edr/code/JouleWise-wt-dependence/configs/campaigns/d117_contrast_v5/generate_configs.py:1857), [generate_configs.py:2576](/Users/edr/code/JouleWise-wt-dependence/configs/campaigns/d117_contrast_v5/generate_configs.py:2576)); the registered interval uses the 0.975 quantile ([estimators.py:224](/Users/edr/code/JouleWise-wt-dependence/joulewise/analysis_engine/estimators.py:224)).

   Concrete failure: `alpha=.10` succeeds, emits critical `1.833`, interval `[4.130532, 5.869468]`, and a gate result instead of refusing. The registered 0.05 result is critical `2.262`, interval `[3.927039, 6.072961]`.

   Minimal fix: remove `--alpha`, or require exact `0.05` before calculation. Add a rejection test for every other finite value.

3. **F3 — BLOCKER — the script emits registered gate outcomes from non-ten-block inputs.**  
   File: [dependence_sensitivity.py:71](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:71), [dependence_sensitivity.py:196](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:196), [dependence_sensitivity.py:238](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:238). The prose caveat is at [dependence-sensitivity.md:29](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:29), but the machine output does not enforce it.

   Registered rule: fixed \(n=10\) and minimum claim \(n=10\) are frozen ([generate_configs.py:1809](/Users/edr/code/JouleWise-wt-dependence/configs/campaigns/d117_contrast_v5/generate_configs.py:1809), [generate_configs.py:1851](/Users/edr/code/JouleWise-wt-dependence/configs/campaigns/d117_contrast_v5/generate_configs.py:1851), [generate_configs.py:2548](/Users/edr/code/JouleWise-wt-dependence/configs/campaigns/d117_contrast_v5/generate_configs.py:2548)). The registered engine labels a shortened set incomplete and suppresses its family p-value ([analysis_engine/__init__.py:694](/Users/edr/code/JouleWise-wt-dependence/joulewise/analysis_engine/__init__.py:694), [analysis_engine/__init__.py:1277](/Users/edr/code/JouleWise-wt-dependence/joulewise/analysis_engine/__init__.py:1277)).

   Concrete failure: `[6,5,4,5,5]` exits 0 with `n_blocks=5` and `independent_blocks.direction_gate.passes=true`.

   Minimal fix: live/registered mode must require exactly ten deltas. If arbitrary-\(n\) arithmetic is retained, give it an explicitly non-claim-bearing mode that emits no registered floor, direction, or Holm-facing fields.

4. **F4 — BLOCKER — DS-26, DS-31, PG-02, and PG-07 are not valid sensitivity consumers.**  
   File: [dependence-sensitivity.md:123](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:123).

   Registered rule: DS-26 and PG-02 own the primary fully composed endpoints; DS-31 and PG-07 own direction derived from those fully composed intervals ([results-fill-registry.md:815](/Users/edr/code/JouleWise-wt-dependence/docs/paper/results-fill-registry.md:815), [results-fill-registry.md:820](/Users/edr/code/JouleWise-wt-dependence/docs/paper/results-fill-registry.md:820), [results-fill-registry.md:825](/Users/edr/code/JouleWise-wt-dependence/docs/paper/results-fill-registry.md:825), [results-fill-registry.md:829](/Users/edr/code/JouleWise-wt-dependence/docs/paper/results-fill-registry.md:829)). The registry forbids a second live row for the same site ([results-fill-registry.md:832](/Users/edr/code/JouleWise-wt-dependence/docs/paper/results-fill-registry.md:832)), and a desk calculation is not an authorized supplier ([fill-checklist.md:17](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/fill-checklist.md:17), [fill-checklist.md:24](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/fill-checklist.md:24)). DS-31, PG-02, and PG-07 are explicitly stopped for missing tokens/suppliers ([fill-checklist.md:288](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/fill-checklist.md:288), [fill-checklist.md:292](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/fill-checklist.md:292), [fill-checklist.md:296](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/fill-checklist.md:296)). The cited ratification only governs DG-071/DG-075 and leaves them stopped until issuance through their declared route ([02-dg071-dg075-ratification.md:18](/Users/edr/code/JouleWise-wt-dependence/docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md:18)).

   Concrete failing sentence: “add a dependence-sensitivity supplier row for … DS-26 … DS-31 … PG-02 … PG-07.” That would overload primary-result sites with sampling-only values and bypass existing STOP_FILL rules.

   Minimal fix: register dedicated sensitivity-table and disagreement-sentence placements with new IDs, an authenticated artifact schema, exact source fields, and lead-approved working-copy insertion. Do not alter the suppliers or meanings of the four existing rows.

5. **F5 — SHOULD-FIX — Holm equality is not reproducible from the text.**  
   File: [dependence-sensitivity.md:66](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:66).

   Registered rule: rejection uses adjusted \(p\le\alpha\), inclusively ([multiplicity.py:153](/Users/edr/code/JouleWise-wt-dependence/joulewise/analysis_engine/multiplicity.py:153)).

   Concrete failure: with sorted raw p-values `0.025` and `0.05`, both comparisons pass under the registered code. “Compare” and “if … passed” do not state whether equality passes.

   Minimal fix: write “reject when \(p_{(1)}\le0.025\), then reject the second when \(p_{(2)}\le0.05\); equality passes.”

6. **F6 — SHOULD-FIX — effective-\(n\) halving is not a mathematical worst case.**  
   File: [dependence-sensitivity.md:23](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:23), [dependence-sensitivity.md:62](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:62).

   Controlling mathematics: the finite-\(n\) multiplier at [dependence-sensitivity.md:55](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:55).

   Concrete failure: for \(n=10,\rho=0.5\), the stated formula gives \(V=2.600391\) and \(n_{\mathrm{eff}}=3.845576\), already more adverse than halving to five. At \(\rho=0.9\), \(n_{\mathrm{eff}}=1.374341\).

   Minimal fix: rename it “fixed effective-\(n\)-halving sensitivity” or “pessimistic halving scenario”; do not call it worst-case.

7. **F7 — SHOULD-FIX — the new calibration replacement competes with the already approved H30 text.**  
   File: [dependence-sensitivity.md:76](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:76), [dependence-sensitivity.md:82](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:82).

   Ratified text: H30 specifies 118 onset/offset excursions from 59 pulses, the clock-anchor addition, both dependence concerns, and no deterministic out-of-sample guarantee ([retensing-plan.md:565](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/retensing-plan.md:565), [retensing-plan.md:569](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/retensing-plan.md:569)); the final fresh seat lists H30 as PASS and specifically verifies the withdrawal ([11-final-adjudication-opus.md:233](/Users/edr/code/JouleWise-wt-dependence/docs/process_traces/2026-08-31-registry-v5/11-final-adjudication-opus.md:233), [11-final-adjudication-opus.md:240](/Users/edr/code/JouleWise-wt-dependence/docs/process_traces/2026-08-31-registry-v5/11-final-adjudication-opus.md:240)).

   Concrete failing sentence: line 82’s alternative omits the 118-edge construction, dependence between onset and offset, and the out-of-sample caveat.

   Minimal fix: reference and reuse H30’s exact replacement instead of creating a second paper sentence.

8. **F8 — SHOULD-FIX — first-use pedagogy failures remain.**  
   File: [dependence-sensitivity.md:1](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:1), [dependence-sensitivity.md:11](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:11), [dependence-sensitivity.md:17](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:17), [dependence-sensitivity.md:39](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:39), [dependence-sensitivity.md:66](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:66), [dependence-sensitivity.md:115](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:115), [dependence-sensitivity.md:123](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:123).

   Registered standard: every technical term must be built or glossed at first use, and the procedure must be reproducible from text alone ([04-pedagogy-adjudication-opus.md:6](/Users/edr/code/JouleWise-wt-dependence/docs/process_traces/2026-08-31-registry-v5/04-pedagogy-adjudication-opus.md:6)).

   Terms failing at first use:

   - Line 1: `_v5`, “direction gate.”
   - Line 11: “sampler phase,” “deterministic drift allowance.”
   - Lines 17–27: “member run,” “standard error,” “critical value,” “half-width,” “t statistic,” “variance multiplier,” “floor gate,” `B_fiducial`, “unseen-population coverage,” “onset/offset,” and “sampling interval.”
   - Lines 33–39: alpha is used before its delayed gloss; “stochastic/deterministic metrology” and “claim-verdict producer” are never built.
   - Line 53: “shrunk toward zero” and “clip.”
   - Line 66: “model-matched.”
   - Line 78: “pulse-index analysis” and “population percentile.”
   - Lines 115 and 123–125: “authenticated block-delta JSON,” “fill registry,” “renderer,” “magistrate,” “supplier row,” and “placement.”

   Minimal fix: define each inline at its first occurrence or replace it with plain physical language; move the gate, SE, half-width, and critical-value definitions ahead of the table.

9. **F9 — SHOULD-FIX — guard deletion leaves most tests green.**  
   File: [test_dependence_sensitivity.py:18](/Users/edr/code/JouleWise-wt-dependence/tests/test_dependence_sensitivity.py:18), especially [test_dependence_sensitivity.py:19](/Users/edr/code/JouleWise-wt-dependence/tests/test_dependence_sensitivity.py:19) and [test_dependence_sensitivity.py:45](/Users/edr/code/JouleWise-wt-dependence/tests/test_dependence_sensitivity.py:45).

   Guard rules: [dependence_sensitivity.py:49](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:49) through [dependence_sensitivity.py:124](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:124), plus [dependence_sensitivity.py:149](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:149) through [dependence_sensitivity.py:200](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:200) and CLI guards at [dependence_sensitivity.py:271](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:271).

   Mutation result:

   - All six named tests still pass after individually deleting guards at lines 52–53, 63–66, 84–89, 103–104, 112–113, 120–121, 123–124, 149–153, 190–194, 199–200, 271–278, or 295–328.
   - Deleting either rho-range guard alone—91–92 or 106–107—also leaves all six tests passing because the duplicate guard masks the mutation.
   - Deleting 55–56 is caught only by `test_refuses_nonfinite_input`; the other five pass.
   - Deleting 71–72 is caught only by `test_refuses_fewer_than_five_blocks`; the other five pass.
   - Deleting both rho-range guards is caught by `test_refuses_out_of_range_rho`.
   - No test covers constant-denominator refusal, \(n_{\mathrm{eff}}<2\), alternating-\(n=10\), CLI nonzero/no-stdout behavior, forbidden Holm/support output, fixed \(\alpha\), fixed \(n=10\), strict gate equality, or invalid floor.
   - The example test asserts only mean, standard deviation, rho, endpoints, and Boolean gates. It does not assert the sum, squared deviations, rho numerator/denominator, nine AR terms, \(V\), \(n_{\mathrm{eff}}\), \(\nu\), SE, critical value, half-width, t statistic, p-value, or literal agreement with the document.

   Minimal fix: add subprocess tests for all five refusal cases and empty stdout; direct tests isolating every public guard; absence assertions for Holm/support verdicts; fixed-alpha/fixed-\(n\) tests; and a golden example covering every documented intermediate plus df 1–9 critical-value parity.

Checks that passed: the sign is correctly \(B-A\); direction equality correctly fails; Holm remains \(m=2\); critical values match for df 1–9; the rho estimator and \(\nu=\min(n-1,\lfloor n_{\mathrm{eff}}\rfloor-1)\) match doc and code; and every worked-example number reproduces.

The AR(1) multiplier derivation is exact:

\[
\operatorname{Var}(\bar d)=\frac{\sigma^2}{n^2}
\left[n+2\sum_{k=1}^{n-1}(n-k)\rho^k\right]
\]

\[
=\frac{\sigma^2}{n}
\left[1+2\sum_{k=1}^{n-1}(1-k/n)\rho^k\right]
=\frac{\sigma^2}{n}V.
\]

The five requested failure cases—\(n=4\), NaN, constant sequence, ten-value perfect alternation, and \(n=5\) with \(n_{\mathrm{eff}}<2\)—all exited 2 with empty stdout. `--example` emitted neither a Holm pass/fail nor a supported verdict.

## Residual risk

No full-suite or live campaign execution was performed. Review was limited to focused unit tests, independent desk recomputation, source inspection, and non-measurement CLI probes. No files were modified.

VERDICT: REFUTE