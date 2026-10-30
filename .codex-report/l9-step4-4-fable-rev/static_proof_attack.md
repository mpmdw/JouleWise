# Item 4: attempts to break the static claim-gate proof (test_R3_claim_gate_member_codes_cannot_reach_a_step4_cell)

The test asserts, at a7e00c9f7: (a) neither claim-gate code is reducer vocabulary or a blind MASK code; (b) in the
generator's eleven modules, every `paired_block_incomplete` string constant is the third positional argument of a
`*.stop_if_member_code_on_kept_unit(...)` call; (c) `fixed_n_plan_incomplete` never occurs there.

Attack 1, data-carried code. A bundle's stored precheck `reasons` list is the only place a cell reason is copied from
input data (`inputs.py:4064-4070`). Line 4067 routes any list with a non-reducer member to `window_evidence_precheck_missing`,
so a stored `paired_block_incomplete` cannot be forwarded. `capture_pipeline_refusal` returns fixed literals
(`uncertainty_evidence.py:1473-1486`). `consumption_session.refusal_reasons` and `whole_window_refusals`
(`floor_extraction.py:2196`, `:3311`) come from `whole_window.py`, which is in the eleven. Result: holds today, but the
proof's backing for this route is assertion (a) plus the filter at line 4067, and no test in `tests/b5_analysis` exercises
the filter (mutant M9).

Attack 2, a producer outside the eleven. The extractor's static import closure is 84 files
(`static_proof_probe.txt`); 73 are outside the eleven, including `calibration_bracketing.py` (an R3 producer) and
`analysis_engine/__init__.py`, which holds every other `paired_block_incomplete` / `fixed_n_plan_incomplete` literal
(`:562, :589-590, :615, :632, :778-780, :875, :1013-1015, :1159, :1363`). The closure imports `analyze_claims` only
in `cli.py` and `paper_custody.py`; `floor_extraction.py`, `whole_window.py`, `inputs.py` and
`scripts/extract_detection_floors.py` import nothing from the package root. So the claim gate is not called on the
step-4 path. Result: holds; the limit is the same one the blind generator has (a literal outside the eleven is unseen).

Attack 3, the p42 escape in the stop. `stop_if_member_code_on_kept_unit(..., p42_precheck=True)` returns without
raising on a non-target p42 cell (`kept_units.py:181-184`). Neither `inputs.py:3590` nor `:3746` passes
`p42_precheck`, and the extractor's stop closure (`floor_extraction.py:3210-3211`) passes only the three positionals.
After a silent return at those two sites, nothing appends the code anywhere. Result: holds.

Attack 4, the AST guard's shape. A keyword form `code="paired_block_incomplete"` is not `args[2]`, so the guard fails
closed (mutant M6). A concatenated or f-string form would be invisible to the guard and to the generator alike; the
classifier would then see an unlisted code and class it tooling (fail-closed, stop-side). `id(node)` is stable because
the parsed tree is held while both walks run.

Attack 5, vacuity. The test never asserts that it saw a stop site; with both `inputs.py` stop sites deleted, assertion (b)
is vacuously true. The regeneration test catches that deletion incidentally, because the literal then leaves the
blind tooling list (mutant M12). A direct `assertEqual(seen['paired_block_incomplete'], 2)` would make the pin its own.

Conclusion: the proof holds at this head. Its two soft spots are the behavioral filter it relies on without exercising
(Attack 1) and the vacuous count (Attack 5); neither is a classification error.
