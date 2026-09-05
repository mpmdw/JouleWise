```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: doc008 lacks sign-off, the Git-fixture guard is red, R7 path handling regressed, and an ARM fixture is timing-dependent.",
  "workspace": {
    "base_requested": "origin/int/2026-09-04-fan-wave-1",
    "base_mode": "exact",
    "head_start": "481b95deb6296252e5c685e1d9865f086e653acc",
    "head_end": "481b95deb6296252e5c685e1d9865f086e653acc",
    "upstream_end": "481b95deb6296252e5c685e1d9865f086e653acc",
    "branch": "int/2026-09-04-fan-wave-2"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/wave-2/03-refuter-contract-integrated-round-3.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "round1": {
      "F1": "CURED",
      "F2": "CURED",
      "F3": "CURED",
      "F4": "CURED",
      "F5": "CURED",
      "F6": "CURED"
    },
    "round2": {
      "R2-F1": "CURED",
      "R2-F2": "CURED",
      "R2-F3": "NOT_CURED",
      "R2-F4": "CURED"
    },
    "findings": [
      {
        "id": "R3-F1",
        "severity": "blocker",
        "location": "docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md; commit 4119eb0d03b514d8787da506afce974f1bd897cb",
        "text": "The asserted doc008 sign-off is absent: HEAD has b50f1493ae and restored terms, but not successor 4119eb0d03; the ruling still says WITHHELD."
      },
      {
        "id": "R3-F2",
        "severity": "blocker",
        "location": "tests/test_git_fixture_maintenance.py:171; tests/test_issue_dg071_dg075_statistics.py:995,1107; tests/test_s0_line_audit_guard.py:103",
        "text": "The estate-wide no-direct-git-init guard finds three calls left by one-name-sweep and LINE-AUDIT-GUARD-01; the fixtures omit its four maintenance controls."
      },
      {
        "id": "R3-F3",
        "severity": "should_fix",
        "location": "tests/test_paper_round7_artifacts.py:864-868",
        "text": "R7F adds a lexical /var assertion, regrowing round-1 F5 when the producer resolves /private/var; aggregate and exact tests fail."
      },
      {
        "id": "R3-F4",
        "severity": "should_fix",
        "location": "tests/test_arm_readiness_integration.py:175-218,317-333",
        "text": "The integration fixture uses the real clock and minimum evidence horizon: the long run expired BETA/GAMMA, but immediate exact replay passed, proving timing dependence."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "mods=$(git diff --name-only origin/int/2026-09-04-fan-wave-1..HEAD -- 'tests/test_*.py' | sed 's#/#.#g;s#\\.py$##' | tr '\\n' ' '); env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest docs.paper.fill-rehearsal.test_select_outcome_branches $mods",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAIL: test_alpha_beta_gamma_end_to_end_pass_and_no_hash_cycle (profile='BETA')",
          "FAIL: test_alpha_beta_gamma_end_to_end_pass_and_no_hash_cycle (profile='GAMMA')",
          "FAIL: test_every_test_module_routes_git_initialization_through_shared_helper",
          "FAIL: test_missing_events_is_incomplete_in_producer_and_driver",
          "FAILED (failures=4, skipped=45)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1927 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git merge-base --is-ancestor 4119eb0d03b514d8787da506afce974f1bd897cb HEAD; a=$?; git grep -q 'doc008 sign-off RECORDED' HEAD -- docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md; g=$?; printf 'signoff_ancestor=%s signoff_text=%s\\n' \"$a\" \"$g\"; test \"$a$g\" = 00",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "signoff_ancestor=1 signoff_text=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "signoff_ancestor=0 signoff_text=0"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_every_test_module_routes_git_initialization_through_shared_helper",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "- {'test_issue_dg071_dg075_statistics.py': (995, 1107),",
          "-  'test_s0_line_audit_guard.py': (103,)}",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_missing_events_is_incomplete_in_producer_and_driver",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test.*OK"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_arm_readiness_integration.ArmReadinessIntegrationTests.test_alpha_beta_gamma_end_to_end_pass_and_no_hash_cycle",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test.*OK"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "printf 'reduce=%s D172=%s/%s\\n' \"$(shasum -a 256 joulewise/reduce.py | cut -d' ' -f1)\" \"$(rg -c '^\\| D-172 \\|' docs/decision_log.md)\" \"$(rg -c '^## D-172:' docs/decision_log.md)\"; git log --first-parent --format='%s' origin/int/2026-09-04-fan-wave-1..HEAD | rg -o 'fan-[A-Za-z0-9-]+' | rg -v '^fan-wave-2$' | sort -u | shasum -a 256",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "reduce=7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc D172=1/1",
          "830a3f52600933b84fb4071d622e5a59276e70d2a70558373350849e244c35c2  -"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "reduce=7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc D172=1/1[\\s\\S]*830a3f52600933b84fb4071d622e5a59276e70d2a70558373350849e244c35c2"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_campaign_generator_core_parity.py --baseline-ref origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PARITY_DIFF_EMPTY generator=ALPHA files=120",
          "PARITY_DIFF_EMPTY generator=BETA files=120",
          "PARITY_DIFF_EMPTY generator=GAMMA files=112",
          "PARITY_OK generators=3 files=352 excluded=['generate_configs.py', 'plan_tree.json', 'plan_tree.sha256'] baseline=origin/main"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PARITY_OK generators=3 files=352.*baseline=origin/main"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Only modules touched by the integrated diff ran, per the preflight rule.",
      "needs": "Magistrate runs the whole suite after R3-F1 through R3-F4 are repaired."
    },
    {
      "id": "G2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No live launcher, hardware, or quiet-machine measurement ran; COLDGATE-HANDOFF-01 remains an operationally fenced handoff.",
      "needs": "Ed ratification and lead-controlled real-entry verification remain required."
    }
  ]
}
```

## Findings

R3-F1 is a direct contradiction of the review premise. The merge contains doc008's compaction and restored terms, but its own ruling record still withholds approval. Integrate `4119eb0d03` before treating doc008 as signed.

R3-F2 is the requested guard/tripped-by-another-landing seam. The guard is intentional and estate-wide; exempting the two modules would defeat its contract. Route the three calls through the shared helper.

R3-F3 is round-1 F5 regrown in a new test added by R7F. Canonicalize only the expected scratch path; producer semantics and the accepted exit-3 partition stay intact.

R3-F4 is a nondeterministic fixture defect: the aggregate run refused BETA/GAMMA on clock freshness, then the identical method passed immediately. Freeze the test clock rather than widening production horizons.

### Landing/ruling and seam audit

All nineteen named remote landing tips are ancestors of HEAD and no branch-name deviation was found. CUSTODY leaves the D-138 reducer restored; FLOOR-WORKLOAD-SIZING retires under D-166; MODULARITY and its fixture cure compose; PREWINDOW carries its F4 wording cure and R-12 attribution; R7F carries the ruled exit partition but R3-F3; aud-wo-rows is bridge-only; doc008 has R3-F1; FIXTURE-MODERNIZATION has R3-F4; LINE-AUDIT-GUARD composes except for R3-F2; rq-refresh stays non-claiming; GENERATOR-CORE is D-161-scoped and parity-clean; C3 recognition composes with custody; PHASE-SHARE is diagnostic; docs-vs-truth remains conservative; GAMMA roster is a guard; one-name-sweep preserves values but contributes two R3-F2 calls; p1-rows keeps physical confirmation pending; COLDGATE-HANDOFF remains fenced; the Git-fixture sweep itself is coherent but detects R3-F2. Ordering-sensitive seams (MODULARITY→fixture, GENERATOR→GAMMA guard, R7F→one-name) otherwise hold.

### Claim-bearing and pinned-surface inventory

- The new frozen detection-floor closed-set registry has JSON digest, sidecar, and source pin `fc91df6d14b02d17dba31d1018c31287b65bde2d94f2b608825411f98b2aed1d`; it moves four calibration scopes and nine metrics from code into authenticated data without changing a floor value.
- The historical `p2_015_floors` campaign constants move into `campaign_spec.json`; validation keeps the issued A/B/B/A estimator and governed `n >= 5`. The corpus is historical/voided, and no new floor is asserted or issued.
- The three live `_v5` generator sources change under the adopted D-161 shared-core ruling. Their source/self-bound plan identities rotate, while V7 proves all 352 other generated files byte-equal to `origin/main`; no pre-registered workload constant changes.
- The R7 producer digest is explicitly repinned to `12d0293b2615eaeb872aa5885cad1ac57b853dc975fb5f376a5ce36ef6000688` for the ruled exit-code split. Issued XD/AQ/F4 artifacts, their values, and statuses are byte-stable.
- Results-fill registry changes only placement/guard vocabulary: DS-32 and PG-08 gain repeated outcome placements while remaining `STOP_FILL`; OB-01/TR-01/OR-01 are new `STOP_FILL` rows; DG-072 is renamed from “two-overlap count” to “overlap count of two” with value, digest, and status unchanged.
- D-172 adds one adopted process index row and one body after packet-21 cold-gate review. PROJECT_STATUS compaction restores its governed-terms block and makes no `_v5` data claim, but R3-F1 withholds its required semantic sign-off. RQ and P1 status edits remain honest: four Section-3 characterizations are uncollected/outside `_v5`, and physical confirmation remains pending.
- D-138's four governed implementation files, calibration artifacts, the D-166 dominance registration, and issued Round-7 XD/AQ/F4 bytes are unchanged. `reduce.py` is exactly `7b9c0d28…`; `identity_pins.py` is format-only/AST-equivalent. No unrefrozen pinned-byte change was admitted.

No additional doctrine/process change bypassed a required cold gate: D-172 used packet 21; COLDGATE-HANDOFF implements an adopted handoff but does not itself satisfy the remaining Ed/real-launch gate.

## Residual risk

The full suite is magistrate-owned. Retained-corpus tests skipped where corpora were absent, and no `[QUIET-MAC]`, hardware, or live-launch evidence was attempted.
