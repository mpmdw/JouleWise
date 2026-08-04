# TEST-SPEED-01 design — from measured per-module timing (2026-08-03, quiet bench)

Data: 93 test modules, 0 failures, 695.0s serial (per-module,
one-module-per-process; the in-process `discover` suite is ~570-580s
because of shared setup). Raw: timings-20260803.jsonl + summary-*.json
(this dir). Bench was idle (both claim streams parked; no Sol running).

## The one finding that drives everything: the suite is a two-module problem

| module | seconds | tests | s/test |
|---|---|---|---|
| test_run_campaign            | 181.8 | 203 | 0.90 |
| test_p2038_production_path   | 133.4 |   7 | 19.1 |  <- extreme per-test cost
| test_reduce                  |  48.4 | 122 | |
| test_bridge                  |  47.1 |  62 | |
| test_powermetrics_fiducial   |  29.6 |  37 | |
| test_controller              |  27.1 |  70 | |
| test_analysis_integration    |  25.3 |  92 | |
| test_cli_run                 |  23.7 |  95 | |
| test_determinism_gate        |  18.5 |  40 | |

- Top 2 modules = 315s = **45%** of total. Top 15 = 583s = **84%**.
- 53 of 93 modules run in **<1s** each (~20s combined). The long tail is thin.

## Lever 1 — shard-runner (LPT bin-packing), and why it ALONE caps at 182s

Greedy longest-processing-time assignment of whole modules to N workers:

| workers | wall | ideal (total/N) |
|---|---|---|
| 2 | 347.5s | 347s |
| 3 | 231.7s | 232s |
| 4 | **181.8s** | 174s |
| 6 | 181.8s | 116s |
| 8 | 181.8s | 181.8s floor |

**Module-atomic sharding is capped at 181.8s by test_run_campaign** — past
4 workers, more parallelism buys nothing. This is THE structural fact: a
shard-runner is necessary but not sufficient.

## Lever 1b — split the two wall modules (required to beat 182s)

Split test_run_campaign (203 tests) into 4 shards by TestCase class and
test_p2038_production_path (7 tests) into 4, then LPT:

| workers | wall |
|---|---|
| 4 | 173.8s |
| 6 | 115.9s |
| 8 | **86.9s** (new floor 48s = test_reduce) |

**~570s → ~87s wall (8 workers) is a 6.5x speedup**, and the new floor
(test_reduce, 48s) is the next split target if more is wanted. RECOMMEND:
shard-runner + split run_campaign/p2038 by TestCase class; 8 workers on
the M3 Max (min(16, cores-2) headroom exists).

## Lever 2 — PR-fast / full tier split (Ed-ratified in principle)

Fast tier = drop the 11 heaviest integration modules (run_campaign,
p2038, reduce, bridge, powermetrics_fiducial, controller, cli_run,
determinism_gate, nvidia_node_integration, claude_bridge_mcp,
node_client). Remainder = 82 modules, 161.9s serial → sharded:

| workers | fast-tier wall |
|---|---|
| 4 | 40.6s |
| 8 | 25.3s (floor = test_analysis_integration) |

So a PR gets **~25-40s** of fast unit feedback. FENCE (doctrine, D-061 +
the full-suite-as-gate rule): the fast tier NEVER substitutes for a
required gate — merges, whole-window verdicts, and audited heads keep the
FULL suite. Fast tier is advisory-fast feedback on PR pushes only; full
suite remains the blocking `test` job and the merge gate. Tag mechanism:
mark the 11 heavy modules (or, finer, the slow classes) with a
`@integration`/env-guard so the fast job selects the complement, mirroring
the D-101 site-lane `JOULEWISE_SITE_CONTENT_TESTS` pattern already in the
repo.

## Lever 3 — Blacksmith runners — NEEDS ED (account/cost)
Blacksmith gives faster hosted runners + better caching than
GitHub-hosted. Evaluation needs Ed's call on account/billing and whether
CI spend is a constraint. Data point for the decision: the GitHub-hosted
`test (3.11)`/`(3.14)` jobs ran 15-17 min each on recent PRs; the bulk is
the serial suite, which levers 1-2 cut to ~1.5 min sharded BEFORE any
runner change — so the shard-runner likely dominates Blacksmith for
wall-clock, and Blacksmith's value is mostly cache/queue latency. RECOMMEND
implementing levers 1-2 first, then measuring whether Blacksmith is still
worth it (likely marginal once sharded). Deferred to Ed.

## Recommended implementation order (all mechanical, delegatable to Sol)
1. `scripts/shard_tests.py` — enumerate modules, read a checked-in
   timing map (timings-20260803.jsonl as the seed), LPT-assign to
   `--workers N`/`--shard-index`, run each shard's modules, aggregate.
   Deterministic, no test deletions (D-061). Self-testable.
2. Split test_run_campaign + test_p2038_production_path by TestCase class
   into sibling files (NEW files, zero deletions) OR support intra-file
   class-level sharding in the runner (preferred — no file churn on the
   most-reviewed test file).
3. CI: add a sharded matrix `test` job (the blocking gate, full suite,
   N shards) + a `test-fast` advisory job (fast tier, complement of the
   integration tag) on PR pushes. Full suite stays the merge gate.
4. Blacksmith: measure post-sharding, Ed decides.

## Status
Data collected + design done (levers 1-2 fully specified from measurement;
lever 3 needs Ed). Implementation queued as the concrete next step —
mechanical, no claim surface, delegatable in one Sol round + CI wiring.
Not run tonight (both claim streams parked for Ed; CI-workflow changes
benefit from Ed seeing this design + the Blacksmith call first).
