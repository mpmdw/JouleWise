# X2 follow-up (Sol 6.1 high): genesis fixtures supply their pinned acceptance

Worktree: /Users/edr/code/JouleWise-wt-dd5-x2 (branch feat/2026-10-05-v5-qual-x2; your previous run's work is committed by the lead). Previous report: `/Users/edr/night-archive/desk-day-v5/sol-x2.md` (F1). Scratch /tmp/dd5-x2f/ only. Leave changes uncommitted; never push.

The finalizer and checker now replay the bracket with the acceptance cutoff, so three test files whose genesis fixtures omit the acceptance input fail with the intended refusal. In `tests/test_pipeline_smoke_tail.py`, `tests/test_d165_dominance_closeout.py` and `tests/test_analysis_integration.py`, pass each genesis fixture its pinned acceptance (`acceptance_bound_path=fixture['acceptance_path']`, or route the real byte-pinned genesis loader where a CLI or downstream API lacks the argument). Do not weaken any production check or any assertion. Run those three files and `tests/test_v5_block4_x2.py tests/test_analysis_finalizer.py tests/test_check_window_provenance.py`. Finish in this turn.

WRITE_SCOPE: ["tests/test_pipeline_smoke_tail.py", "tests/test_d165_dominance_closeout.py", "tests/test_analysis_integration.py"]
