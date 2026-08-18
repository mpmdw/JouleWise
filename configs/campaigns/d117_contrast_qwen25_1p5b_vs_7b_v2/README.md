# D-117 gamma contrast pack v2 — status governed by the D-134 freeze receipt

Pack identity: `d117_contrast_qwen25_1p5b_vs_7b_v2` (`_v2`).

This description does not carry freeze status. The committed D-134 freeze
receipt and its plan-tree attachment are authoritative for this pack's frozen
state; the receipt pins `calibration_plan.json` by SHA, so this text and every
serialized `draft_status` field stay exactly as generated on both sides of the
freeze. An external unexpired PASS/GO arm receipt is required before launch.

This pack stages both prospectively required gamma arms: a 40-member decode
ABBA contrast and the D-122 40-member 256-token prefill ABBA contrast. It makes
no data, verdict, receipt, or artifact-byte claim.

Authority order is D-117, D-122, D-123, D-124, then D-125. D-122 supersedes
the older design-memo and plan-factory decode-only text. The plan tree uses
the shared `joulewise.d117_plan_tree.v1` schema family and every top-level
artifact declares `draft_status = as_generated_pre_d134_freeze`.

The binding 40-member cadence is
`docs/process_traces/2026-08-07-plan-factory/DRAFT-U5U7.md` §6, “U7 — gamma
implementation session”: one midpoint between two 20-member ABBA halves. It
does not settle a mixed two-arm 80-member interpretation. This pack therefore
places references after science members 20, 40, and 60: both arm midpoints
plus the decode/prefill boundary; the committed D-134 freeze receipt and its
plan-tree attachment are the ratification authority for that reading.

The prefill prompt text is a labelled
`PROPOSED-PENDING-LEAD-RATIFICATION` candidate. The pack records the exact
generated hashes so regeneration can be tested; the D-134 freeze receipt, not
this text, is what pins them.

The consumer-family artifact is declaration-only. It names the deterministic
alpha/beta decode cell IDs but contains no aggregate-artifact SHA and is not a
pinset. A 256-token prefill floor or a ruled 128-to-256 transport rule remains
an explicit EMPTY slot.

The receipt oracle is replay-derived from `joulewise.calibration_ledger` and
records 10 physical receipts for
5 logical operations per finalized pre/post
bracket session. Actual receipt bytes and the absolute terminal sequence remain
empty until arm and collection. Identity pins remain EMPTY pending U11. The
Both shared-edge ABBA contrast cells register the canonical D-124 common-mode
floor estimator treatment required to match their floor-calibration cells.

Regenerate or check:

```text
python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2/generate_configs.py
python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2/generate_configs.py --check
python3 -m unittest tests.test_d117_decode_contrast_plan
```
