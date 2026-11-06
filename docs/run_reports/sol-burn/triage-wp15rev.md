# Triage of sol/burn-wp15rev (lead-side verification, 2026-11-06)

All four defects are present at f1864e314 and unchanged on the r4 integration head
(r4-integ-local d9c709ee5; r1_runtime.py is identical). The four new regressions fail
there. The patch applies cleanly to d9c709ee5. tests.align.test_r1_runtime +
test_r1_rehearsal: 53 OK with the patch.

- F4 (gated-D slots): REAL, MEDIUM. derive_step_d_slots can legitimately emit B_D = 0
  (max(0, ...) when the budget is under 1024 tokens). The old code then set
  max_episode_decode_tokens=None, so the run had no decode cap (fail-open). The fix
  refuses instead. A NaN or non-positive T_dead is reachable only by tampering.
- F3 (step-d custody binding): REAL but LOW. The driver runs step-d and the gated D runs
  in order and refuses on a nonzero exit. It also re-checks T_dead after each gated run
  (_check_gated_t_dead). What remains is a post-close edit of B_D or N_chunk, or a custody
  write that fails while the exit code is still 0.
- F2 (nested runtime_custody.json excluded): REAL but LOW, hypothetical. Nothing writes
  that name below a segment.
- F1 (ManagedSession): mostly OVERSTATED. Production never passes on_close, closers holds
  at most one item, and the old finally already ran it. The real remaining gap is not
  fixed: Segment.close catches only Exception, so a first TERM (SystemExit) during
  teardown leaves the remaining open sessions unclosed (powermetrics stop) and skips
  stop_journals. Proposed: catch BaseException in Segment.close and keep going.
