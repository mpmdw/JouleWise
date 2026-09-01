```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented the G2-a probe producer, window binder, read-only checker, runsheet integration, and targeted refusal coverage.",
  "workspace": {
    "base_requested": "bc19bfb6501f5b0dc88f23091e3e3d48865678a5",
    "base_mode": "exact",
    "head_start": "bc19bfb6501f5b0dc88f23091e3e3d48865678a5",
    "head_end": "bc19bfb6501f5b0dc88f23091e3e3d48865678a5",
    "upstream_end": null,
    "branch": "feat/2026-09-01-g2a-probe"
  },
  "pathspec": [
    "scripts/generate_g2a_probe_inputs.py",
    "scripts/gen_g2_phase_d.py",
    "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md",
    "tests/test_generate_g2a_probe_inputs.py",
    "tests/fixtures/g2a/probes/short-prompt-corpus.txt",
    "tests/test_check_window_provenance.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_generate_g2a_probe_inputs tests.test_check_window_provenance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 53 tests in 13.493s",
          "",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 53 tests in .*s\\n\\nOK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=\"$PWD\" /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_generate_g2a_probe_inputs tests.test_check_window_provenance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 53 tests in 14.748s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 53 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "build",
      "cmd": "python3 scripts/gen_g2_phase_d.py --check",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The standard python3 lacks the optional tokenizers package, so its real-tokenizer test skipped with a named reason; the project runtime ran the same 53 tests, including that test, with no skips.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The runsheet intentionally references the stream-2 summarizer, which this stream was forbidden to create.",
      "needs": "Land stream 2 before using the postprocessing block."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The operator must replace G2A_PROMPT_CORPUS='NEEDS-REVIEWED-PATH' with the reviewed prompt-source path before build-probes.",
      "needs": "Supply the reviewed source during lead preparation."
    }
  ]
}
```

## Change

Implemented all three subcommands, exact prompt/config/manifest generation, calibration-window binding, atomic create-new publication, and a read-only authentication check. The generated bracket now checks inputs before ledger readiness and reservation. Runsheet wording follows R2, and the summarizer and selector use `PYTHONPATH="$REPO"`.

The four closing sentences, measured in units produced by the pinned Qwen3 tokenizer, are:

- 512: “The record remains easy to inspect today.” — 8 tokens
- 1024: “The plan remains easy to audit and verify.” — 9 tokens
- 2048: “The plan remains easy to audit and simple to review.” — 11 tokens
- 4096: “The evidence remains easy to audit today.” — 8 tokens

The 2048 rung is exactly 291 repeats plus the required final sentence.

## Verification notes

No measurement or quiet-machine command ran. The central project runtime verified all four full prompt lengths with the real tokenizer.