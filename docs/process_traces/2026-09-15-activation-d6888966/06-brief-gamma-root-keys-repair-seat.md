# Seat brief — GAMMA plan-tree root keys (PACK-ROOT-SUCCESSOR-V5-01 scout row "GAMMA root-key repair", start_now)

SESSION_MODE: delegated
WRITE_SCOPE: ["configs/campaigns/d117_contrast_v5/generate_configs.py","tests/test_d117_contrast_v5_pack.py","tests/test_arm_readiness_evidence_t0.py"]

Worktree `/Users/edr/code/JouleWise-wt-gamma-keys`, branch `fix/2026-09-15-gamma-root-keys` at `664b3f6c` (origin/main). Do NOT commit (the lead commits by pathspec). Never touch `/Users/edr/code/JouleWise` (frozen canonical root), any other worktree, `/Users/edr/JouleWise-measurement-*`, `~/Library/LaunchAgents`, or `/Users/edr/night-custody`. No network. Temp under `/tmp`. Run single modules, not the full suite.

## Defect (bench-verified by the lead at 664b3f6c)
`configs/campaigns/d117_contrast_v5/generate_configs.py:2697` emits the GAMMA pack's `plan_tree.json` with
`"roots": {"claim_leaf": CLAIM_ROOT_LEAF, "bound_leaf": BOUND_ROOT_LEAF}`. The production consumer
`joulewise/arm_readiness_evidence_t0.py:1014–1020` reads `roots.get("claim_root_leaf")` / `roots.get("bound_root_leaf")`
and refuses with "arm roots do not derive from frozen leaves" when they are absent. The same generator's other emitter
at `:1882–1883` already uses `claim_root_leaf` / `bound_root_leaf`. So a GAMMA pack generated today can never pass the
pack-night T-0 root check. Scout report: `docs/process_traces/2026-09-15-activation-d6888966/04-pack-root-scout-report.md` (Q4).

## Task
1. Before editing, grep the repository for every reader of `"claim_leaf"` / `"bound_leaf"` under `roots` (joulewise/, scripts/, tests/, configs/). Report each hit. If any production reader depends on the OLD names, STOP with NEEDS_RULING (do not change either side).
2. Fix line 2697 to emit `claim_root_leaf` / `bound_root_leaf`, matching `:1882–1883` and the T-0 reader.
3. Regressions (defect-shaped; each must FAIL on the unfixed generator and PASS after — run them both ways and paste both tails):
   - in `tests/test_d117_contrast_v5_pack.py`: the generated plan tree's `roots` mapping has exactly the keys `{"claim_root_leaf","bound_root_leaf"}` with the leaf constants as values (use the existing in-memory/tempdir generation pattern in that module; no network, no real model);
   - in `tests/test_arm_readiness_evidence_t0.py`: a generated GAMMA `roots` mapping passes the root-leaf check that contains line 1017 (call the smallest function that contains it, with two empty distinct arm-root directories named after the leaves), and the pre-fix shape `{"claim_leaf","bound_leaf"}` is refused with "arm roots do not derive from frozen leaves".
4. Verify: `python3 -B -m unittest tests.test_d117_contrast_v5_pack tests.test_arm_readiness_evidence_t0 2>&1 | tail -3`; also run any test that pins the generator's bytes or sha (grep `generate_configs` in tests/) and report if one now fails — do not edit outside scope; report instead.
5. Optional, only if cheap: run `python3 -B configs/campaigns/d117_contrast_v5/generate_configs.py --panel configs/model_panels/qwen3_4bit.json --model-a qwen3-1p7b --model-b qwen3-8b --prefill-length 512 --output-root /tmp/magistrate-d6888966/gamma-inventory` and report the refusal reason (the scout expected `prefill_prompt_pin_unresolved`); this is inventory evidence, not a fix target.

## Report
Final message in the claude-codex-report/v1 envelope: readers found in step 1, the diff summary, both regression tails (pre-fix FAIL, post-fix PASS), the pin-test result, and residual risk. Do not guess; NEEDS_RULING on any conflict.
