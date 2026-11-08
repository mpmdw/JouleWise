# ALIGN v4 condition-based waits: Sol and Opus agreement report

RUN_STATE 220 asks for an independent Sol build and an independent Opus build, followed by an agreement report. This is that report. The lead rules; under the window design council, Opus has the final say.

| Build | Branch and head | Document |
|---|---|---|
| Opus | `align/2026-11-08-condition-waits-opus` @ `c3a6aea2b` | `docs/align/v4/CONDITION-WAITS-opus.md`, plus `scripts/align_v4_start_state.py` and its 18 synthetic tests |
| Sol | `align/2026-11-08-condition-waits-sol` @ `8f7af9987` | `docs/align/v4/CONDITION-WAITS-sol.md` |

Both builds start from `align/2026-11-08-v4-r11` @ `05b6d04cb`. Each was written without reading the other. I read Sol's build only after Opus was committed and pushed.

Two inputs were integrated after both builds existed:
- **Timing receipts.** `docs/perf/SPEED-TOOLBOX.md` on `main` @ `32b2a3ca4` defines a timing receipt as a boundary marker only, with no computation inside a window.
- **Harvest hand-off.** It is being designed on `align/2026-11-08-harvest-off-{sol,opus}`. At the time of writing only the Sol branch exists on origin.

Blinding: neither build, nor this report, read any energy, residual, score or alarm value.

## 1. Where both seats agree (high convergence)

| # | Point | Opus | Sol |
|---|---|---|---|
| A1 | The between-window "quiet start state" has no definition. Today it is an informal 15-25 min estimate plus a packet entry with a free-text basis (`v4_cadence.py:29`). Defining it is a **registered start-state and admission design** decision, made before W1 | §0, §4 | §1 row 1, §2 P1, §5 |
| A2 | Replace elapsed time with a measured joint start-state release. The signals are the R1-final fast and slow SMC picks (TV0h/Tf08 are provisional), fans, OS level and PM state, idle package power, and the battery predicates, each held over a stability interval with a floor and a ceiling | P1 | P1 |
| A3 | Heavy between-window work (finalize, hashing, custody traffic, triage) runs **before** the final stability interval. The stability interval starts only after the last disruptive operation | P1 ("wholly after finalize, push and offload") | P1 ("floor at the last disruptive operation; reset after new disruption") |
| A4 | The live start state is certified on the MBP by a native evaluator, never by an Air-built boolean in the packet | P1 (SSE record digest in triage) | P1 (native receipt, checked again at GO) |
| A5 | The hazard arm's 180 s clean-run guard (30 s intervals, 2,700 s cap) is the quiet criterion. Do not add a fixed sleep after READY | P2 | P2 |
| A6 | **Keep the 300 s member idle for v4.** A shorter idle can turn into a longer G0, which then uses up T_dead (time before the deadman). The idle also carries admission, R capture and baseline roles. The paired study is deferred to v5 | P3 | P3 |
| A7 | Keep G0, G1 and H, their caps, and the X2/X4/X7 outcomes. The only lever is the already-ruled S6 tuning | §1d, §4 | P4 |
| A8 | Keep the 60 s chain settles, the 20 s closing countdown, the warmup settle and the sampling tails | P4 | P4 |
| A9 | The committed evidence is LEAD-RULINGS-2 Round 7. Fans stop at about 180 s; there is a shared cooling mode with τ about 430-510 s; slope settledness takes 840-1,040 s after a 900 s load. No committed record times a between-window cool-down | §3a | §3, TAIL |
| A10 | One native characterization run of at most 2 h, in a gap, on the magistrate, with timing and thermal outputs only. R1's `idle-until-soak` recovery curve and gated-run fields are free evidence | §3b-c | §3, §4 |

## 2. Where the seats differ, and the recommended resolution

| # | Topic | Opus | Sol | Recommended resolution |
|---|---|---|---|---|
| D1 | **Arm at the ceiling?** | Yes, for a level-only failure with an offset of 3 °C or less, with a DISCLOSE flag. Hold above 3 °C | **Never.** A ceiling gives `not_ready` and returns to the magistrate. If ambient makes Q unreachable, stop for a setup or cohort decision | **Sol.** A registered band that windows may arm outside of is not start-state equivalence. Anti-idle cover instead: a `not_ready` triggers an ambient and thermostat check and one more attempt; two in a row go to the lead as a setup decision (RS 221 rule 5). Opus withdraws `ceiling_level` |
| D2 | **Temperature band: one- or two-sided** | One-sided (≤ R_soak + δ), following R5-1 and R1's `idle-until-soak` | Two-sided Q ± δ. Being colder is not the same initial condition. G0/G1 stay one-sided | **Sol.** Between-window equivalence is a cohort property, and a cold start is a different state. G0 and G1 remain one-sided, as Sol says |
| D3 | **Reference** | R1's 30-min soak (`r1_soak_reference.json`) | A Q bound to the **final** mode and picks. R1's initial soak precedes the A-B-A comparison, so it may not represent High Power or changed picks. Otherwise CW-1 may capture Q under a prospective ruling | **Sol.** This catches a gap in the Opus build. Q comes from R1's soak only if R1 keeps Automatic mode and keeps its picks. Otherwise a prospectively ruled CW-1 reference capture supplies it before registration |
| D4 | **Slope rule** | 300 s OLS, ≤ 0.1 °C/min | G0's own rule: 60 s OLS, ±0.2 °C/min | **Sol by default** (same predicate as G0, already native-qualified). CW-1 reports both, using the Opus tool's `--grid`. Tighten only if a 0.2 °C/min release later leaves the band within the 1,800 s observation |
| D5 | **Stability interval** | 300 s | 180 s, the same continuous trace as the guard's clean run, so release is the max of the conditions, not their sum | **Sol**: 180 s, shared with the guard on one stamped trace. If the components cannot share a trace, run them sequentially (Sol P2) |
| D6 | **Floor and ceiling** | Floor 600 s after terminal completion. Ceiling at the later of terminal + 2,700 s and quiet + 1,200 s | Floor 300 s after the last disruptive operation, reset on new disruption. Ceiling 1,800 s per attempt | **Sol.** The floor anchored on disruption is the principled one, and with D1 there is no arm at the ceiling, so a shorter attempt ceiling only costs a re-attempt |
| D7 | **Fans** | ≤ soak median + 100 rpm | Q ± max(100 rpm, 3 SD); if the reference fan is stopped, require stopped | **Sol** |
| D8 | **Power** | p95 ≤ 1.0 W (the registered idle-admission bar) | Each trailing 30 s mean within Q_P ± max(0.25 W, 10 %, 3 SD), from powermetrics, distinct from KM003C | **Sol**, with the idle-admission bar kept as an upper limit. A missing channel blocks release |
| D9 | **Display** | Drop the magistrate's 300 s dwell. Sleep the display at the start of cool-down; the guard judges | One shared interval: display observed asleep throughout, at least 300 s since the last sleep transition, guard READY, P1 satisfied; release at the maximum. A wake restarts the display floor. R0's 300 s rule stays (AUTH 209) | **Sol's form.** Sleeping the display at the start of cool-down makes the 300 s floor overlap for free. The two builds then agree on the saving (about 0-5 min) |
| D10 | **Member-idle shadow predicate** | Offline, print-only computation of when G0's predicate first held during idle, run on R1 and W1 journals | Not proposed; notes that idle-shortening needs outcome-bearing evaluation in a separate lane | **Adopt as offline analysis only.** It reads timing and thermal fields after the window and has no control effect. It is evidence for v5, not grounds for a v4 switch, so the Opus pre-C1 switch option is withdrawn |
| D11 | **CW-1 workload** | D 8-bit decode, then a light tail, simulated finalize and offload, then a 40 min recovery | Two synthetic MLX pulses of 900 s each, each followed by an observed 1,800 s recovery, with a display transition in the second. No weights. Load transfer to D must be bridged by R1 fields | **Merge.** Run Sol's structure. Pulse 1 is the R0 long-decode harness on D (the weights are already resident, which closes the load-transfer gap Sol flags). Pulse 2 is a finalize, hash and offload stand-in plus a display transition. Each recovery is 1,800 s, even after an early shadow release. Total stays at or under 2 h, with Sol's pass criteria |
| D12 | **Credited saving** | About 20 min per window as the central scenario (range -2 to +30) | **0 measured.** About 10-20 min only for an already-cool case. On the hot tail, -5.3 to +8 min | **Sol for planning.** Credit 0 until CW-1 and a first real turnaround give a before-and-after (the toolbox's measure-first rule). The Opus range stays as a scenario. Planning keeps the 30-45 min turnaround |
| D13 | **Native arm overhead** | Not quantified | Pilots 8-10 `arm_decision.json`: 276.6, 306.5 and 276.6 s elapsed for the whole arm | Adopt Sol's figure. It is the floor for the in-job part of the turnaround and cannot be saved by these proposals |

## 3. The two integrated points

**Timing receipts are boundary markers only (SPEED-TOOLBOX, `32b2a3ca4`).**
- The start-state evaluator runs **between windows, before GO**. Nothing is computed inside a window.
- Its timing receipt is a handful of turnaround markers appended to journals that are already open: phase name, `monotonic_ns` and wall time at terminal completion, quiet start (the end of the last disruptive work), release or `not_ready`, and GO.
- Durations and the ledger are computed afterwards, off the MBP, by `joulewise.align.window_timing`. Neither the Opus tool nor Sol's design adds a marker inside a member.
- The evaluator's 1 Hz state trace is admission evidence (as the arm's dwell trace is), not a timing receipt. It ends at GO, and its own CPU use is disclosed and kept within the monitor budget (Sol P1).
- The later Opus option of moving the evaluator into the launchd job before the hazard arm is still pre-GO. It stays an engineering item that needs a guard replay and a native smoke.

**Harvest hand-off.**
- Finalize, harvest and offload during cool-down are judged by **the same start-state band**. They are disruptive work: the floor and the stability interval start only after the last of them ends (A3, D6), so their heat and I/O cannot leak into the start state.
- Whatever `harvest-off-{sol,opus}` decides changes only how long the disruptive phase lasts. It does not change the band.
- If the harvest leaves the MBP, the disruptive phase shrinks to finalize and push, and P1's release time is then set by physics. If any harvest step stays on the MBP, cool-down overlaps it entirely.
- Either way, the harvest design must emit a "last disruptive operation" boundary marker that the evaluator can read.

## 4. Evidence each supported proposal still needs

| Proposal | Before registration | Before claiming a saving |
|---|---|---|
| P1 joint release (D1-D8 as resolved) | Q source ruled (D3); channel and decoder definitions for the fans and powermetrics rail; a native evaluator and receipt; synthetic tests covering every failure case Sol lists in its §4 tail | CW-1 passes Sol's criteria on both recoveries; R1's post-D `recovery_curve` bridges load transfer; guard replay on idle traces (R0 re-run 11 idle phase, R1 soak, CW-1 soak) shows 0 false holds |
| P2 shared display and guard interval | The v4 registration copies the hazard thresholds (absent from the kit today; needed for W1 anyway); a continuity receipt over one stamped trace | CW-1 pulse 2 display-transition replay |
| Idle shadow (analysis only) | none | none; it is v5 evidence |
| Unchanged waits (G0/G1/H, idle, settles) | none | none |

## 5. Recommended ruling (for the lead; Opus final say)

1. **Adopt P1 as registration text before W1, in Sol's form.**
   - The reference is Q, bound to the final R1 mode and picks.
   - Temperatures are two-sided, Q ± δ, and the slow-sensor slope follows G0's rule (±0.2 °C/min over 60 s).
   - Fans: Q ± max(100 rpm, 3 SD), and a stopped reference fan means stopped.
   - Power: trailing 30 s means within Q_P ± max(0.25 W, 10 %, 3 SD), under the idle-admission bar.
   - Display, OS level and PM state as Sol specifies; the battery predicates unchanged.
   - 180 s stability, shared with the guard; a floor of 300 s after the last disruptive operation; a ceiling of 1,800 s per attempt.
   - **Never arm at the ceiling.** `not_ready` gets one re-attempt after an ambient check; a second goes to the lead.
   - The evaluator is native and is checked again at GO. The `quiet_start_state` triage entry binds its receipt digest instead of a free-text basis.
   - Finalize, harvest and offload are disruptive work under the same band.
2. **Adopt P2 in Sol's shared-interval form.** Sleep the display at the start of cool-down; R0's 300 s rule is unchanged; no post-READY sleep.
3. **Keep the member idle at 300 s, along with G0/G1/H, the settles, the countdowns and the tails.** The idle shadow runs off the MBP as v5 evidence only.
4. **Authorize one CW-1 run of at most 2 h** in the merged form (D11), in a gap after R1. At W1 registration:
   - If Q and the channel definitions exist, register the band. It is not a fixed timer, so it cannot be "too short"; only its release time is unknown.
   - If Q or CW-1's pass is missing, register the incumbent cool-down for W1 and its cohort, with the band recorded as a print-only shadow. That is Sol's fallback, and it avoids a never-arm rule tuned on no data.
   - Until a measured before-and-after exists, credit **0 min** of saving and keep the 30-45 min turnaround in planning.
5. **Engineering follow-ups.** Neither changes the registered design: add a lower-band option to `align_v4_start_state.py` so it can replay the two-sided Q, and emit the turnaround boundary markers listed in §3.
