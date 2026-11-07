```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Propose availability, baseline and cooling-role amendments; this capture remains inconclusive.",
  "workspace": {
    "base_requested": "e1a91226e",
    "base_mode": "descendant",
    "head_start": "3c0b71b24ed56ed7ec194fbb6cde163004bc7573",
    "head_end": "3c0b71b24ed56ed7ec194fbb6cde163004bc7573",
    "upstream_end": "3c0b71b24ed56ed7ec194fbb6cde163004bc7573",
    "branch": "fix/2026-11-07-r0-smc-coverage-cell"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Repeated-code resets supply the current fast pick"
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The idle baseline is still cooling"
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "Classify cooling roles without the synthetic five-second gap"
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "The receipt reads obsolete capture-wide coverage"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "other",
      "cmd": "env PYTHONPATH=/Users/edr/code/jw-wt/r0-smc-cov /Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python -B -P - <<'PY'\nimport json, math, statistics as s, collections, hashlib, inspect, types\nfrom pathlib import Path\nfrom joulewise.align.apple import smc_enumeration as m\np=Path('/Users/edr/night-align/r0-v4-20261107T0810Z/smc')\nc=json.loads((p/'r0.json').read_text()); raw=(p/'samples.jsonl').read_bytes()\nc['samples']=[json.loads(x) for x in raw.splitlines()]\nph={x['phase']:x for x in c['phases']}\ndef series(k,phase):\n return [(x['elapsed_s']-ph[phase]['start_s'],x['values']['sensors'][k]) for x in c['samples'] if x['phase']==phase and k in x['values']['sensors']]\ndef slope(a):\n x=[t for t,v in a];y=[v for t,v in a];xm=s.mean(x);ym=s.mean(y)\n return 60*sum((t-xm)*(v-ym) for t,v in a)/sum((t-xm)**2 for t in x)\ndef vals(k,phase,a=0,b=1e9):return [v for t,v in series(k,phase) if a<=t<b]\ndef rnd(v): return round(v,6) if isinstance(v,float) else v\n\ndef resets(k):\n a=vals(k,'idle');b=vals(k,'load');d=vals(k,'recovery')\n z,n=collections.Counter(a).most_common(1)[0]; A=s.median(b)-z\n return n>len(a)/2 and d.count(z)>len(d)/2 and A>0 and any(\n  0<t-t0<=2 and v==z and u-v>=(1-1/math.e)*A\n  for (t0,u),(t,v) in zip(series(k,'recovery'),series(k,'recovery')[1:]))\nbad={x['key'] for x in c['inventory']['keys'] if x['unit']=='degC' and resets(x['key'])}\ndef return5(k,T):\n n=0\n for t,v in series(k,'recovery'):\n  n=n+1 if v<=T+1 else 0\n  if n>=5:return t\n return math.inf\ndef baseline_ok(k):\n a=series(k,'idle')\n slopes=[slope([(t,v) for t,v in a if j<=t<j+60]) for j in range(0,300,60)]\n medians=[s.median(vals(k,'idle',j,j+60)) for j in range(0,300,60)]\n return all(abs(v)<=.2 for v in slopes) and max(medians)-min(medians)<=1\nsrc=inspect.getsource(m.rank)\nsrc=src.replace('floor = max(.05, quantum, row[\"noise\"])','floor = max(quantum, row[\"noise\"])')\nsrc=src.replace('t63 <= 5 and tau is not None and tau <= 300','tau is not None and tau <= 30')\nsrc=src.replace('t63 > 5','True')\nsrc=src.replace('die = (sensor','die = (key not in bad and rise >= 3.0 and return5(key, baseline) <= 300 and sensor')\nsrc=src.replace('heatsink = (sensor','heatsink = (key not in bad and rise > 3*floor and rise60 > 3*floor and return5(key, baseline) <= 300 and sensor')\nns=dict(vars(m));ns.update(bad=bad,return5=return5,baseline_ok=baseline_ok)\nexec(src,ns);r=ns['rank'](c)\nprint('module',m.__file__)\nprint('sha256',hashlib.sha256(raw).hexdigest(),'match',hashlib.sha256(raw).hexdigest()==c['samples_sha256'])\nprint('inventory',len(c['inventory']['keys']),'samples',len(c['samples']))\nprint('reset_removed',len(bad),sorted(bad))\noriginal=m.rank(c)\nprint('original_counts',dict(collections.Counter(x['class'] for x in original['ranking'])),'picks',original['selection'])\nprint('signal_removed', sorted(set(original['heatsink_candidates'])-set(r['heatsink_candidates'])))\nprint('diagnostic_counts',dict(collections.Counter(x['class'] for x in r['ranking'])),'picks',r['selection'])\nexec(src.replace(' and return5(key, baseline) <= 300', ''),ns)\nunbounded=ns['rank'](c)\nprint('return_cap_removed',sorted({x['key'] for x in unbounded['ranking'] if x['eligible']}-{x['key'] for x in r['ranking'] if x['eligible']}))\n# Extend this same rank path with a capture-level baseline gate, without choosing substitutes.\ngate='''    candidate_selection = dict(proposed)\n    baseline_valid = all(candidate_selection.values()) and all(baseline_ok(k) for k in candidate_selection.values())\n    if not baseline_valid:\n        for row in ordered:\n            row.update(candidate_class=row[\"class\"], eligible=False, **{\"class\":\"record-only\", \"reason\":\"capture baseline unsettled\"})\n        proposed = select_keys(ordered)\n'''\nsrc=src.replace('    die_candidates = ',gate+'    die_candidates = ',1)\nsrc=src.replace('return {\"rule\": RULE,','return {\"baseline_valid\":baseline_valid, \"candidate_selection\":candidate_selection, \"rule\": RULE,')\nexec(src,ns)\nfor stage in ['r0','r1']:\n out=ns['rank'](c,stage=stage)\n print('full_rule',stage,'counts',dict(collections.Counter(x['class'] for x in out['ranking'])),'picks',out['selection'],'status',out['status'])\nfor k in ['Tg2I','TaRT','TCMb','TCDX','TCMz','Tf18','TW0P']:\n x=next(a for a in r['ranking'] if a['key']==k)\n print('response',k,*(rnd(x[v]) for v in ['observed_rise','delta_t60','noise','t63_s','tau_s']),x['class'])\n a=series(k,'idle');b=series(k,'recovery')\n print('cooling',k,'idle_medians',[round(s.median(vals(k,'idle',j,j+60)),3) for j in range(0,300,60)],'idle_slopes',[round(slope([(t,v) for t,v in a if j<=t<j+60]),3) for j in range(0,300,60)],'recovery_last60_slope',round(slope([(t,v) for t,v in b if t>=540]),3))\nfor k in ['Tf18','TW0P','TaRT']:\n x=next(a for a in r['ranking'] if a['key']==k)\n print('coverage',k,'stored',c['coverage']['per_key'][k]['valid_samples'],c['coverage']['per_key'][k]['expected_samples'],'phase_cells',x['phase_coverage'],'phase_errors',x['phase_read_error_fraction'],'return5_1C',rnd(return5(k,s.median(vals(k,'idle')))))\nz=c['samples'][1202]\nprint('recovery_example',round(z['elapsed_s']-ph['recovery']['start_s'],6),{k:rnd(z['values']['sensors'][k]) for k in ['Tg2I','TCMb']})\n\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "coverage TaRT stored 36 1800 phase_cells {'idle': 1.0, 'load': 1.0, 'recovery': 1.0} phase_errors {'idle': 0.0, 'load': 0.0, 'recovery': 0.0} return5_1C 149.067714",
          "recovery_example 2.078956 {'Tg2I': -2.75, 'TCMb': 79.679222}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "recovery_example 2\\.078956.*79\\.679222"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --porcelain=v1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "L1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING for adoption only: the proposed availability, baseline and role rules change sensor eligibility.",
      "needs": "Lead and owner must ratify eligibility changes before implementation or sensor pinning."
    }
  ]
}
```

## Findings

**Recommendation:** amend the classifier around continuous temperature availability, a settled baseline, and observed recovery. This capture should remain **inconclusive**. Tf18/TW0P are diagnostic candidates, not qualified replacements.

No files changed and no measurements started. V1 contains the exact replay command for the data results below. It authenticated the journal:

```text
sha256 16aa5307ffc24f55bc20d66823e8c9375d84da6ac723fa77b23d024f66244984 match True
inventory 403 samples 1800
```

**Decisions I made from the code and authority text:**

- Both picks must provide meaningful temperatures during idle, load and recovery. G0 compares them with the window reference; G1/H compare them with the episode’s G0 release values. Those references do not ratchet.
- G0 additionally requires the slow key’s preceding 60-second slope to satisfy `|slope| ≤0.2 °C/min`, for ten consecutive admissions. G1/H require five consecutive in-band samples and can stop an episode on timeout. A fast apparent step is insufficient if the key becomes unavailable during cooling.
- R0 supplies provisional candidates. WP14(a), FINAL-DESIGN §2.6 and Amendment 1 §A5 leave final selection to R1’s production D planning-turn step.
- Changing which keys qualify requires a ruling. The existing code’s thresholds do not independently establish anatomical die/heatsink identities.

These readings follow [thermal_gates.py](/Users/edr/code/jw-wt/r0-smc-cov/joulewise/align/apple/thermal_gates.py:350), [thermal_desk.py](/Users/edr/code/jw-wt/r0-smc-cov/joulewise/align/apple/thermal_desk.py:141), and the supplied design sections. The gate semantics, rather than the present five-second split, determine the needed observations.

**F1 — Blocker: reject repeated-code resets, including zero-valued aliases.**

Proposed observable veto:

> Let `z` be the idle modal decoded value and `A = median(load) − z`. Reject a temperature key as unavailable for gating if `z` occupies a strict majority of both idle and recovery, `A > 0`, and recovery contains a single adjacent-reading reset into exactly `z` of at least `(1−1/e)A`, across no more than two sampling periods.

Derivation:

- A strict majority is the point at which the modal code controls the median baseline; it avoids fitting a percentage to the observed occupancy.
- `1−1/e` uses the classifier’s existing one-e-fold response scale.
- Two periods are the maximum separation of observations in adjacent one-second cells with half-period timing allowance.
- Exact decoded-code equality uses the available representation, without inventing a Celsius cutoff.

This is a conservative availability veto, not proof of the firmware’s internal mechanism.

V1 removes **32 keys**, rather than only the 16 currently selected as die:

```text
Tg00 Tg01 Tg04 Tg05 Tg0C Tg0D Tg0K Tg0L Tg0y Tg0z
Tg16 Tg17 Tg1E Tg1F Tg1s Tg1t Tg1x Tg1y Tg21 Tg22
Tg29 Tg2A Tg2H Tg2I Tg33 Tg34 Tg3B Tg3C Tg3J Tg3K Tg3x Tg3y
```

The decisive window-time counterexample is:

```text
recovery_example 2.078956 {'Tg2I': -2.75, 'TCMb': 79.679222}
```

A negative-value filter misses the zero-valued members. The proposed veto uses neither key names nor sign.

**F2 — Blocker: the idle phase does not establish a settled baseline.**

V1 prints these medians for consecutive 60-second idle blocks:

| Key | Block medians, °C | Last idle-block slope, °C/min | Last recovery-block slope, °C/min |
|---|---|---:|---:|
| Tf18 | 42.539, 37.182, 35.060, 34.212, 33.505 | −0.641 | −0.256 |
| TW0P | 44.397, 38.372, 36.191, 35.297, 34.526 | −0.664 | −0.373 |
| TaRT | 33.564, 32.020, 30.965, 30.741, 30.686 | −0.129 | −0.281 |

Thus even the proposed candidate pair is still cooling at the end of idle. Its final recovery minute also exceeds G0’s slope limit after 600 seconds.

Proposed settle criterion:

> Accept the baseline only when both proposed top keys have five consecutive 60-second idle blocks with `|OLS slope| ≤0.2 °C/min`, and the range of those block medians is ≤1.0 °C. Otherwise reject the capture’s selection; retain candidate diagnostics and do not select quieter substitutes merely to pass.

The durations come from the existing 300-second baseline and 60-second slope window. The slope limit comes directly from G0. The 1 °C median-range limit is the minimum release band, also equal to five minutes at the permitted 0.2 °C/min drift. This establishes a baseline compatible with the control band; it does not claim thermodynamic equilibrium.

**R0 time cost:** with checks on those block boundaries, the failed final idle block means the earliest possible admission is after five further passing blocks: **at least +300 s**, making the SMC procedure **2,100 s instead of 1,800 s** in that best case. This is a scheduling lower bound, not a cooling forecast.

A sufficient fixed pre-idle dwell cannot be derived from this capture. **Measure first:** continue an idle-only record through the criterion and report the elapsed time. Extrapolating a fixed dwell from the first 1/e crossing would ignore the measured longer cooling tail.

**F3 — Should fix: classify cooling roles and require resolved signals in both.**

Proposed implementable rule:

> Retain the existing per-phase coverage, error and stale-series checks and model-free response quantities. Apply the repeated-code veto. For both roles require ΔT ≥3 °C, ΔT >3q and ΔT60 >3q, with resolved heating and cooling crossings. Use cooling τ ≤30 s for the fast-response role and 30 s <τ ≤300 s for the slow-state role. Select largest ΔT for fast and longest τ for slow, with lexical ties. Require observed recovery into the release band for five consecutive valid one-second cells by the 300-second cap. Reject both selections if the proposed pair fails baseline admission.

Derivations and limits:

- **30 s:** retain the already ruled cooling boundary and assign its previously uncovered side to the fast role. It also corresponds to three e-folds within the existing 90-second wait target: about 95% relaxation. This is an operating boundary, not an empirical gap or an anatomical classification.
- **300 s and five samples:** inherited from the actual G1/H cap and release condition. τ alone cannot guarantee return within a cap; excursion size and slower response components matter.
- **3 °C:** three times the minimum 1 °C release band, applying the existing slow-key rationale to both roles.
- **3q:** apply the existing fast-key signal-quality condition to both classes. A t63 computed from an unresolved ΔT60 should not qualify a slow key.
- **q:** use idle SD, decoder resolution and observed step information. I cannot derive the fixed **0.05 °C** floor from this capture; the replay removes it. Measure sensor quantum and idle variability after settling before freezing the rule.

For R0, the direct-return replay uses the minimum 1 °C band. R1 must use its qualified soak-derived bands. The return helper is a replay for this complete capture; production code must explicitly enforce valid consecutive cells.

V1’s response output confirms the uncovered CPU-cluster responses:

| Key | t63, s | Cooling τ, s | Amended diagnostic class |
|---|---:|---:|---|
| TCMb | 25.967 | 26.775 | fast |
| TCDX | 21.220 | 24.332 | fast |
| TCMz | 17.977 | 16.412 | fast |

The replay executes modified copies of the real `rank` source in memory and uses the real `select_keys`:

| Rule applied | Fast | Slow | Record-only | Picks |
|---|---:|---:|---:|---|
| Current classifier | 16 | 141 | 246 | Tg2I / TaRT |
| Amended availability, signal, cooling roles and return cap; baseline diagnostic only | 54 | 112 | 237 | Tf18 / TW0P |
| Full amendment including baseline admission | 0 | 0 | 403 | null / null |

The final row means **no qualification from this capture**; it preserves candidate classes separately. Calling the R1 stage on these same R0 samples gives the same refusal, not an R1 hardware result.

The shared signal gate removes these **29 current heatsink candidates**:

```text
TCHP TMVR TPD0 TPD1 TPD2 TPD3 TPD4 TPD5 TPD6 TPD7 TPD8 TPD9
TPDX TPDa TPDb TPDc TPDd TPDe TPDf TPMP TSXR TVFh TVFm
TaLP TaLT TaLW TaRF TaRT TaRW
```

For TaRT, V1 reports ΔT60 **0.063873 °C** against idle SD **1.136900 °C**. Its current heatsink test does not apply the fast class’s noise gate.

The added direct-return cap removes **zero** further candidates in this replay:

```text
return_cap_removed []
```

Tf18/TW0P reach five samples within the warm baseline +1 °C at **175.150041/170.014302 s**. Those times are diagnostic because that baseline failed admission.

**F4 — Should fix: the receipt should consume the classifier’s phase-cell evidence.**

[r0_host.py](/Users/edr/code/jw-wt/r0-smc-cov/joulewise/align/r0_host.py:487) should read—or recompute from the authenticated journal—the **same per-phase coverage counters used by `rank`**, with half-period cell allowance.

It should retain expected/valid cell counts and failed-read counts for each selected key and phase, then check the existing phase bars and the receipt’s aggregate **>99% over at least 600 expected cells** requirement. It should also require baseline admission and resolved distinct picks. It should not re-check the old capture-wide `payload["coverage"]` block.

V1 output for both diagnostic picks is:

```text
stored 36 1800
phase_cells {'idle': 1.0, 'load': 1.0, 'recovery': 1.0}
phase_errors {'idle': 0.0, 'load': 0.0, 'recovery': 0.0}
```

The half-period allowance derives from nearest-cell ownership at 1 Hz. The stored 100 ms allowance does not represent that definition.

**NEEDS_RULING — adoption only:** adopt the proposed availability, baseline, noise-floor and cooling-role changes, or retain the existing eligibility definition and obtain a qualifying alternative step/readout. I recommend the amendment; this consult does not ratify sensors.

For the next quiet R0 run, verify:

1. An extended idle record reaches the proposed settle criterion; record its actual time cost and derive variability/quantum from the accepted baseline.
2. The full inventory reproduces the reset veto, including zero-valued aliases, while candidate temperatures remain observable throughout recovery.
3. Proposed picks complete five valid in-band cells within the cap using phase-cell coverage. Final pins still come from R1’s D planning-turn test and soak-derived bands.

## Residual risk

The capture identifies response behavior, not sensor placement or calibration. The 30-second partition needs repeatability checks near its boundary at 1 Hz. R0 matmul responses cannot establish performance under D’s prefill/decode workload. No live thermometry qualification was performed in this consult.