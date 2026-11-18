# Span cloud offload (RL-173 A; RL-174 D.1/D.2)

The MBP makes its own encrypted off-host copy between spans. The Air is outside the arm path.
`scripts/span_offload.py` uses `joulewise/span_offload.py`, which owns the iCloud backend and the marker
schema `joulewise.span_offload_marker.v1`. The [cluster contract](cluster_contract.md) assigns close,
retirement and reclaim to PR #807. Synthetic coverage is in `tests/test_span_offload.py` and
`tests/contract/test_cluster_804.py`.

Authority: RL-173 A, amended by RL-174 D.1/D.2 in
`origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`.
The research lead accepted this supervised backend as the permanent tool. **Operational status remains
INTERIM / macOS 26 qualification PROVISIONAL until the lead records one native MBP round trip with
the production key.** Software tests do not establish that gate.

## Operations and gates

`offload` packs a closed OUT and retains the original and the materialised stage. Run it after the
span's Check, with all source writers stopped, nothing armed, and before the next soak. A failed
bundle push permits copying. For a stranded span, use `--require-file` with a basename attested by
the Check. Failure holds the next arm and F0. The tool handles
bytes and parses only its own transport records, tar headers and brctl status; no source payload is
parsed. A packed unreleased span remains as restricted as its source. Never expand one outside a
registered look. Keep the newest desk projections outside OUT for the GAP census.

1. Refuse unsafe plan/OUT names (OUT must be `<plan>` or `<plan>-<YYYYMMDDTHHMMSSZ>`), an empty tree,
   and absence of the required file (default `runner_receipt.json`, existence only). Refuse source links,
   special files and unsafe names, and control/output paths overlapping OUT or inside Git repositories.
   Configs, keys, stages and records must be single-name regular files; iCloud directory components
   are opened with O_NOFOLLOW. A plan lock excludes concurrent offloads of the same plan.
2. Census every source name and its device, inode, mode, link count, size, mtime and ctime **before any
   payload is read**. Record each directory before enumerating its children. Compare the entire census
   after packing and immediately before publishing the marker. Added/removed members, inode replacement,
   writes between different files' reads, and writes with restored mtime refuse `SPAN_CHANGED`. Ignore
   only read-induced atime. This requires a closed source on a local filesystem; it cannot freeze an
   active writer or defeat forged kernel metadata. A mutation after the final check is outside that
   contract; the caller must stop writers before copying.
3. Stream tar+gzip into OpenSSL; the SHA256SUMS manifest hashes exactly those archived bytes, in byte
   order, as `sha256  ./relative-path`. Re-read the decrypted transport stream while the fresh passphrase
   is still in memory, requiring both the archive hash and **every file's manifest digest and exact file
   set**. No plaintext archive is written on the MBP. Only this pack receives the descriptor field
   `pack_verification: stream per-file manifest match`.
4. Snapshot and pin the RSA public key by the sha256 of its DER SubjectPublicKeyInfo (>=3072 bits;
   production defaults to 4096). Each span gets a fresh 256-bit random passphrase, AES-256-CBC,
   PBKDF2-SHA256/10000 iterations and RSA-OAEP wrapping. Passphrases travel over pipes, never argv or
   disk. OpenSSL runs with OPENSSL_CONF=/dev/null and no inherited OpenSSL/SSL config environment.
   Integrity rests on marker hashes. The MBP holds only the public key; the Air and Ed's vault hold the
   private key. The first native Air pull tests the RSA unwrap.
5. Complete a private `.<plan>.building-*` directory and rename it to `<stage_root>/<plan>` with read-only
   ciphertext, wrapped key, manifest and descriptor, plus `.source.json`. The descriptor is written last.
   A failed new build removes only its own directory. A complete stage is reused only for the same
   source/recipient after deterministically recreating the archive and comparing manifest, hash and size.
   Foreign/incomplete stages refuse STAGE_CONFLICT; the tool never moves them.
6. Copy all four artifacts using exclusive temporary files and atomic rename to
   `~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-offload/<plan>/`. Existing objects must
   match. For **each** artifact require positive `brctl status com.apple.CloudDocs` idle/caught-up with
   no pending/error state; request eviction; observe SF_DATALESS; request download; observe
   materialisation; compare downloaded sha256 AND size against the stage snapshot. Command success
   alone never proves eviction. The stage remains materialised throughout this verification cycle.
7. Only four complete, consistent observed readbacks permit the absent-only atomic `<plan>.ok`.
   It records all artifact hashes, ciphertext size, source name, key fingerprint and per-artifact
   `icloud evict+redownload sha256 match`, upload, observed eviction and verification times. Recheck
   CloudDocs idle and source stability before publication. Successful completion precedes the next soak.

Upload/status failure, publication I/O failure, or the overall deadline returns 5. Readback hash
mismatches return 6. If the marker is visible after a sync failure, the next writer finishes
publication under the plan lock and rechecks the copy. Failed,
unobserved or phase-timeout eviction/download returns 8 with only `.ok.unconfirmed`, including a retry
of a placeholder left by failed download. That record satisfies no gate. A confirmed retry may add
`.ok` while preserving the historical unconfirmed record. A valid typed `.ok` retry rechecks all four
cloud hashes (and the original archive if OUT remains), then returns 0 without rewriting the marker.
A legacy one-line marker is preserved as `<plan>.ok.legacy-line` under the plan lock. The writer
publishes a typed marker after full verification. A marker publication race returns 3.

Other exits: 1 internal, 2 usage, 4 input/stability refusal, 7 existing or
incomplete pull destination. Every nonzero exit holds the next arm. Await completion and recheck time.
Without `--deadline-epoch`, one 5400 s budget covers the offload; an explicit deadline must be finite and
within 24 h. Supervised children are killed on deadline or TERM/HUP/INT. Filesystem calls are
cooperative: a final delayed publication can complete after its last check, so the caller must still
await and recheck time. After abnormal termination check remaining children and pending sync.

### Copy evidence and SSD receipt

`evidence` prints one JSON object and exits 0 for `CLEAR`. It validates the published marker's
readback proofs, backend, recipient fingerprint and span name, then checks the stage source path and
descriptor digest. It checks receipt presence through file metadata. The controller uses
`copy_evidence(..., require_closed=False)` for a stranded span. Marker publication in progress, a busy
plan lock or a marker more than five minutes ahead of the local clock returns `BUSY`. A legacy line
returns `INVALID` with `LEGACY_MARKER`.

On the Air, `ssd-copy` downloads the four encrypted artifacts to `<mounted SSD>/span-archives/<plan>`,
syncs and re-reads them against the marker, then publishes `ssd.ok.json`. It requires an external mounted
filesystem. Courier the receipt to the MBP through the lead's approved record-delivery path and keep it
with the SSD bytes. The receipt records an observed readback.

### Every arm: pending-transfer read

From the MBP user's **GUI domain**, immediately before every arm and soak:

```sh
"$PY" -B "$REPO/scripts/span_offload.py" pending --config "$MBP_CONFIG"
```

Require exit 0 and a fresh ICLOUD_CLEAR line in the arm record. This read-only CloudDocs status check
never uploads, downloads or evicts. It requires the whole container idle/caught-up, conservatively
including all JouleWise folders. Pending/error/offline/empty/unknown status holds the arm. A cached
observation cannot qualify another arm. Nothing of ours writes to iCloud Drive on the MBP while armed.
Air uploads/evictions are allowed. Permanently list **bird, cloudd and fileproviderd** on the maintenance
line, including after qualification.

## Install (lead, between spans)

**MBP iCloud access requires a process launched in the signed-in user's GUI domain**, such as a
LaunchAgent or the magistrate. SSH processes cannot reach iCloud Drive. Do not run qualification,
offload or pending through SSH or count SSH output as provider evidence. Preparing files is
separate from launching the actual GUI job. The PR builder does not contact the MBP or install this.

1. On the Air, create the private key directory (keygen also creates a missing final directory as 0700):

   ```sh
   mkdir -m 700 /absolute/Air-custody/offload
   python3.13 -B scripts/span_offload.py keygen --out-dir /absolute/Air-custody/offload
   ```

   Record recipient_sha256. Private key mode is 0600. Put a second private-key copy in Ed's vault;
   deliver only span-offload.pub.pem to the MBP. Keep old private keys through rotation. The item-350
   legacy offload.key needs its separate off-MBP backup; generating this pair does not back up that key.
2. In each Mac's GUI session, verify the private iCloud Drive sign-in and create the default
   JouleWise-offload folder if needed. Control/stage/marker/iCloud paths must have no links or `.git`
   ancestor. No rclone, new account, OAuth token or new credential is needed.
3. Install the reviewed checkout at `/Users/edr/code/jw-wt/span-offload-<sha>` on the MBP. Create private
   `/Users/edr/night-custody/offload/span-offload` and `/Users/Shared/JouleWise/desk-copy` directories.
   Write a single-name regular config, substituting the actual fingerprint and lead address:

   ```json
   {"schema":"joulewise.span_offload_config.v1",
    "recipient_public_key":"/Users/edr/night-custody/offload/span-offload.pub.pem",
    "recipient_sha256":"<keygen fingerprint>",
    "stage_root":"/Users/edr/night-custody/offload/span-offload",
    "marker_dir":"/Users/Shared/JouleWise/desk-copy",
    "openssl":"/usr/bin/openssl",
    "backend":{"kind":"icloud","brctl":"/usr/bin/brctl","timeout_s":5400},
    "key_second_copy_attested_sha256":"<attested key fingerprint>",
    "lead_email":"<lead email>","default_budget_s":5400}
   ```

   Remove `forbid_paths` from older offload configs. The close tool's fence mode owns that check.
   The controller's preflight checks the attested fingerprint. Unknown top-level keys refuse.
   An absolute backend root may override the default for a synthetic probe.
   Defaults: polling 2 s, observed eviction 30 s, download 600 s; every phase shares the overall deadline.
4. On the Air, create a config with schema joulewise.span_offload_pull_config.v1, absolute identity,
   recipient_sha256, absolute work_root on JW-EXT (same filesystem as pull destination),
   openssl `/usr/bin/openssl`, and the same iCloud backend/root. Work/desk roots stay outside Git.
5. Configure the GUI-domain magistrate to await the offload, hold every nonzero result, read pending transfers
   before every arm, and retain the daemon maintenance line. Qualification below precedes production use.

## Native production-key round trip (external gate; still owed)

Between spans, with no measurement, pending soak or source writer, use **synthetic bytes** and the
production key pair. Use scratch source/stage/marker/destination paths; never real custody.

1. In the MBP user's **local GUI session**, choose absolute PY (installed Python 3.13), REPO,
   PROBE_CONFIG and PROBE_OUT. Name the plan `span-offload-native-<UTC timestamp>`; OUT's basename must
   equal that plan. Make a random binary file, nested and empty directories, and a synthetic
   runner_receipt.json. Copy the production config to PROBE_CONFIG, keeping its production public
   key/fingerprint and iCloud root but substituting scratch stage/marker roots. Save the source manifest.
2. Create a one-shot LaunchAgent at
   `~/Library/LaunchAgents/com.joulewise.span-offload-probe.plist`, using absolute paths and these fields:

   ```text
   Label = com.joulewise.span-offload-probe
   ProgramArguments = [PY, -B, REPO/scripts/span_offload.py, offload,
                       --config, PROBE_CONFIG, --plan, PROBE_PLAN, --span-dir, PROBE_OUT]
   RunAtLoad = true
   StandardOutPath = <absolute scratch path>/probe.stdout
   StandardErrorPath = <absolute scratch path>/probe.stderr
   ```

   Use a real XML/binary plist and an array for ProgramArguments; placeholders are not literal argv.
   From the local GUI session run:

   ```sh
   launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.joulewise.span-offload-probe.plist"
   ```

   Alternatively the magistrate already running in the GUI domain runs the same command directly.
   **Do not substitute an SSH shell or SSH-launched Python.**
3. Await completion. In that GUI session record
   `launchctl print "gui/$(id -u)/com.joulewise.span-offload-probe"` (last exit status 0), stdout/stderr,
   sw_vers, checkout SHA, Python/OpenSSL versions, public-key fingerprint and complete scratch `.ok`.
   Require four `icloud evict+redownload sha256 match` rows with upload, observed eviction and readback
   observations and equal hashes/sizes. The tool observes Apple's stat.st_flags SF_DATALESS (0x40000000).
   Preserve the status/flag transition evidence in the native record. Unknown status, unsupported
   flags or exit 8 leaves qualification PROVISIONAL; keep source and stage and report to the lead.
4. Courier the scratch marker to the Air by the approved record path. In the Air GUI session, pull into
   a scratch desk using the command below. Require exit 0, exact MBP/Air manifest equality and every
   synthetic file's hash. This tests the production RSA unwrap. Run ssd-copy against that marker and
   JW-EXT; preserve ssd.ok.json and require the retained ciphertext digest to equal the marker.
5. In the MBP GUI domain, require `evidence` to return `CLEAR`, with raw originals and the materialised
   stage ciphertext present. Require a fresh pending read / ICLOUD_CLEAR before any next soak.
6. The lead records plan, paths, hashes, key fingerprint, native evidence and verdict in a dated report.
   Only then change INTERIM/PROVISIONAL to permanent/qualified. Boot out the probe LaunchAgent in the
   GUI session. The lead may remove only the synthetic probe/cloud artifacts; retain the native record.
   A software-review verdict never substitutes for this round trip.

## MBP and Air commands

The magistrate uses the exact OUT from the span record, in its GUI domain after the Check and before
the next soak:

```sh
"$PY" -B "$REPO/scripts/span_offload.py" offload --config "$MBP_CONFIG" \
  --plan "$PLAN" --span-dir "$OUT" --deadline-epoch "$NEXT_SOAK_EPOCH"
"$PY" -B "$REPO/scripts/span_offload.py" evidence --config "$MBP_CONFIG" --plan "$PLAN" --span-dir "$OUT"
"$PY" -B "$REPO/scripts/span_offload.py" pending --config "$MBP_CONFIG"
```

Record OFFLOAD_OK, CLEAR evidence and fresh ICLOUD_CLEAR, then recheck time. Any nonzero result holds the next arm and F0;
report stderr to the lead. On the Air, retaining encrypted SSD copies does not require the private key:

```sh
python3.13 -B scripts/span_offload.py ssd-copy --config "$AIR_CONFIG" --plan "$PLAN" \
  --marker "$MARKER" --ssd-root /Volumes/JW-EXT
# Courier /Volumes/JW-EXT/span-archives/$PLAN/ssd.ok.json through the approved record path.
```

A registered desk/look can stage raw bytes:

```sh
python3.13 -B scripts/span_offload.py pull --config "$AIR_CONFIG" --plan "$PLAN" --kit "$KIT" \
  --dest-root /Volumes/JW-EXT/cadence-desk --marker "$MARKER"
```

Pull verifies anchored hashes, safe tar paths/types and the exact manifest, then lands a read-only tree,
MBP/Air manifests and `<span>.pull.ok`. An existing tree without a valid record is an interrupted landing
(exit 7); the lead moves it and sidecars aside before retrying. Expand unreleased content only in a
registered look. Keep a pending look's designated raw copy until that look ends (RL-174 D.3).

Legacy rclone configurations remain for low-level offload/pull; hash_type size proves length only.
Both rclone and local write only .ok.unconfirmed (exit 8): listing evidence cannot replace RL-174's
observed iCloud round trip. Local additionally requires --allow-local-backend. The copy gate and pending-transfer check require iCloud. Existing legacy typed markers
without that observed iCloud evidence refuse current retry validation.
