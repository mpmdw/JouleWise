# D-117 gamma contrast pack v5 — status governed by the D-134 freeze receipt

Pack identity: `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` (`_v5`).

This description does not carry freeze status. The committed D-134 freeze
receipt and its plan-tree attachment are authoritative for this pack's frozen
state; the receipt pins `calibration_plan.json` by SHA, so this text and every
serialized status field stay exactly as generated on both sides of the freeze.
The generated `calibration_plan.json` and `plan_tree.json` carry
`draft_status = as_generated_pre_d134_freeze`; the prospective
`analysis_manifest_v3.json` instead carries `freeze_status = frozen`.
An external unexpired PASS/GO arm receipt is required before launch.

This pack stages both prospectively required gamma arms: a 40-member decode
ABBA contrast over the D-166 pinned real-prompt profile and the 40-member
2048-token prefill ABBA contrast. It makes
no data, verdict, receipt, or artifact-byte claim.

Authority order is D-117, D-122, D-123, D-124, D-125, D-139, D-157, D-165,
then D-166. D-166 supersedes the synthetic decode prompt and p256 prefill text. The
plan tree uses the shared `joulewise.d117_plan_tree.v1` schema family.

The binding 40-member cadence is
`docs/process_traces/2026-08-07-plan-factory/DRAFT-U5U7.md` §6, “U7 — gamma
implementation session”: one midpoint between two 20-member ABBA halves. It
does not settle a mixed two-arm 80-member interpretation. This pack therefore
places references after science members 20, 40, and 60: both arm midpoints
plus the decode/prefill boundary; the committed D-134 freeze receipt and its
plan-tree attachment are the ratification authority for that reading.

The prefill prompt is `ISSUED-BY-G2A-PROMPT-PIN`, issued by
`prefill_pin/prefill_prompt_pin.json`. The pack records the exact
generated hashes so regeneration can be tested; the D-134 freeze receipt, not
this text, is what pins them.

The consumer-family artifact is declaration-only. It names the deterministic
alpha/beta decode cell IDs but contains no aggregate-artifact SHA and is not a
pinset. Its dedicated 2048-token prefill floor dependencies are
`d117-qwen3-1p7b-prefill-p2048-floor-v5` and `d117-qwen3-8b-prefill-p2048-floor-v5`. Both use
`exact_stack_only` under `exact_stack_only.v1`; no cross-length transport is
licensed or needed.

The receipt oracle is replay-derived from `joulewise.calibration_ledger` and
records 10 physical receipts for
5 logical operations per finalized pre/post
bracket session. Actual receipt bytes and the absolute terminal sequence remain
empty until arm and collection. Identity pins remain unpopulated pending U11.
Both shared-edge ABBA contrast cells register the canonical D-124 common-mode
floor estimator treatment required to match their floor-calibration cells.

Regenerate or check:

```text
python configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generate_configs.py --no-preserve-current-frozen-bytes
python configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generate_configs.py --no-preserve-current-frozen-bytes --check
```
