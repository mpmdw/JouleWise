```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "B1 and S2 cured; S1 still misstates the registered ratio and introduces first-use gaps. All 98 focused tests and generator check pass.",
  "workspace": {
    "base_requested": "1f8c1174",
    "base_mode": "descendant",
    "head_start": "dc93749c2a0848fefe728fc4d9b78615dcba9bf3",
    "head_end": "dc93749c2a0848fefe728fc4d9b78615dcba9bf3",
    "upstream_end": "dc93749c2a0848fefe728fc4d9b78615dcba9bf3",
    "branch": "fix/2026-09-11-c1-registration-seam"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "MERGEABLE AFTER FIXES",
    "findings": [
      {
        "id": "S1",
        "severity": "should_fix",
        "path": "docs/phase_2/derivation_night_runbook.md",
        "line": 504,
        "summary": "The dictated replacement describes measured energy difference versus widened uncertainty, but the registration compares corner-widened unguarded floor versus point unguarded floor."
      },
      {
        "id": "S3",
        "severity": "should_fix",
        "path": "docs/phase_2/derivation_night_runbook.md",
        "line": 503,
        "summary": "The new explanation introduces _v5 contrast campaign, widened uncertainty bound, and falsifier without building or glossing them."
      }
    ],
    "cured": ["B1", "S2"]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "grep -n '\\$H:' docs/phase_2/derivation_night_runbook.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": []},
      "expected": {"exit_code": 1, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "/bin/zsh <<'ZSH'\nMEASUREMENT_ROOT=$PWD\nH=$(git rev-parse HEAD)\ngit -C \"$MEASUREMENT_ROOT\" rev-parse \"${H}:configs/calibration/preregistration_d079_epoch_25g83_rev1.md\"\ngit -C \"$MEASUREMENT_ROOT\" show \"${H}:configs/calibration/preregistration_d079_epoch_25g83_rev1.md\" | shasum -a 256\nZSH",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ac56d931c025f639df4aeab98f32681fb02e83ba",
          "ca2430ddd04b4a95b3ea0420ecf4d0897e1d1409f9d4f9f102414d00c37a5da7  -"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "ca2430ddd04b4a95b3ea0420ecf4d0897e1d1409f9d4f9f102414d00c37a5da7  -"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_night_gate.RegistrationSeamTests.test_runbook_never_writes_unbraced_dollar_h_before_a_colon",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.001s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "git show 1f8c1174:docs/phase_2/derivation_night_runbook.md > /tmp/rb.md\nPYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 - <<'PY'\nfrom pathlib import Path\nimport re\nimport unittest\nfrom tests.test_night_gate import RegistrationSeamTests\nfor n, line in enumerate(Path('/tmp/rb.md').read_text().splitlines(), 1):\n    if re.search(r'\\$H:', line):\n        print(f'{n}: {line.strip()}', flush=True)\nRegistrationSeamTests.RUNBOOK = Path('/tmp/rb.md')\ncase = RegistrationSeamTests('test_runbook_never_writes_unbraced_dollar_h_before_a_colon')\nresult = unittest.TextTestRunner(verbosity=1).run(unittest.TestSuite([case]))\nraise SystemExit(not result.wasSuccessful())\nPY",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 1 test in 0.001s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_gen_derivation_night tests.test_night_gate",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 98 tests in 22.693s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 98 tests[\\s\\S]*OK"}
    },
    {
      "id": "V6",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 scripts/gen_derivation_night.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS generated derivation-night wrapper region matches"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS generated derivation-night wrapper region matches"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --check 1f8c1174..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Findings

**S1 — SHOULD_FIX: the replacement still misdescribes the criterion.**  
`docs/phase_2/derivation_night_runbook.md:504–506` says a measured energy difference counts only when at least twice the widened uncertainty bound. That is **not** the registered comparison. The error originates in counter-review 07’s dictated cure, which round 2 faithfully applied.

Primary evidence:

```text
$ sed -n '525,537p' configs/campaigns/d117_contrast_v5/generate_configs.py
def dominance_criterion_registration() -> dict[str, Any]:
    """Return the frozen D-165 ratio and common-mode replay contract."""

    return {
        "kind": "comparative",
        "ratio_id": DOMINANCE_RATIO_ID,
        "numerator": "corner_widened_unguarded_floor_j",
        "denominator": "point_unguarded_floor_j",
        "threshold": DOMINANCE_THRESHOLD,
        "comparison": DOMINANCE_COMPARISON,
        "exact_equality_policy": "R == 2.0 passes",
        "per_component": True,
        "all_must_pass": True,
```

The registration-builder inspection and byte comparison returned:

```text
builder equals JSON: True
canonical builder bytes equal file: True
sha256: dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265
matches C1 constant: True
ratio_id: attribution_dominance_ratio.v1
numerator: corner_widened_unguarded_floor_j
denominator: point_unguarded_floor_j
threshold: 2.0
comparison: greater_than_or_equal
per_component: True
all_must_pass: True
common_mode.ratio_id: attribution_dominance_ratio_common_mode.v1
common_mode.threshold: 2.0
common_mode.withdrawal_comparison: R_cm < 2.0
common_mode.withdrawal_consequence: withdraw_dominance_sentence
```

`docs/decision_log.md:211` explicitly defines **R = corner-widened unguarded bound / point unguarded bound**, requiring R ≥ 2 per component per cell. The D-165 entry at `:10728` agrees; its addendum at `:11270` retains thresholds while limiting the common-mode interpretation to a sensitivity diagnostic. `joulewise/dominance_closeout.py:517–537` implements exactly that division and comparison.

The other claims are supported:

- The file contains the contrast campaign’s pre-registered D-165 criterion.
- Its filename names D-166; D-166 itself concerns workload (`decision_log.md:10751`, amended at `:11290`).
- `night_gate.py:34–40` pins this path and digest; `:1300–1328` authenticates its bytes for `DIAGNOSTIC_NO_PACK` and `REHEARSAL_STUB`, without evaluating the criterion’s physics.

**Required correction:** explain the ratio of the two registered floors and its dominance-claim consequence. Do not describe an energy-difference acceptance threshold.

**S3 — SHOULD_FIX: the new sentence fails the requested first-use test.**  
`docs/phase_2/derivation_night_runbook.md:503–506` introduces campaign shorthand and technical terms without explaining them. The census returned:

```text
_v5: first occurrence in the path at 502; prose at 503
dominance criterion: 503
widened uncertainty bound: 505
falsifier: 506
```

Command: `rg -n -i 'uncertainty|falsifier|dominance|contrast campaign|_v5' docs/phase_2/derivation_night_runbook.md`.

“Dominance criterion” receives an immediate but inaccurate gloss (S1); “widened uncertainty bound” and “falsifier” receive none. `_v5` is only inferable from the preceding pathname. Build these concepts accurately or remove unnecessary terminology. C1 and receipt class retain adjacent glosses at `:508–511`.

**B1 — CURED.** V1–V4 establish no remaining literal match, successful zsh execution, and a regression that rejects the previous runbook.

Exact §1.5 line (`:1432`), inside its fenced `zsh` block:

```zsh
git -C "$MEASUREMENT_ROOT" rev-parse "${H}:configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
```

Exact §2.5 line (`:1759`):

````text
`git -C "$MEASUREMENT_ROOT" show "${H}:configs/calibration/preregistration_d079_epoch_25g83_rev1.md" | shasum -a 256` (braced `${H}`: zsh reads an unbraced dollar-H followed by a colon as a history-style modifier and eats the colon, so git would hash nothing),
````

§2.5 uses **inline code**, not a fenced block. Both commands work in `/bin/zsh`: `${H}` terminates parameter expansion before the literal colon. The returned digest is `ca2430dd…`, not `e3b0c442…`.

Against `1f8c1174`, the actual new test fails with exactly these offenders:

```text
1428: git -C "$MEASUREMENT_ROOT" rev-parse "$H:configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
1755: `git -C "$MEASUREMENT_ROOT" show "$H:configs/calibration/preregistration_d079_epoch_25g83_rev1.md" | shasum -a 256`,
```

**S2 — CURED.** Item 1 at `:1423` explicitly distinguishes the frozen calibration plan from `night_plan.json`. `$CALIBRATION_PLAN` is real:

```text
345:export CALIBRATION_PLAN="$NIGHT_ROOT/calibration_plan.json"
```

The variable’s table entry at `:374` defines the frozen committed capture plan; generator invocations use it at `:940`, `:1011`, and `:1292`. No invented-variable finding or replacement name is warranted.

**Same-signature assessment:** round 2’s original classes—zsh command expansion and factual misdescription—differ from round 1’s first-use gloss defect. The factual-misdescription class survives as S1. The replacement also introduces another first-use gap, S3, recurring at round 1’s class level.

## Residual risk

The regex scans every line regardless of Markdown context. It catches inline code and prose, including a legitimate explanatory sentence containing `"$H:"`; it can therefore reject documentation of the defect itself. The new parenthetical avoids that literal by spelling out “dollar-H followed by a colon.”

Verification was desk-only: the requested 98-test suite and generator check passed; no live capture or hardware gate ran. No repository files changed, and the worktree remained clean. The next step is lead correction of S1/S3 followed by a bounded delta check.

VERDICT: MERGEABLE AFTER FIXES