# 2026-11-05 MBP offload safety fix round

Task: apply the Opus review of b7ba68335 on
`lane/2026-11-05-mbp-offload-runbook`. Initial tree clean; no network.
The explicit brief overrides coordination-file closeout: RUN_STATE, TASK_QUEUE,
the state kernel and test_gen_state remain untouched. No task registered.

Group 1 (B1 deletion boundary, M1/M2/M4, L2/L4/L9/L10): added one stdlib
inventory/deletion program and synthetic refusal tests. The runbook now calls
that reviewed/hashed program, rather than shell assertions followed by rm.
Checks cover mandatory/inode KEEP, eligible source paths, bound receipts,
retention, dataless refusal, hashes, ACLs/flags and fresh cloud upload state.
Preflight failures never reach rmtree; later OS failure is explicitly partial.
`python3.13 -B -m unittest tests.test_align_offload_delete_root`: PASS,
26 tests, 0.853 s, including native uchg on a synthetic temp file. This is not
validation against real custody, iCloud or a measurement Mac.

Further groups and final verification are recorded below as they land.

Group 2 (B1 shell state; H1–H5/H7; L3/L5/L6/L8): replaced the pause/intake
steps with file-only execution, a persistent zsh environment and a pre-STOP
census checking item 170, DESK_DONE, pin/PILOT products, lock owner and named
writers. No interactive Mac agent before desk handoff. Mandatory KEEP roots,
mechanical model-source/blob census, R0 inventories before offload and retained
pilot-9 source are explicit. Model census refuses this old unintegrated base.
Tier 3 is empty. System/user/cron/at launchers and symlink plists are covered;
only redacted facts enter exported journals. No raw argv/plist export.
`python3.13 -B -m unittest tests.test_align_offload_model_keep`: PASS, 2 tests,
0.007 s. All current zsh fences parse with zsh -n (documentation only).
R0's locally cached code was inspected through Git objects; no data paths
from its example config were followed. Live R0 execution remains lead-owned.

Group 3 (H6, M3/M6, L7/L11 and cloud portions of M5): persistent upload and
stat-flag polling functions prove eviction reaches dataless and hydration
clears it; copied manifests use checked checksum receipts. The continuous
five-second guard launches a new process group and SIGSTOPs the writer group
on low/unknown free space. Archive budget is computed from source.json with
padding/header/expansion/control allowance; no compression savings assumed.
Existing ALIGN 0–7, BYTES H/H2 and R7 A343/P0/READY archives get independent
full-copy/restore receipts. R0 gets separate materialized copies, including
pilot 9 without removal of its retained Mac source. Failed partial retirement
is an exact-path, Ed-only rename, not deletion. Per-item env files preserve
resume identity; outputs remain noclobber.
`python3.13 -B -m unittest tests.test_align_offload_disk_guard`: PASS, 3 tests,
0.003 s. All 23 current zsh fences parse; no commands in them were executed.
The guard's five-second sampling is not transactional allocation control;
whole-operation ceilings must fund bursts and detached writers are forbidden.

Group 4 (M5/M7/M8/M9, L1/L12 and final safety integration): made the external
1–2 TB APFS Thunderbolt/USB4 NVMe path primary. Gold/caches/converted weights
and paged n-gram table stay external. Internal reachable estimates are 66 GB,
or at most 92 GB if pilot 8 is eligible, against 150 GB streaming admission
and 166.2 GB for converted model + next ALIGN window + floor. R0's separate
80 GB internal-free gate stays binding. One budget covers materialized R0
copies/models, independent archives/full restore workspace and gold peak.
Documented Ed-only attachment, exclusions, measured throughput and the external
paging/power-boundary implications, without claiming live measurements.
HF pins and metadata now use exclusive publication, persistent revision env,
checked resume receipts covering actual metadata files, and caches isolated
inside JW_GOLD with xet/chunk cache disabled. Corrected port/base/PR refs and
marked the earlier report historical. Final integration also refuses symlink
control receipts, checks link flags/ACLs, checks the exact operation STOP,
writer census and disk floor in the deletion program, and detects unmounts
in the continuous guard. A synthetic census test caught an initial regex
failure to detect `claude -p`; the corrected gate rejects all Claude sessions.

## Review clause map

| Review items | Final implementation / verification |
| --- | --- |
| B1 | Steps 1–2 file-only execution; env.zsh installs all required setopts, exports, disk/upload helpers. Every later runnable fence sources it. Step 8 calls the reviewed, commit-pinned and hashed align_offload_delete_root.py using -I -B. Preflight never calls rmtree on refusal. |
| H1–H3 | Step 2 requires amended item 170 / PR #662, DESK_DONE, pin, p9-PILOT, dead lock owner and clear process census BEFORE STOP/uninstall/bootout; no interactive agent before handoff; offload.py forbidden for pilots 8/9. |
| H4, L5 | Step 3 + model_keep helper scan every config JSON (including identity_pins), roster files and exact R0 config, print sources/blob paths and input digests; reconcile all BYTES/B6/ALIGN IDs; unresolved paths STOP. Snapshot-link-only baselines insufficient. |
| H5 | Steps 3–4 retain all pilot 9 and its captures through release. Pilot 8 needs structure-only ledger-locator review; capture-bearing trees and pilot-v8-* refuse in program. |
| H6 | env functions poll stat -f %Sf dataless after eviction, clear after hydration; both object digests rechecked; deletion program re-evaluates isUploaded=1 for archive and manifest. |
| H7 | Step 3 R0 --inventory before any offload; step 7b uncompressed/non-symlink destinations, both inventories compared; step 9 internal R0 gate plus combined disk budget. |
| M1 | exact_path + mandatory KEEP + inode/ancestor overlap + narrow source allowlist. Tests include case-variant path and inode alias, symlink components, .., whitespace/Unicode, missing KEEP. |
| M2 | Both independent and Ed receipts require this exact source, source-manifest SHA and archive SHA; tests mutate each binding independently. |
| M3 | disk_guard checks every 5 s, SIGSTOPs whole new writer group below 30 GB or on changed/unknown device. Source.json budget includes tar padding/headers, expansion and control copies; synthetic budget test covers long PAX names. |
| M4 | tree and control/archive reads refuse dataless before opening; synthetic flagged-stat tests. |
| M5 | Fixed operation/env on resume, noclobber, exclusive Python writes, test ! -e hf-pinned.json, hf-env and actual metadata checksum receipts; no repeated mutable-main query. |
| M6 | Step 7a explicitly requires independent full copies/restores of ALIGN 0–7, BYTES H/H2 tars, R7 A343/P0/READY, one receipt per item. |
| M7, L1 | No pilot-9 reclaim credit; tier 3 empty. Explicit internal impossibility and external primary plan with continued ALIGN/R0 admission. |
| M8 | Step 10 pins HF_HOME/HF_HUB_CACHE/HF_XET_CACHE under JW_GOLD, disables xet and chunk cache, budgets pip/temp/cache; shared home HF hub writes/deletion forbidden. |
| M9 | Port PR #664 / lane/2026-11-05-align-flashnext-port, gold PR #667 / lane/2026-11-05-align-flashnext-gold-parity (pushed per lead), moving base origin/port/qwen4-exp-mlx; actual reviewed full SHAs required. |
| L2 | All source nodes (including links) and parent/control dirs checked for uchg/schg/uappnd/sappnd and ACLs before rmtree; native uchg synthetic-tree refusal; OS errors explicitly FAILED_PARTIAL. |
| L3–L4 | Final no-newline candidate line handled in documented loop; exclusive .OFFLOADED.json pointer with staged recovery payload and TSV states. |
| L6, L8 | Symlink plist discovery, GUI/system/cron/at census, quiet-kit and keepawake treatment; exported records redact argv/credentials, raw plist backups stay local. |
| L7 | shasum -a 256 -c for archive/helper/copied manifest, rebinding expected checksums to independent paths. |
| L9–L10 | All inline Python uses -I; hardlinks refused and feasibility consequence explicit. |
| L11–L12 | Exact-path Ed-only partial retirement rename; full restricted path-map warning, no claim literal-directory filtering makes manifests agent-readable. |

## Final verification

Run sequentially, one unittest module at a time, using Python 3.13:

- `python3.13 -B -m unittest tests.test_align_offload_delete_root` — PASS,
  42 tests, 3.426 s. Synthetic trees only, including actual BSD uchg flag on
  a temp file; upload/ACL failures, dataless placeholders and low disk are
  synthetic. Tests verify no rmtree call on every refusal category and
  separate partial-OS-failure reporting. Success checks JSON pointer + TSV.
- `python3.13 -B -m unittest tests.test_align_offload_model_keep` — PASS,
  2 tests, 0.017 s. Reads only synthetic repository files; model paths remain
  inert text. Missing integrated source census refuses.
- `python3.13 -B -m unittest tests.test_align_offload_disk_guard` — PASS,
  4 tests, 0.005 s. Mocked signals verify group SIGSTOP, five-second sampling,
  low/unknown space, volume identity change and no launch on failed admission.
- `python3.13 -B -m unittest tests.test_docs_freshness` — PASS,
  31 tests, 3.767 s.
- Extracted all 26 zsh fences and checked `/bin/zsh -n`; parsed all 7 Python
  heredocs with ast.parse — PASS. All post-bootstrap fences source env; 14
  numbered steps present. Documentation commands were never executed.
- `git diff --check` — PASS. Protected-path diff against b7ba68335 is empty
  for RUN_STATE.md, TASK_QUEUE.md, docs/process/state_kernel.json and
  tests/test_gen_state.py. Full suite deliberately NOT run, per brief and
  active 7-worker analysis job. Targeted tests totaled far below 20 minutes.

## Limits, remaining gates and exact handoff

No real measurement data, restricted tree, or home path outside this clone
was read/listed/statted/searched. Absolute paths in code/config were inert
text. Allowed Git object reads through alternates supplied repository code
and records only. No network, analysis pipeline, harvest, offload, live cloud
operation, real source deletion, model download, native MLX, measurement,
push or deployment occurred. No subagents/consult used; final verification
was performed in this session. No advisor-visible live state changed.

This fixes the requested procedure and guard implementation; it does not
supply a fresh independent SAFE verdict or make any operational STOP pass.
The deletion is not transactional: external mutation or OS/I/O failure after
rmtree begins can still leave partial removal; pending pointer + TSV retain
recovery coordinates. The disk guard samples, so admitted whole-operation
ceilings must cover bursts; writers must not detach from its process group.
No automatic SIGCONT is authorized by a low-space stop. ACLs are refused
conservatively rather than interpreted. Hardlinks or historical missing KEEP
paths can make a root ineligible. Prose roster IDs still require operator
reconciliation to source configs, never guessed paths.

Operational unknowns: actual available internal bytes, pilot-8 locator
eligibility, approved device/UUID/capacity/exclusions/throughput, original
archive trust anchors, live fileproviderctl output/state, integrated item-170
semantics and desk completion, HF immutable SHA, actual harness commit/CLI,
quantization and largest subunit. If pilot 8 cannot be removed and internal
free is below 80 GB, R0 remains blocked; no retention waiver is implied.

Next exact step: lead reviews the local fix commits against the Opus items,
then Ed confirms amended #662 in Mac records and the completed DESK_DONE/pin/
p9-PILOT handoff with no live owner/writer BEFORE STOP/bootout. Ed attaches
and admits the APFS external device (9a) before inventories/copies. Only then
perform the unexecuted procedure and its cloud/restore gates. The lead must
run native harness tiny/config, full 48-layer gold (including real n-gram
rows), conversion, interrupted-unit resume and converted end-to-end/no-swap
checks outside this sandbox; exact commands come from reviewed PR #667, not
from guessed flags here. The new guard unittest modules should also be rerun
on the target Mac; synthetic passes here do not validate iCloud or hardware.

Additional final checks: `PYTHONPYCACHEPREFIX=/private/tmp/jwsol/mbp-offload-3/tmp/compile-cache python3.13 -m compileall -q joulewise tests scripts/align_offload_delete_root.py scripts/align_offload_disk_guard.py scripts/align_offload_model_keep.py`
— PASS (exit 0); compilation only, not full-suite execution. A synthetic zsh
round trip serialized the documented pause function plus env heredoc to a
temporary env.zsh, sourced it in a separate `zsh -f -euo pipefail`, and asserted
all six required options and all four guard functions were restored — PASS.
No guard was invoked, so no Mac/data path was accessed by this shell check.

Changed paths: the runbook; this fix report and the historical-report pointer;
`scripts/align_offload_delete_root.py`, `scripts/align_offload_model_keep.py`,
`scripts/align_offload_disk_guard.py`; their three `tests/test_align_offload_*.py`
modules. Local commit groups: `407fc0375` deletion boundary, `0a97737b5`
pause/retention/R0, `7365b475a` cloud/continuous guard, and the final external
storage/resume/integration commit containing this report. No push.
Final docs-freshness replay after the complete report: PASS, 31 tests in
21.799 s. Total targeted execution remains comfortably under the 20-minute cap.
