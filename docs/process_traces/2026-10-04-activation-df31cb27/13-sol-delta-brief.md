# Delta check: PR #467 review finding F1

Worktree `/Users/edr/code/JouleWise-wt-df31-review`, detached at `92a3661d4ea1e48b89b2a48d419479aa7c63ace8`. Read-only: do not edit tracked files and do not commit. Interpreter `/Users/edr/code/JouleWise/.venv/bin/python -B`, run from the worktree root. Scratch: `/tmp/df31-delta/` only. Never read `summary*.json`, `counts*.json`, `selection*.json` or `bracket*.json` under /Users/edr/night-g2a, /Users/edr/night-custody or /Users/edr/night-archive.

Your earlier review of `96747ff0` (report /Users/edr/night-archive/df31-sol-review.md) found F1 (MAJOR): with zero valid members, the bracket-view refusal codes were lost. The fix is `git diff 96747ff0..92a3661d4ea1e48b89b2a48d419479aa7c63ace8`. Check that:
1. it fixes F1: re-run your /tmp/df31-review/empty_refusal.py reproduction (copy it to /tmp/df31-delta/ if needed);
2. it changes nothing else: when the snapshot has no refusal the reasons are unchanged, the open-session and no-session paths are unchanged, and SELECT is still reachable when everything passes;
3. the new test kills the mutation that deletes the line;
4. the four test modules pass.

Output: a `claude-codex-report/v1` whose first line is `DELTA: PASS` or `DELTA: FAIL`, with evidence. At most 500 words.

WRITE_SCOPE: []
