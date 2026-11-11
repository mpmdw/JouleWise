# ALIGN Stage 3 thermal gates and desk support

**PROVISIONAL: synthetic verification only.** Authority is FINAL-DESIGN §§1(c–e),
2.4–2.6 and B5/B6/B9 on `origin/lane/2026-11-05-align-window-council`.
The controller, MLX runtime, hazard monitor/SMC reader, b5 driver/harvest and
schemas retain their issued bytes. The five files affected by the rejected
#658 API match pilot-9 `c9a0a3943` exactly. Extra decoders/enumeration live in
`align/apple/smc_reader.py`, over the unchanged core transport/reader.
Collection uses #658's fixed `thermal.Sidecar`; there is no campaign-policy
hook or temperature monitor subclass/launcher.
This layer also imports the merged token-budget work.
It does not register, size, arm or run a measurement window.

## Configuration and launch contract

`EpisodeSpec.thermal` supports #658's sensor-only map
`{s_fast, s_slow, fan_keys, r0_sha256}` for diagnostic collection, or the gate
map below, whose `sensors` member has that same shape. `validate_policy`
validates sensors; `thermal_gates.validate_gate_policy` validates the gate map. Unset fields
are omitted from serialized specs, identities and output. For gates, the
required `warmup_condition: "benign"` gives both conditions the same warmup prompt. An example with **synthetic** sensor keys:

```json
{
  "warmup_condition": "benign",
  "thermal": {
    "sensors": {
      "s_fast": "Tfak", "s_slow": "Tslw", "fan_keys": [],
      "r0_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    },
    "delta_fast_c": 1.0, "delta_slow_c": 1.0,
    "turn_cap_s": 90.0, "per_turn": true, "heavy": true,
    "chunk_tokens": 256,
    "window_reference": {
      "fast_c": 40.0, "slow_c": 40.0,
      "source_member": "window-first-sidecar-member",
      "span_ns": [0, 60000000000]
    }
  }
}
```

These values are examples, **not filled R0/R1 slots**. Kit v4 must supply the
selected keys and R0 byte hash, R1 bands, recovery cap, heavy/light class and
chunk size. Heavy cells require G1 and holds. Light cells can independently
switch G1 for the deciding experiment; G0 is always on for a thermal cell.

The first sidecar member omits `window_reference`. At warmup entry it captures
medians over the true 60-second window immediately preceding warmup,
requiring at least 54 successful one-second slots (90%).
Kit v4 must persist that reference and source span in window custody and carry
it unchanged to subsequent members. Each member has a fresh process; this
module does not discover or mutate shared window custody. Omitting the
reference in later members would incorrectly create another reference.

The v4 launcher passes `registry=ThermalRegistry()` from
`joulewise.align.apple.thermal_gates` to the existing controller `run_benchmark`.
It binds this runtime to the actual telemetry adapter regardless of resolution
order. `PowermetricsStatus` reads complete frames incrementally from that
adapter's current capture and reads the existing OS notify bus. It launches
no sampler or subprocess. A launcher can instead inject a status callback,
or atomically publish `{os_level, pm_state, pm_observed_ns, monotonic_ns}` to the bundle-local
`outputs/align_thermal_status.json` (read only while at most 2 seconds old).
No path stored in an episode spec is followed. The ordinary v3 runner does
not select this registry: kit v4 must wire it explicitly.

## Runtime behavior

The in-process sidecar starts during prepare, before load/idle/warmup, and
stops after native runtime cleanup, including cleanup failure. Failed prepare
closes it immediately. Context-free identity readiness opens no collector;
a measured workload requires one. `thermal_gates.ThermalSession` wraps exactly one
`Sidecar`, consuming locked snapshots rather than creating another reader,
thread or journal. The synthetic-clock seam can operate in memory.

The sidecar samples on absolute 1 Hz deadlines and writes
`outputs/align_thermal.jsonl` in schema `joulewise.align_thermal.v1`:
three-clock started/finished stamps, decoded values, type/raw bytes, per-key
errors, and observed OS/PM status under `values`. Status parsing sits outside
the SMC bracket. `Sidecar.event` records `align_thermal_gate` /
`align_thermal_hold` begin/end boundaries; end rows contain the finalized
interval. Hold ends are published after the next dispatch, preserving the
exact dispatch boundary. Writes flush each row and fsync periodically/on stop.
No journal is added to the pinned window monitor. Explicit external thermal
journals remain usable as independent desk evidence.

- G0 is after neutral warmup and before the episode stamp. Ten consecutive
  samples must satisfy both one-sided upper temperature bands, slow-sensor
  OLS slope over the preceding 60 seconds within ±0.2 °C/min, OS level 0 and
  the last PM state Nominal with its own observation stamp at most 2 seconds
  old. A cached Nominal from a stopped PM sampler cannot release G0.
  Its cap is 600 seconds; timeout flags and proceeds.
- G1 precedes chat on every admitted turn after turn 0. Five consecutive
  samples must satisfy bands referenced to that episode's G0 release values.
  The reference never changes after a turn. Cap is the configured R1 value,
  at most 300 seconds; timeout stops without dispatching the next chat.
- Heavy cells hold at each fixed chunk count before dispatching another
  stream step, except after a final token or the per-turn cap. Before hold
  entry, suspended native generator arrays (including nested lookahead) are
  evaluated and the native generation stream explicitly synchronized. A native
  generator whose stream cannot be identified refuses the hold path. This drain is still owned model
  work. The hold uses G1's fixed reference and cap. Timeout or deadman expiry
  stops decoding and prevents tool execution from an incomplete completion.
- More than 10% failed/missing sensor slots in the 60-second evaluation
  window latches a timed wait and `thermal.state_unobserved`: 300 seconds
  for G0, or G_turn for G1/H. All proceed after this wait with X4; an actual
  timeout or deadman still stops G1/H. No guessed sensor
  value or nominal status substitutes for an absent observation.

Every queued sample is checked toward the consecutive-sample rule. A G1/H
timeout stops model/tool work, but the retained partial transcript is scored
for capability (X2: kept for capability). Its incomplete/excluded labels stay.
Deadman (X7) trajectories retain their previous incomplete, unscored handling.

The whole-turn token admission budget is unchanged; cooling consumes no
decode tokens and never shortens an admitted turn's cap. Thermal members
anchor the R1-derived wall-time slack at **G0 entry**, with zero additional
planned G0 allowance. The deadline is the earlier of episode-start + T_dead
and G0-entry + T_dead; G0, G1 and H all consume it. This conservative bound
prevents a 600-second G0 timeout from adding another full episode budget
outside the member cap. Nonthermal members retain the episode-start clock.
The thermal budget record prints the deadline and origin. No model-call timer survives into a hold; its own
wall-deadline guard bounds the wait and records the exact partial interval
as `deadman`, rather than a thermal timeout. Expiry is an intentional X7,
not a reason to extend the deadline beyond the runner's member cap.

## Attribution and desk

Hardware records retain every gate/hold interval with paired clock brackets,
entry/exit temperatures, slow slopes, reference, outcome, turn and token count.
G0 is before the episode. G1 overlays unowned gaps. H splits decode into
unowned `hold` segments. The original gross total and I3 tiling remain intact;
turn energy and the sum of turn-owned episode energy exclude all holds/gates.
`energy_residual.py` needs no change. Malformed, overlapping, out-of-episode
or misowned intervals refuse attribution.
Native decode phase markers are also split around holds, so the unchanged
reducer receives disjoint phases. Original binary64 epoch boundary values are
retained beside paired integer stamps to avoid re-quantization overlaps.

`thermal_desk.member_record` recomputes coverage from Sidecar or legacy
sample rows, using the collector's grid, 100 ms tolerance and excluded partial
edge cells. It retains bracketing samples and requires actual
`max_interval_ns <= 2e9`; absent bounds cannot pass U1.
Gate releases are always verified against the bundle's `align_thermal.jsonl`,
which records the gate's actual decision sample. An external monitor journal
supplies coverage and independent nearby-temperature cross-checks; its sample
phase need not match the sidecar. Missing decision samples are inconclusive;
observed mismatches fail. The desk integrates the real attribution segments, weights decode clocks
by active time excluding holds, and exports exclusions in the selected meter
trace's clock domain, alongside its mapping uncertainty and paired stamps.
It prints gross episode energy/latency beside turn-owned energy.
The manifest supplies each member's registered sampler-stream
`registered_span_ns`; the OS journal is clipped to that span for primary X1.
Absent span binding makes U1 inconclusive. A nonzero reading elsewhere in a
window's journal must not exclude every member in that window.

`thermal_desk` provides U1–U6 support with pass/fail/inconclusive:

- U1: nominal OS/PM observations, X1–X4 member count, ≥99% successful slots,
  no SMC gap over 2 seconds, PM gaps through episode and G0, and exact timeout
  counts/rates against turn admissions. U1(a) uses only members with no X1–X4
  exclusion. Excluded members still count once in U1(b), and timeouts still
  count in U1(d); X4 is omitted from coverage/value checks. Protocol v4 must
  state this included-member convention explicitly before registration.
- U2: ≤3 °C G0 slow-sensor range and journal-verified fixed-reference releases,
  using only members with no X1–X4 exclusion. A G0 timeout is not a release.
- U3: every supplied identical-work pair, exact prompt/output IDs, energy bar
  `3*max(2.97, .0011*mean_pair_energy)` and ≤0.5% difference in active-weighted
  decode clock. Per-turn differences are diagnostic. Missing IDs are
  inconclusive; observed divergence is X5 (`excluded`), retained in the
  pair table but omitted from U3. With no eligible pairs, U3 is inconclusive.
- U4: unweighted window means, W−1 df, point bar ±0.25%, 90% interval within
  ±0.5%, **and** the four-anchor, K≥3 balanced crossed-anchor moment
  estimator: `sigma_w²=max(0,(MS_window-MS_interaction)/4)` with the 6 J bar.
  `cross_window` always returns both `sentinels` and `anchors`, combining their
  statuses. `acceptance` requires both parts; a lone status cannot pass U4.
- U5: maximum absolute 90% contrast endpoint scaled by cell/30B energy for
  light cells. Heavy cells fit energy/temperature pair differences through
  the origin, only with observed, eligible, token-identical pairs; multiply
  the β interval bound by observed G0 range. Compare to 0.1×smaller pair s_r.
- U6 consumes frozen-fit benign residuals, never refits the calibration. It
  implements pooled per-turn OLS and the energy-scaled ±1 J/turn bar; the
  early/late comparison uses within-pair chronological episode halves,
  equal pair weighting and Welch uncertainty, with the ±0.37% episode-energy
  bar. This split must be explicitly selected by
  `split_rule="within_pair_episode_order"`; absent selection is inconclusive.
  Temperature/clock correlations are diagnostic only.

The exact early/late unit, weighting/CI convention, balanced-anchor moment
formula and heavy-cell β fit must be frozen by protocol v4; the council names
these quantities but does not fully specify their estimators. These are
explicit implementation conventions, not new registered scientific rulings.
No live result or final control claim is certified here. W1 leaves U4–U6
inconclusive, and hardware-control and monitoring verdicts remain separate.

The deciding experiment requires two eligible pilot-7-token-identical runs
per template/arm. It fits all eight energies to template + arm S + actual
start hours, reports δ and its 90% Student t interval with **4 df**, and applies
the exact 10 J confirmation / 6 J rejection rule. Missing runs or identity
are inconclusive. It prints same-arm U3 pairs and available per-turn energy,
clock and temperature arm differences. Missing/ambiguous clock mappings,
missing clock uncertainty, uncovered duty support, or nonfinite energy
half-widths make the energy evidence ineligible for the contrast and U3.
Unavailable half-widths are exported as null with a reason flag.
Heavy cells always retain G1/H.

The additive `scripts/align_v4_thermal_desk.py` reads an explicit bundle manifest
and writes a new directory containing `PILOT.json` and `THERMAL.md`. It does
not alter the v3 desk. Its CLI leaves U4–U6 inconclusive; the owning frozen-fit
v4 desk calls the library functions with cross-window/residual inputs. The
full B9 frozen-script import, K-session comparison against historical pilots,
kit generator, protocol registration, and R1 driver remain lead integrations.

## Qualification still owed

R0/R1 must supply real sensor choices, reference custody, bands, recovery caps,
heavy classes, N_chunk and safe wall-time sizing. The inherited R0 selector's
old tau/amplitude-noise proposal rule differs from the council's t63/ΔT/τ
rule: do not accept its proposals as filled council slots without reconciliation.
R1 must verify pinned-generator lookahead draining, token identity, resume
transients, device-clock coverage, sidecar overhead and cleanup under load.
No hardware, real meter trace, model mirror or blinded study data was accessed.

## WP14(b) window-reference custody supersession

Every gate-map policy requires exactly one role form: the first member uses
`{"role":"capture"}` and consumers use `{"role":"consume", "source_run_id":
..., "source_config_sha256": ...}`. Inline temperatures are retired. The
capture member exclusively creates `outputs/align_window_reference.json` with
schema `joulewise.align_window_reference.v1`; consumers bind the source config,
sensor policy, canonical record digest, and recomputed source-journal samples.

## R1 operating reference (2026-11-10 supersession)

For R1, accepted step-30b supplies R_op: the existing WP14(b) per-key
60 s pre-warmup median with coverage ≥ 0.9. Its own G0 uses that capture.
Every later R1 G0, precool and sensors-only release uses the fixed
accepted R_op (designed start states retain their R + offset mechanism).
G1 and H keep the episode reference, the temperatures at that member's G0
release, as in W1.
A release before acceptance uses the soak mean. The soak still supplies
settling, spread and the printed per-key R_op minus mean; that difference
has no acceptance threshold. Missing capture coverage still makes the
member incomplete. Reference provenance and custody are described in
[r1_runtime_contract.md](r1_runtime_contract.md).

R1's fast band stays max(1.0 °C, 3 × soak SD); its slow band is
max(S6 = 1.5 °C, 3 × soak SD), with S5's max(1.0 °C, 3 × soak SD)
retained separately and an S6 tuning receipt. The 1.5 °C floor is the
smallest registered 0.5 °C step whose fitted tail release has 1.25 times
headroom inside the existing 1,200 s maximum (ruling §3.2).

All R1 model-member G0 caps are 1,200 s. The sensors-only release keeps
600 s. A-B-A and optional d-4bit now rearm the deadman after G0, like the
steps; gated D runs and X-G retain their deadman at G0 entry and their
existing mechanism with R_op substituted (NR-1 deferred). W1's episode
reference and cap derivation are unchanged.
