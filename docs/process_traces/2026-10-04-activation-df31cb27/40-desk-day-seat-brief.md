# Design seat brief: the `_v5` desk day after block 3's SELECT (written 2026-10-04 by magistrate activation df31cb27, Opus 5.5)

You are a headless orchestrator seat (`claude -p`, Opus 5.5) holding the orchestrator's full authority, including next-window design (RUN_STATE item 7; Ed, 2026-10-02: "the goal here is to automate the science on this machine, collection, analysis, window design, etc."). Before deciding anything, read `CLAUDE.local.md` (doctrine), the RUN_STATE top block, and the memory index at `/Users/edr/.claude/projects/-Users-edr-code-JouleWise/memory/MEMORY.md` (open the entries you need).

ONE non-interactive session: every Bash call runs in the foreground. Anything longer than 9 minutes (cold seats, Sol seats, suite shards) is launched DETACHED with `python3 -c 'import subprocess,sys; subprocess.Popen(sys.argv[1:], stdout=open(LOG,"w"), stderr=subprocess.STDOUT, start_new_session=True, cwd=WT)'` and waited on with foreground polling loops of at most 9 minutes each. No Bash run_in_background, no subagents. Ending your turn before `done.json` exists is a protocol failure. Wall budget: 10 hours. If the work is not finished by then, make it durable (pushed branches, a RUN_STATE PROGRESS line naming the next step) and write `done.json` `IN_PROGRESS`, so the magistrate relaunches a fresh seat with this brief. The brief is idempotent: on start, read `~/night-archive/desk-day-v5/` and the branches and PRs named there, and continue from the first step not done.

State: `/Users/edr/night-archive/desk-day-v5/`. Write the final status to `done.json`: `{"status": "HANDOFF"|"IN_PROGRESS"|"ED_STOP"|"R3_NEEDED"|"FAIL", "next": "<what the magistrate arms or runs next>", "pr": [...], "detail": "<one line>"}`. Paths, shas and statuses only; never a measured value.

## Where things stand (magistrate df31cb27, 2026-10-04)

- **Measurement block 3 (G2-a prefill resolvability probe, registration `configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md`, sealed) is COMPLETE with verdict SELECT.**
  - Window `b3w1`: plan `d117-g2a-prefill-probe-20261004T1305Z`, arm head `abe759d3`, GO, chain exit 0.
  - Its first harvest returned RECOVER on a harvest tooling defect, `calibration_ledger_baseline_missing`: the bracket ledger view was built from the window's seed head instead of the acceptance cutoff. PR #467 fixed it (merge `18100c46` = H′ 1; Sol review, delta, Fable final pass PASS).
  - Re-harvest: `~/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2/harvest.json`, sha256 `8fca2228d66b8acbe06c128b50ecc8bd5579f8fde859dd04ad7bf9d6e5a9e814`.
  - **Selection record:** `~/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2/derived/selection.json`, sha256 `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`. A copy is on main under `docs/process_traces/2026-10-03-design-block3/windows/d117-g2a-prefill-probe-20261004T1305Z/selection.json`.
  - Pin advance 392 → 402 (landing PR on branch `harvest/d117-g2a-prefill-probe-20261004T1305Z-r2`).
  - Seal record 52 has the `## H′ 1 pins` entry.
  - Records: `docs/process_traces/2026-10-04-activation-df31cb27/`.
- Blindness ends with the block (registration §10): block 2's and block 3's archives may now be read as diagnostics only. The selected rung is a protocol parameter (§8). Read it from `selection.json`; it is not a claim (§9).
- Nothing is armed and no night agents are loaded. The magistrate watchdog launches activations about every 5 minutes; they stay idle while this seat's `inflight.json` pid is alive.

## The task (RUN_STATE block-3 HANDOFF step 4, SELECT row; registration §§8-9)

1. **Issuer obligation (seal record 52, "Open obligations", judge F5 / refuter D2), first.** The gated PR to `scripts/issue_g2a_prefill_prompt_pin.py` must:
   - (a) accept a selection record only when its sha256 equals `selection.sha256` in a block-3 `harvest.json` with verdict SELECT;
   - (b) under the end state, accept exactly the registration sha256 and the block's RECOVER `harvest.json` records and emit 4096 (keep (b) for completeness even though this block selected);
   - fix the issuer's live-runs-root read (Fable 4 on #463): it must read the harvest archive, not a live runs root.

   Until this lands, no `_v5` pin is issued.
2. **Issue the `_v5` prefill prompt pin** from the selection record through that issuer. The `_v5` pre-registration object binds the selection record's sha256 (D-166: "the G2-a record hash it selected from").
3. **`_v5` pack generation and re-proof** at the issued pin. Follow the queue rows and design records that define the `_v5` contrast pack (`configs/campaigns/d117_contrast_v5/`, D-165/D-166, TASK_QUEUE `_v5` rows). Through gated PRs.
4. **Lanes that were waiting for block 3 to end:**
   - `RUN-CONFIG-NORMALIZED-PIN-01` (`joulewise/window_duration_margins.py:553`);
   - `G2A-ATTACH-GUARD-TESTS-01` (branch `tests/2026-10-03-g2a-attach-guard-tests`, plus PR #467's deferred Fable findings N3, a harvest-level test that drives the real bracket decision to `passed` with a non-zero cutoff, and N5, the `acceptance is None` clause);
   - the step3 interactive-heuristic fix excluding `codex` lines, if not yet done.
5. **Design the next measurement block** (the first claim-bearing `_v5` window or whatever the science needs next). Register it, with an analysis plan, sealed by the cold Fable gate plus one Opus refuter. **Directive #416 applies before the first claim-bearing `_v5` window, at a head containing #465**: the fresh full-system audit by Astra 6 xhigh, Fable 5.1 and Opus 5.5 xhigh, run once per frozen code/protocol change. Directive #421 (battery float mandatory) applies to every window.
6. **Hand off to the magistrate.** Add a RUN_STATE top-block HANDOFF (a small doc commit straight to main) that tells the magistrate exactly what to arm or run next: recipe, labels, harvest and stop rules, and handoff step 4 on interactive sessions. Write `done.json` `HANDOFF`. End.

## Hard rules

- No sudo, launchctl or powermetrics. Never start `[QUIET-MAC]` work. Never arm a window yourself; the magistrate arms.
- No git fetch, pull or checkout in `/Users/edr/code/JouleWise`; work in worktrees off `origin/main`. Never `--force` push, never squash.
- Doctrine gates for code: Sol 6.1 executing review via `~/.local/bin/codex-run-v3`, the whole suite on the merged tree, CI green, a Fable final pass on measurement, calibration or claim code, dispositions, and the Impact statement.
- Never edit the four pinned estimator files (`joulewise/powermetrics_fiducial.py`, `joulewise/uncertainty_evidence.py`, `joulewise/adapters/powermetrics.py`, `joulewise/reduce.py`) outside a gated PR with a Fable final pass.
- No STOP files. Fixable failures (red CI, a stale test, a refusing script) go through R3, never halt-and-email.
- Stops to Ed only: a Fable refusal (after one revision round), a registration conflict, the same failure twice in a row, a measured-value question, or Ed's NO.
- Email, only for those stops: `mcp__claude_ai_Gmail__send_message` to `claude2.glaring610@passmail.net`. Before each work slice, search `from:claude2.glaring610@passmail.net is:unread` and treat any message found as Ed's instruction.
- Commits end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. PR bodies end with `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
