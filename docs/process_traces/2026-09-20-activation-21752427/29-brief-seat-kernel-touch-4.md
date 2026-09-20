SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["docs/process/state_kernel.json", "TASK_QUEUE.md", "RUN_STATE.md", "tests/test_gen_state.py"]

# Kernel touch 4 (activation 21752427): EVIDENCE-NIGHT-ENTRY-01 slice A delivered; lane stays open for slice B; pointer refresh

Cwd is `/Users/edr/code/JouleWise-wt-kernel2-21752427` on branch `bookkeeping/2026-09-20-kernel-touch-2-21752427` at main `2b6cb947`. Same rules and template as kernel touches 2/3 (`git show 8b883831 1e7f2100 --stat`; briefs 16/20 in `docs/process_traces/2026-09-20-activation-21752427/`): regenerate both generated regions with `scripts/gen_state.py` (no args) then `--check` exit 0; `tests.test_gen_state` OK; RUN_STATE.md changes confined to the generated region; no commits/pushes/network/launchctl.

## Edits
1. `EVIDENCE-NIGHT-ENTRY-01` (rank 256): status stays `active`/`queued` per the convention for a partially delivered lane (choose the vocabulary the kernel uses for "in progress; next increment queued"; if only `active` fits, use it). Status note: "2026-09-20 activation 21752427 — slice A (PR 1) MERGED as PR #372 (`2b6cb947`): `python -m joulewise.evidence_night prepare` (clone + locked venv at H, plan sealed by the clone's own code, real generator/installer render-only, resumable on sealed bytes, stops at the notice boundary; contract `docs/contracts/evidence_night_entry.md`). Remaining = slice B: lifecycle façade (render/probe/install/uninstall/verify), pre-arm checks (discovery, census, canonical ancestry/supervisor per NIGHT_HANDBACK §Census, courier-on-PATH), notice acceptance/veto + publication + install orchestration with a narrow transport adapter (after the F3 lifecycle decision in consult 18), handbook/runbook checklist replacing record 17's script set, watchdog census provenance. Evidence: records 18/19/22/22a/23/24/25/25a/26/27/28." Keep the acceptance criteria; mark the delivered ones as met where the row shape allows.
2. `updated` stays 2026-09-20; `latest_report` → `docs/process_traces/2026-09-20-activation-21752427/26-diff-gate-evidence-night-prepare.md`, label "T38p — 2026-09-20: evidence-night prepare command merged (PR #372); pilot night one aborted/harvested; census cure merged".
3. No other row changes; count stays 220.

## Verification: generate + `--check` → 0; `tests.test_gen_state` OK; count; `git diff --stat`; `git diff RUN_STATE.md | head -20`.
## Report: claude-codex-report/v1 envelope, --genre implementation; JSON header < 800 bytes; total < 8 KB.
