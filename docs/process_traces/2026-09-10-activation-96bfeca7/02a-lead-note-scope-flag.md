# Lead note on seat A's `run_status=SCOPE_VIOLATION` (02a), 2026-09-10 04:40 PDT

The wrapper flagged four paths (00-README.md, 01a, 01b, 03 briefs) as scope violations for a `read-only`
sandbox seat with `WRITE_SCOPE: []`. Cause: the lead committed those files (`33b512c2`) in the seat's worktree
`/Users/edr/code/JouleWise-wt-gate-sweep` while the seat was running; the post-hoc scope check compares
`head_start` 078a13a4 with `head_end` 33b512c2 and attributes the delta to the seat. The seat could not write
(read-only sandbox); manifest `reported_changed_paths: []`. Report content is consumed as a valid read-only scout
report. Rule for this activation: never commit in a worktree while a seat is running there; seats B and C run in
their own detached worktrees (`-wt-gate-sweep-b`, `-wt-g2a-prep`), which stayed clean.
