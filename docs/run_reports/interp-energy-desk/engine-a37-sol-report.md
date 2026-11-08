**NEEDS_RULING:** Base `c8da9ee40` contains the engine-fix report but lacks its implementation. Should I include `184c37b25` and `8eb7982f0` before applying A37? I recommend including them; otherwise the change would target shared attribution code.

[AGENTS.md](/Users/edr/code/CapstoneProject/jw-wt/sol-engine-a37/AGENTS.md) requires stopping on an authority gap.

- Branch: `engine-a37`; clean, nothing pushed.
- Commit: `a8099a2806eac387b3eb3497a96c162cce8bb23b`.
- Changed only the [handoff report](/Users/edr/code/CapstoneProject/jw-wt/sol-engine-a37/docs/run_reports/2026-11-08-engine-a37-sol.md).
- Three targeted synthetic baseline tests passed; `git diff --check` passed.
- A37 implementation and `ENGINE-sol.md` update remain pending.

The ruling lookup inadvertently returned adjacent sealed B5 summary text. That exposure is documented; no source artifacts were opened or used.