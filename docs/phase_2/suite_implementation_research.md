# Suite implementation research (C-015 follow-on; 2026-07-08)

STATUS: research input for the P2-010a/P2-012/P2-020 implementation session —
NOT adjudicated design. Produced by a 4-agent research workflow, each report
cross-checked by an independent skeptic (all four verdicts:
sound-with-amendments). THE AMENDMENTS ARE UNRESOLVED REVIEW FINDINGS: the
implementing session must adjudicate each amendment (accept/amend/reject with
recorded disposition) BEFORE building against its report, per the
findings-are-discussed rule. Sections: execution architecture, category
generators, affine ladder, sources. Owner queue rows: P2-010, P2-012, P2-020.
Session record: docs/run_reports/2026-07-08-suite-science-expansion.md.
(Amended 2026-07-08, D-043 back-annotation: the D-034/D-041 reopen that
the execution report's amendment 2 calls for WAS recorded the same day
as D-042 — the suite-BUILD lane is open; campaign-execution ordering and
the interop lane's post-2M gate are unchanged.)


---

# A. Suite execution architecture (P2-010a substrate implementation plan)

**Cross-check verdict: sound-with-amendments. Amendments to adjudicate before implementation:**

1. FALSE BYTE-IDENTITY CLAIM (blocker): BenchmarkConfig.to_dict() is asdict-based (joulewise/schemas.py:363-364), so adding WorkloadProfile.suite_manifest_ref emits "suite_manifest_ref": null into EVERY normalized config.json. The report's "Single-prompt profiles are byte-identical" is false: all five PINNED_CONFIG_SHA256 values (tests/test_schemas.py:32-38) break, and config SHA-256 is run identity (D-001 bundle hash, D-022 run-ID suffixes, D-005 experiment grouping). D-029 pins that any to_dict byte change 'must come back through this log'. Amend: the step-10 decision-log entry must explicitly decide the identity migration; step 2 must update the pinned hashes; restate compatibility as 'existing bundles still validate; same logical configs hash differently pre/post'.
2. SEQUENCING GATE OMITTED: D-041 §5 and the TASK_QUEUE P2-010 row pin the suite substrate as post-2M ('only P2-021 and Window-A capture hardening precede P2-015/2M'), and RUN_STATE.md shows P2-015/2M have not run. The 'Codex-executable' plan must state it executes only post-2M or after Ed records a D-034/D-041 reopen; as written it invites building ahead of the stop-line.
3. MANIFEST CONTENT NOT IN RUN IDENTITY: suite_manifest_ref is a path string, so two runs with different manifest bytes at the same ref share config hash and experiment identity (D-005 grouping, D-022 suffix). The decision-log entry must either add the manifest sha256 to config, or explicitly accept ref-only identity on the dataset_ref precedent with campaign sameness checked by metadata.suite.manifest_sha256 equality (mirroring D-033's 'sameness by hash equality, not membership' rule).
4. D-033 TOKEN-LEVEL PROMPT IDENTITY UNDERSPECIFIED: 'prompt_sha256' in item_start/suite_items.jsonl never says text-hash vs token-ID hash; D-033 explicitly rejected text-only hashing because tokenization is part of the workload. Specify per-item domain-separated token-ID hashes via the existing provenance.prompt_provenance scheme (joulewise.prompt_token_ids.v1), and state which workload_provenance identity blocks (tokenizer/generator/model) suite runs retain.
5. EXACT-TOKEN-SHAPE STATUS GAP: the status table defines capped only for natural_eos at budget; it never defines the fixed_budget_exact UNDERRUN case (emitted < planned budget, e.g. mlx stream_exhausted, which today just records a stop_condition). Under the exact-token-shapes rule such an item must not pass as plain succeeded — assign a status (malformed or a dedicated shape-violation status) or a _suite_problems validation error, and pin it in the table.
6. MANIFEST SKETCH COVERAGE INCONSISTENCY: the report claims the dataclasses cover 'exactly the trimmed C-015 field sketch' with unknown-key rejection, but lists no dataclass for the sketch's `markers:` and `outputs:` blocks (research_question_bank.md C-015 sketch) — a manifest written to the bank sketch would be rejected as unknown keys. Either model those blocks or document that marker vocabulary/output obligations are suite.py constants and those keys are deliberately not manifest schema.
7. FLOOR SEAM MISMATCH: §5's below_floor rule uses max(floor_abs_j, floor_cmp_j) (two floors) but §6's seam takes a single floor_j input. Make the seam carry both floors with per-floor provenance, or define floor_j := max(...) and say so.
8. order_seed HAS NO SOURCE: it is required in suite_start metadata and metadata.suite but is not a field of the C-015 manifest sketch (which has suite_seed + execution_policy.order_policy). Define its derivation (from suite_seed / an explicit manifest field) so it stays deterministic and manifest-derived, never runtime-chosen.
9. WORDING FIXES so reviewers don't chase false constraints: (a) _check_summary checks only for MISSING required keys (subset check, bundle_read.py:505), not 'exactly' _SUMMARY_WRITER_KEYS_V0_1 — that tolerance is precisely why additive suite_metrics works; (b) §6's 're-reducing yields identical fields plus suite_metrics: null' omits that summary_provenance.reducer_version also changes to 0.2.0 (step 8 states it correctly — align §6); (c) §4's 'hashed into metadata.extra' contradicts §3's metadata.suite — the suite block is a TOP-LEVEL metadata.json key written by _write_metadata; metadata.json's 'extra' key is reserved for caller-supplied extra_metadata (cooldown cap-hit, controller.py:646-651).

## Report

# P2-010a Suite Substrate — Implementation-Ready Architecture

Design for the minimal generic suite substrate (D-040 / C-015). All file paths absolute under `/Users/edr/code/JouleWise`.

## 0. Ground rules extracted from the code

- The measured window is bounded by the `sampling_started`/`sampling_stopped` markers (D-026, `controller.py:401-458`, `bundle_read.py:267-296`). One sampling window per bundle; the suite's k items must all execute inside it, back-to-back (D-040: no per-item micro-cooldowns).
- D-013: between `start_sampling` and `stop_sampling` the controller does nothing but block on the runtime. Therefore **the item loop cannot live in the controller** — it is runtime-side work behind a single adapter call, returning one `RuntimeResult` exactly as today.
- Events are the five-key shape, enforced with `set(record) == EVENT_KEYS` (`bundle_read.py:62,188`). All suite structure must ride `metadata` and new `event_type` values — no sixth key.
- `phase_windows()` pairs only `phase_start`/`phase_end` and `token_timestamps()` selects only `token`/`decode` events, so new event types are invisible to every existing accessor: per-item `prefill`/`decode` phase events from suite items will simply sum into `phase_energy_j` (multiple intervals per phase are already supported — documented, intended).
- `_check_summary` requires exactly `_SUMMARY_WRITER_KEYS_V0_1` for succeeded runs; `summary_provenance` is the precedent for an additive, optional-for-validation summary field. The suite summary field follows that precedent so historical bundles stay valid.

---

## 1. Where the item loop lives: runtime adapter, behind a new optional protocol

**Decision: a separate `run_suite` method on a new `SuiteRuntimeAdapter` protocol; `RuntimeAdapter.run_workload` is untouched.**

- `joulewise/interfaces.py`: add

```python
@runtime_checkable
class SuiteRuntimeAdapter(RuntimeAdapter, Protocol):
    def run_suite(
        self,
        config: BenchmarkConfig,
        manifest: SuiteManifest,          # typed object from joulewise/suite.py
        context: RunContext | None = None,
    ) -> RuntimeResult: ...
```

- Rejected alternative: a suite-aware `run_workload`. That would force every adapter (mock, mlx, vllm, llama_cpp, node client) to grow suite branching or fail mid-window; a separate capability method keeps every existing single-prompt path byte-compatible and lets the controller fail fast **before** sampling starts.
- Controller wiring (`joulewise/controller.py`):
  - `_stage_validate`: when `config.workload_profile.suite_manifest_ref` is set — (a) load + schema-validate the manifest file (unreadable/invalid ⇒ `_StageFailure(validate, UNKNOWN_ERROR, ...)` → FAILED, in-bundle, D-011 preserved); (b) check `isinstance(runtime, SuiteRuntimeAdapter)` / `callable(getattr(runtime, "run_suite", None))`; missing ⇒ `_StageFailure(validate, UNSUPPORTED_WORKLOAD, ...)` → UNSUPPORTED (matches the D-012 finding-vs-operational split). Store `self._suite_manifest`.
  - `_stage_prepare`: write the `suite_manifest.json` bundle artifact (new writer method, §4) and record its sha256 — all outside the measured window.
  - `_stage_measured_run`: one-line branch at line ~423: `runtime_result = self._runtime.run_suite(config, self._suite_manifest, self._context)` when a suite manifest is present, else `run_workload` exactly as today. Everything downstream (event extend, outputs write, trace write, flush ordering) is unchanged.
  - `run_experiment` needs **zero changes**: B whole-suite bundles = `workload_profile.repetitions=B` with the existing D-014 cooldown gate between bundles. This is exactly the D-040 `B×k` shape.
- Adapter loop contract (inside `run_suite`): iterate `manifest.items` in manifest order; emit `suite_start`, then per group-boundary `block_start`/`level_start`, per item `item_start` → generation (with per-item `phase_start/phase_end` prefill/decode + `token` events as today) → `item_end`, closing group markers, then `suite_end`. A per-item generation exception is caught **per item**: the item gets `item_end` with `status="runtime_failed"` and the loop continues (C-015: failed items are reported, never silently dropped; the suite stays usable). Only suite-level machinery failure raises out of `run_suite`.

## 2. Marker event schema (rides the existing 5-key shape)

All markers use `phase: "suite"` (safe: `measured_window()` filters on `phase == "measured_run"`, `phase_windows()` on event types). New `event_type` values:

| event_type | metadata (required keys) |
|---|---|
| `suite_start` | `suite_id`, `suite_profile`, `suite_revision`, `suite_manifest_sha256`, `item_count`, `order_seed` |
| `suite_end` | `suite_id`, `items_executed`, `status_counts` |
| `block_start` / `block_end` | `block_id`, `block_index` |
| `level_start` / `level_end` | `level_id`, `level_index` |
| `item_start` | `item_id`, `item_index` (execution position, unique, monotonic), `position`, `block_id`, `level_id`, `condition_id`, `prefix_group_id`, `prev_item` (null for first), `category`, `item_type`, `output_policy`, `prompt_sha256`, `planned_prompt_tokens`, `planned_output_tokens` |
| `item_end` | `item_id`, `item_index`, `status` (runtime-assignable subset only), `prompt_tokens`, `emitted_tokens`, `stop_reason`, `response_sha256` |

- Pairing key: FIFO by `item_id` (mirrors `phase_windows()` pairing by phase name), with `item_index` disambiguating sentinel repeats (D-040 allows within-bundle repeats for sentinels only). `item_index` uniqueness/monotonicity is a *validation* check, not a pairing precondition.
- Blocks/levels are explicit markers (per the C-015 sketch), which requires **manifest validation to enforce that `grouping.block_id`/`level_id` are contiguous runs in item order** (add to `SuiteManifest.validate()`).
- Order/cache metadata (`item_index`, `block_index`, `position`, `prev_item`, `prefix_group_id`, `order_seed`) satisfies the C-015 recording requirement.

## 3. `BundleReader` additions (`joulewise/bundle_read.py`)

Mirror `phase_windows()` — tolerant pairing in accessors, strictness in validation:

```python
@dataclass(frozen=True)
class ItemWindow:
    item_id: str
    item_index: int
    status: str
    window: Window
    start_metadata: dict[str, Any]
    end_metadata: dict[str, Any]

def suite_manifest_raw(self) -> dict | None          # tolerant JSON of suite_manifest.json
def suite_manifest(self) -> SuiteManifest | None     # strict when the file exists; None when absent
def suite_window(self) -> Window | None              # suite_start/suite_end pair
def item_windows(self) -> list[ItemWindow]           # ordered by item_index; unpaired starts skipped
def block_windows(self) -> dict[str, list[Window]]   # FIFO-paired by metadata block_id
def level_windows(self) -> dict[str, list[Window]]   # FIFO-paired by metadata level_id
```

- Validation: new private `_suite_problems()` folded into `problems()` **only when** `suite_manifest.json` exists or `config.workload_profile.suite_manifest_ref` is set (old bundles: zero new checks). Checks: manifest file ↔ config ref consistency; manifest re-validates; `metadata.suite.manifest_sha256` matches file bytes; every manifest item has paired `item_start`/`item_end` inside the measured window; `item_index` unique/monotonic; `item_end.status` ∈ {succeeded, malformed, capped, runtime_failed} (**`excluded_from_claim` and `below_floor` in events are validation errors** — see §5); suite/block/level markers pair; markers nest inside the suite window.

## 4. Schema additions

**Manifest placement: own bundle-root artifact `suite_manifest.json`, not a config extra.** Rationale: `BenchmarkConfig` is strictly key-validated at schema 0.1 and its sha256 is the D-001 experiment identity — embedding a k=24 item list would bloat and destabilize it. The manifest is config-adjacent evidence: written during `prepare` (pre-window) via a new `RunBundleWriter.write_suite_manifest(manifest_dict)` (sorted-key, 2-space JSON + newline, matching the D-001 convention), hashed into `metadata.extra` as `metadata["suite"] = {suite_id, suite_profile, suite_revision, manifest_sha256, item_count, order_seed}` via `_write_metadata`.

**New module `joulewise/suite.py`** (stdlib-only, mirrors `schemas.py` style): dataclasses `SuiteManifest`, `SuiteGenerator`, `AnalysisContract`, `ExecutionPolicy`, `SourceManifest`, `SuiteItem`, `ItemShape`, `ItemSource`, `ItemGrouping`, `ItemDifficulty` — exactly the trimmed C-015 field sketch (bank lines 176–253), each with `from_mapping` validation, `to_dict`, plus `load_suite_manifest(path)` and `suite_manifest_sha256(dict)`. Item prompt source rule: exactly one of `prompt_text` (materialized at manifest-build time — generators run offline, never at execution) or `shape.planned_prompt_tokens` (synthetic). `difficulty` is pass-through quarantined metadata `{axis, value, scale, label, source, quarantine_note}` — validated shape, no behavior. Deferred fields (`scoring.*`, `pair_id`, `holdout_role`, import fields) are **rejected as unknown keys** so the deferral is enforced, not silent.

**`WorkloadProfile` (`joulewise/schemas.py:196`)**: add `suite_manifest_ref: str | None = None` as a **fourth mutually exclusive prompt source** in `validate()` (`prompt_text | prompt_tokens | dataset_ref | suite_manifest_ref`); add to `from_mapping` and `json_schema` (nullable string). Single-prompt profiles are byte-identical; CONFIG_SCHEMA_VERSION stays `"0.1"` (additive per R-015). Suite profiles: `name` + `suite_manifest_ref` (+ `repetitions=B`, `warmup_runs`); `output_tokens` et al. stay None (per-item shape owns them).

**`ItemStatus(str, Enum)`** in `suite.py`: `succeeded | malformed | capped | runtime_failed | below_floor | excluded_from_claim`, with two documented subsets: `RUNTIME_ASSIGNABLE = {succeeded, malformed, capped, runtime_failed}` and `REDUCER_ASSIGNABLE = RUNTIME_ASSIGNABLE | {below_floor}`.

**Adapter warmup for suite configs**: `MlxRuntimeAdapter._prompt_for_workload` gains a branch — suite profile ⇒ synthetic seed prompt (`SYNTHETIC_PROMPT_SEED`, `WARMUP_TOKENS`); honoring `execution_policy.warmup_policy` is deferred.

## 5. Per-item status plumbing (confirmed against C-015 aggregation rules)

| Status | Assigned by | Where | Rule |
|---|---|---|---|
| `succeeded` | runtime | `item_end.metadata.status` | generation completed per `output_policy` |
| `malformed` | runtime | item_end | prompt could not be constructed/encoded from the item, or response violates the item's declared `status_policy` structural check (minimal in P2-010a: prompt-construction failure) |
| `capped` | runtime | item_end | `output_policy == "natural_eos"` and emitted == budget (under `fixed_budget_exact`, hitting the budget is `succeeded`) |
| `runtime_failed` | runtime | item_end | per-item generation exception, caught; loop continues |
| `below_floor` | **reducer only** | `SummaryMetrics.suite_metrics` | downgrade of a runtime-`succeeded` item when item gross energy < `max(floor_abs_j, floor_cmp_j)`; the floor comes from the P2-015 calibration artifact, which does not exist yet — P2-010a ships the seam (`floor_j: float | None` input, `floor_source` provenance string, initially `"none_pending_P2-015"`, so `below_floor` is never assigned yet). Independent of status, the reducer always emits per-item `identifiability` (`identifiable | not_resolvable_sample_count`, `MIN_PHASE_SAMPLES=3` reused) which carries the resolvability concern until floors land. |
| `excluded_from_claim` | **nobody in code** | AP-linked analysis artifacts only | C-015: "an explicit analysis decision with a reason" — confirmed analysis-time. It never appears in events or summaries; bundle validation and the reducer both reject it if seen. It exists in the enum purely as shared vocabulary for AP rows. |

C-015 aggregation confirmation: `below_floor` items still contribute to block/suite window energies (they are inside those windows by construction — nothing to do); `malformed/capped/runtime_failed` items remain in `items[]` with full provenance but are only counted in `status_counts`, never in any claim denominator the reducer computes (the reducer computes no claim denominators — APs do).

## 6. Reducer additions (`joulewise/reduce.py`) — strictly additive

New dataclasses in `schemas.py`:

```python
@dataclass(frozen=True)
class SuiteItemMetrics:
    item_id: str; item_index: int; status: str
    start_s: float; end_s: float
    energy_gross_j: float | None
    identifiability: str
    emitted_tokens: int | None; stop_reason: str | None; response_sha256: str | None

@dataclass(frozen=True)
class SuiteGroupMetrics:   # blocks and levels
    group_id: str
    energy_gross_j: float | None
    identifiability: str
    item_count: int
    status_counts: dict[str, int]

@dataclass(frozen=True)
class SuiteSummary:
    suite_id: str; manifest_sha256: str | None
    planned_item_count: int; executed_item_count: int
    status_counts: dict[str, int]
    items: list[SuiteItemMetrics]
    blocks: list[SuiteGroupMetrics]
    levels: list[SuiteGroupMetrics]
    floor_source: str | None
```

- `SummaryMetrics` gains `suite_metrics: SuiteSummary | None = None` + `json_schema` nullable object. **NOT added to `_SUMMARY_WRITER_KEYS_V0_1`** (follows the `summary_provenance` precedent exactly), so: historical summaries stay valid, `is_complete()` unchanged, and re-reducing an old bundle yields identical fields plus `"suite_metrics": null` (the sanctioned D-028 mutation). Bump `SUMMARY_REDUCER_VERSION` → `"0.2.0"`.
- `reduce._suite_metrics(reader, curve) -> SuiteSummary | None`: returns `None` when `reader.suite_manifest()` is None — **old and single-prompt bundles take zero new code paths**. Otherwise: per-item gross energy via the existing `_integrate` over `item_windows()`; identifiability via `_in_window_sample_count`; block/level energies over `block_windows()`/`level_windows()`; status pass-through + (future) floor downgrade. Called from both `_reduce` and `_zero_window_summary`.
- **Per-item/block/level energies are GROSS-only** (`energy_gross_j`), matching the C-014 phase-metrics rule ("phase metrics are GROSS-only until phase-idle modeling exists") and the AP rule that item windows are attribution evidence, never idle-subtracted claim units. No per-item idle subtraction, no per-item token-normalized metrics.
- Existing headline fields are untouched and automatically correct for suites: `gross_energy_j`/`energy_request_j` span the whole marker-bounded window; `token_count`/`output_token_count` are suite totals set by the adapter on `RuntimeResult`; `phase_energy_j` becomes suite-total prefill/decode via existing multi-interval pairing; `ttft_s` = first item's TTFT (document in the reducer docstring).
- `aggregate.py` ignores the new field (additive) — no change.

## 7. Adapter implementations

- **`joulewise/adapters/mock_runtime.py`** — `run_suite`: deterministic per-item timeline (1 ms/prompt token prefill, 10 ms/output token decode, per D-019 constants), full marker emission, closed-form under `FakeClock`. Fault injection conventions (module-docstring documented): item `tags: ["mock-runtime-failed"]` ⇒ runtime_failed item; `["mock-malformed"]` ⇒ malformed — so controller/reducer status plumbing is testable end-to-end without hardware.
- **`joulewise/adapters/mlx_runtime.py`** — refactor: extract the generation core of `run_workload` (lines ~150–296) into `_generate(prompt, prompt_token_ids, prompt_text, max_tokens) -> _GenerationRecord` (events, token records, text, stop condition); `run_workload` delegates so the single-prompt path is behavior-identical (pinned by existing `test_mlx_runtime.py`); `run_suite` loops items over the same core with per-item try/except ⇒ runtime_failed. Per-item prompt: `prompt_text` encode or `_synthetic_prompt_tokens(planned_prompt_tokens)`; budget from `shape.planned_output_tokens`; EOS suppression per item under `fixed_budget_exact` (existing `_suppress_eos`/`_restore_eos`). Hash computation (sha256 of small texts) inside the window is negligible and is part of the named session ecology.
- **Per-item outputs**: one artifact `outputs/suite_items.jsonl` in `RuntimeResult.output_artifacts` — one JSON line per executed item: `{item_id, item_index, status, prompt_sha256, response_sha256, response_text, stop_reason, prompt_tokens, emitted_tokens, tokens: [{index, timestamp_s}...]}`. Rationale: `write_output` rejects path separators (`bundle.py:347-352`), a single JSONL avoids per-item file spray, and it satisfies the C-015 per-item token/stop/response-hash requirement while keeping full response text as D-002 evidence. No `response.txt` for suites. `workload_provenance` gains `{"suite": {suite_id, manifest_sha256, item_count}}`.

## 8. Explicitly NOT built in P2-010a (C-015 deferrals)

- No scorers, no correctness evaluation, no `scoring.*` manifest fields (rejected as unknown keys).
- No `benchmark_import` manifest, importers, or import-specific source fields (D-041/P2-022 land later).
- No rich difficulty machinery — difficulty is pass-through quarantined metadata only.
- No generator implementations (`affine_mod_ladder_v1` generation is P2-010b; the substrate only *executes* materialized manifests).
- No per-item micro-cooldowns, no within-bundle `r>1` orchestration (sentinel repeats are just repeated manifest entries), no order-rotation tooling (campaign-level, later).
- No `excluded_from_claim` assignment anywhere; no per-item idle subtraction or per-item claim denominators; no report.py rich suite rendering (at most a status-counts line — optional).
- No `CompositeBundleReader`/split-suite interaction; no CLI verb for manifest generation.

---

## Ordered implementation plan (Codex-executable)

Branch: continue on `suite-science-hardening` (or a stream branch off it). Each step keeps `pytest` green.

1. **`joulewise/suite.py` (new)** — `ItemStatus` (+ assignable subsets), all manifest dataclasses with `from_mapping`/`to_dict`/`validate` (mutually exclusive item prompt sources; contiguous block/level runs; unknown-key rejection incl. deferred fields), `load_suite_manifest(path)`, `suite_manifest_sha256(mapping)`; marker event-type constants (`SUITE_START = "suite_start"`, …) so controller/reader/adapters share one vocabulary.
   Tests: `tests/test_suite.py` — round-trip, every validation error message, sha canonicalization, deferred-field rejection.
2. **`joulewise/schemas.py`** — `WorkloadProfile.suite_manifest_ref` (from_mapping, validate 4-way exclusivity, json_schema); `SuiteItemMetrics`/`SuiteGroupMetrics`/`SuiteSummary`; `SummaryMetrics.suite_metrics` + json_schema; `SUMMARY_REDUCER_VERSION = "0.2.0"`.
   Tests: extend `tests/test_schemas.py` — exclusivity matrix, additive-field round-trip, old summary dicts still schema-valid.
3. **`joulewise/interfaces.py`** — `SuiteRuntimeAdapter` protocol (import type via `TYPE_CHECKING` or forward ref to avoid a cycle: `suite.py` must not import `interfaces.py`).
   Tests: extend `tests/test_interfaces.py` — protocol isinstance checks; existing adapters still satisfy plain `RuntimeAdapter`.
4. **`joulewise/bundle.py`** — `RunBundleWriter.write_suite_manifest(mapping) -> Path` (sorted-key JSON, `_require_open`, refuse double-write).
   Tests: extend `tests/test_bundle.py`.
5. **`joulewise/adapters/mock_runtime.py`** — `run_suite` + fault-injection tags.
   Tests: extend `tests/test_mock_adapters.py` — FakeClock closed-form marker timestamps, per-item statuses, `suite_items.jsonl` content, token/event totals.
6. **`joulewise/bundle_read.py`** — `ItemWindow`, `suite_manifest_raw/suite_manifest/suite_window/item_windows/block_windows/level_windows`, `_suite_problems()` folded into `problems()` (gated on suite presence).
   Tests: extend `tests/test_bundle_read.py` — pairing (incl. sentinel repeat item_id, unpaired start, out-of-order), each `_suite_problems` failure (sha mismatch, missing markers, illegal status `excluded_from_claim`/`below_floor` in events, non-monotonic item_index), **and a regression test that a pre-suite fixture bundle produces byte-identical `problems()` output**.
7. **`joulewise/controller.py`** — `_stage_validate` manifest load + capability check (two structured failure paths); `_stage_prepare` artifact write + `self._suite_manifest_sha256`; `_write_metadata` `extra["suite"]` block; `_stage_measured_run` one-line dispatch to `run_suite`.
   Tests: extend `tests/test_controller.py` — happy suite run end-to-end on mock (marker ordering vs `sampling_started/stopped` in flushed `events.jsonl`), `UNSUPPORTED_WORKLOAD` when the runtime lacks `run_suite`, FAILED with complete bundle on unreadable/invalid manifest, `run_experiment` with a suite profile ⇒ B bundles + manifest (D-040 shape).
8. **`joulewise/reduce.py`** — `_suite_metrics(reader, curve)` with floor seam (`floor_source="none_pending_P2-015"`), wired into `_reduce` and `_zero_window_summary`; docstring notes (gross-only items, suite-total phase energy, suite TTFT semantics).
   Tests: extend `tests/test_reduce.py` — closed-form per-item/block/level energies on a synthetic trace; identifiability flag under sparse sampling; runtime_failed/malformed items appear with `energy_gross_j` but only in `status_counts` provenance; **golden test: reducing an existing single-prompt fixture bundle yields the previous summary plus `suite_metrics: null` and reducer_version bump, nothing else changed**; `_check_summary` still accepts old summaries.
9. **`joulewise/adapters/mlx_runtime.py`** — extract `_generate`, delegate `run_workload`, add `run_suite`, suite warmup branch in `_prompt_for_workload`.
   Tests: extend `tests/test_mlx_runtime.py` with the existing fake-`mlx_lm` pattern — single-prompt event stream byte-identical after refactor; suite run markers/hashes/statuses; per-item exception ⇒ runtime_failed + loop continues.
10. **Docs (land with implementation per C-015)** — `docs/contracts/run_bundle_layout.md`: `suite_manifest.json` artifact, marker event types + required metadata keys, `outputs/suite_items.jsonl`, `metadata.suite`, summary `suite_metrics` (optional for validation); `docs/contracts/adapter_contracts.md`: `SuiteRuntimeAdapter.run_suite` contract (per-item exception containment, marker obligations, status assignment table); decision-log entry pinning the §1/§4/§5 choices (run_suite-vs-run_workload, manifest-as-artifact, status-assignment ownership, gross-only item energies); `TASK_QUEUE.md` P2-010a row update.
11. **Lead-side verification (not delegable)** — full `pytest`; a live mock suite run via the CLI with `validate-bundle` + `reduce` re-run on the produced bundle; eyeball `events.jsonl` marker nesting and `suite_items.jsonl`.

### Key risk to watch in review
Step 9's `run_workload` refactor is the only place an existing measured path can drift — require the fake-mlx event-stream byte-identity test before accepting it. Step 6/8 byte-compat golden tests are the strict re-reduction guarantee; do not let them be weakened to shape-only assertions.


---

# B. jw_mixed_v1 content generators + content-sensitivity sentinel

**Cross-check verdict: sound-with-amendments. Amendments to adjudicate before implementation:**

1. Fix Part 4 Item A: the chain 14 x3 -9 //5 +7 yields 13 (or 16 under the day-total reading), never the claimed 'answer 15 (verified at generation)'; and 33 (or 47) is not divisible by 5, contradicting the stated integer-intermediate constraint. Make the DAG constructor enforce divisibility for int-div steps and re-verify every published worked example — a 'verified' example that fails verification will be refuted under the repo's adversarial-review protocol.
2. Reconcile budget bookkeeping in the item sketches: Part 1 pins preamble~35 + instruction~60, leaving ~417 background tokens at B=512, but Item A claims a 320-token background (~97 tokens unaccounted); Part 3 pins prologue~8 + instruction~35, leaving ~469, but states the passage is '~430 tokens'.
3. Resolve drawn-range vs pinned-default contradictions: n_constraints=4 vs '3-5 clauses', n_steps=5 vs '4-6 operations', n_fields=7 vs '6-9 fields' (Item B uses 8), and 'seed-parity selected' vs logic_variant_rate=0.25 (parity gives 50%, not 25%). State per parameter whether it is pinned or DRBG-drawn from a range.
4. Make the prefill caveat binding: per the C-014 standing rule in docs/contracts/analysis_plans.md, short-prefill windows with <3 power samples report 'not resolvable', and at 1 Hz a 512-token prefill will not clear 3 samples. Part 3's 'distinguishable via prefill energy/TTFT/phase mix' holds only at the 4096 panel shape; the common-stratum promise must be request-window metrics + TTFT only, matching AP-4's 'optional gross phase-window descriptors only'.
5. Pin BOS handling for AP-6 equal-shape conditions: text-path items realize BOS + 511 content tokens (add_special_tokens=True, mlx_runtime.py:316) while the ids-native random-token sentinel and the existing repeated-seed prompt_tokens path emit 512 raw ids with no BOS. Either prepend the BOS id to ids-native conditions or record BOS presence as part of realized shape, so 'five equal-shape conditions' is literally true.
6. Do not silently redefine C5-W.4's token-matched leg: the RQ bank plans FLORES for BOTH semantic-matched and token-matched multilingual legs (8 languages); substituting the synthetic interlingua for the token-matched half changes the fertility-vs-semantics pairing and needs a discussed decision-log entry (global rule 2: findings discussed, not silently applied). Also reconcile the pinned 6-language synthetic set with the bank's 8-language FLORES set, and either name a license-clean provenance for the Devanagari 'realistic frequency weights' or relabel them as invented weights.
7. Replace 'sha256 over the sorted concatenation' of tokenizer files with a canonical per-file manifest of (filename, sha256) pairs — raw concatenation is ambiguous at file boundaries and unauditable when a file is absent — and clarify that item_id's tokenizer_id folds in tokenizer_files_sha256 (the report's own argument that identifier+revision is insufficient otherwise leaves item_id under-pinned).
8. Specify that the expected-vs-realized token_ids_sha256 assertion runs outside the measured window (post-run validation/reduce), per D-013's no-controller-work-during-window rule; the realized hash is already computed inside run_workload's return path, so the comparison must add no in-window work.
9. Pin the sampler before asserting 'greedy' in output_policy/manifests: the adapter passes no sampler to mlx_lm.stream_generate, so greediness currently rests on an unrecorded mlx_lm default; record sampler/temperature in workload provenance or pin it in the adapter call.
10. Recirculate the missing sections before implementation: Part 6 is truncated mid-sentence and Part 7 (random-token sentinel) plus the explicit mapping of the five AP-6 conditions to generators are absent and therefore unreviewed.

## Report

# jw_mixed_v1 Content-Generator Design — six categories + content-sensitivity sentinel

Design for deterministic, seed-derived, license-clean synthetic prompt generators hitting exact prompt-token budgets on a pinned tokenizer, for the P2-012 identification core (common-shape stratum 512/256 `fixed_budget_exact`, AP-4) and the P2-020 content-sensitivity sentinel (AP-6). Grounded in repo reality: `joulewise/adapters/mlx_runtime.py` (`_prompt_for_workload`, `_synthetic_prompt_tokens`, `_tokenizer_identity`), `joulewise/provenance.py` (`prompt_token_ids_sha256`, `prompt_provenance`), `joulewise/schemas.py` (`WorkloadProfile` with mutually exclusive `prompt_text` / `prompt_tokens` / `dataset_ref`), and `docs/contracts/analysis_plans.md` AP-4/AP-6.

---

## Part 0 — Shared infrastructure (all six generators)

### 0.1 Item identity and reproducibility contract

An item is fully determined by the tuple:

```
item_id = sha256("jw_mixed_v1.item\0" + generator_id + "\0" + generator_version
                 + "\0" + str(seed) + "\0" + str(prompt_budget) + "\0" + tokenizer_id)
```

- `generator_id`: e.g. `jw.chat`, `jw.code`, `jw.summ`, `jw.reason`, `jw.json`, `jw.multiling`, `jw.sentinel.*`.
- `generator_version`: semver string embedded in the module, bumped on ANY change to templates, word banks, or trim logic. Word banks are module constants; their sha256 is folded into the version check at import time (a `BANK_HASH` assertion) so silent bank edits fail loudly.
- `tokenizer_id`: the existing `_tokenizer_identity` (identifier + revision) is not sufficient for reproducibility — pin `tokenizer_files_sha256` = sha256 over the sorted concatenation of `tokenizer.json` / `tokenizer_config.json` / `merges.txt` / `vocab.json` (whichever exist in the model dir). This goes in the item's `source_manifest` alongside the identifier/revision. Rationale: HF revisions can be re-tagged; file hashes cannot.
- Item seeds derive from a suite master seed: `seed_i = int.from_bytes(sha256("jw_mixed_v1.seed\0" + master + "\0" + category + "\0" + str(item_index))[:8])`.

### 0.2 Deterministic randomness: do NOT use `random.Random`

CPython's Mersenne Twister core is stable, but method-level behavior (`randrange` argument handling, `sample` internals) has shifted across versions. For an auditability project the right call is a ~15-line SHA-256 counter-mode DRBG (stdlib `hashlib` only):

```
class Drbg:
    def __init__(self, seed_bytes): self.key, self.ctr = seed_bytes, 0
    def _block(self): self.ctr += 1; return hashlib.sha256(self.key + self.ctr.to_bytes(8,"big")).digest()
    def u64(self): return int.from_bytes(self._block()[:8], "big")
    def below(self, n):            # rejection sampling, exact-uniform, deterministic
        lim = (1<<64) - ((1<<64) % n)
        while True:
            x = self.u64()
            if x < lim: return x % n
    def choice(self, seq): return seq[self.below(len(seq))]
```

Every generator draws exclusively through this. Reproducibility then depends only on SHA-256, never on CPython internals. Record `drbg: "sha256-ctr-v1"` in the manifest.

### 0.3 Budget definition (must match the adapter, or nothing else matters)

The budget B is defined as `len(tokenizer.encode(prompt_text, add_special_tokens=True))` — exactly the count the MLX adapter realizes via `_prompt_for_workload`'s `prompt_text` path (`_encode(..., add_special_tokens=True)`). So if the tokenizer prepends BOS, the BOS is inside the 512. No chat template is applied (raw-completion mode, matching current adapter behavior); if a chat-template mode is ever added, it becomes part of `tokenizer_id`'s scope and the budget re-pins. This must be stated in the generator docstring and the source manifest (`token_accounting: "encode_add_special_true"`).

### 0.4 Exact token-shape: the two-stage grow/greedy-fill algorithm (harness never pads/truncates)

Every generator emits prompts as **prologue + body-units + elastic-slot + epilogue**, where prologue/epilogue are fixed per item (the instruction machinery that must survive intact) and the elastic slot is a category-appropriate region designed to absorb fine adjustment. The algorithm, common to all six:

1. **Coarse stage (unit granularity, approach from below).** Generate body units (sentences / code lines / record fields — each ~5–40 tokens) from the DRBG. After each unit, re-encode the FULL assembled prompt. Add units while `count <= B - Δ` (Δ = 24 default headroom). Never exceed B in this stage; if a unit overshoots past B, drop it and stop (units are tried in DRBG order; no reordering).
2. **Fine stage (atom granularity, greedy fill with full re-encode).** Append filler atoms into the elastic slot from a fixed, ordered, category-specific atom ladder (multi-word phrases → single words → single characters/digits). After EACH candidate append, re-encode the full prompt — never sum per-fragment counts, because BPE merges across boundaries make concatenated counts unsound. Accept the atom iff new count ≤ B. Walk the ladder greedily until count == B.
3. **Backtracking guarantee.** If the ladder is exhausted at count = B−k with no atom of realized cost ≤ k, pop the last accepted atom and continue from the next ladder position (bounded depth, default 8). The ladder's tail is single ASCII characters/digits preceded by a space, which realize as 1 token in essentially every BPE context — but this is verified empirically per item, never assumed. If exact B is still unreachable (pathological tokenizer), the generator raises — **fail closed**, consistent with the repo's validator posture. No silent pad/truncate anywhere.
4. **Boundary hygiene.** The elastic slot terminates with a hard newline before the epilogue so a trailing atom cannot merge into the epilogue's first token — and because step 2 re-encodes the whole prompt, any merge that does occur is caught, not assumed away.
5. **Verification + recording.** Final artifact: `prompt_text`, `realized_token_count` (asserted == B), `token_ids_sha256` via the existing `prompt_token_ids_sha256`, `text_sha256`, plus `elastic_fill_tokens` (how many tokens the fine stage contributed — a useful audit stat; if it's ever a large fraction of B, the item is mostly filler and the manifest shows it).

Why text-canonical rather than token-id-canonical: trimming token ids directly to B is simpler but the resulting id sequence generally does not round-trip (`encode(decode(ids)) != ids`), so `prompt_text` would be unfaithful and the adapter's re-encode would break the count. The one deliberate exception is the random-token sentinel (Part 7), which is ids-native by design.

Determinism note: the greedy fill is a deterministic function of (generated text, ladder, tokenizer), so exact-shape trimming does not add nondeterminism. Cost: O(atoms × full re-encodes) ≈ tens of encodes of a ≤512-token string per item — negligible, and it happens at generation time, not measurement time.

### 0.5 Harness integration (additive, per C-014)

- Generators write items into the campaign matrix as `workload_profile.prompt_text` (existing path) plus additive fields: `workload_profile.category`, `source_manifest` (generator_id/version/seed/tokenizer hashes/drbg), `output_policy` (`fixed_budget_exact`: greedy, EOS suppressed, max_tokens=256), `expected_prompt_token_ids_sha256`.
- The runner asserts the adapter-realized `prompt.token_ids_sha256` (already emitted by `prompt_provenance` in `mlx_runtime.py`) equals the expected hash — this closes the loop between generation-time and run-time tokenization and detects tokenizer drift for free.
- `random-token` sentinel needs an ids-native delivery path: either a small additive `prompt_token_ids` field or reuse of the raw-ids mechanism `_prompt_for_workload` already has internally; keep it additive and mutually exclusive per the existing `WorkloadProfile.validate` pattern.

---

## Part 1 — chat/instruction (`jw.chat`)

**1) Algorithm sketch.** From the DRBG: (a) pick persona/audience from a bank (~40 entries: "a first-year nursing student", "a city council member", …); (b) pick invented topic by composing a noun-phrase grammar over closed banks of our own words (adjective + domain-noun + qualifier: "the seasonal maintenance schedule of tidal ferry routes") — invented composites, so no dataset licensing surface; (c) pick 3–5 constraint clauses from a bank (word-count target, "avoid jargon", "give two examples", "use a numbered list"); (d) generate a background-context paragraph with the shared synthetic-prose engine (subject–verb–object sentence templates over the banks, pronoun chains for surface cohesion); (e) assemble: preamble ("You are a helpful assistant…" style, fixed text) → background paragraph (body units + elastic slot) → final instruction sentence (epilogue, fixed structure with the sampled topic/persona/constraints slotted in).

**2) Exact shape.** Epilogue = instruction sentence (fixed, must survive). Elastic slot = end of the background paragraph; atom ladder = prose phrases ("in most cases", "over time") → common words → " a"/" b"-style single letters. Standard §0.4.

**3) Signature preserved / not.** Preserved: natural-English subword distribution (high-frequency tokens, low punctuation density), instruction-following prompt structure, a decode regime where greedy continuation is fluent prose. Not preserved: real chat topic entropy, multi-turn structure, semantic depth — the model "understands" less, and if attention/FFN energy depends on representational content rather than token statistics, this control under-represents real chat. That is exactly the Token-Shape Sufficiency Null being tested, and this category is the predicted-NULL ecological baseline (RQ bank: "expected NULL at fixed shape").

**4) Parameters (512/256 pinned defaults).** `persona_bank_rev=1`, `topic_grammar_rev=1`, `n_constraints=4`, `preamble_tokens≈35 (fixed text)`, `instruction_reserve≈60`, `background = remainder`, `coarse_headroom Δ=24`, `output_policy=fixed_budget_exact(256, greedy, EOS-suppressed)`.

**5) Item sketches.**
- *Item A (seed x1):* preamble; 320-token background on "the winter staffing rotation of harbor pilot crews"; instruction: "Explain the rotation described above to a new town clerk, in about 200 words, using a numbered list and avoiding jargon."
- *Item B (seed x2):* background on "community greenhouse irrigation scheduling"; instruction targets "a visiting exchange student", constraints: two examples + informal tone.
- *Item C (seed x3):* advice-style: background is a synthetic situation description ("a small library reorganizing its lending desk…"); instruction: "Suggest a plan with three steps and one risk to watch."

---

## Part 2 — code generation (`jw.code`)

**1) Algorithm sketch.** Generate a synthetic Python module via a small grammar, then ask for a completion. From the DRBG: (a) identifiers = snake_case compounds of seed-drawn syllables + a domain-noun bank (`batch_ledger_totals`, `parse_route_manifest`) — invented, license-clean, and importantly they fragment into multiple subwords like real code identifiers do; (b) module skeleton: 2–3 import lines (stdlib names only), a module docstring, 2 complete small functions (loops, dict access, f-strings, early returns — emitted from statement templates with type-consistent slots so the code is syntactically valid Python), 1 function signature + docstring + `# TODO: implement` stub; (c) prologue instruction: "Complete the final function in this module. Return only code."; (d) epilogue = the stub signature + docstring (must survive so the completion target is intact).

**2) Exact shape.** Elastic slot = a trailing comment block ABOVE the stub (`# note: handles the empty-manifest case`, …); atom ladder = comment phrases → comment words → single comment chars. Comments are the natural code-world filler channel: they extend length without changing program semantics, and they keep the token distribution code-like (# tokens, newline-indent tokens). Standard §0.4; indentation is emitted as literal spaces so the tokenizer's whitespace-merge behavior is exercised and captured by full re-encode.

**3) Signature preserved / not.** Preserved: code-token distribution (punctuation-heavy, indentation/newline tokens, identifier fragmentation), code-structured prefill, and a greedy decode that continues in code (under EOS suppression the model emits code-ish tokens to budget — qualitatively the right decode distribution). Not preserved: real API surface (no numpy/pandas idioms a code model may have specialized paths for is too strong a claim — but token-level statistics won't reflect heavily-memorized library completions), solvability/correctness pressure, and repository-scale context. If code-model energy differences come from *which* continuations the model locks into (e.g., degenerate repetition on synthetic stubs vs diverse tokens on real code), the synthetic control can drift from the realistic exemplar — this is precisely why C-005 pairs synthetic controls with HumanEval/MBPP-style realistic exemplars; the synthetic generator does not replace that leg.

**4) Parameters (512/256).** `n_complete_functions=2`, `n_imports=3`, `stub_reserve≈55`, `instruction_tokens≈25`, `indent="    "` (4 spaces, pinned), `statement_bank_rev=1`, Δ=24, output policy as §1.

**5) Item sketches.**
- *Item A:* module `route_manifest.py`: imports `json,collections`; `load_manifest(path)`, `count_active_routes(records)` complete; stub `merge_daily_totals(records, key)` with docstring specifying dict-of-lists output.
- *Item B:* text-processing module: complete `normalize_header(line)`, `split_fields(line, sep)`; stub `validate_row(fields, spec)` returning `list[str]` of errors.
- *Item C:* numeric module: complete `rolling_mean(xs, k)`; stub `detect_step_change(xs, threshold)`; comment block carries the elastic fill.

---

## Part 3 — summarization / long-context (`jw.summ`)

**1) Algorithm sketch.** (a) Invent an entity system: 3–5 named entities (DRBG-composed proper nouns: "the Varnel Basin survey", "Inspector Halden") + 6–10 attribute facts each (dates, quantities, relations) drawn from numeric/temporal banks; (b) generate a pseudo-factual passage: paragraphs of templated sentences realizing the facts, with pronoun/reference chains so the passage has genuine long-range referents (entity introduced in paragraph 1 is referenced in paragraph N — this matters: it puts real information at long attention distances, not just tokens); (c) optionally plant `n_needles` unique fact sentences at DRBG-chosen depths (recorded in the manifest — reusable later for retrieval probes, though jw_mixed_v1 makes no correctness claims); (d) prologue: "Read the following report."; epilogue: "Summarize the report above in about 120 words, covering each named party." Passage is the body; instruction is fixed.

**2) Exact shape.** Elastic slot = final passage paragraph; atom ladder = prose (as `jw.chat`). The instruction epilogue (~35 tokens) is reserved first, so the passage always fills `B − prologue − epilogue` exactly. Standard §0.4.

**3) Signature preserved / not.** Preserved: the category's defining computational signature — prefill-heavy phase mix, contiguous long natural-prose prefill, KV-cache growth, decode attending over the full context. These are shape-and-distribution properties and survive synthesis fully; this is the category the RQ bank marks "YES, distinguishable via prefill energy/TTFT/phase mix". Not preserved: true compression difficulty and discourse structure (synthetic facts are locally template-shaped; entropy-per-sentence is lower than real documents). Honest caveat: at the 512/256 common stratum the passage is only ~430 tokens, so "long-context" is nominal — the category's distinguishing physics really appears at the panel shape (4096/256). The generator takes `passage_tokens` as a parameter so the same code serves both strata; the common-stratum result should be read as "summarization-shaped content at 512", not "long-context".

**4) Parameters (512/256).** `n_entities=4`, `facts_per_entity=7`, `n_needles=2`, `instruction_reserve≈35`, `prologue≈8`, `sentence_bank_rev=1`, Δ=24. Panel stratum later: identical except B=4096.

**5) Item sketches.**
- *Item A:* infrastructure-inspection report: three bridges, an inspector, dated findings with load figures; needle = a unique permit number; summary instruction names the parties.
- *Item B:* invented regional-survey minutes: four departments, budget quantities, two decisions; needle = a specific vote count.
- *Item C:* incident timeline: one facility, five timestamped events; instruction asks for a chronological summary.

---

## Part 4 — reasoning / CoT (`jw.reason`)

**1) Algorithm sketch.** Construct a multi-step word problem BACKWARD from a computation DAG so the item has a known ground-truth answer (quarantined annotation only, per C-004 — recorded in the manifest, never scored in jw_mixed). (a) Draw a chain of `n_steps` = 4–6 operations (add/sub/mul/int-div/percent) over small integers, propagating a running value with constraints (keep intermediates positive, bounded, integer); (b) wrap each step in a narrative template with DRBG-drawn entity names and units ("Marta's stall sells 14 crates each morning. Afternoon sales are 3 times the morning count…"); (c) interleave `n_distractors` numerically-inert sentences (quantities mentioned but flagged irrelevant by construction — logged in the manifest so distractor load is a controlled parameter, since distractors change reasoning difficulty and must not float freely); (d) epilogue: "Work through this step by step, then state the final number." (e) A logic variant (seed-parity selected, 25% of items) emits ordering/deduction puzzles from a transitive-constraint generator with a verified unique solution.

**2) Exact shape.** Elastic slot = narrative scene-setting sentences containing NO numerals (so filler cannot perturb the arithmetic structure); atom ladder = prose. The CoT instruction epilogue is fixed. Standard §0.4.

**3) Signature preserved / not.** Preserved: numeral-dense token distribution, multi-step dependency structure in the prompt, and a decode regime that greedily emits chained arithmetic/derivation tokens (digit-heavy, structured). Not preserved — and this is the most honest caveat in the suite: whether the model performs more "computation" per token on reasoning content is exactly what the Token-Shape Sufficiency Null contests; under `fixed_budget_exact` the transformer executes the same FLOPs per token regardless, so any energy difference must come via token-content-dependent hardware effects (arithmetic-unit utilization patterns, cache behavior over different token distributions) — plausibly null. The category's headline effect (thinking-token inflation, C5-W.2) lives in the `natural_eos` pilot, not this stratum, because it is an output-LENGTH effect. The generator serves both modes unchanged.

**4) Parameters (512/256).** `n_steps=5`, `n_distractors=2`, `value_range=[2,60]`, `intermediate_cap=10000`, `logic_variant_rate=0.25`, `instruction_reserve≈20`, Δ=24. Ground-truth answer + step trace recorded in manifest (annotation only).

**5) Item sketches.**
- *Item A:* market-stall chain: 14 crates → ×3 afternoon → −9 spoiled → ÷ per-5 bundling → +7 reserve; distractors mention stall rent and a neighbor's unrelated count; answer 15 (verified at generation).
- *Item B:* workshop scheduling arithmetic: hours across 4 machines with a 20% maintenance deduction, integer-safe by construction.
- *Item C (logic variant):* five invented delivery drivers with 6 transitive earlier/later constraints; unique-order solution verified by exhaustive check (5! = trivial); question asks who is third.

---

## Part 5 — JSON extraction (`jw.json`)

**1) Algorithm sketch.** (a) Draw a target schema: 6–9 fields from a typed bank (string/int/date/enum/bool/nullable), field names from the identifier composer; (b) draw ground-truth values per type; (c) render a NOISY source record: a semi-structured mess mixing formats — log-style lines (`[2031-04-12 08:31] intake ref=KV-2214`), free-text sentences embedding some values, a partial key:value block, plus `n_distractors` near-miss values (a second date, a similar-looking ID) and `n_red_herrings` irrelevant fields — all DRBG-ordered so value positions vary per seed; (d) prologue: "Extract the following fields from the record below. Output only JSON matching the schema."; then the schema rendered as a JSON skeleton with type annotations (this block is itself punctuation-dense — part of the signature); record body; epilogue: 'Output only the JSON object.' Ground truth JSON recorded in the manifest (annotation only).

**2) Exact shape.** Elastic slot = a designated `notes:` free-text distractor field at the record's tail (explicitly irrelevant to the schema); atom ladder = prose then chars. Schema block and instruction are fixed per item. Standard §0.4.

**3) Signature preserved / not.** Preserved: structural-punctuation-heavy token distribution ({ } " : , tokens in both schema and expected output), constrained short-output decode where greedy emission is schema-shaped, and in `natural_eos` mode the category's defining behavior — early valid-close (model closes the JSON object well before 256 and stops), probing the EOS-bias mechanism the RQ bank names. Not preserved: real-world noise distributions (OCR junk, truly adversarial formats); extraction difficulty is grammar-bounded. Under `fixed_budget_exact` with EOS suppressed the model must continue PAST the closed JSON object — what it emits after close (repetition, whitespace, commentary) is model-dependent and is itself a content signature worth having; the RQ bank correctly predicts collapse at fixed envelope.

**4) Parameters (512/256).** `n_fields=7`, `n_distractors=3`, `n_red_herrings=2`, `record_styles=["log","freetext","kv"]` all present, `schema_reserve≈90`, `instruction_reserve≈30`, Δ=24.

**5) Item sketches.**
- *Item A:* shipment intake record: extract `{ref_id, received_date, weight_kg, carrier, hazardous(bool), dock(enum A-D), inspector}` from interleaved log lines + a sentence burying the weight; a second, wrong date sits in a distractor line.
- *Item B:* clinic-style appointment note (invented names): 8 fields incl. a nullable `followup_date` whose value is genuinely absent — tests null emission.
- *Item C:* device-telemetry blob: kv block with unit suffixes to strip (`"temp: 41.2C"` → int/float field), enum status, `notes:` field carrying the elastic fill.

---

## Part 6 — multilingual (`jw.multiling`)

**Approach decision: synthetic interlingua — chosen over pinned corpus for this stratum.** Rationale: (i) the identification core needs token-matched exact shapes, and exact-token trimming of real FLORES sentences destroys the semantic-matched property that is FLORES's entire value — you'd pay CC BY-SA share-alike propagation and tokenizer-fertility-vs-content confounds for sentences you then mangle; (ii) the computational signature that matters at token-matched shape — script/byte statistics hitting tokenizer fertility and byte-fallback paths — is a property of character distributions, which synthesis preserves fully; (iii) license-clean and reproducible from seed alone. FLORES-200 remains the pinned-corpus instrument for the LATER semantic-matched leg (C5-W.4), exactly as the RQ bank already plans; this generator is the token-matched control half of that pair.

**1) Algorithm sketch.** Per language profile (pinned set of 6): (a) a syllable/character inventory over the script's Unicode range with realistic frequency weights (e.g., Devanagari consonant+matra combinations; CJK from a fixed embedded list of ~300 common-range codepoints chosen by Unicode block, not from any frequency corpus — the list is a module constant, license-clean); (b) a pinned closed-class function-word list per language (20–30 items: articles, conjunctions, particles — individual words are facts, not copyrightable); (c) a phrase grammar: function-word + 1–3 content "words" built from DRBG-drawn syllables, sentence lengths drawn from a pinned distribution, script-appropriate punctuation (。 for CJK, ؟/، for Arabic, danda for Devanagari) and directionality noted in the manifest for Arabic; (d) each ITEM is single-language (script purity per item — the fertility signal must not be blended); the category's 6+ items cover 6 scripts; (e) prologue/epilogue: a short fixed ENGLISH instruction frame ("Continue the following text in the same language:") of ~12 tokens, identical across languages so the cross-language contrast is carried by the body — frame token count recorded.

**2) Exact shape.** Elastic slot = final sentence of the body; atom ladder is SCRIPT-NATIVE: phrases → syllables → single codepoints of that script. Byte-fallback tokenizers give per-codepoint costs of 1–4 tokens (a 3-byte CJK char can be 3 byte-tokens), which actually provides a fine ladder; the last-resort ±1 rung is an ASCII space+digit, permitted only as a final tail and recorded as `ascii_tail_tokens` in the manifest so script purity is measured, not assumed. Standard §0.4 otherwise. Note the deep consequence of token-matching: 512 tokens of Devanagari under a fertility-3 tokenizer is ~3× less TEXT than 512 tokens of English — that is the design, and `chars_per_token` (realized fertility) is recorded per item as the category's key covariate.

**3) Signature preserved / not.** Preserved: script diversity → tokenizer fertility differences, byte-fallback code paths, non-Latin token-id distribution (high-id / byte-token regions of the vocab, different embedding rows), script-consistent greedy continuation. Not preserved: actual morphology/syntax/semantics — the model sees phonotactically plausible pseudo-words, and a model with strong competence in language X may process real X differently from pseudo-X (e.g., higher next-token entropy on pseudo-words could change decode content). The synthetic/realistic pairing at the FLORES leg is the check on exactly this gap.

**4) Parameters (512/256).** `languages=["en-Latin","ru-Cyrillic","zh-CJK","hi-Devanagari","ar-Arabic","el-Greek"]` (one item per script minimum), `syllable_bank_rev=1`, `function_word_list_rev=1`, `sentence_len_dist=pinned(4..14 words)`, `instruction_frame_tokens≈12 (fixed)`, Δ=24, `ascii_tail_max=3`.

**5) Item sketches.**
- *Item A (zh-CJK):* ~500 tokens of pseudo-Chinese prose from the pinned 300-codepoint inventory with 、/。 punctuation; realized fertility recorded (~1–2 tokens/char depending on tokenizer coverage).
- *Item B (hi-Devanagari):* pseudo-Hindi with real function words (और, में, है…) linking DRBG syllable words; high fertility expected on Latin-centric tokenizers — the energy-tax probe.
- *Item C (ar-Arabic):* RTL pseudo-Arabic with real particles (و، في، من) and Arabic punctuation; manifest flags RTL for downstream display only.

---

## Part 7 — Content-sensitivity sentinel set (P2-020 / AP-6)

Five single-item, equal-shape (512/256 `fixed_budget_exact`, greedy, EOS-suppressed — identical output policy across all five, per AP-6's shape/stop-policy-match disqualifier), n=5 bundles each. These are deliberately the DEGENERATE endpoints of the generator space:

1. **`jw.sentinel.repeated_seed` (control).** Exactly the existing `_synthetic_prompt_tokens` recipe: the pinned sentence's token ids tiled to 512 (ids-native; trivially exact-shape). This is the incumbent synthetic stream — the thing whose generalization is being tested. Known hazard to record: maximal repetition is the best case for any prompt-cache/attention-locality effect; the run manifest must record prompt-cache state (the `spike_mlx_prompt_cache.py` findings apply) and caches must be cold/reset identically across all five conditions or the control is confounded.
2. **`jw.sentinel.random_token`.** 512 DRBG-uniform draws from the pinned tokenizer's vocab, excluding special ids and ids that decode to the empty string (exclusion list derived deterministically from the tokenizer files, hence pinned by `tokenizer_id`). Ids-native — this sequence generally does NOT round-trip through text, which is fine and intentional: it is the maximum-entropy, structure-free endpoint; delivered via the ids path (§0.5), `text_sha256=None`, exact shape by construction. Greedy decode over incoherent context is itself a distinct regime (often degenerate repetition) — emitted-token audit will show it.
3. **`jw.sentinel.natural_prose`.** The `jw.chat` prose engine run body-only (no instruction machinery): 512 tokens of coherent synthetic English via §0.4. One fixed seed, pinned in the profile.
4. **`jw.sentinel.code_like`.** The `jw.code` module grammar body-only (no completion instruction): a syntactically valid synthetic Python module at exactly 512 tokens, comment-block elastic slot.
5. **`jw.sentinel.multilingual`.** The `jw.multiling` engine in mixed-script mode — the one place mixing is right: four 120-token single-script blocks (Cyrillic, CJK, Devanagari, Arabic) concatenated in pinned order, exact-shaped in the final block. Maximizes vocab-region diversity within one prompt.

Each sentinel emits the same provenance record as the categories (item_id tuple, token_ids_sha256, realized count asserted == 512). Analysis per AP-6: one-way contrast vs condition 1, gross + idle-subtracted request energy, MDE verdicts; claim ceiling L2 sentinel-validity only — no broad content-neutrality claim beyond these five conditions. The mechanism story: conditions 1→2 bracket the entropy axis; 3/4/5 sit at realistic structure points; if all deltas are below floor, the repeated-seed stream is defensible as the workhorse control; if 2 or 5 separates, content sensitivity exists and jw_mixed_v1 category runs must not assume shape sufficiency.

---

## Part 8 — Cross-cutting risks and honest limits

- **Token-Shape Sufficiency Null is live.** Under `fixed_budget_exact`, per-token FLOPs are content-independent; the only channels for category energy differences are (a) prefill/decode phase mix (shape-adjacent — the summarization signature), (b) token-content-dependent hardware utilization (embedding-row locality, byte-fallback paths, numeric-token patterns) and (c) content-dependent DECODE OUTPUT distributions under greedy (the model's chosen continuations differ by category even at fixed budget — repetitive vs diverse emission has real cache/bandwidth consequences). The generators preserve (a) exactly, (b) faithfully at the token-statistics level, and (c) only qualitatively — this is the honest gap, and the synthetic/realistic pairing plus the sentinel set are its instruments, not a workaround.
- **Greedy-output divergence is a feature to record, not suppress:** per-item emitted-token hashes and stop reasons (already in the C-014 harness-needs list) make the decode-content channel auditable.
- **Determinism surface:** SHA-256 DRBG + embedded banks + full-re-encode trimming means (seed, generator_version, tokenizer_id) → identical `prompt_text` bytes on any Python ≥3.10, no external deps; the only external dependency is the tokenizer itself, pinned by file hash and closed-loop-verified at run time against `expected_prompt_token_ids_sha256`.
- **Fail-closed everywhere:** unreachable exact budget, bank-hash mismatch, or run-time hash mismatch are hard errors, matching the repo's FAIL-CLOSED runner posture (C-011/D-014).
- **512/256 common stratum understates summarization and reasoning:** their defining effects (KV growth; thinking inflation) live at 4096/256 and `natural_eos` respectively — the identification core should be read as the category-at-matched-shape residual test (AP-4), nothing more.

Key repo anchors: /Users/edr/code/JouleWise/joulewise/adapters/mlx_runtime.py (`_prompt_for_workload`, `_synthetic_prompt_tokens`, `_tokenizer_identity`), /Users/edr/code/JouleWise/joulewise/provenance.py, /Users/edr/code/JouleWise/joulewise/schemas.py (`WorkloadProfile`), /Users/edr/code/JouleWise/docs/contracts/analysis_plans.md (AP-4, AP-6), /Users/edr/code/JouleWise/docs/research_question_bank.md (Token-Shape Sufficiency Null, C-014 jw_mixed_v1 phasing), /Users/edr/code/JouleWise/TASK_QUEUE.md (P2-012, P2-020).

---

# C. affine_mod_ladder_v1 implementation-ready design

**Cross-check verdict: sound-with-amendments. Amendments to adjudicate before implementation:**

1. Pin the decoding/sampling policy explicitly. The harness (joulewise/adapters/mlx_runtime.py:174-179) calls mlx_lm.stream_generate with no sampler argument, i.e. greedy/temp-0 deterministic decoding. Under determinism the same item yields the identical response in every bundle, so cross-bundle pooling ('40-80 items/level for the gate statistics') is pseudo-replication: the effective n for all token/stop-reason/correctness statistics is the 8 distinct items per level; bundles replicate energy only. Rewrite section 3 accordingly (this is the scored-side mirror of the repo's own bundle-level-uncertainty rule).
2. Fix the E1 sensitivity claim: 1 - 0.9^40 = 0.985 is the probability of observing at least one non-EOS item, not of tripping the 5% gate (P(r >= 3/40 | true rate 10%) is about 0.78 even granting independence, which determinism removes). Also state that at 8 items/level, r is quantized to eighths so the 5% threshold means zero tolerated non-EOS items per level - acceptable, but say so instead of quoting a fake power number. The SE = 0.16 tokens at n=40 claim falls for the same reason.
3. E5's evaluability condition ('both classes >= 5 parsed items per level') can never be met with 8 deterministic items/level (needs >= 10). Either raise smoke items/level to 16 or predeclare E5 as expected-not_evaluable at smoke sizing.
4. Correct section 1.1: only the PARAMETER distribution is level-identical by construction; the answer(-length) distribution is not guaranteed (a^n mod m collapses when gcd(a,m) > 1; short orbits at high n - the report's own honest limit 8 contradicts the 'by construction' claim). State that the empirical E2/E3 gates are the actual safeguard.
5. Fix k accounting: C-015 defines k as distinct items and reserves within-bundle repeats for sentinels, so the smoke suite is k = 24 exactly (matches the first default - no '2-over' deviation exists) and the full ladder is k = 112 distinct items plus 2 sentinel executions (the k <= 48 conflict stands and still needs ratification).
6. Name the raw-response-text bundle requirement as a P2-010a scope addition requiring lead/council ratification: C-015 explicitly caps P2-010a to the minimal substrate whose sketch carries only per_item_response_hash, not response text. The addition is well-motivated (reducer rescoring) but must go through the same ratification channel as the section 0 level-set pin, not ride in as a parenthetical.
7. Fix citation and power provenance in section 2/3: the 0.028-0.034 J prefill figure is from the slice-2I report (2026-07-06), not 'the flagship run'; the 15 W lower bound of the 15-24 W busy-power band is unsourced, and ladder level windows are prefill/overhead-dominated rather than decode-dominated, so re-anchor the '~4% of a ~20 J window' threshold-defensibility argument on measured level-window energy from the first smoke bundle (add this to the calibration duties already assigned to that bundle).
8. Make the malformed-as-incorrect accuracy denominator an explicit AP-5 row amendment before the scored campaign: C-015 bars malformed/capped/runtime_failed items from numeric claim denominators unless the AP row predeclares that status as part of the endpoint. 'Predeclare at campaign AP time' is the right instinct but should be named as a required AP-5 edit, not left implicit.
9. State in section 4 that under deterministic decoding per-level correct counts are identical across bundles, so bundle-to-bundle variance in energy_per_correct is energy-only; any accuracy uncertainty statement must be over distinct items (or omitted), and the >= 3-correct binomial guard is a deterministic property of the item set, not a per-bundle stochastic event.

## Report

# affine_mod_ladder_v1 — implementation-ready design

Sources read: `docs/research_question_bank.md` (C-004 lines 58–108, C-015 lines 110–275), `docs/contracts/analysis_plans.md` AP-5 (lines 122–141) and the `<3 samples → not resolvable` rule (line 41), `docs/run_reports/2026-07-06-slice-2i-first-real-energy.md` (8.82–8.91 Hz observed, 257 tok/s, TTFT ~95 ms, ~23 W decode), `docs/council_log.md` C-004 entry, `docs/decision_log.md` D-036, `joulewise/provenance.py`, `configs/examples/mac_mlx_local.json`, `TASK_QUEUE.md` P2-010/P2-015.

---

## 0. One pinned interpretation decision (flag for lead ratification)

The bank's C-004 phrase "levels 1..64 powers-of-two, 16 items/level" is ambiguous with "the full 64-level scored campaign is deferred." I pin the reading: **difficulty values are the powers of two {1, 2, 4, 8, 16, 32, 64} — 7 levels spanning 1..64** — and treat "64-level campaign" as loose phrasing for "the ladder up to 64 iterations." Rationale: (a) 64 linear levels × 16 items = 1024 items per suite bundle is indefensible against C-015's k=24/48 defaults; (b) geometric spacing is the natural spacing for an effort axis; (c) item identity below keys on the difficulty *value* (n_iter), so adding intermediate levels later changes nothing retroactively. The bank line should be edited to match whichever reading the lead ratifies; this is a docs fix, not a code fork.

---

## 1. Exact item format

### 1.1 Derivation (pinned, stdlib-only, seed-deterministic)

Item identity keys on the difficulty VALUE (`n_iter`), not a level ordinal, so smoke items are a strict subset of full-ladder items under the same seed.

```python
DOMAIN = "joulewise.workload.affine_mod_ladder.v1"

def derive_item(suite_seed: str, n_iter: int, item_index: int):
    msg = f"{DOMAIN}\x00{suite_seed}\x00{n_iter}\x00{item_index}".encode("utf-8")
    h = hashlib.sha256(msg).digest()          # 32 bytes, four 8-byte lanes
    m  = 100 + int.from_bytes(h[0:8],  "big") % 900   # 3-digit modulus, 100..999
    a  = 10  + int.from_bytes(h[8:16], "big") % 90    # 2-digit multiplier, 10..99
    b  = 10  + int.from_bytes(h[16:24],"big") % 90    # 2-digit increment, 10..99
    x0 = 100 + int.from_bytes(h[24:32],"big") % 900   # 3-digit start, 100..999
    x = x0
    for _ in range(n_iter):                            # n_iter <= 64: trivial
        x = (a * x + b) % m
    return AffineItem(a=a, b=b, m=m, x0=x0, n_iter=n_iter, expected=x)
```

Pins: integers rendered base-10 ASCII unpadded in the hash message; NUL separators; UTF-8 seed bytes. **No rejection sampling of any kind** — any level-dependent rejection would break the core design invariant that the parameter distribution is *identical across levels* (only n_iter varies), which is what makes the envelope claim work. Modulo bias from `2^64 % 900` is ~5e-17 and level-identical; note it, ignore it. Fixed digit lengths (3/2/2/3) hold the prompt shape fixed. Expected answers are uniform-ish on [0, m−1] with an answer-length distribution identical across levels by construction.

`generator.parameters_hash` = SHA-256 of the canonical JSON `{"domain": DOMAIN, "m_range": [100,999], "a_range": [10,99], "b_range": [10,99], "x0_range": [100,999], "levels": [...], "items_per_level": N}` — any retune is a new revision, never silent.

### 1.2 Prompt template (fixed shape across levels — exact text)

```
Compute a modular recurrence.
Start with x = {x0}.
At each step, replace x with ({a} * x + {b}) mod {m}.
Perform exactly {n} steps.
Answer with only the final value of x as a decimal integer. Output nothing except that integer.
```

Rendered as a single user message through the model's chat template, no system message. Realized prompt token ids hashed via the existing `prompt_provenance()` (`joulewise/provenance.py`). Only `{n}` varies in digit count across levels (1–2 digits); operands are digit-fixed. This is a **disclosed** ≤~2-token prompt-shape deviation across levels, gated in §3 (E4), and energetically negligible (prefill measured at 0.03 J vs ~47 J decode in the flagship run). Answer-only is load-bearing: any CoT allowance would make emitted tokens scale with difficulty and destroy the C-004 envelope. Considered and rejected: `fixed_budget_exact` padding (constant tokens by force) — forced generation past EOS produces garbage, extraction becomes unreliable, and "energy per correct answer" stops meaning natural answering.

### 1.3 Output policy and answer extraction (pinned)

- Output policy: `natural_eos_capped`, `requested_tokens = 16`, recorded via the existing `output_policy()` provenance fields; per-item `stop_reason ∈ {eos, length}`.
- Extraction rule (exact-integer): `s = response_text.strip()` (ASCII whitespace); `re.fullmatch(r"[+-]?\d+", s)`; no match → `parse_status = malformed`, `correct = False`; match → `correct = (int(s) == expected)`. `int()` semantics mean `042` and `+42` score as 42 — pinned, accepted. Anything else (`**42**`, `42.`, prose) is malformed *by design*: instruction-following failure is envelope evidence, not something the scorer papers over. A lenient diagnostic parse (first `\d+` run) MAY be recorded as `lenient_correct` annotation but never enters AP-5.
- A model that ignores answer-only and starts reasoning hits the 16-token cap → `stop_reason = length` → item status `capped` → E1 fails the envelope gate. That is the gate working, not a bug.
- **Bundle requirement (new, lands with P2-010a):** per-item raw response TEXT stored in the bundle (e.g., `raw/items/<item_id>/response.txt`; ≤16 tokens each) in addition to C-015's `per_item_response_hash` — required for reducer rescoring (§4).

IDs: `item_id = affine_v1_L{n_iter:02d}_i{item_index:02d}`, `level_id = L{n_iter:02d}`, `block_id = level_id` (levels are the natural blocks; level markers already exist in the C-015 substrate).

---

## 2. Level-duration arithmetic (8.9 Hz sampler, ≥3-sample rule)

Constants from the slice-2I report: observed sampler 8.82–8.91 Hz (use worst case 8.82 Hz → interval T = 113.4 ms); Qwen2.5-1.5B-4bit on M3 Max decodes at ~257 tok/s; TTFT ~95 ms at a ~17-token prompt. Guaranteed sample count in a window of width W is `floor(W/T)` (alignment-independent lower bound), so the AP `<3 samples → not resolvable` rule needs **W ≥ 3T = 340 ms bare**, and a ~3× margin target means **W ≥ ~1.0 s**.

Per-item time (fast-model binding case): prefill of the ~70–85-token realized prompt ≈ 100–150 ms TTFT; decode 2–5 tokens typical ≈ 8–20 ms (worst capped 16 tokens ≈ 62 ms); inter-item harness overhead ~5–20 ms. **Planning value 0.15 s/item, pessimistic 0.11 s, generous 0.20 s.**

Consequence 1 (honest, by design): a single item window is 0.11–0.21 s → **1–2 guaranteed samples → per-item joules are unidentifiable on fast models.** Items get status `below_floor` and contribute only to level/block windows, exactly per the C-015 aggregation rule. AP-5 already names level windows as the primary window class.

Consequence 2 — items/level for level-window identifiability:

| items/level | W @0.11 s/item → samples | W @0.15 s → samples | W @0.20 s → samples | verdict |
|---|---|---|---|---|
| 3 | 0.33 s → **2 ✗** | 0.45 s → 3 (bare) | 0.60 s → 5 | fails pessimistic case |
| 8 | 0.88 s → 7 | 1.20 s → 10 | 1.60 s → 14 | ≥2.3× margin — minimum recommended |
| 16 | 1.76 s → 15 | 2.40 s → 21 | 3.20 s → 28 | 5–7× margin — full-ladder default |

Level-window gross energy at ~15–24 W busy power ≈ 13–29 J (8 items) / 26–58 J (16 items) — same order as the clean 47 J flagship windows, comfortably above any plausible floor, but the AP-5 floor gate stays `pending-P2-015`; note P2-015's scope explicitly includes item/level-window floors, so **the smoke bundles double as level-window floor-calibration evidence**.

### Recommended sizing

**Smoke ladder (P2-010b, envelope validation):** levels **{1, 8, 64}** (endpoints + geometric midpoint — an early-EOS/CoT-leak bias would be monotone in difficulty, so 3 spanning levels detect it), **8 items/level** (item_index 0..7), plus 2 sentinel repeats of item (n=1, i=0) at suite start and end (within-bundle repeats reserved for sentinels per C-015; tagged, excluded from level stats, never inflate n). k = 26 item executions (vs the k=24 first default — 2-over is the sentinel cost; named, acceptable). Measured suite ≈ 26 × 0.15 ≈ 3.9 s; bundle wall ≈ load + 30 s idle + suite + cooldown ≈ 1.5–3 min. **B = 5 whole-suite bundles (top-up to B = 10 near the floor)** → 40–80 items/level for the gate statistics; session cost ~10–25 min. Level order rotated round-robin across bundles, `order_seed` recorded.

**Full ladder (deferred per C-014 until C5-1.9 has a consumer):** 7 levels {1,2,4,8,16,32,64} × **16 items/level** + 2 sentinels = 114 executions/bundle ≈ 17 s measured; per-level windows 2.4 s ≈ 21 samples; **B = 10 bundles**, level order Latin-square/rotated; campaign wall ~20–30 min. Named conflict: k = 114 exceeds C-015's k ≤ 48 default even though wall time (~17 s) is nowhere near the 10–15 min block-split trigger — the k default was sized for realistic-length items, not 0.15 s items. Treating each level as a block (block = level, 16 items) is the natural structure; **the k-policy deviation needs council/lead ratification at campaign time** (cheap, since the campaign is deferred anyway).

Slower models only make this easier: lower tok/s and higher TTFT stretch item time, so the 257 tok/s fast model is the binding case. First smoke bundle calibrates the 0.15 s planning number; if items actually run <0.11 s, raise items/level per the table.

---

## 3. Envelope-validation gate (AP-5 smoke gate, computed per D-036)

Inputs: per-item realized `{prompt_tokens, emitted_tokens, stop_reason, parse_status}` pooled across all strict-valid smoke bundles. The gate is emitted by the analysis script as a machine-readable verdict — `envelope_validated` iff E1–E4 all pass, else `envelope_failed([reason_codes])` — derived from recorded measurements, never asserted in prose (D-036). Thresholds are pinned here; changing them requires a decision-log entry.

- **E1 stop-reason invariance:** per level ℓ, r_ℓ = fraction with `stop_reason != "eos"`. PASS iff `max_ℓ r_ℓ ≤ 0.05` AND `max_ℓ r_ℓ − min_ℓ r_ℓ ≤ 0.05`.
- **E2 emitted-token mean invariance:** PASS iff `max_ℓ mean(emitted) − min_ℓ mean(emitted) ≤ 1.0 token`.
- **E3 emitted-token distribution homogeneity:** chi-square statistic on the level × emitted-token-count contingency (counts binned {1,2,3,4,5+}), p-value by **permutation test** (10,000 label permutations, `random.Random` seeded by SHA-256 of `suite_seed || "envelope_gate"` — stdlib-only, avoids needing a chi-square CDF). PASS iff p ≥ 0.01.
- **E4 prompt-token invariance:** PASS iff global `max − min` realized prompt tokens ≤ 4 AND level means within 2 tokens (tolerance covers the {n}-digit deviation plus BPE digit-merge jitter; tokenizer-specific, recheck per model).
- **E5 early-EOS-bias check (C-004's named caveat; advisory, does not gate):** per level where both classes have ≥5 parsed items, `|mean emitted(incorrect) − mean emitted(correct)| ≤ 1.0 token`, else `not_evaluable` recorded. Uses quarantined correctness as a *validity* input only — within the C-004 quarantine.

Why 1.0 token / 5% are defensible and not vibes-calibrated to zero: one emitted token ≈ 3.9 ms × ~23 W ≈ 0.09 J/item ≈ 0.7 J per 8-item level window ≈ ~4% of a ~20 J window — at/below the expected comparative floor, so a passing gate bounds residual token-count confounding below measurement resolution. Sensitivity at smoke n (40–80 items/level): a 10% non-EOS rate at any level is detected with P ≥ 0.985 (1 − 0.9^40); a 1.0-token mean shift has SE ≈ 0.16 tokens at n=40. Honest limit: the smoke gate catches gross violations (systematic early-EOS, CoT leakage, cap-hitting); subtler shifts are re-gated at full-campaign n before any scored claim.

---

## 4. Scorer design (stdlib, re-derivable from manifest alone)

New module `joulewise/workloads.py` (per C-004: correctness lives in stdlib, scored by the reducer so summaries stay re-reducible):

- `derive_item(suite_seed, n_iter, item_index) -> AffineItem` — §1.1, hashlib-only, pure.
- `render_prompt(item) -> str` — §1.2 template.
- `score_response(text: str, expected: int) -> ScoreResult(parse_status, parsed_value, correct)` — §1.3 rule.
- `scorer_id = "affine_mod_ladder_v1/score_v1"` recorded in outputs.

Reducer flow: for each item, re-derive the item from manifest fields (`suite_seed`, `difficulty.value`, `item_index`, checked against `generator.version`/`parameters_hash`), read the stored raw response text, score, and write results under a **quarantined annotations namespace** in the summary (e.g., `annotations.scored.affine_mod_ladder_v1`: `correct`, `parse_status`, `parsed_value`, `scorer_id`) — never into energy metrics. Re-running `reduce` reproduces scores bit-for-bit; rescoring under a revised scorer is a re-reduce, not a re-run.

Audit chain: the generator writes `expected_answer_sha256 = SHA256("joulewise.affine_answer.v1\x00" + item_id + "\x00" + str(expected))` into the manifest. The scorer recomputes the expected answer and **checks** the hash — mismatch is a hard error (generator/scorer version skew), the hash is never trusted as ground truth. (Honest note: with ≤999 possible answers the hash is trivially brute-forceable; it is an integrity/audit device, not secrecy.)

Denominators (predeclare at campaign AP time; recorded either way): per level report `n_executed`, `n_parsed`, `n_malformed`, `n_correct`. Recommended primary accuracy denominator = all executed items (malformed counts as incorrect — instruction failure is a wrong answer under the output contract), with malformed rate reported alongside. `energy_per_correct` = per-bundle level-window energy / per-bundle level correct count, only after the AP-5 binomial guard (≥3 correct per level per the predeclared unit, else merge adjacent levels or `not estimable`). C-015 status enum applies per item (`succeeded`/`malformed`/`capped`/`below_floor`/...); `below_floor` is the *expected* per-item status on fast models (§2).

---

## 5. Difficulty metadata mapping (C-015 `{axis, value, scale, label, source}`)

```yaml
difficulty:
  axis: iteration_count
  value: 8                      # integer n_iter; also the derivation key
  scale: count                  # linear count axis; ladder samples it geometrically (1..64 powers of two)
  label: "8 iterations"
  source: generator_designed    # vs source_provided for benchmark imports
  quarantine_note: "C-004/C-015: designed effort proxy for stratified envelope analysis; licenses no 'difficulty causes energy' or intelligence-per-joule wording."
shape:                          # shape is NOT difficulty (C-015) — constant across levels by design
  planned_prompt_tokens: ~80    # realized recorded per item
  planned_output_tokens: 16     # natural_eos_capped budget
grouping:
  level_id: L08
  block_id: L08                 # block = level
```

The claim shape this supports is exactly C-004's: level-window *energy* should be ~flat across levels (dense decode FLOPs are shape-fixed; internal "effort" doesn't change per-token compute) — the ladder's output is energy-per-CORRECT rising as accuracy falls, never an energy-vs-difficulty causal curve.

---

## 6. Honest limits (all named, none blocking the smoke)

1. **Accuracy-curve location is unknown and may be degenerate.** Answer-only, in-head modular arithmetic may floor near 0% at *all* levels for a 1.5B model (even n=1 is one 2×3-digit multiply + mod). Then the binomial guard fails everywhere → `not estimable`, which AP-5 already handles; the envelope gate is still fully valid. Recentering (e.g., 2-digit modulus variant) is a new profile revision with a new `parameters_hash`, decided post-smoke — or run the scored campaign on a stronger model.
2. **The §0 level-set reading needs lead ratification** and a one-line bank edit.
3. **Full-ladder k=114 vs C-015 k≤48 default** — named policy conflict, resolvable at campaign time (block=level structure proposed); campaign is deferred regardless.
4. Item-time 0.15 s is a planning estimate; the first smoke bundle calibrates it, with the §2 table as the resizing rule.
5. E4's prompt-token tolerance is tokenizer-dependent (BPE digit merges); recheck per model; the gate stays computed either way.
6. Floors are `pending-P2-015`; smoke bundles feed that calibration but cannot self-certify floors.
7. Per-item joules are unidentifiable at ~8.9 Hz on fast models — by design; per-item records are correctness/token audit evidence only.
8. High-level items can enter short orbits (period < n_iter), so within-level difficulty is heterogeneous at large n; iteration count is a designed effort proxy, not a calibrated psychometric scale. No level-dependent rejection is permitted to "fix" this (§1.1 invariant).
9. Gate thresholds (1.0 token / 5% / p≥0.01 / ±4 prompt tokens) are design-pinned judgment calls justified by the ~4%-of-window energy bound in §3, not derived from measured floors — they can be re-pinned once P2-015 floors exist, via decision-log entry.

Implementation surface: `joulewise/workloads.py` (new, stdlib), suite-manifest profile instance per the C-015 sketch, per-item raw response text in the bundle (P2-010a addition), reducer annotation pass, and the envelope-gate analysis script emitting the D-036-style verdict.

---

# D. Licensing-clean realistic exemplar sources (web-verified)

**Cross-check verdict: sound-with-amendments. Amendments to adjudicate before implementation:**

1. Phase-1 shape conformance: every realistic subset must specify how items realize the pinned common-shape 512/256 fixed_budget_exact stratum (pin a reference tokenizer for selection, define truncation-at-boundary policy, record realized per-model token counts). The Gutenberg ~500/~1500/~3000-token buckets violate this — phase 1 excerpts must fit the 512-token prompt stratum; the 1500/3000 buckets belong to the phase-3 summarization panel (4096/256 per C-005).
2. Restore paired seed-derived synthetic controls in ALL 6 categories, not just JSON. C-005 pins synthetic profiles as the CONTROLS and realistic exemplars as the probes ('every realistic category runs in two modes'); AP-4/C5-W.1 is a paired synthetic-vs-realistic comparison at identical shape. Rewrite 'No other category needs it' and add a synthetic-control column to the decision table.
3. Close the determinism holes in selection rules to selection_rule_sha256 standard (bank C-015 manifest sketch): (a) HumanEval — 'swap within hash order if a quartile is empty' needs an exact algorithm and a pinned tokenizer for the length quartiles, or drop stratification for pure sha256 order; (b) OASST1 — define 'top quality quartile' (which field, which population, tie-breaking) and the three length buckets exactly; (c) record selector_version and selected_item_ids_sha256 per the manifest sketch.
4. Fix the BillSum contradiction: section 3 defers BillSum to phase 2, but section 6 grounds phase-1 JSON generation on 'CC0 BillSum-style bill text'. Phase-1 JSON grounding must be Gutenberg-only (the already-committed summarization subset); note explicitly that cross-category content sharing with summarization is a deliberate content control, and that extraction-over-prose deviates from C-005's 'synthetic fixed-schema records' — record as a design amendment.
5. Council-pinned design changes need discussion + decision-log entries, not silent adoption in a report (global rules 2 and 5): (i) 6 FLORES languages vs the pinned 8-language panel; (ii) chat primary source swap from LMSYS shape-derivation to OASST1; (iii) the JSON design change above. All three are defensible, but each must land as a recorded C-005 amendment.
6. Multilingual two-leg design gap: the single 'Translate into {language}' English-source template cannot produce the semantic-matched leg of C5-W.4 (that leg needs target-language source sentences from the parallel corpus, e.g. X-to-English). Fine for phase 1 (expected token-matched near-null), but the report should say the semantic-matched leg requires a second template and note it for phase 3.
7. Separate frozen source-pool size from per-run item count and repeat count: the pinned full panel is 6 categories x 8 items, n=5, and per-run n must be sized from Window A floors / AP-4 MDE (bundle-level uncertainty), not 'keeps per-run wall time bounded'. The n=32/50/50/30/48/50 figures are fine as frozen pools but must not be presented as run sizes.
8. Align HumanEval with P2-023: the pinned import smoke specifies the 256/512-token completion policy and the C-015 benchmark_import manifest fields (license_text_sha256, source_archive_sha256, revision_or_commit, redistribution_policy, expected_answer quarantined with scorer_allowed:false). The report's 'license id + evidence URL' discipline is a subset of what the contract requires — cite the full field sketch. Also respect C-015 sequencing: HumanEval is the first import, FLORES the second; the six-source table is a selection ranking, not a landing order.
9. Minor factual: the US public-domain line in 2026 is pre-1931 publications (95-year rule), not pre-1929. The stricter cutoff is safe but the report should state the actual rule so the conservatism is visibly a choice, not an error.

## Report

# License-clean exemplar sources for jw_mixed_v1 — per-category research report

Research date: 2026-07-08. All licenses verified against the live source pages today. Discipline assumed throughout: frozen subsets, sha256 manifest, license id + evidence URL recorded per source, synthetic wins ties.

## Cross-cutting legal finding: does CC-BY-SA contaminate the repo?

**No — if scoped correctly.** Creative Commons' own FAQ distinguishes *collections* from *adaptations*: including a CC-BY-SA work verbatim inside a larger work is a collection, and "the collection itself doesn't automatically inherit the ShareAlike requirement" — only an *adaptation* (translated/altered/transformed material) must be SA-licensed ([CC FAQ](https://creativecommons.org/faq/)). Committing a verbatim FLORES subset under `data/flores200/` with its own `LICENSE` (CC-BY-SA 4.0 text), attribution notice, and change note does **not** force the repo's MIT/Apache license to change. Selecting a subset without altering sentence content is reproduction of a portion, not adaptation; even under the most conservative reading, the SA obligation stays scoped to the dataset files themselves. Practical rule: every third-party dataset lives in its own directory with its own LICENSE + ATTRIBUTION file, and the repo README states the repo license "excludes third-party data in `data/`, licensed as marked."

---

## 1. Code — HumanEval

- **License (verified):** MIT, repo-wide badge on [github.com/openai/human-eval](https://github.com/openai/human-eval); the dataset file `data/HumanEval.jsonl.gz` ships inside the MIT-licensed repo with no separate data terms. Cleanest possible case.
- **Commit verbatim?** Yes. MIT requires only copyright + license notice. Commit the subset JSONL, MIT text, and copyright line "(c) 2021 OpenAI".
- **Contamination:** Heavily contaminated — public since mid-2021, memorization documented in multiple contamination studies; irrelevant for energy measurement (we measure joules/token, not pass@1), but record it.
- **Subset:** n=32 of 164 tasks. Deterministic rule: sort by `sha256(task_id)` ascending, take first 32, stratified check that prompt-token-length quartiles are all represented (swap within hash order if a quartile is empty). Full 164 is also small enough to commit whole; 32 keeps per-run wall time bounded.
- **Alternative:** MBPP is CC-BY 4.0 ([google-research-datasets/mbpp](https://huggingface.co/datasets/google-research-datasets/mbpp)) — fine, but HumanEval's MIT is strictly cleaner. No reason to prefer MBPP in phase 1.

## 2. Reasoning — GSM8K

- **License (verified):** MIT — [LICENSE file](https://github.com/openai/grade-school-math/blob/master/LICENSE) reads "MIT License, Copyright (c) 2021 OpenAI"; data lives in the same repo ([openai/grade-school-math](https://github.com/openai/grade-school-math)).
- **Commit verbatim?** Yes, same MIT mechanics as HumanEval.
- **Contamination:** Among the most contaminated benchmarks in existence (the GSM1k replication study documented widespread overfitting); again, harmless for energy measurement.
- **Subset:** n=50 from the 1,319-item test split. Rule: `sha256(question_text)` ascending, first 50; record split, commit hash of the source repo, and per-item sha256 in the manifest.
- **Alternative:** ARC-Challenge is CC-BY-SA 4.0, BBH is MIT — neither beats GSM8K's combination of clean license + natural free-text reasoning shape.

## 3. Summarization — Project Gutenberg excerpts

- **License (verified):** Texts are US public domain. Trademark caveat confirmed at [gutenberg.org/policy/permission.html](https://www.gutenberg.org/policy/permission.html): "you can freely redistribute any eBook... with or without the 'Project Gutenberg' trademark included," but the *name* is a registered trademark and commercial use of the name requires royalties. **Mitigation: strip the PG header/footer and all "Project Gutenberg" references from committed excerpts.** Attribution to author/title (public-domain courtesy, not obligation) goes in the manifest, with the gutenberg.org source URL recorded as evidence only.
- **Commit verbatim?** Yes — public domain, no license text needed; commit a NOTICE explaining PD status and per-item verification that the ebook record said "Public domain in the USA."
- **Contamination:** Total — Gutenberg (PG-19 etc.) is in essentially every pretraining corpus. Fine for our purpose.
- **Subset:** n=30 passages: 10 books × 3 excerpts, each excerpt cut to a target token bucket (~500 / ~1500 / ~3000 tokens) at paragraph boundaries. Deterministic rule: fixed book list (pre-1929 US publications only), excerpt = first complete paragraphs of chapters 1/5/10 up to the bucket cap. Wrap each in a fixed "Summarize the following passage:" template.
- **Alternative:** BillSum is CC0-1.0 ([FiscalNote/billsum](https://huggingface.co/datasets/FiscalNote/billsum); US bills from GPO's govinfo, itself CC0) — a strong second source and stylistically complementary (legal vs. literary). Avoid CNN/DailyMail and XSum: underlying news copyright is genuinely murky. Good phase-2 add; Gutenberg wins phase 1 on length control.

## 4. Chat — OASST1 (new finding: beats shape-derivation)

- **LMSYS-Chat-1M (verified):** gated, custom "LMSYS-Chat-1M Dataset License Agreement" — explicitly: "You should not distribute, copy, disclose, assign, sublicense, embed, host, or otherwise transfer the dataset to any third party," plus a deletion-on-demand clause ([HF page](https://huggingface.co/datasets/lmsys/lmsys-chat-1m)). **Shape-derivation-only is confirmed as the correct call** — the grant covers developing "techniques and technologies," so aggregate turn/length statistics used to parameterize synthetic prompts are permitted; committing any conversation text is not.
- **Better alternative found — OASST1:** Apache-2.0, non-gated, ~88k human-written conversation messages in 24 languages ([OpenAssistant/oasst1](https://huggingface.co/datasets/OpenAssistant/oasst1)). Real human prompts, fully redistributable, quality-rated. This gives chat a *committable realistic* source instead of synthetic-only.
- **Commit verbatim?** Yes — Apache 2.0 requires license text + attribution notice, both trivial.
- **Contamination:** Public April 2023; present in many post-training corpora. Noted, not disqualifying.
- **Subset:** n=50 English root prompter messages, filtered to `review_result=true` and top quality quartile, then `sha256(message_id)` ascending, first 50, stratified across three length buckets. Optionally validate the subset's length/turn distribution against LMSYS-Chat-1M shape statistics (kept out of the repo).
- **Also checked:** [lmsys/chatbot_arena_conversations](https://huggingface.co/datasets/lmsys/chatbot_arena_conversations) — prompts CC-BY-4.0 but the dataset is gated and mixed-license (outputs CC-BY-NC-4.0); messier provenance chain than OASST1, skip. WildChat-1M is ODC-BY and plausible ([allenai/WildChat-1M](https://huggingface.co/datasets/allenai/WildChat-1M)) but contains raw in-the-wild user text with higher toxicity/PII risk for a public undergrad repo — OASST1's human review pipeline wins.

## 5. Multilingual — FLORES-200

- **License (verified):** CC-BY-SA 4.0, confirmed on [facebook/flores](https://huggingface.co/datasets/facebook/flores) ("Licensed with Creative Commons Attribution Share Alike 4.0"). The original [facebookresearch/flores](https://github.com/facebookresearch/flores) repo is archived and points to FLORES+.
- **FLORES+ caveat:** also CC-BY-SA 4.0 but gated, and the stewards explicitly ask "please do not redistribute this file publicly, unless you protect it from automatic scrapping" ([openlanguagedata/flores_plus](https://huggingface.co/datasets/openlanguagedata/flores_plus)). Legally CC-BY-SA permits redistribution, but honoring the steward request matters for an academic project. **Use original FLORES-200 (non-gated, no such request) for verbatim commit; do not commit FLORES+.**
- **Commit verbatim?** Yes, per the ShareAlike analysis above: `data/flores200/` with CC-BY-SA 4.0 license text, attribution ("FLORES-200, Meta AI / NLLB Team"), and a note that files are unmodified selections. Repo license unaffected. If Ed wants zero SA-licensed bytes in the repo at all, the fallback is fetch-at-setup from the stable tarball with a committed sha256 manifest — but this is a preference call, not a legal necessity.
- **Contamination:** devtest public since 2022; likely seen in pretraining. Noted.
- **Subset:** 6 target languages spanning script/tokenizer-cost diversity (e.g., deu, fra, zho_Hans, arb, hin, swh) × 8 devtest source sentences (English side) = 48 translation prompts. Deterministic rule: `sha256(sentence_id)` ascending, first 8 ids, same ids across all languages (parallel corpus makes this exact). Fixed prompt template "Translate the following sentence into {language}:".
- **Alternative:** NTREX-128 is also CC-BY-SA 4.0 ([MicrosoftTranslator/NTREX](https://github.com/MicrosoftTranslator/NTREX)) — same license, less standard; Tatoeba (CC-BY 2.0 FR) has weaker sentence quality. FLORES-200 wins.

## 6. JSON extraction — synthetic-only (phase 1)

- **Finding:** no realistic, license-clean, committable source exists for structured-JSON-extraction prompts. Real-world candidates are either scraped enterprise text (unlicensable), academic NER sets with restrictive terms (CoNLL-2003 is NIST/Reuters-encumbered), or gated. This is the category where "licensing uncertain → synthetic wins" bites cleanly.
- **Recommendation:** ship synthetic-only, but ground it for realism: generate extraction tasks over the *already-committed public-domain Gutenberg excerpts and CC0 BillSum-style bill text* (e.g., "extract all person names, dates, and places from this passage as JSON matching this schema"). That makes the source text realistic and license-clean while the task framing is synthetic — zero incremental license risk, and the JSON schema complexity becomes a controlled variable.
- **Subset:** n=50 generated items, seeded RNG (seed committed), schema complexity stratified (flat / nested / array-of-objects), source passages drawn deterministically from the summarization subset.

---

## Ranked phase-1 decision (jw_mixed_v1)

| Category | Phase-1 realistic source | License | Commit mode |
|---|---|---|---|
| code | **HumanEval** | MIT | verbatim subset, n=32 |
| reasoning | **GSM8K** test | MIT | verbatim subset, n=50 |
| chat | **OASST1** | Apache-2.0 | verbatim subset, n=50 |
| summarization | **Project Gutenberg** excerpts (PG references stripped) | Public domain (US) | verbatim, n=30 |
| multilingual | **FLORES-200** devtest | CC-BY-SA 4.0 (dir-scoped, no repo contamination) | verbatim, 6 langs × 8 = 48 |
| json extraction | **synthetic-only** (grounded on the PD/CC0 texts above) | n/a | generated, seeded, n=50 |

**Synthetic-only in phase 1:** JSON extraction, definitively. No other category needs it — the LMSYS shape-derivation plan for chat is legally correct but is now superseded as the primary source by OASST1 (keep LMSYS shape stats as an optional out-of-repo calibration check, never committed). Every non-PD source directory carries: license id (SPDX), license text file, attribution file, upstream URL + retrieval date, and per-item sha256 in the frozen manifest.

## Sources

- [openai/human-eval (MIT)](https://github.com/openai/human-eval)
- [openai/grade-school-math LICENSE (MIT)](https://github.com/openai/grade-school-math/blob/master/LICENSE)
- [lmsys/lmsys-chat-1m — gated, no-redistribution agreement](https://huggingface.co/datasets/lmsys/lmsys-chat-1m)
- [lmsys/chatbot_arena_conversations — gated, CC-BY-4.0 prompts / CC-BY-NC-4.0 outputs](https://huggingface.co/datasets/lmsys/chatbot_arena_conversations)
- [OpenAssistant/oasst1 — Apache-2.0](https://huggingface.co/datasets/OpenAssistant/oasst1)
- [allenai/WildChat-1M — ODC-BY](https://huggingface.co/datasets/allenai/WildChat-1M)
- [Project Gutenberg permission & trademark policy](https://www.gutenberg.org/policy/permission.html)
- [FiscalNote/billsum — CC0-1.0](https://huggingface.co/datasets/FiscalNote/billsum)
- [facebook/flores — CC-BY-SA 4.0](https://huggingface.co/datasets/facebook/flores)
- [openlanguagedata/flores_plus — gated CC-BY-SA 4.0, anti-scrape request](https://huggingface.co/datasets/openlanguagedata/flores_plus)
- [facebookresearch/flores (archived)](https://github.com/facebookresearch/flores)
- [MicrosoftTranslator/NTREX — CC-BY-SA 4.0](https://github.com/MicrosoftTranslator/NTREX)
- [google-research-datasets/mbpp — CC-BY-4.0](https://huggingface.co/datasets/google-research-datasets/mbpp)
- [Creative Commons FAQ — collections vs. adaptations under ShareAlike](https://creativecommons.org/faq/)