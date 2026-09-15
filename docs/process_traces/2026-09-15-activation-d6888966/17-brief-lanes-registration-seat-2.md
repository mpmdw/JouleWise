# Seat brief — register two kernel lanes from the GAMMA counter-review (PLAN-TREE-ROOTS-CONTRACT-01, ROOT-NAMESPACE-FALLBACK-01)

SESSION_MODE: delegated
WRITE_SCOPE: ["docs/process/state_kernel.json","tests/test_gen_state.py","TASK_QUEUE.md","RUN_STATE.md"]

Worktree `/Users/edr/code/JouleWise-wt-lanes-d6888966`, branch `chore/2026-09-15-lanes-d6888966` at origin/main (run `git rev-parse --short HEAD` and cite it). Do NOT commit. Never touch `/Users/edr/code/JouleWise`, other worktrees, `/Users/edr/JouleWise-measurement-*`, `~/Library/LaunchAgents`, `/Users/edr/night-custody`. No network. `RUN_STATE.md`/`TASK_QUEUE.md` change ONLY inside the generator-owned marker fences via `python3 scripts/gen_state.py`.

## Task
Register two tasks in `docs/process/state_kernel.json` in the shape of the rows registered this morning (`git show 664b3f6c -- docs/process/state_kernel.json tests/test_gen_state.py`: `WATCHDOG-STALE-EXIT-CLASS-01`, `FIXTURE-FAKE-VLLM-LEAK-01`), ranks 199 and 200, lane `agent`, status `queued`, magistrate registration (not a ruling) in `authority.label`. Regenerate, `--check` rc 0, update the row-count assertion (172 + 2 = 174 with the dated comment convention), run `python3 -m unittest tests.test_gen_state`, paste tails.

### Lane 1 — PLAN-TREE-ROOTS-CONTRACT-01 (priority `p2_next_slice`)
Goal: the plan-tree `roots` key set (`claim_root_leaf` / `bound_root_leaf`) has no ONE home in `docs/contracts/` or `docs/specs/`; it lives only in two readers (`joulewise/arm_readiness_evidence_t0.py:1014–1020`, `joulewise/arm_readiness.py:8505–8521`) and one emitter per campaign generator (`configs/campaigns/*/generate_configs.py`), which is how the GAMMA `_v5` generator drifted to `claim_leaf`/`bound_leaf` unnoticed (fixed in PR #339).
Acceptance summary: a short plan-tree schema section in the owning contract under `docs/contracts/` names `roots.claim_root_leaf` / `roots.bound_root_leaf` as the sole canonical pair and the refusal both readers raise; a repo-wide regression asserts every generator named by the live arm-readiness registry roster (`configs/arm_readiness/d117_row_registry_v2.json` successor_pack_ids) emits exactly that pair; the contract text itself goes through a cold-gate or Ed step because creating contract text is process-bearing (rule 11); historical v1–v3 trees are left byte-identical (D-134/D-139).
Evidence: `docs/process_traces/2026-09-15-activation-d6888966/16-gamma-opus-counter-review.md` (F2); `13-gamma-apex-gate-and-prune.md` (Q4a); `15-gamma-findings-triage-delta-fresh-eyes.md` (row 3 table).
Authority: 2026-09-15 activation d6888966 records 13/15 (magistrate registration from the Opus counter-review; not a ruling).

### Lane 2 — ROOT-NAMESPACE-FALLBACK-01 (priority `p3_hardening_candidates`)
Goal: `joulewise/arm_readiness.py:8511–8514` lets a `tree["root_namespace"]` mapping (`claim_leaf`/`bound_leaf`) override the canonical `roots` pair in the receipt-side frozen-leaf binding; no producer of `root_namespace` exists anywhere in the repository (`grep -rl root_namespace configs/` is empty), and the T-0 reader has no such fallback, so a hand-written tree carrying it would pass the receipt binding and be refused by the T-0 author — a split verdict between two gates on one fact, inside a fail-closed evidence binding.
Acceptance summary: the fallback is deleted (preferred) or mirrored identically in both readers, decided by the seat with a written reason; a regression feeds a tree with canonical `roots` plus a conflicting `root_namespace` to BOTH readers and asserts the same verdict; paired refuters (contract + execution) because it is live code under a fail-closed binding; not night-critical; no change to refusal strings.
Evidence: `docs/process_traces/2026-09-15-activation-d6888966/16-gamma-opus-counter-review.md` (F3); `13-gamma-apex-gate-and-prune.md` (Q4b); `joulewise/arm_readiness.py:8505–8522` (cite what you read).
Authority: same as lane 1.

## Verification to paste
`python3 scripts/gen_state.py && python3 scripts/gen_state.py --check; echo rc=$?`; `python3 -m unittest tests.test_gen_state 2>&1 | tail -3`; `git status --short`; `git diff --stat`.

## Report
claude-codex-report/v1 envelope: changed files, ranks, tails, any schema conflict (stop with NEEDS_RULING rather than guess).
