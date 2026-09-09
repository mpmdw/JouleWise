# Cold-gate packet — PR #309 replay door after two attempts (follow-up to ruling 44 Q2)

Assembled by magistrate activation 2145630c on 2026-09-09 ~08:45 PDT. Trigger: rule-11 (reinterpretation of a ruling's acceptance
condition) + the standing escalation trigger (two consecutive replay attempts failing with the same signature: timing-sensitive tests
under four-shard concurrency, each passing alone). Packet files are frozen at assembly; amendments are dated addenda only. SHA256 of
every listed file is in 55-coldgate-packet.sha256.

- P1 44-coldgate-ruling-replay-verdict.md (Q2 A1–A6: exactly the four named IdleAdmissionCoreVerdictTests failures and nothing else)
- P2 45-coldgate-opus-refuter-replay-verdict.md (refuter: flaky wall-clock coupling; wanted rc 0 with bounded retries for a code PR)
- P3 53-replay-309-attempt1-dd135364-tail.txt (5642 tests, 5 failures: the four + test_docs_freshness volatile-literal — caused by the
  magistrate's own README blurb on main, cured on main at a3da3463, main CI green)
- P4 54-replay-309-attempt2-6d76f964-tail.txt (5642 tests, 5 failures: the four + test_arm_readiness_lifecycle
  test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses — thread join timeout under load; passes alone 3/3 at 23.5 s)
- P5 55-arm-integration-load-01-kernel-row.txt (the registered lane for load-sensitive tests under concurrent replay: "four load refusals")
- P6 42-bench-rootcause-low-power-mode.md (+ addendum) and 39b logs (the four fail alone 4/4/3; timer slack 2.1–3.6×)
- P7 31-terminal-review-night-gate-stub-chain.md (+ A6 addendum): PR #309 content review CLEAN at 5db38b58; A2 pathspec/import
  independence and A3 recorded in /tmp draft 52 (quoted in the charge); A4 not yet run on the integration tree; A5 CI green at 5db38b58
  (integration head 6d76f964 CI pending)
