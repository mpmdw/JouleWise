# R16 condition waits implementation: Opus cold review

2026-11-08. Cross-family cold review (Opus 5.5) of Sol 6.1's build.

| | |
|---|---|
| Target | `align/2026-11-08-condition-waits-impl` @ `4d7e5f9a9` (planned integration item 5 on `align/2026-11-08-v4-r11`, RUN_STATE 228) |
| Authority | R16 in `origin/main:RUN_STATE.md` item 226; `docs/align/v4/CONDITION-WAITS-AGREEMENT.md` on `align/2026-11-08-condition-waits-opus`; `docs/perf/SPEED-TOOLBOX.md` on `main` (markers only, no computation in a window) |
| Integration base | v4 head `48a4d1d76`, as briefed. The line has since moved to `1a2574b49` (meter probe ends before the quiet dwell). That change is small, but it adds to the session conflicts below. |
| Witnesses | `tests/align/test_condition_waits_opus_witnesses.py`: 7 failing-first tests, one per HIGH. Each fails on the target and is the acceptance check for its fix. F5 runs only after the merge onto the v4 head. |
| Blinding | I read code, synthetic tests, fixtures and docs only. I read no energy, residual, score, alarm or restricted path. The native probes ran on the Air with no study data. |

## Verdict: **HOLD**

**Safety.** The safety core is right:
- R16 can never arm at the ceiling or outside the band.
- The band is two-sided.
- Q is bound to R1's final mode and its sensor and fan picks.
- Nothing runs inside a window.
- With no `condition_waits_policy.json`, the code is inert: the driver, arm, dwell and session keep their current behaviour.

**Why HOLD.** On real hardware, the active (`condition`) path cannot release at all, for four independent reasons (H1-H4). Each one fails closed, so none of them harms the science, but together they make R16 unusable.

Registering even the fallback (`incumbent_shadow`) policy changes the incumbent arm (H1, H5). That breaks R16's own fallback clause: "today's cool-down applies, with the band print-only".

Two more problems block the path to an active policy:
- **Integration with the v4 head (H6).** The arm now rebuilds the next-arm packet itself, and the rebuilt packet carries no receipt binding.
- **CW-1 qualification (H7).** As built, CW-1 cannot qualify.

**Path to ADMIT.**
- **Item 5 can merge as INERT code once three things are done:**
  1. M1 is fixed (the impl branch fails `tests.hazards.test_refusal_allowlist` by itself).
  2. The six merge conflicts are resolved (§4 shows a working resolution).
  3. L5 (test drift) is fixed.
- **That merge must come with a written prohibition:** no `condition_waits_policy.json`, in either mode, until H1-H7 are fixed and a native dry arm passes.
- **W1 then registers today's cool-down with no policy file.** The print-only band that R16's fallback asks for cannot be recorded without a sampler that leaves the start state alone (H1/H4). The lead should either log that as a public deviation or have a fixed low-cost shadow logger ready before W1.

## 1. Fidelity to R16

| R16 element | Finding | Where |
|---|---|---|
| Never arm at the ceiling | **Holds.** `expired = now-start >= 1800 s` adds `ceiling`, so `band_ready` is false. Enforcing mode forces `ready=False`, and `status='not_ready'` closes the attempt. The arm returns NULL when the joint state is not ready after the dwell, and again when the GO recheck fails. A release just before 1,800 s followed by a GO tick at or after 1,800 s also refuses. | `condition_waits.py:353-364`; `hazards/arm.py:316-317`, `:337-338` |
| Arm outside the band | **Holds.** Every channel is checked again at GO, and failed reads are kept as failures. | `condition_waits.py:307-339`; `condition_waits_native.py:385-389` |
| Two-sided ±δ around Q | **Holds**: `abs(v-q) > delta` for both the fast and slow channels. G0 and G1 stay one-sided, as R16 says. | `condition_waits.py:307-310` |
| Q tied to R1's final mode and sensors | **Holds structurally.** `validate_q` requires a 1,200 s qualified reference in mode 0 or 2. The kit refuses a Q whose `ac_powermode`, `s_fast`/`s_slow` or fans differ from the final R1 slots. **LOW L1:** `q.r1_sha256` is never compared with the actual final R1 digest. Only CW-1's own copy is compared, which makes the check self-referential. | `condition_waits.py:43-86`; `scripts/align_v4_kit.py` (build_files hunk) |
| G0 slope rule | **Holds, but stricter than G0** (L2). A single non-finite slow reading anywhere in the 60 s window blocks release for 60 s. `thermal_gates.slow_slope` skips bad rows under its 90 % coverage rule instead. | `condition_waits.py:152-160` vs `thermal_gates.py:281-292` |
| Fan, idle power, display, OS/PM, battery | Implemented as agreed (D7, D8). The power predicate is unreachable natively (H2) and so is the battery predicate (H4). | `condition_waits.py:314-337` |
| 180 s stability shared with the guard's clean run | **Holds.** Both suffixes end at `now` on one trace, and the guard's clean run is re-checked on the attempt's own `Dwell` copy. | `condition_waits.py:257-275`, `:347-349` |
| Floor of 300 s after the last disruptive work | **Holds conservatively.** In the arm the floor anchors at the start of the arm dwell, which is later than finalize, harvest or offload. **MEDIUM M2:** the display floor also restarts at the arm dwell, so it does not "overlap the cool-down" (P2/D9). Every condition-mode GO is therefore at least 300 s into the dwell, against about 180-210 s for the incumbent guard. | `condition_waits_native.py:352-353`; `condition_waits.py:276-288` |
| One retry after an ambient check, then the lead | **Partial (MEDIUM M3).** Attempt 2 requires an ambient-check digest. But `attempt_number` comes from the install inputs, so a fresh install with `attempt_number: 1` after a `not_ready` makes a third attempt with no lead decision. Nothing reads earlier `not_ready` receipts. | `condition_waits_native.py:469-471`; `condition_waits.py:192-201` |
| `quiet_start_state` binds the receipt digest | Implemented for the *supplied* packet. It cannot work against the v4 head's *rebuilt* packet (H6). | `v4_cadence.py` (R16 hunk) |
| P2: guard READY, nothing extra after READY | Holds: no sleep after READY. But see M2. | `hazards/contention.py:680-687` |
| Fallback: today's cool-down, band print-only | **Does not hold (H5).** | §2 |
| R18 (F-G4): a new guard starts in shadow mode | **MEDIUM M4.** The condition mode adds refusing arm guards (`condition_waits`, `condition_waits_clock`, stale GO). Promotion is gated on the CW-1 guard replay, but not on the R18 shadow-exposure bound. | `hazards/arm.py:213-226`, `:316-348` |

## 2. HIGH findings (each has a failing-first witness)

### H1. The setup census on every tick makes the arm guard hold itself and breaks the observer budget. Affects both modes.

**What happens.** `registered_arm.setup()` runs `external_volume.census()` plus `arm_check()` on every 1 Hz sample: one `mount` and one `diskutil info` per local mount. It is called from `NativeSampler.sample`.
- Location: `condition_waits_native.py:452-457`, called at `:215`.
- On the Air, one call takes 0.70-0.90 s of wall time and 0.39 CPU-s in child processes.
- 20 calls added 4.24 CPU-s to `storagekitd` and 0.89 CPU-s to `diskarbitrationd`. Both run outside the arm's process tree.

**Native witness** (Air, 30 s contention intervals, the real `contention.interval`, limit 0.05):

| Interval | `storagekitd` |
|---|---|
| Baseline | not listed |
| R16 setup at the arm's ~1.9 s period | **0.0904 CPU-s/s, over the limit** |
| Baseline afterwards | not listed |

**Consequences.**
- **Condition mode:** the guard is never clean, so the arm runs to the 1,800 s ceiling.
- **`incumbent_shadow` mode:** the sampler runs in the dwell all the same. The native `Dwell` therefore never reaches READY, and the incumbent arm refuses at 2,700 s.
- **Start state:** the same load (diskutil, storagekitd, APFS) perturbs the very power and temperature that R16 measures.
- **Observer budget:** even without the census, the five subprocesses spawned per sample (`ioreg` twice, `pmset`, `pgrep`, `sysctl`) cost 0.026 CPU-s/s. That is five times CW-1's ≤ 0.005 budget (H7a).

**Witness:** `F1PerTickSetupCensus`: 10 censuses in 10 samples.

**Fix:**
- Run the setup and volume check once at the start of the attempt and once at GO, never per tick.
- Cache `boot_id`.
- Replace the per-tick spawns with in-process IOKit and SMC reads, or reduce the tick work to the SMC plus one `ioreg`.
- Measure the observer tree cost natively before CW-1.

### H2. The PowerStream rejects real powermetrics output, so the power and PM predicates can never pass.

**What happens.** `PowerStream.accept` requires the cumulative endpoint (`last_end + elapsed_ns`) to stay within 0.1 s of the plist `timestamp`.
- Location: `condition_waits_native.py:51-59`.
- The plist `<date>` has whole-second resolution. See `joulewise/adapters/powermetrics.py` `TIMESTAMP_DERIVATION` ("native whole-second constraints") and `tests/fixtures/d117_v2_production/strict_seed_bundle/raw/powermetrics_idle.plist`, whose dates are whole seconds and whose `elapsed_ns` values vary.
- So the difference wanders through [-1, 1) s. The reader thread raises "timestamp discontinuity" within about a minute and stops.
- From then on there are no `power_intervals`, `pm_state` is None, and `power` and `os_or_pm` fail on every row. CW-1's power reference fails too.

**Why the existing test misses it.** The existing test feeds an exact `elapsed_ns = 1e9` with integer timestamps (`test_condition_waits.py:441-451`).

**Witness:** `F2PowerStreamWholeSecondTimestamps`: a 1 Hz stream of 1.001/1.004 s intervals dies.

**Fix:** use the D-078 whole-second set-membership derivation from `adapters/powermetrics.py`. Anchor once and advance by `elapsed_ns`. Treat the native date only as a `[floor, floor+1)` constraint, with a rate tolerance.

### H3. The arm's tick cadence defeats the 99 % per-second coverage, so the native arm never releases.

**What happens.**
- `run_dwell` sleeps `min(tick_s, remaining)` *after* `on_tick` (`contention.py:680-687`). The joint sample period is therefore 1 s plus the cost of the clock sample and the R16 sample.
- The display floor, the stability suffix and the slow slope require that at least 99 % (or 90 %) of the nominal one-second cells be occupied (`condition_waits.py:137-149`, `:286-287`, `:347-348`).
- Any period above 1/0.99 ≈ 1.0101 s fails.

**Evidence.**
- Probe with the repository's native-arm harness (`tests/align/test_condition_waits_arm.py`): 5 ms or 10 ms per sample GOes at 300 s. **20 ms or more per sample never releases**, and the arm refuses at 1,800 s with `display_floor` and `physical_stability`.
- The native sources alone cost about 36 ms of wall time per sample on the Air, before H1's census.
- `run_attempt` and `execute_kit` sleep to a one-second grid, so the preliminary receipt and CW-1 would pass while the arm fails. Neither would catch this.

**Witness:** `F4ArmTickCadenceDefeatsCoverage`: a 50 ms sample does not GO.

**Fix:** with a joint gate present, tick `run_dwell` on a fixed deadline grid (`next_tick += 1 s`), or define coverage against the actual cadence (gaps ≤ 2 s plus a sample count). Re-run the witness at 50 ms and 150 ms.

### H4. Top-up goes stale by protocol, so the battery predicate can never pass at the earliest release.

**What happens.**
- R16 re-derives top-up evidence on every sample from the between-window battery log (`condition_waits_native.py:446-450`; `condition_waits.py:329-332`).
- `v4_topup.derive` refuses when the latest log row is more than 300 s old (`MAX_GAP_S`, `v4_topup.py:42`; on the v4 head, "latest valid battery observation is stale", `:107`).
- The frozen triage row stops that sampler *before the dwell* (v4 head `v4_cadence.py:34-37`: "the between-window battery sampler is stopped before the dwell").
- The R16 floor is at least 300 s after the dwell starts, so the battery fails at every possible release.
- Stopping the sampler later would breach the triage row instead.

**Witness:** `F6TopupGoesStaleOnceTheBatterySamplerStops`. The log admits 60 s after its last row and refuses at +301 s.

**Fix:** derive top-up once at the start of the attempt, then carry float continuity forward from the R16 trace's own per-second battery observations. The trace already records `battery_float.observe` every second. This needs a short lead note, because it changes which source evidences "continuous float".

### H5. The fallback (`incumbent_shadow`) is not today's cool-down.

**(a) Install demands native evidence.** `arm_checks` replays `start_state_evidence` and needs a `released` receipt plus packet binding fields whenever any policy exists (`scripts/align_v4_session.py:318-345`). `_arm_and_install` dereferences `source_evidence['header']` even when no evidence was given, which raises TypeError (`:625-627`). So the fallback adds an install gate that today's process does not have.

**(b) The preliminary attempt never ends.** In shadow mode `status` can never become `not_ready` (`condition_waits.py:360-364`), and `run_attempt`'s default `incumbent_ready` is `lambda: False` (`condition_waits_native.py:246`). The loop therefore runs past 1,800 s without end. No CLI produces the preliminary receipt either: `scripts/align_v4_condition_waits.py` has only kit, replay, guard-replay, cw1-parse and finalize-standin. **Witness:** `F3ShadowAttemptHasNoBound`: still waiting at 2,400 s.

**(c) New refusals are active in shadow mode.**
- The stale-after-cleanup check refuses when closing the sources takes more than 2 s. Closing includes SIGTERM to the sudo'd powermetrics and a 5 s wait (`arm.py:213-226`; `condition_waits_native.py:92-105`).
- The `condition_waits_clock` re-judgement can refuse (`arm.py:339-348`).
- H1's load prevents the incumbent guard from reaching READY.

**Fix:**
- In shadow mode, use no install evidence gate, or record the evidence only.
- Bound the shadow attempt at the ceiling with a `shadow_censored` status.
- Make every new refusal site conditional on `mode == 'condition'`.
- Ship a magistrate CLI for the preliminary attempt.

### H6. Integration with the v4 head: the arm rebuilds the packet, and the rebuilt packet has no R16 binding.

**The packet builder.**
- On `48a4d1d76`, `arm_checks` judges its *own* rebuild (`align_v4_next_arm_packet.rebuild_and_compare`) and refuses any supplied packet that differs from it.
- The builder's `quiet()` (`scripts/align_v4_next_arm_packet.py:434-450`) still emits today's committed quiet observation and never `receipt_sha256`, `policy_sha256`, `attempt_id` or `boot_id`.
- So with a policy registered, every arm fails `quiet_start_state`. Adding the fields by hand to the supplied packet makes it differ from the rebuild, which refuses as well.
- **Witness:** `F5PacketBuilderEmitsNoReceiptBinding`. It fails on the scratch merge and skips before the merge.

**The battery log type.**
- On the v4 head `--battery-log` repeats (`action='append'`) and is passed as a list, with window hazard journals merged in.
- The impl writes `str(Path(battery_log).resolve())`, which raises TypeError on a list (merged `align_v4_session.py:801`).
- The impl's `registered_arm` reads only one log.

**The receipt source.** The builder needs a committed R16 receipt source. The preliminary receipt therefore has to be committed and pushed before the packet is built, and its `attempt_id` must equal the session id, which exists only after `prepare`. The runbook has to state that order.

**Conflicts.** Six files conflict: `plan_tree.json`, `identity_pins.json`, `registration_receipt.json`, `v4_cadence.py`, `align_v4_session.py` and `test_v4_kit.py`. §4 resolves them.

### H7. CW-1 qualification is unreachable as built.

**(a) Observer budget.** `parse_run` requires `observer_cpu_s_per_s ≤ 0.005` (`condition_waits_cw1.py:163`). The sampler's process spawns alone cost about 0.026 CPU-s/s, and the census about 0.2-0.4 CPU-s/s (H1).

**(b) Same-run Q.**
- `execute_kit` records `band_sha256` from the policy it ran under (`:195`), and `parse_run` requires it to equal the parsing policy's band (`:166-167`).
- The agreement's D3/D11 path lets CW-1's soak supply Q when R1 changes mode or picks.
- A Q frozen from that soak always changes the band, so R16's single authorized CW-1 can never qualify its own Q. A second run would be needed, and R16 authorizes only one.
- **Witness:** `F7SameRunReferenceCannotQualify`.
- The lead must choose between two options:
  1. Bind the band at parse time under a prospective rule: soak gives Q, then the two recoveries are judged against it.
  2. Accept that only an R1-sourced Q can be registered.

**(c) Idle traces.**
- `guard_replay` needs `r0_rerun11_idle`, `r1_soak` and `cw1_soak` in the R16 sample schema: 1 Hz battery, top-up, OBC, setup digest, display, PM freshness, `power_intervals` and `guard_intervals` (`condition_waits_cw1.py:11`, `:123-148`).
- R0 re-run 11 and R1 predate that schema, and the branch has no exporter or field mapping for them. Two of the three required sources cannot exist, so the zero-hold replay can never qualify.

## 3. MEDIUM and LOW findings

| # | Sev | Finding | Where |
|---|---|---|---|
| M1 | MED | **The target fails `tests.hazards.test_refusal_allowlist` by itself** (2 failures). The new arm refusal sites (`finish\|NULL\|condition_waits` ×2, `condition_waits_clock`) are missing from `configs/gates/hazard_refusals.json`, and `condition_waits_native.py` is neither scanned nor listed in `not_scanned`. Sol's run report did not run this module or `tests.hazards.test_arm`. CI and the integration full-suite run would be red. | `hazards/arm.py:316-348`; `configs/gates/hazard_refusals.json` |
| M2 | MED | The display floor and the quiet floor restart at the arm dwell. They do not overlap the cool-down (P2/D9), so every condition-mode GO is at least 300 s into the dwell. To fix, read the display-sleep transition and the last-disruptive marker from before the arm, or state the cost in the registration text. | `condition_waits_native.py:352-353` |
| M3 | MED | The retry count is not enforced across installs (see §1). The arm should refuse while a `not_ready` receipt for this window has no `lead_release` or ambient-check binding. | `condition_waits_native.py:469-471` |
| M4 | MED | R18 shadow-default: the condition-mode refusals are new guards and need the R18 shadow-exposure promotion, not only the CW-1 replay. | `hazards/arm.py:213-348` |
| M5 | MED | **CW-1 does not capture the KM003C and does not analyze DC-in.** Ed's standing rule is that every measurement captures the KM003C and every analysis analyzes the DC-in channel. Q's power channel can stay as powermetrics (D8), but CW-1 should record the meter and report DC-in print-only. | `condition_waits_cw1.py:14-37`, `:151-174` |
| M6 | MED | `execute_kit` calls `sampler.sample` directly, not `observation()`. A single transient ioreg, plist or pgrep failure aborts the one authorized two-hour run. | `condition_waits_cw1.py:241` |
| L1 | LOW | `q.r1_sha256` is never checked against the actual final R1 digest at kit time. | `scripts/align_v4_kit.py` |
| L2 | LOW | The slope rule is stricter than G0's (see §1). | `condition_waits.py:152-160` |
| L3 | LOW | **Latent fatal.** A display wake sets `quiet = now`. Any later row carrying the true earlier `last_disruptive_ns`, which is the harvest marker the agreement §3 wants the evaluator to read, then trips `disruptive_boundary`, and that is permanent. | `condition_waits.py:249-256`, `:284` |
| L4 | LOW | **Markers pre-create `night/chain-stages.jsonl`.** On a refused arm, harvest's `stage_journal()` then returns `[]` instead of None, and `collection_presence()` emits `chain.stopped_before_collection` (v4 head `harvest.py:7451-7456`). SPEED-TOOLBOX says markers go on *already-open* journals; write them to the arm's own record instead. | `condition_waits_native.py:478-480` |
| L5 | LOW | **Test drift after the merge.** `TriageBindingTests` must pass `now_epoch_s=NOW_EPOCH`. With that change it passes on the merge. | `tests/align/test_condition_waits.py:513-521` |
| L6 | LOW | `test_disabled_dwell_hooks_are_byte_identical_to_the_pinned_base` compares against the moving ref `origin/align/2026-11-08-v4-r11`. After integration it compares the line with itself. Pin a commit instead. | `tests/align/test_condition_waits_arm.py:143-145` |
| L7 | LOW | **A stray powermetrics can survive.** `PowerStream.close` sends SIGKILL to sudo when TERM times out, which can orphan a root powermetrics into the window. The `wait` after SIGKILL can also raise TimeoutExpired, which nothing catches. Use the `r1_runtime.stop_powermetrics_descendants` pattern and confirm powermetrics is gone before GO. | `condition_waits_native.py:92-105` |
| L8 | LOW | Every trace row carries the full battery `ioreg` text (`raw_ioreg`), so the trace grows by tens of MB per 1,800 s attempt while the arm dwell is running. | `condition_waits_native.py:224` |

## 4. Integration: scratch merge onto `48a4d1d76`

**How it was resolved.**
- Worktree `jw-wt/cw-impl-merge-scratch`, local commit `e55ac391a`, not pushed.
- Generated files:
  - Kept the v4 side of `plan_tree.json` and `identity_pins.json`, then regenerated them with `python3.13 -B scripts/align_v4_kit.py`. `--check` blocks only on the known R1 placeholders.
  - Took the union for `registration_receipt.json`.
- Code:
  - `v4_cadence.py`: the v4 record-binding basis, plus the R16 block.
  - `align_v4_session.py`: the v4 rebuild design, with the R16 binding judged against the **rebuilt** packet entry inside the `else` branch, plus the union of the signatures.
  - `test_v4_kit.py`: the union of the expected keyword arguments.

**Tests.** One module per process, with `TMPDIR` realpath'd under the scratchpad.

| Module | Merge result |
|---|---|
| `tests.align.test_condition_waits_arm`, `test_v4_cadence`, `test_v4_kit`, `test_v4_next_arm_packet`, `test_v4_next_arm_packet_opus_witnesses`, `test_v4_registration`, `test_v4_topup`, `test_v4_w1_blockers`, `test_v4_r11`, `test_v4_receipt_tiers`, `test_v4_record_binding`, `test_v4_opus_cold_witnesses`, `tests.hazards.test_arm`, `test_arm_dwell_clean_run`, `test_contention`, `test_import_graph` | OK |
| `tests.align.test_condition_waits` | 1 failure: L5 drift |
| `tests.hazards.test_refusal_allowlist` | 2 failures: M1. These also fail on the target alone; the v4 head passes. |
| `tests.align.test_v4_prequal` | 2 failures, **pre-existing**: identical on the v4 head |
| `tests.align.test_condition_waits_opus_witnesses` | 7 of 7 fail, as intended (F5 included) |

**On the target alone:**
- `test_condition_waits` (35), `test_condition_waits_arm` (7), `test_v4_kit` (116), `test_arm` (25) and `test_arm_dwell_clean_run` (4) pass.
- `test_refusal_allowlist` fails (M1).
- `test_v4_prequal` has 1 failure, which matches its base.

**Packet rebuild, receipt binding and R12/R15 cadence.**
- With no policy file, the merged arm, triage, rebuild and cadence behave exactly as on the v4 head. The R16 block is skipped, and the dwell hooks are byte-identical when disabled.
- With a policy file, H6 refuses every arm.
- The R15 cadence (arm order, seeds, the C6 fence) is untouched by this branch.
- The R12 B2 triage list is unchanged apart from the R16 entry fields on `quiet_start_state`.

## 5. Measurement safety

**Window-time and GO behaviour.**
- **Holds:**
  - No sampler runs inside a window.
  - Every R16 source closes in `finish()` before the arm returns, so before any member launches (`arm.py:213-218`).
  - The markers carry only `phase`, `monotonic_ns` and `wall_ns`.
  - There is no fsync and no ledger.
  - No outcome fields are read.
- **The sampler does perturb the start state it measures (H1).** Its load is about 0.4 CPU-s/s plus daemon work outside the tree, which is large next to the ±0.25 W power band.
- The powermetrics shutdown races the 2 s stale-GO bound (H5c, L7).
- **Before any native use:** a native dry arm with the measured observer-tree cost.

**CW-1 kit.**
- The plan is concrete and bounded: at most 7,200 s, with each recovery run in full.
- Pulse 2 is synthetic and never scans real directories. The kit CLI never probes the host. Cleanup terminates the child process and saves an inconclusive report.
- Against that, H7 and M5/M6.
- If both pulses use their full caps, the phases sum to exactly 7,200 s. The hard ceiling then lands inside `recovery_finalize` and the run is right-censored. The magistrate should budget the pulses below their caps.

## 6. Required before re-review (delta review is enough)

1. **H1-H7 fixed**, each witness passing.
2. **M1 fixed**: the refusal allowlist updated and the scan scope extended.
3. **Conflicts resolved** as in §4, with L5 fixed.
4. **Lead notes** on four points:
   - H4: the top-up continuity source.
   - H7b: binding the band at parse time, or allowing only an R1-sourced Q.
   - M2: either fix the display-floor overlap or declare its cost.
   - M4: R18 promotion of the new guards.
5. **Native checks on the MBP, by the magistrate**:
   - observer-tree cost;
   - one 1,800 s shadow attempt showing powermetrics stream continuity;
   - a native dry arm in shadow mode showing the incumbent guard's READY time unchanged.

Before those land, the safe W1 configuration is: item 5 merged inert (after M1, the conflicts and L5), no policy file, today's cool-down, and a deviation-log line for the missing print-only band.
