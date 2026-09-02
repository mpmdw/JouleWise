```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Registration and partition checks pass, but strict first-use and draft-only replication gaps remain.",
  "workspace": {
    "base_requested": "913cd59db7a153f1946ff835453cba1c5129362f",
    "base_mode": "exact",
    "head_start": "913cd59db7a153f1946ff835453cba1c5129362f",
    "head_end": "cc52daab2e4d8c045eb2b2938f56b78eda3ed94b",
    "upstream_end": "832a5ce30f46c61c7f5c0817b15eccbc924c4abf",
    "branch": "feat/2026-09-01-skeleton"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "SHOULD-FIX",
    "findings": [
      {"id":"PED-FU-01","severity":"should_fix","path":"docs/paper/draft-v2-skeleton.md","line":128,"summary":"Student-t is used before its distribution/quantile meaning is built; that definition arrives at line 257."},
      {"id":"PED-FU-02","severity":"should_fix","path":"docs/paper/draft-v2-skeleton.md","line":132,"summary":"Reference-run trajectory excursion and issued repeatability bound are used before their physical definitions at lines 461-464."},
      {"id":"PED-FU-03","severity":"should_fix","path":"docs/paper/draft-v2-skeleton.md","line":498,"summary":"Total standard error and metrology scatter lack an estimator and physical source at first use."},
      {"id":"PED-R1-01","severity":"should_fix","path":"docs/paper/draft-v2-skeleton.md","line":128,"summary":"The 17-capture corpus constants cannot be derived from the draft because corpus values, statistics, quantile, and rounding rule are absent."},
      {"id":"PED-R2-01","severity":"should_fix","path":"docs/paper/draft-v2-skeleton.md","line":423,"summary":"Shared/local replay is only conditional: t_.975,1 and block-2 source operands are not printed."},
      {"id":"PED-R6-01","severity":"should_fix","path":"docs/paper/draft-v2-skeleton.md","line":494,"summary":"The direction test gives no ten block differences, standard-error inputs, statistic, or resulting p-values."},
      {"id":"REG-COUNT-01","severity":"nit","path":"docs/paper/draft-v2-skeleton.md","line":41,"summary":"Mechanical STOP_FILL census finds 50 placements, 33 rows, and 38 checklist-exact placements, not the fixer's claimed 36."},
      {"id":"REG-HUNK-01","severity":"nit","path":"docs/paper/draft-v2-skeleton.md","line":209,"summary":"The clipping-example hunk, also mapped at survival-map.md:176, is not named in the fixer table; it introduces no semantic defect."}
    ]
  },
  "verification": [
    {"id":"V1","kind":"test","cmd":"python3 -m unittest tests.test_paper_terms_lint","cwd":".","observed":{"result":"not_run","exit_code":1,"tail":["FileNotFoundError: [Errno 2] No usable temporary directory found","FAILED (errors=2)"]},"expected":{"exit_code":0,"tail_regex":"Ran 3 tests.*OK"}},
    {"id":"V2","kind":"lint","cmd":"python3 scripts/paper_terms_lint.py lexicon --draft docs/paper/draft-v2-skeleton.md --out /dev/null","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["437 terms; wrote /dev/null"]},"expected":{"exit_code":0,"tail_regex":"437 terms; wrote /dev/null"}},
    {"id":"V3","kind":"inspection","cmd":"python3 -c 'import re; m=open(\"docs/paper/round7/survival-map.md\").read(); v=open(\"docs/paper/draft-v1.md\").read().splitlines(); rs=[(int(a),int(b)) for a,b in re.findall(r\"frozen lines (\\d+)[–-](\\d+)\",m)]; c=[0]*len(v); [c.__setitem__(i-1,c[i-1]+1) for a,b in rs for i in range(a,b+1)]; print(f\"ranges={len(rs)} covered={sum(x>0 for x in c)} first={rs[0]} last={rs[-1]} missing={[i+1 for i,x in enumerate(c) if x==0]} duplicates={[i+1 for i,x in enumerate(c) if x>1]} exact={len(rs)==45 and all(x==1 for x in c)}\")'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["ranges=45 covered=672 first=(1, 8) last=(670, 672) missing=[] duplicates=[] exact=True"]},"expected":{"exit_code":0,"tail_regex":"ranges=45 .*missing=\\[\\] duplicates=\\[\\] exact=True"}},
    {"id":"V4","kind":"inspection","cmd":"python3 -c 'import re; from pathlib import Path; norm=lambda s: re.sub(r\"\\s+\",\" \",s.replace(\"[PREFILL_LENGTH]\",\"<P>\")).strip(); sk=Path(\"docs/paper/draft-v2-skeleton.md\").read_text().replace(\"[PREFILL_LENGTH]\",\"<P>\"); reg=Path(\"docs/paper/results-fill-registry.md\").read_text().replace(\"[PREFILL_LENGTH]\",\"<P>\"); raw=[x for x in re.findall(r\"\\[FILL:([^]]+)\\]\",sk) if x!=\"<registry-row-id>\"]; stop=[x for x in raw if any(\"STOP_FILL\" in ln and (\"| \"+x+\" \" in ln or \"[\"+x+\"]\" in ln) for ln in reg.splitlines())]; seg=[(m.group(1),sk[m.end():].split(\"[FILL:\",1)[0]) for m in re.finditer(r\"\\[FILL:([^]]+)\\]\",sk) if m.group(1) in stop]; bad=[r for r,s in seg if not (\"omitted\" in norm(s) and (\"registry row \"+r+\")\") in norm(s))]; ck=[norm(x) for x in re.findall(r\"“([^”]+)”\",Path(\"docs/paper/round7/fill-checklist.md\").read_text())]; exact=sum(any(c in norm(s) for c in ck) for r,s in seg); print(f\"placements={len(seg)} rows={len(set(stop))} local_omission_ok={len(seg)-len(bad)} checklist_exact={exact} bad={bad}\")'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["placements=50 rows=33 local_omission_ok=50 checklist_exact=38 bad=[]"]},"expected":{"exit_code":0,"tail_regex":"placements=50 rows=33 local_omission_ok=50 checklist_exact=38 bad=\\[\\]"}},
    {"id":"V5","kind":"inspection","cmd":"python3 -c 'import re,random; m=open(\"docs/paper/round7/survival-map.md\").read().splitlines(); v=open(\"docs/paper/draft-v1.md\").read().splitlines(); ps=[]\\nfor line in m:\\n q=re.search(r\"frozen lines (\\d+)[–-](\\d+)\",line)\\n if q:\\n  a,b=map(int,q.groups()); title=line.split(\" — frozen lines\",1)[0].lstrip(\"# \").strip(); hs=[re.sub(r\"^#+\\s*\",\"\",x).strip() for x in v[a-1:min(b,a+3)] if x.lstrip().startswith(\"#\")]; ps.append((title,hs))\\np=random.Random(20260901).sample(ps,5); print(f\"sampled={len(p)} heading_matches={sum(title in hs for title,hs in p)}\")'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["sampled=5 heading_matches=5"]},"expected":{"exit_code":0,"tail_regex":"sampled=5 heading_matches=5"}},
    {"id":"V6","kind":"inspection","cmd":"git show feat/d165-dominance-closeout-core:joulewise/dominance_closeout.py | sed -n '1293,1318p'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["if source_errors or refused:","\"branch\": None,","branch = \"A\" if all_independent and all_common else \"B\"","\"dominance_sentence_licensed\": licensed"]},"expected":{"exit_code":0,"tail_regex":"branch = .*all_independent.*all_common"}},
    {"id":"V7","kind":"inspection","cmd":"git diff --check HEAD^ HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["(no output)"]},"expected":{"exit_code":0,"tail_regex":"^\\(no output\\)$"}}
  ],
  "flags": [
    {"id":"F1","kind":"environment","level":"nonblocking","text":"The requested unittest could not create a usable temporary directory; its result was skipped as environment-blocked.","needs":"Rerun in a writable-temp environment."},
    {"id":"F2","kind":"residual_risk","level":"nonblocking","text":"No measurement was run; campaign-value absence was checked statically as required.","needs":""}
  ]
}
```

## Findings

### A. Pedagogy

| ID | severity | file:line | What fails | What would cure it |
|---|---|---|---|---|
| PED-FU-01 | should-fix | `draft-v2-skeleton.md:128` | “Student-\(t\)” is introduced with a result amount, but not explained as a small-sample distribution or quantile until line 257. | Add a plain gloss at line 128, or move the bracket derivation after the definition. |
| PED-FU-02 | should-fix | `draft-v2-skeleton.md:132` | Figure 2 uses “reference-run trajectory excursion” and “issued repeatability bound” as operands before their definitions in Section 4. | Define both quantities inline before Figure 2 uses them, or defer that sentence. |
| PED-FU-03 | should-fix | `draft-v2-skeleton.md:498` | “Total standard error” and “metrology scatter” do not state their physical sources or combination rule. | Give the component estimators and exact variance/standard-error combination before the direction test. |
| PED-R1-01 | should-fix | `draft-v2-skeleton.md:128` | The worked 25/29-ms bracket reproduces \(b=38.724\) ms and the pass/fail comparison, but not \(10.164834757777545\) ms or \(9.724\) ms from the stated 17-capture corpus. | Print the corpus differences or sufficient statistics, the 99% quantile, and the rounding rule. |
| PED-R2-01 | should-fix | `draft-v2-skeleton.md:423-436` | The supplied \(\delta_1,q_1,\ell_1,\delta_2,q_2,\ell_2\) allow the sign sweep, but strict draft-only replay lacks \(t_{.975,1}\) and the source values behind block 2’s \(q_2,\ell_2\). Using the code’s \(t_{.975,1}=12.706\) reproduces the printed \(U_{\mathrm{cmp}}\) values; that is not draft-only replication. | Print the critical value and either the block-2 source sweep/local widths or explicitly mark \(q_2,\ell_2\) as authenticated fixture inputs. |
| PED-R6-01 | should-fix | `draft-v2-skeleton.md:494-506` | The text specifies ten blocks, a Student-\(t\) test, and Holm thresholds, but supplies no ten differences, standard-error inputs, statistic, or actual p-values. | Add a complete numeric ten-block fixture and its test calculation. |

The remaining B-FU rows are physically built, glossed, or absent; B-R3–R5 and B-R7–R9 also pass. B-FU-06 passes only under the ledger’s explicit build-note exception.

### B. Registration

The three close-out dispositions pass the requested comparison. A requires all eight independent and four comparative ratios to be at least 2; B requires every ratio to be authenticated/evaluable with at least one below 2; refusal selects neither branch and stops filling. This matches `_expected_global_fields`.

| ID | severity | file:line | What fails | What would cure it |
|---|---|---|---|---|
| REG-COUNT-01 | nit | `draft-v2-skeleton.md:41,64` | All 50 STOP_FILL placements across 33 rows have local row-specific omission text; none is generic or absent. The mechanical checklist comparison is 38 exact placements, not the fixer’s 36, because the DS-29 and PG-05 abstract placements are also exact checklist sentences. | Correct the fixer’s count, or state the exclusion rule producing 36. |

The survival map passes: 45 ranges cover frozen `draft-v1.md` lines 1–672 exactly once. Five seeded random references also matched their frozen headings: lines 354–359, 9–12, 400–405, 664–669, and 417–422.

No campaign result value was introduced. Numeric examples are labeled diagnostic, pilot, synthetic, retained, or fixed protocol constants; the retained 37-of-50 negative is explicitly historical and non-claim-bearing.

### C. Regression

HEAD is the two-file terra fix round (`cc52daab`), with a clean tree. All diff hunks except the following are traceable to named B-FU/B-R/B-O, A-F, ledger, or map-support findings.

| ID | severity | file:line | What fails | What would cure it |
|---|---|---|---|---|
| REG-HUNK-01 | nit | `draft-v2-skeleton.md:209`; `survival-map.md:176` | Adds a worked 30-W record-clipping example. The fixer report does not name this hunk, although the survival map now requires it. It introduces no undefined term, contradiction, or broken cross-reference. | Add the hunk to the fixer’s traceability table, or leave it documented as map-mandated support. |

Five random frozen-line references remained aligned, and `git diff --check HEAD^ HEAD` passed.

## Replication attempts

1. Timing bracket: \(25\) ms and \(29\) ms give a \(4\)-ms difference, pass \(10.164835\) ms, and produce \(b=38.724\) ms. The two policy constants themselves cannot be rebuilt from the draft.

2. Shared/local split: The printed \(\delta_1,q_1,\ell_1,\delta_2,q_2,\ell_2\) support the \(2\times2^2\) sign enumeration. With the code’s external \(t_{.975,1}=12.706\), the printed \(2.4305766103\)-J point bound, \(8.8304376431\)-J shared bound, and \(R_{cm}=3.6330628732\) replay. Strict draft-only replication is incomplete.

3. Direction test: The draft supplies the ten-block count, null, Student-\(t\) degrees of freedom, and Holm thresholds, but no ten-block values or standard-error inputs. The actual statistic and p-values cannot be computed.

## Residual risk

The requested unit test remains environment-blocked by the unavailable writable temporary directory. No live or quiet-window measurement was performed.

VERDICT: SHOULD-FIX — the close-out and safety partition are sound, but strict pedagogy and replication requirements still fail at the bracket, Figure 2 operands, shared/local fixture, and direction-test inputs.