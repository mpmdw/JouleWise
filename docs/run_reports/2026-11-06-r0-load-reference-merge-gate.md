# PR #686 merge gate: findings dispositions (R0 load reference equivalence)

Lead: laptop lead, interactive session 359dce51, 2026-11-06.

| Source | Finding | Disposition |
|---|---|---|
| Executing review (Opus, at 5cf03e598, `docs/align/reviews/2026-11-06-r0-load-reference-executing-review.md`) | MEDIUM: a null-fixture absolute entry beside a reference entry let unlisted fixtures pass on the absolute limit | Fixed by the reviewer in 76cc22b7c, with an adversarial test |
| Executing review | MEDIUM: the tolerance basis overstated detection power; the sibling fault-injection test missed subtle numeric faults | Fixed in 711f43731: the note and the table basis now state the scope honestly and cite the per-layer HF-vs-MLX evidence. An exact-reproduction tier (1e-3 mean / 1e-2 bin against a pinned profile, comparable only on the same stack) was added. D's pin is taken from the first qualified live R0 |
| Executing review | LOW: any listed tool passed the generation check | Fixed in 711f43731 (`wrong_tool`) |
| Executing review | LOW: the "loss-masked" wording | Fixed in 711f43731 (cause stated as unverified) |
| Executing review | LOW: effort used by the generation check | Superseded by the lead ruling below (effort low) |
| Executing review | LOW: anchor entry unreachable from R0 | Deferred: the anchor is not used by v4 R0. The entry is explicit and documented |
| Executing review | LOW: dangling `$ref` raised KeyError | Fixed in 6ec6ce739 (`schema_ref_unresolved`) |
| Executing review / Fable | LOW: prequal does not test the new gate | Deferred to `lane/2026-11-06-align-v4-prequal` (follow-up: give the sibling its own reference entry; check_load requires `nll_verdict` and generation) |
| Executing review / Fable | LOW: test_r0_checks + test_r0_mlx in one process | Pre-existing on base; not introduced here; each passes in its own process |
| Fable cold pass (at 711f43731, `docs/align/reviews/2026-11-06-r0-load-reference-fable-cold-pass.md`) | HIGH: a non-finite loss made `save_report` raise and left the report at running | Fixed in 6ec6ce739: `nll_losses` is stored only when finite (otherwise `None` plus a count), and the runner records an unserializable row as fail `report_serialization_error`. Runner-level NaN/inf tests added |
| Fable | MEDIUM: a healthy D could spuriously fail the generation check on reasoning length (xhigh, 4,096 cap) | Lead ruling, implemented in 6ec6ce739: the generation turn renders at effort `low`. On `hit_cap` or `unclosed_reasoning` it retries once with the production sampler at seed 96, and the retry decides. Malformed, wrong-tool and schema failures never retry. Both attempts are recorded |
| Fable | MEDIUM: report authority fields did not name the new bar | Fixed in 6ec6ce739: `authority_load_reference`, its blob id at run time, and the basis (RUN_STATE 181/183) |
| Fable | LOW: markdown brief bloat | Fixed in 6ec6ce739 |
| Fable | LOW: third canonicalization in the `references=` path (prequal only) | Deferred to the prequal lane follow-up |
| Fable | LOW: with `--keep-going`, a bad greedy turn counts twice in tool-envelopes | Accepted: R0 runs without keep-going for its verdict, and the row is labelled |
