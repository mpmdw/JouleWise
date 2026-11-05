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
# Kernel executable names only; never match or record arbitrary argv tokens.
subprocess.run(['python3.13', '-I', '-B',
                str(Path(os.environ['JW_CANON']) / 'scripts/align_offload_delete_root.py'),
                'census'], check=True)
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
jw_uploaded() {
  python3.13 -I -B "$JW_CANON/scripts/align_offload_delete_root.py" uploaded "$1"
}
jw_wait_dataless() {
  local file="$1" expected="$2" flags attempt
  for attempt in {1..240}; do
    flags="$(/usr/bin/stat -f %Sf "$file")"
    if [[ "$expected" == yes && "$flags" == *dataless* ]]; then return 0; fi
    if [[ "$expected" == no && "$flags" != *dataless* ]]; then return 0; fi
    jw_disk_check
    sleep 5
  done
  print -u2 -- 'STOP: expected dataless transition not observed'
  return 1
}
ENV
} > "$JW_OP/env.zsh"
shasum -a 256 "$JW_OP/env.zsh" > "$JW_OP/env.sha256"
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
Resume first checks `shasum -a 256 -c "$JW_OP/env.sha256"`; it also requires `cmp "$JW_OP/our-STOP.txt" .../STOP`, env/helper hash checks,
no active writer and reviewed disable-state receipts. Optional remote
`ops/stop*` control is lead-owned; this offline procedure does not push it.

**STOP 2:** Ed attests amended item 170 present, DESK_DONE/pin/p9-PILOT saved,
lock owner gone, no named agent/writer, no collection/armed t0, launchers
absent/disabled, external schedulers accounted for. This check precedes all
STOP/bootout actions; repeat on resume. Agents must exit before measurements.

After STOP 2, perform the Ed-only purchase/attach subsection **9a** before
step 3; it is a storage prerequisite, not permission to begin downloads.

## 3. Mechanical model KEEP census and pre-offload R0 inventories

Use one repository object store containing each reviewed ref; no merged
checkout is required. The model census reads only `git show <full-sha>:<path>`. Before **any offload or archive**, prepare the reviewed R0 config
from PR #661's `docs/align/r0_desk.example.json`. Keep `disk_path` on the
**measurement internal volume**; the example's `/Volumes/ALIGN_MODELS` is not
appropriate for the measurement disk gate. Set all custody parents. Set
`offloads[].destination` to separate **uncompressed, non-symlink materialized
copies** on independent storage, not tar.zst or an HF snapshot of symlinks.
Pilot 9's source is retained even though R0's schema calls its copy an offload.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
: "${JW_R0_CODE:?Set reviewed integrated R0 checkout}"
: "${JW_R0_CONFIG:?Set reviewed operational config JSON}"
: "${JW_ALIGN_V4_REF:?Set reviewed full ALIGN v4 kit SHA}"
: "${JW_AMENDMENT_REF:?Set reviewed full amendment-1 SHA}"
: "${JW_R0_V4_REF:?Set reviewed full v4 R0 SHA}"
: "${JW_R0_CONFIG_BLOB:?Set repository-relative v4 R0 config blob path}"
: "${JW_P8_SOURCE:?Set exact pilot-8 root from handoff}"
export JW_R0_CODE JW_R0_CONFIG JW_P8_SOURCE
python3.13 -I -B "$JW_CANON/scripts/align_offload_model_keep.py" \
  --repo "$JW_CANON" --main-ref origin/main \
  --bytes-ref c58282f87 --b6-ref dda456f98 \
  --align-ref "$JW_ALIGN_V4_REF" --amendment-ref "$JW_AMENDMENT_REF" \
  --r0-ref "$JW_R0_V4_REF" --r0-config "$JW_R0_CONFIG_BLOB" \
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

The helper resolves every role to a full commit SHA before listing inputs.
It reads every registration identity pin and roster across **main**, **BYTES
c58282f87**, **B6 dda456f98** (including its §1.4 roster), the **ALIGN v4 kit**,
**amendment 1** and the **v4 R0 config** from Git blobs. Every receipt records
role, ref, commit, path and content SHA-256, model sources/blob paths and model
identity aliases. No filesystem model path is followed. Symlink blobs, blinded
input components, missing roles/files and stale kits refuse; no ad-hoc merged
checkout is needed. Compare the operational R0 config to that pinned config;
changing sources requires a new reviewed config commit and census.

Amendment 1 must retain Qwen3.8-27B, the Qwen3-30B anchors and the
Qwen2.5-1.5B NEG-8 reference. All sources in older registration pins and BYTES/B6
rosters remain KEEP too, even if dropped from the next ALIGN window. A dropped
model is not automatically unreferenced. Prose-only identities enter the census
as aliases without inventing local paths. UNKNOWN is KEEP and STOP. Keep every
pinned revision and its blob bytes, not merely HF snapshot links. Save reviewed
refs/config variables in a new mode-600 `$JW_OP/r0-env.zsh` with quoted exports.
No env overwrite on resume.

This offline clone currently lacks the amendment-1 blob and v4 kit/config;
its stale refs must **refuse**. Obtain the reviewed objects through the lead's
normal integration process before an operator runs the census; no network or
live model census was performed while writing this fix.

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
pilot 8's retention census ruled or root retained. R0 must use both [coordination patches](r0_disk_gate_patch.md): pilot view
symlinks are recorded as exact target text without following them; model
inventories still require materialized files. Restricted content still refuses;
retain the source and ask the lead rather than weakening that boundary.
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

Run the operation **inside tmux plus caffeinate**: start `tmux new -s jw-offload`,
then keep `caffeinate -i -s` running in a separate tmux pane for the whole
operation. **Never close the Terminal.** Keep the Mac on reliable AC power.
This does not authorize starting a measurement or interacting with analysis.

The tracked `scripts/align_offload_disk_guard.py` runs each allocating writer
in a new session/process group, samples every filesystem supplied with
`--path` every **5 seconds**, and sends **SIGSTOP to the whole writer group**
if free bytes fall below 30 GB or the space check fails. Exit 75 is STOP; it
does not resume or discard partials. Ed records PGID/start identity locally,
resolves space and obtains review before any SIGCONT or new attempt. Writers
must stay in that group, foreground and wait for children (no daemonization,
`setsid` or detached jobs). It protects archive compression/copy/hydration,
HF/package downloads, conversion, backup and step 12, in addition to each
maximum-allocation admission check. Sampled checks cannot prevent sub-5-second
bursts; the admitted whole-operation byte ceiling funds those bursts.
SIGHUP, SIGTERM, SIGINT and SIGQUIT stop the group before the guard exits.
The guard's child supervisor owns the writer group and monitors a private
pipe: guard death (including SIGKILL) closes it and stops the group; a missing
heartbeat for more than 15 seconds also stops it. The actual writer is its
child and inherits no heartbeat descriptors. A stopped group is never resumed
automatically; restarting requires a new guarded attempt after review.

Save a writer's commands in a separate reviewed file (which also sources
env.zsh), then run it from a guarded step file:

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
: "${JW_WRITER_FILE:?Set reviewed foreground writer .zsh file}"
: "${JW_WRITER_VOLUME:?Set exact writable destination volume}"
: "${JW_WRITER_BUDGET:?Set computed/admitted maximum new bytes}"
jw_disk_check "$JW_WRITER_BUDGET" "$JW_WRITER_VOLUME"
python3.13 -I -B "$JW_CANON/scripts/align_offload_disk_guard.py" \
  --path /System/Volumes/Data --path "$JW_WRITER_VOLUME" -- \
  /bin/zsh -f -euo pipefail "$JW_WRITER_FILE"
```

All allocating fences below are **writer files run through this wrapper**.
When hydration may continue after `brctl` returns, its writer file stays alive
through `jw_wait_dataless ... no` and the full hash check. The HF harness must
keep every worker in the guarded group. Persist its actual CLI/PGID receipt.
Watch both internal storage and the external destination; they share a budget
only if `stat` proves the same filesystem. On remount/unmount STOP and recheck
volume identity, never write into a bare mountpoint on the internal SSD.

Ed opens System Settings → Apple Account → iCloud → storage management and
records account, quota, used and remaining bytes, including other devices'
pending uploads. `df` on the iCloud folder measures local SSD capacity, **not
iCloud quota**. If quota is unknown/insufficient, STOP; Ed chooses another
approved cloud destination with equivalent full-byte verification. Never
publish blinded data or create a new integration as a convenience.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
/usr/bin/brctl status com.apple.CloudDocs > "$JW_OP/icloud-before.txt"
# New operation namespace under the established JouleWise-archive namespace.
mkdir -p "$JW_REMOTE"
# Synthetic 256 MiB probe; contains no study data. Keep until operation closes.
jw_disk_check 536870912  # Probe plus its local cloud-folder copy.
dd if=/dev/urandom of="$JW_OP/upload-probe.bin" bs=1048576 count=256
shasum -a 256 "$JW_OP/upload-probe.bin" > "$JW_OP/upload-probe.sha256"
date -u +%FT%TZ > "$JW_OP/upload-start.utc"
cp -p "$JW_OP/upload-probe.bin" "$JW_REMOTE/upload-probe.bin"
/usr/bin/fileproviderctl evaluate "$JW_REMOTE/upload-probe.bin" \
  > "$JW_OP/fileprovider-evaluate-step5.txt" \
  2> "$JW_OP/fileprovider-evaluate-step5.stderr.txt"
shasum -a 256 "$JW_OP/fileprovider-evaluate-step5.txt"
/usr/bin/brctl status com.apple.CloudDocs
```

**STOP 5 parser pin:** capture a real successful `fileproviderctl evaluate`
sample for this synthetic probe, its SHA-256, stderr, macOS/tool version and
reviewed field meanings. Keep successive pending/error samples at unique names.
The shipped parser is intentionally **unpinned and always refuses**. The lead
must review this real sample and commit the exact grammar, known keys and
sample digest before cloud eviction or deletion can proceed. Do not install a
synthetic sample, accept a substring, or pass an operator override. Unknown
keys/formats, `isUploading=1`, any `uploadingError`, and
`hasUnresolvedConflicts=1` must refuse even alongside `isUploaded=1`.
A changed macOS format needs another reviewed pin. No live sample was available
in this blind offline fix session.

After that reviewed parser is installed, require its successful check on the
exact file, record end UTC and elapsed seconds including upload delay, then
use explicit eviction and re-download to confirm the remote round trip.
Unavailable or ambiguous tool output is STOP; a local checksum or progress
bar cannot substitute for upload-state confirmation.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
date -u +%FT%TZ > "$JW_OP/upload-end.utc"
jw_uploaded "$JW_REMOTE/upload-probe.bin"
/usr/bin/brctl evict "$JW_REMOTE/upload-probe.bin"
jw_wait_dataless "$JW_REMOTE/upload-probe.bin" yes
jw_disk_check 268435456
/usr/bin/brctl download "$JW_REMOTE/upload-probe.bin"
jw_wait_dataless "$JW_REMOTE/upload-probe.bin" no
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
: "${JW_OFFLOAD_CODE_COMMIT:?Set reviewed full runbook/tooling commit}"
git -C "$JW_CANON" cat-file -e "$JW_OFFLOAD_CODE_COMMIT^{commit}"
git -C "$JW_CANON" show "${JW_OFFLOAD_CODE_COMMIT}:scripts/align_offload_delete_root.py" \
  > "$JW_OP/align_offload_delete_root.py"
shasum -a 256 "$JW_OP/align_offload_delete_root.py" > "$JW_OP/manifest-helper.sha256"
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
{
  for name in JW_SRC JW_ID JW_ITEM; do
    printf 'export %s=%q\n' "$name" "${(P)name}"
  done
} > "$JW_ITEM/item-env.zsh"
python3.13 -I -B "$JW_OP/align_offload_delete_root.py" tree "$JW_SRC" > "$JW_ITEM/source.json"
shasum -a 256 "$JW_ITEM/source.json" > "$JW_ITEM/source.sha256"
printf '%s\n' "$JW_SRC" > "$JW_ITEM/source-path.txt"
```

The first file only inventories/hashes and writes control receipts; admit its
bounded manifest/journal allocation. Once source.json exists, compute the
archive budget from it, then run the packaging file below through the guard.
Do not type an archive size by hand. Resume uses this same item-env and checks
the existing source.sha256; do not recreate/overwrite the source inventory.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
source "${JW_ITEM:?Set exact item}/item-env.zsh"
shasum -a 256 -c "$JW_OP/manifest-helper.sha256" "$JW_ITEM/source.sha256"
test ! -e "$JW_REMOTE/$JW_ID.tar.zst"
export JW_ARCHIVE_BUDGET_BYTES="$(python3.13 -I -B "$JW_OP/align_offload_delete_root.py" budget "$JW_ITEM/source.json")"
jw_disk_check "$JW_ARCHIVE_BUDGET_BYTES"
COPYFILE_DISABLE=1 /usr/bin/tar --no-mac-metadata --no-xattrs -cf - \
  -C "$JW_SRC" . | zstd -T1 -3 -o "$JW_REMOTE/$JW_ID.tar.zst.partial"
mv "$JW_REMOTE/$JW_ID.tar.zst.partial" "$JW_REMOTE/$JW_ID.tar.zst"
zstd -dc "$JW_REMOTE/$JW_ID.tar.zst" | \
  python3.13 -I -B "$JW_OP/align_offload_delete_root.py" archive > "$JW_ITEM/cloud-local.json"
cmp "$JW_ITEM/source.json" "$JW_ITEM/cloud-local.json"
python3.13 -I -B "$JW_OP/align_offload_delete_root.py" tree "$JW_SRC" > "$JW_ITEM/source-after.json"
cmp "$JW_ITEM/source.json" "$JW_ITEM/source-after.json"
shasum -a 256 "$JW_REMOTE/$JW_ID.tar.zst" > "$JW_ITEM/archive.sha256"
cp -p "$JW_ITEM/source.json" "$JW_REMOTE/$JW_ID.manifest.json"
export JW_MANIFEST_SHA="$(cut -d ' ' -f1 "$JW_ITEM/source.sha256")"
printf '%s  %s\n' "$JW_MANIFEST_SHA" "$JW_REMOTE/$JW_ID.manifest.json" \
  > "$JW_ITEM/cloud-manifest.sha256"
shasum -a 256 -c "$JW_ITEM/cloud-manifest.sha256"
jw_disk_check
```

Step 2 enables `extendedglob` for the zsh ID pattern above. Use one compression
worker to limit non-measurement load. A partial archive is not verified; on
interruption keep the source and use a new ID. **Ed only** may retire the exact
failed partial after recording failure and checking its path; no glob removal:

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
source "${JW_ITEM:?Set exact item directory}/item-env.zsh"
: "${JW_RETIRED_ID:?Set unique reviewed retired ID}"
[[ "$JW_RETIRED_ID" == [A-Za-z0-9_-]## ]]
test -f "$JW_REMOTE/$JW_ID.tar.zst.partial"
test ! -L "$JW_REMOTE/$JW_ID.tar.zst.partial"
test ! -e "$JW_REMOTE/$JW_RETIRED_ID.retired.partial"
mv -n "$JW_REMOTE/$JW_ID.tar.zst.partial" "$JW_REMOTE/$JW_RETIRED_ID.retired.partial"
```

Retiring preserves bytes and uses no delete authority. Budget that retained
partial until Ed separately approves its exact removal. Do not overwrite an earlier receipt.
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
For any eligible evidence root, authenticate coverage against its existing
custody records as well; a new manifest cannot prove a pre-existing omission.
B5 originals and calibration capture roots are ineligible in this pause.

Wait for **both archive and manifest** to report uploaded; save per-file state
and aggregate queue state (the transfer precedent is
`docs/process_traces/2026-10-28-magistrate-39206674/RECORD.md:88`).

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
source "${JW_ITEM:?Set exact item}/item-env.zsh"
jw_uploaded "$JW_REMOTE/$JW_ID.tar.zst"
jw_uploaded "$JW_REMOTE/$JW_ID.manifest.json"
/usr/bin/brctl status com.apple.CloudDocs
# Execute ONLY after confirmed server upload; sources remain intact.
/usr/bin/brctl evict "$JW_REMOTE/$JW_ID.tar.zst"
/usr/bin/brctl evict "$JW_REMOTE/$JW_ID.manifest.json"
jw_wait_dataless "$JW_REMOTE/$JW_ID.tar.zst" yes
jw_wait_dataless "$JW_REMOTE/$JW_ID.manifest.json" yes
# Budget the bytes still to hydrate; wait for eviction before admission.
export JW_ARCHIVE_BUDGET_BYTES="$(python3.13 -I -B "$JW_OP/align_offload_delete_root.py" budget "$JW_ITEM/source.json")"
jw_disk_check "$JW_ARCHIVE_BUDGET_BYTES"
/usr/bin/brctl download "$JW_REMOTE/$JW_ID.tar.zst"
/usr/bin/brctl download "$JW_REMOTE/$JW_ID.manifest.json"
jw_wait_dataless "$JW_REMOTE/$JW_ID.tar.zst" no
jw_wait_dataless "$JW_REMOTE/$JW_ID.manifest.json" no
shasum -a 256 -c "$JW_ITEM/cloud-manifest.sha256"
cmp "$JW_ITEM/source.json" "$JW_REMOTE/$JW_ID.manifest.json"
shasum -a 256 -c "$JW_ITEM/archive.sha256"
zstd -dc "$JW_REMOTE/$JW_ID.tar.zst" | \
  python3.13 -I -B "$JW_OP/align_offload_delete_root.py" archive > "$JW_ITEM/cloud-roundtrip.json"
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

On an attached independent volume, the MBP can verify/copy under its guarded
writer. On another host, Ed first copies the reviewed step files and writes a
host-specific `$JW_OP/env.zsh` with the same shell options, equivalent local
disk guard and only approved local paths (never use the MBP absolute paths).
No remote execution from this agent. Ed fills these variables with approved new
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
# Use EXPECTED hashes authenticated from the original MBP journal (not new local hashes).
: "${JW_ARCHIVE_SHA:?Set original archive SHA256}"
: "${JW_MANIFEST_SHA:?Set original source-manifest SHA256}"
: "${JW_HELPER_SHA:?Set original helper SHA256}"
printf '%s  %s\n' "$JW_ARCHIVE_SHA" "$JW_SECOND_ARCHIVE" \
  "$JW_MANIFEST_SHA" "$JW_SECOND_MANIFEST" "$JW_HELPER_SHA" "$JW_SECOND_HELPER" \
  > "$JW_SECOND_ARCHIVE.expected.sha256"
shasum -a 256 -c "$JW_SECOND_ARCHIVE.expected.sha256"
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

### 7a. Copy existing single-copy archives while the device is attached

This is required even if **no source deletion** is eligible. Ed supplies an
exact path inventory from the existing records for: ALIGN pilots **0–7**
under `JouleWise-archive/2026-11-04-align-pilots`, BYTES **H/H2 raw tars**
(`RUN_STATE.md:1239`), and R7 captures **A343, P0, READY** (the three iCloud-only
captures of R7's 17-capture second-copy obligation). No wildcard hydration.
For each exact archive, copy its authenticated original manifest, original
archive digest and original verifier to the separate non-synced device. Use
its original format/verifier if it predates this helper; no replacement trust
anchor made from a freshly copied corrupt file. Missing original digest or
coverage is STOP for the lead, not an invented success.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
: "${JW_EXISTING_ARCHIVE:?Set one exact existing iCloud archive}"
: "${JW_EXISTING_MANIFEST:?Set its authenticated existing manifest}"
: "${JW_EXISTING_COPY:?Set new item directory on independent device}"
: "${JW_EXISTING_BUDGET:?Set archive hydration plus destination restore budget}"
jw_disk_check "$JW_EXISTING_BUDGET"
jw_uploaded "$JW_EXISTING_ARCHIVE"
jw_uploaded "$JW_EXISTING_MANIFEST"
/usr/bin/brctl download "$JW_EXISTING_ARCHIVE"
/usr/bin/brctl download "$JW_EXISTING_MANIFEST"
jw_wait_dataless "$JW_EXISTING_ARCHIVE" no
jw_wait_dataless "$JW_EXISTING_MANIFEST" no
mkdir -m 700 "$JW_EXISTING_COPY"
cp -p "$JW_EXISTING_ARCHIVE" "$JW_EXISTING_COPY/"
cp -p "$JW_EXISTING_MANIFEST" "$JW_EXISTING_COPY/"
# Continue with the original hash receipts and full member/restore verification
# of step 7, using expected checksums rebound to these destination filenames.
```

Run each as a guarded writer checking BOTH volumes; include destination full
restore bytes in admission, not just compressed archive length. Verify both
archive and manifest with `shasum -a 256 -c`, restore to an empty directory,
re-hash all restored bytes, and save an attributed per-item receipt with both
SHA-256s and device identity. A checklist requires one verified row per pilot,
H/H2 tar and R7 capture; report missing rows as BLOCKED. Only then explicitly
evict its uploaded cloud staging copy and **poll dataless**. Sources and
cloud objects are never deleted by this backup step.

### 7b. Materialized R0 copies without moving retained sources

Use the pre-offload R0 inventories from step 3. Copy **both** pilots into the
configured independent-device destinations as uncompressed directories. R0's
inventory records pilot `measurement/` view links as symlinks with their exact
target text. Preserve those links without dereferencing; never copy target
contents through them. Model inventories remain strict and refuse links. The
copy and a full re-inventory must fit the device budget alongside archives,
restore workspace and gold storage if sharing the device.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
source "$JW_OP/r0-env.zsh"
: "${JW_R0_SOURCE:?Set exact source for this pilot}"
: "${JW_R0_DEST:?Set configured NEW materialized destination}"
: "${JW_R0_EXPECTED:?Set its original pre-offload R0 inventory JSON}"
: "${JW_R0_ACTUAL:?Set NEW comparison receipt path}"
test ! -e "$JW_R0_DEST"
mkdir -m 700 "$JW_R0_DEST"
cp -pRP "$JW_R0_SOURCE/." "$JW_R0_DEST/"
"$JW_R0_CODE/.venv/bin/python" -B "$JW_R0_CODE/scripts/align_r0_checks.py" \
  --config "$JW_R0_CONFIG" --inventory "$JW_R0_DEST" --output "$JW_R0_ACTUAL"
cmp "$JW_R0_EXPECTED" "$JW_R0_ACTUAL"
```

Save as a guarded writer. Reconfirm config `offloads` labels are `pilot8` and
`pilot9`, their inventory filenames are those exact step-3 receipts and their
destinations are these verified directories. tar.zst cannot satisfy R0.
If source content changed since the frozen inventory, STOP and retain it.
Pilot 9's Mac source stays intact regardless of a passing external copy.

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
source "${JW_ITEM:?Set exact item}/item-env.zsh"
# Ed only; a single fail-closed program owns every check and the deletion.
shasum -a 256 -c "$JW_OP/manifest-helper.sha256"
python3.13 -I -B "$JW_OP/align_offload_delete_root.py" delete \
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
file flags and ACLs must pass. The program also checks this operation's exact
STOP, current writer/agent census and 30 GB journal-filesystem floor; `fileproviderctl evaluate` must freshly report
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
source "${JW_ITEM:?Set exact item}/item-env.zsh"
jw_uploaded "$JW_REMOTE/$JW_ID.tar.zst"
/usr/bin/brctl evict "$JW_REMOTE/$JW_ID.tar.zst"
jw_wait_dataless "$JW_REMOTE/$JW_ID.tar.zst" yes
/bin/df -k /System/Volumes/Data > "$JW_OP/df-current.txt"
```

**STOP 8:** record actual available bytes and `(available_after -
available_before) * 1024` from `df -k`. Delete only the already-approved,
eligible leaf. Stop once the combined step-9 budget is met; **150 GB internal
is not reachable from the present eligible set**. Never remove snapshots,
retained pilot 9 or KEEP to force a disk gate. If pilot 8 is ineligible or
clones reclaim less than estimated, keep it and report the shortfall.

## 9. Combined internal/external budget and primary external-SSD plan

### 9a. Ed-only purchase/attach gate (after STOP 2, before step 3 copies)

Ed purchases or attaches a **1–2 TB external NVMe SSD**, Thunderbolt/USB4,
APFS. Ed alone chooses/formats a device in Disk Utility after verifying its
identity and preserving existing contents. No formatting command is supplied.
Exclude the volume in **Spotlight Privacy** and Time Machine; verify exclusions
before writing. Prefer another device for independent durable custody backups,
so a failed gold scratch drive does not take the backup with it. A copy on the
same external device as another copy is not a second independent backup.
A verified external copy is independent of the Mac's internal SSD and iCloud.
Budget all uses if a single external device supplies that independent copy.

Save this as an Ed-reviewed writer file, run via step 5's guard with both
internal and external volumes (at this point only small control writes).
Choose one fixed mount and operation location, not a new date on resume.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
: "${JW_EXTERNAL:?Set actual attached APFS mount under /Volumes}"
: "${JW_EXTERNAL_UUID:?Set verified Volume UUID from diskutil info}"
export JW_EXTERNAL JW_EXTERNAL_UUID
jw_external_check() {
  python3.13 -I -B - <<'PY'
import os, plistlib, subprocess
from pathlib import Path
p = Path(os.environ['JW_EXTERNAL'])
assert p.parent == Path('/Volumes') and not p.is_symlink()
s = subprocess.run(['/usr/sbin/diskutil', 'info', '-plist', str(p)],
                   check=True, capture_output=True).stdout
d = plistlib.loads(s)
assert d['VolumeUUID'] == os.environ['JW_EXTERNAL_UUID']
assert d['FilesystemType'].casefold() == 'apfs' and d['MountPoint'] == str(p)
assert os.stat(p).st_dev != os.stat('/System/Volumes/Data').st_dev
print('external volume identity PASS')
PY
}
jw_external_check
sudo /usr/bin/tmutil addexclusion -p "$JW_EXTERNAL"
/usr/bin/tmutil isexcluded "$JW_EXTERNAL"
# Ed verifies this exact volume in Spotlight Privacy; no fake measurement proof.
export JW_GOLD="$JW_EXTERNAL/flashnext-gold-20261105.noindex"
export JW_GOLD_CODE=/Users/edr/code/JouleWise-flashnext-gold-20261105
{
  for name in JW_EXTERNAL JW_EXTERNAL_UUID JW_GOLD JW_GOLD_CODE; do
    printf 'export %s=%q\n' "$name" "${(P)name}"
  done
  functions jw_external_check
} > "$JW_OP/external-env.zsh"
shasum -a 256 "$JW_OP/external-env.zsh" > "$JW_OP/external-env.sha256"
jw_disk_check 0 "$JW_EXTERNAL"
```

On resume source the existing external-env file, check its digest and call
`jw_external_check`; never rewrite it because a mount path changed. Call it
before **every** external writer. The guard monitors both filesystems; a
missing volume/changed device is STOP, not permission to write into an empty
mountpoint on the internal SSD.

External paging changes throughput, latency, USB/Thunderbolt traffic and power.
Measure sequential read/write and real page-fault behavior on **synthetic or
model bytes**, outside a measurement window; record link, enclosure, firmware,
filesystem, thermal throttling, throughput and n-gram paging policy. The n-gram
table is paged from this external SSD; do not silently copy it internally.
A bus-powered enclosure contributes to the laptop/wall boundary differently
from a separately powered enclosure; the measurement lead must freeze and
document that boundary and the attached hardware for future energy comparisons.
Gold parity/setup performance is not energy evidence. Revalidate no-swap memory,
quiet-state and the measurement boundary before ALIGN; no measurement with
backup, indexing, downloads or agents active. If an external-paging protocol
change needs a ruling, keep the pause and ask the lead.

### 9b. Honest reachable space and one combined admission

The planning estimate after pilot 9 is **about 66 GB internal available**, plus
**about 26 GB for pilot 8 only if eligible**, or **about 92 GB**. This is not a
promise: pilot 9 is retained, clone sharing reduces reclamation, and pilot 8
may also stay. Record actual `df` before/after each allowed deletion. Pilots
0–7 reclaim zero deleted-source bytes and tier 3 is empty. No extra 26 GB is
credited for pilot 9. Without a measured 80 GB internal free, R0's disk gate
still fails even when models are external; retain sources and STOP for the
lead's storage/r0 ruling. External space cannot be substituted for that gate.

Internal SSD alone **CANNOT** fund the roughly **120 GB streaming peak + 30 GB
floor = 150 GB**, or keep the **95 GB converted model + 41.2 GB next ALIGN
window + 30 GB floor = 166.2 GB**. The older 150 GB offload target is unreachable
from this eligible set. Conversion on the internal SSD is not admitted.
`JW_GOLD` and converted weights remain external after gold; no later internal
copy is implied by reaching a checkpoint.

Use this single budget before packaging, hydration, copying, setup and every
gold unit. Fill **all** remaining allocations, and repeat after metadata pins,
retries and materialized R0 copies. Count allocations already reflected in
current `df` once, not again as future bytes. Use maximum **simultaneous** use.

| Filesystem / stage | Remaining new bytes to fund, in addition to current resident bytes |
|---|---|
| Internal, per offload | One archive upper bound from `source.json`, cloud hydration, probe copies and small journal/control writes. Keep source resident until step 8 passes. Retained pilot 9 and all KEEP weights remain. |
| Internal, future selection/measurement | After present weights/copies: R0 requires **amendment-1 window-1 bundle bytes for two copies + 30 GB** on the internal measurement `disk_path`. Pin the plan/config citation and actual bytes; there is no flat 80 GB gate. Next ALIGN separately admits its reviewed allocation plus the floor. Use the larger bound for simultaneous needs; see [R0 patch series](r0_disk_gate_patch.md). |
| External, R0 | Both uncompressed pilot 8/9 materialized copies, matching the pre-offload inventories; complete non-symlink N/D model mirrors if not already present (**44.86 GB N**, about **28 GB D** are estimates). Do not count a compressed tar or HF symlinks as a mirror. Keep inventories/config/results outside sources. |
| External, durable custody | Existing ALIGN 0–7, H/H2, R7 archive/manifest copies, newly eligible archives, plus **largest complete restore workspace**. If this is gold's device, all copies compete in the same budget and remain resident. Otherwise budget/check the backup device separately. |
| External, streaming gold | Remaining converted output up to **95 GB**, maximum simultaneous bounded bf16/download/temp unit initially **15 GB**, and remaining env/cache/metadata/activation/journal overhead initially **10 GB**, plus **30 GB floor**. Replace estimates with the actual frozen schedule; incomplete downloads, output temp/atomic overlap, caches and re-downloads count. |
| Whole operation | Every filesystem passes its own current-free ≥ remaining simultaneous allocations + required floor; the amendment-1 R0 two-copy-plus-floor gate and future ALIGN gate also pass before those stages. Do not add free bytes across disks to satisfy any single-filesystem constraint. |

Layer 0's roughly 24-shard union and layer 1's roughly 35-shard/100 GB bf16
n-gram table need bounded subunits, not entire unions staged simultaneously.
Layers 2–47 are expected at about 3 shards/7 GB each. A 15 GB unit allowance
is valid only after review includes source shard verification, conversion temp
files, partials, shared-shard consumers and activation checkpoints. The exact
step-11 `weight_map` schedule controls final weight admission. No full 360 GB
snapshot or duplicate shared HF cache is admitted on either SSD.

**STOP 9:** Ed records volume identities, available bytes and every remaining
allocation in one budget receipt. External capacity/throughput/exclusions and
internal future-window budget must pass. Retention overrides capacity; if no
plan can pass R0/ALIGN internal headroom, STOP for the lead. Do not bypass R0,
quiet-machine or model/energy review by relabeling the external disk.

## 10. Isolated external storage, caches and venvs

Run new initialization only once; on resume verify existing environment locks,
wheel hashes and the saved env file rather than rerunning package resolution.
`mkdir`/noclobber refusals are deliberate. Use a new reviewed attempt filename
for each additional receipt. No writes, `delete-cache` or cleanup under
`~/.cache/huggingface/hub`, which holds anchor bytes. `HF_HOME`, `HF_HUB_CACHE`
and `HF_XET_CACHE` all live in `JW_GOLD`. Disable xet transport/chunk cache;
cap any other cache in the per-unit byte budget. The harness must refuse a
cache path outside these pinned locations.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
source "$JW_OP/external-env.zsh"
shasum -a 256 -c "$JW_OP/external-env.sha256"
jw_external_check
: "${JW_SETUP_BUDGET_BYTES:?Set reviewed new setup/cache/temp byte ceiling}"
jw_disk_check "$JW_SETUP_BUDGET_BYTES" "$JW_EXTERNAL"
mkdir -m 700 "$JW_GOLD"
touch "$JW_GOLD/.metadata_never_index"
mkdir "$JW_GOLD/envs" "$JW_GOLD/results" "$JW_GOLD/converted" \
  "$JW_GOLD/metadata" "$JW_GOLD/working" "$JW_GOLD/activations" \
  "$JW_GOLD/hf" "$JW_GOLD/pip-cache" "$JW_GOLD/tmp"
{
  cat <<'CACHE'
export HF_HOME="$JW_GOLD/hf"
export HF_HUB_CACHE="$JW_GOLD/hf/hub"
export HF_XET_CACHE="$JW_GOLD/hf/xet"
export HF_HUB_DISABLE_XET=1
export HF_XET_CHUNK_CACHE_SIZE_BYTES=0
export PIP_CACHE_DIR="$JW_GOLD/pip-cache"
export TMPDIR="$JW_GOLD/tmp"
export JW_METADATA="$JW_GOLD/metadata"
export JW_CHECKPOINT="$JW_GOLD/working"
CACHE
} > "$JW_OP/gold-env.zsh"
source "$JW_OP/gold-env.zsh"
shasum -a 256 "$JW_OP/gold-env.zsh" > "$JW_OP/gold-env.sha256"
python3.13 -I -m venv "$JW_GOLD/envs/mlx"
python3.13 -I -m venv "$JW_GOLD/envs/reference"
"$JW_GOLD/envs/mlx/bin/python" -I -m pip install 'mlx==0.31.2' 'mlx-lm==0.31.3'
: "${JW_TORCH_VERSION:?Set harness-reviewed exact torch version}"
"$JW_GOLD/envs/reference/bin/python" -I -m pip install \
  "torch==$JW_TORCH_VERSION" 'transformers==5.22.1' safetensors huggingface_hub
"$JW_GOLD/envs/mlx/bin/python" -I -m pip freeze --all > "$JW_OP/mlx.freeze.txt"
"$JW_GOLD/envs/reference/bin/python" -I -m pip freeze --all > "$JW_OP/reference.freeze.txt"
"$JW_GOLD/envs/mlx/bin/python" -I -m pip check
"$JW_GOLD/envs/reference/bin/python" -I -m pip check
jw_disk_check 0 "$JW_EXTERNAL"
jw_disk_check
```

**STOP 10:** mlx 0.31.2 / mlx-lm 0.31.3, transformers 5.22.1 and the
harness-approved torch pin verified from version locks; preserve wheel digests.
Do not install `[mac]` into the reference venv or upgrade the measurement venv
(main's transformers constraint differs). Confirm external Spotlight/Time
Machine exclusions. On every step-11/12 restart source env, external-env and
gold-env, check their hashes and volume identity, compare the frozen pins,
then resume only from a fully authenticated durable checkpoint.

## 11. Pin the official revision and metadata; plan layer-group streaming

No official checkpoint commit was available in the supplied offline records.
Ed/lead must resolve and approve one **full immutable commit SHA**, recorded
below. Never run parity against `main`, `latest`, community PR #1788, or a
community quantization. Network commands in this section are for the paused
measurement MBP only; none were run while authoring this document.

First resolve metadata without downloading weights:

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
source "$JW_OP/external-env.zsh"
source "$JW_OP/gold-env.zsh"
shasum -a 256 -c "$JW_OP/external-env.sha256" "$JW_OP/gold-env.sha256"
jw_external_check
test ! -e "$JW_OP/hf-pinned.json"
test ! -e "$JW_OP/hf-proposed.json"
export JW_HF_REPO=Qwen/Qwen3.8-Flash-Next
"$JW_GOLD/envs/reference/bin/python" -I -B - <<'PY'
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
with Path(os.environ['JW_OP'], 'hf-proposed.json').open('x') as f:
    f.write(json.dumps(out, indent=2)+'\n')
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
source "$JW_OP/external-env.zsh"
source "$JW_OP/gold-env.zsh"
shasum -a 256 -c "$JW_OP/external-env.sha256" "$JW_OP/gold-env.sha256"
jw_external_check
test ! -e "$JW_OP/hf-pinned.json"
cp -p "$JW_OP/hf-proposed.json" "$JW_OP/hf-pinned.json"
test ! -e "$JW_OP/hf-metadata-verified.json"
test ! -e "$JW_OP/hf-receipts.sha256"
export JW_HF_REPO=Qwen/Qwen3.8-Flash-Next
export JW_HF_REV="$("$JW_GOLD/envs/reference/bin/python" -I -c \
  'import json,os; print(json.load(open(os.environ["JW_OP"]+"/hf-pinned.json"))["revision"])')"
{
  printf 'export JW_HF_REPO=%q\n' "$JW_HF_REPO"
  printf 'export JW_HF_REV=%q\n' "$JW_HF_REV"
} > "$JW_OP/hf-env.zsh"
"$JW_GOLD/envs/reference/bin/python" -I -B - <<'PY'
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
    s = os.statvfs(os.environ['JW_GOLD'])
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
with Path(os.environ['JW_OP'], 'hf-metadata-verified.json').open('x') as f:
    f.write(json.dumps(dict(repo=p['repo'], revision=p['revision'], files=checks,
                           expected_shards=shards), indent=2)+'\n')
print('VERIFIED metadata; expected weight shards', len(shards), '; weights not downloaded')
PY
"$JW_GOLD/envs/reference/bin/python" -I -B - <<'PYHF'
import hashlib, json, os
from pathlib import Path
op = Path(os.environ['JW_OP'])
verified = json.loads((op / 'hf-metadata-verified.json').read_text())
with (op / 'hf-receipts.sha256').open('x') as f:
    for name in ('hf-pinned.json', 'hf-metadata-verified.json', 'hf-env.zsh'):
        p = op / name
        f.write(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + str(p) + '\n')
    for row in verified['files']:
        f.write(row['sha256'] + '  ' + str(Path(os.environ['JW_METADATA']) / row['path']) + '\n')
PYHF
shasum -a 256 -c "$JW_OP/hf-receipts.sha256"
/bin/df -k /System/Volumes/Data
jw_disk_check 0 "$JW_EXTERNAL"
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

On resume **skip both initialization blocks above**, including the mutable
`main` metadata query. First verify the existing bound receipts; never create
a new pin to make resume pass:

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
source "$JW_OP/external-env.zsh"
source "$JW_OP/gold-env.zsh"
shasum -a 256 -c "$JW_OP/env.sha256" "$JW_OP/external-env.sha256" "$JW_OP/gold-env.sha256"
jw_external_check
test -s "$JW_OP/hf-pinned.json"
test -s "$JW_OP/hf-receipts.sha256"
shasum -a 256 -c "$JW_OP/hf-receipts.sha256"
source "$JW_OP/hf-env.zsh"
# Then re-hash every recovered shard/output/activation against its frozen receipt.
```

Record metadata-file checksums at their actual paths in hf-receipts.sha256 as
well as the pin/verification JSON checksums. Missing/corrupt receipts or an
incomplete initialization are STOP for a reviewed recovery; never rerun the
`main` query or overwrite hf-pinned.json. Package setup, metadata/weight fetch
and all conversion commands run through step 5's process-group guard, watching
both internal storage and the external volume. Pin/cache variables are part
of the harness resume identity and may not point at the shared home cache.

## 12. Reviewed gold-parity harness: stream, compare, convert, journal, prune

Harness authority: **PR #667,
`lane/2026-11-05-align-flashnext-gold-parity` (pushed per the lead)**.
The port is **PR #664, `lane/2026-11-05-align-flashnext-port`**, based on
`origin/port/qwen4-exp-mlx`. Record the actual reviewed full SHAs from the
Mac's available objects; no stale cached SHA or moving base is authority.
**STOP 12a:** review the harness README/`--help`, actual streaming/conversion
CLI, tolerances, torch pin, disk-floor and interrupted-unit resume behavior
before downloading weights. This offline authoring session did not fetch or
execute that lane. Do not infer correctness merely from a pushed branch.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
source "$JW_OP/external-env.zsh"
source "$JW_OP/gold-env.zsh"
shasum -a 256 -c "$JW_OP/external-env.sha256" "$JW_OP/gold-env.sha256"
jw_external_check
shasum -a 256 -c "$JW_OP/hf-receipts.sha256"
source "$JW_OP/hf-env.zsh"
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
source "$JW_OP/external-env.zsh"
source "$JW_OP/gold-env.zsh"
shasum -a 256 -c "$JW_OP/external-env.sha256" "$JW_OP/gold-env.sha256"
jw_external_check
shasum -a 256 -c "$JW_OP/hf-receipts.sha256"
source "$JW_OP/hf-env.zsh"
/usr/bin/vm_stat > "$JW_OP/vm-before-phase.txt"
/usr/sbin/sysctl vm.swapusage > "$JW_OP/swap-before-phase.txt"
/bin/df -k /System/Volumes/Data > "$JW_OP/df-before-phase.txt"
/bin/df -k "$JW_EXTERNAL" > "$JW_OP/external-df-before-phase.txt"
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

1. Source/check the saved env, external-env and gold-env files, verify
   external volume identity, then finish uploads; require no pending/error iCloud objects, downloads,
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
   external volume excluded from indexing and Time Machine. Keep the converted
   model and paged n-gram table external; recheck volume identity and the agreed
   power boundary. R0 requires amendment-1 window-1 bundle bytes for two copies plus 30 GB
   internal free after present weights, with the full plan/config citation.
   Independently admit the next kit's exact measurement-volume budget plus
   the 30 GB floor. Use the larger bound for the next stage.
3. Restore any temporarily unloaded non-measurement infrastructure from the
   saved exact plists and restore original disabled states. Do not resume a
   DONE BYTES/B6 loop. With Ed's go, remove **only this operation's** STOP
   file and restore the magistrate supervisor from its original plist:

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
# Ed only, after steps 1–2 and confirmation the STOP was created by step 2.
cmp "$JW_OP/our-STOP.txt" /Users/edr/night-custody/magistrate/STOP
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
account and any storage purchase, including the external NVMe attachment/format;
confirmation ALIGN is paused; control of
personal apps/system launchers and system privileges; independent-copy device
and receipt; exact-manifest deletion approval and every irreversible removal;
any requested change to sealed retention (not granted here); approval of
checkpoint/torch/harness pins; Spotlight Privacy/Time Machine changes; and the
go to restore ALIGN. Measurement agents cannot authorize these on Ed's behalf.

The operation handoff records machine/SSD, before/after `df`, bytes actually
freed, per-root KEEP/offloaded/deleted status, exact cloud/second-copy locations
and manifest hashes, every deletion receipt, pending uploads/errors, pinned
checkpoint and all 131 shard results, venv locks, harness CLI/commit and
coverage, streaming journal/resume state and activation hashes, external
volume/link/paging/power-boundary identity, combined R0/ALIGN disk budget, actual
peak working bytes and lowest free bytes, conversion/end-to-end outcomes, unused
model revision inventory, and pilot-9 harvest/pause/restoration status.
Report UNKNOWN, BLOCKED and PROVISIONAL explicitly. **No offload or hardware
validation occurred merely because this runbook was written.**

## Public weights deletion receipt contract (round-2 ruling N5a)

This is the only class currently eligible to reclaim internal source space:
**PUBLIC MODEL WEIGHTS NOT IN ANY PLAN**, under `jw_models` or the HF hub.
No cloud copy is required for this class. It does not grant an approval list.
Pilot roots and capture-bearing trees remain until after block-5 release.

For each exact proposed model directory, Ed and an independent reviewer must
first review the complete step-3 census from all six refs. Every registration
identity pin, BYTES roster, B6 §1.4 roster, ALIGN v4 kit, amendment-1 plan and
v4 R0 config participates. Path containment or a model identity alias in any
of them is KEEP. Dropping Next-80B or Qwen3.5-122B from ALIGN alone is insufficient:
BYTES/B6 or historical pins may still reference them. Never infer eligibility
from the expected candidate names. No real candidate was inspected here.

Use a new item directory outside the source. Save `source-path.txt` as one
canonical absolute line, `source.json` from the reviewed `tree` helper,
`source.sha256` as its exact checksum receipt, and `source-after.json` with
identical bytes. All model files must be regular, nlink-1 **blob bytes**, never
snapshot symlinks, and every file must appear in the SHA-256 inventory. No
shared HF cache cleanup is authorized. Save the complete step-3 result as
`model-census.json`; it is replayed from its full Git SHAs before deletion.

`public-weights.json` has exactly these fields: `source` (the exact approved
path), `repo_id` (the exact public HF org/repo), `revision` (40 lowercase hex
characters), `manifest_sha256`, `census_sha256`, and `files` (an exhaustive
mapping from each local manifest file path to its HF repo filename at that
revision). This mapping covers blob-cache names too; no symlinks are followed.
The independent review receipt `independent-receipt.txt` must bind the exact
source, both digests, repo id and revision. `retention-review.json` must equal:

```json
{"source":"<exact source>","manifest_sha256":"<source.json digest>","model_class":"public-weights","no_retained_ledger_locators":true,"no_measurement_data":true}
```

Ed approves the **specific list**, not a wildcard, cache root or model family.
For each item save `ed-approval.json` as `{"approver":"Ed","approved":[CLAIM]}`,
where CLAIM is the complete exact `public-weights.json` object. Any changed
path, manifest, repo, revision, census or file mapping requires a new approval.
These local receipts record Ed's review; creating JSON is not approval itself.

At deletion time the guard makes an unauthenticated **HEAD** request to the
HF API `/api/models/ORG/REPO/revision/FULL_SHA` and HEAD-checks every mapped
file at `/ORG/REPO/resolve/FULL_SHA/FILENAME`. Private/gated, missing, failed
or ambiguous responses refuse. No network was used to author or test this
procedure; HF API behavior remains an operator-time gate. This class relaxes
only mandatory model-root containment for this exact approved descendant.
It never relaxes the root itself, another KEEP entry, path/inode checks,
retention, pause/census, 30 GB floor, manifests, permissions/flags/ACLs,
source recheck, exclusive pointer publication or the validated journal.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
: "${JW_PUBLIC_ITEM:?Set reviewed exact item directory with Ed approval}"
python3.13 -I -B "$JW_CANON/scripts/align_offload_delete_root.py" delete \
  --model-class public-weights --item "$JW_PUBLIC_ITEM" \
  --keep "$JW_OP/KEEP.txt" --journal "$JW_OP/deletions.tsv" \
  > "$JW_PUBLIC_ITEM/freed-bytes.json"
```

The success JSON reports `source_regular_bytes` and the observed filesystem
`available_bytes_delta`. APFS sharing/snapshots and concurrent allocations can
make them differ; report both and budget only measured available space.
The `.OFFLOADED.json` pointer records `model_class=public-weights`, exact HF
identity, manifest/census digests, HEAD receipt and regular-file bytes; it does
not claim a cloud archive exists. **Freed in this authoring session: 0 bytes.**
