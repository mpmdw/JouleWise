# Wave-2 integration tree — full unpiped replay disposition (row 9 evidence)

Replay 3 on c5218527 (log: magistrate job dir, int-fan-wave2-replay-3.log), exact tail:

    Ran 5116 tests in 6929.138s
    FAILED (failures=1, errors=1, skipped=110)

Both failures diagnosed in 30-replay-3-failure-diagnosis.md and dispositioned:

1. tests.test_node_worker_subprocess…test_real_client_worker_artifact_contract_over_localhost —
   ENVIRONMENTAL / PRE-EXISTING TEST SENSITIVITY: NV-5 localhost fake-vLLM prepare exceeded the test-only 15 s
   budget under concurrent Mac load; identical main/wave-2 bytes (git diff f1430906..c5218527 empty for the
   worker, client and test), the same failure reproduces on canonical main in isolation under the same load,
   earlier same-Mac 3× green (cd6e2cba), and green Linux CI on this PR head exclude a wave-2 regression.
   Production prepare budget is 900 s. No cure on this tree.
2. tests.test_arm_readiness_evidence_t0…test_acid_real_boot_session_then_real_arm_generator_reaches_go —
   TEST DEFECT unblocked by FIXTURE-MODERNIZATION-01 (structural skip removed): the real-boot case built R0 from
   the fictional 2e18 ns synthetic offset against a real author anchor (delta ≈ 6.7 years). The 5 ms ceiling is a
   production invariant and is unchanged. Test-only cure (31-t0-real-boot-test-cure.md) constructs R0 from a
   contemporaneous real realtime − CLOCK_MONOTONIC_RAW offset. Magistrate bench re-run outside the sandbox on the
   cured tree, this session:

    Ran 1 test in 10.711s  OK
    Ran 1 test in 10.760s  OK
    Ran 1 test in 10.663s  OK
    tests.test_arm_readiness_evidence_t0: Ran 67 tests in 431.905s  OK
