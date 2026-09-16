```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "AMEND: idle MCP helpers under the caller's headless magistrate falsely block a stub arm; 34 mutation probes died by assertions and restored GREEN.",
  "workspace": {
    "base_requested": "e09dd964a0c0336f9a34482e209d1d0d37b77a79",
    "base_mode": "exact",
    "head_start": "e09dd964a0c0336f9a34482e209d1d0d37b77a79",
    "head_end": "e09dd964a0c0336f9a34482e209d1d0d37b77a79",
    "upstream_end": "e09dd964a0c0336f9a34482e209d1d0d37b77a79",
    "branch": "feat/2026-09-15-arm-census-idle"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "AMEND",
    "findings": [
      {
        "id": "R1",
        "severity": "blocker",
        "title": "Own headless magistrate's idle MCP helpers remain foreign",
        "locations": [
          "joulewise/arm_census.py:197",
          "joulewise/arm_census.py:204",
          "tests/test_arm_census.py:176"
        ],
        "detail": "Fixture: claude -p PID 20 -> shell 30 -> census caller 90, plus node codex mcp-server PID 50 -> codex-code-mode-host PID 60. Actual observation/classification yields own_pids=(20,30,90), workloads=(), foreign_pids=(50,60), publication_blocked=True. The headless root cannot receive idle_exemption, and only direct caller ancestry enters exempt. This violates question 4's explicit requirement and manufactures a stub refusal.",
        "recommendation": "Handle idle MCP helpers attached to the proven own activation, add this regression fixture, and retain the paired assertion that a sibling codex exec seat remains blocking. Do not exempt the whole own subtree unconditionally."
      }
    ],
    "answers": {
      "1": "PASS: fake real-shaped interactive Claude tree with zsh -c, ugrep, node codex mcp-server and codex-code-mode-host is IDLE; adding a python3 -m unittest grandchild makes it BUSY.",
      "2": "PASS for tested census outcomes: valid DIAGNOSTIC_NO_PACK and TRANSACTION_PACK plans exit 0 with busy, foreign or unknown observations. Invalid-plan/invocation failures are separate.",
      "3": "PASS: main reads plan bytes and selects receipt_class through NightPlan.from_mapping at line 265; no class flag, environment selection or path selection found.",
      "4": "FAIL for idle own MCP helpers; PASS for rejecting a sibling codex exec seat outside caller ancestry, with options before and after exec.",
      "5": "PASS: production night paths are unchanged. Structural no-import and actual C15 gate oracle pass; introducing an import or bypassing the stub gate census kills their assertions.",
      "6": "PASS: native and Node-launched codex exec are detected with options before and after the subcommand.",
      "7": "UNVERIFIED: the single requested ps read was denied by the sandbox."
    },
    "mutation_evidence": {
      "total": 34,
      "assertion_killed": 34,
      "restored_green": 34,
      "must_die": [
        "unknown_busy: FAILED (failures=1), then OK",
        "drop_unittest: FAILED (failures=6), then OK",
        "stub_class_exemption_removed: FAILED (failures=2), then OK",
        "own_chain_removed: FAILED (failures=4), then OK",
        "main_pack_exit3: FAILED (failures=2), then OK"
      ],
      "additional": "Every arm test was exercised against a plausible assertion-killed defect. Additional probes covered workload-family omissions, descendant depth, overbroad ownership, structural isolation, and C15-C18.",
      "logs": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-contract-mut/review-mutation-logs"
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_arm_census",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-contract-mut",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 13 tests in 0.035s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night.NightDriverTests.test_real_idle_agent_hit_refuses_without_chain_or_pack_authoring tests.test_run_night.PackNightProducerTests.test_idle_agent_hit_preserves_initial_refusal_code tests.test_run_night.NightDriverTests.test_idle_agent_appearing_after_go_still_aborts_real_chain tests.test_run_night.NightDriverTests.test_rehearsal_census_hits_are_observed_without_killing_the_stub",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-contract-mut",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 4 tests in 0.235s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v tests.test_a173_contract_review",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-contract-mut",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "REAL_SHAPED IDLE () ()",
          "REAL_SHAPED BUSY (20, 50, 60) ((70, 'unittest'),)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B review_mutations.py",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-contract-mut",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["MUTATIONS: 28/28 killed by assertions; all controls restored GREEN"]
      },
      "expected": {"exit_code": 0, "tail_regex": "MUTATIONS: [0-9]+/[0-9]+ killed by assertions; all controls restored GREEN"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B review_mutations.py root_substring codex_argument_name_is_work discovery_widened unknown_observation_blocks unreadable_own_root_drops_side_work invalid_plan_accepted",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-contract-mut",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["MUTATIONS: 6/6 killed by assertions; all controls restored GREEN"]
      },
      "expected": {"exit_code": 0, "tail_regex": "MUTATIONS: 6/6 killed by assertions; all controls restored GREEN"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B review_integrity.py",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-contract-mut",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "BASELINE_DIGEST_MATCH",
          "HEAD_UNCHANGED; INDEX_UNCHANGED; WORKTREE_CLEAN",
          "SCRATCH_MUTATIONS_RESTORED; PRODUCTION_NIGHT_PATHS_UNCHANGED"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "SCRATCH_MUTATIONS_RESTORED; PRODUCTION_NIGHT_PATHS_UNCHANGED"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "ps -axo pid,ppid,command > /private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-contract-mut/live-ps.txt",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 127, "tail": ["zsh:1: operation not permitted: ps"]},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Sandbox denied the one ps read. No bypass or second attempt was made; process-shape results are fixture evidence.",
      "needs": "Lead-owned live observation if live-shape verification is required."
    }
  ]
}
```

## Findings

**R1 — blocker:** [arm_census.py:197](/Users/edr/code/JouleWise-wt-a173/joulewise/arm_census.py:197) denies the idle exemption to a headless own root, leaving its idle MCP helpers foreign at [line 204](/Users/edr/code/JouleWise-wt-a173/joulewise/arm_census.py:204). The independent fixture reproduces a blocked stub with **no workloads**. The existing ownership test omits these helpers.

**Verdict: AMEND.** Fix that classification and add the helper/sibling-seat regression pair before returning to the landing gate.

## Residual risk

Live shapes remain unverified because `ps` was denied; T3 remains PROVISIONAL. No full suite or hardware checks ran. The mutation runner now includes all 34 probes; V4 records its initial 28-probe execution, followed by the six additions in V5. Repository files, index and HEAD remained unchanged.