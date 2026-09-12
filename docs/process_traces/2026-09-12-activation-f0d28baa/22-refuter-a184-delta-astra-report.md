```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "B1's output claim is corrected; one new harvest-instruction blocker and two wording should-fixes remain. Both requested checks pass.",
  "workspace": {
    "base_requested": "7014dd0e",
    "base_mode": "exact",
    "head_start": "ca7346e423d4fdc490190d5411c600c84b0aa729",
    "head_end": "ca7346e423d4fdc490190d5411c600c84b0aa729",
    "upstream_end": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "B2",
        "severity": "blocker",
        "path": "docs/phase_2/derivation_night_runbook.md",
        "line": 1670,
        "summary": "The universal harvest-checkout instruction contradicts the mandatory second-checkout replay in section 2.5.",
        "evidence": "Lines 1835-1839 require running the equivalence tool once from the clone and once from a second checkout at the same head. 'Harvest always uses the night's frozen clone, never main' excludes that required second execution.",
        "requested_change": "Replace 'Harvest always uses the night's frozen clone, never main.' with 'Run the recovery tool from the night's frozen clone (§2.4); the equivalence check separately requires a second run from another checkout at the same head (§2.5).'"
      },
      {
        "id": "S1",
        "severity": "should_fix",
        "path": "docs/phase_2/derivation_night_runbook.md",
        "line": 1667,
        "summary": "The date parenthesis substitutes a calendar date for actual merge state.",
        "evidence": "A September 12 merge makes 'after 2026-09-12' imprecise for same-day availability; a later merge leaves an interval after that date when main still lacks the mapping. The preceding checkout-content qualification limits the operational risk.",
        "requested_change": "Replace '`calibration_window_exhausted` only in checkouts that contain that code (main after 2026-09-12).' with '`calibration_window_exhausted` only in checkouts that contain that code.'"
      },
      {
        "id": "S2",
        "severity": "should_fix",
        "path": "docs/phase_2/derivation_night_runbook.md",
        "line": 1666,
        "summary": "'Refusal code' is used without an earlier or inline definition.",
        "evidence": "Earlier passages explain refusal behavior and numeric exit statuses, but do not define this diagnostic-label term. Section 5, lines 2136-2143, only later supplies a Refusal code / Meaning table.",
        "requested_change": "Replace 'refusal code, run from the checkout you harvest with' with 'refusal code—a machine-readable diagnostic label—run from the checkout you harvest with'."
      }
    ],
    "b1_closed": true,
    "same_signature": "Yes at the checkout-instruction level: the new universal harvest statement describes the first execution but is false for the operator's required second-checkout execution. The corrected refusal-output claim itself does not repeat B1."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests -q",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 16 tests in 400.101s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check 7014dd0e..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    }
  ],
  "flags": []
}
```

## Findings

**B2 — blocker.** The final sentence broadens a correct recovery-tool instruction into an incorrect rule for all harvest operations. §2.5, lines 1835–1839, explicitly says:

> Run it twice — once from the clone, once from a second checkout at the same head, with a DIFFERENT `--out` for the second run

Conversely, §2.4, lines 1641–1643, defines desk recovery as:

> the recovery tool run by the operator, at the desk, after the night is over, against the measurement clone

Thus the clone requirement is correct for this recovery operation. The contradiction is the word **always** applied to harvest generally; §2.5 requires another checkout. Nothing inspected establishes that the second checkout must be `main`. The exact replacement in B2 preserves both instructions.

**S1 — should-fix.** “Main after 2026-09-12” is not reliable for either a same-day merge or a delayed merge. Delete the parenthesis as specified above; checkout contents already provide the relevant condition.

**S2 — should-fix.** First-use audit, with all locations in `docs/phase_2/derivation_night_runbook.md`:

| Term | Definition available before or within the paragraph |
|---|---|
| `session-refusal` | Defined inline at 1665–1666 as the recovery tool’s subcommand that prints a stored abort. The tool’s script is identified at 1647. |
| “refusal code” | **Missing before use.** The later §5 table at 2136–2143 associates named codes with meanings. Apply S2’s inline definition. |
| “frozen clone” | Its underlying object is defined in §0.2 at 276–280: the fresh independent clone detached at H. §1.5 at 1439–1444 binds the frozen triple’s root to that clone and forbids moving it. The exact phrase is new, but its meaning is established earlier. |
| “H” | Introduced as the night’s head at 97–98; explicitly defined in §0.1 at 249–253 as the full commit SHA shared by the plan and detached clone. |
| “chain log line above” | The unused-slot evidence is explained at 1223–1228; §2.1 at 1535 identifies `operator_logs/derivation-chain.log` and its lifecycle records. The immediate antecedent is the literal `slot_unused slot=dNN reason=window_exhausted` at 1661–1662. |

No nit findings.

**B1 closure confirmed.** The requested Git-object inspection:

`git show f90cb8c0:scripts/recover_calibration_ledger.py | grep -n _AUTOMATIC_ABORT_REFUSALS -A6`

returned:

```text
62:_AUTOMATIC_ABORT_REFUSALS = {
63-    "display_arm_failed": RefusalCode.DISPLAY_ARM_FAILED,
64-    "powermetrics_never_ready": RefusalCode.SAMPLER_NEVER_READY,
65-    "pulse_calibration_rollover_gate_timeout": RefusalCode.ROLLOVER_GATE_TIMEOUT,
66-}
67-
68-
--
376:            code = _AUTOMATIC_ABORT_REFUSALS.get(str(output.get("abort_reason")))
377-            if output.get("session_state") != "aborted" or code is None:
378-                raise CalibrationLedgerError(RefusalCode.SESSION_NOT_OPEN)
379-            return emit_refusal(
380-                code,
381-                context={"durable_session_status": output},
382-                terminal_result="session_aborted",
```

At that same commit, `joulewise/calibration_exits.py:66` defines:

```text
SESSION_NOT_OPEN = "calibration_session_not_open"
```

`window_exhausted` is absent from the mapping, so the fallback produces the documented older code. Reading the actual reason from the preceding chain-log record is correct.

**Same-signature statement: YES at the checkout-instruction level (B2); NO recurrence in the corrected refusal-output claim.** The new universal claim fits the primary clone execution but excludes the second checkout the operator must actually use.

The inventory command ran **once**:

```text
Ran 16 tests in 400.101s

OK
```

`python3 scripts/gen_state.py --check` exited **0**, with no output. No files changed. Next step: apply the three exact replacements and re-audit the resulting prose.

## Residual risk

Historical behavior was inspected through this worktree’s Git objects; neither fenced directory was accessed. Tests exercised fixtures, not live hardware. The full suite was not run for this one-paragraph documentation delta; both requested checks passed.