# Opus 5.5 xhigh data-safety re-review: PR #665 @ 75c3d5dd7 (lane/2026-11-05-mbp-offload-runbook)

## Verdict: SAFE_WITH_FIXES

- **Deletion is data-safe as written.** No path in the runbook or in `delete_root.py` can delete pilots 8–10, any model root, or any mandatory-KEEP tree. B1, H1, H2, H4 and H6 (as a design) are fixed in the code, and I confirmed this by running it.
- **Saturday copy-only work is data-safe** (SSD copy plus restore verification). I ran the runbook's own step-6 fences end to end through the guard against a mounted synthetic APFS volume, and they pass.
- **Not safe yet:**
  - The H3 process census does not work on real macOS `ps` output (N1).
  - The pre-arm external census cannot see an enclosure that is ejected but still plugged in (N2).
  - The pilot-retention check can be bypassed with a case variant of the path (N3).
  - The Saturday script as given will abort before it makes any SSD copy (N4–N6).
- **Do not unblock deletion until N1 and N3 are fixed.** Do not rely on the census for R0 or R1 until N2 is fixed.

**Method.**
- Read every changed file. Ran all 8 test modules: 91/91 pass (unittest, Python 3.13).
- Built two harnesses in `/private/tmp/claude-501/-Users-edr-code-CapstoneProject-JouleWise/359dce51-5c68-4ddf-a271-1a0232d75749/scratchpad/adv/`:
  - `adv.py`: real tar, zstd, `tar -xpf`, diskutil, `ls -le`, chflags, ACLs and hardlinks against a mounted 100 GB sparse APFS image at `/Volumes/JWTESTSSD`. Only the unpinned upload parser and the launchctl/sudo pause check were mocked.
  - `emu.py`: extracts the runbook fences verbatim, redirects only the `/Users/edr` paths into scratch, and runs them in the Saturday order through the guard.
- Fixtures included 0444, 0600 and 0755 files, 0700 directories, 140-character names, a symlink created under umask 077, dangling absolute links, uchg, ACLs, hardlinks, case variants, interrupts, `env -i` fresh shells and mistyped paths.
- Nothing touched `/Users/edr/jw-b5-*`, `/Users/edr/night-*` or any `restricted/` path. `git show`/`log` read the clone's object store, which sits behind the `jw-b5-analysis` alternates; this was read-only. I did not fetch, push or comment.

## Original findings: was each fixed?

| # | Fixed? | Evidence |
|---|---|---|
| B1 | YES | Steps are files run with `zsh -f -euo pipefail`; `env.zsh` is hash-checked. I ran env generation, the `functions` serialization of the heredoc functions, and errexit on a failing `[[ ]]`. Deletion runs as one Python program. An `env -i` fresh-shell CLI run refuses on its own (`missing mandatory KEEP`, exit 1, REFUSED_NO_DELETE row). |
| H1 | YES | Items 170, 171 and 174 forbid offload.py. `delete_root` refuses any `pilot-v*` child of night-align (S3 refused) and the public-weights class (CLI refused). |
| H2 | YES | Items 170–174 are on cached main f193a320; STOP-2 asserts them. |
| H3 | **PARTIAL → N1** | The lock-owner, DESK_DONE, pin and PILOT gates exist. The `ps` census misses the processes it was meant to catch (see N1). |
| H4 | YES (stricter) | `jw_models` and the HF hub are mandatory KEEP with no exemption, so no model can be deleted. `model_keep` census tests pass. |
| H5 | YES, with a hole (N3) | Pilot and `instrument_validation` refusals work (S2b, S3). A case-variant spelling bypasses the pilot check. |
| H6 | DESIGN YES / operationally BLOCKED | Evict, then poll dataless, then download, then poll not-dataless, then rehash plus member stream; both upload checks repeat before rmtree. The parser is unpinned and cannot work as scaffolded (N5). |
| H7 | PARTIAL | Inventories are moved before offload and the conflict is flagged STOP. Three problems remain: R0 is still blocked by space (~66 GB < 80 GB + journal); `r0_disk_gate_patch.md` targets the stale base 49e78e17, so patch 1 no longer applies to the R0 tip f14cba8fd; the current R0 `inventory()` refuses symlinks, so step 3 refuses on pilot view links. |
| M1 | PARTIAL → N3 | Inode/ancestor overlap verified: S10 (KEEP lists a case variant of the source) refused. Exact-path checks work. The pilot check is still a string comparison. |
| M2 | YES (weak) | Both receipts must contain src, manifest SHA and archive SHA. This is substring containment; attribution and UTC are not checked. |
| M3 | YES | The guard ran natively and SIGSTOPs the group. Caveats: daemon-side `brctl` hydration cannot be stopped (admission still covers it); guarded writers have no tty (N4). |
| M4 | YES | Dataless files are refused before open, read or decompression (code and tests). Not exercised natively; I could not create provider-dataless files safely. |
| M5 | YES for env/HF | Re-running step2 or step6-item refuses (`mkdir` exists). Step 7 has no resume path (N5). |
| M6 | PARTIAL | §7a exists but cannot run Saturday: it starts with the unpinned `jw_uploaded`, requires per-row "original verifier" files that do not exist, and has no evict step (N6, N9). |
| M7, M8, M9 | YES | Documented. |
| L1–L5, L7–L12 | YES | Natively verified: uchg (S4) and ACL (S5) refusals, hardlink refusal (S6), `.OFFLOADED.json` plus both journal rows (S1), a KEEP symlink target survives rmtree (S1). |
| L6 | YES | `crontab -l` aborts step 2 on a Mac with no crontab (N4). |

## New findings

**N1 HIGH: the process census does not work on real macOS.**
- `busy_processes` parses `ps -axo pid=,comm=,args=`. macOS truncates any non-last `comm` column to 16 characters, so the full path becomes something like `/opt/homebrew/bi` or `/Users/edr/.loca`.
- Tested live:
  - MISSED: a native-layout `…/claude/versions/2.1.99` binary, the same binary launched through a `claude` symlink (as the watchdog launches `~/.local/bin/claude`), a long-path `codex`, and Homebrew `zstd` in a running `tar|zstd`.
  - Also MISSED (synthetic rows): npm/node-hosted claude, `magistrate_watchdog.py`, `advance_b5_ledger_pin.py`, `align_r0_checks.py`, `python -m …harvest`, rsync, cp, ditto, pzstd and gtar.
- The unit tests pass only because their fixtures use untruncated `'123 claude'`.
- This breaks H3's guarantee (no surviving setsid magistrate child) in three places: the step-2 pre-pause check, the final check inside `delete_root`, and step 13.
- Fix:
  - Read the executable from a separate `ps -axo pid=,comm=` call where `comm` is the last column, or use libproc `proc_pidpath`. Read arguments from `ps -axww -o pid=,args=`.
  - Match argv tokens for `claude`, `codex`, `magistrate_watchdog`, `advance_b5_ledger_pin`, `align_r0_checks`, `run_night`, `harvest` and `mlx_lm`. Exporting only PIDs is still fine.
  - Add a native test that spawns a long-path `…/claude/versions/X` sleeper.

**N2 HIGH (measurement integrity): the external census cannot see an ejected-but-plugged enclosure, and nothing calls it.**
- The runbook itself names an ejected but still plugged-in enclosure as the energy confound.
- `diskutil eject` removes the media, so `diskutil list external` and `mount` go clean while the USB4/NVMe bridge stays powered on the bus. Step 13 orders eject → unplug → census, so a forgotten unplug passes the census.
- What I verified: the census refuses a mounted image and an attached-but-unmounted image.
- The census is also only document text. There is no RUN_STATE directive, and `arm_census.py`, `run_night.py` and the R0 runner do not call it.
- Fix:
  - Also inventory the bus devices (`system_profiler -json SPThunderboltDataType SPUSBHostDataType SPNVMeDataType` or ioreg) against a baseline taken while unplugged, and refuse any extra device.
  - Saturday native acceptance test: after `diskutil eject` and BEFORE unplugging, the census must exit nonzero.

**N3 MEDIUM: case-variant bypass of pilot retention (demonstrated).**
- `pilot = src.parent == ALIGN_ROOT and re.fullmatch(...)` compares paths case-sensitively. `exact_path` does not canonicalize case on case-insensitive APFS.
- In S2, `<root>/NIGHT-ALIGN/pilot-v7-20261105T015948Z` was listed in `approved-models.txt`, with receipts bound to that spelling. The real `night-align/pilot-v7…` root was DELETED (journal shows DELETE_AUTHORIZED, then DELETED; the pointer was published).
- Only the `instrument_validation` name heuristic remains, and it stopped the variant only when that directory existed (S2b).
- The existing "case variant" test (`test_case_variant_allowed_parent_refuses`) refuses only because `approved-models.txt` does not list the variant.
- Fix: add `/Users/edr/night-align` to `MANDATORY_KEEP` and the §4 KEEP list, so inode overlap catches it. Any future ruled pilot deletion should use an inode-keyed exact allowlist.

**N4 MEDIUM (Saturday-blocking): the single-file Saturday sequence aborts before any SSD copy.**
- (a) Step 2 exits at `crontab -l` when there is no crontab (demonstrated: "crontab: no crontab for edr"). Step 2 cannot then be re-run because `JW_OP` exists.
- (b) Step 9a is run via `guarded`, and the guard starts writers in a new session with no controlling tty. I demonstrated `/dev/tty` gives ENXIO, so `sudo tmutil addexclusion` cannot prompt.
- (c) Step 3 needs the reviewed v4 kit, amendment-1 and v4 R0 config refs, plus an R0 build that records symlinks. None of these exist yet.
- (d) `step5-roundtrip` always fails (unpinned parser) and runs before step 6.
- Expect related trouble in `step2-pause`: it is non-idempotent once STOP exists, and the night-agent uninstall was already done by the magistrate after pilot 10.

**N5 MEDIUM: the cloud parser cannot simply be pinned, and step 7 is not resumable.**
- `parse_uploaded` requires the whole `fileproviderctl evaluate` stdout to equal a fixed 3-line string. Real output is a per-item property dump (`evaluate <item>` "evaluate finder actions and decorations"), so "recording a sample" cannot make it pass. A real parser must be written.
- A documented alternative: the NSURL ubiquitous-item keys (`NSURLUbiquitousItemIsUploadedKey`, `…IsUploadingKey`, `…UploadingErrorKey`, `…HasUnresolvedConflictsKey`, `…DownloadingStatusKey`) via `osascript -l JavaScript`. I prototyped this; it returns null for non-iCloud files, which must refuse.
- Step 7 resume: the first parser refusal leaves the copied archive (~20–36 GB) resident in the iCloud folder. Re-running fails at `test ! -e`, and a `-retryNN` ID forces a whole new SSD copy as well (emulated).

**N6 MEDIUM: internal space at ~66 GB free.**
- `step7-cloud` admits the *uncompressed* `source.json` bound for an archive that is already compressed. Pilot 10 needs about 36 GB + 30 GB, roughly all free space.
- Hydrated archives are kept resident "through deletion", and there is no evict step for pilots or for 7a rows. So the second and third items fail admission.
- `wait_dataless` has a fixed 20-minute cap, which times out on a 20 GB re-download below about 140 Mbit/s.
- Fix: admit the actual archive plus manifest size; add `brctl evict` + `jw_wait_dataless yes` after each verified round trip and each 7a row; scale the timeout from step-5 throughput; make step 7 skip the copy when the destination already matches `archive.sha256`.

**N7 LOW-MEDIUM: a disk image on the internal SSD passes as the "independent" second copy (demonstrated).**
- An hdiutil APFS image reports `Internal=false`, `FilesystemType=apfs`, `BusProtocol='Disk Image'`. It passes both `jw_external_check` and `independent_copy` (S9), and then deletion proceeds.
- Fix: refuse `BusProtocol == 'Disk Image'`, and enroll the SSD's physical identity (media name and serial from SPNVMeDataType/SPThunderboltDataType) in addition to the VolumeUUID.

**N8 LOW: interrupt during deletion leaves no FAILED_PARTIAL row.** A Ctrl-C (KeyboardInterrupt) or SIGTERM during rmtree leaves only DELETE_AUTHORIZED, because the handler catches `Exception` only (S7). The pending pointer survives and a rerun refuses (`predelete source mismatch`), so recovery still works. Fix: catch BaseException for the audit row, or mask SIGINT around rmtree.

**N9 LOW: §7a is over-gated.** For a pure copy of an existing iCloud archive, matching the original authenticated archive and manifest SHA-256 proves the SSD copy is as good as the iCloud one. `jw_uploaded` on a source that is only being read, and a mandatory per-format verifier, block M6 with no safety gain. Make member/restore checks optional or later.

**N10 LOW: R0 patch inconsistencies.** `r0_disk_gate_patch.md` says there is no flat 80 GB threshold, while the runbook enforces `max(80 GB, 2·W1+30 GB)+journal`. The R0 tip f14cba8fd uses `80 GB + journal_bytes_estimate` and `anchor_source`. The R0 lead must reconcile these and rebase the patches.

**N11 LOW: only `delete_root.py` is hash-pinned.** The guard, census and model_keep scripts run from the mutable `$JW_CANON` tree, and step 2's census runs before anything is pinned. Fix: copy and hash all four scripts into `$JW_OP` at step 2.

**N12 LOW: miscellaneous.**
- The `JouleWise-backup/` restored trees have no `.metadata_never_index`, so the SSD relies on Ed setting Spotlight Privacy by hand.
- `delete_root`'s `sudo -n launchctl list` needs a fresh sudo timestamp (it fails closed).
- Receipt binding is substring-based, so a path prefix can be ambiguous.

## The three open items Sol flagged: what each needs

1. **"Pilot deletion remains blocked pending retention authority"** needs a ruling from Ed:
   - **The ruling:** a decision_log entry plus a RUN_STATE item amending the item-26 capture-retention rule (historically line 45) for exactly `pilot-v7-20261105T015948Z`, `pilot-v8-20261105T102850Z` and `pilot-v9-20261105T231016Z`. It must say whether these roots, including the capture dirs bound to ledger pins 620, 630 and the pilot-10 pin, may leave the MBP before block-5 release once the SSD copy and a server-confirmed iCloud copy are both verified.
   - **Evidence before ruling:** a structure-only list of every B5-ledger custody locator under each root. The lead must also establish how issuing-mode custody (`calibration_ledger.py:2368–2375`, `_custody_probe_paths(root, mode="issuing")`, which returns `LEDGER_CUSTODY_INVALID`) behaves if those locators disappear. Pilots 0–7 are a precedent: they were deleted by offload.py and pins 620 and 630 still issued afterwards, so establish why.
   - **If any locator lies under a root:** either the ruling also adds an offloaded-custody mechanism to the ledger, or that subtree stays.
   - **After the ruling:**
     - a reviewed `delete_root` change that replaces the blanket pilot and `instrument_validation` refusals with an exact, inode-keyed allowlist of ruled roots, with N3 fixed first;
     - a new pinned `JW_OFFLOAD_CODE_COMMIT`;
     - a `retention-review.json` per root.
   - **Why it matters:** without this ruling no reclaim exists, and R0 stays blocked at ~66 GB < 80 GB + journal.
2. **"Cloud verification requires a reviewed native parser sample"** needs a native capture on the MBP plus a reviewed parser rewrite:
   - **Capture:** after the pilot-10 desk and pin, by day, with no SSD needed, run step 5's 256 MiB synthetic probe. Capture `fileproviderctl evaluate` stdout, stderr and exit code, plus `sw_vers`, in three states: uploaded, mid-upload, and evicted/dataless.
   - **Parser:** the lead replaces the whole-output-equality scaffold with a real field parser, or switches to the NSURL ubiquitous keys. It must refuse unknown, missing or duplicate fields, `isUploading=1`, any upload error and any conflict. Tests are built on those samples; then review, merge and pin.
   - **Until then:** steps 5 and 7, the cloud part of 7a, and all deletion stay STOP. That is acceptable for a copy-only Saturday.
3. **"R0 … unplugged-SSD copy checks"** needs a ruling from the R0 lead / window-council chair:
   - **The conflict:** R0's `disk_census` (`r0_host.py` on f14cba8fd, around lines 159–171) live-inventories `offloads[].destination` and requires pilot8 and pilot9 to pass. `complete_r0` requires the `disk` check in the same `live_desk` run as the energy checks. So copies kept on a day-only SSD can never satisfy R0 while it is unplugged.
   - **What to rule:** either (a) drop the `offloads` coverage requirement, because the pilots are retained on the internal disk so nothing was offloaded; or (b) accept a daytime copy-verification receipt bound to the SSD VolumeUUID and the inventory SHAs, and keep only the internal free-space check live.
   - **Also needed:**
     - rebase the patch series onto f14cba8fd, because patch 1 is stale;
     - apply the symlink-recording inventory patch, otherwise step 3 `--inventory` refuses on pilot view links;
     - accept that R0 stays blocked by free space (~66 GB) whatever is decided here, until item 1 or another reviewed space source.

## Exactly what must happen before Saturday 2026-11-07

1. **Fix and re-test N1** (process census) and **N3** (add `/Users/edr/night-align` to `MANDATORY_KEEP` and the KEEP list), each with native tests.
2. **Fix N2:** add a bus-device census, and plan the eject-but-plugged native acceptance test for Saturday.
3. **Lead commits a RUN_STATE item** stating:
   - the MBP offload pause for Saturday, with no R0, R1, window or desk while the operation STOP exists or the SSD is attached; this must also bind the forthcoming v4 follow-up item that allows headless R0 by day;
   - every R0, R1 or window arm runs the fixed `external_volume_census.py` immediately before arming and refuses on a nonzero exit;
   - pilots 8–10 stay retained.
4. **Split the Saturday script.**
   - **(A) Copy-only, Saturday:** step 1; step 2 with the crontab absence recorded rather than aborting; step2-pause written to tolerate already-absent jobs; step 9a run *unguarded*, or `sudo -v` plus no tty-dependent sudo inside the guard; step6-tool; step6-item and step6-ssd for pilot8, pilot9 and pilot10; step 7a SSD copies by authenticated-digest match, one row at a time with evict after each; then the eject-before-unplug census test; step 13 eject; physical unplug; census.
   - **(B) Later:** cloud steps 5 and 7, after the parser pin and the N6 fixes. R0 step 3 and 7b, after the R0 ruling and ref pins. These can run any day because the sources are retained.
5. **Integrate the reviewed fix commit on the MBP.** The canonical checkout must contain the commit object, and `JW_OFFLOAD_CODE_COMMIT` is set to its full SHA. Pin the guard, census and model_keep scripts alongside `delete_root.py` (N11). Confirm `python3.13`, `zstd`, `tmux` and `caffeinate` on the MBP.
6. **Ed:**
   - confirm the borrowed SN7100 is APFS, or get the owner's permission to erase it or add an APFS volume; no format command is supplied;
   - record its VolumeUUID and its physical identity (N7);
   - set the Spotlight Privacy exclusion.
7. **Lead or Ed builds the M6 row list** before Saturday:
   - exact iCloud paths for ALIGN 0–7 (`JouleWise-archive/2026-11-04-align-pilots`), BYTES H/H2 (`JouleWise-archive/2026-10-25-disk3/`) and R7 A343/P0/READY;
   - the authenticated archive and manifest SHA-256s, from `~/night-archive/icloud-offload-2026-10-05/`, `/Users/edr/night-bytes/*.icloud-pointer`, and the pilot `.OFFLOADED.json` pointers and manifests;
   - per-row sizes; each hydration must fit within about (internal free − 30 GB) ≈ 36 GB.
8. **Friday by day (Ed or the magistrate, structure-only):** a feasibility probe per pilot root, counting hardlinks (`-links +1`), unreadable or non-owned files, special files, nested mounts, dataless flags and restricted/withheld name components, plus total bytes. Any hit means step 6 will STOP for that root.
9. **Optional but recommended (unblocks B early):** capture the `fileproviderctl` samples on the MBP on Friday (open item 2), so the lead can land the parser.

**Bottom line:** the copy-only Saturday is safe once items 1–8 are done. Deletion stays correctly impossible until the retention ruling, N1, N3 and the parser are all landed and reviewed.
