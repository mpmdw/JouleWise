# Harness bench verification — `scripts/sample_quiet_predicate_evidence.py` live `collect` (magistrate, 2026-09-18 18:59–19:00 PDT)

Branch `feat/2026-09-18-quiet-predicate-evidence-harness` at `98336969` (seat 13's two files, committed by the lead by pathspec; 31 offline tests `OK` under `unittest`; the brief's `pytest` commands were the magistrate's error — the canonical interpreter has no pytest and the repo suite is unittest).

Command (worktree `JouleWise-wt-harness-232`):

```
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/sample_quiet_predicate_evidence.py collect --state contaminated-2seats-2claude --repeat 1 --duration-s 95 --sample-interval-s 30 --out /Users/edr/night-archive/qpe-232/contaminated-2seats-20260918T185907 --power
```

rc 0. State: two Astra seats running (arm-scripts seat 17, root-cause seat 19), Ed's interactive `claude` pid 1505 idle, this activation. Output: `rounds.jsonl` (3 rows; copied here), `session.json`, `raw/` (powermetrics plist at 100 ms + processes text, 27 MB, kept under `~/night-archive/qpe-232/`, sums in `raw-SHA256SUMS.txt`).

| round | status | busy_cores | observer_cpu_s | cpu_w | rail_sum_w | coverage_s | error_bound_j |
|---|---|---|---|---|---|---|---|
| 1 | complete | (see row) | 1.685 | 6.071 | 6.071 | 31.73 | null (anchor needs ≥ 60 s native support) |
| 2 | complete | 1.286 | 1.680 | 5.637 | 5.641 | 31.76 | 3.17 |
| 3 | partial (collection deadline) | — | 1.039 | 8.853 | 8.853 | 30.51 | 4.75 |

What the magistrate checked by reading the rows: the observation is the production smoke round's full JSON (`metrics.busy_cores`, `census`, `boot_identity`, `load_avg_diagnostic`, `raw_sha256`); clusters carry `active_ratio` and `freq_hz` (E 1.48 GHz active 1.0; P0 2.99 GHz active 1.0; P1 1.34 GHz active 0.287 in round 2); alignment uses the production rate-aware anchor (`powermetrics_native_second_rate_aware_set_membership_v1`), reports `anchor_status`, per-rail bounds, `ps_top_span_mismatch` and `round_ps_span_mismatch` flags and the wall/monotonic stamps; missing values carry reasons (`dram_w_reason`). The first-round null bound is the documented behaviour, so a state collection must run ≥ 90 s before its first bounded row and the memo must quote only bounded rows.

Two things for the campaign protocol: (1) the alignment bound of ≈ 3–5 J per 30 s round is of the same order as the ≈ 5 J bar per 480 s slot; over a slot it will scale with the number of frames, so ΔJ per slot comparisons must be made on state means over many rounds, with the bound reported beside them, not per round; (2) raw at 100 ms is ≈ 27 MB per 95 s (≈ 140 MB per 480 s state repeat); storage under `~/night-archive/qpe-232/`, digests in the record, never the raw in the repo.

Not verified here: `load` (the synthetic generator) live, and `summarize` on a multi-state directory. Both follow when the campaign runs; the arm takes precedence tonight.
