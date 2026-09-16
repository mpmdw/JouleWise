# 05 — Registration of TEST-CANONICAL-PATH-DEPENDENCY-01 (2026-09-15 ~23:33 PDT, activation `08ca8197`)

Requested by the interactive session `b0ae8462` (cross-session message) from
its quick-suite seat finding, record 16 flag F3 (on main at `623a6c01`).

## Facts re-read by this activation

`grep -rn --include='*.py' '/Users/edr/code/JouleWise\|~/code/JouleWise' tests joulewise`
at main `623a6c01`: 8 files.

Filesystem-reaching (the defect class):
- `tests/test_paper_round7_artifacts.py:43` — `R7F_CORPUS_ROOT` defaults to the canonical checkout.
- `tests/test_admit_model_panel_entry.py:17` — `PYTHON = Path("/Users/edr/code/JouleWise/.venv/bin/python")`.
- `tests/test_rpt001_report_slice.py:36` — `CONTROLLED_RUNS = Path("/Users/edr/code/JouleWise/runs")`.
- `tests/test_floor_extraction.py:3197,4256` — evidence parent / source corpus under the canonical path.
- `tests/test_run_campaign.py:76-77` — canonical campaign logs.

String-asserting (likely allow-list; the seat classifies):
- `tests/test_install_magistrate_watchdog.py:26,94`, `tests/test_arm_readiness_schemas.py:1697,1752`,
  `tests/test_magistrate_watchdog.py:2102` — the literal is asserted as inventory or launcher CONTENT.

## What was registered

Kernel row `TEST-CANONICAL-PATH-DEPENDENCY-01`, rank 211, `p3_hardening_candidates`,
lane `agent`, `queued`. Kernel 184 → 185 rows; `TASK_QUEUE.md` regenerated;
`tests/test_gen_state.py` updated. Registration only; no test changed.
