# Seat: lane RUN-CONFIG-NORMALIZED-PIN-01 (does the window-duration-margin reader compare run config bytes to a pin of the same bytes?)

Repository worktree: /Users/edr/code/JouleWise-wt-dd5-runcfg (branch fix/2026-10-04-run-config-normalized-pin, based on main 8fa002f7). Commit on this branch if your sandbox allows; otherwise leave changes uncommitted and say so. Do not push.

## The question
PR #463 found that the experiment runner writes each run's `config.json` as a default-filled re-serialization of the input config, so the run's `config.json` bytes are NOT the input config bytes; the G2-a summarizer was fixed to authenticate the run config through `scripts/summarize_g2a_prefill_probe.py::_authenticated_run_config_sha256` (read it and the #463 records: `docs/process_traces/2026-10-03-activation-5bffbeaf/00-session-record.md`, fix report and review there). The same seat flagged (finding F1) that `joulewise/window_duration_margins.py:~553` (`_member_observation`) compares `sha256(<bundle>/config.json)` to `expected_config_sha256`, described as "the pack pin". This reader is used by `scripts/record_window_duration_margins.py` on pack (`_v5` contrast and floor) windows.

## What to do
1. Trace `expected_config_sha256` to its producer: which pack/plan artifact records it, and over which bytes (the input config file in the pack, or the run's written `config.json`). Trace what the runner writes into `<run>/config.json` for a pack member (the same path #463 found). Decide, with file:line evidence, whether a real pack member would pass or be refused `member_config_mismatch` at line ~553.
2. If it would be wrongly refused: fix the reader to authenticate the run config the way the #463 summarizer does (byte-equal OR the authenticated re-serialization relation, whichever the #463 helper implements; reuse a shared helper rather than copying it if one exists in `joulewise/`, and if it lives only in `scripts/`, say whether moving it is needed). Add a regression test using a config written by the real runner serialization path (not a hand-written byte copy) and a negative test (a config whose content differs refuses).
3. If it would pass (the pin is already over the written bytes): change no code; add a test that pins this property (the producer and the reader hash the same bytes), and report the evidence.
4. Run the touched test modules plus `tests/test_window_duration_margins.py` and `tests/test_record_window_duration_margins.py` (if present); report counts.

## Write scope (exhaustive)
WRITE_SCOPE: ["joulewise/window_duration_margins.py", "tests/test_window_duration_margins.py", "tests/test_record_window_duration_margins.py", "tests/fixtures/custody_read_replay_allowlist.json"]
Do not touch the four pinned estimator files (`joulewise/powermetrics_fiducial.py`, `joulewise/uncertainty_evidence.py`, `joulewise/adapters/powermetrics.py`, `joulewise/reduce.py`), the runner, or the summarizer. If the right fix needs another file, stop and report why.

## Report
The verdict (wrongly refused / passes) with file:line evidence; files changed; commit sha or "uncommitted"; test commands with counts; findings outside scope. Finish in this turn.
