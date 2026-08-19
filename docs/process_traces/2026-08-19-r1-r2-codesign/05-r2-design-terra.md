```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Adopt a hybrid: acceptance-generation indexing for replay plus a new immutable _v3 campaign-pack family; never regenerate frozen _v2 packs or re-mint their freeze-0002 receipts.",
  "workspace": {
    "base_requested": "9f7f091",
    "base_mode": "exact",
    "head_start": "9f7f0917751cd7cdbdd61351c98d2fac6132b9e4",
    "head_end": "9f7f0917751cd7cdbdd61351c98d2fac6132b9e4",
    "upstream_end": "085e9d8d50608150afa8380b19261c685ae1295c",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "Hybrid generation-indexed acceptance derivation plus a distinct _v3 D-117 pack family, bound to active r4.",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "In-place _v2 regeneration violates frozen pack identity",
        "detail": "Each _v2 tree has a committed, path-bound freeze-0002 receipt that pins its plan bytes. Changing those trees invalidates historical replay; a new _v3 family must instead inherit from _v2 and mint freeze-0003."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "The mint allowance must be selected by authenticated acceptance generation",
        "detail": "The static 0.010818 checks conflict with r4's n=17 derivation. Route screen and rule through the supplied authenticated acceptance, while retaining _ACCEPTANCE_SELECTION unchanged."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "9f7f0917751cd7cdbdd61351c98d2fac6132b9e4",
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "9f7f091[0-9a-f]+"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "nl -ba joulewise/calibration_bracketing.py | sed -n '40,205p'; nl -ba joulewise/floor_mint_estimator.py | sed -n '140,245p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "D-102 derivations are indexed by acceptance_id",
          "floor mint currently hard-codes 0.010818"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "0\\.010818"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "nl -ba joulewise/arm_readiness.py | sed -n '5425,5504p'; nl -ba configs/campaigns/d117_floor_qwen25_1p5b_v2/arm_readiness.freeze.receipts/freeze-0002.json | sed -n '117,145p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "successor receipt number is predecessor ordinal plus one",
          "d117_floor_qwen25_1p5b_v2 is bound by freeze-0002"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "freeze-0002"
      }
    }
  ],
  "flags": [
    {
      "id": "FLAG1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The parked cycle's stated _v2 regeneration/freeze-0002 re-mint conflicts with the committed receipt lineage now present in the tree.",
      "needs": "Magistrate should ratify F1: mint a _v3 family and freeze-0003 chain instead."
    },
    {
      "id": "FLAG2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No suite was rerun for this read-only design consult; the reported 33 mint-lane reds and separate R1 admission-gate failure are treated as baseline evidence.",
      "needs": "Run focused fan-out suites, then canonical discovery after implementation."
    }
  ]
}
```

## Findings

### F1 — Ratifiable decision

Adopt a two-axis design:

1. Acceptance semantics are generation-indexed by `acceptance_id`.
2. Campaign-pack identity is immutable by family generation.

The new successor is:

- `d117_floor_qwen25_1p5b_v3`
- `d117_floor_qwen25_7b_v3`
- `d117_contrast_qwen25_1p5b_vs_7b_v3`

Each `_v3` pack binds the active science-neutral r4 artifact, `d079_calibration_acceptance_v2_n17_r4`, including its artifact and derivation digests. Its mint allowance is derived from that authenticated artifact’s n=17 D-102 operatives, including the `0.009724` bracket screen. It retains `_ACCEPTANCE_SELECTION == "issued_d116_artifact_only"` exactly; selection and acceptance generation remain independent axes.

The new family succeeds `_v2` prospectively. `_v1` and `_v2` are immutable historical records, remain byte-replayable, and remain usable only as authenticated ancestry—not as silently upgraded live authority.

Each `_v3` freeze is `freeze-0003`, schema v2, with an authenticated predecessor reference to that profile’s `_v2/freeze-0002`. The existing `_v2` receipts stay untouched.

### F2 — Replay integrity

`joulewise/calibration_bracketing.py:155-185` already has the right acceptance-level primitive: `_D102_GENERATION_DERIVATIONS` maps n=19 artifacts to n=19 operatives and r3/r4 to n=17 operatives. Preserve and extend that approach; do not replace it with a global current-generation constant.

The required kernel rule is:

- A supplied issued acceptance authenticates by its own registry entry.
- Its mint policy is derived from its own authenticated `ratified_operatives`.
- The spec’s acceptance ID, artifact hash, derivation hash, bracket screen, rule, and applied allowance must all match that one generation.
- A v2 replay therefore still proves `max(observed_drift_s,0.010818)`.
- A v3 replay proves `max(observed_drift_s,0.009724)`.
- Cross-pairing an r2 acceptance with the r4 screen, or r4 with the old screen, refuses.

This preserves the byte-exact n=19 estimator era while letting the new family carry the r4-derived values. It also prevents a future default flip from mutating historical replay.

### F3 — Enumerated touch points

| Surface | Touch point | Required shape |
|---|---|---|
| Acceptance registry and derivation | `joulewise/calibration_bracketing.py:106-188, 369-377, 642-722` | Make a single authenticated mint-policy helper from the acceptance’s own derivation; fix `DEFAULT_ACCEPTANCE_BOUND_SHA256` at `:138-140` to r4’s digest or an r4 alias. |
| Floor-mint kernel | `joulewise/floor_mint_estimator.py:39-42, 140-205, 208-233` | Remove the global screen/rule as authority. Keep `_ACCEPTANCE_SELECTION`; validate it independently while obtaining screen/rule from the supplied acceptance. |
| Generalized mint | `scripts/mint_floor_artifact_generalized.py:61-68, 570-642, 2173-2203` | Replace static V2 screen parsing with post-authentication comparison to `_v2_allowance_projection`, which is already acceptance-derived. |
| Detection-floor extraction | `scripts/extract_detection_floors.py:99-140`; `joulewise/floor_extraction.py:1102-1180, 2530-2583` | No new screen constant here. Feed it the v3-generated extraction specs; preserve the exact selection literal. |
| Frozen alpha generator | `configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py:125-152, 225-301, 437-457, 1387-1397` | Do not edit. Use it only as the audited source shape for a new `_v3` generator. |
| Frozen beta generator | `configs/campaigns/d117_floor_qwen25_7b_v2/generate_configs.py:196-237, 308-384, 894-931` | Do not edit; v3 must bind r4 and generate its own spec/tree. |
| Frozen gamma generator | `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2/generate_configs.py:337-374, 1691-1735, 2276-2305` | Do not edit; its current “any successor = r2” route is precisely why a v3-specific descriptor is needed. |
| Evidence author | `joulewise/arm_readiness_evidence.py:49-59, 1347-1390` | Keep v1’s immutable map. For successor generations derive the three same-ordinal siblings from the input pack identity, rather than binding `_v3` evidence to v1 trees. |
| Freeze chain | `joulewise/arm_readiness.py:242-266, 2680-2728, 5425-5504` | Existing generic successor logic supports v3; it computes `freeze-0003` from v2’s `freeze-0002`. |
| Test fixture copy list | `tests/test_arm_readiness_evidence_author.py:120-154` | Copy all registered issuance artifacts, including r3 and r4, rather than the present v1/r2 pair. |
| Golden pins | `tests/test_mint_floor_artifact_generalized.py:1276-1310, 9081-9119`; `tests/test_floor_mint_estimator.py:30-105` | Add n19/r2 and n17/r4 vectors; regenerate only affected v3/live goldens with the independent fixture oracle. |

`scripts/package_bundle_pack.py:37` is a public-bundle package tool, not the D-117 campaign-family generator. It should not be pulled into this transaction.

### F4 — Tooling and atomic re-freeze

Use bespoke derive/build tooling; do not ask the scalar-comparison reissue tool to prove v3 semantics.

1. Add a read-only/emit-only mint-policy derivation command that authenticates r4, extracts its D-102 operatives, and emits the exact acceptance/policy tuple used by generators and tests.

2. Add a deterministic v3-family builder that accepts that tuple and emits all three `_v3` trees plus the two `_v3` extraction specs. It must refuse existing destinations and assert it never writes `_v1` or `_v2`.

3. Add a family verifier that checks all three generated trees, sibling references, r4 pins, v2 byte preservation, and the two v3 extraction specs.

4. Re-author evidence only after the v3 pack commit, then create the required identity projections.

5. At `/Users/edr/JouleWise-measurement-20260818`, on the committed exact head, mint each v3 `freeze-0003` with its corresponding `_v2` predecessor root. Do not remove, rewrite, or “re-mint” any v2 `freeze-0002` receipt.

The science issuance remains r3/r4’s bespoke derive/build route. This task consumes r4; it does not issue a replacement D-079 artifact.

### F5 — Test fan-out to green

Focused gates, in order:

1. Acceptance/mint matrix: n19/r2 accepts `0.010818`; n17/r4 accepts `0.009724`; every cross-generation mismatch refuses.
2. Existing `_v1` and `_v2` generator `--check` paths reproduce byte-for-byte.
3. New v3 builder and verifier reproduce all three packs and both extraction specs from clean temporary outputs.
4. `tests/test_d117_floor_qwen25_1p5b_plan.py`, `tests/test_d117_floor_qwen25_7b_plan.py`, and `tests/test_d117_decode_contrast_plan.py` gain v3 assertions without moving v1/v2 goldens.
5. `tests/test_arm_readiness_evidence_author.py` derives actual v3 family evidence without monkey-patching the historical map; `tests/test_arm_readiness_lifecycle.py` proves the v3 freeze is `freeze-0003` and v2’s receipt replays unchanged.
6. Regenerate the affected generalized-mint golden hashes with `_fixture_canonical_sha256`, never through the mint implementation.
7. Run the focused suites, then `python3 -m unittest discover -s tests`.

R2 should eliminate all 33 mint-lane failures. The separate capture-label admission failure belongs to R1; do not mask it in this transaction. Canonical FULL GREEN requires that owner’s independent landing as well.

### F6 — Rejected alternatives and disagreements

- Flat `0.010818 → 0.009724` migration: rejected. It is already empirically refuted because it corrupts the n=19 estimator replay.

- Generation-indexing alone: rejected as insufficient. It preserves acceptance replay but does not preserve campaign-pack identity; the present v2 generators bind every successor to r2.

- `_v3` family alone with static mint constants: rejected. It creates a new pack name but retains the same replay flaw.

- Regenerate `_v2` in place: rejected. The tree contains r2-era, path-bound `freeze-0002` receipts. Rewriting any pinned plan/generator byte destroys the historical proof.

- Scalar-only reissue tooling: rejected for v3 derivation. It cannot establish changed v3-derived values.

I disagree with the brief’s apparent either/or between generation indexing and a v3 pack family: they address different identities and must be composed. I also disagree with treating the parked “freeze-0002 re-mints” as still valid after those receipts became committed r2 history. The correct continuation is a v3 successor and `freeze-0003`.

## Residual risk

The proposed v3 family increases artifact volume and therefore requires strict generator-inventory and byte-preservation tests. No new scientific parameter is introduced: r4 and the magistrate’s unchanged 165,000 budget remain the only claim-bearing inputs.