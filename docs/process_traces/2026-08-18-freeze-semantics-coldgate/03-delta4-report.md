```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "Round 3 passes the 57-test generational transaction through v3, but the closed-write invariant is broken by symlink traversal and mandatory red/freeze evidence remains incomplete.",
  "workspace": {
    "base_requested": "6ddeb7d365772335717e3143dceccf4382c49f8d",
    "base_mode": "exact",
    "head_start": "74028559cfd3a746fc9484672479ed109f24d00e",
    "head_end": "74028559cfd3a746fc9484672479ed109f24d00e",
    "upstream_end": "6ddeb7d365772335717e3143dceccf4382c49f8d",
    "branch": "impl/successor-generator-repairs"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "dual_generation_class_closed_generationally": false,
    "semantic_generational_probe": "pass through emitted v2-to-v3 generation and v3 preservation, but overall closure is rejected because every generator can escape its declared output root through an allowlisted symlink",
    "red_run_complete": false,
    "red_run_summary": "13 of 57 tests went red against pre-fix generators: 9 failures and 4 errors. All four newly added test methods went red; none passed. Six modified defect-bearing methods also went red. Three additional reds were generator-hash controls, not defect evidence. Several consolidated tests aborted before their deeper R-2 through R-7/R-9 assertions.",
    "new_tests_red": [
      "alpha.test_target_status_inventory_and_invalid_modes_are_fail_closed",
      "beta.test_target_status_inventory_and_invalid_modes_are_fail_closed",
      "gamma.test_target_status_inventory_and_invalid_modes_are_fail_closed",
      "gamma.test_dual_generation_transaction_and_generational_induction"
    ],
    "new_tests_passing_prefix": [],
    "consult_items": {
      "implemented_or_observed_conformant": [
        "identity threading uses target_is_current",
        "successor plan references and reservation --plan use target identity",
        "ARM attachment selection uses target pack root",
        "lineage uses target_is_successor_family",
        "README and emitted draft_status use target_status",
        "projection/producer/tree/sidecar/generator-pin replay remains preservation-keyed and pack-local"
      ],
      "diverged": [
        "D-3/I-2 closed write inventory: validation is lexical and does not prevent symlink traversal"
      ],
      "trace_complete": false,
      "new_mode_conditional_emission_found": false
    },
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "title": "All three generators follow allowlisted symlinks and write outside output_root",
        "locations": [
          "configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py:475",
          "configs/campaigns/d117_floor_qwen25_7b_v1/generate_configs.py:2531",
          "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/generate_configs.py:397"
        ]
      },
      {
        "id": "S1",
        "severity": "should_fix",
        "title": "The pre-fix red replay does not independently reach every R-2 through R-7/R-9 assertion"
      },
      {
        "id": "S2",
        "severity": "should_fix",
        "title": "The mandatory consult-conformance site-by-site trace was interrupted before completion"
      },
      {
        "id": "S3",
        "severity": "should_fix",
        "title": "Freeze transition was not executed using a fresh authenticated on-disk v2 freeze attachment"
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
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 57 tests in 9.607s",
          "FAILED (failures=9, errors=4)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=9, errors=4\\)"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest -v tests.test_d117_floor_qwen25_1p5b_plan tests.test_d117_floor_qwen25_7b_plan tests.test_d117_decode_contrast_plan",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 57 tests in 22.736s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 57 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "precreate each target v2 pack path as a symlink outside output_root, then invoke each generator with --no-preserve-current-frozen-bytes",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "alpha_escape_files=117 alpha_root_pack_is_symlink=yes",
          "beta_escape_files=117 beta_root_pack_is_symlink=yes",
          "gamma_escape_files=98 gamma_root_pack_is_symlink=yes"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "output path.*outside|symlink.*refus"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check 6ddeb7d..7402855; rg -n 'preserve_current_frozen_bytes|target_is_current|target_is_successor_family|target_status|write_bytes|write_artifacts' <three generators>",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "diff check clean",
          "mode-conditional and write sites enumerated"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "clean|enumerated"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The requested immediate return interrupted direct replays for red clauses hidden behind earlier consolidated-test aborts, the remaining consult site trace, and a fresh authenticated freeze transition.",
      "needs": "Lead must not treat the red-run or freeze-transition evidence as complete."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "Lexical output allowlisting does not constrain resolved filesystem targets.",
      "needs": "Reject symlinks/non-regular ancestors and targets, or use dirfd-relative no-follow writes, then add regressions for pack-directory, file, spec, and sidecar symlinks."
    }
  ]
}
```

## Findings

### B1 — blocker: the closed write inventory is escapable through symlinks

The inventory validation operates on relative path names, but the final writers use ordinary `Path.write_bytes()` calls:

- Alpha: `generate_configs.py:475-481`
- Beta: `generate_configs.py:2531-2535`
- Gamma: `generate_configs.py:397-406`

A pre-existing allowlisted target-pack symlink is followed. All three commands exited zero and wrote outside `output_root`: alpha 117 files, beta 117 files, gamma 98 files.

Representative reproduction:

```sh
mkdir -p /tmp/delta4-root/configs/campaigns /tmp/delta4-root/configs/floor_mint /tmp/delta4-escape
ln -s /tmp/delta4-escape \
  /tmp/delta4-root/configs/campaigns/d117_floor_qwen25_1p5b_v2

python3 configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py \
  --output-root /tmp/delta4-root \
  --pack-id d117_floor_qwen25_1p5b_v2 \
  --family-suffix _v2 \
  --no-preserve-current-frozen-bytes

find /tmp/delta4-escape -type f
```

This directly diverges from consult D-3/I-2. Validation must cover resolved ancestors and final targets before the first write and prevent link substitution during writing—preferably through dirfd-relative, no-follow operations rather than a check-then-write sequence.

Evidence: `/tmp/delta4-audit.Ydwh2n/symlink-probe`.

### S1 — should-fix: red-run evidence is not complete per regression

The combined pre-fix/new-test suite produced 13 reds:

- All four newly added methods went red; no newly added method passed pre-fix.
- The three `test_freeze_aware_successor_contract_is_forward_only` methods went red.
- The three `test_successor_generation_threads_plan_identity_and_lineage` methods went red.
- Three exact-inventory tests failed only because the pinned generator source hashes changed; those are controls, not defect-specific evidence.

Coverage hidden by early aborts:

- R-2: gamma reached and failed emitted-v2 preserve check; alpha/beta stopped earlier at missing v2 extraction specs.
- R-3: alpha/beta directly exposed missing v2 spec paths.
- R-4: reservation-plan assertions failed, but preserved-lineage assertions were not reached.
- R-5/R-6/R-9: the consolidated gamma test stopped on missing pre-fix `extraction_spec_rel` before induction/order assertions.
- R-7: all status tests stopped on missing `current_ordinal` before exercising the attachment-driven transition.

Evidence: `/tmp/delta4-audit.Ydwh2n/red`.

### S2 — should-fix: consult trace is incomplete

The inspected sites conform for identity threading, plan references, reservation arguments, target-pack attachment selection, lineage, status emission, and legitimate pack-local custody replay. No new mode-conditional semantic emission was identified.

However, the exhaustive site-by-site trace was interrupted. The confirmed divergence is D-3/I-2 through B1.

### S3 — should-fix: authenticated freeze-transition execution is missing

Inspection shows `target_status` reads `ARM_READINESS_ATTACHMENT["freeze_receipt"]`, and the 57-test green run confirms draft successor status is independent of preservation mode. The tests model frozen state by patching `ARM_READINESS_ATTACHMENT`; they do not create, commit, authenticate, and replay a fresh v2 freeze receipt on disk.

Therefore the strongest R-7 requirement—an authenticated draft→frozen transition followed by byte-stable preservation—was not independently executed.

## Check table

| Check | Executed | Verdict | Evidence |
|---|---:|---|---|
| 1. Pre-fix red replay | Partial | 13/57 red; all four new methods red, but deeper clauses were masked by early aborts | `/tmp/delta4-audit.Ydwh2n/red` |
| 2. Full 7402855 green bar | Yes | Pass: 57/57; consolidated transaction covers 334 additions, v1 preservation, v2 preserve, v2→v3, v3 preserve, lineage, and order | `/tmp/delta4-audit.Ydwh2n/green` |
| 3. Consult-conformance trace | Partial | D-3/I-2 diverged; inspected semantic sites otherwise conform | Source tree at `7402855` |
| 4. Freeze transition | Partial | Draft/mode independence passed; fresh authenticated transition not executed | Green focused suite |
| 5. Beyond-ruling hunt | Yes | Blocker found: symlink escape in all generators | `/tmp/delta4-audit.Ydwh2n/symlink-probe` |
| 6. Focused suites | Yes | `Ran 57 tests`, exit 0, `OK` | `/tmp/delta4-audit.Ydwh2n/green` |

## Residual risk

The passing transaction proves semantic induction through emitted v3 preservation, but v3→v4 generation was not separately probed. More importantly, no generational closure claim is acceptable until the symlink-capable write boundary is repaired and re-audited.