# Analysis cadence: making analysis fast, parallel and off the measurement Mac

Proposal, 2026-10-27, written for Ed by Claude Code session 015ASG1T after Ed asked for analysis that "keeps pace"
with collection (directive #587) and for "a more parallel process". Nothing here changes a registered estimator,
exclusion, blinding rule or printed number. Items marked **amend** change *how* a number is computed, and need a
dated, blind amendment before the data they apply to are opened.

## 1. Where the time goes today (measured)

| Cost | Evidence | Share |
|---|---|---|
| Every kept run re-fits the same pulse calibration from scratch | L9-2 report, `lane/2026-10-27-l9-2` `.codex-report/L9-2.md`: 82 projections of one calibration's bytes (951ed3fa…) in the joined run | 63 % of joined-run wall time |
| Steps 1 and 2 run one bundle at a time | `joulewise/b5_analysis/dry_run.py` `step_1` / `step_2`: a plain `for` loop over `kept_bundles()`, one `cli.main` call each (about 350 kept bundles for block 5: 357 planned runs, less a few excluded members) | most of the rest |
| Tests replay the full chain at full size | `tests.b5_analysis.test_dry_run` 20,950-24,782 s; `test_release_equality` 47,231 s (two chains) | a day per fix round |
| Analysis runs only on the measurement Mac | the raw bundles live only there (about 43 GiB per collected session); analysis load would contaminate a running session | analysis waits for collection gaps |
| Human-shaped gates after the numbers exist | plan §3.1 step 12 (a judge and a refuter re-derive every printed number) duplicates the independent recompute; block 6 §13 requires two blind cold passes at merge | days per gate round |

## 2. Speed, in order of payoff

1. **Shared calibration cache** (in progress, L9-2). One `physics_cache` per driver run, keyed by the calibration
   artifact's content hash, with failures never cached. It already exists and the harvest uses it
   (`joulewise/cli.py` `validate_bundle`, `joulewise/b5/harvest.py`). Non-governed code only; byte-identical outputs.
   Ruled: `docs/process_traces/2026-10-27-l9-restart/ED-RULING.md` item 1.
2. **Parallel steps 1 and 2.** Each kept bundle's strict validation and re-reduction is independent. Run them in a
   process pool (spawn context, one worker per performance core), with outputs content-addressed as now. Then
   assemble records in the registered order, so the record and every digest are byte-identical to the serial run.
   This is L9 code (`joulewise/b5_analysis/dry_run.py`). Test: a serial run and a parallel run of the same fixture
   give equal digests. On the M3 Max this should take steps 1 and 2 from hours to minutes. The estimate is
   unmeasured; the first cached run will tell.
3. **Parallel packs and sessions.** Step 4 (floor extraction) is per pack: ALPHA and BETA can run side by side.
   Block 6 has nine sessions. Its six ALPHA and BETA sessions are independent, and each of the three GAMMA sessions
   waits only on its paired floor sessions (registration §6.2). So block 6's analysis is a two-level DAG, not nine
   runs in a row. The driver being built (B6-AN-1) should schedule it that way.
4. **Governed fix to the calibration refit: amend, with a calibration reissue.** Option (a) of the 9b ruling: the
   analysis path stops inheriting the 120 s wall deadline. Also count the coordinate-descent work the cell budget
   currently misses (L9-2: 99 % of a detection's time). Together they make the analysis' outcome independent of host
   speed, which item 5 needs. One change and one reissue, after block 5's first dry run.

## 3. Analysis off the Mac

**Can a cloud Claude seat do it?** For synthetic tests, yes. For the real data, not as things stand:

- **Resources.** A Claude cloud seat has 4 vCPU, 15 GB RAM and about 30 GB free disk (measured in this session).
  Codex Cloud has 5 vCPU and 17 GB. Block 5's three analysed sessions are well over 30 GB of raw bundles
  uncompressed. They compress about 70 times (powermetrics plist text, measured 2026-10-14), so transfer is cheap.
  But the analysis reads uncompressed bundles unless it is taught to stream `.zst`.
- **Speed and the deadline.** With the 120 s deadline kept (ruling item 6, option (c)), a slow shared VM is
  exactly where it fires. Real-data analysis off the Mac should wait for item 2.4, or use a fast dedicated machine.
- **Transfer.** GitHub refuses files over 100 MB, and a raw powermetrics file is about 130 MB. So bundles travel
  as compressed archives (release assets of the private data repo, up to 2 GB each, or a direct copy to Ed's
  machine), with every file's SHA-256 checked on arrival against the harvest record.
- **Blinding** is no worse than on the Mac: there too an agent launches the dry run, and the driver writes only
  structure to public outputs. The machine should run the pipeline as a script, with nothing reading its
  restricted folder.

**Recommendation.**
- Block 5's first dry run: on the Mac (ruled).
- From then on: a dedicated analysis machine, with Ed's 3080 Ti rig the obvious candidate if it runs Linux and has
  the disk, or a larger rented VM. Compressed archives would move to it after each harvest, so the Mac only measures.
- Do this after the cache, the parallel steps and the governed deadline fix land, so the outcome no longer depends
  on host speed.

## 4. Analysis as sessions arrive, not at the end

Block 6's registration already allows the analysis to run blind on real sessions as they arrive (§12.2); only
structure leaves the restricted folder. So the cadence should be:

1. **Session ends:** harvest and structure check (exists today; it caught s1's missing sidecar and s5's heat the
   same day).
2. **Same day, on the analysis machine:** that session's blind analysis (steps 1-11 for its pack) and the
   independent recompute, with structure-only output. A tooling refusal here is found within a day of collection,
   while the cause is fresh and the next session of that pack has not run yet. This answers Ed's "what if there's a
   defect that means I need to recollect".
3. **Pack closes:** the release reads outputs already computed and checked. Release becomes a short step, not a
   multi-day project.

For BYTES this is already the design (stage-1 analysis as soon as the fit set exists).

## 5. Gates that should get lighter: amend, blind

- **Block 5 plan §3.1 step 12** (results cold gate: a judge and a refuter re-derive every printed number). The
  independent recompute already re-derives every printed quantity and must agree within registered bars. Replace
  step 12 with one reviewer reading the recompute's comparison table.
- **Block 6 §13** (full-size synthetic chain plus two blind cold passes before the blind dry run). Replace with the
  ED-RULING.md pattern: the cached full-size run, one executing review, the real blind dry run as the end-to-end
  test, and the cold passes before release rather than before the dry run. Needs a dated §17 entry with one
  executing refuter.
- **Tests.** One cached full-size run per release candidate, not per fix round. Fix rounds use targeted tests of
  the changed step with the cached primary run's inputs. The harness already caches its primary run per process;
  persist it across processes, keyed by source digest.

## 6. Proposed order

| When | Item | Who |
|---|---|---|
| now | shared cache (2.1) | L9-2 |
| now | parallel steps 1-2 (2.2) | L9-2, after the cache, before its full-size run, so one run proves both |
| now | DAG scheduling in the block-6 driver (2.3) | B6-AN-1 |
| before block 5's dry run finishes | step-12 and block-6 §13 amendments (5) | lead drafts, Ed approves, one executing refuter each |
| after block 5's dry run | governed deadline and cell-count fix with its reissue (2.4) | new seat, full gate |
| after 2.4 | analysis machine and per-session analysis (3, 4) | lead with Ed (hardware choice) |

## Disk on the analysis laptop (2026-10-28, lead, at Ed's request)

The laptop has about 190 GiB free. A session is 33-39 GiB plain (block-6 compressed-file census). Block 5's three
windows are about 130 GiB; block 6's nine sessions are about 390 GiB. The constraint is the plain working set, not
storage, because the compressed form is small (`zstd -3` is about 70x on powermetrics plists).

**Measured 2026-10-28 on `tests/fixtures/powermetrics_sample.plist`:** plain 264 KiB on disk; APFS transparent
compression (`ditto --hfsCompression`) 20 KiB, so about 13x, and the file reads back byte-identical (`cmp`);
`zstd -3` 12 KiB.

**Rule:**
1. **The cloud copy is the compressed tars only,** in iCloud `JouleWise-transfer/`. After a tar's SHA-256 is
   checked, evict its local copy (`brctl evict`). It downloads again on demand and is re-checked by hash.
2. **Block 5 unpacks plain.** It fits, and the synthetic acceptance run used plain files, so nothing about the read
   path changes.
3. **Block 6 and BYTES use the block-6 design's rule:** restore one unit's sessions (at most three) as APFS
   transparently compressed files, run the unit, then recompress (`b6_analysis_additions.md` §4.1). The on-disk
   working set is then a few tens of GiB instead of about 390 GiB.
4. **After a block's release has been rerun byte-identically, delete its unpacked copy on the laptop.** The tars and
   their manifests are the record.
5. **Nothing is written into iCloud Drive from the laptop during collection.** iCloud mirrors to the measurement Mac,
   and a download there is load on a session. Outputs leave by git, since they are structure records.
6. **Dropbox, on the analysis laptop only** (installed by Ed 2026-10-28; never on the measurement Mac). Folder
   `~/Dropbox/JouleWise-analysis/`. It is the laptop-only store, so nothing written there reaches the measurement Mac:
   - backups of restricted custody outputs before release (they may not go to git or iCloud);
   - offloaded unpacked copies of released blocks, kept online-only.

   Making a file online-only from a script uses `FileManager.evictUbiquitousItem`, compiled from a three-line Swift
   file. Tested 2026-10-28: a 20 MB file went from 19,532 KiB to 0 on disk, and reading it downloaded it again with a
   matching SHA-256. Quit Dropbox (`osascript -e 'quit app "Dropbox"'`) for the length of a full-size or real
   analysis run, then reopen it, so sync load cannot trip the 120 s deadline.
7. **Fallback: an external 1-2 TB SSD** for a block that must be resident plain all at once.
