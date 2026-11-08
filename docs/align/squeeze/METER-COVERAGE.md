# KM003C coverage audit

2026-11-08 brief; static code audit on `align/2026-11-08-v5-meter-audit`.
**No live coverage is certified. No sealed outcomes, real measurement files,
external directories, model weights or network were accessed.** “Wired” below
means the code starts a collector, not that a usable stream exists for a night.

## Authority and snapshots

Ed's task brief overrides older proposals: v4 keeps its frozen configuration,
settings and thermal policy, adding capture in every window and sealed full
transcripts only. v5 is an add-on using eligible v4 calibration windows,
`m >= 39` per pair, per-channel maximum thresholds, a separate test cohort and
physical positive controls. This audit changes no fit, threshold, cohort,
eligibility rule, model setting or thermal policy, and scores no transcript.

The meter is between the USB-C brick and MagSafe cable. It measures all power
entering through that connection, **DC input, excluding the brick's AC loss**.
Battery discharge/charge is separate: `P_battery = -B0AC*B0AV/1e6` W. Retain
the meter integral independently; add the signed battery term only when it is
available. SMC `PDTR` is a cross-check, not a substitute for KM003C. The
whole-member integral is the authority for small effects; GPU turn ownership
alone cannot cover CPU tools, holds or gaps.

Only existing local Git refs were used; no fetch (standing no-network rule).
Reproduce another-branch source with `git show <snapshot>:<path>`.

| Snapshot | Commit |
|---|---|
| This lane's W1/R10 base; `origin/lane/2026-11-08-v5-squeeze` | `d600baba029f70592bb8e792098338e4cd6811d3` |
| `origin/main` (including RUN_STATE items 202–210; analysis/recompute code) | `32ba4928573ce1981f8a953ab700f00dda9e94d1` |
| `origin/interp/2026-11-07-integrated` | `3c8ce8a5a9918695d1413c12e69b41836fa0d1dd` |
| `origin/align/2026-11-07-squeeze-analysis` | `5af6bafea8d6593066a2f5152ad6e7b3c349d83f` |
| Squeeze-design synthesis | `a832f4993c4f35f333634884b5905768078b8085` |
| Reviewer-2 synthesis | `f01e47f295f36b5f77c06dd2d788bcaf88ff7f21` |
| V4-registration synthesis | `eea648b09933bce93d49cef3a8e7da11ab88e18b` |
| Tripwire directions | `028a705292461646c2cfcbe18b74f4c4a9b0a3ed` |
| Original squeeze-prereg draft | `688d14b6eba63544fee5c60dcb850cdb7caf3813` |

Read alongside this clone's `docs/align/pilot_protocol_v4.md` and
`docs/align/energy_residual.md`. Older review proposals that modify v4 or permit
monitor scoring before registration are superseded by the task brief.

## Coverage by route

Paths refer to this lane unless a different snapshot is named. Rows group
entry points sharing one acquisition/reduction route; metadata, blinding and
pure planning utilities do not independently measure energy.

| Path / entry points | Captured? | Analysed? | Gap and disposition |
|---|---|---|---|
| `scripts/km003c_monitor.py`; `joulewise/external/km003c_usb.py` | Explicit invocation only; 50 SPS default, plain QoS, RAW/MONO clock pairs, SMC battery/PDTR, create-once stream | Collector only | Exit 0 with an `absent` header is intentional. Process success is insufficient proof of capture. Lead must inspect header, samples, coverage, trailer and stop proof. |
| `joulewise/external/km003c_parse.py` | Consumes supplied stream | Yes: unwrap, clock fit, gross/baseline meter and battery integrals, `rho`, `meter.*` flags | Diagnostic API; `delta_machine_energy` falls back to meter-only delta when battery is absent. Do not reinterpret that fallback as complete machine energy. New ALIGN join keeps machine values null in this case. No parser constants changed. |
| `scripts/run_night.py` HAZARD_PACK → `joulewise/b5/driver.py:production_seams/run_hazard_night` | **Wired**: supervised reader, `hazards/meter/stream-NNN.jsonl`, `night/meter_supervision.jsonl`, final digests; orphan cleanup in run_night | Structure/supervision only here | Reader readiness is never awaited; absent/failed capture discloses and collection continues. A mandatory capture-readiness/coverage receipt is still needed for prospective v4/v5. Do not retrofit sealed B5 driver policy. |
| `joulewise/b5/harvest.py:meter_joins`; `scripts/harvest_b5_window.py`, `scripts/harvest_b6_session.py` | Archives existing custody through the shared harvest | Yes: controller request against own idle baseline; `withheld/meter.json`, rail delta, machine delta, `rho`, meter flags | Numerical cross-check only; not a registered small-effect endpoint. Request must fit one aligned stream. It checks request extent, but does not require baseline extent or reject in-span dropped samples before integrating. Flags do not repair missing support. Larger prospective qualification work, L2 below. |
| ALIGN v4 W1/D session: `scripts/align_v4_session.py` → `align_pilot_session.py` → `bytes_h_session.py` → `b5.plan.write_window_plan` | **Wired through HAZARD_PACK**, not through a second ALIGN reader | Previously rail-only PILOT desk; **fixed here** to join harvested whole-request DC/battery beside rails | The broad review claim “no KM003C launch in ALIGN” misses this inherited path. Verify the actual plan/driver revision and stream at arm. No extra sampler should be added to these members. DC residual fitting and registration remain L1. |
| Older ALIGN pilot session/kit (`scripts/align_pilot_session.py`, `align_pilot_kit.py`) | Same HAZARD_PACK inheritance when using this session route | Existing rail attribution/residuals; new diagnostic DC join also applies | Older records with no meter remain explicitly unavailable. `harvest=False` or a failed harvest does not reuse a possibly stale meter record. Historical pilot data are not promoted to registration-grade calibration. |
| `scripts/align_v4_thermal_desk.py`; `joulewise/align/apple/thermal_desk.py` | Analysis only | **Fixed here**: optional explicit harvested `meter_record` in manifest; gross DC, signed battery, machine total printed adjacent to existing GPU tables | No discovery or raw-stream refit. Optional `meter_run_id` maps a bundle ID to the harvest run ID. Missing record is visible. Meter flags are labelled `not_supplied` in this portable route; use the session desk/raw flags for qualification. U1–U6 and rail verdicts remain unchanged. |
| `joulewise/align/apple/pilot_analysis.py`; `joulewise/align/energy_residual.py` | No acquisition | GPU rail residual in pilot path; general numerical API can accept another channel but does not load one | Whole-request DC is now visible, but **no DC fit or squeeze detector is implemented** by this change. Need separately qualified training/whole-member uncertainty and frozen per-channel calibration; L1. Duration must not become an explanatory regressor. |
| Standalone ALIGN Apple runtime/campaign (`apple/pilot.py`, `campaign.py`, `sampler.py`, `endpoint.py`, `workload.py`) | Powermetrics into episode/bundle; no KM003C collector of its own | `align/attribution.py` integrates recorded traces, not external custody | Safe only for universal capture coverage when wrapped by an audited outer collector. Direct CLI use lacks that guarantee. Bind meter stream and trusted whole-request span in the future wrapper, L3. |
| R0: `scripts/align_r0_checks.py`, `align_r0_dispositions.py`; `joulewise/align/r0_runner.py`, `r0_step.py`, `r0_mlx.py` | No dedicated meter reader/join; SMC thermal/census and runtime checks | No DC-energy desk endpoint | A quiet-guard allowlist entry for `km003c_monitor.py` is permission to coexist, not collection. Standalone R0 needs an outer collector plus per-segment boundary mapping, L3. Do not alter R0 results or inspect its real output here. |
| R1: `scripts/align_r1_rehearsal.py`, `align_r1_runtime.py`, `night_chains/align_r1_rehearsal.zsh`; `apple/r1_runtime.py` | No dedicated reader in these entry points. Inheritance is conditional on the **outer plan** being HAZARD_PACK | Rail/decode/turn-owned energy, battery state/drain; no R1 meter desk join | The chain says run_night supplies the plan but does not establish its receipt class. Ordinary run_night use alone is insufficient. Lead verifies outer plan/custody; if needed, an independently controlled sidecar and segment-to-stream join. **R1 lane untouched**; L3. |
| ALIGN budget pilot `joulewise/align/budget/apple/run.py`; SSD study `scripts/align_ssd_qualification.py`, `align_ssd_fixed_decode.py`; operator rail probe | Native rail capture or operator-supplied powermetrics; no meter wiring found | Rail/power/timing diagnostics, no DC endpoint | Qualification measurements also need meter capture and matching segment integrals under the universal instruction. SSD study explicitly takes a continuous PM capture; add continuous KM003C alongside it and preserve paired segment bounds, L3. |
| Squeeze simulator `align/squeeze/{residual,detection,power,adversary,__main__}.py` on squeeze-analysis snapshot | **No**: synthetic planning only | Simulated whole-episode DC quantities; no measurement reader | The documentation's trusted-DC assumption is not an acquisition implementation. Need L1 raw/custody adapter before using real v5 episodes. Keep simulation labelled synthetic. Positive-control executed work must remain inside the registered integral. |
| BYTES kits/session and B6 loop: `scripts/bytes_mac_kit.py`, `bytes_h_session.py`, `joulewise/b6/{plan_inputs,driver_lane}.py` | **Wired through HAZARD_PACK** for the production window route | Harvest meter record plus BYTES reducer below | Confirm meter readiness and every science/reference member's support; do not infer success from a kit lacking a direct `km003c` string. Native BYTES streaming probe `bytes_stream_test.py` itself is a workload/timing tool, not an energy collector. |
| BYTES `scripts/bytes_analyze.py`, `joulewise/bytes_analysis.py` | Analysis only; archive `sources/night-custody/hazards/meter` | Yes after release: rails, `DC input`, and `rest = DC input - rails`; gross/idle-subtracted; signed battery and boundary terms | `--stage blinded` deliberately emits rails only; preserve the blinding gate. `meter_decode` checks both span extents and decode drops, but not dropped samples in the idle baseline; assess baseline-drop qualification prospectively (L2), especially for idle-subtracted secondary. Never run on study data here. |
| BYTES independent `scripts/bytes_twin.py` | Analysis only | Independent meter parse/fit, per-run joins, DC/rest/battery/bounds and comparator quantities | Not evidence of equality without an authorized synthetic/native comparison. Check baseline-drop treatment together with production, not by changing only one implementation. No BYTES estimator changed here. |
| Block 5 `scripts/run_b5_analysis.py`, `joulewise/b5_analysis/disclosures.py` on main snapshot | Consumes immutable archived capture | Yes: disclosure lines per member/window for machine delta, rail delta, `rho`, flags and battery availability | Descriptive cross-check, not a DC claim estimator. Legacy meter-only fallback can remain numeric with `battery_term_available=False`; consumers must retain that distinction. **Sealed code and pipeline untouched/unexecuted.** Any change needs lead custody/registration handling. |
| B5 independent `scripts/independent_recompute_b5.py` on main | Raw archive streams; no capture launch | Yes: independent meter parse/clock fit, request delta+battery; gross phase meter energy and gross rail share | Phase battery correction is explicitly not applied: request-level battery activity is flagged. Phase/gross shares are not request/delta `rho`. Compressed-only streams may be unavailable in this independent route. All are disclosed, not repaired on sealed data. |
| B5 comparator `scripts/compare_b5_recompute.py` on main | Reads analysis, recompute and explicitly supplied harvest records | Yes: `compare_machine`; meter J/W, machine J, rho, counts and edges; `--harvest-meter PACK=PATH` | When a meter line is compared, its source record and meter-family bars are required. No comparison was run; do not claim release equality. |
| Block 6 harvest/export/analysis: `scripts/harvest_b6_session.py`, `b6/{session,export_runs,analysis_lane}.py` | Shared B5 driver and harvest capture/archive | Meter cross-check in archive; generic `AnalysisLane.precision_reached` returns `None` | B6 export is a blinding/replication interface, not a DC analysis implementation. BYTES has its separate consumer above. Future general B6 claims need a frozen DC consumer beside rails, L1/L2. |
| Interp P ladder `interp_energy/rail_data_dependence.py`, `capture_hooks.py` on interp snapshot | Optional `--execute --km003c`; reader readiness checked when requested | Raw stream + slot/idle stamps only, no DC reduction | Native execution permits capture disabled or rail-only. Both collectors must be requested for energy experiments; no measured DC reduction exists yet. `parents[2]` correctly resolves to repo root; no path fix is needed. Module absent from this base, not imported piecemeal here. |
| Interp fixed-token T `scripts/interp_energy/forced_decode.py`, `interp_energy/forced_decode.py` on interp snapshot | Timing/logits only; no collector CLI | No measured-energy reducer | Must wrap authorized native replay with both collectors and trusted whole-member/slot boundaries. Tiny synthetic replay is not physical validation. L4. |
| Interp `behaviour_channel.py`, `power.py`, `lockin.py`; behaviour/power-analysis CLIs | None (predictions/simulation) | Count-based energy predictions or synthetic interval-power analysis | These APIs do not qualify a real DC stream; `lockin` sample-rate capability is not meter acquisition. Build explicit rail/DC readers before measured lock-in or weight-edit energy claims, L4. |
| Core `controller.py`, telemetry adapters `powermetrics.py`, `nvidia_smi.py`, node worker; `reduce.py`, `scored_reduce.py`, `analysis_engine` | Configured platform sensor; no native KM003C backend | Registered platform channels only | Generic direct runs and remote nodes do not inherit HAZARD_PACK capture. Distinguish full-host DC from GPU/NVML/INA3221 rails. A meter on the Mac cannot cover a remote accelerator. L5; no new adapter/contract introduced here. |
| Calibration/floor/reference campaigns; `calibration_*`, `extract_detection_floors.py`, floor mint tools | Outer HAZARD_PACK capture if used; standalone sampler/capture route has no universal meter requirement | Existing registered rail calibration/floors; shared harvest DC cross-check only | Do not reinterpret the rail calibration or replace its authority with a new DC floor. Future small-effect DC claims require their own calibrated uncertainty and per-channel thresholds. Preserve immutable run bundles and all sealed pins; L2/L5. |
| Doctor, T0/arm/instrument readiness and quiet-predicate probes | No full meter measurement route | Readiness/OS/rail evidence only | These are not scientific energy measurements and their success must never serve as meter coverage. If used as an energy experiment, use the same prospective capture/analysis wrapper. |

## Small fixes landed on this branch

`joulewise/align/apple/meter_desk.py` reads **one explicit harvested record**,
checks its schema, retains its exact SHA-256 and joins by member/run ID.
It reports raw DC gross/delta, signed battery gross, corrected machine
gross/delta, rail delta, request/baseline RAW bounds, stream/offset provenance
and supplied meter flags. Missing/nonfinite evidence remains null with reasons.
No raw stream, bundle, model/config path or measurement is discovered by it.

The session desk automatically consumes the successful harvest's
`archive/withheld/meter.json`, even when an episode summary is unreadable.
It emits `dc_input` on each member and a `whole_request_dc_input` console table.
A skipped/failed harvest cannot silently reuse a stale meter record. The
portable thermal desk accepts, for example, this **synthetic manifest shape**:

```json
{
  "meter_record": "archive/withheld/meter.json",
  "members": [{"bundle": "runs/member-1", "meter_run_id": "member-1", "window": "W1"}]
}
```

This is descriptive reporting, not a new detector. A controller request spans
gates/holds/tool gaps **inside that request**. It does not automatically cover
model loading, idle baseline, process startup or work outside sampling stamps.
Do not sum turn cuts and call the sum this integral. The thermal desk labels
meter flags `not supplied`; the session desk carries member/window meter flags
when the harvest flag record exists. Neither desk certifies meter qualification.

## Lead work, in priority order

1. **L1 — Registered v5 DC consumer.** Bind every calibration/test/PC member
   to an independently qualified whole-request meter integral and matching
   logged-work prediction. Retain raw DC and signed battery separately, own
   uncertainty labels, flags and exact trusted boundaries. Freeze the v5
   DC/monitor rules before scoring, use eligible v4 calibration without
   changing its configuration, require `m >= 39` and maximum thresholds, and
   keep held-out T windows separate. Existing simulator or new desk print
   cannot supply this gate. No v4 DC residual refit was added here.
2. **L2 — Prospective coverage qualification.** Require successful streaming
   readiness, full request **and baseline** support, stop/trailer/clock-pair
   stability, restart/drop disclosure, complete battery support and PDTR
   agreement before a small-effect DC result. Record missing/invalid capture
   as unavailable, not zero. The current driver deliberately continues on
   absence and harvest can average incomplete baseline support. Register
   consequences prospectively; never silently modify sealed B5 code or
   re-harvest outcomes. Audit BYTES production/twin baseline drops together.
3. **L3 — R0/R1 and standalone qualification capture/joins.** Verify the exact
   outer R1 receipt class and capture artifact before claiming inheritance.
   Run a sidecar only when an inherited collector is absent; two readers
   must not contend for the same USB meter. Map each R0/R1/SSD/budget segment
   to its trusted RAW/MONO bounds and analyse DC beside rails. No edits were
   made on `lane/2026-11-06-v4-r1-integrated` or to R1 runtime/kit files.
4. **L4 — Interp integration.** On `origin/interp/2026-11-07-integrated`,
   require capture for native energy experiments, join slot/idle/whole-member
   stamps to both sensors, preserve
   battery/uncertainty/flags and add synthetic independent integrals. Forced
   replay and behaviour predictions currently have no measured DC analysis.
5. **L5 — Other launchers and language.** Inventory each future direct,
   calibration and remote launch against an explicit collector wrapper;
   “every measurement” is not enforced by the generic controller today.
   Keep generic AC-wall-meter contracts distinct from this USB-C DC meter.
   `external/__init__.py`, the parser/driver/harvest and older registrations
   describe a diagnostic “never a claim number”; prospective v5 qualification
   must name the new authority without retroactively changing B5 registration.

## Verification limits and native handoff

The added tests create synthetic harvested records and mocked/temporary bundle
inputs only. They cover missing records/members, malformed/nonfinite numbers,
signed charging, missing battery fallback, exact source digests, thermal CLI
plumbing, an unreadable episode, meter flags and stale-archive avoidance.
Existing thermal/pilot test modules exercise the unchanged rail checks/fits.
See `fanout/meter-audit.md` for commands/results.

No native MLX/Metal, libusb or powermetrics test was run, and no physical
coverage, agreement, floor or sensitivity is established. In a clean,
lead-controlled quiet session, verify reader readiness and complete custody
over a synthetic-workload window, compare DC/PDTR/rails on identical trusted
bounds, include a signed battery interval, and exercise reader loss/restart.
On the integrated interp branch, run `tests.interp_energy.test_capture_hooks`
when extending its capture/analysis contract, then the native tiny-workload capture
outside an active agent session. Do not use sealed Block-5 data for any of
these checks and do not download weights.
