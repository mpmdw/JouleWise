"""Pipeline wall-time ledger, bottleneck watcher and weekly report (RL-127 terms 6-9).

Operations tooling only. Nothing here reads a measurement, custody, archive or
result file, and nothing here runs inside a measured window. The watcher reads
RUN_STATE headings and pointer blocks, issue titles, CI run metadata, ref names
and the local process table. It signals no process and never opens SSH
(the RL-128 probe is a disabled hook, see `sources.RL128_PROBE_ENABLED`).

Modules:
- `budgets`: the RL-127 term 6 stage budgets and the 1.5x alarm factor.
- `ledger`: the JSONL timing ledger, the command wrapper and the phase hook.
- `runstate`: a lenient reader of RUN_STATE item headings and pointer blocks.
- `detect`: pure detectors over one snapshot.
- `alarms`: alarm deduplication and the delivery channels.
- `sources`: snapshot gathering (git, gh, ps) and over-budget profiles.
- `report`: the weekly pipeline-time report.
"""
