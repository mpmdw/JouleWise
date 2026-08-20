```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "60ddb03 is not blocked and weakens no generator-check property; a separate should-fix gap exists because legacy PACK evidence replay authenticates bytes but not the receipt's historical pack_sha256/head_commit semantics.",
  "workspace": {
    "base_requested": "afb7d57",
    "base_mode": "exact",
    "head_start": "60ddb03a903d1e005190c966960fb091ed4f0e53",
    "head_end": "60ddb03a903d1e005190c966960fb091ed4f0e53",
    "upstream_end": "60ddb03a903d1e005190c966960fb091ed4f0e53",
    "branch": "impl/r2-s0-mint-resolver (detached HEAD)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "disputed_finding": "not_a_blocker_against_60ddb03",
    "generator_observation": "non-defect: receipt semantic validation is outside generator --check",
    "findings": [
      {
        "id": "C1",
        "severity": "should_fix",
        "artifact": "joulewise/arm_readiness.py",
        "title": "Legacy frozen PACK evidence replay omits historical pack/head validation",
        "evidence": [
          "joulewise/arm_readiness.py:4248-4262 validates pack/head only when expected values are supplied",
          "joulewise/arm_readiness.py:5253-5264 and joulewise/arm_readiness.py:5385-5392 omit expected_pack_sha256 for frozen PACK evidence",
          "joulewise/arm_readiness.py:6871-6879 supplies both values only for WINDOW_CUSTODY LAUNCH_RECIPE evidence"
        ],
        "impact": "A coherently recommitted receipt, sidecar, freeze receipt, and plan binding could preserve the nested hash chain while carrying a false historical pack_sha256/head_commit.",
        "relation_to_commit": "pre-existing and untouched by 60ddb03"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD afb7d57 && git branch -a --contains HEAD && git diff --check afb7d57..60ddb03 && git diff --name-status afb7d57..60ddb03 && PYTHONDONTWRITEBYTECODE=1 python3 -c 'from pathlib import Path; from joulewise.arm_readiness import committed_pack_tree_sha256; root=Path(\"configs/campaigns\"); ids=(\"d117_floor_qwen25_1p5b_v3\",\"d117_floor_qwen25_7b_v3\",\"d117_contrast_qwen25_1p5b_vs_7b_v3\"); [print(i, committed_pack_tree_sha256(root/i)) for i in ids]' && shasum -a 256 configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json configs/campaigns/d117_floor_qwen25_7b_v3/arm_readiness.freeze.receipts/freeze-0003.json configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/arm_readiness.freeze.receipts/freeze-0003.json && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "M\ttests/test_d117_v3_family.py",
          "d117_floor_qwen25_1p5b_v3 1e3f1fa31027e57053c7d26bacf2f373cf2c9ed840ee2bb3befafd99302d63f6",
          "d117_floor_qwen25_7b_v3 6d0b9b758d6a37a69a88827cb47ac58566d957099a3e714143d2e6508a93e45f",
          "d117_contrast_qwen25_1p5b_vs_7b_v3 0d07194143702b266267f0faa7b051695ffb5e1c56dc7a69d0b2dca8aaa883ef",
          "0abfddb13fe8c5e69df3e6be5e2e7efe28d3690b6947d5ed850fcb9652f6ec64  configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json",
          "f232d076d54408851e5728b3f14e9b04e086d809bca3e1cdac0c3641e072578c  configs/campaigns/d117_floor_qwen25_7b_v3/arm_readiness.freeze.receipts/freeze-0003.json",
          "f32bd3a8e4dbd04bc5b1635818ba34394984d1d201d16f02efc21f0b01f31c73  configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/arm_readiness.freeze.receipts/freeze-0003.json",
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "M\\s+tests/test_d117_v3_family\\.py[\\s\\S]*## HEAD \\(no branch\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The published final-tree digests detect drift when independently checked, but arm replay does not itself reproduce and validate each legacy receipt's historical pre-authoring pack digest.",
      "needs": "Add an external pinset or an arm/CI verifier for historical receipt head and pack semantics."
    },
    {
      "id": "V2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This read-only review used source, diff, and digest inspection; mutation-backed unit tests were not executed.",
      "needs": "Lead may rerun the cited focused tests during final verification."
    }
  ]
}
```

## Findings

### C1 — should_fix: legacy frozen PACK evidence is byte-authenticated, but its historical pack/head claim is not

The lead’s principal contract reading is correct, but its cited mechanism is not the mechanism protecting the attacked receipt.

1. Generator `--check` contract

The R2 ruling defines `--check` as the self-regeneration/frozen-family regression step after `_v3` emission; evidence authoring and freeze minting are later, separate S4/S5 stages (`docs/process_traces/2026-08-19-r1-r2-codesign/14-r2-ruling.md:48-62`, `docs/process_traces/2026-08-19-r1-r2-codesign/14-r2-ruling.md:94-103`). The r6 amendment changes only the bound acceptance generation and sequencing consequences, not check-mode ownership (`docs/process_traces/2026-08-19-r1-r2-codesign/15-amendment-r6.md:15-29`).

The strongest evidence is execution order: all three `_v3 --check` commands passed during S3 (`docs/process_traces/2026-08-19-refreeze-execution/reports/S3-emission-report.md:91-104`), while the same report states those packs still had no authored evidence or freeze receipts (`docs/process_traces/2026-08-19-refreeze-execution/reports/S3-emission-report.md:154-162`). Receipt semantics therefore cannot have been a prerequisite of the ruled S3 check.

The frozen generator implements exactly that division. It parses the freeze/evidence files only to construct the expected inventory (`configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py:2560-2607`), then compares inventory and generator-owned regenerated bytes (`configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py:2608-2629`). It never validates an evidence receipt’s `pack_sha256`, `head_commit`, sidecar, or semantic predicates.

D-134 likewise lists generator `--check`, validators, extraction specification, attempt policy, and committed-pack digest as separate sibling conditions under `desk.current_pack` (`docs/process_traces/2026-08-11-5c-readiness-contract/consult.md:211-225`). No located authority assigns receipt-integrity validation to generator check mode.

Therefore, the execution refuter’s observation—changing `pack_sha256` while `--check` still exits 0—is true but is a non-defect of `--check`.

2. Production tamper path

The first refusal depends on how the tamper reaches production:

- For the exact attack—editing the committed receipt in the worktree without committing it—arm construction calls `_pack_record` before loading the freeze receipt (`joulewise/arm_readiness.py:6103-6115`). D-134 reads both disk bytes and the corresponding Git blob and refuses differences with `readiness_pack_digest_mismatch` (`joulewise/arm_readiness.py:2553-2564`, `joulewise/arm_readiness.py:2652-2667`). This behavior is pinned by `test_pack_mutations_refuse_bytes_path_mode_missing_extra_untracked_symlink` (`tests/test_arm_readiness_pack_digest.py:54-73`) and `test_verification_recomputes_current_pack_bytes_despite_skip_worktree` (`tests/test_arm_readiness_integration.py:318-358`).

- If only the altered receipt is committed, D-134’s disk/Git comparison passes, but the frozen evidence binding still contains its old SHA (`configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json:44-51`). Generic authentication recomputes the receipt digest and checks both the freeze item and sidecar, refusing with `readiness_evidence_digest_mismatch` (`joulewise/arm_readiness.py:4189-4215`). Current-receipt byte tampering is pinned generally by `test_replay_refuses_tampered_current_successor_bytes` (`tests/test_arm_readiness_lifecycle.py:1284-1316`).

- If an editor coherently rewrites the receipt, its sidecar, its freeze-receipt item, the freeze sidecar, and the plan’s freeze SHA, the byte-authentication chain can be made internally consistent. Here the lead’s cited `pack_sha256/head_commit` check does not close the attack: those comparisons are conditional on supplied expected values (`joulewise/arm_readiness.py:4248-4262`), while frozen PACK evidence is authenticated without `expected_pack_sha256` (`joulewise/arm_readiness.py:5253-5264`, `joulewise/arm_readiness.py:5383-5392`). The call around 6875 supplies both expected values only after filtering for `WINDOW_CUSTODY` `LAUNCH_RECIPE` evidence (`joulewise/arm_readiness.py:6863-6879`), not for `PACK` `MULTICELL_MINT`.

Freeze minting also deliberately calls evidence discovery with `pack_sha256=None` and `head_commit=None` (`joulewise/arm_readiness.py:5507-5528`). That is the independent C1 gap.

Every `_v3` claim-bearing configuration is marked `launch_lineage_required` by all three generators (`configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:934-945`, `configs/campaigns/d117_floor_qwen25_7b_v3/generate_configs.py:838-849`, `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:1027-1042`). The marked route is fail-closed:

- Launch authenticates the arm before consuming it, then verifies the consumption before `execve` (`scripts/launch_window.py:93-128`, `scripts/launch_window.py:226-249`).
- Consumed-arm replay re-authenticates the current pack and requires equality with the arm’s pack record (`joulewise/arm_readiness.py:7060-7111`); live replay also requires the arm to reproduce `PASS/GO` (`joulewise/arm_readiness.py:7152-7175`).
- The bundle writer authenticates marked lineage before creating the bundle directory (`joulewise/bundle.py:87-165`, `joulewise/bundle.py:925-947`).
- Floor extraction converts lineage authentication failures into member refusal reasons (`joulewise/floor_extraction.py:1907-1920`, `joulewise/floor_extraction.py:2107-2125`).
- Analysis raises on failed lineage authentication and requires one common authenticated lineage across the reduction (`joulewise/analysis_engine/inputs.py:2696-2714`, `joulewise/analysis_engine/inputs.py:2968-2998`).

Representative route tests are `test_honest_launcher_consumes_verifies_and_reaches_execve` (`tests/test_launch_window.py:284`), `test_analysis_input_refuses_missing_launch_consumption` (`tests/test_launch_window.py:404-413`), `test_floor_extraction_refuses_missing_launch_consumption` (`tests/test_launch_window.py:423-436`), and `test_malformed_and_mismatched_lineage_codes_reach_every_consumer` (`tests/test_launch_window.py:438-485`).

Thus every supported claim-bearing route traverses arm/consume lineage authentication. What is missing is specifically the historical semantic comparison inside the grandfathered frozen PACK evidence—not a bypass around the route.

3. No property was weakened by 60ddb03

The diff changes only `tests/test_d117_v3_family.py`.

At `afb7d57`, the test emitted a bare successor tree and immediately required `--check` to pass (`afb7d57:tests/test_d117_v3_family.py:100-150`). After S5 minting, that expectation was no longer satisfiable because the generated plan referenced `freeze-0003`, which was absent from the bare temporary root (`docs/run_reports/2026-08-19-t12-t13-session.md:118-128`). At that baseline, the property was red, not proven.

At `60ddb03`, the test now:

- proves the generator itself emits none of the four mint-custody directories (`tests/test_d117_v3_family.py:163-170`);
- overlays committed custody only before finalized-pack checking (`tests/test_d117_v3_family.py:121-129`, `tests/test_d117_v3_family.py:171-179`);
- retains the frozen-v2 generator byte-preservation assertion (`tests/test_d117_v3_family.py:180-191`);
- adds an explicit negative proving that deletion of generator-owned `order_manifest.json` still makes check mode fail (`tests/test_d117_v3_family.py:193-220`).

That is a lifecycle-correct repair plus stronger negative coverage. It does not weaken any property previously proven at `afb7d57`.

4. Verdict

The execution-lens finding is not a blocker against `60ddb03`. Its generator-specific allegation is a non-defect because receipt semantics are outside the frozen `--check` contract.

Separately, C1 is a true, pre-existing `should_fix` defect in `joulewise/arm_readiness.py`: legacy frozen PACK receipt replay authenticates exact nested bytes but does not independently validate the receipt’s historical `pack_sha256/head_commit`.

The current receipts have substantial provenance: the production evidence author derives pack SHA and reviewed HEAD without caller inputs (`joulewise/arm_readiness_evidence.py:2335-2340`, `joulewise/arm_readiness_evidence.py:2380-2401`) and rechecks both before publication (`joulewise/arm_readiness_evidence.py:2487-2519`). The three current final-tree and freeze digests also match the published S5 confirmation table (`docs/process/ed-s5-mint-decision-2026-08-19.md:71-85`). That supports treating C1 as should-fix rather than retroactively invalidating the currently committed packs.

The clean closure is an external, governed verifier or pinset—outside the immutable frozen pack—that:

- checks the current final committed-tree digest against the published/approved digest;
- resolves each v1 PACK receipt’s recorded `head_commit`;
- recomputes the D-134 pack digest from that historical pre-authoring tree;
- compares it with the receipt’s `pack_sha256`;
- verifies the complete receipt → sidecar → freeze → plan binding;
- runs in CI and again before arm issuance.

## Residual risk

This review did not execute mutation-backed tests because the assignment was read-only. It verified the diff, current committed-tree digests, published freeze hashes, and relevant source/test paths by inspection.