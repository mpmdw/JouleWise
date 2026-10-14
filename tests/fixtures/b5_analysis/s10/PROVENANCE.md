> **Partial last-round fixture:** ALPHA is promoted to `alpha/` and rebuilt with the production writer's default minted semantics. BETA and GAMMA are not built. The latest extraction reached a real ready session and all four target cells; the two p42 cells refused. A further producer campaign-grouping repair requires a fresh extraction. Exact archive versions, verification and remaining gates are in `.scratch-s10f/S10_LAST_REPORT.md`.

# S10 production-shaped synthetic windows

`chain_fixture()` restores the published archives once per process, exposes
built packs in `.windows`, and raises `FileNotFoundError: window not built:
<pack>` for missing packs. The chain module skips missing packs with exactly
`window not built`. No delegated Git commit is made: published archives are
uncommitted files in this directory. Acceptance evidence is in
`.scratch-s10f/S10_LAST_REPORT.md`.

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

Exports were made with `git archive <pin> | tar -x -C .scratch-s10f/<shape>/`.
`prepare_exports.py` copies test support into each export; governing production
hashes are checked before import. Measurement source files are also supplied
from the sealed source inventory's declared Git head where necessary.

Replay from the worktree with the one runner:

```sh
bash /Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/run.sh /opt/homebrew/bin/python3.13 -B .scratch-s10f/build_window.py alpha
bash /Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/run.sh /opt/homebrew/bin/python3.13 -B .scratch-s10f/build_window.py beta
bash /Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/run.sh /opt/homebrew/bin/python3.13 -B .scratch-s10f/build_window.py gamma
bash /Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/run.sh env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/Users/edr/code/JouleWise-wt-l9-s10f/.scratch-s10f/tmp /opt/homebrew/bin/python3.13 -B -m unittest tests.b5_analysis.test_chain_fixture
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

No session, strict validator, reducer, bracket evaluator, exclusion function,
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
