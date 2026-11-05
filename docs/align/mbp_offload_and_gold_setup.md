# Measurement MacBook Pro offload and gold setup runbook

Operator: Ed and the measurement-Mac magistrate, during an explicitly paused,
non-measurement window of approximately two days. **This document has not been
executed. Do not execute it on the analysis laptop.** The measurement machine is
Mac15,9, M3 Max, 128 GB (`docs/process_traces/2026-11-01-interactive-26be5929/RECORD.md:3`).
Its SSD capacity is **UNKNOWN**; step 1 measures it before any capacity promise.

The objective is to reclaim **at least 450,000,000,000 physical bytes**, retain
all required custody, then stage the complete official 360 GB bf16 checkpoint
for full 48-layer parity and conversion. Authority: Goal 11 in
`1643e9aac43ebfc10443a31c30a0cdc506bcbfc6:docs/align/qwen4_exp_port/GOAL.md:25`
(branch `origin/port/qwen4-exp-mlx`; status log at lines 42–44). This is permission
to offload eligible bytes, not permission to override a sealed retention rule.

Run numbered steps individually in Terminal. **STOP means leave the source
intact and resolve the named condition before continuing.** Save receipts in the
operation journal; never put measurement contents in this document or Git.
All block-5 handling is metadata, opaque byte copying/compression and SHA-256
only: never parse or print measurement values. Do not run
`scripts/run_b5_analysis.py`, a reducer, a harvest, or a release/recompute here.
No agent may inspect a real `restricted/` directory. Such directories are
excluded from the commands below and require the authorized custody operator;
they are never silently omitted from an archive declared complete.

## 1. Identify the machine and measure the SSD, read-only

These are the first commands, before creating an operation directory:

```zsh
/usr/sbin/sysctl -n hw.model hw.memsize
/usr/sbin/system_profiler SPHardwareDataType SPNVMeDataType
/bin/df -k / /System/Volumes/Data
/usr/sbin/diskutil info /System/Volumes/Data
/usr/sbin/diskutil apfs list
/usr/bin/tmutil listlocalsnapshots /
```

**STOP 1:** Ed confirms Mac15,9 / M3 Max / 128 GB, physical SSD/container size,
Data volume and actual available bytes. A different machine stops this runbook.
Record APFS sharing, snapshots and purgeable storage separately. Use `df`
available space for admission; do not count purgeable space, promised iCloud
evictions, summed `du` sizes, or the SSD's marketed capacity as available space.

## 2. Pause ALIGN and prove nothing can arm

Do this before hashing, compression, uploads, model downloads or imports. A
live plan takes precedence: if collection is running, stop here and let the
magistrate close it through its normal terminal procedure. Do not kill a
collection to make room. The recorded pilot-9 plan was armed on November 5;
its old record is not evidence of today's terminal state
(`docs/process_traces/2026-11-05-magistrate-c110a6c9/RECORD.md:48–54`).

The following paths are recorded: canonical repository
`scripts/install_magistrate_watchdog.sh:37`, measurement checkout
`docs/process_traces/2026-11-02-magistrate-0eafdaa2/RECORD.md:96`, ALIGN root and
plan layout `docs/process_traces/2026-11-05-magistrate-c110a6c9/RECORD.md:50`.
The journal and all `flashnext-gold-*` paths below are **new proposed paths**,
not claims that those directories already exist.

```zsh
set -euo pipefail
setopt extendedglob
export JW_CANON=/Users/edr/code/JouleWise
export JW_MEAS=/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2
export JW_OP="/Users/edr/night-archive/mbp-offload-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -m 700 "$JW_OP"
/bin/df -k /System/Volumes/Data > "$JW_OP/df-before.txt"
/usr/sbin/diskutil apfs list > "$JW_OP/apfs-before.txt"
git -C "$JW_MEAS" status --short --branch > "$JW_OP/measurement-status.txt"
git -C "$JW_MEAS" rev-parse HEAD > "$JW_OP/measurement-head.txt"
/bin/launchctl list > "$JW_OP/launchd-before.txt"
/bin/launchctl print-disabled "gui/$(id -u)" > "$JW_OP/launchd-disabled-before.txt"
/bin/launchctl print "gui/$(id -u)" > "$JW_OP/launchd-domain-before.txt"
/bin/ps -axo pid,ppid,lstart,command > "$JW_OP/processes-before.txt"
find /Users/edr/Library/LaunchAgents -maxdepth 1 -type f -name '*.plist' -print
```

Ed records `ALIGN PAUSED: mbp-offload; no automatic re-arm; next review <UTC>`
in the journal and informs the laptop lead. Preserve the measurement checkout,
`.venv`, pinned ledger, launchd plists and their executable targets. Copy each
JouleWise/measurement plist into `$JW_OP/plists/` before unloading; record which
jobs were loaded. Include user and system jobs, scheduled probes, BYTES/B6 loop,
magistrate and any external scheduler that can restart a measurement. Do not
unload unrelated Apple services. Inspect system jobs with:

```zsh
sudo /bin/launchctl print system > "$JW_OP/launchd-system-before.txt"
mkdir "$JW_OP/plists"
# For EACH reviewed measurement/agent plist; fill its exact discovered path.
: "${JW_PLIST:?Set exact reviewed plist path}"
cp -p "$JW_PLIST" "$JW_OP/plists/"
plutil -p "$JW_PLIST"
```

When the current plan is terminal, set its exact path from the magistrate's
current control record, not an old timestamp. The established uninstall removes
the night and deadman jobs (`7e06863b/RECORD.md:7` in the directory cited in
step 6). Keep their saved plists even though the installer removes installed
ones. Then prevent the magistrate from launching new agents:

```zsh
: "${JW_PLAN:?Set terminal ALIGN custody/night_plan.json}"
"$JW_MEAS/scripts/install_night_agent.sh" --plan "$JW_PLAN" --uninstall
# STOP is the watchdog's supported local stop gate (watchdog.py:2677).
test ! -e /Users/edr/night-custody/magistrate/STOP
printf '%s\n' 'ALIGN paused for MBP offload and gold validation' \
  > /Users/edr/night-custody/magistrate/STOP
/bin/launchctl bootout "gui/$(id -u)/com.joulewise.magistrate"
/bin/launchctl disable "gui/$(id -u)/com.joulewise.magistrate"
```

If STOP already exists, preserve it and its owner: do not overwrite or later
remove it. `night-custody/magistrate` and the label are established by
`scripts/install_magistrate_watchdog.sh:45–46`; STOP semantics are in
`scripts/magistrate_watchdog.py:2677–2682`. Bootout preserves the installed
plist; unlike `--uninstall`, it does not remove the file. An already-absent job
must be documented as absent, not hidden with a blanket `|| true`.

For every other reviewed automatic launcher (including `com.joulewise.b6loop`,
recorded in `2026-11-01-interactive-26be5929/RECORD.md:6`), boot out its **exact**
label and domain, and temporarily disable only launchers enabled before pause
so a login/reboot cannot re-arm them. Record each change against the original
disabled-state snapshot; inspect system-domain disabled state too if it has
a relevant job. Ed closes resident agent sessions after handoff. Preserve
`local.jwbench.keepawake`, its plist and AC configuration (retention authority
`RUN_STATE.md:36`); it is not a measurement launcher. Do not reuse old PIDs for
Spotlight SIGCONT: verify names and start times first (`c110a6c9/RECORD.md:7`).

```zsh
# Fill for each reviewed launcher; use system domain only when actually found.
: "${JW_JOB_TARGET:?Set reviewed domain/label}"
/bin/launchctl bootout "$JW_JOB_TARGET"
/bin/launchctl disable "$JW_JOB_TARGET"
/bin/launchctl list > "$JW_OP/launchd-paused.txt"
/bin/launchctl print "gui/$(id -u)" > "$JW_OP/launchd-domain-paused.txt"
/bin/ps -axo pid,ppid,lstart,command > "$JW_OP/processes-paused.txt"
```

**STOP 2:** Ed/magistrate attest: terminal plan, no collection process or
`collection.active`, no scheduled t0, night/deadman absent, loops unable to
launch, resident agents drained, every automatic reloader accounted for. A
missing process in `ps` alone does not prove an armed launchd job is absent.
No measurement resumes during any offload or setup step. Agent work is allowed
only in this paused non-measurement window; **all agents must exit before any
future measurement** (`AGENTS.md:60–64`).

## 3. Inventory every root, then mark KEEP before selecting deletions

Start with metadata only. List top-level home roots, including hidden roots;
expand each large root one level at a time. Do not follow symlinks. BSD `du -I`
prunes real `restricted` directories; mark their excluded size UNKNOWN and
send them to the custody operator. Never `cat`, sample or preview a data file.

```zsh
find /Users/edr -mindepth 1 -maxdepth 1 ! -name restricted -print \
  > "$JW_OP/home-roots.txt"
while IFS= read -r root; do
  /bin/df -k "$root"
  /usr/bin/du -sk -I restricted "$root"
done < "$JW_OP/home-roots.txt" > "$JW_OP/root-metadata.txt"
```

Use a per-root ledger with columns: exact path, owning study/registration,
source citation, allocated KiB, logical bytes (later manifest), status
KEEP/CLOSED/UNKNOWN, irreplaceable yes/no, cloud destination, independent-copy
location/device, verified manifest SHA, deletion receipt. UNKNOWN is KEEP.
Include caches, Downloads, home temp roots, `/private/tmp` and `$TMPDIR`
(metadata of Ed-owned entries only, same restricted exclusion). Do not perform
a bulk temp cleanup: the old broad command in `RUN_STATE.md:38` is not adopted.

Records establish this initial inventory; discovery must add missing roots:

| Root (on the measurement Mac unless stated) | Record and treatment |
|---|---|
| `/Users/edr/night-b5`, `night-g2a`, `night-custody/v5-*`, `night-archive/harvest-v5-b5-*`, `night-plan-staging` | `RUN_STATE.md:45,360`; `BLOCK5-TRANSFER.md:26–44,84–104`. Entire B5 custody starts KEEP. Include all attempts, history, failed captures, meters and ledgers. |
| `/Users/edr/night-custody/measurement`, `/Users/edr/night-custody/desk`, canonical `/Users/edr/code/JouleWise` and active worktrees | `RUN_STATE.md:27`; `2026-11-02-magistrate-0eafdaa2/RECORD.md:96`; offload registration `01-data-offload-lane-registration.md:43–50` cited in step 6. KEEP, never move live roots under sync. |
| `/Users/edr/night-b6/sessions`, `night-b6/loop`, `night-b6/loop-bytes` | `docs/registrations/block6_replication_DRAFT.md:1195`; `docs/registrations/bytes_freeze_by_commit_addendum.md:198–217`. Separate closed B6 and BYTES sessions; retain control and registration dependencies. |
| `/Users/edr/night-bytes`, `night-bytes-stream-test`, `night-archive/bytes-stream-test` | `RUN_STATE.md:1239`; `docs/process_traces/2026-10-31-magistrate-5cbfbcfc/RECORD.md:6–8`. Include H/H2, known-bytes receipts, raw streams and original/archived copies. |
| `/Users/edr/night-align` (all v0–v9 preparations and pilots discovered there) | `docs/process_traces/2026-11-04-magistrate-7e06863b/RECORD.md:15–17`; `c110a6c9/RECORD.md:50`. Pilot number differs from root suffix: pilot 9 used `pilot-v8-*`; do not infer absent v9 or treat an empty prepare as disposable. Inventory `.OFFLOADED.json` pointers as custody too. |
| `/Users/edr/night-archive`, `night-plan-staging`, canonical/measurement `runs/instrument_validation` and calibration ledgers | `RUN_STATE.md:45`; `TASK_QUEUE.md:1233` (R7 second-copy obligation); transfer `measurement-corpus18-data.manifest.json:8–24` and `ledger-captures.manifest.json:8–15` under the directory in step 4. Include quarantine, calibration, staging, raw plists and logs. |
| `/Users/edr/jw_models`, `/Users/edr/.cache/huggingface/hub` | `docs/process_traces/2026-10-28-magistrate-39206674/RECORD.md:22`; pinned ALIGN config in step 4. HF snapshots can symlink to shared blobs: account for their actual targets before any cache deletion. |
| `/Users/edr/Library/Mobile Documents/com~apple~CloudDocs` | `configs/campaigns/p2_015_floors/backup_icloud.sh:4–6`. Inventory backup/archive/transfer metadata without triggering mass hydration; already-cloud-only data is not reclaimable SSD space. |

Abbreviations in the table name files under `docs/process_traces/` and the
full dated activation directories used elsewhere in this runbook. Add mount
points, symlink targets and external volumes to the ledger; two paths on one
APFS container do not represent independent copies.

## 4. KEEP list — never delete under this runbook

Copying KEEP material for additional safety is allowed after pause. Deletion,
moving its source, iCloud relocation of live roots, and unreviewed cache
cleanup are not. KEEP ancestors cannot be selected as deletion roots.

1. **Block-5 custody required for release/recompute on BOTH machines.** The
   analysis laptop runs the blind dry run and independent recompute:
   `docs/process_traces/2026-10-27-l9-restart/BLOCK5-TRANSFER.md:13–17,51–60`.
   The release follows the laptop comparison (`RUN_STATE.md:1023`). Its local
   `/Users/edr/night-{archive,b5,custody,g2a,plan-staging}` inputs and
   `/Users/edr/jw-b5-staging/tars` are KEEP through release; the transfer was
   verified at 88,653 files and 190 iCloud captures (`RUN_STATE.md:360`).
   **Do not access those laptop paths from this operation.** Ask the laptop
   lead for a fresh hash-only receipt against the committed manifests in
   `docs/process_traces/2026-10-27-l9-restart/b5-transfer/`. The old receipt
   is evidence of a transfer, not proof that today's entire Mac root has a
   second copy. The laptop's unpacked inputs are independent of the MBP;
   its own iCloud mount is the same cloud copy, not another backup.
2. **On-device retention overrides space goals.** No calibration capture
   after ledger sequence 376 is moved/offloaded before release, including
   removed attempts under `night-b5` and `night-g2a` (`RUN_STATE.md:45`).
   `BLOCK5-TRANSFER.md:44` explicitly leaves B5 originals in place. This runbook
   retains B5 originals rather than interpreting a general offload approval
   as a repeal. Also retain every root/ledger/config a sealed registration,
   night plan, acceptance or recompute pins. Derive dependencies from tracked
   registrations, committed path manifests and released control records;
   do not parse raw blinded ledgers. If their coverage is incomplete: STOP.
   Backup/offload copies inherit the blinding restrictions
   (`configs/campaigns/v5_claim_25g83/registration_block5.md:4874–4904`).
3. **ALIGN anchor Qwen3-30B-A3B-4bit.** Repository
   `mlx-community/Qwen3-30B-A3B-4bit`, revision
   `d388dead1515f5e085ef7a0431dd8fadf0886c57`, source
   `/Users/edr/.cache/huggingface/hub/models--mlx-community--Qwen3-30B-A3B-4bit/snapshots/d388dead1515f5e085ef7a0431dd8fadf0886c57`.
   Citation:
   `8d1ab6e2c1c8f17fac0b20485f519d197e463c38:configs/campaigns/align_pilot_v3/stages/episodes-a/align-pilot-v3-episodes-a-e01.json:16–22`
   (`origin/lane/2026-11-05-align-pilot9-kit`). Keep its referenced blob store.
4. **Qwen3.8-27B-8bit.** Repository `mlx-community/Qwen3.8-27B-8bit`, revision
   `815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9`, path
   `/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit` (28 GB):
   `docs/process_traces/2026-10-28-magistrate-39206674/RECORD.md:22`.
   The record establishes its BYTES-extension use; current ALIGN use must be
   confirmed from the current kit, not asserted from this older record.
   **Models 3–4 may be reclassified CLOSED only if** the lead confirms no
   sealed on-device obligation, resolves every symlink/blob reference, and
   proves the exact pinned revision remains downloadable with a complete
   per-file digest inventory. Record the revision and restore command before
   deletion. Otherwise KEEP. Never delete a model named by an open roster
   (`RUN_STATE.md:1203`). Re-downloadability is not assumed from a repo name.
5. **Measurement infrastructure.** Canonical and measurement checkouts,
   desk checkouts, ignored custody inputs/local-only commits, venvs, runtime
   locks, magistrate executable targets, launchd plist backups, loop state,
   plan staging, keepawake and credentials remain in place. `.venv` was
   reproduced from 55 frozen dependencies, not a fresh unconstrained install
   (`docs/process_traces/2026-11-02-magistrate-0eafdaa2/RECORD.md:96`).
   `DATA-OFFLOAD-ICLOUD-01` never-sync list: `TASK_QUEUE.md:843` and
   `01-data-offload-lane-registration.md:43–50` cited in step 6.
6. **Legacy calibration/acceptance custody.** Retain mint inputs, quarantine,
   six frozen acceptance bundles and experiment custody listed in
   `docs/run_reports/2026-07-28-icloud-archive-prune.md:35–41`, unless the lead
   supplies an explicit superseding dependency ruling. R7's 17 raw captures
   need a second copy outside Git/iCloud (`TASK_QUEUE.md:1233`), including the
   three previously iCloud-only captures. They cannot be counted safe merely
   because an old archive exists. Do not change a ledger locator to repair
   an offload. D-188 allows specific code benchmarking, not deletion or
   unblinding (`docs/decision_log.md:12239`, clauses 1–6).

**STOP 4:** Ed and the lead review the per-root classification. If protected
bytes prevent 450 GB reclamation, retain them and request an external SSD or
a specific retention ruling. Never trade away originals to meet a capacity
target. No B5-original deletion is supplied here.

Save a complete plain-text list of exact absolute KEEP roots in
`$JW_OP/KEEP.txt` (one path per line, no comments or glob patterns), expanding
the table's patterns from metadata only. Include required individual files,
the journal, active infrastructure, original B5 roots and every discovered
sealed dependency. This is an additional deletion guard, not a replacement
for the dependency review.

## 5. Check iCloud quota and measure upload throughput before bulk copying

Ed opens System Settings → Apple Account → iCloud → storage management and
records account, quota, used and remaining bytes, including other devices'
pending uploads. `df` on the iCloud folder measures local SSD capacity, **not
iCloud quota**. If quota is unknown/insufficient, STOP; Ed chooses another
approved cloud destination with equivalent full-byte verification. Never
publish blinded data or create a new integration as a convenience.

```zsh
export JW_CLOUD='/Users/edr/Library/Mobile Documents/com~apple~CloudDocs'
/usr/bin/brctl status com.apple.CloudDocs > "$JW_OP/icloud-before.txt"
# New operation namespace under the established JouleWise-archive namespace.
export JW_REMOTE="$JW_CLOUD/JouleWise-archive/$(basename "$JW_OP")"
mkdir -p "$JW_REMOTE"
# Synthetic 256 MiB probe; contains no study data. Keep until operation closes.
dd if=/dev/urandom of="$JW_OP/upload-probe.bin" bs=1048576 count=256
shasum -a 256 "$JW_OP/upload-probe.bin" > "$JW_OP/upload-probe.sha256"
date -u +%FT%TZ > "$JW_OP/upload-start.utc"
cp -p "$JW_OP/upload-probe.bin" "$JW_REMOTE/upload-probe.bin"
/usr/bin/fileproviderctl evaluate "$JW_REMOTE/upload-probe.bin"
/usr/bin/brctl status com.apple.CloudDocs
```

Poll manually until that exact file reports `isUploaded=1` and no pending
upload/error. Record end UTC and elapsed seconds including upload delay.
If `fileproviderctl` is unavailable or ambiguous, Ed must establish the same
server-upload state in Finder; a local copy, checksum or progress-bar
disappearance alone does not suffice. Then use **explicit** eviction and
re-download of this probe to confirm the remote round trip:

```zsh
date -u +%FT%TZ > "$JW_OP/upload-end.utc"
/usr/bin/brctl evict "$JW_REMOTE/upload-probe.bin"
/usr/bin/brctl download "$JW_REMOTE/upload-probe.bin"
cmp "$JW_OP/upload-probe.bin" "$JW_REMOTE/upload-probe.bin"
```

Compute sustained throughput as `268435456 / elapsed_seconds` bytes/s. Repeat
with the first real archive, and plan using the slower rate. Reserve quota
for the **uncompressed manifest total** until actual compression is measured;
model weights may compress poorly. Time estimate = upload bytes / measured
bytes/s, plus complete source hashing, archive verification, remote hydration
and independent-copy verification. At 10/50/100 Mbit/s, 450 GB takes about
100/20/10 hours for upload alone; 360 GB download takes 80/16/8 hours at those
rates. Thus two days is a planning allowance, not a guarantee.

**STOP 5:** journal actual free quota, existing queue, observed throughput,
estimated cloud bytes/time, independent-device capacity/time and SSD archive
staging headroom. Extend the ALIGN pause if the verified plan exceeds it.
Never use “Optimize Mac Storage” as a verified backup. Explicit eviction is
only for a server-uploaded, verified archive and cannot replace a second copy.

## 6. Offload one CLOSED leaf root at a time; verify all bytes

Established procedure: `DATA-OFFLOAD-ICLOUD-01` in `TASK_QUEUE.md:843`;
`docs/process_traces/2026-09-15-activation-08ca8197/01-data-offload-lane-registration.md:14–24,43–50`.
The pilot implementation used manifest → `tar | zstd` → re-hash every archive
member → delete → pointer, and fixed AppleDouble and directory-symlink loss:
`docs/process_traces/2026-11-04-magistrate-7e06863b/RECORD.md:14–17`.
Pilots 4–5 were verified offloaded (`RUN_STATE.md:1057`); pilots 6–7 later
verified 35,387/35,410 files (`docs/process_traces/2026-11-05-magistrate-c110a6c9/RECORD.md:25`).
Do not invoke the untracked `~/night-archive/seats-7e06863b/offload.py` blindly:
it deletes automatically and this runbook adds an independent-copy gate.
`scripts/backup_runs.sh:59` is only an rsync copy, not proof of safety to delete.

Use the following **new operation-local helper**, saved verbatim as
`$JW_OP/manifest.py`. It never interprets data. It records regular-file bytes,
empty directories and symlink targets without following links; rejects special
files, real restricted directories and duplicate/unsafe archive members.
Any error is a STOP. Hashes alone do not preserve filesystem-specific metadata:
before packaging, Ed must establish that resource forks, ACLs, extended
attributes, sparse layout and hardlink topology are not required for this
root. Otherwise retain it and use a metadata-preserving archival method with
an independently verified restore. The pilot tar flags intentionally omit
AppleDouble/xattrs; do not silently apply them to arbitrary personal files.

```zsh
cat > "$JW_OP/manifest.py" <<'PY'
import hashlib, json, os, stat, sys, tarfile
from pathlib import Path, PurePosixPath

def digest(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
        h.update(chunk)
    return h.hexdigest()

def safe(name):
    p = PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or 'restricted' in p.parts:
        raise ValueError('unsafe or restricted path')
    return p.as_posix()

def tree(root):
    root = Path(os.path.abspath(root))
    safe(str(root).lstrip('/'))
    if root.is_symlink() or not root.is_dir() or root.resolve() != root:
        raise ValueError('root must be a real directory, without symlink ancestors')
    rows = []
    device = root.stat().st_dev
    def walk(directory):
        for p in sorted(directory.iterdir(), key=lambda x: x.name):
            name = safe(p.relative_to(root).as_posix())
            s = p.lstat()
            if s.st_dev != device:
                raise ValueError('nested filesystem: inventory separately')
            mode = stat.S_IMODE(s.st_mode)
            if stat.S_ISLNK(s.st_mode):
                rows.append([name, 'link', mode, os.readlink(p)])
            elif stat.S_ISDIR(s.st_mode):
                rows.append([name, 'dir', mode])
                walk(p)
            elif stat.S_ISREG(s.st_mode):
                with p.open('rb') as f:
                    sha = digest(f)
                after = p.lstat()
                if (s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns) != (
                    after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                    raise ValueError('source changed while hashing')
                rows.append([name, 'file', mode, s.st_size, sha])
            else:
                raise ValueError('special file: retain and resolve')
    walk(root)
    return sorted(rows)

def archive():
    rows, seen = [], set()
    with tarfile.open(fileobj=sys.stdin.buffer, mode='r|') as tf:
        for m in tf:
            name = safe(m.name)
            if name == '.' and m.isdir():
                continue
            if name in seen:
                raise ValueError('duplicate member')
            seen.add(name)
            mode = stat.S_IMODE(m.mode)
            if m.issym():
                rows.append([name, 'link', mode, m.linkname])
            elif m.isdir():
                rows.append([name, 'dir', mode])
            elif m.isfile():
                with tf.extractfile(m) as f:
                    sha = digest(f)
                rows.append([name, 'file', mode, m.size, sha])
            else:
                raise ValueError('unsupported archive member; retain source')
    return sorted(rows)

if sys.argv[1] == 'tree':
    result = tree(sys.argv[2])
elif sys.argv[1] == 'archive':
    result = archive()
else:
    raise ValueError('tree ROOT or archive < uncompressed.tar')
json.dump(result, sys.stdout, ensure_ascii=True, separators=(',', ':'))
sys.stdout.write('\n')
PY
shasum -a 256 "$JW_OP/manifest.py" > "$JW_OP/manifest-helper.sha256"
```

For each reviewed CLOSED leaf, fill variables from its inventory row. No
source may equal/contain/be contained by a KEEP entry; no ancestor root
deletion. Confirm no external symlink target is needed for restoration; archive
such targets separately or retain the source. An archived symlink is not a
copy of its target (especially HF blobs and `.venv`).

```zsh
: "${JW_SRC:?Set one exact approved CLOSED leaf root}"
: "${JW_ID:?Set unique ledger ID using letters digits dash underscore only}"
[[ "$JW_ID" == [A-Za-z0-9_-]## ]]
export JW_SRC JW_ID
export JW_ITEM="$JW_OP/$JW_ID"
mkdir "$JW_ITEM"
python3.13 -B "$JW_OP/manifest.py" tree "$JW_SRC" > "$JW_ITEM/source.json"
shasum -a 256 "$JW_ITEM/source.json" > "$JW_ITEM/source.sha256"
printf '%s\n' "$JW_SRC" > "$JW_ITEM/source-path.txt"
test ! -e "$JW_REMOTE/$JW_ID.tar.zst"
COPYFILE_DISABLE=1 /usr/bin/tar --no-mac-metadata --no-xattrs -cf - \
  -C "$JW_SRC" . | zstd -T1 -3 -o "$JW_REMOTE/$JW_ID.tar.zst.partial"
mv "$JW_REMOTE/$JW_ID.tar.zst.partial" "$JW_REMOTE/$JW_ID.tar.zst"
zstd -dc "$JW_REMOTE/$JW_ID.tar.zst" | \
  python3.13 -B "$JW_OP/manifest.py" archive > "$JW_ITEM/cloud-local.json"
cmp "$JW_ITEM/source.json" "$JW_ITEM/cloud-local.json"
python3.13 -B "$JW_OP/manifest.py" tree "$JW_SRC" > "$JW_ITEM/source-after.json"
cmp "$JW_ITEM/source.json" "$JW_ITEM/source-after.json"
shasum -a 256 "$JW_REMOTE/$JW_ID.tar.zst" > "$JW_ITEM/archive.sha256"
cp -p "$JW_ITEM/source.json" "$JW_REMOTE/$JW_ID.manifest.json"
```

Step 2 enables `extendedglob` for the zsh ID pattern above. Use one compression
worker to limit non-measurement load. A partial archive is not verified; on
interruption keep the source and use a new ID, or explicitly retire only the
failed `.partial` after checking its path. Do not overwrite an earlier receipt.
If tar produces an unsupported hardlink member, the helper refuses; use a
reviewed archival adjustment and verify again, never discard the link silently.

Before the first offload, also use this helper's `tree` command to save
baseline manifests for readable KEEP data roots and the pinned model files,
with output under `$JW_OP/keep-manifests/`, never inside a source. Bind each
manifest to its exact source path in the inventory. Existing authenticated
manifests remain the trust anchors. If a KEEP root contains real `restricted/`
directories, the helper refuses: the authorized custody operator must provide
the baseline receipt without exposing those paths to an agent. Preserve
checkouts/venvs/plists through their saved identity/version records as well.
Without these baselines, the restoration checks in step 13 remain blocked.

**STOP 6a:** all source and cloud-local manifest entries match exactly,
including name set, empty directories, links, file lengths and SHA-256s. Both
pre/post source manifests match. No source writers remain. Save full manifest
digest, total regular bytes, archive bytes and dependency review in the ledger.
For B5 and calibration, match against existing committed transfer manifests
as well; a new manifest alone cannot authenticate a pre-existing omission.

Wait for **both archive and manifest** to report uploaded; save per-file state
and aggregate queue state (the transfer precedent is
`docs/process_traces/2026-10-28-magistrate-39206674/RECORD.md:88`).

```zsh
/usr/bin/fileproviderctl evaluate "$JW_REMOTE/$JW_ID.tar.zst"
/usr/bin/fileproviderctl evaluate "$JW_REMOTE/$JW_ID.manifest.json"
/usr/bin/brctl status com.apple.CloudDocs
# Execute ONLY after confirmed server upload; sources remain intact.
/usr/bin/brctl evict "$JW_REMOTE/$JW_ID.tar.zst"
/usr/bin/brctl evict "$JW_REMOTE/$JW_ID.manifest.json"
/usr/bin/brctl download "$JW_REMOTE/$JW_ID.tar.zst"
/usr/bin/brctl download "$JW_REMOTE/$JW_ID.manifest.json"
cmp "$JW_ITEM/source.json" "$JW_REMOTE/$JW_ID.manifest.json"
shasum -a 256 -c "$JW_ITEM/archive.sha256"
zstd -dc "$JW_REMOTE/$JW_ID.tar.zst" | \
  python3.13 -B "$JW_OP/manifest.py" archive > "$JW_ITEM/cloud-roundtrip.json"
cmp "$JW_ITEM/source.json" "$JW_ITEM/cloud-roundtrip.json"
```

**STOP 6b:** a complete post-upload, post-eviction cloud re-read matches every
entry. Sampling is insufficient under this brief. The July pruning report
used sampled large traces and explicitly left a single durable copy
(`docs/run_reports/2026-07-28-icloud-archive-prune.md:24–28,59–60`); that older
bar does not satisfy this operation's full verification and two-copy rule.

## 7. Require a second independent copy before any irreplaceable deletion

For every irreplaceable root, leave the original until **cloud plus an
independent durable copy** survive its removal. Prefer an owner-held external
disk or another device's non-synced storage. APFS clones, a second folder on
the MBP, another iCloud folder, or the same iCloud account on another device
are not independent failure domains. The active analysis laptop has a 7-worker
job: coordinate a quiet verification slot with its lead; do not start work on
it from this session. B5 laptop custody is KEEP, not spare scratch space.

On the independent device only, Ed fills these variables with approved new
paths; no independent target path is established by the repository. Use a
non-synced filesystem with enough capacity. Copy the entire uploaded archive,
source manifest, archive digest and helper there. Verify archive SHA-256,
and the helper's digest against the MBP journal. Stream every member again,
and make a complete restore to an empty directory
(review member names and symlink targets before extraction; never restore on
top of custody or at the original absolute path):

```zsh
# Independent device, with the same pipefail and helper as step 6.
: "${JW_SECOND_ARCHIVE:?Set archive path on independent storage}"
: "${JW_SECOND_MANIFEST:?Set copied source manifest}"
: "${JW_SECOND_HELPER:?Set copied manifest.py}"
: "${JW_SECOND_RESTORE:?Set new empty non-synced restore directory}"
shasum -a 256 "$JW_SECOND_ARCHIVE"
# Manually compare with archive.sha256 whose digest was anchored on the MBP.
shasum -a 256 "$JW_SECOND_HELPER"
# Compare with manifest-helper.sha256 from the MBP journal too.
zstd -dc "$JW_SECOND_ARCHIVE" | python3.13 -B "$JW_SECOND_HELPER" archive \
  > "$JW_SECOND_ARCHIVE.members.json"
cmp "$JW_SECOND_MANIFEST" "$JW_SECOND_ARCHIVE.members.json"
mkdir -m 700 "$JW_SECOND_RESTORE"
zstd -dc "$JW_SECOND_ARCHIVE" | /usr/bin/tar -xpf - -C "$JW_SECOND_RESTORE"
python3.13 -B "$JW_SECOND_HELPER" tree "$JW_SECOND_RESTORE" \
  > "$JW_SECOND_ARCHIVE.restored.json"
cmp "$JW_SECOND_MANIFEST" "$JW_SECOND_ARCHIVE.restored.json"
```

**STOP 7:** Ed obtains a signed/attributed receipt naming device/volume,
non-synced location, source-manifest SHA-256, archive SHA-256, complete restored
file/byte counts, result and UTC. Copy receipt back to the MBP journal; retain
it with an independently stored manifest. Validate the exact root coverage:
the B5 transfer excluded results-clone and did not include superseded raw
attempts (`BLOCK5-TRANSFER.md:34–35`; `measurement-corpus18-data.manifest.json:8`).
An old B5 receipt cannot cover an unrelated B6/BYTES/ALIGN root. A receipt with
one missing member, pending upload or mismatched digest is not approval.

## 8. Ed-only deletion, one reviewed root per receipt

No batch deletion loop. No `find ... -delete`, cache purge, worktree prune,
snapshot deletion or recursive parent removal. Ed reviews the exact source,
KEEP exclusions, cloud round-trip manifest, independent restore receipt and
current launchd pause **immediately before** each deletion. First deletion
requires Ed's YES against that manifest (standing offload authority in
`TASK_QUEUE.md:843`); this brief's broad approval does not authenticate bytes.

```zsh
# Ed only. JW_SRC/JW_ID still name the ONE reviewed CLOSED root from step 6.
test "$(cat "$JW_ITEM/source-path.txt")" = "$JW_SRC"
test -s "$JW_ITEM/independent-receipt.txt"
test -s "$JW_ITEM/ed-approval.txt"
# Approval files name the source and manifest digest. For replaceable data,
# independent-receipt.txt contains the pinned restore evidence instead.
python3.13 -B - <<'PY'
import os
from pathlib import Path
src = Path(os.environ['JW_SRC'])
op = Path(os.environ['JW_OP'])
assert src.is_absolute() and src == src.resolve() and not src.is_symlink()
assert src not in (Path('/'), Path('/Users'), Path('/Users/edr'))
lines = (op / 'KEEP.txt').read_text().splitlines()
assert lines and all(x.startswith('/') for x in lines)
for line in lines:
    keep = Path(line)
    assert src != keep and src not in keep.parents and keep not in src.parents, \
        'KEEP overlap: '+line
assert op != src and src not in op.parents
PY
python3.13 -B "$JW_OP/manifest.py" tree "$JW_SRC" > "$JW_ITEM/predelete.json"
cmp "$JW_ITEM/source.json" "$JW_ITEM/predelete.json"
cmp "$JW_ITEM/source.json" "$JW_ITEM/cloud-roundtrip.json"
# STOP: record Ed's YES, independent receipt and KEEP/dependency review first.
printf '%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$JW_SRC" \
  "$(shasum -a 256 "$JW_ITEM/source.json")" 'DELETE_AUTHORIZED; see receipts' \
  >> "$JW_OP/deletions.tsv"
/bin/rm -rf -- "$JW_SRC"
test ! -e "$JW_SRC"
printf '%s\n' "archive=$JW_REMOTE/$JW_ID.tar.zst" \
  "manifest=$JW_REMOTE/$JW_ID.manifest.json" \
  "manifest_sha256=$(shasum -a 256 "$JW_ITEM/source.json")" \
  "independent_receipt=$JW_ITEM/independent-receipt.txt" \
  > "$JW_SRC.OFFLOADED.txt"
printf '%s\t%s\tDELETED\n' "$(date -u +%FT%TZ)" "$JW_SRC" \
  >> "$JW_OP/deletions.tsv"
/bin/df -k /System/Volumes/Data >> "$JW_OP/df-after-each.txt"
```

The independent receipt must actually be saved at the pointer's stated path;
for replaceable data write its reviewed pinned-revision/restore evidence there
instead. Keep local pointers, manifests and receipts. Back up the journal and
verify its own cloud and independent copies. The source manifest remains
immutable after authorization. A failed/partial deletion is logged as such and
resolved against that manifest; never declare completion because `rm` started.

Explicitly evict only the verified uploaded tar after independent verification
to reclaim its local staging bytes; do not delete the cloud object:

```zsh
/usr/bin/brctl evict "$JW_REMOTE/$JW_ID.tar.zst"
/bin/df -k /System/Volumes/Data > "$JW_OP/df-current.txt"
```

**STOP 8:** compare `df` against baseline. Require
`(available_after - available_before) * 1024 >= 450000000000` before saying
“450 GB freed.” APFS clone sharing meant pilot offload reclaimed much less
than summed root sizes (`7e06863b/RECORD.md:17`). Do not remove snapshots or KEEP
roots to force this result; unresolved capacity goes to Ed.

## 9. Admit the disk budget before downloading

450 GB = 419.1 GiB; nominal 360 GB = 335.3 GiB. Get exact checkpoint bytes from
the pinned HF metadata in step 11; 360 GB is a planning number. Use this budget:

| Incremental allocation | Admission rule |
|---|---|
| Full official bf16 repo | Exact pinned total bytes, nominal 360 GB; all 131 shards, not a selected-layer subset. |
| Resume/incomplete headroom | At least largest shard plus one verification working allowance; plan 20 GB until measured. Same target directory on resume, no second 360 GB cache. |
| New venvs/packages/logs | Plan 20 GB, measure after install; keep existing measurement venvs. |
| Future ALIGN window | At least current kit's declared floor; historical pilot floor 41.2 GB (`7e06863b/RECORD.md:17`). Re-evaluate for the next kit. |
| OS/free-space margin | At least 50 GB available throughout; not swap capacity. |
| Conversion | Exact expected output plus max simultaneously resident temp/output shards. UNFUNDED until measured; it is additional to bf16, not implicitly inside 450 GB. |

Nominal download-only gate is thus **491.2 GB available**, before conversion
output or a larger actual kit floor. Reclaiming 450 GB from a partially full
disk may meet it; reclaiming 450 GB alone does not prove it. Read-only `df`
checks after every large step enforce the residual margin. If conversion
cannot coexist with the verified bf16 repo, STOP and arrange approved external
storage or more eligible offload. Do not delete official weights, data backups
or custody while parity/conversion is unfinished.

## 10. Create isolated storage and venvs; exclude indexing and backups

New proposed locations under the established non-iCloud model/code roots:

```zsh
export JW_GOLD=/Users/edr/jw_models/flashnext-gold-20261105.noindex
export JW_GOLD_CODE=/Users/edr/code/JouleWise-flashnext-gold-20261105
mkdir -m 700 "$JW_GOLD"
touch "$JW_GOLD/.metadata_never_index"
sudo /usr/bin/tmutil addexclusion -p "$JW_GOLD"
/usr/bin/tmutil isexcluded "$JW_GOLD"
# Ed also adds this exact folder in Spotlight Privacy and confirms exclusion.
# .noindex plus .metadata_never_index are defense in depth, not a UI check.
mkdir "$JW_GOLD/envs" "$JW_GOLD/results" "$JW_GOLD/converted"
python3.13 -m venv "$JW_GOLD/envs/mlx"
python3.13 -m venv "$JW_GOLD/envs/reference"
"$JW_GOLD/envs/mlx/bin/python" -m pip install 'mlx==0.31.2' 'mlx-lm==0.31.3'
: "${JW_TORCH_VERSION:?Set harness-approved exact torch version}"
"$JW_GOLD/envs/reference/bin/python" -m pip install \
  "torch==$JW_TORCH_VERSION" 'transformers==5.22.1' safetensors huggingface_hub
"$JW_GOLD/envs/mlx/bin/python" -m pip freeze --all > "$JW_OP/mlx.freeze.txt"
"$JW_GOLD/envs/reference/bin/python" -m pip freeze --all > "$JW_OP/reference.freeze.txt"
"$JW_GOLD/envs/mlx/bin/python" -m pip check
"$JW_GOLD/envs/reference/bin/python" -m pip check
"$JW_GOLD/envs/mlx/bin/python" -c \
  'from importlib.metadata import version; print(version("mlx"), version("mlx-lm"))'
"$JW_GOLD/envs/reference/bin/python" -c \
  'from importlib.metadata import version; print(version("torch"), version("transformers"))'
```

**STOP 10:** mlx 0.31.2 / mlx-lm 0.31.3 match, transformers 5.22.1 matches,
torch is the harness-reviewed pin, dependency checks pass, Spotlight Privacy
and Time Machine exclusion confirmed. Archive freeze files and wheel hashes
for reproducibility; rebuild from them rather than re-resolving later. Heavy
dependencies are isolated: main's `pyproject.toml:17` currently constrains
`transformers<5.13`; **do not install `[mac]` into the reference venv or upgrade
the measurement venv**. The required MLX pins are corroborated in
`8d1ab6e2c:docs/align/pilot_protocol_v3.md:65–67`; reference version authority
is `1643e9aac4:docs/align/qwen4_exp_port/GOAL.md:13`.

## 11. Pin the official revision, download with resume, verify every LFS shard

No official checkpoint commit was available in the supplied offline records.
Ed/lead must resolve and approve one **full immutable commit SHA**, recorded
below. Never run parity against `main`, `latest`, community PR #1788, or a
community quantization. Network commands in this section are for the paused
measurement MBP only; none were run while authoring this document.

First resolve metadata without downloading weights:

```zsh
export JW_HF_REPO=Qwen/Qwen3.8-Flash-Next
export JW_CHECKPOINT="$JW_GOLD/official-bf16"
"$JW_GOLD/envs/reference/bin/python" -B - <<'PY'
import json, os
from pathlib import Path
from huggingface_hub import HfApi
info = HfApi().model_info(os.environ['JW_HF_REPO'], revision='main', files_metadata=True)
rows = []
for f in info.siblings:
    lfs = f.lfs
    rows.append(dict(path=f.rfilename, size=f.size,
                     sha256=lfs.sha256 if lfs else None))
out = dict(repo=info.id, revision=info.sha, files=rows)
Path(os.environ['JW_OP'], 'hf-proposed.json').write_text(json.dumps(out, indent=2)+'\n')
print('revision', info.sha)
print('total_bytes', sum(r['size'] for r in rows))
print('largest_file', max(r['size'] for r in rows))
print('safetensors_shards', sum(r['path'].endswith('.safetensors') for r in rows))
PY
```

**STOP 11a:** Ed/lead approves SHA, official repo, 131 shards and exact total;
recompute step 9 and remaining disk. A different layout/count stops for review.
Copy approved metadata to `hf-pinned.json`, set `JW_HF_REV` to its full SHA,
and keep both files immutable. The source of each expected SHA-256 is the HF
LFS oid at that revision, not a hash computed from a downloaded corrupt file.

```zsh
cp -p "$JW_OP/hf-proposed.json" "$JW_OP/hf-pinned.json"
export JW_HF_REV="$("$JW_GOLD/envs/reference/bin/python" -c \
  'import json,os; print(json.load(open(os.environ["JW_OP"]+"/hf-pinned.json"))["revision"])')"
"$JW_GOLD/envs/reference/bin/python" -B - <<'PY'
import hashlib, json, os, re
from pathlib import Path, PurePosixPath
from huggingface_hub import snapshot_download
p = json.loads(Path(os.environ['JW_OP'], 'hf-pinned.json').read_text())
assert p['repo'] == 'Qwen/Qwen3.8-Flash-Next'
assert p['revision'] == os.environ['JW_HF_REV'] and re.fullmatch('[0-9a-f]{40}', p['revision'])
for r in p['files']:
    path = PurePosixPath(r['path'])
    assert not path.is_absolute() and '..' not in path.parts
shards = [r for r in p['files'] if r['path'].endswith('.safetensors')]
assert len(shards) == 131 and all(re.fullmatch('[0-9a-f]{64}', r['sha256'] or '') for r in shards)
target = Path(os.environ['JW_CHECKPOINT'])
# Rerun this same call after interruption: existing/incomplete files are resumed
# by huggingface_hub. Do not force_download, delete .cache, or change revision.
snapshot_download(repo_id=p['repo'], revision=p['revision'], local_dir=target,
                  max_workers=2, force_download=False)
checks = []
for r in p['files']:
    f = target / r['path']
    assert not f.is_symlink() and f.is_file() and f.stat().st_size == r['size']
    h = hashlib.sha256()
    with f.open('rb') as stream:
        for b in iter(lambda: stream.read(8*1024*1024), b''):
            h.update(b)
    actual = h.hexdigest()
    if r['sha256'] is not None:
        assert actual == r['sha256'], 'LFS SHA mismatch: '+r['path']
    checks.append(dict(path=r['path'], size=r['size'], sha256=actual,
                       lfs_oid_sha256=r['sha256']))
index = json.loads((target / 'model.safetensors.index.json').read_text())
assert set(index['weight_map'].values()) == {r['path'] for r in shards}
Path(os.environ['JW_OP'], 'hf-verified.json').write_text(json.dumps(
    dict(repo=p['repo'], revision=p['revision'], files=checks), indent=2)+'\n')
print('VERIFIED', len(shards), 'shards; every LFS file matches pinned oid')
PY
shasum -a 256 "$JW_OP/hf-pinned.json" "$JW_OP/hf-verified.json" \
  > "$JW_OP/hf-receipts.sha256"
/bin/df -k /System/Volumes/Data
```

**STOP 11b:** every expected repository file present with correct size, every
LFS object (all 131 weight shards) SHA-256 equals its pinned oid, index names
exactly that shard set. Check the official text config's model type and 48-layer
count against the port/harness contract before loading. Hash-check any manually
recovered/resumed file again.
Non-LFS files have local SHA-256 recorded; their provenance is the pinned HF
snapshot, not an invented LFS oid. Preserve partial files after errors, log the
failure, and retry at the same SHA only after checking disk/network. Do not
convert or load an unverified checkpoint.

## 12. Install and run the gold-parity lane — pending its real CLI

Harness authority: **`lane/2026-11-05-align-flashnext-gold-parity`**. That ref,
its entrypoint, CLI, tolerances, torch pin and conversion command were **not in
this clone's local refs** when this runbook was authored. No network fetch was
authorized in the authoring session. **STOP 12a: obtain the lane's reviewed
commit and README/`--help`; do not substitute guessed flags or claim an
executable parity command is already known.** The following checkout commands
become usable only once the lead supplies the lane object to the MBP:

```zsh
: "${JW_HARNESS_COMMIT:?Set reviewed full gold-parity lane commit}"
git -C "$JW_CANON" cat-file -e "$JW_HARNESS_COMMIT^{commit}"
git -C "$JW_CANON" worktree add --detach "$JW_GOLD_CODE" "$JW_HARNESS_COMMIT"
git -C "$JW_GOLD_CODE" status --short --branch
git -C "$JW_GOLD_CODE" rev-parse HEAD > "$JW_OP/harness-head.txt"
git -C "$JW_GOLD_CODE" ls-tree -r --name-only HEAD -- scripts docs/align \
  > "$JW_OP/harness-files.txt"
```

The expected CLI contract, **to be mapped to the actual lane interface**, is:
verified local checkpoint directory `$JW_CHECKPOINT`, immutable checkpoint
revision/manifest, canonical MLX port file and its SHA-256, separate MLX and
torch interpreters, fixed seed/inputs, explicit precision/tolerances, all layer
indices 0–47, output custody `$JW_GOLD/results`, resumable per-layer receipts
and nonzero exit on mismatch/missing coverage. Record the actual `--help`
and exact argv in `$JW_OP/parity-command.txt` before execution. This is an
interface requirement, not a claim those option names exist.

Run the lane's tiny/config self-check first, then its complete real-weight
command with the approved argv. Success must demonstrate all 48 layers,
DeltaNet, QSA/indexer, MoE, hyper-connections, actual layer-1 n-gram PLE table,
embeddings, final norm and head, identical inputs on both implementations,
prefill and cached decoding, numerical errors and the justified bf16 bounds.
The fp32 tiny logit bound is ≤1e-4; real-weight bounds must be justified and
frozen before inspection, not relaxed until green (Goal items 2, 5 and 11,
`1643e9aac4:docs/align/qwen4_exp_port/GOAL.md:17–25`). A selected-shard smoke,
tiny fixture, zero-filled PLE, or one example output does not satisfy Goal 11.

Stream weights layer by layer rather than loading the full bf16 model on a
128 GB machine. The PLE spans about 35 shards / 100 GB by the goal's planning
record (`GOAL.md:42`). Before and after each phase record:

```zsh
/usr/bin/vm_stat > "$JW_OP/vm-before-phase.txt"
/usr/sbin/sysctl vm.swapusage > "$JW_OP/swap-before-phase.txt"
/bin/df -k /System/Volumes/Data > "$JW_OP/df-before-phase.txt"
```

Use unique phase filenames instead of overwriting earlier receipts. This is
correctness work, **not quiet-machine energy evidence**. If memory pressure,
swap growth, disk margin or unsupported paging prevents the full comparison,
stop and report incomplete coverage. No measurement may run while swapping.

**STOP 12b:** lead audits coverage, actual CLI/commit, both version locks,
checkpoint/port hashes and every mismatch disposition. Only then run the
lane's documented streaming conversion, after independently admitting output
and temp disk. Retain the official bf16 source. Produce a full SHA-256 manifest
of converted output (the step-6 tree helper can do this) and record command,
bits/grouping/paging policy and port hash. Then execute the lane's documented
fixed-text coherence/NLL, real-template tool-call round trip and fixed benchmark
items. Capture reference logprobs only if an approved endpoint supports them;
mark unavailable otherwise. These Goal-7 checks are separate from layer parity
and are not inferred from its pass. Commands for parity, conversion and these
checks remain blocked until the actual lane interface is supplied.

## 13. Restore ALIGN through the magistrate, with a fresh plan

1. Finish uploads; require no pending/error iCloud objects, downloads,
   compression, hashing, conversion, package installs or backup work. Verify
   KEEP paths and pinned model files against their pre-offload manifests.
   If a model was explicitly reclassified and removed, restore the **same
   revision to the original path**, verify all files and dependencies, and
   only then restore the kit. Record the exact HF `snapshot_download` call
   at that model's recorded repo/revision, not `main`.
2. Preserve both data backups, journal and all manifests/receipts. Re-measure
   free disk against the next kit's full footprint plus OS margin. Check
   swap/memory pressure and allow the machine to return to its baseline;
   no energy claims attach to the setup window. Restore only the reviewed
   Spotlight/other service state recorded at pause. Keep the new large model
   directory excluded from indexing and Time Machine.
3. Restore any temporarily unloaded non-measurement infrastructure from the
   saved exact plists and restore original disabled states. Do not resume a
   DONE BYTES/B6 loop. With Ed's go, remove **only this operation's** STOP
   file and restore the magistrate supervisor from its original plist:

```zsh
# Ed only, after steps 1–2 and confirmation the STOP was created by step 2.
test "$(cat /Users/edr/night-custody/magistrate/STOP)" = \
  'ALIGN paused for MBP offload and gold validation'
rm /Users/edr/night-custody/magistrate/STOP
/bin/launchctl enable "gui/$(id -u)/com.joulewise.magistrate"
/bin/launchctl bootstrap "gui/$(id -u)" \
  /Users/edr/Library/LaunchAgents/com.joulewise.magistrate.plist
/bin/launchctl print "gui/$(id -u)/com.joulewise.magistrate"
```

4. The magistrate verifies pinned checkout/venv/model identity, current
   ledger/acceptance, power/thermal/keepawake/census and disk gates, then
   selects the currently approved ALIGN kit. It creates a **new session root,
   plan and future t0**, sends the required notice, and installs through the
   kit. Never bootstrap saved night/deadman plists with stale t0 or reuse a
   prior measurement plan. The recorded interface is
   `8d1ab6e2c:scripts/align_pilot_session.py:430–445`:

```zsh
# Magistrate only, after choosing the current reviewed kit and new root.
: "${JW_NEXT_SESSION:?Set approved NEW /Users/edr/night-align/session root}"
"$JW_MEAS/.venv/bin/python" -B "$JW_MEAS/scripts/align_pilot_session.py" \
  prepare --measurement-root "$JW_MEAS" --session-root "$JW_NEXT_SESSION"
# STOP: normal plan review, notice/ack and install gates; exit all agents
# through the established arm handoff before measurement t0.
"$JW_MEAS/.venv/bin/python" -B "$JW_MEAS/scripts/align_pilot_session.py" \
  install --session-root "$JW_NEXT_SESSION"
```

**STOP 13:** record ALIGN restored only after the fresh plan/notice/install
gates are met, setup activity is gone and the no-agent measurement handoff is
complete. If any restoration check fails, leave ALIGN paused and tell the lead
the exact failed gate; do not shorten or bypass admission.

## 14. Ed-only actions and handoff checklist

Ed owns: physical machine confirmation and measured SSD capacity; iCloud quota,
account and any storage purchase; confirmation ALIGN is paused; control of
personal apps/system launchers and system privileges; independent-copy device
and receipt; exact-manifest deletion approval and every irreversible removal;
any requested change to sealed retention (not granted here); approval of
checkpoint/torch/harness pins; Spotlight Privacy/Time Machine changes; and the
go to restore ALIGN. Measurement agents cannot authorize these on Ed's behalf.

The operation handoff records machine/SSD, before/after `df`, bytes actually
freed, per-root KEEP/offloaded/deleted status, exact cloud/second-copy locations
and manifest hashes, every deletion receipt, pending uploads/errors, pinned
checkpoint and all 131 shard results, venv locks, harness CLI/commit and
coverage, conversion/end-to-end outcomes, and pause/restoration status.
Report UNKNOWN, BLOCKED and PROVISIONAL explicitly. **No offload or hardware
validation occurred merely because this runbook was written.**
