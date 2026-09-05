```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "The real-clock fixture now derives R0 from a contemporaneous real realtime-minus-RAW offset and asserts a 10x margin inside the unchanged 5 ms ceiling.",
  "workspace": {"base_requested":"c52185271f2abdc5bb171945af229d619778240a","base_mode":"exact","head_start":"c52185271f2abdc5bb171945af229d619778240a","head_end":"c52185271f2abdc5bb171945af229d619778240a","upstream_end":"c52185271f2abdc5bb171945af229d619778240a","branch":"int/2026-09-04-fan-wave-2"},
  "pathspec": ["tests/test_arm_readiness_evidence_t0.py","docs/process_traces/2026-09-04-fanout/31-t0-real-boot-test-cure.md"],
  "unowned_dirty": [],
  "verdict": {"implementation":"implemented","acceptance":"pending_verification"},
  "verification": [
    {"id":"V1","kind":"test","cmd":"python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_acid_real_boot_session_then_real_arm_generator_reaches_go","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["s","----------------------------------------------------------------------","Ran 1 test in 0.006s","","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"Ran 1 test in .*s[\\s\\S]*OK \\(skipped=1\\)"}},
    {"id":"V2","kind":"test","cmd":"python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_acid_real_boot_session_then_real_arm_generator_reaches_go","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["s","----------------------------------------------------------------------","Ran 1 test in 0.004s","","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"Ran 1 test in .*s[\\s\\S]*OK \\(skipped=1\\)"}},
    {"id":"V3","kind":"test","cmd":"python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_acid_real_boot_session_then_real_arm_generator_reaches_go","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["s","----------------------------------------------------------------------","Ran 1 test in 0.004s","","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"Ran 1 test in .*s[\\s\\S]*OK \\(skipped=1\\)"}},
    {"id":"V4","kind":"test","cmd":"python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_acid_real_boot_session_then_real_arm_generator_reaches_go","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["s","----------------------------------------------------------------------","Ran 1 test in 0.003s","","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"Ran 1 test in .*s[\\s\\S]*OK \\(skipped=1\\)"}},
    {"id":"V5","kind":"test","cmd":"python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_acid_real_boot_session_then_real_arm_generator_reaches_go","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["s","----------------------------------------------------------------------","Ran 1 test in 0.004s","","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"Ran 1 test in .*s[\\s\\S]*OK \\(skipped=1\\)"}},
    {"id":"V6","kind":"suite","cmd":"python3 -m unittest tests.test_arm_readiness_evidence_t0","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["..............","----------------------------------------------------------------------","Ran 67 tests in 414.758s","","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"Ran 67 tests in .*s[\\s\\S]*OK \\(skipped=1\\)"}}
  ],
  "flags": [
    {"id":"F1","kind":"environment","level":"nonblocking","text":"git fetch origin main was attempted but the managed sandbox denied writing the parent worktree FETCH_HEAD; the existing origin/main e323f1aa contained and supplied the requested diagnosis.","needs":"Lead may refresh origin/main outside this managed sandbox if remote freshness beyond e323f1aa is required."},
    {"id":"F2","kind":"verification_gap","level":"nonblocking","text":"All five focused invocations and the module passed, but the real-boot method skipped because this managed seat denies kern.bootsessionuuid; the new measured-delta assertion did not execute here.","needs":"Replay the named method on a socket/host-capable Darwin seat where kern.bootsessionuuid is readable."}
  ]
}
```

## Change

The non-synthetic fixture samples a real clock anchor and carries its realtime-minus-RAW offset and read skew into the aged R0 capture. The real-boot transaction reads its authored clock receipt and requires the measured anchor delta to remain below 500,000 ns, while the production ceiling and the existing 5 ms ± 1 ns boundary coverage remain unchanged.

## Verification notes

The focused method was invoked five times, then the full requested module ran. Every invocation exited zero; the environment skipped the real-boot method because `kern.bootsessionuuid` is unavailable. The required fetch also could not update `FETCH_HEAD`; the diagnosis was read from the existing `origin/main` at `e323f1aa`.

## Residual risk

The real-clock assertion still needs one non-skipped Darwin replay to confirm the observed sub-500 µs margin end to end.
