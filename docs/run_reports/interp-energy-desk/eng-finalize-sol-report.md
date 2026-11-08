Committed locally on `perf/2026-11-08-eng-finalize`:

- `64302a0c0` — equality and corruption/interruption tests.
- `1a12789bb` — streaming hashes, bounded 1/2/4/8 workers, and per-invocation reuse.

Changed the night/harvest paths, added the hashing helper and benchmark, updated three test files, and wrote two reports. Working tree is clean; nothing pushed.

Synthetic 256 MiB benchmark: **0.599 → 0.057 seconds** for three inventories, with exact manifest equality. Focused hashing/harvest/courier checks passed **13/39/19 tests**; compile and diff checks passed. Three native process-group failures reproduced on unchanged `origin/main` and need outside-sandbox verification.

The [handoff report](/Users/edr/code/CapstoneProject/jw-wt/sol-eng-finalize/docs/perf/2026-11-08-eng-finalize.md) contains test commands, timings, limitations, and the exact MBP gap benchmark command. Production push latency and worker selection remain unmeasured; cache reuse intentionally ends with the invocation.