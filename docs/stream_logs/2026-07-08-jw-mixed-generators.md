# Stream ledger — jw-mixed-generators (P2-012 phase-1 + P2-020, 2026-07-08)

Branch: `jw-mixed-generators` (off suite-substrate unit-1). Scope: the
generator engine + six categories + five AP-6 sentinel conditions.
Real-tokenizer manifest GENERATION is a lead-side .venv step (Window-B
prep), not this unit.

### GEN-1 [codex-lens] [contract] Tokenizer identity requires explicit file-manifest rows

Decision: suite builds REQUIRE an explicit tokenizer manifest (per-file
(filename, sha256) rows, B7); the rows are recorded in the annotations
sidecar and their folded hash enters `source_manifest.subset_sha256` and
item ids. No silent fake-identity fallback exists; the fake path passes
an explicit fake manifest.
Why: item_id reproducibility rests on tokenizer identity; a silent
fallback would mint real-looking ids under a fake tokenizer.
Evidence: g1-lens-main finding 1; FIX-1 diff.
Confidence: high. Binds: lead-side real-tokenizer generation step.

### GEN-2 [codex-lens] [contract] Script purity enforced, truthfully recorded

Decision: multilingual ASCII fill is permitted only as a bounded final
tail (`ascii_tail_max=3`), never interleaved; realized count recorded
truthfully; unreachable budgets fail closed.
Evidence: g1-lens finding 2 (live counterexample: 6 interleaved
insertions recorded as 1); FIX-2 diff + regression test.
Confidence: high.

### GEN-3 [codex-lens] [process] Annotations record actual semantics

Decision: every declared generator parameter in sidecar annotations must
match implementation behavior (B3 discipline): reasoning records
`answer_seed_range=[10,80]` + `intermediate_cap=10000` (the earlier
`value_range=[2,60]` claim was false); summarization records
requested_needles AND realized_needles with needles deterministically
inserted before elastic fill (always present or fail-closed).
Evidence: g1-lens findings 3-4; FIX-3/FIX-4.
Confidence: high. Binds: future generator revisions (truthful-provenance
rule).

### GEN-CHECKPOINT

Unit 1 done: joulewise/gensuite package, 6 categories, 5 ids-native
BOS-less sentinels (D-046), DRBG golden vector pinned, independent
reasoning parse/eval tests, bank-hash fail-closed test. 664 green.
Resume action: after suite-substrate merges — rebase; lead-side real-
tokenizer (Qwen2.5-1.5B .venv) manifest generation + committed jw_mixed
+ sentinel manifests; then campaign configs (Window B, [QUIET-MAC]).
Sampler provenance (D-047.5) is substrate unit-3 scope, not here.
