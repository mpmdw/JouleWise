# Measurement MacBook Pro offload and gold setup runbook

**ED-MANUAL-ONLY, not executed.** Use only on the paused measurement Mac
(Mac15,9, M3 Max, 128 GB, 1 TB internal SSD). Never run these commands from
an agent on the analysis laptop or while measurement is active. The analysis
laptop's 7-worker job and blinded inputs are outside this procedure.

Primary storage plan: Ed attaches a **1–2 TB external NVMe SSD over
Thunderbolt/USB4**, APFS, excluded from Spotlight and Time Machine (step 9).
`JW_GOLD`, rolling bf16 shards, caches, converted model and paged n-gram table
live there. A separate durable backup device is preferable; gold scratch and
the sole independent custody backup must not compete for unbudgeted space.
Internal SSD alone cannot hold the converted model plus the next ALIGN window.
The nominal gold streaming peak is 120 GB; full bf16 is roughly 360 GB/131
shards and must never be downloaded as a resident whole checkpoint.

Authority: the lead's November 5 rulings in this fix brief, RUN_STATE retention
at line 45, and item 170 / PR #662 (`lane/2026-11-05-runstate-170-align-pause`).
**Pilots 8 and 9 must not be auto-offloaded by `offload.py`.** Pilot 9 is
`/Users/edr/night-align/pilot-v8-20261105T102850Z`; its capture directories
`runs-parent/*/instrument_validation/*` stay on the Mac through block-5 release.
Pilot 8 may be considered only after a structure-only locator review finds
none subject to that rule; otherwise keep it and STOP for the lead's ruling.
Pilots 0–7 are already deleted/offloaded and cannot reclaim more source bytes.

Code references: port PR #664 `lane/2026-11-05-align-flashnext-port`, base
`origin/port/qwen4-exp-mlx`; gold harness PR #667
`lane/2026-11-05-align-flashnext-gold-parity` (pushed, per lead); R0 PR #661
`lane/2026-11-05-align-r0-desk`. Obtain reviewed full commit SHAs in the Mac's
checkout; moving branch tips and this clone's stale cached tips are not pins.
This document does not assert any of those PRs merged or any live gate passed.
No network or model download was performed while authoring it.

**Execution contract.** Save each numbered step's commands as a reviewed FILE,
`stepN.zsh`, then run `JW_OP=/exact/existing/operation zsh -f -euo pipefail stepN.zsh`.
Step 2 is the bootstrap and writes `$JW_OP/env.zsh`; every later script starts
by sourcing it. Run step 1 itself with `zsh -f -euo pipefail step1.zsh`.
Never paste a collection of guard commands into an interactive shell. A STOP
is a nonzero exit: keep sources and resolve it. `noclobber` intentionally
refuses existing outputs. Resume with the same env file and immutable receipts;
new phase/attempt output names require review. Never reset initialization to
get past an existing file. Step 8 is one Python program, independent of shell
error handling.

Blinding is a **path map**, not a directory-name filter: claim runs roots,
`withheld/**` and other registered paths can be restricted without the literal
name `restricted`. Agents never inventory, hash, read or print those real
manifests/paths. Only an authorized custody operator may perform opaque byte
copying/SHA-256 on approved roots, without parsing measurement values. The
helper's literal-name refusal is additional defense, not a complete exclusion
mechanism. Never run `scripts/run_b5_analysis.py`, harvest, a reducer, release
or recompute here. Never follow absolute paths from config text during review.

All GB below are decimal bytes. Every allocating operation needs admission
for its maximum additional bytes plus a **30,000,000,000-byte floor** on each
filesystem it writes. Step 5's continuous guard SIGSTOPs the writer process
group below that floor; preserve partials and source on failure. `df` available
bytes control admission; purgeable space, snapshots, summed `du`, APFS clone
sizes and promised evictions do not count as free space.

## 1. Identify the machine and measure the SSD, read-only

Save as `step1.zsh`; no agent sessions on the Mac before the STOP-2 handoff.

```zsh
setopt interactivecomments errexit nounset pipefail extendedglob noclobber
/usr/sbin/sysctl -n hw.model hw.memsize
/usr/sbin/system_profiler SPHardwareDataType SPNVMeDataType
/bin/df -k / /System/Volumes/Data
/usr/sbin/diskutil info /System/Volumes/Data
/usr/sbin/diskutil apfs list
/usr/bin/tmutil listlocalsnapshots /
```

**STOP 1:** Ed confirms the machine, container, Data volume and available bytes.
Below 30 GB, no staging; obtain a separate recovery plan without deleting KEEP.
Do not remove snapshots or treat marketed capacity as available capacity.

## 2. Prove the magistrate finished, then pause and disable re-arm

PR #662 must be integrated in the **Mac records checkout** first. Item 170
must say no auto-offload of pilots 8/9, no pilot 10, and the magistrate must
finish normal harvest, pin, `p9-PILOT.json` and desk custody, then write
`~/night-align/pilot-v8-20261105T102850Z/DESK_DONE`. An interactive Claude or
Codex session on the Mac could prevent that desk handoff: **do not start one**
until this gate completes. Do not stop/bootout a magistrate to force the gate.

Save this bootstrap as `step2.zsh`. Ed sets exact paths in this file before
review. `JW_RECORDS` is the current records checkout, not the old pinned
measurement clone. Set `JW_P9_PIN` and `JW_P9_PILOT` to the exact handoff
products supplied by the magistrate; their existence is checked without
opening measurement content. Choose one fixed operation path, once.

```zsh
setopt interactivecomments errexit nounset pipefail extendedglob noclobber
export JW_CANON=/Users/edr/code/JouleWise
export JW_MEAS=/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2
: "${JW_RECORDS:?Set exact current Mac records checkout}"
: "${JW_P9_PIN:?Set exact pilot-9 ledger-pin receipt path}"
: "${JW_P9_PILOT:?Set exact saved p9-PILOT.json path}"
: "${JW_OP:?Set one fixed NEW operation directory under night-archive}"
export JW_RECORDS JW_P9_PIN JW_P9_PILOT JW_OP
# No STOP creation, bootout or uninstall before this function passes.
jw_pause_check() {
  python3.13 -I -B - <<'PY'
import json, os, re, subprocess
from pathlib import Path
s = (Path(os.environ['JW_RECORDS']) / 'RUN_STATE.md').read_text()
assert re.search(r'^170\.', s, re.M), 'STOP: item 170 absent in Mac records'
# Ed also reviews its amended semantics: no pilot8/9 auto-offload or pilot10.
assert Path('/Users/edr/night-align/pilot-v8-20261105T102850Z/DESK_DONE').is_file(), 'STOP: no DESK_DONE'
assert Path(os.environ['JW_P9_PIN']).is_file(), 'STOP: missing pin receipt'
assert Path(os.environ['JW_P9_PILOT']).name == 'p9-PILOT.json'
assert Path(os.environ['JW_P9_PILOT']).is_file(), 'STOP: missing desk product'
lock = Path('/Users/edr/night-custody/magistrate/magistrate.lock')
if lock.exists():
    obj = json.loads(lock.read_text())
    assert obj.get('schema') == 'joulewise.magistrate_lock.v1'
    pid = obj['pid']
    assert type(pid) is int and pid > 1
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        pass
    else:
        raise SystemExit('STOP: lock owner PID still exists; wait for exit')
# Raw argv may contain credentials: inspect only in memory, never journal it.
ps = subprocess.run(['/bin/ps', '-axo', 'pid=,comm=,args='], check=True,
                    text=True, capture_output=True).stdout
pattern = re.compile(r'(?i)(?:^|[/\s])(?:codex|offload\.py|align_pilot_session(?:\.py)?|harvest(?:[\w.-]*)?|zstd|tar)(?:\s|$)|(?:^|[/\s])claude(?:\s|$).*?(?:\s)-(?:p|[^\s]*p)(?:\s|$)')
for row in ps.splitlines():
    pid, command = row.strip().split(None, 1)
    if pattern.search(command):
        raise SystemExit('STOP: writer/agent census busy; PID=' + pid)
print('STOP-2 pre-pause prerequisites PASS; no argv recorded')
PY
}
jw_pause_check
# Ed confirms no collection.active, armed plan or scheduled t0; all products sealed.
mkdir -m 700 "$JW_OP"
{
  print -r -- 'setopt interactivecomments errexit nounset pipefail extendedglob noclobber'
  for name in JW_CANON JW_MEAS JW_RECORDS JW_OP JW_P9_PIN JW_P9_PILOT; do
    printf 'export %s=%q\n' "$name" "${(P)name}"
  done
  functions jw_pause_check
  cat <<'ENV'
export JW_CLOUD='/Users/edr/Library/Mobile Documents/com~apple~CloudDocs'
export JW_REMOTE="$JW_CLOUD/JouleWise-archive/${JW_OP:t}"
jw_disk_check() {
  python3.13 -I -B - "${1:-0}" "${2:-/System/Volumes/Data}" <<'PY'
import os, sys
s = os.statvfs(sys.argv[2])
free = s.f_bavail * s.f_frsize
extra = int(sys.argv[1])
print('available_bytes', free, 'next_allocation_bytes', extra)
if extra < 0 or free < 30_000_000_000 + extra:
    raise SystemExit('STOP: disk floor or allocation budget')
PY
}
ENV
} > "$JW_OP/env.zsh"
source "$JW_OP/env.zsh"
jw_disk_check
/bin/df -k /System/Volumes/Data > "$JW_OP/df-before.txt"
/usr/sbin/diskutil apfs list > "$JW_OP/apfs-before.txt"
git -C "$JW_MEAS" status --short --branch > "$JW_OP/measurement-status.txt"
git -C "$JW_MEAS" rev-parse HEAD > "$JW_OP/measurement-head.txt"
/bin/launchctl list > "$JW_OP/launchd-before.txt"
/bin/launchctl print-disabled "gui/$(id -u)" > "$JW_OP/disabled-before.txt"
mkdir "$JW_OP/plists"
# Discover paths without following symlinked plists or printing their contents.
find /Users/edr/Library/LaunchAgents /Library/LaunchAgents /Library/LaunchDaemons \
  -maxdepth 1 \( -type f -o -type l \) -name '*.plist' -print
crontab -l
atq
```

`crontab -l` exits nonzero if no crontab exists; record that exact absence and
resume the reviewed script after it, not with a blanket `|| true`. Ed reviews
system launchers/cron/at locally. Never upload raw `ps`, `plutil -p`, crontab
commands, `launchctl print` or plist contents: they can contain credentials.
The journal gets only domain, label, original disabled/loaded state, PID and
executable **basename**, and redacted schedule facts. Keep raw plist backups
in the mode-700 local journal; **exclude plists and other raw credential
records from the cloud/independent journal export**. Ed reviews that export.

Account for every auto-reloader: night/deadman, `com.joulewise.magistrate`,
`com.joulewise.b6loop`, BYTES, scheduled probes and
`com.joulewise.quiet-kit` (`RUN_STATE.md:96`), system domains, cron and at.
Copy each exact reviewed plist with `cp -pP` before unloading; if it is a
symlink, also preserve its exact target and identity separately without
following arbitrary targets. Extract only Label/Program basename locally,
not EnvironmentVariables. Save system disabled states locally too. Preserve
`local.jwbench.keepawake`, its plist, AC settings, checkouts and venvs.

Save this continuation as `step2-pause.zsh`; review exact discovered jobs first.
The source of `JW_PLAN` is the current terminal-plan handoff, not an old date.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
: "${JW_PLAN:?Set exact TERMINAL night_plan.json from handoff}"
jw_pause_check
# Only now may the operation create STOP or boot out/uninstall anything.
test ! -e /Users/edr/night-custody/magistrate/STOP
printf '%s\n' "ALIGN paused for MBP offload and gold validation; $JW_OP" \
  > /Users/edr/night-custody/magistrate/STOP
cp -p /Users/edr/night-custody/magistrate/STOP "$JW_OP/our-STOP.txt"
"$JW_MEAS/scripts/install_night_agent.sh" --plan "$JW_PLAN" --uninstall
/bin/launchctl bootout "gui/$(id -u)/com.joulewise.magistrate"
/bin/launchctl disable "gui/$(id -u)/com.joulewise.magistrate"
# Repeat these two operations for each reviewed non-keepawake launcher.
: "${JW_JOB_TARGET:?Set discovered exact domain/label}"
/bin/launchctl bootout "$JW_JOB_TARGET"
/bin/launchctl disable "$JW_JOB_TARGET"
/bin/launchctl list > "$JW_OP/launchd-paused.txt"
# Assert no com.joulewise.* job is loaded in GUI OR system domain.
python3.13 -I -B - <<'PY'
import subprocess
for domain in ('gui', 'system'):
    argv = ['/bin/launchctl', 'list'] if domain == 'gui' else ['sudo', '/bin/launchctl', 'list']
    s = subprocess.run(argv, check=True, capture_output=True, text=True).stdout
    assert not any('com.joulewise.' in row for row in s.splitlines()), 'STOP: JouleWise job loaded'
print('JouleWise GUI/system jobs absent; keepawake preserved')
PY
jw_pause_check
jw_disk_check
```

If a job is already absent, document the specific absence and continue via a
reviewed revised script. A pre-existing STOP is never overwritten or removed.
Resume requires `cmp "$JW_OP/our-STOP.txt" .../STOP`, env/helper hash checks,
no active writer and reviewed disable-state receipts. Optional remote
`ops/stop*` control is lead-owned; this offline procedure does not push it.

**STOP 2:** Ed attests amended item 170 present, DESK_DONE/pin/p9-PILOT saved,
lock owner gone, no named agent/writer, no collection/armed t0, launchers
absent/disabled, external schedulers accounted for. This check precedes all
STOP/bootout actions; repeat on resume. Agents must exit before measurements.

## 3. Mechanical model KEEP census and pre-offload R0 inventories

Use the integrated Mac records/kit checkout containing the BYTES, B6, ALIGN
and R0 code. Before **any offload or archive**, prepare the reviewed R0 config
from PR #661's `docs/align/r0_desk.example.json`. Keep `disk_path` on the
**measurement internal volume**; the example's `/Volumes/ALIGN_MODELS` is not
appropriate for the measurement disk gate. Set all custody parents. Set
`offloads[].destination` to separate **uncompressed, non-symlink materialized
copies** on independent storage, not tar.zst or an HF snapshot of symlinks.
Pilot 9's source is retained even though R0's schema calls its copy an offload.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
: "${JW_R0_CODE:?Set reviewed integrated R0 checkout}"
: "${JW_R0_CONFIG:?Set reviewed config JSON INSIDE that checkout}"
: "${JW_P8_SOURCE:?Set exact pilot-8 root from handoff}"
export JW_R0_CODE JW_R0_CONFIG JW_P8_SOURCE
python3.13 -I -B "$JW_CANON/scripts/align_offload_model_keep.py" \
  --repo "$JW_R0_CODE" --r0-config "$JW_R0_CONFIG" \
  --output "$JW_OP/model-keep-provenance.json" > "$JW_OP/model-KEEP.txt"
cat "$JW_OP/model-KEEP.txt"
# --inventory only, not the R0 measurement/selection run. Run before any offload.
"$JW_R0_CODE/.venv/bin/python" -B "$JW_R0_CODE/scripts/align_r0_checks.py" \
  --config "$JW_R0_CONFIG" --inventory "$JW_P8_SOURCE" --output "$JW_OP/pilot8-r0-inventory.json"
"$JW_R0_CODE/.venv/bin/python" -B "$JW_R0_CODE/scripts/align_r0_checks.py" \
  --config "$JW_R0_CONFIG" --inventory /Users/edr/night-align/pilot-v8-20261105T102850Z \
  --output "$JW_OP/pilot9-r0-inventory.json"
jw_disk_check
```

The tracked helper reads repository text only and prints model paths without
following them: every config JSON (a superset of **every**
`configs/campaigns/*/registration/identity_pins.json` `model_source`), every
tracked roster file and the exact R0 config. It extracts model sources and
artifact roots/blob paths, and records input SHA-256s. This older authoring
checkout lacks integrated rosters; its census must refuse, not print a
plausible incomplete list. Ed compares every BYTES ten-model + 27B extension,
B6 §1.4 and ALIGN kit roster entry against the printed census, including any
prose-only roster not represented by config sources. Unresolved IDs/paths are
KEEP and STOP; do not infer a filesystem path from a model's display name.
Store R0 config/source variables in a new mode-600 `$JW_OP/r0-env.zsh` with
quoted `export` lines; later R0 scripts source it. No env overwrite on resume.

The printed census must include the NEG-8 Qwen2.5-1.5B-Instruct-4bit,
Qwen3-1.7B-4bit, Qwen3-8B-4bit, all BYTES roster models, Qwen3.8-27B-8bit,
all Qwen3-30B-A3B-4bit anchors and Qwen3-Next-80B-A3B-Thinking-4bit (R0 N).
Keep every pinned revision and its **blob bytes**, not just HF snapshot links.
For HF KEEP baselines use the kit's `model_artifact_inventory` or hash each
referenced blob with its resolved-path binding. A snapshot symlink manifest
alone does not authenticate weights; no shared HF cache cleanup here.

Structure-only candidate metadata comes from the authorized custody operator,
using the full restricted path map. No recursive `du -I restricted` is an
agent-safe inventory. For approved paths only, process even a final line
without newline with `while IFS= read -r root || [[ -n "$root" ]]; do ...; done`.
UNKNOWN is KEEP. A source listing alone does not prove absence from the ledger:
require a structure-only review of **all ledger locators** under that root,
without exposing values, bound to the source manifest/archive in step 8.

Candidate order: (1) verify/second-copy existing pilots 0–7 archives; they
reclaim zero deleted-source bytes; (2) pilot 8 only if no locator falls under
retention and all gates pass; (3) models outside **every** printed model KEEP
entry, every mandatory root and every sealed/live dependency. **Tier 3 is
empty under the present KEEP roots/known roster; budget zero reclaimed bytes
from it.** Do not use cache removal, calibration custody, B6/BYTES or personal
roots as a fallback. Pilot 9 is not a candidate in this pause.

**STOP 3:** R0 inventories for both pilots saved outside sources; materialized
copy destinations agreed and budgeted, full model KEEP printed and reviewed,
pilot 8's retention census ruled or root retained. R0 may refuse symlinks or
restricted content; retain sources and ask the lead rather than weakening it.
Do not run a live R0 desk session from an agent. Copies may be made under this
paused Ed-only procedure; full R0 remains its own lead-controlled gate.

## 4. KEEP roots and immutable custody

`RUN_STATE.md:45` capture retention stays in force until block-5 release,
including removed attempts and ALIGN capture directories. Pilot 9 stays
**entirely on the Mac**; no split-root deletion or locator rewrite. If pilot
8 has even one protected locator, keep it too and STOP for the lead's ruling.
B5 originals on both machines and the transfer/recompute dependencies are
KEEP; the analysis laptop is not spare scratch storage. A previous transfer
receipt does not prove coverage of an unrelated current root.

Before source deletion the complete `$JW_OP/KEEP.txt` must contain these exact
mandatory roots, **all must exist**, plus the printed model paths, operation
journal, active worktrees, venvs, ledgers, plan inputs, executable/plist targets
and every discovered sealed dependency. Ancestors and descendants overlap by
inode. Missing mandatory roots or unresolved KEEP entries are a refusal.

```text
/Users/edr/code/JouleWise
/Users/edr/night-custody
/Users/edr/night-b5
/Users/edr/night-g2a
/Users/edr/night-archive
/Users/edr/night-plan-staging
/Users/edr/night-b6
/Users/edr/night-bytes
/Users/edr/jw_models
/Users/edr/.cache/huggingface/hub
/Users/edr/Library/LaunchAgents
```

KEEP also includes calibration/acceptance/quarantine, raw streams and archived
attempts, night-plan-staging, control state, keepawake, and `.OFFLOADED.json`
pointers. Retain legacy mint/acceptance custody and R7's 17 raw captures;
D-188 engineering permission grants no deletion or unblinding. Preserve raw
bundles/run evidence unchanged. Approval of a broad offload plan is not
approval of any item's bytes. Step 7 adds independent copies of existing
single-copy archives; they remain protected after copying.

**STOP 4:** Ed/lead review exact candidates, KEEP and dependency/retention
coverage. Keep everything UNKNOWN. The external storage plan does not require
removing pilot 9 or taking bytes from protected roots. If the full ledger
locator review is unavailable, pilot 8 stays and no deletion proceeds.

## 5. Check quota, staging space and throughput for the selected roots only

Ed opens System Settings → Apple Account → iCloud → storage management and
records account, quota, used and remaining bytes, including other devices'
pending uploads. `df` on the iCloud folder measures local SSD capacity, **not
iCloud quota**. If quota is unknown/insufficient, STOP; Ed chooses another
approved cloud destination with equivalent full-byte verification. Never
publish blinded data or create a new integration as a convenience.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
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
source "${JW_OP:?Set existing operation}/env.zsh"
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

Use the reviewed stdlib program `scripts/align_offload_delete_root.py` for
opaque-byte inventories and deletion. Copy the reviewed bytes once; preserve
and check its digest at every resume. This helper refuses dataless files
before opening them, hardlinks, special files, nested filesystems, unsafe
members and literal blinded directory names. It does not implement the full
block-5 restricted path map: only the authorized custody operator may run it
on roots cleared by that map. Agents never read real blinded manifests.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
cp -p "$JW_CANON/scripts/align_offload_delete_root.py" "$JW_OP/manifest.py"
shasum -a 256 "$JW_OP/manifest.py" > "$JW_OP/manifest-helper.sha256"
```

Hashes do not preserve resource forks, ACLs, xattrs or sparse/hardlink topology.
Ed must establish those are unnecessary before using the tar flags below;
otherwise keep the root and obtain a reviewed metadata-preserving method.
Hardlinks are refused even when two file names hold identical bytes. The
BYTES helper de-duplicates by inode, so this may make an entire pilot ineligible;
do not split or silently discard links to get past the guard.

For each reviewed CLOSED leaf, fill variables from its inventory row. No
source may equal/contain/be contained by a KEEP entry; no ancestor root
deletion. Confirm no external symlink target is needed for restoration; archive
such targets separately or retain the source. An archived symlink is not a
copy of its target (especially HF blobs and `.venv`).

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
: "${JW_SRC:?Set one exact approved CLOSED leaf root}"
: "${JW_ID:?Set unique ledger ID using letters digits dash underscore only}"
[[ "$JW_ID" == [A-Za-z0-9_-]## ]]
export JW_SRC JW_ID
export JW_ITEM="$JW_OP/$JW_ID"
mkdir "$JW_ITEM"
python3.13 -I -B "$JW_OP/manifest.py" tree "$JW_SRC" > "$JW_ITEM/source.json"
shasum -a 256 "$JW_ITEM/source.json" > "$JW_ITEM/source.sha256"
printf '%s\n' "$JW_SRC" > "$JW_ITEM/source-path.txt"
test ! -e "$JW_REMOTE/$JW_ID.tar.zst"
export JW_ARCHIVE_BUDGET_BYTES="$(python3.13 -I -B "$JW_OP/manifest.py" budget "$JW_ITEM/source.json")"
jw_disk_check "$JW_ARCHIVE_BUDGET_BYTES"
COPYFILE_DISABLE=1 /usr/bin/tar --no-mac-metadata --no-xattrs -cf - \
  -C "$JW_SRC" . | zstd -T1 -3 -o "$JW_REMOTE/$JW_ID.tar.zst.partial"
mv "$JW_REMOTE/$JW_ID.tar.zst.partial" "$JW_REMOTE/$JW_ID.tar.zst"
zstd -dc "$JW_REMOTE/$JW_ID.tar.zst" | \
  python3.13 -I -B "$JW_OP/manifest.py" archive > "$JW_ITEM/cloud-local.json"
cmp "$JW_ITEM/source.json" "$JW_ITEM/cloud-local.json"
python3.13 -I -B "$JW_OP/manifest.py" tree "$JW_SRC" > "$JW_ITEM/source-after.json"
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
source "${JW_OP:?Set existing operation}/env.zsh"
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
  python3.13 -I -B "$JW_OP/manifest.py" archive > "$JW_ITEM/cloud-roundtrip.json"
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
source "${JW_OP:?Set existing operation}/env.zsh"
# Independent device, with the same pipefail and helper as step 6.
: "${JW_SECOND_ARCHIVE:?Set archive path on independent storage}"
: "${JW_SECOND_MANIFEST:?Set copied source manifest}"
: "${JW_SECOND_HELPER:?Set copied manifest.py}"
: "${JW_SECOND_RESTORE:?Set new empty non-synced restore directory}"
shasum -a 256 "$JW_SECOND_ARCHIVE"
# Manually compare with archive.sha256 whose digest was anchored on the MBP.
shasum -a 256 "$JW_SECOND_HELPER"
# Compare with manifest-helper.sha256 from the MBP journal too.
zstd -dc "$JW_SECOND_ARCHIVE" | python3.13 -I -B "$JW_SECOND_HELPER" archive \
  > "$JW_SECOND_ARCHIVE.members.json"
cmp "$JW_SECOND_MANIFEST" "$JW_SECOND_ARCHIVE.members.json"
mkdir -m 700 "$JW_SECOND_RESTORE"
zstd -dc "$JW_SECOND_ARCHIVE" | /usr/bin/tar -xpf - -C "$JW_SECOND_RESTORE"
python3.13 -I -B "$JW_SECOND_HELPER" tree "$JW_SECOND_RESTORE" \
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

Before approval, save `$JW_ITEM/retention-review.json` with exactly these
keys: `source` (exact source path), `manifest_sha256`, `archive_sha256`, and
`no_retained_ledger_locators: true`. The authorized custody operator supplies
this structure-only ruling from the locator census; agents do not open the
ledger. Both `independent-receipt.txt` and `ed-approval.txt` must contain the
exact source path, source-manifest SHA-256 **and archive SHA-256** for this
item. An unrelated receipt cannot authorize deletion.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
# Ed only; a single fail-closed program owns every check and the deletion.
shasum -a 256 -c "$JW_OP/manifest-helper.sha256"
python3.13 -I -B "$JW_OP/manifest.py" delete \
  --item "$JW_ITEM" --keep "$JW_OP/KEEP.txt" --remote "$JW_REMOTE" \
  --journal "$JW_OP/deletions.tsv"
jw_disk_check
```

The program reads `source-path.txt`; shell `JW_SRC` cannot redirect it. It
requires all mandatory KEEP entries to exist and compares device/inode identity
of the source and KEEP entries through their ancestors (including APFS case
aliases). Symlink ancestors, `..`, noncanonical spelling and whitespace refuse.
The only source classes are exact `pilot-v*-*` children of
`/Users/edr/night-align` or exact paths in the lead-reviewed
`$JW_OP/approved-models.txt`; KEEP still overrides that list. Pilot 9's
`pilot-v8-*` and every capture-bearing tree refuse. Model deletion under
`jw_models` or the shared HF cache is therefore unavailable in this pause.

All source/cloud/round-trip digests, both bound receipts, retention review,
file flags and ACLs must pass; `fileproviderctl evaluate` must freshly report
`isUploaded=1` for both cloud objects immediately before deletion. Any
preflight failure exits nonzero with **no deletion** and a
`REFUSED_NO_DELETE` TSV row. The program checks writable directories and
pre-stages the pointer before calling `shutil.rmtree`, then publishes
`$JW_SRC.OFFLOADED.json` and `DELETE_AUTHORIZED`/`DELETED` TSV rows. A later
OS/I/O failure can still cause partial removal: `FAILED_PARTIAL` is recorded,
and the `.pending` pointer retains recovery coordinates. STOP and resolve
against the original manifest; never report it as completed. This is not a
filesystem transaction and requires the proved no-writer pause throughout.
Keep local pointers, immutable manifests and receipts, and verify cloud plus
independent copies of the operation journal.

Explicitly evict only the verified uploaded tar after independent verification
to reclaim its local staging bytes; do not delete the cloud object:

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
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
source "${JW_OP:?Set existing operation}/env.zsh"
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
source "${JW_OP:?Set existing operation}/env.zsh"
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
source "${JW_OP:?Set existing operation}/env.zsh"
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
source "${JW_OP:?Set existing operation}/env.zsh"
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
source "${JW_OP:?Set existing operation}/env.zsh"
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
source "${JW_OP:?Set existing operation}/env.zsh"
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
source "${JW_OP:?Set existing operation}/env.zsh"
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
