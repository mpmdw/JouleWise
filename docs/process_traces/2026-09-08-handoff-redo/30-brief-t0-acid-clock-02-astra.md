WRITE_SCOPE: ["tests/test_launch_window.py"]

# Seat brief — T0-ACID-CLOCK-02: launch-window test mints T-0 evidence with mixed clock families (gpt-6-astra, medium)

Sibling of T0-ACID-CLOCK-01 (fixed on main at e4ce8b3b in tests/test_arm_readiness_evidence_t0.py: the fixture's
R0 anchor now derives from `sample_anchor().monotonic_raw_ns`, the author's RAW clock, plus a regression that fixes
the clock families 2 h apart). A full-suite replay on this Mac (uptime > 5 days) at 02:29 PDT today errored:
`tests/test_launch_window.py:835 test_real_minted_v4_launch_accepts_relocation_and_refuses_content_change` →
`_mint_v4_arm` (`:750`) → `joulewise/arm_readiness_evidence_t0.py:2315 author_arm_readiness_evidence_t0` →
`:1163 _derive_clock_attestation` → `T0EvidenceAuthoringError: T-0 RAW anchor span is below 600000000000 ns`.
CI on Linux passes the same module; the divergence is Darwin's RAW vs ordinary monotonic drift across sleep/uptime.

Do: (1) reproduce with the single test to a log (expect the refusal on this machine; if it passes, say so and
record uptime via `sysctl kern.boottime`); (2) read how the fixed acid fixture derives R0 (`git show e4ce8b3b --
tests/test_arm_readiness_evidence_t0.py` is read-only history) and apply the same clock-family discipline to
`_mint_v4_arm` and any other helper in tests/test_launch_window.py that anchors R0 or the sequence age; (3) add a
regression that fixes the two clocks 2 h apart in BOTH directions and fails on the current test logic; (4) run the
whole module to a log; report rc. Production code must not change (NEEDS_RULING if you believe it must). Do NOT run
the repository-wide suite. No `git commit`. Header < 8192 bytes; genre implementation verdict keys; body = the
counterfactual killed, fail-before/pass-after tails, module rc.
