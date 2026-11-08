Committed `f1ff965fc` on `perf/2026-11-08-eng-desk`. Working tree clean; not pushed.

Added bounded parallel desk stages, shared thermal decoding, separate timing receipts, and authenticated laptop replay from a committed descriptor.

Synthetic outputs matched the original serial implementation byte for byte:

- Dense case: **18.10 → 9.78 s**, 1.85× faster.
- Small case: parallel execution was **4% slower**; default remains serial.

All **51 focused tests**, changed-file compilation, and diff checks passed. No full suite, network, model downloads, or real measurement reads.

The [run report](/Users/edr/code/CapstoneProject/jw-wt/sol-eng-desk/docs/perf/2026-11-08-eng-desk.md) lists changed files, exact verification commands, timings, and handoff instructions.

**Remaining:** actual harvest/export was not relocated or accelerated. The 30–45 minute turnaround remains unproven; the magistrate must benchmark the complete closed-record workflow and 1/2/4/8 workers in an MBP gap. Pending scientific gates remain unchanged.