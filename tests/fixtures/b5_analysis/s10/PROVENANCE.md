> **Rebuilt from clean source checkouts (stage S10 resumed director, 2026-10-14, after the 15:05 restart).**
> The claim gate (`analysis_engine.inputs._read_bundle` through `_source_provenance_admission_problems`)
> admits only members whose recorded source state is clean, and C9 stopped with `member_code_on_kept_unit`
> on GAMMA's first kept decode quad. Every member of all three earlier archives recorded
> `claim_eligible: false` (`start/end_tracked_dirty`, `start/end_untracked_dirty`, some also
> `source_changed_during_run`): the export under `.scratch-s10f/<pin>/` had no `.git`, so the controller's
> `git rev-parse --show-toplevel` (`joulewise/bundle.py` `_capture_source_state`) found the enclosing
> analysis worktree, dirty with the seats' uncommitted work. A real member is collected from the
> measurement clone, a clean checkout. This was a fixture inconsistency, not a production defect: all three
> windows were rebuilt by `.scratch-s10f/build_clean.py`, which makes the export a Git repository of its own
> (one synthetic commit of the exported tree; `git status --porcelain` empty before and after the build), and
> `build_export` now refuses to publish a window whose members are not claim-eligible. In the same rebuild the
> controller, run outside a sandbox for the first time, compared the window's synthetic boot with the host's
> real `kern.bootsessionuuid` (`window_lineage.authenticate_lineage`; inside the seats' sandbox the read failed
> and the comparison was skipped); the builder now supplies the window's synthetic boot to the collection, the
> producer-side seam listed below. ChainTests C1 asserts the claim gate's own source-state admission on every
> kept member.
>
> Two more fixture inconsistencies were then cured the same way (each window rebuilt by the pinned
> programs): the builder wrote every campaign manifest with a null analysis-manifest identity, while
> run_campaign records the contrast pack's prospective manifest id on GAMMA's science stages (the claim gate
> selects GAMMA's cooldown evidence by it; ChainTests test_38); and the lineage recorded the plan tree's file
> digest while production records the measurement clone's committed pack-tree digest, which the claim gate
> recomputes at the lineage's pack root, so the synthetic measurement checkout is now a Git clone with its files
> committed, at build and again at restore (`fixtures_s10.commit_checkout`; ChainTests test_39). The scripts that
> built the windows (`build_clean.py`, `prepare_exports.py`) are archived with the director's logs in
> `/Users/edr/night-archive/b5-consults/l9-rulings/s10/director-k2/`.
>
> **State (stage S10 continuation, 2026-10-14):** ALPHA, BETA and GAMMA are built by the pinned programs and committed. C0 to C4, C-B1 and C-F1 pass on the real programs. The mint passes the per-cell runtime identity check (round K2) and, under the conditional Q-LINEAGE seam below, reaches artifact rebinding; C5 onward and the joined driver from step 5 are conditional on that question. Exact evidence: `/Users/edr/night-archive/b5-consults/l9-rulings/s10/`.

K1 built BETA (125 members, 1,821,172 archive bytes, 575.399521 s wrapper)
and GAMMA (107 members, 1,728,712 archive bytes, 653.993691 s wrapper).
BETA passes C0–C4/C-B1; GAMMA passes C0–C3 and the complete index; both
floor reports classify `p42_floor_cells_only`. C-F1 passes on GAMMA's retained
retired member and uses the explicit writer-dropped fallback on BETA.
C5 enters the real kept-units bootstrap branch and real component/allowance
sessions, then refuses in `_v2_gate_producer_inventory:2630`: decode and prefill
runtime identities differ in `output_policy.stop_condition` (`suite_completed`
versus `requested_tokens_emitted`). The singular-runtime admission rule was
preserved. C5 acceptance remains failing; C8/C9 and optional probes are unproved.
No ALPHA rebuild or archive edit was made. This conflict requires a lead ruling.

# S10 production-shaped synthetic windows

Every class that restores these windows (`ChainTests`, the joined driver classes, the probes,
the argument and partial-index censuses) skips unless `JW_B5_S10_REAL_PROGRAMS=1`: it restores
about 8 GB and runs the real programs (C5 alone is about an hour; one joined driver run is
several hours). The ordinary suite and CI therefore never run them.

`chain_fixture()` restores the published archives once per process, exposes
built packs in `.windows`, and raises `FileNotFoundError: window not built:
<pack>` for missing packs. The chain module skips missing packs with exactly
`window not built`. No delegated Git commit is made: published archives are
new uncommitted files in this directory; ALPHA and the history fixtures are
inherited committed bytes. Acceptance evidence is in
`.scratch-s10f/S10_K1_REPORT.md`.

| Pack | Shape | Governing real writer/harvest pin |
|---|---|---|
| ALPHA | pin2 | `224a264c5faaae90cdf56118df37e773a932700b` |
| BETA | pin4 | `b039c0257d1b1d407ee9598222db3f78f6ad7beb` |
| GAMMA | pin4 | `b039c0257d1b1d407ee9598222db3f78f6ad7beb` |

The sealed pack IDs and pack-directory bytes are unchanged. GAMMA has quads
only, as directed. BETA selects attempt 3 after the included pin2 non-usable
history record and pin3 NULL record. Those small history fixtures change only
S0's pack, plan and attempt identities plus their dependent hashes. Original
pin1–pin4 fixture bytes remain unchanged.

The pin4 export is restored with the exact commands below. `prepare_exports.py`
copies only fixture modules, their support, seal-pin data and S10 fixture bytes.
The deleted `support/` directory is recreated inside the export from the current
`tests/test_harvest_b5_window.py` and `tests/test_harvest_b5_sources.py` helpers.
Before any production import, every governing file in `pins.pin4.files` must
equal both the pin's Git blob and its declared SHA-256. The export's
`joulewise/` and `scripts/` are never overwritten. Measurement source files are
supplied separately from the sealed source inventory's declared Git head.

Because the scratch directory was deleted, the builder restores prior synthetic
custody from each existing archive at its original recorded scratch locators
before extending the ledger. This is extraction and copying of authenticated
prior bytes, not collection or re-harvest. Without this restoration, BETA's first
build recorded `calibration_ledger_custody_invalid` and the pinned harvest refused
`calibration.bracket_acceptance_failed`. The failed raw tree was deleted before
the retry. ALPHA's published archive stays byte-identical.

GAMMA's pinned roster carries science config paths relative to its pack, whereas
the floor rosters carry measurement-relative paths. `member_config_path` resolves
both producer forms before collection; the first path-failing GAMMA tree was
deleted before retry. No production reader was changed for this producer lookup.

The BETA retired-method floor candidate is **not** retained by the real writer:
its retired-method reduction is `energy_uncertainty_status=not_estimable`, so
`anchor_fallback_member_unusable` makes its `MemberEvaluation.usable` false.
`run_campaign._run_whole_window_verdict_locked` selects only usable evaluations
into `bundle_ids`. BETA C-F1 therefore checks disposition 2's aborted-member fallback
and explicitly verifies the retired candidate's writer exclusion; it does not
claim a retained-member preparation disclosure or a killed F1 mutation. GAMMA's
comparative contrast role is outside the writer's floor-member-role gate, so its
retired candidate is retained by the writer; its C-F1 check exercises the stronger
preparation probe when the window is built.

```sh
bash /Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/run.sh mkdir -p /Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/pin4
# export_pin4.sh executes this pipeline, with no change of directory:
git -C /Users/edr/code/JouleWise-wt-l9-s10f archive b039c0257d1b1d407ee9598222db3f78f6ad7beb | tar -x -C /Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/pin4/
bash /Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/run.sh bash /Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/export_pin4.sh
bash /Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/run.sh /opt/homebrew/bin/python3.13 -B .scratch-s10f/prepare_exports.py pin4
```

Replay from the worktree with the one runner. Since the resumed director's rebuild, all three windows are
built in order by `.scratch-s10f/build_clean.py` (extract the pin with `git archive`, `prepare_exports.prepare`,
`git init` and one synthetic commit of the export, then the builder below with the export as its working directory):

```sh
bash /Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/run.sh /opt/homebrew/bin/python3.13 -B .scratch-s10f/build_clean.py alpha
bash /Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/run.sh /opt/homebrew/bin/python3.13 -B .scratch-s10f/build_clean.py beta
bash /Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/run.sh /opt/homebrew/bin/python3.13 -B .scratch-s10f/build_clean.py gamma
```

The earlier rounds' commands were:

```sh
bash /Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/run.sh /opt/homebrew/bin/python3.13 -B .scratch-s10f/build_window.py beta
bash /Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/run.sh /opt/homebrew/bin/python3.13 -B .scratch-s10f/build_window.py gamma
bash /Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/run.sh env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/tmp JW_B5_S10_CHAIN_CACHE=/Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/tmp/s10-chain-cache /opt/homebrew/bin/python3.13 -B -m unittest tests.b5_analysis.test_chain_fixture
```

The runner starts with a standalone `cd`, sets `JW_B5_SYNTHETIC_ONLY=1`, unsets
`JOULEWISE_BACKUP_ROOTS`, and uses `/opt/homebrew/bin/python3.13 -B`,
`PYTHONDONTWRITEBYTECODE=1` and the worktree scratch TMPDIR. Builds use a
foreground eight-process pool, check `df -g /Users/edr` first, remove failed
raw build trees before retrying, and publish successful archives atomically.

## SEAMS

| Side | Function/input | Reason |
|---|---|---|
| producer | `Runtime / mock-runtime duration constants` | Model launch executes pinned prompts with synthetic model identities and .004331/.017331 per-token durations |
| producer | `Registry.resolve_telemetry / fake_powermetrics_process.py` | The real PowermetricsTelemetryAdapter consumes synthetic primary XML |
| producer | `FixtureClock / TimedTelemetry collection clock` | Synthetic paired clocks advance through the persisted idle interval |
| producer | `BatteryClock / battery_probe / environment guards` | Synthetic hardware observations supply battery, adapter, display and environment readings during collection |
| producer | `self_consistent_calibration / clone_member` | Generate primary pulse/telemetry/lifecycle bytes; real evidence derivation and reduction follow |
| producer | `harvest_checkout runner` | git archive has no .git; only head/status observations are supplied; file digests are real |
| producer | `calibration_ledger._committed_pin_bytes` | git archive has no commit for the new synthetic head pin; supply only its Git blob observation, with all ledger parsing and digest checks real |
| producer | `historical calibration custody visibility` | The immutable synthetic cutoff prefix has historical locators. During production only, these are absent observations; current and previously built synthetic windows retain real calibration primary files |
| producer | `Seams.group_alive / Seams.boot_session_uuid / window_lineage.current_boot_session_id` | Synthetic collection has no real chain process or boot observation; the collection and the harvest observe the window's synthetic boot (`fixtures_s10.SYNTHETIC_BOOT`) |
| producer | `write_monitor_journals / write_cooldown` | Synthetic hardware publishes complete monitor observations and hash-bound raw cooldown records; all joins are real |
| producer | `whole_window.REGISTERED_NEG8_REFERENCE_CORPUS_DIR` | Resolve the exact sealed synthetic measurement `settled_corpus.json` during writer/harvest execution. The pinned export's default corpus is from another source tree. The identity check and bound arithmetic run unchanged. |
| consumer | `windows.sealed_pack_table (partial builds only)` | Pinned S0 peers satisfy the full-block selection fence until every S10 window exists; only the built sealed S10 target is opened |
| consumer | `mint_floor_artifact_generalized._actual_v2_git_state` | The task forbids commits and intentionally leaves an uncommitted fixture; supply the actual base HEAD as the synthetic clean checkout observation |
| consumer, **conditional** | `mint_floor_artifact_generalized._common_minted_artifact_launch_lineage` (aggregate only; `fixtures_s10.CONDITIONAL_SEAMS`) | Open question Q-LINEAGE: the aggregate floor joins producers from two windows, so its component lineages differ and the unchanged rule refuses. The fixture omits the aggregate carrier only when every component carries one and they differ; per-producer equality and component authentication are unchanged. Every result from C5 on is conditional on the ruling. |
| consumer, **conditional** | `analysis_engine.inputs._frozen_consumer_identity_set` (hazard lineage over an unprojected sealed pack only; `fixtures_s10.CONDITIONAL_SEAMS`) | Open question Q-CONSUMERID: the claim gate authenticates a contrast arm's declared consumer identities only from the U8 freeze and identity-projection receipts, which the unprojected block-5 sealed packs never carry, so every block-5 contrast floor refuses `consumer_identity_set_unauthenticated`. The fixture reads the declared set from the sealed pack's one identity unit for the family (its config inventory under the committed pack tree the lineage digest authenticates; file digests checked). Results from C9 on, and the joined run from step 9 on, are conditional on the ruling. |
| consumer, **conditional** | `analysis_manifest_v3._authenticate_floor_dependencies` (exact_stack_only lookup only; `fixtures_s10.CONDITIONAL_SEAMS`) | Open question Q-EXACTSTACK: the sealed GAMMA manifest declares exact_stack_only transport, and the finalizer then looks for a floor cell keyed on the consumer family itself, while every block-5 floor is measured on its floor-pack family and names the consumers in its same-stack transport group. The fixture serves the consumer by its transport group's single source cell (group admission and stack identity still checked). Results from C8 on are conditional on the ruling. Extended by the resumed director (2026-10-15), same option, to the close-out's recheck of each finalized arm against its bound floor cell (`dominance_closeout._contrast_floor_binding_error`): an arm is compared with its cell's key when the cell's single-source transport group admits the arm's family; eligibility, stack identity and the common-mode replay are still checked. The joined run from step 6 on is conditional on it. |

With three windows the pack-table seam is inactive (the ordinary index is
used). No session, strict validator, reducer, bracket evaluator, exclusion function,
extraction calculator, mint calculation, finalizer or claim engine is replaced.
The consumer Git observation is necessary because the task forbids committing
the fixture. The partial-only pack-table seam disappears when all three sealed
S10 archives exist. All seams must be applied through `chain_fixture().seams()`.

The harvest's sealed source inventory does not include the synthetic hardware
executable. Exact bytes travel in the outer tar as `synthetic-hardware/` and
are restored at the file-authenticated locator outside the archive. Locator
relocation rebuilds dependent file/content hashes, ledger receipts, sidecars,
source inventory and census digests; raw telemetry and science are unchanged.

Synthetic power starts at 7.331 W with .003331 W reference increments and
.73331 W science increments. Science and endpoint references are written as
separate campaign manifests: a floor spec must cover every invoked member of
each addressed science campaign. Token durations
are .004331/.017331 s. The measured sampling window lasts 30.331 s.
Calibration lag starts at .021331 s, increments .001 s per pack, and post lag
adds .001 s. Another session uses .061331 s. Pulses are 2/20 W at 100 ms.
Shortened streams preserve first endpoint, power transitions, elapsed time and
integrals; real derivation regenerates clock, idle admission, CSV/rich telemetry
and summaries. `restricted_floats()` enumerates summary and withheld JSON floats.
All energies and hardware observations are synthetic. Each archive's
`STRUCTURE.json` records member faults, counts, and measured build wall time.
