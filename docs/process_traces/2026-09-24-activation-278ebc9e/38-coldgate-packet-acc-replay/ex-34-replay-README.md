# ACCEPTANCE-25G83-01 R-ACC-1(b): desk replay

**Verdict: FAIL. Stop and return to the council.** The exact v3 comparison
passes for 22 captures and fails for two. The v4 geometry has zero interior
misses across all 24 × 59 commanded pulses. The ruling requires both conditions;
it does not exempt captures whose clock anchor prevented the production detector
from recording pulse fits.

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

The script writes `results.json` with per-capture recorded, v3, and v4 miss
indices, source file hashes, fit counts, and capture reasons. It exits 0 on
PASS and 1 on FAIL.

| Capture | Recorded misses | v3 replay | v4 replay |
|---|---:|---:|---:|
| n1-d01 | — | — | — |
| n1-d02 | 40, 54 | 40, 54 | — |
| n1-d03 | — | — | — |
| n1-d04 | 10 | 10 | — |
| n1-d05 | — | — | — |
| n1-d06 | 58 | 58 | — |
| n1-d07 | — | **13, 52** | — |
| n1-d08 | 41 | 41 | — |
| n1-d09 | 10, 34 | 10, 34 | — |
| n1-d10 | — | **24, 56** | — |
| n1-d11 | 44 | 44 | — |
| n1-d12 | — | — | — |
| n2-d01 | — | — | — |
| n2-d02 | 1, 6 | 1, 6 | — |
| n2-d03 | — | — | — |
| n2-d04 | 7, 26, 29 | 7, 26, 29 | — |
| n2-d05 | — | — | — |
| n2-d06 | 19 | 19 | — |
| n2-d07 | — | — | — |
| n2-d08 | 20, 55 | 20, 55 | — |
| n2-d09 | — | — | — |
| n2-d10 | 31, 34 | 31, 34 | — |
| n2-d11 | — | — | — |
| n2-d12 | — | — | — |

Indices are zero-based. Totals: 18 recorded misses, 22 v3 geometric misses,
and zero v4 misses. Both discrepant captures have zero recorded fits and
`clock_anchor_unresolved` in their evidence. The production detector bypassed
all fitting after that anchor failure, so their empty recorded miss lists do
not establish that their pulses had usable interiors. Their archived frames
still show four empty interiors at the actual command times.

**PASS criterion:** v3 miss indices equal recorded indices in every one of
the 24 captures, with no additional misses; v4 has no misses in 1,416 pulses.
**Observed: FAIL (22/24 exact v3, 0/1,416 v4 misses).** The ruling says to
stop on deterministic failure. The jittered r6 resampling diagnostic was
therefore not run. The council must rule whether the v3 comparison excludes
the two anchor-bypassed captures or keeps the literal 24-capture criterion;
this implementation does not choose an exception.
