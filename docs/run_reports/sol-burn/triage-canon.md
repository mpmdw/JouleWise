# Triage of sol/burn-canon (lead-side verification, 2026-11-06)

Errors: CI is not "the sole workflow" (gate-ledger.yml is a REQUIRED check;
d117-production-proof.yml is dispatch-only). origin/port/qwen4-exp-mlx DOES exist, along
with the qwen4exp lanes; cloud Sol could not see them. The RUN_STATE citations are off
(the port pointer is at line 1245, not 1195-1202; ":37 (paragraph at 394)" is wrong).
The block-5 release entry is stale against DLE-1 (release_b5.py, lean-release lane).
harvest_b5_window.py and tools/b5_equivalence/compare_b5_results.py are listed as
superseded but are the canonical tools for distinct jobs (harvest; the D-188
equivalence gate). tools/normalized_compare.py is the superseded one.
The ALIGN v4 R0 runner, R1 driver and v4 kit are not on main. They live on
lane/2026-11-05-align-pilot10-benign and the R1 integration lane.
