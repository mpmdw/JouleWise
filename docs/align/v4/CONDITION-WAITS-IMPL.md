# R16 condition waits: inert implementation and native release gates

**PROVISIONAL. W1 runs today's cool-down. Do not add, copy, generate for
installation, or install any `registration/condition_waits_policy.json` on the
v4 line until the lead has reviewed H1–H7 and a native dry arm passes. This
ban includes `incumbent_shadow` policies.** No policy or enabling ruling is
shipped here. No hardware validation or saved MBP minutes is claimed.

The implementation incorporates the [Opus cold review](condition-waits-impl-opus-review.md)
and v4-r11 `1a2574b49fe86eaffa722fb106d851c8e3e1eebc`. The policy-free path
retains that head's rebuilt next-arm packet, battery-log lists/window journals,
R12/R15 cadence and incumbent native guard. Measured episodes stay batch 1.
No observer runs inside a member. No Block 5 analysis or outcome is an input.

## Mechanical install ban and eventual activation

`scripts/align_v4_session.py:install` checks the ban before kit checks, power
changes, meter probes or installer work. `_arm_and_install` also checks embedded
policies, so omitting the policy file cannot bypass it. The registered native
entry repeats the check against the installed measurement root.

An eventual lead-authored, committed
`configs/campaigns/align_v4/registration/condition_waits_lead_ruling.json` must
have schema `joulewise.align.condition_waits.lead_ruling.v1`, `enabled: true`,
`h1_h7_fixed: true`, `native_dry_arm_passed: true`,
`r18_shadow_exposure_passed: true`, `ruled_by`, the exact `policy_sha256`, a
`native_evidence_sha256`, and qualified `observer_accounting`. There is no
example enabling file to accidentally copy into registration. A future ruling
is a lead authority decision, not something the kit or a fixture can issue.

The lead must check the underlying evidence, including the helper modules
listed as `inert_r16_dependency` in the refusal census. The flags are a wire
format for that ruling, not substitute hardware evidence. Bind the ruling and
its evidence in the prospective registration before installation. Promotion
also needs R18 exposure of the new guards, not just CW-1 replay.

## Native sampling and clocks

`NativeSampler` uses an in-process `StatusReader`: IOKit/CoreFoundation for
battery, aggregate display state and the AC power profile; libproc/CoreGraphics
for screensaver/session state; the existing SMC reader and notify reader for
thermal channels. Framework bindings load only at native start. The old command
reader remains an explicit synthetic injection seam. Boot identity is read once
per sampler. No `ioreg`, `pmset`, `pgrep`, `sysctl`, `mount` or `diskutil` runs
in the 1 Hz production status path. The native contention guard still takes its
own registered 30 s process snapshots.

External-volume census runs once at arm and once at release. The arm observation
is retained as source evidence; it is never re-censused by a sample. Release
checks observe the physical setup again. Raw battery plist text is not repeated
in every trace row. Unknown sources yield stamped unobserved rows and reset
stability; a transient read is retried on the next tick.

`PowerStream` keeps one pre-GO powermetrics process. Intervals advance by the
source sequence's `elapsed_ns`, mapped through a single wall/monotonic anchor.
Native plist dates constrain the first endpoint to censored whole-second
intervals; their intersection allows 100 ppm rate drift. Dates are not matched
to a point with a 0.1 s tolerance. Delivery time never makes delayed power fresh.
This is a pre-GO watts diagnostic, not an energy-attribution clock replacement.
Its subsecond phase uncertainty must be checked in the native stream gate.

When a joint gate is present, `contention.run_dwell` sleeps to the next fixed
tick boundary. Source work uses that tick's budget; overruns skip deadlines and
remain coverage failures. The policy-free scheduler is unchanged. Synthetic
50 ms and 150 ms sample work both release. Disabled-hook quiet/burst/persistent
fixtures compare canonical output byte for byte against the pinned v4-r11
commit, not a moving branch name.

Powermetrics closes before GO. Cleanup snapshots descendants, uses the existing
TERM relay procedure, waits for sudo, then confirms the observed PM identities
are gone even if reparented. A timeout does not SIGKILL sudo and orphan its root
child. An unverifiable condition-mode cleanup prohibits GO. Verify this natively;
the branch has not exercised root process shutdown in the sandbox.

## Battery continuity, floors and fallback

Top-up logs are read/derived once at native arm, including repeated
`battery_logs` and `window_battery_journals`. That evidence must be admissible at
arm time. Each R16 battery read then independently proves fresh AC, >=99%, not
charging, current within +/-200 mA, UpdateTime age 0–180 s, and the OBC-off
attestation. The top-up source and admission timestamp stay immutable. R16's
own stamped float observations carry continuity after the between-window
sampler stops. A measured float break or a gap over 2 s breaks that chain;
there is no timestamp refresh from a stopped log. This source change needs the
lead's prospective note at activation.

Display sleep and quiet acquisition may overlap cool-down. The native adapter
can take an explicit `cooldown_evidence` export containing same-boot raw R16
`rows` and `last_disruptive_ns`; install carries its explicit locator. The
attempt checks brackets/order and continuity through handoff (latest row within
2 s), and uses raw display history rather than a previous PASS. Physical
stability still overlaps this arm's own guard. A wake advances the quiet floor
without making an unchanged earlier owner marker permanently fatal.

**Owner ordering matters:** do heavy cadence/collector/setup work before the
cool-down being handed over, and include every later disruptive operation in
the last-disruptive boundary. Never run an incumbent fixed cool-down and then
start another R16 floor as the condition-mode procedure. If no continuous
handoff exists, or native preparation leaves a gap, the safe fallback acquires
fresh floors at the dwell: at least 300 s, with no claimed overlap saving.
The installed owner must demonstrate the continuous handoff on the MBP before
promotion; the synthetic overlap test is not evidence that the current operator
sequence supplies it.

In `incumbent_shadow`, the band is print-only: missing Q, failed readings, the
band ceiling, stale-GO cleanup and the extra R16 clock re-judgment cannot refuse
or authorize incumbent release. The existing arm still owns its clean run and
2700 s cap. Install requires no R16 preliminary receipt or setup attestation in
this mode (the independent inert-merge ban still applies to every policy).
The standalone preliminary diagnostic terminates at 1800 s as
`shadow_censored` if no incumbent release callback has fired; this censoring
never becomes a new live-arm deadline.

## Receipts, packet rebuild and retry ledger

The preliminary entry is explicit and operator-only:

```sh
python3.13 -B scripts/align_v4_condition_waits.py attempt \
  --policy <frozen-policy.json> --inputs <explicit-native-inputs.json> \
  --output <new-attempt-directory> --window C1 --series-ledger <repo>/series/state.json
```

Never invoke it from an active agent or while another job is measuring. Inputs
name the prepared `attempt_id` (session id), battery-log list, optional window
journals, OBC attestation and optional ambient-check evidence. The runner writes
raw trace, boundary markers, receipt and combined `evidence.json`, retaining
failures. It never starts a measured member or downloads weights.

For condition mode, `condition_waits_ledger` reserves attempts in canonical
`series/state.json`, under `condition_waits_attempts[window]`. The fixed window
identity is `condition_waits_window`; changing session ids or reinstalling does
not reset its count. A reservation with no terminal receipt is unresolved.
After one `not_ready`, the next attempt requires a fresh ambient check binding
that exact receipt; after two, return to the lead. The lead must disposition an
interrupted reservation or any further retry, never silently delete history.
Install checks the committed ledger used by the rebuilt packet; the native arm
checks it again and records its terminal receipt there.

Order: prepare the session; collect the preliminary attempt with that session
id; commit its evidence and updated series ledger; have the lead publish those
sources through the existing workflow; build the next-arm packet; then install.
This branch itself is local only and publishes nothing. `series.quiet` names
the combined evidence; `series.condition_waits_policy` names the frozen policy
through the builder's ordinary committed `{path, sha256}` source descriptor.
The builder's `quiet()` replays it and emits `receipt_sha256`, `policy_sha256`,
`attempt_id`, `boot_id`. Install checks those fields on its **own rebuild**.
The native arm constructs and rechecks a fresh attempt for GO; it does not reuse
the preliminary PASS. No extra sleep follows READY.

Timing markers contain only phase, monotonic_ns, wall_ns. Native-arm markers
use the arm-owned hazards journal; a refused arm never pre-creates
`night/chain-stages.jsonl` and masquerades as collection.

## CW-1, fixed Q, export and observer qualification

Q must be frozen from a separate qualified reference **before CW-1 starts**,
for example R1's final-mode soak. This implements H7 option 2 in the cw-fix
brief. Same-run Q is explicitly refused rather than rewriting the captured band.
Kit generation also checks Q's R1 digest against the actual final `r1_slots.json`
bytes, mode and selected sensors/fans. If R1's soak is in another mode, a
separately authorized reference capture and ruling must precede CW-1. The single
CW-1 is not authorized to bootstrap a new band from its own soak.

The kit keeps its <=7200 s bound, full 1800 s recoveries after both actual pulse
ends, one resident/offline batch-1 D pulse, synthetic finalize stand-in, and the
observed wake/sleep transition. Use `KM003CCapture(python, output)` (or an
explicit supervised equivalent) with `execute_kit(..., meter=...)`. It wraps the
existing `scripts/km003c_monitor.py`, closes the capture on every path, exports
its source hash and aligned DC-in samples. The parser reports DC-in energy and
mean watts as SECONDARY/print-only; Q continues to use powermetrics. Missing DC
capture cannot qualify this characterization. Final meter/accounting errors
retain an inconclusive saved report. Transient source errors remain rows and
are retried, not fatal to the two-hour run.

`export-idle --source r0_rerun11_idle|r1_soak|cw1_soak --evidence <export.json>`
converts explicitly permitted channel exports into `{header, rows}` for guard
replay. The export has an explicit `ended_ns`, stamped `smc` rows (R0/R1
`values.sensors` or `sensors`), `status` rows, power averaging intervals and
native guard intervals. Header clocks select the explicit idle/soak span.
No directory search, interpolation, copied PASS, inferred display state or
invented battery/top-up/setup evidence fills a missing channel. Missing legacy
channels remain unknown and hold; if the historical exports do not establish
them, the lead must rule an additional permitted evidence source, not claim a
zero-hold replay. All three sources must have eligible boundaries and zero holds.

The budget is **strictly <0.005 CPU-s/s**, total observer cost, not Python self
CPU. Use `cpu_total()` (the same SELF + reaped CHILDREN basis as the monitor),
`observer_interval()` for complete outside-tree native process rows including
sub-threshold daemons, and offline `observer-parse --evidence <accounting.json>`.
Include baseline/during intervals, elapsed time, before/after CPU totals and
confirmed child reaping. `observer_accounting` checks storagekitd/
diskarbitrationd activation and new outside-tree processes, binding the evidence
hash. Never count the D or finalize workload as observer CPU: run the dedicated
observer-only diagnostic, including both census boundaries and cleanup.
A bare CPU number or truncated over-limit process list cannot qualify.

## Native gates still owed to the lead

No native gate ran in this sandbox. On an otherwise quiet MBP, with no agent or
blinded job active, the lead must:

1. Compare every in-process status read with the native reference commands;
   validate SMC decoders, fan units, AC-mode mapping, all displays/screensaver,
   battery freshness, power intervals and monotonic/raw/wall continuity.
2. Run observer-only baseline/during/after accounting; prove <0.005 CPU-s/s and
   no observer-induced outside-tree daemon work. Retain complete process rows,
   both boundary censuses, cleanup evidence and source hashes.
3. Run one full 1800 s shadow attempt with continuous real powermetrics output.
4. Demonstrate continuous cooldown handoff, battery-log stop/float continuity,
   one-retry persistence and a native shadow dry arm whose incumbent READY time
   is unchanged, with no surviving observer processes before any launch.
5. Freeze the separate Q, run the one authorized CW-1 with KM003C, replay all
   three permitted idle sources, and satisfy R18 shadow exposure before ruling.

Native MLX/resident D pulse tests must run outside this sandbox with the pinned
stack; no MLX test, weight download, real-data read or measurement was performed
here. Keep the 30–45 min planning turnaround and zero credited minutes until a
measured before/after includes preliminary, install, native-arm and cleanup cost.
