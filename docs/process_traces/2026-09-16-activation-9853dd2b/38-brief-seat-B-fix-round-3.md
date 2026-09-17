# Seat B fix round 3 — Opus counter-review F3, F4, F7 (mechanical)

Same worktree `/Users/edr/code/JouleWise-wt-rh-transport`, branch `feat/2026-09-16-reserve-hang-transport`, head `2c6bcfdf`. Same rules: NO git writes; lead commits by pathspec; WRITE_SCOPE in the header; tests as `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest <module>`; bytecode to `/tmp`; no real `launchctl`, `~/night-custody`, measurement roots, network. Counterfactuals: `/tmp` copy restored with `git show 2c6bcfdf:<path>`.

An Opus counter-review of the merged head (read-only: `nl -ba /Users/edr/code/JouleWise-wt-bk-9853dd2b/docs/process_traces/2026-09-16-activation-9853dd2b/36-opus-counter-review-report.md`) found, in your files:

## F3 (SHOULD-FIX) — `PROBE_CODE_PATHS` omits the two programs that do most of the night's custody reading
`joulewise/night_agent_install.py:~631–635` binds only `scripts/reserve_calibration_window_bracket.py`, `joulewise/calibration_ledger.py`, `joulewise/calibration_custody_worker.py`; `scripts/validate_powermetrics_fiducial.py` and `scripts/run_night.py` are unbound, so an UNCOMMITTED edit to either after a successful probe does not invalidate the receipt (a committed one is caught by the measurement-head pin). Add both to `PROBE_CODE_PATHS` (the receipt's `code_digests` are recomputed field by field by `validate_probe_receipt`; the reservation's verify-only receipt line need not echo them — say how the installer-side and receipt-side digest sets are reconciled). Regression: uncommitted one-byte change to each of the two files → install refused naming `code_digests`.

## F4 (SHOULD-FIX) — a spurious second driver fire now plants an authoritative `refusal.json` beside a GO night
`scripts/run_night.py:~1167` `_write_rerun_refusal` now targets `night_dir/"refusal.json"` (was `rerun-<epoch>.refusal.json`); it is reached (`:~1264`, `:~1614`) when `_existing_record` matched, which includes a night whose only records are `receipt.json`/`result.json` with verdict GO; the allocator then creates `refusal.json`, and the amended courier prompt tells the courier to discover all `refusal*.json`, so the morning email reports `night_record_exists` as a refusal for a night that succeeded. Fix: keep a distinct stem for reruns (`rerun.refusal.json`, numbered through the same exclusive-create allocator) AND skip the write entirely when `result.json` exists; make the courier prompt say rerun refusals are informational. Regression: second fire on a GO night → no `refusal.json`, a `rerun.refusal.json` (or nothing, per your choice — state it), result verdict unchanged, courier inventory unchanged.

## F7 (NIT) — `Refused` raised inside `launchd_probe`'s `finally` masks the in-flight exception
`joulewise/night_agent_install.py:~866–894`: a "probe receipt timeout" is replaced by "probe bootout absence unproven". Fail-closed is right; preserve the diagnostic: chain the original (`raise Refused(...) from exc`) and include its message in the refusal text. Regression: timeout followed by a failed bootout proof reports both.

## Verification you must run and paste
Counterfactuals for F3 and F4; `tests.test_run_night tests.test_night_agent_install tests.test_install_night_agent` tails; compileall rc; `git status --short` / `git diff --stat` (only WRITE_SCOPE paths).

Final message: the claude-codex-report/v1 envelope under 8000 bytes.
