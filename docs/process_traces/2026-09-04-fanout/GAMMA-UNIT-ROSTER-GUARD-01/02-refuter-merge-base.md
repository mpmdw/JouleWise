```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The mission delta is in scope and its focused tests pass, but the roster guard remains bypassable through the mutable plan_id that selects it.",
  "workspace": {
    "base_requested": "aa33b0a8a5e8db6c03351cd23f8e75a203f1dcde",
    "base_mode": "exact",
    "head_start": "aa33b0a8a5e8db6c03351cd23f8e75a203f1dcde",
    "head_end": "aa33b0a8a5e8db6c03351cd23f8e75a203f1dcde",
    "upstream_end": "ec8f780337326f82feb1848a972c4746612da6cc",
    "branch": "feat/2026-09-04-fan-GAMMA-UNIT-ROSTER-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/GAMMA-UNIT-ROSTER-GUARD-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "joulewise/identity_pins.py:530-539,627; joulewise/identity_pins.py:2081-2085; joulewise/arm_readiness.py:5786-5809",
        "text": "The canonical-roster check is enabled by plan_id read from the same mutable plan tree it is meant to police. Changing that field to any other string disables the check. The actual freeze loader accepted a self-consistent unprojected three-unit pack after its plan/window ID was changed to plan-not-d131-gamma, and the arm path returned PASS for a matching three-unit receipt and pack under that spoofed ID. The pack therefore remains its own oracle through the dispatch key; current v5 gamma plan IDs also take the unconditional return.",
        "counterfactual": "Remove B/prefill_p256 from the gamma roster and change plan.plan_id plus window_identity.window_id (and the arm receipt's pack.plan_id) to plan-not-d131-gamma; freeze loading accepts three units and the arm comparison accepts PASS instead of refusing against D-131."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --name-only b0ed6991c11f3a515ad293760c6dfc031adda8e1..HEAD && git diff --quiet b0ed6991c11f3a515ad293760c6dfc031adda8e1..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py",
          "docs/process_traces/2026-09-04-fanout/GAMMA-UNIT-ROSTER-GUARD-01/01-sol-report.md",
          "joulewise/arm_readiness.py",
          "joulewise/identity_pins.py",
          "tests/test_gamma_unit_roster_guard.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_gamma_unit_roster_guard\\.py$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_gamma_unit_roster_guard",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 3 tests in 0.645s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 3 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_identity_pins",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 42 tests in 19.629s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 42 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_integration",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 10 tests in 9.045s", "OK (skipped=5)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 10 tests in .*s\\n\\nOK \\(skipped=5\\)"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_decode_contrast_plan",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 25 tests in 33.933s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 25 tests in .*s\\n\\nOK \\(skipped=1\\)"}
    },
    {
      "id": "V6",
      "kind": "build",
      "cmd": "python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py --check",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["generation failed: the current frozen identity requires preserve mode"]},
      "expected": {"exit_code": 1, "tail_regex": "current frozen identity requires preserve mode"}
    },
    {
      "id": "V7",
      "kind": "build",
      "cmd": "python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py --check --preserve-current-frozen-bytes",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["checked D-117 gamma d117_contrast_qwen25_1p5b_vs_7b_v3: decode_members=40 prefill_p256_members=40 plan_sha256=56ed0e534f102ad6e0a1da12a4e2f9856ce4fe17e9d8af546bf2323f9d70bcb5 tree_sha256=788f1a20bc5a22f073539e2d0b4df5ffd0b3e82d8b78015c7e668c0cbda8b5a7"]},
      "expected": {"exit_code": 0, "tail_regex": "^checked D-117 gamma .*decode_members=40 prefill_p256_members=40.*$"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "cd /private/tmp/jw-gamma-refuter.ODcNdU/repo && perl -0pi -e 's/if plan_id != D131_GAMMA_PLAN_ID:\\n        return/if True:  # counterfactual: roster guard reverted\\n        return/' joulewise/identity_pins.py && python3 -m unittest tests.test_gamma_unit_roster_guard",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 3 tests in 2.487s", "FAILED (failures=5)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=5\\)"}
    },
    {
      "id": "V9",
      "kind": "smoke",
      "cmd": "python3 -c 'import hashlib,json,shutil,tempfile; from pathlib import Path; from joulewise import identity_pins; src=Path(\"configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3\"); d=tempfile.TemporaryDirectory(); pack=Path(d.name)/src.name; shutil.copytree(src,pack); path=pack/\"plan_tree.json\"; tree=json.loads(path.read_text()); spoof=\"plan-not-d131-gamma\"; tree[\"plan\"][\"plan_id\"]=spoof; tree[\"window_identity\"][\"window_id\"]=spoof; p=tree[\"arm_attachments\"][\"identity_pin_projection\"]; p[\"state\"]=\"unprojected\"; p[\"projection_receipt\"]=None; p[\"identity_units\"].pop(); [(u.__setitem__(\"model_runtime_config\",{k:None for k in u[\"model_runtime_config\"]})) for u in p[\"identity_units\"]]; raw=(json.dumps(tree,indent=2,sort_keys=True)+\"\\n\").encode(); path.write_bytes(raw); (pack/\"plan_tree.sha256\").write_text(hashlib.sha256(raw).hexdigest()+\"  plan_tree.json\\n\"); t,q,_=identity_pins._load_pack_projection(pack); print(\"actual_freeze_loader:\",t[\"plan\"][\"plan_id\"],len(q[\"identity_units\"]),\"ACCEPTED\")'",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 0, "tail": ["actual_freeze_loader: plan-not-d131-gamma 3 ACCEPTED"]},
      "expected": {"exit_code": 1, "tail_regex": "ordered D-131 gamma unit roster"}
    },
    {
      "id": "V10",
      "kind": "lint",
      "cmd": "git diff --check && python3 -m py_compile joulewise/identity_pins.py joulewise/arm_readiness.py configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py tests/test_gamma_unit_roster_guard.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A real idempotent freeze/arm re-verification of the tracked MLX pack was not run because MLX is unavailable; the claimed focused modules, the frozen-evidence loader, preservation check, and isolated arm counterfactual were run instead.",
      "needs": "Lead final verification should exercise the real MLX-backed freeze/arm path after the blocker is fixed."
    }
  ]
}
```

## Findings

### F1 — blocker — mutable `plan_id` bypasses the rule

`validate_d131_gamma_identity_unit_roster()` returns without checking unless its caller supplies the exact Qwen2.5 v3 plan ID. Every freeze and arm caller added by this delta obtains that ID from `tree["plan"]["plan_id"]`, the same pack-controlled document whose roster is under review. The guard is therefore not an external roster oracle.

Executed exploit: a temporary copy of the tracked gamma pack was made unprojected, its last unit was removed, its plan and window IDs were set to `plan-not-d131-gamma`, and its plan-tree sidecar was recomputed. The production `_load_pack_projection()` entry accepted the resulting three-unit projection:

```text
actual_freeze_loader: plan-not-d131-gamma 3 ACCEPTED
```

The corresponding arm probe made the receipt and pack agree on that spoofed ID and the same three units; `_authenticate_identity_arm_evidence()` returned `PASS, []`. With the canonical plan ID unchanged, the same three-unit projection refuses with `readiness_identity_artifact_unreadable`, proving the dispatch key—not the roster shape—controls enforcement. The same unconditional return also excludes the refreshed base's current v5 gamma IDs despite D-131's 2026-09-02 `<N>` amendment.

Counterfactual sensitivity otherwise holds: in a temporary source copy, replacing the guard condition with an unconditional return caused the new module to fail five assertions; a direct unprojected three-unit projection with the canonical ID changed from REFUSE at HEAD to ACCEPTED under that mutant. The arm test's built-in no-op control likewise returned PASS. Thus the earlier false-counterfactual concern is closed at the asserted canonical-ID behavior, but the trusted-mutable-ID blocker remains open.

Scope evidence: the merge-base delta contains only the five implementer-declared paths. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and `docs/decision_log.md` have no delta. No previous `02-refuter-merge-base.md` was present at the refreshed head; the prompt-identified prior range-staleness issue was not re-raised.

## Residual risk

The real MLX-backed idempotent freeze and arm re-verification could not run in this environment. All four claimed test modules passed, the explicit frozen-byte preservation check retained the declared plan/tree digests, and no full suite was run per the preflight rule.
