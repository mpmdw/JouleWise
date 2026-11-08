# Air offload: closed window records from the MBP to the Air's external SSD (merged build)

Author: Opus 5.5 (laptop lead's delegate), 2026-11-08. Branch `ops/2026-11-08-air-offload-merged`, built on the
Opus build (`ops/2026-11-08-air-offload-opus` @ `7e0c264e0`) with the Sol build's interlocks and integrity edges
(`ops/2026-11-08-air-offload` @ `daecbbc28`), as recommended in `docs/ops/AIR-OFFLOAD-AGREEMENT.md` §4 items 1-9.
This document replaces `AIR-OFFLOAD-opus.md` (deleted here) and Sol's `AIR-OFFLOAD.md` (on its own branch).

Code: `scripts/offload_window.py` (standard library only, Python >= 3.11), tests `tests/test_offload_window.py`
(96 tests); operator setup `scripts/offload_setup_air.sh` (sudo, Air) and `scripts/offload_setup_mbp.sh` (no sudo,
MBP); benchmark `scripts/offload_bench.py`; seed rates `configs/ops/air_offload_rates.json`.

**Status: built and tested off the MBP; nothing installed.** No ssh, no MBP contact, no account, key or
LaunchAgent was created. The operator steps in §3 need Ed (sudo on the Air) and the magistrate (MBP).

## 0. Bottom line

- **Where it runs:** on the MBP at the start of cool-down, after finalize, commit and push, and only then. It
  refuses to start, or stops resumably, so that all of its activity ends at least 120 s before the dwell.
- **One pack per window (lead ruling 2026-11-08).** An ALIGN v4 session (a `finalized_manifest.v2` record) is
  packed once, by the harvest-off lane (`harvest_offload.pack`, step 1c of its runbook). This tool **consumes that
  pack** (`run --harvest-pack <dir>`): it checks it against the committed finalize digest, then transports,
  second-copies, receipts and releases it. It never repacks. Its own pack (`run --pack`) remains only for R1 and
  legacy manifests, and refuses a v2 record.
- **Cost per D window (26.4 GB raw), measured with the single pack (§8):** the harvest-off pack is about 69 s
  (zstd -3 -T4, it hashes every file as it packs); this tool then adds on the MBP about 0.1 s of metadata checks and
  the push of about 1.65 GB (about 33 s at 50 MB/s, 6 s at 300 MB/s). MBP pack + push: about 102 s, against about
  143 s with two packs. The Air verifies the consumed pack in about 47 s and writes no second raw tree. Admission
  estimate (×1.5) for this tool's part: about 2.2 min, against a 15-25 min cool-down.
- **Custody:** the MBP deletes a window only after (1) a sealed Air receipt that every raw file matched the
  record's own sha256 digests, (2) a sealed second-copy receipt (default: iCloud, server-confirmed by an
  evict/re-download/sha256 round trip, off-site), and (3) a **fresh** receipt: at release time the Air re-hashes the
  compressed parts and both manifests for the MBP's nonce. The deletion is journaled and resumable.
- **The Air's landing store** is `/Volumes/JW-EXT/jw-offload`, bound by APFS volume UUID at an explicit
  `init-store` step. Every gate call refuses if the volume is not mounted, is a different volume, lost its marker,
  ignores ownership, or (for writes) is below the free floor (default 100 GiB). The Air's internal disk keeps no
  copy: the iCloud worker evicts after confirming.
- **Which interlock is active:** today the **LaunchAgent/ps probe** (as in the Opus build). The magistrate lease and
  shared loop lock client is built and tested, and takes over as the primary exclusion as soon as the magistrate
  passes `--lease/--watchdog-state/--loop-lock` (§5). That wiring is a magistrate change and needs its own review.

## 1. The nine agreement items, and what was kept

| # | Item | How it is done here |
|---|---|---|
| 1 | Interlock (Sol) | `Lease` client: takes the magistrate's **existing** persistent loop lock (`flock`, never creates the file), reads the lease `joulewise.air_offload_gate.v1` and the watchdog state before every stage (each part, each upload, verify, release): `phase == cooldown`, not armed or measuring, same `generation`, same `record_manifest_sha256`, `record_committed` and `record_pushed`, `fenced_checkouts == []`. Its deadline is `min(quiet_dwell, expires) − 120 s`. The probe always runs too. The span records `interlock.mode` (`probe_only` or `lease+loop_lock+probe`) |
| 2 | Terminal evidence (Sol) | `--terminal <record-relative result.json>` (or an absolute path, see below) is required. Before pack: the file is listed and its bytes match the manifest digest; `plan_id`, a known verdict (`GO`, `ABORTED`, `COLLECTED`, `CHAIN_STOPPED`, `REFUSED`) and a past `ended_epoch_s`; `chain.started` has `chain.exited` (or a zero-capture `REFUSED` with neither); no `chain.unkilled`; `courier.sent`. Every marker must be a listed regular file. `--no-terminal-check` is accepted only for window ids starting `smoke-` or `bench-` |
| 3 | Complete envelope (Sol) | The record tree must equal the manifest's envelope. Unlisted file, unlisted symlink, unlisted directory (v2 lists all), special file, hard link (`st_nlink != 1`), `.git` or `restricted` member: exit 2, before any pack or network. The walk never enters a `.git` or `restricted` directory. A listed entry that is missing, of another type, another size or another link target: exit 3. A manifest that lives inside the record (for example `ssd-closed.json`) travels as a file under its pinned digest |
| 4 | Fresh receipts, cheap (Sol, Opus cost) | `receipts W NONCE`: the Air re-hashes the custody objects (the compressed parts, `offload-manifest.json`, `record-manifest.bin`, read with `F_NOCACHE`), re-reads and re-checks the sealed second-copy receipt, and returns a sealed fresh receipt bound to the nonce and both receipt hashes. The raw tree is a derived convenience and is not re-hashed. A replayed answer or a decayed part refuses (exit 3) and nothing is deleted |
| 5 | Confinement (Sol) | `scripts/offload_setup_air.sh`: dedicated hidden non-admin account `jw-offload`, root-owned gate script in `/usr/local/libexec/jw-offload/`, root-owned `authorized_keys` and binding in `/usr/local/etc/jw-offload/`, an sshd `Match User jw-offload` block (`ForceCommand`, publickey only, no TTY or forwarding). MBP ssh uses `-F /dev/null`, an explicit `UserKnownHostsFile`, `GlobalKnownHostsFile=/dev/null`, `StrictHostKeyChecking=yes`, `BatchMode` |
| 6 | Deadline mechanism (Sol) with the Opus margin | The deadline is held on the monotonic clock (a wall-clock step cannot extend it). A `SIGALRM` backstop at the deadline interrupts blocking I/O; `SIGTERM` unwinds the same way; both exit 4 with state kept. ssh and zstd run in their own process groups, killed as a group on any exit path. The 120 s pre-dwell margin and the `rates.json` × 1.5 admission are kept |
| 7 | Deletion journal (Sol) | `deleting.json` (state `deleting`, the inventory of every file and link to delete with size and mtime or link text, the fresh receipt's hash) is written outside the record before the first unlink, and set to `deleted` at the end. A resumed release re-checks every remaining entry and refuses any new file in the record |
| 8 | Manifest formats | `joulewise.align_v4.finalized_manifest.v2` (the harvest-off lane; consumed with its pack, §1a), `joulewise.ssd_closed_record.v1`, `joulewise.closed_record.v1`, `joulewise.harvest_window.v1`, `joulewise.align.r1_harvest_manifest.v1`, `SHA256SUMS`. Anything else, including schema-less JSON, refuses |
| 9 | Second copy | Default `air-icloud` (round-trip proof, off-site, evicted afterwards; holds when the Air's internal disk is below 15 GiB free). Allowed alternative `air-second-disk` onto a bound store whose volume UUID differs **and** which shares no APFS physical store with the primary (probed live with diskutil). Either counts only with a sealed receipt that matches the custody objects and names the primary store's volume UUID |

Kept from the Opus build without change: zstd -3 -T4 in tar parts (2 GiB raw), no raw hashing on the MBP by
default (`--hash-on-mbp` stays), the `rates.json` prediction (now seeded from `configs/ops/air_offload_rates.json`),
the 120 s pre-dwell margin, the default pressure policy `hold` with opt-in `--pressure-compressed-local`, the
append-only resumable `put`/`commit` transport, and the timing receipts `timing/offload-start.json` and
`timing/offload-span.json` (`kind: backup`) plus the `triage` command for `quiet_start_state`.

### 1a. finalized_manifest.v2 records: one pack, consumed (lead ruling 2026-11-08)

The harvest-off pack directory (`$OUT/offload`: `payload.tar.zst` + `MANIFEST.json`, schema
`joulewise.align_v4.harvest_offload.v1`) is the record's only pack. `run --harvest-pack $OUT/offload` does, with
no raw or payload hashing on the MBP:

1. The record checks as for any record: the finalize manifest's bytes match the pinned digest `H`; the session
   root equals its `source_root` and is exactly its envelope (every file, literal link and directory); the terminal
   evidence holds.
2. The transport manifest is checked against the finalize manifest, as `harvest_offload.unpack` does:
   `finalized_manifest_sha256 == H`, the same `source_root`, its entries equal the finalize entries exactly, every
   `.external/NNNN` member is a declared closure input with the bound bytes, and the payload has its recorded size.
   Any difference is exit 3 and nothing is sent.
3. The payload, `MANIFEST.json`, the finalize manifest (as `record-manifest.bin`) and the offload manifest are
   pushed under their sealed digests. The Air's `commit` re-hashes each one.
4. The Air verify re-derives every expected row from the pinned finalize manifest (not from the MBP's offload
   manifest), re-checks `MANIFEST.json` against it, then streams the payload and checks every member: files by
   sha256 and size, links by text, directories, and the bound external inputs. A member outside the finalize
   manifest is exit 3. It writes **no raw tree**: for a v4 session the raw tree is the harvest restore at the
   session's own path.
5. The custody objects (payload, `MANIFEST.json`, both manifests) are second-copied, rechecked fresh at release
   and, after two copies, deleted from the pack directory together with the session's files (the directory goes if
   empty). The closure's external inputs (the calibration ledger) are never moved here and never deleted.

**The harvest restore reads the verified copy in place.** The store keeps the harvest names, so on the Air:
`$RUN unpack --offload /Volumes/JW-EXT/jw-offload/inbox/$K --finalized-manifest
/Volumes/JW-EXT/jw-offload/inbox/$K/record-manifest.bin --finalized-sha256 $H`. This replaces the separate
transfer of `$OUT/offload` in the harvest-off runbook's step 1d. Checked end to end with the real
`harvest_offload.unpack` (§9).

**Terminal evidence (lead ruling 2026-11-08).** `result.json`, `chain.*` and `courier.sent` must be inside the
finalize manifest's closure: either files of the session root (`--terminal night/result.json`, record-relative),
or, if the native layout puts them outside the session root, declared as external inputs of
`finalized_manifest.v2` by the harvest-off finalize (bound by bytes), and named by absolute path
(`--terminal /abs/.../night/result.json`). Then every marker that exists on disk must be a bound input with
matching bytes, and every bound marker must exist. A marker present but unbound refuses (exit 2), a bound marker
absent or changed is exit 3. The magistrate's N1 native census confirms which layout is real; declaring the inputs
is a harvest-off finalize change, not this tool's.

## 2. Design

```
MBP (after finalize, commit, push; start of cool-down)        Air (on 24/7; /Volumes/JW-EXT/jw-offload)
 run --terminal night/result.json --deadline-epoch <dwell - 120 s>
     [--lease L --watchdog-state W --loop-lock K]  (once wired)
  1 loop lock + lease (if given); probe (always)
  2 predict from rates.json (seeded); refuse if x1.5 does not fit
  3 release older windows: receipts W NONCE ----------------->  re-hash parts + manifests (F_NOCACHE),
       journal deleting -> unlink -> journal deleted              re-read the sealed second receipt
  4 envelope + terminal check; pack: tar parts -> zstd -3 -T4
  5 push: hello, stat, put/commit per file  ------------------>  store check (mounted, UUID, marker, floor);
                                                                 commit checks each sha256
  6 verify ---------------------------------------------------->  re-hash parts, decompress, check EVERY raw
                                                                 file (and link, dir) against the record
                                                                 manifest; raw tree; sealed receipt; queue
  7 release this window if a second copy exists (usually next turnaround)
  8 timing/offload-span.json                                   air-icloud (Ed's LaunchAgent, every 5 min):
                                                                 copy custody objects to iCloud Drive, evict,
                                                                 download, sha256 match -> sealed receipt in
                                                                 second/W/; evict again
```

Store layout on the SSD: `inbox/W/` (the custody objects: parts and both manifests), `windows/W/raw/` (the
verified raw tree) and `air-receipt.json`, `queue/W.json`, `locks/` (all owned by `jw-offload`), `second/W/`
(second-copy receipts, owned by Ed, because iCloud runs as Ed), and the root-owned marker
`.jw-offload-store.json`. The binding `/usr/local/etc/jw-offload/store-binding.json` records the store root, mount
point, volume UUID, store id and free floor.

## 3. One-time setup (operator steps; nothing here has been run)

### 3a. Air, Ed, once (sudo), about 10 min

1. Make a clean checkout of this branch at the **reviewed** sha (for example
   `~/code/CapstoneProject/jw-wt/offload-gate`), outside a window.
2. On the MBP first (3b step 1), get `jw_offload_ed25519.pub` and the MBP's LAN address, and copy the public key to
   the Air (AirDrop is fine; it is not secret).
3. Run, from that checkout:
   ```sh
   sudo bash scripts/offload_setup_air.sh --mbp-pubkey ~/Downloads/jw_offload_ed25519.pub --mbp-from <MBP IP or CIDR>
   ```
   It is idempotent and does, in order:
   - **`diskutil enableOwnership /Volumes/JW-EXT`.** The volume currently ignores ownership (`noowners`), which
     would let any account write anywhere on it. If enabling it leaves `/Volumes/JW-EXT` or `backups/` owned by
     `_unknown` (uid 99), it chowns them back to Ed. This is the only change near `backups/`: its owner, never its
     contents. `mdutil -i off` stays.
   - Creates the hidden, non-admin account `jw-offload` (shell `/bin/sh` so `ForceCommand` can run; root-owned home,
     so no rc files or keys), and adds it to `com.apple.access_ssh` if that group exists.
   - Installs `offload_window.py` root-owned at `/usr/local/libexec/jw-offload/` (it refuses a checkout whose copy
     differs from HEAD) and prints its sha256.
   - Runs `init-store` (binds `/Volumes/JW-EXT/jw-offload` to the volume UUID, refuses an internal disk or a volume
     that ignores ownership, free floor 100 GiB), then hands the store to `jw-offload:staff` (0750) and `second/` to
     Ed.
   - Writes the root-owned `authorized_keys` line `restrict,from="<MBP>",command="<gate>" ssh-ed25519 ...`.
   - Writes `/etc/ssh/sshd_config.d/050-jw-offload.conf` (the `Match User jw-offload` block) and removes it again if
     `sshd -t` rejects it. A `Match` block in an included file ends with that file, so Ed's own logins are unchanged
     (checked here with `sshd -T` against a scratch copy of this Air's config).
   - `pmset -c sleep 0 disksleep 0` (awake on power; the display may sleep).
   - Installs and bootstraps Ed's LaunchAgent `com.joulewise.offload-icloud` (every 300 s, background, low-priority
     I/O), which runs `air-icloud` from the root-owned copy.
4. **Remote Login** (System Settings > General > Sharing): on, with "Only these users" including `jw-offload`. If
   `hello` later fails with "Operation not permitted" on `/Volumes/JW-EXT`, tick "Allow full disk access for remote
   users".
5. Read the host key fingerprint for the MBP pin: `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`.
6. iCloud: about 1.6 GB per D window (synthetic ratio; real data compresses better), so about 40 GB of quota for
   25 windows.

### 3b. MBP, magistrate, once (no sudo)

1. `bash scripts/offload_setup_mbp.sh --air-host Edrs-MacBook-Air.local` creates `~/.ssh/jw_offload_ed25519` and
   prints the public key for 3a.
2. After 3a, pin the host key: `bash scripts/offload_setup_mbp.sh --air-host Edrs-MacBook-Air.local
   --expect-fingerprint SHA256:<from 3a step 5>`. It writes `~/.ssh/jw_offload_known_hosts` only on a match.
3. Smoke test with no window involved: a dummy record (any small directory, its `shasum -a 256` list as
   `SHA256SUMS`) and a fresh id:
   ```sh
   python3 -B scripts/offload_window.py run --state-root ~/code/CapstoneProject/jw-wt/offload-state \
     --window-id smoke-YYYYMMDD --record-root <dir> --record-manifest <dir>.SUMS \
     --record-manifest-sha256 "$(shasum -a 256 <dir>.SUMS | cut -d' ' -f1)" --no-terminal-check
   ```
   Exit 0 and `outcome: verified_on_air` prove the forced command, the key, the host pin, the store binding and the
   Air verify. Within about 10 min the Air writes `second/smoke-YYYYMMDD/second-copy-receipt.json` (iCloud round
   trip); a second `release` call then deletes the dummy record.

## 4. Per-window magistrate sequence

| When | MBP step | Notes |
|---|---|---|
| Window terminal | finalize, hash, commit and push (unchanged), including the record manifest whose sha256 the record pins | For ALIGN v4: the harvest-off runbook's 1b (`finalize-manifest`, digest `H`) and 1c (`pack --threads 4`, the single pack; the CLI's default `--threads 0` uses every core) |
| Cool-down start `t_c` | v4: `offload_window.py run --state-root S --window-id K --record-root <session root> --record-manifest $OUT/finalized_manifest.json --record-manifest-sha256 H --harvest-pack $OUT/offload --terminal <result.json> --deadline-epoch <planned dwell start − 120>`. R1 or legacy: the same with `--pack` instead of `--harvest-pack` | One call; prints the span. Exit 0 = verified on the Air. Without a planned dwell start, `t_c + 900 − 120` is safe |
| Right after | Commit `S/K/timing/offload-span.json` into the record branch | `window_timing --span offload=<path>` reads it; `kind: backup` maps to `offload` |
| Pre-arm checks | `offload_window.py triage --state-root S --window-id K --dwell-start-epoch <planned>` | Evidence for `quiet_start_state`; exit 2 if an offload is running, started without an end receipt, or ended within 120 s of the dwell |
| Dwell, arm | unchanged | |

The next turnaround's `run` releases older windows whose second copy has landed (`release_older`), each with a
fresh receipt; `release --state-root S --window-id K` does the same for one window by hand.

## 5. Interlock: active today, and the magistrate contract

**Active today: the probe.** `run` refuses (exit 2) when a `com.joulewise.night*`, `com.joulewise.align-*` or
`com.joulewise.b6*` LaunchAgent plist exists or a measuring process is alive (`powermetrics`, `run_night.py`,
`align_v4_session.py`, `align_r1_rehearsal.py`, `align_r0_checks.py`, `run_campaign.py`, `mlx_lm`), and re-checks
before every part, upload, verify and release. It also holds its own `flock` (`S/.lock`), which `triage` reads.
This is a heuristic, not a mutual exclusion with the arm.

**Built, not active: the lease and loop lock.** The magistrate activates it by passing all three flags; then the
lease is the primary exclusion and the probe a second opinion. The contract (from the Sol build, unchanged):

- The magistrate uses **one persistent lock file** for every transition into arm, measure and dwell, never unlinks
  or replaces it, and invalidates the lease under that lock before publishing any armed plan. `run` takes the same
  lock (`--loop-lock`) and holds it for the whole offload; it never creates the file.
- Publish the lease under the lock, release the lock, then call `run` (do not hold it in the parent).
- The lease file (`--lease`), written atomically per cool-down with a new generation:
  ```json
  {"schema": "joulewise.air_offload_gate.v1", "generation": "cooldown-<K>-<n>", "phase": "cooldown",
   "armed": false, "measuring": false, "record_manifest_sha256": "<H>", "record_committed": true,
   "record_pushed": true, "quiet_dwell_epoch_s": <planned dwell start>, "expires_epoch_s": <lease expiry>}
  ```
- `--watchdog-state` is the watchdog's state file; `fenced_checkouts` must exist and be `[]`.
- Deadline: `min(quiet_dwell_epoch_s, expires_epoch_s) − --lease-margin-s` (default 120), and also
  `--deadline-epoch` if given (the earlier wins).
- A changed generation or record pin refuses (exit 2), an expired lease stops (exit 4); state is kept either way.

## 6. Second copy

- **iCloud (default).** `air-icloud` (Ed's LaunchAgent) copies each queued window's custody objects (parts and both
  manifests, about 1.6 GB per D window) into `~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-offload/W/`,
  evicts each file to a dataless placeholder, downloads it again and checks sha256, then evicts again. Only then
  does it write the sealed receipt into `second/W/`. A placeholder that downloads again with matching bytes came from
  the server. It holds (and logs to `second/errors.jsonl`) while the internal disk would drop below 15 GiB free.
- **Second disk (allowed alternative).** Bind a store on another physical disk with
  `init-store --role second --store-root /Volumes/<OTHER>/jw-offload-second --binding <file>`, then schedule
  `air-second-disk --second-binding <file>`. It refuses unless the volume UUIDs differ and the two volumes share no
  APFS physical store (so two volumes on the one SN7100 never count), copies with `F_NOCACHE` and re-reads from the
  disk.
- The gate cannot read Ed's iCloud folder, so the fresh recheck at release re-reads the sealed second receipt but
  does not re-download the iCloud copy.

## 7. Failure handling

| Exit | Meaning | Magistrate action |
|---|---|---|
| 0 | Verified on the Air (release may be held for the second copy) | Commit the span |
| 2 `window_armed` / `window_measuring` / `lease_*` / `loop_lock_busy` | Not in a clean cool-down | Do not offload now; the next turnaround retries |
| 2 `envelope_*` / `terminal_*` / `record_is_not_terminal` / `record_manifest_unsupported` | The record is not a closed, terminal envelope | Fix the finalize manifest (lead); nothing was sent |
| 2 `offload_already_running` | Another run holds the lock | Wait; triage refuses the arm until it ends |
| 3 `*_mismatch`, `record_changed*`, `raw_digest:*`, `air_part_decayed:*`, `fresh_receipt_*`, `changed_during_deletion:*`, `window_id_conflict*` | Integrity failure; nothing deleted | Keep everything. Report to the lead with the span and `offload-journal.jsonl`. Do not retry blindly |
| 4 `deadline:*`, `deadline_alarm`, `interrupted_sigterm` | Predicted or actual overrun, or killed | State kept; the next turnaround resumes |
| 5 `air:store_*`, `air_ssd_space`, `transport_*` | Air asleep or unreachable, SSD unmounted or a different volume, below the free floor | The MBP keeps the window; the next turnaround resumes. A UUID mismatch needs Ed |
| 6 `io_error` | e.g. ENOSPC on the MBP | Disk guard; the arm's own disk checks still apply |

Restoring needs no code: `zstd -dc part-NNNN.tar.zst | tar -x` (or `payload.tar.zst` for a v4 session; the
harvest-off `unpack` is the checked route) on any Mac, then check against the record manifest
(done in the end-to-end test, §9).

## 8. Measured rates (2026-11-08, Apple M4 Air, real SSD)

`scripts/offload_bench.py --store-root /Volumes/JW-EXT/jw-offload-test/store --members 8 --skip-codecs`: the real
code path on 8 synthetic pilot-v3 members (4.05 GB raw) calibrated on the real Mac15,9 captures, store bound to the
real JW-EXT volume by diskutil UUID. The Air was shared with other lanes: one run at load average 3.9, three at
5-12.

| Stage | Quiet (load 3.9) | Loaded (load 5-12), median of 3 | Seed in `rates.json` |
|---|---|---|---|
| Pack, zstd -3 -T4 (MBP code path, on the Air) | 2,184 MB/s raw, 1.3 CPU-s/GB | 646 MB/s raw, 3.0 CPU-s/GB | 500 (M3 Max single-thread tar loop, about −20 %) |
| Pack, zstd -3 -T1 | 1,397 MB/s, 1.3 CPU-s/GB | 605 MB/s, 2.7 CPU-s/GB | — |
| Air verify (re-hash parts, decompress, sha256 every raw file, write the raw tree to the SSD) | 1,253 MB/s raw | 472 MB/s raw | 450 |
| Receipt recheck (re-hash compressed parts, `F_NOCACHE`) | 2,255 MB/s | 1,172 MB/s | — |
| Receipt recheck, cold (parts written with `F_NOCACHE`, re-read from the SSD) | — | 953 MB/s | 900 |
| Compression ratio (synthetic; real captures compress better) | 16.1 | 16.1 | 16.0 |
| Full store check (`diskutil` UUID probe), per `hello`/`stat`/`verify`/`receipts` call | — | 0.14 s | — |

**The single pack (lead ruling 2026-11-08)**, `offload_bench.py ... --harvest-offload <harvest_offload.py>`: the
harvest-off lane's real `pack` on the same 8 members (finalize manifest written first, 3.3 s), then this tool's
adopt and the Air verify of the consumed pack. Median of 3 at load 8-11:

| Stage | zstd -3 -T4 | zstd -3 -T0 (the harvest CLI default) |
|---|---|---|
| `harvest_offload.pack` (MBP; it hashes every file while packing) | 383 MB/s raw, 3.95 CPU-s/GB | 444 MB/s, 3.68 CPU-s/GB |
| This tool's adopt (envelope scan, transport manifest against the finalize manifest) | 0.01 s | 0.01 s |
| Air verify of the consumed pack (payload re-hash, decompress, every member; no raw tree written) | 561 MB/s raw | 692 MB/s raw |
| Fresh recheck | 1,203 MB/s | 1,432 MB/s |

**D window (26.4 GB) on the MBP, re-measured with the single pack** (the M3 Max will differ; the next real window's
span measures it): harvest pack about 69 s (T4) + this tool's adopt about 0.1 s + push about 33 s at 50 MB/s = about
**102 s**, against about 143 s with two packs (harvest pack 69 s + this tool's pack 41 s at the loaded 646 MB/s +
push 33 s). The pack time belongs to the harvest-off lane's step 1c; this tool's own MBP work is the push.

The Opus build's earlier figures (pack 490 MB/s, verify 265 MB/s) were taken on a busier Air; all of these vary
about 3-4x with load, so the seed uses the loaded medians. Push is not measured (Wi-Fi) and stays at 40 MB/s. The
first real offload replaces every seed with observed rates.

**Per-window end to end at the seed rates** (push at the network rate, ratio 16, the previous window's fresh
recheck, 10 s of call overhead; about 30 gate calls per D window at about 0.1-0.15 s each plus ssh):

| Window | Network | Pack (MBP) | Push | Verify (Air) | Recheck | Total | ×1.5 admission |
|---|---|---|---|---|---|---|---|
| W1, 18.6 GB | 50 MB/s | 37 s | 23 s | 41 s | 1 s | **113 s** | 170 s |
| W1 | 300 MB/s | 37 s | 4 s | 41 s | 1 s | 94 s | 141 s |
| D, 26.4 GB | 50 MB/s | 53 s | 33 s | 59 s | 2 s | **156 s** | 234 s |
| D | 300 MB/s | 53 s | 6 s | 59 s | 2 s | 129 s | 194 s |

The MBP is busy only for pack and push (D: about 86 s at 50 MB/s, about 70 CPU-s at the loaded 3.0 CPU-s/GB or
about 35 at the quiet 1.3); during the Air verify it holds one idle ssh session. Expected turnaround impact: zero
while cool-down is at least about 6 min (admission plus the 120 s margin). Measurement-safety reasoning (heat at the
start of cool-down, Wi-Fi only, nothing on the MBP's DC-in channel) is unchanged from the Opus build: the first
real window should record the cool-down thermal trace with the span, and drop to `--level 1 --threads 2` if
cool-down lengthens measurably.

## 9. Evidence

- `TMPDIR=/private/tmp/... python3.13 -B -m unittest tests.test_offload_window`: 96 tests, OK (including the
  consumed harvest pack: no repack, pack bound to another finalize, entries or externals that differ, a corrupt
  payload, a smuggled member, and terminal evidence as bound closure inputs) (happy path,
  envelope, v2 links and dirs, terminal evidence, lease and loop lock, store binding, deadline incl. the `SIGALRM`
  backstop and process-group kill, the two-copy rule with fresh receipts, the deletion journal, the second-disk
  alternative, the local subprocess gate, the setup scripts' syntax). `tests.test_offload_bench`: OK.
- End to end with the single pack (same setup as below): the real `harvest_offload.finalized_manifest(...,
  inputs=(ledger,))` and `harvest_offload.pack(threads=4, external=(ledger,))`; `run --pack` refused the v2
  record; `run --harvest-pack` verified it on the Air in 2.25 s (22 files, 2 links, 15 dirs, 1 external; no raw tree
  extracted); a payload decayed after the receipts made release fail closed (`air_part_decayed:payload.tar.zst`);
  release then deleted the session's files and links and the consumed pack, left the ledger, and the real
  `harvest_offload.unpack` restored the session from `/…/inbox/e2e-w1` at its own path with every digest
  matching.
- End to end on the real SSD (`/Volumes/JW-EXT/jw-offload-test`, removed afterwards), first round, own pack: a 1.01 GB synthetic terminal
  record with a manifest written by the harvest-off lane's own `harvest_offload.finalized_manifest()`, the real
  CLI (`run`, `release`, `triage`, `init-store`, `air-second-disk`), the gate as a real subprocess with the
  forced-command protocol (`--air-local-binding`), the real diskutil probe. Results: verified on the Air in 5.1 s;
  the raw tree matched every v2 entry (files, literal links, empty directory); a second run was a no-op; release
  held without a second copy; `air-second-disk` refused a second store on the same SSD
  (`second_disk_not_physically_independent`); a part decayed after the receipts made release fail closed
  (`air_part_decayed`, exit 3, nothing deleted); after repair, release deleted 22 files and 2 links and left the
  external ledger untouched; triage passed; a plain `zstd -dc | tar -x` restore matched the manifest. `init-store`
  without `--allow-noowners` refused the volume as it is today (`store_volume_ignores_ownership`). iCloud was
  simulated (no upload of test data).
- The sshd snippet was checked with `sshd -t` and `sshd -T -C user=...` against a scratch copy of this Air's
  `sshd_config` with a temporary host key; nothing was installed.

## 10. Before the first real window

1. **Ed:** §3a on the Air (sudo), including Remote Login; this also enables ownership on JW-EXT.
2. **Magistrate:** §3b on the MBP, then the smoke test (§3b step 3) and one iCloud round trip on it.
3. **Terminal layout (ruled):** the magistrate's N1 native census confirms where `result.json`, `chain.*` and
   `courier.sent` live. If outside the session root, the harvest-off finalize declares them as external inputs
   (§1a); until then the run refuses clearly (`terminal_not_in_manifest` / `terminal_not_in_closure`).
4. **One pack (ruled, built):** the harvest-off runbook's step 1c should pass `--threads 4` (its CLI default is
   `--threads 0`, every core), and its step 1d becomes `run --harvest-pack` here plus the in-place `unpack` (§1a).
   Both are harvest-off runbook edits.
5. **Magistrate wiring of the lease and loop lock** (§5): a magistrate change with its own review. Until then the
   probe is the active exclusion.
6. **Real-data calibration:** the first real offload's span and `rates.json` replace the seed rates; record the
   cool-down thermal trace with it.
7. **Reviews:** an Opus cold review and Sol seats on this diff before the lead rules (RUN_STATE item 220).
