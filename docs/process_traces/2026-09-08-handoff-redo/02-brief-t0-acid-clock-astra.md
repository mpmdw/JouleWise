WRITE_SCOPE: ["tests/test_arm_readiness_evidence_t0.py"]

# Seat brief — T0-ACID-CLOCK-01 (implementation, gpt-6-astra)

## 1. Mission
Fix the flaky acid test
`tests/test_arm_readiness_evidence_t0.py::test_acid_real_boot_session_then_real_arm_generator_reaches_go`.
TASK_QUEUE.md records (quote, do not edit): the test anchors R0 with `time.monotonic_ns()` under the real clock
while the author anchor is `monotonic_raw_ns`; on Darwin the two drift apart across sleep and uptime, so the
`T-0 RAW anchor span exceeds 3600000000000 ns` refusal fires once the drift exceeds the fixture margin (passed at
uptime 2 d 22 h, fails at 3 d 3 h). This machine's uptime is now > 5 days, so the failure should reproduce.
Cure shape: derive the fixture's R0 anchor from the same RAW clock the author uses (or from a synthetic anchor
with an explicit offset) and add a regression that fixes the two clocks apart by more than the margin (a
counterfactual that FAILS on the current test logic and passes after). Production arming is unaffected (one clock
family within a sequence) — do not change production code; if you believe production must change, return
NEEDS_RULING with the argument.

## 2. Steps
1. Reproduce: run the single acid test to a log; record rc and the refusal text.
2. Read how the author obtains `monotonic_raw_ns` (grep `monotonic_raw` in `joulewise/` — read-only) and mirror
   that clock source in the fixture.
3. Implement, then run the whole module `python3 -m unittest tests.test_arm_readiness_evidence_t0` to a log;
   report rc. Do NOT run the repository-wide suite.

## 3. Constraints
WRITE_SCOPE exhaustive (one file). No `git commit`. JSON envelope header < 8192 bytes.

## 4. Report (genre implementation)
`verdict.implementation` in {implemented, partial, no_change}; `verdict.acceptance` in
{ready, pending_verification, needs_ruling}. Body: the counterfactual the regression kills, both log tails with rc.
