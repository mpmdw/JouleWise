# ALIGN SMC thermal tool — 2026-11-05

Original PR #658: `lane/2026-11-05-align-smc-thermal`, implementation
`274fec2cb`, initial report `5202533f2`; base `c9a0a3943`.
Fix branch: `fix/2026-11-05-pr-658`, cut from `5202533f2`.
The original implementation was **REJECTED**. Its placement, selection and
hardware-enumeration claims are superseded by this fix round.

## Fix round

Authority: `docs/align/council-2026-11-05/FINAL-DESIGN.md` §2.6, §2.8 B4/B5
and V8 on `origin/lane/2026-11-05-align-window-council`, read with `git show`
from the authorized shared Git store at
`6eb1ff5be31bec330ae5af262c2b4c7601e7755e`. This clone has no local ref for
that council branch. Amendment 1 was absent from that origin ref and all
reachable history in the shared store. A request for its commit/text is
pending. The user's explicit ruling is applied: window 1 is Qwen3.8-27B
only, Qwen3-Next is dropped, Flash-Next is later. No model/roster code was
changed here; no other amendment clauses are claimed verified.

Read the complete executing review `/private/tmp/jwsol/rev-658.json` first.
It contains nine findings and no refuted notes. The user reports all
BLOCKER/HIGH findings independently confirmed. The original deviations were:
little-endian #KEY, amplitude/noise ranking, tau<30 / tau>120 classes, 90%
coverage, R0-generated policy picks, and a custody hazard/policy sidecar in
pinned modules. All are removed from the current implementation.

| Finding (review order) | Severity | Commit / disposition |
|---|---|---|
| F1 #KEY is big-endian on Apple Silicon | BLOCKER | `efb8ed7c0`: ALIGN-local decoder; observed `00 00 08 6e` → 2,158, complete fake index walk, normal integer byte order unchanged. |
| F2 flat idle wins amplitude/noise ranking | HIGH | `ef5cefcc5`: physical ΔT ranking, >=0.05 °C/quantum quality floor, stale idle rejection; flat/near-constant/one-degree regressions. |
| F3 selection/R0 pinning differs from §2.6 | HIGH | `ef5cefcc5`: R1-only classification, independent model-free heating t63/cooling τ, inclusive 5 s / 3 °C / 300 s boundaries, <1% errors; R0 picks null and no policy snippet. `a49849cc0` keeps τ referenced to the first observed cooling value when initial reads are missing. |
| F4 sidecar/decoders in pinned hazard/policy code | HIGH | `efb8ed7c0`: all five core modules restored to base bytes; sidecar/reader/R0 helpers moved under `align/apple`; optional ALIGN slot; prepare→cleanup collection to `outputs/align_thermal.jsonl`. |
| F5 caller-phase/partial-slot coverage errors | MEDIUM | `1749185ee`: sampling-grid ticks with 100 ms tolerance, partial edge exclusion, actual maximum intervals including edges; jitter/gate-span/gap regressions. |
| F6 quiet check misses CPU contention, modes, absent custody | MEDIUM | `f780c1f4a`: reuse contention process/host deltas outside own tree, fail closed, refuse missing parents, preserve periodic evidence and before/after power/OS thermal probes. `bf3a240b8` keeps periodic probes off sample deadlines (300 ms census-cost regression). |
| F7 unsupported ioft temperature keys | MEDIUM | `efb8ed7c0`: observed bytes `99 99 27 00 00 00 00 00` → ~39.6 °C, align-local signed little-endian 16.16. Unsupported types retained separately; summary coverage in `ef5cefcc5`. |
| F8 worker EPERM masks readiness / wrong import cwd | LOW | `c5c713070`: re-poll exiting groups, direct owned-child fallback, preserve primary failure with cleanup note, explicit checkout cwd. Fake lifecycle regressions plus opt-in native tests. |
| F9 overstated report/PR body and test status | LOW | Corrected here and in `docs/align/smc_temperature.md`; replacement offline PR body in `2026-11-05-align-smc-thermal-pr-body.md`. Generated summaries now cite the council authority; regression added. Remote PR body was not edited because network is forbidden. |

F1/F4/F7 form one coupled decoder/placement commit: restoring smc.py while
adding correct decoders requires the ALIGN-local reader. F2/F3 form one
selection-rule commit. Each code group has a regression observed failing
before its fix and passing afterward; no review finding is waived.

### Regression evidence

All commands use `JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest`, one
module/case at a time. No pytest, full discovery, block-5 analysis pipeline,
network, live SMC/CPU/power probe or native MLX execution was run.

Before-fix reproductions:

- `tests.hazards.test_smc_enumeration.EnumerationTests`: four failures after
  replacing fake #KEY with real big-endian bytes; includes wrong 1,846,018,048
  count and missing ioft decoder.
- `tests.align.test_thermal_sidecar`: four errors before the ALIGN slot and
  sidecar existed. A byte-hash regression additionally pins the restored
  five core modules to their pre-PR bytes.
- `tests.align.test_smc_selection`: two failures/five errors before the R1
  rule/default-R0 separation; the old selection chose TCHS over THEA.
- `tests.align.test_thermal_coverage`: three test methods, 50 failing and
  19 erroring subcases before the grid/interval fix. These replay 8/30/60 ms
  jitter across episode phases and short gate windows.
- `tests.align.test_smc_quiet`: four methods/five errors before host admission
  and metadata seams existed. Later extended with unavailable-probe evidence.
- `tests.align.test_smc_gpu`: four errors before the cleanup/import fix.
- `tests.align.test_smc_selection.SelectionTests.test_r0_emits_no_sensor_classification_or_policy`:
  failed before the generated report cited the binding design.

Final targeted results (each command suffix below is a separate sequential
unittest invocation with the prefix above):

| Module / case suffix | Result |
|---|---|
| `tests.hazards.test_smc_enumeration` | 15 tests PASS; includes the cadence follow-up. |
| `tests.align.test_smc_selection` | 9 tests PASS. |
| `tests.align.test_thermal_coverage` | 3 tests PASS, including the phase/jitter matrix. |
| `tests.align.test_thermal_sidecar` | 6 tests PASS. |
| `tests.align.test_smc_quiet` | 5 tests PASS. |
| `tests.align.test_smc_gpu` | 4 tests PASS. |
| `tests.hazards.test_temperature` | 8 tests PASS. |
| `tests.hazards.test_smc` | 12 tests, PASS with 2 skips (platform/live guards). |
| `tests.align.test_apple_campaign` | 12 tests PASS, 71.442 s. |
| `tests.hazards.test_monitor` | 36 tests, PASS with 1 skip, 17.168 s. |
| `tests.hazards.test_monitor_p2` | 6 tests PASS. |
| `tests.test_schemas` | 43 tests, PASS with 1 skip. |
| `tests.test_b5_driver_p2.SupervisionTests.test_the_production_monitor_config_names_the_chain_start_record_as_a_tree_root` | 1 test PASS. |
| `tests.align.test_smc_native` | Native SMC class skipped by synthetic-only gate; native GPU case skipped by MLX importability. No native execution. |
| `tests.test_b5_driver` | 48 tests completed, **FAIL: 28 failing assertions/subcases**, 333.898 s. |
| `tests.hazards.test_import_graph` | 6 tests, **FAIL: 1** dynamic arm/monitor case (`NULL` vs `GO`); five static checks PASS, 2.571 s. |

Additional commands: `python3.13 -B -m compileall -q joulewise tests
scripts/align_smc_enumerate.py`, `python3.13 -B
scripts/align_smc_enumerate.py --help`, and `git diff --check` all PASS.
Protected-path and restored-core byte comparisons PASS. Cumulative actual
test runtime was under 10 minutes; no tests ran concurrently. Python 3.11
was not exercised. Native checks are skipped, never passed by simulation.

The cooling-reference follow-up first rejected a valid 299 s heatsink after
five allowed missing initial recovery reads (<1%); `a49849cc0` now measures
τ relative to the same first observed value used to set its 1/e target.
The corresponding single test failed before and the full module passes after.

The cadence regression first reported only 0.2727 coverage for a 300 ms
periodic census cost; `bf3a240b8` now passes with twelve one-Hz samples and
full coverage. It prevents the new CPU/census probes from manufacturing the
very gaps the coverage metric is meant to detect.

**Current integration limitations:** driver failures include `night_chain_alive`
(exit 6 after a zero-returning synthetic chain), unproved dead-man signaling,
and disk-stop expectations. The driver, its test module and fake-window
fixture are byte-identical to `c9a0a3943`. An explicit read-only
`/bin/ps -p 4432 -o pid=,lstart=,command=` was denied with `operation not
permitted`. This establishes the unavailable process-census capability; it
does not prove every failure has that single cause. The dynamic import-graph
case's precise reason for `NULL` was not isolated. The full modules must be
replayed in the lead's normal process-capable environment; no green
integration claim is made here.

The driver emitted ResourceWarnings for synthetic FAKE_MONITOR children,
whose source sleeps for a bounded 600 s. Reported PIDs were 97948, 98102,
98336, 98465, 98660, 99130, 99558, 158, 398, 694, 836, 1030, 1230, 1449,
1975, 2198, 2322, 2464, 2491, 2721, 2820, 2936, 3016, 3313, 3695, 3994,
4312 and 4432. Their final exits could not be verified because ps is denied.
No blind PID/group signal was sent: the long analysis job must not be
mistaken for a reused test PID. The lead may verify/clean up only surviving
synthetic test children, or allow their fixed sleeps to expire.

### Compatibility for PR #666

Full API/migration table: [`smc_temperature.md`](../align/smc_temperature.md).
The existing `hazards.temperature` / `hazards.smc_enumeration` imports alias
the single ALIGN implementations. Existing sampling/coverage function names
and signatures remain, with additive raw evidence and coverage fields.
`rank(capture)` is now R0-only; R1 must request `stage="r1"`. The old fit/ratio
fields are retained as null, amplitude now means measured ΔT, and τ is
cooling-only. The default R0 load is 60 s. Coverage gaps now mean actual
sample-free intervals; use `max_interval_ns` for the 2 s bar.

The rejected CampaignPolicy/monitor hooks and `hazards.smc` enumeration API
are removed to obey V8. #666 must use `EpisodeSpec.thermal`, the ALIGN-local
Reader, and the adapter's sidecar. Gates, hold decisions, RuntimeEvent
emission and hold attribution remain #666's responsibility; this fix does
not claim G0/G1/H are implemented. The collector can journal gate/hold
boundaries via `Sidecar.event`. Anchor spec/identity bytes omit unset slots.
No existing campaign policy, pack, raw evidence or run bundle was edited.

### Files touched

- New ALIGN implementations: `joulewise/align/apple/smc_reader.py`,
  `smc_enumeration.py`, `thermal.py`; optional slot/lifecycle integration in
  `workload.py`; CLI in `scripts/align_smc_enumerate.py`.
- Restored core: `joulewise/hazards/smc.py`, `monitor.py`,
  `joulewise/schemas.py`, `joulewise/b5/driver.py`, `harvest.py`.
- Compatibility imports: `joulewise/hazards/smc_enumeration.py`, `temperature.py`.
- New regressions: `tests/align/test_smc_selection.py`, `test_thermal_sidecar.py`,
  `test_thermal_coverage.py`, `test_smc_quiet.py`, `test_smc_gpu.py`,
  `test_smc_native.py`.
- Updated/restored tests: `tests/hazards/test_smc_enumeration.py`,
  `test_temperature.py`, `test_smc.py`, `tests/test_b5_driver.py`,
  `tests/fixtures/b5_plan/fake_window.py`.
- Docs: `docs/align/smc_temperature.md`, this report, and the adjacent
  `2026-11-05-align-smc-thermal-pr-body.md` (offline replacement PR body).

### Scope and safety

Performed Mission M0/intake reads, root AGENTS/CLAUDE conventions,
orchestration, authority map and D-003. No active stop card was present.
Selected this explicit fix brief as [AGENT] work; did not register a task.
No writes to RUN_STATE.md, TASK_QUEUE.md, docs/process/state_kernel.json or
tests/test_gen_state.py. No delegation, external consult, installation,
quiet measurement, commit of data, push or merge. Commits are local only.
Reads were confined to this checkout, authorized temporary files and Git's
explicitly allowed shared repository store. Configured absolute data paths
were treated as text and never followed; no real restricted/ data was read.

### Remaining uncertainty and next exact step

All real thermometry remains **PROVISIONAL**. The review's live laptop
#KEY/ioft evidence is reported as reviewer evidence; this run only replayed
its bytes synthetically. The reviewer also reports `tests.test_b5_driver`
48/48 and `tests.hazards.test_import_graph` 6/6 passing in its environment.
The initial report's blanket sandbox explanation did not establish current
status; this run distinguishes those historical results from its own checks.

The lead must supply Amendment 1's missing commit/text, review the final
local commits, migrate/rebase #666 using the API table, and run the native
module on the Mac15,9 after all agent sessions end:

```sh
JW_B5_SYNTHETIC_ONLY=0 JW_LIVE_HW=1 python3.13 -B -m unittest tests.align.test_smc_native
```

Use the locked interpreter with MLX importable; the native tests are
`NativeSmcTests.test_native_big_endian_count_and_index_inventory` and
`NativeGpuTests.test_native_worker_starts_from_other_directory_and_is_reaped`.
Then perform R0 and the separate R1 planning-turn/coverage/overhead checks.
The quiet check measures CPU outside the tool tree; it has no direct GPU
utilization measurement or exclusivity lease. The 0.05 CPU-s/s aggregate
check and timing overhead need the normal clean-host validation. No thermal
control or scientific acceptance is claimed from these desk tests.
