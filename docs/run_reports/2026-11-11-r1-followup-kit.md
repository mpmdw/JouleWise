# R1 follow-up rehearsal kit — 2026-11-11

Status (round 5): **D-1/D-2/D-3 fixed; R1 regressions, static closure and kit reproduction pass; equality passes 5/5 isolated runs. Full night-driver module is red and dynamic closure timed out at the bounded test cap.** Native gates and delta review remain owed. Earlier rounds below are historical; the round-5 section owns this run's results and limitations. No night was armed. Branch `ops/2026-11-11-r1-followup-kit`; local commits are recorded in the round-5 handoff.

## Authority and boundaries

Read RL-59, 61, 64, 72, 74, 75 and 76 verbatim from the specified audit ref; the adopted design items and its replay script from `origin/design/2026-11-11-r1-followup`; the speed toolbox from `origin/main`. Mission M0: no active stop card; this direct, named user assignment overrides the ordinary queue. Coordination files were read for intake and left unchanged, including the kernel and `tests/test_gen_state.py`. No delegation or cross-model consult was used; this is **not** the cold review.

No network, model download, measurement pipeline, MBP access or real custody was used. Tests use the repository's synthetic models, clocks, sensor transports and temporary directories. Full-suite execution was prohibited and was not attempted.

Disclosure: the first Git retrieval of the research-lead decision document was overbroad before being corrected to the seven requested sections. Its output included unrelated Block-5-aware policy/summary text. An initial RUN_STATE header read also printed historical collection summaries. I therefore do not claim blindness to those committed summaries. No Block 5 result artifact or measurement data was opened, and none informed the R1 implementation. Absolute data paths in configuration/authority text were not followed.

## What changed

1. **Order and admission units.** `r1_phase_table.py`, `align_r1_rehearsal.py`, `r1_runtime.py` and the runtime contract implement the adopted sequence. A1/B/A2 capture their own references, then an ordinary 30B member immediately precedes step-D. The pair is one admission/redo unit. The production ordinary member uses the unchanged, already-bound `model_30b` template through the existing CLI launch-lineage verifier. No thermal policy or precool is inserted. Planning +4/+2/+0 consumes R_D; each precool belongs to its planning unit. Bank/spam-a/spam-b and X-G follow with W1's configured idle. Soak releases, step-D precool, G0-only retries and 4-bit are cut.
2. **Condition 13.** `v4_registration.verify_r1_executed_sources` compares the six files (driver, runtime, runtime config, phase table, workload, W1 gate) against the full `executed_commit` named in slots. It is called by registration admission and production R1 startup. The registration test mutates each file, supplies a missing commit, and removes the phase module. `thermal_gates.py` remains byte-identical to `82c14c9ea`. New kit/replay scripts join the strict receipt. No signed receipt was fabricated.
3. **Timeout behavior.** `workload.py` adds an inert-default callback. R1 supplies it through thermal-factory session hooks only for the step kinds. An observed timeout retains the original flags and null episode reference, adds `r1.g0_timeout_run`, runs the quiet/turn and re-arms the deadman. Gated D and X-G retain W1's stop. No turn means the next gated run is explicitly not a D-after-D observation. An unobserved capture skips its consumers; invalid/zero budgets never arm a gated member. DEVIATIONS and the runtime contract contain the per-slot bars. Flagged candidates are refused by `align_v4_kit.py`; they need the research lead's ruling.
4. **Deadline.** The phase subtotal is 58,711.9616 s. Largest unit: 7,563.9952 s. Two whole-unit load redos and two encounters of unit + 5,400 s produce ceiling 99,768 s. Brackets 1,800 s each, close 900 s, harvest 4,500 s give overhead 9,000 s and span 108,768 s. The existing writer formula gives **126,480 s**. Runtime child wall caps bound bracket/harvest work; close and total chain span are checked, and the chain reserves its close allowance when capping child work. The redo quota and encounter quota are enforced. `w1_prequal.py` uses the follow-up floors without changing W1/D's own sizing rules. These are bounds, not a wall-time prediction.
5. **A-B-A bars.** Every leg's release is compared with both other captures' fast and slow bands. B's slow capture must be within 0.5 C of A1–A2's range. Either failure is inconclusive. Automatic used after an inconclusive result is marked provisional; `ac_powermode` is null, so that default cannot become an adopted setting.
6. **Inventory sampler.** A spawned process owns its reader, sampling clock and inventory journal. The parent reads it after stopping it; it does not require the busy model interpreter to service a ticker. Errors and missed cells remain data. Registered classifier arithmetic is unchanged; null picks no longer spuriously count as changed picks. Classifier records now include absolute phase bounds for the temperature-only desk.
7. **Smoke kit.** `align_r1_followup_kit.py smoke --part A` runs the ordinary predecessor and step-D through native capture/G0, with an 1,800 s admission cap and an intentional stop before the turn. Part B runs the admission and continues the same D member for at most another 1,200 s through quiet, step and recovery. Its table retains the classifier record, checks full-phase inventory coverage and prints candidate-key releases at 1.0/1.5 C, deciding condition, and sensitivity to reference +/-0.03 C (an explicit diagnostic perturbation, not an inferred sensor quantum). The smoke refuses source drift and a changed W1 gate. Neither part was run natively here.
8. **Sensors.** One `sensors` policy and `slow_band_floor_c` live in the bound runtime configuration. Default is TV0h/Tf08, floor 1.5 C. Prepare requires the smoke-table digest and research-lead ruling. Outcome 2 rejects an R0-fast slow pick under RL-75 and requires the new-key default floor 1.0 C; outcome 3 requires an explicit authorizing ruling. The night's D classifier must reproduce the selected policy; changed/null/aliased picks remain a hold. A new key does not inherit Tf08's tuning receipt. A further record-only temperature key **cannot be carried by policy data alone**: `thermal.validate_policy` permits only the two roles, fan keys and R0 digest. It was not added, and no gate-module edit was made.
9. **Prepare integration.** `align_r1_followup_kit.prepare_checks(root, config, weight_digest_check=..., runtime_stack_check=...)` is the exact integration point for `ops/2026-11-11-w1-armcheck`. Checks run before source validation or any quiet dwell. The missing default callables refuse; this lane implements neither check. The prepare command produces a reviewable arm-input packet with the exact span/window, chain and source digests; the lead still supplies the ordinary machine/custody night-plan fields through the existing arm procedure. It does not install or arm.
10. **Desk print.** The adopted replay script is brought onto this branch and extended with `--night`, also exposed as the kit's `desk` command. It prints each member's own pre-warmup median beside R_op/R_D and the band margins for G0/G1/H releases. Planning and consumers retain their actual gate bands. No own-reference computation is added to the measured runtime. The ordinary ungated 30B anchor has no thermal journal: its desk row explicitly prints “not captured”, not an invented median. All thermally instrumented members have their own-median rows. Planning’s deliberately disabled fast band prints no fast margin.
11. **Closure.** The dynamic trace was regenerated with the explicitly labelled `--bounded` representative profile in a fresh scratch file, then moved into place (cross-device move, SHA-256 checked). It covers the follow-up driver and a real runtime-child TERM/custody path. The full R1 night remains in default CI and was separately exercised. The full trace profile remains the default; it was interrupted after exceeding the test-time budget and is still owed. No test was removed from default CI by the trace-profile selection. `scripts/test_timings.json` receives inserted lines only.

## Verification

Final command results are recorded below after execution. All commands are targeted unittest modules/classes; no pytest, full discovery or real-data analysis was run.

- Baseline `tests.align.test_r1_inventory`: 14 tests, OK (3.091 s).
- Full driver -> subprocess runtime synthetic night: `python3.13 -B -m unittest tests.align.test_r1_runtime_e2e.DriverRuntimeTests.test_full_rehearsal_through_the_runtime`: 1 test, OK (350.087 s). This exercises all accepted segment directories, runtime custody, native gate code on fake transports, D capture/consumption, schedules, mode changes and final slots. It is not hardware evidence.
- Follow-up focused module: observed timeout dispatch versus W1 default, null reference preservation, complete default bundle equality against the pre-edit adapter, per-slot candidate refusal, A-B-A vetoes, pair/planning redos, sensor-ruling holds, candidate/band/sensitivity table and process coverage under a GIL-holding main thread. The pre-final-prepare-addition module run passed 11 tests in 56.597 s; the additional prepare test passed separately. Native-only descriptor forwarding and final summary holds still need the cold review/native smoke; the full night was not re-run after those small final changes.
- Earlier iterations caught the ordinary member's launch-lineage requirement, nested redo-record serialization, inventory/raw-journal readback mismatch, phase-edge cell accounting and a nondeterministic battery-clock field in the bundle comparison fixture. An early full-night attempt was deliberately interrupted after 249.383 s; it is not a pass. The final full-night pass above replaced it. Two brief accidental test-process overlaps occurred (an early rehearsal run, and the first dynamic-closure attempt); the latter was interrupted and re-run serially. The final mandatory checks were serialized. The requested approximate 20-minute total was exceeded, principally by the broad trace (552.7 s before interruption), bounded trace (185.9 s) and iterative end-to-end runs; this is a process deviation, not a pass of that budget.

## Native work still owed — exact next steps

1. Land/wire the RL-62 weight and RL-73 runtime-stack refuse-only checks at `prepare_checks`. Commit the final runtime configuration; production startup/smoke refuses drift in condition-13 files. Do not fetch any weights.
2. In a clean, lead-controlled, **agent-free** measurement session, follow the ordinary R1 night host/DC-in custody procedure (KM003C capture, AC/battery, agent/volume feeds, Automatic readback/restore). Run Part A at the built commit:

   `python3.13 -B scripts/align_r1_followup_kit.py smoke --part A --output <new-A-dir> --soak-reference <accepted-soak.json>`

   Supply the accepted soak's spread, not a substitute gate reference. Verify native 60 s capture before warmup, W1 verifier acceptance, G0 release <=1,200 s, absence of timeout-run, re-arm evidence, complete meter/host feeds and no orphan SMC/heater/restore resources. A partial smoke is not a pass and must not be extended.
3. Run Part B from a new output directory with `--part B`. This performs a fresh admission and one continuous D capture/quiet/load/recovery member. Inspect full-inventory coverage on **the whole pre-warmup idle**, quiet, load and recovery: >=99% cells, <1% read errors, no two empty consecutive cells. Inspect classifier inputs/outputs unchanged, candidate tables, release sensitivity and stability with/without the borderline reads identified by the research lead. The kit's +/-0.03 C diagnostic does not decide that ruling.
4. Send the smoke D table to the research lead for RL-74/75's ruling; no automatic arm on an R0-fast slow key or unstable/null slow class. Apply the one sensor policy and band to the committed runtime config, with the required deviation if changed. The arm waits. Native MLX/Metal/SMC/KM003C behavior is entirely unvalidated in this sandbox.
5. Cold review the bound edits, including workload's inert default and the process sampler. Repeat affected native smoke if executed bytes change. Prepare the arm packet with the linked ruling/table and integrated checks; construct/validate the ordinary night plan with `programmed_span_s=108768`, `window_max_s=126480` and this chain. Arm no later than the adopted 19:26 PST limit, under the ordinary host gates.
6. After the night, off the measurement Mac: `python3.13 -B scripts/align_r1_followup_kit.py desk --run-dir <copied-run>` and the R1-to-W1 chain. Signing must pass condition 13 against the night commit. Raw journals/custody remain immutable.

## Bound files changed

- `configs/align/v4/r1_runtime.json`
- `configs/campaigns/align_v4/registration/r1_slots.json`
- `docs/align/v4/DEVIATIONS.md`
- `docs/align/v4/dynamic_closure_trace.json`
- `joulewise/align/apple/r1_phase_table.py`
- `joulewise/align/apple/r1_runtime.py`
- `joulewise/align/apple/r1_runtime_contract.py`
- `joulewise/align/apple/v4_registration.py`
- `joulewise/align/apple/workload.py`
- `scripts/align_r1_followup_kit.py`
- `scripts/align_r1_rehearsal.py`
- `scripts/align_r1_thermal_replay.py`
- `scripts/align_v4_dynamic_trace.py`
- `scripts/align_v4_kit.py` Unchanged by construction: `joulewise/align/apple/thermal_gates.py`, the bound 30B member template, registered classifier module, identity pins, weight inventory, coordination state and all raw study evidence.


## Final verification results and limits

- `python3.13 -B scripts/align_v4_dynamic_trace.py --bounded --out <fresh-scratch.json>`: 31 tests in seven representative scenarios, all OK; 174 executed paths, zero unbound and zero non-strict. Scratch SHA-256 after move: `5f5f3c7eb80fafcf5ecf4c5a88b763d43475f26eaf4e97f20acf6b07b2d6ee2f`. This is **not** a successful full-profile trace.
- `python3.13 -B -m unittest tests.align.test_v4_executed_closure`: 6 tests, OK, 36.613 s. Static closure/receipt set and strict bindings pass.
- `python3.13 -B -m unittest tests.align.test_v4_dynamic_closure`: 10 tests, OK, 96.566 s. The fresh minimal child stays inside the committed representative trace; spine/receipt/allowlist checks pass. An earlier overlapping attempt was interrupted and is not a pass.
- `python3.13 -B -m unittest tests.align.test_v4_registration.R1ExecutedSourceTests`: 1 test, OK, 1.955 s. Every condition-13 file mutation, nonexistent commit and missing phase module refuses.
- `python3.13 -B -m unittest tests.align.test_r1_followup.PrepareTests`: 1 test, OK, 0.475 s. Actual prepare packet window equals computed worst case (126480), and mocked weight/stack checks precede source validation. Mocked checks are not native pin validation.
- `python3.13 -B -m unittest tests.test_align_r1_thermal_replay`: 19 tests, OK, 27.174 s. Registered replay/status/coverage/margin logic and consume scenarios on synthetic journals.
- `python3.13 -B -m unittest tests.align.test_r1_followup.ProcessSamplerTests`: 1 test, OK, 13.765 s. Inventory process meets the cell/error/gap bar under a GIL-holding main interpreter in all four labelled phases. Native full-inventory sampling remains owed.
- `python3.13 -B -m unittest tests.align.test_r1_rehearsal`: the last broad iteration ran 76 tests in 26.109 s with three failures and one error. They were stale expectations for the removed 4-bit leg, old redo-record shape, old kit refusal route and old zero-turn timeout fixture; those assertions/fixture were migrated. The whole 76-test module was **not** re-run at the final head because of the budget overrun. The new driver tests passed in the representative trace. The complete `test_v4_kit` and `test_w1_prequal` modules likewise remain for CI/lead verification.
- `python3.13 -B -m compileall -q joulewise tests`, targeted script `py_compile`, `git diff --check`, thermal-gate equality with base, and receipt artifact-name equality: passed. Timing manifest diff is exactly two inserted module lines.

Open questions/uncertainty: no native performance or thermal claim is made; smoke table stability with borderline reads is for the research lead, not a new builder threshold. The prepare output is an arm-input packet, not an installed NightPlan. Full-profile closure regeneration and final-head broader CI remain owed. To regenerate the full profile later, use the same trace script **without** `--bounded`, write to a fresh scratch path, inspect every scenario, then move into place and repeat both closure modules. Do not overwrite a trace in place with the generator. No commit was pushed. The final desk-only unknown-anchor/disabled-fast-band display adjustment, and smoke desk authentication/config/close-cap checks, were inspected and compiled, not re-run through the whole synthetic night. Native smoke still must exercise them, including the new-sensor/incomplete-D proposal path.

## Round 2 — RL-78 (2026-11-11)

This section supersedes round 1's sensor-choice, record-only-key, S6-band and
prepare-integration descriptions. The user explicitly assigned this work on the
existing R1 branch; no coordination-state files or kernel tasks were edited.
No agents were delegated. Native cold review remains independent work.

Read the eight requested rulings verbatim, including RL-78, and the adopted
plan/replay implementation. Intake again initially retrieved the audit log too
broadly; its output included unrelated Block-5-aware policy/summary text before
the read was narrowed to the requested rulings. No measurement artifact, store,
real restricted directory or external account path was opened. I do not claim
blindness to the committed summaries. No network, model download, MBP operation,
B5 analysis, full test discovery or real model identity probe was run.

### Implementation and files

- `r1_runtime.py` implements the unchanged classifier's smoke pair, with only
  RL-78's fixed fallback when the registered slow class is empty: maximum
  registered return time <=300 s, slow noise/rise tests, R0-classified and
  unclamped, excluding the fast key and D-record aliases, without a lower tau
  bound. The second role is labelled **near-die settling check**. The night
  checks the fixed pair's admissibility; it retains the full registered ranking
  as a disclosure and never selects a different winner. Its summary, driver
  slots and kit admission use the confirmation. An inadmissible pair holds the
  result for the research lead; the desk refuses it.
- `thermal.py` adds optional `record_keys` to the existing sidecar, preserving
  the absent-field policy and journal bytes. The collector samples a duplicate
  role key only once. `r1_runtime.json` carries `record_keys: ["Tf08"]`, the
  registered 1.0 C floor and the six R0-classified keys documented in RL-75.
  The gate pair remains a smoke/ruling arm parameter; the shipped R0 pair is
  only a default, not a native selection. If the full native R0/D records name
  additional candidates, the lead must supply the authenticated complete R0
  key list in this bound parameter before preparing the night.
- Every R1 model member carries the recording policy. The ordinary 30B
  predecessor derives a sidecar-only config from the unchanged bound template,
  preserving its ordinary workload and schedule and adding no gate or collector
  process. This is the consequence of RL-78's later every-member instruction.
  The bound template itself is unchanged. The synthetic backend supplies its
  fake clock/transport for this existing sidecar-only path.
- `v4_registration.py` adds `thermal.py` to condition 13. The registration
  mutation test iterates the complete list, including this addition.
  `thermal_gates.py` remains byte-identical to `82c14c9ea`.
- `align_r1_followup_kit.py` fixes the smoke choice once, checks coverage and the
  linked research-lead ruling at prepare, refuses any different policy or
  inherited 1.5 C floor, and prints numeric class-edge margins as disclosures.
  The sampler bar, not class-edge headroom, binds. The cap stays 1,200 s.
- `align_r1_thermal_replay.py` prints Tf08's start excess over the last-60-s
  step-D window reference and per-condition comparisons within this window.
  A start is the G0 exit sample, or measured-run entry for the ungated ordinary
  predecessor, labelled in the output. It reads temperatures, phase stamps and
  the config's condition; it does not open episode results, transcripts or
  rails for this disclosure. Missing/insufficient observations remain null.
- `DEVIATIONS.md` includes the exact RL-78 WP14(a)-R1-SLOW text, retains the
  RL-72 workload-callback row and adds the sidecar record_keys row. The runtime
  contract is updated to the same rules.

### Prepare checks and branch integration

The requested functions share `align_v4_session.py` with substantial arm,
watchdog, privilege and hold changes. A whole-file checkout would import more
than the functions need. I therefore merged the specified armcheck revision
`bcc051881` as permitted, cleanly, in local merge commit `71e970c13`.
The origin tracking refs had advanced beyond the hashes in the brief; the
specified hashes are used to avoid silently widening the requested revisions.

R1 prepare calls the public `weight_digest_preflight` and
`runtime_stack_preflight` APIs before source validation or any dwell. It records
both results as `weight_digests` and `runtime_stack` in the prepare/arm-input
record; either failure writes a refused record and raises their joined reasons.
The prepare record remains an input to the lead's ordinary arm procedure; this
command does not install or arm a NightPlan.

R1's renamed members are explicitly projected to the unchanged registered
inventory rows for the 27B D model, 30B model and NEG-8 1.5B reference. The public
weight function still constructs units with `pilot.h.align_unit_id`; the
projection keeps the registered roots, folded digests and file maps, and the
record names each mapping. It also rejects a template root that differs from
its registered root. The registration inventory is not edited. Production uses
the measurement interpreter (default `<root>/.venv/bin/python`) for the stack
check; tests inject metadata and identity functions and never follow the
absolute model-root strings.

### Verification (round 2)

Results, full-profile trace disposition and final-head module coverage are
recorded below after the serial run. Tests added here use fake host boundaries;
none executes sudo, systemsetup, pmset, launchctl lifecycle commands or
caffeinate for real. No native MLX/Metal result is claimed.

The first broader rehearsal run exposed two stale fixtures: a soak-redo
assertion expected an obsolete retry (the follow-up refuses an unsettled soak),
and the synthetic hardware-label record-shape fixture needed a mocked
source-identity check while sources are edited. Production source validation remains intact and has separate mutation
tests. That initial 76-test run failed (1 failure, 1 error; 19.674 s); it is not
a pass.

Focused round-2 checks so far (Python 3.13, `-B -m unittest`, serialized):

- `tests.align.test_r1_round2`: 13 tests, OK, 9.575 s. Real registered classifier
  outputs feed smoke/fallback and confirmation tests; rejects aliases, noise,
  rise, return-time, clamp and unclassified candidates. Confirms the smoke pair
  despite a different nightly winner. Tests linked ruling/coverage/default
  band, non-binding margins, old/new absent-field journal byte equality,
  journalled Tf08 with instrumented no-gate-access assertions at G0/G1/H,
  policy validation, ordinary sidecar-only predecessor/template identity,
  Tf08 within-window disclosures and desk refusal, W1 kit admission of the
  confirmed pair, public preflight calls over exactly three synthetic identity
  results, stack drift, joined refusals and both recorded check results.
- `tests.align.test_r1_followup`: 12 tests, OK, 43.615 s. Carries forward the
  deadline/admission-unit/redo bars, per-slot timeout restrictions, A-B-A bars,
  loaded-main-thread process sampling in all four phases, and complete member
  bundle equality against the pre-callback workload adapter.
- `tests.align.test_r1_inventory`: 14 tests, OK, 5.990 s. Registered classifier
  arithmetic, full inventory/phase handling, aliases, hashing and cleanup.
- Earlier small iterations of the new module passed 10 tests (1.987 s), then
  12 (2.737 s and a later logged 12-test iteration). They are development checks;
  the complete final results below own the handoff.

### Native checks still owed after round 2

No kit command below was run on the measurement Mac. The next native work is a
clean, lead-controlled, agent-free smoke on the final committed bytes; this
sandbox has no usable Metal/MLX device or CPU fallback.

1. Run smoke Part A with the accepted soak and ordinary host/DC-in custody, in
   <=1,800 s. Verify the ordinary predecessor, native pre-warmup R_D capture,
   W1 `load_window_reference` authentication, release inside 1,200 s, re-arm,
   absence of timeout-run, host mode readback/restore and complete cleanup.
2. Run smoke Part B on a native D step with the full inventory. Check >=99%
   one-second cells per phase, <1% read errors and no two adjacent empty cells
   on **pre-warmup idle, quiet, load and recovery**. Review the unchanged
   registered classification, candidate releases at 1.0/1.5 C, deciding
   conditions, reference sensitivities and numeric class-edge margins. The
   margins decide nothing. Select once by RL-78, including its fallback if
   necessary; no manual key substitution.
3. The research lead reviews that exact table before the arm. Commit one sensor
   parameter set, the authenticated R0-classified key list, Tf08 recording,
   1.0 C floor (with 3 x soak idle SD still applied), and 1,200 s cap. A smoke
   selection on the shipped R0 pair is not assumed to pass. Repeat affected
   native smoke after a cold review changes executed bytes.
4. Run the real weight and installed-stack preflights with the measurement
   interpreter. Confirm exactly the three registered roots and both results in
   the arm-input record, before the ordinary dwell/arm procedure. Synthetic
   identity results in this report are not native pin validation.
5. Native array/stream qualification owed:
   `JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx`.
   It uses tiny arrays, no downloaded weights. The pinned real mlx-lm model
   generator, actual SMC cadence, process scheduling, KM003C and host privilege
   behavior must also pass the ordinary native smoke; none is established here.
6. On the night, the fixed picked keys must remain admissible on step-D. Any
   failure is a lead hold, not a new selection. The desk prints the Tf08 start
   disclosures and within-window comparisons. Signing checks all seven
   condition-13 sources against the full night commit, including `thermal.py`.

### Trace disposition and remaining verification debt

The full profile was attempted without `--bounded`, serially, with an 850 s
subprocess limit. It timed out at **850.101 s**, exit 124. Its first scenario
(`dct_series_window`: 56 tests) completed with `ok: false`; the run then reached
the full clean/injected W1 synthetic windows but did not finish the profile.
No full-profile trace was emitted or committed. The failures are **not yet
attributed**; they must not be called inherited or blamed on this patch without
reproducing them. The preserved diagnostic log is
`/private/tmp/r1-round2-full-jzog_5co/run.log`. The trace runner now prints
individual unittest failure/error details for future diagnosis instead of
silently discarding them.

The fresh bounded run took **349.490 s** and initially passed six scenarios,
with one failure in `ArmOrderWitness`: the armcheck merge now requires
`state.plan_path`, which its synthetic fixture omitted. The fixture now writes
its synthetic plan and supplies that path; watchdog, host commands and installer
remain fake. Only that failed scenario was repeated under the same tracer,
passing in **24.342 s**. Production/source/config bytes were held unchanged;
the retry records their SHA-256s and the original failed trace digest. The artifact after that retry was the union of these actual traces, explicitly
`profile: bounded_representative`, **45 successful tests in seven scenarios**,
181 executed paths, zero unbound and zero non-strict. Its arm scenario preserves
`previous_attempt_ok: false` and the retry marker. No failed test was relabelled
without executing its repaired fixture.

Both original scratch traces/logs were retained; the repaired aggregate was
written with exclusive creation to a new scratch path, then moved into the
canonical path with SHA-256 equality checked. This is a successful bounded
closure trace, **not a successful full-profile run**. All 14 new round-2 tests
are in that run. A separate `tests.align.test_v4_series.ManifestTests` command
passed 8 tests in 11.141 s, narrowing but not resolving the first full-profile
failure.

One brief accidental overlap occurred when the final focused module was still
finishing as the Manifest class started. Both were synthetic and were awaited
before subsequent tests; the trace attempts and remaining checks were serial.
The long full attempt plus the slower-than-round-1 bounded profile exhausted
the approximate 20-minute allowance. Required closure checks take precedence
below; the broader modules listed at the end are left for the Air. This is a
verification/budget limitation, not a claim that the full profile passed.

Smoke Part B now writes `smoke_part_b.json` as the exact table passed to
`prepare --smoke-table`; the ruling binds that file's SHA-256. Its R0 key list
and recorded pair must match prepare's re-derivation, so the arm cannot silently
re-select from a different R0 set. The kit CLI `--help` was also executed to
check script-mode imports.

### Bound files changed in round 2

`configs/align/v4/r1_runtime.json`; `docs/align/v4/DEVIATIONS.md`;
`docs/align/v4/dynamic_closure_trace.json`;
`joulewise/align/apple/r1_runtime.py`; `joulewise/align/apple/thermal.py`;
`joulewise/align/apple/v4_registration.py`;
`scripts/align_r1_followup_kit.py`; `scripts/align_r1_rehearsal.py`;
`scripts/align_r1_thermal_replay.py`; `scripts/align_v4_dynamic_trace.py`;
`scripts/align_v4_kit.py`; and `scripts/align_v4_session.py` (the specified
armcheck merge). The ordinary bound 30B template, registered classifier,
thermal-gate module, model inventory and identity pins are unchanged.

Other files: `docs/align/r1_runtime_contract.md`, this report,
`scripts/test_timings.json` (insertions only), the synthetic R1/W1 backends,
`test_r1_followup.py`, `test_r1_round2.py`, `test_r1_rehearsal.py`, and the
arm-order fixture in `test_v4_next_arm_packet.py`. The armcheck merge's broader
file inventory is visible in merge commit `71e970c13` and its own reports.
Coordination-state files remain untouched.


### Final checks, commits and exact remaining work

- Local commits: `71e970c13` imports the specified armcheck revision;
  `b1faa9376` implements RL-78 and records the initial trace disposition;
  `b40911215` merges the specified `1bca029f7` presign revision. That merge
  conflicted only in DEVIATIONS: all four incoming RL-77 rows were preserved
  byte-for-byte and the R1 rows retained. The final commit containing this
  section carries the last admission witness and fixture correction. Nothing
  was pushed.
- `python3.13 -B -m unittest tests.align.test_v4_executed_closure`: **6 tests,
  OK, 60.718 s**. The presign merge changes documentation only; production
  sources are identical across that merge.
- `python3.13 -B -m unittest tests.align.test_v4_dynamic_closure`: **10 tests,
  OK, 219.862 s**. The canonical representative trace covers the fresh minimal
  child, strict bindings and allowlist/spine checks. This does not turn the
  failed/incomplete full profile into a pass.
- Final review caught the kit still requiring the fixed fast key to be in the
  night's fast-class list even after its admissibility confirmation. Both
  fixed keys now use that confirmation; the legacy checks remain when it is
  absent. The targeted admission regression was re-executed under tracing:
  **1 test, OK, 4.854 s**, added as `r1_fixed_pair_admission`. It checks both
  class lists changing without re-selection and refusal without confirmation.
  AST import/launch edges are unchanged. The full closure modules above were
  not repeated after this predicate-only correction; the final trace's
  scenario/binding invariants were checked directly. The trace now records
  **46 passing tests in eight scenarios**, 181 executed paths, zero unbound
  and non-strict paths, SHA-256
  `ab79f1d2fd1d7f4d774fe494bfc4cea2075fc439338baea023b824c1fa083fe5`.
  The extra witness was again written exclusively to scratch and moved with
  digest equality checked; its source digest is recorded separately from the
  earlier fixture-retry snapshot.
- The two repaired rehearsal cases were re-run together: the evidence-binding
  case passed, but my initial attempt to fix the stale soak assertion by
  supplying an unsettled soak correctly refused (1 failure / 2 tests,
  4.773 s). The final test preserves the settled input and asserts no obsolete
  soak retry. Its separate command
  `python3.13 -B -m unittest tests.align.test_r1_rehearsal.R1Tests.test_quiet_segment_redone_on_sustained_cpu_load`
  passed **1 test in 1.897 s**. The earlier native-label evidence-binding
  success remains synthetic command-boundary evidence, not hardware evidence.
- `python3.13 -B -m unittest tests.align.test_v4_registration.R1ExecutedSourceTests`:
  **1 test, OK, 2.323 s**, including thermal.py mutation via the complete
  condition-13 list.
- `python3.13 -B -m compileall -q joulewise tests`: exit 0. The kit CLI help,
  final diff whitespace check, all four presign-row equalities, gate-module
  equality to `82c14c9ea`, insertion-only timing-manifest diff and untouched
  coordination-state checks passed. No real forbidden host command was added.

The targeted execution total was approximately **27 minutes**, exceeding the
requested approximate 20-minute budget. The full-profile attempt and the much
slower representative trace dominate it. No further broad run was started.
This remains a process/verification limitation and is not presented as a
completed final-head broad test run.

**Next exact step on the Air:** run the first full-profile group as individual
modules, capturing failure details: `tests.align.test_v4_series`,
`tests.align.test_v4_series_e2e`, `tests.align.test_v4_series_r20`, and
`tests.align.test_v4_replacement_windows`. Attribute/fix those failures, then run
`python3.13 -B scripts/align_v4_dynamic_trace.py --out <new-scratch>/trace.json`
without `--bounded`, inspect every scenario, move the successful trace into
place, and repeat both closure modules. Do not overwrite a trace with the
generator. Native smoke/selection/ruling/cold review are still required before
arming, as listed above.

The broader final-head modules were not run in full (some classes/cases were
run as documented). In addition to the changed test modules listed below, the
R1/runtime/thermal/replay follow-through owed is:
`tests.align.test_r1_runtime`, `tests.align.test_r1_runtime_contract`,
`tests.align.test_r1_runtime_e2e`, `tests.align.test_thermal_sidecar`,
`tests.align.test_thermal_gate`, `tests.align.test_thermal_coverage`,
`tests.align.test_thermal_legacy`, `tests.align.test_thermal_desk`, and
`tests.test_align_r1_thermal_replay`. Native `test_thermal_mlx` remains opt-in
on Metal only. The imported armcheck tests need their own final-head module
passes; importing their fixes is not evidence that every module passed here.

Changed test modules needing a complete final-head pass:
- `tests.align.test_harvest_off_review_sol2`
- `tests.align.test_r0_host`
- `tests.align.test_r11_delta4_sol1`
- `tests.align.test_r11_delta4_sol2`
- `tests.align.test_r11_delta5_sol1`
- `tests.align.test_r11_delta5_sol2`
- `tests.align.test_r11_delta_sol1`
- `tests.align.test_r1_followup`
- `tests.align.test_r1_rehearsal`
- `tests.align.test_r1_round2`
- `tests.align.test_r1_round6_power`
- `tests.align.test_timing_receipts`
- `tests.align.test_v4_arm_watchdog_check`
- `tests.align.test_v4_cadence`
- `tests.align.test_v4_kit`
- `tests.align.test_v4_next_arm_packet`
- `tests.align.test_v4_record_binding`
- `tests.align.test_v4_registration`
- `tests.align.test_v4_series`
- `tests.align.test_v4_series_e2e`
- `tests.align.test_w1_prequal`
- `tests.test_w1_reliability_r2`
- `tests.test_w1_reliability_r3`
- `tests.test_w1_reliability_r7`

## Round 3 — Opus cold-review fixes (2026-11-11)

This section supersedes the round-2 implementation/status where it differs.
All work is synthetic and non-claim. Native smoke and a delta review of the
executed-byte changes remain required. No night was armed.

Intake: cold review read first; RL-72, RL-74, RL-76, RL-78 and RL-79 read verbatim
from the specified audit ref. The current branch was already the named branch
at `51b6aeb14`; it was continued there. Mission M0 found no active stop card.
The explicit assignment overrides queue selection. No coordination state,
real custody, restricted directory, model weights or measurement data was opened.
No network, full suite, native MLX, model download or hardware smoke was used.
Historical committed summaries appeared in the initial RUN_STATE intake; no
blindness to those summaries is claimed. Absolute custody paths remained text.

### Finding map

| Finding | Fix and witness |
|---|---|
| F-1 | The old `82c14c9ea` workload adapter and current adapter run the same deterministic tiny member, both released and G0-timeout without a callback. Only the RSS source is fixed: `memory_snapshots[*].process_rss_bytes`, as serialized into `metadata.json` and `events.jsonl`. RSS reflects the shared interpreter's allocator/OS process state. The real RSS reader's availability/error diagnostics are retained. Both adapters use the same injected simulation clocks, including the existing battery-clock seam; timestamp bytes remain compared. No other field, timestamp, telemetry, error, file or byte is excluded or normalized. The same byte comparator rejects a one-byte mutant in every bundle file for both paths. |
| F-2 | Negative cases isolate 98% occupied cells, exactly 1% read errors, and two consecutive empty cells while the other bars pass. Each case is repeated in pre-warmup idle, quiet, load and recovery. Another witness pins exactly those four phases in `smoke_table`. Per-key versus sweep scope is unchanged and parked. |
| F-3 | `Segment.thermometry` is exercised with the night's ranking differing from the configured smoke pair, checking the summary and saved confirmation. An inadmissible configured key produces `r1.sensor_inadmissible` and desk refusal. Every gated D kind and X-G runs through the real reference hook and synthetic member adapter on a timeout: no turn and no `r1.g0_timeout_run`. |
| F-4 | Part B's post-G0 engineering watchdog is derived from quiet + re-armed turn bound + recovery + 120 s classification/close margin (currently 300 + 1,580 + 600 + 120 = 2,600 s). The smoke receipt records these components. A 1,000 s D turn fits; the test checks actual timer installation for three turn bounds. G0 remains 1,200 s. Whether the twenty-minute Part B wording is a hard total bound remains parked, and this watchdog change does not settle it. |
| F-5 | The condition-13 test pins the literal seven paths: R1 driver, `r1_runtime.py`, `r1_runtime.json`, `r1_phase_table.py`, `workload.py`, `thermal.py`, and `thermal_gates.py`. Neither the contract module nor launcher was added. |
| F-6 | Non-synthetic driver startup requires `--prepare-packet` before taking the host lock or running host/runtime commands. It checks schema/status `FOR_LEAD_ARM`, the current executed commit, source hashes, and exact boolean `ok: true` for both `weight_digests` and `runtime_stack`. Named `r1.prepare_packet.*` refusals cover missing, unreadable, stale and not-ok evidence. The arm record carries path, SHA-256, executed commit and both results. The chain requires `ALIGN_R1_PREPARE_PACKET`. Tests cover refusals and positive arm-record propagation; synthetic mode remains fixture-only. |
| F-7 | Merge `origin/ops/2026-11-11-w1-presign` at `5df1afbf8` in `b0a39479d`, including RL-53 batch, RL-79 walk-every-final-window holds, `f9d48635c` fixture fixes and host guard. The test conflict uses the newer `session_plan` helper; incoming trace was a temporary baseline for regeneration. The kit continues to call public `weight_digest_preflight` and `runtime_stack_preflight`. |
| F-8 | The R1-PHASE-TABLE deviation row now names `thermal.py` with the other six condition-13 sources. |
| F-9 | A synthetic unit forces `k_step_d`'s production branch and asserts the complete `new_sensor_default` S6 record, including `receipt_transferred: false`, even when a historical tuning receipt was supplied. |
| F-10 | No change: conservative fallback scope remains as reviewed. |
| F-11 | Regenerated the committed v4 kit using its generator. Only `plan_tree.json`'s generator digest and `identity_pins.json`'s dependent tree hash changed. Regenerating the night-plan template produced identical bytes. The fresh full-profile trace remains owed under the test budget; no partial trace was moved into place. Kit byte reproduction is distinct from W1 readiness: pending registration inputs still refuse readiness. |
| F-12 | Stale RL-72 inconclusive-message expectation corrected, citing behavior commit `a85ee8ec6`. |
| F-13 | Stale step-30b inconclusive expectation corrected and `capture-predecessor-30b` added to the contract doc, both citing `a85ee8ec6`. |

### Mutation evidence

In-memory mutants only, using `inspect.getsource`, compilation against the module's
live globals and `unittest.mock.patch`; no gate or classifier file was edited.
Controls are the passing round-3 and registration tests. Each mutant is counted
only for an assertion failure from its relevant witness, with zero harness errors.

| Mutant | Witness | Assertion failures |
|---|---|---:|
| M4a: coverage .99 -> .50 | `CoverageBarTests.test_each_bar_independently_refuses_in_every_phase` | 4 (one per phase) |
| M4b: remove consecutive-empty bar | same | 4 |
| M4c: remove read-error bar | same | 4 |
| M4d: drop pre-warmup from smoke table | `test_smoke_table_emits_exactly_all_four_rl76_phases` | 1 |
| M1b: confirm night's picks | `test_night_confirms_and_reports_smoke_pair_and_refuses_inadmissible_pair` | 1 |
| M1c: summary names night's picks | same | 1 |
| M3b: install timeout hook for every kind | `test_gated_d_and_xg_reference_hooks_do_not_dispatch_timed_out_turns` | 1 |
| M6: drop workload from condition 13 | `R1ExecutedSourceTests.test_condition13_names_exactly_the_seven_ruled_sources` | 1 |
| F-4: reinstall 1,200 s post-G0 cap | `test_post_g0_watchdog_fits_realistic_d_turn_and_is_installed` | 1 |

All nine were killed. F-1's per-file one-byte mutants run inside
`DefaultBundleTests` for both released and timeout-without-hook members.
The scratch harness command was `PYTHONPATH=. python3.13 -B /private/tmp/r1-round3-mutants.py`;
final output is `/private/tmp/r1-round3-mutants-final.log`.
An initial harness copied module globals and therefore bypassed the test's
classification patch: that error was not counted as a kill. The harness was
corrected to preserve live globals and all nine were rerun successfully.

### Verification and boundaries

All commands below used Python 3.13, `-B`, unittest and the installed host-command
guard. Modules ran serially. The full suite was prohibited and was not run.
Total test execution was about nineteen minutes, including development attempts
and interrupted runs; the requested extension of the approximate twenty-minute
budget had no answer when this report was finalized.

Each module row means `python3.13 -B -m unittest <module>`:

| Module | Result |
|---|---|
| `tests.align.test_r1_round3` | 8 OK, 26.732 s |
| `tests.align.test_r1_followup` | 12 OK, 35.887 s |
| `tests.align.test_v4_registration` | 24 OK, 64.069 s |
| `tests.align.test_r1_runtime_contract` | 11 OK, 0.007 s |
| `tests.align.test_r1_rehearsal` | 76 OK, 11.968 s |
| `tests.align.test_v4_kit` | 116 OK, 39.184 s; includes committed-kit byte reproduction and F-12 |
| `tests.align.test_v4_executed_closure` | 6 OK, 17.084 s |
| `tests.align.test_v4_dynamic_closure` | 10 OK, 49.752 s; inherited trace plus its live minimal dry-run check |
| `tests.align.test_r1_round2` | 14 OK, 6.025 s; includes both public prepare-preflight API integrations |

Additional focused witnesses passed before the full modules: the two kit
reproduction/inconclusive tests (2 OK) and the three production-packet/chain
integration tests (3 OK). `python3.13 -B -m compileall -q joulewise tests`
and `git diff --check` passed. Direct generator reproduction compared all
30 generated files byte-for-byte with the committed kit: no drift. This is not
a W1-readiness pass; the pending registration inputs still refuse readiness.
The night-plan template regeneration made no byte change.

**Unfinished verification, not a pass:**

- `tests.align.test_w1_prequal`: interrupted after about 836 s, eight tests
  completed without failure, in `CadenceTests.test_an_arm_that_keeps_no_rebuild_or_trusts_the_supplied_packet_fails`
  while the packet tamper matrix was running. Exit 130. The test-budget limit
  prevented completing this module.
- `tests.align.test_v4_next_arm_packet`: not started in round 3; still owed.
- A new full-profile `align_v4_dynamic_trace.py` run: not started within the
  remaining budget; still owed. The committed trace is the presign merge's
  inherited baseline. No partial trace was moved into place. The closure-module
  passes above do not substitute for this new full-profile evidence.

A broader rehearsal run was also interrupted for budget prioritization before
its later successful full-module rerun. Early development runs exposed incomplete
synthetic packet/chain fixtures, missing fake member fields, and an accidentally
imported TestCase class; these were fixed. All final focused/full-module results
above pass. `nice -n 10` was refused by the sandbox; tests proceeded without a
priority change. No host setter or native MLX was run. The stopped process was
the dedicated unittest session; the blinded job was not signalled or changed.

F-1 through F-9 and F-12/F-13 have code/test fixes. F-11's committed-kit drift is
fixed, but its required fresh full-profile trace and the owed long modules remain
open. All five research-lead questions remain parked. No delta-review or native
smoke pass is claimed.

### Commits, changed files and next step

Merge: `b0a39479d`. Runtime/test/kit fixes: `fa677895f`. This report and final witness refinements are in the subsequent local commit.
The trace retained from the merge is an inherited baseline, not new round-3 evidence. No push was performed.

Round-3 files (excluding the presign merge's incoming files):

- Runtime/startup: `joulewise/align/apple/r1_runtime.py`,
  `scripts/align_r1_rehearsal.py`, `scripts/night_chains/align_r1_rehearsal.zsh`.
- Tests: `tests/align/test_r1_followup.py`, `tests/align/test_r1_round3.py`,
  `tests/align/test_r1_rehearsal.py`, `tests/align/test_r1_runtime_contract.py`,
  `tests/align/test_v4_kit.py`, `tests/align/test_v4_registration.py`.
- Trace profile and scheduling: `scripts/align_v4_dynamic_trace.py`, `scripts/test_timings.json`.
- Generated kit: `configs/campaigns/align_v4/plan_tree.json`,
  `configs/campaigns/align_v4/registration/identity_pins.json`.
- Docs: `docs/align/r1_runtime_contract.md`, `docs/align/v4/DEVIATIONS.md`, this report.

The trace profile includes the new round-3 module. Timing-map diff against the
intake head is three inserted lines and zero removals (two arrived in the merge).
The gate and classifier are byte-identical to `b4a6c217f`; the four forbidden
coordination paths have no diff against intake.

Lead's exact next commands, with an expanded test budget/off-MBP runner:

```sh
python3.13 -B -m unittest tests.align.test_w1_prequal
python3.13 -B -m unittest tests.align.test_v4_next_arm_packet
R1_TRACE_WORK=$(mktemp -d)
python3.13 -B scripts/align_v4_dynamic_trace.py --out "$R1_TRACE_WORK/full.json"
```

Complete PREQUAL and next-arm verification off-MBP,
regenerate the full-profile trace to scratch, verify all scenarios and strict closure,
move only a passing trace into place, and rerun both closure modules. Then delta-review
the executed-byte fixes on the final committed head and run native smoke A/B and the measurement-interpreter
weight/installed-stack preflights in a clean, agent-free session. Generate
the FOR_LEAD_ARM packet on that final commit and carry its path via
`ALIGN_R1_PREPARE_PACKET` into the registered arm. Native Metal check:
`JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx`.
The 30B predecessor sidecar, W1 Tf08, coverage scope, condition-13 contract
scope and hard twenty-minute-total interpretation remain for the research lead.
No synthetic result here establishes native sampler coverage, SMC clock-domain
agreement, real sensor admissibility, installed-stack/weight identity or arm readiness.


## Round 4 — RL-84 installed (2026-11-11)

This section supersedes the round-3 parked questions for P-1/P-3/P-4/P-5.
Implementation is committed at `bc27a808e`; verification remains incomplete
for the process-control reason below. No arm, native smoke, hardware validation or signing is claimed.

### Changes and authority

- Read RL-84 verbatim from
  `origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`.
  The named branch already existed at the requested `f0c825779` and was continued.
  Mission M0 found no active stop card; the explicit brief selects this work.
  Coordination-state files were not changed or registered.
- Merged `origin/ops/2026-11-11-w1-tf08-base` (`0d2031cb8`) first, in
  `8c07cf7f8`. The DEVIATIONS conflict retains the incoming ten-path
  R1-PHASE-TABLE row exactly and preserves all existing R1 rows. The incoming
  HELD-WINDOWS row also remains byte-identical.
- **P-1:** the ordinary predecessor has no sidecar and no prompt rewrite.
  Removing `launch_lineage_required` is its only derivation, recorded as
  `template_derivation` beside `template_sha256`. The ordinary-template refusal
  remains. Its synthetic witness compares the complete config at the member
  boundary and verifies no thermal journal. RL-84's exact WP14(a)-R1-SLOW
  wording is installed; the R1-RECORD-KEYS row and runtime contract agree.
- **P-3:** sampler sweep coverage is independent of key success. In each of
  pre-warmup idle, quiet, load and recovery, >=99% sweeps and no two missed
  consecutively are required. Each key independently needs >=99% cells,
  <1% read errors and no consecutive empty pair. Failing keys are excluded
  from both roles and the fallback, and `rejected_keys` lists key, R0 class,
  phase and reason. Tf08 failure or absence fails smoke. The unchanged
  registered classifier/chooser supplies the role rules; its complete result
  is preserved. Smoke writes its diagnostics before refusing bad bars or a
  missing admissible pair. R0 class labels were transcribed solely from the
  audit's "Follow-up to RL-74" (2026-11-11 06:00 PST), not from R0 data.
- **P-4:** `R1_EXECUTED_SOURCES` and its literal-set test now have exactly
  ten paths, adding the launcher, runtime contract and classifier. The
  per-file mutation comparison covers all ten.
- **P-5:** Part B's twenty minutes is an estimate. Round 3's computed
  post-G0 budget is retained (currently 2,600 s); G0's 1,200 s cap is unchanged.
  Its executed-byte delta review remains required before native smoke.
- The RL-72 `workload.py` DEVIATIONS row was already present as
  R1-FOLLOWUP-TIMEOUT and is retained; no duplicate row was added.
- **`thermal.py` is unchanged from `f0c825779`.** The separate
  `w1-tf08-record` seat can continue taking those bytes. W1's P-2 policy edit
  belongs to that seat; no W1-signing pass is claimed here.

Changed files beyond the merge: `configs/align/v4/r1_runtime.json`,
`joulewise/align/apple/r1_runtime.py`, `joulewise/align/apple/v4_registration.py`,
`scripts/align_r1_followup_kit.py`, `scripts/align_v4_dynamic_trace.py`,
`scripts/test_timings.json`, `tests/align/test_r1_followup.py`,
`tests/align/test_r1_round2.py`, `tests/align/test_r1_round3.py`,
`tests/align/test_r1_round4.py`, `tests/align/test_v4_registration.py`,
`docs/align/r1_runtime_contract.md`, `docs/align/v4/DEVIATIONS.md`, and this report.
The full trace profile includes the new round-4 module; no CI test was removed.
Timing-map changes are one inserted measured scheduling hint, no removals.

### Verification and limitations

All tests use Python 3.13, `-B`, unittest and the installed host-command guard,
with one test process at a time. The full suite, native MLX and model downloads
were not used. Historical committed B5 summaries were visible during RUN_STATE
intake; blindness to those summaries is not claimed. No underlying study data,
real restricted/custody path or referenced external model path was opened.
No network or real sudo/pmset setter/launchctl change/caffeinate was used.
The blinded analysis job was neither signalled nor modified.

Each module entry below means `python3.13 -B -m unittest <entry>`:

| Entry | Result |
|---|---|
| `tests.align.test_r1_round4` | 8 OK, 17.619 s, final code |
| `tests.align.test_r1_round2` | 14 OK, 9.329 s |
| `tests.align.test_r1_round3` | 8 OK, 45.352 s |
| `tests.align.test_v4_registration.R1ExecutedSourceTests` | 2 OK, 1.424 s; literal ten-path set and every-file mutation |
| `tests.align.test_r1_followup` | Initial full run: 12 tests, 1 failure, 71.822 s. The short two-cell sampler fixture started between ticks, so its unobserved leading cell dominated the coverage fraction. Fixed by anchoring all four phase grids to the sampler's actual first sweep; no holes are filled. Final rerun pending. |

Development runs before those passes: round 2 had two fixture failures (14 tests,
8.519 s), then passed after comparing the config before the synthetic backend's
model substitution and mutating coverage eligibility rather than an obsolete
pick field. Round 4 had one fallback-fixture failure (7 tests, 17.045 s), then
7 OK in 19.736 s; the final eighth witness additionally exercises smoke refusal
with persisted diagnostics. No development failure is counted as a pass.

`python3.13 -B -m compileall -q joulewise tests` passed. Direct generator
reproduction compared all 30 generated kit files byte-for-byte: no drift.
This is distinct from W1 readiness, which still needs the pending registration
inputs. `git diff --check` passed. Direct checks pin both protected modules to
`b4a6c217f`:

- `thermal_gates.py`: `c72937bd8bf7b5553c1ffd70e76018ffbf25f32578533c8749aa88419837918d`
- `smc_enumeration.py`: `0132579cc33f8a997cdfd5f3dd84466352cdeeeebf9ca7de8dc1ec7990cea0a9`

Full-profile trace attempt: output target
`/private/tmp/r1-round4-full-trace-csz4f4g2/full.json`, log `run.log` beside it.
The attempt began before the implementation commit. I interrupted its wrapper
before using it as final-head evidence, but the detached tracer continued.
`lsof` identified its sole log holder as PID 68087. Sandbox refused both group
and individual SIGINT; no bypass was attempted. Manual interruption was
requested. No other test process was started while it remained active. No
partial or unreviewed trace was moved into the repository.

### Blocking handoff and exact remaining checks

The interrupt-wrapper handling was my mistake: its KeyboardInterrupt ended
before forwarding the signal to the detached child, losing the timeout watcher.
The sandbox then refused the direct signal. At the final observation PID 68087
still held the scratch log, no scenario had reported completion, and no
`full.json` existed. This is an incomplete diagnostic attempt, not final-head
trace evidence. Its source code bytes were the implementation bytes, but it
began before `bc27a808e` was committed; no final-head/full-profile pass is claimed.
The completed unittest-reported run times total 190.846 s (including development failures).
The detached trace adds ongoing time; a final bounded total cannot be asserted
until it is stopped. No more tests were started while it remained active.

**Immediate external step:** interrupt only this synthetic tracer from Terminal:
`kill -INT 68087`, then confirm the scratch log has no active holder. It is
unrelated to the blinded analysis job. No request to touch that job was made.
After the tracer exits, the exact unfinished work is:

1. `python3.13 -B -m unittest tests.align.test_r1_followup` — rerun after the
   two-cell fixture correction; current final-head full-module result is unverified.
2. `python3.13 -B -m unittest tests.align.test_v4_executed_closure` — not run
   in round 4; the round-3 pass does not establish this head.
3. `python3.13 -B -m unittest tests.align.test_v4_dynamic_closure` — not run
   in round 4; the committed trace is still the inherited baseline.
4. `python3.13 -B -m unittest tests.align.test_w1_prequal` — not started
   in round 4; round 3's interrupted result remains incomplete.
5. `python3.13 -B -m unittest tests.align.test_v4_next_arm_packet` — not
   completed in round 4; the unfinished trace has not reported its arm scenario.
6. Fresh final-head full-profile trace to a new scratch destination:
   `python3.13 -B scripts/align_v4_dynamic_trace.py --out <new-scratch>/full.json`.
   Run it directly with working process control, without the detached-child
   wrapper used here. Require `profile: full`, every scenario successful,
   `not_bound: []`, `not_strict: []`; move only that successful trace into
   `docs/align/v4/dynamic_closure_trace.json`, checking digest equality. Then
   rerun both closure modules against it.

No new final-head broad/module/trace success is implied by the focused passes.
After these software checks, the lead still owns the executed-byte delta review
before native smoke, native A/B smoke, sensor ruling, measurement-interpreter
weight/runtime-stack checks, final-commit prepare packet and signing gates.
Native Metal check, outside this sandbox only:
`JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx`.
There are no newly invented research-policy choices; the remaining uncertainty
is software verification and live/native evidence. RL-84's P-2 W1 policy edit
remains with its separate seat.

Local commits: `8c07cf7f8` (requested W1-base merge), `bc27a808e` (RL-84 code,
config, docs and tests). This section and final verification handoff are in the
subsequent report commit. Nothing was pushed. The four forbidden coordination
paths, `thermal.py`, classifier and thermal-gate module have no diff against
the required baselines.

## Round 5 — Fable delta-review D-1 through D-4 (2026-11-11)

The delta cold review was read in full before other intake. Continued the
brief's existing branch `ops/2026-11-11-r1-followup-kit` from exact base
`4c41fe241787e2e7e1015a4096fba311715f77e2`; the starting tree was clean.
Mission M0 found no active stop card or global selection gate. This explicit
desk brief selects the work; no coordination task was registered. The owning
runtime contract, protocol WP14(a), RL-78 E1/E2 and RL-84 P-3 were consulted.
Repository code, ruling text and synthetic fixtures only; no study-custody
or sealed outcome path was opened.

**Condition 13: no file changed.** All ten paths in `R1_EXECUTED_SOURCES`
were compared byte for byte with `4c41fe241`. In particular,
`thermal_gates.py`, the entire classifier file and `thermal.py` are unchanged.
`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` remain untouched, as the brief requires.

### Findings and implementation

- **D-1:** `smoke_selection` filters the full classifier ranking solely by
  each key's coverage across all smoke phases. Existing diagnostics still list
  every coverage rejection with R0 class, phase and reason. The registered
  chooser runs over those survivors; R0 membership remains a subsequent
  admissibility refusal and restricts RL-78's fallback candidates. A selected
  fast key outside the six is held for the lead. A heatsink-class key outside
  the six keeps the slow class nonempty and refuses, without invoking the
  fallback. Two synthetic classifier-result witnesses reproduce the review's
  cases using the production six-key list. Both failed on the unchanged base
  (silent substitution; improper fallback respectively), then passed with the
  one-line filter correction. They also assert the input classifier is intact.
- **D-2:** the chain derives `ALIGN_R1_PREPARE_PACKET` as
  `$MEASUREMENT_ROOT/.align-r1-prepare.json`. The existing arm pins both
  `MEASUREMENT_ROOT` and the chain bytes, and `_chain_environment` already
  supplies that root. This is the narrowest route: no new plan schema, plist
  variable, inherited-shell dependency or generic `extra_env` authority.
  Generate the real packet at that exact path on the final commit. Its file
  check now follows the traps, startup Automatic restore and persistent-marker
  restore. Missing packets refuse before runtime work; the driver's existing
  schema, commit, both-OK and ten-hash checks remain unchanged.
  `ChainEnvironmentTests` parses the production plist template, starts with
  its PATH-only environment, passes through the real `_chain_environment`,
  then runs the actual chain with fixture-owned sudo/interpreter executables.
  It verifies packet delivery and the missing-packet refusal after all restores.
  On the base, both subcases failed; after the fix they pass. Two older chain
  fixtures now create the packet at the registered fixed location.
- **D-3:** the equality witness supplies deterministic synthetic battery probe
  bytes at `battery_float.run_bundle_probe`, just as RSS is stabilized at its
  source. Fake-clock `UpdateTime` and fixed `Voltage` flow through the real
  parser, raw files, metadata property lines and digests. Each adapter must
  actually execute both battery probes and produce passing battery records.
  Every bundle byte is still compared, including the timeout-without-callback
  case and the one-byte mutation of every emitted file. No production battery
  output or comparison exclusion changed. Five fresh-process runs passed 5/5.
- **D-4:** WP14(a) (`pilot_protocol_v4.md:243`) and the runtime contract
  (`r1_runtime_contract.md:110,167`) define load as prefill dispatch through
  last decode of the native 10k-prefill / 4,096-token-capped D turn; the runtime
  config supplies a 1,580 s deadman, not a fixed duration or minimum, so safety
  at >=150 s is supported by the reviewer's simulation but is not guaranteed
  by registration (a 100 s load retains the reported 3–41% Tf08 failure risk).

The native D duration is therefore an explicit uncertainty for the lead to
check on the smoke journal; no measurement data was read to estimate it. No
coverage threshold or phase accounting was changed for this disclosure.

### Round-5 verification

Targeted modules were invoked serially with Python 3.13 and `-B -m unittest
<target>`, `TMPDIR=/private/tmp`, `JW_B5_SYNTHETIC_ONLY=1`,
`JOULEWISE_BACKUP_ROOTS=''`, `GIT_CONFIG_GLOBAL=/dev/null` and
`GIT_CONFIG_NOSYSTEM=1`. The main runner had a 1,000 s aggregate wall cap;
equality repeats, red/green probes and the standalone reproduction kept total
test execution below the brief's approximately 20-minute limit. No full suite,
network, model download, real measurement,
host-setting command or LaunchAgent change was performed. All
chain host commands in the new witness reach local fixture executables.
The attempted `nice -n 10` on the first failing-first D-1 invocation reported
`setpriority: Operation not permitted`; the tests still ran, and subsequent
commands used ordinary priority without changing any existing process.
The first D-2 witness attempt additionally hit a fixture cleanup
`FileNotFoundError` after the expected base refusal; cleanup was corrected
before the definitive failing-first run, which showed both intended failures.

| Target after `python3.13 -B -m unittest` | Result | unittest elapsed |
|---|---|---|
| `tests.align.test_r1_followup` | 12 OK | 44.542 s |
| `tests.align.test_r1_round2` | 14 OK | 6.072 s |
| `tests.align.test_r1_round3` | 8 OK | 34.999 s |
| `tests.align.test_r1_round4` | 10 OK | 14.567 s |
| `tests.align.test_v4_registration` | 24 OK | 97.586 s |
| `tests.align.test_r1_runtime_contract` | 11 OK | 0.003 s |
| `tests.align.test_r1_rehearsal` | 77 OK, including the real `_chain_environment` witness | 21.352 s |
| `tests.test_run_night` | 318 run; 15 failures, 2 errors, 9 skips | 635.156 s |
| `tests.align.test_v4_executed_closure` | 6 OK | 43.784 s |
| `tests.align.test_v4_dynamic_closure` | **INCOMPLETE**: parent terminated at the runner's remaining 70.683 s; no final unittest result | 70.683 s wall cap |
| `tests.align.test_v4_kit.KitTests.test_committed_bytes_reproduce_without_reading_models` | 1 OK, separate invocation after the cap | 3.113 s |

The equality command was
`TMPDIR=/private/tmp python3.13 -B -m unittest -v tests.align.test_r1_followup.DefaultBundleTests`.
Five fresh processes passed in 13.386, 12.081, 11.257, 13.441 and 13.669 s
of unittest time, respectively; the later full follow-up module also passed
that witness. No generator input changed; the reproduce test compared every
generated byte successfully, so `plan_tree.json` needed no regeneration.
`scripts/test_timings.json` was not edited. Four changed Python files passed
`ast.parse`; `/bin/zsh -n scripts/night_chains/align_r1_rehearsal.zsh` and
`git diff --check` passed. The canonical full suite was expressly prohibited.

The full night-driver failure is **not** a green gate. The 17 diagnostic
events comprise:

- `BindSupervisionProcessTests`: nine failure events and one error (8 s
  external-watchdog timeouts, missing fault acknowledgements/observations,
  journal saturation versus acknowledgement deadline, and empty samples).
- `HazardPackPrimitiveTests`: two failures proving process-group cleanup
  and one error waiting ten seconds for a synthetic monitor to terminate.
- `NightProbeTests`: two supervised-probe subcase failures (`ok` refused,
  `refused` timed out) and the plist expectation failure below.
- `QuietDriverIntegrationTests`: one cancellation/reaping failure; its
  fixture compared `None` with a float for expiry-to-receipt time.

The plist failure is confirmed pre-existing at `4c41fe241`: the test's literal
expected environment omits `MAGISTRATE_WATCHDOG_STATUS_HOST`, which the base's
magistrate template already contains. Both files are unchanged in this round;
the comparison was repeated on their exact Git-object bytes. The timing and
cleanup failures involve unchanged driver/gate/fixture paths. They are
consistent with host load or sandbox process-observation limits, but **were
not reproduced on the base**, so their causes remain unverified. They were
not repaired by expanding this bounded R1 fix into unrelated night machinery.

The end-of-session command
`TMPDIR=/private/tmp python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans`
exited **2**, returning
`{"error": "PermissionError: [Errno 1] Operation not permitted: 'ps'"}`.
A direct scoped process-observation attempt was also denied. This is an
unavailable census, not a clean census; fixture descendants after the dynamic
trace timeout cannot be certified absent. No existing host job was signalled
or reprioritized. The lead must observe the fixture census with working
process permissions before relying on cleanup or starting a quiet window.

Raw targeted results are in `/private/tmp/r1-round5-checks/results.json`;
the full night-driver diagnostics are in
`/private/tmp/r1-round5-checks/tests.test_run_night.log`. Equality repeats 2–5
are in `/private/tmp/r1-round5-equality-{2,3,4,5}.log`; the first run and the
dynamic runner timeout are recorded in this session's tool output. These
scratch logs were not promoted into immutable study evidence.
Their SHA-256 values are `df1a1d59dd0fe30c102eeaf4a21afd96138fc65d323b86683c97840bdba0425c`
(`results.json`) and `be8633edfb3e7be1fd0d785b664ea3fd91e15d27ce7f7f038612a6227e3fbc35`
(`tests.test_run_night.log`).

Changed implementation/test paths: `scripts/align_r1_followup_kit.py`,
`scripts/night_chains/align_r1_rehearsal.zsh`,
`tests/align/test_r1_followup.py`, `tests/align/test_r1_round4.py`,
`tests/align/test_r1_rehearsal.py`. This report is the sixth changed path.

No delegation or external consult was used. The gates that directly caught
the reviewed admission defects were the two D-1 failing-first witnesses and
the D-2 plist-to-chain witness. The D-3 full-byte comparison now removes the
known host-battery source of nondeterminism without discarding output bytes.

### Lead handoff after round 5

Local implementation commit: `52060d393` (D-1/D-2/D-3 and witnesses). This
round-5 report lands in the subsequent documentation commit. **LOCAL_ONLY**:
no push, merge, CI result, arm, signature or native validation is claimed.

1. Obtain the short executing delta review of these D-1/D-2 changes before
   using Part B's table or arming. No condition-13 change here calls for a smoke
   repeat; an existing native Part B segment can have its table recomputed.
   With working process observation and an appropriate test window, triage
   the full night-driver failures and rerun
   `python3.13 -B -m unittest tests.align.test_v4_dynamic_closure`; this round
   does not establish a green dynamic-closure or full night-driver gate.
2. In the clean, agent-free native lane, perform any still-owed A/B smoke and
   research-lead sensor ruling. Check the actual D load duration against D-4.
   Native MLX remains outside this sandbox:
   `JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx`.
3. On the final commit and real measurement interpreter, run the weight and
   installed-stack preflights and generate the `FOR_LEAD_ARM` prepare packet
   at `<measurement_root>/.align-r1-prepare.json`, then use the updated pinned
   chain. No real weights or installed-stack qualification was attempted here.
4. This round does not discharge the inherited full-profile trace, PREQUAL,
   next-arm or separate W1 RL-84 P-2 work. The closure-module tests consume the
   committed trace plus their own fresh-process synthetic witness; they do not
   establish a fresh full-profile trace. Nothing was armed, signed or pushed.
