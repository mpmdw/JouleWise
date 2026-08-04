```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "FAIL: static control-flow audit found multiple grammar-legal workload carriers, so blocker_present=true and the D-107 third-failure return trigger fires; forced handoff prevented capture of the running focused-test and corpus probes.",
  "workspace": {
    "base_requested": "a6ce7af7c6c4e1119d6c4365fb63ce4482f9e246",
    "base_mode": "exact",
    "head_start": "a6ce7af7c6c4e1119d6c4365fb63ce4482f9e246",
    "head_end": "a6ce7af7c6c4e1119d6c4365fb63ce4482f9e246",
    "upstream_end": "a6ce7af7c6c4e1119d6c4365fb63ce4482f9e246",
    "branch": "impl/d100-bii-binding"
  },
  "pathspec": [],
  "unowned_dirty": [
    "joulewise/salvage_dangler.py",
    "tests/test_run_campaign.py",
    "tests/test_salvage_dangler.py",
    "BRIEF.md"
  ],
  "verdict": {
    "overall": "fail",
    "blocker_present": true,
    "d107_return_trigger_fires": true,
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Decidable supersets and shape-only leaves license workload bytes",
        "locations": [
          "joulewise/salvage_dangler.py:79",
          "joulewise/salvage_dangler.py:1117",
          "joulewise/salvage_dangler.py:1150",
          "joulewise/salvage_dangler.py:1179",
          "joulewise/salvage_dangler.py:1396"
        ],
        "scenario": "A valid abort fixture remains licensable after placing workload bytes in metadata.extra.node_cleanup[].error or .path, metadata.adapters.telemetry.command[] ending in .plist, summary.measurement_quality.remote_cleanup_failed[], an unbound 64-hex config_sha256, or an arbitrary finite numeric metadata leaf. These values pass their local predicates and are invisible to the defense-in-depth spelling walk."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "The exact inventory validates names, not producer provenance or file contents",
        "locations": [
          "joulewise/salvage_dangler.py:1469",
          "joulewise/salvage_dangler.py:1504"
        ],
        "scenario": "A foreign file can replace logs/runtime.log or another admitted production path before inspection; exact-set equality still passes and the newly computed digest merely freezes the substituted bytes. The b-i custody walk remains recursive and byte-complete, but it is a separate identity search and does not close this b-ii content-substitution residual."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD; git branch --show-current; git diff --stat; git diff --name-only; git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "joulewise/salvage_dangler.py",
          "tests/test_run_campaign.py",
          "tests/test_salvage_dangler.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_salvage_dangler.py"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --unified=20 -- joulewise/salvage_dangler.py; git diff --unified=20 -- tests/test_salvage_dangler.py; git diff --unified=20 -- tests/test_run_campaign.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Three-file composed diff inspected in full.",
          "No repository writes performed."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "No repository writes performed"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The focused-suite command was launched but its completion was not captured before the runner required an immediate final response; custody hashes, 769-file sweep, 3/3 licensing, and independent dynamic mutation transcripts therefore remain unreported.",
      "needs": "Lead must run the exact focused and independent probe commands at its gate; do not treat this report as P1-P6 execution-complete."
    },
    {
      "id": "G2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "C-A′ §7 says no genuinely open container was found, but the implementation introduces several open string supersets, including remote_cleanup_failed beyond the two residuals named in the prompt.",
      "needs": "Return the arc to the D-107 cold gate; there is no authorized bench round 3."
    },
    {
      "id": "G3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The authority's description of 24 predicate-satisfying repository bundles conflicts with the reported 23 environment_admission_failed bundles plus one abort/null bundle.",
      "needs": "Lead should correct the derivation record after independently reproducing the count; the runtime semantic gate already requires claim_reason=environment_admission_failed."
    }
  ]
}
```

## Findings

F1 — blocker: The D-107 return trigger fires.

The grammar’s open leaves can carry raw workload bytes while satisfying every local check:

- `metadata.extra.node_cleanup[].error` accepts any nonempty printable string up to 1024 characters. The comment names adapter/transport text but does not name the workload-substitution residual.
- `metadata.extra.node_cleanup[].path` accepts up to 4096 safe-path characters. A payload such as `WORKLOAD_OUTPUT_TOKEN_SEQUENCE` is valid.
- `metadata.adapters.telemetry.command[]` accepts arbitrary decimal strings or arbitrary safe paths ending in `.plist`/`powermetrics`; it does not validate the producer’s argv structure.
- `summary.measurement_quality.remote_cleanup_failed[]` accepts arbitrary safe-path strings and is an additional open superset not named in the stated F2 residual.
- Hash fields accept any 64 hex characters without binding `metadata.config_sha256` to `config.json`.
- Numeric metadata leaves accept any finite number without field-specific range or cross-field binding.

The later `_contains_workload_evidence` walk does not inspect these values semantically because their keys are not on its spelling list. Neutralizing that list therefore changes nothing. These are grammar-legal workload carriers and meet D-107 clause 7’s return condition.

F2 — should_fix: The production inventory’s exact 6/8/22-file sets are name sets only. A foreign file can occupy an admitted path and be frozen as though it were producer output. A 21-file production bundle does refuse because `_validate_idle_artifact_inventory` requires exact set equality, but exact equality does not establish the origin or admissibility of bytes under each name.

The separate b-i custody path still recursively visits regular files and performs chunked, overlap-safe raw-byte identity searches. That does not repair b-ii substitution under an admitted filename.

## Checks performed

- P1: closed-key implementation and all four regression shapes inspected. Dynamic completion was not captured.
- P2: failed by deterministic control-flow inspection through the carriers above.
- P3: failed carriers are independent of `_WORKLOAD_EVIDENCE_FIELD_NAMES`.
- P4: iterative walk and constant depth cap of 32 inspected; the 995-depth test exists, but no completed transcript was captured.
- P5: corpus and custody regressions inspected but not independently completed. The custody skip guards are honest: they skip only when the root is absent, then require exactly three subjects or exact per-file hashes. Pins remain unverified here.
- P6: full diff inspected; the D-106 interval/digest machinery and three `test_d106_*` methods showed no substantive edits beyond surrounding closure work. Independent byte/AST hashes were not completed.
- Clause 5: both real-bundle tests are structurally non-vacuous when custody exists. The earlier nested-test tightening is directionally correct, but it does not cover the open carriers in F1.
- F1 count: the final semantic predicate explicitly requires `claim_reason == "environment_admission_failed"`, so an abort bundle with `claim_reason: null` cannot seek the b-ii license even though the nested grammar itself tolerates null before that semantic gate.

## Residual risk

The lead must reproduce the focused suites, 769-file sweep, 3/3 custody licensing, custody SHA-256 pins, 995-depth behavior, and mutation matrix at its authoritative gate. Regardless of those results, F1 already requires returning the arc to the cold gate rather than performing bench round 3.