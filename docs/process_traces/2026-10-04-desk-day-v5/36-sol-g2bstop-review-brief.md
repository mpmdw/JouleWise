# Executing review: unattended one-block stop for G2-b (branch feat/2026-10-04-g2b-one-block-stop at 278a719c)

Worktree: /Users/edr/code/JouleWise-wt-dd5-gsreview, detached at 278a719c (parent main 8fa002f7). Diff: `git diff 8fa002f7 278a719c`. Brief and reports: `docs/process_traces/2026-10-04-desk-day-v5/24-*`, `33-*` on branch records/2026-10-04-desk-day-v5 (or /Users/edr/night-archive/desk-day-v5/sol-g2bstop.md, sol-g2bstop2.md). You are a non-author reviewer with an EXECUTING lens.

The change: `scripts/run_campaign.py` gains `--max-blocks N`, bound to the authenticated plan/authorization `permitted_blocks` (CLI cannot widen it; omission keeps the bound; conflict refuses before dispatch); after N complete, strict-valid A/B/B/A blocks it stops between members, writes a terminal `max_blocks_reached` row and exits rc 3. The G2-b chain rendered by `scripts/gen_g2_phase_d.py` (and the pinned runbook/runsheet regions) now runs the first frozen science stage with this stop instead of an operator's SIGINT (rc 130). `run_campaign.py` is the chain every claim window runs, so behaviour without `--max-blocks` must be byte-identical.

Check, executing:
1. Without `--max-blocks` and without a bound: campaign log, rc and every artifact byte-identical to main on a representative fixture campaign (show the comparison).
2. With the bound: the stop fires exactly after block N, never mid-member; a block containing a failed or invalid member does not count as complete and the campaign continues or fails as main would; the terminal row and rc 3 appear only for the registered stop; a crash or signal is never reported as rc 3. Try to make rc 3 appear without N complete blocks.
3. Binding: can a CLI value exceed `permitted_blocks`? Where is `permitted_blocks` read from and is that read authenticated (file:line)?
4. The rendered G2-b chain: `python3 scripts/gen_g2_phase_d.py --check` passes; the chain asserts rc 3 and still runs the post-bracket path; no other rendered region changed (diff the runbook/runsheet).
5. Run `/Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_run_campaign_max_blocks.py tests/test_gen_g2_phase_d.py tests/test_check_window_provenance.py tests/test_run_campaign.py` and other importers of run_campaign (grep); for failures compare at main (the 60 s first-run timeout in test_check_window_provenance reproduces at main).

Verdict line first: `REVIEW: PASS` or `REVIEW: FAIL`, then findings with severity, file:line and a failing command where possible.

WRITE_SCOPE: []
Scratch: /tmp/dd5-gsreview/ only. No background processes. Finish in this turn.
