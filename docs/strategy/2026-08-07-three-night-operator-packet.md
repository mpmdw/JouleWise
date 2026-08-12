# Three-night quiet-mac operator packet (D-117) — PRE-FREEZE EDITION

Status 2026-08-07: the per-night checklists below are the ratified SHAPE;
the `[PLAN-ID]`/`[BUDGET]` cells bind only when the campaign packs freeze
(work orders U5-U7). Magistrate-supplied values from the ratified design
memo (`docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`):

| Night | Plan (frozen identifier scheme) | Occupancy incl. 20% margin — **DESIGN ESTIMATE, not an arm value** |
|---|---|---|
| 1 | plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v1 | **3.14 h** |
| 2 | plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v1 | **3.24 h** |
| 3 | plan-d117-contrast-qwen25-1p5b-vs-7b-decode-v1 | **2.80 h** |
| (4) | Window C characterization — ED RULING #1 pending | ~3 h class |

These occupancy figures are design estimates from the ratified design memo.
The **arm value** is produced by the frozen timing ledger at pack freeze and
recorded in the plan (freeze manifest A-04 / B-04 / G-06). Never copy a
header figure into a "do-not-return-before" cell.

**HARD GATES before night 1 (none are optional):** U1/U1b two-slot ledger
bracket session + writer integration; U3 pinset v2 / multi-cell mint; U4
three-window regression green; U5-U7 packs each carrying a plan-pinned,
non-authorizing freeze receipt; a non-authorizing D-134 dry-run receipt at the
final reviewed HEAD and committed-pack digest; T-0 external arm receipt only
after live readiness and ledger reservation; atomic consumption of that exact
unsuperseded `GO` receipt before Ed's physical launch; reason-code plumbing (register
item, Ed ruling #3); absolute runs-dir paths in every launch command
(night-strander R6 mitigation); campaign.lock absent at arm; NEVER kill a
running verdict (R7 — it can exceed 2 minutes by design).<br> **2026-08-08 SUPERSESSION NOTE (D-126):** The U2 successor-engine prerequisite above is superseded for this three-night window: keep U2 frozen for its post-window work, and govern ALPHA, BETA, and GAMMA with the issued D-079 calibration-acceptance artifact. **The U2 item has been struck from the enumeration above; this note records why.**

Ed presence: bookends only (~15-20 min each end, §5A sequence in the
night pages). Everything between the bookends is unattended.

---
# Three-Night Quiet-Mac Operator Packet — Draft

**Operator:** Ed  
**Status:** **HOLD until every `[PLACEHOLDER]` and `[BUDGET]` is frozen and the readiness record passes.**

Each night is an independent claim window with fresh roots, calibration bracket, in-window bound, references, verdict, and custody backup.

### Presence legend

- **ED PRESENT:** Ed is physically at the Mac.
- **REMOTE OK:** Allowed only before final arming or after `measurement_complete`.
- **UNATTENDED:** No remote access, agents, browsers, monitoring, log tails, or operator input.

---

# Night 1 — Fresh 1.5B Decode + Prefill Floors

**Window ID:** `[PLACEHOLDER: 1.5B FLOOR WINDOW ID]`  
**Plan root:** `[PLACEHOLDER: PLAN ROOT]`  
**Science configs:** `[PLACEHOLDER: FROZEN CONFIG IDS]`  
**Total duration:** `[BUDGET: TOTAL INCLUDING AT LEAST 20% MARGIN]`  
**Do-not-return-before:** `[BUDGET: COMPLETION TIME/SIGNAL]`

Science payload: the proven decode-floor shape—10 absolute repeats plus 10 null-ABBA blocks/40 members. Prefill floor cells are extracted from these same bundles; they are not optional and are not a separate contrast.

## T-minus preparation — REMOTE OK

- [ ] Authenticate the pack-pinned freeze receipt for this night. Require the
  pinned path and SHA-256, `status: PASS`, and
  `arm_disposition: NOT_APPLICABLE`; this receipt cannot authorize launch.
- [ ] Authenticate the reviewed-head dry-run receipt for this night. Require
  `status: PASS`, `arm_disposition: NOT_APPLICABLE`, and the exact final
  reviewed HEAD and committed-pack digest; this receipt cannot authorize
  launch.
- [ ] At T-0, after live readiness and ledger reservation pass, authenticate
  the external pack-binding arm receipt for this night. Require the exact,
  unexpired, unsuperseded `status: PASS`, `arm_disposition: GO` receipt; no
  automated word authorizes Ed.
- [ ] Immediately before Ed's physical launch, atomically consume that exact
  arm receipt. Require its no-clobber consumption receipt; consumption
  licenses one launch but never performs it.
- [ ] Reviewed `main` is clean and equals the recorded commit.
- [ ] Plan ID, plan-tree hash, chain hash, policy hash, calibration-acceptance hash, and ledger-head pin are recorded.
- [ ] Exact science membership and order are frozen:
  - before midpoint: `[PLACEHOLDER: STAGE IDS]`
  - after midpoint: `[PLACEHOLDER: STAGE IDS]`
- [ ] Decode and prefill extraction cells, analysis rules, and exact evidence-root mappings are frozen.
- [ ] `waivers.json` is exactly `[]`; the launch and verdict commands contain no waiver argument.
- [ ] Retry policy is frozen. There is no manual or outcome-driven retry.
- [ ] Unique claim, bound, custody, quarantine, and backup paths are named and empty.
- [ ] Both claim and bound backup destinations exist and have sufficient capacity.
- [ ] At least 20 GB disk headroom remains.
- [ ] The pinned 1.5B model, tokenizer, configs, scripts, and virtual environment load locally without downloads.
- [ ] Every stage validates and dry-runs in exact manifest order with no unresolved warning.
- [ ] The frozen budget includes both calibrations, 12 bound members, references 3/1/3, all science, every 180-second settle, and at least 20% margin.

## Arm sequence — ED PRESENT

- [ ] Authenticate the freeze receipt path and SHA-256 pinned by this night's
  `plan_tree.json`. Require `status: PASS` and
  `arm_disposition: NOT_APPLICABLE`; it cannot authorize launch.
- [ ] Authenticate the latest D-134 `dry-run-NNNN.json` receipt under this
  pack's window-custody directory. Require `status: PASS`,
  `arm_disposition: NOT_APPLICABLE`, and the exact final reviewed HEAD and
  committed-pack digest. It exercised the real reservation and both ledger
  writers, but no live MLX or `powermetrics` capture. Any reboot since freeze
  voids the pre-reboot readiness receipts and evidence; stop and repeat
  re-verification.
- [ ] Connect the approved 140 W Anker supply and approved cable. Confirm external AC, `ac_high_power`, low-power mode off, and 140 W negotiated. Do not change them afterward.
- [ ] Finish or pause Time Machine, updates, indexing, downloads, and cloud uploads.
- [ ] Confirm thermal pressure is nominal and passwordless `powermetrics` works.
- [ ] Compare the Mac’s clock with an independent trusted source.
- [ ] Record the existing network-time state:

  ```sh
  sudo systemsetup -getusingnetworktime
  ```

- [ ] Disable automatic network-time adjustment:

  ```sh
  sudo systemsetup -setusingnetworktime off
  ```

- [ ] Run and read the preparation probe:

  ```sh
  bash scripts/quiet_mac_prep.sh
  ```

- [ ] Quit Claude, Codex, t3, browsers, browser automation, monitors, watchers, and log tails. Confirm the final process census is clean.
- [ ] Run the frozen pre-window readiness command:

  ```sh
  bash scripts/prewindow_check.sh --wait \
    --timeout-min [BUDGET] \
    --window [PLACEHOLDER: PREWINDOW LABEL]
  ```

- [ ] Run the frozen calibration-ledger readiness and reservation commands
  exactly as written in the frozen plan (run-book §6). Require the readiness
  output to echo the frozen-plan SHA-256; require the reservation to emit
  `calibration_pre_reserve_authorized` and finish with `status: reserved`.
  `needs_pin_commit: true` ends the night — no override exists at night.
- [ ] Only now run the frozen D-134 `arm` command. Require the derived
  `CUSTODY_ROOT/PACK_ID/arm_readiness.receipts/arm-NNNN.json` and sidecar to
  verify as the exact, unexpired, unsuperseded `status: PASS`,
  `arm_disposition: GO` receipt for this HEAD, pack, bracket session, roots,
  backups, waivers, and reservation. No automated word authorizes Ed.
- [ ] Run the frozen D-134 `consume` command against that exact arm-receipt
  path. Require its no-clobber consumption receipt. Consumption licenses one
  physical launch; it never performs the launch. A used capability is never
  reused.
- [ ] Do not hand-count another idle or settle here. The completed
  `prewindow_check.sh --wait` already fulfilled §5's ≥10-minute untouched
  idle and covered the post-`sudo` interval; after launch the chain performs
  its own 180-second settle before the pre-calibration.
- [ ] Tell everyone nearby: do not touch the Mac, lid, display, charger, or cable.
- [ ] After successful consumption, physically launch exactly once from the
  ordinary foreground shell:

  ```sh
  WINDOW_PLAN_ROOT="[PLACEHOLDER: PLAN ROOT]"
  caffeinate -is /bin/zsh \
    "$WINDOW_PLAN_ROOT/window-chain.zsh" \
    "$WINDOW_PLAN_ROOT"
  ```

- [ ] Use the 20-second arm period to step away. After the one-line arm notice, produce no more operator or remote activity.

## Runs unattended — UNATTENDED

| Approximate point | Automatic work |
|---|---|
| T+0 to `[BUDGET]` | 180-second settle, transient display sleep, pre calibration |
| T+`[BUDGET]` | Pre-calibration level screen; failure stops before science |
| T+`[BUDGET]` | Twelve fresh bound members, then same-window dual-family bound mint |
| T+`[BUDGET]` | Three start references |
| T+`[BUDGET]` | 1.5B decode absolute cell, first null blocks, and frozen prefill-floor extraction basis |
| T+`[BUDGET]` | One midpoint reference |
| T+`[BUDGET]` | Remaining null blocks and frozen prefill-floor extraction basis |
| T+`[BUDGET]` | Three end references |
| T+`[BUDGET]` | Post calibration; together with the pre calibration it forms the bracket |
| T+`[BUDGET]` | `measurement_complete` |

Every campaign invocation performs its own 20-second display arm, fresh environment probe, CPU admission, and 180-second settle. Do not inspect the first member or intervene.

## Morning close-out

- [ ] **ED PRESENT:** Use only the frozen completion signal/no-earlier-than time. Wake the display only after `measurement_complete`.
- [ ] **REMOTE OK:** Reconnect the lead/agent. Finalize all calibration-ledger reservations and commit the exact new ledger-head pin before claim evaluation.
- [ ] Confirm the complete calibration bracket, fresh bound, exact membership, seven references, stable adapter identity, and clean admissions.
- [ ] Emit exactly one ordinary whole-window verdict:

  ```sh
  .venv/bin/python scripts/run_campaign.py \
    --whole-window-verdict \
    --runs-dir "$RUNS_ROOT" \
    --log "$RUNS_ROOT/campaign_log.jsonl" \
    --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json \
    --neg8-drift-bound "$BOUND_RUNS_ROOT/neg8-drift-bound.json"
  ```

- [ ] Require `status: passed`; record the evaluation-basis SHA-256.
- [ ] Release any intentionally stopped cloud-sync process using its fail-safe cleanup.
- [ ] Back up both immutable roots; require exit code `0` twice:

  ```sh
  bash scripts/backup_runs.sh "$RUNS_ROOT" "$CLAIM_BACKUP_DEST"
  bash scripts/backup_runs.sh "$BOUND_RUNS_ROOT" "$BOUND_BACKUP_DEST"
  ```

- [ ] **ED PRESENT:** Restore and verify automatic network time:

  ```sh
  sudo systemsetup -setusingnetworktime on
  sudo systemsetup -getusingnetworktime
  ```

- [ ] Keep governed extraction and floor analysis in the same lead-controlled custody session.
- [ ] Call the night claim-bearing only after verdict, both backups, and extraction all pass.

**Send the agent:** window/plan IDs; commit and policy hash; claim, bound, and custody roots; `measurement_complete` timestamp; pre/post calibration directories; verdict status and basis SHA; both backup destinations and exit codes; network-time off/on timestamps; and every failed, quarantined, or superseded occurrence.

---

# Night 2 — Fresh 7B Decode + Prefill Floors

**Window ID:** `[PLACEHOLDER: 7B FLOOR WINDOW ID]`  
**Plan root:** `[PLACEHOLDER: PLAN ROOT]`  
**Science configs:** `[PLACEHOLDER: FROZEN CONFIG IDS]`  
**Total duration:** `[BUDGET: TOTAL INCLUDING AT LEAST 20% MARGIN]`  
**Do-not-return-before:** `[BUDGET: COMPLETION TIME/SIGNAL]`

Science payload: 10 decode absolute repeats plus 10 null-ABBA blocks/40 members on the frozen 7B stack. Prefill floor cells come from the same bundles and must be included in the frozen extraction.

## T-minus preparation — REMOTE OK

- [ ] Authenticate the pack-pinned freeze receipt for this night. Require the
  pinned path and SHA-256, `status: PASS`, and
  `arm_disposition: NOT_APPLICABLE`; this receipt cannot authorize launch.
- [ ] Authenticate the reviewed-head dry-run receipt for this night. Require
  `status: PASS`, `arm_disposition: NOT_APPLICABLE`, and the exact final
  reviewed HEAD and committed-pack digest; this receipt cannot authorize
  launch.
- [ ] At T-0, after live readiness and ledger reservation pass, authenticate
  the external pack-binding arm receipt for this night. Require the exact,
  unexpired, unsuperseded `status: PASS`, `arm_disposition: GO` receipt; no
  automated word authorizes Ed.
- [ ] Immediately before Ed's physical launch, atomically consume that exact
  arm receipt. Require its no-clobber consumption receipt; consumption
  licenses one launch but never performs it.
- [ ] Clean reviewed commit, policy hash, calibration-acceptance hash, ledger head, plan hash, and launcher hash are recorded.
- [ ] Exact stages are frozen:
  - before midpoint: `[PLACEHOLDER: 7B ABSOLUTE + NULL BLOCKS 1–5 CONFIG IDS]`
  - after midpoint: `[PLACEHOLDER: 7B NULL BLOCKS 6–10 CONFIG IDS]`
- [ ] Decode and prefill cells, analysis rules, extraction spec, evidence roots, and counts are frozen.
- [ ] `waivers.json` is exactly `[]`; retry policy is frozen.
- [ ] Fresh claim, bound, custody, quarantine, and backup paths are named and empty.
- [ ] Both 1.5B reference-model and 7B science-model snapshots are complete, revision-correct, and usable offline.
- [ ] Every stage validates and dry-runs in exact order.
- [ ] Disk and both backup destinations have sufficient headroom.
- [ ] Budget includes the 7B cold first load, all settles, calibrations, bound corpus, references, science, and at least 20% margin.

## Arm sequence — ED PRESENT

- [ ] Authenticate the freeze receipt path and SHA-256 pinned by this night's
  `plan_tree.json`. Require `status: PASS` and
  `arm_disposition: NOT_APPLICABLE`; it cannot authorize launch.
- [ ] Authenticate the latest D-134 `dry-run-NNNN.json` receipt under this
  pack's window-custody directory. Require `status: PASS`,
  `arm_disposition: NOT_APPLICABLE`, and the exact final reviewed HEAD and
  committed-pack digest. It exercised the real reservation and both ledger
  writers, but no live MLX or `powermetrics` capture. Any reboot since freeze
  voids the pre-reboot readiness receipts and evidence; stop and repeat
  re-verification.
- [ ] Connect and verify the approved charger/cable: external AC, 140 W negotiated, `ac_high_power`, low-power mode off.
- [ ] Finish or pause background maintenance and cloud transfers.
- [ ] Confirm nominal thermal state and passwordless `powermetrics`.
- [ ] Verify the clock against an independent source.
- [ ] Record and disable automatic network time:

  ```sh
  sudo systemsetup -getusingnetworktime
  sudo systemsetup -setusingnetworktime off
  ```

- [ ] Run `bash scripts/quiet_mac_prep.sh`; resolve every failure.
- [ ] Quit all agents, t3, browsers, automation, monitors, watchers, and tails; require a clean census.
- [ ] Run the frozen `prewindow_check.sh --wait` command and require `READY`.
- [ ] Run the frozen calibration-ledger readiness and reservation commands
  exactly as written in the frozen plan (run-book §6). Require the readiness
  output to echo the frozen-plan SHA-256; require the reservation to emit
  `calibration_pre_reserve_authorized` and finish with `status: reserved`.
  `needs_pin_commit: true` ends the night — no override exists at night.
- [ ] Only now run the frozen D-134 `arm` command. Require the derived
  `CUSTODY_ROOT/PACK_ID/arm_readiness.receipts/arm-NNNN.json` and sidecar to
  verify as the exact, unexpired, unsuperseded `status: PASS`,
  `arm_disposition: GO` receipt for this HEAD, pack, bracket session, roots,
  backups, waivers, and reservation. No automated word authorizes Ed.
- [ ] Run the frozen D-134 `consume` command against that exact arm-receipt
  path. Require its no-clobber consumption receipt. Consumption licenses one
  physical launch; it never performs the launch. A used capability is never
  reused.
- [ ] Do not hand-count another idle or settle here. The completed
  `prewindow_check.sh --wait` already fulfilled §5's ≥10-minute untouched
  idle and covered the post-`sudo` interval; after launch the chain performs
  its own 180-second settle before the pre-calibration.
- [ ] Tell everyone nearby not to touch the machine or power path.
- [ ] After successful consumption, physically launch exactly once:

  ```sh
  WINDOW_PLAN_ROOT="[PLACEHOLDER: PLAN ROOT]"
  caffeinate -is /bin/zsh \
    "$WINDOW_PLAN_ROOT/window-chain.zsh" \
    "$WINDOW_PLAN_ROOT"
  ```

- [ ] Step away during the 20-second arm. No remote or local monitoring afterward.

## Runs unattended — UNATTENDED

| Approximate point | Automatic work |
|---|---|
| T+0 to `[BUDGET]` | Settle, transient display sleep, pre calibration and level screen |
| T+`[BUDGET]` | Twelve fresh bound members and same-window bound mint |
| T+`[BUDGET]` | Three start references |
| T+`[BUDGET]` | 7B absolute cell and null blocks 1–5; prefill evidence rides the same bundles |
| T+`[BUDGET]` | One midpoint reference |
| T+`[BUDGET]` | 7B null blocks 6–10; remaining prefill evidence |
| T+`[BUDGET]` | Three end references |
| T+`[BUDGET]` | Post calibration and bracket closure |
| T+`[BUDGET]` | `measurement_complete` |

The first 7B member may take longer because it reads the local model snapshot cold. That alone is not a failure and is not a reason to intervene.

## Morning close-out

- [ ] **ED PRESENT:** Confirm `measurement_complete` before waking or touching anything.
- [ ] **REMOTE OK:** Reconnect the lead/agent; finalize calibration receipts and commit the new ledger-head pin.
- [ ] Authenticate the calibration bracket, fresh bound, exact science basis, 3/1/3 references, CPU admission, and adapter continuity.
- [ ] Emit exactly one whole-window verdict and require `status: passed`.
- [ ] Record the evaluation-basis SHA-256.
- [ ] Release any stopped cloud-sync process safely.
- [ ] Back up claim and bound roots separately; require exit `0` for both.
- [ ] **ED PRESENT:** Restore automatic network time and verify it is on.
- [ ] Run governed extraction for both 7B decode and 7B prefill floor cells in the same custody session as the consuming analysis.
- [ ] Do not advance to the contrast night until the required 1.5B and 7B floor artifacts, custody, and head pins are ready.

**Send the agent:** all identifiers and roots; completion timestamp; pre/post calibration directories; exact member/failure inventory; verdict row and basis SHA; both backup receipts; network-time timestamps; and the decode/prefill extraction paths.

---

# Night 3 — Fresh 1.5B-vs-7B Decode Contrast

**Window ID:** `[PLACEHOLDER: DECODE CONTRAST WINDOW ID]`  
**Plan root:** `[PLACEHOLDER: PLAN ROOT]`  
**Science configs:** `[PLACEHOLDER: CONTRAST CONFIG IDS]`  
**1.5B floor artifact:** `[PLACEHOLDER: FROZEN ARTIFACT ID/HASH]`  
**7B floor artifact:** `[PLACEHOLDER: FROZEN ARTIFACT ID/HASH]`  
**Total duration:** `[BUDGET: TOTAL INCLUDING AT LEAST 20% MARGIN]`  
**Do-not-return-before:** `[BUDGET: COMPLETION TIME/SIGNAL]`

Science payload: decode only—10 fixed A/B/B/A blocks, 40 members total. Blocks 1–5 run before the midpoint reference and blocks 6–10 after it. Do not add a prefill contrast to this night.<br> **2026-08-08 SUPERSESSION NOTE (D-122):** The no-prefill instruction above is superseded: the frozen GAMMA pack must include the prospectively frozen 256-token prefill ABBA arm, including its members, stages, and budget.

## T-minus preparation — REMOTE OK

- [ ] Both preceding floor windows have passed their verdict, backup, extraction, and custody gates.
- [ ] Exact 1.5B and 7B floor artifact IDs, hashes, stack identities, and ledger-head pins are frozen into the contrast plan.
- [ ] Authenticate the pack-pinned freeze receipt for this night. Require the
  pinned path and SHA-256, `status: PASS`, and
  `arm_disposition: NOT_APPLICABLE`; this receipt cannot authorize launch.
- [ ] Authenticate the reviewed-head dry-run receipt for this night. Require
  `status: PASS`, `arm_disposition: NOT_APPLICABLE`, and the exact final
  reviewed HEAD and committed-pack digest; this receipt cannot authorize
  launch.
- [ ] At T-0, after live readiness and ledger reservation pass, authenticate
  the external pack-binding arm receipt for this night. Require the exact,
  unexpired, unsuperseded `status: PASS`, `arm_disposition: GO` receipt; no
  automated word authorizes Ed.
- [ ] Immediately before Ed's physical launch, atomically consume that exact
  arm receipt. Require its no-clobber consumption receipt; consumption
  licenses one launch but never performs it.
- [ ] Reviewed commit, policy, acceptance artifact, ledger head, plan tree, chain, and exact evidence-root mappings are recorded.
- [ ] Contrast membership is frozen: 10 complete A/B/B/A blocks; no optional member, top-up, block deletion, or outcome-driven replacement.
- [ ] Stage split is frozen:
  - before midpoint: `[PLACEHOLDER: BLOCKS 1–5 CONFIG ID]`
  - after midpoint: `[PLACEHOLDER: BLOCKS 6–10 CONFIG ID]`
- [ ] Both model snapshots and tokenizers are complete, revision-correct, and available offline.
- [ ] `waivers.json` is exactly `[]`; retry policy and analysis direction are frozen.
- [ ] Fresh claim, bound, custody, quarantine, and backup paths are named and empty.
- [ ] Every config validates and both stages dry-run in exact manifest order.
- [ ] Budget includes two-model load churn, all settles, calibrations, bound corpus, references, science, and at least 20% margin.

## Arm sequence — ED PRESENT

- [ ] Authenticate the freeze receipt path and SHA-256 pinned by this night's
  `plan_tree.json`. Require `status: PASS` and
  `arm_disposition: NOT_APPLICABLE`; it cannot authorize launch.
- [ ] Authenticate the latest D-134 `dry-run-NNNN.json` receipt under this
  pack's window-custody directory. Require `status: PASS`,
  `arm_disposition: NOT_APPLICABLE`, and the exact final reviewed HEAD and
  committed-pack digest. It exercised the real reservation and both ledger
  writers, but no live MLX or `powermetrics` capture. Any reboot since freeze
  voids the pre-reboot readiness receipts and evidence; stop and repeat
  re-verification.
- [ ] Verify approved power supply/cable, external AC, 140 W negotiation, high-power policy, and low-power mode off.
- [ ] Finish or pause maintenance, updates, indexing, backups, downloads, and cloud uploads.
- [ ] Confirm nominal thermal state and passwordless `powermetrics`.
- [ ] Verify the clock independently; record and disable automatic network time:

  ```sh
  sudo systemsetup -getusingnetworktime
  sudo systemsetup -setusingnetworktime off
  ```

- [ ] Run `bash scripts/quiet_mac_prep.sh`; resolve every failure.
- [ ] Quit every agent, t3, browser, automation session, monitor, watcher, and tail. Require a zero-survivor census.
- [ ] Run the frozen `prewindow_check.sh --wait` command and require `READY`.
- [ ] Run the frozen calibration-ledger readiness and reservation commands
  exactly as written in the frozen plan (run-book §6). Require the readiness
  output to echo the frozen-plan SHA-256; require the reservation to emit
  `calibration_pre_reserve_authorized` and finish with `status: reserved`.
  `needs_pin_commit: true` ends the night — no override exists at night.
- [ ] Only now run the frozen D-134 `arm` command. Require the derived
  `CUSTODY_ROOT/PACK_ID/arm_readiness.receipts/arm-NNNN.json` and sidecar to
  verify as the exact, unexpired, unsuperseded `status: PASS`,
  `arm_disposition: GO` receipt for this HEAD, pack, bracket session, roots,
  backups, waivers, and reservation. No automated word authorizes Ed.
- [ ] Run the frozen D-134 `consume` command against that exact arm-receipt
  path. Require its no-clobber consumption receipt. Consumption licenses one
  physical launch; it never performs the launch. A used capability is never
  reused.
- [ ] Do not hand-count another idle or settle here. The completed
  `prewindow_check.sh --wait` already fulfilled §5's ≥10-minute untouched
  idle and covered the post-`sudo` interval; after launch the chain performs
  its own 180-second settle before the pre-calibration.
- [ ] Tell everyone nearby not to touch the Mac or its power path.
- [ ] After successful consumption, physically launch exactly once:

  ```sh
  WINDOW_PLAN_ROOT="[PLACEHOLDER: PLAN ROOT]"
  caffeinate -is /bin/zsh \
    "$WINDOW_PLAN_ROOT/window-chain.zsh" \
    "$WINDOW_PLAN_ROOT"
  ```

- [ ] Walk away during the 20-second arm. Do not monitor either model’s progress.

## Runs unattended — UNATTENDED

| Approximate point | Automatic work |
|---|---|
| T+0 to `[BUDGET]` | Settle, transient display sleep, pre calibration and level screen |
| T+`[BUDGET]` | Twelve fresh bound members and same-window bound mint |
| T+`[BUDGET]` | Three start references |
| T+`[BUDGET]` | Decode contrast blocks 1–5 |
| T+`[BUDGET]` | One midpoint reference |
| T+`[BUDGET]` | Decode contrast blocks 6–10 |
| T+`[BUDGET]` | Three end references |
| T+`[BUDGET]` | Post calibration and bracket closure |
| T+`[BUDGET]` | `measurement_complete` |

Alternating models causes ordinary load-time variation. Never use observed run time or apparent effect size to add, drop, reorder, or rerun a block.

## Morning close-out

- [ ] **ED PRESENT:** Confirm `measurement_complete` before waking the display.
- [ ] **REMOTE OK:** Reconnect the lead/agent; finalize calibration receipts and commit the exact ledger-head pin.
- [ ] Authenticate the bracket, bound, 3/1/3 references, all 10 complete blocks, both stack identities, CPU admission, and stable power identity.
- [ ] Emit exactly one ordinary whole-window verdict; require `status: passed`.
- [ ] Record its exact evaluation-basis SHA-256.
- [ ] Release any stopped cloud-sync process using the frozen cleanup.
- [ ] Back up claim and bound roots separately; require two exit-`0` receipts.
- [ ] **ED PRESENT:** Restore and verify automatic network time.
- [ ] Run exact-basis contrast extraction and analysis against the frozen 1.5B and 7B floors in the same custody session.
- [ ] Report the frozen directional result even if it does not clear the decision envelope. Never top up the campaign.

**Send the agent:** window/plan and both floor IDs; code, policy, and ledger pins; all roots; completion timestamp; calibration directories; exact ten-block inventory; verdict and basis SHA; backup receipts; network-time timestamps; extraction path; and every refusal or deviation.

---

# ABORT Page — Stop, Preserve, Diagnose

A failed night is still evidence. It is not permission to clean up and try again.

## Treat the night as failed or non-claim-bearing if any of these occurs

- The chain stops before `measurement_complete`.
- The pre-calibration level screen aborts before member 1.
- A display wakes, the screensaver engages, or anyone touches the Mac.
- CPU, thermal, clock, environment, or adapter admission refuses.
- The charger, cable, wattage, lid, or power policy changes.
- A member is incomplete, fallback-anchored, duplicated, missing, or occupies an existing slot.
- A science stage does not complete its exact frozen membership.
- The post calibration is missing or invalid.
- The calibration ledger has a pending, malformed, or conflicting receipt.
- The whole-window verdict is anything other than `passed`.
- Either custody backup fails.
- Extraction refuses membership or reports that not all frozen cells are extractable.

## What to do immediately

- [ ] Stop touching the machine. Let the foreground chain stop on its own unless safety requires intervention.
- [ ] Record the visible failure and time without altering any artifact.
- [ ] Preserve the complete claim root, bound root, calibration directories, campaign logs, operator logs, locks, and partial bundles.
- [ ] Mark the night **ABORTED / NOT CLAIM-BEARING** until the lead establishes a stronger valid status.
- [ ] Restore automatic network time only after the stopped state and available custody have been recorded.
- [ ] Send the lead/agent the exact roots, last completed stage, failure text, timestamp, process or power change observed, and whether `measurement_complete` exists.

## Never do these things

- **Never delete, overwrite, truncate, or “clean up” failed evidence.**
- **Never retry until a specific cause has been identified, removed, verified, and shown to be retryable by the frozen plan.**
- Never rerun merely because a calibration number, energy result, or verdict was unfavorable.
- Never change a threshold, waiver, membership list, model identity, stage order, analysis rule, or retry count during the night.
- Never use an environment override.
- Never borrow a calibration or bound from another night.
- Never hand-patch metadata, hashes, calibration bounds, or drift allowances.
- Never add members, drop blocks, or top up to improve significance.
- Never append a different verdict over the same basis.
- Never delete an unreadable lock blindly; establish whether its PID is live.
- Never reuse a contaminated root as though it were fresh.
- Never treat a failed backup as permission to alter the source.
- Never wake the display or reconnect remotely simply to check progress.

One automatic settled retry is permitted only when the chain itself identifies a calibration failure whose sole reason is the allowed clock-anchor condition. Any other retry requires the frozen cause-removal rule. With no named removable cause, the night ends.

---

# Appendix — ABORT code to run-book §10 cross-reference

These `ABORT-*` labels are operator aliases for reporting a stopped night.
They are **not new software refusal codes** and do not replace the exact
machine text. Preserve and send both the alias and the literal refusal. The
source actions remain in
[`window_runbook.md` §10](../phase_2/window_runbook.md#10-failure-playbook).

| Operator ABORT code | Exact run-book §10 refusal or symptom | Immediate disposition |
|---|---|---|
| `ABORT-ENVIRONMENT` | `environment_admission_failed`; display awake; screensaver engaged; CPU admission failure | Lose the affected member, preserve it, remove the cause, settle, and follow only the frozen recovery. Never waive admission. |
| `ABORT-CAL-ANCHOR` | `clock_anchor_unresolved` on calibration | Preserve the capture. One settled retry is allowed only when this is the sole reason; otherwise end the attempt. |
| `ABORT-CAL-ROLLOVER` | `pulse_calibration_rollover_gate_timeout` | Abort calibration, preserve it, and repair machine state outside the window. |
| `ABORT-CAL-LEVEL` | Pre-calibration fiducial above `0.033558756679900` (symptom row; no separate literal refusal code in §10) | Stop before member 1. Retry only after a named cause is removed and within the frozen count. |
| `ABORT-CAL-BRACKET-MISSING` | `instrument_calibration_bracket_missing` | Mark the window non-claim-bearing. Never borrow another calibration. |
| `ABORT-CAL-BRACKET-BOUND` | `calibration_bracket_exceeds_minted_bound` | Do not patch metadata. Use a governed prospective re-reduction path or recollect. |
| `ABORT-BOUND-UNDERIVED` | `neg8_drift_bound_underived`; `neg8_idle_sub_drift_bound_underived` | Collect the complete settled-reference corpus and mint both families; never insert a constant. |
| `ABORT-BOUND-STALE` | `neg8_drift_bound_stale` | Mint a fresh same-window corpus and bound. |
| `ABORT-DRIFT-SCREEN` | `neg8_bracket_abs_delta_exceeded`; `neg8_bracket_idle_sub_abs_delta_exceeded` | Reject and preserve this basis; use a new, better-controlled window. |
| `ABORT-ANCHOR-FALLBACK` | `anchor_fallback_member_unusable` | Preserve and quarantine the fragment; recollect the exact frozen member only through the governed supersession path. |
| `ABORT-BUNDLE-IDENTITY` | `bundle_strict_invalid` from telemetry identity | Stop; repair custody or recollect. Do not choose a convenient label. |
| `ABORT-MOCK` | `mock_telemetry_claim_ineligible` | Terminally refuse the member for claims. |
| `ABORT-ALLOWANCE` | `whole_window_drift_allowance_unrecorded` | Refuse the affected floor or claim; rerun the governed verdict/extraction path or recollect. Never substitute zero. |
| `ABORT-MEMBERSHIP` | `whole_window_campaign_membership_unresolved` | Repair custody or recollect. Never replace manifest evidence with a directory scan. |
| `ABORT-VERDICT-CONFLICT` | `whole_window_verdict_conflict` | Stop and preserve every row. Latest-wins is forbidden. |
| `ABORT-OCCUPIED-SLOT` | `incomplete_existing`; occupied run ID | Strict-validate and preserve the old occurrence, move it to quarantine, then use the exact governed supersession procedure. |
| `ABORT-CAMPAIGN-LOCK` | `another campaign appears to be running` | Check the recorded process ID. Stop for a live owner; quarantine a proven dead lock; never delete an unreadable lock blindly. |
| `ABORT-OPERATOR-TOUCH` | Operator touches display, input, lid, or power (symptom row; no literal refusal code) | Lose the active member. A power-identity change ends the entire window. |
| `ABORT-BRACKET-DRIFT-NONCLAIM` | Bracket drift above `0.010818 s` **and** a failed pre-calibration level screen (symptom row; no single literal refusal code) | The window is non-claim-bearing. When the pre-calibration level screen passed, this is not an abort: carry the governed excess through extraction. Never hand-apply an allowance. |

The packet also stops for failures that §10 does not assign a literal refusal
code. Report these packet-level aliases with the exact observed text:

| Operator ABORT code | Packet-level condition | Immediate disposition |
|---|---|---|
| `ABORT-INCOMPLETE-CHAIN` | No `measurement_complete`, or a frozen science stage does not finish exact membership | Preserve every root, log, lock, and partial bundle; mark the night not claim-bearing. |
| `ABORT-POST-CALIBRATION` | Post calibration is missing or invalid without a more specific §10 code | Preserve all calibration attempts and end the window under the run-book’s standing abort rule. |
| `ABORT-LEDGER` | Pending, malformed, abandoned-without-disposition, or conflicting receipt | Do not evaluate the claim. Preserve the ledger state for lead diagnosis. |
| `ABORT-VERDICT` | Whole-window verdict is anything other than `passed`, with no more specific code above | Preserve the basis and the one ordinary verdict; never append a replacement verdict over it. |
| `ABORT-BACKUP` | Either immutable-root backup fails | Leave both source roots unchanged and mark the night not claim-bearing. |
| `ABORT-EXTRACTION` | Extraction refuses membership or not all frozen cells are extractable | Preserve the passing-or-lower evidence status; never top up, drop, or substitute members. |
