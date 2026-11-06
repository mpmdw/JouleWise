# PR #665: Saturday SSD safety handoff

Implemented on `lane/2026-11-05-mbp-offload-runbook`, without rebasing or
pushing. Implementation commit: `e18c89c64` (`fix(offload): require verified
day-only SSD custody and unplugged windows`). The following handoff commit
also contains the documented retry-ID correction and this report; its hash
is in `git log -2 --oneline`.

The procedure now orders **SSD copy/full restore verification → iCloud
server confirmation/proved dataless round trip → one hashed Ed-only deletion
program**. The borrowed WD_Black SN7100 2 TB / OWC Express 1M2 is day-only.
It must be ejected and physically unplugged before every R0, R1 or other
measurement. The pre-arm script refuses external media even if unmounted,
and refuses mounted network/image volumes and unknown census states.

This is a fail-closed implementation, **not an independent SAFE verdict or
live validation**. No pilot deletion is currently authorized. Pilots 8–10
remain intact pending a retention ruling/release and a reviewed guard change.
The upload parser also intentionally refuses until the lead reviews a real
native `fileproviderctl evaluate` sample and installs its grammar/pin. Neither
gate can be replaced by a generic Ed approval receipt.

## Per-finding disposition

Paths below are relative to the repository. `runbook` means
[`docs/align/mbp_offload_and_gold_setup.md`](docs/align/mbp_offload_and_gold_setup.md);
`guard` means [`scripts/align_offload_delete_root.py`](scripts/align_offload_delete_root.py).
Some fixes were already on the supplied branch and are retained/rechecked.
Synthetic tests establish refusal/verification logic, never live custody.

| Finding | Fix / disposition | Where | Test / evidence |
|---|---|---|---|
| B1 | File execution with explicit zsh options; persistent env; deletion checks and rmtree in one pinned, hashed `delete_root.py` invocation. No shell recursive removal. | runbook §§2,6,8; guard `delete_root` | `test_align_offload_runbook` parses every zsh fence/Python heredoc; `test_align_offload_delete_root` asserts no rmtree on refusals. |
| H1 | Auto-deleting offload.py forbidden for all three pilots; public-only deletion path retired; both actual backup copies required. | runbook opening/§§6–8; guard | Pilot retention/refusal tests; `test_align_offload_public_weights` retirement test; second-copy tests. |
| H2 | STOP-2 requires amended item 170 AND 171–174. Item 174 supersedes the historical no-pilot-10 direction; no pilot 11. | runbook §2 | Runbook parsing/contract checks; cached origin/main contains these items; actual Mac directive review remains native gate. |
| H3 | Wait for pilot-9 DESK_DONE/pin/p9-PILOT and pilot-10 terminal/desk/read/pin/p10-PILOT before STOP/bootout. Dead lock owner and quiet process census required; final program repeats lock/launcher checks. Interpreter-launched writers detected without exporting argv. | runbook §2; guard `busy_processes`, `check_pause_and_disk` | Final-pause lock/launcher test, Python-writer tests, refusal tests; real handoff not inspected. |
| H4 | Mechanical six-ref Git census of identity pins, BYTES/B6 rosters, ALIGN/amendment and R0 config. Historical/unknown identities stay KEEP, including all references named in the review. No model-root exception. | runbook §§3–4; `align_offload_model_keep.py` | `test_align_offload_model_keep`; retained model-identity/census policy tests. |
| H5 | All pilot/capture roots retained. Require structure-only complete ledger-locator review; no split-root deletion or locator rewrites. A ruling is still needed to change that policy. | runbook §§4,8; guard | Every-pilot retention test now includes v9/pilot10; capture-tree refusal test. |
| H6 | Program records actual dataless eviction and non-dataless hydration, checks both hashes and every archive member, then publishes bound cloud proof. Final deletion repeats BOTH upload checks after the long SSD/source re-reads. Parser unknowns refuse. | runbook §§5,7–8; guard `cloud_roundtrip`, `wait_dataless` | `test_align_offload_second_copy` cloud transition/timeout/failure tests; proof-binding and upload-parser tests in deletion module. Native parser pin remains STOP. |
| H7 | R0 inventories before copying/offload; uncompressed directory copies; pilot view links preserved, model bytes materialized. Explicit internal budget: max(80 GB, two W1 copies + 30 GB) + remaining journal. Unplugged R0/copy-probe conflict is an explicit STOP. | runbook §§3,7b,9,13; existing R0 patch document | `test_align_offload_r0_patch`; runbook syntax/contract checks. Native R0 not run. |
| M1 | Exact paths, all mandatory existing KEEP roots, inode/ancestor overlap, narrow source allowlist, no model-root exemption. | guard `exact_path`, `check_keep`, `delete_root`; runbook §4 | Path/case/inode/symlink/missing KEEP tests. |
| M2 | Both attributed receipts bind source, source-manifest SHA and archive SHA. Actual SSD UUID/archive/manifest/restored bytes also rechecked. | guard; runbook §8 | Receipt mutation tests; second-copy binding/corruption tests. |
| M3 | Existing five-second guard stops whole writer group on low/unknown space/device change; all writers use it. Archive ceiling derives from source.json; restore allocation added. Guard death/signal behavior preserved. | runbook §§5–7,9,12; `align_offload_disk_guard.py` | `test_align_offload_disk_guard`; tar-budget test; native synthetic process tests only. |
| M4 | Dataless source/control/archive/KEEP/approval data refused before content reads. Enrollment checks archive before decompression. | guard `tree`, `sha_file`, `enroll_second` | Dataless tests in deletion module; second-copy checks. |
| M5 | Fixed operation/env on resume, noclobber/exclusive outputs, immutable item env/checksums; reviewed unique retry suffix retains old receipts/partials. HF pin initialization never repeated; hf-receipts verified on resume. | runbook §§2,6,10–12 | Runbook parser/contract tests; second-copy exclusive-publication test. |
| M6 | SSD backup checklist covers ALIGN 0–7, BYTES H/H2, R7 A343/P0/READY, with original trust anchors, complete member/restore verification and per-item receipts. Missing original-format verifier/hash is STOP. | runbook §7a | Syntax checks; shared complete-restore/hash logic covered by second-copy tests. Real archive formats/coverage remain Ed/lead verification. |
| M7 | No 95 GB internal conversion admission claimed. Historical 166.2 GB + journal need shown; external outputs are daytime-only and cannot be measurement dependencies. | runbook §§9,12–13 | Runbook contract check; actual capacities/kit footprint remain native gates. |
| M8 | HF_HOME/HF_HUB_CACHE/HF_XET_CACHE and temp/pip caches inside JW_GOLD; xet/chunk cache disabled; no writes/delete-cache in shared anchor hub. | runbook §§10–12 | Runbook syntax checks; native harness cache enforcement remains lead-owned. |
| M9 | Retain correct port PR #664, gold PR #667/branch and moving-base warning. Require reviewed full commit pins, not branch-tip assumptions. | runbook opening/§§3,6,11–12 | Git/text inspection and syntax checks; no network verification claimed. |
| L1 | Deleted pilots 0–7 have zero further reclaim. Show retained-source ~66 GB, hypothetical ~118 GB/~144 GB; neither hypothetical satisfies 150 GB and neither is approval. | runbook §9 | Runbook contract check; estimates explicitly non-live. |
| L2 | Flags and ACL prechecks on source nodes/parents/control directories; explicit FAILED_PARTIAL recovery state and pending JSON pointer. | guard; runbook §8 | Protected-flag, ACL, native synthetic uchg and OS-failure tests. |
| L3 | Final unterminated candidate line handled; no batch deletion loop. | runbook §3 | Text review plus zsh syntax check. |
| L4 | `.OFFLOADED.json`, with exclusive pending publication and audit states. | guard; runbook §8 | Success-pointer and failure-state tests. |
| L5 | KEEP baselines must include real model blobs; snapshot-link-only inventories insufficient. | runbook §§3–4,6 | Model census tests; actual blob inventory is operator-only. |
| L6 | Symlink plists, user/system launchers, cron/at and quiet-kit included; keepawake preserved; final deletion rechecks both launcher domains. Optional remote stop remains lead-owned. | runbook §2; guard `check_pause_and_disk` | Final-pause launcher test; syntax check; actual discovery remains native. |
| L7 | Expected archive and copied-manifest digests rebound to destination paths and checked with shasum -c. | runbook §§6–7a | Hash mutation tests and shell syntax checks. |
| L8 | Raw argv inspected only locally; only PIDs exported. Raw plist/cron/evaluate diagnostics excluded from journal export pending Ed review. Census outputs no device URLs/options/credentials. | runbook §§2,5,7,13; both scripts | Census credential-redaction test and Python-writer tests. |
| L9 | Inline Python uses -I -B. | runbook throughout | Every inline Python heredoc parsed; text review. |
| L10 | Hardlinks still fail closed; explicit feasibility STOP for inode-deduplicated pilots. | runbook §6; guard | Hardlink/source/archive refusal tests. |
| L11 | Exact-path Ed-only partial retirement by rename, retained in budget; no glob or automatic cleanup. | runbook §6 | Shell syntax check; no retirement/deletion executed. |
| L12 | Full restricted path-map warning; no claim that literal-name filtering makes real manifests agent-readable. | runbook opening/§§3,6–7a | Text review; synthetic unsafe-member tests only. |

## Exact Saturday command sequence

These are **Ed-only commands on the paused measurement MBP**, not commands
for this clone/agent. Save the runbook fences as their named reviewed `.zsh`
files in one fixed `JW_STEPS` directory. Save the sequence below as a file
and run it with `zsh -f -euo pipefail`; do not paste into default interactive
zsh. Each file sources the persistent operation env. A failed command stops
the sequence. Never continue past an unresolved STOP.

Before starting, the lead must supply reviewed actual values for records,
pilot-9/10 handoff products/plan, integrated tooling SHA with native upload
parser pin, R0 code/config/ref pins, exact SSD mount/UUID, remaining allocation
bounds, original archive trust anchors/verifiers, KEEP and baseline reviews.
No values were obtained from real data here. Absent any required input: STOP.
Do not overwrite an existing operation; resume its env/receipts instead.

```zsh
setopt interactivecomments errexit nounset pipefail extendedglob noclobber
export JW_OP=/Users/edr/night-archive/mbp-offload-20261107
: "${JW_STEPS:?Set exact directory of reviewed step files}"
zsh -f -euo pipefail "$JW_STEPS/step1.zsh"
# Requires terminal pilot-10 handoff, dead lock and clear process census first.
zsh -f -euo pipefail "$JW_STEPS/step2.zsh"
zsh -f -euo pipefail "$JW_STEPS/step2-pause.zsh"
source "$JW_OP/env.zsh"
: "${JW_EXTERNAL:?Set actual attached SSD mount}"
: "${JW_EXTERNAL_UUID:?Set enrolled Volume UUID}"
export JW_EXTERNAL JW_EXTERNAL_UUID

guarded() {
  python3.13 -I -B "$JW_CANON/scripts/align_offload_disk_guard.py" \
    --path /System/Volumes/Data --path "$JW_EXTERNAL" -- \
    /bin/zsh -f -euo pipefail "$1"
}
guarded "$JW_STEPS/step9a.zsh"
source "$JW_OP/external-env.zsh"
zsh -f -euo pipefail "$JW_STEPS/step3.zsh"
# STOP 4: actual KEEP, baseline, locator and capacity review before real copies.
guarded "$JW_STEPS/step5-probe.zsh"
# STOP 5: reviewed real fileproviderctl grammar/pin; no synthetic substitute.
guarded "$JW_STEPS/step5-roundtrip.zsh"
zsh -f -euo pipefail "$JW_STEPS/step6-tool.zsh"

# Complete all SSD backups first. Preserve sources and all failed attempts.
for JW_ID JW_SRC in \
  pilot8 /Users/edr/night-align/pilot-v7-20261105T015948Z \
  pilot9 /Users/edr/night-align/pilot-v8-20261105T102850Z \
  pilot10 /Users/edr/night-align/pilot-v9-20261105T231016Z; do
  export JW_ID JW_SRC
  guarded "$JW_STEPS/step6-item.zsh"
  export JW_ITEM="$JW_OP/$JW_ID"
  guarded "$JW_STEPS/step6-ssd.zsh"
done

# Then each cloud upload and full dataless/hydration/member/hash round trip.
for JW_ID in pilot8 pilot9 pilot10; do
  export JW_ID JW_ITEM="$JW_OP/$JW_ID"
  guarded "$JW_STEPS/step7-cloud.zsh"
done

# For EACH original custody row: ALIGN 0–7, H/H2, R7 A343/P0/READY,
# set the exact JW_EXISTING_* fields from that row, then run:
guarded "$JW_STEPS/step7-existing.zsh"
# Repeat explicitly per row, with a new destination, until checklist complete.
# For EACH pilot's configured uncompressed copy, set JW_R0_SOURCE/DEST/
# EXPECTED/ACTUAL from its agreed config and pre-copy inventory, then run:
guarded "$JW_STEPS/step7b.zsh"
# Repeat for all three pilot backups; R0 requires the pilot8/pilot9 pair.
```

The last two commands are per-item templates: do not run them once and claim
the checklist complete. Unknown original-format verifiers or custody rows
remain BLOCKED; this blind session cannot invent them. The existing-format
writer must perform its full original-verifier cloud round trip as required
by §7a, as well as member/restore verification.

**Do not run step8-delete.zsh for pilots 8–10.** After an installed retention
ruling/guard change, all receipts and actual copies would still be required;
this version deliberately refuses. No public-weight deletion is an alternative.
For any separately eligible source, Ed's command is exactly the pinned call
in runbook §8; it is never an agent operation or shell removal.

After backup, save a redacted journal/receipt export on both destinations,
verify its hashes/coverage, and finish all writers. Then:

```zsh
# Exporting the journal is itself a guarded, admitted writer; exclude raw secrets.
zsh -f -euo pipefail "$JW_STEPS/step13-eject.zsh"
```

**Physically unplug the enclosure now.** After unplugging, the magistrate uses
the following read-only command immediately before each R0/R1/other arm;
a nonzero exit prevents arm/install. Use a new receipt path each time:

```zsh
setopt interactivecomments errexit nounset pipefail extendedglob noclobber
source "${JW_OP:?Set existing operation}/env.zsh"
: "${JW_EXTERNAL_CENSUS_RECEIPT:?Set NEW unique receipt path}"
python3.13 -I -B "$JW_CANON/scripts/external_volume_census.py" \
  > "$JW_EXTERNAL_CENSUS_RECEIPT"
```

Run `step9-budget.zsh` with the actual pinned W1/journal numbers before R0
admission. Expected historical retained-source availability (~66 GB) fails:
at least 80 GB plus remaining journal, and any larger two-copy-plus-floor
plan requirement, is mandatory. Repeat df admission immediately before arm.
Do not restore the magistrate/remove the operation STOP until the lead's
fresh-plan/notice/installation and all remaining gates pass. The runbook
separates prepare from install and repeats the census directly before install.

## Verification, remaining risks and uncertainty

Final focused results (Python 3.13, unittest only, synthetic fixtures):

| Command (`python3.13 -B -m unittest …`) | Result |
|---|---|
| `tests.test_align_offload_delete_root` | PASS, 51 |
| `tests.test_align_offload_second_copy` | PASS, 9 |
| `tests.test_external_volume_census` | PASS, 7 |
| `tests.test_align_offload_disk_guard` | PASS, 7 |
| `tests.test_align_offload_model_keep` | PASS, 4 |
| `tests.test_align_offload_r0_patch` | PASS, 4 |
| `tests.test_align_offload_public_weights` | PASS, 5 |
| `tests.test_align_offload_runbook` | PASS, 4 |

91 targeted tests pass. Compilation also passed:
`PYTHONPYCACHEPREFIX=/private/tmp/jwsol/offload-fix/tmp/compile-cache python3.13 -m compileall -q joulewise tests scripts/align_offload_delete_root.py scripts/external_volume_census.py`.
No full suite, pipeline, measurement, real-source deletion, network, download,
push, native MLX execution or external integration was performed. Cumulative
targeted test runtime was far below 20 minutes. The run report records an
initial brief test-scheduling deviation and the corrected serial replays.

Remaining gates/risks:

- Native cloud parser sample/grammar is absent; upload verification and all
  downstream deletion intentionally STOP. Native diskutil/mount/brctl behavior,
  actual SSD UUID/capacity/exclusions, quotas and throughput are unvalidated.
- All pilot captures remain under ledger retention. A release/ruling plus
  code review is required before deleting any target. Backup success alone
  does not authorize removal. Unknown restricted coverage stays untouched.
- R0 copy destinations on the day-only SSD may conflict with a gate that
  probes them during measurement. The R0 lead must separate daytime copy
  verification from unplugged measurement admission; until then STOP.
- No real free-space or pilot-10 size measurement exists here. The budget is
  a conservative plan with zero current reclaim; R0 is not declared unblocked.
- Original M6 formats/manifests/trust anchors and complete archive checklist
  require the authorized custody operator. Hardlinks/required metadata can
  make a pilot ineligible for the current archive format.
- Deletion cannot be transactional against OS/I/O failure or external
  mutation; pending pointer, immutable backups and FAILED_PARTIAL evidence
  support recovery. The disk guard samples every five seconds and needs
  whole-operation admission to fund bursts. A pre-arm census is instantaneous;
  Ed must prevent reconnection for the complete window.
- Gold source pruning is prospective and gated against the same deletion
  policy; the 120 GB streaming estimate cannot justify a no-pruning run.
  External outputs are never measurement dependencies. The lead must run the
  native PR #667 tiny/config, interrupted-resume, full 48-layer/real-PLE,
  conversion and converted end-to-end/no-swap checks outside this sandbox
  using that reviewed interface. No MLX code changed in this fix.

Read items 169–174 from **cached** `origin/main` at
`f193a320f836601014a88bc169aefad5cead4c71` (through allowed Git objects).
Did **not fetch**, because the binding no-network instruction forbids it;
current server state remains unknown. No absolute data path was followed.
RUN_STATE.md, TASK_QUEUE.md, docs/process/state_kernel.json and
tests/test_gen_state.py remain unchanged; no kernel task was registered.

Changed files: the runbook; both safety scripts; the deletion, public-weight
retirement, runbook, second-copy and external-volume test modules; this answer;
and the dated [run report](docs/run_reports/2026-11-05-mbp-offload-saturday-ssd.md).
Next exact step: lead reviews the local commits and resolves the native parser,
retention and unplugged-R0 gates, then Ed executes the reviewed Saturday files.
