# Saturday 2026-11-07 operator card: offload run A and Flash-Next live kit on the MBP

**Pinned commits**
- **Flash-Next kit:** `lane/2026-11-07-qwen4exp-mbp-live` @ `97d780d59`. The model module hashes to `f4ec75d16f0a…`. It is byte-identical to canonical `65763077a` and to the gold adapter `6f079f132`.
- **Offload run A:** `lane/2026-11-05-mbp-offload-runbook` (PR #665) @ `d38ad49d5b1c4d214ea6926dfaacddcf1a6fba21`.
- **Flash-Next cell amendment (draft, not adopted):** `lane/2026-11-06-align-flashnext-cell-draft` @ `f2943c272`.

**Defaults on this card.** Each one is an answer to an Ed question below. If Ed answers differently, use the alternative given there.
- ALIGN v4 R1 runs **Friday night**.
- **Parallel order:** the download starts right after step 9a and runs alongside A2's copies. The SSD is ejected once, at the end of the day.
- **No bf16 host.** `benchmark` runs without `--reference`, so the bf16 comparison stays OPEN.

**Roles**
- **Ed (Mac)** is at the measurement MBP.
- **Magistrate** is the launchd agent `com.joulewise.magistrate`. It keeps `/Users/edr/code/JouleWise` fast-forwarded to main.
- **Lead (laptop)** is the M4 Air. It runs no MLX and dispatches the Sol jobs.

---

## 1. Timeline

### Friday evening prep (2026-11-06)

**F1 · lead (laptop) · 30 min: PR #665 CI and the step files**
- Watch CI on PR #665 at `d38ad49d5`. Shards 2, 7 and 10 have not been seen green yet; shard 4 is fixed.
- Review the fix commit: runbook §2 and §15, the census name list, and the tests.
- Give Ed the step-file bundle to review: `/private/tmp/claude-501/-Users-edr-code-CapstoneProject-JouleWise/359dce51-5c68-4ddf-a271-1a0232d75749/scratchpad/jw-steps-d38ad49d5/`, with its `SHA256SUMS.txt`.
- Remove the stray `answer.md` from the lane before any merge.
- Expected: all shards green, and `JW_OFFLOAD_CODE_COMMIT=d38ad49d5b1c4d214ea6926dfaacddcf1a6fba21` confirmed (or the head after review).

**F2 · lead (laptop) · 60 min: freeze the Gate S bars**
- Review the Amendment 3 draft.
- Get an Opus 5.5 non-author review and a Fable cold pass of the pre-registered Gate S bars (§1-3).
- Ed acknowledges the bars before any Saturday result file is opened.
- Expected: Gate S frozen before Saturday's data exist. The draft stays not adopted.

**F3 · lead (laptop): give the kit lane a PR**
- `lane/2026-11-07-qwen4exp-mbp-live` has no PR, so CI has never run on it. Open one at `97d780d59` so CI runs and the Saturday commit is frozen.

**F4 · lead dispatches Sol, then reviews: Saturday software**
- Run MISSING-2, MISSING-3, MISSING-1, MISSING-4 and MISSING-5a, plus F15. Details are in §4.
- **Rebase all of them onto `97d780d59`, not `6cacb2be5`.** Their specs name `6cacb2be5`, but the kit lane has since gained the download-resume fix in `qwen4exp_mbp_live.py`.
- Any change that lands on the Saturday commit means Ed must pull it and the native tests must re-pass in S9.
- MISSING-5a changes the converter digest, so the new sha256 has to be recorded in `mbp_live.md`.
- Recommended: nothing reviewed by T0, nothing new on the Saturday commit. Saturday then runs on `97d780d59` as is.

**F5 · Ed (Mac, by day, before any R1 arm) · 15 min: fetch and check the Mac**
```
git -C /Users/edr/code/JouleWise fetch origin lane/2026-11-05-mbp-offload-runbook lane/2026-11-07-qwen4exp-mbp-live
command -v python3.13 zstd tmux
git -C /Users/edr/code/JouleWise show d38ad49d5:scripts/external_volume_census.py | python3.13 -I -B -
grep -cE '^17[0-4]\.' /Users/edr/code/JouleWise/RUN_STATE.md
```
- Expected: both commits present and all three tools found.
- The census command is read-only. It exits 1 because the baseline does not exist yet; its JSON must show `external_device_ids []` and `refused_mounts []`. Any mounted DMG or simulator volume blocks the baseline.
- The grep count must be 5.

**F6 · Ed (Mac, by day) · 30 min: step files and environments**
- Create `JW_STEPS=/Users/edr/night-archive/mbp-offload-20261107-steps`. It must not be inside JW_OP. Put the 16 reviewed step files in it.
- Edit `step2.zsh` to set:
  - `JW_RECORDS=/Users/edr/code/JouleWise`
  - `JW_P9_PILOT=/Users/edr/night-archive/seats-cf1baad2/pilots/p9-PILOT.json`
  - `JW_P10_PILOT=/Users/edr/night-archive/seats-cf1baad2/pilots/p10-PILOT.json`
  - the chosen `JW_P9_PIN` and `JW_P10_PIN` (see question Q6)
  - `JW_OFFLOAD_CODE_COMMIT`
- Write `rows/*.zsh` only where the original archive digests exist (Q7).
- Set up the kit checkout at `97d780d59` and `.venv-qwen4exp` (mlx 0.31.2, mlx-lm 0.31.3, transformers 5.22.1, torch) if they are missing. Package installs only, no weights.
- Expected: a reviewed step directory and zero or more reviewed row files.

**F7 · magistrate: Friday night R1 (default)**
- Offload run A starts Saturday only after R1's terminal record, its desk, the agent uninstall and the magistrate exiting.
- Otherwise step 2-pause would try to uninstall a loaded night agent using the old pilot2 checkout's script.

---

### Saturday: parallel order (default)

T0 is 08:00-09:00, and only once a Friday R1 is terminal, desked and uninstalled. Clock times below assume T0 = 08:00. Do not run an interactive Claude or Codex session on the Mac.

**S1 · T0 (08:00) · Ed (Mac, SSD NOT plugged in) · 10 min: quiet the Mac**
- Quit the Claude desktop app, Claude Code and Codex.
- Run `sysctl vm.swapusage`. If any swap is in use, reboot now.
- Cable the charger and the KM003C exactly as for a window.
- Then run:
```
tmux new -s offload
caffeinate -dimsu &
export JW_STEPS=/Users/edr/night-archive/mbp-offload-20261107-steps JW_OP=/Users/edr/night-archive/mbp-offload-20261107
```
- Expected: a clean, quiet Mac with zero swap and no agents.

**S2 · T0+10 · Ed · 10 min: steps 1 and 2**
```
zsh -f -euo pipefail $JW_STEPS/step1.zsh      # review STOP 1
zsh -f -euo pipefail $JW_STEPS/step2.zsh      # on its own
```
- Expected: Mac15,9, 128 GB, about 80 GB free.
- Step 2 prints PASS, lists the plists it found, and writes `$JW_OP/step2.done`.

**S3 · T0+20 · Ed · 5 min: job targets**
- Write `$JW_OP/job-targets.txt` with:
  - `gui/501/com.joulewise.magistrate`, `.night` and `.night.deadman`
  - every `com.joulewise.*` job step 2 discovered (quiet-kit, b6loop, b6wake.*, and so on)
- Never include `local.jwbench.keepawake`.
- Expected: a non-empty, reviewed list.

**S4 · T0+25 · Ed · 15 min: A1 and the bus baseline**
```
zsh -f -euo pipefail $JW_STEPS/saturday-A1.zsh
```
- Step 2 is skipped because `step2.done` exists. Enter the sudo password when asked (it is for the system `launchctl` list).
- Send the `bus-baseline.sha256` value to the lead.
- Expected: our STOP is in place and every `com.joulewise.*` job is absent or disabled. **The magistrate is booted out here.** The baseline is recorded, the fresh census passes, and the script prints `A1 done. Only NOW plug in the SSD`.

**S5 · after S4 · lead (laptop) · 20 min: census RUN_STATE item**
- Commit the round-3 RUN_STATE item for the pre-arm external census, with the bus-baseline path and SHA-256, plus the v4 follow-up item.
- Expected: the census item exists. Without it there is no §13 item-4 go and no arm.

**S6 · T0+40 (08:40) · Ed · 15 min: plug in and name the SSD**
- Plug the SSD into a fixed port that is not the charger's or the KM003C's.
```
diskutil list external physical; ls /Volumes
```
- Name the volume JW-EXT according to Q1. Any rename, added volume or erase must happen before step 9a.
  - **Add a volume** (non-destructive, recommended):
    ```
    diskutil apfs addVolume "$(diskutil info -plist "$OLDVOL" | plutil -extract APFSContainerReference raw -o - -)" APFS JW-EXT
    ```
  - **Rename** (only if the lender agrees): `diskutil rename "$OLDVOL" JW-EXT`
  - **HFS+:** run `diskutil apfs convert <diskNsM>`, then rename. Copy off anything the lender needs first.
  - **exFAT, FAT, NTFS, unformatted or unreadable:** the only path is an erase, which destroys everything on the disk. It needs the lender's explicit consent, and Ed runs it himself:
    ```
    diskutil list external physical
    export EXTDISK=diskN          # SN7100 whole disk, ~2.0 TB, external USB; never disk0
    diskutil info "$EXTDISK"      # recheck media name, protocol, Internal: No
    diskutil eraseDisk APFS JW-EXT GPT "$EXTDISK"
    diskutil info /Volumes/JW-EXT
    ```
  - Use plain APFS: not case-sensitive, not encrypted.
- Immediately add `/Volumes/JW-EXT` to Spotlight Privacy, then confirm `mdutil -s /Volumes/JW-EXT` shows indexing disabled.
- Expected: `diskutil info /Volumes/JW-EXT` shows APFS mounted exactly at `/Volumes/JW-EXT`. A volume that mounts as "JW-EXT 1" is refused.
- Free space in `df`:
  - The offload audit wants **≥900 GB** for both jobs.
  - The kit alone refuses below **650 GB**, and wants about **800 GB** if the maxfit5 fallback is to stay possible.
  - The reports give no combined figure for offload plus maxfit5.

**S7 · T0+55 · Ed · 10 min: step 9a**
```
JW_EXTERNAL=/Volumes/JW-EXT zsh -f -euo pipefail $JW_STEPS/step9a-identify.zsh
```
- Write `JW_EXTERNAL`, `JW_EXTERNAL_UUID` and `JW_EXTERNAL_MEDIA` into `saturday-A2.zsh`.
- **Parallel order:** delete A2's last three lines (step13-eject, step13-ejected-census and the print).
- Expected: bus is USB, Thunderbolt or PCI-Express; Internal is False; no "Disk Image".

**S8 · T0+65 (09:05) · Ed, tmux window 1 · ~120 min: A2 copies**
```
zsh -f -euo pipefail $JW_STEPS/saturday-A2.zsh
```
- This runs `sudo -v`, then step 9a (Time Machine exclusion and external-env), then the guarded step6-item and step6-ssd for pilots 8, 9 and 10, then the 7a rows one at a time.
- Expected:
  - `pilot{8,9,10}/ssd.sha256` and `independent-copy.json`
  - `existing-<row>.json` for each row
  - sources unchanged (the source-after `cmp`)
- Timing: about 10-15 min per pilot. The 7a rows depend on the link (about 61 GB for H/H2). Any single archive over about 50 GB fails internal admission (about 80 GB free with the 30 GB floor).

**S9 · T0+70, alongside A2 · Ed, tmux window 2 · 45 min: kit step 0**
- Run this only after A1 has finished, so the test processes cannot trip A1's census.
- From the kit checkout at `97d780d59`:
```
export PY=<approved venv python> JW_REPO_ROOT=$PWD
# version check; then:
sysctl vm.swapusage
memory_pressure -Q
# launchctl grep (no joulewise agents)
git rev-parse HEAD
sysctl -n hw.model hw.memsize
# source the offload env and external-env; run jw_external_check
# mbp_live.md step 0 JW-EXT part: diskutil / df / mdutil
sudo tmutil addexclusion -p /Volumes/JW-EXT
# derive DISK; export BASE/RUN/ARTIFACT/PROFILE/HF_*/TMPDIR; mkdir
caffeinate -i -s &
# all --dry-run commands; then the 3 unittest modules one at a time
```
- Expected:
  - mlx 0.31.2, mlx-lm 0.31.3, transformers 5.22.1
  - swap used 0.00M
  - `Mac15,9` and `137438953472`
  - no joulewise agents
  - the external check passes and the folder shows `[Excluded]`
  - DISK is the SN7100 whole disk (USB, Internal: No)
  - every dry run prints JSON with `dry_run` true
  - tests: `test_qwen4exp_mbp_live` 32 OK with 0 skips; `test_qwen4exp_e2e_eval` 37 OK with 1 skip; `test_qwen4exp_hosted_reference` 13 OK with 0 skips
- The offload audit's "30" for the first module is from before the two new tests were added.

**S10 · T0+1h55 (~09:55) · Ed, window 2 · 180-300 min: download**
```
"$PY" -B scripts/qwen4exp_mbp_live.py download --validation-only --out "$RUN/download.json"
export SOURCE_RECEIPT="$RUN/download.json"
```
- If the download is interrupted, re-run it with a **new** `--out`, such as `download-2.json`. Partial blobs count toward the space check.
- Expected: about 360 GB in 131 shards, taking 3-5 h at about 33 MB/s (about 3.0 h at full link rate). The receipt verifies the upstream LFS/blob identity.
- Check the rate 15 minutes in. The kit has no rate tool until MISSING-2 lands.

  | Rate | Action |
  |---|---|
  | ≥30 MB/s | Stay on plan |
  | 15-30 MB/s | Keep going; start conversion only if ≥5 h remain before the cutoff |
  | <15 MB/s | Switch to Ethernet and keep downloading (it resumes); no conversion today |

- A 401 or 403 means exporting `HF_TOKEN` in that shell.
- A shard digest mismatch stops the download at the first bad file, and there is no repair path (MISSING-2c).
- **While the download runs** (no weights needed):
  - The kernel bench at real dimensions (`--other-bits bf16 --expert-bits 6/6`, perf.md §9 steps 1-3). It exists only on `lane/2026-11-05-qwen4exp-port-perf`, so extract it with `git show` into `$BASE/tmp`.
  - If MISSING-1 has landed: `memory --synthetic` and `performance --synthetic --prefill-step 512`. Results are stamped SYNTHETIC; the real-weight run stays the gate.

**S11 · ~T0+3h05 · Ed: A2 finishes**
- Nothing to do. In the parallel order A2 does not eject.

**S12 · after download (~13:00-15:00) · Ed · 70-280 min: convert**
- Export `SOURCE` from the receipt, then:
```
"$PY" -B scripts/qwen4exp_mbp_live.py convert --validation-only --source-receipt "$SOURCE_RECEIPT" --artifact "$ARTIFACT" --profile maxfit --out "$RUN/convert.json"
# export CONVERT_RECEIPT and PIN
(cd "$ARTIFACT" && shasum -a 256 -c "$RUN/convert.json.SHA256SUMS")
# write PIN in the run notes
```
- Expected: 1-4 h for conversion plus 10-40 min for the checksum check; every file OK; about 211 GB for maxfit. At least 240 GB must be free at the start.
- **Conversion cannot resume.** Start it only if at least 5 h remain before the cutoff, and never let it overlap an eject or a window.
- If the cutoff arrives mid-run: kill it, keep the partial folder, eject, and restart under a new name another day.

**S13 · after convert · Ed · 15-90 min: memory gate**
- A2 must be long finished and nothing else running.
```
"$PY" -B scripts/qwen4exp_mbp_live.py memory --validation-only --artifact "$ARTIFACT" --manifest-sha256 "$PIN" --profile maxfit --out "$RUN/memory.json"
```
- Expected: verdict completed; the 4k, 16k and 40,960 contexts all run; zero new swap; pressure level 1; at least 10% free; Metal peak within 10% of 112.7 GB (the ceiling is 115.4 GB).
- What to do with each outcome:

  | Outcome | Action |
  |---|---|
  | All three pass and the prediction is within 10% | PROFILE=maxfit; skip maxfit5 |
  | Fits, but the prediction misses by more than 10% | Keep maxfit; GOAL 6 stays open until the memory breakdown (MISSING-4) explains the gap |
  | Free-percentage-only stop (no swap, pressure level 1) | Counts as a headroom failure: go to maxfit5; keep the maxfit evidence; never lower the floor |
  | Swap, pressure, compressor, Metal-cap or allocation stop | maxfit5; reboot first if swap is in use |
  | PLE-cap stop | maxfit5 does not help. Stop; the pread variant (MISSING-8) is for another day |

- **maxfit5 fallback:** convert (adds about 200 GB and 1-4 h, and the 5 h rule applies), then rerun the memory test (predicted peak 97.6 GB).
  - The conversion refuses below 225 GB free, and only about 80 GB is left if the day started with 650 GB.
  - If maxfit5 passes, use PROFILE=maxfit5 for everything after. If it also fails, STOP: there is no fallback today.
- **If R1 runs Saturday night:** this is the hard stop. Go straight to S18 so the eject is done by about 20:00. Each later probe re-checks the model against its recorded PIN on another day.

**S14 · Ed · 20-90 min: quality**
```
"$PY" -B scripts/qwen4exp_mbp_live.py quality ... --profile "$PROFILE" --out "$RUN/quality.json"
```
- Expected: per-stage reports for consistency, NLL, coherence and XML tools. A person reads the actual text.
- A failed screen means investigating, not dropping to fewer bits.

**S15 · Ed · 30-120 min: benchmark**
- Default: run mbp_live `benchmark` **without** `--reference`. Expected output: `reference missing; comparison gate OPEN`.
- Only if a verified bf16 host exists: run `qwen4exp_bf16_benchmark.py`, then mbp_live `benchmark --reference`, then hosted `plan` and `collect --live`. Expected: identity, items and template all match.

**S16 · ~20:00 (or a later day) · Ed · 60-240 min: performance**
```
"$PY" -B scripts/qwen4exp_mbp_live.py performance --prefill-step 512 --out "$RUN/performance-512.json"
"$PY" -B scripts/qwen4exp_mbp_live.py performance --prefill-step 2048 --out "$RUN/performance-2048.json"
```
- Expected: medians per context and effort, recorded against the targets of ≥400/550 tok/s prefill and ≥30 tok/s decode (advisory for maxfit).
- Record any miss, and do not change the recipe to win speed.
- If 2048 aborts but 512 is clean, only 512 is supported.

**S17 · Ed · 15-45 min: paging**
```
"$PY" -B scripts/qwen4exp_mbp_live.py paging --disk-device "$DISK" --out "$RUN/paging.json"
```
- Expected: two 4k passes, each with before/after iostat files and residency.
- A slow cold pass with a fine warm pass is expected. If the warm pass is also slow, investigate.

**S18 · end of day, and by about 20:00 if R1 runs Saturday · Ed · 20 min: evidence, eject, census**
- Kit §7:
  - run `qwen4exp_mbp_report.py`
  - write `code-commit.txt`
  - write the find-based `EVIDENCE.SHA256SUMS`
  - `ditto` the evidence to `/Users/edr/code/flashnext-evidence-20261107`, then `shasum -c`
  - kill caffeinate
  - check that `lsof +f -- /Volumes/JW-EXT` is empty
- Then, in a **new** shell:
```
step13-eject.zsh
step13-ejected-census.zsh      # must REFUSE at the bus layer
# physically unplug the enclosure and the cable
step13-unplugged-census.zsh    # this equals A3
```
- Expected: the copy verifies OK; the ejected census refuses at the bus layer (N2 acceptance); the unplugged census passes; JW-EXT no longer shows in `df`.
- **If the ejected census passes, STOP.** No window may rely on the census.
- Keep the converted model and the source on the SSD.

### Saturday alternative: the kit's written order (if Ed declines parallel in Q3)

This adds about 1.5-2.5 h and one extra unplug and replug.

1. **S7** without deleting any lines from A2.
2. **A2 in full · ~60 min:** it ends with `A2 done. Now physically unplug` after the ejected census refuses at the bus layer.
3. **Physically unplug, then · 5 min:** `zsh -f -euo pipefail saturday-A3.zsh`. Expected: `A3 done: unplugged census PASS`.
4. **Plug the SSD back in.** Do S9, then continue from S10.

---

### Saturday night: handover to R1/W1

**H1 · lead (laptop) · 60 min: evidence review**
- Pull the evidence from the Mac's internal copy.
- Review the memory accounting (GOAL 6), the quality text and XML (GOAL 7), and the speed and paging results (GOAL 8).
- Fill in the human-review fields and append the GOAL entry template.
- GOAL 11 gold stays separate; it is the laptop streamed run (PR #680, pid 3097).

**H2 · lead (laptop) · 30 min: Gate S verdict** (only if F15 has landed)
- Run `qwen4exp_gate_s.py` on the copied run directory and record ADMIT-CANDIDATE, NOT ADMITTED or INCOMPLETE.
- If ADMIT-CANDIDATE, open the disk decision (E1) with Ed using a live `df`.

**H3 · lead:** confirm the S5 census RUN_STATE item and the v4 follow-up item are committed.

**H4 · Ed (Mac): §13 item-4 go**
- `cmp` our STOP, remove the STOP, then enable and bootstrap the magistrate.
- Allowed only after H3 and with the SSD unplugged (`step13-unplugged-census` PASS). The offload STOP otherwise blocks R0 and R1.

**H5 · magistrate:** restored. It arms R1 (if it runs Saturday night) or the next window W1 (v4 Window 1 plan, PR #679). There is no arm before the census item exists and the SSD is unplugged.

---

## 2. Blockers

| # | Blocker | Owner | When |
|---|---|---|---|
| B1 | **The SSD's format and name are unknown.** The kit accepts only APFS mounted exactly at `/Volumes/JW-EXT`, so any other volume makes every live command refuse. No erase is authorized. Renaming or adding the volume must happen before step 9a. | Ed (+ lender) | Sat S6 |
| B2 | **The bus baseline must be recorded before the SSD is ever plugged in.** Otherwise the baseline's claim that the SSD was never attached is false. Record it with A1/step2b even if the rest of offload is not ready. | Ed | Sat S4 |
| B3 | **CI on PR #665 head `d38ad49d5` is not green yet** (shards 2, 7 and 10 not yet seen green). After that, review the fix commit and set `JW_OFFLOAD_CODE_COMMIT`. | Lead | Fri |
| B4 | **No file is chosen for `JW_P9_PIN` or `JW_P10_PIN`.** step2 requires an existing file. The candidates are the DESK_DONE files holding pins 4b77e09c6 and 4ab3b6e25. | Ed or lead | Fri |
| B5 | **The Mac needs a fetch of both lanes** (F5). Without it, step 2's cat-file check stops. | Ed | Fri |
| B6 | **The Mac's python3.13, zstd and tmux are unverified, and the volume-layer census must show `refused_mounts=[]` and `external_device_ids=[]`.** | Ed | Fri |
| B7 | **Ed still has to write the operator files:** `JW_STEPS` (16 reviewed files), the `step2.zsh` edits, `job-targets.txt`, the `saturday-A2.zsh` edits and the row files. | Ed | Fri/Sat |
| B8 | **The 7a archive rows have no source of record.** If none exists, use zero row files; M6 stays open. | Ed (Q7) | Fri |
| B9 | **The kit checkout at `97d780d59` and `.venv-qwen4exp` on the Mac are unverified.** | Ed | Fri |
| B10 | **The kit lane has no PR, so CI has never run.** Its native tests have run only on the M4 Air. | Lead | Fri |
| B11 | **The native MLX tests have not run yet:** 4 in `test_qwen4exp_mbp_live` and 7 in `test_qwen4exp_e2e_eval` were skipped on the laptop. They must pass natively in S9. | Ed | Sat S9 |
| B12 | **No bf16 reference exists.** There is no verified vLLM host and no `$RUN/bf16-identity.json`, so the comparison stays OPEN. The two ways to close it are MISSING-6/F13 and MISSING-7. | Ed (Q4); lead | Sat+ |
| B13 | **The kit takes 7-20 h after the download starts, and conversion cannot resume.** A Saturday-night R1 makes the memory gate the hard stop, with the eject by about 20:00. | Ed (Q2) | Sat |
| B14 | **The offload STOP stays in place after A3/S18 and blocks R0/R1.** Lifting it needs the lead's census RUN_STATE item (with the baseline SHA-256) plus the v4 follow-up item, then Ed's §13 item-4 go. | Lead, then Ed | Sat night |
| B15 | **The model does not fit on internal disk for ALIGN windows.** maxfit needs about 293 GB free (maxfit5 about 278 GB) against about 66 GB today. Even after deleting both dropped models and freeing pilots 8-10, it is still about 35 GB short (about 20 GB for maxfit5). The pilot-retention ruling (run B) is pending. | Ed (E1) | Post-Sat |
| B16 | **The Gate S bars must be frozen before any Saturday result file is opened.** | Lead + Ed | Fri |
| B17 | **The model card's thinking sampler settings are not recorded anywhere.** Copy them from the pinned README (rev de4b8e4d) before R0-FN. | Lead | Before R0-FN |
| B18 | **Tokenizer equivalence between transformers 5.12.1 and 5.22.1 is unverified** (F14). | Lead/Sol | Before R0-FN |
| B19 | **Unverified whether the Flash-Next template reads `reasoning_content` the way the Qwen3.8-27B template does.** | Lead | Before R0-FN |
| B20 | **The lookup table is read one row at a time.** If R0-FN-b shows these reads take more than 15% of prefill, a batched read is needed, which means a new module hash and requalification. | Lead | R0-FN-b |
| B21 | **A stray `answer.md` sits at the root of the offload lane.** Remove it before merge. | Lead | Before merge |
| B22 | **The MISSING-* specs are based on stale `6cacb2be5`.** Rebase them onto `97d780d59`, or the download-resume fix is lost. | Lead | Fri |

---

## 3. Questions only Ed can answer (deduplicated)

### Needed before Saturday

**Q1. SSD format and name.** Is the borrowed SN7100 already APFS? If it is, may we add a separate APFS volume named JW-EXT to its container? If it is not APFS, does the lender consent to `eraseDisk`, which destroys everything on it?
- **Default:** add a volume (non-destructive, keeps the lender's files separate). Rename only with the lender's OK. Erase only with explicit consent. If it is not APFS and there is no consent, stop.

**Q2. When does ALIGN v4 R1 run?** Friday night or Saturday night, and if Saturday, what is the hard cutoff?
- **Default:** Friday night. With a Saturday night, the eject must be done by about 20:00, no conversion may start within 5 h of the cutoff, and Ed must give the §13 item-4 go.

**Q3. Order of the day.** Start the download right after step 9a, alongside A2, with one eject at day end? Or keep the kit's written order (A2, unplug, plug back in, then download)?
- **Default:** parallel. It saves about 1.5-2.5 h.

**Q4. bf16 reference.** Is a verified bf16 vLLM host available Saturday (official revision, no quantization, KV cache auto, no MTP)? Or should we rent an 8×80 GB host?
- **Default:** no rental. Use the gold-stream reference (MISSING-6/F13; same question as E4), and run `benchmark` without `--reference`.

**Q5. Internal evidence copy.** Is `/Users/edr/code/flashnext-evidence-20261107` on the Mac acceptable as the internal copy of the small evidence files before the SSD leaves?
- **Default:** yes.

**Q6. Pin receipt files.** Which exact files should `JW_P9_PIN` and `JW_P10_PIN` point to?
- **Default:** the pilot-v8 and pilot-v9 DESK_DONE files, which hold pins 4b77e09c6 and 4ab3b6e25.

**Q7. 7a archive rows.** Do the `.OFFLOADED.json` pointers for pilots 0-7 and the H/H2 `*.icloud-pointer.txt` files record a whole-archive SHA-256 and an iCloud manifest path? Check the key names only, on the Mac.
- **Default:** if they don't, use zero row files. M6 stays open.

**Q8. Kit checkout and venv.** Do `.venv-qwen4exp` and a kit checkout at `97d780d59` already exist on the Mac?
- **Default:** if not, build them Friday by day. Package installs only, no weights.

**Q9. Wired Ethernet.** Can the MBP be on wired Ethernet on Saturday?
- **Default:** yes if possible. The plan assumes 33 MB/s Wi-Fi.

**Q10. Gate S acknowledgment.** Will you acknowledge the pre-registered Gate S bars before any Saturday result file is opened?
- **Default:** yes. Acknowledge them Friday.

### Flash-Next cell (after Saturday)

**E1. Internal disk for the 210 GB model.** Options:
- (a) delete Qwen3.5-122B-4bit and Next-80B-Instruct-4bit (+114.5 GB; needs an explicit exception or two verified copies);
- (b) a census of non-restricted roots to find at least 35 GB more;
- (c) wait for the block-5 release and offload pilots 8-10 and the B5 originals;
- (d) a quantized lookup table (8-bit 161.8 GB or 4-bit 136.2 GB; a new recipe with a new Gate S).

This also covers the pilot-retention ruling for run B.
- **Default:** (a) + (b) now, (c) when it comes, and keep the full-precision table.

**E2. SSD loan.** How long can the borrowed SN7100 stay? The converted model and the source have to stay on it until a verified internal copy exists.
- **Default:** none stated. Ed decides.

**E3. Longer windows.** Allow 59,520 s calibration windows if a member costs more than 1,175 s?
- **Default:** yes.

**E5. Token budget.** If the budget comes out below 8,192, keep Flash-Next screen-only, or authorize an 8-bit-core build with a precision disclosure?
- **Default:** screen-only.

**E6. Tokenizer.** If transformers 5.12.1 tokenizes differently from 5.22.1, load the Flash-Next tokenizer through the tokenizers library in align code rather than changing the venv?
- **Default:** yes.

**E7. Scheduling.** Alternate Flash-Next windows with D, or start Flash-Next only after D3?
- **Default:** alternate.

**E8. Re-verification.** Fully re-verify the model before every member (about 100 s each), or once per window with a cheap per-member recheck?
- **Default:** every member.

**E9. Purchased SSD.** Keep a purchased SSD attached for the whole series?
- **Default:** no.

**E10. maxfit4.** Precision sign-off for the maxfit4 contingency (MISSING-12), which applies only after a recorded maxfit5 failure.
- **Default:** not requested unless maxfit5 fails.

---

## 4. Missing software, in priority order

All Saturday items are built by Sol (local codex exec) and reviewed by the lead, on `lane/2026-11-07-qwen4exp-mbp-live` **rebased to `97d780d59`**. They use no real weights and run only targeted test modules under `nice -n 19 taskpolicy -b` with `TMPDIR=/private/tmp/jwwf-tmp`. None of them may modify `joulewise/align/models/qwen4_exp.py` (pin `f4ec75d1…`), except MISSING-11 and MISSING-12, which are post-Saturday lanes that deliberately rebind the pin.

### Needed for Saturday

1. **MISSING-2 · 120 min · needed 15 min into the download.**
   - Timed download and convert receipts, with a `.attempt.json` for failed attempts.
   - A read-only `progress --interval 60 [--cutoff] [--convert-budget-h 4]` that writes `download.progress.jsonl` and flags ETA_PAST_CUTOFF.
   - `download --plan-only`.
   - `verify-source --quarantine`, which collects every mismatch and moves bad blobs aside, so a rerun refetches only those.
   - `--max-workers` (2-8).
2. **MISSING-3 · 150 min · needed before the first native check.**
   - `scripts/qwen4exp_mbp_triage.py` sorts each run into exactly one of 15 classes, such as PREFLIGHT_SWAP, ABORT_*, METAL_CAP, PLE_CAP, JETSAM_KILL, METAL_ERROR, PY_EXCEPTION, SIGNAL_CRASH and COMPLETED.
   - Each class maps to a pre-decided next action, in a rule table shared with MISSING-4.
3. **MISSING-1 · 300 min · must be on the Mac before the download starts.**
   - `scripts/qwen4exp_synthetic_artifact.py build`: a full-shape synthetic maxfit/maxfit5 artifact.
   - `--synthetic` limited to memory, performance and paging, with SYNTHETIC stamps on every result.
   - Gives provisional fit and speed answers during the download.
4. **MISSING-4 · 150 min · needed when the first native results land.**
   - The report computes the memory margin and a predicted-versus-observed breakdown, iostat-based paging MB/s and the PLE lookup share of time, and speed MEETS/MISSES.
   - Adds a "Pre-decided next actions" section and an `--evidence-only` mode.
5. **F15 `scripts/qwen4exp_gate_s.py` · 90 min · needed at end of run.**
   - Reads the run directory and gives a mechanical ADMIT-CANDIDATE, NOT ADMITTED or INCOMPLETE verdict for bars S0-S5.
6. **MISSING-5a · 60 min · behaviour-neutral.**
   - Conversion progress JSONL through `convert(progress_path=…)`, with the manifest byte-identical either way.
   - This changes the converter digest, so it needs the `mbp_live.md` rebind and a native re-test.

### After Saturday

7. **MISSING-6 + F13 (duplicates, merged) · 240-360 min.**
   - `scripts/qwen4exp_gold_logprob_compare.py` (`prepare`, `prompts-json`, `compare`): the bf16 comparison from the gold stream.
   - A `quantize_experts` QUANT_DRIFT mode in the gold adapter, selected by `--quant-drift-bits`.
   - Closes GOAL 7 without renting a host.
8. **F14 · laptop · tokenizer equivalence, 5.12.1 vs 5.22.1,** using tokenizer files only.
9. **MISSING-7 · 120 min · only if the rental is approved.**
   - `scripts/qwen4exp_bf16_host_receipt.py` writes the `bf16-identity.json` that `validate_identity` accepts.
   - Plus the `vllm serve` doc section.
10. **MISSING-8 · 180 min · before the next SSD day, or Saturday if PLE_CAP fires.**
    - `scripts/qwen4exp_ple_io_variant.py`: an APFS clone with `io=pread`, plus `--ple-io`.
11. **F1 + F2 · 180 min.**
    - A `Qwen4ExpMlxRuntime` subclass that goes through `load_verified_model`, with a pread override and a refusal for any file off the internal volume.
    - No pin bump; `mlx_runtime.py` stays sealed.
12. **F3-F6 · 300 min.**
    - qwen4_exp XML family and template round trip, a `prefill_step_size` spec field, the hybrid-cache rebuild, and lookup-table I/O telemetry.
    - Anchor and D configs must stay byte-identical.
13. **MISSING-9 · 360 min.** Resumable canonical conversion (`resume_from`, `convert --resume`).
14. **MISSING-10 · 120 min · once the performance JSONs exist.**
    - `scripts/qwen4exp_align_feasibility.py` gives a FEASIBLE, MARGINAL or INFEASIBLE planning estimate.
15. **F7-F11 · 480 min.**
    - Kit additions, the R0-FN-a/-b checks, the R1-FN phases, the desk tables, the Flash-Next disk gate and a census refusal of off-volume model files.
16. **MISSING-11 · 300 min · only if decode misses by more than 20%.**
    - An `mx.compile` decode path, which needs a new module pin.
17. **MISSING-12 · 180 min · only after a recorded maxfit5 failure.**
    - A maxfit4 profile, which needs Ed's precision sign-off.
18. **F12 · documentation, not software.**
    - Protocol v4 Addendum FN, after R1-FN.