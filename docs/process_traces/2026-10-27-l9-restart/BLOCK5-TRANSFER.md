# Block-5 dry-run inputs: package on the measurement Mac, analyse on the analysis laptop

**Authority:** Ed, 2026-10-27, in Claude Code session 015ASG1T (continued from his MacBook Air): "yes you have my ok
for both moving the block 5 dry run here, and yes, orchestrator should be allowed to package and upload the archives
between sessions". Recorded as `ED-RULING.md` item 6b beside this file. Directive issue #587 carries the scheduling.

**Status: AUTHORIZED, NOT ACTIVE.** Ed gave permission, not a mandate ("i was giving you permission not a
mandate"). The orchestrator does **nothing** under this file until a later commit adds the line
`B5-TRANSFER: GO` at the end of this file. The lead adds that line only after the condition below is met with
executed evidence, and after telling Ed. Until then the block-5 dry run stays on the measurement Mac, as ruling
item 6 says.

**Machines.**
- **Measurement Mac** (M3 Max): collects; holds the only copy of block 5's raw bundles and harvest archives.
- **Analysis laptop** (Ed's MacBook Air, M4, 24 GB, about 200 GiB free on 2026-10-27, Python 3.13 at
  `/opt/homebrew/bin/python3.13`): runs the block-5 blind dry run and the independent recompute. It never measures,
  so agent processes and CPU load there affect no session.

## What the orchestrator on the measurement Mac does

**When:** only at a BYTES SESSION_DESK, after the desk has finished, or while the loop is held. Never while the loop
is in PRECHECK, ARM_WAIT, SMOKE_* or SESSION_RUN: compression and hashing are CPU and disk load on the measurement
machine. If one packaging slot is not enough, finish in the next one; partial work is resumable (one tar per item
below).

**What:** everything the blind dry run reads for the three analysed attempts, and nothing else:
- ALPHA a1 `v5-b5-alpha-a1-20261009T2312Z`, BETA a6 `v5-b5-beta-a6-20261011T2011Z`, GAMMA a1
  `v5-b5-gamma-a1-20261012T0420Z` (RUN_STATE items 28 and 31): each window's runs root and its harvest archive.
- The inputs the scout report lists for the dry run
  (`report/2026-10-22-blind-dry-run-scout:.codex-report/BLIND-DRY-RUN-SCOUT.md` §2, "Required records/inputs").
  That covers the sealed pack, config and manifest files; the terminal-pinned archived calibration ledgers; and
  the bracket, NEG-8 survivor and allowance records. It also covers every capture those ledgers reference: an
  evicted capture must be restored first, never silently left out.
- Not the superseded attempts' bytes. The index records their history; the dry run does not read their bundles.
  If the dry run turns out to need one, add it in a later slot.

**How:**
1. For each item, write a manifest of every file: path relative to one data root, size, SHA-256. Hash the files as
   they are on disk. Do not open, parse or print any energy, power, duration or other number from them.
2. Pack each item as one `tar` compressed with `zstd -3` (about 70 times smaller on powermetrics plists, measured
   2026-10-14). Record each tar's SHA-256 in the manifest.
3. Put the tars and manifests in iCloud Drive at `JouleWise-transfer/b5-dryrun/` (one subfolder per item). Do not
   use `JouleWise-backup` or `JouleWise-archive`; the laptop keeps those cloud-only.
4. Leave the originals in place on the measurement Mac. Nothing here moves or deletes block-5 data.
4b. Each manifest also states the item's total uncompressed bytes. After the last tar is placed, keep the loop held
   (no PRECHECK) until iCloud reports every tar uploaded (for example `brctl status` or the Finder upload state
   shows none pending). The upload must not run into a session.
5. Commit the manifests (not the tars) to `docs/process_traces/2026-10-27-l9-restart/b5-transfer/` and say in
   the RECORD which items are complete.

## What the analysis laptop does

1. Downloads `JouleWise-transfer/b5-dryrun/`, checks every tar's SHA-256, unpacks under one data root, and checks
   every file's SHA-256 against its manifest. Any mismatch stops the transfer for that item. Nothing is analysed
   from it.
2. Writes the S11 index (`configs/analysis/b5/analysed_windows.json`) against that data root, from the same
   authenticated harvest pins.
3. Runs the blind dry run, using the merged L9 at its pinned commit, with a fresh custody root, and then the
   independent recompute. Only structure leaves the restricted folder, as on the Mac. No agent reads the restricted
   folder.

## Condition (all must hold before `B5-TRANSFER: GO`)

1. L9 has passed its acceptance and its executing review (ruling item 1).
2. The 120 s calibration wall deadline (ruling item 6, option (c)) does not fire on the laptop. The full-size synthetic
`test_dry_run` at L9-2's cached commit (`60473bee`), run alone on the laptop on 2026-10-27, is the check. If it fires,
the dry run stays on the measurement Mac, as originally ruled.
3. The lead has told Ed the evidence and Ed has not objected.

## GO record

Condition 1 (L9 acceptance and both executing reviews) is still being completed on 2026-10-28. It governs only
the start of the laptop dry run, not the packaging.

Condition 2: the laptop full-size cached run at `60473bee` passed step 9b with no deadline firing (RUN_STATE item 81).
Its only 2 failures were path-token artefacts of the temporary folder's name.

Condition 3: Ed was told the evidence and plan in session 015ASG1T and answered "b5 transfer go if that gets
analysis done faster" (2026-10-28). ED-RULING item 10 records the custody, disk and upload rules.

B5-TRANSFER: GO


## Addendum 1 (lead, 2026-10-28): history records

The dry run opens the attempt record of **every** indexed attempt, not only the three analysed ones
(`joulewise/b5_analysis/archive.py` `open_attempt_record`, called for each index entry at step 0 and by each child
program; found by S11-INDEX-1, `lane/2026-10-28-b5-window-index` `.codex-report/S11-INDEX-1.md` I5). Without these
records step 0 refuses with `harvest_record_not_the_indexed_one`. At the next BYTES SESSION_DESK, or while the loop is
held, package one more item, `history-records`, by the same **How** steps 1-5 above (hash and compress only; open no
values; manifest with total uncompressed bytes; tar in `JouleWise-transfer/b5-dryrun/history-records/`; hold the loop
until uploaded; commit the manifest to `b5-transfer/`). Contents, for each of these 8 archive roots, `harvest.json`
and the whole `derived/` directory:

- `/Users/edr/night-archive/harvest-v5-b5-alpha-a1-20261008T2201Z`
- `/Users/edr/night-archive/harvest-v5-b5-alpha-a2-20261009T0515Z`
- `/Users/edr/night-archive/harvest-v5-b5-alpha-a3-20261009T0644Z`
- `/Users/edr/night-archive/harvest-v5-b5-beta-a1-20261010T0742Z`
- `/Users/edr/night-archive/harvest-v5-b5-beta-a2-20261010T1756Z`
- `/Users/edr/night-archive/harvest-v5-b5-beta-a3-20261010T2151Z`
- `/Users/edr/night-archive/harvest-v5-b5-beta-a4-20261010T2237Z-r2` (the re-harvest; not the cut-short first harvest)
- `/Users/edr/night-archive/harvest-v5-b5-beta-a5-20261011T0739Z`

If a root or its `harvest.json` is absent, record it in the manifest notes and continue; do not substitute another
directory. These are analysis inputs only for the attempt census; they do not change which attempts are analysed.
