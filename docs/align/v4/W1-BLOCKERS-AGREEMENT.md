# W1 blockers: Sol and Opus agreement, with the recommended ruling

2026-11-08. This is the agreement step under RUN_STATE 220-221 for the two
independent builds of the W1 blockers. Opus has final say under the window
design council. The lead issues the ruling item.

| Build | Branch | Commit | Base |
|---|---|---|---|
| Opus | `align/2026-11-08-w1-blockers-opus` | `3fdf937b6` | `05b6d04cb` |
| Sol | `align/2026-11-08-w1-blockers-sol` | `40db1c675` + report `5b3ee603c`/`35dccf241` | `05b6d04cb` |

The Opus build was committed and pushed before this report read the Sol branch.
Both branches sit on `05b6d04cb`, and `align/2026-11-08-v4-r11` has since moved
to `2cce80ede`, so the carried branch needs a rebase.

## 1. Where the builds agree

| Point | Both builds |
|---|---|
| No installed constant | No k=3, 2.576 or J floor. The bar is a function of a lead-exported input plus lead-frozen parameters. |
| Unit | Relative replay difference (E_late − E_early)/mean of turn-owned GPU J. The pair margin is bar × pair-mean energy. |
| Derivation records | Separated-ordinal (≥3), within-session, token-identical **30B pilot 4-10** replays. |
| R1 D pair | Adjacent, so it is **not** derivation evidence. It is a transfer screen that can refute but never qualifies D. Both builds found this independently. |
| W1 records | Never inputs. W1 5/17 and the contrast pairs are the bar's first prospective tests. |
| Series sizing | **N = 16 comparisons**: W1 4×30B + 1×D, plus C1-C8 and T1-T3 at one D pair each. Series budget **.05**. The roster was reached independently. |
| Admission | `validate_u3` recomputes the derivation and OC from the embedded inputs, then requires a lead signature and an independent ADMIT gate. Pending, v1, k=3 and edited bars refuse, and so do synthetic bars at registration. |
| OC findings | Under the model, both builds report the following: nominal is controlled; **heavy tails** inflate series false-fail (Opus t₄ about 20%; Sol t₃ about 5%, under a more conservative bar); a **D scale above the assumed one** is the dominant risk (Opus ×1.5 → 24-43%, Sol ×2 its factor → 23%); power against D drift is weak at small n. |
| Battery arm | `battery_arm` and the 1,800 s top-up rule are unchanged. MED-3 (which evidence counts as a top-up completion) stays a separate lead item. |
| Battery window | Missing or unobserved battery evidence is **unavailable, never a pass**. An empty report cannot pass. Discharge on AC (assist) is disclosed and retained for the GPU endpoint and gates nothing. The registered GPU residual and the SECONDARY DC-in are unchanged. |
| WP22 | Both builds clear the same harness defects: (a) stale contrast fit, (b) U3 stop; then synthetic R1 X-G turns made consistent with the re-measured pilot-7 count, manifest `delta_slow_c`/stage, and the oracle moved to chair 9 (delivery + stage, df=3). `JW_WP22_FULL=1 test_v4_w1_synthetic` passes on both: Opus 18 OK, Sol 19 OK, each with the one expected failure (F3). |

## 2. Where they differ

| # | Question | Opus | Sol | Recommended ruling |
|---|---|---|---|---|
| D1 | **Pilot pair selection** | All eligible pairs. Within-session dependence is handled only as an OC sensitivity (ρ=.3: 5.6% vs 5%). | **One prespecified pair per independent session**. The selection rule is frozen before energies are opened, with no best-pair substitution. | **Sol.** Independence of the calibration units is an assumption the Opus estimator relies on and cannot check at small n. One pair per session removes it. |
| D2 | **Scale and centre** | RMS about zero, df=n. Drift inflates the scale. | Sample SD (df=n−1) plus \|mean\| added to the half-width. | **Opus.** Both refuse to credit drift. Adding \|μ\| on top of a t half-width double-counts it, and costs a degree of freedom. |
| D3 | **Series calibration** | Exact: solve E_U[1−(1−P(\|Z\|>qU))^N]=β, so the shared ŝ uncertainty is integrated once. | Bonferroni a=α/N per test, with a predictive t factor √(1+1/n). | **Opus.** Both control the series rate under the model; Opus at equality, Sol as a bound. At n=7 and N=16, Opus gives 4.09·RMS (about 3.8·s), and Sol gives 5.09·s+\|μ\|. Sol's bar is about 1.35× wider on 30B. Sol's nominal series rate was 0.4% against a 5% budget, which buys no protection the model does not already give and costs power U3 cannot spare. |
| D4 | **D transfer** | D is in scope iff R1's pair does not refute at factor 1. Factor >1 is not representable. | A lead-justified finite factor f≥1: q_D = f·q_30B, with the R1 screen at q_D. Source and target fingerprints plus a hashed justification are required. | **Sol's mechanism**, with Opus calibration: solve q at the nominal scale for all N tests, then D margin = f·q·s₀. Recommend **f = 1.5**, with a written justification. Report OC at a true D/30B scale of ×1, ×1.5, ×2 and ×3. f=2 at this n makes the D bar about 2.7× the Opus f=1 bar, and U3 for D becomes nearly vacuous. |
| D5 | **Gate binding** | Gate = {verdict, path, sha256 of report bytes}. With root, the report bytes are checked. | The gate JSON must contain the exact `derivation_sha256`. Export, justification and gate are bound to working bytes and the registration commit. | **Sol.** It is a strictly stronger binding. |
| D6 | **Comparison scope** | N is a scalar. | `checks_by_window` per population. The desk refuses U3 when actual comparisons exceed the frozen count or a window is absent. | **Sol.** It enforces N instead of assuming it. |
| D7 | **B tolerance** | B+possible-B ≤1 passes, B≥2 fails. This is a parity argument with U1. | Zero B: any charging, AC-loss or accumulator-excursion member fails. | **Sol: zero B.** LEAD-RULINGS-2 R02 and DEVIATIONS withdrew the earlier builder ≤1 bar. The arm rule is designed to start in float, so any in-span charging means the procedure failed. Count `battery.accumulator_excursion` as B (Sol). Opus counted it as only possible-B. |
| D8 | **B consequence** | B members excluded; **non-B members kept**. The desk fails `v4_B_bar`, and the next arm waits for a fresh top-up, OBC attestation and a lead disposition. | **No pool entry from that model-window**; remedy and adjudicate before the next arm. | **Opus.** v4's endpoint is GPU energy under direct thermal gating (U1/U2), and charging inside member k does not invalidate member j's own span, which read clean. A whole-window pool loss per charging event would spend R13's single-window margin on members not shown to be affected. The operational stop keeps the procedure honest. |
| D9 | **B evidence path** | The session desk reads harvest exclusion codes and requires `exclusions.json` (`battery_evaluated`). The standalone desk has none, so the result is unavailable. | Both desks replay the existing `battery_join` on the closed `hazards/monitor/battery.jsonl` over `member_spans`, with digests. The standalone manifest names the journal. | **Sol.** It works in both desks, records source digests, and reuses the frozen join without trusting a downstream code list. |
| D10 | **Who installs the B rule** | The rule is a code constant (`B_WINDOW_TOLERANCE=1`) and protocol text, labelled "binding only once ruled". | A signed `battery_window_policy.json`. Unsigned or PENDING gives an inconclusive result and a false session check. | **Sol.** DEVIATIONS says "no pass is manufactured from an unruled bar"; a lead-signed policy satisfies that literally. |
| D11 | **Module layout** | Inside `v4_registration.py`. | New `v4_u3.py` and `v4_battery.py`, bound by the receipt. | **Sol.** Smaller modules, and its receipt and closure binding are already done. |
| D12 | **WP22 extras** | — | Fake MLX versions are labelled synthetic, so the D cohort-identity check is actually exercised. | **Sol.** |

## 3. Recommended ruling (Opus final say)

1. **Carry the Sol branch forward** (`align/2026-11-08-w1-blockers-sol`), rebased
   onto the current `align/2026-11-08-v4-r11`. It provides the custody, scope and
   battery evidence path (D5, D6, D9-D12). Do not merge the Opus branch; keep it
   as the record of the independent build.
2. **Port the Opus bar arithmetic into Sol's `v4_u3.prediction` and OC** (D2,
   D3, D4 calibration). Keep Sol's selection, policy and fingerprint inputs.
   - Set s₀ = RMS about zero over the selected pairs, with df = n.
   - Solve q exactly for the series budget at N = Σ`checks_by_window`.
   - Set the 30B margin to q·s₀·Ē and the D margin to f·q·s₀·Ē.
   - Screen R1 against f·q·s₀.
   - Bump the procedure id. Add the Opus quadrature tests (the t-tail
     identity, and the series equality at β), and OC rows at true D scale
     ×1, ×1.5, ×2 and ×3.
   - The change is about 30 lines plus tests. Opus re-runs this
     agreement's checks on the result: one cross-family executing review, not
     a new paired build.
3. **Battery:** Sol's signed policy, with the rule **zero B** (accumulator
   excursion counts as B) and the **Opus consequence** (D8): B members
   excluded, non-B kept, desk `v4_B_bar` false, next arm blocked until a fresh
   completed top-up, OBC attestation and a lead disposition are recorded. Edit
   Sol's policy proposal text and the protocol §4 wording to match.
4. **Protocol and deviation log.** Replace the Opus protocol edits with Sol's
   §4/§5 text as amended by items 2-3. Add one DEVIATIONS entry citing this
   ruling, stating the U3 procedure id and the B rule.
5. **Before W1 arms** (both builds agree these are real prerequisites, not
   guards to relax), the lead:
   - freezes the parameters;
   - exports one prespecified pilot pair per session and R1's D_spam a/b screen;
   - writes the D transfer justification;
   - obtains the independent gate (JSON with `derivation_sha256`);
   - signs `u3_bar.json` and `battery_window_policy.json`.

   All of this is Air work during R1. Only the R1 screen input waits for R1 to close.

## 4. Lead statistics rulings needed

| # | Ruling | Recommendation |
|---|---|---|
| L1 | Series budget β for U3 | **.05**, within the chair's ≤.15 joint U1-U5 budget (Sol's bound) |
| L2 | Comparison roster N, per window and population | **16**: W1 30B:4 and D:1; C1-C8 D:1; T1-T3 D:1. Re-derive only if the final C/T manifest changes **before** any U3 is read. |
| L3 | Pilot selection rule | One pair per session, prespecified by design position before energies are opened, e.g. the session's designed late replay of its earliest eligible member. Minimum 5 sessions. If the selected pair is ineligible, the session is unavailable, never substituted. |
| L4 | Estimator | Zero-centred RMS with exact series quantile (§3 item 2) |
| L5 | Relative vs additive-plus-relative law | **Relative only.** An absolute floor cannot be estimated from n≈7 and would be an installed constant. |
| L6 | D transfer factor f and its justification | **f = 1.5**, with a written source→target note covering quantization, sampler, budget and G0 cap differences. R1 screen at f·q·s₀. A failed or missing screen makes D U3 inconclusive: W1 desk fails and the lead disposes, with no fallback. Disclose "transfer-limited" in the paper. |
| L7 | Heavy-tail handling | Normal model primary, with the t₃/t₄ OC rows in the registration OC table. If any selected pilot \|r\|/s₀ > 3, halve β before signing. Fix this rule now, blind to outcome. |
| L8 | B tolerance | **Zero B**, with accumulator excursion counted as B |
| L9 | B consequence | **Operational stop, no pool loss** (D8) |
| L10 | Assist | Disclose and retain; print-only in v4 |
| L11 | One bar for the whole series | Yes: never re-derived from windows it judges |

## 5. Not in scope of either build (still blocks W1)

- the signed registration receipt with Stage A/B;
- the native WP19 receipt;
- the R1 backfills;
- the triage producer;
- the offload freshness policy;
- the top-up evidence definition (MED-3);
- the U5 consequence;
- native smoke.

Two failures exist at base `05b6d04cb` and are unchanged by the Opus build:
`test_v4_prequal.test_real_launcher_keeps_the_venv` and
`test_v4_powermode_record.test_desk_check_passes_only_when_every_bundle_matches`.
Sol's report did not run those two modules.
