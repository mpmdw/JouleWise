# MBP → Air offload between windows

`scripts/offload_to_air.py` implements option 2: the MBP pushes **one explicitly
named closed record** to the Air's SSD during cool-down. The Air verifies it,
publishes a hashed receipt over authenticated SSH, and queues a second-disk
copy. The MBP deletes only after a fresh receipt proves **two remote verified
copies**. Until then the MBP and Air SSD retain independent copies. A queued
upload, a partial copy, or an iCloud placeholder never authorizes deletion.

Status: **PROVISIONAL — synthetic tests only; not installed or exercised over
SSH/hardware.** This change supplies a hook and its interface; it does not modify
the magistrate, arm machinery, watchdog, or SSD-P1 branch. The lead must wire the
shared lock/lease contract below into the loop before enabling unattended use.
No per-window operator action is needed after that one-time integration/setup.

## Per-window sequence and loop contract

1. The existing loop finishes collection, proves the chain group stopped,
   finalizes/hashes the record, and commits/pushes its record metadata.
2. The magistrate reconciles **all** armed plans, refreshes its watchdog state,
   and publishes the cool-down lease described below. It calls `push` once,
   synchronously, while thermal cool-down is already running.
3. `push` checks the lease, the watchdog's `fenced_checkouts`, and the record's
   authenticated terminal files. It estimates the whole operation against the
   smaller of its budget, lease expiry, and quiet-dwell deadline, reserving a
   five-second dwell margin. An insufficient budget refuses before any network.
4. A status request first checks for an already verified Air record. Otherwise
   rsync pushes into `incoming/<manifest-sha256>/`. Interrupted transfers resume
   there; checksum comparison repairs differing partial bytes. No receipt exists
   for incoming data. A missing/extra file or any digest mismatch refuses.
5. The Air verifies all manifest files, fsyncs files/directories, and renames the
   stage into `records/<manifest-sha256>/`. It atomically queues a background job
   and returns a fresh receipt. MBP re-verifies its local record after transport.
6. The Air's separate `backup-once` job copies to a physically independent disk,
   verifies/fsyncs it, then records `confirmed` in `jobs/<id>.json`. This runs on
   the Air only, without an MBP connection. Later `push` calls re-hash both Air
   copies before returning a two-copy receipt. The next cool-down can therefore
   reclaim a previous window's retained local record without human intervention.
7. The MBP journals the receipt **outside** the record before deletion. A partial
   deletion can resume from that journal only after a fresh two-copy receipt
   and verification of every remaining local file. Repeated completed calls are
   idempotent. It never removes anything outside the exact supplied record.
8. The caller waits for the hook to exit and all MBP transport children to be
   reaped, then starts a **fresh full quiet dwell**, then arms the next window.
   A refusal/timeout retains evidence; retry only in cool-down. Never overlap
   offload, receipt polling, or local cleanup with dwell/arming/measurement.

The magistrate must use the **same persistent `flock` file** for every transition
into arming, measurement, and dwell, as this tool uses for offload. Never unlink
or replace this lock file. Under that lock, transitions atomically invalidate
the lease *before* publishing/installing any armed plan. An armer must wait for
offload to finish before crossing the boundary. Snapshot files alone do not
provide mutual exclusion. Do not wrap the `push` subprocess in a lock the parent
still holds: publish the lease under the lock, release it, then invoke `push`,
which acquires and holds it itself. The loop is sequential; if another transition
wins that gap, `push` rechecks and refuses.

`--armed-state` is a new, magistrate-owned projection, written atomically outside
custody. Its timestamps below are illustrative; the magistrate derives fresh
ones per cool-down, with a new generation and the **committed manifest pin**:

```json
{
  "schema": "joulewise.air_offload_gate.v1",
  "generation": "cooldown-window-EXAMPLE-1",
  "phase": "cooldown",
  "armed": false,
  "measuring": false,
  "record_manifest_sha256": "<64 lowercase hex characters>",
  "record_committed": true,
  "record_pushed": true,
  "quiet_dwell_epoch_s": 1800000600,
  "expires_epoch_s": 1800000600
}
```

`record_committed` / `record_pushed` attest the caller's completed steps; this
tool does not perform Git operations. `--watchdog-state` is the explicitly named
native magistrate watchdog state file; `fenced_checkouts` must exist and equal
`[]`. The magistrate must refresh it before issuing the lease. Missing, malformed,
armed, expired or changed state refuses. The tool never discovers plans, scans
custody parents, invokes a census with default data paths, or follows absolute
references in a manifest. Lease checks repeat during hashing and transport.
Monotonic time bounds the budget even if the MBP wall clock moves backwards.

`--terminal` is relative to the record. Its `result.json` must name a plan, carry
a finite past `ended_epoch_s`, and have a known terminal verdict (`GO`, `ABORTED`,
`CHAIN_STOPPED`, `REFUSED`, or the generic archive `COLLECTED`). Its sibling
`chain.started` must have `chain.exited`; `chain.unkilled` always refuses.
For a zero-capture `REFUSED`, both chain markers must be absent and chain digest
and exit code null/absent. `courier.sent` is required. All these files must be
covered by the record manifest. The magistrate's release remains responsible
for proving no surviving measurement processes; a copied marker alone cannot
prove machine liveness.

## Accepted closed-record manifests

The `--manifest-sha256` pin comes from finalization/committed metadata, never
from an untrusted remote receipt. The entire manifest is hashed separately.
Every regular file in the record, including terminal evidence, must appear
exactly once (except the manifest itself); every listed file must exist and
match size and SHA-256. No unlisted logs or metadata are silently ignored.
Symlinks (including parent components and links staying inside the record),
hard-linked files, special files, `.git` members, `restricted` members and
escaping/noncanonical relative names refuse. Closed records must stay immutable
while either the loop or receiver is handling them.

Supported formats:

- SSD-P1's existing `joulewise.ssd_closed_record.v1`, from
  `origin/align/2026-11-08-ssd-hooks:scripts/ssd_permanent.py`:

  ```json
  {"schema":"joulewise.ssd_closed_record.v1","state":"closed",
   "window_id":"example-window","files":{"payload.bin":"<64 hex>"}}
  ```

  The filename is `ssd-closed.json` (the CLI default). Every file, including
  terminal evidence, is listed by SHA-256. Sizes are read from the exact local
  files and bound into the receipt inventory after all digests match. No
  re-authoring is needed when switching between the two storage options.
- `joulewise.closed_record.v1`, an explicit complete closed-envelope manifest:

  ```json
  {"schema":"joulewise.closed_record.v1","closed":true,"files":{
    "payload.bin":{"sha256":"<64 hex>","size":1234},
    "night/result.json":{"sha256":"<64 hex>","size":100}
  }}
  ```

  This shortened example omits the remaining required terminal marker rows.
  Author the complete manifest during finalization, before committing its pin.
- Existing `joulewise.harvest_window.v1` `harvest.json`: relative `inventory`
  file digests under each archive prefix, plus the Revision 6 `r9_window`
  reference when present. Directory metadata is accepted but only file bytes
  and sizes define copy verification. Absolute `custody_root` and other source
  references are treated as text and never opened.

Other archive schemas refuse. Wrap such a record in a complete closed-envelope
manifest during its existing finalization step; do not reconstruct inventory
from missing files or silently reinterpret a study manifest. This hook neither
runs the block-5 pipeline nor releases or relocates sealed study inputs.

## One-time Air setup (owner/admin, outside a window)

These are deployment instructions, **not commands run by this implementation
session**. Use an approved copy of the script and a reviewed modern `rrsync`
supporting `-wo -no-del`. macOS's bundled rsync installation may not supply
rrsync; provision it on the Air through the owner's normal software process.
Use absolute, tested Python and rrsync paths in the commands below.

1. Create a dedicated standard account `jw-offload` with no sudo rights. Enable
   **System Settings → General → Sharing → Remote Login**, allowing only that
   account (and existing separately authorized admin access as needed). No
   server/daemon is installed on the MBP.
2. Install `offload_to_air.py` on the Air at
   `/usr/local/libexec/jw-air/offload_to_air.py`, owned by root and not writable
   by `jw-offload`. Keep its Python and rrsync executables similarly protected.
3. Create `/Volumes/JW-EXT/jw-air` on the Air's primary SSD, owned by
   `jw-offload`, mode 0700. Create `/Volumes/JW-SECOND/jw-air` on a **different
   physical disk**, likewise owned/mode 0700. An Air internal disk with enough
   space is also an independent destination; select its dedicated absolute
   directory instead. Different APFS volumes/partitions on the same SSD do
   **not** provide independent copies. Code rejects equal filesystem device
   IDs; the owner must establish physical independence at setup. Pre-create
   roots only on mounted destinations; do not auto-create a missing mount.
4. On the MBP, generate a dedicated automation key in an operations directory
   outside records (`ssh-keygen -t ed25519 -f /ABS/ops/air_offload_key -N ''`).
   Protect its directory/key as 0700/0600. Transfer only its public key to the
   Air through the owner's normal trusted setup route. In the account's
   `authorized_keys`, use a **single line**, substituting reviewed paths:

   ```text
   restrict,command="/opt/homebrew/bin/python3.13 -B /usr/local/libexec/jw-air/offload_to_air.py serve --root /Volumes/JW-EXT/jw-air --backup-root /Volumes/JW-SECOND/jw-air --rrsync /opt/homebrew/bin/rrsync" ssh-ed25519 AAAA... mbp-air-offload
   ```

   `restrict` disables forwarding, PTY and user rc execution. The forced
   dispatcher accepts only rsync server traffic (passed directly, with inherited
   protocol streams, to write-only/no-delete rrsync rooted at **incoming/**), or
   `jw-air status|verify <manifest-sha256> <manifest-name> <challenge>`.
   It never executes the supplied text through a shell. The key cannot request
   an interactive shell, arbitrary commands, reads through rsync, or writes to
   `records/`, `receipts/`, `jobs/` or the second disk through rrsync. If desired,
   add a `from=` restriction for the MBP's stable LAN address/CIDR.
5. Configure the account's sshd match block to require public-key authentication
   and disable password/keyboard-interactive authentication. Verify the forced
   key restrictions with the installed sshd/rrsync versions. Protect the key
   configuration from accidental editing by other accounts.
6. Pin the Air's host public key into `/ABS/ops/air_known_hosts` on the MBP after
   comparing its fingerprint through the Air console/trusted owner channel.
   The client uses strict host checking, batch mode, an explicit identity and
   known-hosts file, and `-F /dev/null`. Supply an actual DNS/Bonjour name or IP
   such as `jw-offload@air.local`; user SSH config aliases are not loaded.
7. Schedule this **Air-only** one-shot worker using launchd `StartInterval=60`
   and `RunAtLoad=true`, running as `jw-offload`. For a system LaunchDaemon,
   install a root-owned plist in `/Library/LaunchDaemons` with these keys:

   ```xml
   <key>Label</key><string>local.jw-air.backup</string>
   <key>UserName</key><string>jw-offload</string>
   <key>ProgramArguments</key><array>
     <string>/opt/homebrew/bin/python3.13</string><string>-B</string>
     <string>/usr/local/libexec/jw-air/offload_to_air.py</string>
     <string>backup-once</string>
     <string>--root</string><string>/Volumes/JW-EXT/jw-air</string>
     <string>--backup-root</string><string>/Volumes/JW-SECOND/jw-air</string>
   </array>
   <key>RunAtLoad</key><true/>
   <key>StartInterval</key><integer>60</integer>
   <key>StandardOutPath</key><string>/usr/local/var/log/jw-air-backup.log</string>
   <key>StandardErrorPath</key><string>/usr/local/var/log/jw-air-backup.err</string>
   ```

   Wrap these keys in the normal plist XML declaration/doctype and
   `<plist version="1.0"><dict>…</dict></plist>`; pre-create the log directory
   and writable logs. Validate with `plutil -lint`, then bootstrap the plist
   through the owner's normal launchd setup. Each invocation retries queued
   work; per-record locks serialize it with receipt generation. Missing mounts,
   copy failures and corruption leave jobs unconfirmed. Confirmed copies are
   re-verified when an MBP requests a deletion receipt. A changed/corrupt
   confirmed copy refuses rather than silently replacing evidence.

There is deliberately no iCloud-confirmation adapter in this version. An iCloud
folder can be an *additional* archive, but its local bytes/upload queue do not
prove server persistence or independence. Use the second physical disk path for
automatic deletion. With no available second destination, retain the MBP copy
and let disk pressure hold the loop automatically.

## MBP invocation and retention policy

The magistrate supplies these arguments from its own committed record and
fresh cool-down lease, with no interactive prompts:

```sh
python3.13 -B scripts/offload_to_air.py push \
  --record /ABS/closed-record \
  --manifest manifest.json --manifest-sha256 "$COMMITTED_MANIFEST_SHA256" \
  --terminal night/result.json \
  --armed-state /ABS/ops/offload-gate.json \
  --watchdog-state /ABS/ops/watchdog-state.json \
  --loop-lock /ABS/ops/window-loop.lock --state-dir /ABS/ops/air-offload-state \
  --host jw-offload@air.local \
  --identity /ABS/ops/air_offload_key --known-hosts /ABS/ops/air_known_hosts \
  --budget-s 2000 --transfer-mbps 50 --hash-mbps 100 \
  --bwlimit-kib 48828 --deadline-margin-s 5 \
  --delete-policy after-two --min-free-bytes 60000000000
```

For an existing harvest archive use `--manifest harvest.json` and, usually,
`--terminal custody-root/night/result.json`. These are example paths only;
never point the hook at a live runs/custody parent. `--state-dir` and the
stable loop lock must be outside the supplied immutable record. Key, lease,
watchdog and journal paths are explicit operational inputs, not discovered
from data configuration files.

`--transfer-mbps` and `--hash-mbps` are **decimal MB/s**, despite the compact
option names; they are conservative effective throughput estimates, not link
speeds or megabits/s. `--bwlimit-kib` is rsync's KiB/s cap (0 means no cap).
The estimator uses the smaller of that cap and estimated transfer throughput,
plus five full hashing/checksum passes and `--overhead-s` (default 30). It never
discounts a resumed copy. The minimum of the budget and lease deadline wins;
this illustrative 2000-second budget does not extend a shorter cool-down.

Policies:

- `after-two` (default): delete after two independently confirmed remote copies.
- `never`: copy/verify and retain the MBP record even after confirmation.
- `pressure`: delete after two remote copies **and only when** current MBP free
  bytes are below `--min-free-bytes`. Pressure never permits single-copy deletion.

Successful JSON includes `status` (`retained`, `deleted`, `already-deleted`),
elapsed seconds, and `hold_next_window`. A free-space shortfall after any
attempt sets `hold_next_window=true`; the magistrate must wait/retry the
Air backup/receipt in subsequent cool-down work before arming. Set the floor to
cover the next window's peak local footprint plus margin. An exit status 3
reports a refusal and elapsed seconds on stderr; keep the local record and
retry/back off only while a valid cool-down lease exists. A failure is not an
instruction to delete incoming data or weaken the copy requirement.

Receipts contain the exact manifest ID/name, whole inventory hash, byte/file
counts, verified device IDs, background-copy status, verification time and a
fresh request challenge. `sha256` hashes compact sorted-key JSON plus its final
newline. This is a **hashed receipt authenticated by pinned SSH**, not an
offline digital signature. Receipts and jobs live outside the immutable record.
`incoming/` contains resumable unverified bytes; never count it as a copy.
Inspect only the specific record's receipt/job/journal for recovery. If incoming
contains an extra/unmanifested file, verification refuses until the operator
dispositions that exact staging record; the tool never auto-deletes extras.

## Turnaround budget

Ideal transfer-only wall times, **decimal GB and MB/s**:

| Sustained rate | 18.6 GB | 26.4 GB |
|---|---:|---:|
| 50 MB/s | 372 s — 6m 12s | 528 s — 8m 48s |
| 100 MB/s | 186 s — 3m 06s | 264 s — 4m 24s |
| 300 MB/s | 62 s — 1m 02s | 88 s — 1m 28s |

These are lower bounds, not measured LAN performance. At the conservative
default 100 MB/s hash estimate, five passes add 930–1320 seconds, and setup adds
30 seconds. The total admission estimates are therefore:

| Transfer rate | Total estimate, 18.6–26.4 GB |
|---|---:|
| 50 MB/s | 22m 12s – 31m 18s |
| 100 MB/s | 19m 06s – 26m 54s |
| 300 MB/s | 17m 02s – 23m 58s |

Calibrate both estimates once on synthetic records with the deployed software,
Air background load, SSH encryption and disks; faster demonstrated effective
hashing can reduce these conservative allowances. Transfer/verification runs
**overlap cool-down**, after record publication and before the full clean dwell.
The Air's background second copy can continue while the MBP is quiet because it
does not contact the MBP. If the available cool-down cannot contain the estimate,
the hook refuses: extend cool-down or retain the local record and defer offload;
never consume dwell time or shorten the dwell. No actual cool-down duration or
LAN rate has been validated here, so this is not yet a demonstrated cadence.

## Verification before deployment

Repository check: `python3.13 -B -m unittest tests.test_offload_to_air` uses only
tiny synthetic records and an injected transport. Distinct disk IDs in success
tests are simulated explicitly; an unmocked same-filesystem test must refuse.
Tests cover corruption, partial copies/receipts, interruption/resumption,
duplicate calls, stale challenges, armed/open-terminal refusals, deadline and
lock transitions, symlink/escape refusals, backup failure, pressure, and
interrupted deletion recovery. No MLX/native model tests apply to this stdlib
operations tool.

The deadline also uses a process alarm for blocking Python I/O, and SIGTERM
unwinds the transport cleanup. A hung kernel/device call cannot be guaranteed
to stop at an exact wall time; the magistrate must supervise and await actual
hook/transport exit before beginning dwell, even after a timeout.

The lead's remaining one-time **unarmed synthetic** acceptance is: test real
forced-key/rrsync confinement and stdin/stdout protocol; pin/read back the host
key; interrupt/resume transport; disconnect the second disk and prove retention;
confirm independent physical disks and verified backup; rehearse shared-lock
arm/dwell exclusion in the actual loop; time 18.6–26.4 GB synthetic records and
set conservative rates/budgets. Do not use a study window or sealed bytes as the
deployment test. No network, SSH, hardware, full test suite, measurement or
block-5 analysis was run during implementation.
