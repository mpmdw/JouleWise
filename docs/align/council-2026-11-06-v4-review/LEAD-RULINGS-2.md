# Lead rulings on the v4 council review: round 2, R1 round 5 (2026-11-06)

Laptop lead (Opus 5.5). These rulings settle the findings of the two reviews of the R1 round-4 integrated head:

- "exec" is `docs/align/reviews/2026-11-06-r1-round4-executing-review.md`;
- "cold" is `docs/align/reviews/2026-11-06-r1-round4-fable-cold-pass.md`;
- "Sol wp15rev" / "Sol w1rev" are the local Sol audits on `sol/burn-wp15rev@657c3ad29` and `sol/burn-w1rev@8ce7042ab`, with their triage notes at `docs/run_reports/sol-burn/triage-*.md` on those branches.

Each ruling's text below is verbatim as the lead gave it; the reason is the one the lead stated, or the finding it closes. Under each one: the commit(s) that implemented it, and any deviation or open point the builders reported.

Two builder lanes implemented them, both branched from `lane/2026-11-06-v4-r1-integrated@54e844b87`:

- science: `lane/2026-11-06-v4-r1-round5-science@e8bfd4ed5` (R5-1, R5-2, R5-3, R5-5, R5-7): `664a94757` (the rulings) and `e8bfd4ed5` (fixes from a local Sol critique of that diff);
- infra: `lane/2026-11-06-v4-r1-round5-infra@70986d5c9` (R5-4, R5-6, R5-8, R5-9, R5-10): `99a90e9c6` (the rulings), `002ee41ba` (run report, finally-signal test), `367bc0b42` (Sol critique fixes), `033907f52` (1(f) input-validity test), `70986d5c9` (suite tail). Its report: `docs/run_reports/2026-11-06-align-v4-r1-round5-infra.md`.

Integrated on `lane/2026-11-06-v4-r1-integrated` by the merges `e3e52ce5a` (science) and `e7aec1ea9` (infra). The integration record is in `docs/run_reports/2026-11-06-align-v4-r1-integration.md`, section "Round 5 integration".

## R5-1. Gated runs use the soak reference

> R5-1 (cold HIGH-2, warm reference): the gated D runs and X-G must use the soak-captured reference R, the same consume role W1 members use, not a self-captured warm reference. Before each gated run, idle-cool until S_slow is within the G0 band of R (bounded wait); a timeout makes that gated run INCONCLUSIVE (recorded), not a night refusal. Reason: the ruling 1(d) duty bar must test W1's G0/G1/H; with a warm self-captured R, G0 cannot fail, so the bar is uninformative.

**Implemented by** `664a94757`, `e8bfd4ed5` (science).
- X-G and the gated D runs install the soak R through a session hook (`reference_source = r1_soak_reference`); the driver refuses a run that did not consume it.
- Each gated D run is preceded by an `idle-until-soak` precool (cap 1,500 s, ruling 1(c)) on the one-sided G0 band S_slow ≤ R + δ_slow. X-G's precool is the post-D cooldown.
- A precool timeout makes that run's duty-bar row `inconclusive`. The overall duty verdict is then `inconclusive` unless a judged run fails. A replay-pair run that is inconclusive makes U5 INCONCLUSIVE. The kit treats a non-pass duty bar as before: W1 needs a recorded lead fallback step.

**Reported by the builder (design point for the lead).** Precooling to S_slow ≤ R + δ_slow means a gated run's G0 sheds only its own warmup heat against the soak R. W1's D-after-D G0 follows only the fixed 300 s inter-member idle, not a cool-to-band. So the duty bar's G0 share may still be lower than W1 will see. If the bar should test W1's case exactly, the alternative is a fixed 300 s idle instead of cool-to-band. Implemented as ruled.

## R5-2. Planning-turn deadman covers the decode only; start-state order

> R5-2 (exec MEDIUM-4, cold MEDIUM-3): arm the planning-turn deadman only after the preheat and G0 release; the deadman covers decode only (preheat and G0 keep their own caps). Order the planning start states to minimise G0 timeouts given that the host is warm after D_bank and the heater duty is clamped at 0 (e.g. warmest state first); document the order.

**Implemented by** `664a94757`, `e8bfd4ed5` (science).
- The designed start states keep their preheat (900 s) and G0 (600 s) caps. The deadman is re-armed after them (`token_budget.deadline_origin = R1_after_preheat_and_G0`).
- Order: R + 4, R + 2, R + 0 °C (`PLANNING_RUN_ORDER_C`), recorded in `r1_slots.planning_temperature.run_order_offsets_c` and in the contract doc.
- The ruling 8 batch-window bound of a start state adds the 900 s preheat cap.

No deviation reported.

## R5-3. An A-B-A leg without its own G0 release is inconclusive

> R5-3 (exec MEDIUM-1): an A-B-A leg whose own G0 does not release makes that leg INCONCLUSIVE per ruling 16 and R1 continues; it must not refuse the whole R1 night.

**Implemented by** `664a94757` (science). The leg exits 0 with `g0_released: false`, `t_decline_s: null` and `leg_status: inconclusive`. `aba_adoption` makes adoption INCONCLUSIVE (the ruling 16 rule is then `not_evaluated`); the series stays Automatic and R1 continues.

**Scope reported by the builder.** Only a leg whose own G0 did not release is INCONCLUSIVE. Any other incomplete leg (deadman cut, collector failure) still exits 3 and refuses R1, as in round 4.

## R5-4. A gated D never runs unbudgeted; the kit binds budget and policy

> R5-4 (cold MEDIUM-2, exec MEDIUM-2, Sol wp15rev F4): never run a gated D unbudgeted: refuse when slots.B_D is outside [1024, 40960] or 0. check_r1_evidence/require_ready bind inputs.R1.B_D <= r1_slots.B_D and thermal_policy (chunk_tokens = N_chunk, delta_slow = S5/S6, turn_cap = S7) to r1_slots, and assert ruling 1(f) (worst-case G0 + holds + last turn fit T_dead).

**Implemented by** `99a90e9c6`, `367bc0b42`, `033907f52` (infra).
- Runtime: `gated_budget` refuses (exit 2, before model work) when B_D is not an integer multiple of 1,024 in [1024, 40960] (0 included), or when T_dead is not finite and positive.
- Driver: `_check_step_d` refuses right after step-d.
- Kit: `check_r1_budget_and_policy` enforces:
  - `inputs.R1.B_D` ≤ `slots.B_D`;
  - `chunk_tokens` = N_chunk, `delta_slow_c` = S6 (= S5 unless a lead `s6_tuning` receipt {authority, from_c = S5, to_c = S6 ≤ 2.0 °C} is recorded), `turn_cap_s` = S7;
  - ruling 1(f): max G0 + max (G1 + H) + max (prefill + tool) over the three gated runs + (B_D + turn_cap_tokens) / r_decode ≤ T_dead. On a refusal it names the largest fitting B_D.

**Reported by the builder.**
- Ruling 1(f) will probably bind on hardware. At FD:145's ~11 tok/s, (6,144 + 4,096) / 11 ≈ 930 s against T_dead ≈ 1,200-1,280 s. So even the 6,144-token floor fits only if worst G0 + (G1 + H) + prefill + tool across the gated runs is at most about 270-350 s. When it does not fit, the kit refuses W1 and names the largest fitting B_D (or None). The lead then needs ruling 1(e)'s fallback order, or a ruling on whether the "last admitted turn" term should be the full 4,096-token cap.
- The R1 classification digest: protocol v4 says WP16 also binds `thermometry.D.classification_sha256` into the frozen inputs. Neither lane makes `inputs.R1.thermal_policy` carry it; the kit checks the sensor lists, the bar and the pick-change verification only. Open.

## R5-5. Slots under the adopted series mode; full-inventory journals; 600 s recovery

> R5-5 (cold MEDIUM-1): the code follows protocol v4 :243-251: slots selected from the step run under the ADOPTED series mode (so step-d after the A-B-A decision), full-inventory journals, 600 s recovery. If this cannot fit the R1 night budget, do NOT silently diverge: implement what fits, and return the conflict with numbers in open_findings so the lead can amend the protocol.

**Implemented by** `664a94757`, `e8bfd4ed5` (science).
- The A-B-A legs run right after the 30B step's cooldown. Step-d and every later D measurement run under the adopted series mode. Each member records it as an observed integer, and `r1_slots.slots_ac_powermode` must equal `ac_powermode` (kit).
- Both planning-turn steps journal every inventoried T*/F* key at 1 Hz, idle 300 s after the G0 release, and observe a fixed 600 s recovery. They then run the WP14(a) classifier (stage r1). The D classification is the thermometry bar the kit requires.
- When R1 changes R0's picks, the runtime computes S7 for the R1 picks, and the kit requires a recorded `thermometry.lead_verification`.

**Reported by the builder.** It fits the R1 night budget, so the protocol was not amended. Open points:
- Coverage on hardware: `smc_enumeration.rank` uses `thermal.Coverage`, which counts sweep midpoints on a 1 s grid with a 100 ms tolerance. A full T*/F* sweep longer than about 200 ms (more likely with a second SMC reader under GPU load) drops coverage below 99 %. The thermometry bar then fails and the kit refuses W1. This fails closed. Check the per-sweep duration in `inventory/inventory_journal.jsonl` on the first R1 night.
- A second IOKit SMC reader (the inventory journal) runs beside the ThermalSession sidecar during the 30B and D steps. This is untested on hardware.
- For changed picks, S7's reference R is the median of the 300 s quiet window before prefill, not the soak: the soak journal holds only R0's keys. The lead's verification should confirm this.
- `cooldown_after_30b` (600 s) is kept although step-30b now ends with a 600 s recovery observation. Dropping it would save 600 s per night; the lead's call.

**Integration consequence.** With the legs before step-d, infra's A-B-A batch-window bound (R5-10, round-3 exec LOW-1) could no longer read step-d's I_D. `e7aec1ea9` uses the runtime's largest admissible I_D (1,750 s) in that bound.

## R5-6. W1 under an adopted High Power

> R5-6 (exec MEDIUM-3): W1 under an adopted High Power works end to end: the kit writes plan ac_powermode 2 when R1 adopts High Power; the session sets mode 2 through the allowed sudo rule with the marker; admission accepts 2 only when the plan declares 2; restore to Automatic at close. Tests with fake sudo/pmset.

**Implemented by** `99a90e9c6`, `367bc0b42` (infra).
- `prepare` carries the frozen series value into the night plan.
- `install` writes a W1 marker and then sets 2 through `sudo -n /usr/bin/pmset -c powermode 2`. It reads the mode back, then admits against 2. It restores Automatic (with `staging/v4-arm-NNN.restore.json`) on any refusal from the mode change to the handoff.
- `admit_ac_powermode` keeps the marker only when the plan declares 2.
- `run_night` restores Automatic at close on every exit path, and removes the marker only after the read-back is 0.

All of this is tested with fake sudo/pmset.

**Reported by the builder.** The marker lives in the session's measurement view, which later sessions do not share. If `run_night` itself dies (SIGKILL or power loss) during a W1 High Power night, the host stays at 2 with no marker the next session can see. The next night then refuses on the mode alone (fails closed) and needs a manual `sudo -n pmset -c powermode 0`. The contract doc states this.

## R5-7. WP15 sign-offs and the W1 launcher

> R5-7 (WP15 sign-offs): ACCEPTED: r1_slots S1-S4 carry step-response numbers with key names and class checks in slot_detail; t_decline censored with the t_decline_censored flag; S6 = delta_slow until the FD 2.6 tuning (record a TODO tied to the gated-run G1 median). collection_plan launcher: resolve cold LOW-7 per the protocol (member 5 captures, the others consume) and make the kit consistent.

**Implemented by** `664a94757` (science).
- `r1_slots.s6_tuning` records the TODO (`status: TODO`, S6 = S5) with the gated runs' median G1 and hold waits (`gate_waits_s`).
- `collection_plan` no longer names the R1 runtime as a launcher. `runtime_requirements.window_reference` names member 5 as the capture member and the others as consumers, and `--check` refuses any other roles.

**Reported by the infra builder.** When the lead tunes S6, the kit needs the receipt `s6_tuning {authority, from_c = S5, to_c = S6}` (S6 ≤ 2.0 °C). The TODO record that the science lane writes has no `from_c`/`to_c`, so a tuning must replace it with that receipt.

## R5-8. WP18 fixtures are a hard W1 prerequisite

> R5-8 (WP18 fixtures): ACCEPTED as a hard W1 prerequisite at registration/wp18_x_token_ids.json and registration/wp18_y_token_ids.json. The values need pilot-7 files that exist only on the Mac (b-e25/b-e18 align_turns.jsonl, p7-PILOT.json). Provide a script that computes the WP18 X/Y max_turns + token fixtures + sha256 from those files on the Mac and writes them where the kit reads them, with tests on synthetic inputs, and return in magistrate_request a short kit-delivery note (what to run, what files it needs, what to commit). Do not edit RUN_STATE.

**Implemented by** `99a90e9c6` (infra). Local Sol drafted `scripts/align_v4_wp18_fixtures.py`, and the infra builder reviewed it. It authenticates the member identity, the per-turn decode counts and the summary token ids. It then writes both fixtures and the four `inputs.WP18` leaves; `--check` re-derives them and writes nothing. `require_w1_ready` calls `validate_wp18_fixtures`. Tests: `tests/align/test_v4_wp18_fixtures.py` (synthetic inputs).

The kit-delivery note is in the infra run report and was passed to the magistrate. RUN_STATE was not edited.

## R5-9. Sol fixes, as triaged

> R5-9 (Sol fixes, verified by triage): apply from origin/sol/burn-wp15rev (657c3ad29): F3 bind B_D/N_chunk to the runtime-custody hash, F2 custody nested-name exclusion, PLUS Segment.close must catch BaseException and keep closing the remaining sessions (incl. the powermetrics stop) and still run stop_journals. Apply from origin/sol/burn-w1rev (8ce7042ab): require_sizing provenance check, hf_pins receipt bound to the pin-file bytes; regenerate the kit. The triage notes are on those branches at docs/run_reports/sol-burn/triage-*.md. Each fix needs a failing-first test.

**Implemented by** `99a90e9c6` (infra): F2, F3, `Segment.close`, `require_sizing` provenance and the `hf_pins` byte receipt (in `require_w1_ready` and `prequal.check_kit`), each with a failing-first test. The kit was regenerated.

Not taken: Sol F1 (the `ManagedSession` rewrite, which the triage rated overstated) and a cosmetic R0 message.

**Integration.** The science lane added `stop_inventory` to `Segment.close` under `except Exception`. `e7aec1ea9` widens it to BaseException, so a TERM there cannot strand the sessions or the journals. The extended close test fails without this.

## R5-10. LOWs to fix

> R5-10 (LOWs to fix): exec LOW-1 (the 15 s watchdog writes a terminal custody record and stops powermetrics before os._exit); exec LOW-3 (one diskutil retry); exec LOW-9 (t63 with no rise -> null + flag, not 0.0); round-4 LOWs: reject t_decline_s: true, ruling 16 'A legs infinite, B finite' -> not-adopt, A-B-A leg wait bound from the configured values; cold LOWs: soak_detrended uses the last 1,200 SECONDS not samples; the kit must not admit lead_fallback step 4 (screen-only) as W1 admission; a first signal inside the driver's finally still writes r1_result.json. Document any other LOW you leave, with a reason.

**Implemented by** `99a90e9c6`, `002ee41ba`, `367bc0b42` (infra). Every listed LOW is fixed with a test.

**Deviation.** The A-B-A leg wait bound was written as 65 + 600 + step-d I_D + 1.13544 × `step.deadman_s` + 120 s. Since R5-5 puts the legs before step-d, `e7aec1ea9` uses I_D = 1,750 s, the runtime's admissible maximum. That gives 65 + 600 + 1,750 + 1.13544 × 1,580 + 120 ≈ 4,329 s, which only waits longer for the batch window.

**LOWs left, with the builder's reasons** (detail in the infra run report):

| LOW | Reason left |
|---|---|
| exec LOW-2 | Only a few-ms custody-write window remains. |
| exec LOW-4 | Only in `PowerModeGuard.restore` and `admit_ac_powermode`; admission re-reads. |
| exec LOW-5, LOW-6 | Need a hardware comparison. |
| exec LOW-7 | A stop-table change outside R1. |
| exec LOW-8, cold LOW-5 | Laptop environment, not code. |
| exec LOW-3, second half | The ruling text is "mounted". |
| cold LOW-3 | Harmless. |
| cold LOW-6 | Printed beside the energies in the R1 report. |
| round-3 exec LOW-2, second half (`recovery_curve` row shape) | Left to the science lane's run-loop rewrite. That lane checks `released` (bool) and a non-empty curve but not the row shape, so it is still open. |

## Round 6 (2026-11-07)

These rulings settle the findings of the two reviews of the R1 round-5 integrated head (`998ee2ab0`):

- "exec" is `docs/align/reviews/2026-11-06-r1-round5-executing-review.md`;
- "cold" is `docs/align/reviews/2026-11-06-r1-round5-cold-pass.md` (`d5f1b6606`).

Each ruling's text is quoted verbatim as the lead gave it, with the reason it carries. Under each one are the commits that implemented it and any deviation or open point the builders reported.

Two builder lanes implemented them, both branched from `lane/2026-11-06-v4-r1-integrated@998ee2ab0`:

- **science** (R6-1 to R6-6): `lane/2026-11-07-v4-r1-round6-science@0633a9c21`.
  - `9900f4cd0`: the rulings.
  - `0633a9c21`: fixes from a local Sol 6.1 xhigh critique of that diff (Sol audit: clean).
- **infra** (R6-7, R6-8): `lane/2026-11-07-v4-r1-round6-infra@5086e147a`.
  - `ae26b7c40`: the rulings.
  - `200ca2555`: fixes from a local Sol 6.1 xhigh critique.
  - `5086e147a`: the hazard-refusal allowlist guards.

They were integrated on `lane/2026-11-06-v4-r1-integrated` by two merges: `c42c39a5f` (science) and `c6f178f0f` (infra). The integration record is the "Round 6 integration" section of `docs/run_reports/2026-11-06-align-v4-r1-integration.md`.

### R6-1. The duty bar reproduces W1's D-after-D G0

> R6-1 (exec MEDIUM-2, supersedes the cool-to-band part of R5-1): the duty bar must reproduce W1's D-after-D G0. Each gated D run (and X-G) is preceded by exactly W1's inter-member schedule after a D turn — the fixed 300 s idle (take the value from the W1 plan/protocol, do not hard-code a different one) — and is gated against the soak-captured R (R5-1's consume role stays). No cool-to-band before gated runs. A G0 timeout makes that gated run INCONCLUSIVE (recorded), not a night refusal. Reason: W1 members get only the fixed idle, so cooling to band understates the G0 share the bar exists to measure.

**Implemented by** `9900f4cd0` and `0633a9c21` (science).
- The idle is read from the W1 plan template (`align_v4_kit.w1_inter_member_idle_s`: each member config's `sampling.idle_seconds`, 300 s). The driver checks the runtime templates against it at t0 and checks each run's reported `inter_member_idle_s`.
- `r1_slots.duty_bar.schedule` records the schedule, and the kit requires it.
- The soak-R consume check stays.
- A G0 timeout makes the run INCONCLUSIVE. So does following a member that did no D work. `r1_slots.x_g` records its own status.

**Builder decisions, for the lead to confirm:**
- **Order.** For every gated run and X-G to follow a D turn, the gated block (D_spam a, D_spam b, D_bank, then X-G) now runs *after* the three designed start states. Before, it ran after X-G and the post-D cooldown. The R + 0 °C planning turn is the D turn before D_spam a.
- **Inter-member schedule.** W1's schedule is taken to be the member's own configured idle (300 s), which runs inside `run_benchmark`'s idle_baseline stage. R1 inserts no idle segment of its own between members.
- **No D work.** A gated run or X-G that follows a member which did no D work is INCONCLUSIVE, because it did not test the D-after-D G0. "No D work" means a timed-out G0, or a released G0 with zero decode tokens.
- **Ruling 1(f), conservative.** A gated run whose G0 timed out is INCONCLUSIVE in the duty bar, but its G0 seconds (the 600 s cap) stay in ruling 1(f)'s max-G0 term. So a single gated G0 timeout makes the kit refuse W1 on 1(f). Leaving inconclusive runs out of the 1(f) maxima would need a ruling.

### R6-2. Calibration precools; a G0 timeout is retried, then INCONCLUSIVE

> R6-2 (exec MEDIUM-1): add a bounded precool (cool S_slow to the G0 band of R, cap from config) before step-d and between consecutive planning states. These are calibration measurements, not W1 replicas, so they should start from a defined state. A G0 timeout at step-d or at a planning state must not refuse the whole night after hours of work. Retry that segment once after another precool; if it still times out, record INCONCLUSIVE for that segment and let the kit decide downstream (fail closed at the kit, not mid-night).

**Implemented by** `9900f4cd0` and `0633a9c21` (science).
- **Precool.** An `idle-until-soak` precool runs before step-d and before the second and third designed start states. Its cap is the runtime config's `calibration_precool_cap_s` (1,500 s). The ruling 1(c) post-D cooldown precedes the first designed state.
- **Retry.** A pure G0 timeout is an INCONCLUSIVE runtime result: exit 0, recognised by `r1_runtime.g0_timeout_only`. The driver retries the segment once after another precool. If it times out again, the driver records it in `r1_slots.inconclusive_segments` and continues.
- **An INCONCLUSIVE step-d** skips the gated runs and X-G, so no gated D runs unbudgeted. `r1_slots` is then written with `slots` null.
- **An INCONCLUSIVE designed state** makes beta_T and U5 INCONCLUSIVE.

**Builder decision (Sol critique HIGH), for the lead.** The kit refuses W1 for any entry in `inconclusive_segments`, a designed start state included. Before R6-2 such a case refused the whole night. So after such an R1, W1 needs a lead ruling.

**Schedule cost, reported by the builder.**
- Removed: the three gated precools (up to 1,500 s each) and `cooldown_after_30b` (600 s).
- Added: three calibration precools (up to 1,500 s each), plus up to one retry (precool + segment) per calibration segment.
- The nominal night is about 600 s shorter. Each retry adds up to 1,500 s plus the segment to the worst case. The integrated numbers are under R6-8, cold LOW-6.

### R6-3. Ruling 1(f) uses the slowest observed decode rate

> R6-3 (exec MEDIUM-5): the ruling 1(f) worst-case decode term uses min(step-d decode rate, every gated run's observed decode rate). Keep the 'last admitted turn' term at the full turn cap (conservative). When 1(f) does not fit, the kit keeps refusing W1 and naming the largest fitting B_D; the lead rules on ruling 1(e)'s fallback after the R1 night. No code fallback.

**Implemented by** `9900f4cd0` (science).
- Gated runs report `decode_tokens`.
- `budget_fit_inputs` records step-d's rate, each gated run's observed rate and their minimum.
- The kit re-derives the minimum from the `deadman_budget` rows and refuses a stale recorded rate.
- The last-turn term keeps the full turn cap. There is no code fallback.

No deviation reported.

### R6-4. Changed picks bind S6/S7 to the R1-pick values

> R6-4 (cold MEDIUM-3, protocol fidelity): when R1 changes the picks, S6/S7 bind to the values computed for the R1 picks (s7_for_r1_picks etc.), per protocol v4 :247-251. The kit admits the R1-pick values and refuses the R0-pick ones in that case. Changed-pick S7 uses the median of the 300 s quiet window before prefill as R, because the soak journal lacks those keys: ACCEPTED, record it.

**Implemented by** `9900f4cd0` (drafted by local Sol and reviewed by the builder) and `0633a9c21` (science).
- With changed picks, `turn_cap_s` and `delta_slow_c` bind to `thermometry.D.s7_for_r1_picks` (`S7` and `band_c.s_slow`). The R0-pick slots are refused. An S6 tuning receipt starts from the R1-pick slow band.
- The driver records the accepted quiet-window reference rule.
- Sol critique: `thermal_policy.sensors` must equal `s7_for_r1_picks.keys`.

**Integration (`c6f178f0f`).** The infra lane's cold LOW-1 binding (below) tied `delta_fast_c` to `slots.S5_fast`, the soak fast band of R0's fast key, even when the picks changed. `s7_for_picks` computes a band for both roles, so with changed picks the kit now binds `delta_fast_c` to `s7_for_r1_picks.band_c.s_fast`, and it refuses that band when it is missing or not finite. (The infra report said only the slow band was computed; that was mistaken.) The test is `R1ChangedPickBindingTests.test_changed_picks_bind_delta_fast_to_the_r1_pick_fast_band`, and it fails without the change. The contract doc is updated.

### R6-5. The classification digest is bound

> R6-5 (protocol WP16): inputs.R1.thermal_policy carries thermometry.D.classification_sha256, and the kit binds it to the R1 record.

**Implemented by** `9900f4cd0` (science). `inputs.R1.thermal_policy.classification_sha256` must be a 64-hex digest equal to `r1_slots.thermometry.D.classification_sha256`. The digest is removed before gate-policy validation and member install. The template and kit were regenerated.

No deviation reported.

### R6-6. `cooldown_after_30b` dropped; A-B-A bound accepted

> R6-6 (engineering): drop cooldown_after_30b, because step-30b's 600 s recovery observation already provides the idle. Confirm nothing reads the cooldown as a measurement. ACCEPT the integration's A-B-A batch-window bound using I_D = 1,750 s.

**Implemented by** `9900f4cd0` (science). The phase is gone. The builder confirmed that nothing read it as a measurement: the only references were the phase table and one external-volume test's segment name. The A-B-A bound (`ABA_LEG_I_D_BOUND_S = 1750`, about 4,329 s per leg) is kept.

### R6-7. No exit path leaves the host at mode 2

> R6-7 (exec MEDIUM-4, cold MEDIUM-1/2, SIGKILL case; required before any W1 under High Power): no exit path may leave the host at mode 2 unrestored. Put the High Power marker in a HOST-level location every session can see (outside the per-session measurement view; root-owned under the existing sudo rule if needed). Restore Automatic and clear the marker on every non-measuring exit: install no-op return, malformed plan, rerun or launch_abandoned, admission refusal, failed pmset read, and never-launched. Add the watchdog J4-release restore. At every session start and every run_night admission, a host marker means restore first, then re-check. Make that restore safe against a late launchd fire that overlaps a retried night: never restore while a measuring night holds the night lock. Tests cover every path with fake sudo/pmset. Fix the r1_runtime_contract wording to match.

**Implemented by** `ae26b7c40`, `200ca2555` and `5086e147a` (infra).
- **Location.** The marker is host-level at `$JOULEWISE_HOST_STATE_DIR`. The default is `/Users/Shared/JouleWise/host-power/high-power.marker`, created on first use with mode 0700 and with its owner recorded as JSON. Beside it is a host night lock (flock), which the kernel drops when its holder dies. No new sudo rule is needed.
- **Restore rule.** `restore_owed` restores only a marker this night owns, or any marker at a session start, and never while another process holds the lock. Admission refuses rather than restore under a measuring night.
- **Session (`install`).** It holds the lock and restores a foreign marker first. It then writes a host-level W1 marker naming its session. If the shared installer installs nothing, it restores and refuses.
- **Session (`prepare`).** It restores an owed marker first, and refuses if the restore fails.
- **`run_night`.** A night that declares 2 holds the lock from before its admission read to the end of its close. An admission refusal restores, including a failed pmset read. The malformed-plan, rerun and J4 launch_abandoned exits restore the marker this plan owns.
- **Watchdog.** The J4 release restores its plan's marker.
- **R1 driver.** Its guard also writes and clears the host marker. R1 runs holding the night lock.
- **Contract doc.** The "owed to the next night" wording is replaced.
- **Sol critique fixes (`200ca2555`):**
  - F1: the R1 teardown restores only while it holds the lock.
  - F5: under plan 2, only a marker this night owns is kept.
  - F6: markers are removed only after the read-back is 0.
  - F8: the night-path test modules point `JOULEWISE_HOST_STATE_DIR` at a temp dir.

**Open, for the lead (Sol critique, each rated HIGH by Sol, not changed):**
- **F2.** The lock lives as long as the `run_night` process. If `run_night` alone is SIGKILLed while its chain keeps measuring, the lock is released, and a session start could restore under the surviving chain. The same holds for the R1 driver and its runtime child.
  - The option is to pass the lock fd to the chain (`pass_fds`), so the lock lasts as long as the night's process tree.
  - The cost is that an orphaned descendant would keep it held: later restores defer, and W1 refuses on the lock (fails closed).
- **F3.** The W1 close restores Automatic in `run_night`'s `finally` without proving that the hazard chain has stopped. This is R5-6 behaviour. The night is already aborted, so no data is admitted.
- **F4.** Nights with plan 0 do not hold the lock. A v4 install during a running plan-0 night could therefore set mode 2 for the seconds before that night's no-op restore. The options are that every admitted night holds the lock, or that install checks launchctl before it enters High Power.

**Consequence the builder reported.** Preparing or installing a new session while another W1 High Power session is armed but not yet measuring restores that session's High Power. That night then refuses at admission (expected 2, observed 0). This fails closed, as the ruling text requires.

**R1 chain.** The zsh is unchanged, so no plan pin changes. An R1 night cannot be admitted while a W1 High Power night holds the lock, so the chain's unconditional `pmset 0` cannot run under it.

### R6-8. LOWs to fix

> R6-8 (LOWs to fix): exec LOW-2 (completeness check before an unreleased-G0 leg returns INCONCLUSIVE); exec LOW-3 (block signals around each session close so powermetrics is always stopped); exec LOW-5 (the kit re-derives duty_bar.pass from per-run verdicts); exec LOW-6 (r1_result.status is the authority for committing r1_slots); cold LOW-1 (bind delta_fast_c to an r1_slots fast band, recording it); cold LOW-2 (policy sensors must equal R1's picks); cold LOW-4 (the soak reference check uses the s_slow sensor specifically); cold LOW-5 (WP18 fixture tool checks the rows' run id and seed against p7-PILOT.json); exec LOW-4 (Sol F6, validate turn contents where the fixture format allows); the round-3 recovery_curve row-shape check; cold LOW-6 (compute and write the all-caps R1 night worst case vs the R1 plan's window and record the numbers in LEAD-RULINGS-2; if no plan window_max_s exists, add one from the night plan template). Document any LOW you leave, with a reason.

**Implemented by** `ae26b7c40` and `200ca2555` (infra). The builder mutation-checked each fix's test.

| LOW | What implements it |
|---|---|
| exec LOW-2 | `r1_runtime.only_g0_unreleased`. An A-B-A leg is INCONCLUSIVE only for G0-only reasons; any other incompleteness exits 3. At integration, both this and science's `g0_timeout_only` (step-d and designed states) are kept. |
| exec LOW-3 | `r1_runtime.close_managed_session`. TERM, INT and HUP are held back around each session close, and a failed close stays retryable. CPython runs signal handlers on the main thread, so a close off the main thread runs as before, without deferral. |
| exec LOW-4 (Sol F6) | `align_v4_kit.check_wp18_turn_contents`. It checks each turn's index, its non-empty integer prompt and output token ids, and exactly two source digests. |
| exec LOW-5 | `align_v4_kit.check_duty_bar_consistency`. It re-derives FAIL > INCONCLUSIVE > PASS from the per-run `duty_bar.verdict`. |
| exec LOW-6 | `r1_slots` is committed atomically, only after a complete `r1_result.json`, which carries `registration_sha256`. |
| cold LOW-1 | `slots.S5_fast` (in `SLOT_NAMES`), with `delta_fast_c` bound to it. With changed picks it binds the R1-pick fast band instead (integration, see R6-4). |
| cold LOW-2 | `thermal_policy.sensors` must equal `thermometry.D.s_fast` and `s_slow`. |
| cold LOW-4 | The soak-reference check reads the soak's `sensor_roles.s_slow`. The runtime idle segment now emits `sensor_roles`. |
| cold LOW-5 | `align_v4_wp18_fixtures.py` binds each row to its turn index and to the seed-law per-turn seed. Sol F7 (a round-5 bug) is fixed: the summary seed is the member's seed index (16/14), not the derived 64-bit seed. This could not be checked against the real `p7-PILOT.json` off the Mac. |
| round-3 `recovery_curve` row shape | `_check_recovery_curve`: finite `[t_s, S_slow]` pairs with non-decreasing `t_s`. At integration it runs inside `_check_precool`, so the R6-2 retry precools are checked too. |
| cold LOW-6 | `align_r1_rehearsal.night_worst_case_s`. At integration it uses the round-6 table with the runtime's precool cap, and it reports the R6-2 retry allowance. |

**Cold LOW-6 numbers (integrated head `c6f178f0f`, `night_worst_case_s(None)`).** Bounds: timed segments at their duration or cap; quiet model segments at their ruling 8 bound; A-B-A legs at 4,329.0 s each; other model segments at the 1,800 s member bound. The calibration brackets and the harvest are not bounded.

| Case | Seconds |
|---|---|
| No redo, no retry | **44,487** |
| With one 11:45-13:15 batch-window wait (+5,400) | 49,887 |
| R6-2 retry allowance: 4 × (1,500 s precool + 3,300 s segment) | 19,200 |
| Every R6-2 retry plus one batch-window wait | 69,087 |

Each quiet-segment redo (`MAX_SEGMENT_REDOS` = 2) adds its release and the segment again on top of these.

The infra lane's 45,087 / 50,487 s are for the round-5 table, which still had `cooldown_after_30b`. Its projection of 45,387 s for the round-6 table is superseded by the 44,487 s above.

The gated runs and X-G are bounded at the 1,800 s member bound, with no separate allowance for the R6-1 300 s idle. If the idle falls outside that bound, add 4 × 300 = 1,200 s (45,687 / 51,087 s).

**Deviation (cold LOW-6, second half).** No R1 night plan and no `window_max_s` exists in the repo. The builder added no R1 plan template, because the R1 plan is a Mac-side artifact (`MEASUREMENT_ROOT`, `NIGHT_DIR`, the sudo rules). The W1 night plan template is the only plan in the repo. Its own `window_max_s` is a `PENDING_R1` placeholder, and its only numeric window is W1's `window_cap_s` of 44,640 s. So the template gives no R1 value to copy. *(Corrected in round 7, R7-9; round-6 cold pass LOW-3.)* This sentence first said that 44,640 s "is below even the no-redo R1 worst case". That held for round 5's 45,087 s but was false on the round-6 table above, whose no-redo case is 44,487 s. On the round-7 table (R7-2: step-d and the designed start states arm the 1,200 s G0 timeout), the true figures are: no redo, no retry 46,887 s; with one batch-window wait 52,287 s; R6-2 retry allowance 21,600 s; every retry plus one batch-window wait 73,887 s (48,087 / 53,487 s if the 300 s idle of the gated runs and X-G falls outside their member bound). W1's `window_cap_s` of 44,640 s is 2,247 s below the round-7 no-redo case. The conclusion is unchanged: the R1 plan's `window_max_s` must come from these numbers. The lead must set the R1 plan's `window_max_s` from the numbers above, or accept a wall-clock cut in the all-caps case. The magistrate was asked to do this (kit-delivery note, item 3).

**LOWs left.** None of the listed LOWs, apart from that second half of cold LOW-6.

**Integration notes on R6-8.**
- The science lane's own open items are now closed by the infra lane: exec LOW-2 for the A-B-A leg path, cold LOW-1 (`delta_fast_c`) and cold LOW-2 for unchanged picks.
- The policy sensors must equal the R1 picks in every case (infra). With changed picks they must also equal `s7_for_r1_picks.keys` (science).

## Round 7 (2026-11-07)

These rulings settle the findings of the two reviews of the R1 round-6 integrated head (`54d584de6`, reviewed at lane tip `97714c644`), plus one new physics input from the measurement Mac:

- "exec" is `docs/align/reviews/2026-11-07-r1-round6-executing-review.md` (its fixes are `4f2c3283a`);
- "cold" is `docs/align/reviews/2026-11-07-r1-round6-cold-pass.md` (`1e3f046bc`);
- "builder" is a round-6 builder decision recorded in the Round 6 section above.

**Physics input** (R0 re-run 7 SMC journal, analysed by the magistrate's fresh-design seats; quoted as the lead gave it):

> After the 900 s full load, no physical key reaches G0's 0.2 degC/min until 840-1,040 s after load end, but G0's cap is 600 s. The replayed G1 release came at 279 s, near the 300 s cap. Once the fans stop (180 s after the load), every key cools on one shared slow mode, tau about 430-510 s. TCMb and TVD0 are identical in all 1,800 rows; Tf24/Tf2D/Tf2E are one sensor under three keys. Aliased keys must never count as independent thermometers.

Each ruling's text is quoted verbatim as the lead gave it, with the reason it carries. Under each one are the commits that implemented it and any deviation or open point the builders reported. Two builder lanes implemented them, both branched from `lane/2026-11-06-v4-r1-integrated@97714c644`:

- **science** (R7-1, R7-2, R7-3, R7-12, R7-13): `lane/2026-11-07-v4-r1-round7-science@aa4cbfc6e`.
  - `92cf83226`: the rulings. The kit and gate side was drafted by local Sol 6.1 xhigh and reviewed by the builder.
  - `aa4cbfc6e`: fixes from a local Sol 6.1 xhigh critique of that diff (MEDIUM-2, LOW-3, LOW-4 fixed; MEDIUM-1 left open, below).
  - The builder mutation-checked 25 mutations; every one was caught. Sol audit: no restricted path was opened.
- **infra** (R7-4 to R7-8, R7-10, R7-11, R7-14): `lane/2026-11-07-v4-r1-round7-infra@d0a6d509f`.
  - `0ed43d4e2`: the rulings. R7-6 and R7-8 were drafted by local Sol 6.1 xhigh.
  - `d0a6d509f`: fixes from a local Sol 6.1 xhigh critique (F3-F6, F8; F1, F2, F7 left, below).

They were integrated on `lane/2026-11-06-v4-r1-integrated` by three `--no-ff` merges: `035624383` (science), `9ad3a7d56` (infra) and `bed96a99d` (`origin/lane/2026-11-05-align-pilot10-benign@e1a91226e`, which carries the merged PR #691 R0 contention guard). The integration added `9541b9dbd` (test only: `test_r1_round5_exec_review`'s real-signal test now expects R7-7's read-back record; it failed on the infra lane head alone), and R7-9 and this section are its doc commit. The integration record is the "Round 7 integration" section of `docs/run_reports/2026-11-06-align-v4-r1-integration.md`.

### R7-1. Gated block order: D_bank, D_spam a, D_spam b, X-G

> R7-1 (cold MEDIUM-1, exec LOW-6): reorder the gated block to D_bank, D_spam a, D_spam b, X-G, so both runs of the U5 replay pair follow a full gated D episode (matched predecessors, CHAIR 1(g)). The R + 0 C planning turn stays the D turn before D_bank.

**Implemented by** `92cf83226` (science). `phase_plan` runs `D_bank_benign_s1_gated_held`, `D_spam_benign_s1_gated_held_a`, `D_spam_benign_s1_gated_held_b`, `X_G_contrast` after `planning_turn_R_plus_0C`. X-G follows D_spam b, W1's D → X transition. Tests: `test_r1_round7_science.GatedOrderTests` (the phase table, and both replay runs following a full gated D episode). The contract doc and protocol v4 are updated.

No deviation reported.

### R7-2. R1's G0 timeout is 1,200 s; G0_cap_W1 is an R1-derived slot

> R7-2 (design change before any W1 data; reason: the physics input above shows G0 settling takes longer than the 600 s cap, and R1 exists to measure W1's G0 waits, not truncate them): in R1's gated runs, X-G and the R6-2 precool/retry segments, the G0 timeout is 1,200 s (one config constant, matching the R0 classifier's adaptive-idle cap). Record every G0 wait. W1's G0 cap becomes an R1-derived slot: G0_cap_W1 = clamp(ceil(1.25 x max measured gated G0 wait over D_bank, D_spam a, D_spam b, X-G), 600 s, 1,200 s). The kit binds it to r1_slots and ruling 1(f) uses it in the max-G0 term. A gated G0 that still times out at 1,200 s is INCONCLUSIVE and keeps 1,200 s in 1(f) (builder decision (d) confirmed). Recompute and record the R1 night worst-case table with the new caps.

**Implemented by** `92cf83226` and `aa4cbfc6e` (science).
- **One constant.** `configs/align/v4/r1_runtime.json` `g0_timeout_s` = 1,200. It is armed through an optional gate-policy `g0_cap_s` (`thermal_gates.validate_gate_policy`: 600-1,200 s; absent = the 600 s default, so v3 and every other G0 are unchanged). The driver reads it at t0 and refuses before any power-mode or runtime work when it is missing, out of range, or different from the committed value (Sol MEDIUM-2: the kit re-derives G0_cap_W1 with the committed value).
- **Every G0 wait.** `g0_wait_s` and `g0_timeout_s` are contract fields of every kind that runs a G0 (Sol LOW-3). `r1_slots.g0_waits` lists every wait of the night in run order, superseded and timed-out attempts and the `g0-release-soak` releases included. Each `deadman_budget` row carries its `g0_outcome`, and `x_g` carries `g0_wait_s`.
- **G0_cap_W1.** `r1_slots.g0_cap_w1` (`value_s`, `waits_s`, `censored`, `max_g0_s`, `floor_s`, `factor`, `r1_g0_timeout_s`, `x_g_fallback`). A gated G0 that did not release is censored and counts at 1,200 s. The kit re-derives it (`align_v4_kit.w1_g0_cap`), refuses a missing or stale record field by field (Sol LOW-4), binds `inputs.R1.thermal_policy.g0_cap_s` to `value_s` (W1 template placeholder added), and uses `value_s` as ruling 1(f)'s G0 term.
- **Worst case.** Step-d and the designed start states are bounded with the 1,200 s timeout (3,900 s each in the ruling 8 batch-window bounds). `night_worst_case_s(None)` on the integrated head:

| Case | Round 6 (s) | Round 7 (s) |
|---|---|---|
| No redo, no retry | 44,487 | **46,887** |
| With one 11:45-13:15 batch-window wait (+5,400) | 49,887 | **52,287** |
| R6-2 retry allowance: 4 × (1,500 s precool + segment) | 19,200 | **21,600** |
| Every R6-2 retry plus one batch-window wait | 69,087 | **73,887** |

The gated runs and X-G stay at the 1,800 s member bound (their G0 is inside the member deadman). If their 300 s W1 idle falls outside that bound, add 1,200 s (48,087 / 53,487 s). Each quiet-segment redo (`MAX_SEGMENT_REDOS` = 2) adds its release and the segment again. Tests: `test_r1_round7_science.G0TimeoutTests`, `G0CapW1Tests`, `ContractTests`, and the `test_v4_kit` `test_w1_g0_cap_*`, `test_missing_or_stale_g0_cap_record_is_refused` and `test_policy_g0_cap_must_bind_the_derived_slot` tests.

**Builder interpretation, for the lead to confirm.** "R6-2 precool/retry segments" was implemented as step-d and the designed start states (first attempt and retry) arming 1,200 s. The `idle-until-soak` precools themselves keep their 1,500 s cap.

**Open, reported by the science builder (not changed):**
- **1(f) will likely refuse W1.** The 1(f) G0 term is G0_cap_W1 itself (≥ 600 s and ≥ every counted wait). At about 20 tok/s, 1(f) then does not fit even at the B_D floor (6,144), so the kit will likely refuse W1 until the lead rules on the ruling 1(e) fallback (R6-3: no code fallback).
- **Gated runs and X-G cannot observe a full 1,200 s G0.** Gated runs arm the 1,200 s G0 inside T_dead, and X-G inside its 1,086 s contrast deadman (W1's rule). A longer wait ends as a deadman cut and counts at 1,200 s, so X-G can never record a released G0 of 1,200 s.
- **Sol MEDIUM-1 (pre-existing, not a round-7 ruling).** The ruling 8 batch-window bounds for step-d and the designed states (now 3,900 s) do not include member start-up overhead around the re-armed deadman. A near-cap step-d can take about 4,178 s and cross 11:45. Heavy redos add 600 s for the release but not its 65 s pre-roll.

### R7-3. R6-1 builder decisions confirmed; the R6-2 refusal names its remedy

> R7-3 (builder decisions R6-1 (a)-(c) confirmed; R6-2 refusal): (a) and (b) as built; (c) a gated run after a member with no D work is INCONCLUSIVE, confirmed. R6-2: the kit refusing W1 for any inconclusive_segments entry is confirmed; the remedy is an R1 re-run, which is the magistrate's call — no per-occurrence lead ruling. Make the kit's refusal message say that.

**Implemented by** `92cf83226` (science). Both `inconclusive_segments` refusals in `align_v4_kit` (step-d by name, and any other entry) end with "the remedy is an R1 re-run, which is the magistrate's call, with no per-occurrence lead ruling (LEAD-RULINGS-2 R7-3)". Test: `test_v4_kit` `test_inconclusive_calibration_refusals_name_rerun_and_magistrate`. The order of (a) is now R7-1's. The contract doc and protocol v4 record the confirmations.

No deviation reported.

### R7-4. SIGTERM and SIGHUP run the normal close

> R7-4 (exec MEDIUM-2): run_night and the v4 install get SIGTERM and SIGHUP handlers that run their normal close (High Power restore included). Tests with real signals.

**Implemented by** `0ed43d4e2` (infra). `run_night` and `align_v4_session.py install` handle TERM and HUP like SIGINT, so the normal close (the Automatic restore) runs. Once the close has begun, further TERM/HUP are swallowed. Tests with real signals: `test_r1_round7_power.NightSignalTests` (`test_sigterm_runs_the_close`, `test_sighup_runs_the_close`) and `test_r1_round7_install.InstallSignalTests`.

No deviation reported.

**Correction (round 8, R8-1).** The sentence "the normal close (the Automatic restore) runs" held for `install`, and for `run_night` only before the chain spawned or after it exited; the R7-4 tests parked the signal inside the chain spawn. While the chain ran, the close could not retake the lock the chain had inherited (R7-5), so it deferred, and the chain measured on with no supervisor and no window deadline (round-7 cold MEDIUM-1, exec MEDIUM-3). Since R8-1 an interrupt after launch first terminates the chain's process group and proves it gone, and only then runs the close, which then restores.

### R7-5. The host night lock lives as long as the night's process tree

> R7-5 (exec MEDIUM-3, Sol F2/F3): the host night lock lives as long as the night's process tree: pass the lock fd to the chain (pass_fds) for run_night and the R1 driver. The close restores Automatic only after it has itself taken the lock, which proves no chain still holds it. If it cannot take the lock, it leaves the marker for the dead-man or the next session start. Orphaned descendants keeping the lock make W1 refuse (fail closed): accepted.

**Implemented by** `0ed43d4e2` and `d0a6d509f` (infra).
- `run_night` passes the lock descriptor to the chain (`pass_fds`) for a night admitted under 2; the R1 driver passes it to its runtime child. `HostLock.release` only closes a descriptor, never `LOCK_UN`.
- The `run_night` close and the R1 guard first retake the lock on a fresh descriptor, and only then restore. Otherwise they log `ac powermode close deferred` (or `restore_deferred` in `r1_result.json`) and leave the marker for the dead-man or the next session start.
- Sol F4: under the retaken lock, a W1 marker another session owns (an install between release and retake) is left alone with its mode. Sol F5: the descriptor is moved off the launcher handoff slot (FD 198) before it is passed.
- Tests: `test_r1_round7_power.LockInheritanceTests`, `NightLockTreeTests`, `R1GuardTests`, `CritiqueFixTests` (F4, F5), `R1GuardOwnershipTests`.

**Open, for the lead (Sol F1, MEDIUM, documented, not fixed).** Only the R1 runtime inherits the lock from the driver; the runtime's own children (the heater and powermetrics) do not. If the runtime is killed and those children survive, the driver can retake the lock and restore while they still run. Neither measures anything, and the runtime's teardown stops them. Fixing it means passing the lock through `r1_runtime`.

### R7-6. The install checks launchd before High Power

> R7-6 (exec MEDIUM-4, Sol F4): the install runs the launchd/installer check before it enters High Power, with a test seam.

**Implemented by** `0ed43d4e2` (infra; drafted by local Sol 6.1 xhigh). Before it enters High Power, `install` runs the shared installer's launchd census through its command runner (`launchctl print gui/<uid>/com.joulewise.night`, 10 s timeout). A loaded job or an unavailable job state refuses before any pmset command; only exit 113 with the exact absent-service line admits. Tests: `test_r1_round7_install.InstallCensusTests`.

No deviation reported.

### R7-7. Every restore reads the mode back before clearing a marker

> R7-7 (exec LOW-2, cold LOW-1): PowerModeGuard and every restore read back pmset -g custom before clearing any marker. If the readback is not AC powermode 0, keep the markers and refuse.

**Implemented by** `0ed43d4e2` (infra). `PowerModeGuard.restore` reads `pmset -g custom` after the AUTO and removes both markers only on AC powermode 0; otherwise it keeps them and the run refuses. `powermode.restore_automatic` and `run_night` already read back (round-6 F6). Tests: `R1GuardTests.test_a_restore_that_does_not_read_back_zero_keeps_both_markers` and `..._reads_back_zero_clears_both_markers`.

No deviation reported.

### R7-8. The close signal deferral is bounded at 10 s

> R7-8 (cold LOW-2): bound the round-6 signal deferral around a session close to at most 10 s, so the runtime's 15 s teardown watchdog always arms.

**Implemented by** `0ed43d4e2` (infra; drafted by local Sol 6.1 xhigh) and `d0a6d509f` (F8, test synchronisation). `close_managed_session` delivers held signals to the previous handlers on the main thread (`pthread_kill`) at most 10 s after the first held signal, even if the close is blocked. Tests: `test_r1_round7_close_deferral`.

**Open, for the lead (Sol F2, MEDIUM, not changed).** The 10 s cap plus the runtime's 15 s teardown watchdog lets the watchdog fire up to about 25 s after the first signal, but the driver kills the runtime at 20 s. The watchdog always arms, as R7-8 requires, but can fire after the kill. A fix would arm the watchdog when the first signal is held.

### R7-9. Doc corrections to the window comparison

> R7-9 (cold LOW-3): correct LEAD-RULINGS-2.md:301 and the integration report :958 (the window_cap_s comparison) to the true figures under the new caps.

**Implemented by** the integration's doc commit (the commit that adds this section). The Round 6 cold LOW-6 deviation paragraph above and the integration report's "Open after round 6" line now carry an inline correction: the original claim was false on the round-6 table (44,487 s < 44,640 s); under R7-2's caps the no-redo case is 46,887 s, with 52,287 / 21,600 / 73,887 s for the other cases (48,087 / 53,487 s with the idle caveat), so W1's `window_cap_s` of 44,640 s is now 2,247 s below the no-redo case.

### R7-10. A fixed production host state directory

> R7-10 (cold LOW-4): the host state directory is a fixed path in production (/Users/Shared/JouleWise/host-power). An environment override exists only through a test seam that production entry points refuse. Record the path in the night and session receipts.

**Implemented by** `0ed43d4e2` (infra). The production `__main__` of `run_night.py`, `align_v4_session.py`, `align_r1_rehearsal.py` and `magistrate_watchdog.py` mark themselves; from then on any use of an overridden `$JOULEWISE_HOST_STATE_DIR` refuses (`HostStateOverrideRefused`). The path is recorded in the night's admission record and custody log, the arm record (`staging/v4-arm-NNN.json`), the session-start restore records and `r1_result.json`. Tests: `test_r1_round7_power.HostStateDirTests`, `NightLockTreeTests.test_the_admission_record_and_log_carry_the_host_state_dir`, `R1GuardTests.test_the_r1_result_records_the_host_state_dir`, `test_r1_round7_install.InstallRecordsTests`.

**Deviation (Sol F7, LOW; partial).** For admitted nights the host state directory is recorded in `night.log` and the admission record, not in `night/receipt.json` or `night/result.json`, to avoid changing write-once record schemas. Refusals carry it in their evidence.

### R7-11. Lock errors, pre-admission exceptions and a failed marker write

> R7-11 (cold LOW-5, exec LOW-3/LOW-4): _take_host_lock tells "another night holds the lock" (EWOULDBLOCK) apart from any other OSError, which gets its own refusal code and runs the restore path. Exceptions before admission run the restore path. A failed marker write after a plan-2 admission refuses the night before measuring.

**Implemented by** `0ed43d4e2` and `d0a6d509f` (infra).
- Only EWOULDBLOCK/EAGAIN counts as another holder (still `night_refused_ac_powermode`). Every other lock or lock-file error (EACCES included, Sol F6) refuses with `night_refused_host_lock_error` and runs the owner-scoped restore path.
- Any exception or signal before the night's close is registered (the initial agent census, custody-log or census writes, the admission itself) runs the restore path, under the night's own lock when it already holds it, and then frees that lock (Sol F3: `admission_reached` is set only once the close is registered).
- A failed marker write after a plan-2 admission refuses the night before it measures, and its close restores Automatic.
- Tests: `test_r1_round7_power.HostLockErrorTests` and `CritiqueFixTests` (F3, F6).

**Deviations reported by the infra builder:**
- When the lock file itself cannot be opened, the restore path cannot take the lock either, so the marker stays and a manual restore is needed. This fails closed and follows R7-5's rule of never restoring without the lock. It differs from the round-6 cold pass's proposal (LOW-5) to restore without the lock.
- Exec LOW-3, first half (a plan-2 admission refusal with no marker present restores nothing) is not in the R7-11 ruling text and was not changed.

### R7-12. An INCONCLUSIVE X-G falls back to the 1,200 s cap

> R7-12 (cold LOW-6): if r1_slots.x_g is INCONCLUSIVE, the kit uses the 1,200 s G0 cap for W1's D-to-X G0 term in 1(f) and records x_g_fallback; it does not refuse on that alone.

**Implemented by** `92cf83226` and `aa4cbfc6e` (science). An `x_g` whose `status` is not `measured` counts at 1,200 s in G0_cap_W1 with `x_g_fallback: true`; that alone is never a refusal. Test: `G0CapW1Tests.test_an_inconclusive_x_g_falls_back_to_the_timeout`, and `test_v4_kit` `test_inconclusive_x_g_falls_back_and_is_admitted_when_1f_fits`.

**Integration note.** G0_cap_W1 is one cap for every W1 G0, and 1(f) has one G0 term, so the fallback sets the whole of G0_cap_W1, and with it the 1(f) G0 term, to 1,200 s, not a D-to-X term alone. That is at least as conservative as the ruling text.

### R7-13. Aliased keys are never two thermometers

> R7-13 (aliases): the kit refuses a thermal_policy whose s_fast and s_slow are aliases (byte-identical series over the R1 classification journal), and the R1 classification records alias groups so an alias is never a second thermometer. Classifier code on the pilot10-benign lane is being amended separately by the measurement Mac (PR #692); do not edit smc_enumeration/thermal classification code there. Bind to its outputs only through the kit.

**Implemented by** `92cf83226` (science). The R1 runtime computes `alias_groups` beside the classifier: sorted groups of inventoried keys whose 1 Hz series are identical in every row of the classification journal, failed reads included (keys never read are left out). They sit inside the classification digest, and the driver registers them. The kit refuses a record without `alias_groups`, and a `thermal_policy` whose `s_fast` and `s_slow` are one key or in one alias group. `smc_enumeration` is untouched (the measurement Mac's PR #692 lane). Tests: `test_r1_round7_science.AliasGroupTests` and `test_v4_kit` `test_missing_or_malformed_alias_groups_refuse`, `test_selected_aliases_or_same_key_refuse_as_one_thermometer` and `test_aliases_elsewhere_preserve_admission`.

**Limits reported by the science builder.** Alias groups match recorded series exactly. Coincidentally identical series would be grouped, and true aliases whose failed reads or numbers differ would be missed.

### R7-14. The R1 chain EXIT-trap restore stays as is

> R7-14 (exec LOW-5): leave as is (it cannot overlap a W1 night today); document it.

**Implemented by** `0ed43d4e2` (infra), documentation only. `docs/align/r1_runtime_contract.md` records that the R1 chain's EXIT-trap `pmset 0` runs after the driver has released the lock; no W1 night can be measuring then, because its install needs the single `com.joulewise.night` label, which the R1 night's job still holds, and both the v4 install's census (R7-6) and the shared installer refuse while it is loaded. A future multi-label installer must revisit this.

### Process incident reported by the science builder

A mistaken Sol launch truncated another lane's `r7-sol-crit.events.jsonl`. That lane's owner should audit the codex rollout file `~/.codex/sessions/2026/11/07/rollout-2026-11-07T03-16-19-01a1b5b9-42c4-76e1-88b1-79c2743a9890.jsonl` instead. No code or record of this lane is affected.

## Round 8 (2026-11-07)

These rulings settle the findings of the two reviews of the R1 round-7 integrated head (`915f59446`, with the executing review's fixes `e51156033`), plus the science and infra builders' open items:

- "exec" is `docs/align/reviews/2026-11-07-r1-round7-executing-review.md` (`72c7c8a50`; its fixes are `e51156033`);
- "cold" is `docs/align/reviews/2026-11-07-r1-round7-cold-pass.md` (`d20ccd829`);
- "science Sol" and "infra Sol" are the local Sol 6.1 xhigh critiques recorded under Round 7 above.

Each ruling's text is quoted verbatim as the lead gave it. One builder implemented all of them on `lane/2026-11-06-v4-r1-integrated`, branched from `72c7c8a50`:

- `191455724`: the code and tests (R8-1, R8-3 to R8-6), with `tests/align/test_r1_round8.py`. Every behaviour test in it fails on `72c7c8a50` (checked by stashing the code change).
- The doc commit that adds this section: R8-1's and R8-2's contract text, the R7-4 correction above, R8-4's table and R8-7's protocol v4 text, with `test_r1_round8.DocTests` (which fails on the round-7 docs).
- A fix commit for the Sol critique (under R8-1 below), then a report commit: the Round 8 section of `docs/run_reports/2026-11-06-align-v4-r1-integration.md` (kit check and exact test tails).

### R8-1. An interrupt after launch stops the chain, proves it gone, then closes

> R8-1 (exec MEDIUM-3 = cold MEDIUM-1, option A; required before any W1 arm under High Power): on an interrupt (INT/TERM/HUP) after the chain has launched, run_night terminates the chain's process group (TERM, bounded wait, then KILL) and proves it gone, as the window-deadline path already does, then runs the normal close, which can now retake the lock and restore. Same for the R1 driver and its runtime. Tests with real signals while the chain runs (the round-7 tests only parked the signal before the chain existed). Correct the contract doc and the R7-4 text in LEAD-RULINGS-2.

**Implemented by** `191455724`.
- **`run_night`.** `_run_chain_once` records the launched chain (and its window deadline) and catches `KeyboardInterrupt`, which is what SIGINT and the R7-4 TERM/HUP handler raise. `_stop_chain_on_interrupt` then cancels the deadline thread (if the deadline already fired, its outcome stands), and runs `_terminate_process_group`: killpg TERM, wait 30 s, a re-signalled group census for 5 s, killpg KILL, wait 30 s, census again. It records `chain.exited` for a claimed chain, or `chain.unkilled` if the proof fails, and logs `chain terminated on interrupt (lead ruling R8-1)` with the outcome. The interrupt is then re-raised, so `run_night`'s close runs: it retakes the lock (the chain no longer holds it) and restores. If the group cannot be proven gone, the retake fails and the close defers, as R7-5 says. This covers the HAZARD_PACK chain too (`b5/driver.py` reaches the same `_run_chain_once`).
  - SIGINT (when it still has Python's default handler) now goes through the same handler as TERM/HUP. It still raises `KeyboardInterrupt`, but once the chain termination or the close has begun, further INT/TERM/HUP are swallowed, so they cannot cut either short.
  - The new re-raise site is allowlisted in `configs/gates/hazard_refusals.json` (category INTERNAL: it adds no refusal).
- **R1 driver and runtime.** The driver's `_run` already TERMed its child, waited 20 s and KILLed it on an interrupt. `_terminate` now also records the child's descendants (`ps -A -o pid=,ppid=,command=`) while it lives: before the TERM, and again before a KILL. Once the child is reaped, it TERMs every recorded descendant still alive with its recorded command, waits at most 5 s, KILLs, waits at most 5 s more, and proves none is left. Each proof goes to `r1_result.child_terminations`. If a census fails or a descendant survives (for example a root `powermetrics` the user cannot signal), `PowerModeGuard.restore` restores nothing: `restore_deferred` names R8-1, and the markers stay for the dead-man or the next session start. `_terminate` also no longer waits forever on an output pipe that an orphaned descendant inherited: it waits on the reaped child, ends the tree, then drains with a bound and closes the pipes.
- **Tests with real signals** (`tests/align/test_r1_round8.py`):
  - `NightInterruptTests`: TERM, HUP, and INT on a chain that ignores TERM. Each signal lands while a real chain process, which inherited the host night lock and started a member in its group, is measuring under a plan of 2. In each case the chain and member are gone, `chain.exited` is written, no `chain.unkilled`, the close restores (mode 0, marker gone) and nothing defers.
  - `R1InterruptTests`: a real TERM while a real runtime runs X-G under the adopted High Power. The runtime has started a "heater" that ignores TERM and that the runtime orphans on its own exit. The heater is gone at every restore call, and the proof is recorded. With a descendant that cannot be ended, the restore defers and the markers stay; the next session start restores.
  - `TerminateTreeTests`: an orphan that holds the pipe neither hangs `_terminate` nor survives.
- **Docs.** The contract doc (item 4 of "W1 under an adopted High Power", the driver's TERM bullet, the host-lock paragraph) and the R7-4 text above are corrected.
- **Fixes from a local Sol 6.1 xhigh static critique of `72c7c8a50..543c9565d`** (Sol audit: clean; no command named a restricted path). The fixes are in the commit after the doc commit, and the test for each fails on `543c9565d`:
  1. An unproven chain termination now defers the close even when the lock can be retaken. A survivor that does not hold the lock, such as an unsignalable root descendant, never sees a restore. The close logs "not proven gone after the interrupt" and frees the lock (`NightUnprovenCloseTests`).
  2. The first TERM/HUP/INT now latches the shutdown before it raises, so a second signal cannot escape before the termination begins (`SignalLatchTests`).
  3. The launched process is published inside the spawn's `try`, and the deadline before its thread starts.
  4. In the R1 tree proof, a process is identified by its pid and start time (`ps … lstart`), not its command. An exec into another program is still tracked, and a reused pid is never signalled (`test_identity_is_pid_and_start_time_not_command`).
  5. The tree is re-read about once a second during the 20 s grace.
  6. Output pipes still held open after the tree is ended mean an unrecorded holder exists, so the proof fails (`test_a_pipe_held_by_an_unrecorded_process_is_not_proven`).
  7. The reap after a KILL is bounded at 30 s; an unreaped child is unproven (`test_a_child_that_is_never_reaped_is_not_proven`).
  8. The night tests now check that the chain and member are gone from inside the `run_night` process, before the test's emergency cleanup runs.
- **Residual windows.** A signal inside `Popen` itself, after the fork but before it returns, still escapes the termination; blocking signals there would leave the chain with a blocked signal mask. The R1 tree proof can still miss a descendant that is started and orphaned between two one-second reads and does not hold the output pipe. Both fail toward an unsupervised orphan, the R8-2 class.

No deviation.

### R8-2. Members and runtime children do not inherit the lock: documented

> R8-2 (exec MEDIUM-4, infra Sol F1): document only. Measuring members started by run_campaign and the runtime's heater/powermetrics children do not inherit the host lock; an orphan after a supervisor SIGKILL can see a restore under it. No data is admitted in that case (the night is aborted). Not fixed because it touches shared Block-5 code. Record it in the contract doc.

**Implemented by** the doc commit: `docs/align/r1_runtime_contract.md`, host-level marker and night lock paragraph ("Known gap, not fixed (lead ruling R8-2 …)"). No code change.

### R8-3. The runtime's watchdog arms when the first signal is held

> R8-3 (infra Sol F2): arm the runtime's teardown watchdog when the first signal is held (the R7-8 deferral), not after the deferral ends, so it fires before the driver's 20 s kill.

**Implemented by** `191455724`. `Termination.arm(signum)` starts the 15 s teardown watchdog once (idempotent). `Termination.handler` uses it. `close_managed_session`'s `hold` calls it for the first held signal when the deferred handler is the runtime's `Termination`. So the forced exit counts from the signal's arrival: 15 s, plus at most 4 s of hard-exit teardown, which is inside the driver's 20 s grace. The watchdog's terminal record names the held signal (`armed_signum`) if the handler has not run yet. Tests: `WatchdogArmTests.test_the_watchdog_fires_inside_a_blocked_close` (with a 0.5 s watchdog, it fires inside a close blocked for 2 s; it fails on `72c7c8a50`), and `test_a_handler_that_is_not_the_runtimes_termination_is_left_alone`.

No deviation.

### R8-4. Batch-window bounds include member start-up and the release pre-roll

> R8-4 (science Sol MEDIUM-1): ruling 8's batch-window bounds for step-d and the designed states include member start-up overhead around the re-armed deadman and the 65 s pre-roll of heavy redos. Recompute and record the worst-case table.

**Implemented by** `191455724`.
- `rearmed_member_bound_s` uses the A-B-A leg law (round-3 LOW-1) for the member whose deadman R5-2 re-arms: the member law's start-up and close at the largest I_D the runtime admits (1,750 s; step-d's own I_D is what step-d measures), plus 1.13544 × the re-armed `step.deadman_s` (1,580 s), plus 120 s of margin. That is 3,663.9952 s.
- `segment_bounds(g0_timeout_s, step_deadman_s)` adds the pre-deadman phases:
  - step-d: 3,663.9952 + 1,200 (G0 timeout) + 300 (quiet) + 600 (recovery) = **5,763.9952 s**;
  - each designed state: 3,663.9952 + 900 (preheat cap) + 1,200 (G0 timeout) = **5,763.9952 s**.
  - Round 7 had 3,900 s for each; science Sol's counterexample was a step-d of 4,178 s.
- A release before a segment (a heavy redo, or a release-first attempt) adds `release_segment_bound_s()` = 65 s pre-roll + 600 s G0 cap = **665 s** (round 7: 600 s). The A-B-A leg bound already had both.

`night_worst_case_s(None)` on this head:

| Case | Round 7 (s) | Round 8 (s) |
|---|---|---|
| No redo, no retry | 46,886.99 | **54,342.97** |
| With one 11:45-13:15 batch-window wait (+5,400) | 52,286.99 | **59,742.97** |
| R6-2 retry allowance: 4 × (1,500 s precool + segment) | 21,600 | **29,055.98** |
| Every R6-2 retry plus one batch-window wait | 73,886.99 | **88,798.95** |

The per-segment bounds behind the table:
- the soak 1,800 s;
- step-30b 3,300 s (unchanged);
- each A-B-A leg 4,328.9952 s;
- each precool and the post-D cooldown 1,500 s;
- step-d and each designed state 5,763.9952 s;
- the gated runs and X-G 1,800 s.

If the gated runs' and X-G's 300 s W1 idle falls outside their member bound, add 1,200 s (55,542.97 / 60,942.97 s). Each quiet-segment redo (`MAX_SEGMENT_REDOS` = 2) adds its 665 s release (`redo_release_s`) and the segment again. W1's `window_cap_s` (44,640 s) is now 9,702.97 s below the no-redo case.

Tests:
- `test_r1_round7_science.G0TimeoutTests` (the bounds and the round-8 table), `test_r1_round6_power.R1NightWorstCaseTests` and `test_r1_rehearsal` (the admitted bounds), updated to the round-8 values;
- `test_r1_round8.RedoReleaseBoundTests` (a heavy redo waits with the segment bound + 665 s).

**Builder notes, for the lead.**
- Step-30b keeps its round-5 bound of 3,300 s, because the ruling names step-d and the designed states. The same underbound argument applies to it (its deadman is also re-armed after the G0 and quiet).
- The designed states run after step-d, so their bound could use step-d's measured I_D instead of 1,750 s. That would be tighter. The builder kept the admissible maximum (a larger bound only waits longer).

### R8-5. An interrupt during `--dry-arm` only exits

> R8-5 (cold LOW-1): an interrupt during --dry-arm must not restore an armed session's High Power; it only exits.

**Implemented by** `191455724`. `run_night`'s outer handler runs neither pre-admission restore branch when `dry_arm` is set. Tests: `test_r1_round8.DryArmInterruptTests` covers an interrupt in the dry-arm branch (the cold pass's probe D) and one in its initial agent census. In both, the mode stays 2, the marker is kept and nothing is restored. Both fail on `72c7c8a50`.

No deviation.

### R8-6. Aliased picks fail R1's thermometry bar

> R8-6 (cold LOW-3): R1's thermometry bar fails when s_fast and s_slow are aliases (alias_groups), not only the kit.

**Implemented by** `191455724`. `picks_aliased` is true when the D classification's two picks are one key or sit in one of its `alias_groups`. In that case the driver sets `thermometry.bar` to `fail`, adds the flag `r1.picks_aliased` and records a `bar_reason`. The runtime's classification and its digest are unchanged. Tests: `test_r1_round8.AliasedPicksBarTests` (aliased picks fail; aliases elsewhere keep `pass`; the rule).

No deviation.

### R8-7. Protocol v4 made true

> R8-7 (cold LOW-4): update docs/align/pilot_protocol_v4.md so its claims are true: record R7-1's gated-block order, R7-2's R1 G0 cap of 1,200 s and the R1-derived W1 G0 cap slot, and R7-3, each citing LEAD-RULINGS-2.

**Implemented by** the doc commit. Protocol v4's R1 paragraph now states R7-1's gated-block order and R7-3's confirmations and remedy. Its G0 paragraph now states R1's single 1,200 s G0 timeout, which covers the gated runs, X-G, step-d and the designed states, first attempt and retry; the precools keep 1,500 s (R8-8). It also states that every G0 wait is recorded, and that W1's G0 cap is the R1-derived slot `r1_slots.g0_cap_w1.value_s`, carried as the `thermal_policy.g0_cap_s` placeholder. Each passage cites LEAD-RULINGS-2. With this, the round-7 claims "protocol v4 updated" under R7-1 and R7-3 are true.

### R8-8. Confirmations, recorded only

> R8-8 (confirmations, record only): the builder reading of 'R6-2 precool/retry segments' is confirmed (step-d and the designed states arm 1,200 s; idle-until-soak precools keep 1,500 s). Round-7 exec LOW-2 (G0 waits inside the member deadman) is accepted, because it is conservative. Ruling 1(f) likely refusing W1 at about 20 tok/s is expected: the 1(e) fallback is ruled by the lead after the R1 night, on its numbers.

Recorded. No code change.
