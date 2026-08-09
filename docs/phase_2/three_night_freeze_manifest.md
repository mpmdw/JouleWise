# Three-night packet freeze manifest

**Census target:**
`docs/strategy/2026-08-07-three-night-operator-packet.md` at the T1
checkpoint. **Current verdict: UNFROZEN / NO-GO.**

This manifest accounts for every literal token matched by:

```sh
rg -n -o '\[(PLACEHOLDER|BUDGET)[^]]*\]' \
  docs/strategy/2026-08-07-three-night-operator-packet.md
```

The command finds **59 occurrences**: three explanatory mentions (packet
lines 4 and 30) and **56 fill cells**. The tables below enumerate all 59, so
a future zero-match check cannot hide an unowned value. Line numbers refer to
the packet before its appended ABORT-code appendix; the appendix adds no
placeholder or budget token.

Status terms:

- **UNFROZEN** — a design value may exist, but it is not yet bound by the
  final reviewed pack hash.
- **BLOCKED** — the upstream artifact does not yet exist or depends on an
  earlier night.
- **STALE** — newer binding authority changed the required content.

The upstream names U5, U6, and U7 mean the ALPHA, BETA, and GAMMA campaign-pack
units defined by D-117 clause 7. “Pack freeze” means Phase B item B2 in the
40-hour plan: final identifiers, stage-launch recipes, budgets, hashes, fresh
receipt oracles, and readiness inputs are all bound together.

## Explanatory mentions — not fill cells

| ID | Packet location and literal | Upstream supplier | T1 status |
|---|---|---|---|
| M-01 | line 4, ``[BUDGET]`` in the pre-freeze status sentence | U5–U7 pack freeze | Explanatory mention; no replacement value. The statement remains true. |
| M-02 | line 30, ``[PLACEHOLDER]`` in the HOLD sentence | U5–U7 pack freeze | Explanatory mention; no replacement value. |
| M-03 | line 30, ``[BUDGET]`` in the HOLD sentence | U5–U7 pack freeze | Explanatory mention; no replacement value. |

## Night 1 — ALPHA, 1.5B floors (20 fill cells)

| ID | Packet cell | Upstream supplier | T1 status |
|---|---|---|---|
| A-01 | line 44, Window ID | U5 frozen plan identity | **UNFROZEN.** Candidate naming exists, but U5 had not generated after recovery. |
| A-02 | line 45, Plan root | U5 pack materialization | **BLOCKED** on merged recovery, fresh receipt oracle, and final pack hash. |
| A-03 | line 46, Frozen config IDs | U5 plan tree and stage manifests | **BLOCKED** on U5 generation and review. |
| A-04 | line 47, Total duration including at least 20% margin | U5 dry-run timing ledger and budget calculator | **UNFROZEN.** The packet header carries a 3.14-hour design estimate, not an arm value. |
| A-05 | line 48, Do-not-return-before time/signal | Frozen duration plus the arm timestamp; launcher supplies `measurement_complete` | **BLOCKED** until A-04 and the launch recipe freeze. |
| A-06 | line 58, Before-midpoint stage IDs | U5 `stage_launch.v1` recipe, first half | **BLOCKED** on U5. |
| A-07 | line 59, After-midpoint stage IDs | U5 `stage_launch.v1` recipe, second half | **BLOCKED** on U5. |
| A-08 | line 99, Readiness timeout minutes | U5 total budget converted to the validator’s timeout | **BLOCKED** on A-04 and the readiness validator. |
| A-09 | line 100, Pre-window label | U5 immutable Window ID | **BLOCKED** on A-01. |
| A-10 | line 108, Launch Plan root | Same frozen value as A-02, copied mechanically into the launch command | **BLOCKED** on A-02. |
| A-11 | line 120, settle/display-sleep/pre-calibration interval | U5 cumulative stage schedule | **BLOCKED** on the frozen launch recipe and measured dry-run timings. |
| A-12 | line 121, pre-calibration level-screen point | U5 cumulative stage schedule | **BLOCKED** on A-11. |
| A-13 | line 122, twelve bound members and bound-mint point | U5 cumulative stage schedule | **BLOCKED** on A-11 and the fresh receipt oracle. |
| A-14 | line 123, three start-reference point | U5 cumulative stage schedule | **BLOCKED** on A-13. |
| A-15 | line 124, absolute/null first-half science point | U5 cumulative stage schedule | **BLOCKED** on final U5 membership and timings. |
| A-16 | line 125, midpoint-reference point | U5 cumulative stage schedule | **BLOCKED** on A-15. |
| A-17 | line 126, remaining-null second-half point | U5 cumulative stage schedule | **BLOCKED** on final U5 membership and timings. |
| A-18 | line 127, three end-reference point | U5 cumulative stage schedule | **BLOCKED** on A-17. |
| A-19 | line 128, post-calibration point | U5 cumulative stage schedule | **BLOCKED** on A-18. |
| A-20 | line 129, `measurement_complete` point | U5 cumulative schedule plus launcher terminal event | **BLOCKED** on A-19 and final launch-recipe verification. |

## Night 2 — BETA, 7B floors (17 fill cells)

| ID | Packet cell | Upstream supplier | T1 status |
|---|---|---|---|
| B-01 | line 174, Window ID | U6 frozen plan identity | **UNFROZEN.** Candidate naming exists; U6 was not hash-frozen. |
| B-02 | line 175, Plan root | U6 pack materialization | **BLOCKED** on merged recovery, fresh receipt oracle, and final pack hash. |
| B-03 | line 176, Frozen config IDs | U6 plan tree and stage manifests | **BLOCKED** on U6 generation and review. |
| B-04 | line 177, Total duration including at least 20% margin | U6 dry-run timing ledger and budget calculator | **UNFROZEN.** The 3.24-hour header value is a design estimate. |
| B-05 | line 178, Do-not-return-before time/signal | Frozen duration plus arm timestamp; launcher supplies `measurement_complete` | **BLOCKED** on B-04 and launch-recipe freeze. |
| B-06 | line 187, 7B absolute and null blocks 1–5 config IDs | U6 `stage_launch.v1` recipe, first half | **BLOCKED** on U6. |
| B-07 | line 188, 7B null blocks 6–10 config IDs | U6 `stage_launch.v1` recipe, second half | **BLOCKED** on U6. |
| B-08 | line 218, Launch Plan root | Same frozen value as B-02, copied mechanically into the launch command | **BLOCKED** on B-02. |
| B-09 | line 230, settle/pre-calibration/level-screen interval | U6 cumulative stage schedule | **BLOCKED** on the frozen recipe and dry-run timings. |
| B-10 | line 231, twelve bound members and bound-mint point | U6 cumulative schedule | **BLOCKED** on B-09 and the fresh receipt oracle. |
| B-11 | line 232, three start-reference point | U6 cumulative schedule | **BLOCKED** on B-10. |
| B-12 | line 233, absolute/null first-half science point | U6 cumulative schedule | **BLOCKED** on final U6 membership and timings. |
| B-13 | line 234, midpoint-reference point | U6 cumulative schedule | **BLOCKED** on B-12. |
| B-14 | line 235, null second-half science point | U6 cumulative schedule | **BLOCKED** on final U6 membership and timings. |
| B-15 | line 236, three end-reference point | U6 cumulative schedule | **BLOCKED** on B-14. |
| B-16 | line 237, post-calibration/bracket-closure point | U6 cumulative schedule | **BLOCKED** on B-15. |
| B-17 | line 238, `measurement_complete` point | U6 cumulative schedule plus launcher terminal event | **BLOCKED** on B-16 and final launch-recipe verification. |

## Night 3 — GAMMA, model contrast (19 fill cells)

| ID | Packet cell | Upstream supplier | T1 status |
|---|---|---|---|
| G-01 | line 261, Window ID | U7 frozen plan identity | **STALE / UNFROZEN.** The label says decode contrast, but D-122 also requires the 256-token prefill arm on GAMMA. |
| G-02 | line 262, Plan root | D-122-compliant U7 pack materialization | **BLOCKED** on merged recovery, estimator, identity projection, and final hash. |
| G-03 | line 263, Contrast config IDs | U7 plan tree and stage manifests | **STALE / BLOCKED.** The supplier must include both the decode contrast and D-122 prefill arm. |
| G-04 | line 264, 1.5B floor artifact ID/hash | Governed ALPHA extraction and post-window mint | **BLOCKED** until ALPHA passes verdict, backup, extraction, and mint gates. |
| G-05 | line 265, 7B floor artifact ID/hash | Governed BETA extraction and post-window mint | **BLOCKED** until BETA passes verdict, backup, extraction, and mint gates. |
| G-06 | line 266, Total duration including at least 20% margin | U7 dry-run timing ledger after adding the D-122 arm | **STALE.** The packet header’s 2.80-hour decode-only estimate predates D-122 and cannot be frozen. |
| G-07 | line 267, Do-not-return-before time/signal | Frozen duration plus arm timestamp; launcher supplies `measurement_complete` | **BLOCKED** on G-06 and launch-recipe freeze. |
| G-08 | line 279, Blocks 1–5 config ID | U7 `stage_launch.v1` recipe, first half, revised for D-122 | **STALE / BLOCKED.** Decode-only staging is insufficient. |
| G-09 | line 280, Blocks 6–10 config ID | U7 `stage_launch.v1` recipe, second half, revised for D-122 | **STALE / BLOCKED.** Decode-only staging is insufficient. |
| G-10 | line 307, Launch Plan root | Same frozen value as G-02, copied mechanically into the launch command | **BLOCKED** on G-02. |
| G-11 | line 319, settle/pre-calibration/level-screen interval | U7 cumulative stage schedule | **BLOCKED** on the D-122-compliant recipe and dry-run timings. |
| G-12 | line 320, twelve bound members and bound-mint point | U7 cumulative schedule | **BLOCKED** on G-11 and the fresh receipt oracle. |
| G-13 | line 321, three start-reference point | U7 cumulative schedule | **BLOCKED** on G-12. |
| G-14 | line 322, first-half contrast point | U7 cumulative schedule for both registered contrast arms | **STALE / BLOCKED** on final D-122 membership and timings. |
| G-15 | line 323, midpoint-reference point | U7 cumulative schedule | **BLOCKED** on G-14. |
| G-16 | line 324, second-half contrast point | U7 cumulative schedule for both registered contrast arms | **STALE / BLOCKED** on final D-122 membership and timings. |
| G-17 | line 325, three end-reference point | U7 cumulative schedule | **BLOCKED** on G-16. |
| G-18 | line 326, post-calibration/bracket-closure point | U7 cumulative schedule | **BLOCKED** on G-17. |
| G-19 | line 327, `measurement_complete` point | U7 cumulative schedule plus launcher terminal event | **BLOCKED** on G-18 and final launch-recipe verification. |

## Authority conflicts found during the census

1. The packet’s Night 3 body says “decode only” and says not to add a
   prefill contrast. D-122, ratified later, requires a prospectively frozen
   256-token prefill arm on GAMMA. **D-122 controls.** G-01, G-03, G-06,
   G-08, G-09, G-14, and G-16 therefore remain stale until U7 is regenerated
   and the packet is refreshed by its owner.
2. The packet’s older hard-gate line lists the U2 successor engine before
   night 1. T1 and D-126 move the frozen U2 cold gate post-window and state
   that the issued D-079 artifact governs ALPHA/BETA/GAMMA. **T1 and D-126
   control.** U2 supplies none of the 56 fill cells in this census.

## Freeze closure check

The lead should rerun the exact census command after filling the packet and
require **zero actionable fill cells**. The three explanatory mentions may
remain only if the HOLD prose is still true; otherwise rewrite those
sentences as ordinary prose and require zero total matches. Independently
check that the final GAMMA pack and duration include D-122, that every count
uses the post-recovery receipt model, and that A-04/B-04/G-06 are reproduced
from the frozen timing ledger rather than copied from the header estimates.
