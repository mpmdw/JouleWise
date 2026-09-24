```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All 14 FT clauses are present, but the checker brief has two blockers and several contract and representation defects.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "7335114385927fb93645b5a5542b67951560c41b",
    "head_end": "7335114385927fb93645b5a5542b67951560c41b",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "blocker", "title": "02c plus 25 are not self-contained for the independent checker"},
      {"id": "F2", "severity": "blocker", "title": "RD-6 cannot call the ruled verification signature"},
      {"id": "F3", "severity": "should_fix", "title": "INV-50 tests less than the ruled model-order requirement"},
      {"id": "F4", "severity": "should_fix", "title": "RD-8 adds a mandatory witness column beyond the ruled path list"},
      {"id": "F5", "severity": "should_fix", "title": "RD-13 narrows the accepted registration domain"},
      {"id": "F6", "severity": "should_fix", "title": "A superseded drift-key spelling survives and Q12 precedence is only abbreviated"},
      {"id": "F7", "severity": "should_fix", "title": "Violation fields and composite refusal codes conflict or remain unspecified"},
      {"id": "F8", "severity": "nit", "title": "Q3 blocks-per-cell sentence is represented by a formula rather than installed verbatim"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 - <<'PY'\nfrom pathlib import Path\nimport re\np=Path('docs/process_traces/2026-09-24-activation-a65fb4fa')\nc=(p/'02c-a291-contract-v3-ruled.md').read_text()\nfor name,rel,pattern in [('FT','15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md',r'^\\*\\*(FT-\\d+) .*?\\*\\* \"(.*)\"$'),('Q','15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md',r'^\\*\\*(Q\\d+) .*?\\*\\*.*?(?:Text|Ruled text): \\*\"(.*)\"\\*')]:\n rows=[m.groups() for x in (p/rel).read_text().splitlines() if (m:=re.match(pattern,x))]\n missing=[(n,s) for n,t in rows for s in re.split(r'(?<=\\.) (?=[A-Z`(]|INV-|\\()|; ',t) if len(s)>=45 and s not in c]\n print(name,'rows',len(rows),'missing_clause_ids',sorted(set(n for n,_ in missing)))\nprint('paths',len(re.findall(r'^\\| `(P|E\\d+|R)` \\|',c,re.M)))\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "FT rows 14 missing_clause_ids []",
          "Q rows 18 missing_clause_ids ['Q12', 'Q3', 'Q4', 'Q7', 'Q8', 'Q9']",
          "paths 13"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "FT rows 14 missing_clause_ids \\[\\]"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "## HEAD \\(no branch\\)"}
    }
  ],
  "flags": []
}
```

## Findings

**F1 — BLOCKER.** An independent checker cannot implement every specified row from 02c plus 25 alone. [02c §2.1](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/02c-a291-contract-v3-ruled.md:325) delegates the registration’s full key set and types to 02b; [§2.4–2.7](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/02c-a291-contract-v3-ruled.md:356) likewise delegates block types, envelope consistency, terminal-refusal fields, and digest details. [§4](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/02c-a291-contract-v3-ruled.md:409) leaves CONSUMED fields and some constant values in 02b/AP-5M. Q16 expressly assigns replay verification to `verify_executed_roster`, so that exception should remain explicit. **Fix:** inline the referenced schemas, domains, constants, and checker return rules into 02c, and identify INV-39’s Q16 verification route as its explicit exception to independent checker implementation.

**F2 — BLOCKER.** [RD-6](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/25-a291-residual-details-rulings.md:10) defines `executed_status(registration, roster, captured_window_keys)` and says it first calls `verify_executed_roster`. The latter’s ruled Q16 signature requires `predicted_decode_s`, as [02c INV-39](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/02c-a291-contract-v3-ruled.md:308) states. The implementer must choose an undeclared source for that argument. **Fix:** add `predicted_decode_s` to `executed_status` and specify that it passes the value unchanged to `verify_executed_roster`.

**F3 — MATERIAL.** [INV-50’s predicate](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/02c-a291-contract-v3-ruled.md:162) checks only that `pack` is invariant to mapping insertion order. A packer that always uses **1.7B first** would pass while violating FT-6’s explicit **8B first** rule. **Fix:** check the actual role-derived iteration and tie-break order, including the root placement order; retain the insertion-order permutation witness as an additional check. Authority: addendum §3 FT-6.

**F4 — MATERIAL for the cold gate.** [RD-8](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/25-a291-residual-details-rulings.md:12) adds a mandatory violating witness for *every* row in `requeue_all_keep`. FT-1 fixes eleven edges and thirteen paths; FT-4 imposes the all-cell rule on those paths. An additional all-keep test is useful, but a new mandatory matrix column changes the gate criterion rather than merely representing data. **Fix:** seek cold-gate adoption of the supplementary mandatory column, or describe it as an additional non-gating test. Authority: addendum §3 FT-1 and FT-4; [02c path list](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/02c-a291-contract-v3-ruled.md:46).

**F5 — MATERIAL for the cold gate.** [RD-13](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/25-a291-residual-details-rulings.md:17) rejects model IDs containing `:`, although the inherited registration domain accepts distinct non-empty strings. This narrows accepted registrations; Q4’s ID construction and FT-7’s ten keys do not themselves impose that refusal. **Fix:** remove the new rejection, or have the cold gate explicitly authorize the domain restriction and its code. Authority: ruling-10 Q4; addendum §3 FT-7; [02c §2.1](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/02c-a291-contract-v3-ruled.md:323).

**F6 — MATERIAL.** [INV-27](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/02c-a291-contract-v3-ruled.md:243) still quotes the superseded `planned_drift_lever_slots` spelling before correcting it in the next quote. [§6](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/02c-a291-contract-v3-ruled.md:439) abbreviates Q12’s explicit rule that a level with both `spread_exceeded` and `drift_exceeded` records both NR reasons. **Fix:** put only `drift_lever_slots` in the operative INV-27 sentence and paste Q12’s full precedence sentence into §6. Authority: addendum §3 FT-7; ruling-10 Q12.

**F7 — MATERIAL.** [02c’s checker interface](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/02c-a291-contract-v3-ruled.md:392) names `Violation.inv`; [RD-12](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/25-a291-residual-details-rulings.md:16) names `inv_id` and adds `code`. [RD-10](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/25-a291-residual-details-rulings.md:14) does not determine the fallback code for the composite INV-33/43 row or every INV-35 subrule; it explicitly settles only `inv_35c`. **Fix:** publish one exact `Violation` field set and a code table for composite and lettered rows. Keep `unattributed_overrun` identified as a terminal-refusal type, so its appearance in RD-10 cannot be read as permission to raise on FT-1’s no-culprit outcome. Authority: ruling-10 Q15; addendum §3 FT-1, FT-2, FT-4; [02c INV-33/43 and INV-35](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/02c-a291-contract-v3-ruled.md:281).

**F8 — NIT.** Q3’s sentence “Blocks per cell := `ceil(n / block_size[arm])`” is absent verbatim, although [02c’s `bpc` definition](/Users/edr/code/wt-a65fb4fa-lens4/docs/process_traces/2026-09-24-activation-a65fb4fa/02c-a291-contract-v3-ruled.md:85) gives the same formula. **Fix:** add the ruled sentence beside `bpc`. Authority: ruling-10 Q3.

The scripted comparison found all **14 FT clauses** verbatim in 02c, sometimes divided among rows. It found **13 paths: pack, eleven edges, reduce**. For Q1–Q20, Q4(iii), Q7, Q8’s seal sentence, and Q9’s final sentence are absent as expected because later FT text supersedes them; Q18 is an authority ruling rather than a quoted implementation clause, and Q20’s replay amendment is superseded by FT-8. Apart from F6 and F8, I found no missing operative Q clause or surviving old INV-35 bound.

RD-1–5, RD-7, RD-9, RD-11, and RD-14 read as representation choices consistent with the cited rulings. RD-6 is blocked by F2; RD-8 and RD-13 need cold-gate visibility; RD-10 and RD-12 need the schema repair in F7.

## Residual risk

This was a read-only contract review. No packer code, generated roster, or live reducer was executed; Q16 already marks the A291 reduce-column witnesses PROVISIONAL until A292 reruns them at its real entry.