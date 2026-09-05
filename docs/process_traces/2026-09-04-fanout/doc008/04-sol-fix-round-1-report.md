```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "FIX ROUND 1 cures both DOC-008 refuter blockers with the ruled root-document completion and biting regressions for every named counterfactual.",
  "workspace": {
    "base_requested": "e84fdbf9de26d131ef576eb0ce7e6808005a2199",
    "base_mode": "exact",
    "head_start": "e84fdbf9de26d131ef576eb0ce7e6808005a2199",
    "head_end": "e84fdbf9de26d131ef576eb0ce7e6808005a2199",
    "upstream_end": "e84fdbf9de26d131ef576eb0ce7e6808005a2199",
    "branch": "feat/2026-09-04-fan-doc008"
  },
  "pathspec": [
    "AGENT_PLAN.md",
    "PROJECT_STATUS.md",
    "README.md",
    "docs/process_traces/2026-09-04-fanout/doc008/04-sol-fix-round-1-report.md",
    "tests/test_docs_freshness.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_docs_freshness -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 29 tests in 0.866s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 29 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 - <<'PY'\nimport subprocess\nfrom tests import test_docs_freshness as t\nbase = \"b0ed6991c11f3a515ad293760c6dfc031adda8e1\"\ndef at_base(path):\n    return subprocess.check_output([\"git\", \"show\", f\"{base}:{path}\"], text=True)\ncases = ((\"intake\", (\"docs/agent_playbook.md\", \"docs/phase_2/phase_2_exit_checklist.md\")), (\"reflection\", (\"docs/planning_reflection_protocol.md\",)), (\"orchestration\", (\"docs/orchestration.md\",)), (\"root\", (\"AGENT_PLAN.md\", \"README.md\", \"PROJECT_STATUS.md\")))\nfor name, paths in cases:\n    docs = t._doc008_documents()\n    for path in paths:\n        docs[path] = at_base(path)\n    try:\n        t._assert_doc008_contract(docs)\n    except AssertionError as exc:\n        print(f\"{name} base counterfactual: REJECTED ({exc})\")\n    else:\n        raise SystemExit(f\"{name} base counterfactual unexpectedly passed\")\ndocs = t._doc008_documents()\ndocs.pop(\"docs/project_status_history.md\")\ntry:\n    t._assert_doc008_contract(docs)\nexcept AssertionError as exc:\n    print(f\"archive-absent counterfactual: REJECTED ({exc})\")\nelse:\n    raise SystemExit(\"archive-absent counterfactual unexpectedly passed\")\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "intake base counterfactual: REJECTED (Mission M0 missing required route: generated `RUN_STATE.md` intake/restart region)",
          "reflection base counterfactual: REJECTED (reflection protocol is not the exact DOC-008 redirect stub)",
          "orchestration base counterfactual: REJECTED (orchestration missing exact DOC-008 procedure: ### 7.1 Two-writer rule)",
          "root base counterfactual: REJECTED (AGENT_PLAN retains retired intake)",
          "archive-absent counterfactual: REJECTED (DOC-008 required document missing: ['docs/project_status_history.md'])"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "archive-absent counterfactual: REJECTED"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check",
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
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; import re; s=Path(\"PROJECT_STATUS.md\").read_text(); print(\"H2 sections:\", len(re.findall(r\"^## \", s, re.M))); print(\"total words:\", len(s.split()))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["H2 sections: 7", "total words: 1062"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "H2 sections: 7\\ntotal words: 1062"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The magistrate ruling requires lead semantic review and sign-off of the compact PROJECT_STATUS draft; this implementation supplies the draft and structural regression but cannot self-sign it.",
      "needs": "Magistrate reviews and signs the PROJECT_STATUS.md prose before landing."
    }
  ]
}
```

## Change

F-001 is cured: the two root execution guides now route intake and close-out
through Mission M0 and the state kernel, with generated RUN_STATE/TASK_QUEUE
views. The advisor status page is a 1,062-word, exactly seven-H2 current view;
history remains in its archive, and D-171's delegated transaction GO replaces
the stale personal-authorization wording.

F-002 is cured with one DOC-008 contract checker and five mutation tests. Four
tests cover the refuter's named behavioral groups; the fifth protects the ruled
root completion. The checker pins the exact spec-owned redirect and
orchestration blocks and rejects the actual merge-base versions independently.

Finding-to-cure map:

| finding | cure | file:line |
|---|---|---|
| F-001 | Replace retired reflection/direct queue intake with Mission M0 and kernel-generated views. | `AGENT_PLAN.md:9-18`; `README.md:248-264` |
| F-001 | Replace the 16-H2 historical/current mixture with the exact seven-section compact advisor view and reconcile transaction authority to D-171. | `PROJECT_STATUS.md:1-129` |
| F-002 | Enforce the combined DOC-008 document contract, exact spec blocks, archive, root routes, and seven-section/word target. | `tests/test_docs_freshness.py:23-32`; `tests/test_docs_freshness.py:333-429` |
| F-002 | Reject old M0/checklist, live reflection, missing procedures, absent archive, and independently stale-root/uncompacted-status counterfactuals. | `tests/test_docs_freshness.py:1057-1132` |

No magistrate-owned state row is needed for either cure, so there is no row
text to apply to RUN_STATE, TASK_QUEUE, the kernel, or the decision log.

## Verification notes

The first focused run failed two assertions because the new M0 checker treated
a Markdown line wrap as semantic whitespace. The assertion was normalized and
the final focused run passed. The whole suite was not run, as required by the
preflight rule. V2's complete replay heredoc and output are preserved in the
envelope and runner transcript.

## Residual risk

Structural checks cannot validate advisor-facing scientific judgment. The
magistrate must review and sign the compact PROJECT_STATUS draft before merge.
