```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"partial","summary":"Sentence review found truth and first-use gaps; arithmetic passed, but the required suite exited 1.","workspace":{"base_requested":"5b85d401097c90427ccd1b3de1864c31b17c52ec","base_mode":"exact","head_start":"078a13a461abd124c29796798da5107fe00190a6","head_end":"078a13a461abd124c29796798da5107fe00190a6","upstream_end":null,"branch":null},"pathspec":[],"unowned_dirty":[],"verdict":{"decision":"CHANGES_REQUIRED","findings":[{"id":"R1","severity":"should_fix","sentences":[12,15],"text":"Non-numeric durations receive capture-interval credit; NaN receives zero and also needs a zero-overlap case."},{"id":"R2","severity":"should_fix","sentences":[2,9,10],"text":"Frozen consumers and the cooldown evidence/reference terms lack definitions before use."},{"id":"R3","severity":"should_fix","sentences":[9,13,27],"text":"The 30-second window, thermal requirement and 5-minute cap need production-policy scope."},{"id":"R4","severity":"should_fix","sentences":[8,18],"text":"The comparisons accept deficits within their allowance without establishing their cause."},{"id":"R5","severity":"should_fix","sentences":[11,24],"text":"Requested probe length is not an enforced lower bound on actual capture duration or a reading-count cap."},{"id":"R6","severity":"should_fix","sentences":[25],"text":"No real probe cadence produces this count is an unsupported empirical assertion."}]},"verification":[{"id":"V1","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gate_sensibility_rounding tests.test_docs_freshness","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAILED (errors=4)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V2","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -c 'import math\nu = math.ulp(1.789e9)\nslack = lambda n,c: max(1e-6,2*n*u+math.ulp(c))\nprint(\"ULP_us\", u*1e6)\nprint(\"four_ULP_us\", 4*u*1e6)\nprint(\"per_reading_us\", 2*u*1e6)\nprint(\"sum_ULP_s\", math.ulp(24.0))\nprint(\"six_seven_us\", [slack(n,24)*1e6 for n in (6,7)])\nprint(\"12_13_ULP_edges\", [(k,24-k*u+slack(6,24-k*u)>=24) for k in (12,13)])\nprint(\"20_21_readings_10us\", [(n,24-1e-5+slack(n,24-1e-5)>=24) for n in (20,21)])\nprint(\"40_readings_us\", slack(40,30)*1e6)\nprint(\"forty_probe_span_s\",40*0.75)\nprint(\"210s_1ms_readings\",210/0.001)\nassert 40*0.75==30 and 210/0.001==210000\nprint(\"30s_1ms_readings\", 30/0.001)\nprint(\"30000_30001_readings_ms\", [slack(n,30)*1e3 for n in (30000,30001)])\nprint(\"100ms_readings\", 0.1/(2*u), math.ceil(0.1/(2*u)))\nassert abs(u*1e6-0.238)<0.001\nassert abs(4*u*1e6-0.954)<0.001\nassert abs(2*u*1e6-0.477)<0.001\nassert 24-12*u+slack(6,24-12*u)>=24\nassert 24-13*u+slack(6,24-13*u)<24\nassert 24-1e-5+slack(20,24-1e-5)<24\nassert 24-1e-5+slack(21,24-1e-5)>=24\nassert abs(slack(40,30)*1e6-19)<0.1\nassert abs(slack(30001,30)*1e3-14)<0.4\nassert abs(math.ceil(0.1/(2*u))-210000)<300\nprint(\"ARITHMETIC_OK\")'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["ARITHMETIC_OK"]},"expected":{"exit_code":0,"tail_regex":"ARITHMETIC_OK"}},{"id":"V3","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -c 'import ast, math, subprocess\nfrom dataclasses import asdict, replace\nfrom types import SimpleNamespace\nfrom typing import Any\nfrom joulewise.clock import FakeClock\nfrom joulewise.cooldown import cooldown_disposition_from_raw\nfrom joulewise.schemas import BenchmarkConfig, CooldownPolicy, IdleBaseline, TelemetryBackend\nsource=subprocess.check_output([\"git\",\"show\",\"5b85d401:joulewise/controller.py\"],text=True)\nnode=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name==\"cooldown_gate\")\nns=globals()|{\"_jsonable\":lambda value:value}\nexec(compile(\"from __future__ import annotations\\n\"+ast.unparse(node),\"<5b85d401:cooldown_gate>\",\"exec\"),ns)\nconfig=BenchmarkConfig.from_mapping(__import__(\"json\").loads(subprocess.check_output([\"git\",\"show\",\"5b85d401:configs/examples/mock_local.json\"],text=True)))\ndef run(duration, *, step=5.0, policy=None, thermal=\"nominal\"):\n    clock=FakeClock(1_789_000_000.0)\n    class Telemetry:\n        def measure_idle(self, config):\n            clock.sleep(step)\n            return IdleBaseline(5.0,0.0,duration,40,TelemetryBackend.POWERMETRICS)\n        def thermal_state(self, config):\n            return SimpleNamespace(thermal_pressure=thermal)\n    return ns[\"cooldown_gate\"](Telemetry(),IdleBaseline(5.0,0.0,30.0,30,TelemetryBackend.POWERMETRICS),config,clock,policy=policy)\nfor name,duration in [(\"None\",None),(\"string\",\"bad\"),(\"NaN\",float(\"nan\")),(\"zero\",0),(\"negative\",-1)]:\n    result=run(duration)\n    print(name,result[\"result\"],result[\"window_coverage_s\"])\n    assert result[\"window_coverage_s\"] == (0 if name==\"NaN\" else 30)\ncustom=CooldownPolicy.from_mapping({\"sustained_window_s\":5,\"subwindow_s\":1,\"cap_s\":10,\"require_thermal_nominal\":False})\nresult=run(1,step=1,policy=custom,thermal=\"serious\")\nprint(\"custom_policy\",result[\"result\"],result[\"window_span_s\"],result[\"thermal_pressure\"])\nassert result[\"result\"]==\"recovered\" and result[\"window_span_s\"]==5\nresult=run(1,step=1)\nprint(\"requested_5s_actual_1s\",result[\"result\"],len(result[\"_trace\"]))\nassert len(result[\"_trace\"])==30\nu=math.ulp(1_789_000_000.0)\nresult=run(4-u)\nprint(\"explicit_short_duration\",result[\"result\"],24-result[\"window_coverage_s\"])\nassert result[\"result\"]==\"recovered\" and result[\"window_coverage_s\"]<24\nendpoints=[1_789_000_000.0+5*i for i in range(1,9)]\nprint(\"at_least_5s_retained_counts\",[sum(end>now-30 for end in endpoints[:i+1]) for i,now in enumerate(endpoints)])\nassert all(sum(end>now-30 for end in endpoints[:i+1])<=6 for i,now in enumerate(endpoints))\nprint(\"CODE_PROBES_OK\")'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["CODE_PROBES_OK"]},"expected":{"exit_code":0,"tail_regex":"CODE_PROBES_OK"}},{"id":"V4","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -c 'import math\nepoch=1_789_000_000.0\nduration=30.0000005\nspan=(epoch+30)-epoch\nprint(\"admission_explicit_excess_s\",duration-span)\nprint(\"admission_duration_refuses\",duration>span+1e-6)\nassert duration>span and not duration>span+1e-6\nstart=epoch\nend=epoch+5\nduration=math.nan\nevidence_start=max(end-duration,start)\nclipped_start=max(evidence_start,end-30)\ndifference=end-clipped_start\noverlap=max(0.0,difference)\nprint(\"nan_overlap\",math.isnan(difference),difference<0,overlap)\nassert math.isnan(difference) and not difference<0 and overlap==0.0\nprint(\"BOUNDARY_PROBES_OK\")'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["BOUNDARY_PROBES_OK"]},"expected":{"exit_code":0,"tail_regex":"BOUNDARY_PROBES_OK"}}],"flags":[{"id":"F1","kind":"baseline_drift","level":"blocking","text":"The detached worktree is not the reviewed commit and lacks tests.test_gate_sensibility_rounding. Source review used git show at the requested commit.","needs":"Lead must rerun the required suite against the reviewed revision."},{"id":"F2","kind":"environment","level":"blocking","text":"Three docs-freshness tests failed because the read-only sandbox provides no writable temporary directory; no test pass is claimed.","needs":"Lead must rerun with ordinary test-temporary-directory access."}]}
```

## Findings

**CHANGES REQUIRED.** Arithmetic passes, but the prose still has code-truth and first-use defects. No files or Git state were changed.

All references below are at `5b85d401`. Filenames are under `joulewise/`, except `powermetrics.py`, which is under `joulewise/adapters/`. Rows 1–8 cover admission; rows 9–27 cover cooldown.

| Sentence and code verdict | Terms built or glossed before first use? |
|---|---|
| **1.** “Each admission attempt records its start and end times” — **TRUE-OF-CODE:** `controller.py:1113–1124`; `clock.py:55–56`. | Yes. |
| **2.** “Strict reduction” — **TRUE-OF-CODE:** `environment_admission.py:84–124,140–191`; strict dispatch at `reduce.py:703–716`. | **No — R2:** “frozen consumers” is named without explaining what is frozen. |
| **3.** “First, a duration check” — **TRUE-OF-CODE:** `environment_admission.py:172–184`; sampler sum at `powermetrics.py:333–334`. | Yes; attempt span is defined inline. |
| **4.** “Second, a timestamp check” — **TRUE-OF-CODE:** `environment_admission.py:116–124,186–191`. | Yes; endpoints and capture interval are constructed inline. |
| **5.** “A record whose timestamp is not a finite number” — **TRUE-OF-CODE:** `environment_admission.py:67–71,104–115`. | Yes. |
| **6.** “The 1 μs allowance exists” — **TRUE-OF-CODE:** the two arithmetic paths appear at `powermetrics.py:333–334` and `environment_admission.py:120,182,188–189`; rationale at `environment_admission.py:23–24`. | Yes. |
| **7.** “A binary64 epoch value near 1.789e9” — **TRUE-OF-CODE:** executed arithmetic confirms 0.238418579 μs and 0.953674316 μs; allowance at `environment_admission.py:24`. | Yes. |
| **8.** “The allowance never credits unobserved time” — **FALSE — R4:** `baseline_duration_s > attempt_end_s - attempt_start_s + ADMISSION_TIME_ROUNDING_S` (`environment_admission.py:182`) permits a positive excess within the allowance without determining its cause. The three stated refusal examples are correct. | Yes. |
| **9.** “Between live repetitions, cooldown v2 holds” — **FALSE as an unqualified policy statement — R3:** `window_span_s + 1e-6 >= selected.sustained_window_s` and `(thermal_nominal or not selected.require_thermal_nominal)` (`controller.py:2559,2571`). Thirty seconds and mandatory Nominal pressure describe production defaults. | **No — R2:** retained readings, cooldown span, coverage, overlap, and the reference power are used before their constructions. “Both built below” explicitly postpones definitions. |
| **10.** “A below-reference mean therefore counts as recovery” — **TRUE-OF-CODE for the relative power criterion:** `controller.py:2552,2565–2567`; other release conditions still apply. | **No — R2:** the reference remains unspecified here. |
| **11.** “The evidence is a series of idle probes” — **FALSE as an actual-duration statement — R5:** `idle_seconds=selected.subwindow_s` sets the request (`controller.py:2496`); actual reported duration comes separately from `duration_s = baseline.duration_s` (`controller.py:2505`). | Yes; `subwindow_s` is introduced as a duration. |
| **12.** “Every probe becomes a reading with three clock readings” — **FALSE — R1:** `if not isinstance(duration_s, int \| float) or duration_s <= 0.0:` selects `duration_s = max(0.0, now_s - subwindow_start_s)` (`controller.py:2506–2507`). Non-numeric values receive capture-interval credit; floating-point NaN receives zero overlap. | Yes. |
| **13.** “The window cutoff is the current time minus 30 s” — **FALSE without production scope — R3:** `cutoff = now_s - selected.sustained_window_s` (`controller.py:2515`). | Yes. |
| **14.** “A reading is retained” — **TRUE-OF-CODE:** `controller.py:2516`. | Yes; retention is defined here, although already used in sentence 9. |
| **15.** “A retained reading's clipped start” — **FALSE for NaN duration — R1:** `overlap_s = max(0.0, evidence_end - clipped_start)` (`controller.py:2523`) returns zero when the difference is NaN, although NaN is not negative. The sentence omits that case. | Yes; clipped start and overlap are constructed here. |
| **16.** “Coverage is the sum of the overlaps” — **TRUE-OF-CODE:** `controller.py:2518,2525`. | Yes; coverage is defined here, although already used in sentence 9. |
| **17.** “Span is the current time” — **TRUE-OF-CODE for forward-running captures:** `controller.py:2526–2541`. | Yes; cooldown span is constructed here. |
| **18.** “Span and coverage are tested” — **FALSE in its “never” clause — R4:** `coverage_s + coverage_slack_s >= required_coverage_s` (`controller.py:2563`) accepts any sufficiently small deficit. It does not classify its cause. | Yes. |
| **19.** “One representable step of a binary64 epoch value” — **TRUE-OF-CODE:** executed `math.ulp(1.789e9)`; the same operation appears at `controller.py:2528`. | Yes; ULP is glossed inline. |
| **20.** “The span test allows 1 μs” — **TRUE-OF-CODE:** `controller.py:2559`. | Yes. |
| **21.** “The coverage test allows the larger” — **TRUE-OF-CODE:** `controller.py:2526–2529,2560–2563`. At 24 s, the additional ULP is `3.5527136788e-15` s. | Yes. |
| **22.** “The term is an upper bound” — **TRUE-OF-CODE as a conservative bound:** `controller.py:2526–2529,2560–2562`. Six/seven contributions give 2.861022953/3.337860111 μs. | Yes. |
| **23.** “At that policy a six-reading coverage deficit” — **TRUE-OF-CODE:** `controller.py:2560–2563`; executed boundary checks accept 12 ULP and reject 13 ULP, and reject 10 μs with 20 readings. | Yes. |
| **24.** “A shorter `subwindow_s` retains more readings” — **FALSE as a guaranteed cap — R5:** `minimum=0.001` constrains the requested value (`schemas.py:542–544`); retention uses only `reading[2] > cutoff` (`controller.py:2516`). No actual-duration minimum or reading-count cap is enforced here. The 14 ms calculation is correct **conditional on actual cadence**. | Yes. |
| **25.** “Reaching a full sample would need about 210,000 retained readings” — **UNVERIFIABLE — R6:** arithmetic supports approximately 210,000 positive-overlap readings; the assertion that no real probe cadence produces them requires empirical evidence absent from this code. `controller.py:2516,2526–2529` imposes no count cap. | Yes. |
| **26.** “An optional calibrated absolute ceiling” — **TRUE-OF-CODE:** `effective_upper_w = min(effective_upper_w, selected.absolute_ceiling_w)` at `controller.py:2554–2555`. | Yes; its role is glossed as an additional upper cap. |
| **27.** “The wait has a 5-minute cap” — **FALSE without production scope — R3:** `cap_hit = waited_s >= selected.cap_s` (`controller.py:2573`). Cap precedence and late-trace recording are correct (`controller.py:2574–2592,2636–2648`), as is propagation to the following repetition (`controller.py:2984–2985`; `reduce.py:2844`). | Yes. |

The executed arithmetic returned:

- ULP: **0.238418579 μs**; four ULP: **0.953674316 μs**; two ULP per reading: **0.476837158 μs**.
- Six/seven readings: **2.861022953 / 3.337860111 μs**.
- Six-reading deficit: **12 ULP passes; 13 ULP refuses**.
- A 10 μs deficit: **20 readings refuse; 21 pass**.
- **40 × 0.75 s = 30 s**, with **19.073486332 μs** allowance.
- **30 s / 1 ms = 30,000 readings**, giving approximately **14.305 ms**.
- A 100 ms term corresponds to **209,715.2 readings**, hence approximately **210,000**.

The target-function probes also confirmed: `None` and `"bad"` durations recovered with full capture coverage; NaN reached `cap_hit` with zero coverage; a configurable five-second window released under Serious thermal pressure when the policy disabled the thermal requirement.

**Exact minimal edits**

The old sentences are identified by their table numbers; each replacement below is complete.

1. **R2 — Sentence 2 →**

   “Strict reduction (the consumer path that re-validates admission evidence; historical replay paths preserve their older validation rules instead) then makes two containment checks; when either fails, or when the attempt's telemetry file is absent, empty or unparsable, the attempt refuses with `environment_admission_missing`.”

2. **R4 — Sentence 8 →**

   “A baseline longer than the attempt by 10 μs, or a capture endpoint 10 μs outside the attempt, refuses, as does an endpoint one sample interval (100 ms) outside it.”

3. **R2/R3 — Move sentences 9–10 immediately after sentence 17. Replace sentence 9 with the following; retain sentence 10 after it.**

   “Under the production policy, cooldown v2 releases when span covers the 30 s window, coverage reaches the required fraction of that window (`coverage_fraction`, 0.8 by default, hence 24 s), and thermal pressure is Nominal, subject to the rounding allowances and cap below; its power check compares the sum of each retained reading's mean idle power times its overlap, divided by coverage (`rolling_mean`), with the selected reference baseline's mean power (`reference`) using `rolling_mean <= reference * (1 + tolerance)`, where `tolerance` is 0.10 in production.”

4. **R5 — Sentence 11 →**

   “Cooldown v2 collects a series of idle probes, each requesting a capture of `subwindow_s` seconds (5 s by the production policy).”

5. **R1 — Sentence 12 →**

   “Every probe becomes a reading with three clock readings (seconds since the Unix epoch as binary64 numbers): its capture start, taken just before the probe began; its evidence end, taken when the probe returned; and its evidence start, the evidence end minus the probe's reported capture duration, but never earlier than the capture start (a probe that reports a zero, negative, or non-numeric duration is credited its whole capture interval; one that reports floating-point NaN, the ‘not a number’ value, is credited nothing).”

6. **R3 — Sentence 13 →**

   “The window cutoff is the current time minus the policy's window length, `sustained_window_s` (30 s in production).”

7. **R1 — Sentence 15 →**

   “A retained reading's clipped start is the later of its evidence start and the cutoff, and its overlap is its evidence end minus its clipped start, or zero if that difference is negative or NaN.”

8. **R4 — Sentence 18 →**

   “Span and coverage are tested with a small allowance intended for floating-point rounding.”

9. **R5 — Sentence 24 →**

   “A shorter `subwindow_s` can retain more readings and widen the term in proportion (40 readings of 0.75 s: 19 μs); if probes actually last at least 1 ms, a 30 s window retains at most 30,001 readings, keeping the term near 14 ms, below one 100 ms sample.”

10. **R6 — Sentence 25 →**

    “At the stated epoch, a 100 ms allowance would require about 210,000 retained readings with positive overlap (for example, about 210 s of 1 ms probes); the gate has no explicit reading-count cap.”

11. **R3 — Sentence 27 →**

    “The wait is capped by the policy's `cap_s` duration (5 minutes in production); the cap is evaluated before release on every iteration, so recovery criteria first met at or after the deadline remain a `cap_hit` (with the late criteria recorded in the trace) and are recorded in the following repetition's measurement quality.”

Nonblocking style nits: none.

## Residual risk

The required suite **failed with rc 1**, so approval remains gated even after the prose corrections. It reported one missing test module and three temporary-directory errors. The supplemental cooldown probes executed the requested commit’s function in memory with fake telemetry; they do not replace the required suite or constitute live validation.

Next step: the lead applies the sentence replacements and ordering change, then reruns the required suite against that revised commit with normal temporary-directory access.