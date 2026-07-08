# Stream ledger — affine-ladder (P2-010b, 2026-07-08)

Branch: `affine-ladder` (off suite-substrate unit-1). Scope: workload core
+ smoke-ladder manifest generator; the envelope-gate analysis script is a
follow-on unit (needs the merged reducer).

### AFF-1 [lead+codex-lens] [contract] Sentinel is a dedicated item — D-047.2 accounting amendment

Decision: the smoke sentinel is its own derived item
(`derive_item(seed, n_iter=1, item_index=8)`, id `affine_v1_sentinel`),
executed at suite start and end (both tagged `sentinel`, own blocks).
Ordinary level items i00..i07 carry no sentinel tag. Accounting: k=25
distinct items, 26 executions (amends D-047.2's "k=24 distinct" — the
prior shape would have tagged ordinary L01/i00 as sentinel, corrupting
the 8-distinct-items-per-level denominator).
Alternatives: duplicate L01/i00 with tag (rejected — level denominator
7 vs 8); untagged duplicates (rejected — SUB-1 validation).
Evidence: b1-lens-main finding 1-2; regenerated manifest
`24fb008b...`; config pin `cd113411...`.
Confidence: high. Binds: D-047 gets a dated accounting-amendment line at
bookkeeping; envelope-gate script excludes tag `sentinel` items from
level stats.

### AFF-2 [codex-lens] [contract] Scorer is ASCII-only

Decision: `score_response` matches `[+-]?[0-9]+` (ASCII); unicode digits
(Arabic-Indic, fullwidth) are malformed.
Why: Python `\d` is unicode-aware; "decimal integer" in the output
contract means ASCII; leniency here would silently score non-conforming
outputs correct.
Evidence: b1-lens finding 3; test matrix rows.
Confidence: high. Binds: AP-5 scored campaign.

### AFF-3 [lead] [contract] Raw-completion prompt delivery (report §1.2 deviation)

Decision: `render_prompt` emits raw completion text; NO chat template
(report C §1.2's "through the model's chat template" contradicts adapter
reality — no chat-template path exists in `_prompt_for_workload`).
Evidence: lead scoping catch; LEAD PIN 1 in the stream prompt.
Confidence: high. Binds: any future chat-template mode re-pins prompt
identity and budgets (tokenizer_id scope per report B §0.3).

### AFF-4 [lead] [contract] Output policy normalized to pinned vocabulary

Decision: `natural_eos` + `planned_output_tokens=16` (not the report's
`natural_eos_capped` string; SUB-3 vocabulary is closed).
Confidence: high. Binds: manifest authors.

### AFF-CHECKPOINT

Unit 1 done: workloads.py, generator, manifests, config, tests (660
green incl. byte-determinism + injection tests). Ref path fixed to
repo-root-relative (substrate SUB-5 convention). Resume action: after
suite-substrate merges, rebase, live mock affine smoke run, then the
envelope-gate analysis script unit (E1-E4 + E5 advisory per D-047.3/4).
