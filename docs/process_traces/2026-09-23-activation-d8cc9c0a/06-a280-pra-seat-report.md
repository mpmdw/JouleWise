```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the two-row night-kind table with byte-identical idle artifacts; two importer tests fail on denied host process probes.",
  "workspace": {
    "base_requested": "cdc05e9b",
    "base_mode": "exact",
    "head_start": "cdc05e9ba580783311595d353be2513b8dfdb9f7",
    "head_end": "cdc05e9ba580783311595d353be2513b8dfdb9f7",
    "upstream_end": "cdc05e9ba580783311595d353be2513b8dfdb9f7",
    "branch": "feat/2026-09-23-a280-kind-table"
  },
  "pathspec": [
    "joulewise/night_kinds.py",
    "joulewise/evidence_night.py",
    "joulewise/night_gate.py",
    "joulewise/quiet_predicate_campaign.py",
    "scripts/gen_evidence_night.py",
    "tests/test_night_kinds.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_night_kinds tests.test_evidence_night tests.test_night_gate tests.test_quiet_predicate_campaign",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 400 tests in 277.380s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 400 tests.*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_arm_retry tests.test_night_plan_writer tests.test_launch_window tests.test_magistrate_watchdog_cli tests.test_run_night tests.test_evidence_arm_sequence tests.test_arm_census tests.test_quiet_admission tests.test_sample_quiet_predicate_evidence tests.test_night_agent_install tests.test_gen_evidence_night tests.test_install_night_agent tests.test_gen_derivation_night tests.test_agent_census_concurrency tests.test_arm_readiness",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 701 tests in 1422.253s", "FAILED (failures=2, skipped=12)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_night_kinds tests.test_gen_evidence_night tests.test_quiet_predicate_campaign",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 170 tests in 24.673s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_gen_evidence_night tests.test_install_night_agent tests.test_gen_derivation_night tests.test_agent_census_concurrency tests.test_arm_readiness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 193 tests in 112.207s", "OK (skipped=3)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=3\\)"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "Two importer tests depend on host process probes unavailable in this sandbox: pgrep reports sysmond unavailable and /bin/ps returns Operation not permitted.",
      "needs": "Magistrate reruns the two named failures in an environment with process-list access."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "The new night_kinds.py is not among the idle manifest's per-file digests. Adding it would change the byte-identical idle manifest required by K3.",
      "needs": "Magistrate rules on manifest binding before merge or carries an explicit manifest update into PR B."
    }
  ]
}
```

## Change

**K1–K2.** [night_kinds.py](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/night_kinds.py:25) defines frozen rows in an immutable mapping; `kind_row` raises `UnknownNightKind`, a typed `ValueError` ([line 93](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/night_kinds.py:93)). The two rows render as:

| Kind | Row values |
|---|---|
| `quiet_predicate_evidence` | Prefix `qpe01-pilot-n1-`; root suffix `qpe01-pilot-n1`; chain `scripts/night_chains/quiet_predicate_evidence.zsh`; protocol `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json`; receipt `DIAGNOSTIC_NO_PACK`; window `9000`; manifest and executor `joulewise.quiet_predicate_campaign`; generator `scripts/gen_evidence_night.py`; chain authentication, chain-bound registration, corecaptured, and 30 s non-observer predicates **true**. Notice fields retain the idle-variance introduction, “idle envelopes,” the “No model…” sentence, and the block-two follow-up. |
| `calibration` | Chain `scripts/night_chains/calibration_derivation_only.zsh`; no plan prefix, root suffix, protocol, manifest, generator, executor, window, or notice text in this table; all four gate predicates **false**. |

The §1.3 site dispositions are:

| Site | Disposition |
|---|---|
| Evidence `KIND` and idle-only preparation refusal | Table-derived `KIND`; existing `Refused("invalid or unresolved kind")` retained ([evidence_night.py:28, 369](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/evidence_night.py:369)). |
| Plan-id prefix, measurement-root suffix, prior-candidate and notice searches | Table-driven ([evidence_night.py:158, 217, 433, 1653](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/evidence_night.py:158)). |
| Plan authoring and generator selection | Receipt, protocol, window, and generator path read from the row ([evidence_night.py:506, 540](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/evidence_night.py:506)). The H-side snippets use H’s row when present and preserve base-H compatibility. |
| Sealed candidate and census classification | Manifest module, chain source, and receipt class read from the row ([evidence_night.py:239, 1021](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/evidence_night.py:239)). |
| Notice and arm predicates | Kind-specific wording and corecaptured/non-observer scope read from the row ([evidence_night.py:294, 298, 1360](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/evidence_night.py:294)). |
| Gate chain path, payload recognition, source authentication, t0 predicates, registration defect | Table-driven; existing public constants and refusal text remain ([night_gate.py:116, 129, 197, 1403, 1555, 1597, 1730](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/night_gate.py:116)). |
| `manifest_for` protocol, receipt, and window requirements | Table-driven with unchanged refusal messages ([quiet_predicate_campaign.py:146](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/quiet_predicate_campaign.py:146)). |
| Generator kind, manifest function, and executor | Table-driven with unchanged wrapper bytes ([gen_evidence_night.py:20](/Users/edr/code/wt-d8cc9c0a-a280a/scripts/gen_evidence_night.py:20)). |
| Installer, night driver, watchdog, retry, and courier sites listed in §1.3 | **Deferred to PR B** by the scope cut. `quiet_predicate_campaign.verify_manifest` is outside PR A’s `manifest_for` cut. |

**K3.** [test_night_kinds.py](/Users/edr/code/wt-d8cc9c0a-a280a/tests/test_night_kinds.py:186) compares decoded golden **bytes** for the writer’s plan, rendered chain and both sidecars, sealed-candidate manifest and its digest, draft notice, and checked notice. It also calls the real `sealed_candidate` check. The manifest byte digest is `3f6b0039c0799be4f79e5c4ab2c21e1aa10aa9db8e3c77ded00dd85b5330f9bb`. [Refusal parity](/Users/edr/code/wt-d8cc9c0a-a280a/tests/test_night_kinds.py:193) passes on both base and current code: unknown and calibration kinds each give `Refused: invalid or unresolved kind`; a wrong plan-id prefix gives `Refused: candidate is not a completed, owned preparation`.

The goldens were produced by copying `git archive cdc05e9b` to `/tmp/jwkindbase`, initializing and committing that disposable copy with fixed Fixture identity and date, copying the **same test module** into it, then running:

```sh
JW_KIND_BASE_SOURCE=/tmp/jwkindbase PYTHONPATH=/tmp/jwkindbase python3 -B /tmp/jwkindbase/tests/test_night_kinds.py --dump-goldens
```

A final run of that command matched the stored goldens with `cmp`; the base-archive refusal test also passed. No repository commit was made.

**K4–K5.** Public function signatures are unchanged. `git status` names exactly the six allowed paths. `git diff cdc05e9b --stat` names only the four tracked allowed paths; the two new allowed files remain untracked because the shared Git index is read-only. The exact four-module command passed 400 tests. The grep-derived importer list is the 15 modules in V2; all were run by name.

## Verification notes

V2’s two failures are:

- `tests.test_sample_quiet_predicate_evidence.CollectionTests.test_real_collect_no_power_reaps_all_recorded_workers`: the collector records `sysmond service not found` and `PermissionError: Operation not permitted: '/bin/ps'`, leaving every round in error. Its base-archive run passed, with a timing-dependent partial round.
- `tests.test_night_agent_install.LaunchdAccessProbeTests.test_cleanup_refusal_reports_the_failure_it_interrupted`: `pgrep` fails before the expected bootout diagnostic. The exact failure reproduces at `cdc05e9b`.

Focused post-edit checks passed: 92 gate/lifecycle tests, 170 kind/generator/campaign tests, the census transport test, and the generator-path composition tests. The final golden test passed after adding the checked notice.

## Residual risk

**Suspected defect:** `joulewise/night_kinds.py` is absent from the idle manifest’s per-file list. K3’s required manifest byte identity prevented adding that digest in this PR. The magistrate should resolve that binding gap before relying on a merged night that imports the table.

The magistrate should also review [night_gate.py:29](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/night_gate.py:29): its frozen compatibility rows support an existing isolated test fixture that copies `night_gate.py` without the new sibling module. A checkout whose HEAD tracks `night_kinds.py` fails closed if that sibling is missing.