```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REJECT: the branch violates the staged scope fence, leaves a public non-launcher consumption writer, weakens inner config authentication to semantic equality, and overclaims launch readiness in E-10.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "exact",
    "head_start": "e7fa8fd37b2de27e6600cd74b91dbffc9871dec3",
    "head_end": "e7fa8fd37b2de27e6600cd74b91dbffc9871dec3",
    "upstream_end": "fac87d1f8350ab5277d45f422fbfa6098630efe4",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "REJECT",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The whole branch diff crosses the explicit stages 3-4 scope fence",
        "files": [
          "joulewise/analysis_engine/inputs.py:2396",
          "joulewise/floor_extraction.py:1865",
          "joulewise/whole_window.py:3148",
          "joulewise/whole_window.py:5023"
        ],
        "evidence": "The branch adds post-hoc analysis, extraction, NEG-8 bound-mint, and whole-window reauthentication even though the adopted staging assigns reduce/mint downstream gates to stage 3 and the review fence forbids those edits."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The inner writer does not independently authenticate the selected config file as a pack member",
        "files": [
          "joulewise/bundle.py:95",
          "joulewise/bundle.py:103",
          "joulewise/bundle.py:122",
          "joulewise/cli.py:284"
        ],
        "evidence": "The CLI parses the invoked path into BenchmarkConfig and discards the path. The writer then calls authenticate_campaign_launch_lineage without config_paths and accepts any config semantically equal to a pack member. A direct CLI invocation using an external or byte-modified semantic clone therefore passes the inner gate; only the outer campaign verifies exact source bytes/path."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "A public non-launcher path can still consume an arm capability",
        "files": [
          "joulewise/arm_readiness.py:4762",
          "joulewise/arm_readiness.py:4806",
          "joulewise/arm_readiness.py:4861",
          "joulewise/arm_readiness.py:5805"
        ],
        "evidence": "consume_launch_capability explicitly preserves its all-None legacy writer, emits the deterministic consumption primary and sidecar, and remains exported in __all__. The standalone CLI refuses correctly, but direct library invocation still consumes outside scripts/launch_window.py."
      },
      {
        "id": "F4",
        "severity": "blocker",
        "title": "Runbook E-10 claims enforcement that is not present and can misdirect a physical launch",
        "files": [
          "docs/phase_2/window_runbook.md:1040",
          "docs/phase_2/window_runbook.md:1075",
          "docs/phase_2/window_runbook.md:1360",
          "docs/decision_log.md:9379"
        ],
        "evidence": "E-10 says calibration slots are writer-gated and presents successor configs as marker-bearing, while the decision-log amendment says calibration enforcement is deferred and stages 3-4 still gate launch readiness. No campaign config currently contains launch_lineage_required."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --check origin/main...HEAD",
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
      "id": "V2",
      "kind": "lint",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import ast, pathlib; paths=[pathlib.Path(p) for p in (\"joulewise/analysis_engine/inputs.py\",\"joulewise/arm_readiness.py\",\"joulewise/bundle.py\",\"joulewise/floor_extraction.py\",\"joulewise/whole_window.py\",\"scripts/generate_arm_readiness.py\",\"scripts/launch_window.py\",\"scripts/run_campaign.py\")]; [ast.parse(p.read_text(encoding=\"utf-8\"), filename=str(p)) for p in paths]; print(f\"AST_OK {len(paths)} files\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "AST_OK 8 files"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^AST_OK 8 files$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "Compare LAUNCH_LINEAGE_REASON_CODES against the D-078 launch-consumption amendment using Python AST and regex extraction",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "code=launch_binding_mismatch,launch_consumption_invalid,launch_consumption_missing,launch_handoff_invalid,launch_lifecycle_incomplete,launch_lineage_conflict",
          "decision=launch_binding_mismatch,launch_consumption_invalid,launch_consumption_missing,launch_handoff_invalid,launch_lifecycle_incomplete,launch_lineage_conflict",
          "MATCH"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MATCH$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness tests.test_bundle tests.test_launch_window tests.test_run_campaign",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --quiet origin/main...HEAD -- joulewise/analysis_engine/inputs.py joulewise/floor_extraction.py joulewise/whole_window.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
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
      "cmd": "git diff --quiet origin/main...HEAD -- scripts/validate_powermetrics_fiducial.py 'configs/**'",
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
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The focused suite could not start because the read-only environment exposes no writable temporary directory.",
      "needs": "Lead should rerun the focused tests and canonical suite in the normal writable bench after fixes."
    }
  ]
}
```

## Findings

**VERDICT: REJECT.**

- **F1 — Blocker: stages 3-4 landed across the scope fence.** [inputs.py:2396](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtB-lensCON/joulewise/analysis_engine/inputs.py:2396), [floor_extraction.py:1865](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtB-lensCON/joulewise/floor_extraction.py:1865), and [whole_window.py:3148](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtB-lensCON/joulewise/whole_window.py:3148) implement downstream analysis, extraction, bound-mint, and verdict gates. The adopted staging assigns these to stage 3; this review’s fence explicitly forbids them.

- **F2 — Blocker: inner config membership is not independent.** The outer gate passes exact paths, but [bundle.py:95](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtB-lensCON/joulewise/bundle.py:95) does not. It accepts semantic equality at [bundle.py:122](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtB-lensCON/joulewise/bundle.py:122) after the CLI has discarded the invoked path. Direct invocation with a semantic clone can therefore pass the inner writer gate.

- **F3 — Blocker: standalone consumption is not fully retired.** [arm_readiness.py:4762](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtB-lensCON/joulewise/arm_readiness.py:4762) deliberately preserves the legacy all-`None` writer, and [arm_readiness.py:5805](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtB-lensCON/joulewise/arm_readiness.py:5805) publicly exports it. The CLI refusal is correct but does not close this alternate consumption path.

- **F4 — Blocker: E-10 overclaims readiness.** [window_runbook.md:1040](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtB-lensCON/docs/phase_2/window_runbook.md:1040) claims calibration-slot enforcement, while [decision_log.md:9379](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtB-lensCON/docs/decision_log.md:9379) explicitly says it is deferred and later stages still gate launch readiness. No current campaign config carries the marker.

## Residual risk

Dynamic verification remains outstanding because this read-only environment has no writable temporary directory. The locator schema, dual-root no-clobber publication, pack-root derivation fix, T‑0 handling, and six D-078 spellings passed static inspection.