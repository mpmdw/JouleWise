# ALIGN v4 D/C/T series: Sol and Opus agreement report

**2026-11-08. Written by the Opus seat after its own build was committed and
pushed. This follows RUN_STATE 220: two independent builds, an agreement
report, then a lead ruling. Under the window design council, Opus has the
final say on window design.** The report recommends; the lead rules.

| Build | Branch | Commit | Report |
|---|---|---|---|
| Opus | `align/2026-11-08-dct-series-opus` | `b45579446` | `docs/align/v4/DCT-SERIES-opus.md` |
| Sol | `align/2026-11-08-dct-series-sol` | `75be90bb1` (implementation `e38ab94f3`) | `docs/align/v4/DCT-SERIES-sol.md`, `docs/run_reports/2026-11-08-dct-series-sol.md` |

Both start from `origin/align/2026-11-08-v4-r11` @ `05b6d04cb`. The Opus build
was committed and pushed (`b45579446`) before the Sol branch was fetched or read.

## Where the builds agree without being coordinated

- **Route.** Both use one production route for every window: `align_v4_session
  prepare --window…` → shared `bytes_h_session` view and plan writer → `install`
  (R12 triage, then a series binding) → shared installer → HAZARD_PACK
  `run_night`. Neither adds a D-specific launcher or any v5 runtime dependency,
  and W1 keeps its kit and route.
- **Window shape.** Every C/T window has the same D shape:
  - 22 members, midpoint after ordinal 11;
  - byte-identical original anchors at ordinals 1–4;
  - early and late sentinels at 5 and 22, both replaying W1 ordinal 5;
  - 7 benign and 1 sabotage per pair;
  - the member-5 capture/consume window reference;
  - every D setting copied from W1.
- **Sizing.** 40,527 s programmed, 58,260 s maximum (under 59,520), pilot-3 disk law.
- **Fixed 8.** Calibration is exactly 8 counted windows through
  `v4_cadence.calibration_stop`.
  - A zero-capture attempt re-arms the same slot.
  - Two consecutive zero-capture attempts hold for the lead.
  - A captured but lost window counts and is never replaced.
  - Tests arm only on `calibration_complete`.
- **Packets.** The R12 packet is built off the MBP from an ordered attempt
  history. The arm re-derives it and refuses packets that skip windows, reorder
  them, carry the wrong role, carry hand-edited counts, or come from another
  manifest. The full desk must pass after W1.
- **Test windows are v4, not v5.** v4 test windows have the ordinary D shape,
  with no v5 attacks or physical controls.
- **Not certified by either build.** Neither certifies U3, the B bar, U4–U6 or a
  scorer. The +2-sentinel variant (61,860 s, over the ceiling) is held by both,
  not built.
- **Batching.** Measured members stay batch-1. Neither build finds unmeasured
  inference inside the v4 series.

## Differences and recommended rulings

| # | Topic | Opus | Sol | Recommended ruling |
|---|---|---|---|---|
| A1 | **D1–D3 mapping** | D_k ≡ C_k (aliases). The series is W1 + 8 C + 3 T = 11 windows. | Default: three separate fit windows D1–D3 (seeds 101–121), then C1–C8; 14 windows. Alias mode is also supported. | **Alias (D_k ≡ C_k).** B3 gives C1–C8 the D shape and forbids repurposing windows. Amendment 1's D1–D3 were held-out calibration windows, and U4 is evaluable at D3. Separate fit windows cost about 35.3–36.0 MBP h and have no admitted scorer that needs them. If the R14 scorer ruling later requires fit support, fund it then as a separate prospective block. |
| A2 | **Seed allocation** | Distinct index per fresh member, consumed per pair in kit order from 2, skipping 1 and 91–99. C uses 2–65, T uses 66–89. | Each window uses a 7-index block per pair; the sabotage member **reuses the block's first index**, so it has the same episode seed as one benign member. C uses 2–57, fit 101–121, T 201–221. | **Opus allocation.** The protocol text says held-out seeds are "consumed in kit order by window order". Sol's within-window condition reuse gives a benign and a sabotage trajectory the same sampler stream (the condition is not a seed input). That correlates sampling noise between a calibrator and a known-H member, and gains nothing because v4 claims no common-random-number pairing. |
| A3 | **Order within a window** | Pairs alternate member by member, and the first pair alternates by window (odd windows spam first). Sabotage sits at ordinals 9 and 18, one per half. | Benign at 6–19 alternating, always spam first; sabotage at 20–21. | **Opus order.** Amendment 1 A2 says "pair order alternating … and sabotage spread across the window". Sol follows the older v5-series sheet. Spreading sabotage avoids putting both sabotage members back to back at the end of the window, so their thermal predecessor state matches the calibrators'. |
| A4 | **Number of test windows** | Three (recommended). The six-window alternative is coded as one-pair 14-member windows, which give the same per-pair test units. | Recommends six two-pair windows (42 benign per pair against 21). | **Three.** Neither 21 nor 42 benign per pair can verify a 2.5 % FPR: with 0 alarms observed, the 95 % upper bound is about 13 % at 21 and about 7 % at 42. The v4 test is a gross-failure check on a threshold that is conditional on exchangeability. The extra three windows (about 35 h) buy more from v5 development. If the lead wants the 7 %-class bound, take Sol's six two-pair windows, not Opus's one-pair variant. |
| A5 | **RUN_STATE 216 fence** ("from window 6, pending eligibility blocks the next arm") | Not enforced; protocol V allows provisional counts through C7. | Enforced from C6. | **Enforce it (Sol).** RUN_STATE 216 is an explicit lead text that 217 did not withdraw. It costs nothing in practice, because the R12 `member_eligibility` check already requires the previous window's final adjudication before every arm. Record the disposition in the protocol. |
| A6 | **Series admission** | The manifest, generator and `v4_series.py` are bound through the W1 registration receipt artifact set. | Separate `series/admission.json`: lead-signed, with evidence locators (`scorer_fit_contract`, `seed_allocation`, `r13_r14_gate`, `paired_build_agreement`, `w1_clearance`). | **Both.** Keep the receipt binding (the series is part of the registration) and add Sol's admission file as the series-specific lead sign-off. |
| A7 | **Threshold freeze before T1** | Missing. | `test_threshold_freeze` locator binding the sha256 of the exact 8 final calibration rows, rechecked at every T arm. | **Adopt Sol's.** It is a real gap in the Opus build: thresholds must not follow later C counts. |
| A8 | **Packet evidence** | Each pass/fail/deferred check needs a sha256, written into the basis. The packet carries the whole ledger, and the arm recomputes `plan_next`. | JSON locators with a pointer whose value must equal the status. The source bytes are embedded (`content_utf8`) and rechecked, so the packet is portable to the MBP. | **Adopt Sol's locator embedding.** It authenticates more than a bare digest. Keep the ledger recomputation; both builds already re-derive the cadence. |
| A9 | **Shared measurement-view identity bug** | Not found. The Opus e2e ran `measurement_view` and passed silently. | Found and fixed: `bytes_h_session.measurement_view` projected every ALIGN D config as `neg8_reference-<run>`, because the BYTES roster has no D. The fix derives the unit from the frozen `align-model=` tag. | **Adopt Sol's fix.** It also affects **W1** (the same view code), so it is a W1 pre-registration fix, not only a series fix. It needs one independent review because `bytes_h_session` is shared BYTES code. |
| A10 | **End-to-end depth** | Real `arm_checks`, triage, binding and `measurement_view`. Synthetic seams: the plan writer, the installer and `run_night`. 12 armed windows plus 7 refusal scenarios, 13 s. | Real session prepare/install, plan writer, generated zsh chain and HAZARD_PACK driver for all 15 windows. Process census and launchd are synthetic. | **Sol's replay is the stronger route proof.** Keep Opus's refusal scenarios (deferred desk, wrong window, unbound packet, escalation, pending and insufficient calibration, alias) as cheap unit-level tests. Both stay synthetic; the native smoke (RUN_STATE 221 rule 3) is still owed. |
| A11 | **Committed kits** | All 11 window kits are generated and committed (3.3 MB). `--check` shows no drift. | Materialized per window when needed. Only the manifest is committed. | **Sol's model, plus one condition:** before each arm, commit the next two windows' kits at the final head, so readiness rule 221-1 can check them. Committing all of them now only adds churn until R1 fills the inputs. |
| A12 | **Desk** | The window is labelled. The U3/WP19/soak evidence comes from the W1 registration. A provisional `series_ledger_row` is computed, and a U1–U3 FAIL sets that window's calibrators to zero. | Window-labelled desk with separate pools and later-window sentinel diagnostics. Counts are never inferred as final from the desk. | **Merge the two.** Take Sol's desk structure and add Opus's explicit "U1–U3 FAIL bars pool entry" counting rule as a lead-confirmed rule (Opus R-8). |
| A13 | **Final adjudication** | May lower provisional counts, never raise them without a lead ruling. | Takes counts from the adjudication record as given. | **Opus rule.** |
| A14 | **Sentinel alternate** (seed-93 bank/benign) | Not built. Regenerate the manifest before C1 if needed. | Not built; held. | Same in both. If W1's desk rejects ordinal 5, regenerate prospectively before C1. |

## Recommended integration

**Use the Sol branch as the code base.** It goes deeper through production code,
and it has the admission file, the threshold freeze, embedded evidence and the
identity fix. Change its allocation to Opus's: alias mapping, distinct seeds in
kit order, and the Amendment 1 within-window order (A1–A3). Port Opus's
refusal-scenario tests and the desk counting rules (A12–A13). Keep the RUN_STATE
216 fence (A5) and three test windows (A4).

The allocation changes alter the manifest bytes, so the merged manifest needs
one more paired check before the lead signs it: each seat independently
recomputes the seeds and order from the ruling text. The A9 identity fix also
needs a W1-side review.

## Lead decisions to take from this report

1. D1–D3 ≡ C1–C3 (A1).
2. Seed allocation and within-window order (A2–A3).
3. Three test windows (A4).
4. Keep the C6 fence (A5).
5. The shared view identity fix, for W1 too (A9).
6. Requesting Ed's 61,860 s ceiling for +2-sentinel windows, before C3 closes.

Still open from both reports and not series-specific: U3, the B bar, the R14
scorer and its fit source, the W1 receipt, and R1's W1 plan, which also unlocks
per-window sizing.

## Verification of the Sol build by the Opus seat

The Sol module `tests.align.test_v4_series` was run on the Sol commit in a
separate detached worktree: **10 tests OK, 80.5 s**. The 15-window FakeWorld replay through the plan writer and the HAZARD_PACK driver passed. The Opus modules are listed in
DCT-SERIES-opus.md: `test_v4_series` 24 OK, `test_v4_series_e2e` 8 OK,
`test_v4_series_kit` 6 OK.
