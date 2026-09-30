DELTA: FINDINGS

Opus 5.5 read-only delta check of the uncommitted fix round in the rev6int worktree (head 1b419f0e plus 18 modified files). The worktree was not modified (still 18 dirty files, no untracked files). Probes are in scratchpad/fix2delta/.

SUITE: I ran the 13 briefed modules with python3 -B: 776 tests, 1 skipped. All 42 failures were in test_gen_derivation_night, all with "no census-clean temporary directory". The cause was the TMPDIR I set (the path contains "claude"). Rerun with TMPDIR=/private/tmp/f2d-ff50b201: 50/50 OK. Net result: all green.
PINNED ESTIMATORS: none touched. None of the four P8 pins (powermetrics_fiducial, uncertainty_evidence, adapters/powermetrics, reduce) appears in the diff, and all four sha256 values equal P8's.

RULINGS
1 DONE. cap_replay_harness.py:138-155,217 adds compare_stored_bound=False. It decodes in "BLIND" mode, so b_fiducial_s is never decoded and _stored_reproduced is never called. harvest_window.py:120-122 uses only this path.
  Probe probe_r1.py: I wrapped every JSON dict get/[] call, LedgerObservation.exact_bound_lexeme_s, _stored_reproduced and _evidence_inputs, then ran the real e2e and null harvests. Results:
  - 12 harness calls, all in BLIND mode.
  - 0 _stored_reproduced calls; 0 B decoded by the harness; 0 harvest or issuer accesses of any bound field.
  - The only reads are by the generic ledger loader (calibration_ledger.py:967/1605), which builds each row.
  - Residual: some decoders parse the whole instrument_evidence.json, so the B lexeme sits in memory without its key ever being read. These are _read_member_evidence :1790, battery_float :730, and _revision_six_anchor_outcome :1503. The first two predate this round.
  REPORT comparison defaults to on outside harvest. The sweep row was updated.
2 DONE. harvest_window.py:143-145: `disposition` is now the ledger word, and `replay_disposition` is the harness word. Test test_real_harvest_to_issuer_invalid_and_clock_unresolved runs real harvest (real harness; only the detector is mocked) into the real revision_six_records/count_replay: NEXT_WINDOW, counted 11, members 10, with a clock refusal at slot 12.
  Counterfactual probe_r2.py: re-introducing B1 in-process makes the test FAIL with "disagrees with ledger".
3 DONE. Issuer :1558-1567 accepts null work fields and a ledger reason; such a slot is not counted and raises no stop. Real harvest output was accepted (probe_r3: ledger_reason='ordinary-invalid'; no R9 stop; only STOP-FUTILITY from the 1-of-12 fixture).
  Nit: the issuer checks only that ledger_reason is truthy, not that it equals the ledger's word.
4 DONE. harvest_window.py:311-352 writes a null record with abort_reason for a refused start and for a missing start; the issuer accepts TERMINAL_SESSION_STATES (:1537). Test test_revision6_null_refused_or_aborted_harvest_is_issuer_input: ok.
5 DONE. harvest_window.py:120-126 tries up to 3 times. After 3 wall deadlines, harvest refuses without writing a record. The tests for retry-then-success (3 calls, cap_trigger None, no STOP-R9-DEADLINE) and for 3 deadlines refusing both passed.
  Note: STOP-R9-DEADLINE (the campaign void) is now unreachable from harvest output, as ruled.
6 DONE (misdispatch not traced end to end).
  - Issuer :2615 names R7 explicitly; the rev5 ACTIVE patch was removed.
  - Real W1/W2 Rev5 prepare (rev5_replay.py) with shipping ACTIVE=r8 unpatched: WI13_W1W2_REPLAY=PASS, byte-identical to baseline, n=12.
  - A misnamed Rev 6 session refuses with "pattern mismatch" (test ok). The generator enforces the pattern (gen_derivation_night.py:556-567; test ok).
  - Caveat: Rev 6 is selected by the "# Revision 6 (" marker in the digest-authenticated registration text, not by comparison with a sealed digest constant. Harvest cross-checks the plan registration digest (:224-230).
7 DONE. Harvest imports issuer.revision_six_count_replay (:321-326) and writes next_window plus next_window_sha256. The generator (:952-965), run_night (:3063-3072, :3128) and issuer start-conditions (:1445-1460) authenticate the decision and refuse anything but NEXT_WINDOW. The STOP and tamper tests pass (generator and driver; the driver refuses before the OFF receipt and before the chain).
8 PARTIAL. Normal path: OFF, then dwell during the settle, then a fresh t0 census, thermal and battery, then chain start (run_night.py:3361-3378). Test ok; argv matches the runbook.
  REGRESSION: if a plan has quiet_admission and its first census sees an agent, derivation_admission stays None. When bind then returns GO, `manifest, manifest_evidence, budget = derivation_admission` (:3512) raises an uncaught TypeError. probe_r8.py: "UNCAUGHT TypeError cannot unpack non-iterable NoneType". No chain starts, but the driver crashes without writing a result or report. HEAD ran the admission after the gate, so this path worked before this round.
9 DONE in code, but the test does not discriminate. Live test on this Mac with the new check-8 pipeline:
  - baseline count 4;
  - a python process whose arguments are /tmp/claude/x.json and /tmp/codex/y.json: still 4;
  - a process whose executable is named `claude`: 5.
  The test's fake `ps` ignores its argv and prints only the executable, so test_driver_arguments_containing_agent_strings_are_allowed also PASSES against HEAD's `ps aux|grep` script (probe_r9.py).
  Also: comm names with a space (e.g. "Codex (Service)", "T3 Code") are no longer counted. night_gate's broad `pgrep -lf` census still catches them at t0.
10 DONE. Issuer :1660-1736 checks each of the four pin files (chain, validator, cap_rule_text, roster) against its sealed digest. It writes the campaign record (5 clauses, harness and cap-rule digests, clock refusals by slot) and refuses until that record is committed. Test (B read patched to raise; each pin byte-mutated refuses): ok.
11 DONE. calibration_bracketing.py:1122 returns False on ImportError. Test ok.

WEAKENED TESTS (diff of tests/)
- test_harvest_window: three `assertEqual(stop_flags, ["STOP-R9-FRAME"])` became assertIn, and `assertEqual(stop_flags, [])` became assertNotIn(FRAME). The reason is that stop flags now include STOP-FUTILITY from the padded fixture. They should pin the exact list.
- test_revision6_cap_triggers_are_preserved was deleted. No harvest test now feeds evaluated_cell_budget. The behaviour still holds: my probe_cell.py shows cap_trigger preserved and STOP-R9-CELL raised. The coverage should be restored, because this is the path by which a truncated search would count.
- The ruling-9 test is non-discriminating (above).
- The other changes follow rulings 6 and 10 (R7 named explicitly, docstring text, the two-step prepare).
- Nit: `check` without --preregistration no longer refuses r6-named sessions; it runs the ordinary dry run.

FALSE NUMBER? I found no path. Every new mismatch refuses. The quiet-admission crash starts no chain. The deleted cell-trigger test is a coverage gap; the behaviour is currently correct.
