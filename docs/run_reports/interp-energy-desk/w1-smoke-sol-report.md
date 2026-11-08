Partial handoff committed on `align/2026-11-08-w1-smoke`; clean tree, no push.

- Added offline PREQUAL checks, smoke recorder/parser, synthetic tests, and [W1-SMOKE.md](/Users/edr/code/CapstoneProject/jw-wt/sol-w1-smoke/docs/align/v4/W1-SMOKE.md).
- Commits: `8fd55af2a`, `b122a6298`.
- Verification: 38 new tests and 19 existing focused tests passed; compileall and diff checks passed. Commands/results and changed files are in the [run report](/Users/edr/code/CapstoneProject/jw-wt/sol-w1-smoke/docs/run_reports/2026-11-08-w1-smoke.md).
- PREQUAL correctly returned nonzero: three PASS, four FAIL.

**The native kit remains incomplete.** Production accepts stale valid triage packets, and the unchanged scaffold alone takes 83 minutes.

Two rulings are pending: permit a reduced smoke scaffold or exceed 45 minutes; assign production triage binding here or leave it lead-owned. These change contract semantics, so I followed AGENTS.md’s early-return rule. Native hardware validation remains unperformed.