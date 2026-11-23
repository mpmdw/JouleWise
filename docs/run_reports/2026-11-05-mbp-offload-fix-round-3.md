# MBP offload, fix round 3: Opus data-safety re-review N1–N8

Task: fix every code/runbook item listed under "Before Saturday 2026-11-07" in
the Opus 5.5 xhigh re-review of PR #665 at `75c3d5dd7` (verdict
SAFE_WITH_FIXES). Branch `lane/2026-11-05-mbp-offload-runbook`. Authored and
verified natively on the analysis MacBook Air (macOS 15.7.9, Python 3.13).
RUN_STATE.md was not edited; the item text Ed/the lead should commit is below.

## Per-finding fixes and evidence

| # | Fix | Evidence |
|---|---|---|
| N1 HIGH: process census missed real processes | `busy_processes(comm, args, executables)` combines three untruncated views: `ps -axww -o pid=,comm=` (comm last), `ps -axww -o pid=,args=` (args last), and the kernel executable path from libproc `proc_pidpath`. It matches by basename (also stripping `.py/.sh/.js`), by agent path component (`claude`, `claude-code`, `codex`), and by `python -m` module components. The names now cover agents, the watchdog, ledger-pin, R0 checks, run_night, harvest*, mlx_lm, the guard and the tar/zstd/pzstd/gtar/rsync/cp/ditto/dd writers. Only PIDs leave the function. | **Native** `NativeProcessCensusTests` (7) spawn real processes under a >200-character temp path. A compiled sleeper at `.../claude/versions/2.1.99` is launched via a `claude` symlink, by bare argv0 `claude`, and with a disguised argv0 (only `proc_pidpath` can see that one). The class also spawns a symlinked `claude` shell script, a >250-character `codex` binary, a long-path `magistrate_watchdog.py`, `python -m fakepkg.harvest_b5`, and real Homebrew `zstd` and `/usr/bin/tar`. All are detected; a benign long-path sleeper is not. **Mutation check:** the same native class run against the old `75c3d5dd7` census fails 6 of the 6 detection tests. Synthetic rows reproduce every row the review listed as missed; the fake-list tests are kept and updated. |
| N2 HIGH: ejected-but-plugged enclosure invisible | `external_volume_census.py` v2 adds a bus layer. system_profiler `SPThunderboltDataType SPUSBDataType SPUSBHostDataType SPNVMeDataType` nodes and ioreg `IOThunderboltSwitch`, `IOUSBHostDevice` and `IOBlockStorageDevice` entries are reduced to identity digests, with volatile link, speed, power and BSD numbering excluded. These are compared as a multiset with an **unplugged baseline**. `--record-baseline … --attest-unplugged` writes the baseline exclusively and refuses unless the volume layer is clean and no detachable NVMe drive is present. The census refuses when the baseline is missing, the digest is wrong, the baseline came from another Mac (platform-UUID digest), the sections changed, or any extra device appears. Serials and the UUID are stored only as digests. Runbook: step2b records the baseline before the SSD is ever plugged in; `step13-ejected-census.zsh` is the native acceptance test (after `diskutil eject` and BEFORE unplug it must refuse, specifically on the bus layer); `step13-unplugged-census.zsh` must then pass; every pre-arm call passes `--baseline`. | Fixture tests (19 in the module) cover: ejected-but-plugged USB4 (receptacle, device node and switch), USB-mode enclosure, each bus signal alone, a duplicated device, mounted (both layers), the full Saturday state sequence, volatile-only changes (stay clean), redaction, binding/format refusals and the CLI record-then-pinned flow. **Native:** this laptop's real bus inventory is stable across reads. Attaching an unmounted APFS image in a temp dir adds an `ioreg:IOBlockStorageDevice` row; after detach the inventory is clean again. |
| N3 MEDIUM: case-variant pilot bypass | `/Users/edr/night-align` is in `MANDATORY_KEEP` and in the §4 KEEP list. Every mandatory root, and **every existing** `/Users/edr/night-*`, `jw-b5-*` and `jw_models` directory, must be in KEEP **by inode**. The pilot rule is now inode-keyed: nothing under night-align, by any spelling, is deletable, and it is checked before KEEP. | **Native** on case-insensitive APFS: the review's S2 case (`NIGHT-ALIGN/pilot-v7-…` listed in `approved-models.txt`, receipts bound to that spelling) now refuses with `pilot roots retained`. With the pilot check disabled it still refuses with `KEEP inode overlap`. An unlisted `night-new-lane`/`NIGHT-Other`/`jw-b5-analysis` refuses until it is kept. |
| N4 MEDIUM: Saturday script aborted | The run is split into COPY-ONLY run A (runbook §15, drivers A1/A2/A3) and run B (later). Step 2 records an absent crontab in `crontab-absent.txt`; any other failure is still a STOP. `step2-pause.zsh` is idempotent: it accepts only its own existing STOP (`cmp`), records already-absent jobs and still disables them, and uninstalls the night agent only if it is loaded. Step 9a runs **unguarded** after `sudo -v`. Run A contains pilots 8–10 through step6-item/step6-ssd, then the §7a rows. Each §7a row is verified against its **original authenticated digest** in iCloud and on the SSD copy, and then evicted (poll dataless) before the next row. No parser and no per-format verifier are needed (N9). `jw_wait_dataless` takes a size-scaled attempt limit (N6 timeout). Run A ends: eject, ejected census (must refuse), unplug, census (must pass). Cloud steps 5/7, step 3, W1 and step 8 are run B. | `test_align_offload_runbook` (11) checks: run A contains no step3/5/7-cloud/7b/8/9-budget/delete; 9a is unguarded; the order is 9a → copies → 7a → eject → ejected census; the crontab and STOP idempotency; 7a digest, then copy, then digest, then evict; every census call is pinned. All 34 zsh fences pass `zsh -n` and every Python heredoc parses. **Native emulation:** the crontab block on a crontab-less Mac records the absence and exits 0; `jw_wait_dataless` handles size-scaled, default and invalid limits. |
| R0 patch (lead ruling) | `docs/align/r0_disk_gate_patch.md` and `tests/test_align_offload_r0_patch.py` are deleted. The runbook states that R0 is report-only and needs no offload (v4 ruling 6, `origin/lane/2026-11-05-align-v4-wp4-r0` @ 82cca4295). The step-3 R0 inventories became W1-only and conditional, §7b is withdrawn, and the §9b budget is now W1's 80 GB + journal (the `2*w1+30 GB` gate is removed). | Runbook test `test_r0_patch_withdrawn_and_r0_is_report_only`. |
| N7 LOW-MEDIUM: disk image as second copy | `physical_external()`: the volume, its APFS physical store and that store's whole disk must all be `Internal=false` on USB/PCI-Express/PCI/Thunderbolt, not `Virtual`, and not MediaName `Disk Image`. `independent_copy` and the new pinned `delete_root.py volume-check --media` (now `jw_external_check`) enforce it, with the whole-disk MediaName enrolled at 9a. The new read-only `step9a-identify.zsh` shows Ed the bus and media before enrolment. | **Native:** a real APFS sparse image mounted from a temp dir passes every legacy check (`Internal=False`, apfs, MountPoint) and now refuses as `not on physical external`. 12 synthetic variants also refuse (image at volume/store/whole level, Virtual, Internal, Apple Fabric, unknown bus, malformed stores/parent). USB, Thunderbolt and PCI-Express pass. The identify fence, run natively on the image, prints `Disk Image`. |
| N8 LOW: Ctrl-C left no row | The audit handler catches `BaseException`. In `delete`, SIGTERM and SIGHUP raise `KeyboardInterrupt`; the CLI exits 130. | KeyboardInterrupt and SystemExit during rmtree each journal `FAILED_PARTIAL` after `DELETE_AUTHORIZED`, keep the pending pointer and never write `DELETED`. |
| N11 (cheap, done) | Step 2 pins delete_root, disk guard, model_keep and the census into `$JW_OP` with one hash file; later steps run only those copies. | Runbook test. |

Not done (run B by design): N5 (a real `fileproviderctl` or NSURL parser needs
native samples) and the remaining N6 items (admitting archive size rather than
source size in step7-cloud, the step-7 resume skip), plus N9's optional
member/restore check of the 7a rows, N10 (moot: patch withdrawn) and N12.

## Test results (native, unittest, Python 3.13.18)

| Module | Tests | Native tests inside |
|---|---|---|
| `tests.test_align_offload_delete_root` | 66 OK | 7 process-census spawns, 2 case-variant APFS, 1 uchg |
| `tests.test_align_offload_second_copy` | 12 OK | 1 real disk image |
| `tests.test_external_volume_census` | 19 OK | 1 real bus inventory + attached image |
| `tests.test_align_offload_runbook` | 11 OK | zsh -n on all fences |
| `tests.test_align_offload_disk_guard` | 7 OK | process groups |
| `tests.test_align_offload_model_keep` | 4 OK | — |
| `tests.test_align_offload_public_weights` | 5 OK | — |
| **Total** | **124 OK, 0 skipped**, about 16 s | |

The `r0_patch` module (4 tests) was removed with the withdrawn patch.
`git diff --check` is clean. All fixtures stayed under TemporaryDirectory or
the session scratchpad. No real `night-*`, `jw-b5-*`, restricted path or home
listing was touched; the tests patch `HOME`.

## RUN_STATE item text (for the lead to commit; next free item number)

> **N. Laptop lead, 2026-11-0X: MacBook Pro offload pause (Saturday
> 2026-11-07) and the mandatory pre-arm external census.** Authority: PR #665,
> `docs/align/mbp_offload_and_gold_setup.md` §§13 and 15 at the reviewed
> commit; Opus data-safety re-review SAFE_WITH_FIXES and its fix round 3.
> (a) On Saturday Ed runs only the COPY-ONLY run A (§15). While the operation
> STOP file `/Users/edr/night-custody/magistrate/STOP` (text beginning
> `ALIGN paused for MBP offload and gold validation;`) exists, **or** while
> the borrowed SN7100/OWC SSD is attached to the MacBook Pro in any form
> (mounted, unmounted, or ejected but still plugged in), no R0, R1, ALIGN
> window, desk session, plan install or arm may start on the MacBook Pro. The
> magistrate never removes, rewrites or bypasses that STOP; only Ed removes it
> (§13 item 4). (b) From now on, **every** R0, R1, ALIGN or other measurement
> arm, install or desk session on the MacBook Pro, including the forthcoming
> v4 follow-up item that allows headless R0 by day, first runs the pinned
> `external_volume_census.py --baseline <bus-baseline.json> --baseline-sha256
> <sha>` immediately before arming, with a fresh receipt path kept with the
> arm record, and refuses on any nonzero exit. A missing baseline is a
> refusal. The baseline is the one Saturday's step 2b records at
> `/Users/edr/night-archive/mbp-offload-20261107/bus-baseline.json`, with the
> SHA-256 in `bus-baseline.sha256`; the lead records both values in a
> follow-up line. (c) Pilots 8–10 (`pilot-v7-20261105T015948Z`,
> `pilot-v8-20261105T102850Z`, `pilot-v9-20261105T231016Z`) stay retained on
> the MacBook Pro under the item-26 capture-retention rule. The SSD copies add
> redundancy and authorize no deletion; `offload.py` never runs on them.
> (d) Cloud upload/round trip, W1 offloads and any deletion belong to the
> later run B, each behind its own reviewed gate.

## Decisions for Ed

1. **Pilot deletion retention ruling.** Do pilots 8–10, including the capture
   dirs bound to pins 620, 630 and the pilot-10 pin, stay until block-5
   release? Or may they leave the MBP once both an SSD copy and a
   server-confirmed iCloud copy are verified? The default is retain, and
   Saturday needs no ruling. The review's evidence prerequisites (ledger
   locator list, issuing-mode custody behavior, the pilots 0–7 precedent)
   apply before any deletion.
2. **Borrowed SSD.** Is it already APFS, or does its owner permit an erase or
   an added APFS volume? No format command is supplied. On Saturday, record
   its VolumeUUID and whole-disk MediaName from `step9a-identify` and set the
   Spotlight Privacy exclusion.
3. **Baseline cabling.** Record the bus baseline with the charger/KM003C path
   and any measurement-time USB device in their measurement ports, and keep
   that cabling for every window. Moving a cable can make the census refuse
   (safe, but blocking).
4. **No agents on the MBP during run A.** Quit the Claude desktop app and any
   Claude Code or Codex session: the stricter census treats any of them as
   busy.
