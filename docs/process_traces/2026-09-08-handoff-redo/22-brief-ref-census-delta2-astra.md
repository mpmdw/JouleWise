WRITE_SCOPE: []

# DELTA RE-AUDIT 2 — disposition B landing on the WATCHDOG-CENSUS-01 / RESUME-DAEMON-01 branch (gpt-6-astra, read-only)

Branch history in this detached worktree: HEAD = disposition-B commit; HEAD~1 = 7a18fddc prune; HEAD~2 = b3eeee9a
fix round 1; HEAD~3 = 898e5305 landing; HEAD~4 = main d8ad6c15. Packet: `git diff HEAD~1 HEAD` (4 files, +186/−26).
A cold gate ruled (quoted): "in both the tick's dead-lock branch and the step-4 block, treat `read_lock() == {}` as
'consult `state["resident_session"]`', refuse if that pair is live, if any resumed twin is live, if any daemon is
live, or if the record is absent or malformed; unlink only when the pair is provably absent. Regression: headless
resident live, corrupt lock, populated resident_session → HOLD, lock kept; record absent → HOLD, lock kept; pair
gone → unlink. Document Ed-hands recovery only for the both-unreadable case." The seat claims exactly that, plus
refusal events and a retained launch notice, and that drain adoption cannot discard the evidence; 3 regression
methods failed before / pass after; scoped modules rc 0.

Break it: (1) Re-run the cold judge's tick matrix yourself against `decide()` at HEAD with injected process tables
and corrupt forms `{torn`, `{}`, `[]`: live `claude -p` resident with matching (pid,start) → HOLD + lock kept;
record absent/malformed → HOLD + lock kept; pair gone (pid absent; pid present with different token) → unlink →
LAUNCHING; pair gone but resumed twin / daemon / bg-pty-host / bg-spare live → HOLD; pair present but defunct →
HOLD. (2) Same matrix through the DOCUMENTED step-4 block extracted exactly per the doc's contract. (3) VALID-lock
semantics unchanged vs HEAD~1: diff the valid-lock paths and run the pre-existing valid-lock tests. (4) Does the
new refusal ever starve a legitimate relaunch — e.g. resident_session populated with a pid that was reused by an
unrelated process with the SAME start-time string granularity (start_time is seconds-resolution `lstart`)? Is
PID+start-time binding strong enough on macOS? (5) The retained launch notice and events: do they serialise into
events.jsonl in the existing `joulewise.magistrate_event.v1` schema without breaking `load_state`/older readers?
(6) Mutation probe: in a $TMPDIR copy, drop the "record absent → HOLD" conjunct and the "twin live → HOLD"
conjunct separately; confirm the named regressions fail. (7) Anything HEAD~1 had right that HEAD broke.
Run only the three scoped modules, never the repository-wide suite. Report (genre review): `verdict` = {counts,
findings} ONLY; header < 8192 bytes; each finding with file:line, severity, exact demonstrating command.
