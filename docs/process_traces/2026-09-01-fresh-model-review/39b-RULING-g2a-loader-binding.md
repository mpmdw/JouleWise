# Ruling 39b — G2-a loader binding (terra fix round 39 returned NEEDS_RULING on L-F4 / L-F5)

Magistrate ruling, 2026-09-01. Seat that raised it: terra xhigh, report `39-terra-fix-g2a.md`
(flags F1, F2 — blocking). Refuter finding under cure: luna `30-luna-refute-g2a-exec.md`
L-F4 (no panel binding in the pin) and L-F5 (hand-edited pin with recomputed hashes is
accepted by `_load_prefill_prompt_pin`).

## What terra found

The `_v5` generator (`configs/campaigns/d117_contrast_v5/generate_configs.py`) is a pure
function of committed inputs: it never opens a tokenizer or a model mirror
(`_load_prefill_prompt_pin` docstring, `:816`; the decode side takes pre-tokenized ids from
the reviewed rendering pinset in the panel, `:1030-1066`). So (F2) the loader cannot
"re-tokenize `prompt_text`" as L-F5(i) asked without inventing a model-mirror read, and (F1)
the generator hashes no panel bytes, so there is nothing for the pin's `panel_sha256` to be
compared with. Both are correct readings of the code; the fix brief assumed a binding that
does not exist.

## Ruling

1. **The no-model-read contract stands.** The loader never loads a tokenizer or model.
   L-F5(i) is AMENDED as follows: the tokenization authority is the probe-input generator
   (`scripts/generate_g2a_probe_inputs.py`), which produced the prompt ladder under the real
   tokenizer and hash-bound it; the issuer copies a ladder rung into the pin. The loader
   therefore checks the pin against the **ladder rung**, not against a fresh tokenization.

2. **The pin becomes a hash-bound bundle.** The pin gains `prompt_ladder: {"path", "sha256"}`
   beside the already-ruled `selection_record: {"path", "sha256"}`; both paths are relative
   to the pin file's directory (L-F5(iii)/L-F6 unchanged). The loader resolves and hashes
   both files; refusals `prompt_ladder_missing`, `prompt_ladder_sha256_mismatch`,
   `selection_record_missing`, `selection_record_sha256_mismatch`. It then takes the ladder
   rung whose `prefill_tokens == prefill_length` (`prompt_ladder_rung_missing` if absent) and
   requires the pin's `prompt_text`, `prompt_text_utf8_sha256`, `prompt_token_ids`,
   `prompt_token_ids_sha256`, `prompt_tokens`, `repeat_count`, `closing_sentence`,
   `generation_method`, and `tokenizer_json_sha256` to equal the rung's field for field
   (`prefill_prompt_pin_ladder_rung_mismatch: <field>`). The ladder's top-level
   `tokenizer_json_sha256` must equal the panel entry's (existing
   `prefill_prompt_pin_tokenizer_sha256_mismatch` covers the pin; add
   `prompt_ladder_tokenizer_sha256_mismatch` for the ladder). L-F5(ii) — construction
   equality `prompt_text == " ".join([PROMPT_SENTENCE] * repeat_count + [closing_sentence])`
   and `generation_method` naming that construction — stays in the loader; it needs no
   tokenizer.

3. **Panel binding (L-F4), narrow call-site change AUTHORIZED.** In `configure_model_pair`,
   compute `panel_sha256 = hashlib.sha256(panel_path.read_bytes()).hexdigest()` — the same
   file `load_model_panel(panel_path)` reads at `:993` — and pass it to
   `_load_prefill_prompt_pin(..., panel_sha256=panel_sha256)`. The loader requires
   `pin.panel_sha256 == ladder.panel_thinking_policy.panel_sha256 == panel_sha256`
   (`prefill_prompt_pin_panel_sha256_mismatch`, naming which of the three disagreed). No
   other change to `configure_model_pair`; the registration bytes are unaffected (the frozen
   hash covers `dominance_criterion_registration()` only — `tests/test_d117_contrast_v5_pack.py:518`).

4. **Scope amendment.** `tests/test_d117_contrast_v5_pack.py` is ADDED to WRITE_SCOPE for
   the pin-plumbing helpers and tests only (`write_prefill_pin`, `rewrite_prefill_pin`,
   `test_prefill_prompt_pin_*`): the synthetic pin must become a self-consistent bundle
   (a two-rung synthetic ladder written beside it whose `panel_thinking_policy.panel_sha256`
   is the sha256 of the real `PANEL` bytes, a synthetic selection record, both hashed into
   the pin). `PINNED_DOMINANCE_CRITERION_BYTES`, every `test_golden_readback_*`, and every
   `test_common_mode_*` test are untouched — the report must show `git diff` of that file
   in full so the delta seat can confirm it.

5. **Desk chain (L-F6).** The issuer writes the bundle — the pin plus verbatim copies of the
   selection record and the ladder, hashes recorded in the pin — into one directory under
   `$G2A_WINDOW_PLAN_ROOT`. The runsheet's desk-day step copies that directory to
   `configs/campaigns/d117_contrast_v5/prefill_pin/` and passes
   `--prefill-prompt-pin configs/campaigns/d117_contrast_v5/prefill_pin/<pin>.json`.
   Committing the ladder (four rungs of token ids, ~100 KB) is accepted: it is the
   pre-registration record of what the tokenizer produced.

6. **What is deliberately not refused.** A coordinated hand edit of pin + ladder + selection
   record with every hash recomputed is the operator-only adversary; under D-161 the loader
   does not defend against it. The evidence-side fence is the run itself: the adapter
   re-tokenizes `prompt_text` on the live clock and records the realized count and ids hash
   (`joulewise/adapters/mlx_runtime.py:400-407`). Whether any analysis-side consumer compares
   that realized hash with the registered `prompt_candidate.per_model[].token_ids_sha256`
   is UNVERIFIED as of this ruling — the magistrate found no such consumer in
   `joulewise/analysis_manifest_v3.py` or `joulewise/floor_extraction.py` by grep. If absent
   it is a kernel row (`V5-PREFILL-REALIZED-IDS-CHECK-01`), not this round's work.

Luna's five edits (L-F5) map to: edited token id with ids hash recomputed → rung mismatch
on `prompt_token_ids`/`prompt_token_ids_sha256`; edited `generation_method` or
`repeat_count` → rung mismatch (and construction inequality); edited selection path →
`selection_record_missing`; edited selection hash → `selection_record_sha256_mismatch`.
Each is a named regression in the round.
