# Stream ledger — suite-substrate (P2-010a, 2026-07-08)

Branch: `suite-substrate`. Scope: P2-010a substrate per report A as amended
by D-044..D-046. Unit 1 = foundation (suite.py, schemas, interfaces,
bundle, mock adapter); unit 2 = read/controller/reduce wiring; unit 3 =
MLX adapter + contracts docs.

### SUB-1 [lead+codex-lens] [contract] Sentinel-gated item_id duplicates

Decision: duplicate `item_id` manifest entries are a validation error
unless every duplicate carries the `sentinel` tag.
Alternatives: blanket uniqueness (rejected — breaks D-040 sentinel
repeats, which are repeated manifest entries); no check (rejected —
ambiguous pairing/prev_item).
Why: D-040 reserves within-bundle repeats for sentinels; FIFO pairing +
`item_index` disambiguation stays sound only when duplication is
intentional and tagged.
Evidence: bug-lens finding 2 (`a1-lens-bugs.md`), lead triage amendment;
`joulewise/suite.py` duplicate check + tests.
Confidence: high. Binds: manifest authors, generators (P2-012/P2-020
sentinels must tag).

### SUB-2 [codex-lens] [contract] Level contiguity is per-block

Decision: a level run closes at its block boundary in BOTH validation and
runtime marker emission; level marker indexing keys on
`(block_id, level_id)`.
Alternatives: global level contiguity (rejected — validation would pass
manifests the runtime splits into duplicate level windows).
Why: validation-accepted manifests must produce well-nested markers.
Evidence: bug-lens finding 3; FIX-3 diff.
Confidence: high. Binds: unit-2 `level_windows()` semantics (a level_id
recurring across blocks yields multiple windows — reader API is
`dict[str, list[Window]]`, already shaped for this).

### SUB-3 [codex-lens] [contract] Pinned manifest vocabularies

Decision: `schema_version` pinned exactly to `suite_manifest.v1`;
`output_policy` ∈ {fixed_budget_exact, natural_eos}; `status_policy` ∈
{none} (grows only by decision).
Alternatives: free strings (rejected — typo'd policies silently change
status semantics).
Evidence: bug-lens findings 4-5; FIX-4/FIX-5 diff + tests.
Confidence: high. Binds: P2-010b/P2-012 manifests.

### SUB-5 [lead-live-gate] [contract] Manifest refs resolve from process cwd (repo root)

Decision: `suite_manifest_ref` is used as given — absolute, or resolved
against the process cwd; example configs use repo-root-relative paths
(`configs/suite_manifests/...`). The CLI convention is run-from-repo-root.
Why: the first live CLI run failed on a config-dir-relative ref that all
680 unit tests had masked (tests construct their own configs; one test
even encoded the wrong convention).
Evidence: live gate catch 1 (trace notes); controller docstring; repinned
config hashes.
Confidence: high. Binds: all future suite configs incl. stream B's.

### SUB-6 [lead-live-gate] [contract] Suite bundles carry rollup provenance

Decision: suite runs synthesize bundle-level `workload_provenance.prompt`
(domain `joulewise.suite_prompt_token_ids.v1` over the canonical JSON
list of per-item token-id hashes in execution order) and
`workload_provenance.output_policy` (default policy, summed budgets,
`stop_condition="suite_completed"`) so `validate-bundle --strict` D-033
checks hold; the strict validator requires the suite domain exactly when
`metadata.suite` is present. Helper: `provenance.suite_prompt_rollup`.
Evidence: live gate catch 2; a3-provenance-fix round; strict-tamper test.
Confidence: high. Binds: every SuiteRuntimeAdapter implementation
(contract doc updated).

### SUB-7 [opus-lens+lead] [contract] Tokenize-window bracketing semantics

Decision: single-prompt runs encode INSIDE the tokenize phase window
(`_generate(prepare_prompt=...)` evaluates the encode between the
markers — an Opus-caught refactor regression, invisible to FakeClock
byte-identity tests). Suite items deliberately encode BEFORE `item_start`
(the marker must carry the real prompt hash), so their per-item tokenize
window is residual — a documented design choice, not drift. Sampler
provenance detection covers both `mlx_lm.make_sampler` and
`mlx_lm.sample_utils.make_sampler` (live catch 3: the installed API is
the latter; fake-only tests could not see it), and suite-level sampler
provenance is first-real-record-wins.
Evidence: Opus review findings 1/3 + live catch 3; advancing-clock
bracket test; live re-run pinned:true.
Confidence: high. Binds: adapter implementations; phase-attribution
consumers.

### SUB-4 [codex-test-audit] [process] Omission whitelist is exact

Decision: the emitted-keys round-trip test whitelists exactly
{suite_manifest_ref, suite_manifest_sha256} as omission-serialized; any
other omitted optional fails the test.
Why: a section-wide whitelist would let future fields silently go
omission-serialized, eroding D-029.
Evidence: test-audit finding 4; `test_workload_to_dict_omits_suite_fields_only_when_none`.
Confidence: high. Binds: schema changes (a third omission field triggers
D-044's revisit clause).
