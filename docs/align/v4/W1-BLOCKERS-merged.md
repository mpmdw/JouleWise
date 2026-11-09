# W1 blockers: merged build and U3 export runbook

2026-11-08. This branch, `align/2026-11-08-w1-blockers-merged`, combines:
- `align/2026-11-08-w1-blockers-sol` (`35dccf241`), taken as the base;
- `origin/align/2026-11-08-v4-r11`, merged in (not rebased): first at
  `2cce80ede`, then again at `9891d679b` (delta2: strict receipt, dynamic
  closure, top-up, smoke G1-G3).

It implements the lead's rulings on
[W1-BLOCKERS-AGREEMENT](W1-BLOCKERS-AGREEMENT.md) (on
`align/2026-11-08-w1-blockers-opus`). Two of those rulings changed later: ruling 2
was revised from N = 19 back to N = 16 by RUN_STATE 226 R15 (three test windows),
then prospectively expanded to N = 22 by RUN_STATE 239 R25 (C9-C14 reserves),
and ruling 9 is the lead's modified version. Design background:
[W1-BLOCKERS-sol](W1-BLOCKERS-sol.md) and `W1-BLOCKERS-opus.md` on the Opus branch.
A Sol executing review follows.

## 1. What the merge contains

| Area | Source | Change in this merge |
|---|---|---|
| U3 inputs, custody, gate binding, per-window scope, D fingerprints | Sol | None, apart from the D screen becoming optional (below) |
| U3 arithmetic (`v4_u3.prediction`, OC) | Opus | Ported into Sol's module. The method is now `session_zero_rms_series_exact_v1`. |
| B evidence: journal replay in both desks, signed policy | Sol | Rule renamed `zero_B_auto_resume_v1`. The consequence follows ruling 9. |
| B resume and escalation | New (ruling 9) | Triage row `battery_window`, plus `align_v4_session.full_desk_gate_pass` |
| Top-up evidence (`v4_topup`, `--battery-log`), R12 cadence, receipt tiers, cold fixes | v4-r11 `f993b784f`/`2cce80ede` | Merged unchanged |
| WP22 | Both | Sol's signed synthetic registration and battery journal. The v4 side's pending-U3 registration dir is removed. The v4 side's minimal default-CI dry-run test is kept and updated: the dry run now carries a signed synthetic bar that registration refuses. A pending bar is tested to be inconclusive at the desk, not a crash. |
| Export helper | New | `scripts/align_v4_u3_export.py` |

## 2. U3 as ruled

- **Rulings 3 and 4.** The procedure takes one prespecified 30B pilot pair per
  session (n ≥ 5). From the relative differences r it computes s₀ = √(mean r²),
  the RMS about zero, with df = n.
- **Ruling 2 (revised).** q solves E_U[1−(1−P(|Z|>qU))^N] = β. This is exact
  under the normal model, and it integrates the uncertainty in s₀, which all
  later tests share, once. N = Σ `checks_by_window` = **22**: W1 has 30B:4 and
  D:1; C1-C14 and T1-T3 have D:1 each (RUN_STATE 239 R25, prospective expansion
  from N = 16 before signing).
- **Rulings 1 and 7.** β = .05. It is halved if any pilot |r_i| is more than 3×
  the RMS of the *other* sessions.
  - *Implementation note:* computed against s₀ itself, |r_i|/s₀ can never
    exceed √n. The rule as written would therefore be vacuous for n ≤ 9.
    Leave-one-out keeps its intent. This needs lead confirmation.
- **Rulings 5 and 6.**
  - The 30B margin is q·s₀·Ē. The D margin is 1.5·q·s₀·Ē; f = 1.5 is bound to a
    written justification by digest.
  - R1's adjacent D_spam a/b pair is a screen. It is `not_refuted` iff
    |r_D| ≤ 1.5·q·s₀.
  - A screen that is `refuted` or `missing` leaves the bar valid for 30B. D pairs
    are then inconclusive (`u3_margin`), so the W1 D U3 check fails and the lead
    disposes.
  - Under Sol's original design a failed screen voided the whole bar. That is
    replaced.
- **Ruling 11.** There is one bar for the whole series. The OC block reports D at
  true scale ×1, ×1.5, ×2 and ×3, plus correlation, t₃, skew and drift scenarios.
- `validate_u3` recomputes the prediction, the OC and the derivation digest. It
  requires the lead signature and an independent ADMIT gate whose JSON names
  `derivation_sha256`. At registration, it also binds the export, the
  justification and the gate bytes to the registration commit.

## 3. B as ruled (rulings 8-10, ruling 9 as modified by the lead)

- **Fail condition.** Any member with `battery.member_span` (charging or AC
  loss) or `battery.accumulator_excursion` fails the model-window B bar.
- **Missing evidence** is unavailable. It counts as non-passing but is never a pass.
- **Assist** is disclosed and the member is retained.
- **Consequence.**
  1. The B (or unobserved) members are excluded and every other member is kept.
  2. `v4_B_bar` is false, but `full_desk_gate_pass(checks)` ignores it. That
     function defines what the `full_desk_gate` packet status means.
  3. The next arm waits only for the existing arm-computed `charging_battery`
     check: fresh admissible `v4_topup` evidence from `--battery-log`, plus
     `--obc-off-attested-by`.
- **Escalation.** The triage row `battery_window` controls it:
  - `pass` admits the arm.
  - `fail` with `consecutive_non_pass: 1` becomes `automatic_resume`.
  - `fail` with `consecutive_non_pass` ≥ 2 refuses the arm unless the packet
    carries a `battery_rulings` row with this shape:
    `{ruling_id, text_sha256, after_window: <previous window>, lead_signature}`.
- **R1 → W1** reads `not_applicable` (`first_window_na`).

## 4. Export and signing: exact commands and machines

Use `$J` for a checkout of this branch. The pilot custody paths below are
placeholders that the lead or magistrate fills in. No agent opens them.

| Step | Machine | When | Command |
|---|---|---|---|
| 1. Policy template | Air | now | `python3.13 -B scripts/align_v4_u3_export.py policy-template --output configs/campaigns/align_v4/registration/u3_sources/policy.json` |
| 2. Transfer justification | Air (lead) | now | Write `docs/align/v4/U3-transfer.md`, a one-page source→target note for f = 1.5. Put its sha256 in `policy.json` as `transfer_justification_sha256`. |
| 3. Pilot selection file | Air (lead) | now, before any energy is read | `u3_sources/selection.json`: `{"sessions": [{"session": "p4", "candidates": [{"ordinals": [a, b], "early_bundle": "<path>", "late_bundle": "<path>"}, ...]}, ...]}`. List each session's replay pairs in **design order**. The script takes the first pair ≥3 apart and never substitutes. |
| 4. Pilot export | **MBP magistrate**, in the quiet gap after R1 closes and before W1 arms. Use the Air instead if it already holds verified copies of the pilot 4-10 bundles. Read-only, minutes. | after R1 | `python3.13 -B scripts/align_v4_u3_export.py pilot --selection u3_sources/selection.json --output u3_sources/pilot.json` |
| 5. R1 D screen | Same machine as step 4 | after R1 closes | `python3.13 -B scripts/align_v4_u3_export.py r1 --early-bundle <R1 D_spam a run dir> --late-bundle <R1 D_spam b run dir> --ordinals 2 3 --output u3_sources/r1.json` |
| 6. Fill configuration digests | Air (lead) | after step 5 | In `policy.json`: `r1_configuration_sha256` is the R1 pair's `configuration_sha256` from `r1.json`. `d_configuration_sha256` is the final W1/D configuration fingerprint, identical unless a lead-reviewed change is justified in step 2. |
| 7. Assemble | Air | after step 6 | `python3.13 -B scripts/align_v4_u3_export.py assemble --pilot u3_sources/pilot.json --r1 u3_sources/r1.json --policy u3_sources/policy.json --output u3_sources/pairs.json` |
| 8. Derive (PENDING draft) | Air | after step 7 | `python3.13 -B scripts/align_v4_u3_bar.py --input configs/campaigns/align_v4/registration/u3_sources/pairs.json --supporting-source docs/align/v4/U3-transfer.md --output configs/campaigns/align_v4/registration/u3-draft.json` |
| 9. Independent gate | Air (cross-family reviewer seat) | after step 8 | The reviewer recomputes, then writes `docs/align/v4/U3-gate.json` = `{"verdict": "ADMIT", "derivation_sha256": "<from draft>", ...}`. |
| 10. Adopt and sign | Air (lead) | after step 9 | `python3.13 -B scripts/align_v4_u3_bar.py --adopt-draft configs/campaigns/align_v4/registration/u3-draft.json --gate docs/align/v4/U3-gate.json --lead-signature 'lead: <name> <YYYY-MM-DD>' --output configs/campaigns/align_v4/registration/u3_bar.json` |
| 11. B policy | Air (lead) | now | Edit `registration/battery_window_policy.json` to `status: registered` with `lead_signature`, keeping `rule: zero_B_auto_resume_v1`. |
| 12. Commit and receipt | Air | after steps 10 and 11 | Commit everything above, then regenerate the registration receipt at that commit. It binds `u3_bar.json`, the sources, the gate and the policy. |

Paths under `u3_sources/` are relative to `configs/campaigns/align_v4/registration/`.
Steps 4-5 print counts and unavailable sessions only.

Steps 1-3 and 11 can be done during R1. Steps 4-10 fit in the R1→W1 gap. Only
steps 4-5 touch measurement bundles.

## 5. Verification

The final results are in the commit message: every related module was run one
per process, followed by `JW_WP22_FULL=1 test_v4_w1_synthetic`.
