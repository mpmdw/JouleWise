# Record 15 — full sharded replay at `7ea54846` (production code of the render-only fix before the two bench closures; wt-fix-renderonly, untouched during the run), 22:19–23:06 PDT 2026-09-19

`scripts/shard_tests.py --workers 4 --split` (unpiped, `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=$PWD`). Log: `15-full-replay-7ea54846.log.gz`. Exit 0.

| shard | modules | tests | failures | errors | skipped | result |
|---|---|---|---|---|---|---|
| 1 | 60 | 1368 | 0 | 0 | 4 | PASS |
| 2 | 61 | 2349 | 0 | 0 | 85 | PASS |
| 3 | 63 | 1627 | 0 | 0 | 6 | PASS |
| 4 | 62 | 1261 | 0 | 0 | 9 | PASS |

Total 6,605 tests / 246 module runs, all PASS. The final head `0c6626f7` differs from `7ea54846` in `joulewise/night_agent_install.py` (render-only branch + admission records list), `tests/test_night_agent_install.py` and `docs/phase_2/derivation_night_runbook.md`; the five modules that exercise that file were re-run alone at `bbce496f` (record 16, 228 OK) and at `0c6626f7` (record 16b, 228 OK), and the quick tier at `0c6626f7` passed (16c). Terminal review 18's condition is met: **MERGE**.
