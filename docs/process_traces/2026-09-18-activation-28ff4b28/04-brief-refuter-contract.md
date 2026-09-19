SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

# Refuter (read-only, CONTRACT lens) — lane TEST-LARGE-FRAME-ARGV-PORTABILITY-01, fix head `e32ea56c` vs base `6ec5b460`

Cwd is a detached read-only worktree at `e32ea56c`. Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree; write nothing but `/tmp` scratch. No network, no `sudo`, no `powermetrics`. Never run the canonical `python3 -m unittest discover`; run at most `tests.test_run_night.BindSupervisionProcessTests`. Set `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp` and `-B`.

## What you are refuting

`git diff 6ec5b460 e32ea56c -- tests/` is a test-only change: the bind-supervision fault bench (`tests/night_gate_fixtures/bind_supervision.py`) stops expanding a 200,000-character string in the parent and passes it as one argv string (200,884 bytes, over Linux's 131,072-byte per-string cap, `E2BIG` on hosted CI), expands it inside the worker instead, records the largest argv string per launched task, and `tests/test_run_night.py` gains a regression asserting every launched string in the `large_frame` scenario stays under 131,072 bytes. The seat's report is at `/Users/edr/code/JouleWise-wt-mag-28ff4b28/docs/process_traces/2026-09-18-activation-28ff4b28/03-bench-verification-argv-fix.md (the seat died before reporting; this is the magistrate bench verification)` (read its verification section; do not trust it).

## Contract lens — answer each with evidence (file:line you read, commands you ran)

C1. Does the `large_frame` scenario still exercise what `test_large_frame_is_incremental_and_still_bounded` claims: a frame over 200,000 bytes received incrementally with ≤ 4 reads and ≤ 65,536 bytes per tick and a GO verdict? Show that the worker-side expansion produces a frame of the same size class as before (compute both from the code, and state the byte counts).
C2. Are the existing assertions at `tests/test_run_night.py` (the four lines of that test) byte-identical to base? Is the new regression defect-shaped: would it fail on the base fixture? Verify by running the new test against the base fixture (`git show 6ec5b460:tests/night_gate_fixtures/bind_supervision.py` into `/tmp`, run with a `PYTHONPATH` shim or by temporarily copying inside `/tmp` — never modify the worktree).
C3. Did the change alter anything in the bench's timing model (fake clock, ack barrier, deadlines) or the production driver's read budget? Any behavioural change beyond argv size is a finding.
C4. Does any other scenario in the bench still build an argv string that could exceed 131,072 bytes on Linux? Enumerate the largest string per scenario (a `/tmp` scratch that imports the bench and computes `max(len(os.fsencode(a))+1)` over the launcher argv for every scenario is acceptable).
C5. Is anything platform-conditional (skips, `sys.platform`) introduced? That would violate the lane's acceptance.
C6. Does the fix misstate the production seam: confirm from `scripts/run_night.py` (cite lines) that sample/census workers receive only small arguments and that the uncapped `--request` payload is a separate lane (BIND-REQUEST-PAYLOAD-CAP-01).

## Report

Final message in the `claude-codex-report/v1` envelope for `--genre review`; `verdict` = `{counts, findings}` only; JSON header under 8000 bytes; all evidence in the markdown body. Severity vocabulary: blocker / should_fix / nit. State explicitly "same-signature: none found" or name the surviving signature. If you find nothing, say so with the commands that would have found it.
