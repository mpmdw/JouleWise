Committed locally on `x86/2026-11-08-cuda-backend`:

- `ba03c31a9` — import shared ALIGN runner and interfaces.
- `4740de170` — add llama.cpp backend, Linux samplers, quiet guard, DRAFT configs and documentation.

The path preserves seed provenance, token accounting, reasoning and transcripts. Every member requests wall-meter capture and records missing-stream flags. Apple/R0 code and coordination files remain unchanged. Working tree is clean; nothing was pushed.

Verification: **124 tests passed, 1 optional pynvml test skipped**; compileall passed. Exact commands, results and changed-file details are in the [handoff report](/Users/edr/code/CapstoneProject/jw-wt/sol-x86-backend/docs/run_reports/2026-11-08-x86-cuda-backend.md).

Hardware remains **PROVISIONAL**. Python 3.11 and native MLX checks were unavailable. Canonical 64-bit seeds are retained, with an explicit 32-bit llama.cpp projection; cross-engine output equality is unverified.

Next: pin the server/GGUF and real AC meter, then have Ed qualify the clean rig using [CUDA-BACKEND.md](/Users/edr/code/CapstoneProject/jw-wt/sol-x86-backend/docs/x86/CUDA-BACKEND.md).