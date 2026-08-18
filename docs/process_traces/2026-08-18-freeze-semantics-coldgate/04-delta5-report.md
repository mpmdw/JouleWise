```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Mandatory controls and all 61 focused tests pass, but post-validation symlink substitution still escapes every generator and the freeze regression leaves serialized successor status bytes unfrozen.",
  "workspace": {
    "base_requested": "74028559cfd3a746fc9484672479ed109f24d00e",
    "base_mode": "exact",
    "head_start": "b6b5e6d3445fe47620e7292244647f0c88b9be80",
    "head_end": "b6b5e6d3445fe47620e7292244647f0c88b9be80",
    "upstream_end": "6ddeb7d365772335717e3143dceccf4382c49f8d",
    "branch": "impl/successor-generator-repairs"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "symlink_class": "NOT_CLOSED: all pre-created link cases refuse before writes, but post-validation ancestor substitution escapes in all families",
    "mutation_probes": "ALL_KILLED; no tautology list",
    "consult_conformance": "INCOMPLETE: B2 identity/path/lineage sites conform, but B3/README freeze transition remains unrealized because preserve mode replays draft bytes",
    "freeze_fixture": "Production CLI entrypoint is byte-identical; the copied runtime models only three v2 profile-map entries and one deterministic boot UUID. Receipts are genuine committed REFUSE receipts with valid GNU sidecars.",
    "profile_map": "Faithful miniature: the transaction registry lane must add v2 pack-name aliases to the existing ALPHA/BETA/GAMMA profiles",
    "stream_closure": "DO_NOT_MERGE b6b5e6d into the Phase-2 transaction until B1 and B2 are fixed and re-audited; the registry profile-map addition alone is insufficient",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "title": "Check-then-write boundary permits post-validation symlink escape in all three generators",
        "locations": [
          "configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py:484",
          "configs/campaigns/d117_floor_qwen25_7b_v1/generate_configs.py:2550",
          "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/generate_configs.py:409"
        ],
        "evidence": "/tmp/delta5-audit.hna75s/postcheck-substitution.log"
      },
      {
        "id": "B2",
        "severity": "blocker",
        "title": "Authenticated freeze regression does not transition serialized draft_status or README bytes",
        "locations": [
          "tests/test_d117_decode_contrast_plan.py:855",
          "configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py:1752",
          "configs/campaigns/d117_floor_qwen25_7b_v1/generate_configs.py:2081",
          "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/generate_configs.py:1754"
        ],
        "evidence": "/tmp/delta5-audit.hna75s/freeze-status-field-audit.log"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest -v tests.test_d117_floor_qwen25_1p5b_plan tests.test_d117_floor_qwen25_7b_plan tests.test_d117_decode_contrast_plan",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 61 tests in 33.622s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 61 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_d117_decode_contrast_plan.D117GammaPlanTest.test_dual_generation_transaction_and_generational_induction",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 5.674s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_d117_decode_contrast_plan.D117GammaPlanTest.test_authenticated_freeze_transition_preserves_frozen_bytes",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 12.938s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "pre-create target pack, pack-file, extraction-spec, sidecar, configs/campaigns-ancestor, and configs/floor_mint-parent symlinks; invoke each successor generator with --no-preserve-current-frozen-bytes",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "16 valid cases refused with generator exit 1",
          "all output-root regular-file counts=0; all escape-file counts=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "refused.*escape-file counts=0"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "invoke each generator with a deterministic filesystem substitution immediately after validate_generation_write_boundary returns",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "alpha postcheck_substitution_exit=0 escape_files=117",
          "beta postcheck_substitution_exit=0 escape_files=117",
          "gamma postcheck_substitution_exit=0 escape_files=98"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "refusing generation|escape_files=0"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_d117_floor_qwen25_1p5b_plan.D117FloorQwen251p5BPlanTests.test_successor_generation_threads_plan_identity_and_lineage",
      "cwd": "/tmp/delta5-audit.hna75s/mutations/lineage",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 'launch_lineage_required' not found",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "launch_lineage_required.*not found"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_d117_floor_qwen25_1p5b_plan.D117FloorQwen251p5BPlanTests.test_target_status_inventory_and_invalid_modes_are_fail_closed",
      "cwd": "/tmp/delta5-audit.hna75s/mutations/inventory",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "ValueError: generation output inventory escapes the target allowlist",
          "FAILED (errors=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "inventory escapes the target allowlist"
      }
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_d117_floor_qwen25_1p5b_plan.D117FloorQwen251p5BPlanTests.test_successor_generation_threads_plan_identity_and_lineage",
      "cwd": "/tmp/delta5-audit.hna75s/mutations/preserve",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "generation failed: generated file drifted: configs/campaigns/d117_floor_qwen25_1p5b_v2/plan_tree.json",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "plan_tree.json"
      }
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_d117_decode_contrast_plan.D117GammaPlanTest.test_generation_refuses_symlinked_write_inventory_before_any_write",
      "cwd": "/tmp/delta5-audit.hna75s/mutations/sidecar",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "(name='sidecar') ... FAIL",
          "AssertionError: 0 == 0"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "name='sidecar'.*FAIL"
      }
    },
    {
      "id": "V10",
      "kind": "inspection",
      "cmd": "git diff --check 7402855..b6b5e6d; git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "diff check clean",
          "worktree clean; branch ahead 2"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "clean"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "b6b5e6d does not close the generator stream: filesystem substitution remains escapable and D-6/R-7 frozen-status bytes are not produced.",
      "needs": "Repair both blockers, add discriminating regressions, and run another delta audit before merge."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The whole-repository canonical suite was not requested or rerun; round 4's earlier canonical attempt was incomplete.",
      "needs": "After blocker repair, rerun the canonical suite in addition to the 61 focused tests."
    }
  ]
}
```

## Findings

### B1 — blocker: symlink class is not closed

All mandatory pre-created cases now behave correctly. The original Delta-4 pack-directory probe was rerun for alpha, beta, and gamma, followed by pack-file, exact successor-spec, sidecar, `configs/campaigns` ancestor, and `configs/floor_mint` parent variants. Every valid case refused before a regular file was written, and every escape directory remained empty.

The implementation still separates validation from ordinary `mkdir()`/`Path.write_bytes()` operations. Replacing an ancestor immediately after `validate_generation_write_boundary()` returns produced:

- Alpha: exit 0, 117 escaped files.
- Beta: exit 0, 117 escaped files.
- Gamma: exit 0, 98 escaped files.
- Post-check replacement of `configs/floor_mint` additionally escaped one spec for each floor family.

This is the check-to-write substitution Delta-4 explicitly required the repair to prevent. Evidence: `/tmp/delta5-audit.hna75s/postcheck-substitution.log` and `/tmp/delta5-audit.hna75s/postcheck-floor-parent.log`.

### B2 — blocker: the freeze regression does not prove D-6/R-7

The fixture’s construction is otherwise honest:

- `scripts/generate_arm_readiness.py` is copied byte-for-byte and checked against production.
- The copied runtime changes only `_PROFILE_BY_PACK` by adding the three v2 aliases and `_current_boot_session_id()` by returning a deterministic UUID.
- The production freeze engine creates genuine JSON receipts, GNU SHA-256 sidecars, and plan-tree attachments.
- The receipts are committed and rediscovered through the production Git/sidecar authentication path.
- All three receipts are genuine `REFUSE` receipts, with real refusal reasons: `readiness_clock_preflight_refused`, `readiness_dependency_refused`, and `readiness_identity_pinset_frozen_mismatch`.

However, the test checks only the dynamically evaluated `GenerationIdentity.target_status` and the number of status expressions in source. It never asserts the serialized status fields or README.

A retained reproduction after the authenticated transition showed:

| Family | Dynamic status | Serialized `draft_status` | README |
|---|---|---|---|
| Gamma v2 | `frozen_by_d134_receipt` | 11 × `unfrozen_draft` | “unfrozen draft” |
| Alpha v2 | `frozen_by_d134_receipt` | 10 × `unfrozen_draft` | “unfrozen draft” |
| Beta v2 | `frozen_by_d134_receipt` | 10 × `unfrozen_draft` | “unfrozen draft” |

The new whole-inventory preserve branches replay the draft bytes, so the target-derived B3/README emission sites are never executed during the transition. This is residual mode-keyed output selection even though the individual field expressions use `target_status`.

Evidence: `/tmp/delta5-audit.hna75s/freeze-status-field-audit.log`.

### Mandatory-check disposition

| Check | Verdict | Evidence |
|---|---|---|
| Pre-created symlink probes | Pass, but broader class fails B1 | `/tmp/delta5-audit.hna75s/pack-dir/`, `symlink-variants/` |
| R-9 + 334-file transaction | Pass; v1 unchanged | `positive-controls.log` |
| v2→v3 and v3 preserve | Pass | `positive-controls.log` |
| Four mutation probes | All killed; no tautologies | `mutations/*/mutation-*-test.log` |
| Consult B2/B3 trace | Complete; B2 paths/identity/lineage conform, B3 transition residual remains | source trace plus `freeze-status-field-audit.log` |
| Freeze fixture authenticity | Genuine to stated fixture boundary; D-6/R-7 claim fails | `freeze-transition.log`, `freeze-status-field-audit.log` |
| Focused suites | 61/61, exit 0 | `focused-61.log` |

Consult B2 site trace:

- Identity threading: alpha `283/304`, beta `365/386`, gamma `195/218` — conformant, target-identity keyed.
- Stored floor-plan references: alpha `336/342`, beta `418/424` — conformant, ordinal keyed; gamma already pack-local.
- Reservation `--plan`: alpha `946`, beta `1338`, gamma `1032` — conformant, ordinal/target-pack keyed.
- ARM attachment: alpha `348`, beta `430`, gamma `228` — conformant, target-pack keyed.
- Projection replay: alpha `357`, beta `445` — pack-local preservation replay.
- Lineage: alpha `791`, beta `748`, gamma `877` — conformant, successor-family keyed.
- README status: alpha `1693`, beta `1949`, gamma `1677` — expression conformant, but not executed at freeze transition; B2.
- Generator-pin replay: alpha `368`, beta `456`, gamma `237` — pack-local custody replay.
- Producer replay: alpha `2076`, beta `2448` — pack-local custody replay.
- Tree/sidecar replay: alpha `2263`, beta `2524`, gamma `1951` — pack-local, but superseded by whole-inventory replay.

B3 sites all use `active_generation().target_status`:

- Alpha: `1459, 1546, 1827, 1985, 2005, 2096`.
- Beta: `1025, 1100, 1780, 2113, 2326, 2351`.
- Gamma: `599, 625, 741, 1404, 1531, 1647, 1819, 1857`.
- Gamma hardware note at `278` also uses target status.

Their source expressions conform, but their frozen serialized outputs do not.

## Residual risk

The deterministic post-validation probe demonstrates exploitability of the remaining race window; it does not measure the probability of an unsynchronized external process winning that race.

The transaction’s proposed v2 profile-map aliases are a faithful minimal registry-lane addition, but they do not repair either blocker. The full canonical repository suite also remains to be rerun after repairs.