```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "One-line delta and standing-rules identity pass; local cure evidence supports the revision, but required remote verification is blocked.",
  "workspace": {
    "base_requested": "1f4c4492",
    "base_mode": "exact",
    "head_start": "1b56c9d26284e06399ad45f39cf310e8c4f4b0b7",
    "head_end": "1b56c9d26284e06399ad45f39cf310e8c4f4b0b7",
    "upstream_end": "83ab38edcacd67312171c0051cc31cc70a9be682",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [],
    "item_1": "Partial: local cure commit, four changed files, expected parent, and non-ancestry against cached origin/main verified; fresh remote checks blocked.",
    "item_2": "Pass: exactly one line replaced in NIGHT_HANDBACK.md; standing-rules block byte-identical to 20f95848.",
    "item_3": "same signature: none",
    "upstream_freshness": "Cached origin/main only; remote freshness unverified."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git ls-remote origin refs/heads/fix/2026-09-09-night-gate-stub-chain refs/heads/main",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": ["fatal: unable to access 'https://github.com/mpmdw/JouleWise/': Could not resolve host: github.com"]
      },
      "expected": {"exit_code": 0, "tail_regex": "bb7090e2.*refs/heads/fix/2026-09-09-night-gate-stub-chain"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git fetch origin fix/2026-09-09-night-gate-stub-chain",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 255,
        "tail": ["error: cannot open '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-ref-308-delta/FETCH_HEAD': Operation not permitted"]
      },
      "expected": {"exit_code": 0, "tail_regex": "FETCH_HEAD"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git show --stat FETCH_HEAD",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": ["fatal: ambiguous argument 'FETCH_HEAD': unknown revision or path not in the working tree."]
      },
      "expected": {"exit_code": 0, "tail_regex": "4 files changed"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git show --stat bb7090e2; git rev-parse bb7090e2^ origin/main FETCH_HEAD; git merge-base --is-ancestor bb7090e2 origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead"]
      },
      "expected": {"exit_code": 1, "tail_regex": "using /tmp instead"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "python3 -B -c 'import subprocess,hashlib; g=lambda *a: subprocess.check_output([\"git\",*a],stderr=subprocess.DEVNULL); p=\"docs/process/NIGHT_HANDBACK.md\"; m=b\"**Standing rules** <!-- F11 -->\"; a=g(\"show\",\"20f95848:\"+p); b=g(\"show\",\"1b56c9d2:\"+p); assert a[a.index(m):]==b[b.index(m):]; print(\"standing-rules block: byte-identical\"); print(\"sha256=\"+hashlib.sha256(b[b.index(m):]).hexdigest()); assert g(\"diff\",\"--name-only\",\"1f4c4492..1b56c9d2\").decode().splitlines()==[p]; assert g(\"diff\",\"--numstat\",\"1f4c4492..1b56c9d2\").decode().strip()==\"1\\t1\\t\"+p; print(\"delta: one file; 1 insertion, 1 deletion\"); print(\"parent=\"+g(\"rev-parse\",\"bb7090e2^\").decode().strip()); print(\"cached origin/main=\"+g(\"rev-parse\",\"origin/main\").decode().strip()); r=subprocess.run([\"git\",\"merge-base\",\"--is-ancestor\",\"bb7090e2\",\"origin/main\"],stderr=subprocess.DEVNULL); assert r.returncode==1; print(\"cure is not ancestor of cached origin/main: exit 1 (expected)\"); print(\"HEAD=\"+g(\"rev-parse\",\"HEAD\").decode().strip()); assert g(\"status\",\"--porcelain\")==b\"\"; print(\"worktree: clean\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "standing-rules block: byte-identical",
          "sha256=81947da269eaa3a6b84c719c2ab83e9ec3d785afb27357f4392e9b18bc6d4aef",
          "delta: one file; 1 insertion, 1 deletion",
          "parent=83ab38edcacd67312171c0051cc31cc70a9be682",
          "cached origin/main=83ab38edcacd67312171c0051cc31cc70a9be682",
          "cure is not ancestor of cached origin/main: exit 1 (expected)",
          "HEAD=1b56c9d26284e06399ad45f39cf310e8c4f4b0b7",
          "worktree: clean"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "worktree: clean"}
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "blocking",
      "text": "GitHub DNS resolution failed; the read-only sandbox denied FETCH_HEAD creation. Local objects and cached remote-tracking refs cannot establish current remote branch or merge status.",
      "needs": "Lead must rerun ls-remote and the authorized fetch in a network-enabled environment permitting Git metadata writes, then verify FETCH_HEAD and non-merge against fresh origin/main."
    }
  ]
}
```

## Findings

No new document finding established.

1. **Cure claim — partially verified.** Local commit `bb7090e2b8d4cfe30effbfb7e89cef802277d448` has parent `83ab38edcacd67312171c0051cc31cc70a9be682`. Its stat lists exactly:

   ```text
   joulewise/night_gate.py
   scripts/run_night.py
   tests/test_night_gate.py
   tests/test_run_night.py
   4 files changed, 152 insertions(+), 53 deletions(-)
   ```

   The cached remote branch points to that commit. It is not an ancestor of cached `origin/main` (exit 1, expected). Fresh remote confirmation remains blocked by E1; `FETCH_HEAD` is unavailable.

2. **Delta boundary — pass.** Only `docs/process/NIGHT_HANDBACK.md` changed: one insertion and one deletion. The standing-rules block is byte-identical to `20f95848`; V5 records its hash.

3. **same signature: none.** The unsupported “cured by” assertion now cites an inspectable commit and explicitly qualifies it as under review and unmerged. The remaining reconciliation statements retain support in 21h/21i and captured artifacts. Inspected artifact tails include:

   ```text
   results-clone pushed and clean
   worktree removed rc=0
   plan root removed rc=0
   message_id=1a08599a4ff4d005
   ```

## Residual risk

This was a documentation delta audit, not verification of the cure’s runtime correctness. No tests or live-machine measurements were run. No files changed; HEAD and the clean worktree remained unchanged.