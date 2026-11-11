Implemented on `ops/2026-11-11-computer-use-mcp`; worktree clean, nothing pushed.

- Added the stdio server, Swift helper, allowlist and README under `tools/computer_use_mcp/`, synthetic tests under `tests/tools/`, and one timing-map line.
- Commits: `6d628733b` implementation; `e4d3b7378` report.
- `python3.13 -B -m unittest tests.tools.test_computer_use_mcp`: **32 passed**. Syntax, stdlib imports, JSON, timing-map preservation and diff checks passed. No full suite or network used.
- **Unverified:** real Swift compilation, screenshots, Accessibility/TCC, native input and headless LaunchAgent behavior. No open design questions; next step is the documented native smoke outside armed/quiet windows.

[README](/Volumes/JW-EXT/jw-wt/sol-cu-mcp/tools/computer_use_mcp/README.md) · [Run report](/Volumes/JW-EXT/jw-wt/sol-cu-mcp/docs/run_reports/2026-11-11-computer-use-mcp.md)