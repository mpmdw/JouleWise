```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Four findings: valid live-process shapes and invalid successful censuses bypass refusal; existing tests pass and the substring mutation is killed.",
  "workspace": {
    "base_requested": "HEAD~1",
    "base_mode": "exact",
    "head_start": "a37de2ec31d32be02cec0fa5c3ffd9bde6c5da83",
    "head_end": "a37de2ec31d32be02cec0fa5c3ffd9bde6c5da83",
    "upstream_end": "71588d6ab4e99bae3057e59463c27d2fe471dac7",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 2, "should_fix": 2, "nit": 0},
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "scripts/window_status.sh",
        "line": 74,
        "summary": "The exact window-chain basename restriction misses valid run_night chains with other filenames, including the requested emitted chain.",
        "command": "python3 -B /tmp/window-guard-review.galiun/probe.py g2a_full_settle",
        "observed": "rc=0 wrote=True for a census containing run_night, /bin/zsh /tmp/window-guard-review.galiun/chain, and /bin/sleep 600",
        "expected": "Refuse before writing."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "file": "scripts/window_status.sh",
        "line": 57,
        "summary": "Whitespace tokenization misses campaign scripts, Python executables, and window-chain paths containing spaces.",
        "command": "python3 -B /tmp/window-guard-review.galiun/probe.py space_script",
        "observed": "rc=0 wrote=True for python3 /repo with space/scripts/run_campaign.py /configs; space_interpreter and space_chain also bypass",
        "expected": "Refuse before writing."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "file": "scripts/window_status.sh",
        "line": 61,
        "summary": "The interpreter-option parser misses Python's valid -- separator.",
        "command": "python3 -B /tmp/window-guard-review.galiun/probe.py python_separator",
        "observed": "rc=0 wrote=True for python3 -- scripts/run_campaign.py /configs",
        "expected": "Refuse before writing."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "file": "scripts/window_status.sh",
        "line": 44,
        "summary": "Successful census commands returning garbage or no process records fail open.",
        "command": "python3 -B /tmp/window-guard-review.galiun/probe.py garbage",
        "observed": "rc=0 wrote=True for THIS IS NOT A PROCESS CENSUS; empty_census also writes",
        "expected": "Reject an unusable census before writing."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_window_status_guard",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 5 tests in 2.058s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 -B /tmp/window-guard-review.galiun/probe.py",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 0, "tail": ["Selected live shapes and invalid censuses returned rc=0 and wrote=True."]},
      "expected": {"exit_code": 0, "tail_regex": "Live shapes and invalid censuses must return rc=1 wrote=False"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B /tmp/window-guard-review.galiun/mutate.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["FAILED (failures=1)", "MUTANT_KILLED=True"]},
      "expected": {"exit_code": 0, "tail_regex": "MUTANT_KILLED=True"}
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "bash -n scripts/window_status.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "other",
      "cmd": "python3 -B scripts/gen_g2_phase_d.py --emit-chain /tmp/window-guard-review.galiun/chain --night-date 20260910",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["emitted /tmp/window-guard-review.galiun/chain"]},
      "expected": {"exit_code": 0, "tail_regex": "emitted .*/chain"}
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Shellcheck is unavailable. bash -n passed.",
      "needs": ""
    },
    {
      "id": "E2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The supplied workspace is detached at the reviewed commit. Repository files and HEAD remained unchanged; probes and mutation artifacts are under /tmp.",
      "needs": ""
    }
  ]
}
```

## Findings

**F1 — blocker:** `scripts/window_status.sh:74` assumes a filename that `run_night.py:1237` does not require. The driver launches `plan.chain_path`; the generator accepts an arbitrary output path. During the emitted chain’s settling periods, neither the driver nor `sleep` compensates for the missed chain. The demonstrating command is in the envelope.

**F2 — blocker:** `scripts/window_status.sh:57` treats flattened `ps` text as argument boundaries. Spaces in the interpreter, campaign path, or chain path defeat detection. All three injected variants wrote status.

**F3 — should_fix:** `scripts/window_status.sh:61` skips selected Python flags but omits `--`, allowing a valid standalone campaign invocation through.

**F4 — should_fix:** `scripts/window_status.sh:44` checks only the census command’s exit status. Exit 7 correctly refuses without writing; garbage and empty successful output both write.

## Residual risk

These were injected-census checks, not live measurement validation.

Ordinary campaign, module, venv, and historical shell-chain shapes refuse. Historical `caffeinate` and campaign-child rows are individually missed, but their complete censuses refuse through the shell or campaign parent. The literal `/usr/bin/env python3 …` row is missed; ordinarily `env` replaces itself with Python, so that alone does not establish a sustained bypass.

All five requested non-measurement shapes pass without refusal. The temporary substring mutation preserves census injection and causes the sibling-process regression to fail as required.