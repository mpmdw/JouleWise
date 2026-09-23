# Delta lens (execution + contract) — REPLAY-FEEDER-FIRST-FRAME-CAUSALITY-01 @ 6acad9e8

Worktree `/Users/edr/code/JouleWise-wt-a267-review3`, detached at 6acad9e8, tree clean at exit.
Verdict: **no BLOCKER.** The cure is correct, the kill is real, the `auto` deviation is sound and
load-bearing — but it is **untested**.

## Kill ledger (all executed, all restored with `git checkout -- .`)

| # | Mutation | Result |
|---|---|---|
| A | `scripts/replay_powermetrics_frames.py:262` frame-1 `due = time.monotonic()` (pre-fix pacing) | R7 arrival test RED (`0.0814` vs required `0.2374`); R7 deriver test RED (violation **-0.1817 s**); other 8 seam tests green — no over-kill |
| B | same line, re-seat removed (`first_due = due`, base stays `spawn` = the literal dictate) | `auto` cadence collapses: frames 2,3 arrive **0.0001–0.0002 s** apart vs archived 0.260/0.259 — **and the full module stays 78/78 OK** |
| C | frames 2..n at fixed 15 ms spacing | R7 arrival test RED; **pre-existing R3 cadence test GREEN** |

Command for all: `env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_sample_quiet_predicate_evidence[.BenchReplayRecorderSeamTests]`.
Final state: `tests.test_sample_quiet_predicate_evidence tests.test_quiet_predicate_campaign` → **206 OK**.

## (2) Deriver inequality, executed myself — 5 live `ReplayRecorder`+`Clock` runs on the fixture

margin = `first_parse.monotonic_after − (pre_spawn.monotonic_before + elapsed[0])`, elapsed[0] = 0.257382541 s:
`0.0898, 0.1186, 0.1283, 0.0731, 0.1526` → **min 0.0731 s, median 0.1186 s**.
The margin cannot go negative by construction: the feeder's `spawn` (`:325`) is taken after `Popen`,
which is after `pre_spawn` (`sample_quiet_predicate_evidence.py:740`), and the collector adds its
20 ms poll quantum (`:770`). Production is *looser* still — `uncertainty_evidence.py:1193-1200`
allows `pre_resolution + first_parse_resolution` (~2 µs) of slack that the test does not, so the
test is strictly stricter than the gate it guards. Correct direction.

## (3) `auto` probe — 10 launch phases across the whole K-rounding range

Real feeder, `--label-shift auto`, arrivals timed on NUL as R7 does. `first_write_delay_s` spanned
**0.2702 → 1.0070 s** (both branches governed: causality floor at phases 0.8–0.9, the wall target
elsewhere, including K rounding up by ~0.99 s). In every phase the inter-frame arrival deltas were
**0.2369–0.2791 s** against archived 0.2601/0.2590 — the archived cadence is kept, not fired back to
back. Causality (`arrival_i ≥ Σ_{j≤i} elapsed_j − 0.02`) held for **every frame in every phase**.
Seat Deviation 1 is therefore **correct and necessary**: `pacing_base = due − elapsed[0] ≥ spawn`
(since `due ≥ spawn + elapsed[0]`), so frame *i* is due no earlier than `spawn + Σelapsed`, and kill
B shows that without it the cadence is destroyed.

## (4) Production identity — confirmed
`git diff --stat 4dea946b..6acad9e8 -- joulewise scripts/sample_quiet_predicate_evidence.py` is
**empty**; only the feeder and the test file moved. No live doc enumerates the sidecar schema (only
process traces do) and the four new keys are additive.

## (5) Tests that pass for the wrong reason
- **`tests/…:1734` (pre-existing R3)**: `assertAlmostEqual(delta, elapsed_ns/1e9, delta=0.25)` on a
  0.2601 s signal passes for any observed delta in **[0.0101, 0.5101]** — 10 ms of discrimination.
  Kill C proves it vacuous. The delta's own R7 frame-2 lower bound is what catches it now, so this
  delta *improves* coverage; the tolerance itself stays a latent hazard.
- **Not a defect, worth recording**: an end-to-end "deriver no longer says `clock_stamp_invalid`"
  assertion would be *vacuous on this fixture* — I ran the production deriver through
  `ReplayRecorder.finish()` under both modes, fixed and killed, and it returns
  `native_rollover_anomalous` (`uncertainty_evidence.py:1047`, reached before the k-comparison at
  `:1193`) either way: 3 frames / 0.78 s yield one native rollover. The seat's stamp-level
  assertion is the only non-vacuous form available; the end-to-end payoff stays bench evidence.

## Findings
- **SHOULD-FIX** — `scripts/replay_powermetrics_frames.py:262`, the `auto` cadence re-seat.
  Scenario: any future edit taking the code back to the literal dictate silently returns every
  `auto` slot to a back-to-back burst (kill B: 0.0002 s deltas) while all 78 tests stay green; the
  bench then measures a stream no recorder could produce. Fix: one assertion — run
  `feed_watching_arrivals(tmp, "auto", 3)` and assert deltas ≈ `elapsed[i]` **and**
  `arrival_i ≥ Σ elapsed`. Do not copy R3's 0.25 tolerance; ±0.08 s is ample (measured spread
  0.237–0.279).
- **NIT** — `scripts/bench_replay_start_drift.py:283`. The defect was visible only on a real bench
  run; the sidecar now carries `first_write_delay_s`/`first_write_late_s`, but the per-slot table
  does not quote them. Adding both columns makes a recurrence self-evident in the artifact.
- **NIT** — R3's 0.25 s cadence tolerance (above), whenever that test is next touched.
