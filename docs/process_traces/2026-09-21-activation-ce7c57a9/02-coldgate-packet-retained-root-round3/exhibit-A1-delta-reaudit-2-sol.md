# Exhibit A1 — Sol delta re-audit 2 (xhigh) on bd671744 (round-1 head merged with main), verbatim

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "100 tests pass; three should-fix findings remain: manual-loop symlink parity, uncaught JSON recursion on Python 3.11, and an unpinned realpath comparison.",
  "workspace": {
    "base_requested": "fc28d7822c5b5eac8f42a3b56634fe86b08465a8",
    "base_mode": "descendant",
    "head_start": "bd67174440f877f6dd660402a0acf3ae9ed2b9f7",
    "head_end": "bd67174440f877f6dd660402a0acf3ae9ed2b9f7",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "location": "docs/phase_2/derivation_night_runbook.md:736",
        "title": "Manual classifier still prints retained for unsafe symlink paths",
        "cure": "Use the Python inventory for manual inspection, or implement complete safe_path-equivalent guards and parity tests."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "location": "joulewise/evidence_night.py:740",
        "title": "Deep JSON escapes classification on supported Python 3.11",
        "cure": "Catch RecursionError at the plan parsing boundary and test UNKNOWN plus a persisted failing check record."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "location": "tests/test_evidence_night.py:914",
        "title": "Removing realpath survives the new span-fence test",
        "cure": "Add equivalent custody_root spellings, including a symlink component and trailing slash, and require their normal span classification."
      }
    ],
    "q1": {
      "Astra_F1": "CLOSED",
      "Astra_F2": "CLOSED",
      "Astra_F3": "CLOSED",
      "Astra_F4": "CLOSED",
      "Astra_F5": "CLOSED",
      "Astra_F6": "CLOSED",
      "Sol_F1": "OPEN",
      "Sol_residual_A263": "CLOSED"
    },
    "q4": {
      "m7": "KILLED",
      "m8": "SURVIVED",
      "m9": "KILLED",
      "m10": "KILLED"
    },
    "q7": "night_agents still gates may_fast_forward; canonical executes before retained_roots",
    "q8": "Fix-first recommendation; no blocker-level defect established"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_evidence_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 100 tests in 275.168s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 100 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/retention-delta-bd671744/mutations.py > /tmp/retention-delta-bd671744/mutations.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/retention-delta-bd671744/authority.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "F5 handbook ruled paragraph: MATCH (whitespace normalized)",
          "F5 runbook ruled paragraph: MATCH (whitespace normalized); source annotation separate",
          "F1 obsolete heading/prohibition: REMOVED",
          "F6 coexisting marker comment: CORRECTED"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "F6 coexisting marker comment: CORRECTED"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3.11 -B /tmp/retention-delta-bd671744/integration.py > /tmp/retention-delta-bd671744/integration.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "deep-check: RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string",
          "deep-check-record-exists: False",
          "loaded: {\"canonical\": \"fail\", \"head_moved\": false, \"night_agents\": \"fail\", \"order\": [\"night_agents\", \"canonical_check\", \"supervisor_check\", \"retained_roots\"], \"pull\": false, \"retained_roots\": \"pass\"}",
          "unknown: {\"canonical\": \"fail\", \"head_moved\": false, \"night_agents\": \"fail\", \"order\": [\"night_agents\", \"canonical_check\", \"supervisor_check\", \"retained_roots\"], \"pull\": false, \"retained_roots\": \"pass\"}",
          "plist: {\"canonical\": \"fail\", \"head_moved\": false, \"night_agents\": \"fail\", \"order\": [\"night_agents\", \"canonical_check\", \"supervisor_check\", \"retained_roots\"], \"pull\": false, \"retained_roots\": \"pass\"}",
          "clear-with-active-root: {\"canonical\": \"pass\", \"head_moved\": true, \"night_agents\": \"pass\", \"order\": [\"night_agents\", \"canonical_check\", \"supervisor_check\", \"retained_roots\"], \"pull\": true, \"retained_roots\": \"fail\"}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "deep-check: Refused:.*[\\s\\S]*deep-check-record-exists: True"
      }
    }
  ],
  "flags": []
}
```

## Findings

**Blocker: none established.**

**F1 — Should-fix: the manual loop still accepts unsafe symlink paths.**  
At `docs/phase_2/derivation_night_runbook.md:736–738`, the plan guard checks only the final component, and `(N.)` does not reject symlinked ancestors. The open-chain check also follows symlinks.

Executed:

```sh
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/retention-delta-bd671744/probes.py
/bin/zsh /tmp/retention-delta-bd671744/runbook.zsh
```

The script extracts the actual runbook loop and changes only its discovery prefix. Output:

```text
directory-marker: UNKNOWN
directory-plan: REFUSED plan is not a regular file
symlink-exit: retained refusal.json
symlink-marker: UNKNOWN
symlink-night: retained refusal.json
symlink-plan-parent: retained refusal.json
```

Python raises `Refused: symlink/path collision` for the last three false-retained cases. The symlink-exit fixture has regular `chain.started` and `refusal.json`, plus symlinked `chain.exited`.

**Cure:** use `retained_roots` for the manual inventory, or add complete path guards and executable parity coverage.

**F2 — Should-fix: malformed JSON can escape the new exception boundary.**  
`joulewise/evidence_night.py:733–741` omits `RecursionError`; `check.inspect` at :897 also omits it. On supported Python 3.11, a plan containing 2,000 nested arrays aborts the check before it writes its evidence record.

Executed:

```sh
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3.11 -B /tmp/retention-delta-bd671744/integration.py
```

Output:

```text
deep-check: RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string
deep-check-record-exists: False
```

This remains fail-closed for arming, but violates the promised `UNKNOWN` classification and loses the failing check record. The same 1,500-level probe on Python 3.13 and default Python 3.14 returned `UNKNOWN`; this finding is specifically reproduced on the supported 3.11 floor.

**Cure:** catch `RecursionError` around plan parsing and pin both classification and check-record persistence.

**F3 — Should-fix: the realpath comparison has no discriminating regression.**  
`tests/test_evidence_night.py:914–940` uses identical canonical strings for matching roots. Replacing the comparison with:

```python
parsed.custody_root != str(plan.parent)
```

survives the new test.

Executed:

```sh
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/retention-delta-bd671744/mutations.py
```

Output:

```text
baseline: PASS
m7: KILLED
m8: SURVIVED
m9: KILLED
m10: KILLED
```

**Cure:** test equivalent paths with a trailing slash and symlink component; include `/tmp` versus `/private/tmp` where applicable.

**Nit: none separately raised.**

**Q1 — Closure**

| Prior finding | Disposition | Closing delta location and verification |
|---|---|---|
| Astra F1: obsolete prohibition | **CLOSED** | Runbook :699–703 permits discoverable retained roots. `authority.py` verifies obsolete heading/prohibition removed. |
| Astra F2: missing span fence | **CLOSED** | `evidence_night.py:733–739`; executed exited-chain fixture at `t0 + 600` returns `ACTIVE/fail`, after the span `retained/pass`. New test :914 passes; m7 and m10 die. |
| Astra F3: marker directories accepted | **CLOSED** | Runbook :738 uses `(N.)`; actual zsh directory-marker fixture prints `UNKNOWN`. |
| Astra F4: refusal-only verdict/full evidence paths unpinned | **CLOSED** | Tests :895–896 and :905–912 assert complete paths and isolated refusal-only success. Both original defect mutations now die. |
| Astra F5: ruled prose altered | **CLOSED** | Handbook :298–311 separates explanation from ruled text; runbook :747 separates attribution. `authority.py` confirms both ruled paragraphs match after whitespace normalization. |
| Astra F6: exactly-one-family comment | **CLOSED** | `evidence_night.py:699–705` explicitly allows coexisting families. |
| Sol F1: manual path/file-type parity | **OPEN** | The three named fixtures are fixed by runbook :736/:738, but unsafe symlink combinations still print `retained`; see F1 above. |
| Sol residual A263 | **CLOSED** | Shared watchdog span rule now executes at `evidence_night.py:737`; the prior active-span counterexample refuses. |

Additional closure probe:

```sh
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/retention-delta-bd671744/closure_mutations.py
```

```text
closure-baseline: PASS
refusal-verdict: KILLED
wrong-full-path: KILLED
```

The refusal-verdict mutant raises `Refused` at the newly isolated success call, test :908. Wrong-full-path produces seven assertion failures, including :895 and :910.

**Q2 — Span-fence counterexamples**

Executed [probes.py](/tmp/retention-delta-bd671744/probes.py); complete output is in [probes.log](/tmp/retention-delta-bd671744/probes.log).

| Input | Observed |
|---|---|
| Exited chain inside span | `ACTIVE/fail` |
| Exited chain long after span | `retained/pass` |
| Matching custody via `/tmp` alias | `ACTIVE/fail`, correct identity |
| Matching custody with trailing slash | `ACTIVE/fail`, correct identity |
| Matching custody through symlink component | `ACTIVE/fail`, correct identity |
| Different physical custody directory | `UNKNOWN/fail` |
| `{}` plan | `UNKNOWN`, `PlanError` reason |
| Invalid JSON | `UNKNOWN`, `JSONDecodeError` reason |
| Huge numeric t0/window | `UNKNOWN`, `OverflowError` reason |
| Invalid numeric type | `UNKNOWN`, `PlanError` reason |
| Injected `TypeError`, `OverflowError`, `OSError` | Each becomes `UNKNOWN` |
| Injected `deadman_epoch` `ValueError` | `UNKNOWN`, recorded reason |
| `now_epoch_s=None` | Uses `time.time()` once; patched inside-span clock yields `ACTIVE` |
| Valid `TRANSACTION_PACK` v3 | Inside span `ACTIVE`; ended span `retained` |
| Valid quiet v4 | Inside span `ACTIVE`; ended span `retained` |
| Missing `night/` | `UNKNOWN/fail`, “no terminal night record” |
| Deep JSON on Python 3.11 | Uncaught `RecursionError`; F2 |

`Storage` construction and this span call perform no writes. One inherited semantic detail remains: `Storage.exists` counts directories. With regular `chain.exited` and a **directory** named `courier.sent`, the reused watchdog rule returns inactive immediately after completion, producing `retained`. This matches the explicitly selected watchdog rule; it is not a merge-induced divergence.

**Q4 — Mutation results**

Each run loaded the package and test from the scratch copy, verified by `SCRATCH_IMPORT_OK`; the unchanged baseline passed. Initial scratch setup lacked a registration fixture; those setup-error runs were discarded before the valid replay.

| Mutation | Result | Failing assertion |
|---|---|---|
| m7 Drop `plan_span_active` | **KILLED** | Test :921: `('retained', None) != ('ACTIVE', 'plan span active (…)')` |
| m8 Compare without `realpath` | **SURVIVED** | None; one test passed |
| m9 Swallow `PlanError` as retained | **KILLED** | Test :940: `'retained' != 'UNKNOWN'` |
| m10 Pass `now + 1e9` | **KILLED** | Test :921: `('retained', None) != ('ACTIVE', 'plan span active (…)')` |

**Q3 — Real-root output, verbatim**

Executed the exact requested read-only command:

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'from joulewise import evidence_night as e; import json; print(json.dumps(e.retained_roots({"roots_under": "/Users/edr"}), indent=1))'
```

```json
{
 "inventory": [
  {
   "plan": "/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night_plan.json",
   "classification": "retained",
   "reason": null,
   "evidence": [
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night/courier.sent",
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night/result.json",
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night/chain.exited"
   ]
  },
  {
   "plan": "/Users/edr/night-custody/d079-epoch-25g83-derivation-n2-20260919/night_plan.json",
   "classification": "retained",
   "reason": null,
   "evidence": [
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n2-20260919/night/courier.sent",
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n2-20260919/night/result.json",
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n2-20260919/night/chain.exited"
   ]
  },
  {
   "plan": "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night_plan.json",
   "classification": "retained",
   "reason": null,
   "evidence": [
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/courier.sent",
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/result.json",
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/chain.exited",
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/refusal.json",
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/refusal-01.json"
   ]
  }
 ],
 "now_epoch_s": 1790057109.679536,
 "verdict": "pass"
}
```

**Q5 — Whole-module tail, verbatim**

```text
----------------------------------------------------------------------
Ran 100 tests in 275.168s

OK
```

Exit 0. Run once with the requested command; default `python3` was 3.14.7.

**Q6 — Same-signature statement**

- **Defective ruled executable text:** recurs in the incompletely repaired manual loop, F1.
- **Evidence asserted only by basename:** no recurrence found; complete evidence paths are now pinned.
- **Documentation contradicting its adjacent rule:** recurs through F1—the loop still emits `retained` for paths the contract’s `safe_path` rule refuses. The active-span difference is now explicitly documented, so that specific contradiction is closed.

**Q7 — PR #378 interaction and ordering**

The merge preserves the guard at `evidence_night.py:909–911`: `may_fast_forward` receives the boolean verdict from `night_agents`.

Executed fixture checks established:

| Agent observation | Pull attempted | Canonical moved |
|---|---:|---:|
| Loaded agent | No | No |
| Unknown discovery | No | No |
| Plist present | No | No |
| Clear agents, active sibling span | Yes | Yes; subsequent `retained_roots` fails |

Recorded execution order was:

```text
night_agents → canonical_check → supervisor_check → retained_roots
```

Thus retention failure does **not** gate the earlier fast-forward. That matches D-183’s item-0 authorization and its definition of armed as installed agents. No lost night-agent gate or additional merge regression was found.

**Q8 — Final-head recommendation**

**Fix first:** F1 and F2 remain executable defects; add F3’s regression alongside the fix round. No blocker-level defect established. Final HEAD remains `bd67174440f877f6dd660402a0acf3ae9ed2b9f7`, with a clean worktree and no repository writes.

## Residual risk

The requested module, targeted fixtures, mutation copies, and read-only real inventory were exercised. The repository-wide suite, live installation, supervisor handoff, and quiet-machine hardware gates were not run. The lead retains final verification and merge authority.