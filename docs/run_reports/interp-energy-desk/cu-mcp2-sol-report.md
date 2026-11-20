Implemented all requested fixes on `ops/2026-11-11-computer-use-mcp`. Working tree is clean; nothing pushed.

Commits: `ce1713f10` (fixes), `03694cd5d` (report).

Changed the server, Swift helper, allowlist, README, functional/mutation tests, and one inserted timing line.

Verification:

- `python3.13 -B -m unittest tests.tools.test_computer_use_mcp` — 55 passed.
- `python3.13 -B -m unittest tests.tools.test_computer_use_mcp_mutations` — 31/31 mutants caught.
- Static compilation, JSON, timing-byte preservation, and diff checks passed.

No network, real screen/input, or study-data access occurred. No unresolved implementation questions. Native Swift compilation and GUI behavior remain unverified; the lead’s next step is an unarmed native smoke after the concurrent job ends.

[Full handoff report](/Volumes/JW-EXT/jw-wt/sol-cu-mcp2/docs/run_reports/2026-11-11-computer-use-mcp-r2.md)