# Measurement MacBook Pro offload and gold setup runbook

Operator: Ed and the measurement-Mac magistrate, during an explicitly paused,
non-measurement window of approximately two days. **This document has not been
executed. Do not execute it on the analysis laptop.** The measurement machine is
Mac15,9, M3 Max, 128 GB (`docs/process_traces/2026-11-01-interactive-26be5929/RECORD.md:3`).
Ed confirmed its SSD is **1 TB** on November 5; step 1 still measures actual
available space and the APFS container before admission.

The objective is **minimal verified offload to about 150 GB available**, then
full 48-layer real-weight gold parity and conversion by **streaming layer
groups**. The official checkpoint is nominally 360 GB bf16 / 131 shards, but
only the current bounded working unit is staged on disk. Converted output is
about 90–95 GB; peak additional allocation is about 120 GB, including a working
unit of about 15 GB and overhead. The starting target leaves a separate 30 GB
free-space floor. Step 9 replaces estimates with measured byte budgets.

Authority: the lead's November 5 streaming revision of Goal 11 and status log
in `docs/align/qwen4_exp_port/GOAL.md` on `port/qwen4-exp-mlx`, supplied in the
revision brief. The authoring clone's offline `origin/port/qwen4-exp-mlx` still
resolves to `1643e9aac43ebfc10443a31c30a0cdc506bcbfc6`, whose item 11 describes
the superseded full-checkpoint plan. The streaming brief controls this revision;
the operator records the updated goal commit when the lead supplies it.
Offload authority preserves every sealed retention and verify-then-delete gate.

Scheduling authority: **RUN_STATE item 170 (PR #662), as relayed by the lead:
ALIGN is paused after pilot 9.** This clone's base contains only item 169,
which records pilot 9 armed. The Mac operator must obtain the current harvest
and pause receipts; neither historical text proves live completion.

| Slot | Work admitted |
|---|---|
| Pilot 9 still collecting | Off-machine runbook/harness review only; no Mac steps, hashing, downloads or imports. |
| Pilot 9 terminal, harvest/desk still writing | Let the magistrate finish its normal harvest, ledger pin and desk custody. Keep pilot 9's root intact; this runbook runs no harvest. |
| Harvest and required desk products saved, no source writers | Confirm the item-170 pause and perform steps 1–11 in order, including re-arm disable in step 2. Offload only enough eligible roots to reach the budget. |
| Reviewed harness available | Step 12 runs in resumable units; it may span multiple operator sessions. Leave ALIGN paused at every checkpoint. |
| Validation complete, lead/Ed release the pause | Step 13 admits a fresh ALIGN plan; no automatic next pilot after pilot 9. |

Run numbered steps individually in Terminal. **STOP means leave the source
intact and resolve the named condition before continuing.** Save receipts in the
operation journal; never put measurement contents in this document or Git.
When resuming an operator session, keep the same operation/journal and gold
directories, restore their recorded variables and disk guard, re-confirm the
pause and available bytes, and use the reviewed harness's resume entrypoint.
Do not rerun initialization that creates a new journal or overwrites pins and
receipts; restart only from the last validated durable unit checkpoint.
All block-5 handling is metadata, opaque byte copying/compression and SHA-256
only: never parse or print measurement values. Do not run
`scripts/run_b5_analysis.py`, a reducer, a harvest, or a release/recompute here.
No agent may inspect a real `restricted/` directory. Such directories are
excluded from the commands below and require the authorized custody operator;
they are never silently omitted from an archive declared complete.

**Disk STOP throughout:** all GB budgets below are decimal bytes. Abort the
active allocating operation if available space falls below **30,000,000,000
bytes at any point**; retain sources, receipts and recoverable partial work.
Check before/after every numbered step, archive hydration, download and output
write, and monitor during long operations. Admit each operation only if its
maximum additional allocation still leaves 30 GB. A check at step end alone
does not protect a long write. The reviewed streaming runner must enforce this
floor during downloads/conversion; absent that enforcement, step 12 stays STOP.

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

**STOP 1:** Ed confirms Mac15,9 / M3 Max / 128 GB / 1 TB SSD, physical container size,
Data volume and actual available bytes. A different machine stops this runbook.
Record APFS sharing, snapshots and purgeable storage separately. Use `df`
available space for admission; do not count purgeable space, promised iCloud
evictions, summed `du` sizes, or the SSD's marketed capacity as available space.
Below 30 GB, stop here for a separately reviewed space-recovery action; do not
start archive staging or discard protected data to bootstrap this procedure.

## 2. Pause ALIGN and prove nothing can arm

Do this before hashing, compression, uploads, model downloads or imports. A
live plan takes precedence: if collection is running, stop here and let the
magistrate close it through its normal terminal procedure. Do not kill a
collection to make room. The recorded pilot-9 plan was armed on November 5;
its old record is not evidence of today's terminal or harvested state
(`docs/process_traces/2026-11-05-magistrate-c110a6c9/RECORD.md:48–54`).
Require the normal pilot-9 harvest/ledger-pin receipt and saved `PILOT.json`
and required desk products before offload. Schedule the Mac session after that
handoff under item 170 / PR #662; do not start pilot 10. Obtain these receipts
from the magistrate without opening measurement contents in this runbook.

The following paths are recorded: canonical repository
`scripts/install_magistrate_watchdog.sh:37`, measurement checkout
`docs/process_traces/2026-11-02-magistrate-0eafdaa2/RECORD.md:96`, ALIGN root and
plan layout `docs/process_traces/2026-11-05-magistrate-c110a6c9/RECORD.md:50`.
The journal and all `flashnext-gold-*` paths below are **new proposed paths**,
not claims that those directories already exist.

```zsh
set -euo pipefail
setopt extendedglob
# Admission guard: argument is the maximum NEXT additional allocation in bytes.
# Long-running writers also need the continuous floor enforcement above.
jw_disk_check() {
  python3.13 -B - "${1:-0}" <<'PY'
import os, sys
s = os.statvfs('/System/Volumes/Data')
free = s.f_bavail * s.f_frsize
next_bytes = int(sys.argv[1])
print('available_bytes', free, 'next_allocation_bytes', next_bytes)
if next_bytes < 0 or free < 30_000_000_000 + next_bytes:
    raise SystemExit('STOP: disk floor or next-allocation budget would fail')
PY
}
jw_disk_check
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

**STOP 2:** Ed/magistrate attest: pilot 9 harvested and required desk custody
saved, item-170 pause confirmed, terminal plan, no collection process or
`collection.active`, no scheduled t0, night/deadman absent, loops unable to
launch, resident agents drained, every automatic reloader accounted for. A
missing process in `ps` alone does not prove an armed launchd job is absent.
No measurement resumes during any offload or setup step. Agent work is allowed
only in this paused non-measurement window; **all agents must exit before any
future measurement** (`AGENTS.md:60–64`).

## 3. Inventory KEEP dependencies and the minimum offload candidates

Start with metadata only for the exact candidate and KEEP roots supplied by the
magistrate; expand only as needed to select a CLOSED leaf. Do not follow
symlinks. BSD `du -I` prunes real `restricted` directories; mark their excluded
size UNKNOWN and send them to the custody operator. Never `cat`, sample or
preview a data file.

```zsh
# Operator prepares exact absolute candidate paths, one per line, no globs.
test -s "$JW_OP/candidates.txt"
while IFS= read -r root; do
  /bin/df -k "$root"
  /usr/bin/du -sk -I restricted "$root"
done < "$JW_OP/candidates.txt" > "$JW_OP/root-metadata.txt"
jw_disk_check
```

Use a per-root ledger with columns: exact path, owning study/registration,
source citation, allocated KiB, logical bytes (later manifest), status
KEEP/CLOSED/UNKNOWN, irreplaceable yes/no, cloud destination, independent-copy
location/device, verified manifest SHA, deletion receipt. UNKNOWN is KEEP.
Do not expand into a home-wide cleanup or wipe. The old broad temp-removal
command in `RUN_STATE.md:38` is not adopted. Default selection order is:

1. **Already-offloaded ALIGN roots first.** Re-read the existing cloud archive
   and authenticated manifest, verify the independent restore, then delete
   only a surviving local CLOSED source through steps 6–8. A pointer whose
   source is already gone offers no additional free bytes. Do not upload a
   duplicate archive merely to reuse the new-root commands.
2. **Pilots 0–3 and 6–9 after their harvests.** Require per-root terminal,
   harvest and required desk-product custody receipts and no remaining
   writers/dependencies. Deduplicate paths already covered by tier 1. Pilot
   numbers are not directory suffixes; pilot 9 is `pilot-v8-*`. Keep its root
   until its harvest and desk handoff finish. Apply all verification gates.
3. **Unused models only if still needed.** First list each candidate's repo,
   full revision, exact snapshot/blob paths, per-file digests, restore command
   and live references in the ledger. Resolve shared HF blobs before selecting
   a leaf. Keep all Qwen3-30B anchor revisions and Qwen3.8-27B (step 4).

After each root, measure actual available bytes. **Stop offloading once about
150 GB is available and the measured step-9 budget passes.** If already enough
is free, skip offload mutations; still record KEEP/identity baselines required
by steps 6 and 13. Other B6/BYTES/calibration/personal roots are custody
exclusions here, not a fallback deletion queue. If these candidates cannot
meet admission, stop for the lead's revised storage plan; preserve KEEP.

Records establish these candidates and custody exclusions; add any dependency
that the current candidate review discovers:

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
   **Models 3–4 stay on-device under this runbook**, including every shared
   blob needed by the Qwen3-30B anchors and Qwen3.8-27B. Add any other anchor
   revision named by the current kit to KEEP. For tier-3 unused models,
   require no sealed/live obligation, a full revision and per-file digest
   inventory, a verified cloud copy and pinned restore evidence before
   deletion. Never delete a model named by an open roster
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

**STOP 4:** Ed and the lead review the per-root classification and ordered
minimal candidate list. Block-5 originals stay on-device until after release;
this runbook supplies no B5-original deletion. If the eligible list cannot
reach the measured streaming budget, retain protected bytes and ask for a
revised storage plan. No wipe or retention waiver is supplied here.

Save a complete plain-text list of exact absolute KEEP roots in
`$JW_OP/KEEP.txt` (one path per line, no comments or glob patterns), expanding
the table's patterns from metadata only. Include required individual files,
the journal, active infrastructure, original B5 roots and every discovered
sealed dependency. This is an additional deletion guard, not a replacement
for the dependency review.

## 5. Check quota, staging space and throughput for the selected roots only

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
jw_disk_check 536870912  # Probe plus its local cloud-folder copy.
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
jw_disk_check
```

Compute sustained throughput as `268435456 / elapsed_seconds` bytes/s. Repeat
with the first real archive, and plan using the slower rate. Reserve quota
for the **uncompressed manifest total** until actual compression is measured;
model weights may compress poorly. Time estimate = upload bytes / measured
bytes/s, plus complete source hashing, archive verification, remote hydration
and independent-copy verification. Size the upload from only the selected
roots; existing verified archives need re-reading, not another upload. The
nominal cumulative 360 GB checkpoint transfer takes about 80/16/8 hours at
10/50/100 Mbit/s, even though it is never retained all at once; shared-shard
re-downloads and retries can add transfer. Two days is a planning allowance,
not a guarantee. Finish verification serially so hydrated archives do not
accumulate on the SSD.

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

For an **existing offload with a surviving local source**, reuse its exact
archive/manifest paths. Anchor the original authenticated manifest and archive
digest in a new operation receipt; compare the current source before and after
verification to that manifest. If its format differs from the helper below,
the lead must review a complete name/type/length/hash comparison without
replacing the original trust anchor. Skip only new-archive creation/upload;
STOP 6a, post-upload eviction/re-download and STOP 6b, independent full restore
in step 7, and Ed's step-8 deletion still apply. Missing coverage means KEEP.
Set its hydration/staging byte ceiling from the recorded archive length
before calling `jw_disk_check`; do not inherit another root's budget.
The packaging commands below are for a **new** offload only.

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
: "${JW_ARCHIVE_BUDGET_BYTES:?Set archive plus staging upper bound from manifest}"
jw_disk_check "$JW_ARCHIVE_BUDGET_BYTES"
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
jw_disk_check
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
# Budget the bytes still to hydrate; wait for eviction before admission.
jw_disk_check "$JW_ARCHIVE_BUDGET_BYTES"
/usr/bin/brctl download "$JW_REMOTE/$JW_ID.tar.zst"
/usr/bin/brctl download "$JW_REMOTE/$JW_ID.manifest.json"
cmp "$JW_ITEM/source.json" "$JW_REMOTE/$JW_ID.manifest.json"
shasum -a 256 -c "$JW_ITEM/archive.sha256"
zstd -dc "$JW_REMOTE/$JW_ID.tar.zst" | \
  python3.13 -B "$JW_OP/manifest.py" archive > "$JW_ITEM/cloud-roundtrip.json"
cmp "$JW_ITEM/source.json" "$JW_ITEM/cloud-roundtrip.json"
jw_disk_check
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
jw_disk_check
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

**STOP 8:** record both `available_after * 1024` and the actual reclaimed
`(available_after - available_before) * 1024` bytes from `df -k`. The target is
about **150,000,000,000 available bytes**, not a prescribed deletion volume.
When it and step 9 pass, stop deleting. APFS clone sharing meant pilot offload
reclaimed much less than summed root sizes (`7e06863b/RECORD.md:17`). Do not
remove snapshots or KEEP roots to force admission. Check the 30 GB floor after
each upload, hydration, deletion and eviction; unresolved capacity goes to Ed.

## 9. Admit the disk budget before downloading

Use measured available bytes in execution order. About 150 GB free is
139.7 GiB; it is an admission target on the confirmed 1 TB SSD. Nominal peak
**additional allocation** is about 120 GB, leaving 30 GB available. It comprises
up to 95 GB converted output + about 15 GB maximum working unit + about 10 GB
for new environments, metadata, activation/cache checkpoints, journals and
temporary writes. These are planning estimates, not measured guarantees.

| Step / allocation order | Accounting and STOP check |
|---|---|
| 1–4: identify, pause, inventory | Record initial available bytes `F0`; only small control/manifest writes. Below 30 GB: STOP. Mark KEEP before selecting a source. |
| 5: quota/probe | Budget two local 256 MiB probe copies plus receipts. New cloud archives consume local SSD until uploaded and explicitly evicted. |
| 6–8: one root at a time | Before packaging/hydration, require available bytes ≥ 30 GB + maximum added archive/staging bytes. Verify cloud and independent restore, authorize/delete one local root, evict verified cloud staging, then measure the actual `df` gain. Stop offloading at about 150 GB available once the remaining budget fits. |
| 9–10: setup | Freeze the byte budget, then measure new venv/package/metadata/log allocation. Include pip/HF cache and temporary space in the overhead ceiling; reuse one location on resume. Existing measurement environments and both anchor models stay in place. |
| 11: metadata only | Fetch pinned config/tokenizer/index and LFS metadata; derive exact layer-group shard unions from `weight_map`. No bf16 bulk download. Replace the estimated largest working unit with its true maximum, including incomplete downloads and temporary output overlap. |
| 12: each streaming unit | From current free bytes `F`, admit only if `F ≥ 30 GB + next unit's maximum incremental allocation`. Download/verify → gold parity with real carried activations → convert/commit output and journal → delete that verified bf16 working unit → measure space. Converted shards accumulate toward 90–95 GB; bf16 working units do not accumulate. |
| 12: final peak | Current available bytes must cover **remaining converted output + largest additional simultaneous working/temp unit + remaining overhead + 30 GB**. Do not double-count setup/output already reflected in current `df`. Recompute before every unit and after a retry; reject a projected overrun before starting it. |
| 13: future ALIGN | Re-admit the next kit's full footprint and the 30 GB floor before re-arm. Historical pilot floor 41.2 GB is context (`7e06863b/RECORD.md:17`), not a second concurrent pilot during gold work. |

The group plan must bound **simultaneous** disk use. Layers 2–47 are expected
to touch about 3 shards / 7 GB each. Layer 0 touches about 24 shards, so it
needs bounded shard/tensor subunits rather than staging that whole union.
Layer 1's n-gram table spans about 35 shards / 100 GB bf16, processed one shard
at a time (step 12). A 15 GB working allowance is valid only after the harness
accounts for these large unions, shared shards, partial files, output temp
files and activation checkpoints. No second full HF snapshot/cache is allowed.

**STOP 9:** measured free space and the preliminary budget must admit the
bounded setup and metadata work of steps 10–11. Final admission for weights
waits for the exact step-11 group schedule and step-12 harness review; repeat
this gate then. If measured output, working unit or overhead exceeds the
120 GB estimate, re-admit the actual total plus the 30 GB floor. Stop for a
revised plan if minimal eligible offload cannot fund it; retain all KEEP data.
No full 360 GB checkpoint is required on disk. Never delete custody to pay for
an unbounded layer-0 or n-gram working set.

## 10. Create isolated storage and venvs; exclude indexing and backups

New proposed locations under the established non-iCloud model/code roots:

```zsh
export JW_GOLD=/Users/edr/jw_models/flashnext-gold-20261105.noindex
export JW_GOLD_CODE=/Users/edr/code/JouleWise-flashnext-gold-20261105
: "${JW_SETUP_BUDGET_BYTES:?Set approved new setup and temporary allocation ceiling}"
jw_disk_check "$JW_SETUP_BUDGET_BYTES"
mkdir -m 700 "$JW_GOLD"
touch "$JW_GOLD/.metadata_never_index"
sudo /usr/bin/tmutil addexclusion -p "$JW_GOLD"
/usr/bin/tmutil isexcluded "$JW_GOLD"
# Ed also adds this exact folder in Spotlight Privacy and confirms exclusion.
# .noindex plus .metadata_never_index are defense in depth, not a UI check.
mkdir "$JW_GOLD/envs" "$JW_GOLD/results" "$JW_GOLD/converted" \
  "$JW_GOLD/metadata" "$JW_GOLD/working" "$JW_GOLD/activations"
export JW_METADATA="$JW_GOLD/metadata"
export JW_CHECKPOINT="$JW_GOLD/working"  # Rolling verified bf16 unit only.
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
jw_disk_check
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

## 11. Pin the official revision and metadata; plan layer-group streaming

No official checkpoint commit was available in the supplied offline records.
Ed/lead must resolve and approve one **full immutable commit SHA**, recorded
below. Never run parity against `main`, `latest`, community PR #1788, or a
community quantization. Network commands in this section are for the paused
measurement MBP only; none were run while authoring this document.

First resolve metadata without downloading weights:

```zsh
export JW_HF_REPO=Qwen/Qwen3.8-Flash-Next
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

**STOP 11a:** Ed/lead approves SHA, official repo, 131 shards and exact total
transfer bytes. A different layout/count stops for review. This total sizes
the network transfer, not a resident bf16 disk allocation.
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
from huggingface_hub import hf_hub_download
p = json.loads(Path(os.environ['JW_OP'], 'hf-pinned.json').read_text())
assert p['repo'] == 'Qwen/Qwen3.8-Flash-Next'
assert p['revision'] == os.environ['JW_HF_REV'] and re.fullmatch('[0-9a-f]{40}', p['revision'])
for r in p['files']:
    path = PurePosixPath(r['path'])
    assert not path.is_absolute() and '..' not in path.parts
assert all(isinstance(r['size'], int) and r['size'] >= 0 for r in p['files'])
shards = [r for r in p['files'] if r['path'].endswith('.safetensors')]
assert len(shards) == 131 and all(re.fullmatch('[0-9a-f]{64}', r['sha256'] or '') for r in shards)
target = Path(os.environ['JW_METADATA'])
# Explicit metadata allowlist. No weight shard or remote Python is fetched here.
names = {'model.safetensors.index.json', 'config.json', 'tokenizer.json',
         'tokenizer_config.json', 'special_tokens_map.json',
         'generation_config.json', 'chat_template.jinja'}
selected = [r for r in p['files'] if r['path'] in names]
assert {'model.safetensors.index.json', 'config.json'} <= {r['path'] for r in selected}
checks = []
for r in selected:
    s = os.statvfs('/System/Volumes/Data')
    if s.f_bavail * s.f_frsize < 30_000_000_000 + r['size']:
        raise SystemExit('STOP: metadata download would violate disk floor')
    hf_hub_download(repo_id=p['repo'], revision=p['revision'], filename=r['path'],
                    local_dir=target, force_download=False)
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
Path(os.environ['JW_OP'], 'hf-metadata-verified.json').write_text(json.dumps(
    dict(repo=p['repo'], revision=p['revision'], files=checks,
         expected_shards=shards), indent=2)+'\n')
print('VERIFIED metadata; expected weight shards', len(shards), '; weights not downloaded')
PY
shasum -a 256 "$JW_OP/hf-pinned.json" "$JW_OP/hf-metadata-verified.json" \
  > "$JW_OP/hf-receipts.sha256"
/bin/df -k /System/Volumes/Data
jw_disk_check
```

**STOP 11b:** metadata sizes/hashes pass, index names exactly the pinned shard
set, official text config's model type and 48-layer count match the port/harness
contract. Non-LFS metadata gets a local SHA-256 bound to its pinned HF revision;
do not invent an LFS oid. If the actual tokenizer/template needs other files,
extend the exact metadata allowlist under review and record their hashes.

The reviewed harness derives ordered layer groups from the index's
`weight_map`, using the actual tensor-to-component mapping. Its saved plan
names required tensors, shard union, ordered bounded subunits, byte ceilings,
shared-shard consumers and embedding/final-norm/head coverage. Account for
every index entry; any non-text exclusion must be explicit and reviewed.
Freeze this plan and re-admit step 9 before the first weight download. No
unfiltered `snapshot_download` or whole-repo CLI download belongs in this loop.

For each step-12 unit, fetch only its listed shard filenames at `JW_HF_REV`
into the rolling `JW_CHECKPOINT` directory. Resume there without changing the
revision or duplicating caches. Before loading **any** tensor, verify its
entire containing shard's exact size and SHA-256 against the pinned HF LFS oid;
record the actual digest, expected oid, path and unit in the journal. Re-hash
every recovered/resumed file. A shard may contain other layers' tensors:
extract only planned tensors, and either retain it within the admitted bound
until all immediate consumers finish or re-download/re-verify it later.
Preserve partials and error receipts on failure; retry only after checking
space/network. A partial or hash mismatch never enters parity or conversion.

## 12. Reviewed gold-parity harness: stream, compare, convert, journal, prune

Harness authority: **`lane/2026-11-05-align-flashnext-gold-parity`**. That ref,
its entrypoint, CLI, tolerances, torch pin and conversion command remain
**unavailable in this clone's local refs**; the branch may not have been pushed
yet. No network fetch was authorized in the authoring session. **STOP 12a:
obtain the lane's reviewed commit and README/`--help`, and lead review of its
streaming parity/conversion, disk-floor and resume behavior before downloading
weights or running the loop.** The following checkout commands become usable
only once the lead supplies the lane object to the MBP:

```zsh
: "${JW_HARNESS_COMMIT:?Set reviewed full gold-parity lane commit}"
git -C "$JW_CANON" cat-file -e "$JW_HARNESS_COMMIT^{commit}"
git -C "$JW_CANON" worktree add --detach "$JW_GOLD_CODE" "$JW_HARNESS_COMMIT"
git -C "$JW_GOLD_CODE" status --short --branch
git -C "$JW_GOLD_CODE" rev-parse HEAD > "$JW_OP/harness-head.txt"
git -C "$JW_GOLD_CODE" ls-tree -r --name-only HEAD -- scripts docs/align \
  > "$JW_OP/harness-files.txt"
```

The **intended CLI** supplies `--mlx-module` for the canonical MLX module,
an explicit **layer-range** selector, and **resume** (`--resume`) against the
progress journal. Confirm actual range flag spelling and inclusive/exclusive
endpoints from the reviewed `--help`; the complete schedule must cover layers
0–47. A resumed later range must restore validated real incoming activations
and caches, not initialize random inputs. Do not publish a guessed executable
command before review.

The remaining interface contract includes the rolling shard directory
`$JW_CHECKPOINT`, pinned metadata/index/group-plan hashes, canonical module
SHA-256, separate MLX/torch interpreters, fixed prompt/tokenizer/seed hashes,
precision/tolerances, chosen quantization, output `$JW_GOLD/converted`, results
`$JW_GOLD/results` and activation checkpoints `$JW_GOLD/activations`. It must
exit nonzero on mismatch, missing coverage, incompatible resume or disk-floor
failure. Record actual `--help`, exact argv for parity/conversion/resume and
the reviewed commit in `$JW_OP/parity-command.txt` before execution.

Run the lane's tiny/config self-check first. Freeze tolerances before viewing
real-weight differences: fp32 tiny max abs logit difference ≤1e-4; justify the
bf16 real-weight and quantization bounds separately (Goal items 2, 5 and 11).
For the fixed prompts, the real-weight pass carries the actual validated
reference activations from one layer/group to the next and supplies identical
copies to MLX and transformers. Preserve all required hyper-connection streams,
DeltaNet state and attention caches for prefill and cached decoding. A fresh
random hidden state at each layer cannot establish the full gold pass.

Execute this loop in the **frozen `weight_map` group/subunit order**:

1. **Admit and download.** Record current free bytes and the next unit's full
   additional-allocation ceiling. Fetch only its shards; verify complete
   shard lengths and SHA-256s against HF LFS oids before extracting tensors.
   Enforce the 30 GB floor during download, not just after it.
2. **Gold parity.** Run the planned layers/components in both implementations
   on the same real incoming activations. Save numerical errors, frozen
   tolerances, per-component coverage and passing receipts. Carry validated
   real outputs forward; save input/output activations and decoding state
   with hashes so a later unit can resume without old bf16 shards. Gold uses
   the official unquantized tensors; converted weights do not replace them
   in the reference chain.
3. **Convert and commit.** Convert those verified, parity-passed tensors to
   the lead-chosen highest precision MLX quantization that fits the 128 GB
   no-swap memory constraint (core bits/grouping and n-gram paging policy
   measured and recorded). Append new output shards and SHA-256 manifest
   entries, recording source tensor/shard identities and quantization settings.
   “Append” means new immutable safetensors files with an atomically updated
   index/manifest, not appending raw bytes to an existing safetensors file.
   Include quantization validation in the reviewed unit's completion gate.
4. **Durable checkpoint, then bf16 cleanup.** Re-read/hash output files and
   activation checkpoints; commit the manifest/index and journal checkpoint
   durably (temporary write, flush/fsync and atomic publication). Only after
   parity, conversion and restart state are committed may the runner delete
   the exact reproducible bf16 working shards it no longer needs. Record
   each deletion and measured free bytes. Keep LFS metadata, verification
   receipts and gold results. This cleanup authority covers only the new
   official-checkpoint working directory, never measurement/custody roots.
5. **Resume or advance.** At restart, validate all pins and re-hash every
   committed output/activation file before skipping a completed unit. Recover
   an interrupted output transaction without duplicate manifest entries or
   duplicate output copies; re-download/re-verify missing source shards when
   needed. Never infer completion from file existence. Advance only from a
   fully committed checkpoint; preserve failure evidence and stop on mismatch.

**Large groups:** layers 2–47 are expected to use about 3 shards / 7 GB per
layer. Layer 0 spans about 24 shards: the reviewed harness must process bounded
shard/tensor subunits and establish complete layer parity before advancing
its activations. It must not download that entire union at once. Layer 1's
n-gram PLE table spans about 35 shards / 100 GB bf16. Derive the row IDs
required by the frozen prompts/tokenization and decoding cases; for each
shard verify its whole-file LFS hash, gather only the actual needed rows for
gold parity, and stream **all** table tensors through conversion in bounded
chunks. Commit that shard's conversion and row-parity/checkpoint evidence,
then delete its bf16 source before fetching the next. Accumulate actual PLE
outputs/state until the layer is complete. Report fixed-prompt row coverage
honestly; untouched rows are converted, not claimed parity-tested. No full
100 GB bf16 table or 24-shard layer-0 staging allocation is admitted. If the
harness cannot establish these streaming parity boundaries within budget,
STOP 12a remains in force.

The progress journal binds each transaction to: HF revision and LFS metadata,
index/group-plan/module hashes, harness commit and both environment locks,
fixed prompts/seed/precision/tolerances, quantization settings, layer/subunit
and tensor coverage, incoming/outgoing activation/cache hashes, expected and
actual source digests, parity results, output paths/lengths/SHA-256s, free-byte
readings and phase state. Distinguish `download_verified`, `parity_passed`,
`conversion_committed` and `source_pruned`; record failures and UTCs. A resume
with different pins, prompts, bounds or quantization needs a new reviewed run.

Before/after each unit, also record memory and disk state:

```zsh
/usr/bin/vm_stat > "$JW_OP/vm-before-phase.txt"
/usr/sbin/sysctl vm.swapusage > "$JW_OP/swap-before-phase.txt"
/bin/df -k /System/Volumes/Data > "$JW_OP/df-before-phase.txt"
```

Use unique unit/phase filenames instead of overwriting earlier receipts. This is
correctness work, **not quiet-machine energy evidence**. If memory pressure,
swap growth, disk margin or unsupported paging prevents the full comparison,
stop and report incomplete coverage. No measurement may run while swapping.

**STOP 12b (each unit):** no next unit or source pruning until the reviewed
parity/conversion/checkpoint gates above pass and disk admission holds. A failed
unit retains its bf16 source and evidence; stop and disposition the mismatch
before retrying. Reproducible official shards may be pruned after this gate;
their pinned provenance and journal remain available for re-download.

**STOP 12c (whole pass):** lead audits all 48 layers, DeltaNet, QSA/indexer,
MoE, hyper-connections, actual fixed-prompt n-gram PLE rows, embeddings, final
norm/head and final logits for prefill and cached decoding. Audit cumulative
receipts accounting for all 131 official shards, the complete required-tensor
conversion manifest (and explicit exclusions), both version locks, actual
CLI/commit, checkpoint/module hashes and every mismatch disposition. Re-read
the final converted files against their full SHA-256 manifest (the step-6
tree helper can produce an additional inventory). A selected-layer smoke,
tiny fixture or zero-filled PLE cannot satisfy this gold pass.

Then run the lane's documented end-to-end checks **from the converted output**:
fixed-text coherence/NLL, real-template tool-call round trip and fixed benchmark
items, with measured resident bytes/no-swap memory validation. Capture reference
logprobs only if an approved endpoint supports them; mark unavailable otherwise.
These Goal-7 checks are separate from gold parity and remain blocked until
the reviewed lane interface is supplied. Keep output, manifests, gold receipts
and restart checkpoints; the complete bf16 checkpoint need never coexist on
the SSD.

## 13. Restore ALIGN through the magistrate, with a fresh plan

1. Finish uploads; require no pending/error iCloud objects, downloads,
   compression, hashing, conversion, package installs or backup work. Verify
   KEEP paths and pinned model files against their pre-offload manifests.
   The Qwen3-30B anchors and Qwen3.8-27B have stayed on-device. If a previously
   unused, offloaded model becomes a dependency of the next kit, restore the
   **same revision to the original path**, verify all files/dependencies and
   admit its additional disk before restoring the kit. Record its exact repo,
   full revision and restore command.
2. Preserve both data backups, journal and all manifests/receipts. Re-measure
   free disk against the next kit's full footprint plus the 30 GB floor. Check
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

4. ALIGN stays paused after pilot 9 until the lead/Ed explicitly schedule its
   return; reaching a gold checkpoint does not authorize another pilot.
   The magistrate verifies pinned checkout/venv/model identity, current
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
coverage, streaming journal/resume state and activation hashes, actual peak
working bytes and lowest free bytes, conversion/end-to-end outcomes, unused
model revision inventory, and pilot-9 harvest/pause/restoration status.
Report UNKNOWN, BLOCKED and PROVISIONAL explicitly. **No offload or hardware
validation occurred merely because this runbook was written.**
