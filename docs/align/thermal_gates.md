# ALIGN Stage 3 thermal gates and desk support

**PROVISIONAL: synthetic verification only.** Authority is FINAL-DESIGN §§1(c–e),
2.4–2.6 and B5/B6/B9 on `origin/lane/2026-11-05-align-window-council`.
The pinned controller, monitor, MLX runtime and SMC reader remain unchanged.
This layer imports the merged 1 Hz journal/SMC transport and token-budget work.
It does not register, size, arm or run a measurement window.

## Configuration and launch contract

`EpisodeSpec.thermal` opts in; unset fields are omitted from serialized specs,
identities and output. The required `warmup_condition: "benign"` gives both
conditions the same warmup prompt. An example with **synthetic** sensor keys:

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
medians from 60 successful one-second slots immediately preceding warmup.
Kit v4 must persist that reference and source span in window custody and carry
it unchanged to subsequent members. Each member has a fresh process; this
module does not discover or mutate shared window custody. Omitting the
reference in later members would incorrectly create another reference.

The v4 launcher passes `registry=ThermalRegistry()` from
`joulewise.align.apple.thermal` to the existing controller `run_benchmark`.
It binds this runtime to the actual telemetry adapter regardless of resolution
order. `PowermetricsStatus` reads complete frames incrementally from that
adapter's current capture and reads the existing OS notify bus. It launches
no sampler or subprocess. A launcher can instead inject a status callback,
or atomically publish `{os_level, pm_state, monotonic_ns}` to the bundle-local
`outputs/align_thermal_status.json` (read only while at most 2 seconds old).
No path stored in an episode spec is followed. The ordinary v3 runner does
not select this registry: kit v4 must wire it explicitly.

## Runtime behavior

The in-process sidecar starts during prepare, before load/idle/warmup, and
stops at cleanup. It samples at 1 Hz and writes `outputs/align_thermal.jsonl`:
paired epoch/monotonic brackets, decoded native values and types, per-key
errors, observed OS/PM state, and gate events. The existing window monitor's
`temperature.jsonl` remains usable as independent desk evidence.

- G0 is after neutral warmup and before the episode stamp. Ten consecutive
  samples must satisfy both one-sided upper temperature bands, slow-sensor
  OLS slope over the preceding 60 seconds within ±0.2 °C/min, OS level 0 and
  the last PM state Nominal. Its cap is 600 seconds; timeout flags and proceeds.
- G1 precedes chat on every admitted turn after turn 0. Five consecutive
  samples must satisfy bands referenced to that episode's G0 release values.
  The reference never changes after a turn. Cap is the configured R1 value,
  at most 300 seconds; timeout stops without dispatching the next chat.
- Heavy cells hold at each fixed chunk count before dispatching another
  stream step, except after a final token or the per-turn cap. Before hold
  entry, suspended native generator arrays (including nested lookahead) are
  evaluated and the native generation stream explicitly synchronized. A native
  generator whose stream cannot be identified refuses the hold path. This drain is still owned model
  work. The hold uses G1's fixed reference and cap. Failure stops decoding
  and prevents tool execution from an incomplete completion.
- More than 10% failed/missing sensor slots in the 60-second evaluation
  window latches a timed wait and `thermal.state_unobserved`: 300 seconds
  for G0, or G_turn for G1/H. G0 proceeds; G1/H stop. No guessed sensor
  value or nominal status substitutes for an absent observation.

The whole-turn token admission budget is unchanged; cooling consumes no
decode tokens and never shortens an admitted turn's cap. The deadman remains
**episode wall time**, as explicitly required in §2.2. G0 precedes that
clock. G1/H consume it. No model-call timer survives into a hold; its own
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

`thermal_desk.member_record` recomputes coverage from either journal form.
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
  inconclusive; observed divergence is X5.
- U4: unweighted window means, W−1 df, point bar ±0.25%, 90% interval within
  ±0.5%. The four-anchor, K≥3 branch uses the balanced crossed-anchor moment
  estimator: `sigma_w²=max(0,(MS_window-MS_interaction)/4)` and the 6 J bar.
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
clock and temperature arm differences. Heavy cells always retain G1/H.

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
