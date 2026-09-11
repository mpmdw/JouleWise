# Consult provenance — D-110 re-mint fork (2026-08-06)

- Route: audited CLI bridge `scripts/codex-bridge new`, standalone
  transport (`CODEX_APP_BRIDGE=off` fallback — desktop app IPC socket
  down). Model `gpt-5.6-sol`, effort `xhigh`, service tier `fast` per
  Ed's standing license. Runtime 11m16s. Read-only; tree clean at
  `c537386` before and after.
- Run id `20260806T165843Z-10884-new`; Sol session id
  `019fd803-53df-7841-90c0-2d9525bff75b` (resumable via
  `scripts/codex-bridge resume`).
- Prompt sha256 `b64ad7e5…`, response sha256 `01abaa1f…` (full digests
  in the bridge manifest row); envelope `bridge-report/v1`,
  `status: DISCUSSION`, flags `no_edits, read_only, full_suite_not_run`.
- Launcher (Opus-lane codex subagent) replayed and confirmed: the
  import-exclusion sites (`calibration_bracketing.py:726` + 752/980/
  1051/1322), the enshrining test (`test_calibration_bracketing.py:716`),
  the F1 literal (`mint_floor_artifact.py:91`), the exclusion-origin
  commit (`63f43a6`, via `git log -S is_historical_import`), ledger
  receipt count and cited pre/post attempt ids, and the existence of
  `runs_window_contrast_20260730` + `runs_window_7bfloor_20260729`
  (each with `_bound` sibling).
- Magistrate synthesis and disposition: `SYNTHESIS.md` (same directory).
  Decision is Ed's; no decision-log entry until his ruling.
