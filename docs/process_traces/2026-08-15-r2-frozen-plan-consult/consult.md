```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "R2 rules FROZEN_PLAN as the committed calibration_plan.json inside PACK_ROOT, stored pack-root-relative and passed to commands as one resolved absolute literal.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "head_end": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "ruling_id": "R2",
    "choice": "a",
    "identity": "The exact committed bytes of PACK_ROOT/calibration_plan.json named by plan_tree.json.plan.path, bound by pack_id, normalized pack-root-relative path, plan_id, and SHA-256.",
    "resolution_rule": {
      "stored_reference": "Canonical POSIX path relative to PACK_ROOT; for the three current packs: calibration_plan.json.",
      "runtime_literal": "Resolve the stored reference once against an already-resolved PACK_ROOT, require an existing committed regular non-symlink file contained within PACK_ROOT, and pass that resolved absolute path unchanged as FROZEN_PLAN and every --plan value.",
      "forbidden": [
        "repository-root-relative interpretation",
        "current-working-directory-relative interpretation",
        "absolute paths stored in plan_tree.json",
        "basename normalization with PurePosixPath(...).name",
        "fallback between pack and repository roots",
        "a custody copy even when byte-identical"
      ]
    },
    "findings": [
      {
        "id": "R2-F1",
        "severity": "blocker",
        "title": "The runbook assigns FROZEN_PLAN to a second custody reservation-plan identity.",
        "ruling": "Change the runbook prose and examples; do not widen the parser to accept the custody plan."
      },
      {
        "id": "R2-F2",
        "severity": "blocker",
        "title": "Alpha and beta plan-tree producers store repository-relative plan paths that become nonexistent doubled paths under the correct pack-root resolver.",
        "ruling": "Change the producers and generated pack bytes; harden consumers to reject malformed references rather than stripping their prefix."
      },
      {
        "id": "R2-F3",
        "severity": "should_fix",
        "title": "Synthetic fixtures replace the producer value with calibration_plan.json and therefore mask the real-pack doubled-path defect.",
        "ruling": "Add a table-driven regression over all three committed D-117 packs and retain alias/custody-copy negative cases."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "8937dec9bd7be8f6d87694a739089ac8434b8bc9"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\).*8937dec9bd7be8f6d87694a739089ac8434b8bc9"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "for p in configs/campaigns/d117_floor_qwen25_1p5b_v1 configs/campaigns/d117_floor_qwen25_7b_v1 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1; do plan_sha=$(shasum -a 256 \"$p/calibration_plan.json\" | awk '{print $1}'); tree_sha=$(jq -r '.plan.actual_sha256' \"$p/plan_tree.json\"); freeze_sha=$(jq -r '.pack_identity.plan_sha256' \"$p/arm_readiness.freeze.receipts/freeze-0001.json\"); freeze_path=$(jq -r '.pack_identity.plan_path' \"$p/arm_readiness.freeze.receipts/freeze-0001.json\"); printf '%s %s %s %s %s\\n' \"${p##*/}\" \"$plan_sha\" \"$tree_sha\" \"$freeze_sha\" \"$freeze_path\"; done",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "d117_floor_qwen25_1p5b_v1 2afabe9854a8ac8c9d3d212bb0236fa787d660cf5ef452c66f2d84f97d4f227d 2afabe9854a8ac8c9d3d212bb0236fa787d660cf5ef452c66f2d84f97d4f227d 2afabe9854a8ac8c9d3d212bb0236fa787d660cf5ef452c66f2d84f97d4f227d calibration_plan.json",
          "d117_floor_qwen25_7b_v1 77056ffc154fc8d3fd461233a6ab54800a25055fdf3296c974996c32bd9612a0 77056ffc154fc8d3fd461233a6ab54800a25055fdf3296c974996c32bd9612a0 77056ffc154fc8d3fd461233a6ab54800a25055fdf3296c974996c32bd9612a0 calibration_plan.json",
          "d117_contrast_qwen25_1p5b_vs_7b_v1 4609b74f5b1b40eb4576a1f389c5d90be3edde532bdc017314cdb300c485a218 4609b74f5b1b40eb4576a1f389c5d90be3edde532bdc017314cdb300c485a218 4609b74f5b1b40eb4576a1f389c5d90be3edde532bdc017314cdb300c485a218 calibration_plan.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "d117_floor_qwen25_1p5b_v1 .* calibration_plan.json.*d117_floor_qwen25_7b_v1 .* calibration_plan.json.*d117_contrast_qwen25_1p5b_vs_7b_v1 .* calibration_plan.json"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "Resolve each real plan_tree.json plan.path by joining it to its pack root and report existence.",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "alpha: doubled path does not exist",
          "beta: doubled path does not exist",
          "gamma: PACK_ROOT/calibration_plan.json exists"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "alpha: doubled path does not exist.*beta: doubled path does not exist.*gamma: PACK_ROOT/calibration_plan.json exists"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The named council-verdict and sol-refuter-B files are absent from this detached worktree; their F6 content was available only through the prompt synopsis.",
      "needs": "Lead should compare this ruling against the source reports when consuming the verdict."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "The current runbook/producer/author combination must not arm a production window until the identity fixes, regenerated pack bindings, and real-pack regression land.",
      "needs": "Implement through the full D-118 gate, re-establish the append-only freeze state, recompute the final pack digest, and rerun the same-head dry run."
    }
  ]
}
```

## Findings

R2-F1 — blocker. The ruled identity is option (a): the committed pack’s `calibration_plan.json`, not a separately created custody reservation JSON. More precisely, its identity is the tuple:

`(pack_id, canonical pack-relative path, plan_id, SHA-256 of exact committed bytes)`

The freeze receipts settle this: all three already record `plan_path: calibration_plan.json`, and their plan SHA values exactly equal both the real pack files and `plan_tree.json.plan.actual_sha256`.

Per-surface changes:

- Runbook §4 — prose/example changes. `FROZEN_PLAN` must be the resolved literal path to `$PACK_ROOT/calibration_plan.json`; `PLAN_ID` must be the pack plan’s actual `plan_id`. Remove the custody `calibration-reservation.json` identity. Because the author rejects ambiguous shell expansion, the frozen `window.env` should contain literal absolute values, not `$MEASUREMENT_REPO` expansion.

- Runbook §6 — prose/template changes. “Freeze `FROZEN_PLAN`” means authenticate the already committed pack plan; it must not create or select a second JSON. Every readiness, reservation, `session-status`, `resume-finalize`, and `abort-session` call uses the same literal.

- E-8 — prose plus enforcement changes. Require the diagnostic result’s `frozen_plan.path`, `plan_id`, and `sha256` to equal the ruled literal, pack plan ID, and digest—not SHA equality alone. E-9 must use that identical `--plan` literal.

Rejected readings fail as follows:

- Custody reservation plan: creates an uncommitted second authority outside the committed-pack digest, presently carries a different window-style plan ID, and cannot satisfy D-134’s “pack plan SHA” requirement.

- `plan_tree.json` itself: lacks the required top-level `plan_id`, has a distinct digest, and participates in the freeze-receipt attachment lifecycle; treating it as the ledger plan would conflate the plan index with the indexed calibration plan.

- Repository-relative storage: alpha/beta only appear meaningful from the repository root, while gamma already uses pack-relative storage. One rule cannot interpret both without unsafe heuristics.

- Absolute storage: embeds machine-specific checkout paths in committed artifacts. Absolute paths belong only at the execution boundary.

R2-F2 — blocker. The authoritative storage rule is canonical pack-root-relative POSIX syntax. Reject absolute paths, backslashes, `.`, `..`, missing files, symlinks, non-regular files, escapes, and uncommitted bytes. Resolve strictly against `PACK_ROOT`; never use `.name` to sanitize an invalid reference.

Code-side changes:

- Alpha and beta producers must emit `plan.path: "calibration_plan.json"` and the same pack-relative sidecar path. Gamma already conforms.

- Reservation launch templates should derive their rendered `--plan` from the authoritative plan reference instead of independently rebuilding a repository-relative path.

- Add one shared resolver and use it in `_pack_identity`, dry-run rehearsal, generic evidence authoring, estimator derivation, manifest validation, and T-0 ledger derivation.

- The T-0 author must parse and bind `window.env`’s `FROZEN_PLAN`, use that literal for both captured commands, and verify the diagnostic’s path/ID/SHA triple. A byte-identical custody copy must refuse.

- Correct generated `plan_tree.json` and sidecars through the append-only freeze lifecycle. Do not rewrite `freeze-0001`; any changed pack bytes invalidate downstream pack-digest and dry-run evidence.

R2-F3 — should-fix. The regression should be table-driven over alpha, beta, and gamma real pack directories:

1. Load each committed `plan_tree.json` without rewriting `plan.path`.
2. Pass it through the production shared resolver.
3. Assert the result is exactly the resolved `PACK_ROOT/calibration_plan.json`.
4. Assert its bytes match the plan-tree SHA, sidecar, and freeze-receipt plan identity.
5. Feed that exact literal into diagnostic and reservation captures and require T-0 ledger derivation to pass.
6. Negative variants must reject a repo-relative prefix, `..`, an absolute stored reference, a symlink, basename aliasing, and a custody copy with identical bytes.

The existing synthetic fixture should also include the documented `FROZEN_PLAN` field instead of constructing `pack / "calibration_plan.json"` independently.

## Residual risk

The other non-identity env/chain mismatches reported by F6 remain separate blockers; this ruling does not silently disposition them. The referenced council/refuter report files were unavailable in this worktree, so the lead should perform a final source-report comparison before recording the council disposition.