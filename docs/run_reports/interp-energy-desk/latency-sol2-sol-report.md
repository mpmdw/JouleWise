Committed locally as `b98d0ee1b` on `perf/2026-11-08-latency-audit-sol2`. Working tree clean; no push.

Files:

- [Inventory and ranked fixes](docs/perf/LATENCY-AUDIT-sol2.md)
- [Timing evidence ledger](docs/perf/latency-audit-sol2-evidence.json)
- [Handoff report](docs/run_reports/2026-11-07-latency-audit-sol2.md)

Top opportunities: move desks off the measurement Mac and split BYTES test work. CI projections fall from 152 to about 56 minutes; this is **estimated**, not demonstrated. R1’s 15.61-hour figure is a planning bound.

Verification: `python3.13 -B -m unittest tests.test_shard_split.ConservativeUnknownWeightTests` — **3 passed**. Arithmetic, links, table structure, protected-path checks and staged whitespace checks passed.

Actual R1, BYTES stage-1 and offload timings remain unknown. No sealed data, network, measurement or full suite was used. Next step: lead reviews fixes F1/F2 and commissions final-head timing.