Completed on clean local branch `engine-fix`; nothing pushed.

- Applied R21 engine changes, streaming reducer, raw ingestion, benign DC LOTO analysis and incremental window mode.
- **179 targeted tests passed**, plus compileall and diff checks.
- Scanner measured **549 MB/s/core**. The 845 MB synthetic series produced byte-identical outputs across serial/parallel cold/cache modes.
- Commits: `184c37b25`, `8eb7982f0`.

[Handoff report](docs/run_reports/2026-11-08-v4-engine-fix-sol.md) lists changed files, exact test commands and limits. [ENGINE-sol.md](docs/analysis/v4/ENGINE-sol.md) contains the A0–A36 code map.

Remaining lead gates: native exporter integration, full-size Air/DC timing and independent comparator qualification. No ruling questions remain; no study data or full suite was accessed.