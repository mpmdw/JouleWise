# r6 jitter resampling diagnostic

**Headline: pending raw r6 source access.** The archived 25G83 duration
templates and the r6 registry are available, but the 17 raw r6 bundles appear
only under `/Users/edr/code/JouleWise`, which this implementation seat is
explicitly forbidden to touch. No new jitter result is claimed. An allowed
copy of the registry's `runs_window_a_*` source directories is needed to run
`decim.py` and produce `results.json`.

This is the diagnostic trace called for by ex-26 D1 and cold ruling 38/20
§3.3. It is **diagnostic only**: its output changes no rule, gate, or count,
and is not a merge precondition.

The script reads the 17 members pinned in
`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`. As in
ex-26's original `decim.py`, it merges adjacent r6 frames in both pairwise
phases with an energy-weighted mean and calls production `detect_pulses`.
For the added jitter replay it integrates each r6 interval-average power
trace onto each of the 24 archived 25G83 frame-duration sequences, tiling
those durations from the r6 trace start. It then calls production
`_fit_pulse` for the v3 interior test. The high baseline exits at amplitude
after the interior test so projection cannot affect the geometry result.
The output records source hashes, each miss list, pairwise detection counts,
and the aggregate fraction of 17 × 24 synthetic captures with zero misses.
The 25G83 durations include both fallback captures as duration templates;
their unanchored absolute times are not used.

From the repository root, after obtaining an allowed local copy:

```sh
python3 -B docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/jitter_r6/decim.py --r6-root /path/to/allowed/r6-copy
```

ex-26 reported 34/34 detected after pairwise decimation alone. That is a
historical result, not a result of this pending jitter execution. The new
jitter headline will be the script's `zero_miss_trials` of `jitter_trials`
and `missed_pulses` in `results.json`.
