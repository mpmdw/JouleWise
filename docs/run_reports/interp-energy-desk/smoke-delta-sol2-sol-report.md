**HOLD.** Five blocker classes remain: detach/TOCTOU isolation escapes, preparation bypassing the deadline, missed cleanup after installation, forged-plan admission, and incomplete packet-chain mutations.

Committed `ec2213b6d` on `align/2026-11-08-w1-smoke-delta-sol2`. Working tree clean; no push.

Changed only:

- [Witness tests](/Users/edr/code/CapstoneProject/jw-wt/sol-smoke-delta-sol2/tests/align/test_smoke_delta_sol2.py)
- [Report with commands, evidence and repair criteria](/Users/edr/code/CapstoneProject/jw-wt/sol-smoke-delta-sol2/docs/align/v4/w1-smoke-delta-sol2.md)

Verification took about 12 minutes, serially:

- Smoke and prior witnesses: **58 tests pass**.
- Delta: **7 controls pass; 8 property tests fail**, reproducing the findings.
- Clean-clone `--w1-next w1`: **FAIL**, 9 PASS / 7 FAIL / 1 WARN.
- PREQUAL module: two meter failures remain sandbox-limited; the shim-induced R1 failure passes on corrected rerun.
- `compileall`: passes.

Next: disposition and fix D2-1–5. Installed-plan identity binding and the TOCTOU trust boundary need lead decisions. Native MBP timing, teardown, KM003C and MLX checks remain unverified.