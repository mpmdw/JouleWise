```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Distilled the seven process lessons and installed only the additive doctrine that belongs in the repository playbook and orchestration guide.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-skill-distill"
  },
  "pathspec": [
    "docs/agent_playbook.md",
    "docs/orchestration.md",
    "docs/process_traces/2026-09-04-fanout/skill-distill/01-sol-report.md",
    "docs/process_traces/2026-09-04-fanout/skill-distill/02-lessons.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "lint",
      "cmd": "git diff --check -- docs/agent_playbook.md docs/orchestration.md docs/process_traces/2026-09-04-fanout/skill-distill/01-sol-report.md docs/process_traces/2026-09-04-fanout/skill-distill/02-lessons.md && echo DIFF-CHECK-OK",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["DIFF-CHECK-OK"]},
      "expected": {"exit_code": 0, "tail_regex": "DIFF-CHECK-OK"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'import pathlib,re,sys; fs=[pathlib.Path(\"docs/orchestration.md\"),pathlib.Path(\"docs/agent_playbook.md\"),pathlib.Path(\"docs/process_traces/2026-09-04-fanout/skill-distill/02-lessons.md\")]; refs=sorted({p for f in fs for p in re.findall(r\"`(docs/process_traces/[^`]+[.]md)`\",f.read_text())}); missing=[p for p in refs if not pathlib.Path(p).is_file()]; print(\"EVIDENCE-PATHS-OK\" if not missing else \"MISSING: \"+\" \".join(missing)); sys.exit(bool(missing))'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["EVIDENCE-PATHS-OK"]},
      "expected": {"exit_code": 0, "tail_regex": "EVIDENCE-PATHS-OK"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c 'import pathlib,subprocess,sys; allowed={\"docs/agent_playbook.md\",\"docs/orchestration.md\",\"docs/process_traces/2026-09-04-fanout/skill-distill/01-sol-report.md\",\"docs/process_traces/2026-09-04-fanout/skill-distill/02-lessons.md\"}; rows=subprocess.check_output([\"git\",\"status\",\"--porcelain=v1\",\"--untracked-files=all\"],text=True).splitlines(); paths={r[3:].split(\" -> \")[-1] for r in rows}; extra=sorted(paths-allowed); print(\"WRITE-SCOPE-OK\" if not extra else \"UNEXPECTED: \"+\" \".join(extra)); sys.exit(bool(extra))'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["WRITE-SCOPE-OK"]},
      "expected": {"exit_code": 0, "tail_regex": "WRITE-SCOPE-OK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "rg -n '^## ([1-7][.]|Addendum 2026-09-04)' docs/process_traces/2026-09-04-fanout/skill-distill/02-lessons.md docs/orchestration.md docs/agent_playbook.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["02-lessons.md:14:## 1. Wrapper cost", "02-lessons.md:34:## 2. Direct `codex-run-v3` pitfalls", "02-lessons.md:61:## 3. The preflight trap", "02-lessons.md:82:## 4. Replay hygiene", "02-lessons.md:103:## 5. Packet hygiene", "02-lessons.md:126:## 6. First-use gate outcomes", "02-lessons.md:149:## 7. Cold-gate seat separation"]},
      "expected": {"exit_code": 0, "tail_regex": "## 7[.] Cold-gate seat separation"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "python3 -c 'import json,pathlib,re,sys; p=pathlib.Path(\"docs/process_traces/2026-09-04-fanout/skill-distill/01-sol-report.md\"); m=re.match(r\"```json\\n(.*?)\\n```\",p.read_text(),re.S); assert m; n=len(m.group(1).encode()); json.loads(m.group(1)); print(\"ENVELOPE-JSON-OK\"); sys.exit(n>8192)'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["ENVELOPE-JSON-OK"]},
      "expected": {"exit_code": 0, "tail_regex": "ENVELOPE-JSON-OK"}
    }
  ],
  "flags": []
}
```

## Change

The lesson record defines each process term in plain language, ties every lesson
to repository evidence, supplies one proposed doctrine sentence, and identifies
the global skill that should receive the same rule later. The orchestration
addendum installs direct-seat ceremony, harvest-before-retry, clean replay
custody, packet hygiene, first-use evidence, and independent cold-seat scratch
space. The playbook addendum makes an explicit task-local, edit-first, or
focused-test rule override Mission M0's default repository-wide preflight test.

| Finding | Decision | Evidence |
|---|---|---|
| A passive model wrapper adds cost and another failure boundary. | Use direct bounded seats after the lead fixes the contract; retain directors for actual judgment. | Hands-free durable state, budget and recovery sections. |
| Direct runner status can be invalidated by lead dirt or an oversized envelope. | Pin the invocation, isolate read-only work, separate semantic judgment from runner status, and harvest before retry. | DX and T26 magistrate notes; failed and corrected final-head reports. |
| Generic preflight discovery can consume a bounded seat without answering its question. | Task-local verification instructions govern; edit first and run focused checks when required. | Watchdog contract review and focused landing report. |
| Replays can be invalidated by wrong parents, contaminated trees, or bad mutation restores. | Use disposable exact trees, recorded parents/logs/status, restored digests, and artifact byte comparison. | Plan-pin, watchdog, and paper integration replay records. |
| A mechanically complete packet can still bias or contaminate its gate. | Require neutral questions, evidence labels and pins, complete manifests, symmetric alternatives, and side-effect-safe commands. | Watchdog cold-gate refuter and ruling. |
| Vocabulary first-use and behavioral first-use are different gates. | Require the term table and an executed probe for behavioral clauses. | Projection pedagogy review, D-171 addendum audit, watchdog first-use finding. |
| Shared cold-seat scratch space weakens independence. | Give each seat a separate scratch root and open outputs only after sealing. | Watchdog gate synthesis. |

No forbidden state or paper files were edited. The needed global-skill changes
are proposals only because the skill files are outside the repository write
scope:

| Global skill | Proposed edit |
|---|---|
| `operation-loop` | Prefer direct bounded seats once the lead has fixed the contract; add task-local verification precedence, harvest-before-retry, and clean exact-parent replay checks. |
| `codex-delegation` | Add the direct-run launch checklist, small-envelope rule, clean read-only checkout rule, and separate semantic verdict from wrapper failure caused by attributed pre-existing dirt. |
| `adversarial-review` | Require packet side-effect review and a distinct sealed scratch root for every cold-gate seat. |
| `council` | Add neutral atomic questions, symmetric alternatives, complete bounded exhibits, volatile-fact pins, and post-seal-only comparison. |
| `consistency-sweep` | Produce the defined-term first-use table and flag behavioral clauses that lack executed first-real-use evidence. |

## Verification notes

Verification was intentionally deferred until after the documentation edits.
No repository-wide unit-test discovery was run, and no test module was named or
touched. Executed commands and stable tails are recorded in the final envelope.
