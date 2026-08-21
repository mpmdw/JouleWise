```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "C1 needs a static external pinset plus Git-object historical hashing and a mandatory generate_arm_receipt hook; a CLI-only hook is bypassable.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "bea06481275b3b23e9f9777e0ac9206287155d6b",
    "head_end": "bea06481275b3b23e9f9777e0ac9206287155d6b",
    "upstream_end": "bea06481275b3b23e9f9777e0ac9206287155d6b",
    "branch": "impl/d144-followups-prewindow"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "H1",
        "severity": "should_fix",
        "title": "Historical receipt semantics are not yet mandatory at the arm boundary",
        "detail": "The existing helper hashes HEAD plus worktree bytes, while legacy PACK replay only compares pack/head when expected values are supplied. Add a Git-object historical hash primitive, an external immutable-pack pinset, and invoke it directly from generate_arm_receipt before any arm custody output."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "set -e; rg -N '\"head_commit\": \"[0-9a-f]{40}\"' configs/campaigns/*_v[123]/arm_readiness.evidence/*.json | sed -E 's/.*\"head_commit\": \"([0-9a-f]{40})\".*/\\1/' | sort -u | while IFS= read -r oid; do git cat-file -e \"${oid}^{commit}\"; printf '%s present\\n' \"$oid\"; done; printf 'heads='; rg -N '\"head_commit\": \"[0-9a-f]{40}\"' configs/campaigns/*_v[123]/arm_readiness.evidence/*.json | sed -E 's/.*\"head_commit\": \"([0-9a-f]{40})\".*/\\1/' | sort -u | wc -l; printf 'receipts='; find configs/campaigns -path '*/arm_readiness.evidence/*.json' -type f | wc -l; git rev-parse --is-shallow-repository",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "c3d805ee94629a0588f44b0ccb8430fd52ec07b3 present",
          "heads=       5",
          "receipts=      99",
          "false"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "heads=\\s*5[\\s\\S]*receipts=\\s*99[\\s\\S]*false"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --check && git status --short --branch && git rev-parse HEAD @{upstream}",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## impl/d144-followups-prewindow...origin/impl/d144-followups-prewindow",
          "bea06481275b3b23e9f9777e0ac9206287155d6b",
          "bea06481275b3b23e9f9777e0ac9206287155d6b"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## impl/d144-followups-prewindow.*bea06481275b3b23e9f9777e0ac9206287155d6b"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "This is a D-144 independent design seat, not a ratified implementation contract.",
      "needs": "Magistrate should adopt or amend the pinset, direct-arm-hook, and archival-coordinate design before implementation."
    }
  ]
}
```

## Findings

### H1 — should_fix: proposed implementation contract

`committed_pack_tree_sha256()` is not directly suitable for historical computation: it queries `HEAD`, inventories the live worktree, and compares every live byte to the Git blob before applying the D-134 framing (`joulewise/arm_readiness.py:2553-2677`). That is correct for current-pack custody, but historical replay needs a Git-object-only sibling.

Implement `historical_pack_tree_sha256(repository, pack_path, head_commit)` in `joulewise/arm_readiness.py`:

- Require a full 40-hex commit, resolve `head_commit^{commit}`, run `git ls-tree -rz --full-tree <resolved-head> -- <pack-path>`, and read each listed blob with `git cat-file blob <oid>`.
- Retain the exact D-134 domain and framing: sorted UTF-8 relative path, NUL, mode (`100644`/`100755` only), NUL, byte length, NUL, SHA-256 of blob bytes, newline. Reject empty trees, non-blob/gitlink entries, duplicate/out-of-prefix/non-UTF-8 paths, or missing objects.
- Refuse `histsem_history_unavailable` before computation when `git rev-parse --is-shallow-repository` is true, when the commit/tree/blob cannot be read, or when Git fails. Do not fetch or repair history during CI or arming. The current checkout has all five recorded historical heads and is non-shallow; the verifier must preserve that as a hard precondition.

Add a static, versioned pinset outside every frozen pack, for example `configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json`. It must enumerate—not discover—nine `_v1`–`_v3` pack roots, their current final D-134 tree digest, plan-tree hash, freeze path/hash, and all 99 v1 PACK evidence entries (ID, kind, path, receipt SHA). Pinset changes require a new versioned governed artifact; no auto-reseal.

For each pinset item, the verifier must:

1. Authenticate the current pack against its pinned final-tree digest.
2. Verify plan-tree raw bytes and sidecar; require its arm attachment to name the pinned freeze path/hash.
3. Verify freeze raw bytes, canonical schema, deterministic sidecar, pack/plan identity, and that its PACK evidence inventory equals the pinset exactly.
4. For every legacy evidence receipt, verify canonical bytes, deterministic sidecar, freeze-item metadata/hash, receipt schema/ID/kind, and each fact-source hash.
5. Recompute the historical tree digest from that receipt’s recorded `head_commit` and require equality with `pack_sha256`.

This closes the conditional gap at `joulewise/arm_readiness.py:4249-4262`; legacy freeze replay currently supplies no expected pack hash, and only supplies head for the newer lifecycle route (`joulewise/arm_readiness.py:5255-5267`, `5363-5408`).

Run the same library verifier in two places:

- CI: add one early `python scripts/verify_legacy_receipt_semantics.py --repository-root .` step to `.github/workflows/ci.yml`, whose test job already uses `fetch-depth: 0` (`.github/workflows/ci.yml:17-28`).
- Pre-arm: call the library verifier directly in `generate_arm_receipt()` immediately after resolving the pack root and before `_pack_record()` or any custody write (`joulewise/arm_readiness.py:6099-6122`). Do not rely only on `scripts/generate_arm_readiness.py`; its `arm` branch is merely a wrapper (`scripts/generate_arm_readiness.py:108-113`). This is the same integration-seam pattern used by sampler teardown: controller-owned orchestration wraps otherwise untouched components (`joulewise/controller.py:809`, `1645-1675`).

Regression set:

- Clean corpus pass: all nine packs / 99 receipts.
- Shallow clone and missing historical-object fixtures: `histsem_history_unavailable`, no arm issuance.
- Defect shape: construct a Git fixture, rewrite receipt `head_commit` and `pack_sha256`, then coherently update receipt sidecar, freeze evidence hash/sidecar, and plan freeze hash/sidecar. The verifier must reach `histsem_historical_digest_mismatch`; a second case leaves the external pinset unchanged and must refuse its pin mismatch. This prevents a test that passes merely because an inner hash broke.
- Direct `generate_arm_receipt()` regression: histsem refusal occurs before an arm receipt/custody artifact is created.

WRITE_SCOPE for the implementation:

- `joulewise/arm_readiness.py`
- `joulewise/receipt_histsem.py`
- `scripts/verify_legacy_receipt_semantics.py`
- `configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json`
- `.github/workflows/ci.yml`
- `tests/test_receipt_histsem.py`
- `docs/contracts/receipt_histsem_verifier.md`

Do not modify `configs/campaigns/**` or the four r6-pinned estimator sources: `powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py`, and `reduce.py` (`docs/process_traces/2026-08-20-go-session/opus-seat-report.md:178-185`). `scripts/test_timings.json` is unnecessary: unmeasured modules receive the deterministic median fallback (`scripts/shard_tests.py:4-6`).

Stages: ratify this design → add focused fixtures/tests → implement hash primitive and pinset verifier → wire direct pre-arm and CI → run focused tests plus canonical suite → lead-owned kernel/queue/run-report closeout.

Scope boundary: this is an integrity/authenticity check for historical Git and frozen receipt claims. It does not reverse D-139 A1’s trusted-process threat model (`docs/decision_log.md:10047-10058`), nor is it an `_v3` lifecycle replay. `_v3` replay remains only at the pre-install measurement checkout; a location refusal is not pack corruption (`docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING.md:138-141`). The new verifier only performs static byte-binding and historical-object recomputation at other coordinates.

## Residual risk

Historic Git object retention becomes an availability gate: shallow, pruned, or otherwise incomplete history prevents CI/pre-arm authorization until a full governed checkout is supplied.