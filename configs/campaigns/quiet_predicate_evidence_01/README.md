# QPE-01: the first quiet-predicate evidence night

This pilot measures how much consecutive idle energy observations vary on the
current Mac. It collects evidence for a future CPU activity limit; it does not
choose or activate a limit. All results are **PROVISIONAL**. Stage B and a
separate cold-gate ruling remain necessary before activation.

The frozen registration is `pilot_protocol_v3.json`, SHA-256
`9491bc370b515c7d56d21f87e0c6721be8cb2b6501b430b9dce75a93f59a6f0a`. It keeps
every value of v1 (cold gate 10 Q1/Q2 of 2026-09-19, adjudication 10a and
sizing ruling 46b) and v2 (the A269 gate of 2026-09-22), and adds the rules of
cold gate QPE01-DAEMON-CONTAMINATION-01 of 2026-09-23: ruling 10 (the
non-observer process rule below) and ruling 31's reporting limbs as
adjudicated by synthesis 35 (the corrected observer floor below). Its exact
SHA-256 fingerprint is a key in `night_gate.RULED_REGISTRATIONS`. That table
can change only by cold-gate ruling. v1 and v2 stay in the table as
superseded history; no night can be armed against them again.
The registration also names the fingerprint of the tracked evidence chain
source. The gate measures that source at the plan's measurement commit and
compares it to the literal in the pinned wrapper. An advisory sidecar cannot
substitute for the measured source.

The plan uses v2 `DIAGNOSTIC_NO_PACK` admission and a 9000-second window. After
GO, the chain settles for 600 seconds, then schedules 12 consecutive 600-second
envelopes. Each analysis interval is the interior 480 seconds, starting 60
seconds into its envelope. There is no load generator. Absolute start times
prevent cumulative schedule drift; collection ends at each scheduled envelope
boundary. Late starts remain visible, and starts more than ten seconds from schedule
are excluded. Nothing is compressed, retried or topped up.

The chain runs `quiet_admission.sample_interval` every 30 seconds as a recorder.
It writes `evidence_busy_cores.jsonl`, never `quiet_samples.jsonl`. Its busy-core
intervals are joined to scheduled envelopes by monotonic support; the summary
reports each envelope's median/max and the distribution for envelopes passing
census, AC and thermal probes. These numbers are covariates: they describe the machine and are **never an exclusion
or admission input**. Observer CPU cost is never subtracted from energy. The
observer floor is the collector's whole-envelope CPU -- its own CPU plus the
CPU of every child it reaped (the power recorder, the round's sampler and the
census) -- divided by the collector's own span, summed over envelopes. The
30-second recorder is started by the executor, beside the collector rather
than under it, so its CPU is not in that figure; the summary reports it as a
separate component and adds it back in a reported-only companion,
`observer_floor_including_load_recorder_cores`.

**Processes that are not the measurement (registration v3).** An *observer*
process is one the measurement started: the executor, which is the root of
the night's process tree, and everything descended from it (collector,
`sudo`, `powermetrics`, `top`, the census and the 30-second recorder). The
recorder is handed the executor's process id and marks each busy process it
sees `observer: true` or `false` by that ancestry; every other process is a
*non-observer*. Three rules read that mark. First, per envelope: for each
non-observer process (identified by pid and start time) the summary adds up
busy cores times interval seconds over the recorder rows that lie wholly
inside the envelope, and if one process reaches 30 core-seconds -- the
smallest block-two level, 0.05 core, held for the whole 600 s -- the
envelope is excluded as `non_observer_process_busy`, with the process's name,
pid and core-seconds written on the envelope's row. On the 2026-09-22 21:00
night `fseventsd` held about one full core, roughly 600 core-seconds per
envelope, and would have excluded all twelve. Second, before the night: the
pre-arm check and the t0 gate each take one 30-second observation and refuse
if any non-observer process is using 0.5 busy cores or more (`armable: false`
at the arm check, `night_refused_not_quiet` at t0), naming the process and
keeping the observation in `top_consumers_at_decision`. Third, during the
night: two envelopes in a row excluded this way end the chain with a typed
refusal whose reason is `non_observer_process_busy`, about 31 minutes after
t0 instead of three hours later; one such envelope followed by a clean one
does not end it.

Envelopes are excluded only by frozen, named mechanisms: the census is not
clean or is unknown; the AC probe does not report “AC Power” or errors; a
`CPU_Speed_Limit` is below 100 or the thermal probe errors; the clock anchor is
unresolved; or native sample support does not cover the complete interior.
A collector failure is `collect_error`; unproven per-envelope cleanup is
`cleanup_unproven`. Both exclude that envelope and continue on the frozen
cadence. Two consecutive cleanup failures or a chain refusal/crash (including
a dead recorder) abort with a typed refusal document.
The frozen schedule also excludes `start_drift` above ten seconds. Partial
rows, original power files and exclusion reasons remain in the evidence.
Energy is integrated over native support, not inferred by multiplying a
whole-envelope mean by 480 seconds. CPU+GPU+ANE joules are the main quantity;
combined power is a cross-check. OS build, boot identity, tool identity,
per-round AC/thermal results, cadence and observer cost accompany the numbers.

Sizing uses the six fixed, disjoint pairs `(e1,e2), (e3,e4), …, (e11,e12)`.
Each difference is the second envelope's interior joules minus the first's.
A pair survives only when both envelopes are retained and share boot and OS
identity. Excluding one envelope drops exactly its original pair; pairs are
never re-formed across a gap. At least eight retained envelopes and four
retained disjoint pairs are required (`minimum_adjacent_pairs` counts these
disjoint pairs). Otherwise the pilot is INCONCLUSIVE and leaves the upper
bound and sizing unset. There is no top-up.

For `n` retained pairs, `s_pair` is the sample standard deviation of their
differences, with `n − 1` degrees of freedom. The one-sided upper 90% confidence
bound is `s_upper = s_pair * sqrt((n − 1) / χ²(0.10, n − 1))`, using the
chi-square lower-tail 10th percentile. The factors are approximately 1.762
for six pairs and 2.266 for four pairs. The implementation numerically inverts
the regularized gamma function using the Python standard library, without
rounding these factors for sizing. **Independence and normality of the pair
differences are assumptions of this construction**, not pilot findings.

The next plan can be authored only after the pilot's spread is measured.
The source for all five sizing constants is the frozen registration (values unchanged since `pilot_protocol_v1.json`): δ = 1 J,
multiplier 8, minimum 3 pairs, stop above 24 pairs, and smallest holdable
block-two share 0.05 core. Code reads these registered values. Its sample size is
`n_pairs = max(3, ceil(8 * s_upper² / δ²))`. The eleven overlapping adjacent
differences and twelve single-envelope values remain diagnostics only; neither
sizes block two. The report includes their spreads, first-to-last retained
energy drift, and names every overlapping original adjacent pair with `|Δ| > 3 * s_pair`.
Excluded observations remain visible in those diagnostics; magnitude is never
an exclusion rule. Missing observations remain explicit and cannot bridge a gap.

The pre-registered negative result is **“no cutoff qualifies”** if the sized
sample exceeds 24 pairs, the observer's own busy-core floor exceeds the smallest
holdable share, or block two's upper bound at that share exceeds 1 J. The
result is then the upper bound and the clean-machine busy-core distribution.
Block two would test idle against the smallest holdable share (0.05 core), one
profile and one QoS, with idle–load–idle bracketing; it is not authored here.

For an already authored v2 plan, render its wrapper, sealed manifest and
sidecars with `python3 -B scripts/gen_evidence_night.py --plan /absolute/plan.json
--render-only` (one command). The generator accepts no count, timing, cadence
or protocol overrides and refuses calibration/derivation chains. Every pinned
file must match the measurement commit. The separate evidence verify-only
probe reads files and checks imports, emits exactly one matching manifest
line, and never starts collection, synthetic load or power sampling. It is not
permission to arm. Follow NIGHT_HANDBACK for lead-owned review and arming.

At runtime, collector, recorder, power and sampler groups are journaled and
terminated under bounded cleanup budgets. Only a process-absence census
proves cleanup; a denied group signal is logged, and the power recorder keeps
its supervised stop path. The executor or driver writes one cleanup record;
the courier reads it and reports even pre-execute refusals and unproven cleanup.
A missing process journal means nothing was launched and nothing needs cleaning. The courier may describe completed envelopes,
exclusions and uncertainty; it cannot make a scientific decision.
