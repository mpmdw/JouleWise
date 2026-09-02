```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Applied all dictated skeleton and DG-128 provenance corrections; every requested check passed.",
  "workspace": {
    "base_requested": "b1d23e41bcaf1a5fbb295f8f82da78cc2020f805",
    "base_mode": "exact",
    "head_start": "b1d23e41bcaf1a5fbb295f8f82da78cc2020f805",
    "head_end": "b1d23e41bcaf1a5fbb295f8f82da78cc2020f805",
    "upstream_end": null,
    "branch": "feat/2026-09-01-skeleton"
  },
  "pathspec": [
    "docs/paper/draft-v2-skeleton.md",
    "docs/paper/results-fill-registry.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
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
        "tail": ["Ran 3 tests in 0.790s", "OK"]
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
        "tail": ["ranges=45 covered=672 first=(1, 8) last=(670, 672) missing=[] duplicates=[] exact=True"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ranges=45 .*missing=\\[\\] duplicates=\\[\\] exact=True"
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
        "tail": ["placements=50 rows=33 local_omission_ok=50 checklist_exact=38 bad=[]"]
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
        "tail": ["545:named pessimistic scenario, not an estimate—obtaining \\(t=7.607258\\) and", "548:\\(t=8.111070\\), \\(p=0.0013\\). The documents differ in that dependence"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "7\\.607258.*8\\.111070"
      }
    },
    {
      "id": "V5",
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
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [" M docs/paper/draft-v2-skeleton.md", " M docs/paper/results-fill-registry.md"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "draft-v2-skeleton\\.md.*results-fill-registry\\.md"
      }
    }
  ],
  "flags": []
}
```

## Change

- Blocker (`draft-v2-skeleton.md:542–549`) → correctly separates stipulated \(n_\mathrm{eff}=5\) halving from the estimated AR(1) \(n_\mathrm{eff}=5.76\) result.
- Items 1–2 (`:507–512`) → adds variance-term, gross-repetition, and covariance-cancellation glosses.
- Items 3–6 (`:128`, `:1140–1146`) → restores \(s_b\), the \(\sqrt2\) reason, rounding rule, and full S17 file attribution.
- Items 9 and 12 (`:425–428`, `:442–444`) → corrects the 12.706 provenance and limits replay agreement to nine significant figures.
- Items 8 and 13 (`:553–560`) → repairs the second illustrative probability wording and distinguishes Holm from the direction gate.
- Items 10–11 (`:1140–1166`; registry `:722`) → corrects the capture-date heading and points DG-128 to the table’s 17 data rows.