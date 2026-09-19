```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented two harness evidence-retention fixes; NEEDS_RULING on chain-source authentication and D-166 receipt compatibility before executor implementation.",
  "workspace": {
    "base_requested": "0c529f99",
    "base_mode": "exact",
    "head_start": "0c529f99ea95ccee37207057934a2f79a6941c98",
    "head_end": "0c529f99ea95ccee37207057934a2f79a6941c98",
    "upstream_end": "0c529f99ea95ccee37207057934a2f79a6941c98",
    "branch": "feat/2026-09-19-stage-a-evidence-executor"
  },
  "pathspec": [
    "scripts/sample_quiet_predicate_evidence.py",
    "tests/test_sample_quiet_predicate_evidence.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_sample_quiet_predicate_evidence.FrameTests tests.test_sample_quiet_predicate_evidence.IntegrationTests tests.test_sample_quiet_predicate_evidence.SummaryTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 21 tests in 0.042s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 21 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stage_a_offline_tests.py > /tmp/stage-a-evidence-harness.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 47 tests in 2.867s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 47 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stage_a_counterfactual.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["COUNTERFACTUAL PASS: all four new regressions reject the HEAD harness"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "COUNTERFACTUAL PASS: all four new regressions reject the HEAD harness"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/quick_suite.py --tier quick --workers 4 > /tmp/stage-a-evidence-quick.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["QUICK SUMMARY tier=quick modules=153 excluded=86 failures=1 seconds=103.439 result=FAIL"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "QUICK SUMMARY tier=quick modules=153 excluded=86 failures=0 .*result=PASS"
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
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --stat -- scripts/sample_quiet_predicate_evidence.py tests/test_sample_quiet_predicate_evidence.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " scripts/sample_quiet_predicate_evidence.py    | 61 ++++++++++++++++++-",
          " tests/test_sample_quiet_predicate_evidence.py | 88 +++++++++++++++++++++++++++",
          " 2 files changed, 147 insertions(+), 2 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "2 files changed, 147 insertions\\(\\+\\), 2 deletions\\(-\\)"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "launchctl list",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: adjudication 10a assumes _check_chain_identity already measures chain_source_sha256, but it measures only wrapper bytes. The existing generator explicitly makes the chain-source sidecar advisory.",
      "needs": "Approve the evidence-only source-authentication construction described below."
    },
    {
      "id": "R2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: requiring new C1 registration fields for D-166 conflicts with acceptance requiring a byte-identical calibration receipt unless that promise applies only to calibration probe receipts.",
      "needs": "Specify whether byte identity covers calibration probe receipts only or also D-166 admission receipts."
    },
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Quick suite failed only tests.test_axi_controller_events: two tests reported campaign start identity unavailable. Direct /bin/ps execution is denied by this sandbox; the fixture census also failed observation.",
      "needs": "Replay the quick suite and fixture census in the lead environment."
    },
    {
      "id": "E2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The two existing live collect/load harness tests were excluded. launchctl list returned exit 1 with no output, so installed-job state could not be independently certified. No installation command ran.",
      "needs": "Lead owns live tests and installed-job verification."
    }
  ]
}
```

## Change

Completed the independent evidence-retention portion of item 7:

- Rows carry the validated session `os_build`; missing or malformed builds remain explicitly unavailable. Summarization rejects substituted builds and mismatched session identities.
- Rows retain hard-probe worker responses, including AC output, thermal output, `CPU_Speed_Limit`, exit codes and stderr. Interrupted, missing and failed workers retain their evidence or error.

Four new regressions pass against the changed harness and fail against the untouched HEAD harness. No commits, live collection, power sampling, installation, canonical-root writes, or out-of-scope repository edits occurred.

**NEEDS_RULING R1 — source authentication**

**Question:** May `_check_chain_identity` gain evidence-only source authentication? At [night_gate.py:1074](/Users/edr/code/JouleWise-wt-stagea-d0b83820/joulewise/night_gate.py:1074), it currently measures only the per-plan wrapper. The generator expressly describes its source sidecar as advisory at [gen_derivation_night.py:431](/Users/edr/code/JouleWise-wt-stagea-d0b83820/scripts/gen_derivation_night.py:431).

**Options considered:**

1. Measure the tracked evidence template, authenticate it against the source digest embedded in the pinned wrapper and the tracked bytes at `measurement_head`, then populate C5’s `chain_source_sha256`.
2. Trust the advisory source sidecar, changing its existing authority.
3. Bind registration directly without the ruled C5 measurement.

**Recommendation:** Option 1, confined to evidence payloads. It supplies the missing authenticated measurement while preserving calibration behavior.

**Blocked work:** Registration-to-source binding and dependent gate/probe round trips.

**NEEDS_RULING R2 — receipt compatibility**

**Question:** Does “byte-identical receipt for a calibration plan” mean the calibration **probe receipt**, or also the D-166 **admission receipt**?

**Options considered:**

1. Preserve calibration probe bytes; add the ruled registration metadata to both admission paths.
2. Preserve both receipt types; add C1 metadata only for evidence registrations.

**Recommendation:** Option 1 best matches adjudication 10a’s general C1 requirement. Keep the existing D-166 detail literal for its own entry.

**Blocked work:** C1 implementation and its compatibility regression.

**Exact remaining work:** Items 1–6 and 8; item 7’s load-log identity/support join and complete interior reduction; item 9’s executor, dispatch, refusal, protocol-digest and render/probe tests. Resume gate and receipt implementation after R1/R2 are answered.

## CLAUSE MAP

“NOT PINNED” identifies unimplemented obligations, not satisfied clauses.

| Ruled proposition | Production site | Biting test | Counterfactual |
|---|---|---|---|
| F2: retain validated session OS build in rows | `scripts/sample_quiet_predicate_evidence.py:109`, `:690` | `CollectionTests.test_collected_os_build_is_validated_persisted_and_used_by_summary` | Untouched HEAD omits the field; regression rejects it. |
| F2: validate row/session OS identity | `scripts/sample_quiet_predicate_evidence.py:1022` | `SummaryTests.test_row_os_build_cannot_be_substituted_or_joined_to_another_session` | Untouched HEAD accepts substituted identity; regression rejects it. |
| F2: retain AC/thermal results, including interrupted rounds | `scripts/sample_quiet_predicate_evidence.py:429`, `:607` | `CollectionTests.test_hard_probe_results_survive_complete_and_interrupted_rounds` | Untouched HEAD discards responses; regression rejects it. |
| F2: retain missing/failed hard-probe evidence | `scripts/sample_quiet_predicate_evidence.py:438` | `CollectionTests.test_missing_and_failed_hard_workers_are_retained_as_errors` | Untouched HEAD loses worker errors; regression rejects it. |
| Q1: digest-keyed table, unknown-digest refusal, pilot digest | **NOT PINNED:** gate unit awaits R1/R2 | Pending | Unknown registration must refuse. |
| Q1: chain-source binding and truthful C1 fields/detail | **NOT PINNED:** R1/R2 | Pending | Substituted source must refuse; evidence receipt must not claim D-166. |
| Q2: frozen pilot timing, retention, exclusions, covariate-only busy cores | **NOT PINNED:** protocol not authored | Pending | Changed frozen parameter or busy-core exclusion must fail. |
| Q2: upper-confidence-bound sizing and no-cutoff branches | **NOT PINNED:** campaign reduction not implemented | Pending | Point-estimate sizing or excess budget must not qualify. |
| Q3: dedicated chain, recorder journal, bounded teardown | **NOT PINNED:** chain not authored | Pending | Residue or forbidden journal/ledger use must fail. |
| Q3: authoring refusals, manifest, sidecars, render-only | **NOT PINNED:** authoring tool not implemented | Pending | Class, chain or frozen-protocol override must refuse. |
| Q3: typed probe, both dispatch points, freshness and tracked digests | **NOT PINNED:** receipt unit awaits R1/R2 | Pending | Ambiguous exports, stale receipt or changed digest must refuse. |
| Q3: verify-only starts no collection/load/power; calibration compatibility | **NOT PINNED:** executor tests pending | Pending | Measurement launch during verification must fail the test. |
| F1: artifact inventory, cleanup before courier, descriptive courier summary | **NOT PINNED:** driver/courier integration pending | Pending | Residue must prevent courier launch. |
| F2: load-log identity/support join; complete native interior support | **NOT PINNED:** remaining harness/campaign work | Pending | PID reuse, unsupported intervals or partial coverage must not qualify. |
| Q3: handback and runbook amendments | **NOT PINNED:** docs deferred with executor | Pending | Docs must distinguish evidence bindings from calibration custody. |

## Verification notes

The changed harness module passed **47 offline tests**. Its existing live collection and real-load tests were deliberately excluded. An initial stdin-based replay failed because multiprocessing could not reload `<stdin>`; the file-backed replay passed.

The quick suite passed **152/153 selected modules**. Its sole failed module had two process-identity failures consistent with the confirmed `/bin/ps` sandbox denial. Full output is in [the quick-suite log](/tmp/stage-a-evidence-quick.log).

The fixture census could not observe processes. `launchctl list | grep joulewise.night` produced no matches before and after, but standalone `launchctl list` failed; this is not proof of unchanged installed-job state.

## Residual risk

This is a partial harness change, not an executable Stage A night. Campaign admissibility, teardown, statistical reduction, probe authentication and live operation remain unverified.