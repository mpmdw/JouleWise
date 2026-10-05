# Executing review: PR #476 `_v5` floors declare `prompt_tokens` in the decode identity unit (fd0b08db)

Worktree: /Users/edr/code/JouleWise-wt-dd5-flidrev, detached at fd0b08db (parent main 784d12f1). Diff: `git diff 784d12f1 fd0b08db`. Finding it fixes: `/Users/edr/night-archive/desk-day-v5/clone-proof/REPORT.md` F1. Non-author reviewer, EXECUTING lens.

Check: (1) the declaration matches what every floor decode config carries (generate both floors with the issued pin from `git show origin/desk/2026-10-04-v5-pin-and-packs:configs/campaigns/d117_contrast_v5/prefill_pin/<file>` for the three bundle files into a /tmp clone, then inspect); (2) no science config byte changes vs the floors generated at 784d12f1 with the same pin (diff the trees: only declaration-bearing files should differ); (3) the new test fails with the field removed; (4) `/Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-flidrev/pc tests/test_d117_floor_qwen3_v5_generate.py tests/test_identity_pins.py`. (The identity projection itself needs Metal, unavailable in your sandbox; the lead ran it: PASS for both floors.)

Verdict line first: `REVIEW: PASS` or `REVIEW: FAIL`, then findings with severity and evidence.

WRITE_SCOPE: []
Scratch: /tmp/dd5-flidrev/ only. No background processes. Finish in this turn.
