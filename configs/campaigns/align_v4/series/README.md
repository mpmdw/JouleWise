# Frozen v4 D/C/T series (merged build, RUN_STATE 226 R15)

`series_manifest.json` is the frozen series ruled in RUN_STATE 226 R15: Sol's
code base with Opus's allocation. It still needs one paired seed check before
the lead signs `series/admission.json`.

**Order.** W1, then C1–C8, then T1–T3. D_k is C_k, so `--window-id D3` selects
C3; there are no separate fit windows.

**Window shape.** Every C/T window has 22 members:

| Ordinals | Members |
|---|---|
| 1–4 | Original anchors |
| 5 | W1:5 sentinel; captures the window reference |
| 6–21 | Fresh held-out D members, alternating pair by pair |
| 22 | Late sentinel |

- Odd windows start with spam, even windows with bank. The first pair takes the even ordinals.
- Sabotage sits at 9 (second pair) and 18 (first pair).
- A C-window sabotage member is pool `known_h` and counts toward nothing.
- The midpoint follows ordinal 11.

**Seeds.** Held-out seeds are distinct and consumed per pair in kit order: C1–C8
use 2–65, T1–T3 use 66–89, never 1 or 91–99. A zero-capture re-arm reuses the
same seeds.

**Ceiling.** An ordinary window may run to 59,520 s. A window carrying the two
escalation sentinels may run to 62,400 s (`window_ceiling_s`); the placement of
those two sentinels is still unruled.

## Commands

```sh
python3.13 -B scripts/align_v4_series.py materialize --window-id C1
python3.13 -B scripts/align_v4_series.py materialize --window-id C1 --check
python3.13 -B scripts/align_v4_series.py packet --window-id C2 --sources S.json --out P.json
```

The first command writes `configs/campaigns/align_v4_c1`. Sizing gives every D
member the largest W1 D `member_s` from the committed W1 plan. Before R1, the
planning allowances are used and flagged.

The packet's `S.json` carries `history`, `checks`, `record_commit` and
`last_desk_passed_artifact_set_sha256`. `history` is the series ledger:
- **Attempt entries** start after W1. Their counts are bound to eligibility
  receipts. They may carry `desk_eligible_benign`, and the final counts may be
  lower than those desk counts but never higher.
- **`lead_release` entries** resume the series after two consecutive
  zero-capture attempts. Each has `ruling_id`, `text_sha256`,
  `resets: zero_capture_escalation`, `after_window: <last attempt id>` and
  `lead_signature`.

## Arming

**Every arm binds the series, W1 included** (`align_v4_series.bind_packet`).
The arm refuses, before the installer runs, any packet that:
- names another window, or skips or reorders windows;
- carries hand-edited counts;
- skips the C6 fence (prior calibration eligibility must be final from C6 on);
- arrives while calibration is pending or insufficient;
- arrives during an unreleased escalation;
- reaches a test window without the C1–C8 threshold freeze.

Details: [DCT-SERIES-MERGED.md](../../../../docs/align/v4/DCT-SERIES-MERGED.md).
