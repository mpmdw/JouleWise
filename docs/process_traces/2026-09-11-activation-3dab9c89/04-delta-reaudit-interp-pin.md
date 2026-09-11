```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All requested cures and execution probes passed, including 108 tests; fresh-eyes review found one interpreter-path rendering defect.",
  "workspace": {
    "base_requested": "3b99a1a0",
    "base_mode": "exact",
    "head_start": "3b99a1a03e2c4a5ebfc020a5ac6ffde981c86a09",
    "head_end": "3b99a1a03e2c4a5ebfc020a5ac6ffde981c86a09",
    "upstream_end": "1dddcfea573d85ee8facebc2b50dac412cb3b69f",
    "branch": "fix/2026-09-11-night-interpreter-pin"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "MERGEABLE AFTER FIXES",
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "file": "scripts/install_night_agent.sh:197",
        "title": "Later template substitutions can change the validated interpreter path.",
        "evidence": "An executable named 'python @@MODE@@ & pinned' passes preflight and rendering returns 0, but the two plists name nonexistent 'python run & pinned' and 'python dead-man & pinned' executables.",
        "recommendation": "Substitute template tokens in one pass without rescanning replacement values, and add an exact-argv regression."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -B -m unittest tests.test_install_night_agent tests.test_run_night > /tmp/night-pin-reaudit-suite.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 108 tests in 27.361s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 108 tests in [0-9.]+s\\s+OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -B /tmp/night-pin-reaudit-probes.py > /tmp/night-pin-reaudit-probes.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ALL_PROBES_PASS ROOT=/private/tmp/night-pin-reaudit-uombs4j2"]
      },
      "expected": {"exit_code": 0, "tail_regex": "ALL_PROBES_PASS ROOT=/private/tmp/night-pin-reaudit-"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -B /tmp/night-pin-reaudit-render-regression.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "argv0 executable: FileNotFoundError",
          "AssertionError: rendered interpreter differs from validated --python"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": ""}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -B /tmp/night-pin-reaudit-extra.py > /tmp/night-pin-reaudit-extra.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "BASELINE tests=3 failures=7 errors=0",
          "EXTRA_PROBES_COMPLETE"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "BASELINE tests=3 failures=7 errors=0\\s+EXTRA_PROBES_COMPLETE"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "/bin/zsh -n scripts/install_night_agent.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "git diff --check origin/main..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "grep -c plutil scripts/install_night_agent.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["0"]},
      "expected": {"exit_code": 1, "tail_regex": "^0\\n?$"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git status --porcelain=v1; git diff --exit-code; git diff --cached --exit-code; git rev-parse HEAD origin/main; git branch --show-current",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "3b99a1a03e2c4a5ebfc020a5ac6ffde981c86a09",
          "1dddcfea573d85ee8facebc2b50dac412cb3b69f",
          "fix/2026-09-11-night-interpreter-pin"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "fix/2026-09-11-night-interpreter-pin"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Verification was performed on macOS. Ubuntu CI, the canonical discovery suite, and live launchd or hardware operation were not executed.",
      "needs": "Lead retains final CI, canonical-suite, live-gate, and merge verification."
    }
  ]
}
```

## Findings

**R1 — SHOULD_FIX: rendering can change the validated interpreter path.**

At [scripts/install_night_agent.sh:197](/Users/edr/code/JouleWise-wt-interp-pin/scripts/install_night_agent.sh:197), `@@PYTHON@@` is replaced before `@@MODE@@`; the loop at line 209 subsequently scans the inserted path.

A real executable symlink named `python @@MODE@@ & pinned` passes validation and preflight. Both rendered plists pass lint, but their executable paths differ from the validated path:

```text
installer rc=0 stderr=''
requested: .../bin/python @@MODE@@ & pinned

dead-man argv0: .../bin/python dead-man & pinned
night argv0:    .../bin/python run & pinned

Both: lint_rc=0
Both: argv0 executable: FileNotFoundError
```

Reproduction:

```sh
TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -B /tmp/night-pin-reaudit-render-regression.py
```

Observed rc 1:

```text
AssertionError: rendered interpreter differs from validated --python
```

This is an uncommon filename, but it violates the central guarantee that launchd receives the interpreter that passed validation. It originates in the seat landing, not rounds 1–3. Use substitution that does not rescan inserted values. No repository edits were made.

**Part A — delta dispositions**

| Earlier finding | Disposition | HEAD evidence |
|---|---|---|
| 08 F1 — whole-driver parsing under an old interpreter | **CURED** | `install_night_agent.sh:78–84` reads only the assignment. Real 3.9 still gives the intended version refusal when newer syntax follows it. |
| 09 F2 — contradictory night status | **CURED** | `NIGHT_HANDBACK.md:44–50,71–106` records the crash, completed harvest/retirement, item 5 MET, item 6 NOT MET, and nothing armed. |
| 09 F4 — uninstall rejects `--python` | **CURED** | Installer `:29–30,151–158,229–233`; isolated execution returned rc 0 and exactly the notice below. |
| 09 F5 — overstated preflight coverage | **CURED** | Handback `:143–149`, runbook `:1258–1264`, driver `:1872–1877` explicitly bound coverage to the driver and direct module-scope project imports. |
| 09 F6 — unexplained `--render-only` | **CURED** | Handback `:132–133` explains rendering two job files without installing them. |
| 09 F7 — explanation follows flag use | **CURED** | Runbook `:1245–1264` now precedes the arm block. `$PY` is exported at `:287`, required at `:1272`, and passed at `:1330`. |
| 09 F8 — missing glossary entry | **CURED** | Runbook §Terms `:175–178` and glossary `:2230` agree, including the exclusions. |

The “compatible interpreter” wording, indexed as **09 F9** but called F8 in report 17, is also cured at handback `:135–138`.

Additional requested checks:

- **`scripts.run_night` identity:** the preflight executes as `__main__`. Instrumentation printed `PREFLIGHT_NAME=__main__` and `NAMED_MODULE_LOADED=False`. A separate minimal-environment import succeeded and printed `scripts.run_night`, the correct file, and `(3, 11)`. The JSON entry is truthful as the driver’s canonical source-module name; it is not a literal `sys.modules` inventory. Installer `:161` also explicitly imports that named module.
- **Version regex:** HEAD’s exact bytes are `b'MIN_PYTHON = (3, 11)\n'`. They match. No spaces, extra spaces, and tabs around `=` all worked under real 3.9. Leading indentation does **not** match and produces `cannot find the MIN_PYTHON assignment in …`, rc 2. This preserves the current top-level literal convention; it is not a general Python assignment parser.
- **Handback reconciliation:** the crash, absent result/receipt, dead-man refusal, courier ID, archive location, item dispositions, and retirement agree with records 01/02. No new active pin is invented.
- **Record 13:** absent from this branch, but present in the supplied bookkeeping worktree as `13-arm-runbook-stub-20260912.md`, explicitly **DRAFT / NOT ARMED**. Acceptable as a forward pointer: the handback requires actual committed pins before arming. Records 01/02 likewise await their companion bookkeeping landing here.
- **Runbook variables:** the moved prose creates no new use-before-definition. The arm block checks its inherited variables; hour/minute are assigned before installation.

**Part A2 — round 3**

1. **Portable bootstrap: PASS.** Executed the exact source expression:

   ```python
   import json, sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["measurement_root"])
   ```

   Under `/usr/bin/python3` **3.9.6**, `/opt/homebrew/bin/python3` **3.14.7**, and the real venv interpreter, `-B -S` returned the expected measurement root, rc 0, empty stderr. It uses only stdlib facilities and no project imports. The full installer also succeeded with ambient `python3` explicitly linked to Apple’s 3.9.

2. **`-S`: PASS for all three interpreters.** Each reported `sys.flags.no_site == 1`; JSON parsing remained functional. This bootstrap needs no site packages.

3. **zsh precedence: PASS.** The expression behaves as `(A && nonempty) || refusal`. Empty root, missing key, and non-JSON input each returned **rc 2**, empty stdout, and exactly one stderr line:

   ```text
   cannot derive measurement_root/.venv/bin/python from /private/tmp/night-pin-reaudit-uombs4j2/empty.json; pass --python ABS_PATH
   cannot derive measurement_root/.venv/bin/python from /private/tmp/night-pin-reaudit-uombs4j2/missing.json; pass --python ABS_PATH
   cannot derive measurement_root/.venv/bin/python from /private/tmp/night-pin-reaudit-uombs4j2/not-json.json; pass --python ABS_PATH
   ```

   No ambient `python3` likewise produced the prescribed refusal, without leaked shell diagnostics.

4. **Suppressed diagnostic:** `2>/dev/null` hides the distinction between unavailable Python, malformed JSON, and missing keys. I accept the deliberate single-line refusal here. More diagnostic detail would be optional usability polish, at most a nit.

5. **No-courier fixture: PASS.** Its PATH directory contained exactly `["python3"]`. Observed rc 2:

   ```text
   courier unavailable: command -v claude found no executable
   ```

   The test still reaches and tests courier absence.

6. **Contract pin cell: accurate.** Installer `:91–122` is the NightPlan validation heredoc. `:182–212` covers `render()` and its heredoc; the closing shell brace is `:213`. That one-line boundary omission does not misidentify the function.

7. **Historical runbook pins: agree with preservation.** Runbook 67 identifies its preparation commit at line 3 and confines itself to that dated night. `git show 7ca2908f…:scripts/install_night_agent.sh` confirms its `:81–96` pin checks and `:123–125` custody creation references. Retaining those historical pins is appropriate now that the handback retires that night and routes future arming elsewhere.

The no-`plutil` tripwire passes. The restricted-PATH regression is useful execution coverage, but on macOS it would also pass before round 3 because the old absolute `/usr/bin/plutil` remains available; the text tripwire and Linux CI distinguish that defect.

**Part B — execution evidence**

All fixtures and probe scripts are under `/tmp` (resolved as `/private/tmp`).

**B1: real venv, no `--python`.** Created a temporary Git measurement repository and ran `/opt/homebrew/bin/python3 -B -m venv …/.venv`. The v2 `REHEARSAL_STUB` installer render returned **rc 0**, empty stderr. Both plists have:

```text
ProgramArguments[0] = /private/tmp/night-pin-reaudit-uombs4j2/measurement/.venv/bin/python
```

Exact preflight line:

```json
{"preflight": "ok", "python": "/private/tmp/night-pin-reaudit-uombs4j2/measurement/.venv/bin/python", "version": "3.14.7", "modules": ["scripts.run_night", "joulewise.arm_readiness", "joulewise.arm_readiness_evidence_t0", "joulewise.t0_rehearsal", "joulewise.night_gate", "joulewise.measurement_liveness"]}
```

**B2: explicit real 3.9.** **rc 2**, empty stdout, exact stderr:

```text
interpreter /usr/bin/python3 reports Python 3.9; minimum is 3.11
```

**B3: space-and-ampersand symlink.** **rc 0**, empty stderr. Both `/usr/bin/plutil -lint` calls returned rc 0:

```text
/private/tmp/night-pin-reaudit-uombs4j2/render-spaced/com.joulewise.night.deadman.plist: OK
/private/tmp/night-pin-reaudit-uombs4j2/render-spaced/com.joulewise.night.plist: OK
```

Both decoded arrays contain seven elements, with this entire string as one element:

```text
ProgramArguments[0] = /private/tmp/night-pin-reaudit-uombs4j2/bin/python space & pinned
```

**B4: isolated uninstall.** The fixture checkout contained only the installer and template—no driver, project package, or venv. Passed `--python /missing/recovery/python` and an explicit fake launchctl. **rc 0**, empty stdout, exact stderr:

```text
--python ignored on uninstall
```

Exact fake-launchctl calls:

```text
bootout gui/501/com.joulewise.night
bootout gui/501/com.joulewise.night.deadman
```

Both fixture plists were removed; no custody directory was created.

**B5: two modules.**

```text
Ran 108 tests in 27.361s

OK
```

Additionally, three current defect-shaped tests executed against immutable `origin/main` installer/template bytes under `/tmp`: all three failed as expected, with seven failed assertions including subtests and zero errors.

Replay scripts and complete outputs: [requested probes](/tmp/night-pin-reaudit-probes.py), [probe log](/tmp/night-pin-reaudit-probes.log), [suite log](/tmp/night-pin-reaudit-suite.log), [R1 reproducer](/tmp/night-pin-reaudit-render-regression.py).

## Residual risk

Ubuntu CI and the canonical discovery suite were not rerun. All installation-shaped checks used render-only mode or fake launchctl; they establish no live launchd or hardware result. Final verification remains lead-owned.

The repository remained clean at the requested HEAD. Next exact step: repair R1’s substitution behavior, rerun its reproducer and the focused modules, then complete lead verification.

**VERDICT: MERGEABLE AFTER FIXES**