# ACCEPTANCE-25G83-01 R-ACC-1(b): desk replay

**Verdict: PASS under cold ruling 38/20 §3.1.** The v3 comparison is exact
for all 22 fitted captures. The two unresolved-anchor captures are unfitted,
so their v3 comparison is undefined. The v4 geometry has zero interior
misses across all 24 × 59 commanded pulses. The prior literal FAIL remains
in the historical seat report; this result applies the corrected criterion.

`replay.py` reads the two 2026-09-19 n1/n2 harvest archives under
`/Users/edr/night-archive/`. For each capture it reads GPU intervals from
`power_trace.csv`, actual commanded on/off epoch stamps from `events.jsonl`,
and recorded pulse reasons from `instrument_evidence.json`. It calls the
production `joulewise.powermetrics_fiducial._fit_pulse` interior check. An
artificially high baseline forces every pulse with an interior interval to
exit at the subsequent amplitude gate, so this geometry replay does not run
the unrelated model fit. The only result used is whether the production check
returns `no_plateau_interior_intervals`. The v3 test uses the observed on/off
stamps. The v4 counterfactual keeps each observed command-on phase and extends
its observed duration by 1.0 s, giving a 1.5 s interior with the unchanged
0.25 s inset. This is a frame geometry check, not a claim that the archived
v3 pulses carried v4 power.

Run from the repository root:

```sh
python3 -B docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/replay.py
```

This command requires the v4 detector constant `PULSE_DURATION_S == 2.0`.
The present replay worktree still has v3 (`1.0`), so its `results.json` was
regenerated with a process-local preview of the ruled v4 constant:

```sh
python3 -B -c 'import runpy, sys; from joulewise import powermetrics_fiducial as detector; detector.PULSE_DURATION_S = 2.0; sys.argv = ["replay.py"]; runpy.run_path("docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/replay.py", run_name="__main__")'
```

The preview changes only the pulse-duration constant in memory. The normal
command must be rerun at the v4 PR head before merge.

The script writes `results.json` with per-capture recorded, v3, and v4 miss
indices, fitted labels, source file hashes, fit counts, and capture reasons.
It exits 0 on PASS and 1 on FAIL.

| Capture | Fitted | Recorded misses | v3 replay | v4 replay |
|---|---|---:|---:|---:|
| n1-d01 | yes | — | — | — |
| n1-d02 | yes | 40, 54 | 40, 54 | — |
| n1-d03 | yes | — | — | — |
| n1-d04 | yes | 10 | 10 | — |
| n1-d05 | yes | — | — | — |
| n1-d06 | yes | 58 | 58 | — |
| n1-d07 | no | — | 13, 52¹ | — |
| n1-d08 | yes | 41 | 41 | — |
| n1-d09 | yes | 10, 34 | 10, 34 | — |
| n1-d10 | no | — | 24, 56¹ | — |
| n1-d11 | yes | 44 | 44 | — |
| n1-d12 | yes | — | — | — |
| n2-d01 | yes | — | — | — |
| n2-d02 | yes | 1, 6 | 1, 6 | — |
| n2-d03 | yes | — | — | — |
| n2-d04 | yes | 7, 26, 29 | 7, 26, 29 | — |
| n2-d05 | yes | — | — | — |
| n2-d06 | yes | 19 | 19 | — |
| n2-d07 | yes | — | — | — |
| n2-d08 | yes | 20, 55 | 20, 55 | — |
| n2-d09 | yes | — | — | — |
| n2-d10 | yes | 31, 34 | 31, 34 | — |
| n2-d11 | yes | — | — | — |
| n2-d12 | yes | — | — | — |

¹ `v3_comparison_undefined_unfitted`: these indices arise from the unanchored
native fallback timeline and are not comparisons to recorded fits. Their
`power_trace.csv` is the unanchored native fallback timeline (plateaus sit
≈0.40 s and ≈0.62 s before the commanded windows; frames overlap and gap by
up to 0.15 s), so no per-index v3 comparison exists for them; the v4
zero-miss result is time-base invariant and holds.

Indices are zero-based. Totals: 18 recorded misses; 18 v3 misses across the
22 fitted captures, all exact; four undefined v3 indices across two unfitted
captures; and zero v4 misses across all 24 captures.

**PASS criterion:** v3 miss indices equal the recorded indices for every
fitted capture (`clock_anchor_resolved: true`, 59 pulse rows); unfitted
captures contribute no v3 comparison. The v4 geometry must have zero misses
in all 1,416 pulses. **Observed: PASS (22/22 defined v3 comparisons exact;
0/1,416 v4 misses).** The jittered r6 resampling under `jitter_r6/` is
diagnostic only and changes no rule or count.
