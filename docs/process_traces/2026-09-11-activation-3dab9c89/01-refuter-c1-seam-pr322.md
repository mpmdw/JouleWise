```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "C1 correction and all requested execution checks pass; one first-use glossary defect should be fixed before merge.",
  "workspace": {
    "base_requested": "503a271ebe9d8a0fb5c13e93fc53351afe7ffb0e",
    "base_mode": "exact",
    "head_start": "503a271ebe9d8a0fb5c13e93fc53351afe7ffb0e",
    "head_end": "503a271ebe9d8a0fb5c13e93fc53351afe7ffb0e",
    "upstream_end": "1dddcfea573d85ee8facebc2b50dac412cb3b69f",
    "branch": "fix/2026-09-11-c1-registration-seam"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "MERGEABLE AFTER FIXES",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "docs/phase_2/derivation_night_runbook.md",
        "line": 504,
        "summary": "Receipt class is used before it is explained.",
        "detail": "Section 0.5 says 'this receipt class'; its first explanation appears later at line 754. This fails the brief's explicit first-use standard.",
        "recommendation": "At line 504, name DIAGNOSTIC_NO_PACK and explain receipt class as the plan category selecting the applicable gate checks."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gen_derivation_night tests.test_night_gate -v > /tmp/c1-refuter-focused-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 97 tests in 25.801s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 97 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_derivation_night.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS generated derivation-night wrapper region matches"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS generated derivation-night wrapper region matches$"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 /tmp/c1-refuter-replay.py arm",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "d166: rc=0",
          "staged plan checks PASS",
          "pre-registration: rc=1",
          "AssertionError",
          "PASS extracted arm block accepts D-166 and rejects pre-registration"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS extracted arm block accepts D-166 and rejects pre-registration"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 /tmp/c1-refuter-replay.py baseline > /tmp/c1-refuter-baseline.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 4 tests in 0.005s",
          "FAILED (failures=7)",
          "BASELINE tests=4, failures=7, errors=0",
          "PASS T1-T3 fail on baseline; T4 passes"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "BASELINE tests=4, failures=7, errors=0[\\s\\S]*PASS T1-T3 fail on baseline; T4 passes"
      }
    },
    {
      "id": "V5",
      "kind": "build",
      "cmd": "PYTHONPYCACHEPREFIX=/tmp/c1-refuter-pycache python3 -m compileall -q scripts joulewise",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check origin/main..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Findings

**F1 — SHOULD_FIX — [docs/phase_2/derivation_night_runbook.md:504](/Users/edr/code/JouleWise-wt-c1-seam/docs/phase_2/derivation_night_runbook.md:504): explain “receipt class” at first use.**

The new §0.5 sentence says “the file required for this receipt class,” but neither names that class nor explains the term. Its explanation appears 250 lines later.

Command:

```sh
grep -n 'receipt class' docs/phase_2/derivation_night_runbook.md
```

First two matches:

```text
504:the file required for this receipt class by C1, the night gate's registration
754:`DIAGNOSTIC_NO_PACK` is the receipt class for a night that runs no measurement
```

Add an inline explanation at 504: `DIAGNOSTIC_NO_PACK` means a night without a measurement pack; its receipt class selects the applicable gate checks. This is a writing-standard defect, with no observed execution failure.

**Contract audit**

Below, **R** means `docs/phase_2/derivation_night_runbook.md`. PASS assesses the binding requirement; F1 separately assesses its explanation.

| Ruling 12 §5 requirement | Result | Implementation |
|---|---|---|
| §0.5: plan names D-166; scientific pre-registration bound separately | PASS | R:500–507; digest procedure R:528–546 |
| §1.1: correct `registration_path` table cell | PASS | R:778 |
| §1.4: correct registration in arm description | PASS | R:1256–1259 |
| Arm block: exact path equality | PASS | R:1305 |
| Arm block: hash file inside `$MEASUREMENT_ROOT` against gate constant | PASS | R:1306–1308 |
| §5: explain D-166 refusal and exclude scientific pre-registration from C1 | PASS | R:2113–2117 |
| §2.5: re-hash committed file at H before applying rule | PASS | R:1750–1753 |
| §2.5: quote arm-record digest in PASS continuation addendum | PASS | R:1754–1755 |
| Revision 7 changelog | PASS | R:11–21 |
| Generator example imports and uses D-166 constant | PASS | `scripts/gen_derivation_night.py:47,687` |
| Regenerated runsheet region | PASS | `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:1667`; `--check` passes |
| T1: literal and actual digest; remove override | PASS | `tests/test_gen_derivation_night.py:1044–1056` |
| T2: arm-block path check; exclude pre-registration filename | PASS | `tests/test_night_gate.py:212–224` |
| T3: every registration-path reference names D-166, except index | PASS | `tests/test_night_gate.py:226–244` |
| T4: real pre-registration refuses; real D-166 passes; documentary label | PASS | `tests/test_night_gate.py:246–271` |

The arm-record requirements are all present:

| Required evidence | Result | Runbook implementation and reproduction source |
|---|---|---|
| Night `plan_id`; frozen-plan digest matching `PLAN_SHA256`; verbatim registration path and actual digest | PASS | R:1416. Night ID: R:767; frozen **calibration** plan and its digest: R:374,832–836; registration path: R:502 |
| Pre-registration path, committed-byte SHA-256 after filling fields, 40-hex H, blob ID | PASS | R:1417; hash command R:533; H definition R:243; blob command R:1425 |
| D-102 rule commit and runbook-revision commit, with revision number | PASS | R:1418; rule source identified R:1646–1649; revision R:11. The table requests containing commits, so H supplies both when its tree contains that rule and revision |
| Wrapper digest, identity-epoch digest, T1-bindings digest, evidence-root ID | PASS | R:1419; producer output R:715–724,941; evidence-root selection R:370,952–954 |
| Nights 2/3: re-record digest as “equal to night 1,” otherwise STOP | PASS | R:1420,1814–1819 |

`PLAN_SHA256` in row 1 is the frozen **calibration-plan** digest, as R:832–834 already explains. It is not the SHA-256 of `night_plan.json`; the generator confirms this at `scripts/gen_derivation_night.py:286–287`.

| FAIL-route requirement | Result | Implementation |
|---|---|---|
| Re-hash before arm; mismatch means do not arm | PASS | R:1814–1818 |
| File discrepancy for Ed; never silently substitute a pin | PASS | R:1818–1819 |
| If mistakenly armed, issuer uses night-one digest and refuses changed bytes | PASS | R:1884–1903; unchanged issuer comparison at `scripts/issue_calibration_acceptance_generation.py:1178–1181` |
| C1 remains independent of the scientific pre-registration | PASS | R:2113–2117; T4 |
| No runtime mechanisms from rejected options (ii)/(iii) | PASS | Protected runtime paths unchanged |

**Scope and remaining references**

`git diff --name-status origin/main..HEAD` reports exactly:

```text
M docs/phase_2/derivation_night_runbook.md
M docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md
M scripts/gen_derivation_night.py
M tests/test_gen_derivation_night.py
M tests/test_night_gate.py
```

Both baseline-to-HEAD and working-tree comparisons confirm these are untouched:

```text
joulewise/night_gate.py
scripts/night_chains/
scripts/run_night.py
scripts/issue_calibration_acceptance_generation.py
configs/calibration/preregistration_d079_epoch_25g83_rev1.md
docs/process/state_kernel.json
docs/decision_log.md
```

The final porcelain status is empty. This review modified no repository paths.

The requested `grep -n registration_path` census found:

| Path | Lines | Assessment |
|---|---|---|
| R | 500, 778, 1256, 1305, 1416, 2113 | All name D-166 or `D166_REGISTRATION_PATH` |
| R | 2204 | Permitted symbol-index row |
| `docs/process/NIGHT_HANDBACK.md` | No matches | No stale binding |
| `docs/process/MAGISTRATE_WATCHDOG.md` | 365, 455 | Explicit fake rehearsal examples using `registration.json`; neither names the scientific pre-registration |
| `docs/contracts/pack_night_go_receipt.md` | 155 | Schema-key inventory |
| Other `docs/contracts/*.md` | No matches | No stale binding |

A broader search for pre-registration language also found **no sentence in the requested corpus still binding the night plan to the calibration pre-registration**. No such out-of-scope follow-up is needed.

**Execution evidence**

The focused suite comprised **40 generator tests + 57 night-gate tests**:

```text
Ran 97 tests in 25.801s

OK
```

Generator check:

```text
PASS generated derivation-night wrapper region matches
```

The [replay harness](/tmp/c1-refuter-replay.py) extracts only the Python heredoc containing the specified assertion into [arm-block.py](/tmp/c1-refuter-replay/arm-block.py). It authors temporary JSON plans, sets `H` to HEAD and `MEASUREMENT_ROOT` to this worktree, supplies the remaining environment variables, and executes the extracted source unchanged through Python stdin.

```text
d166: rc=0
staged plan checks PASS
pre-registration: rc=1
Traceback (most recent call last):
  File "<stdin>", line 13, in <module>
AssertionError
PASS extracted arm block accepts D-166 and rejects pre-registration
```

That failing line is the exact registration-path assertion, R:1305.

For baseline proof, the harness uses `git show origin/main:<path>` to place the original generator and runbook in `/tmp`. It points the current tests’ `GEN` and `RUNBOOK` references at those copies. Gate, ledger module, tracked chain, and both registration files were verified byte-identical to `origin/main`. No stash, checkout mutation, or assertion replacement was used.

```text
T1: FAIL
T2: FAIL
T3: FAIL at baseline lines 488, 760, 1238, 1283, 2054
T4: PASS

Ran 4 tests in 0.005s

FAILED (failures=7)
BASELINE tests=4, failures=7, errors=0
```

The harness exits 0 only after confirming that expected failure pattern. Separately, rendering the example wrapper through both generator versions produced:

```text
PASS rendered wrapper bytes identical between origin/main and HEAD
```

**Pedagogy audit**

| New sentence group | First-use assessment |
|---|---|
| Revision 7, R:11–21 | PASS: D-166 explained at 11–12; measurement head at 13; SHA-256 digest at 14; blob ID at 17; continuation at 18–19 |
| §0.5, R:500–507 | PARTIAL: D-166/path and measurement commit explained locally; “receipt class” fails first use — F1 |
| §1.1, R:778 | PASS: D-166 built at 500–504; receipt class built at 754–757 |
| §1.4, R:1256–1259 | PASS: earlier definitions apply; SHA-256 also glossed locally |
| §1.5, R:1408–1425 | PASS: arm record, FAIL route, digest, blob ID and measurement head explained locally; capture-input sources given |
| §2.5, R:1750–1755 | PASS: H and digest glossed locally; continuation explained earlier at 1739 |
| §3, R:1814–1819 | PASS: FAIL route explained at 1803–1806; H, digest and replacement pin explained locally |
| §5, R:2113–2117 | PASS: D-166 built earlier; C1 and both named classes explained locally |

Apart from F1’s unexplained classification, I found no new operational sentence that lacks an actionable source or procedure.

## Residual risk

Verification is desk-only: synthetic plans and fixture machine probes establish assertion behavior, not live C1 success. No agents were installed and no quiet-machine work was performed. The full repository suite was not run; the requested focused suites, compilation, generator consistency check, and baseline counterfactuals passed.

Next step: fix F1 in the runbook, then let the lead review the final diff.

VERDICT: MERGEABLE AFTER FIXES