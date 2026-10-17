claude-fable-5-1

# Block 6 acceptance: cold ruling (Fable 5.1, 2026-10-17)

Judged: the fill `git diff 63c388776 df8373292` of `docs/registrations/block6_replication_DRAFT.md`, the acceptance
file at `5ffbe15c4` (`configs/b6/registration/acceptance.json`, SHA-256
`ea130c87ece4e8b557a6357f1f75df045b5a0a738db18fe5ee990a7b539ce2a8`, recomputed), the writer's DERIVATION.md and Sol's
SOL-DERIVATION.md, against the raw kit results under `/Users/edr/night-archive/threshold-validation/` and the
non-claim rehearsals under `/Users/edr/night-archive/gate-prune/rehearsal-real/`. No block-5 claim data opened.
Every number below was recomputed from raw files by the commands in §4; where I used either seat's number I say so.

## 1. Verdict per slot

| Slot | Verdict | Change, if any |
|---|---|---|
| S-4 fresh acceptance | **REGISTER** | none. Alignment reference 0.037054941476587 s, s_bracket 0.010818 s (floor binds; measured range 0.009675 s), drift budget 0.01550217418713139 s (predecessor binds), corpus the 13 quiet captures, digest as committed. All recomputed through the block-5 issuer's own functions (§4.1). Replay: 0 of 4 rehearsal sessions stopped; 2 of 7 rehearsal captures above the reference (48.009, 40.136 ms); 0 of 3 brackets above the budget. |
| S-6 M2's d | **REGISTER-WITH-CHANGE** | d = +0.180 J (prefill), +0.009 J (decode), both below 0.475 J; `idle.waited` disclosed only; 0 removed on replay. The one change is text: the ordinary arm's baseline was 75.0 to 75.2 s delivered (`idle_baseline_delivered_s`), not "the ordinary 85 s"; write what M2 did. The value stands. |
| S-7 r and T_stream_max | **REGISTER** | r = 0 within 6 × 10⁻⁷ ppm (kit −4.7 × 10⁻⁷ ± 5.2 × 10⁻⁷; my anchor-stamp fit −5.8 × 10⁻⁷ ± 5.6 × 10⁻⁷; the two differ by float-level detail of the fit, 10⁻¹³ relative). T_stream_max = 335 s. Hold 14.675 ppm. 0 of 4 sessions held; 1 of 77 runs over 5 ms at 0 ppm (5.64 ms, placement alone). |
| S-8 w and c_q | **REGISTER-WITH-CHANGE** | w = 5.432 J per CPU-s registered as the measured value. c_q: 0.55 CPU-s per interval governs for windows (the kit's median with Spotify and the orphaned `hazard_monitor.py` subtracted); 0.73 is printed beside it as the as-measured kit value. **The exclusion clause is not adopted for round 1**: `contention.request_overlap` stays DISCLOSE (as the catalog at 5ffbe15c4 already has it), with C, k and E_add at the registered w printed per flagged run, and E_add at the background-priority w = 0.0862 printed beside it as the labelled alternative. Reason in §2a. |
| c_q (§8.5) | see S-8 | 0.55 governs; 0.73 beside it. |
| S-12 printed cross-check (M14, M10) | **REGISTER** | values as filled; they exclude nothing (decided 2026-10-15). Not recomputed from the meter stream (NOT EXECUTED: out of my 90 minutes); the eight segment values agree between the two seats to the printed digit. |
| S-5, S-9, S-11 | **HOLD** | correctly left open: no pack smoke exists. M15's decode lengths stay "comparison only". |
| D25 to D30 | **REGISTER** D25, D28, D29, D30; **D26** register with the reading in §2c; **D27** replaced by the S-8 ruling above. |

## 2. Rulings on the questions

**(a) S-8: adopt the exclusion as registered, at background-priority w, or keep a flag?** Keep the flag; do not
adopt either exclusion for round 1. The registered rule removes 12 of the 53 known-good quiet runs of 2026-10-09 (36 of
77 overall; recomputed, §4.5), which §8.7 item 1 forbids outright. The physics also refuses it: on the same 33
reference runs of 2026-10-09, phase energy regressed on outside CPU-seconds gives −0.09 ± 0.09 J per CPU-s (prefill)
and −0.29 ± 0.31 (decode), and the two runs carrying 20 CPU-s of outside work (refcorpus r01, r03) sit at 11.11 and
11.44 J prefill, 25.70 and 25.58 J decode, inside their siblings' scatter, where w = 5.432 predicts +109 J and even
w = 0.0862 predicts +1.7 J. A conversion whose prediction the known-good data contradict by two orders of magnitude
cannot be the physics that excludes a run; w = 5.432 is the cost of a P-core at full clock and interactive priority,
which the quiet machine's daemons (E-cores, background QoS; M4's in-situ daemon fit 0.17 ± 0.06 J per CPU-s) never
realize. The background-priority alternative still removes r01 and r03 (2 of 53), known-good runs, so it fails the same
test. Nothing computes E_add in code today, so adopting any exclusion would also need code before round 1; a DISCLOSE
code needs none. The remedy the charge names applies: print the registered result (E_add at 5.432) and the labelled
alternative (at 0.0862) beside each flagged run, and let the analysis decide. What would qualify an exclusion later: a
w measured for outside work as it occurs (bursts at background priority on the quiet machine) whose replay removes 0
of the 53 quiet runs.

**(b) c_q with or without Spotify and the orphaned monitor?** Without them: 0.55. c_q is the outside CPU of the quiet
machine, and the right baseline is the one the machine will have in its windows. The orphan (`hazard_monitor.py`,
pid 43816, parent 1, alive 1 d 22 h at 0% CPU, confirmed with `ps` at ruling time) is a leaked test process, not a
property of the machine; Spotify (pids 917, 921, 925; Spotify Helper is a GPU process drawing 0.128 CPU-s per
interval in every one of the 2,496 intervals) is a user program that has no place in a measurement window. Both must
be stopped before round 1 and the pre-session check must confirm them absent; with them gone, 0.73 would credit 0.18
CPU-s per interval that is not there. 0.73 is written beside 0.55 as the as-measured value. On the 0.73 versus 0.72
disagreement: both are right for the interval set each pooled (0.72 for M2's 2,391 intervals alone and for Sol's raw
re-count; 0.73 for every result-file interval pooled, 2,496, which is the registration's "median over the quiet-machine
measurement sessions"); they differ by one unit of the last printed digit, 0.054 J at w = 5.432, and change no replay
count at any w (§4.5). Immaterial, and superseded by 0.55.

**(c) Can M2's d qualify S-6, and is the proportional carry the right reading?** Yes, and no. Block 6's own waiting
rule retries a baseline until one passes or 1,500 s elapse (§8.3, draft line 313), so a block-6 waited run is a run
admitted after up to 25 minutes of intermittent disturbance and one passing baseline; M2's long arm (2,700 s with 7 to
24 restarts, then a 75 s baseline, then the run) is that same object with a longer wait, and a continuous-20-quiet-
minute arm would have measured a cleaner machine than block 6 will ever deliver. The fallback timeline applies to both
arms alike; d is a paired difference over five quads and its interval (−0.008 to +0.368 J) already carries the per-run
alignment scatter; the point estimate and the interval's upper end both sit below 0.475 J. The rule reads d in joules
on the reference workload; the proportional carry (+2.35% × 26.1 J = 0.61 J) is not the rule, and the measurement
cannot support it: a power-offset model gives 0.6 W × 0.62 s = 0.37 J, a fixed-cost model 0.18 J, and the interval
includes zero, so no carry is distinguishable from none. The cells without waited runs are printed either way. Register
d = +0.180 J, disclose only.

**(d) S-7: keep T_stream_max = 335 s?** Yes. 335 s is not a measurement that is missing; it is the longest stream any
`_v5` member is programmed to have (`sizing_b5.json`, registration 0.14 and 5.5), which block 6 replicates unchanged,
and under waiting admission every try starts a fresh stream, so waiting cannot lengthen it. The rehearsal spans (median
90.0 s, max 106.8 s over 77 runs) sit well under it. Sol's "undetermined" is wrong for that reason, and Sol is right
that the kit's 2,292.6 s sampler duration is not the quantity. With r measured at zero the hold stays above |r| for
every T_stream_max below 20,000 s, so nothing turns on it; the machine test reports the spans and a span above 335 s
replaces it, as the draft says.

**(e) Is a 13-capture, one-job corpus adequate for a fresh acceptance?** Yes. It meets block 5's own issuance rule
(revision six, minimum 12; the derivation was run through the issuer's functions, §4.1). The only constant that enters
a number, s_bracket, is set by the D-125 floor, not by the corpus; a corpus from more days could only raise it (the
7 rehearsal captures from two other days span 29.35 to 48.01 ms), and its joule weight is 0.175 J on a 26.1 J prefill,
below the 1 J attribution limit, while b_op uses the session's own |post − pre| whenever that is larger. The two
corpus-dependent constants only flag, and both were checked against captures from other days (2 of 7 above the
reference, exactly the two above block 5's reference; 0 of 3 brackets above the budget). A HOLD would change a flag
level, not a number. Note for the record: the reference is the maximum quantized half-even to 10⁻¹⁵ s, so capture-011
sits 2.8 × 10⁻¹⁶ s above it and would flag itself; block 5's reference has the same construction. It is a flag; no
change.

## 3. What either seat got wrong

- **Sol:** offering 19.33 J per CPU-s as the "literal maximum" for w. That arm (s007, interactive 5%) delivered
  0.0052 CPU-s/s of load while outside daemons rose by 0.154 CPU-s/s, so its 0.100 W step is the daemons' power
  divided by the load's CPU time; the kit flagged it, and M14's independent one-core loads (5.42 and 5.21 W on the
  rails for a full core) put w near 5, not 19. Sol's own text recommends the clean burst; the literal number should
  not have been carried as a candidate. Also: T_stream_max "undetermined" (see 2d) and "M2 cannot qualify S-6" (2c).
- **Writer:** "the ordinary 85 s" for M2's ordinary arm; M2 delivered 75.0 to 75.2 s baselines. "Outside processor
  time adds at most 0.03 J per CPU-second": on the 33 reference runs the fitted slope is −0.09 ± 0.09 J per CPU-s
  (prefill); the conclusion (far below 5.432) stands, the figure should carry its uncertainty. c_q including the two
  user programs (overruled in 2b). D26's proportional carry is correctly flagged but is not the rule (2c). Every other
  value and every replay count the writer printed I reproduced exactly.
- **Both seats** agree with me on S-4 to the last digit, on d, on r, on the 20 burst values, on 5.432, and on the
  replay counts 12/53 and 36/77 (registered) and 2/53 and 14/77 (background priority).

## 4. Re-derived numbers, with the commands

All Python: `/opt/homebrew/bin/python3.13 -I -B` (the issuer import used `-B` with `PYTHONPATH` set to this worktree,
`TMPDIR=$(mktemp -d /private/tmp/accept.XXXX)`, `JW_B5_SYNTHETIC_ONLY=1`). Q = `/Users/edr/night-archive/threshold-validation`.

### 4.1 S-4 (block 5's derivation, run through its issuer's functions)

Corpus: every capture with `condition == "quiet"` in `Q/m1-capture-stop-line/attempts/1/collection.json` (10) and
`Q/m13-meter-edges/attempts/1/collection.json` (3), each value the `b_fiducial_s` lexeme of its
`instrument_evidence.json` (all 13 `status: valid`, `clock_anchor.status: bounded`, 59 pulses; the 4 `load` and 4
`utility` captures of M1 left out, 2 of the utility ones invalid).

```
spec=importlib.util.spec_from_file_location("issuer","scripts/issue_calibration_acceptance_generation.py")
m=module_from_spec(spec); sys.modules["issuer"]=m; spec.loader.exec_module(m)
st=m._corpus_statistics(members)            # n = 13
ref=Decimal(st["maximum_s"]).quantize(Decimal("1e-15"), ROUND_HALF_EVEN)
S=m.envelope_screen(Decimal(st["range_s"]).quantize(Decimal("1e-6"), ROUND_HALF_EVEN), m.D125_SCREEN_FLOOR_S)
Q99=m.two_draw_prediction_lexeme(m.student_t_quantile("0.995",12), st["sample_sd_presentation_s"]["value"])
w=m.within_window_prediction(members, {M1 ids: "M1", M13 ids: "M13"})
C=max(predecessor 0.01550217418713139, Q99, S, w["prediction_99_within_window_two_draw_s"])
```
Output: max 0.037054941476587284 (M1/capture-011), min 0.027380174613889405 (M1/capture-000), range
0.009674766862697879 → 0.009675; floor 0.010818 → **S = 0.010818**; **reference 0.037054941476587**; mean
0.030721483979622774, s 0.002808268859283743, t(0.995,12) 3.0545395893929021, **Q99 0.012131079260684415**; K = 2,
df 11, s_within 0.002917865816168467, **Q99_within 0.01281606527393005**; **C = 0.01550217418713139** (own-corpus
alternative 0.01281606527393005). Issuer constants: REVISION_FIVE_MINIMUM_CORPUS_SIZE 12 (block 5's file:
`registration_revision` 6, `minimum_corpus_size` 12), SUCCESSOR_MINIMUM_CORPUS_SIZE 19, ENVELOPE_MINIMUM_CORPUS_N 17.
File digest: `git -C /Users/edr/code/JouleWise show 5ffbe15c4:configs/b6/registration/acceptance.json | shasum -a 256`
→ ea130c87…539ce2a8; its 13 corpus lexemes equal the 13 above.

Replay on the rehearsal captures (`runs-parent/*/instrument_validation/*/instrument_evidence.json`): alpha-1 pre
30.599 post 30.097 → b_op 30.599 + max(0.502, 10.818) = 41.417 ms; corpus18 29.350/30.500 → 41.318; gamma-2
32.849/40.136 → 50.954; gamma-1 pre 48.009, b_pre + s_bracket = 58.827. All under 139 ms: 0 of 4 stopped.

### 4.2 S-6 (M2)

`Q/m2-long-wait/result.json` → `measured.run_table` (20 rows, quads 0..4, arms N L L N). d = mean(L) − mean(N):
prefill 7.845990 − 7.665669 = **+0.180321 J** (+2.35%); decode 15.966076 − 15.957175 = **+0.008901 J**. Quad
differences prefill [0.1159, 0.2147, 0.1198, 0.4241, 0.0271], SE 0.067779, 95% (t 2.776) −0.0078 to +0.3685; decode
[0.0943, −0.1776, 0.0716, 0.1375, −0.0813], SE 0.059437, −0.1561 to +0.1739. Equal to the kit's `long_minus_ordinary`.
Flags: 8 long waits capped at 2,700 s (longest quiet stretch 148.5 to 992.6 s, 7 to 24 restarts).
`idle_baseline_delivered_s` 74.9 to 75.2 s on all 20 runs; prefill 0.29 to 0.31 s at about 25 W, decode 0.99 s at
about 16 W.

### 4.3 S-7 (M3)

`Q/m3-clock-rate/attempts/1/clock-end.jsonl`, 5,147 rows, one boot `ea2d3ec8-…`, network time "already off". Centred
OLS of (realtime_ns − monotonic_raw_ns) on monotonic_raw_ns using the `anchor` stamps (the kit's definition,
`quiet_kit/analysis.py:390-394`): slope **−5.77 × 10⁻⁷ ppm, SE 5.6 × 10⁻⁷**, max residual 0.028 ms, span 51,513.96 s.
Using `finished` stamps: −2.0 × 10⁻⁶ ± 8.6 × 10⁻⁷. Kit: −4.67 × 10⁻⁷ ± 5.19 × 10⁻⁷. All zero within error. Hold
5 ms / 335 s − 0.25 = 14.675 ppm; 335 s from `sizing_b5.json` `T_stream_max_s`. From the council's `runs.json`
(77 runs): m > 5 ms at 0 ppm: 1 (5.64 ms); stream span median 90.0 s, max 106.8 s.

### 4.4 S-8 (M4) and c_q

`Q/m4-contention-watts/result.json` → `measured.bursts` (20): w_i = `added_energy.value` ÷ (added ÷ below ×
permitted) = below ÷ permitted. Range 4.213 to **5.432** (s033: 3.5780553 J ÷ 0.6587 CPU-s). `measured.arms`:
background 5% 1.287 ± 2.303, 20% 2.025 ± 1.469, **100% 0.0862 ± 0.0106**; interactive 5% **19.333 ± 3.662 (flag:
outside contention during s007; outside rate +0.154 CPU-s/s against a load of 0.0052)**, 20% 1.504 ± 0.292 (flag s009),
100% 4.969 ± 0.015. `daemon_watts_per_cpu_rate_fit`: slope 0.1722 ± 0.0565, n 62. Line at w = 5.432:
0.475 / 5.432 = 0.0874 CPU-s.

c_q: every record with `outside_total_cpu_s_per_s` and `elapsed_s` under every `Q/m*/result.json`, de-duplicated on
`interval.monotonic_raw_ns`, kept at 9 ≤ elapsed ≤ 11 s, C = rate × elapsed. M2 2,391 → median **0.72**; M4 89 →
0.79; M2+M4 2,480 → **0.73**; all tests 2,496 → **0.73** (p10 0.44, p90 1.82, min 0.33, max 15.96). Subtracting the
listed `Spotify`, `Spotify Helper` and pid 43816 entries per interval: **0.55** in every pooling. Listed contributors
averaged over all intervals: Spotify Helper (925) 0.128 CPU-s per interval in 2,496 of 2,496; launchd 0.107; Python
43816 0.056 in 2,243. The kit's `contention.interval` sums ps-listed processes outside the kit's tree and excludes
`kernel_task` when listed (ps does not list pid 0), so it is the registered C.

### 4.5 Replay of the outside-processor rule (77 rehearsal runs)

For each run in `/private/tmp/claude-501/silly-council-opus/runs.json` (request [ss, se] from each bundle's
`sampling_started`/`sampling_stopped`; I checked one bundle's `events.jsonl` against it), the `kind == "interval"`
records of `<session>/custody/hazards/monitor/contention.jsonl` overlapping [ss, se] (k = 1 for 60 runs, 2 for 17);
C = Σ (outside_total − listed agent processes `2.1.294`, `Python`, `claude`, `codex`, `node`) × elapsed. Session
medians per interval, agents out: 10-09 0.52, alpha-1 4.15, gamma-2 5.86. Excluded when C − k c_q ≥ 0.475 / w:

| w | c_q | 10-09 (53) | alpha-1 (13) | gamma-2 (11) | all 77 |
|---|---|---|---|---|---|
| 19.333 | 0.73 / 0.72 | 12 | 13 | 11 | 36 |
| 5.432 | 0.73 / 0.72 | 12 | 13 | 11 | 36 |
| 5.432 | 0.55 | 14 | 13 | 11 | 38 |
| 5.432 | 0.52 | 16 | 13 | 11 | 40 |
| 4.969 | 0.73 | 12 | 13 | 11 | 36 |
| 0.1722 | 0.73 | 3 | 7 | 10 | 20 |
| 0.0862 | any of the four | 2 | 4 | 8 | 14 |
| flag only | — | 0 | 0 | 0 | 0 |

The 12 quiet runs excluded at 5.432/0.73 are the writer's 12 (decode b01-b1 C 2.60; prefill b06-a1 1.71, b06-b2 0.86,
b07-a1 1.28, b08-b2 4.07, b09-b1 0.98, b09-b2 1.87; window-end-r3 2.52; refcorpus r01 20.23, r03 20.18, r05 1.58,
r06 1.99). With agent processes counted in C: 46 of 77.

Energy against C on the 33 `neg8-*` reference runs of 10-09 (same workload): prefill slope −0.0870 ± 0.0858 J per
CPU-s, decode −0.2893 ± 0.3123; r01/r03 (C 20.2) prefill 11.11/11.44 J, decode 25.70/25.58 J.

### 4.6 Processes at ruling time

`ps -o pid,ppid,%cpu,etime,command -p 43816` → alive, ppid 1, 0.0% CPU, elapsed 01-22:45:52,
`…/JouleWise-wt-b6-s3cold-fix/scripts/hazard_monitor.py --config …/.scratch-fix/tmp/s3-run/…/config.json`.
`pgrep -lf Spotify` → 917 Spotify, 921 and 925 Spotify Helper (925 is `--type=gpu-process`). Not stopped by me (a
cold judge changes no system state); the orchestrator stops them before round 1.

### 4.7 Code state

`git -C /Users/edr/code/JouleWise show 5ffbe15c4:configs/b6/flag_catalog_b6.json` lines 577-584:
`contention.request_overlap` effect **DISCLOSE**, note "exclusion needs M4's w times max(0, C − k*c_q) ≥ F_min/4".
`git grep` over `joulewise/` at 5ffbe15c4 for `e_add|joules_per_cpu|c_q`: no computation of E_add; `flags/catalog.py:125`
(block 5's catalog) still has the code as EXCLUDE_MEMBER with the per-process 0.05 CPU-s/s rule, which block 6's
catalog supersedes.

## 5. What I ran

Read: CHARGE, TASK.md, the fill diff, DERIVATION.md, SOL-DERIVATION.md (§S-4 to §S-12), the draft's §8.5, §8.6, §8.7,
§14, D25 to D30; `scripts/issue_calibration_acceptance_generation.py` (constants, `_corpus_statistics`,
`envelope_screen`, `envelope_ceiling`, `two_draw_prediction_lexeme`, `within_window_prediction`); block 5's
`calibration_acceptance_d079_v2_n24_25g83_r2.json` (revision and predecessor fields only); the kit's
`hazards/contention.py` (interval accounting) and `quiet_kit/analysis.py:372-394` (M3 fit); `sizing_b5.json`;
the b6 flag catalog entry. Executed: §4.1 to §4.7 above (all in the foreground; no subagents). NOT EXECUTED: a raw
re-integration of M14's meter stream, M5, M9, M10, M13, M15 and M2b (no slot turns on them; the two seats agree on
their printed values); a replay over block 5's sessions (blinded; stays S-16); killing the orphan or Spotify.

## 6. Conditions before round 1 (from this ruling)

1. Stop pid 43816 and close Spotify; the pre-session check confirms the process list is free of both.
2. Draft text: S-8 row and §8.5 carry "DISCLOSE for round 1; E_add printed at w = 5.432 and, labelled, at 0.0862;
   c_q = 0.55 (as-measured 0.73)"; S-6's "ordinary 85 s" becomes "ordinary baseline, 75 s delivered in M2".
3. `tests/test_b6_registration.py:29` (asserts the file is absent) is updated to assert it loads with
   `defaults_used == []`, as the writer proposed.
