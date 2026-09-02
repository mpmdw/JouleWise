```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All scientific cures and numbers pass; DG-128 has an off-by-one body locator and strict first-use pedagogy still needs fixes.",
  "workspace": {
    "base_requested": "b1d23e41..97fe8fc2",
    "base_mode": "exact",
    "head_start": "b1d23e41bcaf1a5fbb295f8f82da78cc2020f805",
    "head_end": "97fe8fc2af1672d948f10464b2dcc5309d5ad11a",
    "upstream_end": "97fe8fc2af1672d948f10464b2dcc5309d5ad11a",
    "branch": "feat/2026-09-01-skeleton"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "SHOULD-FIX",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "file": "docs/paper/results-fill-registry.md:722",
        "text": "DG-128 cites 1150-1166, but table data is 1151-1167 and the final member is omitted."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file": "docs/paper/draft-v2-skeleton.md:122-128",
        "text": "Strict Section 2 first-use residue remains for warm-up pulses, base-two schedule, cadence, quiet trace, clock-anchor bound, quantile notation, sample standard deviation, and corpus range."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "file": "docs/paper/draft-v2-skeleton.md:501-560",
        "text": "Holm mechanics, measurement variance, directional comparison, and the direction gate are named before their plain-language build or gloss."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 3 tests in 0.475s",
          "FAILED (errors=2)",
          "FileNotFoundError: No usable temporary directory found"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'import re; m=open(\"docs/paper/round7/survival-map.md\").read(); v=open(\"docs/paper/draft-v1.md\").read().splitlines(); rs=[(int(a),int(b)) for a,b in re.findall(r\"frozen lines (\\d+)[–-](\\d+)\",m)]; c=[0]*len(v); [c.__setitem__(i-1,c[i-1]+1) for a,b in rs for i in range(a,b+1)]; print(f\"ranges={len(rs)} covered={sum(x>0 for x in c)} first={rs[0]} last={rs[-1]} missing={[i+1 for i,x in enumerate(c) if x==0]} duplicates={[i+1 for i,x in enumerate(c) if x>1]} exact={len(rs)==45 and all(x==1 for x in c)}\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ranges=45 covered=672 first=(1, 8) last=(670, 672) missing=[] duplicates=[] exact=True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ranges=45 covered=672.*exact=True"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c 'import re; from pathlib import Path; norm=lambda s: re.sub(r\"\\s+\",\" \",s.replace(\"[PREFILL_LENGTH]\",\"<P>\")).strip(); sk=Path(\"docs/paper/draft-v2-skeleton.md\").read_text().replace(\"[PREFILL_LENGTH]\",\"<P>\"); reg=Path(\"docs/paper/results-fill-registry.md\").read_text().replace(\"[PREFILL_LENGTH]\",\"<P>\"); raw=[x for x in re.findall(r\"\\[FILL:([^]]+)\\]\",sk) if x!=\"<registry-row-id>\"]; stop=[x for x in raw if any(\"STOP_FILL\" in ln and (\"| \"+x+\" \" in ln or \"[\"+x+\"]\" in ln) for ln in reg.splitlines())]; seg=[(m.group(1),sk[m.end():].split(\"[FILL:\",1)[0]) for m in re.finditer(r\"\\[FILL:([^]]+)\\]\",sk) if m.group(1) in stop]; bad=[r for r,s in seg if not (\"omitted\" in norm(s) and (\"registry row \"+r+\")\") in norm(s))]; ck=[norm(x) for x in re.findall(r\"“([^”]+)”\",Path(\"docs/paper/round7/fill-checklist.md\").read_text())]; exact=sum(any(c in norm(s) for c in ck) for r,s in seg); print(f\"placements={len(seg)} rows={len(set(stop))} local_omission_ok={len(seg)-len(bad)} checklist_exact={exact} bad={bad}\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "placements=50 rows=33 local_omission_ok=50 checklist_exact=38 bad=[]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "placements=50 rows=33 local_omission_ok=50 checklist_exact=38 bad=\\[\\]"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "grep -n '8.111070\\|7.607258' docs/paper/draft-v2-skeleton.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "546:named pessimistic scenario, not an estimate—obtaining \\(t=7.607258\\) and",
          "549:\\(t=8.111070\\), \\(p=0.0013\\). The documents differ in that dependence"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "7\\.607258.*8\\.111070"
      }
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check b1d23e41..97fe8fc2",
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
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short",
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
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 2792 tests in 109.770s",
          "FAILED (errors=1787, skipped=114)",
          "FileNotFoundError: No usable temporary directory found"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2792 tests.*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Focused and canonical unittest runs are blocked by the read-only runner's inability to create temporary directories.",
      "needs": "Rerun in a writable temporary-directory environment."
    }
  ]
}
```

## Findings

No blocker-level wrong number or physical attribution was found.

| Item | Result | Evidence |
|---|---|---|
| Blocker clause | PASS | Lines 541–550 distinguish stipulated halving, \(t=7.607258,p=.0016\), from estimated AR(1), \(n_{\rm eff}=5.76,t=8.111070,p=.0013\). |
| 1 | PASS | Lines 507–509 exclude gross repetition because its scatter is already in `se_repeat`; source excludes `GROSS_REPETITION_TERM`. |
| 2 | PASS | Lines 511–513 gloss shared covariance as measurement error moving together and cancelling in \(B-A\). |
| 3 | PASS | Line 128 explicitly gives two fresh bounds and the \(\sqrt2\) spread rule. |
| 4 | PASS | Line 128 binds \(s_b=2.460856\) ms and preserves the unrounded value. |
| 5 | PASS | Line 128 states nearest-microsecond rounding with ties to the even digit. |
| 6 | PASS | Lines 128 and 1143–1147 name the retained calibration acceptance file and registry source S17. |
| 7 | PASS | Lines 543–545 define effective sample size and the resulting \(\nu=5-1=4\). |
| 8 | PASS | Lines 553–555 pair \(2.8\times10^{-6}\) with the second illustrative raw probability \(0.041\). |
| 9 | PASS | Lines 424–428 cite `_T_CRITICAL_95[1]`, `student_t_critical_95`, detection-floor use, and artifact provenance. |
| 10 | PASS | Line 1141 gives the instrument-validation date span; table IDs run `20260722T145535` through `20260725T060617`. |
| 11 | FAIL (F1) | Registry line 722 cites `1150–1166`; line 1150 is the separator, data are `1151–1167`, and line 1167 contains the omitted final member. |
| 12 | PASS | Lines 442–443 correctly limit the printed-operand replay claim to nine significant figures. |
| 13 | PASS | Lines 558–561 forward-point to Holm as one step and the decision-interval direction gate as the other. |

F2/F3 first-use residue under a strict metrology/pedagogy reading:

| Term | First use | Gloss I would dictate |
|---|---:|---|
| warm-up pulses | 122 | “three warm-up pulses used to bring the GPU to its operating state, excluded from the measured train” |
| base-two varied-gap schedule | 122 | “a varied-gap schedule whose gaps follow a base-two progression” |
| sampler cadence | 122 | “the requested 100-ms cadence, meaning the interval between sampler records” |
| quiet trace | 122 | “a quiet power trace: sampler records collected with no commanded pulse” |
| clock-anchor bound | 124 | “the uncertainty in placing the power trace on wall-clock time” |
| 99% quantile | 128 | “the cutoff below which 99% of the Student-\(t\) distribution lies” |
| sample standard deviation \(s_b\) | 128 | “the square root of the sum of squared deviations of the 17 bounds from their mean divided by \(17-1\)” |
| \(t_{0.995,16}\) | 128 | “the Student-\(t\) cutoff at cumulative probability 0.995 with 16 degrees of freedom” |
| corpus range | 128 | “the largest corpus bound minus the smallest” |
| directional comparison | 501 | “a comparison tested against a preregistered sign, not only a two-sided difference” |
| Holm step-down correction | 502 | “order the raw probabilities, compare the smaller with 0.025, and only if it passes compare the larger with 0.05” |
| measurement variance | 507 | “the squared spread attributed to the measurement process” |
| decision-interval sign test / direction gate | 559 | “the measurement and widened decision intervals must both remain strictly on the registered side of zero” |

The covariance, effective-sample-size, AR(1), two-draw, stage/member, energy-family, interval, and deterministic-bound glosses are satisfactory. The inserted sentences remain grammatical and self-consistent; no grammar finding is warranted.

## Bench computations

The requested Student-\(t\) function imported successfully.

| Case | \(n_{\rm eff}\) | \(\nu\) | \(se_{\rm repeat}\) | \(se_{\rm total}\) | \(t\) | two-sided \(p\) |
|---|---:|---:|---:|---:|---:|---:|
| stipulated halving | 5 | 4 | 0.626099033699941 | 0.657267069006199 | 7.607257743127308 → 7.607258 | 0.001602484161945 → 0.0016 |
| AR(1), unrounded | 5.764703479529582 | 4 | 0.583095311006357 | 0.616441515245039 | 8.111069544062861 → 8.111070 | 0.001256213762446 → 0.0013 |

The literal rounded input \(n_{\rm eff}=5.764703\) gives \(t=8.111069242219303\); the printed \(8.111070\) correctly reflects the underlying unrounded AR(1) value.

Additional checks:

- Deltas: mean \(5.0\), squared-deviation sum \(17.64\), \(s=1.4\).
- Calibration corpus: \(s_b=2.460856207694636\) ms; range \(9.723589288793850\) ms; `ROUND_HALF_EVEN` gives \(9.724\) ms; two-draw value \(10.164834757777545\) ms.
- Printed ratio replay: \(8.8304376431/2.4305766103=3.6330628730974586\), supporting nine significant figures.
- Source checks pass: `aggregate.py:42` has `1: 12.706`; `detection_floor.py:696` calls `student_t_critical_95`; `:1283` records `t_critical_source`; estimators excludes `GROSS_REPETITION_TERM`.

Replayed census outputs:

```text
ranges=45 covered=672 first=(1, 8) last=(670, 672) missing=[] duplicates=[] exact=True
placements=50 rows=33 local_omission_ok=50 checklist_exact=38 bad=[]
```

The focused test and full suite failures are temporary-directory environment failures, not paper-result failures.

## Residual risk

Only the unittest runs need rerunning in a writable temporary environment.

VERDICT: SHOULD-FIX