# Refuter brief — GAMMA root-key fix (`fix/2026-09-15-gamma-root-keys` @ `678d9bcc`, one seat, both lenses)

SESSION_MODE: delegated
WRITE_SCOPE: []

Read-only. Worktree `/Users/edr/code/JouleWise-wt-ref-gamma` (detached at `678d9bcc`). Never touch `/Users/edr/code/JouleWise`, other worktrees, `/Users/edr/JouleWise-measurement-*`, `~/Library/LaunchAgents`, `/Users/edr/night-custody`. No network. Temp under `/tmp`. Run single modules. You may copy files to `/tmp` to try mutations there (e.g. `git worktree`-free: copy the repo subtree or use `python3 -c` against a mutated temp copy); never edit this worktree.

## Under review
`git diff 664b3f6c..678d9bcc` — three files, 66 insertions, 1 deletion. Defect: `configs/campaigns/d117_contrast_v5/generate_configs.py:2697` emitted `roots: {claim_leaf, bound_leaf}`; the T-0 reader `joulewise/arm_readiness_evidence_t0.py:1014–1020` requires `claim_root_leaf` / `bound_root_leaf`. Context: seat report `/tmp/magistrate-d6888966/12-gamma-keys-astra.md` (read it; it lists the pre-edit reader census). Scout context: the GAMMA `_v5` pack directory does not exist on main yet; this generator will produce it after the G2-a pin is issued.

## Lens 1 — contract
1. Is `{claim_root_leaf, bound_root_leaf}` the ONE canonical `roots` key set for plan trees across every reader on this tree (`joulewise/arm_readiness.py`, `arm_readiness_evidence_t0.py`, `scripts/`, `tests/`)? The seat says `arm_readiness.py:8506–8521` reads old keys under `root_namespace`, not `roots` — verify that claim by reading the code, and say whether a `roots`-shaped mapping ever flows there.
2. The historical contrast generators v1/v2/v3 and their committed `plan_tree.json:938–939` still carry the old keys. Does any CURRENT reader consume those historical trees' `roots` (predecessor chains, dominance closeout, histsem verifier)? If yes, is the historical shape a latent defect or a frozen artifact that must not change (D-134/D-139 freeze semantics)? Cite lines.
3. Is the fix complete inside the v5 contrast generator (any other emitter/consumer of `roots` in that file — the seat cites `:1882–1883` already canonical) and in the v5 floor generators (`configs/campaigns/d117_floor_qwen3-1p7b_v5`, `-8b_v5`)?
## Lens 2 — execution
4. Run `python3 -B -m unittest tests.test_d117_contrast_v5_pack tests.test_arm_readiness_evidence_t0` (the G4 census test needs a real `pgrep`; if it fails in your sandbox with "Cannot get process list", say so and exclude it by name).
5. Mutation: in a `/tmp` copy, revert line 2697 to the old keys and run the two new regressions; both must fail. Then mutate the T-0 regression's fixture to use the old keys and confirm the refusal branch is the real one (the regression must call the real function that contains line 1017, not a re-implementation).
6. Test quality: do the regressions name the counterfactual input and the production call site? Are they isolated (tempdirs cleaned; no leaked processes)?

## Report
claude-codex-report/v1 envelope (genre `review`), under 8192 bytes: verdict LANDABLE / FIX-FIRST with a severity-tiered list (blocker / should-fix / nit), each with file:line and the counterfactual; the mutation results verbatim (tails); anything you could not verify.
