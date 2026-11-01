# BYTES extension: two current open-weights models as extra held-out tests (Ed, 2026-10-27)

**Authority.** Ed, Claude Code session 015ASG1T (laptop), 2026-10-27: "keep the registered roster, but add those models
you just discovered to the roster". Gate policy rule 5: one blind executing refuter (Sol 6.1 xhigh fast) before any
session of these models.

**Blind.** Written before any BYTES energy has been unblinded and before any data for these models exist.

**What does not change.** The registered BYTES analysis (`docs/registrations/bytes_pack_v1.md`) is untouched: its
ten-model roster, fit set, three rival lines, the 21-check H1 family, H2, the blinding, the stopping rule and every
printed registered quantity. Llama-3.3-70B stays as the top-of-range dense model (it sets the upper end of the
bytes-per-token range); the paper says it was chosen for that reason.

**What is added.** An *extension* group of held-out models, reported in its own labelled section and never mixed into
the registered results:

| Model | Kind | Why | Status |
|---|---|---|---|
| Qwen3.8-27B (MLX, 8-bit, the revision already downloaded; RUN_STATE item 66) | dense | the strongest open-weights model that fits the laptop (Artificial Analysis open-weights index, checked 2026-10-27); fills the bytes gap between Qwen3-32B 4-bit (18.6 GB) and Llama-70B (39.9 GB) | runs on the pinned mlx-lm 0.31.3 |
| NVIDIA Nemotron 3.5 Super 120B-A12B (MLX, about 4-bit) | mixture-of-experts, hybrid Mamba-Transformer | a current non-Qwen MoE that fits at about 4 bits; a second-family test of active versus resident bytes | **conditional**: added only if a pinned-mlx-lm-compatible MLX build exists and passes a 3-5 run resolvability check; otherwise dropped, recorded, no substitute |

**Rules.**
1. Each extension model gets one pass (one floor module, 50 runs, the registered workload of §3), in its own sub-pack,
   scheduled after the registered pass-1 sub-packs and the fit set, and before none of them. If time runs short before
   the registered end (no t0 after 2026-11-05T00:00:00-08:00), extension sessions are dropped first.
2. Bytes per token come from the model files, by the registered manifest script (§4). Recurrent or state-space layers
   are recorded as constant-size state, as for Qwen3-Next and Qwen3.5.
3. Their rows go to the withheld store like any held-out model (§11). They enter no export, and no extension result is
   computed, before the registered predictions file is committed and its hash recorded.
4. They are predicted by the **committed** registered lines, unchanged. For each: the word (bytes / resident / time /
   unresolved / neither) and ln(measured/predicted) per boundary, with their own Bonferroni family over the extension
   checks only (2 models x 3 explanations = 6 per boundary, or 3 if Nemotron is dropped). They are never added to the
   registered family.
5. They do not enter H2's registered fits. They may be printed beside H2 as labelled deviations from the tier line,
   like the other non-tier models.
6. The paper says the extension was added on 2026-10-27, after pass 1 began and before any energy was seen, because the
   registered roster predates these models.
