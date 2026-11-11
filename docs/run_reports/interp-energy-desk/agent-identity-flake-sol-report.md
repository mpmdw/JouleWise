Committed locally on `fix/2026-11-10-agent-identity-flake`; clean tree, nothing pushed.

The tests compared synthetic census rows against later live process reads. Fixed both cases with closed process fixtures feeding the real matcher, and removed the orphaned child. Measurement code is unchanged.

- Commits: `bbb01c8c3` (tests), `c2decb670` (report).
- Verification: 50/50 serial runs, 15/15 concurrent runs, compile check passed.
- Each module run: 12 passed, one existing sandbox `pgrep` skip.
- Controlled fixture expiry reproduced both failure signatures; the original CI trigger remains unconfirmed.

Changed [test_agent_identity.py](/Volumes/JW-EXT/jw-wt/sol-agent-identity-flake/tests/test_agent_identity.py) and the [full report](/Volumes/JW-EXT/jw-wt/sol-agent-identity-flake/docs/run_reports/2026-11-10-agent-identity-flake.md).

Remaining native check outside the sandbox: `python3.13 -B -m unittest -v tests.test_agent_identity.AncestorCensusLiveTests`.