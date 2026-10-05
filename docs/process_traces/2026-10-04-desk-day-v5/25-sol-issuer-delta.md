```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "DELTA: PASS — F1/F2 counterexamples resolved; anchor, supersession, prior checks, and focused suite verified.",
  "workspace": {
    "base_requested": "a1126009",
    "base_mode": "descendant",
    "head_start": "c783f0ee9f8e44e6fb1854f021f48714f513e597",
    "head_end": "c783f0ee9f8e44e6fb1854f021f48714f513e597",
    "upstream_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "line": "DELTA: PASS",
    "findings": [],
    "dry_issue": {
      "exit_code": 0,
      "pin_sha256": "d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb",
      "g2a_record_sha256": "c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222"
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-isdelta PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_issue_g2a_prefill_prompt_pin.py tests/test_summarize_g2a_prefill_probe.py tests/test_select_g2a_prefill_length.py tests/test_d117_contrast_v5_pack.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["103 passed, 209 subtests passed in 110.45s (0:01:50)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "103 passed, 209 subtests passed"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/dd5-isdelta PYTHONDONTWRITEBYTECODE=1 HF_HOME=/tmp/dd5-isdelta/hf HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-isdelta/verify_findings.py real_select",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-isdelta PYTHONDONTWRITEBYTECODE=1 HF_HOME=/tmp/dd5-isdelta/hf HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-isdelta/verify_findings.py relabeled_block2",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["{\"case\": \"relabeled_block2-ot2uhev_\", \"exit_code\": 2, \"expectation_met\": true, \"expected_exit\": 2, \"expected_refusal\": null, \"no_live_path_opened\": true, \"open_events\": 12, \"refusal\": \"archive_sha256sum_mismatch\"}"]
      },
      "expected": {"exit_code": 0, "tail_regex": "archive_sha256sum_mismatch"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-isdelta PYTHONDONTWRITEBYTECODE=1 HF_HOME=/tmp/dd5-isdelta/hf HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-isdelta/verify_findings.py reconstructed_select",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["{\"case\": \"reconstructed_select-qwbwk_s4\", \"exit_code\": 2, \"expectation_met\": true, \"expected_exit\": 2, \"expected_refusal\": null, \"no_live_path_opened\": true, \"open_events\": 15, \"refusal\": \"harvest_committed_harvest_mismatch\"}"]
      },
      "expected": {"exit_code": 0, "tail_regex": "harvest_committed_harvest_mismatch"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-isdelta PYTHONDONTWRITEBYTECODE=1 HF_HOME=/tmp/dd5-isdelta/hf HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-isdelta/verify_findings.py excluded_large",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: actual summarizer reproduces the excluded-large SELECT summary and counts"]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS: actual summarizer reproduces the excluded-large SELECT summary and counts"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-isdelta PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-isdelta/check_anchors.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS: anchor invokes git show HEAD in issuer repository from non-git caller cwd",
          "PASS: missing-record; exit=2; committed_window_record_missing; no pin",
          "PASS: no-checkout; exit=2; committed_window_record_missing; no pin",
          "PASS: superseded-r1; exit=2; harvest_committed_harvest_mismatch; no pin",
          "PASS: all anchor and supersession checks"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS: all anchor and supersession checks"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-isdelta PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-isdelta/check_round_checks.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: all prior receipt constraints retained"]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS: all prior receipt constraints retained"}
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp/dd5-isdelta PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
      },
      "expected": {"exit_code": 0, "tail_regex": ""}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Fixture-orphan census could not observe processes because the sandbox denied ps. This does not affect the completed delta checks.",
      "needs": ""
    }
  ]
}
```

## Findings

DELTA: PASS

No findings. F1/F2 are resolved within the stated threat model. The superseded r1 RECOVER cannot count toward an end state. Anchor location and clean refusal behavior passed; no round-1/2 check weakening was found.

Repository unchanged and clean. Evidence and replays: [/tmp/dd5-isdelta/](/tmp/dd5-isdelta/).

## Residual risk

V6 uses a mocked reviewed-record snapshot to isolate the permitted validity-filtered SELECT. Successful end-state coverage remains fixture-based, without live hardware validation.