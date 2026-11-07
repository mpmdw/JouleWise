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
