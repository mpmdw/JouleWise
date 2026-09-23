# Exhibit G — observer accounting, verified at the bench (magistrate, 2026-09-23 00:30 PDT; read-only archives; code at main 69315e79)

## G1 — the two observer accountings in `scripts/sample_quiet_predicate_evidence.py` (verbatim)
```
712:     return {"status": status, "error": error, "observation": observation,
713:             "observer_cpu_s": cost if not residue else None,
714:             "observer_cpu_s_reason": "worker cleanup incomplete" if residue else "SELF + reaped CHILDREN; no subtraction",
715:             "end_stamp": asdict(support_end), "workers": jobs, "argv": argv_records,
716:             "censuses": censuses, "census_errors": census_errors,
...
1164:         session["whole_envelope_observer_cpu_s"] = cpu_total() - envelope_cpu_start
1165:         session["whole_envelope_observer_definition"] = "SELF + all reaped CHILDREN, including power recorder; never subtracted"
1166:     session["error_rounds"] = sum(row["status"] == "error" for row in rows)
```
The per-round figure (`observer_cpu_s`) is the worker/census block's own CPU; the whole-envelope figure additionally reaps the power recorder. `pilot_summary` (campaign 1067–1072) sums the per-round figure only.

## G2 — both nights, per envelope: observer_cpu_s (round), recorder_observer_cpu_s, whole_envelope_observer_cpu_s (summary.json envelopes[])
```
PRIOR 20260922-0217 sha256 9121f080c97e4b2f8f01261d0a2f9f407840dea9a6c8ca4468406617403d6f04
  env 01  round 31.401  recorder 4.426  whole 104.381
  env 02  round 31.408  recorder 4.421  whole 106.761
  env 03  round 31.388  recorder 4.394  whole 104.029
  env 04  round 31.557  recorder 4.169  whole 103.363
  env 05  round 31.312  recorder 4.404  whole 106.207
  env 06  round 31.302  recorder 4.463  whole 104.772
  env 07  round 31.261  recorder 4.372  whole 103.130
  env 08  round 31.265  recorder 4.154  whole 107.039
  env 09  round 31.411  recorder 4.390  whole 105.477
  env 10  round 31.308  recorder 4.376  whole 103.566
  env 11  round 31.541  recorder 4.345  whole 106.032
  env 12  round 31.212  recorder 4.144  whole 106.113
  reported observer_floor_cores 0.05310 (= 376.4 s / 7088.1 s)
  whole-envelope floor over the same support 0.17789 cores; over 12x600 s 0.17512 cores
  per-envelope whole-envelope share: mean 0.17512  sd 0.00229  min 0.17188  max 0.17840 cores
  excess of the whole-envelope floor over smallest_holdable_share 0.05: 0.12789 cores; x 0.3194 W x 480 s = 19.61 J; x 1.0349 W x 480 s = 63.53 J
  stop causes: ['observer_floor_above_smallest_holdable_share']
TONIGHT 20260922-2100 sha256 84bfcafb84cb08ddb6b4c1e2fe707ac2b74a1e5b055ecba204a3740c58fe2bc2
  env 01  round 31.928  recorder 4.517  whole 101.051
  env 02  round 31.311  recorder 4.425  whole 94.422
  env 03  round 31.613  recorder 4.436  whole 95.174
  env 04  round 31.659  recorder 4.158  whole 97.041
  env 05  round 31.547  recorder 4.349  whole 96.073
  env 06  round 31.634  recorder 4.213  whole 96.626
  env 07  round 31.649  recorder 4.355  whole 96.095
  env 08  round 31.551  recorder 4.361  whole 97.286
  env 09  round 31.635  recorder 4.217  whole 97.157
  env 10  round 31.618  recorder 4.422  whole 96.616
  env 11  round 31.597  recorder 4.193  whole 95.240
  env 12  round 31.610  recorder 4.426  whole 95.976
  reported observer_floor_cores 0.05282 (= 379.4 s / 7181.6 s)
  whole-envelope floor over the same support 0.16135 cores; over 12x600 s 0.16094 cores
  per-envelope whole-envelope share: mean 0.16094  sd 0.00277  min 0.15737  max 0.16842 cores
  excess of the whole-envelope floor over smallest_holdable_share 0.05: 0.11135 cores; x 0.3194 W x 480 s = 17.07 J; x 1.0349 W x 480 s = 55.31 J
  stop causes: ['sized_pairs_above_24', 'observer_floor_above_smallest_holdable_share']
```

## G3 — what the registration and its authority say the floor is
```
registration v2 block_two = {"authored_after_pilot": true, "contrast": "idle-load-idle bracket", "levels": [0, 0.05], "one_profile": true, "one_qos": true, "smallest_holdable_share": 0.05, "upper_bound": "one-sided 95% paired-contrast upper bound"}
registration v2 stop_branches = {"block_two_upper_bound_above_1_J": "no cutoff qualifies", "observer_floor_above_smallest_holdable_share": "no cutoff qualifies", "sized_pairs_above_24": "no cutoff qualifies"}
registration v2 summary[5] = "whole-round observer cpu-s, self plus reaped children including recorder; never subtracted"
summary.json observer_definition = "SELF + reaped CHILDREN, including collector, recorder, sampler and census; never subtracted"
10a line 9 (extract): stop branch pre-registered: if the sized `n` exceeds 24 pairs, or the observer floor's own busy cores exceed the smallest holdable share, or block two's upper bound at that share exceeds 1 J → "no cutoff qualifies", deliverable = the upper bound and the clean-machine busy-core distribution. Exclusions decided by NAMED mechanisms
occurrences of 'holdable' in 10a: 1 ; in 46b: 0
```
