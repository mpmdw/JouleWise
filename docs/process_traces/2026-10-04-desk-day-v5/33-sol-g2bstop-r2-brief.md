# Implementation seat, round 2: G2-b one-block stop — the provenance checker's termination regression (scope granted)

Worktree: /Users/edr/code/JouleWise-wt-dd5-g2bstop (branch feat/2026-10-04-g2b-one-block-stop; your round-1 work is committed as the branch head). Round-1 report: /Users/edr/night-archive/desk-day-v5/sol-g2bstop.md. Commit if your sandbox allows; otherwise leave changes uncommitted. Do not push.

Ruling on F1: scope granted for `tests/test_check_window_provenance.py` (and `scripts/check_window_provenance.py` ONLY if the checker itself encodes the SIGINT/130 termination as an expected value; say which). Replace the obsolete termination assertions with the new contract: the G2-b chain's science stage ends with rc 3 and a terminal `max_blocks_reached` row after exactly one complete strict-valid A/B/B/A block; a stage that ends any other way is not the registered stop. Keep every other assertion. F2: confirm the 60 s first-run timeout reproduces at 8fa002f7 in your environment and leave it (pre-existing). Run to completion: `tests/test_check_window_provenance.py tests/test_run_campaign_max_blocks.py tests/test_gen_g2_phase_d.py tests/test_run_campaign.py` and `python3 scripts/gen_g2_phase_d.py --check`. No background processes.

WRITE_SCOPE: ["tests/test_check_window_provenance.py", "scripts/check_window_provenance.py", "tests/fixtures/**"]
Scratch: /tmp/dd5-g2bstop2/ only. Finish in this turn.
