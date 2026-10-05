```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented the authenticated complete-block stop and regenerated G2-b; acceptance needs an out-of-scope regression update.",
  "workspace": {
    "base_requested": "8fa002f7",
    "base_mode": "exact",
    "head_start": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "head_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "upstream_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "branch": "feat/2026-10-04-g2b-one-block-stop"
  },
  "pathspec": [
    "scripts/run_campaign.py",
    "scripts/gen_g2_phase_d.py",
    "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md",
    "docs/phase_2/window_runbook.md",
    "tests/test_run_campaign_max_blocks.py",
    "tests/test_gen_g2_phase_d.py",
    "tests/fixtures/campaign_max_blocks_legacy.jsonl"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-g2bstop python3 -m unittest tests.test_run_campaign_max_blocks tests.test_gen_g2_phase_d > /tmp/dd5-g2bstop/new-focused.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-g2bstop python3 -m unittest tests.test_run_campaign_max_blocks > /tmp/dd5-g2bstop/max-blocks-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-g2bstop python3 -m unittest tests.test_run_campaign tests.test_run_campaign_max_blocks > /tmp/dd5-g2bstop/campaign-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (errors=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-g2bstop JOULEWISE_CUSTODY_PARENT=/tmp/dd5-g2bstop/importer-custody JOULEWISE_ADDITIONAL_CUSTODY_PARENTS='[]' JOULEWISE_IDENTITY_PROBE=/tmp/dd5-g2bstop/importer-identity-probe python3 -m unittest tests.test_gen_g2a_window tests.test_generate_g2a_probe_inputs tests.test_harvest_g2a_window tests.test_controller_retry_backoff tests.test_schemas > /tmp/dd5-g2bstop/focused-importers.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK (skipped=2)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-g2bstop JOULEWISE_CUSTODY_PARENT=/tmp/dd5-g2bstop/importer-custody JOULEWISE_ADDITIONAL_CUSTODY_PARENTS='[]' JOULEWISE_IDENTITY_PROBE=/tmp/dd5-g2bstop/importer-identity-probe python3 -m unittest tests.test_collector_analysis_manifest_id > /tmp/dd5-g2bstop/collector-importer.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-g2bstop python3 -m unittest tests.test_check_window_provenance > /tmp/dd5-g2bstop/provenance-importer.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (errors=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-g2bstop python3 -m unittest tests.test_gen_derivation_night.GeneratedRegionTests.test_the_g2a_emitter_still_passes_its_own_check > /tmp/dd5-g2bstop/derivation-importer.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"
      }
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-g2bstop python3 scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS generated Phase D matches pinned runbook bytes"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS generated Phase D matches pinned runbook bytes"
      }
    },
    {
      "id": "V9",
      "kind": "inspection",
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
      "id": "V10",
      "kind": "inspection",
      "cmd": "git diff --exit-code -- joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py joulewise/controller.py",
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
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Unmodified tests/test_check_window_provenance.py still requires SCIENCE_RC=130 and the operator SIGINT card; its termination regression fails.",
      "needs": "Grant the exact test path and replace the obsolete termination assertions."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The campaign provenance first-run test times out after 60 seconds; isolated replay of 8fa002f7 reproduces the timeout.",
      "needs": "Recheck this pre-existing timeout in the lead test environment."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Git add failed: shared worktree index.lock creation was denied. Changes are uncommitted; nothing was pushed.",
      "needs": ""
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Interrupted an overbroad 1,031-test importer pass after identity-fixture failures. The affected collector tests and focused launch/render importers passed with the established identity fixture supplied.",
      "needs": ""
    }
  ],
  "scope_expansion": {
    "requested_paths": ["tests/test_check_window_provenance.py"],
    "reason": "Its pinned termination assertions require the retired SIGINT/130 procedure.",
    "blocked_work": "Green provenance importer regression and final acceptance.",
    "minimal_change": "Assert --max-blocks 1, registered rc 3 and absence of the SIGINT card; retain governed-chain ordering assertions."
  }
}
```

## Change

Added `--max-blocks`, registered return code **3**, and a terminal `max_blocks_reached` row. Only complete, strict-valid A/B/B/A blocks count. Authenticated `permitted_blocks` binds more strongly than CLI input: omission retains that limit, and conflicting values refuse before dispatch. Legacy unbound logs match the original fixture byte for byte after temporary-path substitution.

G2-b now runs only the first frozen science stage, checks rc 3, and continues through the post-bracket path without SIGINT.

The deferred plan writer should use v3 `TRANSACTION_PACK` serialization, binding the exact pack digest, attempt ordinal, chain digest, confirmation record, and authorization with `purpose=G2B_SHAKEDOWN`, `claim_eligible=false`, `permitted_blocks=1`, and D-167/D-171 authority. It also needs the measurement checkout, custody, and timing fields.

## Verification notes

The next exact step is to grant scope for `tests/test_check_window_provenance.py`, replace its obsolete termination assertions, and rerun that module.

The campaign timeout also reproduces at the requested base. Initial generator-pin failures were superseded by clean regenerated-chain checks. No whole suite or live measurement ran.

Changes remain uncommitted because Git metadata writes were denied. Nothing was pushed.