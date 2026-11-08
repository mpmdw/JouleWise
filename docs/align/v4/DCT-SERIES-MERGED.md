# ALIGN v4 D/C/T series: merged build (RUN_STATE 226 R15)

**Date:** 2026-11-08. **Owner:** Opus seat.

**Branch:** `align/2026-11-08-dct-series-merged`. It contains:
- Sol's code base, `align/2026-11-08-dct-series-sol` @ `75be90bb1`;
- a merge (not a rebase) of `origin/align/2026-11-08-v4-r11` @ `2cce80ede`;
- the R15 changes listed below.

**Status:** PROVISIONAL and non-claim. The manifest bytes changed, so a paired
Sol seed check is due before the lead signs `series/admission.json`.

**Inputs:** the paired builds and their agreement report,
[DCT-SERIES-AGREEMENT.md](DCT-SERIES-AGREEMENT.md). The independent build
records are [DCT-SERIES-sol.md](DCT-SERIES-sol.md) and
[DCT-SERIES-opus.md](DCT-SERIES-opus.md); both are superseded for use.

## What R15 changed relative to the Sol build

| R15 item | Implementation |
|---|---|
| D_k ≡ C_k, no separate fit windows | `candidate()` produces W1, C1–C8 and T1–T3. Aliases D1–D8 map to C1–C8. The `separate_fit` option is removed. |
| Distinct held-out seeds in kit order | Per pair, starting at 2 and skipping 1 and 91–99. C uses 2–65 and T uses 66–89. Sol's reuse of a benign seed for sabotage is removed. |
| Sabotage at ordinals 9 and 18; Amendment 1 order | Pairs alternate member by member. Odd windows start with spam, even windows with bank. |
| Three test windows | Fixed (`TEST_WINDOWS = 3`). Tests have the D shape and no v5 content. |
| Keep the C6 fence | Sol's check is unchanged. |
| A U1–U3 fail bars the window from the pool, but the window still counts toward 8 | `align_v4_series.desk_row`. The window desk report now carries `series_desk_row`. |
| Final adjudication may lower counts, never raise them | A history attempt may carry `desk_eligible_benign`. A final count above it refuses. |
| C-window sabotage counts toward nothing | Pool `known_h`, `counts_toward: none`. Its DC rows stay sealed through the existing `km003c.seal_non_benign`. |
| D members sized at the largest W1 D member time | `member_seconds()` reads it from the committed W1 plan. Before R1 the planning allowances are used and flagged `sizing.planning_allowances_pending_r1_w1_plan`. |
| Series binding on the W1 arm too | `_arm_and_install` calls `bind_packet` on every arm and records `series_binding` in the arm record. An unbound W1 packet refuses before the installer runs. |
| `lead_release` resume | A history entry `{"lead_release": {ruling_id, text_sha256, resets: zero_capture_escalation, after_window: <last attempt id>, lead_signature}}` clears an escalation. It is valid only right after two consecutive zero-capture attempts and only if it names the last one. Releases that follow a calibration attempt go into the packet's `lead_rulings`, which `v4_cadence.calibration_stop` already consumes. |
| 62,400 s ceiling for windows with the two extra sentinels | `window_ceiling_s(extra_sentinels)` returns 59,520 s, or 62,400 s with 2 extra sentinels. `derive_sizing` refuses a window above its ceiling. The +2 window is 61,860 s, which fits. **The placement of the two escalation sentinels is not ruled and not built.** |
| `measurement_view` `neg8_reference` bug | Sol's fix in `bytes_h_session.measurement_view` takes the unit from the frozen `align-model=` tag. `tests/align/test_measurement_view_identity.py` covers both the **W1** path and a series window. It was red on the pre-fix code (W1 D projected as `neg8_reference-align-v4-episodes-a-e05`) and is green now. |

## Merge with the v4-r11 head

The v4-r11 head added:
- the battery log in place of hand-entered top-up times;
- an arm-derived artifact-set and `record_commit` identity;
- the meter rows `meter_reader_live` and the non-gating `meter_coverage`;
- `lead_rulings` in `calibration_stop`.

The series producer and binding now follow that head:
- `make_packet` takes `record_commit` and `last_desk_passed_artifact_set_sha256`.
- It no longer writes `code_or_config_changed`. The arm derives that flag and the W1 flag.
- It pre-checks the packet with the arm's identity derivation.
- `previous_window` is the window id, not the attempt id, as the head's id regex requires.

The one textual conflict, in `align_v4_session.py`, was resolved by keeping both
sides. The new artifacts `scripts/align_v4_series.py` and
`configs/campaigns/align_v4/series/series_manifest.json` are now bound in
`v4_registration.ARTIFACTS` and the receipt template. W1 install fixtures in
`test_v4_kit` and `test_r1_round6_power` now carry the committed manifest and a
W1-bound packet.

## Manifest

- **File:** `configs/campaigns/align_v4/series/series_manifest.json`.
- **Canonical sha256** (compact sorted JSON): `01e2363d1d45e3593def99e538761bd8424fdd962faa12576559733a11964672`.
- **File-byte sha256:** `eba6fb0732ec26996a0c63bb679a899b71dc2009474502e59048dd67d764f0c7`.
- **Cross-check:** for all 242 C/T member slots, (pair, condition, seed index,
  episode seed, model) is identical to the Opus build's independent manifest
  (`align/2026-11-08-dct-series-opus` @ `b45579446`).

## Verification

Synthetic tests only, one module per process.

- **`test_v4_series`:** 16 tests, including Sol's HAZARD_PACK replay, now 12 windows (W1, C1–C8, T1–T3).
  - The replay runs through the real session prepare/install, the plan writer, the rendered zsh chain and `run_night` HAZARD_PACK.
  - Every window reaches EXIT_GO with its bundles present. About 60 s.
- **`test_v4_series_e2e`:** 9 tests, the Opus cadence scenarios ported.
  - The full series armed W1-a1, C1-a1, C2-a1, C3-a1, C3-a2 (after a zero-capture attempt), C4-a1 … C8-a1, T1-a1 … T3-a1.
  - The C1–C8 totals are 54 spam / 56 bank, which reaches calibration_complete.
  - Refused before the installer: a deferred desk after W1, a packet for the wrong window, unbound W1 and C1 packets, an escalation (which arms after a `lead_release`), pending C8 before T1, insufficient calibration, and the C6 fence. The D1 alias resolves to C1 and the desk routes the window kit. About 27 s.
- **`test_measurement_view_identity`:** 3 tests.
- **Regressions:** the W1 and registration modules are listed in the commit report.

## Still open

- The paired seed check of the manifest bytes.
- The placement of the two escalation sentinels.
- R15 text in `pilot_protocol_v4.md`. The protocol lives on v4-r11, where another fixer is active, so the text lands there.
- The existing W1 blockers (R14).
- The ≤45-minute native smoke before the first long C window.
