```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The repeated failure is a circular open-world census; retire the fail-closed ratification mission and retain only metadata-free advisory analysis over mechanically discoverable syntax.",
  "workspace": {
    "base_requested": "9517ea31da86d5657ac311a434aa71679fef32ec",
    "base_mode": "exact",
    "head_start": "9517ea31da86d5657ac311a434aa71679fef32ec",
    "head_end": "9517ea31da86d5657ac311a434aa71679fef32ec",
    "upstream_end": "9517ea31da86d5657ac311a434aa71679fef32ec",
    "branch": "feat/2026-09-04-fan-EPOCH-LINT-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/EPOCH-LINT-01/07-consult-sol-structural.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "scripts/lint_runsheet_epoch.py:558-596; docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:829-835,3574-3584; tests/test_lint_runsheet_epoch.py:380-393",
        "text": "The ratifier treats the author's declarations as the complete universe, so an empty checks array proves only that the author declared nothing and cannot prove that the block has no obligations."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "location": "scripts/lint_runsheet_epoch.py:607-612,647-655",
        "text": "Historical replay accepts and consumes patch_overlay, so it can report PASS for bytes other than those in its named executing Git object; this is a distinct evidence-identity defect if replay is retained."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && git branch --show-current",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "9517ea31da86d5657ac311a434aa71679fef32ec",
          "feat/2026-09-04-fan-EPOCH-LINT-01"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "9517ea31da86d5657ac311a434aa71679fef32ec.*feat/2026-09-04-fan-EPOCH-LINT-01"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --shortstat \"$(git merge-base origin/main HEAD)\"..HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " 12 files changed, 2138 insertions(+), 3 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "12 files changed, 2138 insertions\\(\\+\\), 3 deletions\\(-\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The present branch should not land as a fail-closed ratification fence; the standing escalation requires the magistrate to retire or re-scope the mission.",
      "needs": "Adopt the Q4 ruling row before any further implementation round."
    }
  ]
}
```

## Findings

### Q1 — Structural cause (F1)

The repeated signature is specification circularity, not a missed member of a finite list. `_inline_checks` requires a declaration and a list, then trusts that list as the universe (`scripts/lint_runsheet_epoch.py:558-596`); consequently `{"checks":[]}` means both “audited and exempt” and “the author forgot every obligation.” The runsheet nevertheless calls those annotations a “complete revision census” (`docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:829-835`) and certifies only `check_count == 3` (`:890-894`), while the real `SuccessorPinsetDigestConditionTests` invocation sits under an empty list (`:3574-3584`); the production test repeats the same existential proof by asserting only three checks and three kinds (`tests/test_lint_runsheet_epoch.py:380-393`). A closed-world obligation-or-exemption label would merely move the self-attestation from `checks` to `exemption` and would not cure the class. Separately, F2 is not the repeated signature: allowing `patch_overlay` in both schemas and applying it without a mode guard (`scripts/lint_runsheet_epoch.py:607-612,647-655`) breaks the named-object meaning of historical replay.

### Q2 — Threat model under D-161

F1 is an operator-maintainability guard and should be removed from fail-closed ratification, not promoted into more machinery. D-161's exact recorded test retains fail-closed handling for plausible operator mistakes but retires deliberate-only defenses (`docs/decision_log.md:10390-10400`); here the relevant distinction is that the underlying mistakes are already loud at execution: an absent unittest target exits nonzero, a missing authenticator input makes the consumer refuse, and the separate `LINE-AUDIT-GUARD-01` owns the silent runtime-coordinate case (`docs/process/state_kernel.json:2344-2350`). Epoch lint therefore protects schedule and review convenience, not physics, raw-evidence identity, or a pre-registered analytical choice; making its self-authored inventory an additional transaction gate is over-engineering. F2 is the narrow opposite: if historical replay remains evidence, substituting overlay bytes is a real evidence-identity violation, so replay must read only the named Git object.

### Q3 — Cure that ends the class

RETIRE EPOCH-LINT-01 in its current fail-closed form; do not attempt a third census repair and do not land its inline declarations, ratification transcript gate, or overlay ceremony. If the diagnostics are worth keeping, re-home them under a new non-gating maintainability check whose universe is derived rather than declared: enumerate only mechanically recognizable unittest targets, governed CLI invocations, and formally shaped whole-symbol citations from the runsheet, take CLI requirements from a consumer-owned interface registry, warn on dynamic/unknown syntax, and use immutable Git objects with no overlays. The one proving test is the standing counterfactual: add `python -m unittest tests.sample.NoSuchClass` to an arbitrary executable block with no annotation at all and require the analyzer to discover and report it; no author-supplied metadata may participate in that result. If historical replay is retained alongside that advisory analyzer, the same design boundary simply rejects `patch_overlay` in replay mode.

### Q4 — Magistrate ruling row, verbatim

`| EPOCH-LINT-01 | RETIRE the fail-closed ratification mission under D-161: its repeated open-world census defect is an operator-maintainability problem, while the motivating commands already refuse at execution and LINE-AUDIT-GUARD-01 owns the silent coordinate case. Do not land the inline declarations, authenticated overlay, check-count transcript gate, or a third-round obligation/exemption census. If retained at all, re-home only automatically discoverable checks as a non-gating maintainability lint over immutable Git objects; an undeclared \`python -m unittest tests.sample.NoSuchClass\` must be discovered without author metadata. |`

## Residual risk

No executable prototype of the proposed metadata-free analyzer was built, and no tests were run because this is a structural ruling consult and the preflight permits tests only to confirm a specific claim. The recommended retirement depends on the magistrate confirming that the existing execution refusals plus `LINE-AUDIT-GUARD-01` remain the owning gates; if either ownership changes, that changed evidence boundary must be ruled separately rather than smuggled back into an advisory lint.
