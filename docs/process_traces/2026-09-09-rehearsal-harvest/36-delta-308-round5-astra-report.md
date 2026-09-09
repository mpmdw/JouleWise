```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Round-5 delta closes F1–F4 and S-A/S-C; artifact counts and kernel projections agree; same signature: none.",
  "workspace": {
    "base_requested": "2aae25f69a6be0b11465129e353d1a27eb63c4cb",
    "base_mode": "descendant",
    "head_start": "5d13d0e6079a283fbfa54af30d733bf079d77b07",
    "head_end": "5d13d0e6079a283fbfa54af30d733bf079d77b07",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 0},
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse fix/2026-09-09-night-gate-stub-chain",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["5db38b5816bce05b67cabfe3eb621bf2b22aa3e6"]},
      "expected": {"exit_code": 0, "tail_regex": "5db38b5816bce05b67cabfe3eb621bf2b22aa3e6"}
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "python3 -B scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -B -c 'from pathlib import Path; import hashlib,json; p=Path(\"docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/night-harvest\"); rows=[l.split(None,1) for l in (p/\"SHA256SUMS\").read_text().splitlines()]; assert all(hashlib.sha256((p/n).read_bytes()).hexdigest()==h for h,n in rows); names=[n for h,n in rows]; print(\"SHA256SUMS: %d/%d OK\"%(len(rows),len(rows))); print(\"night/ record copies:\",sum(n.startswith(\"night-\") for n in names)); print(\"other manifest entries:\",\", \".join(n for n in names if not n.startswith(\"night-\"))); k=json.loads(Path(\"docs/process/state_kernel.json\").read_text()); note=k[\"tasks\"][\"NIGHT-GATE-STUB-CHAIN-01\"][\"status_note\"]; rows=[(i,l) for i,l in enumerate(Path(\"TASK_QUEUE.md\").read_text().splitlines(),1) if l.startswith(\"| A168 | NIGHT-GATE-STUB-CHAIN-01 |\")]; assert len(rows)==2 and all(l.split(\" Note: \",1)[1].removesuffix(\" |\")==note for i,l in rows); print(\"status_note verbatim: TASK_QUEUE.md:\"+\",\".join(str(i) for i,l in rows))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "SHA256SUMS: 17/17 OK",
          "night/ record copies: 14",
          "other manifest entries: night.log, night_plan.json, pre-uninstall-observations.txt",
          "status_note verbatim: TASK_QUEUE.md:782,942"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "status_note verbatim: TASK_QUEUE.md:782,942"}
    }
  ],
  "flags": []
}
```

## Findings

None. Reviewed only the requested four-file delta and its supporting evidence.

1. **F1 / S-A — closed.** `NIGHT_HANDBACK.md:83` and harvest record `21i:84` name `5db38b58`, PR #309. The branch resolves to:
   ```text
   5db38b5816bce05b67cabfe3eb621bf2b22aa3e6
   ```
   `rg -n 'bb7090e2|5db38b58'` across all four documents found `bb7090e2` only as **initial cure** in `state_kernel.json:3263` and `TASK_QUEUE.md:782,942`. No occurrence presents it as the head under review.

2. **F2 / S-C — closed.** Replacement at `NIGHT_HANDBACK.md:86–88`:
   > The standing rules below are unchanged. RECORD: harvest, uninstall and removal for this night are complete; no next plan is armed; §Purpose, §Where the results are and §Next lane describe the completed night (this file's history holds no separate between-nights template text; whether one should exist is referred to the cold gate, not decided here).

   **No word rules.** “Should” occurs inside an unresolved question; “is referred” records its disposition. There is no actor assignment, future obligation, or new rule.

3. **F3 — closed.** Manifest lines 1–14 enumerate the fourteen `night-` record copies; lines 15–17 enumerate `night.log`, `night_plan.json`, and `pre-uninstall-observations.txt`. Recomputed hashes:
   ```text
   SHA256SUMS: 17/17 OK
   night/ record copies: 14
   other manifest entries: night.log, night_plan.json, pre-uninstall-observations.txt
   ```
   Thus the copied custody files number **16**; the observation file makes **17 manifest entries**. Separately, `uninstall-output.txt:7–8` records:
   ```text
   == custody root untouched?
         17
   ```
   Revised `21i:56` correctly distinguishes that raw count and acknowledges its uncaptured counting command.

4. **F4 — closed.** `21i:78` agrees with `git show 5db38b58:joulewise/night_gate.py`, lines 1044–1050:
   ```text
   rows["C5"].measured.update(
   ...
   "chain_sha256": None,
   "expected_chain_sha256": None,
   "chain_stub": "built_in_stub_by_design",
   ```
   The value belongs in C5 `measured`, not a `basis` field.

5. **Kernel/projection — passed.** `python3 -B scripts/gen_state.py --check` returned **0**, with empty output. Exact extracted-note comparison returned:
   ```text
   status_note verbatim: TASK_QUEUE.md:782,942
   ```

**same signature: none** within the requested four-document delta and checked facts.

No edits; HEAD remained `5d13d0e6`, detached and clean. Next step: lead final disposition of this delta.

## Residual risk

This audit verifies committed documentation, artifact bytes, and cure-source representation—not live hardware behavior or current remote PR status. The source counting command remains unavailable. No full suite was needed for this documentation-only delta.

An initial heredoc inspection failed because the read-only sandbox prohibited its temporary file; the equivalent `python3 -B -c` inspection then passed.