# v4 D/C/T series (Option B candidate, RUN_STATE 251)

`series_manifest.json` retains R15's indices and adds Option B's seeded sabotage
placement and two blind test reserves. Its new bytes need council admission
and an independent second-seat seed check before signature. The single-builder
check is `docs/align/v4/CLAIM-B-SEED-CHECK-sol.json`, reproducible with
`python3.13 -B scripts/check_align_v4_claim_seeds.py`. It independently checks
436 members, including every episode seed, first-turn seed and placement draw.

**Order.** W1, then C1–C8, then C9–C14 only as owed, then T1–T3. D_k is C_k, so
`--window-id D3` selects C3; there are no separate fit windows. C9–C14 are the six
pre-declared blind replacement calibration windows (R22-2 / R24, cap C14): each armed, in order,
ONLY to replace a STRUCTURAL bar of a C window (U1–U3 FAIL, whole-window capture failure,
zero-capture refusal beyond the retry), never on scores, counts or to repair low m;
calibration stays exactly 8 admitted windows (`insufficient_calibration` if a pair is below 39
after 8, or C14 is reached with fewer than 8 admitted).
T4/T5 are registered TEST RESERVE candidates, replacing structural bars only,
from fresh indices 200-215 per pair. The target stays three admitted T slots.
They are outside the current executable `order` and **not armable** until the
round-2 scheduler and lead U3 scope ruling land: N=22 currently covers only
T1-T3. No U constant changes in this build. See the protocol claim contract.

**Window shape.** Every C/T window has 22 members:

| Ordinals | Members |
|---|---|
| 1–4 | Original anchors |
| 5 | W1:5 sentinel; captures the window reference |
| 6–21 | Fresh held-out D members, alternating pair by pair |
| 22 | Late sentinel |

- Odd windows start with spam, even windows with bank. The first pair takes the even ordinals.
- Sabotage is drawn per window by `align-v4-sabotage-order-v1`, seed 20261110:
  one per pair and half, ordinals 7-20, separation >=3; SHA-256 rejection draw
  over lexicographic (spam ordinal, bank ordinal) choices. The protocol gives
  exact encoding. Re-arms never redraw. W1 is unchanged.
- A C-window sabotage member remains pool `known_h`, outside calibration m;
  Option B admits its H=0 GPU score to S. DC stays sealed for v5.
- The midpoint follows ordinal 11.

**Seeds.** Held-out seeds are distinct and consumed per pair in kit order: C1–C8
use 2–65, T1–T3 use 66–89 (exactly R15), and the contiguous reserve pool for C9–C14 is 100–147 (8 per pair per window; C13 132–139, C14 140–147), never 1 or 91–99. A zero-capture re-arm reuses the
same seeds.
Index 90 is explicitly unused. Test-reserve seeds use a separate contiguous
200-215 range; calibration, calibration-reserve, test and test-reserve ranges
are mutually disjoint. Original members retain their indices and seed values;
only fresh members' condition/pool labels change with placement.

**Ceiling.** An ordinary window may run to 59,520 s. A window carrying the two
escalation sentinels may run to 62,400 s (`window_ceiling_s`).

**Escalation sentinels (R20).** After a window whose **U4** is inconclusive (A15 / R21: not U5, which is inconclusive by
construction), the next
window appends two sentinels at ordinals 23 and 24 (after the late sentinel at 22, before
the closing reference/scaffold): `materialize --window-id C3 --extra-sentinels 2`, or
`align_v4_session.py prepare --window-id C3 --extra-sentinels 2`. Both are exact replays
of the admitted W1:5 trajectory (same D model, spam/benign, seed index 1, seed law,
sampler, budgets, cache policy and stack), separate batch-1 members with the normal idle
and thermal gates. They are supplemental diagnostics: U4's W and W-1 df are unchanged,
they join no identical-work group, use no held-out seed and never count toward captured
members or any calibration count. The manifest bytes do not change (never in W1).

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
- leaves any attempt other than the previous one provisional (R17: window k's final
  eligibility is due before the arm of k+2; the RUN_STATE 216 "from window 6" fence is withdrawn);
- arrives while calibration is pending or insufficient;
- arrives during an unreleased escalation;
- reaches a test window without the C1–C8 threshold freeze.

Details: [DCT-SERIES-MERGED.md](../../../../docs/align/v4/DCT-SERIES-MERGED.md).
