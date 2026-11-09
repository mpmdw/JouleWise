# Air offload: Sol and Opus builds compared, and a merged recommendation

Author: Opus 5.5 (laptop lead's delegate), 2026-11-08. This is the agreement step required by RUN_STATE item 220.

**Implemented:** the merged build of items 1-9 is `docs/ops/AIR-OFFLOAD.md` on `ops/2026-11-08-air-offload-merged`.
The Opus-only doc `AIR-OFFLOAD-opus.md` named below was deleted there (retrievable at `44c264f69`).
Later lead ruling (2026-11-08, delta review S1-D03): the opt-in `--pressure-compressed-local` route kept below was
removed; under disk pressure the policy is HOLD only.

| Build | Branch and sha | Files |
|---|---|---|
| **Opus** | `ops/2026-11-08-air-offload-opus` @ `44c264f69`, committed and pushed before Sol's branch was fetched | `scripts/offload_window.py`, `docs/ops/AIR-OFFLOAD-opus.md`, `scripts/offload_bench.py` |
| **Sol 6.1** | `ops/2026-11-08-air-offload` @ `daecbbc28` (implementation `5e870361b`) | `scripts/offload_to_air.py`, `docs/ops/AIR-OFFLOAD.md`, run report |

Both test suites pass here, one module per process: Opus 34 + 1, Sol 35. Neither build touched the network, ssh or
hardware.

**Brief difference that explains part of the gap.** Sol's report calls its task "option 2, MBP-push/Air-SSD", and
says the second disk is "the chosen allowed alternative to iCloud". So Sol's brief allowed a second physical disk in
place of iCloud. Sol also did not compress, while Ed's idea (this brief) says "compress the raw result data on the
MBP".

## 1. Where the two builds agree

The builds were made independently and converge on the core design. That is good evidence the core is right.

- **Placement.** The MBP pushes during cool-down, after finalize, commit and push. The offload never overlaps the
  dwell or a window, and it refuses rather than eat into the dwell.
- **Authentication.** The digests come from the record's own manifest, which is authenticated by the sha256 pinned
  in the committed record. The Air checks every raw file against them.
- **Restricted SSH.** One forced-command key, `restrict`, no shell, and confinement to one directory. Host key
  pinned, `BatchMode`, `StrictHostKeyChecking=yes`. No server runs on the MBP.
- **Receipts.** Hashed receipts, where the receipt hash covers its canonical JSON body. Two verified copies are
  required before the MBP deletes, and a queued copy never counts.
- **Failure behaviour.** Resumable, idempotent and fail closed. No symlink at any path component. All files are
  checked before any unlink. Only empty directories are removed, and `rmtree` is never used. Disk pressure never
  relaxes the two-copy rule.
- **Second copy.** The Air makes the second copy in the background, without the MBP.
- **Open item both flag.** The W1/D finalize must author a complete closed-record manifest and pin it.

## 2. Differences

| Topic | Opus | Sol | Safer | Faster |
|---|---|---|---|---|
| **Compression** | tar parts, zstd -3 -T4 (stdlib zstd or gzip fallback); about 16x on calibrated synthetic plists | none; raw rsync | — | **Opus, about 16x fewer bytes on Wi-Fi** |
| **MBP work per D window (26.4 GB)** | pack about 55-70 s (about 2.7 CPU-s/GB), push of about 1.6 GB: about 35 s at 50 MB/s. **About 1.5 min.** | 2 full SHA-256 passes (`inspect_record` before and after the copy, about 37 s each at the 715 MB/s measured on this Air), rsync `--checksum` sender pass, 26.4 GB over Wi-Fi (528 s at 50 MB/s), ssh encryption of 26.4 GB. **About 11-12 min.** | **Opus** (less heat and radio time in cool-down) | **Opus** |
| **Admission estimate, D at 50 MB/s** | 196 s predicted × 1.5 = 294 s | 31 min 18 s (Sol's own table, 5 passes at 100 MB/s) | — | Sol's estimator refuses any cool-down under 31 min, which is longer than 15-25 min. Calibrated, Sol is still about 12 min. |
| **Who verifies what** | the MBP hashes only the compressed parts; raw files are checked end to end on the Air | the MBP re-hashes all raw bytes twice, and the Air hashes them again | Sol: corruption on the MBP is localized before transfer. Opus catches the same corruption on the Air (the test `test_raw_corruption_is_caught_on_the_air_end_to_end`), and `--hash-on-mbp` exists. | Opus |
| **Second copy** | iCloud Drive, **server-confirmed by an evict-to-placeholder / re-download / sha256 round trip**; off-site; about 1.6 GB compressed per window; evicted again afterwards | a second **physical disk on the Air**, raw (26.4 GB per D window); explicitly rejects iCloud ("upload queue does not prove server persistence") | **Opus for failure domain:** both of Sol's copies sit in one machine on one desk (theft, power surge, spill). Sol's objection to iCloud is answered: a placeholder that downloads again with matching bytes did come from the server. | Opus |
| **Practicality of the second copy** | uses Ed's iCloud. Needs about 40 GB of quota for about 25 windows; the Air's internal disk stays nearly empty. | needs a second external disk on the Air of about 700 GB for about 25 raw windows. The Air's internal disk has 28 GB free, and Ed has one borrowed SSD. **Without a second disk, nothing is ever deleted**, and the MBP (51-115 GB free) holds after about 2 windows. | — | Opus |
| **Armed / measuring interlock** | standalone probe: `com.joulewise.night*`, `align-*`, `b6*` LaunchAgents and a `ps` census of measuring processes. Checked at the start and before every part, upload and release. Plus an own `flock`. | **magistrate-owned lease** (`joulewise.air_offload_gate.v1`: generation, phase, armed, measuring, committed/pushed, dwell and expiry), the watchdog's `fenced_checkouts == []`, and **the same persistent flock the magistrate takes for every arm/measure/dwell transition** | **Sol** (a real mutual exclusion, not a heuristic). It requires magistrate wiring; Opus works today without it. | — |
| **Terminal evidence** | trusts the magistrate's call order | `result.json` verdict and `ended_epoch_s`, `chain.started`/`chain.exited`, refuses `chain.unkilled`, needs `courier.sent` | **Sol** | — |
| **Completeness** | ships manifest-listed files. Unlisted files are reported, never sent and never deleted. | refuses if any regular file is unlisted; also refuses hard links, `.git` and `restricted` members | **Sol** (a closed envelope means no silent residue) | — |
| **Receipt freshness** | sealed receipts stored on the Air. Release validates both against the local manifest, but does not re-hash the Air copies at release time. | a challenge nonce on every request. `status` re-hashes **both** Air copies before a deletion receipt. | **Sol** (it catches later decay on the Air before the MBP deletes) | Opus (Sol re-hashes about 53 GB on the Air for every pending window) |
| **Air-side confinement** | the gate runs as `edr` from a pinned checkout | a dedicated non-sudo `jw-offload` account, a root-owned script, write-only/no-delete `rrsync` into `incoming/`, sshd match block | **Sol** | — |
| **Transport** | its own append-only `put`/`commit` (the Air checks each part's sha256 before rename); no dependency | `rsync -rt --checksum --partial` through `rrsync -wo -no-del`; needs a modern rrsync, which macOS lacks | tie (both verify; rsync is better proven, Opus has fewer moving parts) | Opus (no checksum pre-pass) |
| **Deadline** | wall-clock `--deadline-epoch` (dwell start minus 120 s), prediction × 1.5 from observed `rates.json`, checks every 64 MiB and per call, ssh timeout = time left | monotonic deadline from the lease, `SIGALRM` backstop, process-group kill of rsync/ssh; 5 s margin | Sol for the mechanism (monotonic, alarm, group kill); Opus for the margin (120 s is better than 5 s before a dwell) | — |
| **Interrupted deletion** | resumable: deleted files are skipped; the inventory lives in the state dir's offload manifest | an explicit `deleting`/`deleted` journal with the inventory; resume re-hashes the remaining files | Sol, slightly | — |
| **Manifests accepted** | `r1_harvest_manifest.v1` (R1 `harvest_manifest.json`), `SHA256SUMS`, generic `{files}` | `ssd_closed_record.v1` (SSD-P1 `ssd-closed.json`), `closed_record.v1`, `harvest_window.v1` | union | — |
| **Timing / triage receipts** | `timing/offload-start.json` and `offload-span.json` (`kind: backup`, epoch and monotonic fields), readable by `window_timing --span offload=…`. A `triage` command gives evidence for `quiet_start_state`. | elapsed seconds in the JSON output; `hold_next_window` | **Opus** (it feeds the existing timing reader and the frozen triage entry) | — |
| **Benchmark** | measured: zstd 1/3/6/9 × T1/T4 plus stdlib, and the real pack/verify path, on synthetic data calibrated on real Mac15,9 captures | none (estimates only) | — | — |

## 3. Which is safer, which is faster

- **Faster: Opus, clearly.** D window at 50 MB/s: about 1.5 min of MBP work and about 3.3 min end to end, against
  Sol's calibrated about 12 min of MBP work (31 min as Sol's estimator admits it). At 300 MB/s Sol's transfer is
  88 s, but its hashing passes and the extra raw bytes still put it well above Opus.
- **Safer for the measurement: Opus.** Inside cool-down it uses about 3x less CPU (about 70 against about 200 CPU-s: Sol's two SHA-256 passes, the rsync checksum pass and ssh encryption of the raw bytes) and about 8x less busy and radio time, its 120 s margin
  before the dwell is larger, and the triage receipt feeds the frozen `quiet_start_state` check.
- **Safer for custody: Opus.** Its second copy is off-site and proven by a round trip; Sol's is a second disk in the
  same machine, and that disk does not exist yet.
- **Safer for the software interlock and integrity edges: Sol.** It has the shared loop lock and lease, the terminal
  evidence check, the complete-envelope rule, the hard-link refusal, challenge-fresh receipts that re-hash at
  deletion, a dedicated account with a root-owned script, a monotonic deadline with an alarm, and an explicit
  deletion journal.

## 4. Merged recommendation

Take **Opus as the base** (compression, transport, iCloud round-trip proof, timing and triage receipts, measured
budget) and add Sol's interlocks and integrity edges. Each item is small:

1. **Interlock (Sol).** When the magistrate wires it, the lease file and shared persistent loop lock are the primary
   armed/measuring exclusion. `run` takes the loop lock and checks the lease (`phase == cooldown`, generation
   unchanged, `record_manifest_sha256` equal, `fenced_checkouts == []`) before each stage. The Opus LaunchAgent/ps
   probe stays as a backstop for the period before wiring and as a second opinion afterwards.
2. **Terminal evidence (Sol).** Before pack, check `result.json` verdict and `ended_epoch_s`, the chain markers, no
   `chain.unkilled`, and `courier.sent`.
3. **Complete envelope (Sol).** Refuse unlisted regular files, hard links (`st_nlink != 1`), `.git` and
   `restricted` members, instead of reporting and keeping them. This makes the open finalize-manifest item a hard
   precondition, which it should be.
4. **Fresh receipts at release (Sol, made cheap).** `receipts` takes the MBP's nonce. The Air re-hashes the
   **compressed parts** (about 1.6 GB, a few seconds, not Sol's about 53 GB raw) and re-reads the sealed
   second-copy receipt before answering. The raw tree on the Air is a derived convenience; the parts are the custody
   object.
5. **Confinement (Sol).** A dedicated `jw-offload` account, the gate script root-owned under `/usr/local/libexec`,
   `-F /dev/null` with an explicit `UserKnownHostsFile`.
6. **Deadline mechanism (Sol) with the Opus margin.** A monotonic deadline from the lease or `--deadline-epoch`, a
   `SIGALRM` backstop and a process-group kill, keeping the 120 s pre-dwell margin and the measured-rate prediction.
7. **Deletion journal (Sol).** Write `deleting`, then `deleted`, with the inventory outside the record. On resume,
   re-check the remaining files' size and mtime.
8. **Manifest formats.** Accept the union: `ssd_closed_record.v1`, `closed_record.v1`, `harvest_window.v1`,
   `r1_harvest_manifest.v1`, `SHA256SUMS`. One envelope then serves either storage option.
9. **Second copy.** The default is iCloud with the round-trip proof (Ed's brief, off-site). Sol's `backup-once` to a
   physically independent disk is an allowed alternative proof of the second copy if Ed attaches one. Either counts
   only with a sealed, re-checkable receipt.

Kept from Opus without change: zstd -3 -T4 (level 1 if the first real cool-down trace shows any lengthening), no raw
hashing on the MBP by default (`--hash-on-mbp` stays available), `rates.json` prediction, the default pressure
policy `hold` with opt-in `--pressure-compressed-local` (two verified copies still exist), and the span/triage files.

**Merged per-window cost (expected):** D at 50 MB/s is about 1.5 min of MBP work and about 3.5 min end to end,
including the cheap fresh-receipt check. Turnaround impact is zero while cool-down is at least about 7 min.

**Not decided here:**
- Ed's choice between this Air option and the SSD-on-MBP option.
- The W1/D finalize manifest writer.
- The magistrate-side lease and lock wiring (a magistrate change, so a lead ruling and the magistrate's own review).

**Process note.** Under item 220 the next step is a merged build. Both families should review the diff of items 1-9
before the lead rules. Nothing here is installed, and neither build has run over real SSH.
