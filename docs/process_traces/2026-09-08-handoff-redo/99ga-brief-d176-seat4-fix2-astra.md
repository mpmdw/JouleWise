WRITE_SCOPE: ["tests/test_launch_window.py","tests/test_t0_rehearsal.py"]

# D-176 seat 4 fix round — two test repairs (gpt-6-astra, medium, genre implementation)
Worktree feat/2026-09-08-d176-seat4-rehearsal at 3032dd93 with the UNCOMMITTED fix round in the tree (report
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99fz-seat-d176-seat4-fix-partial-astra-report.md; keep every edit). Two named-acceptance failures remain, both
test-side: (F1) tests/test_launch_window.py ~:2368 — the DIAGNOSTIC_NO_PACK admission regression's fixture omits the
required `registration_path`, so it never reaches admission: complete the fixture so the non-pack path is exercised and
the assertion (admission does not touch non-pack launches) bites; (F2) tests/test_launch_window.py ~:2459 — the
refusal regression expects zero rehearsal consumptions, but the new completed-rehearsal fixture correctly retains one:
change the assertion to "the pre-existing rehearsal consumption is preserved byte-for-byte AND no NEW consumption
appears in the control custody". Change nothing else. Acceptance (rc-gated; named modules ONLY, never discover/shard):
tests.test_launch_window tests.test_t0_rehearsal; git diff --check; no commit; header < 8192 bytes; report before/after.
