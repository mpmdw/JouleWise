```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "All authorized skeleton fixes and checks are complete, except a lead ruling is needed because the dictated t=10.2924 does not replay from its operands.",
  "workspace": {
    "base_requested": "cc52daab2e4d8c045eb2b2938f56b78eda3ed94b",
    "base_mode": "exact",
    "head_start": "cc52daab2e4d8c045eb2b2938f56b78eda3ed94b",
    "head_end": "cc52daab2e4d8c045eb2b2938f56b78eda3ed94b",
    "upstream_end": null,
    "branch": "feat/2026-09-01-skeleton"
  },
  "pathspec": [
    "docs/paper/draft-v2-skeleton.md",
    "docs/paper/results-fill-registry.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 3 tests in 0.755s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "python3 scripts/paper_terms_lint.py lexicon --draft docs/paper/draft-v2-skeleton.md --out /dev/null",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["444 terms; wrote /dev/null"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "[0-9]+ terms; wrote /dev/null"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c 'import re; m=open(\"docs/paper/round7/survival-map.md\").read(); v=open(\"docs/paper/draft-v1.md\").read().splitlines(); rs=[(int(a),int(b)) for a,b in re.findall(r\"frozen lines (\\d+)[–-](\\d+)\",m)]; c=[0]*len(v); [c.__setitem__(i-1,c[i-1]+1) for a,b in rs for i in range(a,b+1)]; print(f\"ranges={len(rs)} covered={sum(x>0 for x in c)} first={rs[0]} last={rs[-1]} missing={[i+1 for i,x in enumerate(c) if x==0]} duplicates={[i+1 for i,x in enumerate(c) if x>1]} exact={len(rs)==45 and all(x==1 for x in c)}\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ranges=45 covered=672 first=(1, 8) last=(670, 672) missing=[] duplicates=[] exact=True"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ranges=45 .* missing=\\[\\] duplicates=\\[\\] exact=True"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -c 'import re; from pathlib import Path; norm=lambda s: re.sub(r\"\\s+\",\" \",s.replace(\"[PREFILL_LENGTH]\",\"<P>\")).strip(); sk=Path(\"docs/paper/draft-v2-skeleton.md\").read_text().replace(\"[PREFILL_LENGTH]\",\"<P>\"); reg=Path(\"docs/paper/results-fill-registry.md\").read_text().replace(\"[PREFILL_LENGTH]\",\"<P>\"); raw=[x for x in re.findall(r\"\\[FILL:([^]]+)\\]\",sk) if x!=\"<registry-row-id>\"]; stop=[x for x in raw if any(\"STOP_FILL\" in ln and (\"| \"+x+\" \" in ln or \"[\"+x+\"]\" in ln) for ln in reg.splitlines())]; seg=[(m.group(1),sk[m.end():].split(\"[FILL:\",1)[0]) for m in re.finditer(r\"\\[FILL:([^]]+)\\]\",sk) if m.group(1) in stop]; bad=[r for r,s in seg if not (\"omitted\" in norm(s) and (\"registry row \"+r+\")\") in norm(s))]; ck=[norm(x) for x in re.findall(r\"“([^”]+)”\",Path(\"docs/paper/round7/fill-checklist.md\").read_text())]; exact=sum(any(c in norm(s) for c in ck) for r,s in seg); print(f\"placements={len(seg)} rows={len(set(stop))} local_omission_ok={len(seg)-len(bad)} checklist_exact={exact} bad={bad}\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["placements=50 rows=33 local_omission_ok=50 checklist_exact=38 bad=[]"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "placements=50 rows=33 local_omission_ok=50 checklist_exact=38 bad=\\[\\]"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "printf 'head='; git show HEAD:docs/paper/draft-v2-skeleton.md | grep -c illustrative; printf 'worktree='; grep -c illustrative docs/paper/draft-v2-skeleton.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["head=1", "worktree=3"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "head=1.*worktree=[2-9]"
      }
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["(no output)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^\\(no output\\)$"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git status --short; git diff --name-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/paper/draft-v2-skeleton.md",
          " M docs/paper/results-fill-registry.md",
          "docs/paper/draft-v2-skeleton.md",
          "docs/paper/results-fill-registry.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "draft-v2-skeleton.md.*results-fill-registry.md"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "PED-R6-01 dictates t=10.2924, but the stated operands and the repository Student-t implementation give t=10.2923371, which rounds to 10.2923 at four decimal places. The draft contains the source-backed 10.2923.",
      "needs": "Rule whether 10.2923 is ratified or whether the draft must print the non-replaying dictated value 10.2924."
    }
  ]
}
```

## Change

Implemented the Student-\(t\) and allowance first-use glosses, calibration sufficient statistics, 17-bound appendix table, two-block critical and fixture provenance, component standard-error estimators, ten-block direction fixture, completed Holm example, and dependence-sensitivity cross-reference.

Added registry row DG-128 with the required S17 source and corpus-doubling regeneration note. The survival map was unchanged because neither it nor the registry contains a relevant “36 exact placements” census line; V4 confirms the correct count is 38. The frozen `draft-v1.md` was untouched.

| Item | Draft lines | Replay result | Bench evidence |
|---|---:|---|---|
| PED-FU-01 | 128 | Identifies what the quantile sets and why it exceeds the normal quantile. | B1 reproduces the \(n=17\) statistics. |
| PED-FU-02 | 132, 465–468 | Defines both allowance operands and their reference runs consistently. | Direct text inspection; no numeric inference required. |
| PED-FU-03 | 499–522 | Prints \(d_i\), both component estimators, their combination, and 9 df before testing. | B3 computes all components. |
| PED-R1-01 | 128, 1127–1151 | Table matches all 17 S17 strings; sd, range, and rounded screen replay. | B1 output below. |
| PED-R2-01 | 423–442 | The authenticated fixture plus \(t_{0.975,1}=12.706\) reproduces both bounds and \(R_{cm}\). | B2 output below. |
| PED-R6-01 | 523–557 | Reproduces \(s\), both standard errors, \(t\), raw \(p\), and completed Holm decisions. | B3 output below; exposes the ruling conflict. |
| REG-COUNT-01 | — | Census is 38 exact placements. | V4. |
| REG-HUNK-01 | — | No draft change, as ruled. | Diff inspection. |

B1:

```sh
python3 -c 'from decimal import Decimal as D,ROUND_HALF_EVEN as H,getcontext; import json,re; getcontext().prec=50; j=json.load(open("configs/calibration/calibration_acceptance_d079_v2_n17_r3.json")); src=[(m["member_id"],m["b_fiducial_s"]) for m in j["derivation_corpus"]["members"]]; x=[D(v) for _,v in src]; m=sum(x)/D(len(x)); s=(sum((v-m)**2 for v in x)/D(len(x)-1)).sqrt(); r=max(x)-min(x); text=open("docs/paper/draft-v2-skeleton.md").read(); q=chr(96); tab=re.findall(rf"^\| {q}([^{q}]+){q} \| ([0-9.]+) \|$",text,re.M)[-17:]; print(f"table={tab==src} n={len(x)} sd_ms={s*1000:.15f} replay_ms={D(\"2.92078162\")*D(\"2.460856\")*D(\"1.41421356\")} range_ms={r*1000} rounded_ms={r.quantize(D(\"0.000001\"),rounding=H)*1000}")'
```

```text
table=True n=17 sd_ms=2.460856207694636 replay_ms=10.1648338743755264807232 range_ms=9.72358928879385000 rounded_ms=9.724000
```

B2:

```sh
python3 -c 'from itertools import product; from math import sqrt; from tests.test_detection_floor import TestTwoSharedEdgeCommonModeFloor as F; d=F.REPLAY_DELTAS[:2]; q=F.REPLAY_SHARED_WIDTHS[:2]; l=F.REPLAY_LOCAL_WIDTHS[:2]; B=lambda v:max(max(map(abs,v)),abs(sum(v)/2)+12.706*abs(v[0]-v[1])/sqrt(2)*sqrt(1.5)); p=B(d); s=max(B([d[i]+a*q[i]+e[i]*l[i] for i in range(2)]) for a in (-1,1) for e in product((-1,1),repeat=2)); print(f"tcrit=12.706 point={p:.10f} shared={s:.10f} ratio={s/p:.10f}")'
```

```text
tcrit=12.706 point=2.4305766103 shared=8.8304376431 ratio=3.6330628732
```

B3:

```sh
python3 -c 'from math import sqrt; from joulewise.analysis_engine.distributions import two_sided_student_t_p_value as P; d=[5.0,7.6,5.5,4.2,4.7,6.8,5.5,3.6,3.9,3.2]; m=sum(d)/10; ss=sum((x-m)**2 for x in d); s=sqrt(ss/9); r=s/sqrt(10); z=sqrt(r*r+.2**2); t=m/z; p=P(t,9); print(f"mean={m:.1f} ss={ss:.2f} s={s:.1f} se_repeat={r:.9f} se_total={z:.9f} t={t:.7f} p={p:.8g} Holm={p:.2g}<.025_then_.041<.05")'
```

```text
mean=5.0 ss=17.64 s=1.4 se_repeat=0.442718872 se_total=0.485798312 t=10.2923371 p=2.8137597e-06 Holm=2.8e-06<.025_then_.041<.05
```

## Verification notes

The first V3/V4 wrapper invocation over-escaped the regular expressions. The exact report-36 commands were then rerun verbatim and passed, as recorded above.

## Residual risk

Lead ruling is required on the PED-R6-01 last digit. All other requested work is complete and source-backed.