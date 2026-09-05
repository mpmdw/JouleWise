# D-117 CONTRAST `_v5` production-pack preparation

This document describes the preparation state of the D-117 CONTRAST `_v5`
campaign pack. A *campaign pack* is the closed set of plans, manifests, run
configurations, and provenance hashes that fixes a measurement before data are
collected. `_v5` is a new generation of the already-ruled D-139 A2 design: two
ABBA contrasts, ten blocks per contrast, four members per block, and 80 science
members in total. ABBA means the within-block execution order alternates model
A and model B as A1, B1, B2, A2.

## DRAFT AP Row

| Field | Value |
|---|---|
| Plan ID / RQ consumer | DRAFT-AP-D117-V5 / D-117 CONTRAST `_v5` D-165 dominance preparation. |
| family_id | FAM-D117-CONTRAST-V5-DOMINANCE |
| claim_role | exploratory |
| selection_scope | Two frozen Qwen3 model arms, decode and the G2-selected prefill arm, with ten predeclared ABBA blocks per contrast. |
| multiplicity_rule | Exploratory with no-confirmatory-inference until the final pack and analysis plan are frozen. |
| Metric + exact window class | Comparative and absolute gross-energy false-effect floors on the registered decode and prefill phase windows. |
| Unit of analysis + dependence structure | ABBA block deltas for comparative components and authenticated member energies for absolute components; members within one block are dependent. |
| Estimator/formula | D-165 independent-corner R and comparative common-mode R_cm registrations described below. |
| Inclusion/exclusion + quality-flag waiver rules | Only strict-valid authenticated campaign members; no new quality waiver is introduced by this preparation pack. |
| Order/blocking/covariates | Frozen ABBA order with ten blocks per contrast; model arm, block, and phase are fixed before collection. |
| Floor gate | pending-P2-015 until the final `_v5` floor cells and pack receipt are frozen. |
| MDE/n sizing + predeclared top-up rule | Ten frozen ABBA blocks per contrast under D-062; outcome-dependent top-up is forbidden, and any changed n permanently demotes the result to exploratory. |
| Denominator provenance requirement | Authenticated point and corner-widened floor records, model-panel pins, prompt pins, and retained common-mode replay inputs. |
| Holdout cells (L3 only) | Not applicable to this pre-mint preparation row; no L3 claim is registered here. |
| Claim ceiling + exact forbidden upgrade | L0 preparation only. Forbidden upgrade: no dominance sentence before the frozen analysis consumes every ruled gate. |
| Disqualifiers + not-resolvable conditions | Unresolved G2 prefill selection, missing pack receipt, model-byte pin mismatch, invalid replay authentication, zero denominator, or any component below its ruled gate. |
| Linked manifests/bundle hashes | Pending final generation and D-134 freeze; no collected bundles are linked by this preparation document. |

The production pair is `mlx-community/Qwen3-1.7B-4bit` at revision
`3b1b1768f8f8cf8351c712464f906e86c2b8269e` and
`mlx-community/Qwen3-8B-4bit` at revision
`545dc4251c05440727734bcd94334791f6ab0192`. Both panel entries bind the same
`tokenizer.json` SHA-256,
`aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4`.
The generator reads these identities and all rendering pins from
`configs/model_panels/qwen3_4bit.json`; it does not inspect a local model mirror
or load a tokenizer or model. Every emitted member carries both hashes. At the
existing MLX member-prepare boundary, before `mlx_lm.load`, the runtime hashes
the local mirror's literal `tokenizer.json` and the UTF-8 bytes of the
`chat_template` string in `tokenizer_config.json`; a missing or mismatched pin
refuses the member with a named reason. The measurement-machine preflight tool
`scripts/admit_model_panel_entry.py` separately applies the same panel-versus-
mirror checks as an operational belt.

Known limitation: a single operator's accidental mirror mutation between the
identity hash checks and `mlx_lm.load` remains a check-to-load TOCTOU risk.

## Decode workload

The *decode arm* measures energy while the model generates output. Its eight
real prompts come from `configs/workloads/real_prompts_v1.json`, where every
UTF-8 prompt text and the ordered prompt set are SHA-256-bound. The model panel
contains the corresponding generation-time rendering pinset. That pinset was
computed by applying the Qwen3 chat template to one user message with
`tokenize=true`, `add_generation_prompt=true`, and `enable_thinking=false`.
It records the exact token IDs, their domain-separated SHA-256 values, the
template SHA-256, and the tokenizer SHA-256. *Domain-separated* means the hash
includes a JouleWise type label as well as the token-ID bytes, preventing the
same bytes in another artifact class from being mistaken for this prompt pin.

At generation time, the generator matches the workload profile ID, ordered
prompt IDs, prompt-text hashes, prompt-set hash, tokenizer hash, template hash,
and thinking policy against that panel pinset. A template, tokenizer, prompt,
or ordering drift therefore causes a named refusal before pack bytes are
published. The decode policy is greedy generation with thinking off and an
exact forced budget of 512 output tokens.

## Prefill remains deliberately unresolved

The *prefill arm* measures processing of the input tokens before output
generation. A separate G2-a diagnostic sweep, meaning a pre-campaign probe that
cannot support a paper claim, runs at 512, 1024, 2048, and 4096 prompt tokens.
Each rung must contain at least five small-model probe members. A *member* is
one independently collected campaign run. Large-model probes are retained as
supporting observations but do not select the length.

The production reducer writes each member's
`overlapping_power_interval_count`, the number of power records that overlap
the prefill phase, into `summary_metrics.json`. The reducer's physical minimum,
`MIN_PHASE_SAMPLES`, is 3. The pre-registration adds a declared two-record
safety factor, so a rung clears only when every small-model member has a count
of at least 5. The selected prefill length is the first, and therefore shortest,
rung that clears. Counts are read from the reducer output and are not recomputed
for selection.

If no rung clears 5, the prefill arm is still collected at 4096 and the Holm
multiple-testing family remains fixed at two contrasts. The reported outcome
then separates two cases. A reducer count below 3 emits
`not_resolvable_sample_count`, and that reducer refusal is printed as itself. A
reducer count of 3 or 4 is physically resolvable but below the pre-registered
floor; the paper instead prints "below the pre-registered count floor of 5"
and discloses the reducer's resolvable result alongside it. It never prints a
reducer refusal code that the reducer did not emit.

The selection result does not yet exist. Consequently the command-line length
defaults to no value, and the generator refuses with
`prefill_length_unresolved`. Once G2-a selects the length, the generator also
requires an explicit `joulewise.prefill_prompt_pin.v2` artifact. Its closed
schema binds the ordered ladder, the five-member minimum, count floor 5,
reducer floor 3, the derived safety factor 2, the selection expression, the
split refusal rule, the selected G2-a record's SHA-256 hash, the ruling trace,
the selected length, prompt text, tokenizer hash, token IDs, token-ID hash, and
generation method. An absent G2-a record hash refuses just as an absent length
does; there is no 512-token fallback.

## Dominance criterion

The *dominance ratio* R asks whether admitted timing uncertainty could be large
enough to dominate the measured effect. For each registered claim-bearing
component in each cell, R is the corner-widened unguarded floor divided by the
point unguarded floor. *Unguarded floor* means the false-effect floor before the
separate guard multiplier is applied; *corner-widened* means every allowed
uncertainty interval corner is considered. The ruled gate is `R >= 2.0`, so
exact equality passes. Every registered component must pass. A mixture of pass
and fail results is reported component by component and uses null framing
instead of a dominance headline. A zero point-floor denominator is a named
refusal, never infinity or NaN.

The registration also defines R_cm under
`d165_shared_sign_local_corner_replay.v2`, a shared-energy-sign / local-corner
sensitivity diagnostic. One additive energy sign is shared across all ten ABBA
blocks, while bundle-local residual signs remain independently adversarial.
This has no proven conservatism for common-time motion; passage licenses no
physical timing-robustness claim. The replay reconstructs the shared and
local terms from the custodied onset sweep, offset sweep, zero-point contrast,
four residual half-widths, member-window bounds, operative shared-edge bound,
member envelope sum, and block delta before the mint path's final
shared-plus-local sum loses that split. It then enumerates both shared signs
and every local corner. The replay refuses unless the authenticated operative
bound is finite and positive, every zero point appears exactly in both sweeps,
and every zero point approximately agrees with its block delta under the
production tolerance. If `R_cm < 2.0`, the dominance sentence is withdrawn.

The component dispositions are explicit. Absolute independent-corner R is
reportable and participates in the R >= 2 gate. Absolute R_cm uses the registered
rationale (`ABSOLUTE_COMMON_MODE_REASON`): a uniform additive energy offset
cancels from absolute residuals; no absolute common-time replay is implemented;
absolute R_cm is not_applicable because the registered replay is comparative-only,
not because absolute timing uncertainty vanishes. Comparative R_cm is mandatory and retains the `< 2`
withdrawal. No absolute local-only diagnostic is registered for `_v5`; such a
quantity is deferred because it requires a distinct versioned name.

The contrast dictionaries carry this `dominance_criterion` beside the
canonical common-mode estimator registration. Producer floor plans and the
mint path continue to validate only the canonical common-mode registration;
the dominance sub-object is contrast analysis semantics and is included in the
analysis manifest's `frozen_semantics_sha256`.

## Work remaining before mint

The pack is not ready to mint or collect. The remaining sequence is:

1. Run the lead-controlled four-rung G2-a sweep and record the shortest rung
   that clears the pre-registered count floor.
2. Create and review the hash-bound prefill prompt pin for that ruled length.
3. Run estate 12, the full clone proof that the new pack follows the established
   mint path without changing frozen modules.
4. Generate the final bytes and mint the D-134 freeze receipt. A *freeze
   receipt* is the committed hash authority that makes the generated pack
   immutable and armable.

No `_v4` pack is collected. Until all four steps complete, any generated `_v5`
bytes are test-only drafts and not hardware-validation evidence.
