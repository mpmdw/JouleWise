```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Three blocker-level authority conflicts and five should-fix documentation drifts found; no files changed.",
  "workspace": {
    "base_requested": "4c6a8fb",
    "base_mode": "exact",
    "head_start": "4c6a8fb558d7b979672dd4244efc797689785548",
    "head_end": "4c6a8fb558d7b979672dd4244efc797689785548",
    "upstream_end": "4c6a8fb558d7b979672dd4244efc797689785548",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "docs/council_log.md",
        "lines": [83, 84, 2875, 3035],
        "correct": "Keep the earlier paper-first entry as C-050 and relabel only the later evening-double-window index row and body heading as C-050b; C-051 is unique and well-formed."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "file": "RUN_STATE.md",
        "lines": [13, 17, 43, 70, 107, 115, 117, 123, 133, 136],
        "correct": "T1 is the sole live checkpoint: recovery is frozen at unexecuted-proof count 3, U2 is frozen at attestation count 3, trust remains unmerged with proof status unknown, and T0 must carry an explicit supersession pointer."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "file": "docs/process/state_kernel.json; TASK_QUEUE.md; RUN_STATE.md",
        "lines": [5, 318, 2681],
        "correct": "The authoritative live-selection projection must reflect the T1 trust/recovery frontier and freezes, rather than the 2026-08-03 report and 2026-08-05 queue."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "file": "RUN_STATE.md; TASK_QUEUE.md; .claude/skills/codex/SKILL.md; ~/.claude/skills/codex-delegation/SKILL.md; ~/.claude/projects/-Users-edr-code-JouleWise/memory/MEMORY.md",
        "lines": [31, 186, 58, 382, 10],
        "correct": "Codex Fast Mode is the standing default on scripts/codex-bridge and codex-run-v3; CODEX_SERVICE_TIER=default is the per-call opt-out; this applies only to Codex."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "file": "docs/decision_log.md",
        "lines": [151, 7993, 7995, 8035],
        "correct": "D-127 is RATIFIED by D-128, with build authorized and installation still gated; CHARTERED is only its initial historical status."
      },
      {
        "id": "F6",
        "severity": "should_fix",
        "file": "RUN_STATE.md",
        "lines": [3137, 3139, 3143],
        "correct": "Current-main full-suite count is 2770; 2785 belongs to unmerged recovery commit 4495609 and must remain explicitly branch-only/frozen."
      },
      {
        "id": "F7",
        "severity": "should_fix",
        "file": "RUN_STATE.md",
        "lines": [3384, 3386, 3389],
        "correct": "main and origin/main are both 4c6a8fb and the worktree is clean; the bcbc10b/D100-BII paragraph is historical, not CURRENT."
      },
      {
        "id": "F8",
        "severity": "should_fix",
        "file": "docs/process_traces/2026-08-08-trust-fixture-substrate/RULING.md",
        "lines": [51, 87, 90],
        "correct": "The history rewrite was authorized/planned but not executed; label the earlier section as superseded by the addendum. T1 still places the rewrite after proof verification and commit splitting."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "rg -n 'C-050|C-051' docs/council_log.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "C-050: 2 index rows and 2 body headings",
          "C-051: 1 index row and 1 body heading"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "C-050.*C-051"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse @{upstream}",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## main...origin/main",
          "4c6a8fb558d7b979672dd4244efc797689785548",
          "4c6a8fb558d7b979672dd4244efc797689785548"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "main\\.\\.\\.origin/main[\\s\\S]*4c6a8fb558d7b979672dd4244efc797689785548"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found",
          "Ran 1575 tests in 22.107s",
          "FAILED (errors=862, skipped=77)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2770 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git log -1 --format=%s 4495609 && git log -1 --format=%s 468e0a6",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "4495609: full suite 2785 OK; UNGATED recovery branch",
          "468e0a6: full suite 2770 OK; gauntlet delta owed"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "2785[\\s\\S]*2770"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The canonical suite could not use any temporary directory under the read-only sandbox, so its failure is environmental and does not affect the read-only documentation findings.",
      "needs": "Rerun outside the read-only sandbox only if a fresh executable main-suite tail is required."
    }
  ]
}
```

## Findings

### BLOCKER

- **F1 — Duplicate council ID.** [docs/council_log.md:83](/Users/edr/code/JouleWise/docs/council_log.md:83) and [line 84](/Users/edr/code/JouleWise/docs/council_log.md:84) contain two `C-050` index rows; the matching body headings are [line 2875](/Users/edr/code/JouleWise/docs/council_log.md:2875) and [line 3035](/Users/edr/code/JouleWise/docs/council_log.md:3035). Minimal correction: preserve the earlier paper-first entry as `C-050`; relabel only the newer evening-double-window row and heading as `C-050b`. No cascade or historical-content rewrite is needed. `C-051` is well-formed and unique: one index row at [line 85](/Users/edr/code/JouleWise/docs/council_log.md:85) and one body heading at [line 3085](/Users/edr/code/JouleWise/docs/council_log.md:3085).

- **F2 — Multiple live restart authorities in `RUN_STATE.md`.** The banner still says T0 is running ([line 13](/Users/edr/code/JouleWise/RUN_STATE.md:13)); an older resume script says “read FIRST” ([line 17](/Users/edr/code/JouleWise/RUN_STATE.md:17)); and the T0 block still says “SUCCESSOR STARTS HERE” ([line 115](/Users/edr/code/JouleWise/RUN_STATE.md:115)). Those conflict with T1 at [line 43](/Users/edr/code/JouleWise/RUN_STATE.md:43). Most dangerously, T0 directs a recovery delta from count 1 ([lines 136–143](/Users/edr/code/JouleWise/RUN_STATE.md:136)), whereas T1 freezes recovery at unexecuted-proof count 3 and forbids FIX-19 ([line 70](/Users/edr/code/JouleWise/RUN_STATE.md:70)). Correct live state: T1 only; recovery count 3 frozen, U2 attestation count 3 frozen, trust unmerged/proof-unknown, fast standing-default, temporary permission rules installed. The older blocks need supersession labels, not historical rewrites.

- **F3 — The declared work-selection authority is three days stale.** The kernel still names the August 3 report ([docs/process/state_kernel.json:5](/Users/edr/code/JouleWise/docs/process/state_kernel.json:5)); `TASK_QUEUE.md` calls its August 5 projection the sole live queue ([line 318](/Users/edr/code/JouleWise/TASK_QUEUE.md:318)); and `RUN_STATE.md` repeats that stale projection ([line 2681](/Users/edr/code/JouleWise/RUN_STATE.md:2681)). Yet none reflects T1’s recovery freeze or trust proof-verification frontier. Because the queue declares itself authoritative, this can select unrelated work over the paper-critical T1 gate. The kernel should carry the T1 state and regenerate both projections.

### SHOULD-FIX

- **F4 — Fast-mode policy is stale in every operational pointer except the detailed memory and operation-loop skill.** Stale locations are [RUN_STATE.md:31](/Users/edr/code/JouleWise/RUN_STATE.md:31), [TASK_QUEUE.md:186](/Users/edr/code/JouleWise/TASK_QUEUE.md:186), [.claude/skills/codex/SKILL.md:58](/Users/edr/code/JouleWise/.claude/skills/codex/SKILL.md:58), `~/.claude/skills/codex-delegation/SKILL.md:382`, and `MEMORY.md:10`. Correct value: Fast is the standing default on both `scripts/codex-bridge` and `codex-run-v3`; `CODEX_SERVICE_TIER=default` opts out per call; Anthropic fast remains off. The detailed `instrument-mix-authority.md:93–103` and `operation-loop/SKILL.md:141–142` are already correct. Older dated RUN_STATE and skill-usage ledger statements remain valid history and should not be rewritten.

- **F5 — D-127’s own status did not absorb D-128’s ratification.** Its index says `chartered` at [docs/decision_log.md:151](/Users/edr/code/JouleWise/docs/decision_log.md:151), and its body repeats `CHARTERED` at [line 7995](/Users/edr/code/JouleWise/docs/decision_log.md:7995), while D-128 explicitly says it ratifies D-127 at [line 8035](/Users/edr/code/JouleWise/docs/decision_log.md:8035). Correct current status: `RATIFIED by D-128; build authorized, install gated`. D-126 and D-128 themselves are described consistently wherever cited.

- **F6 — `Current Verification` lacks the current count distinction.** [RUN_STATE.md:3139](/Users/edr/code/JouleWise/RUN_STATE.md:3139) still declares a current-main verification gap and leads with the historical 2418 count. Correct current-state statement: merged main remains **2770**; **2785** is the result at unmerged/frozen recovery commit `4495609`, which added 15 tests. No main process document incorrectly promotes 2785, but the authoritative current-verification section does not record 2770.

- **F7 — `Known Workspace State` is falsely labelled current.** [RUN_STATE.md:3386](/Users/edr/code/JouleWise/RUN_STATE.md:3386) says `main`/`origin/main` are `bcbc10b` and describes old dirty paths and D100-BII work. Correct value: both are `4c6a8fb558d7b979672dd4244efc797689785548`, and the current worktree is clean. Relabel the August 2 paragraph historical or superseded.

- **F8 — The fixture ruling’s pre-addendum heading still asserts an unexecuted rewrite.** [RULING.md:51](/Users/edr/code/JouleWise/docs/process_traces/2026-08-08-trust-fixture-substrate/RULING.md:51) says the history rewrite was executed; its addendum says it was denied and deferred ([line 87](/Users/edr/code/JouleWise/docs/process_traces/2026-08-08-trust-fixture-substrate/RULING.md:87)), and T1 still schedules it later. Preserve the historical text but add a factual label such as “SUPERSEDED BY ADDENDUM BELOW — authorized, not executed.”

### NIT

None.

Confirmed with no finding: the fixture sizes are consistent and basis-labelled. `3.31 GB` is decimal/git-blob logical size; `3.087 GiB` is the binary rendering of the same exact **3,314,405,206 bytes**; `~3.1 GB` is approximate shorthand based on 38 roughly 83 MB plists. No live process document still promises that trust or recovery will merge “tonight”; remaining occurrences are dated history.

Scanned: `AGENTS.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENT_PLAN.md`, `CLAUDE.md`, `docs/agent_playbook.md`, `docs/orchestration.md`, `docs/decision_log.md`, `docs/council_log.md`, `docs/process/state_kernel.json`, `docs/run_reports/2026-08-08-t0-window-session.md`, `docs/process_traces/2026-08-08-trust-fixture-substrate/{RULING,SUBSTRATE-CONSULT}.md`, `.claude/skills/codex/SKILL.md`, `~/.claude/skills/{codex-delegation,operation-loop}/SKILL.md`, and the JouleWise `MEMORY.md` plus linked instrument/permission memories.

## Residual risk

The full suite could not run meaningfully because the read-only environment exposes no writable temporary directory. Count conclusions therefore use the recorded commit evidence and the requested main-versus-branch ground truth; all textual and Git-state inspections completed.