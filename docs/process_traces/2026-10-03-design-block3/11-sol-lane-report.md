```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented block-3 retry backoff; requested tests passed; Git staging and commit blocked by sandbox permissions.",
  "workspace": {
    "base_requested": "871a43f6",
    "base_mode": "exact",
    "head_start": "871a43f620a64f95152f3e50467225d52d7faa9e",
    "head_end": "871a43f620a64f95152f3e50467225d52d7faa9e",
    "upstream_end": "871a43f620a64f95152f3e50467225d52d7faa9e",
    "branch": "feat/2026-10-03-g2a-b3-retry-backoff"
  },
  "pathspec": [
    "configs/campaign_policies/quiet_mac_p2_g2a_b3.json",
    "joulewise/controller.py",
    "joulewise/schemas.py",
    "scripts/gen_g2_phase_d.py",
    "scripts/generate_g2a_probe_inputs.py",
    "scripts/harvest_g2a_window.py",
    "tests/fixtures/custody_read_replay_allowlist.json",
    "tests/test_controller_retry_backoff.py",
    "tests/test_gen_g2a_window.py",
    "tests/test_generate_g2a_probe_inputs.py",
    "tests/test_harvest_g2a_window.py",
    "tests/test_run_campaign.py",
    "tests/test_schemas.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_controller_retry_backoff tests.test_gen_g2a_window tests.test_harvest_g2a_window tests.test_summarize_g2a_prefill_probe tests.test_generate_g2a_probe_inputs tests.test_idle_admission tests.test_schemas tests.test_run_campaign > /tmp/g2a-b3-requested-tests.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 458 tests in 276.787s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_controller_retry_backoff > /tmp/g2a-b3-controller-final.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 7 tests in 2.793s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_custody_mode_inventory > /tmp/g2a-b3-custody-tests.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 7 tests in 39.321s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS generated Phase D matches pinned runbook bytes"]},
      "expected": {"exit_code": 0, "tail_regex": "^PASS generated Phase D matches pinned runbook bytes$"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-b3-clock-gap-audit.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS long-stream active-v3 drift audit"]},
      "expected": {"exit_code": 0, "tail_regex": "^PASS long-stream active-v3 drift audit$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "other",
      "cmd": "git add joulewise/schemas.py joulewise/controller.py configs/campaign_policies/quiet_mac_p2_g2a_b3.json scripts/gen_g2_phase_d.py scripts/generate_g2a_probe_inputs.py scripts/harvest_g2a_window.py tests/test_schemas.py tests/test_run_campaign.py tests/test_gen_g2a_window.py tests/test_harvest_g2a_window.py tests/test_generate_g2a_probe_inputs.py tests/test_controller_retry_backoff.py tests/fixtures/custody_read_replay_allowlist.json",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 128, "tail": ["fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-db3-code/index.lock': Operation not permitted"]},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V8",
      "kind": "suite",
      "cmd": "PYTHONPATH=/tmp/jw-b3-test-guard PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest discover -s tests > /tmp/g2a-b3-canonical-tests.log 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 130, "tail": ["KeyboardInterrupt"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "Sandbox denied Git index.lock creation. Changes remain unstaged; no commit was created.",
      "needs": "Lead must stage the pathspec files and commit on the named branch."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "This worktree has no .venv/bin/python. Tests used the existing canonical-checkout interpreter with this worktree as cwd.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Broader canonical discovery was interrupted after the requested module suite passed; no full-suite pass is claimed.",
      "needs": "Run the full suite through the lead's CI gate."
    },
    {
      "id": "F4",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The longer stream can trip the unchanged active-v3 5 ms clock-span cap. A synthetic 8 ppm example passes at 151 records and refuses at 751 records.",
      "needs": "Evaluate the clock-cap risk before the block-3 seal and final validation."
    }
  ]
}
```

## Change

Implemented bounded, default-zero backoff, the 600-second block-3 policy, exactly one generator policy substitution, four retry allowances, and inventory-bound harvest policy resolution with hash and directory checks.

**Commit SHA:** none; staging was denied. **`NIGHT_PROGRAMMED_SPAN_S`: 20,068.** **`ceil((span + 2700)/60)*60`: 22,800.**

The requested suite had **457 passes and one skip**. The final retry-specific and custody reruns each had **seven passes**. Generator checking passed.

Production policy bytes and normalized serialization remain unchanged. The runsheet source and all four pinned estimator files are byte-identical to the base.

| Consumer | Effect of a long inter-attempt gap | Evidence |
|---|---|---|
| Powermetrics adapter | Keeps one sampler; cursor catch-up excludes wait frames from attempt 2’s idle slice. Full retained stream grows. No gap ceiling found. | `adapters/powermetrics.py:452`, `:1219`, `:1302` |
| Strict CLI validation | No direct gap limit; reconstructs clock evidence from the entire raw stream, so clock refusals can change. | `cli.py:1269`, `:1292` |
| Environment admission | Allows monotonic attempt gaps. The 600-second freshness limit applies from **final attempt end** to measured start. | `environment_admission.py:161`, `:454`; retry fixture passes both validators |
| Whole-window validation | Uses the shared admission validator and final attempt’s telemetry; inherits clock-related refusals. | `whole_window.py:4236`, `:4245` |
| Reducer | Integrates measured marker windows, excluding wait energy. Reconstructs the anchor from all raw records. | `reduce.py:167`, `:711`, `:1794` |
| Clock-anchor estimator | Fits every native record. Longer support changes rate constraints and exposure to fixed drift limits. Active capture remains v3 with its 5 ms cap. | `uncertainty_evidence.py:785`, `:1070`, `:1110`, `:1246`, `:1460`; V5 |
| Summarizer | Reads retained prefill-window counts; no attempt-gap assumption. Clock offset diagnostics may change. | `summarize_g2a_prefill_probe.py:291`, `:573` |
| Harvest | No gap ceiling; strict validation and bounded-anchor requirements can invalidate a member. Both policy fixtures harvest successfully. | `harvest_g2a_window.py:167`, `:173`; harvest tests |
| Floor extraction / salvage | Floor extraction shares admission validation. Salvage bounds telemetry relative to run start and terminal failure, without a retry-gap ceiling. | `floor_extraction.py:1867`; `salvage_dangler.py:759`, `:803` |
| Runner / controller timeouts | No member or stage wall timeout found. Adapter slice deadlines start afresh; overall night-window expiry remains. | `run_campaign.py:1959`; `adapters/powermetrics.py:1256`, `:1468`; `run_night.py:914` |

No consumer requires the top-level production `policy_id` or a specific campaign `policy_version`. `profile` controls production/exploratory gates; the nested cooldown version requires `cooldown-v2`. Those values remain unchanged. Runner and controller provenance hash raw policy bytes; `CampaignPolicy.to_dict()` omits zero backoff, preserving the pinned historical digest.

## Verification notes

The missing worktree interpreter required the command substitution recorded above. Broad discovery was interrupted and remains unverified.

Git staging failed because the sandbox cannot write the worktree’s index lock. The next exact step is for the lead to stage the 13 `pathspec` files and commit them on `feat/2026-10-03-g2a-b3-retry-backoff`, then complete CI and final verification.

## Residual risk

A synthetic 8 ppm clock drift produced a bounded anchor over 151 seconds but exceeded the unchanged 5 ms cap over 751 seconds. This is an outside-scope finding: no estimator changes or live measurement were performed.