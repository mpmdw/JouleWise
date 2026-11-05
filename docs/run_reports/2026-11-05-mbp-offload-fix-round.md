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
