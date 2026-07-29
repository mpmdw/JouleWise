# Modularity survey — how close the harness is to "every axis swappable by config"

Date: 2026-07-29. Prompted by Ed's standing directive: model, inference
type, model type, workload content, workload size, etc. should each be
modular. Survey executed by a read-only Explore agent over `main`
(mint-tool branch consulted via `git show` where relevant); findings below
carry file:line evidence. One finding is a suspected live defect and is
explicitly UNVERIFIED by the lead (queued as STACK-ID-BIND-01).

## Verdict summary

Roughly 60% of the way there — and it is the hard 60%. The architecture is
modular where modularity is expensive to retrofit (adapter interfaces,
content-addressed provenance) and per-campaign-bespoke where it is cheap
to fix (campaign authoring, code-side literal assertions).

Boundary ruling (Ed-confirmed framing): modularity applies to the
HARNESS; each CLAIM stays deliberately frozen. Ratified hard pins —
e.g. the six-decimal pre-registration floor literal — are anti-modular on
purpose and stay that way.

## Per-axis grades

Legend: MODULAR = swap by config edit only. PARTIAL = config-swappable for
collection but at least one parallel manual edit or regeneration step.
FUSED = library-code edits in two or more places.

| Axis | Verdict | Key evidence |
|---|---|---|
| Model identity (name/revision/source) | PARTIAL | `ModelConfig` (`joulewise/schemas.py:713-735`) flows to bundle metadata (`controller.py:2058`) and artifact identity (`adapters/mlx_runtime.py:1022-1082`); but `configs/campaigns/p2_015_floors/generate_configs.py:31-38` is a module-constant `MODEL` dict with no argv, and a swap needs parallel edits to `MODEL_TAG`, `PLAN_ID`, `RUNS_DIR`, `SUITE_REF`, `SUITE_SHA256`, and the run-ID prefix (:198/:247) or artifact IDs silently keep the old model's name |
| Model family/type | MODULAR by omission | `model.family` is parsed and never branched on; olmoe-bf16, qwen3-4b-mlx and qwen3.5-122b ran the identical path (exploratory 2026-07-17). Flip side: no chat-template/thinking-mode/multimodal seam exists at all (`_prompt_for_workload`, `mlx_runtime.py:754-775`) — a chat/thinking model needs a new prompt-rendering seam |
| Inference runtime + phase split | PARTIAL | Real Protocol registry (`interfaces.py:336-410`, `adapters/__init__.py:117-217`); phase split is generic `phase_start`/`phase_end` events, reducer integrates any phase name. But mlx leaks past the boundary (`cli.py:982-985`, `environment.py:226-228`, `determinism_gate.py:90`, `reduce.py:1610-1616`, `powermetrics_fiducial.py:1327`) and the closed phase-metric list (`detection_floor.py:89-95`) admits only prefill/decode — a new phase is a code edit |
| Workload content | PARTIAL | Suites are hash-pinned config artifacts (`schemas.py:823-830`, verified at `controller.py:651-675`); but only two generator families exist, both hardcoded Python; plan class is classified by substring match (`provenance.py:34-44`); manifests embed literal token IDs so a model swap forces regeneration + re-pinning; no external-dataset ingestion path |
| Workload size | PARTIAL | `WorkloadProfile` fields are config; but `N = 10` and the eight size profiles are module literals (`generate_configs.py:21,55-131`), and `analysis_manifest.py:29-30,542-549` hard-asserts the current condition pairs in code — a differently-shaped registry fails validation without a code change |
| Campaign shape (ABBA, families, refs) | FUSED | Condition-family hashing is generic; but the A/B/B/A block is baked in three places (`generate_configs.py:243-246`, `detection_floor.py:590-609`, `floor_extraction.py:182`) joined by stringly-typed tags; NEG-8 reference structure is library-resident; `_CALIBRATION_SCOPES` needed a library edit for the next campaign (made on `impl/mint-tool`) |
| Telemetry backend | PARTIAL | `TelemetryAdapter` Protocol + registry, three real backends; but analysis is powermetrics-centric below the interface (`reduce.py:115,1421,1469,1534,1739-1741`; ~150 references across controller/doctor/reduce/cli) and other telemetry degrades to a no-anchor path |
| Analysis/claims coupling | PARTIAL | Core is artifact-driven and content-addressed (`floor_stack_identity`, `inputs.py:414-493`; cohort agreement by hash `:967-980`); but AP-2's conditions, experiment IDs, site row labels and legacy bundle IDs are code literals (`analysis_manifest.py:542-549`, `make_figures.py:58-61`, `build_site.py:271-287`, `bundle_read.py:129-155`) |

## Live defect — CONFIRMED (lead-reproduced 2026-07-29, Ed-escalated to immediate fix)

`analysis_engine/inputs.py` `floor_stack_identity` reads only
`artifact_identity.sha256` (`:453`), but the MLX runtime emits
`folded_sha256` for directory-shaped (`file_set`) model artifacts
(`mlx_runtime.py:1064-1072`) — the only shape MLX produces.
**Lead repro against the real a10 bundle**
`runs_window_a10_20260725/p2015-df-ph-decode-abs-r01`: `artifact_identity`
keys are `{algorithm, files, folded_sha256, kind, root, status}`,
`kind=file_set`, no `sha256`; `floor_stack_identity -> None`. Consequence
verified in code: None → per-bundle problem "stack identity is
unavailable" (`inputs.py:970-973`) → cell never enters `bound_ids`
(`:990`) → **claim-side floor binding refuses every real cell**
(fail-closed availability defect; soundness intact). Fixtures use the
single-file `sha256` shape (`tests/test_analysis_integration.py:2493`,
`tests/test_determinism_gate.py:352`), which is why the suite never
catches it.

The mint-side binder already handles the shape —
`scripts/mint_floor_artifact.py` (on `impl/mint-tool`) derives
`artifact.get("sha256") or artifact.get("folded_sha256")` — which is why
the mint worked on real inputs while the claim side would refuse. The two
derivations have FURTHER divergences that would break hash agreement with
the minted `stack_identity_sha256` even after the sha fix: the mint
normalizes the tokenizer identifier path-independently and falls back
across `version`/`mlx_version`/`mlx_lm_version` for runtime version; the
claim side does neither. The repair therefore aligns the claim-side
derivation with the mint derivation and adds a parity regression on a
directory-shaped (real-bundle-shaped) fixture, plus an end-to-end
mint→claim binding regression. Ordered into the live fix round on
`impl/mint-tool` (FIX-7) with delta re-audit; tracked as STACK-ID-BIND-01
until the lead re-verifies binding against a real bundle. Distinct from
the refuted B1 finding (device.boundary placeholders) — do not conflate.

## Roadmap (queued as MODULARITY-01)

In effort order, closing most of the remaining distance:

1. Make the campaign generator a parameterized function over a
   campaign-spec artifact (model, N, size profiles, block pattern, suite
   ref, run-ID prefix) instead of module constants; derive `MODEL_TAG` /
   `PLAN_ID` / prefixes from the spec so a model swap is one file.
2. Replace code-side literal assertions with registry-declared,
   hash-validated closed sets (`analysis_manifest.py:29-30,542-549`;
   `detection_floor.py:87` calibration scopes; `:89-95` phase metrics).
3. Fix the `folded_sha256` read (subject to STACK-ID-BIND-01
   verification) so model identity actually reaches the floor binding it
   is supposed to gate.

Deferred-but-recorded residue: powermetrics references outside the adapter
boundary; no external-dataset ingestion; no chat-template/thinking-mode
seam (relevant to the planned Qwen3 cross-generation follow-up); ABBA
arity welded into three sites; AXI two-arm design welded into interface,
manifest, report schema and CLI.

None of this is needed for tonight's window; the practical payoff arrives
with the Qwen3 cross-generation follow-up and any post-capstone reuse.
