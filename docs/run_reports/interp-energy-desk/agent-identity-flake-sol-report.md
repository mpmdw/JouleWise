First-round work committed on `fix/2026-11-10-agent-identity-flake` (PR #712).
For the Fable follow-up and current verification, see the
[round-2 report](../2026-11-10-agent-identity-flake-r2.md).

The tests compared synthetic census rows against later live process reads. Fixed both cases with closed process fixtures feeding the real matcher, and removed the orphaned child. Measurement code is unchanged.

- Commits: `bbb01c8c3` (tests), `c2decb670` (report).
- Verification: 50/50 serial runs, 15/15 concurrent runs, compile check passed.
- Each module run: 12 passed, one existing sandbox `pgrep` skip.
- Controlled fixture exit reproduced both failure signatures. CI timings rule
  out 60-second expiry; multicall coreutils on ubuntu-26.04 is the leading,
  still unverified explanation (see the full report).

Changed [test_agent_identity.py](../../../tests/test_agent_identity.py) and the
[full report](../2026-11-10-agent-identity-flake.md).

Remaining native check outside the sandbox: `python3.13 -B -m unittest -v tests.test_agent_identity.AncestorCensusLiveTests`.
