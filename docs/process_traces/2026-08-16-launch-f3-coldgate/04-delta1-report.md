```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REJECT: most fixes verify cleanly, but F3 remains publicly reachable and its caller-path guard is forgeable; marker-bearing AXI dispatch also cannot locate launch custody.",
  "workspace": {
    "base_requested": "e7fa8fd37b2de27e6600cd74b91dbffc9871dec3",
    "base_mode": "exact",
    "head_start": "72cd69842434962d95176c9a625d256bc55f4fe5",
    "head_end": "72cd69842434962d95176c9a625d256bc55f4fe5",
    "upstream_end": "72cd69842434962d95176c9a625d256bc55f4fe5",
    "branch": "impl/wo-launch-binding"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "REJECT",
    "findings": [
      {
        "id": "F3",
        "severity": "blocker",
        "title": "Public consumption entrypoint remains reachable and its launcher-context check is forgeable",
        "paths": [
          "joulewise/arm_readiness.py",
          "scripts/launch_window.py"
        ],
        "text": "consume_launch_capability is absent from __all__ but remains a public module attribute. Both launcher-context checks trust the caller frame's mutable __file__. With neither context guard mocked, a caller setting __file__ to scripts/launch_window.py reached the writer and returned CONSUMED."
      },
      {
        "id": "NDF1",
        "severity": "should_fix",
        "title": "Marker-bearing AXI children derive custody from an unpopulated nested runs root",
        "paths": [
          "scripts/run_campaign.py",
          "joulewise/bundle.py",
          "joulewise/arm_readiness.py"
        ],
        "text": "AXI outer authentication uses the governed top-level runs root, but each child receives an axi_attempt_bundles/.../aN nested --runs-dir. The inner writer derives its fixed locator from that nested root, where no locator is published, and refuses launch_consumption_missing."
      }
    ],
    "confirmed": [
      "F2: a byte-differing semantic clone refuses launch_binding_mismatch; membership digests originate in the committed-pack-authenticated plan-tree inventory.",
      "F4: E-10 is explicitly NO-GO and names calibration-side, downstream, successor-marker, and gauntlet deferrals without claiming calibration-slot enforcement.",
      "B1: outer preflight lineage and selected-locator digest are retained before child start and compared post-hoc with child metadata; mismatch raises launch_lineage_conflict while preserving the bundle. No receipt, token, or lineage transport was added to argv or environment.",
      "S1/S2/N1: the ceremony mutant is killed; primary corruption is exercised; the mixed case uses two real authenticated lineages; retry-death after a precreated locator is asserted.",
      "Lifecycle: exactly four lifecycle tests were migrated to explicit readiness_usage_invalid assertions, while their race, boot-expiry, collision, and dry-run semantics remain exercised through launch_window.",
      "D-078 launch registrations were not expanded in the fix; the three frozen pack trees and the three lead-overruled F1 blobs are unchanged."
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest tests.test_arm_readiness",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 18 tests in 0.133s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 18 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest tests.test_arm_readiness_lifecycle",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 12 tests in 9.665s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 12 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest tests.test_launch_window",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 11 tests in 0.237s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 11 tests.*OK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest tests.test_bundle",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 74 tests in 25.054s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 74 tests.*OK"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest tests.test_run_campaign",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 239 tests in 460.168s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 239 tests.*OK"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest tests.test_d078_reason_registry",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 13 tests in 0.056s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 13 tests.*OK"}
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest tests.test_d117_floor_qwen25_1p5b_plan",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 18 tests in 3.179s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 18 tests.*OK"}
    },
    {
      "id": "V8",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest tests.test_d117_floor_qwen25_7b_plan",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 17 tests in 3.101s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 17 tests.*OK"}
    },
    {
      "id": "V9",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest tests.test_d117_decode_contrast_plan",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 15 tests in 3.146s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 15 tests.*OK"}
    },
    {
      "id": "V10",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -c 'import unittest; from unittest import mock; from tests import test_run_campaign as t; p=mock.patch.object(t.run_campaign_module,\"authenticate_campaign_launch_lineage\",return_value=None); p.start(); r=unittest.TestResult(); t.CampaignLaunchLineagePreflightTests(\"test_ceremony_bypass_refuses_before_lock_provenance_or_child\").run(r); p.stop(); assert len(r.failures)==1 and not r.errors; print(\"MUTANT_KILLED\",len(r.failures))'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["MUTANT_KILLED 1"]},
      "expected": {"exit_code": 0, "tail_regex": "MUTANT_KILLED 1"}
    },
    {
      "id": "V11",
      "kind": "smoke",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -c 'import hashlib; from contextlib import ExitStack; from pathlib import Path; from unittest import mock; import joulewise.arm_readiness as r; from tests.test_arm_readiness import LaunchConsumptionV2Tests as T; c=T(\"test_v2_claim_is_fsynced_and_replays_from_consumption\"); c.setUp(); globals()[\"__file__\"]=str(Path(r.__file__).resolve().parents[1]/\"scripts\"/\"launch_window.py\"); s=ExitStack(); s.enter_context(mock.patch.object(r,\"verify_arm_receipt\",return_value={\"pack_sha256\":c.arm[\"pack\"][\"pack_sha256\"]})); s.enter_context(mock.patch.object(r,\"reviewed_main\",return_value=c.arm[\"reviewed_main\"])); s.enter_context(mock.patch.object(r,\"_root_policy_refusals\",return_value=([],set()))); print(\"FORGED_CALLER_BYPASS\",r.consume_launch_capability(c.pack,c.arm_path,c.custody,launch_manifest=c.manifest_path,exec_argv=c.exec_argv,handoff_token_sha256=hashlib.sha256(b\"x\").hexdigest())[\"status\"]); s.close(); c.doCleanups()'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["FORGED_CALLER_BYPASS CONSUMED"]},
      "expected": {"exit_code": 0, "tail_regex": "FORGED_CALLER_BYPASS CONSUMED"}
    },
    {
      "id": "V12",
      "kind": "inspection",
      "cmd": "git diff --quiet e7fa8fd..72cd698 -- joulewise/analysis_engine/inputs.py joulewise/floor_extraction.py joulewise/whole_window.py && git diff --quiet e7fa8fd..72cd698 -- configs/campaigns/d117_floor_qwen25_1p5b_v1 configs/campaigns/d117_floor_qwen25_7b_v1 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1 && echo F1_BLOBS_AND_FROZEN_PACKS_UNTOUCHED",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["F1_BLOBS_AND_FROZEN_PACKS_UNTOUCHED"]},
      "expected": {"exit_code": 0, "tail_regex": "F1_BLOBS_AND_FROZEN_PACKS_UNTOUCHED"}
    }
  ],
  "flags": [
    {
      "id": "LR1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Contract-F1 was treated as overruled and not relitigated; inputs.py, floor_extraction.py, and whole_window.py are blob-identical across the range.",
      "needs": ""
    },
    {
      "id": "VG1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The repository-wide canonical suite was not run; all nine specifically requested focused suites passed.",
      "needs": ""
    }
  ]
}
```

## Findings

### F3 — blocker

`consume_launch_capability` was removed from `__all__`, but it remains directly present on `joulewise.arm_readiness` and is still imported by `launch_window.py`.

More seriously, both context checks at `arm_readiness.py:4751` and `:4884` authorize by comparing the caller frame’s mutable `__file__` global to `scripts/launch_window.py`. The adversarial reproduction changed only that global; neither context guard was mocked. It returned:

```text
FORGED_CALLER_BYPASS CONSUMED
```

Thus the legacy entrypoint is not actually retired, and a non-launcher caller can impersonate the launcher context. The direct all-None call does correctly refuse `readiness_usage_invalid`, and the reviewed launcher’s focused suite passes, but those facts do not close this bypass.

### NDF1 — should_fix

The AXI path authenticates the governed top-level runs root, then dispatches each child with a nested path such as:

```text
runs/axi_attempt_bundles/<manifest>/<entry>/a0
```

`RunBundleWriter` independently derives its locator from that nested `--runs-dir`. No locator is published there, and the nested path is not itself one of the two authenticated arm-context roots. A genuine-lineage fixture produced:

```text
OUTER_AUTH claim_runs_root
NESTED_CHILD_AUTH_REFUSAL launch_consumption_missing
```

This is fail-closed rather than a soundness bypass, but any future marker-bearing AXI campaign will be unable to run.

## Residual risk

Only the nine requested focused suites were run; the repository-wide canonical suite was not. The worktree remained clean and no repository file was modified.