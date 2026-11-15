# Span cloud offload (RL-173 A): the MBP's own off-host copy

Tool: `scripts/span_offload.py` (library `joulewise/span_offload.py`, tests `tests/test_span_offload.py`).
Ruling: RL-173 A (research lead, 2026-11-15) makes a verified, encrypted cloud offload made by the MBP the
off-host copy of RL-171 §6.1, permanently. The Air leaves the arm path. The lead's Air copy becomes a later
pull from the cloud, checked against the marker's hashes.

## What it does

`offload` (MBP, in the close interval, after the span's Check, before the next soak):

1. Refuses at once, doing nothing, if `<marker_dir>/<plan>.ok` exists (exit 3).
2. Checks the recipient public key against the pinned fingerprint (sha256 of its DER encoding) and size
   (RSA, at least 3072 bits).
3. Walks OUT without following links. A symlink, a socket, fifo or device, or a name with a newline,
   carriage return, backslash or non-UTF-8 bytes refuses the offload (exit 4).
4. Streams OUT through tar and gzip into `openssl enc`, reading each regular file **once, as bytes**. The
   plaintext manifest (`<plan>.SHA256SUMS`, `shasum -a 256` format on `./<path>`, byte order) hashes exactly
   the archived bytes. A file that changes while it is read refuses the offload. **No file under OUT is
   parsed** (A.4); `--require-file runner_receipt.json` checks existence only.
5. Wraps the per-span passphrase to the recipient key, writes the descriptor last, and keeps the four
   files in `<stage_root>/<plan>/` (about 4 % of OUT; the dev-02-s02 archive was 110 MB for 2.9 GB).
6. Uploads the four files synchronously (`rclone copyto --immutable`, which exits), and reads each back from
   the provider (`rclone lsjson --hash`): the size and the provider's hash must equal the local file's (A.3).
7. Writes the marker `<marker_dir>/<plan>.ok` only if it does not exist (`link(2)` of a complete temporary
   file: the `test ! -e` rule, atomic). It records the plaintext manifest's sha256, the ciphertext's sha256
   and size, and the provider's confirmation for each file (A.2).

Nothing under OUT is changed or deleted (A.5). The tool has no git step, and the remote is a private
cloud folder, never the repository (A.6). Any failure writes no marker and exits non-zero: 4 refused
before upload, 5 upload or read-back failed or the deadline passed. A failed or unverified offload holds
the next arm, and F0 does not run past it either (A.7). A re-run reuses a complete stage (same bytes, so
the immutable upload is idempotent) and sets a partial one aside as `<plan>.partial-<epoch>`.

`--deadline-epoch` is the next soak's start: the offload gives up, without a marker, if it cannot finish
by then (A.3: the upload ends before the next soak starts).

`pull` (Air, any time later): downloads the four files, checks the ciphertext and manifest against the
marker's hashes (or the two A.2 hashes given by hand from RUN_STATE), checks the descriptor, decrypts with
the private key, checks the archive hash, extracts only regular files and directories under the span's
top directory, re-hashes every file against the manifest (exact set), and moves the tree read-only
(files 0444, directories 0555) to `/Volumes/JW-EXT/cadence-desk/<kit>/<span name>/`, beside
`<span name>.mbp.SHA256SUMS` and `<span name>.air.SHA256SUMS`, the layout the Air copies already use.
Exit 6 on any integrity failure (nothing lands), 7 if the destination exists. A look reads a pulled copy
that matches the marker (A.5).

`keygen` (Air): makes the recipient key pair and prints the fingerprint to pin.

## Key scheme (proposed; replaces `offload.key`)

| | Interim (item 347) | This tool |
|---|---|---|
| Encryption | `openssl enc -aes-256-cbc -pbkdf2 -iter 200000`, one symmetric key file | Per span: a fresh 256-bit random passphrase, `openssl enc -aes-256-cbc -pbkdf2 -md sha256 -iter 10000`; the passphrase wrapped with RSA-OAEP to a 4096-bit recipient key |
| What the MBP holds | the secret key `~/night-custody/offload/offload.key` | the **public** key only, pinned by fingerprint |
| Who can decrypt | anyone with the MBP account | only the holder of the private key (Air custody root and Ed's vault) |
| A.1 (second key copy off the MBP) | must be copied off the MBP by hand, within 24 h | met at creation: the private key is made on the Air and never exists on the MBP |

Why public-key:
- **The MBP needs only to encrypt.** It never decrypts its own copies (the round trip moves to the Air's
  pull), so it holds nothing secret about the cloud copies. A compromised or lost MBP exposes none of them.
- **A.1 holds by construction.** The cloud copy is useless only if the private key is lost. The private key
  is generated on the Air, kept in its custody root, and a second copy goes to Ed's vault. It is never
  in the cloud folder, the repository or on the MBP.
- **No new binary on the measurement host.** `openssl` (LibreSSL 3.3.6 on macOS; OpenSSL 3 in CI) does both
  halves; the passphrase travels over a pipe (`-pass fd:N`, `pkeyutl` stdin) and is never on disk or argv.
  `age` would give the same separation with authenticated encryption, but it is not installed on either
  Mac. Integrity does not rest on the cipher: the ciphertext and the plaintext manifest are anchored by the
  marker's sha256 (and RUN_STATE), and the pull checks both, plus the archive hash, before anything lands.
- **Rotation** is a new key pair and a new pinned fingerprint; old copies stay readable with the old
  private key, which is kept.

**The interim archive** `cq-dev-02-s02-a1` (item 350) was encrypted with `offload.key`, which is on the
MBP only. RL-173 A.1 gives it 24 h from the ruling (until 2026-11-16 11:58 PST): either copy `offload.key`
to the Air's custody root (and Ed's vault), or re-offload that span with this tool.

## Backends and the provider

`backend.kind` is pluggable:

- `rclone` (production): `rclone copyto --immutable` then `rclone lsjson --files-only --hash --hash-type
  <t>`. `hash_type` is `sha256`, `sha1` or `md5` (compared with the local file's digest), `dropbox`
  (compared with `rclone hashsum dropbox` of the local file) or `size` (size only). A listing that lags the
  upload, or a hash the provider has not computed yet, is retried `readback_tries` times
  (`readback_wait_s` apart); a differing size or hash is final.
- `local` (tests; a sync folder): a copy with a local read-back. It cannot see a provider, so it is allowed
  only with `--allow-local-backend` and writes `<plan>.ok.unconfirmed`, which no copy gate accepts. A sync
  folder daemon (iCloud's `bird`, `cloudd`, `fileproviderd`) is the interim only (A.3).

Provider evaluation (no account or credential was created for this PR):

| Option | Synchronous, exits | Provider read-back | Unattended credential | Verdict |
|---|---|---|---|---|
| rclone + Google Drive (`drive`, `scope = drive.file`) | yes | MD5 (and SHA-1/SHA-256 where Drive reports them) | OAuth refresh token; `drive.file` sees only files rclone created | **Recommended** (15 GB free: about 130 spans) |
| rclone + Dropbox | yes | Dropbox content hash | OAuth refresh token; rclone's app has full Dropbox access unless an app-folder app is registered | Good if the plan has the space (2 GB free is about 18 spans) |
| rclone + iCloud Drive (`iclouddrive`, rclone 1.69+) | yes | size only | Apple ID password and a 2FA trust token that expires and is renewed interactively; fails under Advanced Data Protection | Not for unattended use |
| iCloud sync folder (item 347) | no: a daemon uploads when it chooses | `brctl status` | none | Interim only (RL-173 A.3) |

## What the lead provisions (the one credential)

An rclone remote named `jwoffload` of type `drive` with `scope = drive.file`, authorized once against the
Google account that will hold the copies (Ed's consent in a browser; the lead can do it in the Air's
signed-in browser):

```sh
# Air (has a browser). One token per host: run it twice, once for the MBP and once for the Air.
rclone authorize "drive" "$(printf '%s' '{"scope":"drive.file"}' | base64)"   # token JSON after browser consent
# (or the exact `rclone authorize ...` line that `rclone config` prints on the headless MBP)
# MBP and Air: ~/.config/rclone/rclone.conf, mode 600, not encrypted (the job is unattended):
#   [jwoffload]
#   type = drive
#   scope = drive.file
#   token = <that host's token JSON>
```

Nothing else is a credential: the recipient public key is not secret, and the private key never leaves
the Air and Ed's vault.

## Install (the lead, between spans; no measurement running)

Air:
1. `python3.13 -B scripts/span_offload.py keygen --out-dir <Air custody root>/offload` and record the
   printed `recipient_sha256`. Put a second copy of `span-offload.key.pem` in Ed's vault (A.1).
2. `brew install rclone` (or the official release binary in `~/bin`), then the `jwoffload` remote above.
3. Air config (`schema` `joulewise.span_offload_pull_config.v1`): `identity` (the private key path),
   `recipient_sha256`, `work_root` (a directory on JW-EXT), `backend`, `openssl`.

MBP:
4. `brew install rclone` (a recorded host event: a new binary, used only in the close interval), then the
   `jwoffload` remote with the MBP's own token.
5. Copy `span-offload.pub.pem` to `/Users/edr/night-custody/offload/span-offload.pub.pem`.
6. A checkout of `main` at the merge commit of this tool, for example
   `/Users/edr/code/jw-wt/span-offload-<sha>`, used only for this command.
7. `/Users/edr/night-custody/offload/span_offload.json`:

```json
{"schema": "joulewise.span_offload_config.v1",
 "recipient_public_key": "/Users/edr/night-custody/offload/span-offload.pub.pem",
 "recipient_sha256": "<the keygen fingerprint>",
 "stage_root": "/Users/edr/night-custody/offload",
 "marker_dir": "/Users/Shared/JouleWise/desk-copy",
 "openssl": "/usr/bin/openssl",
 "backend": {"kind": "rclone", "rclone": "/opt/homebrew/bin/rclone",
             "rclone_config": "/Users/edr/.config/rclone/rclone.conf",
             "remote": "jwoffload:JouleWise-offload", "hash_type": "md5", "timeout_s": 5400}}
```

   The config refuses unknown keys, so a private key (`identity`) cannot be put in it.
8. Probe with synthetic bytes only, never a span: make a scratch directory of random files, run
   `offload` with a copy of the config whose `marker_dir` is a scratch directory and a plan id such as
   `probe-offload-20261116`, then `pull` it on the Air into a scratch `--dest-root` and compare the two
   manifests. Delete the probe's remote folder afterwards. If `rclone lsjson --hash --hash-type sha256`
   on the probe shows a SHA-256 for every file, `hash_type` may be `sha256`.

## The close step (magistrate or controller)

After the span's Check passes, between spans, with no fence up and nothing else running:

```sh
python3.13 -B /Users/edr/code/jw-wt/span-offload-<sha>/scripts/span_offload.py offload \
  --config /Users/edr/night-custody/offload/span_offload.json --plan "$PLAN" --span-dir "$OUT" \
  --require-file runner_receipt.json --deadline-epoch "$NEXT_SOAK_EPOCH"
```

Exit 0 prints one `OFFLOAD_OK` line (plan, files, both hashes, ciphertext size, marker path), which goes
into the span's RUN_STATE item. Exit 3 means the marker already exists: record which path wrote it. Any
other exit holds the next arm and F0; mail Ed and the lead with the one stderr line.

Later, on the Air:

```sh
python3.13 -B scripts/span_offload.py pull --config <air config> --plan "$PLAN" --kit "$KIT" \
  --dest-root /Volumes/JW-EXT/cadence-desk --marker <copy of the .ok marker>
# or, from RUN_STATE alone: --expect-manifest-sha256 <...> --expect-ciphertext-sha256 <...>
```

The MBP keeps OUT, uncompressed, until a second verified location holds it (A.5): the Air's pulled copy
is that location.
