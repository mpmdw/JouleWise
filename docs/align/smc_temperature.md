# ALIGN SMC inventory and in-process thermometry

Binding authority: `docs/align/council-2026-11-05/FINAL-DESIGN.md` §2.6,
§2.8 B4/B5 and V8, on `origin/lane/2026-11-05-align-window-council`.
The fix round read that file at council commit
`6eb1ff5be31bec330ae5af262c2b4c7601e7755e` through Git's authorized shared
object store. `FINAL-DESIGN-AMENDMENT-1.md` was absent from the named ref and
reachable history available to this clone; the lead must supply its commit.
The user's binding amendment summary applies: window 1 is Qwen3.8-27B only;
Qwen3-Next is dropped and Flash-Next is later. This thermometry code selects
no model or window roster.

Hardware validation remains **PROVISIONAL**. No live capture was run in the
fix round. Synthetic regressions use the review's observed bytes, rather
than treating fixtures as hardware validation.

## R0: inventory and step data

After every agent session and measurement chain has ended, the lead can run
this on the Mac15,9, using the existing interpreter with MLX installed:

```sh
# Idle inventory only. This opens the real SMC: never run during agent work.
python3.13 -B scripts/align_smc_enumerate.py \
  --output desk-custody/align-r0-idle-UNIQUE --seconds 60

# R0's 60-second diagnostic load; this does not classify or pin sensors.
python3.13 -B scripts/align_smc_enumerate.py \
  --output desk-custody/align-r0-step-UNIQUE --gpu-step \
  --idle-seconds 300 --load-seconds 60 --recovery-seconds 600
```

R0 uses command 8 to inventory every readable T* and F* key. Fan RPM keys
are F?Ac; other F* keys retain their native values/units. ALIGN's reader in
`joulewise/align/apple/smc_reader.py` subclasses the unchanged hazard Reader
and uses its transport, cache and reconnection seams. Additional decoding
stays local: big-endian `sp78` / `fpe2`, little-endian signed int64 / 65536
for `ioft`, and **big-endian ui32 for #KEY only**. Ordinary integer keys
remain little-endian. The review's `00 00 08 6e` is 2,158 keys; interpreting
it as little-endian gave 1,846,018,048 and prevented enumeration entirely.

`samples.jsonl`, `r0.json` and `summary.md` retain key/type/raw-byte evidence,
values/errors, three clocks, phase bounds, idle/load medians, unsupported
types, journal digest and per-key coverage. Capture completion is not a
thermometry pass: `thermometry_bar` is `PENDING_R1_CLASSIFICATION`.
R0 emits no S_fast/S_slow picks or campaign-policy snippet. Failed captures
return 3 and preserve partial samples; existing output directories refuse.
The load is an explicitly requested, bounded 2048×2048 float32 MLX matmul
child, ready before the load clock starts. The child starts from the checkout
regardless of the caller's directory. Cleanup re-polls exiting groups on
EPERM, reaps children and preserves the primary readiness error.

Admission fails on agents, measurement owners, direct collectors, missing
custody parents or unmeasured/over-limit CPU contention outside the tool's
own process tree. Configure the real custody-parent environment explicitly;
missing directories are never treated as an empty census. A stateful probe
reuses `hazards.contention` snapshots and host ticks. Both per-process and
aggregate outside CPU use the campaign default of 0.05 CPU-s/s. The tool's
own controlled load is a descendant and is excluded. The initial CPU check
measures one second; later checks reuse snapshots. All periodic quiet-check
evidence is retained. Raw `pmset -g`, `-g custom`, `-g batt`, active power
mode fields, AC state and the OS notify thermal level are recorded before
and after capture; unavailable readings remain explicit null/error data.
There is no direct GPU-utilization measurement or GPU exclusivity lease.

## R1: planning-turn classification

R1's actual planning-turn step, rather than the fixed R0 matmul, supplies the
input to `smc_enumeration.rank(capture, stage="r1")`. The default
`rank(capture)` is R0 inventory only and always returns null selections.

- ΔT is the final 10% load median minus the idle median.
- Heating t63 is the first 63.2% rise crossing. Cooling τ is the first
  1/e crossing measured relative to the first observed recovery value/time,
  including when a few initial reads fail. Crossings interpolate
  timestamps between adjacent valid readings; no exponential model is fitted.
- S_fast has the largest ΔT with t63 ≤ 5 s. S_slow has the longest τ among
  keys with ΔT ≥ 3 °C and τ ≤ 300 s. Lexical keys break ties. Keys with
  τ > 300 s are recorded and excluded from gating. RPM/raw F* values never
  enter temperature selection.
- Each phase needs at least five valid samples, ≥99% coverage and **<1%**
  failed reads. Unresolved recovery is not assigned a τ. An idle series with
  fewer than three distinct values is rejected as stale. Noise is a quality
  gate: ΔT must exceed three times max(idle SD, sensor quantum, 0.05 °C).
  The quantum includes the type's resolution and minimum observed idle step.
  Noise ratios never order candidates.

The additional data-quality choices are conservative implementation filters,
not newly registered measurement admission constants. Inspect their retained
reasons and raw traces in R1. A null pick or identical fast/slow pick does
not supply the required distinct die/heatsink pair; do not invent a pin.
Sensor locations, refresh behavior and thermometry acceptance require lead
verification on the Mac15,9. If the design's thermometry bar fails, follow its
IOHID/X4 ruling; this tool does not authorize thermal-control claims.

## Sidecar and the #666 integration contract

`joulewise/align/apple/thermal.py` owns the in-process sidecar. The five
core files modified by the rejected PR (`hazards/smc.py`, `hazards/monitor.py`,
`schemas.py`, `b5/driver.py`, `b5/harvest.py`) are restored byte-for-byte to
PR #658's base `c9a0a3943`. No temperature journal is added to custody hazards,
and no temperature field is added to CampaignPolicy.

The optional ALIGN `EpisodeSpec.thermal` slot has the existing sensor-map
shape `{s_fast, s_slow, fan_keys, r0_sha256}`. Key names come from R1; the
R0 digest is provenance only. The slot is omitted when unset, preserving
anchor spec bytes and legacy identity. When set, the slot is included in
the ALIGN execution identity, and `EpisodeRuntimeAdapter.prepare` starts
`thermal.Sidecar` before native runtime preparation. Cleanup stops it in a
finally block, including runtime cleanup failure; failed preparation closes
it immediately. It therefore covers idle, warmup, gates, episode and holds.

Public surfaces for #666:

| Surface | Contract / migration |
|---|---|
| `thermal.Sidecar(outputs_dir, config, *, reader=None, ctx=None)` | One in-process reader/thread; `start()`, `tick()`, `stop()`; `start(background=False)` is a test seam. Writes create-once `outputs/align_thermal.jsonl`. |
| `Sidecar.readings` | Recent reading rows, deque of 3,600; collector appends concurrently. Gate integration must synchronize any iteration (collector `_lock`) or add an accessor. |
| `Sidecar.event(kind, values)` | Records `align_thermal_gate` or `align_thermal_hold` phase boundaries with timestamps. #666 owns gate decisions, RuntimeEvent emission and attribution. This PR supplies collection, not G0/G1/H algorithms. |
| `thermal.validate_policy`, `keys`, `sample`, `Coverage`, `coverage` | Existing function names and calling signatures preserved. `sample` adds raw/type evidence under `readings`. Validation is of an ALIGN slot, despite the legacy helper name. |
| `hazards.temperature`, `hazards.smc_enumeration` | Compatibility imports of the single ALIGN implementations; no second collector. New code should import `align.apple` directly. |
| `smc_reader.Reader` | Enumeration lives here; `hazards.smc.Reader.enumerate_sensors`, `CMD_GET_KEY_BY_INDEX` and the added hazard decoders are removed to restore pinned code. `read/read_key/close` retain normal signatures, with additive raw metadata. |
| `rank(capture, *, stage="r0")` | Return shape retained; explicit R1 stage now required for selection. `amplitude` aliases measured ΔT, `observed_rise` remains; `t63_s` is added, τ is cooling-only. Retired `fit_r2` and `amplitude_to_noise` are null. |
| Campaign/monitor hooks | Removed: `CampaignPolicy.smc_temperature`, `monitor_temperature_policy`, `monitor.build_config(smc_temperature=...)`, optional hazard journal loading and `harvest.OBSERVATION_KIND["temperature"]`. The new `Monitor.temperature_*`, `fast_tasks` and `journal_names` attributes are also removed. #666 must move any uses to the ALIGN slot/sidecar. |
| R0 CLI | Existing options retained; default load duration is now 60 s. Output schema name retained, with additive host/quality fields; sensor picks are always null. |

The sidecar schema is `joulewise.align_thermal.v1`; R0 retains its existing hazard-shaped diagnostic rows. Every journal row has monotonic, raw-monotonic and epoch stamps. Reading
rows contain sensors, units, per-key type/raw hex/value/error, and aggregate
error text. Writes flush each row and fsync every five seconds and on stop.
Thread/journal failures surface on teardown and remain recorded when writable.

Coverage uses the sampling grid with 100 ms tolerance, unique nominal ticks
and excluded partial edge cells; near-grid boundaries snap within that
same tolerance. Reads crossing a caller's slot boundary remain valid; reads
lasting over one second do not. `max_interval_ns` reports actual consecutive
valid sample intervals including both span edges. `gaps_ns` now contains
actual sample-free intervals exceeding 1.1 s, rather than merged missing
caller-anchored cells. #666 must use `max_interval_ns <= 2e9` for the design's
maximum-gap bar. A span with no complete cells reports a null fraction;
never interpret that as a pass. Constant valid temperatures count for
coverage; rejecting stale idle sensors is a separate R1 classification rule.

## Native checks still required

In a clean, lead-controlled session after agents exit, on the Mac15,9:

```sh
# Use the locked measurement interpreter with MLX available; clear synthetic-only mode.
JW_B5_SYNTHETIC_ONLY=0 JW_LIVE_HW=1 python3.13 -B -m unittest tests.align.test_smc_native
```

This checks native #KEY/enumeration and the real MLX worker's readiness,
checkout import and cleanup. Then run R0 and the separate R1 planning-turn
classification/coverage/overhead checks. Neither native check was executed
in this sandbox. The module gates hardware on explicit opt-in and MLX on
importability; it never attempts a CPU fallback.
