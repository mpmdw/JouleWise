```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Round 4 cures R1; 109 tests pass, all 18 ordinary fixture plists are byte-identical, and the two regression plists differ exactly as intended.",
  "workspace": {
    "base_requested": "6dddb545",
    "base_mode": "exact",
    "head_start": "6dddb54569b71d56a3082453f9a899320fba6b55",
    "head_end": "6dddb54569b71d56a3082453f9a899320fba6b55",
    "upstream_end": "6dddb54569b71d56a3082453f9a899320fba6b55",
    "branch": "fix/2026-09-11-night-interpreter-pin"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "MERGEABLE",
    "comparison_base": "3b99a1a0",
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_install_night_agent tests.test_run_night > /tmp/night-pin-round4-suite.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 109 tests in 27.528s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 109 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/night-pin-round4-audit.py > /tmp/night-pin-round4-audit.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 109 tests in 27.500s",
          "OK",
          "FIXTURE_COMPARISON_PASS equal=18 intentional_difference=2 tests=109",
          "ARTIFACTS=/tmp/night-pin-round4-xyvq_dtb"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "FIXTURE_COMPARISON_PASS equal=18 intentional_difference=2 tests=109"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/night-pin-round4-r1.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "R1_REPRODUCER_PASS both argv0 equal validated interpreter; both executable; both plutil lint rc=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R1_REPRODUCER_PASS"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "/bin/zsh -n scripts/install_night_agent.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "diff -u /tmp/night-pin-round4-xyvq_dtb/08-test_install_with_both_pins_matching_renders_both_plists/3b99a1a0-com.joulewise.night.deadman.plist /tmp/night-pin-round4-xyvq_dtb/08-test_install_with_both_pins_matching_renders_both_plists/HEAD-com.joulewise.night.deadman.plist",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "diff -u /tmp/night-pin-round4-xyvq_dtb/09-test_install_with_both_pins_matching_renders_both_plists/3b99a1a0-com.joulewise.night.plist /tmp/night-pin-round4-xyvq_dtb/09-test_install_with_both_pins_matching_renders_both_plists/HEAD-com.joulewise.night.plist",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --check 3b99a1a0..HEAD; git status --porcelain=v1; git diff --exit-code; git diff --cached --exit-code; git rev-parse HEAD '@{upstream}'; git branch --show-current",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "6dddb54569b71d56a3082453f9a899320fba6b55",
          "6dddb54569b71d56a3082453f9a899320fba6b55",
          "fix/2026-09-11-night-interpreter-pin"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "fix/2026-09-11-night-interpreter-pin"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This delta audit ran on macOS. Ubuntu CI, canonical discovery, and live launchd or hardware validation were not performed.",
      "needs": "Lead retains final verification and merge authority."
    }
  ]
}
```

## Findings

None: **0 BLOCKER, 0 SHOULD_FIX, 0 NIT.**

1. **Render equivalence: PASS for every ordinary fixture rendered by the two modules.** The [audit helper](/tmp/night-pin-round4-audit.py) executes both commits’ extracted renderers with identical fixture values, checks HEAD bytes against actual installer output, and runs `diff -u`. Results:

   ```text
   FIXTURE_COMPARISON_PASS equal=18 intentional_difference=2 tests=109
   ```

   Both two-pins-matching plists—including the deadman job—produce empty diffs, rc 0 (V5/V6). The two intentional differences belong exclusively to the new token-name regression. Strictly, equivalence across *every current fixture* is therefore false by design.

2. **Token coverage and alternation: PASS.** At [scripts/install_night_agent.sh:196](/Users/edr/code/JouleWise-wt-interp-pin/scripts/install_night_agent.sh:196), all ten distinct template tokens have dictionary entries and match the regex. Command:

   ```sh
   grep -o '@@[^@]*@@' configs/launchd/com.joulewise.night.plist.template
   ```

   Output, with repeated occurrences consolidated:

   ```text
   @@PYTHON@@ @@REPO@@ @@MODE@@ @@PLAN@@ @@COURIER_BIN@@
   @@PATH@@ @@HOUR@@ @@MINUTE@@ @@CUSTODY_ROOT@@ @@LOG_STEM@@
   ```

   The helper’s comparison reports:

   ```text
   TOKEN_COVERAGE missing_from_dict=[] missed_by_regex=[] unused_dict_keys=[]
   ALTERNATION label=com.joulewise.night: reverse_order_equal=True unknown_preserved=True
   ALTERNATION label=com.joulewise.night.deadman: reverse_order_equal=True unknown_preserved=True
   ```

   Alternation order does not matter: the two alternatives cannot match at the same starting position. The deadman label is a replacement value, never rescanned. An original template occurrence of `com.joulewise.night.deadman` would have its prefix replaced once, just as with the old `str.replace`.

3. **R1: CURED.** V3 reuses the existing reproducer with only its fixture root redirected to a fresh HEAD-pinned fixture, preserving the earlier evidence. Output:

   ```text
   installer rc=0 stderr=''
   R1_REPRODUCER_PASS both argv0 equal validated interpreter; both executable; both plutil lint rc=0
   ```

   Both decoded paths retain `python @@MODE@@ & pinned`. The old renderer instead emits `python run & pinned` and `python dead-man & pinned`. The regression at [tests/test_install_night_agent.py:278](/Users/edr/code/JouleWise-wt-interp-pin/tests/test_install_night_agent.py:278) directly checks this defect.

4. **Same-signature statement:** rescanned substitution is the same defect as re-audit 04’s R1, which round 4 now cures. It is **not the defect class addressed by rounds 1–3**: whole-driver parsing under an older interpreter; uninstall/documentation inconsistencies; and the macOS-only bootstrap dependency. No surviving or newly found same-signature defect appears in this delta.

5. **Fresh-eyes review: no objection.** `import re` at [installer line 191](/Users/edr/code/JouleWise-wt-interp-pin/scripts/install_night_agent.sh:191) sits with the existing standard-library imports. The heredoc at line 189 uses `<<'PY'`. V2 extracts its source, passes it through zsh’s quoted-heredoc handling, compares the delivered bytes, and compiles them:

   ```text
   HEREDOC 3b99a1a0: byte_equal=True compile=PASS
   HEREDOC HEAD: byte_equal=True compile=PASS
   ```

   The literal-dot backslashes survive. The callable replacement also avoids interpreting replacement values as regex backreferences.

The requested suite passed **109 tests**; zsh syntax and diff whitespace checks passed. The repository remains clean at the requested HEAD. All audit artifacts are under `/tmp`.

## Residual risk

Ubuntu CI, canonical discovery, and live launchd/hardware checks were not rerun. Installation-shaped checks used render-only mode or existing fake-launchctl fixtures. Next step: lead final verification and merge disposition.

**VERDICT: MERGEABLE**