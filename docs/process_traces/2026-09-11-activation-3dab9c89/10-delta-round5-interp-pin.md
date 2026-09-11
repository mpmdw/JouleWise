```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "F1, F3 and F4 are cured; all 110 focused tests pass; full merge-diff review found no new material objection.",
  "workspace": {
    "base_requested": "e46f06c8",
    "base_mode": "exact",
    "head_start": "e46f06c84359cef40a75fd97e298381321e57e6c",
    "head_end": "e46f06c84359cef40a75fd97e298381321e57e6c",
    "upstream_end": "1dddcfea573d85ee8facebc2b50dac412cb3b69f",
    "branch": "fix/2026-09-11-night-interpreter-pin"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "MERGEABLE",
    "findings": [],
    "cures": {
      "F1": "Baseline table restored; no other cell changed; both dated HEAD ranges verified.",
      "F3": "Four distinct derivation failures independently observed; all return installer rc 2 with exact single-line stderr.",
      "F4": "Only occurrence is glossed at first use; meaning matches NIGHT_HANDBACK and wording follows the dictated cure."
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_install_night_agent.InstallNightAgentTests.test_default_derivation_refuses_when_measurement_root_cannot_be_read",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.306s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 110 tests in 26.959s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 110 tests[\\s\\S]*OK"}
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "/bin/zsh -n scripts/install_night_agent.sh && git diff --check 6dddb545..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=\"$PWD\" python3 /tmp/pr321-round5-audit.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "empty-measurement-root: probe_rc=0; probe_tail='\\n'; installer_rc=2; exact_single_line=True; no_render_or_custody=True",
          "missing-key: probe_rc=1; probe_tail=KeyError: 'measurement_root'; installer_rc=2; exact_single_line=True; no_render_or_custody=True",
          "not-json: probe_rc=1; probe_tail=json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 3 (char 2); installer_rc=2; exact_single_line=True; no_render_or_custody=True",
          "no-python3-on-path: probe_rc=127; probe_tail=env: python3: No such file or directory; installer_rc=2; exact_single_line=True; no_render_or_custody=True",
          "F1: only the dictated table pin changed; full table equals origin/main; HEAD ranges match",
          "F4: exactly one --render-only occurrence, glossed at first use"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "F4: exactly one --render-only occurrence, glossed at first use"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git show d3cab2d4c2937886a25659756374483c7a8dc578:scripts/install_night_agent.sh | nl -ba | sed -n '39,75p;125,160p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["   160\tif [[ -z \"$render_only\" ]]; then"]
      },
      "expected": {"exit_code": 0, "tail_regex": "160"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## fix/2026-09-11-night-interpreter-pin...origin/fix/2026-09-11-night-interpreter-pin",
          "e46f06c84359cef40a75fd97e298381321e57e6c",
          "1dddcfea573d85ee8facebc2b50dac412cb3b69f"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "1dddcfea573d85ee8facebc2b50dac412cb3b69f"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Review exercised fixtures and stubbed launchctl, not live launchd or quiet-machine measurements. The repository-wide suite was not rerun in this bounded read-only audit.",
      "needs": ""
    },
    {
      "id": "R2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "F2 remains declined by the lead. The positive restricted-PATH test alone does not detect the former absolute plutil dependency on macOS; the string tripwire and Ubuntu CI remain its guards. Remote CI was not rerun here.",
      "needs": ""
    }
  ]
}
```

## Findings

No **BLOCKER**, **SHOULD_FIX**, or new material **NIT**.

**F1 — CURED.** `docs/contracts/pack_night_go_receipt.md:640` again names `:39–75,132–141`. V5 confirms that, at `d3cab2d4`, those ranges cover plan resolution/validation and the beginning of the renderer’s heredoc/substitution mapping. They are baseline seams, not a claim to encompass the entire renderer.

The dated sentence at `:631` correctly identifies HEAD’s NightPlan validation heredoc at `scripts/install_night_agent.sh:91–122` and complete `render()` function at `:182–220`, including its closing brace. V4 mechanically confirms that only the dictated table pin changed and the complete table now equals `origin/main`.

**F3 — CURED.** `tests/test_install_night_agent.py:274` passes verbosely (V1). Instrumentation replayed the exact derivation expression against each actual subTest fixture, without suppressing its underlying diagnostic (V4):

| Case | Underlying result | Installer result |
|---|---|---|
| Empty string | rc 0, stdout `"\n"`; substitution becomes empty, so `[[ -n ... ]]` fails | rc 2 |
| Missing key | rc 1, `KeyError: 'measurement_root'` | rc 2 |
| Non-JSON | rc 1, `JSONDecodeError` | rc 2 |
| No PATH Python | rc 127, `env: python3: No such file or directory` | rc 2 |

All four assert this exact single stderr line, including its final newline:

```text
cannot derive measurement_root/.venv/bin/python from <resolved-plan>; pass --python ABS_PATH
```

The instrumentation also confirmed empty stdout and no rendered or custody directory. The plan fixtures have distinct filenames.

The no-Python PATH contains exactly one directory, verified empty; `shutil.which("python3", path=...)` returns `None`. Before derivation at `scripts/install_night_agent.sh:54`, operations use zsh builtins and absolute `/usr/bin/grep`. Later commands **do** need PATH—particularly `mkdir` at `:175/:178` and `id` at `:180`—but execution exits at `:56`, before reaching them.

**F4 — CURED.** `docs/phase_2/derivation_night_runbook.md:1251` contains its sole `--render-only` occurrence, now with `DIR` and an immediate gloss. It matches `docs/process/NIGHT_HANDBACK.md:132` semantically, though not verbatim: “into `DIR`” versus “to a directory.” The new wording follows the dictated cure, and “Install and … default to … when `--python` is omitted” remains grammatical and accurate.

**Same-signature assessment.** These are different from the earlier runtime signatures: parsing the whole driver under an old interpreter, platform-specific bootstrap, and rescanning inserted substitutions. However, describing *every* round-5 issue as a wholly new class would overstate it: F4 repeats the earlier documentation-consistency/gloss omission in the second file, and F1 corrects provenance damage introduced by a previous cure. None of F1/F3/F4 survives at HEAD. F2’s accepted coverage limitation remains.

**Whole-unit review.** Reviewed all eight changed files in `git diff origin/main..HEAD`, including interpreter selection, version refusal, preflight/import hoisting, rendering, uninstall recovery, tests, and documentation. No additional material objection found. V2 reports **110 tests, OK**; syntax and whitespace checks pass. HEAD stayed fixed and the repository remained clean.

## Residual risk

Live launchd behavior and quiet-machine execution remain lead-owned gates; fixture success does not establish them. Preflight intentionally excludes lazy imports inside project functions. The full repository suite and remote Ubuntu CI were not rerun during this bounded audit.

**VERDICT: MERGEABLE**