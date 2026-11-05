# MBP offload fix round 2 — 2026-11-05

Base 43ce366556423eb2ff8be273af9caa83ec3d4138, branch
`lane/2026-11-05-mbp-offload-runbook`, initially clean. Explicit task authority
overrides coordination closeout: no RUN_STATE, TASK_QUEUE, state-kernel or
test_gen_state edits, task registration, network, real measurement reads,
analysis execution, full suite or push. All filesystem tests are synthetic.

N1: termination handlers stop the writer group; a child supervisor detects
guard death through private-pipe EOF (including SIGKILL), or a stale heartbeat
after 15 seconds, and self-SIGSTOPs the group. The actual writer is its child.
Runbook requires tmux, caffeinate and keeping Terminal open. Targeted command
`python3.13 -B -m unittest tests.test_align_offload_disk_guard`: PASS, 6 tests,
1.346 s. Real synthetic subprocess tests kill guards with SIGHUP and SIGKILL;
the writer remains alive and its 20 ms execution counter stops advancing.
Sandbox denies /bin/ps, so the test uses that observable stopped execution,
not a native process-state query. Lead should repeat on the Mac and confirm
state T for supervisor, writer and workers. Initial test iteration exposed
the ps sandbox restriction and mocked-pipe BrokenPipe; both tests corrected.
No stopped production group or real writer was involved.

N2: journal validation precedes all audit paths: exact item.parent and
`deletions.tsv`, regular non-symlink, nlink 1; open uses O_NOFOLLOW, O_APPEND,
O_CREAT, and fstat/lstat identity is rechecked before each write. Invalid
journals receive no refusal row. Tests preserve exact KEEP bytes for symlink,
hardlink and a link substituted during open, and reject wrong parent/name.
`python3.13 -B -m unittest tests.test_align_offload_delete_root`: PASS,
45 tests, 0.721 s.
