# Delta check: packs PR #477 since your review (24741cab → ca5f3f11)

Worktree: /Users/edr/code/JouleWise-wt-dd5-pkdelta, detached at ca5f3f11. Your review at 24741cab: /Users/edr/night-archive/desk-day-v5/sol-pkreview.md (FAIL on two stale tests). Since then: main merged in (#474, #476: floors declare `prompt_tokens: null` in the decode identity unit), both floor packs regenerated with #476 (only `plan_tree*` and `producer_contract.json` changed), and the two tests fixed (`tests/test_campaign_generator_core.py`, `tests/test_d117_floor_qwen25_1p5b_plan.py`).

Executing: regenerate all three packs from this commit in a fresh `git clone --no-local` under /tmp/dd5-pkdelta and `diff -r` against the committed trees (must be empty); confirm the floors' science configs are byte-identical to 24741cab's; re-run your content checks (pin ids/length L on all prefill members; acceptance; reported-energy census and floor-to-contrast join at L); run the two fixed test files plus `tests/test_d117_contrast_v5_pack.py tests/test_d117_floor_qwen3_v5_generate.py tests/test_paper_reported_energy.py` with `/Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-pkdelta/pc`; judge whether the test changes weaken anything. Do not print L.

Verdict line first: `DELTA: PASS` or `DELTA: FAIL`, then findings with severity and evidence.

WRITE_SCOPE: []
Scratch: /tmp/dd5-pkdelta/ only. No background processes. Finish in this turn.
