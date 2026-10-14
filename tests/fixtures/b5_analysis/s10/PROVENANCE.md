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

Replay from the worktree with the one runner:

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
| producer | `Seams.group_alive / Seams.boot_session_uuid` | Synthetic collection has no real chain process or boot observation |
| producer | `write_monitor_journals / write_cooldown` | Synthetic hardware publishes complete monitor observations and hash-bound raw cooldown records; all joins are real |
| producer | `whole_window.REGISTERED_NEG8_REFERENCE_CORPUS_DIR` | Resolve the exact sealed synthetic measurement `settled_corpus.json` during writer/harvest execution. The pinned export's default corpus is from another source tree. The identity check and bound arithmetic run unchanged. |
| consumer | `windows.sealed_pack_table (partial builds only)` | Pinned S0 peers satisfy the full-block selection fence until every S10 window exists; only the built sealed S10 target is opened |
| consumer | `mint_floor_artifact_generalized._actual_v2_git_state` | The task forbids commits and intentionally leaves an uncommitted fixture; supply the actual base HEAD as the synthetic clean checkout observation |
| consumer, **conditional** | `mint_floor_artifact_generalized._common_minted_artifact_launch_lineage` (aggregate only; `fixtures_s10.CONDITIONAL_SEAMS`) | Open question Q-LINEAGE: the aggregate floor joins producers from two windows, so its component lineages differ and the unchanged rule refuses. The fixture omits the aggregate carrier only when every component carries one and they differ; per-producer equality and component authentication are unchanged. Every result from C5 on is conditional on the ruling. |

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
