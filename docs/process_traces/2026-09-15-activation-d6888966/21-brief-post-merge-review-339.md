# Post-merge cross-unit integration review — PR #339 merged into main at `e7cf1fe3` (row 11, second half)

SESSION_MODE: delegated
WRITE_SCOPE: []

Read-only. Worktree `/Users/edr/code/JouleWise-wt-postmerge-339` (detached at `e7cf1fe3`, the merge commit of PR #339). Never touch `/Users/edr/code/JouleWise`, other worktrees, `/Users/edr/JouleWise-measurement-*`, `~/Library/LaunchAgents`, `/Users/edr/night-custody`. No network. You may write under `/tmp` only. Run single modules (`TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest ...`), not the full suite.

## What merged
`git show --stat HEAD` and `git diff HEAD^1..HEAD`: `configs/campaigns/d117_contrast_v5/generate_configs.py:2697` now emits `roots: {claim_root_leaf, bound_root_leaf}`; two regressions in `tests/test_d117_contrast_v5_pack.py` and `tests/test_arm_readiness_evidence_t0.py`. Pre-merge evidence (on main): `docs/process_traces/2026-09-15-activation-d6888966/11-…20-…` (read 13, 15, 16, 19).

## Cross-unit questions (the ones a per-diff refuter does not ask)
1. Integration on main: with the bookkeeping commits merged since `664b3f6c` (state kernel rows A197–A200, generated queue regions), does everything that imports the contrast v5 generator or reads plan-tree roots still pass together on THIS head? Run: `tests.test_d117_contrast_v5_pack`, `tests.test_arm_readiness_evidence_t0` (exclude the G4 census test by name if `pgrep` fails in your sandbox — say so), `tests.test_d165_dominance_closeout`, `tests.test_gamma_unit_roster_guard`, `tests.test_issue_g2a_prefill_prompt_pin`, `tests.test_campaign_generator_core`, `tests.test_gen_state`, and `python3 scripts/gen_state.py --check`.
2. Registry consistency: `configs/arm_readiness/d117_row_registry_v2.json` successor_pack_ids name the GAMMA pack; does any registry/histsem/pinset artifact on main embed a digest of the contrast v5 generator or of a GAMMA plan tree that this change would now contradict? Cite files and lines; "none" must be shown by the grep you ran.
3. Does any script under `scripts/` (pack authoring, freeze, projection, desk tools) construct or read `roots` with the legacy keys? Cite.
4. Anything the merge commit itself (a merge of `804eb394` with main) resolved oddly — compare `git diff 804eb394..HEAD -- configs tests joulewise scripts` (must be empty or bookkeeping-only).

## Report
claude-codex-report/v1 envelope (genre `review`, under 8192 bytes): verdict CLEAN / FINDINGS with severity, file:line, the test tails verbatim, and what you could not verify.
