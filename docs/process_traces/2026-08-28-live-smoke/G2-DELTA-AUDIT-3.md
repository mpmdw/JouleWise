```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "DO-NOT-MERGE: B2 accepts contradictory G2-a summaries, and the main merge introduced an active three-rung/margin-5 pre-registration projection that contradicts amended D-166.",
  "workspace": {
    "base_requested": "46477ceb88787c1675b34a42bd13e243a3ddb3b2",
    "base_mode": "exact",
    "head_start": "b301173fedd4d626fc7f37a8fab7941aed39a97d",
    "head_end": "b301173fedd4d626fc7f37a8fab7941aed39a97d",
    "upstream_end": "9de48a9f262ca71dfa558bcbff9b07f39daffacd",
    "branch": "feat/window-provenance-check"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "DO-NOT-MERGE",
    "items": {
      "audit2_1_generated_region": {
        "verdict": "PASS",
        "detail": "The existing G2-b generated region remains byte-exact and rejects runbook/runsheet mutation."
      },
      "audit2_2_h2_boundary": {
        "verdict": "PASS",
        "detail": "The night chain still stops at physical_ahead with a non-null candidate, no completion event, and no pin advance; the reviewed desk advance remains separate."
      },
      "audit2_6_cross_damage": {
        "verdict": "PASS",
        "detail": "The ten-ID assertion roster, frozen roster source, TERMINATE HERE card, exact finalizer refusal, and required preflight checkout argument remain intact."
      },
      "B1": {
        "verdict": "PASS",
        "detail": "All 20 G2A_* shell variables are produced in the variable block or before consumption; function/loop locals and jq variables are locally bound. The G2-a bracket is generated from pinned reservation/helper bytes, and mutations go red in both directions."
      },
      "B2": {
        "verdict": "FAIL",
        "detail": "Rung ordering, exhausted-ladder collect-at-4096 behavior, split refusal vocabulary, deterministic rendering, desk invocation, and output hashing pass. Semantic malformed-input handling and the binding MIN_PHASE_SAMPLES consistency check do not."
      },
      "B3": {
        "verdict": "PASS",
        "detail": "The regression builds the real fixture tree, mutates real campaign/verdict membership surfaces, invokes check_main without checker mocks, and requires exactly S11-A2 plus F5-1..4 to fail for both add-one and delete-one."
      },
      "merge_behavior_pins": {
        "verdict": "PASS",
        "detail": "The merge commit did not touch the six G2 implementation/test paths; docs freshness, state generation, and generated-region checks pass."
      },
      "merge_readiness": {
        "verdict": "FAIL",
        "detail": "The new unittest module is dynamically shard-discovered with four non-skipped tests, but active stale three-rung/margin-5 projection material remains and B2 is unsound."
      }
    },
    "findings": [
      {
        "id": "B2",
        "severity": "blocker",
        "title": "The selector authorizes internally contradictory summaries and only restates, rather than checks, the reducer floor",
        "locations": [
          "scripts/select_g2a_prefill_length.py:18",
          "scripts/select_g2a_prefill_length.py:34",
          "scripts/select_g2a_prefill_length.py:47",
          "scripts/select_g2a_prefill_length.py:76",
          "tests/test_select_g2a_prefill_length.py:71",
          "docs/decision_log.md:193"
        ],
        "refutation": "Provide four ladder rows with small_members=5 and all_small_count_ge_5=true while small_minimum_count=0. The selector discards small_minimum_count and selects 512. It also hard-codes reducer_min_phase_samples=3 without importing or validating joulewise.reduce.MIN_PHASE_SAMPLES."
      },
      {
        "id": "M1",
        "severity": "blocker",
        "title": "The main merge introduced an active pre-registration projection with superseded three-rung and margin-5 semantics",
        "locations": [
          "scripts/paper_prefill_resolvability_projection.py:2",
          "scripts/paper_prefill_resolvability_projection.py:54",
          "scripts/paper_prefill_resolvability_projection.py:56",
          "docs/paper/round7/prefill-resolvability-projection.md:1",
          "docs/paper/round7/prefill-resolvability-projection.md:95",
          "docs/paper/round7/prefill-resolvability-projection.md:368"
        ],
        "refutation": "Import the script: CANDIDATE_LENGTHS is (512,1024,2048) and A_repo_margin_field requires count 8. The companion document still calls the ambiguity NEEDS-RULING and treats 4096 as outside the ladder, despite amended D-166 already being the merge parent's authority."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "build",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS generated Phase D matches pinned runbook bytes"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS generated Phase D matches pinned runbook bytes$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import unittest; from scripts.gen_g2_phase_d import *; r=RUNBOOK_PATH.read_text(); s=RUNSHEET_PATH.read_text(); m=r.replace(\"  /bin/sleep \\\"$SETTLE_S\\\"\",\"  /bin/sleep 999\",1); t=unittest.TestCase(); [(t.assertEqual(s[s.index(a):s.index(b,s.index(a))+len(b)+1],f(r)),t.assertRaises(ValueError,f,m)) for f,a,b in ((render_g2a_generated_region,G2A_BEGIN_MARKER,G2A_END_MARKER),(render_generated_region,BEGIN_MARKER,END_MARKER))]; print(\"PASS both regions exact; runbook mutations red; exact compare makes runsheet mutations red\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS both regions exact; runbook mutations red; exact compare makes runsheet mutations red"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS both regions exact"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; from scripts.select_g2a_prefill_length import LADDER,select; mk=lambda q:[{\"length\":n,\"small_members\":5,\"all_small_count_ge_5\":q is not None and n>=q} for n in reversed(LADDER)]; assert [select(mk(q),summary_sha256=\"a\")[\"selected_prefill_tokens\"] for q in LADDER]==list(LADDER); r=select(mk(None),summary_sha256=\"b\"); assert r[\"collection_prefill_tokens\"]==4096 and r[\"refusal\"][\"fallback_label\"]==\"collect-at-4096\"; a=json.dumps(select(mk(1024),summary_sha256=\"c\"),indent=2,sort_keys=True)+\"\\n\"; b=json.dumps(select(mk(1024),summary_sha256=\"c\"),indent=2,sort_keys=True)+\"\\n\"; assert a.encode()==b.encode(); print(\"PASS each rung, zero-rung refusal, deterministic render\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS each rung, zero-rung refusal, deterministic render"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS each rung"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'from scripts.select_g2a_prefill_length import LADDER,select; bad=[{\"length\":n,\"small_members\":5,\"all_small_count_ge_5\":True,\"small_minimum_count\":0} for n in LADDER]; r=select(bad,summary_sha256=\"c\"*64); print(\"status=%s selected=%s\"%(r[\"status\"],r[\"selected_prefill_tokens\"])); raise SystemExit(r[\"status\"]==\"selected\")'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "status=selected selected=512"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^status=refused selected=None$"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import sys,unittest; sys.path.insert(0,\"scripts\"); import shard_tests; import tests.test_select_g2a_prefill_length as m; target=\"tests.test_select_g2a_prefill_length\"; print(\"discovered=%s tests=%d\"%(target in shard_tests.discover_test_modules(),unittest.defaultTestLoader.loadTestsFromModule(m).countTestCases()))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "discovered=True tests=4"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^discovered=True tests=4$"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_select_g2a_prefill_length",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (errors=10)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_check_window_provenance.CheckWindowProvenanceTests.test_real_add_delete_membership_reaches_s11_a2_and_all_f5_assertions",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The read-only sandbox has no writable temporary directory, so the new selector module and the B3 real-fixture regression could not execute locally; pure-function checks and static real-call-path inspection completed.",
      "needs": "After fixing B2 and M1, rerun both focused modules and the canonical suite in writable CI or on the lead bench."
    }
  ]
}
```

## Findings

- **B2 — blocker:** [select_g2a_prefill_length.py:47](/Users/edr/code/JouleWise-wt-g1/scripts/select_g2a_prefill_length.py:47) validates only `length`, `small_members`, and the derived Boolean. It ignores the emitted `small_minimum_count`, so four rows claiming `all_small_count_ge_5=true` can carry a minimum count of zero and still select 512. It also hard-codes the reducer floor at [line 18](/Users/edr/code/JouleWise-wt-g1/scripts/select_g2a_prefill_length.py:18), rather than implementing D-166’s required consistency check against the production reducer. Refutation: submit that contradictory four-row object; the observed result is `status=selected selected=512`.

- **M1 — blocker:** The main merge added [paper_prefill_resolvability_projection.py:54](/Users/edr/code/JouleWise-wt-g1/scripts/paper_prefill_resolvability_projection.py:54), whose executable ladder is still `(512, 1024, 2048)` and whose Reading A still requires count 8. Its companion [prefill-resolvability-projection.md:95](/Users/edr/code/JouleWise-wt-g1/docs/paper/round7/prefill-resolvability-projection.md:95) presents the ambiguity as unresolved and 4096 as outside the ladder. These are current desk-pre-registration artifacts, not merely immutable historical quotations, and contradict [amended D-166](/Users/edr/code/JouleWise-wt-g1/docs/decision_log.md:193).

Per-B verdict: **B1 PASS; B2 FAIL; B3 PASS.** Audit-2 items **1/2/6 remain PASS**. The merge did not disturb the behavior pinned by the G2 tests, but it introduced M1. **DO-NOT-MERGE.**

## Residual risk

The focused filesystem-backed tests and canonical suite require a writable CI/lead rerun. Historical cold-gate traces and the runsheet’s explicit “NEVER margin ≥ 5” rejection appropriately retain old literals; M1 is different because it remains executable/current.