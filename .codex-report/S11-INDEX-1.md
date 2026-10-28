# S11-INDEX-1

Status: IN PROGRESS (milestone 1 of 2: index and test committed; I5 input census pending).

Branch `lane/2026-10-28-b5-window-index`, cut from `lane/2026-10-27-l9-2` at `2b3047d5b`.

- `configs/analysis/b5/analysed_windows.json`: 11 entries (first seal ALPHA a1-a3; second seal ALPHA a1,
  BETA a1-a6, GAMMA a1), loads with `load_window_index` under the real seal pins and sealed pack table.
- `tests/b5_analysis/test_analysed_windows_index.py`: 5 tests; 3 pass in the cloud, 2 skip with a reason.

The full report follows at milestone 2.
