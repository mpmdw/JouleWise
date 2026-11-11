# R1 follow-up night — independent Sol design, RL-64

2026-11-11. Design seat only; research-lead disposition pending. Branch
`design/2026-11-11-r1-followup-sol`, base/W1 `b4a6c217f0285a20aff33a8407160dd77af2a8a6`.
No other design seat's work was read. References below mean this W1 base unless
explicitly prefixed `da3187e6e` or `78e6b19ce`.

## Recommendation and material corrections

Keep S6 at **1.5 °C for the arm**, every model G0 at **1,200 s**, and A-B-A before
step-D. Add a fresh, ordinary 30B control after A-B-A; step-D follows that control
with its configured **300 s loaded idle**, captures its own last-60-second
pre-warmup reference, and supplies it unchanged to planning and the gated block.
Remove the soak-release waits before the legs and the cold precool before
step-D. An observed G0 timeout runs flagged; it does not manufacture a release,
adopt a mode, admit a slot, or skip the following block merely because it timed out.

Three qualifications matter before building:

1. **The large margins in RL-64 are at the old timeout, not at release.** The
   earlier replay table labelled them “at cap”. At the earlier own-reference
   release, the passive D members are only **0.019–0.460 °C inside the 1.5 °C
   slow band**. All still release at 1.0 °C, but generally later: up to
   **1,049.16 s** against their own capture. The consume case must be computed;
   the at-cap margins cannot establish its release time by themselves.
2. **The workload currently stops after unreleased G0**, despite the gate's
   “proceeds on timeout” docstring. This is true on the W1 base and the R1 build.
   A real R1 timeout-run hook is necessary outside `thermal_gates.py`.
3. **The original 30B classifier failure cannot be diagnosed from the supplied
   copies.** They contain only the two gate temperatures, no full-inventory or
   recovery journal and no measured-step phase boundaries. Section 7 states
   exactly what was run and what remains unknown. I do not assign a physical
   cause to that null pick.

## Authority, intake and blinding

I read the requested RL-23/26/31/32/35/58/59/61/64 sections from
`origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`,
the sanctioned `r1-structural-rl58.md`, and the replay script, tests, manifest and
report at `78e6b19ce`. RL-59 and RL-64 supersede the old R_op/soak consumers,
pre-leg soak releases, and G0-timeout retries. RL-32 still fixes the armed S6;
RL-35 conditions 10/11 still require clean battery and presence evidence.
RL-26's helper binary/source digests and pre-t0 frequency word remain arm
records for the lead, not a reason to run a native helper here.

M0: no active stop card or global gate in the generated intake; the existing
queue does not describe this newer seat assignment. This direct RL-64 brief is
the task authority. Initial Git status was clean on the requested branch.
I read the relevant playbook, orchestration, source-of-truth map, D-009 and
D-050 conventions. I leave coordination state untouched as instructed.

No network, SSH, hardware collection, model loading, weight downloads, protocol
or preregistration text, real restricted directory, or original custody was
used. Absolute custody/model paths in source and the extract were text only.
Only the named structural extract and temperature-journal copy root were read
outside the clone; Git object reads used the permitted shared alternate.
The source code's timing/budget formulas are discussed below, but no measured
energy, power, token count, model output or performance value was read or printed.
This is not live hardware qualification. Measured members remain batch-1;
there is no optimization, batching or decision cache in this change.

## 1. Journals first: own and consume replay at both bands

I extended `scripts/align_r1_thermal_replay.py` from `78e6b19ce`, with its
synthetic tests and original hashed manifest. It still first reproduces all
**13 recorded G0 outcomes** and recovers R_op exactly. Recorded releases agree
within the original 2 s tolerance; sample-arrival polling can be about 1 s early.
All table times are seconds after G0 entry, excluding warmup and planning preheat.

The extension evaluates recorded, own, and specified D-capture references at
δ_slow = 1.0 and 1.5 °C, with δ_fast = 1.0 °C. Each counterfactual stops at the
**recorded G0 end**: later workload samples cannot establish a hypothetical
release. `right_censored` means the available idle/control trace ended before
the new gate released, not a 1,200 s timeout. A planning consumer uses
`(150 °C, captured_D_slow + offset)` as the existing planning hook does.

R_op is (fast **34.164196**, slow **27.044062**) °C. For the prospective
single-attempt capture I use **step-D first try**: (fast **34.322969**, slow
**28.591406**) °C. The old retry's capture is (34.306715, 28.585626) °C; both
are computed and its sensitivity is tabulated below. These are old records,
not a prediction of the new night's warmer capture.

`F` and `S` below are **band edge minus the replayed release temperature**, in °C;
positive means inside. For planning, F is merely distance below the artificial
151 °C fast edge and is not a physical start-state comparison. The main tables
show S for planning and both margins for passive members.

### Own-reference releases (including the 30B diagnostic)

| Member | own fast / slow °C | 1.0: wait s | F / S margin °C | 1.5: wait s | F / S margin °C |
|---|---:|---:|---:|---:|---:|
| step_30b | 34.164 / 27.044 | censored at 715.86 | — | 714.95 | 0.864 / 0.114 |
| high_power_A1 | 34.310 / 28.546 | 873.42 | 0.914 / 0.206 | 728.41 | 0.875 / 0.019 |
| high_power_B | 34.288 / 28.269 | 937.65 | 0.910 / 0.080 | 877.65 | 0.894 / 0.460 |
| high_power_A2 | 34.278 / 28.220 | 1028.54 | 0.917 / 0.157 | 862.54 | 0.882 / 0.362 |
| step_D (first try) | 34.323 / 28.591 | 1049.16 | 0.926 / 0.153 | 753.16 | 0.865 / 0.132 |
| step_D (retry) | 34.307 / 28.586 | 932.21 | 0.922 / 0.063 | 815.21 | 0.874 / 0.205 |
| planning +4C | 34.302 / 28.458 | 462.11 | ceiling / 1.267 | 462.11 | ceiling / 1.767 |
| planning +2C | 34.327 / 28.968 | 694.37 | ceiling / 1.769 | 694.37 | ceiling / 2.269 |
| planning +0C (first try) | 34.293 / 28.441 | 982.52 | ceiling / 0.105 | 888.53 | ceiling / 0.271 |
| planning +0C (retry) | 34.282 / 28.339 | 997.24 | ceiling / 0.066 | 869.25 | ceiling / 0.271 |

### Consume step-D first-try capture (planning adds its offset)

| D member | 1.0: wait s | F / S margin °C | 1.5: wait s | F / S margin °C |
|---|---:|---:|---:|---:|
| high_power_A1 | 835.42 | 0.932 / 0.013 | 724.43 | 0.880 / 0.171 |
| high_power_B | 877.65 | 0.928 / 0.283 | 877.65 | 0.928 / 0.783 |
| high_power_A2 | 862.54 | 0.927 / 0.234 | 716.55 | 0.868 / 0.200 |
| step_D (first try) | 1049.16 | 0.926 / 0.153 | 753.16 | 0.865 / 0.132 |
| step_D (retry) | 932.21 | 0.938 / 0.068 | 815.21 | 0.891 / 0.210 |
| planning +4C | 462.11 | ceiling / 1.400 | 462.11 | ceiling / 1.900 |
| planning +2C | 694.37 | ceiling / 1.392 | 694.37 | ceiling / 1.892 |
| planning +0C (first try) | 982.52 | ceiling / 0.255 | 888.53 | ceiling / 0.421 |
| planning +0C (retry) | 966.25 | ceiling / 0.284 | 866.25 | ceiling / 0.445 |

### Sensitivity: consume the old step-D retry capture instead

| D member | 1.0: wait s / slow margin °C | 1.5: wait s / slow margin °C |
|---|---:|---:|
| high_power_A1 | 835.42 / 0.007 | 728.41 / 0.058 |
| high_power_B | 877.65 / 0.277 | 877.65 / 0.777 |
| high_power_A2 | 862.54 / 0.228 | 716.55 / 0.194 |
| step_D (first try) | 1055.16 / 0.073 | 753.16 / 0.126 |
| step_D (retry) | 932.21 / 0.063 | 815.21 / 0.205 |
| planning +4C | 462.11 / 1.395 | 462.11 / 1.895 |
| planning +2C | 694.37 / 1.387 | 694.37 / 1.887 |
| planning +0C (first try) | 982.52 / 0.249 | 888.53 / 0.416 |
| planning +0C (retry) | 966.25 / 0.278 | 866.25 / 0.439 |

Both capture choices release all D records within cap. They do not always release on the same sample.

### All recorded-reference gate intervals at both slow bands

| Member | 1.0 outcome / wait-or-observed s | 1.5 outcome / wait s / slow release margin °C |
|---|---|---|
| step_30b | right_censored / 715.86 | released / 714.95 / 0.114 |
| high_power_A1 | timeout / 1200.05 | timeout / 1200.05 / — |
| high_power_B | timeout / 1200.05 | timeout / 1200.05 / — |
| high_power_A2 | timeout / 1200.06 | timeout / 1200.06 / — |
| step_D (first try) | timeout / 1200.04 | timeout / 1200.04 / — |
| step_D (retry) | timeout / 1200.03 | timeout / 1200.03 / — |
| planning +4C | right_censored / 463.11 | released / 462.11 / 0.353 |
| planning +2C | right_censored / 694.56 | released / 694.37 / 0.345 |
| planning +0C (first try) | timeout / 1200.05 | timeout / 1200.05 / — |
| planning +0C (retry) | timeout / 1200.06 | timeout / 1200.06 / — |
| release vs soak before A1 | timeout / 600.01 | timeout / 600.01 / — |
| release vs soak before B | right_censored / 580.63 | released / 580.03 / 0.262 |
| release vs soak before A2 | timeout / 600.02 | timeout / 600.02 / — |

The three obsolete release-against-soak sessions have no own capture and are shown only under their recorded reference. All anchored own captures have 60 samples and coverage 1.0. The first two tables cover every D model member for which the copied journals contain a G0; the skipped gated block contributes no rows.

No gated D episode or X-G ran in the old night: there is **no D-after-full-D
consume trace** to replay, and no duty-bar conclusion follows from these rows.
The planning rows are **threshold tests on the old heater trajectory**, not
counterfactual heater experiments. Raising the reference raises its target;
the new night must establish that trajectory natively.

The tighter band changes passive release timing materially. For example,
step-D first try moves from 753.16 to 1,049.16 s against itself; A2 from
862.54 to 1,028.54 s. The 1.5 °C gate is not always decided solely by the
slope with a large thermal margin. Keep the RL-32 setting for this arm and
give the lead both actual release margins and a censored 1.0 °C replay on the
new journals. Do not silently narrow the armed band.

Reproduce offline, from the clone:

```sh
python3.13 -B scripts/align_r1_thermal_replay.py \
  --manifest docs/run_reports/2026-11-11-r1-thermal-replay.manifest.json \
  --root /private/tmp/claude-501/-Users-edr-code-CapstoneProject-JouleWise/41120c85-9f5f-48c9-aa4d-c3d83d4df41c/scratchpad/r1-journals \
  --consume-label 'step_D (first try)' --consume-label 'step_D (retry)'
```

The manifest supplies all 13 hashes and warmup anchors; no event/transcript
file is opened by this command. The replay's `Session.capture_reference` and
`replay_g0` document the source-rule mapping. W1's corresponding routines are
`thermal_gates.py:265` (window rows), `:282` (slope), `:441` (capture), and
`:515` (G0 loop). The gate rule relevant here is unchanged between the two
builds at these 1,200 s caps; Section 10 lists every module difference.

## 2. Exact sequence and capture predecessor

The named predecessor is a **new `capture_predecessor_30b`**, an ordinary,
complete benign 30B control using the existing `model_30b` template and the
adopted series mode. It has no R1 post-G0 quiet or 600 s recovery suffix.
It is not the cold `step_30b`: that step's required recovery and the intervening
A-B-A legs would make that claim false. The ordinary control has its usual
member deadman and 1,800 s member bound. **The actual `model_30b` template has
no thermal policy**, so the ordinary predecessor has no G0; do not insert one
merely because the R1 step wrapper normally supplies it. Its completed
work and any deadman/fault flag are recorded; incomplete predecessor work
makes the following capture's W1 likeness unresolved for the lead.

Proposed phase table, in order:

| Segment | State/mode/reference and transition |
|---|---|
| pre-calibration bracket | Existing R1 bracket; begin common custody and host-state records. |
| idle_soak, 1,800 s | Automatic; retain the final 1,200 s detrended spread for S5/S5_fast. |
| step_30b | Automatic; unchanged cold diagnostic: own pre-warmup capture R_op, warmup, G0 ≤1,200 s, 300 s quiet, step, 600 s recovery and record-only classification. R_op feeds no D gate. |
| A1 | Set/read back Automatic; D load, configured 300 s idle, own capture, warmup, own G0 ≤1,200 s, step. No separate soak release. |
| B | Set/read back High Power; same recipe, fresh own capture under this mode. |
| A2 | Restore/read back Automatic; same recipe, fresh own capture. Evaluate adoption or mark it unresolved. |
| series mode | Apply/read back adopted mode. If adoption is inconclusive, run remaining diagnostics in explicitly provisional Automatic; do not freeze Automatic from that default. |
| capture_predecessor_30b | Fresh ordinary 30B control from the unchanged no-thermal template, full episode, series mode. |
| step_D | **No cold precool.** D load and its own configured 300 s idle, then native capture at warmup entry: final 60 s median = R. Warmup, G0 ≤1,200 s against R, 300 s quiet, D step, 600 s recovery/full inventory. |
| cooldown_after_D | S_slow to R_slow + δ_slow, cap 1,500 s; record curve and timeout. This is the first planning state's conditioning, not an extra wait between gated members. |
| planning +4 | Its configured idle/load/warmup; preheat ≤900 s, G0 ≤1,200 s at R+4; heater stops before the measured turn. |
| planning +2 precool | Same D-captured R band, ≤1,500 s. |
| planning +2 | Same design at R+2. |
| planning +0 precool | Same D-captured R band, ≤1,500 s. |
| planning +0 | Same design at R+0. This must dispatch actual D work before D_bank. |
| D_bank | Full gated/held bank member; consumes R; only its configured 300 s idle before warmup/G0. |
| D_spam a | Full gated/held benign seed-1 member; follows D_bank; same idle and fixed R. |
| D_spam b | Same member/seed; follows D_spam a; same idle and fixed R. This and a are the replay pair. |
| X-G | Follows D_spam b with its configured 300 s idle, consumes R; record light-contrast timing evidence. |
| post-calibration bracket, close, harvest | Restore/read back Automatic, close collectors/custody, then harvest. |

“300 s idle” is the **next member's configured idle before warmup**, with its
model resident; it is not 300 s after all load/warmup work. No extra thermal
precool is inserted in the final four transitions. The code-derived W1 schedule
returns D = X-G = 300 s (`align_r1_rehearsal.py:1192`, `r1_runtime.py:1841`).
The 30B template also has 300 s configured idle and `thermal` absent:
`configs/campaigns/align_v4/stages/episodes-a/align-pilot-v3-episodes-a-e01.json`
(selected by `configs/align/v4/r1_runtime.json:8`).
The brief/RL-59 permits one 30B predecessor; this does not assert that it
reconstructs all four W1 anchors or their accumulated heat. The smoke must
test this particular chosen predecessor.

**Admit the 30B-predecessor/step-D pair as one unit against the OS blackout.**
A batch-window wait between those two members would silently insert the very
long cooling gap this design removes. If either unit member is contaminated,
redo the whole pair, at most twice in total, with no nested per-member redo.
Accept R only from the accepted pair. Every planning redo likewise repeats
its bounded R-band precool before the preheat/member. Section 8 counts these
complete recipes; it does not count a bare member redo as a matched start.

The old phase table is `align_r1_rehearsal.py:495`; the D-bank/a/b order and
matched-predecessor reason are `:44–65`. Replace its old step-D precool and
reference semantics rather than retaining contradictory comments. Optional
4-bit is **cut** from this night: it is a later fallback requiring its own
qualification, not an input to the current 8-bit slots.

## 3. A-B-A start states and adoption

Keep the legs ahead of step-D so all D slot inputs are measured under the
chosen series mode. Each leg captures through W1's original
`ThermalSession.capture_reference(member)` at warmup entry. Use the same
template, idle duration, warmup, step, 1,200 s G0 and band; re-arm the step
deadman only after that G0. No pre-leg release against the soak remains.

For each accepted leg print mode/readback, own two-key capture, last-60-second
coverage/slope/noise, G0 outcome/wait, two release temperatures, two excesses
above capture, two release margins, slow slope, and the interval to prefill.
Put A1/B/A2 side by side, with absolute A2−A1 capture/release differences.
This demonstrates the same **settled-start procedure and relative band**;
it does not prove identical absolute temperatures under two fan/mode states.
Do not use the old at-timeout margin as the leg's start state.

Keep the existing adoption arithmetic (`align_r1_rehearsal.py:588`): B must
outlast max(A1,A2) by factor 1.25, with the two finite Automatic decline times
within 25% of their maximum. All three genuinely observed no-decline outcomes
mean not adopted; an unobserved clock is not infinity. If a leg starts on a
timeout, is overlapped/contaminated, or if start-state comparability remains
questionable, adoption is inconclusive for the research lead. Do not invent
a new temperature-spread acceptance threshold in this design seat.

## 4. Planning turns and the preheat cap

Against the old first step-D capture, targets are **28.591406, 30.591406,
32.591406 °C** for offsets 0/2/4. Preheat stops on the first valid
`T_slow ≥ target − 0.5 °C`, or at 900 s; a proportional heater then runs
during the native G0 and stops in `finally` before the turn
(`r1_runtime.py:1494–1540`). Heating cannot cool a warm start, which is why
the three bounded precools remain, warmest state first.

The copied old traces show the preheat threshold was already exceeded by
post-preheat G0 entry: slow readings +4/+2/+0 first/+0 retry were
**69.0234 / 69.1334 / 69.0416 / 68.6653 °C**, respectively. Warmup-entry to
post-preheat G0 entry was **104.291 / 104.508 / 104.653 / 104.828 s**.
Since the preheat starts after warmup, those are conservative upper bounds
on its duration, all <900 s. Thus **on these old trajectories** every shifted
threshold is reached inside the preheat cap. This is not evidence of a
controlled start near the target: load/warmup made the machine much hotter.

The consume replay then releases all four planning records at both bands
inside 1,200 s (table above), but changing the target changes the heater's
duty. The new night must record preheat entry/end, target, threshold crossing,
cap-hit flag, valid samples, actual G0 release temperature, and heater stop.
Both the G0 release and the **two-sided** `abs(release−target) ≤ δ_slow` check
must hold, with distinct measured release states
(`align_r1_rehearsal.py:614–653`). A preheat cap hit is retained as
`r1.preheat_cap_reached`, not hidden by a later G0 release; it makes the
planning/U5 evidence provisional until the lead rules. A G0 timeout has no
release temperature, even though the gate's field is named `release`.

## 5. Exact timeout-run semantics and admissibility

Current behavior is not the requested behavior. Native G0 returns an interval
and leaves `episode_reference = None` on timeout (`thermal_gates.py:613–651`);
`holds_suppressed` is then true (`:429`). The adapter tests that condition
(`workload.py:440–445`) and breaks without generation (`:486–500`), recording
`episode.g0_unreleased:<turn>`. Both reviewed builds do this. The old R1
runtime consequently returns no-turn inconclusive rows or refuses, retries
step-D/planning once, and skips all four final members on an inconclusive
step-D (`r1_runtime.py:1648–1783`; `align_r1_rehearsal.py:1279`, `:1710`).

Proposed semantics, to be built/reviewed separately:

1. The unchanged W1 gate runs first. On an **observed `timeout` only**, retain
   `thermal.start_gate_timeout`, the real interval, last temperatures, slope,
   coverage and null episode reference. Add `r1.g0_timeout_run` plus the
   existing `episode.g0_unreleased:0`; dispatch the normal bounded workload.
   A timed-out G0 is never renamed released and never installed as a G1/H
   reference. Native hold suppression remains in effect and is disclosed.
2. Steps/legs re-arm their decode deadman after G0; steps retain the same
   300 s quiet even on this observed timeout, so their classifier input is
   observed. Planning re-arms after preheat/G0 and always stops the heater.
   The ordinary no-G0 predecessor keeps its normal member deadman. Gated
   members keep G0 inside their normal shared member deadman; timeout does
   not add an unbudgeted decode allowance.
3. Unobserved gates, missing status, collector faults, deadman expiry and
   incomplete/failed generation retain their separate fault semantics.
   The timeout-only hook must not turn those into usable starts. Missing
   reference custody is a refusal, never permission to recapture.
4. Record actual dispatched work and timings, timeout/censor flags, reference
   source/digest and attempt number. Do not retry merely for a G0 timeout.
   Do not skip the gated block merely because step-D's G0 timed out: derive
   **candidate** finite step-D budgets from its completed flagged turn and
   use them provisionally. A nonfinite/zero budget or incomplete step is a
   different failure; do not run unbudgeted members.
5. A candidate is not an admissible registration input. Add explicit
   `inadmissible_slots`/dependency evidence; keep the kit closed pending a
   cited lead ruling. Do not clear `inconclusive_segments` or label the
   night admissible to defeat its current kit guard (`align_v4_kit.py:183–239`).
   Keep the S6=1.5 receipt even in an inconclusive proposal (RL-59).

Universal slot-feed bars: a complete terminal record/chain exit 0; accepted
attempt provenance; no overlapping agent (`agent.presence_overlap` or an
episode in the presence journal); AC present and no discharge throughout
every feeding segment; correct mode; valid custody. Battery/presence records
are checked directly, not inferred from absence of an emitted flag (RL-35
10/11). Proposed `r1.battery_feed_invalid` and `r1.agent_feed_overlap` are
explicit summary codes for those failed checks, not claims that such codes
already exist in the catalog.

For any slot dependent on a timeout-run source, `r1.g0_timeout_run` and its
underlying `thermal.start_gate_timeout` make it **inadmissible without the
research lead's ruling**. Subsequent members also record whether their
predecessor completed actual D work and whether it was flagged. Continuing
the night is diagnostic preservation, not automatic rehabilitation or a
model/quantization fallback. Only the lead applies the registered fallback
order: S6 to 2.0, D-predecessor idle to 450 s, 4-bit, then screen-only.

## 6. Complete slot and evidence inventory

The W1 template lists S1–S9 plus B_D/I_D/T_dead/N_chunk/t_decline/class (15).
The driver additionally requires **S5_fast** (16 total;
`align_r1_rehearsal.py:36–38`, `:571`). The template/driver must agree in the
build. Slot formulas are code, not observed numbers (`r1_runtime.py:769–826`).

| Slot | Feed and required observation | Specific disqualifier besides universal bars |
|---|---|---|
| S1 | step-D, chosen fast key's baseline-to-peak ΔT | step-D timeout flag; invalid/no response. |
| S2 | step-D fast t63 | step-D timeout; `no_rise`/`t63_censored` or no finite crossing. |
| S3 | step-D slow ΔT | step-D timeout; invalid/no response. |
| S4 | step-D slow peak-to-63%-fall tau, including 600 s recovery | step-D timeout; `tau_censored` must retain its lower bound and go to lead, never be a measured tau. |
| S5 | idle soak: max(1 °C, 3 × detrended slow SD), final 1,200 s | unresolved soak slope, missing time coverage or contaminated accepted soak. It does not acquire a G0 flag merely because a later step times out. |
| S5_fast | same soak and formula for fast key | same soak failures. |
| S6 | armed 1.5 °C receipt plus new release-margin and G1/H-median evidence | no valid gated evidence, any relevant timeout/hold suppression, missing receipt; a narrower value needs RL-64 lead disposition. Preserve S5 separately. |
| S7 | step-D peak-to-both-keys-in-band recovery, G_turn = min(300 s, 3 × recovery) | step-D timeout; `recovery_censored`/unobserved tail; changed sensor picks require recomputation/verification. |
| S8 | step-D N_chunk alias | step-D timeout or unobserved decline/decode support. |
| S9 | step-D t_decline alias | step-D timeout or `t_decline_status=unobserved`; no-decline censoring is a distinct valid bound, not an unobserved clock. |
| B_D | step-D timing/count fields and member-law fit; largest allowed 1,024 multiple fitting 1,800 s | step-D timeout flag; incomplete turn; nonfinite fit or budget outside allowed positive range. Final fit also needs gated evidence. |
| I_D | step-D member wall minus episode wall from G0 entry | step-D timeout flag; incomplete boundaries; outside [0,1750). The rearmed-step accounting must be checked, not adjusted ad hoc. |
| T_dead | step-D first L1 term (1750−I_D)/1.13544, then gated-tail constraint | step-D or relevant gated timeout; missing/cut tail evidence. |
| N_chunk | step-D decline/decode-derived chunk, same source as S8 | step-D timeout; unobserved decline. No-decline uses the existing censored branch. |
| t_decline | step-D clock decline, same source as S9 | step-D timeout; missing GPU-clock support. |
| class | declared D class plus step-D thermal/timing class diagnostics | unresolved D thermometry, step-D timeout, missing/censored diagnostic requiring lead judgment; the declared `heavy` string alone is not qualification. |

Other mandatory `r1_slots` evidence is not optional because it lacks an S number:

| Output | Required segments and bar |
|---|---|
| ac_powermode / slots_ac_powermode | All three A-B-A legs; settled starts, GPU clock support, adoption arithmetic and mode readbacks; an inconclusive adoption is lead-owned. |
| thermometry.D/bar | step-D full-inventory classification over quiet/step/recovery, two non-null independent picks; changed picks require cited lead verification of S6/S7. Null/alias (`r1.picks_aliased`) blocks. 30B stays record-only. |
| g0_cap_w1 / g0_waits | D_bank, spam a, spam b, X-G; all actual waits/censored starts and references. Existing cap rule: clamp(ceil(1.25 × max wait),600,1200); a timeout counts at cap for the conservative candidate but is not automatically admissible (`align_r1_rehearsal.py:1412`). |
| duty_bar, deadman_budget, max_r1_tail_s, l1, budget_fit_inputs | All three full gated D members, matched predecessor evidence, phase accounting, actual tail and budget support. X7, too few admitted turns, gate/hold share >0.40, timeout or suppressed holds keep the duty result from being a pass. |
| planning_temperature / U5 | All three valid planning starts and both spam replay members, inside the calibration brackets. Actual release temperatures, common R and band, nondegenerate temperature leverage; any timeout/preheat cap, incomplete point or unmatched predecessor blocks ordinary use. U5 is evaluated at armed 1.5 °C and its word reported to the lead. No energy is inspected by this seat. |
| x_g | Full X-G after D with W1 idle; G0, counts/timings and deadman support for the light contrast cap. Timeout is a flagged non-veto contrast record, not evidence of D passing. |
| battery / presence / custody | Journals for every feeding segment, superseded attempts distinguished, both brackets, complete results and fresh provenance. |

Retain the soak, both step observations, legs, three planning turns, all three
gated D members, X-G, brackets and custody. Cuts proposed here are the obsolete
pre-leg soak releases, step-D cold precool, G0-only retries, and optional 4-bit.
Do not cut D_bank: it gives spam a the full-D predecessor that spam b also has.

Before any slot enters STRICT registration, the lead checks the full
RL-32/35 list, not just numeric slot presence: terminal status complete and
chain exit 0 (the summary verdict is not evidence); cold step-30b accepted
attempt 0 with released G0 inside cap, or an explicit ruling on its redo or
unreleased start; report a release far outside the old 700–970 s diagnostic
range; admissible gated evidence; no unresolved inconclusive segment; U5 at
1.5 °C with any FAIL disclosed under RL-20; decided A-B-A adoption; all own
pre-warmup medians printed beside both R_op and D-captured R; post-custody
structural review; and the battery/presence/byte-identity bars. RL-59 allows
the flagged night to continue but does not silently waive those registration
conditions. The reference or band can change the diagnostic range, so a
range exception is reported to the lead, not mechanically labelled a failure.

## 7. Thermometry: what the null picks do and do not establish

`classify_step` (`r1_runtime.py:280–323`) labels the last 300 s before measured
prefill idle, prefill through last decode load, and the next 600 s recovery.
It calls **the same** `smc_enumeration.rank(stage='r1')`. The classifier requires
full inventory and all three phase bounds (`smc_enumeration.py:470–492`).
For both roles, it requires ≥99% one-second-cell coverage in each phase,
<1% failed reads, no two adjacent empty cells, a non-stale last-60-second
baseline, adequate positive rise/early rise, no implausible jumps, and
return-to-band within 300 s (`:531–684`). Fast needs tau ≤60 s and noise
≤1/3 °C; slow needs 60<tau≤300 s and noise ≤0.15 °C. Clamps, heat-ordering
exclusions and aliases must be printed. Fast heating t63 and cooling tau are
different diagnostics; do not replace the classifier with the slot's t63 test.

The **changed-pick flag's software cause is established**: it is
`any(ranked[role] != previous[role])` (`r1_runtime.py:300–310`). Therefore null
versus the R0 picks TV0h/Tf08 sets `r1.sensor_pick_changed`. It does not mean
the classifier found and adopted two new sensors. The structural extract
records status fail and “null pick: s_fast, s_slow”, with no ranking reasons.

I read the authorized step_30b thermal journal through the replay's projection:
**1,657 reading rows**, keys **TV0h and Tf08 only**, plus session start/end and
one G0 begin/end. There are no measured-prefill/last-decode boundaries in that
journal. The exact optional paths `step_30b/inventory/inventory_journal.jsonl`
and `step_30b/recovery/align_thermal.jsonl` are absent from the sanctioned copy
root. I did not search elsewhere or open original custody.

I ran `smc_enumeration.rank` on those projected temperature/read-stamp rows as
an **input-completeness probe**, with the two observed keys and no invented
phase anchors. It returned both picks null, with each reason
“classifier requires idle, load and recovery”. That is a diagnosis of the
supplied replay input's incompleteness, **not a reproduction of the original
full-inventory failure**. It cannot identify which original D1–D6 rule removed
which original sensor. Claims of insufficient rise, a recovery gap, thermal
failure or bad sensors would be guesses on the available record.

Before the long arm the lead needs a sanctioned temperature-only projection
of the old 30B inventory **including the original three phase boundaries**,
inventory key/unit/quantum metadata and per-key read errors. Re-run
`classify_step`/`rank` without changing thresholds and print each candidate's
reason, coverage, baseline/noise, rise/early rise, tau, band-return time,
clamp/alias/heat-order diagnostics. The new night must journal the same input
for step-D and 30B through the complete 600 s recovery, with sufficiently
early recovery reads to resolve the fast crossing. A verdict needs a genuine
D pass with two independent picks, or a research-lead ruling on a failure;
the old 30B record-only failure neither passes nor automatically fails D.

## 8. Deadline arithmetic and OS batch window

These are **planning bounds from code, not measured duration predictions**.
No speed saving is claimed. The configured step deadman is 1,580 s
(`configs/align/v4/r1_runtime.json:15`); the rearmed-member law is

`M = 1750 + 1.13544 × 1580 + 120 = 3663.9952 s`

(`align_r1_rehearsal.py:124–157`, `:1119–1130`). With the required 1,200 s
G0 outside the step deadman:

| Segment(s) | Each bound s | Multiplicity | Subtotal s |
|---|---:|---:|---:|
| soak | 1800 | 1 | 1800 |
| cold step_30b | M+1200+300+600 = 5763.9952 | 1 | 5763.9952 |
| own-capture A-B-A | M+1200 = 4863.9952 | 3 | 14591.9856 |
| ordinary 30B predecessor | 1800, unchanged no-G0 member | 1 | 1800 |
| capture step-D | M+1200+300+600 = 5763.9952 | 1 | 5763.9952 |
| post-D/planning precools | 1500 | 3 | 4500 |
| planning 4/2/0 | M+900+1200 = 5763.9952 | 3 | 17291.9856 |
| D_bank, spam a/b, X-G | 1800, G0 inside member bound | 4 | 7200 |
| **No-redo phase subtotal** | | | **58711.9616 (16.309 h)** |

This removes step-D's old 1,500 s precool, adds the ordinary predecessor, and
replaces the three pre-leg release+member constructions with own-gate ones.
The extra 300 s quiet of a step is already included, not counted again as a
separate member idle. Model load/start/close are in M or the ordinary member
bound; the build must assert actual wall limits, not rely on comments alone.

The **actual existing** `night_worst_case_s()` on W1 returns 56,206.9616 s,
plus one batch encounter 11,163.9952 = 67,370.9568 s; its four G0 retries add
29,055.9808 s, yielding floor **96,427 s**. At `da3187e6e` it returns
60,406.9616 s and uses only 5,400 s for a batch wait, yielding
94,862.9424 s with G0 retries. Correcting that build's one encounter to
11,163.9952 gives **100,626.9376 s**, ceil **100,627**. RL-23's intermediate
97,027/106,027 s numbers precede the final leg changes; none is the new plan's
derived deadline. W1's hard-coded floor and encounter constant
(`w1_prequal.py:934`, `:997–1020`, `:1160`) must be updated from the new table.

The **G0 retry floor is now zero**: run flagged, no G0-only retry. CPU-load
redos are a separate policy. Preserve the inherited maximum of two redos,
but apply it to **complete quiet recipes**, with no nested redo
(`align_r1_rehearsal.py:163`, `:1050–1108` currently count bare segments).
There are nine recipes: soak, cold step_30b, three legs, the capture pair,
and three precool+planning units. Their bounds sum to:

`Q = 1800 + 5763.9952 + 3×4863.9952 + (1800+5763.9952)
     + 3×(1500+5763.9952) = 51511.9616 s`.

The capture pair bound is **7,563.9952 s**; each precool+planning unit is
**7,263.9952 s**. Redoing step-D after a D step without another 30B predecessor
would violate the reference design. Redoing planning without its precool
would violate the conditioning recipe. These additional pieces must not be
omitted from the retry floor.

The new `night_worst_case_s` result must expose both segment bounds and these
admission/redo units, their attempt quotas and blackout count; a maximum over
the ungrouped segment rows alone is insufficient. The pure phase table still
lists the individual custody segments. Deadline tests must include a start
just before the capture pair would overlap 11:45, a repeated pair, planning
redos, and a multi-day calendar traversal.

Two redos of every recipe add `2Q = 103023.9232 s`, for **161735.8848 s**
before blackout waits and external overhead. No redo reintroduces a release
against cold soak. If the implementation also keeps the legacy 65+600 s
redo release, it must add 18×665 = **11,970 s**, and explain its reference.
That behavior is not in this proposal. Grouping the capture pair and its
redo quota needs an explicit table/driver implementation and lead acceptance.

The OS exclusion is **11:45–13:15 America/Los_Angeles**, width 5,400 s.
`wait_outside_os_batch` checks the **whole upcoming attempt**, not just its
start (`align_r1_rehearsal.py:963–994`). Its maximum admission-unit bound
here is 7,563.9952 s, so an encounter costs up to **12,963.9952 s**, not 5,400.
Each redo is admitted again, and a multi-day night can encounter later days.
Use the local-calendar/DST code; do not add a fixed-offset UTC daily mask.

Concrete conservative envelope for the table above:

- No redos, allow two daily encounters: ceil(58711.9616 + 2×12963.9952)
  = **84,640 s** phase/release floor.
- All allowed load redos, allow four encounters: ceil(161735.8848 +
  4×12963.9952) = **213,592 s** retry-inclusive floor.
- Proposed **explicit overhead caps**, to be reviewed/built: pre bracket
  1,800 + post bracket 1,800 + close 900 + harvest 4,500 = **9,000 s**.
  Existing `night_worst_case_s` assigns brackets zero and omits close/harvest;
  these allowances are not established native bounds. Refuse the arm if the
  build neither enforces nor replaces them with verified bounds.
- Programmed span including that overhead = **222,592 s** with all redos.
  The existing writer formula is `60×ceil((ceil(span)+3300+7200+7200)/60)`
  (`joulewise/b6/plan_inputs.py:56`, `joulewise/b5/plan.py:59–67`). Hence
  **window_max_s = 240,300 s (66 h 45 min)** for this conservative proposal.
  The no-redo comparison is span 93,640 → **111,360 s (30 h 56 min)**.

Four encounter allowances are deliberately conservative: the resulting
66.75-hour envelope, including maximum admission look-ahead <2.11 h, spans
less than three full days; at most four daily blackout intervals can affect
it. The no-redo 30.94-hour envelope plus look-ahead spans <48 h, so two are
sufficient. These are self-consistent envelopes, not “one encounter per
attempt” sums; an installed exact-t0 simulation may tighten them only with
the same caps/attempt policy and a checked calendar traversal.

**This is not a 24-hour worst case.** The lead can choose a smaller global
load-redo allowance or staged diagnostic follow-up, but that is an explicit
change to the inherited retry policy, not a saving already supported by
measurements. Do not arm the stock table or reuse an old 29-hour deadline.
No OS mask is applied by this desk session.

## 9. Thirty-minute native smoke and the before-arming order

The lead runs this later from a clean, agent-free native session; this seat
does not schedule or run it. The before-arming order is replay → this single
design round closed by the research lead → native smoke → cold review of
the final kit changes (RL-59). Synthetic hook/closure checks precede the
smoke; if cold review changes executed bytes, repeat the affected smoke.

The **1,800 s smoke** uses the intended mode, W1 gate bytes and the chosen
ordinary 30B predecessor, then D with its configured 300 s idle, native
capture, warmup and G0. It is a smoke of **admission**, not full slot collection.
It must show:

- both model/config identities are the intended local pinned ones, batch-1;
  no weight fetch, agents, extra collector, battery discharge or host-mode
  change; normal terminal restoration/closed custody;
- one completed ordinary 30B predecessor, no inserted cold precool, and D's
  own 300 s loaded idle; D reference equals its final-60-second median with
  ≥0.9 coverage, names the D producer/digest and is not R_op/soak;
- D captures **before** warmup, runs warmup, releases native G0 inside
  1,200 s at S6=1.5, and records ten good observations, fresh nominal status,
  slope, temperatures and margins. Inspect a stricter 1.0 replay only through
  the recorded release, with censoring. No forced release or hook mutation
  of the outcome is accepted;
- the same captured R can be authenticated by a consumer in a desk/synthetic
  smoke, without recapture; model/collector close leaves no orphan heater,
  SMC worker or High Power restore marker.

**Thirty minutes is not guaranteed by these caps.** The necessary inequality
is `30B observed wall + D load/start/warmup/close + 300 + D gate wait ≤1800`.
Using the old passive own-capture waits 753–815 s only as a planning guide
leaves **685–747 s** for 30B plus D overhead; at the full G0 cap it leaves
only **300 s**. No 30B performance record was read here to prove this fit.
If the smoke cannot finish admission in 1,800 s, stop and report its boundary
and reason to the lead; do not call a partial smoke passing or automatically
extend it into the long block. A new 30B/D thermal trace, after the chosen
predecessor, is the missing native evidence.

The smoke does not establish A-B-A adoption, all planning targets, full
D-after-D duty, thermometry ranking, tails, restore-on-fault coverage or
final slots. Synthetic targeted tests must also exercise observed timeout
dispatch, unobserved/fault refusal, null references/hold suppression, unchanged
default W1 stop behavior, candidate/slot refusal, heater cleanup and budget
edges. Native fault/restore and D-inventory checks remain lead-owned.

## 10. Condition 13: exact W1 bytes and R1 hooks

**Do not copy da3187e6e's thermal-gate module over W1's.** The W1 file is
SHA-256 `c72937bd8bf7b5553c1ffd70e76018ffbf25f32578533c8749aa88419837918d`;
the R1 build's is
`2d4917b7e499630a653fcf8a0d0dbec4e7db87193b16df92e29e82faa04eda37`.
Every difference listed below belongs to the **shared W1 side** and must be
retained. No difference in this module implements the R_op capture, widened
R1 band, all-model R1 cap, or R1 deadman rearm: those live in `r1_runtime.py`.

| W1 diff versus da3187e6e | Ownership |
|---|---|
| import `timing_receipts`; wrap `wait` around `_wait`, mark unsuccessful G0 span timeout/refused | Shared W1 timing instrumentation, retain byte for byte. |
| add `R10_G0_CAP_AUTHORITY` and `G0_UNOBSERVED_LIMIT_S` | Shared cap/receipt semantics, retain. |
| policy accepts/validates `g0_cap_receipt` and `contrast_fit`, including fitted light cap zero, receipt shape and sub-600 cap authority | W1 R10/R11 qualification, retain; no R1 special case belongs here. |
| authenticated unobserved consumed reference raises `WindowReferenceRefused` instead of returning None | Shared custody/admission fence, retain. |
| unobserved G0 limit becomes min(300,armed cap), instead of unconditional 300 | Shared low-cap correctness; equal for this R1's 1200 s cap. |

Full diff, direction **da3187e6e → W1 b4a6c217f**, follows so no hunk is hidden:

```diff
diff --git a/joulewise/align/apple/thermal_gates.py b/joulewise/align/apple/thermal_gates.py
index 4878ebad2..b46769d70 100644
--- a/joulewise/align/apple/thermal_gates.py
+++ b/joulewise/align/apple/thermal_gates.py
@@ -6,6 +6,7 @@ legacy hazards.temperature alias retain their isolated import boundary.
 from __future__ import annotations
 from collections.abc import Mapping
 from contextlib import nullcontext
+from joulewise import timing_receipts
 import hashlib
 import json
 import math
@@ -22,6 +23,11 @@ from joulewise.interfaces import RuntimeEvent
 REFERENCE_SCHEMA = 'joulewise.align_window_reference.v1'
 G0_CAP_DEFAULT_S = 600
 G0_CAP_MAX_S = 1200
+# LEAD-RULINGS-2 R10-2(a): a D member's W1 G0 cap may fall below the 600 s
+# floor only under the lead's committed ruling 1(f) receipt; the policy then
+# names it (g0_cap_receipt), and the kit binds that digest to the receipt bytes.
+R10_G0_CAP_AUTHORITY = 'LEAD-RULINGS-2 R10-2(a)'
+G0_UNOBSERVED_LIMIT_S = 300
 
 
 class WindowReferenceRefused(RuntimeError):
@@ -95,14 +101,51 @@ def sample_rows(rows):
 def validate_gate_policy(value):
     required = {'sensors', 'delta_fast_c', 'delta_slow_c', 'turn_cap_s', 'per_turn', 'heavy', 'chunk_tokens'}
     if (not isinstance(value, Mapping) or not required <= value.keys()
-            or 'window_reference' not in value or set(value) - required - {'window_reference', 'g0_cap_s'}):
+            or 'window_reference' not in value
+            or set(value) - required - {'window_reference', 'g0_cap_s', 'g0_cap_receipt', 'contrast_fit'}):
         raise ValueError('thermal policy has missing or unknown fields')
     policy = dict(value)
     policy['sensors'] = validate_policy(policy['sensors'])
+    receipt = policy.get('g0_cap_receipt')
+    contrast = policy.get('contrast_fit')
+    if 'contrast_fit' in policy:
+        if (not isinstance(contrast, Mapping) or contrast.get('authority') != 'LEAD-RULINGS-2 R11 / RUN_STATE 212'
+                or contrast.get('role') != 'contrast' or policy.get('heavy') is not False
+                or receipt is not None or contrast.get('value_s') != policy.get('g0_cap_s')
+                or (contrast.get('predeclared') is not None and
+                    not str(contrast['predeclared']).startswith('INCONCLUSIVE:'))):
+            raise ValueError('thermal.contrast_fit must bind the R11 non-veto light contrast cap')
+        episode = contrast.get('episode_s')
+        nominal, deadman = contrast.get('nominal_cap_s'), contrast.get('deadman_s')
+        if any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in (nominal, deadman)):
+            raise ValueError('thermal.contrast_fit timing malformed')
+        if episode is not None and (type(episode) not in (int, float) or not math.isfinite(episode) or episode < 0):
+            raise ValueError('thermal.contrast_fit episode malformed')
+        expected = 0 if episode is None else max(0, min(nominal, math.floor(deadman-episode-10)))
+        if contrast['value_s'] != expected:
+            raise ValueError('thermal.contrast_fit cap differs from deadman arithmetic')
+    if 'g0_cap_receipt' in policy:
+        # R10-2(a): the receipt travels only with a cap below the 600 s floor.
+        if (not isinstance(receipt, Mapping) or set(receipt) != {'authority', 'receipt_sha256'}
+                or receipt['authority'] != R10_G0_CAP_AUTHORITY
+                or not isinstance(receipt['receipt_sha256'], str) or len(receipt['receipt_sha256']) != 64
+                or any(c not in '0123456789abcdef' for c in receipt['receipt_sha256'])):
+            raise ValueError('thermal.g0_cap_receipt must be {authority: '
+                             f'{R10_G0_CAP_AUTHORITY!r}, receipt_sha256: 64-hex}}')
+        policy['g0_cap_receipt'] = dict(receipt)
     if 'g0_cap_s' in policy:
         cap = policy['g0_cap_s']
-        if type(cap) not in (int, float) or not math.isfinite(cap) or not G0_CAP_DEFAULT_S <= cap <= G0_CAP_MAX_S:
-            raise ValueError(f'thermal.g0_cap_s must be finite and in [{G0_CAP_DEFAULT_S}, {G0_CAP_MAX_S}]')
+        if (type(cap) not in (int, float) or not math.isfinite(cap)
+                or not 0 <= cap <= G0_CAP_MAX_S or (cap == 0 and contrast is None)):
+            raise ValueError(f'thermal.g0_cap_s must be finite and in [{G0_CAP_DEFAULT_S}, {G0_CAP_MAX_S}], or in '
+                             f'(0, {G0_CAP_MAX_S}] with a g0_cap_receipt ({R10_G0_CAP_AUTHORITY})')
+        if cap < G0_CAP_DEFAULT_S and receipt is None and contrast is None:
+            raise ValueError(f'thermal.g0_cap_s must be finite and in [{G0_CAP_DEFAULT_S}, {G0_CAP_MAX_S}]; '
+                             f'a cap below {G0_CAP_DEFAULT_S} s needs the lead\'s ruling 1(f) receipt '
+                             f'(thermal.g0_cap_receipt, {R10_G0_CAP_AUTHORITY})')
+    if receipt is not None and not (policy.get('g0_cap_s', G0_CAP_DEFAULT_S) < G0_CAP_DEFAULT_S):
+        raise ValueError(f'thermal.g0_cap_receipt only accompanies a g0_cap_s below {G0_CAP_DEFAULT_S} s '
+                         f'({R10_G0_CAP_AUTHORITY})')
     for name in ('delta_fast_c', 'delta_slow_c', 'turn_cap_s'):
         v = policy[name]
         if type(v) not in (int, float) or not math.isfinite(v) or v <= 0:
@@ -210,7 +253,9 @@ def load_window_reference(policy, context):
         value = {'fast_c': record['fast_c'], 'slow_c': record['slow_c'],
                  'source_member': source_id, 'span_ns': record['span_ns']}
     else:
-        value = None
+        # D-14b-1: authenticated loss at member 5 is not a new reference.
+        # Refuse before the consumer's runtime.prepare/model load.
+        raise WindowReferenceRefused('thermal.window_reference_unobserved')
     custody = {'record_sha256': digest, 'source_run_id': source_id,
                'source_config_sha256': ref['source_config_sha256'],
                'source_journal_sha256': journal_digest}
@@ -457,6 +502,17 @@ class ThermalSession:
                         'source_journal_sha256': None}
 
     def wait(self, kind, *, turn=0, token_count=None, deadman=None, defer_resume=False):
+        # G1/H already have native entry/exit receipts, including H's later
+        # dispatch endpoint. Do not duplicate their per-turn boundaries. G0
+        # needs a persisted start even when admission faults before an interval.
+        with (timing_receipts.span("gates", "G0") if kind == 'G0' else nullcontext()) as receipt:
+            row = self._wait(kind, turn=turn, token_count=token_count, deadman=deadman,
+                             defer_resume=defer_resume)
+            if receipt is not None and row['outcome'] != 'released':
+                receipt.status = 'timeout' if row['outcome'] in ('timeout', 'deadman') else 'refused'
+            return row
+
+    def _wait(self, kind, *, turn=0, token_count=None, deadman=None, defer_resume=False):
         """G0 proceeds on timeout; unobserved gates wait then proceed with X4.
 
         G1/H stop only on an actual timeout or the member deadman.
@@ -534,7 +590,10 @@ class ThermalSession:
                         reason = 'deadman'
                         break
                     elapsed = (now - start) / NS
-                    limit = 300 if unobserved and kind == 'G0' else cap
+                    # The unobserved G0 wait never outlasts the armed cap: under
+                    # R10-2(a) the cap can be below 300 s, and ruling 1(f)'s G0
+                    # term is the armed cap.
+                    limit = min(G0_UNOBSERVED_LIMIT_S, cap) if unobserved and kind == 'G0' else cap
                     if elapsed >= limit:
                         break
                     delay = min(1, limit - elapsed)
```

The R1-only behaviors go through the following **proposed** interfaces. They
are a build specification, not implemented changes in this commit:

| Behavior | File, hook/function and proposed signature |
|---|---|
| Construct the original shared gate session | Keep `r1_runtime.py:1264` `ProductionBackend.run_member(self, config_map, runs_root, hook)` and its factory `factory(policy, clock, context, status_reader=None)`. It constructs W1's `ThermalSession`; `hook(session)` decorates the instance outside the module. |
| Ordinary 30B capture predecessor | Add `Segment.k_capture_predecessor_30b(self)` in `r1_runtime.py`, running the unchanged ordinary `model_30b` episode template with `run_member(config_map, hook=None)`, not `step_member`. Preserve its absent thermal policy, normal task and member budget; change only run identity/custody routing as needed. |
| Own capture for 30B, each leg, step-D; fixed consumption elsewhere | Extend `Segment.reference_hook(self, reference, *, quiet_s=0, rearm_s=None, capture=False)` at `r1_runtime.py:1462`. With capture=True leave session.reference unset and call original `capture_reference(member)` unchanged. With consume, authenticate the accepted step-D result/capture custody and install that fixed reference. Persist the real source run/span/digest; never relabel R_op as D. |
| Print every member's own pre-warmup median beside its gate reference | Add `Segment.own_reference_diagnostic(self, session, now_ns) -> dict` in `r1_runtime.py`; compute temperature-only median/coverage for disclosure at capture entry, without changing/publishing the consumer's fixed R. This diagnostic is not a second admission rule. |
| Quiet after G0 and rearmed step/leg deadman | Same `reference_hook` wait wrapper; invoke original `session.wait(kind, **kwargs)` first, preserve its interval/result and null episode reference, then quiet/rearm as specified in Section 5. G1/H delegate unchanged. Existing `rearm_deadman(deadman, seconds, origin)` is `r1_runtime.py:469`. |
| Planning target, preheat/control/cleanup and rearm | Existing `Segment.planning_hook(self, reference, target_slow_c, *, rearm_s)` at `r1_runtime.py:1494`; target comes only from D capture + offset. Calls original G0; never changes its outcome, band, slope or observation rule. Add cap/threshold evidence. |
| Every R1 model gate uses 1200; S5 remains the soak formula, S6 retains adopted 1.5 | R1 `gate_policy(...)`/`g0_cap_s`/`bands_c(...)` and receipt handling (`r1_runtime.py:403–448`, `:1544`). Port the da3187e6e runtime changes for all-model caps, separate S5 and adopted-S6 floor/receipt; shared validator remains W1's. |
| Observed timeout dispatch rather than early stop | Add `EpisodeRuntimeAdapter(..., g0_timeout_hook=None)` in `workload.py:188` and invoke it at `:440–445` with `(session, g0_row) -> bool`. R1 supplies `allow_g0_timeout_run(session, g0_row) -> bool` from `r1_runtime.py`, true only for an observed timeout. An R1 backend delegate decorates the resolved adapter before `ThermalRegistry._bind`; do not edit the shared gate registry just to pass the callback. Default None preserves W1's current behavior. Retain all unreleased flags and null episode reference; loop flagging at `workload.py:486` is separated from its default early-stop branch. |
| Candidate versus admissible slots, no G0-only retry/skip, A-B-A own-start checks, D-predecessor/reference checks, redo/deadline accounting | Driver `run(args)`, `_calibration_segment(...)`, `aba_adoption(...)`, `night_worst_case_s(...)`; runtime `k_step`, `k_step_d`, `k_planning`, `k_gated_d`, `reference_fields`; contract/result schema and kit guard updated together. These are orchestration hooks/consumers, never alternate thermal decision code. |
| R1 schedule consumed by the W1 night | Pure `joulewise/align/apple/r1_phases.py:phase_plan(include_4bit=False, precool_cap_s=...)` with constants, no runtime/driver/wait imports. No such module is present on this base. First move the existing function text unchanged, with table equality tests for both include_4bit values (RL-61); then make the ruled follow-up schedule change as an explicit separate diff/test expectation. |

The remaining sensor-only R1 behavior also stays outside the shared module:
`Segment.open_session(self, label, *, pm_status=False, reference=None,
policy=None)` (`r1_runtime.py:1419`) uses
`ProductionBackend.session(self, policy, outputs_dir, run_id, *, pm_status=False)`
(`:1235`). `k_idle(self)` supplies the soak, `k_idle_until_soak(self)` the
bounded R-band precools (rename its obsolete “soak” semantics), and
`observe_recovery(self, member)` the fixed 600 s observation. Those functions
read the same session's rows; they do not replace its gate decision.
`start_inventory(self)`, `stop_inventory(self)` and
`thermometry(self, member, *, label, record_only)` (`:1716–1758`) own the
separate full-inventory classifier record. Mode changes/restores remain
`_set_powermode(guard, mode, label, refusal)` in the driver (`:1558`), with
no mode-switching code in `ThermalSession`. Battery/CPU/presence/custody,
slot derivation and harvest remain runtime/driver orchestration, not a fork
of the thermal gate.

The timeout-run adapter change is an additional **shared bound-code change**,
even with an inert default. It needs cold review and unchanged-default tests;
Condition 13 does not authorize an R1 fork of workload or a fake episode reference.
If the lead instead wants W1 itself to generate after timeout, that is a
separate ruling because the actual W1 base currently stops. Do not resolve
that contradiction by changing W1 behavior implicitly.

At signing, compare **all five** bytes at the executed night commit with W1:
R1 driver, R1 runtime, thermal gates, runtime config, new phase module. Name
that exact executed commit in the slot record. Also bind/review the shared
adapter hook and contract dependencies under the normal closure rule; the
five-file equality is not an excuse to leave a new executed dependency
unbound. Re-register only after identity/closure tests, the thermometry
disposition and RL-32/35 conditions are satisfied. Port no stale deadline,
S6 TODO/reset, old soak-consumer or G0-inconclusive skip from the W1 base.
Implement that check in `joulewise/align/apple/v4_registration.py`, for
example `verify_r1_executed_sources(root, slots, executed_commit)`, with a
focused registration regression that changes each of the five bytes in turn,
changes the slot's named commit, and supplies a missing phase module. A
passed filename list or the current checkout's identity is insufficient.

## Work product and verification

Changed files are this report, the copied/extended temperature replay,
`tests/test_align_r1_thermal_replay.py`, and the original replay manifest.
No production runtime, configuration, slot template, coordination file or
measurement job was modified. No subagents or external consults were used;
the independent Opus seat and final research-lead review remain external to
this seat. The base's driver/runtime/config were compared with da3187e6e;
the config is byte-identical, while driver/runtime need the changes above.

Verification commands/results and the replay commit are recorded below; this report is delivered in the following local documentation commit.
Full-suite execution is intentionally omitted under the brief's running-job
constraint. Tests use tiny synthetic temperature journals and stdlib only.
No MLX test or native claim was attempted; the lead must run the smoke and
the native collector/heater/restore/inventory checks on the eventual built
head outside this sandbox.

- Baseline copied from `78e6b19ce`: `python3.13 -B -m unittest tests.test_align_r1_thermal_replay` — **17 tests passed**.
- Extended module: the same command — **23 tests passed**, final verified run **14.059 s**, exit 0. New regressions cover fixed consume references, both bands/margins, censoring rather than borrowing later workload rows, planning offset/trace-only labeling, release versus at-cap margins, invalid capture-source refusal and no follow-up verdict after a failed self-check. All targeted test executions together were under two minutes; no suite/discovery command ran.
- The exact replay command in Section 1, with both D capture labels — **exit 0**, all **13/13** recorded outcomes reproduced, R_op exact, all nine D records release under own/consume references at both bands. Hashed input manifest unchanged from `78e6b19ce`.
- `compile(source, filename, 'exec')` under Python 3.13 for replay and tests — **PASS**, no bytecode written. Final edits after the passing unit run were indentation only.
- Default text renderer compared with the original `78e6b19ce` renderer on the same journal-derived result with follow-up output disabled — **byte-identical**. This is a renderer preservation check, not a claim that the extended JSON schema is unchanged.
- Temperature-only classifier input probe — both null, both missing-phase reasons; **original full-inventory diagnosis remains unresolved**, as detailed in Section 7.
- Desk-only invocation of `night_worst_case_s()` on W1 and source at `da3187e6e` — arithmetic reproduced in Section 8. Separate Decimal arithmetic confirmed the proposed complete-recipe sums, retry floors and minute-rounded windows. These do not verify native overhead bounds.
- `git diff --check` / staged whitespace check — **PASS**. Final review was by this seat; no independent cold review is claimed.
- Local code commit: **`eacb8c55c`**, `Extend R1 thermal replay with RL-64 consume cases and release margins`. The subsequent documentation commit contains this plan. Both stay on `design/2026-11-11-r1-followup-sol`; no push or measurement action.


## Open questions for the research lead

1. **30B null pick — missing input, blocks a complete diagnosis.** May the
   build lead provide the sanctioned full-inventory temperature/error stream,
   metadata and the original quiet/prefill/last-decode/recovery bounds? The
   alternatives are to diagnose that original capture or accept this as
   unresolved and require a new classified native capture. I recommend the
   former before building; no original-custody access is requested by this seat.
2. **Deadline/redo budget — needs a ruling before arm.** Retain two load redos
   per complete quiet recipe and enforce the conservative 66 h 45 min envelope, or
   approve a smaller global redo allowance with an explicit flagged/stop
   policy and recomputed deadline. I recommend an explicit smaller allowance
   if a roughly one-day night is required; the existing policy does not prove
   that deadline. Overhead caps also need native evidence or enforced limits.
3. **Timeout-run scope — code contradicts the W1 premise.** Approve the R1-only
   adapter callback with unchanged W1 default, or separately rule W1's own
   timeout behavior. I recommend the R1-only callback for this build. Candidate
   fields from any unreleased start stay barred until your cited disposition.
4. **Predecessor/mode comparability.** Approve the added ordinary 30B control
   after A-B-A, and confirm how to judge thermally different own-reference
   A-B-A starts or an inconclusive adoption before freezing the series mode.
   I recommend this explicit control rather than calling the earlier cold
   step the immediate predecessor. No numerical new start-spread bar is
   adopted by this seat.
5. **S6 interpretation.** The new tables support the cap at both bands on old
   passive D records, but correct the large-at-release-margin premise and
   cannot replay the 30B 1.0 °C release beyond its recorded end. Keep 1.5 for
   this arm as ruled; decide the smallest usable registered step from the
   new release record, planning/heater evidence and full D-after-D block.
6. **Smoke feasibility.** The thirty-minute smoke has a hard acceptance
   boundary; the code caps do not guarantee it can contain one full 30B run
   plus D admission. If it reaches that boundary, rule the next bounded
   diagnostic rather than treating it as permission to arm the long block.

These are my independent proposals and uncertainties, not reported
disagreements with the other seat, whose plan I have not seen. The next exact
step is research-lead reconciliation of the two plans and the missing
thermometry input; no long-block arm is authorized by this report.
