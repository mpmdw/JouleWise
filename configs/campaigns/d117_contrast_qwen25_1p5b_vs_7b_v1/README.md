# D-117 gamma contrast pack v1 — unfrozen draft

This pack stages both prospectively required gamma arms: a 40-member decode
ABBA contrast and the D-122 40-member 256-token prefill ABBA contrast. It is
not armable and makes no data, verdict, receipt, or artifact-byte claim.

Authority order is D-117, D-122, D-123, D-124, then D-125. D-122 supersedes
the older design-memo and plan-factory decode-only text. The plan tree uses
the shared `joulewise.d117_plan_tree.v1` schema family and every top-level
artifact declares `draft_status = unfrozen_draft`.

The binding 40-member cadence is
`docs/process_traces/2026-08-07-plan-factory/DRAFT-U5U7.md` §6, “U7 — gamma
implementation session”: one midpoint between two 20-member ABBA halves. It
does not settle a mixed two-arm 80-member interpretation. This draft therefore
places references after science members 20, 40, and 60: both arm midpoints
plus the decode/prefill boundary, pending lead ratification at freeze.

The prefill prompt text is a labelled
`PROPOSED-PENDING-LEAD-RATIFICATION` candidate. The pack records exact draft
hashes so regeneration can be tested, not as a hash-freeze claim.

The consumer-family artifact is declaration-only. It names the deterministic
alpha/beta decode cell IDs but contains no aggregate-artifact SHA and is not a
pinset. A 256-token prefill floor or a ruled 128-to-256 transport rule remains
an explicit EMPTY slot.

Every receipt-count, arm-time receipt, and terminal-sequence slot remains
EMPTY with a TODO naming `impl/d117-ledger-recovery`. Identity pins remain
EMPTY pending U11. The D-124 estimator identity and stationarity-transfer
assumption are registered as proposed implementation identities; the
implementing unit must still land through D-118/D-121 before ratification.

Regenerate or check:

```text
python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/generate_configs.py
python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/generate_configs.py --check
python3 -m unittest tests.test_d117_decode_contrast_plan
```
