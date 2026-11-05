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
