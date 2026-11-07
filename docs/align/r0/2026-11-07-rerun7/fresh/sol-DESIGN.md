```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Choose sensors by observed control roles: TCMb and TVS0 are provisional candidates, but this capture does not qualify either because its baseline is still cooling.",
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
        "summary": "State-dependent placeholder channels qualify as temperatures; the observed pattern affects 32 keys."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "summary": "The 300-second idle is not a settled baseline for the proposed control sensors."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "summary": "Anatomical classes and fixed rise-time boundaries should be replaced by demonstrated control roles."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "summary": "The receipt rechecks coverage using a different grid from the classifier."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## fix/2026-11-07-r0-smc-coverage-cell...origin/fix/2026-11-07-r0-smc-coverage-cell"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## fix/2026-11-07-r0-smc-coverage-cell"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "PYTHONPATH=/Users/edr/code/jw-wt/r0-smc-cov /Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python -B -P -c 'import json,hashlib,collections; from pathlib import Path; from joulewise.align.apple import smc_enumeration as s; p=Path(\"/Users/edr/night-align/r0-v4-20261107T0810Z/smc\"); c=json.loads((p/\"r0.json\").read_text()); b=(p/\"samples.jsonl\").read_bytes(); assert hashlib.sha256(b).hexdigest()==c[\"samples_sha256\"]; c[\"samples\"]=[json.loads(x) for x in b.splitlines()]; r=s.rank(c); print(s.__file__); print(len(c[\"samples\"]),len(c[\"inventory\"][\"keys\"]),dict(collections.Counter(x[\"class\"] for x in r[\"ranking\"])),r[\"selection\"])'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "/Users/edr/code/jw-wt/r0-smc-cov/joulewise/align/apple/smc_enumeration.py",
          "1800 403 {'record-only': 246, 'die': 16, 'heatsink': 141} {'s_fast': 'Tg2I', 's_slow': 'TaRT'}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1800 403.*'die': 16.*'heatsink': 141.*Tg2I.*TaRT"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git merge-base --is-ancestor e1a91226e HEAD",
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
      "id": "A1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The proposed role, settling, and selection rules change which sensors count. They are design advice, not an adopted amendment.",
      "needs": "Lead and owner adjudicate the proposed amendment before implementation."
    },
    {
      "id": "A2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Offline replay completed; no new measurement or production-model qualification was performed.",
      "needs": "Run prospective R0 and R1 qualification after agents exit."
    }
  ]
}
```

## Findings

**Recommendation:** retain two control roles, choose **TCMb as the provisional hot-state witness** and **TVS0 as the provisional thermal-memory witness**, and qualify them prospectively. **This capture supplies no qualified pair.** Applying the proposed settling rule produces 403 record-only keys and null selections.

All analysis ran in memory. No files were written, no other proposals were read, and no measurement was started.

### F1 — Blocker: reject state-dependent placeholders, including their zero-valued counterparts

The observable disqualifier I propose is:

> A temperature channel is unsuitable for continuous control if its idle and recovery phases have the same exact nonpositive value on a strict majority of readings, while its load median is positive.

The majority boundary comes from the median: the state code controls both idle and recovery baselines. Exact recurrence identifies a code rather than ordinary temperature variation. The nonpositive boundary describes this capture’s observed inactive states; it is **not** a proposed universal ambient-temperature cutoff.

This rule scans all 403 keys and removes these **32**:

```text
Tg00 Tg01 Tg04 Tg05 Tg0C Tg0D Tg0K Tg0L Tg0y Tg0z
Tg16 Tg17 Tg1E Tg1F Tg1s Tg1t Tg1x Tg1y Tg21 Tg22
Tg29 Tg2A Tg2H Tg2I Tg33 Tg34 Tg3B Tg3C Tg3J Tg3K Tg3x Tg3y
```

Thus, rejecting negative readings alone misses the zero-valued versions. Removing these channels from the existing classifier leaves **0 die, 141 heatsink, 262 record-only**, with `s_fast=null`, `s_slow=TaRT`.

“Power-gated placeholder” is a physical interpretation of the pattern, not something waveform analysis proves uniquely. The operational conclusion is sufficient: these channels cannot report the state needed during idle, gates, or holds. Their **active portions remain useful reference observations**.

Constant idle temperature alone should not disqualify a channel. A real sensor can remain within one quantum at equilibrium. Demonstrated load response, continuity, and valid state reporting should decide suitability.

### F2 — Blocker: establish the baseline before estimating responses

The capture’s successive 60-second idle medians are:

| Key | First minute | Second | Third | Fourth | Fifth |
|---|---:|---:|---:|---:|---:|
| TCMb | 57.606 | 52.751 | 50.814 | 50.142 | 49.705 |
| TVS0 | 41.175 | 37.735 | 35.436 | 34.078 | 33.262 |
| TaRT | 33.564 | 32.020 | 30.965 | 30.741 | 30.686 |

The final-minute slopes are respectively **−0.634, −0.677, and −0.129 °C/min**. Replacing the whole-idle median with the final-minute median changes the response estimates, but does not make that minute settled.

My proposed R0 settling rule is:

> For both proposed control keys, require ten successive evaluations of the preceding 60-second OLS slope to satisfy  
> `abs(slope) × H / 60 ≤ δ`,  
> then use that final 60-second interval for the baseline and noise estimate.

For this replay:

- `H = 900 + 600 = 1500 s`, the subsequent response-observation interval.
- `δ = 1 °C`, the existing minimum control band.
- Therefore the slope limit is **0.04 °C/min**.
- The 60-second lookback and ten successive evaluations retain G0’s existing observation and confirmation periods.

This bounds projected background drift over the response test by one control band, **assuming passive cooling continues with decreasing slope**. Fan changes, environmental changes, or a poorly resolved tail invalidate that extrapolation and must be recorded.

**R0 time cost.** Diagnostic exponential fits give:

```text
EXTRAPOLATION idle TCMb tau 63.506 slope -0.634098 total_idle 485
EXTRAPOLATION idle TVS0 tau 140.433 slope -0.677427 total_idle 707
PLANNING_COST idle 707 extra_vs_300 407
EXTRAPOLATION recovery TCMb tau 485.284 slope -0.404511 total_idle 1732
EXTRAPOLATION recovery TVS0 tau 411.332 slope -0.312438 total_idle 1455
PLANNING_COST recovery 1732 extra_vs_300 1432
```

The difference between initial and recovery-tail estimates demonstrates why a fixed multiple of the initial cooling time is insufficient.

I would **budget 1,800 seconds of pre-idle**, rounding the approximately 1,732-second hot-tail estimate to the already specified R1 idle-soak duration. That adds **1,500 seconds** to the current R0 profile: **3,300 seconds total instead of 1,800**. Admission still depends on observed settling; expiration leaves qualification inconclusive.

Place this thermometry step before model and memory exercises. That reduces avoidable heat history, while the settling requirement handles whatever history remains.

### F3 — Should fix: choose demonstrated roles instead of anatomical classes

**What the control system actually needs.** From FINAL-DESIGN §§2.1, 2.2, 2.6, 2.8/V8 and [thermal_gates.py](/Users/edr/code/jw-wt/r0-smc-cov/joulewise/align/apple/thermal_gates.py:410):

- **Both keys** constrain G0, G1, and hold release.
- G0 additionally uses the slow key’s preceding-minute slope.
- The window reference is frozen from the first member’s idle; G1 and holds refer to that episode’s G0 release, preventing ratcheting.
- Holds begin at token boundaries determined from measured clock-decline behavior. Temperature determines their release.
- Missing state must become X4, not an apparent cold reading.
- Successful thermometry must support repeatable work and the U1–U5 acceptance requirements. Merely producing smooth traces is insufficient.

Consequently, `s_fast` needs a continuously available witness to the active hot state. `s_slow` needs a distinguishable memory of accumulated heating. Neither requirement establishes a physical die/heatsink location.

**Decisions I made:**

1. Keep two roles because the existing controller consumes two references with these distinct purposes. Two sensors remain a hypothesis to qualify.
2. Replace the fixed `t63≤5 s` class with an **active-state tracking test**.
3. Replace the `30<tau≤300 s` class with **resolved slower recovery and demonstrated release within the actual gate cap**.
4. Keep R0 selections provisional. R1’s production D workload owns final selection and qualification.
5. Preserve the in-process reader, frozen references, timeout behavior, and X4 fallback. These follow the code and design.

**Short implementable rule text**

> Enumerate and retain every channel. Exclude state-dependent placeholders from control eligibility. Require the existing per-phase readability bars. Estimate baseline and noise only from a settled final-minute interval. Require the load rise to exceed both the control band and three noise/quantum floors, and require a detectable rise within the first control-observation minute. Measure crossings against the full observed response.
>
> For the hot-state role, compare each continuous candidate against the maximum active reading of the state-dependent hot channels. Shortlist candidates whose RMS discrepancy and maximum under-reading are within the control band; select minimum RMS discrepancy, with lexical ties.
>
> For the memory role, require its cooling-crossing bracket to lie wholly after the hot witness’s bracket. Require five consecutive in-band recovery samples before the gate cap. Select the longest resolved cooling time, with lexical ties.
>
> Emit a usable pair only after both baselines and both roles qualify.

Threshold derivations:

| Quantity | Derivation |
|---|---|
| One-second cells; half-period assignment tolerance | Sampling period; nonoverlapping nearest-cell assignment |
| Format quantum | Decoder precision; for `flt `, binary32 spacing at the observed magnitude |
| Three noise floors | Existing three-SD band convention, applied symmetrically |
| One-degree replay band | Existing minimum δ; R1 must replace it with its measured band |
| 50–60-second response window | Last ten seconds of the existing 60-second observation period |
| `1−1/e` and `1/e` crossings | Definitions of heating and cooling characteristic times |
| Distinct recovery brackets | Separation exceeds the actual sampling uncertainty; no invented 30-second boundary |
| Five in-band observations | Existing G1/H release requirement |
| 300-second deadline | Existing maximum G1/H cap; τ alone does not determine return time |

The RMS threshold is a **shortlisting tolerance**, not proof of bounded error at every sample. R1 must explicitly examine worst under-reading, latency, and post-release behavior.

**Replay results through the real `rank` path**, patched only in memory:

| Stage | Retained / effect |
|---|---|
| Original classifier | 16 die; 141 heatsink; 246 record-only; `Tg2I / TaRT` |
| Placeholder rejection | Removes 32 channels |
| Units, signal, and resolved-crossing screen | 198 response candidates |
| Observed five-sample return before cap | 193 candidates |
| Hot-state tracking screen | 2 candidates: TCMb and TVD0 |
| Resolved memory-role screen | 160 candidates |
| Conditional role selection | **TCMb / TVS0**; 2 hot, 160 memory, 241 record-only |
| Settling enforced | **0 hot, 0 memory, 403 record-only; null / null** |

The recovery deadline removes `Tf0A` at **300.150 s**, and `Tp0C`, `Tp0D`, `Tp0R`, `Tp0S` at **305.057 s**.

Selected diagnostics, using the final-minute baseline for exploratory comparison:

| Key | Rise °C | Full-response t63 s | Cooling τ s | Five-sample return s | Hot-reference RMS °C |
|---|---:|---:|---:|---:|---:|
| TCMb | 36.148 | 22.225 | 28.926 | 264.105 | **0.054** |
| TCDX | 43.043 | 21.990 | 25.925 | 275.150 | 6.945 |
| TCMz | 40.823 | 11.882 | 20.095 | 270.143 | 3.172 |
| TVS0 | 9.212 | 123.208 | 148.309 | 257.150 | — |
| TaRT | 4.375 | 137.864 | 128.957 | 168.114 | — |

TCMb has **zero observed under-reading** against the active hot-channel maximum in the 899 reference rows. TCMb and TVD0 are exactly equal in all **1,800** captured rows; lexical selection chooses TCMb. They should not count as independent thermometers.

This is a stronger reason to investigate TCMb than relabelling its 22-second rise “die.” Its apparent rise time does not measure its tracking error against the active hot channels.

### F4 — Should fix: the receipt must consume the classifier’s phase coverage

[r0_host.py](/Users/edr/code/jw-wt/r0-smc-cov/joulewise/align/r0_host.py:484) should read the selected rows’ **per-phase coverage and read-error evidence**, recomputed from the digest-verified journal using the same helper as `rank`.

Retain, per key and phase:

- Phase span, grid origin, period, and cell-assignment rule.
- Expected and occupied cells.
- Actual read failures and invalid sensor states.
- Actual maximum sample gap.

Check the existing ten-minute readability requirement separately from response classification. Do not substitute a capture-wide grid for the phase grids.

The observed mismatch is:

```text
COVERAGE_OLD 100000000 1800 36
COVERAGE_PHASES {'idle': 1.0, 'load': 1.0, 'recovery': 1.0}
```

The old block reports only **36/1,800** occupied ticks at 100 ms tolerance; the classifier reports full phase coverage for TCMb. The common coverage definition should also reach the sidecar, gate, and desk paths so admission and acceptance evaluate the same observation requirement.

**Executed replay command A**

This authenticates the journal, invokes the existing classifier, patches its source in memory, and prints the proposed classifications and diagnostics. Exit code: **0**.

```bash
PYTHONPATH=/Users/edr/code/jw-wt/r0-smc-cov /Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python -B -P - <<'PY'
import json, math, inspect, hashlib, statistics as S
from collections import Counter
from pathlib import Path
from joulewise.align.apple import smc_enumeration as M
P=Path('/Users/edr/night-align/r0-v4-20261107T0810Z/smc')
C=json.loads((P/'r0.json').read_text()); B=(P/'samples.jsonl').read_bytes()
assert hashlib.sha256(B).hexdigest()==C['samples_sha256']
C['samples']=[json.loads(x) for x in B.splitlines()]; phases={p['phase']:p for p in C['phases']}
print('IMPORT',M.__file__); print('INPUT',len(C['samples']),len(C['inventory']['keys']),hashlib.sha256(B).hexdigest())
def summary(label,r): print(label,dict(Counter(x['class'] for x in r['ranking'])),r['selection'])
summary('ORIGINAL',M.rank(C))
V={i['key']:{p:[(r['elapsed_s'],r['values']['sensors'][i['key']]) for r in C['samples'] if r['phase']==p] for p in phases} for i in C['inventory']['keys']}
D={}
for i in C['inventory']['keys']:
 k=i['key']; a={p:[v for t,v in V[k][p]] for p in phases}; m=S.median(a['idle'])
 if i['unit']=='degC' and m<=0 and m==S.median(a['recovery']) and S.median(a['load'])>0 and all(a[p].count(m)>len(a[p])/2 for p in ['idle','recovery']): D[k]=m
print('PLACEHOLDERS',len(D),' '.join(sorted(D)))
ref=[]
for r in C['samples']:
 if r['phase']=='load':
  live=[r['values']['sensors'][k] for k,m in D.items() if r['values']['sensors'][k]!=m]
  if live: ref.append((r,max(live)))
print('ACTIVE_ROWS',len(ref)); print('TCMb_TVD0_EQUAL',sum(r['values']['sensors']['TCMb']==r['values']['sensors']['TVD0'] for r in C['samples']))
def slope(a):
 xm=S.mean(t for t,v in a); ym=S.mean(v for t,v in a)
 return 60*sum((t-xm)*(v-ym) for t,v in a)/sum((t-xm)**2 for t,v in a)
def extra(row,key,good):
 ends=[phases['idle']['end_s']-j for j in range(9,-1,-1)]
 row['slopes']=[slope([(t,v) for t,v in good['idle'] if e-60<=t<e]) for e in ends]
 row['settled']=all(abs(b)<=60/1500 for b in row['slopes'])
 d=[r['values']['sensors'][key]-v for r,v in ref]
 row['rmse']=math.sqrt(S.mean(x*x for x in d)); row['under']=max(0,-min(d))
 row['return']=None; n=0
 for t,v in good['recovery']:
  n=n+1 if v<=row['base']+1 else 0
  if n==5: row['return']=t-phases['recovery']['start_s']; break
 target=row['base']+(good['recovery'][0][1]-row['base'])/math.e
 j=next((j for j,(t,v) in enumerate(good['recovery']) if v<=target),None)
 row['bracket']=None if j is None else [good['recovery'][max(0,j-1)][0]-good['recovery'][0][0],good['recovery'][j][0]-good['recovery'][0][0]]
src=inspect.getsource(M.rank); a=src.index('        if len(set(idle)) < 3:'); b=src.index('        onset =',a)
src=src[:a]+'''        if key in D:
            row['reason']='placeholder'
            continue
        idle=[v for t,v in good['idle'] if phases['idle']['end_s']-60<=t<phases['idle']['end_s']]
        baseline=statistics.median(idle); row['base']=baseline; row['noise']=statistics.pstdev(idle)
        typed={'sp78':1/256,'fpe2':.25,'ioft':1/65536,'ui8 ':1,'ui16':1,'ui32':1}
        q=2**(max(-126,math.floor(math.log2(max(abs(v) for v in idle))))-23) if sensor.get('data_type')=='flt ' and any(idle) else typed.get(sensor.get('data_type'),2**-149)
        floor=max(q,row['noise']); row['noise_floor']=floor
'''+src[b:]
src=src.replace('baseline + .632*rise60','baseline + (1-1/math.e)*rise').replace('if rise60 > 0 else None','if rise > 0 else None')
a=src.index('        die = ('); b=src.index('        row["class"]',a)
src=src[:a]+'''        extra(row,key,good)
        die=(sensor['unit']=='degC' and rise>max(1,3*floor) and rise60>3*floor
             and t63 is not None and tau is not None and tau>0)
        heatsink=False
'''+src[b:]
strict=False
def choose(rows):
 q=[r for r in rows if r['eligible']]; u=[r for r in q if r['return'] is not None and r['return']<=300]
 hot=[r for r in u if r['rmse']<=1 and r['under']<=1]; f=min(hot,key=lambda r:(r['rmse'],r['key'])) if hot else None
 memory=[r for r in u if f and r not in hot and r['bracket'][0]>f['bracket'][1]]
 if not strict: print('SCREENS',len(q),len(u),len(hot),len(memory),'RECOVERY_REMOVED',[(r['key'],round(r['return'],3)) for r in q if r not in u])
 for r in rows: r['class']='record-only'; r['eligible']=False
 for bank,label in [(hot,'die'),(memory,'heatsink')]:
  for r in bank:
   if not strict or r['settled']: r['class']=label; r['eligible']=True
 hot=[r for r in hot if r['eligible']]; memory=[r for r in memory if r['eligible']]
 return {'s_fast':min(hot,key=lambda r:(r['rmse'],r['key']))['key'] if hot else None,'s_slow':min(memory,key=lambda r:(-r['tau_s'],r['key']))['key'] if memory else None}
ns=dict(vars(M),D=D,extra=extra,select_keys=choose); exec(compile(src,'<in-memory-rank>','exec'),ns)
R=ns['rank'](C); summary('CONDITIONAL',R)
for k in ['TCMb','TCDX','TCMz','TVS0','TaRT']:
 r=next(r for r in R['ranking'] if r['key']==k)
 print('KEY',k,[(n,round(r[n],6)) for n in ['base','amplitude','delta_t60','noise_floor','t63_s','tau_s','return','rmse','under']], 'SLOPE',round(r['slopes'][-1],6))
 print('IDLE60',k,[round(S.median(v for t,v in V[k]['idle'][j:j+60]),6) for j in range(0,300,60)])
strict=True; summary('SETTLED',ns['rank'](C))
print('COVERAGE_OLD',C['coverage']['tolerance_ns'],C['coverage']['all_keys']['expected_samples'],C['coverage']['all_keys']['valid_samples'])
print('COVERAGE_PHASES',next(r['phase_coverage'] for r in R['ranking'] if r['key']=='TCMb'))
PY
```

Key output, with detailed numeric rows transcribed into the tables above:

```text
IMPORT /Users/edr/code/jw-wt/r0-smc-cov/joulewise/align/apple/smc_enumeration.py
INPUT 1800 403 16aa5307ffc24f55bc20d66823e8c9375d84da6ac723fa77b23d024f66244984
ORIGINAL {'record-only': 246, 'die': 16, 'heatsink': 141} {'s_fast': 'Tg2I', 's_slow': 'TaRT'}
ACTIVE_ROWS 899
TCMb_TVD0_EQUAL 1800
SCREENS 198 193 2 160 RECOVERY_REMOVED [('Tf0A', 300.15), ('Tp0C', 305.057), ('Tp0D', 305.057), ('Tp0R', 305.057), ('Tp0S', 305.057)]
CONDITIONAL {'record-only': 241, 'heatsink': 160, 'die': 2} {'s_fast': 'TCMb', 's_slow': 'TVS0'}
SETTLED {'record-only': 403} {'s_fast': None, 's_slow': None}
COVERAGE_OLD 100000000 1800 36
COVERAGE_PHASES {'idle': 1.0, 'load': 1.0, 'recovery': 1.0}
```

The replay retains the original class labels only for compatibility with `rank`’s return shape.

**Executed cooling-cost command B**

This fits `C + A exp(−t/τ)` to the final 300 observations of each phase. The logarithmic grid is numerical search configuration, not an eligibility threshold. Exit code: **0**; output appears under F2.

```bash
PYTHONPATH=/Users/edr/code/jw-wt/r0-smc-cov /Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python -B -P - <<'PY'
import json,math,statistics as st
from pathlib import Path
P=Path('/Users/edr/night-align/r0-v4-20261107T0810Z/smc')
rows=[json.loads(x) for x in (P/'samples.jsonl').read_bytes().splitlines()]
def fit(a):
 best=None
 for j in range(600):
  tau=.5*(10000/.5)**(j/599);xx=[math.exp(-t/tau) for t,v in a]
  xm=st.mean(xx);ym=st.mean(v for t,v in a)
  amp=sum((x-xm)*(v-ym) for x,(t,v) in zip(xx,a))/sum((x-xm)**2 for x in xx);base=ym-amp*xm
  sse=sum((v-base-amp*x)**2 for x,(t,v) in zip(xx,a))
  if best is None or sse<best[0]:best=(sse,tau)
 return best[1]
for phase,duration in [('idle',300),('recovery',600)]:
 estimates=[]
 for key in ['TCMb','TVS0']:
  rr=[r for r in rows if r['phase']==phase][-300:];t0=rr[0]['elapsed_s'];a=[(r['elapsed_s']-t0,r['values']['sensors'][key]) for r in rr]
  last=a[-60:];xm=st.mean(t for t,v in last);ym=st.mean(v for t,v in last)
  slope=60*sum((t-xm)*(v-ym) for t,v in last)/sum((t-xm)**2 for t,v in last)
  tau=fit(a);extra=math.ceil(tau*math.log(abs(slope)/(60/(900+600))))+9
  estimates.append(duration+extra)
  print('EXTRAPOLATION',phase,key,'tau',round(tau,3),'slope',round(slope,6),'total_idle',duration+extra)
 print('PLANNING_COST',phase,max(estimates),'extra_vs_300',max(estimates)-300)
PY
```

## Residual risk

This is one GPU workload and one heat history. It cannot establish sensor anatomy, absolute accuracy, or production-workload sufficiency. TVS0 could be a filtered or virtual channel; its independent value for control remains to be demonstrated. The cooling extrapolations are planning estimates, not guaranteed settling times.

The next exact work is a lead-controlled R0 after agents exit:

1. Put thermometry before model exercises; retain all channels and fan observations. Budget the longer idle and admit only after observed settling.
2. Repeat the response capture and apply the same classification path. Check whether TCMb’s active-hot-state agreement and TVS0’s distinct recovery survive the settled baseline.
3. In R1, use the actual production D planning workload. Measure idle noise, refresh behavior, read-bracket uncertainty, worst under-reading, joint five-sample recovery, and behavior immediately after release. **Measure first** before setting any additional latency or repeatability tolerance.
4. Freeze the sensor map only after production replay demonstrates the existing energy, clock, release-state, and state-sensitivity requirements. If the pair cannot do that, retain X4/no thermal-control claim or investigate another reader.