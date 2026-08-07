OpenAI Codex v0.146.1
--------
workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: xhigh
reasoning summaries: none
session id: 019fdd22-9975-7582-8ec2-956146a9f0e2
--------
user
PORTFOLIO SYNTHESIS — 24 developed paper directions, each with an adversarial Opus 5
counter-review. Your job: produce the ranked portfolio and the recommended paper arc
for Ed. Emit the full synthesis as your FINAL MESSAGE.

CONTEXT: read /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/portfolio-brief.md
first (project brief + constraints). Repo ground truth: the checkout you are in
(main; D-117 at the end of docs/decision_log.md; design memo at
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md).

MATERIALS: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/portfolio/
contains prop-<tag>.md (proposal; the final large markdown block — ignore transport
noise) and rev-<tag>.md (Opus counter-review) for 24 tags. Read ALL reviews first
(they are shorter and carry verdicts/scores/fatal-flaws); read proposals selectively
where ranking decisions need the primary text.

CROSS-CUTTING CORRECTIONS the referee corps established (apply when re-ranking;
verify, don't trust my summary): (1) several proposals sized against the generic ~5 J
bar when their 7B-arm cells face the measured ~14.0 J armwise comparative floor;
(2) EVERY "MVP+N nights" figure omits Window C — the MVP's §6 characterization table
is wholly [PENDING WINDOW C] and D-117 cl.4 schedules it AFTER the three windows, so
the complete MVP is 3 claim nights + 1 characterization night, and Ed owes a scope
ruling (fund night 4 vs declare §6 future work); (3) floor transport across workload
lengths is anti-conservative (repeatability scales with magnitude) — length sweeps
must self-floor; (4) referee verdict distribution: quantization (as shrunk BF16/Q4/Q8)
and moe-routing (as re-anchored Qwen3-30B-A3B vs dense partner) were the only VIABLEs;
everything else WEAK/KILL as written, but many reviews extracted night-cheap SALVAGE
items.

SALVAGE POOL the reviews produced (verify each against its review file): single-window
KV-context-scaling ABBA contrast (from rev-mvp-icpe-upgrade move 1); held-out
floor-validation ladder window (rev-floor-methodology move 1); desk-only
"price of never-zero" MVP subsection (rev-drift-thermal move 1); interior-chunk
noise-limited estimand (rev-long-generation-dynamics); spec-decode 2-hour daytime
tok/s pilot gating the "does it ever repay" question (rev-spec-decode);
negative-label 3080 Ti demonstration (rev-energy-nutrition-label move 3); tokenizer
matched-content non-Latin ranking-flip night (rev-tokenizer-honesty M1); prefix-reuse
boundary/refusal reframe (rev-open-explore-registry R2); A4 batch adapter as cheap
queued desk work (rev-batch-concurrency); GPU-cadence one-evening probe
(rev-split-inference move 1); 20x time-anchor-defect cautionary figure
(rev-open-explore meta-finding).

DELIVER:
1. RANKED PORTFOLIO: top 8 with one-paragraph justifications each (verdict-aware,
   cost-corrected: nights INCLUDING floor obligations and Window C, desk weeks,
   probability of surviving its own kill gates); remaining 16 as one-line
   dispositions with explicit KILLs.
2. THE RECOMMENDED ARC for Ed: MVP capstone (fixed, in flight) -> second paper ->
   stretch — with concrete sequencing against the D-117 windows + Window C +
   semesters, night-budget table, and which salvage items ride WHICH paper (many are
   MVP subsections, not papers).
3. SYNERGY MAP: which funded items share windows/desk work so marginal cost drops.
4. THE SINGLE BEST SECOND-PAPER BET and why, with its honest total cost and its
   kill-gate schedule (what desk evidence, by when, would kill it before a night).
5. OPEN QUESTIONS FOR ED, ranked (include the §6/Window-C scope ruling and the
   256-token prefill arm).
Be decisive; where you disagree with a referee verdict, say so and argue it.
PRIOR for tie-breaks: maximize academic impact and venue ceiling; prefer the bet with the highest publishable upside if its kill gates clear.

LATE SALVAGE ADDITIONS (from the final review pair): contamination desk-study over the
203 in-custody idle captures every D-117 member already carries (P(asymmetric burst)
analysis — zero nights, rev-contamination move 1); refusal-mechanism census + the
PRE-WINDOW plumbing fix (member_id→reason_code in verdict rows; 16 shadow codes
brought under the ratified spec) — rev-refusal move 2/3, operationally URGENT before
the three nights regardless of any paper.

codex
I’ll build this from the actual 24 referee files, then reconcile the rankings against D‑117, the design memo, and the corrected floor/Window‑C accounting. I’ll keep this read-only and make the final message the complete portfolio synthesis.
  → Read project controls, D-117/design memo, and inventory the 24 proposal/review pairs
  • Read all 24 counter-reviews first and extract verdicts, scores, costs, kill gates, and salvage
  • Read proposals selectively to resolve ranking, sequencing, and cost ambiguities
  • Synthesize ranked portfolio, paper arc, synergy map, second-paper bet, and Ed rulings
exec
/bin/zsh -lc "pwd && git status --short --branch && rg --files | rg '("'^|/)(RUN_STATE'"\\.md|TASK_QUEUE\\.md|AGENT_PLAN\\.md|docs/agent_playbook\\.md|docs/orchestration\\.md|docs/decision_log\\.md|DESIGN-MEMO\\.md)"'$'"' && rg --files ../portfolio | sort" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
## main...origin/main
RUN_STATE.md
TASK_QUEUE.md
AGENT_PLAN.md
docs/orchestration.md
docs/decision_log.md
docs/agent_playbook.md
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md
../portfolio/prompts/attention-variant-energy.txt
../portfolio/prompts/batch-concurrency-energy.txt
../portfolio/prompts/contamination-characterization.txt
../portfolio/prompts/cross-runtime-contrast.txt
../portfolio/prompts/drift-thermal-science.txt
../portfolio/prompts/energy-nutrition-label.txt
../portfolio/prompts/floor-methodology-general.txt
../portfolio/prompts/kv-context-energy.txt
../portfolio/prompts/long-generation-dynamics.txt
../portfolio/prompts/moe-routing-energy.txt
../portfolio/prompts/mtp-energy.txt
../portfolio/prompts/mvp-icpe-upgrade.txt
../portfolio/prompts/open-explore-advisor.txt
../portfolio/prompts/open-explore-contrarian.txt
../portfolio/prompts/open-explore-registry.txt
../portfolio/prompts/open-explore-repo.txt
../portfolio/prompts/param-scaling-energy.txt
../portfolio/prompts/prefill-scaling-laws.txt
../portfolio/prompts/quantization-ladder.txt
../portfolio/prompts/refusal-as-result.txt
../portfolio/prompts/spec-decode-energy.txt
../portfolio/prompts/split-inference-metrology.txt
../portfolio/prompts/tokenizer-honesty.txt
../portfolio/prompts/wall-meter-validation.txt
../portfolio/prop-attention-variant-energy.err
../portfolio/prop-attention-variant-energy.md
../portfolio/prop-batch-concurrency-energy.err
../portfolio/prop-batch-concurrency-energy.md
../portfolio/prop-contamination-characterization.err
../portfolio/prop-contamination-characterization.md
../portfolio/prop-cross-runtime-contrast.err
../portfolio/prop-cross-runtime-contrast.md
../portfolio/prop-drift-thermal-science.err
../portfolio/prop-drift-thermal-science.md
../portfolio/prop-energy-nutrition-label.err
../portfolio/prop-energy-nutrition-label.md
../portfolio/prop-floor-methodology-general.err
../portfolio/prop-floor-methodology-general.md
../portfolio/prop-kv-context-energy.err
../portfolio/prop-kv-context-energy.md
../portfolio/prop-long-generation-dynamics.err
../portfolio/prop-long-generation-dynamics.md
../portfolio/prop-moe-routing-energy.err
../portfolio/prop-moe-routing-energy.md
../portfolio/prop-mtp-energy.err
../portfolio/prop-mtp-energy.md
../portfolio/prop-mvp-icpe-upgrade.err
../portfolio/prop-mvp-icpe-upgrade.md
../portfolio/prop-open-explore-advisor.err
../portfolio/prop-open-explore-advisor.md
../portfolio/prop-open-explore-contrarian.err
../portfolio/prop-open-explore-contrarian.md
../portfolio/prop-open-explore-registry.err
../portfolio/prop-open-explore-registry.md
../portfolio/prop-open-explore-repo.err
../portfolio/prop-open-explore-repo.md
../portfolio/prop-param-scaling-energy.err
../portfolio/prop-param-scaling-energy.md
../portfolio/prop-prefill-scaling-laws.err
../portfolio/prop-prefill-scaling-laws.md
../portfolio/prop-quantization-ladder.err
../portfolio/prop-quantization-ladder.md
../portfolio/prop-refusal-as-result.err
../portfolio/prop-refusal-as-result.md
../portfolio/prop-spec-decode-energy.err
../portfolio/prop-spec-decode-energy.md
../portfolio/prop-split-inference-metrology.err
../portfolio/prop-split-inference-metrology.md
../portfolio/prop-tokenizer-honesty.err
../portfolio/prop-tokenizer-honesty.md
../portfolio/prop-wall-meter-validation.err
../portfolio/prop-wall-meter-validation.md
../portfolio/rev-attention-variant-energy.md
../portfolio/rev-batch-concurrency-energy.md
../portfolio/rev-contamination-characterization.md
../portfolio/rev-cross-runtime-contrast.md
../portfolio/rev-drift-thermal-science.md
../portfolio/rev-energy-nutrition-label.md
../portfolio/rev-floor-methodology-general.md
../portfolio/rev-kv-context-energy.md
../portfolio/rev-long-generation-dynamics.md
../portfolio/rev-moe-routing-energy.md
../portfolio/rev-mtp-energy.md
../portfolio/rev-mvp-icpe-upgrade.md
../portfolio/rev-open-explore-advisor.md
../portfolio/rev-open-explore-contrarian.md
../portfolio/rev-open-explore-registry.md
../portfolio/rev-open-explore-repo.md
../portfolio/rev-param-scaling-energy.md
../portfolio/rev-prefill-scaling-laws.md
../portfolio/rev-quantization-ladder.md
../portfolio/rev-refusal-as-result.md
../portfolio/rev-spec-decode-energy.md
../portfolio/rev-split-inference-metrology.md
../portfolio/rev-tokenizer-honesty.md
../portfolio/rev-wall-meter-validation.md
../portfolio/synth-impact.err
../portfolio/synth-impact.md
../portfolio/synth-pragmatic.err
../portfolio/synth-pragmatic.md

exec
/bin/zsh -lc "rg -n '"'^#{1,4} '"' RUN_STATE.md TASK_QUEUE.md docs/agent_playbook.md docs/orchestration.md AGENT_PLAN.md docs/decision_log.md docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md ../portfolio-brief.md && wc -l ../portfolio/rev-*.md ../portfolio/prop-*.md | tail -n 3" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:112:## Findings
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:114:### F1 — Live-ledger bookending is not yet armable (blocker)
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:133:### F2 — The mint path needs a real v2, not another widened literal list (blocker)
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:153:### F3 — The D-102 successor packet is a pre-arm dependency (blocker)
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:169:### F4 — Referenced trace missing (should-fix)
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:180:### F5 — Queue terminology is superseded (should-fix)
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:184:### Ranked design decisions and rejected alternatives
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:200:### Proven template lineage
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:215:### Immutable identifier proposal
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:225:### Common order-manifest contract
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:242:### Per-window plans
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:244:#### Alpha — 1.5B decode floor plus prefill rider
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:265:#### Beta — 7B decode floor plus prefill rider
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:273:#### Gamma — 1.5B-versus-7B decode contrast
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:300:### Runtime evidence and budgets
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:332:### §5A operator bookends
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:353:### Prefill floor claim eligibility
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:368:### Two-stage mint freeze
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:405:### Synthetic three-window live-ledger regression
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:433:### Optional 256-token prefill contrast
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:441:### Freeze order and lead gates
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:452:### Work-order list with enforced WRITE_SCOPE units
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:469:### What the lead should double-check
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:486:## Residual risk
AGENT_PLAN.md:1:# Agent Implementation Plan
AGENT_PLAN.md:8:## Ground Rules For Agents
AGENT_PLAN.md:33:## Single Source Of Truth Map
AGENT_PLAN.md:58:## Canonical Architecture
AGENT_PLAN.md:71:## Phase Index
AGENT_PLAN.md:73:### Phase 1: Approval, Feasibility, And Measurement Design
AGENT_PLAN.md:118:### Phase 2: Harness, Mac Vertical Slice, And Homogeneous Baselines
AGENT_PLAN.md:166:### Phase 3: Disaggregation, Offline KV Replay, And Interconnect Sweep
AGENT_PLAN.md:191:### Phase 4: Core Characterization And Analysis
AGENT_PLAN.md:211:### Phase 5: Presentation, Repository Polish, And Final Submission
AGENT_PLAN.md:231:## Current Verification Command
AGENT_PLAN.md:243:# Phase 1: config + schema verbs
AGENT_PLAN.md:248:# Phase 2: run the harness (mock, deterministic) and verify the bundle
AGENT_PLAN.md:255:## Run Report Protocol
AGENT_PLAN.md:274:## Task Queue Protocol
docs/orchestration.md:1:# The Orchestration Process
docs/orchestration.md:12:## Roles: a lead, independent implementers/reviewers, and a human at the top
docs/orchestration.md:45:## The loop, end to end
docs/orchestration.md:110:### Stop cards and paused work
docs/orchestration.md:142:## The artifact system (where rigor becomes auditable)
docs/orchestration.md:189:## Council discipline
docs/orchestration.md:210:## Spend guardrails (WO-022; R2 ruled, Ed-ratified 2026-07-13)
docs/orchestration.md:261:## Topology: how it evolved (an example of the loop improving itself)
docs/orchestration.md:288:## What one session looks like (2026-07-07/08, the merge session)
docs/orchestration.md:306:## Reconstructing the loop on a clean machine
docs/orchestration.md:338:## Where to read the evidence
docs/decision_log.md:1:# Decision Log
docs/decision_log.md:7:## How To Use This Log
docs/decision_log.md:22:## Index
docs/decision_log.md:146:## D-001: Run bundles store normalized `config.json`, not YAML
docs/decision_log.md:186:## D-002: Telemetry sampling via subprocess + file, no controller threading
docs/decision_log.md:234:## D-003: Timestamp and clock-alignment policy
docs/decision_log.md:277:## D-004: `powermetrics` privilege workflow
docs/decision_log.md:326:## D-005: One bundle per repetition, grouped by experiment manifest
docs/decision_log.md:366:## D-006: Dashboard v1 is a static HTML report generator
docs/decision_log.md:408:## D-007: YAML config input is deferred
docs/decision_log.md:441:## D-008: Split runs arrive via schema v0.2 (`run_kind` + `split_plan`)
docs/decision_log.md:487:## D-009: Dependency policy: stdlib core, optional extras
docs/decision_log.md:527:## D-010: Run ID scheme
docs/decision_log.md:562:## D-011: `summary_metrics.json` is the bundle completion marker
docs/decision_log.md:622:## D-012: Failure-reason to run-status mapping
docs/decision_log.md:669:## D-013: Controller-as-DUT mitigation for Mac-local runs
docs/decision_log.md:721:## D-014: Statistical protocol for repeated runs
docs/decision_log.md:776:## D-015: Split-mechanism priority and same-runtime rule
docs/decision_log.md:838:## D-016: Benchmark model selection
docs/decision_log.md:907:## D-017: CI scope
docs/decision_log.md:942:## D-018: Per-backend `power_w` definition and rail policy
docs/decision_log.md:989:## D-019: Mock adapters use simulated time via an injectable clock
docs/decision_log.md:1028:## D-020: CLI binds `FakeClock` for all-mock runs, `SystemClock` otherwise
docs/decision_log.md:1077:## D-021: Controller flushes `events.jsonl` before the reduce stage
docs/decision_log.md:1125:## D-022: Auto-generated run-ID suffix is config-hash-derived, not random
docs/decision_log.md:1175:## D-023: Per-item phase status lives solely in the exit checklists
docs/decision_log.md:1232:## D-024: Adapters receive a `RunContext`, not piecemeal parameters
docs/decision_log.md:1296:## D-025: One shared bundle read layer for all bundle consumers
docs/decision_log.md:1347:## D-026: Measured window is bounded by sampling-active marker events
docs/decision_log.md:1402:## D-027: Per-rail rows must share per-sample timestamps; misalignment is a structured failure
docs/decision_log.md:1460:## D-028: `reduce` verb rewrites `summary_metrics.json` in place
docs/decision_log.md:1508:## D-029: Config schema declares nullable optionals; serialization unchanged
docs/decision_log.md:1562:## D-030: `validate-bundle` stays structural by default; `--strict` adds raw-evidence checks
docs/decision_log.md:1741:## D-031: Multi-model council review, PR convention, and drift controls
docs/decision_log.md:1853:## D-032: `phase_energy_j` is gross-only in summary v0.1
docs/decision_log.md:1892:## D-033: Prompt-content provenance is recorded per run bundle
docs/decision_log.md:1942:## D-034: Slice 2O owns the workload program after 2M and 3.0.1
docs/decision_log.md:1987:## D-035: Replay claims require fresh-process (subprocess-per-stage) isolation
docs/decision_log.md:2017:## D-036: Spike verdict codes derive from measured data, never hardcoded
docs/decision_log.md:2043:## D-037: Claims ladder (L0-L4) binds reader-facing claim language from 2M onward
docs/decision_log.md:2087:## D-038: Analysis-plans contract binds L2/L3 claims to pre-registered plans
docs/decision_log.md:2134:## D-039: Workload program v2 — substrate first, identification before scale
docs/decision_log.md:2192:## D-040: Suite architecture v2 — one generic suite mechanism, bundle-level replication
docs/decision_log.md:2240:## D-041: Benchmark interop — frozen-subset imports + marker-shim energy layer
docs/decision_log.md:2305:## D-042: D-034 implementation lane reopened — suite build proceeds pre-2M (owner directive)
docs/decision_log.md:2340:## D-043: Supersession-closure discipline
docs/decision_log.md:2382:## D-044: Suite config identity — omission-serialized ref + effective-manifest hash
docs/decision_log.md:2446:## D-045: Suite substrate execution semantics
docs/decision_log.md:2522:## D-046: AP-6 sentinel delivery — ids-native, BOS-less, literal equal shape
docs/decision_log.md:2560:## D-047: Affine ladder pins — level set, smoke sizing, gate denominators
docs/decision_log.md:2624:## D-048: Split program is model-first — pre-registered compositional prediction before split runs
docs/decision_log.md:2674:## D-049: Split transfer-energy boundary accounting on discrete-GPU ends
docs/decision_log.md:2713:## D-050: Active stop cards and process-trace manifests
docs/decision_log.md:2780:## D-051: Advisor status site uses source-derived static pages plus fail-soft live GitHub overlays
docs/decision_log.md:2836:## D-052: Capstone scope contract — frozen umbrella headline and contribution ladder
docs/decision_log.md:2864:## D-053: Contrast-level statistical inference and the frozen analysis registry
docs/decision_log.md:2892:## D-054: False-effect guard floor and unknown-term claim-ceiling policy
docs/decision_log.md:2927:## D-055: Research-question registry is the canonical live index
docs/decision_log.md:2949:## D-056: Suite order policies and order_row provenance
docs/decision_log.md:2985:## D-057: Uncertainty terms — drift is a bound; claim-gate reason codes are stable vocabulary
docs/decision_log.md:3104:## D-058: Token-normalization and stack-identity contract adopted
docs/decision_log.md:3127:## D-059: Claims-lint mechanical enforcement in CI
docs/decision_log.md:3155:## D-060: Depth-before-breadth stop line (RATIFIED)
docs/decision_log.md:3209:## D-061: Review-layer evaluation rule v2 (replaces the two-zero-sessions drop rule)
docs/decision_log.md:3238:## D-062: Confirmatory sampling policy — fixed n, explicit demotion, no silent top-ups
docs/decision_log.md:3268:## D-063: Process architecture v2 — machine-readable state kernel first
docs/decision_log.md:3310:## D-064: Delegated-invocation compliance surface — tracked JSONL event stream, report envelope, enforced write scope
docs/decision_log.md:3434:## Adjudication note (was: drafting notes for the lead)
docs/decision_log.md:3446:## D-065: bridge-protocol/v1.1 — co-work lane, session wrappers, tolerant envelope
docs/decision_log.md:3525:## D-066: Scoped spec-freeze override for the AXI extension agenda (Ed override)
docs/decision_log.md:3571:## D-067: Idle reporting basis — gross headline; idle-subtracted is a labeled within-device secondary view
docs/decision_log.md:3639:## D-068: Site deployment is Ed-manual; sessions end with a drift report, never a deploy
docs/decision_log.md:3683:## D-069: Advisor-doc alignment (stream S-0) is sanctioned front-facing work
docs/decision_log.md:3710:## D-070: Architectural-axes extension agenda (AXI): scope, claim posture, batch-axis rulings
docs/decision_log.md:3786:## D-071: G10 memory-fit rule ratified (axi-sd-memory-fit-shape-v1); device-list review opened
docs/decision_log.md:3816:## D-072: Standing self-merge-with-full-gate authority (gh merges included)
docs/decision_log.md:3839:## D-073: D-016 device-list amendment — Mac + 3080 Ti primary fleet, 12 GiB cap
docs/decision_log.md:3857:## D-074: Conditional Qwen3-4B primary repin + OLMo-1B conversion spike authorized
docs/decision_log.md:3874:## D-075: Extension-axis intake — ranked fold-in without new thesis proliferation
docs/decision_log.md:3934:## D-076: Site capacity right-sizing (AUD-WO-039 review) — measured-first budgets
docs/decision_log.md:3948:## D-077: Environment guard, idle admission, and cooldown v2
docs/decision_log.md:4058:## D-078: Soundness gate — no claim-bearing extraction from time-anchor-defective powermetrics corpora
docs/decision_log.md:4096:### D-078 amendment — 2026-07-20: fail-closed vocabulary and immutable summaries
docs/decision_log.md:4156:### D-078 additive registry addendum — 2026-07-20: causal-set repair
docs/decision_log.md:4169:### D-078 amendment — 2026-07-21: convergence fix wave (lead adjudications)
docs/decision_log.md:4210:### D-078 amendment — 2026-07-21 (second): two-edge envelope and confirmation-round rulings
docs/decision_log.md:4284:### D-078 amendment — 2026-07-21 (third): provenance authentication rulings
docs/decision_log.md:4671:## D-079: Calibration acceptance v2 — derived bracket screen plus budget, pre-flight calibration screen with cause-removal retry, one general production scope name, and publishing the decode floor now
docs/decision_log.md:4922:## D-080: Standing fresh-eyes sweep — a periodic, non-reactive outside review
docs/decision_log.md:5078:## D-081: Session History pointer convention — parser learns the pointer-retirement form
docs/decision_log.md:5095:## D-082: Floor-mint execution semantics — basis-pinned consumption and the cross-window v2 artifact
docs/decision_log.md:5131:## D-083: The additive effective-clearable-effect expression is a disclosure obligation, not an acceptance threshold
docs/decision_log.md:5191:## D-084: Operative decode-floor pin re-set to the composed cell gate 7.377086 J
docs/decision_log.md:5228:## D-085: splitwise_decode_v1 / qwen25_7b_decode_floor_v1 pre-registration ratifications (Q1–Q9)
docs/decision_log.md:5297:## D-086: Supersession-aware cooldown-evidence join (FIX-9)
docs/decision_log.md:5342:## D-087: Cold-gate exercise record — F1, and the third-failure-closes precedent
docs/decision_log.md:5427:## D-088: Cooldown-join escalation — no FIX-11; ratified join contract; conditioned merge license (cold gate + refuter synthesis)
docs/decision_log.md:5499:## D-089: D5-J — declaration-first, join-owned occurrence ledger; the liberalization cell struck; no interim merge
docs/decision_log.md:5603:## D-090: Delegation conduct — read-only briefs bind, and commit messages may not assert reviews that have not happened
docs/decision_log.md:5637:## D-091: Metrology pivot — the instrument is the product
docs/decision_log.md:5677:## D-092: Wall meter ratified for the paper (claim C8); operate without hardware until purchased
docs/decision_log.md:5707:## D-093: DA-1 cold-gate synthesis — register-and-merge at a corrected head; no behavior-changing fix round; bench scan extended
docs/decision_log.md:5770:## D-094: Gauntlet counting domain — composed design adopted (writer outcome enum + fail-closed legacy log binding)
docs/decision_log.md:5826:## D-095: MANIFEST-CONTRAST design — analysis-manifest v3 with cross-stack armwise-max floor gating
docs/decision_log.md:5886:## D-096: Metrology v1 plan vocabulary ratified; four window-A plans FROZEN
docs/decision_log.md:5926:## D-097: B1 cold-gate synthesis — v2 outcome consumption DEFERRED to commit 3; interim v2/outcome refusal everywhere
docs/decision_log.md:5979:## D-098: Metrology window A record — salvage close, recorded-deviation post-cal, verdict FAILED as-issued
docs/decision_log.md:6027:## D-099: Metrology window B record — bird-SIGSTOP protocol, knife-edge anchor finding, streaming hazard; verdict FAILED as-issued
docs/decision_log.md:6088:## D-100: Salvage-dangler terminal semantic — cold-gate synthesis (S2-A as redrawn, landed in the S3 semantics-dispatch shape)
docs/decision_log.md:6207:## D-101: The site gates nothing — publication chain fully decoupled from CI pass/fail and session doctrine
docs/decision_log.md:6241:## D-100 addendum (2026-08-01): four mechanical spellings ratified for the repair; reader fail-open folds in
docs/decision_log.md:6280:## D-102: CAL-BRACKET-D079-01 pins ratified — corpus-derived budget cap, identity-epoch freshness, never-zero allowance, decimal numeric semantics
docs/decision_log.md:6344:## D-103: C3 structural cold-gate synthesis — WAL attestation ordering, two named aggregation policies (cold instance overruled on B2 with recorded dissent), reader-tolerant/writer-strict path discipline
docs/decision_log.md:6465:## D-104: C3 residuals cold-gate synthesis — acquisition-identity lock tokens, positive writer-grammar tail recognizer (convergent gate; both magistrate candidates rejected)
docs/decision_log.md:6545:## D-105: C3 disposition synthesis — LAND with a final custody micro-commit; F1/F2 registered as a NEW ruling with refuter-amended closure; number-grammar exactness struck
docs/decision_log.md:6625:## Repairs disposition note (2026-08-02, magistrate; D-104-precedent containment)
docs/decision_log.md:6649:## D-106: b-ii residual synthesis — Variant D (land the inert branch, register NOTHING, window B blocked on two decidable fixes; cold instance overruled with dissent)
docs/decision_log.md:6723:### D-078 registry amendment — 2026-08-02: D-100 semantics-scoped non-refusing disposition
docs/decision_log.md:6736:## D-101 addendum (2026-08-02): live-content site tests leave the blocking gate
docs/decision_log.md:6758:## D-101 addendum II (2026-08-03): the site observatory is a separate failure domain
docs/decision_log.md:6792:## D-107: D100-BII-BINDING-01 nested-content closure — cold-gate synthesis: producer-derived admission grammar with value domains (C-A′), scope expanded to the inventory grammar and the false-refusal repairs, over-refusal gate added to the row
docs/decision_log.md:6927:## D-108: D100-BII-BINDING-01 clause (c) RETIRED as a license precondition — row closes on (a)+(b)+(d), with the clause-(d) three-occurrence re-record carrying the formal load
docs/decision_log.md:6988:## D-109: CAL-BRACKET-D079-01 F3 — A-min-with-reservation adopted (writer-enforced receipt ledger, reservation-first, repo-committed head pin); R1 ledger-authority and R2 prior-observation-set rulings
docs/decision_log.md:7083:## D-110: Mint 1 retroactively NON-CLAIM-BEARING (taint-and-remint); RT-2 dependency edge minted; the night consult's 7B-mint license SUSPENDED
docs/decision_log.md:7135:## D-111: Adjudication evidence gains tracked custody — docs/process_traces/ is the home; .desk is working scratch only
docs/decision_log.md:7167:## D-112: Window B re-evaluation STOP gate — classification (i) adopted; the D-100 license is EXHAUSTED AS DRAWN; the r06 disposition ruling is PARKED FOR ED
docs/decision_log.md:7209:## D-109 addendum II: reviewed mint-core interface amendment (integration-collision resolution); D-110 oracle clarification
docs/decision_log.md:7248:## D-113: WINDOW B TERMINALLY CLAIM-RETIRED — abandonment ruled (Ed); fresh collection beginning Window C; F7 whole-window precedent affirmed
docs/decision_log.md:7363:## D-114: T3-CHAIN DESCOPE — t3 stays the interactive control plane; t3-resident-during-measurement-windows is DROPPED (Ed directive, supersedes the 2026-08-03 T3-DRIVE priority)
docs/decision_log.md:7432:## D-115: Quiet-guard Q2 setup authority is a FIXED INSTALLATION CAPABILITY, not general root authority (Commit-1 packet entry; renumbered from the contract's proposed D-114 marker)
docs/decision_log.md:7489:## D-116: D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (D-110 condition (b) SATISFIED)
docs/decision_log.md:7508:## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired
docs/agent_playbook.md:1:# Agent Playbook: Ordered Missions
docs/agent_playbook.md:24:## How To Pick A Mission
docs/agent_playbook.md:50:## Mission M0: Preflight (every session)
docs/agent_playbook.md:91:## Mission M1: Slice 2N — Pre-Hardware Hardening (queue P2-007)
docs/agent_playbook.md:121:### 2N.1 `RunContext` seam + raw evidence
docs/agent_playbook.md:143:### 2N.2 Measured window excludes sampler startup
docs/agent_playbook.md:162:### 2N.3 Reducer token-count fallback
docs/agent_playbook.md:178:### 2N.4 Rail-summation timestamp contract
docs/agent_playbook.md:193:### 2N.5 Config schema accepts emitted configs
docs/agent_playbook.md:212:### 2N.6 Post-hoc `reduce` verb + structured reducer failures
docs/agent_playbook.md:228:### 2N.7 Report/reducer rail-policy alignment (via 2N.8)
docs/agent_playbook.md:240:### 2N.8 Shared bundle read layer (`BundleReader`)
docs/agent_playbook.md:258:### 2N.9 Schema v0.2 compatibility check (design-only, no code required)
docs/agent_playbook.md:279:## Mission M2: Measurement-Corpus Backup Protocol (queue P0-002)
docs/agent_playbook.md:300:## Mission M3: Background / Related-Work Draft (queue P3-001, Stage 4.6)
docs/agent_playbook.md:323:## Mission M4: Close D-016 Model Selection (queue P2-004)
docs/agent_playbook.md:346:## Mission M5: Slice 2G — MLX Runtime Adapter (part of queue P2-003)
docs/agent_playbook.md:366:## Mission M6: Slice 2H — powermetrics Telemetry Adapter
docs/agent_playbook.md:386:## Mission M7: Slice 2I — Mac Vertical Slice (the flagship)
docs/agent_playbook.md:407:## Mission M8: Slices 2K/2L — Remote Targets
docs/agent_playbook.md:434:## Mission M9: Slice 2M — Homogeneous Baselines
docs/agent_playbook.md:451:## Mission M10: Phase 3 Stage 3.0 — KV Feasibility Spikes
docs/agent_playbook.md:470:## After Any Mission
TASK_QUEUE.md:1:# JouleWise Task Queue
TASK_QUEUE.md:6:## Intake Rule For New Tasks
TASK_QUEUE.md:34:## Priority Scale
TASK_QUEUE.md:47:## Ranking Factors
TASK_QUEUE.md:65:## Ready/Shelf Rule
TASK_QUEUE.md:80:## Machine-State Lanes (adopted C-007, 2026-07-07)
TASK_QUEUE.md:92:## Historical Queue Snapshot (superseded 2026-07-15)
TASK_QUEUE.md:98:## Completed Queue Items
TASK_QUEUE.md:184:## Shelved Follow-Ups With Triggers (C-027 disposition ledger — REV-10)
TASK_QUEUE.md:213:## Current Do-Not-Do-Yet List
TASK_QUEUE.md:241:## Queue Maintenance
TASK_QUEUE.md:254:## Intake Batch Owed To The Kernel (2026-07-30/31)
TASK_QUEUE.md:306:## Current Queue
TASK_QUEUE.md:384:## Active Global Work-Selection Gates
TASK_QUEUE.md:388:### [ED-EXTERNAL] lane
TASK_QUEUE.md:399:### [QUIET-MAC] lane
TASK_QUEUE.md:412:### [AGENT] lane
TASK_QUEUE.md:462:### Shelved task records
RUN_STATE.md:1:# JouleWise Run State
RUN_STATE.md:16:## ⏳ 2026-08-07 — paper-first session (LIVE; interim block, refreshed mid-flight)
RUN_STATE.md:47:## ✅ CHECKPOINT 2026-08-06 late — machine-move stop (resume script)
RUN_STATE.md:101:## ⏳ 2026-08-06 AFTERNOON — re-mint fork: historical consumption is closed at main; Ed's ruling owed
RUN_STATE.md:156:## ✅ CHECKPOINT 2026-08-06 morning — executed by the afternoon session above
RUN_STATE.md:242:## ⏳ 2026-08-05 LATE NIGHT — Fable resume: all 4 audits harvested, D-115 adjudicated, two Sol rounds in flight
RUN_STATE.md:299:### Overnight progress ledger (updated ~23:50; all evidence in .desk + session scratchpad, custody commits as noted)
RUN_STATE.md:342:### D-079 ISSUANCE HELD by cold gate (recorded ~03:30 2026-08-06) — issuance is IMPLEMENTATION, not an edit
RUN_STATE.md:369:### GOVERNING PRIORITY STACK (Ed, 2026-08-06) — all work serves the paper
RUN_STATE.md:378:### SYLLABUS ANCHOR (Ed, 2026-08-06) — the overarching goal
RUN_STATE.md:388:### QG census — magistrate stop-condition set (recorded ~02:40 2026-08-06)
RUN_STATE.md:407:### ESCALATION TRIGGER FIRED — quiet-guard observation-failure→absence class (recorded ~01:15 2026-08-06)
RUN_STATE.md:423:### Ed directive batch (2026-08-05 ~22:00, in-thread; 12-hour autonomous window)
RUN_STATE.md:445:## ✅ CHECKPOINT 2026-08-05 night — Ed model-switch stop (successor is FABLE; read this, then the EVENING queue)
RUN_STATE.md:453:### What landed this session (pushed; main green at `b55008f`)
RUN_STATE.md:472:### IN FLIGHT at checkpoint — harvest, do NOT re-run blind
RUN_STATE.md:504:### Next substantive item (un-gated payoff)
RUN_STATE.md:512:### Standing facts unchanged
RUN_STATE.md:518:## ✅ CHECKPOINT 2026-08-05 evening — DESCOPE + RESUME SCRIPT (still-valid queue; NIGHT block above updates it)
RUN_STATE.md:531:### SUCCESSOR'S QUEUE — start here, all agent-startable desk work
RUN_STATE.md:548:### What landed this session (all pushed; main green)
RUN_STATE.md:565:### IN FLIGHT at checkpoint (harvest from disk — do NOT re-run blind)
RUN_STATE.md:579:### DESCOPE — what is SHELVED (do not build; reopen only on Ed's word)
RUN_STATE.md:591:### Design record worth keeping (from the credential consult, before descope)
RUN_STATE.md:605:### Follow-on rows to register (queued this checkpoint)
RUN_STATE.md:621:### Standing operating facts (unchanged, still binding)
RUN_STATE.md:638:## ✅ 2026-08-05 — Ed's decision batch executed (PR #100 merged; acks recorded; quiet-guard ruled)
RUN_STATE.md:681:## ✅ CHECKPOINT 2026-08-04 ~06:30 — Ed-ordered stop (successor script)
RUN_STATE.md:726:## ✅ CHECKPOINT 2026-08-04 early AM — T3 HANDOFF (successor script)
RUN_STATE.md:739:### What landed overnight (all pushed; nothing dangling)
RUN_STATE.md:845:### ED OWES (nothing blocks the successor's queue)
RUN_STATE.md:865:### Standing operating facts for the successor
RUN_STATE.md:884:## ✅ CHECKPOINT 2026-08-03 late night — T3 CUTOVER (successor session, ACTIVE)
RUN_STATE.md:1021:## ✅ CHECKPOINT 2026-08-03 night — 16h-runway stream state (successor is FABLE, MAGISTRATE, on T3 Code)
RUN_STATE.md:1129:## DESK-SESSION UPDATE (HISTORICAL — superseded by the checkpoint block at top) (2026-08-03, Ed away — first the cold-gate arc, then a sleep-window of non-claim rows) — read this, then the two ⏸️ blocks above
RUN_STATE.md:1221:## EXECUTED RESUME SCRIPT (2026-08-02 ~16:10 PT checkpoint — FULLY EXECUTED by the 2026-08-03 desk session; see the DESK-SESSION UPDATE above; retained as historical record)
RUN_STATE.md:1350:## PRIOR RESUME SCRIPT (2026-08-01 desk session, second checkpoint; resume EXACTLY here)
RUN_STATE.md:1451:## PRIOR ACTIVE RESUME SCRIPT (2026-08-01 ~07:00 PT checkpoint; EXECUTED this desk session — retained for the collection facts)
RUN_STATE.md:1559:## PRIOR ACTIVE RESUME SCRIPT (2026-07-31 ~22:15 PT checkpoint; EXECUTED — window A verdict emitted [FAILED], window B run and salvage-closed; retained for the collection facts)
RUN_STATE.md:1663:## PRIOR STATE (2026-07-31 claims-desk close-out; resume script below FULLY EXECUTED)
RUN_STATE.md:1755:## EXECUTED RESUME SCRIPT (2026-07-30 19:15 PT pre-window checkpoint; historical — fully executed, see CURRENT STATE)
RUN_STATE.md:1834:## PRIOR STATE (2026-07-30 afternoon; the resume script below is EXECUTED except where struck)
RUN_STATE.md:1856:## EXECUTED RESUME SCRIPT (2026-07-30 ~11:00 PT handoff checkpoint; historical)
RUN_STATE.md:1984:## Start Here For Every Big Run
RUN_STATE.md:2033:## Historical Stop-Card Note
RUN_STATE.md:2039:## ACTIVE_STOP_CARD
RUN_STATE.md:2043:## Active Global Work-Selection Gates
RUN_STATE.md:2047:## Restart By Machine-State Lane
RUN_STATE.md:2051:### [ED-EXTERNAL]
RUN_STATE.md:2055:### [QUIET-MAC]
RUN_STATE.md:2059:### [AGENT]
RUN_STATE.md:2065:## CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR #77 open
RUN_STATE.md:2089:## CHECKPOINT 2026-07-18: Claude script bridge runs in the pet's app task
RUN_STATE.md:2115:## CHECKPOINT 2026-07-17 (late session): env-guard branch open, review pending
RUN_STATE.md:2166:## Superseded stop card (CP-5)
RUN_STATE.md:2178:## Current Project Status
RUN_STATE.md:2185:### The central measurement fact (read before any measurement decision)
RUN_STATE.md:2197:### Collection state
RUN_STATE.md:2231:### The critical path: build the mint (HISTORICAL — CLOSED 2026-07-30)
RUN_STATE.md:2266:### Disk
RUN_STATE.md:2290:### Orchestration
RUN_STATE.md:2298:### What needs Ed
RUN_STATE.md:2377:## Session History (pointers only — run reports own the narrative)
RUN_STATE.md:2499:## Current Verification
RUN_STATE.md:2596:### Historical verification archive (exact at the recorded heads)
RUN_STATE.md:2739:## Known Workspace State
RUN_STATE.md:2806:## Historical Next-Work Snapshot (superseded 2026-07-15)
RUN_STATE.md:2824:## Reference Decisions And Blockers (non-selection context)
    4712 ../portfolio/prop-tokenizer-honesty.md
    7413 ../portfolio/prop-wall-meter-validation.md
  157760 total

exec
/bin/zsh -lc 'wc -l ../portfolio/rev-*.md ../portfolio/prop-*.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
     184 ../portfolio/rev-attention-variant-energy.md
     292 ../portfolio/rev-batch-concurrency-energy.md
     199 ../portfolio/rev-contamination-characterization.md
     319 ../portfolio/rev-cross-runtime-contrast.md
     227 ../portfolio/rev-drift-thermal-science.md
     172 ../portfolio/rev-energy-nutrition-label.md
     216 ../portfolio/rev-floor-methodology-general.md
     308 ../portfolio/rev-kv-context-energy.md
     181 ../portfolio/rev-long-generation-dynamics.md
     339 ../portfolio/rev-moe-routing-energy.md
     223 ../portfolio/rev-mtp-energy.md
     180 ../portfolio/rev-mvp-icpe-upgrade.md
     305 ../portfolio/rev-open-explore-advisor.md
     166 ../portfolio/rev-open-explore-contrarian.md
     337 ../portfolio/rev-open-explore-registry.md
     326 ../portfolio/rev-open-explore-repo.md
     315 ../portfolio/rev-param-scaling-energy.md
     308 ../portfolio/rev-prefill-scaling-laws.md
     294 ../portfolio/rev-quantization-ladder.md
     240 ../portfolio/rev-refusal-as-result.md
     318 ../portfolio/rev-spec-decode-energy.md
     143 ../portfolio/rev-split-inference-metrology.md
     292 ../portfolio/rev-tokenizer-honesty.md
     205 ../portfolio/rev-wall-meter-validation.md
    5212 ../portfolio/prop-attention-variant-energy.md
    7197 ../portfolio/prop-batch-concurrency-energy.md
    5736 ../portfolio/prop-contamination-characterization.md
    7785 ../portfolio/prop-cross-runtime-contrast.md
    7012 ../portfolio/prop-drift-thermal-science.md
    4688 ../portfolio/prop-energy-nutrition-label.md
    5953 ../portfolio/prop-floor-methodology-general.md
    6247 ../portfolio/prop-kv-context-energy.md
    5684 ../portfolio/prop-long-generation-dynamics.md
    7701 ../portfolio/prop-moe-routing-energy.md
    6744 ../portfolio/prop-mtp-energy.md
    4634 ../portfolio/prop-mvp-icpe-upgrade.md
    4269 ../portfolio/prop-open-explore-advisor.md
    6004 ../portfolio/prop-open-explore-contrarian.md
    6368 ../portfolio/prop-open-explore-registry.md
    6941 ../portfolio/prop-open-explore-repo.md
    5696 ../portfolio/prop-param-scaling-energy.md
    4961 ../portfolio/prop-prefill-scaling-laws.md
    8344 ../portfolio/prop-quantization-ladder.md
    6725 ../portfolio/prop-refusal-as-result.md
    7701 ../portfolio/prop-spec-decode-energy.md
    7944 ../portfolio/prop-split-inference-metrology.md
    4712 ../portfolio/prop-tokenizer-honesty.md
    7413 ../portfolio/prop-wall-meter-validation.md
  157760 total

exec
/bin/zsh -lc "sed -n '1,220p' ../portfolio-brief.md
sed -n '1,90p' docs/agent_playbook.md
sed -n '1,230p' docs/orchestration.md
sed -n '1,190p' RUN_STATE.md
sed -n '2039,2064p' RUN_STATE.md
sed -n '2178,2310p' RUN_STATE.md
sed -n '2739,2805p' RUN_STATE.md
sed -n '213,240p' TASK_QUEUE.md
sed -n '306,462p' TASK_QUEUE.md
sed -n '7508,7645p' docs/decision_log.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
PAPER-PROPOSAL DEVELOPMENT SESSION (one of a 20-direction parallel fan-out).

You are developing ONE candidate research-paper direction for the JouleWise project
into a full, reviewable proposal. Work read-mostly; do NOT create or modify any files —
your final message IS the deliverable. You may read any repo file.

== PROJECT BRIEF (state as of 2026-08-07) ==
JouleWise is Ed's undergraduate CS capstone: treating Apple's `powermetrics` software
power counter as a calibrated scientific instrument for phase-resolved (prefill vs
decode), single-request LLM inference energy on one named M3 Max stack (MLX, Qwen2.5
family, 4-bit). Core findings/machinery to date: in-window bracketed pulse-train
calibration of timing attribution; the instrument is ATTRIBUTION-LIMITED (~1 J per
phase member from ~30 ms edge uncertainty × ~33 W swings; repetition cannot average it
away), not noise-limited; detection floors composed from repeatability + worst-case
attribution + measured never-zero drift, published labelled; TWO separate claim gates
(floor clearance; interval-supported direction) with a practical ~5 J sizing bar for
phase contrasts; fail-closed collection protocol (pre-registration, admission gates,
ABBA counterbalancing, hash-bound custody chains, refusal log as evidence). MVP paper
draft is complete-in-structure (docs/paper/draft-v1.md) with demonstration values
pending. The claim path (decision D-117, adopted today): THREE fresh prospective quiet
windows — 1.5B decode floor, 7B decode floor, 1.5B-vs-7B decode contrast — each
live-bracketed under an issued calibration-acceptance regime; prefill floor cells ride
the floor windows; a 256-token prefill contrast arm is an open option (128-token
prefill contrast is MARGINAL vs the bar — custodied desk check).
Steps from here: 3 quiet-mac nights (operator bookends only) + desk work (window plans,
mint pinsets, extraction specs, regression) → mint floors → populate the paper →
capstone submission; then an ICPE-class version.

== CONTEXT AND CONSTRAINTS ==
- Advisor: Suzanne Rivoire (JouleSort co-author) — sets a real metrology bar; plain
  language required in reader-facing text.
- Venue ladder: capstone (CSCSU-class) → ICPE full research track is the realistic
  ambitious target; top-tier only if a mechanism/split research bet lands.
- Hardware: M3 Max MacBook Pro 128 GB (the instrumented unit); an RTX 3080 Ti desktop
  rig; optional Jetsons; a Yokogawa WT310E wall meter is NOT owned but may be BORROWED
  from the advisor's lab (claim C8 ratified the wall-meter axis as future work).
- Measurement economics: each claim window is a 2-4 h quiet night with operator
  bookends; effects must clear the two gates (~5 J practical sizing for phase
  contrasts on this stack; workload LENGTH is the free lever since attribution error
  is ~duration-independent).
- Ed's ORIGINAL research goals (pre-metrology-pivot, still wanted long-term):
  mechanism-level energy profiling as a third metrics axis alongside quality+latency —
  speculative decoding, multi-token prediction (MTP), mixture-of-experts (MoE)
  routing, KV/attention variants (e.g. KDA), and SPLIT/disaggregated inference across
  consumer devices; a modular harness where every experiment axis (model, inference
  technique, workload, size) is swappable; energy-honest leaderboard/reporting
  critique. Repo context worth reading: docs/strategy/2026-08-06-impressiveness-roadmap.md,
  docs/research_question_registry.md, docs/research_question_bank.md,
  docs/paper/draft-v1.md (esp. §§3-5), CLAIMS_STATUS.md, docs/decision_log.md (D-117,
  at end of file).

== YOUR DELIVERABLE (final message, markdown, ~600-1200 words) ==
1. TITLE + one-sentence thesis.
2. PROJECT-BRIEF-AND-STEPS paragraph: half a page restating the current project state
   and the concrete steps from today to THIS paper (audience: Ed deciding what to
   fund with nights/desk time).
3. CONTRIBUTIONS (3-5, numbered, each falsifiable).
4. EXPERIMENT PLAN sized against the instrument: cells, contrasts, expected effect
   magnitudes vs the ~5 J sizing bar (estimate from public knowledge + repo
   diagnostics you can find; state which effects might NOT clear and what the refusal
   would mean), number of quiet windows needed, desk-work list, any new harness
   capability required (and whether it violates the frozen single-request boundary).
5. HARDWARE/INSTRUMENT needs (owned / borrowed / new; wall-meter dependency yes/no).
6. VENUE fit + why (capstone chapter? ICPE? workshop?), and how it BUILDS ON the MVP
   paper (shared method sections, what's new).
7. RISKS + KILL CRITERIA (what desk evidence would kill it before spending a night).
8. RELATION TO ED'S ORIGINAL GOALS: which original axis it serves, or state plainly
   that it does not.
Be concrete and quantitative wherever possible; flag every number you are unsure of.

== HARD CONSTRAINT (Ed, binding) ==
Every proposal MUST turn the EXISTING material into a solid scientific paper: the
calibrated instrument and its custody/fail-closed protocol machinery, the
attribution-limited finding, the banked diagnostics, the data the three D-117 windows
will produce (decode floors for 1.5B and 7B, prefill floor riders, the decode
contrast), and modest extensions collectible on the owned hardware under the SAME
instrument discipline. Do NOT propose work that abandons the instrument or needs
apparatus/data without a concrete path (the borrowed WT310E wall meter is allowed
where justified as an extension of existing material). If your assigned direction
cannot honestly be built from existing material, SAY SO PLAINLY and shrink it to the
version that can — a smaller honest paper beats an unmoored ambitious one.

== REQUIRED READING (read these in the repo before writing anything) ==
docs/paper/draft-v1.md (the whole draft — every proposal must state what it reuses
from it); CLAIMS_STATUS.md; the D-117 entry at the end of docs/decision_log.md;
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md (exactly what the three
windows produce, budgets, mint machinery); docs/strategy/2026-08-06-impressiveness-roadmap.md;
docs/research_question_registry.md; docs/research_question_bank.md;
docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md.
# Agent Playbook: Ordered Missions

Audience: an agent (or human) told "go do the next step" with no other
context. This file turns the project's plans into self-contained,
executable missions. Each mission says what to read, what to do, how to
verify, and what to update afterward.

Division of labor (D-023 discipline — do not duplicate):

- **This file owns:** the operational wrapper per mission (read-first
  lists, execution order, verification commands, handoff checklists) and
  the code-level pointers from the 2026-07-05 external code review that
  exist nowhere else.
- **It points to:** `docs/phase_N/phase_N_plan.md` for objectives, gates,
  acceptance criteria, and fallbacks; `docs/phase_2/
  hardware_slice_implementation_guide.md` for hardware-slice pinned APIs;
  `docs/decision_log.md` for settled decisions; the phase exit checklists
  for current per-item status.
- **No status lives here.** To find out what is already done, read
  `RUN_STATE.md` and the exit checklists. To find out what outranks what,
  read `TASK_QUEUE.md`. If this playbook and a plan disagree, the plan
  wins; fix the drift in the same run.

## How To Pick A Mission

1. Run Mission M0 (preflight) — always.
2. Take the highest-ranked task in `TASK_QUEUE.md` whose gate is open.
3. Find its mission below and execute it. One mission per session unless
   the first finishes early and cleanly.

Gate summary (check the queue/checklists for live status; this is just
the dependency shape):

```text
ungated, any time:      M1 (Slice 2N), M2 (backup protocol prep), M3 (related work)
needs user/advisor:     M4 (D-016 model selection), and the P1 evidence gates
needs D-016 + install:  M5 (2G MLX)
needs auth session:     M6 (2H powermetrics)
needs M5+M6:            M7 (2I Mac slice — the flagship)
needs P1-006 evidence:  M8 (2K/2L remote-target live validation;
                         2K fixture-first stack merged 2026-07-08 via PR #11)
needs M7:               M9 (2M baselines)
post-docs branch:       M10 Stage 3.0.1 verdict is replay_supported
                         after lead live re-verification
needs 2M baselines:     M10 later pairing-feasibility matrix + split runs
```

---

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

# The Orchestration Process

How this project is actually built: a human researcher directing a
multi-model AI system whose workflow is itself a deliberate, versioned,
self-instrumenting piece of engineering. This document is the single
in-repo description of that process. (The executable playbooks live
outside the repository as reusable "skills" so they transfer to future
projects; this page describes what they do and where their evidence
lands in this repo.) Binding role and process changes live in
`docs/decision_log.md`; this page avoids copying volatile model versions.

## Roles: a lead, independent implementers/reviewers, and a human at the top

- **Ed (researcher)** sets research direction, methodology
  non-negotiables (raw-evidence bundles, dual-basis capture with gross-energy
  headlines, named
  measurement boundaries, no unauditable claims), hardware/access
  decisions, and — critically — *process policy*: every rule below
  traces to a standing instruction issued after an observed failure or
  opportunity. External-facing claims and merge authority derive from
  him (he granted the lead conditional self-merge authority on
  2026-07-08 once the review gate had proven itself).
- **The designated lead** owns
  decomposition, triage, design adjudication, every final diff gate,
  all live/hardware verification, merge decisions, bookkeeping, and
  process evolution. Other agents save lead capacity without inheriting
  final authority; all escalation paths terminate at the lead.
- **Independent implementation and review agents** do the heavy reading and
  writing: implementation against pinned specs, adversarial review
  lenses, test writing, test *auditing* (never of its own tests — a
  fresh instance audits), docs drafting, and review of the lead's own
  consequential decisions. Cross-model review is load-bearing by
  design: the attributed per-layer catch record (below) shows the two
  roles consistently catching different classes of defect.
- **Specialist agents** handle bounded sweeps (for example, docs
  consistency) and, when a stream genuinely needs
  mid-stream judgment, as a stream director — a role that is now the
  exception rather than the default (see Topology).
- **Image-heavy analysis uses the designated image-capable review route** per
  C-012, after the site-observatory stream's image-critique rounds.
- **Invited-peer validation is allowed to overturn lead designs**; C-014
  recorded two lead designs overturned by an invited peer before
  implementation.

## The loop, end to end

Every substantial session runs one conductor procedure:

1. **Intake** — read `RUN_STATE.md` (the intake pointer), the task
   queue, the latest run report; never re-decide anything the decision
   log settled.
2. **Decompose** — split work into genuinely independent streams
   (disjoint expected diff footprints), one git worktree + branch each;
   assign each stream a review tier by *cost of being wrong*
   (measurement-semantics and contract-bearing work gets the full
   pipeline; docs get a light tier). Preflight gates: hardware-shaped
   streams require a confirmed device inventory; anything pinned
   without live validation carries a PROVISIONAL label; measurement
   sessions require a no-agent "quiet machine" lock.
3. **Per-stream pipeline** — for each reviewable unit: an invited
   design-argument round (the implementer must argue trade-offs before
   coding), implementation, then a layered review stack:
   2–3 fresh-instance counterreview lenses over the diff → lead triage
   with recorded dispositions → fixes → a dedicated test-amplification
   round (an independent writer adds edge-case tests) → a
   writer≠reviewer test audit (a fresh instance hunts tautological,
   vacuous, or wrong-expectation tests) → the lead's diff gate.
4. **Lead live gates** — never delegated: the lead runs the real flow
   (real corpus, real CLI, real hardware where present). This layer has
   repeatedly caught blockers no other layer saw, including defects
   whose own tests were green because the tests encoded the same wrong
   assumption as the code.
5. **Merge gate** — multi-commit series land as branch + PR. Before any
   merge: a pre-merge oversight pass by 2–3 fresh reviewers with
   distinct angles (deep regression hunt; claim-to-evidence trace;
   merge-order simulation across sibling PRs), lead triage, fixes, CI
   green. **Final-head rule:** any commit that lands after the last
   review round gets one more fresh review before merge — no commit
   merges unreviewed, however small (its first application caught a
   crash path in a "trivial" post-review fix).
6. **Integration review** — after parallel streams merge, one dedicated
   review hunts *interaction* defects no single-stream review can see.
   Its catches are definitionally unique (first outing: two).
7. **Bookkeeping** — a single session record (run report) with a
   verbatim process-trace appendix; the intake pointer and queue
   refreshed; a delegated docs-consistency sweep before the final
   commit (its latest pass found 15 real drift items; earlier passes
   found 5–6). Large documentation batches add the pre-commit
   docs-verify mode; the `consistency-sweep` skill owns that shape,
   including the D-043 supersession check.
8. **Same-session distillation** — lessons fold into the process
   playbooks the same session they are learned. Measured effect: one
   failure mode recurred five times before its fix was distilled, zero
   times after. The current operation-loop also runs its §0
   primary-deliverable check and §8 shipped-check before the session is
   considered done.
9. **Post-landing verification and close-out** — landed work gets the
   matching verification workflow with severity-tiered refuters. Sessions
   that change front-facing state refresh `docs/site/DRIFT.md`; no agent
   regenerates or deploys the site. Automation informs and Ed deploys
   manually, per D-068 and `RUN_STATE.md` end-of-work step 8.
10. **Meta-review (the final step)** — event-driven, not calendar-driven:
    when a review layer stops earning its keep, when an intervention
    repeats despite a folded fix, or when the user asks, the loop is
    reviewed with its own evidence discipline (see Topology for the
    consensus one such review produced). After large workloads the
    post-large-workload meta-reassessment (owned by operation-loop §10)
    always fires, and it runs LAST.

### Stop cards and paused work

When a session stops with live work in progress, the lead creates or
updates an `ACTIVE_STOP_CARD` at the top of `RUN_STATE.md`. While active,
that card is the single restart authority and overrides every lower
"what next" list, queue rank, mission guide, and run-report default.

A stop card must name:

- the resume authority and exact artifact pointer,
- the reason for stopping,
- worktrees, branches, PRs, and off-repo artifacts that must not be
  cleaned accidentally,
- status terms for each paused item,
- the first resume action, and
- the clearance criteria.

Use these status terms for paused work:

| Term | Meaning |
|---|---|
| `APPLIED_UNVERIFIED` | A worker reports code or docs are applied, but the lead has not gated the diff. Not merge-safe. |
| `LEAD_GATED` | The lead has reviewed and run the required local/live checks for the item. |
| `PR_OPEN_CI_GREEN` | A PR exists and CI is green, but merge authority has not yet fired. |
| `MERGED` | The accepted work has landed on main. |
| `UNREAD_UNADJUDICATED` | A report/synthesis exists but has not been consumed into decisions, queue rows, or rejected findings. |
| `ADJUDICATED` | Findings have explicit accept/reject/defer disposition and downstream artifacts are updated. |

Before an intentional pause, do the minimal stop sync even if full
bookkeeping cannot fit: update only `RUN_STATE.md`'s stop card and the
rank-0 queue row. That is enough to prevent accidental bypass.

## The artifact system (where rigor becomes auditable)

Each fact has exactly one home; everything else points at it:

| Artifact | Role |
|---|---|
| `docs/decision_log.md` | Binding design decisions, each with alternatives considered, consequences, and revisit conditions. The log is the count authority; nothing re-decides these silently. |
| `docs/council_log.md` | The deliberation record: review-council positions, reasoning exchanged, who prevailed, overridden dissents — so a future reader can reconstruct *why*, not just *what*. The log is the range/count authority. |
| `docs/contracts/` | Claim/evidence contracts: `claims_ladder.md` (D-037) plus `analysis_plans.md` (D-038) form the claim gate; strict validation is the evidence ticket. |
| `docs/stream_logs/` | Per-stream decision ledgers, committed WITH the code they justify: every non-trivial in-stream decision (`A-1..A-30`, `B-1..B-46`, …) with mandatory evidence pointers; wrong pins are SUPERSEDED in place, never erased. |
| `docs/run_reports/` | One record per working session: outcomes, verification evidence, a per-layer catch/yield table, the delegation-calibration ledger, restart instructions. |
| `docs/process/state_kernel.json` | Source of truth for work selection: active gates, dependencies, and machine-state lanes ([QUIET-MAC] / [AGENT] / [ED-EXTERNAL]). |
| `TASK_QUEUE.md` | Generated detailed queue projection plus dated history; do not hand-copy its live rows into reader docs. |
| `RUN_STATE.md` | Intake pointer with the generated restart projection. History lives in run reports. |
| `docs/risk_register.md` | Live risks with triggers and mitigation states. |

Instrumentation ledgers close the loop on the process itself:

- **Per-layer yield:** every review layer's unique catches are
  attributed and tallied per session under D-061 (C-027; replaces the
  earlier two-zero-sessions auto-drop, which the integration-review
  zero/zero/five sequence falsified): applicability is decided by
  PRE-DECLARED mechanical predicates; outcomes are classified
  accepted-unique-defect / duplicate / clean-verification /
  false-positive-suppression (suppression is not a catch); severity
  weights are fixed before the session; three applicable exposures
  TRIGGER an expected-loss review decision, never automatic deletion;
  safety/final-head/integration layers are never auto-dropped on
  zero-defect streaks. (One layer, the default specialist review lens, was
  dropped under the old rule before D-061.)
- **Delegation calibration:** every delegated unit gets a row — task
  altitude (pinned-spec / design-freedom / judgment-call), outcome
  (assigned by the lead after the gate, never self-labeled), catches,
  and lead rework minutes, with prompt-defects separated from
  model-defects. Delegation boundaries move on this evidence, not
  vibes. Current signal: pinned-spec delegation runs essentially
  defect-free; the serious defects cluster in volunteered additions and
  design-freedom wire contracts — which is exactly where the full lens
- **Invocation manifest:** substantial delegated/tool/skill runs get a
  lightweight manifest row per invocation. Minimum fields:
  `run_id`, `parent_report`, `role_or_lens`, `model`, `wrapper`,
  `session_id`, `prompt_sha256`, `prompt_path`, `output_path`, `status`,
  `consumed_by`, `disposition`, and `commit_or_pr`. Raw logs can stay
  out of git; every ephemeral artifact still needs a committed pointer
  row with `path`, `sha256` or stable id, `promoted_to`, and
  `not_promoted_reason`.

## Council discipline

Councils are expensive instruments. Use a full council for methodology,
measurement validity, schema/contract changes, claim boundaries, hardware
protocols, or explicit user requests. For ordinary implementation, use a
small number of targeted lenses plus lead adjudication.

Every high-impact council must leave a durable scorecard:

- unique catches by severity,
- accepted/rejected/deferred/false-positive counts,
- lead triage and rework time when practical,
- shipped artifacts,
- queue rows created or re-ranked,
- decision-log IDs promoted, and
- a disposition table: finding → ruling → owner → artifact/queue/decision
  target → closure check.

Deferred decision-log promotion is itself a tracked obligation, not
ambient prose in a report.

## Spend guardrails (WO-022; R2 ruled, Ed-ratified 2026-07-13)

The following policy text is the R2-ratified section, landed verbatim per
audit work order WO-022 (`docs/reviews/2026-07-13-comprehensive-audit/`).

SPEND GUARDRAILS (capstone benchmark bands) — provisional calibration constants; review after two completed arcs; sunset at capstone submission.

1. ACCOUNTING SOURCE. Sol spend: `codex-usage` local accounting (the standing snapshot convention), corroborated by codex-run-v3 manifest `token_usage` rows where populated. The extraction window must cover the full arc — sum incremental snapshots for multi-day arcs; a single trailing-24h view is insufficient. Fable spend: estimated from local usage accounting; each snapshot names its method and price-table version. Price table v2026-07 (pinned until amended): GPT-5.6-sol $5/$30 per M in/out, cached input $0.50; Fable 5 $10/$50, cache reads $1. All figures are estimates, not billing truth, and are recorded as such. Missing data is recorded as `accounting_unknown`, never as zero.

2. DENOMINATOR AND CACHED-TOKEN TREATMENT. Token bands count total tokens (cached + uncached, all directions) exactly as codex-usage reports them — cached tokens are never excluded (exclusion invites cache-heavy gaming). Dollar figures apply cached pricing honestly. Cross-family aggregate ceilings bind in combined estimated dollars, because raw cross-family token sums are not commensurable (C-028: Sol ~180x the token volume, Fable ~3.4x the cost).

3. BOUNDARIES AND ATTRIBUTION. An arc = one council-log C-row, opened at its first delegated session, closed at its closeout snapshot. A work order = one WO/task id. Failed calls, retries, resumes, refuters, fix rounds, delta re-audits, lead usage, and subagents all count against the initiating WO and arc. Arcs and WOs may not be split, renamed, or reopened to reset counters.

4. BANDS. Each dimension is independent. SOFT crossing = record-and-continue: flag in the spend snapshot plus a one-line justification in the council row. HARD crossing = pause-and-ask Ed before any NEW delegated work in that category; in-flight sessions finish; quiet-machine measurement is never interrupted.

   | Scope | Soft | Hard |
   |---|---|---|
   | Sol high session | 6M tokens | 12M |
   | Sol xhigh session | 8M | 16M |
   | Sol ultra session | 40M | 60M |
   | Bench-effort WO | 10M / 3 Sol sessions / ~$40 combined | 20M / 6 / ~$80 |
# JouleWise Run State

This file is the single running pointer for the project: the one doc to
read to get back here. Session records live in `docs/run_reports/` and
`docs/process_traces/`; deliberation lives in `docs/council_log.md`;
policy lives in `docs/decision_log.md`. The three dated restart docs
`docs/process_traces/RESUME-2026-07-26.md`, `RESUME-2026-07-27.md`, and
`RESUME-2026-07-28.md` are now point-in-time session records only — each
carries a superseded banner, and everything still current in them is
folded in below. Do not create another dated restart doc; update this
file instead.

Last updated: 2026-08-07 — **LIVE SESSION (14h Ed window). Read this
block first;** the 2026-08-06 checkpoint below is executed history.

## ⏳ 2026-08-07 — paper-first session (LIVE; interim block, refreshed mid-flight)

**Ed's directives this session:** (1) abandon t3 work; (2) MVP capstone
paper FIRST, rest later; (3) 14h autonomous window; (4) three quiet
nights + desk work accepted as the path → **D-117 transcribed+pushed**
(D-110 re-mint order superseded; three prospective windows; prefill
floors ride floor windows; contrast decode-only; 256-tok prefill arm
still Ed's option); (5) Workflow license for non-serial desk work.

**DONE this session (all pushed):** checkpoint resume items 2-4 —
T3-CHAR-PAIR r01/r02 analysis banked (`fc48b1b`, dormant floor 0.192 W,
NON-CLAIM); prefill feasibility scout MARGINAL-at-128-tok custodied
(`docs/process_traces/2026-08-07-prefill-feasibility/`); C-049 marathon
council record (`03841c8`); skill-usage log; D-117 (`dbb9685`);
CLAIMS_STATUS un-staled (`a1f0e19`).

**IN FLIGHT (harvest, do not re-run):** (a) paper fix round on branch
`impl/paper-mvp-complete` — Sol xhigh, WRITE_SCOPE
docs/paper/draft-v1.md, closing round-2 findings (lens A 3 blockers:
tense, two-gate rule collapse, prefill-marginality misstatement; lens B
11; F-BIB-1) — review records + bibliography audit custodied on the
branch (`3542265`, `1892edc`); on harvest: lead diff gate → delta
re-audit → PR → merge on green (D-072). (b) Plan-freeze design consult
(Sol xhigh, read-only, scratchpad desk worktree) for the three-window
packet → on return: lead ratify → enforced-scope implementation units →
adversarial review → PR(s). Then: three-night operator packet for Ed;
end-of-session sweep + run report.

**Worktrees:** `<session-scratchpad>/desk` (main, bookkeeping) — prune
at close. Main tree holds `impl/paper-mvp-complete`.

## ✅ CHECKPOINT 2026-08-06 late — machine-move stop (resume script)

**Nothing in flight; nothing unpushed after this commit.** All background
jobs harvested; consult custodied; campaign logs sha-verified untouched.

**STATE IN ONE BREATH:** PR #109 merged (`c537386`); first consumption
attempt proved the historical re-mint structurally closed at main (see
AFTERNOON block + `docs/process_traces/2026-08-06-d110-remint-fork/`);
Sol xhigh + magistrate recommend Option 2 (three fresh prospective
windows); **Ed has NOT yet ruled** — he was probing costs when the
session stopped.

**Ed's in-thread directives this exchange (record, not yet decision-log):**
1. **MVP claim scope: "a little more than just decode, at least
   decode/prefill."** Magistrate's proposed shape (not yet Ed-acked):
   prefill FLOOR cells ride both fresh floor windows cheaply; a prefill
   CONTRAST first gets a labelled non-claim desk feasibility check from
   historical diagnostics against the D-078 ~5 J effective bar — if it
   clears, the contrast window grows a prefill ABBA arm; if not, prefill
   floors are claimed, contrast stays decode-only, and the infeasibility
   becomes a limitations paragraph.
2. **Ed challenged the zero-agent window rule** ("why can't you be
   running quietly?"). Owed answer components, for the successor: (a)
   physics at our bar — a bursty resident agent stack at ~0.1–0.5 W over
   minute-scale members is joules-to-tens-of-joules gross vs a ~5 J
   effective bar; idle subtraction cancels only the steady part; every
   CLAIM window to date was zero-agent; the app-resident mode was only
   ever used for fenced NON-claim characterization. (b) The banked
   `runs_char_t3appup_20260804_r01/_r02` captures exist precisely to
   QUANTIFY the dormant-app delta — **desk analysis queued (protocol
   §Analysis: mean/p95 package power from rich_telemetry_idle.jsonl)**;
   run it and give Ed a NUMBER. (c) The honest reframe: the binding
   presence constraint is §5A's sudo (network-time toggle), not the
   zero-agent rule; the agent-armed window design (QUIET-GUARD two-phase
   handoff, commits 2–4 + a scoped sudoers rule for the two systemsetup
   commands) exists and was descoped by Ed's OWN ruling as not worth the
   security-critical code — reopenable on his word if three fresh
   windows change his calculus.
3. Ed confirmed understanding that Option 2 = recollect the science
   windows (~3 windows, bookend-presence only) while everything else
   (instrument arc, acceptance rule, tooling, process record) stands.

**RESUME ORDER for the successor:**
1. If Ed has ruled the fork → transcribe the decision (supersede/amend
   D-110 + D-113 rewire per SYNTHESIS.md) and start the Option-2 desk
   queue (AFTERNOON block bottom). If not ruled → he owes: fork ruling,
   prefill-contrast shape ack, three-nights scheduling.
2. T3-CHAR-PAIR r01/r02 desk analysis (the dormant-app number) — cheap,
   answers his live question, informs any zero-agent-rule revisit.
3. Prefill-contrast feasibility desk check from historical diagnostics
   (labelled, non-claim).
4. End-of-session bookkeeping STILL OWED from the marathon session:
   consistency sweep, council log, skill-usage log.

## ⏳ 2026-08-06 AFTERNOON — re-mint fork: historical consumption is closed at main; Ed's ruling owed

**PR #109 merged on green** under D-072 at the gate-reviewed head
`d85b4f9` (no post-review commits; ledger + custody backup verified
byte-identical to the checkpoint sha before merge). `d079recon`
worktree + local branch pruned. All three D-110 conditions were thereby
satisfied — and the FIRST consumption attempt exposed a structural
block.

**THE FINDING (full record:
`docs/process_traces/2026-08-06-d110-remint-fork/` — DIAGNOSIS,
consult prompt+response, SYNTHESIS):** no historical window (a10,
window-C, old window-D, 7B-floor, contrast — all pre-genesis) can pass
authenticated max-bracket consumption at merged main. The issued ledger
holds only import-marked receipts; candidate discovery excludes imports
by design (CAL-BRACKET arc `63f43a68`, retained through issuance);
future live receipts cannot causally bracket past windows. Every
refusal was fail-closed; campaign logs sha-verified untouched (backups
in `~/JouleWise-window-custody/d110-remint-20260806/log_backups/`).

**Sol xhigh pre-decision consult (run `20260806T165843Z-10884`) +
magistrate CONCUR: Option 2 — supersede the D-110 historical re-mint
with THREE compact prospective windows** (fresh 1.5B decode floor,
fresh 7B decode floor, fresh contrast; each live-bracketed under the
issued regime, ~3 h class each). Chain: historical corpus → issued
acceptance rule → live brackets → prospective floors → contrast.
Option 1 (finite-allowlist historical candidacy) preserved as a
cold-gated contingency only — semantics sketch is in the consult
response. The consult verified all five historical bracket pairs exist
physically (drifts 0.000167–0.003680 s, under the 0.010818 s screen) —
the objection is provenance completeness, not causality.

**ED OWES (his ruling moots a cold gate — apex authority):**
1. Ratify superseding D-110's re-mint order with prospective
   replacement (+ the D-113 dependency rewire the consult flags).
2. MVP claim scope: decode contrast only, or more phase cells?
3. Three quiet-mac nights scheduling appetite (§5A each).

**Desk work unblocked regardless (consult §4, queue for the successor):**
freeze the three window plans + budgets (new immutable identifiers —
"Window D" name is taken); 1.5B decode-only floor plan from the proven
10-absolute/40-null design; generalized mint pinsets w/ per-plan
six-decimal literals (the D-084 literal `7.377086` refuses any
corrected mint under EVERY option — closure is per-plan supply via the
generalized path); freeze extraction specs/order manifests/
evidence-root ids/contrast manifest; synthetic three-window live-ledger
integration regression; D-102 successor-artifact packet; results/
methods prose with placeholders.

**Session ops notes:** verdict/extraction tooling gotchas (relative
`--runs-dir` path-doubling; verdict >2 min; stale `campaign.lock` on a
killed run) are recorded in the trace DIAGNOSIS. End-of-session
bookkeeping (consistency sweep, council log, skill-usage log) still
OWED.

## ✅ CHECKPOINT 2026-08-06 morning — executed by the afternoon session above

**IMMEDIATE RESUME ACTION (one live item):**
1. **PR #109 (`impl/d079-issuance`) — merge on green, then RE-MINT.**
   This PR ISSUES the D-079 calibration acceptance artifact (the
   authentication anchor for all floor-mint claims): D-116, issued
   config (fixture→issued, file sha `316113960c…`), committed head-pin
   (seq 76 / head `08456d50…`), cold-gate custody, + a 5-file test
   reconciliation. It cleared its FULL gauntlet (two rule-11 cold gates,
   adversarial audit + 3 delta rounds, exact-bytes dual cold review,
   zero-regression reconciliation + coverage-preservation audit ACCEPT).
   At checkpoint: CI running. **On green → self-merge under D-072**
   (it's the completed gate shape). If a successor finds it already
   merged, skip to the re-mint.

**THE AUTHORITATIVE LEDGER — do not lose (survives /clear as a file):**
- `runs/calibration_observation_ledger.jsonl` — the 76-receipt genesis
  chain, **git-ignored** (local custody artifact), sha256
  `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`.
  BACKED UP at `~/JouleWise-window-custody/d079-issuance-20260806/`
  (byte-identical). Deterministic from the custodied inputs
  (`docs/process_traces/2026-08-06-d079-issuance-coldgate/ISSUANCE-*`,
  on the PR branch → main after merge) + raw evidence. The committed
  head-pin (in the config) is the D-109 R1.4 trust anchor; the ledger
  file itself is a custody artifact. **Must stay backed up before the
  re-mint consumes it.**

**THE RE-MINT (task 8, the payoff — next after PR #109):**
- D-110 conditions now ALL satisfied: (a) PR #100, (c) PR #105, (b) THIS
  issuance. MINT-GENERALIZE-01 UNBLOCKED. Next: ONE custody session —
  governed a10 phase-floor extraction
  (`configs/floor_mint/a10_extraction_spec.json`, ~20 min) THEN mint #1
  re-derivation under the corrected selector, embedding the never-zero
  `A_s = max(observed_drift_s, 0.010818)` allowance (D-102 pin 3 /
  D-110). Same custody session (FLOOR-BIND-01 fence). Claim-critical →
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
detects it in the ~4-minute pre-calibration, with cause-removal (never
outcome-selection) retry semantics.

**Corrected floor figures — the old ones must not be repeated.** a10's
**absolute** floors are **3.823787 J prefill / 3.592138 J decode**,
INCLUDING the 0.652272 J whole-window drift allowance. The 3.17 / 2.94 J
numbers circulated earlier are the attribution-width floors BEFORE the
allowance and are diagnostics only (D-079 clause 5).

**AMENDED BY D-084 (2026-07-29): `3.592138` is the ABSOLUTE COMPONENT IN
ISOLATION, not the operative decode floor.** Mint #1's cell composes
a10's absolute 3.592138 J with window C's comparative 7.377086 J, and
under W3 rule 8 the cell gate is the **max, never the sum** — so the
canonical **operative decode floor is 7.377086 J**, and that is the hard
six-decimal literal pinned in `scripts/mint_floor_artifact.py`. D-079
clause 5's "3.592138" pin predates window C's comparative extraction and
is superseded for the operative figure; both components remain published
and LABELLED per D-078 clause 11.

### The critical path: build the mint (HISTORICAL — CLOSED 2026-07-30)

All four blockers below are closed and this section is retained as
chronology only: `scripts/mint_floor_artifact.py` is the non-test call
site (1), the 30-vs-37 basis question RESOLVED (2), `production_window`
is in `_CALIBRATION_SCOPES` (3), and `impl/floor-mint` merged via PR #87
(4). Mint #1 merged via PR #88 at `da83337`.

`build_floor_cell` / `build_floor_artifact` / `build_absolute_record` /
`build_comparative_record` in `joulewise/detection_floor.py` have zero
non-test call sites; `scripts/extract_detection_floors.py` writes an
extraction report and stops. Established blockers:

1. **`claim_ready` requires an absolute AND a comparative record in the
   SAME cell**, so a10 alone mints a structurally `smoke_only` artifact.
   Mint #1 must pair a10's absolute cell with window C's decode
   comparative. Verifying that the two share backend, metric,
   `window_class`, condition family, and stack identity is a GO/NO-GO,
   not a task.
2. **A 30-vs-37 member authentication mismatch:** the a10 phase spec
   selects 30 members; the passed verdict authenticates 37. Extraction of
   the authenticated basis takes **20 min 36 s** on real data — budget
   for it.
3. **Windows C and D have no legal `calibration_scope`.**
   `_CALIBRATION_SCOPES` is `("window_a", "window_b_revalidation",
   "smoke")`. D-079 clause 4 adopts one general production name; proposed
   literal `production_window`.
4. **Pre-mint schema hardening was then written but unmerged** (it
   merged via PR #87; the branch is on main): branch
   `impl/floor-mint` @ `617060a` (pushed) makes the extraction report
   export the admissible half-widths it already computes, and moves
   `_WIDENED_FLOOR_KEYS` from optional into the required key sets so
   width ABSENCE is a schema error rather than a silent fall-back to the
   point-only floor. Suite 2198 OK.

### Disk

**EXECUTED 2026-07-28 (Ed-authorized 2026-07-27: iCloud-only acceptable,
delete after verified upload — resolving both open disk questions).**
Disk now has **115 GB free** (was 33 GB; ~61 GB freed by the repo prune described below, the rest by unrelated local housekeeping). The selective-prune plan was
generalized to every runs corpus: all 27 corpora are archived in
`~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/` with a
per-corpus `MANIFEST.sha256`. Verification before any deletion: APFS-clone
name+byte parity; `brctl evict` of 100% of files (evict success = upload
complete); rematerialize-and-rehash of 20,028 files from iCloud (100% of
small evidence files + sampled traces) against the manifests — 0
mismatches. Then 1,848 `powermetrics*.plist` traces ≈ 61 GB were deleted
locally; **every small evidence file remains resident**, each pruned dir
carries `PRUNED.md` + `MANIFEST.sha256`. Restoring any trace =
`brctl download` its path under the archive.

Kept fully local (no deletion): `runs_window_a10_20260725(+_bound)` and
`runs_window_c_20260726(+_bound)` (mint #1 inputs),
`runs_window_a5_quarantine` (quarantine is evidence), and in `runs/` the
six frozen acceptance-gate bundles (`example-mac-mlx-*`) + `experiments/`
custody — the retained-corpus strict gate re-ran green post-prune (3/3,
incl. six-bundle strict validation), and keep-list file counts verified
unchanged.

### Orchestration

Global `CLAUDE.md` hard rule 11 now defines the topology: Fable as
MAGISTRATE and Ed's direct, Opus 5 as LIEUTENANT / operational chief, a
cold-Fable-instance gate with mandatory (not discretionary) triggers, and
an enumerated forbidden-to-decide-alone list for the lieutenant. D-080's
standing fresh-eyes sweep is the first exercise of that list.

### What needs Ed

1. RESOLVED 2026-07-27/28: Ed answered both disk questions (iCloud-only
   acceptable; delete after verified upload) and the archive+prune
   executed — see "Disk" above. Note the traces are now iCloud-only
   (single durable copy); flag if a second physical copy is wanted.
2. **AC power** for measurement windows — the production policy requires
   it and the machine was on battery.
3. A magistrate ruling on a conflict between D-080 and D-061: D-080's
   anti-ritual clause 4(ii) evaluates a rotating lens against the
   two-zero-sessions drop rule, which D-061 explicitly superseded with an
   expected-loss adjudication ("three applicable exposures TRIGGER an
   expected-loss review decision, never automatic deletion").
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
| A22 | P2-004 | P2 Next Slice | PARTIAL; READY; GATES close: P1-001 [AGENT] | Close model selection (D-016): decision-log entry with models, revisions, artifact paths, local mirror, fallback candidate; mid-model pick, CUDA load, GGUF paths outstanding. | Decision-log entry complete; full closure gated on P1-001. Evidence: Decision-log entry: models, revisions, artifact paths, mirror, fallback. Authority: [D-016](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Provisional small-model pick 2026-07-06 opens 2G. |
| A23 | P2-005 | P2 Next Slice | PARTIAL; READY; GATES live_promotion: P1-006 [AGENT] | Remote targets (2K NVIDIA/vLLM/ssh and 2L Orin): fixture-first and NV-GATE-2 code-now hardening are merged; protocol pins remain provisional until the external live-promotion rows execute. | Live 2K/2L evidence or a documented access blocker; applicability table updated; NV-GATE-2 live rows close without promoting fixture evidence. Evidence: Remote bundle or documented access blocker; Applicability table updated; NV-GATE-2 items closed at live promotion. Authority: [NV-GATE-2 live-promotion spec](docs/specs/c027/nv-gate-2_live_promotion.md). Acceptance: [2K live verification checklist](docs/phase_1/2k_live_verification_checklist.md). Note: PR #49 merged the code-now verifier, streaming, cleanup, and localhost gates; P1-006 and device execution remain open. |
| A24 | P2-016 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists) [AGENT] | Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment. | Each item lands with its named gate; dispositions plus rejected items recorded in C-011. Evidence: Each subitem lands with its named gate; Dispositions recorded in C-011. Authority: [C-011 ledger + C-027 (post-2M umbrella)](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-016 acceptance](docs/process/state_kernel.json). Note: Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake. |
| A25 | P2-047A | P2 Next Slice | READY [AGENT] | Freeze the controller capture-overhead ABBA harness comparing the standard event path with a buffered or minimal-marker path under identical outputs and hashes. | A frozen controller-overhead ABBA harness preserves output identity and defaults to instrumented-stack scope rather than unvalidated subtraction. Evidence: Frozen ABBA manifest; Standard and buffered/minimal-marker paths have identical output policy and hashes; Analysis refuses unsupported subtraction. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047A acceptance](docs/process/state_kernel.json). Fence: Do not subtract controller overhead without a separately justified correction model (Hardening adjudication C7). |
| A29 | DOC-008-REFLECTION | P4 Polish | READY [AGENT] | Replace planning_reflection_protocol.md with the DOC-008 redirect stub and reconcile its inbound references under condition 6. | Retire the reflection protocol as an independent intake surface while preserving its compatibility path. Evidence: planning_reflection_protocol.md is the exact redirect stub; Useful fields remain owned by the kernel or run reports; Inbound references use the consolidated intake route. Authority: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Fence: Keep the compatibility path and do not create another intake checklist (DOC-008 reflection-protocol fence). |
| A30 | DOC-008-STATUS | P4 Polish | READY [AGENT] | Perform the lead-authored PROJECT_STATUS compaction and verbatim history archival required by DOC-008 condition 8. | Lead compacts PROJECT_STATUS and preserves removed dated updates in the specified history archive. Evidence: Lead-authored PROJECT_STATUS has at most seven current sections; Removed dated updates are preserved verbatim in the history archive; Advisor-visible quantitative claims retain evidence pointers. Authority: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Fence: Lead authors final advisor-facing claims and no generator writes PROJECT_STATUS (DOC-008 PROJECT_STATUS authorship fence). |
| A31 | DOC-008-INTAKE | P4 Polish | READY [AGENT] | Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9. | Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: [DOC-008 intake and procedure reconciliation](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 intake reconciliation](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence). |
| A32 | DOC-008 | P4 Polish | PARTIAL; READY; GATES close: DOC-008-INTAKE; GATES close: DOC-008-REFLECTION; GATES close: DOC-008-STATUS [AGENT] | Close the reopened DOC-008 migration only after residual conditions 4, 6, 8, and 9 land and every original completion condition is rechecked. | Every original DOC-008 completion condition lands before the reopened task returns to complete. Evidence: All nine DOC-008 required outcomes rechecked; Focused and canonical suites pass; Final-head review confirms one work-selection authority. Authority: [DOC-008 state-kernel specification](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 required outcomes](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not redeclare DOC-008 complete until every original required outcome lands (DOC-008 required outcomes). Note: Reopened by WO-021; phase C repairs work-selection authority while three residual task records remain live. |
| A33 | P2-050 | P3 Hardening Candidates | READY [AGENT] | Adjudicate the C-028 dissent-record candidates separately: frozen-legacy claim_eligibility mapper, semantic cooldown-row verification, once-per-manifest first-run exemption, scoped top-up detection, and cooldown trace v2. | Each C-028 dissent-record candidate receives its own adjudication before any implementation. Evidence: Frozen-legacy claim_eligibility mapper receives its own adjudication; Semantic cooldown-row verification receives its own adjudication; Once-per-manifest first-run exemption receives its own adjudication; Scoped top-up detection and cooldown trace v2 receive their own adjudications. Authority: [C-028 dissent-record queue candidates](docs/run_reports/2026-07-11-c028-continuation.md). Acceptance: [P2-050 acceptance](docs/process/state_kernel.json). Fence: Do not implement any candidate before its own recorded adjudication (C-028 dissent-record queue candidates). |
| A34 | TOOL-01 | P3 Tooling | READY [AGENT] | Fix codex-run-v3 defects: resume-after-NEEDS_SCOPE no-op; preventive permission profiles; NEEDS_RULING recognition; effort-default passthrough; stream-death OK exits with thin out-files; resume --last cross-thread attachment through the global latest session; and session-open paths lacking per-path match specifiers. | All seven codex-run-v3 defects close in lead personal tooling with targeted regressions and updated adapter operations lessons. Evidence: Resume after NEEDS_SCOPE continues the requested work; Preventive permission profiles and NEEDS_RULING recognition are covered; Omitted effort defaults to xhigh instead of config passthrough; Upstream stream death fails instead of exiting OK with a thin out-file; Resume requires an explicit session ID and cannot cross-attach through a global --last pointer; Session-open accepts a per-path match specifier without post-hoc child expansion. Authority: [Bridge v1.1 wrapper and session operations record](docs/run_reports/2026-07-13-bridge-v11.md). Acceptance: [TOOL-01 acceptance](docs/process/state_kernel.json). Fence: Keep implementation in lead personal tooling; this repository owns only the work record (Bridge v1.1 wrapper and session operations record). Note: lead personal tooling, non-repo |
| A35 | AUD-FOLLOWUPS | P3 Hardening Candidates | READY [AGENT] | Close the ULTRA comparison audit's accepted small residue in one bounded agent task: WO-012's owned D-062 lint queue row, WO-014 realized-token discrimination, WO-017 default no-handoff regression, WO-020 standalone bridge-checker decision, and WO-040 authored-instruction absolute-path plus genuine pristine-clone coverage. | The ULTRA comparison audit's five accepted small follow-ups close with discriminating tests or an explicit recorded decision, without creating a ceremony-dispositions task. Evidence: WO-012's owned D-062 lint queue-row obligation is implemented and covered; WO-014 has a realized-token discriminating test; WO-017 has a default no-handoff regression assertion; WO-020 has a recorded standalone bridge-checker decision; WO-040 has authored-instruction absolute-path coverage plus a genuine pristine-clone test. Authority: [Comprehensive-audit close-out and accepted-residue list](docs/reviews/2026-07-13-comprehensive-audit/report.md). Acceptance: [AUD-FOLLOWUPS acceptance](docs/process/state_kernel.json). Fence: Do not create AUD-CEREMONY-DISPOSITIONS; ceremony dispositions remain report-owned (Comprehensive-audit report disposition ledger). Note: Accepted small residue only; audit ceremony dispositions remain in the report. |
| A36 | AUD-WO-033 | P3 Hardening Candidates | READY; GATES close: P2-006 [AGENT] | After 2M, split scripts/run_campaign.py along tested policy seams, pure validation and provenance first and execution lifecycle second, only when campaign-scale or split or multi-node work first forces edits to that path. | The post-2M campaign-runner refactor is behavior-preserving across the full campaign test portfolio and retains every collection and claim-readiness safeguard. Evidence: Pure validation and provenance seams are extracted before execution lifecycle seams; The full campaign behavior-parity portfolio is green before and after the split; Locks, waivers, backups, cooldown, and claim-readiness behavior remain unchanged. Authority: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Keep this post-2M and behavior-preserving; do not redesign campaigns or weaken locks, waivers, backups, cooldown, or claim-readiness gates (Comprehensive-audit register WO-033 non-goals and risk note). |
| A37 | AUD-WO-034 | P3 Hardening Candidates | READY; GATES close: PHASE-3-SPLIT-SCHEDULED [AGENT] | At Phase-3 split scheduling, assign bounded owners and dependencies for transfer-bench, split replay, composite validate and reduce, KV-economics reduction, and matrix-generator extension before any PLANNED command becomes executable. | When Phase-3 split work is scheduled, every PLANNED pack command gains an owner or explicit deferred marker without pack collapse or premature implementation. Evidence: Every PLANNED command has a bounded owner row or explicit deferred-design marker; Pack-command ownership lint passes positive and negative fixtures; Settled split pre-registration requirements and offline-before-live fences remain intact. Authority: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not prune draft designs, collapse campaign packs, or implement split or KV work in this ownership pass (Comprehensive-audit register WO-034 non-goals). |
| A38 | AUD-WO-035 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-TRANSFER-SCHEDULED [AGENT] | Before the first 2K-live or remote split-transfer task, define a versioned discriminated node-worker payload and test realistic typed rejection without overloading telemetry blocks. | The 2K-live and remote roadmap has a versioned transfer-task payload seam with typed rejection before split-transfer implementation. Evidence: A versioned discriminated payload path exists for transfer tasks; A realistic unsupported transfer request fails with a typed versioned error; Telemetry blocks are not overloaded with transfer semantics. Authority: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Define and reject the future transfer shape only; do not implement split execution or transfer benchmarking (Comprehensive-audit register WO-035 non-goals). Note: D-043 supersession closure falls due at landing: add the dated protocol-version supersession line identified by PA-2. |
| A39 | AUD-WO-036 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-CONCURRENCY-SCHEDULED [AGENT] | When 2K-live or remote retries or concurrency are introduced, add a pre-launch node and GPU ownership lease plus idempotent duplicate prepare and start behavior. | Retries or concurrent 2K-live and remote campaigns cannot double-own a node or GPU and duplicate delivery is idempotent. Evidence: Duplicate prepare and start delivery is idempotent; Node and GPU ownership is leased before launch; Concurrency coverage exercises the ownership and duplicate-delivery contract. Authority: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not run concurrent hardware campaigns or make live-correctness claims in this agent task (Comprehensive-audit register WO-036 non-goals). |
| A40 | AUD-WO-037 | P3 Hardening Candidates | READY; GATES live_promotion: 2K-LIVE-PROMOTION-SCHEDULED [AGENT] | Fold non-self-asserted promotion authority into the 2K-live P2-005 and NV-GATE-2 code-now path before live promotion: bind an implementation receipt to commit and protocol pins and derive per-bundle execution class from the transport path. | Before 2K live promotion, non-self-asserted implementation authority and transport-derived execution classification fail closed at claim admission. Evidence: Fixture, unknown, unpromoted-live, and promoted-live classifications are tested; Unknown and unpromoted NVIDIA bundles are refused at claim admission; Promotion receipt is commit and protocol bound and cannot be forged through config or metadata. Authority: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Land this before, never after, the first claim-bearing NVIDIA live promotion; do not execute NV-GATE-2 or de-provisionalize hardware results here (Comprehensive-audit register WO-037 non-goals). Note: D-043 supersession closure falls due at landing: add the dated D-057 governed-reason amendment identified by PA-2. |
| A41 | AUD-WO-038 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-MULTINODE-DECIDED [AGENT] | At the 2K-live or remote multi-node roadmap decision, choose one owned remote execution boundary, consolidate duplicated lifecycle evidence helpers, and remove only proven-unconsumed transport surface with compatibility disposition. | At the 2K-live or remote multi-node decision, one owned execution boundary replaces only proven duplication while node-worker safeguards and public compatibility remain intact. Evidence: Lifecycle parity covers node-worker, subprocess, SSH, interface, and controller failure paths; Every deleted surface has a bounded absence or deprecation-compatibility trace; node_worker remains self-contained with backend-specific timeout, identity, log, clock, and cleanup safeguards. Authority: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Re-baseline against WO-001 and WO-010, keep node_worker self-contained, and do not delete public transport methods on repository absence alone (Comprehensive-audit register WO-038 risk boundaries). Note: D-043 supersession closure falls due at landing: back-annotate the public adapter and transport contract as required by PA-2. |
| A42 | AUD-WO-039 | P3 Hardening Candidates | PARTIAL; READY; GATES close: SITE-CAPACITY-RIGHTSIZING-DECIDED [AGENT] | At the next explicit site-capacity or right-sizing decision after SITE-02, remove only proven-unused live payload fields and make any further page trim through a recorded retained-route and value-versus-bytes review. | The remaining site payload and right-sizing work removes only proven-unused live fields and any page removal follows an explicit value-versus-bytes retention review. Evidence: Packed-byte and request reduction is measured; Route and link checks pass and every removed page has a retention decision; Consumed views, deep links, source access, and provenance stamps remain intact. Authority: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Trim only live payload fields proven unused; preserve advisor-facing pages, navigation, source access, stable deep links, and provenance unless a per-page retention review says otherwise (Comprehensive-audit register WO-039 preservation boundary). Note: Partial page trim landed 2026-07-15 by redirecting the duplicative capsule task-queue mirror while preserving its routes; remaining payload work is open. D-043 supersession closure falls due at landing through the dated D-051 amendment identified by PA-2. |
| A43 | CUSTODY-HARDEN-01 | P2 Next Slice | READY [AGENT] | Custody hardening follow-on from the screen+budget gauntlet: reduce-layer label-trust removal (G2A), drift-bound seal authentication (A3-r2), dead no-freshness accommodation disposition, artifact_schema_invalid mislabel. | Close the PR #85 gauntlet's deferred custody-hardening seams: config-derived mockness reaches the reduce-layer barriers, the drift-bound seal stops being self-certifying, and two diagnostic nits are resolved. Evidence: Reduce-layer environment/CPU claim barriers derive mockness from the custody-bound config, with metadata/summary-label early returns removed; Drift-bound artifact corpus identities resolve against repo-registered or custody-bound bytes (seal no longer self-certifying); Dead pre-addendum no-freshness accommodation removed or pinned as intentional forward-compatibility; artifact_schema_invalid evidence-binding mislabel renamed or documented at emission site. Authority: [C-045 gauntlet deferrals (council log; detail in docs/run_reports/2026-07-24-screen-budget-gauntlet.md)](docs/council_log.md). Acceptance: [CUSTODY-HARDEN-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from PR #85 gauntlet deferrals; triangle-agreement enforcement (merged) already raises these seams to three-file forgery cost. |
| A46 | FLOOR-WORKLOAD-SIZING-01 | P1 Phase Gate | READY [AGENT] | Re-size the floor/science campaign workloads so measured effects clear the duration-independent attribution floor, and pilot the resulting effect-to-floor ratio before spending quiet-machine nights on ABBA collection at current sizes. | Anchor-attribution error is approximately duration-independent (~1 J regardless of phase size) while effects scale with workload, so lengthening prefill/decode raises effect-to-floor linearly at zero instrument cost. Evidence: Measured effect-to-floor ratio at candidate workload sizes, from a pilot rather than assumption; Re-sized configs for the remaining floor stages, with the sizing rationale recorded; Explicit decision on which queued stages are collected at which sizes. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-WORKLOAD-SIZING-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25; scope corrected same day after the quantitative replay. NOT a blocker on the ABBA roadmap: under the labelled-floor path the queued stages remain scientifically viable at current sizes (tens-of-percent effects on ~50 J clear a ~3 J floor plus claim-side bound). This is a MARGIN optimisation — attribution error is duration-independent while effects scale with workload, so longer prefill/decode buys effect-to-floor ratio for free. Pilot the ratio at candidate sizes before committing the remaining quiet-machine nights. |
| A47 | FLOOR-COMMONMODE-01 | P2 Next Slice | READY [AGENT] | Pre-register and evaluate a common-mode anchor estimator for ABBA blocks: sweep one shared fiducial shift across all four members, re-integrate measured curves, and add only genuinely per-bundle components adversarially. | The fiducial term is ~80% of the composed anchor bound (24.9 of ~31.1 ms, verified) and is literally the same artifact for all four members of a block; treating it as four independent adversarial draws is itself an unphysical modelling choice. Evidence: Block-timescale fiducial stationarity registered as a NAMED transfer assumption with its evidence; Estimator pre-registered before it touches claim-bearing data; The identical estimator applied to BOTH the calibration blocks and the consuming science contrast (a floor calibrated with cancellation the consumer does not get would understate false effects); Quantified gain on a5/a10 blocks versus the worst-case-sum default. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-COMMONMODE-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25. Quantified same day on a5 decode ABBA (10 complete blocks): implemented worst-case-sum half-width gives a 6.46 J comparative floor; a common-mode proxy gives 2.13 J, a 3x improvement — material, but still above that cell's 0.60 J point floor, so it does not by itself restore extraction under the current gate. Value is in tightening the labelled floor, not in avoiding the label. Fiducial share of the composed bound measured at 80-87%. |
| A48 | PHASE-SHARE-ESTIMAND-01 | P2 Next Slice | READY [AGENT] | Investigate the anti-correlated prefill/decode boundary error: energy a shift removes from one phase it adds to the other, so the phase-share estimand has ONE boundary nuisance parameter whose joint envelope is a curve, not a box. | Treating each phase's anchor envelope as an independent box double-spends the shared interior boundary and inflates uncertainty on exactly the split/share quantity the Splitwise replication needs. Evidence: Determined whether _corner_composed_anchor_shift_envelope treats the shared interior boundary independently; Joint envelope over the single boundary-position parameter derived by re-integration sweep (measured-curve arithmetic only); Quantified effect on the phase-asymmetry claim envelope versus the independent-box treatment. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [PHASE-SHARE-ESTIMAND-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from the attribution-limit adjudication. Potentially the largest single win available for Splitwise sizing, at no instrument cost. |
| A49 | MODULARITY-01 | P3 Hardening Candidates | READY [AGENT] | Close the campaign-authoring modularity gap surveyed 2026-07-29: parameterize the campaign generator over a campaign-spec artifact and replace code-side literal assertions (analysis-manifest condition pairs, calibration scopes, phase-metric list) with registry-declared hash-validated sets. | Close the campaign-authoring modularity gap: campaign-spec-driven generation and registry-declared closed sets make every experiment axis swappable by config, per Ed's modularity directive. Evidence: Campaign generator is a parameterized function over a campaign-spec artifact (model, N, size profiles, block pattern, suite ref, run-ID prefix); a model swap touches one spec file and MODEL_TAG/PLAN_ID/run-ID prefixes derive from it with no parallel literal edits; Analysis-side closed sets (condition pairs, calibration scopes, phase-metric list) are declared in hash-bound registry artifacts and validated against those declarations, replacing the code-side literals at analysis_manifest.py:29-30,542-549 and detection_floor.py:87,89-95; Recorded-but-deferred residue dispositioned or re-queued: powermetrics references outside the adapter boundary, external-dataset ingestion, chat-template/thinking-mode seam, ABBA arity welded into three sites. Authority: [2026-07-29 modularity survey (Ed directive + per-axis grades)](docs/run_reports/2026-07-29-modularity-survey.md). Acceptance: [MODULARITY-01 acceptance](docs/process/state_kernel.json). Fence: Modularity applies to the harness, never to frozen claim pins: ratified hard literals (six-decimal pre-registration floor pins, lead-verified digests) stay anti-modular on purpose and must not be parameterized. (D-078 provenance amendment + D-079 operative-floor pins (hard literals are lead-verified, never parameterized)). Note: Minted 2026-07-29 from Ed's modularity directive. Survey verdict: runtime/telemetry Protocol layer and content-addressed provenance spine are already modular; the gap is campaign authoring above the adapter and literal assertions below the reader. Practical payoff lands with the planned Qwen3 cross-generation follow-up. |
| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
| A51 | NODE-CUSTODY-DEFAULT-01 | P3 Hardening Candidates | READY [AGENT] | Decide and implement whether the production DEFAULT_RETENTION_ROOT should be process/instance-unique: it currently is a fixed shared temp path (a latent collision hazard for genuinely concurrent clients), but making it unique conflicts with next-session custody reclamation. Resolve the tradeoff or record it as accepted. | Harden the production DEFAULT_RETENTION_ROOT against concurrent-client collision while preserving next-session custody reclamation (the NEEDS_RULING tradeoff deferred from NVIDIA-RETENTION-FLAKE-01). Evidence: The production DEFAULT_RETENTION_ROOT no longer collides for genuinely concurrent NodeClients sharing a scope, without breaking next-session custody reclamation (a later process must still locate the manifest it is entitled to reclaim); A regression proves two default-constructed clients in one process do not clobber each other AND that the documented reclamation contract still resolves the correct manifest across process boundaries; No retention/custody assertion is weakened; only root selection changes. Authority: [NVIDIA-RETENTION-FLAKE-01 fix report F1/F3 (PR #97): unique default roots close concurrent collision but conflict with next-session reclamation](docs/run_reports/2026-08-03-desk-session.md). Acceptance: [NODE-CUSTODY-DEFAULT-01 acceptance](docs/process/state_kernel.json). Fence: Isolation-only: do not weaken any retention/custody assertion; the reclamation contract's cross-process manifest resolution must survive any default-root change (NVIDIA-RETENTION-FLAKE-01 test-side fix (PR #97) already closed the flake). Note: Deferred 2026-08-03 from NVIDIA-RETENTION-FLAKE-01 (PR #97 closed the test-side flake); the production hardening is a NEEDS_RULING tradeoff, non-blocking (no current concurrent-client scenario). |
| A52 | D080-TRIGGER-01 | P3 Hardening Candidates | BLOCKED — D-080-amendment (Ed ratifies the trigger cadence and the runner (cron routine vs manual)) [AGENT] | Wire D-080's standing fresh-eyes sweep to a REAL trigger (calendar cron or every-N-merged-PRs), run as a separate concurrent read-only instance per the Ed-validated 2026-08-03 pattern, findings delivered mid-flight; reconcile D-080 clause 4(ii)'s stale zero-unique-catch citation. | The fresh-eyes sweep fires without anyone remembering it, on a ratified cadence, as a concurrent read-only instance. Evidence: A ratified trigger exists (cron routine or PR-count hook) and has fired at least once; D-080 clause 4(ii)'s stale citation is reconciled by amendment. Authority: [D-080 + the 2026-08-03 sweep finding (never fired) + Ed's concurrent-audit validation](docs/decision_log.md). Acceptance: [D080-TRIGGER-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-03: minted from the two-week soundness sweep's finding that D-080 has never fired, plus Ed's validated concurrent-audit pattern (memory: concurrent-fable-audit-pattern). Non-blocking hardening. |
| A53 | CGV-HARDEN-01 | P3 Hardening Candidates | READY [AGENT] | Harden runner-owned receipt persistence after validator --receipt-out removal: use a dirfd-relative receipt write that closes receipt-write TOCTOU and supplies fsync plus directory-sync atomicity. | The convening runner durably persists validator receipts through a dirfd-relative, crash-atomic, fsync-complete write path. Evidence: The convening runner persists the validator receipt with a dirfd-relative write that closes the receipt-write TOCTOU; Receipt publication is atomic and includes file fsync plus parent-directory sync; Regression tests distinguish path replacement, durability failure, and successful atomic publication. Authority: [2026-08-05 COLDGATE-VALIDATOR F3 consult Q2 receipt-persistence disposition](docs/process_traces/2026-08-05-cgv-f3-consult/SYNTHESIS.md). Acceptance: [CGV-HARDEN-01 acceptance](docs/process/state_kernel.json). Fence: Keep this row a sibling of COLDGATE-HANDOFF-01 and never merge them: durable receipt storage and validated-byte judge handoff have different contracts, tests, and failure consequences (2026-08-05 F3 consult Q2 dissent). Note: 2026-08-05: runner-scoped because PR #103 removed the validator's --receipt-out; deliberately registered as a sibling of, never folded into, COLDGATE-HANDOFF-01. |

## Active Global Work-Selection Gates

NONE — no global work-selection gate is active.

### [ED-EXTERNAL] lane

| Rank | ID | Priority | Queue state | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| E1 | P1-008 | P1 Phase Gate | READY | Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability). | Colloquium/report dates plus borrow window in docs/milestones.md; phase targets derived; acceptance-bar notes beside the P1-001 scope notes. Evidence: Dates + borrow window in docs/milestones.md; Derived phase targets; Acceptance-bar notes beside P1-001 scope notes. Authority: [Milestones + R-012](docs/milestones.md). Acceptance: [P1-008 acceptance](docs/process/state_kernel.json). Note: R-012 is the biggest active management risk for an undergrad timeline. |
| E2 | P2-027 | P2 Next Slice | READY | Publish a privacy-transformed, integrity-verified three-bundle pack from a clean tagged commit and obtain one documented external re-reduction by an uninvolved party. | Published pack plus a documented external re-reduction; until then the auditability claim stays L0-scoped. Evidence: Published pack; Documented external re-reduction. Authority: [C-020 + C-027 NEG-9](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-027 acceptance](docs/process/state_kernel.json). Note: Environment locks, pack preparation, integrity tooling, and fail-closed privacy transformation are merged; publication and external re-reduction remain ED-EXTERNAL. |
| E3 | P1-001 | P1 Phase Gate | READY | Capture supervisor approval and scope notes. | Dated notes in the Phase 1 exit checklist; unblocks full D-016 closure (P2-004). Evidence: Dated notes in docs/phase_1/phase_1_exit_checklist.md. Authority: [R-001](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: User-deferred 2026-07-06; R-001 mitigation holds: all work stays harness-shaped. |
| E4 | P1-003 | P1 Phase Gate | READY | Record the wall-meter decision: meter make/model or unavailable verdict plus measurement/export method. | Exit-checklist wall-meter section filled; informs D-018 boundary calibration. Evidence: Wall-meter section of the Phase 1 exit checklist filled. Authority: [D-018/C-003](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Elevated value: gates Q6 boundary sensitivity (C-003). |
| E5 | P1-004 | P1 Phase Gate | READY | Fill the network/interconnect topology plan: physical topology, link-speed paths, throughput method. | Network section of the Phase 1 exit checklist recorded. Evidence: Network section of the Phase 1 exit checklist recorded. Authority: [R-011](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Partial. |
| E6 | P1-006 | P1 Phase Gate | READY | Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L). | Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: [Remote gate / NV-GATE-2](docs/phase_2/hardware_slice_implementation_guide.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). |

### [QUIET-MAC] lane

| Rank | ID | Priority | Queue state | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| Q1 | MET-WINDOW-C-01 | P1 Phase Gate | BLOCKED — FROZEN-PLAN-READINESS-RECORD (A reviewed FROZEN-PLAN READINESS RECORD exists before any collection night: frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight, launcher-verified), ED-5A (Ed section-5A window prep FRESH POST-MOVE (the 2026-08-02 laptop move invalidated settled-machine conditions; network time off, AC, settled machine, walk-away)) | Execute a reviewed fresh-claim collection plan beginning with Window C: no Window B member enters a replacement claim basis; split prospectively across windows C and D if the complete replacement cannot fit the 2-4 hour envelope with at least 20 percent failure margin. | The fresh-claim metrology plan replaces every still-desired Window-B claim component without using any Window-B member, under reviewed frozen-plan and validated-window controls. Evidence: A fresh-claim plan recollects every still-desired Window-B claim component beginning with Window C; no Window B member enters a replacement claim basis; The fresh plan includes the still-required C2, C4, and C5 collection scope under the frozen-plan discipline, split prospectively across windows C and D if one window cannot retain at least 20 percent failure margin inside the runbook's 2-4 hour envelope; Window operated under the validated protocols: bird-SIGSTOP with identity custody, guarded launcher, one-line arm messages with zero output streaming during idle-gate exposure, third-failure salvage rule; Whole-window verdict emitted by machinery that has passed MET-VERDICT-ADJ-01 adjudication; supersessions recorded once, pre-verdict; both roots backed up rc=0. Authority: [D-113 clauses 7-9 fresh-claim reset, readiness fence, and prospective C/D split](docs/decision_log.md). Acceptance: [MET-WINDOW-C-01 acceptance](docs/process/state_kernel.json). Fence: A window-C dangler seeking the b-ii mechanical license before D100-BII-BINDING-01 closes RETURNS TO THE GATE; the window itself may run (D-106 revisit clause). Fence: Before any collection night, the ordinary launcher verifies a reviewed FROZEN-PLAN READINESS RECORD binding the frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight (D-113 clauses 8-9 hard start fence). Fence: Plan root assembled and frozen before measurement; no plan edits after freeze (D-096 frozen-plan ratification). Fence: Zero agents AND zero operator output streaming during measurement idle gates; arm messages are one line; bird-SIGSTOP protocol with identity custody and fail-safe CONT trap on all exit paths (2026-08-01 run report: streaming-during-idle-gate hazard + bird-SIGSTOP protocol). Note: D-113 clauses 7 and 9: the former remainder-only scope is SUPERSEDED. A fresh-claim plan is required; no Window B member enters a replacement claim basis. If the full replacement exceeds the runbook's 2-4 hour envelope with at least 20 percent margin, split it prospectively across windows C and D. |
| Q2 | P2-006 | P2 Next Slice | READY | Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison. | Strict-valid reducer-0.5.2/0.6.2 campaign bundles with counterbalanced order and drift sentinels; interpretation uses campaign claim_readiness plus the merged fail-closed analysis engine. Evidence: Strict-valid campaign bundles under the fixed validator; Counterbalanced order manifest + drift sentinel positions recorded; baseline_results.md with variance + prefill/decode comparison. Authority: [Phase 2 plan + analysis plans](docs/phase_2/phase_2_plan.md). Acceptance: [Phase 2 exit checklist](docs/phase_2/phase_2_exit_checklist.md). Note: Software interpretation gates are satisfied; Window-A floors landed 2026-07-31 (mint #1 mainline), so only the campaign remains. |
| Q3 | P2-010 | P2 Next Slice | READY | P2-010b remainder: affine smoke campaign execution (B=5) plus envelope-gate verdict on its bundles, on a quiet-window tail. | joulewise envelope-gate emits the D-036 verdict from strict-valid smoke bundles; campaign acceptance in AP-5. Evidence: D-036 verdict from strict-valid smoke bundles; AP-5 campaign acceptance met. Authority: [AP-5 + affine stream log](docs/contracts/analysis_plans.md). Acceptance: [P2-010 acceptance](docs/process/state_kernel.json). Note: Envelope-gate script merged 2026-07-09 (PR #23); only the campaign remains. |
| Q4 | P2-019 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) | q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6). | Grid campaign lands per AP-1; top-up near-floor cells before L3 wording. Evidence: AP-1 grid campaign bundles; Holdout cells honored; 8192 anchor cells on small+mid models. Authority: [AP-1](docs/contracts/analysis_plans.md). Acceptance: [P2-019 acceptance](docs/process/state_kernel.json). |
| Q5 | P2-020 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) | Content-sensitivity sentinel campaign (Window B, AP-6): five equal-shape ids-native conditions, n sized from Window A; request-energy deltas and MDE verdicts. | Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046). Evidence: Five equal-shape ids-native conditions; Request-energy deltas + MDE verdicts. Authority: [AP-6 + D-046](docs/contracts/analysis_plans.md). Acceptance: [P2-020 acceptance](docs/process/state_kernel.json). Note: Generator merged (PR #19), manifests ready (PR #26); a tiny AP-6 pilot may ride a Window-A tail (CP-6). |
| Q6 | P2-012 | P2 Next Slice | BLOCKED — P2-006 (identification-core runs after Window A) | Identification-core campaign (jw_mixed) after Window A; natural-EOS pilot plus full panels in later phases. | Campaign bundles strict-valid per AP-4; no category claims outside matched strata. Evidence: Strict-valid bundles per AP-4; No category claims outside matched strata. Authority: [AP-4 + D-039/D-040](docs/contracts/analysis_plans.md). Acceptance: [P2-012 acceptance](docs/process/state_kernel.json). Note: Manifests generated + regenerated (PR #26); runner/runtime/validator hash guards merged (PRs #24/#27). |
| Q8 | P2-046B | P1 Phase Gate | READY | Execute the frozen load-transition alignment harness on the real Mac and adjudicate the production interval-support bound from offset and residual artifacts. | Real-Mac counterbalanced transitions validate or widen the P2-038 conservative interval-support bound; physical evidence replaces the PROVISIONAL Part-A verdict. Evidence: Counterbalanced real-Mac transition artifacts; Offset, residual, and conservative-bound verdict; P2-038 bound cited or amended. Authority: [Hardening adjudication C6](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-046B acceptance](docs/process/state_kernel.json). Fence: Do not promote Part-A fixture evidence or retain PROVISIONAL interval support after a conflicting physical verdict (Hardening adjudication C6). Note: Part A merged in PR #50; Part B is quiet-machine physical execution. |
| Q9 | P2-047B | P2 Next Slice | BLOCKED — P2-047A (frozen controller-overhead harness exists) | Run the frozen controller capture-overhead ABBA on the quiet Mac and record the floor-governed overhead verdict. | Real floor-governed ABBA execution yields a named overhead verdict with instrumented-stack scope unless a separate subtraction model is justified. Evidence: Floor-governed quiet-Mac ABBA bundles; Named overhead verdict; Instrumented-stack scope or separately justified model. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047B acceptance](docs/process/state_kernel.json). |

### [AGENT] lane

| Rank | ID | Priority | Queue state | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| A0 | P2-035 | P3 Research Expansion | READY | RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests). | Promotion decided per registry rules; harness gaps closed before promotion. Evidence: Registry promotion record per docs/research_question_bank.md rules; G-RQVAR-* harness gaps implemented with tests. Authority: [RQ-ENERGY-VARIANCE candidate design](docs/specs/rq_energy_variance_design.md). Acceptance: [P2-035 acceptance](docs/process/state_kernel.json). Fence: C-004 quarantine binds; no promotion before floors exist (C-004 quarantine). |
| A2 | QUIET-GUARD-01 | P1 Phase Gate | READY; GATES live_promotion: T3-CHAR-PAIR-01 | Quiet-guard work order (full gauntlet): host-wide quiet lease, refuse-at-arm, characterized resident watcher; plus Ed requirements recorded 2026-08-03 — t3-armed operation (a t3-launched claude session arms a detached guarded chain, then self-quits and quits t3 with a survivor inventory), t3-relaunch-on-close, and README-banner signaling. | The quiet guard lands through the full C-028 gauntlet with the host-wide lease, refuse-at-arm, characterized resident watcher, and all three Ed-required t3 behaviors working end to end. Evidence: Commit 1 only: host-wide quiet lease implemented and enforced; Refuse-at-arm: arming refuses when the host is not quiet (usable by the ordinary guarded-shell window launcher); Installed-INACTIVE: no arming path, no production lease, live_promotion=false; Seven focused-audit blockers closed (priv-esc interpreter, validate/install TOCTOU, arbitrary-root initializer, macOS process identity, boot/hostname wedge, decision entry, independently-pinned tests); Full gauntlet on the landed commit: independent audit + delta re-audit of every fix round. Authority: [Ed directive 2026-08-03 ~23:55 (t3-drive chain is the critical path; non-in-flight work paused) + t3-doctrine gate synthesis + synthesis-exhibits SX5](docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md). Acceptance: [QUIET-GUARD-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-05: DESCOPED by Ed's directive (t3 control-plane build-out not worth its cost; t3 stays the INTERACTIVE control plane, t3-resident-during-windows dropped; windows return to the zero-agent guarded-shell path). ROW RE-SCOPED TO COMMIT 1 ONLY: the host-wide quiet lease + process census, installed-INACTIVE. Retained because it has non-t3 value — mechanical refuse-at-arm for the ordinary guarded window launcher, replacing procedural eyeballing. SHELVED: commit 2 (launcher interception), commit 3 (t3 handoff + resident watcher), commit 4 (t3-relaunch + README banner projection + all credential handling). In flight at checkpoint: Sol fix round closing 7 audit blockers; work UNCOMMITTED in scratchpad/quietguard (branch impl/quiet-guard); harvest scratchpad/qg-fix-out.md. |
| A3 | FLOOR-BIND-01 | P1 Phase Gate | READY | Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions. | Floor/MDE artifacts stop being self-attesting: claim consumption authenticates admissible widths and complete governed campaign membership against extraction evidence, retiring registered limitation L1. Evidence: Canonical floor cells bound to their extraction report and source-member disposition (or extraction gates and widths rederived at binding); Binding refuses on any stored width/corner mismatch or campaign-membership deviation; Integration regressions reject width substitution and member omission end-to-end. Authority: [D-078 clause 8 (confirmation round 9, registered limitation L1)](docs/decision_log.md). Acceptance: [FLOOR-BIND-01 acceptance](docs/process/state_kernel.json). Fence: Until this row closes, claim-bearing analysis may consume floor artifacts only from same-custody-session governed extraction; standalone artifacts are non-claim-bearing (D-078 clause 8 L1). Note: Minted 2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1 workflow rule mitigates until closed. |
| A4 | AXI-SB-ADAPTER | P2 Next Slice | READY | Implement the static-batch Mac adapter follow-on minted by the AXI-SB supported verdict: batch_size configuration knob, per-sequence request-scoped token events per the AXI-SA contract, realized-vs-configured batch recording, and structured memory-fit outcomes, with strict-valid mock or smoke bundles and no energy claims. | The follow-on static-batch adapter turns the AXI-SB supported verdict into an instrumented batch_size-configurable Mac runtime path emitting per-sequence AXI-SA events, with memory-fit failures structured and zero claim or quiet-Mac consumption. Evidence: A batch-capable Mac adapter exposes a batch_size configuration knob and emits per-sequence request-scoped token events conforming to the landed AXI-SA event contract, validated by strict bundle validation on a mock or live smoke bundle; Realized batch size is recorded alongside configured batch size, and structured memory-fit failures are captured as data rather than crashes; No energy claim, campaign scheduling, or quiet-Mac consumption occurs in this row; AP-BATCH execution remains separately floor-gated per AXI-SE. Authority: [AXI-SB verdict document (supported; mint-on-supported follow-on)](docs/specs/axi/sb_static_batch_verdict.md). Acceptance: [AXI-SB-ADAPTER acceptance](docs/process/state_kernel.json). Fence: Build on the verified BatchGenerator path with per-request observability; a Python loop over singleton calls is not a batch adapter (AXI-SB verdict document classification and scope). Fence: Keep continuous batching deferred and do not infer coalescing, scheduler-optimum, or offered-load claims from static-batch work (D-070 static-batch scope). Fence: Window A retains every quiet-Mac measurement slot; adapter implementation and mock or smoke validation are agent-lane work and consume no quiet-Mac campaign time (D-070 Window A ownership). |
| A5 | TEST-SPEED-01 | P2 Next Slice | READY | Cut suite wall-clock (three Ed-ratified levers, 2026-08-03): collect per-module timing data with the recovered profiling scripts, implement the shard-runner and the PR-fast/full tier split from the data, and evaluate Blacksmith runners. | The three Ed-ratified levers land: timing data drives a shard-runner plus PR-fast/full split with the full suite still holding every authoritative gate, and the Blacksmith runner option is evaluated on evidence. Evidence: Per-module timing corpus collected on a quiet bench (the recovered Sol profiling scripts; timings.jsonl + summary.json banked under .desk/) identifying the slow tail by module and by test; Shard-runner and the ratified PR-fast/full tier split implemented from the data: the fast tier gates PRs, the FULL suite remains the gate for merges, verdicts, and audited heads; zero test deletions; Blacksmith runner evaluation recorded with an adopt/defer recommendation and measured latency/cost comparison against GitHub-hosted runners. Authority: [Ed ratification 2026-08-03 (three levers: suite-speed priority, PR-fast/full split, Blacksmith runner evaluation); origin row in the 2026-07-28 report](docs/run_reports/2026-07-28-floor-mint-implementation.md). Acceptance: [TEST-SPEED-01 acceptance](docs/process/state_kernel.json). Fence: No test deletions, and the fast tier never substitutes for a required full-suite gate: merges, whole-window verdicts, and audited heads keep the full suite (D-061 zero-deletion clearance; the full suite as the authoritative gate). Note: 2026-08-03: timing DATA collected (quiet bench, 93 modules, 695s serial; raw in .desk/test-speed-consult/timings-20260803.jsonl) and DESIGN done (.desk/test-speed-consult/DESIGN-from-timing-data.md). Findings: suite is a 2-module problem (run_campaign 182s + p2038 133s = 45%); module-atomic sharding CAPS at 182s so those two must be split by TestCase class; shard-runner + splits -> ~87s wall @8 workers (6.5x); fast tier (drop 11 heavy integ modules) -> 25-40s PR feedback with the full suite still the merge gate. Blacksmith (lever 3) NEEDS ED (account/cost; likely marginal once sharded). Implementation queued: scripts/shard_tests.py + class-split + CI matrix — mechanical, delegatable, zero deletions (D-061). 2026-08-04: PHASE 1 LANDED — PR #98 MERGED (9b02539): module-atomic shard-runner + 8-way CI shard matrix, main CI green under it (~15min -> ~6min proven); worktree/branch pruned. Remaining scope: class-split of the two heavy modules (Phase 2), fast PR tier (lever 2), Blacksmith runners (lever 3, NEEDS ED). |
| A6 | AXI-SD | P2 Next Slice | READY | Prepare the matched dense/MoE pair proposal with the consult's pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT. | A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016's cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: [AXI handoff work program S-D](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SD acceptance](docs/process/state_kernel.json). Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership). |
| A7 | AXI-SE | P2 Next Slice | READY | Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult's floor and ownership closures. | The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A's gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: [AXI handoff work program S-E](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SE acceptance](docs/process/state_kernel.json). Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership). |
| A10 | SUPERSESSION-DUP-REFUSAL-01 | P1 Phase Gate | READY | Rule on and then implement write-time refusal in the supersession recorder, which today appends silent duplicate records when run more than once for a member and voids campaign membership downstream; the ruling is the first half of the deliverable. | A repeat recorder invocation for the same member refuses instead of appending a duplicate record. Evidence: The write-time refusal ruling is recorded in the decision log before any implementation; A regression asserts that a second recorder invocation for the same member refuses. Authority: [D-086 supersession-aware cooldown-evidence join (recorder duplicate-append defect)](docs/decision_log.md). Acceptance: [SUPERSESSION-DUP-REFUSAL-01 acceptance](docs/process/state_kernel.json). Fence: Until the refusal lands, run the supersession recorder exactly once per member (D-086 operator mitigation). Note: Minted 2026-07-30 from the D-086 arc; ruling-first, no implementation before it. |
| A11 | T3-PROV-SCHEMA-01 | P2 Next Slice | READY | Implement the tracked four-axis provenance record with authority_class and the ingestion-event schema, then make reverse-consult admission consume authoritative launch-route and owner_kind evidence so bridge §8's transitional convention ends. | The four-axis provenance plus ingestion-event schema ends bridge §8's transitional convention by mechanically enforcing reverse-consult eligibility from authoritative route and ownership evidence. Evidence: A tracked provenance record represents the four axes control_plane, transport, authority_class, and governance, with authority_class explicit; A tracked ingestion-event schema binds native session identity, output digest, lead disposition, and tracked process-trace location; Reverse-consult admission consumes authoritative launch-route and owner_kind evidence rather than self-reported headers; Rejection regressions fail closed on delegated, unknown, or contradictory provenance and prove that merely persisting the schema cannot end the transition. Authority: [Bridge protocol §8 transitional reverse-consult enforcement follow-on](docs/contracts/bridge_protocol.md). Acceptance: [T3-PROV-SCHEMA-01 acceptance](docs/process/state_kernel.json). Fence: The transition ends only when admission consumes authoritative launch-route and owner_kind evidence with rejection tests; defining or persisting the schema alone is insufficient (Bridge protocol §8 fail-closed transition rule). Note: Bridge §8 currently validates only self-reported headers; consumption-side fail-closed is the actual protection until this row supplies real enforcement. |
| A12 | MINT-GENERALIZE-01 | P1 Phase Gate | BLOCKED — D-110 (The remaining D-110 re-mint conditions hold before ANY further mint, including the governed 7B mint: (b) the acceptance artifact is ISSUED after verified R2 backfill and deterministic ledger bootstrap; (c) the evidence_root_id validator pin is widened) | Generalize the mint beyond the mint-1 pair: scripts/mint_floor_artifact.py is hard-pinned to the p2_015, a10, and window-C evidence (cell id, plan sha, both order-manifest ids, the two member counts, the expected operative-floor text), so build a sibling taking those pins per plan and carrying the 7B mint's remaining scope. | A generalized mint sibling takes the mint-1 hard pins per plan so a second floor artifact can be minted without weakening the pre-registration gate. Evidence: A 7B decode-floor artifact mints from qwen25_7b_decode_floor_v1 evidence with its own hard six-decimal operative-floor literal supplied per plan, never derived inside the mint path; The pre-registration gate passes as-embedded and validate_floor_artifact returns no findings; The generalized path mints byte-identical to the reviewed core from the same inputs on the same integration tree (core-vs-wrapper parity per D-109 addendum II; NOT a match against historical mint-1 digests, which D-110's corrected re-mint may legitimately change). Authority: [splitwise_decode_v1 campaign doc section 2 Blocker A (mint pins); D-082, D-084, D-085 Q6](docs/phase_2/splitwise_decode_campaign.md). Acceptance: [MINT-GENERALIZE-01 acceptance](docs/process/state_kernel.json). Fence: Generalize the plumbing, never the pins: six-decimal floor literals and lead-verified digests stay supplied per plan and hard-checked in-tool (D-082 and D-084 operative-floor pins). Note: 2026-08-03: D-110 (sweep finding RT-1/RT-2): mint #1 is retroactively NON-CLAIM-BEARING (taint-and-remint); the night consult's conditional 7B-mint license is SUSPENDED. The mint-1 byte-compare replay completed BYTE-IDENTICAL at pinned 3de370ec (all four digests; docs/process_traces/2026-08-03-q1-remint-bytecompare/). 2026-08-05: condition (a) is satisfied by merged PR #100. Condition (b) preparation is complete and its verification blocker is resolved: the B1 disposition is lead-ruled 30/2/6 and deterministic bootstrap is implemented on impl/ledger-bootstrap, under audit. Condition (c) is in flight on impl/validator-rootpins. The row remains hard-blocked on the still-pending D-110 (b)+(c) completion gate. |
| A13 | CODEX-BRIDGE-SANDBOX-01 | P2 Next Slice | READY | Correct scripts/codex-bridge review-mode sandbox enforcement: pass the read-only sandbox flag instead of launching workspace-write while recording read-only metadata. | codex-bridge review launches read-only exactly as its audit manifest claims, with regression coverage binding recorded and effective sandbox values. Evidence: scripts/codex-bridge review passes the read-only sandbox flag to every non-app review launch; The review audit manifest records the sandbox actually supplied to the launch; A regression proves the recorded review sandbox and launched sandbox are both read-only and cannot drift apart. Authority: [2026-08-05 live inspection: review records observer_sandbox=read-only but the non-app launch omits -s read-only](scripts/codex-bridge). Acceptance: [CODEX-BRIDGE-SANDBOX-01 acceptance](docs/process/state_kernel.json). Note: Caught live 2026-08-05: observer_sandbox is set to read-only, but the non-app review invocation omits the sandbox flag, so audit metadata misstates enforcement. |
| A14 | COLDGATE-HANDOFF-01 | P2 Next Slice | READY | Build runner-owned sealed-byte judge handoff: capture immutable in-process packet, charter, and exhibit byte snapshots; compute digests over those exact buffers; construct judge input from the same buffers; and specify and test transport byte-to-request binding. | The convening runner delivers exactly the bytes the validator observed, with immutable snapshot-to-judge transport binding and a judge-identity-bound runner receipt. Evidence: Deterministic post-hash path replacement delivers the original immutable snapshot or refuses without invoking the judge; Same-inode mutation through a second descriptor never delivers mutated bytes under the old receipt; Judge-received payload hashes equal the receipt hashes and the runner receipt binds the judge request or session identity. Authority: [2026-08-05 COLDGATE-VALIDATOR F3 consult Q2 handoff ruling and tests](docs/process_traces/2026-08-05-cgv-f3-consult/CONSULT-REPORT.md). Acceptance: [COLDGATE-HANDOFF-01 acceptance](docs/process/state_kernel.json). Fence: Until this row lands, no validator PASS may be used to convene a cold judge (2026-08-05 F3 consult standing operational constraint). Note: Design warnings: holding file descriptors open does NOT seal bytes because a second descriptor can mutate the same inode; path-based launch-time revalidation alone leaves a revalidate-to-read race. Pending-ratification payload carried by this row: the proposed amendment to docs/process/coldgate_charter_registry.md separating validator observation from runner custody. The registry is Ed-ratified and is NOT edited by this or any session without a cold-gate/Ed ratification. |
| A15 | C3-RECOGNIZER-EXACT-01 | P1 Phase Gate | READY | Close the two D-105-registered recognizer-exactness blockers: exact escape-ordering completion-feasibility (F1) and the documented decidable superset number grammar (F2, with the D-104 cl.2 subset-direction amendment), plus the bundled F3/N2 release-path hygiene if not already landed. | The two registered recognizer-exactness blockers (escaped-key ordering; number-prefix over-acceptance) close together under D-105's refuter-amended criteria with an independent audit. Evidence: F1 closes via the exact escape-ordering completion-feasibility procedure (hex-digit interval derivation, surrogate-pair arithmetic, prefix-extension rule) with both registered counterexamples pinned verbatim and a BMP/non-BMP boundary property test; F2 closes via a DOCUMENTED DECIDABLE SUPERSET grammar of json.dumps float spellings (fixed-notation exponent window, coefficient rules, two-digit exponent padding) — the D-104 cl.2 subset direction is amended per D-105 to 'accepted within the documented superset AND containing every real writer prefix'; both counterexamples refuse; randomized-float completeness property passes; Both registered blockers close together with an independent delta audit at the exact head; the acceptance-set contract re-proven in both amended directions over a corpus including non-BMP keys. Authority: [D-105 disposition synthesis (F1/F2 registered as a NEW ruling, not D-088 precedent; closure criteria refuter-amended; number-grammar exactness struck)](docs/decision_log.md). Acceptance: [C3-RECOGNIZER-EXACT-01 acceptance](docs/process/state_kernel.json). Fence: F1/F2 severity may not be downgraded by any role; closure ONLY through this row; while open the recognizer's accepted set may only SHRINK; the custody sidecar and writer-side ASCII key assertion (the D-105 micro-commit) are load-bearing compensating controls and may not be weakened (D-105 registration fences). Fence: This registration must not be cited as precedent for registering corpus-absent defects generally; it is a new ruling made with three recorded independent absence scans and mechanical compensating controls (D-105: branch-introduced registration is NOT QA-10A/B precedent). |
| A16 | P3-000 | P3 Research Expansion | BLOCKED — R-003 (user approves the 3.0.2 installs (R-003)) | KV persistence feasibility spikes (Phase 3 Stage 3.0): 3.0.2+ open; 3.0.2 needs installs and inherits the 3.0.1 harness shape plus its two deferred hardening fixes (ledger C-8). | Verdicts recorded in docs/phase_3/kv_feasibility.md; checklist rows are the status authority; must complete before any borrow-window scheduling. Evidence: Verdicts in docs/phase_3/kv_feasibility.md; Checklist rows updated. Authority: [D-035/D-036](docs/decision_log.md). Acceptance: [Phase 3 exit checklist](docs/phase_3/phase_3_exit_checklist.md). Note: 3.0.1 complete and merged (PR #9, replay_supported). |
| A17 | P2-022 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)) | Marker-shim energy-layer feasibility spike: verdict-shaped export path only (external_markers_supported / partial / external_markers_unsupported). | 3+ marked items, external result artifact hashed, strict bundle valid; verdict recorded. Evidence: 3+ marked items; External result artifact hashed; Strict bundle valid. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [Adapter contract](docs/contracts/adapter_contracts.md). Fence: Energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim (D-041). Note: C-027: the C-026 revisit-after-Window-A note is a revisit of sequencing, not permission. |
| A18 | P2-023 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)), P2-022 (P2-022 verdict recorded) | HumanEval import smoke: benchmark_import manifest plus suite profile plumbing goal; freeze subset with C-005 discipline, MIT license/provenance fields, 256/512-token completion policy. | Frozen subset with license/provenance fields lands; no pass@k/accuracy/capability claim. Evidence: Frozen subset manifest with C-005 discipline; License/provenance fields present. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [RQ bank import-smoke design](docs/research_question_bank.md). Fence: No pass@k, accuracy, or capability claim (D-041). |
| A19 | P2-024 | P2 Next Slice | BLOCKED — P2-006 (2M reductions identify floor/MDE headroom) | Cheap-campaign shortlist: select among C5-1.6 sampler ABBA, C5-1.12 quant decomposition, C5-1.8 runtime attribution per measured floors; the selected campaign is then queued [QUIET-MAC]. | Explicit selection recorded after floors; selection cites floor/MDE headroom. Evidence: Selection recorded with floor/MDE headroom rationale; Selected campaign queued as a quiet_mac task. Authority: [C-015 + RQ bank](docs/research_question_bank.md). Acceptance: [P2-024 acceptance](docs/process/state_kernel.json). |
| A21 | P3-001b | P3 Research Expansion | BLOCKED — P2-006 (2M affine coefficients exist) | Seed the split analysis-plan row: pre-registered compositional predictions per pairing/link (including named same-boundary headline and at least one predicted-crossover cell if feasible), per-cell transfer-boundary labels (D-049). | AP row committed before any split hardware run; phase_3_plan amendment line landed. Evidence: AP row committed pre-split-hardware; phase_3_plan amendment line landed. Authority: [D-048/D-049](docs/decision_log.md). Acceptance: [Analysis plans (split row)](docs/contracts/analysis_plans.md). |
| A22 | P2-004 | P2 Next Slice | PARTIAL; READY; GATES close: P1-001 | Close model selection (D-016): decision-log entry with models, revisions, artifact paths, local mirror, fallback candidate; mid-model pick, CUDA load, GGUF paths outstanding. | Decision-log entry complete; full closure gated on P1-001. Evidence: Decision-log entry: models, revisions, artifact paths, mirror, fallback. Authority: [D-016](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Provisional small-model pick 2026-07-06 opens 2G. |
| A23 | P2-005 | P2 Next Slice | PARTIAL; READY; GATES live_promotion: P1-006 | Remote targets (2K NVIDIA/vLLM/ssh and 2L Orin): fixture-first and NV-GATE-2 code-now hardening are merged; protocol pins remain provisional until the external live-promotion rows execute. | Live 2K/2L evidence or a documented access blocker; applicability table updated; NV-GATE-2 live rows close without promoting fixture evidence. Evidence: Remote bundle or documented access blocker; Applicability table updated; NV-GATE-2 items closed at live promotion. Authority: [NV-GATE-2 live-promotion spec](docs/specs/c027/nv-gate-2_live_promotion.md). Acceptance: [2K live verification checklist](docs/phase_1/2k_live_verification_checklist.md). Note: PR #49 merged the code-now verifier, streaming, cleanup, and localhost gates; P1-006 and device execution remain open. |
| A24 | P2-016 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists) | Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment. | Each item lands with its named gate; dispositions plus rejected items recorded in C-011. Evidence: Each subitem lands with its named gate; Dispositions recorded in C-011. Authority: [C-011 ledger + C-027 (post-2M umbrella)](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-016 acceptance](docs/process/state_kernel.json). Note: Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake. |
| A25 | P2-047A | P2 Next Slice | READY | Freeze the controller capture-overhead ABBA harness comparing the standard event path with a buffered or minimal-marker path under identical outputs and hashes. | A frozen controller-overhead ABBA harness preserves output identity and defaults to instrumented-stack scope rather than unvalidated subtraction. Evidence: Frozen ABBA manifest; Standard and buffered/minimal-marker paths have identical output policy and hashes; Analysis refuses unsupported subtraction. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047A acceptance](docs/process/state_kernel.json). Fence: Do not subtract controller overhead without a separately justified correction model (Hardening adjudication C7). |
| A29 | DOC-008-REFLECTION | P4 Polish | READY | Replace planning_reflection_protocol.md with the DOC-008 redirect stub and reconcile its inbound references under condition 6. | Retire the reflection protocol as an independent intake surface while preserving its compatibility path. Evidence: planning_reflection_protocol.md is the exact redirect stub; Useful fields remain owned by the kernel or run reports; Inbound references use the consolidated intake route. Authority: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Fence: Keep the compatibility path and do not create another intake checklist (DOC-008 reflection-protocol fence). |
| A30 | DOC-008-STATUS | P4 Polish | READY | Perform the lead-authored PROJECT_STATUS compaction and verbatim history archival required by DOC-008 condition 8. | Lead compacts PROJECT_STATUS and preserves removed dated updates in the specified history archive. Evidence: Lead-authored PROJECT_STATUS has at most seven current sections; Removed dated updates are preserved verbatim in the history archive; Advisor-visible quantitative claims retain evidence pointers. Authority: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Fence: Lead authors final advisor-facing claims and no generator writes PROJECT_STATUS (DOC-008 PROJECT_STATUS authorship fence). |
| A31 | DOC-008-INTAKE | P4 Polish | READY | Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9. | Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: [DOC-008 intake and procedure reconciliation](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 intake reconciliation](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence). |
| A32 | DOC-008 | P4 Polish | PARTIAL; READY; GATES close: DOC-008-INTAKE; GATES close: DOC-008-REFLECTION; GATES close: DOC-008-STATUS | Close the reopened DOC-008 migration only after residual conditions 4, 6, 8, and 9 land and every original completion condition is rechecked. | Every original DOC-008 completion condition lands before the reopened task returns to complete. Evidence: All nine DOC-008 required outcomes rechecked; Focused and canonical suites pass; Final-head review confirms one work-selection authority. Authority: [DOC-008 state-kernel specification](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 required outcomes](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not redeclare DOC-008 complete until every original required outcome lands (DOC-008 required outcomes). Note: Reopened by WO-021; phase C repairs work-selection authority while three residual task records remain live. |
| A33 | P2-050 | P3 Hardening Candidates | READY | Adjudicate the C-028 dissent-record candidates separately: frozen-legacy claim_eligibility mapper, semantic cooldown-row verification, once-per-manifest first-run exemption, scoped top-up detection, and cooldown trace v2. | Each C-028 dissent-record candidate receives its own adjudication before any implementation. Evidence: Frozen-legacy claim_eligibility mapper receives its own adjudication; Semantic cooldown-row verification receives its own adjudication; Once-per-manifest first-run exemption receives its own adjudication; Scoped top-up detection and cooldown trace v2 receive their own adjudications. Authority: [C-028 dissent-record queue candidates](docs/run_reports/2026-07-11-c028-continuation.md). Acceptance: [P2-050 acceptance](docs/process/state_kernel.json). Fence: Do not implement any candidate before its own recorded adjudication (C-028 dissent-record queue candidates). |
| A34 | TOOL-01 | P3 Tooling | READY | Fix codex-run-v3 defects: resume-after-NEEDS_SCOPE no-op; preventive permission profiles; NEEDS_RULING recognition; effort-default passthrough; stream-death OK exits with thin out-files; resume --last cross-thread attachment through the global latest session; and session-open paths lacking per-path match specifiers. | All seven codex-run-v3 defects close in lead personal tooling with targeted regressions and updated adapter operations lessons. Evidence: Resume after NEEDS_SCOPE continues the requested work; Preventive permission profiles and NEEDS_RULING recognition are covered; Omitted effort defaults to xhigh instead of config passthrough; Upstream stream death fails instead of exiting OK with a thin out-file; Resume requires an explicit session ID and cannot cross-attach through a global --last pointer; Session-open accepts a per-path match specifier without post-hoc child expansion. Authority: [Bridge v1.1 wrapper and session operations record](docs/run_reports/2026-07-13-bridge-v11.md). Acceptance: [TOOL-01 acceptance](docs/process/state_kernel.json). Fence: Keep implementation in lead personal tooling; this repository owns only the work record (Bridge v1.1 wrapper and session operations record). Note: lead personal tooling, non-repo |
| A35 | AUD-FOLLOWUPS | P3 Hardening Candidates | READY | Close the ULTRA comparison audit's accepted small residue in one bounded agent task: WO-012's owned D-062 lint queue row, WO-014 realized-token discrimination, WO-017 default no-handoff regression, WO-020 standalone bridge-checker decision, and WO-040 authored-instruction absolute-path plus genuine pristine-clone coverage. | The ULTRA comparison audit's five accepted small follow-ups close with discriminating tests or an explicit recorded decision, without creating a ceremony-dispositions task. Evidence: WO-012's owned D-062 lint queue-row obligation is implemented and covered; WO-014 has a realized-token discriminating test; WO-017 has a default no-handoff regression assertion; WO-020 has a recorded standalone bridge-checker decision; WO-040 has authored-instruction absolute-path coverage plus a genuine pristine-clone test. Authority: [Comprehensive-audit close-out and accepted-residue list](docs/reviews/2026-07-13-comprehensive-audit/report.md). Acceptance: [AUD-FOLLOWUPS acceptance](docs/process/state_kernel.json). Fence: Do not create AUD-CEREMONY-DISPOSITIONS; ceremony dispositions remain report-owned (Comprehensive-audit report disposition ledger). Note: Accepted small residue only; audit ceremony dispositions remain in the report. |
| A36 | AUD-WO-033 | P3 Hardening Candidates | READY; GATES close: P2-006 | After 2M, split scripts/run_campaign.py along tested policy seams, pure validation and provenance first and execution lifecycle second, only when campaign-scale or split or multi-node work first forces edits to that path. | The post-2M campaign-runner refactor is behavior-preserving across the full campaign test portfolio and retains every collection and claim-readiness safeguard. Evidence: Pure validation and provenance seams are extracted before execution lifecycle seams; The full campaign behavior-parity portfolio is green before and after the split; Locks, waivers, backups, cooldown, and claim-readiness behavior remain unchanged. Authority: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Keep this post-2M and behavior-preserving; do not redesign campaigns or weaken locks, waivers, backups, cooldown, or claim-readiness gates (Comprehensive-audit register WO-033 non-goals and risk note). |
| A37 | AUD-WO-034 | P3 Hardening Candidates | READY; GATES close: PHASE-3-SPLIT-SCHEDULED | At Phase-3 split scheduling, assign bounded owners and dependencies for transfer-bench, split replay, composite validate and reduce, KV-economics reduction, and matrix-generator extension before any PLANNED command becomes executable. | When Phase-3 split work is scheduled, every PLANNED pack command gains an owner or explicit deferred marker without pack collapse or premature implementation. Evidence: Every PLANNED command has a bounded owner row or explicit deferred-design marker; Pack-command ownership lint passes positive and negative fixtures; Settled split pre-registration requirements and offline-before-live fences remain intact. Authority: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not prune draft designs, collapse campaign packs, or implement split or KV work in this ownership pass (Comprehensive-audit register WO-034 non-goals). |
| A38 | AUD-WO-035 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-TRANSFER-SCHEDULED | Before the first 2K-live or remote split-transfer task, define a versioned discriminated node-worker payload and test realistic typed rejection without overloading telemetry blocks. | The 2K-live and remote roadmap has a versioned transfer-task payload seam with typed rejection before split-transfer implementation. Evidence: A versioned discriminated payload path exists for transfer tasks; A realistic unsupported transfer request fails with a typed versioned error; Telemetry blocks are not overloaded with transfer semantics. Authority: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Define and reject the future transfer shape only; do not implement split execution or transfer benchmarking (Comprehensive-audit register WO-035 non-goals). Note: D-043 supersession closure falls due at landing: add the dated protocol-version supersession line identified by PA-2. |
| A39 | AUD-WO-036 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-CONCURRENCY-SCHEDULED | When 2K-live or remote retries or concurrency are introduced, add a pre-launch node and GPU ownership lease plus idempotent duplicate prepare and start behavior. | Retries or concurrent 2K-live and remote campaigns cannot double-own a node or GPU and duplicate delivery is idempotent. Evidence: Duplicate prepare and start delivery is idempotent; Node and GPU ownership is leased before launch; Concurrency coverage exercises the ownership and duplicate-delivery contract. Authority: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not run concurrent hardware campaigns or make live-correctness claims in this agent task (Comprehensive-audit register WO-036 non-goals). |
| A40 | AUD-WO-037 | P3 Hardening Candidates | READY; GATES live_promotion: 2K-LIVE-PROMOTION-SCHEDULED | Fold non-self-asserted promotion authority into the 2K-live P2-005 and NV-GATE-2 code-now path before live promotion: bind an implementation receipt to commit and protocol pins and derive per-bundle execution class from the transport path. | Before 2K live promotion, non-self-asserted implementation authority and transport-derived execution classification fail closed at claim admission. Evidence: Fixture, unknown, unpromoted-live, and promoted-live classifications are tested; Unknown and unpromoted NVIDIA bundles are refused at claim admission; Promotion receipt is commit and protocol bound and cannot be forged through config or metadata. Authority: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Land this before, never after, the first claim-bearing NVIDIA live promotion; do not execute NV-GATE-2 or de-provisionalize hardware results here (Comprehensive-audit register WO-037 non-goals). Note: D-043 supersession closure falls due at landing: add the dated D-057 governed-reason amendment identified by PA-2. |
| A41 | AUD-WO-038 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-MULTINODE-DECIDED | At the 2K-live or remote multi-node roadmap decision, choose one owned remote execution boundary, consolidate duplicated lifecycle evidence helpers, and remove only proven-unconsumed transport surface with compatibility disposition. | At the 2K-live or remote multi-node decision, one owned execution boundary replaces only proven duplication while node-worker safeguards and public compatibility remain intact. Evidence: Lifecycle parity covers node-worker, subprocess, SSH, interface, and controller failure paths; Every deleted surface has a bounded absence or deprecation-compatibility trace; node_worker remains self-contained with backend-specific timeout, identity, log, clock, and cleanup safeguards. Authority: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Re-baseline against WO-001 and WO-010, keep node_worker self-contained, and do not delete public transport methods on repository absence alone (Comprehensive-audit register WO-038 risk boundaries). Note: D-043 supersession closure falls due at landing: back-annotate the public adapter and transport contract as required by PA-2. |
| A42 | AUD-WO-039 | P3 Hardening Candidates | PARTIAL; READY; GATES close: SITE-CAPACITY-RIGHTSIZING-DECIDED | At the next explicit site-capacity or right-sizing decision after SITE-02, remove only proven-unused live payload fields and make any further page trim through a recorded retained-route and value-versus-bytes review. | The remaining site payload and right-sizing work removes only proven-unused live fields and any page removal follows an explicit value-versus-bytes retention review. Evidence: Packed-byte and request reduction is measured; Route and link checks pass and every removed page has a retention decision; Consumed views, deep links, source access, and provenance stamps remain intact. Authority: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Trim only live payload fields proven unused; preserve advisor-facing pages, navigation, source access, stable deep links, and provenance unless a per-page retention review says otherwise (Comprehensive-audit register WO-039 preservation boundary). Note: Partial page trim landed 2026-07-15 by redirecting the duplicative capsule task-queue mirror while preserving its routes; remaining payload work is open. D-043 supersession closure falls due at landing through the dated D-051 amendment identified by PA-2. |
| A43 | CUSTODY-HARDEN-01 | P2 Next Slice | READY | Custody hardening follow-on from the screen+budget gauntlet: reduce-layer label-trust removal (G2A), drift-bound seal authentication (A3-r2), dead no-freshness accommodation disposition, artifact_schema_invalid mislabel. | Close the PR #85 gauntlet's deferred custody-hardening seams: config-derived mockness reaches the reduce-layer barriers, the drift-bound seal stops being self-certifying, and two diagnostic nits are resolved. Evidence: Reduce-layer environment/CPU claim barriers derive mockness from the custody-bound config, with metadata/summary-label early returns removed; Drift-bound artifact corpus identities resolve against repo-registered or custody-bound bytes (seal no longer self-certifying); Dead pre-addendum no-freshness accommodation removed or pinned as intentional forward-compatibility; artifact_schema_invalid evidence-binding mislabel renamed or documented at emission site. Authority: [C-045 gauntlet deferrals (council log; detail in docs/run_reports/2026-07-24-screen-budget-gauntlet.md)](docs/council_log.md). Acceptance: [CUSTODY-HARDEN-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from PR #85 gauntlet deferrals; triangle-agreement enforcement (merged) already raises these seams to three-file forgery cost. |
| A46 | FLOOR-WORKLOAD-SIZING-01 | P1 Phase Gate | READY | Re-size the floor/science campaign workloads so measured effects clear the duration-independent attribution floor, and pilot the resulting effect-to-floor ratio before spending quiet-machine nights on ABBA collection at current sizes. | Anchor-attribution error is approximately duration-independent (~1 J regardless of phase size) while effects scale with workload, so lengthening prefill/decode raises effect-to-floor linearly at zero instrument cost. Evidence: Measured effect-to-floor ratio at candidate workload sizes, from a pilot rather than assumption; Re-sized configs for the remaining floor stages, with the sizing rationale recorded; Explicit decision on which queued stages are collected at which sizes. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-WORKLOAD-SIZING-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25; scope corrected same day after the quantitative replay. NOT a blocker on the ABBA roadmap: under the labelled-floor path the queued stages remain scientifically viable at current sizes (tens-of-percent effects on ~50 J clear a ~3 J floor plus claim-side bound). This is a MARGIN optimisation — attribution error is duration-independent while effects scale with workload, so longer prefill/decode buys effect-to-floor ratio for free. Pilot the ratio at candidate sizes before committing the remaining quiet-machine nights. |
| A47 | FLOOR-COMMONMODE-01 | P2 Next Slice | READY | Pre-register and evaluate a common-mode anchor estimator for ABBA blocks: sweep one shared fiducial shift across all four members, re-integrate measured curves, and add only genuinely per-bundle components adversarially. | The fiducial term is ~80% of the composed anchor bound (24.9 of ~31.1 ms, verified) and is literally the same artifact for all four members of a block; treating it as four independent adversarial draws is itself an unphysical modelling choice. Evidence: Block-timescale fiducial stationarity registered as a NAMED transfer assumption with its evidence; Estimator pre-registered before it touches claim-bearing data; The identical estimator applied to BOTH the calibration blocks and the consuming science contrast (a floor calibrated with cancellation the consumer does not get would understate false effects); Quantified gain on a5/a10 blocks versus the worst-case-sum default. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-COMMONMODE-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25. Quantified same day on a5 decode ABBA (10 complete blocks): implemented worst-case-sum half-width gives a 6.46 J comparative floor; a common-mode proxy gives 2.13 J, a 3x improvement — material, but still above that cell's 0.60 J point floor, so it does not by itself restore extraction under the current gate. Value is in tightening the labelled floor, not in avoiding the label. Fiducial share of the composed bound measured at 80-87%. |
| A48 | PHASE-SHARE-ESTIMAND-01 | P2 Next Slice | READY | Investigate the anti-correlated prefill/decode boundary error: energy a shift removes from one phase it adds to the other, so the phase-share estimand has ONE boundary nuisance parameter whose joint envelope is a curve, not a box. | Treating each phase's anchor envelope as an independent box double-spends the shared interior boundary and inflates uncertainty on exactly the split/share quantity the Splitwise replication needs. Evidence: Determined whether _corner_composed_anchor_shift_envelope treats the shared interior boundary independently; Joint envelope over the single boundary-position parameter derived by re-integration sweep (measured-curve arithmetic only); Quantified effect on the phase-asymmetry claim envelope versus the independent-box treatment. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [PHASE-SHARE-ESTIMAND-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from the attribution-limit adjudication. Potentially the largest single win available for Splitwise sizing, at no instrument cost. |
| A49 | MODULARITY-01 | P3 Hardening Candidates | READY | Close the campaign-authoring modularity gap surveyed 2026-07-29: parameterize the campaign generator over a campaign-spec artifact and replace code-side literal assertions (analysis-manifest condition pairs, calibration scopes, phase-metric list) with registry-declared hash-validated sets. | Close the campaign-authoring modularity gap: campaign-spec-driven generation and registry-declared closed sets make every experiment axis swappable by config, per Ed's modularity directive. Evidence: Campaign generator is a parameterized function over a campaign-spec artifact (model, N, size profiles, block pattern, suite ref, run-ID prefix); a model swap touches one spec file and MODEL_TAG/PLAN_ID/run-ID prefixes derive from it with no parallel literal edits; Analysis-side closed sets (condition pairs, calibration scopes, phase-metric list) are declared in hash-bound registry artifacts and validated against those declarations, replacing the code-side literals at analysis_manifest.py:29-30,542-549 and detection_floor.py:87,89-95; Recorded-but-deferred residue dispositioned or re-queued: powermetrics references outside the adapter boundary, external-dataset ingestion, chat-template/thinking-mode seam, ABBA arity welded into three sites. Authority: [2026-07-29 modularity survey (Ed directive + per-axis grades)](docs/run_reports/2026-07-29-modularity-survey.md). Acceptance: [MODULARITY-01 acceptance](docs/process/state_kernel.json). Fence: Modularity applies to the harness, never to frozen claim pins: ratified hard literals (six-decimal pre-registration floor pins, lead-verified digests) stay anti-modular on purpose and must not be parameterized. (D-078 provenance amendment + D-079 operative-floor pins (hard literals are lead-verified, never parameterized)). Note: Minted 2026-07-29 from Ed's modularity directive. Survey verdict: runtime/telemetry Protocol layer and content-addressed provenance spine are already modular; the gap is campaign authoring above the adapter and literal assertions below the reader. Practical payoff lands with the planned Qwen3 cross-generation follow-up. |
| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
| A51 | NODE-CUSTODY-DEFAULT-01 | P3 Hardening Candidates | READY | Decide and implement whether the production DEFAULT_RETENTION_ROOT should be process/instance-unique: it currently is a fixed shared temp path (a latent collision hazard for genuinely concurrent clients), but making it unique conflicts with next-session custody reclamation. Resolve the tradeoff or record it as accepted. | Harden the production DEFAULT_RETENTION_ROOT against concurrent-client collision while preserving next-session custody reclamation (the NEEDS_RULING tradeoff deferred from NVIDIA-RETENTION-FLAKE-01). Evidence: The production DEFAULT_RETENTION_ROOT no longer collides for genuinely concurrent NodeClients sharing a scope, without breaking next-session custody reclamation (a later process must still locate the manifest it is entitled to reclaim); A regression proves two default-constructed clients in one process do not clobber each other AND that the documented reclamation contract still resolves the correct manifest across process boundaries; No retention/custody assertion is weakened; only root selection changes. Authority: [NVIDIA-RETENTION-FLAKE-01 fix report F1/F3 (PR #97): unique default roots close concurrent collision but conflict with next-session reclamation](docs/run_reports/2026-08-03-desk-session.md). Acceptance: [NODE-CUSTODY-DEFAULT-01 acceptance](docs/process/state_kernel.json). Fence: Isolation-only: do not weaken any retention/custody assertion; the reclamation contract's cross-process manifest resolution must survive any default-root change (NVIDIA-RETENTION-FLAKE-01 test-side fix (PR #97) already closed the flake). Note: Deferred 2026-08-03 from NVIDIA-RETENTION-FLAKE-01 (PR #97 closed the test-side flake); the production hardening is a NEEDS_RULING tradeoff, non-blocking (no current concurrent-client scenario). |
| A52 | D080-TRIGGER-01 | P3 Hardening Candidates | BLOCKED — D-080-amendment (Ed ratifies the trigger cadence and the runner (cron routine vs manual)) | Wire D-080's standing fresh-eyes sweep to a REAL trigger (calendar cron or every-N-merged-PRs), run as a separate concurrent read-only instance per the Ed-validated 2026-08-03 pattern, findings delivered mid-flight; reconcile D-080 clause 4(ii)'s stale zero-unique-catch citation. | The fresh-eyes sweep fires without anyone remembering it, on a ratified cadence, as a concurrent read-only instance. Evidence: A ratified trigger exists (cron routine or PR-count hook) and has fired at least once; D-080 clause 4(ii)'s stale citation is reconciled by amendment. Authority: [D-080 + the 2026-08-03 sweep finding (never fired) + Ed's concurrent-audit validation](docs/decision_log.md). Acceptance: [D080-TRIGGER-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-03: minted from the two-week soundness sweep's finding that D-080 has never fired, plus Ed's validated concurrent-audit pattern (memory: concurrent-fable-audit-pattern). Non-blocking hardening. |
| A53 | CGV-HARDEN-01 | P3 Hardening Candidates | READY | Harden runner-owned receipt persistence after validator --receipt-out removal: use a dirfd-relative receipt write that closes receipt-write TOCTOU and supplies fsync plus directory-sync atomicity. | The convening runner durably persists validator receipts through a dirfd-relative, crash-atomic, fsync-complete write path. Evidence: The convening runner persists the validator receipt with a dirfd-relative write that closes the receipt-write TOCTOU; Receipt publication is atomic and includes file fsync plus parent-directory sync; Regression tests distinguish path replacement, durability failure, and successful atomic publication. Authority: [2026-08-05 COLDGATE-VALIDATOR F3 consult Q2 receipt-persistence disposition](docs/process_traces/2026-08-05-cgv-f3-consult/SYNTHESIS.md). Acceptance: [CGV-HARDEN-01 acceptance](docs/process/state_kernel.json). Fence: Keep this row a sibling of COLDGATE-HANDOFF-01 and never merge them: durable receipt storage and validated-byte judge handoff have different contracts, tests, and failure consequences (2026-08-05 F3 consult Q2 dissent). Note: 2026-08-05: runner-scoped because PR #103 removed the validator's --receipt-out; deliberately registered as a sibling of, never folded into, COLDGATE-HANDOFF-01. |

### Shelved task records
## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired

**Date:** 2026-08-07 (Ed directive, in-thread; transcribed by the Fable
magistrate. Ed, verbatim: "if i recall for a paper ready at the quality
needed we need 3 more machine quiet nights and a lot of desk work",
with an explicit go to "execute all the deskwork" — read together with
his 2026-08-06 in-thread MVP-scope directive "a little more than just
decode, at least decode/prefill". His ruling moots a cold gate: apex
authority per rule 11.)
**Status:** ADOPTED. Full technical record:
`docs/process_traces/2026-08-06-d110-remint-fork/` (DIAGNOSIS: the
structural closure live-reproduced at `c537386`; Sol xhigh consult run
`20260806T165843Z-10884`; SYNTHESIS: magistrate concurrence).

1. **The D-110 clause-3 re-mint order (historical a10 consumption under
   the corrected selector) is SUPERSEDED.** The issued ledger holds only
   import-marked receipts; candidate discovery excludes imports by
   design; future live receipts cannot causally bracket past windows.
   The order is structurally unsatisfiable at main, not merely
   inconvenient. D-110's OTHER holdings STAND untouched: mint #1 and
   derivatives remain non-claim-bearing, and the never-zero
   `A_s = max(observed_drift_s, 0.010818)` allowance (D-102 pin 3)
   BINDS every mint under this entry.
2. **Replacement: three compact prospective claim windows** — fresh
   1.5B decode floor, fresh 7B decode floor, fresh 1.5B-vs-7B contrast
   — each with fresh §5A, live pre/post calibration receipts appended
   to the issued ledger, own verdict + head-pin + custody. Claims
   chain: historical corpus → issued D-079 acceptance rule → live
   brackets → prospective floors → prospective contrast. Honest
   framing preserved from the consult: historical data establish the
   RULE; live receipts bracket all claim-bearing science.
3. **Scope (Ed's decode/prefill directive):** prefill FLOOR cells ride
   both floor windows (cheap, same members' prefill phase). The model
   contrast is DECODE-ONLY by default: the 2026-08-07 desk feasibility
   check (`docs/process_traces/2026-08-07-prefill-feasibility/`) found
   the 128-token prefill contrast MARGINAL against the effective bar
   (interval overlaps it). A prospectively frozen ≥256-token prefill
   contrast arm remains an OPEN ED OPTION (estimand change +
   ~110 core minutes, likely its own window) — not adopted here.
4. **D-113 rewire:** its readiness dependency on the historical re-mint
   completing is REMOVED. The three-window P1 closure PRECEDES the
   broader MET-WINDOW-C-01 C2/C4/C5 replacement campaign (grounds:
   Ed's paper-first priority stack, 2026-08-06).
5. **Naming:** "Window D" is unavailable (collides with
   `runs_window_d_20260726` and D-113's reserved terminology); the
   three windows receive new immutable plan/root identifiers at plan
   freeze.
6. **Option 1 (finite-allowlist historical candidacy) is PRESERVED as
   a versioned contingency ONLY**, requiring a rule-11 cold gate before
   any implementation (semantics sketch: consult response §3). The
   historical corpora remain untouched on disk, non-claim-bearing per
   D-110 cl.1, logs sha-verified.
7. **Unblocked desk queue** (consult §4): freeze three window plans +
   budgets; 1.5B decode floor plan from the proven 10-absolute/40-null
   design; generalized mint pinsets with per-plan six-decimal literals
   (the D-084 hard literal `7.377086` refuses any corrected mint under
   every option — closure is per-plan supply via the generalized path);
   extraction specs / order manifests / evidence-root ids / contrast
   manifest; synthetic three-window live-ledger integration regression;
   D-102 successor-artifact packet; results/methods prose placeholders.

exec
/bin/zsh -lc "sed -n '1,190p' RUN_STATE.md
sed -n '2039,2064p' RUN_STATE.md
sed -n '2178,2310p' RUN_STATE.md
sed -n '2739,2805p' RUN_STATE.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# JouleWise Run State

This file is the single running pointer for the project: the one doc to
read to get back here. Session records live in `docs/run_reports/` and
`docs/process_traces/`; deliberation lives in `docs/council_log.md`;
policy lives in `docs/decision_log.md`. The three dated restart docs
`docs/process_traces/RESUME-2026-07-26.md`, `RESUME-2026-07-27.md`, and
`RESUME-2026-07-28.md` are now point-in-time session records only — each
carries a superseded banner, and everything still current in them is
folded in below. Do not create another dated restart doc; update this
file instead.

Last updated: 2026-08-07 — **LIVE SESSION (14h Ed window). Read this
block first;** the 2026-08-06 checkpoint below is executed history.

## ⏳ 2026-08-07 — paper-first session (LIVE; interim block, refreshed mid-flight)

**Ed's directives this session:** (1) abandon t3 work; (2) MVP capstone
paper FIRST, rest later; (3) 14h autonomous window; (4) three quiet
nights + desk work accepted as the path → **D-117 transcribed+pushed**
(D-110 re-mint order superseded; three prospective windows; prefill
floors ride floor windows; contrast decode-only; 256-tok prefill arm
still Ed's option); (5) Workflow license for non-serial desk work.

**DONE this session (all pushed):** checkpoint resume items 2-4 —
T3-CHAR-PAIR r01/r02 analysis banked (`fc48b1b`, dormant floor 0.192 W,
NON-CLAIM); prefill feasibility scout MARGINAL-at-128-tok custodied
(`docs/process_traces/2026-08-07-prefill-feasibility/`); C-049 marathon
council record (`03841c8`); skill-usage log; D-117 (`dbb9685`);
CLAIMS_STATUS un-staled (`a1f0e19`).

**IN FLIGHT (harvest, do not re-run):** (a) paper fix round on branch
`impl/paper-mvp-complete` — Sol xhigh, WRITE_SCOPE
docs/paper/draft-v1.md, closing round-2 findings (lens A 3 blockers:
tense, two-gate rule collapse, prefill-marginality misstatement; lens B
11; F-BIB-1) — review records + bibliography audit custodied on the
branch (`3542265`, `1892edc`); on harvest: lead diff gate → delta
re-audit → PR → merge on green (D-072). (b) Plan-freeze design consult
(Sol xhigh, read-only, scratchpad desk worktree) for the three-window
packet → on return: lead ratify → enforced-scope implementation units →
adversarial review → PR(s). Then: three-night operator packet for Ed;
end-of-session sweep + run report.

**Worktrees:** `<session-scratchpad>/desk` (main, bookkeeping) — prune
at close. Main tree holds `impl/paper-mvp-complete`.

## ✅ CHECKPOINT 2026-08-06 late — machine-move stop (resume script)

**Nothing in flight; nothing unpushed after this commit.** All background
jobs harvested; consult custodied; campaign logs sha-verified untouched.

**STATE IN ONE BREATH:** PR #109 merged (`c537386`); first consumption
attempt proved the historical re-mint structurally closed at main (see
AFTERNOON block + `docs/process_traces/2026-08-06-d110-remint-fork/`);
Sol xhigh + magistrate recommend Option 2 (three fresh prospective
windows); **Ed has NOT yet ruled** — he was probing costs when the
session stopped.

**Ed's in-thread directives this exchange (record, not yet decision-log):**
1. **MVP claim scope: "a little more than just decode, at least
   decode/prefill."** Magistrate's proposed shape (not yet Ed-acked):
   prefill FLOOR cells ride both fresh floor windows cheaply; a prefill
   CONTRAST first gets a labelled non-claim desk feasibility check from
   historical diagnostics against the D-078 ~5 J effective bar — if it
   clears, the contrast window grows a prefill ABBA arm; if not, prefill
   floors are claimed, contrast stays decode-only, and the infeasibility
   becomes a limitations paragraph.
2. **Ed challenged the zero-agent window rule** ("why can't you be
   running quietly?"). Owed answer components, for the successor: (a)
   physics at our bar — a bursty resident agent stack at ~0.1–0.5 W over
   minute-scale members is joules-to-tens-of-joules gross vs a ~5 J
   effective bar; idle subtraction cancels only the steady part; every
   CLAIM window to date was zero-agent; the app-resident mode was only
   ever used for fenced NON-claim characterization. (b) The banked
   `runs_char_t3appup_20260804_r01/_r02` captures exist precisely to
   QUANTIFY the dormant-app delta — **desk analysis queued (protocol
   §Analysis: mean/p95 package power from rich_telemetry_idle.jsonl)**;
   run it and give Ed a NUMBER. (c) The honest reframe: the binding
   presence constraint is §5A's sudo (network-time toggle), not the
   zero-agent rule; the agent-armed window design (QUIET-GUARD two-phase
   handoff, commits 2–4 + a scoped sudoers rule for the two systemsetup
   commands) exists and was descoped by Ed's OWN ruling as not worth the
   security-critical code — reopenable on his word if three fresh
   windows change his calculus.
3. Ed confirmed understanding that Option 2 = recollect the science
   windows (~3 windows, bookend-presence only) while everything else
   (instrument arc, acceptance rule, tooling, process record) stands.

**RESUME ORDER for the successor:**
1. If Ed has ruled the fork → transcribe the decision (supersede/amend
   D-110 + D-113 rewire per SYNTHESIS.md) and start the Option-2 desk
   queue (AFTERNOON block bottom). If not ruled → he owes: fork ruling,
   prefill-contrast shape ack, three-nights scheduling.
2. T3-CHAR-PAIR r01/r02 desk analysis (the dormant-app number) — cheap,
   answers his live question, informs any zero-agent-rule revisit.
3. Prefill-contrast feasibility desk check from historical diagnostics
   (labelled, non-claim).
4. End-of-session bookkeeping STILL OWED from the marathon session:
   consistency sweep, council log, skill-usage log.

## ⏳ 2026-08-06 AFTERNOON — re-mint fork: historical consumption is closed at main; Ed's ruling owed

**PR #109 merged on green** under D-072 at the gate-reviewed head
`d85b4f9` (no post-review commits; ledger + custody backup verified
byte-identical to the checkpoint sha before merge). `d079recon`
worktree + local branch pruned. All three D-110 conditions were thereby
satisfied — and the FIRST consumption attempt exposed a structural
block.

**THE FINDING (full record:
`docs/process_traces/2026-08-06-d110-remint-fork/` — DIAGNOSIS,
consult prompt+response, SYNTHESIS):** no historical window (a10,
window-C, old window-D, 7B-floor, contrast — all pre-genesis) can pass
authenticated max-bracket consumption at merged main. The issued ledger
holds only import-marked receipts; candidate discovery excludes imports
by design (CAL-BRACKET arc `63f43a68`, retained through issuance);
future live receipts cannot causally bracket past windows. Every
refusal was fail-closed; campaign logs sha-verified untouched (backups
in `~/JouleWise-window-custody/d110-remint-20260806/log_backups/`).

**Sol xhigh pre-decision consult (run `20260806T165843Z-10884`) +
magistrate CONCUR: Option 2 — supersede the D-110 historical re-mint
with THREE compact prospective windows** (fresh 1.5B decode floor,
fresh 7B decode floor, fresh contrast; each live-bracketed under the
issued regime, ~3 h class each). Chain: historical corpus → issued
acceptance rule → live brackets → prospective floors → contrast.
Option 1 (finite-allowlist historical candidacy) preserved as a
cold-gated contingency only — semantics sketch is in the consult
response. The consult verified all five historical bracket pairs exist
physically (drifts 0.000167–0.003680 s, under the 0.010818 s screen) —
the objection is provenance completeness, not causality.

**ED OWES (his ruling moots a cold gate — apex authority):**
1. Ratify superseding D-110's re-mint order with prospective
   replacement (+ the D-113 dependency rewire the consult flags).
2. MVP claim scope: decode contrast only, or more phase cells?
3. Three quiet-mac nights scheduling appetite (§5A each).

**Desk work unblocked regardless (consult §4, queue for the successor):**
freeze the three window plans + budgets (new immutable identifiers —
"Window D" name is taken); 1.5B decode-only floor plan from the proven
10-absolute/40-null design; generalized mint pinsets w/ per-plan
six-decimal literals (the D-084 literal `7.377086` refuses any
corrected mint under EVERY option — closure is per-plan supply via the
generalized path); freeze extraction specs/order manifests/
evidence-root ids/contrast manifest; synthetic three-window live-ledger
integration regression; D-102 successor-artifact packet; results/
methods prose with placeholders.

**Session ops notes:** verdict/extraction tooling gotchas (relative
`--runs-dir` path-doubling; verdict >2 min; stale `campaign.lock` on a
killed run) are recorded in the trace DIAGNOSIS. End-of-session
bookkeeping (consistency sweep, council log, skill-usage log) still
OWED.

## ✅ CHECKPOINT 2026-08-06 morning — executed by the afternoon session above

**IMMEDIATE RESUME ACTION (one live item):**
1. **PR #109 (`impl/d079-issuance`) — merge on green, then RE-MINT.**
   This PR ISSUES the D-079 calibration acceptance artifact (the
   authentication anchor for all floor-mint claims): D-116, issued
   config (fixture→issued, file sha `316113960c…`), committed head-pin
   (seq 76 / head `08456d50…`), cold-gate custody, + a 5-file test
   reconciliation. It cleared its FULL gauntlet (two rule-11 cold gates,
   adversarial audit + 3 delta rounds, exact-bytes dual cold review,
   zero-regression reconciliation + coverage-preservation audit ACCEPT).
   At checkpoint: CI running. **On green → self-merge under D-072**
   (it's the completed gate shape). If a successor finds it already
   merged, skip to the re-mint.

**THE AUTHORITATIVE LEDGER — do not lose (survives /clear as a file):**
- `runs/calibration_observation_ledger.jsonl` — the 76-receipt genesis
  chain, **git-ignored** (local custody artifact), sha256
  `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`.
  BACKED UP at `~/JouleWise-window-custody/d079-issuance-20260806/`
  (byte-identical). Deterministic from the custodied inputs
  (`docs/process_traces/2026-08-06-d079-issuance-coldgate/ISSUANCE-*`,
  on the PR branch → main after merge) + raw evidence. The committed
  head-pin (in the config) is the D-109 R1.4 trust anchor; the ledger
  file itself is a custody artifact. **Must stay backed up before the
  re-mint consumes it.**

**THE RE-MINT (task 8, the payoff — next after PR #109):**
- D-110 conditions now ALL satisfied: (a) PR #100, (c) PR #105, (b) THIS
  issuance. MINT-GENERALIZE-01 UNBLOCKED. Next: ONE custody session —
  governed a10 phase-floor extraction
  (`configs/floor_mint/a10_extraction_spec.json`, ~20 min) THEN mint #1
  re-derivation under the corrected selector, embedding the never-zero
  `A_s = max(observed_drift_s, 0.010818)` allowance (D-102 pin 3 /
  D-110). Same custody session (FLOOR-BIND-01 fence). Claim-critical →
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
detects it in the ~4-minute pre-calibration, with cause-removal (never
outcome-selection) retry semantics.

**Corrected floor figures — the old ones must not be repeated.** a10's
**absolute** floors are **3.823787 J prefill / 3.592138 J decode**,
INCLUDING the 0.652272 J whole-window drift allowance. The 3.17 / 2.94 J
numbers circulated earlier are the attribution-width floors BEFORE the
allowance and are diagnostics only (D-079 clause 5).

**AMENDED BY D-084 (2026-07-29): `3.592138` is the ABSOLUTE COMPONENT IN
ISOLATION, not the operative decode floor.** Mint #1's cell composes
a10's absolute 3.592138 J with window C's comparative 7.377086 J, and
under W3 rule 8 the cell gate is the **max, never the sum** — so the
canonical **operative decode floor is 7.377086 J**, and that is the hard
six-decimal literal pinned in `scripts/mint_floor_artifact.py`. D-079
clause 5's "3.592138" pin predates window C's comparative extraction and
is superseded for the operative figure; both components remain published
and LABELLED per D-078 clause 11.

### The critical path: build the mint (HISTORICAL — CLOSED 2026-07-30)

All four blockers below are closed and this section is retained as
chronology only: `scripts/mint_floor_artifact.py` is the non-test call
site (1), the 30-vs-37 basis question RESOLVED (2), `production_window`
is in `_CALIBRATION_SCOPES` (3), and `impl/floor-mint` merged via PR #87
(4). Mint #1 merged via PR #88 at `da83337`.

`build_floor_cell` / `build_floor_artifact` / `build_absolute_record` /
`build_comparative_record` in `joulewise/detection_floor.py` have zero
non-test call sites; `scripts/extract_detection_floors.py` writes an
extraction report and stops. Established blockers:

1. **`claim_ready` requires an absolute AND a comparative record in the
   SAME cell**, so a10 alone mints a structurally `smoke_only` artifact.
   Mint #1 must pair a10's absolute cell with window C's decode
   comparative. Verifying that the two share backend, metric,
   `window_class`, condition family, and stack identity is a GO/NO-GO,
   not a task.
2. **A 30-vs-37 member authentication mismatch:** the a10 phase spec
   selects 30 members; the passed verdict authenticates 37. Extraction of
   the authenticated basis takes **20 min 36 s** on real data — budget
   for it.
3. **Windows C and D have no legal `calibration_scope`.**
   `_CALIBRATION_SCOPES` is `("window_a", "window_b_revalidation",
   "smoke")`. D-079 clause 4 adopts one general production name; proposed
   literal `production_window`.
4. **Pre-mint schema hardening was then written but unmerged** (it
   merged via PR #87; the branch is on main): branch
   `impl/floor-mint` @ `617060a` (pushed) makes the extraction report
   export the admissible half-widths it already computes, and moves
   `_WIDENED_FLOOR_KEYS` from optional into the required key sets so
   width ABSENCE is a schema error rather than a silent fall-back to the
   point-only floor. Suite 2198 OK.

### Disk

**EXECUTED 2026-07-28 (Ed-authorized 2026-07-27: iCloud-only acceptable,
delete after verified upload — resolving both open disk questions).**
Disk now has **115 GB free** (was 33 GB; ~61 GB freed by the repo prune described below, the rest by unrelated local housekeeping). The selective-prune plan was
generalized to every runs corpus: all 27 corpora are archived in
`~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/` with a
per-corpus `MANIFEST.sha256`. Verification before any deletion: APFS-clone
name+byte parity; `brctl evict` of 100% of files (evict success = upload
complete); rematerialize-and-rehash of 20,028 files from iCloud (100% of
small evidence files + sampled traces) against the manifests — 0
mismatches. Then 1,848 `powermetrics*.plist` traces ≈ 61 GB were deleted
locally; **every small evidence file remains resident**, each pruned dir
carries `PRUNED.md` + `MANIFEST.sha256`. Restoring any trace =
`brctl download` its path under the archive.

Kept fully local (no deletion): `runs_window_a10_20260725(+_bound)` and
`runs_window_c_20260726(+_bound)` (mint #1 inputs),
`runs_window_a5_quarantine` (quarantine is evidence), and in `runs/` the
six frozen acceptance-gate bundles (`example-mac-mlx-*`) + `experiments/`
custody — the retained-corpus strict gate re-ran green post-prune (3/3,
incl. six-bundle strict validation), and keep-list file counts verified
unchanged.

### Orchestration

Global `CLAUDE.md` hard rule 11 now defines the topology: Fable as
MAGISTRATE and Ed's direct, Opus 5 as LIEUTENANT / operational chief, a
cold-Fable-instance gate with mandatory (not discretionary) triggers, and
an enumerated forbidden-to-decide-alone list for the lieutenant. D-080's
standing fresh-eyes sweep is the first exercise of that list.

### What needs Ed

1. RESOLVED 2026-07-27/28: Ed answered both disk questions (iCloud-only
   acceptable; delete after verified upload) and the archive+prune
   executed — see "Disk" above. Note the traces are now iCloud-only
   (single durable copy); flag if a second physical copy is wanted.
2. **AC power** for measurement windows — the production policy requires
   it and the machine was on battery.
3. A magistrate ruling on a conflict between D-080 and D-061: D-080's
   anti-ritual clause 4(ii) evaluates a rotating lens against the
   two-zero-sessions drop rule, which D-061 explicitly superseded with an
   expected-loss adjudication ("three applicable exposures TRIGGER an
   expected-loss review decision, never automatic deletion").
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


exec
/bin/zsh -lc "sed -n '7508,"'$p'"' docs/decision_log.md
sed -n '1,111p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md
sed -n '112,520p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired

**Date:** 2026-08-07 (Ed directive, in-thread; transcribed by the Fable
magistrate. Ed, verbatim: "if i recall for a paper ready at the quality
needed we need 3 more machine quiet nights and a lot of desk work",
with an explicit go to "execute all the deskwork" — read together with
his 2026-08-06 in-thread MVP-scope directive "a little more than just
decode, at least decode/prefill". His ruling moots a cold gate: apex
authority per rule 11.)
**Status:** ADOPTED. Full technical record:
`docs/process_traces/2026-08-06-d110-remint-fork/` (DIAGNOSIS: the
structural closure live-reproduced at `c537386`; Sol xhigh consult run
`20260806T165843Z-10884`; SYNTHESIS: magistrate concurrence).

1. **The D-110 clause-3 re-mint order (historical a10 consumption under
   the corrected selector) is SUPERSEDED.** The issued ledger holds only
   import-marked receipts; candidate discovery excludes imports by
   design; future live receipts cannot causally bracket past windows.
   The order is structurally unsatisfiable at main, not merely
   inconvenient. D-110's OTHER holdings STAND untouched: mint #1 and
   derivatives remain non-claim-bearing, and the never-zero
   `A_s = max(observed_drift_s, 0.010818)` allowance (D-102 pin 3)
   BINDS every mint under this entry.
2. **Replacement: three compact prospective claim windows** — fresh
   1.5B decode floor, fresh 7B decode floor, fresh 1.5B-vs-7B contrast
   — each with fresh §5A, live pre/post calibration receipts appended
   to the issued ledger, own verdict + head-pin + custody. Claims
   chain: historical corpus → issued D-079 acceptance rule → live
   brackets → prospective floors → prospective contrast. Honest
   framing preserved from the consult: historical data establish the
   RULE; live receipts bracket all claim-bearing science.
3. **Scope (Ed's decode/prefill directive):** prefill FLOOR cells ride
   both floor windows (cheap, same members' prefill phase). The model
   contrast is DECODE-ONLY by default: the 2026-08-07 desk feasibility
   check (`docs/process_traces/2026-08-07-prefill-feasibility/`) found
   the 128-token prefill contrast MARGINAL against the effective bar
   (interval overlaps it). A prospectively frozen ≥256-token prefill
   contrast arm remains an OPEN ED OPTION (estimand change +
   ~110 core minutes, likely its own window) — not adopted here.
4. **D-113 rewire:** its readiness dependency on the historical re-mint
   completing is REMOVED. The three-window P1 closure PRECEDES the
   broader MET-WINDOW-C-01 C2/C4/C5 replacement campaign (grounds:
   Ed's paper-first priority stack, 2026-08-06).
5. **Naming:** "Window D" is unavailable (collides with
   `runs_window_d_20260726` and D-113's reserved terminology); the
   three windows receive new immutable plan/root identifiers at plan
   freeze.
6. **Option 1 (finite-allowlist historical candidacy) is PRESERVED as
   a versioned contingency ONLY**, requiring a rule-11 cold gate before
   any implementation (semantics sketch: consult response §3). The
   historical corpora remain untouched on disk, non-claim-bearing per
   D-110 cl.1, logs sha-verified.
7. **Unblocked desk queue** (consult §4): freeze three window plans +
   budgets; 1.5B decode floor plan from the proven 10-absolute/40-null
   design; generalized mint pinsets with per-plan six-decimal literals
   (the D-084 hard literal `7.377086` refuses any corrected mint under
   every option — closure is per-plan supply via the generalized path);
   extraction specs / order manifests / evidence-root ids / contrast
   manifest; synthetic three-window live-ledger integration regression;
   D-102 successor-artifact packet; results/methods prose placeholders.
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Complete D-117 freeze design: three prospective windows fit the envelope, but live-ledger sessions, multi-cell minting, and D-102 successor generation must land before any arm.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "dbb9685669ac76ea65bf458b78eeb98d94bc6a80",
    "head_end": "94a24e562290b59f7b40908315bbae7a032ea47e",
    "upstream_end": "94a24e562290b59f7b40908315bbae7a032ea47e",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The current ledger cannot safely reserve both bookend observations under one unchanged committed head",
        "detail": "The append path requires the physical ledger head to equal the committed pin before each reservation. Finalizing the pre observation advances the physical head, so an ordinary post reservation cannot occur without an intervening pin advance or a new bracket-session capability.",
        "recommendation": "Implement an atomic two-slot bracket-session capability plus exact postcollection bracket binding before freezing arm packets."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The generalized mint is still decode-only and single-plan/single-cell",
        "detail": "The current generalized path hard-checks phase_energy_j.decode and a decode phase target. It cannot mint the two prefill riders or D-095's required combined multi-cell, multi-plan floor artifact.",
        "recommendation": "Introduce pinset v2 with per-plan component pins and an aggregate four-cell artifact pinset."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "No usable D-102 successor-artifact path exists for a live-prefixed ledger",
        "detail": "The issued acceptance artifact is exact-byte pinned and prior-set verification assumes the issuance corpus. A valid range-expanding live observation could therefore stop a campaign before member one or prevent its verdict.",
        "recommendation": "Pre-build and cold-gate a deterministic successor builder, registry, live-prefix verification, and trigger-time operator procedure."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "The referenced prefill-feasibility synthesis is absent at the inspected HEAD",
        "detail": "docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md does not exist in this worktree even though RUN_STATE says the trace was custodied.",
        "recommendation": "Recover or commit the trace before lead ratification; this memo uses D-117's adopted summary as authority."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "title": "Current queue rows still encode superseded C/D and D-110 gates",
        "detail": "TASK_QUEUE.md still presents MET-WINDOW-C-01 and MINT-GENERALIZE-01 under terminology and blockers superseded by D-117.",
        "recommendation": "Regenerate queue/state views from the owning state kernel after the plan-freeze decision is ratified."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse '@{upstream}'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## main...origin/main",
          "94a24e562290b59f7b40908315bbae7a032ea47e",
          "94a24e562290b59f7b40908315bbae7a032ea47e"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "94a24e562290b59f7b40908315bbae7a032ea47e$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "test -f docs/decision_log.md && test -f docs/process_traces/2026-08-06-d110-remint-fork/CONSULT-RESPONSE.md && test ! -e docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "FLAG1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "main advanced concurrently from dbb9685 to 94a24e5 during the read-only consult; the final state was re-inspected and remained clean.",
      "needs": "Freeze implementation scopes against 94a24e5 or a later explicitly reviewed head."
    },
    {
      "id": "FLAG2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No suites were run because this was a read-only design consult with no implementation.",
      "needs": "Each implementation unit below carries focused and canonical-suite obligations."
    }
  ]
}
```

## Findings

### F1 — Live-ledger bookending is not yet armable (blocker)

D-116’s issued ledger is the correct trust root, and D-117 correctly requires fresh live pre/post observations. The obstacle is mechanical: the present append path requires the physical ledger head to match the committed pin when reserving an attempt. Once the pre observation is finalized, that equality no longer holds for an ordinary post reservation.

The best design is an atomic `calibration_window_bracket_session.v1` capability:

1. At the pre-bookend, under a clean committed head, append one receipt reserving exactly two immutable slots: `pre` and `post`, each with its attempt ID, plan ID/SHA, evidence-root ID, expected time role, and shared session ID.
2. Finalize the pre slot before member one.
3. Leave the post slot prospectively open without treating it as an unresolved candidate or permitting claim evaluation.
4. Finalize or explicitly abort the post slot at the closing bookend.
5. Commit the terminal ledger head once, then issue an exact `calibration_bracket_binding.v1` mapping the frozen plan and evidence root to the two finalized content/receipt digests.
6. Candidate discovery still examines the complete live candidate universe; the binding selects the claimed pair but cannot hide extra candidates.

This is preferable to a source commit after the pre observation: that would mutate the repository and readiness head inside every quiet-window procedure. Two ordinary reservations appended in advance are also inferior because the outstanding post reservation would look unresolved unless ledger semantics were widened anyway.

Base plans should freeze calibration retry count at zero. A failed pre observation aborts before member one and closes the unused post slot; a failed post makes the physical attempt non-claim-bearing. If the lead wants one cause-removal retry, the session capability needs additional prospectively numbered slots and deterministic selection semantics before freeze—never an improvised retry.

Ideal no-failure receipt evolution from the issued sequence-76 head is three receipts per window—session capability, pre finalization, post finalization—ending at sequence 85 after all three windows. Exact sequence numbers are arm-time facts, not desk-frozen plan literals.

### F2 — The mint path needs a real v2, not another widened literal list (blocker)

The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:

- one plan and one artifact cell;
- `phase_energy_j.decode` only;
- `["phase","decode"]` only;
- no aggregate artifact over independently collected plans.

D-095 requires one multi-cell floor artifact whose 1.5B and 7B cells remain independently stack-scoped. D-117 adds prefill cells to both floor plans. The correct closure is therefore one four-cell artifact, not two loosely associated artifacts:

| Cell | Producer | Metric | Scientific family |
|---|---|---|---|
| 1.5B decode | 1.5B floor plan | `phase_energy_j.decode` | existing `df-ph-decode` |
| 1.5B prefill rider | 1.5B floor plan | `phase_energy_j.prefill` | new exact rider family |
| 7B decode | 7B floor plan | `phase_energy_j.decode` | D-085 `df-ph-decode-qwen25-7b` |
| 7B prefill rider | 7B floor plan | `phase_energy_j.prefill` | new exact rider family |

Each producer gets a component pinset; an aggregate pinset hard-checks both components and mints `d117-qwen25-phase-floor-set-v1`. Gamma consumes the two decode cells through D-095’s predeclared transport groups. It does not relabel contrast configs as floor configs.

### F3 — The D-102 successor packet is a pre-arm dependency (blocker)

A valid pre calibration can expand the observed range or approach the valid-observation limit. The issued artifact cannot absorb that live prefix today. The campaign therefore needs the following on disk and cold-gated before its first §5A arm:

- deterministic successor builder and validator;
- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
- generalized prior-set validation over a complete authenticated import-plus-live prefix;
- exact Decimal arithmetic, rounding, budget, prediction, and screen reproduction from D-079;
- a dry-run fixture that produces exact successor bytes and expected head pin;
- trigger-disposition logic that judges the range-expanding observation under the prior artifact before incorporating it into the successor;
- operator commands for pre-trigger and post-trigger branches.

I recommend deriving a successor from all content-distinct, valid, same-epoch observations through the chosen cutoff. Systematic, ordinary-invalid, aborted, or unresolved attempts remain recorded but excluded. The lead should explicitly ratify that corpus rule because D-102 establishes the successor obligation but does not fully spell out this live-prefix derivation policy.

At the pre bookend, a range expansion stops the chain before member one: close or preserve the bracket session according to the frozen state machine, commit the current ledger head, build and authenticate the successor, revalidate, then proceed. A post range expansion follows the same process after science but before the verdict. Systematic mismatch is a refusal, never something a successor can launder.

### F4 — Referenced trace missing (should-fix)

The named `docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md` is absent at `94a24e5`. D-117 itself records the adopted conclusion, so this memo treats the following as governing:

- floor prefill cells ride the floor-window decode members;
- gamma remains decode-only;
- the historical 128-token prefill contrast was marginal;
- a prospectively frozen 256-token contrast remains Ed’s option.

The missing trace prevents verification of any additional numerical assumptions it may contain. In particular, this memo does not freeze a 256-token runtime or effect-size target.

### F5 — Queue terminology is superseded (should-fix)

`TASK_QUEUE.md` still carries `MET-WINDOW-C-01`, prospective “C/D” splitting, and an old `MINT-GENERALIZE-01` D-110 blocker. Those rows cannot govern this work. D-117 clause 5 owns the namespace, and the live `RUN_STATE.md` block now recognizes that ruling. The queue should be regenerated after ratification, not manually interpreted during arm readiness.

### Ranked design decisions and rejected alternatives

1. **Use a two-slot ledger session capability and exact bracket binding.** Rejected: implicit reuse of neighboring observations, mid-window Git pin commits, or pre-reserving ordinary unresolved observations.

2. **Mint one four-cell floor artifact through pinset v2.** Rejected: two unrelated floor artifacts, summing arm floors, or weakening D-095’s independently stack-scoped maximum.

3. **Freeze zero calibration retries in the base plans.** Rejected: unbounded cause-removal retries and post hoc choice among observations. A retry-enabled variant requires a different capability state machine before freeze.

4. **Make prefill a metric rider over the exact decode members.** Rejected: copying the old dedicated 4096-prompt/64-output prefill workload, because that would add members and estimate a different condition. Post hoc extraction without a pre-registered cell is also insufficient.

5. **Treat the 256-token contrast as a fourth window plan.** Rejected: appending it to gamma later, which would change gamma’s plan SHA, member universe, order, multiplicity, runtime, and verdict basis.

6. **Use semantic immutable identifiers without dates or letters.** Rejected: `Window D`, C/D, and date-derived identities. Attempt dates belong in custody metadata, not scientific identity.

7. **Use a two-stage pin freeze.** Desk time freezes every knowable identifier, schema, member list, hash, and rule. Six-decimal operative values freeze only after governed collection and extraction. Rejected: placeholder literals presented as valid pins or any mint-time derivation.

### Proven template lineage

The templates are scientific and structural sources, not claim evidence.

| Plan | Files treated as the proven template | What is reused |
|---|---|---|
| 1.5B floor | `configs/campaigns/p2_015_floors/calibration_plan.json`; its SHA sidecar and generator; `02_phase_absolute/p2015-df-ph-decode-abs-r01.json` through `r10.json`; `05_phase_decode_abba/`’s forty decode configs and manifest; root `order_manifest.json`; `configs/floor_mint/a10_extraction_spec.json`; `configs/floor_mint/window_c_extraction_spec.json` | Exact Qwen2.5-1.5B stack identity, 10 absolute members, ten fixed A/B/B/A null blocks, runtime/config conventions, extraction shape |
| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
| Decode contrast | Entire `configs/campaigns/splitwise_decode_v1/`, particularly the plan, generator, forty configs, root/stage manifests, condition families, and `analysis_manifest_v3.json` | A=1.5B, B=7B, ten ABBA blocks, B−A orientation, v3 estimator and cross-stack floor rule |
| Operational references | `configs/campaigns/neg8_reference_corpus/` and the existing start/mid/end reference manifests | Twelve-member same-window NEG8 binding plus 3/1/3 references |

The old `02_phase_absolute/order_manifest.json` contains thirty interleaved decode, prefill, and short-prefill configs. It must not be copied as the new absolute manifest. Only its ten decode configs are the alpha source; the new ten-entry manifest is regenerated and independently hashed.

Historical results are diagnostic inputs only. No old evidence-root ID, calibration bracket, member output, or operative floor literal enters a prospective claim basis.

### Immutable identifier proposal

| Placeholder | Frozen plan ID | Evidence-root ID | Physical root |
|---|---|---|---|
| W-alpha | `plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v1` | `evidence-d117-floor-qwen25-1p5b-v1` | `runs_d117_floor_qwen25_1p5b_v1` |
| W-beta | `plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v1` | `evidence-d117-floor-qwen25-7b-v1` | `runs_d117_floor_qwen25_7b_v1` |
| W-gamma | `plan-d117-contrast-qwen25-1p5b-vs-7b-decode-v1` | `evidence-d117-contrast-qwen25-1p5b-vs-7b-v1` | `runs_d117_contrast_qwen25_1p5b_vs_7b_v1` |

Each also gets a separately named bound root ending in `_bound`. Failed physical attempts receive custody attempt suffixes outside the scientific ID; the clean evidence root is never silently reused.

### Common order-manifest contract

Every root manifest should bind:

- plan ID, exact plan SHA, generator SHA, and model/runtime revisions;
- ordered stage records with exact stage-manifest ID, SHA, expected member count, predecessor, and successor;
- exact relative config paths and config SHAs—no globs or directory discovery;
- ordinal, member ID, ABBA block and slot where applicable;
- fixed reference and NEG8 manifests;
- the prefill rider mapping for floor members;
- frozen attempt policy, including zero calibration retries and no outcome-driven top-ups;
- evidence-root ID and expected fresh physical path;
- hashes of condition families, extraction spec, and analysis manifest;
- arm-time attachment slots for the readiness record, session capability, and actual receipt identifiers without modifying frozen plan bytes.

An ABBA stage manifest records each block as `A1,B1,B2,A2`. Splitting blocks 1–5 and 6–10 around the midpoint reference does not reset block numbering.

### Per-window plans

#### Alpha — 1.5B decode floor plus prefill rider

| Stage | Members | Order |
|---|---:|---|
| Pre calibration | 1 live observation | Finalize reserved `pre` slot before science |
| Same-window bound corpus | 12 | Frozen NEG8 order, then bound evaluation |
| Start references | 3 | Frozen triplet |
| Absolute floor | 10 | `abs-r01` through `abs-r10` |
| Null half 1 | 20 | ABBA blocks 1–5 |
| Midpoint reference | 1 | Frozen midpoint |
| Null half 2 | 20 | ABBA blocks 6–10 |
| End references | 3 | Frozen triplet |
| Post calibration | 1 live observation | Finalize reserved `post` slot |
| Closeout | 0 science members | Terminal head pin, bracket binding, verdict, dual-root backup |

Science count is 50; operational captures are 12 bound, 7 references, and 2 calibrations. The prefill rider adds no member and no runtime.

The rider is a new condition family over the same 128-prompt/512-output decode bundles. It must pre-register `phase_energy_j.prefill`, phase precheck `["phase","prefill"]`, exact tokenizer/model/config identity, the same ten absolute members and forty null members, its estimator, n=10 block basis, and both absolute and comparative floor rules. It is not the old dedicated prefill condition.

The extraction spec contains four cells: decode absolute, decode comparative, prefill absolute, and prefill comparative. It names 100 cell-member references but exactly 50 unique bundles. Each cell supplies an exact member list, config hash list, expected n, condition-family hash, metric key, phase precheck, order-manifest pin, calibration basis, and evidence-root ID. Missing prefill phases, fallback values, or member discovery outside the list are fatal.

#### Beta — 7B decode floor plus prefill rider

The schedule is identical to alpha: pre calibration; 12 NEG8; start 3; absolute 10; ABBA blocks 1–5; midpoint 1; blocks 6–10; end 3; post calibration.

The decode condition remains D-085’s `df-ph-decode-qwen25-7b`; the fresh plan does not rename settled scientific semantics. The new prefill-rider family pins `phase_energy_j.prefill` over the exact 7B decode members and stack revision.

Its extraction contract is the same four-cell/50-unique-bundle shape as alpha. Old 7B values—absolute 6.294380… J and comparative 13.998036… J—are budget/design diagnostics only and are not pre-registered pins.

#### Gamma — 1.5B-versus-7B decode contrast

| Stage | Members | Order |
|---|---:|---|
| Pre calibration | 1 live observation | Finalize `pre` slot |
| Same-window bound corpus | 12 | Frozen NEG8 order, then bound evaluation |
| Start references | 3 | Frozen triplet |
| Contrast half 1 | 20 | ABBA blocks 1–5 |
| Midpoint reference | 1 | Frozen midpoint |
| Contrast half 2 | 20 | ABBA blocks 6–10 |
| End references | 3 | Frozen triplet |
| Post calibration | 1 live observation | Finalize `post` slot |
| Closeout | 0 science members | Pin, binding, verdict, backup, then analysis |

The frozen manifest remains decode-only:

- A is the exact 1.5B stack; B is the exact 7B stack.
- Metric is exactly `phase_energy_j.decode`.
- Estimand orientation is B−A.
- Design is ten A/B/B/A blocks, n=10 block estimates.
- Estimator is `abba_block_arm_mean_difference_t_v1`.
- Test is two-sided at family alpha 0.05, with the positive direction stated as the scientific hypothesis rather than used to change the test.
- `equivalence_margin` and `mde` remain null unless prospectively ruled otherwise.
- Floor rule remains `cross_stack_armwise_max.v1`: independently resolve the 1.5B and 7B decode cells and take their maximum, never their sum.
- Claim-side anchor bounds remain separate from the detection-floor operation.
- The finalized analysis basis pins the exact forty member paths, config hashes, stack identities, floor artifact bytes, calibration binding, and evidence root.

### Runtime evidence and budgets

Historical evidence in `docs/phase_2/splitwise_decode_campaign.md` §4 supplies:

- 1.5B decode member: 92.7 s, measured n=40;
- 1.5B reference member: 90.5 s, measured n=7;
- 7B decode member: approximately 97 s from the measured/probed anchor;
- 1.5B/7B mixed ABBA half: about 31.6 min raw member time.

The stage allowances incorporate the configured 30-second idle, warmup/teardown, stage arm overhead, and cooldown conventions. The pre-calibration allowance includes the required 180-second post-admin settle. The separate ten-minute untouched quiet-idle gate is added before applying the 20% margin.

| Component, minutes | Alpha | Beta | Gamma |
|---|---:|---:|---:|
| Pre calibration bracket | 8 | 8 | 8 |
| 12 NEG8 bound members | 22 | 22 | 22 |
| Bound evaluation | 1 | 1 | 1 |
| Start 3 references | 8 | 8 | 8 |
| Absolute 10 | 19 | 20 | — |
| ABBA blocks 1–5 | 34 | 36 | 35 |
| Midpoint reference | 5 | 5 | 5 |
| ABBA blocks 6–10 | 34 | 36 | 35 |
| End 3 references | 8 | 8 | 8 |
| Post calibration bracket | 8 | 8 | 8 |
| Campaign subtotal | 147 | 152 | 130 |
| Untouched pre-arm idle | 10 | 10 | 10 |
| Base occupancy | 157 | 162 | 140 |
| With 20% failure margin | **188.4** | **194.4** | **168.0** |
| Hours | **3.14 h** | **3.24 h** | **2.80 h** |
| 2–4 h envelope | Pass | Pass | Pass |

The margin is time headroom, not authority to add members, replace a cap-hit observation, or top up an unfavorable result. The fixed manifest and frozen failure policy decide scientific validity.

### §5A operator bookends

Before each window:

1. Verify the reviewed plan/readiness record, fresh empty roots, model artifacts, charger/AC state, power policy, OS/tool identity, empty waiver set, and current acceptance artifact.
2. Verify the physical ledger head equals the authenticated committed pin.
3. Correct the clock against the trusted source, record the correction and `usingnetworktime` state, turn network time off, and settle for at least 180 seconds.
4. Establish zero-agent/zero-output-streaming conditions and complete ten untouched minutes of daemon idle.
5. Append the exact two-slot bracket session capability.
6. Capture and finalize the pre observation; run the acceptance and D-102 trigger probe.
7. Only after every gate is green, emit the one-line arm message and walk away.

At the closing bookend:

1. Capture the post observation before changing power, network-time, or workload state.
2. Finalize the post slot or write the governed failure/abort closure.
3. Commit and authenticate the terminal ledger head.
4. Emit the exact bracket binding and whole-window verdict from one immutable ledger snapshot.
5. Back up evidence and bound roots with verified return code and hashes.
6. Restore network time and record the restoration only after measurement completion and custody closeout.

### Prefill floor claim eligibility

A rider is claim-eligible only if desk freeze already binds:

- exact metric and phase path;
- exact workload parameters, model/tokenizer revision, seeds, quantization, runtime, sampling, and telemetry mode;
- absolute and comparative member lists and order manifests;
- exact condition-family ID and hash;
- n and estimator;
- calibration cell, acceptance artifact role, and D-110 allowance rule;
- extraction failure behavior;
- allowed consumer families.

For each metric, the operative floor is the maximum of independently evaluated absolute and comparative components. Apply D-110 once as `A_s = max(observed_drift, 0.010818)`. Never sum components and never borrow a decode floor for prefill.

### Two-stage mint freeze

**Desk-frozen pin requirements**

For each floor plan, freeze:

- plan ID, declared SHA, sidecar SHA, and actual artifact SHA;
- evidence-root ID;
- four intended cell roles across the two plans;
- condition-family IDs/hashes;
- metric and phase-precheck paths;
- absolute and comparative order-manifest IDs/hashes;
- extraction-spec SHA and exact members;
- expected counts;
- model/runtime/config hashes;
- calibration acceptance artifact ID/SHA/derivation rule;
- D-110 never-zero allowance rule;
- aggregate artifact ID and transport allowlists.

These live in a non-mintable `pin_requirements.v2` artifact. Unresolved values must be structurally absent or explicitly marked unresolved; the file cannot satisfy the final pinset schema.

**Postcollection-frozen pins**

After passed verdicts and governed extraction, freeze separately for each of the four cells:

- absolute and comparative evaluation-basis SHA/count;
- exact accepted pre/post receipt and content digests;
- bracket-binding SHA and terminal ledger head;
- observed drift and applied allowance;
- extraction-report SHA;
- absolute, comparative, and operative values;
- the operative literal formatted independently as exactly six decimals using the repository’s `.6f` convention.

The lead independently recomputes each six-decimal literal from primary extraction bytes. The mint only compares supplied literals and hashes; it does not calculate them. The old `7.377086` literal is never reused.

Gamma has no producer mint. Its consumer pinset instead binds the exact combined floor artifact bytes, the two decode-cell IDs, its plan/order/analysis manifests, and its finalized evaluation basis.

### Synthetic three-window live-ledger regression

The fixture begins with the exact issued-ledger semantics: 76 receipts, including 38 historical import observations—30 valid, 2 systematic, 6 ordinary-invalid. Candidate discovery must exclude every import-marked observation.

The no-failure live extension adds three bracket capabilities and six finalized live observations. From one immutable final snapshot, the regression must prove:

- exactly six live candidates and zero imported candidates;
- alpha, beta, and gamma each bind only their own pre/post pair;
- all six are same-epoch, causal, fresh, within protocol and T1 limits;
- no neighboring endpoint can substitute for a bound endpoint;
- all three verdicts use the same complete candidate universe;
- the ideal terminal sequence is 85 under the proposed three-receipt session model;
- the D-110 never-zero allowance remains active.

Required refusal vectors:

- import-marker removal, import leakage, or candidate-discovery regression;
- missing, duplicate, reordered, or conflicting session/finalization receipts;
- open or abandoned session without a governed closure;
- physical-head/pin mismatch, rollback, fork, or uncommitted terminal head;
- omitted, added, duplicated, off-ledger, or content-substituted observations;
- missing, tampered, swapped, or cross-window bracket binding;
- noncausal endpoint, stale endpoint, T1 failure, protocol failure, or epoch mismatch;
- systematic classification;
- one range-expanding live observation requiring a successor;
- the observation-count boundary reaching the D-102 limit;
- a successor whose prior set omits or changes an authenticated prefix.

### Optional 256-token prefill contrast

Clean attachment inside frozen gamma is impossible. Adding the arm changes the workload, metric family, members, order, runtime, multiplicity, plan digest, evidence root, and verdict basis.

If Ed adopts it, create a fourth independently frozen, independently calibrated plan and evidence root. It may attach later only in a higher-level synthesis/claim packet that references gamma and the new prefill result as sibling artifacts. Gamma’s bytes remain unchanged.

The floor riders here use the prefill phase of the 128-prompt decode workload. They do not automatically transport to a prospectively defined 256-token contrast. The fourth plan needs either exact matching prefill floor cells or a separately predeclared and justified transport rule. No placeholder members or plan ID should be added to gamma now.

### Freeze order and lead gates

1. **Ruling gate:** lead accepts the session-capability semantics, zero-retry policy, successor corpus rule, four-cell artifact shape, and fourth-window treatment.
2. **Toolchain gate:** ledger session/binding, successor builder, pinset v2, multi-cell mint, prefill metric support, and three-window regression all land and pass focused plus canonical suites.
3. **Desk freeze gate:** generate all three campaign packs; freeze identifiers, model revisions, configs, manifests, condition families, extraction/analysis specs, budgets, failure policy, and hashes. Six-decimal values do not yet exist.
4. **Per-window arm gate:** attach current clean head, acceptance artifact, physical/committed ledger equality, fresh roots, exact environment preflight, empty waivers, §5A evidence, and bracket-session identifiers.
5. **Pre-science trigger gate:** finalize the pre observation and either accept it, issue a governed successor, or abort before member one.
6. **Post-window gate:** finalize post, commit terminal head, issue bracket binding, verdict, and verified backup.
7. **Floor mint gate:** after alpha and beta pass, run governed four-cell extraction, independently freeze literals, mint the combined artifact, and require `validate_floor_artifact` to return no findings.
8. **Gamma claim gate:** pass the whole-window verdict, finalize the v3 basis, run D-093 root scanning, resolve both decode arm floors from exact combined-artifact bytes, and apply the armwise maximum.

### Work-order list with enforced WRITE_SCOPE units

| Unit | Exact write scope | Invariants and tests | Dependency |
|---|---|---|---|
| U1 — ledger session and binding | `joulewise/calibration_ledger.py`; `joulewise/calibration_bracketing.py`; `scripts/reserve_calibration_window_bracket.py`; `tests/test_calibration_ledger.py`; `tests/test_calibration_bracketing.py` | Two immutable slots, one-use finalization, governed abort, no unresolved-candidate leakage, exact binding, head/pin refusals. Focused ledger/bracketing tests plus full suite. | Foundation; independent of U3 |
| U2 — D-102 successor engine | `joulewise/calibration_bracketing.py`; `scripts/build_calibration_acceptance_successor.py`; `configs/calibration/calibration_acceptance_registry.json`; `tests/test_calibration_acceptance_successor.py` | Complete authenticated live prefix, deterministic bytes, parent ancestry, exact Decimal derivation, range/count triggers, systematic refusal. Focused cold-gate fixtures plus full suite. | Sequential after U1 because of shared bracketing semantics |
| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
| U4 — three-window ledger regression | `tests/fixtures/calibration_live_three_window/**`; `tests/test_calibration_live_three_window.py` | Exact issuance fixture, import exclusion, six live candidates, three causal bindings, successor and refusal vectors. | After U1 and U2 |
| U5 — alpha campaign pack | `configs/campaigns/d117_floor_qwen25_1p5b_v1/**`; `configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json`; `tests/test_d117_floor_qwen25_1p5b_plan.py` | Exact 10+40 schedule, split midpoint, two metric riders, 50 unique bundles, fresh IDs, deterministic regeneration. | After U3 schema/IDs freeze; parallel with U6 |
| U6 — beta campaign pack | `configs/campaigns/d117_floor_qwen25_7b_v1/**`; `configs/floor_mint/d117_qwen25_7b_extraction_spec.json`; `tests/test_d117_floor_qwen25_7b_plan.py` | Same as U5, retaining D-085 stack/family identity. | After U3; parallel with U5 |
| U7 — gamma campaign pack | `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/**`; `tests/test_d117_decode_contrast_plan.py` | Forty ABBA members, decode-only metric, B−A orientation, v3 estimator, exact four-cell artifact consumer pins, no prefill placeholder. | After U3 floor cell/transport IDs freeze |
| U8 — operator/readiness packet | `docs/phase_2/window_runbook.md`; `scripts/validate_frozen_plan_readiness.py`; `tests/test_frozen_plan_readiness.py` | §5A sequence, session capability, pre-trigger successor gate, fresh roots, empty waivers, terminal binding/pin/backup. | After U1, U2, U5–U7 |
| U9 — state and custody bookkeeping | `docs/process/state_kernel.json`; `RUN_STATE.md`; `TASK_QUEUE.md`; `CLAIMS_STATUS.md`; `docs/run_reports/2026-08-07-d117-plan-freeze.md` | D-117 vocabulary, no C/D plan references, exact frozen digests, generated-view consistency. | Lead-owned, after all desk artifacts pass |
| U10 — postcollection pin closure | `scripts/floor_mint_pinsets/d117_qwen25_1p5b_v2.json`; `scripts/floor_mint_pinsets/d117_qwen25_7b_v2.json`; `scripts/floor_mint_pinsets/d117_qwen25_phase_floor_set_v2.json`; `results/floor_artifacts/d117_qwen25_phase_floor_set_v1.json`; `results/floor_artifacts/d117_qwen25_phase_floor_set_v1.sha256` | Only postcollection facts; independent literal recomputation; exact receipt/binding/head pins; validator returns no findings. | Sequential after alpha and beta pass |

Every unit should run its focused tests and `python3 -m unittest discover -s tests`. Shared files make U1→U2 sequential; U1 and U3 can proceed independently. U5 and U6 can proceed independently after U3 freezes the vocabulary. U7 waits for final floor-cell and transport identifiers. U10 is deliberately absent from the desk freeze.

### What the lead should double-check

- Recover the missing prefill-feasibility trace and compare its exact 256-token assumptions with this fourth-window conclusion.
- Ratify the two-slot ledger capability against D-109/D-116, especially whether an open post slot may exist during the pre-science successor probe.
- Decide explicitly between zero calibration retries and a prospectively numbered retry-capability variant.
- Ratify the D-102 successor corpus rule: all content-distinct valid same-epoch observations through the cutoff.
- Confirm that D-085’s 7B decode family ID is preserved and contrast transport uses allowlists rather than relabeling configs.
- Confirm pinset v2 supports multiple producer plans while preserving byte-for-byte v1 behavior.
- Verify the 20% allowance does not become permission for member replacement or result-driven top-up.
- Recheck full model revisions, local artifact hashes, runtime version, charger identity, and post-move environment at each arm.
- Independently calculate all four `.6f` operative literals from primary extraction bytes.
- Verify every one of the fifty floor bundles actually contains the registered prefill phase; a missing phase must fail extraction.
- Ensure gamma takes the maximum of the two decode arm floors, never their sum, and retains separate claim-side anchor bounds.
- Ensure the 128-prompt prefill riders are not presented as a floor for a later 256-token contrast without exact transport evidence.
- Regenerate the active queue from the state kernel so superseded C/D and D-110 gates cannot be mistaken for arm authority.
- Freeze against the final reviewed repository head; this consult began at `dbb9685` and ended cleanly at concurrently advanced `94a24e5`.

## Residual risk

No live timings, calibration observations, successor generation, or mint replay were performed. Runtime estimates therefore inherit historical-machine variance; the 20% margin is the current mitigation.

The absent feasibility synthesis limits review of the optional 256-token arm. Its attachment architecture is sound, but its member count, runtime, estimand, and floor transport remain intentionally unfrozen.
codex
The governing correction is now concrete: the fixed MVP is not “three nights total.” Alpha, beta, and gamma consume about 3.14 h, 3.24 h, and 2.80 h, and the paper’s §6 characterization table still requires a separate post-window decision/night. I’m now reading the full referee set before touching proposal claims, as requested.
exec
/bin/zsh -lc 'for f in ../portfolio/rev-attention-variant-energy.md ../portfolio/rev-batch-concurrency-energy.md ../portfolio/rev-contamination-characterization.md ../portfolio/rev-cross-runtime-contrast.md; do echo "FILE $f"; sed -n '"'1,"'$p'"' \""'$f"; done' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
FILE ../portfolio/rev-attention-variant-energy.md
# Counter-review — "Windowed Attention Under an Attribution-Limited Energy Instrument"

Reviewer: Opus 5 counter-reviewer (portfolio referee, adversarial charge).
Target: `scratchpad/portfolio/prop-attention-variant-energy.md` (final block, L5158–5212).
Ground truth: `scratchpad/desk` @ main. Every repo claim below is cited by path.

## VERDICT: **WEAK** — kill as written; a different, cheaper study survives underneath it.

Scores (1–10): **novelty 5 · feasibility 3 · mvp_leverage 5 · venue_fit 5 · original_goals 6**

The proposal deserves credit for one thing and should be read as honest about it:
it *self-demotes* the assigned KDA/GQA four-way to a same-checkpoint ablation and
says so plainly. That is exactly the behaviour the brief asked for. Unfortunately
the surviving ablation is itself infeasible on this stack, logically
self-contradictory at the only cell that carries an effect, and duplicates a
question the repo already banked in a form that needs **no runtime work at all**.

---

## F1 (FATAL). No admitted checkpoint on this stack has a sliding-window path in the pinned runtime.

The proposal's entire experiment rests on "one MLX-supported, 4–7B-class
checkpoint whose native sliding-window mask can be changed to full attention
without changing weights." Checked directly:

- Locally mirrored artifacts (`/Users/edr/jw_models/mlx-community/`) are exactly
  five: `Qwen2.5-0.5B/1.5B/7B-Instruct-4bit`, `Qwen3-4B-4bit`,
  `Qwen3.5-122B-A10B-4bit`.
- In pinned `mlx-lm` (`/Users/edr/code/JouleWise/.venv/.../mlx_lm/models/`), the
  files that reference `sliding_window` are: `olmo3`, `gemma3_text`, `gemma3n`,
  `mimo_v2_flash`, `llama`, `exaone_moe`, `step3p5`, `cohere2`, `gemma4_text`,
  `afmoe`, `gpt_oss`, `baichuan_m1`, `ministral3`, `exaone4`. **`qwen2.py` and
  `qwen3.py` are not among them.**

So the intersection of {admitted, hash-pinned, D-117-relevant models} and
{models with an SWA path} is **empty**. The experiment requires acquiring,
converting, quality-gating, hash-pinning and admitting a *new model family*
(Gemma-3 / Ministral-3 / Cohere2 class). The proposal budgets zero desk work for
this and never names a candidate. Under D-074-class precedent a conditional
primary repin is its own multi-week gated exercise
(`docs/decision_log.md` D-073/D-074).

Worse for the proposal's numbers: its sizing anchor is "the diagnostic Qwen2.5-7B
decode level is about 192 J for 512 outputs" — a number transplanted from a model
that **categorically cannot run this experiment**. The actual subject would be a
3–4B-class SWA model at roughly half the weight-byte traffic. My own estimate
(mine, not the repo's; ±large): Gemma-3-4B-4bit at 4× a 1024-token window moves
KV-read bytes ~13% (weights ≈2.5 GB vs KV 0.22→0.57 GB per step), i.e. ≈**12–18 J
on a ≈110 J decode** — above the ~5 J bar but *below* the proposal's own 10 J
desk gate at the low end. The proposal's headline "10–80 J" range is anchored on
the wrong model and is optimistic by roughly a factor of two.

## F2 (FATAL). The output-identity gate is logically impossible at the only cell with an effect.

The proposal makes exact output-token identity a hard admission gate ("merely
similar prose is insufficient"), and simultaneously predicts a resolvable effect
only *above* the window. But above the window, forcing full attention **is** a
change to the attention mask on ~5/6 of layers; the attention outputs differ, the
logits differ, and greedy decoding diverges. Identity holds only below the
window — precisely the cell the proposal itself expects to be `<5 J` and
unresolved.

The repo saw this coming: the 2026-07-17 axis evaluation lists as a named risk
"Output divergence at long context can fail C-023-OUTPUT-IDENTITY gates
mid-campaign" (`docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json`,
attention axis, `risks`). The proposal quotes the discipline and then writes a
protocol that guarantees the gate fires. As written, the campaign is
pre-destined to a refusal that teaches nothing about attention.

Second-order: forcing *global* attention on layers **trained** local is
off-distribution. Quality is therefore not matched either — so even if one waived
identity, the contrast confounds "KV traffic" with "degraded model." The D-070
quality-equivalence control is unsatisfiable in this design.

## F3 (MAJOR). The repo already adjudicated this axis and scored it low; the proposal contradicts that record without engaging it.

`docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json`, attention
axis, `summary`: *"The attention-mechanism half is currently weak: no MLA/GQA or
SWA/full pair survives single-axis scrutiny … llama.cpp's `--swa-full` is a
cache-allocation toggle not an attention toggle … **no MLA weight-absorption or
SWA-mask-disable flag was established**"*; enrichment verdict *"low-medium
marginal for attention mechanisms today since C5-1.2/RQ-KV-GROWTH already carry
the context/KV-scaling question."*

And one day before this proposal, `docs/strategy/2026-08-06-impressiveness-roadmap.md`
L146: *"KDA/hybrid comparisons currently involve cross-model confounding and
**unverified long-context execution**"*; L148: *"No tracked repository document
uses 'KDA' as a governed project axis."* The roadmap's rank-7 mechanism slot
costs *"2–3-week desk feasibility gate; if passed, another 6–12 weeks and roughly
2 nights"* and its **recommended first choice is external-draft speculative
decode, explicitly because KDA is confounded.**

A proposal that re-opens a ranked-and-deprioritised axis owes the reader a reason
the prior adjudication was wrong. This one does not cite it at all. Note the
sharpest irony: the *only* readily-available MLX lever, `--max-kv-size →
RotatingKVCache` (`mlx_lm/models/cache.py:410`), is a cache-eviction policy — and
the proposal's own kill criterion says "Never reinterpret a cache-allocation flag
as an attention mechanism." The proposal forbids itself the one thing that works
out of the box.

## F4 (MAJOR). Forking the runtime breaks the pin the custody chain is built on.

There is no SWA-disable flag; the toggle must be a **source patch to
`mlx-lm`**. The proposal's manifest field "runtime commit" acknowledges this in
passing and then treats it as free. It is not: the D-117 acceptance regime, the
issued ledger, admission gates and hash-bound custody all key off the pinned
runtime identity. A patched fork is arguably a different instrument stack
requiring its own calibration acceptance — and a patched attention path is
exactly the "runtime fallback kernels can silently make a subject execute a
different path than its architecture label" failure the axis evaluation names as
a risk. The proposal lists "MLX silently falls back to another cache/kernel" as a
kill criterion but proposes no mechanism to *detect* it beyond a config digest,
which cannot see kernel dispatch.

## F5 (MAJOR). Night budget doubles the paper's cost for a P3 axis.

D-117 funds three windows (3.14 + 3.24 + 2.80 h). This proposal adds **three
more** ("Native-window floor", "Forced-full floor", "Science contrast", each
2.5–4 h) — a 100% increase in Ed's quiet-night spend, plus a new-model admission
program, plus a runtime fork. Under the ratified paper-first priority stack
(P1 MVP, P2 ICPE, **P3 modularity sacrificed if it costs P1/P2**), this is P3
work bought with P1 currency. History says the nights are not cheap: the project
has run windows A and B since 2026-06-09 and **both verdicts FAILED**
(`WINDOW_STATUS.md`), with `CLAIMS_STATUS.md` §1 reading *"VALID — minted,
mainline, citable: **NONE at this checkpoint.**"*

## F6 (MODERATE). Unverifiable citation.

`[H200 attention-energy study](https://arxiv.org/abs/2605.11999)` carries the
load-bearing "up to roughly half of request energy" sizing prior. I could not
verify this identifier; it should be treated as unconfirmed until checked. The
Kimi Linear / Moonshot claims (75% KV reduction, ~6× throughput) are consistent
with the public model card and are correctly labelled as *not* energy
measurements — that part is well handled.

## What is actually good here

- The demotion of the KDA four-way to a matched ablation, with the confound
  named (MoE + MLA + tokenizer + training all move together in Kimi Linear), is
  exactly right and is the single best paragraph in the proposal.
- Contribution 4 ("architecture labels alone do not license attribution") is a
  genuine, publishable methodological point that costs **zero nights**.
- The below-window null as a causal sanity check is a good instinct, correctly
  motivated.
- Venue honesty is broadly consistent with `impressiveness-roadmap.md`'s ladder,
  though "ICPE full-track becomes credible" omits that the roadmap's own ICPE
  full-track row also requires C1–C8, cross-day stability and an artifact-ready
  release — none of which this proposal funds.

## Three strengthening moves if kept

1. **Replace the mask hack with the already-banked context-slope row.** Run
   `RQ-AXI-ATTN-CONTEXT-SLOPE` (registry: fixed-decoded-output decode energy vs
   initial context length, within one named artifact) on the *already admitted*
   Qwen2.5-7B-4bit. This measures the same physical quantity — decode energy as a
   function of KV bytes read — with **no new model, no runtime fork, no
   output-identity contradiction** (outputs are trivially identical across a
   within-artifact sweep of one variable if you hold the prompt prefix and force
   fixed-length greedy decode), and it reuses D-117's admitted model and floors.
   Length is the free lever the brief already identifies. This is the honest
   paper hiding inside the dishonest one.
2. **If the SWA ablation is retained, replace output identity with a declared
   quality-equivalence band and pre-register the divergence.** State up front
   that above-window outputs *must* diverge, measure the divergence (token
   agreement rate, perplexity delta on a held-out set) as a reported covariate,
   and bind the claim to "windowed vs full KV access at matched decode length,
   with quality difference reported" — not to a mechanism claim. Otherwise the
   gate kills the campaign at the desk and the nights are wasted.
3. **Front-load a zero-night desk gate with a hard kill date**, per
   `impressiveness-roadmap.md` rank 7: (a) name one SWA checkpoint and prove it
   loads, converts to 4-bit, and passes the harness admission battery; (b) prove
   the mask toggle changes *dispatched kernels*, not just a config field, with a
   traced execution receipt; (c) time a pilot at both contexts and project the
   effect. If any of (a)–(c) fails, publish the feasibility refusal as
   contribution 4 and spend the nights on D-117. The proposal already gestures at
   this; it should be the *primary* deliverable, not a precondition.

## Bottom line

The submitted design cannot be executed on the admitted stack, and its central
admission gate contradicts its central hypothesis. The good news is that the
scientifically identical measurement — decode energy vs KV traffic — is already
banked, costs no runtime work, and rides D-117's own model. Kill the mask
ablation; fund the context slope.
FILE ../portfolio/rev-batch-concurrency-energy.md
# Counter-review — "Cohort Joules: Defining Honest Energy Boundaries for Batched LLM Inference on Consumer Silicon"

Reviewer: Opus 5 counter-reviewer (adversarial charge: kill it if it can be killed).
Target: `scratchpad/portfolio/prop-batch-concurrency-energy.md` (proposal = final block, lines 7137–7197; an identical duplicate sits at 7074–7136).
Ground truth: `scratchpad/desk` @ main (`89b929c`), verified by two independent repo audits.

## VERDICT: **WEAK** — and KILL as currently framed. Only the rewritten form survives.

The proposal is honest in tone, well-disciplined about D-117, and correctly defers continuous
batching. But three things are fatal as written: the **headline contribution cannot fail**, the
**effect sizing is drawn from the wrong physical regime and is wrong by ~3×**, and the **true cost
is roughly 2–3× the claimed cost** once you count what the repo actually has (which for batch
floors is: nothing, not even a window class that can be expressed). It also produces the one
result class in this project's entire option space where the instrument's distinguishing
capability is irrelevant. The proposal has its own strengths and weaknesses inverted — it hedges
on feasibility (easy) and overclaims on novelty and venue (the actual problems).

## Scores

| Axis | Score | One-line |
|---|---:|---|
| Novelty | **3/10** | Batch-size energy curves are a saturated literature; "no per-request joules under batching" is stated verbatim in ML.ENERGY (NeurIPS D&B spotlight), which then *solves* it. The genuinely uncovered slice (Apple/MLX) is thin and is not what the proposal leads with. |
| Feasibility | **4/10** | The runtime gate is genuinely passed and effects will clear any bar easily — but batch floors are **zero lines of implementation** on top of a floor module that hard-refuses the required window class, plus a mandatory 31-group alias-calibration campaign the budget omits. |
| MVP leverage | **4/10** | Reuses the method sections honestly, but §8 of the MVP draft is the project's *own written argument* for scoping overlapping requests out. And a 30 J effect on a ~47 J baseline needs no detection floor. |
| Venue fit | **3/10** | Workshop-plausible. "Plausible ICPE full-paper component" contradicts the repo's 2026-08-06 roadmap, which enumerates the qualifying deeper contributions (held-out Q4 prediction / second-unit replication / one mechanism study) and does not rank batching anywhere in its top nine. |
| Original goals | **5/10** | Real infrastructure dividend for spec-decode and MoE-by-batch — D-070 cl.3 designed the request-scoped schema for exactly this. But it touches no mechanism, and it consumes the nights the mechanism study needs. |

---

## FATAL FLAWS

### F1. The headline contribution is unfalsifiable by construction — the crux failure

Thesis and Contribution 1 are the **overlap-boundary rule**: report phase energy "only when
request events prove a globally separated prefill/decode boundary." The matching kill criterion
is "cohort phase unions overlap."

That criterion **cannot fire**, for four compounding reasons, all documented in the repo:

1. The design imposes a **prefill barrier** with **sixteen equal-shape requests**
   (`docs/specs/axi/se_analysis_plans_draft.md` §1 `selection_scope`), and the S-B probe
   "freezes a static cohort by inserting all B requests once before the first `next()` … and
   draining the cohort to completion" (`docs/specs/axi/sb_static_batch_verdict.md`). Overlap is
   engineered away before any measurement.
2. `mlx-lm` 0.31.3 prefills the whole cohort in **one batched 2-D forward**: "Prompt processing
   constructs a two-dimensional batch, including right padding … then calls the model with
   `tokens[:, :n_to_process]`. Decode likewise calls the model once with `inputs[:, None]`."
   Live evidence shows `input_shape [2,12]` → `[2,1]` and `[4,13]` → `[4,1]`. With equal-shape
   prompts there is no padding and there are no per-request prefill intervals at all.
3. Most damaging: the same verdict records that the harness "takes a monotonic timestamp when
   each `next()` result returns … and **records the shared return timestamp honestly for
   responses from the same scheduler step**." There are no independent per-request phase edges to
   compare. The "union of prefill intervals vs union of decode intervals" is a test over
   *group-level scheduler-step bookkeeping*, not over physical per-request intervals.
4. The MVP paper already makes this argument, as its own scoping rationale
   (`docs/paper/draft-v1.md:172`): "continuous batching makes an 'active phase' label difficult
   to interpret when requests overlap. JouleWise adopts phase-specific reporting but **restricts
   its primary scope to one sequential request**, where runtime-emitted phase boundaries are
   well posed and can be calibrated." Contribution 1 is the MVP paper's *limitation sentence*
   promoted to a finding.

So the flagship contribution validates the harness's own accounting against a case constructed to
satisfy it, and the interesting case — real overlap under continuous batching — is explicitly
deferred to "a later paper." A referee will call this a tautology dressed as a rule. **This alone
prevents any rating above WEAK.**

### F2. Effect sizing uses the wrong reference class, a voided number, and lands ~3× low

The proposal projects a "cautious 5–30% per-request reduction (~2.5–15 J)" and concludes "**B=2
may not clear 5 J**, B=4 is uncertain," sourcing this from "datacenter literature reports roughly
a 25% energy/token reduction over a much larger batch range."

Wrong regime. Datacenter batch curves are measured on GPUs already compute-saturated; the cited
25% is the *flat* part of their curve. An M3 Max running Qwen2.5-1.5B-4bit at B=1 is deeply
**memory-bandwidth-bound and grossly under-utilized** — decode reads ~0.8–1 GB of weights per
token per sequence, and batching amortizes that read across B sequences nearly for free.

Independent evidence: *Native LLM and MLLM Inference at Scale on Apple Silicon* (arXiv 2601.19139,
M4 Max 128 GB) measures **3.7–4.3× throughput at 16 concurrent requests**. If power rises ~1.3×
while throughput rises ~4×, per-request decode energy falls **~65–75%** — from ~47 J to ~13–17 J,
an effect of **~30–35 J**, i.e. **6–7× the ~5 J phase bar**. Even B=2 should show ~15–20 J.
*(Flagged: that throughput figure is a different model on a different chip and the power factor is
my inference. The sign and order are not in doubt, and the proposal's own "group-gross differences
should be much larger" concedes the mechanism.)*

Two consequences, the second worse than the first:

- The "cautious" posture and several kill criteria are mis-sized; "B=2 may not clear 5 J" is very
  likely a false-negative call that could kill the project's best cell for the wrong reason.
- **The paper does not need this instrument.** JouleWise's thesis is that detection floors and the
  attribution limit decide what may be claimed. A ~30 J effect on a ~47 J baseline is visible to a
  stopwatch and a wall plug. Scalpel, tree trunk.

Compounding compliance point: the ~47–50 J sizing input is **permanently VOIDED for claim use**
by D-078 (`PROJECT_STATUS.md:381`, `README.md:69`). The proposal calls it "the old … diagnostic"
but never says voided. Sizing an MDE off a voided corpus is exactly what D-078 forbade.

### F3. True cost is roughly 2–3× claimed, and the priority case is never made

The proposal budgets "**three additional quiet nights, possibly four**" beyond D-117's three, and
folds the batch floor *and* the 93-group three-block pilot into one window. Every load-bearing
piece of that is missing from the repo:

- **No batch adapter exists.** `joulewise/adapters/mlx_runtime.py` contains the string "batch"
  **zero times**. The only `static_batch` producer is the mock (`mock_spec_runtime.py:194`). Queue
  row `A4 / AXI-SB-ADAPTER` is `READY` — i.e. unstarted. *(The proposal does say "the required
  adapter is not yet implemented" — credit.)*
- **The floor module cannot express a batch window at all.** `joulewise/detection_floor.py:227–239`
  hard-raises on any `window_class` outside `("request","phase")`, and `batch_group_gross_energy_j`
  is absent from `FLOOR_METRIC_CATALOG`. Grep for `Sigma_F` / covariance machinery across
  `joulewise/`: **zero hits**; `detection_floor.py` is scalar-only.
- **A dedicated calibration campaign is mandatory, not optional.** AP-BATCH's floor gate: "accept a
  group calibration only if it covers **every B's** unioned window semantics, duration/cadence/drift
  range and supplies the joint `Sigma_F`; **a scalar single-request floor alone refuses** … If any
  required covariance, bound, B, or nonlinear denominator support is absent, **a dedicated 31-group
  same-design alias calibration is mandatory; otherwise this AP does not execute.**" And: "There is
  no fallback transport that always accepts."
- **The inherited hours exclude that calibration.** The ~3 h / ~5 h figures are not from AP-BATCH;
  they are from `docs/phase_2/splitwise_replication_roadmap.md` (2026-07-19), whose own row already
  warns "group-level floor/covariance path (**single-request floors do NOT transport**)". *(The
  proposal does flag these as uncertain historical estimates — credit — but then budgets from them
  anyway.)*

Realistic total: **four to six nights**, plus a from-scratch floor/covariance subsystem, plus an
adapter, under a fail-closed protocol where a refused window costs the whole night
(D-079 rationale: "it costs a whole quiet window per occurrence and window time is the project's
scarcest physical resource").

Now the priority arithmetic the proposal never does. The 2026-08-06 roadmap recommends **5–7
Ed-present sessions** total, 8–10 for an ICPE-full attempt, and concludes: "The strongest realistic
paper is … C1–C8 metrology + the already-collected 1.5B/7B demonstration + **one designed extension**
+ an independently usable artifact" — with the shortlist for that one slot being held-out Q4
prediction, quantization, or one mechanism study. D-117's three nights plus this proposal's four-to-six
consumes the entire ICPE-full budget on an axis that **appears at no rank in the roadmap's nine**.
(The only batch-adjacent phrase there is rank 7's "batch-**1**" speculative decode — that means the
*single-request* condition, not batching. Do not let it be read as support.) Rank 1's decision line
is explicit: "Reserve the core nights now and **prohibit breadth work from consuming them**." Under
Ed's paper-first stack (P1 MVP, P2 ICPE, **P3 sacrificed if it costs P1/P2**), this is P3 work
eating P1/P2 nights, and the proposal argues neither side of that trade.

### F4. Existing-material compliance gaps

- **"the existing AP-BATCH design"** — it is `AP-BATCH-**DRAFT**`, in a file headed "**DRAFT — design
  only; no campaign authority**", plan state "**PROVISIONAL pending P2-015 Window-A floors**", last
  edited 2026-07-15, owning queue row `A7 / AXI-SE` still `READY`, every number literal-marked
  `PROVISIONAL-UNTIL-P2-015-AND-PILOT-BATCH-V1`. P2-015 floors do not exist: `CLAIMS_STATUS.md` §1
  reads "**NONE at this checkpoint.**" The proposal's desk list does say "AP-BATCH finalization after
  the pilot," so this is overstatement rather than fabrication — but a reader budgeting nights off
  this text will think a frozen plan exists.
- **"authorized by D-070"** overstates it. D-070 cl.3 authorizes *scope and schema shape*; cl.2 holds
  that "every AP remains floor-gated on P2-015 floors … and no AXI stream consumes a [QUIET-MAC]
  window until Window A completes"; cl.5 caps everything at L2 with "no live claims from
  fixture-first code." No campaign authority was granted.
- **Contribution 4 is already repo doctrine.** AP-BATCH's metric row already states "**No overlapping
  group energy is divided among requests.**" Presenting the design constraint as an empirical finding
  is circular.
- **The claim-bearing phase work is unauthorized and unbudgeted.** AP-BATCH: "Gross phase-window
  energy is a **descriptive L1 audit** unless a later registry enumerates a phase family."
  Contributions 1–2 need a newly minted phase family, its own Holm denominator, and a phase-specific
  floor route. None appears in the desk list or the night budget.
- **C5-2.2 is never named.** The row this paper consumes carries the binding caveat "*no serving
  conclusion without latency-bound policy*." Its Mac leg *is* minted (2026-07-16, in
  `docs/research_question_bank.md`, per D-070 cl.4's mint-on-`supported` rule) — but the proposal
  cites neither the row, its caveat, nor D-070's requirement that these axes be framed as **stress
  tests of the single Q4 thesis, "not five new theses."** The proposal gives batching its own thesis.
- **Multiplicity is never mentioned.** AP-BATCH runs a seven-hypothesis Holm family for model
  selection, a separate denominator for normalized energy, and eight two-sided latency hypotheses —
  at draft `n_blocks=5`. That is where the statistical risk actually lives.
- **D-117 licenses no new axes.** Its only fenced extensions are the ≥256-token prefill arm (Ed's
  open option, "not adopted here," ~110 core min, "likely its own window") and Option 1 historical
  candidacy as a contingency requiring a rule-11 cold gate. Three severity-`blocker` desk items
  (F1/F2/F3 in the design memo) plus live night-stranding defects (L4, L5, R6) stand before the
  first D-117 arm runs.

*(One overreach I checked and did **not** find: the proposal does not claim the token-normalization
contract needs re-issuance, and correctly so — `docs/contracts/token_normalization.md:137` already
requires batch/concurrency policy disclosure as "Always applicable.")*

### F5. Contributions 3 and 4 contradict each other

C3 promises "gross joules/request" and "joules/output-token." C4 declares that "physical energy
remains identifiable only at cohort level" and that "no equal-share allocation is presented as
measurement." Both C3 metrics *are* cohort energy divided by a request or token count.

AP-BATCH resolves this and the proposal does not: dividing a **complete 16-request block partition**
by exactly 16 is legitimate *by symmetry of the design* (`BATCH-JREQ-B<value>-VS-B1`), whereas
allocating a single overlapping group window among its members is not. As stated, "an empirical
limit on per-request energy" is simply wrong — with sixteen identical equal-shape requests the
symmetric mean **is** the correct per-request estimator, and refusing it would be a metrology error
dressed as rigor.

### Minor

- The B=16 memory-fit kill criterion is near-empty. Measured marginal cost is **~33 MB per added
  sequence** (B=2 peak 968.7 MB → B=4 peak 1,034.4 MB); B=16 extrapolates to ~1.43 GB on a machine
  that has absorbed a 68.9 GB peak (Qwen3.5-122B-A10B-4bit run). D-070 cl.3's own rationale says "a
  single model instance with B KV caches is **memory-feasible on current hardware**." Fair as an
  untested-cell check; not a kill, and it must not be used to justify a smaller grid.
- "This intentionally extends the frozen single-request boundary, but does not alter or contaminate
  the D-117 campaigns" is the right sentence — and it is the only place the extension is priced. It
  prices *contamination* risk correctly (~zero) but never prices the *authorization* cost: the new
  phase family, the new floor window class, the AP freeze.

---

## What the proposal gets right (credit where due)

- Correctly defers continuous batching per D-070 cl.3, and names *why* (arrival traces, steady-state
  detection, scheduler policy, offered-load) rather than gesturing.
- Correctly refuses looped-singleton dispatch, matching AP-BATCH's inclusion rule and the S-B
  verdict's `unsupported_for_joulewise(native_batch_execution)` code.
- Correctly states that single-request floors do not license batch claims and that the ~5 J bar is
  only a planning proxy here. This is the sharpest sentence in the document, and it is consistent
  with D-078 cl.11 / D-083, which scope that bar to *phase contrasts on single-request windows* and
  provide no bar for any other estimand.
- Correctly rules the borrowed WT310E a non-dependency, for the right reason (validates totals, not
  allocation) — matching the roadmap's own C8 row and D-092.
- Correctly protects D-117 as non-negotiable, and reproduces its 3.14 / 3.24 / 2.80 h budgets and
  six-item desk list **faithfully** (independently re-verified against the design memo, including
  the arithmetic).
- Honest that the adapter does not exist and that the inherited hour estimates are stale.
- Kill criteria are mostly real, pre-committed, and desk-checkable — except the one that matters (F1).

---

## THREE STRENGTHENING MOVES (if kept)

**1. Re-center the thesis on the *shape* of E(B), not on the boundary rule.**
Make the primary claim AP-BATCH's *existing* primary family — the affine slope and the three
lack-of-fit curvature contrasts `d_1,d_2,d_3` — and ask what the datacenter literature structurally
cannot answer: **where is the amortization knee on a memory-bandwidth-bound consumer SoC, and is the
departure from affine resolvable above the floor?** Curvature contrasts are small differences of
large numbers; unlike the J/request curve, they *are* floor-sensitive, which makes the instrument
load-bearing again and turns the paper into the Q4 stress test D-070 actually asked for. Retitle
accordingly; demote the overlap rule to a two-paragraph methods subsection.

**2. Replace Contribution 1 with a negative control that can actually fire.**
Pre-register a deliberately **ragged cohort** — unequal prompt lengths (triggering `mlx-lm`'s right
padding) or staggered admission at B=4 — and show the validator *refusing* the phase split there
while *accepting* it under the equal-shape barrier. That is the only version of the boundary claim a
referee will accept; it is falsifiable; it costs desk time plus a slot inside the pilot rather than a
new claim night; and it yields the paper's one genuinely publishable refusal. If it cannot be built
on a shared-scheduler-step timestamp surface — and the S-B verdict suggests it cannot — **drop the
boundary claim entirely** and say so in print.

**3. Re-price honestly, and force the head-to-head before a single night is committed.**
(a) Build the A4 adapter and run the group ladder **off-window** on the unquiet machine to produce a
real occupancy number, replacing the 2026-07-19 inherited estimates. (b) Scope the batch-floor
subsystem explicitly as what it is — a new `detection_floor` window class, a `Sigma_F` covariance
implementation, and a 31-group alias-calibration campaign — and put *that* on the night ledger, not
just the pilot. (c) Write the ledger against roadmap ranks 1, 2 and 3 (remint / C8 wall meter /
artifact release) and state in writing which Ed accepts delaying; the roadmap's "one designed
extension" slot has a shortlist and batching is not on it, so that omission must be argued *with*,
not around. (d) If the lack-of-fit family cannot be powered at `n_blocks=5` under Holm-7, **shrink to
B ∈ {1,4,16}** — three well-floored cells beat five unresolvable ones, and the knee is still
locatable. Bind the limitations section to C5-2.2's existing "no serving conclusion without
latency-bound policy" wording, and re-derive the sizing input from D-117's fresh floors rather than
the D-078-voided ~47 J corpus.

---

## Novelty evidence (external)

| Work | Overlap | Why it hurts |
|---|---|---|
| ML.ENERGY Benchmark (arXiv 2505.06371; NeurIPS D&B spotlight) | Direct | States Contribution 4 verbatim: batching makes "the energy consumption of a single request dependent on all other requests being processed at the same time." It then *solves* it with a steady-state accounting method. The proposal's answer is to refuse — weaker than the state of the art, not stronger. |
| "Where Do the Joules Go?" (arXiv 2601.22076) | Direct | 1,858 configurations with batch-size sweeps, static-power accounting, causal knob→latent-factor→energy framework. Already in the repo's related work. |
| TokenPowerBench; SweetSpot (2602.05695); vLLM energy benchmarking (2509.08867); Bench360 | Direct | Batch-size energy curves are a crowded, actively published space. |
| *Silicon Showdown* (arXiv 2605.00519) | Partial | Apple M3 Ultra + RTX 5090, `powermetrics`, tokens/joule, prefill/decode separated — but **batch size 1 only**. Half the gap. |
| *Native LLM/MLLM Inference at Scale on Apple Silicon* (arXiv 2601.19139) | Partial | Continuous batching on MLX, 16 concurrent, M4 Max — but **no energy measured at all**; energy profiling listed as future work. The other half. |
| `ml-energy/zeus-apple-silicon` | Reviewer question | Sub-millisecond per-rail IOKit energy counters on Apple Silicon. A referee *will* ask why the attribution limit is accepted rather than instrumented away. The repo has the rebuttal (`docs/run_reports/2026-07-30-sweep-cv-paths.md`: 8 stars, README "explicitly disclaims accuracy… no calibration, no error bars, tests use mocked data") — **but the proposal does not carry it**, and this paper needs it far more than the MVP does. |

Net: the honest uncovered slice is "phase-resolved energy vs static batch size on Apple
Silicon/MLX, with floors." That is real and narrow — a workshop paper. The proposal instead leads
with the boundary rule, which is the *least* novel and *least* testable thing in it.

---

## Bottom line

Do not fund this as a paper. In its current form it spends four-to-six quiet nights — plus an
adapter and a floor/covariance subsystem that do not exist — to measure a large, well-known effect
with an instrument whose distinguishing capability the measurement does not need, and to prove a
boundary rule its own design cannot violate, on an axis the project's own strategy document does not
rank.

Fund it only in the rewritten form (a Q4 shape-of-E(B) stress test with a falsifiable ragged-cohort
refusal control, re-priced, with an explicit written trade against roadmap ranks 1–3) and only
**after** the MVP lands and the roadmap's single "designed extension" slot has been spent on
something from its own shortlist. Until then, the correct disposition is: build the A4 adapter as
desk work — it is cheap, it is already queued, and it is the infrastructure D-070 cl.3 wanted for
speculative decode — and spend no quiet nights on batching.
FILE ../portfolio/rev-contamination-characterization.md
# Counter-review: "Quiet Is a Measured State" (prop-contamination-characterization)

Reviewer: Opus 5, counter-review pass. Charge: kill it.
Ground truth: `desk/` @ main. Every number below was checked against primary repo bytes.

**VERDICT: WEAK** (one notch from KILL; survives only in the shrunken forms in §Strengthening).

| axis | score |
|---|---:|
| novelty | 3 |
| feasibility | 3 |
| mvp_leverage | 6 |
| venue_fit | 4 |
| original_goals | 2 |

---

## What is actually right (stated first, because it is unusual)

The arithmetic is clean and I could not break it. `0.1923 W` mean, between-capture
SD `0.0008 W`, max `6.74–7.47 W` reproduce exactly from
`docs/process_traces/2026-08-04-t3-char-pair/ANALYSIS-APPUP-R01R02.md`. The
screensaver figure (`43/50` bundles, `~+30%` energy) reproduces from
`RUN_STATE.md:2118-2119` and `PROJECT_STATUS.md:376`. `5 J / 93 s = 0.054 W` and
`0.1923 W × 93 s ≈ 18 J` are both correct. The proposal correctly refuses to use
the n=2 permanently-non-claim captures as claim evidence, correctly says no wall
meter is needed, and correctly declines to divert the D-117 windows. The
guard-confusion-matrix idea (contribution 3) is the one genuinely novel item in
the document.

That is the whole of the good news. The design does not survive contact with the
project's own rules.

---

## Fatal flaws

### FF1 — The window as specified cannot produce a claim-bearing result. Its own project would refuse it.

The design is 12 Williams-balanced epochs, 3 per state, 2 members per epoch:
**6 LLM observations per cell, and at most 3 paired contrasts per state-pair.**

`docs/paper/draft-v1.md:78`, the project's own floor rule:

> "fewer than five valid bundles or blocks are treated only as development
> evidence, not as a claim gate."

Three blocks is below five. The comparative side of every state contrast — the
side that carries the entire thesis — is *development evidence by the paper's own
§4*. The absolute side (n=6) clears the threshold by one and still eats the
pre-registered small-sample guard factor. Compare the ratified standard: D-117
alpha/beta/gamma each run **10 absolute + 10 ABBA blocks**
(`DESIGN-MEMO.md:246-263`). To reach that standard across four states you need
4 × (10 + 40) = 200 members, i.e. **four-plus windows, not one**. The proposal's
"approximately 3.4 h" is understated by roughly 4×.

This is not a tuning quibble. The proposal asks Ed to spend a night on a design
that his own §4 will classify as non-claim-bearing before the data is reduced.

### FF2 — There is no floor for the condition family this paper needs, and the proposal never notices.

The `~5 J` bar the whole Experiment Plan is sized against is the **phase-contrast**
effective bar, `F_cell + B_claim`, for `phase_energy_j.decode` on the 1.5B stack
(`draft-v1.md:109-115`). An environment-state contrast on gross member energy is a
**different condition family**. The project's rule is explicit and repeated:

- `draft-v1.md:60` — a floor governs "the same telemetry backend, metric, window
  type, workload profile, and stack identity. One such family forms a measurement cell."
- `DESIGN-MEMO.md:366` — "Never sum components and **never borrow a decode floor
  for prefill**." If a decode floor cannot transport to prefill on the *same
  members*, it certainly cannot transport to a new environment-state estimand.

So the contamination cells need their own minted absolute and comparative floors —
which requires null-ABBA members for an `env_state_contrast` family that appear
**nowhere in the proposed member list**. The list carries 12 NEG-8 bound members
(the bracket-drift corpus, not a floor) and 7 references. Either the headline
result has no decision bar at all, or a second window's worth of floor members
must be funded. This is the single largest cost omission in the document and it is
completely silent.

### FF3 — This is not an operator-bookend window. It needs Ed awake, or an unbuilt controller plus a rule waiver.

Twelve within-window state transitions, three of them into cell A (**app DOWN**).
The repo's own protocol for that exact transition
(`2026-08-04-t3-char-pair/PROTOCOL.md`, §Design):

> "Arm B (app-DOWN), collected **with Ed present** ... Arm B is deliberately NOT
> collected unattended tonight: quitting t3 would kill Ed's own observation
> threads, and the app-death-recovery acceptance gate wants Ed present for the
> quit/relaunch."

Cells C and D are worse. C requires *starting an agent session inside a
measurement window*; the repo's binding rule (`CLAUDE.md`, enforcement boundaries)
reads "Never start or continue a `[QUIET-MAC]` measurement while an agent session
is active." Treating the agent as a deliberate treatment is scientifically
defensible, but relaxing that boundary is a ratification act, not a design choice
— and under CLAUDE.local.md rule 11 the lieutenant is forbidden to self-exempt
from a mandatory trigger. The proposal's one-line "detached state controller" is
QUIET-GUARD-01 (still unbuilt, named as unbuilt in the very PROTOCOL it cites,
limitation 1) plus a detached agent-session launcher plus 12 supervised process
transitions with identity custody. None of it is costed.

Add the settle time the proposal omits: the project's convention is a 180 s settle
after operator/stage activity (`draft-v1.md:151`, `DESIGN-MEMO.md:309`). Twelve
transitions × 3 min = **36 min** that does not appear in the 3.4 h figure. With
FF1's member count and FF2's floor members, the honest number is 3–4 nights.

### FF4 — The novelty is folklore that the literature already formalized.

"Background software corrupts measurements" is not an open question; it is the
premise of every energy-benchmarking standard and the subject of an active
methodology literature. Standard controls are documented and in use: freeze all
non-essential cgroups so only workload and sampler run; subtract idle energy;
randomize/shuffle run order against unnoticed background processes; CPU warm-up
against thermal confounders. Recent work does exactly the framework version of
this ([METRION: A Framework for Accurate Software Energy
Measurement](https://arxiv.org/html/2512.06806); [Measuring Software Performance
on Linux](https://arxiv.org/pdf/1811.01412)), and there is already a paper whose
entire subject is the energy cost of a background feature ([Toward Greener
Background Processes](https://arxiv.org/pdf/2509.11738)). MLPerf Power/SPEC make
environment control an *admission condition*; JouleWise's own `draft-v1.md:125`
already encodes it as an admission gate.

What is left after prior art is: *a macOS-specific numeric budget for one laptop
with one app resident*. That is a paragraph, honestly. Formalization earns
publication only when it changes practice — and the proposal's own contribution 4
anticipates the likely landing as "retain zero-agent operation with a measured
reason," i.e. **no practice change**.

### FF5 — The expected result is "the obvious things are big, the interesting thing is unresolved."

Sort the four cells by (decision relevance × uncertainty):

- **B (dormant app delta)** — the only cell whose answer is both unknown and
  decision-relevant. The proposal itself says its increment over app-down "is
  unknown and may not clear 5 J." Most likely outcome: *unresolved*.
- **C (idle agent)** — largely known already. D-099 puts an idle-waiting session
  at 12–18% CPU of agent load; the banked analysis (`ANALYSIS-APPUP-R01R02.md:49-52`)
  already calls active streaming "two orders of magnitude over the effective bar."
- **D (transcript replay)** — the proposal predicts order-one watts, i.e.
  hundreds of joules. Nobody doubts this. Worse, D is a **proxy**: frozen-rate
  transcript replay is not an agent, so the paper's "background software"
  characterization for the agent regime rests on a simulacrum.

So the modal paper is: two cells confirm the obvious at 100× the bar, one cell
returns "not resolvable," one cell measures a stand-in. The proposal is admirably
honest that "unresolved is a valid outcome" — but you cannot *build* a paper on the
likelihood that its central quantity is unresolvable.

## Non-fatal but worth recording

- **Existing-material compliance is thin on registration.** `docs/research_question_registry.md`
  has no background-contamination RQ; its "contamination" rows (C5-2.5d) are
  *dataset* contamination. The nearest environment RQ is `RQ-POWER-MODE`, banked,
  "analysis-plan-only." D-117 is adopted; this is not registered anywhere.
- **Minor misreport:** proposal says p95 "approximately 0.46–0.48 W"; banked values
  are 0.463 / 0.484 W. Rounding down the top edge in a paper about tails is a bad habit.
- **Roadmap collision.** `docs/strategy/2026-08-06-impressiveness-roadmap.md` ranks
  nine expansions. This direction is not among them, and rank 1 is an explicit
  instruction to "prohibit breadth work from consuming" the core nights.
- **Venue arithmetic.** CSCSU is **5 pages including references**. There is no
  world in which the MVP method + D-117 results + a four-state contamination study
  fit in five pages. The proposal's "capstone paper/chapter" glosses this.

---

## Three strengthening moves

1. **Make it desk work, not a night — and the corpus is already being collected.**
   Every D-117 member carries its own idle capture (lifecycle stage 4,
   `raw/powermetrics_idle.plist` + `rich_telemetry_idle.jsonl`). Three windows
   × 203 captures gives an in-custody, claim-adjacent idle corpus for free.
   Compute the empirical distribution of *asymmetric burst energy* over real
   93 s member durations and publish `P(asymmetric burst > 1 J)` and `P(> 5 J)`,
   plus the same statistic recomputed on the banked n=2 app-up pair as an
   out-of-family cross-check. Zero new nights, zero new floors, zero rule waivers,
   and it is the paper's actual contribution — the burst-asymmetry budget — rather
   than its ceremony.

2. **If a window is funded, fund exactly two states at the ratified standard.**
   A (app-down) vs B (app-up dormant), 10 absolute + 10 ABBA blocks, with a
   pre-registered `env_state_contrast` condition family carrying its own null
   members and its own minted floor. One question, properly powered, with a real
   decision bar. Drop C (answer already known) and D (a proxy) entirely — they buy
   nothing and they are what force the agent-session rule waiver and the
   detached-controller program.

3. **Reframe the headline onto contribution 3, which is the only novel item.**
   Not "background software contaminates measurements" (settled) but *"how good is
   an admission gate?"* — false-accept and false-refuse rates of JouleWise's §5
   quiet-state guard against prospectively labelled environment states. That is an
   instrument-validation result about the project's own machinery, no prior work
   reports it, it is cheap, and a false-accept above the bar would be a genuinely
   publishable negative finding about §5 rather than a restatement of the field's
   standing assumption.

---

Sources: [METRION: A Framework for Accurate Software Energy Measurement](https://arxiv.org/html/2512.06806) · [Toward Greener Background Processes — Measuring Energy Cost of Autosave Feature](https://arxiv.org/pdf/2509.11738) · [Measuring Software Performance on Linux](https://arxiv.org/pdf/1811.01412)
FILE ../portfolio/rev-cross-runtime-contrast.md
# Counter-review: "Same Silicon, Different Stack: Floor-Gated MLX–llama.cpp Inference Energy on an M3 Max"

Reviewer: Opus 5, counter-review lens (charge: kill it). Ground truth: `scratchpad/desk` @ main.

## VERDICT: **WEAK** — do not fund as a paper.

Scores (1–10):

| Axis | Score |
|---|---:|
| novelty | **3** |
| feasibility | **3** |
| mvp_leverage | **5** |
| venue_fit | **4** |
| original_goals | **3** |

Recommendation: demote to a 0-night desk note, or fold the artifact-parity
machinery into the already-ranked quantization-ladder axis (roadmap rank 5),
which needs the same conversion-provenance work and already carries a quality
gate. Do not spend the two (really three) nights.

The proposal is honestly written and self-aware — it flags its own confound and
its own ICPE ceiling. It is not incoherent. It is *dominated*: every night it
spends buys a result the project's own registry has pre-capped at L2
stack-vs-stack, at a moment when P1 is an unwritten MVP paper.

---

## FATAL FLAWS

### F1. The effect-size arithmetic is calibrated against the wrong floor — off by ~3×.

This is the flaw that kills the experiment plan as written.

The proposal sizes everything against "the ~5 J bar": 3 % = 5.77 J, 5 % =
9.62 J, "difficult only when the stacks are within roughly 2.6 %", and a
pre-night kill criterion at **7.5 J**.

But the ~5 J number is the project's *generic* statement of attribution-limited
sizing (`CLAIMS_STATUS.md` §1: "floor + claim-side bound ≈ 5 J"), and the
proposal's own primary cell is **7B decode**, whose measured diagnostic floors
are (`CLAIMS_STATUS.md` §2, `window_7bfloor_20260729`):

- absolute **6.294380135190098 J**
- comparative **13.998036715259254 J**

`docs/paper/draft-v1.md` §"detection floor": the cell's operative floor is the
**maximum** of the two → **≈ 14.0 J**, not 5 J. `DESIGN-MEMO.md` line 450
confirms the contrast gate resolves "both decode arm floors … and appl[ies] the
armwise maximum" — and one of this proposal's two arms is a 7B decode cell.

So the real bar is:

| Bar | J | as % of the 192.39 J 7B decode cell mean |
|---|---:|---:|
| proposal's assumed bar | ~5 | 2.6 % |
| proposal's pre-night kill threshold | 7.5 | 3.9 % |
| **actual applicable armwise floor (diagnostic)** | **~14.0** | **7.3 %** |
| floor + claim-side interval margin (cf. prefill synthesis half-width ~1.81 J) | **~16–18** | **8–9 %** |

Every number in §"Experiment plan" is therefore wrong in the direction that
matters. A 3 % stack difference does **not** clear. A 5 % difference does
**not** clear. The proposal's own gate ("kill if the pilot's conservative lower
estimate is below 7.5 J") would *pass* a study that is then guaranteed to be
refused at the floor gate after burning two quiet nights. That is precisely the
failure mode this project exists to prevent, committed inside a proposal whose
thesis is floor discipline.

Fixing this is not cosmetic: it forces the honest question "do MLX and
llama.cpp-Metal differ by ≥8 % in batch-1 decode energy at 7B/4-bit?" — and the
answer to that is F2.

### F2. The only effect size large enough to clear the floor is the size the artifact mismatch alone can manufacture.

The charge asked whether "same model artifact class" is well-posed. It is not,
and the failure is quantitative, not philosophical.

Batch-1 decode on unified memory is bandwidth-bound: energy tracks bytes moved
per token. The two arms do not move the same bytes.

- MLX 4-bit (default group_size 64, fp16 scale+bias): ≈ **4.5 bits/weight**.
- GGUF **Q4_K_M**: ≈ **4.8–4.85 bits/weight** average (Q6_K promotion on
  attention-output / FFN-down and higher-precision embed/output tensors).
- Realized 7B file sizes: MLX-4bit ≈ 4.2–4.3 GB vs Q4_K_M ≈ 4.6–4.7 GB.
  *(Flagged: from public artifact listings, not measured here — but the
  direction and rough magnitude are robust.)*

That is a **~7–9 % difference in weight bytes**, sitting exactly on top of the
~8 % effect the floor requires. A cleared result is therefore
**unidentifiable**: "llama.cpp uses 9 % more decode energy" and "Q4_K_M carries
9 % more weight bytes than MLX-4bit" are the same sentence. The paper's headline
number would be a quantization-format result wearing a runtime costume.

The escape routes both fail:

- Match bits-per-weight with **Q4_0** (4.5 bpw): now the arms differ in
  quantization *algorithm* and quality, and Q4_0 is a strictly worse quantizer —
  you have swapped a byte confound for a quality confound.
- Match quality with Q4_K_M: byte confound restored.

There is no GGUF quantization that is simultaneously byte-matched and
quality-matched to MLX 4-bit. The contrast is **structurally confounded at
exactly the effect scale it needs**. Contribution 4 ("keep the wording
'MLX-stack versus llama.cpp-stack'") is a *labelling* fix for an
*identifiability* problem. It renames the confound; it does not remove it.

And the project already knows this. `docs/research_question_bank.md` C5-1.8:
"where formats force different artifacts (MLX vs GGUF), the comparison is
stack-vs-stack, stated as such." `docs/research_question_registry.md` line 68 and
lines 128–131 set the ceiling at **L2 stack-vs-stack** and *forbid* "belongs to
the runtime" language. So contribution 4 is not a contribution — it is the
pre-existing guardrail on a pre-existing registry row, restated.

### F3. No quality gate — the project's own standard for cross-artifact energy comparison.

`docs/strategy/2026-08-06-impressiveness-roadmap.md` rank 5 (quantization
ladder) requires "one frozen source revision, reproducible conversions, **256-item
quality gate**, 32-item energy subset, stack-specific floors" — for comparisons
*within* one runtime across BF16/Q8/Q4. This proposal compares across two
runtimes *and* two quantization schemes with **zero** quality evaluation; its
only nod is "quantify output-token divergence," i.e. counting how much the
strings differ, which is not a quality measurement.

Worse, `docs/paper/related_work_draft.md` criticises Silicon Showdown for
exactly this: "unmatched runtimes and precision stacks and **no comparison of
model-output accuracy**." As written, this paper reproduces the flaw it
indicts, with a floor bolted on. A referee who has read the project's own
related-work section will make that observation in one sentence.

`C-023-OUTPUT-IDENTITY` (registry line 103) is explicit: "no quant/**runtime**
efficiency claim without equivalence or divergence report," and "fixed
output-token count is not fixed decoded work." The proposal fixes the output cap
at 512 and calls that parity. It isn't.

### F4. No llama.cpp adapter exists, and the desk estimate is off by roughly 2×.

`joulewise/adapters/` contains `mlx_runtime.py`, `vllm_runtime.py`,
`mock_runtime.py`, `mock_spec_runtime.py`, telemetry and transport modules —
**no llama.cpp anything**. `RuntimeBackend.LLAMA_CPP` exists in
`joulewise/schemas.py:211` as an enum value only; `adapters/__init__.py
resolve_runtime()` falls through to
`RUNTIME_UNAVAILABLE: "runtime backend 'llama_cpp' has no registered adapter"`.
The enum is a placeholder, not a capability. The proposal says "new harness work
is substantial but bounded" — the word doing the work there is "bounded," and it
is unsupported.

Scale reference: `mlx_runtime.py` is **1246 lines**, and the phase boundary it
emits is `phase_boundary_method: "first_token"` — a marker planted *inside* the
Python generation loop, monotonic-clock-stamped, aligned to the powermetrics
anchor, with prefill/decode `phase_start`/`phase_end` `RuntimeEvent`s and
item-level control/failure semantics. A llama.cpp arm must reproduce all of it
against a C API (or `llama-cpp-python`), plus Metal build provenance, plus
`docs/contracts/adapter_contracts.md` conformance, plus tests.

Then the *campaign* machinery. `DESIGN-MEMO.md` §units enumerates **U1–U10** of
desk work — successor bracketing engine, pinset schema v2, multi-cell mint,
three campaign packs, extraction specs, post-collection pin closure — for
D-117, which adds **only prefill riders to existing MLX plans on an existing
adapter**. This proposal needs all of that *again* for a second stack identity,
plus the adapter itself, plus conversion manifests, plus "multi-runtime
floor/contrast consumers." "2–4 weeks of desk engineering" is not credible; 6–10
weeks is the honest range, and it is 6–10 weeks of the same desk capacity P1
needs.

### F5. The night budget is wrong: it is three new nights, not two — by the proposal's own protocol.

The proposal's own artifact-parity protocol (contribution 2: "both arms must
share the upstream checkpoint revision") requires deriving the MLX artifact from
the same source revision as the GGUF. But the D-117 windows pin a **prebuilt
mlx-community artifact** with its own revision hash (see
`configs/examples/mac_mlx_local.json`: source
`.../mlx-community/Qwen2.5-7B-Instruct-4bit`, `revision` pinned;
`DESIGN-MEMO.md` line 208 pins "Exact Qwen2.5-7B stack identity"). A locally
re-converted MLX artifact is a **different stack identity** → a different cell →
the D-117 7B floor does not transport → you must mint a fresh MLX floor too.

That is the proposal's own listed kill criterion ("D-117's MLX floor cannot
legally transport to the exact contrast cell") — and its own plan *guarantees*
the trigger. Either:

- keep the prebuilt MLX artifact (D-117 floor transports, but "same source
  revision" parity is nominal — mlx-community's conversion settings are not
  recorded, so contribution 2 is unenforceable), **or**
- re-convert (parity real, but **3 new nights**: MLX floor + llama.cpp floor +
  contrast).

Either branch breaks a headline claim. The stated "five quiet nights total" is
the optimistic branch of a dilemma the proposal doesn't notice it has.

### F6. Silent on the residency/warm-cache asymmetry that makes the floors non-transportable.

The two floor windows are single-runtime-resident. The ABBA contrast window
alternates MLX and llama.cpp members. Two options, both bad, neither addressed:

- **Both resident**: ~9 GB of weights held simultaneously plus two process
  memory footprints. That is a different environment — different idle baseline,
  different memory pressure, different thermal state — from the single-resident
  floor windows that minted the floors being transported in. Floors are cell-
  scoped on "telemetry backend, metric, window type, workload profile, and
  **stack identity**" (`draft-v1.md` §detection floor). A dual-resident window is
  not the cell the floor was minted for.
- **Tear down and reload between members**: injects model-load energy and
  thermal transients inside the claim window and violates the frozen "warm
  model" boundary the proposal explicitly promises to preserve.

D-117's gamma window does swap models within one MLX process, so there is
precedent for *model* swapping — but not for *process/runtime* swapping, which
is strictly harder and adds a variance source that neither arm's within-stack
null block measures. Which brings the last point: the "maximum of the two decode
floors, never their sum" rule is (a) **not a contribution** — it is verbatim
existing doctrine (`DESIGN-MEMO.md` line 481: "Ensure gamma takes the maximum of
the two decode arm floors, never their sum"; line 450: "apply the armwise
maximum"), and (b) **anti-conservative here**, because a comparative floor is
measured from a null in which "labels are deliberately made identical"
(`draft-v1.md` §detection floor), and no such null can exist for a cross-stack
pair. Both within-stack nulls are blind to runtime-switch variance. The proposal
imports a rule validated for two cells of one runtime into a setting where its
validating construction is unavailable.

---

## SECONDARY OBJECTIONS

**Novelty (d).** MLX-vs-llama.cpp on Apple silicon is a heavily trodden
comparison in the grey literature and is Silicon-Showdown-adjacent in kind. The
one differentiator is the floor gate — which is the **MVP paper's** contribution,
not this paper's. Strip the floor and nothing here is new; keep the floor and the
new content reduces to "we applied C1–C7 to one more pair of conditions." The
registry ceiling (L2, descriptive, stack-conditioned, no causal attribution) means
the best possible outcome is: *"stack X used ~9 % more decode energy than stack Y
for one model, one workload shape, one machine, and we cannot attribute it, and we
did not measure whether the outputs were equally good."* That is a table row, not
a paper.

Coverage is also thin against the bank's own framing of C5-1.8, which asks for
"MLX vs llama.cpp-Metal vs ollama … over a **shared shape grid**, n≥5." The
proposal delivers one model, one shape, two runtimes. It is the minimum viable
instance of an already-banked question.

**Venue (d/e).** The proposal's own assessment is right and should be taken at
face value: not an ICPE full-paper centerpiece. But it undersells the downside —
a workshop referee at EuroMLSys will ask "why is this not a quantization result?"
(F2) and "where is quality?" (F3), and the paper has no answer. Meanwhile
`impressiveness-roadmap.md` does not rank a cross-runtime axis **at all** among
its nine expansions; the nearest neighbour is rank 9 ("additional model families,
generic workloads" — "add only a model or device that changes the claim, not
merely the size of a results table"), and rank 1 carries the standing
instruction to "**prohibit breadth work from consuming**" the core nights. This
proposal is breadth work asking for core nights.

**Original goals (f).** It serves **none** of Ed's named mechanism axes —
speculative decoding, MTP, MoE routing, KV/attention, split inference — and the
proposal concedes this. Its claimed service is "exercises the intended
swappable-runtime harness," i.e. **modularity**, which is **P3** in the ratified
priority stack and is *explicitly sacrificeable if it costs P1/P2*. This costs
P1/P2 (6–10 weeks of desk capacity and 2–3 nights). Under the stack's own rule,
that is a decline. The claim that it "establishes the substrate those later
mechanisms require" is also weak: the mechanism studies (roadmap rank 7) name
speculative decode on a *forked or instrumented* runtime with proposal/acceptance
events — a llama.cpp *adapter* is not that substrate, and the roadmap recommends
external-draft spec-decode as the first mechanism precisely because it gives a
same-target on/off contrast with **no artifact mismatch at all** — the exact
property this proposal cannot have.

**One thing done right.** Section §Risks is genuinely good — the kill list is
specific, pre-night, and mostly correct in kind. It is wrong in *threshold* (F1)
and it omits the two triggers its own plan guarantees (F5, F6). That is a
proposal that reviewed its execution risk and not its design risk.

---

## THREE STRENGTHENING MOVES (if Ed keeps it anyway)

1. **Re-derive the entire sizing against the ~14 J armwise 7B floor, then let
   the arithmetic decide.** Set the pre-night gate at **lower interval edge >
   18 J (≈ 9.4 %)**, not 7.5 J. Run the daytime pilot *first, this week, at zero
   night cost*: build nothing but a throwaway `llama-cli`/`mlx_lm.generate`
   timing-and-power comparison at 7B/128-in/512-out, and compute
   `(E_llama − E_mlx)` from the diagnostic corpus scale. If the pilot gap is
   under ~10 %, **the paper is dead before any adapter is written** — that single
   afternoon is the highest-value action in this whole proposal, and it should be
   the gate on funding the desk work, not a step inside it. Publish the refusal
   in the MVP's limitations if it fails; that costs nothing and is on-thesis.

2. **Convert the confound into the contribution: make it a bits-per-weight
   study, not a runtime study.** Pre-register the *measured* weight-byte totals
   and realized bits-per-weight of both artifacts, and predict decode energy from
   bytes-per-token under the bandwidth-bound model. Then the paper's claim
   becomes falsifiable and identifiable: *"cross-stack decode energy is predicted
   within X J by weight bytes alone; the residual bounds the runtime-attributable
   term at < Y J, which is below/above our floor."* That converts F2 from a fatal
   confound into a covariate, upgrades the result past a bare L2 pairwise
   contrast, and — critically — a residual that is *below floor* is a publishable
   refusal ("no runtime-attributable term resolvable above bytes"), so the study
   has a positive outcome in both branches. This also merges cleanly with roadmap
   rank 5, which needs the same conversion-provenance apparatus.

3. **Add the quality gate and fix the two unbudgeted triggers.** (a) Adopt rank
   5's 256-item quality screen on both artifacts — it runs *outside* quiet
   windows at zero night cost and is the difference between this paper and the
   Silicon Showdown critique the project already published. (b) Decide the
   artifact-provenance dilemma explicitly and budget **three** new nights, not
   two, if re-conversion is chosen — or drop contribution 2's "same upstream
   revision" language and state honestly that MLX conversion settings are
   unrecorded. (c) Pre-register the residency policy for the contrast window
   (both-resident vs reload) and mint the floors **under that same residency
   condition**, or the floors do not transport and the window is refused after
   collection.

---

## Summary for the funder

Wrong bar (5 J assumed, ~14 J actual), a confound the same size as the only
clearable effect, no quality gate the project's own roadmap demands, an adapter
that does not exist behind an enum that suggests it does, and a night budget
that is 2 when the plan implies 3. The proposal is well-written and honest about
its ceiling; the ceiling is just too low for what it costs. **Spend the
afternoon on move 1. Do not spend the nights.**

exec
/bin/zsh -lc "sed -n '1,360p' ../portfolio/rev-batch-concurrency-energy.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review — "Cohort Joules: Defining Honest Energy Boundaries for Batched LLM Inference on Consumer Silicon"

Reviewer: Opus 5 counter-reviewer (adversarial charge: kill it if it can be killed).
Target: `scratchpad/portfolio/prop-batch-concurrency-energy.md` (proposal = final block, lines 7137–7197; an identical duplicate sits at 7074–7136).
Ground truth: `scratchpad/desk` @ main (`89b929c`), verified by two independent repo audits.

## VERDICT: **WEAK** — and KILL as currently framed. Only the rewritten form survives.

The proposal is honest in tone, well-disciplined about D-117, and correctly defers continuous
batching. But three things are fatal as written: the **headline contribution cannot fail**, the
**effect sizing is drawn from the wrong physical regime and is wrong by ~3×**, and the **true cost
is roughly 2–3× the claimed cost** once you count what the repo actually has (which for batch
floors is: nothing, not even a window class that can be expressed). It also produces the one
result class in this project's entire option space where the instrument's distinguishing
capability is irrelevant. The proposal has its own strengths and weaknesses inverted — it hedges
on feasibility (easy) and overclaims on novelty and venue (the actual problems).

## Scores

| Axis | Score | One-line |
|---|---:|---|
| Novelty | **3/10** | Batch-size energy curves are a saturated literature; "no per-request joules under batching" is stated verbatim in ML.ENERGY (NeurIPS D&B spotlight), which then *solves* it. The genuinely uncovered slice (Apple/MLX) is thin and is not what the proposal leads with. |
| Feasibility | **4/10** | The runtime gate is genuinely passed and effects will clear any bar easily — but batch floors are **zero lines of implementation** on top of a floor module that hard-refuses the required window class, plus a mandatory 31-group alias-calibration campaign the budget omits. |
| MVP leverage | **4/10** | Reuses the method sections honestly, but §8 of the MVP draft is the project's *own written argument* for scoping overlapping requests out. And a 30 J effect on a ~47 J baseline needs no detection floor. |
| Venue fit | **3/10** | Workshop-plausible. "Plausible ICPE full-paper component" contradicts the repo's 2026-08-06 roadmap, which enumerates the qualifying deeper contributions (held-out Q4 prediction / second-unit replication / one mechanism study) and does not rank batching anywhere in its top nine. |
| Original goals | **5/10** | Real infrastructure dividend for spec-decode and MoE-by-batch — D-070 cl.3 designed the request-scoped schema for exactly this. But it touches no mechanism, and it consumes the nights the mechanism study needs. |

---

## FATAL FLAWS

### F1. The headline contribution is unfalsifiable by construction — the crux failure

Thesis and Contribution 1 are the **overlap-boundary rule**: report phase energy "only when
request events prove a globally separated prefill/decode boundary." The matching kill criterion
is "cohort phase unions overlap."

That criterion **cannot fire**, for four compounding reasons, all documented in the repo:

1. The design imposes a **prefill barrier** with **sixteen equal-shape requests**
   (`docs/specs/axi/se_analysis_plans_draft.md` §1 `selection_scope`), and the S-B probe
   "freezes a static cohort by inserting all B requests once before the first `next()` … and
   draining the cohort to completion" (`docs/specs/axi/sb_static_batch_verdict.md`). Overlap is
   engineered away before any measurement.
2. `mlx-lm` 0.31.3 prefills the whole cohort in **one batched 2-D forward**: "Prompt processing
   constructs a two-dimensional batch, including right padding … then calls the model with
   `tokens[:, :n_to_process]`. Decode likewise calls the model once with `inputs[:, None]`."
   Live evidence shows `input_shape [2,12]` → `[2,1]` and `[4,13]` → `[4,1]`. With equal-shape
   prompts there is no padding and there are no per-request prefill intervals at all.
3. Most damaging: the same verdict records that the harness "takes a monotonic timestamp when
   each `next()` result returns … and **records the shared return timestamp honestly for
   responses from the same scheduler step**." There are no independent per-request phase edges to
   compare. The "union of prefill intervals vs union of decode intervals" is a test over
   *group-level scheduler-step bookkeeping*, not over physical per-request intervals.
4. The MVP paper already makes this argument, as its own scoping rationale
   (`docs/paper/draft-v1.md:172`): "continuous batching makes an 'active phase' label difficult
   to interpret when requests overlap. JouleWise adopts phase-specific reporting but **restricts
   its primary scope to one sequential request**, where runtime-emitted phase boundaries are
   well posed and can be calibrated." Contribution 1 is the MVP paper's *limitation sentence*
   promoted to a finding.

So the flagship contribution validates the harness's own accounting against a case constructed to
satisfy it, and the interesting case — real overlap under continuous batching — is explicitly
deferred to "a later paper." A referee will call this a tautology dressed as a rule. **This alone
prevents any rating above WEAK.**

### F2. Effect sizing uses the wrong reference class, a voided number, and lands ~3× low

The proposal projects a "cautious 5–30% per-request reduction (~2.5–15 J)" and concludes "**B=2
may not clear 5 J**, B=4 is uncertain," sourcing this from "datacenter literature reports roughly
a 25% energy/token reduction over a much larger batch range."

Wrong regime. Datacenter batch curves are measured on GPUs already compute-saturated; the cited
25% is the *flat* part of their curve. An M3 Max running Qwen2.5-1.5B-4bit at B=1 is deeply
**memory-bandwidth-bound and grossly under-utilized** — decode reads ~0.8–1 GB of weights per
token per sequence, and batching amortizes that read across B sequences nearly for free.

Independent evidence: *Native LLM and MLLM Inference at Scale on Apple Silicon* (arXiv 2601.19139,
M4 Max 128 GB) measures **3.7–4.3× throughput at 16 concurrent requests**. If power rises ~1.3×
while throughput rises ~4×, per-request decode energy falls **~65–75%** — from ~47 J to ~13–17 J,
an effect of **~30–35 J**, i.e. **6–7× the ~5 J phase bar**. Even B=2 should show ~15–20 J.
*(Flagged: that throughput figure is a different model on a different chip and the power factor is
my inference. The sign and order are not in doubt, and the proposal's own "group-gross differences
should be much larger" concedes the mechanism.)*

Two consequences, the second worse than the first:

- The "cautious" posture and several kill criteria are mis-sized; "B=2 may not clear 5 J" is very
  likely a false-negative call that could kill the project's best cell for the wrong reason.
- **The paper does not need this instrument.** JouleWise's thesis is that detection floors and the
  attribution limit decide what may be claimed. A ~30 J effect on a ~47 J baseline is visible to a
  stopwatch and a wall plug. Scalpel, tree trunk.

Compounding compliance point: the ~47–50 J sizing input is **permanently VOIDED for claim use**
by D-078 (`PROJECT_STATUS.md:381`, `README.md:69`). The proposal calls it "the old … diagnostic"
but never says voided. Sizing an MDE off a voided corpus is exactly what D-078 forbade.

### F3. True cost is roughly 2–3× claimed, and the priority case is never made

The proposal budgets "**three additional quiet nights, possibly four**" beyond D-117's three, and
folds the batch floor *and* the 93-group three-block pilot into one window. Every load-bearing
piece of that is missing from the repo:

- **No batch adapter exists.** `joulewise/adapters/mlx_runtime.py` contains the string "batch"
  **zero times**. The only `static_batch` producer is the mock (`mock_spec_runtime.py:194`). Queue
  row `A4 / AXI-SB-ADAPTER` is `READY` — i.e. unstarted. *(The proposal does say "the required
  adapter is not yet implemented" — credit.)*
- **The floor module cannot express a batch window at all.** `joulewise/detection_floor.py:227–239`
  hard-raises on any `window_class` outside `("request","phase")`, and `batch_group_gross_energy_j`
  is absent from `FLOOR_METRIC_CATALOG`. Grep for `Sigma_F` / covariance machinery across
  `joulewise/`: **zero hits**; `detection_floor.py` is scalar-only.
- **A dedicated calibration campaign is mandatory, not optional.** AP-BATCH's floor gate: "accept a
  group calibration only if it covers **every B's** unioned window semantics, duration/cadence/drift
  range and supplies the joint `Sigma_F`; **a scalar single-request floor alone refuses** … If any
  required covariance, bound, B, or nonlinear denominator support is absent, **a dedicated 31-group
  same-design alias calibration is mandatory; otherwise this AP does not execute.**" And: "There is
  no fallback transport that always accepts."
- **The inherited hours exclude that calibration.** The ~3 h / ~5 h figures are not from AP-BATCH;
  they are from `docs/phase_2/splitwise_replication_roadmap.md` (2026-07-19), whose own row already
  warns "group-level floor/covariance path (**single-request floors do NOT transport**)". *(The
  proposal does flag these as uncertain historical estimates — credit — but then budgets from them
  anyway.)*

Realistic total: **four to six nights**, plus a from-scratch floor/covariance subsystem, plus an
adapter, under a fail-closed protocol where a refused window costs the whole night
(D-079 rationale: "it costs a whole quiet window per occurrence and window time is the project's
scarcest physical resource").

Now the priority arithmetic the proposal never does. The 2026-08-06 roadmap recommends **5–7
Ed-present sessions** total, 8–10 for an ICPE-full attempt, and concludes: "The strongest realistic
paper is … C1–C8 metrology + the already-collected 1.5B/7B demonstration + **one designed extension**
+ an independently usable artifact" — with the shortlist for that one slot being held-out Q4
prediction, quantization, or one mechanism study. D-117's three nights plus this proposal's four-to-six
consumes the entire ICPE-full budget on an axis that **appears at no rank in the roadmap's nine**.
(The only batch-adjacent phrase there is rank 7's "batch-**1**" speculative decode — that means the
*single-request* condition, not batching. Do not let it be read as support.) Rank 1's decision line
is explicit: "Reserve the core nights now and **prohibit breadth work from consuming them**." Under
Ed's paper-first stack (P1 MVP, P2 ICPE, **P3 sacrificed if it costs P1/P2**), this is P3 work
eating P1/P2 nights, and the proposal argues neither side of that trade.

### F4. Existing-material compliance gaps

- **"the existing AP-BATCH design"** — it is `AP-BATCH-**DRAFT**`, in a file headed "**DRAFT — design
  only; no campaign authority**", plan state "**PROVISIONAL pending P2-015 Window-A floors**", last
  edited 2026-07-15, owning queue row `A7 / AXI-SE` still `READY`, every number literal-marked
  `PROVISIONAL-UNTIL-P2-015-AND-PILOT-BATCH-V1`. P2-015 floors do not exist: `CLAIMS_STATUS.md` §1
  reads "**NONE at this checkpoint.**" The proposal's desk list does say "AP-BATCH finalization after
  the pilot," so this is overstatement rather than fabrication — but a reader budgeting nights off
  this text will think a frozen plan exists.
- **"authorized by D-070"** overstates it. D-070 cl.3 authorizes *scope and schema shape*; cl.2 holds
  that "every AP remains floor-gated on P2-015 floors … and no AXI stream consumes a [QUIET-MAC]
  window until Window A completes"; cl.5 caps everything at L2 with "no live claims from
  fixture-first code." No campaign authority was granted.
- **Contribution 4 is already repo doctrine.** AP-BATCH's metric row already states "**No overlapping
  group energy is divided among requests.**" Presenting the design constraint as an empirical finding
  is circular.
- **The claim-bearing phase work is unauthorized and unbudgeted.** AP-BATCH: "Gross phase-window
  energy is a **descriptive L1 audit** unless a later registry enumerates a phase family."
  Contributions 1–2 need a newly minted phase family, its own Holm denominator, and a phase-specific
  floor route. None appears in the desk list or the night budget.
- **C5-2.2 is never named.** The row this paper consumes carries the binding caveat "*no serving
  conclusion without latency-bound policy*." Its Mac leg *is* minted (2026-07-16, in
  `docs/research_question_bank.md`, per D-070 cl.4's mint-on-`supported` rule) — but the proposal
  cites neither the row, its caveat, nor D-070's requirement that these axes be framed as **stress
  tests of the single Q4 thesis, "not five new theses."** The proposal gives batching its own thesis.
- **Multiplicity is never mentioned.** AP-BATCH runs a seven-hypothesis Holm family for model
  selection, a separate denominator for normalized energy, and eight two-sided latency hypotheses —
  at draft `n_blocks=5`. That is where the statistical risk actually lives.
- **D-117 licenses no new axes.** Its only fenced extensions are the ≥256-token prefill arm (Ed's
  open option, "not adopted here," ~110 core min, "likely its own window") and Option 1 historical
  candidacy as a contingency requiring a rule-11 cold gate. Three severity-`blocker` desk items
  (F1/F2/F3 in the design memo) plus live night-stranding defects (L4, L5, R6) stand before the
  first D-117 arm runs.

*(One overreach I checked and did **not** find: the proposal does not claim the token-normalization
contract needs re-issuance, and correctly so — `docs/contracts/token_normalization.md:137` already
requires batch/concurrency policy disclosure as "Always applicable.")*

### F5. Contributions 3 and 4 contradict each other

C3 promises "gross joules/request" and "joules/output-token." C4 declares that "physical energy
remains identifiable only at cohort level" and that "no equal-share allocation is presented as
measurement." Both C3 metrics *are* cohort energy divided by a request or token count.

AP-BATCH resolves this and the proposal does not: dividing a **complete 16-request block partition**
by exactly 16 is legitimate *by symmetry of the design* (`BATCH-JREQ-B<value>-VS-B1`), whereas
allocating a single overlapping group window among its members is not. As stated, "an empirical
limit on per-request energy" is simply wrong — with sixteen identical equal-shape requests the
symmetric mean **is** the correct per-request estimator, and refusing it would be a metrology error
dressed as rigor.

### Minor

- The B=16 memory-fit kill criterion is near-empty. Measured marginal cost is **~33 MB per added
  sequence** (B=2 peak 968.7 MB → B=4 peak 1,034.4 MB); B=16 extrapolates to ~1.43 GB on a machine
  that has absorbed a 68.9 GB peak (Qwen3.5-122B-A10B-4bit run). D-070 cl.3's own rationale says "a
  single model instance with B KV caches is **memory-feasible on current hardware**." Fair as an
  untested-cell check; not a kill, and it must not be used to justify a smaller grid.
- "This intentionally extends the frozen single-request boundary, but does not alter or contaminate
  the D-117 campaigns" is the right sentence — and it is the only place the extension is priced. It
  prices *contamination* risk correctly (~zero) but never prices the *authorization* cost: the new
  phase family, the new floor window class, the AP freeze.

---

## What the proposal gets right (credit where due)

- Correctly defers continuous batching per D-070 cl.3, and names *why* (arrival traces, steady-state
  detection, scheduler policy, offered-load) rather than gesturing.
- Correctly refuses looped-singleton dispatch, matching AP-BATCH's inclusion rule and the S-B
  verdict's `unsupported_for_joulewise(native_batch_execution)` code.
- Correctly states that single-request floors do not license batch claims and that the ~5 J bar is
  only a planning proxy here. This is the sharpest sentence in the document, and it is consistent
  with D-078 cl.11 / D-083, which scope that bar to *phase contrasts on single-request windows* and
  provide no bar for any other estimand.
- Correctly rules the borrowed WT310E a non-dependency, for the right reason (validates totals, not
  allocation) — matching the roadmap's own C8 row and D-092.
- Correctly protects D-117 as non-negotiable, and reproduces its 3.14 / 3.24 / 2.80 h budgets and
  six-item desk list **faithfully** (independently re-verified against the design memo, including
  the arithmetic).
- Honest that the adapter does not exist and that the inherited hour estimates are stale.
- Kill criteria are mostly real, pre-committed, and desk-checkable — except the one that matters (F1).

---

## THREE STRENGTHENING MOVES (if kept)

**1. Re-center the thesis on the *shape* of E(B), not on the boundary rule.**
Make the primary claim AP-BATCH's *existing* primary family — the affine slope and the three
lack-of-fit curvature contrasts `d_1,d_2,d_3` — and ask what the datacenter literature structurally
cannot answer: **where is the amortization knee on a memory-bandwidth-bound consumer SoC, and is the
departure from affine resolvable above the floor?** Curvature contrasts are small differences of
large numbers; unlike the J/request curve, they *are* floor-sensitive, which makes the instrument
load-bearing again and turns the paper into the Q4 stress test D-070 actually asked for. Retitle
accordingly; demote the overlap rule to a two-paragraph methods subsection.

**2. Replace Contribution 1 with a negative control that can actually fire.**
Pre-register a deliberately **ragged cohort** — unequal prompt lengths (triggering `mlx-lm`'s right
padding) or staggered admission at B=4 — and show the validator *refusing* the phase split there
while *accepting* it under the equal-shape barrier. That is the only version of the boundary claim a
referee will accept; it is falsifiable; it costs desk time plus a slot inside the pilot rather than a
new claim night; and it yields the paper's one genuinely publishable refusal. If it cannot be built
on a shared-scheduler-step timestamp surface — and the S-B verdict suggests it cannot — **drop the
boundary claim entirely** and say so in print.

**3. Re-price honestly, and force the head-to-head before a single night is committed.**
(a) Build the A4 adapter and run the group ladder **off-window** on the unquiet machine to produce a
real occupancy number, replacing the 2026-07-19 inherited estimates. (b) Scope the batch-floor
subsystem explicitly as what it is — a new `detection_floor` window class, a `Sigma_F` covariance
implementation, and a 31-group alias-calibration campaign — and put *that* on the night ledger, not
just the pilot. (c) Write the ledger against roadmap ranks 1, 2 and 3 (remint / C8 wall meter /
artifact release) and state in writing which Ed accepts delaying; the roadmap's "one designed
extension" slot has a shortlist and batching is not on it, so that omission must be argued *with*,
not around. (d) If the lack-of-fit family cannot be powered at `n_blocks=5` under Holm-7, **shrink to
B ∈ {1,4,16}** — three well-floored cells beat five unresolvable ones, and the knee is still
locatable. Bind the limitations section to C5-2.2's existing "no serving conclusion without
latency-bound policy" wording, and re-derive the sizing input from D-117's fresh floors rather than
the D-078-voided ~47 J corpus.

---

## Novelty evidence (external)

| Work | Overlap | Why it hurts |
|---|---|---|
| ML.ENERGY Benchmark (arXiv 2505.06371; NeurIPS D&B spotlight) | Direct | States Contribution 4 verbatim: batching makes "the energy consumption of a single request dependent on all other requests being processed at the same time." It then *solves* it with a steady-state accounting method. The proposal's answer is to refuse — weaker than the state of the art, not stronger. |
| "Where Do the Joules Go?" (arXiv 2601.22076) | Direct | 1,858 configurations with batch-size sweeps, static-power accounting, causal knob→latent-factor→energy framework. Already in the repo's related work. |
| TokenPowerBench; SweetSpot (2602.05695); vLLM energy benchmarking (2509.08867); Bench360 | Direct | Batch-size energy curves are a crowded, actively published space. |
| *Silicon Showdown* (arXiv 2605.00519) | Partial | Apple M3 Ultra + RTX 5090, `powermetrics`, tokens/joule, prefill/decode separated — but **batch size 1 only**. Half the gap. |
| *Native LLM/MLLM Inference at Scale on Apple Silicon* (arXiv 2601.19139) | Partial | Continuous batching on MLX, 16 concurrent, M4 Max — but **no energy measured at all**; energy profiling listed as future work. The other half. |
| `ml-energy/zeus-apple-silicon` | Reviewer question | Sub-millisecond per-rail IOKit energy counters on Apple Silicon. A referee *will* ask why the attribution limit is accepted rather than instrumented away. The repo has the rebuttal (`docs/run_reports/2026-07-30-sweep-cv-paths.md`: 8 stars, README "explicitly disclaims accuracy… no calibration, no error bars, tests use mocked data") — **but the proposal does not carry it**, and this paper needs it far more than the MVP does. |

Net: the honest uncovered slice is "phase-resolved energy vs static batch size on Apple
Silicon/MLX, with floors." That is real and narrow — a workshop paper. The proposal instead leads
with the boundary rule, which is the *least* novel and *least* testable thing in it.

---

## Bottom line

Do not fund this as a paper. In its current form it spends four-to-six quiet nights — plus an
adapter and a floor/covariance subsystem that do not exist — to measure a large, well-known effect
with an instrument whose distinguishing capability the measurement does not need, and to prove a
boundary rule its own design cannot violate, on an axis the project's own strategy document does not
rank.

Fund it only in the rewritten form (a Q4 shape-of-E(B) stress test with a falsifiable ragged-cohort
refusal control, re-priced, with an explicit written trade against roadmap ranks 1–3) and only
**after** the MVP lands and the roadmap's single "designed extension" slot has been spent on
something from its own shortlist. Until then, the correct disposition is: build the A4 adapter as
desk work — it is cheap, it is already queued, and it is the infrastructure D-070 cl.3 wanted for
speculative decode — and spend no quiet nights on batching.

exec
/bin/zsh -lc "sed -n '1,260p' ../portfolio/rev-contamination-characterization.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review: "Quiet Is a Measured State" (prop-contamination-characterization)

Reviewer: Opus 5, counter-review pass. Charge: kill it.
Ground truth: `desk/` @ main. Every number below was checked against primary repo bytes.

**VERDICT: WEAK** (one notch from KILL; survives only in the shrunken forms in §Strengthening).

| axis | score |
|---|---:|
| novelty | 3 |
| feasibility | 3 |
| mvp_leverage | 6 |
| venue_fit | 4 |
| original_goals | 2 |

---

## What is actually right (stated first, because it is unusual)

The arithmetic is clean and I could not break it. `0.1923 W` mean, between-capture
SD `0.0008 W`, max `6.74–7.47 W` reproduce exactly from
`docs/process_traces/2026-08-04-t3-char-pair/ANALYSIS-APPUP-R01R02.md`. The
screensaver figure (`43/50` bundles, `~+30%` energy) reproduces from
`RUN_STATE.md:2118-2119` and `PROJECT_STATUS.md:376`. `5 J / 93 s = 0.054 W` and
`0.1923 W × 93 s ≈ 18 J` are both correct. The proposal correctly refuses to use
the n=2 permanently-non-claim captures as claim evidence, correctly says no wall
meter is needed, and correctly declines to divert the D-117 windows. The
guard-confusion-matrix idea (contribution 3) is the one genuinely novel item in
the document.

That is the whole of the good news. The design does not survive contact with the
project's own rules.

---

## Fatal flaws

### FF1 — The window as specified cannot produce a claim-bearing result. Its own project would refuse it.

The design is 12 Williams-balanced epochs, 3 per state, 2 members per epoch:
**6 LLM observations per cell, and at most 3 paired contrasts per state-pair.**

`docs/paper/draft-v1.md:78`, the project's own floor rule:

> "fewer than five valid bundles or blocks are treated only as development
> evidence, not as a claim gate."

Three blocks is below five. The comparative side of every state contrast — the
side that carries the entire thesis — is *development evidence by the paper's own
§4*. The absolute side (n=6) clears the threshold by one and still eats the
pre-registered small-sample guard factor. Compare the ratified standard: D-117
alpha/beta/gamma each run **10 absolute + 10 ABBA blocks**
(`DESIGN-MEMO.md:246-263`). To reach that standard across four states you need
4 × (10 + 40) = 200 members, i.e. **four-plus windows, not one**. The proposal's
"approximately 3.4 h" is understated by roughly 4×.

This is not a tuning quibble. The proposal asks Ed to spend a night on a design
that his own §4 will classify as non-claim-bearing before the data is reduced.

### FF2 — There is no floor for the condition family this paper needs, and the proposal never notices.

The `~5 J` bar the whole Experiment Plan is sized against is the **phase-contrast**
effective bar, `F_cell + B_claim`, for `phase_energy_j.decode` on the 1.5B stack
(`draft-v1.md:109-115`). An environment-state contrast on gross member energy is a
**different condition family**. The project's rule is explicit and repeated:

- `draft-v1.md:60` — a floor governs "the same telemetry backend, metric, window
  type, workload profile, and stack identity. One such family forms a measurement cell."
- `DESIGN-MEMO.md:366` — "Never sum components and **never borrow a decode floor
  for prefill**." If a decode floor cannot transport to prefill on the *same
  members*, it certainly cannot transport to a new environment-state estimand.

So the contamination cells need their own minted absolute and comparative floors —
which requires null-ABBA members for an `env_state_contrast` family that appear
**nowhere in the proposed member list**. The list carries 12 NEG-8 bound members
(the bracket-drift corpus, not a floor) and 7 references. Either the headline
result has no decision bar at all, or a second window's worth of floor members
must be funded. This is the single largest cost omission in the document and it is
completely silent.

### FF3 — This is not an operator-bookend window. It needs Ed awake, or an unbuilt controller plus a rule waiver.

Twelve within-window state transitions, three of them into cell A (**app DOWN**).
The repo's own protocol for that exact transition
(`2026-08-04-t3-char-pair/PROTOCOL.md`, §Design):

> "Arm B (app-DOWN), collected **with Ed present** ... Arm B is deliberately NOT
> collected unattended tonight: quitting t3 would kill Ed's own observation
> threads, and the app-death-recovery acceptance gate wants Ed present for the
> quit/relaunch."

Cells C and D are worse. C requires *starting an agent session inside a
measurement window*; the repo's binding rule (`CLAUDE.md`, enforcement boundaries)
reads "Never start or continue a `[QUIET-MAC]` measurement while an agent session
is active." Treating the agent as a deliberate treatment is scientifically
defensible, but relaxing that boundary is a ratification act, not a design choice
— and under CLAUDE.local.md rule 11 the lieutenant is forbidden to self-exempt
from a mandatory trigger. The proposal's one-line "detached state controller" is
QUIET-GUARD-01 (still unbuilt, named as unbuilt in the very PROTOCOL it cites,
limitation 1) plus a detached agent-session launcher plus 12 supervised process
transitions with identity custody. None of it is costed.

Add the settle time the proposal omits: the project's convention is a 180 s settle
after operator/stage activity (`draft-v1.md:151`, `DESIGN-MEMO.md:309`). Twelve
transitions × 3 min = **36 min** that does not appear in the 3.4 h figure. With
FF1's member count and FF2's floor members, the honest number is 3–4 nights.

### FF4 — The novelty is folklore that the literature already formalized.

"Background software corrupts measurements" is not an open question; it is the
premise of every energy-benchmarking standard and the subject of an active
methodology literature. Standard controls are documented and in use: freeze all
non-essential cgroups so only workload and sampler run; subtract idle energy;
randomize/shuffle run order against unnoticed background processes; CPU warm-up
against thermal confounders. Recent work does exactly the framework version of
this ([METRION: A Framework for Accurate Software Energy
Measurement](https://arxiv.org/html/2512.06806); [Measuring Software Performance
on Linux](https://arxiv.org/pdf/1811.01412)), and there is already a paper whose
entire subject is the energy cost of a background feature ([Toward Greener
Background Processes](https://arxiv.org/pdf/2509.11738)). MLPerf Power/SPEC make
environment control an *admission condition*; JouleWise's own `draft-v1.md:125`
already encodes it as an admission gate.

What is left after prior art is: *a macOS-specific numeric budget for one laptop
with one app resident*. That is a paragraph, honestly. Formalization earns
publication only when it changes practice — and the proposal's own contribution 4
anticipates the likely landing as "retain zero-agent operation with a measured
reason," i.e. **no practice change**.

### FF5 — The expected result is "the obvious things are big, the interesting thing is unresolved."

Sort the four cells by (decision relevance × uncertainty):

- **B (dormant app delta)** — the only cell whose answer is both unknown and
  decision-relevant. The proposal itself says its increment over app-down "is
  unknown and may not clear 5 J." Most likely outcome: *unresolved*.
- **C (idle agent)** — largely known already. D-099 puts an idle-waiting session
  at 12–18% CPU of agent load; the banked analysis (`ANALYSIS-APPUP-R01R02.md:49-52`)
  already calls active streaming "two orders of magnitude over the effective bar."
- **D (transcript replay)** — the proposal predicts order-one watts, i.e.
  hundreds of joules. Nobody doubts this. Worse, D is a **proxy**: frozen-rate
  transcript replay is not an agent, so the paper's "background software"
  characterization for the agent regime rests on a simulacrum.

So the modal paper is: two cells confirm the obvious at 100× the bar, one cell
returns "not resolvable," one cell measures a stand-in. The proposal is admirably
honest that "unresolved is a valid outcome" — but you cannot *build* a paper on the
likelihood that its central quantity is unresolvable.

## Non-fatal but worth recording

- **Existing-material compliance is thin on registration.** `docs/research_question_registry.md`
  has no background-contamination RQ; its "contamination" rows (C5-2.5d) are
  *dataset* contamination. The nearest environment RQ is `RQ-POWER-MODE`, banked,
  "analysis-plan-only." D-117 is adopted; this is not registered anywhere.
- **Minor misreport:** proposal says p95 "approximately 0.46–0.48 W"; banked values
  are 0.463 / 0.484 W. Rounding down the top edge in a paper about tails is a bad habit.
- **Roadmap collision.** `docs/strategy/2026-08-06-impressiveness-roadmap.md` ranks
  nine expansions. This direction is not among them, and rank 1 is an explicit
  instruction to "prohibit breadth work from consuming" the core nights.
- **Venue arithmetic.** CSCSU is **5 pages including references**. There is no
  world in which the MVP method + D-117 results + a four-state contamination study
  fit in five pages. The proposal's "capstone paper/chapter" glosses this.

---

## Three strengthening moves

1. **Make it desk work, not a night — and the corpus is already being collected.**
   Every D-117 member carries its own idle capture (lifecycle stage 4,
   `raw/powermetrics_idle.plist` + `rich_telemetry_idle.jsonl`). Three windows
   × 203 captures gives an in-custody, claim-adjacent idle corpus for free.
   Compute the empirical distribution of *asymmetric burst energy* over real
   93 s member durations and publish `P(asymmetric burst > 1 J)` and `P(> 5 J)`,
   plus the same statistic recomputed on the banked n=2 app-up pair as an
   out-of-family cross-check. Zero new nights, zero new floors, zero rule waivers,
   and it is the paper's actual contribution — the burst-asymmetry budget — rather
   than its ceremony.

2. **If a window is funded, fund exactly two states at the ratified standard.**
   A (app-down) vs B (app-up dormant), 10 absolute + 10 ABBA blocks, with a
   pre-registered `env_state_contrast` condition family carrying its own null
   members and its own minted floor. One question, properly powered, with a real
   decision bar. Drop C (answer already known) and D (a proxy) entirely — they buy
   nothing and they are what force the agent-session rule waiver and the
   detached-controller program.

3. **Reframe the headline onto contribution 3, which is the only novel item.**
   Not "background software contaminates measurements" (settled) but *"how good is
   an admission gate?"* — false-accept and false-refuse rates of JouleWise's §5
   quiet-state guard against prospectively labelled environment states. That is an
   instrument-validation result about the project's own machinery, no prior work
   reports it, it is cheap, and a false-accept above the bar would be a genuinely
   publishable negative finding about §5 rather than a restatement of the field's
   standing assumption.

---

Sources: [METRION: A Framework for Accurate Software Energy Measurement](https://arxiv.org/html/2512.06806) · [Toward Greener Background Processes — Measuring Energy Cost of Autosave Feature](https://arxiv.org/pdf/2509.11738) · [Measuring Software Performance on Linux](https://arxiv.org/pdf/1811.01412)

exec
/bin/zsh -lc 'for f in ../portfolio/rev-drift-thermal-science.md ../portfolio/rev-energy-nutrition-label.md; do echo "FILE $f"; sed -n '"'1,380p' \""'$f"; done' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
FILE ../portfolio/rev-drift-thermal-science.md
# Counter-review: "Drift Is Never Zero: Temporal Metrology for LLM Energy Experiments on Consumer Silicon"

Reviewer: Opus 5, adversarial lens. Ground truth read at `desk` @ `89b929c`.

## Verdict: **WEAK**

Not a KILL — the underlying material is real, cheap, and honestly described, and the
proposal is unusually disciplined about its own limits (accurate arithmetic, correct
citation of the diagnostics, explicit refusal semantics, explicit concession on Ed's
original goals). But it is not a standalone paper. It is (i) §4 of the MVP draft, (ii)
one row of the MVP's own characterization table, and (iii) a methods appendix — bundled
and given a title. Its central quantity is, by its own cited evidence, *below the
instrument's resolution*, and the one quantity that would clear a floor (recovery-tail
energy) is a new metric family with no minted floor, no calibration basis, no
pre-registered extraction spec, and a confound the D-117 design cannot break.

## Scores (1–10)

| Axis | Score | One-line justification |
|---|---:|---|
| Novelty | **3** | Steady-state/thermal-state protocol discipline is a 15-year-old norm; only the never-zero allowance *construction* is fresh, and it is ~1.5 pages. |
| Feasibility | **6** | Reference cells and 5 s-resolution cooldown traces are genuinely banked; but the recovery-energy claim needs a new floor family and reopens a ratified freeze. |
| MVP leverage | **4** | Leverage is so high it inverts into double-publication risk: >70% of this paper is verbatim MVP §§3–5. |
| Venue fit | **4** | Already a capstone chapter (it is literally in `draft-v1.md`). Standalone ICPE: no. Workshop: marginal. |
| Original goals | **2** | Proposal concedes it serves none. Correct concession; the score follows. |

---

## Fatal flaws

**F1 — It is already published. Double-publication is not a risk here, it is the
baseline state.** `docs/paper/draft-v1.md` line 86–95 is a section titled *"Measured,
never-zero drift allowance"* that states the exact `A_drift = max(observed excursion,
derived reference-repeatability bound)` rule, the 3/1/3 reference design, the midpoint-
curvature rationale, and the "a passing drift screen never means zero drift" claim. That
is Contribution 2's entire descriptive content, already written. Line 151 is the
characterization table's **"Drift and settling"** row, whose method column reads: *"Place
long controlled holds and fixed reference workloads through the window, including start,
midpoint, and end references. After operator or stage activity, repeat the reference
while recording the time required for thermal and admission observables to stabilize;
compare it with the 180 s operating convention."* That is Contributions 1, 3 and 4. Line
158 is a paragraph already distinguishing slow drift from thermal settling. A referee
handed both manuscripts will ask which one is the extended version of the other, and with
Rivoire — who sets a metrology bar and will read both — the salami question is asked out
loud. The proposal never once acknowledges that the MVP contains this content; it says
only that the MVP "treats it as one characterization row," which understates it by a
section and a half.

**F2 — The D-117 windows do not schedule the experiment the MVP's own drift row
specifies, and the proposal substitutes weaker data without saying so.** The frozen
per-window schedule (DESIGN-MEMO §schedule, identical for alpha/beta/gamma) is: *pre
calibration → 12 NEG8 → 3 start refs → absolutes/ABBA → 1 midpoint ref → ABBA → 3 end
refs → post calibration*. There are **no long controlled holds** and **no
post-transition reference repeats**. The 180 s post-admin settle appears exactly once per
window, inside the pre-calibration allowance, and is followed by 22 minutes of NEG8
members before the first reference — so nothing measures residual settling against the
180 s convention. Contribution 4's settle-sensitivity item and the MVP row's "compare it
with the 180 s operating convention" test are therefore **unobservable** from D-117 data.
The proposal's desk-work list includes "sensitivity to the 180-second operator settle" as
if it were reduction work. It is not; it is an experiment that was never scheduled.

**F3 — The central quantity is below the instrument's own resolution, and the proposal
knows it.** Its own best clean estimate is 0.006718 J of point drift over 2.96 h on
~38.5 J references (decision_log line 4519) — 0.017%, roughly **150× below the ~1 J
attribution limit** and ~750× below the ~5 J practical bar. The other two cited numbers
are worse as evidence, not better: 0.778 J is the signature of a **stale end reference
measured ~2 h post-collection** (decision_log line 4508, run report a5) — i.e. a protocol
violation, not in-window drift; and 0.70 J is an ABBA-mitigated 0.47% cross-block trend
on a ~148 J workload. So the honest prospective statement is: *in-window drift on this
stack in a quiet window is not measurable with this instrument.* The proposal correctly
refuses to claim "no drift" and reports containment instead — but a paper whose principal
object is unresolvable by its own instrument yields six binary pass/fail cells. That is a
table, not a results section.

**F4 — Contribution 2 validates the wrong never-zero rule, or two of them at once.**
There are two distinct never-zero constructs in this project and the proposal conflates
them. The one it writes down is the **energy** allowance `A_drift` from draft §4. The one
that actually carries a reportable number is D-102 pin 3 / D-117 cl.1: `A_s =
max(observed_drift_s, 0.010818)` — a **timing** allowance in seconds, worth **~+43% on
the a10 anchor bound** (`CLAIMS_STATUS.md` lines 34, 140). The proposal's stated formula
is the energy one; the constant a reader will expect (0.010818) is the timing one. As
written the contribution is not evaluable. Worse: the interesting version — "does the
never-zero timing floor change a mint decision?" — is a **desk replay of existing
material requiring zero nights**, which means the strongest single result in this paper
does not need any of the three windows.

**F5 — The recovery-tail contrast is (a) unfloored, (b) confounded, (c) informatively
censored, and (d) n=1 at the stated replication unit.**
- *(a) Unfloored.* "Excess-energy area above baseline" is a new metric family. Under this
  project's own regime a claim-bearing metric needs a minted floor (repeatability +
  attribution + drift), a calibration basis, and a pre-registered extraction spec. The
  pulse-train bracket calibrates **phase-edge timing**; it says nothing about
  free-running integration of 5 s idle means over a 100–300 s window. The proposal
  applies "the applicable approximately 5 J bar" without deriving any applicable floor.
  Under D-117's gate discipline that claim cannot be published. The claim "no extra
  base-case night" quietly assumes a floor family that does not exist.
- *(b) Confounded.* 1.5B and 7B decode arms differ in *both* power and duration, so
  "workload-conditioned recovery" is total-delivered-energy-conditioned recovery. Model
  identity is not separable from thermal load without an intensity ladder — which the
  proposal itself defers to an optional fourth window. The headline hypothesis is
  unidentified in the base design, and the proposal lists it as a falsifiable
  contribution anyway.
- *(c) Informatively censored.* `cooldown_gate` (controller.py ~2408–2540, policy
  `subwindow_s=5.0, sustained_window_s=30.0, tolerance_fraction=0.10, cap_s=300.0`)
  terminates the observation at the moment the 30 s rolling mean falls to ≤110% of the
  frozen reference. The tail is right-censored *by the threshold that defines the
  outcome*, and censored at 300 s by the cap — and cap-hit members are additionally
  stamped `{"cooldown_cap_hit": True}` against the **following** repetition, i.e. the
  longest-tail observations are simultaneously admission-affecting events elsewhere in
  the protocol. The proposal lists "cap-hit frequency" as a metric and never addresses
  that the censoring is informative and entangled with science-cell admission.
- *(d) n=1.* The proposal declares "window, not individual cooldown subwindows, is the
  independent replication unit." Only gamma has paired 1.5B/7B arms. Therefore the
  recovery contrast has **one** independent replication unit. Under the project's own
  two-gate rule (floor clearance *and* interval-supported direction), an interval over
  n=1 is not constructible. Either the sentence is wrong or Contribution 3 is dead; the
  proposal does not notice the contradiction.

**F6 — It proposes to reopen a magistrate-ratified freeze, and prices the risk at
zero.** "Before freezing those plans, add a prospective temporal-analysis specification"
— but D-117 plan-freeze is already ratified (`de9e879`, gates 1–8 adopted, U1–U10 work
orders, three toolchain blockers), with U1/U2 confirmed live blockers in the
night-hardening triage register (`89b929c`). There is no U11 for a temporal spec. Adding
one is a new work order into an already-blocked queue, and DESIGN-MEMO's extraction
semantics are explicitly fatal-on-anomaly ("missing prefill phases, fallback values, or
member discovery outside the list are fatal"). A mis-specified temporal extraction that
refuses would jeopardize **the floor mint the P1 capstone paper depends on**. Under Ed's
paper-first priority stack this is the decisive argument: a secondary paper is proposing
to add refusal surface to the primary deliverable's critical path. The proposal's risk
section does not mention this at all.

## On the charge questions, directly

**(b) How many additional windows does it truly need?** The proposal says **0** (+1
optional). Honest accounting is **2 minimum** plus a new floor family:
1. A **long-hold / post-transition reference window** — the experiment the MVP's own
   drift row specifies and D-117 does not schedule (F2). Without it there is no settling
   science, only a drift screen.
2. An **intensity-ladder window** to de-confound thermal load from model identity (F5b).
   The proposal makes this conditional on gamma showing "a repeatable recovery effect
   that is censored or underidentified" — but it is underidentified *a priori*, by
   design, so the condition is already met before collection.
3. Plus desk + likely a repeatability corpus to mint a floor for recovery-tail excess
   energy (F5a).
The three D-117 windows give you: six containment cells (three nights × two families),
~39 cooldown traces per window at 5 s resolution, and a 3-night between-day containment
replication. That supports one table and one figure. It does not support a paper.

**(c) Effect sizes vs floors.** Drift half: 0.0067–0.78 J against a ~1 J attribution
limit and ~5 J bar — structurally sub-floor, guaranteed null. Recovery half: probably
*large* (a ~0.3–2 W elevation over 100–300 s is tens to hundreds of joules, so it will
clear any bar) — but a large effect that "the heavier model heats the chip more and it
cools slower" is thermodynamically obligatory, not a finding. The proposal's stated
"1–20 J, highly uncertain" range looks low to me by roughly an order of magnitude given
the release rule (10% tolerance on a small idle reference); I flag this as my estimate,
not a repo number. Either way the paper faces a bind: the resolvable effect is trivial
and the interesting effect is unresolvable.

**(d) Novelty.** Thin. "Fixed cooldowns and visually stable endpoints are insufficient
evidence of temporal stability" is the founding premise of SPECpower's calibration and
steady-state run rules, of sustained-performance-state methodology in mobile SoC
benchmarking, and of the rigorous-benchmarking literature on measurement bias and
warm-up (Mytkowicz et al.; Blackburn et al.). "Energy tail after a burst of work" is the
tail-energy concept from mobile radio energy work (TailEnder-lineage). Rivoire's own
JouleSort run rules encode the same discipline. *Cited from general knowledge — verify
before use.* What is actually new is narrow and worth stating narrowly: a never-zero
allowance with a **derived, hash-sealed positive lower bound** that is propagated into a
published detection floor, plus its measured arithmetic consequence (+43% on an anchor
bound). That is a contribution. It is one contribution, and it fits in the MVP.

**(e) Existing-material compliance.** Formally compliant — owned hardware only, WT310E
correctly declared a non-dependency, no abandonment of the instrument, no fabricated
apparatus. Substantively non-compliant on one point: it presents a new claim-bearing
metric family (recovery-tail excess energy) as free reduction of banked evidence when it
requires a floor mint the project has not designed (F5a).

**(f) Original-goals service.** Near-zero, and the proposal says so plainly — credit for
that. Its offered defense ("prevents temporal history from being misreported as the
energy effect of those mechanisms") is a hygiene argument that D-014 already implements.
It does not advance spec decode, MTP, MoE, KV/attention, or split inference by one step.

## What the proposal gets right (so this is not a hatchet job)

Its arithmetic reconciles exactly with the DESIGN-MEMO (140 = 50+50+40 science, 36 bound,
21 references = 7×3, 6 bookends). Its diagnostic citations are accurate to the source
lines. Its refusal framing is correct and it explicitly forbids the tempting bad claim
("the result is containment or refusal, not 'no drift'"). Its kill criteria are real,
including the `thermal_pressure`-is-categorical concession — which is correct: the trace
field is a string in `{nominal, normal}`, so "thermal dynamics" is unsupportable
vocabulary. And it correctly refuses to invoke the wall meter. This is a well-executed
proposal for a paper that should not exist separately.

## Three strengthening moves, if kept

1. **Demote it into the MVP and promote the one real result.** Do not write a second
   paper. Write **one subsection** of the MVP — "the price of never-zero" — that reports
   the D-102 pin-3 lower bound's *decision-changing* arithmetic: for each of the four
   minted cells, the operative floor with and without the 0.010818 s floor, and whether
   any claim verdict flips. This is desk-only, needs zero nights, uses the windows Ed is
   already funding, is genuinely novel against the literature, and is exactly the kind of
   result Rivoire will respect. Everything else in this proposal is either the MVP's own
   text or a null.
2. **Make the temporal extraction structurally incapable of harming the floor mint.**
   If any temporal spec is added, it must be a *separate, read-only, non-blocking*
   artifact with its own evidence root that cannot refuse or gate the D-117 extraction —
   explicitly outside the fatal-on-anomaly path, and added as a post-hoc reduction of
   already-collected bundles rather than a pre-freeze plan amendment. Otherwise the
   proposal is trading P1 risk for P3 content. If that separation is not achievable
   without a plan amendment, drop the temporal spec entirely and reduce the cooldown
   traces after collection with no pre-registration claim attached (report as
   characterization, not claim).
3. **If the recovery science is wanted, fund the identifying design and say the price
   out loud.** One intensity-ladder window (fixed model, three delivered-energy levels)
   plus a long-hold/post-transition window, plus a minted floor for recovery-tail excess
   energy with its own repeatability corpus and a defined baseline and integration
   boundary. State the censoring model explicitly (right-censored at release and at the
   300 s cap, with cap-hits informative) and pre-register a survival-style analysis of
   time-to-release rather than an energy contrast. That is a **real** two-extra-night
   paper — and then it should be honestly compared against the other 19 directions on
   two nights of Ed's scarcest resource, where I do not expect it to win.

## Bottom line for the portfolio decision

Fund the **desk-only** never-zero-arithmetic subsection inside the MVP. Do not fund a
standalone drift/thermal paper, and do not amend the D-117 freeze for it. If Ed wants a
metrology-flavored second paper, the never-zero construction is a better *seed* for the
general floor-methodology direction than it is a paper of its own.
FILE ../portfolio/rev-energy-nutrition-label.md
# Counter-review — `prop-energy-nutrition-label.md`

**Reviewer:** Opus 5 counter-reviewer (adversarial charge: kill it)
**Target:** "Before Joules Become Rankings: A Metrology-Complete Energy Label for Consumer LLM Inference"
**Ground truth:** desk checkout at `.../scratchpad/desk` (main), D-117, DESIGN-MEMO, `docs/paper/draft-v1.md`, `CLAIMS_STATUS.md`, `docs/research_question_registry.md`, `docs/research_question_bank.md`

---

## VERDICT: **WEAK**

Precisely: **KILL as a standalone paper in its proposed four-contribution form; WEAK-but-keep as an MVP section + released artifact, with one narrow re-cut worth a workshop/Emerging-track submission.**

It is the only direction in the fan-out that hits Ed's leaderboard/reporting axis head-on at zero marginal quiet-night cost, and it is scrupulously compliant with the existing-material constraint — that is why it does not get a flat KILL. But it is not a second paper. Stripped of ceremony, its four contributions reduce to: a schema whose every field is *already mandated in the MVP draft* and ~70% covered externally by MLPerf Power / SPECpower / AI Energy Score; a comparability rule ~65% covered by AI Energy Score's own same-hardware/same-task/same-size-class procedure; a re-rendering of the MVP's own D-117 results; and a 40-row audit dominated ~19× in scale by a June-2025 754-model audit, whose conclusion is known before it runs. A May-2026 position paper already occupies the genre. What genuinely survives is **one field and one rule** — the detection floor and the claim gate that refuses directional language below it.

### Scores (1–10)

| Axis | Score | One-line |
|---|---|---|
| Novelty | **2** | Every schema field is already in MVP draft §§1,3–6, and externally the label is ~70% covered by MLPerf Power + SPECpower + AI Energy Score, the comparability procedure ~65% covered, and the audit dominated 19× in scale by an existing 754-model audit. A May-2026 position paper already occupies the genre. Survivor: one field and one rule. |
| Feasibility | **6** | Zero extra nights is real and good. But the cost is misstated by the repo's own sizing, the two-coder audit is unstaffed, and the whole paper is a hostage to all three D-117 windows passing. |
| MVP leverage | **6** | Maximum possible reuse — which is precisely the problem: total reuse with near-zero incremental yield is a duplicate-publication hazard, not leverage. |
| Venue fit | **3** | Self-assessment is commendably honest in tone, but contradicts the project's own venue table: CSCSU's 5-pages-including-references budget makes the "§§2–6 reused nearly intact" plan physically impossible, no workshop is named (EuroMLSys/HotCarbon are already identified in-repo), the invented ICPE-full criteria do not match the roadmap's, and the dual-submission collision with the MVP paper is never mentioned. |
| Original goals | **7** | Best-in-class on the reporting axis — but delivers only the prohibitive half of the critique ("you may not compare") with no constructive bridge, and serves no mechanism axis. |

---

## FATAL FLAWS

### F1 — Contribution 1 is a table of contents for the MVP paper. (decisive)

The proposal's headline contribution is "a falsifiable minimum reporting schema" binding: *boundary, gross-J/request estimand, workload, phase, physical unit, OS/runtime/model/quantization/tokenizer identity, calibration bracket and status, floor decomposition, claim interval, gate verdict, custody digest.*

Every single one is already mandatory in `docs/paper/draft-v1.md`:

| Proposed "new" field | Already mandated at |
|---|---|
| measurement boundary | §3 "Measurement model and boundary"; §6 final para |
| gross-J/request estimand | §1: "Gross joules per request are the primary energy metric" |
| workload / phase | §3 (runtime-emitted phase events) |
| physical unit, OS build, runtime/library versions, model artifact hash, quantization, tokenizer identity, sampler policy, telemetry backend | §6 final para — verbatim list, with "Silent omission is not permitted" |
| calibration bracket + status | §3 "The pre- and post-window calibrations form a bracket…"; freshness/authentication rules |
| floor decomposition | §4 + the **LABELLED** publication path (corner-widened value, `floor_source`, decomposition required) |
| claim interval + gate verdict | §4 "effective clearable effect = F_cell + B_claim"; "reported as *not resolvable*" |
| custody digest | §5 "Cryptographic hashes bind those files to the campaign manifest" |

Coverage is 13/13. Contribution 1 contributes **zero novel fields**. What actually remains is serialization + a validator — engineering, not a scientific contribution. A referee who reads both documents will say this in one sentence and it will end the paper.

### F2 — Salami slicing / duplicate submission, unaddressed.

The proposal states it "reuses the MVP draft's Sections 2–6 nearly intact" and consumes the identical D-117 dataset. Relative to the MVP paper it therefore has **no new measurements, no new method, and no new data** — only a new output format for the same numbers. Two papers sharing §§2–6 near-verbatim and one dataset, submitted to a capstone and then ICPE, is a live ACM prior/concurrent-publication problem. The proposal never names the risk, never proposes a partition of contributions, and its "what is new" list (schema, comparability rules, mutation evaluation, audit) is exactly the list F1 just dissolved.

### F2b — Novelty against external prior art, using the project's own related-work section.

I do not need an outside literature search to establish this; the MVP draft convicts the proposal. Draft §2 and §8 state that **MLPerf Power and SPEC already require** "a qualified analyzer, uncertainty evaluated at the observed load, fixed measurement ranges, synchronized clocks, sufficiently long intervals, invalid-sample accounting, and explicit treatment of battery-backed systems," and that their governing principle is precisely *reject-on-missing-evidence per run*. Map that onto contribution 1:

| Label field | Covered by MLPerf Power / SPEC? |
|---|---|
| measurement boundary (SUT definition) | **yes** |
| calibration/qualification state | **yes** (qualified analyzer, fixed ranges) |
| uncertainty interval | **yes** (uncertainty at observed load) |
| stack/system identity | **yes** (submission descriptor) |
| workload identity | **yes** |
| invalid-sample / validity accounting | **yes** |
| phase (prefill/decode) identity | no — but this is the MVP's contribution, not the label's |
| detection-floor decomposition | **no** |
| explicit gate verdict / refusal of direction | **no** |
| custody digest | partial (submission bundles) |

So on the repo's own related-work text, the genuine novelty of the schema is **three fields**, two of which (floor decomposition, gate verdict) are the MVP paper's own C-ii and one of which (custody digest) is its C-iii. The label contributes the *serialization*, not the *fields*.

### F2c — External prior-art survey: worse than F2b. (novelty 3 → 2)

A dedicated literature sweep confirms and deepens this. Coverage of the proposed fields:

| Proposed label field | External coverage |
|---|---|
| measurement boundary | **~90%** — MLPerf `power_measurement.adoc` (SUT = everything LoadGen sensitizes, measured AC-side at the wall); SPECpower run/reporting rules; **ISO/IEC 21031:2024 (Software Carbon Intensity)** mandates a declared boundary + functional unit; AI Energy Score declares GPU-only |
| stack identity | **~95%** — SPECpower's rules are *strictly more exhaustive* (CPU/mem/storage/NIC/PSU, OS+JVM versions and flags, firmware, every power-management setting, non-default tuning with justification); MLPerf `system_desc` + `power_settings`; Model Cards |
| calibration state | **~75%** — SPECpower requires **annual NIST-traceable calibration**, an accepted-analyzer list, crest factor ≥3 |
| uncertainty interval | **~55%** — SPECpower (**2008**) mandates ≤1% average uncertainty and **no more than 5% of samples above 1%** |
| claim verdict | **~25%** — SPECpower gates *run validity* (invalid runs cannot be published); MLPerf and AI Energy Score gate *comparability by configuration partition* |
| custody digest | **~50%** — MLPerf's compliance checker computes client/server source and results checksums and validates the full PTD transcript; AI Energy Score requires an unaltered-logs attestation |
| **detection floor** | **~5% — this, and only this, is the contribution** |

Three specific threats the proposal must survive and never mentions:

1. **AI Energy Score** (Hugging Face + Salesforce + Cohere + CMU; launched at the Paris AI Action Summit, 10 Feb 2025). A *literal energy label with a literal label generator*: model, Wh/1,000 queries, task, scoring date, benchmarking hardware, 1–5 stars, verification link — **plus an explicit comparability decision procedure** (same hardware/H100, same task, text generation only within size class; alternative hardware permitted but ineligible for the leaderboard) **plus a custody attestation**. It lands on contributions 1 *and* 2. The "energy nutrition label for AI" framing is occupied.
2. **"Position: LLM Inference Should Be Evaluated as Energy-to-Token Production"** (arXiv:2605.11733, **May 2026**) — a position paper prescribing mandatory reporting fields for LLM inference energy. Nearest competitor in genre *and* recency; three months old. Must be cited and differentiated in the abstract or the paper is dead on arrival.
3. **Papadopoulos et al., "Methodological Principles for Reproducible Performance Evaluation in Cloud Computing"** (SPEC-RG-2019-04 / IEEE TSE 2021, ICSE 2020 Journal-First) — eight principles, a decision procedure, and an audit of an existing benchmark against them, from **SPEC's own research group**. The exact structural analogue of this entire proposal. Cite it or be caught. (Adjacent: Raasveldt et al., "Fair Benchmarking Considered Difficult", DBTEST@SIGMOD 2018 — a pitfalls-and-detection paper with no new system.)

Contribution 2 survives **only** if its gating predicate is the floor/uncertainty rather than configuration equivalence. That distinction is the paper's whole spine and the proposal never states it.

*Favourable finding, and it cuts against this paper:* the sweep found **no peer-reviewed validation of Apple `powermetrics` accuracy** — only Apple's own "estimated and may be inaccurate" man page, the ml-energy/zeus RFC #159 thread, community IOReport findings (1 mJ resolution; sub-10 ms windows dominated by quantization noise), and "Apple vs. Oranges" (arXiv:2502.05317) using it while flagging its imprecision. That void is real and citable — but it is **the MVP paper's** novelty, not the label paper's. Which is F1 again.

### F2d — Contribution 4 is dominated ~19× in scale by an existing audit.

- **Luccioni, Gamazaychikov, Alves da Costa, Strubell, "Misinformation by Omission"** (arXiv:2506.15572, June 2025): **754 models, 2010–Q1 2025**, three-level Direct/Indirect/No-Disclosure taxonomy, OpenRouter usage-weighted (84% of token traffic served by No-Disclosure models).
- **Luccioni & Hernandez-Garcia, "Counting Carbon"** (arXiv:2302.08476): **95 models**.
- **BetterBench** (NeurIPS 2024 D&B): AI benchmarks scored against **46 criteria**.

"Approximately 40 rows" is a pilot, not a study. Defensible *only* if reframed so the **instrument** — scoring against fields nobody else checks (floor, calibration bracket, custody) — is the contribution and n=40 is a stated limitation, not a headline. Two flagged unknowns that could make this worse and need a targeted read before funding: **AI-CARE** (arXiv:2602.16042, Feb 2026, "carbon-aware reporting evaluation metric") could not be characterized past its abstract and may collide head-on; and the **NREL "Beginner's Guide to Power and Energy Measurement and Estimation for Computing and ML"** (arXiv:2412.17830, Dec 2024) already covers at-the-wall vs. on-device boundaries, sampling strategy, and common error sources, closing with a call for "measurement methods and standards for facilitating robust comparisons" — i.e. it published this proposal's motivation twenty months ago.

### F3 — The audit cannot fail, and its sample is rigged.

Contribution 4's stated falsification condition: *"the critique fails if prevailing reporting already supplies the proposed mandatory evidence reliably."* Nobody publishes a corner-widened detection floor with a two-gate claim verdict and a custody digest, because nobody built JouleWise. The disconfirming outcome is foreknown to be impossible. Two coders and a κ statistic applied to a foregone conclusion is bookkeeping dressed as an experiment.

Worse, the sample is drawn from "the four nearest reporting systems discussed in the MVP draft" — i.e. TokenPowerBench, ML.ENERGY, Silicon Showdown, Intelligence-per-Watt: the four the MVP already criticizes for exactly these omissions (draft §2.3, §8.1). Auditing only your own straw men and excluding the strongest-practice reporters (MLPerf Power inference-power submissions, SPECpower results, HuggingFace/Salesforce AI Energy Score) is selection on the outcome — the precise sin §5 of the MVP draft forbids in collection. The paper preaches pre-registration and then proposes "approximately 40 result rows" with no frozen sample, no frozen selection rule, and no named second coder.

### F4 — "Base paper cost is exactly the three D-117 windows" is false by the repo's own numbers.

`docs/research_question_bank.md:1087` sizes the nearest existing item — **"Bundle contract as a standards contribution — the run-bundle layout + boundary table + strict validator packaged as a proposed artifact format for edge-LLM energy (MLPerf-Power-adjacent)" — at ~15–30 person-days**, and that is the *export* alone. The proposal additionally requires: machine-readable + human-readable renderer, completeness validator, comparability validator, a mutation-test suite with four named refusal classes, byte-linked artifact→label provenance, and a two-coder 40-row audit. Claiming zero marginal cost because no new night is needed conflates the scarce resource (nights) with the actually-binding one (Ed's desk hours), which the DESIGN-MEMO already shows is the critical path: gates U1–U7 (ledger session/binding, successor builder, pinset v2, multi-cell mint, prefill metric support, three-window regression, campaign packs) must all land *before* alpha runs.

Compounding this: "no hand-copied scientific numbers and byte-linked provenance" implies the renderer hooks the governed mint chain — `scripts/mint_floor_artifact_generalized.py` / `joulewise/detection_floor.py`, i.e. **U3, on the D-117 critical path**. The proposal never specifies whether the label layer is upstream (critical-path-perturbing) or a downstream read-only consumer of minted artifacts. That ambiguity is the difference between "free" and "delays the three windows."

### F5 — Governance-fence collision, unacknowledged.

The registry already carries this direction: **`APP-STANDARDS-CONTRIBUTION`** — status *candidate*, claim ceiling *"methodology artifact proposal"*, explicit fence: **"no claim to be the standard."** The proposal cites neither the row nor the fence, and titles itself *"A **Metrology-Complete** Energy Label"* with contribution 1 phrased as "A result is complete **only if** it binds…". That is a claim to *be* the standard, in the title and the first contribution.

Adjacent fences it also walks past: **`APP-MODEL-CARDS`** — "internal only until L4 replication… public version is killed until cross-lab replication"; and **C5-3.5** (`docs/research_question_bank.md:1050`), which the bank states "**gates every public-facing application (leaderboard, standard, audit service)**." A proposal whose whole selling point is existing-material compliance should have found the two registry rows that fence it.

### F6 — A standard nobody else can satisfy is a description of an instrument, not a standard.

The mandatory fields include an in-window bracketed pulse-train calibration status, a corner-widened attribution-limited detection floor, and a custody digest. On an nvidia-smi or RAPL setup, three of the twelve fields are not merely *absent* — they are **unproducible**. The paper proposes a universal reporting minimum derived from n=1 lab, n=1 machine, n=1 stack, and never tests whether the schema degrades gracefully anywhere else. The audit measures whether published rows *have* the fields; it never measures whether they *could*. External validity is the load-bearing question for any standards paper and this one does not ask it.

### F7 — Correlated single point of failure with the MVP.

All four label cells (1.5B/7B × prefill/decode) and the contrast verdict depend on alpha, beta, **and** gamma all passing. The same failure kills the MVP paper's §7. There is no degraded-mode plan: no "what the paper is if gamma refuses," no fallback to labels-over-refusals. Ironically, a refusal-rendered label would be the most interesting artifact the paper could produce, and it is not planned for.

### F8 — Precision failures inside a paper about precision.

- "**Five real label cells** plus a contrast verdict" — D-117 yields **four** cells (DESIGN-MEMO §"four-cell artifact", rows at lines 147–149) plus one contrast. The paper miscounts its own results in its contribution list.
- "approximately 40 result rows" — an unfrozen n in a paper whose thesis is pre-registration.
- The 141.29 J figure and the 5.81 J / ~4.0 J-lower-edge prefill numbers are correctly sourced and correctly labelled diagnostic (`CLAIMS_STATUS.md:63`; prefill SYNTHESIS). Credit where due — the factual base is clean. The 3.14/3.24/2.80 h budgets, 10+40 schedule, and 50-unique-bundle shape all reconcile with DESIGN-MEMO lines 259–271, 327.

### F9 — Venue analysis contradicts the project's own venue table, and the page budget makes the reuse plan physically impossible.

`docs/strategy/2026-08-06-impressiveness-roadmap.md` §"Venue ambition" already fixes the ladder with cited page limits:

- **CSCSU: 5 pages *including references*.** The proposal's core mechanism — "reuses the MVP draft's Sections 2–6 nearly intact" — cannot be executed twice inside 5-page budgets. At the capstone venue there is room for one paper, and §§2–6 are already spoken for. The reuse plan is not merely redundant; it does not fit.
- The roadmap names **EuroMLSys (6 pp excl. refs) and HotCarbon (5 pp excl. refs)** as "the natural near-term research target," and notes HotCarbon "needs a stronger sustainability-metrics argument" — which is arguably what a reporting-standards paper *is*. The proposal says "credible performance- or sustainable-systems workshop paper" and names **no venue at all**, missing the one the project already identified as its best fit.
- **ICPE full track**: the roadmap enumerates the qualifying deeper contributions — "held-out Q4 prediction, second-unit replication, or a successful mechanism study" — on top of C1–C8, cross-day stability, and artifact-ready release, at 28% acceptance. **A reporting label is not on that list.** The proposal invents its own ICPE-full criteria ("executable validator, reporting audit, artifact-quality release, and preferably external adoption") and then gates on external adoption, which is unreachable in a capstone timeline and is in any case fenced by C5-3.5.
- Roadmap **rank 3, "Artifact-evaluation-quality release" (4–6 weeks, 0 measurement nights)**, already covers the validator/renderer/reproducible-provenance work, and ICPE runs a dedicated artifact-evaluation track aligned to it. The proposal re-derives a large part of rank 3 as a novel paper contribution without citing it.

**Partial correction in the proposal's favour, which it did not claim for itself.** On the charge's question (a) — *can a standards paper without new measurements carry weight at the target venue?* — the answer is **yes, but only in the right track**. ICPE's **Emerging Research track** explicitly solicits "new ideas and vision papers on emerging research challenges" and states that some aspects may "remain open, possibly with limited or no evaluation" (it was formerly the Work-in-Progress and Vision track). **HotCarbon** explicitly solicits "research **and position** papers"; **LOCO** welcomes "new ideas and visions." So the genre is admissible — at Emerging/WIP and workshop tier, which is exactly where the roadmap already placed it and where the proposal declined to look. Two caveats: the **ICPE 2026 cycle has closed** (4–8 May 2026, Florence; research abstracts were due 3 Nov 2025), so the real target is ICPE 2027; and the sweep **could not find a single named ICPE paper that is purely a reporting standard with zero new measurements** — permitted by track scope, but unevidenced by precedent. Do not let that be asserted unsupported.

### F10 — It serves only the prohibitive half of Ed's goal.

Ed wants an *energy-honest leaderboard*. This paper's comparability procedure is a list of refusals: no boundary substitution, no tokenizer-blind J/token ranking, no cross-boundary ranking. It explicitly disclaims public cross-device leaderboards and declares the WT310E "**not a dependency**." Cost-honest, but it leaves the reader with "you may almost never compare" and no constructive bridge to what a *valid* comparison would look like. That reads as nihilism to a systems referee, and it under-serves the very goal the proposal claims to serve best.

---

## STRENGTHENING MOVES (if kept)

**1. Dissolve contribution 1; re-cut the standalone around the floor-gated refusal, not around a label.**
Fold the schema into MVP §6 — where its every field already lives — and release the validator as an MVP artifact. If a standalone is still wanted, build it on the one thing the sweep found genuinely uncovered (~95%): **no existing ML-energy reporting regime states a detection floor or gates a directional claim on it, and the software-counter regimes the entire ML literature runs on (CodeCarbon, RAPL, `powermetrics`) are precisely the ones with no calibration story.** That is **one** contribution, not four. Its comparability rule must be gated on floor/uncertainty, explicitly contrasted with AI Energy Score's configuration-equivalence partition and MLPerf's Closed/Open × Available/Preview/RDI divisions. Title it around refusal ("When Two Energy Numbers May Not Be Compared"), never "nutrition label" — that framing is occupied by a funded four-institution initiative. And import SPECpower's ≤1%-uncertainty / NIST-traceable-calibration rules and the RAPL-validation literature **as the standard you are carrying into a new regime**, not as a gap you discovered. Non-negotiable: cite and differentiate arXiv:2605.11733 (May 2026) and Papadopoulos et al. (SPEC-RG/TSE 2021) in the abstract. This also cures F2 — MVP contributes measurements, this contributes a decision procedure, and the overlap becomes a citation instead of duplicated §§2–6.

**2. Make the audit capable of failing, staff it, and stop pretending n=40 is a study.**
Freeze sample size, source list, and selection rule *before* coding, in the repo, under the project's own pre-registration discipline. Include the strongest-practice reporters (MLPerf Power submissions, SPECpower results, AI Energy Score, MLCommons result JSON) alongside the four weak ones — an audit that excludes best practice is not evidence. Change the scored question from *"is the field present in the row?"* (foregone) to **"is the field *recoverable* from the artifacts the publisher released?"** — recoverability produces a real bifurcation instead of a uniform zero. Position n=40 as an **instrument demonstration** with the sample size stated as a limitation, and cite Misinformation by Omission (754), Counting Carbon (95), and BetterBench (46 criteria) as the scale precedent you are deliberately not competing with — otherwise a referee will do it for you. Read AI-CARE (arXiv:2602.16042) and the NREL Beginner's Guide (arXiv:2412.17830) in full before committing; either could pre-empt this contribution outright. On staffing: name the second coder now; if there isn't one, drop κ, run single-coder, and publish rubric plus full coding sheet so others can re-code — cheaper and more honest than an unstaffed inter-rater claim.

**2b. Pick the venue the project already picked, and the track the genre actually fits.** Target **HotCarbon** (5 pp excl. refs; explicitly solicits position papers; explicitly wants a stronger sustainability-metrics argument — a refusal calculus for energy comparisons is exactly that) or **EuroMLSys** (6 pp). For ICPE, target the **Emerging Research track at ICPE 2027** — it takes vision papers with limited or no evaluation by construction; the 2026 cycle is closed and the full research track's qualifying deeper contributions (held-out Q4 prediction, second-unit replication, mechanism study) do not include this. Send the validator to **ICPE's artifact-evaluation track** as roadmap rank 3, not as a research-paper contribution. Verify ICPE 2027 page limits directly — the sweep could not confirm them.

**3. Buy external validity with hardware that is already idle — the negative-label demonstration.**
The proposal declares the RTX 3080 Ti "irrelevant." That is the missed opportunity. Render a **deliberately incomplete label** for an nvidia-smi measurement on the owned 3080 Ti, showing exactly which mandatory fields cannot be produced on that instrument, and what the comparability gate then refuses when asked to rank it against the M3 Max. This requires no quiet night, no calibration bracket, no floor, no claim — it is a *negative* demonstration, which is the project's native genre. It converts F6 from a fatal objection into the paper's sharpest figure, gives the audit a live worked case, and partially answers F9 by showing concretely what a bridge would have to supply. Failing that, retitle away from "metrology-complete" and adopt the registry's own ceiling language ("a proposed metrology disclosure schema; not a claim to be the standard") to clear F5.

---

## KILL CRITERIA I WOULD ADD

- If a side-by-side of contribution 1's field list against MVP draft §§1,3–6 does not surface **at least three fields the MVP does not already mandate**, the standalone paper is dead on arrival — do not spend desk hours on it. (On my read: zero.)
- If the label serialization touches `mint_floor_artifact_generalized.py` / `detection_floor.py` rather than consuming minted artifacts read-only, kill it until after the three D-117 windows land. Nothing goes on the critical path for a formatting layer.
- If a pilot coding of 8 rows across the four proposed sources yields uniform zeros on the metrology fields, the audit is confirmed unfalsifiable as designed — re-scope to recoverability (move 2) or drop contribution 4.
- **Read arXiv:2605.11733 (Energy-to-Token position paper, May 2026) and arXiv:2602.16042 (AI-CARE, Feb 2026) before any desk hour is spent.** If either already prescribes a mandatory-field set for LLM inference energy reporting with a completeness evaluation, this direction is pre-empted and should collapse to an MVP section immediately.

exec
/bin/zsh -lc "sed -n '1,110p' ../portfolio/rev-energy-nutrition-label.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review — `prop-energy-nutrition-label.md`

**Reviewer:** Opus 5 counter-reviewer (adversarial charge: kill it)
**Target:** "Before Joules Become Rankings: A Metrology-Complete Energy Label for Consumer LLM Inference"
**Ground truth:** desk checkout at `.../scratchpad/desk` (main), D-117, DESIGN-MEMO, `docs/paper/draft-v1.md`, `CLAIMS_STATUS.md`, `docs/research_question_registry.md`, `docs/research_question_bank.md`

---

## VERDICT: **WEAK**

Precisely: **KILL as a standalone paper in its proposed four-contribution form; WEAK-but-keep as an MVP section + released artifact, with one narrow re-cut worth a workshop/Emerging-track submission.**

It is the only direction in the fan-out that hits Ed's leaderboard/reporting axis head-on at zero marginal quiet-night cost, and it is scrupulously compliant with the existing-material constraint — that is why it does not get a flat KILL. But it is not a second paper. Stripped of ceremony, its four contributions reduce to: a schema whose every field is *already mandated in the MVP draft* and ~70% covered externally by MLPerf Power / SPECpower / AI Energy Score; a comparability rule ~65% covered by AI Energy Score's own same-hardware/same-task/same-size-class procedure; a re-rendering of the MVP's own D-117 results; and a 40-row audit dominated ~19× in scale by a June-2025 754-model audit, whose conclusion is known before it runs. A May-2026 position paper already occupies the genre. What genuinely survives is **one field and one rule** — the detection floor and the claim gate that refuses directional language below it.

### Scores (1–10)

| Axis | Score | One-line |
|---|---|---|
| Novelty | **2** | Every schema field is already in MVP draft §§1,3–6, and externally the label is ~70% covered by MLPerf Power + SPECpower + AI Energy Score, the comparability procedure ~65% covered, and the audit dominated 19× in scale by an existing 754-model audit. A May-2026 position paper already occupies the genre. Survivor: one field and one rule. |
| Feasibility | **6** | Zero extra nights is real and good. But the cost is misstated by the repo's own sizing, the two-coder audit is unstaffed, and the whole paper is a hostage to all three D-117 windows passing. |
| MVP leverage | **6** | Maximum possible reuse — which is precisely the problem: total reuse with near-zero incremental yield is a duplicate-publication hazard, not leverage. |
| Venue fit | **3** | Self-assessment is commendably honest in tone, but contradicts the project's own venue table: CSCSU's 5-pages-including-references budget makes the "§§2–6 reused nearly intact" plan physically impossible, no workshop is named (EuroMLSys/HotCarbon are already identified in-repo), the invented ICPE-full criteria do not match the roadmap's, and the dual-submission collision with the MVP paper is never mentioned. |
| Original goals | **7** | Best-in-class on the reporting axis — but delivers only the prohibitive half of the critique ("you may not compare") with no constructive bridge, and serves no mechanism axis. |

---

## FATAL FLAWS

### F1 — Contribution 1 is a table of contents for the MVP paper. (decisive)

The proposal's headline contribution is "a falsifiable minimum reporting schema" binding: *boundary, gross-J/request estimand, workload, phase, physical unit, OS/runtime/model/quantization/tokenizer identity, calibration bracket and status, floor decomposition, claim interval, gate verdict, custody digest.*

Every single one is already mandatory in `docs/paper/draft-v1.md`:

| Proposed "new" field | Already mandated at |
|---|---|
| measurement boundary | §3 "Measurement model and boundary"; §6 final para |
| gross-J/request estimand | §1: "Gross joules per request are the primary energy metric" |
| workload / phase | §3 (runtime-emitted phase events) |
| physical unit, OS build, runtime/library versions, model artifact hash, quantization, tokenizer identity, sampler policy, telemetry backend | §6 final para — verbatim list, with "Silent omission is not permitted" |
| calibration bracket + status | §3 "The pre- and post-window calibrations form a bracket…"; freshness/authentication rules |
| floor decomposition | §4 + the **LABELLED** publication path (corner-widened value, `floor_source`, decomposition required) |
| claim interval + gate verdict | §4 "effective clearable effect = F_cell + B_claim"; "reported as *not resolvable*" |
| custody digest | §5 "Cryptographic hashes bind those files to the campaign manifest" |

Coverage is 13/13. Contribution 1 contributes **zero novel fields**. What actually remains is serialization + a validator — engineering, not a scientific contribution. A referee who reads both documents will say this in one sentence and it will end the paper.

### F2 — Salami slicing / duplicate submission, unaddressed.

The proposal states it "reuses the MVP draft's Sections 2–6 nearly intact" and consumes the identical D-117 dataset. Relative to the MVP paper it therefore has **no new measurements, no new method, and no new data** — only a new output format for the same numbers. Two papers sharing §§2–6 near-verbatim and one dataset, submitted to a capstone and then ICPE, is a live ACM prior/concurrent-publication problem. The proposal never names the risk, never proposes a partition of contributions, and its "what is new" list (schema, comparability rules, mutation evaluation, audit) is exactly the list F1 just dissolved.

### F2b — Novelty against external prior art, using the project's own related-work section.

I do not need an outside literature search to establish this; the MVP draft convicts the proposal. Draft §2 and §8 state that **MLPerf Power and SPEC already require** "a qualified analyzer, uncertainty evaluated at the observed load, fixed measurement ranges, synchronized clocks, sufficiently long intervals, invalid-sample accounting, and explicit treatment of battery-backed systems," and that their governing principle is precisely *reject-on-missing-evidence per run*. Map that onto contribution 1:

| Label field | Covered by MLPerf Power / SPEC? |
|---|---|
| measurement boundary (SUT definition) | **yes** |
| calibration/qualification state | **yes** (qualified analyzer, fixed ranges) |
| uncertainty interval | **yes** (uncertainty at observed load) |
| stack/system identity | **yes** (submission descriptor) |
| workload identity | **yes** |
| invalid-sample / validity accounting | **yes** |
| phase (prefill/decode) identity | no — but this is the MVP's contribution, not the label's |
| detection-floor decomposition | **no** |
| explicit gate verdict / refusal of direction | **no** |
| custody digest | partial (submission bundles) |

So on the repo's own related-work text, the genuine novelty of the schema is **three fields**, two of which (floor decomposition, gate verdict) are the MVP paper's own C-ii and one of which (custody digest) is its C-iii. The label contributes the *serialization*, not the *fields*.

### F2c — External prior-art survey: worse than F2b. (novelty 3 → 2)

A dedicated literature sweep confirms and deepens this. Coverage of the proposed fields:

| Proposed label field | External coverage |
|---|---|
| measurement boundary | **~90%** — MLPerf `power_measurement.adoc` (SUT = everything LoadGen sensitizes, measured AC-side at the wall); SPECpower run/reporting rules; **ISO/IEC 21031:2024 (Software Carbon Intensity)** mandates a declared boundary + functional unit; AI Energy Score declares GPU-only |
| stack identity | **~95%** — SPECpower's rules are *strictly more exhaustive* (CPU/mem/storage/NIC/PSU, OS+JVM versions and flags, firmware, every power-management setting, non-default tuning with justification); MLPerf `system_desc` + `power_settings`; Model Cards |
| calibration state | **~75%** — SPECpower requires **annual NIST-traceable calibration**, an accepted-analyzer list, crest factor ≥3 |
| uncertainty interval | **~55%** — SPECpower (**2008**) mandates ≤1% average uncertainty and **no more than 5% of samples above 1%** |
| claim verdict | **~25%** — SPECpower gates *run validity* (invalid runs cannot be published); MLPerf and AI Energy Score gate *comparability by configuration partition* |
| custody digest | **~50%** — MLPerf's compliance checker computes client/server source and results checksums and validates the full PTD transcript; AI Energy Score requires an unaltered-logs attestation |
| **detection floor** | **~5% — this, and only this, is the contribution** |

Three specific threats the proposal must survive and never mentions:

1. **AI Energy Score** (Hugging Face + Salesforce + Cohere + CMU; launched at the Paris AI Action Summit, 10 Feb 2025). A *literal energy label with a literal label generator*: model, Wh/1,000 queries, task, scoring date, benchmarking hardware, 1–5 stars, verification link — **plus an explicit comparability decision procedure** (same hardware/H100, same task, text generation only within size class; alternative hardware permitted but ineligible for the leaderboard) **plus a custody attestation**. It lands on contributions 1 *and* 2. The "energy nutrition label for AI" framing is occupied.
2. **"Position: LLM Inference Should Be Evaluated as Energy-to-Token Production"** (arXiv:2605.11733, **May 2026**) — a position paper prescribing mandatory reporting fields for LLM inference energy. Nearest competitor in genre *and* recency; three months old. Must be cited and differentiated in the abstract or the paper is dead on arrival.
3. **Papadopoulos et al., "Methodological Principles for Reproducible Performance Evaluation in Cloud Computing"** (SPEC-RG-2019-04 / IEEE TSE 2021, ICSE 2020 Journal-First) — eight principles, a decision procedure, and an audit of an existing benchmark against them, from **SPEC's own research group**. The exact structural analogue of this entire proposal. Cite it or be caught. (Adjacent: Raasveldt et al., "Fair Benchmarking Considered Difficult", DBTEST@SIGMOD 2018 — a pitfalls-and-detection paper with no new system.)

Contribution 2 survives **only** if its gating predicate is the floor/uncertainty rather than configuration equivalence. That distinction is the paper's whole spine and the proposal never states it.

*Favourable finding, and it cuts against this paper:* the sweep found **no peer-reviewed validation of Apple `powermetrics` accuracy** — only Apple's own "estimated and may be inaccurate" man page, the ml-energy/zeus RFC #159 thread, community IOReport findings (1 mJ resolution; sub-10 ms windows dominated by quantization noise), and "Apple vs. Oranges" (arXiv:2502.05317) using it while flagging its imprecision. That void is real and citable — but it is **the MVP paper's** novelty, not the label paper's. Which is F1 again.

### F2d — Contribution 4 is dominated ~19× in scale by an existing audit.

- **Luccioni, Gamazaychikov, Alves da Costa, Strubell, "Misinformation by Omission"** (arXiv:2506.15572, June 2025): **754 models, 2010–Q1 2025**, three-level Direct/Indirect/No-Disclosure taxonomy, OpenRouter usage-weighted (84% of token traffic served by No-Disclosure models).
- **Luccioni & Hernandez-Garcia, "Counting Carbon"** (arXiv:2302.08476): **95 models**.
- **BetterBench** (NeurIPS 2024 D&B): AI benchmarks scored against **46 criteria**.

"Approximately 40 rows" is a pilot, not a study. Defensible *only* if reframed so the **instrument** — scoring against fields nobody else checks (floor, calibration bracket, custody) — is the contribution and n=40 is a stated limitation, not a headline. Two flagged unknowns that could make this worse and need a targeted read before funding: **AI-CARE** (arXiv:2602.16042, Feb 2026, "carbon-aware reporting evaluation metric") could not be characterized past its abstract and may collide head-on; and the **NREL "Beginner's Guide to Power and Energy Measurement and Estimation for Computing and ML"** (arXiv:2412.17830, Dec 2024) already covers at-the-wall vs. on-device boundaries, sampling strategy, and common error sources, closing with a call for "measurement methods and standards for facilitating robust comparisons" — i.e. it published this proposal's motivation twenty months ago.

### F3 — The audit cannot fail, and its sample is rigged.

Contribution 4's stated falsification condition: *"the critique fails if prevailing reporting already supplies the proposed mandatory evidence reliably."* Nobody publishes a corner-widened detection floor with a two-gate claim verdict and a custody digest, because nobody built JouleWise. The disconfirming outcome is foreknown to be impossible. Two coders and a κ statistic applied to a foregone conclusion is bookkeeping dressed as an experiment.

Worse, the sample is drawn from "the four nearest reporting systems discussed in the MVP draft" — i.e. TokenPowerBench, ML.ENERGY, Silicon Showdown, Intelligence-per-Watt: the four the MVP already criticizes for exactly these omissions (draft §2.3, §8.1). Auditing only your own straw men and excluding the strongest-practice reporters (MLPerf Power inference-power submissions, SPECpower results, HuggingFace/Salesforce AI Energy Score) is selection on the outcome — the precise sin §5 of the MVP draft forbids in collection. The paper preaches pre-registration and then proposes "approximately 40 result rows" with no frozen sample, no frozen selection rule, and no named second coder.

### F4 — "Base paper cost is exactly the three D-117 windows" is false by the repo's own numbers.


exec
/bin/zsh -lc "sed -n '1,300p' ../portfolio/rev-floor-methodology-general.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review — "From Repeatability to Resolvability: Detection Floors for Software Energy Counters"

Reviewer: Opus 5 counter-reviewer (portfolio referee, adversarial charge).
Target: `scratchpad/portfolio/prop-floor-methodology-general.md` (final block, L5903–5953).
Ground truth: `scratchpad/desk` @ main. Every repo claim below is cited by path.

## VERDICT: **WEAK** — the framing is the best in the portfolio; the evidence plan for it is not fundable, is fenced by a ratified decision, and collapses into the MVP in its most likely branch.

Scores (1–10): **novelty 6 · feasibility 3 · mvp_leverage 4 · venue_fit 4 · original_goals 5**

"From repeatability to **resolvability**" is a genuinely good title and a genuinely
good idea — it is the sentence a JouleSort co-author would underline. Everything
after the title is the problem.

---

## F1 (FATAL). The paper's novel finding is the one thing synthetic pulses cannot generalize.

JouleWise's central empirical result is not "software counters are noisy." It is
that `powermetrics` is **attribution-limited** — ~30 ms of phase-edge uncertainty
across a ~33 W transition misassigns ~1 J *across a boundary between two phases
of one request*, and repetition cannot average it away. That is a statement about
**phase attribution**, and it is what makes the paper more than a RAPL-in-Action
replication.

The proposed portability battery is explicitly **not** LLM work: *"the portability
kernels are separately identified instrument-characterization workloads."* It is
pulse drivers, absolute repeats, identical-label ABBA nulls, and held-out duration
deltas at `0/0.5F/1F/2F/4F`. Synthetic duration deltas **have no prefill/decode
boundary**. Therefore the NVML and RAPL legs can demonstrate transfer of
repeatability, quantization/update-granularity handling, wrap behaviour and drift
— the *easy, already-published* half — and **cannot** demonstrate transfer of the
attribution-limited finding, the half that is the contribution.

The proposal notices this asymmetry for the wall meter (*"it cannot validate phase
attribution"*) and then fails to apply the identical test to its own new backends.
A referee will apply it. The abstract promises a counter-agnostic *detection-floor
calculus* whose distinguishing term is boundary attribution; the experiment
validates every term except that one.

There is also a circularity: the calibration signal and the validation signal are
both generated by the same pulse driver. On the Mac, the acknowledged risky step
is **pulse-to-workload transfer**. On NVML/RAPL there is no workload at all, so
the battery tests the pulse instrument against itself.

## F2 (FATAL). NVIDIA in the paper's claims is prohibited by a ratified fence the proposal never cites.

`TASK_QUEUE.md` A50 / `NVIDIA-PORTABILITY-01` is **BLOCKED — ED-NVIDIA-RATIFY**,
and carries this fence verbatim:

> *"**Fence:** No NVIDIA energy number enters the December paper's claims table;
> S2 never binds the submission; mixed-boundary sums are never presented as split
> totals (Consult synthesis: **December claims table stays Mac-only (both
> lenses)**)."*

Sequencing is also already ruled: S2 (the single-node RTX instrument-portability
study) runs **only after the Mac claims table closes and Ed ratifies**, under four
named Sol gates, from the 2026-08-02 two-lens consult with magistrate synthesis.
It is filed under **P3 Research Expansion**.

The proposal makes NVML portability **contribution #3** and puts it in the results
table. That is a direct collision with a ratified fence and a decision Ed has not
made. Under rule 11 this is not a lieutenant-level call. A proposal that reverses
a ratified fence must argue for the reversal; this one appears unaware the fence
exists.

## F3 (FATAL). RAPL has zero capability evidence in this repo, and half the "three-counter" contribution is vapor.

Grepping the tree for `rapl|powercap|energy_uj`: every hit is a **related-work
citation** (`docs/paper/draft-v1.md` L30/L180 — RAPLInAction, Jay & Ostapenco) or
a downstream copy. There is **no RAPL adapter, no capability probe, no CPU
identification, no OS identification** for the desktop rig anywhere in the repo.
The proposal itself concedes RAPL is "conditional on the desktop CPU and OS
exposing `energy_uj` … through Linux powercap" — but the repo's only CUDA path is
a **vLLM adapter over an SSH node-worker protocol**
(`joulewise/adapters/__init__.py`), which implies a remote Linux-ish host that has
never been described, let alone probed.

A three-counter paper where counter #3 is a coin flip resolved by a desk gate is a
two-counter paper with optimistic framing. The proposal's own kill criterion
("Kill the three-counter claim if RAPL is unavailable") is honest and should be
read as the base case.

## F4 (FATAL). The cost estimate is off by roughly an order of magnitude, and the repo proves it.

The proposal budgets *"two estimated 2–3-hour desktop sessions"* to reach
**mint-able floors** on two brand-new counters. Measure that against what one
well-understood counter has actually cost this project:

- First commit **2026-06-09**. Today is **2026-08-07**.
- `CLAIMS_STATUS.md` §1 — *"VALID — minted, mainline, citable: **NONE at this
  checkpoint.**"*
- `WINDOW_STATUS.md` — windows A and B collected, **both verdicts FAILED**;
  window A *permanently* non-claim-bearing; window B's re-evaluation stopped with
  its license exhausted.
- D-078 voided the time anchors on the powermetrics corpora; ~43/50
  su-calibration bundles were screensaver-contaminated; D-110 made mint #1
  retroactively non-claim-bearing; D-117 then superseded D-110's re-mint order as
  **structurally unsatisfiable**, replacing it with three fresh windows.

Two months, multiple voided corpora, four decision-log entries of adjudication,
and the flagship instrument still has zero citable numbers. NVML on this project
has **never touched live hardware at all**: the 2K stream log states it is
*"fixture-first / provisional-contract — NVIDIA hardware is arriving but NOT yet
available. Everything is built CI-safe against fixtures/fakes; all protocol pins
are PROVISIONAL until first live hardware validation"*
(`docs/stream_logs/2026-07-07-2k-nvidia.md`). Proposing that two novel counters
reach mint-grade floors in one evening each is not a plan; it is the same
optimism the project's own history has already falsified twice.

Compounding it: the existing adapter is `joulewise/adapters/nvidia_smi.py` —
**sampled power via nvidia-smi over SSH**. The proposal wants
`nvmlDeviceGetTotalEnergyConsumption`, a *cumulative millijoule* counter with
different semantics (wrap, update cadence, board boundary). That is a new adapter,
a new reducer path, a new custody/mint family, and a new quiet-device protocol for
a **desktop** — a far dirtier quiet environment than a closed MacBook (case fans,
GPU idle power in the tens of watts, an OS full of daemons). None of this is
budgeted.

## F5 (MAJOR). Hardware availability is asserted, not established.

*"Owned hardware is sufficient for the core: the M3 Max for D-117 and the RTX 3080
Ti rig for NVML."* The repo is internally inconsistent and, on either reading,
less favourable than that sentence:

- `docs/decision_log.md` D-073 (2026-07-16) makes the 3080 Ti (12 GiB) part of the
  **primary fleet**.
- `PROJECT_STATUS.md` L563 still says *"the 3080 Ti is a separate, **borrowed**
  card used only for Phase 3's interconnect sweep"*, names `nvidia_3050` as *"the
  owned always-available NVIDIA target"*, and lists *"NVIDIA / Jetson Orin device
  access evidence — **the one hard gate left**"* among external blockers.
- The risk register carries *"3080 Ti borrow window slips"*; `TASK_QUEUE.md` L230
  says *"Do not schedule the 3080 Ti borrow window before Stage 3.0 verdicts."*

So access is a **time-boxed borrow window gated on unfinished verdicts**, not a
machine on the desk. A proposal that makes it a load-bearing dependency must
resolve this contradiction and schedule against the window; this one does not
mention it.

## F6 (MAJOR). Double-publication / self-collapse, admitted in the text.

The proposal states it *"reuses MVP §§3–5 nearly intact, the D-117 results
section, custody machinery, attribution-limited finding, and most of §6"* — i.e.
essentially all of `docs/paper/draft-v1.md` (§3 calibration, §4 floor composition,
§5 fail-closed protocol, §6 instrument characterization, §7 demonstration). New
material is one abstraction layer plus the portability battery.

Then: *"**Without portability data, this is the capstone paper's methods-first
framing.**"* That is the proposal conceding the charge. In the branch where RAPL
is unavailable (F3) and NVML is fenced (F2) — the *modal* branch — this paper is
the MVP with a better title and a renamed §1. The capstone is not archival, so
there is no formal self-plagiarism bar; the problem is **expected value**: Ed
would spend the extra desk program to end up submitting the paper he already has.

Novelty ceiling is also lower than claimed. Software-counter floor/validation
methodology across RAPL and NVML is a populated area (RAPL in Action; Jay &
Ostapenco; the Illusion-of-Power-Capping line already cited in
`draft-v1.md` §8). JouleWise's differentiator is *phase* resolvability on Apple
silicon — which F1 shows this design does not port.

## What is actually good here

- **The reframe itself is the strongest asset in the portfolio.** Recasting the
  paper's thesis as "software counters are admitted as instruments only after
  workload-local calibration establishes what they can *resolve*" elevates a
  case study into a methodology, at **zero measurement cost**. This is a pure
  writing win and Rivoire-shaped.
- The **held-out effect ladder** at `0/0.5F/1F/2F/4F` with a predeclared pass/fail
  rule is a real, falsifiable validation instrument the MVP currently lacks.
- The refusal-taxonomy contribution (#4: stale calibration, wrap, unsupported
  fields, reordered members, contaminated nulls, substituted evidence) is
  executable **entirely at the desk** against the existing synthetic regression
  suite — genuinely new, genuinely cheap.
- Correctly refuses to transport the Mac's ~5 J bar to another backend, and
  correctly refuses cross-boundary energy *rankings* in favour of comparing
  *resolvability*. Both are the right calls.
- Honest that the wall meter is not a dependency and cannot validate phase
  attribution.

## Three strengthening moves if kept

1. **Run the held-out ladder on `powermetrics`, not on new counters.** Add a
   fourth Mac window that plants predeclared effects at ≈0, 0.5F, 1F, 2F, 4F —
   using **workload length**, the free lever, on the already-admitted Qwen2.5
   models — and validate that the composed floor accepts what it should and
   refuses what it should. This is the paper's missing validation, it is
   *within-instrument* so it tests the attribution term F1 says the ports cannot,
   it needs no new hardware, no new adapter, no fence reversal, and one night.
   It turns "we composed a floor" into "we composed a floor **and showed it is
   calibrated**" — which is the actual leap from repeatability to resolvability.
2. **Demote NVML/RAPL to a desk-only capability appendix with zero claims — which
   is what A50 stage S1 already authorized and reports as landed.** Write the
   backend-neutral counter schema, the counter-mechanics analysis (wrap, cadence,
   Ampere's documented ~1 s power averaging, `NOT_SUPPORTED` paths), and a
   published capability probe, and state as a *prediction* what each backend's
   floor structure would be. That satisfies the generalization framing, respects
   the ratified Mac-only fence, costs zero nights, and leaves S2 as declared
   future work with a ready protocol. If Ed later ratifies S2, the paper's ICPE
   version inherits it.
3. **Pick the venue before the evidence, and stop hedging across three tiers.**
   Committed as "MVP + held-out ladder + desk-only portability appendix," this is
   a strong capstone and a credible **ICPE Emerging Research / EuroMLSys** entry
   under the roadmap's own venue table. The ICPE full-track claim should be
   dropped from this proposal entirely: the roadmap's full-track row requires
   C1–C8, cross-day stability, and an artifact-ready release, none of which this
   plan funds, and F1 shows the portability legs would not carry it anyway.

## Bottom line

Take the title, the resolvability framing, the held-out ladder and the refusal
taxonomy — all of which are excellent and nearly free. Reject the portability
battery: it validates the wrong half of the contribution, breaks a ratified fence,
depends on a counter with no capability evidence and a rig with a borrow window,
and is costed at roughly a tenth of what this project's own history says a new
instrument costs. Executed as reframe-plus-ladder, this is not a competitor to the
MVP — it is the best available **upgrade** to it.

exec
/bin/zsh -lc "sed -n '1,380p' ../portfolio/rev-kv-context-energy.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review: "The Cost of Remembering: Floor-Gated Context Scaling of Decode Energy on Apple Silicon"

Reviewer: Opus 5 counter-reviewer (adversarial charge: try to kill it).
Ground truth: desk checkout at `89f28bf`; D-117 (end of `docs/decision_log.md`);
`docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`;
`docs/paper/draft-v1.md`; `CLAIMS_STATUS.md`; `docs/research_question_registry.md`
(rows `RQ-KV-GROWTH`, `C5-1.2`, `C5-2.11`).

**VERDICT: WEAK** (borderline KILL as designed; rebuildable to VIABLE).

This is the more careful of the two proposals — its window arithmetic is honest, its
single-request compliance is clean, and it is the only one in the pair that serves an
original Ed axis. It nevertheless fails on two independent grounds, either of which is
sufficient: (a) an untreated confound that is perfectly aligned with the hypothesised
direction, and (b) an effect that is a ~12–25% perturbation on a large baseline,
measured against floors that the project's own minted diagnostics suggest scale with
that baseline. It also spends two nights collecting data that is unclaimable unless a
transport rule it does not yet have is ratified.

---

## 1. Fatal flaw A — prefill thermal carryover is confounded *in the hypothesised direction*

The proposal names three things it must separate ("position vs cache-size vs
attention cost") only implicitly, and treats none of them. Let me do the arithmetic,
because it reorders the whole problem.

**Position (RoPE) is negligible.** No meaningful energy.

**Attention FLOPs are negligible.** For 7B at 8192 context, per decode step:
attention ≈ 2 × 8192 × 512 (KV dim) × 2 (K and V) × 28 layers ≈ 4.7e8 FLOPs, against
weight FLOPs ≈ 2 × 7e9 = 1.4e10. That is **~3%**. Attention *compute* is not a
candidate cause.

**Memory traffic is the only real hypothesis.** The proposal's KV arithmetic checks
out: 1.5B = 28 layers × 2 KV heads × 128 dim × 2 (K,V) × 2 B = 28 KiB/token; 7B = 4 KV
heads → 56 KiB/token; at 8192 tokens, 224 MiB and 448 MiB resident. Per decode step
this adds ~25% (1.5B: 0.224 GiB vs ~0.9 GB weights) and ~11.5% (7B: 0.448 GiB vs
~3.9 GB weights) to streamed bytes.

**But the rival cause is untreated and is the size of the effect.** In the B arm, the
decode phase is preceded *within the same request* by an 8192-token prefill. For 7B
that is ~1.15e14 FLOPs — on the order of 15–30 s of sustained high-power GPU work
(my estimate, flag as uncertain) at a materially higher package power than decode.
In the A arm, the 128-token prefill is sub-second. **Decode in the B arm therefore
begins on a hotter die, at a different DVFS/residency operating point, every single
time.** Hotter silicon leaks more; the direction is *the same* as the hypothesised KV
effect.

This confound is immune to every control the proposal lists:

- **ABBA counterbalancing** cancels linear *time trends across members*. This is a
  deterministic *within-member* carryover, locked to condition, not to order. ABBA
  cannot touch it.
- **NEG8 bound corpus, start/mid/end references, drift allowance** all characterise
  *whole-window* drift. This is a per-member state difference.
- **Fresh pre/post calibration** bounds edge placement, not thermal state.

Contribution 4 — "a quantitative link between analytical resident-KV size and
observed decode energy" — is exactly the claim this guts, because *prefill thermal
load is also monotone in prompt length*. A good fit to KV bytes is, in this design,
an equally good fit to prefill thermal work. The two candidate causes are perfectly
collinear across every cell. The paper cannot distinguish "remembering costs energy"
from "the machine that just did a big prefill decodes hotter."

The proposal does honourably refuse module attribution ("it must not be renamed an
'attention energy fraction'"), which is the registry's stated forbidden upgrade for
`RQ-KV-GROWTH`. But this is not module attribution — it is a rival cause for the
*entire* whole-phase effect.

**A second, lesser rival cause:** decode at 8192 context is *slower per token*, so the
decode phase is longer. A model with constant mean decode power and longer duration
predicts the same energy slope with no KV-specific energy at all. The proposal lists
mean decode power as a secondary metric but never states the discriminating
prediction, so the result will be uninterpretable either way.

## 2. Fatal flaw B — the base windows carry no floor for the family they measure

Each proposed window is: 10 ABBA blocks of 128-vs-8192 (40 members) + 5 absolute
members each at 1024 and 4096 (10 members). That is **zero A=A null blocks and zero
absolute members in the 8192-context condition family** — no comparative floor
component, no absolute floor component, for the family in which the entire claim
lives.

The plan is to transport D-117's comparative null floor from the 128-prompt decode
family to "the otherwise identical long-context decode family." It is not otherwise
identical. Draft §4 defines a condition family as "the same telemetry backend,
metric, window type, **workload profile**, and stack identity"; the DESIGN-MEMO's
claim-eligibility list binds "exact **workload parameters**, model/tokenizer
revision, seeds, quantization, runtime, sampling, and telemetry mode." Prompt length
is a workload parameter. And the memo already ruled the exactly analogous case:

> "The floor riders here use the prefill phase of the 128-prompt decode workload.
> They **do not automatically transport to a prospectively defined 256-token
> contrast.** The fourth plan needs either exact matching prefill floor cells or a
> separately predeclared and justified transport rule."

If 128 → 256 does not transport automatically, 128 → 8192 does not.

The proposal *does* list this as a pre-quiet-time kill criterion, which I credit —
that is more honest than its sibling. But it then budgets the remedy as "a sixth
night… contingency," and the arithmetic is wrong: a long-context decode floor family
is 10 absolute + 40 null = **50 members ≈ one full window, per model**. The
contingency is nights **six and seven**, not six. Realistic headline cost is 7, not 5.

Worse, the ordering is inverted relative to risk. The two base windows are worthless
without a rule the project has not written. The ratification is *desk work and free*;
the nights are the scarce resource. Nothing should be armed until the transport rule
exists in ratified form — or, better, until the windows no longer need one (§ moves).

## 3. Effect sizes vs the bar — the interior points are dead and both endpoints are coin flips

The proposal's expectation table is asserted, not derived. Deriving it from the
project's own anchors changes the conclusion, including the *ordering*.

Anchors: historical diagnostics imply ~51 J for 1.5B decode and ~192 J for 7B decode
at the D-117 shape (memo/proposal, both non-claim). If decode energy tracks streamed
bytes plus duration, the 8192−128 effect is roughly the traffic ratio:

| Stack | KV/weights at 8192 | Decode anchor | Traffic-ratio Δ estimate |
|---|---:|---:|---:|
| 1.5B | ~25% | ~51 J | **~13 J** |
| 7B | ~11.5% | ~192 J | **~22 J** |

(Both uncertain; an independent LPDDR5-class pJ/byte estimate gives ~1–5 J and
~2–10 J respectively, i.e. 2–3× lower, so treat 13/22 J as an upper band.)

Now the floors. The project's minted diagnostics are 1.5B absolute/comparative
3.823787 / 3.592138 J at a ~51 J decode (~7%) and 7B 6.294380 / 13.998036 J at a
~192 J decode (~3–7%). **Two stacks, 4× apart in magnitude, land in the same ratio
band — the floors look roughly proportional to phase magnitude, not fixed at ~5 J.**
The proposal itself flags this ("the nominal 5 J planning bar may not govern that
stack"), then does not follow it through.

Following it through:

| Contrast | Δ estimate | Plausible operative floor | Effect/floor |
|---|---:|---:|---:|
| 1.5B 8192−128 | ~13 J | ~4–5 J | **~2.9×** |
| 7B 8192−128 | ~22 J | ~14 J | **~1.6×** |
| either 4096−128 | ~6–11 J | ~4–14 J | **~0.8–1.5×** |
| either 1024−128 | ~1–3 J | ~4–14 J | **< 1** |

Three consequences, all bad for the proposal as written:

1. **The interior points (1024, 4096) are near-certain refusals.** The proposal
   concedes 1024 ("probably unresolved") but still spends 10 members per window on
   1024 and 4096 absolutes. Those 10 members buy nothing claim-bearing.
2. **Contributions 2 and 4 collapse in the modal outcome.** If only 128 and 8192
   resolve, you have a **two-point "curve."** You cannot fit "a pre-registered
   monotonic or piecewise context model" (Contribution 2) or establish "a
   quantitative link between analytical resident-KV size and observed decode energy"
   (Contribution 4) to two points. The modal paper is one resolved contrast plus
   three refusals.
3. **The proposal's stack ordering is inverted for funding purposes.** Its table
   shows 7B effects ~2× the 1.5B effects and implies 7B is the better bet. In
   *absolute* joules that is right, but under proportional floors what matters is the
   ratio — and 1.5B wins (2.9× vs 1.6×) because GQA gives it proportionally more KV
   per weight byte. **The 1.5B window is the one to fund first, not both.**

## 4. Does varying resident context stay inside the frozen single-request boundary?

**Yes.** I tried to break this and could not. Each member is one sequential request,
batch/concurrency one, no continuous batching, no cross-request cache reuse, no cache
eviction or quantization, no server. Prompt length is a workload-axis parameter, and
the harness is explicitly modular by axis. The new harness work (record initial KV
tokens, predicted/observed KV bytes, cache class and precision, MLX memory counters)
is metadata capture only — no measured-path change. The 512-token fixed output with a
fixed EOS policy is already the D-117 shape and the repo already distinguishes
requested vs runtime-observed emitted tokens.

Memory is a non-issue: 448 MiB KV + ~3.9 GB weights on a 128 GB machine. No swap, no
wired-memory pressure, no allocation confound.

This is the proposal's cleanest section, and it is a real advantage over
batching/serving directions in the same portfolio.

## 5. Per-length window cost arithmetic — the one piece that checks out

Reconstructing from the DESIGN-MEMO's alpha/beta columns: fixed operational overhead
is 8 (pre-cal) + 22 (12 NEG8) + 1 (bound eval) + 8 (start refs) + 5 (midpoint) + 8
(end refs) + 8 (post-cal) + 10 (untouched idle) = **70 min/window** before science.
Science runs ~1.7–2.0 min/member. The 4 h ceiling with the mandatory 20% margin caps
base occupancy at 200 min → ~130 min of science → **≈ 65–75 members per window**.

The proposal's 50 science members therefore fit, and its 3.4–3.8 h estimate is about
right: 20 of the 40 ABBA members carry an 8192-token prefill (+~25 s each for 7B, my
estimate) ≈ +8–10 min raw, so beta's 3.24 h → ~3.45 h; 1.5B lower. This is the only
budget in the pair I did not have to correct, and it leaves ~15–25 member-slots of
genuine headroom per window — which is exactly the resource that should be spent
fixing §2 (see moves).

**Lengths can share a window.** Nothing in the manifest contract forbids multiple
condition families in one window — D-117 alpha itself mints four cells from 50
bundles. The binding constraints are (i) the ~70-member occupancy ceiling and (ii)
the fact that different lengths mean different *members* (unlike alpha's four cells,
which ride the same 50 bundles at zero marginal runtime). So each new length costs
members linearly, and each new *window* costs 70 min of pure overhead. That
arithmetic argues for packing lengths — but only lengths that will actually resolve.

## 6. Novelty

Weak, and the proposal supplies the refutation itself: it cites Fernandez et al.
(ACL 2025) as showing "decode energy begins scaling with input length at sufficiently
large contexts" on an A6000. The headline finding is already published; what is new
is the hardware and the floor/refusal discipline. `draft-v1.md` §8 also notes
TokenPowerBench already "groups results by context length."

There is a genuinely novel angle here, but the proposal does not lead with it: a
*calibrated refusal boundary* for context effects — "on this stack, context effects
below ~X tokens of growth are not resolvable, and here is the instrument-grounded
reason" — is rare and is what Rivoire's bar rewards. Reframing around the refusal
rather than the curve would raise novelty and would also survive the modal outcome of
§3.

## 7. Existing-material and registry compliance

- **Registry rows exist and cap this work.** `RQ-KV-GROWTH` (banked, "L1/L2 chunked",
  forbidden: "no per-token joule claims; no attention-vs-FFN fraction from context
  slopes") and `C5-1.2` "Context-length energy scaling" (candidate, "L2/L3 if
  modeled", forbidden: "no short-prompt phase point claims"). The proposal respects
  the attention-fraction prohibition explicitly — credit.
- **Compliance gap 1:** `RQ-KV-GROWTH`'s registry note says the candidate riders
  "**stay attached rather than becoming independent rows**." This proposal promotes a
  banked rider into a standalone two-window campaign and a standalone paper. That is a
  registry promotion and needs one; the proposal never mentions it.
- **Compliance gap 2:** Contribution 2's "decode J/output-token" brushes
  `RQ-KV-GROWTH`'s "no per-token joule claims." The proposal's guard ("phase
  aggregates — not energy assigned to individual tokens") plus draft §1's
  tokenizer-scoped-companion-metric framing probably clears it, but it should be
  stated in the registry's own words, not paraphrased.
- **Compliance gap 3 — Contribution 1 is not this paper's.** "A claim-bearing
  calibration and floor characterization for two Qwen2.5 model sizes" is D-117's
  alpha/beta output, already funded and already the MVP's C-v material. Double-counted.
- **Cost omission shared with the sibling proposal.** "Five planned quiet nights"
  assumes the MVP closes in three. It does not: `draft-v1.md` §6 has **all six C-iv
  characterization rows marked `[PENDING WINDOW C]`**, and D-117 cl.4 schedules
  MET-WINDOW-C-01 *after* the three windows. The MVP is 3 nights **plus Window C**.
- **Correctly compliant otherwise:** owned hardware only; wall meter correctly
  declared a non-dependency with the right reason (a wall meter validates totals, not
  the prefill/decode split — draft §8); §§3–5 reuse is accurately scoped.

## 8. The lever the proposal leaves on the table

The project brief states the design principle explicitly: "workload LENGTH is the
free lever since attribution error is ~duration-independent." The proposal applies
this to *context* length and fixes decode at 512 tokens to match D-117.

That is the wrong lever. The KV effect scales with **decode steps × resident KV**.
Raising decode length multiplies the effect *and* the baseline, but it is far cheaper
in window time than raising context: 1.5B decode of 512 tokens is only ~5–10 s of a
~92.7 s member (most of a member is idle, warmup, teardown, cooldown). Going to 2048
decode tokens roughly quadruples the KV-read effect — 1.5B ~13 J → ~50 J — for
roughly +20 s/member (my estimate; ~+25 min across 40 members for 1.5B, ~+40 min for
7B, which is why it needs rehearsal). Against a floor that grows with magnitude this
does not buy a 4× ratio improvement, but it moves both endpoints out of the coin-flip
band, and it is the cheapest joules-per-minute available anywhere in this design.

This is the single largest missed opportunity in the proposal, and it is the
project's own stated doctrine.

---

## Scores

| Axis | Score | One-line justification |
|---|---:|---|
| Novelty | **3** | Finding already published (proposal cites Fernandez et al. ACL 2025); novelty is hardware + refusal discipline; registry says this should be a rider, not a row. |
| Feasibility | **3** | Effect is a 12–25% perturbation on a large baseline against apparently magnitude-proportional floors; interior points near-certain refusals; base windows carry no floor for their own condition family; untreated thermal confound. |
| MVP leverage | **5** | §§3–5 reuse is accurate and clean, but Contribution 1 is D-117's, and the 5-night total ignores Window C. |
| Venue fit | **5** | Honest ladder (capstone / EuroMLSys / HotCarbon / ICPE-ERT), correctly excludes ICPE-full without wall or second-unit; but modal outcome is a one-result-plus-three-refusals paper. |
| Original goals | **7** | Best in the pair. Directly serves the KV/attention axis and builds the unmodified full-KV baseline that quantized-KV (C5-2.11) and KDA work require. |

## Three strengthening moves

1. **Make each window self-flooring, and pay for it by deleting the interior points.**
   Replace the 10 absolute members at 1024/4096 (which the proposal already expects to
   be unresolved) with **5 A=A null blocks at 8192 context (20 members)**. New window:
   40 contrast + 20 null = 60 science members, inside the ~65–75 ceiling, ~3.6–3.9 h —
   rehearse before freezing. This gives the long-context family its own *comparative*
   floor, which is the binding component (7B historically 14.0 comparative vs 6.29
   absolute), and transports only the non-binding absolute component. It removes the
   entire transport dependency, deletes the contingency nights six and seven, and
   turns two unclaimable-by-default nights into two claim-bearing ones. Cost: you lose
   the "curve," which §3 says you were going to lose anyway.
2. **Add a thermal-matched control arm, or the causal claim is not defensible.** Run
   ABBA blocks of *128-context decode preceded by an out-of-window GPU preload*
   matched in duration and energy to the 8192 prefill, versus ordinary cold-start
   128-context decode. The preload sits *outside* the measured request, so the
   single-request boundary and the phase markers are untouched. If that hot-vs-cold
   128-context contrast is itself resolvable, the KV claim as framed is dead and you
   have found something more interesting (a measurable prefill→decode thermal
   carryover, which is a real metrology contribution and directly relevant to every
   phase-resolved energy paper). If it is below floor, the confound is bounded and
   Contribution 4 becomes defensible. Either way, pre-register die temperature /
   thermal pressure at decode onset as a recorded covariate, and pre-register mean
   decode power as the discriminator between "KV bytes cost energy" and "decode just
   ran longer."
3. **Fund the 1.5B window first, alone, and raise decode length.** Under
   magnitude-proportional floors the 1.5B arm has the better effect/floor ratio
   (~2.9× vs ~1.6×) despite the smaller absolute effect, because GQA gives it ~25%
   KV-to-weight traffic versus 7B's ~11.5%. Combine with move 2's lever: raise the
   decode target from 512 to 2048 tokens so the effect scales with decode steps. Then
   gate the 7B window on the 1.5B result. Before any of this, spend zero nights and
   do the desk arithmetic the proposal skipped: derive the expected Δ from the
   *freshly minted* D-117 decode floors and the traffic ratio, and check whether the
   fresh 7B comparative floor lands near the old ~14 J. If it does, the 7B arm should
   never be armed.

exec
/bin/zsh -lc 'for f in ../portfolio/rev-long-generation-dynamics.md ../portfolio/rev-mtp-energy.md; do echo "FILE $f"; sed -n '"'1,360p' \""'$f"; done' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
FILE ../portfolio/rev-long-generation-dynamics.md
# Counter-review — `prop-long-generation-dynamics.md`

**Reviewer:** Opus 5 counter-reviewer (independent). Ground truth: `desk` @ main.
**Proposal:** "Does Token 4,000 Cost More Than Token 400? Calibrated Decode-Energy Dynamics on Apple Silicon"

## Verdict: **WEAK**

Not because the physics is below the floor — the assigned worry is answered NO, the
effects are probably resolvable — but because the proposal picks the confounded
observational design when the repo already banks the interventional one, builds its
primary estimand on a floor construction that cannot exist, and misses the single
genuinely novel methodological point sitting in its own material. This needs a
redesign, not a tune-up. The redesigned sibling (below) would be VIABLE-to-STRONG.

| Axis | Score | One-line justification |
|---|---:|---|
| novelty | **4** | "Energy drifts within a request" restates the project's already-published never-zero drift allowance at finer granularity. The one novel idea in the material (interior-bounded estimands escape the attribution limit) is absent from the proposal. |
| feasibility | **6** | Exact-N generation and per-token timestamps genuinely exist. Per-*chunk* energy does not, and the extension lands on a D-117 desk stack (U1–U10) that is not yet built. |
| mvp_leverage | **3** | Reuses §§2–5 but costs 1–2 extra nights + a substantial schema/reducer/floor extension, and closes none of the MVP's open sections. |
| venue_fit | **5** | Capstone chapter, yes. ICPE only if the methodological point becomes the headline — as framed it is a descriptive table with a conceded confound. |
| original_goals | **6** | Really does serve the KV/attention axis (RQ-KV-GROWTH, C5-1.2, C5-2.12) and builds substrate for KDA / quantized-KV. Then explicitly declines the causal version the axis needs. |

---

## First, the assigned question: is anything here resolvable?

**Yes — marginally, and the proposal gets the reason wrong in both directions.**

**Sub-request resolution exists, partially.** Verified in the tree:

- Per-token timestamps are real: `joulewise/bundle_read.py:555` `token_timestamps()`,
  `_is_decode_token_event` (`bundle_read.py:1499`), provenance
  `runtime_per_token_callback` (`reduce.py:3062`, `axi_decode_config.py:520`), and a
  precheck that *refuses* to treat them as eligible on stream-chunk fallback
  (`reduce.py:3650`, `token_count_stream_chunk_fallback`).
- Exact-N EOS-masked generation is real: `adapters/mlx_runtime.py:206` `suppress_eos=True`,
  `:414` `output_policy == "fixed_budget_exact"`, with `eos_suppressed` and
  `original_eos_token_ids` recorded into metadata.
- **Per-chunk energy is NOT real.** `phase_energy_j` is keyed by phase *name*, and
  `bundle_read.py` states the contract explicitly: "Multiple valid intervals with the
  same phase name are integrated separately **and summed by the reducer**." Chunking
  therefore requires either distinct per-chunk phase identities or a new reducer path —
  plus new condition families, new bound corpora, new floor cells, pinset/extraction
  changes. The proposal calls this "decode-chunk schema and reducer support"; that is a
  fair label for a large piece of work stacked on U1–U10, which do not exist yet.

**Per-token is hopeless; per-chunk is fine.** The repo already did this arithmetic:
`docs/research_question_bank.md:51` — "token cadence (~4 ms) far outruns the power
sampler (~113 ms); no per-token joule claims." Confirmed independently:
`SAMPLING_INTERVAL_MS = 100` (`powermetrics_fiducial.py:63`), and the design memo's
timing probe gives 512-token generation at **2.05 s (1.5B)** and **6.40 s (7B)**
(`docs/phase_2/splitwise_decode_campaign.md` §4). So a 512-token chunk is ~18 samples
at 1.5B and ~57 at 7B. Chunked works; per-token is 25× below resolution.

**The magnitude.** The proposal's base numbers reconcile (51 J / 192 J per 512 tokens
matches the repo's measured 0.098 / 0.376 J/tok, `2026-07-30-sweep-mechanisms.md:66`).
Its *effect* sizing does not. Scaling the position effect proportionally to base energy
is the wrong model. The effect is extra KV traffic per token against weight traffic per
token. Using the repo's own `joulewise/kv_size.py` formula (2·L·H_kv·d·dtype):
Qwen2.5-1.5B ≈ **28.7 kB/token** (28 layers, 2 KV heads, d=128, fp16) against ~0.9–1.0 GB
of 4-bit weights; Qwen2.5-7B ≈ **57.3 kB/token** against ~4.2 GB. The *relative* effect
is roughly **2× larger for the 1.5B model**, not smaller. Back-solving ~90–100 pJ/byte
from the repo's own J/token figures, late-1024 minus early-1024 over a 4096-token
generation lands near **≈9 J (1.5B)** and **≈16 J (7B)** — flag: my estimate, ±50%,
depends on Qwen2.5 config values I did not read from disk.

Consequences: the effect is ~2–3× the ~5 J bar, not the 4–19× the proposal implies for
7B; and the arm the proposal offers to kill (1.5B) is the one with the strongest
*relative* signal. Its "kill that model's night if runtime-only sizing projects under
7.5 J" gate would likely kill the wrong arm.

---

## Fatal flaws

**F1 — The primary estimand has no comparative floor, and comparative is the binding term.**
The operative floor is `max(F_abs, F_cmp)` (draft §4), and comparative has historically
bound: mint #1 was absolute 3.592138 J vs comparative **7.377086 J**, operative 7.377086
(D-110). A comparative floor requires A/B/B/A blocks in which A and B are *aliases of the
exact same configuration* (draft §4: "A and B are aliases of the exact same configuration
and payload, so any nonzero block delta is a false comparative effect"). "Early chunk" and
"late chunk" are **positions, not swappable labels** — no alias null can be constructed for
them. The proposal's "the alias blocks supply comparative false-effect evidence" yields a
floor for the *member-level* metric; transporting it to a *within-member* chunk difference
is exactly the transport violation the D-117 design memo forbids ("never borrow a decode
floor for prefill"; "the 128-prompt prefill riders do not automatically transport"). The
same rule binds here. Contribution 2 has no gate it can pass.

**F2 — The estimand is not counterbalanceable, and the confound is never zero by the
project's own measurement.** ABBA cancels a linear time trend *between* members
(draft §5). Within a member, token position and elapsed time are the same variable and
cannot be reordered — no design fixes this. Draft §4: the drift allowance "remains
positive even in an exceptionally stable window." So late-minus-early ≡ KV growth + DVFS +
thermal + within-run drift, inseparably. The proposal is honest about this ("position-
associated drift, not KV growth causes energy") — but that honesty collapses Contribution 2
into *re-measuring the known drift limitation on a finer timescale*. That is a
re-parameterization, not a result.

**F3 — Duplicative of banked work whose discipline it doesn't cite, and it picks the weaker
of two designs that cost the same nights.** `docs/research_question_registry.md:48` banks
**RQ-KV-GROWTH** at "L1/L2 chunked", "no per-token joule claims", with the rider "bounded-
window KV marginal slope". **C5-2.12** (`research_question_bank.md:977`) already specifies
the *interventional* version: bounded evicting `RotatingKVCache` via `max_kv_size` vs
unbounded step-growing `KVCache` — available in the pinned mlx-lm, ABBA-counterbalanceable
at matched positions, with a real alias null and a real comparative floor. The proposal
defers this ("a causal KV-mechanism claim would still require a later bounded-versus-
unbounded cache intervention") while spending the same nights on the confounded version.
That is a design error, not a scoping choice.

## Should-fix

**S4 — The attribution model is inherited uncritically, and in the *pessimistic* direction —
which is why the best idea got missed.** Draft §4 derives ~1 J from "a roughly 30 ms timing
uncertainty meets a power change of roughly **33 W**" — that 33 W is the *prefill→decode
power step*. A decode-to-decode chunk boundary sits inside a homogeneous power regime where
the step is ≈0 W, so the existing corner scan would honestly return a near-zero interval
there. Two consequences: (i) the proposal's own floors are **not** attribution-dominated,
so the "attribution-limited" framing it leans on doesn't apply to its estimand; (ii) if you
drop the phase-adjacent chunks (compare chunk 2 vs chunk 7, both bounded by interior edges)
the estimand becomes the project's **first noise-limited (~0.3 J) rather than attribution-
limited quantity**. That is the most publishable thing available in this direction, and it
is nowhere in the proposal. As written, chunk 1's leading edge is the prefill boundary and
chunk 8's trailing edge is the decode-end step, so the proposal gratuitously imports ~2 J of
worst-case attribution into a ~9 J effect.

**S5 — Budget bookkeeping is understated (though the headline hours survive).** Per the
design memo the member is overwhelmingly fixed overhead (1.5B member 92.7 s of which only
2.05 s is generation; 7B ~97 s / 6.40 s). 4096 tokens adds ~14 s (1.5B) / ~45 s (7B) per
member, so ~2.6 h / ~3.4 h is about right *for a 40-member design* — but only because the
proposal silently leaves the 12-member NEG-8 bound corpus and the 3/1/3 references at the
**short** workload. Draft §4 defines a condition family by "workload profile", so a
512-token bound corpus cannot bound a 4096-token cell. Moving them adds ~10–14 min and puts
the 7B window at ~3.5 h with no headroom against the 4 h cap. Also unbudgeted: cooldown
cap-hits (historically one 305 s cap-hit against a 117 s recovery) under 40 × 51 s sustained
GPU bursts.

**S6 — 4096 tokens is 2× beyond the untested range.** Draft §6 ramps linearity 128→2048 and
every one of the six characterization rows is `[PENDING WINDOW C]`. The proposal asserts the
extrapolation and simultaneously makes the untested range its estimand.

**S7 — No minimum-samples-per-chunk rule.** The 8-chunk secondary trajectory at 1.5B is ~18
samples/chunk. The bank's own convention ("bundles with fewer than N samples report a flag,
not a bare joule value") applies and is never stated.

**S8 — The ABBA structure is decorative for the primary estimand.** All 40 members are the
same config; the position contrast is computed *within* each member. ABBA buys nothing for
the headline number — it only supports the member-level null. Say so, or drop the framing.

## Three strengthening moves

1. **Make it an intervention, not an observation.** Run C5-2.12's bounded (`max_kv_size`)
   vs unbounded `KVCache` contrast at matched token positions in real ABBA blocks. This
   converts an uncounterbalanceable within-request difference into the project's standard
   A/B estimand with a legitimate alias null and a legitimate comparative floor, and it
   answers "does KV growth cost energy" *causally*. Price: eviction changes generations, so
   pre-register a **work-matched, never output-matched** contrast per C5-2.12's own
   forbidden-upgrade wording and report divergence. Output-identity-preserving sibling:
   hold the measured chunk at a fixed position in the request and vary the *starting* KV
   size via prompt length (128 vs ~3200 prefill, then measure the first 512 decode tokens) —
   the repo's KV replay spike already demonstrates prefix-cache save/load with
   `tokens_identical: true` (`docs/stream_logs/2026-07-07-kv-spike-301/`).
2. **Make the interior-boundary result the headline.** Pre-register that chunk floors are
   minted for *interior-bounded chunks only* (drop chunks 1 and 8), demonstrate via the
   existing corner scan that their attribution intervals collapse, and publish: *the
   attribution limit is a phase-boundary property, not a global property of the instrument —
   interior-bounded estimands are repeatability-limited at ~0.3 J.* That extends the MVP's
   central finding instead of merely reusing it, and it costs desk work rather than nights.
3. **Fix the sizing before asking for a night.** Replace proportional-to-base sizing with a
   bandwidth model built from `kv_size.bytes_per_token` and the measured 0.098 / 0.376 J/tok;
   publish the implied pJ/byte; set the kill gate on the *interior-bounded* (chunk 2 vs 7)
   estimand, whose effect I estimate at ~6 J (1.5B) / ~11 J (7B), not the full-span one.
   Then declare the minimum-samples-per-chunk rule, re-spec the NEG-8 bound corpus and the
   3/1/3 references at the long workload, and re-run the 4 h envelope with those members in.

## Sequencing note

The proposal correctly refuses to disturb the three D-117 windows. But it adds 1–2 nights
plus a large desk extension (chunk reducer, new condition families, pinset/extraction
changes) on top of a U1–U10 stack that is not built, while closing neither §6 nor §7 of the
MVP. Under the paper-first stack this is not an MVP candidate. Post-redesign it is a
reasonable ICPE-version chapter.
FILE ../portfolio/rev-mtp-energy.md
# Counter-review — `prop-mtp-energy.md`
**"Does Multi-Token Prediction Save Joules? A Detection-Floor-Gated Study on Apple Silicon"**
Reviewer: Opus 5 (counter-reviewer, adversarial charge). Ground truth: `desk` @ `89b929c`.

## VERDICT: **WEAK**

More precisely: **KILL as a standalone funded direction; survives only as a ~zero-cost desk rider
on the speculative-decoding proposal.** It is not a dishonest proposal — it self-gates behind a
feasibility check and explicitly refuses to displace D-117, which is more discipline than most of
this portfolio will show. But it was given an instruction it did not follow: *"If your assigned
direction cannot honestly be built from existing material, SAY SO PLAINLY and shrink it to the
version that can."* It said so. It did not shrink. It kept the full three-window ambition behind a
gate whose prior of returning "no" is high, and it never noticed that its own evidence base
contains a strictly better version of the same paper.

## Scores

| Axis | Score | One-line |
|---|---:|---|
| Novelty | **5/10** | Real gap (on-device MTP energy is unexamined), but 2 of 4 contributions restate already-frozen repo contracts. |
| Feasibility | **2/10** | The runtime does not exist in supported form; the named artifact is wrong; the fix is "fork and self-instrument mlx-lm." |
| MVP leverage | **4/10** | Reuses method prose, cannot reuse a single number — and the floor machinery does no work at this effect size. |
| Venue fit | **5/10** | ICPE-credible *if* it lands; conditional on a gate it probably fails. |
| Original goals | **8/10** | MTP is a named original mechanism goal and this squarely serves it. Best axis by far. |

---

## (a) Does an MTP-capable model + runtime exist on the MLX stack today? — **No, and the proposal names the wrong artifact.**

This is the fatal axis, and the repo answers it unambiguously.

`docs/specs/axi/sc_spec_decode_verdict.md` closed native MTP as
`unsupported_for_joulewise(native_mtp_generation)` on 2026-07-17 with lead-run Metal evidence
(SHA-256 `f7ab8800…`). The mechanism is exact and cited to source: `mlx_lm/models/qwen3_5.py:307-314`
**detects MTP weights and then deletes every key containing `mtp.`**. The package exports no native-MTP
entry point; `stream_generate`'s only accelerated branch is an external `draft_model`.

Three specific failures follow.

**1. The proposal names a model that is neither on disk nor established to exist.** It nominates
"Qwen3.5-27B" as a "plausible candidate but uncertain and not frozen." The repo's actual on-disk
MTP-candidate artifact is **`mlx-community/Qwen3.5-122B-A10B-4bit`, ~65 GiB, vocab 248,320, config
advertising one MTP hidden layer** (same verdict doc, "Historical pre-live artifact snapshot").
A proposal that has read AXI-SC — and it cites AXI-SC — should be able to name the artifact AXI-SC
already probed. Getting this wrong is not cosmetic: 27B-dense and 122B-A10B-MoE differ in every
budget-bearing dimension in the plan.

**2. The reopening gate is violated by the proposed remedy.** AXI-SC's revisit condition is explicit:
*"Revisit native MTP only when a **newly pinned runtime** retains MTP weights, executes an identifiable
native path, **and supplies** the same AXI-SA counters and step boundaries."* The proposal offers an
unmerged community fork (upstream issue open, by its own admission) and then proposes to **add the
counters itself** ("add runtime-observed head provenance and per-round counters"). That is the
measurer writing the measurement into the artifact under test. The AXI-SC controller's entire design
premise is independence — *"The controller suppresses the child's verdict and re-derives the result"*;
*"Proposal/acceptance observability must be real runtime evidence and is never inferred."* Self-supplied
counters may still be admissible, but that is a **custody and contract question requiring a cold-gate
ruling and a successor verdict**, not an engineering line-item. The proposal budgets it as the latter.

**3. Undisclosed dependencies that are themselves open research.** Nowhere does the plan account for:
(i) whether **MTP heads survive 4-bit quantization** with usable acceptance — nobody has shown this, and
a 4-bit MTP head with 40% acceptance produces a different paper; (ii) that a **65 GiB MoE** is a new
model family, new architecture, new tokenizer, and — critically — a **new power envelope**. The
attribution-limited finding (~1 J per phase member) is derived from ~30 ms edge uncertainty × **~33 W
swings**, and the ~5 J practical bar descends from it. Move to a 122B MoE whose decode is dominated by
expert-weight streaming and that 33 W figure, the ~1 J bound, and the 5 J bar all require
re-characterization before a single floor can be minted. **The proposal treats the instrument's
acceptance basis as portable across a 16× change in resident working set. It is not.** This is the
single largest omission in the document.

Net: this is not "one desk gate." It is *new artifact acquisition + quantization validation + a runtime
fork + self-instrumentation + a new stack-identity contract + re-characterization of the attribution
bound + new pinsets/extraction specs + a pilot window*. That is a runtime-and-instrument program, which
is precisely what the hard constraint forbids.

## (b) Is "per accepted token" well-posed? — **Yes, and the proposal handles it correctly — but it is not a contribution.**

Contribution 3 is right on the merits: gross request energy primary, J/committed-output-token as
companion, J/accepted-MTP-token as a spec-on diagnostic only because it is undefined for MTP-off.
It is also **already ratified doctrine**, verbatim, in two places:

- `docs/contracts/token_normalization.md:50-56` — "Committed output tokens and accepted draft/MTP
  tokens are distinct denominators… gross joules per accepted draft token is a speculation-enabled
  [diagnostic]… D-037 claims-ladder rider."
- `docs/research_question_bank.md` C5-2.5c — "accepted-draft J/token stays a mechanism diagnostic,
  never the on/off efficiency denominator (token_normalization.md D-037 rider)."

Contribution 4 (`emitted = accepted + target-origin`, observed not configured) is likewise a restatement
of the frozen AXI-SA contract (`tokens_proposed` / `tokens_accepted` / `acceptance_rate` +
one request-scoped `decode_emission` per step). **Two of four falsifiable contributions are compliance,
not findings.** Halve the novelty score accordingly.

One thing the proposal *misses* on this axis: the 122B artifact's tokenizer (vocab 248,320) is not the
Qwen2.5 tokenizer (151,936). Under the token-normalization contract every per-token number here is
tokenizer-scoped to a stack that shares nothing with the MVP. Within-arm off/on comparison is clean;
**cross-reference to any MVP or D-117 number is forbidden**. The study is hermetically sealed from the
paper it claims to extend. The proposal says "do not transport the Qwen2.5 floors" but does not follow
that through to "therefore this chapter shares no numbers with the rest of the paper."

## (c) Effect sizes vs the ~5 J bar and the two gates — **the strongest section, but it contains a hard error and a self-defeating implication.**

Effect size is genuinely **not** the risk. At 1024-token decode on a model ≥ the 7B anchor, gross decode
energy is hundreds to thousands of joules and a 20–40% mechanism effect is 10–50× any floor. Correct
conclusion, sloppy arithmetic (the 192 J anchor is a **7B, 128-prompt/512-output** member mean from
`window_7bfloor_20260729`, D-110 RT-5-untainted; applying a fork's speedup ratio measured on other
hardware to a different model at 2× the decode length is theater, even for sizing).

**Hard error — the kill threshold is set below the instrument's own comparative floor.** The proposal
kills on *"a bench pilot projects |ΔE| < 10 J."* The measured 7B **comparative** floor from that same
window is **13.998036715259254 J** (absolute 6.294380135190098 J). A 10 J threshold would greenlight a
three-night campaign that structurally cannot clear gate 1. Referee-fatal as written; trivially fixable.

**Undisclosed design problem — duration asymmetry.** MTP-on and MTP-off differ in wall time **by the
effect itself** (~30–40%). Every existing floor design has near-equal arms: D-117's gamma arms are
90.5 s (1.5B ref) vs ~97 s (7B) — ~7% — and the comparative floors are built from *identical-label*
ABBA null blocks where drift loads both halves equally. A 30–40% asymmetric contrast means the two arms
sample different amounts of the **measured never-zero drift** trajectory and different thermal states.
Attribution error is duration-independent; drift is not. **The proposal's contrast imports an asymmetry
the floor machinery has never had to handle and does not say how the drift allowance is apportioned.**

**Self-defeating implication.** If the effect is 10–50× the floor, JouleWise's *entire published
contribution* — attribution-aware detection floors — does no work in this study. An ICPE referee will
ask why the apparatus is needed to see a 60 J effect. The MVP's method sections become ceremonial
reuse. The proposal's defence ("a refusal is still a result") only holds if refusal is plausible,
and its own sizing says it is not.

**Budget is asserted, not derived.** The D-117 memo derives windows from anchor member times
(7B decode member ≈ 97 s) → alpha 3.14 h, beta 3.24 h, gamma 2.80 h against a 2–4 h envelope, beta
already near the ceiling. The proposal doubles decode length (512 → 1024) and multiplies the resident
working set ~16× (≈4 GiB → 65 GiB), then asserts "2.8–4 h windows" **with no anchor member time in
existence**. Its own kill criterion ("cannot fit within four hours including 20% margin") is likely
triggered by its own design. The budget and the design contradict each other.

## (d) Novelty — **thin, and dominated within the portfolio.**

On-device native-MTP energy is genuinely unmeasured — credit where due. But MTP is *self-speculative
decoding*, a special case of a question the repo has already scoped, and `docs/run_reports/2026-07-30-sweep-mechanisms.md`
— which this proposal **does not cite** — already adjudicated it:

> `| — | MTP | — | — | **unreachable** (no runtime) |`
> `| MTP | MiMo-7B-Base (heads in checkpoint) | — | — | **Not reachable**: no MLX MTP support (vLLM only) |`

…while ranking **spec decode on/off (7B + 0.5B) at 6–16× floor clearance** as recommended first
campaign #1: *"cleanest single-mechanism ABBA in existence (identical target weights, flag-toggled),
verified runtime, open sign question."* The proposal's Contribution 1 — a floor-gated on/off energy
verdict at matched output — is **achievable today** for external-draft spec decode and **not at all**
for MTP. Same science, same estimand, on models already floor-characterized. That is domination, and
the proposal reached past it for an external arXiv cite (`2602.09113`, unverifiable here, absent from
the repo's own source list) to make a point the repo already banked with a native citation
(mlx-lm #250: the spec-decode step may be *slower*).

Citation hygiene: `1.41–1.52×` and `~80% acceptance` are load-bearing for a three-night spend and are
**un-custodied third-party claims from an open issue on other hardware**. Under this project's own
evidence discipline they should be labelled as such in the proposal body, not cited as sizing input.

## (e) True cost — **understated by a factor of several.**

Stated: 2–3 weeks desk + 3 windows (8.5–12 h). Realistic floor, assuming everything works:
artifact acquisition/conversion + 4-bit MTP-head validation; fork adoption; runtime instrumentation to
AXI-SA shape; 100-prompt exact-output validation; **cold-gate ruling on measurer-authored counters**;
new stack-identity contract; **re-characterization of the attribution bound and the 5 J bar at the new
power envelope** (itself a measurement campaign, uncounted); pinset v2 analogues; extraction specs;
an uncounted pilot night; then 3 windows that its own parameters suggest exceed the 4 h envelope.
Call it 4–8 weeks desk and 4–5 nights, with a high probability of terminating at "no" somewhere in the
first third. Under Ed's stated priority stack (P1 MVP paper, P2 ICPE, **P3 sacrificed if it costs
P1/P2**), this is textbook P3 spend on the critical path.

## (f) Original-goals service — **genuine, and the proposal's best claim.**

MTP is a named original mechanism axis, and this is a faithful, well-shaped attempt at it: energy as a
third axis beside output-equivalence and latency, single-request boundary preserved, modular harness
exercised. If Ed's question is *"does anything in the portfolio serve the original MTP goal?"*, the
honest answer is: **only via a dated negative result**, and AXI-SC already produced that. A
well-written "this mechanism is currently unreachable on this stack, here is the source-level
evidence" section is real, publishable, advisor-legible material — it just is not a paper.

---

## Fatal flaws (ranked)

1. **No supported runtime, and the remedy is a runtime project.** AXI-SC's reopening gate requires a
   *newly pinned runtime* that *supplies* the counters. The proposal offers an unmerged fork plus
   self-written counters — violating the gate and the existing-material constraint simultaneously.
2. **The instrument's acceptance basis is treated as portable and is not.** The ~1 J attribution bound
   and the ~5 J bar derive from ~33 W swings on the current stack; a 65 GiB MoE requires them re-derived
   before any floor mints. Not mentioned, not budgeted.
3. **Wrong artifact named.** "Qwen3.5-27B" (speculative) instead of the repo's probed
   `Qwen3.5-122B-A10B-4bit` — and every budget/scale/tokenizer consequence flows from that error.
4. **Kill threshold (10 J) sits below the measured 7B comparative floor (13.998 J).**
5. **Strictly dominated by external-draft spec decode**, which the repo's own 07-30 sweep ranks #1 and
   which is reachable on the current pin with already-characterized models. Not cited, not considered.
6. **Budget asserted without an anchor member time**, in contradiction with its own 4 h kill criterion.
7. **Unaddressed drift asymmetry** between arms whose durations differ by the effect under test.

## Three strengthening moves (if kept)

1. **Re-target to external-draft speculative decoding on Qwen2.5-7B + 0.5B; demote MTP to one dated
   paragraph.** AXI-SC established that this exact pair **executes live** (evidence SHA
   `559731f4…`), with distinct loaded paths, matching terminal token IDs, and **directly observed
   accepted tokens via `GenerationResponse.from_draft`**. The `event_observability` verdict blocks only
   `tokens_proposed`, aggregate acceptance rate, and per-step emission bursts — i.e. the *mechanism-yield*
   claims. It does **not** block the paper's actual estimand: gross request energy and
   J/committed-output-token, on/off, at matched output (greedy speculation is output-identical by
   construction — a *stronger* version of Contribution 2 than MTP can offer). Result: zero runtime
   engineering, target model already floor-characterized, floors already minted, tokenizer identical
   to the MVP so numbers *do* cross-reference, and the missing proposal counters become an honest
   declared limitation — which is itself on-brand for this project. Keep MTP as the dated
   unreachable-mechanism section; that costs one rerun of `scripts/axi_sc_spec_decode_spike.py`.
2. **Fix the sizing block and add the asymmetry analysis.** Replace the 10 J kill threshold with the
   measured comparative floor (13.998 J) plus stated margin. Re-derive effect estimates from the repo's
   own anchors (7B 0.376 J/tok, 1.5B 0.098 J/tok) at the actual pre-registered decode length rather
   than from a 512-token member mean on a different model. Add a pre-registered rule for apportioning
   the never-zero drift allowance when contrast arms differ in wall time by the effect itself — and
   state plainly that at 10–50× floor clearance the floor machinery is *method provenance*, not the
   detection mechanism, so the paper's claim to extend the MVP rests on protocol reuse rather than
   floor-limited inference.
3. **If MTP is kept at all, make the desk gate terminate in a written AXI-SC successor verdict, not a
   paper.** Name `Qwen3.5-122B-A10B-4bit` explicitly; add the three missing gate items the proposal
   omits — (a) do the MTP heads survive 4-bit conversion with usable acceptance at all, (b) a
   re-characterization of the attribution bound and the sizing bar at the 65 GiB MoE power envelope
   *before* any floor plan is frozen, (c) a cold-gate ruling on whether measurer-authored counters
   inside the runtime under test satisfy AXI-SA's "real runtime evidence, never inferred" rule. Any
   one of the three returning "no" closes the axis at desk cost, which is the only defensible way to
   spend anything here.

exec
/bin/zsh -lc "sed -n '1,440p' ../portfolio/rev-moe-routing-energy.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review — `prop-moe-routing-energy.md`

**Reviewer:** Opus 5, adversarial counter-review. Ground truth: desk checkout at `89f28bf`
(main), D-117 + design memo, `CLAIMS_STATUS.md`, `docs/research_question_registry.md`,
`docs/run_reports/2026-07-30-sweep-mechanisms.md`,
`docs/run_reports/2026-07-07-flagship-qwen35-122b.md`,
`docs/run_reports/2026-07-29-modularity-survey.md`, and **direct inspection of the installed
runtime** at `/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/` plus the
local artifact config at `/Users/edr/jw_models/mlx-community/Qwen3.5-122B-A10B-4bit/`.

**VERDICT: VIABLE** (with two blockers that must be closed before any night is committed)

| axis | score |
|---|---|
| novelty | 6 / 10 |
| feasibility | 4 / 10 |
| mvp_leverage | 5 / 10 |
| venue_fit | 6 / 10 |
| original_goals | 8 / 10 |

This is the better of the two proposals I was assigned, and it survives a serious attempt to
kill it. It does not survive intact.

---

## The existing-material question, answered from the runtime source

The charge asked whether a Qwen MoE variant exists on MLX at a servable size with per-token
expert-activation observability. I checked the installed code rather than the model card.

**Artifact: EXISTS, pinned, already exercised.** `Qwen3.5-122B-A10B-4bit` is present at
`/Users/edr/jw_models/mlx-community/`, and `docs/run_reports/2026-07-07-flagship-qwen35-122b.md`
records 3/3 reps `validate-bundle --strict` green, rev `e9c67b0`, 65 GB on disk, 68.9 GB peak,
46 tok/s decode, 12.8 s warm load, gross CV **0.3 %** across reps (the tightest in the corpus).
The ~304 J / 512-token diagnostic the proposal cites is real (303.5 / 303.5 / 305.1 J) and is
correctly labelled as planning-only. The claim is not invented.

**Architecture: the proposal's numbers are exactly right.** From the local `config.json`
(`text_config`): `num_hidden_layers=48`, `num_experts=256`, `num_experts_per_tok=8`,
`hidden_size=3072`, `moe_intermediate_size=1024`, `shared_expert_intermediate_size=1024`,
`decoder_sparse_step=1`. So all 48 layers are MoE, giving 48 × 8 = **384** routed
expert-layer activations and 48 shared activations per token — as stated. Per routed expert:
3 × 3072 × 1024 = 9.44 M params; × 8 × 48 = **3.624 B** routed-active. Halving k removes
**1.812 B**. The proposal's "about 1.81B, roughly 18 % of the advertised 10B active" is
arithmetically exact. Credit.

**Runtime: the knob is real and the observability gap is real.** `qwen3_5_moe.py` subclasses
`qwen3_5.py`, which imports `Qwen3NextSparseMoeBlock as SparseMoeBlock` from `qwen3_next.py`
— so the proposal's citation of `qwen3_next.py` is **correct**, not the mismatch it looks
like. I had that queued as a hit and withdrew it. The block reads:

```python
gates = mx.softmax(self.gate(x), axis=-1, precise=True)
k = self.top_k                                    # = args.num_experts_per_tok
inds = mx.argpartition(gates, kth=-k, axis=-1)[..., -k:]
scores = mx.take_along_axis(gates, inds, axis=-1)
if self.norm_topk_prob:
    scores = scores / scores.sum(axis=-1, keepdims=True)
y = self.switch_mlp(x, inds)
```

Three consequences, two favourable:

1. **`routing_top_k_override` is a one-line config change** (`num_experts_per_tok`). No source
   patch needed for the *intervention*. Feasible as claimed.
2. **`norm_topk_prob` defaults to `True`** (`qwen3_5.py:51`, and the artifact does not
   override it). So forcing k=4 **renormalizes the gate mass** and preserves output scale.
   This is important and the proposal does not know it: the obvious "k=4 produces scaled-down
   garbage" failure mode is structurally excluded. The quality risk is real but it is
   distribution shift, not numerical collapse.
3. **`inds` is a live intermediate, never returned.** Per-token expert IDs require a source
   patch to `Qwen3NextSparseMoeBlock`. The proposal's "current MLX code calculates those
   indices internally but does not expose them as evidence" is exactly right.

So the existing-material constraint is **satisfied** — better than for most of this portfolio.
The problems are elsewhere.

---

## BLOCKER 1 — The contrast has no floor for arm B

The proposal budgets "one exact-stack floor window" using "the proven 10-absolute plus 40
A=A null design". That produces **one** floor cell, for the native k=8 configuration.

But the k=4 arm is a *different config hash* → a different condition family → a different
stack identity under this repo's own rules. D-117 gamma's floor rule is
`cross_stack_armwise_max.v1`: "independently resolve the 1.5B and 7B decode cells and take
their maximum, never their sum." Both arms need independently resolved floors. The design
memo is emphatic about the general principle — *"never borrow a decode floor for prefill"*,
and prefill riders "do not automatically transport" to a differently-parameterised workload
without "either exact matching prefill floor cells or a separately predeclared and justified
transport rule."

A k=8 floor is precisely a borrowed floor for the k=4 arm. As designed, the contrast cannot
be governed. The fix is cheap if made now and expensive if discovered at the arm gate: split
the null half into 20 members at k=8 and 20 at k=4 (or run 10-absolute + 20 + 20 in one
window), or pre-register an explicit transport ruling with justification. Either way the
proposal's window count and member schedule change, and its "5 nights, 14–16 h" figure is
understated.

## BLOCKER 2 — The effect/floor ratio is asserted against the wrong denominator, and the kill gate is set below the largest measured floor

> "use **40–120 J/request** as the uncertain planning range. Even its low end is about 8× the
> 5 J bar."
>
> Kill if "a pessimistic desk timing proxy … projects under **15 J**".

Two problems.

**(a) The "5 J bar" is a document-level prose constant; the measured floors are 2–3× larger.**
`CLAIMS_STATUS.md` line 55 gives "floor + claim-side bound ≈ 5 J", but eight lines below it
records the only actually-minted comparative floor: **13.998036715259254 J** for the 7B decode
cell, on an absolute-cell member mean of **192.386233 J** — i.e. the comparative floor is
**7.3 % of member energy**, and the absolute component (6.294380 J) is 3.3 %. On this
instrument, floors have empirically scaled with member energy, not sat at an absolute ~1 J.
(The ~1 J attribution limit is one *component*; at 7B it is not the binding one.)

A 122B member at 1024 output tokens is **~597 J** (583 mJ/output-token measured × 1024 —
note this, not "roughly 110 J at 1,024 tokens", is the request energy; see the prose defect
below). Scaling the one measured precedent forward, a projected comparative floor of
**~44 J** is the honest central estimate, with a plausible range of ~25–90 J.

Against that, the proposal's own 110 J central effect is **~2.5×** the floor, not 8×; its
40 J low end is **below** it. The proposal is not obviously wrong — the flagship report's
0.3 % gross CV suggests this stack may be unusually repeatable, and an attribution-dominated
floor of ~5–10 J is genuinely possible — but it asserts the optimistic branch without
engaging the one measured precedent that contradicts it. The honest statement is:
*effect/floor is somewhere between ~1.2× and ~20× and the floor window is the experiment that
decides it.*

**(b) The 15 J desk kill gate is below the largest already-measured floor (13.998 J).** A gate
set at 1.07× the biggest floor this project has ever minted cannot fail for any reason that
matters. It must be expressed as a multiple of the *projected floor for this cell* — I would
demand ≥3× — not as a fixed joule literal inherited from a different model's regime.

**(c) The physics may cut against the proposal.** Decode here is bandwidth-bound. Per-token
weight traffic ≈ routed 3.62 B + shared 0.45 B + LM head 0.76 B (`tie_word_embeddings: false`,
vocab **248320** × 3072) + attention ≈ 6.3 B params at ~4.25 effective bits (group_size 64,
affine) ≈ **3.35 GB/token**. At the measured 46 tok/s that is **~154 GB/s** — roughly 40 % of
the M3 Max's ~400 GB/s, whereas dense Qwen2.5-7B (0.376 J/tok at ~28–36 W → ~93 tok/s ×
4.2 GB) runs at **~390 GB/s**, essentially at peak.

That gap is the real story: **batch-1 MoE on unified memory achieves ~40 % of the bandwidth
efficiency of dense inference**, because gathering 8 of 256 experts per layer is
dispatch-bound, not traffic-bound. Which means the k=8→k=4 saving will be **sublinear** in
removed parameters: the gather/dispatch cost per layer is roughly fixed, so halving k halves
the bytes but not the overhead. The proposal's proportional 18 % assumption is an upper
bound on the mechanism it is measuring. (Conversely, counting only per-token *read* traffic
rather than the advertised 10 B active gives 1.81/6.3 = 29 %, an upper-upper bound. The
truth is bracketed by dispatch overhead and nobody knows where.) This is simultaneously the
proposal's biggest risk and its most interesting potential finding — and it is unstated.

---

## FLAW 3 — The confound between expert budget and sequence content is treated as a quality question when it is an estimand question

The proposal correctly rejects cross-model MoE comparisons as confounded and correctly picks
a same-checkpoint intervention. But it then declares:

> "Native k=8 and forced k=4 differ **only** in routed-expert budget on one
> artifact/runtime/boundary."

That is false past token 1. Forcing k=4 changes the logits, which changes the greedy argmax,
which changes the emitted token, which changes the next hidden state, which changes **which
experts route** and **what the KV cache contains**. By token ~50 the two arms are generating
different text. With `max_tokens` pinned at exactly 1024 the *count* matches, but the two arms
are no longer "the same work minus four experts" — they are **1024 tokens of text X versus
1024 tokens of text Y**, and if arm B degenerates into a repetition loop (a classic
reduced-top-k failure) then Y has systematically different routing entropy, expert-reuse
locality, and cache behaviour. Repetition loops concentrate routing on few experts, which
*improves* gather locality and would **inflate** the measured energy saving beyond the
mechanism.

The repo already owns this gate: `C-023-OUTPUT-IDENTITY` — *"Fixed output-token count is not
fixed decoded work"* — is a registry row, and it is `status: candidate (C-023)` with
`AP owner: none-yet`. The machinery is **not built**. The proposal's response (an
"exact-output divergence report", and a quality gate that "kills 'quality-equivalent' wording
but may retain a trade-off paper") mis-frames it: divergence is not a caveat on the *wording*,
it is a bias on the *estimand*. The minimum honest addition is a **routing-locality
companion** — unique experts touched per layer, expert-reuse rate, and routing entropy per
arm — so that a divergence-driven locality shift can be distinguished from the budget effect
it is being credited to. The proposal already plans "expert-load/unique-expert summaries";
it just does not connect them to this confound.

The teacher-forced variant (replay arm A's exact token IDs through arm B's k=4 routing) would
eliminate the confound entirely at the cost of measuring a counterfactual rather than a
deployment. Worth at least a paragraph of adjudication; the proposal gives none.

---

## FLAW 4 — Instrumentation overhead is the most likely killer, and MLX's execution model makes it worse than budgeted

The proposal's ≤2 % decode-time overhead gate is right in spirit but underestimates the
mechanism. MLX is lazy and asynchronous. Exporting `inds` per layer per token requires
keeping 48 live arrays alive across the decode step, which prevents buffer donation and
kernel fusion around the MoE block, and any host readback forces a graph sync **48 × 1024
times per member**. The proposal's mitigation ("buffered routing evidence must be flushed
outside the measured decode interval") is the correct instinct and probably necessary, but
on-device buffering still materialises 48 × 1024 × 8 index arrays per member and still adds a
graph node per layer.

This is a desk-testable question and the proposal treats it as one — good. But note what a
failure means: an instrumentation-on run is a **different stack identity** from an
instrumentation-off run, so a patched `mlx_lm` cannot silently inherit D-117's runtime
identity. The instrumentation-on/off ABBA equivalence test the proposal names is exactly
`C-023-TELEMETRY-PERTURBATION` from the registry (`status: candidate (C-023)`, `AP owner:
none-yet`) — another unbuilt dependency it inherits without acknowledging.

## FLAW 5 — Undeclared properties of the chosen artifact

The proposal describes the target as "the already exercised, pinned `Qwen3.5-122B-A10B-4bit`
MLX artifact" and cites the *text* model card. The local artifact is not quite that:

- **It is a vision-language checkpoint.** Root config carries `vision_config`,
  `image_token_id: 248056`, `video_token_id`, `vision_start/end_token_id`, and
  `qwen3_5_moe.py`'s `sanitize()` explicitly **discards** every `vision_tower` / `model.visual`
  weight at load. So part of the 65 GB on disk is read and thrown away, which is why peak
  memory hit 68.9 GB. Model identity, artifact SHA, and the discarded-weight behaviour all
  need to be in the stack-identity table; citing the text model card's parameter counts for a
  VLM artifact is an identity mismatch a referee will catch.
- **It is a hybrid, not a transformer.** `full_attention_interval: 4` and
  `from .gated_delta import gated_delta_update` — 36 of 48 layers are GatedDeltaNet linear
  attention, 12 are full attention. The paper would place a hybrid-linear-attention MoE
  alongside D-117's dense Qwen2.5 transformers without saying so.
- **It is a reasoning model with a different tokenizer.** `vocab_size` **248320** vs Qwen2.5's
  151936/152064. Within the two MoE arms this is fine (same tokenizer, so the mJ/output-token
  companion is well-scoped). But the paper juxtaposes MoE results with D-117's Qwen2.5
  results, and `docs/contracts/token_normalization.md` forbids cross-tokenizer/cross-family
  per-token comparison without a J/char or J/byte companion or purely descriptive language.
  Unaddressed.
- **The quality screen the proposal promises has no harness support.**
  `docs/run_reports/2026-07-29-modularity-survey.md` records that model family is "MODULAR by
  omission" — qwen3.5-122b ran the identical path — but also that **"no chat-template/
  thinking-mode/multimodal seam exists at all … a chat/thinking model needs a new
  prompt-rendering seam."** Contribution 4 (a "frozen quality screen" with an overall pass
  rate and per-stratum breakdown) requires chat templating and task scoring on a *reasoning*
  model, and neither exists. This is a substantially larger build than the routing sidecar and
  the proposal budgets it as an afterthought.

---

## Novelty, honestly

The proposal oversells its position relative to the repo's own prior art.

`docs/run_reports/2026-07-30-sweep-mechanisms.md` already contains this idea, ranked and
costed. Its pairs table lists **"MoE top-k knob | Qwen3-30B-A3B, `num_experts_per_tok=8` |
same checkpoint, k=4 (config edit) | same weights | *Unverified but mechanically plausible* —
single-mechanism, same-weights knob"**, and its claims ranking puts "MoE top-k slope (same
weights)" at **rank 6 of 6** with "expert-FFN energy ~∝ k; maybe 20–40 % of J/tok". The
top-3 recommended first campaigns are spec decode, the quant ladder, and **MoE-vs-dense
matched-active** — not the top-k knob. So the proposal re-derives a repo-registered idea,
picks a *worse* artifact than the one already vetted for it, and does not engage the
adjudication that ranked it last.

The literature position is also weaker than claimed. arXiv 2606.21428 (the one Apple-silicon
MoE paper) already reports that **"routing itself is <9 % of MoE-block compute — the penalty
is total-parameter footprint, dispatch, KV pressure."** A paper titled *"What Does a Routed
Expert Cost?"* whose intervention is expert *budget* (not routing overhead) will be read as
answering the question 2606.21428 already answered, unless the framing shifts to what is
genuinely open: **the dispatch-bound sublinearity above**, and the matched-active-vs-matched-total
sign flip between arXiv 2504.17674 (+54 % vs dense, A100) and arXiv 2601.22076 (3.56× *less*,
H100/B200 batched) — which the sweep calls "a point of genuine confusion the literature hasn't
resolved cleanly." That is the paper. The k-knob is the *instrument* for it, not the thesis.

Governance, unmentioned: there is **no registry row for MoE routing energy**. The nearest is
`C5-1.9` ("MoE-vs-dense controlled ladder", `status: banked`, L2 after envelope and
denominator guards). Promotion requires a named RQ slot in `PROJECT_STATUS.md` and a data
plan that does not displace higher queue ranks. Also note `TASK_QUEUE.md` A7 (AXI-SE) already
fences this: **"routing-mechanism claims allowed only when auditable expert evidence exists"**
and requires AP-MOE-BATCH / the AP-5 MoE rider to be finalized *against P2-015 floors* — both
still `READY`, i.e. unbuilt.

## Prose defect worth fixing before anyone reads it twice

> "A permanently voided … diagnostic observed approximately 304 J for a 512-output-token
> request … Crude proportional scaling therefore suggests roughly **110 J at 1,024 tokens**;
> use 40–120 J/request as the uncertain planning range."

304 J at 512 tokens scales to **~608 J** at 1024 tokens (and the measured 583 mJ/output-token
gives ~597 J). The 110 J is 18 % of 608 — i.e. the **effect**, not the request energy — and
"40–120 J/**request**" mislabels the effect range as a request quantity. The arithmetic
underneath is right; the sentence says something false. In a metrology paper that is not a
typo, it is a credibility event.

---

## Three strengthening moves

1. **Swap the artifact to `Qwen3-30B-A3B-4bit` (~17 GB) and drop the 122B.** The repo's own
   sweep already verified this checkpoint exists and named it the MoE arm; it is a pure text
   MoE with no vision tower to load-and-discard, no 65 GB residency squeezing the page cache
   during a quiet window, no reasoning/thinking-mode seam gap, and a member energy small
   enough that the projected floor is a smaller fraction of a smaller number. Critically, it
   makes the **matched-active dense comparison possible in the same paper** — `Qwen3-4B-4bit`
   is *already present locally* — so one artifact swap converts a rank-6 knob study into the
   rank-3 campaign the sweep actually recommended, with the k-knob as the causal
   within-checkpoint leg that no prior work has. Keep the 122B as a single scale-context
   diagnostic, not as the claim vehicle.

2. **Fix the floor design and re-anchor every sizing number to a projected floor.** Produce
   **two** floor cells in the floor window (10 absolute + 20 null at k=8 + 20 null at k=4, or
   a second window), so `cross_stack_armwise_max.v1` has both arms. Replace the 15 J desk kill
   gate with **≥3× the projected floor for this cell**, where the projection is scaled from
   the one measured precedent (7B comparative floor = 7.3 % of member mean) and stated as a
   range. Publish the projection and its precedent in the paper — "we predicted our own floor
   from a prior cell and here is how the live mint compared" is a genuine methodological
   contribution that costs nothing.

3. **Promote routing locality from a summary statistic to a co-primary endpoint, and add a
   teacher-forced arm to the desk gate.** Report unique experts per layer, expert-reuse rate,
   and routing entropy per arm alongside joules; this is what separates "removing 4 experts
   costs N joules" from "the divergent text arm B generated happened to route more locally."
   Then reframe the thesis around the finding the physics actually predicts and nobody has
   measured: **batch-1 MoE decode on unified memory realises only ~40 % of the bandwidth
   efficiency of dense inference, so expert-budget savings are sublinear in removed
   parameters.** That claim is floor-gated, mechanism-level, contradicts the naive
   active-parameter model, speaks directly to the matched-active-vs-matched-total sign flip
   the literature has not resolved, and is exactly the kind of result that lifts this from a
   capstone chapter to an ICPE Emerging or EuroMLSys submission.

---

## Bottom line

The feasibility spine is sound and I verified it in source: the artifact exists and is pinned,
the k-knob is a config field, `norm_topk_prob=True` protects output scale, the effect is
plausibly large, the single-request boundary holds, and no borrowed apparatus is needed. This
serves Ed's highest-priority original axis (MoE mechanism) better than anything else in this
portfolio slice, and it reuses §§3–5 of the MVP draft essentially intact.

But the contrast currently has no floor for one of its two arms; the effect/floor ratio is
quoted against a prose constant rather than the one measured precedent, which cuts it from 8×
to plausibly ~2.5×; the kill gate is set below the largest floor ever minted here; the
output-divergence confound is filed as a wording risk when it is an estimand bias; and the
chosen artifact is a 65 GB vision-language hybrid reasoning checkpoint when a 17 GB text MoE
with a matched-active dense partner is sitting one download away and was already vetted by
the repo's own sweep. Fix the artifact, fix the floor, re-anchor the sizing — then it is worth
two nights.

exec
/bin/zsh -lc "sed -n '1,260p' ../portfolio/rev-mvp-icpe-upgrade.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review — `prop-mvp-icpe-upgrade.md`
### "From Software Counter to Scientific Instrument: Phase-Resolved LLM Energy Measurement with Calibrated Refusal"

**VERDICT: WEAK** — sound core, fatal flaw in the thing that makes it an *upgrade*.

| Axis | Score |
|---|---|
| Novelty | **4 / 10** |
| Feasibility | **4 / 10** |
| MVP leverage | **8 / 10** |
| Venue fit | **5 / 10** |
| Original goals | **3 / 10** |

Contributions 1–3 *are* the MVP paper. The proposal's own thesis is that C4 (held-out
workload prediction, "Q4") and C5 (WT310E wall validation) lift it to ICPE full track.
Reviewed on that thesis: C4 cannot be claim-bearing under standing repo doctrine, C5 is
an Apple-silicon replication of a paper the MVP draft already cites, and the night budget
is understated by ~30%. The fallback the proposal itself names — metrology core, workshop
or ICPE Emerging — is the honest version and is genuinely strong.

---

## Numbers audit (the proposal's best feature)

Verified exact against the checkout at `89b929c`:

| Cited | Repo source | Status |
|---|---|---|
| 141.29 J decode contrast | `CLAIMS_STATUS.md:63` (`phase_energy_j.decode`, 7B−1.5B, frozen v3 manifest) | ✅ exact, correctly labelled diagnostic/pre-genesis |
| 14.0 J 7B comparative floor | `CLAIMS_STATUS.md:62` — 13.998036715259254 J | ✅ |
| 5.81 J 128-tok prefill delta; interval to ~4.0 J | `2026-08-07-prefill-feasibility/CONSULT-RESPONSE.md:173,204` — mean 5.809930 J; composed interval **4.001878–7.617982 J** | ✅ exact, and correctly used to *exclude* the arm |
| 3.14 / 3.24 / 2.80 h budgets | `d117-plan-freeze/DESIGN-MEMO.md:327` | ✅ |
| 59-pulse bookends | `docs/contracts/powermetrics_fiducial.md:27` (v3) | ✅ |
| 1.5B decode ≈ 0.09–0.10 J/token | derivable: 7B absolute-cell mean 192.386 J @512 out, minus 141.29 J ⇒ 51.1 J / 512 = **0.0998 J/tok** | ✅ independently reconstructs |
| "long-prompt effects reach tens of joules" | 1.5B prefill 51.07 J @4096 vs 1.712889 J @128 | ✅ understated, if anything |
| **"150-config metrology suite"** | `configs/campaigns/metrology_v1/` holds **191** JSON configs; no "150" anywhere in the repo | ❌ unsourced |
| **"two or three windows"** for the metrology suite | `configs/campaigns/metrology_v1/README.md` §Window packing packs **three** windows (A ~2.76 h, B ~3.09 h "TIGHT", C spillover) | ❌ contradicts the plan it cites |

Arithmetic discipline is above the bar for this factory. That makes the structural
failures below more damning, not less — they are not sloppiness, they are unexamined
inheritance from a superseded measurement regime.

---

## FATAL FLAWS

**F1 — Q4's held-out prediction is a cross-window effect estimate, which standing doctrine
demotes to "preliminary observation."** This kills contribution 4 as specified.

The proposal needs 4 prompt × 3 decode × 2 models × 5 reps = **120 members minimum**, and
concedes it spans "two or three windows." But the repo's sanctioned cross-window mechanism
is *floor transport* — D-082 cl.2 defines a component-scoped cross-window **floor artifact**
schema, where each component keeps its own window basis and allowance, composed by max.
There is no sanctioned path for pooling **point estimates** from different windows into one
estimator. The precedent is explicit and magistrate-set: `docs/run_reports/2026-07-30-mint-merge-coldgate.md:86`
records the 142 J cross-window effect being *relabelled down* to "a strong preliminary
observation — floors bound within-session error; the pre-registered head-to-head is what
upgrades it." `CONSULT-RESPONSE.md` likewise files its cross-window prefill subtraction as
"Corroborating diagnostic only," and D-113 cl.7 forbids mixing window members into a claim
basis at all. A categorical additive fit whose cells were collected on three different nights
is precisely the structure the magistrate has already refused once. The proposal calls the
missing capability "multi-session campaign packing" — a scheduling problem. It is a
claim-custody problem, and nothing in D-082/D-113/D-117 authorises it.

**F2 — Q4's replication counts are sized by a noise-limited formula the project retired.**
The proposal says "normally five repetitions per cell and ten only where prospectively
identified as near-floor." That is AP-1/D-062 sizing, whose arithmetic is
`MDE95 ≈ 1.46 × CV` off a Window-A CV anchor of ~0.3% (`docs/contracts/analysis_plans.md:71-75`)
— a √n-scaling, repeatability-based model. D-078 cl.11 ratified that this instrument is
**attribution-limited (~1 J), not noise-limited (~0.3 J)**, and floors compose repeatability
**plus** a worst-case attribution bound **plus** never-zero drift. A bound does not divide by
√n. The evidence is in the proposal's own citation: the prefill delta has SD 0.121 J over
n=10 blocks, yet a composed half-width of **1.808 J**. Going 5 → 10 reps buys essentially
nothing against the binding term, so the mitigation the plan reserves for near-floor cells is
inert. Per the project's own doctrine, workload **length** is the only free lever — which the
proposal knows (it uses it correctly for micro-deltas) and then forgets for Q4.

**F3 — the ICPE venue gate is hung on hardware that is neither owned nor doctrinally load-bearing.**
"Wall-meter dependency: **yes** for this proposed ICPE-full version" directly contradicts
D-092, which ratified C8 while ruling that "**every claim except C8 must stand on the internal
instrument characterization; C8 stays conditional in the outline and is not assumed**." The
proposal inverts a ratified conditional into a submission blocker. Compounding: D-092 assumed
*purchase*; the borrow path adds an advisor-lab calendar dependency the proposal never dates.
The kill list names "battery-charge neutralization" but supplies no protocol — an M3 Max MBP
on AC with a charging battery makes wall power a function of state-of-charge, and this is the
single most likely way the whole C5 arm produces uninterpretable data. A "safe inline fixture"
is also mains work by an undergraduate, unscoped and unscheduled.

---

## Should-fix

**S1 — night budget understated ~30%.** Claimed 9–10 (3 D-117 + 6–7). Reconstructed:
D-117 **3**; metrology suite **3** (the README packs A/B/C, not "two or three"); Q4 **3–4**
(at ~2.6 min/member from the proven ten-absolute set's 25–28 min, 120 members ≈ 5.5–6 h
science before references, NEG-8 corpus, and 20% margin — and P2-019 additionally requires an
8192-prompt anchor that the proposal silently drops); wall pilot + confirmatory **2**;
contingency **1**. Total **12–13 nights**. One contingency night against a project whose
recorded history includes Window B failing outright (D-113 claim-retired) and 43/50
su-calibration bundles contaminated by a screensaver is not a reserve, it is optimism.

**S2 — "already-designed metrology suite" overstates readiness.** `metrology_v1/README.md`:
"The five draft plans … **must be magistrate-ratified before measurement**,"
`freeze_status: draft_pending_magistrate_ratification`, `micro_delta/k0064` is "only a
DRAFT-PENDING-SLOPE placeholder," and three open ratification questions remain. Also, the
suite "**does not gate a scientific claim, introduce a model, or mint a detection floor**"
and its runnable members are **1.5B only** — so three of the six-to-seven extra nights buy
characterisation, not claims, and say nothing about the 7B stack that carries the headline
contrast. Worth funding; not worth mislabelling.

**S3 — pre-arm blockers omitted from the critical path.** DESIGN-MEMO F1–F3 (two-slot bracket
session; prefill-capable multi-cell mint; D-102 live-prefix successor path) are open blockers
before *any* D-117 arm, and `89b929c` adds live ones (path-doubling in verdict R6; bracket
borrowing; scalar-only preflight). The proposal lists these as desk work without acknowledging
they gate night one.

---

## Novelty

Weakest axis, and the diagnosis is uncomfortable: **the two contributions that constitute the
"upgrade" are the two least novel things in the proposal.**

- **C4** — that inference energy ≈ fixed + prompt term + decode term is the working assumption
  of essentially every LLM-energy paper (Samsi et al.; Fernandez et al.; Husom et al.;
  Stojkovic et al.; LLMCarbon; ML.ENERGY/Zeus). Confirming additivity is not a finding. Its
  only novel element is pre-registered refusal semantics — which is C2's contribution, reused.
- **C5** — Jay & Ostapenco (CCGRID 2023) already established load-dependent software-vs-wall
  divergence, and `docs/paper/draft-v1.md:30` **already cites it** while arguing a wall meter
  observes only a total and cannot validate phase attribution. C5 is therefore a
  substrate-swapped replication of prior work the draft itself frames as the less interesting
  axis, purchased with a borrowed instrument and two nights.
- **C1–C3** are the real novelty, and they are the MVP. The measurement space is now populated
  — *Silicon Showdown* (arXiv 2605.00519, May 2026) uses powermetrics for Apple-silicon LLM
  tokens/joule; TokenPowerBench (arXiv 2512.03024) decomposes prefill/decode phase power;
  ML.ENERGY has published Mac profiling. What none of them do is quantify what their counter
  **cannot** resolve. Targeted search returns nothing on detection floors, attribution limits,
  or refusal reporting for software power counters. That gap is real and it is already banked.

## Venue-fit honesty

Partly creditable, partly evasive. Creditable: it names the workshop/Emerging-track fallback
and reuses the MVP's single-stack limitations rather than hiding them. Evasive: **no calendar**
— the impressiveness roadmap flagged "Venue and calendar ambition remain unbound" as an open
finding (F3) and this proposal reproduces the blindness while proposing 6–7 extra nights plus
a hardware loan. And the generalisability objection an ICPE full-track referee will actually
raise (n=1 machine, one model family, one framework, one quantisation) is not addressed by
either upgrade; a single borrowed meter on the same single machine does not touch it.

## Original goals

Honestly declared as unserved — credit for refusing to smuggle. But the proposal *misses that
it is holding the mechanism axis in its hand.* The (4096, 512) cell is a KV-cache/attention
scaling experiment: decode cost per token rises with context because attention reads a growing
cache. Sizing it (Qwen2.5 configs, from memory — **verify against the pinned `config.json`**):
1.5B ≈ 28 layers × 2 KV heads × 128 dim × 2 × 2 B ≈ 28 KB/token ⇒ ~117 MB at 4096 ctx against
~0.77 GB of 4-bit weights ⇒ **~14% decode-energy rise ≈ +7 J** over 512 tokens; 7B ≈ 57 KB/token
⇒ ~235 MB against ~3.8 GB ⇒ ~6% ⇒ **≈ +12 J**. Both clear the ~5 J bar. The proposal predicts
additivity *holds*; the interesting, publishable, mechanism-level result is the measurable
deviation — and it is exactly the KV/attention axis Ed wants.

---

## Three strengthening moves

1. **Replace C4 with a single-window KV-context-scaling contrast.** Fix decode length,
   vary prompt context (128 vs 4096), collect both arms **inside one window** as an ABBA
   pair — which cures F1 (no cross-window estimator), cures F2 (length is the lever, not
   reps), converts the least-novel contribution into the most-novel one, and serves the
   original KV/attention goal. Freeze the tolerance as a number before collection.
2. **Re-cost to 12–13 nights, and label each night's yield.** Separate claim-bearing nights
   from characterisation nights (the metrology suite mints nothing), scale contingency to the
   project's demonstrated window-failure rate rather than to one reserve night, and put the
   DESIGN-MEMO F1–F3 blockers and the `89b929c` U1/U2 findings on the critical path ahead of
   night one.
3. **Demote C5 to a conditional appendix and unhook it from the venue.** Restore D-092's
   posture: C8 conditional, not assumed. Submit on the metrology core; add the wall arm only
   if the loan, an in-calibration certificate, a named battery-neutralisation protocol, and a
   qualified fixture all land by a dated deadline — and set that deadline, since the repo has
   flagged its absence twice.

exec
/bin/zsh -lc 'for f in ../portfolio/rev-open-explore-advisor.md ../portfolio/rev-open-explore-contrarian.md; do echo "FILE $f"; sed -n '"'1,420p' \""'$f"; done' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
FILE ../portfolio/rev-open-explore-advisor.md
# Counter-review: `prop-open-explore-advisor.md` (advisor-lens open exploration)

**Reviewer:** Opus 5, counter-review lens (contract + resourcing + dedup).
**Ground truth checked against:** `desk@89f28bf` — `docs/decision_log.md` D-117,
`docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`,
`docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md`,
`docs/paper/draft-v1.md` §§6–8, `CLAIMS_STATUS.md`.
**Pool members compared:** `prop-mvp-icpe-upgrade`, `prop-wall-meter-validation`,
`prop-prefill-scaling-laws`, `prop-drift-thermal-science`,
`prop-long-generation-dynamics`, `prop-floor-methodology-general`.

---

## Headline

**Every factual number in this proposal checks out** — the most accurate submission
I have audited in this pool. And it does not matter, because **all three papers are
dominated by other pool members.** Paper 1 is the plan of record with a title on it.
Paper 2 is `draft-v1.md` §6, which already exists in the repo as six
`[PENDING WINDOW C]` rows, and is also contribution 2 of `prop-mvp-icpe-upgrade`.
Paper 3 is `prop-wall-meter-validation` with the acceptance rule, the held-out
design, the battery control and the primary-source meter citations removed.

Net unique portfolio contribution: **approximately zero.** Its residual value is as a
*convergence signal* (an independent lens ranked the same three things in the same
order) and as the surfacing of one real gap in the MVP scope (§6 ships empty), which
argues for a merge that a different proposal already proposes.

---

## (a) Is the advisor modeling credible, or a caricature?

**CREDIBLE, but shallow and under-exploited. Not a caricature — and that is the
problem.** It invents no advisor opinions that contradict the record; it also never
reaches the two artifacts that a JouleSort/Mantis author would most obviously want.

What it gets genuinely right:

- **Full-system boundary as the deepest objection.** JouleSort's defining move was
  measuring the *whole system at the wall* under a fixed workload with published
  entry rules. The proposal correctly identifies that `powermetrics`' modeled SoC
  boundary is *not* the full system, and makes closing that gap a whole paper. That
  is the highest-signal advisor prediction available and it is correctly made.
- **Refusal-as-evidence maps to benchmark-entry validation.** JouleSort disqualified
  invalid entries; JouleWise retains refusals as evidence. The proposal connects
  these, correctly.
- **Correct instinct that a metrology referee prefers instrument depth over
  premature mechanism breadth.** Consistent with the repo's own advisor-feedback
  record. It also correctly refuses to smuggle mechanism work in.
- **It does not overclaim what a wall meter can validate** ("agreement validates
  totals, not the prefill/decode split"). That is the right epistemic line and it is
  drawn explicitly as a *contribution*, which is good taste.

Where the modeling is thin — and these are misses, not stylistic quibbles:

1. **It never proposes an efficiency metric or benchmark rule set.** JouleSort's
   actual contribution was `sorted records per joule` plus divisions, entry rules and
   a validator. The JouleWise-shaped analogue — a defined tokens-per-joule with a
   named boundary, an honest denominator, and the fail-closed protocol as the entry
   rule set — is the single most JouleSort-lineage artifact this material can yield,
   and the session dedicated to the advisor lens does not mention it once. (It lives
   in `prop-energy-nutrition-label` / `prop-tokenizer-honesty` instead.)
2. **It never names Mantis / the counter→wall-model lineage.** Rivoire's other
   principal line of work is full-system power *models* from OS counters validated
   against a wall meter across load families. That is *exactly* Paper 3's shape, and
   framing it that way would materially strengthen the positioning. Worse:
   `draft-v1.md` §8 cites RAPL-in-Action, Jay & Ostapenco, MLPerf Power and SPEC —
   **and cites neither JouleSort nor Mantis.** The one session tasked with the
   advisor's perspective failed to catch that the paper does not cite its own
   advisor's foundational work. This is a real, actionable finding the session was
   uniquely positioned to make and did not.
3. **It ignores the standing plain-language requirement.** Advisor-facing surfaces
   get plain language and defined terms (standing, from actual professor feedback).
   A session modeling this advisor should have flagged the reader-facing prose bar.
   It modeled the advisor's *technical taste* and not her *communication bar*.
4. **One unevidenced disposition claim carries the whole ranking** ("a metrology
   reviewer would value these above premature mechanism breadth"). Probably true;
   asserted, not argued.

**Verdict on (a): credible lineage instincts, executed at half depth. Do not use this
document as the portfolio's model of the advisor — it is missing the benchmark-design
half of the lens entirely.**

---

## (b)+(c) Per-idea audit

### Paper 1 — "Calibration Before Comparison: Detection Floors for Phase-Resolved LLM Energy"

**Verdict: VIABLE (redundant — it is the funded plan, not a proposal).**

| axis | score |
|---|---:|
| novelty | **2** |
| feasibility | **10** |
| mvp_leverage | **10** |
| venue_fit | **6** |
| original_goals | **1** |

**Fact-check: clean.** Every number verified against ground truth — 3.14 / 3.24 /
2.80 h budgets (DESIGN-MEMO §Runtime evidence and budgets, all Pass in the 2–4 h
envelope); 50 science bundles as 10 absolute + 40 null-ABBA (memo §alpha, and the
extraction spec's "100 cell-member references but exactly 50 unique bundles"); 40
ABBA contrast members; prefill riders as a new condition family over the same
bundles at zero added runtime; 141.29 J as the *registered* claim metric (correctly
distinguished from the 146.73 J whole-request diagnostic, which it does not quote);
141.29 / 5 = 28×; prefill exclusion at 5.809930 J point with ~4.0 J interval lower
edge. It also correctly states that a contrast failure would mean changed stack
behavior or invalid transfer — **not** license to select another run. That is the
exact discipline D-110/D-117 demand.

**Fatal flaw (as a *direction*, not as work):** it proposes nothing. "Exactly the
three D-117 nights; no extra members" is the decision already adopted today. A
portfolio direction that recommends executing the current plan carries zero decision
information. Its correct role is baseline, and the baseline is already funded.

**Second flaw — the one substantive thing it hides:** Paper 1 says it reuses "the
draft's introduction, calibration, floor, protocol, and limitations sections." It
never mentions **§6, Instrument characterization** — whose six rows are *all*
`[PENDING WINDOW C]`. So Paper 1 ships a metrology paper whose entire
instrument-characterization section is empty, publishing detection floors with no
operating-characteristic evidence that those floors mean anything. That is precisely
the first question a measurement referee — and this advisor specifically — will ask.
The advisor lens should have caught this and merged Papers 1 and 2. It instead split
them and stayed silent about the seam.

**Contribution 1 is not new:** "attribution width exceeds ordinary repeatability" is
already RATIFIED (D-078 cl.11) as a standing project finding. Publishing it is
right; listing it as a falsifiable contribution of these three nights is padding.

**Venue:** capstone yes. "Credible ICPE emerging/workshop" — I'll grant workshop; not
ICPE full, and the proposal does not claim otherwise. Fair.

**OVERLAP FLAG — SUBSET of `prop-mvp-icpe-upgrade`.** That proposal contains Paper 1
verbatim as its stage 1 (same budgets, same 10+40, same 141.29 J / 5.81 J reasoning)
and then adds the ICPE delta. Paper 1 is strictly contained. **Dedup value: nil.**

---

### Paper 2 — "Does the Detection Floor Behave Like a Detection Floor?"

**Verdict: VIABLE as *content*, WEAK as a *standalone paper*. Merge, do not fund
separately.**

| axis | score |
|---|---:|
| novelty | **6** |
| feasibility | **4** |
| mvp_leverage | **9** |
| venue_fit | **5** |
| original_goals | **2** |

The science is the right science — a published operating characteristic for a
software energy counter is a genuinely uncommon artifact and is what makes the floor
claim credible. Four specific problems.

**1. Night budget understated ~2×. Its own kill criterion fires.** Using the memo's
own runtime evidence (1.5B decode member 92.7 s; ABBA blocks 1–5 = 20 members in a
34 min allowance, i.e. ~10% overhead; fixed per-window cost = 8+8 calibration + 22
NEG8 + 21 references + 10 untouched idle ≈ 69 min; 20% margin):

- *Linearity window* (5 length levels 128→2048, n=5): ~52 min raw member time →
  ~2.7 h. **Feasible in one window. Correctly sized.**
- *Micro-delta window* at the project's standard n=10 block basis: 4 levels × 40
  members = 160 members at ~100 s ≈ 267 min raw → (294 + 69) × 1.2 ≈ **7.3 h.**
- Even degraded to n=5 blocks (80 members): (147 + 69) × 1.2 ≈ **4.3 h** — still over
  the proposal's own stated kill line of four hours, and now with a halved block
  basis for the very interval gate under test.

Realistic total is **1 linearity + 3 micro-delta nights ≈ 4 additional windows**, not
"two." And the proposal's kill criterion — "kill if the frozen design exceeds four
hours" — self-executes on its own arithmetic. `prop-mvp-icpe-upgrade` budgets the
same experiment across a metrology window A, a window B *and* a short third window;
that is the honest number.

**2. Slope estimate is biased in the wrong direction.** The proposal derives
"~47 J / 512 tokens ≈ 0.09 J/token" from a *whole-request* diagnostic. Whole-request
energy includes prefill and fixed per-request overhead, so this is an **average**,
not a **marginal** slope, and the true marginal slope is *lower*. Consequently the
quoted 27 / 54 / 81 / 163-token deltas are **too small** to hit 0.5×/1×/1.5×/3× the
floor — longer members, worse budget, in the same direction as flaw 1. The proposal
does hedge ("crude, design-only, must be frozen from a desk pilot"), which is why
this is a should-fix and not a blocker; but the hedge does not rescue the budget.

**3. Circular ground truth — the design's real blocker.** The "known" injected effect
magnitude is *predicted from the fitted slope*. So the operating-characteristic test
measures (slope-model error + detection performance) jointly and cannot separate
them. At the 0.5× arm the slope's prediction uncertainty is of the same order as the
injected effect, so "the instrument correctly refused a sub-floor effect" is
observationally identical to "the injection missed its target." The pass/fail rule
must be stated against a *propagated prediction interval* on the injected effect,
with per-member runtime-observed token counts, or the whole contribution is
unfalsifiable. Not addressed anywhere.

**4. Two physical confounds silently assumed away.**
   (i) **Unequal-duration ABBA.** Injecting effects via output-length deltas makes A
   and B members different lengths, breaking the duration symmetry the null-ABBA
   design and the measured drift allowance were established under; A and B stop being
   exchangeable within a block. This is exactly the coupling `prop-drift-thermal-science`
   exists to characterize.
   (ii) **The floor is treated as one scalar across 128–2048 tokens.** Repeatability
   plausibly scales with total energy while attribution does not, so there is likely a
   *per-magnitude* floor — which multiplies windows again. Draft §6 knows this (it has
   a separate "Null response across magnitudes" row); the proposal does not.

**Venue:** I contest "the strongest owned-hardware route toward an ICPE full paper."
An operating-characteristic study alone is a methods/measurement workshop paper.
`prop-mvp-icpe-upgrade`'s argument — that ICPE full needs characterization *plus* a
held-out prediction study — is the more persuasive read of that track.

**OVERLAP FLAGS (three):**
- **`prop-mvp-icpe-upgrade` contribution 2** is this experiment, stated more
  precisely (nulls at 128/512/2048; slope 0.09–0.10 J/token; 64-token delta ≈
  5.8–6.4 J) and honestly multi-window budgeted. **Dominated.**
- **`docs/paper/draft-v1.md` §6** already specifies this program in-repo as
  `[PENDING WINDOW C]` — linearity, null response across magnitudes, empirical floor
  verification via 0.5/1/1.5/3× micro-deltas in both directions. This is not a new
  paper idea; it is an unexecuted section of the existing draft. The proposal
  half-admits this ("adds the currently pending draft §6 rows") without drawing the
  conclusion.
- **`prop-long-generation-dynamics`** owns the 128→2048 decode ramp as its subject.
  Partial overlap on the linearity window.

---

### Paper 3 — "From SoC Estimate to Wall Energy: Validating the Measurement Boundary"

**Verdict: KILL as a distinct direction. Strictly dominated by
`prop-wall-meter-validation`; subsume.**

| axis | score |
|---|---:|
| novelty | **3** |
| feasibility | **3** |
| mvp_leverage | **6** |
| venue_fit | **6** |
| original_goals | **3** |

Same thesis, same borrowed WT310E, same 1.5B/7B levels, same "one pilot + one
confirmatory window," same correct "totals not the split" conclusion as
`prop-wall-meter-validation` — and worse on every axis where they differ:

| | advisor Paper 3 | `prop-wall-meter-validation` |
|---|---|---|
| acceptance rule | none stated | `ΔE_wall = α + βΔE_pm`, held-out residual ≤ `max(floor, 5% ΔE_wall)` |
| design | "paired workloads at ~512 and 2048" | 4 levels × 6 paired blocks, 4 fit / 2 held-out, counterbalanced |
| load-dependence | not tested | explicit falsifier across idle / GPU-pulse / LLM families |
| battery control | one clause inside *kill criteria* | designed control with recorded battery observations |
| meter sourcing | marketing product page | user manual + communication manual, 100 ms update, fixed-range warning |
| planning energies | 47 J / 192 J | 51 J / 192 J **with a 5–30% discrepancy band → 2.5–15 J and 10–58 J**, i.e. it actually shows the short cell may not clear the bar |

Flaws that are Paper 3's own, beyond being dominated:

1. **Unbudgeted extra window.** It requires "a wall-specific null/repeatability
   floor" — i.e. a whole floor-minting program with its own members and calibration —
   and then budgets one pilot plus one confirmatory window. Minting a wall floor is
   at minimum another night. Under-budgeted by ≥1 window.
2. **Contribution 2 has no acceptance rule.** "Test whether the 1.5B-vs-7B direction
   survives the boundary change" needs a wall-side interval, which needs the floor in
   (1). Circular as written.
3. **Meter suitability asserted, not computed.** It quotes "0.1% of reading + 0.05%
   of range" from a product page and then says suitability "must be calculated at the
   observed load" — without calculating it. At a ~5–75 W laptop load on coarse power
   ranges the *range* term likely dominates; that arithmetic is the feasibility
   question and it is deferred. Also: the accuracy figure itself needs verification
   against the WT310E manual before it goes anywhere near a paper.
4. **It never derives its own central claim.** The crisp argument for "wall cannot
   validate the split" is a sampling-rate argument: 100 ms meter updates are ~3×
   *coarser* than the ~30 ms edge uncertainty that defines the attribution limit. The
   proposal states the conclusion as an assertion instead of deriving it from the
   instrument, which is a wasted opportunity in the one section where this lens
   should be strongest.
5. **Prior art unengaged.** Counter-vs-wall validation with load-dependent error is
   ~2006-era Mantis territory and the Jay & Ostapenco line already cited in the
   draft's §8. Neither is engaged; novelty rests on "on a Mac, for LLM phases."
6. **External dependency.** Gated entirely on a loan Ed does not control. The
   proposal is right to make "no loan means no paper" a kill criterion and right to
   refuse a smart-plug substitute.

**OVERLAP FLAG — NEAR-TOTAL DUPLICATE of `prop-wall-meter-validation`**, and also
overlaps `prop-mvp-icpe-upgrade` contribution 5. **Dedup value: nil. Discard this
version; keep the sibling.**

---

## Synthesis guidance

1. **Do not allocate a portfolio slot to this session.** All three papers are
   dominated. Use it as corroboration that the pool's center of gravity
   (floors → characterization → wall boundary) is correctly ranked, which is real but
   cheap information.
2. **Harvest exactly two things.** (i) The observation that the MVP as scoped by
   D-117 ships with `draft-v1.md` §6 entirely `[PENDING]` — which is an argument for
   folding characterization into the MVP/ICPE scope, i.e. for
   `prop-mvp-icpe-upgrade` over a Papers-1-and-2 split. (ii) Paper 1's fact-checked
   restatement of the D-117 spine, which is accurate enough to reuse verbatim as the
   shared project-brief paragraph across the portfolio.
3. **Log the advisor-lens gap as a task, not a paper.** `draft-v1.md` §8 cites
   neither JouleSort nor Mantis. The paper does not cite its advisor's foundational
   work, and the advisor-lens session did not notice. Fix in the draft; it costs desk
   minutes and it is the kind of omission that colors a first read.
4. **If Paper 2's content is funded** (inside the ICPE upgrade, where it belongs),
   the three blockers above — circular injected-effect ground truth, unequal-duration
   ABBA exchangeability, per-magnitude floors — must be resolved at the desk *before*
   any night is armed. Each is cheap on paper and expensive in wasted windows.
FILE ../portfolio/rev-open-explore-contrarian.md
# Counter-review — `prop-open-explore-contrarian.md`

**Reviewer:** Opus 5 counter-reviewer (independent). Ground truth: `desk` @ main.
**Proposal:** "Contrarian recommendation: three defensible course changes"

## Verdict: **WEAK**

Unusually accurate on facts — I found essentially no factual error worth calling a
defect — and almost entirely empty as a course-change argument. All three "course
changes" are already-ratified items in `docs/strategy/2026-08-06-impressiveness-roadmap.md`
(ranks 1, 2 and 7), and Idea 1's thesis is verbatim the existing thesis of `draft-v1.md`
§2. One genuinely load-bearing finding is buried inside Idea 1 as a subordinate clause,
and it *should* go to Ed — but as a scope ruling, not as a change of course.

| Axis | Score | One-line justification |
|---|---:|---|
| novelty | **2** | Nothing here is absent from the ratified roadmap or the draft's own framing. It re-types rank 1, rank 2 and rank 7 and calls them departures. |
| feasibility | **7** | Idea 1 is trivially feasible because it *is* the current plan; Idea 2 is feasible only on an unsecured loan; Idea 3's feasibility is better than it claims but its stack swap breaks floor transport. |
| mvp_leverage | **6** | Idea 1 helps by pruning, and the §6 / C-iv gap it half-surfaces is the single most useful thing in the file. Ideas 2 and 3 both spend before the MVP lands. |
| venue_fit | **5** | Idea 1's ladder matches the roadmap. Idea 2's "best chance of an ICPE full metrology paper" contradicts the repo's own criteria. |
| original_goals | **5** | Idea 3 really serves the mechanism axis — then picks the second-best mechanism and silently discards the best-scoring one. |

---

## Part 1 — Fact-check against the repo (this is the proposal's strongest section)

| Claim | Status | Evidence |
|---|---|---|
| "complete methods-paper structure but **no citable scientific number**" | **VERIFIED** | `CLAIMS_STATUS.md` §1: "**NONE at this checkpoint**"; "pre-genesis windows CANNOT be claim-consumed — their role is diagnostic and rule-establishing only." |
| D-110/D-117 made earlier passed windows diagnostic | **PARTLY** — right conclusion, loose mechanism | It attributes this to windows "predating the issued calibration regime". The actual ground (D-117 cl.1) is that the issued ledger holds only **import-marked** receipts, candidate discovery excludes imports *by design*, and future live receipts cannot causally bracket past windows — structurally unsatisfiable, not a date rule. D-110's separate ground (RT-1: a never-zero allowance of ZERO where D-102 pin 3 mandates `max(drift, 0.010818)`) is a different defect. Also worth noting the verdicts themselves are **untainted** (RT-5); it is *consumption* that is closed. |
| 3.14 / 3.24 / 2.80 h occupancies | **VERIFIED exactly** | DESIGN-MEMO budget table (188.4 / 194.4 / 168.0 min with 20% margin). |
| 10 absolute + 40 null-ABBA per floor window; "140 science members" | **VERIFIED** | Alpha/beta stage tables (absolute 10, null halves 20+20 → 50); gamma 40. 50+50+40 = 140. |
| Prefill riders ride the same bundles at no extra capture cost | **VERIFIED** | "The prefill rider adds no member and no runtime"; 100 cell-member references over exactly 50 unique bundles. |
| "141.29 J" historical decode contrast; "~28× the 5 J bar" | **VERIFIED**, correctly labelled diagnostic | `docs/run_reports/2026-08-03-16h-runway.md:67`: "registered claim metric `phase_energy_j.decode` 141.29 J vs the 146.73 J idle-subtracted diagnostic." 141.29/5 = 28.3. |
| 128-token prefill contrast 5.81 J, lower interval edge ~4 J, should remain unclaimed | **VERIFIED exactly** | prefill-feasibility SYNTHESIS: 5.809930 J point, composed half-width ~1.81 J, lower edge ~4.0 J, corroborated at 5.903 J; magistrate CONCUR on decode-only. |
| Desk blocker list (two-slot bracket, D-102 successor, prefill-capable four-cell mint, three-window regression, campaign packs, operator/readiness) | **VERIFIED** | Maps 1:1 onto DESIGN-MEMO F1/F2/F3 and units U4–U8. Omits U9/U10 (bookkeeping, postcollection pins) — immaterial. |
| C8 wall meter ratified as future work; borrowable | **VERIFIED but understated** | D-092 (`decision_log.md:117`, Rivoire-answered) ratified the wall meter *for the paper* as claim C8. Roadmap ranks it **#2** and already parks "borrow versus buy… and a cutoff date" as an open Ed decision. |
| Spec-decode 80–230 J, "~6–16× the older conservative 14 J floor" | **VERIFIED verbatim**, correctly flagged uncertain | `docs/run_reports/2026-07-30-sweep-mechanisms.md`, rank-2 row. |
| "pinned `mlx-lm` lacks proposal-count and step-boundary observability" | **VERIFIED — and the proposal understates its own case** | Roadmap F2 confirms it for pinned `mlx-lm`. But `RUN_STATE.md:1979` records "**DSpark/DFlash MLX feasibility CONFIRMED w/ per-round observability**" (2026-07-17), and `joulewise/adapters/mock_spec_runtime.py` plus the frozen AXI-SA bundle contract (`AxiCancelledProposalCounters`) already exist. Part of the gate it wants 2–3 weeks for is already discharged. |

Verdict on Part 1: **near-zero factual error, and the two imprecisions run against the
proposal's own interest.** Credit where due — this is a well-grounded document.

## Part 2 — Are these course changes? No.

**Idea 1 is not a course change; it is the ratified plan plus a label.** Its thesis — "make
the attribution-limited instrument and its calibrated refusals the scientific result" — is
already `draft-v1.md` §2, closing paragraph: *"JouleWise fills that gap by making instrument
characterization and refusal behavior the primary result; model comparisons are
demonstrations of what the characterized instrument can and cannot resolve."* Its experiment
plan is exactly D-117, unmodified. Roadmap rank **1** is "Complete C1–C7 cleanly." Nothing
is being changed. Presenting the status quo as a departure spends the proposal's credibility
on a no-op, and it is the reason the document reads as contrarian in posture only.

**...but one real finding is hiding inside it,** in a subordinate clause: *"replace the
oversized pending characterization table in §6 with the prospective floor/contrast
evaluation."* That points at a live, unrecorded scope contradiction:

> Draft §6 — contribution **C-iv, "full instrument characterization"** (linearity, null
> response across magnitudes, empirical floor verification, phase-attribution causal
> consistency, drift/settling, between-session stability) — has **all six rows marked
> `[PENDING WINDOW C]`**. D-117 funds three windows, none of which is a Window C, and
> D-117 cl.4 explicitly places the broader MET-WINDOW-C-01 C2/C4/C5 campaign *after* the
> three-window closure. So when all three D-117 nights land, §4 gets its floors and §7 gets
> its demonstration — **and §6 stays entirely empty. One of the paper's six advertised
> contributions will have zero evidence.**

Either C-iv is descoped for the MVP (contribution list, abstract and §6 rewritten as
declared future work, with the limitation stated) or the MVP needs a fourth night. I can
find no decision entry recording that choice. **This is the one item worth surfacing to
Ed.** The proposal earns partial credit for reaching it and a mark down for not naming it
as *the* finding — it is buried under a rhetorical frame that invites dismissal.

**Idea 2 is not a course change and its payoff is overstated.** D-092 already ratified the
wall meter for the paper as C8; the roadmap ranks it #2 and already lists borrow-vs-buy and
a cutoff date as Ed decisions. Its headline claim — "best chance of an ICPE full metrology
paper" — contradicts the repo directly: the roadmap says wall validation "validates totals
only—not phase allocation," and ICPE full requires "C1–C8, cross-day stability,
artifact-ready release, **and at least one deeper contribution**." Wall validation is one of
four prerequisites, and the only one gated on an instrument Ed does not own and a loan that
is not secured. Against the paper-first stack (P1 = capstone MVP), funding the
importer / clock-sync / held-out-regression desk stack *before* the MVP lands trades P1 time
for a P2 benefit contingent on someone else's lab calendar. Its own kill criteria concede
the dependency. The roadmap's sequencing — after the MVP, in parallel with the artifact
release, with a hard cutoff — is better and already ratified.

**Idea 3 is the only real course change — and it is the wrong pick, for a reason in the file
it cites.** Three problems:

1. **It selects against the repo's own effect/floor arithmetic.** The
   `2026-07-30-sweep-mechanisms.md` table it quotes ranks spec decode **second**
   (80–230 J, ~6–16× floor). **Rank one in the same table is weight quantization 4b vs 8b:
   ~450–700 J, ~35–50× floor** — a larger, better-understood effect needing no new stack,
   no new observability, no event-schema extension, no custody/admission re-integration,
   with quality screening runnable outside quiet windows (roadmap #5, "1–2 nights"). The
   proposal drops quantization in a list ("Drop wall validation, Q4, broad C1–C5
   characterization, quantization, MoE, MTP, and split") **without ever arguing against
   it**. Choosing ~1/4 the effect/floor ratio at ~10× the engineering risk, while silently
   discarding the dominant alternative, is the document's worst reasoning failure.
2. **Its stack swap voids the D-117 floors it claims to build on.** Draft §1 scopes a
   measurement to "one physical unit, operating-system build, **runtime and library stack**,
   model artifact, quantization, tokenizer, sampling policy…". A separately pinned
   DSpark/DFlash MLX stack is a new condition family; the design memo's transport rule
   (which forbids even a 128-prompt prefill rider from transporting to a 256-token contrast
   without exact matching cells) binds here too. So "use D-117 as the calibration
   foundation" is precisely what a new runtime pin forbids. Its "five nights total including
   D-117" is right in *count* and wrong in *kind*: it buys the MVP plus a separate island
   study sharing §§3–5 methods and none of its floors.
3. **Output identity is the fragile part and gets one sentence.**
   `C-023-OUTPUT-IDENTITY` binds every C5-2.5 rider ("Fixed output-token count is not fixed
   decoded work"). "Deterministic on/off outputs match exactly in dry trials" is the right
   gate, but spec decode against a different drafter is exactly where it breaks, and the
   proposal budgets nothing for the failure branch.

**Funding order:** its own ordering (1 safest, 2 if the loan lands, 3 highest upside) is the
roadmap's ordering with the numbers re-typed. No new information.

---

## Fatal flaws

1. **Not contrarian.** All three proposals are already-ranked items in the ratified roadmap
   (ranks 1, 2, 7 — and rank 7 even names *external-draft speculative decode* as the
   recommended first mechanism choice behind a 2–3 week feasibility gate, which is Idea 3
   almost word for word). Idea 1's thesis is the draft's existing §2 thesis. A proposal
   whose assignment was to challenge ratified direction instead ratifies it while claiming
   otherwise; that mislabelling is itself an evidence failure and it obscures the one thing
   in the file that *is* new.
2. **Idea 3 discards the higher-scoring mechanism without argument** (quantization
   450–700 J / 35–50× floor / existing stack, vs spec decode 80–230 J / 6–16× / new stack).
3. **Idea 3's new stack pin breaks the very floor transport it claims to inherit**, so its
   five-night plan does not produce one paper.
4. **Idea 2's headline payoff contradicts the repo's own assessment** of what a wall meter
   can validate (totals, not phase allocation) and of what ICPE full requires, while being
   the only idea gated on unowned apparatus.

## Three strengthening moves

1. **Lead with the one real finding and drop the other two.** Rewrite the whole document as
   a single scope ruling for Ed: *the three D-117 windows do not produce §6.* Quantify it —
   six `[PENDING WINDOW C]` rows, one of six advertised contributions, zero D-117 members
   addressing them — and present the binary: descope C-iv from the MVP (rewriting the
   contribution list, abstract and §6 as declared future work, with the limitation stated in
   the paper) or fund a fourth characterization night. That is a genuine, decidable,
   currently-unrecorded decision; the "three course changes" framing is what buries it.
2. **Re-run Idea 3's selection against the repo's own table, then defend the pick or switch.**
   The honest comparison is spec decode (80–230 J, new stack, new events, floors don't
   transport, output identity fragile) versus the quantization ladder (450–700 J, existing
   stack, existing floors transport, off-window quality screening). Either argue the novelty
   premium explicitly — it may well win, spec decode is the more interesting result — or
   take the quantization ladder for the capstone and hold the mechanism ambition for ICPE.
   Also update the feasibility claim: `RUN_STATE.md` already records DSpark/DFlash per-round
   observability CONFIRMED, so the 2–3 week gate is partly pre-paid.
3. **Re-scope Idea 2 to what is actually decidable now.** Not "spend two nights on the wall
   meter" but "set a loan-secured-by date and a cutoff after which C8 is cleanly removed" —
   literally the open decision the roadmap already parks with Ed. Correct the payoff claim to
   the repo's own wording (totals only, not phase allocation) and state the residual plainly:
   the wall meter cannot validate the paper's central contribution.

## Should the magistrate surface anything to Ed?

**Yes — exactly one item, and it is none of the three ideas as framed:** the §6 / C-iv gap.
Recommend surfacing it as a **scope ruling** ("does the MVP still claim C-iv?"), not as a
course change, and not attributed to this proposal's contrarian framing, which will invite
the wrong kind of dismissal. Nothing else in this document meets the bar for reopening
D-117 or the paper-first stack.

exec
/bin/zsh -lc "sed -n '1,430p' ../portfolio/rev-open-explore-registry.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review — `prop-open-explore-registry.md` (open-ended, registry-sourced)

Reviewer: Opus 5, adversarial counter-review lens (contract + feasibility + novelty).
Ground truth: `scratchpad/desk` @ main; D-117 at end of `docs/decision_log.md`;
`docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`;
`docs/process_traces/2026-08-07-prefill-feasibility/CONSULT-RESPONSE.md`;
`docs/strategy/2026-08-06-impressiveness-roadmap.md`; `docs/paper/draft-v1.md`;
`docs/research_question_bank.md` / `_registry.md`.

Proposal reviewed: final block, lines 6314–6368 (an earlier identical copy at 6257–6313
is streaming duplication and was ignored).

---

## Meta-finding: the brief was not answered

The assignment said, verbatim: *"propose the TOP 3 paper ideas YOU judge most promising
(**yours may be original — not on any list**)."* What came back is three rows lifted
off existing lists:

- Idea 1 = registry row **Q4** (`docs/research_question_registry.md:42`), analysis plan
  **AP-1**, suite element `q4_l3_shape_grid_v1`, with the holdout cells `(512,256)` and
  `(4096,512)` copied verbatim from `research_question_bank.md:475`.
- Idea 3 = registry row **Q6** (`:44`), plus its C5-2.10 elaboration.
- Both are already **ranked** in the repo's own strategy doc: the impressiveness
  roadmap puts wall-meter at **rank 2** and Q4-held-out at **rank 4**.

Only Idea 2 (prefix-reuse crossover) is a construction rather than a transcription, and
even it sits adjacent to banked riders C5-2.12/C5-2.14. A session invited to originate
returned the repo's own ranked backlog. That is a compliance failure against the
*framing* of the brief, not against the hard existing-material constraint — the work is
honestly grounded, it is just not new information for a 20-direction fan-out.

**Positive counterweight:** the numeric grounding is unusually good. Every diagnostic I
spot-checked reproduces:

| Proposal claim | Repo source | Verdict |
|---|---|---|
| 1.5B prefill 1.65 J @128 | 1.649076 J, `runs_window_a10_20260725/...short-prefill-abs` | ✅ exact |
| 1.5B prefill 51.07 J @4096 | 51.072749 J, a10 prefill-abs, n=10 clean | ✅ exact |
| "49 J diagnostic difference" | 51.073 − 1.649 = 49.42 J | ✅ |
| 12.8 / 25.5 / 51.1 J avoidable prefill @1k/2k/4k | proportional from 51.07 | ✅ arithmetic sound |
| cache load ~0.4 ms | `cacheload_s` 0.000426 s (1024) / 0.000455 s (2048) | ✅ exact |
| save 14–28 ms | `save_s` 0.0136 s (1024) / 0.0276 s (2048) | ✅ exact |
| cache-size prediction within 0.02% | `cache_bytes_pct` 0.0182% (1024), 0.0091% (2048) | ✅ exact |
| exact 64/64 token identity | `tokens_identical: true`, `verdict: replay_supported` | ✅ |
| historical energies 47–200 J | 1.5B decode 50.26 J, 7B 192.39 J (advisor brief) | ✅ |

No fabricated numbers found. Contrast this with the framing looseness below.

---

## Idea 1 — "JouleWise-Q4: Predicting Request Energy from Prompt and Output Shape"

### What is actually being proposed
Freeze AP-1's `4×3` grid (prompt {128,512,2048,4096} × output {64,256,512}), hold out
`(512,256)` and `(4096,512)`, collect **one magnitude/null-ladder window + one grid
window per model = 3 additional quiet windows**, ~120–160 science bundles, fit the
additive categorical model on training cells, evaluate holdouts once.

### The one genuinely good idea in this document
The **magnitude/null-ladder window** is the sharpest thing either open-explore session
produced, and the proposal does not seem to know why. A detection floor in this project
is bound to *"one declared condition family: the same telemetry backend, metric, window
type, **workload profile**, and stack identity"* (`draft-v1.md:60`). Taken literally,
each of 12 (prompt,output) cells per model is a distinct condition family → **24 floor
cells**. D-117 spends **three full windows and ~9.2 h to mint four**. At that exchange
rate a floor-per-cell grid is ~18 windows, and both Q4 proposals in this portfolio are
dead on arrival.

The escape hatch is exactly the null ladder: `draft-v1.md:148` already specifies
*"Null response across magnitudes — identical A=B ABBA blocks at short, medium and long
output magnitudes"* as instrument characterization, currently **[PENDING WINDOW C]**.
That is the empirical license to transport one comparative floor across the grid's
magnitude range. Proposing it as window 1 of the campaign is correct engineering and
folds an unfunded draft placeholder into a funded campaign. **Credit where due.**

### Fatal-flaw candidates

**FF1 — "Prediction" is the wrong word and the title inherits the error.**
The bank's model is **categorical**: `E = fixed + prompt_level + decode_level`. The
holdouts `(512,256)` and `(4096,512)` are unmeasured *combinations of measured levels*.
The study therefore tests **additivity / absence of interaction**, and predicts nothing
outside the grid. "Predicting Request Energy from Prompt and Output Shape" promises a
scaling law it cannot deliver; a referee will call this out in the first paragraph.
Contribution 4 ("labels predictions outside the measured grid unsupported") shows the
author knows — which makes the title a choice, not a slip. **Retitle around additivity.**

**FF2 — Window budget is optimistic against the only calibrated evidence.**
D-117's own budget table (memo §Runtime evidence, `:327`) gets **50 science bundles into
3.14 h** using 1.5B 128-prompt/512-output members at 92.7 s and 7B at ~97 s. The grid's
heavy cells (4096 prompt × 512 output, 7B) are strictly longer than every member those
budgets were built from, and the proposal wants **60 grid bundles per window**. The
proposal's own kill criterion ("dry-run timing cannot fit 60 bundles plus operations and
20% margin") is the right guard, but it is stated as a risk rather than priced — and the
realistic answer is 4–5 windows, not 3. Both Q4 proposals under-book nights; this one
under-books harder because it insists on two models.

**FF3 — Mint machinery is scoped for four cells, not twenty-four.**
D-117 blocker **F2** says the generalized mint is *"decode-only and single-plan/
single-cell"* and needs **pinset v2 + a four-cell aggregate artifact** just to serve
D-117. The Q4 grid needs the same machinery at ~6× the cardinality plus prospectively
frozen acceptance thresholds for every cell before data exists. That desk cost is
invisible in this proposal. It is not fatal, but "three additional quiet windows" is not
the true cost — the true cost is dominated by desk, and the proposal's own
"HARDWARE/VENUE/RISKS" paragraph never says so.

**FF4 — Ambiguity on where model size enters.** 24 cells is 12 per model × 2 models, but
the model is written as `fixed + prompt_level + decode_level` with no model factor. Fit
per-stack (as the repo-sourced sibling proposal does) or add a factor — unspecified, and
it changes both the df budget (10 training cells, 6 parameters, 4 residual df is already
thin) and the floor story.

### Feasibility vs the ~5 J bar and the two gates
Magnitudes are not the problem and are correctly sized. Decode 64→512 at
0.098 J/token (1.5B) → 43.9 J and 0.376 J/token (7B) → 168 J: both ≫ 5 J. The proposal's
"~40 J / ~165 J" is slightly conservative and flagged uncertain — acceptable. Prefill
128→512 ≈ 5 J is genuinely marginal and 128→2048 ≈ 24 J clears. The **residual /
interaction** term is the quantity that may sit under the floor, and the proposal handles
that correctly ("additive at this instrument's resolution, not mathematical exactness").
Gate discipline is honest throughout. **This is a competent instrument-aware design.**

### Venue-fit honesty
Overstated by omission. The roadmap's ICPE-full row requires *"C1–C8, cross-day
stability, artifact-ready release, **and at least one** deeper contribution: held-out Q4
prediction, second-unit replication, or a successful mechanism study."* Q4 is one of
three alternatives for the *last* item, not the ticket. Calling it "the strongest ICPE
full-paper direction" without stating the C8/stability/artifact prerequisites is the
kind of half-truth that gets a proposal funded and then stranded.

### Overlap flags
- **prefill-scaling-laws** — SEVERE. The prompt axis {128…4096} × prefill energy *is*
  that direction's core, and both draw on the same 2026-08-07 sizing desk check.
- **long-generation-dynamics** — MODERATE. Shares the output axis {64,256,512}, though
  that direction is within-request position effects, not cell-level totals.
- **mvp-icpe-upgrade** — SEVERE. The roadmap names Q4 held-out as *the* ICPE upgrade;
  that directed proposal will almost certainly propose this same grid.
- **param-scaling-energy** — MILD. Two-model factor overlaps its 0.5B–14B ladder.
- **kv-context** — MILD, via the 4096-prompt cells.

### Scores
novelty **5** · feasibility **6** · mvp_leverage **9** · venue_fit **8** ·
original_goals **5**

### Verdict: **VIABLE** (strong design, unoriginal selection, under-booked)
Fund the *design* — specifically the null-magnitude-ladder window, which should be
extracted and funded regardless of what happens to Q4, because it discharges
`draft-v1.md`'s [PENDING WINDOW C] rows. Do not fund this as a separate portfolio
direction; it belongs inside `mvp-icpe-upgrade` / `prefill-scaling-laws`.

---

## Idea 2 — "Cache Once, Pay Once? A Calibrated Prefix-Reuse Crossover"

### What is actually being proposed
Promote the July KV spike 3.0.1 (`docs/stream_logs/2026-07-07-kv-spike-301/`,
`verdict: replay_supported`) into claim-grade energy science: cold-prefill vs
cache-assisted request at 1024/2048/4096 prompt tokens, 64 greedy output tokens,
~135 members across 2 windows, solving `E_build+save + k·E_cached < k·E_cold`.

This is the only idea in either open-explore proposal that is not a transcription, and
it mines a real, verified, otherwise-idle repo asset. That earns it a serious read.

### Fatal-flaw candidates

**FF1 (BLOCKER) — the headline crossover is arithmetic, not measurement.**
`E_build` is not a small extra cost; **`E_build` is the prefill itself**. Substituting
`E_build ≈ E_prefill`, `E_save ≈ 0`, `E_cold ≈ E_prefill + E_decode`,
`E_cached ≈ E_decode`, the inequality collapses to
`E_prefill + k·E_decode < k·E_prefill + k·E_decode` → `k > 1`.
The crossover is at **k = 2 by construction**, on any hardware, with no measurement.
The only way the experiment moves that number is if cache load or altered execution
costs something — and the proposal's own evidence says those cost **0.4 ms load and
14–28 ms save**, i.e. ≲0.9 J at ~33 W, an order of magnitude **below the ~1 J
attribution limit** and two below the ~5 J bar. So the single empirically interesting
parameter in the paper is provably unresolvable by this instrument *before collection*.
The proposal half-admits this ("tiny subcomponents may be reported unresolved") without
noticing it has just conceded the thesis. What survives is a real but thin finding:
*"prefix reuse recovers essentially the whole prefill; the overhead is below our
detection floor."* That is one figure and a paragraph, not a paper — unless it is
reframed as a **null/refusal result about cache-overhead invisibility**, which would
actually be publishable in this project's idiom.

**FF2 (BLOCKER, unflagged anywhere) — the cached arm's real cost falls partly OUTSIDE
the named measurement boundary.**
The spike's cache is **58.7 MB** (`cache_bytes_measured: 58725623`). Putting cache load
inside the measured request boundary — which the proposal explicitly requires — means the
cached arm performs a ~59 MB NVMe read that the instrument attributes to the request.
But `draft-v1.md:11` fixes the boundary as *"internal to the named `powermetrics`
system-on-chip boundary"*: SSD controller and NAND energy is **not on the SoC rails**.
The contrast therefore has a **systematic bias in favour of caching** whose size the
instrument cannot see, on a project whose entire thesis is naming your boundary
honestly. Nobody in this proposal, or in its sibling, flags it. This is not
unfixable — it is a limitations paragraph, a `dd`-style desk estimate, or exactly the
case where the borrowed WT310E earns its keep — but shipping it unflagged would be the
worst kind of own-goal for a paper about measurement honesty.

**FF3 — magnitude at the anchor length is marginal, and the proposal's own bar is
wrong.** The kill criterion is "less than ~8 J at 1,024 tokens". But the effective bar
in this project is `floor + claim-side bound` (`draft-v1.md:109–115`), and the *minted*
1.5B decode floor is **7.38 J** (advisor brief). A gross-request floor for a new
condition family will be of that order or larger. 12.8 J projected at 1024 tokens is
~1.7× a 7.4 J floor before the claim-side bound is added — the same marginality profile
as the 128-token prefill contrast that D-117 flagged as marginal at 5.81 J. **The 1024
arm should be presumed unresolvable and the design anchored at 2048/4096** (25.5 / 51.1 J),
which are comfortable. Anchoring the "crossover" story at the length where the
instrument is weakest is the design error.

**FF4 — stack-pin risk.** The spike ran `mlx_lm 0.31.3` / `mlx 0.31.2` on 2026-07-07.
Prompt-cache file format is not a stability-guaranteed surface; a version change between
spike and campaign can silently break replay or, worse, change cache contents while
`tokens_identical` still passes. The proposal's kill criterion covers token identity but
not cache-format identity across the pinned stack. Add a cache-bytes/hash reproduction
check to the desk gate.

### Feasibility, cost, gates
Two windows / ~135 members is plausible at 64-token outputs (cheap members), and this is
the *least* window-hungry idea in either document. Desk cost is real but bounded: new
condition family, cached workload profile, manifest, custody for the cache artifact.
Single-request boundary is genuinely preserved — one request per bundle, no concurrency.
Good discipline.

### Venue-fit honesty
The most honest venue paragraph in either proposal: capstone chapter → ICPE
Emerging/EuroMLSys, "full ICPE becomes plausible". Correctly humble.

### Novelty
Prefix/prompt-cache reuse is thoroughly known in the serving literature (vLLM prefix
caching, SGLang RadixAttention); the novel wrapper is *energy*, *on-device*, *phase-
resolved*, *with a published floor and a refusal for the sub-floor overhead*. That is a
genuine delta, and no directed pool member covers it: `kv-context-energy` is assigned
"decode energy per token as a function of resident context length" — a growth-of-KV
question, not a reuse-economics question. **This is the only genuinely new idea in
either open-explore proposal.**

### Overlap flags
- **kv-context-energy** — PARTIAL (shared KV/cache subject matter, different question).
- **prefill-scaling-laws** — MILD (uses the same 1024/2048/4096 prefill ladder as its
  magnitude source).
- Otherwise clear of the directed pool.

### Scores
novelty **6** · feasibility **6** · mvp_leverage **7** · venue_fit **6** ·
original_goals **7**

### Verdict: **VIABLE** — keep alive, but only after a desk resolution of FF1+FF2
The idea survives only if reframed away from "where is the crossover" (arithmetic)
toward "what does prefix reuse cost that the instrument cannot see" (a boundary and
refusal result), with the off-SoC I/O flaw stated up front and the anchor moved to
2048/4096. In that form it is a legitimate short paper and the closest thing in this
portfolio to Ed's original KV/mechanism axis.

---

## Idea 3 — "Two Boundaries, One Verdict: Validating `powermetrics` Against Wall Power"

### Assessment
Technically the most competent of the three write-ups and the least useful to this
portfolio, because it is a **direct duplicate of the directed
`wall-meter-validation` proposal**, which was commissioned with a sharper brief
("what it adds, what it can never validate"). Funding both is waste; the directed one
should own the axis.

**Genuinely good technical point (worth transplanting into the directed proposal):**
*"The existing ~5 J phase-contrast sizing bar does not automatically govern the external
meter; a new paired meter/synchronization floor does."* Correct, non-obvious, and
exactly the kind of thing a careless version of this paper would get wrong by reusing
the 5 J number out of context. Likewise the discipline that a sub-floor residual licenses
only *"no boundary difference resolved,"* never equivalence.

### Fatal-flaw candidates

**FF1 — the instrument does not exist and its acquisition is not a task anyone owns.**
`TASK_QUEUE.md:327` still lists **P1-003** as `READY [ED-EXTERNAL]` — *record the
wall-meter decision: meter make/model or unavailable verdict*. Not "borrowed", not
"pending": **undecided, and blocked on Ed**. The importer (`P2-048`) is **SHELVED**,
trigger = P1-003. So the whole idea is downstream of a decision that has sat unmade, and
the proposal presents it as a scheduling matter. Its kill criteria are all
*post*-borrow (calibration status, cadence, fixture, sync bound); the *actual* first
kill gate is "does Ed have the unit at all." The roadmap prices this honestly at
**4–8 weeks**; this proposal does not price it at all.

**FF2 — HotCarbon fit is overstated.** The roadmap says plainly: *"HotCarbon needs a
stronger sustainability-metrics argument."* A rail-vs-wall agreement study is a metrology
paper; citing the HotCarbon CFP scope does not make it a sustainability contribution.
EuroMLSys or ICPE is the honest read, which the proposal also gives — so this is
padding, not deception, but a referee notices padding.

**FF3 — the held-out design is under-specified where it matters.** "Reserve one workload
family as the held-out bridge test" across only **four active levels** leaves three
training levels to fit a paired regression with a held-out check. That is not a
regression; it is three points and a hope. Either widen the level set or drop the
held-out framing and call it a paired-agreement study with a stated residual bound.

**FF4 — battery neutralization is named but not solved.** On a MacBook the AC-side
measurement includes charging current. "Battery-charge neutralization" appears as a
requirement in both the kill criteria and the capability list, but the repo has no
mechanism for it, and it is the single most likely reason a first pilot produces
unusable data. It deserved a paragraph, not a noun.

### Feasibility vs the bar
Workload magnitudes (47–200 J) are comfortable. The scientific target — the wall-minus-SoC
residual and any boundary-dependent contrast flip — is explicitly acknowledged as
possibly sub-floor, with correct refusal semantics. Honest.

### Overlap flags
- **wall-meter-validation** — **TOTAL DUPLICATE**. Do not double-fund.
- **floor-methodology-general** — MILD (the new paired-meter floor is a floor-composition
  contribution).

### Scores
novelty **4** · feasibility **3** · mvp_leverage **8** · venue_fit **7** ·
original_goals **3**

### Verdict: **WEAK** — redundant and hardware-blocked
Kill as a portfolio entry; transplant the "new paired floor, not the 5 J bar" point and
the equivalence-refusal language into the directed `wall-meter-validation` proposal.

---

## Cross-cutting

1. **Existing-material compliance: PASS on all three.** Nothing here abandons the
   instrument or invents apparatus without a path. The hard constraint was respected.
2. **Original-goals service: weak overall.** Idea 2 touches the KV/cache axis; Ideas 1
   and 3 admit they serve no mechanism. Nothing here advances spec-decode, MoE, MTP, or
   split inference.
3. **The unmined assets.** For a session told to originate, the repo's most under-used
   claim-grade assets went untouched: the **refusal log** as a corpus, the
   **contamination events** (the 43/50 screensaver-contaminated bundles; the two live
   contamination catches in the 7B window), the **drift/bracket corpus**, and the
   **pulse-train calibration corpus** itself. Idea 2 is the one asset-mining move and it
   is the best thing in the document.
4. **Duplication with the sibling open-explore session.** Ideas 1 and 3 are the same
   ideas as `prop-open-explore-repo.md` #2 and #3. Two independent open-ended sessions
   converging on the repo's own ranked roadmap is informative about the roadmap's
   quality and uninformative about the design space.

2026-08-07T16:52:18.585837Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "sed -n '1,420p' ../portfolio/rev-open-explore-repo.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review — `prop-open-explore-repo.md` (open-ended, repo-asset-sourced)

Reviewer: Opus 5, adversarial counter-review lens (contract + feasibility + novelty).
Ground truth: `scratchpad/desk` @ main; D-117; `2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`;
`2026-08-07-prefill-feasibility/CONSULT-RESPONSE.md`; `2026-08-06-impressiveness-roadmap.md`;
`docs/paper/draft-v1.md`; `docs/advisor_briefs/2026-07-30-advisor-brief.md`;
`TASK_QUEUE.md`; `docs/research_question_bank.md`.

Proposal reviewed: final block, lines 6886–6941 (identical earlier copy at 6828–6885 is
streaming duplication and was ignored).

---

## Meta-finding: the brief was answered backwards

The assignment: *"examine the repository itself — instrument code capabilities, banked
non-claim data, custody machinery, existing diagnostics — and propose 3 papers that the
CURRENT assets make **uniquely cheap or uniquely strong**."*

What came back:

- **#1** = the MVP paper that is already written and already funded. Its "assets" are the
  three D-117 windows that have not been collected yet. Nothing about it is *newly*
  cheap; it is the baseline against which cheapness is measured.
- **#2** = registry row **Q4** / analysis plan **AP-1**, roadmap rank **4**.
- **#3** = registry row **Q6**, roadmap rank **2**, gated on hardware the project does
  not have.

So a session asked "what do your assets uniquely enable" answered with the paper it is
writing plus the top of the strategy backlog. **Zero of the three is asset-discovered.**
The sibling session (`prop-open-explore-registry.md`), which was *not* asked to mine
assets, is the one that surfaced an actual idle asset — the July KV replay spike.

The genuinely un-mined claim-grade assets sitting in this repo, none of which this
proposal mentions: the **refusal-log corpus** as a dataset; the **contamination event
record** (43/50 screensaver-contaminated su-calibration bundles; two live contamination
catches inside the 7B floor window, both recovered per written playbook); the
**pulse-train calibration corpus** itself as a counter-timing dataset independent of
LLMs; the **bracket-drift corpus** and the ~10.82 ms bracket-drift limit; the
**pre-D-078 time-anchor-defective corpora** as a documented instance of a measurement
error class (0.081 J vs 1.649 J for the *same* 128-token prefill workload — a 20× error
caused purely by a time-anchor defect, which is a striking, publishable cautionary
figure that costs zero nights).

**Positive counterweight — factual accuracy is high, and in places better than the
sibling's.** Everything I spot-checked reproduces:

| Proposal claim | Repo source | Verdict |
|---|---|---|
| windows 3.14 / 3.24 / 2.80 h, ≈9.2 h total | DESIGN-MEMO `:327` (sum 9.18) | ✅ exact |
| 50 science bundles per floor window, 40 contrast | Alpha: abs 10 + 10 ABBA blocks ×4 = 50; Gamma: 40 | ✅ exact |
| decode contrast ≈140 J | registered metric `phase_energy_j.decode` 7B−1.5B = 141.29 J | ✅ |
| 7B comparative floor 14.0 J | advisor brief 2026-07-30 | ✅ exact |
| prefill contrast 5.81 J, half-width ≈1.81 J | 5.809930 J; composed half-width 1.808052 J | ✅ exact |
| decode 64→512 ≈45 J (1.5B) / 165–170 J (7B) | 0.098 J/tok ×448 = 43.9; 0.376 ×448 = 168.4 | ✅ best-in-portfolio |
| "no scientific number is presently claim-bearing" | CLAIMS_STATUS + D-117 | ✅ |

One arithmetic understatement: prefill **128→2048 "roughly 19 J"**. From the measured
51.073 J @4096, proportional gives ~25.5 J @2048, minus the 1.65 J base ≈ **23.9 J**.
Flagged uncertain, and conservative in the safe direction, so a nit — but it is the only
number in either document that does not reproduce.

---

## Idea 1 — "When More Repetitions Do Not Help"

### What it is
The MVP paper. Exactly the three D-117 windows, four floor cells, the 7B−1.5B decode
contrast, the refusal machinery. Draft §§1–5 and §8 reused intact; §§6–7 placeholders
filled.

### Assessment
As a *paper*, this is correct, well-scoped, and the right thing to submit. The title is
good — "When More Repetitions Do Not Help" is a better one-line statement of the
attribution-limited finding than anything in `draft-v1.md`, and Ed should consider
stealing it. The kill criterion — *"None short of an unrepaired instrument defect.
Repeated prospective refusals narrow the paper to calibrated non-identifiability; they
do not justify relaxed gates"* — is the single most disciplined sentence in the entire
open-explore pair.

As a *portfolio proposal*, it contributes nothing. There is no decision for Ed to make:
these windows are already the adopted D-117 claim path. A 20-direction fan-out spends a
slot to be told to keep doing what is already funded. And it duplicates three directed
lanes simultaneously.

### Fatal-flaw candidates

**FF1 — no decision content.** Every proposal in this factory is supposed to help Ed
allocate nights and desk time. This one allocates the nights already allocated. Its
marginal information is the title.

**FF2 — contribution 1 is not falsifiable as written.** *"Show whether 59-pulse,
live-bookended calibration contains the observed phase-edge uncertainty in all three
prospective windows."* "Contains" has no threshold here. The repo does have one — the
~10.82 ms bracket-drift screen (`draft-v1.md:54`) — and the contribution should name it.
The brief demanded falsifiable contributions; contributions 2–4 are, 1 is not.

**FF3 — silent on the three D-117 blockers.** The DESIGN-MEMO opens with **F1** (the
ledger cannot reserve both bookend slots under one committed head), **F2** (the
generalized mint is decode-only and single-cell — it *cannot mint the two prefill
riders*), and **F3** (no D-102 successor path for a live-prefixed ledger). All three are
severity `blocker` and all three stand between today and window one. The shared brief
paragraph lists the desk work generically ("two-slot calibration-ledger session,
acceptance-successor machinery, four-cell mint…") but the idea's own "Needs and fit"
paragraph says only *"Owned M3 Max only; no wall meter"* — i.e. the honest answer to
"what does this cost" is **weeks of blocker-clearing desk work**, and the proposal reads
as though the nights are the cost. For the one idea whose entire value is honesty about
cost, that is a real defect.

**FF4 — venue claim drifts.** *"a credible ICPE-full foundation"* — the roadmap is
explicit that ICPE-full additionally needs **C8 (wall validation), cross-day stability,
an artifact-evaluation-quality release, and one deeper contribution**. Idea 1 is
CSCSU + workshop, full stop; the proposal says that too, then adds the ICPE gloss.

### Feasibility vs the bar and the two gates
Impeccable, because it is D-117 as written. Decode contrast ≈141 J against a 14.0 J
comparative floor is ~10×; the ~5 J bar is irrelevantly far away. Prefill riders are
floor cells, not contrasts — correctly, since the 128-token prefill *contrast* is
marginal (5.81 J point, 1.81 J composed half-width → interval 4.00–7.62 J, lower side
under the bar). The proposal explicitly declines that contrast. Correct call, matching
D-117.

### Overlap flags
- **mvp-icpe-upgrade** — SEVERE (this is its baseline; that lane owns the delta).
- **floor-methodology-general** — SEVERE (floors + attribution limit are its whole core).
- **refusal-as-result** — SEVERE (contribution 4 is verbatim that direction).
- **contamination-characterization** — MODERATE (the admission-gate catches).
- **drift-thermal-science** — MILD (drift allowance, bracket screen).

### Scores
novelty **2** · feasibility **9** · mvp_leverage **10** · venue_fit **7** ·
original_goals **2**

### Verdict: **WEAK** as a portfolio entry (excellent as the paper it already is)
Nothing to fund. Harvest the title and the kill-criterion sentence; discard the rest.

---

## Idea 2 — "From Measurements to Workload Energy Budgets"

### What it is
AP-1's `4×3` grid (prompt {128,512,2048,4096} × output {64,256,512}), holdouts
`(512,256)` and `(4096,512)`, n=5 (n=10 near floor), **one stack first, second stack
only if the first passes its holdouts**, ~2–3 additional nights.

### Head-to-head with the sibling proposal's Idea 1 (same idea)
Both sessions independently landed on registry Q4. They differ in exactly two places,
and the comparison is decisive:

| | repo #2 | registry #1 |
|---|---|---|
| Staging | **one stack first, gated on holdout pass** ✅ better | both stacks at once |
| Nights | 2–3 (one stack) — closer to the roadmap's 2–3 | 3 (both stacks) — under-booked |
| Floor transport across the grid | **named as a kill criterion, no mechanism** ❌ | **null/magnitude-ladder window** ✅ better |
| Magnitude estimates | 45 / 165–170 J — exact | ~40 / ~165 J — slightly loose |
| Overselling | "predict held-out single-request energy" | same error, plus in the title |

**The decisive gap is floor transport.** A detection floor here binds to *"one declared
condition family: the same telemetry backend, metric, window type, **workload profile**,
and stack identity"* (`draft-v1.md:60`). Read literally, 12 (prompt,output) cells = 12
condition families = 12 floor cells per stack. D-117 spends **9.2 quiet hours to mint
four**. Repo #2 names this ("if planned cells lack compatible floor transport") and then
proceeds as though 2–3 nights suffices. The sibling proposal has the answer — the
`draft-v1.md:148` **[PENDING WINDOW C]** "null response across magnitudes" ladder is the
empirical license to transport a comparative floor across the grid's magnitude range —
and this proposal does not. **Merge the sibling's ladder into this proposal's staging and
you have the best version of Q4 in the portfolio.**

### Fatal-flaw candidates

**FF1 (shared with the sibling) — "prediction" oversells a categorical additivity test.**
`E = fixed + prompt_level + decode_level` is categorical (per `research_question_bank.md:475`).
Holdouts are unmeasured *combinations of measured levels*. The study tests **absence of
interaction**; it does not predict any workload outside the grid, and cannot. The thesis
sentence — *"can predict held-out single-request energy on one named local-LLM stack"* —
will be read by a referee as a scaling law and then found not to be one. Retitle around
additivity. To its credit, contribution 3 ("identify which workload increments are
resolvable and where attribution prevents coefficient claims") is exactly right.

**FF2 — floor transport unsolved (above).** The blocker.

**FF3 — the desk cost of minting is unpriced.** D-117 blocker **F2**: the generalized
mint is *single-plan/single-cell*, and pinset v2 + a four-cell aggregate artifact is
being built *just for D-117's four cells*. A 12–24-cell grid needs the same machinery at
several times the cardinality, with prospectively frozen acceptance thresholds per cell
before data exists (the D-079 discipline: thresholds hash-sealed eight days before the
data). "New work is campaign-spec generation, AP-1 registry freeze, deterministic
holdout analysis, and figures" understates this by a wide margin.

**FF4 — one-stack staging weakens the paper it is trying to strengthen.** Gating the
second stack on the first's holdout pass is good risk management and bad science
communication: a single-stack additivity result on one 1.5B model is a much thinner ICPE
contribution than a two-stack result, and the roadmap's rank-4 entry assumes the full
designed matrix (*"Fund the full designed matrix or omit the predictive claim; do not
replace it with opportunistic workload breadth"*). The staging must therefore be framed
as *sequencing*, with both stacks committed — not as an option to stop at one.

### Feasibility vs the ~5 J bar and the two gates
Effect sizing is the best in the portfolio. Decode 64→512: 43.9 J (1.5B), 168 J (7B) —
both ≫ bar, both derived correctly from 0.098 / 0.376 J-per-token. Prefill 128→512 ≈
4–5 J, correctly flagged *may not clear*; 128→2048 ~24 J (proposal says 19 J,
understated but conservative), clears. The **residual/interaction** term is the one that
may sit under the floor, correctly handled: *"a holdout miss means the additive model is
rejected — not patched with an interaction after inspection."* That single sentence is
the pre-registration discipline this project exists to demonstrate, and it is the
strongest reason to fund some version of Q4.

Single-request boundary: preserved. No wall meter. No new hardware. Existing runtime,
suite, reducer, ABBA, custody, analysis-registry all reused — the "uniquely cheap"
argument is genuinely true *here*, if nowhere else in this document.

### Venue-fit honesty
*"Capstone second chapter, then ICPE full research"* — defensible and matches the
roadmap's rank-4 rationale, provided the C8/stability/artifact prerequisites are stated.
They are not. Same omission as the sibling.

### Overlap flags
- **prefill-scaling-laws** — SEVERE (prompt axis is that direction's core).
- **long-generation-dynamics** — MODERATE (output axis; different question — position
  effects vs cell totals).
- **mvp-icpe-upgrade** — SEVERE (roadmap names Q4 held-out as *the* ICPE upgrade).
- **param-scaling-energy** — MILD (two-stack factor).
- **`prop-open-explore-registry.md` #1** — **NEAR-TOTAL DUPLICATE**. Merge, do not fund
  twice.

### Scores
novelty **5** · feasibility **6** · mvp_leverage **9** · venue_fit **8** ·
original_goals **5**

### Verdict: **VIABLE** — the best-staged version of a well-known backlog item
Fund the *merged* Q4 (this proposal's staging + the sibling's null-magnitude ladder),
inside `mvp-icpe-upgrade` / `prefill-scaling-laws`, not as a standalone direction.

---

## Idea 3 — "Do SoC-Rail and Wall-Power Measurements Support the Same Conclusion?"

### Assessment
A duplicate of the directed **`wall-meter-validation`** proposal *and* of the sibling
session's Idea 3. Three slots in one factory spent on one axis. The directed lane, which
was briefed specifically on *"what it adds, what it can never validate (phase split)"*,
should own it.

Best line in the write-up, and a real contribution: contribution 4, *"empirically
separate total-scale validation from phase-attribution validation,"* with the thesis
stating up front that external AC measurement *"remain[s] explicitly unable to validate
the prefill/decode split."* That is precisely what `draft-v1.md:56` says the pulse
calibration validates and the wall meter cannot (*"only an external meter could
additionally validate the absolute whole-system scale"* — scale, not attribution). The
proposal gets this right where a careless version would claim the meter validates the
phase split. Transplant it.

### Fatal-flaw candidates

**FF1 (BLOCKER) — the instrument is not merely unowned, its acquisition decision is
unmade and Ed-blocked.** `TASK_QUEUE.md:327`: **P1-003**, status `READY [ED-EXTERNAL]` —
*"Record the wall-meter decision: meter make/model or unavailable verdict."* The
importer, `P2-048`, is `SHELVED — trigger: P1-003`. The kill criterion here is entirely
*post*-borrow (calibration status, cadence, uncertainty, clock bound, battery
neutralization) and never states the *first* gate: does the unit exist and is a loan
agreed. The roadmap prices the path at **4–8 weeks**; the proposal gives no calendar at
all. A proposal whose critical path runs through an unmade external decision must lead
with that, not bury it.

**FF2 — battery neutralization is named four times and solved zero times.** On a
MacBook the AC-side reading includes charging current, which can dwarf the residual
being measured. The repo has no mechanism. This is the single most likely cause of an
unusable first pilot, and it gets a noun.

**FF3 — sizing is inside-out.** *"The model-size effect should exceed 100 J … the
absolute wall-minus-SoC gap is probably tens of joules."* Both are true and both are
the easy parts. The scientifically interesting quantity is the **load-dependent
boundary bias** — whether the SoC-to-wall ratio changes between compute-heavy and
long-context conditions — and the proposal concedes that *"boundary-interaction effects
may be below 5 J."* So, as with the sibling's cache proposal, the headline question may
be unresolvable while the easy questions clear. It handles the refusal semantics
correctly (*"no flip resolvable, not boundary equivalence"*), but the design should be
**powered for the interaction**, not for the model-size effect that is already known to
be ~141 J. No power argument is offered.

**FF4 — two windows is optimistic for a first-contact instrument.** One pilot plus one
confirmatory, with a bespoke synchronization bridge, a new floor class, dual-stream
custody, and an inline AC fixture, all on hardware nobody in this project has used
before. The roadmap says the confirmatory run may share a later frozen campaign *"only
after the importer and protocol pass independently"* — i.e. more than two sessions.

### Feasibility vs the bar and the two gates
Correctly notes (as does the sibling) that the ~5 J phase-contrast bar does not govern an
external meter and a new paired meter/synchronization floor is required. Good. Refusal
semantics correct. Existing-material compliance: acceptable — the WT310E is explicitly
permitted by the brief and P2-048's bridge design already exists.

### Overlap flags
- **wall-meter-validation** — **TOTAL DUPLICATE**.
- **`prop-open-explore-registry.md` #3** — **TOTAL DUPLICATE**.
- **floor-methodology-general** — MILD (the new paired-meter floor class).

### Scores
novelty **4** · feasibility **3** · mvp_leverage **8** · venue_fit **7** ·
original_goals **3**

### Verdict: **WEAK** — redundant and blocked on an unmade external decision
Kill as a portfolio entry. Transplant contribution 4's scale-vs-attribution distinction
into the directed `wall-meter-validation` proposal.

---

## Cross-cutting

1. **Existing-material compliance: PASS on all three.** Nothing abandons the instrument;
   nothing invents apparatus without a path. The hard constraint was respected, and the
   shared brief paragraph is the most accurate project restatement in either document.
2. **Asset-mining: FAIL against the assignment.** The brief asked what the *current
   assets* uniquely enable. All three answers came from the strategy roadmap and the
   registry, not from the repository. The refusal log, the contamination record, the
   pulse-train corpus, the bracket-drift corpus, and the pre-D-078 time-anchor defect
   (0.081 J vs 1.649 J on identical workloads — a 20× error from a pure timing defect,
   available at zero night cost) were all left on the floor.
3. **Original-goals service: essentially nil.** All three write-ups concede they serve no
   mechanism axis. Idea 2 claims to serve "modular-harness, workload-swappability,
   split-budgeting" — of these only workload-swappability is real; nothing here builds
   toward spec-decode, MoE, MTP, KDA, or split inference.
4. **Numeric discipline: the best of the two open-explore sessions.** Every claim-bearing
   number reproduced from primary evidence except the 128→2048 prefill estimate (19 J vs
   ~24 J), and uncertain quantities carry explicit `[uncertain]` / `[linear estimates]`
   labels. Whatever else is wrong here, it is not fabrication.

2026-08-07T16:52:21.264161Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "sed -n '1,390p' ../portfolio/rev-param-scaling-energy.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review — `prop-param-scaling-energy.md`

**Reviewer:** Opus 5, adversarial counter-review. Ground truth: desk checkout at `89f28bf`
(main), D-117 at end of `docs/decision_log.md`, `docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`,
`docs/contracts/token_normalization.md`, `docs/research_question_registry.md`,
`CLAIMS_STATUS.md`, `docs/run_reports/2026-07-30-sweep-mechanisms.md`, and the local
model artifacts under `/Users/edr/jw_models/mlx-community/`.

**VERDICT: WEAK** (borderline KILL as scoped; a 1-night shrink is the only fundable residue)

| axis | score |
|---|---|
| novelty | 2 / 10 |
| feasibility | 7 / 10 |
| mvp_leverage | 5 / 10 |
| venue_fit | 4 / 10 |
| original_goals | 3 / 10 |

---

## What the proposal gets right (credit before the knife)

The reading is real, not hallucinated. I verified against primary sources:

- Historical anchors are correct: `docs/run_reports/2026-07-30-sweep-mechanisms.md` records
  7B-4bit decode = 0.376 J/tok and 1.5B = 0.098 J/tok → 192.5 J and 50.2 J at 512 tokens,
  matching `CLAIMS_STATUS.md`'s 192.386233 J absolute-cell member mean. The registered ABBA
  claim metric is indeed `phase_energy_j.decode`, 7B−1.5B = **141.29 J per block**, and the
  proposal correctly does *not* quote the 146.730349 J idle-subtracted diagnostic that
  sweep DC-1 quarantined. Good discipline.
- The two-anchor projection arithmetic is reproducible: slope 25.84 J/B, intercept 11.5 J →
  24 / 50 / 90 / 192 / 371 J. Correct.
- The registry cap is honestly acknowledged. `C5-1.1` is `candidate`, `claim_ceiling` = "L2
  pairwise only unless larger predeclared model set", `forbidden_upgrade` = "no
  active+total+KV regression on 4-6 models". The proposal explicitly refuses the
  scaling-law framing. Correct, and rarer than it should be.
- n=5 blocks for the dual-contrast window is **conformant**, not a deviation:
  `docs/contracts/analysis_plans.md` line 121 records D-062 as "n=10 for near-floor
  cells/contrasts, n=5 elsewhere". At 66 J and 281 J these are not near-floor. I had this
  queued as an attack and it does not land.
- Holm machinery exists (`joulewise/analysis_engine/multiplicity.py`, `holm_adjust`,
  `tests/test_analysis_multiplicity.py`). Not a new build.
- Artifact availability checks out: `Qwen2.5-0.5B-Instruct-4bit`, `-1.5B-`, `-7B-` are
  present locally; 3B and 14B are absent and must be fetched (~1.7 GB and ~8.3 GB — trivial).
- Single-request boundary is genuinely preserved. No violation.

That is where the good news stops.

---

## FATAL FLAW 1 — Contribution 3's normalization is not well-posed, and its only substantive observation is a denominator artifact

The proposal's headline normalization is

> `phase J / (runtime-observed phase tokens × published non-embedding parameters)`, in
> "pJ per non-embedding-parameter-forward", with 1.5B → ~75 pJ and 7B → ~58 pJ,
> "suggesting the normalization may decrease with size".

I checked the actual artifacts. **Three of the five ladder rungs use tied word embeddings
and two do not.** Verified directly from local `config.json`:

| model | `tie_word_embeddings` | `vocab_size` | `hidden_size` | head params read per decode token |
|---|---|---:|---:|---:|
| 0.5B | **True** (verified) | 151936 | 896 | 136.1 M |
| 1.5B | **True** (verified) | 151936 | 1536 | 233.4 M |
| 3B | True (inferred) | 151936 | 2048 | 311.2 M |
| 7B | **False** (verified) | **152064** | 3584 | 545.0 M |
| 14B | False (inferred) | **152064** | 5120 | 778.6 M |

The 3B/14B inferences are arithmetic-tight, not guesses: the published total-minus-non-embedding
gaps are 0.32 B (= 151936 × 2048 exactly, one matrix → tied) and 1.6 B (= 2 × 152064 × 5120,
two matrices → untied). Same check reproduces 0.5B/1.5B/7B against their verified configs.

The consequence is fatal. For a tied model, **the embedding matrix *is* the LM head and is
read on every decode token.** For an untied model there is a separate output head, also read
every token. "Non-embedding parameters" excludes this per-token traffic in every case. The
excluded fraction is:

> 38 % (0.5B) → 17.8 % (1.5B) → 11.2 % (3B) → 8.3 % (7B) → 5.9 % (14B)

— a monotone decline **along exactly the axis being studied**. The denominator's error is
correlated with the independent variable. Recomputing the two anchors with the head included:

| anchor | proposal (non-embedding) | with per-token head read |
|---|---:|---:|
| 1.5B | 74.9 pJ | 63.6 pJ |
| 7B | 57.5 pJ | 53.1 pJ |
| **decline** | **−23.3 %** | **−16.5 %** |

**Roughly 29 % of the reported "decrease with size" is manufactured by the denominator
choice.** Contribution 3 has exactly one substantive observation and it is not robust to a
defensible alternative definition of the same quantity. Rivoire will find this; JouleSort's
whole point is that the denominator is the claim.

Three further well-posedness objections, any one of which is sufficient on its own:

1. **The ladder spans two tokenizer identities, not one.** `vocab_size` is 151936 for
   0.5B/1.5B/3B and **152064** for 7B/14B — verified from the local 7B config.
   `docs/contracts/token_normalization.md` defines tokenizer identity as "name, revision,
   class, and vocabulary size" and C-023 compares all three strings plus
   `tokenizer_artifact_sha256`. So the five-point per-token normalization is a
   **cross-tokenizer comparison**, and the contract's "Cross-Tokenizer And
   Cross-Model-Family Comparisons" clause fires: it must either carry a tokenizer-independent
   companion denominator (J/char, J/byte) or "avoid efficiency-ranking language entirely and
   remain descriptive". The proposal's desk list contains a "tokenizer/prompt-token identity
   audit", but the audit is scoped to *prompt-token identity* (which will almost certainly
   pass — the extra 128 ids are reserved specials appended at the tail) and not to *tokenizer
   identity* (which will fail). The proposal writes contribution 3 as if the family is one
   tokenizer scope. It is not.
2. **The unit name does the work the registry forbids.** "pJ per parameter-forward" is a
   work-unit name asserting an operation count. `RQ-METHOD-FLOOR`'s `forbidden_upgrade` is
   literally "no module-energy fraction or regression-slope attribution", and
   `token_normalization.md` §"J/Token As Tokenizer-Scoped Companion Metrics" says per-token
   denominators "are not tokenizer-blind work units". The proposal's inline hedge ("not
   direct energy attribution or an operation count") does not survive the unit appearing in a
   figure axis label. Also, `token_normalization.md` requires gross request energy to be
   "co-displayed with equal or greater salience" wherever a token-normalized metric appears —
   the proposal never says it will do this.
3. **The same normalization is applied to two physically different phases.** Decode is
   bandwidth-bound (energy ∝ bytes read per token); prefill at 128 tokens is compute-bound
   with an O(n²) attention term. Calling both "pJ per parameter-forward" asserts that
   parameter-forwards are the common cost driver in both. They are not. A single unit spanning
   both phases is not well-posed even before the denominator problem.

**Verdict on contribution 3: not salvageable in its current form.** Either delete it or
rebuild the denominator as *measured bytes read per decode token from the actual quantized
artifact* — which is custodiable (artifact SHA is already pinned), phase-appropriate, and
robust. Note the artifacts are `bits: 4, group_size: 64, affine` for every rung, so
scales/zeros add ~0.5 effective bits/weight uniformly; that cancels in trend but means a
"per-parameter" figure is really a per-(parameter + quantization overhead) figure.

---

## FATAL FLAW 2 — The instrument is irrelevant to every claim that will actually resolve

This is the deeper problem, and it is a novelty problem masquerading as a design problem.

The projected decode contrasts are **66 J** (0.5B→3B) and **281 J** (3B→14B) against a
practical bar the proposal quotes as ~5 J. That is 13× and 56× clearance. `CLAIMS_STATUS.md`
records the largest actually-measured comparative floor on this instrument as
**13.998036715259254 J** (7B decode, `window_7bfloor_20260729`); even against that the
clearance is 5× and 20×.

An effect at 20–56× the detection floor **does not need this instrument.** It does not need
in-window bracketed pulse-train calibration, worst-case timing attribution, a never-zero
drift allowance, ABBA counterbalancing, hash-bound custody, or a two-gate claim regime. It
needs a wall socket and a stopwatch. The entire scientific spine that the MVP paper
(`docs/paper/draft-v1.md`, whose title is *"Detection Floors for LLM Inference Energy
Measurement on Consumer Silicon"*) exists to establish is, in this paper, load-bearing for
nothing.

And the finding itself is foreknown. There is no open question in the literature about
whether a 14B model uses more decode energy than a 0.5B model on a bandwidth-bound
accelerator. Contribution 1's stated falsification condition — "measurements do not form the
projected ordering" — is not a real risk; it is a monotone curve everyone can predict from
`bytes_read × 512`. Compare the repo's own `docs/run_reports/2026-07-30-sweep-mechanisms.md`,
which ranks six reachable mechanism claims and puts **spec decode on/off** at rank 2 with an
explicitly *open sign* in the literature ("mlx overhead could plausibly flip it"; "Batch-1
on-device … has *no published energy measurement anywhere I found*"). Parameter scaling is
not in that ranking at all, and the sweep's top-3 recommended first campaigns do not include
it. The repo has already adjudicated this direction's relative value and the proposal did not
engage with that adjudication.

The only genuinely instrument-dependent content in the entire proposal is **contribution 4,
the prefill refusal** — the one place where the effect is near the floor and the two gates
actually decide something. That is one bit of information, and D-117's floor riders plus the
already-custodied 128-token prefill feasibility finding deliver most of it for free.

---

## FLAW 3 — The kill criterion is set *below* the largest measured floor

> "desk diagnostics project the smallest registered decode contrast below **10 J** — a
> conservative 2× sizing buffer."

10 J is **less than** the 13.998 J comparative floor already measured for the 7B decode cell.
A gate that passes an effect smaller than the instrument's own largest measured floor is not
a "conservative 2× buffer"; it is a gate that cannot fail for any reason that matters. This
is a symptom of anchoring on the "≈5 J" prose constant in `CLAIMS_STATUS.md` line 55 rather
than on the measured floor values eight lines below it in the same file. The proposal should
express every sizing threshold as a multiple of the *projected floor for that cell*, not of a
document-level constant.

Related and unaddressed: **the prefill floors do not exist yet.** They are precisely what
D-117's riders will mint. Every prefill effect-size statement in the proposal (0.6 / 1.6 /
3.3 / 7.6 / 15 J, contrasts of 2.7 / 6.0 / 11.7 J) is compared against a bar that has never
been measured for that phase. The proposal's claim that 3B→14B prefill "might clear" is
therefore unfalsifiable desk speculation, and its framing of a "mixed outcome … more
informative than lengthening prompts" is a rhetorical rescue of what may well be a uniform
refusal across all three prefill contrasts.

---

## FLAW 4 — The "two free points" are not free, and the window arithmetic hides the real cost

**On the free points.** The proposal treats D-117's alpha/beta windows as delivering the 1.5B
and 7B rungs of contribution 1 ("report gross prefill and decode joules for … 0.5B/1.5B/3B/
7B/14B"). They do not, as frozen. Per the design memo, alpha/beta pre-register four cells —
decode absolute, decode comparative, prefill absolute, prefill comparative — all of which are
*floor* cells. A reported mean phase energy is a different estimand, and the memo is explicit:
*"Post hoc extraction without a pre-registered cell is also insufficient."* The
absolute-cell member mean (e.g. 192.386233 J for 7B) is quoted in `CLAIMS_STATUS.md` only
with the standing warning **"always name the cell"**, and the whole point of D-117 is that
pre-genesis values are diagnostic-only.

So contribution 1 requires **amending the alpha and beta campaign packs to pre-register a
reported-energy cell**. That is possible today — U5/U6 are unbuilt work orders — and
impossible after desk freeze, because it changes plan SHAs, extraction specs, and the
four-cell mint. The proposal never mentions this dependency. It is also a rule-11
freeze-amendment, i.e. a magistrate/cold-gate decision, not a lieutenant's.

**On the nights.** The "seven quiet nights / 21–23 quiet-machine hours" figure is arithmetically
honest — I re-derived it and the 14B window does *not* blow the 4 h envelope, because member
time is dominated by fixed overhead (1.5B decode member = 92.7 s, 7B ≈ 97 s per the design
memo's §4 evidence, for compute of ~1.2 s and ~5.4 s respectively; 14B adds ~5 s → ~102 s).
I had "14B blows the budget" queued as an attack and it does not land. Credit where due.

But nights are not the cost driver, and the proposal counts the cheap resource. The real cost
is the desk program. D-117's **three** windows required a 489-line design memo, **ten**
enumerated WRITE_SCOPE work orders (U1–U10), **three** toolchain blockers (ledger bracket
sessions, D-102 successor engine, pinset v2 multi-cell mint), and a synthetic three-window
live-ledger regression with ~15 required refusal vectors — and none of it has landed yet.
This proposal adds four more windows, each needing a U5/U6-class campaign pack, extraction
spec, condition families, order manifests, and plan-readiness tests; expands the mint from
**4 cells to 10**; adds two new registered hypotheses with multiplicity control; and
introduces two new stack identities into the custody chain. Then there is the serialization
tax the proposal ignores entirely: `[QUIET-MAC]` forbids running an agent session during a
measurement window, so every additional night is a night the desk program cannot advance.

Set against `paper-first-priority-stack` (P1 = MVP paper; P3 sacrificed if it costs P1/P2),
this is a P3-flavoured extension that materially delays P1 to buy a curve nobody disputes.

---

## FLAW 5 — Governance and title exposure

- **No registry promotion path is stated.** `C5-1.1` is `status: candidate`. The registry's
  own promotion rule requires "a named RQ slot in `PROJECT_STATUS.md`, a data plan that does
  not displace queue ranks above it, and scope fit". This proposal displaces the rank
  directly above it (D-117 closure). Unmentioned.
- **The title and thesis do the forbidden work.** "Calibrated Parameter **Scaling** on Apple
  Silicon" plus a thesis asserting "a large, resolvable association with parameter count"
  across five points is exactly the wording `C5-1.1`'s `forbidden_upgrade` and the C-014
  amendment were written to prevent, even though the body correctly disclaims a scaling law.
  Reviewers read titles. `RQ-TWO-MODEL-ACTIVE-NONCLAIM` exists in the registry precisely
  because this project has been here before.
- **Contribution 4 has no specified data source.** D-117 gamma is decode-only *by ratified
  decision* (D-117 cl.3), and the design memo rejected attaching prefill to it. The
  proposal's dual-contrast window would need prefill riders, and the memo warns the 128-prompt
  riders "do not automatically transport" without an exact matching floor cell or a
  "separately predeclared and justified transport rule". Contribution 4 is currently a claim
  with no floor.

---

## Where I tried to kill it and failed

Recorded for honesty, because a referee who only lists hits is not calibrated:

1. **"14B will swap/throttle/blow the 4 h window."** No. 68 GB is the 122B artifact's peak;
   14B-4bit is ~8.3 GB on a 128 GB machine, and member time is overhead-dominated.
2. **"n=5 blocks is an unproven deviation from the 10-block template."** No — D-062 sets
   n=5 as the default for non-near-floor contrasts. Conformant.
3. **"Holm correction is new machinery."** No — `holm_adjust` ships with tests.
4. **"The hour budget is optimistic."** No — 21–23 h reconciles with the memo's 3.14 / 3.24 /
   2.80 h per D-117 window plus four comparable extensions.
5. **"It abandons the instrument / needs unowned apparatus."** No. Existing-material
   compliance is *clean*: owned hardware, no wall-meter dependency, same discipline, single-request
   boundary preserved. This is the proposal's strongest suit and it is genuinely strong.

---

## Three strengthening moves

1. **Delete or rebuild contribution 3.** As written it is a cross-tokenizer normalization
   presented as within-family, named as a work unit the registry forbids, applied across two
   phases with different physics, and its only trend is ~29 % denominator artifact. If Ed
   wants a normalization, make it **measured bytes read per decode token from the pinned
   quantized artifact** (weights actually traversed, including the tied-or-untied head and
   the group-64 affine scales, plus a separately reported KV term). That denominator is
   custodiable, phase-honest, physically motivated, and it turns the *gap* between
   bytes-predicted and measured joules into an actual finding rather than a restatement.
   Publish the 75/58-vs-64/53 sensitivity table as evidence of denominator discipline —
   that is a real, Rivoire-shaped methodological contribution and it costs zero nights.

2. **Cut four extension nights to one: 14B only.** Drop 0.5B and 3B. They buy interpolated
   points on a curve whose shape is already determined by the two D-117 anchors, and their
   prefill contrasts are projected to refuse anyway. 14B is the only rung that adds anything:
   it is the sole prefill contrast that might clear a floor, it is the top of the servable
   dense ladder, and it extends the projection range 2× rather than interpolating inside it.
   One floor window + one 1.5B/7B-anchored contrast at n=10 is ~6.5 h across two nights; if
   the budget is truly one night, take the floor window and reuse gamma's contrast basis.
   Reframe the paper as a **§7 enrichment of the MVP** — three dense rungs plus a phase-specific
   refusal — not a standalone family study.

3. **Amend the D-117 alpha/beta packs *now*, before U5/U6 freeze, to pre-register a
   reported-phase-energy cell alongside the four floor cells.** This is the single highest-leverage
   move in the whole proposal and it is time-critical: after desk freeze the plan SHAs are
   immutable and the 1.5B/7B points become a fresh-window purchase instead of a free rider.
   Route it as a rule-11 cold-gate item (it amends a ratified freeze), attach it to U5/U6's
   WRITE_SCOPE, and state explicitly that the added cell changes no member, no runtime, and
   no floor derivation — the same argument that justified the prefill riders.

---

## Bottom line

Existing-material compliance: **clean**. Instrument discipline: **preserved**. Arithmetic:
**mostly checkable and mostly correct**. And the paper still should not be funded as scoped,
because it spends four scarce quiet nights and a D-117-sized desk program to measure a curve
whose shape is a foregone conclusion at 20–56× the detection floor — using an instrument
whose entire reason for existing is to adjudicate effects near the floor. The one thing it
proposes that the instrument is actually needed for, the prefill refusal, is nearly free.
Take that, take 14B, and give the other three nights to the mechanism axis where the sign is
genuinely open.

2026-08-07T16:52:25.110624Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "sed -n '1,390p' ../portfolio/rev-prefill-scaling-laws.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review: "Detectability-Aware Prefill Energy Scaling on Apple Silicon"

Reviewer: Opus 5 counter-reviewer (adversarial charge: try to kill it).
Ground truth: desk checkout at `89f28bf`; D-117 (end of `docs/decision_log.md`);
`docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`;
`docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md`;
`docs/paper/draft-v1.md`; `CLAIMS_STATUS.md`; `docs/research_question_registry.md`.

**VERDICT: WEAK.** The underlying physics is the most favourable in the portfolio —
prefill length contrasts have effect/magnitude ≈ 1, so they clear the bar by ~10×
rather than by ~1.5×. Everything built on top of that physics is wrong: the cost is
understated by 2–4×, the floor-transport rule is anti-conservative on its dominant
component, three of the four length points have no admissible floor of any kind, the
headline falsifiable test is constructed so it cannot fail, and three of five
contributions already belong to the MVP paper. Kill it *as framed*; it survives only
as a one-night rider on the D-117 fourth-window option.

---

## 1. Feasibility vs the bar and the two claim gates

### 1.1 What is right (and it matters)

The effect sizing is the proposal's one genuine strength and I could not break it.
D-078 cl.11's attribution term is ~duration-independent (~30 ms edge × ~33 W), while
prefill energy is ~linear in prompt tokens. The SYNTHESIS diagnostic (1.5B prefill
predicts 128→4096 within ~3.3%) supports ~0.0125 J/prompt-token for 1.5B. So
128→1024 ≈ 11 J and 128→4096 ≈ 49 J against a ~5 J practical bar. Critically, a
prompt-length contrast is a contrast between two *magnitudes*, not a perturbation on
a shared baseline: the effect is nearly the whole of the larger arm. Under any floor
model — absolute or proportional — effect/floor is roughly 10–13×. This is the only
proposal I have reviewed where gate 1 (floor clearance) is not in doubt.

That is also why it is not a paper. See §3.

### 1.2 Fatal flaw A — the floor-transport rule is anti-conservative on repeatability

The proposal's transport rule is: "maximum of both 128-token floors, long-end null
behavior, all observed member attribution widths, and window drift allowances."

Draft §4 composes the floor as `F_cell = max(F_abs, F_cmp)`, where

- `F_abs = max(max_i |r_i|, t·s_r·sqrt(1+1/n))` — **repeatability, scales with the
  magnitude of the measured quantity**;
- the corner-widened attribution term — **~duration-independent** (this is the whole
  content of the attribution-limited finding);
- `A_drift` — measured per window, explicitly **no duration-scaling law applied**.

The proposal's transport rule silently assumes all three components are
duration-independent. Two are; the first is not. Prefill energy at 4096 tokens is
~32× that at 128 tokens (1.5B). If the coefficient of variation is even roughly
stable, `s_r` in absolute joules grows by the same factor. Taking `max(128-token
floors)` as the absolute component at 4096 is therefore anti-conservative by
something like an order of magnitude. This is not a nit: it is the exact failure
mode draft §8 says the project refuses ("Root-sum-square composition would be
anti-conservative for a systematic edge-placement bound" — same epistemic error,
opposite direction).

The DESIGN-MEMO forbids exactly this shape of reasoning twice:

- §"Prefill floor claim eligibility": "For each metric, the operative floor is the
  maximum of independently evaluated absolute and comparative components. … Never
  sum components and **never borrow a decode floor for prefill**."
- §"Optional 256-token prefill contrast": "The floor riders here use the prefill
  phase of the 128-prompt decode workload. They **do not automatically transport to
  a prospectively defined 256-token contrast**. The fourth plan needs either exact
  matching prefill floor cells or a separately predeclared and justified transport
  rule."

If a 128→**256** transport is not automatic, a 128→**4096** transport built on a
component that provably grows with magnitude is not defensible at all.

### 1.3 Fatal flaw B — three of four length points have no floor evidence whatsoever

Count what the plan actually collects. S1 = 256 and 1024 tokens, five cross-model
ABBA blocks per length = 40 members total, **zero absolute members, zero A=A null
blocks**. S2 = five cross-model ABBA blocks at 4096 (20 members) + five 4096-token
A=A null blocks per model (40 members) = 60.

So:

| Length | Absolute floor component | Comparative floor component |
|---|---|---|
| 256 | none | none |
| 1024 | none | none |
| 4096 | none | 5 blocks/model (half the D-117 design) |

D-117 gamma's floor rule is `cross_stack_armwise_max.v1`: independently resolve the
1.5B and 7B cells and take their maximum. A cross-model contrast at length L
therefore needs *two* floor cells at length L. The plan supplies zero at two of
three new lengths and a half-strength comparative-only cell at the third. Every
claim in Contributions 2 and 3 rests entirely on the unratified transport rule of
§1.2. If the metrology review rejects it — and the memo's own language says it
should — **both extension nights produce nothing claim-bearing.**

### 1.4 Fatal flaw C — the design under-powers precisely the cells it calls refusals

The proposal drops from D-117's ten ABBA blocks (n=10) to **five** (n=5) for every
contrast. Gate 2 is interval-supported direction, and the interval half-width scales
as ~1/sqrt(n): the SYNTHESIS's composed contrast half-width of ~1.81 J at n=10
becomes ~2.6 J at n=5. The repo's own D-062 rule (visible in the seeded AP-1/AP-2
plan rows) is "n=10 for near-floor cells/contrasts, n=5 elsewhere."

The proposal then designates 128→256 within 1.5B (~1.6 J projected — definitionally
near-floor) as a *deliberate refusal* and gives it **n=5**. A refusal produced by a
design the project's own sizing rule says was under-powered is not evidence about
the instrument; it is evidence about the manifest. Contribution 5 ("published
refusal boundaries … distinguishing measurement incapacity from equality") is
directly undermined: you cannot distinguish incapacity from under-powering when you
chose the under-powering.

### 1.5 Fatal flaw D — the headline falsifiable test cannot fail

Contribution 2 is the paper's flagship: fit a pre-registered linear-in-length model
and predict a held-out cell. The proposal states "The linear model is trained on
128, 256, and 4096; 1024 is held out."

- Three training points, two free parameters → **1 degree of freedom**.
- 1024 lies *between* 256 and 4096 → this is **interpolation**, not extrapolation.
- The prediction envelope is "guarded" by floors, i.e. widened by the same
  conservative machinery that makes floors large.

A 1-df linear interpolation to a mid-range point, judged against a
deliberately-conservative envelope, passes essentially by construction. The registry
already says so: seeded plan AP-1's "Holdout cells (L3 only)" row reads "both factor
levels occur in the training grid, so neither is statistical extrapolation. **No
extrapolation claim is available from this grid.**"

### 1.6 True cost — understated by 2–4×

Reconstruct the window budget from the DESIGN-MEMO's own alpha column. Fixed
per-window operational overhead: pre-cal 8 + 12 NEG8 members 22 + bound eval 1 +
start refs 8 + midpoint 5 + end refs 8 + post-cal 8 + untouched idle 10 = **70 min**
before any science. Science rates: ~1.9 min/member (absolute stage), ~1.7 min/member
(ABBA stage) for 1.5B; ~1.8–2.0 for 7B. The 4 h ceiling with the mandatory 20%
margin gives base occupancy ≤ 200 min → science ≤ ~130 min → **≈ 65–75 science
members per window**, before long-prompt prefill inflates per-member time.

Now price the plan honestly:

- **Minimum defensible version** (one long-endpoint floor pair per model, transported
  downward under a ratified monotone envelope): 1.5B floor window (10 abs + 40 null
  = 50 members) + 7B floor window (50) + contrast window(s) (40–60). **4 extra
  nights**, not 2.
- **Fully compliant version** (own floor cells per length per model, as the memo's
  "exact matching prefill floor cells" branch requires): 3 new lengths × 2 models ×
  50 members = 300 members ≈ 5 nights of floors alone, plus ~2.5 nights of contrasts.
  **≈ 7–8 extra nights.**

The proposal says two. Its own contingency clause ("fund a third extension night
with ten-block long-prompt floors") already concedes the direction of the error but
under-counts it, because a ten-block long-prompt floor is needed *per model*.

### 1.7 Cost error shared with the whole portfolio: the MVP is not 3 nights

The proposal asserts "the complete paper therefore costs **five quiet windows from
today**: the three already authorized plus two." That is false on the repo's own
draft. `docs/paper/draft-v1.md` §6 (contribution C-iv, "full instrument
characterization") has **all six rows marked `[PENDING WINDOW C]`** — linearity, null
response across magnitudes, empirical floor verification, phase-attribution causal
consistency, drift/settling, between-session stability. D-117 cl.4 explicitly places
the MET-WINDOW-C-01 campaign *after* the three-window closure. The MVP paper as
drafted is 3 nights **plus Window C**. Every "N + 2" arithmetic in this proposal
inherits that omission.

---

## 2. Existing-material compliance

Mostly compliant in spirit, with two hard violations.

- **Compliant:** owned hardware only, no wall-meter dependency, single-request
  boundary intact, all new harness work is manifest/generator/extraction plumbing.
  The correct statement that "a WT310E cannot validate prefill/decode attribution"
  matches draft §8 exactly.
- **Diagnostic reuse — what is genuinely reusable.** Per D-078/D-110 and
  `CLAIMS_STATUS.md` §1 ("pre-genesis windows CANNOT be claim-consumed — their role
  is diagnostic and rule-establishing only"), the historical corpora are void for
  claims. Reusable: (a) *sizing* projections (0.0125 J/prompt-token; the 5.81 J
  128-token cross-model delta; the ~3.3% linearity agreement), (b) runtime/memory
  budgeting, (c) design templates. **Not reusable:** any floor literal (the memo
  bans `7.377086` by name), any effect size as a result, and — the one the proposal
  gets wrong — the diagnostic linearity *as a fitted model*. The proposal is right to
  re-fit prospectively; it is wrong to then call the re-fit a validation of anything,
  since the prospective grid is the same shape as the diagnostic that motivated it.
- **Violation 1 — forbidden upgrade in the title.** AP-1's registry row: "Ceiling
  L3. **Forbidden upgrade: no curvature, universal scaling law**, or
  architecture-wide conclusion from this grid." The paper is titled "Prefill Energy
  **Scaling** … " with Contribution 2 named "empirical scaling curves." The body
  disclaims it ("not a universal scaling law"), but a title that a reviewer, an
  advisor, or a future citation will read as the forbidden upgrade is a governance
  problem, not a wording preference.
- **Violation 2 — gratuitous incompatibility with the seeded grid.** AP-1 freezes
  prompt levels {128, 512, 2048, 4096}. The proposal picks {128, 256, 1024, 4096}.
  There is no stated reason. Choosing non-overlapping interior levels forfeits reuse
  of AP-1's frozen design, estimator, multiplicity rule, and holdout logic, and
  guarantees that neither dataset can ever be pooled with the other.

---

## 3. Novelty — the real problem

Prefill energy is approximately linear in prompt length because prefill is
compute-bound over tokens. This is not in dispute anywhere in the literature; the
proposal's own related work will have to cite TokenPowerBench (which already
"groups results by context length", draft §8) and Fernandez et al. ACL 2025. The
scientific finding is a figure, not a paper.

So the novelty must be carried entirely by the metrology wrapper — and the metrology
wrapper *is the MVP paper*. Score the five contributions against `draft-v1.md`:

| # | Contribution | Already MVP? |
|---|---|---|
| 1 | Two claim-bearing prefill floors | **Yes.** These are D-117's alpha/beta prefill riders, already funded, already the MVP's C-v material. Not a contribution of this paper. |
| 2 | Model-specific scaling curves + held-out prediction | New — but see §1.5, it cannot fail. |
| 3 | Model-size × length interaction | New — but needs floors at every length it spans (§1.3). |
| 4 | Prospective workload sizing as methodology | **Substantially MVP.** Draft §8 already writes the PairedMDE one-way-ratchet doctrine; the SYNTHESIS records it is "consumed by the MVP paper draft §7 'Prospective workload sizing'." |
| 5 | Published refusal boundaries | **Yes.** This is C-iii, the fail-closed protocol and refusal log, already the MVP's third contribution. |

Two of five are new, and one of those two is unfalsifiable as designed.

## 4. Dedup against the D-117 fourth-window option

This is the decisive comparison for funding. D-117 cl.3 leaves open "a prospectively
frozen ≥256-token prefill contrast arm" at "+~110 core minutes, likely its own
window." That option buys the one thing the project actually lacks: a *prefill
contrast that clears the bar* (SYNTHESIS projects ~11.6 J at 256, ~2.3× the bar,
against a 128-token contrast whose interval lower edge sits ~4.0 J, below it).

The proposal's S1 arm at 256 tokens is a **strictly worse version of that option**:
same length, half the blocks (n=5 vs the fourth window's presumed n=10), and no
dedicated floor cell where the fourth window would carry its own. The proposal then
adds two further lengths whose claim status depends on an unratified transport rule.

Dedup value is therefore **low and negative**: funding this proposal would consume
the fourth-window option and replace it with an under-powered instance of itself.

## 5. Venue fit

Broadly honest — capstone chapter, EuroMLSys/HotCarbon or ICPE emerging-research,
ICPE full only conditionally. But the honesty is undercut by the title, and the
stated ICPE-full condition ("if the held-out prediction … succeed[s]") is
circular given §1.5. Against Rivoire's bar specifically, a JouleSort co-author will
ask the repeatability-scaling question in §1.2 within one reading.

## 6. Original-goals service

Accurate and appropriately modest. Serves the workload/length axis of the modular
harness and the "energy as a third metric" goal; serves none of speculative decode,
MTP, MoE, KV variants, or split. Its claim that long workloads are "foundational"
for those mechanisms is true and is the best argument for it — but the same argument
is served more cheaply by the fourth window plus a decode-length rider.

## 7. Non-findings (things I tried and could not break)

- "Identical nested token prefixes cannot be proven across tokenizers" is listed as a
  kill criterion. It is a non-risk: Qwen2.5-1.5B and Qwen2.5-7B share the same
  tokenizer, so nested prefixes are trivially identical. Listing it inflates the
  apparent rigour of the kill list.
- The single-request boundary claim is correct. Nothing here batches, reuses cache
  across requests, or introduces a server.
- The 4096-token memory-headroom concern is real but small: 1.5B/7B 4-bit KV at 4096
  tokens is ~112 MiB / ~224 MiB on a 128 GB machine. This will not be the kill.

---

## Scores

| Axis | Score | One-line justification |
|---|---:|---|
| Novelty | **3** | Prefill ∝ prompt length is known; the metrology wrapper is the MVP's; title claims a forbidden upgrade. |
| Feasibility | **4** | Effect sizing is excellent (~10× the bar); the *plan* is not feasible — no floors at 3 of 4 lengths, anti-conservative transport, n=5 on near-floor cells. |
| MVP leverage | **4** | Reuses §§3–5 cleanly, but 3 of 5 contributions are re-labelled MVP contributions; incompatible with the seeded AP-1 grid. |
| Venue fit | **5** | Honest ladder, but the ICPE-full condition is circular and the title is a referee magnet. |
| Original goals | **4** | Workload axis only, honestly stated; no mechanism axis. |

## Three strengthening moves

1. **Shrink to the fourth window plus one long-endpoint rider, and make each window
   self-flooring.** Drop 256 and 1024 as claim points. Fund, per model, one window
   of: 10 ABBA blocks of the 128-vs-L prefill contrast (40 members) + 5 A=A null
   blocks at L (20 members, the in-window comparative floor for the new condition
   family) = 60 science members, ~3.6–3.9 h with long prefills — rehearse against the
   4 h ceiling before freezing. Pick L = 1024 (≈11 J projected, comfortably clearing,
   and short enough to keep the window inside budget). This converts an
   unclaimable-by-default 2-night plan into a claim-bearing 2-night plan and removes
   the transport dependency entirely. Take the absolute component by transport only —
   it is the non-binding one (historically 6.29 vs 14.0 J for 7B).
2. **Run the repeatability-scaling desk check before funding anything — it is free
   and it is a kill criterion.** From the existing (void-for-claims, fine-for-sizing)
   1.5B corpora, compute the CV of prefill energy at 128 and at 4096 tokens and the
   corner-widened `F_abs` at each. If CV is roughly constant, the floor grows ~linearly
   with length, effect/floor is roughly *flat* across the ladder, and the entire
   "length is the free lever" premise fails beyond the attribution-dominated regime.
   The minted diagnostics already hint at proportionality: 1.5B decode ~51 J with
   absolute/comparative floors 3.82/3.59 J (~7%), 7B decode ~192 J with 6.29/14.0 J
   (~3–7%). Two points, same ratio band. Settle this at the desk, today, before a
   night is spent.
3. **Replace the unfalsifiable held-out fit with a real prospective test, and fix the
   title.** Either (a) pre-register a point prediction with a *pre-stated* tolerance
   in joules (not a floor-guarded envelope) and a stated interval that would falsify
   linearity, or (b) drop Contribution 2 and reframe the paper around the one thing
   that is genuinely novel and genuinely at risk: *the sizing rule itself* — "we
   pre-registered which contrasts would clear, and here is the pre-registration
   against the outcome," with the 128-token marginality as the registered near-miss.
   Retitle to something the AP-1 forbidden-upgrade clause permits, e.g. "Prospective
   Workload Sizing for Phase-Resolved Prefill Energy," and align interior levels to
   AP-1's {128, 512, 2048, 4096} so the data can ever be pooled.

2026-08-07T16:52:27.860017Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "sed -n '1,390p' ../portfolio/rev-quantization-ladder.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review — `prop-quantization-ladder.md`
## "Quantization Under the Floor: Which Precision Rungs Are Measurably Different on Apple Silicon?"

Reviewer: Opus 5 counter-reviewer (adversarial charge: try to kill it).
Ground truth: repo checkout at `scratchpad/desk` @ `89b929c`, main.

**VERDICT: VIABLE — but only as a shrunk 3-rung BF16/Q4/Q8 ladder without a
quality gate.** As written (Q4/Q5/Q6/Q8, quality-equivalence contributions, four
extension nights) it is a WEAK proposal that invents two unverified rungs,
deletes the largest-effect arm the repo already designed for, imports an accuracy
axis that D-041 fences off, and hides a multi-month desk build behind a
truthful-looking night count. Every one of those defects is fixable at the desk
with no external dependency — which is why it survives where the mechanism
directions do not.

| Axis | Score |
|---|---|
| Novelty | 4/10 |
| Feasibility | 5/10 |
| MVP leverage | 7/10 |
| Venue fit | 6/10 |
| Original-goals service | 4/10 |

---

## 1. Which rungs actually exist at pinned revisions — the answer is: one

Asked directly. The repo's local artifact inventory is **4-bit only**:

- `/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit` (839 MB),
  revision `8b403126…ea677`, mirrored per R-014, D-016 provisional pick
  (`docs/decision_log.md:876-879`); `"quantization": {"name":"int4","bits":4}`
  in `configs/examples/mac_mlx_local.json`.
- `Qwen2.5-7B-Instruct-4bit` (4.0 GB), revision `c26a38f6…d9fed`
  (`configs/campaigns/qwen25_7b_decode_floor_v1/calibration_plan.json`).
- **No BF16/fp16 mirror of Qwen2.5-1.5B-Instruct. No Q5. No Q6. No Q8. Nothing.**

The repo's own frozen-on-paper ladder is `docs/specs/axi/sd_model_pair_scorecard.md`
§8, ladder ID `c5-1.12-qwen2.5-1.5b-mlx-bf16-q8-q4-v1` — **three levels: BF16,
Q8_G64, Q4_G64** — and every row is marked `NEEDS-VERIFICATION`. The document is
labelled "PRE-REGISTERED PROPOSAL — no model pair is selected and D-016 is not
amended", authorizing "no model download, campaign, quiet-Mac use, or claim". It
even pre-specifies its own shrink: "A pre-freeze capability check may
prospectively reduce the design to the two-level BF16/Q4_G64 ladder."

So the proposal's **Q5 and Q6 rungs are its own invention**, absent from the
repo's design, unverified at pinned `mlx==0.31.2` / `mlx-lm==0.31.3`, and
unmirrored. The evidence the proposal offers for their existence is that
"current MLX conversion exposes integer bit width" with a link to `convert.py`.

**That is precisely the inference the repo's own AXI-SC verdict forbids.**
`docs/specs/axi/sc_spec_decode_verdict.md` classifies "the parameter exists in
the API" as *not* support evidence — "Configured `num_draft_tokens`, model-call
shapes … may not be substituted for direct evidence"; a surface must be
*exercised*. The proposal applies the loose standard to itself and the strict one
to nobody. Q5 in particular is the least likely to exist as an optimized affine
kernel at this pin. The proposal does flag "local support on the pinned
JouleWise versions remains a required smoke gate" and carries a shrink clause
("If Q5 fails capability before freeze, shrink honestly to Q4/Q6/Q8") — honest,
but it means the headline four-rung ladder is a *hope*, and the paper's title
question is answerable only after a smoke that has not been run.

**And there is an authorization gate the proposal never names.** Deriving four
new artifacts from a new BF16 source revision is a **D-016 model decision**,
explicitly reserved to Ed ("artifact acquisition and any D-016 model decision
remain lead/Ed-owned"). The proposal presents conversion as desk work. It is a
ruling.

## 2. FATAL as written: it deletes the largest-effect arm and keeps only the sub-floor ones

This is the design inversion that would sink it at review.

The repo's motivation for a ladder (`docs/strategy/2026-08-06-impressiveness-roadmap.md`
row 5) is a **"Quality-gated BF16/Q8/Q4 quantization ladder"** whose value is to
"adjudicate the reported q4-vs-q8 anomaly" — **1–2 nights**, 4–8 weeks desk.

The proposal instead:

- **Demotes BF16 to a quality reference only, with no energy arm.** BF16 vs Q4 is
  ~4× the weight bytes — on a batch-1, bandwidth-bound decode this is by an
  enormous margin the most resolvable contrast available, and the one contrast
  guaranteed to clear any floor. It is dropped.
- **Demotes Q4–Q8 to "secondary"** — the exact contrast the roadmap says the
  ladder exists to adjudicate.
- **Promotes the three adjacent rungs to primary** — Q4–Q5, Q5–Q6, Q6–Q8 — which
  the proposal itself concedes are the most likely to miss the bar ("Q5–Q6 the
  most likely miss").

Net: the plan **maximizes night count and minimizes effect size**, then spends
its multiplicity budget (Holm over three adjacent contrasts) on the three tests
most likely to fail. If you were designing to produce a null, this is how.

## 3. Effect sizes vs the ~5 J bar, and whether refusal is the finding

Sizing evidence in the repo: ~**0.098 J/decode token** for 1.5B Q4 (non-claim
diagnostic; note historical corpora are voided for claim use under D-078's
time-anchor defect) → ~**50 J** for a 512-token decode. The ~5 J bar is
`floor + claim-side bound` "for the measured phase-contrast regime"
(`docs/paper/draft-v1.md:115`, `CLAIMS_STATUS.md:55`). **So the bar is ~10% of
total decode energy for the 1.5B/512 workload.** That is a brutal ratio, and the
proposal states it nowhere — it quotes 4–10 J estimates without saying they are
8–20% of the whole measured quantity.

My own first-principles estimate, offered as a check rather than a prior:
batch-1 decode on this stack is weight-bandwidth bound, so energy roughly tracks
weight bytes moved. Q4→Q5 ≈ +25% weight bytes, Q5→Q6 ≈ +20%, Q6→Q8 ≈ +33%. If
energy tracked bytes 1:1 the adjacent contrasts would be ~10–15 J and would
clear comfortably. They probably won't track 1:1 — which exposes the real
problem:

**INTERNAL VALIDITY, unaddressed: this ladder measures MLX kernel maturity, not
the energy cost of precision.** 4-bit and 8-bit are the well-trodden paths in
MLX; 5- and 6-bit affine kernels are, at best, less optimized. A measured
Q5 > Q6 inversion, or a Q5–Q6 gap larger than Q6–Q8, would be an artifact of
which kernels Apple/`ml-explore` tuned — not a fact about precision. A competent
ICPE referee will say "you have measured a software engineering roadmap." The
finding is still legitimate and publishable, but **only if framed that way from
the title down**, and the proposal frames it as a "phase-energy ladder", which
implies a precision→energy relationship it cannot isolate. This is the single
biggest missing caveat in the document.

**The proposal's own sizing evidence is self-refuting.** Its only quantitative
anchor is "an official MLX benchmark on a different Qwen model and M4 Max
reports adjacent generation-throughput differences of roughly 10–17%; **at
comparable power**, that suggests approximately 4–10 J". Different model,
different chip, throughput not energy — and the conversion runs through exactly
the latency⇒energy assumption that JouleWise exists to falsify. The project's
thesis and the proposal's power-analysis are in direct contradiction. Delete it
or replace it with a local daytime timing smoke.

**Is the refusal the finding?** Yes, and this is the proposal's strongest idea —
the title question ("which rungs are measurably different") is genuinely well
posed, and contribution 1 (a rung-specific resolvability map) is the version of
this paper that cannot fail. But be clear-eyed about what a refusal costs and
buys: four extension nights to report "our calibrated instrument cannot separate
Q5 from Q6 at 512 tokens" is a *methods* result that the floor-methodology
direction already delivers more cheaply. The refusal is worth publishing; it is
not worth four nights **unless** it is bundled with at least one contrast that
resolves loudly — which is exactly the BF16/Q4 arm the proposal deleted. And the
proposal's own escape hatch (workload length as the "permitted redesign lever")
means a Q5–Q6 refusal at 512 tokens can be dissolved at 2048 tokens, which
weakens "not resolvable" into "not resolvable at a workload we chose".

**Prefill:** the proposal correctly predicts 128-token prefill rung differences
will miss the bar, correctly says what that refusal means, and this is
corroborated by `docs/process_traces/2026-08-07-prefill-feasibility/` and D-117's
finding that even the 128-token prefill *contrast* is marginal. Fine.

## 4. Cost arithmetic: the night count is roughly right; the desk cost is off by an order of magnitude

Credit where due — I checked the night arithmetic and it broadly survives.
Against DESIGN-MEMO's measured budget (W-alpha 3.14 h, W-beta 3.24 h,
W-gamma 2.80 h; 50 science members = 10 absolute + 40 ABBA for a floor window,
40 for a contrast; overhead of 12 NEG8 + 7 references + 2 live calibration
brackets + 10 min untouched idle, ×1.2 margin):

- Q5/Q6/Q8 floor windows at 10 abs + 40 null each → ≈3.1 h each ≈ **9.4 h**.
- 4-arm contrast, 48 members vs gamma's 40 → ≈**3.1 h**.
- Total ≈ **12.5 h over 4 nights**. The proposal claims "approximately 12–15
  additional quiet-machine hours". **Correct.** It also correctly copies D-117's
  10+40 member design rather than improvising it. Good discipline.

Two real gaps:

1. **Per-rung floors mean per-rung *cells*, and the mint tool is single-cell.**
   `docs/phase_2/floor_mint_contract.md:41` targets one cell,
   `phase_energy_j.decode @ window_class phase`; DESIGN-MEMO F2 (a **blocker**)
   says the tool is "one plan and one artifact cell; `phase_energy_j.decode`
   only; `["phase","decode"]` only; no aggregate artifact over independently
   collected plans." D-117's U3 work order extends it to a **four-cell**
   aggregate (decode+prefill × 1.5B/7B) with component + aggregate pinsets. This
   proposal needs an **eight-cell** aggregate (decode+prefill × four rungs), each
   with its own pre-frozen `pin_requirements.v2` component pinset, plus
   postcollection pins, plus a **four-arm Williams-block estimator with Holm
   control that does not exist**. The proposal's desk paragraph names all of this
   in one 40-word sentence.
2. **Desk cost dwarfs night cost, and desk time is the binding constraint.** The
   roadmap budgets 4–8 weeks for the *three-level* version. This is the four-level
   version plus prefill riders plus an unimplemented quality screen plus a
   multi-arm estimator plus conversion/mirror/dual-hash machinery for four new
   artifacts. Realistically 8–12 weeks. The proposal's funding line — "the three
   D-117 nights plus four extension nights … with no new apparatus" — is
   technically true and rhetorically misleading, because nothing here is
   apparatus-limited; it is desk-limited, against a capstone deadline where P1 is
   the MVP paper.
3. **Failure correlation.** Seven quiet nights total, and each rung floor window
   is a single point of failure: lose the Q6 window to admission and **both**
   Q5–Q6 and Q6–Q8 die. This repo's night history (Window A: 43/50 bundles lost
   to a Ventura screensaver; night-hardening audits still surfacing blockers as
   of today's HEAD) does not support a 7-night serial dependency without a
   re-run reserve. None is budgeted.

## 5. FATAL as written: the quality axis is fenced off, and the harness for it does not exist

Contribution 3 promises "quality-qualified energy conclusions" — a rung is
"called quality-equivalent" only if a 256-item BF16 comparison clears −2 pp
overall and −5 pp per stratum.

**D-041** (`docs/decision_log.md:2239-2287`) fences exactly this:

> cl.3 — joined accuracy+energy data "may never produce **JouleWise accuracy
> claims**, pass@k-per-joule, leaderboard standing, or intelligence-per-joule."
> cl.4 kill/defer list — "**accuracy scoring beyond quarantined annotation**,
> judges/retries/pass@k/benchmark-score normalization."

A JouleWise-run, JouleWise-scored 256-item stratified screen producing a
JouleWise-issued "quality-equivalent" verdict is a JouleWise accuracy
determination. Whether it is *forbidden* or merely *requires a D-041 amendment*
is a lead/Ed ruling — but the proposal makes it a numbered contribution without
noticing that a decision stands in the way. That is an existing-material
compliance miss.

**And the screen does not exist.** The "256-item, four-stratum quality screen"
appears only inside `docs/specs/axi/se_analysis_plans_draft.md` §3 (`AP-QUANT-DRAFT`,
lines 283–294), a file headed "**DRAFT — design only; no campaign authority**",
"PROVISIONAL pending P2-015", claim ceiling **L2 or lower**, and itself dependent
on the unfrozen `sd_model_pair_scorecard.md`. There is **no implementation** —
no scorer, no MMLU/benchmark harness, no per-stratum gate anywhere in
`joulewise/`. The proposal's phrase "**Run the existing** 256-item, four-stratum
quality screen" is factually wrong: nothing existing is being run. That single
word is the proposal's worst sentence, because it converts a multi-week build
into an assumed capability.

**Does the paper need a quality axis to mean anything?** Honest answer: **partly
yes, and that is the direction's core tension.** "Q4 uses less energy than Q8"
without a quality qualifier is a trivially uninteresting statement — of course
fewer bits move fewer bytes; nobody trades precision for joules blind. The repo
agrees: `C-023-QUALITY-EQUIV-QUANT` (`docs/research_question_registry.md:105`) —
"no quantization efficiency or quality-neutrality claim without AP-level
equivalence rule." So a pure-energy ladder is a *resolvability* paper (fine, and
that is the honest title) but not an *efficiency* paper. The resolution is not to
build an accuracy harness; it is to **cite published quality numbers for these
exact rungs as related work** and confine JouleWise's own claim to
resolvability + energy. That keeps D-041 intact and cuts weeks.

## 6. Novelty, venue fit, original goals

- **Novelty: low.** Quantization energy is thoroughly trodden ground. The only
  novel element is the floor-gated *resolvability* framing — and that framing
  belongs to the floor-methodology contribution, not to quantization. Strip the
  instrument and there is no paper here; which is compliant with the hard
  constraint but also tells you the instrument is doing all the work.
- **Venue fit: honest and correctly calibrated.** "Strong capstone/CSCSU chapter
  and a credible EuroMLSys, HotCarbon, or ICPE Emerging extension; for an ICPE
  full paper, combine with artifact release and preferably wall validation or
  second-unit replication." That is the right ladder and the right hedge. No
  WT310E dependency, correctly argued.
- **MVP leverage: the best of any direction I have seen in this portfolio.** It
  keeps the exact D-117 128/512 single-request profile, consumes the D-117 **Q4
  decode and prefill floors directly as the fourth rung**, and reuses the intro,
  related-work gap, calibration method, floor composition, fail-closed protocol,
  attribution-limited result, and the model-size demonstration. That is genuine
  data reuse, not just method-section reuse.
- **Original goals: overclaimed.** The proposal says it "directly serves the
  original **quantization** … axes". Ed's original-goals list is speculative
  decoding, MTP, MoE routing, KV/attention variants, split inference, modular
  harness, energy-honest reporting. **Quantization is not on it.** It is in
  `capstone_scope.md` ("the model set spans quantization and size axes") as a
  *stack dimension*, not a mechanism. The proposal is right that it does not
  advance MTP/MoE/KV/split and right that it exercises the modular harness — it
  should just delete the word "original" from the quantization claim.

## 7. Three strengthening moves

1. **Shrink to the ladder the repo already designed: BF16 / Q4 / Q8, three
   arms, two extension nights.** Q4's floor comes free from D-117. Mint two new
   floors (BF16, Q8), run one 3-arm contrast window. BF16–Q4 is a guaranteed
   loud result (~4× weight bytes) that anchors the paper; Q4–Q8 adjudicates the
   anomaly the roadmap actually cares about. Zero Q5/Q6 capability risk, ladder
   lineage matches `sd_model_pair_scorecard.md` §8 verbatim so the frozen design
   is reused rather than reinvented, and the night count halves. If Q5/Q6 smoke
   *does* pass at the pinned version, add them later as a second-order figure —
   as *exploratory* rungs, not primary contrasts.
2. **Delete the quality gate; cite it instead.** Replace contribution 3 with a
   related-work table of published task-quality deltas for these exact rung
   families, and restrict JouleWise's claim to "energy resolvability at named
   rungs, quality qualified by external evidence." This preserves D-041 intact,
   removes the largest unbuilt component from the desk list, removes a D-041
   amendment from the critical path, and honestly answers the "does it mean
   anything?" objection. If Ed *wants* a quality axis, it is its own decision
   and its own quarter — not a bullet inside a quantization proposal.
3. **Front-load a two-hour daytime capability-and-sizing smoke, and rewrite the
   sizing section around it.** Before any night is committed: (a) convert BF16 →
   Q8 (and Q5/Q6 if you must) at the pinned mlx, load each, verify token
   identity and memory; (b) run wall-clock tok/s and mean-power-free duration
   for each rung on the exact 128/512 workload. That replaces the M4-Max/
   different-model/"at comparable power" extrapolation — which contradicts the
   project's own thesis — with local evidence, and it directly evaluates the
   proposal's own kill criterion ("a daytime timing smoke predicts two adjacent
   effects remain below 5 J") *before* the D-016 amendment, not after four
   nights. Add to the plan: an explicit statement that adjacent-rung differences
   may reflect MLX kernel maturity rather than precision, and a pre-registered
   re-run reserve night, since seven serial nights with no slack against a
   capstone deadline is not a schedule.

2026-08-07T16:52:31.139984Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "sed -n '1,330p' ../portfolio/rev-refusal-as-result.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review: "When the Benchmark Says No" (prop-refusal-as-result)

Reviewer: Opus 5, counter-review pass. Charge: kill it.
Ground truth: `desk/` @ main, plus a full census of the machine-side run roots.
Every cited number was checked against primary bytes.

**VERDICT: WEAK as proposed** (as a standalone paper). The same material
is STRONG in the two forms named in §Strengthening — neither of which is what
was proposed.

| axis | score |
|---|---:|
| novelty | 3 |
| feasibility | 4 |
| mvp_leverage | 3 |
| venue_fit | 3 |
| original_goals | 3 |

`mvp_leverage` is scored **low deliberately**. See FF5: this proposal's
"leverage" is that it reuses §§1–6 *and* republishes the MVP's results as its own
contribution 4. Leverage that high is not leverage; it is double publication.

---

## What is right (stated first, and it is a lot)

Factually this is the most disciplined proposal I have audited. I tried to break
its numbers and could not:

| claim | status |
|---|---|
| 38 calibration observations; 30 valid / 6 ordinary-invalid / 2 systematic-invalid | **EXACT.** `configs/calibration/calibration_acceptance_d079_v2.json` (`prior_observation_set.observations` = 38; `candidate_inventory` states 30/6/2), independently confirmed against the 76-row physical ledger (38 reservations × 2), head pin `sequence: 76` |
| 229-member early collection arc; four windows non-claim-bearing | **EXACT.** a5=108, a6=19, a7=42, a8=60 → 229 (`README.md:30`, `docs/run_reports/2026-07-23-window-a-collection-arc.md:45-48`); reproduced on disk as 228 live + 1 quarantined; a5/a6/a7/a8 produced 7 FAILED verdicts, zero PASS |
| historical decode contrast ≈ 141.29 J, diagnostic | **EXACT** (`CLAIMS_STATUS.md:63`), and correctly labelled pre-genesis/diagnostic per D-117 |
| pre-genesis 7B comparative-floor diagnostic ≈ 14 J | **EXACT** (13.998036 J, `DESIGN-MEMO.md:271`) |
| 128-token prefill difference ≈ 5.81 J, half-width ≈ 1.81 J, lower edge ≈ 4 J | **EXACT** (ten block deltas 5.645–6.008 J, `2026-08-07-prefill-feasibility/CONSULT-RESPONSE.md:173`; `SYNTHESIS.md:12`) |
| budgets 3.14 / 3.24 / 2.80 h; 140 science bundles; 203 total captures | **EXACT** (`DESIGN-MEMO.md:311-328`; 50+50+40 = 140; +36 bound +21 refs +6 cal = 203) |
| alpha/beta = 10 absolute + 10 A=A ABBA blocks; gamma = 10 blocks | **EXACT** |

The correct ICPE Research-vs-Industry track distinction is also drawn properly,
and the "no quiet window, no borrowed hardware" claim is true.

The problem is not accuracy. **The accurate facts do not add up to the paper.**

---

## Fatal flaws

### FF1 — There is no refusal log. The paper's primary evidence object does not exist as an artifact.

`find` over the entire repo for `refusal*` returns **exactly one file**:
`docs/phase_2/refusal_scope_spec.md` — a 72-line *specification*. Zero committed
machine-emitted refusal records. The phrase "the refusal log" occurs in three
non-derivative places, all prose, two of them in `draft-v1.md` itself (`:17`, `:139`).

The actual evidence is **40 `campaign_log.jsonl` files (1,747 rows) and 1,402
`summary_metrics.json`**, living entirely under gitignored run roots
(`.gitignore:7,25,29,31`) on the measurement machine. None is committed,
published, or hash-manifested into any repo artifact. A paper whose primary
evaluation is "the refusal log" is today proposing to cite ~26k uncommitted files.

The proposal describes this as *converting existing failures* — harvesting. It is
not harvesting. The artifact has to be **built first**, and building it is
contribution 1's exporter plus a custody/publication decision (what raw evidence
may be public) that nobody has made.

### FF2 — The honest denominator is ~6–7 distinct refusal mechanisms, and the proposal never states any denominator at all.

Full census of the machine-side corpus:

| refusal event class | count |
|---|---:|
| whole-window verdicts | 16 (6 PASSED, **10 FAILED**) |
| supersession / quarantine records | 7 |
| member-level `status: failed` rows | 64 (39 `exit_code: 3`) |
| bundles carrying ≥1 precheck reason code | 1,368 |
| refusals in the calibration ledger | **0** |

The 1,368 deflates hard: **24,547 of the 35,019 precheck reason occurrences
(70.1%) are on sub-millisecond `phase/tokenize` and `phase/generation_setup`
windows that refuse BY DESIGN**, documented as such in `refusal_scope_spec.md`.
Those are not incidents; they are a gate working.

And the 10 FAILED verdicts are not 10 stories. a5 ×3 are the *same window* with
largely the same condition set; a6 and a8 are the *same* `neg8_bracket_abs_delta_exceeded`
gate; a8's second is a stale-drift re-verdict of a6/a8's material. Deduplicated by
**distinct refusal mechanism** you have roughly six: environment/admission
missing, NEG-8 corner-statistic exceedance, stale drift bound, GPU-DVFM ramp
aliasing the calibration, clock-anchor unresolved, campaign-membership unresolved.

Six mechanisms, one machine, one operator, one project. That is a strong
**lessons-learned section**. It is not a paper's primary evaluation, and "how
many refusals do you actually have?" is the first question any referee asks. The
proposal answers it nowhere.

### FF3 — The proposal's own kill criterion has already fired, and it does not know.

> "Kill the standalone refusal-paper framing if fewer than 90% of claim-relevant
> refusal outcomes can be reconstructed..."

The desk evidence exists today and points to KILL:

1. **No `{member_id → reason_code}` mapping exists anywhere.** In `campaign_verdict`
   rows the per-member failure is free-text prose — e.g. `"invalid unwaived member
   bundle(s): mtadd-p2048o0128-r08"`. **31 of the 51 distinct condition strings**
   across all campaign logs take this form.
2. **No reason→member join at window level.** In the D-098 verdict record,
   `members` has 68 entries and **0 carry a failed/False field**;
   `idle_admission_core.conditions` is a flat set over the whole window. "Which
   member caused `whole_window_bundle_invalid`?" is answerable only from
   decision-log prose.
3. **The paper's flagship anecdote has no machine record at all.** The single
   refusal `draft-v1.md:139` narrates — the r06 `native_intersection_empty` STOP —
   refused *pre-verdict* and produced **no `campaign_log` row**. Its entire
   existence is markdown in `docs/process_traces/2026-08-03-winB-reeval-stop/`.

The proposal treats the census as future desk work. It is a day's work, it should
be done *before* the direction is funded, and every signal I have says the answer
is below 90%.

### FF4 — Contribution 1 is 100% unbuilt, and there is no single taxonomy to predeclare against.

`grep -rn -i 'fault famil'` across the entire tree: **0 hits.** The phrase does
not exist. `mutation matrix`: 2 hits, both as a *review requirement* in one
2026-08-03 cold-gate thread, never a harness. Parametrized fault tests in
`test_whole_window.py` / `test_reduce.py` / `test_floor_extraction.py`: **0**.
What exists is ad-hoc per-test mutators (`test_envelope_gate.py:61-156`), not a matrix.

Worse than "unbuilt" is what it would have to be built *on*:

- **184 distinct reason codes across 11 disjoint enums** in 5+ modules
  (`claims.py` 97, `floor_extraction.py` 34, `bundle_read.py` 22,
  `detection_floor.py` 15, `calibration_ledger.py` 14, `powermetrics_fiducial.py` 14,
  `whole_window.py` 12, `output_identity.py` 11, `idle_dependence.py` 8,
  `registry.py` 6). There is no ONE home.
- **Only 16 of 184 (8.7%) have ever fired on real data.** 34 appear in neither
  tests nor any bundle — dead vocabulary (`floor_row_stale`,
  `equivalence_not_supported`, `randomization_sensitivity_disagrees`, …).
- **The killer:** the 10 FAILED window verdicts are expressed in a 20-code
  condition vocabulary of which **only 4 appear in any enum**. Sixteen codes —
  `neg8_bracket_abs_delta_exceeded`, `neg8_drift_bound_stale`,
  `whole_window_bundle_invalid`, `cpu_busy_ratio_p95_exceeded`,
  `calibration_identity_change`, … — are scattered literals in
  `idle_admission.py:44-67`, `whole_window.py:95-113`, and bare strings in
  `run_campaign.py:5270,:4921`, and are **not covered by `refusal_scope_spec.md`
  §S1**, the ratified ONE home. *The paper's headline refusal events are governed
  by a shadow taxonomy the project's own spec does not scope.*

A refusal-taxonomy paper cannot ship on a taxonomy that is 91% dead vocabulary
with an unscoped shadow governing exactly the events it wants to publish. And
because the proposal also promises artifact release, a referee gets to *see* the
91%.

### FF5 — Double publication. Contribution 4 is the MVP's results section verbatim.

> "**Contribution 4. Useful science after refusal gates.** Publish fresh 1.5B/7B
> prefill and decode floors plus the prospective decode contrast, each with its
> full decomposition and separate floor-clearance and interval-direction verdicts."

That is `draft-v1.md` §7 (C-v) plus §4 (C-ii). Verbatim. Combined with the
proposal's own admitted reuse of "introduction, background, calibration, floor
composition, protocol, scope, and demonstration methods" (§§1–6), **this is the
MVP paper with a taxonomy table appended.** It is not a second paper.

The concrete risk the proposal never mentions in a §"Venue fit" that discusses
ICPE tracks in detail: CSCSU is a real conference with proceedings. If the
capstone version appears there, an ICPE submission carrying the same §§1–5 text
*and* the same D-117 floors and contrast as its own contribution is a
prior-publication disclosure obligation at minimum, and plausibly a desk reject
under ACM substantial-similarity rules. Method-section reuse across a workshop and
a full paper is normal. Republishing the *same results* as a contribution is not.

### FF6 — The ICPE Research Track argument is right about what the track accepts and wrong about what it takes.

The repo's own venue analysis sets the bar
(`docs/strategy/2026-08-06-impressiveness-roadmap.md`, ICPE full research row):

> "C1–C8, cross-day stability, artifact-ready release, and **at least one deeper
> contribution: held-out Q4 prediction, second-unit replication, or a successful
> mechanism study**." Reported 2026 full-paper acceptance: **28%**.

A refusal taxonomy is none of those three. Nor does it meet what "empirical /
case study" means at that track: those papers have a subject *population*. This
has n=1 project, n=1 machine, n=1 author grading his own tooling on six refusal
mechanisms. The honest ladder is ICPE **Artifact Track** (roadmap rank #3 — and
genuinely strong, because refusals are exactly the thing a reviewer can verify),
ICPE Emerging/WIP at 6 pp, or a workshop. Not full research.

## Non-fatal but recorded

- **Two exact numbers used as a category error.** The 38 calibration observations
  are ruled *dispositions* in a genesis historical import — **not one is a refusal
  record**; the 229 are *collected* members, not refused ones. Contribution 2
  cites both as the refusal corpus. A referee who checks finds the taxonomy's
  empirical base is 10 failed verdicts, not 267 of anything.
- **A hidden adjudication.** The D-079 cold gate initially returned **32
  VERIFIED-VALID / 6 invalid** and was BLOCKED until two of the 32 were re-ruled
  systematic-invalid (`2026-08-06-d079-issuance-coldgate/COLDGATE2-FABLE-transcript.jsonl:11`).
  Quoting "30 valid" without that provenance hides a ruling — a bad look in a
  paper whose thesis is that adjudications must be preserved. Also note the
  *derivation* corpus is n=19, not 38.
- **"Adds no quiet window" is true and irrelevant.** It adds a large desk program:
  unify 184 codes, bring 16 shadow codes under `refusal_scope_spec.md` (and per
  §S4 *every* scope move is a **mandatory cold-gate trigger**, per code), build a
  fault-injection framework, a 184-code coverage matrix, a normalized exporter,
  and deterministic replay. That competes for the exact desk hours D-117's U1–U10
  needs, with three blockers (F1/F2/F3) still open. Ed's priority stack is P1 MVP
  paper, P3 sacrificed if it costs P1/P2. **This is P3 work wearing a P1 badge.**
- Fail-closed-with-preserved-negative-evidence is the stated operating principle of
  MLPerf Power / SPEC (`draft-v1.md:26`, `:182`). The contribution here is a
  well-executed *instance* of a published principle, not a method. That is the
  novelty ceiling, and it is low.

---

## Three strengthening moves

1. **Kill the standalone paper; ship it as the MVP's §5 evaluation plus an ICPE
   Artifact-Track companion.** That is roadmap rank #3, it needs zero extra nights,
   "a reviewer can verify our refusals rather than trust screenshots" is exactly
   the artifact-track product, and it dissolves FF5 entirely — an artifact
   companion to your own paper is expected, not double-dipping. The normalized
   refusal exporter and deterministic replay become the artifact, not a paper's
   contribution 1.

2. **Run the census before funding anything, and publish the denominator.**
   One day of desk work: distinct refusal mechanisms (~6–7), failed windows (10),
   supersessions (7), member failures (64), by-design sub-ms deflation (70.1%),
   and the reconstructability rate. If reconstructability is <90% — and FF3 says
   it is — the proposal's own kill criterion fires and the direction closes
   cheaply. That is the correct next spend regardless of which way it lands.

3. **Fix the defect the census exposed; it is worth more than the paper.**
   Sixteen of the twenty window-verdict condition codes sit outside every enum and
   outside `refusal_scope_spec.md` §S1. Bring the shadow taxonomy under the spec,
   and add a `{member_id → reason_code}` field to `campaign_verdict` rows —
   **before the three D-117 windows run**. Then D-117's refusals are
   machine-attributable *prospectively* instead of prose-reconstructed afterwards.
   That is a real contribution to the MVP's C-iii, it is small, and if it does not
   happen before the nights the evidence is lost for good.

2026-08-07T16:52:39.724993Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "sed -n '1,430p' ../portfolio/rev-spec-decode-energy.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review — `prop-spec-decode-energy.md`
## "When Does Speculative Decoding Save Energy on a Mac? Floor-Gated Break-Even Curves"

Reviewer: Opus 5 counter-reviewer (adversarial charge: try to kill it).
Ground truth: repo checkout at `scratchpad/desk` @ `89b929c`, main.

**VERDICT: WEAK.** High ceiling, correct axis, honest hedging — but the proposal
mis-specifies the floor class it needs, understates the build by roughly a
quarter, and the repo's own banked evidence predicts that its headline
deliverable (a localized break-even acceptance threshold) does not exist in the
observable region on this stack.

| Axis | Score |
|---|---|
| Novelty | 7/10 |
| Feasibility | 3/10 |
| MVP leverage | 4/10 |
| Venue fit | 7/10 |
| Original-goals service | 9/10 |

---

## 1. The existing-material constraint: what actually checks out

Credit where due — several things the assignment asked me to attack are **fine**:

- **The draft+target pair exists and is resident-feasible.** All three artifacts
  are mirrored locally: `Qwen2.5-0.5B-Instruct-4bit` (276 MB),
  `Qwen2.5-1.5B-Instruct-4bit` (839 MB), `Qwen2.5-7B-Instruct-4bit` (4.0 GB)
  under `/Users/edr/jw_models/mlx-community/`. Target + draft co-residency is
  ~4.3 GB on a 128 GB machine. There is no memory story here; the
  "M3 Max holds concurrently" constraint is trivially satisfied. Tokenizer
  compatibility holds (Qwen2 vocab 151,936 across the family, per
  `docs/specs/axi/sc_spec_decode_verdict.md`).
- **MLX serves external-draft speculative decoding today.** Pinned
  `mlx-lm==0.31.3` / `mlx==0.31.2` exposes `--draft-model`,
  `--num-draft-tokens`, `speculative_generate_step(...)` with separate
  target/draft caches, and `stream_generate(draft_model=...)` dispatch
  (`sc_spec_decode_verdict.md` §A with line cites into `mlx_lm/generate.py`).
  A **lead-run live Metal probe on 2026-07-17 executed the exact
  1.5B-target/0.5B-draft pair** to completion, evidence SHA-256
  `559731f4…0645f11`. So generation is not the blocker.
- **`gross_energy_per_accepted_draft_token_j` is already policy-correct.**
  `docs/contracts/analysis_plans.md:159` already defines it as a *spec-on-only
  diagnostic*, with `gross_energy_per_committed_output_token_j` as the companion
  efficiency denominator. The proposal restates this correctly and does not
  smuggle accepted-token-J in as an efficiency metric. Good.
- **AP-SPEC exists** as `AP-SPEC-DRAFT` in `docs/specs/axi/se_analysis_plans_draft.md:209`.

So the proposal is not unmoored. Its failures are elsewhere and they are sharper.

## 2. FATAL: the floor class it needs does not exist, and is not on any work order

The proposal's primary metric is **paired `spec_on − spec_off` gross joules per
request**, and its floor window collects "three `gross_request` cells". That
choice is metrologically sensible (see §4) but it walks straight off the end of
the repo's minting machinery:

- `docs/phase_2/floor_mint_contract.md:41` — the ratified mint contract targets
  `phase_energy_j.decode @ window_class phase`.
- `docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md` F2 (blocker):
  the current mint tool is "one plan and one artifact cell;
  `phase_energy_j.decode` only; `["phase","decode"]` only". D-117's own U3 work
  order extends it to **four phase cells** — decode+prefill × 1.5B/7B. It does
  **not** add a gross window class.
- `docs/contracts/analysis_plans.md:164` is explicit that the gross gate is not
  live: floor gate for `gross_request` is "**pending-P2-015** … otherwise **a
  dedicated calibration cell is required**."

So this proposal needs a floor artifact class that (a) does not exist, (b) is not
in D-117's U3, and (c) the analysis-plan contract flags as requiring its own
dedicated calibration cell. The proposal's desk list says "floor selectors" in a
six-word clause. That is a contract-and-mint build comparable in size to U3
itself, invisible in the plan and invisible in the budget.

**Corollary that also guts the MVP-leverage story:** because it needs gross
floors and D-117 mints phase floors, this paper reuses **none of the three
D-117 windows' claim products**. Its "builds on the MVP" is method-section reuse
(§§3–5, instrument characterization, limitations) plus a demonstration figure.
Every claim-bearing number in the mechanism chapter comes from its own two new
windows under a floor class nobody has built. Contrast with the quantization
direction, which consumes the D-117 Q4 floor directly as a rung.

## 3. FATAL: the repo's own dated verdict closes the observability route the proposal reopens

`docs/specs/axi/sc_spec_decode_verdict.md` is a **closed, dated applicability
finding**: `unsupported_for_joulewise(event_observability)`. Its revisit clause
is narrow and explicit:

> "External draft is revisited only after a **pinned-runtime upgrade** exposes
> an **exercised callback** carrying per-round proposal counts, running
> aggregate acceptance, and exact decode-step emitted slices."
> …
> "configured caps or reconstructed groups **do not trigger revisit**."

The proposal's answer is "the current MLX path must be **wrapped or narrowly
forked** to emit actual `tokens_proposed`, `tokens_accepted`, acceptance rate,
and exact committed bursts." Two problems:

1. **It is not a pinned-runtime upgrade.** The proposal quietly proposes to
   satisfy a closed verdict by editing the thing the verdict is about, without
   naming the decision that reopens it. That is a lead/Ed ruling, not a desk
   task. The proposal never says "this requires reopening the AXI-SC verdict" —
   it should, in its first paragraph. (To be fair to it: a fork *can* emit real
   proposal counts, because they are genuine local variables inside
   `speculative_generate_step` at `mlx_lm/generate.py:607-627`. This is real
   evidence, not the forbidden inference. The objection is procedural and
   metrological, not epistemic.)
2. **A forked runtime is a different measured stack.** The floor-mint pin set
   binds "model/runtime/config hashes"; `sc_spec_decode_verdict.md` itself pins
   per-file SHA-256 of `mlx_lm/generate.py`. Changing `generate.py` changes the
   stack identity for *both* arms and severs any inheritance from D-117-era
   calibration. The proposal collects its own floors, so this is survivable —
   but it must be stated, and the spec-off arm must run the *forked* runtime too,
   which the proposal never says.

**Unaddressed and serious: in-window instrumentation load.** The plan emits one
`decode_emission` event per decode step across a 256-token generation, in the
middle of a quiet-machine measurement whose instrument is *attribution-limited
at ~1 J per phase member* and whose bar is ~5 J. Callback + serialization work
inside the measured window is exactly the contamination class this project has
already been burned by (Window A: 43/50 bundles lost to a screensaver). Worse,
the instrumentation load is **asymmetric across arms**: spec-on has fewer decode
steps but more per-step payload; spec-off has one event per token. So it does
not cancel in the pairing. Nothing in the proposal budgets, measures, or bounds
this. A referee at ICPE will ask, and there is no answer in the text.

## 4. Phase-boundary well-posedness: the proposal dodges correctly, then pays for it

Asked directly: is energy-per-ACCEPTED-token well-posed under this project's
phase boundary? **Under phase resolution, no. Under gross_request, yes but
weakly.**

- Under spec-on, the **draft model performs its own prompt prefill**. If the
  prefill/decode split is anchored on the target's first committed token, the
  draft's prompt pass lands inside "prefill" and the phase now contains two
  models' prompt processing — a different physical object than the spec-off
  prefill carrying the same label.
- Inside "decode", the target's verify pass is a *batched K+1-token forward* —
  prefill-shaped compute wearing a decode label. Comparing "decode energy"
  across arms compares different mechanism compositions under a shared name.
- The proposal **sidesteps this by making `gross_request` primary** and
  explicitly attempting "no per-round energy attribution". That is the right
  call and I credit it. But note the cost: **the mechanism chapter is the one
  chapter of the paper with no phase resolution** — it abandons the project's
  signature contribution precisely where it would be most interesting, and it
  is the reason §2's missing floor class bites.
- Energy per *accepted* token: numerator = whole-request gross J including draft
  work, verify work, *and* rejected-proposal waste; denominator counts only
  draft-originated committed tokens and excludes the target's bonus token. It is
  a well-defined ratio and a legitimate mechanism-yield diagnostic. It is not an
  efficiency metric, it is undefined for spec-off, and the D-037 rider in
  `analysis_plans.md` already says so. Compliant. But the paper's *title*
  gestures at exactly the quantity it is contractually barred from headlining.

## 5. FATAL: acceptance rate is not manipulated — the break-even curve is observational and under-identified

The assignment asked how the proposal honestly *sets* acceptance rate as an
independent variable. **It doesn't.** It uses "a frozen, equal-token-shape prompt
roster spanning chat, code, and structured reasoning to generate acceptance
variation" and regresses paired Δ-energy on runtime-observed acceptance. Three
consequences the proposal never confronts:

1. **Effective n is the number of prompts, not the number of members.**
   Acceptance is a per-prompt property; 80 members over a handful of prompts
   yields a handful of distinct x-values. Contribution 2's headline is a
   *break-even threshold with an interval* — the root of a fitted line — and no
   estimator is named (Fieller? delta method?). Rooted-ratio intervals from ~6–10
   prompt-level points will be enormous. This is the most likely quiet failure
   mode: not a refusal, but a "break-even is somewhere between 40% and 95%"
   non-result that still cost two nights.
2. **No multiplicity control is specified**, unlike the sibling quantization
   proposal which names Holm. There are at minimum: on/off at two draft sizes,
   the size contrast, and a fitted threshold.
3. **Acceptance is a post-treatment mediator observable only in the spec-on
   arm.** Regressing the paired difference on a spec-on-only covariate is a
   descriptive model at best; any threshold statement is an extrapolation the
   claims ladder would push below L2. (Note: `se_analysis_plans_draft.md` sets a
   **claim ceiling of L2 or lower** for every plan in the file, including
   AP-SPEC-DRAFT, and is PROVISIONAL pending P2-015 floors.)

**The obvious manipulable lever is fixed by fiat.** The proposal pins the
proposal cap at **K=3** and then hunts for variation in prompt content. K is a
genuine, settable, pre-registrable independent variable (K=1,2,3,…), and draft
size is a second. The design uses the two weak levers and freezes the strong one.

## 6. Effect sizes vs the ~5 J bar — and the self-refuting prior

Provenance check: the ~5 J bar is `floor + claim-side bound`, "**for the measured
phase-contrast regime**" (`docs/paper/draft-v1.md:115`, `CLAIMS_STATUS.md:55`,
D-078 cl.11). The proposal imports it wholesale into a **gross_request** design.
That is not obviously the right bar in either direction — a gross window has two
request edges rather than an internal phase split, so its attribution term may
well be *smaller*. The proposal never re-derives it. Since its own floors will
define the real bar, all the "5 J ≈ 5% of request energy" arithmetic is
decorative.

On magnitudes: the ~192 J historical 7B 512-token member halved to "~96 J at 256
tokens" is flagged as non-claim extrapolation — fine, but note the historical
corpora are voided for claim use (D-078 time-anchor defect), so this is a
diagnostic-of-a-diagnostic.

**The killer is the repo's own smoke.**
`docs/process_traces/2026-07-17-dspark-dflash-smoke/README.md` (lead-run, Metal):

| mode | tok/s | accept/round |
|---|---|---|
| dspark | 45.8 | 2.60 |
| dflash | 40.4 | 2.45 |
| **baseline greedy** | **113.0** | — |

Speculative modes ran at **0.36–0.41× baseline throughput** on this class of
stack. Two models drawing power for 2.5× longer is not a break-even candidate;
it is a rout. If the mlx-lm external-draft path behaves similarly (different
mechanism family, so not dispositive — but it is the only local evidence there
is), then Δ-energy is large, positive, and monotone across the entire observable
acceptance range, **the break-even root lies outside the data**, and the
proposal's own kill criterion "the break-even is unlocalized" fires *after* the
nights are spent rather than before. The honest expected deliverable is one
sentence: "on this stack, external-draft speculative decoding never repays its
energy." That is a real result. It is not two quiet windows plus a quarter of
runtime engineering worth of result.

The counter-evidence the proposal leans on (`mlx-dspark` reporting 1.7–2.3× on
an M4 Pro) is a *different mechanism, different model family, different chip*,
and the proposal itself notes the contradiction and widens its prior to
−40 J…+100 J. A prior that wide is an admission that the desk gate cannot size
the effect, which means the gate cannot do the job the proposal assigns it.

## 7. Cost accounting the proposal understates

- **Nights.** Floor window: 3 cells × (5 absolute + 5 ABBA null blocks = 25
  members) = 75 science members, plus D-117's fixed overhead (12 NEG8 = 22 min,
  7 references, 2 live calibration brackets = 16 min, 10 min untouched idle,
  ×1.2 margin). Mechanism window: 80 members. Both land near or over the 4 h
  envelope depending on whether spec-on members are ~2.5× slower (see §6) — and
  if they are, the mechanism window blows the envelope and splits into a third
  night, which the proposal concedes.
- **The repetition counts are cut in half without justification.** D-117 floor
  windows are **10 absolute + 40 ABBA null = 50 science members per cell**
  (DESIGN-MEMO §budget, 3.14 h / 3.24 h). This proposal uses **5 + 20 = 25 per
  cell**. The operative floor is `max(absolute_component, comparative_component)`
  — a **max of two noisy estimates biases upward**, so halving n does not merely
  loosen the floor, it systematically *raises the bar the effect must clear*.
  Self-defeating, and it is the one number in the plan that should have been
  copied verbatim from D-117 rather than improvised.
- **Calendar.** The proposal advertises "a two-to-three-week desk feasibility
  gate" then two nights.
  `docs/strategy/2026-08-06-impressiveness-roadmap.md` row 7 — the roadmap entry
  for exactly this direction — says **"2–3-week desk feasibility gate; if passed,
  another 6–12 weeks and roughly 2 nights."** The proposal reproduces the gate
  and silently drops the 6–12 weeks. For a capstone on a submission clock with
  P1 = MVP paper, a hidden quarter is the single most consequential omission in
  the document.
- **Exact-output-identity gate.** The proposal's own kill criterion, correctly
  identified, citing a live mlx-lm greedy-divergence report at K=4. My read: the
  probability this gate fires is high — spec decode's exactness guarantee is
  distributional, and batched verify vs sequential decode differ in float
  reduction order. If identity fails, the contrast is a workload change, not a
  mechanism contrast, and the paper ends. Honest of them to name it; it does not
  stop it being a coin-flip on which a quarter is staked.

## 8. Existing-material compliance, venue honesty, original goals

- **Existing material:** artifacts PASS (all mirrored, no downloads, no D-016
  amendment needed). Runtime FAILS-with-caveat (requires forking the pinned
  runtime and reopening a closed dated verdict). Floor machinery FAILS (needs an
  unbuilt window class). No wall-meter dependency — correctly argued, and the
  argument that WT310E cannot validate phase allocation is right.
- **Venue honesty: the best part of the document.** It explicitly disclaims
  "first speculative-decoding energy study", names EuroMLSys / ICPE emerging as
  the destination if the interval is broad, and positions the capstone version as
  an *optional* chapter on an independently complete metrology paper. That
  optionality is the proposal's real strength — a null here does not damage P1.
- **Original goals: bullseye.** Speculative decoding is the first-named axis on
  Ed's original list, and the roadmap explicitly recommends it as the *first*
  mechanism choice. It also genuinely exercises the modular-harness vision
  (swappable draft/target/policy). If any direction deserves the mechanism bet,
  it is this one — which is why the flaws above are worth fixing rather than
  walking away from.

## 9. Three strengthening moves

1. **Make K the manipulated variable and drop the break-even curve as the
   headline.** Pre-register a K ∈ {1, 2, 3, 4} sweep at a single draft size
   against a fixed prompt, with acceptance as a *measured mediator*, not the
   x-axis. K is settable, pre-registrable, and generates a monotone design with
   a real dose-response; the current design has no manipulated variable at all.
   Retitle to "Does speculative decoding ever repay its energy at batch 1?" —
   a question this instrument can actually answer, with a directional
   floor-gated answer either way. Keep acceptance-vs-Δenergy as a secondary
   descriptive figure with an honest prompt-level n.
2. **Move the go/no-go evidence to the front and make it cheap.** Before any
   runtime fork, run a *non-claim, daytime, wall-clock-only* spec-on/off timing
   pilot on the 7B/0.5B pair with the stock pinned runtime (generation already
   works — no instrumentation needed for tok/s). If spec-on is slower than
   baseline, as the DSpark/DFlash smoke predicts, the energy answer is settled
   at essentially zero cost and the whole fork/floor/AP build is never funded.
   This is a two-hour desk task that currently sits *after* two to three weeks
   of instrumentation work.
3. **Fix the floor story explicitly, or change the primary metric.** Either
   (a) name the `gross_request` floor-class build as a first-class work item,
   fold it into D-117's U3 pinset-v2 scope so one mint effort serves both, and
   restore the 10+40 member design; or (b) if that is too much, re-scope the
   primary metric to `phase_energy_j.decode` with an explicit, pre-registered
   statement of how the draft's prompt pass is attributed — and accept the
   phase-comparability caveat in the text rather than avoiding it by metric
   choice. Additionally: run the spec-off arm on the *same forked runtime*, and
   pre-register a measured bound on in-window instrumentation energy (an
   instrumented-vs-uninstrumented spec-off pair) before either arm is claimed.

**Bonus route worth a paragraph in any revision:** `mlx-dspark`/`mlx-dflash` are
already vendored and smoked locally, and the smoke README notes they surface
**per-round acceptance and target-forward counts — precisely the observability
surface pinned mlx-lm lacks**. That path needs no fork of the calibrated runtime.
It costs a different target model (Qwen3-4B), a D-016 touch, a non-mirrored
auto-fetched drafter, and a thinking-policy pin (D-074) — but the proposal does
not even mention it, and it may be the cheaper road to the same paper.

2026-08-07T16:52:44.508418Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "sed -n '1,260p' ../portfolio/rev-split-inference-metrology.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review: "From One Boundary to Two: Fail-Closed Energy Metrology for Split LLM Inference"

**Reviewer:** Opus 5, adversarial lens (contract + feasibility). **Charge:** kill it.

## Verdict

**WEAK** — and the headline version (split-vs-monolithic energy winner, wall-meter dependent) is a **KILL**.
The proposal is the most honest of the ambitious directions and the only one that serves the original
split axis, but it (i) proposes a joint error budget whose dominant term is unmeasured and probably an
order of magnitude larger than every effect it wants to claim, (ii) depends on hardware the project does
not own and a decision (D-092) that forbids assuming it, (iii) requires a runtime stack for which no
adapter, no artifact lineage, and no calibration exist — which is why it quietly reuses *none* of the
D-117 data while claiming it reuses all of it, and (iv) budgets three nights for building a second
instrument that took four months and nine adversarial rounds the first time. There is a genuine, small,
fundable paper inside it. It is not this one.

## Scores (1-10)

| Axis | Score | One-line |
|---|---|---|
| novelty | **4** | Split case study is derivative *and* operationally irrelevant as configured; the cross-boundary budget idea is real but underdeveloped. |
| feasibility | **2** | Two hardware gates never closed, no llama.cpp adapter, no cross-device fiducial exists, meter not owned, laptop AC boundary is battery-buffered. |
| mvp_leverage | **3** | High method reuse (§§3-5), near-zero data reuse — by its own admission. |
| venue_fit | **4** | ICPE full track will reject one unsizable replay pairing; WIP/workshop plausible for the metrology remnant only. |
| original_goals | **9** | This *is* the split axis, honestly scoped, honestly silent on spec-decode/MTP/MoE/KDA. Real credit here. |

## Fatal flaws

**F1 — The joint error budget is not constructible, and the proposal's own arithmetic understates it by
~10x.** The Mac term is known: ~1 J per phase member, 30 ms edge x 33 W (`docs/paper/draft-v1.md:84`).
The GPU term is *unknown by the project's own admission*: `docs/JouleWise_Hardening_Proposal.md:453`
lists "nvidia-smi cadence and averaging characterization" as an unexecuted Phase-7 promotion item, and
`joulewise/adapters/nvidia_smi.py:401-402` computes `interval_ms = 1000/power_hz` — i.e. the harness
*assumes the requested poll rate is the instrument cadence*. That is precisely the class of assumption
D-078 was created to destroy on the Mac. NVML board power on consumer Ampere is a filtered average whose
internal update period is not the poll period; at a 350 W board, a 100 ms edge is ~35 J and a 1 s edge is
~350 J. Four stages x two edges. Against effects the proposal itself sizes at 10-200 J, **the budget is
plausibly larger than every claimable quantity in the paper.** The proposal spots this ("a 100 ms
uncertain edge on a high-power PC can be tens of joules") and then does not act on it: no composite bar
is stated, S2/S3 are unchanged, and contribution 2 still promises transfer floors. A referee reads that
as knowing the study is unsizable and submitting anyway.

**F1b — There is no cross-device fiducial, so the method's core does not transport.** The project's
distinguishing move is an *in-window physical* pulse-train fiducial (`joulewise/powermetrics_fiducial.py`,
`calibration_bracketing.py`). It is intrinsically within-machine: you cannot inject a Mac power pulse and
observe it on a 3080 Ti. The proposal substitutes an ordinary software clock bound ("both clocks produce a
prospective bound smaller than 25% of the shortest claimed interval") while retaining D-078's rhetoric of
calibration. The only shared physical channel that could bracket both clocks is the wall meter — borrowed,
single, 100 ms-cadenced. **This is the deepest flaw: the paper inherits the vocabulary of the calibrated
instrument without its mechanism.**

**F2 — Both endpoint boundaries structurally exclude the quantity the paper is about, and the repo already
ruled on it.** D-049 (`docs/decision_log.md:2673`): on nvidia-smi ends, board power excludes host
CPU/NIC/DRAM, so "transfer energy measured at a discrete-GPU end is near-zero by construction." D-018:
powermetrics = cpu+gpu+ane, an SoC subsystem proxy excluding display/storage/PSU. An M3 Max MacBook Pro
has no Ethernet port — the 1GbE/2.5GbE link runs through a Thunderbolt/USB-C adapter drawing outside the
SoC rails. So sender NIC energy is outside the Mac boundary and receiver host/NIC energy is outside the
GPU boundary: **transfer energy, the load-bearing new quantity, is unmeasurable at both endpoints.**
D-049 already picked the remedy (wall meter, or explicit board-only lower bounds). The proposal takes the
wall meter, which lands it in F3.

**F3 — The wall-meter plan is internally contradictory and physically unsound for a laptop.**
(i) *Contradiction:* one meter on a shared strip cannot mint "sender, receiver, combined-wall and
composite" floors (contribution 2). Sender and receiver wall floors require two meters. Unrepaired.
(ii) *Battery buffer:* a MacBook Pro at the AC boundary is charge-buffered; macOS charges
opportunistically, so second-scale AC draw is decoupled from SoC power. MLPerf Power's battery rule is
quoted in this project's own draft (`draft-v1.md:26,182`) — and the proposal violates it without mention.
First-page referee kill. (iii) *Baseline swamping:* the "unused reference node remains powered and idle"
adds ~60-100 W of PSU-inclusive idle to the combined boundary, with nonlinear efficiency in load, against
10-200 J effects; the WT310E's 0.1% rdg + 0.1% rng at a ~400 W range is ~0.4 W of systematic error, i.e.
~12 J over a 30 s composite window — comparable to the effect. The proposal says the meter spec "must
enter the floor calculation" and never does the arithmetic. (iv) *Standing decision:* D-092 ratified the
meter but recorded **no hardware, C8 conditional, "not assumed by any campaign plan."** The proposal's
headline assumes it.

**F4 — Existing-material compliance is rhetorical.** MLX prompt-cache state is not portable to CUDA;
D-015's hard rule forces same-runtime both ends, which means llama.cpp/GGUF. The repo has
`adapters/{mlx_runtime,vllm_runtime,mock_*}.py` and **no llama.cpp adapter**. So the paper needs a new
runtime adapter, a new artifact/quantization lineage (not the pinned MLX 4-bit Qwen2.5 rev `8b40312`),
re-run determinism/output-identity machinery, and — because floors are stack-specific — **a full floor
re-mint under a runtime that has never been calibrated.** The proposal concedes it in its last section
("D-117 MLX results are *not* direct monolithic comparators for a llama.cpp split stack"), which
contradicts its own claim two paragraphs earlier that it "reuses all three D-117 datasets as the validated
one-boundary baseline." Under Ed's binding constraint this proposal reuses §§3-5 prose and **zero data**.
That is permissible only if stated plainly; it states the opposite.

**F5 — Schedule is off by a large factor, on the project's own record.** Three 2-4 h windows + a pilot +
a contingency, to stand up a *second, harder* instrument. Cost of the first: P0 instrument repair =
nine adversarial confirmation rounds and PR #79; D-078 through D-117 = ~4 months; and `CLAIMS_STATUS.md`
§1 today reads **"VALID — NONE at this checkpoint."** Zero citable numbers exist. Meanwhile the
prerequisites are worse than the proposal's list: `TASK_QUEUE.md` E6/P1-006 is still `READY
[ED-EXTERNAL]` and A23/P2-005 records the NVIDIA lane as fixture-first with "protocol pins remain
provisional until the external live-promotion rows execute" — **the 3080 Ti has never produced a live
bundle and its telemetry access has never been confirmed.** P1-004 (measured topology) is open; 2.5GbE is
aspirational in the plan, not evidenced as owned. Add schema v0.2, composite bundles, two importers,
cross-clock propagation, portability spikes, D-048 pre-registered predictions, D-049 per-cell boundary
labels — on top of the three *blockers* the D-117 memo already carries for the existing windows (F1
bracket-session capability, F2 pinset v2, F3 successor-artifact path). Honest re-cost: 8-12 windows and a
semester, not three nights.

**F6 — Novelty is thin in both directions.** As systems: the repo's own `related_work_draft.md` already
surveys Revisiting Disaggregation Energy (EuroMLSys'26, 2xA100 PCIe, higher energy), DualScale (16xH100,
IB, GPU-only NVML), Splitwise, Prima.cpp, SplitZip. An *offline file-replay* split — prefill on a Mac,
scp a 56-448 MiB cache, decode on a consumer GPU over 1GbE — is not disaggregation as the field means it;
it is a deployment nobody proposes, whose crossover is dominated by link bandwidth, answering a question
whose answer is both predictable and uninteresting. As metrology: Silicon Showdown already demonstrated
the failure mode (PyNVML board vs powermetrics SoC); showing the comparison is invalid is not new, and
repairing it needs the bridge hardware that isn't owned.

*Credited, in fairness:* the kill-criteria section is the best-shaped in the portfolio; the "~5 J is only
a Mac phase-design reference" paragraph is exactly the right instinct; the honest statement that live
split is stretch and that portability failure caps the work at synthetic metrology is correct discipline.
The proposal is not naive — it is under-costed and one step short of following its own best insight.

## Three strengthening moves (if kept)

1. **Invert the paper: make the refusal the result, and drop the meter.** Kill the split-vs-monolithic
   winner claim and contribution 4. Ship a *boundary-composability* paper: pre-register the composite
   budget arithmetic before any collection; add the one cheap missing empirical input — a **GPU-side
   cadence/averaging characterization** (pulse-train step-load on the 3080 Ti, no LLM, no Mac, closes
   hardening Phase-7 item 4 and costs one non-quiet evening on owned hardware); then publish "the
   two-boundary composite budget is ~N J against candidate effects of 10-200 J, therefore the split
   comparison is REFUSED, and here is the exact operating domain where it would resolve (payload >= X GiB,
   link <= Y Gb/s, board TDP <= Z W)." Falsifiable, entirely owned-hardware, and it makes the fail-closed
   machinery do the most interesting work in the paper. This is the version that fits ICPE WIP.
2. **Build a shared physical fiducial or declare its impossibility as the finding.** Replace the NTP-shaped
   clock criterion with a cross-device *power-step* fiducial: a pre-registered train of fixed-size
   transfers whose starts/stops appear as power steps on both endpoints, with the cross-clock bound derived
   from observed step alignment rather than from a software clock. This is the only construction that
   preserves continuity with D-078's actual mechanism. If it cannot produce a bound under 25% of the
   shortest claimed interval, that failure is the headline — and a better one than a crossover plot.
3. **Fix the runtime accounting and the two contradictions, then re-cost in the open.** State plainly that
   the split stack is llama.cpp/GGUF and therefore a *new instrument* needing its own calibration regime
   and floor mints, with the honest 8-12-window budget attached — or drop the real-split arm to future work
   under D-092/C8's existing conditional framing. Separately: delete the sender/receiver wall floors from
   contribution 2 (one meter cannot mint them), and add battery-charge neutralization with verified steady
   state as a hard admission gate before any wall-boundary claim, per the MLPerf rule the draft already
   cites.

**Disposition recommendation:** do not fund as a second paper. Fund move 1 as a ~1-evening desk+bench
probe; if the GPU cadence characterization comes back at 100 ms or better *and* a cross-device power-step
bound lands under the 25% criterion, revisit. Otherwise this direction's correct home is a quantified
future-work section in the MVP paper — which is exactly where D-092 already put it.

2026-08-07T16:52:49.854435Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "sed -n '1,390p' ../portfolio/rev-tokenizer-honesty.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review: "A Token Is Not a Unit: Tokenizer-Honest Energy Reporting for Local LLM Inference"

Reviewer: Opus 5, counter-review lens (contract + prior-art + existing-material).
Target: `scratchpad/portfolio/prop-tokenizer-honesty.md`
Ground truth: repo at `scratchpad/desk`, HEAD `89f28bf`; D-117 at `docs/decision_log.md:7507`;
`docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`.

**VERDICT: WEAK.** Not a kill on honesty — the proposal is unusually careful about what it
refuses to claim, and every load-bearing feasibility assertion I checked is *true*. It is a kill
on **paper-hood**. This is a correct, cheap, ~1.5-page section of the MVP paper that has been
inflated into a standalone paper by borrowing the MVP paper's three windows wholesale and
attaching a desk exercise whose headline result was published at 100× the scale in 2023.

**Scores** — novelty 2, feasibility 9, mvp_leverage 5, venue_fit 3, original_goals 5.

---

## What I verified (the proposal's factual base is mostly sound)

Credit where due. I checked the proposal's concrete assertions rather than taking them:

| Assertion | Verdict |
|---|---|
| Qwen2.5-1.5B and 7B tokenizer artifacts are byte-identical | **TRUE.** Both `tokenizer.json` sha256 `a8506e7111b80c6d8635951a02eab0f4e1a8e4e5772da83846579e97b16f61bf` (`~/jw_models/mlx-community/`) |
| Qwen2.5, Qwen3, OLMo tokenizer artifacts "already present locally" | **TRUE.** `~/jw_models/` holds Qwen2.5-{0.5,1.5,7}B, Qwen3-4B, Qwen3.5-122B, OLMo-1B-0724-hf, OLMoE-1B-7B-0924 |
| 141 J historical decode contrast, non-claim | **TRUE.** `CLAIMS_STATUS.md:63` — `phase_energy_j.decode` 7B−1.5B = 141.29 J, re-scoped DIAGNOSTIC by D-117 |
| 128-token prefill contrast ≈ 5.81 J, marginal | **TRUE.** Ten block deltas 5.645–6.008 J, `docs/process_traces/2026-08-07-prefill-feasibility/CONSULT-RESPONSE.md:173` |
| D-117 budgets 3.14 / 3.24 / 2.80 h | **TRUE.** DESIGN-MEMO:327 |
| Prefill rider adds no member, no runtime | **TRUE.** DESIGN-MEMO:261 |
| Outputs retained for cross-tokenization | **TRUE.** `response_text` is a bundle field, `docs/contracts/run_bundle_layout.md:401` |
| No frozen-boundary violation | **TRUE.** All three new capabilities are desk reducers; inference execution untouched |

So the proposal is not fantasy. That makes the following objections harder, not easier — they are
objections to what the work *is*, not to whether it can be done.

---

## FATAL FLAWS

### F1. It is not an energy paper. The proposal itself proves this.
The charge asked whether the paper needs *any* new windows. The proposal answers, in bold:
"This paper needs **no additional quiet night beyond those three**." Those three are the MVP
paper's windows. Subtract the MVP paper and what remains is: token counts on parallel text,
computed at a desk, in an afternoon, with zero joules.

The tell is Contribution 2. Strip the LaTeX and it reads: for any positive reals,
`((E_A/T_A)/(E_B/T_B)) / (E_A/E_B) = T_B/T_A`. That is an identity. It holds for every E and
every T. It cannot be falsified by any experiment, on any instrument, on any hardware. Listing an
algebraic tautology as a numbered falsifiable contribution is a category error, and a metrology
advisor who co-authored JouleSort will name it in the first paragraph of her feedback.

The paper's whole causal step — from "token counts differ" to "reported *energy* comparisons
distort" — is made by that identity, never by measurement. Everything downstream is arithmetic on
someone else's joules.

### F2. Direct-hit prior art, entirely unacknowledged.
Contribution 1 is "a measured denominator-distortion distribution": ~200 FLORES parallel sentences
× 6–8 languages × 3 tokenizers. This is a strict *subset* of published work:

- **Petrov, La Malfa, Torr, Bibi, "Language Model Tokenizers Introduce Unfairness Between
  Languages," NeurIPS 2023** — tokenization lengths over **2000 FLORES-200 sentences**, ~17
  tokenizers, disparities **up to 15×**, framed explicitly as cost, latency, and context
  unfairness. They ship `tokenization_lengths.csv` publicly. The proposal's entire Contribution 1
  is a row-and-column slice of a released dataset.
- **Ahia, Kumar, Gonen, Kasai, Mortensen, Smith, Tsvetkov, "Do All Languages Cost the Same?
  Tokenization in the Era of Commercial Language Models," EMNLP 2023** — FLORES-based, up to 5×
  token inflation, and the *identical* argumentative move: the token is a billing denominator, so
  denominator disparity distorts the reported cost of the same content.

The proposal contains **zero** related-work positioning against tokenizer-fertility literature.
Not a hedge, not a citation, not a "we differ in that…". For a paper whose entire headline is that
literature's flagship result, this is not an omission — it is the review.

The only available differentiator is substituting **joules for dollars**. Per F1, the proposal
never measures that substitution. So the delta over Petrov 2023 is: a unit relabel, asserted.

### F3. The project's own contrast is a negative control *by construction* — the proposal admits it and moves on.
Contribution 3 offers gamma (1.5B vs 7B decode) as "a calibrated same-tokenizer control." I
verified the tokenizers are byte-identical. Correct — and devastating. The paper's **only**
calibrated energy evidence is, by design, evidence in which the pitfall it is about **cannot
occur**. A paper about a hazard whose measured content is guaranteed hazard-free is a paper whose
measured content is decorative.

Worse: gamma is already the MVP paper's headline result. Contribution 3 is the MVP paper's
demonstration study, relabelled as a control.

### F4. The tokenizer roster is inflated 3→2. I measured it.
The proposal names "three exact artifacts already present locally—Qwen2.5, Qwen3, and OLMo."
Byte-distinct, yes. Behaviorally distinct, no. I loaded all four local `tokenizer.json` files and
tokenized ten matched parallel sentences (nine scripts), same semantic content:

```
lang    chars  bytes  Qwen2.5  Qwen3   OLMo  OLMoE   OLMo/Q2.5  Q3/Q2.5
eng       168    168       28     28     28     28        1.00     1.00
spa       183    193       45     45     54     54        1.20     1.00
deu       174    176       47     47     58     58        1.23     1.00
zho        41    123       23     23     59     59        2.57     1.00
jpn        69    207       44     44     75     75        1.70     1.00
ara       133    244       46     46     90     90        1.96     1.00
hin       131    339      121    121    130    130        1.07     1.00
kor        67    167       45     45    116    116        2.58     1.00
rus       165    303       54     54     82     82        1.52     1.00
tha       118    352       52     52    131    131        2.52     1.00
```

Vocab: Qwen2.5 151665, Qwen3 151669 (four added specials), OLMo/OLMoE 50280.

**Qwen3/Qwen2.5 = 1.00 on every language, every script.** Same merges. And OLMo-1B ≡ OLMoE-1B-7B
(`tokenizer.json` sha256 `a094266ac6c4982efba277bc251349a5a6d6ad37efb39a2a90f53d8be2a40a40` for
both). The proposal's three-tokenizer audit is an **N=2** comparison — Qwen-family vs
GPT-NeoX-family — dressed as three. Contribution 1's "distribution" is one ratio with two
endpoints. A reviewer who runs the check I just ran (fifteen minutes, no hardware) finds this.

### F5. On the paper's own measured corpus the effect is exactly zero.
The proposal's second desk leg is "cross-tokenize the exact prompts and retained outputs from the
three D-117 windows." I pulled the actual window config
(`configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/…-b04-a1.json`):
workload profile `df_ph_decode`, `prompt_tokens: 128`, `output_tokens: 512` — synthetic English.
Row 1 of my table: **OLMo/Qwen2.5 = 1.00 on English.** Cross-tokenizing the D-117 corpus is
guaranteed to produce nothing. The one place the paper touches its own measured data with its own
new method, the method returns the null by construction.

### F6. The kill criteria cannot fire; they are pre-registration theatre.
Stated kill: "less than 5% distortion throughout." Already falsified by the table above (1.07–2.58,
i.e. +7% to +158%) before a single FLORES sentence is downloaded. Stated headline threshold:
"median absolute distortion ≥10% in two scripts or 95th percentile >20%." Guaranteed to pass —
Petrov published up to 15×.

This project's whole moral authority rests on gates that can actually refuse (D-117, the two claim
gates, the refusal log as evidence). Importing that vocabulary onto a threshold whose answer is
already public inverts it. This is the single most damaging thing in the proposal *for the
project*, because it teaches the reader that JouleWise pre-registration is decorative.

### F7. The one quantitative diagnostic offered is uncorroborated and computed on a caricature.
"Across eight existing 512-Qwen-token multilingual controls, OLMo produces 4,540 tokens versus
Qwen2.5's 4,096, or +10.8%. The widest item is 722 versus 512 (+41.0%), while another is 459 versus
512 (−10.4%)." I grepped the repo for `4,540` / `4540` / these ratios: **nothing**. The numbers
have no tracked provenance.

They are also computed on `jw.multiling` synthetic sentinel text
(`joulewise/gensuite/__init__.py:1059,1250`) — programmatically generated function-word blocks with
script-appropriate punctuation. That is a caricature of language. Two consequences: (a) +10.8% is
about an order of magnitude below real matched-text dispersion (my measured 1.07–2.58); (b) the
reported **−10.4% sign reversal** (OLMo producing *fewer* tokens than Qwen) is an artifact of
repeated function words hitting NeoX merges, and does not occur on any of my ten real sentences.
The proposal's "ranking hazard" framing leans on exactly that sign reversal. Its only support is a
generator artifact.

### F8. FLORES is not acquired. The proposal writes as if a session that hasn't happened, has.
`docs/campaign_packs/c5_i_3_flores_fertility.md` header: **"Status: pre-source-session DRAFT."**
Unresolved placeholders: `FLORES_REVISION`, `FLORES_LICENSE`, `ARCHIVE_SHA256`, `SUBSET_ID`,
`LANGUAGE_IDS`, `PAIR_IDS`, `TOKEN_MATCHED_METHOD`, and the 6-vs-8 language count **deferred by
D-046/B6**. The proposal says "the source session's prospectively chosen six or eight FLORES
languages/scripts" — there is no such choice on record. It is a named prerequisite session, unrun,
that the proposal has quietly converted into a completed input.

### F9. Salami-slice risk against P2 (ICPE), which the proposal concedes and then ignores.
It states it reuses draft-v1 §§3–5 "almost intact," reuses the same three windows' results, and is
"not, by itself, enough for an ICPE full-track claim." Under Ed's paper-first stack (P1 MVP, P2
ICPE), that is a P1-schedule desk cost with no P2 payoff, plus a live dual-publication hazard: two
papers, shared method sections, identical results tables. An ICPE PC checks for exactly this.

Also, §§3–5 are **not currently clean for reuse**: the paper-fidelity audit at HEAD
(`docs/process_traces/2026-08-07-night-hardening/AUDIT-PAPER-FIDELITY.md`) found draft-v1 §3 claims
trapezoidal integration while the reducer performs overlap-weighted interval averaging (HEAD commit
message: "paper needs interval-average (not trapezoidal) correction … before advisor review").
Minor, but "reuse §§3–5 intact" is currently false.

---

## Non-fatal: what is already project doctrine, presented as new

Contribution 4 ("a mechanically checkable reporting rule") is largely **ratified JouleWise contract
since 2026-07-09**. `docs/contracts/token_normalization.md` already binds: gross request energy is
PRIMARY; J/token is "tokenizer-scoped companion" and "never a tokenizer-blind work unit";
runtime-observed denominators; tokenizer name/revision/class/vocab named wherever a per-token
number appears; co-display at equal-or-greater salience (D-033/D-037/D-052/D-053). The FLORES pack
already **pins now**: "Required companion denominators: J/char, J/byte, and semantic-pair IDs" and
the ceiling "no tokenizer efficiency ranking without semantic and token-matched legs."

And `docs/paper/draft-v1.md:11` — the MVP paper's *scope statement* — already reads: "Joules per
prompt or output token are tokenizer-scoped companion metrics and are never treated as
tokenizer-independent work units."

The paper's central normative claim is already in the MVP paper. The proposal's own token-matched
control leg is a pack requirement, presented as a design choice. What is genuinely new in
Contribution 4 is only *mechanical enforcement* — which is a tool, not a finding.

---

## Scores, with reasoning

**Novelty — 2/10.** Contribution 1 is a subset of Petrov 2023's released dataset. Contribution 2 is
an identity. Contribution 3 is the MVP paper's result relabelled. Contribution 4 is the project's
own 2026-07-09 contract plus a linter. The two points are for the linter and for the honesty of the
"forbid the causal sentence" fence, which is genuinely good discipline.

**Feasibility — 9/10.** The highest score in this portfolio, and deservedly. Zero incremental
nights. Tokenizer artifacts verified present. `response_text` retained. No frozen-boundary
violation. Only real risk is F8 (FLORES acquisition), and Petrov's published length tables are a
fallback. Docked one point because the desk stream (auditor + reducer + validator) lands squarely
on the P1 critical path, which is currently the D-117 desk freeze — window plans, generalized mint
pinsets, extraction specs, synthetic integration regression. Not free.

**MVP leverage — 5/10.** Bimodal. As **§7 of the MVP paper**: 8 — it costs nothing, it sharpens the
existing scope statement into a measured one, and it makes the shared-tokenizer gamma contrast look
deliberate rather than lucky. As a **separate paper**: 3 — it leverages the MVP by *duplicating*
it, and creates F9. Averaged, 5. The proposal itself writes "Section 7 becomes a tokenizer-honesty
evaluation," which is the correct instinct pointing at the wrong deliverable.

**Venue fit — 3/10.** Capstone chapter: fine. EuroMLSys / HotCarbon / ICPE-WiP: the Petrov+Ahia
collision is disqualifying for the headline as written; the first reviewer question is "what is new
beyond Petrov 2023?" and the honest answer is "we relabel dollars as joules but do not measure it."
HotCarbon additionally wants a carbon argument this does not make. ICPE full track: disclaimed by
the proposal.

**Original goals — 5/10.** Genuinely serves the **energy-honest leaderboard/reporting critique**,
which is a real Ed axis, and the normalization discipline is a true prerequisite for later
mechanism work. Serves **zero** mechanism axes — no spec decode, no MTP, no MoE routing, no
KV/attention, no split inference. The proposal says so plainly, which earns it points for honesty
and costs it points on the axis.

---

## Three strengthening moves, if kept

### M1 — Buy the paper an actual measurement: the ranking flip, on one added night.
This is the move that converts a tokenization note into an energy paper, and it is available on
**owned hardware with already-proven harness support**.

Add a fourth window: matched-content decode contrast, **Qwen2.5-1.5B vs OLMo-1B / OLMoE-1B-7B**, on
a frozen non-Latin-script prompt set (Korean, Chinese, Thai — my table shows 2.5×+ OLMo inflation
there), budgeted by **characters or bytes, not tokens**, with gross J/request primary. Then show,
with real joules and both claim gates, that **J/output-token ranks the two stacks in one direction
while J/request-for-identical-semantic-content ranks them in the other.** That is a measured
ranking flip. It is the thing Petrov could not do and Ahia approximated with API prices.

Feasibility is not speculative: OLMoE-1B-7B has already run on this harness
(`docs/process_traces/2026-07-17-exploratory-block/results.md`, three reps, 229.028 ± 2.445 J), and
the exploratory OLMoE-vs-Qwen3-4B gross gap was **133.720 J — 5.43× the guard then, ~27× the 5 J
bar**. Effects are enormous; sizing is not the risk.

The confound is real and must be owned in the title, not buried: OLMoE is BF16, Qwen is INT4;
architectures differ. So the estimand is **"as-shipped stacks," not "tokenizer holding model
fixed"** — which is precisely the unit a leaderboard reports, and therefore precisely the unit whose
distortion matters. State that the study identifies *reporting* distortion between deployable
stacks and explicitly does not decompose tokenizer from architecture. Now the kill criterion is
real: if no script exhibits a flip region, the paper refuses, and the refusal is a result.

Cost: one added quiet night (~2.5–3 h) + a matched-content-budget workload generator. Verify first
whether an INT4 OLMo conversion is available to reduce the quantization confound.

### M2 — Fix the roster, retire the synthetic corpus, drop the D-117 cross-tokenization leg.
(a) Three artifacts is two tokenizers — Qwen3 ≡ Qwen2.5 (measured 1.00 across nine scripts) and
OLMo-1B ≡ OLMoE. Either add genuinely distinct locally-obtainable tokenizers (Llama-3 128k,
Gemma 256k, Mistral 32k, plus a byte-level control) or state N=2 and shrink the claim accordingly.
(b) Delete the `jw.multiling` synthetic diagnostic from the evidence base. It understates real
dispersion by ~an order of magnitude and manufactures the −10.4% sign reversal the "ranking hazard"
framing leans on. Replace with real matched text.
(c) Drop the "cross-tokenize the D-117 prompts and outputs" leg entirely. English, ratio 1.00,
guaranteed null. Spending desk time on it and reporting the null as a finding would be worse than
not doing it.
(d) Add the related-work paragraph the proposal has no version of, leading with Petrov NeurIPS 2023
and Ahia EMNLP 2023, and stating the delta in one sentence you are willing to defend.

### M3 — If M1 is not funded, demote to §7 + ship the validator as the artifact.
Do not write this as a standalone paper. Land it as MVP §7 (~1.5 pages: the identity as a
one-line remark, my table's real-text dispersion as one figure, the shared-tokenizer note that
makes gamma's design legible) and put the *new* contribution where it is actually new: a released,
mechanically enforcing **report validator** that refuses any cross-stack J/token comparison lacking
gross J/request at equal salience, tokenizer artifact digest, runtime-observed denominator
provenance, and J/byte + J/char — i.e. `docs/contracts/token_normalization.md` compiled into a
checker.

Then add the one thing nobody has done: **run it over published LLM-energy leaderboards and
benchmarks** (ML.ENERGY, Silicon Showdown, TokenPowerBench, Intelligence-per-Watt) and report which
of their comparisons it refuses and why. That is an artifact/tool contribution with a real,
falsifiable empirical result attached, it costs zero nights, it does not collide with Petrov, and
it is exactly Ed's energy-honest-reporting axis. It is also a much better fit for an ICPE artifact
or tool track than the current framing is for anything.

---

## Bottom line

The proposal's greatest virtue — it needs no new measurement — is also the proof of its central
defect. A paper about energy reporting that measures no energy attributable to its own thesis, on a
project whose only contrast is tokenizer-identical by construction, is a tokenization note with the
MVP paper's method sections stapled to the front. Fund **M1** and it becomes a real, modest,
defensible energy paper with a measured ranking flip. Fund **M3** and it becomes a good section
plus a genuinely useful tool. Fund it as written and Ed spends P1 desk time reproducing a 2023
NeurIPS result at 1% scale, with a pre-registered threshold whose answer he already knows.

2026-08-07T16:52:52.471812Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "sed -n '1,330p' ../portfolio/rev-wall-meter-validation.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Counter-review: "Calibrating the Calibrator: External Validation of `powermetrics`"

**Reviewer:** Opus 5 counter-reviewer (adversarial charge: kill it)
**Target:** `scratchpad/portfolio/prop-wall-meter-validation.md`
**Ground truth checked against:** desk checkout at main — `docs/paper/draft-v1.md`,
`docs/decision_log.md` (D-092 §5676, D-117 tail), `docs/strategy/2026-08-06-impressiveness-roadmap.md`,
`docs/campaign_packs/q6_c5_2_10_rail_vs_wall.md`, `TASK_QUEUE.md` A26/P2-048,
`docs/paper/related_work_draft.md`, `docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`.

## Verdict: **WEAK**

Scores (1–10):

| axis | score |
|---|---|
| novelty | 4 |
| feasibility | 4 |
| mvp_leverage | 5 |
| venue_fit | 5 |
| original_goals | 3 |

The *work item* survives — C8 is ratified (D-092), the Q6/D-018 bridge design exists,
and the bibliography gap is real. The *paper proposal* does not. It is not a paper; it
is a revision to §6 of the paper Ed is already writing, wrapped in a title that promises
a result the apparatus cannot produce.

---

## Fatal flaws

### F1. The headline claim is not identifiable on this apparatus. (fatal to the framing)

The thesis says the study can "determine whether `powermetrics` preserves the absolute
gain … of whole-request LLM energy." It cannot. Paired idle/active differencing removes
the constant terms, leaving

    ΔE_wall ≈ [ ΔE_SoC·(1+ε_pm) + ΔE_DRAM + ΔE_fan + ΔE_other ] / η(P) ± ΔE_battery

where ε_pm is the counter bias the paper claims to measure. A single wall meter yields
one number, β, that is a *product* of counter bias, the non-SoC incremental power tree,
and the charger efficiency curve. β = 1.3 is equally consistent with "`powermetrics` is
perfect and the rest of the laptop costs 30%" and with "`powermetrics` under-reports by
25%." Nothing in the design separates them — a sealed MacBook offers no SoC-rail DC tap,
which is precisely the affordance Desrochers-class RAPL validations had and this one does
not. The proposal is admirably explicit that wall agreement cannot validate the *phase
split*; it is silent on the fact that it cannot validate the *total gain* either. That
silence is the flaw, because the title, the thesis sentence, and Contribution 1 all rest
on it.

Corollary, and this one Rivoire will circle in red: Contribution 1's acceptance gate —
held-out residual ≤ max(floor, 5% of ΔE_wall) — tests **linearity and stability of a
fitted mapping, never accuracy**, because α and β are fit from the data. A clean 5%
held-out pass is fully compatible with `powermetrics` being 30% wrong. Calling that
"whole-request gain validation" is a category error printed in the contributions list.

### F2. Two of four contributions are already in `draft-v1.md`, unmeasured.

- Contribution 4 ("matching totals is compatible with energy redistributed between
  phases") is **already written**, verbatim in substance, at `draft-v1.md:180` and
  `related_work_draft.md:15`, sourced to [JayOstapenco]. It requires zero measurement,
  zero meter, and zero nights. It is not a contribution; it is a paragraph that exists.
- Contribution 2 (load-dependent rather than constant gap) is the **published headline
  finding of Jay/Ostapenco**, already cited in the draft as such. Replicating it on Apple
  silicon is a platform note, not a finding.

That leaves Contribution 1 (not identifiable, F1) and Contribution 3 (the boundary
conclusion-flip test on the 1.5B-vs-7B contrast). Contribution 3 is the one genuinely
new, genuinely MVP-relevant item in the proposal — and it is already predeclared in
`docs/campaign_packs/q6_c5_2_10_rail_vs_wall.md` as the frozen conclusion-flip test. So
the proposal's four contributions reduce to one, and that one was designed a month ago.

### F3. Fan hysteresis will manufacture Contribution 2 as an artifact.

The design is four output-length levels (128/512/1024/2048 tokens) and reads
slope/residual structure across them as evidence of load-dependent counter gain. On an
M3 Max MacBook Pro, longer sustained decode means higher sustained die temperature means
higher fan RPM — a non-SoC load of order several watts (uncertain; must be measured),
**thermally lagged by tens of seconds to minutes and therefore hysteretic in run order,
not a function of instantaneous load**. That term rises monotonically with output length.
It will appear as ΔE_wall superlinear in ΔE_SoC, i.e. exactly the signature the paper is
built to report as "load-dependent `powermetrics` gain." The proposal has no fan-RPM
covariate, no display-state control, no thermal-state admission term, and no cooldown
accounting in the described blocks. Counterbalancing level order does not fix a
hysteretic term; it smears it into residual structure, which then trips the 5% gate for
the wrong reason. The same confound contaminates Contribution 3: 7B runs longer and
hotter than 1.5B, so a boundary "flip" is the *expected* result from fans alone and
would say nothing about the counter.

### F4. The battery term is unbounded and is 5–10× the signal.

The proposal's own planning value is ~51 J for a 1.5B decode. A residual battery
charge/discharge flux of ±5 W over a 60 s block is ±300 J. "Charge-neutral, recorded
battery observations" is the right instinct, but no mechanism is proposed that resolves
the battery term to the ~1 J scale this instrument works at. macOS optimized charging,
periodic top-off cycles, and Apple-silicon burst draw supplemented from the cell are all
live. This is checkable at a bench in an afternoon **with no meter**, and it is not in
the plan — it sits downstream of "borrow the WT310E."

### F5. Venue/location conflict with the quiet-window protocol — unaddressed.

A borrowed, in-calibration WT310E plus a mains-voltage inline fixture from a university
lab will plausibly have to be operated *in that lab*, or under supervision. The JouleWise
claim window requires a controlled quiet environment, zero background activity, 2–4 hours,
operator bookends, and thermal/environmental admission gates — and environmental
contamination is this project's single most expensive historical failure mode (the
Ventura screensaver episode; "another environmental refusal" is the named risk in the
roadmap's rank-1 row). The proposal never states where the confirmatory window happens.
If the meter cannot come to the instrumented unit under the standard gates, the
wall-validation window is not admissible under the same regime as the D-117 windows and
the comparison loses its warrant. This is a scheduling/logistics question with a binary
answer that has not been asked.

### F6. Cost is understated ~2× on nights and omits calendar entirely.

The proposal's headline cost is "one non-claim pilot plus one new 2–4 h quiet window."
The repo's own strategy doc rates this expansion at **4–8 weeks, 1 pilot plus 1
confirmatory session**, and the desk list the proposal itself enumerates — importer, raw
schema, meter-metadata/calibration binding, sync residual, fixed-range uncertainty,
paired reducer, held-out regression, refusal reasons, corrupt-trace tests, hash-bound
custody — is *a second instrument's entire calibration-acceptance regime*. Note that
P2-048 is **SHELVED** in `TASK_QUEUE.md` and the Q6 pack is an explicit "pre-hardware
DRAFT … not frozen until the boundary-pair hardware and calibration manifest are known."
"Already-designed" is honest about the design contract but understates the build. Given
this repo's delivery record on comparable machinery (D-079 issuance: multiple PRs, two
cold gates, a full C-028 gauntlet), realistic cost is 5–9 weeks wall-clock, 2–3 nights
including one contingency, contending directly with P1.

### F7. It is not a paper.

The proposal's own venue section says: reuse MVP §§1–5 almost intact, reuse the D-117
result structure, reuse related work, "add … a paired wall/SoC figure," "do not rewrite
the paper as a generic power-meter benchmark." That is a description of a section edit.
In a 20-direction portfolio it duplicates `prop-mvp-icpe-upgrade` rather than competing
with it.

## Does it answer a question the MVP needs answered? No.

The MVP's claims are *same-boundary* contrasts under a declared floor. A multiplicative
gain error cancels in a ratio and merely scales a difference; `draft-v1.md:11` already
fences this explicitly and honestly ("absolute values remain internal to the named
`powermetrics` SoC boundary; same-boundary contrasts can still be scientifically useful").
`draft-v1.md:36` goes further and makes the *absence* of the wall meter part of the stated
gap. C8 is a reviewer-comfort item, not a soundness item. The one exception is
Contribution 3 — but see F3.

## On the bibliography finding (no published `powermetrics` validation)

It opens less than it looks. Consider *why* the gap exists: the standard RAPL-validation
recipe (Khan/Desrochers/Jay/Ostapenco) works on machines where you can meter the wall
**and** tap the rails, so ε_pm is identifiable. On a sealed, battery-buffered, actively
cooled laptop it is not (F1). A paper that runs the recipe anyway does not fill the gap;
it publishes a transfer function for one MacBook's power tree and labels it validation.
The empty shelf is partly evidence that the well-posed version of this experiment needs
apparatus Ed does not have. Novelty = platform only, and the platform is the reason the
result is weaker than its lineage.

## Original goals: 3/10

The proposal concedes it studies no mechanism axis — no spec decode, MTP, MoE, KDA, KV.
Its claimed service to the "energy-honest reporting / leaderboard-critique" axis is real
but indirect, and its claimed foundation for split inference is thin: split work needs
*two* meters (RUN_STATE is explicit) and a cross-device clock bound, neither delivered here.

## Credit where due

The single best judgment in the proposal is refusing to attach an uncharacterized meter
path to the frozen D-117 windows, and sequencing C8 strictly after they close. That
protects P1 and should be preserved in any surviving version. The kill-criteria section
is also genuinely well-formed — it is simply pointed at the wrong risks (calibration
certificate, fixture) rather than the ones that will actually end it (F1, F3, F4, F5).

---

## Three strengthening moves, if kept

1. **Re-scope to what is identifiable, and re-title.** Kill "validation of `powermetrics`"
   from the title, thesis, and Contribution 1. The honest, defensible object is *the
   AC-to-SoC boundary transfer function for one named stack* — how much energy the machine
   draws that the SoC counter never sees, and whether that fraction is stable across load.
   Then actually attempt the decomposition instead of black-boxing β: log fan RPM (SMC
   sampler) as a modelled covariate, fix display state, and report an explicit
   identifiability limitation stating that one wall meter plus one SoC counter cannot
   separate counter bias from the power tree. This converts a claim reviewers will reject
   into one they will accept — and it is the version that honestly fills the empty shelf.

2. **Move the two owner-controlled kill gates in front of the borrow.** Both need zero
   meter and zero advisor coordination: (a) **battery-flux bound** — log SMC battery
   current/voltage at maximum cadence through a representative quiet decode block and
   demonstrate the net battery term over a block is bounded well below the smallest cell's
   signal; kill on failure. (b) **fan/thermal confound** — log fan RPM across the four
   length levels and show fan power does not correlate with level, or bound it with a
   forced-fan control arm; kill or redesign on failure. One afternoon at the bench can end
   this direction before a single lab-coordination email, and F4/F3 are more likely to kill
   it than the calibration certificate is.

3. **Redesign the cells for the AC side's time constants, and settle the venue up front.**
   Drop the 128-token cell — at ~1–2 s it is below the charger input capacitance, battery
   buffering, and the meter's 100 ms update interval, and cannot be integrated cleanly.
   Promote the sustained repeated-request 60–120 s blocks from fallback to *primary*
   design (they raise the signal without touching the frozen single-request boundary).
   Make "the meter physically comes to the instrumented unit, under the standard admission
   gates" a **precondition negotiated before the borrow**, not a discovery afterward; if
   the fixture cannot leave the lab, that is a pre-borrow kill. Keep the boundary
   conclusion-flip test on the 1.5B-vs-7B contrast as the single headline result — with
   fans modelled — because it is the only contribution the MVP actually consumes.

2026-08-07T16:52:55.388351Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
codex
All 24 counter-reviews are now read. The reviewers’ “only two VIABLE” summary checks out, but the raw scores alone are misleading: the portfolio contains several worthwhile riders and pre-night gates that should be funded even though their parent paper should be killed. I’m now reading the primary proposals only for the close ranking calls and cost schedules.
Completed governing-state intake and all 24 full counter-reviews; moving to the primary-text tie-breakers.
  ✓ Read project controls, D-117/design memo, and inventory the 24 proposal/review pairs
  ✓ Read all 24 counter-reviews first and extract verdicts, scores, costs, kill gates, and salvage
  → Read proposals selectively to resolve ranking, sequencing, and cost ambiguities
  • Synthesize ranked portfolio, paper arc, synergy map, second-paper bet, and Ed rulings
exec
/bin/zsh -lc 'for f in ../portfolio/prop-quantization-ladder.md ../portfolio/prop-moe-routing-energy.md ../portfolio/prop-mvp-icpe-upgrade.md ../portfolio/prop-spec-decode-energy.md; do echo "FILE $f"; tail -n 220 "$f"; done' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
FILE ../portfolio/prop-quantization-ladder.md
| 2 | Spec decode on/off (7B+0.5B) | ±10–30% → Δ≈0.04–0.11 J/tok | ×2048 ≈ **80–230 J** | **~6–16×** |
| 3 | MoE vs dense matched-active | +30–100% of ~0.1–0.15 J/tok dense | ×2048 ≈ **60–300 J** | **~5–20×** |
| 4 | KV-quant 4b vs fp16, long ctx | Qwen2.5-7B KV ≈57 KB/tok fp16 → ~9.6% of decode bandwidth at 8k ctx; save ~75% of it ≈ 3.5% avg over 0→8k | ×8192 ≈ **~100 J** (concentrated late — phase resolution helps) | **~7×** at full 8k; marginal below 4k |
| 5 | Hybrid-linear vs full-attn: J/tok-vs-context slope | GQA slope from KV reads; linear ~flat; tens of % at 16–32k ctx | context-sweep design, per-point Δ ≥ 50–100 J | ~5–10× (**runtime risk**) |
| 6 | MoE top-k slope (same weights) | expert-FFN energy ~∝ k; maybe 20–40% of J/tok | ×2048 ≈ 100–250 J | ~10× (**mechanism knob unverified**) |
| — | MTP | — | — | **unreachable** (no runtime) |

All effect estimates except row 1's bandwidth scaling are extrapolations from server-class literature — flagged as such; that gap is the point.

## (iv) What each claim says that the literature can't

1. **Spec decode**: "On batch-1 unified-memory inference, speculative decoding changes decode energy by X% ± CI" — first *measured* on-device energy verdict incl. the **sign** (all lit is server GPU batch sweeps; mlx overhead could plausibly flip it — issue #250 hints the spec-decode step is slower).
2. **Quantization**: CI-bounded J/token-vs-bits curve on Apple silicon, adjudicating the q4>q8 anomaly the edge literature reports without error bars.
3. **MoE**: whether the +54% matched-active GPU penalty survives unified memory, phase-resolved — direct extension of 2606.21428 (M2 Pro, one pair, coarse) with the sign-flip (matched-active vs matched-total) pinned down on one instrument.
4. **KV quant**: the first measured energy number of any kind — lit has only memory/latency.
5. **Attention slope**: on-device d(J/tok)/d(context) for hybrid-delta vs full attention — 2605.11999 is H200-only and whole-request.

## Top-3 recommended first campaigns

1. **Speculative decoding on/off (Qwen2.5-0.5B→7B, models already characterized)** — cleanest single-mechanism ABBA in existence (identical target weights, flag-toggled), verified runtime, open sign question, 6–16× floor clearance.
2. **Weight-quant ladder (Qwen 7B/8B at 4/8/16-bit)** — 35–50× floor clearance, checkpoints trivially available, and it calibrates the bytes-moved→joules model every other campaign's predictions rest on.
3. **MoE vs dense matched-active (Qwen3-30B-A3B vs Qwen3-4B, plus the OLMoE/OLMo-2 lit-replication pair)** — settles the matched-active vs matched-total sign flip on unified memory and directly extends the only existing Apple-silicon result.

Sources: [2605.11999](https://arxiv.org/abs/2605.11999) · [2504.17674](https://arxiv.org/abs/2504.17674) · [2606.21428](https://arxiv.org/abs/2606.21428) · [2411.13157](https://arxiv.org/abs/2411.13157) · [2510.26692](https://arxiv.org/abs/2510.26692) · [2601.22076](https://arxiv.org/html/2601.22076v1) · [2512.03024](https://arxiv.org/html/2512.03024v1) · [2504.03360](https://arxiv.org/pdf/2504.03360) · [2401.18079](https://arxiv.org/pdf/2401.18079) · [2405.06219](https://arxiv.org/pdf/2405.06219) · [mlx-lm models](https://github.com/ml-explore/mlx-lm/tree/main/mlx_lm/models) · [mlx-lm #250](https://github.com/ml-explore/mlx-lm/issues/250) · [mlx-lm #1132](https://github.com/ml-explore/mlx-lm/issues/1132) · [mlx-examples #1075](https://github.com/ml-explore/mlx-examples/commit/85ffd2c96a45a8cb900f95a2ded61d858d673399)## D-070: Architectural-axes extension agenda (AXI): scope, claim posture, batch-axis rulings

- Date: 2026-07-14 (Ed-directed; provenance `docs/axi-handoff.md`
  §1.1/§4/§5 plus Ed's rulings recorded this session)
- Status: accepted (C-033 coherence-reviewed)
- Phase: Phase 2+ research program

Decision:

1. **Agenda.** Once the harness works, it must be able to characterize
   architectural inference features generally — static batching,
   speculative decoding / MTP, MoE vs dense, quantization, and
   reasoning-length variance — framed as stress tests of the single Q4
   thesis (E = fixed + coefficients·work), not five new theses.
2. **Claim posture.** Instrument support (L0 smoke bundles) for ALL
   axes. Ed ruling 2026-07-14 (supersedes the handoff's narrower
   default): ALL five axes get characterized-claim commitments with
   dedicated quiet-Mac hardware time — it is Ed's own hardware and Ed
   wants maximum axis flexibility. Sequencing and floor discipline are
   unchanged: every AP remains floor-gated on P2-015 floors,
   `TASK_QUEUE.md` remains the ordering authority, Window A outranks
   everything, and no AXI stream consumes a [QUIET-MAC] window until
   Window A completes.
3. **Batch axis (Ed ruling).** STATIC batching only for the capstone:
   AP-BATCH covers B ∈ {1,2,4,8,16} static dispatch. Continuous
   batching is DEFERRED as a post-capstone, NV-gated extension — not
   killed. BINDING continuous-ready design constraint so the deferral
   stays additive rather than rework: all batch-related event schema is
   **request-scoped, not run-scoped** — token and phase events carry a
   `request_id`; each request gets its own lifecycle envelope
   (submit/prefill/decode/complete) even though static runs happen to
   synchronize them; no schema assumption that all sequences share one
   prefill boundary or one decode window. The reducer MAY exploit
   synchronization for static-mode metrics but MUST NOT require it at
   the schema level. Schema placement pin: `request_id` lives in event
   `metadata` (`events.jsonl` `metadata.request_id`) — the five-key
   event contract gains no sixth top-level key. Request-grouped
   lifecycle/phase pairing is NEW-version reducer dispatch, purely
   additive; legacy arms stay frozen and no existing bundle is
   re-dispatched (D-066 clause 2). Rationale: a single model instance
   with B KV
   caches is memory-feasible on current hardware; only the serving
   scheduler is hardware-gated, so a future continuous stream (load
   generator, steady-state detection, energy-per-token-at-offered-load
   metric) becomes purely additive on top.
4. **Registry.** Existing rows already carry the axes — the C5-* rows
   live in `docs/research_question_bank.md`; the C-023-* and RQ-* rows
   live in `docs/research_question_registry.md` (D-055): C5-2.2 and
   C5-2.6 (batching), C5-2.5 + C-023-OUTPUT-IDENTITY (spec decode),
   C5-1.1 / C5-1.9 / RQ-TWO-MODEL-ACTIVE-NONCLAIM (MoE/dense), C5-1.12
   + C-023-QUALITY-EQUIV-QUANT (quantization), RQ-ENERGY-VARIANCE +
   C5-W.2 (reasoning variance). Two new rows to mint at their gates:
   a **Mac-batching leg of C5-2.2** (minted ONLY on an S-B `supported`
   verdict), and **MOE×BATCH** (candidate, ceiling L2, forbidden
   upgrade: no MoE-serving-efficiency generalization from one pair).
5. **Ceilings.** Everything caps at L2 (L3 only through Q4/AP-1's
   existing holdout machinery); ceilings move only via replication rows
   (C5-3.1). No live claims from fixture-first code; PROVISIONAL until
   first live hardware contact.

Options considered: (a) five independent theses — rejected (dilutes
Q4 and is unfundable in the timeline); (b) axes as Q4 stress tests
with narrow claim commitments (the handoff default: MoE/dense +
batching only) — superseded by Ed's ruling; (c) axes as Q4 stress
tests with all-axes commitment — chosen by Ed.

Open item: the D-016 matched dense/MoE model pair remains with Ed and
the advisor; stream S-D presents the proposal (same family, matched
active params; fallback matched total) — do not finalize unilaterally.

Revisit triggers: an S-B `unsupported` verdict removes the Mac-batching
leg (the dated negative verdict is filed as a finding, Hailo idiom);
measured P2-015 floors that make a predeclared AXI effect size
undetectable send that AP back for redesign before any campaign is
scheduled.

## D-071: G10 memory-fit rule ratified (axi-sd-memory-fit-shape-v1); device-list review opened

codex
# Quantization Under the Floor: Which Precision Rungs Are Measurably Different on Apple Silicon?

**Thesis:** On one frozen M3 Max/MLX/Qwen2.5 stack, lower weight precision is not automatically more energy-efficient: rung-specific detection floors and quality gates determine whether 4-, 5-, 6-, and 8-bit variants can be ranked, traded off, or only reported as unresolved.

## Project brief and steps

JouleWise already has the scientific core of this paper: an in-window calibrated `powermetrics` instrument; an attribution-limited finding of roughly 1 J per phase member; LABELLED floors composed from repeatability, worst-case edge placement, and never-zero drift; separate floor-clearance and interval-direction gates; and a fail-closed protocol with pre-registration, admission checks, counterbalancing, hash-bound custody, and published refusals. No claim-bearing numbers currently exist: historical values are diagnostic only. D-117 therefore requires three fresh prospective windows—1.5B decode floor, 7B decode floor, and 1.5B-versus-7B decode contrast—with prefill floors riding the first two. Before those nights, the two-slot live-calibration ledger, D-102 successor path, multi-cell mint, frozen plans, extraction specifications, and synthetic regressions must land. Those three approximately 2.8–3.25-hour windows then mint four phase-floor cells and the model-size contrast, after which the existing draft can be populated.

This paper keeps that spine intact and adds a conditional four-window extension on the owned Mac. The subject is Qwen2.5-1.5B-Instruct because its 4-bit condition and exact 128-prompt/512-output workload already occur in D-117. From one frozen BF16 source revision, derive affine group-64 Q4/Q5/Q6/Q8 artifacts with identical converter, module allowlist, tokenizer, runtime, and sampling policy. Run the existing 256-item, four-stratum quality screen outside quiet time, using BF16 only as the quality reference. Then collect separate Q5, Q6, and Q8 decode-plus-prefill floor windows; the D-117 Q4 floor supplies the fourth rung. Finally, run one 48-member, 12-block balanced four-arm contrast window. Total funding request: the three D-117 nights plus **four extension nights**, approximately **12–15 additional quiet-machine hours [estimate]**, with no new apparatus.

## Contributions

1. **A rung-specific resolvability map.** For each quantization, mint separate decode and prefill floors; falsified if any planned cell cannot pass its calibration, custody, or floor-mint gates.

2. **A prospective Q4/Q5/Q6/Q8 phase-energy ladder.** Test the three adjacent decode contrasts—Q4–Q5, Q5–Q6, Q6–Q8—with Holm-controlled, two-sided intervals; any failed gate yields `not_resolvable`, not equality.

3. **Quality-qualified energy conclusions.** A rung is called quality-equivalent only if its frozen 256-item comparison against BF16 passes both the greater-than −2 percentage-point overall bound and the no-worse-than −5-point per-stratum rule. Otherwise it becomes a descriptive quality–energy trade-off.

4. **Power-versus-time decomposition.** For every resolvable contrast, report whether the observed energy difference is associated with mean power, duration, or both, using the exact symmetric decomposition already specified by C5-1.12—without causal kernel attribution.

## Experiment plan

The primary energy workload remains D-117’s exact 128/512 single-request profile, preserving the Q4 floor’s applicability. Q5, Q6, and Q8 each receive a 50-member floor window: 10 absolute members and ten four-member null blocks, plus NEG8, start/mid/end references, and live calibration bookends. Prefill is a preregistered rider over the same members.

The contrast window uses 12 balanced Williams-style blocks, each containing one request from every rung; its 48 members preserve sequential batch-one execution. Primary contrasts are adjacent rungs; Q4–Q8 is secondary. This needs multi-arm counterbalancing and block analysis, but does **not** violate the frozen single-request boundary.

Sizing is uncertain. The repo’s non-claim diagnostic is about **0.098 J/decode token** for 1.5B Q4, or roughly **50 J at 512 tokens**. An official MLX benchmark on a different Qwen model and M4 Max reports adjacent generation-throughput differences of roughly 10–17%; at comparable power, that suggests approximately **4–10 J [high-uncertainty estimate]** per adjacent 512-token contrast, with Q5–Q6 the most likely miss. Q4–Q8 should be materially larger. These estimates are extrapolations, not priors to select results; the official data also show that bit width changes quality and performance nonlinearly. [MLX benchmark table](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/BENCHMARKS.md)

Short 128-token prefill differences probably will not clear the approximately 5 J practical bar. That refusal would mean “this instrument cannot rank these prefill rungs at this workload,” not “quantization has no prefill effect.” If decode also fails, workload length—not repetitions—is the permitted redesign lever, but only in a new preregistered campaign with matching floors.

Desk work comprises reproducible conversion and dual-mirror hashing; load/memory/token-identity smokes; the quality screen; AP-QUANT and multiplicity freeze; three floor packs; the multi-arm manifest and estimator; multi-quant floor minting; synthetic refusal regressions; and quality–energy figures. Current MLX conversion exposes integer bit width, while public 4/5/6/8 benchmarks establish discovery feasibility; local support on the pinned JouleWise versions remains a required smoke gate. [MLX conversion implementation](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/convert.py)

## Hardware and instrument

Required: the owned 128 GB M3 Max, pinned MLX environment, local immutable model mirrors, and existing `powermetrics` instrumentation. The RTX 3080 Ti and Jetsons are out of scope. **WT310E dependency: no.** A borrowed wall meter would strengthen absolute whole-system validation but cannot validate prefill/decode attribution and should not gate this paper.

## Venue and relationship to the MVP

This is a strong capstone/CSCSU chapter and a credible EuroMLSys, HotCarbon, or ICPE Emerging-paper extension. For an ICPE full paper, combine it with an artifact-quality release and preferably wall validation or second-unit replication.

It reuses the MVP draft’s introduction, related-work gap, calibration method, floor composition, fail-closed protocol, attribution-limited result, and D-117 model-size demonstration. New material is the quality gate, quantization-specific floors, multi-arm design, power/time decomposition, and a figure showing which rungs the instrument resolves or refuses.

## Risks and kill criteria

Kill or shrink before spending a night if:

- pinned MLX cannot reproducibly convert and load uniform Q5 or Q6 with the same module recipe;
- artifacts differ in anything beyond declared bit width;
- a daytime timing smoke predicts two adjacent effects remain below 5 J even at the longest affordable frozen workload;
- the multi-arm window cannot fit under four hours with 20% margin;
- phase-floor transport or the multi-arm estimator cannot be frozen fail-closed; or
- fewer than two quantized levels pass quality and Ed does not want a trade-off paper.

If Q5 fails capability before freeze, shrink honestly to Q4/Q6/Q8; do not substitute an unrelated community artifact.

## Relation to Ed’s original goals

This directly serves the original **quantization** and energy-honest quality-plus-latency-plus-energy axes. It also demonstrates the modular harness’s intended model/technique/workload swapping. It does not advance MTP, MoE routing, KV variants, or split inference, but supplies the disciplined comparison template those mechanisms will need.
tokens used
217,966
# Quantization Under the Floor: Which Precision Rungs Are Measurably Different on Apple Silicon?

**Thesis:** On one frozen M3 Max/MLX/Qwen2.5 stack, lower weight precision is not automatically more energy-efficient: rung-specific detection floors and quality gates determine whether 4-, 5-, 6-, and 8-bit variants can be ranked, traded off, or only reported as unresolved.

## Project brief and steps

JouleWise already has the scientific core of this paper: an in-window calibrated `powermetrics` instrument; an attribution-limited finding of roughly 1 J per phase member; LABELLED floors composed from repeatability, worst-case edge placement, and never-zero drift; separate floor-clearance and interval-direction gates; and a fail-closed protocol with pre-registration, admission checks, counterbalancing, hash-bound custody, and published refusals. No claim-bearing numbers currently exist: historical values are diagnostic only. D-117 therefore requires three fresh prospective windows—1.5B decode floor, 7B decode floor, and 1.5B-versus-7B decode contrast—with prefill floors riding the first two. Before those nights, the two-slot live-calibration ledger, D-102 successor path, multi-cell mint, frozen plans, extraction specifications, and synthetic regressions must land. Those three approximately 2.8–3.25-hour windows then mint four phase-floor cells and the model-size contrast, after which the existing draft can be populated.

This paper keeps that spine intact and adds a conditional four-window extension on the owned Mac. The subject is Qwen2.5-1.5B-Instruct because its 4-bit condition and exact 128-prompt/512-output workload already occur in D-117. From one frozen BF16 source revision, derive affine group-64 Q4/Q5/Q6/Q8 artifacts with identical converter, module allowlist, tokenizer, runtime, and sampling policy. Run the existing 256-item, four-stratum quality screen outside quiet time, using BF16 only as the quality reference. Then collect separate Q5, Q6, and Q8 decode-plus-prefill floor windows; the D-117 Q4 floor supplies the fourth rung. Finally, run one 48-member, 12-block balanced four-arm contrast window. Total funding request: the three D-117 nights plus **four extension nights**, approximately **12–15 additional quiet-machine hours [estimate]**, with no new apparatus.

## Contributions

1. **A rung-specific resolvability map.** For each quantization, mint separate decode and prefill floors; falsified if any planned cell cannot pass its calibration, custody, or floor-mint gates.

2. **A prospective Q4/Q5/Q6/Q8 phase-energy ladder.** Test the three adjacent decode contrasts—Q4–Q5, Q5–Q6, Q6–Q8—with Holm-controlled, two-sided intervals; any failed gate yields `not_resolvable`, not equality.

3. **Quality-qualified energy conclusions.** A rung is called quality-equivalent only if its frozen 256-item comparison against BF16 passes both the greater-than −2 percentage-point overall bound and the no-worse-than −5-point per-stratum rule. Otherwise it becomes a descriptive quality–energy trade-off.

4. **Power-versus-time decomposition.** For every resolvable contrast, report whether the observed energy difference is associated with mean power, duration, or both, using the exact symmetric decomposition already specified by C5-1.12—without causal kernel attribution.

## Experiment plan

The primary energy workload remains D-117’s exact 128/512 single-request profile, preserving the Q4 floor’s applicability. Q5, Q6, and Q8 each receive a 50-member floor window: 10 absolute members and ten four-member null blocks, plus NEG8, start/mid/end references, and live calibration bookends. Prefill is a preregistered rider over the same members.

The contrast window uses 12 balanced Williams-style blocks, each containing one request from every rung; its 48 members preserve sequential batch-one execution. Primary contrasts are adjacent rungs; Q4–Q8 is secondary. This needs multi-arm counterbalancing and block analysis, but does **not** violate the frozen single-request boundary.

Sizing is uncertain. The repo’s non-claim diagnostic is about **0.098 J/decode token** for 1.5B Q4, or roughly **50 J at 512 tokens**. An official MLX benchmark on a different Qwen model and M4 Max reports adjacent generation-throughput differences of roughly 10–17%; at comparable power, that suggests approximately **4–10 J [high-uncertainty estimate]** per adjacent 512-token contrast, with Q5–Q6 the most likely miss. Q4–Q8 should be materially larger. These estimates are extrapolations, not priors to select results; the official data also show that bit width changes quality and performance nonlinearly. [MLX benchmark table](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/BENCHMARKS.md)

Short 128-token prefill differences probably will not clear the approximately 5 J practical bar. That refusal would mean “this instrument cannot rank these prefill rungs at this workload,” not “quantization has no prefill effect.” If decode also fails, workload length—not repetitions—is the permitted redesign lever, but only in a new preregistered campaign with matching floors.

Desk work comprises reproducible conversion and dual-mirror hashing; load/memory/token-identity smokes; the quality screen; AP-QUANT and multiplicity freeze; three floor packs; the multi-arm manifest and estimator; multi-quant floor minting; synthetic refusal regressions; and quality–energy figures. Current MLX conversion exposes integer bit width, while public 4/5/6/8 benchmarks establish discovery feasibility; local support on the pinned JouleWise versions remains a required smoke gate. [MLX conversion implementation](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/convert.py)

## Hardware and instrument

Required: the owned 128 GB M3 Max, pinned MLX environment, local immutable model mirrors, and existing `powermetrics` instrumentation. The RTX 3080 Ti and Jetsons are out of scope. **WT310E dependency: no.** A borrowed wall meter would strengthen absolute whole-system validation but cannot validate prefill/decode attribution and should not gate this paper.

## Venue and relationship to the MVP

This is a strong capstone/CSCSU chapter and a credible EuroMLSys, HotCarbon, or ICPE Emerging-paper extension. For an ICPE full paper, combine it with an artifact-quality release and preferably wall validation or second-unit replication.

It reuses the MVP draft’s introduction, related-work gap, calibration method, floor composition, fail-closed protocol, attribution-limited result, and D-117 model-size demonstration. New material is the quality gate, quantization-specific floors, multi-arm design, power/time decomposition, and a figure showing which rungs the instrument resolves or refuses.

## Risks and kill criteria

Kill or shrink before spending a night if:

- pinned MLX cannot reproducibly convert and load uniform Q5 or Q6 with the same module recipe;
- artifacts differ in anything beyond declared bit width;
- a daytime timing smoke predicts two adjacent effects remain below 5 J even at the longest affordable frozen workload;
- the multi-arm window cannot fit under four hours with 20% margin;
- phase-floor transport or the multi-arm estimator cannot be frozen fail-closed; or
- fewer than two quantized levels pass quality and Ed does not want a trade-off paper.

If Q5 fails capability before freeze, shrink honestly to Q4/Q6/Q8; do not substitute an unrelated community artifact.

## Relation to Ed’s original goals

This directly serves the original **quantization** and energy-honest quality-plus-latency-plus-energy axes. It also demonstrates the modular harness’s intended model/technique/workload swapping. It does not advance MTP, MoE routing, KV variants, or split inference, but supplies the disciplined comparison template those mechanisms will need.
FILE ../portfolio/prop-moe-routing-energy.md
  this local configuration is part of the observation's identity. Source:
  [OLMoE config](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r1/config.json).
- **Evidence ceiling.** All nine bundles are strict-valid and
  `collection=usable`, but all nine are `claim_evidence_classification=flagged`.
  Universal families include clock/cadence/short-window flags; OLMoE r2 and
  Qwen3.5 r2 also hit a cooldown cap, and OLMoE r3 carries additional
  interpolation/nonpositive-short-window flags. The three retained campaign
  verdicts say claim readiness was not assessed. Source:
  [campaign log](../../../runs/exploratory_2026_07_17/campaign_log.jsonl).
- **Throughput is descriptive.** Tok/s is runtime-observed output throughput
  for these exact artifacts, prompts, fixed output budget, and warm-cache
  sequence. It is not a hardware, architecture, or serving benchmark ranking.

## Verification

The extraction read only retained artifacts. The nine-bundle strict replay was:

```bash
for bundle in runs/exploratory_2026_07_17/exploratory-*__r?; do
  .venv/bin/python -m joulewise validate-bundle --strict "$bundle"
done
```

Result: all nine reported `valid bundle`. Direct arithmetic over the nine
`summary_metrics.json` files reproduced the three retained experiment
aggregates for means, sample standard deviations, and ranges. No bundle,
summary, campaign log, or raw evidence file was modified.
# Stream ledger — exploratory measurement blocks (2026-07-17)

Scope: Ed-directed configuration preparation only. No measurement was started.

## EXP-1 — Label and claim boundary

These three blocks follow the FLAGSHIP-001 precedent for production-shaped,
strict-validation-eligible bundles, but their evidence posture is explicitly
`EXPLORATORY` / `L1-legacy`. They are observation-only and carry no claim
framing. Strict bundle validity is an evidence-integrity property, not a claim
upgrade. The D-070 axis-name tags are agenda/indexing tags; they do not assert
that static batching, speculation/MTP, MoE-vs-dense, quantization, or reasoning
length was independently manipulated or identified in these runs.

## EXP-2 — Frozen sequential block order

The directory prefixes and per-block order manifests freeze this sequence:

1. `olmoe-1b-7b`, three contiguous repetitions;
2. `qwen3-4b`, three contiguous repetitions;
3. `qwen35-122b`, three contiguous repetitions.

Each config uses the experiment runner's `repetitions: 3`, yielding three
member bundles with the existing inter-repetition cooldown gate. Do not
interleave the blocks. The operator remains responsible for the quiet-machine
gate and for strict validation of every produced member bundle.

## EXP-3 — Workload parity and tokenizer binding

All blocks preserve the template's five-item `jw_mixed_v1_sentinel` workload,
generator seed/semantics, manifest order, 512-token prompt shape, 256-token
fixed-budget output shape, one warmup run, 10 Hz sampling, 30-second idle
baseline, and 5-second post-warmup settling period.

The template manifest itself is Qwen2.5-tokenizer-bound and contains token IDs
above OLMoE's 50,304-token vocabulary. Reusing it verbatim would pass config
schema validation but fail during OLMoE execution. Therefore the existing
`scripts/gen_jw_mixed.py` generator emitted model-specific manifests and
annotation sidecars from each local tokenizer, inside the authorized campaign
tree. This preserves workload semantics and shape while making the ids-native
prompt path executable and provenance-bound for each model.

Schema 0.1 has no supported chat-template or thinking-mode field. Qwen3-4B
therefore uses the ids-native raw-token prompt path, which bypasses its chat
template and avoids thinking mode; no unknown config key is introduced.

## EXP-4 — Model identity notes

- OLMoE uses upstream revision
  `6d84c48581ece794365f2b8e9cfb043c68ade9c5`. Its local `config.json` is
  intentionally patched with the verified Transformers default
  `rms_norm_eps=1e-05`; the patched file SHA-256 is
  `a57cfd3b1e587296e4e61e68acd467c3acdf7d70f34f51744c2bf826325b649c`.
- Qwen3-4B uses the local D-074 candidate mirror at revision
  `4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25`.
- Qwen3.5-122B-A10B uses the existing FLAGSHIP-001 mirror at revision
  `e9c67b08899964be5fdd069bb1b4bc8907fe68f5`.

## EXP-5 — Planning wall-clock estimates

Each measured bundle includes 30 seconds idle, 5 seconds post-warmup settling,
a four-token adapter warmup, five 512-token prefills, and 1,280 measured output
tokens. A three-bundle block also has two cooldown gates; nominal recovery is
about 30 seconds per gate, while the fail-closed cap is 300 seconds per gate.

| Sequential block | Nominal planning estimate | Basis |
|---|---:|---|
| OLMoE-1B-7B | 3.5–4.5 min | No harness throughput receipt yet; allows roughly 80–160 tok/s plus BF16 load/prefill overhead. |
| Qwen3-4B | 3.3–4.2 min | Anchored to the dated 113 tok/s local greedy feasibility observation, with suite prefill/load margin. |
| Qwen3.5-122B-A10B | 4.5–5.5 min | Anchored to FLAGSHIP-001's 46 tok/s and 12.8 s warm-cache load receipt. |

If both cooldowns hit their 300-second caps, add up to about 9 minutes to a
nominal block estimate. These are scheduling estimates, not measured campaign
results.

## EXP-6 — Execution handoff

Run the three subdirectories in numeric order with the production campaign
runner. Do not execute while any agent session is active. Afterward, validate
every member bundle with `validate-bundle --strict`; retain EXPLORATORY/L1-legacy
labels regardless of strict validity.

codex
The direction is viable only after a deliberate shrink: not a cross-model “MoE is efficient” comparison, and not a correlation on native runs where top‑k is constant. The defensible paper is a same-checkpoint routing-budget intervention—native top‑8 versus prospectively forced top‑4—with complete dispatch logs, a quality/divergence gate, and its own stack-specific floor. Two extra quiet windows should be enough if the desk gate passes.
Required sources and current primary runtime/model evidence have been reviewed; the proposal is narrowed to an identifiable same-checkpoint routing-budget intervention.
  ✓ Read required project, decision, design, feasibility, and strategy sources
  ✓ Extract MoE-specific feasibility, instrument limits, and quantitative sizing evidence
  ✓ Draft and self-check the 600–1200 word proposal against all requested sections
codex
# What Does a Routed Expert Cost? Floor-Gated MoE Routing Energy on an M3 Max

**Thesis:** JouleWise can identify the energy cost of changing MoE routing only through a same-checkpoint, directly observed routing-budget intervention; native cross-model comparisons are too confounded, and native top-*k* counts do not vary.

## Project brief and steps

This paper retains the completed MVP’s scientific spine: `powermetrics` is treated as a calibrated, stack-specific instrument; phase edges are live-bracketed; detection floors combine repeatability, worst-case timing attribution, and never-zero drift; and claims must separately clear the floor and an interval-supported direction gate. The central result remains that the instrument is attribution-limited—roughly 1 J can move across a phase boundary—and practical phase contrasts should be sized around the approximately 5 J effective bar. First complete D-117 exactly as frozen: the 1.5B decode-floor window with prefill rider (~3.14 h), the 7B equivalent (~3.24 h), and the 1.5B-versus-7B decode contrast (~2.80 h). Mint the four phase-floor cells, govern the contrast against the two decode floors, and populate the MVP tables. Those three windows contribute the paper’s metrology evidence and Qwen2.5 demonstration; their floors cannot be borrowed for MoE.

Then run a desk-only MoE feasibility gate. Instrument the already exercised, pinned `Qwen3.5-122B-A10B-4bit` MLX artifact to preserve the router’s actual expert IDs and weights without changing tokens. Freeze one intervention: native routed top-*k*=8 versus forced *k*=4 in the same checkpoint. The official architecture specifies 48 layers, 256 experts, eight routed experts plus one shared expert; current MLX code calculates those indices internally but does not expose them as evidence. [Qwen model card](https://huggingface.co/Qwen/Qwen3.5-122B-A10B), [MLX implementation](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/models/qwen3_next.py). If the desk gate passes, fund two additional quiet windows: one exact-stack floor window and one science contrast window. Thus the complete paper costs five nights, approximately 14–16 quiet-machine hours total; the MoE increment is approximately 5–7 hours, both estimates uncertain until dry-run timing.

## Contributions

1. **Fresh metrology backbone.** The three D-117 windows either produce authenticated 1.5B/7B phase floors and a floor-clearing decode contrast, or the paper refuses those claims.

2. **Auditable MoE routing evidence.** Every measured layer-token must reconcile to exactly eight or four routed expert IDs plus the shared expert. Any missing or inconsistent trace removes the mechanism claim.

3. **A causal, pair-specific routing-budget contrast.** Native *k*=8 and forced *k*=4 differ only in routed-expert budget on one artifact/runtime/boundary. A directional energy result exists only if both JouleWise gates pass.

4. **Energy–quality separation.** A frozen quality screen and exact-output divergence report determine whether the result is “quality-equivalent,” an explicit quality/energy trade-off, or unusable—not a generic MoE-efficiency claim.

## Experiment plan

Use batch 1, one sequential request, 128 prompt tokens, exactly 1,024 greedy output tokens, identical prompt IDs, cache policy, quantization, runtime, and routing logging in both arms. This preserves the frozen single-request boundary. The primary endpoint is gross decode joules/request; tokenizer-scoped mJ/output-token is the required companion.

At *k*=8, each output token causes 384 routed expert-layer activations (48×8), versus 192 at *k*=4; both execute 48 shared-expert activations. The primary window uses ten A/B/B/A blocks—40 members—with A=native-8 and B=forced-4. The preceding floor window uses the proven 10-absolute plus 40 A=A null design, alongside 12 NEG8 members, 3/1/3 references, and live pre/post calibration. No D-117 floor transport is claimed.

Effect sizing is deliberately conservative and uncertain. The architecture implies that changing 8→4 removes about 1.81B routed active parameters per token, roughly 18% of the advertised 10B active total. A permanently voided, planning-only repository diagnostic observed approximately 304 J for a 512-output-token request on this artifact. Crude proportional scaling therefore suggests roughly 110 J at 1,024 tokens; use **40–120 J/request** as the uncertain planning range. Even its low end is about 8× the 5 J bar. If the interval still fails either live gate, the result is “not resolvable”; there are no outcome-driven top-ups.

New desk capabilities are a hash-bound routing sidecar, realized-*k* reconciliation, expert-load/unique-expert summaries, a pinned `routing_top_k_override`, output-difference reporting, and an instrumentation-on/off equivalence test. Buffered routing evidence must be flushed outside the measured decode interval.

## Hardware and instrument needs

Required: the owned 128 GB M3 Max, existing Qwen3.5 artifact, MLX, and `powermetrics`. The RTX 3080 Ti and Jetsons are unnecessary. The WT310E is **not a dependency**: it could later validate whole-system scale, but it cannot establish phase attribution or per-expert energy.

## Venue fit and relationship to the MVP

This is a strong capstone paper and a plausible EuroMLSys or ICPE Emerging submission. It becomes an ICPE full-track candidate only if routing observability, the quality gate, both MoE windows, and an artifact-ready replay all land. It reuses the MVP introduction and Sections 3–5 nearly intact, plus every D-117 result. New material is one routing-instrument subsection, one mechanism experiment, and its refusal/quality analysis.

## Risks and kill criteria

Kill the MoE nights before collection if:

- routing traces are not 100% reconcilable, alter output tokens, or add more than a prospectively fixed ~2% decode-time overhead;
- the forced-*k* path does not execute the exact expected count;
- a pessimistic desk timing proxy—lower timing separation multiplied by 20 W—projects under 15 J;
- forced *k*=4 produces pathological output. A quality gap above 5 percentage points overall or 10 points in any frozen stratum kills “quality-equivalent” wording but may retain a trade-off paper;
- the D-117 floor/mint chain is not green.

## Relation to Ed’s original goals

This directly serves the original MoE mechanism axis and advances the modular-harness goal by making routing policy, realized expert activity, workload, and model artifact independently swappable. It does not yet support an energy-honest public leaderboard or a general claim that MoE is more efficient than dense inference.
tokens used
225,940
# What Does a Routed Expert Cost? Floor-Gated MoE Routing Energy on an M3 Max

**Thesis:** JouleWise can identify the energy cost of changing MoE routing only through a same-checkpoint, directly observed routing-budget intervention; native cross-model comparisons are too confounded, and native top-*k* counts do not vary.

## Project brief and steps

This paper retains the completed MVP’s scientific spine: `powermetrics` is treated as a calibrated, stack-specific instrument; phase edges are live-bracketed; detection floors combine repeatability, worst-case timing attribution, and never-zero drift; and claims must separately clear the floor and an interval-supported direction gate. The central result remains that the instrument is attribution-limited—roughly 1 J can move across a phase boundary—and practical phase contrasts should be sized around the approximately 5 J effective bar. First complete D-117 exactly as frozen: the 1.5B decode-floor window with prefill rider (~3.14 h), the 7B equivalent (~3.24 h), and the 1.5B-versus-7B decode contrast (~2.80 h). Mint the four phase-floor cells, govern the contrast against the two decode floors, and populate the MVP tables. Those three windows contribute the paper’s metrology evidence and Qwen2.5 demonstration; their floors cannot be borrowed for MoE.

Then run a desk-only MoE feasibility gate. Instrument the already exercised, pinned `Qwen3.5-122B-A10B-4bit` MLX artifact to preserve the router’s actual expert IDs and weights without changing tokens. Freeze one intervention: native routed top-*k*=8 versus forced *k*=4 in the same checkpoint. The official architecture specifies 48 layers, 256 experts, eight routed experts plus one shared expert; current MLX code calculates those indices internally but does not expose them as evidence. [Qwen model card](https://huggingface.co/Qwen/Qwen3.5-122B-A10B), [MLX implementation](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/models/qwen3_next.py). If the desk gate passes, fund two additional quiet windows: one exact-stack floor window and one science contrast window. Thus the complete paper costs five nights, approximately 14–16 quiet-machine hours total; the MoE increment is approximately 5–7 hours, both estimates uncertain until dry-run timing.

## Contributions

1. **Fresh metrology backbone.** The three D-117 windows either produce authenticated 1.5B/7B phase floors and a floor-clearing decode contrast, or the paper refuses those claims.

2. **Auditable MoE routing evidence.** Every measured layer-token must reconcile to exactly eight or four routed expert IDs plus the shared expert. Any missing or inconsistent trace removes the mechanism claim.

3. **A causal, pair-specific routing-budget contrast.** Native *k*=8 and forced *k*=4 differ only in routed-expert budget on one artifact/runtime/boundary. A directional energy result exists only if both JouleWise gates pass.

4. **Energy–quality separation.** A frozen quality screen and exact-output divergence report determine whether the result is “quality-equivalent,” an explicit quality/energy trade-off, or unusable—not a generic MoE-efficiency claim.

## Experiment plan

Use batch 1, one sequential request, 128 prompt tokens, exactly 1,024 greedy output tokens, identical prompt IDs, cache policy, quantization, runtime, and routing logging in both arms. This preserves the frozen single-request boundary. The primary endpoint is gross decode joules/request; tokenizer-scoped mJ/output-token is the required companion.

At *k*=8, each output token causes 384 routed expert-layer activations (48×8), versus 192 at *k*=4; both execute 48 shared-expert activations. The primary window uses ten A/B/B/A blocks—40 members—with A=native-8 and B=forced-4. The preceding floor window uses the proven 10-absolute plus 40 A=A null design, alongside 12 NEG8 members, 3/1/3 references, and live pre/post calibration. No D-117 floor transport is claimed.

Effect sizing is deliberately conservative and uncertain. The architecture implies that changing 8→4 removes about 1.81B routed active parameters per token, roughly 18% of the advertised 10B active total. A permanently voided, planning-only repository diagnostic observed approximately 304 J for a 512-output-token request on this artifact. Crude proportional scaling therefore suggests roughly 110 J at 1,024 tokens; use **40–120 J/request** as the uncertain planning range. Even its low end is about 8× the 5 J bar. If the interval still fails either live gate, the result is “not resolvable”; there are no outcome-driven top-ups.

New desk capabilities are a hash-bound routing sidecar, realized-*k* reconciliation, expert-load/unique-expert summaries, a pinned `routing_top_k_override`, output-difference reporting, and an instrumentation-on/off equivalence test. Buffered routing evidence must be flushed outside the measured decode interval.

## Hardware and instrument needs

Required: the owned 128 GB M3 Max, existing Qwen3.5 artifact, MLX, and `powermetrics`. The RTX 3080 Ti and Jetsons are unnecessary. The WT310E is **not a dependency**: it could later validate whole-system scale, but it cannot establish phase attribution or per-expert energy.

## Venue fit and relationship to the MVP

This is a strong capstone paper and a plausible EuroMLSys or ICPE Emerging submission. It becomes an ICPE full-track candidate only if routing observability, the quality gate, both MoE windows, and an artifact-ready replay all land. It reuses the MVP introduction and Sections 3–5 nearly intact, plus every D-117 result. New material is one routing-instrument subsection, one mechanism experiment, and its refusal/quality analysis.

## Risks and kill criteria

Kill the MoE nights before collection if:

- routing traces are not 100% reconcilable, alter output tokens, or add more than a prospectively fixed ~2% decode-time overhead;
- the forced-*k* path does not execute the exact expected count;
- a pessimistic desk timing proxy—lower timing separation multiplied by 20 W—projects under 15 J;
- forced *k*=4 produces pathological output. A quality gap above 5 percentage points overall or 10 points in any frozen stratum kills “quality-equivalent” wording but may retain a trade-off paper;
- the D-117 floor/mint chain is not green.

## Relation to Ed’s original goals

This directly serves the original MoE mechanism axis and advances the modular-harness goal by making routing policy, realized expert activity, workload, and model artifact independently swappable. It does not yet support an energy-honest public leaderboard or a general claim that MoE is more efficient than dense inference.
FILE ../portfolio/prop-mvp-icpe-upgrade.md
  refuters confirmed with line chains); oversight 8 (incl. AP-4
  equivalence self-contradiction, display pipe-counting via live DUT
  repro); final-head passes 3; lead diff/live gates 4 (C-014 impl 2,
  deprecation fix, venv/runtime_unavailable diagnosis).
- **Deliberations:** P2-010 split (consensus), jw_mixed phasing
  (supersedes C-005 sequencing, consensus), window packing (peer
  OVERTURNED lead single-window — position reversal), Q4 grid (peer
  AMENDED 3x3→4x3 — position reversal), D-042 gate reopening (owner
  directive, recorded not re-decided).
- **Interventions:** zero wake stalls across all codex-runs/workflows.
  Worktree-commit sandbox block hit 2x (lead commits at gate — skill
  fold staged). Ed interventions: worktrees directive; ultracode;
  skill-usage logging; hold-skill-folds-for-full-evidence; the
  object-level suite catch (the session's most important correction).
- **Delegation calibration (schema v2):**

| id | to | unit | altitude | outcome | catches | lead-rework |
|---|---|---|---|---|---|---|
| scout-1 | codex | review packet | pinned-spec | good | 4 unique | none |
| lenses x9 | codex | design/reach/review | design-freedom | good-excellent | 40+ unique | none |
| peers x2 | codex | counterreview | judgment-invited | excellent | 2 overturns + 1 unique | none |
| impl-docs x2 | codex | doc batches | pinned-spec | good | — | 2 inline gate fixes |
| impl-code x2 | codex | streams C/S | pinned+design | good; review layers caught 1 blocker + 15 SF | — | 1 deprecation fix |
| fix rounds x5 | codex | pinned fixes | pinned-spec | clean one-shot each | — | none |
| workflows x6 | workflow(codex) | review/research fan-outs | pinned-spec | high precision (~2 refuted / ~30 confirmed) | — | none |
| research x4 | 2 codex + 2 claude(web) | suite research | design-freedom | sound-with-amendments x4 | 37 amendments self-caught | none |

- **Yield/spend:** ~2.3M workflow-agent tokens + ~25 codex sessions.
  Pre-merge catches that would have been expensive post-2M: the
  sacred-window blocker (would have contaminated the entire 2M corpus),
  the AP-4 unfalsifiable-null (would have poisoned pre-registration),
  dead probes (silent evidence loss on every Window-A bundle).
- **Skill-usage:** full entry + staged folds in
  `~/.claude/skills/skill-usage-log.md` (folds applied at session close
  per Ed's full-evidence hold).


## Addendum — post-large-workload meta-reassessment (same day, C-016)

Run after all merges as the session's final step (now standing per
operation-loop §10 / Ed's directive). Shape: 4 parallel analysts over the
full council log, decision log, and skill stack + a cold-start
derivability audit + a completeness critic; then a pre-commit docs-verify
pass over its own batch (5 should-fixes caught, two by D-043's self-test).
Landed: D-043 supersession-closure discipline + back-annotations
      ],
      "fallback": null,
      "fences": [],
      "flags": [
        "blocked_post_2m"
      ],
      "goal": "Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment.",
      "id": "P2-016",
      "lane": "agent",
      "priority": "p2_next_slice",
      "rank": 24,
      "status": "blocked",
      "status_note": "Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake.",
      "stop_card": null
    },
    "P2-019": {
      "acceptance": {
        "evidence": [
          "AP-1 grid campaign bundles",
          "Holdout cells honored",
          "8192 anchor cells on small+mid models"
        ],
        "pointer": {
          "json_pointer": "/tasks/P2-019/acceptance",
          "label": "P2-019 acceptance",
          "path": "docs/process/state_kernel.json"
        },
        "summary": "Grid campaign lands per AP-1; top-up near-floor cells before L3 wording."
      },
      "authority": {
        "label": "AP-1",
        "path": "docs/contracts/analysis_plans.md"
      },
      "dependencies": [
        {
          "evidence": {
            "label": "R-016 mitigated: off-machine backup and restore proof",
            "path": "docs/risk_register.md"
          },
          "kind": "task",
          "required": "external backup destination live before irreplaceable Window-A evidence accumulates",
          "scope": "retain_evidence",
          "state": "satisfied",
          "strength": "hard",
          "target": "P0-003"
        },
        {
          "evidence": null,
          "kind": "task",
          "required": "Window-A baselines size n",
          "scope": "start",
          "state": "pending",
          "strength": "hard",
          "target": "P2-006"
        }
      ],
      "fallback": null,
      "fences": [],
      "flags": [
        "lead_only"
      ],
      "goal": "q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6).",
      "id": "P2-019",
      "lane": "quiet_mac",
      "priority": "p2_next_slice",
      "rank": 4,
      "status": "blocked",
      "stop_card": null
    },
    "P2-020": {
      "acceptance": {
        "evidence": [
          "Five equal-shape ids-native conditions",
          "Request-energy deltas + MDE verdicts"
        ],
        "pointer": {
          "json_pointer": "/tasks/P2-020/acceptance",
          "label": "P2-020 acceptance",
          "path": "docs/process/state_kernel.json"
        },
        "summary": "Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046)."

codex
# From Software Counter to Scientific Instrument: Phase-Resolved LLM Energy Measurement with Calibrated Refusal

**Thesis:** An Apple software power counter can support reproducible, phase-resolved LLM energy research only when in-session calibration determines both what it can measure and what it must refuse; full characterization, held-out workload prediction, and wall-boundary validation elevate JouleWise from a capstone demonstration to an ICPE-quality metrology paper.

## Project brief and steps

JouleWise currently has a complete paper structure but no live claim-bearing values: historical windows establish the rules and supply design diagnostics, while D-117 requires three fresh prospective windows. The 1.5B floor window contains 10 absolute members and 10 four-member null-ABBA blocks; the 7B floor window repeats that 50-bundle design; both obtain prefill floors from the same bundles at zero additional runtime. The contrast window contains ten 1.5B/7B decode ABBA blocks. Their budgeted durations, including calibration, NEG8 bounds, references, untouched idle, and 20% margin, are 3.14, 3.24, and 2.80 hours respectively. Before any night, desk work must land the two-slot live-calibration ledger session, D-102 acceptance-successor machinery, prefill-capable four-cell mint, three frozen campaign packs, synthetic live-ledger regression, extraction specifications, and readiness packet. After the floor windows pass, mint the combined 1.5B/7B decode-and-prefill floor artifact; after the contrast passes, apply the two distinct claim gates and populate the MVP manuscript.

The ICPE delta should then be disciplined rather than broad: collect the already-designed metrology suite in two or three windows; run the promoted Q4 4×3 workload-shape study in two or three windows; borrow Suzanne Rivoire’s lab WT310E for a pilot and confirmatory whole-machine validation; and package a hardware-free raw-to-figure artifact. Total target: **9–10 claim sessions**, comprising D-117’s three plus **6–7 additional sessions**, with one contingency night reserved but not silently used for outcome-dependent top-up.

## Contributions

1. **Calibrated phase attribution:** Across accepted sessions, the 59-pulse bookends bound edge placement, and every admitted science interval remains inside its authenticated bracket. A systematic or out-of-family calibration falsifies transfer and refuses the window.

2. **Operational detection floors:** Null contrasts at 128, 512, and 2048 output tokens stay inside the declared envelopes, while prospectively sized micro-deltas below the floor are refused and sufficiently above-floor effects clear in both directions. Failure of this ordering falsifies the floor model.

3. **Phase-accounting validity:** Prefill plus decode reconciles with the enclosing request boundary, and prefill does not acquire an above-floor dependence on later decode length. A material residual or slope narrows or defeats phase-resolved claims.

4. **Held-out workload prediction:** A categorical model, \(E=\text{fixed}+\text{prompt level}+\text{decode level}\), fitted without the `(512,256)` and `(4096,512)` cells predicts those held-out cells within the prospectively frozen tolerance. A miss is published and downgrades Q4 from L3 to descriptive L2.

5. **Boundary validation:** On held-out loads, synchronized WT310E measurements determine whether `powermetrics` has a stable gain or load-dependent disagreement for whole-request totals. This does not validate phase allocation; it tests only the absolute whole-machine boundary.

## Experiment plan

The D-117 contrast is low-risk scientifically: the historical diagnostic decode effect is **141.29 J**, roughly 28× the stated 5 J sizing bar and about 10× the historical 7B comparative-floor diagnostic of 14.0 J. Neither historical number is claim-bearing, but both justify the design. The 128-token prefill contrast is excluded: its diagnostic point effect is 5.81 J, but its interval reaches approximately 4.0 J. A refusal would mean “not resolvable at this workload,” not equality.

Metrology window A collects the five-level 1.5B decode ramp (128–2048 outputs; 40 members), three-shape additivity set (24 bundles), the 512-token null rung, and sustained 4096-token holds. Window B collects the 128/2048 null rungs and micro-deltas; a short third window carries extended 120/300/600-second idle holds, stability repetition, or spillover. From diagnostic request energies, the 1.5B decode slope is approximately **0.09–0.10 J/token (uncertain)**: a 64-token delta should be roughly 5.8–6.4 J, while the full ramp spans roughly 170–190 J. Final micro-delta lengths must be computed from the fresh ramp to target approximately 0.5×, 1×, 1.5×, and 3× the minted bar. Near-floor members may honestly refuse.

Q4 uses prompt `{128,512,2048,4096}` × output `{64,256,512}` on the two frozen Qwen2.5 stacks, normally five repetitions per cell and ten only where prospectively identified as near-floor. Decode-length effects should be approximately 12 J per additional 128 tokens for 1.5B and much larger for 7B (**uncertain diagnostics**); long-prompt effects should reach tens of joules. Short-prompt 1.5B effects may not clear 5 J and would become unresolved cells, not fitted evidence. This remains sequential single-request inference and therefore does **not** violate the frozen boundary. Required harness additions are multi-session campaign packing, held-out prediction artifacts, and wall-meter import/synchronization—not batching or concurrency.

## Hardware and instrument needs

Owned: M3 Max/128 GB, pinned MLX/Qwen artifacts, `powermetrics`, and existing calibration/custody machinery. The RTX 3080 Ti and Jetsons are unnecessary. Borrowed: an in-calibration Yokogawa WT310E, safe inline fixture, and its export interface. **Wall-meter dependency: yes for this proposed ICPE-full version**, but no for the underlying MVP. If a qualified loan and safe fixture cannot be secured, do not substitute a consumer plug; submit the metrology core to a workshop or ICPE Emerging track.

## Venue and relationship to the MVP

This is a strong capstone chapter immediately after D-117. ICPE full-track fit comes from the combination of instrument characterization, falsifiable held-out performance prediction, physical-boundary validation, and an artifact reviewers can replay. It reuses the MVP draft’s introduction, related-work gap, measurement model, pulse calibration, floor composition, fail-closed protocol, custody rules, and single-stack limitations. New material is the completed C1–C8 results, cross-day stability, Q4 prediction study, wall regression, and artifact evaluation. Without Q4 or equivalent depth, the work remains an excellent metrology workshop paper rather than a convincing full research-track submission.

## Risks and kill criteria

Kill the ICPE upgrade before spending expansion nights if D-117 cannot mint valid floors; the 150-config metrology suite cannot be repacked below four hours with 20% margin; fresh ramp diagnostics cannot safely place micro-deltas around the operative floor; or Q4 dry runs show missing phases, capped contexts, or a campaign budget above three nights. Kill wall validation if the meter lacks current calibration, safe fixture, adequate synchronized sampling, fixed-range uncertainty at Mac loads, or battery-charge neutralization. A failed Q4 holdout or load-dependent wall discrepancy does not kill the paper—both are publishable findings—but they prohibit predictive or simple-gain claims.

## Relation to Ed’s original goals

This direction directly serves the “energy as a third axis beside quality and latency” goal and the energy-honest leaderboard critique: it supplies the error model and refusal semantics every later comparison needs. Q4 also advances the modular harness by making workload and model axes swappable under one calibrated protocol. It does **not** yet deliver speculative decoding, MTP, MoE routing, KV mechanisms, or split inference. Those remain follow-on studies; forcing one into this paper would weaken its coherent instrument-first contribution.
tokens used
130,264
# From Software Counter to Scientific Instrument: Phase-Resolved LLM Energy Measurement with Calibrated Refusal

**Thesis:** An Apple software power counter can support reproducible, phase-resolved LLM energy research only when in-session calibration determines both what it can measure and what it must refuse; full characterization, held-out workload prediction, and wall-boundary validation elevate JouleWise from a capstone demonstration to an ICPE-quality metrology paper.

## Project brief and steps

JouleWise currently has a complete paper structure but no live claim-bearing values: historical windows establish the rules and supply design diagnostics, while D-117 requires three fresh prospective windows. The 1.5B floor window contains 10 absolute members and 10 four-member null-ABBA blocks; the 7B floor window repeats that 50-bundle design; both obtain prefill floors from the same bundles at zero additional runtime. The contrast window contains ten 1.5B/7B decode ABBA blocks. Their budgeted durations, including calibration, NEG8 bounds, references, untouched idle, and 20% margin, are 3.14, 3.24, and 2.80 hours respectively. Before any night, desk work must land the two-slot live-calibration ledger session, D-102 acceptance-successor machinery, prefill-capable four-cell mint, three frozen campaign packs, synthetic live-ledger regression, extraction specifications, and readiness packet. After the floor windows pass, mint the combined 1.5B/7B decode-and-prefill floor artifact; after the contrast passes, apply the two distinct claim gates and populate the MVP manuscript.

The ICPE delta should then be disciplined rather than broad: collect the already-designed metrology suite in two or three windows; run the promoted Q4 4×3 workload-shape study in two or three windows; borrow Suzanne Rivoire’s lab WT310E for a pilot and confirmatory whole-machine validation; and package a hardware-free raw-to-figure artifact. Total target: **9–10 claim sessions**, comprising D-117’s three plus **6–7 additional sessions**, with one contingency night reserved but not silently used for outcome-dependent top-up.

## Contributions

1. **Calibrated phase attribution:** Across accepted sessions, the 59-pulse bookends bound edge placement, and every admitted science interval remains inside its authenticated bracket. A systematic or out-of-family calibration falsifies transfer and refuses the window.

2. **Operational detection floors:** Null contrasts at 128, 512, and 2048 output tokens stay inside the declared envelopes, while prospectively sized micro-deltas below the floor are refused and sufficiently above-floor effects clear in both directions. Failure of this ordering falsifies the floor model.

3. **Phase-accounting validity:** Prefill plus decode reconciles with the enclosing request boundary, and prefill does not acquire an above-floor dependence on later decode length. A material residual or slope narrows or defeats phase-resolved claims.

4. **Held-out workload prediction:** A categorical model, \(E=\text{fixed}+\text{prompt level}+\text{decode level}\), fitted without the `(512,256)` and `(4096,512)` cells predicts those held-out cells within the prospectively frozen tolerance. A miss is published and downgrades Q4 from L3 to descriptive L2.

5. **Boundary validation:** On held-out loads, synchronized WT310E measurements determine whether `powermetrics` has a stable gain or load-dependent disagreement for whole-request totals. This does not validate phase allocation; it tests only the absolute whole-machine boundary.

## Experiment plan

The D-117 contrast is low-risk scientifically: the historical diagnostic decode effect is **141.29 J**, roughly 28× the stated 5 J sizing bar and about 10× the historical 7B comparative-floor diagnostic of 14.0 J. Neither historical number is claim-bearing, but both justify the design. The 128-token prefill contrast is excluded: its diagnostic point effect is 5.81 J, but its interval reaches approximately 4.0 J. A refusal would mean “not resolvable at this workload,” not equality.

Metrology window A collects the five-level 1.5B decode ramp (128–2048 outputs; 40 members), three-shape additivity set (24 bundles), the 512-token null rung, and sustained 4096-token holds. Window B collects the 128/2048 null rungs and micro-deltas; a short third window carries extended 120/300/600-second idle holds, stability repetition, or spillover. From diagnostic request energies, the 1.5B decode slope is approximately **0.09–0.10 J/token (uncertain)**: a 64-token delta should be roughly 5.8–6.4 J, while the full ramp spans roughly 170–190 J. Final micro-delta lengths must be computed from the fresh ramp to target approximately 0.5×, 1×, 1.5×, and 3× the minted bar. Near-floor members may honestly refuse.

Q4 uses prompt `{128,512,2048,4096}` × output `{64,256,512}` on the two frozen Qwen2.5 stacks, normally five repetitions per cell and ten only where prospectively identified as near-floor. Decode-length effects should be approximately 12 J per additional 128 tokens for 1.5B and much larger for 7B (**uncertain diagnostics**); long-prompt effects should reach tens of joules. Short-prompt 1.5B effects may not clear 5 J and would become unresolved cells, not fitted evidence. This remains sequential single-request inference and therefore does **not** violate the frozen boundary. Required harness additions are multi-session campaign packing, held-out prediction artifacts, and wall-meter import/synchronization—not batching or concurrency.

## Hardware and instrument needs

Owned: M3 Max/128 GB, pinned MLX/Qwen artifacts, `powermetrics`, and existing calibration/custody machinery. The RTX 3080 Ti and Jetsons are unnecessary. Borrowed: an in-calibration Yokogawa WT310E, safe inline fixture, and its export interface. **Wall-meter dependency: yes for this proposed ICPE-full version**, but no for the underlying MVP. If a qualified loan and safe fixture cannot be secured, do not substitute a consumer plug; submit the metrology core to a workshop or ICPE Emerging track.

## Venue and relationship to the MVP

This is a strong capstone chapter immediately after D-117. ICPE full-track fit comes from the combination of instrument characterization, falsifiable held-out performance prediction, physical-boundary validation, and an artifact reviewers can replay. It reuses the MVP draft’s introduction, related-work gap, measurement model, pulse calibration, floor composition, fail-closed protocol, custody rules, and single-stack limitations. New material is the completed C1–C8 results, cross-day stability, Q4 prediction study, wall regression, and artifact evaluation. Without Q4 or equivalent depth, the work remains an excellent metrology workshop paper rather than a convincing full research-track submission.

## Risks and kill criteria

Kill the ICPE upgrade before spending expansion nights if D-117 cannot mint valid floors; the 150-config metrology suite cannot be repacked below four hours with 20% margin; fresh ramp diagnostics cannot safely place micro-deltas around the operative floor; or Q4 dry runs show missing phases, capped contexts, or a campaign budget above three nights. Kill wall validation if the meter lacks current calibration, safe fixture, adequate synchronized sampling, fixed-range uncertainty at Mac loads, or battery-charge neutralization. A failed Q4 holdout or load-dependent wall discrepancy does not kill the paper—both are publishable findings—but they prohibit predictive or simple-gain claims.

## Relation to Ed’s original goals

This direction directly serves the “energy as a third axis beside quality and latency” goal and the energy-honest leaderboard critique: it supplies the error model and refusal semantics every later comparison needs. Q4 also advances the modular harness by making workload and model axes swappable under one calibrated protocol. It does **not** yet deliver speculative decoding, MTP, MoE routing, KV mechanisms, or split inference. Those remain follow-on studies; forcing one into this paper would weaken its coherent instrument-first contribution.
FILE ../portfolio/prop-spec-decode-energy.md

| state | primary_claim_eligible | allowed_disposition | required wording |
|---|---:|---|---|
| `exact_token_match` | true | `matched_decoded_work` | effect of speculative decoding on matched decoded work |
| `text_match_token_divergent` | false | `text_matched_descriptive_or_predeclared_quality_matched` | exact text matched but tokenizer-level work diverged; no matched-token efficiency claim |
| `output_divergent` | false | `descriptive_only` | outputs diverged; energy difference is not an efficiency contrast on matched work |
| `unassessable` | false | `refuse_efficiency_claim` | output identity could not be established |

A separately predeclared quality-equivalence design may support
quality-matched wording for divergent outputs. It does not change this report
state or retroactively create token identity.

### 9.3 Generic manifest v2

## 10. C-023-OUTPUT-IDENTITY cross-bundle gate

### 10.1 Separation of duties

Single-bundle strict validation proves count, hash, lifecycle, and output-policy
integrity. It cannot prove that two arms produced the same decoded work.
`joulewise.output_identity_report.v1` is a separate analysis gate that
compares one frozen AP-SPEC pair.

The report's exact top-level fields are:

| Field | Type | Null rule |
|---|---|---|
| `schema_version` | const string `joulewise.output_identity_report.v1` | Required. |
| `report_id` | string matching `oir-[0-9a-f]{64}` | Required, canonical content hash. |
| `manifest_id` | non-empty string | Required. |
| `pair_id` | non-empty string | Required. |
| `spec_off_bundle` | BundleReference object | Required. |
| `spec_on_bundle` | BundleReference object | Required. |
| `config_gate` | ConfigGate object | Required. |
| `target_tokenizer_comparison` | enum `exact_match`, `mismatch`, or `unassessable` | Required and mechanically derived from the two BundleReference identities; never producer-asserted. |
| `requests` | array of RequestComparison objects | Required in roster order; may be empty only when missing/malformed roster evidence prevents construction of a request key, which forces `unassessable`. |
| `overall_state` | one of the four report states | Required. |
| `claim_disposition` | one of `matched_decoded_work`, `text_matched_descriptive_or_predeclared_quality_matched`, `descriptive_only`, or `refuse_efficiency_claim` | Required and mechanically derived. |

The report ID is `oir-` plus SHA-256 of JouleWise canonical JSON for the
complete report with `report_id` removed.

Before that hash is computed, every `reason_codes`,
`missing_evidence_reasons`, and `unexpected_difference_pointers` array is
deduplicated and sorted ascending by Unicode code point. The on-disk report
MUST already use that order; validators reject unsorted or duplicate arrays
rather than silently reordering them. This ordering is part of report identity
and the hand-authored byte goldens.

BundleReference is exact-keyed:

| Field | Type | Null rule |
|---|---|---|
| `run_id` | non-empty string or null | Required key; null iff unavailable and reason `run_id_unavailable` is present. |
| `config_sha256` | 64-character lowercase hexadecimal string or null | Required key; null iff unavailable and reason `config_sha256_unavailable` is present. |
| `requests_artifact_sha256` | 64-character lowercase hexadecimal string or null | Required key; null iff missing/malformed and reason `requests_artifact_unavailable` is present. |
| `request_tokens_artifact_sha256` | 64-character lowercase hexadecimal string or null | Required key; null iff missing/malformed and reason `request_tokens_artifact_unavailable` is present. |
| `summary_sha256` | 64-character lowercase hexadecimal string or null | Required key; null iff missing/malformed and reason `summary_artifact_unavailable` is present. |
| `strict_validation_state` | enum `valid`, `invalid`, or `unavailable` | Required and derived from the single-bundle strict-validation report. Only `valid` satisfies the C-023 precondition. |
| `strict_validation_report_sha256` | 64-character lowercase hexadecimal string or null | Required key; non-null for `valid` or `invalid`; null iff state is `unavailable` and reason `strict_validation_report_unavailable` is present. |
| `target_tokenizer_identity` | TargetTokenizerIdentity object or null | Required key; exact copy of `metadata.runtime.target_tokenizer_identity` when valid, otherwise null with reason `target_tokenizer_identity_unavailable`. |
| `missing_evidence_reasons` | array of unique MissingEvidenceReason values | Required, lexicographically sorted, and empty iff none of this reference's fields is missing. |

ConfigGate exact fields:

| Field | Type | Null rule |
|---|---|---|
| `allowed_difference_pointers` | exact four-string array from §9.2 | Required. |
| `spec_off_projection_sha256` | 64-hex string or null | Required key; null when projection evidence is unavailable. |
| `spec_on_projection_sha256` | 64-hex string or null | Required key; null when projection evidence is unavailable. |
| `projections_equal` | boolean or null | Required key; null unless both projections are available. |
| `unexpected_difference_pointers` | array of unique strings | Required and lexicographically sorted by Unicode code point; empty when equal or comparison is unavailable. |
| `missing_evidence_reasons` | array of unique MissingEvidenceReason values | Required and lexicographically sorted; contains `config_projection_unavailable` iff either projection hash or the comparison is null. |

Any unexpected config difference or unavailable projection sets overall state
`unassessable` and disposition `refuse_efficiency_claim`, regardless of
coincidentally matching output.

RequestComparison exact fields:

| Field | Type | Null rule |
|---|---|---|
| `request_ordinal` | integer >= 0 or null | Required key; null iff reason `request_roster_key_unavailable` is present. |
| `request_input_id` | non-empty identifier string or null | Required key; null iff reason `request_roster_key_unavailable` is present. |
| `spec_off_request_id` | non-empty string or null | Required key; null with reason `spec_off_request_id_unavailable`. |
| `spec_on_request_id` | non-empty string or null | Required key; null with reason `spec_on_request_id_unavailable`. |
| `spec_off_token_ids_sha256` | 64-hex string or null | Required key; null iff reason `spec_off_token_ids_unavailable` is present. |
| `spec_on_token_ids_sha256` | 64-hex string or null | Required key; null iff reason `spec_on_token_ids_unavailable` is present. |
| `spec_off_text_sha256` | 64-hex string or null | Required key; null iff reason `spec_off_response_text_unavailable` is present. |
| `spec_on_text_sha256` | 64-hex string or null | Required key; null iff reason `spec_on_response_text_unavailable` is present. |
| `output_token_count_equal` | boolean or null | Required key; null iff reason `output_count_comparison_unavailable` is present. |
| `stop_reason_equal` | boolean or null | Required key; null iff reason `stop_reason_comparison_unavailable` is present. |
| `state` | one of the four report states | Required. |
| `missing_evidence_reasons` | array of unique MissingEvidenceReason values | Required and lexicographically sorted. Each nullable field has its corresponding reason iff null. |

codex
The repository’s own mechanism evidence changes the answer: generic `mlx-lm` speculative decoding is executable but not claim-instrumentable, while the vendored DSpark/DFlash path is observable yet was 2.5–2.8× slower than greedy in its only smoke. That makes “speculation always saves energy” a poor thesis; the publishable question is the floor-gated break-even curve, including a credible no-savings/refusal outcome.
web search: 
web search: site:arxiv.org speculative decoding energy consumption acceptance rate paper ...
web search: 
web search: site:github.com/ml-explore/mlx-lm speculative_decode_callback tokens_proposed acceptance callback ...
web search: 
web search: 
web search: 
web search: 'Qwen3'
codex
# When Does Speculative Decoding Save Energy on a Mac? Floor-Gated Break-Even Curves on Consumer Silicon

**Thesis:** Speculative decoding saves energy only when accepted-token yield repays the draft-and-verification work; JouleWise can measure—or explicitly refuse—that break-even point using calibrated, same-boundary measurements rather than assuming that latency speedup implies energy savings.

## Project brief and steps

JouleWise already supplies the scientific foundation for this paper. The structured MVP draft contributes the named M3 Max/MLX/`powermetrics` boundary, phase-resolved integration, in-window pulse-train calibration, the finding that measurement is attribution-limited at roughly 1 J per phase member, composed detection floors, two separate claim gates, and the fail-closed custody protocol. D-117 now requires three prospective claim windows: a 1.5B decode floor with a prefill-floor rider (budgeted at 3.14 h), a 7B equivalent (3.24 h), and a 1.5B-versus-7B decode contrast (2.80 h). Before those nights, the ledger-bookend capability, D-102 successor path, multi-cell mint, extraction pinsets, frozen manifests, synthetic integration regression, and operator packet must land. After collection, the four phase-floor cells are minted, the decode contrast is evaluated against the armwise maximum floor and its separate claim interval, and the MVP paper is populated.

Only then should the speculative-decoding extension consume nights. First run a two-to-three-week desk feasibility gate: instrument the already-executable Qwen2.5 external-draft path with direct proposal, acceptance, and decode-step events; prove exact output identity; conduct non-claim timing/energy pilots; and freeze an AP-SPEC campaign. If it passes, spend two additional quiet windows—one request-window floor campaign and one mechanism campaign, splitting the latter into a third window only if its measured runtime plus 20% margin exceeds four hours. Thus the paper has a solid three-night metrology core regardless of whether the mechanism bet survives, and a five-night target if it does.

## Contributions

1. **A calibrated consumer-silicon measurement spine.** The issued D-079 rule, D-117 live brackets, minted 1.5B/7B phase floors, prefill riders, and decode contrast must all pass their frozen gates; otherwise the affected result is withheld.

2. **A floor-gated speculative-decoding break-even curve.** For one exact 7B target stack, estimate paired gross-energy change versus runtime-observed acceptance rate. A break-even acceptance threshold is reported only if its interval lies inside the observed acceptance range and the underlying contrasts clear approximately 5 J.

3. **A controlled draft-size tradeoff.** Compare Qwen2.5-0.5B and Qwen2.5-1.5B 4-bit drafts against the same Qwen2.5-7B 4-bit target, tokenizer, prompts, proposal cap, and output policy. The falsifiable question is whether higher acceptance from the larger draft compensates for its extra work.

4. **A documented refusal result.** Output divergence, missing counters, a below-floor contrast, or an unlocalized break-even must produce a named refusal—not “no effect,” equality, or an efficiency claim.

## Experiment plan

Use batch one, one sequential request, 128 prompt tokens, exactly 256 greedy output tokens, cold request KV, and proposal cap \(K=3\). The current MLX path must be wrapped or narrowly forked to emit actual `tokens_proposed`, `tokens_accepted`, acceptance rate, and exact committed bursts. This extends observability but **does not violate the frozen single-request boundary**; no per-round energy attribution is attempted.

The floor window contains three `gross_request` cells: spec-off, 0.5B-draft spec-on, and 1.5B-draft spec-on. Each gets five absolute repetitions and five A=A ABBA null blocks, with the registered small-sample guard. The mechanism window uses ten ABBA blocks per draft size—80 members total—with a frozen, equal-token-shape prompt roster spanning chat, code, and structured reasoning to generate acceptance variation. Primary metric: paired `spec_on − spec_off` gross joules/request. Companion: gross J/committed-output-token. Gross J/accepted-draft-token remains a spec-on mechanism diagnostic, never the efficiency denominator.

The historical 7B floor member averaged about 192 J for its 512-token decode workload; halving length suggests roughly **96 J at 256 tokens**, but this is an uncertain, non-claim extrapolation. The 5 J bar is therefore about 5% of expected request energy. Public results show why a wide prior is necessary: current `mlx-dspark` reports roughly 1.7–2.3× Qwen3 speedups on an M4 Pro, whereas JouleWise’s older Qwen3-4B smoke achieved only 0.36–0.41× greedy throughput. A separate energy study also found cases where speculative decoding used more energy despite lower latency. [MLX-DSpark results](https://github.com/ARahim3/mlx-dspark), [energy study](https://arxiv.org/abs/2602.09113).

Accordingly, the expected on/off effect is a deliberately broad, **highly uncertain −40 J saving to +100 J penalty** per 256-token request; most of that range clears 5 J. The draft-size difference is less certain—approximately **5–25 J**, and it may not clear. A refusal would mean only that this instrument cannot distinguish the two draft sizes under the frozen workload.

Desk work includes runtime callback instrumentation, live AXI adapter integration, strict-bundle tests, output-identity reports, model/tokenizer/hash receipts, AP-SPEC registries, floor selectors, ABBA manifests, multiplicity rules, runtime budgeting, and raw-to-figure regression.

## Hardware and instrument needs

Owned: the M3 Max MacBook Pro, approved 140 W power path, Qwen2.5 target/draft artifacts, MLX, and `powermetrics`. No RTX, Jetson, purchase, or wall meter is required. The WT310E could later validate whole-system gain, but it cannot validate phase allocation and is **not a dependency** for these same-SoC-boundary contrasts.

## Venue and relationship to the MVP

For the capstone, this is an optional mechanism chapter appended to an independently complete metrology paper. It directly reuses MVP §§3–5, the instrument characterization and limitations, D-117 floor tables, and the model-size demonstration; new material is the speculative runtime, request-window floors, acceptance-energy curve, and draft-size result.

For ICPE full research, the mechanism result supplies the deeper systems contribution the MVP alone lacks. EuroMLSys or an ICPE emerging/WIP track remains appropriate if the break-even interval is broad or the result is chiefly a well-supported refusal. The claim cannot be “first speculative-decoding energy study”; its novelty is calibrated, floor-gated evidence on named consumer silicon.

## Risks and kill criteria

Kill the quiet-window campaign if any of these occurs during desk work:

- Direct proposal/acceptance counters or step boundaries remain unavailable.
- Any frozen-prompt spec-on/off pair fails exact token identity. This is especially important because a current MLX-LM report documents greedy divergence at \(K=4\); \(K=3\) still requires independent exhaustive parity testing. [MLX-LM issue](https://github.com/ml-explore/mlx-lm/issues/1470)
- The prompt roster spans less than 15 percentage points of acceptance, making a break-even curve unidentified.
- Pilot uncertainty places both draft effects wholly inside ±5 J.
- The floor selector cannot bind all three request-window cells.
- Dry-run timing exceeds four hours after the mandatory 20% margin; first cut the size comparison, then cancel rather than compress the protocol.

## Relation to Ed’s original goals

This directly serves the original **mechanism-level speculative-decoding** axis and the broader goal of treating energy as a third metric beside quality and latency. It also exercises the modular-harness vision: target model, draft model, proposal policy, workload, and analysis registry become swappable while output identity, measurement boundary, floors, and custody remain invariant.
tokens used
207,791
# When Does Speculative Decoding Save Energy on a Mac? Floor-Gated Break-Even Curves on Consumer Silicon

**Thesis:** Speculative decoding saves energy only when accepted-token yield repays the draft-and-verification work; JouleWise can measure—or explicitly refuse—that break-even point using calibrated, same-boundary measurements rather than assuming that latency speedup implies energy savings.

## Project brief and steps

JouleWise already supplies the scientific foundation for this paper. The structured MVP draft contributes the named M3 Max/MLX/`powermetrics` boundary, phase-resolved integration, in-window pulse-train calibration, the finding that measurement is attribution-limited at roughly 1 J per phase member, composed detection floors, two separate claim gates, and the fail-closed custody protocol. D-117 now requires three prospective claim windows: a 1.5B decode floor with a prefill-floor rider (budgeted at 3.14 h), a 7B equivalent (3.24 h), and a 1.5B-versus-7B decode contrast (2.80 h). Before those nights, the ledger-bookend capability, D-102 successor path, multi-cell mint, extraction pinsets, frozen manifests, synthetic integration regression, and operator packet must land. After collection, the four phase-floor cells are minted, the decode contrast is evaluated against the armwise maximum floor and its separate claim interval, and the MVP paper is populated.

Only then should the speculative-decoding extension consume nights. First run a two-to-three-week desk feasibility gate: instrument the already-executable Qwen2.5 external-draft path with direct proposal, acceptance, and decode-step events; prove exact output identity; conduct non-claim timing/energy pilots; and freeze an AP-SPEC campaign. If it passes, spend two additional quiet windows—one request-window floor campaign and one mechanism campaign, splitting the latter into a third window only if its measured runtime plus 20% margin exceeds four hours. Thus the paper has a solid three-night metrology core regardless of whether the mechanism bet survives, and a five-night target if it does.

## Contributions

1. **A calibrated consumer-silicon measurement spine.** The issued D-079 rule, D-117 live brackets, minted 1.5B/7B phase floors, prefill riders, and decode contrast must all pass their frozen gates; otherwise the affected result is withheld.

2. **A floor-gated speculative-decoding break-even curve.** For one exact 7B target stack, estimate paired gross-energy change versus runtime-observed acceptance rate. A break-even acceptance threshold is reported only if its interval lies inside the observed acceptance range and the underlying contrasts clear approximately 5 J.

3. **A controlled draft-size tradeoff.** Compare Qwen2.5-0.5B and Qwen2.5-1.5B 4-bit drafts against the same Qwen2.5-7B 4-bit target, tokenizer, prompts, proposal cap, and output policy. The falsifiable question is whether higher acceptance from the larger draft compensates for its extra work.

4. **A documented refusal result.** Output divergence, missing counters, a below-floor contrast, or an unlocalized break-even must produce a named refusal—not “no effect,” equality, or an efficiency claim.

## Experiment plan

Use batch one, one sequential request, 128 prompt tokens, exactly 256 greedy output tokens, cold request KV, and proposal cap \(K=3\). The current MLX path must be wrapped or narrowly forked to emit actual `tokens_proposed`, `tokens_accepted`, acceptance rate, and exact committed bursts. This extends observability but **does not violate the frozen single-request boundary**; no per-round energy attribution is attempted.

The floor window contains three `gross_request` cells: spec-off, 0.5B-draft spec-on, and 1.5B-draft spec-on. Each gets five absolute repetitions and five A=A ABBA null blocks, with the registered small-sample guard. The mechanism window uses ten ABBA blocks per draft size—80 members total—with a frozen, equal-token-shape prompt roster spanning chat, code, and structured reasoning to generate acceptance variation. Primary metric: paired `spec_on − spec_off` gross joules/request. Companion: gross J/committed-output-token. Gross J/accepted-draft-token remains a spec-on mechanism diagnostic, never the efficiency denominator.

The historical 7B floor member averaged about 192 J for its 512-token decode workload; halving length suggests roughly **96 J at 256 tokens**, but this is an uncertain, non-claim extrapolation. The 5 J bar is therefore about 5% of expected request energy. Public results show why a wide prior is necessary: current `mlx-dspark` reports roughly 1.7–2.3× Qwen3 speedups on an M4 Pro, whereas JouleWise’s older Qwen3-4B smoke achieved only 0.36–0.41× greedy throughput. A separate energy study also found cases where speculative decoding used more energy despite lower latency. [MLX-DSpark results](https://github.com/ARahim3/mlx-dspark), [energy study](https://arxiv.org/abs/2602.09113).

Accordingly, the expected on/off effect is a deliberately broad, **highly uncertain −40 J saving to +100 J penalty** per 256-token request; most of that range clears 5 J. The draft-size difference is less certain—approximately **5–25 J**, and it may not clear. A refusal would mean only that this instrument cannot distinguish the two draft sizes under the frozen workload.

Desk work includes runtime callback instrumentation, live AXI adapter integration, strict-bundle tests, output-identity reports, model/tokenizer/hash receipts, AP-SPEC registries, floor selectors, ABBA manifests, multiplicity rules, runtime budgeting, and raw-to-figure regression.

## Hardware and instrument needs

Owned: the M3 Max MacBook Pro, approved 140 W power path, Qwen2.5 target/draft artifacts, MLX, and `powermetrics`. No RTX, Jetson, purchase, or wall meter is required. The WT310E could later validate whole-system gain, but it cannot validate phase allocation and is **not a dependency** for these same-SoC-boundary contrasts.

## Venue and relationship to the MVP

For the capstone, this is an optional mechanism chapter appended to an independently complete metrology paper. It directly reuses MVP §§3–5, the instrument characterization and limitations, D-117 floor tables, and the model-size demonstration; new material is the speculative runtime, request-window floors, acceptance-energy curve, and draft-size result.

For ICPE full research, the mechanism result supplies the deeper systems contribution the MVP alone lacks. EuroMLSys or an ICPE emerging/WIP track remains appropriate if the break-even interval is broad or the result is chiefly a well-supported refusal. The claim cannot be “first speculative-decoding energy study”; its novelty is calibrated, floor-gated evidence on named consumer silicon.

## Risks and kill criteria

Kill the quiet-window campaign if any of these occurs during desk work:

- Direct proposal/acceptance counters or step boundaries remain unavailable.
- Any frozen-prompt spec-on/off pair fails exact token identity. This is especially important because a current MLX-LM report documents greedy divergence at \(K=4\); \(K=3\) still requires independent exhaustive parity testing. [MLX-LM issue](https://github.com/ml-explore/mlx-lm/issues/1470)
- The prompt roster spans less than 15 percentage points of acceptance, making a break-even curve unidentified.
- Pilot uncertainty places both draft effects wholly inside ±5 J.
- The floor selector cannot bind all three request-window cells.
- Dry-run timing exceeds four hours after the mandatory 20% margin; first cut the size comparison, then cancel rather than compress the protocol.

## Relation to Ed’s original goals

This directly serves the original **mechanism-level speculative-decoding** axis and the broader goal of treating energy as a third metric beside quality and latency. It also exercises the modular-harness vision: target model, draft model, proposal policy, workload, and analysis registry become swappable while output identity, measurement boundary, floors, and custody remain invariant.

exec
/bin/zsh -lc 'tail -n 180 ../portfolio/prop-moe-routing-energy.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:

## EXP-2 — Frozen sequential block order

The directory prefixes and per-block order manifests freeze this sequence:

1. `olmoe-1b-7b`, three contiguous repetitions;
2. `qwen3-4b`, three contiguous repetitions;
3. `qwen35-122b`, three contiguous repetitions.

Each config uses the experiment runner's `repetitions: 3`, yielding three
member bundles with the existing inter-repetition cooldown gate. Do not
interleave the blocks. The operator remains responsible for the quiet-machine
gate and for strict validation of every produced member bundle.

## EXP-3 — Workload parity and tokenizer binding

All blocks preserve the template's five-item `jw_mixed_v1_sentinel` workload,
generator seed/semantics, manifest order, 512-token prompt shape, 256-token
fixed-budget output shape, one warmup run, 10 Hz sampling, 30-second idle
baseline, and 5-second post-warmup settling period.

The template manifest itself is Qwen2.5-tokenizer-bound and contains token IDs
above OLMoE's 50,304-token vocabulary. Reusing it verbatim would pass config
schema validation but fail during OLMoE execution. Therefore the existing
`scripts/gen_jw_mixed.py` generator emitted model-specific manifests and
annotation sidecars from each local tokenizer, inside the authorized campaign
tree. This preserves workload semantics and shape while making the ids-native
prompt path executable and provenance-bound for each model.

Schema 0.1 has no supported chat-template or thinking-mode field. Qwen3-4B
therefore uses the ids-native raw-token prompt path, which bypasses its chat
template and avoids thinking mode; no unknown config key is introduced.

## EXP-4 — Model identity notes

- OLMoE uses upstream revision
  `6d84c48581ece794365f2b8e9cfb043c68ade9c5`. Its local `config.json` is
  intentionally patched with the verified Transformers default
  `rms_norm_eps=1e-05`; the patched file SHA-256 is
  `a57cfd3b1e587296e4e61e68acd467c3acdf7d70f34f51744c2bf826325b649c`.
- Qwen3-4B uses the local D-074 candidate mirror at revision
  `4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25`.
- Qwen3.5-122B-A10B uses the existing FLAGSHIP-001 mirror at revision
  `e9c67b08899964be5fdd069bb1b4bc8907fe68f5`.

## EXP-5 — Planning wall-clock estimates

Each measured bundle includes 30 seconds idle, 5 seconds post-warmup settling,
a four-token adapter warmup, five 512-token prefills, and 1,280 measured output
tokens. A three-bundle block also has two cooldown gates; nominal recovery is
about 30 seconds per gate, while the fail-closed cap is 300 seconds per gate.

| Sequential block | Nominal planning estimate | Basis |
|---|---:|---|
| OLMoE-1B-7B | 3.5–4.5 min | No harness throughput receipt yet; allows roughly 80–160 tok/s plus BF16 load/prefill overhead. |
| Qwen3-4B | 3.3–4.2 min | Anchored to the dated 113 tok/s local greedy feasibility observation, with suite prefill/load margin. |
| Qwen3.5-122B-A10B | 4.5–5.5 min | Anchored to FLAGSHIP-001's 46 tok/s and 12.8 s warm-cache load receipt. |

If both cooldowns hit their 300-second caps, add up to about 9 minutes to a
nominal block estimate. These are scheduling estimates, not measured campaign
results.

## EXP-6 — Execution handoff

Run the three subdirectories in numeric order with the production campaign
runner. Do not execute while any agent session is active. Afterward, validate
every member bundle with `validate-bundle --strict`; retain EXPLORATORY/L1-legacy
labels regardless of strict validity.

codex
The direction is viable only after a deliberate shrink: not a cross-model “MoE is efficient” comparison, and not a correlation on native runs where top‑k is constant. The defensible paper is a same-checkpoint routing-budget intervention—native top‑8 versus prospectively forced top‑4—with complete dispatch logs, a quality/divergence gate, and its own stack-specific floor. Two extra quiet windows should be enough if the desk gate passes.
Required sources and current primary runtime/model evidence have been reviewed; the proposal is narrowed to an identifiable same-checkpoint routing-budget intervention.
  ✓ Read required project, decision, design, feasibility, and strategy sources
  ✓ Extract MoE-specific feasibility, instrument limits, and quantitative sizing evidence
  ✓ Draft and self-check the 600–1200 word proposal against all requested sections
codex
# What Does a Routed Expert Cost? Floor-Gated MoE Routing Energy on an M3 Max

**Thesis:** JouleWise can identify the energy cost of changing MoE routing only through a same-checkpoint, directly observed routing-budget intervention; native cross-model comparisons are too confounded, and native top-*k* counts do not vary.

## Project brief and steps

This paper retains the completed MVP’s scientific spine: `powermetrics` is treated as a calibrated, stack-specific instrument; phase edges are live-bracketed; detection floors combine repeatability, worst-case timing attribution, and never-zero drift; and claims must separately clear the floor and an interval-supported direction gate. The central result remains that the instrument is attribution-limited—roughly 1 J can move across a phase boundary—and practical phase contrasts should be sized around the approximately 5 J effective bar. First complete D-117 exactly as frozen: the 1.5B decode-floor window with prefill rider (~3.14 h), the 7B equivalent (~3.24 h), and the 1.5B-versus-7B decode contrast (~2.80 h). Mint the four phase-floor cells, govern the contrast against the two decode floors, and populate the MVP tables. Those three windows contribute the paper’s metrology evidence and Qwen2.5 demonstration; their floors cannot be borrowed for MoE.

Then run a desk-only MoE feasibility gate. Instrument the already exercised, pinned `Qwen3.5-122B-A10B-4bit` MLX artifact to preserve the router’s actual expert IDs and weights without changing tokens. Freeze one intervention: native routed top-*k*=8 versus forced *k*=4 in the same checkpoint. The official architecture specifies 48 layers, 256 experts, eight routed experts plus one shared expert; current MLX code calculates those indices internally but does not expose them as evidence. [Qwen model card](https://huggingface.co/Qwen/Qwen3.5-122B-A10B), [MLX implementation](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/models/qwen3_next.py). If the desk gate passes, fund two additional quiet windows: one exact-stack floor window and one science contrast window. Thus the complete paper costs five nights, approximately 14–16 quiet-machine hours total; the MoE increment is approximately 5–7 hours, both estimates uncertain until dry-run timing.

## Contributions

1. **Fresh metrology backbone.** The three D-117 windows either produce authenticated 1.5B/7B phase floors and a floor-clearing decode contrast, or the paper refuses those claims.

2. **Auditable MoE routing evidence.** Every measured layer-token must reconcile to exactly eight or four routed expert IDs plus the shared expert. Any missing or inconsistent trace removes the mechanism claim.

3. **A causal, pair-specific routing-budget contrast.** Native *k*=8 and forced *k*=4 differ only in routed-expert budget on one artifact/runtime/boundary. A directional energy result exists only if both JouleWise gates pass.

4. **Energy–quality separation.** A frozen quality screen and exact-output divergence report determine whether the result is “quality-equivalent,” an explicit quality/energy trade-off, or unusable—not a generic MoE-efficiency claim.

## Experiment plan

Use batch 1, one sequential request, 128 prompt tokens, exactly 1,024 greedy output tokens, identical prompt IDs, cache policy, quantization, runtime, and routing logging in both arms. This preserves the frozen single-request boundary. The primary endpoint is gross decode joules/request; tokenizer-scoped mJ/output-token is the required companion.

At *k*=8, each output token causes 384 routed expert-layer activations (48×8), versus 192 at *k*=4; both execute 48 shared-expert activations. The primary window uses ten A/B/B/A blocks—40 members—with A=native-8 and B=forced-4. The preceding floor window uses the proven 10-absolute plus 40 A=A null design, alongside 12 NEG8 members, 3/1/3 references, and live pre/post calibration. No D-117 floor transport is claimed.

Effect sizing is deliberately conservative and uncertain. The architecture implies that changing 8→4 removes about 1.81B routed active parameters per token, roughly 18% of the advertised 10B active total. A permanently voided, planning-only repository diagnostic observed approximately 304 J for a 512-output-token request on this artifact. Crude proportional scaling therefore suggests roughly 110 J at 1,024 tokens; use **40–120 J/request** as the uncertain planning range. Even its low end is about 8× the 5 J bar. If the interval still fails either live gate, the result is “not resolvable”; there are no outcome-driven top-ups.

New desk capabilities are a hash-bound routing sidecar, realized-*k* reconciliation, expert-load/unique-expert summaries, a pinned `routing_top_k_override`, output-difference reporting, and an instrumentation-on/off equivalence test. Buffered routing evidence must be flushed outside the measured decode interval.

## Hardware and instrument needs

Required: the owned 128 GB M3 Max, existing Qwen3.5 artifact, MLX, and `powermetrics`. The RTX 3080 Ti and Jetsons are unnecessary. The WT310E is **not a dependency**: it could later validate whole-system scale, but it cannot establish phase attribution or per-expert energy.

## Venue fit and relationship to the MVP

This is a strong capstone paper and a plausible EuroMLSys or ICPE Emerging submission. It becomes an ICPE full-track candidate only if routing observability, the quality gate, both MoE windows, and an artifact-ready replay all land. It reuses the MVP introduction and Sections 3–5 nearly intact, plus every D-117 result. New material is one routing-instrument subsection, one mechanism experiment, and its refusal/quality analysis.

## Risks and kill criteria

Kill the MoE nights before collection if:

- routing traces are not 100% reconcilable, alter output tokens, or add more than a prospectively fixed ~2% decode-time overhead;
- the forced-*k* path does not execute the exact expected count;
- a pessimistic desk timing proxy—lower timing separation multiplied by 20 W—projects under 15 J;
- forced *k*=4 produces pathological output. A quality gap above 5 percentage points overall or 10 points in any frozen stratum kills “quality-equivalent” wording but may retain a trade-off paper;
- the D-117 floor/mint chain is not green.

## Relation to Ed’s original goals

This directly serves the original MoE mechanism axis and advances the modular-harness goal by making routing policy, realized expert activity, workload, and model artifact independently swappable. It does not yet support an energy-honest public leaderboard or a general claim that MoE is more efficient than dense inference.
tokens used
225,940
# What Does a Routed Expert Cost? Floor-Gated MoE Routing Energy on an M3 Max

**Thesis:** JouleWise can identify the energy cost of changing MoE routing only through a same-checkpoint, directly observed routing-budget intervention; native cross-model comparisons are too confounded, and native top-*k* counts do not vary.

## Project brief and steps

This paper retains the completed MVP’s scientific spine: `powermetrics` is treated as a calibrated, stack-specific instrument; phase edges are live-bracketed; detection floors combine repeatability, worst-case timing attribution, and never-zero drift; and claims must separately clear the floor and an interval-supported direction gate. The central result remains that the instrument is attribution-limited—roughly 1 J can move across a phase boundary—and practical phase contrasts should be sized around the approximately 5 J effective bar. First complete D-117 exactly as frozen: the 1.5B decode-floor window with prefill rider (~3.14 h), the 7B equivalent (~3.24 h), and the 1.5B-versus-7B decode contrast (~2.80 h). Mint the four phase-floor cells, govern the contrast against the two decode floors, and populate the MVP tables. Those three windows contribute the paper’s metrology evidence and Qwen2.5 demonstration; their floors cannot be borrowed for MoE.

Then run a desk-only MoE feasibility gate. Instrument the already exercised, pinned `Qwen3.5-122B-A10B-4bit` MLX artifact to preserve the router’s actual expert IDs and weights without changing tokens. Freeze one intervention: native routed top-*k*=8 versus forced *k*=4 in the same checkpoint. The official architecture specifies 48 layers, 256 experts, eight routed experts plus one shared expert; current MLX code calculates those indices internally but does not expose them as evidence. [Qwen model card](https://huggingface.co/Qwen/Qwen3.5-122B-A10B), [MLX implementation](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/models/qwen3_next.py). If the desk gate passes, fund two additional quiet windows: one exact-stack floor window and one science contrast window. Thus the complete paper costs five nights, approximately 14–16 quiet-machine hours total; the MoE increment is approximately 5–7 hours, both estimates uncertain until dry-run timing.

## Contributions

1. **Fresh metrology backbone.** The three D-117 windows either produce authenticated 1.5B/7B phase floors and a floor-clearing decode contrast, or the paper refuses those claims.

2. **Auditable MoE routing evidence.** Every measured layer-token must reconcile to exactly eight or four routed expert IDs plus the shared expert. Any missing or inconsistent trace removes the mechanism claim.

3. **A causal, pair-specific routing-budget contrast.** Native *k*=8 and forced *k*=4 differ only in routed-expert budget on one artifact/runtime/boundary. A directional energy result exists only if both JouleWise gates pass.

4. **Energy–quality separation.** A frozen quality screen and exact-output divergence report determine whether the result is “quality-equivalent,” an explicit quality/energy trade-off, or unusable—not a generic MoE-efficiency claim.

## Experiment plan

Use batch 1, one sequential request, 128 prompt tokens, exactly 1,024 greedy output tokens, identical prompt IDs, cache policy, quantization, runtime, and routing logging in both arms. This preserves the frozen single-request boundary. The primary endpoint is gross decode joules/request; tokenizer-scoped mJ/output-token is the required companion.

At *k*=8, each output token causes 384 routed expert-layer activations (48×8), versus 192 at *k*=4; both execute 48 shared-expert activations. The primary window uses ten A/B/B/A blocks—40 members—with A=native-8 and B=forced-4. The preceding floor window uses the proven 10-absolute plus 40 A=A null design, alongside 12 NEG8 members, 3/1/3 references, and live pre/post calibration. No D-117 floor transport is claimed.

Effect sizing is deliberately conservative and uncertain. The architecture implies that changing 8→4 removes about 1.81B routed active parameters per token, roughly 18% of the advertised 10B active total. A permanently voided, planning-only repository diagnostic observed approximately 304 J for a 512-output-token request on this artifact. Crude proportional scaling therefore suggests roughly 110 J at 1,024 tokens; use **40–120 J/request** as the uncertain planning range. Even its low end is about 8× the 5 J bar. If the interval still fails either live gate, the result is “not resolvable”; there are no outcome-driven top-ups.

New desk capabilities are a hash-bound routing sidecar, realized-*k* reconciliation, expert-load/unique-expert summaries, a pinned `routing_top_k_override`, output-difference reporting, and an instrumentation-on/off equivalence test. Buffered routing evidence must be flushed outside the measured decode interval.

## Hardware and instrument needs

Required: the owned 128 GB M3 Max, existing Qwen3.5 artifact, MLX, and `powermetrics`. The RTX 3080 Ti and Jetsons are unnecessary. The WT310E is **not a dependency**: it could later validate whole-system scale, but it cannot establish phase attribution or per-expert energy.

## Venue fit and relationship to the MVP

This is a strong capstone paper and a plausible EuroMLSys or ICPE Emerging submission. It becomes an ICPE full-track candidate only if routing observability, the quality gate, both MoE windows, and an artifact-ready replay all land. It reuses the MVP introduction and Sections 3–5 nearly intact, plus every D-117 result. New material is one routing-instrument subsection, one mechanism experiment, and its refusal/quality analysis.

## Risks and kill criteria

Kill the MoE nights before collection if:

- routing traces are not 100% reconcilable, alter output tokens, or add more than a prospectively fixed ~2% decode-time overhead;
- the forced-*k* path does not execute the exact expected count;
- a pessimistic desk timing proxy—lower timing separation multiplied by 20 W—projects under 15 J;
- forced *k*=4 produces pathological output. A quality gap above 5 percentage points overall or 10 points in any frozen stratum kills “quality-equivalent” wording but may retain a trade-off paper;
- the D-117 floor/mint chain is not green.

## Relation to Ed’s original goals

This directly serves the original MoE mechanism axis and advances the modular-harness goal by making routing policy, realized expert activity, workload, and model artifact independently swappable. It does not yet support an energy-honest public leaderboard or a general claim that MoE is more efficient than dense inference.

exec
/bin/zsh -lc 'tail -n 150 ../portfolio/prop-floor-methodology-general.md
tail -n 150 ../portfolio/prop-mvp-icpe-upgrade.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
backend block).
Binds: protocol doc non-goals wording, 2L runtime shape, Phase 3.
PROMOTE-TO-DECISION-LOG with B-2.

### B-7 [orchestrator] [type: contract] hardware_target.host is an opaque OpenSSH destination
Decision: `host` is passed verbatim to ssh/scp (`user@host`, bare host, or
~/.ssh/config alias); user/port/key/identity come from SSH config. No new
schema fields for 2K.
Alternatives: adding user/port/key fields to HardwareTarget (additive but
speculative; SSH config already expresses all of it).
Why: zero schema surface; live hardware may prove otherwise, then fields are
added additively (R-015).
Evidence: both lens memos raised as blocker; identical resolution.
Confidence: high. Binds: 2L configs, example configs.

### B-8 [orchestrator] [type: code-shape] Runner ships as an importable zero-dependency module
Decision: the runner lives at `joulewise/adapters/node_worker.py` with ZERO
joulewise imports and stdlib-only top level (vllm imported inside runtime
operations); it is shipped to the node as a single file via scp and invoked
`python3 node_worker.py --task <task.json> --artifacts <dir>`. A shared
`joulewise/adapters/node_client.py` (NodeWorkerClient: composes transport +
clock; ships worker, writes/pushes task JSON, runs it, collects artifacts,
parses status.json, takes B-5 markers) is used by both remote adapters so
protocol logic exists once.
Alternatives: script under scripts/ (not importable — tests would shell out
for everything); per-task-type scripts (four protocol surfaces, drift).
Why: tests import runner functions directly AND exercise it as a real
subprocess; both adapters share one protocol client.
Evidence: lens memos §Q6; importable-module placement is orchestrator
synthesis.
Confidence: high. Binds: 2L (reuses runner + client).

### B-9 [orchestrator] [type: process] Implementation units and shared-file isolation
Decision: five reviewable units, suite green after each: U1 protocol doc pin
+ node_worker.py + tests; U2 ssh_transport.py + node_client.py + tests; U3
nvidia_smi.py + tests; U4 vllm_runtime.py + tests; U5 registry wiring
(ONLY shared-file commit) + example config + fake end-to-end integration
tests. All shared-file edits (adapters/__init__.py only, expected) isolated
in U5's dedicated commit for the post-merge rebase. Exit-checklist/
applicability table NOT touched (tier directive: no live claims; evidence
comes only from the lead's live verification).
Alternatives: transport+telemetry+runtime in one commit (protocol accretes
accidental details before review).
Why: merge-order directive (this stream rebases last); protocol reviewed in

codex
# From Repeatability to Resolvability: Detection Floors for Software Energy Counters

**Thesis:** Software energy counters should be admitted as scientific instruments only after workload-local calibration establishes what effects they can resolve; JouleWise demonstrates this framework rigorously on `powermetrics` and tests whether it transfers to NVML and RAPL without assuming that it will.

## Project brief and steps

JouleWise already contains the spine of a strong measurement-methodology paper: a complete-in-structure MVP draft; a 59-pulse, in-window bracket calibration; worst-case phase-edge integration; separately measured repeatability and never-zero drift; two independent claim gates; and a fail-closed, hash-bound protocol whose refusals are retained as evidence. Its central empirical finding is that the M3 Max instrument is attribution-limited: roughly 30 ms of edge uncertainty across a roughly 33 W transition can misassign about 1 J, while ordinary repeatability is nearer 0.3 J. Because the calibrated floor and the contrast’s own interval are separate requirements, practical phase contrasts need roughly 5 J, and repetition cannot average away the boundary term. No current demonstration number is claim-bearing: D-117 therefore requires three fresh prospective windows—1.5B decode floor with a free prefill rider, 7B decode floor with a prefill rider, and a 1.5B-versus-7B decode contrast—budgeted at 3.14, 3.24, and 2.80 hours respectively. From today, first finish the two-slot calibration-ledger session, D-102 successor builder, four-cell mint, campaign packs, extraction specifications, and synthetic refusal regression; then collect and mint the two floor windows, collect gamma, and populate the MVP tables. Only afterward should this paper add two compact portability sessions on the desktop rig: one NVML GPU-counter characterization and, if the host exposes a usable package-energy counter, one RAPL characterization. The honest target is therefore **five quiet-device sessions: three already required Mac nights plus two estimated 2–3-hour desktop sessions**. If RAPL capability fails at the desk gate, the paper shrinks to a counter-agnostic framework evaluated on `powermetrics` and NVML, with RAPL described only as a future instantiation—not falsely presented as validated.

## Contributions

1. **A counter-agnostic detection-floor calculus.** For sampled-power and cumulative-energy counters, the paper will compose repeatability, null-comparison error, boundary attribution, counter quantization/update behavior, and measured drift. It succeeds only if held-out null effects remain inside the resulting floor.

2. **A complete `powermetrics` case study.** The D-117 floor cells and decode contrast will test whether the method can both refuse marginal effects and support a large effect on one fully named stack. The contribution survives if gamma is refused, but no model-size direction may then be claimed.

3. **A portability battery for NVML and RAPL.** Each backend must mint its own floor; the Mac’s approximately 5 J bar is never transported. A backend passes only if deliberately super-floor effects clear in both directions while sub-floor effects are refused.

4. **Executable refusal evidence.** Stale calibration, counter wrap, unsupported fields, reordered members, missing timestamps, contaminated nulls, and substituted evidence must deterministically prevent claim consumption.

## Experiment plan

| Cell | Design and expected magnitude | Decision |
|---|---|---|
| D-117 alpha/beta | Ten absolute members and ten four-member null ABBA blocks per model; decode and prefill extracted from the same 50 bundles. | Mint four stack-specific floor cells. No decode floor may substitute for prefill. |
| D-117 gamma | Ten ABBA blocks, `7B−1.5B` decode. Historical diagnostic: about 141.29 J, far above the approximately 5 J bar, but the fresh effect is not assumed. | Require floor clearance and an interval-supported positive direction. Otherwise report “not resolvable.” |
| 128-token prefill contrast | Historical diagnostic: 5.81 J point estimate, approximately 4.0 J lower interval edge. | Do not spend a fourth Mac night: this is marginal. Publish floors and the refusal rationale. |
| NVML portability | Pre/post pulse calibration, absolute repeats, identical-label ABBA nulls, and held-out positive/negative duration deltas. Prefer cumulative board-energy readings if supported. | Tentative GPU swing of 200–300 W is **uncertain**: 25–100 ms added work suggests roughly 5–30 J, but Ampere’s reported power may be averaged over one second, making calibration essential. [NVIDIA documents the one-second Ampere average](https://docs.nvidia.com/deploy/nvidia-smi/index.html). |
| RAPL portability | Equivalent CPU pulse and null battery, including counter wrap and update-granularity tests. | A **highly uncertain** 50–100 W active-minus-idle swing makes 100–400 ms deltas roughly 5–40 J. Actual cells are resized only after the capability pilot. |

After each backend’s pilot, define held-out effects at approximately `0`, `0.5F`, `1F`, `2F`, and `4F`, where `F` is that backend’s prospective floor. Failure below `F` means only “not resolvable.” Failure near or above `2F` means the error model or pulse-to-workload transfer is inadequate, and that backend is not admitted.

Desk work includes the D-117 machinery above; a backend-neutral counter schema; counter-wrap, cadence, timestamp, and sampler-overhead probes; generalized pulse drivers; backend-specific condition families and mint pins; frozen effect ladders; and raw-to-figure replay. This does **not** violate the frozen single-request boundary: D-117 remains sequential single-request LLM science, while the portability kernels are separately identified instrument-characterization workloads.

## Hardware and instrument needs

Owned hardware is sufficient for the core: the M3 Max for D-117 and the RTX 3080 Ti rig for NVML. NVML exposes cumulative energy in millijoules on supported devices but can return `NOT_SUPPORTED`, so support must be probed before scheduling collection. [NVML API documentation](https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html). RAPL is conditional on the desktop CPU and OS exposing `energy_uj` and `max_energy_range_uj` through Linux powercap. [Linux powercap documentation](https://cdn.kernel.org/doc/html/latest/power/powercap/powercap.html).

The WT310E wall meter is **not a dependency**. A borrowed-meter session would strengthen absolute-gain and boundary claims, but it cannot validate phase attribution. Treat it as an optional sixth session, not a prerequisite.

## Venue fit and relationship to the MVP

Without portability data, this is the capstone paper’s methods-first framing. With one additional passing backend, it fits an energy/performance workshop or ICPE emerging-research track. With both NVML and RAPL, held-out floor verification, and preferably wall-total validation, it becomes a plausible ICPE full-paper direction.

It reuses MVP §§3–5 nearly intact, the D-117 results section, custody machinery, attribution-limited finding, and most of §6. New material is the backend-neutral abstraction, cumulative-counter treatment, portability battery, and cross-counter comparison of *resolvability*, never a heterogeneous-boundary energy ranking.

## Risks and kill criteria

Kill a backend before a measurement session if its required counter is unsupported, timestamps or wrap behavior cannot be bounded, deterministic pulses cannot be reproduced, telemetry overhead materially perturbs the signal, or a desk pilot projects that a `2F` effect cannot fit inside a four-hour window. Kill the three-counter claim if RAPL is unavailable. Kill “general validation” if NVML’s held-out super-floor contrasts fail; retain it as a documented portability refusal. Never compensate by smoothing, increasing repetitions after seeing results, or borrowing the Mac floor.

## Relation to Ed’s original goals

This serves the modular-instrument and energy-honest reporting goals directly: every future speculative-decoding, MTP, MoE, KV, or split result would inherit a backend-specific resolvability gate. It does not itself deliver a mechanism-level LLM result; it supplies the measurement foundation that prevents those later studies and leaderboards from reporting distinctions their counters cannot support.
tokens used
131,293
# From Repeatability to Resolvability: Detection Floors for Software Energy Counters

**Thesis:** Software energy counters should be admitted as scientific instruments only after workload-local calibration establishes what effects they can resolve; JouleWise demonstrates this framework rigorously on `powermetrics` and tests whether it transfers to NVML and RAPL without assuming that it will.

## Project brief and steps

JouleWise already contains the spine of a strong measurement-methodology paper: a complete-in-structure MVP draft; a 59-pulse, in-window bracket calibration; worst-case phase-edge integration; separately measured repeatability and never-zero drift; two independent claim gates; and a fail-closed, hash-bound protocol whose refusals are retained as evidence. Its central empirical finding is that the M3 Max instrument is attribution-limited: roughly 30 ms of edge uncertainty across a roughly 33 W transition can misassign about 1 J, while ordinary repeatability is nearer 0.3 J. Because the calibrated floor and the contrast’s own interval are separate requirements, practical phase contrasts need roughly 5 J, and repetition cannot average away the boundary term. No current demonstration number is claim-bearing: D-117 therefore requires three fresh prospective windows—1.5B decode floor with a free prefill rider, 7B decode floor with a prefill rider, and a 1.5B-versus-7B decode contrast—budgeted at 3.14, 3.24, and 2.80 hours respectively. From today, first finish the two-slot calibration-ledger session, D-102 successor builder, four-cell mint, campaign packs, extraction specifications, and synthetic refusal regression; then collect and mint the two floor windows, collect gamma, and populate the MVP tables. Only afterward should this paper add two compact portability sessions on the desktop rig: one NVML GPU-counter characterization and, if the host exposes a usable package-energy counter, one RAPL characterization. The honest target is therefore **five quiet-device sessions: three already required Mac nights plus two estimated 2–3-hour desktop sessions**. If RAPL capability fails at the desk gate, the paper shrinks to a counter-agnostic framework evaluated on `powermetrics` and NVML, with RAPL described only as a future instantiation—not falsely presented as validated.

## Contributions

1. **A counter-agnostic detection-floor calculus.** For sampled-power and cumulative-energy counters, the paper will compose repeatability, null-comparison error, boundary attribution, counter quantization/update behavior, and measured drift. It succeeds only if held-out null effects remain inside the resulting floor.

2. **A complete `powermetrics` case study.** The D-117 floor cells and decode contrast will test whether the method can both refuse marginal effects and support a large effect on one fully named stack. The contribution survives if gamma is refused, but no model-size direction may then be claimed.

3. **A portability battery for NVML and RAPL.** Each backend must mint its own floor; the Mac’s approximately 5 J bar is never transported. A backend passes only if deliberately super-floor effects clear in both directions while sub-floor effects are refused.

4. **Executable refusal evidence.** Stale calibration, counter wrap, unsupported fields, reordered members, missing timestamps, contaminated nulls, and substituted evidence must deterministically prevent claim consumption.

## Experiment plan

| Cell | Design and expected magnitude | Decision |
|---|---|---|
| D-117 alpha/beta | Ten absolute members and ten four-member null ABBA blocks per model; decode and prefill extracted from the same 50 bundles. | Mint four stack-specific floor cells. No decode floor may substitute for prefill. |
| D-117 gamma | Ten ABBA blocks, `7B−1.5B` decode. Historical diagnostic: about 141.29 J, far above the approximately 5 J bar, but the fresh effect is not assumed. | Require floor clearance and an interval-supported positive direction. Otherwise report “not resolvable.” |
| 128-token prefill contrast | Historical diagnostic: 5.81 J point estimate, approximately 4.0 J lower interval edge. | Do not spend a fourth Mac night: this is marginal. Publish floors and the refusal rationale. |
| NVML portability | Pre/post pulse calibration, absolute repeats, identical-label ABBA nulls, and held-out positive/negative duration deltas. Prefer cumulative board-energy readings if supported. | Tentative GPU swing of 200–300 W is **uncertain**: 25–100 ms added work suggests roughly 5–30 J, but Ampere’s reported power may be averaged over one second, making calibration essential. [NVIDIA documents the one-second Ampere average](https://docs.nvidia.com/deploy/nvidia-smi/index.html). |
| RAPL portability | Equivalent CPU pulse and null battery, including counter wrap and update-granularity tests. | A **highly uncertain** 50–100 W active-minus-idle swing makes 100–400 ms deltas roughly 5–40 J. Actual cells are resized only after the capability pilot. |

After each backend’s pilot, define held-out effects at approximately `0`, `0.5F`, `1F`, `2F`, and `4F`, where `F` is that backend’s prospective floor. Failure below `F` means only “not resolvable.” Failure near or above `2F` means the error model or pulse-to-workload transfer is inadequate, and that backend is not admitted.

Desk work includes the D-117 machinery above; a backend-neutral counter schema; counter-wrap, cadence, timestamp, and sampler-overhead probes; generalized pulse drivers; backend-specific condition families and mint pins; frozen effect ladders; and raw-to-figure replay. This does **not** violate the frozen single-request boundary: D-117 remains sequential single-request LLM science, while the portability kernels are separately identified instrument-characterization workloads.

## Hardware and instrument needs

Owned hardware is sufficient for the core: the M3 Max for D-117 and the RTX 3080 Ti rig for NVML. NVML exposes cumulative energy in millijoules on supported devices but can return `NOT_SUPPORTED`, so support must be probed before scheduling collection. [NVML API documentation](https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html). RAPL is conditional on the desktop CPU and OS exposing `energy_uj` and `max_energy_range_uj` through Linux powercap. [Linux powercap documentation](https://cdn.kernel.org/doc/html/latest/power/powercap/powercap.html).

The WT310E wall meter is **not a dependency**. A borrowed-meter session would strengthen absolute-gain and boundary claims, but it cannot validate phase attribution. Treat it as an optional sixth session, not a prerequisite.

## Venue fit and relationship to the MVP

Without portability data, this is the capstone paper’s methods-first framing. With one additional passing backend, it fits an energy/performance workshop or ICPE emerging-research track. With both NVML and RAPL, held-out floor verification, and preferably wall-total validation, it becomes a plausible ICPE full-paper direction.

It reuses MVP §§3–5 nearly intact, the D-117 results section, custody machinery, attribution-limited finding, and most of §6. New material is the backend-neutral abstraction, cumulative-counter treatment, portability battery, and cross-counter comparison of *resolvability*, never a heterogeneous-boundary energy ranking.

## Risks and kill criteria

Kill a backend before a measurement session if its required counter is unsupported, timestamps or wrap behavior cannot be bounded, deterministic pulses cannot be reproduced, telemetry overhead materially perturbs the signal, or a desk pilot projects that a `2F` effect cannot fit inside a four-hour window. Kill the three-counter claim if RAPL is unavailable. Kill “general validation” if NVML’s held-out super-floor contrasts fail; retain it as a documented portability refusal. Never compensate by smoothing, increasing repetitions after seeing results, or borrowing the Mac floor.

## Relation to Ed’s original goals

This serves the modular-instrument and energy-honest reporting goals directly: every future speculative-decoding, MTP, MoE, KV, or split result would inherit a backend-specific resolvability gate. It does not itself deliver a mechanism-level LLM result; it supplies the measurement foundation that prevents those later studies and leaderboards from reporting distinctions their counters cannot support.
          "path": "docs/process/state_kernel.json"
        },
        "summary": "Grid campaign lands per AP-1; top-up near-floor cells before L3 wording."
      },
      "authority": {
        "label": "AP-1",
        "path": "docs/contracts/analysis_plans.md"
      },
      "dependencies": [
        {
          "evidence": {
            "label": "R-016 mitigated: off-machine backup and restore proof",
            "path": "docs/risk_register.md"
          },
          "kind": "task",
          "required": "external backup destination live before irreplaceable Window-A evidence accumulates",
          "scope": "retain_evidence",
          "state": "satisfied",
          "strength": "hard",
          "target": "P0-003"
        },
        {
          "evidence": null,
          "kind": "task",
          "required": "Window-A baselines size n",
          "scope": "start",
          "state": "pending",
          "strength": "hard",
          "target": "P2-006"
        }
      ],
      "fallback": null,
      "fences": [],
      "flags": [
        "lead_only"
      ],
      "goal": "q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6).",
      "id": "P2-019",
      "lane": "quiet_mac",
      "priority": "p2_next_slice",
      "rank": 4,
      "status": "blocked",
      "stop_card": null
    },
    "P2-020": {
      "acceptance": {
        "evidence": [
          "Five equal-shape ids-native conditions",
          "Request-energy deltas + MDE verdicts"
        ],
        "pointer": {
          "json_pointer": "/tasks/P2-020/acceptance",
          "label": "P2-020 acceptance",
          "path": "docs/process/state_kernel.json"
        },
        "summary": "Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046)."

codex
# From Software Counter to Scientific Instrument: Phase-Resolved LLM Energy Measurement with Calibrated Refusal

**Thesis:** An Apple software power counter can support reproducible, phase-resolved LLM energy research only when in-session calibration determines both what it can measure and what it must refuse; full characterization, held-out workload prediction, and wall-boundary validation elevate JouleWise from a capstone demonstration to an ICPE-quality metrology paper.

## Project brief and steps

JouleWise currently has a complete paper structure but no live claim-bearing values: historical windows establish the rules and supply design diagnostics, while D-117 requires three fresh prospective windows. The 1.5B floor window contains 10 absolute members and 10 four-member null-ABBA blocks; the 7B floor window repeats that 50-bundle design; both obtain prefill floors from the same bundles at zero additional runtime. The contrast window contains ten 1.5B/7B decode ABBA blocks. Their budgeted durations, including calibration, NEG8 bounds, references, untouched idle, and 20% margin, are 3.14, 3.24, and 2.80 hours respectively. Before any night, desk work must land the two-slot live-calibration ledger session, D-102 acceptance-successor machinery, prefill-capable four-cell mint, three frozen campaign packs, synthetic live-ledger regression, extraction specifications, and readiness packet. After the floor windows pass, mint the combined 1.5B/7B decode-and-prefill floor artifact; after the contrast passes, apply the two distinct claim gates and populate the MVP manuscript.

The ICPE delta should then be disciplined rather than broad: collect the already-designed metrology suite in two or three windows; run the promoted Q4 4×3 workload-shape study in two or three windows; borrow Suzanne Rivoire’s lab WT310E for a pilot and confirmatory whole-machine validation; and package a hardware-free raw-to-figure artifact. Total target: **9–10 claim sessions**, comprising D-117’s three plus **6–7 additional sessions**, with one contingency night reserved but not silently used for outcome-dependent top-up.

## Contributions

1. **Calibrated phase attribution:** Across accepted sessions, the 59-pulse bookends bound edge placement, and every admitted science interval remains inside its authenticated bracket. A systematic or out-of-family calibration falsifies transfer and refuses the window.

2. **Operational detection floors:** Null contrasts at 128, 512, and 2048 output tokens stay inside the declared envelopes, while prospectively sized micro-deltas below the floor are refused and sufficiently above-floor effects clear in both directions. Failure of this ordering falsifies the floor model.

3. **Phase-accounting validity:** Prefill plus decode reconciles with the enclosing request boundary, and prefill does not acquire an above-floor dependence on later decode length. A material residual or slope narrows or defeats phase-resolved claims.

4. **Held-out workload prediction:** A categorical model, \(E=\text{fixed}+\text{prompt level}+\text{decode level}\), fitted without the `(512,256)` and `(4096,512)` cells predicts those held-out cells within the prospectively frozen tolerance. A miss is published and downgrades Q4 from L3 to descriptive L2.

5. **Boundary validation:** On held-out loads, synchronized WT310E measurements determine whether `powermetrics` has a stable gain or load-dependent disagreement for whole-request totals. This does not validate phase allocation; it tests only the absolute whole-machine boundary.

## Experiment plan

The D-117 contrast is low-risk scientifically: the historical diagnostic decode effect is **141.29 J**, roughly 28× the stated 5 J sizing bar and about 10× the historical 7B comparative-floor diagnostic of 14.0 J. Neither historical number is claim-bearing, but both justify the design. The 128-token prefill contrast is excluded: its diagnostic point effect is 5.81 J, but its interval reaches approximately 4.0 J. A refusal would mean “not resolvable at this workload,” not equality.

Metrology window A collects the five-level 1.5B decode ramp (128–2048 outputs; 40 members), three-shape additivity set (24 bundles), the 512-token null rung, and sustained 4096-token holds. Window B collects the 128/2048 null rungs and micro-deltas; a short third window carries extended 120/300/600-second idle holds, stability repetition, or spillover. From diagnostic request energies, the 1.5B decode slope is approximately **0.09–0.10 J/token (uncertain)**: a 64-token delta should be roughly 5.8–6.4 J, while the full ramp spans roughly 170–190 J. Final micro-delta lengths must be computed from the fresh ramp to target approximately 0.5×, 1×, 1.5×, and 3× the minted bar. Near-floor members may honestly refuse.

Q4 uses prompt `{128,512,2048,4096}` × output `{64,256,512}` on the two frozen Qwen2.5 stacks, normally five repetitions per cell and ten only where prospectively identified as near-floor. Decode-length effects should be approximately 12 J per additional 128 tokens for 1.5B and much larger for 7B (**uncertain diagnostics**); long-prompt effects should reach tens of joules. Short-prompt 1.5B effects may not clear 5 J and would become unresolved cells, not fitted evidence. This remains sequential single-request inference and therefore does **not** violate the frozen boundary. Required harness additions are multi-session campaign packing, held-out prediction artifacts, and wall-meter import/synchronization—not batching or concurrency.

## Hardware and instrument needs

Owned: M3 Max/128 GB, pinned MLX/Qwen artifacts, `powermetrics`, and existing calibration/custody machinery. The RTX 3080 Ti and Jetsons are unnecessary. Borrowed: an in-calibration Yokogawa WT310E, safe inline fixture, and its export interface. **Wall-meter dependency: yes for this proposed ICPE-full version**, but no for the underlying MVP. If a qualified loan and safe fixture cannot be secured, do not substitute a consumer plug; submit the metrology core to a workshop or ICPE Emerging track.

## Venue and relationship to the MVP

This is a strong capstone chapter immediately after D-117. ICPE full-track fit comes from the combination of instrument characterization, falsifiable held-out performance prediction, physical-boundary validation, and an artifact reviewers can replay. It reuses the MVP draft’s introduction, related-work gap, measurement model, pulse calibration, floor composition, fail-closed protocol, custody rules, and single-stack limitations. New material is the completed C1–C8 results, cross-day stability, Q4 prediction study, wall regression, and artifact evaluation. Without Q4 or equivalent depth, the work remains an excellent metrology workshop paper rather than a convincing full research-track submission.

## Risks and kill criteria

Kill the ICPE upgrade before spending expansion nights if D-117 cannot mint valid floors; the 150-config metrology suite cannot be repacked below four hours with 20% margin; fresh ramp diagnostics cannot safely place micro-deltas around the operative floor; or Q4 dry runs show missing phases, capped contexts, or a campaign budget above three nights. Kill wall validation if the meter lacks current calibration, safe fixture, adequate synchronized sampling, fixed-range uncertainty at Mac loads, or battery-charge neutralization. A failed Q4 holdout or load-dependent wall discrepancy does not kill the paper—both are publishable findings—but they prohibit predictive or simple-gain claims.

## Relation to Ed’s original goals

This direction directly serves the “energy as a third axis beside quality and latency” goal and the energy-honest leaderboard critique: it supplies the error model and refusal semantics every later comparison needs. Q4 also advances the modular harness by making workload and model axes swappable under one calibrated protocol. It does **not** yet deliver speculative decoding, MTP, MoE routing, KV mechanisms, or split inference. Those remain follow-on studies; forcing one into this paper would weaken its coherent instrument-first contribution.
tokens used
130,264
# From Software Counter to Scientific Instrument: Phase-Resolved LLM Energy Measurement with Calibrated Refusal

**Thesis:** An Apple software power counter can support reproducible, phase-resolved LLM energy research only when in-session calibration determines both what it can measure and what it must refuse; full characterization, held-out workload prediction, and wall-boundary validation elevate JouleWise from a capstone demonstration to an ICPE-quality metrology paper.

## Project brief and steps

JouleWise currently has a complete paper structure but no live claim-bearing values: historical windows establish the rules and supply design diagnostics, while D-117 requires three fresh prospective windows. The 1.5B floor window contains 10 absolute members and 10 four-member null-ABBA blocks; the 7B floor window repeats that 50-bundle design; both obtain prefill floors from the same bundles at zero additional runtime. The contrast window contains ten 1.5B/7B decode ABBA blocks. Their budgeted durations, including calibration, NEG8 bounds, references, untouched idle, and 20% margin, are 3.14, 3.24, and 2.80 hours respectively. Before any night, desk work must land the two-slot live-calibration ledger session, D-102 acceptance-successor machinery, prefill-capable four-cell mint, three frozen campaign packs, synthetic live-ledger regression, extraction specifications, and readiness packet. After the floor windows pass, mint the combined 1.5B/7B decode-and-prefill floor artifact; after the contrast passes, apply the two distinct claim gates and populate the MVP manuscript.

The ICPE delta should then be disciplined rather than broad: collect the already-designed metrology suite in two or three windows; run the promoted Q4 4×3 workload-shape study in two or three windows; borrow Suzanne Rivoire’s lab WT310E for a pilot and confirmatory whole-machine validation; and package a hardware-free raw-to-figure artifact. Total target: **9–10 claim sessions**, comprising D-117’s three plus **6–7 additional sessions**, with one contingency night reserved but not silently used for outcome-dependent top-up.

## Contributions

1. **Calibrated phase attribution:** Across accepted sessions, the 59-pulse bookends bound edge placement, and every admitted science interval remains inside its authenticated bracket. A systematic or out-of-family calibration falsifies transfer and refuses the window.

2. **Operational detection floors:** Null contrasts at 128, 512, and 2048 output tokens stay inside the declared envelopes, while prospectively sized micro-deltas below the floor are refused and sufficiently above-floor effects clear in both directions. Failure of this ordering falsifies the floor model.

3. **Phase-accounting validity:** Prefill plus decode reconciles with the enclosing request boundary, and prefill does not acquire an above-floor dependence on later decode length. A material residual or slope narrows or defeats phase-resolved claims.

4. **Held-out workload prediction:** A categorical model, \(E=\text{fixed}+\text{prompt level}+\text{decode level}\), fitted without the `(512,256)` and `(4096,512)` cells predicts those held-out cells within the prospectively frozen tolerance. A miss is published and downgrades Q4 from L3 to descriptive L2.

5. **Boundary validation:** On held-out loads, synchronized WT310E measurements determine whether `powermetrics` has a stable gain or load-dependent disagreement for whole-request totals. This does not validate phase allocation; it tests only the absolute whole-machine boundary.

## Experiment plan

The D-117 contrast is low-risk scientifically: the historical diagnostic decode effect is **141.29 J**, roughly 28× the stated 5 J sizing bar and about 10× the historical 7B comparative-floor diagnostic of 14.0 J. Neither historical number is claim-bearing, but both justify the design. The 128-token prefill contrast is excluded: its diagnostic point effect is 5.81 J, but its interval reaches approximately 4.0 J. A refusal would mean “not resolvable at this workload,” not equality.

Metrology window A collects the five-level 1.5B decode ramp (128–2048 outputs; 40 members), three-shape additivity set (24 bundles), the 512-token null rung, and sustained 4096-token holds. Window B collects the 128/2048 null rungs and micro-deltas; a short third window carries extended 120/300/600-second idle holds, stability repetition, or spillover. From diagnostic request energies, the 1.5B decode slope is approximately **0.09–0.10 J/token (uncertain)**: a 64-token delta should be roughly 5.8–6.4 J, while the full ramp spans roughly 170–190 J. Final micro-delta lengths must be computed from the fresh ramp to target approximately 0.5×, 1×, 1.5×, and 3× the minted bar. Near-floor members may honestly refuse.

Q4 uses prompt `{128,512,2048,4096}` × output `{64,256,512}` on the two frozen Qwen2.5 stacks, normally five repetitions per cell and ten only where prospectively identified as near-floor. Decode-length effects should be approximately 12 J per additional 128 tokens for 1.5B and much larger for 7B (**uncertain diagnostics**); long-prompt effects should reach tens of joules. Short-prompt 1.5B effects may not clear 5 J and would become unresolved cells, not fitted evidence. This remains sequential single-request inference and therefore does **not** violate the frozen boundary. Required harness additions are multi-session campaign packing, held-out prediction artifacts, and wall-meter import/synchronization—not batching or concurrency.

## Hardware and instrument needs

Owned: M3 Max/128 GB, pinned MLX/Qwen artifacts, `powermetrics`, and existing calibration/custody machinery. The RTX 3080 Ti and Jetsons are unnecessary. Borrowed: an in-calibration Yokogawa WT310E, safe inline fixture, and its export interface. **Wall-meter dependency: yes for this proposed ICPE-full version**, but no for the underlying MVP. If a qualified loan and safe fixture cannot be secured, do not substitute a consumer plug; submit the metrology core to a workshop or ICPE Emerging track.

## Venue and relationship to the MVP

This is a strong capstone chapter immediately after D-117. ICPE full-track fit comes from the combination of instrument characterization, falsifiable held-out performance prediction, physical-boundary validation, and an artifact reviewers can replay. It reuses the MVP draft’s introduction, related-work gap, measurement model, pulse calibration, floor composition, fail-closed protocol, custody rules, and single-stack limitations. New material is the completed C1–C8 results, cross-day stability, Q4 prediction study, wall regression, and artifact evaluation. Without Q4 or equivalent depth, the work remains an excellent metrology workshop paper rather than a convincing full research-track submission.

## Risks and kill criteria

Kill the ICPE upgrade before spending expansion nights if D-117 cannot mint valid floors; the 150-config metrology suite cannot be repacked below four hours with 20% margin; fresh ramp diagnostics cannot safely place micro-deltas around the operative floor; or Q4 dry runs show missing phases, capped contexts, or a campaign budget above three nights. Kill wall validation if the meter lacks current calibration, safe fixture, adequate synchronized sampling, fixed-range uncertainty at Mac loads, or battery-charge neutralization. A failed Q4 holdout or load-dependent wall discrepancy does not kill the paper—both are publishable findings—but they prohibit predictive or simple-gain claims.

## Relation to Ed’s original goals

This direction directly serves the “energy as a third axis beside quality and latency” goal and the energy-honest leaderboard critique: it supplies the error model and refusal semantics every later comparison needs. Q4 also advances the modular harness by making workload and model axes swappable under one calibrated protocol. It does **not** yet deliver speculative decoding, MTP, MoE routing, KV mechanisms, or split inference. Those remain follow-on studies; forcing one into this paper would weaken its coherent instrument-first contribution.

exec
/bin/zsh -lc "for f in ../portfolio/rev-*.md; do printf '%s\\t' \""'${f##*/}"; rg -m1 -i '"'"'^'"\\*\\*?VERDICT|"'^## VERDICT|''^## Verdict|''^# Verdict'"' \""'$f" | tr '"'\\n' ' '; printf '\\n'; done" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
rev-attention-variant-energy.md	## VERDICT: **WEAK** — kill as written; a different, cheaper study survives underneath it. 
rev-batch-concurrency-energy.md	## VERDICT: **WEAK** — and KILL as currently framed. Only the rewritten form survives. 
rev-contamination-characterization.md	**VERDICT: WEAK** (one notch from KILL; survives only in the shrunken forms in §Strengthening). 
rev-cross-runtime-contrast.md	## VERDICT: **WEAK** — do not fund as a paper. 
rev-drift-thermal-science.md	## Verdict: **WEAK** 
rev-energy-nutrition-label.md	## VERDICT: **WEAK** 
rev-floor-methodology-general.md	## VERDICT: **WEAK** — the framing is the best in the portfolio; the evidence plan for it is not fundable, is fenced by a ratified decision, and collapses into the MVP in its most likely branch. 
rev-kv-context-energy.md	**VERDICT: WEAK** (borderline KILL as designed; rebuildable to VIABLE). 
rev-long-generation-dynamics.md	## Verdict: **WEAK** 
rev-moe-routing-energy.md	**VERDICT: VIABLE** (with two blockers that must be closed before any night is committed) 
rev-mtp-energy.md	## VERDICT: **WEAK** 
rev-mvp-icpe-upgrade.md	**VERDICT: WEAK** — sound core, fatal flaw in the thing that makes it an *upgrade*. 
rev-open-explore-advisor.md	**Verdict on (a): credible lineage instincts, executed at half depth. Do not use this 
rev-open-explore-contrarian.md	## Verdict: **WEAK** 
rev-open-explore-registry.md	
rev-open-explore-repo.md	
rev-param-scaling-energy.md	**VERDICT: WEAK** (borderline KILL as scoped; a 1-night shrink is the only fundable residue) 
rev-prefill-scaling-laws.md	**VERDICT: WEAK.** The underlying physics is the most favourable in the portfolio — 
rev-quantization-ladder.md	**VERDICT: VIABLE — but only as a shrunk 3-rung BF16/Q4/Q8 ladder without a 
rev-refusal-as-result.md	**VERDICT: WEAK as proposed** (as a standalone paper). The same material 
rev-spec-decode-energy.md	**VERDICT: WEAK.** High ceiling, correct axis, honest hedging — but the proposal 
rev-split-inference-metrology.md	## Verdict 
rev-tokenizer-honesty.md	**VERDICT: WEAK.** Not a kill on honesty — the proposal is unusually careful about what it 
rev-wall-meter-validation.md	## Verdict: **WEAK** 

exec
/bin/zsh -lc "rg -n '"'^## |''^### |'"\\[PENDING WINDOW C\\]|C-iv|characterization' docs/paper/draft-v1.md | sed -n '1,140p'
sed -n '135,165p' docs/paper/draft-v1.md
sed -n '1,120p' docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md 2>/dev/null || true" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
3:## 1. Introduction
18:4. (C-iv) full instrument characterization: linearity, null response across magnitudes, empirical floor verification, phase-attribution causal consistency, drift/settle;
22:## 2. Background and the gap
24:### Energy-benchmarking rules
28:### Software-counter validation
32:### LLM energy studies
36:The specific gap is therefore not another energy table. To our knowledge, no published work combines phase-resolved LLM energy on consumer silicon, a per-measurement error budget, and validation of `powermetrics` timing attribution under its named measurement boundary (as distinct from validating its absolute counter gain or whole-system energy scale, which would require an external meter). JouleWise fills that gap by making instrument characterization and refusal behavior the primary result; model comparisons are demonstrations of what the characterized instrument can and cannot resolve.
38:## 3. In-window calibration method (C-i)
40:### Measurement model and boundary
46:### Bracketed pulse-train calibration
58:## 4. Detection-floor composition (C-ii)
62:### Repeatability and false-comparison guards
80:### Worst-case timing attribution
86:### Measured, never-zero drift allowance
105:### LABELLED publication and the effective decision bar
117:## 5. Fail-closed collection protocol (C-iii)
121:### Pre-registration and admission
127:### Counterbalanced order
131:### Evidence custody and refusals
141:## 6. Instrument characterization (C-iv)
143:Instrument characterization asks whether the complete measurement system behaves predictably when driven by signals whose qualitative answer is known in advance. The workload is therefore a test signal, not yet the scientific finding. All tests retain the same calibration, admission, custody, and floor rules as the later demonstration measurements. Existing campaign fragments are not promoted where the governing whole-window verdict did not pass; the table marks the required claim-bearing results explicitly.
147:| Linearity | Hold the prompt profile fixed and ramp the requested output from 128 to 2048 tokens. Regress gross request and decode energy on the runtime-observed output count; inspect residual structure as well as the fitted slope. | Energy responds proportionally over the tested dynamic range, and the fitted per-token slope can serve as the known-effect standard for floor probes on this stack. It would not establish linearity outside the tested range or on another stack. | **[PENDING WINDOW C]** |
148:| Null response across magnitudes | Run identical A-equals-B ABBA blocks at short, medium, and long output magnitudes. Evaluate the paired deltas against zero and against the predicted decision envelopes. | The comparison path does not create a directional effect merely because total energy or duration changes, and false contrasts across the tested range are contained by the error model. A non-significant result alone is insufficient; the interval must be interpreted relative to the floor. | **[PENDING WINDOW C]** |
149:| Empirical floor verification | Use the pre-registered linearity slope to create micro-deltas with predicted effects near 0.5, 1, 1.5, and 3 times the declared floor. Test positive and negative directions in counterbalanced blocks. | Sub-floor effects are refused while sufficiently super-floor effects clear in both directions. This is an operational check of the detection boundary, not a validation of the counter's absolute gain. | **[PENDING WINDOW C]** |
150:| Phase-attribution causal consistency | First compare the sum of separately integrated phase energies with the gross energy over their enclosing request. Then vary output length while holding prompt tokens fixed and fit the slope of prefill energy against output length. | Phase accounting is additive within its stated boundaries, and energy assigned to prefill does not acquire a systematic dependence on work that occurs later in decode. Together these tests challenge both missing energy and cross-phase leakage. | **[PENDING WINDOW C]** |
151:| Drift and settling | Place long controlled holds and fixed reference workloads through the window, including start, midpoint, and end references. After operator or stage activity, repeat the reference while recording the time required for thermal and admission observables to stabilize; compare it with the 180 s operating convention. | The measured drift trajectory is contained by the published allowance, and the chosen settling time is supported or revised from observed recovery rather than convenience. Endpoint agreement alone is not enough if the midpoint reveals curvature. | **[PENDING WINDOW C]** |
152:| Between-session stability | Repeat calibrations, null blocks, and floor cells across at least three sessions or days with the full stack identity recorded. | The calibration and floor are stable enough to reuse only under their declared freshness and identity rules, or reveal that a new session must mint a new floor. | **[PENDING WINDOW C]** |
158:Temporal characterization separates slow drift from thermal settling. Start, midpoint, and end references expose whole-window curvature, while post-transition references estimate how long the system takes to return to its admitted state after operator activity or stage churn. Repetition across days tests whether one session's calibration is representative under identical recorded bindings. Internal channel-sum versus package reconciliation is retained as a secondary consistency check. External wall-power regression remains conditional on a suitable meter and would validate totals only; the pulse experiment remains the evidence for phase splitting.
162:## 7. Demonstration results (C-v)
168:## 8. Related work
170:### LLM inference energy measurement
178:### Software power counters and measurement standards
184:### Metrology and experimental discipline
190:### Split and disaggregated inference
Collection does not continue indefinitely through environmental interruptions. Each stage attempt stops at its first member failure, and after the same cause fails a window stage for the third time the window itself closes rather than being retried; in actual operation, nights with three environmental member interruptions were closed and preserved as salvage rather than repeatedly retried. The surviving data may remain diagnostic, but it becomes claim-bearing only if the pre-registered verdict and extraction rules accept the exact resulting basis. This abandon-after-three rule limits outcome-dependent retrying and makes the cost of a noisy environment visible.

The custody chain continues after collection. The immutable corpus is backed up before extraction. The extractor re-authenticates member hashes, required files and cross-file consistency, calibration identity, environment admission, complete campaign membership, cooldown evidence, phase metric identity, and the whole-window drift allowance. It excludes or refuses a cell according to the frozen rules; missing uncertainty never becomes zero. The current artifact boundary is stated honestly: until floor artifacts are independently bound to their source extraction, a claim-bearing floor must be produced by protocol-controlled extraction in the same controlled custody session as the analysis that consumes it. A standalone floor file is not independently claim-licensing.

The refusal log is part of the evaluation, not an embarrassment to omit. It records contaminated members, out-of-family calibration, stale drift evidence, unresolved clock anchors, duplicate occurrences, and below-floor effects. In one real end-of-night case, the governed re-evaluation refused a window because a member's internal clock alignment could not be resolved. Independent adjudication found that refusal correct. The result remained non-claim-bearing: an example of the fail-closed design working as intended, not a software defect to be bypassed.

## 6. Instrument characterization (C-iv)

Instrument characterization asks whether the complete measurement system behaves predictably when driven by signals whose qualitative answer is known in advance. The workload is therefore a test signal, not yet the scientific finding. All tests retain the same calibration, admission, custody, and floor rules as the later demonstration measurements. Existing campaign fragments are not promoted where the governing whole-window verdict did not pass; the table marks the required claim-bearing results explicitly.

| Property | Characterization method | What a passing result would establish | Claim-bearing result |
|---|---|---|---|
| Linearity | Hold the prompt profile fixed and ramp the requested output from 128 to 2048 tokens. Regress gross request and decode energy on the runtime-observed output count; inspect residual structure as well as the fitted slope. | Energy responds proportionally over the tested dynamic range, and the fitted per-token slope can serve as the known-effect standard for floor probes on this stack. It would not establish linearity outside the tested range or on another stack. | **[PENDING WINDOW C]** |
| Null response across magnitudes | Run identical A-equals-B ABBA blocks at short, medium, and long output magnitudes. Evaluate the paired deltas against zero and against the predicted decision envelopes. | The comparison path does not create a directional effect merely because total energy or duration changes, and false contrasts across the tested range are contained by the error model. A non-significant result alone is insufficient; the interval must be interpreted relative to the floor. | **[PENDING WINDOW C]** |
| Empirical floor verification | Use the pre-registered linearity slope to create micro-deltas with predicted effects near 0.5, 1, 1.5, and 3 times the declared floor. Test positive and negative directions in counterbalanced blocks. | Sub-floor effects are refused while sufficiently super-floor effects clear in both directions. This is an operational check of the detection boundary, not a validation of the counter's absolute gain. | **[PENDING WINDOW C]** |
| Phase-attribution causal consistency | First compare the sum of separately integrated phase energies with the gross energy over their enclosing request. Then vary output length while holding prompt tokens fixed and fit the slope of prefill energy against output length. | Phase accounting is additive within its stated boundaries, and energy assigned to prefill does not acquire a systematic dependence on work that occurs later in decode. Together these tests challenge both missing energy and cross-phase leakage. | **[PENDING WINDOW C]** |
| Drift and settling | Place long controlled holds and fixed reference workloads through the window, including start, midpoint, and end references. After operator or stage activity, repeat the reference while recording the time required for thermal and admission observables to stabilize; compare it with the 180 s operating convention. | The measured drift trajectory is contained by the published allowance, and the chosen settling time is supported or revised from observed recovery rather than convenience. Endpoint agreement alone is not enough if the midpoint reveals curvature. | **[PENDING WINDOW C]** |
| Between-session stability | Repeat calibrations, null blocks, and floor cells across at least three sessions or days with the full stack identity recorded. | The calibration and floor are stable enough to reuse only under their declared freshness and identity rules, or reveal that a new session must mint a new floor. | **[PENDING WINDOW C]** |

Linearity and the null ladder test complementary failure modes. A smooth response can still carry an offset, and a zero-centered null can coexist with a nonlinear scale. The micro-delta experiment then closes the loop by using the measured slope to place effects deliberately below and above the declared decision boundary. Success requires the instrument to refuse the former and resolve the latter in both directions; merely observing larger effects with larger workloads is not sufficient.

The causal tests address the most important phase-specific risk. Additivity checks conservation inside the declared request boundary: phase intervals should reconcile with the enclosing total, subject to explicitly labeled setup or gap intervals. Causal invariance checks direction: holding the prompt fixed while increasing later decode work should not change energy attributed to earlier prefill. A nonzero prefill slope would indicate boundary leakage, shared-state coupling that invalidates the simple phase model, or both; it would narrow the claim rather than be explained away.

Temporal characterization separates slow drift from thermal settling. Start, midpoint, and end references expose whole-window curvature, while post-transition references estimate how long the system takes to return to its admitted state after operator activity or stage churn. Repetition across days tests whether one session's calibration is representative under identical recorded bindings. Internal channel-sum versus package reconciliation is retained as a secondary consistency check. External wall-power regression remains conditional on a suitable meter and would validate totals only; the pulse experiment remains the evidence for phase splitting.

Every resulting figure and table will identify the physical unit, operating-system version and build, runtime and relevant library versions, model artifact hash, quantization, tokenizer identity, sampler and output policy, configured and realized batch/concurrency policy, measurement boundary, and telemetry backend. Silent omission is not permitted. Measurements support stack-specific conclusions only; independent replication or a calibrated boundary bridge would be required for hardware-class, vendor-class, or cross-boundary rankings.

## 7. Demonstration results (C-v)

**[RESULT PENDING RE-MINT]**

# Prefill-contrast feasibility desk check — synthesis (2026-08-07)

Sol scout (read-only, high, gpt-5.6-sol) over historical diagnostics;
prompt + full response in this directory. ALL NUMBERS NON-CLAIM /
DIAGNOSTIC.

**Verdict: MARGINAL at the historical 128-token workload.** Best-evidence
matched ABBA diagnostic (decode-contrast window's off-manifest prefill
field, 20v20 members, identical prompt hash): 7B−1.5B prefill delta
5.809930 J point vs the ~5 J practical bar (D-078 cl.11 / D-083 wording
control — two separately enforced gates, not one summed threshold);
composed contrast half-width ~1.81 J puts the interval lower edge ~4.0 J,
BELOW the bar. Independent cross-window subtraction corroborates
(5.903 J).

**Length is the lever:** 1.5B prefill scales ~proportionally with prompt
length (128→4096 tokens predicts within ~3.3%); a prospectively frozen
256-token prompt projects ~11.6 J (~2.3× bar). NO long-prompt 7B corpus
exists — the projection is an extrapolation and workload resizing is a
preregistration decision (estimand change).

**Recommended default (scout + magistrate CONCUR):** claim prefill
FLOORS; keep the model contrast decode-only; state the 128-token
marginality as a limitation. The 256-token contrast is Ed's ruling
(needs_ruling row): +~110 core minutes, likely splits into its own
window.

**Consumed by:** the MVP paper draft §7 "Prospective workload sizing"
(qualitative, no diagnostic joules quoted per the draft's
no-demo-values discipline) and the pending fork/window planning.
Scout flags F1 (D-083 wording preserved), F2 (no long-prompt 7B
evidence), F3 (CLAIMS_STATUS staleness vs D-116 — check before window
freeze) all noted.

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
