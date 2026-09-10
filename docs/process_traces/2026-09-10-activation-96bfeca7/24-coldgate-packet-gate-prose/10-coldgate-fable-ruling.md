# Cold-gate Fable ruling — packet 24 (contract prose for the epoch-representation allowances)

Cold seat: Claude Fable 5.1, fresh non-interactive session, worktree detached at `58d4696b` (verified by
`git rev-parse HEAD`). Written 2026-09-10. Packet digest as briefed: `8971acb5ea2d1cd9` (not recomputed; the
packet directory contents were read as they stand).

## Contamination disclosure

Before I opened the packet, the harness had already placed three texts into my context without my asking: the
global `~/.claude/CLAUDE.md` (writing standard and skill pointers), this worktree's `CLAUDE.md` (Codex bridge
notes), and the one-line index `MEMORY.md` of the auto-memory store, which includes a 2026-09-10 pointer titled
"Sensible gates directive" summarised as "every tolerance sized to the instrument (~1 J / ~5 J), never
microscopic". I did not open any memory file, `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/decision_log.md`,
`docs/process/`, any process trace outside this packet directory, or `.claude/`. After the packet I read only:
`docs/contracts/measurement_methodology.md` lines 55–85 and 288–318; `joulewise/environment_admission.py` lines
15–30, 74–132, 140–200; `joulewise/controller.py` lines 2440–2640; the `CooldownPolicy` class in
`joulewise/schemas.py`; `tests/test_gate_sensibility_rounding.py` lines 1–28 and 123–148 plus a grep of its test
names; a grep of `joulewise/adapters/powermetrics.py` for `duration_s` (line 334); and Exhibit E §B (lines
305–474) plus its heading list. The memory index line above is the only steer I received on the design question;
the ruling below is argued from the code and the arithmetic, and it happens to agree with that line.

## Verdicts on Exhibit C

**F1 (should_fix) — UPHELD.** The categorical sentence "A 10 μs deficit in span or coverage still refuses" is
false for coverage. Reproduced on the live code at `58d4696b`: with `subwindow_s = 0.75` and 40 retained
readings, 13.35 μs of missing coverage recovers (probe 2). The allowance is 2 ULP per retained reading, so it
crosses 10 μs at 21 retained readings (probe 5). The claim is true at the production policy, where at most about
seven readings overlap the window (allowance ≤ 3.34 μs), and the exact edge there is sharp: a 12 ULP deficit
(2.861 μs) admits, a 13 ULP deficit (3.099 μs) refuses (probe 4). The span claim is true (span allowance is a
fixed 1 μs). Disposition: prose, per the design ruling below.

**F2 (should_fix) — UPHELD.** "Evidence end" and "clipped start" are used in the bullet before either is built.
The replacement A2 text defines capture start, evidence end, evidence start, cutoff, retained reading, clipped
start, overlap, coverage and span in that order, each from the clock readings the code actually takes.

**F3 (nit) — UPHELD.** The first admission comparison is a duration against a duration (the baseline's summed
sampler intervals against attempt end minus attempt start); only the second, the capture-interval containment,
compares epoch timestamps against epoch timestamps. The replacement A1 text separates them.

Opus refuter F5 (four ULP exceed 1 μs from epoch 2^31, 2038-01-19) is confirmed by probe 1 (4 ULP at 2^31 =
1.907 μs) and is fail-closed, so no prose change is needed beyond the "at epoch 1.789e9" qualifier already present.

## A1 replacement text

Replaces `docs/contracts/measurement_methodology.md` lines 66–80 exactly as excerpted in Exhibit A (the first
five lines are unchanged and are repeated so the block pastes cleanly). Every clause was checked against
`joulewise/environment_admission.py` lines 20–24, 74–125 and 168–192.

```text
both attempts preserve distinct raw artifacts and provenance. A persistent
failure either aborts (production) or records the exploratory-only,
unwaivable `environment_admission_failed` claim barrier (`on_fail: flag`).
There is no skip disposition in a fixed-n campaign. A lightweight post-run
display/screensaver/HID observation makes within-member transitions visible.
Each admission attempt records its start and end times as clock readings
(seconds since the Unix epoch, stored as binary64 floating-point numbers).
Strict reduction then makes two containment checks, both refusing with
`environment_admission_missing`. First, a duration check: the admitted
baseline's duration, which the sampler produces by summing its per-sample
elapsed intervals, must be positive and must not exceed the attempt's span,
which is the stored end time minus the stored start time, by more than
1 μs. Second, a timestamp check: the attempt's idle telemetry records each
carry an endpoint timestamp and an elapsed interval; the capture interval
runs from the earliest (timestamp minus elapsed) to the latest timestamp,
and it must start no more than 1 μs before the attempt's start time and
end no more than 1 μs after the attempt's end time. A record without a
finite timestamp and a positive elapsed interval refuses outright. The
1 μs allowance exists because the compared numbers were formed on
different arithmetic paths (a sum of sampler intervals against a
difference of stored clock readings, or a clock reading reconstructed from
a sampler record against one stored directly), so they can differ by a
few representable steps while describing the same instant. A binary64
epoch value near 1.789e9 has representable steps 0.238 μs apart, and four
steps are 0.954 μs, inside the allowance. The allowance never credits
unobserved time: a baseline longer than the attempt by 10 μs, or a
capture endpoint 10 μs outside the attempt, refuses, as does an endpoint
one sample interval (100 ms) outside it.
```

## A2 replacement text

Replaces the whole cooldown bullet, `docs/contracts/measurement_methodology.md` lines 295–314 (Exhibit A stops at
line 312 mid-sentence; the two closing lines "recorded in the trace) and are recorded in the following
repetition's / measurement quality." are kept verbatim at the end). Every clause was checked against
`joulewise/controller.py` lines 2490–2575 and the `CooldownPolicy` defaults in `joulewise/schemas.py`.

```text
- Between live repetitions, cooldown v2 holds until the retained evidence has
  both a complete 30-second wall-clock span and at least
  `coverage_fraction * sustained_window_s` of captured coverage
  (`coverage_fraction = 0.8` by default, so 24 s of the 30 s window), and
  its duration-weighted idle-power mean satisfies the one-sided rule
  `rolling_mean <= reference * (1 + tolerance)` (10% by the production
  policy), while thermal pressure is Nominal. A below-reference mean
  therefore counts as recovery. The evidence is a series of idle probes,
  each a capture of `subwindow_s` seconds (5 s by the production policy).
  Every probe becomes a reading with three clock readings (seconds since
  the Unix epoch as binary64 numbers): its capture start, taken just before
  the probe began; its evidence end, taken when the probe returned; and its
  evidence start, the evidence end minus the probe's reported capture
  duration, but never earlier than the capture start (a probe that reports
  no positive duration is credited its whole capture interval). The window
  cutoff is the current time minus 30 s. A reading is retained while its
  evidence end is later than the cutoff. A retained reading's clipped start
  is the later of its evidence start and the cutoff, and its overlap is its
  evidence end minus its clipped start, or zero if that is negative.
  Coverage is the sum of the overlaps. Span is the current time minus the
  earliest capture start among readings with positive overlap, that start
  itself clipped to the cutoff. Span and coverage are tested with a small
  allowance for floating-point rounding, never for unobserved time. One
  representable step of a binary64 epoch value (one unit in the last
  place, ULP) is 0.238 μs at epoch 1.789e9. The span test allows 1 μs.
  The coverage test allows the larger of 1 μs and a summed rounding term
  that adds, for every retained reading with positive overlap, one ULP of
  its evidence end plus one ULP of its clipped start (0.477 μs per
  reading), plus one ULP of the coverage sum itself (4e-15 s at 24 s). The
  term is the worst case of the rounding in the subtractions that formed
  the sum, so it grows with the number of retained readings: 2.86 μs for
  six readings and at most 3.34 μs for the seven that can overlap a 30 s
  window when each probe lasts at least its 5 s production length. At that
  policy a six-reading coverage deficit of 13 ULP (3.1 μs) refuses, and a
  10 μs deficit refuses under any policy that retains at most 20 readings.
  A shorter `subwindow_s` retains more readings and widens the term in
  proportion (40 readings of 0.75 s: 19 μs), but even the schema's
  smallest probe length of 1 ms caps the term near 14 ms, below one 100 ms
  sample, so a missing sample refuses under every policy. An optional
  calibrated absolute ceiling is an additional upper cap and never an OR
  escape. The wait has a 5-minute cap; the cap is evaluated before release
  on every iteration, so recovery criteria first met at or after the
  deadline remain a `cap_hit` (with the late criteria
  recorded in the trace) and are recorded in the following repetition's
  measurement quality.
```

## Design ruling: (i) keep the code, state the growth and bound it

**Ruling: option (i).** No code change to `cooldown_gate`; the prose above carries the rule, the growth, the
production number, and the ceiling. Reasoning:

1. **The growth is the true shape of the error, not a defect.** Coverage is a sum of N subtractions, one per
   retained reading, and each subtraction's operands are clock readings that each carry up to half a step of
   rounding from the real instant. The worst case of that rounding is therefore proportional to N. The code's
   term (one ULP per endpoint) is exactly the quantisation limit: probe 4 shows that at the production policy a
   12 ULP deficit admits and a 13 ULP deficit refuses. An allowance that did not grow with N would be either
   looser than the arithmetic for small N or tighter than the arithmetic for large N. Neither is more honest.
2. **A ceiling (option ii) would be a number with no physical source.** `min(…, 1e-4)` is 30 times the true
   production error (3.34 μs) and would itself need a paragraph explaining why 100 μs. At policies dense enough
   to exceed it, it refuses below the real rounding error; harmless (one more probe iteration), but a rule the
   contract cannot derive from anything. It also adds code and a test on a path G2-a never exercises.
3. **Sized to the instrument, the whole question is small.** The production allowance of 3.34 μs is 1/30,000 of
   one 100 ms sample and, at 10 W, 3.3e-5 J against a ~1 J attribution limit. The physics barrier that matters,
   one missing 100 ms sample refuses, holds for every policy the schema admits (probe 1: the schema's 1 ms probe
   minimum bounds the term near 14 ms; 210,000 readings would be needed to reach 100 ms). D-161's fail-closed
   stance for physics and evidence is intact without any new code.
4. **Option (iii) candidates considered and rejected.** Rewriting the term as `2 * N * ulp(now)` is arithmetically
   the same and buys nothing. Replacing the ULP sum with a fixed instrument-sized allowance (for example 1 ms,
   1 % of a sample) would credit up to 1 ms of genuinely unobserved probe-gap time, contradicting the contract's
   own "never for unobserved time" clause, for zero benefit at the production policy.
5. **Tests.** The existing `test_r3_refuses_ten_microsecond_coverage_deficit` (six readings; 10 μs is 3.5 times
   the 2.86 μs allowance) already binds the production allowance from above, and
   `test_r3_refuses_one_missing_sample_of_coverage` binds the physics barrier. No new test is required by this
   ruling. If the lead wants the exact edge pinned, the 12-ULP-admits / 13-ULP-refuses pair from probe 4 is the
   defect-shaped input.

Physics-sized barriers untouched: one 100 ms sample refuses; 30 s span; 80 % coverage; 300 s cap evaluated
before release.

## Executed probes

All run in the foreground from the worktree root at `58d4696b`. No tracked file was edited; no git write.

**Probe 0 — test module.**
```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gate_sensibility_rounding
.............
----------------------------------------------------------------------
Ran 13 tests in 0.008s

OK
```

**Probe 1 — ULP and allowance arithmetic.**
```
$ python3 -c "
import math
u=math.ulp(1.789e9); print('ulp(1.789e9) s =',u, '; 4 ulp =',4*u, '; <1e-6:',4*u<1e-6)
print('ulp(2**31)=',math.ulp(2.0**31),'; 4 ulp =',4*math.ulp(2.0**31))
print('ulp(30.0)=',math.ulp(30.0),' ulp(24.0)=',math.ulp(24.0))
for n in (6,7,40,301):
    s=n*2*u+math.ulp(24.0); print(f'N={n}: 2N ulp + ulp(24) = {s:.4e} s = {s*1e6:.3f} us; ratio to 0.1 s sample = 1/{0.1/s:,.0f}')
print('readings needed for 0.1 s:', math.ceil(0.1/(2*u)))
print('readings needed for 1e-5 (10 us):', math.ceil((1e-5-math.ulp(24.0))/(2*u)))
print('ceil(30/5)+1 =', math.ceil(30/5)+1, '; ceil(30/0.75)+1 =', math.ceil(30/0.75)+1, '; ceil(30/0.1)+1 =', math.ceil(30/0.1)+1)
print('3.34e-6 s * 10 W =', 3.34e-6*10, 'J ; 1.435e-4 s*10 W =',1.435e-4*10,'J')
"
ulp(1.789e9) s = 2.384185791015625e-07 ; 4 ulp = 9.5367431640625e-07 ; <1e-6: True
ulp(2**31)= 4.76837158203125e-07 ; 4 ulp = 1.9073486328125e-06
ulp(30.0)= 3.552713678800501e-15  ulp(24.0)= 3.552713678800501e-15
N=6: 2N ulp + ulp(24) = 2.8610e-06 s = 2.861 us; ratio to 0.1 s sample = 1/34,953
N=7: 2N ulp + ulp(24) = 3.3379e-06 s = 3.338 us; ratio to 0.1 s sample = 1/29,959
N=40: 2N ulp + ulp(24) = 1.9073e-05 s = 19.073 us; ratio to 0.1 s sample = 1/5,243
N=301: 2N ulp + ulp(24) = 1.4353e-04 s = 143.528 us; ratio to 0.1 s sample = 1/697
readings needed for 0.1 s: 209716
readings needed for 1e-5 (10 us): 21
ceil(30/5)+1 = 7 ; ceil(30/0.75)+1 = 41 ; ceil(30/0.1)+1 = 301
3.34e-6 s * 10 W = 3.34e-05 J ; 1.435e-4 s*10 W = 0.0014349999999999999 J
```
Derived in-head from the same numbers: 30,001 readings (schema minimum `subwindow_s = 0.001`) give
30,001 × 2 × 2.384e-7 s = 14.3 ms.

**Probe 2 — Exhibit C V2 reproduction on the live code, plus production-policy deficits.**
```
$ PYTHONDONTWRITEBYTECODE=1 python3 -c "<FakeClock harness: Telemetry.measure_idle sleeps `subwindow`, returns
IdleBaseline(duration = per_reading_duration - deficit/n); cooldown_gate(..., policy=CooldownPolicy.from_mapping({'subwindow_s': subwindow}))>"
--- Exhibit C V2 reproduction (live code, 40 readings of 0.6 s at subwindow 0.75) ---
subwindow=0.75 N_target=40 deficit=1.000e-05s -> recovered span=30.0 coverage=23.99998664855957 missing=13.3514us
--- production policy: subwindow 5.0, six 4 s readings; allowance = 12 ulp + ulp(24) = 2.861 us ---
subwindow=5.0 N_target=6 deficit=1.000e-05s -> cap_hit span=30.0 coverage=23.999989986419678 missing=10.0136us
subwindow=5.0 N_target=6 deficit=2.800e-06s -> recovered span=30.0 coverage=23.99999713897705 missing=2.8610us
subwindow=5.0 N_target=6 deficit=3.000e-06s -> recovered span=30.0 coverage=23.99999713897705 missing=2.8610us
subwindow=5.0 N_target=6 deficit=1.000e-01s -> cap_hit span=30.0 coverage=23.90000009536743 missing=99999.9046us
```
Note on the 3.0e-6 row: a uniform per-reading deficit of 0.5 μs quantises to 2 ULP (0.477 μs) on the epoch grid,
so the realised deficit was 12 ULP, equal to the allowance. Probe 4 sets the deficits in whole ULPs to reach
the true edge.

**Probe 3 — admission arithmetic.** First run (stored end derived from the duration, so the span tracks the
duration; shows the four-step case admits and that endpoint shifts inside the attempt are not refused):
```
$ python3 -c "<start=1789000000.0; for dur: end=float(start+dur); refuse = dur > (end-start) + ADMISSION_TIME_ROUNDING_S;
capture_start shifts vs start - ADMISSION_TIME_ROUNDING_S>"
duration=30.00000001 stored_end=1789000000.0 end-start=30.0 refuse(duration>span+1us)=False
duration=30.0000009 stored_end=1789000030.000001 end-start=30.000000953674316 refuse(duration>span+1us)=False
duration=30.0000011 stored_end=1789000030.0000012 end-start=30.000001192092896 refuse(duration>span+1us)=False
duration=30.00001 stored_end=1789000030.00001 end-start=30.000010013580322 refuse(duration>span+1us)=False
capture_start shift=-2.384e-07 refuse=False
capture_start shift=+2.384e-07 refuse=False
capture_start shift=-1.000e-05 refuse=True
capture_start shift=+1.000e-05 refuse=False
capture_start shift=-1.000e-01 refuse=True
allowance/duration_ULP at 30 s = 281474976.710656
```
Second run (attempt endpoints fixed, which is the contract's "baseline longer than the attempt" case):
```
$ python3 -c "<start=1789000000.0; end=1789000030.0; span=end-start; refuse = dur > span + ADMISSION_TIME_ROUNDING_S>"
attempt span=30.0 duration=30.0000009 refuse=False
attempt span=30.0 duration=30.0000011 refuse=True
attempt span=30.0 duration=30.00001 refuse=True
```

**Probe 4 — exact allowance edge at the production policy, read from the first span-complete trace row.**
```
$ PYTHONDONTWRITEBYTECODE=1 python3 -c "<FakeClock harness; each probe sleeps 5.0 s and reports duration
4.0 - k*ulp(1789000000.0) with k from a per-reading schedule; policy=CooldownPolicy(); inspect r['_trace']>"
six readings each 2 ULP short (12 ULP = allowance): result=recovered; trace key=['_trace']; first span-complete row: waited=30.0 s, missing=12.000 ULP, coverage_complete=True
five readings 2 ULP short + sixth 3 ULP short (13 ULP, one over): result=cap_hit; trace key=['_trace']; first span-complete row: waited=30.0 s, missing=13.000 ULP, coverage_complete=False
six readings each 3 ULP short (18 ULP = 4.29 us): result=cap_hit; trace key=['_trace']; first span-complete row: waited=30.0 s, missing=18.000 ULP, coverage_complete=False
```
An earlier variant of this probe that placed the 3 ULP reading first reported 12 ULP missing at release; that
reading had rolled out of the window (its evidence end equalled the cutoff at 35 s) before the gate released,
which is the retention rule working, not a counter-example. It is superseded by the row-level read above.

**Probe 5 — retained-reading threshold for a 10 μs deficit.** From probe 1: 21 readings × 2 ULP = 1.0014e-5 s
≥ 1e-5 s, so 21 or more retained readings admit a 10 μs deficit; 20 readings (9.54 μs) refuse it.

**Not executed:** nothing in the packet's scope was left unrun. The canonical full test suite was not run
(outside the 12-minute budget and not requested).
