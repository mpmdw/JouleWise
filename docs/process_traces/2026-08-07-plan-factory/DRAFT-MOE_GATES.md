Reading additional input from stdin...
OpenAI Codex v0.146.1
--------
workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: high
reasoning summaries: none
session id: 019fddaa-d140-7f53-8a39-53333218435b
--------
user
EXECUTION-PLAN DRAFT — MoE STRETCH DESK GATES (read-only; no writes; final message = the plan). The stretch paper is the re-anchored MoE study (docs/strategy/2026-08-07-paper-portfolio/ADJUDICATION.md arc item 3; referee re-anchoring in reviews/rev-moe-routing-energy.md: Qwen3-30B-A3B-4bit vs matched-active dense Qwen3-4B-4bit already local; the impact synthesis SYNTHESIS-IMPACT-FIRST.md tail has the 7-gate kill schedule). Draft the executable desk-gate plan for gates 1-4 (all pre-night): (1) pair-ratification packet contents for Ed (artifact revisions, claim ceiling, estimand statement); (2) capability week protocol: acquisition commands (30B-A3B is NOT local — verify; 17GB download), hash/pin, memory headroom probe, 4h envelope timing probe; (3) observability week: where expert IDs/weights are interceptable in the installed mlx_lm qwen3_next/qwen3_5 source (cite lines), the instrumentation approach that does NOT fork the pinned runtime semantics (or states honestly that a fork is needed + stack-identity consequence), realized-k reconciliation + <=2%% overhead check protocol; (4) estimand week: teacher-forced vs free-running comparison design, routing-locality/divergence reports; (5) the sublinearity-thesis pre-registration sketch (bandwidth model, predictions); (6) desk-week estimate; open questions. Quality bar: executable.
codex
I’ll inspect the adjudication, referee review, impact synthesis, current queue/state, and the installed `mlx_lm` source. I’ll keep this strictly read-only and return only the executable plan.
exec
/bin/zsh -lc 'git status --short --branch && rg -n "ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next" RUN_STATE.md && rg -n "Current Queue|Do-Not-Do-Yet|MoE|stretch|paper" TASK_QUEUE.md && rg -n "Mission M0|M0" docs/agent_playbook.md && rg -n "arc item 3|MoE|Qwen3-30B|Qwen3-4B" docs/strategy/2026-08-07-paper-portfolio/ADJUDICATION.md reviews/rev-moe-routing-energy.md docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 exited 2 in 0ms:
## main...origin/main
2008:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
2043:## ACTIVE_STOP_CARD
2182:## Current Project Status
2743:## Known Workspace State
96:Current Queue region is the sole live work-selection view.
213:## Current Do-Not-Do-Yet List
304:| LITREAD-VERIFY-01 | P4 Polish | [AGENT] | Pre-submission verbatim re-verification of the two load-bearing related-work sources against the **PDFs of record**: TokenPowerBench (arXiv **2512.03024**) and "The Illusion of Power Capping in LLM Decode" (arXiv **2605.11999**). Both were read in full text during the sweep, but through WebFetch's extraction model against the arXiv HTML renders. | Every quote and number cited in a submission re-checked against the PDF. **Note the id correction:** TokenPowerBench is 2512.03024; 2605.11999 is the Illusion paper — earlier handoff text conflated the two. | [Sweep-techniques access summary](docs/run_reports/2026-07-30-sweep-techniques.md) |
306:## Current Queue
343:| A6 | AXI-SD | P2 Next Slice | READY [AGENT] | Prepare the matched dense/MoE pair proposal with the consult's pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT. | A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016's cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: [AXI handoff work program S-D](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SD acceptance](docs/process/state_kernel.json). Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership). |
344:| A7 | AXI-SE | P2 Next Slice | READY [AGENT] | Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult's floor and ownership closures. | The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A's gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: [AXI handoff work program S-E](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SE acceptance](docs/process/state_kernel.json). Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership). |
379:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
421:| A6 | AXI-SD | P2 Next Slice | READY | Prepare the matched dense/MoE pair proposal with the consult's pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT. | A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016's cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: [AXI handoff work program S-D](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SD acceptance](docs/process/state_kernel.json). Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership). |
422:| A7 | AXI-SE | P2 Next Slice | READY | Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult's floor and ownership closures. | The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A's gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: [AXI handoff work program S-E](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SE acceptance](docs/process/state_kernel.json). Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership). |
457:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
26:1. Run Mission M0 (preflight) — always.
50:## Mission M0: Preflight (every session)
472:The M0 step-6 handoff list, plus: if you changed an adapter or bundle
rg: reviews/rev-moe-routing-energy.md: No such file or directory (os error 2)
docs/strategy/2026-08-07-paper-portfolio/ADJUDICATION.md:25:3. **Stretch — MoE re-anchored** (the impact-first pick): Qwen3-30B-A3B
docs/strategy/2026-08-07-paper-portfolio/ADJUDICATION.md:26:   vs its matched-active dense partner Qwen3-4B (already local) — the
docs/strategy/2026-08-07-paper-portfolio/ADJUDICATION.md:98:| Stretch MoE | 2-3 | desk gates first; Spring-class |
docs/strategy/2026-08-07-paper-portfolio/ADJUDICATION.md:114:   conversion smoke; MoE reserves the stretch slot.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:37:and moe-routing (as re-anchored Qwen3-30B-A3B vs dense partner) were the only VIABLEs;
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:327:docs/decision_log.md:3857:## D-074: Conditional Qwen3-4B primary repin + OLMo-1B conversion spike authorized
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:602:  speculative decoding, multi-token prediction (MTP), mixture-of-experts (MoE)
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:1450:| A6 | AXI-SD | P2 Next Slice | READY [AGENT] | Prepare the matched dense/MoE pair proposal with the consult's pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT. | A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016's cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: [AXI handoff work program S-D](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SD acceptance](docs/process/state_kernel.json). Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership). |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:1451:| A7 | AXI-SE | P2 Next Slice | READY [AGENT] | Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult's floor and ownership closures. | The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A's gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: [AXI handoff work program S-E](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SE acceptance](docs/process/state_kernel.json). Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership). |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:1528:| A6 | AXI-SD | P2 Next Slice | READY | Prepare the matched dense/MoE pair proposal with the consult's pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT. | A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016's cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: [AXI handoff work program S-D](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SD acceptance](docs/process/state_kernel.json). Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership). |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:1529:| A7 | AXI-SE | P2 Next Slice | READY | Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult's floor and ownership closures. | The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A's gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: [AXI handoff work program S-E](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SE acceptance](docs/process/state_kernel.json). Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership). |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:2641:  five: `Qwen2.5-0.5B/1.5B/7B-Instruct-4bit`, `Qwen3-4B-4bit`,
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:2753:  named (MoE + MLA + tokenizer + training all move together in Kimi Linear), is
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:2825:| Original goals | **5/10** | Real infrastructure dividend for spec-decode and MoE-by-batch — D-070 cl.3 designed the request-scoped schema for exactly this. But it touches no mechanism, and it consumes the nights the mechanism study needs. |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:3544:speculative decoding, MTP, MoE routing, KV/attention, split inference — and the
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:3641:| Original goals | **5/10** | Real infrastructure dividend for spec-decode and MoE-by-batch — D-070 cl.3 designed the request-scoped schema for exactly this. But it touches no mechanism, and it consumes the nights the mechanism study needs. |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:4295:It does not advance spec decode, MTP, MoE, KV/attention, or split inference by one step.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5393:already probed. Getting this wrong is not cosmetic: 27B-dense and 122B-A10B-MoE differ in every
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5409:a 4-bit MTP head with 40% acceptance produces a different paper; (ii) that a **65 GiB MoE** is a new
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5412:swings**, and the ~5 J practical bar descends from it. Move to a 122B MoE whose decode is dominated by
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5532:   and the ~5 J bar derive from ~33 W swings on the current stack; a 65 GiB MoE requires them re-derived
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5567:   re-characterization of the attribution bound and the sizing bar at the 65 GiB MoE power envelope
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5603:The charge asked whether a Qwen MoE variant exists on MLX at a servable size with per-token
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5616:`decoder_sparse_step=1`. So all 48 layers are MoE, giving 48 × 8 = **384** routed
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5718:That gap is the real story: **batch-1 MoE on unified memory achieves ~40 % of the bandwidth
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5732:The proposal correctly rejects cross-model MoE comparisons as confounded and correctly picks
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5771:kernel fusion around the MoE block, and any host readback forces a graph sync **48 × 1024
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5798:  attention, 12 are full attention. The paper would place a hybrid-linear-attention MoE
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5801:  151936/152064. Within the two MoE arms this is fine (same tokenizer, so the mJ/output-token
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5802:  companion is well-scoped). But the paper juxtaposes MoE results with D-117's Qwen2.5
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5822:costed. Its pairs table lists **"MoE top-k knob | Qwen3-30B-A3B, `num_experts_per_tok=8` |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5824:single-mechanism, same-weights knob"**, and its claims ranking puts "MoE top-k slope (same
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5826:top-3 recommended first campaigns are spec decode, the quant ladder, and **MoE-vs-dense
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5832:MoE paper) already reports that **"routing itself is <9 % of MoE-block compute — the penalty
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5841:Governance, unmentioned: there is **no registry row for MoE routing energy**. The nearest is
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5842:`C5-1.9` ("MoE-vs-dense controlled ladder", `status: banked`, L2 after envelope and
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5846:and requires AP-MOE-BATCH / the AP-5 MoE rider to be finalized *against P2-015 floors* — both
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5865:1. **Swap the artifact to `Qwen3-30B-A3B-4bit` (~17 GB) and drop the 122B.** The repo's own
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5866:   sweep already verified this checkpoint exists and named it the MoE arm; it is a pure text
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5867:   MoE with no vision tower to load-and-discard, no 65 GB residency squeezing the page cache
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5870:   makes the **matched-active dense comparison possible in the same paper** — `Qwen3-4B-4bit`
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5890:   measured: **batch-1 MoE decode on unified memory realises only ~40 % of the bandwidth
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5904:serves Ed's highest-priority original axis (MoE mechanism) better than anything else in this
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5911:chosen artifact is a 65 GB vision-language hybrid reasoning checkpoint when a 17 GB text MoE
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:6506:   characterization, quantization, MoE, MTP, and split") **without ever arguing against
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:6905:   and 3 admit they serve no mechanism. Nothing here advances spec-decode, MoE, MTP, or
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:7243:   toward spec-decode, MoE, MTP, KDA, or split inference.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:7822:MTP, MoE, KV variants, or split. Its claim that long workloads are "foundational"
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:8141:  decoding, MTP, MoE routing, KV/attention variants, split inference, modular
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:8145:  advance MTP/MoE/KV/split and right that it exercises the modular harness — it
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:8745:It costs a different target model (Qwen3-4B), a D-016 touch, a non-mirrored
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:8777:| original_goals | **9** | This *is* the split axis, honestly scoped, honestly silent on spec-decode/MTP/MoE/KDA. Real credit here. |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:8925:| Qwen2.5, Qwen3, OLMo tokenizer artifacts "already present locally" | **TRUE.** `~/jw_models/` holds Qwen2.5-{0.5,1.5,7}B, Qwen3-4B, Qwen3.5-122B, OLMo-1B-0724-hf, OLMoE-1B-7B-0924 |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:8993:lang    chars  bytes  Qwen2.5  Qwen3   OLMo  OLMoE   OLMo/Q2.5  Q3/Q2.5
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9006:Vocab: Qwen2.5 151665, Qwen3 151669 (four added specials), OLMo/OLMoE 50280.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9008:**Qwen3/Qwen2.5 = 1.00 on every language, every script.** Same merges. And OLMo-1B ≡ OLMoE-1B-7B
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9119:mechanism work. Serves **zero** mechanism axes — no spec decode, no MTP, no MoE routing, no
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9131:Add a fourth window: matched-content decode contrast, **Qwen2.5-1.5B vs OLMo-1B / OLMoE-1B-7B**, on
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9138:Feasibility is not speculative: OLMoE-1B-7B has already run on this harness
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9140:the exploratory OLMoE-vs-Qwen3-4B gross gap was **133.720 J — 5.43× the guard then, ~27× the 5 J
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9143:The confound is real and must be owned in the title, not buried: OLMoE is BF16, Qwen is INT4;
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9155:OLMo-1B ≡ OLMoE. Either add genuinely distinct locally-obtainable tokenizers (Llama-3 128k,
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9356:The proposal concedes it studies no mechanism axis — no spec decode, MTP, MoE, KDA, KV.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9417:| 3 | MoE vs dense matched-active | +30–100% of ~0.1–0.15 J/tok dense | ×2048 ≈ **60–300 J** | **~5–20×** |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9420:| 6 | MoE top-k slope (same weights) | expert-FFN energy ~∝ k; maybe 20–40% of J/tok | ×2048 ≈ 100–250 J | ~10× (**mechanism knob unverified**) |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9429:3. **MoE**: whether the +54% matched-active GPU penalty survives unified memory, phase-resolved — direct extension of 2606.21428 (M2 Pro, one pair, coarse) with the sign-flip (matched-active vs matched-total) pinned down on one instrument.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9437:3. **MoE vs dense matched-active (Qwen3-30B-A3B vs Qwen3-4B, plus the OLMoE/OLMo-2 lit-replication pair)** — settles the matched-active vs matched-total sign flip on unified memory and directly extends the only existing Apple-silicon result.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9450:   speculative decoding / MTP, MoE vs dense, quantization, and
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9488:   C5-1.1 / C5-1.9 / RQ-TWO-MODEL-ACTIVE-NONCLAIM (MoE/dense), C5-1.12
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9493:   upgrade: no MoE-serving-efficiency generalization from one pair).
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9501:with narrow claim commitments (the handoff default: MoE/dense +
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9505:Open item: the D-016 matched dense/MoE model pair remains with Ed and
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9575:This directly serves the original **quantization** and energy-honest quality-plus-latency-plus-energy axes. It also demonstrates the modular harness’s intended model/technique/workload swapping. It does not advance MTP, MoE routing, KV variants, or split inference, but supplies the disciplined comparison template those mechanisms will need.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9635:This directly serves the original **quantization** and energy-honest quality-plus-latency-plus-energy axes. It also demonstrates the modular harness’s intended model/technique/workload swapping. It does not advance MTP, MoE routing, KV variants, or split inference, but supplies the disciplined comparison template those mechanisms will need.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9638:  [OLMoE config](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r1/config.json).
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9641:  Universal families include clock/cadence/short-window flags; OLMoE r2 and
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9642:  Qwen3.5 r2 also hit a cooldown cap, and OLMoE r3 carries additional
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9675:that static batching, speculation/MTP, MoE-vs-dense, quantization, or reasoning
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9699:above OLMoE's 50,304-token vocabulary. Reusing it verbatim would pass config
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9700:schema validation but fail during OLMoE execution. Therefore the existing
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9706:Schema 0.1 has no supported chat-template or thinking-mode field. Qwen3-4B
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9712:- OLMoE uses upstream revision
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9717:- Qwen3-4B uses the local D-074 candidate mirror at revision
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9731:| OLMoE-1B-7B | 3.5–4.5 min | No harness throughput receipt yet; allows roughly 80–160 tok/s plus BF16 load/prefill overhead. |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9732:| Qwen3-4B | 3.3–4.2 min | Anchored to the dated 113 tok/s local greedy feasibility observation, with suite prefill/load margin. |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9747:The direction is viable only after a deliberate shrink: not a cross-model “MoE is efficient” comparison, and not a correlation on native runs where top‑k is constant. The defensible paper is a same-checkpoint routing-budget intervention—native top‑8 versus prospectively forced top‑4—with complete dispatch logs, a quality/divergence gate, and its own stack-specific floor. Two extra quiet windows should be enough if the desk gate passes.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9750:  ✓ Extract MoE-specific feasibility, instrument limits, and quantitative sizing evidence
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9753:# What Does a Routed Expert Cost? Floor-Gated MoE Routing Energy on an M3 Max
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9755:**Thesis:** JouleWise can identify the energy cost of changing MoE routing only through a same-checkpoint, directly observed routing-budget intervention; native cross-model comparisons are too confounded, and native top-*k* counts do not vary.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9759:This paper retains the completed MVP’s scientific spine: `powermetrics` is treated as a calibrated, stack-specific instrument; phase edges are live-bracketed; detection floors combine repeatability, worst-case timing attribution, and never-zero drift; and claims must separately clear the floor and an interval-supported direction gate. The central result remains that the instrument is attribution-limited—roughly 1 J can move across a phase boundary—and practical phase contrasts should be sized around the approximately 5 J effective bar. First complete D-117 exactly as frozen: the 1.5B decode-floor window with prefill rider (~3.14 h), the 7B equivalent (~3.24 h), and the 1.5B-versus-7B decode contrast (~2.80 h). Mint the four phase-floor cells, govern the contrast against the two decode floors, and populate the MVP tables. Those three windows contribute the paper’s metrology evidence and Qwen2.5 demonstration; their floors cannot be borrowed for MoE.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9761:Then run a desk-only MoE feasibility gate. Instrument the already exercised, pinned `Qwen3.5-122B-A10B-4bit` MLX artifact to preserve the router’s actual expert IDs and weights without changing tokens. Freeze one intervention: native routed top-*k*=8 versus forced *k*=4 in the same checkpoint. The official architecture specifies 48 layers, 256 experts, eight routed experts plus one shared expert; current MLX code calculates those indices internally but does not expose them as evidence. [Qwen model card](https://huggingface.co/Qwen/Qwen3.5-122B-A10B), [MLX implementation](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/models/qwen3_next.py). If the desk gate passes, fund two additional quiet windows: one exact-stack floor window and one science contrast window. Thus the complete paper costs five nights, approximately 14–16 quiet-machine hours total; the MoE increment is approximately 5–7 hours, both estimates uncertain until dry-run timing.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9767:2. **Auditable MoE routing evidence.** Every measured layer-token must reconcile to exactly eight or four routed expert IDs plus the shared expert. Any missing or inconsistent trace removes the mechanism claim.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9771:4. **Energy–quality separation.** A frozen quality screen and exact-output divergence report determine whether the result is “quality-equivalent,” an explicit quality/energy trade-off, or unusable—not a generic MoE-efficiency claim.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9789:This is a strong capstone paper and a plausible EuroMLSys or ICPE Emerging submission. It becomes an ICPE full-track candidate only if routing observability, the quality gate, both MoE windows, and an artifact-ready replay all land. It reuses the MVP introduction and Sections 3–5 nearly intact, plus every D-117 result. New material is one routing-instrument subsection, one mechanism experiment, and its refusal/quality analysis.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9793:Kill the MoE nights before collection if:
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9803:This directly serves the original MoE mechanism axis and advances the modular-harness goal by making routing policy, realized expert activity, workload, and model artifact independently swappable. It does not yet support an energy-honest public leaderboard or a general claim that MoE is more efficient than dense inference.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9806:# What Does a Routed Expert Cost? Floor-Gated MoE Routing Energy on an M3 Max
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9808:**Thesis:** JouleWise can identify the energy cost of changing MoE routing only through a same-checkpoint, directly observed routing-budget intervention; native cross-model comparisons are too confounded, and native top-*k* counts do not vary.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9812:This paper retains the completed MVP’s scientific spine: `powermetrics` is treated as a calibrated, stack-specific instrument; phase edges are live-bracketed; detection floors combine repeatability, worst-case timing attribution, and never-zero drift; and claims must separately clear the floor and an interval-supported direction gate. The central result remains that the instrument is attribution-limited—roughly 1 J can move across a phase boundary—and practical phase contrasts should be sized around the approximately 5 J effective bar. First complete D-117 exactly as frozen: the 1.5B decode-floor window with prefill rider (~3.14 h), the 7B equivalent (~3.24 h), and the 1.5B-versus-7B decode contrast (~2.80 h). Mint the four phase-floor cells, govern the contrast against the two decode floors, and populate the MVP tables. Those three windows contribute the paper’s metrology evidence and Qwen2.5 demonstration; their floors cannot be borrowed for MoE.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9814:Then run a desk-only MoE feasibility gate. Instrument the already exercised, pinned `Qwen3.5-122B-A10B-4bit` MLX artifact to preserve the router’s actual expert IDs and weights without changing tokens. Freeze one intervention: native routed top-*k*=8 versus forced *k*=4 in the same checkpoint. The official architecture specifies 48 layers, 256 experts, eight routed experts plus one shared expert; current MLX code calculates those indices internally but does not expose them as evidence. [Qwen model card](https://huggingface.co/Qwen/Qwen3.5-122B-A10B), [MLX implementation](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/models/qwen3_next.py). If the desk gate passes, fund two additional quiet windows: one exact-stack floor window and one science contrast window. Thus the complete paper costs five nights, approximately 14–16 quiet-machine hours total; the MoE increment is approximately 5–7 hours, both estimates uncertain until dry-run timing.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9820:2. **Auditable MoE routing evidence.** Every measured layer-token must reconcile to exactly eight or four routed expert IDs plus the shared expert. Any missing or inconsistent trace removes the mechanism claim.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9824:4. **Energy–quality separation.** A frozen quality screen and exact-output divergence report determine whether the result is “quality-equivalent,” an explicit quality/energy trade-off, or unusable—not a generic MoE-efficiency claim.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9842:This is a strong capstone paper and a plausible EuroMLSys or ICPE Emerging submission. It becomes an ICPE full-track candidate only if routing observability, the quality gate, both MoE windows, and an artifact-ready replay all land. It reuses the MVP introduction and Sections 3–5 nearly intact, plus every D-117 result. New material is one routing-instrument subsection, one mechanism experiment, and its refusal/quality analysis.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9846:Kill the MoE nights before collection if:
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9856:This directly serves the original MoE mechanism axis and advances the modular-harness goal by making routing policy, realized expert activity, workload, and model artifact independently swappable. It does not yet support an energy-honest public leaderboard or a general claim that MoE is more efficient than dense inference.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10030:This direction directly serves the “energy as a third axis beside quality and latency” goal and the energy-honest leaderboard critique: it supplies the error model and refusal semantics every later comparison needs. Q4 also advances the modular harness by making workload and model axes swappable under one calibrated protocol. It does **not** yet deliver speculative decoding, MTP, MoE routing, KV mechanisms, or split inference. Those remain follow-on studies; forcing one into this paper would weaken its coherent instrument-first contribution.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10077:This direction directly serves the “energy as a third axis beside quality and latency” goal and the energy-honest leaderboard critique: it supplies the error model and refusal semantics every later comparison needs. Q4 also advances the modular harness by making workload and model axes swappable under one calibrated protocol. It does **not** yet deliver speculative decoding, MTP, MoE routing, KV mechanisms, or split inference. Those remain follow-on studies; forcing one into this paper would weaken its coherent instrument-first contribution.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10211:The historical 7B floor member averaged about 192 J for its 512-token decode workload; halving length suggests roughly **96 J at 256 tokens**, but this is an uncertain, non-claim extrapolation. The 5 J bar is therefore about 5% of expected request energy. Public results show why a wide prior is necessary: current `mlx-dspark` reports roughly 1.7–2.3× Qwen3 speedups on an M4 Pro, whereas JouleWise’s older Qwen3-4B smoke achieved only 0.36–0.41× greedy throughput. A separate energy study also found cases where speculative decoding used more energy despite lower latency. [MLX-DSpark results](https://github.com/ARahim3/mlx-dspark), [energy study](https://arxiv.org/abs/2602.09113).
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10269:The historical 7B floor member averaged about 192 J for its 512-token decode workload; halving length suggests roughly **96 J at 256 tokens**, but this is an uncertain, non-claim extrapolation. The 5 J bar is therefore about 5% of expected request energy. Public results show why a wide prior is necessary: current `mlx-dspark` reports roughly 1.7–2.3× Qwen3 speedups on an M4 Pro, whereas JouleWise’s older Qwen3-4B smoke achieved only 0.36–0.41× greedy throughput. A separate energy study also found cases where speculative decoding used more energy despite lower latency. [MLX-DSpark results](https://github.com/ARahim3/mlx-dspark), [energy study](https://arxiv.org/abs/2602.09113).
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10325:above OLMoE's 50,304-token vocabulary. Reusing it verbatim would pass config
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10326:schema validation but fail during OLMoE execution. Therefore the existing
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10332:Schema 0.1 has no supported chat-template or thinking-mode field. Qwen3-4B
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10338:- OLMoE uses upstream revision
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10343:- Qwen3-4B uses the local D-074 candidate mirror at revision
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10357:| OLMoE-1B-7B | 3.5–4.5 min | No harness throughput receipt yet; allows roughly 80–160 tok/s plus BF16 load/prefill overhead. |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10358:| Qwen3-4B | 3.3–4.2 min | Anchored to the dated 113 tok/s local greedy feasibility observation, with suite prefill/load margin. |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10373:The direction is viable only after a deliberate shrink: not a cross-model “MoE is efficient” comparison, and not a correlation on native runs where top‑k is constant. The defensible paper is a same-checkpoint routing-budget intervention—native top‑8 versus prospectively forced top‑4—with complete dispatch logs, a quality/divergence gate, and its own stack-specific floor. Two extra quiet windows should be enough if the desk gate passes.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10376:  ✓ Extract MoE-specific feasibility, instrument limits, and quantitative sizing evidence
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10379:# What Does a Routed Expert Cost? Floor-Gated MoE Routing Energy on an M3 Max
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10381:**Thesis:** JouleWise can identify the energy cost of changing MoE routing only through a same-checkpoint, directly observed routing-budget intervention; native cross-model comparisons are too confounded, and native top-*k* counts do not vary.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10385:This paper retains the completed MVP’s scientific spine: `powermetrics` is treated as a calibrated, stack-specific instrument; phase edges are live-bracketed; detection floors combine repeatability, worst-case timing attribution, and never-zero drift; and claims must separately clear the floor and an interval-supported direction gate. The central result remains that the instrument is attribution-limited—roughly 1 J can move across a phase boundary—and practical phase contrasts should be sized around the approximately 5 J effective bar. First complete D-117 exactly as frozen: the 1.5B decode-floor window with prefill rider (~3.14 h), the 7B equivalent (~3.24 h), and the 1.5B-versus-7B decode contrast (~2.80 h). Mint the four phase-floor cells, govern the contrast against the two decode floors, and populate the MVP tables. Those three windows contribute the paper’s metrology evidence and Qwen2.5 demonstration; their floors cannot be borrowed for MoE.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10387:Then run a desk-only MoE feasibility gate. Instrument the already exercised, pinned `Qwen3.5-122B-A10B-4bit` MLX artifact to preserve the router’s actual expert IDs and weights without changing tokens. Freeze one intervention: native routed top-*k*=8 versus forced *k*=4 in the same checkpoint. The official architecture specifies 48 layers, 256 experts, eight routed experts plus one shared expert; current MLX code calculates those indices internally but does not expose them as evidence. [Qwen model card](https://huggingface.co/Qwen/Qwen3.5-122B-A10B), [MLX implementation](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/models/qwen3_next.py). If the desk gate passes, fund two additional quiet windows: one exact-stack floor window and one science contrast window. Thus the complete paper costs five nights, approximately 14–16 quiet-machine hours total; the MoE increment is approximately 5–7 hours, both estimates uncertain until dry-run timing.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10393:2. **Auditable MoE routing evidence.** Every measured layer-token must reconcile to exactly eight or four routed expert IDs plus the shared expert. Any missing or inconsistent trace removes the mechanism claim.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10397:4. **Energy–quality separation.** A frozen quality screen and exact-output divergence report determine whether the result is “quality-equivalent,” an explicit quality/energy trade-off, or unusable—not a generic MoE-efficiency claim.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10415:This is a strong capstone paper and a plausible EuroMLSys or ICPE Emerging submission. It becomes an ICPE full-track candidate only if routing observability, the quality gate, both MoE windows, and an artifact-ready replay all land. It reuses the MVP introduction and Sections 3–5 nearly intact, plus every D-117 result. New material is one routing-instrument subsection, one mechanism experiment, and its refusal/quality analysis.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10419:Kill the MoE nights before collection if:
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10429:This directly serves the original MoE mechanism axis and advances the modular-harness goal by making routing policy, realized expert activity, workload, and model artifact independently swappable. It does not yet support an energy-honest public leaderboard or a general claim that MoE is more efficient than dense inference.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10432:# What Does a Routed Expert Cost? Floor-Gated MoE Routing Energy on an M3 Max
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10434:**Thesis:** JouleWise can identify the energy cost of changing MoE routing only through a same-checkpoint, directly observed routing-budget intervention; native cross-model comparisons are too confounded, and native top-*k* counts do not vary.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10438:This paper retains the completed MVP’s scientific spine: `powermetrics` is treated as a calibrated, stack-specific instrument; phase edges are live-bracketed; detection floors combine repeatability, worst-case timing attribution, and never-zero drift; and claims must separately clear the floor and an interval-supported direction gate. The central result remains that the instrument is attribution-limited—roughly 1 J can move across a phase boundary—and practical phase contrasts should be sized around the approximately 5 J effective bar. First complete D-117 exactly as frozen: the 1.5B decode-floor window with prefill rider (~3.14 h), the 7B equivalent (~3.24 h), and the 1.5B-versus-7B decode contrast (~2.80 h). Mint the four phase-floor cells, govern the contrast against the two decode floors, and populate the MVP tables. Those three windows contribute the paper’s metrology evidence and Qwen2.5 demonstration; their floors cannot be borrowed for MoE.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10440:Then run a desk-only MoE feasibility gate. Instrument the already exercised, pinned `Qwen3.5-122B-A10B-4bit` MLX artifact to preserve the router’s actual expert IDs and weights without changing tokens. Freeze one intervention: native routed top-*k*=8 versus forced *k*=4 in the same checkpoint. The official architecture specifies 48 layers, 256 experts, eight routed experts plus one shared expert; current MLX code calculates those indices internally but does not expose them as evidence. [Qwen model card](https://huggingface.co/Qwen/Qwen3.5-122B-A10B), [MLX implementation](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/models/qwen3_next.py). If the desk gate passes, fund two additional quiet windows: one exact-stack floor window and one science contrast window. Thus the complete paper costs five nights, approximately 14–16 quiet-machine hours total; the MoE increment is approximately 5–7 hours, both estimates uncertain until dry-run timing.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10446:2. **Auditable MoE routing evidence.** Every measured layer-token must reconcile to exactly eight or four routed expert IDs plus the shared expert. Any missing or inconsistent trace removes the mechanism claim.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10450:4. **Energy–quality separation.** A frozen quality screen and exact-output divergence report determine whether the result is “quality-equivalent,” an explicit quality/energy trade-off, or unusable—not a generic MoE-efficiency claim.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10468:This is a strong capstone paper and a plausible EuroMLSys or ICPE Emerging submission. It becomes an ICPE full-track candidate only if routing observability, the quality gate, both MoE windows, and an artifact-ready replay all land. It reuses the MVP introduction and Sections 3–5 nearly intact, plus every D-117 result. New material is one routing-instrument subsection, one mechanism experiment, and its refusal/quality analysis.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10472:Kill the MoE nights before collection if:
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10482:This directly serves the original MoE mechanism axis and advances the modular-harness goal by making routing policy, realized expert activity, workload, and model artifact independently swappable. It does not yet support an energy-honest public leaderboard or a general claim that MoE is more efficient than dense inference.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10584:This serves the modular-instrument and energy-honest reporting goals directly: every future speculative-decoding, MTP, MoE, KV, or split result would inherit a backend-specific resolvability gate. It does not itself deliver a mechanism-level LLM result; it supplies the measurement foundation that prevents those later studies and leaderboards from reporting distinctions their counters cannot support.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10637:This serves the modular-instrument and energy-honest reporting goals directly: every future speculative-decoding, MTP, MoE, KV, or split result would inherit a backend-specific resolvability gate. It does not itself deliver a mechanism-level LLM result; it supplies the measurement foundation that prevents those later studies and leaderboards from reporting distinctions their counters cannot support.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10740:This direction directly serves the “energy as a third axis beside quality and latency” goal and the energy-honest leaderboard critique: it supplies the error model and refusal semantics every later comparison needs. Q4 also advances the modular harness by making workload and model axes swappable under one calibrated protocol. It does **not** yet deliver speculative decoding, MTP, MoE routing, KV mechanisms, or split inference. Those remain follow-on studies; forcing one into this paper would weaken its coherent instrument-first contribution.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10787:This direction directly serves the “energy as a third axis beside quality and latency” goal and the energy-honest leaderboard critique: it supplies the error model and refusal semantics every later comparison needs. Q4 also advances the modular harness by making workload and model axes swappable under one calibrated protocol. It does **not** yet deliver speculative decoding, MTP, MoE routing, KV mechanisms, or split inference. Those remain follow-on studies; forcing one into this paper would weaken its coherent instrument-first contribution.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10922:The ranking is converging on a staged decision rather than eight competing full papers: finish the four-night metrology capstone, run the urgent zero-night evidence/plumbing work before alpha, then make a mechanism paper conditional on hard desk gates. The key close call is MoE versus quantization; I’m pricing both at their real floor obligations rather than accepting the reviews’ optimistic “two-night” shorthand.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10932:Fund a four-night MVP, make the re-anchored MoE study the conditional second paper, keep the three-rung quantization ladder as the automatic fallback, and treat speculative decoding as the high-risk stretch. Do not fund the other proposals as standalone papers.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10948:### 2. Re-anchored MoE routing: Qwen3-30B-A3B, dense partner, and a causal routing-budget leg
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10950:This is the **best second-paper bet** under the impact-first prior. The viable version abandons the awkward 65 GB Qwen3.5 VLM hybrid and uses the repo-vetted Qwen3-30B-A3B text MoE with Qwen3-4B as the matched-active dense partner, plus a within-checkpoint top-*k* intervention to distinguish routing-budget effects from cross-model confounding. It directly serves Ed’s original MoE goal and has the best chance of becoming a real mechanism paper rather than another metrology application. Honest cost is **six to seven nights from today**: four MVP nights, at least one independently scoped MoE/dense floor night, one science night, and a third extension night if dense, native-*k*, and forced-*k* floors cannot be packed without weakening the frozen replication standard. Desk cost is approximately **4–6 weeks**. Survival prior: **35–50%**. I agree with the VIABLE verdict but disagree that “two nights” is guaranteed once the dense partner is added.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10962:The original context-curve proposal is confounded and under-floored, but the rebuilt version is credible: start with one 1.5B 128-vs-long-context ABBA contrast, lengthen decode to amplify KV traffic, replace dead interior points with long-condition A=A nulls, and include or separately bound prefill-to-decode thermal carryover. Every length must self-floor; no 7B study may use the generic 5 J bar. Cost is **five to six nights from today**—four MVP plus one self-flooring claim window, with a second only if the thermal-matched control cannot fit—and **2–4 desk weeks**. Survival prior: **45–60%**. It has a lower venue ceiling than MoE but directly serves the KV/attention goal and stays within the frozen single-request boundary.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11020:## Winter 2026/27–Spring 2027: MoE second paper
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11022:After the MVP’s tables and artifact are locked, spend 4–6 weeks on the MoE gates. If all pass, collect one floor night and one mechanism night; add a third only if that need is determined prospectively by the frozen floor design. Target EuroMLSys or ICPE Emerging first; upgrade venue ambition only if the dense comparison, routing intervention, and replay artifact all land.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11024:If MoE fails a desk gate, switch immediately to BF16/Q4/Q8 quantization. Do not attempt to “repair” the MoE paper with a cross-model descriptive table.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11047:| A4 static-batch adapter | Infrastructure only | Cheap queued desk work; later supports batch/spec/MoE work |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11054:- MoE and quantization share multi-cell mint, multi-arm analysis, artifact hashing, and divergence-report machinery—but **not floors**.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11059:# Single best second-paper bet: MoE
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11061:Choose the re-anchored MoE paper because it has the highest publishable upside if its kill gates clear: it answers an original mechanism question, offers a causal within-checkpoint leg, and can explain why batch-1 unified-memory MoE behaves differently from active-parameter intuition and server-GPU results.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11067:1. **Pair ruling, before engineering:** Ed/advisor ratify Qwen3-30B-A3B and Qwen3-4B, exact artifact revisions, and the claim ceiling.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11080:4. **Second-paper commitment:** Will Ed reserve two to three Spring 2027 nights for the re-anchored MoE study if every desk gate passes? If not, select BF16/Q4/Q8 now as the lower-risk fallback.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11091:Fund a four-night MVP, make the re-anchored MoE study the conditional second paper, keep the three-rung quantization ladder as the automatic fallback, and treat speculative decoding as the high-risk stretch. Do not fund the other proposals as standalone papers.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11107:### 2. Re-anchored MoE routing: Qwen3-30B-A3B, dense partner, and a causal routing-budget leg
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11109:This is the **best second-paper bet** under the impact-first prior. The viable version abandons the awkward 65 GB Qwen3.5 VLM hybrid and uses the repo-vetted Qwen3-30B-A3B text MoE with Qwen3-4B as the matched-active dense partner, plus a within-checkpoint top-*k* intervention to distinguish routing-budget effects from cross-model confounding. It directly serves Ed’s original MoE goal and has the best chance of becoming a real mechanism paper rather than another metrology application. Honest cost is **six to seven nights from today**: four MVP nights, at least one independently scoped MoE/dense floor night, one science night, and a third extension night if dense, native-*k*, and forced-*k* floors cannot be packed without weakening the frozen replication standard. Desk cost is approximately **4–6 weeks**. Survival prior: **35–50%**. I agree with the VIABLE verdict but disagree that “two nights” is guaranteed once the dense partner is added.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11121:The original context-curve proposal is confounded and under-floored, but the rebuilt version is credible: start with one 1.5B 128-vs-long-context ABBA contrast, lengthen decode to amplify KV traffic, replace dead interior points with long-condition A=A nulls, and include or separately bound prefill-to-decode thermal carryover. Every length must self-floor; no 7B study may use the generic 5 J bar. Cost is **five to six nights from today**—four MVP plus one self-flooring claim window, with a second only if the thermal-matched control cannot fit—and **2–4 desk weeks**. Survival prior: **45–60%**. It has a lower venue ceiling than MoE but directly serves the KV/attention goal and stays within the frozen single-request boundary.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11179:## Winter 2026/27–Spring 2027: MoE second paper
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11181:After the MVP’s tables and artifact are locked, spend 4–6 weeks on the MoE gates. If all pass, collect one floor night and one mechanism night; add a third only if that need is determined prospectively by the frozen floor design. Target EuroMLSys or ICPE Emerging first; upgrade venue ambition only if the dense comparison, routing intervention, and replay artifact all land.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11183:If MoE fails a desk gate, switch immediately to BF16/Q4/Q8 quantization. Do not attempt to “repair” the MoE paper with a cross-model descriptive table.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11206:| A4 static-batch adapter | Infrastructure only | Cheap queued desk work; later supports batch/spec/MoE work |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11213:- MoE and quantization share multi-cell mint, multi-arm analysis, artifact hashing, and divergence-report machinery—but **not floors**.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11218:# Single best second-paper bet: MoE
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11220:Choose the re-anchored MoE paper because it has the highest publishable upside if its kill gates clear: it answers an original mechanism question, offers a causal within-checkpoint leg, and can explain why batch-1 unified-memory MoE behaves differently from active-parameter intuition and server-GPU results.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11226:1. **Pair ruling, before engineering:** Ed/advisor ratify Qwen3-30B-A3B and Qwen3-4B, exact artifact revisions, and the claim ceiling.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11239:4. **Second-paper commitment:** Will Ed reserve two to three Spring 2027 nights for the re-anchored MoE study if every desk gate passes? If not, select BF16/Q4/Q8 now as the lower-risk fallback.

codex
The first scan confirms the portfolio selected the Qwen3-30B-A3B/Qwen3-4B pair and gives a 4–6 desk-week envelope, but the referenced review lives elsewhere than the prompt’s shorthand path. I’m resolving the exact review and runtime locations now, then I’ll pin the kill criteria to source-level evidence.
exec
/bin/zsh -lc "sed -n '2040,2215p' RUN_STATE.md; sed -n '2740,2815p' RUN_STATE.md; sed -n '50,110p' docs/agent_playbook.md; sed -n '306,355p' TASK_QUEUE.md; sed -n '213,275p' TASK_QUEUE.md; find . -path '*rev-moe-routing-energy.md' -o -path '*moe*routing*energy*'; sed -n '1,150p' docs/strategy/2026-08-07-paper-portfolio/ADJUDICATION.md; sed -n '10920,11090p' docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
and work-selection state is generated immediately below from the kernel.

<!-- BEGIN GENERATED: state-kernel run-state-intake -->
## ACTIVE_STOP_CARD

Status: NONE — no stop card is active. Stop-card authority: D-050 / D-063 ([decision log](docs/decision_log.md)).

## Active Global Work-Selection Gates

NONE — no global work-selection gate is active.

## Restart By Machine-State Lane

Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-08-05). Latest report: [16h runway checkpoint 2026-08-03: D-108..D-112 minted; kernel pins 60; CAL-BRACKET held at 2e61ff9 (rule-11 gate owed for B1 round 2); winB license exhausted as drawn (r06 disposition parked, WINB-R06-DISPOSITION-01); mint chain D-110-blocked; CLAIMS_STATUS §1 honestly NONE; checkpoint block at the top of RUN_STATE is the successor resume script.](docs/run_reports/2026-08-03-16h-runway.md).

### [ED-EXTERNAL]

- READY — E1 `P1-008`: Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability).

### [QUIET-MAC]

- READY — Q2 `P2-006`: Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison.

### [AGENT]

- READY — A0 `P2-035`: RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests).

<!-- END GENERATED: state-kernel run-state-intake -->

## CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR #77 open

The RESUME list from the 2026-07-17 checkpoint is fully executed. The
relaunched execution-lens review, fix rounds 1-2, and their delta
re-audits had already run earlier on 2026-07-18 (commits `1aebf14`,
`6d80039`); this session closed the surviving P1 (child accepted any
JSON object as the frozen cooldown anchor) plus every finding from four
further delta re-audits, as fix rounds 3-8 in commit `ad0920b`:
canonical anchor validator (`joulewise/cooldown_anchor.py`) enforced
fail-closed at parent/CLI/controller boundaries; collision-safe,
crash-atomic, flock-serialized rejection-verdict custody
(`experiments/rejections/`); physical-domain baseline validation (the
`inf`-anchor fail-open gate is closed); discriminating process-race
regression. Suite green lead-side at every round boundary, final
`Ran 1746 tests`, `OK (skipped=12)`. Awake-half live probe validation
passed on real hardware (zero probe errors); the Ventura screensaver is
now disabled on the machine (`idleTime = 0`). PR #77 carries the gate
narrative; merge is Ed's call. Full record:
`docs/run_reports/2026-07-18-d077-fix-rounds.md`. Tooling: codex-run-v3
xhigh review-genre sessions ended with null final messages 4x
(bridge-resume recovered each; personal-tooling defect, recorded in the
run report and the global codex-delegation skill field notes, not the
repo queue).

## CHECKPOINT 2026-07-18: Claude script bridge runs in the pet's app task

The actual Claude Code fallback route is `scripts/codex-bridge`, not the MCP
server for recent audited work. The wrapper now sends `new` and `review` turns
through a dedicated app-owned Codex desktop task when the local host id is
configured. This is the same local-conversation state the native pet consumes;
the prior observer-only diagnosis was incorrect because the pet never reads
`~/.codex/claude-spawned/index.jsonl`. A live Sol/high smoke appeared in the
Codex app as thread `019f77a6-3612-7332-9f5e-be9fbde56be5`, turn
`019f77a9-2827-7de1-accf-ac2eda21927e`, and returned
`JOULEWISE_NATIVE_PET_BRIDGE_OK` through the script. Adaptive effort remains
unchanged: `high` fallback/default, `xhigh` only on named hard-task triggers,
and `ultra` only for sessions that must spawn subagents. Full record:
`docs/run_reports/2026-07-18-claude-codex-pet-observer.md`.

Committed 2026-07-18 on `impl/env-guard-cooldown` (after the D-077
packet boundary `6d80039`) with a lead execution review at the bench:
IPC socket ownership/permission checks, PID-checked host-task lock,
interrupt-on-terminate, no-network sandbox policy, and one-hop rule all
verified in `scripts/codex-app-bridge.mjs`; real-socket fake-router
tests plus observer lifecycle tests included; canonical suite green
lead-side (`Ran 1722 tests`, `OK (skipped=12)`). The same commit
carries the doctor-driven CLAUDE.md trims (global + repo; content
deduplicated into `.claude/skills/codex/SKILL.md`, which is the
operating home) and stamp-only `docs/site/*.html` provenance refresh.

## CHECKPOINT 2026-07-17 (late session): env-guard branch open, review pending

Window A floors contamination diagnosed from primary data: macOS Ventura
*video* screensaver on an awake display contaminated 43/50 suite-calibration
bundles (~+30% energy, −11% throughput; engage at HID-idle +20 min, dismiss on
unlock — pmset assertion log corroborated to the second). The six "low"
su-ABBA runs (18:16–18:36 UTC) are the only CLEAN suite runs; comparative
suite floors (4.923 J item / 24.62 J suite) are transition artifacts. The
professor's power-source hypothesis is refuted (AC/140 W/100% throughout).
Details: memory note + `docs/run_reports/2026-07-17-environment-guard.md`.

Branch `impl/env-guard-cooldown` (pushed, commit e2813ee) holds the D-077
response: environment-guard preflight (+`--arm-quiet-mode`), per-run idle
admission gate, cooldown v2, unwaivable `environment_admission_failed` claim
barrier, policy sidecars, contract/doc updates. Design consult (Sol xhigh,
thread 019f7356-32d3) adjudicated and encoded; implementation by Sol xhigh
(thread 019f7362-6627, resumed via codex-bridge after an MCP transport
timeout); session-close scope check SCOPE_OK; full suite green lead-side
(OK, 12 skips). Lead bench fix included: `pmset -g systemstate` parser now
accepts the live "Capabilities are:" form (was null → fail-closed on real
hardware); fixtures pinned to verbatim live output.

RESUME (in order):
1. Relaunch the adversarial review round (was stopped mid-run at checkpoint):
   fresh read-only Sol xhigh, execution lens, over `git diff main...impl/env-guard-cooldown`
   (prompt shape in `.codex-bridge/` prompt snapshots); lead holds the
   contract lens (done for cooldown_gate/claim-barrier/anchor hunks).
2. Triage findings → fix rounds (defect-shaped regressions) → DELTA RE-AUDIT.
3. Live-validate flagged probes during next quiet-window prep:
   `pmset -g systemstate` display-asleep form + screensaver-engaged probe
   while a screensaver is actually running (run report flags
   `live_validation_provisional`).
4. PR per operation-loop §5 gate shape; then re-run suite ABBA calibration
   under the new guard ([QUIET-MAC], needs Ed) — floors D-076 figures for
   suite comparative cells must be recomputed/caveated pending re-run.

Status: **CLEARED 2026-07-11.** Every clearance criterion met: all
checkpoint-#4 resume items executed (P2-044 fix+merge #55; P2-037
audit dispositions → two fix rounds + approved NEEDS_SCOPE expansion +
delta re-audit → #58; P2-043 #57; P2-045 #56); the four held hardening
PRs #50-#53 merged after the cross-stream integration review over the
combined tree (38 pre-merge cross-stream failures caught and fixed; 1
review blocker confirmed by refuters → PR #59; SF1 refuted; SF3 →
queue row P2-049); DOC-008 kernel refreshed at final head (schema v2,
authority field, branch impl/doc008-kernel awaiting PR); bookkeeping
arc complete (run report, C-028 council entry with layer catch-rates
and ~57-invocation spend record, D-064 ratified incl. manifest v3 +
claude-codex-report/v1 + WRITE_SCOPE enforcement; queue reconciled;
consistency sweep; site regen+deploy). All clearance-time opens since CLOSED same day: #59 MERGED, DOC-008
MERGED (#60). Remaining queue heads: P2-049/P2-050/TOOL-01.

## Superseded stop card (CP-5)

Status: **CLEARED 2026-07-09** by the CP-5 resume session. Every
clearance criterion was met: all three worktree diffs lead-gated
(envgate live-gated against the real affine mock bundle) and merged as
PRs #23/#24/#25; PR #22 merged after a fresh final-head pass; the
methodology synthesis and suite_next specs packet adjudicated (CP-6 in
the stream log); all accepted pre-campaign changes landed and merged
(PRs #26/#27/#28); both post-merge integration reviews CLEAN; queue
rank 0 closed. Full record:
`docs/run_reports/2026-07-09-cp5-resume.md`. No stop card is active.

## Current Project Status

**Mint era OPEN AND FIRST MINT LANDED (2026-07-30): main `da83337`. The
data exists and passes, and the code path that turns it into a published
floor now exists and has been exercised — `df-ph-decode-floor-mint1` is
mainline.**

### The central measurement fact (read before any measurement decision)

The instrument is **attribution-limited (~1 J), not noise-limited
(~0.3 J)** — D-078 clause 11, Ed-ratified. Floors publish LABELLED with
the widened number; the point floor is a repeatability diagnostic that
may never be the published claim floor. The anchor term appears in
**both** the floor and each claim's decision interval, so the effective
clearable effect is floor + claim-side bound ≈ 5 J for phase contrasts,
and neither term may later be deleted as an apparent double count. Do
not launch an instrument-tightening program; it was measured and
eliminated.

### Collection state

| Window | Contents | Verdict | Notes |
|---|---|---|---|
| a9, a10 | earlier corpora | **PASSED** | a10 supplies the absolute component |
| **B** (`04_phase_prefill_abba`) | 40 prefill ABBA members, 59/59 collected clean | **FAILED** | `instrument_calibration_mismatch`, bracket drift 11.581436 ms; preserved, not claim-bearing |
| **C** (`05_phase_decode_abba`) | 40 decode ABBA members, 59/59 collected | **PASSED** | bracket drift 1.279 ms; first comparative window in project history to pass |
| **D** (absolute) | 30 claim members, 49/49 collected | **PASSED** | bracket drift 0.484 ms, tightest of the campaign |
| **7B floor** (`window_7bfloor_20260729`) | Qwen2.5 7B decode floor, collected 2026-07-29 | **PASSED** | CLAIM-BEARING; governed extraction clean (`all_cells_extractable` true). Floors: absolute 6.294380135190098 J, comparative 13.998036715259254 J; absolute-cell member mean 192.38623252628366 J (n=10). NOT yet minted — `MINT-GENERALIZE-01` is OPEN and unblocked as of 2026-08-02 (gauntlet closed PR #93; D-088 no-mint condition lifted), so these figures live only in prose plus the out-of-repo custody extraction until that mint runs |
| **contrast** (`window_contrast_20260730`) | 40 contrast ABBA members + 7 references, 47 bundles, 1 supersession | **PASSED** | bracket drift 1.281 ms; contrast diagnostic 146.730349 J σ 0.241 (n=10 blocks) UNGATED — MANIFEST-CONTRAST-01 closed 2026-08-02 (PR #95); the gated claim now rides `MINT-GENERALIZE-01` then the D-095 chain |

Window B's cause is established and is NOT a clock problem: a GPU DVFM
power ramp that the rectangular-pulse fiducial estimator aliases into an
apparent onset shift (93.28% of the drift; the wall-clock term moved the
OPPOSITE way, −0.201464 ms). D-079 clause 3 adds a pre-flight screen that
- `validate-bundle --strict` green over all 6 real corpus bundles under
  the new era rule (PR #22 live gate: 6/6 valid, tamper fails named).

## Known Workspace State

- (2026-08-02, CURRENT) `main` and `origin/main` at `bcbc10b`; working
  tree clean except the untracked private `CLAUDE.local.md` (Ed's;
  never commit) and `.desk/` (adjudication custody; never commit).
  PR #93 merged (the c3 branch is closed). Branch
  `impl/d100-bii-binding` exists in the session worktree
  `scratchpad/d100bii` holding the UNCOMMITTED, audit-pending
  D100-BII-BINDING-01 diff (envelope protocol failure; see §9).
- (2026-07-31, historical) `main` and `origin/main` were both at `6ed1625`:
  the PR #89 merge `7ee680c` (D5-J) plus the close-out commits
  `49c1876`, `0d0bd0b`, and `6ed1625`. Branch `impl/mint-tool` is MERGED
  (verified `git merge-base --is-ancestor impl/mint-tool main`), as are
  `impl/floor-mint` and `impl/floor-label-clean`; all three may be
  deleted. Their scratchpad worktrees are still registered (`minttool`
  plus ~11 review/pin worktrees under the `9c166892…` session dir, and
  prunable entries under `ad48bfae…` and `d714f367…`) — `git worktree
  prune` plus explicit removal is owed as housekeeping. The working tree
  is clean except for the untracked private `CLAUDE.local.md` (Ed's
  file; never commit it).
- (2026-07-28 late, historical) `main` and `origin/main` were at that
  session's bookkeeping commit atop the PR #87 merge `058c918`. Branch
  `impl/mint-tool` (pushed, then UNMERGED) held the 9-commit mint series
  `2a0ecbc..697f741` in worktree
  `/private/tmp/claude-501/-Users-edr-code-JouleWise/9c166892-d763-42c4-8cf7-383912f054c9/scratchpad/minttool`;
  canonical suite at its head `1d83d68` is UNVERIFIED (rerun was in
  flight at checkpoint). Branch `impl/floor-mint` is merged via PR #87
  and may be deleted. NOTE: a concurrent session force-rewrote main
  history this evening (content preserved; see run report Anomalies) —
  verify `git log` freshness before building on a cached head.
- (2026-07-27, historical) `main` and `origin/main` were at `7337b33`. Branch
  `impl/floor-mint` @ `617060a` is pushed and NOT merged; it carries the
  pre-mint floor schema hardening. Window C (+bound) and a10 (+bound)
  remain FULLY resident in the working tree (mint #1 inputs); windows B/D
  and all other runs corpora are locally pruned to small evidence files
  (traces archived + verified in iCloud, see "Disk" above), and custody
  material lives OUTSIDE the repo at `~/JouleWise-window-custody/` — an
  agent searching only the repo will wrongly report quarantined evidence
  missing. Disk has 115 GB free; a window writes ~6 GB. The next quiet-window operator must start
  from a separate clean, merged-main measurement checkout per
  `docs/phase_2/window_runbook.md`.
- The generated state-kernel regions in this file and `TASK_QUEUE.md` are
  IN SYNC with `docs/process/state_kernel.json`
  (`python3 scripts/gen_state.py --check` exits 0), and the kernel's own
  content was refreshed on 2026-08-01 (desk adjudication session):
  stamped `updated: 2026-08-01`, `latest_report` points at
  `docs/run_reports/2026-08-01-desk-adjudication-session.md`, the MET
  rows are folded in, the completed
  `FLOOR-LABEL-01`, `STACK-ID-BIND-01`, `P2-015`, and
  `COOLDOWN-JOIN-DA1-01` rows are retired to
  `TASK_QUEUE.md`'s completed table, and the post-mint intake
  (`COOLDOWN-JOIN-GAUNTLET-01`, `MINT-GENERALIZE-01`,
  `MANIFEST-CONTRAST-01`, `SUPERSESSION-DUP-REFUSAL-01`,
  `QA-10A-JOIN-OMISSION`, `QA-10B-EXISTING-RETRY`) is folded in. Any
  further change means editing the kernel and then running
  `python3 scripts/gen_state.py` — never hand-editing the generated
  regions.
- (2026-07-25, historical) `main` and `origin/main` were at `c3e2647`,
  the PR #85 merge; PR #79's repair and PR #85's SCREEN+BUDGET
  implementation both landed with green final PR-head CI.
- The generated state-kernel blocks are authoritative for work selection.
  Hand-authored `RUN_STATE.md` and `TASK_QUEUE.md` text remains authoritative
  only for its own factual, policy, and historical domains;
  `docs/decision_log.md` remains the policy authority, exit checklists own
  phase completion, and evidence artifacts own scientific truth.
- Retained corpus and session scratchpad evidence are immutable.

## Historical Next-Work Snapshot (superseded 2026-07-15)

The following 2026-07-13 narrative is retained for chronology only. It is not
a live queue or restart instruction; the generated work-selection region is
the sole selector.

## Mission M0: Preflight (every session)

1. Read only the targeted `RUN_STATE.md` sections: `ACTIVE_STOP_CARD`
   if present, "Current Project Status", "Known Workspace State", and
   "What Is Next". If the stop card is ACTIVE, it overrides this
   playbook and the task queue until cleared.
2. Read `TASK_QUEUE.md`'s Current Queue and Do-Not-Do-Yet list.
3. Read the selected mission's own read-first list. Read `AGENT_PLAN.md`
   only at phase starts or when the project structure changes. Consult
   `docs/decision_log.md` by targeted decision ID, not as a whole-file
   intake step.
   If the session involves delegation, review, or multi-stream work, also
   read `docs/orchestration.md` (the process layer) — not optional for
   landing code.
4. Check workspace state with `git status --short --branch`; inspect
   recent commits only when the handoff or mission needs them.
5. `python3 -m unittest discover -s tests` — expect `Ran <N> tests` (N per `RUN_STATE.md` Current Verification; `, OK
   (skipped=10)` with zero expected failures as of 2026-07-08 after
   P2-013/P2-014 and the C-011 rigor mechanics. The skips are the `[analysis]`-extra chart tests plus one
   optional-jsonschema test. A red suite is itself the mission: stop and fix
   or report.
6. Review `docs/risk_register.md` at phase starts, before hardware tasks,
   when a trigger fires, or if >14 days passed since the last run report
   with no break recorded in `docs/milestones.md`.
7. At session end, always: update `RUN_STATE.md`, update `TASK_QUEUE.md`,
   write a dated run report in `docs/run_reports/`, update the phase exit
   checklist for anything that closed, and `PROJECT_STATUS.md` if
   advisor-visible state changed. Commit when the user asks or has
   standing-approved it.

Environment cautions:

- The repo must stay at a non-iCloud path (`~/code/...`; R-017). If you
  see `Operation not permitted` on reads inside the repo, stop, wait for
  the lock to clear, re-run the suite, and record the incident.
- CI installs no extras; every new test must pass on a bare Python
  (lazy imports, `skipUnless` for optional deps — D-009).
- Schema changes are additive-only until v0.2 (R-015/D-008).

---

## Mission M1: Slice 2N — Pre-Hardware Hardening (queue P2-007)

**Gate:** none. **Spec + acceptance:** `docs/phase_2/phase_2_plan.md`
Slice 2N. This mission adds the code-level route for each work item,
sourced from the 2026-07-05 external code review. Line numbers are from
commit `ae48abe` — re-locate by symbol name if the files have moved on.

Read first: `phase_2_plan.md` Slice 2N + Cross-Slice Contracts;
`joulewise/bundle.py`, `controller.py`, `reduce.py`, `interfaces.py`
(skim whole files — they are small and the invariants interlock).

2N is one mission but NOT one sitting: it touches adapter interfaces,
controller timing, reducer behavior, report parsing, CLI, schema export,
and validation policy. Work item-by-item with the suite green after each,
and land it as roughly three commits so a failure bisects cleanly:

- **Commit A — the adapter seam:** 2N.1 (RunContext + raw evidence),
  2N.2 (measured-window boundaries). Both touch controller/interfaces.
- **Commit B — the read layer:** 2N.8 (BundleReader), with 2N.4 (rail
  contract), 2N.7 (report alignment), and 2N.6's structured read
## Current Queue

The generated region below is the sole live queue and source of truth for
work selection. Edit the kernel and regenerate; do not hand-edit its rows.

Superseded (2026-07-15, WO-012; D-043): Q4/P2-019 sample size is frozen in the hash-bound analysis registry before outcomes, and outcome-dependent growth permanently demotes the contrast to exploratory; see `docs/contracts/analysis_plans.md` §Required fields.

Superseded (2026-07-15, WO-017; D-043): P2-027 publication and uninvolved-party re-reduction are optional owner-directed evidence-handoff work, not the default reproducibility or project-completion gate; see `docs/specs/c027/rpt-001_report_vertical_slice.md` §0.4 and `docs/contracts/publication_privacy.md` §Publication boundary.

<!-- BEGIN GENERATED: state-kernel current-queue -->
<!-- GENERATED from docs/process/state_kernel.json by scripts/gen_state.py. Do NOT hand-edit between the markers; edit the kernel and regenerate. -->

Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-08-05).

Generated compatibility table for repository consumers; the lane tables below are the detailed view of the same kernel state.

| Rank | ID | Priority | Status | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| E1 | P1-008 | P1 Phase Gate | READY [ED-EXTERNAL] | Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability). | Colloquium/report dates plus borrow window in docs/milestones.md; phase targets derived; acceptance-bar notes beside the P1-001 scope notes. Evidence: Dates + borrow window in docs/milestones.md; Derived phase targets; Acceptance-bar notes beside P1-001 scope notes. Authority: [Milestones + R-012](docs/milestones.md). Acceptance: [P1-008 acceptance](docs/process/state_kernel.json). Note: R-012 is the biggest active management risk for an undergrad timeline. |
| E2 | P2-027 | P2 Next Slice | READY [ED-EXTERNAL] | Publish a privacy-transformed, integrity-verified three-bundle pack from a clean tagged commit and obtain one documented external re-reduction by an uninvolved party. | Published pack plus a documented external re-reduction; until then the auditability claim stays L0-scoped. Evidence: Published pack; Documented external re-reduction. Authority: [C-020 + C-027 NEG-9](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-027 acceptance](docs/process/state_kernel.json). Note: Environment locks, pack preparation, integrity tooling, and fail-closed privacy transformation are merged; publication and external re-reduction remain ED-EXTERNAL. |
| E3 | P1-001 | P1 Phase Gate | READY [ED-EXTERNAL] | Capture supervisor approval and scope notes. | Dated notes in the Phase 1 exit checklist; unblocks full D-016 closure (P2-004). Evidence: Dated notes in docs/phase_1/phase_1_exit_checklist.md. Authority: [R-001](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: User-deferred 2026-07-06; R-001 mitigation holds: all work stays harness-shaped. |
| E4 | P1-003 | P1 Phase Gate | READY [ED-EXTERNAL] | Record the wall-meter decision: meter make/model or unavailable verdict plus measurement/export method. | Exit-checklist wall-meter section filled; informs D-018 boundary calibration. Evidence: Wall-meter section of the Phase 1 exit checklist filled. Authority: [D-018/C-003](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Elevated value: gates Q6 boundary sensitivity (C-003). |
| E5 | P1-004 | P1 Phase Gate | READY [ED-EXTERNAL] | Fill the network/interconnect topology plan: physical topology, link-speed paths, throughput method. | Network section of the Phase 1 exit checklist recorded. Evidence: Network section of the Phase 1 exit checklist recorded. Authority: [R-011](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Partial. |
| E6 | P1-006 | P1 Phase Gate | READY [ED-EXTERNAL] | Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L). | Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: [Remote gate / NV-GATE-2](docs/phase_2/hardware_slice_implementation_guide.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). |
| Q1 | MET-WINDOW-C-01 | P1 Phase Gate | BLOCKED — FROZEN-PLAN-READINESS-RECORD (A reviewed FROZEN-PLAN READINESS RECORD exists before any collection night: frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight, launcher-verified), ED-5A (Ed section-5A window prep FRESH POST-MOVE (the 2026-08-02 laptop move invalidated settled-machine conditions; network time off, AC, settled machine, walk-away)) [QUIET-MAC] | Execute a reviewed fresh-claim collection plan beginning with Window C: no Window B member enters a replacement claim basis; split prospectively across windows C and D if the complete replacement cannot fit the 2-4 hour envelope with at least 20 percent failure margin. | The fresh-claim metrology plan replaces every still-desired Window-B claim component without using any Window-B member, under reviewed frozen-plan and validated-window controls. Evidence: A fresh-claim plan recollects every still-desired Window-B claim component beginning with Window C; no Window B member enters a replacement claim basis; The fresh plan includes the still-required C2, C4, and C5 collection scope under the frozen-plan discipline, split prospectively across windows C and D if one window cannot retain at least 20 percent failure margin inside the runbook's 2-4 hour envelope; Window operated under the validated protocols: bird-SIGSTOP with identity custody, guarded launcher, one-line arm messages with zero output streaming during idle-gate exposure, third-failure salvage rule; Whole-window verdict emitted by machinery that has passed MET-VERDICT-ADJ-01 adjudication; supersessions recorded once, pre-verdict; both roots backed up rc=0. Authority: [D-113 clauses 7-9 fresh-claim reset, readiness fence, and prospective C/D split](docs/decision_log.md). Acceptance: [MET-WINDOW-C-01 acceptance](docs/process/state_kernel.json). Fence: A window-C dangler seeking the b-ii mechanical license before D100-BII-BINDING-01 closes RETURNS TO THE GATE; the window itself may run (D-106 revisit clause). Fence: Before any collection night, the ordinary launcher verifies a reviewed FROZEN-PLAN READINESS RECORD binding the frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight (D-113 clauses 8-9 hard start fence). Fence: Plan root assembled and frozen before measurement; no plan edits after freeze (D-096 frozen-plan ratification). Fence: Zero agents AND zero operator output streaming during measurement idle gates; arm messages are one line; bird-SIGSTOP protocol with identity custody and fail-safe CONT trap on all exit paths (2026-08-01 run report: streaming-during-idle-gate hazard + bird-SIGSTOP protocol). Note: D-113 clauses 7 and 9: the former remainder-only scope is SUPERSEDED. A fresh-claim plan is required; no Window B member enters a replacement claim basis. If the full replacement exceeds the runbook's 2-4 hour envelope with at least 20 percent margin, split it prospectively across windows C and D. |
| Q2 | P2-006 | P2 Next Slice | READY [QUIET-MAC] | Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison. | Strict-valid reducer-0.5.2/0.6.2 campaign bundles with counterbalanced order and drift sentinels; interpretation uses campaign claim_readiness plus the merged fail-closed analysis engine. Evidence: Strict-valid campaign bundles under the fixed validator; Counterbalanced order manifest + drift sentinel positions recorded; baseline_results.md with variance + prefill/decode comparison. Authority: [Phase 2 plan + analysis plans](docs/phase_2/phase_2_plan.md). Acceptance: [Phase 2 exit checklist](docs/phase_2/phase_2_exit_checklist.md). Note: Software interpretation gates are satisfied; Window-A floors landed 2026-07-31 (mint #1 mainline), so only the campaign remains. |
| Q3 | P2-010 | P2 Next Slice | READY [QUIET-MAC] | P2-010b remainder: affine smoke campaign execution (B=5) plus envelope-gate verdict on its bundles, on a quiet-window tail. | joulewise envelope-gate emits the D-036 verdict from strict-valid smoke bundles; campaign acceptance in AP-5. Evidence: D-036 verdict from strict-valid smoke bundles; AP-5 campaign acceptance met. Authority: [AP-5 + affine stream log](docs/contracts/analysis_plans.md). Acceptance: [P2-010 acceptance](docs/process/state_kernel.json). Note: Envelope-gate script merged 2026-07-09 (PR #23); only the campaign remains. |
| Q4 | P2-019 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC] | q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6). | Grid campaign lands per AP-1; top-up near-floor cells before L3 wording. Evidence: AP-1 grid campaign bundles; Holdout cells honored; 8192 anchor cells on small+mid models. Authority: [AP-1](docs/contracts/analysis_plans.md). Acceptance: [P2-019 acceptance](docs/process/state_kernel.json). |
| Q5 | P2-020 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC] | Content-sensitivity sentinel campaign (Window B, AP-6): five equal-shape ids-native conditions, n sized from Window A; request-energy deltas and MDE verdicts. | Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046). Evidence: Five equal-shape ids-native conditions; Request-energy deltas + MDE verdicts. Authority: [AP-6 + D-046](docs/contracts/analysis_plans.md). Acceptance: [P2-020 acceptance](docs/process/state_kernel.json). Note: Generator merged (PR #19), manifests ready (PR #26); a tiny AP-6 pilot may ride a Window-A tail (CP-6). |
| Q6 | P2-012 | P2 Next Slice | BLOCKED — P2-006 (identification-core runs after Window A) [QUIET-MAC] | Identification-core campaign (jw_mixed) after Window A; natural-EOS pilot plus full panels in later phases. | Campaign bundles strict-valid per AP-4; no category claims outside matched strata. Evidence: Strict-valid bundles per AP-4; No category claims outside matched strata. Authority: [AP-4 + D-039/D-040](docs/contracts/analysis_plans.md). Acceptance: [P2-012 acceptance](docs/process/state_kernel.json). Note: Manifests generated + regenerated (PR #26); runner/runtime/validator hash guards merged (PRs #24/#27). |
| Q8 | P2-046B | P1 Phase Gate | READY [QUIET-MAC] | Execute the frozen load-transition alignment harness on the real Mac and adjudicate the production interval-support bound from offset and residual artifacts. | Real-Mac counterbalanced transitions validate or widen the P2-038 conservative interval-support bound; physical evidence replaces the PROVISIONAL Part-A verdict. Evidence: Counterbalanced real-Mac transition artifacts; Offset, residual, and conservative-bound verdict; P2-038 bound cited or amended. Authority: [Hardening adjudication C6](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-046B acceptance](docs/process/state_kernel.json). Fence: Do not promote Part-A fixture evidence or retain PROVISIONAL interval support after a conflicting physical verdict (Hardening adjudication C6). Note: Part A merged in PR #50; Part B is quiet-machine physical execution. |
| Q9 | P2-047B | P2 Next Slice | BLOCKED — P2-047A (frozen controller-overhead harness exists) [QUIET-MAC] | Run the frozen controller capture-overhead ABBA on the quiet Mac and record the floor-governed overhead verdict. | Real floor-governed ABBA execution yields a named overhead verdict with instrumented-stack scope unless a separate subtraction model is justified. Evidence: Floor-governed quiet-Mac ABBA bundles; Named overhead verdict; Instrumented-stack scope or separately justified model. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047B acceptance](docs/process/state_kernel.json). |
| A0 | P2-035 | P3 Research Expansion | READY [AGENT] | RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests). | Promotion decided per registry rules; harness gaps closed before promotion. Evidence: Registry promotion record per docs/research_question_bank.md rules; G-RQVAR-* harness gaps implemented with tests. Authority: [RQ-ENERGY-VARIANCE candidate design](docs/specs/rq_energy_variance_design.md). Acceptance: [P2-035 acceptance](docs/process/state_kernel.json). Fence: C-004 quarantine binds; no promotion before floors exist (C-004 quarantine). |
| A2 | QUIET-GUARD-01 | P1 Phase Gate | READY; GATES live_promotion: T3-CHAR-PAIR-01 [AGENT] | Quiet-guard work order (full gauntlet): host-wide quiet lease, refuse-at-arm, characterized resident watcher; plus Ed requirements recorded 2026-08-03 — t3-armed operation (a t3-launched claude session arms a detached guarded chain, then self-quits and quits t3 with a survivor inventory), t3-relaunch-on-close, and README-banner signaling. | The quiet guard lands through the full C-028 gauntlet with the host-wide lease, refuse-at-arm, characterized resident watcher, and all three Ed-required t3 behaviors working end to end. Evidence: Commit 1 only: host-wide quiet lease implemented and enforced; Refuse-at-arm: arming refuses when the host is not quiet (usable by the ordinary guarded-shell window launcher); Installed-INACTIVE: no arming path, no production lease, live_promotion=false; Seven focused-audit blockers closed (priv-esc interpreter, validate/install TOCTOU, arbitrary-root initializer, macOS process identity, boot/hostname wedge, decision entry, independently-pinned tests); Full gauntlet on the landed commit: independent audit + delta re-audit of every fix round. Authority: [Ed directive 2026-08-03 ~23:55 (t3-drive chain is the critical path; non-in-flight work paused) + t3-doctrine gate synthesis + synthesis-exhibits SX5](docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md). Acceptance: [QUIET-GUARD-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-05: DESCOPED by Ed's directive (t3 control-plane build-out not worth its cost; t3 stays the INTERACTIVE control plane, t3-resident-during-windows dropped; windows return to the zero-agent guarded-shell path). ROW RE-SCOPED TO COMMIT 1 ONLY: the host-wide quiet lease + process census, installed-INACTIVE. Retained because it has non-t3 value — mechanical refuse-at-arm for the ordinary guarded window launcher, replacing procedural eyeballing. SHELVED: commit 2 (launcher interception), commit 3 (t3 handoff + resident watcher), commit 4 (t3-relaunch + README banner projection + all credential handling). In flight at checkpoint: Sol fix round closing 7 audit blockers; work UNCOMMITTED in scratchpad/quietguard (branch impl/quiet-guard); harvest scratchpad/qg-fix-out.md. |
| A3 | FLOOR-BIND-01 | P1 Phase Gate | READY [AGENT] | Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions. | Floor/MDE artifacts stop being self-attesting: claim consumption authenticates admissible widths and complete governed campaign membership against extraction evidence, retiring registered limitation L1. Evidence: Canonical floor cells bound to their extraction report and source-member disposition (or extraction gates and widths rederived at binding); Binding refuses on any stored width/corner mismatch or campaign-membership deviation; Integration regressions reject width substitution and member omission end-to-end. Authority: [D-078 clause 8 (confirmation round 9, registered limitation L1)](docs/decision_log.md). Acceptance: [FLOOR-BIND-01 acceptance](docs/process/state_kernel.json). Fence: Until this row closes, claim-bearing analysis may consume floor artifacts only from same-custody-session governed extraction; standalone artifacts are non-claim-bearing (D-078 clause 8 L1). Note: Minted 2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1 workflow rule mitigates until closed. |
| A4 | AXI-SB-ADAPTER | P2 Next Slice | READY [AGENT] | Implement the static-batch Mac adapter follow-on minted by the AXI-SB supported verdict: batch_size configuration knob, per-sequence request-scoped token events per the AXI-SA contract, realized-vs-configured batch recording, and structured memory-fit outcomes, with strict-valid mock or smoke bundles and no energy claims. | The follow-on static-batch adapter turns the AXI-SB supported verdict into an instrumented batch_size-configurable Mac runtime path emitting per-sequence AXI-SA events, with memory-fit failures structured and zero claim or quiet-Mac consumption. Evidence: A batch-capable Mac adapter exposes a batch_size configuration knob and emits per-sequence request-scoped token events conforming to the landed AXI-SA event contract, validated by strict bundle validation on a mock or live smoke bundle; Realized batch size is recorded alongside configured batch size, and structured memory-fit failures are captured as data rather than crashes; No energy claim, campaign scheduling, or quiet-Mac consumption occurs in this row; AP-BATCH execution remains separately floor-gated per AXI-SE. Authority: [AXI-SB verdict document (supported; mint-on-supported follow-on)](docs/specs/axi/sb_static_batch_verdict.md). Acceptance: [AXI-SB-ADAPTER acceptance](docs/process/state_kernel.json). Fence: Build on the verified BatchGenerator path with per-request observability; a Python loop over singleton calls is not a batch adapter (AXI-SB verdict document classification and scope). Fence: Keep continuous batching deferred and do not infer coalescing, scheduler-optimum, or offered-load claims from static-batch work (D-070 static-batch scope). Fence: Window A retains every quiet-Mac measurement slot; adapter implementation and mock or smoke validation are agent-lane work and consume no quiet-Mac campaign time (D-070 Window A ownership). |
| A5 | TEST-SPEED-01 | P2 Next Slice | READY [AGENT] | Cut suite wall-clock (three Ed-ratified levers, 2026-08-03): collect per-module timing data with the recovered profiling scripts, implement the shard-runner and the PR-fast/full tier split from the data, and evaluate Blacksmith runners. | The three Ed-ratified levers land: timing data drives a shard-runner plus PR-fast/full split with the full suite still holding every authoritative gate, and the Blacksmith runner option is evaluated on evidence. Evidence: Per-module timing corpus collected on a quiet bench (the recovered Sol profiling scripts; timings.jsonl + summary.json banked under .desk/) identifying the slow tail by module and by test; Shard-runner and the ratified PR-fast/full tier split implemented from the data: the fast tier gates PRs, the FULL suite remains the gate for merges, verdicts, and audited heads; zero test deletions; Blacksmith runner evaluation recorded with an adopt/defer recommendation and measured latency/cost comparison against GitHub-hosted runners. Authority: [Ed ratification 2026-08-03 (three levers: suite-speed priority, PR-fast/full split, Blacksmith runner evaluation); origin row in the 2026-07-28 report](docs/run_reports/2026-07-28-floor-mint-implementation.md). Acceptance: [TEST-SPEED-01 acceptance](docs/process/state_kernel.json). Fence: No test deletions, and the fast tier never substitutes for a required full-suite gate: merges, whole-window verdicts, and audited heads keep the full suite (D-061 zero-deletion clearance; the full suite as the authoritative gate). Note: 2026-08-03: timing DATA collected (quiet bench, 93 modules, 695s serial; raw in .desk/test-speed-consult/timings-20260803.jsonl) and DESIGN done (.desk/test-speed-consult/DESIGN-from-timing-data.md). Findings: suite is a 2-module problem (run_campaign 182s + p2038 133s = 45%); module-atomic sharding CAPS at 182s so those two must be split by TestCase class; shard-runner + splits -> ~87s wall @8 workers (6.5x); fast tier (drop 11 heavy integ modules) -> 25-40s PR feedback with the full suite still the merge gate. Blacksmith (lever 3) NEEDS ED (account/cost; likely marginal once sharded). Implementation queued: scripts/shard_tests.py + class-split + CI matrix — mechanical, delegatable, zero deletions (D-061). 2026-08-04: PHASE 1 LANDED — PR #98 MERGED (9b02539): module-atomic shard-runner + 8-way CI shard matrix, main CI green under it (~15min -> ~6min proven); worktree/branch pruned. Remaining scope: class-split of the two heavy modules (Phase 2), fast PR tier (lever 2), Blacksmith runners (lever 3, NEEDS ED). |
| A6 | AXI-SD | P2 Next Slice | READY [AGENT] | Prepare the matched dense/MoE pair proposal with the consult's pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT. | A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016's cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: [AXI handoff work program S-D](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SD acceptance](docs/process/state_kernel.json). Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership). |
| A7 | AXI-SE | P2 Next Slice | READY [AGENT] | Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult's floor and ownership closures. | The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A's gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: [AXI handoff work program S-E](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SE acceptance](docs/process/state_kernel.json). Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership). |
| A10 | SUPERSESSION-DUP-REFUSAL-01 | P1 Phase Gate | READY [AGENT] | Rule on and then implement write-time refusal in the supersession recorder, which today appends silent duplicate records when run more than once for a member and voids campaign membership downstream; the ruling is the first half of the deliverable. | A repeat recorder invocation for the same member refuses instead of appending a duplicate record. Evidence: The write-time refusal ruling is recorded in the decision log before any implementation; A regression asserts that a second recorder invocation for the same member refuses. Authority: [D-086 supersession-aware cooldown-evidence join (recorder duplicate-append defect)](docs/decision_log.md). Acceptance: [SUPERSESSION-DUP-REFUSAL-01 acceptance](docs/process/state_kernel.json). Fence: Until the refusal lands, run the supersession recorder exactly once per member (D-086 operator mitigation). Note: Minted 2026-07-30 from the D-086 arc; ruling-first, no implementation before it. |
| A11 | T3-PROV-SCHEMA-01 | P2 Next Slice | READY [AGENT] | Implement the tracked four-axis provenance record with authority_class and the ingestion-event schema, then make reverse-consult admission consume authoritative launch-route and owner_kind evidence so bridge §8's transitional convention ends. | The four-axis provenance plus ingestion-event schema ends bridge §8's transitional convention by mechanically enforcing reverse-consult eligibility from authoritative route and ownership evidence. Evidence: A tracked provenance record represents the four axes control_plane, transport, authority_class, and governance, with authority_class explicit; A tracked ingestion-event schema binds native session identity, output digest, lead disposition, and tracked process-trace location; Reverse-consult admission consumes authoritative launch-route and owner_kind evidence rather than self-reported headers; Rejection regressions fail closed on delegated, unknown, or contradictory provenance and prove that merely persisting the schema cannot end the transition. Authority: [Bridge protocol §8 transitional reverse-consult enforcement follow-on](docs/contracts/bridge_protocol.md). Acceptance: [T3-PROV-SCHEMA-01 acceptance](docs/process/state_kernel.json). Fence: The transition ends only when admission consumes authoritative launch-route and owner_kind evidence with rejection tests; defining or persisting the schema alone is insufficient (Bridge protocol §8 fail-closed transition rule). Note: Bridge §8 currently validates only self-reported headers; consumption-side fail-closed is the actual protection until this row supplies real enforcement. |
| A12 | MINT-GENERALIZE-01 | P1 Phase Gate | BLOCKED — D-110 (The remaining D-110 re-mint conditions hold before ANY further mint, including the governed 7B mint: (b) the acceptance artifact is ISSUED after verified R2 backfill and deterministic ledger bootstrap; (c) the evidence_root_id validator pin is widened) [AGENT] | Generalize the mint beyond the mint-1 pair: scripts/mint_floor_artifact.py is hard-pinned to the p2_015, a10, and window-C evidence (cell id, plan sha, both order-manifest ids, the two member counts, the expected operative-floor text), so build a sibling taking those pins per plan and carrying the 7B mint's remaining scope. | A generalized mint sibling takes the mint-1 hard pins per plan so a second floor artifact can be minted without weakening the pre-registration gate. Evidence: A 7B decode-floor artifact mints from qwen25_7b_decode_floor_v1 evidence with its own hard six-decimal operative-floor literal supplied per plan, never derived inside the mint path; The pre-registration gate passes as-embedded and validate_floor_artifact returns no findings; The generalized path mints byte-identical to the reviewed core from the same inputs on the same integration tree (core-vs-wrapper parity per D-109 addendum II; NOT a match against historical mint-1 digests, which D-110's corrected re-mint may legitimately change). Authority: [splitwise_decode_v1 campaign doc section 2 Blocker A (mint pins); D-082, D-084, D-085 Q6](docs/phase_2/splitwise_decode_campaign.md). Acceptance: [MINT-GENERALIZE-01 acceptance](docs/process/state_kernel.json). Fence: Generalize the plumbing, never the pins: six-decimal floor literals and lead-verified digests stay supplied per plan and hard-checked in-tool (D-082 and D-084 operative-floor pins). Note: 2026-08-03: D-110 (sweep finding RT-1/RT-2): mint #1 is retroactively NON-CLAIM-BEARING (taint-and-remint); the night consult's conditional 7B-mint license is SUSPENDED. The mint-1 byte-compare replay completed BYTE-IDENTICAL at pinned 3de370ec (all four digests; docs/process_traces/2026-08-03-q1-remint-bytecompare/). 2026-08-05: condition (a) is satisfied by merged PR #100. Condition (b) preparation is complete and its verification blocker is resolved: the B1 disposition is lead-ruled 30/2/6 and deterministic bootstrap is implemented on impl/ledger-bootstrap, under audit. Condition (c) is in flight on impl/validator-rootpins. The row remains hard-blocked on the still-pending D-110 (b)+(c) completion gate. |
| A13 | CODEX-BRIDGE-SANDBOX-01 | P2 Next Slice | READY [AGENT] | Correct scripts/codex-bridge review-mode sandbox enforcement: pass the read-only sandbox flag instead of launching workspace-write while recording read-only metadata. | codex-bridge review launches read-only exactly as its audit manifest claims, with regression coverage binding recorded and effective sandbox values. Evidence: scripts/codex-bridge review passes the read-only sandbox flag to every non-app review launch; The review audit manifest records the sandbox actually supplied to the launch; A regression proves the recorded review sandbox and launched sandbox are both read-only and cannot drift apart. Authority: [2026-08-05 live inspection: review records observer_sandbox=read-only but the non-app launch omits -s read-only](scripts/codex-bridge). Acceptance: [CODEX-BRIDGE-SANDBOX-01 acceptance](docs/process/state_kernel.json). Note: Caught live 2026-08-05: observer_sandbox is set to read-only, but the non-app review invocation omits the sandbox flag, so audit metadata misstates enforcement. |
| A14 | COLDGATE-HANDOFF-01 | P2 Next Slice | READY [AGENT] | Build runner-owned sealed-byte judge handoff: capture immutable in-process packet, charter, and exhibit byte snapshots; compute digests over those exact buffers; construct judge input from the same buffers; and specify and test transport byte-to-request binding. | The convening runner delivers exactly the bytes the validator observed, with immutable snapshot-to-judge transport binding and a judge-identity-bound runner receipt. Evidence: Deterministic post-hash path replacement delivers the original immutable snapshot or refuses without invoking the judge; Same-inode mutation through a second descriptor never delivers mutated bytes under the old receipt; Judge-received payload hashes equal the receipt hashes and the runner receipt binds the judge request or session identity. Authority: [2026-08-05 COLDGATE-VALIDATOR F3 consult Q2 handoff ruling and tests](docs/process_traces/2026-08-05-cgv-f3-consult/CONSULT-REPORT.md). Acceptance: [COLDGATE-HANDOFF-01 acceptance](docs/process/state_kernel.json). Fence: Until this row lands, no validator PASS may be used to convene a cold judge (2026-08-05 F3 consult standing operational constraint). Note: Design warnings: holding file descriptors open does NOT seal bytes because a second descriptor can mutate the same inode; path-based launch-time revalidation alone leaves a revalidate-to-read race. Pending-ratification payload carried by this row: the proposed amendment to docs/process/coldgate_charter_registry.md separating validator observation from runner custody. The registry is Ed-ratified and is NOT edited by this or any session without a cold-gate/Ed ratification. |
| A15 | C3-RECOGNIZER-EXACT-01 | P1 Phase Gate | READY [AGENT] | Close the two D-105-registered recognizer-exactness blockers: exact escape-ordering completion-feasibility (F1) and the documented decidable superset number grammar (F2, with the D-104 cl.2 subset-direction amendment), plus the bundled F3/N2 release-path hygiene if not already landed. | The two registered recognizer-exactness blockers (escaped-key ordering; number-prefix over-acceptance) close together under D-105's refuter-amended criteria with an independent audit. Evidence: F1 closes via the exact escape-ordering completion-feasibility procedure (hex-digit interval derivation, surrogate-pair arithmetic, prefix-extension rule) with both registered counterexamples pinned verbatim and a BMP/non-BMP boundary property test; F2 closes via a DOCUMENTED DECIDABLE SUPERSET grammar of json.dumps float spellings (fixed-notation exponent window, coefficient rules, two-digit exponent padding) — the D-104 cl.2 subset direction is amended per D-105 to 'accepted within the documented superset AND containing every real writer prefix'; both counterexamples refuse; randomized-float completeness property passes; Both registered blockers close together with an independent delta audit at the exact head; the acceptance-set contract re-proven in both amended directions over a corpus including non-BMP keys. Authority: [D-105 disposition synthesis (F1/F2 registered as a NEW ruling, not D-088 precedent; closure criteria refuter-amended; number-grammar exactness struck)](docs/decision_log.md). Acceptance: [C3-RECOGNIZER-EXACT-01 acceptance](docs/process/state_kernel.json). Fence: F1/F2 severity may not be downgraded by any role; closure ONLY through this row; while open the recognizer's accepted set may only SHRINK; the custody sidecar and writer-side ASCII key assertion (the D-105 micro-commit) are load-bearing compensating controls and may not be weakened (D-105 registration fences). Fence: This registration must not be cited as precedent for registering corpus-absent defects generally; it is a new ruling made with three recorded independent absence scans and mechanical compensating controls (D-105: branch-introduced registration is NOT QA-10A/B precedent). |
| A16 | P3-000 | P3 Research Expansion | BLOCKED — R-003 (user approves the 3.0.2 installs (R-003)) [AGENT] | KV persistence feasibility spikes (Phase 3 Stage 3.0): 3.0.2+ open; 3.0.2 needs installs and inherits the 3.0.1 harness shape plus its two deferred hardening fixes (ledger C-8). | Verdicts recorded in docs/phase_3/kv_feasibility.md; checklist rows are the status authority; must complete before any borrow-window scheduling. Evidence: Verdicts in docs/phase_3/kv_feasibility.md; Checklist rows updated. Authority: [D-035/D-036](docs/decision_log.md). Acceptance: [Phase 3 exit checklist](docs/phase_3/phase_3_exit_checklist.md). Note: 3.0.1 complete and merged (PR #9, replay_supported). |
| A17 | P2-022 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)) [AGENT] | Marker-shim energy-layer feasibility spike: verdict-shaped export path only (external_markers_supported / partial / external_markers_unsupported). | 3+ marked items, external result artifact hashed, strict bundle valid; verdict recorded. Evidence: 3+ marked items; External result artifact hashed; Strict bundle valid. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [Adapter contract](docs/contracts/adapter_contracts.md). Fence: Energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim (D-041). Note: C-027: the C-026 revisit-after-Window-A note is a revisit of sequencing, not permission. |
| A18 | P2-023 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)), P2-022 (P2-022 verdict recorded) [AGENT] | HumanEval import smoke: benchmark_import manifest plus suite profile plumbing goal; freeze subset with C-005 discipline, MIT license/provenance fields, 256/512-token completion policy. | Frozen subset with license/provenance fields lands; no pass@k/accuracy/capability claim. Evidence: Frozen subset manifest with C-005 discipline; License/provenance fields present. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [RQ bank import-smoke design](docs/research_question_bank.md). Fence: No pass@k, accuracy, or capability claim (D-041). |
| A19 | P2-024 | P2 Next Slice | BLOCKED — P2-006 (2M reductions identify floor/MDE headroom) [AGENT] | Cheap-campaign shortlist: select among C5-1.6 sampler ABBA, C5-1.12 quant decomposition, C5-1.8 runtime attribution per measured floors; the selected campaign is then queued [QUIET-MAC]. | Explicit selection recorded after floors; selection cites floor/MDE headroom. Evidence: Selection recorded with floor/MDE headroom rationale; Selected campaign queued as a quiet_mac task. Authority: [C-015 + RQ bank](docs/research_question_bank.md). Acceptance: [P2-024 acceptance](docs/process/state_kernel.json). |
| A21 | P3-001b | P3 Research Expansion | BLOCKED — P2-006 (2M affine coefficients exist) [AGENT] | Seed the split analysis-plan row: pre-registered compositional predictions per pairing/link (including named same-boundary headline and at least one predicted-crossover cell if feasible), per-cell transfer-boundary labels (D-049). | AP row committed before any split hardware run; phase_3_plan amendment line landed. Evidence: AP row committed pre-split-hardware; phase_3_plan amendment line landed. Authority: [D-048/D-049](docs/decision_log.md). Acceptance: [Analysis plans (split row)](docs/contracts/analysis_plans.md). |
## Current Do-Not-Do-Yet List

- (satisfied 2026-06-12) The mock bundle/reducer path and report generator
  now exist; dashboard/report work is no longer blocked.
- (satisfied 2026-06-12) The mock lifecycle is runnable, so live
  MLX/powermetrics implementation may proceed once its hardware gates open
  (P1-002 + D-016); follow `docs/phase_2/hardware_slice_implementation_guide.md`.
- (resolved 2026-06-12) Hailo feasibility has a verdict
  (`unsupported_workload`); do not implement a Hailo backend — report it as
  an applicability finding.
- Do not implement schema v0.2 before Phase 3 Stage 3.1 (design is fixed in
  D-008; implementation waits).
- Phase 3 DESK feasibility spikes (Stage 3.0.x) may run now — their gate
  (2G/2I + model) is open. Do not start Phase 3 DATA collection, hardware
  pairings, or borrow-window scheduling before 2M baselines and the Stage
  3.0 verdicts exist (C-007 wording fix; was previously stated as a
  blanket Phase 3 hold that contradicted the queue).
- Do not schedule the 3080 Ti borrow window before Stage 3.0 verdicts and the
  rehearsed runbook exist (R-006).
- Do not start Phase 3 live-split work (3.3) before offline replay (3.2) has
  produced data.
- Do not close D-016 (model selection) without P1-001 supervisor scope or an
  explicit user go-ahead.
- (satisfied 2026-07-06) Slice 2N landed; 2G/2H may start once their own
  gates (D-016 + `[mac]` install; privileged sample + D-004 sudoers) open —
  build on the post-2N seams (RunContext raw evidence, D-026 markers,
  D-027 rail rows, 2N.3 observed-token fallback).

## Queue Maintenance

At the end of substantial work:

- Update live status, rank, dependencies, and new tasks in
  `docs/process/state_kernel.json`.
- Remove terminal tasks from the kernel only after their owning completion
  evidence supports closure; preserve the dated Completed row here.
- Run `python3 scripts/gen_state.py`; never hand-edit generated queue or
  restart rows.
- Keep hand-authored edits here to policy, completed/history records, and
  non-selection context.

## Intake Batch Owed To The Kernel (2026-07-30/31)

**PARTIALLY FOLDED 2026-07-30.** Six rows —
`COOLDOWN-JOIN-GAUNTLET-01`, `QA-10A-JOIN-OMISSION`,
`QA-10B-EXISTING-RETRY`, `MINT-GENERALIZE-01`, `MANIFEST-CONTRAST-01`,
and `SUPERSESSION-DUP-REFUSAL-01` — were folded into
`docs/process/state_kernel.json` on 2026-07-30; their staged rows were
removed from this table. Of the six, only `MINT-GENERALIZE-01` and
`SUPERSESSION-DUP-REFUSAL-01` remain LIVE as of 2026-08-02: the
gauntlet trio retired with PR #93 and `MANIFEST-CONTRAST-01` with
PR #95 (see the completed table).
`COOLDOWN-JOIN-DA1-01` followed on 2026-07-31 (D-093), in the same pass
that retired `P2-015` to the completed table and closed
`QUEUE-RECONCILE-01`; both of those staged rows were removed too. It was
short-lived as a live row: DA-1 closed later the same day inside the
gauntlet's commit 2 and `COOLDOWN-JOIN-DA1-01` is now retired to the
completed table (PR #91, `67d268a`).

**The rows that remain below are STAGED, not live**, and stay staged by
magistrate scope decision 2026-07-30 (the P2/P3/P4 residue is not
competing for this window's selection). Work selection is the generated
region below; nothing here competes with it until the magistrate folds a
./docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md
./docs/strategy/2026-08-07-paper-portfolio/reviews/rev-moe-routing-energy.md
# Paper portfolio — magistrate adjudication (2026-08-07)

**Process:** 24 paper directions (20 directed + 4 open-ended) each developed
by a Sol high/fast session with full repo context (BRIEF.md), each
adversarially counter-reviewed by an Opus 5 referee (reviews/), then two
opposing-prior Sol xhigh syntheses (SYNTHESIS-*.md). This file is the
magistrate's binding synthesis of the syntheses. Ed's rulings section at
the end supersedes anything here once he answers.

## The adopted arc

1. **P1 — the MVP capstone paper (in flight, draft COMPLETE on main as of
   PR #110).** Data: the three D-117 windows **plus Window C as night 4**
   (both syntheses' top recommendation — §6's six characterization rows
   are the paper's own contribution 4 and currently have no scheduled
   evidence; shipping them empty or descoping is Ed's ruling #1).
2. **P2 — second paper: QUANTIZATION, shrunk to BF16/Q4/Q8** (the
   pragmatics-first pick; referee verdict VIABLE — the only unconditional
   one in the corpus). Three extension nights + 4-8 desk weeks; consumes
   the D-117 Q4 floors DIRECTLY as a rung; BF16-Q4 anchors (guaranteed
   resolvable), Q4-Q8 adjudicates a real open question; an honest refusal
   on adjacent rungs is itself publishable under the project's thesis.
   Kill gates: 2-hour pinned-version conversion smoke BEFORE any D-016
   amendment; off-window Q4-Q8 projection within a week of alpha's floor.
3. **Stretch — MoE re-anchored** (the impact-first pick): Qwen3-30B-A3B
   vs its matched-active dense partner Qwen3-4B (already local) — the
   rank-3 campaign the repo's own mechanism sweep recommended, with the
   novel batch-1 bandwidth-sublinearity thesis. Strictly gated behind the
   seven-desk-gate schedule in SYNTHESIS-IMPACT-FIRST; no night until all
   clear. Spec decode gets ONLY its 2-hour daytime pilot (the repo's own
   smoke predicts spec-on never repays energy — the pilot is nearly free
   and decisive); MTP stays closed (dated AXI-SC verdict); split gets
   only the one-evening GPU-cadence probe.

## Riders into the MVP (night-cheap or free; fund by default)

- **Price-of-never-zero subsection** (desk-only): per-cell floors with and
  without the 0.010818 s bound; does any verdict flip. (rev-drift-thermal)
- **Contamination desk-study** over the ~203 in-custody idle captures:
  P(asymmetric burst > 1 J / > 5 J) over real member durations — feeds §10's
  operational-constraints paragraph with a real number. (rev-contamination)
- **20x time-anchor cautionary figure**: 0.081 J vs 1.649 J on identical
  workloads, pre/post D-078 — free, vivid, on-thesis. (rev-open-explore)
- **Refusal census + denominator** (one desk day) — makes §5's refusal-log
  claims quantitative. (rev-refusal)
- **Single-window KV-context-scaling contrast** (128 vs 4096 context at
  fixed decode; ~2.9x floor on 1.5B): THE candidate for the roadmap's "one
  designed extension" slot if Ed funds a fifth night — cures the
  cross-window custody problem, uses length as the lever, serves the
  original KV/attention goal. Decision rides the scheduling ruling.
  (rev-mvp-icpe move 1 + rev-kv-context strengthening)
- **Interior-chunk noise-limited estimand** (desk + reduction design): the
  project's first noise-limited quantity; methodological extension of the
  attribution-limited finding. (rev-long-generation)
- **Negative-label 3080 Ti demonstration** (zero nights): render the
  deliberately incomplete label for an nvidia-smi measurement — the
  sharpest figure for any reporting/limitations discussion.
  (rev-energy-nutrition move 3)

## Dispositions of the remaining directions (one line each; full arguments in reviews/)

KILLED as papers, salvage noted: mvp-icpe-upgrade (WEAK — its C4/C5 fail
doctrine; its KV move adopted above); wall-meter-validation (WEAK —
unidentifiable on a sealed laptop; re-scoped to an AC-boundary transfer
function IF the loan ever lands; never gates a submission); split-inference
(WEAK/KILL — no cross-device fiducial; cadence probe only);
mtp (KILL — runtime closed by dated verdict; dominated by spec decode);
spec-decode (WEAK — pilot only, K-manipulation rescope if it survives);
attention-variants (WEAK — no admitted checkpoint has the toggle;
context-slope study supersedes); floor-methodology-general (WEAK —
resolvability reframe + held-out floor-validation ladder absorbed into
MVP/Window C); batch-concurrency (WEAK/KILL — headline unfalsifiable;
A4 adapter stays queued desk work); param-scaling (WEAK — denominator
artifact ~29% of its trend); cross-runtime (WEAK — artifact-mismatch
identifiability; afternoon pilot only); drift-thermal (WEAK — is the MVP's
own §4; never-zero subsection adopted); tokenizer-honesty (WEAK — Petrov/
Ahia prior art; M1 ranking-flip night deferred; validator = artifact-track
candidate); prefill-scaling (WEAK — anti-conservative floor transport;
self-flooring 1024 endpoint deferred); kv-context (WEAK as 5-night version;
single-window core adopted above); long-generation (WEAK — comparative
floor unconstructible; interior-chunk estimand adopted);
contamination (WEAK — desk-study adopted, window version dead);
refusal-as-result (WEAK — census + plumbing adopted, paper dead);
energy-nutrition-label (WEAK — schema is the MVP's §6; negative-label demo
adopted); open-explore-registry/repo/contrarian/advisor (their unique
survivals: prefix-reuse boundary reframe kept as a cold idea; §6/Window-C
scope ruling surfaced; everything else duplicated the directed pool).

## Night-budget table (honest, cost-corrected)

| Item | Nights | Status |
|---|---|---|
| D-117 alpha/beta/gamma (MVP claims) | 3 | Ed-adopted; blocked on U1-U3 toolchain |
| Window C (MVP §6 characterization) | 1 | ED RULING #1 |
| Optional: KV-context designed extension | 1 | ED RULING (with #1) |
| Optional: 256-tok prefill contrast | 1 | recommend NO for capstone (both syntheses) |
| P2 quantization BF16/Q4/Q8 | 3 | after MVP; kill gates first |
| Stretch MoE | 2-3 | desk gates first; Spring-class |

## Ed's rulings (ranked; both syntheses' merged list)

1. **§6/Window C**: fund night 4, or rewrite abstract+contributions+§6 as
   declared future work. RECOMMEND: fund.
2. **Reported-energy cells in alpha/beta**: pre-register reader-facing
   phase-energy means alongside floor cells (no added members) — must be
   decided BEFORE campaign-pack hashes freeze (time-critical, U5/U6).
   RECOMMEND: yes, pending a no-semantics-change check at the pack gate.
3. **Reason-code plumbing before night one** (member_id→reason_code +
   16 shadow codes under the ratified spec). RECOMMEND: yes (urgent).
4. **256-tok prefill arm**: RECOMMEND no for the capstone; the marginality
   is published as prospective sizing evidence.
5. **P2 commitment**: authorize the shrunk quantization posture
   (BF16/Q4/Q8, no Q5/Q6, no internal quality verdict) conditional on the
   conversion smoke; MoE reserves the stretch slot.
6. **Calendar**: capstone/advisor/venue evidence-by dates — needed to
   convert "Fall/Spring" into last-arm dates (six post-data weeks + one
   rerun slot reserved first).
7. **Public-artifact scope** (what evidence may be archived) and the
   wall-meter/second-unit external-coordination choice (RECOMMEND: second
   Apple unit over WT310E if only one; neither gates anything).

codex
The ranking is converging on a staged decision rather than eight competing full papers: finish the four-night metrology capstone, run the urgent zero-night evidence/plumbing work before alpha, then make a mechanism paper conditional on hard desk gates. The key close call is MoE versus quantization; I’m pricing both at their real floor obligations rather than accepting the reviews’ optimistic “two-night” shorthand.
All 24 reviews and the primary text needed for the close calls are reconciled; synthesis and cost corrections are complete.
  ✓ Read project controls, D-117/design memo, and inventory the 24 proposal/review pairs
  ✓ Read all 24 counter-reviews first and extract verdicts, scores, costs, kill gates, and salvage
  ✓ Read proposals selectively to resolve ranking, sequencing, and cost ambiguities
  ✓ Synthesize ranked portfolio, paper arc, synergy map, second-paper bet, and Ed rulings
2026-08-07T16:55:35.245296Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
codex
# Portfolio decision

Fund a four-night MVP, make the re-anchored MoE study the conditional second paper, keep the three-rung quantization ladder as the automatic fallback, and treat speculative decoding as the high-risk stretch. Do not fund the other proposals as standalone papers.

Three corrections govern the ranking:

- The generic “~5 J” bar is not portable. Any 7B-arm study must plan against the measured diagnostic comparative floor of about **14.0 J**, plus its claim-side interval.
- Longer workloads need their own repeatability/floor evidence; transporting a short-workload floor is anti-conservative.
- The MVP is **four nights**, not three: D-117 alpha, beta, gamma, then a Window-C characterization night unless Ed explicitly descopes §6/C-iv. See [D-117](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/decision_log.md:7508), the [plan-freeze memo](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:242), and the six pending rows in [MVP §6](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/paper/draft-v1.md:141).

The probabilities below are portfolio-planning priors, not statistical estimates.

## Ranked portfolio

### 1. MVP capstone: calibrated resolvability and refusal

The MVP is fixed and remains the highest-value use of every immediate desk hour. Its scientific spine is already distinctive: phase attribution is systematically limited, repetitions do not remove that limit, and the instrument publishes what it cannot resolve. Honest cost is **four nights**—3.14 h alpha, 3.24 h beta, 2.80 h gamma, and one 2–4 h Window-C characterization night—plus roughly **2–4 concentrated desk/review weeks** for the open D-117 machinery and postcollection pin closure. I estimate an **80–90% chance that a defensible paper survives**, but only about **55–65% that every desired claim cell and characterization row passes without a refusal**. That distinction is healthy: valid refusals still support the paper. The MVP-review verdict was WEAK only as an overgrown ICPE upgrade, not as the capstone paper itself.

### 2. Re-anchored MoE routing: Qwen3-30B-A3B, dense partner, and a causal routing-budget leg

This is the **best second-paper bet** under the impact-first prior. The viable version abandons the awkward 65 GB Qwen3.5 VLM hybrid and uses the repo-vetted Qwen3-30B-A3B text MoE with Qwen3-4B as the matched-active dense partner, plus a within-checkpoint top-*k* intervention to distinguish routing-budget effects from cross-model confounding. It directly serves Ed’s original MoE goal and has the best chance of becoming a real mechanism paper rather than another metrology application. Honest cost is **six to seven nights from today**: four MVP nights, at least one independently scoped MoE/dense floor night, one science night, and a third extension night if dense, native-*k*, and forced-*k* floors cannot be packed without weakening the frozen replication standard. Desk cost is approximately **4–6 weeks**. Survival prior: **35–50%**. I agree with the VIABLE verdict but disagree that “two nights” is guaranteed once the dense partner is added.

### 3. Shrunk quantization ladder: BF16/Q4/Q8

This is the safest fallback second paper. Use one frozen Qwen2.5-1.5B source revision, retain D-117’s exact Q4 workload and floor, add only BF16 and Q8, delete Q5/Q6, and make no JouleWise-issued quality-equivalence claim under D-041. The result is a floor-gated resolvability map that also tests whether energy tracks artifact bytes or MLX kernel maturity. Honest cost is **seven nights from today**: four MVP nights, separate BF16 and Q8 floor nights, and a three-arm contrast night; **4–8 desk weeks** for acquisition, conversion provenance, multi-cell minting, estimator work, and artifact release. Survival prior: **65–75%**. The review’s concluding “two extension nights” conflicts with its own plan—two new standard floors plus a contrast are three nights unless Ed prospectively ratifies a packed dual-floor design that still fits the four-hour envelope.

### 4. Held-out floor-validation ladder inside Window C

This is the strongest metrology content but not a separate paper. Use the MVP’s fourth night to place effects prospectively around roughly 0, 0.5F, 1F, 2F, and 4F, with nulls at more than one magnitude and explicit positive/negative directions. It turns “we composed a floor” into “we tested the floor’s operating characteristic.” Cost is **the same four-night MVP total**, not an added fifth night, plus **1–3 desk weeks** to eliminate circular slope-derived ground truth, self-floor the tested magnitudes, and freeze the packing. Survival prior: **70–80%** as useful characterization, lower if Ed insists that every one of §6’s six rows become a separate claim in one window. Its standalone floor-methodology proposal is WEAK; this rider is excellent.

### 5. Self-floored KV/context contrast, 1.5B first

The original context-curve proposal is confounded and under-floored, but the rebuilt version is credible: start with one 1.5B 128-vs-long-context ABBA contrast, lengthen decode to amplify KV traffic, replace dead interior points with long-condition A=A nulls, and include or separately bound prefill-to-decode thermal carryover. Every length must self-floor; no 7B study may use the generic 5 J bar. Cost is **five to six nights from today**—four MVP plus one self-flooring claim window, with a second only if the thermal-matched control cannot fit—and **2–4 desk weeks**. Survival prior: **45–60%**. It has a lower venue ceiling than MoE but directly serves the KV/attention goal and stays within the frozen single-request boundary.

### 6. Interior-chunk decode estimand

The useful paper inside “token 4,000 versus token 400” is methodological: phase-adjacent edges are attribution-limited, but decode chunks bounded entirely inside a homogeneous power regime may be repeatability-limited near ~0.3 J. That would materially refine the MVP’s central result by showing the attribution limit is a boundary property, not a global property of `powermetrics`. The full early-vs-late observational paper remains confounded by elapsed time, temperature, DVFS, and KV growth. Cost is **five to six nights total**, preferably by riding a KV claim window or Window-C characterization rather than buying two independent nights, plus **3–5 desk weeks** for distinct chunk identities, reducer support, floors, and nonblocking extraction. Survival prior: **50–65%** for the estimand result, lower for a standalone paper.

### 7. Speculative decoding, only after the two-hour tok/s gate

This has the highest theoretical venue ceiling but the lowest survival probability. The stock runtime already executes the Qwen2.5 target/draft pair; therefore the first action is not a fork but a **two-hour daytime spec-on/off throughput pilot**. If speculation is slower—as the local DSpark/DFlash evidence suggests—the campaign dies cheaply and the negative answer becomes a short limitation. If it passes, manipulate proposal cap *K* rather than treating observed acceptance as an independent variable; build the missing gross-request floor class; run both arms on the same instrumented runtime; and bound instrumentation overhead. Cost if alive: **six to seven nights total**, **6–12 desk weeks**, and two or three extension nights. Pre-pilot survival prior: **10–25%**; conditional on a clear tok/s win and exact output identity, approximately **40%**. This is a stretch, not the second-paper schedule.

### 8. Tokenizer-honest matched-content ranking flip

The desk-only tokenizer proposal is not a paper, but one added matched-content, non-Latin measurement night could make it one. Compare deployable Qwen and OLMo-family stacks on the same semantic content budgeted by characters/bytes, report gross J/request first, and ask whether J/token reverses the ranking. The effect should be large, but the claim must remain “reporting distortion between as-shipped stacks,” not causal tokenizer attribution, because architecture and precision also differ. Cost is **five nights total**, **1–3 desk weeks**, and one claim window with its own floors. Survival prior: **40–55%** for an actual flip. Venue ceiling is workshop/tool-track rather than ICPE full, but it cleanly serves Ed’s reporting goal.

## Remaining 16 dispositions

- **attention-variant-energy — KILL.** No admitted SWA checkpoint, impossible output-identity gate, and runtime-fork risk; fold its context-slope residue into rank 5.
- **batch-concurrency-energy — KILL as a paper.** Build the already-queued A4 adapter as desk infrastructure; do not spend the four-to-six nights required for batch floors/covariance.
- **contamination-characterization — KILL as a paper.** Run the zero-night asymmetric-burst study over the 203 in-custody idle captures and put the result in the MVP.
- **cross-runtime-contrast — KILL.** Wrong ~5 J sizing, MLX/GGUF byte confound at the only clearable effect size, no llama.cpp adapter, and realistically three new floor/contrast nights.
- **drift-thermal-science — KILL as a paper.** Publish the desk-only “price of never-zero” subsection in the MVP; do not reopen D-117.
- **energy-nutrition-label — KILL as a standalone paper.** Retain the validator/artifact and negative 3080 Ti label demonstration.
- **mtp-energy — KILL.** Native MTP is unavailable at the pinned runtime; retain the dated negative verdict as a speculative-decoding rider.
- **open-explore-advisor — KILL as a portfolio slot.** It duplicates the MVP, Window C, and wall-meter directions; harvest the JouleSort/Mantis citation gap.
- **open-explore-contrarian — KILL.** It restates roadmap ranks rather than changing course; preserve only the §6 scope ruling.
- **open-explore-registry — KILL as an umbrella.** Retain prefix reuse as a later boundary/refusal short study, not a “crossover” paper.
- **open-explore-repo — KILL as an umbrella.** Harvest the 20× time-anchor-defect figure; shelve the expensive Q4 grid.
- **param-scaling-energy — KILL.** Foregone monotonic result, broken denominator, and an irrelevant floor; at most add a later 14B enrichment cell.
- **prefill-scaling-laws — KILL.** Short-to-long floor transport is anti-conservative; the only live choice is D-117’s independently self-floored 256-token arm.
- **refusal-as-result — KILL as a paper.** Make it the MVP evaluation plus an artifact-track companion; fix the evidence schema before alpha.
- **split-inference-metrology — KILL.** Preserve only the one-evening GPU-cadence probe; the full split study is a new instrument and a semester.
- **wall-meter-validation — KILL as a standalone paper.** Keep C8 as a conditional MVP/ICPE subsection after battery, fan, fixture, loan, and identifiability gates pass.

# Recommended paper arc

## August–Fall 2026: MVP capstone

Before alpha, finish the D-117 blockers and the urgent evidence fixes:

1. Two-slot calibration bracket session and exact binding.
2. D-102 live-prefix successor engine.
3. Prefill-capable four-cell pinset/mint.
4. Frozen alpha/beta/gamma packs and regression.
5. **Urgent refusal plumbing:** add `member_id → reason_code` to verdict rows and bring the 16 shadow window-verdict codes under the ratified refusal spec.
6. Freeze the Window-C scope or explicitly descope C-iv.

Then execute:

| Sequence | Night | Budget | Output |
|---:|---|---:|---|
| 1 | Alpha: 1.5B floor + prefill rider | 3.14 h | Two fresh floor cells |
| 2 | Beta: 7B floor + prefill rider | 3.24 h | Two fresh floor cells |
| desk | Four-cell extraction and mint | — | Combined floor artifact |
| 3 | Gamma: 1.5B vs 7B decode | 2.80 h | Main demonstration contrast |
| 4 | Window C | 2–4 h | Characterization, led by null-magnitude and held-out floor validation |

Fall 2026 should be paper, analysis, artifact, and advisor work—not another mechanism campaign. The MVP should absorb the zero-night salvage listed below.

## Winter 2026/27–Spring 2027: MoE second paper

After the MVP’s tables and artifact are locked, spend 4–6 weeks on the MoE gates. If all pass, collect one floor night and one mechanism night; add a third only if that need is determined prospectively by the frozen floor design. Target EuroMLSys or ICPE Emerging first; upgrade venue ambition only if the dense comparison, routing intervention, and replay artifact all land.

If MoE fails a desk gate, switch immediately to BF16/Q4/Q8 quantization. Do not attempt to “repair” the MoE paper with a cross-model descriptive table.

## Spring–Summer 2027: stretch

Run the speculative-decoding two-hour timing pilot early, but fund no runtime fork until the pilot shows a real throughput win and exact identity. If it clears, the stretch is the *K*-sweep “does it ever repay?” paper. If it does not, close the axis with the negative pilot and stop.

# Salvage placement and synergy map

| Salvage item | Home | Marginal cost / shared work |
|---|---|---|
| Held-out floor-validation ladder | MVP Window C | Uses the fourth MVP night and D-117 mint/custody stack |
| “Price of never-zero” arithmetic | MVP §4/§7 | Desk-only reduction of the four minted cells |
| 203-capture asymmetric-burst contamination study | MVP admission/evaluation section | Zero nights; D-117 creates the corpus |
| 20× time-anchor-defect cautionary figure | MVP motivation/limitations | Zero nights; existing defective and corrected corpora |
| Refusal-mechanism census | MVP evaluation + artifact | One desk day; establishes the honest denominator |
| Refusal `member_id→reason_code` and 16-code spec repair | All future papers | Must land before alpha; prevents irreversible prose-only evidence |
| Interior-chunk noise-limited estimand | Window C or KV paper | Reuses traces; keep extraction nonblocking to the floor mint |
| Single-window KV ABBA contrast | KV follow-on | Reuses 1.5B model/workload and D-117 campaign templates, but needs its own long-workload floor |
| Two-hour spec-decode tok/s pilot | Stretch gate | Uses existing target/draft artifacts; no claim window |
| MTP unreachable verdict | Spec-decode limitations | Desk-only; no separate paper |
| Negative 3080 Ti energy-label example | MVP artifact/reporting appendix | Zero claim nights; demonstrates an honest refusal across boundaries |
| Matched-content non-Latin ranking flip | Tokenizer short paper | One independent claim night; reporting validator is shared |
| Prefix-reuse boundary/refusal reframe | Later KV/cache short paper | Reuses the existing replay spike; requires its own floors and explicit off-SoC SSD boundary |
| A4 static-batch adapter | Infrastructure only | Cheap queued desk work; later supports batch/spec/MoE work |
| GPU-cadence probe | Split future-work section | One non-quiet evening; determines whether split metrology is even sizeable |

The largest genuine cost sharing is:

- D-117’s ledger, successor, pinset-v2, custody, and readiness work benefits every later paper.
- Quantization uniquely reuses the exact D-117 Q4 floor and workload.
- MoE and quantization share multi-cell mint, multi-arm analysis, artifact hashing, and divergence-report machinery—but **not floors**.
- Window C supplies the floor-validation result, magnitude-null evidence, and traces for the interior-chunk analysis.
- Refusal plumbing benefits every future claim window and has to precede them.
- No floor should be declared shared merely because a model, runtime, or phase name looks similar.

# Single best second-paper bet: MoE

Choose the re-anchored MoE paper because it has the highest publishable upside if its kill gates clear: it answers an original mechanism question, offers a causal within-checkpoint leg, and can explain why batch-1 unified-memory MoE behaves differently from active-parameter intuition and server-GPU results.

Honest cost: **4–6 desk weeks, two extension nights minimum, three if independently scoped dense/native/forced floors cannot be packed**, no wall meter. Total from today: **six to seven nights including MVP Window C**.

Kill-gate schedule:

1. **Pair ruling, before engineering:** Ed/advisor ratify Qwen3-30B-A3B and Qwen3-4B, exact artifact revisions, and the claim ceiling.
2. **Capability week:** acquire/hash/load both; prove memory headroom, fixed output policy, tokenizer/workload validity, and a four-hour campaign envelope.
3. **Observability week:** capture actual expert IDs and weights; require 100% realized-*k* reconciliation, buffered evidence, and instrumentation overhead ≤2%.
4. **Estimand week:** run teacher-forced and free-running desk comparisons; require routing-locality, unique-expert, reuse, and entropy reports so text divergence cannot masquerade as an expert-budget effect.
5. **Sizing gate:** project the floor from the relevant member magnitude and require the conservative effect lower bound to exceed **3× the projected operative floor**. The proposal’s fixed 15 J gate is rejected.
6. **Floor-packing gate:** prove that every claim arm has an independently governed floor and that the frozen schedule fits under four hours with 20% margin. If not, budget the third night before collection or kill.
7. **Only then collect.**

# Open questions for Ed, ranked

1. **§6 / Window C:** Fund night 4, or formally declare C-iv future work and rewrite the abstract, contribution list, §6, and claims. Recommendation: fund one carefully packed characterization night; do not leave six `[PENDING]` rows in a “complete” paper.
2. **256-token prefill arm:** Is a directional prefill contrast required beyond the already-funded prefill floors? Recommendation: no in the base MVP. If yes, freeze it as an independent, self-floored fifth claim window; the 128-token riders do not transport.
3. **Urgent refusal evidence fix:** Authorize the minimal `member_id→reason_code` verdict plumbing and the 16-code spec reconciliation before alpha. Recommendation: yes; this is operationally urgent regardless of publication plans.
4. **Second-paper commitment:** Will Ed reserve two to three Spring 2027 nights for the re-anchored MoE study if every desk gate passes? If not, select BF16/Q4/Q8 now as the lower-risk fallback.
5. **D-117 reported-energy cells:** Should alpha/beta prospectively register reader-facing phase-energy means in addition to floor cells? This adds no members but must be decided before campaign-pack hashes freeze.
6. **Calibration retry semantics:** Keep zero retries, or prospectively number cause-removal retry slots in the bracket-session state machine? Recommendation: zero for the base plans.
7. **Wall-meter cutoff:** Set a date by which a calibrated WT310E loan, safe fixture, battery-flux bound, and fan control must exist; otherwise C8 remains future work and cannot block a submission.
8. **3080 Ti access status:** Resolve owned-versus-borrowed status before presenting GPU portability or split work as scheduled research. The cadence probe can proceed only when access is real.

The portfolio’s central lesson is unusually clear: Ed does not have 24 papers. He has one strong metrology paper, two credible second-paper bets, one high-upside stretch, and a rich set of cheap riders that make the first paper substantially better.
tokens used
235,848
# Portfolio decision


exec
/bin/zsh -lc "nl -ba docs/strategy/2026-08-07-paper-portfolio/reviews/rev-moe-routing-energy.md | sed -n '1,380p'; nl -ba docs/strategy/2026-08-07-paper-portfolio/ADJUDICATION.md | sed -n '1,135p'; nl -ba docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md | sed -n '11215,11245p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
     1	# Counter-review — `prop-moe-routing-energy.md`
     2	
     3	**Reviewer:** Opus 5, adversarial counter-review. Ground truth: desk checkout at `89f28bf`
     4	(main), D-117 + design memo, `CLAIMS_STATUS.md`, `docs/research_question_registry.md`,
     5	`docs/run_reports/2026-07-30-sweep-mechanisms.md`,
     6	`docs/run_reports/2026-07-07-flagship-qwen35-122b.md`,
     7	`docs/run_reports/2026-07-29-modularity-survey.md`, and **direct inspection of the installed
     8	runtime** at `/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/` plus the
     9	local artifact config at `/Users/edr/jw_models/mlx-community/Qwen3.5-122B-A10B-4bit/`.
    10	
    11	**VERDICT: VIABLE** (with two blockers that must be closed before any night is committed)
    12	
    13	| axis | score |
    14	|---|---|
    15	| novelty | 6 / 10 |
    16	| feasibility | 4 / 10 |
    17	| mvp_leverage | 5 / 10 |
    18	| venue_fit | 6 / 10 |
    19	| original_goals | 8 / 10 |
    20	
    21	This is the better of the two proposals I was assigned, and it survives a serious attempt to
    22	kill it. It does not survive intact.
    23	
    24	---
    25	
    26	## The existing-material question, answered from the runtime source
    27	
    28	The charge asked whether a Qwen MoE variant exists on MLX at a servable size with per-token
    29	expert-activation observability. I checked the installed code rather than the model card.
    30	
    31	**Artifact: EXISTS, pinned, already exercised.** `Qwen3.5-122B-A10B-4bit` is present at
    32	`/Users/edr/jw_models/mlx-community/`, and `docs/run_reports/2026-07-07-flagship-qwen35-122b.md`
    33	records 3/3 reps `validate-bundle --strict` green, rev `e9c67b0`, 65 GB on disk, 68.9 GB peak,
    34	46 tok/s decode, 12.8 s warm load, gross CV **0.3 %** across reps (the tightest in the corpus).
    35	The ~304 J / 512-token diagnostic the proposal cites is real (303.5 / 303.5 / 305.1 J) and is
    36	correctly labelled as planning-only. The claim is not invented.
    37	
    38	**Architecture: the proposal's numbers are exactly right.** From the local `config.json`
    39	(`text_config`): `num_hidden_layers=48`, `num_experts=256`, `num_experts_per_tok=8`,
    40	`hidden_size=3072`, `moe_intermediate_size=1024`, `shared_expert_intermediate_size=1024`,
    41	`decoder_sparse_step=1`. So all 48 layers are MoE, giving 48 × 8 = **384** routed
    42	expert-layer activations and 48 shared activations per token — as stated. Per routed expert:
    43	3 × 3072 × 1024 = 9.44 M params; × 8 × 48 = **3.624 B** routed-active. Halving k removes
    44	**1.812 B**. The proposal's "about 1.81B, roughly 18 % of the advertised 10B active" is
    45	arithmetically exact. Credit.
    46	
    47	**Runtime: the knob is real and the observability gap is real.** `qwen3_5_moe.py` subclasses
    48	`qwen3_5.py`, which imports `Qwen3NextSparseMoeBlock as SparseMoeBlock` from `qwen3_next.py`
    49	— so the proposal's citation of `qwen3_next.py` is **correct**, not the mismatch it looks
    50	like. I had that queued as a hit and withdrew it. The block reads:
    51	
    52	```python
    53	gates = mx.softmax(self.gate(x), axis=-1, precise=True)
    54	k = self.top_k                                    # = args.num_experts_per_tok
    55	inds = mx.argpartition(gates, kth=-k, axis=-1)[..., -k:]
    56	scores = mx.take_along_axis(gates, inds, axis=-1)
    57	if self.norm_topk_prob:
    58	    scores = scores / scores.sum(axis=-1, keepdims=True)
    59	y = self.switch_mlp(x, inds)
    60	```
    61	
    62	Three consequences, two favourable:
    63	
    64	1. **`routing_top_k_override` is a one-line config change** (`num_experts_per_tok`). No source
    65	   patch needed for the *intervention*. Feasible as claimed.
    66	2. **`norm_topk_prob` defaults to `True`** (`qwen3_5.py:51`, and the artifact does not
    67	   override it). So forcing k=4 **renormalizes the gate mass** and preserves output scale.
    68	   This is important and the proposal does not know it: the obvious "k=4 produces scaled-down
    69	   garbage" failure mode is structurally excluded. The quality risk is real but it is
    70	   distribution shift, not numerical collapse.
    71	3. **`inds` is a live intermediate, never returned.** Per-token expert IDs require a source
    72	   patch to `Qwen3NextSparseMoeBlock`. The proposal's "current MLX code calculates those
    73	   indices internally but does not expose them as evidence" is exactly right.
    74	
    75	So the existing-material constraint is **satisfied** — better than for most of this portfolio.
    76	The problems are elsewhere.
    77	
    78	---
    79	
    80	## BLOCKER 1 — The contrast has no floor for arm B
    81	
    82	The proposal budgets "one exact-stack floor window" using "the proven 10-absolute plus 40
    83	A=A null design". That produces **one** floor cell, for the native k=8 configuration.
    84	
    85	But the k=4 arm is a *different config hash* → a different condition family → a different
    86	stack identity under this repo's own rules. D-117 gamma's floor rule is
    87	`cross_stack_armwise_max.v1`: "independently resolve the 1.5B and 7B decode cells and take
    88	their maximum, never their sum." Both arms need independently resolved floors. The design
    89	memo is emphatic about the general principle — *"never borrow a decode floor for prefill"*,
    90	and prefill riders "do not automatically transport" to a differently-parameterised workload
    91	without "either exact matching prefill floor cells or a separately predeclared and justified
    92	transport rule."
    93	
    94	A k=8 floor is precisely a borrowed floor for the k=4 arm. As designed, the contrast cannot
    95	be governed. The fix is cheap if made now and expensive if discovered at the arm gate: split
    96	the null half into 20 members at k=8 and 20 at k=4 (or run 10-absolute + 20 + 20 in one
    97	window), or pre-register an explicit transport ruling with justification. Either way the
    98	proposal's window count and member schedule change, and its "5 nights, 14–16 h" figure is
    99	understated.
   100	
   101	## BLOCKER 2 — The effect/floor ratio is asserted against the wrong denominator, and the kill gate is set below the largest measured floor
   102	
   103	> "use **40–120 J/request** as the uncertain planning range. Even its low end is about 8× the
   104	> 5 J bar."
   105	>
   106	> Kill if "a pessimistic desk timing proxy … projects under **15 J**".
   107	
   108	Two problems.
   109	
   110	**(a) The "5 J bar" is a document-level prose constant; the measured floors are 2–3× larger.**
   111	`CLAIMS_STATUS.md` line 55 gives "floor + claim-side bound ≈ 5 J", but eight lines below it
   112	records the only actually-minted comparative floor: **13.998036715259254 J** for the 7B decode
   113	cell, on an absolute-cell member mean of **192.386233 J** — i.e. the comparative floor is
   114	**7.3 % of member energy**, and the absolute component (6.294380 J) is 3.3 %. On this
   115	instrument, floors have empirically scaled with member energy, not sat at an absolute ~1 J.
   116	(The ~1 J attribution limit is one *component*; at 7B it is not the binding one.)
   117	
   118	A 122B member at 1024 output tokens is **~597 J** (583 mJ/output-token measured × 1024 —
   119	note this, not "roughly 110 J at 1,024 tokens", is the request energy; see the prose defect
   120	below). Scaling the one measured precedent forward, a projected comparative floor of
   121	**~44 J** is the honest central estimate, with a plausible range of ~25–90 J.
   122	
   123	Against that, the proposal's own 110 J central effect is **~2.5×** the floor, not 8×; its
   124	40 J low end is **below** it. The proposal is not obviously wrong — the flagship report's
   125	0.3 % gross CV suggests this stack may be unusually repeatable, and an attribution-dominated
   126	floor of ~5–10 J is genuinely possible — but it asserts the optimistic branch without
   127	engaging the one measured precedent that contradicts it. The honest statement is:
   128	*effect/floor is somewhere between ~1.2× and ~20× and the floor window is the experiment that
   129	decides it.*
   130	
   131	**(b) The 15 J desk kill gate is below the largest already-measured floor (13.998 J).** A gate
   132	set at 1.07× the biggest floor this project has ever minted cannot fail for any reason that
   133	matters. It must be expressed as a multiple of the *projected floor for this cell* — I would
   134	demand ≥3× — not as a fixed joule literal inherited from a different model's regime.
   135	
   136	**(c) The physics may cut against the proposal.** Decode here is bandwidth-bound. Per-token
   137	weight traffic ≈ routed 3.62 B + shared 0.45 B + LM head 0.76 B (`tie_word_embeddings: false`,
   138	vocab **248320** × 3072) + attention ≈ 6.3 B params at ~4.25 effective bits (group_size 64,
   139	affine) ≈ **3.35 GB/token**. At the measured 46 tok/s that is **~154 GB/s** — roughly 40 % of
   140	the M3 Max's ~400 GB/s, whereas dense Qwen2.5-7B (0.376 J/tok at ~28–36 W → ~93 tok/s ×
   141	4.2 GB) runs at **~390 GB/s**, essentially at peak.
   142	
   143	That gap is the real story: **batch-1 MoE on unified memory achieves ~40 % of the bandwidth
   144	efficiency of dense inference**, because gathering 8 of 256 experts per layer is
   145	dispatch-bound, not traffic-bound. Which means the k=8→k=4 saving will be **sublinear** in
   146	removed parameters: the gather/dispatch cost per layer is roughly fixed, so halving k halves
   147	the bytes but not the overhead. The proposal's proportional 18 % assumption is an upper
   148	bound on the mechanism it is measuring. (Conversely, counting only per-token *read* traffic
   149	rather than the advertised 10 B active gives 1.81/6.3 = 29 %, an upper-upper bound. The
   150	truth is bracketed by dispatch overhead and nobody knows where.) This is simultaneously the
   151	proposal's biggest risk and its most interesting potential finding — and it is unstated.
   152	
   153	---
   154	
   155	## FLAW 3 — The confound between expert budget and sequence content is treated as a quality question when it is an estimand question
   156	
   157	The proposal correctly rejects cross-model MoE comparisons as confounded and correctly picks
   158	a same-checkpoint intervention. But it then declares:
   159	
   160	> "Native k=8 and forced k=4 differ **only** in routed-expert budget on one
   161	> artifact/runtime/boundary."
   162	
   163	That is false past token 1. Forcing k=4 changes the logits, which changes the greedy argmax,
   164	which changes the emitted token, which changes the next hidden state, which changes **which
   165	experts route** and **what the KV cache contains**. By token ~50 the two arms are generating
   166	different text. With `max_tokens` pinned at exactly 1024 the *count* matches, but the two arms
   167	are no longer "the same work minus four experts" — they are **1024 tokens of text X versus
   168	1024 tokens of text Y**, and if arm B degenerates into a repetition loop (a classic
   169	reduced-top-k failure) then Y has systematically different routing entropy, expert-reuse
   170	locality, and cache behaviour. Repetition loops concentrate routing on few experts, which
   171	*improves* gather locality and would **inflate** the measured energy saving beyond the
   172	mechanism.
   173	
   174	The repo already owns this gate: `C-023-OUTPUT-IDENTITY` — *"Fixed output-token count is not
   175	fixed decoded work"* — is a registry row, and it is `status: candidate (C-023)` with
   176	`AP owner: none-yet`. The machinery is **not built**. The proposal's response (an
   177	"exact-output divergence report", and a quality gate that "kills 'quality-equivalent' wording
   178	but may retain a trade-off paper") mis-frames it: divergence is not a caveat on the *wording*,
   179	it is a bias on the *estimand*. The minimum honest addition is a **routing-locality
   180	companion** — unique experts touched per layer, expert-reuse rate, and routing entropy per
   181	arm — so that a divergence-driven locality shift can be distinguished from the budget effect
   182	it is being credited to. The proposal already plans "expert-load/unique-expert summaries";
   183	it just does not connect them to this confound.
   184	
   185	The teacher-forced variant (replay arm A's exact token IDs through arm B's k=4 routing) would
   186	eliminate the confound entirely at the cost of measuring a counterfactual rather than a
   187	deployment. Worth at least a paragraph of adjudication; the proposal gives none.
   188	
   189	---
   190	
   191	## FLAW 4 — Instrumentation overhead is the most likely killer, and MLX's execution model makes it worse than budgeted
   192	
   193	The proposal's ≤2 % decode-time overhead gate is right in spirit but underestimates the
   194	mechanism. MLX is lazy and asynchronous. Exporting `inds` per layer per token requires
   195	keeping 48 live arrays alive across the decode step, which prevents buffer donation and
   196	kernel fusion around the MoE block, and any host readback forces a graph sync **48 × 1024
   197	times per member**. The proposal's mitigation ("buffered routing evidence must be flushed
   198	outside the measured decode interval") is the correct instinct and probably necessary, but
   199	on-device buffering still materialises 48 × 1024 × 8 index arrays per member and still adds a
   200	graph node per layer.
   201	
   202	This is a desk-testable question and the proposal treats it as one — good. But note what a
   203	failure means: an instrumentation-on run is a **different stack identity** from an
   204	instrumentation-off run, so a patched `mlx_lm` cannot silently inherit D-117's runtime
   205	identity. The instrumentation-on/off ABBA equivalence test the proposal names is exactly
   206	`C-023-TELEMETRY-PERTURBATION` from the registry (`status: candidate (C-023)`, `AP owner:
   207	none-yet`) — another unbuilt dependency it inherits without acknowledging.
   208	
   209	## FLAW 5 — Undeclared properties of the chosen artifact
   210	
   211	The proposal describes the target as "the already exercised, pinned `Qwen3.5-122B-A10B-4bit`
   212	MLX artifact" and cites the *text* model card. The local artifact is not quite that:
   213	
   214	- **It is a vision-language checkpoint.** Root config carries `vision_config`,
   215	  `image_token_id: 248056`, `video_token_id`, `vision_start/end_token_id`, and
   216	  `qwen3_5_moe.py`'s `sanitize()` explicitly **discards** every `vision_tower` / `model.visual`
   217	  weight at load. So part of the 65 GB on disk is read and thrown away, which is why peak
   218	  memory hit 68.9 GB. Model identity, artifact SHA, and the discarded-weight behaviour all
   219	  need to be in the stack-identity table; citing the text model card's parameter counts for a
   220	  VLM artifact is an identity mismatch a referee will catch.
   221	- **It is a hybrid, not a transformer.** `full_attention_interval: 4` and
   222	  `from .gated_delta import gated_delta_update` — 36 of 48 layers are GatedDeltaNet linear
   223	  attention, 12 are full attention. The paper would place a hybrid-linear-attention MoE
   224	  alongside D-117's dense Qwen2.5 transformers without saying so.
   225	- **It is a reasoning model with a different tokenizer.** `vocab_size` **248320** vs Qwen2.5's
   226	  151936/152064. Within the two MoE arms this is fine (same tokenizer, so the mJ/output-token
   227	  companion is well-scoped). But the paper juxtaposes MoE results with D-117's Qwen2.5
   228	  results, and `docs/contracts/token_normalization.md` forbids cross-tokenizer/cross-family
   229	  per-token comparison without a J/char or J/byte companion or purely descriptive language.
   230	  Unaddressed.
   231	- **The quality screen the proposal promises has no harness support.**
   232	  `docs/run_reports/2026-07-29-modularity-survey.md` records that model family is "MODULAR by
   233	  omission" — qwen3.5-122b ran the identical path — but also that **"no chat-template/
   234	  thinking-mode/multimodal seam exists at all … a chat/thinking model needs a new
   235	  prompt-rendering seam."** Contribution 4 (a "frozen quality screen" with an overall pass
   236	  rate and per-stratum breakdown) requires chat templating and task scoring on a *reasoning*
   237	  model, and neither exists. This is a substantially larger build than the routing sidecar and
   238	  the proposal budgets it as an afterthought.
   239	
   240	---
   241	
   242	## Novelty, honestly
   243	
   244	The proposal oversells its position relative to the repo's own prior art.
   245	
   246	`docs/run_reports/2026-07-30-sweep-mechanisms.md` already contains this idea, ranked and
   247	costed. Its pairs table lists **"MoE top-k knob | Qwen3-30B-A3B, `num_experts_per_tok=8` |
   248	same checkpoint, k=4 (config edit) | same weights | *Unverified but mechanically plausible* —
   249	single-mechanism, same-weights knob"**, and its claims ranking puts "MoE top-k slope (same
   250	weights)" at **rank 6 of 6** with "expert-FFN energy ~∝ k; maybe 20–40 % of J/tok". The
   251	top-3 recommended first campaigns are spec decode, the quant ladder, and **MoE-vs-dense
   252	matched-active** — not the top-k knob. So the proposal re-derives a repo-registered idea,
   253	picks a *worse* artifact than the one already vetted for it, and does not engage the
   254	adjudication that ranked it last.
   255	
   256	The literature position is also weaker than claimed. arXiv 2606.21428 (the one Apple-silicon
   257	MoE paper) already reports that **"routing itself is <9 % of MoE-block compute — the penalty
   258	is total-parameter footprint, dispatch, KV pressure."** A paper titled *"What Does a Routed
   259	Expert Cost?"* whose intervention is expert *budget* (not routing overhead) will be read as
   260	answering the question 2606.21428 already answered, unless the framing shifts to what is
   261	genuinely open: **the dispatch-bound sublinearity above**, and the matched-active-vs-matched-total
   262	sign flip between arXiv 2504.17674 (+54 % vs dense, A100) and arXiv 2601.22076 (3.56× *less*,
   263	H100/B200 batched) — which the sweep calls "a point of genuine confusion the literature hasn't
   264	resolved cleanly." That is the paper. The k-knob is the *instrument* for it, not the thesis.
   265	
   266	Governance, unmentioned: there is **no registry row for MoE routing energy**. The nearest is
   267	`C5-1.9` ("MoE-vs-dense controlled ladder", `status: banked`, L2 after envelope and
   268	denominator guards). Promotion requires a named RQ slot in `PROJECT_STATUS.md` and a data
   269	plan that does not displace higher queue ranks. Also note `TASK_QUEUE.md` A7 (AXI-SE) already
   270	fences this: **"routing-mechanism claims allowed only when auditable expert evidence exists"**
   271	and requires AP-MOE-BATCH / the AP-5 MoE rider to be finalized *against P2-015 floors* — both
   272	still `READY`, i.e. unbuilt.
   273	
   274	## Prose defect worth fixing before anyone reads it twice
   275	
   276	> "A permanently voided … diagnostic observed approximately 304 J for a 512-output-token
   277	> request … Crude proportional scaling therefore suggests roughly **110 J at 1,024 tokens**;
   278	> use 40–120 J/request as the uncertain planning range."
   279	
   280	304 J at 512 tokens scales to **~608 J** at 1024 tokens (and the measured 583 mJ/output-token
   281	gives ~597 J). The 110 J is 18 % of 608 — i.e. the **effect**, not the request energy — and
   282	"40–120 J/**request**" mislabels the effect range as a request quantity. The arithmetic
   283	underneath is right; the sentence says something false. In a metrology paper that is not a
   284	typo, it is a credibility event.
   285	
   286	---
   287	
   288	## Three strengthening moves
   289	
   290	1. **Swap the artifact to `Qwen3-30B-A3B-4bit` (~17 GB) and drop the 122B.** The repo's own
   291	   sweep already verified this checkpoint exists and named it the MoE arm; it is a pure text
   292	   MoE with no vision tower to load-and-discard, no 65 GB residency squeezing the page cache
   293	   during a quiet window, no reasoning/thinking-mode seam gap, and a member energy small
   294	   enough that the projected floor is a smaller fraction of a smaller number. Critically, it
   295	   makes the **matched-active dense comparison possible in the same paper** — `Qwen3-4B-4bit`
   296	   is *already present locally* — so one artifact swap converts a rank-6 knob study into the
   297	   rank-3 campaign the sweep actually recommended, with the k-knob as the causal
   298	   within-checkpoint leg that no prior work has. Keep the 122B as a single scale-context
   299	   diagnostic, not as the claim vehicle.
   300	
   301	2. **Fix the floor design and re-anchor every sizing number to a projected floor.** Produce
   302	   **two** floor cells in the floor window (10 absolute + 20 null at k=8 + 20 null at k=4, or
   303	   a second window), so `cross_stack_armwise_max.v1` has both arms. Replace the 15 J desk kill
   304	   gate with **≥3× the projected floor for this cell**, where the projection is scaled from
   305	   the one measured precedent (7B comparative floor = 7.3 % of member mean) and stated as a
   306	   range. Publish the projection and its precedent in the paper — "we predicted our own floor
   307	   from a prior cell and here is how the live mint compared" is a genuine methodological
   308	   contribution that costs nothing.
   309	
   310	3. **Promote routing locality from a summary statistic to a co-primary endpoint, and add a
   311	   teacher-forced arm to the desk gate.** Report unique experts per layer, expert-reuse rate,
   312	   and routing entropy per arm alongside joules; this is what separates "removing 4 experts
   313	   costs N joules" from "the divergent text arm B generated happened to route more locally."
   314	   Then reframe the thesis around the finding the physics actually predicts and nobody has
   315	   measured: **batch-1 MoE decode on unified memory realises only ~40 % of the bandwidth
   316	   efficiency of dense inference, so expert-budget savings are sublinear in removed
   317	   parameters.** That claim is floor-gated, mechanism-level, contradicts the naive
   318	   active-parameter model, speaks directly to the matched-active-vs-matched-total sign flip
   319	   the literature has not resolved, and is exactly the kind of result that lifts this from a
   320	   capstone chapter to an ICPE Emerging or EuroMLSys submission.
   321	
   322	---
   323	
   324	## Bottom line
   325	
   326	The feasibility spine is sound and I verified it in source: the artifact exists and is pinned,
   327	the k-knob is a config field, `norm_topk_prob=True` protects output scale, the effect is
   328	plausibly large, the single-request boundary holds, and no borrowed apparatus is needed. This
   329	serves Ed's highest-priority original axis (MoE mechanism) better than anything else in this
   330	portfolio slice, and it reuses §§3–5 of the MVP draft essentially intact.
   331	
   332	But the contrast currently has no floor for one of its two arms; the effect/floor ratio is
   333	quoted against a prose constant rather than the one measured precedent, which cuts it from 8×
   334	to plausibly ~2.5×; the kill gate is set below the largest floor ever minted here; the
   335	output-divergence confound is filed as a wording risk when it is an estimand bias; and the
   336	chosen artifact is a 65 GB vision-language hybrid reasoning checkpoint when a 17 GB text MoE
   337	with a matched-active dense partner is sitting one download away and was already vetted by
   338	the repo's own sweep. Fix the artifact, fix the floor, re-anchor the sizing — then it is worth
   339	two nights.
     1	# Paper portfolio — magistrate adjudication (2026-08-07)
     2	
     3	**Process:** 24 paper directions (20 directed + 4 open-ended) each developed
     4	by a Sol high/fast session with full repo context (BRIEF.md), each
     5	adversarially counter-reviewed by an Opus 5 referee (reviews/), then two
     6	opposing-prior Sol xhigh syntheses (SYNTHESIS-*.md). This file is the
     7	magistrate's binding synthesis of the syntheses. Ed's rulings section at
     8	the end supersedes anything here once he answers.
     9	
    10	## The adopted arc
    11	
    12	1. **P1 — the MVP capstone paper (in flight, draft COMPLETE on main as of
    13	   PR #110).** Data: the three D-117 windows **plus Window C as night 4**
    14	   (both syntheses' top recommendation — §6's six characterization rows
    15	   are the paper's own contribution 4 and currently have no scheduled
    16	   evidence; shipping them empty or descoping is Ed's ruling #1).
    17	2. **P2 — second paper: QUANTIZATION, shrunk to BF16/Q4/Q8** (the
    18	   pragmatics-first pick; referee verdict VIABLE — the only unconditional
    19	   one in the corpus). Three extension nights + 4-8 desk weeks; consumes
    20	   the D-117 Q4 floors DIRECTLY as a rung; BF16-Q4 anchors (guaranteed
    21	   resolvable), Q4-Q8 adjudicates a real open question; an honest refusal
    22	   on adjacent rungs is itself publishable under the project's thesis.
    23	   Kill gates: 2-hour pinned-version conversion smoke BEFORE any D-016
    24	   amendment; off-window Q4-Q8 projection within a week of alpha's floor.
    25	3. **Stretch — MoE re-anchored** (the impact-first pick): Qwen3-30B-A3B
    26	   vs its matched-active dense partner Qwen3-4B (already local) — the
    27	   rank-3 campaign the repo's own mechanism sweep recommended, with the
    28	   novel batch-1 bandwidth-sublinearity thesis. Strictly gated behind the
    29	   seven-desk-gate schedule in SYNTHESIS-IMPACT-FIRST; no night until all
    30	   clear. Spec decode gets ONLY its 2-hour daytime pilot (the repo's own
    31	   smoke predicts spec-on never repays energy — the pilot is nearly free
    32	   and decisive); MTP stays closed (dated AXI-SC verdict); split gets
    33	   only the one-evening GPU-cadence probe.
    34	
    35	## Riders into the MVP (night-cheap or free; fund by default)
    36	
    37	- **Price-of-never-zero subsection** (desk-only): per-cell floors with and
    38	  without the 0.010818 s bound; does any verdict flip. (rev-drift-thermal)
    39	- **Contamination desk-study** over the ~203 in-custody idle captures:
    40	  P(asymmetric burst > 1 J / > 5 J) over real member durations — feeds §10's
    41	  operational-constraints paragraph with a real number. (rev-contamination)
    42	- **20x time-anchor cautionary figure**: 0.081 J vs 1.649 J on identical
    43	  workloads, pre/post D-078 — free, vivid, on-thesis. (rev-open-explore)
    44	- **Refusal census + denominator** (one desk day) — makes §5's refusal-log
    45	  claims quantitative. (rev-refusal)
    46	- **Single-window KV-context-scaling contrast** (128 vs 4096 context at
    47	  fixed decode; ~2.9x floor on 1.5B): THE candidate for the roadmap's "one
    48	  designed extension" slot if Ed funds a fifth night — cures the
    49	  cross-window custody problem, uses length as the lever, serves the
    50	  original KV/attention goal. Decision rides the scheduling ruling.
    51	  (rev-mvp-icpe move 1 + rev-kv-context strengthening)
    52	- **Interior-chunk noise-limited estimand** (desk + reduction design): the
    53	  project's first noise-limited quantity; methodological extension of the
    54	  attribution-limited finding. (rev-long-generation)
    55	- **Negative-label 3080 Ti demonstration** (zero nights): render the
    56	  deliberately incomplete label for an nvidia-smi measurement — the
    57	  sharpest figure for any reporting/limitations discussion.
    58	  (rev-energy-nutrition move 3)
    59	
    60	## Dispositions of the remaining directions (one line each; full arguments in reviews/)
    61	
    62	KILLED as papers, salvage noted: mvp-icpe-upgrade (WEAK — its C4/C5 fail
    63	doctrine; its KV move adopted above); wall-meter-validation (WEAK —
    64	unidentifiable on a sealed laptop; re-scoped to an AC-boundary transfer
    65	function IF the loan ever lands; never gates a submission); split-inference
    66	(WEAK/KILL — no cross-device fiducial; cadence probe only);
    67	mtp (KILL — runtime closed by dated verdict; dominated by spec decode);
    68	spec-decode (WEAK — pilot only, K-manipulation rescope if it survives);
    69	attention-variants (WEAK — no admitted checkpoint has the toggle;
    70	context-slope study supersedes); floor-methodology-general (WEAK —
    71	resolvability reframe + held-out floor-validation ladder absorbed into
    72	MVP/Window C); batch-concurrency (WEAK/KILL — headline unfalsifiable;
    73	A4 adapter stays queued desk work); param-scaling (WEAK — denominator
    74	artifact ~29% of its trend); cross-runtime (WEAK — artifact-mismatch
    75	identifiability; afternoon pilot only); drift-thermal (WEAK — is the MVP's
    76	own §4; never-zero subsection adopted); tokenizer-honesty (WEAK — Petrov/
    77	Ahia prior art; M1 ranking-flip night deferred; validator = artifact-track
    78	candidate); prefill-scaling (WEAK — anti-conservative floor transport;
    79	self-flooring 1024 endpoint deferred); kv-context (WEAK as 5-night version;
    80	single-window core adopted above); long-generation (WEAK — comparative
    81	floor unconstructible; interior-chunk estimand adopted);
    82	contamination (WEAK — desk-study adopted, window version dead);
    83	refusal-as-result (WEAK — census + plumbing adopted, paper dead);
    84	energy-nutrition-label (WEAK — schema is the MVP's §6; negative-label demo
    85	adopted); open-explore-registry/repo/contrarian/advisor (their unique
    86	survivals: prefix-reuse boundary reframe kept as a cold idea; §6/Window-C
    87	scope ruling surfaced; everything else duplicated the directed pool).
    88	
    89	## Night-budget table (honest, cost-corrected)
    90	
    91	| Item | Nights | Status |
    92	|---|---|---|
    93	| D-117 alpha/beta/gamma (MVP claims) | 3 | Ed-adopted; blocked on U1-U3 toolchain |
    94	| Window C (MVP §6 characterization) | 1 | ED RULING #1 |
    95	| Optional: KV-context designed extension | 1 | ED RULING (with #1) |
    96	| Optional: 256-tok prefill contrast | 1 | recommend NO for capstone (both syntheses) |
    97	| P2 quantization BF16/Q4/Q8 | 3 | after MVP; kill gates first |
    98	| Stretch MoE | 2-3 | desk gates first; Spring-class |
    99	
   100	## Ed's rulings (ranked; both syntheses' merged list)
   101	
   102	1. **§6/Window C**: fund night 4, or rewrite abstract+contributions+§6 as
   103	   declared future work. RECOMMEND: fund.
   104	2. **Reported-energy cells in alpha/beta**: pre-register reader-facing
   105	   phase-energy means alongside floor cells (no added members) — must be
   106	   decided BEFORE campaign-pack hashes freeze (time-critical, U5/U6).
   107	   RECOMMEND: yes, pending a no-semantics-change check at the pack gate.
   108	3. **Reason-code plumbing before night one** (member_id→reason_code +
   109	   16 shadow codes under the ratified spec). RECOMMEND: yes (urgent).
   110	4. **256-tok prefill arm**: RECOMMEND no for the capstone; the marginality
   111	   is published as prospective sizing evidence.
   112	5. **P2 commitment**: authorize the shrunk quantization posture
   113	   (BF16/Q4/Q8, no Q5/Q6, no internal quality verdict) conditional on the
   114	   conversion smoke; MoE reserves the stretch slot.
   115	6. **Calendar**: capstone/advisor/venue evidence-by dates — needed to
   116	   convert "Fall/Spring" into last-arm dates (six post-data weeks + one
   117	   rerun slot reserved first).
   118	7. **Public-artifact scope** (what evidence may be archived) and the
   119	   wall-meter/second-unit external-coordination choice (RECOMMEND: second
   120	   Apple unit over WT310E if only one; neither gates anything).
 11215	- Refusal plumbing benefits every future claim window and has to precede them.
 11216	- No floor should be declared shared merely because a model, runtime, or phase name looks similar.
 11217	
 11218	# Single best second-paper bet: MoE
 11219	
 11220	Choose the re-anchored MoE paper because it has the highest publishable upside if its kill gates clear: it answers an original mechanism question, offers a causal within-checkpoint leg, and can explain why batch-1 unified-memory MoE behaves differently from active-parameter intuition and server-GPU results.
 11221	
 11222	Honest cost: **4–6 desk weeks, two extension nights minimum, three if independently scoped dense/native/forced floors cannot be packed**, no wall meter. Total from today: **six to seven nights including MVP Window C**.
 11223	
 11224	Kill-gate schedule:
 11225	
 11226	1. **Pair ruling, before engineering:** Ed/advisor ratify Qwen3-30B-A3B and Qwen3-4B, exact artifact revisions, and the claim ceiling.
 11227	2. **Capability week:** acquire/hash/load both; prove memory headroom, fixed output policy, tokenizer/workload validity, and a four-hour campaign envelope.
 11228	3. **Observability week:** capture actual expert IDs and weights; require 100% realized-*k* reconciliation, buffered evidence, and instrumentation overhead ≤2%.
 11229	4. **Estimand week:** run teacher-forced and free-running desk comparisons; require routing-locality, unique-expert, reuse, and entropy reports so text divergence cannot masquerade as an expert-budget effect.
 11230	5. **Sizing gate:** project the floor from the relevant member magnitude and require the conservative effect lower bound to exceed **3× the projected operative floor**. The proposal’s fixed 15 J gate is rejected.
 11231	6. **Floor-packing gate:** prove that every claim arm has an independently governed floor and that the frozen schedule fits under four hours with 20% margin. If not, budget the third night before collection or kill.
 11232	7. **Only then collect.**
 11233	
 11234	# Open questions for Ed, ranked
 11235	
 11236	1. **§6 / Window C:** Fund night 4, or formally declare C-iv future work and rewrite the abstract, contribution list, §6, and claims. Recommendation: fund one carefully packed characterization night; do not leave six `[PENDING]` rows in a “complete” paper.
 11237	2. **256-token prefill arm:** Is a directional prefill contrast required beyond the already-funded prefill floors? Recommendation: no in the base MVP. If yes, freeze it as an independent, self-floored fifth claim window; the 128-token riders do not transport.
 11238	3. **Urgent refusal evidence fix:** Authorize the minimal `member_id→reason_code` verdict plumbing and the 16-code spec reconciliation before alpha. Recommendation: yes; this is operationally urgent regardless of publication plans.
 11239	4. **Second-paper commitment:** Will Ed reserve two to three Spring 2027 nights for the re-anchored MoE study if every desk gate passes? If not, select BF16/Q4/Q8 now as the lower-risk fallback.
 11240	5. **D-117 reported-energy cells:** Should alpha/beta prospectively register reader-facing phase-energy means in addition to floor cells? This adds no members but must be decided before campaign-pack hashes freeze.
 11241	6. **Calibration retry semantics:** Keep zero retries, or prospectively number cause-removal retry slots in the bracket-session state machine? Recommendation: zero for the base plans.
 11242	7. **Wall-meter cutoff:** Set a date by which a calibrated WT310E loan, safe fixture, battery-flux bound, and fan control must exist; otherwise C8 remains future work and cannot block a submission.
 11243	8. **3080 Ti access status:** Resolve owned-versus-borrowed status before presenting GPU portability or split work as scheduled research. The cadence probe can proceed only when access is real.
 11244	
 11245	The portfolio’s central lesson is unusually clear: Ed does not have 24 papers. He has one strong metrology paper, two credible second-paper bets, one high-upside stretch, and a rich set of cheap riders that make the first paper substantially better.

exec
/bin/zsh -lc 'set -u
for p in /Users/edr/jw_models/mlx-community/Qwen3-30B-A3B-4bit /Users/edr/jw_models/mlx-community/Qwen3-4B-4bit /Users/edr/jw_models/mlx-community/Qwen3.5-122B-A10B-4bit; do if [ -d "$p" ]; then echo "PRESENT $p"; du -sh "$p"; find "$p" -maxdepth 3 -type f '"\\( -name '*.metadata' -o -name 'config.json' -o -name 'README.md' \\) -print | sort | head -40; else echo \"ABSENT "'$p"; fi; done
find /Users/edr/.cache/huggingface/hub /Users/edr/Library/Caches/huggingface/hub -maxdepth 2 -type d -iname '"'*Qwen3*30B*A3B*4bit*' -print 2>/dev/null || true
find /Users/edr -maxdepth 5 -type d -iname '*Qwen3*30B*A3B*4bit*' -print 2>/dev/null | head -50
python3 - <<'PY'
import importlib.util
for m in ['mlx_lm','mlx','huggingface_hub']:
 s=importlib.util.find_spec(m)
 print(m, s.origin if s else 'NOT_IMPORTABLE')
PY
/Users/edr/code/JouleWise/.venv/bin/python - <<'PY'
import importlib.metadata as md, mlx_lm, mlx
print('mlx_lm_path', mlx_lm.__file__)
for p in ('mlx-lm','mlx'):
 print(p, md.version(p))
PY
command -v hf || true
command -v huggingface-cli || true
df -h /Users/edr/jw_models
sysctl -n hw.memsize
vm_stat | head -15" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
exec
/bin/zsh -lc "find /Users/edr/.cache/huggingface/hub -maxdepth 2 -type d -iname '*Qwen3*30B*A3B*4bit*' -print 2>/dev/null; find /Users/edr/Library/Caches/huggingface/hub -maxdepth 2 -type d -iname '*Qwen3*30B*A3B*4bit*' -print 2>/dev/null; /Users/edr/code/JouleWise/.venv/bin/python - <<'PY'
import importlib.metadata as md, mlx_lm
print('mlx_lm_path', mlx_lm.__file__)
for p in ('mlx-lm','mlx','huggingface-hub'):
 try: print(p, md.version(p))
 except Exception as e: print(p, type(e).__name__)
PY
command -v hf || true; command -v huggingface-cli || true; df -h /Users/edr/jw_models; sysctl -n hw.memsize; vm_stat | head -15" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/__init__.py", line 9, in <module>
    from .convert import convert
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/convert.py", line 8, in <module>
    import mlx.nn as nn
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx/nn/__init__.py", line 4, in <module>
    from mlx.nn.layers import *
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx/nn/layers/__init__.py", line 3, in <module>
    from mlx.nn.layers.activations import (
    ...<52 lines>...
    )
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx/nn/layers/activations.py", line 19, in <module>
    @partial(mx.compile, shapeless=True)
     ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: [metal::load_device] No Metal device available. This typically occurs in headless, sandboxed, or virtualized macOS sessions where the GPU is not accessible.
Exception ignored in atexit callback <nanobind.nb_func object at 0x10587e8a0>:
RuntimeError: [metal::load_device] No Metal device available. This typically occurs in headless, sandboxed, or virtualized macOS sessions where the GPU is not accessible.
Filesystem      Size    Used   Avail Capacity iused ifree %iused  Mounted on
/dev/disk3s5   926Gi   876Gi    29Gi    97%    2.1M  300M    1%   /System/Volumes/Data
sysctl: sysctl fmt -1 1024 1: Operation not permitted
Mach Virtual Memory Statistics: (page size of 16384 bytes)
Pages free:                                  4332982.
Pages active:                                1789048.
Pages inactive:                              1775277.
Pages speculative:                            162706.
Pages throttled:                                   0.
Pages wired down:                             261835.
Pages purgeable:                               95618.
"Translation faults":                    16436754152.
Pages copy-on-write:                      2125781513.
Pages zero filled:                        5607453446.
Pages reactivated:                           3479550.
Pages purged:                               16103329.
File-backed pages:                           1406955.
Anonymous pages:                             2320076.

codex
Local verification is decisive: the 30B artifact directory and Hugging Face cache snapshot are absent; the dense 4B artifact is present (2.1 GB). Only 29 GiB is currently free, so the nominal ~17 GB acquisition is possible but leaves too little safety margin unless the capability gate first establishes a larger disk reserve. This sandbox also has no Metal device, so load/headroom/timing must be run later in Ed’s real host session, not inferred here.
 succeeded in 25492ms:
mlx_lm NOT_IMPORTABLE
mlx NOT_IMPORTABLE
huggingface_hub NOT_IMPORTABLE
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/__init__.py", line 9, in <module>
    from .convert import convert
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/convert.py", line 8, in <module>
    import mlx.nn as nn
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx/nn/__init__.py", line 4, in <module>
    from mlx.nn.layers import *
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx/nn/layers/__init__.py", line 3, in <module>
    from mlx.nn.layers.activations import (
    ...<52 lines>...
    )
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx/nn/layers/activations.py", line 19, in <module>
    @partial(mx.compile, shapeless=True)
     ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: [metal::load_device] No Metal device available. This typically occurs in headless, sandboxed, or virtualized macOS sessions where the GPU is not accessible.
Exception ignored in atexit callback <nanobind.nb_func object at 0x10841a8a0>:
RuntimeError: [metal::load_device] No Metal device available. This typically occurs in headless, sandboxed, or virtualized macOS sessions where the GPU is not accessible.
Filesystem      Size    Used   Avail Capacity iused ifree %iused  Mounted on
/dev/disk3s5   926Gi   876Gi    29Gi    97%    2.1M  300M    1%   /System/Volumes/Data
sysctl: sysctl fmt -1 1024 1: Operation not permitted
Mach Virtual Memory Statistics: (page size of 16384 bytes)
Pages free:                                  4332883.
Pages active:                                1788077.
Pages inactive:                              1775162.
Pages speculative:                            161996.
Pages throttled:                                   0.
Pages wired down:                             263237.
Pages purgeable:                               95664.
"Translation faults":                    16437773425.
Pages copy-on-write:                      2125917988.
Pages zero filled:                        5607618038.
Pages reactivated:                           3479550.
Pages purged:                               16103649.
File-backed pages:                           1406074.
Anonymous pages:                             2319161.

exec
/bin/zsh -lc "SITE=/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages; python3 - <<'PY'
from importlib.metadata import PathDistribution
from pathlib import Path
site=Path('/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages')
for dist in map(PathDistribution, site.glob('*.dist-info')):
 n=(dist.metadata.get('Name') or '').lower()
 if n in {'mlx-lm','mlx','huggingface-hub'}:
  print(n, dist.version, dist._path)
PY
rg -n \"class Qwen3NextSparseMoeBlock|def __call__|top_k|argpartition|take_along_axis|switch_mlp|norm_topk_prob|SparseMoeBlock|qwen3_5_moe\" \""'$SITE/mlx_lm/models/qwen3_next.py" "$SITE/mlx_lm/models/qwen3_5.py" "$SITE/mlx_lm/models/qwen3_5_moe.py" "$SITE/mlx_lm/models/qwen3.py" 2>/dev/null
nl -ba "$SITE/mlx_lm/models/qwen3_next.py" | sed -n '"'245,335p'
nl -ba \""'$SITE/mlx_lm/models/qwen3_5.py" | sed -n '"'1,90p'
nl -ba \""'$SITE/mlx_lm/models/qwen3_5_moe.py" | sed -n '"'1,100p'
nl -ba \""'$SITE/mlx_lm/models/qwen3.py" | sed -n '"'1,180p' 2>/dev/null" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
mlx-lm 0.31.3 /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm-0.31.3.dist-info
mlx 0.31.2 /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx-0.31.2.dist-info
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5_moe.py:42:                new_weights[f"{prefix}.switch_mlp.gate_proj.weight"] = gate_up[
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5_moe.py:45:                new_weights[f"{prefix}.switch_mlp.up_proj.weight"] = gate_up[
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5_moe.py:48:                new_weights[f"{prefix}.switch_mlp.down_proj.weight"] = new_weights.pop(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:51:    norm_topk_prob: bool = False
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:71:    def __call__(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:121:    def __call__(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:168:    def __call__(self, x) -> mx.array:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:236:    def __call__(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:267:                cache[0] = mx.take_along_axis(conv_input, positions, axis=1)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:308:class Qwen3NextSparseMoeBlock(nn.Module):
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:315:        self.norm_topk_prob = args.norm_topk_prob
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:317:        self.top_k = args.num_experts_per_tok
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:320:        self.switch_mlp = SwitchGLU(dim, intermediate_size, num_experts)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:327:    def __call__(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:337:        k = self.top_k
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:338:        inds = mx.argpartition(gates, kth=-k, axis=-1)[..., -k:]
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:339:        scores = mx.take_along_axis(gates, inds, axis=-1)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:340:        if self.norm_topk_prob:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:343:        y = self.switch_mlp(x, inds)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:373:            self.mlp = Qwen3NextSparseMoeBlock(args)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:377:    def __call__(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:404:    def __call__(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:433:    def __call__(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:467:                weights[f"{prefix}.switch_mlp.{n}.weight"] = mx.stack(to_join)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3.py:59:    def __call__(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3.py:99:    def __call__(self, x) -> mx.array:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3.py:116:    def __call__(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3.py:142:    def __call__(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3.py:172:    def __call__(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py:21:from .qwen3_next import Qwen3NextSparseMoeBlock as SparseMoeBlock
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py:51:    norm_topk_prob: bool = True
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py:132:    def __call__(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py:164:                cache[0] = mx.take_along_axis(conv_input, positions, axis=1)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py:224:            self.mlp = SparseMoeBlock(args)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py:228:    def __call__(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py:254:    def __call__(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py:287:    def __call__(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py:374:    def __call__(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py:509:                    layer.mlp.switch_mlp.gate_proj, "all-to-sharded", group=group
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py:512:                    layer.mlp.switch_mlp.down_proj, "sharded-to-all", group=group
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py:515:                    layer.mlp.switch_mlp.up_proj, "all-to-sharded", group=group
   245	        )
   246	
   247	        if cache is not None and cache[0] is not None:
   248	            conv_state = cache[0]
   249	        else:
   250	            conv_state = mx.zeros(
   251	                (B, self.conv_kernel_size - 1, self.conv_dim),
   252	                dtype=inputs.dtype,
   253	            )
   254	
   255	        mixed_qkv = mx.concatenate(
   256	            [q.reshape(B, S, -1), k.reshape(B, S, -1), v.reshape(B, S, -1)], axis=-1
   257	        )
   258	        if mask is not None:
   259	            mixed_qkv = mx.where(mask[..., None], mixed_qkv, 0)
   260	        conv_input = mx.concatenate([conv_state, mixed_qkv], axis=1)
   261	
   262	        if cache is not None:
   263	            n_keep = self.conv_kernel_size - 1
   264	            if cache.lengths is not None:
   265	                ends = mx.clip(cache.lengths, 0, S)
   266	                positions = (ends[:, None] + mx.arange(n_keep))[..., None]
   267	                cache[0] = mx.take_along_axis(conv_input, positions, axis=1)
   268	            else:
   269	                cache[0] = mx.contiguous(conv_input[:, -n_keep:, :])
   270	
   271	        conv_out = nn.silu(self.conv1d(conv_input))
   272	
   273	        q, k, v = [
   274	            t.reshape(B, S, h, d)
   275	            for t, h, d in zip(
   276	                mx.split(conv_out, [self.key_dim, 2 * self.key_dim], -1),
   277	                [self.num_k_heads, self.num_k_heads, self.num_v_heads],
   278	                [self.head_k_dim, self.head_k_dim, self.head_v_dim],
   279	            )
   280	        ]
   281	
   282	        state = cache[1] if cache else None
   283	        inv_scale = k.shape[-1] ** -0.5
   284	        q = (inv_scale**2) * mx.fast.rms_norm(q, None, 1e-6)
   285	        k = inv_scale * mx.fast.rms_norm(k, None, 1e-6)
   286	
   287	        out, state = gated_delta_update(
   288	            q,
   289	            k,
   290	            v,
   291	            a,
   292	            b,
   293	            self.A_log,
   294	            self.dt_bias,
   295	            state,
   296	            mask,
   297	            use_kernel=not self.training,
   298	        )
   299	
   300	        if cache is not None:
   301	            cache[1] = state
   302	            cache.advance(S)
   303	
   304	        out = self.norm(out, z)
   305	        return self.out_proj(out.reshape(B, S, -1))
   306	
   307	
   308	class Qwen3NextSparseMoeBlock(nn.Module):
   309	    def __init__(self, args: ModelArgs):
   310	        super().__init__()
   311	        dim = args.hidden_size
   312	        intermediate_size = args.moe_intermediate_size
   313	        shared_expert_intermediate_size = args.shared_expert_intermediate_size
   314	
   315	        self.norm_topk_prob = args.norm_topk_prob
   316	        self.num_experts = num_experts = args.num_experts
   317	        self.top_k = args.num_experts_per_tok
   318	
   319	        self.gate = nn.Linear(dim, num_experts, bias=False)
   320	        self.switch_mlp = SwitchGLU(dim, intermediate_size, num_experts)
   321	
   322	        self.shared_expert = Qwen3NextMLP(dim, shared_expert_intermediate_size)
   323	        self.shared_expert_gate = nn.Linear(dim, 1, bias=False)
   324	
   325	        self.sharding_group = None
   326	
   327	    def __call__(
   328	        self,
   329	        x: mx.array,
   330	    ) -> mx.array:
   331	        if self.sharding_group is not None:
   332	            x = sum_gradients(self.sharding_group)(x)
   333	
   334	        gates = self.gate(x)
   335	        gates = mx.softmax(gates, axis=-1, precise=True)
     1	# Copyright © 2026 Apple Inc.
     2	
     3	from dataclasses import dataclass, field
     4	from typing import Any, Dict, List, Optional, Union
     5	
     6	import mlx.core as mx
     7	import mlx.nn as nn
     8	from mlx.nn.layers.distributed import shard_inplace, shard_linear, sum_gradients
     9	from mlx.utils import tree_map
    10	
    11	from .base import (
    12	    BaseModelArgs,
    13	    create_attention_mask,
    14	    create_ssm_mask,
    15	)
    16	from .cache import ArraysCache, KVCache
    17	from .gated_delta import gated_delta_update
    18	from .qwen3_next import Qwen3NextAttention as Attention
    19	from .qwen3_next import Qwen3NextMLP as MLP
    20	from .qwen3_next import Qwen3NextRMSNormGated as RMSNormGated
    21	from .qwen3_next import Qwen3NextSparseMoeBlock as SparseMoeBlock
    22	
    23	
    24	@dataclass
    25	class TextModelArgs(BaseModelArgs):
    26	    model_type: str = ""
    27	    hidden_size: int = 4096
    28	    intermediate_size: int = 14336
    29	    num_hidden_layers: int = 32
    30	    num_attention_heads: int = 32
    31	    rms_norm_eps: float = 1e-6
    32	    vocab_size: int = 151936
    33	    num_key_value_heads: int = 8
    34	    max_position_embeddings: int = 131072
    35	    linear_num_value_heads: int = 64
    36	    linear_num_key_heads: int = 16
    37	    linear_key_head_dim: int = 192
    38	    linear_value_head_dim: int = 128
    39	    linear_conv_kernel_dim: int = 4
    40	    tie_word_embeddings: bool = False
    41	    attention_bias: bool = False
    42	    head_dim: Optional[int] = None
    43	    full_attention_interval: int = 4
    44	
    45	    # MoE fields (optional, for Qwen3_5MoeForConditionalGeneration)
    46	    num_experts: int = 0
    47	    num_experts_per_tok: int = 0
    48	    decoder_sparse_step: int = 1
    49	    shared_expert_intermediate_size: int = 0
    50	    moe_intermediate_size: int = 0
    51	    norm_topk_prob: bool = True
    52	
    53	    # Rope parameters
    54	    rope_parameters: Optional[Dict[str, Union[float, str, bool, List[int]]]] = field(
    55	        default_factory=lambda: {
    56	            "type": "default",
    57	            "mrope_section": [11, 11, 10],
    58	            "rope_theta": 100000,
    59	            "partial_rotary_factor": 0.25,
    60	        }
    61	    )
    62	
    63	    # Derived from rope_parameters (set in __post_init__)
    64	    partial_rotary_factor: float = 0.25
    65	    rope_theta: float = 100000.0
    66	    rope_scaling: Optional[Dict[str, Union[float, str]]] = None
    67	
    68	    def __post_init__(self):
    69	        if self.head_dim is None:
    70	            self.head_dim = self.hidden_size // self.num_attention_heads
    71	
    72	        if self.rope_parameters:
    73	            if (
    74	                "type" not in self.rope_parameters
    75	                and "rope_type" in self.rope_parameters
    76	            ):
    77	                self.rope_parameters["type"] = self.rope_parameters.pop("rope_type")
    78	
    79	            self.partial_rotary_factor = self.rope_parameters.get(
    80	                "partial_rotary_factor", 0.25
    81	            )
    82	            self.rope_theta = self.rope_parameters.get("rope_theta", 100000.0)
    83	            self.rope_scaling = self.rope_parameters
    84	
    85	
    86	class GatedDeltaNet(nn.Module):
    87	    def __init__(self, config: TextModelArgs):
    88	        super().__init__()
    89	        self.hidden_size = config.hidden_size
    90	        self.num_v_heads = config.linear_num_value_heads
     1	# Copyright © 2026 Apple Inc.
     2	
     3	from dataclasses import dataclass
     4	
     5	from .base import BaseModelArgs
     6	from .qwen3_5 import Model as Qwen3_5Model
     7	
     8	
     9	@dataclass
    10	class ModelArgs(BaseModelArgs):
    11	    model_type: str
    12	    text_config: dict
    13	
    14	    @classmethod
    15	    def from_dict(cls, params):
    16	        if "text_config" not in params:
    17	            return cls(model_type=params["model_type"], text_config=params)
    18	        return super().from_dict(params)
    19	
    20	
    21	class Model(Qwen3_5Model):
    22	
    23	    def sanitize(self, weights):
    24	        new_weights = {}
    25	        for key, value in weights.items():
    26	            if key.startswith("vision_tower") or key.startswith("model.visual"):
    27	                continue
    28	            if key.startswith("model.language_model"):
    29	                key = key.replace("model.language_model", "language_model.model")
    30	            elif key.startswith("language_model."):
    31	                pass
    32	            else:
    33	                key = "language_model." + key
    34	            new_weights[key] = value
    35	
    36	        for l in range(self.language_model.args.num_hidden_layers):
    37	            prefix = f"language_model.model.layers.{l}.mlp"
    38	            gate_up_key = f"{prefix}.experts.gate_up_proj"
    39	            if gate_up_key in new_weights:
    40	                gate_up = new_weights.pop(gate_up_key)
    41	                mid = gate_up.shape[-2] // 2
    42	                new_weights[f"{prefix}.switch_mlp.gate_proj.weight"] = gate_up[
    43	                    ..., :mid, :
    44	                ]
    45	                new_weights[f"{prefix}.switch_mlp.up_proj.weight"] = gate_up[
    46	                    ..., mid:, :
    47	                ]
    48	                new_weights[f"{prefix}.switch_mlp.down_proj.weight"] = new_weights.pop(
    49	                    f"{prefix}.experts.down_proj"
    50	                )
    51	
    52	        return self.language_model.sanitize(new_weights)
     1	# Copyright © 2023-2024 Apple Inc.
     2	
     3	from dataclasses import dataclass
     4	from typing import Any, Dict, Optional, Union
     5	
     6	import mlx.core as mx
     7	import mlx.nn as nn
     8	from mlx.nn.layers.distributed import shard_linear
     9	
    10	from .activations import swiglu
    11	from .base import BaseModelArgs, create_attention_mask, scaled_dot_product_attention
    12	from .rope_utils import initialize_rope
    13	
    14	
    15	@dataclass
    16	class ModelArgs(BaseModelArgs):
    17	    model_type: str
    18	    hidden_size: int
    19	    num_hidden_layers: int
    20	    intermediate_size: int
    21	    num_attention_heads: int
    22	    rms_norm_eps: float
    23	    vocab_size: int
    24	    num_key_value_heads: int
    25	    max_position_embeddings: int
    26	    rope_theta: float
    27	    head_dim: int
    28	    tie_word_embeddings: bool
    29	    rope_scaling: Optional[Dict[str, Union[float, str]]] = None
    30	
    31	
    32	class Attention(nn.Module):
    33	    def __init__(self, args: ModelArgs):
    34	        super().__init__()
    35	
    36	        dim = args.hidden_size
    37	        self.n_heads = n_heads = args.num_attention_heads
    38	        assert args.num_key_value_heads is not None
    39	        self.n_kv_heads = n_kv_heads = args.num_key_value_heads
    40	
    41	        head_dim = args.head_dim
    42	        self.scale = head_dim**-0.5
    43	
    44	        self.q_proj = nn.Linear(dim, n_heads * head_dim, bias=False)
    45	        self.k_proj = nn.Linear(dim, n_kv_heads * head_dim, bias=False)
    46	        self.v_proj = nn.Linear(dim, n_kv_heads * head_dim, bias=False)
    47	        self.o_proj = nn.Linear(n_heads * head_dim, dim, bias=False)
    48	
    49	        self.q_norm = nn.RMSNorm(head_dim, eps=args.rms_norm_eps)
    50	        self.k_norm = nn.RMSNorm(head_dim, eps=args.rms_norm_eps)
    51	        self.rope = initialize_rope(
    52	            head_dim,
    53	            base=args.rope_theta,
    54	            traditional=False,
    55	            scaling_config=args.rope_scaling,
    56	            max_position_embeddings=args.max_position_embeddings,
    57	        )
    58	
    59	    def __call__(
    60	        self,
    61	        x: mx.array,
    62	        mask: Optional[mx.array] = None,
    63	        cache: Optional[Any] = None,
    64	    ) -> mx.array:
    65	        B, L, D = x.shape
    66	
    67	        queries, keys, values = self.q_proj(x), self.k_proj(x), self.v_proj(x)
    68	
    69	        queries = self.q_norm(queries.reshape(B, L, self.n_heads, -1)).transpose(
    70	            0, 2, 1, 3
    71	        )
    72	        keys = self.k_norm(keys.reshape(B, L, self.n_kv_heads, -1)).transpose(
    73	            0, 2, 1, 3
    74	        )
    75	        values = values.reshape(B, L, self.n_kv_heads, -1).transpose(0, 2, 1, 3)
    76	
    77	        if cache is not None:
    78	            queries = self.rope(queries, offset=cache.offset)
    79	            keys = self.rope(keys, offset=cache.offset)
    80	            keys, values = cache.update_and_fetch(keys, values)
    81	        else:
    82	            queries = self.rope(queries)
    83	            keys = self.rope(keys)
    84	
    85	        output = scaled_dot_product_attention(
    86	            queries, keys, values, cache=cache, scale=self.scale, mask=mask
    87	        )
    88	        output = output.transpose(0, 2, 1, 3).reshape(B, L, -1)
    89	        return self.o_proj(output)
    90	
    91	
    92	class MLP(nn.Module):
    93	    def __init__(self, dim, hidden_dim):
    94	        super().__init__()
    95	        self.gate_proj = nn.Linear(dim, hidden_dim, bias=False)
    96	        self.down_proj = nn.Linear(hidden_dim, dim, bias=False)
    97	        self.up_proj = nn.Linear(dim, hidden_dim, bias=False)
    98	
    99	    def __call__(self, x) -> mx.array:
   100	        return self.down_proj(swiglu(self.gate_proj(x), self.up_proj(x)))
   101	
   102	
   103	class TransformerBlock(nn.Module):
   104	    def __init__(self, args: ModelArgs):
   105	        super().__init__()
   106	        self.num_attention_heads = args.num_attention_heads
   107	        self.hidden_size = args.hidden_size
   108	        self.self_attn = Attention(args)
   109	        self.mlp = MLP(args.hidden_size, args.intermediate_size)
   110	        self.input_layernorm = nn.RMSNorm(args.hidden_size, eps=args.rms_norm_eps)
   111	        self.post_attention_layernorm = nn.RMSNorm(
   112	            args.hidden_size, eps=args.rms_norm_eps
   113	        )
   114	        self.args = args
   115	
   116	    def __call__(
   117	        self,
   118	        x: mx.array,
   119	        mask: Optional[mx.array] = None,
   120	        cache: Optional[Any] = None,
   121	    ) -> mx.array:
   122	        r = self.self_attn(self.input_layernorm(x), mask, cache)
   123	        h = x + r
   124	        r = self.mlp(self.post_attention_layernorm(h))
   125	        out = h + r
   126	        return out
   127	
   128	
   129	class Qwen3Model(nn.Module):
   130	    def __init__(self, args: ModelArgs):
   131	        super().__init__()
   132	        self.args = args
   133	        self.vocab_size = args.vocab_size
   134	        self.num_hidden_layers = args.num_hidden_layers
   135	        assert self.vocab_size > 0
   136	        self.embed_tokens = nn.Embedding(args.vocab_size, args.hidden_size)
   137	        self.layers = [
   138	            TransformerBlock(args=args) for _ in range(args.num_hidden_layers)
   139	        ]
   140	        self.norm = nn.RMSNorm(args.hidden_size, eps=args.rms_norm_eps)
   141	
   142	    def __call__(
   143	        self,
   144	        inputs: mx.array,
   145	        cache=None,
   146	        input_embeddings: Optional[mx.array] = None,
   147	    ):
   148	        if input_embeddings is not None:
   149	            h = input_embeddings
   150	        else:
   151	            h = self.embed_tokens(inputs)
   152	
   153	        if cache is None:
   154	            cache = [None] * len(self.layers)
   155	        mask = create_attention_mask(h, cache[0])
   156	
   157	        for layer, c in zip(self.layers, cache):
   158	            h = layer(h, mask, c)
   159	
   160	        return self.norm(h)
   161	
   162	
   163	class Model(nn.Module):
   164	    def __init__(self, args: ModelArgs):
   165	        super().__init__()
   166	        self.args = args
   167	        self.model_type = args.model_type
   168	        self.model = Qwen3Model(args)
   169	        if not args.tie_word_embeddings:
   170	            self.lm_head = nn.Linear(args.hidden_size, args.vocab_size, bias=False)
   171	
   172	    def __call__(
   173	        self,
   174	        inputs: mx.array,
   175	        cache=None,
   176	        input_embeddings: Optional[mx.array] = None,
   177	    ):
   178	        out = self.model(inputs, cache, input_embeddings)
   179	        if self.args.tie_word_embeddings:
   180	            out = self.model.embed_tokens.as_linear(out)

exec
/bin/zsh -lc 'SITE=/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models
ls "$SITE" | rg '"'"'^qwen3.*'"\\.py"'$'"'
rg -n \"class .*Sparse.*Moe|class .*MoE|num_experts_per_tok|argpartition|top_k|switch_mlp|scores\" \""'$SITE"/qwen3*.py
nl -ba "$SITE/qwen3_next.py" | sed -n '"'308,355p'
if [ -f \""'$SITE/qwen3_moe.py" ]; then nl -ba "$SITE/qwen3_moe.py" | sed -n '"'1,260p'; fi
python3 - <<'PY'
import json
from pathlib import Path
for name in ['Qwen3-4B-4bit','Qwen3.5-122B-A10B-4bit']:
 p=Path('/Users/edr/jw_models/mlx-community')/name
 c=json.loads((p/'config.json').read_text())
 print(name)
 for k in ['_name_or_path','model_type','architectures','quantization','quantization_config','num_hidden_layers','hidden_size','intermediate_size','vocab_size','num_experts','num_experts_per_tok','moe_intermediate_size','shared_expert_intermediate_size','tie_word_embeddings']:
  if k in c: print(' ',k, c[k])
 print(' files', len([x for x in p.iterdir() if x.is_file()]))
 cache=p/'.cache/huggingface/download'
 if cache.exists():
  for f in sorted(cache.glob('*.metadata'))[:20]:
   print(' meta',f.name, f.read_text(errors='replace').splitlines()[:3])
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
qwen3.py
qwen3_5.py
qwen3_5_moe.py
qwen3_moe.py
qwen3_next.py
qwen3_vl.py
qwen3_vl_moe.py
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:39:    num_experts_per_tok: int
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:308:class Qwen3NextSparseMoeBlock(nn.Module):
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:317:        self.top_k = args.num_experts_per_tok
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:320:        self.switch_mlp = SwitchGLU(dim, intermediate_size, num_experts)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:337:        k = self.top_k
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:338:        inds = mx.argpartition(gates, kth=-k, axis=-1)[..., -k:]
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:339:        scores = mx.take_along_axis(gates, inds, axis=-1)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:341:            scores = scores / scores.sum(axis=-1, keepdims=True)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:343:        y = self.switch_mlp(x, inds)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:344:        y = (y * scores[..., None]).sum(axis=-2)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py:467:                weights[f"{prefix}.switch_mlp.{n}.weight"] = mx.stack(to_join)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5_moe.py:42:                new_weights[f"{prefix}.switch_mlp.gate_proj.weight"] = gate_up[
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5_moe.py:45:                new_weights[f"{prefix}.switch_mlp.up_proj.weight"] = gate_up[
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5_moe.py:48:                new_weights[f"{prefix}.switch_mlp.down_proj.weight"] = new_weights.pop(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py:47:    num_experts_per_tok: int = 0
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py:509:                    layer.mlp.switch_mlp.gate_proj, "all-to-sharded", group=group
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py:512:                    layer.mlp.switch_mlp.down_proj, "sharded-to-all", group=group
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py:515:                    layer.mlp.switch_mlp.up_proj, "all-to-sharded", group=group
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_vl_moe.py:59:                weights[f"{prefix}.switch_mlp.gate_proj.weight"] = gate_up[
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_vl_moe.py:62:                weights[f"{prefix}.switch_mlp.up_proj.weight"] = gate_up[
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_vl_moe.py:65:                weights[f"{prefix}.switch_mlp.down_proj.weight"] = weights.pop(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_moe.py:22:    num_experts_per_tok: int
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_moe.py:110:class Qwen3MoeSparseMoeBlock(nn.Module):
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_moe.py:117:        self.top_k = args.num_experts_per_tok
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_moe.py:121:        self.switch_mlp = SwitchGLU(dim, intermediate_size, num_experts)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_moe.py:130:        k = self.top_k
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_moe.py:131:        inds = mx.argpartition(gates, kth=-k, axis=-1)[..., -k:]
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_moe.py:132:        scores = mx.take_along_axis(gates, inds, axis=-1)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_moe.py:134:            scores /= mx.sum(scores, axis=-1, keepdims=True)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_moe.py:136:        y = self.switch_mlp(x, inds)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_moe.py:137:        y = (y * scores[..., None]).sum(axis=-2)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_moe.py:245:                    weights[f"{prefix}.mlp.switch_mlp.{n}.weight"] = mx.stack(to_join)
   308	class Qwen3NextSparseMoeBlock(nn.Module):
   309	    def __init__(self, args: ModelArgs):
   310	        super().__init__()
   311	        dim = args.hidden_size
   312	        intermediate_size = args.moe_intermediate_size
   313	        shared_expert_intermediate_size = args.shared_expert_intermediate_size
   314	
   315	        self.norm_topk_prob = args.norm_topk_prob
   316	        self.num_experts = num_experts = args.num_experts
   317	        self.top_k = args.num_experts_per_tok
   318	
   319	        self.gate = nn.Linear(dim, num_experts, bias=False)
   320	        self.switch_mlp = SwitchGLU(dim, intermediate_size, num_experts)
   321	
   322	        self.shared_expert = Qwen3NextMLP(dim, shared_expert_intermediate_size)
   323	        self.shared_expert_gate = nn.Linear(dim, 1, bias=False)
   324	
   325	        self.sharding_group = None
   326	
   327	    def __call__(
   328	        self,
   329	        x: mx.array,
   330	    ) -> mx.array:
   331	        if self.sharding_group is not None:
   332	            x = sum_gradients(self.sharding_group)(x)
   333	
   334	        gates = self.gate(x)
   335	        gates = mx.softmax(gates, axis=-1, precise=True)
   336	
   337	        k = self.top_k
   338	        inds = mx.argpartition(gates, kth=-k, axis=-1)[..., -k:]
   339	        scores = mx.take_along_axis(gates, inds, axis=-1)
   340	        if self.norm_topk_prob:
   341	            scores = scores / scores.sum(axis=-1, keepdims=True)
   342	
   343	        y = self.switch_mlp(x, inds)
   344	        y = (y * scores[..., None]).sum(axis=-2)
   345	
   346	        shared_y = self.shared_expert(x)
   347	        shared_y = mx.sigmoid(self.shared_expert_gate(x)) * shared_y
   348	
   349	        y = y + shared_y
   350	
   351	        if self.sharding_group is not None:
   352	            y = mx.distributed.all_sum(y, group=self.sharding_group)
   353	
   354	        return y
   355	
     1	# Copyright © 2026 Apple Inc.
     2	
     3	from dataclasses import dataclass
     4	from typing import Any, Dict, List, Optional, Union
     5	
     6	import mlx.core as mx
     7	import mlx.nn as nn
     8	
     9	from .activations import swiglu
    10	from .base import BaseModelArgs, create_attention_mask, scaled_dot_product_attention
    11	from .switch_layers import SwitchGLU
    12	
    13	
    14	@dataclass
    15	class ModelArgs(BaseModelArgs):
    16	    model_type: str
    17	    hidden_size: int
    18	    num_hidden_layers: int
    19	    intermediate_size: int
    20	    num_attention_heads: int
    21	    num_experts: int
    22	    num_experts_per_tok: int
    23	    decoder_sparse_step: int
    24	    mlp_only_layers: List[int]
    25	    moe_intermediate_size: int
    26	    rms_norm_eps: float
    27	    vocab_size: int
    28	    num_key_value_heads: int
    29	    head_dim: int
    30	    rope_theta: float
    31	    tie_word_embeddings: bool
    32	    max_position_embeddings: int
    33	    norm_topk_prob: bool
    34	    rope_scaling: Optional[Dict[str, Union[float, str]]] = None
    35	
    36	
    37	class Attention(nn.Module):
    38	    def __init__(self, args: ModelArgs, layer_idx: int):
    39	        super().__init__()
    40	
    41	        dim = args.hidden_size
    42	        self.n_heads = n_heads = args.num_attention_heads
    43	        assert args.num_key_value_heads is not None
    44	        self.n_kv_heads = n_kv_heads = args.num_key_value_heads
    45	
    46	        head_dim = getattr(
    47	            args, "head_dim", args.hidden_size // args.num_attention_heads
    48	        )
    49	        self.scale = head_dim**-0.5
    50	
    51	        self.q_proj = nn.Linear(dim, n_heads * head_dim, bias=False)
    52	        self.k_proj = nn.Linear(dim, n_kv_heads * head_dim, bias=False)
    53	        self.v_proj = nn.Linear(dim, n_kv_heads * head_dim, bias=False)
    54	        self.o_proj = nn.Linear(n_heads * head_dim, dim, bias=False)
    55	
    56	        self.q_norm = nn.RMSNorm(head_dim, eps=args.rms_norm_eps)
    57	        self.k_norm = nn.RMSNorm(head_dim, eps=args.rms_norm_eps)
    58	
    59	        self.rope = nn.RoPE(
    60	            head_dim,
    61	            traditional=False,
    62	            base=args.rope_theta,
    63	        )
    64	
    65	    def __call__(
    66	        self,
    67	        x: mx.array,
    68	        mask: Optional[mx.array] = None,
    69	        cache: Optional[Any] = None,
    70	    ) -> mx.array:
    71	        B, L, D = x.shape
    72	
    73	        queries, keys, values = self.q_proj(x), self.k_proj(x), self.v_proj(x)
    74	
    75	        # Prepare the queries, keys and values for the attention computation
    76	        queries = self.q_norm(queries.reshape(B, L, self.n_heads, -1)).transpose(
    77	            0, 2, 1, 3
    78	        )
    79	        keys = self.k_norm(keys.reshape(B, L, self.n_kv_heads, -1)).transpose(
    80	            0, 2, 1, 3
    81	        )
    82	        values = values.reshape(B, L, self.n_kv_heads, -1).transpose(0, 2, 1, 3)
    83	
    84	        if cache is not None:
    85	            queries = self.rope(queries, offset=cache.offset)
    86	            keys = self.rope(keys, offset=cache.offset)
    87	            keys, values = cache.update_and_fetch(keys, values)
    88	        else:
    89	            queries = self.rope(queries)
    90	            keys = self.rope(keys)
    91	
    92	        output = scaled_dot_product_attention(
    93	            queries, keys, values, cache=cache, scale=self.scale, mask=mask
    94	        )
    95	        output = output.transpose(0, 2, 1, 3).reshape(B, L, -1)
    96	        return self.o_proj(output)
    97	
    98	
    99	class MLP(nn.Module):
   100	    def __init__(self, dim, hidden_dim):
   101	        super().__init__()
   102	        self.gate_proj = nn.Linear(dim, hidden_dim, bias=False)
   103	        self.down_proj = nn.Linear(hidden_dim, dim, bias=False)
   104	        self.up_proj = nn.Linear(dim, hidden_dim, bias=False)
   105	
   106	    def __call__(self, x) -> mx.array:
   107	        return self.down_proj(swiglu(self.gate_proj(x), self.up_proj(x)))
   108	
   109	
   110	class Qwen3MoeSparseMoeBlock(nn.Module):
   111	    def __init__(self, args: ModelArgs):
   112	        super().__init__()
   113	        dim = args.hidden_size
   114	        intermediate_size = args.moe_intermediate_size
   115	
   116	        self.num_experts = num_experts = args.num_experts
   117	        self.top_k = args.num_experts_per_tok
   118	        self.norm_topk_prob = args.norm_topk_prob
   119	
   120	        self.gate = nn.Linear(dim, num_experts, bias=False)
   121	        self.switch_mlp = SwitchGLU(dim, intermediate_size, num_experts)
   122	
   123	    def __call__(
   124	        self,
   125	        x: mx.array,
   126	    ) -> mx.array:
   127	        gates = self.gate(x)
   128	        gates = mx.softmax(gates, axis=-1, precise=True)
   129	
   130	        k = self.top_k
   131	        inds = mx.argpartition(gates, kth=-k, axis=-1)[..., -k:]
   132	        scores = mx.take_along_axis(gates, inds, axis=-1)
   133	        if self.norm_topk_prob:
   134	            scores /= mx.sum(scores, axis=-1, keepdims=True)
   135	
   136	        y = self.switch_mlp(x, inds)
   137	        y = (y * scores[..., None]).sum(axis=-2)
   138	
   139	        return y
   140	
   141	
   142	class Qwen3MoeDecoderLayer(nn.Module):
   143	    def __init__(self, args: ModelArgs, layer_idx: int):
   144	        super().__init__()
   145	        self.hidden_size = args.hidden_size
   146	        self.self_attn = Attention(args, layer_idx)
   147	
   148	        self.input_layernorm = nn.RMSNorm(args.hidden_size, eps=args.rms_norm_eps)
   149	        self.post_attention_layernorm = nn.RMSNorm(
   150	            args.hidden_size, eps=args.rms_norm_eps
   151	        )
   152	        self.args = args
   153	
   154	        if (layer_idx not in args.mlp_only_layers) and (
   155	            args.num_experts > 0 and (layer_idx + 1) % args.decoder_sparse_step == 0
   156	        ):
   157	            self.mlp = Qwen3MoeSparseMoeBlock(args)
   158	        else:
   159	            self.mlp = MLP(args.hidden_size, args.intermediate_size)
   160	
   161	    def __call__(
   162	        self,
   163	        x: mx.array,
   164	        mask: Optional[mx.array] = None,
   165	        cache: Optional[Any] = None,
   166	    ) -> mx.array:
   167	        r = self.self_attn(self.input_layernorm(x), mask, cache)
   168	        h = x + r
   169	        r = self.mlp(self.post_attention_layernorm(h))
   170	        out = h + r
   171	        return out
   172	
   173	
   174	class Qwen3MoeModel(nn.Module):
   175	    def __init__(self, args: ModelArgs):
   176	        super().__init__()
   177	        self.args = args
   178	        self.vocab_size = args.vocab_size
   179	        self.num_hidden_layers = args.num_hidden_layers
   180	        assert self.vocab_size > 0
   181	        self.embed_tokens = nn.Embedding(args.vocab_size, args.hidden_size)
   182	        self.layers = [
   183	            Qwen3MoeDecoderLayer(args=args, layer_idx=i)
   184	            for i in range(args.num_hidden_layers)
   185	        ]
   186	        self.norm = nn.RMSNorm(args.hidden_size, eps=args.rms_norm_eps)
   187	
   188	    def __call__(
   189	        self,
   190	        inputs: mx.array,
   191	        cache=None,
   192	        input_embeddings: Optional[mx.array] = None,
   193	    ) -> mx.array:
   194	        if input_embeddings is not None:
   195	            h = input_embeddings
   196	        else:
   197	            h = self.embed_tokens(inputs)
   198	
   199	        if cache is None:
   200	            cache = [None] * len(self.layers)
   201	
   202	        mask = create_attention_mask(h, cache[0])
   203	
   204	        for layer, c in zip(self.layers, cache):
   205	            h = layer(h, mask, c)
   206	
   207	        return self.norm(h)
   208	
   209	
   210	class Model(nn.Module):
   211	    def __init__(self, args: ModelArgs):
   212	        super().__init__()
   213	        self.args = args
   214	        self.model_type = args.model_type
   215	        self.model = Qwen3MoeModel(args)
   216	        if not args.tie_word_embeddings:
   217	            self.lm_head = nn.Linear(args.hidden_size, args.vocab_size, bias=False)
   218	
   219	    def __call__(
   220	        self,
   221	        inputs: mx.array,
   222	        cache=None,
   223	        input_embeddings: Optional[mx.array] = None,
   224	    ) -> mx.array:
   225	        out = self.model(inputs, cache, input_embeddings)
   226	        if self.args.tie_word_embeddings:
   227	            out = self.model.embed_tokens.as_linear(out)
   228	        else:
   229	            out = self.lm_head(out)
   230	        return out
   231	
   232	    def sanitize(self, weights):
   233	        if self.args.tie_word_embeddings:
   234	            weights.pop("lm_head.weight", None)
   235	        if "model.layers.0.mlp.experts.0.up_proj.weight" not in weights:
   236	            return weights
   237	        for l in range(self.args.num_hidden_layers):
   238	            prefix = f"model.layers.{l}"
   239	            for n in ["up_proj", "down_proj", "gate_proj"]:
   240	                if f"{prefix}.mlp.experts.0.{n}.weight" in weights:
   241	                    to_join = [
   242	                        weights.pop(f"{prefix}.mlp.experts.{e}.{n}.weight")
   243	                        for e in range(self.args.num_experts)
   244	                    ]
   245	                    weights[f"{prefix}.mlp.switch_mlp.{n}.weight"] = mx.stack(to_join)
   246	        return weights
   247	
   248	    @property
   249	    def quant_predicate(self):
   250	        def predicate(path, _):
   251	            if path.endswith("mlp.gate"):
   252	                return {"group_size": 64, "bits": 8}
   253	            return True
   254	
   255	        return predicate
   256	
   257	    @property
   258	    def layers(self):
   259	        return self.model.layers
Qwen3-4B-4bit
  model_type qwen3
  architectures ['Qwen3ForCausalLM']
  quantization {'group_size': 64, 'bits': 4}
  quantization_config {'group_size': 64, 'bits': 4}
  num_hidden_layers 36
  hidden_size 2560
  intermediate_size 9728
  vocab_size 151936
  tie_word_embeddings True
 files 11
 meta .gitattributes.metadata ['4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25', '52373fe24473b1aa44333d318f578ae6bf04b49b', '1784271400.058351']
 meta README.md.metadata ['4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25', '56a0296b7d72cd9b0438f99913ca38b200a22ce3', '1784271400.138549']
 meta added_tokens.json.metadata ['4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25', 'b54f9135e44c1e81047e8d05cb027af8bc039eed', '1784271400.1862788']
 meta config.json.metadata ['4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25', '032ad326a0daaaeeec00f2a585262acf5f692861', '1784271400.1298912']
 meta merges.txt.metadata ['4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25', '31349551d90c7606f325fe0f11bbb8bd5fa0d7c7', '1784271400.248822']
 meta model.safetensors.index.json.metadata ['4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25', '07e230a328dd17a09d96ee045d49b27596656aff', '1784271400.07003']
 meta model.safetensors.metadata ['4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25', 'e240c0bdc0ebb0681bf0da0f98d9719fd6ebe269a3633f81542c13e81345651d', '1784271422.217062']
 meta special_tokens_map.json.metadata ['4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25', 'ac23c0aaa2434523c494330aeb79c58395378103', '1784271400.1214669']
 meta tokenizer.json.metadata ['4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25', 'aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4', '1784271401.0807118']
 meta tokenizer_config.json.metadata ['4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25', '7345216a0785dc7086e8c245b2a9d3896ce2b756', '1784271400.234236']
 meta vocab.json.metadata ['4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25', '4783fe10ac3adce15ac8f358ef5462739852c569', '1784271400.361224']
Qwen3.5-122B-A10B-4bit
  model_type qwen3_5_moe
  architectures ['Qwen3_5MoeForConditionalGeneration']
  quantization {'group_size': 64, 'bits': 4, 'mode': 'affine'}
  quantization_config {'group_size': 64, 'bits': 4, 'mode': 'affine'}
  tie_word_embeddings False
 files 26
 meta .gitattributes.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', '52373fe24473b1aa44333d318f578ae6bf04b49b', '1783424632.393284']
 meta README.md.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', 'ebdfda1b60ed71e752bc0a86bb381fe85dac9554', '1783424632.365376']
 meta chat_template.jinja.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', 'a585dec894e63da457d9440ec6aa7caa16d20860', '1783424632.365206']
 meta config.json.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', '37a388afaa2b23882b335a3a9561507bf1d91309', '1783424632.393075']
 meta generation_config.json.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', '85b45ab4f3a24f95a061c5260559471a259187cc', '1783424632.296816']
 meta model-00001-of-00014.safetensors.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', 'a2e5982d8ae4087ef151c5faab112a4a1d4b511a399dd4c83390183cf9dc2bed', '1783425074.010657']
 meta model-00002-of-00014.safetensors.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', '617d0276db85950faff4d7e8a253940addcb05137f6374d95d0a9c83e752f883', '1783425075.43778']
 meta model-00003-of-00014.safetensors.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', 'a96a3a6e837c1f2dea15f312ed85189c1887c04b94bbf0e9bd4ce400f4514991', '1783425006.415207']
 meta model-00004-of-00014.safetensors.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', 'fb70d290b16264828109df54b627e448fefbe3477c2772a0c36bc6e8cbbdadb3', '1783425008.374279']
 meta model-00005-of-00014.safetensors.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', 'd396eef8d4fe4911bdf6dcc0e219f60fa55922baae647929c9f2fa00d26abab6', '1783424799.3542888']
 meta model-00006-of-00014.safetensors.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', '19f338fdd7ac3f9246addcb9ec387f28f129a3b36082ebb8f90de20abea10ad2', '1783424793.511633']
 meta model-00007-of-00014.safetensors.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', 'ef428dd92ed6ee5a7d4e32dd8caba3919cb2963040b11e26fbeae98191e23f7f', '1783424805.217982']
 meta model-00008-of-00014.safetensors.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', 'e7c877102c7f1e572838cce84d83890478ca45a3dd6f603d923da2bd9fc68cf5', '1783424793.530713']
 meta model-00009-of-00014.safetensors.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', '4fb3c12704e6010312fd8c377ec15b0f582ca5772e61d67dd4e28c91decc56ce', '1783424993.047817']
 meta model-00010-of-00014.safetensors.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', 'a1de2cfcb5c251578bde9cec23c4d02ed2c37be3de4b5a8a30f5168078aa5a07', '1783424986.965885']
 meta model-00011-of-00014.safetensors.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', 'b8f6fc3bdf62bad1d0db747bafff02a8c179172508bf5ed08d625690f8bac2d1', '1783425002.801536']
 meta model-00012-of-00014.safetensors.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', 'bd42762181ba345e1b092b95384d575b37fe402ad191796b6eab2d38d8b7d357', '1783425014.1561651']
 meta model-00013-of-00014.safetensors.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', 'e240d793b2b925df9564ff934ce2da30ba81f72c78fa1671cffe6958fc7fcbe8', '1783425074.72541']
 meta model-00014-of-00014.safetensors.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', 'aeee4503d75b5d55bd65e001cb4d781bacac886529351cfa7593e9d9fb25ecb0', '1783425064.870324']
 meta model.safetensors.index.json.metadata ['e9c67b08899964be5fdd069bb1b4bc8907fe68f5', 'fbe15d1587f48767933e52ad9c5243759df1d545', '1783425003.1814241']

web search: 
web search: site:huggingface.co/mlx-community/Qwen3-30B-A3B-4bit mlx-community Qwen3-30B-A3B-4bit ...
web search: 
web search: https://huggingface.co/api/models/mlx-community/Qwen3-30B-A3B-4bit
web search: 
web search: "mlx-community/Qwen3-30B-A3B-4bit" "d388dea" ...
web search: 
web search: site:huggingface.co/mlx-community/Qwen3-4B-4bit/commit "4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25" ...
exec
/bin/zsh -lc "ls -1 /Users/edr/code/JouleWise/.venv/bin | rg '"'^(hf|huggingface-cli|mlx_lm'"\\.)' || true
python3 - <<'PY'
from importlib.metadata import PathDistribution
from pathlib import Path
site=Path('/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages')
for dist in map(PathDistribution, site.glob('*.dist-info')):
 n=(dist.metadata.get('Name') or '').lower()
 if n in {'mlx-lm','mlx','huggingface-hub'}:
  print(n, dist.version)
PY
find /Users/edr/jw_models/mlx-community/Qwen3-4B-4bit/.cache/huggingface/download -type f -name '*.metadata' -maxdepth 1 -exec awk 'FNR==1{print FILENAME \":\" "'$0}'"' {} \\; | sort -t: -k2,2 -u
shasum -a 256 /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_moe.py /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
hf
huggingface-cli
mlx_lm.awq
mlx_lm.benchmark
mlx_lm.cache_prompt
mlx_lm.chat
mlx_lm.convert
mlx_lm.dwq
mlx_lm.dynamic_quant
mlx_lm.evaluate
mlx_lm.fuse
mlx_lm.generate
mlx_lm.gptq
mlx_lm.lora
mlx_lm.manage
mlx_lm.perplexity
mlx_lm.server
mlx_lm.share
mlx_lm.upload
mlx-lm 0.31.3
mlx 0.31.2
/Users/edr/jw_models/mlx-community/Qwen3-4B-4bit/.cache/huggingface/download/added_tokens.json.metadata:4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25
539a201316616d2296a15a0998859e8bc0af36d8433d6f78ab0c46beed51b005  /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_moe.py
3c572fe3fbb36721efab4d80d1bb6af11beb4ad1caae18deefc9fc84cbcd9b79  /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_next.py
f0daa30bba5cb521c8bdfa7093101a544c6a37bbba09bca582288219cb04ae3a  /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/models/qwen3_5.py

exec
/bin/zsh -lc "/Users/edr/code/JouleWise/.venv/bin/hf download --help | sed -n '1,180p'; /Users/edr/code/JouleWise/.venv/bin/mlx_lm.generate --help | sed -n '1,220p'; rg -n \"benchmark|peak memory|metal|get_peak|reset_peak|max_tokens|prompt\" /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/benchmark.py /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/utils.py | head -200" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 291ms:
Usage: hf download [OPTIONS] REPO_ID [FILENAMES]...

  Download files from the Hub.

Arguments:
  REPO_ID         The ID of the repo (e.g. `username/repo-name` or
                  `spaces/username/repo-name`).  [required]
  [FILENAMES]...  Files to download (e.g. `config.json`,
                  `data/metadata.jsonl`).

Options:
  --type, --repo-type [model|dataset|space]
                                  The type of repository (model, dataset, or
                                  space).  [default: (model)]
  --revision TEXT                 Git revision id which can be a branch name,
                                  a tag, or a commit hash.
  --include TEXT                  Glob patterns to include from files to
                                  download. eg: *.json
  --exclude TEXT                  Glob patterns to exclude from files to
                                  download.
  --cache-dir TEXT                Directory where to save files.
  --local-dir TEXT                If set, the downloaded file will be placed
                                  under this directory. Check out https://hugg
                                  ingface.co/docs/huggingface_hub/guides/downl
                                  oad#download-files-to-a-local-folder for
                                  more details.
  --force-download / --no-force-download
                                  If True, the files will be downloaded even
                                  if they are already cached.  [default: no-
                                  force-download]
  --dry-run / --no-dry-run        If True, perform a dry run without actually
                                  downloading the file.  [default: no-dry-run]
  --token TEXT                    A User Access Token generated from
                                  https://huggingface.co/settings/tokens.
  --max-workers INTEGER           Maximum number of workers to use for
                                  downloading files. Default is 8.  [default:
                                  8]
  -h, --help                      Show this message and exit.

Formatting options:
  --format [auto|human|agent|json|quiet]
                                  Output format. Defaults to 'auto' which
                                  picks 'agent' or 'human' based on the
                                  terminal.
  --json                          JSON output. Equivalent to '--format json'.
  -q, --quiet                     Quiet output (one ID per line). Equivalent
                                  to '--format quiet'.
  --no-truncate                   Do not truncate scalar values in human
                                  tables (list/dict columns stay shortened).

Examples
  $ hf download meta-llama/Llama-3.2-1B-Instruct
  $ hf download meta-llama/Llama-3.2-1B-Instruct config.json tokenizer.json
  $ hf download meta-llama/Llama-3.2-1B-Instruct --include "*.safetensors"
  --exclude "*.bin"
  $ hf download meta-llama/Llama-3.2-1B-Instruct --local-dir ./models/llama
  $ hf download HuggingFaceM4/FineVision art/ --repo-type dataset
  $ hf download hf://datasets/HuggingFaceH4/ultrachat_200k

Learn more
  Use `hf <command> --help` for more information about a command.
  Read the documentation at
  https://huggingface.co/docs/huggingface_hub/en/guides/cli
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise/.venv/bin/mlx_lm.generate", line 3, in <module>
    from mlx_lm.generate import main
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/__init__.py", line 9, in <module>
    from .convert import convert
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/convert.py", line 8, in <module>
    import mlx.nn as nn
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx/nn/__init__.py", line 4, in <module>
    from mlx.nn.layers import *
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx/nn/layers/__init__.py", line 3, in <module>
    from mlx.nn.layers.activations import (
    ...<52 lines>...
    )
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx/nn/layers/activations.py", line 19, in <module>
    @partial(mx.compile, shapeless=True)
     ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: [metal::load_device] No Metal device available. This typically occurs in headless, sandboxed, or virtualized macOS sessions where the GPU is not accessible.
Exception ignored in atexit callback <nanobind.nb_func object at 0x109790370>:
RuntimeError: [metal::load_device] No Metal device available. This typically occurs in headless, sandboxed, or virtualized macOS sessions where the GPU is not accessible.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:39:    load_prompt_cache,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:93:        "--system-prompt",
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:95:        help="System prompt to be used for the chat template",
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:98:        "--prompt",
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:154:        help="Use the raw prompt without the tokenizer's chat template.",
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:180:        "--prompt-cache-file",
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:238:    if not mx.metal.is_available():
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:279:        prompt_tokens (int): The number of tokens in the prompt.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:280:        prompt_tps (float): The prompt processing tokens-per-second.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:283:        peak_memory (float): The peak memory used so far in GB.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:291:    prompt_tokens: int
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:292:    prompt_tps: float
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:299:def maybe_quantize_kv_cache(prompt_cache, quantized_kv_start, kv_group_size, kv_bits):
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:302:    for e, c in enumerate(prompt_cache):
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:304:            prompt_cache[e] = c.to_quantized(group_size=kv_group_size, bits=kv_bits)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:308:    prompt: mx.array,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:311:    max_tokens: int = 256,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:315:    prompt_cache: Optional[Any] = None,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:320:    prompt_progress_callback: Optional[Callable[[int, int], None]] = None,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:324:    A generator producing token ids based on the given prompt from the model.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:327:        prompt (mx.array): The input prompt.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:329:        max_tokens (int): The maximum number of tokens. Use``-1`` for an infinite
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:338:        prompt_cache (List[Any], optional): A pre-computed prompt cache. Note, if
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:340:        prefill_step_size (int): Step size for processing the prompt.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:346:        prompt_progress_callback (Callable[[int, int], None]): A call-back which takes the
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:347:           prompt tokens processed so far and the total number of prompt tokens.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:349:          conjunction with prompt tokens. Default: ``None``.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:357:        elif len(prompt) > 0 and len(prompt) != len(input_embeddings):
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:360:                f"must match the sequence length of the prompt ({len(prompt)}), or the "
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:361:                "prompt must be empty."
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:363:    elif len(prompt) == 0:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:365:            "Either input_embeddings or prompt (or both) must be provided."
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:371:    if prompt_cache is None:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:372:        prompt_cache = cache.make_prompt_cache(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:377:    prompt_progress_callback = prompt_progress_callback or (lambda *_: None)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:391:                input_tokens, cache=prompt_cache, input_embeddings=input_embeddings
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:394:            return model(input_tokens, cache=prompt_cache)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:418:            quantize_cache_fn(prompt_cache)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:425:        total_prompt_tokens = (
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:426:            len(input_embeddings) if input_embeddings is not None else len(prompt)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:428:        prompt_processed_tokens = 0
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:429:        prompt_progress_callback(prompt_processed_tokens, total_prompt_tokens)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:430:        while total_prompt_tokens - prompt_processed_tokens > 1:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:431:            remaining = (total_prompt_tokens - prompt_processed_tokens) - 1
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:434:                input_tokens=prompt[:n_to_process][None],
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:441:            quantize_cache_fn(prompt_cache)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:442:            mx.eval([c.state for c in prompt_cache])
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:443:            prompt_processed_tokens += n_to_process
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:444:            prompt_progress_callback(prompt_processed_tokens, total_prompt_tokens)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:445:            prompt = prompt[n_to_process:]
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:453:        y, logprobs = _step(input_tokens=prompt, input_embeddings=input_embeddings)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:458:        if n != max_tokens:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:463:            prompt_progress_callback(total_prompt_tokens, total_prompt_tokens)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:464:        if n == max_tokens:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:474:    prompt: mx.array,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:479:    max_tokens: int = 256,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:482:    prompt_cache: Optional[Any] = None,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:489:    A generator producing token ids based on the given prompt from the model.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:492:        prompt (mx.array): The input prompt.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:497:        max_tokens (int): The maximum number of tokens. Use``-1`` for an infinite
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:504:        prompt_cache (List[Any], optional): A pre-computed prompt cache. Note, if
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:506:        prefill_step_size (int): Step size for processing the prompt.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:518:    y = prompt.astype(mx.uint32)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:522:    if prompt_cache is None:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:523:        model_cache = cache.make_prompt_cache(model)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:524:        draft_cache = cache.make_prompt_cache(draft_model)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:526:        model_cache = prompt_cache[: len(model.layers)]
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:527:        draft_cache = prompt_cache[len(model.layers) :]
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:529:    if not cache.can_trim_prompt_cache(model_cache):
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:532:            f"Speculative decoding requires a trimmable prompt cache " f"(got {types})."
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:590:        cache.trim_prompt_cache(model_cache, num_draft - num_accept)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:591:        cache.trim_prompt_cache(draft_cache, max(num_draft - num_accept - 1, 0))
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:613:            num_draft = min(max_tokens - ntoks, num_draft_tokens)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:630:                if ntoks == max_tokens:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:632:            if ntoks < max_tokens:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:636:            if ntoks == max_tokens:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:660:    prompt: Union[str, mx.array, List[int]],
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:661:    max_tokens: int = 256,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:666:    A generator producing text based on the given prompt from the model.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:671:        prompt (Union[str, mx.array, List[int]]): The input prompt string or
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:673:        max_tokens (int): The maximum number of tokens to generate.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:688:    if not isinstance(prompt, mx.array):
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:689:        if isinstance(prompt, str):
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:691:            add_special_tokens = tokenizer.bos_token is None or not prompt.startswith(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:694:            prompt = tokenizer.encode(prompt, add_special_tokens=add_special_tokens)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:695:        prompt = mx.array(prompt)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:699:    kwargs["max_tokens"] = max_tokens
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:703:        token_generator = generate_step(prompt, model, **kwargs)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:710:        kwargs.pop("prompt_progress_callback", None)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:712:            prompt, model, draft_model, **kwargs
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:718:                prompt_time = time.perf_counter() - tic
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:719:                prompt_tps = prompt.size / prompt_time
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:725:            if (n + 1) == max_tokens:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:733:                prompt_tokens=prompt.size,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:734:                prompt_tps=prompt_tps,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:737:                peak_memory=mx.get_peak_memory() / 1e9,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:747:            prompt_tokens=prompt.size,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:748:            prompt_tps=prompt_tps,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:751:            peak_memory=mx.get_peak_memory() / 1e9,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:759:    prompt: Union[str, List[int]],
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:769:       prompt (Union[str, List[int]]): The input prompt string or integer tokens.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:779:    for response in stream_generate(model, tokenizer, prompt, **kwargs):
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:788:            print("No text generated for this prompt")
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:791:            f"Prompt: {response.prompt_tokens} tokens, "
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:792:            f"{response.prompt_tps:.3f} tokens-per-sec"
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:802:def _left_pad_prompts(prompts, max_length=None):
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:804:        max_length = max(len(p) for p in prompts)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:805:    return mx.array([[0] * (max_length - len(p)) + p for p in prompts])
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:808:def _right_pad_prompts(prompts, max_length=None):
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:810:        max_length = max(len(p) for p in prompts)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:811:    return mx.array([p + [0] * (max_length - len(p)) for p in prompts])
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:820:        prompt_tokens (int): The number of prompt tokens processed.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:821:        prompt_tps (float): The prompt processing tokens-per-second.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:822:        prompt_time (float): The time in seconds spent in prompt processing.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:826:        peak_memory (float): The peak memory used so far in GB.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:829:    prompt_tokens: int = 0
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:830:    prompt_tps: float = 0
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:831:    prompt_time: float = 0
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1006:    A batch processor for prompt tokens with support for incremental processing.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1008:    This class handles batched prompt processing, managing KV caches and preparing
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1017:        end_of_prompt: bool
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1032:        max_tokens: Optional[List[int]] = None,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1036:        self.prompt_cache = _merge_caches(caches)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1050:        self.max_tokens = (
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1051:            max_tokens
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1052:            if max_tokens is not None
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1060:        return [c.extract(idx) for c in self.prompt_cache]
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1075:        self.prompt_cache = _extend_cache(self.prompt_cache, batch.prompt_cache)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1079:        self.max_tokens.extend(batch.max_tokens)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1086:        new_batch.prompt_cache = copy.deepcopy(self.prompt_cache)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1093:        new_batch.max_tokens = list(self.max_tokens)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1108:            self.prompt_cache.clear()
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1110:            for c in self.prompt_cache:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1121:        self.max_tokens = [self.max_tokens[idx] for idx in keep]
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1124:    def prompt(self, tokens: List[List[int]]):
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1126:        Process prompt tokens through the model.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1151:            tokens = _right_pad_prompts(tokens, max_length=max_length)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1152:            for c in self.prompt_cache:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1157:        # Actual prompt processing loop
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1160:            self.model(tokens[:, :n_to_process], cache=self.prompt_cache)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1161:            mx.eval([c.state for c in self.prompt_cache])
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1167:            for c in self.prompt_cache:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1169:            mx.eval([c.state for c in self.prompt_cache])
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1174:        Transition from prompt processing to generation.
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1183:            self.prompt([t[:-1] for t in tokens])
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1190:            self.prompt_cache,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1196:            self.max_tokens,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1200:        self.prompt_cache = []
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1204:        self.max_tokens = []
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1224:            max_tokens=[],
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1233:    This class handles the generation phase after prompt processing, managing
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1245:        prompt_cache: Optional[List[Any]]
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1253:        prompt_cache: List[Any],
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1261:        max_tokens: List[int],
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1265:        self.prompt_cache = prompt_cache
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1272:        self.max_tokens = max_tokens
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1296:        self.prompt_cache = _extend_cache(self.prompt_cache, batch.prompt_cache)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1300:        self.max_tokens.extend(batch.max_tokens)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1332:        logits = self.model(inputs[:, None], cache=self.prompt_cache)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1381:        return [c.extract(idx) for c in self.prompt_cache]
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1387:            self.prompt_cache.clear()
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1389:            for c in self.prompt_cache:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1396:        self.max_tokens = [self.max_tokens[idx] for idx in keep]
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1424:            if self._num_tokens[i] >= self.max_tokens[i]:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1442:                        prompt_cache=self.extract_cache(i),
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1456:                        prompt_cache=None,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1477:            prompt_cache=[],
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1481:            max_tokens=[],
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1490:    This class provides automatic management of prompt processing and generation
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1493:    It also allows for segmented prompt processing which guarantees that the
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1501:        max_tokens: int = 128,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1514:        self.max_tokens = max_tokens
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1530:        self._prompt_batch = PromptProcessingBatch.empty(
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1539:        self._prompt_tokens_counter = 0
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1540:        self._prompt_time_counter = 0
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1544:        if mx.metal.is_available():
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1567:        self._prompt_tokens_counter = 0
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1568:        self._prompt_time_counter = 0
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1576:            gen_time = total_time - self._prompt_time_counter
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1577:            stats.prompt_tokens += self._prompt_tokens_counter
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1578:            stats.prompt_time += self._prompt_time_counter
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1579:            stats.prompt_tps = stats.prompt_tokens / stats.prompt_time
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1583:            stats.peak_memory = max(stats.peak_memory, mx.get_peak_memory() / 1e9)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1587:        prompts: List[List[int]],
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1588:        max_tokens: Optional[List[int]] = None,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1598:            [[p] for p in prompts],
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1599:            max_tokens,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1610:        max_tokens: Optional[List[int]] = None,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1621:        max_tokens = max_tokens or [self.max_tokens] * len(segments)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1638:            max_tokens,
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1659:            return cache.make_prompt_cache(self.model)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1667:            for ci in cache.make_prompt_cache(self.model)
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1676:        for i, uid_i in enumerate(self._prompt_batch.uids):
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1691:                    self._prompt_batch.extract_cache(idx),
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1692:                    self._prompt_batch.tokens[idx],
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1701:    def remove(self, uids, return_prompt_caches=False):
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1703:        if return_prompt_caches:
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1708:            set(range(len(self._prompt_batch))),
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1718:        if len(keep[1]) < len(self._prompt_batch):
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:1719:            self._prompt_batch.filter(sorted(keep[1]))

exec
/bin/zsh -lc 'rg -n "Qwen3-4B-4bit|jw_mixed_v1_sentinel|max_tokens|output policy|greedy|temperature|mlx_lm" docs/run_reports/2026-07-17-window-a-floors.md docs/run_reports/2026-07-30-sweep-mechanisms.md configs experiments joulewise scripts tests 2>/dev/null | head -260; rg -n "memory|peak_memory|mx.get_peak_memory|reset_peak_memory" joulewise scripts docs/run_reports/2026-07-07-flagship-qwen35-122b.md 2>/dev/null | head -200; rg -n "4.hour|four.hour|20% margin|campaign envelope|timing probe" docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md docs/strategy/2026-08-07-paper-portfolio/reviews/rev-moe-routing-energy.md docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md | head -200' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
docs/run_reports/2026-07-17-window-a-floors.md:233:Qwen3.5-122B-A10B INT4 on the five-item `jw_mixed_v1_sentinel` shape. Every
docs/run_reports/2026-07-17-window-a-floors.md:269:baseline greedy 113.0 tok/s. Thinking mode was engaged and outputs were
docs/run_reports/2026-07-30-sweep-mechanisms.md:53:| Spec decode on/off | Qwen2.5-7B (or Qwen3-8B) alone | same + 0.5B/0.6B draft | ~4.4 GB | **Verified**: `mlx_lm.generate --draft-model` exists ([issue #250](https://github.com/ml-explore/mlx-lm/issues/250), [#1132](https://github.com/ml-explore/mlx-lm/issues/1132)) |
docs/run_reports/2026-07-30-sweep-mechanisms.md:56:| MoE vs dense (matched active, same family) | mlx-community/Qwen3-30B-A3B-4bit (**verified exists**) | Qwen3-4B-4bit | ~17 GB vs ~2.3 GB | Qwen3-MoE runs widely in mlx-lm (checkpoint verified; arch file not individually confirmed — *low risk*) |
docs/run_reports/2026-07-30-sweep-mechanisms.md:94:Sources: [2605.11999](https://arxiv.org/abs/2605.11999) · [2504.17674](https://arxiv.org/abs/2504.17674) · [2606.21428](https://arxiv.org/abs/2606.21428) · [2411.13157](https://arxiv.org/abs/2411.13157) · [2510.26692](https://arxiv.org/abs/2510.26692) · [2601.22076](https://arxiv.org/html/2601.22076v1) · [2512.03024](https://arxiv.org/html/2512.03024v1) · [2504.03360](https://arxiv.org/pdf/2504.03360) · [2401.18079](https://arxiv.org/pdf/2401.18079) · [2405.06219](https://arxiv.org/pdf/2405.06219) · [mlx-lm models](https://github.com/ml-explore/mlx-lm/tree/main/mlx_lm/models) · [mlx-lm #250](https://github.com/ml-explore/mlx-lm/issues/250) · [mlx-lm #1132](https://github.com/ml-explore/mlx-lm/issues/1132) · [mlx-examples #1075](https://github.com/ml-explore/mlx-examples/commit/85ffd2c96a45a8cb900f95a2ded61d858d673399)
tests/test_controller.py:1284:        self.assertEqual(metadata["thermal_pre"]["temperature_c"], 42.0)
tests/test_controller.py:1285:        self.assertEqual(metadata["thermal_post"]["temperature_c"], 42.0)
configs/analysis_registry/ap_spec_native_mtp_front.v2.json:195:  "selection_scope": "One mock target stack, one fixed request roster, one exact output policy, one single-request policy, and one native-MTP off/on pair."
scripts/axi_sc_spec_decode_spike.py:52:RUNTIME_CALLBACK_SOURCE = "mlx_lm.speculative_decode_callback"
scripts/axi_sc_spec_decode_spike.py:120:        top_level = "mlx_lm" if name == "mlx-lm" else "mlx"
scripts/axi_sc_spec_decode_spike.py:134:            "reason": "mlx_lm_package_root_missing",
scripts/axi_sc_spec_decode_spike.py:277:        "max_tokens": args.max_tokens,
scripts/axi_sc_spec_decode_spike.py:739:            import mlx_lm
scripts/axi_sc_spec_decode_spike.py:800:            target_model, target_tokenizer = mlx_lm.load(args.target_model)
scripts/axi_sc_spec_decode_spike.py:801:            draft_model, draft_tokenizer = mlx_lm.load(args.draft_model)
scripts/axi_sc_spec_decode_spike.py:823:    callback_available = _has_explicit_runtime_callback(mlx_lm.stream_generate)
scripts/axi_sc_spec_decode_spike.py:885:                "max_tokens": args.max_tokens,
scripts/axi_sc_spec_decode_spike.py:893:            responses = mlx_lm.stream_generate(
scripts/axi_sc_spec_decode_spike.py:1074:        probe="pinned_mlx_lm_spec_decode",
scripts/axi_sc_spec_decode_spike.py:1099:    mlx_lm_root = next(
scripts/axi_sc_spec_decode_spike.py:1102:    source_surface = _source_surface_record(mlx_lm_root)
scripts/axi_sc_spec_decode_spike.py:1190:        str(args.max_tokens),
scripts/axi_sc_spec_decode_spike.py:1379:    if args.max_tokens <= 0:
configs/analysis_registry/ap_spec_draft_front.v2.json:195:  "selection_scope": "One mock target stack, one fixed request roster, one exact output policy, one single-request policy, and one draft-model off/on pair."
tests/test_mint_floor_artifact.py:73:        "sampler_output_policy": "greedy",
tests/test_mint_floor_artifact.py:199:        prepare.pop("mlx_lm_version", None)
tests/test_axi_sb_spike.py:94:            max_tokens=2,
tests/test_axi_sb_spike.py:121:        self.assertNotIn("mlx_lm", spike.__dict__)
tests/test_axi_sb_spike.py:190:            max_tokens=2,
tests/test_axi_sb_spike.py:209:            max_tokens=2,
tests/test_axi_sb_spike.py:235:                max_tokens=2,
tests/test_axi_sb_spike.py:265:                max_tokens=2,
tests/test_axi_sb_spike.py:304:                max_tokens=2,
tests/test_axi_sb_spike.py:400:        mlx_lm = ModuleType("mlx_lm")
tests/test_axi_sb_spike.py:401:        mlx_lm.__path__ = []  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:402:        mlx_lm.load = lambda _model: (fake_model, FakeTokenizer())  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:403:        mlx_lm_generate = ModuleType("mlx_lm.generate")
tests/test_axi_sb_spike.py:404:        mlx_lm_generate.BatchGenerator = FakeBatchGenerator  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:405:        mlx_lm.generate = mlx_lm_generate  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:411:            "mlx_lm": mlx_lm,
tests/test_axi_sb_spike.py:412:            "mlx_lm.generate": mlx_lm_generate,
tests/test_axi_sb_spike.py:414:        args = SimpleNamespace(model="/fake/model", batch_size=2, max_tokens=2)
tests/test_axi_sb_spike.py:430:                max_tokens=2,
joulewise/gensuite/__init__.py:384:    """Grow coarse units, then full-re-encode greedy-fill to exact shape."""
joulewise/gensuite/__init__.py:996:def _ascii_tail_candidates(tokenizer: TokenizerProtocol, max_tokens: int) -> list[str]:
joulewise/gensuite/__init__.py:1000:        if tail and len(_encode(tokenizer, tail, add_special_tokens=False)) > max_tokens:
joulewise/gensuite/__init__.py:1606:        "suite": "jw_mixed_v1_sentinel",
joulewise/gensuite/__init__.py:1641:    suite_profile = f"jw_mixed_v1_sentinel_{prompt_budget}_{output_budget}"
joulewise/gensuite/__init__.py:1643:        suite_id="jw_mixed_v1_sentinel",
scripts/mint_floor_artifact.py:344:        or prepare.get("mlx_lm_version")
tests/test_axi_sc_spike.py:28:        "generate_path": "/fake/mlx_lm/generate.py",
tests/test_axi_sc_spike.py:31:        "qwen3_5_path": "/fake/mlx_lm/models/qwen3_5.py",
tests/test_axi_sc_spike.py:54:        max_tokens=4,
tests/test_axi_sc_spike.py:224:            max_tokens=4,
tests/test_axi_sc_spike.py:258:        self.assertNotIn("mlx_lm", spike.__dict__)
tests/test_axi_sc_spike.py:442:                max_tokens=4,
tests/test_axi_sc_spike.py:476:                max_tokens=4,
tests/test_axi_sc_spike.py:506:            max_tokens=4,
tests/test_axi_sc_spike.py:559:        mlx_lm = ModuleType("mlx_lm")
tests/test_axi_sc_spike.py:560:        mlx_lm.load = fake_load  # type: ignore[attr-defined]
tests/test_axi_sc_spike.py:561:        mlx_lm.stream_generate = fake_stream_generate  # type: ignore[attr-defined]
tests/test_axi_sc_spike.py:562:        modules = {"mlx": mlx, "mlx.core": mlx_core, "mlx_lm": mlx_lm}
tests/test_axi_sc_spike.py:568:            max_tokens=2,
tests/test_axi_sc_spike.py:643:        mlx_lm = ModuleType("mlx_lm")
tests/test_axi_sc_spike.py:644:        mlx_lm.load = fake_load  # type: ignore[attr-defined]
tests/test_axi_sc_spike.py:645:        mlx_lm.stream_generate = fake_stream_generate  # type: ignore[attr-defined]
tests/test_axi_sc_spike.py:646:        modules = {"mlx": mlx, "mlx.core": mlx_core, "mlx_lm": mlx_lm}
tests/test_axi_sc_spike.py:652:            max_tokens=4,
tests/test_mock_adapters.py:766:        self.assertEqual(state.temperature_c, 42.0)
tests/test_mock_adapters.py:880:    def test_resolves_mlx_runtime_adapter_without_importing_mlx_lm(self) -> None:
joulewise/cli.py:985:        and generator.get("name") == "mlx_lm.stream_generate"
tests/test_audit_reduce_degenerate.py:130:            thermal_pre={"timestamp_s": 0.0, "temperature_c": "hot"},
tests/test_audit_reduce_degenerate.py:131:            thermal_post={"timestamp_s": 2.0, "temperature_c": 42.0},
scripts/build_capstone.py:234:token counts are retained for audit, but runtime stop reason and output policy
tests/test_suite_control_parity.py:341:        max_tokens: int = 256,
tests/test_suite_control_parity.py:349:        for index, piece in enumerate(pieces[:max_tokens]):
tests/test_suite_control_parity.py:437:        self.mlx._mlx_lm = LiteralMlxLm()
tests/test_suite_control_parity.py:525:            {"name": "mlx_lm.stream_generate", "version": "literal-mlx-1"},
joulewise/schemas.py:56:        "decode_emission_burst_size_max_tokens",
joulewise/schemas.py:2037:    burst_size_max_tokens: int | None
joulewise/schemas.py:2060:        if self.burst_size_max_tokens is not None and (
joulewise/schemas.py:2061:            not isinstance(self.burst_size_max_tokens, int)
joulewise/schemas.py:2062:            or isinstance(self.burst_size_max_tokens, bool)
joulewise/schemas.py:2063:            or self.burst_size_max_tokens < 1
joulewise/schemas.py:2065:            raise SchemaError("request_decode_metrics.burst_size_max_tokens invalid")
joulewise/schemas.py:2071:            self.burst_size_max_tokens,
joulewise/schemas.py:2091:    decode_emission_burst_size_max_tokens: int | None = None
joulewise/schemas.py:2137:        if self.decode_emission_burst_size_max_tokens is not None and (
joulewise/schemas.py:2138:            not isinstance(self.decode_emission_burst_size_max_tokens, int)
joulewise/schemas.py:2139:            or isinstance(self.decode_emission_burst_size_max_tokens, bool)
joulewise/schemas.py:2140:            or self.decode_emission_burst_size_max_tokens < 1
joulewise/schemas.py:2172:                "decode_emission_burst_size_max_tokens": {"type": ["integer", "null"], "minimum": 1},
joulewise/schemas.py:2195:                "burst_size_p50_tokens", "burst_size_p95_tokens", "burst_size_max_tokens",
joulewise/schemas.py:2210:                "burst_size_max_tokens": {"type": ["integer", "null"], "minimum": 1},
joulewise/schemas.py:2226:                        "decode_emission_burst_size_max_tokens", "request_decode_metrics",
tests/test_2k_amplification.py:168:            "query_fields": ["timestamp", "power.draw", "temperature.gpu"],
tests/test_2k_amplification.py:278:                    "query_fields": ["timestamp", "power.draw", "temperature.gpu"],
tests/test_2k_amplification.py:317:                    "query_fields": ["timestamp", "power.draw", "temperature.gpu"],
tests/test_axi_burst_reduce.py:508:        self.assertEqual(value["decode_emission_burst_size_max_tokens"], 3)
scripts/spike_mlx_prompt_cache.py:13:cache saved after ``max_tokens=0`` has already advanced through the full
scripts/spike_mlx_prompt_cache.py:97:        "mlx_lm_version": package_version("mlx-lm"),
scripts/spike_mlx_prompt_cache.py:104:    from mlx_lm.generate import generate_step
scripts/spike_mlx_prompt_cache.py:105:    from mlx_lm.models.cache import (
scripts/spike_mlx_prompt_cache.py:112:    from mlx_lm.utils import load
scripts/spike_mlx_prompt_cache.py:165:    max_tokens: int,
scripts/spike_mlx_prompt_cache.py:167:    validate_decode_tokens(max_tokens)
scripts/spike_mlx_prompt_cache.py:173:        max_tokens=max_tokens,
scripts/spike_mlx_prompt_cache.py:245:    for _ in generate_step(prompt_array, model, max_tokens=0, prompt_cache=prompt_cache):
scripts/spike_mlx_prompt_cache.py:510:        "mlx_lm_version": mono_meta.get("mlx_lm_version"),
tests/test_cli.py:177:                "mlx_lm.stream_generate"
tests/test_experiment.py:425:            temperature_c=42.0,
tests/test_detection_floor.py:326:        "sampler_output_policy": "greedy/max_new_tokens=64",
tests/test_env_locks.py:62:            "mlx-lm": prepare["mlx_lm_version"],
tests/test_vllm_runtime.py:284:            self.assertEqual(task["workload"]["sampling_params"]["temperature"], 0.0)
tests/test_vllm_runtime.py:287:            self.assertEqual(task["workload"]["sampling_params"]["max_tokens"], 3)
tests/test_corpus_strict_validation.py:180:                            "sampler": {"kind": "greedy"},
tests/test_analysis_ratio_integration.py:63:            "sampler": {"kind": "greedy", "temperature": 0.0},
tests/test_analysis_ratio_integration.py:202:            "output policy mismatch": (
tests/test_analysis_ratio_integration.py:278:                        "sampler": {"kind": "greedy", "temperature": 0.0},
tests/test_analysis_ratio_integration.py:413:                        "sampler": {"kind": "greedy"},
tests/test_publication_privacy.py:202:                "thermal_pre": {"temperature_c": 40.0},
tests/test_publication_privacy.py:203:                "thermal_post": {"temperature_c": 41.0},
tests/test_node_worker_subprocess.py:168:                                "max_tokens": 3,
tests/test_node_worker_subprocess.py:169:                                "temperature": 0.0,
tests/test_node_worker_subprocess.py:218:                                "temperature.gpu",
tests/test_node_worker_subprocess.py:240:                            "temperature.gpu",
tests/test_node_worker.py:45:            "query_fields": ["timestamp", "power.draw", "temperature.gpu"],
tests/test_node_worker.py:96:                "max_tokens": 3,
tests/test_node_worker.py:97:                "temperature": 0.0,
tests/test_node_worker.py:1171:                            "--query-gpu=timestamp,power.draw,temperature.gpu",
tests/test_node_worker.py:1194:                    "--query-gpu=timestamp,power.draw,temperature.gpu",
tests/test_analysis_engine.py:31:    policy_a: str = "greedy/max_new_tokens=200",
tests/test_analysis_engine.py:32:    policy_b: str = "greedy/max_new_tokens=200",
tests/test_analysis_engine.py:33:    stop_a: str = "max_tokens",
tests/test_analysis_engine.py:34:    stop_b: str = "max_tokens",
tests/test_analysis_engine.py:313:            "output policy": [replace_ratio(base[0], output_policy_b="sampling/temp=1"), base[1]],
tests/test_mlx_runtime.py:115:        max_tokens: int = 256,
tests/test_mlx_runtime.py:124:                "max_tokens": max_tokens,
tests/test_mlx_runtime.py:131:        for index, piece in enumerate(self.pieces[:max_tokens]):
tests/test_mlx_runtime.py:145:        max_tokens: int = 256,
tests/test_mlx_runtime.py:154:                "max_tokens": max_tokens,
tests/test_mlx_runtime.py:161:        for index, piece in enumerate(self.pieces[:max_tokens]):
tests/test_mlx_runtime.py:271:        adapter._mlx_lm = fake_mlx
tests/test_mlx_runtime.py:280:            raise ImportError("no module named mlx_lm")
tests/test_mlx_runtime.py:282:        adapter._import_mlx_lm = raise_import_error  # type: ignore[method-assign]
tests/test_mlx_runtime.py:304:        self.assertEqual(fake_mlx.calls[0]["max_tokens"], 2)
tests/test_mlx_runtime.py:410:                    ("mono_meta.json", {"mlx_lm_version": "test", "mlx_version": "test"}),
tests/test_mlx_runtime.py:497:                        "max_tokens": 3,
tests/test_mlx_runtime.py:546:        adapter._import_mlx_lm = lambda: fake_mlx  # type: ignore[method-assign]
tests/test_mlx_runtime.py:728:        adapter._mlx_lm = fake_mlx
tests/test_mlx_runtime.py:852:                max_tokens: int = 256,
tests/test_mlx_runtime.py:857:        adapter._mlx_lm = NoSamplerMlx(["A"])
tests/test_mlx_runtime.py:874:        adapter._mlx_lm = fake_mlx
tests/test_mlx_runtime.py:886:                "kind": "greedy",
tests/test_mlx_runtime.py:887:                "temperature": 0.0,
tests/test_mlx_runtime.py:889:                "reason": "mlx_lm sampler API unavailable",
tests/test_mlx_runtime.py:898:        adapter._mlx_lm = fake_mlx
tests/test_mlx_runtime.py:910:                "kind": "greedy",
tests/test_mlx_runtime.py:911:                "temperature": 0.0,
tests/test_mlx_runtime.py:913:                "reason": "mlx_lm sampler API unavailable",
tests/test_mlx_runtime.py:923:        adapter._mlx_lm = BadSamplerMlx(["A"])
tests/test_mlx_runtime.py:935:                "kind": "greedy",
tests/test_mlx_runtime.py:936:                "temperature": 0.0,
tests/test_mlx_runtime.py:938:                "reason": "mlx_lm sampler API unavailable",
tests/test_mlx_runtime.py:941:                    "temperature: unsupported sampler form",
tests/test_mlx_runtime.py:950:        adapter._mlx_lm = fake_mlx
tests/test_mlx_runtime.py:962:        self.assertEqual(workload.workload_provenance["sampler"]["kind"], "greedy")
tests/test_mlx_runtime.py:963:        self.assertEqual(workload.workload_provenance["sampler"]["temperature"], 0.0)
tests/test_mlx_runtime.py:973:        # Installed mlx_lm exposes make_sampler under sample_utils, not
tests/test_mlx_runtime.py:979:        adapter._mlx_lm = fake_mlx
tests/test_mlx_runtime.py:986:        self.assertEqual(sampler["api"], "mlx_lm.sample_utils.make_sampler")
tests/test_mlx_runtime.py:995:        adapter._mlx_lm = fake_mlx
tests/test_mlx_runtime.py:1048:        adapter._mlx_lm = fake_mlx
tests/test_nvidia_smi.py:148:        self.assertEqual([row.temperature_c for row in rows], [40.0, 41.0, 43.0])
tests/test_nvidia_smi.py:221:        self.assertEqual(metadata["query_fields"], ["timestamp", "power.draw", "temperature.gpu"])
tests/test_nvidia_smi.py:347:            self.assertEqual(thermal.temperature_c, 43.0)
tests/test_nvidia_smi.py:450:        self.assertIsNone(thermal.temperature_c)
tests/test_nvidia_smi.py:451:        self.assertFalse(thermal.metadata["temperature_c_available"])
tests/test_axi_schemas.py:72:        burst_size_max_tokens=2,
tests/test_axi_schemas.py:114:        decode_emission_burst_size_max_tokens=2,
joulewise/adapters/mock_telemetry.py:159:            temperature_c=42.0,
tests/goldens/axi_summary_v061.json:10:  "decode_emission_burst_size_max_tokens": 2,
tests/goldens/axi_summary_v061.json:83:      "burst_size_max_tokens": 2,
scripts/make_figures.py:505:            "token_companion_status": "omitted: runtime stop reason and output policy unavailable",
scripts/make_figures.py:608:             "reason": "legacy bundles predate captured tokenizer identity, sampler/output policy, and stop-reason provenance; values remain explicitly tokenizer-unknown L1 descriptors and support no ranking"},
tests/test_powermetrics.py:221:    def test_thermal_pressure_without_temperature(self) -> None:
tests/test_powermetrics.py:228:        self.assertIsNone(state.temperature_c)
tests/goldens/axi_summary_v062.json:10:  "decode_emission_burst_size_max_tokens": 2,
tests/goldens/axi_summary_v062.json:83:      "burst_size_max_tokens": 2,
tests/goldens/mock_axi_spec_summary_oracle.json:10:  "decode_emission_burst_size_max_tokens": 2,
tests/goldens/mock_axi_spec_summary_oracle.json:26:      "burst_size_max_tokens": 2,
scripts/axi_sb_static_batch_spike.py:79:        top_level = "mlx_lm" if name == "mlx-lm" else "mlx"
scripts/axi_sb_static_batch_spike.py:453:            import mlx_lm
scripts/axi_sb_static_batch_spike.py:454:            from mlx_lm.generate import BatchGenerator
scripts/axi_sb_static_batch_spike.py:487:            model, tokenizer = mlx_lm.load(args.model)
scripts/axi_sb_static_batch_spike.py:508:            max_tokens=args.max_tokens,
scripts/axi_sb_static_batch_spike.py:514:        uids = generator.insert(prompt_ids, [args.max_tokens] * args.batch_size)
scripts/axi_sb_static_batch_spike.py:745:        probe="pinned_mlx_lm_static_batch",
scripts/axi_sb_static_batch_spike.py:748:        max_tokens=args.max_tokens,
scripts/axi_sb_static_batch_spike.py:796:        str(args.max_tokens),
scripts/axi_sb_static_batch_spike.py:948:    if args.max_tokens <= 0:
tests/goldens/axi_summary_v060.json:10:  "decode_emission_burst_size_max_tokens": 2,
tests/goldens/axi_summary_v060.json:66:      "burst_size_max_tokens": 2,
tests/test_reduce.py:372:            extra["thermal_pre"] = {"timestamp_s": 0.0, "temperature_c": thermal_pre_c}
tests/test_reduce.py:374:            extra["thermal_post"] = {"timestamp_s": 0.0, "temperature_c": thermal_post_c}
tests/fixtures/axi_valid_burst/summary_metrics.json:10:  "decode_emission_burst_size_max_tokens": 2,
tests/fixtures/axi_valid_burst/summary_metrics.json:83:      "burst_size_max_tokens": 2,
joulewise/adapters/powermetrics.py:1107:            temperature_c=None,
joulewise/adapters/powermetrics.py:1109:            metadata={"source": "powermetrics", "temperature_c_available": False},
tests/test_gensuite.py:529:            self.assertEqual(sentinel["suite_profile"], "jw_mixed_v1_sentinel_640_128")
tests/test_gensuite.py:532:                "jw_mixed_v1_sentinel_640_128",
joulewise/interfaces.py:330:    temperature_c: float | None = None
joulewise/adapters/nvidia_smi.py:40:QUERY_FIELDS = ["timestamp", "power.draw", "temperature.gpu"]
joulewise/adapters/nvidia_smi.py:58:    temperature_c: float
joulewise/adapters/nvidia_smi.py:72:        self._last_temperature_c: float | None = None
joulewise/adapters/nvidia_smi.py:214:            temperature_c=self._last_temperature_c,
joulewise/adapters/nvidia_smi.py:218:                "temperature_c_available": self._last_temperature_c is not None,
joulewise/adapters/nvidia_smi.py:267:        self._last_temperature_c = last.temperature_c
joulewise/adapters/nvidia_smi.py:444:            temperature_c = float(parts[2])
joulewise/adapters/nvidia_smi.py:451:        if not math.isfinite(power_w) or not math.isfinite(temperature_c):
joulewise/adapters/nvidia_smi.py:457:                temperature_c=temperature_c,
joulewise/reduce.py:295:    pre_temp = pre.get("temperature_c")
joulewise/reduce.py:296:    post_temp = post.get("temperature_c")
joulewise/reduce.py:301:            finite_float(post_temp, "thermal_post.temperature_c")
joulewise/reduce.py:302:            - finite_float(pre_temp, "thermal_pre.temperature_c")
joulewise/reduce.py:3098:                burst_size_max_tokens=request_bursts[3],
joulewise/reduce.py:3354:        decode_emission_burst_size_max_tokens=bundle_bursts[3],
joulewise/adapters/vllm_runtime.py:51:    "temperature": 0.0,
joulewise/adapters/vllm_runtime.py:231:        sampling_params["max_tokens"] = output_tokens
joulewise/adapters/node_worker.py:50:NVIDIA_SMI_QUERY = "timestamp,power.draw,temperature.gpu"
joulewise/adapters/node_worker.py:270:        "warmup_max_tokens": VLLM_WARMUP_MAX_TOKENS,
joulewise/adapters/node_worker.py:275:        "max_tokens": VLLM_WARMUP_MAX_TOKENS,
joulewise/adapters/node_worker.py:276:        "temperature": 0.0,
joulewise/adapters/node_worker.py:321:    max_tokens = _positive_int_or_default(workload.get("output_tokens"), 1)
joulewise/adapters/node_worker.py:323:    sampling_params["max_tokens"] = _positive_int_or_default(
joulewise/adapters/node_worker.py:324:        sampling_params.get("max_tokens"),
joulewise/adapters/node_worker.py:325:        max_tokens,
joulewise/adapters/node_worker.py:340:        "requested_output_tokens": max_tokens,
joulewise/adapters/node_worker.py:376:                "requested_output_tokens": max_tokens,
joulewise/adapters/node_worker.py:407:                                    "requested_output_tokens": max_tokens,
joulewise/adapters/node_worker.py:466:                    "requested_output_tokens": max_tokens,
joulewise/adapters/node_worker.py:480:                "requested_output_tokens": max_tokens,
joulewise/adapters/mlx_runtime.py:4:and ``mlx_lm`` is imported only inside ``prepare``. Tests exercise the workload
joulewise/adapters/mlx_runtime.py:72:    """RuntimeAdapter implementation backed by ``mlx_lm``."""
joulewise/adapters/mlx_runtime.py:78:        self._mlx_lm: Any | None = None
joulewise/adapters/mlx_runtime.py:100:            mlx_lm = self._import_mlx_lm()
joulewise/adapters/mlx_runtime.py:125:            loaded = mlx_lm.load(
joulewise/adapters/mlx_runtime.py:142:        self._mlx_lm = mlx_lm
joulewise/adapters/mlx_runtime.py:148:            "mlx_lm_version": _module_or_distribution_version(mlx_lm, "mlx-lm"),
joulewise/adapters/mlx_runtime.py:168:        if self._mlx_lm is None or self._model is None or self._tokenizer is None:
joulewise/adapters/mlx_runtime.py:176:            for _ in self._mlx_lm.stream_generate(
joulewise/adapters/mlx_runtime.py:180:                max_tokens=WARMUP_TOKENS,
joulewise/adapters/mlx_runtime.py:194:        if self._mlx_lm is None or self._model is None or self._tokenizer is None:
joulewise/adapters/mlx_runtime.py:197:        max_tokens = config.workload_profile.output_tokens or DEFAULT_OUTPUT_TOKENS
joulewise/adapters/mlx_runtime.py:205:            max_tokens,
joulewise/adapters/mlx_runtime.py:226:                    "name": "mlx_lm.stream_generate",
joulewise/adapters/mlx_runtime.py:227:                    "version": _module_or_distribution_version(self._mlx_lm, "mlx-lm"),
joulewise/adapters/mlx_runtime.py:241:                        requested_tokens=max_tokens,
joulewise/adapters/mlx_runtime.py:245:                    requested_tokens=max_tokens,
joulewise/adapters/mlx_runtime.py:261:        if self._mlx_lm is None or self._model is None or self._tokenizer is None:
docs/run_reports/2026-07-07-flagship-qwen35-122b.md:6:linearly with ACTIVE parameter count" and showed "textbook memory-bound MoE
docs/run_reports/2026-07-07-flagship-qwen35-122b.md:28:tok/s decode, 68.9 GB peak memory — fits without any wired-limit change.
docs/run_reports/2026-07-07-flagship-qwen35-122b.md:63:textbook memory-bound MoE behavior and exactly the kind of
joulewise/environment.py:189:        "memory_free_percent": None,
joulewise/environment.py:190:        "memory_pressure_percent": None,
joulewise/environment.py:191:        "memory": {
joulewise/environment.py:250:    ``memory_pressure_percent`` is derived from a free-memory percentage when
joulewise/environment.py:251:    available; it is a pressure proxy, not the kernel's memorystatus level.
joulewise/environment.py:280:    memory_ok = _apply_command(
joulewise/environment.py:283:        "memory_pressure",
joulewise/environment.py:284:        ["memory_pressure", "-Q"],
joulewise/environment.py:285:        _parse_memory_pressure,
joulewise/environment.py:288:    if not memory_ok:
joulewise/environment.py:692:def _parse_memory_pressure(snapshot: dict[str, Any], text: str) -> None:
joulewise/environment.py:693:    match = re.search(r"System-wide memory free percentage:\s*(\d+(?:\.\d+)?)%", text)
joulewise/environment.py:695:        raise ValueError("memory free percentage not found")
joulewise/environment.py:697:    snapshot["memory_free_percent"] = free_percent
joulewise/environment.py:698:    snapshot["memory_pressure_percent"] = 100.0 - free_percent
joulewise/environment.py:709:    snapshot["memory_free_percent"] = free_percent
joulewise/environment.py:710:    snapshot["memory_pressure_percent"] = 100.0 - free_percent
joulewise/environment.py:734:    memory = snapshot["memory"]
joulewise/environment.py:736:    memory["page_size_bytes"] = page_size
joulewise/environment.py:737:    memory["pages_free"] = counters.get("Pages free")
joulewise/environment.py:738:    memory["pageins"] = counters.get("Pageins")
joulewise/environment.py:739:    memory["pageouts"] = counters.get("Pageouts")
joulewise/environment.py:740:    memory["pages_occupied_by_compressor"] = counters.get("Pages occupied by compressor")
joulewise/environment.py:741:    memory["pages_stored_in_compressor"] = counters.get("Pages stored in compressor")
joulewise/environment.py:742:    if page_size is not None and memory["pages_occupied_by_compressor"] is not None:
joulewise/environment.py:743:        memory["compressor_bytes"] = memory["pages_occupied_by_compressor"] * page_size
joulewise/environment.py:753:    snapshot["memory"]["swap_usage"] = {
scripts/generate_matrix.py:9:The Slice 2M footnote's target-memory cap is out of scope for this static
scripts/generate_matrix.py:11:memory-driven caps must be pre-applied by the operator in the base config.
joulewise/calibration_ledger.py:277:    """Deterministic, authenticated genesis bootstrap prepared in memory."""
scripts/axi_sb_static_batch_spike.py:685:        peak_memory_bytes = int(mx.get_peak_memory())
scripts/axi_sb_static_batch_spike.py:687:        peak_memory_bytes = None
scripts/axi_sb_static_batch_spike.py:690:        "memory_fit_observation",
scripts/axi_sb_static_batch_spike.py:693:        peak_memory_bytes=peak_memory_bytes,
joulewise/adapters/powermetrics.py:178:        This is an in-memory controller seam: it does not replace or alter the
joulewise/adapters/vllm_runtime.py:222:                "gpu_memory_utilization": DEFAULT_GPU_MEMORY_UTILIZATION,
joulewise/adapters/node_worker.py:81:    "cuda out of memory",
joulewise/adapters/node_worker.py:82:    "outofmemoryerror",
joulewise/adapters/node_worker.py:83:    "out of memory",
joulewise/adapters/node_worker.py:85:    "cuda error: memory allocation",
joulewise/adapters/node_worker.py:227:                ready.get("message", "vLLM server failed with out-of-memory evidence"),
joulewise/adapters/node_worker.py:290:                "vLLM warmup failed with out-of-memory evidence",
joulewise/adapters/node_worker.py:494:                "vLLM workload failed with out-of-memory evidence",
joulewise/adapters/node_worker.py:923:        "gpu_memory_utilization": "--gpu-memory-utilization",
joulewise/calibration_bracketing.py:470:    """Authenticate an in-memory artifact against the checked-in byte pin."""
joulewise/whole_window.py:383:    bound from primary evidence, and memoizes every in-memory member
joulewise/whole_window.py:730:        """Return the operative in-memory summary only after full discharge."""
joulewise/whole_window.py:2731:        # returns an in-memory summary.  Minutes-scale claim verification cost
joulewise/reduce.py:2701:    """Re-run the mint reducer in memory under one authenticated wider bound.
joulewise/adapters/mlx_runtime.py:162:        metadata["memory_snapshots"] = [self._memory_snapshot("prepare_end")]
joulewise/adapters/mlx_runtime.py:731:        metadata = {"memory_snapshots": [self._memory_snapshot("cleanup_start")]}
joulewise/adapters/mlx_runtime.py:739:    def _memory_snapshot(self, label: str) -> dict[str, Any]:
joulewise/adapters/mlx_runtime.py:745:            "mlx_metal": _mlx_metal_memory(errors),
joulewise/adapters/mlx_runtime.py:1186:    except Exception as exc:  # noqa: BLE001 - memory metadata must be fail-soft.
joulewise/adapters/mlx_runtime.py:1200:def _mlx_metal_memory(errors: dict[str, str]) -> dict[str, Any]:
joulewise/adapters/mlx_runtime.py:1203:        "active_memory_bytes": None,
joulewise/adapters/mlx_runtime.py:1204:        "cache_memory_bytes": None,
joulewise/adapters/mlx_runtime.py:1205:        "peak_memory_bytes": None,
joulewise/adapters/mlx_runtime.py:1212:    except Exception as exc:  # noqa: BLE001 - memory metadata must be fail-soft.
joulewise/adapters/mlx_runtime.py:1218:        "api_available": metal is not None or callable(getattr(mx, "get_active_memory", None)),
joulewise/adapters/mlx_runtime.py:1219:        "active_memory_bytes": None,
joulewise/adapters/mlx_runtime.py:1220:        "cache_memory_bytes": None,
joulewise/adapters/mlx_runtime.py:1221:        "peak_memory_bytes": None,
joulewise/adapters/mlx_runtime.py:1225:        ("get_active_memory", "active_memory_bytes"),
joulewise/adapters/mlx_runtime.py:1226:        ("get_cache_memory", "cache_memory_bytes"),
joulewise/adapters/mlx_runtime.py:1227:        ("get_peak_memory", "peak_memory_bytes"),
joulewise/controller.py:18:  memory and flush only after ``stop_sampling``; inside the MARKER-bounded
joulewise/controller.py:22:  (no file writes, no disk event appends, no logging; the two in-memory
joulewise/controller.py:49:on-disk artifacts (D-002): events are never handed to it in memory.
joulewise/controller.py:2633:    in-memory evidence rather than re-opening the derived bundle artifact.
joulewise/analysis_engine/inputs.py:1277:        # supply an in-memory artifact and a descriptor base directory.  Root
joulewise/analysis_engine/inputs.py:2842:                    # authority.  Claim math consumes this in-memory widened
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:1437:| Q1 | MET-WINDOW-C-01 | P1 Phase Gate | BLOCKED — FROZEN-PLAN-READINESS-RECORD (A reviewed FROZEN-PLAN READINESS RECORD exists before any collection night: frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight, launcher-verified), ED-5A (Ed section-5A window prep FRESH POST-MOVE (the 2026-08-02 laptop move invalidated settled-machine conditions; network time off, AC, settled machine, walk-away)) [QUIET-MAC] | Execute a reviewed fresh-claim collection plan beginning with Window C: no Window B member enters a replacement claim basis; split prospectively across windows C and D if the complete replacement cannot fit the 2-4 hour envelope with at least 20 percent failure margin. | The fresh-claim metrology plan replaces every still-desired Window-B claim component without using any Window-B member, under reviewed frozen-plan and validated-window controls. Evidence: A fresh-claim plan recollects every still-desired Window-B claim component beginning with Window C; no Window B member enters a replacement claim basis; The fresh plan includes the still-required C2, C4, and C5 collection scope under the frozen-plan discipline, split prospectively across windows C and D if one window cannot retain at least 20 percent failure margin inside the runbook's 2-4 hour envelope; Window operated under the validated protocols: bird-SIGSTOP with identity custody, guarded launcher, one-line arm messages with zero output streaming during idle-gate exposure, third-failure salvage rule; Whole-window verdict emitted by machinery that has passed MET-VERDICT-ADJ-01 adjudication; supersessions recorded once, pre-verdict; both roots backed up rc=0. Authority: [D-113 clauses 7-9 fresh-claim reset, readiness fence, and prospective C/D split](docs/decision_log.md). Acceptance: [MET-WINDOW-C-01 acceptance](docs/process/state_kernel.json). Fence: A window-C dangler seeking the b-ii mechanical license before D100-BII-BINDING-01 closes RETURNS TO THE GATE; the window itself may run (D-106 revisit clause). Fence: Before any collection night, the ordinary launcher verifies a reviewed FROZEN-PLAN READINESS RECORD binding the frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight (D-113 clauses 8-9 hard start fence). Fence: Plan root assembled and frozen before measurement; no plan edits after freeze (D-096 frozen-plan ratification). Fence: Zero agents AND zero operator output streaming during measurement idle gates; arm messages are one line; bird-SIGSTOP protocol with identity custody and fail-safe CONT trap on all exit paths (2026-08-01 run report: streaming-during-idle-gate hazard + bird-SIGSTOP protocol). Note: D-113 clauses 7 and 9: the former remainder-only scope is SUPERSEDED. A fresh-claim plan is required; no Window B member enters a replacement claim basis. If the full replacement exceeds the runbook's 2-4 hour envelope with at least 20 percent margin, split it prospectively across windows C and D. |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:1510:| Q1 | MET-WINDOW-C-01 | P1 Phase Gate | BLOCKED — FROZEN-PLAN-READINESS-RECORD (A reviewed FROZEN-PLAN READINESS RECORD exists before any collection night: frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight, launcher-verified), ED-5A (Ed section-5A window prep FRESH POST-MOVE (the 2026-08-02 laptop move invalidated settled-machine conditions; network time off, AC, settled machine, walk-away)) | Execute a reviewed fresh-claim collection plan beginning with Window C: no Window B member enters a replacement claim basis; split prospectively across windows C and D if the complete replacement cannot fit the 2-4 hour envelope with at least 20 percent failure margin. | The fresh-claim metrology plan replaces every still-desired Window-B claim component without using any Window-B member, under reviewed frozen-plan and validated-window controls. Evidence: A fresh-claim plan recollects every still-desired Window-B claim component beginning with Window C; no Window B member enters a replacement claim basis; The fresh plan includes the still-required C2, C4, and C5 collection scope under the frozen-plan discipline, split prospectively across windows C and D if one window cannot retain at least 20 percent failure margin inside the runbook's 2-4 hour envelope; Window operated under the validated protocols: bird-SIGSTOP with identity custody, guarded launcher, one-line arm messages with zero output streaming during idle-gate exposure, third-failure salvage rule; Whole-window verdict emitted by machinery that has passed MET-VERDICT-ADJ-01 adjudication; supersessions recorded once, pre-verdict; both roots backed up rc=0. Authority: [D-113 clauses 7-9 fresh-claim reset, readiness fence, and prospective C/D split](docs/decision_log.md). Acceptance: [MET-WINDOW-C-01 acceptance](docs/process/state_kernel.json). Fence: A window-C dangler seeking the b-ii mechanical license before D100-BII-BINDING-01 closes RETURNS TO THE GATE; the window itself may run (D-106 revisit clause). Fence: Before any collection night, the ordinary launcher verifies a reviewed FROZEN-PLAN READINESS RECORD binding the frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight (D-113 clauses 8-9 hard start fence). Fence: Plan root assembled and frozen before measurement; no plan edits after freeze (D-096 frozen-plan ratification). Fence: Zero agents AND zero operator output streaming during measurement idle gates; arm messages are one line; bird-SIGSTOP protocol with identity custody and fail-safe CONT trap on all exit paths (2026-08-01 run report: streaming-during-idle-gate hazard + bird-SIGSTOP protocol). Note: D-113 clauses 7 and 9: the former remainder-only scope is SUPERSEDED. A fresh-claim plan is required; no Window B member enters a replacement claim basis. If the full replacement exceeds the runbook's 2-4 hour envelope with at least 20 percent margin, split it prospectively across windows C and D. |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:2427:The stage allowances incorporate the configured 30-second idle, warmup/teardown, stage arm overhead, and cooldown conventions. The pre-calibration allowance includes the required 180-second post-admin settle. The separate ten-minute untouched quiet-idle gate is added before applying the 20% margin.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:2606:No live timings, calibration observations, successor generation, or mint replay were performed. Runtime estimates therefore inherit historical-machine variance; the 20% margin is the current mitigation.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5036:Science runs ~1.7–2.0 min/member. The 4 h ceiling with the mandatory 20% margin caps
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5217:timing probe gives 512-token generation at **2.05 s (1.5B)** and **6.40 s (7B)**
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5478:existence**. Its own kill criterion ("cannot fit within four hours including 20% margin") is likely
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:6014:science before references, NEG-8 corpus, and 20% margin — and P2-019 additionally requires an
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:6263:NEG8 + 21 references + 10 untouched idle ≈ 69 min; 20% margin):
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:6270:  the proposal's own stated kill line of four hours, and now with a halved block
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:6440:| 3.14 / 3.24 / 2.80 h occupancies | **VERIFIED exactly** | DESIGN-MEMO budget table (188.4 / 194.4 / 168.0 min with 20% margin). |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:6674:20% margin") is the right guard, but it is stated as a risk rather than priced — and the
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9300:claim window requires a controlled quiet environment, zero background activity, 2–4 hours,
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9567:- the multi-arm window cannot fit under four hours with 20% margin;
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9627:- the multi-arm window cannot fit under four hours with 20% margin;
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:9992:JouleWise currently has a complete paper structure but no live claim-bearing values: historical windows establish the rules and supply design diagnostics, while D-117 requires three fresh prospective windows. The 1.5B floor window contains 10 absolute members and 10 four-member null-ABBA blocks; the 7B floor window repeats that 50-bundle design; both obtain prefill floors from the same bundles at zero additional runtime. The contrast window contains ten 1.5B/7B decode ABBA blocks. Their budgeted durations, including calibration, NEG8 bounds, references, untouched idle, and 20% margin, are 3.14, 3.24, and 2.80 hours respectively. Before any night, desk work must land the two-slot live-calibration ledger session, D-102 acceptance-successor machinery, prefill-capable four-cell mint, three frozen campaign packs, synthetic live-ledger regression, extraction specifications, and readiness packet. After the floor windows pass, mint the combined 1.5B/7B decode-and-prefill floor artifact; after the contrast passes, apply the two distinct claim gates and populate the MVP manuscript.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10026:Kill the ICPE upgrade before spending expansion nights if D-117 cannot mint valid floors; the 150-config metrology suite cannot be repacked below four hours with 20% margin; fresh ramp diagnostics cannot safely place micro-deltas around the operative floor; or Q4 dry runs show missing phases, capped contexts, or a campaign budget above three nights. Kill wall validation if the meter lacks current calibration, safe fixture, adequate synchronized sampling, fixed-range uncertainty at Mac loads, or battery-charge neutralization. A failed Q4 holdout or load-dependent wall discrepancy does not kill the paper—both are publishable findings—but they prohibit predictive or simple-gain claims.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10039:JouleWise currently has a complete paper structure but no live claim-bearing values: historical windows establish the rules and supply design diagnostics, while D-117 requires three fresh prospective windows. The 1.5B floor window contains 10 absolute members and 10 four-member null-ABBA blocks; the 7B floor window repeats that 50-bundle design; both obtain prefill floors from the same bundles at zero additional runtime. The contrast window contains ten 1.5B/7B decode ABBA blocks. Their budgeted durations, including calibration, NEG8 bounds, references, untouched idle, and 20% margin, are 3.14, 3.24, and 2.80 hours respectively. Before any night, desk work must land the two-slot live-calibration ledger session, D-102 acceptance-successor machinery, prefill-capable four-cell mint, three frozen campaign packs, synthetic live-ledger regression, extraction specifications, and readiness packet. After the floor windows pass, mint the combined 1.5B/7B decode-and-prefill floor artifact; after the contrast passes, apply the two distinct claim gates and populate the MVP manuscript.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10073:Kill the ICPE upgrade before spending expansion nights if D-117 cannot mint valid floors; the 150-config metrology suite cannot be repacked below four hours with 20% margin; fresh ramp diagnostics cannot safely place micro-deltas around the operative floor; or Q4 dry runs show missing phases, capped contexts, or a campaign budget above three nights. Kill wall validation if the meter lacks current calibration, safe fixture, adequate synchronized sampling, fixed-range uncertainty at Mac loads, or battery-charge neutralization. A failed Q4 holdout or load-dependent wall discrepancy does not kill the paper—both are publishable findings—but they prohibit predictive or simple-gain claims.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10193:Only then should the speculative-decoding extension consume nights. First run a two-to-three-week desk feasibility gate: instrument the already-executable Qwen2.5 external-draft path with direct proposal, acceptance, and decode-step events; prove exact output identity; conduct non-claim timing/energy pilots; and freeze an AP-SPEC campaign. If it passes, spend two additional quiet windows—one request-window floor campaign and one mechanism campaign, splitting the latter into a third window only if its measured runtime plus 20% margin exceeds four hours. Thus the paper has a solid three-night metrology core regardless of whether the mechanism bet survives, and a five-night target if it does.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10236:- Dry-run timing exceeds four hours after the mandatory 20% margin; first cut the size comparison, then cancel rather than compress the protocol.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10251:Only then should the speculative-decoding extension consume nights. First run a two-to-three-week desk feasibility gate: instrument the already-executable Qwen2.5 external-draft path with direct proposal, acceptance, and decode-step events; prove exact output identity; conduct non-claim timing/energy pilots; and freeze an AP-SPEC campaign. If it passes, spend two additional quiet windows—one request-window floor campaign and one mechanism campaign, splitting the latter into a third window only if its measured runtime plus 20% margin exceeds four hours. Thus the paper has a solid three-night metrology core regardless of whether the mechanism bet survives, and a five-night target if it does.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10294:- Dry-run timing exceeds four hours after the mandatory 20% margin; first cut the size comparison, then cancel rather than compress the protocol.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10580:Kill a backend before a measurement session if its required counter is unsupported, timestamps or wrap behavior cannot be bounded, deterministic pulses cannot be reproduced, telemetry overhead materially perturbs the signal, or a desk pilot projects that a `2F` effect cannot fit inside a four-hour window. Kill the three-counter claim if RAPL is unavailable. Kill “general validation” if NVML’s held-out super-floor contrasts fail; retain it as a documented portability refusal. Never compensate by smoothing, increasing repetitions after seeing results, or borrowing the Mac floor.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10633:Kill a backend before a measurement session if its required counter is unsupported, timestamps or wrap behavior cannot be bounded, deterministic pulses cannot be reproduced, telemetry overhead materially perturbs the signal, or a desk pilot projects that a `2F` effect cannot fit inside a four-hour window. Kill the three-counter claim if RAPL is unavailable. Kill “general validation” if NVML’s held-out super-floor contrasts fail; retain it as a documented portability refusal. Never compensate by smoothing, increasing repetitions after seeing results, or borrowing the Mac floor.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10702:JouleWise currently has a complete paper structure but no live claim-bearing values: historical windows establish the rules and supply design diagnostics, while D-117 requires three fresh prospective windows. The 1.5B floor window contains 10 absolute members and 10 four-member null-ABBA blocks; the 7B floor window repeats that 50-bundle design; both obtain prefill floors from the same bundles at zero additional runtime. The contrast window contains ten 1.5B/7B decode ABBA blocks. Their budgeted durations, including calibration, NEG8 bounds, references, untouched idle, and 20% margin, are 3.14, 3.24, and 2.80 hours respectively. Before any night, desk work must land the two-slot live-calibration ledger session, D-102 acceptance-successor machinery, prefill-capable four-cell mint, three frozen campaign packs, synthetic live-ledger regression, extraction specifications, and readiness packet. After the floor windows pass, mint the combined 1.5B/7B decode-and-prefill floor artifact; after the contrast passes, apply the two distinct claim gates and populate the MVP manuscript.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10736:Kill the ICPE upgrade before spending expansion nights if D-117 cannot mint valid floors; the 150-config metrology suite cannot be repacked below four hours with 20% margin; fresh ramp diagnostics cannot safely place micro-deltas around the operative floor; or Q4 dry runs show missing phases, capped contexts, or a campaign budget above three nights. Kill wall validation if the meter lacks current calibration, safe fixture, adequate synchronized sampling, fixed-range uncertainty at Mac loads, or battery-charge neutralization. A failed Q4 holdout or load-dependent wall discrepancy does not kill the paper—both are publishable findings—but they prohibit predictive or simple-gain claims.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10749:JouleWise currently has a complete paper structure but no live claim-bearing values: historical windows establish the rules and supply design diagnostics, while D-117 requires three fresh prospective windows. The 1.5B floor window contains 10 absolute members and 10 four-member null-ABBA blocks; the 7B floor window repeats that 50-bundle design; both obtain prefill floors from the same bundles at zero additional runtime. The contrast window contains ten 1.5B/7B decode ABBA blocks. Their budgeted durations, including calibration, NEG8 bounds, references, untouched idle, and 20% margin, are 3.14, 3.24, and 2.80 hours respectively. Before any night, desk work must land the two-slot live-calibration ledger session, D-102 acceptance-successor machinery, prefill-capable four-cell mint, three frozen campaign packs, synthetic live-ledger regression, extraction specifications, and readiness packet. After the floor windows pass, mint the combined 1.5B/7B decode-and-prefill floor artifact; after the contrast passes, apply the two distinct claim gates and populate the MVP manuscript.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10783:Kill the ICPE upgrade before spending expansion nights if D-117 cannot mint valid floors; the 150-config metrology suite cannot be repacked below four hours with 20% margin; fresh ramp diagnostics cannot safely place micro-deltas around the operative floor; or Q4 dry runs show missing phases, capped contexts, or a campaign budget above three nights. Kill wall validation if the meter lacks current calibration, safe fixture, adequate synchronized sampling, fixed-range uncertainty at Mac loads, or battery-charge neutralization. A failed Q4 holdout or load-dependent wall discrepancy does not kill the paper—both are publishable findings—but they prohibit predictive or simple-gain claims.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10954:This is the safest fallback second paper. Use one frozen Qwen2.5-1.5B source revision, retain D-117’s exact Q4 workload and floor, add only BF16 and Q8, delete Q5/Q6, and make no JouleWise-issued quality-equivalence claim under D-041. The result is a floor-gated resolvability map that also tests whether energy tracks artifact bytes or MLX kernel maturity. Honest cost is **seven nights from today**: four MVP nights, separate BF16 and Q8 floor nights, and a three-arm contrast night; **4–8 desk weeks** for acquisition, conversion provenance, multi-cell minting, estimator work, and artifact release. Survival prior: **65–75%**. The review’s concluding “two extension nights” conflicts with its own plan—two new standard floors plus a contrast are three nights unless Ed prospectively ratifies a packed dual-floor design that still fits the four-hour envelope.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11068:2. **Capability week:** acquire/hash/load both; prove memory headroom, fixed output policy, tokenizer/workload validity, and a four-hour campaign envelope.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11072:6. **Floor-packing gate:** prove that every claim arm has an independently governed floor and that the frozen schedule fits under four hours with 20% margin. If not, budget the third night before collection or kill.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11113:This is the safest fallback second paper. Use one frozen Qwen2.5-1.5B source revision, retain D-117’s exact Q4 workload and floor, add only BF16 and Q8, delete Q5/Q6, and make no JouleWise-issued quality-equivalence claim under D-041. The result is a floor-gated resolvability map that also tests whether energy tracks artifact bytes or MLX kernel maturity. Honest cost is **seven nights from today**: four MVP nights, separate BF16 and Q8 floor nights, and a three-arm contrast night; **4–8 desk weeks** for acquisition, conversion provenance, multi-cell minting, estimator work, and artifact release. Survival prior: **65–75%**. The review’s concluding “two extension nights” conflicts with its own plan—two new standard floors plus a contrast are three nights unless Ed prospectively ratifies a packed dual-floor design that still fits the four-hour envelope.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11227:2. **Capability week:** acquire/hash/load both; prove memory headroom, fixed output policy, tokenizer/workload validity, and a four-hour campaign envelope.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:11231:6. **Floor-packing gate:** prove that every claim arm has an independently governed floor and that the frozen schedule fits under four hours with 20% margin. If not, budget the third night before collection or kill.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:696:*Fail-closed* means that missing, inconsistent, stale, or contaminated evidence produces a refusal rather than an optimistic default. The collection unit is one uninterrupted two-to-four-hour window with one power state, one instrument identity, fresh calibration before and after, a fresh drift-bound corpus, and one verdict over the exact member set. Work that does not fit with at least a 20% failure margin is split prospectively into another independently calibrated window.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:824:The stage allowances incorporate the configured 30-second idle, warmup/teardown, stage arm overhead, and cooldown conventions. The pre-calibration allowance includes the required 180-second post-admin settle. The separate ten-minute untouched quiet-idle gate is added before applying the 20% margin.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:1003:No live timings, calibration observations, successor generation, or mint replay were performed. Runtime estimates therefore inherit historical-machine variance; the 20% margin is the current mitigation.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:1127:*Fail-closed* means that missing, inconsistent, stale, or contaminated evidence produces a refusal rather than an optimistic default. The collection unit is one uninterrupted two-to-four-hour window with one power state, one instrument identity, fresh calibration before and after, a fresh drift-bound corpus, and one verdict over the exact member set. Work that does not fit with at least a 20% failure margin is split prospectively into another independently calibrated window.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:1402:   2-4 hour envelope with references, calibrations, and >=20% failure
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:1970:The stage allowances incorporate the configured 30-second idle, warmup/teardown, stage arm overhead, and cooldown conventions. The pre-calibration allowance includes the required 180-second post-admin settle. The separate ten-minute untouched quiet-idle gate is added before applying the 20% margin.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:2153:No live timings, calibration observations, successor generation, or mint replay were performed. Runtime estimates therefore inherit historical-machine variance; the 20% margin is the current mitigation.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:2487:Planning estimates below assume the current 2–4-hour claim-window protocol, at least 20% failure margin, and physical Ed preparation through §5A.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:3805:Planning estimates below assume the current 2–4-hour claim-window protocol, at least 20% failure margin, and physical Ed preparation through §5A.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:4759:| Q1 | MET-WINDOW-C-01 | P1 Phase Gate | BLOCKED — FROZEN-PLAN-READINESS-RECORD (A reviewed FROZEN-PLAN READINESS RECORD exists before any collection night: frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight, launcher-verified), ED-5A (Ed section-5A window prep FRESH POST-MOVE (the 2026-08-02 laptop move invalidated settled-machine conditions; network time off, AC, settled machine, walk-away)) [QUIET-MAC] | Execute a reviewed fresh-claim collection plan beginning with Window C: no Window B member enters a replacement claim basis; split prospectively across windows C and D if the complete replacement cannot fit the 2-4 hour envelope with at least 20 percent failure margin. | The fresh-claim metrology plan replaces every still-desired Window-B claim component without using any Window-B member, under reviewed frozen-plan and validated-window controls. Evidence: A fresh-claim plan recollects every still-desired Window-B claim component beginning with Window C; no Window B member enters a replacement claim basis; The fresh plan includes the still-required C2, C4, and C5 collection scope under the frozen-plan discipline, split prospectively across windows C and D if one window cannot retain at least 20 percent failure margin inside the runbook's 2-4 hour envelope; Window operated under the validated protocols: bird-SIGSTOP with identity custody, guarded launcher, one-line arm messages with zero output streaming during idle-gate exposure, third-failure salvage rule; Whole-window verdict emitted by machinery that has passed MET-VERDICT-ADJ-01 adjudication; supersessions recorded once, pre-verdict; both roots backed up rc=0. Authority: [D-113 clauses 7-9 fresh-claim reset, readiness fence, and prospective C/D split](docs/decision_log.md). Acceptance: [MET-WINDOW-C-01 acceptance](docs/process/state_kernel.json). Fence: A window-C dangler seeking the b-ii mechanical license before D100-BII-BINDING-01 closes RETURNS TO THE GATE; the window itself may run (D-106 revisit clause). Fence: Before any collection night, the ordinary launcher verifies a reviewed FROZEN-PLAN READINESS RECORD binding the frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight (D-113 clauses 8-9 hard start fence). Fence: Plan root assembled and frozen before measurement; no plan edits after freeze (D-096 frozen-plan ratification). Fence: Zero agents AND zero operator output streaming during measurement idle gates; arm messages are one line; bird-SIGSTOP protocol with identity custody and fail-safe CONT trap on all exit paths (2026-08-01 run report: streaming-during-idle-gate hazard + bird-SIGSTOP protocol). Note: D-113 clauses 7 and 9: the former remainder-only scope is SUPERSEDED. A fresh-claim plan is required; no Window B member enters a replacement claim basis. If the full replacement exceeds the runbook's 2-4 hour envelope with at least 20 percent margin, split it prospectively across windows C and D. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:4832:| Q1 | MET-WINDOW-C-01 | P1 Phase Gate | BLOCKED — FROZEN-PLAN-READINESS-RECORD (A reviewed FROZEN-PLAN READINESS RECORD exists before any collection night: frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight, launcher-verified), ED-5A (Ed section-5A window prep FRESH POST-MOVE (the 2026-08-02 laptop move invalidated settled-machine conditions; network time off, AC, settled machine, walk-away)) | Execute a reviewed fresh-claim collection plan beginning with Window C: no Window B member enters a replacement claim basis; split prospectively across windows C and D if the complete replacement cannot fit the 2-4 hour envelope with at least 20 percent failure margin. | The fresh-claim metrology plan replaces every still-desired Window-B claim component without using any Window-B member, under reviewed frozen-plan and validated-window controls. Evidence: A fresh-claim plan recollects every still-desired Window-B claim component beginning with Window C; no Window B member enters a replacement claim basis; The fresh plan includes the still-required C2, C4, and C5 collection scope under the frozen-plan discipline, split prospectively across windows C and D if one window cannot retain at least 20 percent failure margin inside the runbook's 2-4 hour envelope; Window operated under the validated protocols: bird-SIGSTOP with identity custody, guarded launcher, one-line arm messages with zero output streaming during idle-gate exposure, third-failure salvage rule; Whole-window verdict emitted by machinery that has passed MET-VERDICT-ADJ-01 adjudication; supersessions recorded once, pre-verdict; both roots backed up rc=0. Authority: [D-113 clauses 7-9 fresh-claim reset, readiness fence, and prospective C/D split](docs/decision_log.md). Acceptance: [MET-WINDOW-C-01 acceptance](docs/process/state_kernel.json). Fence: A window-C dangler seeking the b-ii mechanical license before D100-BII-BINDING-01 closes RETURNS TO THE GATE; the window itself may run (D-106 revisit clause). Fence: Before any collection night, the ordinary launcher verifies a reviewed FROZEN-PLAN READINESS RECORD binding the frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight (D-113 clauses 8-9 hard start fence). Fence: Plan root assembled and frozen before measurement; no plan edits after freeze (D-096 frozen-plan ratification). Fence: Zero agents AND zero operator output streaming during measurement idle gates; arm messages are one line; bird-SIGSTOP protocol with identity custody and fail-safe CONT trap on all exit paths (2026-08-01 run report: streaming-during-idle-gate hazard + bird-SIGSTOP protocol). Note: D-113 clauses 7 and 9: the former remainder-only scope is SUPERSEDED. A fresh-claim plan is required; no Window B member enters a replacement claim basis. If the full replacement exceeds the runbook's 2-4 hour envelope with at least 20 percent margin, split it prospectively across windows C and D. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:5055:./docs/site/run_state.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>Run State - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html">Roadmap</a> <a href="process.html">Process</a> <a href="record.html">Record</a> <a href="library.html" class="active">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <div class="doc-layout"> <aside class="toc-sidebar"><div class="card-label">Table of contents</div><a href="#start-here-for-every-big-run">Start Here For Every Big Run</a> <a href="#historical-stop-card-note">Historical Stop-Card Note</a> <a href="#active-stop-card">ACTIVE_STOP_CARD</a> <a href="#active-global-work-selection-gates">Active Global Work-Selection Gates</a> <a href="#restart-by-machine-state-lane">Restart By Machine-State Lane</a> <a href="#checkpoint-2026-07-18-late-d-077-adversarial-arc-complete-pr-77-open">CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR 77 open</a> <a href="#checkpoint-2026-07-18-claude-script-bridge-runs-in-the-pet-s-app-task">CHECKPOINT 2026-07-18: Claude script bridge runs in the pet&#x27;s app task</a> <a href="#checkpoint-2026-07-17-late-session-env-guard-branch-open-review-pending">CHECKPOINT 2026-07-17 (late session): env-guard branch open, review pending</a> <a href="#superseded-stop-card-cp-5">Superseded stop card (CP-5)</a> <a href="#current-project-status">Current Project Status</a> <a href="#session-history-pointers-only-run-reports-own-the-narrative">Session History (pointers only — run reports own the narrative)</a> <a href="#current-verification">Current Verification</a> <a href="#known-workspace-state">Known Workspace State</a> <a href="#historical-next-work-snapshot-superseded-2026-07-15">Historical Next-Work Snapshot (superseded 2026-07-15)</a> <a href="#reference-decisions-and-blockers-non-selection-context">Reference Decisions And Blockers (non-selection context)</a></aside> <div class="doc-wrap doc-source-run-state-md"> <p class="doc-meta"><a href="library.html">Back to sources</a> · rendered from <code>RUN_STATE.md</code></p> <div class="provenance-plate"><span class="source-chip" title="RUN_STATE.md · commit 1af9f92"><span class="source-file">RUN_STATE.md</span><span class="source-commit">commit 1af9f92</span></span></div> <!-- rendered: marked@18.0.6 --> <h1>JouleWise Run State</h1> <p>Last updated: 2026-07-25. <strong>Main is at <code>c3e2647</code>: PR #79&#39;s D-078 instrument repair merged on 2026-07-22, and PR #85&#39;s ratified SCREEN+BUDGET rules are merged with green CI after the four-round adversarial gauntlet.</strong> The repaired-instrument collection contains 229 strict members across four bracketed windows (a5-a8). Those windows are non-claim-bearing diagnostic, instrument-proving evidence; they do not license a floor or research claim.</p> <p>The merged rules now screen gross and idle-subtracted energy separately, carry a never-zero drift allowance for each family, require a fresh 24-hour drift bound, reject fallback-clock members from floor/claim cells, derive mockness from custody-bound config, and bar terminal mock evidence. NEXT: use one clean <code>[QUIET-MAC]</code> window and follow <code>docs/phase_2/window_runbook.md</code> exactly — mint the bound inside the window, collect the start triplet, midpoint reference, and end triplet, and produce the first claim-grade floors. Then re-verdict a8 and size the Splitwise campaign. The capsule was redeployed from <code>c3e2647</code> as <code>dep_2I04CG6tQ4t0mzY7</code> at 2026-07-25T01:46Z.</p> <p>Prior context (historical, pre-repair; superseded by the sign-off above): PRs #77 and #78 are both MERGED (#78 at b52abf3). The recal windows of 2026-07-18/19 collected 94 + 266 strict-valid bundles under the production environment guard (records: <code>docs/run_reports/2026-07-19-d077-recal-window.md</code>, <code>2026-07-19-recal456-extended-window.md</code>); that corpus is instrument evidence only — the pre-repair floor re-extraction plan is VOID, and P2-015 restarts under the repaired instrument per the roadmap. Ed-side standing: <code>sudo pmset -c displaysleep 10</code>.</p> <p>Prior arc (2026-07-17, SESSION ARC COMPLETE: Window A floors published (222 strict-valid bundles; P2-015 partial pending P2-039 artifact + P2-037 adjudication); advisor brief delivered (docs/advisor_briefs/); Ed DEPLOYED the README-first site + Learn guide (PR #75); exploratory block measured (OLMoE ~229 J / Qwen3-4B ~362.8 J / 122B ~1072 J gross suite, n=3, exploratory-labeled); DSpark/DFlash MLX feasibility CONFIRMED w/ per-round observability; D-075 extension-axis intake folded. Session records: docs/run_reports/2026-07-16-resumption-nohw-batch.md + 2026-07-17-window-a-floors.md.)</p> <h2 id="start-here-for-every-big-run">Start Here For Every Big Run</h2> <p>Before starting substantial work:</p> <ol> <li>Read this file.</li> <li>Read <code>TASK_QUEUE.md</code>.</li> <li>Read <code>AGENT_PLAN.md</code> (phase index) and the active phase&#39;s plan doc under <code>docs/phase_N/</code>; per-item status lives in the phase exit checklist (D-023).</li> <li>Read <code>docs/planning_reflection_protocol.md</code>.</li> <li>Check <code>docs/decision_log.md</code> before re-deciding anything; check <code>docs/risk_register.md</code> if starting a phase or a hardware-dependent task.</li> <li>Check the last 2-3 commits with <code>git log --oneline --decorate -3</code>.</li> <li>Check <code>git status --short --branch</code>.</li> <li>Run <code>python3 -m unittest discover -s tests</code> unless the task is docs-only.</li> <li>Do not commit local deletions or unrelated changes unless the user asks.</li> <li>Heartbeat rule (<code>docs/milestones.md</code>): if &gt;14 days passed with no run report and no recorded break, start with a milestones + risk review.</li> <li>Live MLX gates use the repo venv: <code>.venv/bin/python -m joulewise ...</code> (system python3 lacks mlx → <code>runtime_unavailable</code>).</li> <li>If an <code>ACTIVE_STOP_CARD</code> exists below, it overrides every normal &quot;restart&quot;, &quot;next&quot;, queue, and mission pointer until explicitly cleared.</li> </ol> <p>At the end of substantial work:</p> <ol> <li>Update only hand-authored factual/history sections of this file.</li> <li>Update <code>docs/process/state_kernel.json</code> for live task state and regenerate; do not hand-edit either generated region.</li> <li>Add or update a detailed report in <code>docs/run_reports/</code>.</li> <li>Record tests, commands, and blockers; generated lane heads own next-work selection.</li> <li>Record new decision-log entries and any risk-register status changes.</li> <li>Refresh <code>PROJECT_STATUS.md</code> if advisor-visible state changed.</li> <li>Push green commits promptly (small doc/bookkeeping commits straight to main; multi-commit code series as branch + PR per D-031). Do not accumulate unpushed local state — the remote and the high-level docs (README, PROJECT_STATUS) are the user&#39;s and advisor&#39;s view.</li> <li>Run a docs-consistency sweep before the final bookkeeping commit (delegate to a fast subagent): stale test counts, gate-state contradictions between prose summaries and checklist matrix rows, numbers cited in multiple places (C-002; D-023 extension). After any session that changed front-facing state, refresh <code>docs/site/DRIFT.md</code> (site-drift report) instead of deploying: per D-068 (2026-07-14) NO agent regenerates or deploys the site, ever — automation informs; Ed deploys manually. (Supersedes the C-013 regenerate+redeploy convention.)</li> <li>Call out any dirty working-tree state that should not be accidentally committed.</li> </ol> <h2 id="historical-stop-card-note">Historical Stop-Card Note</h2> <p>This 2026-07-11 clearance note is retained as history only; current stop-card and work-selection state is generated immediately below from the kernel.</p> <!-- BEGIN GENERATED: state-kernel run-state-intake --> <h2 id="active-stop-card">ACTIVE_STOP_CARD</h2> <p>Status: NONE — no stop card is active. Stop-card authority: D-050 / D-063 (<a href="docs/decision_log.md">decision log</a>).</p> <h2 id="active-global-work-selection-gates">Active Global Work-Selection Gates</h2> <p>NONE — no global work-selection gate is active.</p> <h2 id="restart-by-machine-state-lane">Restart By Machine-State Lane</h2> <p>Source of truth for work selection: <a href="docs/process/state_kernel.json">state kernel</a> (updated 2026-07-25). Latest report: <a href="docs/run_reports/2026-07-24-screen-budget-gauntlet.md">SCREEN+BUDGET rules ratified, adversarially verified, and merged via PR #85; prospective quiet-window collection is next</a>.</p> <h3>[ED-EXTERNAL]</h3> <ul> <li>READY — E1 <code>P1-008</code>: Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability).</li> </ul> <h3>[QUIET-MAC]</h3> <ul> <li>READY — Q1 <code>P2-015</code>: Collect the first claim-grade Window A floors in one clean prospective quiet window per the claim-window run-book: mint the drift bound in-window, then run the start triplet, midpoint reference, and end triplet before the a8 re-verdict and Splitwise sizing.</li> </ul> <h3>[AGENT]</h3> <ul> <li>READY — A3 <code>FLOOR-BIND-01</code>: Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions.</li> </ul> <!-- END GENERATED: state-kernel run-state-intake --><h2>CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR #77 open</h2> <p>The RESUME list from the 2026-07-17 checkpoint is fully executed. The relaunched execution-lens review, fix rounds 1-2, and their delta re-audits had already run earlier on 2026-07-18 (commits <code>1aebf14</code>, <code>6d80039</code>); this session closed the surviving P1 (child accepted any JSON object as the frozen cooldown anchor) plus every finding from four further delta re-audits, as fix rounds 3-8 in commit <code>ad0920b</code>: canonical anchor validator (<code>joulewise/cooldown_anchor.py</code>) enforced fail-closed at parent/CLI/controller boundaries; collision-safe, crash-atomic, flock-serialized rejection-verdict custody (<code>experiments/rejections/</code>); physical-domain baseline validation (the <code>inf</code>-anchor fail-open gate is closed); discriminating process-race regression. Suite green lead-side at every round boundary, final <code>Ran 1746 tests</code>, <code>OK (skipped=12)</code>. Awake-half live probe validation passed on real hardware (zero probe errors); the Ventura screensaver is now disabled on the machine (<code>idleTime = 0</code>). PR #77 carries the gate narrative; merge is Ed&#39;s call. Full record: <code>docs/run_reports/2026-07-18-d077-fix-rounds.md</code>. Tooling: codex-run-v3 xhigh review-genre sessions ended with null final messages 4x (bridge-resume recovered each; personal-tooling defect, recorded in the run report and the global codex-delegation skill field notes, not the repo queue).</p> <h2 id="checkpoint-2026-07-18-claude-script-bridge-runs-in-the-pet-s-app-task">CHECKPOINT 2026-07-18: Claude script bridge runs in the pet&#39;s app task</h2> <p>The actual Claude Code fallback route is <code>scripts/codex-bridge</code>, not the MCP server for recent audited work. The wrapper now sends <code>new</code> and <code>review</code> turns through a dedicated app-owned Codex desktop task when the local host id is configured. This is the same local-conversation state the native pet consumes; the prior observer-only diagnosis was incorrect because the pet never reads <code>~/.codex/claude-spawned/index.jsonl</code>. A live Sol/high smoke appeared in the Codex app as thread <code>019f77a6-3612-7332-9f5e-be9fbde56be5</code>, turn <code>019f77a9-2827-7de1-accf-ac2eda21927e</code>, and returned <code>JOULEWISE_NATIVE_PET_BRIDGE_OK</code> through the script. Adaptive effort remains unchanged: <code>high</code> fallback/default, <code>xhigh</code> only on named hard-task triggers, and <code>ultra</code> only for sessions that must spawn subagents. Full record: <code>docs/run_reports/2026-07-18-claude-codex-pet-observer.md</code>.</p> <p>Committed 2026-07-18 on <code>impl/env-guard-cooldown</code> (after the D-077 packet boundary <code>6d80039</code>) with a lead execution review at the bench: IPC socket ownership/permission checks, PID-checked host-task lock, interrupt-on-terminate, no-network sandbox policy, and one-hop rule all verified in <code>scripts/codex-app-bridge.mjs</code>; real-socket fake-router tests plus observer lifecycle tests included; canonical suite green lead-side (<code>Ran 1722 tests</code>, <code>OK (skipped=12)</code>). The same commit carries the doctor-driven CLAUDE.md trims (global + repo; content deduplicated into <code>.claude/skills/codex/SKILL.md</code>, which is the operating home) and stamp-only <code>docs/site/*.html</code> provenance refresh.</p> <h2 id="checkpoint-2026-07-17-late-session-env-guard-branch-open-review-pending">CHECKPOINT 2026-07-17 (late session): env-guard branch open, review pending</h2> <p>Window A floors contamination diagnosed from primary data: macOS Ventura <em>video</em> screensaver on an awake display contaminated 43/50 suite-calibration bundles (~+30% energy, −11% throughput; engage at HID-idle +20 min, dismiss on unlock — pmset assertion log corroborated to the second). The six &quot;low&quot; su-ABBA runs (18:16–18:36 UTC) are the only CLEAN suite runs; comparative suite floors (4.923 J item / 24.62 J suite) are transition artifacts. The professor&#39;s power-source hypothesis is refuted (AC/140 W/100% throughout). Details: memory note + <code>docs/run_reports/2026-07-17-environment-guard.md</code>.</p> <p>Branch <code>impl/env-guard-cooldown</code> (pushed, commit e2813ee) holds the D-077 response: environment-guard preflight (+<code>--arm-quiet-mode</code>), per-run idle admission gate, cooldown v2, unwaivable <code>environment_admission_failed</code> claim barrier, policy sidecars, contract/doc updates. Design consult (Sol xhigh, thread 019f7356-32d3) adjudicated and encoded; implementation by Sol xhigh (thread 019f7362-6627, resumed via codex-bridge after an MCP transport timeout); session-close scope check SCOPE_OK; full suite green lead-side (OK, 12 skips). Lead bench fix included: <code>pmset -g systemstate</code> parser now accepts the live &quot;Capabilities are:&quot; form (was null → fail-closed on real hardware); fixtures pinned to verbatim live output.</p> <p>RESUME (in order):</p> <ol> <li>Relaunch the adversarial review round (was stopped mid-run at checkpoint): fresh read-only Sol xhigh, execution lens, over <code>git diff main...impl/env-guard-cooldown</code> (prompt shape in <code>.codex-bridge/</code> prompt snapshots); lead holds the contract lens (done for cooldown_gate/claim-barrier/anchor hunks).</li> <li>Triage findings → fix rounds (defect-shaped regressions) → DELTA RE-AUDIT.</li> <li>Live-validate flagged probes during next quiet-window prep: <code>pmset -g systemstate</code> display-asleep form + screensaver-engaged probe while a screensaver is actually running (run report flags <code>live_validation_provisional</code>).</li> <li>PR per operation-loop §5 gate shape; then re-run suite ABBA calibration under the new guard ([QUIET-MAC], needs Ed) — floors D-076 figures for suite comparative cells must be recomputed/caveated pending re-run.</li> </ol> <p>Status: <strong>CLEARED 2026-07-11.</strong> Every clearance criterion met: all checkpoint-#4 resume items executed (P2-044 fix+merge #55; P2-037 audit dispositions → two fix rounds + approved NEEDS_SCOPE expansion + delta re-audit → #58; P2-043 #57; P2-045 #56); the four held hardening PRs #50-#53 merged after the cross-stream integration review over the combined tree (38 pre-merge cross-stream failures caught and fixed; 1 review blocker confirmed by refuters → PR #59; SF1 refuted; SF3 → queue row P2-049); DOC-008 kernel refreshed at final head (schema v2, authority field, branch impl/doc008-kernel awaiting PR); bookkeeping arc complete (run report, C-028 council entry with layer catch-rates and ~57-invocation spend record, D-064 ratified incl. manifest v3 + claude-codex-report/v1 + WRITE_SCOPE enforcement; queue reconciled; consistency sweep; site regen+deploy). All clearance-time opens since CLOSED same day: #59 MERGED, DOC-008 MERGED (#60). Remaining queue heads: P2-049/P2-050/TOOL-01.</p> <h2 id="superseded-stop-card-cp-5">Superseded stop card (CP-5)</h2> <p>Status: <strong>CLEARED 2026-07-09</strong> by the CP-5 resume session. Every clearance criterion was met: all three worktree diffs lead-gated (envgate live-gated against the real affine mock bundle) and merged as PRs #23/#24/#25; PR #22 merged after a fresh final-head pass; the methodology synthesis and suite_next specs packet adjudicated (CP-6 in the stream log); all accepted pre-campaign changes landed and merged (PRs #26/#27/#28); both post-merge integration reviews CLEAN; queue rank 0 closed. Full record: <code>docs/run_reports/2026-07-09-cp5-resume.md</code>. No stop card is active.</p> <h2 id="current-project-status">Current Project Status</h2> <p><strong>Collection era open (2026-07-25): main <code>c3e2647</code> contains the merged instrument repair (PR #79) and the merged SCREEN+BUDGET rules (PR #85). The 229-member a5-a8 collection is non-claim-bearing diagnostic, instrument-proving evidence.</strong> The next claim attempt is one clean prospective quiet window per <code>docs/phase_2/window_runbook.md</code>, with an in-window bound mint and start-triplet + midpoint + end-triplet references. A passing window produces the first claim-grade floors; the a8 re-verdict and Splitwise sizing follow. Records: <code>docs/run_reports/2026-07-23-window-a-collection-arc.md</code> and <code>docs/run_reports/2026-07-24-screen-budget-gauntlet.md</code>.</p> <p>The D-078 Phase-0 instrument repair was signed off and merged through PR #79 on 2026-07-22. Registered limitation L1 remains owned by FLOOR-BIND-01; it does not reopen the completed repair. Record: <code>docs/run_reports/2026-07-20-p0-instrument-repair.md</code>. Earlier arcs below are historical.</p> <p><strong>C-028 CLOSED (2026-07-11): the full hardening + analysis-engine arc is on main.</strong> Reducer lattice 0.4.2 (inter-token metric) / 0.4.1 (idle ESS, HAC variance — local r1&#39;s 47x underestimate closed) / 0.4.0 (verdict split + window_evidence_precheck) with frozen legacy arms; the analysis trio complete (P2-042 manifest → P2-041 verdict split → P2-037 contrast/claim engine with unwaivable cleanup claim gating per the two-layer waiver reconciliation); doctor preflight; publication privacy pack (fail-closed inventory); packaging CI; primary-verified related work; load-transition prep (B remains [QUIET-MAC]). Window A&#39;s software gates are ALL satisfied; execution needs a quiet machine + Ed.</p> <p>PRs #41-#60 form the landed C-028 arc, all merged 2026-07-11 (incl. the #59 integration-review fixes and the #60 DOC-008 kernel refresh); none implies live evidence. P0-003 is satisfied by the verified iCloud backup/restore. All NVIDIA/Orin protocol pins remain PROVISIONAL pending P1-006 live evidence.</p> <p><strong>Historical restart snapshot (recorded 2026-07-13; non-operative).</strong> The numbered sequence below is retained as dated handoff narrative, not current work-selection authority. Use the generated region above for selection.</p> <ol> <li>DONE 2026-07-13: #61-#63 merged at delta-audited heads; site deployed live under the cap; XSI-1 CI hardening green on main; bridge landed and lead-verified (8/8 protocol checks; suite 1318 OK).</li> <li>[ED + AGENT] <strong>Comprehensive whole-project audit (declared gate).</strong> The audit method proposal is with Ed; no further feature work, queue pulls, or campaign prep until the audit runs and its findings are adjudicated. Audit focus per Ed: overproduction (excess code/tests), plus everything a serious external review would check.</li> <li>[QUIET-MAC + ED] After the audit: Window A — C-019 production-shaped shakedown and P2-015-SMOKE, then P2-015 floors and P2-006 baselines. Do not run this lane while an agent session is active.</li> <li>[AGENT] Post-audit, outside a quiet window: P2-050 adjudication, SITE-02 follow-ups, P2-027 publication prep. P2-022/P2-023 remain blocked until the 2M corpus exists.</li> </ol> <h2 id="session-history-pointers-only-run-reports-own-the-narrative">Session History (pointers only — run reports own the narrative)</h2> <p>Parenthetical states below are historical at each report&#39;s head; they are not current restart instructions. Current state is the C-028 block above.</p> <ul> <li><p>2026-07-18 Claude Code script bridge + native pet integration: <code>docs/run_reports/2026-07-18-claude-codex-pet-observer.md</code></p> </li> <li><p>2026-07-13 Bridge v1: bridge-protocol/v1 contract + scripts/bridge tooling (PR #64; co-designed with Sol over the bridge itself): <code>docs/run_reports/2026-07-13-bridge-v1.md</code></p> </li> <li><p>2026-07-13 Restart close: #61-#63 merged at delta-audited heads (DRA-001 fixed; XSI-1 CI hardening), site live under cap; audit gate declared: <code>docs/run_reports/2026-07-13-restart-merge-deploy.md</code></p> </li> <li><p>2026-07-12 Claude↔Sol bidirectional bridge (concurrent Ed-directed thread; lead-verified 2026-07-13): <code>docs/run_reports/2026-07-12-claude-sol-bridge.md</code></p> </li> <li><p>2026-07-12 Agent-lane triple: SITE-01/P2-049/P2-028 → PRs #61-#63 at lead-gated heads; delta re-audits owed pre-merge on #62/#63: <code>docs/run_reports/2026-07-12-agent-lane-triple.md</code></p> </li> <li><p>2026-07-11 P2-041 vetted rebuild (uncommitted; lead pathspec review and commit pending): <code>docs/run_reports/2026-07-11-p2041-vetted-rebuild.md</code></p> </li> <li><p>2026-07-10 NV-GATE-2 idle-capture regression debug/fix (uncommitted; localhost re-verification remains lead-gated): <code>docs/run_reports/2026-07-10-nvgate2-idle-capture-fix.md</code></p> </li> <li><p>2026-07-10 NV-GATE-2 CODE-NOW implementation (NV-1/NV-3/NV-4/NV-5; live promotion evidence still gated): <code>docs/run_reports/2026-07-10-nvgate2-codenow.md</code></p> </li> <li><p>2026-07-10 NV-GATE-2 accepted-findings fix round (uncommitted; merge metadata recreation and lead gate pending): <code>docs/run_reports/2026-07-10-nvgate2-fix-round.md</code></p> </li> <li><p>2026-07-10 P2-038 accepted-findings fix round (all FIX-1..FIX-6 green; content-merged <code>origin/main</code>, Git merge metadata sandbox-blocked): <code>docs/run_reports/2026-07-10-p2038-fix-round.md</code></p> </li> <li><p>2026-07-10 P2-038 production uncertainty software path (live quiet-machine closure still open): <code>docs/run_reports/2026-07-10-p2038-production-uncertainty.md</code></p> </li> <li><p>2026-07-10 P2-040 reducer-version compatibility review fix (uncommitted): <code>docs/run_reports/2026-07-10-p2040-versioning-fix.md</code></p> </li> <li><p>2026-07-10 P2-040 remainder implementation (uncommitted, pending lead pathspec commit/corpus gate): <code>docs/run_reports/2026-07-10-p2040-remainder.md</code></p> </li> <li><p>2026-07-10 P2-040 / RETRO-001 fix round (committed on c027-int-p2040 after lead review): <code>docs/run_reports/2026-07-10-p2040-fix-round.md</code></p> </li> <li><p>2026-07-09 C-027 whole-project council review (7 gpt-5.6-sol lenses + counterreview + independent final examiner): <code>docs/reviews/2026-07-09-c027-whole-project-review.md</code> (compact run report: <code>docs/run_reports/2026-07-09-c027-council-review.md</code>)</p> </li> <li><p>2026-07-09 Claude Code → Codex MCP bridge hardening and live smoke: <code>docs/run_reports/2026-07-09-claude-codex-mcp-bridge.md</code></p> </li> <li><p>2026-07-12 adaptive Claude Code ↔ Sol/Fable bridge follow-up: <code>docs/run_reports/2026-07-12-claude-sol-bridge.md</code></p> </li> <li><p>2026-07-09 P2-034 broad campaign packs (C-026; PR #39): <code>docs/run_reports/2026-07-09-p2034-broad-packs.md</code></p> </li> <li><p>2026-07-09 spec-fleshing wave 2, ultracode (C-025; PRs #33..#38; D-056..D-059): <code>docs/run_reports/2026-07-09-spec-fleshing-wave2.md</code></p> </li> <li><p>2026-07-09 spec-fleshing wave 1 (C-024; PRs #29..#32; D-052..D-055): <code>docs/run_reports/2026-07-09-spec-fleshing-wave1.md</code></p> </li> <li><p>2026-07-09 scientific-rigor review of suite/benchmark/question bank (C-023; review-only; full record in <code>docs/reviews/2026-07-09-scientific-rigor-review.md</code>): <code>docs/run_reports/2026-07-09-scientific-rigor-review.md</code></p> </li> <li><p>2026-07-09 CP-5 resume: pre-campaign review completed, stop card cleared, PRs #22..#28 merged, Window-A GO (C-022): <code>docs/run_reports/2026-07-09-cp5-resume.md</code></p> </li> <li><p>2026-07-09 meta-process stop-card + codex-bridge audit cleanup (D-050; CP-5 preserved untouched): <code>docs/run_reports/2026-07-09-meta-process-stop-card-cleanup.md</code></p> </li> <li><p>2026-07-09 advisor status-site live-depth refresh (D-051/C-021; subordinate to the then-active CP-5 stop card): <code>docs/run_reports/2026-07-09-advisor-status-site.md</code></p> </li> <li><p>2026-07-08 suite build (C-017; adjudication + PRs #17/#18/#20/#19; D-044..D-047): <code>docs/run_reports/2026-07-08-suite-build.md</code></p> </li> <li><p>2026-07-08 suite-science + expansion (C-014/C-015; PRs #14/#15/#16; D-038..D-042): <code>docs/run_reports/2026-07-08-suite-science-expansion.md</code></p> </li> <li><p>2026-07-08 Lakebed deploy (C-013): <code>docs/run_reports/2026-07-08-lakebed-deploy.md</code></p> </li> <li><p>2026-07-08 site observatory (PR #13): <code>docs/run_reports/2026-07-08-site-observatory.md</code></p> </li> <li><p>2026-07-08 critique second-pass + councils+critique (C-011 → PR #12): <code>docs/run_reports/2026-07-08-councils-critique-session.md</code></p> </li> <li><p>2026-07-07/08 resume+merge (C-009 first full run; PRs #8..#11): <code>docs/run_reports/2026-07-07-resume-merge-session.md</code></p> </li> <li><p>Older: see <code>docs/run_reports/</code> (dated files).</p> </li> </ul> <h2 id="current-verification">Current Verification</h2> <ul> <li><strong>Merged main <code>c3e2647</code> / PR #85 (2026-07-25, current):</strong> the SCREEN+BUDGET implementation completed four adversarial audit rounds. Final PR-head CI was green on all five checks (<code>build</code>, <code>installed-wheel</code>, <code>release-chain</code>, <code>test (3.11)</code>, <code>test (3.14)</code>). The final lead-side suite recorded 2141 passed / 21 skipped; its one battery-timing flake passed on rerun. The capsule was redeployed as <code>dep_2I04CG6tQ4t0mzY7</code> at 2026-07-25T01:46Z.</li> <li><strong>D-078 repair sign-off gate (2026-07-22, historical merged gate):</strong> branch <code>impl/p0-instrument-repair</code> code/test head <code>040ca3a</code> (docs-only close-out <code>debc6d2</code> carries it unchanged; merged through PR #79): lead-run <code>pytest -q tests/</code> = <strong>2088 passed, 15 skipped, 1570 subtests, 0 failures</strong>; round-9 focused review surface 357 passed at the same head. Entries below are historical.</li> <li>PR #65 branch <code>impl/bridge-v1.1</code> final head <code>8b96bd4</code>: canonical <code>Ran 1387 tests</code>, <code>OK (skipped=10)</code>, lead-run 2026-07-13 (four lead-side full-suite runs across the fix arc: 1371→1381→1385→1387); CI green on the final head (build, installed-wheel, tests 3.11 + 3.14); <code>scripts/check-codex-mcp.mjs</code> 5/5 PASS with the v1.1 adapter; live session-open/close and reverse-consult probes recorded in <code>docs/run_reports/2026-07-13-bridge-v11.md</code>.</li> <li>Merged main <code>d285989</code> (post #65): canonical <code>Ran 1387 tests</code>, <code>OK (skipped=10)</code>, lead-run 2026-07-13 on the merged head; <code>scripts/check-codex-mcp.mjs</code> all PASS; no active workspace leases.</li> <li>Previous session (post #61-#63 merges + bridge v1 landing, pre-commit head <code>99b8640</code>): canonical <code>Ran 1318 tests in 111.017s</code>, <code>OK (skipped=10)</code>, lead-run 2026-07-13; bridge protocol checker 8/8 PASS; bridge focused tests 4/4 OK. Merged-main backstop at <code>12131b0</code> was <code>Ran 1314 tests</code>, <code>OK (skipped=10)</code>. Live capsule: measured artifact 854,349 B deployed, routes 5/5 HTTP 200, freshness 14/14 current at <code>7d3ea57</code>.</li> <li>Prior head <code>main@194ea39</code> (post #59 + #60 merges): canonical <code>Ran 1258 tests</code>, <code>OK (skipped=10)</code>, lead-run 2026-07-11 fresh-thread intake. PRs #41-#60 are all merged.</li> <li>Prior head <code>main@cc3afc3</code>: canonical <code>Ran 1220 tests</code>, <code>OK (skipped=10)</code>; retained corpus strict gate 6/6; PR #59 pre-merge lead replay was <code>Ran 1224 tests</code>, <code>OK (skipped=12)</code>.</li> <li>Count convention for C-028 records: ordinary worktree replays report <code>skipped=12</code>, final main reports <code>skipped=10</code>, and restricted managed sandboxes may report <code>skipped=13</code> when their environment-gated probe is unavailable. Preserve those environment labels when citing a tail.</li> </ul> <h3>Historical verification archive (exact at the recorded heads)</h3> <ul> <li><p>P2-041 vetted rebuild: baseline canonical <code>Ran 1041 tests in 67.995s</code>, <code>OK (skipped=13)</code>; final focused recipe modules <code>Ran 398 tests in 54.964s</code>, <code>OK (skipped=1)</code>; final canonical <code>Ran 1062 tests in 76.436s</code>, <code>OK (skipped=13)</code>; <code>git diff --check</code> and the dead-private-helper search clean. The retained corpus and localhost socket gates skipped loudly; no live or quiet-Mac validation was claimed. Report: <code>docs/run_reports/2026-07-11-p2041-vetted-rebuild.md</code>.</p> </li> <li><p>PR #49 P2-038 rail-only flake: pre-fix exact-test loop failed 4/100; retained failure emitted <code>cadence_ratio_unrecorded</code> plus <code>interpolation_bound_unrecorded</code> because the final trace sample preceded the stop marker. Archived <code>origin/main</code> reproduced on iteration 6. The fixture-only terminal-sample handshake fix passed the exact test 100/100, focused module <code>Ran 5 tests in 30.480s</code>, <code>OK</code>, and canonical suite <code>Ran 1041 tests in 66.509s</code>, <code>OK (skipped=13)</code>. Report: <code>docs/run_reports/2026-07-10-pr49-p2038-flake-root-cause.md</code>.</p> </li> <li><p>NV-GATE-2 idle-capture regression fix: historic fake-sampler plus new delayed-readiness regression passed together in 3 consecutive fresh processes; canonical suite <code>Ran 1023 tests in 35.164s</code>, <code>OK (skipped=13)</code>; <code>py_compile</code> and <code>git diff --check</code> clean. The exact localhost contract was attempted 3 times but loudly skipped before worker execution because this sandbox denied socket bind; lead socket-capable 3x rerun remains required. Report: <code>docs/run_reports/2026-07-10-nvgate2-idle-capture-fix.md</code>.</p> </li> <li><p>NV-GATE-2 accepted-findings fix round: focused node-worker/subprocess, controller, reducer, strict-dispatch, and schema surface <code>Ran 229 tests in 4.995s</code>, <code>OK (skipped=2)</code>; the historic fake-sampler test passed three consecutive fresh-process runs; canonical suite <code>Ran 1022 tests in 34.406s</code>, <code>OK (skipped=13)</code>; targeted <code>py_compile</code> and <code>git diff --check</code> clean. The 0.3.1 dispatch came from <code>origin/impl/p2040-remainder</code> because post-main did not contain it. Report: <code>docs/run_reports/2026-07-10-nvgate2-fix-round.md</code>.</p> </li> <li><p>NV-GATE-2 CODE-NOW worktree: baseline <code>Ran 910 tests in 32.549s</code>, <code>OK (skipped=12)</code>; final canonical suite <code>Ran 922 tests in 33.551s</code>, <code>OK (skipped=13)</code>; focused NV-1/NV-3/NV-4/NV-5 surface <code>Ran 232 tests in 6.085s</code>, <code>OK (skipped=2)</code>; <code>git diff --check</code> and targeted <code>py_compile</code> clean. The added skip is loud and specific: this managed sandbox denied localhost socket bind for NV-5. No live NVIDIA evidence or de-provisionalization was claimed.</p> </li> <li><p>P2-038 accepted-findings fix round: all FIX-1..FIX-6 complete; focused <code>Ran 70 tests in 41.211s</code>, <code>OK</code>; canonical <code>Ran 992 tests in 68.140s</code>, <code>OK (skipped=12)</code>; <code>git diff --check</code> clean. The real-child rail-only path now withholds drift on unknown contamination while gross remains eligible; P2-039&#39;s pending guard validator accepts the emitted block; backup launch failure, extreme-sentinel exclusion, child invocation, and literal phase constants are regression-tested. The absent worktree <code>runs/</code> corpus produced the loud six-bundle acceptance-gate skip. Git merge metadata remains absent because the managed sandbox cannot write the external worktree admin dir; the exact clean three-way <code>origin/main</code> content snapshot is applied.</p> </li> <li><p>P2-040 reducer-version review fix: focused strict/reducer run <code>Ran 84 tests in 1.908s</code>, <code>OK</code>; extended strict/reducer/schema run <code>Ran 104 tests in 1.997s</code>, <code>OK (skipped=1)</code>. Canonical run reached <code>Ran 926 tests in 33.732s</code>, <code>FAILED (failures=1, skipped=12)</code> solely at pre-existing <code>test_telemetry_measure_idle_with_fake_nvidia_smi</code>; isolated reruns reproduce its 0.2-second fake-process timing failure. All reducer/version tests pass; no out-of-scope node-worker change was made.</p> </li> <li><p>P2-040 remainder worktree: pre-change baseline <code>Ran 910 tests in 34.584s</code>, <code>OK (skipped=12)</code>; post-change focused affected modules <code>Ran 256 tests in 3.744s</code>, <code>OK (skipped=1)</code>; canonical <code>Ran 924 tests in 32.812s</code>, <code>OK (skipped=12)</code>; compileall and <code>git diff --check</code> clean. The unchanged six-corpus test produced its required loud skip because <code>runs/</code> is absent; lead 6/6 strict read-only rerun remains the landing gate.</p> </li> <li><p>P2-042 emitter branch <code>impl/p2042</code> (lead-committed base; draft PR #46; targeted-review fix round complete in the worktree, no fix-round commit): FIX-1 fail-closed typed identity/linkage validation, FIX-2 semantic <code>run_id</code> derivation, and FIX-3 raw-byte AP hashing/LF config emission are implemented. Focused manifest/generator/campaign checks: <code>Ran 82 tests in 12.317s, OK</code>; final canonical suite: <code>Ran 989 tests in 33.405s, OK (skipped=12)</code>. Review regressions cover <code>run_id=[]</code>, one malformed identity at each manifest object layer, a fully rehashed coherent rename, and a CRLF AP fixture. Report: <code>docs/run_reports/2026-07-10-p2042-analysis-manifest.md</code>.</p> </li> <li><p>P2-040 reducer-version review fix: focused strict/reducer run <code>Ran 84 tests in 1.908s</code>, <code>OK</code>; extended strict/reducer/schema run <code>Ran 104 tests in 1.997s</code>, <code>OK (skipped=1)</code>. Canonical run reached <code>Ran 926 tests in 33.732s</code>, <code>FAILED (failures=1, skipped=12)</code> solely at pre-existing <code>test_telemetry_measure_idle_with_fake_nvidia_smi</code>; isolated reruns reproduce its 0.2-second fake-process timing failure. All reducer/version tests pass; no out-of-scope node-worker change was made.</p> </li> <li><p>P2-040 remainder worktree: pre-change baseline <code>Ran 910 tests in 34.584s</code>, <code>OK (skipped=12)</code>; post-change focused affected modules <code>Ran 256 tests in 3.744s</code>, <code>OK (skipped=1)</code>; canonical <code>Ran 924 tests in 32.812s</code>, <code>OK (skipped=12)</code>; compileall and <code>git diff --check</code> clean. The unchanged six-corpus test produced its required loud skip because <code>runs/</code> is absent; lead 6/6 strict read-only rerun remains the landing gate.</p> </li> <li><p>P2-040 / RETRO-001 fix-round worktree: canonical suite <code>Ran 908 tests in 32.723s</code>, <code>OK (skipped=11)</code>; focused 211 tests OK; claims lint exit 0 with no errors; <code>git diff --check</code> clean. The absent <code>runs/</code> corpus produced the required loud six-bundle acceptance-gate skip; the lead corpus gate then PASSED (6/6 strict via corpus symlink), plus mock e2e run+strict+reduce and the post-merge full suite (OK, skipped=12).</p> </li> <li><p>Claude Code 2.1.207, Codex CLI 0.144.0, and Node 23.7.0 pass the bidirectional protocol checker. Claude → Sol now uses <code>gpt-5.6-sol</code> with <code>high</code> fallback/default and task-triggered xhigh/ultra escalation; the final guarded <code>/codex</code> smoke returned <code>JOULEWISE_SOL_HIGH_GUARDED_OK</code> (thread <code>019f5a2a-2f4a-7b33-8a6d-b44dcc5a7a26</code>) with source <code>mcp</code>, effort <code>high</code>, read-only sandbox, and <code>on-request</code> approvals. Claude-originated Sol sessions disable the reverse server. Top-level Sol → Fable uses the sole <code>consult_fable</code> MCP tool; live token <code>JOULEWISE_FABLE_MCP_OK</code> on thread <code>019f5a26-d8a6-7993-b48d-8131d88748b9</code>. Focused bridge tests pass 4/4 and <code>gen_state.py --check</code> passes. The current full suite ran 1,317 tests but is not green: one failure + one error in <code>test_gen_state</code> are caused by the concurrent uncommitted state-kernel removal of <code>P2-028</code> while the existing fidelity tests still require that ID; bridge tests are unaffected. Full details: <code>docs/run_reports/2026-07-12-claude-sol-bridge.md</code>.</p> </li> <li><p>Last code-bearing verified head c095c83 (post PR #39; note: 36d5641 later changed <code>scripts/build_site.py</code> on main without a recorded verification — flagged by C-027, covered by RETRO-001): suite <code>OK (skipped=10)</code> and repo lint errors=0, lead-run; pack lint errors=0 warnings=0.</p> </li> <li><p>Prior: main after wave-2 integration fixes: <code>python3 -m unittest discover -s tests</code> → <code>Ran 877 tests, OK (skipped=10)</code>, lead-run; repo lint errors=0; CI green on all six PR heads (#33..#38); combined-ref pre-merge suite check green; live rotated mock campaign strict-valid with order provenance (lead-validated); mock e2e emits uncertainty fields per D-057.</p> </li> <li><p>Prior: series head f75134d (post PRs #29..#32; docs-only) lead-verified; integration-fix commit 7156295 is also docs-only (no test surface): <code>python3 -m unittest discover -s tests</code> → <code>Ran 822 tests, OK (skipped=10)</code>, lead-run; CI green on all four PR heads (py3.11+py3.14); integration reviewer independently re-ran the suite and recomputed the detection-floor campaign arithmetic.</p> </li> <li><p>Prior verification (7666652, post PRs #22..#28): <code>Ran 822 tests, OK (skipped=10)</code>, lead-run.</p> </li> <li><p>Live lead gates this session (real MLX, Qwen2.5-1.5B via <code>.venv</code>, mock telemetry): single-prompt + TWO full 48-item jw_mixed suite runs (pre-merge old manifests, then final merged main with the REGENERATED manifests) — all strict-valid; 48/48 hash-domain closures on the real tokenizer; output token ids, model artifact hash, pinned sampler, and package versions verified present in the bundles.</p> </li> <li><p>Envelope gate live: honest <code>envelope_failed[E1]</code> on the mock affine bundle; refusals for wrong-profile/malformed/mixed inputs; exit codes 0/2/3.</p> </li> <li><p>Bundle pack live: pack → verify(0) → tamper → verify(2).</p> </li> <li><p>Manifest regen: byte-identical double-regen; all realized counts 512; new effective shas 855be4e5 (mixed) / 0316283d (sentinel).</p> </li> <li><p>CI green on every merged head (PR #27&#39;s first merge-ref run failed on a cross-branch fixture interaction; fixed test-side, then green).</p> </li> <li><p>Post-merge integration reviews (both waves): CLEAN, incl. an end-to-end mock campaign → strict → envelope-gate → pack → verify flow and a D-033 legacy-identity spoof probe that failed closed.</p> </li> <li><p><code>validate-bundle --strict</code> green over all 6 real corpus bundles under the new era rule (PR #22 live gate: 6/6 valid, tamper fails named).</p> </li> </ul> <h2 id="known-workspace-state">Known Workspace State</h2> <ul> <li>(2026-07-25) <code>main</code> and <code>origin/main</code> are at <code>c3e2647</code>, the PR #85 merge. PR #79&#39;s repair and PR #85&#39;s SCREEN+BUDGET implementation are both landed; final PR-head CI is green. The current working tree contains intentional lead bookkeeping and run-book/report work that must be preserved; it is not a clean measurement checkout. The next quiet-window operator must start from a separate clean, merged-main measurement checkout per <code>docs/phase_2/window_runbook.md</code>.</li> <li>The generated state-kernel blocks are authoritative for work selection. Hand-authored <code>RUN_STATE.md</code> and <code>TASK_QUEUE.md</code> text remains authoritative only for its own factual, policy, and historical domains; <code>docs/decision_log.md</code> remains the policy authority, exit checklists own phase completion, and evidence artifacts own scientific truth.</li> <li>Retained corpus and session scratchpad evidence are immutable.</li> </ul> <h2 id="historical-next-work-snapshot-superseded-2026-07-15">Historical Next-Work Snapshot (superseded 2026-07-15)</h2> <p>The following 2026-07-13 narrative is retained for chronology only. It is not a live queue or restart instruction; the generated work-selection region is the sole selector.</p> <p>The comprehensive whole-project audit is the declared gate (Ed, 2026-07-13): method proposal pending Ed&#39;s approval, then the audit runs and its findings are adjudicated before any further feature work. After that: Window A in the first clean quiet-machine window (C-019/P2-015-SMOKE, then P2-015 floors, P2-006 baselines), with post-audit [AGENT] heads P2-050 adjudication, SITE-02, and P2-027 publication prep outside quiet windows. <code>TASK_QUEUE.md</code> remains the ordering authority.</p> <p>Hardware-gated (unchanged): 2K/2L (P1-006; NV-GATE-2 additions from C-027 apply at live promotion), wall meter (P1-003), topology (P1-004), calendar mapping (P1-008).</p> <h2 id="reference-decisions-and-blockers-non-selection-context">Reference Decisions And Blockers (non-selection context)</h2> <p>These pointers retain external-dependency context but do not rank or select work. The generated region controls task selection.</p> <ul> <li>Supervisor approval and scope pending (P1-001, R-001 — mitigation holding); gates FULL D-016 closure.</li> <li>Calendar dates pending (P1-008, R-012).</li> <li>Wall-meter decision pending (P1-003, R-007).</li> <li>Physical network topology pending (P1-004, R-011).</li> <li>NVIDIA/Orin access evidence pending (P1-006; gates 2K/2L).</li> <li>Git author identity on this machine auto-selected as <code>Ed R &lt;edr@Eds-MacBook-Pro.local&gt;</code>. Amend future commits if a different identity is needed.</li> </ul> </div> </div> </main> <footer class="site"> <div class="inner"> <span>JouleWise · github.com/mpmdw/JouleWise</span> <span>RUN_STATE.md · commit 1af9f92 · regenerate: <span class="mono">python3 scripts/build_site.py</span></span> </div> </footer> </body> </html>
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:5154:./docs/site/readme.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>README - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html">Roadmap</a> <a href="process.html">Process</a> <a href="record.html">Record</a> <a href="library.html" class="active">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <div class="doc-layout"> <aside class="toc-sidebar"><div class="card-label">Table of contents</div><a href="#current-state">Current State</a> <a href="#verify">Verify</a> <a href="#release">Release</a> <a href="#run-the-harness-mock-target-no-hardware-or-extras-needed">Run The Harness (mock target — no hardware or extras needed)</a> <a href="#config-and-schema-verbs">Config And Schema Verbs</a> <a href="#documentation-map">Documentation Map</a></aside> <div class="doc-wrap doc-source-readme-md"> <p class="doc-meta"><a href="library.html">Back to sources</a> · rendered from <code>README.md</code></p> <div class="provenance-plate"><span class="source-chip" title="README.md · commit 1af9f92"><span class="source-file">README.md</span><span class="source-commit">commit 1af9f92</span></span></div> <!-- rendered: marked@18.0.6 --> <h1>JouleWise</h1> <p>JouleWise is an extensible measurement harness for energy-wise LLM inference across heterogeneous local hardware. The benchmark layered on that harness is the frozen workload suite, run rules, and strict validator. The name is a deliberate nod to JouleSort and Splitwise: energy measurement as the spine, split inference as the first major research application.</p> <p>The harness is designed around three stable ideas:</p> <ul> <li>Typed experiment configs define what should run.</li> <li>Runtime and telemetry adapters define how each hardware target is exercised and measured.</li> <li>Run bundles preserve raw traces, events, metadata, logs, and summary metrics for later audit and analysis.</li> </ul> <p><strong>Status:</strong> research prototype. The Mac (Apple M3 Max) measurement harness has completed its instrument repair (D-078 phase 0) and the repaired path has collected 229 strict members across four bracketed windows, a5-a8. Those windows are non-claim-bearing diagnostic, instrument-proving evidence, not published floors. The SCREEN+BUDGET rules are ratified and merged (D-078 clause 10; council C-033): they screen gross and idle-subtracted energy separately, retain a nonzero drift allowance for each family, require a fresh 24-hour bound, reject fallback-clock members from floor cells, and bar mock evidence from claims. The next step is one clean prospective quiet-machine window following <code>docs/phase_2/window_runbook.md</code>, producing the first claim-grade floors before the a8 re-verdict and Splitwise sizing.</p> <p>The post-audit architectural verdicts remain deliberately bounded: AXI-SB is <code>supported</code> for native static-batch runtime feasibility with request-scoped observability, while AXI-SC is <code>unsupported_for_joulewise</code> on the pinned runtime because the required speculative-decode/MTP observability or execution surface is absent. Neither is energy evidence. This summary does not select work: the generated state-kernel regions in <code>RUN_STATE.md</code> and <code>TASK_QUEUE.md</code> own live gates and next-task state. Quiet-machine execution still requires the lead-controlled hardware lane with Ed. The verified end-user quickstart remains a Phase 5 deliverable.</p> <h2 id="current-state">Current State</h2> <p>Phase 1 is in its final stretch; <strong>Phase 2&#39;s Mac vertical slice is complete and the project has its first real energy measurements</strong> (2026-07-06). From a typed config, one command produces a complete, schema-valid, auditable run bundle and reduces it to energy/latency summary metrics — proven first on deterministic mock adapters, and now live on real hardware: the MLX runtime + <code>powermetrics</code> telemetry adapters measured Qwen2.5-1.5B-Instruct (4-bit) on an Apple M3 Max. <strong>P2-003, gross energy — M3 Max / powermetrics SoC rails:</strong> ~47.2 J per 512-token request. <strong>P2-003, idle-subtracted energy — M3 Max / powermetrics SoC rails:</strong> ~44.4 J per request and ~79-90 mJ per generated output token (mean 86.8 mJ). Throughput was 257 tok/s. These are legacy L1 preliminary observations (pre-2M, manual review) under <code>docs/contracts/claims_ladder.md</code>; metric bases per <code>docs/contracts/token_normalization.md</code>. The six real corpus bundles pass <code>validate-bundle --strict</code> read-only and unrewritten: strict re-derives the recorded powermetrics power trace from raw plist evidence, re-derives summary metrics from the recorded trace and event log, checks the legacy additive summary comparison, and requires shape-valid provenance for new-era bundles. This validates the recorded evidence path; it does not independently rerun the hardware session.</p> <p>Unless a figure explicitly states otherwise, JouleWise uses gross measured energy within the named measurement boundary as the headline basis. Gross energy retains the idle, model-residency, and runtime overhead present during the measured interval, so comparisons across devices, configurations, and split versus monolithic execution use gross energy. Idle-subtracted energy is reported separately as a within-device secondary view of activity above the measured idle baseline; it is not used to rank devices or configurations. In Q4, the fixed term is estimated from the gross-energy workload sweep and is not set equal to measured idle energy. The advisor-review rationale and full basis/boundary rule are recorded in <a href="PROJECT_STATUS.md#measurement-methodology-highlights"><code>PROJECT_STATUS.md</code></a>.</p> <p>Under D-070, static batching, speculative decoding / native MTP, MoE versus dense execution, quantization, and reasoning-length variance are five stress tests of Q4&#39;s single thesis. The harness must instrument all five axes and all five have strict-valid L0 smoke-bundle support plus characterization commitments, but every study remains floor-gated, capped at L2, and sequenced after Window A. See the fuller <a href="PROJECT_STATUS.md#summary">Q4 architectural stress-test agenda</a> in <code>PROJECT_STATUS.md</code>.</p> <p>D-075 now folds a ranked extension-axis evaluation into that same agenda without proliferating theses: DSpark/DFlash break-even and control riders, on-device quantized KV, one named hybrid pair, and attached cache/context/kernel/backend provenance work. Every admitted unit remains a floor-gated candidate at or below L2 with a named forbidden upgrade; unresolved runtime and device-fit questions stay NEEDS-WEB, and Ed retains commitment authority. Separate lead-run DSpark/DFlash smokes established native MLX execution and per-round observability only. Their thinking-mode, unmatched-output throughput inversion is hypothesis-generating, not energy evidence.</p> <p>Window A remains open and still requires Ed and a quiet Mac. The repaired instrument has produced the 229-member a5-a8 diagnostic collection, and the merged screening and uncertainty-budget rules (D-078 clause 10) are ready for prospective use. The next claim attempt must follow the run-book: mint the drift bound inside the quiet window, then collect a start triplet, midpoint reference, and end triplet around the science members. A passing window will support the first claim-grade floors; only then do the a8 re-verdict and Splitwise sizing follow. The earlier 222-bundle floor publication remains a caveated historical record. Use the generated state kernel—not this summary—to select the next live or agent-lane step.</p> <p>A separate nine-bundle follow-on is now available as an explicitly <strong>exploratory, unmatched, no-claim</strong> observation block. All nine bundles are strict-valid and collection-usable but claim-evidence-flagged; each model ran three repetitions of the fixed five-item sentinel shape and emitted 1,280 generated output tokens per bundle.</p> <div class="table-scroll"><table> <thead> <tr> <th>unmatched configuration</th> <th align="right">mean gross suite energy — Apple M3 Max / powermetrics SoC rails (CPU + GPU + ANE)</th> <th align="right">mean gross energy/generated output token — same boundary</th> <th align="right">runtime-observed output throughput</th> </tr> </thead> <tbody><tr> <td>OLMoE-1B-7B BF16</td> <td align="right">229.028 J</td> <td align="right">178.928 mJ/token</td> <td align="right">122.361 tok/s</td> </tr> <tr> <td>Qwen3-4B INT4</td> <td align="right">362.772 J</td> <td align="right">283.416 mJ/token</td> <td align="right">106.519 tok/s</td> </tr> <tr> <td>Qwen3.5-122B-A10B INT4</td> <td align="right">1072.273 J</td> <td align="right">837.713 mJ/token</td> <td align="right">39.473 tok/s</td> </tr> </tbody></table></div> <p>These points differ in model scale, architecture, tokenizer, and quantization, so they do not establish a controlled scaling relation, architecture effect, or efficiency comparison. The stored per-generated-token field is idle-subtracted and appears only as D-067&#39;s labeled within-device secondary view in the <a href="docs/process_traces/2026-07-17-exploratory-block/results.md">bundle-cited extraction</a>, which also records spreads, every repetition, the floor comparison, and the Qwen thinking/config caveats.</p> <p>Remaining backends plug into the same adapter interfaces: the fixture-first 2K NVIDIA stack (SSH transport, node worker, nvidia-smi + vLLM adapters) includes NV-GATE-2 software hardening: per-backend raw-lineage verifier registration, usage-first vLLM streaming, and identity-aware process-survival handling. The NV-5 localhost lead gate passed 3/3, but ALL remote protocol pins remain PROVISIONAL pending first live hardware contact; Jetson Orin (2L) remains gated on device access.</p> <p>The landed C-028 arc includes the frozen analysis manifest, the production-uncertainty path, the campaign-verdict split, idle-dependence/HAC uncertainty, the inter-token metric, doctor preflight, and the contrast/claim engine. The analysis trio—manifest, verdict split, and contrast/claim engine—is complete. The six frozen legacy arms and 0.3.x/0.4.x dispatch rules remain explicit; landed software is not being presented as new live evidence. P0-003 closed with an iCloud Drive backup and a fresh restore that was strict-valid and byte-identical. No new live NVIDIA or quiet-Mac measurement is claimed here.</p> <p>The post-audit landings add request-scoped AXI-SA burst/decode semantics, freeze SPLIT-AP Part I before outcomes, close SITE-02&#39;s discovery and emitted-code regression work, and establish AXI-SB&#39;s <code>supported</code> verdict from lead-run B=2/B=4 Metal probes. The probes establish runtime feasibility and request observability only; they add no energy result. The corresponding AXI-SC pinned-runtime spike returned <code>unsupported_for_joulewise</code>: the external- draft path lacks the full proposal/acceptance/decode-boundary observability contract, and native MTP lacks a usable generation surface. No Mac energy leg was minted from that negative applicability result.</p> <p>The repository currently contains:</p> <ul> <li>Typed config and output schemas with JSON-Schema export and validation.</li> <li>Runtime, telemetry, and transport interface contracts, with shipped mock adapters and a backend registry.</li> <li>The runnable harness: bundle writer, controller lifecycle, reducer, a shared bundle read layer, static HTML report generator, and a CLI (<code>run</code>, <code>validate-bundle</code>, <code>reduce</code>, <code>report</code>).</li> <li>Example Mac-local and mock-local configs.</li> <li>Phase 1 methodology, feasibility, and measurement-design docs.</li> <li>A test suite run in CI on every push, including a mock end-to-end run and bundle validation. The canonical command below and CI output own the current result; reader docs intentionally do not copy its volatile count.</li> </ul> <h2 id="verify">Verify</h2> <pre><code class="language-bash">python3 -m unittest discover -s tests
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:5292:| Q1 | MET-WINDOW-C-01 | P1 Phase Gate | BLOCKED — FROZEN-PLAN-READINESS-RECORD (A reviewed FROZEN-PLAN READINESS RECORD exists before any collection night: frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight, launcher-verified), ED-5A (Ed section-5A window prep FRESH POST-MOVE (the 2026-08-02 laptop move invalidated settled-machine conditions; network time off, AC, settled machine, walk-away)) [QUIET-MAC] | Execute a reviewed fresh-claim collection plan beginning with Window C: no Window B member enters a replacement claim basis; split prospectively across windows C and D if the complete replacement cannot fit the 2-4 hour envelope with at least 20 percent failure margin. | The fresh-claim metrology plan replaces every still-desired Window-B claim component without using any Window-B member, under reviewed frozen-plan and validated-window controls. Evidence: A fresh-claim plan recollects every still-desired Window-B claim component beginning with Window C; no Window B member enters a replacement claim basis; The fresh plan includes the still-required C2, C4, and C5 collection scope under the frozen-plan discipline, split prospectively across windows C and D if one window cannot retain at least 20 percent failure margin inside the runbook's 2-4 hour envelope; Window operated under the validated protocols: bird-SIGSTOP with identity custody, guarded launcher, one-line arm messages with zero output streaming during idle-gate exposure, third-failure salvage rule; Whole-window verdict emitted by machinery that has passed MET-VERDICT-ADJ-01 adjudication; supersessions recorded once, pre-verdict; both roots backed up rc=0. Authority: [D-113 clauses 7-9 fresh-claim reset, readiness fence, and prospective C/D split](docs/decision_log.md). Acceptance: [MET-WINDOW-C-01 acceptance](docs/process/state_kernel.json). Fence: A window-C dangler seeking the b-ii mechanical license before D100-BII-BINDING-01 closes RETURNS TO THE GATE; the window itself may run (D-106 revisit clause). Fence: Before any collection night, the ordinary launcher verifies a reviewed FROZEN-PLAN READINESS RECORD binding the frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight (D-113 clauses 8-9 hard start fence). Fence: Plan root assembled and frozen before measurement; no plan edits after freeze (D-096 frozen-plan ratification). Fence: Zero agents AND zero operator output streaming during measurement idle gates; arm messages are one line; bird-SIGSTOP protocol with identity custody and fail-safe CONT trap on all exit paths (2026-08-01 run report: streaming-during-idle-gate hazard + bird-SIGSTOP protocol). Note: D-113 clauses 7 and 9: the former remainder-only scope is SUPERSEDED. A fresh-claim plan is required; no Window B member enters a replacement claim basis. If the full replacement exceeds the runbook's 2-4 hour envelope with at least 20 percent margin, split it prospectively across windows C and D. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:5374:limits expire after 24 hours so stale calibrations cannot be reused,
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:5461:| 2026-07-25 | SCREEN+BUDGET rules merged (PR #85) | D-078 clause 10 landed: separate gross and idle-subtracted screens, a nonzero drift allowance in every passing window's budget, a 24-hour bound expiry, and mock evidence barred from claims. | `docs/run_reports/2026-07-24-screen-budget-gauntlet.md` |

exec
/bin/zsh -lc "/usr/sbin/system_profiler SPHardwareDataType 2>/dev/null | sed -n '1,80p'; /usr/sbin/system_profiler SPMemoryDataType 2>/dev/null | sed -n '1,100p'; memory_pressure 2>/dev/null | head -40" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 290ms:
Hardware:

    Hardware Overview:

      Model Name: MacBook Pro
      Model Identifier: Mac15,9
      Model Number: Z1CM000M7LL/A
      Chip: Apple M3 Max
      Total Number of Cores: 16 (12 Performance and 4 Efficiency)
      Memory: 128 GB
      System Firmware Version: 18000.121.3
      OS Loader Version: 18000.121.3
      Serial Number (system): C3V22D19P4
      Hardware UUID: D29AF251-5827-5B5D-A291-74943BC9CFBC
      Provisioning UDID: 00006031-000808112669001C

Memory:

      Memory: 128 GB
      Type: LPDDR5
      Manufacturer: Micron

The system has 137438953472 (8388608 pages with a page size of 16384).

Stats: 
Pages free: 4398774 
Pages purgeable: 97264 
Pages purged: 16103973 

Swap I/O:
Swapins: 0 
Swapouts: 0 

Page Q counts:
Pages active: 1728860 
Pages inactive: 1775494 
Pages speculative: 154726 
Pages throttled: 0 
Pages wired down: 263870 

Compressor Stats:
Pages used by compressor: 7798 
Pages decompressed: 6459835 
Pages compressed: 6558470 

File I/O:
Pageins: 151156187 
Pageouts: 10022 

System-wide memory free percentage: 96%

exec
/bin/zsh -lc "rg -n \"def reset_peak_memory|reset_peak_memory|get_peak_memory|clear_cache|set_cache_limit|set_memory_limit\" /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm | head -160; nl -ba /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py | sed -n '705,760p'; nl -ba docs/run_reports/2026-07-07-flagship-qwen35-122b.md | sed -n '1,200p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
   705	        token_generator = (
   706	            (token, logprobs, False) for token, logprobs in token_generator
   707	        )
   708	    else:
   709	        kwargs.pop("max_kv_size", None)
   710	        kwargs.pop("prompt_progress_callback", None)
   711	        token_generator = speculative_generate_step(
   712	            prompt, model, draft_model, **kwargs
   713	        )
   714	    with wired_limit(model, [generation_stream]):
   715	        tic = time.perf_counter()
   716	        for n, (token, logprobs, from_draft) in enumerate(token_generator):
   717	            if n == 0:
   718	                prompt_time = time.perf_counter() - tic
   719	                prompt_tps = prompt.size / prompt_time
   720	                tic = time.perf_counter()
   721	            if token in tokenizer.eos_token_ids:
   722	                break
   723	
   724	            detokenizer.add_token(token)
   725	            if (n + 1) == max_tokens:
   726	                break
   727	
   728	            yield GenerationResponse(
   729	                text=detokenizer.last_segment,
   730	                token=token,
   731	                logprobs=logprobs,
   732	                from_draft=from_draft,
   733	                prompt_tokens=prompt.size,
   734	                prompt_tps=prompt_tps,
   735	                generation_tokens=n + 1,
   736	                generation_tps=(n + 1) / (time.perf_counter() - tic),
   737	                peak_memory=mx.get_peak_memory() / 1e9,
   738	                finish_reason=None,
   739	            )
   740	
   741	        detokenizer.finalize()
   742	        yield GenerationResponse(
   743	            text=detokenizer.last_segment,
   744	            token=token,
   745	            logprobs=logprobs,
   746	            from_draft=from_draft,
   747	            prompt_tokens=prompt.size,
   748	            prompt_tps=prompt_tps,
   749	            generation_tokens=n + 1,
   750	            generation_tps=(n + 1) / (time.perf_counter() - tic),
   751	            peak_memory=mx.get_peak_memory() / 1e9,
   752	            finish_reason="stop" if token in tokenizer.eos_token_ids else "length",
   753	        )
   754	
   755	
   756	def generate(
   757	    model: nn.Module,
   758	    tokenizer: Union[PreTrainedTokenizer, TokenizerWrapper],
   759	    prompt: Union[str, List[int]],
   760	    verbose: bool = False,
     1	# 2026-07-07: Flagship-Class Model Benchmarked — Qwen3.5-122B-A10B on the M3 Max
     2	
     3	## Addendum (2026-07-08, C-011)
     4	
     5	The original wording below that energy per output token "scaled almost exactly
     6	linearly with ACTIVE parameter count" and showed "textbook memory-bound MoE
     7	behavior" is superseded per C-005/DOC-007. The two Mac/MLX/powermetrics points
     8	are strict-valid but confounded by model size, architecture, quantization, and
     9	runtime details. They are hypothesis-generating for Q4's fixed-vs-marginal
    10	model, not an active-parameter scaling result.
    11	
    12	User direction: run the benchmark on "the top of the line model that can
    13	run on this 128 GB machine." Model selected by a web-verified research
    14	pass (candidates and exclusions recorded below), mirrored per R-014, and
    15	run through the unmodified vertical-slice harness the same day.
    16	
    17	## Selection (D-016 flagship addendum)
    18	
    19	Winner: `mlx-community/Qwen3.5-122B-A10B-4bit` (rev `e9c67b0`, 65 GB on
    20	disk, 122B-total / 10B-active MoE, reasoning model, 262K context,
    21	Feb 2026 generation; Artificial Analysis Intelligence Index 32 vs
    22	gpt-oss-120b's 24). Runners-up: gpt-oss-120b-MXFP4 (~63 GB, older
    23	generation, known mlx-lm prefill instability), GLM-4.5-Air-4bit (60 GB,
    24	mid-2025 gen). Excluded for size: Qwen3.5-397B, DeepSeek V4-Flash
    25	(~107-140 GB footprints), GLM-4.7 (355B), MiniMax, Kimi K2.
    26	
    27	Sanity generation (mlx_lm 0.31.3 loads `qwen3_5_moe` natively): 48.9
    28	tok/s decode, 68.9 GB peak memory — fits without any wired-limit change.
    29	
    30	## Results — 3/3 reps succeeded, all `validate-bundle --strict` green
    31	
    32	Config `mac_mlx_qwen35_122b.json` (hash-pinned): identical workload shape
    33	to the small-model flagship (same prompt, 512 output tokens, 10 Hz,
    34	30 s idle, 3 reps) for direct comparison.
    35	
    36	| rep | gross J | idle-sub J | mJ/out-token | prefill J | decode J | TTFT ms | tok/s | obs Hz | idle W |
    37	|---|---|---|---|---|---|---|---|---|---|
    38	| 1 | 303.5 | 299.3 | 584.5 | 0.551 | 303.0 | 265 | 46.3 | 8.89 | 0.38 |
    39	| 2 | 303.5 | 298.7 | 583.4 | 0.511 | 302.9 | 275 | 46.1 | 8.88 | 0.42 |
    40	| 3 | 305.1 | 298.1 | 582.2 | 0.464 | 304.6 | 275 | 46.0 | 8.80 | 0.61 |
    41	
    42	Gross CV across reps: **0.3%** (the tightest yet). Model load 12.8 s
    43	(warm file cache). Idle baselines clean this time (0.38-0.61 W — the
    44	rep-1 contamination seen with the small model did not recur; worth
    45	watching whether cold-start sessions reproduce it).
    46	
    47	## Cross-model comparison (same workload, same harness, same machine)
    48	
    49	| | Qwen2.5-1.5B-4bit | Qwen3.5-122B-A10B-4bit | ratio |
    50	|---|---|---|---|
    51	| Active params | 1.5B | 10B | 6.7× |
    52	| Gross energy / 512 tok | ~47 J | ~304 J | 6.5× |
    53	| Energy per output token | ~87 mJ | ~583 mJ | **6.7×** |
    54	| Decode throughput | 257 tok/s | 46 tok/s | 0.18× |
    55	| TTFT | ~94 ms | ~270 ms | 2.9× |
    56	| Implied decode power | ~23.5 W | ~27.5 W | 1.17× |
    57	
    58	**Finding (first real Q4 data point):** energy per output token scaled
    59	almost exactly linearly with ACTIVE parameter count (6.7× params →
    60	6.7× mJ/token), while total parameters grew 81×. Decode POWER barely
    61	moved (~23.5 → ~27.5 W — the SoC runs near its power envelope either
    62	way); the energy difference is almost purely decode TIME. This is
    63	textbook memory-bound MoE behavior and exactly the kind of
    64	fixed-vs-marginal structure Q4's model fits — two points on the curve
    65	now exist.
    66	
    67	## Bookkeeping
    68	
    69	- Corpus (3 bundles + manifest) backed up per R-016.
    70	- D-016 flagship addendum recorded (second provisional model,
    71	  user-directed; D-016 full closure still open).
    72	- Queue: flagship-run completed row added.

codex
A key source correction changes Gate 3: Qwen3-30B-A3B advertises `model_type: qwen3_moe`, so its live interception point is `qwen3_moe.py`, not the `qwen3_next.py` path reviewed for the retired 122B candidate. The installed runtime exposes IDs and normalized routing weights only as local intermediates; there is no observer/callback seam. Therefore an auditable trace requires an instrumented derivative of the pinned runtime, with a new stack identity and its own floors.
exec
/bin/zsh -lc "rg -n \"L2|claim ceiling|MoE|matched.active|D-016|D-070|OUTPUT-IDENTITY|TELEMETRY-PERTURBATION|tokenizer|cross-model|gross\" docs/contracts/claims_ladder.md docs/contracts/token_normalization.md docs/research_question_registry.md docs/decision_log.md docs/axi-handoff.md | head -320; nl -ba docs/contracts/claims_ladder.md | sed -n '1,220p'; nl -ba docs/contracts/token_normalization.md | sed -n '1,240p'; rg -n \"## D-016|## D-070|C-023-OUTPUT-IDENTITY|C-023-TELEMETRY-PERTURBATION\" docs/decision_log.md docs/research_question_registry.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
docs/axi-handoff.md:56:  reporting with **gross energy as the headline basis for all
docs/axi-handoff.md:60:  prefill + decode) is **fit on gross energy** across the workload
docs/axi-handoff.md:85:MTP, MoE vs dense, quantization, reasoning-length variance** — framed as
docs/axi-handoff.md:88:currently P1-006-gated), C5-2.5 and C-023-OUTPUT-IDENTITY (spec decode),
docs/axi-handoff.md:89:C5-1.1 / C5-1.9 / RQ-TWO-MODEL-ACTIVE-NONCLAIM (MoE/dense), C5-1.12 and
docs/axi-handoff.md:93:(expert-activation diversity vs batch size; candidate, ceiling L2,
docs/axi-handoff.md:94:forbidden upgrade: no MoE-serving-efficiency generalization from one
docs/axi-handoff.md:121:Record the D-entry per §1: gross-headline for cross-device/split claims;
docs/axi-handoff.md:123:fit on gross. Rivoire's energy-proportionality argument is the recorded
docs/axi-handoff.md:177:gross-first for any cross-config number), the harness/benchmark
docs/axi-handoff.md:194:- Make C-023-OUTPUT-IDENTITY executable: output equivalence/divergence
docs/axi-handoff.md:217:model-selection input feeding D-016, not as runtime work.
docs/axi-handoff.md:221:Matched dense/MoE pair proposal for D-016 (same family, matched active
docs/axi-handoff.md:232:- **AP-5 extension:** dense/MoE contrast rides inside the 2M baseline
docs/axi-handoff.md:233:  campaign (zero extra quiet-machine cost) if D-016 selects the pair.
docs/axi-handoff.md:248:2. **Characterized-claim commitments** — default: MoE/dense (free via
docs/axi-handoff.md:249:   D-016 inside the 2M campaign) + static batching (one quiet-machine
docs/axi-handoff.md:254:3. **D-016 model pair** — needs Ed (and advisor input in flight). Present
docs/axi-handoff.md:268:- No claim-ceiling renegotiation: everything in §4 caps at L2 (L3 only
docs/contracts/claims_ladder.md:44:  block order is forced, the claim must say so and remain below L2 unless the
docs/contracts/claims_ladder.md:53:- (2026-07-09) Token-denominated metrics and cross-tokenizer comparison
docs/contracts/claims_ladder.md:63:| L2 - Comparative Result | Condition A differed from condition B within the same measurement boundary under a named workload and policy. | n >= 5 per condition; strict-valid bundles; 2M experiment manifest order recorded and interleaved where permitted; confidence intervals reported; effect clears the Phase 4 detection floor; same boundary label, or a named calibration bundle if boundaries differ. | cross-boundary winner without calibration, universal, architecture-wide conclusion, extrapolated crossover |
docs/contracts/token_normalization.md:3:Status: binding for token-denominated metrics, cross-tokenizer comparison
docs/contracts/token_normalization.md:20:Request energy means gross joules per request under a named measurement
docs/contracts/token_normalization.md:29:`energy_request_j` is not renamed or redefined; reader-facing gross request
docs/contracts/token_normalization.md:30:energy is `gross_energy_j`.
docs/contracts/token_normalization.md:32:Per-token metrics never replace gross request energy in a headline. They may
docs/contracts/token_normalization.md:33:appear as companion metrics when their tokenizer scope, energy basis, and
docs/contracts/token_normalization.md:38:table containing token-normalized metrics, gross request energy must be
docs/contracts/token_normalization.md:40:states its basis and boundary; any cross-configuration number is gross-first.
docs/contracts/token_normalization.md:45:to a named tokenizer. They describe the measured stack and tokenizer that
docs/contracts/token_normalization.md:46:produced the denominator; they are not tokenizer-blind work units.
docs/contracts/token_normalization.md:53:  efficiency, gross joules per committed output token is the companion
docs/contracts/token_normalization.md:54:  denominator; gross joules per accepted draft token is a speculation-enabled
docs/contracts/token_normalization.md:58:- The tokenizer identity must be named wherever a per-token number appears:
docs/contracts/token_normalization.md:59:  tokenizer name, revision, class, and vocabulary size where available, per
docs/contracts/token_normalization.md:68:- `J/token` values from different tokenizers are NEVER an efficiency ranking
docs/contracts/token_normalization.md:83:complete batch group and its governed gross metric is
docs/contracts/token_normalization.md:84:`batch_group_gross_energy_j` on window class `gross_batch_group`. It must not
docs/contracts/token_normalization.md:87:gross energy remains `gross_energy_j` on `gross_request`.
docs/contracts/token_normalization.md:91:Any comparison across tokenizer families, or across model families with
docs/contracts/token_normalization.md:92:different tokenizers, must do one of two things:
docs/contracts/token_normalization.md:94:1. Carry companion denominators that are tokenizer-independent, such as
docs/contracts/token_normalization.md:103:| "more efficient per token" | Cross-tokenizer or cross-model-family ranking. | "lower `J/token` for [stack A] under tokenizer [name/revision/class/vocab size] than [stack B] under tokenizer [name/revision/class/vocab size], with request energy [direction/value] under [boundary]." |
docs/contracts/token_normalization.md:104:| "better J/token" | Cross-family efficiency conclusion. | "different tokenizer-scoped `J/token` under [stack A tokenizer name/revision/class/vocab size] and [stack B tokenizer name/revision/class/vocab size]; request energy is [direction/value] under [boundary]." |
docs/contracts/token_normalization.md:106:| Tokenizer-blind "energy per token" leaderboard language | Ranking stacks without naming tokenizer identity and request energy. | "tokenizer-scoped companion metrics for [stack A tokenizer name/revision/class/vocab size] and [stack B tokenizer name/revision/class/vocab size], reported beside request energy." |
docs/contracts/token_normalization.md:107:| Treating token counts as comparable work units across vocabularies | Any inference that equal token counts imply equal semantic, byte, or character work across tokenizers. | "same-content item energy" or "`J/char`/`J/byte` companion denominator, with tokenizer-scoped `J/token` only as context." |
docs/contracts/token_normalization.md:109:Within one tokenizer identity, per-token comparisons still obey the claims
docs/contracts/token_normalization.md:111:only prevents token denominators from being promoted into tokenizer-blind
docs/contracts/token_normalization.md:145:Event-semantics-v2 bundles record the actually loaded target tokenizer at
docs/contracts/token_normalization.md:146:`metadata.runtime.target_tokenizer_identity` with exact name, immutable
docs/contracts/token_normalization.md:147:revision, and `tokenizer_artifact_sha256`. C-023 compares all three strings
docs/research_question_registry.md:5:aliases, status, claim ceilings, owners, gates, and pre-hardware readiness so
docs/research_question_registry.md:39:| Q1 | Split reduces energy | research question | promoted | L2 boundary-labeled; stronger only with calibration | no uncalibrated cross-boundary total-energy winner | none-yet | Phase 3 split; P1-004; P1-006 | hardware | fully | Central split question; total energy must be decomposed and boundary-labeled. |
docs/research_question_registry.md:40:| Q2 | Link bandwidth sensitivity | research question | promoted | L2 | no nominal-link crossover without measured links | none-yet | Phase 3 split; P1-004 | hardware | fully | Clean interconnect sensitivity question; link throughput and transfer energy must be measured. |
docs/research_question_registry.md:41:| Q3 | Split energy-latency Pareto | research question | promoted | L2 | no Pareto claim without frozen set and latency metric | none-yet | Phase 3 split | hardware | fully | Requires a fixed comparison set and latency metric per figure. |
docs/research_question_registry.md:42:| Q4 | Fixed-vs-marginal energy model; C5-2.14 cache-policy coefficient rider | research question | promoted | L3 | no holdout-prediction claim without AP-1 floor and residual checks | AP-1 | P2-019 q4_l3_shape_grid_v1 | floor | analysis-plan-only | Strongest predictive science row; includes compositional split-energy prediction only when transfer terms exist. C5-2.14 is a candidate rider capped at L2, earliest PF, with no coefficient-direction claim below P2-015 floors ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:43:| Q5 | Ranking stability | research question | promoted | L2 | no uncalibrated cross-device winner; no ranking where gap below MDE | AP-3 | 2M; Window B grid | floor | analysis-plan-only | Promoted within-machine ranking question; workload-axis analogue C5-W.3 remains a separate candidate row. |
docs/research_question_registry.md:44:| Q6 | Boundary sensitivity; C5-2.10 boundary-directional bias quantification | research question | promoted | L2; L4 only with replication | no wall/rail conclusion flip claim without paired boundary plan | none-yet | P1-003 wall meter; F11 | hardware | fully | Registry indexes C5-2.10 as the C5 elaboration of promoted Q6. |
docs/research_question_registry.md:46:| C5-1.11 | Dark silicon; rail utilization; ANE-dark finding | research question | candidate | L2 structural | no true silicon-energy fraction from modeled rails | none-yet | P2-009 rich telemetry; C5-1.8 runtime grid | software | analysis-plan-only | Measures modeled-rail utilization structure, not physical absolute rail truth. |
docs/research_question_registry.md:47:| C5-1.3 | CPU:GPU phase division; rail/DVFS phase signatures; prefill/decode power asymmetry | research question | candidate | L2 structural | no short-phase joules when windows are under-resolved | none-yet | 2M with P2-009 | floor | analysis-plan-only | Merges the banked CPU:GPU phase question with C5-1.3 telemetry framing. |
docs/research_question_registry.md:48:| RQ-KV-GROWTH | KV-growth decode drift; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | banked | L1/L2 chunked | no per-token joule claims; no attention-vs-FFN fraction from context slopes | none-yet | none | floor | analysis-plan-only | Candidate riders, earliest PF: bounded-window KV marginal slope and named-artifact attention/context slope; both retain chunked-window/floor discipline and stay attached rather than becoming independent rows ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:49:| C5-1.5 | Cooldown recovery as thermal characterization; cooldown-recovery curves | research question | candidate | L1/L2 | no claim that power recovery proves thermal-state equality | none-yet | none | floor | analysis-plan-only | Turns cooldown tails and cap-hit rates into reportable methodology evidence. |
docs/research_question_registry.md:50:| C5-1.10 | Failure frontier | research question | candidate | L1/L2 descriptive | no silent discard of failures; no population claim from one memory class | none-yet | none | software | analysis-plan-only | Structured `unsupported`, fit, swap, throttle, and cap-hit outcomes become data. |
docs/research_question_registry.md:51:| C5-1.7 | Cold-start / keep-warm energy; reload-vs-resident scheduling | research question | banked | L2 after harness extension | no breakeven without load-window and resident-idle sampling | none-yet | none | software | analysis-plan-only | Review and bank both identify reload-vs-resident as the same question. |
docs/research_question_registry.md:52:| C5-1.9 | Energy-per-correct-answer vs difficulty; MoE-vs-dense controlled ladder | research question | banked | L2 after envelope and denominator guards | no intelligence-per-joule; no `difficulty causes energy` | AP-5 | P2-010a plus P2-010b plus later scored campaign | substrate | analysis-plan-only | Correctness remains quarantined annotation under the C-004/C-014 rules. |
docs/research_question_registry.md:53:| C5-2.5 | Speculative-decoding energy; C5-2.5b proposal-work rider; C5-2.5c break-even rider | research question | banked | L2 | no efficiency claim without output equivalence and accepted-token accounting | none-yet | none | software | analysis-plan-only | C5-2.5c is the primary PF Q4 rider, C5-2.5b its PF secondary, and C5-2.5d the mandatory PF contamination control; C5-2.5a remains a deferred NS bank rider. `C-023-OUTPUT-IDENTITY` binds all efficiency contrasts ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:54:| RQ-POWER-MODE | Power-mode Pareto | research question | banked | L2 possible | no OS-mode conclusion until power mode is a first-class config field | none-yet | none | software | analysis-plan-only | Waits on config/environment capture for OS power modes. |
docs/research_question_registry.md:61:| RQ-MLX-KV-REPLAY | Same-machine MLX KV replay token identity and size prediction; C5-2.13 | capability claim | answered-L1 | L1 feasibility | no cross-machine portability claim | none-yet | Stage 3.0.1 | software | no | The L1 feasibility result remains answered; candidate C5-2.13, earliest PF and capped at L2, attaches the same-machine energy-crossover rider without cross-stack generalization ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:63:| RQ-SHAPE-ENERGY | Workload shape changes request energy | research question | candidate | L2 | no causal token-shape claim beyond AP-2 contrasts | AP-2 | 2M | floor | analysis-plan-only | Distinct from Q4 because it describes shape contrasts rather than holdout prediction. |
docs/research_question_registry.md:64:| C5-1.1 | Active-parameter energy scaling | research question | candidate | L2 pairwise only unless larger predeclared model set | no active+total+KV regression on 4-6 models | none-yet | P2-024 shortlist | floor | analysis-plan-only | C-014 caps the tempting wording; registry hygiene, not re-adjudication. |
docs/research_question_registry.md:65:| C5-1.2 | Context-length energy scaling; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | candidate | L2/L3 if modeled | no short-prompt phase point claims; no wall implication from SoC rails | none-yet | none | floor | analysis-plan-only | Natural local-inference question with chunked phase limits; the two candidate PF riders remain capped at L2 and forbid module attribution from context-associated slopes ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:66:| C5-1.4 | DVFS residency as throttling early-warning | research question | candidate | L2 if prediction rule fixed | no prediction claim without horizon and rule | none-yet | none | software | analysis-plan-only | Convert characterization to a predeclared warning rule before claiming prediction. |
docs/research_question_registry.md:67:| C5-1.6 | Sampling-strategy energy overhead | research question | candidate | L2 if above floor | no telemetry-perturbation claim from this row | none-yet | P2-024 shortlist | floor | analysis-plan-only | Bank row is greedy vs temperature/top-p/beam overhead, not sampler instrumentation cost. |
docs/research_question_registry.md:68:| C5-1.8 | Runtime energy attribution; same-silicon kernel-layer provenance rider | research question | candidate | L2 stack-vs-stack | no `belongs to runtime` or `belongs to kernel layer` language when artifacts/formats differ; no runtime-agnostic kernel claim | none-yet | P2-024 shortlist | floor | analysis-plan-only | Candidate NV provenance rider stays inside the stack-conditioned comparison; it does not mint C5-1.13 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:69:| C5-1.12 | Quantization benefit decomposition, Mac leg | research question | candidate | L2 | no quantization efficiency claim without output divergence reporting | none-yet | P2-024 shortlist | floor | analysis-plan-only | Splits benefit into lower watts vs shorter time on one stack/family. |
docs/research_question_registry.md:70:| C5-W.1 | Category beyond token counts; Token-Shape Sufficiency Null | research question | candidate | L2 | no category effect below floor or without shape control | AP-4 | jw_mixed_v1 after P2-010a | substrate | analysis-plan-only | Strong null-or-effect design for workload-category residuals. |
docs/research_question_registry.md:71:| C5-W.2 | Thinking-token inflation | research question | candidate | L2 | no cognition claim; attribute only to emitted-token/stop distributions | none-yet | jw_mixed_v1 natural-EOS pilot | substrate | analysis-plan-only | Operational-cost view for reasoning models under natural EOS. |
docs/research_question_registry.md:72:| C5-W.3 | Category energy-ranking stability; workload-axis Q5 analogue | research question | candidate | L2 | no category ranking claim where rank gap is below MDE or without workload-expansion gate | none-yet | jw_mixed_v1 workload expansion | substrate | analysis-plan-only | Workload-axis analogue of promoted Q5, not the same ratified question; asks whether code/long-context/reasoning categories flip model/quant ordering. |
docs/research_question_registry.md:73:| C5-I.3 | C5-W.4; FLORES tokenizer fertility tax | research question | candidate | L2 | no tokenizer efficiency ranking without semantic and token-matched legs | none-yet | FLORES after HumanEval smoke | substrate | fully | C5-I.3 and C5-W.4 are the same FLORES fertility question. |
docs/research_question_registry.md:74:| C5-I.1 | External benchmark energy signatures | research question | candidate | L2 | no benchmark capability or accuracy claim | none-yet | import/export contracts | substrate | fully | Needs matched shape/output policy before family-level energy signatures. |
docs/research_question_registry.md:75:| C5-I.2 | Published-difficulty strata vs energy | research question | candidate | L1 association; L2 only if preplanned repeated bundles | no `difficulty causes energy` | none-yet | import/export contracts | substrate | fully | Weak/secondary because source difficulty labels are heterogeneous. |
docs/research_question_registry.md:76:| C5-I.4 | Harness overhead floor | methodology artifact | candidate | L1/L2 | no item energy claim when harness overhead dominates unnoticed | none-yet | P2-022 shim | substrate | fully | Methodology question for marked external harnesses. |
docs/research_question_registry.md:77:| C5-I.5 | Prompt-template energy sensitivity | research question | candidate | L2 | no prompt-quality or capability claim | none-yet | import/export contracts | substrate | fully | Same external item, canonical vs JouleWise-rendered prompt format. |
docs/research_question_registry.md:78:| RQ-CONTENT-SENTINEL | Synthetic prompt content sentinel; fixed-shape content sensitivity | research question | candidate | L2 | no content-effect claim unless realized shape/stop policy stays matched and effect clears floor; no broad content-neutrality claim beyond the five tested AP-6 conditions | AP-6 | P2-020 content sentinel | substrate | analysis-plan-only | Tests whether synthetic prompt content matters at fixed shape under the AP-6 ids-native no-BOS sentinel design. |
docs/research_question_registry.md:79:| RQ-ENERGY-VARIANCE | Sampling-induced energy variance; energy-at-risk per prompt; lucky-short-reasoning variance | research question | candidate | L2 within boundary | no intelligence-per-joule or correctness-causal claim (C-004 quarantine); variance claims need repeated-bundle n sized for variance estimation and floor-gated residuals; per-bundle sampler seeds must be recorded | none-yet | none (post-floor; reasoning model on current Mac feasible) | floor | analysis-plan-only | Ed-added 2026-07-09 row: distribution (not just mean) of request energy for a fixed hard prompt under sampling; decomposable into reasoning-length vs residual variance via recorded output token IDs + deterministic replay of sampled paths (P2-025 capture + 3.0.1 replay make paths replayable). |
docs/research_question_registry.md:80:| RQ-SESSION-SHAPE | Session-shape energy | research question | candidate | L2/L3 depending holdout | no app-session prediction without holdout validation | none-yet | suite profiles after P2-010a | substrate | analysis-plan-only | Tests whether Q4 coefficients compose in realistic session ecology. |
docs/research_question_registry.md:81:| RQ-ORDER-POSITION | Order-position effects | methodology artifact | candidate | L2 | no category/thermal inference without executable order policy | none-yet | suite profiles after ordering executability | substrate | analysis-plan-only | Drift/order probe; not a headline result. |
docs/research_question_registry.md:82:| RQ-CACHE-PREFIX | Cache/prefix economics; C5-2.13 | research question | candidate | L2 | no bundled cache-state conclusion without exact cache policy; no crossover generalization beyond the measured prompt-length ladder | none-yet | none | software | analysis-plan-only | Covers prefix reuse, resident state, and prompt-cache warmth; candidate C5-2.13 attaches a same-machine/same-stack energy crossover at earliest PF ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:83:| RQ-AXI-HYBRID-PAIR | Named hybrid (SSM/attention)-vs-pure-transformer pair | research question | candidate | L2 pair-specific characterization | no architecture-class efficiency generalization, causal SSM-mechanism attribution, or tokenizer-blind ranking from one named pair | none-yet | post-floors named-pair campaign | floor | analysis-plan-only | Earliest PF; floor-gated and bindingly worded as “this named pair”; controlled-pair availability remains NEEDS-WEB ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:84:| RQ-EXTERNAL-MARKED-RUNNER | External marked-runner energy layer | capability claim | candidate | L1/L2 with AP row | no accuracy, leaderboard, pass@k, or capability interpretation | none-yet | P2-022 | substrate | fully | Export-layer feasibility becomes research only when overhead/energy comparisons are specified. |
docs/research_question_registry.md:86:| C5-2.1 | Quantization decomposition, cross-stack | research question | candidate | L2 | no cross-boundary quant winner without calibration | none-yet | P1-006 CUDA/3050 manifests | hardware | fully | Extends C5-1.12 to CUDA/GGUF legs. |
docs/research_question_registry.md:87:| C5-2.2 | Batch size and prefill/decode energy split | research question | candidate | L2 | no serving conclusion without latency-bound policy | none-yet | P1-006 CUDA/3050 manifests | hardware | fully | Strong systems question for serving-style hardware and batching backend. |
docs/research_question_registry.md:88:| C5-2.3 | Predicted-vs-measured KV economics | research question | candidate | L2 | no KV economics claim without measured payload/link/deserialization terms | none-yet | P1-004 plus P1-006 | hardware | fully | One of the strongest Phase 3 questions; useful even if live split fails. |
docs/research_question_registry.md:89:| C5-2.4 | KV-cache quantization end-to-end; C5-2.11 on-device MLX leg | research question | candidate | L2 | no byte-saving equals energy-saving claim | none-yet | none | software | analysis-plan-only | Transfer leg still depends on cache portability; candidate C5-2.11 is the PF on-device MLX-scoped leg and also binds output-equivalence evidence ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:90:| C5-2.11 | On-device quantized-KV energy | research question | candidate | L2, per-boundary, MLX-scoped | no byte-saving-equals-energy-saving claim; no cross-runtime generalization from MLX alone; no quality-neutrality claim without C-023-style output-equivalence evidence | none-yet | post-floors Mac cache-policy campaign | floor | analysis-plan-only | Earliest PF; indexed under C5-2.4/C5-1.12/C-023-QUALITY-EQUIV-QUANT and runnable without the transfer leg ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:91:| C5-2.6 | Request coalescing under latency bound | research question | candidate | L2 | no scheduler optimum without arrival trace and latency policy | none-yet | none | hardware | analysis-plan-only | Useful but drifts toward scheduler research. |
docs/research_question_registry.md:92:| C5-2.7 | Device perf/W rankings with runtime held constant; kernel-provenance rider | research question | candidate | L2 within boundary; L4 with second unit/calibration | no generic hardware or cross-vendor kernel-API ranking from heterogeneous boundaries | none-yet | P1-006; 3080 Ti borrow window | hardware | fully | Candidate NV rider records attention-kernel/BLAS/graph provenance and remains per-boundary at L2; NEEDS-WEB feasibility stays open ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:93:| C5-2.8 | Placement-policy optimality from Q4 coefficients | research question | candidate | L2/L3 | no optimal-placement claim without measured split validation cells | none-yet | Phase 3 full set | hardware | fully | Uses Q4 coefficients plus measured transfer costs to choose placement. |
docs/research_question_registry.md:96:| C5-3.2 | Battery-path energy and modeled-rail validation | research question | candidate | L2/L4 bridge | no full-system claim from modeled rails alone | none-yet | USB-C PD analyzer | hardware | fully | Complements AC wall meter with a second physical boundary. |
docs/research_question_registry.md:100:| C-023-TELEMETRY-PERTURBATION | Telemetry perturbation cost | methodology artifact | candidate (C-023) | L1/L2 floor component | no near-floor claim without telemetry-on/off ABBA check | none-yet | P2-015 component | floor | analysis-plan-only | New coverage-gap row; distinct from C5-1.6 sampling-strategy overhead. |
docs/research_question_registry.md:101:| C-023-VERSION-DRIFT | OS/runtime version-drift forensics; OS/driver/runtime update forensics | research question | candidate (C-023) | L1/L2 stack-conditioned | no version regression claim without before/after pinned bundles | none-yet | none | software | analysis-plan-only | Turns version churn into a named science/application row. |
docs/research_question_registry.md:103:| C-023-OUTPUT-IDENTITY | Output-token identity effects; binding gate for C5-2.5a/b/c/d | methodology artifact | candidate (C-023) | L1/L2 depending comparison | no quant/runtime/spec-decoding efficiency claim without equivalence or divergence report | none-yet | none | software | analysis-plan-only | Fixed output-token count is not fixed decoded work; binding for the PF/NS speculative-decoding riders admitted by D-075 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:104:| C-023-IDLE-STATIONARITY | Idle-baseline stationarity | methodology artifact | candidate (C-023) | L1 methodology | no idle-subtracted conclusion without idle model-choice sensitivity | none-yet | P2-015 component | floor | analysis-plan-only | D-067 CLOSED the headline-basis question: gross energy within the named boundary is primary. This row stays alive only to test how idle-model choice affects conclusions in the labeled within-device SECONDARY view. |
docs/research_question_registry.md:105:| C-023-QUALITY-EQUIV-QUANT | Quality-equivalent quantization comparisons; C5-2.11 gate | research question | candidate (C-023) | L2 after equivalence rule | no quantization efficiency or quality-neutrality claim without AP-level equivalence rule | none-yet | none | software | analysis-plan-only | C5-2.11's candidate PF on-device KV leg binds this gate; footprint savings alone do not establish energy or quality neutrality ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:106:| C-023-COEFF-TRANSPORT | Coefficient transport synthetic-to-realistic; energy model portability across workload mixtures | research question | candidate (C-023) | L2/L3 depending holdout | no realistic-session prediction from synthetic grid without transport validation | none-yet | suite traces after Q4 | substrate | analysis-plan-only | Explicitly tests Q4 coefficient transport from synthetic grids to realistic app traces. |
docs/research_question_registry.md:107:| APP-PROMPT-PROFILER | Prompt/template energy profiler | application idea | candidate | internal L1/L2 only | no prompt-quality claim | none-yet | none | software | analysis-plan-only | Product-facing use of prompt/template energy sensitivity. |
docs/research_question_registry.md:109:| APP-CI-ENERGY-GATES | CI energy-regression gates | application idea | candidate | internal L1/L2 after floors | no CI failure threshold below detection floor | none-yet | P2-015 prerequisite | floor | analysis-plan-only | Needs floors, env snapshots, and baseline-refresh policy. |
docs/research_question_registry.md:110:| APP-VENDOR-PRESS-AUDIT | Vendor/press claim audit | application idea | candidate | boundary-named L1/L2 | no absolute device-energy verdict without calibration | none-yet | none | hardware | analysis-plan-only | Can audit specific boundary/workload claims, not universal efficiency. |
docs/research_question_registry.md:123:  4-6-model designs at descriptive L2 pairwise contrasts unless the model set
docs/decision_log.md:41:| D-016 | Benchmark model selection | open (provisional small-model pick 2026-07-06; opens 2G only) |
docs/decision_log.md:57:| D-032 | `phase_energy_j` is gross-only in summary v0.1 | accepted |
docs/decision_log.md:63:| D-038 | Analysis plans bind L2/L3 claims to pre-registered comparison rows | accepted |
docs/decision_log.md:92:| D-067 | Idle reporting basis — gross headline; idle-subtracted is a labeled within-device secondary view | accepted |
docs/decision_log.md:95:| D-070 | Architectural-axes extension agenda (AXI): scope, claim posture, batch-axis rulings | accepted |
docs/decision_log.md:98:| D-073 | D-016 device-list amendment: Mac + 3080 Ti primary fleet, 12 GiB cap | accepted |
docs/decision_log.md:838:## D-016: Benchmark model selection
docs/decision_log.md:1359:inside the integrated window, inflating gross energy, the
docs/decision_log.md:1661:reduced summaries, and retains the metric-specific `gross_request` and
docs/decision_log.md:1811:~72-76 GB inference footprint, 122B MoE / 10B active, Feb 2026
docs/decision_log.md:1815:Qwen2.5-1.5B pick — it does not close D-016 (mid-model/CUDA/GGUF
docs/decision_log.md:1853:## D-032: `phase_energy_j` is gross-only in summary v0.1
docs/decision_log.md:1868:1. Store gross phase energy only in `phase_energy_j`.
docs/decision_log.md:1870:3. Store both gross and idle-subtracted phase maps in summary v0.1.
docs/decision_log.md:1872:Decision: option 1. `phase_energy_j` is gross joules only in summary
docs/decision_log.md:1876:Considerations: gross phase windows are direct integrations over the
docs/decision_log.md:1884:from gross phase energy, idle baseline, and phase durations, but those
docs/decision_log.md:1899:counts do not prove realized prompt content. A tokenizer or generator
docs/decision_log.md:1907:   tokenizer/model drift under the same config.
docs/decision_log.md:1912:   identity, tokenizer identity/revision/class/vocab size, model source
docs/decision_log.md:1928:identity, tokenizer/model identity, generator identity, and
docs/decision_log.md:1935:Revisit when: a new runtime cannot expose token IDs or tokenizer
docs/decision_log.md:2087:## D-038: Analysis-plans contract binds L2/L3 claims to pre-registered plans
docs/decision_log.md:2095:sample sizing, and claim ceilings lived in scattered prose, and the
docs/decision_log.md:2108:   rule: no reader-facing L2/L3 claim without a filled plan row.
docs/decision_log.md:2114:denominator provenance, holdouts for L3, claim ceiling, disqualifiers,
docs/decision_log.md:2116:metrics are gross-only until phase-idle modeling exists; short-prefill
docs/decision_log.md:2126:reviewers check L2/L3 wording against plan rows as part of standard
docs/decision_log.md:2144:L2/L3 claims are gated by the comparative MDE; jw_mixed_v1 cross-
docs/decision_log.md:2171:5. P2-015 expands to per-metric/window-class floors (gross request,
docs/decision_log.md:2257:   short-answer benchmarks); FLORES second (tokenizer/multilingual
docs/decision_log.md:2555:Revisit when: AP-6b is proposed, or a model/tokenizer without a stable
docs/decision_log.md:2655:pairing, which is L2-eligible calibration-free); (b) Phase 3 acceptance
docs/decision_log.md:2889:Consequences: the claims-index linter (future) refuses L2/L3 without these
docs/decision_log.md:2938:LIVE index of question status, aliases, type, claim ceiling, forbidden
docs/decision_log.md:3013:Request gating is metric-specific: `gross_request` governs
docs/decision_log.md:3014:`gross_energy_j` without idle-baseline or drift requirements, while
docs/decision_log.md:3037:`tokenizer_identity_mismatch`, `multiplicity_family_incomplete`,
docs/decision_log.md:3087:tokenizer_identity_mismatch
docs/decision_log.md:3112:surfaces: request energy primary; J/token tokenizer-scoped with
docs/decision_log.md:3113:runtime-observed denominators; cross-tokenizer/model-family comparisons
docs/decision_log.md:3117:model artifact hash, quantization, tokenizer identity incl.
docs/decision_log.md:3178:   contrast/claim path (P2-037) before any L2 interpretation.
docs/decision_log.md:3551:3. Claim ceilings are unchanged: everything caps at L2; L3 only via
docs/decision_log.md:3552:   the existing Q4/AP-1 holdout machinery (D-070 clause 5).
docs/decision_log.md:3571:## D-067: Idle reporting basis — gross headline; idle-subtracted is a labeled within-device secondary view
docs/decision_log.md:3588:   request-level metrics; per-phase energy stays gross-only per D-032 —
docs/decision_log.md:3595:4. **Q4's fixed term (E = fixed + prefill + decode) is fit on gross
docs/decision_log.md:3600:   number is gross-first.
docs/decision_log.md:3611:gross headline with labeled idle-subtracted secondary — chosen.
docs/decision_log.md:3617:  headline request energy as idle-subtracted; the headline is now gross.
docs/decision_log.md:3622:  stated on every number, gross-first for any cross-configuration
docs/decision_log.md:3629:- AP-BATCH and subsequent analysis plans fit on gross energy.
docs/decision_log.md:3631:Revisit trigger: the P1-003 wall-meter decision. Wall-boundary gross is
docs/decision_log.md:3633:changes conclusions; when P1-003 lands, re-examine whether rail-gross
docs/decision_log.md:3634:remains an adequate headline or wall-calibrated gross supersedes it.
docs/decision_log.md:3710:## D-070: Architectural-axes extension agenda (AXI): scope, claim posture, batch-axis rulings
docs/decision_log.md:3721:   speculative decoding / MTP, MoE vs dense, quantization, and
docs/decision_log.md:3758:   C5-2.6 (batching), C5-2.5 + C-023-OUTPUT-IDENTITY (spec decode),
docs/decision_log.md:3759:   C5-1.1 / C5-1.9 / RQ-TWO-MODEL-ACTIVE-NONCLAIM (MoE/dense), C5-1.12
docs/decision_log.md:3763:   verdict), and **MOE×BATCH** (candidate, ceiling L2, forbidden
docs/decision_log.md:3764:   upgrade: no MoE-serving-efficiency generalization from one pair).
docs/decision_log.md:3765:5. **Ceilings.** Everything caps at L2 (L3 only through Q4/AP-1's
docs/decision_log.md:3772:with narrow claim commitments (the handoff default: MoE/dense +
docs/decision_log.md:3776:Open item: the D-016 matched dense/MoE model pair remains with Ed and
docs/decision_log.md:3799:   stands FOR NOW because it encodes D-016's 8 GB-class cross-target
docs/decision_log.md:3807:   only by a recorded D-016 amendment after Ed reads that brief.
docs/decision_log.md:3810:   D-016 primary family; the brief must weigh re-pinning costs against
docs/decision_log.md:3839:## D-073: D-016 device-list amendment — Mac + 3080 Ti primary fleet, 12 GiB cap
docs/decision_log.md:3853:models now fit comfortably; (b) dense/MoE pair re-search under the
docs/decision_log.md:3861:(1) Qwen3-4B becomes the D-016 primary CONDITIONALLY: the repin lands
docs/decision_log.md:3870:authorized; success revives the matched OLMoE pair, failure files the
docs/decision_log.md:3883:index; D-070 keeps these axes as stress tests of Q4, caps candidate
docs/decision_log.md:3884:commitments at L2, and reserves commitment authority to Ed. The disposition
docs/decision_log.md:3895:   C-023-OUTPUT-IDENTITY is binding.
docs/decision_log.md:3900:3. Admit one new canonical RQ row, RQ-AXI-HYBRID-PAIR, at an L2 named-pair
docs/decision_log.md:3914:   violates D-070's single-Q4-thesis posture.
docs/decision_log.md:3922:earliest-phase tagged, capped at L2 unless an already-existing parent row's
docs/decision_log.md:3926:D-070 remains the authority for Ed's axis commitments and quiet-Mac ordering.
docs/decision_log.md:3930:undetectable; or Ed changes the D-070 commitment set. Revisit by amending the
docs/decision_log.md:3997:  gross-energy, idle-subtracted-energy, and throughput claims. There is no
docs/decision_log.md:4019:  universal and unwaivable for gross-energy, idle-subtracted-energy, and
docs/decision_log.md:4077:1. No claim-bearing floor, MDE, or L2/L3 energy claim may be published from
docs/decision_log.md:4171:Recorded by the lead after the two-round cross-model convergence loop over
docs/decision_log.md:4515:   original gross-only form was superseded the same day and never
docs/decision_log.md:4522:   DRIFT abs(end_point_gross − start_point_gross); the idle-subtracted
docs/decision_log.md:4545:   build): per-claim-family point-drift screens (gross AND
docs/decision_log.md:4986:   review. (b) Cold lens alone, always — rejected: cross-model diversity is
docs/decision_log.md:5232:  packet — the required pre-decision cross-model consult; Ed directive: "don't
docs/decision_log.md:5353:packet, **paired with an Opus contract-lens refuter** for cross-model
     1	# Claims Ladder
     2	
     3	Status: binding for reader-facing claims from Slice 2M onward. Decision
     4	D-037 records adoption. Per-claim IDs and mechanical enforcement arrive with
     5	the Phase 4 claims index; until then, authors apply this ladder during review.
     6	
     7	This contract governs wording in reports, slides, README/status prose, figure
     8	captions, and tables that a reader could treat as a result. Dated run reports,
     9	stream logs, council logs, and decision logs may preserve historical wording,
    10	but later reader-facing summaries must use the current level.
    11	
    12	The warning-only prose scan mechanically enumerates `README.md`,
    13	`PROJECT_STATUS.md`, `docs/report_src/**`, the generated Phase-4 claims
    14	projection, Markdown tables/captions under analysis and figure artifacts, and
    15	present or future `slides/`, `captions/`, and `tables/` publication trees.
    16	Historical `docs/run_reports/**` records and the decision/council/stream logs
    17	are deliberately outside that scan. Warning-only exit behavior remains the
    18	D-059 policy: these findings require editorial review but are not structural
    19	claim-gate failures.
    20	
    21	The canonical JSONL accepts two authority-distinct row dialects through one
    22	fail-closed validator: the single pre-P2-037 legacy L1 row only under its exact
    23	hash-pinned identity, and current rows linked to a governed
    24	`joulewise.claim_verdicts.v1` artifact. Rows with unknown authority fields or a
    25	mixture of legacy and engine-linked authority fields are invalid. Verdict
    26	semantics belong to `joulewise.analysis_engine`; the claims-index layer adds
    27	only linkage, canonical ordering/rendering, relative-path, editorial, and
    28	current production-admission checks. `two_look_alpha_spending` remains outside
    29	claims-index production admission until separately ruled in; current admission
    30	is deliberately `fixed_n` only.
    31	
    32	## Global Rules
    33	
    34	- Strict validation is the entry ticket for evidence. A run bundle that cannot
    35	  pass the applicable strict checks does not support a result claim.
    36	- Measurement boundaries follow D-018. Claims must name the boundary label
    37	  where it matters, for example `M3 Max / MLX / powermetrics SoC rails`,
    38	  `RTX / vLLM / nvidia-smi board power`, or `wall_meter AC`.
    39	- Cross-boundary comparisons are descriptive only unless a named calibration
    40	  bundle exists for the compared boundaries. Calibration bundles include wall
    41	  meter or USB-C PD evidence that explicitly bridges the boundary.
    42	- Comparative claims from 2M use the experiment manifest order. Interleaved
    43	  order is required where model reload and operational constraints permit; if
    44	  block order is forced, the claim must say so and remain below L2 unless the
    45	  Phase 4 drift audit clears it.
    46	- Detection-floor gates follow Phase 4 Stage 4.0 and Stage 4.5. Effects below
    47	  the floor are reported as `not resolvable`, not as wins, losses, or no
    48	  difference.
    49	- Energy-per-output-token claims require runtime-observed output token counts,
    50	  the runtime stop reason, and the output policy label. If the denominator
    51	  comes from config fallback rather than runtime observation, the claim
    52	  downgrades to L0 capability language.
    53	- (2026-07-09) Token-denominated metrics and cross-tokenizer comparison
    54	  language follow `docs/contracts/token_normalization.md`, including its
    55	  stack-identity table, across all surfaces this ladder governs.
    56	
    57	## Ladder
    58	
    59	| Level | Allowed Claim Shape | Required Evidence | Forbidden Language |
    60	|---|---|---|---|
    61	| L0 - Capability | The harness can execute this path and preserve auditable evidence. | One complete bundle; applicable strict validation; raw artifacts present; boundary label recorded. Config-fallback token denominators may appear only here. | faster, cheaper, more efficient, scales, crossover, ranking, law, proves |
    62	| L1 - Instrument Result | On this exact stack, boundary, workload, and output policy, this measured quantity was observed. | n >= 3 strict-valid bundles, or a single run only if explicitly labeled smoke/capability; runtime-observed token counts for per-token claims; stop reason and output policy label; no suspect quality flags unless waived in text. | general device ranking, model-family law, cross-target winner, active-parameter scaling result |
    63	| L2 - Comparative Result | Condition A differed from condition B within the same measurement boundary under a named workload and policy. | n >= 5 per condition; strict-valid bundles; 2M experiment manifest order recorded and interleaved where permitted; confidence intervals reported; effect clears the Phase 4 detection floor; same boundary label, or a named calibration bundle if boundaries differ. | cross-boundary winner without calibration, universal, architecture-wide conclusion, extrapolated crossover |
    64	| L3 - Model Fit | A fitted fixed/marginal model predicts held-out cells within stated error for the tested matrix. | Designed matrix with holdout cells; strict-valid source bundles; runtime-observed token denominators; residual and sensitivity analysis; detection-floor audit for every fitted effect; boundaries and workload policies stated. | law, universal scaling, architecture-wide result, causal language beyond the fitted variables |
    65	| L4 - Generalized Finding | The finding holds across named stacks, units, or calibrated boundaries under stated limits. | Independent replication across a second target or second unit; strict-valid bundles; n and order rules satisfied per condition; named calibration bundles for cross-boundary quantitative comparison; replicated runbook; sensitivity audit survives boundary and version changes. | unqualified claims outside tested hardware, workloads, runtime versions, policies, or calibration scope |
    66	
    67	## Downgrade Examples
    68	
    69	- Two strict-valid Mac/MLX/powermetrics points that differ in model size,
    70	  architecture, and quantization are hypothesis-generating for Q4. They are
    71	  not an active-parameter scaling result.
    72	- A same-boundary energy/token difference with runtime-observed token counts
    73	  but fewer than five interleaved repetitions is L1 until the comparative
    74	  protocol is satisfied.
    75	- A per-token result using configured output length because runtime token
    76	  counts were unavailable is L0 capability language, even if the bundle is
    77	  otherwise strict-valid.
     1	# Token Normalization And Stack Identity Contract
     2	
     3	Status: binding for token-denominated metrics, cross-tokenizer comparison
     4	language, and stack identity on all claims-ladder-governed surfaces from
     5	2026-07-09 onward.
     6	It composes with `docs/contracts/claims_ladder.md` for claim levels and
     7	`docs/contracts/capstone_scope.md` for single-unit limitation language.
     8	
     9	Evidence inputs: `docs/reviews/2026-07-09-scientific-rigor-review.md` M3,
    10	Appendix B finding 6, and Appendix D Part C rows "Stack confound" and
    11	"J/token comparability"; `docs/decision_log.md` D-033, D-037, D-052, and
    12	D-053; `docs/contracts/claims_ladder.md`;
    13	`docs/contracts/capstone_scope.md`; and
    14	`docs/contracts/run_bundle_layout.md`.
    15	
    16	## Primary Metric
    17	
    18	Request energy is the PRIMARY reader-facing energy metric.
    19	
    20	Request energy means gross joules per request under a named measurement
    21	boundary. The basis and boundary labels are parts of the metric identity, not
    22	caption garnish. Gross energy retains idle, model-residency, and runtime
    23	overhead inside the measured interval and is the headline basis for every
    24	cross-device, cross-configuration, and split-versus-monolithic claim.
    25	
    26	Idle-subtracted joules per request remain a clearly labeled within-device
    27	secondary view of activity above the measured idle baseline. They are never
    28	used to rank devices or configurations. The stored historical field
    29	`energy_request_j` is not renamed or redefined; reader-facing gross request
    30	energy is `gross_energy_j`.
    31	
    32	Per-token metrics never replace gross request energy in a headline. They may
    33	appear as companion metrics when their tokenizer scope, energy basis, and
    34	denominator provenance are explicit.
    35	
    36	A headline means the primary reader-facing figure or table and any
    37	abstract-level claim, not only the title. In any reader-facing figure or
    38	table containing token-normalized metrics, gross request energy must be
    39	co-displayed with equal or greater salience. Every reported energy number
    40	states its basis and boundary; any cross-configuration number is gross-first.
    41	
    42	## J/Token As Tokenizer-Scoped Companion Metrics
    43	
    44	`J/token`, `J/output-token`, and `J/prompt-token` are companion metrics scoped
    45	to a named tokenizer. They describe the measured stack and tokenizer that
    46	produced the denominator; they are not tokenizer-blind work units.
    47	
    48	Requirements:
    49	
    50	- Per-token denominators must be runtime-observed token counts. Committed
    51	  output tokens and accepted draft/MTP tokens are distinct denominators and
    52	  must never be substituted for one another. For speculative-on/off
    53	  efficiency, gross joules per committed output token is the companion
    54	  denominator; gross joules per accepted draft token is a speculation-enabled
    55	  mechanism-yield diagnostic only and is undefined for spec-off. This is the
    56	  D-037 claims-ladder rider; use `docs/contracts/claims_ladder.md` Global
    57	  Rules as the downgrade authority rather than restating it here.
    58	- The tokenizer identity must be named wherever a per-token number appears:
    59	  tokenizer name, revision, class, and vocabulary size where available, per
    60	  the D-033 `metadata.workload_provenance` block.
    61	- For per-token metrics, denominator provenance includes prompt-delivery
    62	  regime and BOS handling: `prompt_source` and `bos_present` as recorded in
    63	  `outputs/suite_items.jsonl` (D-046).
    64	- When prompt token-ID hashes are cited, the single-prompt hash domain is
    65	  `joulewise.prompt_token_ids.v1` (D-033). The suite rollup hash domain is
    66	  `joulewise.suite_prompt_token_ids.v1` per
    67	  `docs/contracts/run_bundle_layout.md`.
    68	- `J/token` values from different tokenizers are NEVER an efficiency ranking
    69	  by themselves.
    70	
    71	Burst-decode bundles use the counter meanings and null rules frozen by
    72	`docs/specs/axi/sa_burst_decode_contract.md`. Acceptance rate is the ratio
    73	of aggregate accepted to aggregate proposed tokens, never a mean of local
    74	rates, and is null when proposal total is zero. Spec-off proposal,
    75	acceptance, and acceptance-rate fields are null rather than zero.
    76	
    77	`inter_token_throughput_tokens_s` is eligible only when every committed
    78	output token in scope has a genuine per-token runtime timestamp. Burst-safe
    79	decode-phase output throughput and emission/burst metrics use their new names
    80	and must not be reported under either frozen throughput name.
    81	
    82	For an event-semantics-v2 static batch, the energy analysis unit is the
    83	complete batch group and its governed gross metric is
    84	`batch_group_gross_energy_j` on window class `gross_batch_group`. It must not
    85	appear in a request-scoped object or under a request-energy estimand name, and
    86	trace energy must not be divided among overlapping requests. Single-request
    87	gross energy remains `gross_energy_j` on `gross_request`.
    88	
    89	## Cross-Tokenizer And Cross-Model-Family Comparisons
    90	
    91	Any comparison across tokenizer families, or across model families with
    92	different tokenizers, must do one of two things:
    93	
    94	1. Carry companion denominators that are tokenizer-independent, such as
    95	   `J/char`, `J/byte`, or semantic-matched pair denominators
    96	   (FLORES-style same-content parallel items).
    97	2. Avoid efficiency-ranking language entirely and remain descriptive.
    98	
    99	Forbidden language:
   100	
   101	| Forbidden language | Forbidden use | Allowed replacement |
   102	|---|---|---|
   103	| "more efficient per token" | Cross-tokenizer or cross-model-family ranking. | "lower `J/token` for [stack A] under tokenizer [name/revision/class/vocab size] than [stack B] under tokenizer [name/revision/class/vocab size], with request energy [direction/value] under [boundary]." |
   104	| "better J/token" | Cross-family efficiency conclusion. | "different tokenizer-scoped `J/token` under [stack A tokenizer name/revision/class/vocab size] and [stack B tokenizer name/revision/class/vocab size]; request energy is [direction/value] under [boundary]." |
   105	| "cheaper tokens" | Treating tokens from different vocabularies as comparable work units. | "lower `J/char`, `J/byte`, or semantic-pair energy under the stated companion denominator." |
   106	| Tokenizer-blind "energy per token" leaderboard language | Ranking stacks without naming tokenizer identity and request energy. | "tokenizer-scoped companion metrics for [stack A tokenizer name/revision/class/vocab size] and [stack B tokenizer name/revision/class/vocab size], reported beside request energy." |
   107	| Treating token counts as comparable work units across vocabularies | Any inference that equal token counts imply equal semantic, byte, or character work across tokenizers. | "same-content item energy" or "`J/char`/`J/byte` companion denominator, with tokenizer-scoped `J/token` only as context." |
   108	
   109	Within one tokenizer identity, per-token comparisons still obey the claims
   110	ladder, analysis registry, floor, order, and boundary rules. This contract
   111	only prevents token denominators from being promoted into tokenizer-blind
   112	efficiency units.
   113	
   114	## Stack-Identity Table
   115	
   116	Every reader-facing result claim governed by
   117	`docs/contracts/claims_ladder.md` must carry stack identity across all
   118	claims-ladder-governed surfaces: reports, slides, README/status prose,
   119	captions, tables, and figures. Any exported or reused rendering of a governed
   120	figure must carry the same stack identity in the rendered artifact or
   121	immediately adjacent text, at minimum by naming a stack-identity table it
   122	resolves to.
   123	
   124	The table below defines the minimum fields and the expected
   125	bundle/provenance surface when it is already known.
   126	
   127	| Field | What satisfies it | Bundle/provenance surface |
   128	|---|---|---|
   129	| Hardware unit | Concrete physical target or node label, hardware model, and unit identity when available. | `metadata.device`; composite/split node identity where applicable. |
   130	| OS + version | Operating system name and version/build. | `metadata.environment` or device/environment capture fields. |
   131	| Runtime + version | Runtime or serving stack name and version, for example MLX, vLLM, llama.cpp, mock, or adapter-specific runtime. | `metadata.runtime`; `metadata.environment.python_packages` for Python package versions such as `mlx`, `mlx-lm`, and `transformers`; `metadata.adapters.runtime` for additive adapter metadata. |
   132	| Kernel/library where known | Kernel, attention implementation, library backend, graph/capture mode, or equivalent runtime kernel identity when exposed. | Runtime adapter metadata; `metadata.adapters.runtime.prepare_metadata` when captured. |
   133	| Model artifact hash | Model artifact byte identity, not only a display name. For directories, the folded directory identity satisfies this field. | `metadata.runtime.model_artifact_identity`; model identity inside `metadata.workload_provenance` where recorded. |
   134	| Quantization | Quantization format, precision, and runtime quantization label, or `none`/`unknown` if that is the recorded state. | `metadata.runtime`; model/config fields; `metadata.workload_provenance` model fields where recorded. |
   135	| Tokenizer identity | Tokenizer name, revision, class, and vocabulary size where available; prompt source and BOS handling (`prompt_source`, `bos_present`) when per-token metrics are shown; token-ID hash domain and hash when the caption cites prompt-token identity. | `metadata.workload_provenance` (D-033); `outputs/suite_items.jsonl` item `prompt_source`, `bos_present`, and per-item token hashes; single-prompt domain `joulewise.prompt_token_ids.v1`; suite rollup domain `joulewise.suite_prompt_token_ids.v1`. |
   136	| Sampler/output policy | Sampler settings, stop condition, runtime stop reason, and output cap/policy label. | `events.jsonl` `item_start` event metadata `output_policy`; `outputs/suite_items.jsonl` item `stop_reason`; `metadata.workload_provenance.output_policy`; `metadata.workload_provenance.sampler` (single-prompt and suite runs); suite sampler provenance per `docs/contracts/run_bundle_layout.md`. |
   137	| Batching/concurrency policy | Always applicable: state configured and realized batch size separately; mode, admission, synchronization, and dispatch policy; and `single-request` or explicit `unavailable`. Static batch-group identity and required-nullable scheduler-step identity never replace request identity. | Normalized `config.json.batch_policy`; `metadata.batch`; request-scoped `events.jsonl` metadata; or explicit `unavailable` only for historical compatibility. |
   138	| Measurement boundary label | Named boundary whose joules are reported, including rail/source semantics. | `metadata.telemetry`, `power_trace.csv` `source`/`rail`, rail-manifest metadata, and D-018 boundary label used under `docs/contracts/claims_ladder.md`. |
   139	| Telemetry backend | Backend that produced the power trace, including version or command semantics where available. | `metadata.telemetry`; `metadata.device.powermetrics` for powermetrics sampler evidence; backend-native artifacts under `raw/`; telemetry logs. |
   140	
   141	Every field in this table must appear on every governed surface as either a
   142	concrete value or an explicit `unavailable`/`unknown`; silent omission of any
   143	field is non-compliant.
   144	
   145	Event-semantics-v2 bundles record the actually loaded target tokenizer at
   146	`metadata.runtime.target_tokenizer_identity` with exact name, immutable
   147	revision, and `tokenizer_artifact_sha256`. C-023 compares all three strings
   148	byte-for-byte; it performs no case folding, alias resolution, revision-prefix
   149	matching, Unicode normalization, display-name fallback, or config-only
   150	fallback. Missing or malformed runtime identity is unassessable, never an
   151	asserted equality.
   152	
   153	## Caption-Compliance Rule
   154	
   155	A figure or table caption is compliant when it carries the stack-identity
   156	fields above and composes with both:
   157	
   158	- the boundary-label rule in `docs/contracts/claims_ladder.md` Global Rules;
   159	- the single-unit caption template in `docs/contracts/capstone_scope.md`
   160	  "Single-Unit Limitation Language".
   161	
   162	Do not duplicate those contracts' text here. Their rules remain the source of
   163	truth for boundary labels and single-unit limitation wording.
docs/research_question_registry.md:53:| C5-2.5 | Speculative-decoding energy; C5-2.5b proposal-work rider; C5-2.5c break-even rider | research question | banked | L2 | no efficiency claim without output equivalence and accepted-token accounting | none-yet | none | software | analysis-plan-only | C5-2.5c is the primary PF Q4 rider, C5-2.5b its PF secondary, and C5-2.5d the mandatory PF contamination control; C5-2.5a remains a deferred NS bank rider. `C-023-OUTPUT-IDENTITY` binds all efficiency contrasts ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:100:| C-023-TELEMETRY-PERTURBATION | Telemetry perturbation cost | methodology artifact | candidate (C-023) | L1/L2 floor component | no near-floor claim without telemetry-on/off ABBA check | none-yet | P2-015 component | floor | analysis-plan-only | New coverage-gap row; distinct from C5-1.6 sampling-strategy overhead. |
docs/research_question_registry.md:103:| C-023-OUTPUT-IDENTITY | Output-token identity effects; binding gate for C5-2.5a/b/c/d | methodology artifact | candidate (C-023) | L1/L2 depending comparison | no quant/runtime/spec-decoding efficiency claim without equivalence or divergence report | none-yet | none | software | analysis-plan-only | Fixed output-token count is not fixed decoded work; binding for the PF/NS speculative-decoding riders admitted by D-075 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/decision_log.md:838:## D-016: Benchmark model selection
docs/decision_log.md:3710:## D-070: Architectural-axes extension agenda (AXI): scope, claim posture, batch-axis rulings
docs/decision_log.md:3758:   C5-2.6 (batching), C5-2.5 + C-023-OUTPUT-IDENTITY (spec decode),
docs/decision_log.md:3895:   C-023-OUTPUT-IDENTITY is binding.

exec
/bin/zsh -lc "nl -ba docs/decision_log.md | sed -n '838,940p'; nl -ba docs/decision_log.md | sed -n '3710,3795p'; nl -ba docs/axi-handoff.md | sed -n '80,105p'; nl -ba docs/axi-handoff.md | sed -n '185,275p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
   838	## D-016: Benchmark model selection
   839	
   840	- Date: 2026-06-09
   841	- Status: open (criteria fixed now; closure requires Phase 1 supervisor scope
   842	  plus Phase 2 install evidence)
   843	- Phase: 2+
   844	
   845	Context: every cross-target comparison needs identical model(s). The example
   846	config's `qwen-placeholder` must become a real decision before Slice 2G.
   847	
   848	Selection criteria (fixed now):
   849	
   850	1. Must run on all primary targets: MLX-format weights available (or
   851	   convertible) for Mac; GGUF available for llama.cpp paths; vLLM-loadable
   852	   for the CUDA path.
   853	2. Must fit the smallest VRAM targets at the chosen quantization: 8 GB
   854	   (RTX 3050, Orin Nano) with headroom for KV at experiment prompt lengths.
   855	3. KV-per-token small enough that transfer payloads span an interesting
   856	   range (see Phase 3 KV table) but large enough to exercise the
   857	   interconnect.
   858	4. Open weights with a license permitting academic benchmarking and local
   859	   mirroring (R-014: mirror weights locally once chosen).
   860	5. Prefer one small + one mid model from the same family to separate
   861	   model-size effects from family effects.
   862	
   863	Candidate set (to be narrowed with evidence): Qwen2.5-1.5B-Instruct,
   864	Qwen2.5-7B-Instruct, Llama-3.2-1B-Instruct, Llama-3.2-3B-Instruct,
   865	Llama-3.1-8B-Instruct.
   866	
   867	Options considered (shape of the decision): single model (cleanest matrix,
   868	no size axis) vs small+mid pair (size axis, double hardware time) vs per-
   869	target best model (incomparable - rejected outright).
   870	
   871	Decision pending; leaning small+mid pair from one family, final call
   872	recorded here with per-runtime artifact paths and exact revisions when
   873	closed.
   874	
   875	**Provisional pick recorded (2026-07-06, user-directed build-out session;
   876	gate = explicit user go-ahead, recorded in the run report):**
   877	Qwen2.5-1.5B-Instruct as the small model, MLX 4-bit artifact
   878	`mlx-community/Qwen2.5-1.5B-Instruct-4bit`, revision
   879	`8b403126fc14f14cfc99bb4cfa72ecbc129ea677`, mirrored locally (R-014) at
   880	`/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit` (839 MB).
   881	Evidence: HF repo verified via API 2026-07-06; loaded and generated on
   882	the M3 Max via Slice 2G (bundle `example-mac-mlx-mock-telemetry`,
   883	265.8 tok/s decode); KV row verified against the mirrored config.json
   884	(28,672 B/token fp16, matches the Phase 3 table). This opens the 2G gate
   885	("closed or provisional") ONLY. Full closure still requires: P1-001
   886	supervisor scope, the mid-model pick (leaning Qwen2.5-7B-Instruct, same
   887	family per criterion 5), a CUDA-target load, and GGUF artifact paths.
   888	The provisional pick is reversible at config level (one model stanza +
   889	pinned hash update).
   890	
   891	Closure evidence required: supervisor scope notes (P1-001); successful load
   892	on Mac MLX (Slice 2G) and one CUDA target; recorded weight artifact
   893	paths/revisions; KV-size table row computed for the chosen models.
   894	
   895	Revisit when: a chosen model's weights become unavailable or a target cannot
   896	load it (then the recorded fallback candidate is promoted).
   897	
   898	Amended (2026-07-15, WO-019; D-043): CI scope extends beyond the core
   899	suite — a clean-clone publication release check (`scripts/release_check.py
   900	--dry-run`, real temporary-directory execution of every non-secret seam)
   901	and the WO-021 `gen_state.py --check` drift gate are CI jobs; credential-
   902	bearing steps (deploy) remain outside CI per D-068 and the publication
   903	release checklist.
   904	
   905	---
   906	
   907	## D-017: CI scope
   908	
   909	- Date: 2026-06-09
   910	- Status: accepted
   911	- Phase: all
   912	
   913	Context: the GitHub remote has no CI; agents benefit from remote green-check
   914	evidence, and Phase 5 promises a reproducible mock path.
   915	
   916	Options considered:
   917	
   918	1. No CI. Con: "tests pass" claims rest on local runs in handoff notes.
   919	2. Full matrix with extras (mlx cannot install on Linux runners; GPU absent).
   920	   Con: impossible or meaningless for hardware paths.
   921	3. Core-only CI: ubuntu runner, Python 3.11 and 3.14 (oldest supported per
   922	   `pyproject.toml`, plus the version observed in local development),
   923	   `python -m unittest discover -s tests` plus CLI smoke
   924	   (`validate-config` on both example configs). Later phases extend it with
   925	   the mock-bundle end-to-end run and `validate-bundle` once those exist.
   926	
   927	Decision: option 3.
   928	
   929	Considerations: the stdlib-only core (D-009) is exactly the testable surface
   930	on a hosted runner; hardware adapters are validated by run bundles, not CI.
   931	Two Python versions catch the realistic compat risks (3.11 floor vs 3.14
   932	local) at trivial cost.
   933	
   934	Consequences: `.github/workflows/ci.yml` added; Phase 2 Slice 2E adds the
   935	mock end-to-end step to it; README badges optional, not required.
   936	
   937	Revisit when: a self-hosted runner with GPU/Mac hardware ever materializes
   938	(unlikely; not planned).
   939	
   940	---
  3710	## D-070: Architectural-axes extension agenda (AXI): scope, claim posture, batch-axis rulings
  3711	
  3712	- Date: 2026-07-14 (Ed-directed; provenance `docs/axi-handoff.md`
  3713	  §1.1/§4/§5 plus Ed's rulings recorded this session)
  3714	- Status: accepted (C-033 coherence-reviewed)
  3715	- Phase: Phase 2+ research program
  3716	
  3717	Decision:
  3718	
  3719	1. **Agenda.** Once the harness works, it must be able to characterize
  3720	   architectural inference features generally — static batching,
  3721	   speculative decoding / MTP, MoE vs dense, quantization, and
  3722	   reasoning-length variance — framed as stress tests of the single Q4
  3723	   thesis (E = fixed + coefficients·work), not five new theses.
  3724	2. **Claim posture.** Instrument support (L0 smoke bundles) for ALL
  3725	   axes. Ed ruling 2026-07-14 (supersedes the handoff's narrower
  3726	   default): ALL five axes get characterized-claim commitments with
  3727	   dedicated quiet-Mac hardware time — it is Ed's own hardware and Ed
  3728	   wants maximum axis flexibility. Sequencing and floor discipline are
  3729	   unchanged: every AP remains floor-gated on P2-015 floors,
  3730	   `TASK_QUEUE.md` remains the ordering authority, Window A outranks
  3731	   everything, and no AXI stream consumes a [QUIET-MAC] window until
  3732	   Window A completes.
  3733	3. **Batch axis (Ed ruling).** STATIC batching only for the capstone:
  3734	   AP-BATCH covers B ∈ {1,2,4,8,16} static dispatch. Continuous
  3735	   batching is DEFERRED as a post-capstone, NV-gated extension — not
  3736	   killed. BINDING continuous-ready design constraint so the deferral
  3737	   stays additive rather than rework: all batch-related event schema is
  3738	   **request-scoped, not run-scoped** — token and phase events carry a
  3739	   `request_id`; each request gets its own lifecycle envelope
  3740	   (submit/prefill/decode/complete) even though static runs happen to
  3741	   synchronize them; no schema assumption that all sequences share one
  3742	   prefill boundary or one decode window. The reducer MAY exploit
  3743	   synchronization for static-mode metrics but MUST NOT require it at
  3744	   the schema level. Schema placement pin: `request_id` lives in event
  3745	   `metadata` (`events.jsonl` `metadata.request_id`) — the five-key
  3746	   event contract gains no sixth top-level key. Request-grouped
  3747	   lifecycle/phase pairing is NEW-version reducer dispatch, purely
  3748	   additive; legacy arms stay frozen and no existing bundle is
  3749	   re-dispatched (D-066 clause 2). Rationale: a single model instance
  3750	   with B KV
  3751	   caches is memory-feasible on current hardware; only the serving
  3752	   scheduler is hardware-gated, so a future continuous stream (load
  3753	   generator, steady-state detection, energy-per-token-at-offered-load
  3754	   metric) becomes purely additive on top.
  3755	4. **Registry.** Existing rows already carry the axes — the C5-* rows
  3756	   live in `docs/research_question_bank.md`; the C-023-* and RQ-* rows
  3757	   live in `docs/research_question_registry.md` (D-055): C5-2.2 and
  3758	   C5-2.6 (batching), C5-2.5 + C-023-OUTPUT-IDENTITY (spec decode),
  3759	   C5-1.1 / C5-1.9 / RQ-TWO-MODEL-ACTIVE-NONCLAIM (MoE/dense), C5-1.12
  3760	   + C-023-QUALITY-EQUIV-QUANT (quantization), RQ-ENERGY-VARIANCE +
  3761	   C5-W.2 (reasoning variance). Two new rows to mint at their gates:
  3762	   a **Mac-batching leg of C5-2.2** (minted ONLY on an S-B `supported`
  3763	   verdict), and **MOE×BATCH** (candidate, ceiling L2, forbidden
  3764	   upgrade: no MoE-serving-efficiency generalization from one pair).
  3765	5. **Ceilings.** Everything caps at L2 (L3 only through Q4/AP-1's
  3766	   existing holdout machinery); ceilings move only via replication rows
  3767	   (C5-3.1). No live claims from fixture-first code; PROVISIONAL until
  3768	   first live hardware contact.
  3769	
  3770	Options considered: (a) five independent theses — rejected (dilutes
  3771	Q4 and is unfundable in the timeline); (b) axes as Q4 stress tests
  3772	with narrow claim commitments (the handoff default: MoE/dense +
  3773	batching only) — superseded by Ed's ruling; (c) axes as Q4 stress
  3774	tests with all-axes commitment — chosen by Ed.
  3775	
  3776	Open item: the D-016 matched dense/MoE model pair remains with Ed and
  3777	the advisor; stream S-D presents the proposal (same family, matched
  3778	active params; fallback matched total) — do not finalize unilaterally.
  3779	
  3780	Revisit triggers: an S-B `unsupported` verdict removes the Mac-batching
  3781	leg (the dated negative verdict is filed as a finding, Hailo idiom);
  3782	measured P2-015 floors that make a predeclared AXI effect size
  3783	undetectable send that AP back for redesign before any campaign is
  3784	scheduled.
  3785	
  3786	## D-071: G10 memory-fit rule ratified (axi-sd-memory-fit-shape-v1); device-list review opened
  3787	
  3788	Date: 2026-07-16. Owner: Ed (ruling given in-session; recorded verbatim
  3789	in intent).
  3790	
  3791	1. **Ratified:** the `axi-sd-memory-fit-shape-v1` probe shape (batch 1,
  3792	   frozen 8,192-token prompt, exactly 128 EOS-masked greedy decode
  3793	   tokens, cold KV, no offload/swap), the peak-measurement semantics
  3794	   (load-start through decode token 128, full time series, one named
  3795	   counter per target), and the `H_t >= max(1 GiB, 0.15 * C_t)` reserve.
    80	
    81	### 1.1 The extension agenda (Ed's directive)
    82	
    83	Once the harness works, Ed wants it able to characterize architectural
    84	inference features generally: **static batching, speculative decoding /
    85	MTP, MoE vs dense, quantization, reasoning-length variance** — framed as
    86	stress tests of the single Q4 thesis, not five new theses. The registry
    87	already contains most of the target rows: C5-2.2 and C5-2.6 (batching,
    88	currently P1-006-gated), C5-2.5 and C-023-OUTPUT-IDENTITY (spec decode),
    89	C5-1.1 / C5-1.9 / RQ-TWO-MODEL-ACTIVE-NONCLAIM (MoE/dense), C5-1.12 and
    90	C-023-QUALITY-EQUIV-QUANT (quantization), RQ-ENERGY-VARIANCE and C5-W.2
    91	(reasoning variance). Two genuinely new rows to mint: a **Mac-batching
    92	leg of C5-2.2** (de-gates it from NVIDIA access) and **MOE×BATCH**
    93	(expert-activation diversity vs batch size; candidate, ceiling L2,
    94	forbidden upgrade: no MoE-serving-efficiency generalization from one
    95	pair). Claim posture: **instrument support (L0 smoke bundles) for all
    96	axes; characterized-claim commitments narrow** (§5.2).
    97	
    98	---
    99	
   100	## 2. Ed's decisions to record FIRST (allowed under the audit gate)
   101	
   102	These are decision-log / process work, not feature work. Record each as
   103	a D-entry with this handoff cited as provenance; where a council is
   104	normally required for contract-bearing changes, hold a short recorded
   105	session per standing rules, but the outcomes below are Ed-directed.
   185	### S-A — Burst-decode metric-semantics contract [contract-bearing; blocks S-C]
   186	
   187	- Extend `docs/contracts/token_normalization.md` + schema:
   188	  `tokens_proposed`, `tokens_accepted`, `acceptance_rate`,
   189	  emission-event granularity in events.jsonl (N tokens per decode
   190	  step), draft-model identity fields (null for native MTP heads).
   191	- Generalize the reducer's per-generated-token and inter-token metrics
   192	  for burst arrivals; freeze against legacy arms (no re-dispatch of
   193	  existing bundles).
   194	- Make C-023-OUTPUT-IDENTITY executable: output equivalence/divergence
   195	  report required by any spec-decode efficiency claim.
   196	- **Freeze the denominator rules into the P2-042 analysis manifest
   197	  BEFORE any spec-decode bundle can exist.** Post-C-027, denominator
   198	  ambiguity is made structurally impossible or nothing merges.
   199	- Exit: schema + reducer + validator merged; a mock spec-decode adapter
   200	  produces strict-valid bundles; manifest entry frozen; zero live claims.
   201	
   202	### S-B — mlx-lm static-batch feasibility spike [time-boxed, verdict-shaped]
   203	
   204	One session + one live-verification pass. Question: does pinned mlx-lm
   205	support static batch generation with per-sequence token streams adequate
   206	for the event model? `supported` → follow-on adapter row (batch_size
   207	config knob, per-sequence token events). `unsupported` → C5-2.2 stays
   208	P1-006-gated and the dated negative verdict is filed as a finding
   209	(Hailo idiom). Mint the Mac-batching registry leg on a `supported`
   210	verdict only.
   211	
   212	### S-C — Spec-decode runtime spike [after S-A schema lands]
   213	
   214	Leg 1: mlx-lm speculative/draft support on the Mac stack (live spike).
   215	Leg 2: vLLM spec-decode fixture-first for the 2K slice (PROVISIONAL, NV-
   216	GATE discipline). Survey native-MTP (draft-free) model candidates as a
   217	model-selection input feeding D-016, not as runtime work.
   218	
   219	### S-D — Model + quantization artifact groundwork [desk work]
   220	
   221	Matched dense/MoE pair proposal for D-016 (same family, matched active
   222	params; fallback matched total) with local mirrors + hash manifests.
   223	Quantization ladder for C5-1.12: 2–3 quant levels of one model, mirrored
   224	and hashed, with the quality-equivalence reporting rule predeclared per
   225	C-023-QUALITY-EQUIV-QUANT.
   226	
   227	### S-E — Analysis plans [desk work]
   228	
   229	- **AP-BATCH:** E(B) = fixed + B·marginal fit on GROSS energy,
   230	  B ∈ {1,2,4,8,16}, one model, one workload shape, n=5, predeclared
   231	  breakpoint handling; framed as a Q4 coefficient stress test.
   232	- **AP-5 extension:** dense/MoE contrast rides inside the 2M baseline
   233	  campaign (zero extra quiet-machine cost) if D-016 selects the pair.
   234	- **AP-SPEC:** spec-on vs spec-off at matched output policy; both
   235	  denominators reported; equivalence-gated per S-A.
   236	- All APs floor-gated: none executes before P2-015 publishes floors;
   237	  every predeclared effect size is checked against the measured floor
   238	  before its campaign is scheduled.
   239	
   240	---
   241	
   242	## 5. Decisions to put to Ed (batch these at session start)
   243	
   244	1. **Audit-first confirmation** — default (safe to assume): resume and
   245	   complete the audit fix-wave/adjudication before launching §4 streams;
   246	   §2 D-entries recorded immediately regardless. Ask only if the audit
   247	   scope makes S-0 awkward to sequence.
   248	2. **Characterized-claim commitments** — default: MoE/dense (free via
   249	   D-016 inside the 2M campaign) + static batching (one quiet-machine
   250	   block, ~25 runs). Everything else = ordered stretch rungs below the
   251	   split study on the descope ladder. **Confirm the ranking** — every
   252	   stretch rung funded with quiet-Mac time is a session the interconnect
   253	   sweep doesn't get. This is Ed's genuine trade-off; do not default it.
   254	3. **D-016 model pair** — needs Ed (and advisor input in flight). Present
   255	   S-D's proposal when ready; do not finalize unilaterally.
   256	4. **Continuous batching** — default: out of capstone scope (per-token-
   257	   at-offered-load deferred); static batch only. Confirm.
   258	5. **Site-drift mechanism** — default: script + DRIFT.md; subagent diff
   259	   acceptable alternative. Pick whichever is cleaner; only ask if both
   260	   turn out awkward.
   261	6. **Idle D-entry wording** — draft it, show Ed the final text before
   262	   recording (it will be quoted to the advisor).
   263	
   264	## 6. Explicit do-nots
   265	
   266	- No live claims from fixture-first code; PROVISIONAL until first live
   267	  hardware contact.
   268	- No claim-ceiling renegotiation: everything in §4 caps at L2 (L3 only
   269	  through Q4/AP-1's existing holdout machinery); ceilings move only via
   270	  replication rows (C5-3.1).
   271	- No quiet-machine consumption by §4 streams; [QUIET-MAC] windows belong
   272	  to Window A until Ed says otherwise.
   273	- No site regeneration or deployment by any agent, ever, effective §2.3.
   274	- No skipping the batched §5 question set — Ed expects to be asked.

