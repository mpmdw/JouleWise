# Cold review: W1 kit lane for lead ruling R10 (`lane/2026-11-07-w1-kit-r10`)

- **Reviewed:** `lane/2026-11-07-w1-kit-r10@05bdff797` against `lane/2026-11-06-v4-r1-integrated@e901eb2a4` (10 commits, 18 files, +1,436/-69).
- **Reviewer:** an Opus 5.5 sub-agent of the laptop lead. This is a cold pass: the only context was the documents named below.
- **Read:** `RUN_STATE.md` item 203 (`origin/main`); LEAD-RULINGS-2 Round 10 (on the branch); the research audit `docs/research-audits/2026-11-07/w1-budget-fallback.md` (`origin/research/2026-11-07-w1-budget-fallback@93b049612`, §3 D, §5 and §6); CHAIR 1(e)/1(f) as quoted there; `docs/align/pilot_protocol_v4.md`; the full code diff. I also read the runtime paths the diff depends on: `thermal_gates.ThermalSession` G0 wait, `workload.py` g0_unreleased stop, `r1_runtime.k_x_g` and `episode_phases`.
- **Verdict: ADMIT_WITH_FIXES.** There are no BLOCKER or HIGH findings.
  - Under a receipt, no admitted W1 night breaks 1(f), and no forged, stale or mismatched receipt passes the numeric binding.
  - The procedure reads no energy, U5, β_T, MDE or thermometry field.
  - Two MEDIUM findings should be closed before any W1 arm. MEDIUM-1 is a one-condition kit fix. MEDIUM-2 needs a lead ratification line and a doc correction.

## Tests run

All runs used `/private/tmp/jwsol/venv-both/bin/python -B -P` under `nice -n 19 taskpolicy -b`, one module per process and at most two at once, with `PYTHONPATH` set to the worktree. The R1 rehearsal tests pin their own clock (`_now_local` = `NOON_SAFE`). My adversarial tests never reach the batch-window wait.

| Module | Result |
|---|---|
| `tests.align.test_w1_kit_r10` | 24 tests, OK |
| `tests.align.test_v4_kit` | 116 tests, OK |
| `tests.align.test_thermal_gate` | 44 tests, OK |
| `tests.align.test_r1_rehearsal` | 73 tests, OK |
| `tests.align.test_v4_w1_synthetic` (`JW_WP22_FULL=1`) | 18 tests, OK (1 expected failure, the existing WP22 F3) |

**Adversarial tests (not committed).** There are seven tests, all on synthetic R1 records:
- `CurrentRuleFitsButReceiptAdmits`: confirms MEDIUM-1.
- `NoReceiptBehaviourChanged`: confirms MEDIUM-2.
- `SignatureWhitespace`: confirms LOW-1.
- `ReceiptFreeTextNotBound`: confirms LOW-2.
- `BlindingProbe`: confirms LOW-3. It poisons every level, nested `phases_s` included, and hooks `__deepcopy__` and `items`.
- `ZeroDecodeGatedRuns`: confirms LOW-4.
- `FloorArithmeticProperty`: 300 random 8-bit records (I_D 250-560 s, tail 0-60 s, r 10.5-14 tok/s, one gated run slightly slower than step-d). It checks:
  - G0\* against an independent recomputation, to 1e-9;
  - the branch-(a) predicate;
  - that every admitted receipt has G0 term = floor(G0\*) and worst ≤ T_dead at B_D 6,144.

  61 of the 300 records took branch (a), and all of them held.

## Findings

### MEDIUM-1: the kit admits a branch-(a) receipt when the 600 s rule already fits (contradicts protocol v4 and R10-2's order)

- **Where:** `scripts/align_v4_kit.py:676-680` (`r10_2_derivation`), and `:756` (`verify_ruling_1f_receipt`, which accepts any derived branch `a`).
- **What happens.** `r10_2_derivation` returns `current` only when floor(G0\*) ≥ 600 s. G0\* projects holds per token to 10,240, but the no-receipt rule uses the *recorded* max(G1 + H). So a record can satisfy both of these at once:
  - the current rule fits at B_D = 6,144 (`max_fitting_b_d` ≥ 6,144);
  - floor(G0\*) < 600 s, so the derivation says (a).
- **Why that matters.** Protocol v4, as this branch amends it (`docs/align/pilot_protocol_v4.md:381`), says R10-2(a) "applies only when … the 600 s rule does not fit". R10-2 orders (a) after the current rule. `decide` gets this right (it returns CURRENT-RULE first), but the kit is the gate, and it admits a signed (a) receipt over such a record.
- **Reproduction.** I_D 400 s, tail 20 s (T_dead 1,188.97 s). Each gated run has G1 + H = 30 s and prefill + tool = 36 s, and decodes 2,200 tokens in 100 s (22 tok/s). The current rule fits at 6,144 tokens: 600 + 30 + 36 + 465.5 = 1,131.5 s. The projected holds are 139.6 s, so G0\* = 547.9 s. `decide` says CURRENT-RULE, yet `require_ready(..., receipt=<signed (a) receipt>)` admits with D armed at 547 s.
- **Impact.** 1(f) still holds, because the term is the armed cap. But the kit lets a public deviation be applied, with a sub-600 s D cap and more X2s, when the pre-declared order says none is needed.
- **Fix (one condition).** In `r10_2_derivation`, return `current` whenever `max_fitting_b_d(r1_slots, t_dead)` is not None. Or have `verify_ruling_1f_receipt` refuse in that case. Then extend `test_receipt_is_refused_where_the_current_rule_already_fits` with this record. The existing test only covers G0\* ≥ 600.

### MEDIUM-2: the no-receipt W1 path changed, and the branch's own record says it did not

- **Where:**
  - `scripts/align_v4_kit.py:555-556` (`ruling_1f_fit`) and `:815-819` (`check_r1_budget_and_policy`): D's G0 term and armed cap are now `w1_d_g0_cap`, the gated D waits only;
  - `:829-832`: the contrast proof is unconditional;
  - LEAD-RULINGS-2 `:772`: "No receipt. The kit behaves as before".
- **What changed.** On `e901eb2a4`, the no-receipt 1(f) G0 term and D's armed `g0_cap_s` were R7-2's G0_cap_W1, taken over D_bank, D_spam a, D_spam b **and X-G**. They are now D-only. My test case has D waits of 120 s and an X-G wait of 560 s, with the X-G contrast episode at 326 s, so the contrast fits. At 20 tok/s with no receipt:
  - this branch admits: worst 1,178.0 s ≤ T_dead 1,189.0 s, with a G0 term of 600 s;
  - the e901 rule refuses: worst 1,278.0 s, with a G0 term of 700 s.

  In the other direction, an INCONCLUSIVE X-G now refuses W1 even without a receipt.
- **What it does not break.** It is not a 1(f) break: D's term is still the cap D arms.
- **Why it still needs a ruling.**
  - Brief item (d) asked for no-receipt behaviour to be unchanged, and LEAD-RULINGS-2 says it is.
  - The only no-receipt guard test (`test_without_a_receipt_1f_still_refuses_unconditionally`) checks one direction only.
  - R10-4 does name "separate D and contrast G0 caps", so the change is arguably in scope. But the lead's rulings on the builder decisions covered (i)-(v) and (a)-(c). They never ratified dropping X-G from D's no-receipt term, which R7-2 defines explicitly. Ruling (iv) is worded "under R10-2(a)", while the code applies it to every W1.
  - The practical exposure: four of W1's six D members (ordinals 8, 11, 14 and 17) follow a contrast member, and they now arm a cap derived from D-after-D waits only.
- **Fix.** Pick one:
  - **(a)** The lead records in LEAD-RULINGS-2 that R10-4's per-role caps and (iv)'s unconditional contrast proof apply to every W1, receipt or not, as a deviation from R7-2's G0_cap_W1 for the D term. Then correct `:772` and add a test that pins the new no-receipt behaviour.
  - **(b)** Keep R7-2's combined cap as the D term when there is no receipt.

### LOW-1: the signature check accepts any non-empty string, including a disguised "PENDING"

- **Where:** `scripts/align_v4_kit.py:740`; `scripts/align_w1_budget_procedure.py:168`.
- **What happens.** `signature.startswith(UNSIGNED)` runs on the unstripped string. `' PENDING_LEAD_SIGNATURE: …'` and `'pending_lead_signature'` are both admitted by the kit, and so is `'x'`.
- **How serious.** The receipt's authenticity rests on git custody; the signature line is a form, not a cryptographic check, and no numeric forgery passes the re-derivation. Still, the check should be robust.
- **Fix.** Strip the string and compare case-insensitively. Optionally require the "name, session, date" form that the draft asks for.

### LOW-2: the receipt's deviation line, X2 exposure, rules, procedure digest and `r1_record` are not verified

- **Where:** `scripts/align_v4_kit.py:749-751`, which compares only `inputs`, `derivation` and `contrast`.
- **What happens.** A signed (a) receipt is admitted with all of these:
  - `deviation_log: null` and `x2_exposure: null`;
  - `rules: {}`;
  - a forged `procedure.sha256`;
  - `r1_record.source: "forged"`.
- **Why it matters.** R10-2(a) says the change "is logged as a public deviation when applied", and the receipt is the artifact that carries that line.
- **Fix.** Require `deviation_log` to be a non-empty string naming R10-2(a). Then either check `procedure.sha256` against the committed procedure file or drop the field. The numbers are already bound.

### LOW-3: the blinding whitelist is shallow for `phases_s`

- **Where:** `scripts/align_w1_budget_procedure.py:46`, `:48`, `:55`, `:71` and `:75`.
- **What happens.** `ROW_FIELDS` and `X_G_FIELDS` include `phases_s`, so `_pick` deep-copies each whole `phases_s` dict, and only afterwards does `_phases` filter it. With poisoned nested keys (`energy_j`, `u5_value`, `beta_T`, `mde_tokens`, `temperature_c`), the copy touched all of them. `test_reads_only_timing_and_count_fields` misses this, for two reasons:
  - its `TrackingDict` does not hook `__deepcopy__` or iteration;
  - it never poisons nested `phases_s`.
- **Not an actual unblinding.** The runtime's `phases_s` (`r1_runtime.episode_phases`) holds phase seconds only. Nothing outside the whitelist reaches the output, and no top-level energy, U5, thermometry or `planning_temperature` key was touched.
- **Fix.** Drop `phases_s` from the two `_pick` field lists and copy it only through `_phases`. Extend the test to poison nested dicts and hook `__deepcopy__` and `items`.

### LOW-4: gated runs that decoded nothing give holds_proj = 0 and r from step-d alone

- **Where:** `scripts/align_v4_kit.py:519-524` (`projected_holds_s`), plus `gated_fit_inputs`.
- **What happens.** Take a record where all three gated D runs have `decode_tokens` 0 and G1 = H = 0. With the 1(f) case's numbers (r 11.9 tok/s), the derivation gives branch (a) with G0\* = 292.5 s. No gated decode evidence backs either the holds term or the rate.
- **Why it is LOW.** The duty bar then fails (`admitted_turns_ge_3`) and needs a recorded lead fallback, so the case does not pass silently. The no-receipt rule has the same property.
- **Fix.** Require at least one gated D run with `decode_tokens` > 0 for branch (a); every run would be stricter.

### LOW-5: small consistency points

- **`decide` can recommend B_D 6,144 that the kit then refuses.** It recommends (a) with `R1.B_D` = 6,144 (`align_w1_budget_procedure.py:151`) without checking that `r1_slots.slots.B_D` ≥ 6,144. The kit then refuses with "exceeds r1_slots.slots.B_D", so this fails closed. `decide` could name the problem itself.
- **Stale error text.** `thermal_gates.validate_gate_policy` (`joulewise/align/apple/thermal_gates.py:121`) still prints "[600, 1200]" for a receipt-bearing cap below 600 s that is out of range.
- **Contradictory contract bullet.** `docs/align/r1_runtime_contract.md:94` keeps "that alone is never a refusal" ahead of its R10-4 supersession sentence. Strike it or mark it superseded inline.
- **No template slot for `g0_cap_receipt`.** The W1 night-plan template has none. Under a receipt the operator must add it by hand. If it is missing, the validator's equality check against `inputs.R1.thermal_policy` refuses, so this fails closed.

## Checked and found sound

**(a) The 1(f) fit and the deadmen.**
- Under a receipt, the 1(f) worst case is G0 term floor(G0\*) + holds projected to B_D + 4,096 + max(prefill + tool) + (B_D + 4,096)/r. At the floor it is ≤ T_dead by construction, and the property test confirmed this. Any B_D above the floor refuses.
- The contrast cap is clamp(ceil(1.25 × X-G wait), 600 s, 1,200 s). It must fit 1,086.3 s on X-G's full WP18 X turns with no deadman, or the kit refuses in every branch.
- Contrast members never carry the receipt, and their `g0_cap_s` is `contrast_g0_cap_s` (`gate_policy_fields(role='contrast')`).
- A G0 timeout ends the member before turn 1 (`workload.py:444-490`, `episode.g0_unreleased`). So a D G0 longer than G0\* is X2, not X7.
- The unobserved G0 wait is now min(300 s, cap) (`thermal_gates.py:563`), so a sub-300 s cap cannot be outlasted. Nothing changes for caps ≥ 300 s.

**(b) Receipt binding.**
- The kit refuses any of these receipts:
  - unsigned;
  - with another schema or authority;
  - taking branch (b), (c) or anything else;
  - whose `inputs`, `derivation` or `contrast` differ from the re-derivation, including T_dead, the R1 G0 timeout, the WP18 X turns and every gated phase;
  - a branch-(a) receipt over a censored D G0.
- A re-run R1 or a changed T_dead makes a committed receipt refuse W1 (fail closed).
- `g0_cap_receipt.receipt_sha256` must equal the sha256 of the committed canonical bytes, and `read_ruling_1f_receipt` refuses non-canonical files.
- A `g0_cap_receipt` with no committed receipt is refused, and so is a sub-600 s cap without one (both in the kit and in `validate_gate_policy`).

**(c) Blinding.**
- `decide` and `backfill-x-g` read only the whitelisted top-level keys, with the LOW-3 caveat on nested `phases_s`.
- The duty-bar verdict is a timing and count verdict: x7, admitted turns, gate-hold fraction.
- `inconclusive_segments` values are fixed strings.
- `backfill-x-g` loads `r1_result.json` but picks only X_G_contrast's `g0_outcome`, `g0_wait_s`, `admitted_turns`, `phases_s` and `episode_flags`, and prints nothing from it.

**(d) No receipt.** The 1(f) refusal, `max_fitting_b_d` and the recorded-holds term are unchanged, apart from MEDIUM-2.

**(e) The G0\* derivation.**
- The units are seconds throughout, and tokens = 6,144 + 4,096 = 10,240.
- r = min(step-d, every gated run's tokens / decode seconds) is re-derived and checked against `budget_fit_inputs`.
- The holds projection is max(G1 + H, (G1 + H)/tokens × 10,240), taken as the maximum over the runs.
- PT = max(prefill + tool).
- The admit bound is ceil(1.25 × W_D) ≤ G0\* over released D waits, any censored D G0 blocks (a), and the armed cap is floor(G0\*). Rulings (i) and (ii) are honoured.

**Driver and print-only report.**
- The X-G evidence fields match `r1_runtime.k_x_g`'s result keys (`admitted_turns`, `episode_flags`, `phases_s`; `r1_runtime.py:1916-1921`).
- The `d_member_x2` desk report reads the G0 interval `outcome` and the merged `thermal.gate_timeout:` and `thermal.hold_timeout:` flags, and it is print-only.

**(f) Text against R10.** Apart from MEDIUM-1, MEDIUM-2 and LOW-5, the protocol v4 and contract text matches R10-2 and R10-4 and the lead's rulings on the builder decisions. The duty-bar fallback under (a), open point (a), is correctly left open with no code.

## Fixes requested before any W1 arm

1. **MEDIUM-1.** Make branch (a) unreachable whenever the current rule fits at some B_D ≥ 6,144, and add a test.
2. **MEDIUM-2.** Either the lead ratifies in LEAD-RULINGS-2 that per-role caps and the unconditional contrast proof apply to every W1, as a deviation from R7-2's D term, with LEAD-RULINGS-2 `:772` corrected and a test added; or the combined cap is kept as the no-receipt D term.
3. **LOW-1 to LOW-4.** Small hardening, recommended in the same fix commit.
