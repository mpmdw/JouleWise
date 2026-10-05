# Fix seat: two existing tests need updating now that the `_v5` packs are committed (packs review F1, F2)

Worktree: /Users/edr/code/JouleWise-wt-dd5-packs (branch desk/2026-10-04-v5-pin-and-packs, head 196e532c: main + #476's floor identity fix + the pin + the three generated packs). Review: /Users/edr/night-archive/desk-day-v5/sol-pkreview.md. Commit if your sandbox allows; otherwise leave changes uncommitted. Do not push.

- F1: `tests/test_d117_floor_qwen25_1p5b_plan.py:~1700` asserts that neither `_v5` floor extraction spec exists (a sentinel from before generation). Replace the absence sentinel with verification of the committed specs' registration ordering at the pack's length L (the check the reviewer ran independently), keeping the registration mutation checks. Do not print L.
- F2: `tests/test_campaign_generator_core.py:~72` `LIVE_V5_GENERATORS` omits the emitted contrast generator `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generate_configs.py`; add it so the census (~195) and the live shared-core checks cover it.
- Then grep tests/ for any other test that asserts the `_v5` pack roots are absent/empty or enumerates generators, and fix the same way (tests only); list them.

Run to completion with `/Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-pktests/pc`: the two files, `tests/test_d117_contrast_v5_pack.py tests/test_d117_floor_qwen3_v5_generate.py tests/test_paper_reported_energy.py`, and every test that reads these pack roots (grep the three pack ids). No background processes.

WRITE_SCOPE: ["tests/test_d117_floor_qwen25_1p5b_plan.py", "tests/test_campaign_generator_core.py", "tests/**"]
Scratch: /tmp/dd5-pktests/ only. Tests only; no production code, no pack bytes. Finish in this turn.
