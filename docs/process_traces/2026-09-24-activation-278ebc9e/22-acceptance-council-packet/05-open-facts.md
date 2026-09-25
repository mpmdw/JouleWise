# Open facts and citation spot-checks

## Unresolved facts, with the next evidence required

1. **Native cadence cause:** the 19 September raw plist shows long `elapsed_ns` intervals with frame parity, but has no independent arrival timestamps. A matched 50/100/200 ms, sampler-set, output-path and hook matrix with arrival stamps can separate some mechanisms; binary-versus-OS attribution needs a compatible old signed binary and/or an approved alternate OS boot. The proposed probe is sudo-enabled and agent-free. [docs/process_traces/2026-09-19-activation-a743be05/06-consult-instrument-cadence-astra.md:5-9,28,30-50]
2. **Future valid yield at 0.245 s:** 11/24 valid in the two equivalence nights; subsequent `qpe01` pilots measure idle power, not 59-pulse calibration detectability. A prospective pulse-validation capture is needed to learn whether altered pulse duration/margin or stable conditions raise yield. [docs/process_traces/2026-09-19-activation-d0b83820/01-n2-20260919-harvest-record.md:71-87; docs/process_traces/2026-09-19-activation-a743be05/06-consult-instrument-cadence-astra.md:54-62]
3. **Successor screen and joule bar:** no issued 25G83 corpus yields a new max, range, SD or Q99. The old ~1 J attribution example and ~5 J clearable effect cannot be carried over numerically or multiplied by cadence; actual edge powers, timing bounds and floor/claim formulas must be reduced from prospective data. [configs/calibration/preregistration_d079_epoch_25g83_rev1.md:190-259; docs/decision_log.md:4758-4814]
4. **Acceptance rule change:** the existing three-day registration was frozen before the two nights, and Ed ruled those nights out. Whether a shorter/different registration retains sufficient coverage and prevents false admission needs an explicit pre-capture scientific rule and the council's desk simulations, not retrospective inclusion disguised as prospective. [configs/calibration/preregistration_d079_epoch_25g83_rev1.md:143-190; docs/process_traces/2026-09-19-activation-a743be05/01-ed-ruling-fail-route-c.md:9-14; docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md:32-36]
5. **Diagnostic science night timing:** rails/USB-C calibration requires a new registered payload, meter alignment and battery/reader controls. The council placed it after G2-a but did not verify G2-a readiness; a prior critical-path scout identified live acceptance as a blocker. [docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md:18-24,50-54; docs/process_traces/2026-09-24-activation-278ebc9e/20b-acceptance-critical-path-report.md:68-90]
6. **Prior-set handling:** the live ledger contains valid 25G83 observations from the two ruled-out equivalence sessions. The present registration says a valid same-epoch observation outside its registered corpus refuses issuance, while Ed says neither night counts. A replacement registration/issuer transaction must explicitly reconcile that prior set without quietly absorbing already-read outcomes. [configs/calibration/preregistration_d079_epoch_25g83_rev1.md:156-163,253-259; docs/process_traces/2026-09-19-activation-a743be05/01-ed-ruling-fail-route-c.md:9-14]

## Ten `sed -n` source spot-checks

Run from the repository root. The **tail** column reproduces a short exact excerpt from each command's inspected lines; these are citation checks, not new measurements.

| # | Command | Stable observed tail |
|---|---|---|
| 1 | `sed -n '20,26p' configs/calibration/calibration_acceptance_d079_v2_n17_r7.json` | `"os_build": "25F84",` / `"sampling_interval_ms": 100,` / `"pulse_protocol_id": "powermetrics_pulse_fiducial_v3"` |
| 2 | `sed -n '143,147p' configs/calibration/preregistration_d079_epoch_25g83_rev1.md` | `Sample. Three agent-free [QUIET-MAC] windows on distinct calendar days, DIAGNOSTIC_NO_PACK class` |
| 3 | `sed -n '173,177p' configs/calibration/preregistration_d079_epoch_25g83_rev1.md` | `Retained n >= 19 is REQUIRED for` / `No top-ups, retries, early stops, or outcome-driven extra nights.` |
| 4 | `sed -n '188,190p' configs/calibration/preregistration_d079_epoch_25g83_rev1.md` | `If two or more retained members exceed 0.032898493715362, the corpus is not issued and Ed rules in` |
| 5 | `sed -n '24,25p' docs/process_traces/2026-09-19-activation-d0b83820/01-n2-20260919-harvest-record.md` | `d01, d03, d05, d07, d09, d11, d12` / `ordinary-invalid` |
| 6 | `sed -n '9,14p' docs/process_traces/2026-09-19-activation-a743be05/01-ed-ruling-fail-route-c.md` | `neither night counts toward the three-night derivation` / `resolve the instrument` |
| 7 | `sed -n '15,19p' docs/process_traces/2026-09-19-activation-a743be05/06-consult-instrument-cadence-astra.md` | `d01|871|110.4/244.3/274.0/284.5` / `d05|855|113.4/247.7/274.2/299.1` |
| 8 | `sed -n '234,237p' docs/process_traces/2026-09-22-activation-22666c9f/01-qpe01-pilot-n1-20260922-0217-harvest-record.md` | `2,535 frames in` / `interval of ~237 ms` |
| 9 | `sed -n '424,434p' scripts/validate_powermetrics_fiducial.py` | `if identity_epoch is not None and identity_epoch not in judged_epochs:` / `"acceptance_artifact_epoch_mismatch",` |
| 10 | `sed -n '2572,2579p' joulewise/calibration_bracketing.py` | `allowance = max(drift_decimal, screen)` / `operative_bound = endpoint_max_decimal + allowance` |
