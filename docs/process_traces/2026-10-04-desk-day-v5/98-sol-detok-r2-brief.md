# Fix seat round 2 (Sol 6.1 high): PR #480 detokenizer, cold-pass findings

Worktree: /Users/edr/code/JouleWise-wt-dd5-detok (branch fix/2026-10-05-detokenizer-outside-prefill, head 33b68dfd). Scratch /tmp/dd5-detok2/ only. Leave changes uncommitted; never push.

Cold Fable pass FAILED: `/Users/edr/night-archive/desk-day-v5/fable-detok.md` (probe `/tmp/dd5-fable-dt/probe_class.py`). Fix:
- **F2 (MAJOR):** the optimized path records the tokenizer identity class as `PreparedTokenizerWrapper`, the fallback as `TokenizerWrapper`; identity pins (`joulewise/identity_pins.py:2476`), analysis matching (`joulewise/analysis_engine/inputs.py:2912`) and the determinism gate compare that field. The recorded tokenizer identity must be byte-identical to before the PR on both paths (have `_tokenizer_identity` report mlx-lm's wrapper class, or avoid the subclass). Add a test that the tokenizer identity record is equal on the optimized path, the fallback path and the parent behavior.
- **F1 (BLOCKER):** `tests/test_suite_control_parity.py:523` pins the generator record exactly; the PR added `detokenizer`. Update that pin deliberately to the new exact shape (do not loosen the comparison), and grep for every other exact-shape pin on `workload_provenance.generator` (tests and `joulewise/`) and run them.
- **F4 (LOW):** guard the detokenizer construction in `prepare()` so a failure becomes the structured fallback with its reason recorded, not a raw exception.
- F3 (determinism gate does not see the detokenizer path): no code change; the lead records it.
Run `tests/test_mlx_runtime*.py tests/test_adapter*.py tests/test_suite_control_parity.py tests/test_identity_pins*.py tests/test_determinism_gate*.py` and any file your grep finds. Finish in this turn.

WRITE_SCOPE: ["joulewise/adapters/mlx_runtime.py", "tests/test_mlx_runtime_detokenizer.py", "tests/test_suite_control_parity.py"]
