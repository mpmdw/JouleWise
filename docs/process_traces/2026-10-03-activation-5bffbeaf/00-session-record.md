# Activation 5bffbeaf (Opus 5.5, headless magistrate), 2026-10-03 from 16:29 PDT

## Launch state

- Watchdog notice pending: `transition-1575-hold_census` ("production census non-empty inside
  plan span"), epoch 1791049978 (11:12:58 PDT). The census row that caused it is the `w2` night
  driver itself (pid 66658, `run_night.py run --plan .../d117-g2a-prefill-probe-20261003T1748Z/night_plan.json`).
  The hold lasted until 1791057807 (13:23 PDT), after the chain exited. That is the watchdog keeping the
  magistrate off the machine during the window, as designed. It is not a fault.
- `w2` = plan `d117-g2a-prefill-probe-20261003T1748Z`, t0 1791049680. Night log: gate GO 11:12:38;
  result GO 12:58:55 with chain exit 1; courier sent 13:00. Courier report: p512 5/5 ok, p1024 5/5 ok,
  p2048 r01/r02 ok, r03 FAILED (exit 3, `unknown_error`), the rest never ran.

## Owner instruction (unread Gmail from Ed, message `1a103f859387e353`, thread `1a1035a2f6cc5b34`, 22:52Z)

Ed's words, verbatim, replying to the courier report:

> keep working, if you the courier can't do those things pass the to do list to
> the magistrate and get work going again

Applied: this activation is the magistrate taking the courier's to-do list (harvest, uninstall,
records, next step by verdict).

## Harvest (recipe §6), 16:31 PDT

- `scripts/harvest_g2a_window.py` from the clone at H (`1d6b5668`), archive
  `~/night-archive/harvest-d117-g2a-prefill-probe-20261003T1748Z`: **verdict REFUSED**, exit 3,
  cause `summary_regeneration_failed`, members 12/24. `harvest.json` sha256
  `3d88096e879b11b517cb505553a65956b98116858c7a29e42b6c991671a4cad5`.
- Underlying error: `run_provenance_mismatch: g2a-small-p0512-r01: config_sha256`.
- Cause (read from the files): `scripts/summarize_g2a_prefill_probe.py::_run_provenance` requires
  `runs/<id>/config.json` to be byte-identical to the input config under `prefill-probe-configs/`.
  The runner re-serializes the config with its schema defaults filled in (`host`, `link_speed_mbps`,
  `notes`, `ambient_temp_c`, `dataset_ref`, `prompt_tokens` added as null), so the bytes differ
  (input `e99d78a4…f8`, run copy `3ed56079…49`, which `metadata.json.config_sha256` also records).
  `w1` produced no runs, so this path first met real data in `w2`. Tooling fault → R3.
- Night agents uninstalled (`install_night_agent.sh --uninstall`, rc 0); no `com.joulewise.night*`
  label or plist remains. Canonical root fast-forwarded to `e256ac28`.

## Next

R3 fix on branch `fix/2026-10-03-g2a-w2-summary-config-provenance` (Sol 6.1 seat), gates, merge; then
re-harvest into a fresh root (`-r2`), then recipe §7 by verdict.
