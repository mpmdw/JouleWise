# 21 — Opus contract-lens refuter, cold gate BATTERY-FLOAT-01

Seat: Opus 5.5, paired contract-lens refuter. Worktree `JouleWise-wt-ed17a643-cg-refuter`, HEAD `6b769d98`, which is `origin/main` `c6814dd8` plus trace and RUN_STATE commits only (`git diff --stat c6814dd8 HEAD` touches no code, config or test file). Code was read from a `git archive c6814dd8` extraction in `/tmp/refuter-bfg`. Phase 1 was written ≈14:40–14:50 PDT, 2026-09-25.

**Contamination disclosure.** Besides this packet I loaded the global and project CLAUDE.md files and the auto-memory index (harness-injected; not opened by me). I read no RUN_STATE, TASK_QUEUE, council log, run report, memory file or other process trace. Code and config files read: `joulewise/{night_gate,arm_retry,evidence_night,calibration_bracketing,uncertainty_evidence,scored_reduce,environment,adapters/powermetrics}.py`, `scripts/{validate_powermetrics_fiducial,issue_calibration_acceptance_generation,calibration_cadence_report,gen_derivation_night}.py`, `scripts/night_chains/calibration_derivation_only.zsh`, `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` (Revision 1 text, Known conditions, Revision 5), and one `arm_readiness.sources` JSON.

**Manifest.** All six exhibit sha256 values match the charge. The charter matches its pin `099de884…c95d81`.

## Executed evidence (this session)

| # | Command | Result |
|---|---|---|
| E1 | `shasum -a 256 ex-*` and the charter | 7/7 match |
| E2 | `/usr/bin/time -p ioreg -r -c AppleSmartBattery -w0` at 14:35 PDT | rc 0, **real 0.01 s**, 17 353 bytes. Top level: `"ExternalConnected" = Yes`, `"IsCharging" = Yes`, `"InstantAmperage" = 585`, `"Amperage" = 585`, `"CurrentCapacity" = 100`, `"FullyCharged" = No`, `"Voltage" = 12952`, `"Temperature" = 3038`, `"UpdateTime" = 1790372085`, `"AppleRawCurrentCapacity" = 7516`. Nested in `ChargerData`: `"ChargingCurrent"=583`, `"NotChargingReason"=0`. Nested in `AdapterDetails`: `"Current"=4990`, `"FamilyCode"=18446744073172697098` |
| E3 | `pmset -g batt` | `AC Power`, `100%; finishing charge` |
| E4 | Six ioreg reads 20 s apart, 1790372155–1790372255 | `UpdateTime` moved 1790372145 → 1790372205, so the **gauge refreshes every 60 s**. Reads between refreshes returned identical values (596, 596, 596, then 579, 579, 579). `InstantAmperage` equalled `Amperage` in every read. `AppleRawCurrentCapacity` stayed at 7516 throughout, although about 20 mAh flowed in at ≈590 mA. `IsCharging = Yes` throughout |
| E5 | Code reads, cited below | — |

What E2–E4 establish:

- About 2 h after the limit change, the battery still charges at ≈0.58 A (≈7.5 W) while displaying 100 %. At W1's arm the gate refuses today.
- ioreg reads are passive: three reads inside one 60 s period left `UpdateTime` unchanged, so reading does not trigger a gauge poll.
- One read costs ≈10 ms.
- Negative 64-bit values really are printed unsigned: see the nested `FamilyCode`.
- Nested dictionaries carry look-alike current keys, written in the compact `"Key"=v` form.
- Any single reading can be up to 60 s old.

## B1 — design: seat claims verified at c6814dd8

Verified as the seats state them:

- **C3 site.** `night_gate.py:1486-1505`: `pmset -g batt` is stored as `ac_power_raw`; a missing "AC Power" refuses as `night_refused_not_quiet` with detail `ac_power`.
- **Registries.** `_CONDITION_IDS = ("C1".."C5")` at `:301`, and `NIGHT_GATE_REASON_CODES` at `:203`.
- **`_check_machine`** (`:1461`) is reached from both `evaluate_dynamic_hard` (`:1811`, `legacy_load=False`) and `evaluate_night` (`:1856`).
- **Retry set.** `arm_retry.ZERO_CAPTURE_MACHINE_REFUSALS` (`:21`). Its registry comment (`:31`) says: "Explicit assignments are intentional: registry additions must force review."
- **SAMPLERS pin.** `SAMPLERS = "cpu_power,gpu_power,ane_power,thermal"` (`adapters/powermetrics.py:58`). The file is in `ESTIMATOR_CODE_PATHS` (`calibration_bracketing.py:206-210`). The writer's preflight compares `_current_estimator_code_sha256()` against the r7 artifact's `prospective_rederivation.estimator_code_sha256` (`validate_powermetrics_fiducial.py:396-398`) and raises `acceptance_artifact_stale`. **Editing SAMPLERS therefore makes every capture refuse at preflight.** It is also an "estimator-code rotation mid-campaign", which Revision 1 says voids the registration. A3 holds, and more strongly than stated.
- **Writer lifecycle.** Ledger `begin()` at `:2174`; `raw/` created at `:2228`; `pre_spawn = clock.stamp()` at `:2296`; the `_sampler_lifetime` block runs to teardown at `:2451`; then `post_parse = clock.stamp()` at `:2453`; artifact hashing follows.
- **Chain.** Writer rc 0 or 1 continues the night; any other rc stops the chain with the row unfinalized and the session OPEN for desk recovery (`calibration_derivation_only.zsh:266-279`).
- **Skipping of non-valid slots.** `registration_dry_run` skips them at `:215-216`, and so does `_select_members` at `:1076-1077`. The dry run's valid count comes from ledger dispositions, not bundles (`:231`).
- **`scored_reduce._check_window`** checks only the syntax of `bundle_sha256` (`_hex(...)`); it authenticates nothing behind it.

**A1–A8: AFFIRM, with the amendments below.**

**B1-F1 (MATERIAL): the bracket sites must lie outside the clock-anchor stamps, or the check perturbs B itself.**

- *What the stamps do.* `uncertainty_evidence.py:269-273` builds the anchor interval from `pre_spawn.monotonic_before_s` and `first_parse.monotonic_after_s`. `:1077-1081` uses `post_parse − pre_spawn` as controller coverage in the `clock_fit_span_insufficient` gate.
- *The defect.* A1–A7 and both seats locate the brackets loosely:
  - Sol says "before sampler start" and "after teardown".
  - Astra says "final pre-sampler check before `:2296`" and "post observation after teardown at `:2452`".
  
  Line `:2452` lies between `_terminate_powermetrics` (`:2451`) and `post_parse` (`:2453`). A pre-bracket placed after `:2296` but before the sampler spawn would lengthen the anchor interval. That changes the estimand B, and it changes it on every slot.
- *Required wording.*
  - The pre-bracket completes before `pre_spawn = clock.stamp()` (`:2296`). The best place is right after `raw/` creation (`:2228`).
  - The post-bracket runs only after the `with _sampler_lifetime(...)` block has exited, which is after `post_parse` (`:2453`) and after `active_sampler = None`.
  - The exceptional-exit post-bracket goes in the writer's own error path, after sampler teardown. It never runs inside the `with` block.
- *Test.* Assert, via the `WriterStage` hooks, that neither ioreg invocation's monotonic span overlaps `[pre_spawn.monotonic_before_s, post_parse.monotonic_after_s]`.

**B1-F2 (MATERIAL): the parser must handle the 60 s gauge refresh and the nested look-alikes (E2, E4).**

- *Staleness.* `InstantAmperage` is not instantaneous: it is a registry value refreshed every 60 s. A frozen gauge would otherwise pass forever. The parser must record top-level `UpdateTime` and fail closed when `observed_wall_epoch − UpdateTime > 180 s` (three refresh periods). That failure is a probe error, not a pass.
- *Top-level form.* Top-level properties print as `^\s*"Key" = value$`, with spaces around `=`. Nested dictionaries print as `"Key"=value` with no spaces, inside `{…}`. The parser matches only whole top-level lines of the single `+-o AppleSmartBattery` object. It must never read `ChargingCurrent`, `Current` or `FamilyCode`.
- *Two's complement.* Real evidence of unsigned printing of a negative value is the nested `FamilyCode = 18446744073172697098`, which is −536 854 518. The negative-`InstantAmperage` fixture stays labelled synthetic.

**B1-F3 (MATERIAL): the arm check must not inherit the kind-gated "skipped = pass" route.**

- *The route.* In `evidence_night.check`, `machine_quiet` and `corecaptured` run only when the `NIGHT_KINDS` row sets a flag. Otherwise they record `skipped`, and `skipped` is exempted from failure (`evidence_night.py:1373-1401`). An unknown kind (`row is None`) also skips.
- *The rule.* The battery check is unconditional:
  - It is never gated on a `NIGHT_KINDS` flag.
  - It is never added to the `("machine_quiet", "corecaptured")` skip exemption.
  - A `skipped`, missing or errored battery row fails the arm.
- *Test.* An unknown payload kind and a derivation kind both still fail on a charging fixture.

**B1-F4 (MATERIAL; a consumer gap seen by no seat and not by ex-30): the issuer cannot carry out P2's "retain, disclose, replace" at all today, and the obvious fixes open a cherry-pick bypass.**

- *Named sessions.* `_prepare_candidate` takes `session_ids` from the caller (`--registration-session-id`, `:1242`). Revision 5's structural checks are positional:
  - W1 = `session_ids[0]`, whose valid count must be ≥ 6 (`:1318-1331`);
  - there must be 2 or 3 sessions (`:1303-1310`);
  - sessions are named in ledger order (`:1311-1315`);
  - a W3 check covers the first two (`:1353-1362`).
- *Both routes refuse.*
  - If the confounded session is *named*, those positional checks count it as W1.
  - If it is *omitted*, addendum A-7 (`:1362-1382`) refuses issuance, because its valid same-epoch rows lie "outside this registration". The only exemption is `_registered_dispositions()`, and that accepts exactly one `DISPOSITION_DECISION_ID` and mechanism (`:1118-1140`), the n1/n2 diagnostics.
- *The danger.* Once a W1 is confounded, the pipeline refuses. That is fail-closed, not bad science. The danger is the improvised fix: an implementer who widens the A-7 exemption or lets the caller omit sessions creates the route by which a clean but unfavourable window can be dropped.
- *Required contract.*
  - The issuer classifies battery state **itself**, from raw bytes, for every derivation-kind session of the target epoch whose reservation follows the Revision 5 seal.
  - The caller names the confounded sessions separately (`--battery-confounded-session-id`).
  - The issuer refuses unless the caller's set **equals** the set it computes. It never trusts a label, and a clean session cannot be declared confounded.
  - Confounded sessions are dropped before the positional Revision 5 checks and are exempt from A-7 by that computed status, never by a registry row.
  - They are disclosed in `derivation_notes.battery_confounded_sessions`, with the session id, failing slot ids, reason codes and raw-artifact hashes. No B value appears there.
- *The dry run* uses the same computed classification and prints `battery=confounded|clean|evidence_missing` per session.

**B1-F5 (MATERIAL): harvest order.**

- *The defect.* W1's first harvest step is the pin-free cadence report (`scripts/calibration_cadence_report.py`). It is a stop decision ("no W2") that reads raw plists, and it has no battery awareness. A5 omits it (Astra listed it).
- *The rule.*
  1. The battery classification runs first, by the shared validator over all slots.
  2. The cadence report and the count-only dry run follow.
  3. For a confounded window, the cadence and count results are diagnostics that trigger neither STOP nor CONTINUE. Its replacement faces both stops afresh.

  The cadence tool itself need not change. The harvest procedure and the addendum fix the order.

**B1-F6 (NIT): the consumer inventory.**

- *Readers outside A5.* Other readers of derivation `b_fiducial_s` exist: `epoch_equivalence_check.py`, `reissue_calibration_acceptance.py`, `whole_window.py`, and the `paper_*` scripts. Revision 5 takes no equivalence look, and the paper scripts target historical captures, so none is a live bypass for W1.
- *Required statement.* The final text should say so and bind future readers of Revision 5 rows to the shared validator.
- *Placement.* The lower candidate loader and `evaluate_calibration_bracket` (`calibration_bracketing.py:1542/1965`) serve bracketed G2-a captures, never derivation windows: Revision 5 says derivation observations "never bracket endpoints". They belong in BFG-S.
- *Pin movement.* Editing `calibration_bracketing.py` moves pinned source digests in the frozen `configs/campaigns/d117_floor_qwen25_7b_v3/arm_readiness.sources/*.json` (`reason-code-coverage.json` lists it). Transaction packs must re-freeze. Moving the edit to BFG-S keeps that out of W1's path.

**B1-F7 (AFFIRM A7, with a disclosed limit).**

- *The miss window.* Brackets fall at 600 s cadence around captures of ≤ 480 s, so a charging episode that starts and ends inside one capture escapes both brackets. A 1 % top-up at ≈1 A lasts about 5 min, so such an episode is plausible.
- *No integral check.* `AppleRawCurrentCapacity` did not move while ≈20 mAh flowed in (E4), so a capacity-delta integral check is **not** available without characterization. Do not adopt it.
- *The disclosure.* "Brackets cannot exclude a charging excursion shorter than one capture" belongs in the addendum and the harvest record.

**Perturbation, positive result.**

- One ioreg read costs ≈10 ms of CPU and does not poll the gauge (E2, E4).
- At the sites fixed in B1-F1, a read falls outside the sampler's life and outside the anchor stamps.
- The C3 and arm reads come before the chain's 600 s settle.
- I find no perturbation path beyond B1-F1.

## B2 — split

**Affirm P1** (split by window kind), with these contents:

- **Before W1 arms, merged:** BFG-D, which is A1, A2 (C3, `evidence_night.check`, `publish_install` pre-rename, the installer's `validate_install`, and the `arm_retry` and cold-gate registries), A4 (writer brackets at the B1-F1 sites), and A5 restricted to the derivation consumers (`registration_dry_run`, `_prepare_candidate` with the B1-F4 contract, and the cadence-first harvest order). Then the addendum PR, then #418 sealed, per P5.
- **Before any non-derivation window arms (quiet-predicate evidence, calibration bracket, G2-a, scored), merged:** BFG-S, which is A6 plus the bracket-consumer half of A5 (B1-F6).
- A t0-only PR closes nothing, and neither PR alone is labelled as closing BATTERY-FLOAT-GATE-01.

## B3 — registration

**An addendum is required before W1.** The whole-window exclusion changes Revision 5's "Every valid resolved member is retained", and Revision 1's exclusions list names only (a)–(c).

**P2 is amended, not affirmed.** Four defects:

- **(i) Unused slots would confound every truncated window.** P2 says "If any slot's bracket is missing … the whole window is battery-confounded". A slot recorded `slot_unused reason=window_exhausted` never runs the writer (`calibration_derivation_only.zsh:226-241`), so it has no bracket, and P2's text would confound every truncated window. The rule must cover only slots whose writer ran past ledger `begin()`.
- **(ii) "Replaced once" and "second consecutive" are ambiguous.** Is the limit per window position or per epoch? Fix it at one replacement per epoch.
- **(iii) Stop order is unspecified.** See B1-F5.
- **(iv) Confounded B values need a reading rule.** They must stay unread until issuance is decided, and afterwards they are diagnostics only.

**S2 ruling.** One replacement, bounded to one per epoch. This is admissible because the confound is decided from instrument state, blind to B and before any B read. The count-triggered W3 is not a replacement.

**Proposed text, replacing P2:**

> **Addendum A-R5b — battery float (directive #421), prospective, before W1.** A derivation window of this registration is admitted only if a battery observation passes at the arm check, immediately before publication, and at t0. An observation passes when one reading of `ioreg -r -c AppleSmartBattery`, whose gauge `UpdateTime` is no more than 180 s old, shows top-level ExternalConnected = Yes, IsCharging = No and |InstantAmperage| ≤ 200 mA, with unsigned 64-bit values of 2^63 or more read as value − 2^64. A failing observation postpones the arm and is never waived. Every slot whose capture writer passed ledger reservation records one raw observation completed before its sampler is spawned, and one after its sampler has been torn down and its last clock stamp taken. Both are hashed into that slot's evidence. Before the cadence report, the count-only dry run or any B value is read, the window is classified from those raw bytes alone. If any such slot's observation is missing, unparseable or failing, the window is battery-confounded. A confounded window's observations are not members and count toward no stop or valid-slot rule. Its cadence and count results are diagnostics only. Its B values are not read before issuance is decided. It is retained in the ledger and listed by session, slot, reason and raw-artifact hash in the candidate's derivation notes. A confounded window is replaced by one fresh window under the unchanged protocol, at least 6 h after the confounded window and at least 6 h before the next. The replacement takes the confounded window's place in the W1/W2/W3 sequence and faces its stops. At most one replacement is permitted per epoch; a second confounded window stops the epoch and returns it to council. Brackets cannot exclude a charging excursion shorter than one capture; this limit is disclosed. Nothing here changes the pulse protocol, the estimator code, the sampler set, the slot shape or any threshold.

**Landing.** #418 merges as ruled. A-R5b is appended as its own labelled amendment. Its digest, taken over the whole file, replaces the arm-notice pin. The issuer's `preregistration_sha256` check (`:1227`) then binds it automatically.

## B4 — threshold physics (P3)

**Affirm P3 for powermetrics-only windows.** The ≤ 200 mA bound is a gross screen of charge-heat state. The SoC rails do not carry the charge current, and the settle and thermal gates stay in force.

**Amend the wall-meter clause.** The gauge cannot certify a wall-meter window at all:

- *Resolution.* It reports whole mA refreshed every 60 s (E4). 1 mA at 12.95 V is 13 mW, which is 6.2 J over a 480 s capture. That is already above the ≈5 J claim-side bar.
- *Consequence.* WALL-METER-GAIN-01 must bound the battery's contribution from the wall side, or with the battery path excluded by design, not by a tighter InstantAmperage bound. An example of a wall-side method is a same-window idle wall reading against a float reference.
- *Registration.* This is a registered obligation before any wall-meter window.

## B5 — P4

**AFFIRM.**

- The frozen plan enters the derivation chain only as the reservation's `--plan-id`, `--plan-sha256` and `--plan` (`calibration_derivation_only.zsh:187-205`; generator `:564-601`). It does not touch the pulse capture.
- Its sha256 at c6814dd8 is `9ab4776f3c416284d6d01a5a49587eedcdfbcb8ef61428cdc1046e9b9d74a072`. That value belongs in the notice.

## B6 — missed by all

1. B1-F1: anchor-stamp placement.
2. B1-F2: 60 s staleness and nested look-alikes.
3. B1-F3: the arm "skipped = pass" route.
4. B1-F4: A-7 and the positional issuer, with the anti-cherry-pick classification.
5. B3(i): unused slots.
6. B4: the gauge's resolution floor.
7. Live fact: at 14:35 the battery was charging 0.58 A at displayed 100 % with `FullyCharged = No`. **Expect arm refusals until it floats.** Whether it then stays floating for 150 min is unobserved. The first W1 arm attempt is the first real test of the top-up cadence.
8. **Record, do not gate.** The raw bytes already hashed carry `Temperature`, `NotChargingReason`, `ChargerInhibitReason` and `UpdateTime`. The harvest record should quote the first two per slot. Adding a battery-temperature gate needs characterization first.

## Test obligations (defect-shaped, production call sites)

1. **Anchor non-overlap.** Drive `validate_powermetrics_fiducial.main` in logical-test mode with an injected ioreg runner that records monotonic spans. Assert that no span intersects `[pre_spawn, post_parse]`. Also assert that `instrument_evidence.json`'s anchor stamps are byte-identical with the runner stubbed to take 0 s and to take 2 s.
2. **Staleness.** A fixture with `UpdateTime` 181 s old refuses through `night_gate.evaluate_night`, as a probe error. At 179 s it passes.
3. **Look-alikes.** A fixture where the top-level `InstantAmperage` is absent but `ChargingCurrent=0` is nested refuses.
4. **Arm bypass.** `evidence_night.check` with an unknown payload kind, and with a derivation kind, plus a charging fixture → `armable = false`.
5. **Issuer.**
   - `_prepare_candidate` with sessions [confounded W1, W1′, W2]: the caller's confounded set must equal the computed set.
   - A clean session declared confounded refuses.
   - A confounded session omitted refuses.
   - W1′ is treated as W1 in the positional checks.
   - A-7 does not refuse the disclosed confounded rows.
6. **Unused slots.** A session with `window_exhausted` unused slots and clean brackets on every run slot classifies clean.
7. **Pin regression.** `SAMPLERS`, `protocol_v3.json`, the four `ESTIMATOR_CODE_PATHS` files and the chain bytes are byte-identical to c6814dd8.

## Phase 1 verdict

**AFFIRM** A1–A8, P1, P4 and S2 (one bounded replacement), each with the amendments above. **AMEND** P2 into the A-R5b text above, and the wall-meter clause of P3. **No BLOCKER** in the synthesis: every defect found fails closed at issuance or is a placement rule the final texts must pin. B1-F1 would become a BLOCKER if the final texts carried Astra's "after teardown at :2452" site.

<!-- Phase 2 appended below -->

## Phase 2 — refutation of the judge's ruling

**Ruling read.** `/Users/edr/code/JouleWise-wt-ed17a643-cg-judge/docs/process_traces/2026-09-25-activation-ed17a643/10-coldgate-packet-bfg/20-coldgate-fable-bfg-ruling.md`: 40 735 bytes, sha256 `11e6d30cf5f3b3b552030bbc43a0b1fb15f7fac42117918ac2efad28e030211a`. It appeared at 14:44:37 PDT, and its size was unchanged over the following 60 s.

**New executed evidence for Phase 2:**

| # | Command | Result |
|---|---|---|
| E6 | `ioreg -r -c AppleSmartBattery -w0` at epoch 1790372774 (≈14:46 PDT) | `"IsCharging" = No`, `"InstantAmperage" = 0`, `"FullyCharged" = Yes`, `"CurrentCapacity" = 100`, `"UpdateTime" = 1790372745`, **`"AppleRawCurrentCapacity" = 7591`** |
| E7 | `sed -n 1150,1215p joulewise/uncertainty_evidence.py` | The v3 anchor sets `m0 = pre_spawn.monotonic_before_s` and `k_pre_spawn = pre_spawn.monotonic_before − resolution − m0 + exact_elapsed_ns[0]`, the causal lower bound fed to `_eliminate_alpha_v3(…, k_pre_spawn, k_first_parse)` |
| E8 | `sed -n 3024,3038p joulewise/calibration_ledger.py` | Exact-set checks `set(manifest_artifacts) != set(MANIFEST_BOUND_ARTIFACTS)` and `set(evidence_artifacts) != set(EVIDENCE_BOUND_ARTIFACTS)`. This confirms the ruling's F-1 |
| E9 | `ioreg -r -c AppleSmartBattery` without `-w0`, to a pipe | Longest line 9 179 chars, so no truncation. Exactly one top-level `"InstantAmperage" = ` line |

Two consequences of E6:

- **Float is now observed for the first time.** This supersedes ruling V18 and summary line 7. One read is not yet the two reads ≥ 5 min apart that §7.7(5) requires.
- **The coulomb counter is step-updated.** It read **7516 mAh** in the judge's 14:33 read (739 mA) and in every one of my reads through epoch 1790372255 (≈14:37:35; 579–596 mA). That is ≈4.5 min at ≈0.6 A, so ≈45 mAh of true inflow with no change in the counter. Then it **stepped +75 to 7591** by 14:46, when `FullyCharged` had flipped to Yes.

### Item-by-item

**§0 disclosure, §1 verification, §2 hygiene: AGREE.**

**§3.1 V1–V18: AGREE.** V18 is superseded by E6.

**F-1 (inventories): AGREE.** Verified (E8). The cure — a `battery_float` key inside the hashed `instrument_evidence.json`, with raw files chained through `raw_stdout_sha256` — is the right shape.

**F-2 (cadence report first): AGREE.** It matches my B1-F5.

**F-3 (arm sites unconditional; `validate_install`; `_derive_power`): AGREE.** It matches my B1-F3.

**F-4 (one refusal code; probe failure = `night_probe_error`): AGREE.**

**F-5 (coulomb-counter integral screen): BLOCKER, as to the registered text and the summary for Ed.**

- *The claim.* The ruling says ΔQ = post − pre "is the net charge into the pack between the two brackets", "the same 200 mA bound expressed as an integral". §6 says "The integral screen of F-5 is added so the bound also holds between brackets". A-R5b's Disclosure says "Two observations bound the slot's endpoints and its net charge". Summary line 5 says "charging between the two readings is caught too".
- *The evidence against it.*
  - E4 and E6, with the judge's own 14:33 read, show the counter did **not** move during ≈4.5 min of 0.58–0.74 A charging, about 45 mAh of inflow. That exceeds the ruling's own 28 mAh allowance per slot.
  - It then stepped +75 mAh at the full-charge transition.
  - In the regime that matters on this machine now (topping up at a displayed 100 %), ΔQ reads 0 across a charging interval.
- *The consequence.*
  - The screen is not an integral. It passes a slot that charged throughout, provided the flip to full does not fall inside the slot.
  - It can also confound a clean slot on a gauge re-estimation step. That step is outcome-blind, so it causes waste, not bias.
  - Keeping the check adds refusals and never admits anything. The **text**, however, would register a false statement about what the screen detects. Ed's general principle in #421 makes a disclosure that bears on whether a number is true mandatory, so an untrue disclosure is a science defect, not a wording nit.
- *Required cure* (either option is acceptable; both need the disclosure fixed):
  - (a) **Record, do not gate.** Keep `apple_raw_current_capacity_mah` in the record and report ΔQ per slot as a diagnostic. Drop the charge-delta clause from the Window verdict and from test 7.
  - (b) **Keep it as an extra refusal.** Keep the clause and the test.
- *Replacement disclosure text, for either option:* "`AppleRawCurrentCapacity` is updated by the gauge in steps, not continuously. On 2026-09-25 it held at 7516 mAh through about 4.5 min of 0.58–0.74 A charging (about 45 mAh), then stepped to 7591 mAh when charging ended. Its difference across a slot therefore does not bound the net charge in between. A charging excursion that begins and ends between a slot's two observations is not detectable, and this is disclosed."
- *Other fixes needed.*
  - Strike §6's sentence "so the bound also holds between brackets".
  - Rewrite summary line 5 as: "The gauge's mAh counter is recorded, but it updates in jumps, so it does not catch charging between readings; that gap is disclosed."
  - The A7 "as amended" residual-limit sentence ("a charge-then-discharge excursion that nets to ≤ 28 mAh … is invisible") understates the gap in the same way. Replace it with the text above.

**F-6 (live logger must be dead): AGREE.**

**F-7: AGREE.** E2 and E4 show `Amperage` = `InstantAmperage` on every read.

**F-8: AGREE**, with one addition: the procedural gate should also log `UpdateTime`. See the staleness item below.

**F-9 and §7.3 writer sites (perturbation): BLOCKER, as to the site text.**

- *The claim.* §7.3 places the pre-bracket "after `:2228` … and before `:2297` (spawn)", and the post-bracket "after `:2452` (teardown)". A-R5b says "immediately before its sampler is spawned and one immediately after the sampler is torn down". F-9 concludes that the brackets lie "outside the measured interval". That conclusion holds only for the sampler's plist stream, not for the clock stamps the estimator uses.
- *The pre-bracket.* `pre_spawn = clock.stamp()` is `:2296`, so "before `:2297`" admits a site between `:2296` and `:2297`. The v3 anchor uses `pre_spawn.monotonic_before` as the origin `m0` and the causal lower bound `k_pre_spawn` (E7). A ≈10 ms ioreg call there, or up to the 10 s timeout, widens the feasible clock-offset set for **every slot**. That can enlarge B, the registered estimand.
- *The post-bracket.* `post_parse = clock.stamp()` is `:2453`, so "after `:2452`" lands before it. That lengthens `post_parse − pre_spawn`, the controller-coverage input to the `clock_fit_span_insufficient` gate (`uncertainty_evidence.py:1077-1081`). It also changes the serialized stamps.
- *Why BLOCKER.* The mandate says the text must be executable without choosing. A faithful implementer can pick a perturbing site. A-R5b also asserts "estimator-code pins are unchanged", which is true of the bytes while the estimator's inputs move.
- *Required cure.*
  - §7.3: "pre-observation completes after `:2228` and **before `pre_spawn = clock.stamp()` (`:2296`)**; post-observation runs **after the `with _sampler_lifetime(...)` block has exited** (after `post_parse`, `:2453`, and `active_sampler = None`)".
  - A-R5b: replace "immediately before its sampler is spawned … immediately after the sampler is torn down" with "before the capture's first clock stamp is taken and after its last clock stamp is taken, so that neither observation falls inside the interval the clock anchor is computed from".
  - Add a test: via `WriterStage` hooks and an injected probe that records its monotonic span, no ioreg span intersects `[pre_spawn.monotonic_before_s, post_parse.monotonic_after_s]`. Then, with the probe stubbed to take 0 s and to take 2 s, the serialized clock stamps' *differences* and `b_fiducial_s` are identical under the logical test clock.
- *`finalize_abandoned` (NIT).* §7.3 also attempts the post-observation inside `finalize_abandoned`. That function also runs at `:2326` and `:2344`, *inside* the `with` block while the sampler is alive. An abandoned row writes no `instrument_evidence.json`, so the observation cannot enter the hashed chain there. Either drop it, or have it write only the raw file, not the `battery_float` key, and state that it proves nothing. The window verdict is `evidence_missing` either way.

**§3.3 A1: AGREE, plus a MATERIAL gap (staleness).**

- *The gap.* The gauge refreshes every 60 s (E4: `UpdateTime` 1790372085 → …145 → …205; reads in between returned identical values).
- *The consequence.* §7.1 records `UpdateTime` but never gates on it. A stalled gauge — one whose `UpdateTime` stops advancing — would pass a frozen "IsCharging = No" indefinitely.
- *Cure.* A-R5b and §7.1 add: "an observation whose `UpdateTime` is more than 180 s before the observation's wall time is not a pass (probe error)". §7.4 adds a field `update_age_s`. §7.6 adds a test: 181 s refuses as `night_probe_error`, 179 s passes.

**A2–A4, A6, A8: AGREE**, with A4 as amended by F-9 above.

**A5 (all-slots clarification incl. `window_exhausted`): AGREE.** It cures my B3(i).

**A7: AGREE** on no polling. Its "as amended" residual sentence falls under F-5 above.

**Bypass audit (the six consumers) and §7.6 test 6: MATERIAL. As written, the issuer cannot carry out A-R5b's replacement, and the natural repair creates a cherry-pick route.**

- *What the ruling says.* Test 6 says `_prepare_candidate` **refuses** before `_select_members` when a session is confounded. A-R5b says a confounded window is **retained, excluded and replaced**, and issuance then proceeds.
- *Why that cannot work at c6814dd8.*
  - Sessions come from the caller (`--registration-session-id`, `:1242`).
  - Revision 5's checks are positional: W1 = `session_ids[0]` with ≥ 6 valid (`:1318-1331`), 2 or 3 sessions (`:1303-1310`), ledger order (`:1311-1315`), and the W3 check (`:1353-1362`).
  - If the confounded session is named, the ruled validator refuses.
  - If it is omitted, A-7 (`:1363-1382`) refuses on its valid same-epoch rows. The only exemption, `_registered_dispositions()` (`:1118-1140`), accepts a single `DISPOSITION_DECISION_ID` and mechanism.
  - So after any confounded window, nothing ever issues. The implementer will improvise, either by adding rows to `observation_dispositions.json` or by relaxing A-7. Both give the caller the power to drop a *clean* window.
- *Required cure* (add to §7.5 and to BFG-D):
  - The issuer computes the battery verdict itself, from raw bytes, for **every** derivation-kind session of the target epoch in the ledger after the Revision 5 seal.
  - The caller names confounded sessions in a separate flag (`--battery-confounded-session-id`), and the issuer refuses unless that set **equals** the computed set.
  - Confounded sessions are removed before the positional Revision 5 checks, and are exempt from A-7 by computed status only.
  - They are disclosed in `derivation_notes.battery_confounded_sessions` (session, slots, reasons, raw digests; no B).
  - **Test 6 becomes:** [W1 confounded, W1′, W2] issues with W1′ as W1. Declaring a clean session confounded refuses. Omitting a confounded session refuses. Naming a confounded session as a registration session refuses.
  - `registration_dry_run` prints the computed per-session verdict.

**NIT (pin movement).** The §3.3 consumers in `calibration_bracketing.py` (`_load_calibration_candidate_unbounded`, `evaluate_calibration_bracket`) serve bracketed G2-a captures, never derivation windows: Revision 5 says derivation observations "never bracket endpoints". Editing that file moves the source digests pinned in the frozen `configs/campaigns/d117_floor_qwen25_7b_v3/arm_readiness.sources/*.json`. Either move those two sites to BFG-S, or state in BFG-D that transaction packs must re-freeze.

**§4 B2 (P1, two PRs by window kind; the before-W1 and before-non-derivation contents): AGREE.**

**§5 B3.** Addendum needed: AGREE. S2, one bounded replacement: AGREE. Count handling: AGREE. Landing after #418 as its own labelled amendment: AGREE. The A-R5b text has four defects:

- **BLOCKER:** the Disclosure paragraph and the charge-delta clause. See F-5.
- **BLOCKER:** the "immediately before … spawned / after … torn down" wording. See F-9.
- **MATERIAL: the replacement bound is ambiguous.**
  - The text says "replaced once" and "A second **consecutive** confounded window stops the epoch". Under W1 ✗, W1′ ✓, W2 ✗, W2 is not consecutive with W1, so the text permits a second replacement. §5's own gloss says "one replacement, then stop".
  - The text also never says where the replacement sits in the W1/W2/W3 sequence, or that the ≥ 6 h spacing to the *next* window applies.
  - Cure: "At most one replacement window is permitted per epoch; any further confounded window stops the epoch and returns it to council. The replacement takes the confounded window's place in the W1/W2/W3 sequence, faces that window's stops, and keeps Revision 5's ≥ 6 h spacing to its neighbours."
- **MATERIAL:** add the staleness clause (A1 above).

**NIT, A-R5b and §7.3: writer behaviour on a failing pre-observation is unstated.** Record and continue. Add no new writer exit path: rc ≥ 2 would leave the session OPEN for desk recovery, and the window verdict decides anyway. Say so.

**§6 B4.** 200 mA adequate for powermetrics-only windows: AGREE. The wall-meter energy-bound arithmetic (0.8 mA, the 46.6 J counter step) and "no wall-meter window is claim-bearing until WALL-METER-GAIN-01": AGREE. The sentence "The integral screen of F-5 is added so the bound also holds between brackets" is false. Strike it (F-5).

**§7.1: AGREE**, plus staleness. The quoted-key and top-level-indentation rule suffices against the nested compact-form look-alikes (`"ChargingCurrent"=583`, `"Current"=4990`) and against `AppleRawExternalConnected`. `-w0` is unnecessary (E9).

**§7.2: AGREE.**

**§7.3: BLOCKER** on the writer sites (F-9). The BFG-S controller wording ("never inside `sampling_started`…`sampling_stopped`") needs the same stamp-based precision before BFG-S is built, but it does not block W1.

**§7.4: AGREE**, plus `update_age_s`.

**§7.5: AGREE**, plus the issuer contract above (MATERIAL).

**§7.6.**

- Tests 1–5 and 8: AGREE.
- Test 6: MATERIAL, rewrite as above.
- Test 7: goes with F-5. Either drop it, or keep it but label the property it tests a synthetic rule, not a physical integral.
- Missing tests: anchor non-overlap (BLOCKER cure) and staleness (MATERIAL).

**§7.7 W1 prerequisites: AGREE on the order.** Two notes:

- Prerequisite 5 now has its first float read (E6, `UpdateTime` 1790372745, `InstantAmperage = 0`). A second read ≥ 5 min later is still needed.
- Prerequisite 2 must include the F-9 site correction and the issuer contract before BFG-D is merged.

**§8 B5 (P4, calibration plan `9ab4776f…a072`): AGREE.** This is independently verified (Phase 1 B5).

**§9 B6: AGREE**, except the F-5 item, which rests on a false premise.

**§10: AGREE.**

**§11, the plain summary for Ed.**

- Line 5 is false (F-5); replace it as given above.
- Line 7 is superseded: float was first seen at 14:46 PDT, 0 mA, not charging, with one read so far.
- Lines 1–4, 6 and 8: AGREE.

### Phase 2 verdict

**Two BLOCKERS.** Both are fixes to text, each a few sentences, and neither reopens a design decision:

1. **F-5.** The registered disclosure and the summary for Ed claim that the coulomb counter bounds net charge between readings. Executed evidence shows it is step-updated: it held flat through ≈45 mAh of charging, more than the 28 mAh allowance per slot.
2. **F-9 / §7.3 / A-R5b.** The bracket-site text admits placements inside the clock-anchor stamps (`pre_spawn` `:2296`, `post_parse` `:2453`). That would change the estimator's inputs on every slot.

**Three MATERIAL findings:**

1. Issuer contract for confounded sessions: A-7 and the positional checks, and the cherry-pick guard.
2. Replacement-bound ambiguity ("second consecutive").
3. `UpdateTime` staleness gate.

**Two NITs:** `finalize_abandoned` observations; `calibration_bracketing.py` pin movement.

Everything else: AGREE. W1 may arm only after the prerequisites of §7.7 **with these corrections folded into BFG-D and A-R5b**.
