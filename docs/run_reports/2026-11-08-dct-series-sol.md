# DCT series Sol build — 2026-11-08

Branch: `align/2026-11-08-dct-series-sol` (already created at intake).
Base: `05b6d04cba4868531cc03da187689a3dc187e0eb`,
`origin/align/2026-11-08-v4-r11`.
Implementation commit: `e38ab94f3` — `align v4: materialize frozen D C T series through production sessions`.
This report is a subsequent local documentation commit. Nothing was pushed.

## Outcome and boundary

Built the primary 22-member D/fit, C1–C8 and locked-test kit materializer,
frozen prospective allocation, selected production session path, per-window
desk routing, portable evidence-bound R12 producer and test threshold-freeze
binding. A synthetic W1 → D1 → D2 → D3 → C1…C8 → T1…T3 ran through the real
session prepare/install calls, plan writer, generated zsh chain and
`run_night` HAZARD_PACK driver. All fifteen windows completed in the final
synthetic test. This establishes a software route, **not native readiness**.

The candidate explicitly separates three fit windows from eight calibration
windows and three ordinary v4 test windows. The alternative D1=C1…D3=C3
mapping and six-test allocation are also supported. None is silently adopted:
exact-byte lead admission and independent Opus agreement are mandatory.
The checked-in candidate is unsigned. Native W1 registration remains blocked
by its owning pending inputs/U3/B/scorer gates; this work does not fake them.

The full design, runnable commands, source formats, limits and NEEDS_RULING
table are in [DCT-SERIES-sol.md](../align/v4/DCT-SERIES-sol.md).

## Files touched

| File | Change |
|---|---|
| `scripts/align_v4_series.py` | Candidate/alternative allocation, exact validator, real per-window configs/stage graph/identities/seeds/sizing, admission, ordered history, fixed-eight wiring, R12 packet CLI, embedded exact source-receipt bytes, C8-bound test freeze |
| `scripts/align_v4_session.py` | `prepare --window-id`, stored selection and install revalidation, source/admission binding, selected desk and pool metadata, later-window sentinel diagnostics, packet retention, consistent injected clock forwarded to shared install |
| `scripts/align_pilot_session.py` | Optional prepare flags and desk callback, retaining legacy defaults |
| `scripts/bytes_h_session.py` | Derive ALIGN model identity from its frozen `align-model=` tag; the older BYTES roster lacks D and previously projected D as `neg8_reference` |
| `configs/campaigns/align_v4/series/series_manifest.json` | Canonical prospective per-member window/role/pair/condition/index/episode-seed/turn-seed allocation, including W1 |
| `configs/campaigns/align_v4/series/README.md` | Materialization and admission entry point |
| `tests/align/test_v4_series.py` | Independent seed/disk/roster checks, policy refusal tests, evidence transport/tampering, desk selection and fifteen-window FakeWorld production-route replay |
| `docs/align/v4/DCT-SERIES-sol.md` | Design, authority, arm/desk/triage commands, options/recommendations/blocked work and native handoff |
| `docs/run_reports/2026-11-08-dct-series-sol.md` | This handoff |

Generated later-window kits are materialized by the builder after the lead
chooses the manifest and W1 inputs are filled; they are not committed here as
thousands of redundant configs containing pending native slots. Each generator
output is checked for exact bytes before selected-window native preparation.
The materializer itself never inspects model/data directories.

No edits to `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`
or `tests/test_gen_state.py`; no kernel task registration. No advisor-visible
measurement status changed, so `PROJECT_STATUS.md` is untouched. No delegates
or cross-model consults were launched; this is the requested independent Sol
build, awaiting the separately owned Opus build/agreement.

## Final verification

Executed serially with Python 3.13, unittest only:

| Command | Result |
|---|---|
| `python3.13 -B -m unittest -f tests.align.test_v4_series` | **10 passed**, 75.161 s; all fifteen primary candidate windows exercised, no skips |
| `python3.13 -B -m unittest tests.align.test_v4_kit` | **116 passed**, 12.967 s |
| `python3.13 -B -m unittest tests.align.test_v4_cadence` | **16 passed**, 0.004 s |
| `python3.13 -B -m unittest tests.test_bytes_h_session.RealKitStagingTests tests.test_bytes_h_session.SessionTests.test_prepare_uses_real_writer_without_install_or_loop_registration tests.test_bytes_h_session.SessionTests.test_install_calls_only_the_real_installer_interface_with_stub` | **3 passed**, 1.164 s |
| `python3.13 -B -m compileall -q joulewise tests` | Exit 0 |
| `git diff --cached --check` and protected-path diff | Exit 0; protected paths unchanged |

Total final passing selection: **145 tests**. The final series module includes
the real v4 arm checks with fake OS answers: power mode, battery/top-up/OBC,
volume census and R12. Its stage/scaffold, seed, custody, identity, sizing and
order predicates use production code. Model-presence and native registration
checks are fixture seams because the base's real prerequisites are pending.
The shared installer interface is called; launchd execution is simulated.
The actual zsh chain and HAZARD_PACK driver run. Fake measurement tools write
synthetic bundles. No native data/energy/thermal validity is asserted.

The full suite was deliberately not run under the explicit blinded-job
resource instruction. No MLX test or real model ran, no weights were downloaded,
and no native measurement, process census, sampler or measurement pipeline
was deliberately started. Git reads used only repository objects, including
the expressly allowed shared alternate. No network was used.

### Development failures and verification limits

- The first full synthetic attempt exposed the injected `now` not reaching
  shared install; all downstream windows then correctly refused their missing
  predecessors. Fixed the clock forwarding; final replay passes.
- A subsequent attempt entered real scaffold settle waits and was interrupted.
  The final fixture uses the production writer's existing `settle_s=0` seam;
  production retains its original timing. Another attempt reached natural
  chain exit but the sandbox denied `ps`/process-group operations and returned
  `night_chain_alive`. The final FakeWorld explicitly substitutes process
  census and uses three-second, naturally exiting synthetic monitors. Those
  assertions are simulation, not native process-group proof. Native teardown
  tests remain the lead's responsibility.
- `python3.13 -B -m unittest tests.test_bytes_h_session` was attempted, then
  interrupted at `SessionTests.test_desk_gates_exit_one_with_new_c5_is_unavailable`
  in its unrelated four-worker synthetic harvest subprocess. Exit **130**;
  no full-module pass is claimed. Its interruption also printed a temporary
  archive cleanup `Directory not empty` warning. No process census/cleanup
  success is claimed for that interrupted harvest in this restricted sandbox.
  The affected staging/prepare/install selection was subsequently run
  separately and passed as listed above. Do not repeat the broader harvest
  regression on the busy MBP as a prerequisite to this lane's review.

## Open questions and next exact step

The lead must compare the independent Opus delivery against this commit and
rule on mapping/F support, 3 vs 6 test windows and exact ordinary-v4 shape,
F/C/T seeds and condition seed reuse, R13/R14 scorer validity/freeze, W1:5
sentinel/final cohort, and the outstanding U3/B/U5 contracts. Sol recommends
six ordinary v4 test windows for stronger empirical FPR evidence; separate
fit windows only if the admitted scorer requires and funds them, otherwise
alias mode with a qualified independent fit source. The unsigned candidate's
three-test choice is historical scaffolding, not a ruling.

Conditional extra-sentinel placement/sizing and ordinal-18 matched-reference
recovery are **not implemented as admitted native variants**. The primary
builder supports 22 members; an inconclusive U4/U5 requiring two more must
hold for an explicit variant rather than pretend it fits the old ceiling.
The per-window desk does not create a new qualified U4–U6 evidence/scorer
producer: the existing portable multi-window interface still needs its
authenticated R1/W1 reference and frozen residual inputs. Source-bound
triage verifies bytes and ordering, not the scientific truth or commit/push
authentication of another owner's receipt. Those input owners must provide
actual finalizer, terminal/watchdog, quiet and eligibility records.

Next: **lead/Opus agreement and the ruling table in DCT-SERIES-sol.md, then
materialize and commit every admitted kit at the final measuring head while
R1 runs.** Supply actual admission/triage sources, run final-head PREQUAL and
the agreed ≤45-minute non-registrable native smoke, and hand the magistrate
the next two reviewed window packets. Native MLX/process-group commands and
physical prerequisites are listed in the design note. Never arm a real
window from this active agent session or label these fixtures live evidence.
