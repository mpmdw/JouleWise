# Span cloud offload (RL-173 A): the MBP's own off-host copy

Tool: `scripts/span_offload.py` (library `joulewise/span_offload.py`, tests `tests/test_span_offload.py`).
Ruling: RL-173 A (research lead, 2026-11-15) makes a verified, encrypted cloud offload made by the MBP the
off-host copy of RL-171 §6.1, permanently. The Air leaves the arm path. The lead's Air copy becomes a later
pull from the cloud, checked against the marker's hashes.

## What it does

`offload` (MBP, in the close interval, after the span's Check, before the next soak):

1. Refuses at once, doing nothing, if `<marker_dir>/<plan>.ok` exists (exit 3), if OUT's name is not the
   plan id or `<plan>-<YYYYMMDDTHHMMSSZ>` (`PLAN_SPAN_MISMATCH`; the pull applies the same rule to the
   descriptor's span name), if `--deadline-epoch` is not finite or is more than 24 h ahead (`BAD_DEADLINE`), or if any `forbid_paths` entry exists (the config names
   the magistrate's desk fence: `FORBIDDEN_PATH_PRESENT`). Without `--deadline-epoch` the whole offload
   gets `default_budget_s` (90 min, item 347's limit); with no time left it does nothing.
2. Reads no control file from inside OUT: the config path is checked against OUT before it is read, and
   the config, the recipient key, any optional rclone config, the stage files and the completion records are opened
   only as single-name regular files (no symlink followed, no hard link accepted, no fifo waited on). Walks OUT without following links. A symlink, a socket, fifo or device, or a name with a newline,
   carriage return, backslash or non-UTF-8 bytes refuses the offload (exit 4). The stage root, the marker
   directory, the recipient key and the iCloud/local backend root must not overlap OUT and must not be
   inside a git repository (`PATH_OVERLAPS_SPAN`, `PATH_IN_REPOSITORY`). The repository check walks
   every ancestor. Check `/Users/edr`, `/Users/edr/night-custody`, `/Users/Shared/JouleWise` and the iCloud
   destination at install. Optional rclone configs get the same checks (rclone may rewrite them on token
   refresh). OUT must hold at least one regular file and
   `runner_receipt.json` (the default `--require-file`; existence only).
3. Takes an exclusive lock for the plan (`<stage_root>/.<plan>.lock`, held until the marker; a second
   offload of the same plan is refused `BUSY`). It never deletes a directory it did not make in this run: a
   killed run's `.<plan>.building-*` and `.<plan>.key-*` directories stay for the lead to remove.
4. Reads the recipient public key once into a private snapshot, and checks that snapshot against the pinned
   fingerprint (sha256 of its DER encoding) and size (RSA, at least 3072 bits); the wrap uses the same bytes.
5. Streams OUT through tar and gzip into `openssl enc`, reading each regular file **once, as bytes**. The
   plaintext manifest (`<plan>.SHA256SUMS`, `shasum -a 256` format on `./<path>`, byte order) hashes exactly
   the archived bytes. A file that changes while it is read refuses the offload. **No file under OUT is
   parsed** (A.4). The deadline is checked before each file, and one watchdog bounds the whole stream: at
   the deadline it kills openssl and the offload fails `DEADLINE`.
6. Decrypts the staged ciphertext once with the passphrase still in memory and requires the archive's
   sha256 (`CIPHERTEXT_UNVERIFIED` otherwise; plaintext is hashed, never written). The MBP cannot test the
   RSA wrap; the first pull is that test (install step 6). Then wraps the passphrase to the recipient key
   (the wrapped key must be exactly one RSA block) and writes the descriptor last. All of this happens in a private `.<plan>.building-*` directory, removed on
   any failure and renamed to `<stage_root>/<plan>/` only when complete (about 4 % of OUT; the dev-02-s02
   archive was 110 MB for 2.9 GB), with a local `.source.json` naming OUT's resolved path.
7. Copies the four files to iCloud Drive using exclusive random temporary names and atomic rename,
   under `~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-offload/<plan>/`. Every directory
   component is opened without following links; files must be single-name regular files. Existing
   objects must match the staged bytes (immutable retry). For **each** file it waits for
   `brctl status com.apple.CloudDocs` to report the container `client:idle` and `caught-up`, with no
   pending or error state. Empty or unknown status text never counts. Then it calls `brctl evict <file>`,
   waits until `stat.st_flags & SF_DATALESS` is set, calls `brctl download <file>`, waits until that flag
   clears, and hashes the downloaded bytes. The size and sha256 must equal the stage's pre-upload
   snapshot. All four artifacts, including the descriptor, get this readback. The staged files are
   read-only (0400). The tool parses only brctl's status text, never CloudDocs databases or journals.
   An upload/status timeout or a hash mismatch is UNVERIFIED (exit 5), without any marker. If eviction
   or download fails, times out within its phase budget, or cannot be observed, only `.ok.unconfirmed`
   may be written (exit 8). Expiry of the overall deadline still writes no marker.
8. Checks the deadline once more, then writes the marker `<marker_dir>/<plan>.ok` only if it does not exist
   (`link(2)` of a complete, synced temporary file: the `test ! -e` rule, atomic). It records the plaintext
   manifest's sha256, the ciphertext's sha256 and size, and the provider's confirmation for each file (A.2):
   `icloud evict+redownload sha256 match`, `uploaded_epoch_s`, `evicted_epoch_s`, `verified_epoch_s`,
   and the downloaded size and sha256. Only four confirmed readbacks permit `.ok`.

Nothing under OUT is changed or deleted (A.5). The tool has no git step, refuses output paths inside a
repository, and the destination is a private iCloud folder, never the repository (A.6). Exit 4 means
refused before upload; exit 5 means UNVERIFIED (upload/status/readback/deadline failure); neither writes
a marker. Exit 8 writes only `<plan>.ok.unconfirmed`, which satisfies no gate. A failed or unverified
offload holds the next arm, and F0 does not run past it either (A.7). SIGTERM, SIGHUP and SIGINT kill
tracked openssl/brctl/rclone children before exit 5. An uncatchable kill can leave a child alive and
CloudDocs can keep syncing; after an abnormal exit the controller holds the next soak and the lead
checks child activity and outstanding sync. Await the command, then recheck the time before starting
the next soak. While iCloud sync is in use, **RL-171 §5's maintenance line must list `bird`, `cloudd`
and `fileproviderd`** (RL-173 A.3), including after this tool exits.

**Re-runs.** A complete stage is reused only for the same OUT (resolved path) and recipient, and only after
the archive is derived again from OUT (deterministic: fixed gzip header and level, tar metadata from the
files) and its manifest, digest and size equal the stored ones, so an edited or corrupted stored descriptor
is refused; the upload of the same bytes is then idempotent. That costs one more archive pass (about a
minute for 2.9 GB), and a span whose files or directory times changed since the first attempt is refused.
A repeated iCloud attempt that is still unconfirmed exits 8 (`ICLOUD_UNCONFIRMED`) and preserves the
existing `.ok.unconfirmed`; it never uses exit 3 for that record. A later confirmed attempt may create
`.ok` while leaving the historical unconfirmed record intact.
Anything else at the stage path, complete or not, is refused `STAGE_CONFLICT`: the tool never moves a
directory it did not build. The tool never deletes a stage or a remote folder. After the Air's pull of a
span succeeds, the lead may remove `<stage_root>/<plan>/`; a remote `<plan>/` folder is removed only by the
lead, and only to retry a plan whose stage was lost (the immutable upload otherwise refuses new bytes).

`--deadline-epoch` is the next soak's start: the offload gives up, without a marker, if it cannot finish
by then (A.3: the upload ends before the next soak starts). The bound is enforced by watchdogs on the
openssl and provider children and by checks between files and phases; a single blocked filesystem call can
return after the deadline. Expiry detected before publication prevents a marker; a delayed final
marker filesystem call can publish an already verified marker after the last deadline check. The caller awaits the command and
holds the next arm on any failure.

**What `hash_type: size` proves.** RL-173 A.3 accepts the provider's hash or size. A size read-back proves
the upload finished with the right length, not byte equality; the pull still checks the ciphertext against
the marker. Prefer a hash type for production.

`pull` (Air, any time later): downloads the four files, checks the ciphertext and manifest against the
marker's hashes (or the two A.2 hashes given by hand from RUN_STATE), checks the descriptor, decrypts with
the private key, checks the archive hash, extracts only regular files and directories under the span's
top directory (no duplicate names), re-hashes every regular file against the manifest (the exact set of
regular files; directories, including empty ones, are not in the manifest), and moves the tree read-only
(files 0444, directories 0555) to `/Volumes/JW-EXT/cadence-desk/<kit>/<span name>/`, beside
`<span name>.mbp.SHA256SUMS` and `<span name>.air.SHA256SUMS`, the layout the Air copies already use. A
symlinked kit directory, a symlinked backend plan directory and a kit directory inside a git repository are
refused. `<span name>.pull.ok` is written last, synced and linked atomically, and marks a complete landing; a
tree without a valid one is an interrupted landing, which the pull refuses (`INCOMPLETE_LANDING`) until the lead
moves the tree and any sidecars aside (`chmod u+w <tree>` first if the tree is already 0555: a read-only
directory cannot be renamed on APFS). Exit 6 on any integrity failure (nothing lands), 7 if the
destination exists. A look reads a pulled copy that matches the marker (A.5).

`keygen` (Air): makes the recipient key pair and prints the fingerprint to pin.

## Key scheme (proposed; replaces `offload.key`)

| | Interim (item 347) | This tool |
|---|---|---|
| Encryption | `openssl enc -aes-256-cbc -pbkdf2 -iter 200000`, one symmetric key file | Per span: a fresh 256-bit random passphrase, `openssl enc -aes-256-cbc -pbkdf2 -md sha256 -iter 10000`; the passphrase wrapped with RSA-OAEP to a 4096-bit recipient key |
| What the MBP holds | the secret key `~/night-custody/offload/offload.key` | the **public** key only, pinned by fingerprint |
| Who can decrypt | anyone with the MBP account | only the holder of the private key (Air custody root and Ed's vault) |
| A.1 (second key copy off the MBP) | must be copied off the MBP by hand, within 24 h | met at creation: the private key is made on the Air and never exists on the MBP |

Why public-key:
- **The MBP needs only to encrypt.** It holds no persistent archive-decryption key (it decrypts each new
  ciphertext once, with the in-memory passphrase, only to self-check it), so a stolen MBP disk does not open
  past cloud copies.
  (The MBP still holds the plaintext originals, each span's passphrase in memory while it encrypts, and the
  upload credential; a live compromise of the MBP is out of scope.)
- **A.1 holds by construction.** The cloud copy is useless only if the private key is lost. The private key
  is generated on the Air, kept in its custody root, and a second copy goes to Ed's vault. It is never
  in the cloud folder, the repository or on the MBP.
- **No new binary on the measurement host.** `openssl` (LibreSSL 3.3.6 on macOS; OpenSSL 3 in CI) does both
  halves; the passphrase travels over a pipe (`-pass fd:N`, `pkeyutl` stdin) and is never on disk or argv.
  Every openssl child runs with `OPENSSL_CONF=/dev/null` and no inherited `OPENSSL_*`, `SSL_*` or
  `RANDFILE` variable, so it reads no configuration file (one under OUT included).
  `age` would give the same separation with authenticated encryption, but it is not installed on either
  Mac. Integrity does not rest on the cipher: the ciphertext and the plaintext manifest are anchored by the
  marker's sha256 (and RUN_STATE), and the pull checks both, plus the archive hash, before anything lands.
- **Rotation** is a new key pair and a new pinned fingerprint; old copies stay readable with the old
  private key, which is kept.

**The interim archive** `cq-dev-02-s02-a1` (item 350) was encrypted with `offload.key`, which is on the
MBP only. RL-173 A.1 gives it 24 h from the ruling (until 2026-11-16 11:58 PST): copy `offload.key` to the
Air's custody root and Ed's vault. (This tool will not re-offload that span: its marker exists, exit 3.)

## iCloud is the default production path; no new credential

Owner decision, 2026-11-15 17:46 PST: "use icloud, no? why would you not use icloud".
Omitting `backend` or `backend.kind` selects `icloud`. The existing macOS iCloud Drive sign-in supplies
access; there is no new account, OAuth token, rclone install or credential. Both Macs must already have
access to the private iCloud Drive folder. Do not share it publicly. The provider sees encrypted file
contents, wrapped keys, the descriptor and the plaintext manifest (relative names and per-file hashes).

The optional, already tested `rclone` backend remains available for existing configurations. It requires
an explicit absolute `rclone_config`, a named `remote`, and `hash_type` (`sha256`, `sha1`, `md5`, `dropbox`
or `size`); it uses synchronous immutable copy and provider listing readback. No such provisioning is
part of this install. `local` is synthetic testing only, requires `--allow-local-backend`, and always
writes `.ok.unconfirmed`.

### What the iCloud evidence establishes

CloudDocs sync is asynchronous. This command synchronously waits for it and tests provider readback;
it cannot shut down or bound the lifetime of Apple's daemons. The idle/caught-up status observation is
from item 350's hand-run on the MBP. Eviction followed by an observed dataless placeholder and matching
re-downloaded bytes supplies stronger evidence than hashing the still-resident sync-folder copy.
A successful `brctl evict` exit alone does **not** prove eviction.

The implementation uses Apple's `SF_DATALESS` flag (`0x40000000` in `sys/stat.h`), via Python's
`os.stat(..., follow_symlinks=False).st_flags`, as described in
[Apple TN3150](https://developer.apple.com/documentation/technotes/tn3150-getting-ready-for-data-less-files).
The local Apple `brctl(1)` manual describes `evict` and `download`. No xattr, Spotlight (`mdls`) or
`brctl monitor` interpretation is used. Unknown status formats, missing flag support, missing/removed
commands, or a pinned file that cannot become dataless never earn `.ok`.

**PROVISIONAL on macOS 26:** the builder ran synthetic fake-brctl tests on macOS 15.8.3; it did not
contact the MBP or exercise live CloudDocs. Apple does not specify a stable `brctl status` wire format.
The lead must qualify the commands/status/flag transitions on macOS 26 with synthetic bytes at install.
The phase budgets default to 30 s for observed eviction and 600 s for download; `timeout_s` defaults
to 5400 s, `poll_interval_s` to 2 s. Every phase is also bounded by the overall offload deadline.
A filesystem operation can still block; the deadline is cooperative outside supervised subprocesses.

**Research-lead question:** is iCloud with evict+redownload readback the permanent tool under A.3?
The owner selected iCloud; this software review does not settle A.3's classification of its daemons.
Until the research lead rules, retain the daemon maintenance line and the PROVISIONAL label.

## Install (the lead, between spans; no measurement running)

1. On the Air, run `python3.13 -B scripts/span_offload.py keygen --out-dir <Air custody root>/offload`.
   Record `recipient_sha256`; put a second copy of `span-offload.key.pem` in Ed's vault (A.1).
   The MBP receives only `span-offload.pub.pem` at `/Users/edr/night-custody/offload/`.
2. On each Mac, verify iCloud Drive is already signed in and the destination is private. Create
   `~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-offload` if needed. No directory component
   may be a link. Check that no `.git` exists in any ancestor of this destination, the custody control
   paths, the stage root, the marker directory or the Air work/destination roots.
3. On the MBP, create `/Users/edr/night-custody/offload/span-offload` (separate from the interim stages).
   Install a checkout of the eventual merge under `/Users/edr/code/jw-wt/span-offload-<sha>`.
   Write `/Users/edr/night-custody/offload/span_offload.json` as a single-name regular file:

```json
{"schema": "joulewise.span_offload_config.v1",
 "recipient_public_key": "/Users/edr/night-custody/offload/span-offload.pub.pem",
 "recipient_sha256": "<the keygen fingerprint>",
 "stage_root": "/Users/edr/night-custody/offload/span-offload",
 "marker_dir": "/Users/Shared/JouleWise/desk-copy",
 "openssl": "/usr/bin/openssl",
 "backend": {"kind": "icloud", "brctl": "/usr/bin/brctl", "timeout_s": 5400},
 "forbid_paths": ["/Users/edr/night-custody/magistrate/desk_fence.json"],
 "default_budget_s": 5400}
```

   The root defaults to the item-350 destination above. `root` can be specified as an absolute path
   for a synthetic probe; `poll_interval_s`, `evict_timeout_s` and `download_timeout_s` can be tuned.
   Unknown top-level config keys are refused; no private key belongs on the MBP.
4. On the Air, write a config with schema `joulewise.span_offload_pull_config.v1`, `identity` (the
   private key path), `recipient_sha256`, `work_root` (on JW-EXT, same filesystem as `--dest-root`),
   `openssl: /usr/bin/openssl` and `backend: {"kind": "icloud", "brctl": "/usr/bin/brctl"}`.
5. Add `bird`, `cloudd`, `fileproviderd` to the RL-171 §5 maintenance line. Configure the controller
   to await offload, hold the next arm and F0 on any nonzero/unconfirmed result, and check its deadline
   again before the next soak. No test here authorizes a live measurement.
6. **Qualify with synthetic bytes and production keys before counting any tool marker.** Make a scratch
   span named for a probe plan (with a synthetic `runner_receipt.json`); use a scratch `marker_dir`.
   Run `offload` on the MBP between spans. Require exit 0, four readback confirmations with observed
   eviction/download times, and the documented status/flag transitions on macOS 26. Pull on the Air
   into a scratch destination and compare manifests. The lead may remove the probe's cloud folder
   afterwards. If the host cannot evict or redownload, exit 8 is expected: it does not satisfy a gate.

## The close step (magistrate or controller)

After the span's Check passes, between spans, with no fence up and nothing else running:

```sh
setopt NULL_GLOB 2>/dev/null
OUT=$(ls -d /Users/edr/campaign-out/<kit>/${PLAN}-*Z); test "$(echo "$OUT" | wc -l | tr -d ' ')" = 1 || { echo "STOP: OUT"; exit 1; }
python3.13 -B /Users/edr/code/jw-wt/span-offload-<sha>/scripts/span_offload.py offload \
  --config /Users/edr/night-custody/offload/span_offload.json --plan "$PLAN" --span-dir "$OUT" \
  --require-file runner_receipt.json --deadline-epoch "$NEXT_SOAK_EPOCH"
```

`--require-file` replaces the default list; name `runner_receipt.json` whenever it is given.

Exit 0 prints one `OFFLOAD_OK` line (plan, files, both hashes, ciphertext size, marker path), which goes
into the span's RUN_STATE item. Before treating exit 3 as an already satisfied copy gate, check that
`<marker_dir>/<plan>.ok` actually exists and record which path wrote it. An `.ok.unconfirmed` record
never satisfies that check. Any
other exit holds the next arm and F0; mail Ed and the lead with the one stderr line.

Later, on the Air:

```sh
python3.13 -B scripts/span_offload.py pull --config <air config> --plan "$PLAN" --kit "$KIT" \
  --dest-root /Volumes/JW-EXT/cadence-desk --marker <copy of the .ok marker>
# or, from RUN_STATE alone: --expect-manifest-sha256 <...> --expect-ciphertext-sha256 <...>
```

The MBP keeps OUT, uncompressed, until a second verified location holds it (A.5): the Air's pulled copy
is that location.
