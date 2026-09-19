# QPE-01: the first quiet-predicate evidence night

This pilot measures how much consecutive idle energy observations vary on the
current Mac. It collects evidence for a future CPU activity limit; it does not
choose or activate a limit. All results are **PROVISIONAL**. Stage B and a
separate cold-gate ruling remain necessary before activation.

The frozen registration is `pilot_protocol_v1.json`, under cold gate 10 Q1/Q2
(2026-09-19), adjudication 10a. Its exact SHA-256 fingerprint is a key in
`night_gate.RULED_REGISTRATIONS`. That table can change only by cold-gate ruling.
The registration also names the fingerprint of the tracked evidence chain
source. The gate measures that source at the plan's measurement commit and
compares it to the literal in the pinned wrapper. An advisory sidecar cannot
substitute for the measured source.

The plan uses v2 `DIAGNOSTIC_NO_PACK` admission and a 9000-second window. After
GO, the chain settles for 600 seconds, then schedules 12 consecutive 600-second
envelopes. Each analysis interval is the interior 480 seconds, starting 60
seconds into its envelope. There is no load generator. Absolute start times
prevent cumulative schedule drift; collection ends at each scheduled envelope
boundary. Late starts remain visible, and starts more than five seconds late
are excluded. Nothing is compressed, retried or topped up.

The chain runs `quiet_admission.sample_interval` every 30 seconds as a recorder.
It writes `evidence_busy_cores.jsonl`, never `quiet_samples.jsonl`. Its busy-core
numbers are covariates: they describe the machine and are **never an exclusion
or admission input**. Observer CPU cost includes the whole observer and its
reaped children, including the recorder and census, and is never subtracted.

Envelopes are excluded only by frozen, named mechanisms: the census is not
clean or is unknown; the AC probe does not report “AC Power” or errors; a
`CPU_Speed_Limit` is below 100 or the thermal probe errors; the clock anchor is
unresolved; or native sample support does not cover the complete interior.
The frozen schedule also excludes start drift above five seconds. Partial
rows, original power files and exclusion reasons remain in the evidence.
Energy is integrated over native support, not inferred by multiplying a
whole-envelope mean by 480 seconds. CPU+GPU+ANE joules are the main quantity;
combined power is a cross-check. OS build, boot identity, tool identity,
per-round AC/thermal results, cadence and observer cost accompany the numbers.

At least eight retained envelopes and six original adjacent pairs are needed;
otherwise the pilot is INCONCLUSIVE. Exclusion does not make formerly separated
envelopes adjacent. There is no top-up. The next plan can be authored only after
the pilot's spread is measured. Its target is δ = 1 J and its sample size is
`n = max(3, ceil(8 * s_upper² / δ²))` pairs, where `s_upper` is the upper 90%
confidence bound on the adjacent-pair standard deviation, not the point SD.
The confidence construction for overlapping adjacent differences is still a
lead-ruling dependency: this implementation records the SD and leaves
`s_upper` and the next sample size unset rather than silently choosing a model.

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
terminated under bounded cleanup budgets. The driver checks that cleanup
before launching a courier. The courier may describe completed envelopes,
exclusions and uncertainty; it cannot make a scientific decision.
