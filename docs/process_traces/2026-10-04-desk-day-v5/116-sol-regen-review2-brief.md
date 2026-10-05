# Executing review (Sol 6.1 high, non-author): PR #481 round 2 (head cfd51a96)

Worktree: /Users/edr/code/JouleWise-wt-dd5-rgrev2, detached at cfd51a96 (parent main b2ff2f36; round 1 was c3f4ea14). Diff: `git diff b2ff2f36 cfd51a96`. The cold Fable pass on round 1 (`/Users/edr/night-archive/desk-day-v5/fable-regen.md`) failed it on F1 (shared NEG-8 and window-reference configs edited in place broke historical pins) and F2 (interior reference run ids → three midpoint references fail the whole-window verdict). Round 2: shared directories restored, 75 s copies in `configs/campaigns/neg8_reference_corpus_v5/` and `window_references_v5/`, used by the `_v5` packs and (opt-in `v5_references=True`) by `scripts/gen_g2_phase_d.py`; run-id change reverted.

Check by running code: (1) `git diff --quiet b2ff2f36 cfd51a96 -- configs/campaigns/neg8_reference_corpus configs/campaigns/window_references`; (2) every historical consumer Fable listed still verifies (`tests/test_d117_floor_qwen25_1p5b_plan.py tests/test_d117_floor_qwen25_7b_plan.py tests/test_d117_v3_family.py tests/test_d117_decode_contrast_plan.py tests/test_receipt_histsem.py`, and `scripts/check_window_provenance.py` on one block-3 window record if it has a replay mode); (3) regenerate the three packs in a /tmp clone and diff: empty; each committed pack's emitted `generate_configs.py --check` passes; (4) every config the `_v5` packs and the opt-in G2-b render dispatch has idle 75; the default render is byte-identical to main and `--check` passes; (5) GAMMA's interior references are as on main; (6) `tests/test_d117_*v5*.py tests/test_d165_rationale_census.py tests/test_gen_g2_phase_d.py tests/test_v5_pack_regen.py`.

Verdict line first: `REVIEW: PASS` or `REVIEW: FAIL`, then findings with severity and evidence.

WRITE_SCOPE: []
Scratch: /tmp/dd5-rgrev2/ only. No background processes. Finish in this turn.
