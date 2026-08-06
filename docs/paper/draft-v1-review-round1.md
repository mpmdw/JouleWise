```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REVISE: the quantitative method is faithful, but the retry paragraph incorrectly says the third failure closes the stage rather than the window; three smaller precision issues remain.",
  "workspace": {
    "base_requested": "af0b719",
    "base_mode": "exact",
    "head_start": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    "head_end": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    "upstream_end": "af0b7195cc9700a8c1d2f9e5305c20e923db4d4f",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "REVISE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "docs/paper/draft-v1.md",
        "line": 135,
        "title": "Third-failure rule names the wrong closure scope",
        "draft": "A third recurrence of the same cause closes the stage under the fixed protocol rule.",
        "correct": "Each stage attempt stops on its first member failure under --max-failures 1; after the same cause fails a window stage for the third time, the entire window closes rather than being retried.",
        "source": "docs/phase_2/window_runbook.md:363-381,620; docs/decision_log.md:5406-5409"
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file": "docs/paper/draft-v1.md",
        "line": 54,
        "title": "Calibration-bracket account omits the derived drift screen and budget rule",
        "draft": "The operative bound is the larger of the two.",
        "correct": "The operative bound is max(B_pre,B_post), but bracket drift is also screened against 10.817749309 ms (0.010818 s); a slight repeatability-only excess is propagated as added uncertainty, while an identified systematic defect is not budgetable.",
        "source": "docs/phase_2/detection_floor.md:757-783; docs/phase_2/window_runbook.md:701-728"
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "file": "docs/paper/draft-v1.md",
        "line": 36,
        "title": "Unqualified 'validation of powermetrics' is broader than the achieved validation",
        "draft": "JouleWise fills that gap ... [with] validation of powermetrics.",
        "correct": "The achieved validation concerns timing attribution under the named powermetrics boundary; the counter is not wall-calibrated and its absolute gain or whole-system scale remains unvalidated without an external meter.",
        "source": "docs/phase_2/detection_floor.md:398-405; docs/contracts/capstone_scope.md:44-46,108-119"
      },
      {
        "id": "F4",
        "severity": "nit",
        "file": "docs/paper/draft-v1.md",
        "line": 88,
        "title": "Idle-subtracted energy is used without a plain-language definition",
        "draft": "Gross energy and idle-subtracted energy are treated as separate claim families.",
        "correct": "Define idle-subtracted energy on first use as gross energy minus the measured idle-power baseline multiplied by the measured duration.",
        "source": "docs/phase_2/detection_floor.md:410-415,424-428"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "Resolve af0b719, impl/paper-draft-v1, and origin/impl/paper-draft-v1; require identical commit IDs and a clean git status; scan §7 for numeric J/W/ms values; scan the draft for D-/C- decision IDs; count result placeholders.",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "TARGET_EXACT af0b7195cc9700a8c1d2f9e5305c20e923db4d4f",
          "WORKTREE_UNCHANGED clean",
          "DEMO_VALUE_SCAN none",
          "INTERNAL_ID_SCAN none",
          "6 [PENDING WINDOW C]",
          "2 [RESULT PENDING RE-MINT]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "6 \\[PENDING WINDOW C\\]\\n[[:space:]]*2 \\[RESULT PENDING RE-MINT\\]"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The external literature and novelty assertions in §§1-2 and 8 were not independently source-verified; this review was limited to the specified method contracts and claims boundaries.",
      "needs": "Run a separate bibliography and novelty-claim audit before submission."
    }
  ]
}
```

## Findings

### F1 — Blocker: third-failure rule names the wrong closure scope

Draft, line 135:

> “A third recurrence of the same cause closes the stage under the fixed protocol rule.”

The runbook stops each stage attempt after its first member failure (`--max-failures 1`). The ratified third-failure rule instead says that after the same cause fails a window stage for the third time, the **window closes** rather than being retried. Sources: `docs/phase_2/window_runbook.md:363-381,620`; `docs/decision_log.md:5406-5409`.

### F2 — Should-fix: bracket handling is materially incomplete

Draft, line 54:

> “The operative bound is the larger of the two.”

That max rule is correct, but it omits a distinct part of the current method. Bracket drift is the absolute pre/post difference and is screened against the derived 10.817749309 ms limit. A slight repeatability-only excess is propagated into every floor and claim; an identified systematic defect cannot be absorbed by that budget. Sources: `docs/phase_2/detection_floor.md:757-783`; `docs/phase_2/window_runbook.md:701-728`.

### F3 — Should-fix: “validation of powermetrics” is too broad

Draft, line 36:

> “JouleWise fills that gap … [with] validation of `powermetrics`.”

The implemented evidence validates timing attribution under the named `powermetrics` boundary. It does not validate counter gain, wall energy, or absolute whole-system scale. The draft states that limitation correctly elsewhere, so this gap sentence should carry the same qualification. Sources: `docs/phase_2/detection_floor.md:398-405`; `docs/contracts/capstone_scope.md:44-46,108-119`.

### F4 — Nit: define idle subtraction

Draft, line 88 introduces “idle-subtracted energy” without explaining it. The contract definition is gross energy minus measured idle mean power multiplied by duration. Source: `docs/phase_2/detection_floor.md:410-415,424-428`.

Everything else in the requested numerical audit is faithful: 59 pulses; ≥4.5 s commanded-quiet baselines; 180 s default settling within 150–240 s; 3/1/3 references; 2–4 h targeting; ≥20% failure margin; both point-floor formulas; max-not-sum operative composition; the nonzero start/mid/end drift allowance; and approximately 1 J from ±31 ms across ~33 W, producing the approximately 5 J effective phase-contrast bar.

No real demonstration energy value appears. The draft contains six `[PENDING WINDOW C]` and two `[RESULT PENDING RE-MINT]` placeholders. No decision-log or council IDs leak into the prose, and the stack-specific, single-unit, same-boundary claim ceiling is consistently preserved.

## Residual risk

The cited literature and novelty assertions were not independently checked; they need a separate bibliography/related-work audit before submission.