# Executing review: RUN-CONFIG-NORMALIZED-PIN-01 at ee749c39 (branch fix/2026-10-04-run-config-normalized-pin)

Worktree: /Users/edr/code/JouleWise-wt-dd5-rcreview, detached at ee749c39 (parent main 8fa002f7). Diff: `git diff 8fa002f7 ee749c39` (`joulewise/window_duration_margins.py`, `tests/test_window_duration_margins.py`). Author's report: `docs/process_traces/2026-10-04-desk-day-v5/12-sol-runcfg-report.md` on branch records/2026-10-04-desk-day-v5 (also at /Users/edr/night-archive/desk-day-v5/sol-runcfg.md). You are a non-author reviewer with an EXECUTING lens.

The change: the reader used to compare sha256(<run>/config.json) with the pack pin; the pin is over the pack's SOURCE config bytes and the runner writes `BenchmarkConfig.to_dict()` re-serialized bytes, so real members were refused. Now it (1) locates each member's source config through the authenticated plan tree's science rows (`_member_input_paths`; repo-relative for floor generators, pack-relative for GAMMA, chosen by `downstream_contract.extraction_spec`), (2) requires sha256(source bytes) == pin, (3) requires sha256(run config.json) == `controller._config_sha256(BenchmarkConfig.from_mapping(source))`, (4) requires metadata `config_sha256` to equal the run config hash.

Check, executing:
1. Does it now pass a REAL pack member? Build one end to end through the real runner serialization path (the CLI/bundle writer the seat cites, `joulewise/cli.py:~292`, `joulewise/bundle.py:~950`) from a real generated pack config (a `_v5` or floor pack config in the repo), and run `_observe_member` on it. Show it passes; show a member whose source config differs by one field refuses; show a run config.json edited after the run refuses.
2. Is any authentication weakened compared with the old byte check? E.g. could two different source configs normalize to the same run bytes, and does that matter given (2)? Is `_config_sha256` the exact function the runner used to write `metadata.config_sha256` (file:line)?
3. `_member_input_paths`: the `source_root` choice heuristic (is `downstream_contract` always present, a Mapping? KeyError/TypeError paths?), path confinement (`_safe_relative_path`), duplicated or missing science rows, and whether the plan tree read is authenticated (bound by `tree_sha` from `_pack_inventory`) or a second unauthenticated read of the same file.
4. Custody read-replay: does the new `read_authentication_input` call require an update to `tests/fixtures/custody_read_replay_allowlist.json` and its consuming test? Run that test.
5. Run `python3 -m pytest -q tests/test_window_duration_margins.py tests/test_custody_mode_inventory.py` plus any test module importing `joulewise.window_duration_margins` or `scripts/record_window_duration_margins.py` (grep). Use /Users/edr/code/JouleWise/.venv/bin/python if needed.

Verdict line first: `REVIEW: PASS` or `REVIEW: FAIL`, then findings with severity (BLOCKER/MAJOR/MINOR/NIT), file:line and a failing command where possible.

WRITE_SCOPE: []
Scratch: /tmp/dd5-rcreview/ only. Finish in this turn.
