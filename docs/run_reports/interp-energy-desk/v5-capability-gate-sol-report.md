Implemented on `align/2026-11-08-v5-capability-gate`; working tree clean.

- Added episode success/work accounting, assigned-cap `S_hidden(H)`, hint fallback, and staged D0 reader.
- Draft gate: 40 seeds per pair/hint setting; ≥10 successes and exact 90% lower bound ≥15%. Both hints failing yields a capability-limits result.
- Added two synthetic test modules, rule documentation, and [handoff report](/Users/edr/code/CapstoneProject/jw-wt/sol-v5-capability-gate/docs/align/squeeze/fanout/capability-gate.md).

Local commits: `8d07587ad`, `c8a8cac7b`. Nothing pushed.

Verification: **59 tests passed**, each module separately using `python3.13 -B -m unittest`:

- `tests.align.test_capability` — 14
- `tests.align.test_capability_d0` — 8
- `tests.align.test_records` — 4
- `tests.align.test_tamper` — 9
- `tests.align.test_runner` — 24

Syntax and diff checks passed. No full suite, network, real-data analysis, or MLX execution.

Outstanding: lead admission of the draft rule, a staged unblinded pilot export for D0, and native validation of future cap enforcement. Existing Apple records may leave concealed scratchpad size unknown. Coordination files and R1 were untouched.