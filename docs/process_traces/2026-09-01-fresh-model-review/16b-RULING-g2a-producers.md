# Magistrate ruling 16b — G2-a probe producers (R1–R4)

Date: 2026-09-01. Seat: Fable magistrate. Input: `16-sol-g2a-executability-scout.md`
(Sol xhigh, read-only, `feat/2026-09-01-g2a-probe` at bc19bfb6). The scout's
bottom line is confirmed by the flow map (`11-sol-v5-artifact-flow.md`,
verified by `15-terra-verify-11-flowmap.md`): **nothing in the repository
produces the eight G2-a probe directories, their manifests and member configs,
the frozen probe plan, the identity/T1 vectors, or the post-selection prompt
pin.** The runsheet calls them "lead-prepared"; no lead has a producer.

The scout raised three rulings. All three are ruled here, plus a fourth the
scout treated as an engineering default. Each ruling is binding on the
implementation brief (`run-impl-g2a.md`) and is open to refutation by the
review seats — a refuter who thinks a ruling is wrong reports it as
`NEEDS_RULING`, not as a silent deviation.

## R1 — prompt source, cuts, and workload equivalence: Option A, with a closing-sentence rule

The probe measures the workload `_v5` will later consume, so the probe text at
the selected rung IS the `_v5` prompt text (the pin carries `prompt_text`,
`prompt_token_ids`, `repeat_count`, `generation_method`;
`generate_configs.py:812-950`). Construction follows the `_v3`/`_v5` idiom
(`PROMPT_SENTENCE` = "The plan remains easy to audit.", seven tokens under the
shared Qwen3 tokenizer; `_v3` hit 256 as 35 × 7 + one 11-token closing
sentence).

**Magistrate check that changes the design:** the `_v3` construction cannot
hit three of the four rungs. Under
`/Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit/tokenizer.json`
(`tokenizers` encode, no special tokens; verified at the bench 2026-09-01):

| rung L | L mod 7 | 7·r + 11 reachable? | closing-sentence length needed (≡ L mod 7) |
|---|---|---|---|
| 512 | 1 | no (501/7 not integral) | 8 or 15 tokens |
| 1024 | 2 | no | 9 or 16 tokens |
| 2048 | 4 | **yes, r = 291** (verified: 2048 tokens) | 11 (`PROMPT_FINAL_SENTENCE`) |
| 4096 | 1 | no | 8 or 15 tokens |

Ruling:

1. Each rung's text is `" ".join([PROMPT_SENTENCE] * r + [CLOSING_SENTENCE[L]])`
   with `r = (L − len_tokens(CLOSING_SENTENCE[L])) / 7`, integral.
2. `CLOSING_SENTENCE[2048]` = `PROMPT_FINAL_SENTENCE` (the `_v3` idiom). The
   other three closing sentences are fixed constants in the producer, in the
   same plain-English audit-register (no numerals, no code, no proper nouns),
   chosen so the count closes; their token lengths are asserted by
   re-tokenization at build time. The implementer proposes them; the refuters
   check them.
3. The producer re-tokenizes every rung's full text with the runtime's raw
   mode (`add_special_tokens=True`, `mlx_runtime.py:931-940`) and refuses
   unless the count equals L exactly. No `workload_profile.prompt_tokens`
   synthesis anywhere in the probe (Option C rejected: different workload).
4. The prompt ladder (`joulewise.g2a_prefill_prompt_ladder.v1`) records, per
   rung: text, text sha256, token ids, token-ids sha256, `repeat_count`,
   closing sentence, tokenizer sha256, and `generation_method` as a single
   string of the form
   `"<r> x '<PROMPT_SENTENCE>' + '<closing>' under tokenizer sha256:<…>"`.
   The eventual pin copies these fields verbatim for the selected rung.
5. The scout's "token-ID prefix relation" across rungs is NOT required
   (closing sentences differ per rung); exactness per rung is the invariant.

## R2 — "thinking disabled and greedy pinned": Option A

Raw `prompt_text` bypasses the chat template, so no thinking switch is
rendered; the admitted panel's thinking-off policy
(`configs/model_panels/qwen3_4bit.json:23-26,71-81`) is bound by hash into the
ladder and the input inventory, and greedy decoding is the MLX adapter's
fail-closed sampler (`mlx_runtime.py:975-1023`). No `BenchmarkConfig` schema
change. The runsheet wording "thinking disabled and greedy pinned in each
config" is corrected to "panel thinking-off policy and the MLX greedy runtime
are hash-bound in the G2-a input inventory".

## R3 — G2-a `record_id`: Option A

`selection_authority.g2a_record.record_id` = `"sha256:" + <sha256 of the
selection-record bytes>`; `path` = the selection record's path relative to the
window plan root. The selector's output schema
(`joulewise.g2a_prefill_selection.v1`) is not modified.

## R4 — probe workload shape and member counts (scout's "engineering default", ruled)

- Workload per member: identical to `_v5` `workload_for("prefill")`
  (`generate_configs.py:1404-1419`) — `repetitions: 1`, `warmup_runs: 1`,
  `output_tokens: 512`, `prompt_text` from the ladder — because the
  resolvability finding transfers to `_v5` only if the probe's phase window is
  shaped like `_v5`'s.
- Exactly five small members and one large member per rung (24 members); more
  is allowed by A4 but is not the default.
- `check` (read-only) runs before ledger readiness/reservation in the
  generated Phase-D bracket, and the bracket's later `select_g2a_prefill_length.py`
  and the new summarizer invocations run with `PYTHONPATH="$REPO"` (the bare
  call fails today).

## What this ruling does not decide

- The evening date (Ed; after `check` is green on Ed's machine).
- Anything about calibration custody: pre/post custody remains the live
  writer's (`validate_powermetrics_fiducial.py:1732-1816`), never a desk
  producer's — the scout's "Calibration custody: wait_for" row stands.
- The ordinary-manifest hash gap in `run_campaign.py:3020-3064` (F4) is closed
  for G2-a by the `check` gate, not by changing `run_campaign.py`.
