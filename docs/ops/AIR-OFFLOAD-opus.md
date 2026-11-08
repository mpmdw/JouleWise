# Air offload: the external SSD on the M4 Air, the MacBook Pro kept bare (Opus build)

Author: Opus 5.5 (laptop lead's delegate), 2026-11-08, branch `ops/2026-11-08-air-offload-opus` from `origin/main`
@ `dcfa4c593`. This is the Opus half of an independent Sol/Opus build (RUN_STATE item 220). The Sol build is on
`ops/2026-11-08-air-offload`; it was not read before this branch was committed. The comparison is
`docs/ops/AIR-OFFLOAD-AGREEMENT.md`.

Code: `scripts/offload_window.py` (standard library only, Python >= 3.11), tests `tests/test_offload_window.py`;
benchmark `scripts/offload_bench.py`, smoke test `tests/test_offload_bench.py`. No hardware, network or ssh was
used. Nothing under `jw-b5-*`, `night-*`, `night-custody`, `night-archive` or `restricted/` was opened.

Status: a proposal for Ed's choice. Nothing here is in force and nothing changes a window's measurement.

## 0. Bottom line

- **The offload fits inside cool-down with a wide margin.** A D window (26.4 GB raw) is busy on the MBP for about
  1.5 min (pack about 55-70 s, push about 35 s at 50 MB/s). The Air then needs about 100 s to verify. The whole
  offload ends about 3-3.5 min after finalize, against a 15-25 min physical cool-down. **Expected turnaround impact:
  zero** while cool-down is at least about 7 min (the predicted offload times the 1.5 safety factor, plus a 2 min margin before
  the dwell).
- **Heat:** about 2.7 CPU-s per raw GB, so about 70 CPU-s for a D window (about 1.3 cores for about a minute).
  That is roughly the heat of 5-8 s of the window's own decode, added at the hottest point of cool-down. Estimated
  cool-down extension: a few seconds, and at most the about 1 min the compression runs.
- **The MBP stays bare.** Nothing is attached, no drive power reaches the KM003C DC-in channel, no SSD qualification
  and no R1 re-run are needed. The only new MBP activity is about 1.5 min of CPU and Wi-Fi, which starts after
  finalize and must end before the dwell. A deadline enforces that end.
- **Custody:** the MBP deletes a window only after two checks. (1) The Air sends a sealed receipt saying every raw file
  matched the record's own sha256 digests. (2) The second copy is in iCloud, and the server has confirmed it: the Air
  evicts each file to a placeholder, downloads it again, and checks that the bytes match. Until both arrive, the
  MBP keeps the window.
- **Compression:** zstd level 3, 4 threads, gives about 16x on synthetic plists calibrated on real captures. Real
  captures compress better (the real 10 Hz fixture gives 42x where synthetic gives 26x on equal samples), so every
  time and size here errs long. A D window is about 1.6 GB compressed (synthetic), likely less.

## 1. Facts checked in the repository

- **Window size:** 18.6 GB (W1) to 26.4 GB (D) per copy, two in-window copies (`SSD-ALWAYS-ATTACHED-STUDY.md` §3 on
  `origin/align/2026-11-08-v4-r11`).
- **What a member bundle holds.** These are the measured means over the 24 pilot-v3 members in
  `configs/campaigns/align_pilot_v3/registration/sizing_evidence.json`. Every bundle has 29 files and about 507 MB.

  | File | MB per member | Share |
  |---|---|---|
  | `raw/powermetrics.plist` | 212.8 | 42.0 % |
  | `raw/powermetrics_idle.plist` | 157.0 | 30.9 % |
  | `instrument_calibration/raw/powermetrics.plist` | 83.6 | 16.5 % |
  | `rich_telemetry.jsonl` + `rich_telemetry_idle.jsonl` | 27.1 + 19.9 | 9.3 % |
  | `raw/powermetrics_idle_post.plist` | 2.6 | 0.5 % |
  | everything else (turns, power trace, events, metadata, ioreg) | < 4 | < 1 % |

  The plists are 89.9 %, and none of these files is compressed.
- **The plist format.** The committed real captures are `tests/fixtures/d078_r01/raw/powermetrics.plist` and
  `tests/fixtures/powermetrics_sample.plist`, both from a Mac15,9, the M3 Max. They are NUL-separated XML plist
  documents at about 100 ms, with keys `processor{clusters[E, P0, P1]{cpus, dvfm_states}, cpu/gpu/ane/combined_power,
  *_energy}`, `gpu{dvfm_states, sw_state}` and `thermal_pressure`. Each sample is 52.8 kB, which matches the study's
  52 kB.
- **What is already compressed (nothing in an ALIGN v4 window).**
  - `joulewise/desk_compress.py` (on the lanes, not on `main`) compresses in place: `zstd -3 -T0`, files of at least
    1 MiB, verified, after `chain.exited` and a non-fault harvest. Only the block-6 desk and precheck lanes call it
    (`joulewise/b6/desk_lane.py:244`, `joulewise/b6/precheck_lane.py:120`).
  - `joulewise/b5/harvest.py` and `joulewise/align/apple/km003c.py` only **read** `.zst` siblings
    (`stream-*.jsonl.zst`, monitor and flag journals) through `desk_compress.read_bytes`. They are there for older
    archives and write nothing.
  - `joulewise/hazards/contention.py:306` keeps raw `ps` snapshots as gzip level 1 when asked. These are kilobytes.
  - Neither `run_night.py` nor `align_v4_session.py` calls compression. The sizing evidence records
    `digest_bytes: "logical uncompressed bytes"`, and there are no `.zst` files in the bundle inventories.
- **The record's own manifest.** R1 writes `harvest_manifest.json`
  (`joulewise.align.r1_harvest_manifest.v1`, `{root, files: {relpath: sha256}}`), and the harvest result pins its
  `manifest_sha256` (`joulewise/align/apple/r1_runtime.py` `k_harvest`). I found no equivalent full-tree manifest
  writer for W1/D windows on the lanes I read. **Open item:** the W1/D finalize must write one (`SHA256SUMS` format is
  accepted) and commit its sha256. The item 214 backlog already has "incremental manifests and parallel hashing for
  finalize".
- **Turnaround order** (items 213-217): finalize, hash and push; cool-down (15-25 min); the pre-arm checks, including
  the frozen next-arm triage; the display/quiet dwell. The triage entry `quiet_start_state` says "no desk, hashing or
  evidence traffic on the MBP". Item 214 rejected offload that overlaps the next window on the MBP. The synthesis
  allows only "a non-measuring host verifying an already-closed copy". This design is that: the MBP's part runs
  inside cool-down, and all verification runs on the Air.

## 2. Design

```
MBP (after finalize, start of cool-down)                 Air (on 24/7; SSD at /Volumes/JW-AIR)
 run --deadline-epoch <dwell start - 2 min>
  1 refuse if armed/measuring (LaunchAgents com.joulewise.night*/align-*/b6*, ps census)
  2 predict time from rates.json; refuse if x1.5 does not fit the deadline
  3 release older windows whose two receipts are in    -> receipts W   (gate)
  4 pack: tar parts (2 GiB raw each) -> zstd -3 -T4,
    file list and sha256 taken from the record manifest
    (pinned by --record-manifest-sha256), O_NOFOLLOW
  5 push: append-only, resumable                         -> stat/put/commit (gate checks part sha256)
  6 verify                                               -> verify: re-hash parts, decompress, check
                                                            EVERY raw file's size+sha256 against the record
                                                            manifest, extract to windows/W/raw, sealed receipt,
                                                            queue W for the second copy
  7 store the receipt; release if a second copy exists (usually next turnaround)
  8 write timing/offload-span.json (start/end receipts)
                                                          air-icloud (LaunchAgent, every 5 min):
                                                            copy parts+manifest to iCloud Drive, evict to a
                                                            placeholder, download again, sha256 match ->
                                                            sealed second-copy receipt; evict again
```

The rules the code enforces:

- **Digests come from the record, not from the offload.** The record manifest is authenticated by the sha256 pinned in
  the committed record. Each file's digest is copied from it into the offload manifest, and the Air checks each
  decompressed raw file against that digest. By default the MBP does not hash raw files (`--hash-on-mbp` turns it on)
  for two reasons: the Air's check is end to end, and hashing on the MBP adds heat. Compressed parts are hashed (about
  1.6 GB per D window), so that transfer is resumable and checked.
- **Never follow symlinks.** Every path is walked one component at a time with `O_NOFOLLOW` (`parent_fd`). A symlinked
  file, directory or root is a mismatch. Manifest paths may not contain `..`, be absolute, or contain empty
  components.
- **Fail closed.** Any digest, size, mtime, receipt-hash or tar mismatch exits 3 and deletes nothing. A transit
  mismatch also drops the Air's partial copy, so the next attempt starts that file from zero.
- **Resumable and idempotent.** Packed parts carry sidecars, and the push resumes at the Air's partial size. A second
  run with the same content does nothing. The same window id with different content is refused, whether locally
  (`duplicate_run_conflict`) or on the Air (`window_id_conflict_on_air`). An `flock` stops two runs.
- **Delete only after two verified copies.** `release` needs a sealed Air receipt that matches the local manifest
  (files, bytes, part digests, manifest sha) and a sealed second-copy receipt for the same parts. Before deleting
  anything it re-checks that every record file still has its packed size and mtime; one change refuses the whole
  release. Then it unlinks only manifest-listed files and removes only directories left empty, never `rmtree`. Files
  not in the record manifest are never sent and never deleted (`unlisted_not_offloaded`).
- **Disk pressure** (`--min-free-gib`, default 60, which is a D window's two copies plus margin). The default is
  **hold**: nothing is deleted, `disk_pressure: true` is reported in the span, and the magistrate decides. Opt-in
  `--pressure-compressed-local`: for a window that has the Air receipt but no second copy yet, the raw files go and the
  Air-verified compressed parts stay on the MBP. Two verified copies still exist (MBP parts and Air SSD). This frees
  about 94 % of the window.
- **In-window duplicate copy** (`--duplicate-root`, for example the backup rsync root). Its files are released with
  the record only when their sizes match. A copy that differs is kept and reported.

## 3. One-time Air setup (Ed, about 20 min)

1. **SSD.** Format the SN7100 as APFS, named `JW-AIR`. Then:
   `sudo mdutil -i off /Volumes/JW-AIR` (no Spotlight), `mkdir /Volumes/JW-AIR/offload`. In Time Machine, exclude it
   or leave it as is (your call).
2. **Keep the Air awake on power:** `sudo pmset -c sleep 0 disksleep 0`. The display may sleep.
3. **Remote Login** (System Settings > General > Sharing > Remote Login): on, for user `edr` only. If `hello` later
   fails with a permission error on `/Volumes`, also tick "Allow full disk access for remote users".
4. **The gate checkout.** Use a fixed checkout pinned to a reviewed sha, for example
   `~/code/CapstoneProject/jw-wt/offload-gate` at the merged sha, not a moving worktree. The forced command runs
   whatever file is at that path.
5. **Restricted key (on the MBP):** `ssh-keygen -t ed25519 -N '' -C jw-offload-mbp -f ~/.ssh/jw_offload_ed25519`.
   Add one line to the Air's `~/.ssh/authorized_keys`:
   ```
   restrict,from="<MBP hostname or IP>",command="/opt/homebrew/bin/python3 /Users/edr/code/CapstoneProject/jw-wt/offload-gate/scripts/offload_window.py air-gate --root /Volumes/JW-AIR/offload" ssh-ed25519 AAAA... jw-offload-mbp
   ```
   `restrict` turns off pty, port, agent and X11 forwarding and `~/.ssh/rc`. The gate runs no shell. It accepts six
   verbs (`hello`, `stat`, `put`, `commit`, `verify`, `receipts`) with validated window ids and file names, inside
   one directory. The key cannot read or delete anything else.
6. **MBP `~/.ssh/config`:**
   ```
   Host jw-air
     HostName Edrs-MacBook-Air.local
     User edr
     IdentityFile ~/.ssh/jw_offload_ed25519
     IdentitiesOnly yes
   ```
   Pin the host key once: run `ssh-keyscan` and compare the fingerprint with `ssh-keygen -lf
   /etc/ssh/ssh_host_ed25519_key.pub` on the Air. The script uses `StrictHostKeyChecking=yes`.
7. **Second-copy worker:** a LaunchAgent `com.joulewise.offload-icloud` on the Air, `StartInterval` 300,
   `ProcessType` Background, running `offload_window.py air-icloud --root /Volumes/JW-AIR/offload`. The default
   cloud dir is `~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-offload`. iCloud needs space for about
   1.2-1.6 GB per window (at the synthetic ratio), so about 40 GB for 25 windows. The Air's internal disk is tight
   (28 GB free today). The worker evicts each file after confirming it, so only the window in flight takes local
   space.
8. **Smoke test, no window involved:** on the MBP run `offload_window.py run` against a small dummy record (any
   directory plus its `shasum -a 256` list) with a fresh `--window-id smoke-YYYYMMDD`. Then check
   `/Volumes/JW-AIR/offload/windows/smoke-*/air-receipt.json`.

## 4. Per-window magistrate sequence

| When | MBP step | Notes |
|---|---|---|
| Window terminal | finalize, hash, commit and push the record (unchanged) | The finalize must write the record manifest (§1 open item) and pin its sha256 |
| Cool-down start, `t_c` | `offload_window.py run --state-root ~/jw-offload-state --window-id <id> --record-root <root> --record-manifest <manifest> --record-manifest-sha256 <pinned> --deadline-epoch <t_c + 900 - 120>` | One call; it prints the span JSON. Exit 0 means verified on the Air. |
| Right after | Commit `<state>/<id>/timing/offload-span.json` into the record branch | The timing reader takes it as `--span offload=<path>`. Its `kind` is `backup`, so the journal reader also maps it to `offload`. |
| Cool-down continues | nothing | The offload ended long ago. |
| Pre-arm checks | `offload_window.py triage --state-root ~/jw-offload-state --window-id <id> --dwell-start-epoch <planned>` | Evidence for `quiet_start_state`. Exit 2 if an offload is running, if one started without an end receipt, or if it ended within 120 s of the dwell. |
| Dwell, arm | unchanged | |

The deadline is the only timing input. It should be the planned dwell start minus a margin. When the magistrate does
not know the dwell start yet, cool-down start plus the 15 min physical minimum, minus 2 min, is safe. `run` refuses to
start (exit 4) if the predicted time times 1.5 does not fit. `rates.json` holds the last observed rates; the first run
uses conservative defaults (pack 250 MB/s, push 40 MB/s, verify 250 MB/s, ratio 8). Mid-run, every part,
every 64 MiB read and every ssh call checks the deadline. An ssh call's timeout is the time left. At the deadline the
offload stops with exit 4 and keeps its state; the next turnaround resumes it.

## 5. Benchmark (Apple M4 Air, zstd 1.5.7, synthetic member bundle of 506 MB)

Synthetic data: `scripts/offload_bench.py` keeps the exact XML skeleton of the two real Mac15,9 captures and re-draws
every field that varies between real samples (lognormal noise, the same sparsity). The member bundle follows the
pilot-v3 inventory above. Check against the real captures at equal sample counts, zstd -3:

| Fixture | Real ratio | Synthetic ratio |
|---|---|---|
| `d078_r01` (9 samples) | 41.6x | 25.8x |
| `powermetrics_sample` (5) | 25.3x | 23.9x |

The synthetic data is less compressible than real data: real consecutive 10 Hz samples are correlated, and the
synthetic ones are drawn independently. All figures below therefore err long.

| Codec | Level | Threads | Ratio | Compress MB/s | CPU-s per GB | Decompress MB/s |
|---|---|---|---|---|---|---|
| zstd CLI | 1 | 1 | 17.5 | 417 | 1.4 | 944 |
| zstd CLI | 1 | 4 | 17.5 | 1,444 | 1.3 | 1,273 |
| zstd CLI | **3** | 1 | 16.1 | 299 | 1.9 | 1,608 |
| zstd CLI | **3** | **4** | **16.1** | **1,572** | **1.9** | 1,713 |
| zstd CLI | 6 | 1 | 19.6 | 123 | 5.2 | 1,740 |
| zstd CLI | 6 | 4 | 19.6 | 400 | 5.1 | 1,307 |
| zstd CLI | 9 | 1 | 20.9 | 79 | 7.9 | 1,778 |
| zstd CLI | 9 | 4 | 20.9 | 321 | 7.7 | 1,924 |
| stdlib `compression.zstd` (3.14) | 3 | 1 | 16.0 | 476 | 1.5 | — |
| stdlib gzip | 1 | 1 | 11.3 | 132 | 3.9 | — |
| stdlib gzip | 6 | 1 | 15.1 | 64 | 9.9 | — |

Single-run figures; inputs are in the page cache. Level 6 and 9 buy 20-30 % smaller output for 2.7-4x the CPU.
At Wi-Fi speeds the transfer is already short, so level 3 is the choice: the heat costs more than the bytes.
Level 1 is equally good if the MBP should be cooler still.

**The real code path**, end to end on the same member: `Offload.pack` (Python tar into zstd -3 -T4) packs at
**490 MB/s** for 2.7 CPU-s per GB; Python's tar loop is the bottleneck, not zstd. With T1 it is 340 MB/s.
`Gate.verify` on the Air (re-hash parts, decompress, sha256 every raw file, write the raw tree) runs at **265 MB/s**.

**Per-window end-to-end** at the measured rates (pack 490 MB/s, Air verify 265 MB/s, ratio 16.1, 10 s of ssh
overhead):

| Window | Network | Pack (MBP) | Push | Verify (Air) | Total |
|---|---|---|---|---|---|
| W1, 18.6 GB | 50 MB/s | 38 s | 23 s | 70 s | **141 s** |
| W1 | 100 MB/s | 38 s | 12 s | 70 s | 130 s |
| W1 | 300 MB/s | 38 s | 4 s | 70 s | 122 s |
| D, 26.4 GB | 50 MB/s | 54 s | 33 s | 100 s | **196 s** |
| D | 100 MB/s | 54 s | 16 s | 100 s | 180 s |
| D | 300 MB/s | 54 s | 6 s | 100 s | 169 s |

These are measured on the M4. The M3 Max has 12 P-cores but slightly slower single-core speed. The pack is bound by
one Python thread, so expect it to be up to about 20 % slower there: D pack about 65 s. The MBP is busy only during
pack and push (D: about 1.5 min). While the Air verifies, the MBP holds one idle ssh session. Speed-ups not taken:
verifying parts in parallel on the Air (about 2-3x), and pipelining pack with push. Neither is needed with a 15-25
min cool-down.

## 6. Measurement safety

- **Where it sits:** at the start of cool-down, the hottest and least valuable point of the turnaround. The machine is
  cooling from 60-100 W decode toward its quiet start state either way, and cool-down ends on temperature, not on a
  clock. Offload heat (about 70 CPU-s, roughly 6-8 W above idle for about 1 min, so about 0.5 kJ) is absorbed by the
  same decay.
- **Estimate (planning guess, unmeasured on the MBP):** the window's excess stored heat at cool-down start is tens
  of kJ. 0.5 kJ is about 2 % of it, so cool-down lengthens by about τ·ln(1.02), a few seconds at τ of about 5-8 min.
  The upper bound is the about 1 min the compression runs.
- **Never in the dwell or a window:** the deadline (§4), the armed/measuring refusal (re-checked before every part,
  every upload and the release), and the triage receipt all enforce this. `run` exits before the dwell or it does not
  start.
- **First real window:** record the cool-down's thermal trace together with the span. If cool-down is measurably
  longer than on windows without an offload, drop to `--level 1 --threads 2`. The pack is single-thread-bound anyway,
  so this costs about 10 s.
- **Network:** Wi-Fi only, about 1.6 GB per D window. Nothing is plugged into the MBP, so its DC-in channel sees no
  drive power. The Air's own power is irrelevant: it is not measured.

## 7. Failure handling

| Exit | Meaning | Magistrate action |
|---|---|---|
| 0 | Verified on the Air (release may be held for the second copy) | Commit the span. Nothing else. |
| 2 `window_armed` / `window_measuring` | A window is armed or a measuring process is alive | Do not offload now. The next turnaround retries. |
| 2 `offload_already_running` | Another run holds the lock | Wait. Triage refuses the arm until it ends. |
| 3 `*_mismatch`, `record_changed*`, `raw_digest:*`, `window_id_conflict*`, `duplicate_run_conflict` | Integrity failure; nothing deleted | Keep the record. Report to the lead with the span and journal (`offload-journal.jsonl`). Do not retry blindly. |
| 4 `deadline:*` | Predicted or actual overrun | State is kept; the next turnaround resumes. If it repeats, the rates or the network need a look. |
| 5 `air:*`, `transport_*` | Air asleep, unreachable or busy | The next turnaround resumes from the partial. The MBP keeps the copy. |
| 6 `io_error` | e.g. ENOSPC on the MBP | Disk guard. The arm's own disk checks still apply. |
| Second copy pending for long | iCloud upload slow or out of quota | See `queue/second-copy-errors.jsonl` on the Air. The MBP keeps the window. Under pressure, opt in to `--pressure-compressed-local`. |

The MBP never deletes on any non-zero path, and release is all or nothing. Restoring a window needs no code:
`zstd -dc part-NNNN.tar.zst | tar -x` on any Mac, then check the files against the record manifest.

## 8. Open items

1. The W1/D finalize must write a full-tree sha256 manifest and pin it (§1). R1's `harvest_manifest.json` already
   works.
2. Ratio and pack rate on real MBP data are unmeasured. The first real offload measures them: `rates.json` and the
   span hold the ratio and stage times.
3. iCloud quota, and whether `brctl evict` behaves the same on Ed's account. The smoke test (§3.8) shows it before
   any window depends on it.
4. Air availability: the Air must be awake and on the same network during cool-down. If it is not, the MBP keeps the
   window (exit 5) and nothing is lost. Disk pressure then accumulates at about 26 GB per window.
5. Wiring: the triage output is evidence for the existing `quiet_start_state` entry. It adds no new triage entry,
   because the B2 list is frozen in the registration text.
