# JouleWise Hardening Proposal

**Status:** ADJUDICATED 2026-07-10 (C-028). Received from an independent
Codex review commissioned by Ed. The binding adjudication is
`docs/reviews/2026-07-10-hardening-adjudication.md` — its rulings decide
where this proposal wins, loses, or was already landed. This document is
preserved as received below (one header edit only).

**Repository baseline:** `mpmdw/JouleWise`, `main` at `d9389cd` (2026-07-10)

**Purpose:** Convert a strong hardware-independent research prototype into a calibrated, externally auditable, narrowly useful benchmark without discarding the rigor already built.

## Executive summary

JouleWise’s vacation-period work was directionally sound. With the hardware unavailable, the project usefully retired software risks: bundle contracts, strict re-derivation, adapter seams, workload generation, campaign planning, evidence provenance, failure handling, and prospective statistical rules. Those are not wasted layers. They are the foundation that should make the next hardware campaign much less likely to produce unusable evidence.

The project has now reached a phase transition. The highest-value work is no longer additional breadth. It is closing the loop from physical measurement to calibrated claim, publishing evidence that another person can rederive, and simplifying the operating layer so it does not compete with the science.

This proposal therefore recommends:

1. Freeze new research breadth and hardware backends temporarily.
2. Close the remaining semantic and claim-readiness gaps on `main`.
3. Run a production-shaped Mac shakedown and executable detection-floor calibration.
4. Execute one small, counterbalanced, single-variable campaign through the complete evidence-to-claim path.
5. Publish several complete real bundles and obtain one independent re-reduction.
6. Improve the report and quickstart so users see boundaries, denominators, uncertainty, and eligibility before headline numbers.
7. Compact the governance layer while preserving historical evidence.
8. Resume NVIDIA and split-inference work only after the Mac reference path meets a release gate.

The guiding idea is simple: **protect the measurement kernel, reduce the project-management surface, and make every next feature earn itself through real evidence.**

## 1. Current-state assessment

### 1.1 What should be preserved

The following are core assets, not overengineering:

- Immutable, no-overwrite run bundles.
- Raw telemetry retention and raw-to-derived re-reduction.
- Typed configuration and output schemas.
- Shared bundle-reading and validation policy.
- Explicit measurement-boundary labels and rail manifests.
- Runtime, telemetry, and transport adapter seams.
- Injected clocks and measured-window discipline.
- Structured failure outcomes that still preserve evidence.
- Deterministic mock adapters and a fast end-to-end test substrate.
- Runtime-observed token provenance and output-policy recording.
- A conservative claims ladder with `not resolvable` and downgrade rules.
- Predeclared order, contrast, multiplicity, and fixed-`n` principles.

These elements directly address known failure modes in energy measurement. Removing them would make JouleWise easier to read but less scientifically defensible.

### 1.2 What has outgrown its present value

The following layers should be frozen, consolidated, or archived until the reference campaign is complete:

- Additional research-question expansion.
- New campaign packs unrelated to the reference path.
- New hardware backends beyond live-promoting the existing NVIDIA path.
- Further advisor-site features.
- New orchestration or model-council machinery.
- New state authorities, stop-card formats, or planning protocols.
- Broad refactors of unvalidated hardware paths.
- New benchmark-import breadth.

The project already contains more prospective machinery than empirical evidence. The right response is not to delete the machinery indiscriminately; it is to stop extending it and require the existing pieces to prove themselves end to end.

### 1.3 Correct project identity during hardening

Until the release gate in this proposal is met, describe JouleWise as:

> An auditable research instrument for boundary-labeled local LLM energy measurement, with a working Mac reference path and provisional heterogeneous extensions.

Avoid presenting it as:

- A hardware leaderboard.
- A universal efficiency benchmark.
- A calibrated whole-system energy meter.
- A completed heterogeneous benchmark.
- The first project to study energy in prefill/decode disaggregation.

The defensible research differentiator is narrower: **self-contained, re-reducible measurement bundles and conservative claim gates for heterogeneous local inference, potentially including per-stage local split inference.**

## 2. Hardening goals and non-goals

### 2.1 Goals

By the end of the hardening cycle, JouleWise should be able to demonstrate that:

1. A clean Mac can be prepared from a documented environment and pass a preflight check.
2. A production run records all uncertainty and timing evidence needed by the claim gates.
3. The detection floor is generated from real calibration bundles and consumed automatically.
4. Collection validity, analysis readiness, claim readiness, and publication approval are distinct states.
5. A small comparative campaign is executed in frozen order with a frozen analysis manifest.
6. Every reported comparison is reproduced from raw bundles by one command.
7. At least one person other than the author can validate the released bundle pack.
8. Reader-facing reports lead with the measurement boundary, denominator, raw points, uncertainty, floor status, and claim ceiling.
9. The repository has one current status source and substantially less volatile duplicated prose.

### 2.2 Non-goals

The hardening cycle should not attempt to:

- Complete every research question already documented.
- Fill the entire hardware/model/workload matrix.
- Establish device-class or vendor-wide conclusions.
- Build a public leaderboard.
- Implement new accuracy benchmarks.
- Add additional orchestration frameworks.
- Rewrite the working single-node architecture.
- Make powermetrics equivalent to a calibrated wall meter.
- Finish split inference before the reference measurement path is published.

## 3. Principles governing the work

### Principle A — Evidence before breadth

No new major capability should land unless it either closes a current claim blocker or is exercised by the reference campaign.

### Principle B — Physical validity and artifact validity are separate

`validate-bundle --strict` proves consistency of the recorded artifact chain. It does not prove sensor truth. Reports and code should preserve this distinction explicitly.

### Principle C — One reference path first

The Mac/MLX/powermetrics stack becomes the reference implementation. It should reach calibration, publication, and external re-reduction before other hardware is promoted.

### Principle D — Fail closed at interpretation, not necessarily collection

A run may remain useful raw evidence even when it cannot support a claim. Therefore use separate states:

- `collection_complete`
- `strict_valid`
- `analysis_ready`
- `claim_ready`
- `publication_approved`

Do not use `publishable` as a synonym for “all requested bundles exist and passed structural checks.”

### Principle E — Refactor after observing the live seam

Do not substantially refactor NVIDIA, remote orchestration, or split code before the first live session reveals where the actual boundaries are.

### Principle F — Historical evidence may be archived, not erased

Council outputs, run reports, and decision histories can move under an archive hierarchy. Their provenance should remain, but they should not compete with current operating instructions.

## 4. Phased hardening plan

This plan should be mapped onto existing queue rows and branches rather than copied into a second backlog. Re-check each item against the latest `main`, close work that has already landed, and preserve the repository’s existing task identities.

The phases express dependency order, not a requirement that all work be serialized. CI and documentation improvements may proceed alongside hardware work. In particular, do not waste a scarce quiet-machine window merely because a non-critical lint or packaging task remains open.

### Phase 0 — Scope freeze and baseline capture

**Objective:** Establish one known-good software baseline and prevent additional scope from entering the critical path.

#### Work

- Declare a temporary feature freeze covering new backends, research questions, campaign packs, and site features.
- Reconcile or merge the already-developed correctness branches in dependency order.
- Record the exact reference commit, Python version, macOS version, MLX versions, model artifact hashes, and test result.
- Ensure an external/off-machine destination exists before creating irreplaceable campaign evidence.
- Replace volatile test-count prose with either generated output or non-numeric wording.
- Confirm the current task authority and remove contradictory “next action” sections.

#### Acceptance gate G0

- Clean checkout passes the canonical test suite.
- Mock `run -> validate --strict -> reduce -> report` succeeds.
- Working tree is clean.
- External evidence destination passes a restore test.
- No unresolved ambiguity exists about which branch or commit will produce calibration data.
- The feature freeze is stated in the current status document.

#### Explicitly deferred

- New adapters.
- New question-bank entries.
- Site redesign.
- Large module refactors.

### Phase 1 — Semantic correctness and claim-state separation

**Objective:** Ensure the software cannot describe structurally usable evidence as a scientifically publishable result.

#### Required corrections

1. **Campaign verdict vocabulary**
   - Replace the current one-stage `publishable` verdict.
   - Collection tooling reports completeness and structural validity only.
   - Claim tooling consumes frozen contrasts, floor artifacts, uncertainty evidence, and quality flags.
   - Publication approval remains an explicit final review action.

2. **Configuration safety**
   - Reject unknown configuration keys by default.
   - If backward compatibility requires warning mode, make warnings machine-readable and cause campaign preflight to fail unless acknowledged.
   - Implement `sampling.warmup_seconds` as post-warmup settling outside the measured window, or remove it in a versioned schema change. Do not silently accept a dead experimental control.

3. **Cleanup and contamination**
   - Surface runtime/telemetry cleanup failures in run quality.
   - Prevent a following repetition from starting when a prior runtime may still be alive.
   - Clean remote temporary directories or retain them through an explicit forensic-retention policy.

4. **Metric conventions**
   - Name total-token and generated-output-token metrics unambiguously.
   - Review the throughput convention `N / (t_last - t_first)` versus `(N-1) / span`; either correct it or version and document the convention.

5. **Claim engine integration**
   - Finish frozen analysis-manifest consumption.
   - Implement paired/block contrasts, fixed-`n` handling, multiplicity rules, leave-one-out sensitivity, and three-way floor outcomes.
   - Ensure propagated uncertainty terms actually affect the governed interval or bound rather than appearing as unused metadata.

#### Acceptance gate G1

- A one-bundle campaign can never return `claim_ready` or `publication_approved` for an L2 comparison.
- Unknown configuration keys fail preflight.
- Positive `warmup_seconds` produces a verified clock advance outside the measured window.
- Cleanup failure blocks or contaminates the next member visibly.
- A fixture campaign exercises every claim outcome: directional, unresolved, not resolvable, equivalence-qualified, and invalid.
- The report and command-line output use the same controlled vocabulary.

### Phase 2 — CI and maintainability hardening

**Objective:** Raise confidence in a codebase whose tests are strong but whose modules and dynamic JSON structures are increasingly large.

#### CI changes

- Install the package in CI rather than relying only on repository-root imports.
- Add a console entry point such as `joulewise` while retaining `python -m joulewise`.
- Change the mock CI path to strict validation.
- Add `compileall` and package-build/install smoke tests.
- Add a macOS job that installs the Mac extra and exercises imports, captured powermetrics fixtures, MLX feature detection, and failure messages. Live privileged telemetry remains a manual hardware gate.
- Add a scheduled or release-only corpus validation job when the released reference bundles become available.

#### Static-quality changes

- Add a development extra containing a formatter/linter and coverage tooling; these do not affect the zero-dependency runtime core.
- Start with Ruff formatting/linting and a measured coverage report.
- Do not impose a repository-wide type-checking rewrite immediately. Instead, type new public interfaces and progressively replace `Any` at bundle, schema, and adapter boundaries.
- Add architecture-level tests that prevent report, reducer, and validator interpretations from drifting apart.

#### Module strategy

Do not split modules merely to lower line counts. After the reference campaign:

- Separate core bundle reading from suite validation and provenance validation.
- Separate claim calculation from artifact serialization/validation.
- Keep the remote worker deployable as one file, but consider authoring it as modules and producing the single-file artifact deterministically.
- Extract stable interfaces only after live NVIDIA behavior is observed.

#### Acceptance gate G2

- CI installs the built package on every supported Python version.
- Strict mock E2E runs in CI.
- macOS dependency/import and captured-fixture jobs pass.
- Lint is clean.
- Coverage is measured and published; any threshold is based on the observed baseline rather than chosen arbitrarily.
- No interpretation rule is implemented independently in more than one consumer without a parity test.

### Phase 3 — Production-shaped Mac shakedown

**Objective:** Demonstrate that a real run naturally emits all evidence required by the current reducer and claim gates, without injecting synthetic metadata afterward.

#### Preflight command

Add a read-only `joulewise doctor` or equivalent preflight that reports:

- Supported macOS and architecture.
- Python and package versions.
- MLX/MLX-LM/transformers versions.
- Model path and artifact hash status.
- Tokenizer identity status.
- powermetrics availability and privilege status.
- Available sampler fields.
- External evidence destination and free space.
- Background-load/quiet-machine warnings.
- Current thermal pressure.
- Config/schema compatibility.

The preflight must never alter sudoers configuration automatically.

#### Timing and sampling hardening

- Define whether each powermetrics value represents a preceding interval, a following interval, or a point estimate.
- Preserve the raw interval duration and anchor evidence.
- Run a controlled load-transition experiment to estimate marker-to-sample alignment.
- Record a conservative alignment bound when the exact phase is not identifiable.
- Refuse phase/item claims when window duration, cadence ratio, or alignment bound is inadequate.
- Retain request-level evidence even when short phase attribution is refused.

#### Controller-overhead hardening

- Measure the cost of per-token event construction using an ABBA or equivalent design.
- Compare the standard capture path with a minimal-marker or buffered-token path while preserving generated outputs.
- Treat any difference above the floor as harness overhead and either subtract through a justified model or scope claims to the instrumented stack.

#### Idle and thermal hardening

- Estimate idle uncertainty from independent idle windows or block means, not raw adjacent samples treated as independent observations.
- Quantify autocorrelation and derive an effective sample count if raw-sample intervals are retained.
- Calibrate the idle-drift guard from pre/post windows.
- Verify that positive `warmup_seconds` and the cooldown gate produce stable starting states.
- Record ambient conditions and thermal-pressure state consistently.

#### Acceptance gate G3

A production-shaped Mac run must:

- Pass strict validation.
- Populate clock/alignment, interpolation, idle-drift, cooldown, stack-identity, token, and output-policy evidence naturally.
- Produce metric-specific eligibility: gross request, idle-subtracted request, and short phase/item windows may legitimately differ.
- Be reducible byte-stably from its published raw evidence.
- Produce no synthetic or manually patched uncertainty fields.

### Phase 4 — Detection-floor and boundary calibration

**Objective:** Turn the existing prospective floor machinery into a real, versioned calibration artifact with a known physical scope.

#### Detection-floor campaign

- Freeze the calibration config, order, model artifact, output policy, environment, and sample size before collection.
- Run absolute-repeatability cells and ABBA null-comparison blocks.
- Generate the floor artifact from bundle identities and verify every source hash.
- Exercise the transport/refusal rules against intentionally mismatched stacks, durations, power envelopes, and cadence.
- Record the floor as an operational false-effect guard, not a population tolerance guarantee.

#### Wall or PD bridge

Where feasible, add an external whole-system meter or USB-C PD meter for controlled steady loads and representative inference loads.

The objective is not to force powermetrics rails to equal wall energy. It is to estimate:

- Offset and load-dependent differences.
- Stability of the mapping across workload regimes.
- Whether relative within-stack rankings survive the boundary change.
- Which claim language remains allowed without the bridge.

If no suitable meter is available, retain L1 rail-bound results and same-boundary L2 comparisons only. Do not delay the entire capstone for unattainable whole-system calibration.

#### Acceptance gate G4

- A versioned floor artifact is generated from real bundles through one command.
- Provenance binds to actual bundle bytes and frozen order evidence.
- At least one eligible real run consumes the floor automatically.
- All refusal cases are exercised against real or deliberately modified evidence.
- Calibration scope and expiration/staleness rules are explicit.
- Cross-boundary claims remain disabled unless the bridge passes its predeclared criteria.

### Phase 5 — Reference vertical-slice campaign

**Objective:** Prove the entire path with a modest scientific question before launching the broad matrix.

#### Recommended design

Select one model/runtime/quantization stack and change one principal variable. Suitable examples include:

- Two prompt-length conditions with fixed generated-output policy.
- Two output-length conditions with fixed prompt tokens.
- Two sampler/capture conditions for overhead characterization.
- Two quantizations only if output-equivalence/divergence reporting is ready.

Use:

- At least five predeclared exchangeable blocks, yielding five or more observations per condition.
- Interleaved or ABBA order.
- A fixed sample size.
- Frozen configs and analysis manifest.
- Runtime-observed denominators.
- Raw points in every figure.
- A predeclared primary contrast and a small multiplicity family.

Do not use the existing 1.5B-versus-122B pair as the first comparative proof. Size, architecture, active parameters, quantization, and runtime behavior are confounded. Those observations can remain useful demonstrations but not the reference L2 contrast.

#### End-to-end command

Provide one command that:

1. Verifies preflight.
2. Runs or resumes the frozen campaign.
3. Strict-validates every bundle.
4. Verifies order and prompt/model identities.
5. Loads the floor artifact.
6. Computes the governed contrast and sensitivity checks.
7. Emits the claim verdict.
8. Produces the figure/table/report slice.
9. Builds a publication bundle with hashes.

#### Acceptance gate G5

- Every planned member is accounted for.
- No outcome-dependent top-up occurred; if it did, results are demoted as predeclared.
- The primary contrast has one machine-readable verdict and one reader-facing wording.
- Raw points, confidence interval, floor, boundary, denominator, and stack identity appear together.
- Re-running reduction and analysis from the published pack reproduces the released artifacts.

### Phase 6 — Public reproducibility release

**Objective:** Make the strongest contribution externally exercisable.

#### Release contents

- Versioned source tag.
- Complete mock sample bundle.
- At least two or three complete real Mac bundles, including raw plist evidence where safe.
- The reference campaign pack or a clearly documented representative subset.
- Environment constraints and model/tokenizer identity records.
- One-command pack verification.
- Generated report and primary figure.
- Verified clean-Mac quickstart.
- Citation metadata and a concise contribution statement.
- Security/privacy publication checklist.

#### Privacy and publication controls

Bundles can contain prompt text, responses, local paths, usernames, hostnames, environment details, logs, and device metadata. Add a publication-mode audit that:

- Enumerates potentially identifying fields.
- Uses non-sensitive controlled prompts for public bundles.
- Distinguishes an immutable private source bundle from a derived public pack.
- Records every allowed transformation and hashes the public result.
- Never silently redacts a bundle that is presented as byte-identical to the source.

#### External reproduction

Recruit one technically capable person who did not build the run to:

- Clone the tagged release.
- Verify the bundle pack.
- Rederive the trace, summary, contrast, and report.
- Record the environment and any ambiguities.

A hardware rerun is desirable but not required for the first external audit. Independent re-reduction is the minimum bar; a second-unit rerun is the next bar.

#### Acceptance gate G6 — Reference release

- Public bundle verification succeeds from a clean checkout.
- One external re-reduction succeeds.
- Documentation has no operator-specific absolute paths in the quickstart.
- The report foregrounds claim eligibility and boundary information.
- Source, environment, artifact, and analysis versions are linked.
- No unresolved critical correctness or provenance issue remains on the reference path.

### Phase 7 — Selective heterogeneous promotion

**Objective:** Expand only after the reference path is proven.

#### NVIDIA promotion order

1. Live transport and host-key behavior.
2. Remote lifecycle cleanup and timeout behavior.
3. vLLM streaming/token-count truth; do not equate SSE chunks with tokenizer tokens.
4. nvidia-smi cadence and averaging characterization.
5. Raw-lineage strict validation for NVIDIA evidence.
6. Host CPU/DRAM/NIC boundary treatment for transfer workloads.
7. Same-boundary calibration and floor artifact.
8. A small NVIDIA reference campaign.

Only after these pass should NVIDIA be described as validated rather than fixture-first/provisional.

#### Split-inference promotion order

1. Reconfirm novelty positioning against current 2026 literature.
2. Freeze the exact split estimand and baselines.
3. Validate KV replay correctness and output identity.
4. Measure serialize, transfer, deserialize, and decode as separate stages.
5. Ensure both endpoints’ relevant energy boundaries include transfer work.
6. Run a same-boundary pairing first where possible.
7. Add cross-boundary interpretation only with calibration.

#### Gate G7

No additional backend or split pairing becomes claim-bearing until it independently meets G3–G6 for its own stack and boundary.

## 5. Reader-facing and product hardening

The current static report is useful for debugging but should become claim-oriented.

### Index page

Show, in this order:

1. Run/campaign identity.
2. Stack identity.
3. Measurement boundary.
4. Collection and strict-valid status.
5. Claim-ready status and reasons.
6. Gross request energy.
7. Idle-subtracted request energy.
8. Generated-output-token energy with denominator source.
9. Uncertainty and floor status.
10. Detail link.

Do not show an unlabeled `energy/token` field.

### Comparison page

For every governed contrast, show:

- Raw points.
- Executed order.
- Point estimate and governed interval.
- Detection floor.
- Three-way verdict.
- Boundary and stack identity.
- Output-equivalence/divergence status where relevant.
- Sensitivity and influential-point results.
- Exact allowed wording.

### Quickstart

The first public quickstart should support:

- Mock run with no extras.
- Clean Mac preflight.
- User-supplied model path rather than an author-specific path.
- Safe explanation of powermetrics privilege requirements.
- One real run.
- Strict validation.
- Report generation.
- Common refusal messages and remediation.

## 6. Governance and documentation simplification

### Canonical current documents

Keep only a small current surface:

- `README.md` — what it is, status, quickstart, limitations.
- One current status/roadmap document.
- `TASK_QUEUE.md` or an equivalent ordered work list, but not multiple next-action authorities.
- Measurement methodology and claims ladder.
- Decision log for decisions that still bind behavior.
- Changelog/release notes.

### Historical archive

Move dated material beneath a clearly historical hierarchy:

- Council sessions.
- Model review outputs.
- Stream logs.
- Superseded stop cards.
- Old planning reflections.
- Past run reports.

Archived files remain linkable but are excluded from current-state searches and onboarding instructions.

### Rules

- One fact has one current home.
- Do not duplicate volatile test counts, task state, or next action in reader-facing prose.
- Avoid adding a new state system to solve state-system sprawl.
- Generate only the small pieces that demonstrably reduce drift.
- Treat multi-model review as internal QA, never as independent validation.

### Documentation gate

At release:

- A new contributor can find the current status and next step in under two minutes.
- No current document contradicts the release tag, test command, or claim ceiling.
- Historical content is visibly marked historical.
- The README does not require reading agent-operation documents to use the tool.

## 7. Security and operational hardening

### Local measurement

- Document exactly what the recommended sudoers rule permits.
- Prefer a root-owned wrapper that validates allowed powermetrics arguments if a broad `NOPASSWD` command is otherwise required.
- Never create or edit sudoers automatically.
- Treat benchmark configs as trusted input unless and until an untrusted-input threat model is implemented.

### Remote execution

- Preserve normal SSH host-key verification.
- Validate remote paths and arguments.
- Bind vLLM to loopback unless remote exposure is explicitly required.
- Define cleanup behavior after timeout, disconnect, and controller death.
- Record whether remote state was removed or intentionally retained.
- Review forwarded vLLM extra arguments before advertising shared/institutional use.

### Public bundles

- Add a documented publication review for prompts, outputs, paths, hostnames, usernames, logs, and environment snapshots.
- Keep private raw evidence and public derived packs cryptographically linked without claiming byte identity after redaction.

## 8. Priority order

| Priority | Work | Why now | Exit condition |
|---|---|---|---|
| P0 | External evidence destination | Prevent loss of irreplaceable hardware data | Restore test passes |
| P0 | Merge semantic correctness and claim-state fixes | Prevent misleading campaign/report outcomes | G1 passes |
| P0 | Production uncertainty path | Current real runs cannot naturally clear the intended gates | G3 passes |
| P0 | Floor artifact integration | Existing floor code is not yet claim-consumable | G4 passes |
| P1 | Narrow Mac reference campaign | Proves the entire architecture with real evidence | G5 passes |
| P1 | Publish bundles and external re-reduction | Makes the main contribution externally real | G6 passes |
| P1 | Report and quickstart hardening | Converts an internal instrument into a usable artifact | Clean-user test passes |
| P1 | Documentation compaction | Reduces state drift and maintenance burden | Documentation gate passes |
| P2 | Full Mac matrix | Earned only after the reference campaign | Reference release exists |
| P2 | NVIDIA live promotion | Hardware breadth after reference rigor | NVIDIA G3–G6 equivalent passes |
| P3 | Split-inference campaign | Differentiating stretch result | Hardware, estimand, and boundary gates pass |
| P3 | New imports/leaderboard/site breadth | Low marginal value before adoption | External demand exists |

## 9. Suggested post-vacation sequence

### First two working days

- Reestablish the hardware environment.
- Complete the external backup/restore gate.
- Reconcile pending branches and freeze the reference commit.
- Run full tests, strict mock E2E, and `doctor` manually if not yet implemented.
- Fix campaign/report terminology before generating more evidence.

### First hardware session

- Capability and privilege checks.
- Production-shaped shakedown.
- Timing-alignment/load-transition experiment.
- Idle-window autocorrelation and drift characterization.
- Telemetry/controller-overhead experiment.
- No headline campaign yet.

### Second hardware session

- Frozen detection-floor calibration.
- Generate and validate the floor artifact.
- Exercise real claim eligibility and refusal paths.

### Third hardware session

- Run the narrow reference campaign.
- Re-reduce and analyze immediately while the environment is still available.
- If a correctness problem appears, preserve the failed evidence and fix the instrument before rerunning.

### Following week

- Build the public pack and report.
- Run the clean-machine quickstart.
- Obtain independent re-reduction.
- Tag the reference release.
- Decide whether the next increment is the full Mac matrix or NVIDIA live promotion based on remaining capstone time.

## 10. Success metrics

The hardening effort succeeds when the following statements are true:

- The strongest public result can be traced from a released raw bundle to its wording automatically.
- Another person can reproduce the reduction and analysis without access to the author’s machine.
- A metric displayed prominently is always accompanied by its boundary, denominator, uncertainty, and eligibility.
- Short windows are refused when the sampler cannot resolve them.
- Calibration and floor artifacts are tied to exact source bundles and expire when the stack changes.
- The reference path has one current status source and no contradictory next-action instructions.
- New hardware work is additive rather than requiring changes to the meaning of existing Mac evidence.
- The project can stop after the Mac reference release and still constitute a complete, defensible capstone.

## 11. Post-hardening research agenda

This agenda is intentionally **post-hardening**. It should not be converted into immediate implementation scope or allowed to delay gates G0–G6. Its purpose is to show what the instrument can do once the reference path is calibrated, published, and independently re-reduced.

The most promising niche is not the broad question “does disaggregation or quantization save energy?” Both topics now have substantial prior work. JouleWise can make a more distinctive contribution by asking:

> **Under what workload, precision, interconnect, and hardware conditions does heterogeneous local inference reduce measured energy without violating latency or capability requirements—and when does it merely move cost across a measurement boundary?**

That framing fits the project’s strengths: explicit boundaries, phase-resolved evidence, conservative comparisons, both-end measurement, and small but carefully controlled local hardware campaigns.

### 11.1 Terminology and comparison discipline

Use these terms consistently:

- **Monolithic or colocated inference:** prefill and decode run on one node.
- **Homogeneous disaggregation:** prefill and decode run on separate physical nodes of the same hardware class and materially equivalent software stack.
- **Heterogeneous disaggregation:** prefill and decode run on different hardware classes, such as a consumer NVIDIA GPU for prefill and Apple Silicon or Jetson for decode.
- **Deployable-stack comparison:** hardware, runtime, kernels, model format, and quantization are treated as one system configuration.
- **Hardware-effect comparison:** the model artifact, numerical format, runtime behavior, and workload are controlled tightly enough to attribute a difference primarily to hardware. Most cross-vendor JouleWise comparisons will initially be deployable-stack comparisons, not pure hardware effects.

The distinction matters. An MLX 4-bit model on Apple Silicon and an AWQ model under vLLM on NVIDIA do not isolate a vendor or silicon effect. They answer which complete deployable stack is better under the declared conditions. JouleWise should make the narrower claim unless it can demonstrate artifact and numerical equivalence.

Recent work has already shown that datacenter prefill/decode disaggregation can lose its expected energy benefit depending on request load, the colocated baseline, and KV-transfer path; other work optimizes phase placement and DVFS on H100-class clusters. Lossless KV compression and heterogeneous GPU/CPU/NPU orchestration are also active topics. Quantization studies now jointly evaluate performance, energy, and quality on datacenter GPUs and constrained edge devices. The open space for JouleWise is therefore **auditable consumer/edge crossover measurement**, especially where multiple device classes, transfer energy, and capability retention are evaluated together.

Relevant anchors include:

- [*Revisiting Disaggregated Large Language Model Serving for Performance and Energy Implications*](https://arxiv.org/abs/2601.08833), which shows that benefits depend on load and transfer medium and that disaggregation can consume more energy than an appropriate colocated baseline.
- [*DualScale: Energy-Efficient Disaggregated LLM Serving via Phase-Aware Placement and DVFS*](https://arxiv.org/abs/2602.18755), which studies phase-aware energy optimization on an H100 cluster.
- [*SplitZip: Ultra Fast Lossless KV Compression for Disaggregated LLM Serving*](https://arxiv.org/abs/2605.01708), which makes codec cost part of the online KV-transfer path.
- [*Systematic Characterization of LLM Quantization: A Performance, Energy, and Quality Perspective*](https://arxiv.org/abs/2508.16712), which finds task-, workload-, method-, and GPU-dependent tradeoffs rather than a universal low-bit winner.
- [*Sustainable LLM Inference for Edge AI*](https://arxiv.org/abs/2504.03360), which measures quantization, task accuracy, latency, and hardware energy on Raspberry Pi-class edge hardware.
- [*Silicon Showdown: Performance, Efficiency, and Ecosystem Barriers in Consumer-Grade LLM Inference*](https://arxiv.org/abs/2605.00519), which compares Apple and NVIDIA consumer inference stacks and illustrates why runtime, capacity, precision, and architecture must be considered together.

### 11.2 Ranked research program

| Priority | ID | Research question | Minimum hardware | JouleWise role |
|---|---|---|---|---|
| 1 | HET-PD-1 | Where is the energy crossover between monolithic, homogeneous split, and heterogeneous split inference? | Two same-class nodes plus at least one different node | Attempt to answer |
| 2 | QNT-1 | What is the Pareto frontier between energy reduction and retained task capability across precision levels? | One calibrated node initially; two or more stacks for extension | Attempt to answer |
| 3 | XFER-1 | When does the KV-transfer tax erase phase-placement savings? | Two nodes, controllable wired links, both-end measurement | Attempt to answer |
| 4 | QNT-HW-1 | Does the energy-optimal quantization reverse across Apple, NVIDIA, and edge accelerators? | At least two hardware/runtime stacks | Attempt to answer as a stack effect |
| 5 | PHASE-1 | Is “powerful prefill, efficient decode” actually the optimal direction? | Heterogeneous pair supporting both placement directions | Attempt to answer |
| 6 | MODEL-1 | Can monolithic phase measurements predict split energy on held-out conditions? | Same as HET-PD-1 | Attempt to answer |
| 7 | KVQ-1 | Does lossy or lossless KV compression save net energy after codec work and capability effects? | Split-capable pair with configurable KV representation | Attempt after XFER-1 |
| 8 | LOAD-1 | At what arrival rate does an extra device’s idle cost become worthwhile? | Sustained-load driver and wall/both-end measurement | Attempt to answer |
| 9 | ADAPT-1 | Can a request-aware placement policy beat the best static policy under an SLO? | Mature crossover model and repeatable live scheduler | Pose, then attempt |
| 10 | SPEC-1 | Can a low-power draft device reduce total energy in heterogeneous speculative decoding? | Compatible draft/verifier stacks | Pose; attempt if protocol support matures |
| 11 | CACHE-1 | Is it cheaper to transfer, retain, or recompute KV state across multi-turn sessions? | Cache lifecycle and storage instrumentation | Pose; likely later campaign |
| 12 | GEN-1 | Do observed rankings generalize across physical units, sites, and generations? | Multiple units and external collaborators | Pose; cannot solve on one lab rig |

The first six questions form a coherent capstone-to-paper sequence. HET-PD-1 establishes the crossover surface; QNT-1 adds capability; XFER-1 and PHASE-1 explain the mechanism; QNT-HW-1 tests whether the result is stack-specific; MODEL-1 asks whether the evidence can support prediction rather than only retrospective description.

### 11.3 Core question: heterogeneous versus homogeneous disaggregation

#### HET-PD-1 — Where is the disaggregation energy crossover?

**Question.** For a fixed model, request shape, output policy, and latency requirement, when does heterogeneous prefill/decode placement consume less total energy than:

1. monolithic inference on node A;
2. monolithic inference on node B;
3. homogeneous disaggregation on A-class nodes;
4. homogeneous disaggregation on B-class nodes; and
5. request-level replication across the same number of devices?

**Why it matters.** A split configuration can look efficient if compared only with a weak monolithic baseline. The scientifically interesting result is a crossover map against the best predeclared alternatives at equal service conditions, not a single winning percentage.

**Primary hypothesis.** Heterogeneous placement will be beneficial only in a bounded region: sufficiently compute-heavy prefill to exploit the faster node, sufficiently long or memory-bound decode to exploit the lower-power node, and a KV payload small enough—or a link efficient enough—that transfer does not dominate.

**Independent variables.** Input tokens, requested and observed output tokens, batch/concurrency, model family and size, quantization, P/D direction, link bandwidth, and sustained request rate.

**Primary outcomes.** Both-end joules per completed request, joules per generated token, TTFT, TPOT/inter-token latency, throughput under an SLO, and total KV bytes transferred. Report endpoint energy separately before summing it.

**Required baselines.** Do not use “best observed baseline” selected after seeing the data. Freeze the baseline set and contrasts prospectively. A two-device split should normally be compared with a two-device colocated/replicated service baseline as well as single-device monolithic runs.

**Claim ceiling.** With one unit per class, conclude only that a named pair of stacks has a crossover under the measured conditions. Hardware-class claims require multiple physical units or external reproductions.

#### PHASE-1 — Which device should own each phase?

**Question.** Is the common rule “large accelerator for prefill, efficient device for decode” reliable, or does the optimal direction reverse with context length, model architecture, precision, or interconnect?

Run both A→B and B→A whenever technically feasible. A one-direction campaign cannot distinguish a general phase-affinity result from a convenient implementation choice.

**Mechanistic expectation.** Prefill is often compute-intensive and parallel; decode is often memory-bandwidth- and latency-sensitive. But unified memory, kernel maturity, model fit, MoE routing, host copies, and low-bit dequantization can overturn that shorthand. The output should be a phase-placement map, not a slogan.

#### LOAD-1 — When does adding a device pay for itself?

**Question.** At what arrival rate, burst pattern, and idle timeout does activating a second device reduce energy per completed request after its idle, wake, network, and orchestration costs are included?

This connects single-request lab measurement to an operational decision. Evaluate isolated requests, bursts, and sustained load. Keep queueing and service SLOs explicit. A configuration that saves joules only by making requests wait indefinitely is not an efficiency improvement.

### 11.4 Quantization: consumption versus capability

Treat three interventions separately:

1. **Weight quantization**, which changes model storage, memory traffic, kernels, and sometimes fit/offload behavior.
2. **Activation or compute precision**, which changes arithmetic and kernel execution.
3. **KV-cache quantization or compression**, which changes decode memory traffic and, in split inference, transfer volume.

Combining all three under a label such as “4-bit” makes causal interpretation impossible.

#### QNT-1 — What capability is retained per unit of energy reduction?

**Question.** For a fixed base model and task suite, what energy, latency, and capability frontier results from BF16/FP16, 8-bit, 6-bit, 4-bit, 3-bit, and any supported mixed-precision variants?

**Primary hypothesis.** Energy savings will be nonlinear. Some low-bit formats will improve memory fit and decode efficiency substantially; others will add conversion or poorly optimized kernel overhead and save little or even increase energy. Capability loss will be task-dependent and may show a knee rather than a smooth decline.

**Do not collapse the result to one ratio.** Publish at least three axes:

- measured energy for the fixed workload;
- task capability with uncertainty; and
- latency or SLO attainment.

The main result should be a Pareto frontier. “Joules per correct answer” may be a useful secondary statistic within a fixed benchmark and decoding policy, but it can behave pathologically when accuracy is near zero and can hide whether a configuration is both wasteful and incapable.

**Capability suite.** Use a small, frozen suite spanning at least factual/commonsense selection, mathematical reasoning, and code generation. Prefer tasks with deterministic scoring. Record prompt templates, tokenizer, chat template, sampling policy, maximum output length, stopping rules, and scorer version. Do not infer broad “intelligence” from one benchmark.

**Two estimands are needed.** A fixed-output-budget experiment isolates per-token execution effects. A natural-completion experiment captures the operational reality that quantization can alter output length, stopping behavior, and success rate. Report both rather than allowing changed token count to masquerade as an energy effect.

**Artifact control.** Ideally quantize one frozen base checkpoint with a documented toolchain. If formats differ across runtimes, label the result as a deployable-stack comparison. Comparing arbitrary pre-quantized community artifacts cannot support a clean bit-width effect.

#### QNT-HW-1 — Does the precision ranking reverse across hardware?

**Question.** Is the energy-optimal format on Apple Silicon also optimal on consumer NVIDIA and Jetson-class hardware, or do kernel support, unified memory, tensor-core formats, and dequantization overhead produce rank reversals?

This is more interesting than another per-device leaderboard because it tests an interaction: **quantization × hardware/runtime**. A result such as “4-bit wins on stack A, 8-bit wins on stack B, and FP16 remains competitive on stack C at short outputs” would be both useful and appropriately bounded.

Use a factorial model only where cells are genuinely comparable. When equivalent formats do not exist, publish matched deployable-stack contrasts and avoid pretending the labels represent identical arithmetic.

#### PHASE-QNT-1 — Does precision affect prefill and decode differently?

**Question.** Does lowering weight or activation precision produce different energy effects during prefill and decode, and does the answer change with input/output ratio?

JouleWise’s phase-resolved measurement can contribute here. A single whole-request energy number can conceal a prefill saving and decode regression. Estimate phase-specific joules and duration, with explicit handling of boundary uncertainty. This question should precede any adaptive “use different precision by phase” system proposal.

### 11.5 Transfer and KV-state questions

#### XFER-1 — What is the full KV-transfer tax?

**Question.** As a function of KV size and link condition, what energy is added by serialization, copies, network interfaces, transport, deserialization, and decode-side admission?

Vary prompt length and, where practical, wired link rates such as 1, 2.5, and 10 GbE. Wi-Fi may be included as a separate operational stack, not mixed casually with wired results. Measure both endpoints; if the switch cannot be measured, state that it is outside the boundary.

The useful output is a crossover model:

\[
E_{\mathrm{split}} = E_{\mathrm{prefill},A} + E_{\mathrm{transfer},A,B} + E_{\mathrm{decode},B}
\]

and a condition under which it is lower than each frozen baseline. Do not assume transfer energy is proportional to bytes until the experiment establishes the relevant regime; fixed wake, copy, and protocol costs may dominate small payloads.

#### KVQ-1 — Does compressing KV state save net energy?

**Question.** Do lossless compression, FP8/INT8/INT4 KV representations, or selective/adaptive KV methods reduce total split-inference energy after encoding, decoding, transfer, additional latency, and any capability loss are counted?

Use four linked outcomes: compression ratio, codec energy, transfer energy, and task capability. A reduction in bytes is not itself an energy result. Lossless methods can isolate system overhead without a quality confound; lossy methods then extend the frontier.

This question has an especially useful interaction with link speed. A codec may save energy on 1 GbE, break even on 10 GbE, and lose when transport is already cheap. JouleWise should look for that boundary rather than seek a universal compression winner.

#### CACHE-1 — Transfer, retain, or recompute?

**Question.** For multi-turn sessions, when is it cheaper to retain KV state on the decode node, transfer it again, store it elsewhere, or recompute prefill?

The answer depends on turn interval, cache lifetime, context growth, memory pressure, and device idle behavior. This is a strong future question, but it needs explicit cache-lifecycle events and longer-duration energy measurement. Initially pose it and design the required bundle schema; do not rush it into the first split campaign.

### 11.6 From characterization to prediction and control

#### MODEL-1 — Can JouleWise predict split energy compositionally?

**Question.** Can phase-specific coefficients learned from monolithic runs plus an independently measured transfer curve predict total split energy and latency on held-out prompt/output/link combinations?

This is the research question that could turn JouleWise from a benchmark harness into a useful planning instrument. Train or fit the simplest defensible model first. Candidate terms include fixed request cost, input-token prefill cost, output-token decode cost, KV byte cost, phase duration, and thermal/order block.

Use held-out conditions and report prediction intervals, residual structure, and failure regions. A model that accurately predicts only one stack is still useful if labeled accordingly. Avoid a large learned optimizer until the simple physical model has been falsified.

#### ADAPT-1 — Can an online policy beat the best static placement?

**Question.** Given prompt length, requested output budget, current device state, and link state, can a policy choose monolithic, homogeneous split, or heterogeneous split placement that reduces energy while meeting TTFT and TPOT constraints?

This should come only after HET-PD-1 and MODEL-1. Evaluate against the best frozen static policy on a held-out request trace and include policy overhead. The policy should be allowed to abstain when the estimated difference lies below JouleWise’s detection floor.

#### SPEC-1 — Heterogeneous speculative decoding

**Question.** Can a low-power device act as the draft model while a more capable device verifies tokens, reducing total both-end energy without lowering exact output quality relative to the verifier’s decoding policy?

This is appealing because speculative decoding can preserve the verifier distribution under the correct algorithm, avoiding the ordinary quantization/capability tradeoff. It is also operationally difficult: accepted-token rate, draft/verifier communication, synchronization, and idle overlap all matter. Treat it as a frontier question until compatible runtimes and protocol instrumentation are stable.

### 11.7 Questions JouleWise can responsibly pose but not solve alone

Some conclusions require a larger experimental population than the planned rig can provide:

- **Unit and generation generality:** do rankings survive different physical units, memory capacities, chip bins, OS versions, and ambient environments?
- **Datacenter generality:** do consumer/edge crossover rules transfer to high-speed fabrics, server GPUs, batching, and production schedulers?
- **Whole-system and carbon effects:** do rail-level savings persist at the wall, including PSU losses, displays, switches, cooling, and time-varying grid carbon?
- **Embodied versus operational tradeoffs:** can adding a second device be justified when manufacturing and underutilization are included?
- **User-perceived capability:** do benchmark-preserving quantizations also preserve long-form reliability, calibration, safety behavior, and preference quality?

JouleWise can provide protocols and evidence schemas for these questions, but it should invite multi-site replication rather than imply that a single-machine campaign resolves them.

### 11.8 Minimum experimental design for the first research paper

After hardening, the smallest coherent study would combine HET-PD-1, XFER-1, and a narrow QNT-HW-1 slice:

1. **Stacks:** one Apple Silicon node, one consumer NVIDIA node, and—if available—one lower-power edge node. Add a second same-class node for at least one homogeneous baseline.
2. **Model:** one model family and size that runs on every selected stack without CPU/disk offload. Freeze checkpoint and chat template. Use the closest documented numerical formats and describe any mismatch.
3. **Precision:** one higher-precision reference and one practically important low-bit format; avoid a large quantization sweep initially.
4. **Workloads:** a small factorial grid of short/long input and short/long output, plus a bounded deterministic capability suite.
5. **Placements:** monolithic on every node, both heterogeneous directions, one homogeneous split, and a same-resource replicated/colocated baseline.
6. **Links:** one normal wired link and one throttled or lower-bandwidth condition.
7. **Evidence:** both endpoints, phase timestamps, KV bytes, wall calibration where feasible, randomized/counterbalanced blocks, frozen repetitions, and a predeclared contrast set.
8. **Outputs:** crossover plots, a three-axis energy/latency/capability frontier, raw bundle release, and held-out evaluation of the simple compositional model.

The first paper should not attempt every model, precision, and device. A complete 3-device × 2-precision × 4-workload study with correct baselines and public evidence is more valuable than a sparse matrix of headline numbers.

### 11.9 Research claim rules

For this agenda, add the following rules to the claims ladder:

- Say **stack**, not hardware, when runtime or format is not controlled.
- Say **energy within the measured boundary**, not total energy, unless wall and network boundaries justify it.
- Treat latency and capability constraints as first-class outcomes, not footnotes to energy.
- Report phase and endpoint components before the summed total.
- Use a Pareto frontier instead of a single weighted score unless the weights are externally justified and frozen.
- Distinguish “no detected difference” from equivalence and from inadequate resolution.
- Treat content-dependent MoE or routing claims as associations unless routing telemetry is captured.
- Do not extrapolate from one unit to a hardware family.
- Make the request shape, model artifact, quantization toolchain, runtime, and link part of every result’s identity.

If followed, these constraints make the research more useful, not less ambitious: they turn broad intuitions about heterogeneous inference into falsifiable crossover conditions that another lab can test.

## 12. Final recommendation

Do not interpret the current imbalance—large software/process surface, small hardware corpus—as evidence that the vacation work was a mistake. Given the hardware constraint, much of that work was rational and several layers have already caught real defects.

The risk is continuing the same mode after the constraint disappears.

The recommended pivot is:

> **From proving that every conceivable future experiment has a contract, to proving that one real experiment survives the complete contract.**

Protect the evidence kernel. Finish the physical and statistical loop. Publish the bundles. Get one external reproduction. Simplify the process surface. Then expand.

That sequence gives JouleWise the best chance of becoming both a strong capstone and a genuinely reusable research artifact.

## Appendix A — Immediate “do not build” list

Until G6 passes, do not start:

- Another research-question expansion council.
- Another broad campaign-pack wave.
- Another public status-site feature.
- A new hardware backend.
- A new benchmark import.
- A generalized plugin architecture.
- A leaderboard.
- Carbon or battery extrapolation.
- A major remote-worker refactor.
- New model-review orchestration infrastructure.

## Appendix B — Immediate “protect and finish” list

- Strict raw-to-derived validation.
- Bundle publication tooling.
- Production uncertainty evidence.
- Timing and idle-drift calibration.
- Detection-floor integration.
- Frozen analysis manifest.
- Campaign verdict separation.
- Contrast and claim engine.
- Claim-oriented report.
- Clean Mac quickstart and preflight.
- External bundle re-reduction.

## Appendix C — Positioning update

The related-work chapter should add at least:

- [*Revisiting Disaggregated Large Language Model Serving for Performance and Energy Implications*](https://arxiv.org/abs/2601.08833) (`arXiv:2601.08833`).
- [*DualScale: Energy-Efficient Disaggregated LLM Serving via Phase-Aware Placement and DVFS*](https://arxiv.org/abs/2602.18755) (`arXiv:2602.18755`).
- [The latest Prima.cpp revision and its local multi-device energy evaluation](https://arxiv.org/abs/2504.08791) (`arXiv:2504.08791`).

Recommended novelty language:

> JouleWise contributes an auditable, boundary-labeled evidence pipeline for local LLM energy measurement. Its intended split-inference extension targets per-stage, both-end measurement on heterogeneous consumer/edge devices with self-contained re-reducible bundles. It does not claim to originate energy-aware disaggregated inference generally.
