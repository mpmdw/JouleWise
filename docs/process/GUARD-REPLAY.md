# Guard replay before live admission

Requested by Ed, 2026-11-08. This is an offline engineering qualification
requirement. It changes no guard, registration, scientific exclusion, or live
launch route. D-009 (stdlib core), D-161 (physics and operator mistakes), the
night/Quiet Guard contracts, and the owning lead's rulings remain authoritative.

Any PR that adds or changes a predicate capable of refusing an arm, capture,
member, or run **must include a replay report before that predicate gates a real
run**. This includes changed defaults, matching rules, cadences, aggregation,
missing-data handling, latch/reset logic, and thresholds. The report must run the
actual candidate implementation with injected samplers, compare the previous
implementation, and disclose coverage gaps. A threshold calculation or a test
that copies the predicate is insufficient. No replay report alone grants launch
authority.

The proposed idle false-refusal bound is **5% per declared run length**, not per
sample. Declare the intended duration (R0 example: 23,400 s), cadence, host/OS,
display and power-mode strata, labels and their evidence before evaluating the
candidate. One refusal anywhere in a run counts once. At 5% per whole run the
expected waste is already one attempt in twenty; at 5% per sample a long R0
would almost certainly be lost. A measured benign refusal fraction above this
bound blocks live gating unless the lead records an explicit ruling naming the
guard head, corpus digest, missing coverage, expected lost time and mitigation.
The 5% proposal is for lead acceptance, not an amendment to sealed registrations.

Zero observed failures is not sufficient. For representative, independent,
complete benign runs, require the upper two-sided 95% Wilson endpoint to be
<=5%: zero refusals needs at least **73** such runs. Selected failure incidents,
synthetic fixtures and overlapping windows never establish that qualification.
Missing or unsupported trials must be shown, not counted as passes. Inspect
host/day clusters and serial correlation; the simple binomial interval is
descriptive when independence is unsupported. With insufficient coverage,
collect more traces or obtain a lead ruling. Also include known-contended
positive controls, their true-refusal rate and interval, and every missed hazard;
an always-passing guard cannot qualify by its idle rate. For guards that flag or
redo rather than refuse, state that action and exercise it explicitly.

## Reproduce the delivered reports

No network, model weights, measurement directory or live sampler is needed.
Run from the clone root; output files are review artifacts, never launch inputs.

```sh
python3.13 -B scripts/guard_replay.py list
python3.13 -B scripts/guard_replay.py collect > docs/process/guard_replay/corpus.json
python3.13 -B scripts/guard_replay.py run docs/process/guard_replay/corpus.json --run-seconds 23400 > docs/process/guard_replay/recorded-report.json
python3.13 -B scripts/guard_replay.py run tests/fixtures/guard_replay/synthetic.json --run-seconds 30 > docs/process/guard_replay/synthetic-report.json
python3.13 -B -m unittest tests.test_guard_replay
```

`run --require-qualified` exits 2 unless every adapter has a representative
benign stratum meeting the interval/coverage requirement and no above-bound
benign stratum. This is only an idle
screen: the lead still assesses positive controls, correlation and guard scope.
The delivered corpora intentionally cannot pass that screen. Normal `run` exits
0 on a completed evaluation even when rules are flagged. Adapter errors fail the
command; they are never silently converted to a measured CPU refusal.

Reports bind corpus bytes, implementation/dependency SHA256s, and historical
source commit/blob ids. Historical prewindow/contention dependencies must match
the current executable AST (the pinned contention files differ only in comments);
future executable drift fails evaluation rather than silently mixing versions.
`collect` reads only explicit committed Git blobs; it
never follows a receipt's absolute paths, raw-file locators or model configs.
Numbers in mixed JSON reports remain opaque until selected as a host field.
Only the CPU dictionary after the exact NotQuiet prefix is extracted from
check stdout/stderr; arbitrary check output is discarded. No energy, power,
accuracy, token score or Block-5 analysis output enters these artifacts.

Historical definitions are imported from their original Python ASTs with
injected defaults and samplers; unrelated module/model code is not imported.
The filesystem/agent/custody/LaunchAgent predicates in the CPU adapters are
neutral observations implemented without filesystem access. Consequently these
reports qualify **only the named CPU decision**, never the full census. The
original `QuietGuard.check`, SMC `require_quiet`, `CpuQuietProbe` (for raw counter
traces), `Ruling8Quiet`, `contention.interval/Dwell/judge/span_findings`, display
predicate and thermal judge supply the evaluated logic. Receipt summaries can
replay a decision but cannot revalidate its original sampler.

## Inventory and source pins

Line references below are fixed at main
`dcfa4c59351615cdf3879a0ef68c5800f56f53a7` (**M**), unless marked otherwise.
ALIGN is absent from that main tree: its R0 sources are in the local kit history.
**Q** = `165e1287290794bf4e3854997d2291651c784134` (before #691);
**P** = `5f817856b33f65b269a44ea52811dbbed28d02a8` (before R0-L3);
**L** = `9c40e4e5d9fa453cce3c70984e11fa382b7d4591` (#699);
**K** = `05b6d04cba4868531cc03da187689a3dc187e0eb` (local v4-r11 kit).
For these sources use `git show COMMIT:path`; no checkout is necessary. Source
availability in K does not establish that a draft feature is authorized live.

The inventory covers measurement host-state refusal families and their
arm/runtime consumers. Schema/custody/registration checks are grouped by their
owning validator; it is not a census of every `raise` in analysis code.

| Guard / action | Input and refusing condition | Cadence / source file:line |
|---|---|---|
| R0 QuietGuard, before #691 | Named contaminant in `ps pid,pcpu,args`, decayed `%CPU >5`; any such row latches refusal | 15 s unless forced; Q `joulewise/align/r0_host.py:41`, M `joulewise/prewindow.py:5`, `:10` |
| R0 QuietGuard, #691 before L3 | Cumulative process TIME delta / >=30 s >0.05 CPU-s/s for contaminant matched in ucomm or args; prior over-limit exit evidence carried; latch | 15 s, startup waits for baseline; P `joulewise/align/r0_host.py:98`, `:165`, `:216` |
| R0 QuietGuard, L3 | Same CPU signal is a flag. Invalid/backward monotonic clock, unavailable/malformed process census, missing/invalid custody parents, registered acquisition owner, other agent/measurement chain, installed or loaded night LaunchAgent still refuse and latch | L `joulewise/align/r0_host.py:90`, `:216`; no CPU-refusal threshold now |
| SMC CpuQuietProbe, before #691 | Outside-tree per-process >0.05 **or host aggregate >0.05** CPU-s/s, kernel_task included; failed snapshot/host term unmeasured and refusing via require_quiet | Initial 1 s then since previous snapshot; Q `joulewise/align/apple/smc_enumeration.py:36`, `:84` |
| SMC admission, #691 before L3 | Largest outside process >0.05 CPU-s/s over >=30 s; aggregate diagnostic only. Unmeasured CPU, agent/custody/collector process census still refuses | 5 s supervision, retained >=30 s opening; P `joulewise/align/apple/smc_enumeration.py:87`, `:161` |
| SMC R0-L3 | CPU >0.05 flags; largest **single** outside process excluding kernel_task >=0.5 for union of touching/overlapping heavy intervals >=60 s raises redo; first redo then flag policy. Aggregate and kernel_task recorded only | L `joulewise/align/apple/smc_enumeration.py:227`, `:245`, `:321`; census/unmeasured refusals remain |
| Hazard contention arm | Any outside process (including kernel_task) >0.05; optional registered aggregate bar (default null). Need 180 s clean in 30 s intervals within 2700 s. Cap without READY refuses only if contention actually measured | `joulewise/hazards/contention.py:108`, `:354`, `:562`, `:688` |
| Hazard contention request | Any >0.05 outside process overlapping request; excludes kernel_task in monitor. Coverage hole yields unmeasured finding. A finding is not itself a driver stop | 10 s; `joulewise/hazards/contention.py:733`, `joulewise/hazards/monitor.py:99` |
| Legacy T0 maintenance/dwell | Named `ps %CPU >5`; AC required, repository free >=20 GiB, stale run roots absent. Clean dwell 600 s, every30 s, cap2700 s | `joulewise/prewindow.py:40`, `:113` |
| Night C3 agent census | Shared executable identity matcher; foreign agent or indeterminate census refuses | Arm/T0; `joulewise/night_gate.py:219`, `:991`, `:1775`; `joulewise/agent_identity.py` |
| Night C3 HID | Screensaver idleTime command must succeed and return exactly `0` | `joulewise/night_gate.py:1888` |
| Night C3 power/battery | pmset AC; battery float external-connected true, charging false, abs current <=200 mA, update age<=180 s; malformed/failed read is probe refusal | `joulewise/night_gate.py:1917`, `:1941`; `joulewise/battery_float.py:37`, `:258` |
| Night C3 display/load/thermal | `pmset -g` must contain displaysleep setting (no numeric cutoff here). Legacy 1-min load<=2.0. Every reported CPU_Speed_Limit must equal100; no reported limit is accepted | `joulewise/night_gate.py:1956`, `:1977`, `:2003` |
| Night corecaptured | >2 launches in preceding600 s; at arm the one licensed Wi-Fi cycle has180 s settle; detection-only at T0 | `joulewise/night_gate.py:2035`, `joulewise/corecaptured_loop.py:37` |
| Night non-observer CPU | A named non-observer process >=0.5 busy cores over30 s; v4 uses sealed policy cutoff, ignores load diagnostic | `joulewise/night_gate.py:236`, `:2077`; `joulewise/quiet_admission.py:122`, `:165` |
| Night v4 bind | `max(sum(process CPU),logical CPUs*(1-top idle)) <= busy_core_max`; zero cutoff is non-admitting fixture sentinel. Consecutive samples, bind/post-bind deadlines and boot identity must match sealed policy | `joulewise/quiet_admission.py:38`, `:165`, `:173`; `joulewise/night_gate.py:2252` |
| Night C1/C2/C4/C5 | Registration/chain/checkout identity and plan fields must match owning schemas; plan age<=36 h where applicable, within window; current boot UUID and authenticated ARM deadline must agree. Invalid/missing observations refuse, no estimated thresholds | `joulewise/night_gate.py:1494`, `:1621`, `:1791`, `:2123`, `:2173`, `:2270`; night contracts own version/class branches |
| Campaign environment | AC, external power connected, low-power mode off, all displays asleep, screensaver disengaged, thermal nominal; each enabled critical unknown fails closed | `joulewise/environment.py:43`; defaults `joulewise/schemas.py:434` |
| Controller idle/runtime display | `display_power_state=all_asleep` AND screensaver_engaged=false, including unknowns; HAZARD post-run collector failures can instead be disclosed flags | `joulewise/environment_admission.py:30`, `:54`; consumer `joulewise/controller.py:2198` |
| Controller idle/cooldown | Declared baseline/reference with 5 s subwindows, sustained30 s, >=80% coverage, mean<=reference*(1+0.10) and optional absolute ceiling; thermal nominal/normal; cap300 s and configured abort/skip action | `joulewise/controller.py:3790`, `:3887`, `:4340`; defaults `joulewise/schemas.py:468`, `:516`. **No power trace replay in this blinded task** |
| OS thermal hazard | notify thermal level must be0; arm nonzero refuses, missing is UNMEASURED. Runtime elevated levels/coverage gaps are findings. pmset therm is diagnostic here | 5 s, max gap15 s; `joulewise/hazards/thermal.py:40`, `:128`, `:145` |
| Rich telemetry thermal admission | Non-nominal thermal interval overlapping measured window refuses strict admission; missing coverage cannot certify nominal | `joulewise/environment_admission.py:336`, `:557` |
| Battery hazard | ExternalConnected true, IsCharging false, abs SMC B0AC<=200mA; fallback registry current when SMC unreadable; registry age<=180 s; runtime no publication>120 s and SMC gaps>5 s disclosed | `joulewise/hazards/battery.py:128`, `:423`, `:450`, `:863`; cadence `joulewise/hazards/monitor.py:99` |
| Battery member exclusion | Runtime charging current>+200mA excludes; AC loss/charging state or unread publication state excludes; charge-accumulator mean beyond200mA*Voltage excludes. Discharge alone is disclosed assist, not exclusion; sign-inconsistent discharge accumulator excludes only without covering SMC reads. Publication gap>120 s excludes | `joulewise/hazards/battery.py:863`, `:950`, `:1010`. Accumulator/power evidence was not replayed in this task |
| Disk hazard and runtime stop | Per device arm free>=planned_bytes*copies+20GiB; runtime free<10GiB stops. Unreadable arm disk is UNMEASURED, unreadable runtime disk flagged | `joulewise/hazards/disk.py:37`, `:93`, `:112`; `joulewise/b5/driver.py:1081` |
| Clock hazard | 3.7ms+(abs(f)+0.25ppm)*335 s<=5ms; anchor skew<=1ms, dwell residual<=1ms, runtime step>1ms; boot continuity. Raw clock frequency/anchor inputs only | `joulewise/hazards/clock.py:75`, `:287`, `:357` |
| Instrument cadence | 300 frames within55 s, median<=150ms/max<=200ms; invocation/group termination proved. Failed/unmeasured instrument refuses unlike other hazard modules | `joulewise/hazards/instrument.py:58`, `:143`; `joulewise/hazards/arm.py:87` |
| Hazard arm identity/census | Both agent censuses clean; registered OS/hardware epoch must be admissible; any measured module REFUSE blocks, only instrument UNMEASURED blocks | `joulewise/hazards/arm.py:1`, `:98`, `:209`; NTP-off action and diagnostic collectors do not gate |
| Hazard runtime readiness/outage | Session-start plus successful battery/contention record before launch; 3 readiness attempts with20 s timeout each; battery/contention journal outage>=600 s stops (check10 s). Foreign agent stops; missing agent census retries3 times1 s apart then flags | `joulewise/b5/driver.py:122`, `:1124`, `:1165`, `:1206`, `:1272` |
| Privileged Quiet Guard | Host/boot/schema/registry/lease exact binding, legal actor/state transition, independent census zero and empty registry before quiet_held; exact PID/start/executable/argv/ancestry identity, observable process census; recovery descendants absent | `joulewise/quiet_guard.py:117`, `:483`, `:651`, `:879`, `:1040`, `:1090`; `joulewise/quiet_guard_process.py:302`; contract `docs/contracts/quiet_guard.md:273` enumerates canonical causes |
| R0 launcher | AC required; live magistrate must exit by bounded handoff/deadline; active desk fence blocks second launch. Disk at R0 is report-only. Sleeps display +300 s dwell; failed displaysleepnow recorded, not refused | `scripts/launch_align_r0.py:125`, `:146`, `:161`, `:175`, `:225` (#700 main) |
| R0 disk / W1 disk | R0 reports capacity; W1 free>=80,000,000,000 bytes and configured offloads hash-match their inventories | L `joulewise/align/r0_host.py:379`, `:406` |
| ALIGN thermal G0/G1/H | Selected fast/slow sensors within reference+deltas with continuous fresh samples; G0 needs10 consecutive nominal samples plus abs slow slope<=0.2C/min; G1/H5. Cap G0 default600,max1200 with ruled exceptions, per-turn<=300. Collector/status fault refuses; G1/H timeout/deadman stops; G0 timeout/unobserved state has flag/proceed semantics | K `joulewise/align/apple/thermal_gates.py:23`, `:100`, `:349`, `:503` |
| ALIGN thermal sensor validity | Selected sensor/config/receipt validity, timestamp/coverage rules and fresh reference are required. R0 classifier's candidate rejection is distinct from live thermal gating; provisional picks are not hardware validation | K `joulewise/align/apple/thermal_gates.py:179`, `:264`; L `joulewise/align/apple/smc_enumeration.py:470` |
| ALIGN R1 power/CPU/schedule | PowerModeGuard must read/set/restore requested AC mode; sudo rule and host lock required. Largest outside process>=0.5 for60 s invokes bounded segment redo; configured local batch-window scheduling, G0/precool/deadman checks use sealed runtime contract, not new cutoffs here | K `scripts/align_r1_rehearsal.py:94`, `:157`, `:360`, `:1204`, `:1473`, `:1558`, `:1605` |
| External log volume arm | Default off: **any external mount refuses**. Qualification/active draft: exactly one allowlisted UUID at expected mount, physical external APFS writable, ownership enabled, indexing off, TM excluded, `.fseventsd/no_log` present; malformed/missing census refuses; diskutil retries once | K `joulewise/align/apple/external_volume.py:1`, `:71`, `:183`, `:270`, `:312`; caller K `scripts/align_r1_rehearsal.py:1493`. Activation requires separate adopted amendment/hardware qualification |
| External volume runtime | Device disappears/changes => latched internal routing fallback and loss journal, not a new refusing CPU guard | K `joulewise/align/apple/external_volume.py:376` |

## Committed corpus and the regression proof

`guard_replay/corpus.json` holds host-only projections, source refs and full
commit/blob/SHA256 provenance. There are twelve matching local records refs:
eleven committed `report.json` files yield **552 census/SMC receipt frames**.
The rerun11 ref has NOTE.md but no committed report at its expected path; it is
listed as unavailable, with no filesystem fallback. Refs can move; the committed
report's object ids and corpus digest identify this evaluation exactly.

| Evidence | Available content | Missing / use |
|---|---|---|
| 11-06 first attempt, rerun, rerun2; 11-07 rerun3 through10 | Census time, over-limit pcpu rows; after #691, cumulative-CPU interval/quiet decisions; six CPU-only SMC error dictionaries across the records | Failure-selected, sparse, overlapping checks. No continuous ps counters or complete run-length idle trace. No recorded known-contended positive control independently labelled here |
| Rerun3 / rerun4 | photoanalysisd34% and mdworker6% diagnostic rows | Ed's engineering-benign labels; not independently proven physically idle. No raw TIME deltas with which to remeasure those old bursts |
| Rerun4 SMC | Original1.179 s per-process+aggregate refusal dictionary; aggregate about0.250 CPU-s/s | Can replay the original decision; cannot reconstruct a30 s baseline |
| Rerun8/9/10 SMC | >=30 s CPU intervals: frauddefensed~0.092, WindowServer~0.084 / ControlCenter~0.057, routined~0.052 CPU-s/s | Benign incident labels follow Ed's brief. Display wake/dasd wave timing is not present as a complete raw display trace |
| Fixture monitor journals | Committed FakeMac contention intervals and thermal readings (README `tests/fixtures/b5_harvest/README.md:61`); **125 projected frames**, separate synthetic_fixture stratum | Injected fseventsd/thermal positive control, no live-host accuracy claim. Snapshot raw counters absent from this projection |
| Other battery/corecaptured fixtures | `tests/fixtures/battery_float/`, `tests/fixtures/hazards/battery/`, `tests/fixtures/corecaptured/` exist as committed fixtures | Not imported into this CPU/thermal corpus. Battery files can contain power fields; future work must project state/current only, under its own scope |
| Display/SMC journals | Records retain report CPU diagnostics and at least a rerun7 SMC journal digest; kit code has display-census support | No committed full display-state timeline or raw SMC journal in the inspected R0 record subtree; a digest/absolute locator cannot substitute for samples. No power/temperature outcome journal opened |

General records-tree discovery was confined to the named R0 refs/subtree and
committed fixture paths. Unrelated record families were not traversed for study
data. Missing here means absent from that bounded inventory, not absent from
the measurement Mac or private archive.

The replay counts one stopped attempt per guard, not every census as an
independent Bernoulli trial. All selected incident runs are `complete:false`.
The five benign incident labels were assigned from this brief, independently of
the candidate result; the remaining attempts are `unknown`, not opportunistic
positive/negative examples. Separate synthetic controls provide sensitivity.

| Imported decision | Benign incidents refused / measured | Descriptive95% Wilson | Result |
|---|---:|---:|---|
| pre-#691 QuietGuard | 2/5 =40% | 11.8–76.9% | ABOVE_BOUND: would have flagged photoanalysisd and mdworker rules |
| pre-#691 SMC admission | 1/1 =100% | 20.7–100% | ABOVE_BOUND; original short aggregate-probe receipt only |
| pre-R0-L3 SMC admission | 3/3 =100% | 43.9–100% | ABOVE_BOUND: rerun8/9/10 routine daemon/display/location incidents |
| R0-L3 redo predicate | 0/3 =0% | 0–56.1% | INSUFFICIENT to qualify; those same incidents no longer refuse |

The synthetic report also demonstrates that L3 still requests redo for a
>=0.5-core single-process episode spanning60 s and isolates the old SMC aggregate
failure with low per-process CPU and0.3-core host load. The recorded pre-#691
SMC receipt exceeds both old bars, so it alone does not distinguish their causes.
Separate tests cover overlapping
interval union, gaps, kernel_task exclusion, aggregate-only load, exact threshold
boundaries, insufficient startup baselines, missing evidence, and current hazard
arm READY/cap behavior. No synthetic replay discharges a live/hardware gate.

## Adapter and trace contract

`joulewise.guard_replay` defines `Tape`, `Decision` and `replay`. A corpus has
`schema=joulewise.guard_replay.corpus.v1` and a `runs` list. Each run has a unique
`id`, independent `label` (`benign`, `contended`, `unknown`), `label_basis`,
`stratum`, `complete`, `duration_s`, and time-ordered `frames` with finite `t` in
monotonic seconds. Preserve actual gaps and original identities; never interpolate
clean samples or recycle one window into many nominally independent trials.

Channels used here are `pcpu_busy` (sufficient statistic for the historical
matching CPU predicate only), `quiet_busy`/`quiet_interval` (original measured
receipt), `smc_cpu`/`cpu_era` (original CPU summary), `snapshot` (raw process
counters and optional per-core host ticks), `contention_interval`, `environment`
and `thermal`. Raw snapshot processes require pid, ppid, start identity,
start_epoch_s, command and cumulative cpu_s; snapshot wall_s permits new-process
accounting. See `tests/fixtures/guard_replay/synthetic.json` and synthetic test
builders. The receipt decision adapters intentionally cannot judge every other
channel or reconstruct a missing baseline.

For another guard, add a **trusted repository** `module:function` adapter and
pass `--guard module:function`. It receives a fresh `Tape`; inject its `sample`,
`clock` and `sleep` into the real guard or a memory-only Context. Return
`Decision("PASS"|"REFUSE"|"UNMEASURED"|"UNSUPPORTED", reason, evaluated,
coverage_complete=False)`. Set coverage_complete true only after checking that
the adapter's own channel spans the declared run at the guard's cadence; the
run's complete flag alone is insufficient. The supplied cadence checks allow
10% timing jitter. Supply tighter checks for a guard that needs them.
Use a fresh guard per run so latches reset between independent trials. Only
catch the implementation's expected refusals; an adapter/programming error must
fail evaluation. Plugins are ordinary trusted Python, not a security sandbox:
they must not call live samplers or follow trace paths. Source hashes are
reported. For night_gate, inject its Probes/plan and recorded command outputs;
for battery/external volume inject their runner/exists/stat seams. Never use
real custody directories to satisfy a replay constructor.

The inventory is broader than the built-in adapters. Battery, full night-gate,
external-volume, privileged process identity and ALIGN thermal-session replay
still lack representative committed inputs/adapters. Their absence is a coverage
finding, not an implied passing report. Power-dependent cooldown replay is
explicitly out of this blinded task's read scope.

## Idle-MBP recorder specification (not started here)

The magistrate should commission one unprivileged recorder **between windows**,
after the current analysis job and other agent load have ended. Do not install a
LaunchAgent or begin collection from this task. The recorder observes and writes
an append-only host-state JSONL under a new unrestricted, lead-chosen directory;
it never opens a study bundle, model, custody or restricted directory. It records
boot UUID, OS build, logical CPU count, configured mode, monotonic and wall stamps,
command exit/timeout, actual sample times and its own process identity/cost.

| Schedule | Probe / retained fields | Reason |
|---|---|---|
| Every5 s | One `ps -Ao pid=,ppid=,lstart=,time=,pcpu=,ucomm=,args=`; retain pid/ppid/start/TIME/ucomm, pcpu and contaminant match bits; discard arbitrary args after matching | Matches SMC5 s supervision, retains >=30 s openings; replay15 s QuietGuard,10 s hazard monitoring and30 s arm samples by timestamp selection |
| Every1 s | In-process host CPU ticks, SMC **B0AC only** and monotonic/raw/realtime anchors | Host aggregate/clock and battery-current guards. Never read PDTR/PSTR/PPBR or outcome power keys |
| Every5 s | In-process notify thermal level; `pmset -g batt` state and minimal display/HID/screensaver state via injected native reader or bounded ioreg projection | Captures thermal/display/battery changes; keeps observer work out of measured windows |
| Every30 s | `top -l 2 -s 1 -n 0` host CPU second-sample idle field; record exact sample endpoints | Replays legacy top-based quiet-admission. First top sample is not a valid interval |
| Every60 s and state change | `pmset -g`, `pmset -g therm`, minimal AppleSmartBattery ioreg projection (ExternalConnected,IsCharging,current,UpdateTime), mount/device/free-space identity via statvfs and diskutil/mount only at start/change | Captures policy configuration, battery publication and disk/volume conditions. Strip all PowerTelemetryData/energy/voltage fields before persistence |

Use one process and monotonic deadlines, C locale, no sudo, no system_profiler,
no log streaming, no network and no busy polling. Native probes and command
snapshots must carry before/after stamps; distinguish stale/timeout/error from
nominal. The sampler is an observer tree, excluded only where the real guard
excludes it. Keep its CPU visible in a separate channel. Record the precise
subsampling grid and expected sample gaps for each guard; never stretch a short
interval to30 s. Include display-on/asleep and ordinary idle daemon episodes,
not only hand-picked quiet stretches. An operator schedule and workload diary,
separate from guard output, assigns labels. Known contention is labelled from
an explicit synthetic workload schedule, never from the guard being evaluated.

Proposed cost budget: <=0.01 busy core averaged over30 min, <=64MiB RSS,
target<=128MiB/day with an absolute256MiB/day output cap. Delta-encode unchanged
process rows with periodic full keyframes; lightweight compression/rotation runs
inside that budget. At most one command of each type may be in flight; bound
each command, record missed deadlines, and stop **the recorder itself** on cost,
storage or window-start breach. It must never veto a run or control the existing
analysis job. Flush every30 s rather than fsync every sample. On stop record all
gaps; dropped samples preclude claiming complete coverage.

These are design limits, **not measured costs**. Before always-on use, the lead
must run a model-free30 min overhead check on a clean idle MBP, compare recorder
CPU/RSS/writes with recorder off/on (no power outcomes needed), and adjust or
reject the recorder if it exceeds the budget. Stop it before a real window
unless the registration explicitly includes its load. Long independent traces
can then be sliced once, by a predeclared non-overlapping run-length schedule,
to grow the representative corpus without spending another R0 on a new guard.
