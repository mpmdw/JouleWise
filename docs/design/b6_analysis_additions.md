# Block-6 analysis additions: design and build brief (item B6-1)

**Status: design, written blind, 2026-10-21; third, fourth and fifth passes 2026-10-22 (§21 to §23).** Author: Opus 5.5 (interactive session 2dc9c377, workflow item B6-1).
Claim-path. It designs the code that registration B6-REPL §13 requires
(`docs/registrations/block6_replication_DRAFT.md`, written "the registration" or "REG" below), maps every clause of
REG §9.5 to §11.4 and §13 to a function (§13 of this file), and ends with the Sol build brief (§17).

**Which text wins.** The registration, then the rulings it cites (cold gates of 2026-10-17, the threshold and silly-numbers
rulings, block 5's B5-REG and B5-PLAN where REG says "unchanged"), then this design. Where this file and the registration
differ, the registration governs and this file is wrong.

**Blind.** The author opened no block-5 or block-6 archive, export, withheld file, restricted custody or harvest
record. Read: the registration on main `ef520743c`; B5-PLAN §2.4, §3, §8.1, §8.2; B5-REG §0.12 and §9.2; the block-6
code at `lane/2026-10-17-b6-packs-registered` `1706257c4` (`joulewise/b6/acceptance.py`, `session.py`, `queue.py`,
`loop.py`, `export_runs.py`, `session_paths.py`, `survivor_screen.py`, `analysis_lane.py`, `lanes.py`, the pack files,
`configs/b6/registration/README.md`, `scripts/harvest_b6_session.py`); lane L9 at
`lane/2026-10-20-l9-ruling-build` `1ab888a68` (`joulewise/b5_analysis/*.py`, the step programs' window-index
bindings, `joulewise/external/km003c_parse.py`, `joulewise/analysis_engine/inputs.py`,
`joulewise/paper_reported_energy_issuer.py`; L9's head on 2026-10-22, `64b4e2cbf`, changes no file under
`joulewise/` or `scripts/` that this design reads; in its tests it amends `tests/b5_analysis/fixtures_s10.py` and adds
the real joined-driver harness `tests/b5_analysis/joined_s10.py`; its head at the third pass, `500f7ad3d`, adds only
reports since `64b4e2cbf`); the independent recompute at
`lane/2026-10-14-independent-recompute` `76f45da3e` (its meter functions only); RUN_STATE items 53, 59 and 65, and
the record of activation c634f6f3 (item 53), which carry structure only (counting, rounds, flag codes). One blind
consult round (§19) checked the draft by execution on synthetic inputs. For the third pass: the BAT-2 battery ruling
(`docs/process_traces/2026-10-22-forward/BAT-RULING.md` at `fc7548a17`; its numbers come from the non-claim BYTES
session H only) and B5-PLAN §8.1's battery-assist rule. For the fourth pass: B6-2's fill of S-9 and S-11
(`lane/2026-10-22-b6-s9-s11` `9715af399`; its registration diff and trace read with every digit masked except the two
replay counts of science runs reaching the line, which are structure) and the code of its replay program;
`joulewise/desk_compress.py`, `joulewise/b6/desk_lane.py` and `joulewise/b6/driver_lane.py` at `1706257c4`; L9 at
`195d2d405` and its L9-1 report (digits masked). For the fifth pass: the data-integrity audit of 2026-10-22
(`REPORT.md` F1, F4 and G4, and its compressed-file census, which gives file counts and bytes per session, root and
file category, and no energy); L9 at `152d8dc9f` (`dry_run.py` `RunState`, `invoke`, `kept_bundles` and steps 0 to 4,
`archive.py` `_read` and `compare_runs_root`, `joulewise/cli.py` `_cmd_reduce`,
`arm_readiness.authenticate_bundle_launch_lineage`, `detection_floor.complete_bundle_sha256`,
`floor_extraction.py`'s `hash_bundles` path); `desk_compress.py` `read_bytes`, `restore` and `compress` at
`1706257c4`; the audit-fix lane's draft `scripts/restore_run_to_scratch.py` (uncommitted); and
`joulewise/twins/harvest_twin.py` on main `c21c52dfa`.

---

## 0. What this file decides (summary)

1. **L9 cannot open a block-6 archive today**, for reasons that are about block 5's bindings, not about block 6's
   numbers. L9 hard-binds block 5's seal pins, pack ids, flag catalog, harvest pins and the rule "the analysed
   attempt is the first claim-usable one". Item 53 is one face of this: r2-gamma would be refused at four places
   (§4.4). The additions therefore start with a **binding seam**: one value, `AnalysisBlock`, collects every
   block-5 binding, constants and policies alike, with block 5's as the default, and block 6 supplies its own (§4).
2. **Counting comes from the loop and the session's acceptance, never from `claim_usable`** (§4.5, §4.6, §12). The kept
   units are recomputed with the sealed exclusion function under the block-6 rule (no GAMMA midpoint reason,
   REG §8.2), then the desk graphics exclusion of REG §8.3 item 3 is applied; a session whose target stratum then
   falls below 5 kept units stops counting before pairing is computed.
3. **Units of analysis**: one *floor unit* per counting ALPHA or BETA session, and one *GAMMA unit* per counting GAMMA
   session, which is an L9 chain over (that GAMMA session, its paired ALPHA, its paired BETA) (§4.3, §5).
4. **Two dry-run phases**: per-session steps run blind now; the cross-block steps (REG §10, §11) read block 5's
   released outputs, so they run only after block 5's release event. The dry run that satisfies REG §12.3 item 3 is
   the one that includes them (§14).
5. **S-15 cannot be filled by pointing at a block-5 analysis commit**: L9 defines only the request-level
   whole-machine cross-check (B5-PLAN §8.2). The per-phase definition exists only in the independent recompute. §8
   gives the definition, and §15 says how the lead fills the slot.
6. **Battery assist** (the MagSafe question in RUN_STATE item 65): the problem was real and was ruled on
   2026-10-06. The rail numbers are unaffected. The whole-machine line was the remaining gap. §7 closes it. The
   BAT-2 ruling of 2026-10-21 adds the battery term to BYTES' DC input; it does not change block 6's registered
   per-phase line, and §7.1 says what block 6 takes from it.
7. **The block-6 harvest stored its brackets with block 5's acceptance** (by the code at `f31aca19f`; found by the
   consult, §19 F2). Counting is unaffected; the analysis builds the registered block-6 bracket and keeps the stored
   one out of every number (§4.8).
8. **The session bytes are desk-compressed** (fourth pass; mechanism replaced in the fifth). After each harvest the
   loop's desk replaces every file of 1 MiB or more under the session's runs roots, its custody and the archive's
   `sources/` (the raw sampler files among them) with a verified `.zst` sibling (`joulewise/desk_compress.py`). L9
   opens these files by their plain paths, so as written it would refuse every session at step 0. Restoring a whole
   unit plain does not fit the disk (a GAMMA unit is about 109 GiB plus a 20 GiB reserve, against 69 GiB free), and
   restoring less is not enough, because readers at every step, most of them in files the analysis may not edit,
   open plain paths, some over three sessions in one call (the fifth pass's consult). So the driver restores a unit's
   sessions in place as APFS transparently compressed files (plain to every reader, about their compressed size on
   disk), checked file by file, and compresses them again after the unit. A test requires every output to be
   identical on plain and compressed fixture sessions (§4.1). A session's paths come from its session
   record, because a re-harvest moves the archive to `archive.reharvest-<n>`.
9. **S-9 and S-11 are filled** (B6-2, pending merge): T_phase and P* per pack and target phase, GAMMA's from its 8B
   runs, with its 1.7B values printed beside. The design follows that grain (§4.6, D11 revised). B6-2's replay of the
   filled line over the nine counting sessions removes 0 of 840 science runs.

---

## 1. Terms used below

- **Session**: one block-6 collection of one pack (REG §1.6), with a loop session id of the form `r<round>-<pack>`,
  sometimes with a suffix (`-a<n>`, `-n<m>`; `joulewise/b6/loop.py` `_layout`, `_fresh_id`).
- **Session record**: `/Users/edr/night-b6/sessions/<session id>/session.json`
  (`joulewise.b6.driver_lane.metadata_path`): the session's `paths` (custody, runs parent, archive, export, staging,
  measurement checkout), its `runs_roots` and, after a re-harvest, `harvest_history`.
- **Archive**: the harvest's output (REG §14 S-2), at the session record's `paths.archive`:
  `/Users/edr/night-b6/sessions/<session id>/archive`, or `archive.reharvest-<n>` after a re-harvest (REG §4;
  `joulewise/b6/desk_lane.py` `reharvest`). It holds the
  block-5 harvest's files (`harvest.json`, `derived/exclusions.json`, `derived/flags.jsonl`, `derived/roster.json`,
  `derived/window_flags.json`, `derived/neg8-allowance.json`, `withheld/…`, `sources/…`) plus the block-6 files
  `derived/b6-acceptance.json`, `derived/b6-flags.jsonl` and `withheld/b6-neg8.json`.
- **Desk compression**: what the loop's desk does after a session's harvest and acceptance
  (`joulewise/b6/desk_lane.py`, `joulewise/desk_compress.py`, unchanged since `f31aca19f`): each file of at least
  1 MiB under the runs roots, the custody and `<archive>/sources` becomes `<file>.zst`, checked by decompressing it and
  comparing SHA-256 before the original is removed. Never compressed: `derived/`, `withheld/`, `harvest.json`,
  `sources/ledger`, `sources/inputs`, `sources/repo`, `SHA256SUMS`, and every capture the capture list names. The
  record is `<archive>.desk/compression.jsonl`, one row per event (`compress` or `restore`: path, root kind, SHA-256 of
  the plain bytes, size, mode, modification time), plus `compression-summary.json`. The root kinds are `runs`,
  `custody` and `archive` (the archive's `sources/`). On the nine sessions (audit census, bytes only) the desk
  compressed 1,410 to 1,640 files per session, 32.75 to 38.82 GiB of plain bytes: per session at most 19.14 GiB under
  `runs`, 19.41 GiB under `archive` and 0.28 GiB under `custody`. Compressed categories: each claim run's
  `raw/powermetrics.plist`, `raw/powermetrics_idle.plist`, `raw/powermetrics_idle_post.plist`, the idle-attempt
  plists, `rich_telemetry.jsonl` and `rich_telemetry_idle.jsonl`; and per session the hazard monitor's journals
  (`hazards/monitor/clock.jsonl`, `battery.jsonl`, `contention.jsonl`, `thermal.jsonl`), the meter stream under
  `hazards/meter/`, the cadence sampler file, `SHA256SUMS` files over 1 MiB, five sessions' `campaign_log.jsonl`, and
  the results clones' `.git` packs.
- **Loop record**: `/Users/edr/night-b6/loop/attempts.jsonl` (one line per attempt: `session_id`, `round`, `packs`,
  `t0`, `outcomes`, `line`) and `state.json` (its `reharvested` corrections). `joulewise.b6.queue.counting_ids`
  reads both.
- **Acceptance record**: `derived/b6-acceptance.json`, schema `joulewise.b6_acceptance.v1`, with `counting`,
  `verdict`, `excluding`, `cells` (kept units per cell), `calibration` (b_op), `neg8`.
- **Block-5 exclusions document**: `derived/exclusions.json`, written by the block-5 harvest code that the block-6
  harvest runs. Its `claim_usable` and `reasons` carry block 5's meaning (item 53).
- **Block-6 exclusions document**: the same function's output under the block-6 rule (§4.5), written by the
  analysis into restricted custody. It is never written into an archive.
- **Desk exclusion**: an exclusion the registration assigns to the desk instead of the harvest. There is one, the
  graphics and neural-engine line P* (REG §8.3 item 3, S-9).
- **Analysis counting**: the loop's counting, confirmed by the acceptance record and re-tested for REG §8.2 N3 after
  the desk exclusion (§4.6).
- **Floor unit, GAMMA unit**: §4.3.
- **Structure**: what REG §12.1 releases during the block (verdicts, counting, flag counts by code and family, kept
  unit counts, the drift screen's verdict word, hazard measurements, timing that is not a phase duration).

---

## 2. The forcing problem

REG §13 says the programs are L9 at its release tag "plus the block-6 additions (pairing, between-session summary,
side-by-side table, replication word, flagged-inclusive line)". Reading L9 against a block-6 archive shows more than
those five additions are needed:

| L9 place (at `1ab888a68`) | What it requires | What a block-6 archive has |
|---|---|---|
| `archive.compare_runs_root` (step 0) and `dry_run` steps 1 and 2 (strict validation, re-reduction) | every claim-run file the archive's `SHA256SUMS` lists, and every raw file, at its plain path | files of 1 MiB or more under the runs roots, custody and `archive/sources` stored as `.zst` by the desk (§4.1) |
| `dry_run._step_results` | an analysed window with `superseded_archive_roots` refuses `reharvest_disclosure_record_required` (block 5's index has no deciding record) | REG §4: a harvest fault is re-run on the same bytes and the re-run decides; the record is the loop's `reharvested` entry and the session record's `harvest_history` (§4.9) |
| `b5_analysis/windows.py` `SealPins.load()`, `governing_pin`, `sealed_pack_table` | block 5's harvest pins (pin1 to pin4), pack ids from `sizing_b5.json`, plan ids `v5-b5-<pack>-a<n>-…` | harvest from the measurement checkout at `f31aca19f`; session ids `r<k>-<pack>` |
| `windows.select_analysed_attempts` → `flags.exclusions.first_claim_usable` | the first claim-usable attempt per pack, all three packs | up to three counting sessions per pack; selection by counting and pairing |
| `archive.open_attempt_record`, `open_archive` | `claim_usable` true; block 5's catalog digest; block 5's record shapes | r2-gamma: `claim_usable` false (`neg8.midpoint_lost_primary`); block-6 catalog `b5bce6c6…` |
| `kept_units.load_kept_units` | `claim_usable` true, `reasons == []`, catalog = block 5's | as above |
| `analysis_engine/inputs.py` `require_contrast_attempt_keeps_midpoint` | GAMMA carries no `neg8.midpoint_lost` | REG §8.2: on GAMMA a lost midpoint is disclosed, not removing |
| `bracket.evaluate_window_bracket` | block 5's acceptance (s_bracket 14.531 ms) | block 6's acceptance (s_bracket 10.818 ms, REG §3.3) |
| `bracket.block_b_max_for_archives`, `dry_run` steps 4, 10, 11 | exactly three archives, one per pack | floor sessions that serve no GAMMA session (ALPHA r4) |
| `whole_window` admission, `floor_extraction` and mint allowance acquisition | a passing stored or survivor NEG-8 decision under block 5's rules | REG §1.8's allowance from the b6 screen; block 5's 0.05 J bracket bar fails every session by construction (REG §9.5 item 7) |
| the archive's stored bracket | (L9 reads it) | computed with block 5's acceptance, s_bracket 14.531 ms (§4.8) |
| `disclosures._machine_lines` | request-level ΔE and ρ only | REG §9.5 item 5 asks for per-phase energy (S-15) |
| `disclosures` sentence constants (`AGREE_SENTENCE`, `DIFFER_SENTENCE` and the other fixed sentences) | "window" wording; the cross-window line says "within-window intervals" | REG §9.5: "session" for "window"; item 6's label "agree within the statistical half-widths; timing bounds B not included" |
| `joulewise/b6/analysis_lane.py` | "No registered-estimator precision entry point exists in stage 1" | correct and stays so: REG §5.3 says no precision stopping applies to the replication packs |

So the additions are: reading compressed session bytes (§4.1); the binding seam (§4.2); the block-6 binding (§4.4 to
§4.9); the units and pairing (§4.3, §5);
the new labelled lines (§6); whole-machine per phase (§8); the cross-block outputs (§10, §11); the release comparison
(`compare.py`, §15 step 10); the structure-only record (§14).

---

## 3. Module layout

New, in L9's package (the seam; §4.2):

- `joulewise/b5_analysis/block.py`: `AnalysisBlock` (a frozen dataclass), `BLOCK5` (built from exactly the
  constants L9 uses today) and `block_for_index(path) -> AnalysisBlock` (reads the index file's `schema` field only).

New package `joulewise/b6_analysis/`:

| Module | Contents |
|---|---|
| `sessions.py` | read the loop record and each acceptance record; `counting_sessions()`; `desk_exclusions()` (P*); `analysis_counting()`; `pair()` (REG §6.2) |
| `binding.py` | `BLOCK6`: the session index writer, `configs/analysis/b6/seal_pins.json` reader, block-6 record shapes, the block-6 exclusions document (§4.5), the allowance (§4.7), the b_op check (§4.8), the usable predicate |
| `driver.py` | unit construction, the restore into transparently compressed files, the re-compression and the after-check around each unit (§4.1), the step lists of floor and GAMMA units, invocation of L9's programs, the structure-only record (§14) |
| `lines.py` | REG §9.5 items 3, 7, 8, the battery-assist value of the whole-machine line, the outside-processor labelled alternative (§8.5), the P* exclusion's record |
| `machine.py` | whole-machine energy per phase (REG §9.5 item 5, S-15; §8 here) |
| `crossblock.py` | between-session summary (§10), side-by-side table and Δ (§11.1), replication word (§11.2), sentence templates (§11.3), flagged-inclusive line (§11.4) |
| `compare.py` | REG §12.3 item 4: the analysis against the independent recompute |

New script `scripts/b6_analyze.py`: `--mode blind-dry-run|release --loop-root <dir> --sessions-root <dir>
--custody <dir> [--block5-release-record <file>]`. Exit 0, 3 (a registered outcome) or 2, as
`scripts/run_b5_analysis.py`.

New configuration under `configs/analysis/b6/`:

- `seal_pins.json`: the block-6 bindings by digest: the S-1 commit `f31aca19f` as the only harvest pin; the
  registration file, catalog (`b5bce6c6…`, S-3), acceptance (`ea130c87…`, S-4), identity pins (`513d7d4a…`, S-18)
  and the three pack files.
- `registered_constants.json`: F_min = 1.9 J (S-10), w = 5.432 J per CPU-s and c_q = 0.54 CPU-s per 10 s interval
  (S-8; 0.72 as measured, printed beside), d = +0.180 J (S-6), and T_phase and P* per pack and target phase (S-11,
  S-9: filled by B6-2 from each pack's first smoke, copied as the registration's exact decimal strings; GAMMA's 1.7B
  values beside them, marked not registered; null while the base lacks the fill). Each value carries its REG
  section, and a test checks each copied string against the registration text (exact strings).
- `dry_run_refusal_classes.json`: tooling and outcome classes for the block-6 steps (L9's file is the model).
- `printed_precision.json`: decimals per quantity kind (§11).

Untouched: `joulewise/b6/analysis_lane.py` (§2, last row); every `joulewise/b5/*.py` file in
`configs/campaigns/v5_claim_25g83/sealed_inventory.json`; `configs/b6/flag_catalog_b6.json` (pinned, S-3); the
measurement checkout.

---

## 4. How L9's steps run on block-6 sessions

### 4.1 One session's inputs (layout S-2)

For session `s`, the analysis reads, and only by automation into restricted custody:

| Input | Path | Used for |
|---|---|---|
| Session record | `sessions/s/session.json` | the archive path (`paths.archive`), the runs roots, the measurement checkout, the re-harvest history |
| Plan | `sessions/s/custody/night_plan.json` | the session's runs, custody and archive roots |
| Archive | the session record's `paths.archive` | everything L9 reads, plus the block-6 records above |
| Compression record | `<archive>.desk/compression.jsonl` | what to restore before the unit, and the check after it |
| Claim runs | the plan's claim runs root under `sessions/s/runs-parent/` | strict validation and re-reduction of every kept bundle (L9 steps 1, 2) |
| Capture list | `<measurement checkout>/runs/calibration_observation_ledger.jsonl` (S-2) | L9's ledger-prefix check |
| Loop record | `/Users/edr/night-b6/loop/attempts.jsonl`, `state.json` | round, t0, counting |

Never read: the export directory (`sessions/s/export`). Its per-run table carries the hidden-offset factors
(`joulewise/b6/export_runs.py`, pack files `"blinding": {"hidden_offset": true}`), and the analysis computes from the
bundles. So REG §12.1's "divided out before any number is printed" is satisfied by never reading the export. A test
asserts that no `b6_analysis` module opens a path under `export`.

**Desk-compressed bytes.** *Forcing problem.* The desk compressed each session after its harvest (§1). L9 and the
programs it calls read session files by their plain paths, at every step: step 0 reads every claim-run file the
archive's `SHA256SUMS` lists and every archive source; steps 1 and 2 run the CLI (`validate-bundle --strict`,
`reduce`); and the strict bundle validator, the reducer and the campaign-log reader are called again by step 4's
extraction, step 5's pinset emitter and mint, step 8's finalizer, step 6's close-out, step 9's claim gate, step 10's
issuer and step 11's sensitivity pass and disclosures (consult of the fifth pass, §23 F1). Several of these calls
read two or three sessions in one call (step 5: ALPHA and BETA; steps 9 and 11: all three), and steps 3, 3b and the
sensitivity half of step 11 do not go through `RunState.invoke` (§23 F2). Most of the readers are in files the
analysis may not edit. On compressed bytes they fail in four ways, all executed on synthetic bundles: strict
validation exits 2; `reduce` exits 0 with different output bytes; `detection_floor.complete_bundle_sha256` returns a
different digest without raising (it hashes the `.zst` files under their own names); and
`campaign_provenance.load_campaign_log_rows` reads a compressed log as an empty log.

So all of a unit's session files must be at their plain paths for the whole unit. Restored plain, that does not fit
the disk: a GAMMA unit's sessions hold, for example, 32.75 + 37.90 + 38.64 = 109.29 GiB (54.01 GiB under their runs
roots alone, r2-gamma with r3-alpha and r2-beta), and `desk_compress.restore` also keeps 20 GiB free, against 69 GiB
free on 2026-10-22.

*Rule* (`driver.restored(unit)`, a context manager around each unit). Everything that reads session bytes (§4.5 to
§4.9, §6 to §8 and L9's steps) runs inside it.

1. **Restore into transparently compressed files.** Before the unit, for each of its sessions, every row of
   `<archive>.desk/compression.jsonl` whose latest event is `compress` (all root kinds) is restored in place as an
   APFS transparently compressed file: `zstd -d` the `<x>.zst` into `<x>.partial`; check its SHA-256 against the row;
   `/usr/bin/ditto --hfsCompression <x>.partial <x>.tc.partial`; check the SHA-256 read back from that copy; put back
   the row's mode and modification time; fsync; rename it to `<x>`; remove `<x>.partial` and `<x>.zst`; append a
   `restore` row (the desk's row, plus `"apfs_compressed": true`). This is `desk_compress.restore`'s per-row
   procedure with the `ditto` step added. The file is then a regular file at its plain path, of its full logical
   size, whose bytes every reader gets unchanged (the kernel decompresses on read), and which takes about its
   compressed size on disk. Where transparent compression is unavailable (Linux, the CI unit tests) the file is
   written plain and the row says `"apfs_compressed": false`; the real dry run runs on the Mac.
   *Space.* Before each file: free space must exceed the file's plain size (the transient `.partial`) plus 20 GiB
   (the desk's reserve), or the unit stops with the tooling refusal `b6_restore_failed` (`restore_space`, shortfall
   in bytes) and recovery (item 2) runs. The cure is freeing disk; the analysis never deletes anything to make room.
   *Measured* (synthetic plist text, this Mac, macOS 26.6.2): `ditto --hfsCompression` stored a 13,262,618-byte file
   in 1,728 KiB (12,952 KiB plain; `zstd -3` 1,012 KiB), with the same SHA-256 and the `UF_COMPRESSED` flag, and a
   265 MB file in 0.17 s. At that 7.5x ratio a GAMMA unit's 109.29 GiB would take about 14.6 GiB; the real ratio is
   printed per session (on-disk bytes from `st_blocks`, structure).
2. **Recovery and re-compression.** After the unit, also when it stopped early, the driver runs the desk's
   `compress(...)` for each session of the unit, with the arguments the desk used (`archive`, `custody`, the session
   record's `runs_roots`, the measurement checkout's capture list as `ledgers`, the default `min_bytes`). It reads the
   transparent files as plain, writes verified `.zst` siblings and removes them. If that checkout's capture list no
   longer exists, `ledgers` is empty: `compress` always adds the archive's own copy
   (`sources/ledger/calibration_observation_ledger.jsonl`, taken at the harvest, after both of the session's captures
   were written), and a missing path would make it return 5 (`ledger_unreadable`). A non-zero return is the tooling
   refusal `b6_restore_failed`.
3. **After-check** (exact: paths, sizes, times, digests). Before the restore and after the re-compression, the driver
   takes an inventory of every file under the session's runs roots, custody and archive, except the record directory
   `<archive>.desk` (which grows by design): relative path, size and modification time for every file, and SHA-256 for
   every file below `min_bytes` (those are never compressed, so any write to them shows). The two inventories must be
   equal, except that a `.zst` file's size may differ (its bytes need not be identical); for those, the record's
   latest event must be `compress` with the SHA-256 of the first `compress` row. A difference is the tooling refusal
   `b6_recompress_differs`. Checking only the compression record would miss a new or changed small file (§23 F4).
4. **Equivalence, plain against compressed** (a test; bar B1, exact). The fixture sessions (§16) are analysed
   twice: as harvested, before the desk compresses them, and compressed, through item 1. Every unit output must be
   byte-identical between the two after the projection of the release comparison (§13, 13-l). This is the test that
   would show a reader that sees anything other than the harvested bytes, and it is audit G4's release-time half.

The restored bytes are the harvested bytes, file by file. So L9's content addressing, and later the release re-run,
see identical inputs. `compression-summary.json` then describes the analysis's last compression; the desk's own
summary stays in the loop staging's `compression.json`, and every event stays in `compression.jsonl`.

*Not chosen.* Routing reads through `desk_compress.read_bytes` (the fifth pass's first version): most readers are
in files the analysis may not edit, and an editable caller does not make its callee editable (§23 F1). Restoring
one session per call through `RunState.invoke` (also that version): the calls that read two or three sessions and the
steps that bypass `invoke` defeat it (§23 F2). A copy of the sessions elsewhere: the plans and several bindings name
the sessions' original absolute roots (`whole_window.py` line 6553, `analysis_engine/inputs.py` line 895,
`mint_floor_artifact.py` line 1130). The fifth pass's first version also gave the launch-lineage locator as a
reason; that was wrong for block 6, whose hazard lineage authenticates the stamped lineage without the locator
(§23 F3). Plain restore: it does not fit (above). `desk_compress.read_bytes` remains the reader for the independent
recompute (§15 step 10).

*Cost.* A floor unit restores and re-compresses one session, a GAMMA unit three: 6 + 9 = 15 session cycles over the
nine sessions, each 32.75 to 38.82 GiB logical. The CLI prints per cycle the session, bytes restored (logical and on
disk) and seconds, and before the first one the free space (bytes and seconds are structure). The restore writes
into the only physical copy of the session bytes (audit F1). At every moment one verified copy of each file exists
(the restore checks the plain and the transparent copy before it removes the `.zst`; `compress` checks the `.zst`
before it removes the file), and the after-check proves the end state; the lead may still schedule the dry run after
audit F1's second copy exists (§15 step 8).

*Temporary space.* L9's block-5 bracket path rebuilds complete archived bundles under `$TMPDIR` (`bracket.py` line
173, consult Q5). Block 6 does not run it: `BLOCK6.window_bracket` reads the session's two captures, which are never
compressed (§4.8). The record carries each unit's peak `$TMPDIR` bytes.

Restoring writes into session directories, so the CLI refuses every root outside `$TMPDIR` when
`JW_B5_SYNTHETIC_ONLY=1` is set (§17).

### 4.2 The binding seam

`AnalysisBlock` carries every value L9 now binds to block 5:

| Field | Block 5 (`BLOCK5`) | Block 6 (`BLOCK6`) |
|---|---|---|
| `index_schema` | `joulewise.b5_window_index.v1` | `joulewise.b6_session_index.v1` |
| `seal_pins` | `configs/analysis/b5/seal_pins.json` | `configs/analysis/b6/seal_pins.json` |
| `pack_table` | `sealed_pack_table` (sizing_b5, `v5-b5-<pack>-a<n>-`) | the three block-6 pack files, session id grammar `r<k>-<pack>[-a<n>][-n<m>]` |
| `governing_pin(entry)` | pin1 to pin4 by seal and t0 | the commit the session's `harvest.json` names; any commit other than `f31aca19f` (S-1) is recorded (§4.9) |
| `record_shapes` | per pin, as L9 has them | the shapes the harvest at `f31aca19f` writes (taken from a fixture produced by that code, §16) |
| `catalog` | `configs/campaigns/v5_claim_25g83/flag_catalog.json` | `configs/b6/flag_catalog_b6.json` |
| `select(index, records)` | first claim-usable attempt per pack | the index names one session per pack in the unit; each must have analysis counting true |
| `usable(record)` | `claim_usable` true, `reasons == []` | analysis counting true (§4.6) |
| `kept_units(archive)` | `derived/exclusions.json` | the block-6 exclusions document from restricted custody, by digest (§4.5) |
| `allowance(archive, family)` | `whole_window.harvest_neg8_allowance_bracket` | REG §1.8 from `withheld/b6-neg8.json` (§4.7) |
| `screen_admission(row)` | the stored or survivor NEG-8 decision must have passed (`whole_window` admission and source replay) | the acceptance verdict and the b6 survivor screen (§4.7, §4.9) |
| `window_bracket(archive)` | `bracket.evaluate_window_bracket` (block 5's acceptance: corpus 24, cutoff 376) | block 6's acceptance from the session's two captures, issued fresh into consumption provenance (§4.8) |
| `gamma_midpoint_refuses` | true (B5-PLAN §2.4) | false (REG §8.2) |
| `verdict_row_answers` | as L9 (`dry_run._step_results`) | block 5's session-removing conditions and `neg8_bracket_*` answered as disclosed, once admission itself is the block's (§4.9) |
| `reharvest` | an analysed window harvested twice refuses (`reharvest_disclosure_record_required`) | allowed by REG §4; the account comes from the loop's `reharvested` entry and the session record's `harvest_history`, printed by `lines.history()` (§4.9) |
| `refusal_classes` | `configs/analysis/b5/dry_run_refusal_classes.json` | `configs/analysis/b6/dry_run_refusal_classes.json` |
| `custody_open` | true (D-173 opens in steps 9b and 10) | false (§18 D9) |
| `results_fill` | true | false (§18 D9) |
| `sentences` | L9's fixed sentences in `disclosures.py` ("window") | the same sentences with "session" for "window", and the cross-session line's label "agree within the statistical half-widths; timing bounds B not included" (REG §9.5 preamble, item 6); every block-6 string is a §11.3 template (§18 D24) |

**Binding sites.** Every call that reads one of these values goes through the block of the index it was given. The
seam is a policy seam, not only a constant table: screen admission, allowance acquisition and bracket evaluation are
behaviour, and the block supplies each as a function. The sites at L9 `1ab888a68` found by a grep (`SealPins.load(`,
`sealed_pack_table(`, `CATALOG_PATH`, `v5_claim_25g83`, `configs/analysis/b5`, `first_claim_usable`,
`select_analysed_attempts(`, `governing_pin(` outside `joulewise/b5/`, plus the midpoint check and the bracket
evaluator) are, with counts:

`joulewise/b5_analysis/windows.py` (14), `archive.py` (1), `kept_units.py` (2), `context.py` (2), `disclosures.py`
(3), `dry_run.py` (5), `bracket.py` (`evaluate_window_bracket`, `block_b_max_for_archives`),
`joulewise/analysis_engine/inputs.py` (2, and `require_contrast_attempt_keeps_midpoint`),
`joulewise/paper_reported_energy_issuer.py` (3), `scripts/extract_detection_floors.py` (3),
`scripts/mint_floor_artifact_generalized.py` (3), `scripts/build_results_fill_input.py` (2),
`scripts/produce_b5_disclosures.py` (2).

The consult (§19, F1) executed the paths a block-6 archive takes and found the policy sites the grep misses, all at
L9 `1ab888a68`: `joulewise/whole_window.py` lines 263, 333, 385, 414, 8056 and 8226 (screen admission, answered
conditions, source replay, allowance consumption); `joulewise/floor_extraction.py` line 3293 (allowance acquisition);
`joulewise/floor_mint_estimator.py` line 370 (a direct read of the stored bracket during lineage authentication);
`joulewise/b5_analysis/context.py` lines 30, 168, 211, 227 and 328 (stored screen, survivor descriptor, exclusions and
their digest); `joulewise/b5_analysis/bracket.py` lines 321 and 355 (block 5's acceptance corpus of 24 and cutoff
376); `scripts/mint_floor_artifact_generalized.py` line 2475 (the issued acceptance's allowance projection); and
`joulewise/b5_analysis/disclosures.py` line 705 (it iterates all three packs and reads GAMMA). Each routes through the block. The
builder re-runs the census on the merged base, where line numbers may move, and lists every site it binds.

Not bound, because block 6 does not run them: `joulewise/paper_custody.py`, `scripts/run_b5_analysis.py`,
`scripts/rehearse_b5_real.py`, `scripts/size_b5_window.py`, `scripts/write_b5_identity_pins.py`,
`scripts/digest_pin_census.py`, `scripts/collect_window_flags.py`, `joulewise/flags/*`.

**Two checks keep the seam honest.**

1. *Binding census* (a test): after the seam, the grep above finds the block-5 constants only in `block.py`.
2. *Equivalence replay* (a test, exact): L9's own production-shaped synthetic block-5 chain (the S10 fixture,
   `tests/b5_analysis/fixtures_s10.py`, driven through L9's real joined driver by its harness
   `tests/b5_analysis/joined_s10.py`) runs at L9's release tag and at the analysis commit. Whole-file digests
   cannot match, because L9 writes the analysis commit into the mint (`dry_run.py` 729, 735; minted cells record it,
   `mint_floor_artifact_generalized.py` 3229; issuance requires it to equal HEAD, 4508). So the test compares every
   output after a closed projection removes the provenance fields (the analysis and project commit and the paths
   derived from it), requires the rest to be equal (exact: identical inputs through identical arithmetic), and checks
   separately that each run's provenance names its own HEAD. The projection's field list is in the test and is
   reviewed with it. This is what "L9 at its release tag" means once the seam exists. Like L9's own S10 chain
   classes, the replay runs only on request (`JW_B5_S10_REAL_PROGRAMS=1`: `fixtures_s10.py` says it restores about
   8 GB and one joined run takes hours), never in the ordinary suite or CI. The build seat and the executing review
   run it and report its result.

Block 5's own dry run and release run from L9's release tag, never from the block-6 analysis commit (§18 D2). Its
`release_difference` check compares analysis commits, so mixing the two would refuse block 5's release.

### 4.3 Units

- **Floor unit**: one counting ALPHA or BETA session. Steps: L9 `0`, `1`, `2`, `3`, `3b`, `4` (that pack only),
  `10` (issue only, no custody open), then `11f`: the floor pack's disclosures through L9's per-pack line functions
  (kept units, battery-assist and load-correlated lines, battery, thermal, contention and clock counts, reference drift,
  monitor cost) plus the block-6 floor lines (§6). L9's `disclosures.py` iterates all three packs and reads GAMMA
  (line 705); making that iteration follow the unit's packs is one of its binding sites (§4.2). L9's `RunState` assumes
  all three packs in `prepare_brackets` (`block_b_max_for_archives`), `kept_bundles` (it iterates `PACKS`) and steps
  4, 10 and 11, so the floor unit uses a subclass in `driver.py` that overrides exactly those, with no change to L9's
  step functions.
- **GAMMA unit**: one counting GAMMA session `g` with its pairing (§5). It runs L9's step functions unchanged over the
  index {g, A(g), B(g)}: `0`, `1`, `2`, `3`, `3b`, `4`, `5`, `8`, `6`, `9`, `10` (issue only), `11` (disclosures only;
  no results-fill input). Steps 9b and the custody open of step 10 are not run (§18 D9).
- **Flagged-inclusive units.** The same units, built for each non-counting session that REG §11.4 admits (§11.4
  here), with the binding's usable predicate replaced by §11.4's test. They are marked `flagged_inclusive` in the
  record, and their outputs feed only the flagged-inclusive line.
- **Equalities between units (exact).** A floor session that appears in a GAMMA unit produces, in that unit, step-4
  and step-10 outputs byte-identical to its floor unit's. Each floor session's four dominance ratios R per model
  (REG §9.3) come from its floor unit, through `joulewise.dominance_closeout.dominance_ratio` on the extraction
  report's `floor.corner_widened_unguarded_floor_j` over `point_floor_diagnostic.unguarded_floor_j` (the `ratio` of
  the returned record); in each GAMMA unit, the close-out's R for that session equals them. Identical code on identical inputs, so bit identity is the property.

Order: floor units first, then GAMMA units, then the cross-block step (§14). The driver does not call L9's `run()`:
it builds one `RunState` (or the floor subclass) per unit in its own restricted directory, calls the step functions in
the unit's order, stops the unit at the first step that is not `ok`, and copies each `StepRecord` into the block-6
record.

### 4.4 The session index (block 6)

`binding.write_index(unit)` writes one `joulewise.b6_session_index.v1` file per unit into restricted custody (not
into the repository). Its entries use L9's `IndexEntry` fields: `pack`, `pack_id`, `attempt` (1; see below),
`plan_id` (= session id), `t0_epoch_s` (from the loop record), `seal` (`"b6"`), `entry_kind`
`"harvested"`, `archive_root` (the session record's `paths.archive`), `superseded_archive_roots` (the archives in the
session record's `harvest_history`, empty unless re-harvested), `harvest_record_sha256`, the four roots (from the
plan), `harvest_pin` (the commit `harvest.json` names, §4.9),
`verdict` (from `harvest.json`), `claim_usable` (the value the archive's harvest record holds, unchanged: L9 checks
the index against the archive, `archive.py` line 174, and refuses `window_index_disagrees_with_archive` when they
differ), `cause_key` null, and one block-6 field, `analysis_counting`, which `BLOCK6.select` and `BLOCK6.usable` read.
L9's `_complete_history` requires attempts 1..n without gaps: the index lists only the unit's sessions, each as
attempt 1 of its pack, so the history check is trivially met, and the pack's full attempt history is printed from
the loop record (§6, B5-PLAN §8.1 history line).

Item 53 would have stopped r2-gamma at four places, all now behind the binding: `select_analysed_attempts`
(`first_claim_usable`; with no usable GAMMA attempt, `block_incomplete`, `windows.py` line 289), `open_archive`
(`attempt_not_claim_usable`), `load_kept_units` (`exclusions_schema_invalid`) and
`require_contrast_attempt_keeps_midpoint` (`analysed_attempt_carries_midpoint_lost`). Writing counting into the index's
`claim_usable` would have added a fifth, `window_index_disagrees_with_archive`; the consult (§19, F3) reproduced all
five on synthetic records, which is why counting travels in its own field.

### 4.5 Kept units: the block-6 exclusions document (the item-53 fix)

*Forcing problem.* The block-5 harvest code wrote `derived/exclusions.json` with GAMMA's pack-scoped midpoint reason
(B5-PLAN §2.4, Q11). REG §8.2 drops that reason on GAMMA. The acceptance applied the block-6 rule
(`compute(..., pack_scoped=False)` in `joulewise/b6/acceptance.py`), and the loop counted r2-gamma; the archive's
document still says `claim_usable: false`.

*Rule.* `binding.b6_exclusions(archive)`:

1. Build the acceptance's inputs exactly as `joulewise.b6.session.accept_archive` does
   (`acceptance.evidence_from_archive`, `archive.ordered_roster`, the internal flags and spans), and add the flags in
   `derived/b6-flags.jsonl`. Rebuild the roster projection the acceptance hands to `compute`, not the archive's raw
   roster: one entry per run id in plan order, units from the blueprint where a member carries none, and
   `member.bytes_ambiguous` for a duplicated run id (`joulewise/b6/acceptance.py` `evaluate`, the `roster_members` and
   duplicate blocks).
2. Call the sealed `joulewise.flags.exclusions.compute(flags, roster, spans, b6_catalog)` with the roster's
   `pack_id` key removed. With no pack id, `PACK_SCOPED_WINDOW_REASONS` adds nothing, which is REG §8.2's rule. This
   needs no keyword that the frozen file lacks, so the analysis runs whichever version of `exclusions.py` the base
   carries (§15 step 3).
3. Apply the desk exclusion (§4.6): each run it removes enters `compute` as one more member flag through an
   in-memory overlay of the catalog with one added entry, `desk.graphics_pstar` (effect EXCLUDE_MEMBER, family
   PHYSICS_IN_SPAN). So the whole unit containing the run is removed, as REG §8.3 requires. The overlay's bytes and
   digest are written beside the document; the pinned catalog file is not changed (REG §8.1: the graphics line has
   no catalog code).
4. Checks before step 3 (all exact: integers, run-id sets and code sets):
   - `members_excluded` (run id and codes) equals the acceptance record's member entries of `excluding`, and every
     cell's kept count equals the acceptance record's `cells`. A difference is a tooling refusal
     (`b6_kept_units_differ_from_acceptance`): the acceptance is the registered judge, so the analysis may not keep
     a different set;
   - for a counting session, the document's `claim_usable` is true. A false value means a window reason the
     acceptance did not apply: tooling refusal;
   - `members_excluded` and every cell's `kept_units` against `derived/exclusions.json`. The pack-scoped reason only
     adds a window reason, so they should agree; the acceptance's own emitted member flags (for example
     `member.bytes_ambiguous`) can legitimately add to them, so a difference is a structure word in the record
     (`b5_exclusions_member_sets_differ`), not a refusal.
5. Write the document (schema `joulewise.exclusions.v1`, the sealed function's own output) to
   `restricted/b6/kept/<session>.json`; the index entry's kept-units binding names its digest.

The analysis never reads `claim_usable` or `reasons` from `derived/exclusions.json` (§12).

### 4.6 Counting, the desk exclusion, and analysis counting

*Counting (REG §4).* `sessions.counting_sessions(pack)` returns `joulewise.b6.queue.counting_ids(state, pack)` over
the loop record (it applies `reharvested` corrections). For each, the acceptance record must say `counting: true`
and `joulewise.session_structure`'s `counting_source` must be `b6_acceptance`; a disagreement is a tooling refusal
(`b6_counting_records_disagree`).

*The desk exclusion (REG §8.3 item 3, §8.5 graphics row, S-9, S-11; filled by B6-2).*

- *Scope.* Every science run of a counting session whose target phase has a registered T_phase: decode and
  prefill-p2048 runs, repeats and quad runs. Reference runs (`neg8-window-*`, GAMMA's interior references) and
  prefill-p42 runs have no registered T_phase and are outside the line (B6-2's decision 4).
- *P_x.* P_x = Σ_i (gpu_power_i + ane_power_i) × elapsed_i / Σ_i elapsed_i over the records i of the run's admitted
  idle baseline, `raw/powermetrics_idle.plist`: NUL-separated plist documents, with `processor.gpu_power` and
  `processor.ane_power` in mW (divided by 1,000) and `elapsed_ns`. These are the values the powermetrics adapter turns
  into the `gpu_power` and `ane_power` rails. For a run admitted at its second attempt the file is the admitted
  attempt's (B6-2 checked one such run byte for byte). The file is compressed in every session; it is read inside the unit's
  restore (§4.1).
- *Line.* E_add = P_x × T_phase, with T_phase the registered value for the run's pack and target phase (for GAMMA,
  the 8B runs' length: the registered grain is per pack and phase, §18 D11). The run is excluded when
  E_add ≥ F_min / 4 = 0.475 J, that is, when P_x ≥ P* = 0.475 J / T_phase; the unit containing the run goes with it.
  T_phase enters as the registration's exact decimal string (B6-2 computes P* from the exact stamp difference), so
  no rounded P* enters the comparison.
- *GAMMA's per-model line.* For GAMMA's 1.7B runs the line at their own length (S-11's 1.7B values, printed beside,
  not registered) is evaluated too. The structure record carries both counts. If they ever differ, each affected cell
  prints the per-model result beside the registered one as a labelled alternative (REG §12.4, last sentence).
- *No P_x.* A run whose idle file has fewer than 2 records has no P_x. Such a run is already removed by block 5's
  missing-idle-telemetry exclusion (REG §8.3 item 1). If a kept run has no P_x anyway, it stays kept and is counted
  as `pstar_unread` (a flag; the lead reads the count).

*Worked example (synthetic).* T_phase = 6.0 s, so P* = 0.0792 W. A run whose idle records all read 150 mW has
P_x = 0.15 W and E_add = 0.90 J: excluded. A run at 0.2 mW (the quiet rails, REG §8.5) has E_add = 0.0012 J: kept.
Two records, 100 mW over 0.25 s and 200 mW over 0.75 s: P_x = (25 + 150) mW·s / 1.0 s = 0.175 W, time-weighted (the
plain mean would be 0.150 W); E_add = 1.05 J: excluded. While the base lacks the S-11 fill, this step records
`pstar_unsized` in the structure record and the release-gating dry run cannot complete (REG §14 S-9: due before the
blind dry run).

*Analysis counting.* A counting session stays counting unless, after the desk exclusion, a target cell's stratum
keeps fewer than 5 units (REG §8.2 N3). Then it stops counting, its structure record says
`analysis_counting: false, cause: cell.below_minimum (desk)`, and pairing (§5) is computed on analysis counting.
Pairing then depends on an idle-baseline power, a hazard measurement, never on a science energy (REG §6.2). On the
77 rehearsal runs the line removes 0 runs (REG §8.3 item 3). B6-2's replay of the filled line over the nine counting
sessions (counts only) removes 0 of 840 science runs, and none reaches a tenth of the line. So no change of counting
is expected; the code path still has a fixture (§16).

### 4.7 The drift allowance (REG §1.8)

*Forcing problem.* L9's consumers read the allowance through `whole_window.harvest_neg8_allowance_bracket`, from the
block-5 harvest's NEG-8 record. Block 6's registered allowance is REG §1.8 (clean corpus of 6 or more, survivors
under the block-6 catalog, the midpoint's two-value fallback). The b6 survivor screen
(`joulewise/b6/survivor_screen.py`) records its inputs in `withheld/b6-neg8.json`: per family, the start, midpoint
and end means and the bound terms, but not the allowance itself.

*Rule.* `binding.allowance(archive, family)` = max(spread, bound_j), where bound_j is the screen's recorded
`bound_terms.bound_j` for that family and spread is the largest minus the smallest of the start mean, the midpoint mean
and the end mean, or |end mean − start mean| when the midpoint is lost (REG §1.8). Each run carries half of it, as in
block 5. The screen's family keys `gross` and `idle_subtracted` map to L9's `gross_energy` and
`idle_subtracted_energy`. Registered phase floors, rail cells and contrasts take `gross_energy`; request-energy
metrics take `idle_subtracted_energy` (`whole_window.py` line 2596), as in block 5.

*Check.* When the block-5 harvest's NEG-8 record is defined and its corpus and reference run-id sets equal the b6
screen's (`corpus_run_ids`, `reference_run_ids`), both allowances come from the same functions on the same energies,
so they must be equal (exact, float hex). A check against the block-5 harvest's allowance is possible only when
that one is defined at all: L9's loader returns a failed stored bracket and its admission then rejects it, and it
rejects a failed survivor bracket itself (§19, consult), so on many block-6 sessions there is nothing to compare and
the record says `b5_allowance_absent`. When the sets differ, the b6 value governs and the structure record says
`allowance_sources_differ` (a structure word, no number). An undefined b6 screen is REG §8.2 N2: the session does not
count, and the acceptance already says so. The analysis never re-runs the survivor screen on the session bytes (on
compressed archives it returns "undefined", audit F4); it reads the screen's record in `withheld/`, which the desk
never compresses.

*Independent oracle.* `joulewise/twins/harvest_twin.py` (main, PR #554) implements REG §1.8 (`session_drift`, whose
`member_drift_allowance_j` is half the gross family's allowance) and REG §1.7 (`calibration_bracket`) from the
registered text, without the production code. On the fixtures the tests compare the analysis's allowance per family
and its b_op (§4.8) with the twin's, at bar B3 (§17): it is a different implementation of the same arithmetic.

### 4.8 The operative timing bound

*Forcing problem* (§19, F2). REG §1.7 and §3.3 give block 6 its own b_op: max(opening, closing) + max(|closing −
opening|, 10.818 ms), from the session's own two captures. The block-6 harvest did not compute that bracket:
`scripts/harvest_b6_session.py` overrides only the catalog and the identity pins, the block-6 plans name no
`acceptance_path`, and so `_Harvest._acceptance_path` (`joulewise/b5/harvest.py` line 3820, the same at `f31aca19f`)
falls back to block 5's acceptance: by the code, the archive's stored bracket carries s_bracket 14.531 ms. (Read from
the code; no archive was opened. The dry run confirms it per session, below.) The acceptance, which decided counting, evaluated the bracket with block 6's
registration (`joulewise.b6.calibration`), so counting and the P3 stop line are unaffected; but a consumer that takes
the stored bracket would print block 5's larger b_op. *Worked example (synthetic, the consult's probe):* both
captures 28.0 ms: stored bracket 28.0 + 14.531 = 42.531 ms; registered b_op 28.0 + 10.818 = 38.818 ms. A second example
(REG §1.7 with block 6's s_bracket): opening 40.0 ms, closing 30.0 ms gives 40.0 + max(10.0, 10.818) = 50.818 ms.

*Rule.* `BLOCK6.window_bracket(archive)` builds the block-6 bracket from the session's two refitted captures
(`joulewise.b6.calibration.read_own_capture`) and block 6's acceptance (`configs/b6/registration/acceptance.json`), as
the acceptance did, and represents it as L9's complete `WindowBracket` (bound, both captures, the bracket screen, its
evaluation record). Its value must equal the acceptance record's `calibration` b_op (exact decimal string; a difference
is a tooling refusal). L9 issues each member's consumption provenance fresh from the context's bracket
(`whole_window.py` lines 1193, 1260, 1468), so `require_member_bound_is_window_bracket` passes once the context holds the
block-6 bracket; the stored bracket enters no number. The mint's lineage authentication (`floor_mint_estimator.py`
line 370) and the J6 b_max (§18 D10) read the same block-6 bracket. The structure record carries
`harvest_bracket_block5_acceptance`, true when the digest of the archive's `sources/inputs/acceptance.json` equals
block 5's acceptance file, so the difference is visible without a number.

### 4.9 The stored whole-window verdict row and the harvest commit

L9's consumers read the whole-window verdict row the harvest stored (`analysis_engine.inputs.archived_verdict_row`,
`whole_window.validate_whole_window_verdict_row`) and admit it only if its NEG-8 decision passed and every condition it
carries is answered (`whole_window.py` admission and source replay; `dry_run._step_results`, `answered_by`). In block 6
the row's NEG-8 bracket decision and its `neg8_bracket_*` conditions are disclosed only (REG §9.5 item 7: block 5's
0.05 J bar fails every session by construction), and block 5's other session-removing codes are flags (REG §8.2).
Answering the conditions with text does not cure the admission (§19, consult), so the block supplies admission itself:
`BLOCK6.screen_admission(row)` admits the row when the acceptance verdict counts the session and the b6 survivor screen
passed, and then answers each block-5 condition as `disclosed (REG §8.2, §9.5 item 7)`. The builder confirms on the
fixtures which conditions the real harvest writes, and lists them.

The harvest commit each session's `harvest.json` names is the S-1 commit `f31aca19f` unless the session was
harvested again (REG §4: a harvest fault is fixed and re-run on the same bytes). A different commit is recorded in the
structure record with the loop's `reharvested` entry beside it; it is a flag, not a refusal (records are flags), and
the lead reads it.

*Re-harvested sessions.* L9 refuses an analysed window whose index lists superseded archives
(`reharvest_disclosure_record_required`, `dry_run.py` line 1007), because block 5's index has no record of why the
second harvest decides. Block 6 has one: REG §4 says the re-run decides, the loop's `state.json` holds the
`reharvested` correction, and the session record's `harvest_history` names the earlier archives. So the index lists
those archives honestly (§4.4), `BLOCK6.reharvest` turns the refusal off, and `lines.history()` prints the account:
both archives' harvest commits and `harvest.json` digests, the loop's reason, and each archive's survivor count where
that archive has a b6 screen record, otherwise "none (harvest fault)". L9's own `reharvest_account` line is not used
for block 6: it needs a survivor count for the earlier harvest, which a faulted harvest does not have, and the line
must not invent one. Fixture B1 exercises this (§16).

---

## 5. GAMMA pairing (REG §6.2)

`sessions.pair(g, counting)` takes a counting GAMMA session `g` of round k and, for each floor pack P in (ALPHA, BETA),
the list of P's analysis-counting sessions with their rounds and t0. It returns (session, rule):

1. `same_round`: P's counting session of round k;
2. `later_round`: otherwise P's counting session of the smallest round greater than k;
3. `earlier_round`: otherwise P's counting session of the largest round smaller than k;
4. `block5`: otherwise block 5's analysed session of P, labelled "floor from block 5". This step reads block 5's
   floors, which exist only after block 5's release, so a pairing that needs it is computed in the cross-block phase
   (§14).

Ties (two counting sessions of P in one round, possible after a held pack is resumed): the earlier t0 (§18 D16).
Pairing reads only round, t0 and analysis counting. One floor session may serve several GAMMA sessions; every pairing
is printed with its rule. A GAMMA session's own counting does not depend on its pairing.

*When a pairing is final.* While sessions are still arriving, a pairing can change. GAMMA runs first in round 3's
order, so its same-round partner may not exist yet. Rule 3 applies only when no later counting session exists "at the
close" (REG §6.2). So before the loop's state is `DONE` with its `close` event, `pair()` works over the sessions
judged so far, and the record marks each pairing `final: false`. The release-gating dry run runs after the close
(§14), so its pairings are final. A GAMMA unit whose provisional pairing changes is built again from the start; it
carries nothing over (§18 D23).

*Worked example 1 (structure as recorded, RUN_STATE item 59: counting only, no energy).* ALPHA counted in rounds 1, 3,
4; BETA in 1, 2, 3; GAMMA in 1, 2, 3. GAMMA r1 → ALPHA r1 (rule 1), BETA r1 (rule 1). GAMMA r2 → ALPHA r3 (rule 2: no
ALPHA counted in round 2; r2-alpha never ran, item 52), BETA r2 (rule 1). GAMMA r3 → ALPHA r3, BETA r3 (rule 1). ALPHA
r3 serves two GAMMA sessions. ALPHA r4 serves none: it is a floor unit only, and its cells, floors and R are printed.
So there are six floor units and three GAMMA units.

*Worked example 2 (synthetic, exercising rules 3 and 4).* As example 1, but BETA r3 does not count and BETA has no
later counting session: GAMMA r3 pairs with BETA r2 (rule 3), which then serves GAMMA r2 and r3. Had BETA no counting
block-6 session at all, every GAMMA session would pair with block 5's BETA session, and each contrast's outcome line
and the replication sentence would print "floor from block 5".

---

## 6. REG §9.5: disclosures and labelled lines

Each counting session prints B5-PLAN §8.1's disclosures with "session" for "window". L9's disclosure producer prints
them per unit. What changes for block 6, and the new lines:

| REG §9.5 | Where | Block-6 specifics |
|---|---|---|
| preamble: kept units and positions of removed units | L9 `disclosures._kept_lines` | from the block-6 exclusions document; desk-excluded units carry the label `desk.graphics_pstar` |
| preamble: attempt history | `lines.history()` | block 5's attempts (block 5's index, structure) and the pack's block-6 attempts from the loop record, with outcome status and cause |
| preamble: battery, thermal, contention, clock counts; reference drift with realised counts; monitor cost; fixed sentences | L9 `disclosures` | unchanged; the GAMMA midpoint sentence (L9 `MIDPOINT_SENTENCE`) is printed for a GAMMA session with `neg8.midpoint_lost` (REG §8.2), where block 5 refused |
| 1 load-correlated physics sensitivity | L9 `_energy_lines` | unchanged. `contention.request_overlap` removes nothing in block 6, so only the two thermal codes can trigger it |
| 2 battery-assist line | L9 `_energy_lines` (cells, contrasts) and `lines.machine_without_assist()` | unchanged for rail cells and contrasts; also applied to the whole-machine per-phase value (§7, §8) |
| 3 scaled drift allowance | `lines.scaled_allowance()` | new; below |
| 4 single-step reconstruction diagnostic | the independent recompute | not computed by the analysis (REG: "computed by the independent recompute"); `crossblock` places the recompute's value beside the cell, labelled |
| 5 whole-machine energy per phase | `machine.py` | new; §8; ALPHA and BETA only |
| 6 cross-session consistency | L9 `_energy_lines` (cross-window check), per GAMMA unit, for each model and phase | G = mean over the GAMMA session's kept quads of that model's side mean, h_G = t(0.975, n − 1) × s / √n; F = that model's reported mean in the paired floor session, h_F its h (without B); "agree" when \|G − F\| ≤ √(h_G² + h_F²), which is L9's `math.hypot` test (`disclosures.py` line 440). The sentence is block 6's (`sentences`, §4.2): "session" for "window", with the label "agree within the statistical half-widths; timing bounds B not included"; otherwise the difference is printed as between-session variation the intervals do not cover |
| 7 block-5 codes carried | `lines.block5_codes()` | new; below |
| 8 waited runs | `lines.without_waited()` | new; below |
| REG §8.3 item 3, §8.5 "What is printed": outside-processor labelled alternative | `lines.outside_processor_alternative()` | new; below |

**Item 3, scaled drift allowance.** For a cell: factor = max(1, E / E_ref, T / T_ref). E is the cell's estimator-1
mean. T is the cell's mean phase length, by estimator 1's weights (0.2 × mean over kept repeats + 0.8 × mean over the
runs of kept quads). E_ref and T_ref are the plain means of the gross request energy and request length over the
surviving start, midpoint and end references that set the allowance (§18 D12). The line prints the allowance term
(half the allowance, as it enters B) times the factor, and B and the interval recomputed with it. For a contrast:
factor = max(1, E_a / E_ref, E_b / E_ref, T_a / T_ref, T_b / T_ref) on the allowance term of D, with E_a, E_b, T_a,
T_b the side means over kept quads. *Worked example (synthetic):* allowance term 0.40 J, E_ref = 37.2 J, T_ref =
4.1 s. A BETA prefill cell with E = 58.5 J, T = 0.95 s: factor max(1, 1.5726, 0.2317) = 1.5726, scaled term
0.629 J. A 1.7B decode cell with E = 25.5 J, T = 1.99 s: factor 1, unchanged. A contrast with E_a = 25.5 J, E_b =
85.0 J, T_a = 1.99 s, T_b = 6.6 s: factor max(1, 0.6855, 2.2849, 0.4854, 1.6098) = 2.2849, scaled term 0.914 J.
(REG §9.5 item 3's own example: 0.49 J × 8.108 = 3.97 J.)

**Item 6, cross-session consistency, worked example (synthetic).** G = 25.400 J, h_G = 0.300 J; F = 25.100 J,
h_F = 0.250 J: |G − F| = 0.300 J ≤ √(0.0900 + 0.0625) = 0.3905 J, so the line says "agree". With F = 24.850 J:
0.550 J > 0.3905 J, so the line prints the difference +0.55000 J as between-session variation the intervals do not
cover.

**Item 7, block-5 codes carried.** For each block-6 session: the codes in its flags (`derived/flags.jsonl` and
`derived/b6-flags.jsonl`) whose effect in block 5's sealed catalog (`configs/campaigns/v5_claim_25g83/flag_catalog.json`,
digest from `configs/analysis/b5/seal_pins.json`) is EXCLUDE_WINDOW, plus block 5's pack-scoped reasons
(`flags.exclusions.PACK_SCOPED_WINDOW_REASONS`: on GAMMA, `neg8.midpoint_lost` → `neg8.midpoint_lost_primary`),
minus the NEG-8 bracket decision and its `neg8_bracket_*` conditions (disclosed only, never listed as a carried
failure). Codes absent from block 5's catalog are listed separately as "not in block 5's catalog". Beside the list:
`harvest.json`'s `claim_usable` (structure; `session_structure` records it as `b5_harvest_claim_usable`). For
r2-gamma the line reads `neg8.midpoint_lost_primary` (the item-53 session, shown, not removed). A restricted code
(REG §12.1, D21) prints as "removed (restricted code)" in the blind record.

**Item 8, waited runs.** For each registered cell and contrast: the same estimator over the kept units with every unit
that contains an `idle.waited` run removed, printed as "without waited runs (n_r = …, n_b = …)" (contrast: "(n = …)"),
with the number of waited runs per stratum; below 5 units it carries "below the registered minimum of 5 units" and
decides nothing (the battery-assist line's form, B5-PLAN §8.1). d = +0.180 J (S-6) is below 0.475 J, so waited runs
stay in the registered value.

**Outside-processor labelled alternative (REG §8.3 item 3, §8.5).** For every cell and every contrast (a GAMMA
contrast is a cell of the exclusion function), and for every kept run: C = Σ of the monitor's
`outside_total` over the k accounting intervals that overlap its request (the quantity the harvest's contention join
reads, `joulewise.b5.harvest`; the journal, `hazards/monitor/contention.jsonl`, is compressed in every session and is
read inside the unit's restore, §4.1), excess = C − k × 0.54, E_add = 5.432 × max(0, excess). The alternative removes each
run with E_add ≥ 0.475 J (and its unit), recomputes the estimator (for a contrast, REG §9.4 steps 1 to 3 only: dbar and its metrology interval, no Holm
test, no floor decision, no outcome, as the battery-assist contrast line), and prints "registered outside-processor rule (w =
5.432 J per CPU-s, c_q = 0.54 CPU-s; 0.72 as measured with Spotify and the orphaned test process)" with the count of
runs removed, and, for each removed or `contention.request_overlap`-flagged run, C, k, excess and E_add. It never
replaces the registered value. *Worked example (REG §8.5):* C = 1.54 CPU-s over k = 2 intervals: excess 0.46 CPU-s,
E_add = 2.499 J: removed by the alternative, kept and flagged in the registered value. C = 0.95 over k = 2: excess
below 0, E_add = 0. The background-priority line (w = 0.0862) is not printed (§18 D14).

---

## 7. Battery assist (the MagSafe question, RUN_STATE item 65)

*What happens.* Under heavy load the machine draws more than the 140 W adapter supplies and the battery makes up the
difference while the adapter stays connected. This was measured on 2026-10-06 (B5-REG §9.2): in a 170 s load of 8B
plus a CPU burner, the SMC battery current B0AC was nonzero in 126 of the run's 536 SMC publications, all of them
inside the load phase, about 63 s of the 170 s, lowest −5,331 mA.

*Was it a problem?* For the numbers the paper claims, no. They are processor-rail energies (CPU, GPU and ANE), and
the rails are regulated downstream of the supply, so the sampler reads the same rail energy whichever source delivers
it. Removing assisted runs would have been the real bias, because assist happens exactly when load is highest, so the
kept means would drop, most for 8B. The ruling of 2026-10-06 (two blind seats, then the orchestrator) therefore made
discharge a disclosure (`battery.assist`), kept charging and AC loss as exclusions, and printed every cell with and
without assisted runs. 8B decode ran at 69.1 to 72.6 tokens/s under up to −5.3 A of assist against 68.9 to 71.1
tokens/s without. Block 6 carries all of this (REG §8.3 item 1, §9.5 item 2).

*Where it was a problem: the whole-machine line.* The wall meter sits on the adapter's cable, so it cannot see energy
the battery supplies. Block 5's request-level cross-check adds the battery term (ΔE_machine = ΔE_meter + ΔE_battery,
B5-PLAN §8.2). Block 6's per-phase line (REG §9.5 item 5) is meter-only, because the battery current is read once a
second and no reading falls inside 38% of prefill phases. So in an assisted phase the per-phase whole-machine value
reads low by the battery's share. The registration flags such phases but defines no value free of the gap.

*What this design does.*

1. Assisted runs are those carrying `battery.assist` (the registered member rule: a negative SMC read held into the
   request, B5-PLAN §8.1). `meter.battery_activity` (a nonzero B0AC read in the meter stream inside the request) is
   counted beside it.
2. REG §9.5 item 2 applies to "each estimate", so the whole-machine per-phase value is printed twice, like every rail
   cell: over all kept units, and over the kept units with no assisted run, with the count of assisted runs per
   stratum (`lines.machine_without_assist()`). The second value is free of the gap for every run whose battery state
   was observed, except for discharge in the last τ of a request (up to about 2.3 s), which the SMC reports only after
   the request ends (§7.1): such a run carries `battery.assist_outside_request`, stays in the second value as
   registered, and the count of such runs per stratum is printed beside it. A run whose request held no battery observation (`meter_battery_unavailable`, or no SMC read) cannot be
   called unassisted: it stays in both values as the registered membership has it, and the count of such runs per
   stratum is printed beside, so a reader sees how much of "without assisted runs" rests on missing observations.
3. Each run's request-level ΔE_machine with the battery term (block 5's definition) is printed beside, with the
   count of runs whose battery term was unavailable.
4. The boundary sentence is printed as registered ("DC input at the USB-C port; the adapter's AC-to-DC loss is not
   included."), followed by one added sentence: "Battery energy is not included in the per-phase value; phases whose
   request shows battery assist are counted and the value is also printed without them."
5. The ruling's reopening conditions (B5-REG §9.2: lower rail power, frequency or tokens per second in assisted
   against matched unassisted seconds; power-mode transitions with assist; a battery-temperature rise concentrated in
   assisted stages) are visible after the release in the battery-assist line (energy) and in the existing
   battery-temperature diagnostic. The analysis adds no new test for them.

How many block-6 runs carry `battery.assist` is structure (flag counts by code, REG §12.1); the blind dry run writes
it per session and cell (§14), so the lead can say how often assist happened without opening an energy.

### 7.1 The BAT-2 ruling (2026-10-21) and block 6

*What BAT-2 ruled.* It is a ruling for BYTES, which is not registered and has no data; every number in it comes from
the non-claim BYTES session H. BYTES' DC input over a decode span becomes the meter's energy plus the battery's signed
energy E_b = (T / n) × Σ P_b over the n meter polls received in the span, with P_b = −B0AC × B0AV / 10⁶ W from the SMC
values that each 0.2 s KM003C poll carries (`km003c_parse.Stream.battery_watts` and `integrate`'s rule, the reads
block 5's request-level ΔE_machine already uses). It measured how late those values are. The SMC publishes about once
a second (T_SMC = 1.0 s; median 1.002 s between changes on H), each value averages the second before it, and a poll
sees it up to one poll interval later. So energy that flows at time t is reported within (t, t + τ], with
τ = 2 × T_SMC + Δt_p and Δt_p the stream's own largest poll interval: 2.302 s on H, whose longest observed tail was
2.130 s. The attribution error of E_b is then at most v = v_start + v_end, where v_edge = (T / n) × Σ |P_b| over the
polls received in [edge, edge + τ). BYTES' without-assisted line keys on a decode-scoped marker (a negative B0AC
received in [d0 + τ, d1 + τ)), because the request-scoped `battery.assist` marked every 122B run of H on prefill
discharge reported late into decode. The ruling also amended BYTES' Addendum 1 item 2, so BYTES no longer takes
S-15's fill.

*Why block 6's per-phase value stays meter-only.* REG §9.5 item 5 registers it that way: meter energy per phase; "the
battery term … stays at request level, and a phase whose request shows the battery assisting the adapter is
flagged". S-15 fills only "its exact definition, including how the meter's clock-fit residual and the alignment bound
enter its uncertainty". Putting the battery inside the value would change registered arithmetic (REG §12.4: a dated
§17 entry, with the registered value printed beside). BAT-2's delay also shows what that would buy on a short phase.
When the phase is no longer than τ, every poll in it is received in [p0, p0 + τ), so v_start ≥ |E_b|, and the term
can never be told apart from zero within its own bound. The registration's reason, "read only once a second", is this
delay.

*What block 6 takes from it.* Two facts about the registered member rule (B5-PLAN §8.1: a run is assisted when an SMC
read below 0 mA is held into its request). Neither needs new arithmetic:

1. A run assisted only in prefill carries `battery.assist`, so its unit also leaves the decode cell's without-assist
   value, although its decode may have had no assist. That line is a description and selects nothing in the
   registered value, so it stays as registered. The per-run request-level ΔE_machine of §7 item 3 shows where the
   battery energy was.
2. Discharge in the last τ of a request is read only after the request ends. Such a run carries
   `battery.assist_outside_request` instead and stays in the without-assist value. The count of such runs per stratum
   is printed beside that value (§7 item 2); B5-PLAN §8.1 already counts the flag per session.

A phase-scoped marker like BYTES' was considered and not adopted (§18 D21). For a phase shorter than τ, its window
[p0 + τ, p1 + τ) lies wholly after the phase, so it would also mark the next phase's discharge.

*Worked example (synthetic).* τ = 2 × 1.0 + 0.302 = 2.302 s. A 1.7B prefill at [10.00, 10.40) s with polls at 10.10 and
10.30 s: both lie in [10.00, 12.302), so v_start counts both, and v_start ≥ |E_b| whatever the battery did. An 8B
decode at [10.40, 17.00) s whose request ends at 17.00 s discharges during [16.80, 17.00) s. With SMC publications at
16.00, 17.00 and 18.00 s, the first negative value is published at 17.00 s and read at 17.10 s, after the request
ends. So the run carries `battery.assist_outside_request`, not `battery.assist`, and is counted beside the
without-assist value.

---

## 8. Whole-machine energy per phase (REG §9.5 item 5, S-15)

*Finding.* REG §9.5 item 5 says the definition is "the one committed for block 5". L9 at `1ab888a68` commits only the
request-level cross-check of B5-PLAN §8.2 (`disclosures._machine_lines`, `km003c_parse.delta_machine_energy`), and
B5-PLAN §8.2 says "the harvest computes no phase-level figures". The per-phase line exists in the independent recompute
(`scripts/independent_recompute_b5.py` at `76f45da3e`: `machine_member`, `phase_machine_mean`, the edge-shift
corners), labelled "gross meter energy per phase; battery assist flagged at request level", which is item 37's 03:26
amendment. The analysis must implement the same definition independently, or REG §12.3 item 4 cannot pass on these
values.

The item brief points S-15 at `km003c_parse` and at L9's `disclosures.MACHINE_BOUNDARY` ("whole-machine DC input plus
the battery term, measured at the USB-C input; the adapter's AC-to-DC loss is not included."). That string is the
boundary of block 5's request-level line, which block 6 prints unchanged beside each run's ΔE_machine (§7 item 3).
REG §9.5 item 5 registers the per-phase value differently: meter only, the battery at request level, and its own
boundary sentence. So the per-phase definition below uses `km003c_parse`'s meter functions (`clock_fit`,
`raw_offset_ns`, `integrate` on the meter samples), not `delta_machine_energy`. The registration wins over the brief
(§7.1).

*Definition* (`machine.py`; the proposed S-15 fill, §15):

1. **Timeline.** Meter samples (Vbus × Ibus, 50 per second; the stream under `hazards/meter/` is compressed in every
   session and is read inside the unit's restore, §4.1) are placed on CLOCK_MONOTONIC_RAW by the stream's clock
   fit (`km003c_parse.clock_fit`, the lower-envelope line). A run's phase edges, stamped on its wall clock, are mapped
   to the same clock by the run's clock anchor (the midpoint of its wall-minus-monotonic bounds) plus the stream's
   raw-minus-monotonic offset (`km003c_parse.raw_offset_ns`; failing that, the hazard monitor's journal line nearest
   the phase, recorded as `meter_offset_from_journal`).
2. **Per-run value.** E_meter(phase) = mean power of the samples whose host time lies in [start, end) × (end −
   start), gross (`km003c_parse.integrate`). No sample in the phase, or no stream covering the phase: the run's value
   is absent.
3. **Per cell.** Estimator 1's arithmetic (REG §9.1 steps 1 to 3: m, V, h), per model and phase, ALPHA and BETA only,
   over the rail cell's kept units less any unit with an absent run value; the number of such units per stratum is
   printed (the recompute's `missing_units_by_stratum`). The rails' share is printed beside: the median over kept runs of gross rail energy ÷ gross
   meter energy for the same phase.
4. **Uncertainty from the timeline.** δ = b_op + r_max, where r_max is the largest height of any fit point above the
   fitted envelope (the meter's clock-fit residual). The cell mean is recomputed with every run's start edge moved by
   ±δ and end edge by ±δ, four corners, the same sign for all runs in a corner; the largest |change| of m is printed as
   "edge-shift sensitivity (b_op + clock-fit residual)". It is a sensitivity printed beside m ± h, not a term added to
   the interval. Three rules, as the recompute has them (`independent_recompute_b5.py` lines 1815, 1821, 1827): a
   shifted run is integrated on the stream that carried its unshifted value; a corner whose shift changes the cell's
   unit counts (an edge moved out of coverage) has no change, so that the sensitivity never compares different units;
   and the sensitivity is printed only when all four corners have a change, otherwise "not computed". *Why the second
   rule:* in the consult's synthetic probe, a lost repeat moved the mean from 42.120 to 42.121 J by dropping a unit,
   not by shifting an edge.
5. **Battery.** §7 items 1 to 4 and §7.1.

*Worked example (synthetic).* A prefill phase of 0.620 s holds 31 meter samples with mean 68.0 W: E_meter = 42.16 J.
Its request holds an SMC read of B0AC = −1,200 mA at B0AV = 12,600 mV, 15.12 W supplied by the battery, so the run
carries `battery.assist`; its unit is left out of the "without assisted runs" value. With b_op = 45 ms and r_max =
6 ms, δ = 51 ms; if the four corners move m by +0.41, −0.38, +0.05 and −0.02 J, the line prints 0.41 J.

*Block 5's value for REG §10.* The between-session summary needs block 5's per-phase value too. `machine.py` computes
it from block 5's archives in the cross-block phase, after block 5's release, with the same function (§18 D13); the
recompute's block-5 value is its comparison partner.

---

## 9. Estimators 1 to 4 (REG §9.1 to §9.4): unchanged, run by L9 per unit (§4.3)

Estimators 1 to 4 are block 5's, one counting session at a time; no run, unit or cell is pooled across sessions
(REG §9). The kept-unit issuer must equal `paper_reported_energy._project_cell` exactly on a complete cell (REG §9): a
test runs both on a complete synthetic cell and compares float hex.

---

## 10. The between-session summary (REG §10)

`crossblock.summary(Q, pack)`: for each printed quantity Q and pack, the values Q_j of block 5's analysed session and
of every counting block-6 session (each computed by §9 within its session), n = 1 + (counting block-6 sessions),

    Q̄ = (1/n) Σ_j Q_j,        s_Q = √( Σ_j (Q_j − Q̄)² / (n − 1) ).

Printed as "between-session summary (n sessions): mean, standard deviation". Nothing else: no ratio to a half-width,
no pooled interval, no test, no claim. The quantities (REG §10): each reported mean and per-token value, attribution
floor, operative floor, dominance ratio, dbar and energy ratio, and each whole-machine per-phase value. A per-token
value is computed per session and then summarized. For R the "session" is the floor session; for dbar and the energy
ratio, the GAMMA session.

*Edge cases.* n = 1 (no counting block-6 session of the pack): Q̄ = Q_1 and s_Q prints "not defined (n = 1)". A
session whose Q is not computable (for example a refused cell): left out, n reduced, and the line names it. A block-5
value that its analysis did not compute: n counts block-6 sessions only and the line says "block 5: not computed".

*Worked example (synthetic).* BETA's prefill-p2048 reported mean: block 5 58.40 J; three counting block-6 sessions
58.71, 57.96 and 58.83 J. n = 4, Q̄ = 58.475 J, s_Q = 0.388 J. The per-token values (÷ 2,048) are 0.02851562,
0.02866699, 0.02830078 and 0.02872559 J (58.40 / 2,048 is 0.028515625 exactly, a tie at 8 decimals; the float
rounds down, so 0.02851562 is printed); their summary is 0.02855225 J, standard deviation 0.00018955 J. GAMMA decode
dbar: block 5 +3.00 J; block 6 +2.84, +3.21, +2.95 J: n = 4, Q̄ = 3.000 J, s_Q = 0.155 J. A dominance ratio: 3.84, 3.51,
4.02, 3.77: Q̄ = 3.785, s_Q = 0.211.

---

## 11. Reporting rules (REG §11.1 to §11.4), written exactly

### 11.1 Side by side (`crossblock.side_by_side`)

For every quantity of REG §9 and each pack, one row per session: block 5's value, then each counting block-6
session's value, each with its interval (where the estimator has one), its kept units (n_r, n_b, or n) and its flags
(the session's flag codes with counts; restricted codes as such until the release). Then:

- Δ = (mean of the counting block-6 sessions' values) − (block 5's value);
- each block-6 session's own difference, Q_j − Q_block5;
- the between-session summary (§10);
- two fixed facts, printed with every table: "Block 6 makes record conditions flags; the rules for which runs and
  sessions enter differ between the blocks (REG §8)." and "Each block's own calibration acceptance sets its b_op:
  s_bracket 14.531 ms in block 5, 10.818 ms in block 6.";
- for each block-6 session, the item-7 line (§6).

*Same worked example:* block-6 mean 58.50 J, Δ = +0.10 J; own differences +0.31, −0.44, +0.43 J.

No Δ is printed when block 5's value is absent ("block 5: not computed") or no block-6 session counts ("no counting
block-6 session").

### 11.2 The replication word (`crossblock.replication_word`), per GAMMA contrast

Inputs: block 5's outcome word w5 and dbar5; for each counting block-6 GAMMA session j, w_j and dbar_j.

1. If w5 is `not_estimable` (no dbar): the word "replicated" is not used; print the sessions' words and signs.
2. Otherwise "replicated" when, for every counting block-6 GAMMA session j, w_j = w5 **and** sign(dbar_j) =
   sign(dbar5); else "not replicated", followed by each session's word and signed dbar.
3. A block-6 session whose contrast is `not_estimable` has no sign: it differs from any w5 other than `not_estimable`,
   so the contrast is "not replicated".
4. If GAMMA closed with fewer than 3 counting sessions (k and the short mark from the loop's `close` event, written
   when the loop state becomes `DONE`, `joulewise/b6/loop.py` `_next`, fields `counts` and `short`), the sentence adds "short: k counting block-6 sessions of the
   3 targeted" (and, below 2, "below the commitment of 2"). With k = 0 there is no replication sentence, only that
   line.
5. A pairing with rule 4 (§5) adds "floor from block 5" to that session's outcome line and to the sentence.
6. The flagged-inclusive sessions' words and signs are printed beside, labelled, and never enter the word.

*Worked example (synthetic).* Block 5 `direction_supported`, +3.00 J. Block 6 `direction_supported` +2.84,
`direction_supported` +3.21, `direction_supported` +2.95: **replicated**. Had the third been `unresolved` with +0.95:
**not replicated** (sessions: supported +2.84, supported +3.21, unresolved +0.95), although every sign agrees.

### 11.3 What may be said (`crossblock.SENTENCES`)

Every printed sentence about block 6 comes from one closed table of templates:

- a reported cell is an L1 instrument result; its interval is printed and not tested;
- a contrast reaches L2 only by REG §9.4 within its own session (its own outcome and leave-one-out), never from the
  replication word or the summary;
- "replicated" and "not replicated" describe agreement of outcome words and signs, and no template places an
  interval, p-value, "significant" or "confirmed" next to them;
- every between-session statement uses the §10 summary and states n ("(n sessions)").

A test asserts that every string the analysis prints for block 6 matches a template, and that no template breaks the
four rules.

### 11.4 The flagged-inclusive line (`crossblock.flagged_inclusive`)

Added back: each non-counting block-6 session that (i) ran the registered experiment, meaning none of
`model.files_differ_from_registered`, `model.stack_differs_from_registered`, `code.number_bearing_unreviewed`,
`structure.*` (REG §8.2 W1, W2, W3, S1), and (ii) can be computed: every target stratum keeps at least 5 units under
the run exclusions, b_op is defined (no N1), and the drift screen is defined (no N2). The session-level conditions P1 to
P4 and D1 are ignored for it; run exclusions, including the desk exclusion, still apply. A non-counting GAMMA session
pairs by §5 with analysis-counting floor sessions only (§18 D17).

Printed beside every registered result (each §10 summary, each replication sentence) as "including sessions that did
not count (n = …)", listing each added session with its session-level codes. It never replaces the registered value.
With no session added it prints "including sessions that did not count: none". *Worked example (synthetic):* the BETA
example of §10 plus a session removed by its drift screen that read 59.10 J: n = 5, mean 58.600 J, standard deviation
0.437 J, labelled as such.

**Printed precision** (`configs/analysis/b6/printed_precision.json`; §18 D15): energies in joules to 5 decimals, as
L9's disclosure lines print cells; ratios (R, ρ, the energy ratio, the scaling factor) to 4 decimals; per-token
energies to 8 decimals (÷ 512 or ÷ 2,048 moves a value down about three decimal places); counts as integers. This fixes
REG §12.3 item 4's "half a unit of its last printed digit": 5 × 10⁻⁶ J, 5 × 10⁻⁵ and 5 × 10⁻⁹ J. *Derivation.* The
project's agreement rule puts a bar between 10⁶ times float noise and 1% of the smallest printed half-width. Float
noise: 10⁶ × 2.2 × 10⁻¹⁶ × 1,000 J = 2.2 × 10⁻⁷ J for the largest energies. Smallest half-width: with 10 repeats and 10
quads, estimator 1 gives V = 0.04 s²/10 + 0.64 (s/2)²/10 = 0.020 s² for a run-to-run standard deviation s (a quad mean
of four runs has s/2), so h = 2.262 × √0.020 × s = 0.32 s. The smallest s in the non-claim rehearsals is 0.083 J (REG
§9.5 item 4, the single-step reconstruction; the ordinary assignment gives 0.379 J), so h ≥ 0.027 J and 1% of it is
2.7 × 10⁻⁴ J. 5 × 10⁻⁶ J lies inside [2.2 × 10⁻⁷, 2.7 × 10⁻⁴] J, and stays inside as long as the smallest printed
half-width exceeds 5 × 10⁻⁴ J (s above 0.0016 J). Per-token: the smallest per-token half-width is 0.027 J / 2,048 =
1.3 × 10⁻⁵ J, 1% of it 1.3 × 10⁻⁷ J, and 5 × 10⁻⁹ J lies above its float noise (10⁶ × 2.2 × 10⁻¹⁶ × 0.6 J = 1.3 ×
10⁻¹⁰ J). Ratios carry no interval; a ratio of two floors printed to 5 decimals of joules (floors of about 0.3 J and
up) is known to about 2 × 1.7 × 10⁻⁵ = 3.3 × 10⁻⁵ relative, 1.0 × 10⁻⁴ at R = 3, so 4 decimals print what the inputs resolve. Block 5's
renderer prints floors as exact decimals; in the block-6 tables they print to 5 decimals, so the half-unit bar is not
float noise. If the release-time check finds a smallest half-width below 5 × 10⁻⁴ J, the energy decimals move to 6.

---

## 12. `claim_usable`: every reader, and what it does on the block-6 line

Two different fields share the name. *Window-level*: a session (attempt) is usable for claims. *Cell-level*: a floor
cell of the aggregate floor artifact is claim-ready (`eligibility.claim_usable`). Item 53 concerns only the first.

| Reader | Which field | Block-6 behaviour |
|---|---|---|
| `joulewise/flags/exclusions.py` | window: `compute` writes `claim_usable = not window_reasons`; with the default `pack_scoped=True` a GAMMA `neg8.midpoint_lost` adds `neg8.midpoint_lost_primary`. `first_claim_usable` picks the first usable attempt | The harvest at `f31aca19f` writes `derived/exclusions.json` with block 5's meaning (item 53). The acceptance calls `compute(..., pack_scoped=False)`. The analysis calls `compute` with no pack id (same result, §4.5), never uses the file's `claim_usable` or `reasons` for block-6 eligibility (it reads them only to print them, §6 item 7 and the r2-gamma fields below), never calls `first_claim_usable`. Not edited |
| `joulewise/b5/harvest.py` (line 7460) | window: forms `harvest.json`'s `claim_usable` = the exclusions document's value and verdict COLLECTED | Written at harvest with block 5's meaning; the analysis keeps it in the index unchanged (§4.4) and never uses it for eligibility. Not edited (sealed) |
| `joulewise/session_structure.py` (block-6 line only) | window: reads `harvest.json` `claim_usable` into its counting reasons (line 252), then, when `derived/b6-acceptance.json` exists, discards those reasons and counts from the acceptance (line 266); records `b5_harvest_claim_usable` | All nine counting sessions have an acceptance record, so `counting_source` is `b6_acceptance`. The analysis requires that (§4.6) and prints `b5_harvest_claim_usable` in item 7 (§6). Not edited |
| `joulewise/analysis_manifest_v3.py` (block-6 line, line 3498) | cell: finalization selects aggregate-floor cells whose `eligibility.claim_usable` is true | Unchanged meaning, per GAMMA unit, on the aggregate floor minted from the paired floor sessions. Not touched by item 53 |
| `joulewise/detection_floor.py` | cell: the validator requires `eligibility.claim_usable` boolean and equal to `status == claim_ready` | Unchanged, per floor cell |
| `joulewise/dominance_closeout.py` (block-6 line, line 1909) | cell: a floor cell resolves only if `eligibility.claim_usable` is true | Unchanged, per GAMMA unit |
| `scripts/harvest_b5_window.py` | window: prints `claim_usable` from the harvest record | Not on the block-6 path: block 6 harvests through `scripts/harvest_b6_session.py`, which prints `counting`. The analysis never runs it |
| `scripts/mint_floor_artifact.py` | cell: writes `claim_usable: true` (v1 mint) | Not used: L9 mints with the generalized mint |
| `scripts/mint_floor_artifact_generalized.py` | cell: writes `claim_usable: true` on claim-ready cells | Used per GAMMA unit (L9 step 5); cell-level |
| `scripts/render_results_fills.py` | cell: requires the mint cell `claim_ready` and `claim_usable` | Not run by the block-6 analysis (§18 D9); when block-6 tables are rendered later, cell-level only |
| L9 `windows.select_analysed_attempts`, `archive.open_attempt_record` and `open_archive`, `kept_units.load_kept_units`, `analysis_engine/inputs.require_contrast_attempt_keeps_midpoint` (not in the item's list, but where item 53 bites) | window | Behind the binding: the index keeps the archived `claim_usable` so the index-against-archive check passes; selection and `usable` read `analysis_counting`; kept units from §4.5; midpoint check off (§4.2, §4.4) |

On L9's branch, `analysis_manifest_v3.py` and `dominance_closeout.py` no longer carry the cell-level check at the lines
above (it moved with L9's changes); the base of §15 step 3 decides which version runs, and the meaning stays cell-level
either way.

**The r2-gamma check.** No test may hold r2-gamma's real `exclusions.json`: that file names each excluded run's codes,
which REG §12.1 restricts. Instead: (a) a synthetic fixture shaped like
r2-gamma (§16, session G2), and (b) in the blind dry run on the real sessions, r2-gamma's structure record must read
`b5_exclusions_claim_usable: false`, `b5_reasons: ["neg8.midpoint_lost_primary"]`, `b6_exclusions_claim_usable: true`,
`acceptance_counting: true`, `analysis_counting: true` and `analysed: true` (structure only). The lead reads those
six fields.

---

## 13. Clause map (REG §9 to §11.4, §12 and §13)

One row per clause, in the registration's order, with the function that implements it and the test that shows it.
"e2e" is the end-to-end CLI test over the eleven synthetic sessions (§16; §17 stage B5). Every sentence of REG §9.5
to §11.4 and §13 that states a rule has a row. Rows for REG §4, §6.2, §8 and §12 cover the clauses those sections
need. Bars B1 to B4 are defined in §17.

| ID | REG clause | Function | Test |
|---|---|---|---|
| 9-a | §9: block 5's arithmetic, one counting session at a time; no run, unit or cell pooled across sessions | `driver.units()` (§4.3) | e2e: each unit's index lists one session per pack |
| 9-b | §9: GAMMA with the floors of its paired sessions (§6.2) | the GAMMA unit's index {g, A(g), B(g)} from `sessions.pair()` | e2e: three GAMMA units, paired as in §5 example 1 |
| 9-c | §9: the kept-unit issuer equals `_project_cell` exactly on a complete cell | L9's issuer, through `driver` | `test_issuer_equals_project_cell` (B1) |
| 9-d | §9: GAMMA's pack-file estimator-1 entry corrected when S-14 is pinned | the lead (§15 step 6) | — |
| 9.1 | §9.1 items 1 to 5: m, V, h, B, interval, per-token value, attribution floor beside | L9's issuer; floor unit step `11f` (§4.3) | REG §9.1 worked example as a unit test (B2); e2e against the oracle (B3) |
| 9.2 | §9.2: six floor cells per model, absolute and comparative; point, corner-widened and operative floors; guard | floor unit step 4 (L9's floor extraction) | REG §9.2 worked example (B2); e2e: six floor units |
| 9.3-a | §9.3: R per model, phase and form, with numerator, denominator and n, labelled "point diagnostic; no interval"; four R per model for each floor session | floor unit step 4's report, printed by step `11f` | e2e; B1: each floor session's R is equal in its floor unit and in every GAMMA unit (§4.3) |
| 9.3-b | §9.3: R_cm and the branch A or B sentence, once per GAMMA pairing | GAMMA unit step 6 (dominance close-out) | REG §9.3 worked example (B2); e2e |
| 9.4-a | §9.4 items 1 to 4: d_k, dbar, metrology interval, D, decision interval, t test, Holm over the two contrasts | GAMMA unit steps 8 and 9 (finalization, claim gate) | REG §9.4 worked example (B2); e2e |
| 9.4-b | §9.4 item 5: the floor gate from the paired floor sessions | GAMMA unit step 9, reading step 5's aggregate floor | e2e; unit test with a rule-3 pairing |
| 9.4-c | §9.4 items 6 and 7: outcome word in its precedence; leave-one-quad-out; the L2 ceiling | GAMMA unit step 9 | e2e: G3's word differs from G1's |
| 9.4-d | §9.4 item 8: the energy ratio with its t interval; dbar per token | GAMMA unit step 11 | e2e |
| 9.5-p1 | §9.5 preamble: kept units and the positions of removed units | L9 `disclosures._kept_lines` on the block-6 exclusions document; desk-excluded units labelled | fixture A4 |
| 9.5-p2 | §9.5 preamble: the pack's attempt history, block 5's and block 6's attempts | `lines.history()` | fixtures N1, N2 and B1 (re-harvested) |
| 9.5-p3 | §9.5 preamble: battery, thermal, contention and clock counts; reference drift with realised reference counts; monitor cost | L9 `disclosures`, per unit | e2e: every unit has a disclosure record |
| 9.5-p4 | §9.5 preamble: the fixed sentences, with "session" for "window" | `sentences` binding (§4.2) | `test_block6_templates` (§11.3) |
| 9.5-p5 | §9.5 preamble: none of the labelled lines changes a registered number | `lines` and `machine` write their own outputs and read the registered ones only | test: the registered outputs' digests are equal with and without the labelled-line steps |
| 9.5-1 | item 1: load-correlated physics sensitivity line | L9 `_energy_lines` | fixture A1 |
| 9.5-2 | item 2: each estimate also over the units with no battery-assisted run | L9 `_energy_lines`; `lines.machine_without_assist()` with the `battery.assist_outside_request` count (§7.1) | fixture B2 |
| 9.5-3 | item 3: scaled drift allowance, the cell factor and the contrast factor | `lines.scaled_allowance()` | §6's and REG's worked examples (B2); fixture |
| 9.5-4 | item 4: single-step reconstruction, computed by the independent recompute | not computed by the analysis; `crossblock` places the recompute's value | `test_single_step_is_read_not_computed` |
| 9.5-5a | item 5: meter DC-input energy per phase, gross, summarised with estimator 1's arithmetic per model and phase, with the rails' share | `machine.phase_energy()`, `machine.cell()` (§8 items 1 to 3) | §8 worked example (B2); fixture meter streams |
| 9.5-5b | item 5: the battery term at request level; a phase whose request shows assist is flagged | §7 items 1 to 3; `lines.machine_without_assist()` | fixture B2 |
| 9.5-5c | item 5: not given for GAMMA | `machine.cell()` for ALPHA and BETA only | e2e: no machine line in a GAMMA unit |
| 9.5-5d | item 5: the boundary sentence, printed every time | `sentences` (§7 item 4) | template test |
| 9.5-5e | item 5: the definition, with the clock-fit residual and the alignment bound in its uncertainty (S-15) | §8 item 4; the lead's S-15 fill (§15 step 7) | §8 worked example; fixture |
| 9.5-6 | item 6: G, h_G, F, h_F; "agree" when \|G − F\| ≤ √(h_G² + h_F²); the label | L9's cross-window check per GAMMA unit, with block-6 `sentences` | §6 worked example (B2); fixtures G1 (agree) and G3 (differ) |
| 9.5-7a | item 7: the block-5 session-removing codes each block-6 session carries, as flags | `lines.block5_codes()` | fixture G2 lists `neg8.midpoint_lost_primary` |
| 9.5-7b | item 7: the NEG-8 bracket decision and its `neg8_bracket_*` conditions disclosed only, never listed | `lines.block5_codes()` filter; `BLOCK6.screen_admission` (§4.9) | e2e: no session lists a `neg8_bracket_*` code |
| 9.5-8 | item 8: each registered cell also without its waited runs, labelled | `lines.without_waited()` | fixture B3 |
| 10-a | §10: the quantities (each reported mean and per-token value, attribution floor, operative floor, R, dbar, energy ratio, whole-machine per-phase value), per pack | `crossblock.summary()` over the list of printed quantity kinds | unit test: every quantity kind §9 prints has a summary row |
| 10-b | §10: block 5's analysed session and every counting block-6 session; n = 1 + counting block-6 sessions; Q̄; s_Q with divisor n − 1 | `crossblock.summary()` | §10 worked example (B2); unit tests for n = 1 and an absent block-5 value |
| 10-c | §10: nothing else (no ratio to a half-width, no pooled interval, no test, no claim); printed as "between-session summary (n sessions): mean, standard deviation" | `crossblock.SENTENCES` | template test |
| 11.1-a | §11.1: for every quantity of §9 and each pack, block 5's value and each counting block-6 session's value, each with its interval, kept units and flags | `crossblock.side_by_side()` | §11.1 worked example (B2) |
| 11.1-b | §11.1: Δ = (mean over counting block-6 sessions) − block 5's value; each session's own difference; then §10's summary | `crossblock.side_by_side()` | same |
| 11.1-c | §11.1: the two facts (different entry rules; each block's own b_op) printed with the table; §9.5 item 7 shown for each block-6 session | `crossblock.side_by_side()` | template test |
| 11.2-a | §11.2: "replicated" when every counting block-6 GAMMA session gives block 5's outcome word and sign of dbar; otherwise "not replicated", with each session's word and sign | `crossblock.replication_word()` | REG's and §11.2's worked examples (B2) |
| 11.2-b | §11.2: block 5's contrast `not_estimable`: "replicated" is not used; the words are printed | same | unit test |
| 11.2-c | §11.2 with REG §5.3: closed short, "short: k counting block-6 sessions of the 3 targeted", and below 2 the commitment line | same; k and the short mark from the loop's `close` event | unit test with a short GAMMA |
| 11.2-d | §11.2: the flagged-inclusive sessions' words printed beside, never entering the word | same | unit test with a non-counting GAMMA session |
| 11.2-e | REG §6.2: "floor from block 5" in the outcome line and in the sentence | `sessions.pair()` rule 4; `crossblock.replication_word()` | unit test with the block-5 stub |
| 11.3 | §11.3: a cell is L1, its interval printed and not tested; L2 only by §9.4 in its own session; "replicated" is not a test and carries no interval; between-session statements use §10 and state n | `crossblock.SENTENCES`, one closed table of templates | `test_block6_templates`: every printed string matches a template, and no template breaks the four rules |
| 11.4-a | §11.4 (i): ran the registered experiment (no W1, W2, W3 or S1) | `crossblock.flagged_inclusive()` | fixture N2 (W1) is not added |
| 11.4-b | §11.4 (ii): can be computed: at least 5 kept units per stratum, a defined b_op, a defined drift screen | same | fixture N1 (D1) is added |
| 11.4-c | §11.4: P1 to P4 and D1 ignored; run exclusions still apply, the desk exclusion included | same, with the binding's usable predicate replaced (§4.3) | fixture N1 |
| 11.4-d | §11.4: each added session listed with its flags; printed as "including sessions that did not count (n = …)"; never replaces the registered value | same; template | §11.4 worked example (B2); template test |
| 4-a | REG §4, §8.2 N3: counting from the loop and the acceptance; analysis counting after the desk exclusion | `sessions.counting_sessions()`, `sessions.analysis_counting()` | fixtures; unit test: a desk exclusion drives a stratum below 5 |
| 4-b | REG §4: a harvest fault is re-run on the same bytes, and the re-run decides counting | the session record's `paths.archive`; §4.9 | fixture B1 (re-harvested) |
| 6.2 | REG §6.2: rules 1 to 3; ties; one floor session serving several GAMMA sessions; final only at the close | `sessions.pair()` (§5) | §5 worked examples 1 and 2 as unit tests; a provisional-pairing unit test |
| 8.2 | REG §8.2: on GAMMA a lost midpoint is disclosed, with the fixed sentence | `BLOCK6.gamma_midpoint_refuses = False`; the block-6 exclusions document (§4.5) | fixture G2 analysed |
| 8.3-a | REG §8.3 item 3, §8.5: the graphics line P* per pack and phase, applied at the desk | `sessions.desk_exclusions()`; `binding.b6_exclusions()` step 3 | §4.6 worked example (B2); fixture A4; fixture G3's 1.7B run between the two lines |
| 8.3-b | REG §8.3 item 3, §8.5 "What is printed": the outside-processor rule as a labelled alternative, with C, k, excess and E_add | `lines.outside_processor_alternative()` | §6 worked example (B2); fixture G1 |
| 12.1 | §12.1: structure only before the release; restricted codes masked | `driver.record()` (§14) | no float token in the record; restricted codes masked |
| 12.1-b | §12.1: hidden-offset factors divided out before any number is printed | the export is never read; numbers come from the bundles (§4.1) | test: no `b6_analysis` module opens a path under `export` |
| 12.2 | §12.2: built and run blind on the real archives with only structure written out; code by models that read no block-5 or block-6 energy | `--mode blind-dry-run`; the brief's blind rule (§17) | the §12.1 record test; process |
| 12.3-a | §12.3 items 1 and 2: block 6 has closed; block 5's release event has happened | `--mode release` and the cross-block phase require the loop's `DONE` with its `close` event, and block 5's `B5-RELEASE-RECORD.json` by digest; otherwise exit 2 naming the missing condition | e2e: release mode with the loop not `DONE`, and with no block-5 record |
| 12.3-b | §12.3 item 3: the blind dry run over every session with no tooling refusal | `scripts/b6_analyze.py --mode blind-dry-run`, both phases | e2e |
| 12.3-c | §12.3 item 4, S-13: 1 mJ per run phase energy; half a unit of the last printed digit | `compare.py`; it refuses a recompute file that carries `trace_plist_missing` (§15 step 10) | unit test with a synthetic recompute file (B4), and one carrying `trace_plist_missing` |
| 12.3-d | §12.3: the release is a dated record tying the digests of the registration, the catalog and every block-6 harvest record; no separate cold gate | the §14 record carries those digests; the lead's dated record cites it (§15 step 11) | e2e: the record lists the registration's, the catalog's and every `harvest.json` digest |
| 12.4 | §12.4: a §8 rule changed while blind applies to every session, with the original rule's result beside | process: a dated REG §17 entry with one executing refuter; none exists at this design's date, so no switch is built | — |
| 13-a | §13: for each counting session, B5-PLAN §3.1 steps 1 to 11 | L9's step functions per unit (§4.3) | e2e |
| 13-b | §13: strict validation and re-reduction of every kept run | L9 steps 1 and 2 per unit, inside the unit's restore (§4.1), from the claim runs root | e2e on desk-compressed fixture sessions; `test_compressed_equals_plain` (B1); restore unit tests |
| 13-c | §13: the kept units from the session's exclusions | `binding.b6_exclusions()` (§4.5), never the archive's `claim_usable` | fixture G2; member sets and cell counts equal the acceptance record (B1) |
| 13-d | §13: floor extraction for each ALPHA and BETA session | floor unit step 4 | e2e: six floor units |
| 13-e | §13: per GAMMA pairing, the aggregate floor record and the dominance close-out | GAMMA unit steps 5 and 6 | e2e |
| 13-f | §13: per GAMMA session, finalization and the claim gate, given the paired floor sessions | GAMMA unit steps 8 and 9 | e2e |
| 13-g | §13: reported energy per cell; descriptive estimates and disclosures | L9's issuer and step 11 per unit; floor units' step `11f` | e2e; `test_issuer_equals_project_cell` |
| 13-h | §13: then §9.5, §10 and §11 | `driver` order: units, then `lines` and `machine`, then `crossblock` (§4.3, §14) | e2e: the step records are in that order |
| 13-i | §13: L9 at its release tag plus the five additions (pairing, summary, side by side, replication word, flagged-inclusive line) | the binding seam with its census and equivalence replay (§4.2); `sessions.pair()`; `crossblock` | `test_binding_census`, `test_block5_equivalence` |
| 13-j | §13: synthetic fixtures and full-size production-shaped archives through the real stage chain | the §16 generator at the S-1 code; the CLI in separate processes | e2e (on request, §16); unit-level tests |
| 13-k | §13: independent executing review; one blind executing cold pass by Fable and one by Opus; S-14 pinned before the blind dry run | process (§15 steps 5 and 6) | — |
| 13-l | §13: every output content-addressed; after the release a re-run from identical bytes, every digest equal to the dry run's | L9 `RunState.register`, `release_difference`; `driver` for the block-6 outputs | `test_release_equals_dry_run` |

---

## 14. Blind output layout (structure only)

```
<custody>/
  b6-dry-run/  (or b6-release/)
    B6-BLIND-DRY-RUN-RECORD.json    public: structure only
    restricted/
      logs/
      b6/sessions/<session>.json    counting, desk exclusions, allowance check, b_op check (restricted copy)
      b6/kept/<session>.json        block-6 exclusions documents and the catalog overlay
      units/<unit id>/              one L9 RunState custody per unit (index, outputs, disclosures)
      b6/lines/, b6/machine/        §6 to §8 outputs
      b6/crossblock/                §10, §11 outputs (cross-block phase only)
```

The record (`joulewise.b6_blind_dry_run.v1`) holds: mode; analysis commit; digests of the registration file, the
loop record, every session's `harvest.json` and acceptance record, `registered_constants.json`, the catalog and the
acceptance file;
per session: id, pack, round, t0 (integer epoch seconds), loop status, acceptance counting, analysis counting and its
cause, `analysed` (whether a unit analysed it), the harvest commit, `harvest_bracket_block5_acceptance`,
`b5_allowance_absent`, `b5_exclusions_claim_usable`, `b5_reasons`, `b6_exclusions_claim_usable`, kept units per cell and stratum
(integers), desk-excluded run count, `pstar_unread` count, GAMMA's per-model line count, `battery.assist` run count per
cell, allowance check word, b_op check word, the archive's name (`archive` or `archive.reharvest-<n>`), per restore
cycle (§4.1) the unit, return codes, files restored, bytes restored (logical and on disk) and seconds, and per unit the
after-check word and the peak `$TMPDIR` bytes; the pairing table (session ids, rule words,
`final`); per unit, L9's step records (step, status, exit status, refusal token,
output names and digests); the block-6 step records; `cross_block` status (`ok`, or `not_run` with
`block5_not_released`); `completed_without_tooling_refusal`.

Before writing, the record passes L9's structure test: no float token (`dry_run._FLOAT_TOKEN`) anywhere, codes
derived from a science energy or phase duration (REG §12.1, D21) masked as "removed (restricted code)", and an
outcome-class refusal shown only as "outcome-class refusal at step N".

**Two phases.** *Per-session phase* (any time, block 5 need not be released): floor units, GAMMA units, §6 to §8.
`cross_block` reads `not_run`. *Cross-block phase* (after block 5's release event): `crossblock` reads block 5's
release record (`B5-RELEASE-RECORD.json`), authenticates every output it uses by the digests in that record, and runs
§10 and §11. **The dry run that satisfies REG §12.3 item 3 is a full run that includes the cross-block phase**, so its
output digests are the ones the release re-run must reproduce (§18 D18).

---

## 15. Plan: S-14 and S-15 (the lead runs this after merging L9)

1. **Merge L9 into main** at its release tag (outside this item).
2. **S-11 and S-9: merge B6-2.** B6-2 filled both from each pack's first non-claim smoke, by the registered rule, with
   one blind executing refuter and a dated REG §17 entry (`lane/2026-10-22-b6-s9-s11`, `9715af399`, docs only). The
   lead merges it into main before the build's base is cut. The build then copies T_phase and P* per pack and target
   phase into `configs/analysis/b6/registered_constants.json` as the registration's exact decimal strings, with
   GAMMA's 1.7B values beside them marked not registered (§3, §4.6).
3. **Base branch.** `lane/<date>-b6-analysis-build` = main (with L9) merged with the block-6 line
   (`lane/2026-10-17-b6-packs-registered`, `1706257c4`, or its successor). A trial merge on 2026-10-21 (main
   `ef520743c` + L9 `1ab888a68`, then + `1706257c4`) conflicts in exactly three files; a repeat on 2026-10-22 (main
   `81db9f355` + L9 `195d2d405`, then + `1706257c4`) gives the same three conflicts and the same frozen-file result
   below. `joulewise/whole_window.py`: take L9's version and re-apply the block-6 line's whole delta to it,
   `git diff 3bb305d7a 1706257c4 -- joulewise/whole_window.py` (`3bb305d7a` is the merge base of L9 and the block-6
   line): 31 changed lines from `6ae3965bf` and `0276a3327`, among them the busy-only admission in the shared
   environment validator and the whole-window core check;
   `configs/gates/hazard_refusals.json` and `configs/pins/registry.json` (regenerate with their census tools). L9's `tests/b5_analysis/test_frozen_files.py`
   will then report five files that the block-6 line changed after L9 froze them (found by running the test's own
   digest list against the trial-merged tree, 388 frozen paths): `joulewise/b5/harvest.py` (code-table entries, two
   arm-flag pass-throughs, the NEG-8 comparison tolerance; merged digest `1b08dfe4…` against pin4's `68d21947…`),
   `joulewise/flags/catalog.py` (the DRAFT_CODES block), `joulewise/flags/core.py` (13 added lines),
   `joulewise/flags/exclusions.py` (the `pack_scoped` keyword) and `scripts/run_campaign.py` (the block-6 waiting
   admission and busy-only admission; a number-bearing path covered by `configs/b6/executing_reviews.json`). The guard
   on the analysis line is amended to accept exactly these five merged digests, each with its source commit range.
   Whether the deltas change anything on block 5's inputs is tested, not assumed: the equivalence replay (§4.2) must
   show block-5 bytes unchanged. The merge brings these deltas in; nobody writes a new line in a `joulewise/b5/*.py`
   file. This is stage B0 of the build (§17) unless the lead does it; if git cannot merge any other file cleanly,
   stop.
4. **Build** by the brief (§17), stages B0 to B5.
5. **Executing review** (a non-author model that runs the fixtures and the CLI), then **two blind executing cold
   passes**, Fable 5.1 and Opus 5.5 (REG §13).
6. **S-14 pin.** The merged commit is the analysis commit; a dated REG §17 entry names it. In the same entry, GAMMA's
   pack file estimator list is corrected (REG §9: GAMMA does not print estimator 1, so its `reported_phase_energy`
   entry is removed from `configs/b6/packs/gamma/registration.json` on the analysis line; no program reads the field).
7. **S-15** (whole-machine per phase): the lead checks L9's release tag for a per-phase definition. If one exists, S-15
   is that definition and commit, and `machine.py` calls it. If not (the state at `1ab888a68`), S-15 is filled by a
   dated REG §17 entry adopting §8 of this file, citing the recompute commit that implements it for block 5
   (`76f45da3e` or its successor), with one executing refuter (REG §12.4). The §7 additions (the without-assist value
   and the boundary's second sentence) are part of that fill; the recompute lane adds the without-assist value so that
   REG §12.3 item 4 covers it. The BAT-2 ruling amended BYTES' Addendum 1 item 2, so S-15's fill binds block 6 only.
   If the lead reads the brief's "DC input plus the battery term" as asking for the battery inside the per-phase
   value, that changes registered arithmetic: a REG §17 entry under §12.4 with one executing refuter, BAT-2's E_b and
   v as the definition, and the registered meter-only value printed beside. §7.1 gives its cost on phases shorter
   than τ.
8. **Per-session blind dry run** on the Mac (blinded data never goes to a cloud seat): `scripts/b6_analyze.py --mode
   blind-dry-run` over the nine sessions. It restores each unit's sessions in place as transparently compressed files
   (§4.1) and uses CPU and disk, so it runs only while no session is armed, between windows. The restore keeps 20 GiB
   free beside each file it writes; the CLI prints each session's logical and on-disk bytes. Before the run, the lead
   compares those with `df -g /Users/edr`. A `restore_space` refusal is cured by freeing disk, never by deleting
   session bytes. The restore rewrites files of the only physical copy (audit F1), each step verified (§4.1); the
   lead may wait for F1's second copy before running it. Each tooling refusal is cured blind and the run repeats until none
   remains. The lead reads only the structure record, including r2-gamma's six fields (§12).
9. **After block 5's release event:** the full dry run including the cross-block phase; this is REG §12.3 item 3.
10. **Recompute agreement** (`compare.py`, REG §12.3 item 4, S-13) for block 6's printed quantities. The independent
    recompute needs a block-6 mode (nine sessions, the pairing, the §10 and §11 quantities, §8's without-assist
    value, and reading compressed files, since it too reads raw files); that is a recompute-lane item, named here
    because the release needs it. Audit F4 found that the recompute, when `raw/powermetrics.plist` is missing (as it is
    on every compressed session), integrates `power_trace.csv` instead and raises only `trace_plist_missing`, which does
    not stop its comparison. That CSV comes from the same capture code as the analysis's inputs, so the check would no
    longer be independent: a 1% fault planted in both the CSV and the stored energies raised no mismatch when only the
    `.zst` existed. The block-6 mode must read the plist through `desk_compress.read_bytes`, and `trace_plist_missing`
    must stop the comparison (audit F4's plain fix) before `compare.py`'s result counts for REG §12.3 item 4.
11. **Release** (REG §12.3): the dated record; then `--mode release` reproduces every dry-run digest.

---

## 16. Fixture specification

*Rule.* Every fixture is generated by code, never copied from a real archive. The archives must have the shape that
the real ones have, so the generator runs the **measurement code at the S-1 commit** (`f31aca19f`): a `git archive`
export of that commit, the real block-6 loop composition (`joulewise/b6/compose.py`), the real chain and driver and
the real harvest (`scripts/harvest_b6_session.py`), with only the hardware replaced (the seams of L9's S10 producer,
`tests/b5_analysis/fixtures_s10.py`, and of `tests/b6/round_support.py`: mock model runtime, synthetic powermetrics
XML, synthetic battery, meter and monitor journals, no launchd). The analysis under test runs from the build branch,
in separate processes through `scripts/b6_analyze.py`. The fixtures use their own synthetic
`registered_constants.json`, with T_phase and P* set at synthetic values.

*Desk compression and re-harvest, as in the real sessions.* After each synthetic harvest the generator runs the
desk's compression from the same export (`desk_compress.compress` with the arguments `desk_lane.py` passes and the
real `min_bytes` of 1 MiB). The synthetic sampler files, telemetry, hazard journals and meter streams are written at
the real record sizes and rates over a full-length session, so the files the real desk compresses are compressed in
the fixtures too. `PROVENANCE.md` lists the compressed-file count per session and per category of §1, and the
end-to-end test requires every category of §1 to be compressed in at least one fixture session (the category names are
in the test; they are structure). The generator keeps each session's plain state until the first analysis of it has
run, for the plain-against-compressed equivalence (§4.1 item 4): either a copy taken before compression in the cache,
or an analysis run between harvest and compression. One session is re-harvested (B1,
below), so its archive is `archive.reharvest-1` and the loop's `state.json` carries its `reharvested` entry.

*Where the archives live.* Full-size archives are generated, never committed. They are cached under the seat's
scratch TMPDIR through `JW_B6_ANALYSIS_FIXTURE_CACHE` (L9's `JW_B5_S10_CHAIN_CACHE` is the model), and the classes
that need them run only on request (`JW_B6_ANALYSIS_REAL_PROGRAMS=1`), never in the ordinary suite or CI.
`tests/fixtures/b6_analysis/` holds only `PROVENANCE.md` (the export commit and every seam) and the small unit-level
fixtures. Before a cold build the seat checks `df -g /Users/edr`, and it reports the build's bytes and wall time
afterwards.

*Size.* Full size: ALPHA and BETA sessions 125 runs, GAMMA 107 (REG §3.1), 10 planned units per stratum, corpus 18,
start, midpoint and end references.

*The sessions* (eleven): three counting sessions per pack in the round structure of §5 example 1 (A1, A3, A4; B1,
B2, B3; G1, G2, G3), plus two that do not count:

| Session | Shape |
|---|---|
| G2 | **r2-gamma's shape**: the midpoint reference lost (fails admission), no other window reason. The harvest's `exclusions.json` must read `claim_usable: false`, `reasons: ["neg8.midpoint_lost_primary"]`, and the acceptance `counting: true` |
| A1 | one repeat removed by `thermal.os_level_nonzero` (item 1) and one quad removed by `member.anchor_not_bounded` |
| B1 | harvested twice: the first harvest fails with an injected `HARVEST_FAULT`; the loop's `reharvest` restores the source bytes and writes `archive.reharvest-1`; counting comes from the re-run (REG §4) |
| B2 | four 8B prefill-p2048 runs carry `battery.assist` (two repeats, two in different quads), with meter streams whose B0AC is negative inside their requests and a run whose request has no SMC read (`meter_battery_unavailable`). One of the four is assisted in prefill only, with its negative reads arriving within τ into decode (its unit leaves the decode without-assist value by the registered rule). One further 8B run discharges in the last 0.2 s of its decode, read only after the request ends (`battery.assist_outside_request`: it stays in the without-assist value and is counted beside it, §7.1). Each discharge is at least 1 J (the attribution limit) and at least bar B5 |
| B3 | two runs admitted after waiting (`idle.waited`) |
| A4 | one run whose idle baseline holds GPU power above P* (the desk exclusion removes its unit); A4 still counts |
| G1 | one quad with an outside-processor excess (C = 1.54, k = 2: E_add 2.50 J) and one flagged run below the line |
| G3 | a contrast whose outcome word differs from G1's and G2's (exercises "not replicated"); an 8B side mean shifted from its paired BETA r3 cell by more than the two statistical half-widths (the cross-session line says the sessions differ; in G1 they agree); and one 1.7B decode run whose P_x lies between the registered line and the 1.7B per-model line, so the registered line removes its quad and the per-model line keeps it (the labelled alternative prints, §4.6) |
| N1 (ALPHA, round 2) | does not count: drift screen failed (D1); computable, so it enters the flagged-inclusive line |
| N2 (BETA, round 4) | does not count: model files differ (W1); not added to the flagged-inclusive line |

Plus a block-5 stub for the cross-block phase: a synthetic `B5-RELEASE-RECORD.json` with the output files it names,
built by L9's own S10 chain (block-5 binding), so the cross-block phase reads real block-5-shaped outputs.

*Synthetic worlds.* The generator sets each effect so that the rule it tests acts above the bar that judges it (the
project's rule: a method difference is caught by making the synthetic world exercise it, never by tightening the bar):
the assisted runs differ from their siblings by at least 10 times the agreement bar of their cell, so "with" and
"without" differ visibly; the same for waited runs, the desk-excluded run, the outside-processor run and the thermal
unit; the GAMMA midpoint excursion in G2 is planted so that the two-value spread differs from the three-value one; the
between-session spread of each quantity is planted at a known value; reference energies about 37 J over about 4 s and
8B cells large enough that the §6 scaling factor exceeds 1 for 8B prefill and for the contrasts. The generator writes,
beside each archive, its own expected values computed by a separate small oracle in the test (not by the analysis).

*Unit-level fixtures* (no archive needed): pairing examples 1 and 2, and a provisional pairing before the close; a
desk exclusion that drops a stratum below 5; `not_estimable` in block 5; n = 1; a short GAMMA; a synthetic recompute
file for `compare.py`; and, on a small synthetic session tree compressed by the desk's `compress` with `min_bytes`
lowered so small files are compressed (§4.1): the restore of every row with its digest checks, and a row whose
decompressed digest differs (`b6_restore_failed`); on macOS, each restored file carries `UF_COMPRESSED` and reads back
its row's SHA-256 (skipped where `ditto` is absent); `complete_bundle_sha256`, strict validation and `reduce` on a
plain, a compressed and a restored bundle (compressed differs, restored equals plain); a compressed campaign log,
which `load_campaign_log_rows` reads as empty, and the same log restored; an interruption after restoring, the next
run's recovery; the after-check on a new four-byte file and on a changed small file written into the session tree;
and `restore_space` through the module's injectable `statvfs`.

---

## 17. Sol build brief (B6-1 build)

You are a Codex seat (gpt-6.1-sol, effort xhigh). This is claim-path code written blind: open no real archive, no
path under `/Users/edr/night-b6/`, `/Users/edr/night-custody/`, `/Users/edr/night-archive/b5-*` or any block-5
restricted path. Read this file in full first.

**Authority, in order:** (1) the registration, `docs/registrations/block6_replication_DRAFT.md` on main; (2) the
rulings it cites, and B5-PLAN and B5-REG where the registration says "unchanged"; (3) this design. Where they disagree,
the higher one wins; report the disagreement under "decisions I made". Decide anything these texts determine.
NEEDS_RULING only for a choice that changes which data count or a printed number; record it with its evidence and
continue with the rest.

**Base.** Branch `lane/<date>-b6-analysis-build`, created by the lead per §15 step 3. If the launch message says the
base does not exist yet, build it in stage B0. Check `git rev-parse HEAD` against the commit the lead gives; stop if it
differs.

**Seat setup.** Fresh TMPDIR; `JW_B5_SYNTHETIC_ONLY=1` in every test and CLI process (the project's safety switch for
synthetic-only runs; never point a test or the CLI at a real archive or key directory); never set
`JW_REAL_METER_SMOKE` or `JW_LIVE_HW` (they enable tests that read the live meter or SMC);
`/opt/homebrew/bin/python3.13` (in a cloud seat, the seat setup's python3.13). No `cd` in any shell command; use absolute paths and `git -C`. Do not run the whole suite: CI runs it on
the draft PR; run only the modules you touched plus the registry tests below. Check `df -g /Users/edr` before every
fixture build and every on-request run (seat TMPDIRs are disk).

**Root guard (build it first, in B3).** `scripts/b6_analyze.py` restores and re-compresses session bytes in place
(§4.1). With `JW_B5_SYNTHETIC_ONLY=1` set, it must refuse (exit 2, before reading anything) every `--loop-root`,
`--sessions-root` and `--custody` that does not resolve to a path under `$TMPDIR`; a test shows the refusal. The real
roots are run only by the lead, without the switch.

**No silly numbers (binding).** Every tolerance, threshold or assertion on a measured or derived quantity carries its
derivation in a comment beside it. You do not choose a bar; use these:

| Bar | Value | Derivation |
|---|---|---|
| B1 exact | equality (`==`, float hex for floats) | where bit identity is the property: integers, run-id and code sets, digests, words; the equivalence replay (identical inputs through identical arithmetic, provenance fields projected out, §4.2); one floor session's outputs in two units; per-session R against the close-out's R; the issuer against `_project_cell` on a complete cell; the two allowances when the survivor sets are equal; b_op against the acceptance record; restored and re-compressed files against their compression rows (SHA-256); registered constants against the registration text (exact strings); the after-check inventories (§4.1 item 3); every unit output on plain against compressed fixture sessions (§4.1 item 4) |
| B2 worked examples | half a unit of the last digit printed in this file's or the registration's example | the expected value is known only to that precision |
| B3 analysis against the test oracle or the harvest twin on synthetic archives | 1% of the cell's smallest printed half-width h for an energy with a half-width; otherwise 10⁻⁶ relative | the project's agreement rule: between 10⁶ × float noise (2.2 × 10⁻⁷ J at 1,000 J) and 1% of the smallest printed uncertainty |
| B4 release comparison (`compare.py`) | each run's phase energy within 1 mJ; every printed quantity, unrounded, within half a unit of its last printed digit (§11: 5 × 10⁻⁶ J, 5 × 10⁻⁵, 5 × 10⁻⁹ J) | REG §12.3 item 4, S-13 (registered); the observed agreement is printed beside and never used as the bar |
| B5 synthetic effects | each planted effect at least 10 × the B3 bar of its cell | so that a method difference cannot hide under the bar |

**Stages** (one branch, commit and push after each; push a first commit early):

- **B0, base** (only if the lead has not done it): the merge of §15 step 3, resolved by exactly the rules there. Any
  other conflict: stop and report.
- **B1, binding seam.** `joulewise/b5_analysis/block.py`; every binding site of §4.2 reads through
  `block_for_index`; `tests/b6_analysis/test_binding_census.py`; `tests/b6_analysis/test_block5_equivalence.py` (L9's
  S10 chain through its joined-driver harness `tests/b5_analysis/joined_s10.py`, at L9's release tag and at your head:
  equal outputs after the provenance projection of §4.2, bar B1). Done
  when both pass and the L9 tests that
  import an edited file pass unchanged (CI runs all of `tests/b5_analysis/` on the draft PR).
- **B2, fixtures.** The generator of §16 (desk compression and B1's re-harvest included) and the eleven archives plus
  the block-5 stub, in the on-request cache (§16); `PROVENANCE.md`. Report the bytes and wall time of a cold build.
- **B3, sessions and binding.** The root guard; `driver.restored()` (§4.1: the restore into transparently compressed
  files, the re-compression through the desk's `compress`, the after-check), with its unit-level tests and
  `tests/b6_analysis/test_compressed_equals_plain.py`; `sessions.py`
  (session records, counting, the desk exclusion of §4.6, pairing), `binding.py` (§4.4 to §4.9), floor units in
  `driver.py` with their step `11f`; `configs/analysis/b6/*.json`. Done when the six floor units and N1's
  flagged-inclusive unit run on the fixtures with no tooling refusal, every §4.1, §4.5 and §4.8 check holds, the
  floor units' outputs are byte-identical on plain and compressed sessions, the allowance and b_op match the harvest
  twin (B3), and every fixture session is compressed again afterwards. Report each session's logical and on-disk
  restore bytes and seconds.
- **B4, GAMMA units and lines.** GAMMA units (§4.3), `lines.py`, `machine.py`. Done when the three GAMMA units run,
  G2 is analysed with the midpoint sentence, and every §6 to §8 line matches the oracle (bars B2, B3).
- **B5, cross-block, comparison, CLI.** `crossblock.py`, `compare.py`, `scripts/b6_analyze.py`, the record of §14;
  the end-to-end test (on request, §16) runs the CLI in separate processes over the eleven sessions in both phases,
  then `--mode release`, and asserts equal digests, equal outputs on plain and compressed sessions (§4.1 item 4),
  and that every session is compressed again with its original file digests.

**WRITE_SCOPE (exhaustive).**

- New modules: `joulewise/b5_analysis/block.py`; `joulewise/b6_analysis/__init__.py`, `sessions.py`, `binding.py`,
  `driver.py`, `lines.py`, `machine.py`, `crossblock.py`, `compare.py`; `scripts/b6_analyze.py`.
- New configuration: `configs/analysis/b6/seal_pins.json`, `registered_constants.json` (T_phase and P* copied from
  the registration's S-11 and S-9 rows when the base carries B6-2's fill, otherwise null), `dry_run_refusal_classes.json`,
  `printed_precision.json`.
- Binding sites (edits that route a block-5 binding, a constant or a policy such as screen admission, allowance
  acquisition, bracket evaluation, usability or pack iteration, through the block object, and nothing else; with the
  block-5 binding every output must stay as it was, which the equivalence replay checks):
  `joulewise/b5_analysis/windows.py`, `archive.py`, `kept_units.py`, `context.py`, `disclosures.py`, `dry_run.py`,
  `bracket.py`; `joulewise/analysis_engine/inputs.py`; `joulewise/paper_reported_energy_issuer.py`;
  `joulewise/whole_window.py`, `joulewise/floor_extraction.py`, `joulewise/floor_mint_estimator.py` (the policy sites
  of §4.2); `scripts/extract_detection_floors.py`, `scripts/mint_floor_artifact_generalized.py`,
  `scripts/build_results_fill_input.py`, `scripts/produce_b5_disclosures.py`.
- Tests: `tests/b6_analysis/**` (new); `tests/fixtures/b6_analysis/**` (new: `PROVENANCE.md` and the small
  unit-level fixtures only; full-size archives stay in the on-request cache and are never committed);
  `tests/b5_analysis/test_frozen_files.py` only for the §15 step 3 amendment and only in stage B0.
- Registries, each only to add the rows its test names for the new modules or sites:
  `tests/test_battery_float_sweep.py` (`READERS`: a row for each new file that reads `b_fiducial_s`, classification
  "bracket rows", gate "outside the derivation scope: block-6 analysis reads its session's own b_op");
  `configs/gates/hazard_refusals.json` (run `python3.13 -m tests.hazards.refusal_census`; a new module that a scanned
  module imports goes into `scan.modules` or into `scan.not_scanned` with reason `analysis`; never BASELINE);
  `tests/hazards/test_import_graph.py`; `tests/flags/test_flags_import_graph.py`; `tests/b6/test_catalog.py` (expect no
  change: the catalog file is pinned); `tests/test_fixture_orphan_census.py`; `tests/test_digest_pin_census.py`;
  `tests/test_schemas.py` (expect no change). The inventory tests L9's own stages had to join (precedents in
  brackets): `tests/fixtures/custody_read_replay_allowlist.json`, one row per new call that passes a read-replay mode
  to a custody reader that `tests/test_custody_mode_inventory.py` censuses (L9 S9, `af36e8292`);
  `tests/test_single_count_discipline_census.py`, a manifest row for each new reader of the single-count discipline
  (L9 S10, `d5e5a0ffd`); `tests/test_authentication_io.py`, only to move the line numbers of its existing
  `path:function:line:call` rows in files you edit, or to classify a new read or write in a file it scans, with the
  reason beside it (L9 `67bdea4a7`).
- `tests/b6_analysis/__init__.py` uses the `load_tests` loader of `tests/b5_analysis/__init__.py` (the shard runner
  finds the tests only through it).
- In stage B0 only: `configs/pins/registry.json`, and `joulewise/whole_window.py` and `configs/gates/hazard_refusals.json`
  for the merge resolution of §15 step 3 (both are also in scope later, for the seam and its census rows).

**Never edit:** any `joulewise/b5/*.py` listed in `configs/campaigns/v5_claim_25g83/sealed_inventory.json`;
`configs/b6/flag_catalog_b6.json`; `configs/b6/registration/*`; `configs/b6/packs/*` (the lead corrects GAMMA's
estimator entry at the pin); `joulewise/b6/*.py` (the analysis imports them; a defect there is reported, not fixed);
any path in `joulewise/b6/registration.py` `NUMBER_BEARING_PATHS`; `joulewise/flags/*`; `joulewise/paper_custody.py`;
`joulewise/desk_compress.py` (the analysis imports its `status` and `compress`, and its restore follows `restore`'s
per-row procedure with the `ditto` step added, §4.1); `joulewise/twins/*` (the tests import the harvest twin as an
oracle). Do not use `scripts/restore_run_to_scratch.py` or `desk_compress.read_bytes` for any analysis step (§4.1,
*Not chosen*).
If a file outside this scope is needed, name it in the report and continue with the rest.

**Always run:** the modules you touched, the `tests/b5_analysis/` modules that import a file you edited (CI runs
the rest on the draft PR), `tests/b5_analysis/test_frozen_files.py`, `tests/b6/test_catalog.py`,
`tests/hazards/test_refusal_allowlist.py`, `tests/hazards/test_import_graph.py`,
`tests/flags/test_flags_import_graph.py`, `tests/test_battery_float_sweep.py`, `tests/test_fixture_orphan_census.py`,
`tests/test_digest_pin_census.py`, `tests/test_schemas.py`, `tests/test_custody_mode_inventory.py`,
`tests/test_single_count_discipline_census.py`, `tests/test_authentication_io.py`, `tests/test_d165_rationale_census.py`,
`tests/test_shard_tests.py` (a new test package must keep the shard union equal to the discover set);
`tests/flags/test_number_coverage.py` and `tests/hazards/test_physics_coverage.py` (they name functions and tests in
`whole_window.py` and `floor_extraction.py`; a seam edit renames none of them, and `configs/flags/number_rows.json`
and `configs/gates/physics_rows.json` are not edited); and the test modules of each library file you edit:
`tests/test_whole_window.py`, `tests/test_whole_window_selection.py`, `tests/test_floor_extraction.py`,
`tests/test_floor_mint_estimator.py`, `tests/test_mint_floor_artifact_generalized.py`,
`tests/test_mint_floor_artifact_generalized_d165.py`, `tests/test_analysis_inputs.py`,
`tests/b5_analysis/test_issuer.py`, `tests/b5_analysis/test_disclosures.py`. Environmental failures (`/private/tmp`, launchd,
powermetrics, fixture `git commit` exit 128) are listed, not chased.

**Report** (first line your model id): commits; tests run with counts; the cold-build wall time of the fixtures;
decisions I made; NEEDS_RULING (or "none"); every L9 or block-6 defect found, with the fixture that shows it.

---

## 18. Decisions made by the author

- **D1.** One seam (`AnalysisBlock`) instead of a block-6 copy of L9's driver: two copies would drift, the defect the
  project removed from `flags/exclusions.py` on 2026-10-06. The seam carries policy as well as constants (screen
  admission, allowance, bracket, usability, pack iteration), because the consult showed constants alone cannot open a
  block-6 archive (§19, F1). The equivalence replay is the price.
- **D2.** Block 5's dry run and release run from L9's release tag; block 6's from the S-14 commit. L9's
  `release_difference` compares analysis commits, so the two blocks cannot share a run.
- **D3.** Units: a floor unit per counting ALPHA or BETA session, a GAMMA unit per counting GAMMA session (§4.3). A
  floor session serving no GAMMA session (ALPHA r4) still gets its cells, floors and R.
- **D4.** Kept units from the sealed `compute` with no pack id (§4.5). It reproduces REG §8.2 without the `pack_scoped`
  keyword, so the result does not depend on which `exclusions.py` the base carries.
- **D5.** Counting is the loop's, confirmed by the acceptance, re-tested for N3 after the desk exclusion (§4.6).
- **D6.** The allowance is REG §1.8's from the b6 screen record, delivered to every L9 consumer through the block
  (extraction, mint, claim gate, issuer, admission); the block-5 harvest's allowance is a cross-check where it exists
  (§4.7).
- **D7.** b_op from block 6's acceptance and the session's own captures, built as a complete bracket and issued into
  consumption provenance; the harvest's stored bracket, computed with block 5's acceptance, enters no number (§4.8).
- **D8.** The GAMMA midpoint refusal is off for block 6 and the fixed sentence printed (REG §8.2).
- **D9.** The paper-custody opens (L9 step 9b, the open half of step 10) and the results-fill input are not run for
  block 6. They admit paper inputs for block 5's placements; block 6's tables have no placement yet (placement is the
  orchestrator's call), and its numbers are protected by content addressing, the release re-run and the recompute.
  A later placement lane adds them with block-6 roles.
- **D10.** L9's J6 sensitivity (b_max) runs per GAMMA unit over its three sessions, labelled "per pairing".
- **D11 (revised in the fourth pass).** T_phase and P* are keyed by (pack, target phase), as REG §8.3 item 3 ("set
  per pack and phase") and B6-2's fill have them; GAMMA's value is its 8B runs' length, so the line is stricter for
  its 1.7B runs than their own length would make it. The per-model count is kept as structure and printed as a
  labelled alternative if it ever differs (§4.6). The earlier reading of this file, each run's own model, is dropped:
  the registration governs. On replay both readings remove 0 runs (B6-2).
- **D12.** E_ref and T_ref of the scaled allowance: plain means of gross request energy and request length over the
  start, midpoint and end survivors; T of a cell by estimator 1's weights.
- **D13.** The per-phase whole-machine value is computed for block 5 too, after its release, by the same function, so
  REG §10 has its n.
- **D14.** The background-priority outside-processor line (w = 0.0862) is not printed: REG says "may", and the table
  already carries the registered alternative.
- **D15.** Printed precision as in §11, with its derivation there; it is a printing choice, and it is what makes
  S-13's half-unit bar a real number instead of float noise.
- **D16.** Pairing ties go to the earlier t0.
- **D17.** A non-counting GAMMA session in the flagged-inclusive line pairs only with analysis-counting floor
  sessions.
- **D18.** The release-gating dry run includes the cross-block phase and so runs after block 5's release.
- **D19.** The session index keeps the archived `claim_usable` and carries counting in its own field (§4.4, §19 F3).
- **D20.** The equivalence replay compares outputs with provenance projected out, and checks provenance on its own
  (§4.2, §19 F4).
- **D21.** From the BAT-2 ruling, block 6 takes no new arithmetic. The per-phase value stays meter-only, as REG §9.5
  item 5 registers it; the battery-assist line keeps B5-PLAN §8.1's member rule. The one addition is a printed count
  of `battery.assist_outside_request` runs beside the whole-machine without-assist value (§7.1). A phase-scoped
  marker like BYTES' was not adopted: for a phase shorter than τ its window lies wholly after the phase.
- **D22 (revised in the fifth pass).** A unit's sessions are restored in place as APFS transparently compressed
  files for the whole unit, checked file by file, and compressed again with the desk's own `compress` after it
  (§4.1). Readers at every step, most of them in files the analysis may not edit, open plain paths, some over three
  sessions in one call, so nothing narrower than the unit's sessions works (consult F1, F2, §23); plain restore of a
  GAMMA unit needs up to 129.29 GiB free against 69 GiB. Not chosen: routing reads through `desk_compress.read_bytes`
  and restoring per call (the fifth pass's first version, refuted by its consult); editing the sealed readers; copies
  elsewhere (several bindings name the original absolute roots).
- **D23.** A pairing is final only at the close; before it, pairings are computed over the sessions judged so far and
  marked `final: false` (§5).
- **D24.** Block 6's printed sentences are a binding (`sentences`, §4.2): REG §9.5 asks for "session" for "window"
  and item 6 registers its own label, which L9's sentences lack.
- **D25.** The harvest twin is the independent test oracle for the allowance (REG §1.8) and b_op (REG §1.7), at bar
  B3; the acceptance record stays the exact check for b_op (B1).
- **D26.** The equivalence of every unit output on plain and compressed sessions is a test of the analysis (audit G4's
  release-time half, which the audit recommended), not a per-session gate: the restore and the desk's `compress` already
  check every file's digest, so a per-session replay would carry no news (the audit's own reasoning).

**For the lead.** Five things. (1) S-15 (§15 step 7) changes no registered number, but it fills a slot by adopting a
definition that no block-5 analysis commit holds, so it is the lead's call with a REG §17 entry. (2) By the code at
`f31aca19f`, the block-6 harvest stored each session's bracket with block 5's acceptance (s_bracket 14.531 ms, not the
registered 10.818 ms; §4.8). Counting is unaffected, because the acceptance evaluated b_op with block 6's registration,
and the design keeps the stored bracket out of every number; the dry run's structure record confirms it per session.
(3) The BAT-2 ruling put the battery term into BYTES' DC input. Block 6's registered per-phase line stays meter-only
(§7.1). If you want the brief's "plus the battery term" inside the per-phase value, it is a REG §12.4 entry (§15
step 7). (4) REG §5.1 says the desk compresses raw files "after the harvest and the independent recompute"; the loop
at `1706257c4` compresses right after the harvest and acceptance, before any recompute. The compression is verified
and restorable file by file, so no number changes, but both the analysis (§4.1) and the recompute's block-6 mode
(§15 step 10) must read compressed files. This is a records difference, a flag, not a rule change. (5) Audit F4's
plain fixes (exempt `hazards/`, `campaign_log.jsonl` and `.git/` from future compression; restore the 36 `.git` files;
`trace_plist_missing` stops the recompute) leave this design valid either way: the restore only touches rows whose latest event is `compress`.
The recompute's stop is a precondition of REG §12.3 item 4 (§15 step 10). Nothing else here needs a ruling.

---

## 19. Consult round

One round with a blind Sol 6.1 xhigh seat, as the item allows. Codex Cloud could not provision an environment
(`snapshot_materialization_failed`, `gateway_unavailable`), so the seat ran locally through `codex-run-v3` on the idle
Mac, read-only, told that real blinded data exists on the machine and forbidden every `/Users/edr/night-*` path. It
read the design at `1185ad470`, ran 174 existing tests (62 block-6, 112 L9) and synthetic probes, reproduced the trial
merge, and re-derived every worked example (all correct at their printed precision). Its findings and what this file
did with each:

| # | Finding (seat's verdict) | Disposition |
|---|---|---|
| F1 | blocker, confirmed: the grep census is right but the seam also needs policy sites in `whole_window.py`, `floor_extraction.py`, `floor_mint_estimator.py`, `context.py`, `bracket.py`, the mint and `disclosures.py`; "constants and nothing else" cannot implement the behaviour | adopted: §4.2 lists the sites, the seam carries policy, the WRITE_SCOPE adds the three library files (D1) |
| F2 | blocker, confirmed: the block-6 harvest stored its bracket with block 5's acceptance; a synthetic probe gives 42.531 ms against the registered 38.818 ms; L9 issues consumption provenance fresh, so a correct context can pass | adopted: §4.8 rewritten (D7), and the lead is told |
| F3 | blocker, confirmed: writing counting into the index's `claim_usable` adds a fifth refusal, `window_index_disagrees_with_archive` | adopted: §4.4 keeps the archived value and adds `analysis_counting` (D19) |
| F4 | should fix, confirmed: the analysis commit is written into the mint and checked against HEAD, so whole-file digests cannot match across commits | adopted: the replay compares projected outputs and checks provenance separately (§4.2, D20) |
| F5 | should fix, confirmed: three recompute rules for the edge-shift sensitivity were missing; "without assisted runs" is "without recorded assist" | adopted: §8 item 4, §7 item 2 |
| F6 | should fix, confirmed: floor units had no disclosure route; L9's producer reads GAMMA | adopted: step `11f`, `disclosures.py` pack iteration bound (§4.3) |
| F7 | should fix, confirmed: the precision derivation used a wrong smallest half-width | adopted: §11 derives the smallest half-width (0.027 J) and shows the bars inside the window (D15) |
| F8 | nit, confirmed: `session_structure.py` reads the harvest field before the acceptance overrides it; `b5/harvest.py` line 7460 forms it; "never reads" should be "never uses for eligibility" | adopted: §12 |

Also confirmed by the seat and folded in: removing the roster's `pack_id` reproduces REG §8.2 with the sealed
function, and a synthetic replay reproduced the acceptance's member codes and cell counts exactly (§4.5, with the
roster projection it named); the b6 screen record suffices for the allowance, with the family-key mapping now in §4.7;
the dominance ratio's fields are `floor.corner_widened_unguarded_floor_j` over
`point_floor_diagnostic.unguarded_floor_j` (`floor_extraction.py` lines 1430, 1493), and `dominance_ratio` returns a
record whose `ratio` is the value; L9 commits only the request-level whole-machine line. Not run by the seat: the
full-size joined S10 chain.


## 20. Second pass (2026-10-22)

A re-check of this file against the item's acceptance list, by the author, blind as before. Changes: the clause map
gains rows for REG §12.2, §12.3 items 1 and 2, §12.4 and the four §13 clauses it had folded into one row (strict
validation, kept units from the session's exclusions, floor extraction, reported energy and disclosures); §11.2 takes
k and the short mark from the loop's `close` event; the build brief adds the three inventory registries L9's own stages
had to join (custody read-replay allowlist, single-count discipline census, authentication IO census), the tests that
name functions in the seam's library files, and the test modules of those files; the equivalence replay names L9's
joined-driver harness, added after `1ab888a68`; the §10 per-token example prints 0.02851562 (the exact value is a tie
at 8 decimals and the float rounds down, so a test at bar B2 would have failed on the old digit).

## 21. Third pass (2026-10-22)

A re-check against the item's acceptance list and against what changed since the second pass, blind as before.

- **BAT-2.** The battery ruling of 2026-10-21 (BYTES) came after the draft and cites it. §7.1 states what it ruled,
  why block 6's registered per-phase value stays meter-only (REG §9.5 item 5; and by BAT-2's own delay τ, on a phase
  shorter than τ the term never exceeds its own bound v), and what block 6 takes from it: §7 item 2 no longer
  claims the without-assist value is free of the gap for discharge read after the request ends, and the count of
  `battery.assist_outside_request` runs is printed beside it (D21). §8 reconciles the brief's pointer to
  `MACHINE_BOUNDARY` (block 5's request-level boundary) with the registered per-phase text, and §15 step 7 says how
  the lead would add the battery inside the per-phase value if wanted. Fixture B2 gains a prefill-only assist and a
  discharge read after its request.
- **Clause map.** Rows for REG §9.1 to §9.4 added, so every estimator clause of §9 maps to a step and a test.
- **Inputs moved?** L9's head is now `500f7ad3d` (reports only since `64b4e2cbf`); the block-6 line is still at
  `1706257c4`; on main, the registration and the nine `claim_usable` readers of §12 are unchanged since `ef520743c`.
- **Worked examples** of §4.6, §4.8, §6, §8, §10, §11.1 and §11.4 and the §11 precision derivation re-run with
  `/opt/homebrew/bin/python3.13 -I -B`: every printed digit reproduces.

## 22. Fourth pass (2026-10-22)

A re-check against the item's acceptance list and against what moved since the third pass, blind as before (the
**Blind** paragraph at the top lists what was read).

- **Desk compression (new, §4.1, D22).** The loop's desk compresses each session's large files after the harvest,
  so L9 would refuse every unit at step 0 (`runs_root_differs_from_archive`). The driver restores a unit's sessions
  with `desk_compress.restore`, checks the bytes against the compression record, and compresses them again after the
  unit. The CLI refuses roots outside `$TMPDIR` under `JW_B5_SYNTHETIC_ONLY=1`, because it writes into session
  directories. Fixtures are compressed by the desk code at the S-1 commit.
- **Re-harvested sessions (new, §1, §4.4, §4.9).** Paths come from the session record (`archive.reharvest-<n>` after a
  re-harvest). L9 refuses an analysed window harvested twice; block 6 allows it (REG §4), so the index lists the
  superseded archives, the block turns the refusal off, and `lines.history()` prints the account without inventing
  a survivor count. Fixture B1.
- **S-9 and S-11 (B6-2).** §4.6 now follows the fill: grain per pack and target phase (D11 revised), P_x from the
  admitted idle baseline's `powermetrics_idle.plist` records, time-weighted, scope decode and prefill-p2048 science
  runs, GAMMA's per-model line as structure and a labelled alternative if it ever differs, B6-2's replay count
  (0 of 840). §15 step 2 now merges B6-2 instead of filling the slots.
- **Pairing before the close (§5, D23)** and **block-6 sentences (§4.2, D24)**, with §9.5 item 6's formula, label and
  a worked example in §6.
- **Clause map (§13)** rewritten with one row per clause and an ID, covering REG §9 to §11.4, §12 and §13, plus the
  clauses of §4, §6.2 and §8 the analysis implements.
- **Trial merge re-run** with main `81db9f355`, L9 `195d2d405` and `1706257c4`: the same three conflicts; L9's
  frozen-file digest list (388 paths) reports the same five files; merged `joulewise/b5/harvest.py` digest `1b08dfe4…`.
  Correction: the block-6 delta to `whole_window.py` comes from `6ae3965bf` and `0276a3327` only (31 changed lines
  from the merge base `3bb305d7a`); the earlier list named two commits that do not touch the file.
- **Inputs moved?** L9's head `195d2d405` merges main and the sensitivity-guard lane; nothing under
  `joulewise/b5_analysis/`, `joulewise/analysis_engine/` or the scripts this design binds changed since `1ab888a68`
  (only `joulewise/night_gate.py` and tooling). Its L9-1 joined acceptance currently refuses at step 9b on synthetic
  data, a step block 6 does not run (D9); L9's release tag must clear it first (§15 step 1). The block-6 line is
  still at `1706257c4`; on main the registration and the §12 readers are unchanged.
- **Worked examples** of §4.6 (new), §4.8, §6 (item 6 new), §8, §10, §11.1 and §11.4 re-run with
  `/opt/homebrew/bin/python3.13 -I -B`: every printed digit reproduces.

## 23. Fifth pass (2026-10-22)

A re-check against the item's acceptance list and against what moved since the fourth pass, blind as before (the
**Blind** paragraph lists what was read). The new input is the data-integrity audit of 2026-10-22: its finding F4
(readers of desk-compressed files), its draft gate G4 and its compressed-file census (bytes only).

- **Compressed bytes (§0 item 8, §1, §4.1, D22 revised).** The fourth pass restored a unit's sessions plain, which
  needs up to 129.29 GiB free for a GAMMA unit against 69 GiB. A first version of this pass (`dedf7ef68`) read
  compressed files through `desk_compress.read_bytes` in editable readers and restored one session's root per call
  through `RunState.invoke()` for sealed readers (steps 1, 2 and 4). Its consult (below) refuted the second half by
  execution. The design now restores the unit's sessions in place as APFS transparently compressed files for the
  whole unit: plain to every reader at its plain path, about its compressed size on disk, each file checked against
  its compression row, and compressed again with the desk's `compress` after the unit. Measured on this Mac on
  synthetic plist text: same SHA-256, 7.5x smaller on disk, 265 MB written in 0.17 s. The after-check now compares a
  full inventory of the session tree, and a test requires every unit output to be byte-identical on plain and
  compressed fixture sessions (D26). The audit's plain fix "name `read_bytes` in the block-6 consumer's build brief"
  is answered in §17: the analysis does not use it, and the recompute does (§15 step 10).
- **Survivor screen (§4.7).** The analysis reads the screen's record and never re-runs the screen, which returns
  "undefined" on compressed archives.
- **Recompute (§15 step 10; clause 12.3-c).** Its silent fallback to `power_trace.csv` when the plist is compressed
  must become a stop before `compare.py` counts.
- **Harvest twin (§4.7, D25).** Merged on main (PR #554): the independent oracle for the allowance and b_op in the
  tests, at bar B3.
- **Fixtures (§16).** Every compressed category of the real census is compressed in at least one fixture session;
  each session's plain state is kept for the equivalence test; unit-level cases for the restore, the after-check and
  the four failure modes on compressed bytes.
- **Brief (§17).** The restore in stage B3; `tests/test_shard_tests.py` added to the modules always run (main now
  qualifies nested test packages, `9a270bd2e`); the live-hardware opt-ins (`JW_REAL_METER_SMOKE`, `JW_LIVE_HW`) are
  never set; `joulewise/twins/*` never edited.
- **Inputs moved?** L9's head is `152d8dc9f`: since `195d2d405` it merged main, and nothing changed under
  `joulewise/b5_analysis/`, `joulewise/analysis_engine/`, the library files or the scripts this design binds (only
  `joulewise/twins/` from main and two bridge scripts). The block-6 line is still at `1706257c4`. B6-2 is at
  `c37614f71` (its trace and one tense fix in the S-11 row; read as a file list only). On main `c21c52dfa` the
  registration, the nine `claim_usable` readers of §12 and the registries named in §17 are unchanged since
  `81db9f355`.
- **Worked numbers** re-derived with `/opt/homebrew/bin/python3.13 -I -B`: 32.75 + 37.90 + 38.64 = 109.29 GiB, plus
  20 = 129.29 GiB; GAMMA units' runs roots 54.01, 53.83 and 53.88 GiB; 12,952 / 1,728 KiB = 7.5; 109.29 / 7.5 =
  14.6 GiB; 120.297 GiB / 2,142 files = 57.5 MiB; 6 + 9 = 15 restore cycles. The consult re-derived the first
  version's numbers independently.

**Consult of the fifth pass.** One blind Sol 6.1 xhigh seat, local through `codex-run-v3` on the idle Mac (read-only
except its scratch; every `/Users/edr/night-*` path forbidden; `JW_B5_SYNTHETIC_ONLY=1`), on `dedf7ef68` against L9
`152d8dc9f`. It built a synthetic claim-run bundle with `tests/test_harvest_b5_window.make_member`, compressed it with
the desk's code, ran the CLI and the hashing on plain, compressed and restored states, parsed every step's `invoke`
call, and traced each reader to file and line. Report: `/Users/edr/night-archive/forward-20261021/B6-1/consult5/`
(full text, probes and their outputs in `scratch/` there).

| # | Finding (seat's verdict) | Disposition |
|---|---|---|
| F1 | blocker, executed and traced: R2_STEPS {1, 2, 4} misses plain readers in steps 5, 8, 6, 9, 10 and 11 (and conditionally 3 and 3b), many outside the WRITE_SCOPE; strict validation exits 2 on compressed bytes, `reduce` exits 0 with different bytes, a compressed campaign log reads as empty | adopted: the unit-scoped transparent restore covers every reader at every step (§4.1, D22) |
| F2 | blocker, executed (AST census of every call): steps 5, 8, 6, 9 and 11 pass no window; steps 5, 9 and 11 read two or three sessions in one call; steps 3, 3b and step 11's sensitivity bypass `invoke` | adopted: no per-call boundary remains; the whole unit's sessions are restored |
| F3 | should fix, executed: block 6's hazard lineage authenticates a relocated bundle without the sibling locator, so the stated reason against a scratch copy was wrong | adopted: the reason is replaced by the bindings that name original absolute roots (§4.1 *Not chosen*) |
| F4 | should fix, executed: a new four-byte file passes the compression-record after-check | adopted: the after-check compares a full inventory of the session tree (§4.1 item 3) |

Also confirmed by the seat: desk compress, `restore(root="runs")` and compress again return 0 and give back every
original SHA-256; step 0's sealed callees open no session file; L9's monitor and meter readers take their bytes
through the archive handle. Not run by the seat: the joined S10 chain and a full-unit equivalence run (the build's
on-request tests).
