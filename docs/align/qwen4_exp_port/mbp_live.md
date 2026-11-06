# Saturday 2026-11-07: Flash-Next on the measurement MacBook Pro

Preparation is PROVISIONAL. No real weights or Mac validation were run to
write this document. This run covers GOAL 6, 7, 8 and the conversion/end-to-end
portion of 11. The full 48-layer streamed gold pass is separate, lead-owned
PR #680 (`origin/lane/2026-11-05-qwen4exp-gold-stream`). Its laptop result does
not establish full-model fit or close GOAL 11's Mac gate.

This is daytime **validation**, outside every energy measurement window.
Do not use powermetrics, arm a campaign, or run the block-5 analysis pipeline.
Never open study data or a real `restricted/` directory. Stop or wait out the
seven-worker analysis job before the Saturday native checks; do not stop it
as part of preparing this runbook. Exit all agent sessions before native
validation. `--validation-only` is the operator's explicit assertion that
these conditions hold; it is not an automatic census of measurement jobs.
One automatic guard exists: every live command (download, convert, each
native probe, the bf16 benchmark) refuses while `launchctl list` shows a
measurement agent (`com.joulewise.night*`, `com.joulewise.b6loop`,
`com.joulewise.b6wake*`). It checks at command start only, in the logged-in
GUI user's launchd domain; run from Terminal on the Mac, not over SSH. Unload
those agents by the lead's procedure before validation and restore them only
after step 7's eject. The magistrate/watchdog is not covered: stop it first
so it cannot arm a window mid-validation.

## Hardware, storage and acceptance

Use the M3 Max MacBook Pro, 128 GB unified memory, AC power, lid open, sleep
prevented for the duration. The 1 TB internal SSD has little free space.
Keep **all** checkpoint/cache/conversion/temp/evidence bytes on the WD SN7100
2 TB in the OWC Express 1M2 USB4 enclosure, APFS `/Volumes/JW-EXT`. Expected
sequential throughput is about 3 GB/s; random PLE paging may be much slower.
The SN7100 is DRAM-less and relies on host memory buffer (HMB), which a
USB4-NVMe bridge cannot provide; expect higher random-read latency than its
internal-slot specification, so first-pass PLE gathers can bound decode.
Do not reformat, wipe, offload or delete study data. This external-storage
plan supersedes the old internal-SSD/offload logistics for this run only.

### Saturday order with offload run A (same SSD, same day)

PR #665's copy-only offload run A (`docs/align/mbp_offload_and_gold_setup.md`
§15 on `lane/2026-11-05-mbp-offload-runbook`) uses the same enclosure and must
record its bus baseline **before the SSD is ever plugged in**. Its step
`step2-pause` also boots out every `com.joulewise.*` launchd job, which is the
"lead's procedure" this kit's agent guard expects. Order:

1. SSD unplugged: offload driver A1 (steps 1, 2, 2-pause, 2b bus baseline).
   Meanwhile this runbook's step 0 internal checks and native tiny tests.
2. Plug in. Settle the volume name/format (next subsection) **before**
   offload `step9a-identify`, because 9a enrolls the VolumeUUID and mount.
   Use `JW_EXTERNAL=/Volumes/JW-EXT` for the offload so both jobs share one
   enrolled volume.
3. Offload driver A2 (pilot 8-10 copies, 7a rows, eject, ejected census),
   unplug, driver A3 (unplugged census must pass).
4. Plug in again; offload `jw_external_check` from its external-env; then
   this runbook from step 0's JW-EXT part through step 7.
5. Step 7 ends with offload `step13-eject.zsh`, `step13-ejected-census.zsh`,
   physical unplug and `step13-unplugged-census.zsh` (offload §15 "each day
   the SSD is used"). The operation STOP stays; restoring the magistrate for
   ALIGN R1 is Ed's separate go (offload §13).

The Flash-Next probes take 7-20 h after the download starts. If ALIGN v4 R1
must run Saturday night, stop at a clean command boundary (memory gate first),
do step 7's evidence copy and eject/census, and resume the remaining native
commands another daytime slot: each native command re-verifies the artifact
by its recorded `PIN`, so a later resume is sound. Never leave JW-EXT attached
into a window.

### Volume name and format (before anything is written)

The scripts hard-require the mounted **APFS** volume at exactly
`/Volumes/JW-EXT` (`diskutil info` MountPoint and FilesystemType). Inspect
first, read-only:

```sh
diskutil list external physical   # the SN7100 whole disk and its partitions
diskutil list external            # includes the APFS synthesized container, if any
ls /Volumes
export OLDVOL="/Volumes/WD_BLACK" # replace with the SSD's actual mount, if mounted
diskutil info "$OLDVOL" | grep -E 'Volume Name|File System Personality|Mount Point|Volume UUID|Volume Free Space'
```

- **APFS volume already named JW-EXT:** proceed.
- **APFS, other name** (e.g. `/Volumes/WD_BLACK`), non-destructive. To keep
  the lender's files separate, add a new volume in the same container; free
  space is shared, so confirm `df -h` afterwards (needs >=650 GB, >=800 GB
  for the maxfit5 fallback):
  ```sh
  diskutil apfs addVolume "$(diskutil info -plist "$OLDVOL" | plutil -extract APFSContainerReference raw -o - -)" APFS JW-EXT
  ```
  Or, if the lender agrees the volume itself may hold this work,
  `diskutil rename "$OLDVOL" JW-EXT` (keeps data and VolumeUUID).
- **Mac OS Extended (HFS+):** `diskutil apfs convert <its diskNsM>` converts
  in place, then rename as above. Copy anything the lender needs first.
- **exFAT, MS-DOS/FAT, NTFS, unformatted or "not readable":** the kit
  refuses. The only supported path is erasing the **whole** disk, which
  **destroys every file on it**. Ed only, and only with the lender's explicit
  consent. Identify the enclosure's physical whole disk (about 2.0 TB,
  external, USB, the SN7100 media name) and re-check it immediately before:
  ```sh
  diskutil list external physical
  export EXTDISK=disk4                # the SN7100 whole disk; NEVER disk0
  diskutil info "$EXTDISK" | grep -E 'Device / Media Name|Disk Size|Protocol|Internal|Removable'
  diskutil eraseDisk APFS JW-EXT GPT "$EXTDISK"   # DESTROYS ALL DATA on $EXTDISK
  diskutil info /Volumes/JW-EXT | grep -E 'File System Personality|Mount Point'
  ```
  Use plain `APFS` (not case-sensitive, not encrypted, so no password prompt
  blocks a remount). If it mounts as `/Volumes/JW-EXT 1`, a stale name
  exists; eject and resolve that before continuing, since the kit refuses it.

Source: `Qwen/Qwen3.8-Flash-Next` at
`de4b8e4d43b917e7706784d8bb445c9af86a3540`, 131 bf16 shards, about 360 GB.
The source snapshot is a set of HF-cache symlinks to the external blob store,
not a second 360 GB copy. Allow at least **650 GB free initially**: source
360 + maxfit about 211 + temp/headroom (the download refuses below it). A
resumed download is credited the source blobs already cached, so an
interrupted transfer restarts with the same command. Keeping maxfit5 as well
requires another 195.3 GB (the converter's plan for the pinned config: 92.9 GB
of weights plus the 102.4 GB PLE table; maxfit is 210.4 GB): its convert
refuses below 225 GB free, so
the fallback path needs about **800 GB free initially** (650 GB leaves about
80 GB after maxfit). Check `df -h /Volumes/JW-EXT` before starting it. The
source stays intact for retry and reproducibility. No automatic deletion.

`maxfit`: routed experts 6-bit/group-64; every other weight bf16; the entire
102.4 GB PLE table bf16 on disk, mmap. `maxfit5` changes only routed experts
to 5-bit/group-64. Start at maxfit; 8-bit experts are already predicted not
to fit. Predicted peak at 40,960 tokens: 112.7 GB maxfit, 97.6 GB maxfit5;
default Metal working set approximately 115.4 GB. The probe clamps its
115.4e9-byte ceiling to the actual recommended working set; it never raises it.
All GB here are decimal; native reports also preserve exact byte counts.

Stop the native worker on **any** of:

- Swap usage nonzero before loading, any new `vm_stat` Swapouts (or a reset
  of that counter), pressure level other than normal (`1`), or
  `memory_pressure -Q` free percentage below 10%. The abort reason names
  which one fired. 128 GB here is 128 GiB = 137.4e9 bytes; the 10% floor
  leaves about 24.7e9 bytes beside a 112.7e9-byte Metal peak for macOS,
  apps and reclaimable cache, so a floor-only stop (no swap, kernel level
  1) at the 40,960 rung is plausible. It is still a stop and a headroom
  failure; record it as such for the lead. Never lower the floor to rescue
  maxfit. On the M4 Air an MLX 4 GiB Metal allocation moved this
  percentage by 22 points (25.8e9-byte machine), so it does track Metal.
- Compressor growth >2 GB, Metal peak above the effective ceiling, an
  allocation error, inability to sample/parse the memory monitors, or PLE
  resident file pages above 21.5 GB at a probe checkpoint.
- Failure of the 40,960-token Metal-peak prediction check (relative error
  >10%). A lower measured value can also indicate an accounting/model gap;
  explain it before accepting the memory model.

The parent watches system memory every two seconds during **load and work**;
it terminates the child, escalates after five seconds, and retains logs.
Metal/PLE checks occur at prefill/decode checkpoints in the memory probe;
other stages check PLE residency before/after work. This is an operational
abort bound, **not a hard macOS page-cache quota**. No claim of strict global
cache bounding is possible with mmap alone. The canonical pread/F_NOCACHE
alternative is a separate recipe change, not a silent Saturday substitution.

Metal allocations, sampled RSS and mincore's resident PLE file pages overlap
in unified memory: **never sum them**. The automated 10% check compares the
prediction to Metal allocation peak as a proxy. GOAL 6 still needs the lead's
resident-accounting review, including PLE pages, compressor and OS headroom.
Historical nonzero Swapouts alone are fine if initial live swap usage is zero
and the counter never changes. Do not disable swap or raise the wired limit.

## Ordered schedule (planning estimates, not observed throughput)

| Step | Budget | Required output / stop |
|---|---|---|
| Inventory, venv checks, native tiny tests | 20–45 min | correct Mac/disk, green native checks; no concurrent jobs |
| Pinned source download | 3–5 h | 360 GB; home link measured 267 Mbit/s down (33 MB/s, M4 Air Wi-Fi, 11-05 `networkQuality`) = 3.0 h at full link rate; Ethernet may be faster; resumable cache; hash receipt |
| Source SHA verification and maxfit conversion | 1–4 h | bounded streaming converter; source reverified; finished manifest |
| Ordinary SHA256SUMS + manifest verification | 10–40 min | external checksum sidecar + recorded manifest pin |
| Memory 4k → 16k → 40,960, 64 decode forwards | 15–90 min | zero new swap, normal pressure, fit + accounting review |
| Fixed texts, NLL, XML tool round trips | 20–90 min | PR #671 stage reports + human coherence review |
| Hosted bf16 fixed benchmarks + local comparison | 30–120 min | matching identity/items/template; reviewed disagreements |
| Speed at low/medium/xhigh, both chunk sizes | 1–4 h | warmup + 3 repeats per effort/context/chunk |
| PLE cache/I/O passes + report + eject | 15–45 min | post-load per-pass physical-disk counters and residency |

The rows sum to roughly 7–20 h, plus about 2–5 min per native command
(seven of them) to re-hash 211 GB and load about 109 GB of weights. Serial
source hashing runs near 2.4 GB/s (SHA-256, single thread, measured), so each
360 GB source verification is minutes, not hours. Expect probes to spill past
Saturday evening: start the download first thing, and do not arm a
measurement window Saturday night unless step 7's eject is complete. Stage
downloads in an earlier non-measurement daytime slot if necessary. A fallback conversion
adds another 1–4 h plus complete validation. Do not rush an unfinished gate
into a measurement window. The hash passes and full model verification also
consume real external I/O; their time is included, not claimed as PLE paging.

## 0. Operator setup and dry rehearsal

Run from this repository on the Mac, at the reviewed Saturday branch commit.
Use an already approved **validation venv** with `mlx==0.31.2`,
`mlx-lm==0.31.3`, `transformers==5.22.1`, numpy, jinja2 and huggingface_hub.
The reference venv uses transformers 5.22.1; a combined validation venv needs
that tokenizer version too. Do not install the repo's broad `[mac]` extra
over these pins (its transformers constraint differs). No runtime pin bump
or production measurement environment change is part of this task.

```sh
export PY="$PWD/.venv-qwen4exp/bin/python"  # operator's approved validation venv
export JW_REPO_ROOT="$PWD"
"$PY" -B -c 'import importlib.metadata as m; print({p:m.version(p) for p in ("mlx","mlx-lm","transformers","huggingface-hub","jinja2","torch")})'
sysctl vm.swapusage          # used must be 0.00M; otherwise reboot cleanly NOW, before the download
memory_pressure -Q | tail -1 # expect well above 10% on an idle Mac
launchctl list | grep -E 'com\.joulewise\.(night|b6loop|b6wake|magistrate)' || echo 'no joulewise agents loaded'
git rev-parse HEAD
git status --short --branch
sysctl -n hw.model hw.memsize  # expect Mac15,9 and 137438953472
diskutil list external physical
diskutil info /Volumes/JW-EXT
df -h /Volumes/JW-EXT
mdutil -s /Volumes/JW-EXT
sudo tmutil addexclusion -p /Volumes/JW-EXT  # already done if offload 9a enrolled this volume
tmutil isexcluded /Volumes/JW-EXT            # expect [Excluded]
```

Before any write, add JW-EXT to Spotlight Privacy (System Settings) and
confirm `mdutil -s` reports indexing disabled; confirm Time Machine excludes
it. Indexing 570 GB adds whole-disk I/O to the paging counters and can hold
the volume open at eject.

Verify the device is the SN7100/Express 1M2, attached by USB4, APFS, and has
the space above. Set `DISK` to its **physical whole disk**, not the APFS
synthesized disk; the paging script validates the APFS ancestry.

```sh
export DISK="$(diskutil info -plist /Volumes/JW-EXT | plutil -extract APFSPhysicalStores.0.APFSPhysicalStore raw -o - - | sed -E 's/s[0-9]+$//')"
diskutil info "$DISK" | grep -E 'Device / Media Name|Protocol|Internal|Disk Size'  # SN7100, USB, Internal: No
export BASE=/Volumes/JW-EXT/flashnext
export RUN="$BASE/evidence/20261107-maxfit"
export ARTIFACT="$BASE/models/maxfit"
export PROFILE=maxfit
export HF_HOME="$BASE/hf"
export HF_HUB_CACHE="$HF_HOME/hub"
export HF_XET_CACHE="$HF_HOME/xet"
export HF_XET_CHUNK_CACHE_SIZE_BYTES=0
export HF_XET_SHARD_CACHE_SIZE_LIMIT=1073741824
export TMPDIR="$BASE/tmp"
export TOKENIZERS_PARALLELISM=false
mkdir -p "$RUN" "$BASE/models" "$TMPDIR"
caffeinate -i -s &
export JW_CAFFEINATE_PID=$!

for stage in download convert memory quality benchmark hosted performance paging; do
  "$PY" -B scripts/qwen4exp_mbp_live.py "$stage" --dry-run
done
"$PY" -B scripts/qwen4exp_bf16_benchmark.py --dry-run
"$PY" -B scripts/qwen4exp_mbp_report.py --dry-run
```

If this shell is lost later (closed Terminal, logout), open a new one in the
repository, re-run the `PY`/`JW_REPO_ROOT` and JW-EXT `export` lines above
(not `mkdir`/`caffeinate` if caffeinate is still running), then re-derive
`SOURCE_RECEIPT`, `SOURCE`, `CONVERT_RECEIPT` and `PIN` with the commands in
step 1 from the receipts already written. Never re-run a completed command
with the same `--out`; it refuses.

Dry runs make no requests, read no artifacts, import no MLX and write no
results. They are command-plan checks, not validation evidence. Native tiny
tests below must run **outside the Codex sandbox** on the Mac. Run modules
one at a time; no full suite while sharing this machine.

```sh
"$PY" -B -m unittest tests.test_qwen4exp_mbp_live
"$PY" -B -m unittest tests.test_qwen4exp_e2e_eval
"$PY" -B -m unittest tests.test_qwen4exp_hosted_reference
```

Expected, as run natively on the M4 Air on 2026-11-05 (mlx 0.31.2, mlx-lm
0.31.3, transformers 5.22.1, torch 2.15.0, Metal): `test_qwen4exp_mbp_live`
32 tests OK, 0 skips (30 on 11-05 plus the two 11-06 download-resume tests); `test_qwen4exp_e2e_eval` 37 OK, 1 skip (item rebuild
needs `QWEN4EXP_ITEM_SOURCES`, fetched public sources; acceptable);
`test_qwen4exp_hosted_reference` 13 OK, 0 skips. Any other skip is OPEN.

The first includes canonical maxfit conversion + verified load + QSA/PLE
timed-cache smoke, the tiny hybrid timing check, and Darwin mincore. It
requires torch in the native test venv for the canonical fixture; any skip
is an OPEN check to resolve. No real model weights are involved. The reused
hosted-client fixture tests are separate; their local HTTP test need not run
on a machine where networking is prohibited.

## 1. Download, authenticate, convert

The download command is the only new script that fetches weights. It pins
the immutable revision, selects the 131 shards and tokenizer/config files,
uses two concurrent transfers, disables the Xet chunk cache, and caps the
Xet shard cache at 1 GiB. Inspect actual cache growth/free disk during a long
transfer; the Xet limit is a library cache limit, not a filesystem quota.
Partial transfers remain in the external cache for resumption.
`HF_HOME` on JW-EXT also moves the token lookup to `$HF_HOME/token`, which
does not exist. The pinned repo needs none if it is public; if `model_info`
answers 401/403, export `HF_TOKEN` from the existing login for this shell
only (never echo it) and rerun. Do not run `hf auth login`, which would
write a token onto JW-EXT. A fresh
receipt is written only after every file is authenticated: upstream LFS
SHA-256 for large files, upstream Git blob identity for small files, plus
ordinary SHA-256 for all files in the receipt. No unpinned Python is fetched.

```sh
"$PY" -B scripts/qwen4exp_mbp_live.py download --validation-only --plan-only --out "$RUN/download.plan.json"
"$PY" -B scripts/qwen4exp_mbp_live.py progress --metadata "$RUN/download.plan.json" \
  --run-dir "$RUN" --interval 60 --cutoff 2026-11-07T20:00:00Z &
PROGRESS_PID=$!
"$PY" -B scripts/qwen4exp_mbp_live.py download --validation-only --max-workers 2 --out "$RUN/download.json"
kill "$PROGRESS_PID" 2>/dev/null || true
export SOURCE_RECEIPT="$RUN/download.json"
```

The plan performs the single pinned `model_info` request and downloads no
payload. Progress imports neither MLX nor Hugging Face, makes no network call,
counts complete and `.incomplete` blob bytes plus the Xet cache, and appends
1/5/15-minute rates, ETA, and JW-EXT free space to
`download.progress.jsonl`. `ETA_PAST_CUTOFF` includes the four-hour conversion
budget and one-hour verify/eject margin. Download and conversion receipts, and
their `.attempt.json` failure sidecars, retain UTC start/finish, elapsed time,
bytes and mean MB/s. Before conversion, a full collecting check may be run as:

```sh
"$PY" -B scripts/qwen4exp_mbp_live.py verify-source --validation-only \
  --snapshot "$("$PY" -B -c 'import json,os; print(json.load(open(os.environ["SOURCE_RECEIPT"]))["snapshot"])')" \
  --metadata "$SOURCE_RECEIPT"
# Add --quarantine only to move bad cache blobs aside and unlink their snapshot links.
```

Set the source path from the completed receipt, then convert. The standalone
converter has no dry-run option; the wrapper provides planning and calls
`scripts/align_convert_qwen4_exp.py`'s `convert()` directly with the exact
maxfit/group-64/bf16-PLE options. It re-authenticates the source first.

```sh
export SOURCE="$("$PY" -B -c 'import json,os; print(json.load(open(os.environ["SOURCE_RECEIPT"]))["snapshot"])')"
"$PY" -B scripts/qwen4exp_mbp_live.py convert --validation-only \
  --source-receipt "$SOURCE_RECEIPT" --artifact "$ARTIFACT" --profile maxfit --out "$RUN/convert.json"
export CONVERT_RECEIPT="$RUN/convert.json"
export PIN="$("$PY" -B -c 'import json,os; print(json.load(open(os.environ["CONVERT_RECEIPT"]))["manifest_sha256"])')"
(cd "$ARTIFACT" && shasum -a 256 -c "$CONVERT_RECEIPT.SHA256SUMS")
```

Keep the recorded `PIN` independently with the run notes. Do not derive an
expected pin afresh from an artifact presented later. Converter format v2's
large-file digests are **SHA256 of concatenated 256 MiB chunk digests**, not
ordinary file SHA-256. `manifest.json` itself is small and its pin is ordinary
SHA-256. The wrapper additionally writes ordinary `convert.json.SHA256SUMS`
**outside** the strict artifact directory. Never add reports or sidecars
inside the artifact. On interruption preserve the partial directory and resume
the same artifact name (the evidence output name must still be new):

```sh
"$PY" -B scripts/qwen4exp_mbp_live.py convert --resume --validation-only \
  --source-receipt "$SOURCE_RECEIPT" --artifact "$ARTIFACT" --profile "$PROFILE" \
  --out "$RUN/convert-resumed.json"
export CONVERT_RECEIPT="$RUN/convert-resumed.json"
export PIN="$("$PY" -B -c 'import json,os; print(json.load(open(os.environ["CONVERT_RECEIPT"]))["manifest_sha256"])')"
(cd "$ARTIFACT" && shasum -a 256 -c "$CONVERT_RECEIPT.SHA256SUMS")
```

The interrupted attempt wrote no `convert.json`, so `CONVERT_RECEIPT` must
name the resumed receipt; every later step (and a shell re-entry) reads `PIN`
from it. A second interruption resumes again under another new name
(`convert-resumed-2.json`) and re-exports both. An interrupt after the
converter's manifest is written (including during the wrapper's
`SHA256SUMS` hashing) resumes without rewriting anything: the complete
manifest is re-verified against every payload digest and kept.

Resume re-authenticates the source receipt, module and converter pins and every
completed shard/PLE span before writing. A normal conversion error marks the
attempt failed; do **not** pass `--resume` then—preserve it and choose a new
artifact name. A changed profile, module, converter, pinned stack, source
receipt, grouping, PLE format, or shard plan is never resumable.
Conversion progress is appended outside the artifact at
`$RUN/convert.progress.jsonl` (a resumed run appends to the same file and
reports carried-over verified bytes as `bytes_resumed`). The converter script
SHA-256 for this kit is
`f06e3e01ac16da57ce1b79021b3095ce145faa22a86098792bf46b859ec3d389`.

Each native invocation below hashes the artifact once through the canonical
`load_verified_model` gate, pins the module and 0.31.x stack, then uses the
mlx-lm config `model_file` class contract with verified source bytes. It never
executes an unverified cache .pyc or an upstream community port.

## 2. Memory fit, strictly staged

```sh
"$PY" -B scripts/qwen4exp_mbp_live.py memory --validation-only \
  --artifact "$ARTIFACT" --manifest-sha256 "$PIN" --profile maxfit --out "$RUN/memory.json"
```

This uses fresh batch-1 full precision KV caches at final consumed contexts
4,096 / 16,384 / 40,960, including 64 decode forwards. Prompt lengths are
4,032 / 16,320 / 40,896; the first next-token selection belongs to prefill.
No padding, batching, KV quantization or all-40k logits materialization.
Prefill chunks are 512. Read `memory.json`, `.worker.json`, `.monitor.jsonl`,
`.worker.log` and `.rungs.jsonl`. Check the load peak as well as each rung.
Stopping midway makes the gate incomplete, even when lower rungs pass.

On a **memory/headroom** failure: stop, retain all evidence, release the
worker, let pressure settle, and use maxfit5. If swap was used, a clean reboot
may be necessary; never proceed with nonzero live swap. Do not change limits
to rescue maxfit. A quality failure is an investigation, not a reason to
silently select fewer bits.

```sh
# CONDITIONAL branch only, after a recorded maxfit memory failure:
export RUN="$BASE/evidence/20261107-maxfit5"
export ARTIFACT="$BASE/models/maxfit5"
export PROFILE=maxfit5
mkdir -p "$RUN"
cp -n "$SOURCE_RECEIPT" "$RUN/download.json"  # small evidence receipt, not weights
"$PY" -B scripts/qwen4exp_mbp_live.py convert --validation-only \
  --source-receipt "$SOURCE_RECEIPT" --artifact "$ARTIFACT" --profile maxfit5 --out "$RUN/convert.json"
export CONVERT_RECEIPT="$RUN/convert.json"  # resumed: as in step 1, convert-resumed.json
export PIN="$("$PY" -B -c 'import json,os; print(json.load(open(os.environ["CONVERT_RECEIPT"]))["manifest_sha256"])')"
(cd "$ARTIFACT" && shasum -a 256 -c "$CONVERT_RECEIPT.SHA256SUMS")
"$PY" -B scripts/qwen4exp_mbp_live.py memory --validation-only \
  --artifact "$ARTIFACT" --manifest-sha256 "$PIN" --profile maxfit5 --out "$RUN/memory.json"
```

For the remaining commands keep the selected profile. The setup set maxfit;
only the conditional fallback changes it. Do not mix reports.

```sh
printf '%s\n' "$PROFILE"
```

## 3. Fixed quality, NLL and XML tool round trips

```sh
"$PY" -B scripts/qwen4exp_mbp_live.py quality --validation-only \
  --artifact "$ARTIFACT" --manifest-sha256 "$PIN" --profile "$PROFILE" --out "$RUN/quality.json"
```

Reuses PR #671's pinned `e2e_items.json`, its official-template hash and
tokenizer-control-token preflight. Stages: greedy-vs-teacher-forced
consistency (including sparse QSA), six fixed natural texts plus shuffled
control NLL, eleven coherence items, sixteen XML tool items including two
tool-response round trips. Read the actual text, NLL per item, XML AST and
final answers, not only the overall verdict. All round-trip turns render
through the artifact's real `chat_template.jinja`; no JSON-only tool shim.
Thresholds and caveats are in [e2e_validation.md](e2e_validation.md).

The new maxfit/maxfit5 threshold labels deliberately use the existing strict
8-bit screening bounds, **PROVISIONAL** until real recipe drift is measured.
They are not a 6/5-bit error calibration. A passing screen alone cannot close
GOAL 7. Full-model hosted NLL is unavailable on text-only endpoints; keep that
relative-NLL check open unless an identical-weight scoring reference exists.

## 4. Same small benchmarks vs separately hosted bf16

Reuse the **exact** GSM8K first 30 items and IFEval first 25 checkable items
from #671, plus coherence/tool items in the reference report. Do not compare
a provider's published aggregate score to these selected items.

A separately operated/rented bf16 host is a prerequisite, not something
these scripts provision. A large multi-GPU vLLM host must load the official
revision, no quantization, bf16, full precision KV (`auto`), no MTP. Obtain
server command/version/logs and its authenticated checkpoint SHA-256 manifest.
Save an operator-verified receipt at `$RUN/bf16-identity.json` with these keys:

```json
{"repo":"Qwen/Qwen3.8-Flash-Next","revision":"de4b8e4d43b917e7706784d8bb445c9af86a3540",
 "dtype":"bfloat16","quantization":null,"kv_cache_dtype":"auto","mtp":false,
 "transformers":"5.22.1",
 "template_sha256":"c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041",
 "server_command":"FILL actual command","server_version":"FILL exact version",
 "checkpoint_sha256_manifest":"FILL retained manifest location + SHA256"}
```

Do not use the placeholders as evidence. HTTP cannot prove weight precision;
the report labels the identity **operator-attested**. Preserve server evidence.
The model ID alone, a Featherless FP8 endpoint, and Alibaba's proprietary
`qwen3.8-flash` do not establish the required bf16 comparison. If no verified
bf16 host is available, run local benchmarks without `--reference`, record
`reference missing`, and leave the comparison gate OPEN.

```sh
export BF16_ENDPOINT=https://OPERATOR-VERIFIED-HOST/v1
# Set VLLM_API_KEY in the environment if the host needs it; never paste it in logs.
"$PY" -B scripts/qwen4exp_bf16_benchmark.py --validation-only \
  --endpoint "$BF16_ENDPOINT" --tokenizer "$SOURCE" \
  --identity "$RUN/bf16-identity.json" --out "$RUN/bf16-benchmark.json"
"$PY" -B scripts/qwen4exp_mbp_live.py benchmark --validation-only \
  --artifact "$ARTIFACT" --manifest-sha256 "$PIN" --profile "$PROFILE" \
  --reference "$RUN/bf16-benchmark.json" --out "$RUN/benchmark.json"
```

Requests send the real template's token IDs, greedy decoding, neutral
penalties, and explicit stop IDs. Item/template/harness hashes, bf16 identity
receipt and complete item coverage must match before local comparison.
PR #671 reports per-item text/pass agreement informationally; the lead must
review disagreements and truncations. Exact greedy text identity across
quantized and bf16 models is not an acceptance requirement.

Optional logprobs use #671's existing client. This collection is separate
from the identical-item benchmark above and sends only fixed public prompts.
Use it only in the non-measurement validation slot with the verified host:

```sh
"$PY" -B scripts/qwen4exp_hosted_reference.py plan --provider vllm-selfhost --base-url "$BF16_ENDPOINT"
"$PY" -B scripts/qwen4exp_hosted_reference.py collect --provider vllm-selfhost \
  --base-url "$BF16_ENDPOINT" --live --max-cost-usd 0.25 --traces "$RUN/bf16-traces.jsonl"
"$PY" -B scripts/qwen4exp_mbp_live.py hosted --validation-only \
  --artifact "$ARTIFACT" --manifest-sha256 "$PIN" --profile "$PROFILE" \
  --provider vllm-selfhost --reference "$RUN/bf16-benchmark.json" \
  --traces "$RUN/bf16-traces.jsonl" --out "$RUN/hosted.json"
```

`hosted` only reads retained traces; it makes no requests. Teacher forcing
measures top-1, top-k overlap, chosen-token Δlogprob and bucketed KL (a lower
bound on full KL). If logprobs are missing, preserve the explicit text-only
outcome; never claim a top-k pass. `plan` and `collect` without `--live` are
the existing harness's dry-run mechanisms; they have no `--dry-run` flag.

## 5. Prefill/decode at every supported reasoning effort

```sh
"$PY" -B scripts/qwen4exp_mbp_live.py performance --validation-only \
  --artifact "$ARTIFACT" --manifest-sha256 "$PIN" --profile "$PROFILE" \
  --prefill-step 512 --out "$RUN/performance-512.json"
"$PY" -B scripts/qwen4exp_mbp_live.py performance --validation-only \
  --artifact "$ARTIFACT" --manifest-sha256 "$PIN" --profile "$PROFILE" \
  --prefill-step 2048 --out "$RUN/performance-2048.json"
```

Each command runs all 3 contexts × **low/medium/xhigh** (the real template's
supported efforts), one warmup and three timed repeats per cell. It renders
the thinking template, fills a fixed-token prose prompt while preserving
template prefix/suffix, synchronizes MLX on every timing boundary and times
64 decode forwards. EOS is deliberately ignored to hold work constant;
generated token IDs/text are retained. All reasoning tokens count. These
are controlled throughput probes, not complete reasoning-task latency or
reasoning-quality scores. Quality checks separately exercise thinking closure.

P5 / PR #670 targets: prefill >=400 tok/s at chunk 512, >=550 at chunk 2048;
decode >=30 tok/s, stretch 40. They were extrapolated for an older e3 recipe
on M3 Max; **maxfit's heavier bf16 core/6-bit experts may miss them**. Record
the medians against the targets and retain raw repeats, cache state, prompt
counts, output counts, Metal peak and monitoring overhead. Do not change the
recipe to win speed. A 2048-chunk memory abort does not invalidate a clean
512 fit, but it leaves that performance configuration unsupported.

## 6. PLE paging and physical external I/O

```sh
"$PY" -B scripts/qwen4exp_mbp_live.py paging --validation-only \
  --artifact "$ARTIFACT" --manifest-sha256 "$PIN" --profile "$PROFILE" \
  --disk-device "$DISK" --out "$RUN/paging.json"
```

This loads/validates first, then runs the identical 4k token workload twice.
Each pass has its **own post-load** `iostat -Id` before/after files; whole
artifact hashing and weight loading are outside those intervals. Compute
the cumulative physical-disk MB difference and divide by snapshot elapsed
time for aggregate throughput. Record other activity on that disk; this is
a whole-device upper bound on workload I/O, not an exclusive PLE byte count.
The script verifies external/physical/whole disk and APFS store ancestry.

Each pass also records PLE gather lookups, deduplicated rows, gather seconds,
major/minor faults, ru_inblock and `mincore` resident pages. Table gather
faults/time help attribute paging; faults are not bytes, row bytes are not
physical traffic, and mmap resident bytes do not measure total OS cache.
The first pass's cache state is **unknown**, the second is a warm repeat.
The converter's hash gate uses F_NOCACHE, but previous probes still warm PLE.
For a defensible cold comparison, operator-eject/remount or reboot cleanly
outside measurement, start a fresh paging output, record initial residency
and show that it was low. Eject/remount alone may not evict all pages. Do not
run `purge`, clear caches in an energy window, or claim a cold run from timing.

## 7. Fill results, preserve evidence, eject and unplug

```sh
"$PY" -B scripts/qwen4exp_mbp_report.py --run-dir "$RUN" --out "$RUN/results.md"
git rev-parse HEAD > "$RUN/code-commit.txt"
(cd "$RUN" && find . -maxdepth 1 -type f ! -name EVIDENCE.SHA256SUMS -print0 | sort -z \
  | xargs -0 shasum -a 256 > EVIDENCE.SHA256SUMS)
# Copy the small evidence (never weights) to the internal disk before eject;
# the borrowed SSD leaves the Mac. Include a maxfit run dir if maxfit5 ran.
export EVIDENCE_COPY=/Users/edr/code/flashnext-evidence-20261107
mkdir -p "$EVIDENCE_COPY"
ditto "$BASE/evidence" "$EVIDENCE_COPY/evidence"
(cd "$EVIDENCE_COPY/evidence/$(basename "$RUN")" && shasum -a 256 -c EVIDENCE.SHA256SUMS)
```

The `find` form avoids zsh's "no matches found" abort and also hashes the
`convert*.json.SHA256SUMS` and `paging.json.iostat-*` sidecars.

The report fills [the results template](mbp_live_results_template.md) from
fixed evidence filenames. Missing checks stay PENDING; no GOAL is auto-closed.
Complete the human review fields and record the final evidence digest after
that review. Keep raw JSON/journals/logs immutable. If a probe aborts, do not
reuse its basename; use a new run directory for a fresh complete attempt.
Append the [GOAL status-log template](mbp_live_goal_entry_template.md) only
after the lead reviews actual outputs. Keep GOAL 11 full gold evidence separate.

```sh
# All Python workers, shell CWDs and file viewers must have released JW-EXT.
cd "$JW_REPO_ROOT"
kill "$JW_CAFFEINATE_PID"
sync
lsof +f -- /Volumes/JW-EXT   # must print nothing; close any holder first
```

Then close this shell (it still exports `TMPDIR` and `HF_*` paths on JW-EXT)
and, in a **new** shell, eject through the offload operation so the census
evidence is recorded (offload §15 "each day the SSD is used"):

```sh
export JW_OP=/Users/edr/night-archive/mbp-offload-20261107
export JW_STEPS=/EXACT/REVIEWED/STEPS/DIR   # the same directory used for run A
zsh -f -euo pipefail "$JW_STEPS/step13-eject.zsh"
zsh -f -euo pipefail "$JW_STEPS/step13-ejected-census.zsh"   # must report bus-layer refusal
# Now PHYSICALLY UNPLUG the enclosure and its cable.
zsh -f -euo pipefail "$JW_STEPS/step13-unplugged-census.zsh" # must pass
df -h | grep JW-EXT || echo 'JW-EXT gone'
```

Without an offload operation, use `diskutil eject /Volumes/JW-EXT`, unplug,
and confirm `df` no longer lists it. Then hand the
Mac back to the lead's clean measurement-window procedure. No measurement
starts until validation has ended, agents are gone, and normal quiet-machine
checks pass. No result in this bundle is an energy measurement.
