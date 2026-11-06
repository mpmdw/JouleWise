# Measurement MacBook Pro offload and gold setup runbook

**ED-MANUAL-ONLY, not executed.** Use only on the paused measurement Mac
(Mac15,9, M3 Max, 128 GB, 1 TB internal SSD). Never run these commands from
an agent on the analysis laptop or while measurement is active. The analysis
laptop's 7-worker job and blinded inputs are outside this procedure.

**Saturday 2026-11-07, DAY ONLY:** Ed attaches the borrowed **WD_Black SN7100
2 TB NVMe in an OWC Express 1M2 USB4 enclosure**. Wear is no concern. This SSD
is the independent second copy; server-confirmed iCloud is the first. The order
is **SSD copy + full verification → iCloud upload + proved eviction/download/
hash round trip → Ed-only guarded deletion**. No public-downloadability
exception authorizes deletion without both copies. This update supersedes
the earlier public-only deletion and attached-external measurement proposals.

**Eject and physically unplug the SSD before EVERY measurement window,
including R0 and R1.** Gold setup, rolling bf16 shards, caches, converted
weights and paged tables may use it by day only. Those external files are
unavailable to a measurement. Step 13's external-volume census is mandatory
immediately before arming. An ejected but still plugged-in enclosure is an
energy confound. The nominal gold peak is 120 GB; never stage the whole
roughly 360 GB/131-shard bf16 checkpoint.

Authority: RUN_STATE's item-26 capture-retention rule (historically cited as
line 45), amended item 170 / PR #662 and **items 171–174**. Item 174 ends v3
after pilot 10; it supersedes the old no-pilot-10 instruction. Wait for its
terminal record, uninstall, desk, read and pin. No pilot 11 is authorized.

| Backup target | Exact root (operator only; inert text during agent work) |
|---|---|
| Pilot 8 | `/Users/edr/night-align/pilot-v7-20261105T015948Z` |
| Pilot 9 | `/Users/edr/night-align/pilot-v8-20261105T102850Z` |
| Pilot 10 | `/Users/edr/night-align/pilot-v9-20261105T231016Z` |

Never run auto-deleting `offload.py` on any target. All three pilot/capture
roots remain KEEP until the lead installs an explicit retention ruling or
release and a reviewed guard change. The supplied program refuses all pilot
roots and capture-bearing trees; an approval receipt cannot override it.
Copying is authorized; no ledger-custody waiver is implied. Pilots 0–7 are
already offloaded; copy their iCloud-only archives to the SSD (step 7a).
They offer zero further source reclaim.

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

PR #662 / amended item 170 and later items 171–174 must be integrated in the
**Mac records checkout** first. Item 170 prohibits auto-offload; item 174
supersedes its no-pilot-10 instruction. Require pilot 9's DESK_DONE/pin/
`p9-PILOT.json` and pilot 10's terminal record, uninstall, desk, read, pin and
`p10-PILOT.json` handoff. An interactive Claude or
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
: "${JW_P10_PIN:?Set exact pilot-10 pin receipt path}"
: "${JW_P10_PILOT:?Set exact saved p10-PILOT.json path}"
: "${JW_OP:?Set one fixed NEW operation directory under night-archive}"
: "${JW_OFFLOAD_CODE_COMMIT:?Set reviewed full tooling commit}"
export JW_RECORDS JW_P9_PIN JW_P9_PILOT JW_P10_PIN JW_P10_PILOT JW_OP
# No STOP creation, bootout or uninstall before this function passes.
jw_pause_check() {
  python3.13 -I -B - <<'PY'
import json, os, re, subprocess
from pathlib import Path
s = (Path(os.environ['JW_RECORDS']) / 'RUN_STATE.md').read_text()
for item in (170, 171, 172, 173, 174):
    assert re.search(r'^' + str(item) + r'\.', s, re.M), 'STOP: current directive absent'
# Ed reviews amended item 170 AND item 174: no auto-offload or further v3 arm.
assert Path('/Users/edr/night-align/pilot-v8-20261105T102850Z/DESK_DONE').is_file(), 'STOP: no DESK_DONE'
assert Path(os.environ['JW_P9_PIN']).is_file(), 'STOP: missing pin receipt'
assert Path(os.environ['JW_P9_PILOT']).name == 'p9-PILOT.json'
assert Path(os.environ['JW_P9_PILOT']).is_file(), 'STOP: missing desk product'
assert Path(os.environ['JW_P10_PIN']).is_file(), 'STOP: missing pilot-10 pin'
assert Path(os.environ['JW_P10_PILOT']).name == 'p10-PILOT.json'
assert Path(os.environ['JW_P10_PILOT']).is_file(), 'STOP: missing pilot-10 desk'
assert Path('/Users/edr/night-align/pilot-v9-20261105T231016Z/custody/night/result.json').is_file(), 'STOP: pilot 10 not terminal'
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
# Inspect argv locally for Python-launched writers; export only matched PIDs.
subprocess.run(['python3.13', '-I', '-B',
                str(Path(os.environ['JW_CANON']) / 'scripts/align_offload_delete_root.py'),
                'census'], check=True)
print('STOP-2 pre-pause prerequisites PASS; no argv recorded')
PY
}
jw_pause_check
# Ed confirms no collection.active, armed plan or scheduled t0; all products sealed.
mkdir -m 700 "$JW_OP"
[[ "$JW_OFFLOAD_CODE_COMMIT" == [0-9a-f]## && ${#JW_OFFLOAD_CODE_COMMIT} == 40 ]]
git -C "$JW_CANON" show "${JW_OFFLOAD_CODE_COMMIT}:scripts/align_offload_delete_root.py" \
  > "$JW_OP/delete_root.py"
shasum -a 256 "$JW_OP/delete_root.py" > "$JW_OP/manifest-helper.sha256"
{
  print -r -- 'setopt interactivecomments errexit nounset pipefail extendedglob noclobber'
  for name in JW_CANON JW_MEAS JW_RECORDS JW_OP JW_P9_PIN JW_P9_PILOT JW_P10_PIN JW_P10_PILOT; do
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
  shasum -a 256 -c "$JW_OP/manifest-helper.sha256"
  python3.13 -I -B "$JW_OP/delete_root.py" uploaded "$1"
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

**STOP 2:** Ed attests current items 170–174 present, pilot-9 DESK_DONE/pin/
p9-PILOT and pilot-10 terminal/desk/read/pin/p10-PILOT saved,
lock owner gone, no named agent/writer, no collection/armed t0, launchers
absent/disabled, external schedulers accounted for. This check precedes all
STOP/bootout actions; repeat on resume. Agents must exit before measurements.

After STOP 2, perform the Ed-only SSD attach subsection **9a** before
step 3; it is a storage prerequisite, not permission to begin downloads.

## 3. Mechanical model KEEP census and pre-offload R0 inventories

Use one repository object store containing each reviewed ref; no merged
checkout is required. The model census reads only `git show <full-sha>:<path>`. Before **any offload or archive**, prepare the reviewed R0 config
from PR #661's `docs/align/r0_desk.example.json`. Keep `disk_path` on the
**measurement internal volume**; the example's `/Volumes/ALIGN_MODELS` is not
appropriate for the measurement disk gate. Set all custody parents. Set
`offloads[].destination` to separate **uncompressed directory copies** on
independent storage. Copy regular files as bytes and preserve pilot view
symlinks as links; never follow their targets. Model mirrors require regular
materialized files, not HF snapshot symlinks; tar.zst is not an R0 directory.
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
"$JW_R0_CODE/.venv/bin/python" -B "$JW_R0_CODE/scripts/align_r0_checks.py" \
  --config "$JW_R0_CONFIG" --inventory /Users/edr/night-align/pilot-v9-20261105T231016Z \
  --output "$JW_OP/pilot10-backup-inventory.json"
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

There are **no currently approved source deletions**. The former public-only
exception is retired: every deletion requires both verified backup copies. Verify/second-copy existing pilots 0–7
archives, but they reclaim no deleted-source bytes. All pilot roots and
capture-bearing trees stay until after block-5 release. The model roots remain
mandatory KEEP; this procedure grants no model-root containment exception.
Expected Next-80B and Qwen3.5-122B names are hypotheses, not approvals. Until the
complete census and Ed's specific list pass, **budget zero reclaimed bytes**.
No cache-wide, custody, calibration, B6/BYTES or personal-tree removal is granted.

**STOP 3:** R0 inventories for pilots 8/9 plus pilot10's backup inventory saved outside sources; materialized
copy destinations agreed and budgeted, full model KEEP printed and reviewed,
all three Mac pilot roots retained. R0 must use both [coordination patches](r0_disk_gate_patch.md): pilot view
symlinks are recorded as exact target text without following them; model
inventories still require materialized files. Restricted content still refuses;
retain the source and ask the lead rather than weakening that boundary.
Do not run a live R0 desk session from an agent. Copies may be made under this
paused Ed-only procedure; full R0 remains its own lead-controlled gate.

## 4. KEEP roots and immutable custody

`RUN_STATE.md:45` capture retention stays in force until block-5 release,
including removed attempts and ALIGN capture directories. Pilots 8–10 stay
**entirely on the Mac**; no split-root deletion or
locator rewrite. Their copies provide redundancy without source removal.
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
removing any pilot or taking bytes from protected evidence. Unavailable
locator review makes the proposed source UNKNOWN and KEEP.

Before copying, Ed saves immutable baseline manifests for readable KEEP data
and model blobs outside every source, with exact original path bindings and
authenticated expected digests. Existing custody manifests remain authoritative.
Checkouts/venvs/plists use saved commit/version/identity records. A blinded
baseline comes only from its authorized custody operator; agents never read
it. Missing baselines block step 13's restoration check.

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

## 6. FIRST: copy and fully verify on the SSD

Run each allocating fence as a reviewed writer file through step 5's guard
against **both** filesystems, inside tmux plus caffeinate. Device identity,
quota and source checks are required, not optional. Source bytes stay intact.
Step 2 pins the reviewed program once; all later invocations use this
immutable copy, including deletion. `step6-tool.zsh` verifies it on resume.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
shasum -a 256 -c "$JW_OP/env.sha256" "$JW_OP/manifest-helper.sha256"
```

The helper refuses dataless files **before opening**, hardlinks, special files,
nested filesystems and unsafe members. Its literal restricted/withheld-name
check is only added defense: agents must never read real blinded manifests;
the full registered path map controls operator authorization. Do not run
analysis, harvest or reducers. HF KEEP baselines hash actual **blobs** using
`model_artifact_inventory`, not just snapshot links. Hardlinks from inode
deduplication can make pilots ineligible for this format: retain the source
and obtain a reviewed preservation method. Tar drops AppleDouble/xattrs; Ed
must establish that ACLs/resource forks/xattrs/topology are unnecessary or
STOP for a reviewed preservation format. Original custody manifests stay the
trust anchors; a new manifest cannot repair pre-existing missing coverage.

`step6-item.zsh` initializes one item: **pilot8, pilot9 or pilot10**, with the
exact source from the table. First admit manifest/control bytes from existing
custody totals. No recursive home search. Resume sources this existing item-env
and checks its hashes; never initialize a new date to bypass STOP/receipts.
After an interrupted attempt, a reviewed new item ID may append `-retry01`
(or another unique ASCII suffix); preserve the old item and partial in this
same operation. Never reuse a partial or overwrite its manifest.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
source "$JW_OP/external-env.zsh"
shasum -a 256 -c "$JW_OP/env.sha256" "$JW_OP/external-env.sha256" "$JW_OP/manifest-helper.sha256"
jw_external_check
: "${JW_SRC:?Set one exact pilot source from the table}"
: "${JW_ID:?Set pilot8 pilot9 pilot10 or a reviewed unique retry ID}"
[[ "$JW_ID" == [A-Za-z0-9_-]## ]]
[[ "$JW_ID" == (pilot8|pilot9|pilot10|pilot8-*|pilot9-*|pilot10-*) ]]
export JW_SRC JW_ID JW_ITEM="$JW_OP/$JW_ID"
mkdir -m 700 "$JW_ITEM"
{
  for name in JW_SRC JW_ID JW_ITEM; do
    printf 'export %s=%q\n' "$name" "${(P)name}"
  done
} > "$JW_ITEM/item-env.zsh"
printf '%s\n' "$JW_SRC" > "$JW_ITEM/source-path.txt"
python3.13 -I -B "$JW_OP/delete_root.py" tree "$JW_SRC" > "$JW_ITEM/source.json"
shasum -a 256 "$JW_ITEM/source.json" > "$JW_ITEM/source.sha256"
shasum -a 256 "$JW_ITEM/item-env.zsh" > "$JW_ITEM/item-env.sha256"
```

`step6-ssd.zsh`, a guarded writer: create the archive **directly on the SSD**,
then compare every member, make a complete restore and re-hash it. The
source.json totals compute admission; assume no compression savings. Retain
the restored tree until the operation closes; deletion re-reads all its bytes.
These two forms on one SSD still count as only one independent device.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
source "$JW_OP/external-env.zsh"
source "${JW_ITEM:?Set existing item}/item-env.zsh"
shasum -a 256 -c "$JW_OP/env.sha256" "$JW_OP/external-env.sha256" \
  "$JW_OP/manifest-helper.sha256" "$JW_ITEM/item-env.sha256" "$JW_ITEM/source.sha256"
jw_external_check
export JW_SECOND_DIR="$JW_EXTERNAL/JouleWise-backup/${JW_OP:t}/$JW_ID"
export JW_ARCHIVE_BUDGET_BYTES="$(python3.13 -I -B "$JW_OP/delete_root.py" budget "$JW_ITEM/source.json")"
export JW_SOURCE_BYTES="$(python3.13 -I -B -c \
  'import json,sys; print(sum(r[3] for r in json.load(open(sys.argv[1])) if r[1]=="file"))' "$JW_ITEM/source.json")"
jw_disk_check "$((JW_ARCHIVE_BUDGET_BYTES + JW_SOURCE_BYTES))" "$JW_EXTERNAL"
mkdir -p "${JW_SECOND_DIR:h}"
mkdir -m 700 "$JW_SECOND_DIR"
COPYFILE_DISABLE=1 /usr/bin/tar --no-mac-metadata --no-xattrs -cf - \
  -C "$JW_SRC" . | zstd -T1 -3 -o "$JW_SECOND_DIR/$JW_ID.tar.zst.partial"
test ! -e "$JW_SECOND_DIR/$JW_ID.tar.zst"
mv -n "$JW_SECOND_DIR/$JW_ID.tar.zst.partial" "$JW_SECOND_DIR/$JW_ID.tar.zst"
cp -p "$JW_ITEM/source.json" "$JW_SECOND_DIR/$JW_ID.manifest.json"
zstd -dc "$JW_SECOND_DIR/$JW_ID.tar.zst" | \
  python3.13 -I -B "$JW_OP/delete_root.py" archive > "$JW_ITEM/ssd-members.json"
cmp "$JW_ITEM/source.json" "$JW_ITEM/ssd-members.json"
mkdir -m 700 "$JW_SECOND_DIR/restored"
zstd -dc "$JW_SECOND_DIR/$JW_ID.tar.zst" | /usr/bin/tar -xpf - -C "$JW_SECOND_DIR/restored"
python3.13 -I -B "$JW_OP/delete_root.py" second-copy --item "$JW_ITEM" \
  --volume "$JW_EXTERNAL" --uuid "$JW_EXTERNAL_UUID" \
  --archive "$JW_SECOND_DIR/$JW_ID.tar.zst" --manifest "$JW_SECOND_DIR/$JW_ID.manifest.json" \
  --restore "$JW_SECOND_DIR/restored"
python3.13 -I -B "$JW_OP/delete_root.py" tree "$JW_SRC" > "$JW_ITEM/source-after.json"
cmp "$JW_ITEM/source.json" "$JW_ITEM/source-after.json"
shasum -a 256 "$JW_SECOND_DIR/$JW_ID.tar.zst" "$JW_SECOND_DIR/$JW_ID.manifest.json" \
  > "$JW_ITEM/ssd.sha256"
shasum -a 256 -c "$JW_ITEM/ssd.sha256"
```

**STOP 6:** all source/member/restore bytes match, copied manifest and archive
checksums verified, exact UUID and coverage in independent-copy.json. A
receipt alone never authorizes deletion: step 8 re-reads the attached SSD.
On interruption preserve source/partial; use a new reviewed attempt ID.
**Ed only** can retire a failed partial with an exact-path rename, never a glob:

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
source "$JW_OP/external-env.zsh"
: "${JW_PARTIAL:?Set exact failed SSD partial path}"
: "${JW_RETIRED:?Set exact NEW retired path on that SSD}"
jw_external_check
test -f "$JW_PARTIAL"
test ! -L "$JW_PARTIAL"
test ! -e "$JW_RETIRED"
mv -n -- "$JW_PARTIAL" "$JW_RETIRED"
```

Record failure and both paths; budget retained bytes. Rename is no deletion
permission. No automatic cleanup and no overwrite of a prior receipt.

## 7. THEN: iCloud upload, server confirmation and proved round trip

`step7-cloud.zsh`, a guarded writer. Quota and step 5's **real parser pin**
must pass first. The parser is unpinned and always refuses until a reviewed
native sample is installed. Copy from the verified SSD; bind EXPECTED hashes
to the cloud destinations and check the copied manifest too.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
source "$JW_OP/external-env.zsh"
source "${JW_ITEM:?Set existing item}/item-env.zsh"
shasum -a 256 -c "$JW_OP/env.sha256" "$JW_OP/external-env.sha256" \
  "$JW_OP/manifest-helper.sha256" "$JW_ITEM/item-env.sha256" "$JW_ITEM/ssd.sha256"
jw_external_check
export JW_SECOND_DIR="$JW_EXTERNAL/JouleWise-backup/${JW_OP:t}/$JW_ID"
export JW_ARCHIVE_BUDGET_BYTES="$(python3.13 -I -B "$JW_OP/delete_root.py" budget "$JW_ITEM/source.json")"
jw_disk_check "$JW_ARCHIVE_BUDGET_BYTES"
test ! -e "$JW_REMOTE/$JW_ID.tar.zst"
test ! -e "$JW_REMOTE/$JW_ID.manifest.json"
cp -p "$JW_SECOND_DIR/$JW_ID.tar.zst" "$JW_REMOTE/$JW_ID.tar.zst"
cp -p "$JW_SECOND_DIR/$JW_ID.manifest.json" "$JW_REMOTE/$JW_ID.manifest.json"
python3.13 -I -B - <<'PY'
import json, os
from pathlib import Path
item = Path(os.environ['JW_ITEM'])
receipt = json.loads((item/'independent-copy.json').read_text())
for name, sha, dest in [('archive', receipt['archive_sha256'], os.environ['JW_ID']+'.tar.zst'),
                        ('cloud-manifest', receipt['manifest_sha256'], os.environ['JW_ID']+'.manifest.json')]:
    with (item/(name+'.sha256')).open('x') as f:
        f.write(sha+'  '+str(Path(os.environ['JW_REMOTE'])/dest)+'\n')
PY
shasum -a 256 -c "$JW_ITEM/archive.sha256" "$JW_ITEM/cloud-manifest.sha256"
zstd -dc "$JW_REMOTE/$JW_ID.tar.zst" | \
  python3.13 -I -B "$JW_OP/delete_root.py" archive > "$JW_ITEM/cloud-local.json"
cmp "$JW_ITEM/source.json" "$JW_ITEM/cloud-local.json"
jw_uploaded "$JW_REMOTE/$JW_ID.tar.zst"
jw_uploaded "$JW_REMOTE/$JW_ID.manifest.json"
python3.13 -I -B "$JW_OP/delete_root.py" cloud-roundtrip --item "$JW_ITEM" --remote "$JW_REMOTE"
shasum -a 256 -c "$JW_ITEM/archive.sha256" "$JW_ITEM/cloud-manifest.sha256"
cmp "$JW_ITEM/source.json" "$JW_ITEM/cloud-roundtrip.json"
```

The hashed program runs fileproviderctl evaluate for BOTH files and requires
isUploaded=1 with no pending/error/conflict state. For each it evicts, polls
st_flags until **dataless**, downloads, polls **not dataless**, re-hashes archive
and manifest, streams every tar member, then publishes cloud-proof.json.
Asynchronous/no-op eviction or Keep Downloaded timeout is STOP. Keep the
hydrated files through deletion; the final program repeats server checks.
No local hash/progress bar/sampling replaces that round trip.

**STOP 7:** SSD plus server-confirmed iCloud cover every byte. Export only
redacted facts; keep raw diagnostic/plist/argv/cron records local until Ed
reviews credentials. Sources and raw custody records remain immutable.

### 7a. Copy the existing iCloud-only archives to this SSD (M6)

Required even when no deletion is eligible: **ALIGN pilots 0–7**, under
`JouleWise-archive/2026-11-04-align-pilots`, **BYTES H/H2 raw tars** (historical
RUN_STATE:1239) and **R7 A343/P0/READY**. Ed supplies each exact archive path,
authenticated original manifest/digest and original reviewed verifier. No
wildcard hydration or agent reads. One checklist row per item records source,
coverage, archive/manifest SHA-256, SSD UUID, full member/restore result and UTC.

In a guarded `step7-existing.zsh` writer, admit internal archive hydration and
SSD archive plus largest complete restore workspace separately. Require
uploaded, hydrate and poll not-dataless, check **original expected** digests,
copy to a new SSD item directory, rebind those expected checksums to destination
filenames and run `shasum -a 256 -c`. Stream ALL members using the original
format/verifier, restore into an empty directory, re-hash every restored byte
against the original manifest. Verify copied manifest/helper hashes too. Apply
the same proved cloud round trip with that original verifier. Missing original
hash/coverage/parser/quota is BLOCKED; hashing a possibly corrupt copy never
creates a replacement trust anchor. Preserve the attributed per-item receipt.
No archive is deleted. Only after verification may the uploaded cloud staging
copy be evicted; poll dataless. Finish by day or preserve state and eject/unplug
at day end. The measurement pause continues if work is incomplete.

Save the following as the guarded `step7-existing.zsh` for one original-format
item. Ed supplies the exact original hashes and a reviewed format-specific
verifier file whose commands perform BOTH full member and restore comparison,
with these exported paths. The file is a required input, not a supplied or
guessed historical interface; absent reviewed verifier means STOP for that row.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
source "$JW_OP/external-env.zsh"
shasum -a 256 -c "$JW_OP/env.sha256" "$JW_OP/external-env.sha256" "$JW_OP/manifest-helper.sha256"
jw_external_check
: "${JW_EXISTING_ARCHIVE:?Set exact iCloud archive from original custody records}"
: "${JW_EXISTING_MANIFEST:?Set its original manifest}"
: "${JW_EXISTING_ARCHIVE_SHA:?Set authenticated original archive digest}"
: "${JW_EXISTING_MANIFEST_SHA:?Set authenticated original manifest digest}"
: "${JW_EXISTING_COPY:?Set NEW exact item directory on enrolled SSD}"
: "${JW_EXISTING_VERIFY_FILE:?Set reviewed original-format verifier writer file}"
: "${JW_EXISTING_VERIFY_SHA:?Set its reviewed SHA256}"
: "${JW_EXISTING_INTERNAL_BUDGET:?Set recorded archive plus manifest hydration bytes}"
: "${JW_EXISTING_SSD_BUDGET:?Set archive plus complete restore and controls}"
export JW_EXISTING_ARCHIVE JW_EXISTING_MANIFEST JW_EXISTING_COPY
jw_disk_check "$JW_EXISTING_INTERNAL_BUDGET"
jw_disk_check "$JW_EXISTING_SSD_BUDGET" "$JW_EXTERNAL"
jw_uploaded "$JW_EXISTING_ARCHIVE"
jw_uploaded "$JW_EXISTING_MANIFEST"
/usr/bin/brctl download "$JW_EXISTING_ARCHIVE"
/usr/bin/brctl download "$JW_EXISTING_MANIFEST"
jw_wait_dataless "$JW_EXISTING_ARCHIVE" no
jw_wait_dataless "$JW_EXISTING_MANIFEST" no
mkdir -m 700 "$JW_EXISTING_COPY"
printf '%s  %s\n' "$JW_EXISTING_ARCHIVE_SHA" "$JW_EXISTING_ARCHIVE" \
  "$JW_EXISTING_MANIFEST_SHA" "$JW_EXISTING_MANIFEST" \
  "$JW_EXISTING_VERIFY_SHA" "$JW_EXISTING_VERIFY_FILE" > "$JW_EXISTING_COPY/original.sha256"
shasum -a 256 -c "$JW_EXISTING_COPY/original.sha256"
cp -p "$JW_EXISTING_ARCHIVE" "$JW_EXISTING_COPY/archive"
cp -p "$JW_EXISTING_MANIFEST" "$JW_EXISTING_COPY/manifest"
printf '%s  %s\n' "$JW_EXISTING_ARCHIVE_SHA" "$JW_EXISTING_COPY/archive" \
  "$JW_EXISTING_MANIFEST_SHA" "$JW_EXISTING_COPY/manifest" > "$JW_EXISTING_COPY/copied.sha256"
shasum -a 256 -c "$JW_EXISTING_COPY/copied.sha256"
/bin/zsh -f -euo pipefail "$JW_EXISTING_VERIFY_FILE"
```

### 7b. Materialized R0 copies, retaining all sources

R0's own `--inventory` receipts for **pilot8 and pilot9** must already exist
from step 3. Also inventory and copy pilot10 for backup. Destinations are
**uncompressed directories**, never tar.zst. Preserve pilot measurement-view
symlinks as links without following targets; models require materialized
non-symlink files. Use both [R0 inventory patches](r0_disk_gate_patch.md).

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
source "$JW_OP/external-env.zsh"
source "$JW_OP/r0-env.zsh"
shasum -a 256 -c "$JW_OP/env.sha256" "$JW_OP/external-env.sha256"
jw_external_check
: "${JW_R0_SOURCE:?Set exact pilot source}"
: "${JW_R0_DEST:?Set configured NEW SSD directory destination}"
: "${JW_R0_EXPECTED:?Set original pre-offload inventory JSON}"
: "${JW_R0_ACTUAL:?Set NEW comparison receipt path}"
test ! -e "$JW_R0_DEST"
mkdir -m 700 "$JW_R0_DEST"
cp -pRP "$JW_R0_SOURCE/." "$JW_R0_DEST/"
"$JW_R0_CODE/.venv/bin/python" -B "$JW_R0_CODE/scripts/align_r0_checks.py" \
  --config "$JW_R0_CONFIG" --inventory "$JW_R0_DEST" --output "$JW_R0_ACTUAL"
cmp "$JW_R0_EXPECTED" "$JW_R0_ACTUAL"
```

Run through the two-volume guard, with all remaining bytes admitted. Agree
labels/destinations before copying; never rewrite original locators. **The SSD
is absent during R0.** Copy verification is a daytime desk phase; preserve its
authenticated receipts, then eject/unplug before measurement. If the current
R0 gate requires probing external destinations during measurement, STOP for
the R0 lead to separate copy verification from measurement admission. Do not
claim that gate passes after unplugging or measure with the enclosure attached.

## 8. LAST: Ed-only deletion through one hashed program

**No currently approved pilot deletion.** All three pilot/capture roots stay
until release or an installed ruling and guard change. Obtain a structure-only
list of **all ledger locators under each source**, without values. Missing or
retained locators are STOP. Do not split roots, move captures or rewrite
locators. This is copy-only for pilots 8–10 until the lead resolves retention.
The former public-weights no-backup path is retired: ALL deletion needs SSD
plus server-confirmed iCloud. No model or shared-HF-cache cleanup is implied.

For a separately approved eligible model leaf, mandatory KEEP entries must
all exist and pass inode/ancestor comparison. The exact source must be in
`$JW_OP/approved-models.txt`; that list cannot bypass KEEP. Both
`independent-receipt.txt` and `ed-approval.txt` must contain this source path,
source-manifest SHA and archive SHA, reviewer/Ed attribution and UTC.
`retention-review.json` must exactly bind `source`, `manifest_sha256`,
`archive_sha256`, `no_retained_ledger_locators: true`. An approval file records
an actual review; writing JSON is no substitute. The technical
independent-copy.json is checked against the mounted SSD UUID, archive,
copied manifest and complete restored tree. Keep that restore until completion.

`step8-delete.zsh`, **Ed only**; inoperative for all three pilot targets:

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
source "$JW_OP/external-env.zsh"
source "${JW_ITEM:?Set reviewed eligible item}/item-env.zsh"
shasum -a 256 -c "$JW_OP/env.sha256" "$JW_OP/external-env.sha256" \
  "$JW_OP/manifest-helper.sha256" "$JW_ITEM/item-env.sha256" "$JW_ITEM/source.sha256"
jw_external_check
python3.13 -I -B "$JW_OP/delete_root.py" delete --item "$JW_ITEM" \
  --remote "$JW_REMOTE" --keep "$JW_OP/KEEP.txt" --journal "$JW_OP/deletions.tsv" \
  > "$JW_ITEM/freed-bytes.json"
```

All checks and shutil.rmtree are in this program; no shell rm -rf. It refuses
uncanonical paths, symlink ancestors, missing KEEP, inode overlap, disallowed
sources, pilots/captures, dataless/hardlink/special files, nested filesystems,
uchg/schg/uappnd/sappnd and ACLs. It verifies source and all manifests/hashes,
both attributed receipts, actual SSD bytes and retention review; re-hashes the
source, then repeats STOP/writer/disk checks and BOTH fileproviderctl upload
checks immediately before removal. Python-launched writers are detected by
locally inspected argv; only matched PIDs leave the census. Unknown state
refuses before deletion, independently of the shell's error handling.

An exclusive `.OFFLOADED.json.pending` recovery pointer and fsynced
DELETE_AUTHORIZED journal row precede removal. Success publishes
`.OFFLOADED.json` and DELETED. Preflight failure is REFUSED_NO_DELETE;
OS/I/O failure after removal starts is FAILED_PARTIAL. Keep pending pointer,
partials and original manifests for lead review; deletion is not transactional.
Never retry blindly. **STOP 8:** record regular-file bytes and actual available
space delta separately; credit only measured df space. APFS clones/snapshots
can make them differ. **Freed in this authoring session: 0 bytes.**

## 9. Combined internal/external budget and primary external-SSD plan

### 9a. Ed-only Saturday SSD attach gate (after STOP 2, before step 3 copies)

From Saturday November 7, use the borrowed **WD_Black SN7100 2 TB / OWC
Express 1M2 USB4** SSD, attached **by day only**. Wear is no concern. Ed checks
its identity, existing contents and APFS format in Disk Utility; no formatting
command or permission to erase the borrowed disk is supplied. Set Spotlight
Privacy and Time Machine exclusions. Record the actual volume UUID, capacity,
free bytes and enclosure identity. This is the independent second copy,
separate from internal storage and iCloud; two folders on it are one device.
Keep backups in `JouleWise-backup`, apart from gold scratch. Budget every use.
Eject and physically unplug before R0, R1 or any other measurement, every time.

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
assert d.get('Internal') is False
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

Gold/setup throughput may be measured on synthetic or model bytes by day,
outside all measurement windows. Record link/enclosure/firmware, filesystem,
throughput and thermal behavior; these are setup observations, not energy
validation. External paging is forbidden during measurements under the day-only
rule. A model/table required for a later measurement must first fit and be
verified on internal storage, with its own disk and no-swap admission. Otherwise
that measurement stays blocked. Neither gold parity nor an attached external
R0 copy authorizes leaving the enclosure connected.

### 9b. Honest reachable space and one combined admission

Measure current internal available bytes with df. No deletion candidate or
byte total is established in this blind session: **budget zero reclaimed bytes**
until retention, copies and Ed's exact approval all pass. All pilots/capture
trees remain retained. Pilots 0–7 offer no further source reclaim. Eviction of
a cloud staging copy returns only that staging allocation.

Post-offload planning budget (decimal GB; historical sizes are estimates,
not live observations):

| Case | Estimated internal available AFTER staging eviction, before journal/new allocations |
|---|---|
| Current estimate, all pilot sources retained | about **66 GB**; no pilot reclaim credited |
| Hypothetical later approval of pilots 8 + 9, about 26 GB each | about **118 GB**, below the 150 GB gold target |
| Hypothetical later approval of pilot 10 too, another about 26 GB | about **144 GB**, still below 150 GB; actual pilot-10 size unknown |
| R0 admission | at least **80 GB + remaining journal/control bytes**, AND any larger reviewed plan requirement |
| Internal 95 GB converted model + historical 41.2 GB next window + 30 GB floor | **166.2 GB + journal**, unavailable in all the estimates above |

The hypothetical rows authorize nothing. Compute live post-offload availability
as `F_before + actual_source_available_delta - still_resident_staging - new_journal`.
Do not count logical sizes, snapshots, purgeable capacity or promised evictions.
R0's minimum is **80,000,000,000 bytes plus journal**, after model weights; if
the reviewed amendment-1 gate is larger, also enforce **two copies + 30 GB**
(`max(80 GB, 2 * W1_bundle_bytes + 30 GB) + remaining journal`). Pin actual
W1 bytes/config/citation using the [R0 patch series](r0_disk_gate_patch.md).
Unknown W1/budget or a gate still probing an unplugged SSD is STOP, not waiver.

`step9-budget.zsh` records and enforces the combined internal requirement; it
reads only filesystem free-space metadata. The budget inputs come from the
reviewed current plan, never a guessed number or zero for an unknown need.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
: "${JW_W1_BUNDLE_BYTES:?Set pinned amendment-1 one-copy bytes}"
: "${JW_JOURNAL_REMAINING_BYTES:?Set remaining journal/control allocation}"
export JW_W1_BUNDLE_BYTES JW_JOURNAL_REMAINING_BYTES
python3.13 -I -B - <<'PY'
import json, os
from pathlib import Path
w1 = int(os.environ['JW_W1_BUNDLE_BYTES'])
journal = int(os.environ['JW_JOURNAL_REMAINING_BYTES'])
assert w1 > 0 and journal > 0, 'STOP: missing allocation bounds'
s = os.statvfs('/System/Volumes/Data')
free = s.f_bavail * s.f_frsize
required = max(80_000_000_000, 2*w1 + 30_000_000_000) + journal
with Path(os.environ['JW_OP'], 'r0-budget.json').open('x') as f:
    json.dump(dict(available=free, required=required, shortfall=max(0, required-free)), f)
assert free >= required, 'STOP: R0 internal disk budget'
PY
```

Gold by day may use the external **120 GB streaming peak + 30 GB floor =
150 GB** bound, replaced by the frozen actual schedule. Keeping its roughly
95 GB output external does not make it usable for an unplugged measurement.
The historical 41.2 GB next-window estimate must also be replaced by the current
kit's exact allocation before arming; independently admit that need + floor.

Use this single budget before packaging, hydration, copying, setup and every
gold unit. Fill **all** remaining allocations, and repeat after metadata pins,
retries and materialized R0 copies. Count allocations already reflected in
current `df` once, not again as future bytes. Use maximum **simultaneous** use.

| Filesystem / stage | Remaining new bytes to fund, in addition to current resident bytes |
|---|---|
| Internal, per offload | One archive upper bound from `source.json`, cloud hydration, probe copies and small journal/control writes. Keep source resident until step 8 passes. Retained pilots 8–10 and all KEEP weights remain. |
| Internal, future selection/measurement | After present weights/copies: R0 requires **amendment-1 window-1 bundle bytes for two copies + 30 GB** on the internal measurement `disk_path`. Pin the plan/config citation and actual bytes; also enforce the 80 GB minimum plus journal. Next ALIGN separately admits its reviewed allocation plus the floor. Use the larger bound for simultaneous needs; see [R0 patch series](r0_disk_gate_patch.md). |
| External, R0 | Uncompressed pilot 8/9/10 materialized copies, matching the pre-offload inventories; complete materialized mirrors of the reviewed v4 R0 models if not already present, using their exact pinned inventories and measured bytes. Do not count a compressed tar or HF symlinks as a mirror. Keep inventories/config/results outside sources. |
| External, durable custody | Existing ALIGN 0–7, H/H2, R7 archive/manifest copies, any separately approved new backup archives, plus **largest complete restore workspace**. If this is gold's device, all copies compete in the same budget and remain resident. Otherwise budget/check the backup device separately. |
| External, streaming gold | Remaining converted output up to **95 GB**, maximum simultaneous bounded bf16/download/temp unit initially **15 GB**, and remaining env/cache/metadata/activation/journal overhead initially **10 GB**, plus **30 GB floor**. Replace estimates with the actual frozen schedule; incomplete downloads, output temp/atomic overlap, caches and re-downloads count. |
| Whole operation | Every filesystem passes its own current-free ≥ remaining simultaneous allocations + required floor; the amendment-1 R0 two-copy-plus-floor gate and future ALIGN gate also pass before those stages. Do not add free bytes across disks to satisfy any single-filesystem constraint. |

Layer 0's roughly 24-shard union and layer 1's roughly 35-shard/100 GB bf16
n-gram table need bounded subunits, not entire unions staged simultaneously.
Layers 2–47 are expected at about 3 shards/7 GB each. A 15 GB unit allowance
is valid only after review includes source shard verification, conversion temp
files, partials, shared-shard consumers and activation checkpoints. The exact
step-11 `weight_map` schedule controls final weight admission. No full 360 GB
snapshot or duplicate shared HF cache is admitted on either SSD.

**STOP 9:** the estimated 66 GB retained-source case fails R0; do not claim an arm is unblocked. Ed records volume identities, available bytes and every remaining
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

**Prospective harness requirements, not Saturday execution authority.** No
automatic data/model-source deletion is authorized by this section. Before a
runner may use the pruning lifecycle described below, the lead must review
its cleanup against this update's two-copy rule and Ed-only hashed deletion
program, or obtain Ed's explicit separate scratch-retention policy. Until then,
retain downloaded sources and STOP before a unit that depends on pruning.
The 120 GB streaming estimate relies on pruning; it is not an admitted bound
for a no-pruning run. Re-budget retained bytes before continuing. This prevents
the old gold runner from becoming a back door around step 8.

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
   parity, conversion and restart state are committed AND the cleanup gate
   above is satisfied may Ed use the reviewed deletion program to remove
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
then stop at the cleanup gate before removing its bf16 source or fetching the
next unit that depends on that space. Accumulate actual PLE
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
before retrying. Official shards remain retained until the cleanup gate passes;
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
   model and paged n-gram table external for daytime setup only. They cannot be
   dependencies of an unplugged window. R0 requires at least 80 GB plus journal
   AND amendment-1 window-1 bundle bytes for two copies plus 30 GB
   internal free after present weights, with the full plan/config citation.
   Independently admit the next kit's exact measurement-volume budget plus
   the 30 GB floor. Use the larger bound for the next stage.
3. Finish the guarded writers, validate backup coverage/receipts, preserve
   both copies and the redacted journal, and stop every allocating process.
   **Ed only:** eject the exact enrolled SSD, then physically unplug it.
   Save this as `step13-eject.zsh`; a failed eject keeps the pause:

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
source "$JW_OP/external-env.zsh"
shasum -a 256 -c "$JW_OP/env.sha256" "$JW_OP/external-env.sha256" "$JW_OP/manifest-helper.sha256"
jw_external_check
python3.13 -I -B "$JW_OP/delete_root.py" census
/bin/sync
/usr/sbin/diskutil eject "$JW_EXTERNAL"
```

   **Physically unplug before the next script.** The magistrate runs the
   read-only census below immediately before **every** R0, R1 and later arm,
   with a fresh receipt filename. A nonzero exit prevents arm/install and
   keeps STOP. It uses `diskutil list -plist external` AND `mount`, refuses
   unknown/tool-failure state, any mounted non-system external/network/image
   volume and even attached-but-unmounted external media. It writes only
   redacted mount points/device IDs; never raw mount options/credentials.
   An all-clear is an instant census, not proof against later reconnection.

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
: "${JW_EXTERNAL_CENSUS_RECEIPT:?Set NEW unique pre-arm JSON receipt path}"
python3.13 -I -B "$JW_CANON/scripts/external_volume_census.py" \
  > "$JW_EXTERNAL_CENSUS_RECEIPT"
```

4. Restore any temporarily unloaded non-measurement infrastructure from the
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
/bin/launchctl list
```

5. ALIGN stays paused after pilot 10 until the lead/Ed explicitly schedule its
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
```

**STOP:** separate normal plan review/notice/ack and exit every agent through
the established arm handoff. Only the authorized magistrate saves and runs
the separate install file after those gates. Re-run the census immediately
before installation; failure prevents the following command:

```zsh
source "${JW_OP:?Set existing operation}/env.zsh"
: "${JW_NEXT_SESSION:?Set approved NEW session root}"
: "${JW_EXTERNAL_CENSUS_RECEIPT:?Set NEW unique pre-arm JSON receipt}"
python3.13 -I -B "$JW_CANON/scripts/external_volume_census.py" \
  > "$JW_EXTERNAL_CENSUS_RECEIPT"
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
model revision inventory, pilots 8–10 terminal/desk/pin and retained-source
status, SSD eject/unplug receipt and each pre-arm external-volume census.
Report UNKNOWN, BLOCKED and PROVISIONAL explicitly. **No offload or hardware
validation occurred merely because this runbook was written.**
