# RPT-001: Capstone report skeleton and end-to-end report vertical slice

Status: DRAFT pending lead adjudication (C-027 spec wave)

Queue authority: `TASK_QUEUE.md` row `RPT-001`.

Binding inputs:

- `docs/reviews/2026-07-09-c027-whole-project-review.md` §2 item 3,
  §5-Q4 gate 4, and §7 rows TOP-6, RIG-2, ARC-9, NEG-2, and NEG-5.
- `docs/reviews/c027/lens-negspace.md` findings 2 and 5 and its investment
  judgment.
- `docs/contracts/capstone_scope.md` / D-052.
- `docs/contracts/claims_ladder.md` / D-037.
- `docs/contracts/token_normalization.md` / D-058.
- `docs/phase_4/phase_4_plan.md` Stages 4.1–4.3 and the F1/F2 figure plan.
- `docs/phase_5/phase_5_plan.md` Stage 5.5.
- The six strict-valid legacy bundles and their two experiment manifests
  under `runs/`.
- Existing consumers `joulewise/aggregate.py` and `joulewise/report.py`.

Named decisions and contracts win over this draft. Any implementation
disagreement is escalated rather than silently resolved in code.

---

## 0. Design rulings and premise corrections

### 0.1 Default report format

Adopt **Pandoc-compatible Markdown as the canonical report source**, assembled
by a stdlib-only build script into one deterministic Markdown document. Do not
make Pandoc, LaTeX, Typst, or a PDF engine part of the RPT-001 acceptance gate.

Rationale:

1. P1-008 has not established the institution’s required file format,
   template, length, or citation style.
2. Markdown preserves the prose, chapter, citation, figure, table, and
   claims-index structure needed now without guessing those requirements.
3. An assembled Markdown document is directly reviewable in GitHub and is a
   valid future input to Pandoc.
4. The eventual renderer is isolated behind a report profile. If P1-008 later
   requires PDF, DOCX, or an institutional LaTeX class, only the renderer,
   style, and front-matter mapping change; chapter sources and analysis
   artifacts do not.
5. Hosted CI currently installs no extras. A renderer that depends on an
   unpinned system binary would make the claimed byte-stability false.

The default is therefore a defensible report-source format, not an assertion
that Markdown itself is the final submission container.

### 0.2 Source directory

Use `docs/report_src/`, not root `report/`.

Root `report/` is already ignored by `.gitignore` and is the conventional
output directory for the existing:

```sh
python3 -m joulewise report runs --output report
```

That command produces a per-run HTML browser through
`joulewise/report.py`. Reusing the same directory for the capstone source
would conflate a generated run browser with the graded written artifact and
would require changing an existing documented convention.

`docs/report_src/` keeps the scholarly source tracked while preserving
`report/` as disposable run-browser output.

### 0.3 Existing consumer roles

Two prompt premises need explicit narrowing:

- `joulewise/aggregate.py` is an experiment-manifest uncertainty aggregator.
  It does not implement the Stage-4 one-row-per-bundle dataset described in
  `phase_4_plan.md`. RPT-001 must reuse `aggregate_experiment()` for group
  summaries, not pretend the full Stage-4 aggregation layer already exists.
- `joulewise/report.py` is a static run browser requiring matplotlib. It is
  not a thesis/report assembler. RPT-001 must not overload or replace it.

Both files remain valid consumers and regression constraints. No RPT-001
change should alter their behavior.

### 0.4 CI availability of the real corpus

The six legacy bundles are ignored by Git and total approximately 110 MB.
They will not be present in a clean hosted-CI checkout. Therefore:

- the lead acceptance gate runs the complete bundle-to-report command locally
  against the real six bundles;
- hosted CI exercises bundle ingestion with synthetic strict-valid fixtures;
- hosted CI regenerates downstream artifacts from a committed sealed dataset
  produced by the local real-bundle gate;
- CI output must say that real-bundle ingestion was not rerun;
- no fixture or sealed dataset may be described as live hardware validation.

A future published bundle pack may enable full real-corpus CI, but RPT-001
does not depend on REPRO-001 or external publication.

### 0.5 Claims tooling

`scripts/claims_lint.py` currently has no Phase-4/claims-index mode. RPT-001
owns the first `phase4` mode, extending the existing linter as required by
D-059. This is new implementation work, not configuration of an existing
mode.

### 0.6 Figure dependency and byte stability

The existing `[analysis]` extra names matplotlib without an exact version,
and normal CI installs no extras. Matplotlib output therefore cannot honestly
be promised byte-identical across the Python 3.11/3.14 matrix.

The RPT-001 figure uses a deliberately small stdlib SVG renderer. This is a
vertical-slice backend, not a ruling that all twelve final figures must be
hand-rendered SVG. Phase 4 may move final figures to a pinned plotting
environment under REPRO-001.

---

## 1. Required outcome and acceptance boundary

RPT-001 is complete only when one command can regenerate this chain:

```text
six pinned strict-valid legacy bundles
  -> sealed one-row-per-bundle dataset
  -> experiment aggregate artifact
  -> report-shaped figure
  -> result table + full stack-identity table
  -> one canonical claims-index row
  -> one assembled report page
```

The slice is an engineering and writing-path demonstration. It makes no
comparative or scaling finding.

The six bundles remain:

- legacy;
- pre-2M;
- manual-review evidence;
- L1 instrument observations only.

The following are forbidden outcomes:

- an L2 comparison between the two model stacks;
- a size, architecture, active-parameter, or efficiency-scaling conclusion;
- a tokenizer-blind per-token ranking;
- a “winner,” “savings,” or “more efficient” statement;
- an invented detection-floor or P2-037 verdict;
- treating missing legacy provenance as if it had been captured.

The exact rendered label on the figure, table, report page, and claims row is:

> legacy L1 (manual review; pre-2M)

---

## 2. Report source and scholarly build

### 2.1 Directory layout

Create:

```text
docs/report_src/
  README.md
  report.json
  report.md
  references.csl.json
  source_map.json
  chapters/
    00_abstract.md
    01_introduction.md
    02_problem_and_scope.md
    03_background_and_related_work.md
    04_contributions.md
    05_harness_design.md
    06_methodology.md
    07_results.md
    08_discussion_and_limitations.md
    09_conclusion.md
  appendices/
    A_reproducibility.md
    B_claims_index.md
    C_stack_identity.md
  generated/
    rpt001_vertical_slice.md
```

Generated files carry this first line:

```markdown
<!-- GENERATED by scripts/build_capstone.py; DO NOT EDIT. -->
```

`report.md` is only an ordered include manifest. Chapter prose lives in the
chapter files; generated result content lives under `generated/`.

### 2.2 Report profile

`docs/report_src/report.json` is stdlib-readable JSON with at least:

```json
{
  "schema": "joulewise.report_profile.v1",
  "source_format": "pandoc_markdown",
  "default_target": "assembled_markdown",
  "bibliography": "references.csl.json",
  "chapters": [
    "chapters/00_abstract.md",
    "chapters/01_introduction.md",
    "chapters/02_problem_and_scope.md",
    "chapters/03_background_and_related_work.md",
    "chapters/04_contributions.md",
    "chapters/05_harness_design.md",
    "chapters/06_methodology.md",
    "chapters/07_results.md",
    "chapters/08_discussion_and_limitations.md",
    "chapters/09_conclusion.md",
    "appendices/A_reproducibility.md",
    "appendices/B_claims_index.md",
    "appendices/C_stack_identity.md"
  ],
  "format_adapter": {
    "status": "pending-P1-008",
    "renderer": null,
    "template": null
  }
}
```

The assembler rejects unknown schema versions, missing chapters, duplicate
chapter paths, absolute paths, paths outside `docs/report_src/`, and unresolved
include directives.

### 2.3 Chapter skeleton and contribution-ladder mapping

| Chapter | Draft state at RPT-001 | Contribution role |
|---|---|---|
| Abstract | Deliberate scaffold; no headline result language yet. | Summarizes only after results freeze. |
| Introduction | Substantive stable draft now. | Frames consumer, problem, and auditability warrant. |
| Problem and scope | Substantive stable draft now. | D-052 frozen headline and stop-lines. |
| Background and related work | Assembly stub wired to the existing 11-source draft and bibliography. | Positions Rung 2 novelty; does not redo research. |
| Contributions | Substantive stable draft now. | Explicit Rung 1 → Rung 2 → Rung 3 ladder. |
| Harness design | Substantive stable draft now. | Rung 1 instrument contribution. |
| Methodology | Substantive stable draft now. | Rung 1 evidence/measurement warrant. |
| Results | Contains only the RPT-001 legacy-L1 page initially. | Demonstrates the consumer path; not a comparative finding. |
| Discussion and limitations | Structured scaffold plus current single-unit/boundary limitations. | Protects claim ceilings. |
| Conclusion | Deliberate scaffold. | Written after supported contribution rungs are known. |
| Reproducibility appendix | Commands and artifact map now; release details later. | Audit path. |
| Claims index appendix | Generated view. | Claim-to-evidence spine. |
| Stack identity appendix | Generated full D-058 table. | Boundary and stack interpretation. |

### 2.4 Prose that must be drafted now

The following files must contain actual reviewable prose, not only headings or
generic TODOs:

1. `01_introduction.md`
   - why local LLM energy is a decision problem;
   - named consumers from `capstone_scope.md`;
   - why latency/throughput alone are insufficient;
   - why auditability is a warrant rather than the empirical contribution.

2. `02_problem_and_scope.md`
   - frozen D-052 umbrella headline;
   - exact stack-bound scope;
   - explicit non-claims;
   - minimum-viable fallback story;
   - split inference described only as a gated stretch extension.

3. `04_contributions.md`
   - Rung 1 instrument/methodology;
   - Rung 2 scoped empirical coverage, conditional on filled-matrix and
     related-work support;
   - Rung 3 contingent scientific findings;
   - explicit statement that an unresolved or boring matrix is not a failed
     instrument result.

4. `05_harness_design.md`
   - config → adapters → run bundle → validation → reduction → analysis;
   - raw evidence versus derived summaries;
   - shared `BundleReader` role;
   - existing run browser clearly distinguished from the capstone report.

5. `06_methodology.md`
   - lifecycle and measured-window definition;
   - gross and idle-subtracted bases;
   - measurement boundaries;
   - repetitions/order/quality flags;
   - strict validation’s actual guarantee;
   - claims ladder and floor/verdict routing at a high level.

These drafts may contain explicit `PENDING RESULT` markers only where the
content genuinely requires future data. They may not contain `TBD` for facts
already settled by contracts.

### 2.5 Contract transclusion, not manual mirroring

The repository has demonstrated that manually maintained mirrors drift. Exact
contract-bearing content therefore uses build-time inclusion.

Supported directive:

```markdown
{{jw:include-section path="docs/contracts/capstone_scope.md" heading="Frozen Headline Claim"}}
```

The assembler:

1. resolves the exact heading;
2. fails on missing or duplicate headings;
3. copies the section body without modifying it;
4. records the source path and SHA-256 in the build source manifest;
5. never writes back to the contract.

At minimum, use transclusion for:

- D-052 frozen headline;
- D-052 contribution ladder;
- D-052 single-unit limitation language;
- the measurement-boundary table;
- the run-bundle directory shape;
- D-058 primary-metric rule;
- D-058 full stack-identity field definition.

Large internal status prose should not be transcluded merely for convenience.
Authored narrative surrounds the exact binding blocks.

Every substantive authored chapter begins with a non-rendered dependency block:

```markdown
<!-- jw:contract-sources
docs/contracts/capstone_scope.md#Frozen Headline Claim
docs/contracts/claims_ladder.md#Global Rules
-->
```

The report linter verifies that each named source and heading exists. This
does not pretend semantic paraphrases can be mechanically proven correct; it
makes dependencies visible and leaves exact high-risk wording generated.

### 2.6 Bibliography pipeline

Create `docs/report_src/references.csl.json` as the canonical citation metadata
source. Seed it with the eleven verified keys from
`docs/phase_4/related_work_draft.md`:

- `joulesort2007`
- `splitwise-isca2024`
- `distserve`
- `mooncake`
- `mlperf_power`
- `zeus`
- `tokenpowerbench`
- `mlenergy_benchmark`
- `intelligence_per_watt`
- `bench360`
- `chung2026joules`

CSL JSON is preferred to a manually parsed BibTeX subset because:

- Python can validate it with the standard library;
- Pandoc accepts CSL JSON directly;
- identifiers, author arrays, dates, titles, DOI/arXiv IDs, and venue notes
  remain structured;
- the report build requires no citation package.

Report prose cites sources using Pandoc citation keys such as
`[@joulesort2007]`.

Update the related-work draft’s citation section during implementation so it
points to `docs/report_src/references.csl.json` rather than maintaining a
second full metadata table. Preserve unresolved camera-ready checks, including
the MLPerf Power venue note, in structured `note` fields or
`source_map.json`; do not silently resolve them.

`source_map.json` records which related-work draft sections feed which report
chapter subsections. The report chapter is initially an assembly/distillation
stub; it must not trigger new literature research.

Build-time bibliography checks:

- unique non-empty citation IDs;
- every `[@key]` resolves;
- all eleven seeded keys remain present;
- DOI/arXiv/URL identifiers are strings, not invented;
- build performs no network access;
- unused references warn but do not fail during RPT-001.

---

## 3. Analysis inputs and provenance

### 3.1 Pinned input manifest

Create:

```text
analysis/rpt001-v1/input_manifest.json
```

Minimum shape:

```json
{
  "schema": "joulewise.report_analysis_input.v1",
  "artifact_version": "rpt001-v1",
  "evidence_class": "legacy_l1_manual_review_pre_2m",
  "runs_root": "runs",
  "experiments": [
    {
      "experiment_id": "example-mac-mlx-local",
      "manifest_path": "runs/experiments/example-mac-mlx-local.json",
      "manifest_sha256": "<filled by implementation>",
      "members": [
        "example-mac-mlx-local__r1",
        "example-mac-mlx-local__r2",
        "example-mac-mlx-local__r3"
      ]
    },
    {
      "experiment_id": "example-mac-mlx-qwen35-122b-512t",
      "manifest_path": "runs/experiments/example-mac-mlx-qwen35-122b-512t.json",
      "manifest_sha256": "<filled by implementation>",
      "members": [
        "example-mac-mlx-qwen35-122b-512t__r1",
        "example-mac-mlx-qwen35-122b-512t__r2",
        "example-mac-mlx-qwen35-122b-512t__r3"
      ]
    }
  ],
  "bundle_tree_sha256": {
    "example-mac-mlx-local__r1": "<filled>",
    "example-mac-mlx-local__r2": "<filled>",
    "example-mac-mlx-local__r3": "<filled>",
    "example-mac-mlx-qwen35-122b-512t__r1": "<filled>",
    "example-mac-mlx-qwen35-122b-512t__r2": "<filled>",
    "example-mac-mlx-qwen35-122b-512t__r3": "<filled>"
  },
  "analysis_manifest_ref": null,
  "claim_verdict_ref": {
    "schema": "joulewise.claim_verdict.v1",
    "path": null,
    "sha256": null
  }
}
```

A bundle-tree digest is the SHA-256 of the canonical sorted list of every
relative file path, byte SHA-256, and size in the bundle. Use the same
file-identity semantics as `scripts/package_bundle_pack.py`; do not identify a
bundle from `config.json` alone.

All paths stored in committed artifacts are repository-relative. Absolute
local paths are forbidden.

### 3.2 Input gate

Before writing any output, `scripts/make_figures.py` must:

1. load and schema-check the input manifest;
2. require exactly two experiment manifests and six unique member IDs;
3. verify experiment-manifest hashes and exact membership/order;
4. verify each bundle-tree hash;
5. run the current strict validator on every bundle;
6. require six `status=succeeded` summaries;
7. read bundle data through `BundleReader`;
8. record all quality flags and missing provenance fields;
9. fail if a manifest member is missing or an unlisted member is introduced;
10. stage output only after every input passes.

Strict validation is the existing legacy-allowlist route. The analysis artifact
must say that explicitly; it must not relabel these as current-era provenance
bundles.

The command is read-only with respect to `runs/`. It must never invoke
post-hoc `reduce` on the source bundles or modify any evidence file.

### 3.3 Dataset artifact

Generate:

```text
analysis/rpt001-v1/dataset.csv
```

One row per bundle, sorted by `experiment_id`, then repetition number.

Required columns:

- `run_id`
- `experiment_id`
- `repetition`
- `bundle_tree_sha256`
- `config_sha256`
- `strict_validation`
- `evidence_class`
- `stack_id`
- `hardware_target_id`
- `hardware_model`
- `model_name`
- `model_family`
- `model_revision`
- `quantization_name`
- `quantization_bits`
- `quantization_group_size`
- `workload_name`
- `prompt_text_sha256`
- `runtime_output_tokens`
- `token_count_source`
- `runtime_stop_reason`
- `output_policy`
- `gross_energy_j`
- `energy_request_j`
- `energy_output_token_j`
- `ttft_s`
- `throughput_tokens_s`
- `cooldown_cap_hit`
- `boundary_label`
- `telemetry_backend`
- `bundle_path`

Missing legacy values are serialized as the literal `unknown`, not empty
cells. Numeric nulls remain empty only when the metric itself is unavailable;
their status must be represented by an adjacent status field.

CSV rules:

- UTF-8;
- `\n` line endings;
- RFC-4180 quoting through `csv`;
- fixed column order above;
- full finite numeric precision using a single pinned formatter;
- no timestamps, host paths, locale-dependent formatting, or Git tree state.

### 3.4 Aggregate artifact and existing consumer reuse

Generate:

```text
analysis/rpt001-v1/aggregates.json
```

For each experiment, call `joulewise.aggregate.aggregate_experiment()`.
Do not implement a second mean/SD/interval engine in the plotting script.

The artifact preserves the aggregator’s:

- raw repetition count;
- arithmetic mean;
- sample standard deviation;
- Student-t interval fields;
- `below_headline_protocol`;
- missing-member data;
- outlier status;
- energy uncertainty fields.

The RPT-001 figure deliberately does not render the Student-t interval; see
§4.2. Preserving it in the analysis artifact keeps the consumer path honest
without promoting that interval into a legacy comparative claim.

### 3.5 P2-042 and P2-037 seams

RPT-001 does not implement the frozen contrast manifest or claim engine.

It pins these future consumer rules:

- `analysis_manifest_ref` is null for the legacy L1 slice.
- `claim_verdict_ref` is null for the legacy L1 slice.
- L0/L1 observations may render with `verdict_ref.status =
  not_applicable_l1`.
- Any future L2/L3 row must provide both a P2-042 analysis-manifest reference
  and a P2-037 verdict reference.
- Plotting/report code may select, format, and display a verdict. It may not
  calculate, reinterpret, or upgrade it.
- The accepted P2-037 verdict vocabulary is:
  `not_estimable`, `not_resolvable`, `unresolved`,
  `direction_supported`, and `equivalent`.
- Unknown verdict schemas or unrecognized reason codes fail closed.
- A non-null verdict artifact is addressed by schema, relative path, SHA-256,
  and row ID; a bare path is insufficient.

Minimum future verdict reference:

```json
{
  "schema": "joulewise.claim_verdict.v1",
  "path": "analysis/verdicts/<artifact>.json",
  "sha256": "<sha256>",
  "row_id": "<verdict-row-id>",
  "contrast_id": "<P2-042 contrast-id>",
  "status": "direction_supported",
  "reason_codes": []
}
```

This seam does not pre-judge the full P2-037 artifact schema.

---

## 4. Figure and table design

### 4.1 Versioned outputs

Generate and track:

```text
figures/rpt001-v1/F1_legacy_l1_instrument_results.svg
analysis/rpt001-v1/tables/T1_legacy_l1_results.csv
analysis/rpt001-v1/tables/T1_legacy_l1_results.md
analysis/rpt001-v1/tables/S1_legacy_stack_identity.csv
analysis/rpt001-v1/tables/S1_legacy_stack_identity.md
analysis/rpt001-v1/artifact_manifest.json
```

`F1_legacy_l1_instrument_results` is intentionally not the final Phase-4 F1.
It is an F1-style vertical-slice artifact. Final registry ownership remains
with Stage 4.2.

A material semantic change after merge requires `rpt001-v2`; do not silently
change the meaning of a versioned artifact. Exact regeneration of v1 is
allowed and expected.

### 4.2 Honest n=3 spread representation

Use:

- all three raw points;
- a mean marker;
- a min-to-max whisker;
- sample SD in the table;
- no inferential error bar in the figure.

Do not use the 95% Student-t interval as the visible error bar for this slice.

Rationale:

1. n=3 is sufficient for an L1 instrument observation but below the n>=5
   headline-comparison protocol.
2. The repetitions are sequential legacy observations, not a randomized
   comparative design.
3. One small-stack repetition carries a cooldown-cap quality flag.
4. A t interval at two degrees of freedom is extremely assumption-sensitive
   and visually invites an inference this page is forbidden to make.
5. Raw points plus observed range make the actual evidence legible without
   pretending the range is a population interval.
6. The final Phase-4 F1 can use design-respecting intervals and P2-037
   verdicts once the production corpus exists.

The caption must say:

> Points are the three retained sequential repetitions; the marker is the
> arithmetic mean and the whisker is the observed min–max range, not a
> confidence interval.

### 4.3 Figure layout

The SVG has two panels:

- **Panel A, primary and at least 60% of plot width:** request energy.
  - idle-subtracted `energy_request_j` is the visually primary series;
  - gross `gross_energy_j` is a hollow/context series;
  - both bases are named in axis/legend text.
- **Panel B, companion:** idle-subtracted
  `energy_output_token_j`, displayed as mJ/runtime-observed output token.

Fixed rules:

- stack order is lexical by stable `stack_id`;
- repetition point offsets are fixed `[-1, 0, +1]`, never random jitter;
- axes start at zero;
- no ratio, delta, percent difference, frontier, ranking, or significance
  annotation;
- request energy has equal or greater visual salience than the per-token
  panel;
- SVG contains no date, absolute path, random ID, generator version timestamp,
  or font embedding;
- all coordinates and displayed values use fixed deterministic precision.

Required visible footer:

> legacy L1 (manual review; pre-2M) · n=3 per exact stack · Apple SoC
> CPU+GPU+ANE package-power boundary · descriptive stack-specific
> observations; no cross-stack efficiency or scaling claim · full identities:
> Table S1

Per-token footer:

> Output-token values use runtime-observed counts. Tokenizer identity was not
> captured in these legacy bundles; values are tokenizer-scoped descriptors,
> not comparable work units.

### 4.4 Result table T1

T1 contains one row per stack and these columns:

- stack ID;
- model display name;
- n;
- gross J/request: mean, sample SD, min–max;
- idle-subtracted J/request: mean, sample SD, min–max;
- idle-subtracted mJ/runtime-observed output token: mean, sample SD, min–max;
- mean throughput;
- mean TTFT;
- boundary;
- evidence label;
- quality-waiver note.

Column order gives request metrics greater salience than token metrics.

Reference values that the implementation’s golden test must reproduce before
display rounding:

| Stack | Metric | Mean | Sample SD |
|---|---|---:|---:|
| Qwen2.5-1.5B legacy stack | gross J/request | 47.22042349222679 | 0.6925294273729872 |
| Qwen2.5-1.5B legacy stack | idle-subtracted J/request | 44.42591347410544 | 3.2688350349895874 |
| Qwen2.5-1.5B legacy stack | idle-subtracted J/output-token | 0.08676936225411219 | 0.006384443427714038 |
| Qwen3.5-122B-A10B legacy stack | gross J/request | 304.02005544776165 | 0.8978118844403994 |
| Qwen3.5-122B-A10B legacy stack | idle-subtracted J/request | 298.68731644234157 | 0.5926770973521417 |
| Qwen3.5-122B-A10B legacy stack | idle-subtracted J/output-token | 0.5833736649264484 | 0.0011575724557659017 |

Display rounding:

- request energy: one decimal joule;
- token companion: one decimal mJ;
- throughput: one decimal token/s;
- TTFT: one decimal ms;
- SD and range use the same display precision as their mean.

No displayed ratio or subtraction between stack rows is allowed.

### 4.5 Stack-identity table S1

S1 implements all eleven D-058 fields for both stacks:

1. hardware unit;
2. OS + version;
3. runtime + version;
4. kernel/library where known;
5. model artifact hash;
6. quantization;
7. tokenizer identity, including prompt source/BOS handling when applicable;
8. sampler/output policy;
9. batching/concurrency policy;
10. measurement boundary;
11. telemetry backend.

Every cell is a concrete value or an explicit:

- `unknown (legacy bundle)`, or
- `unavailable (not captured)`.

Do not infer a tokenizer identity from the model name. Do not treat a model
repository revision as a byte hash. Those are separate fields.

Known legacy values include:

- target `macbook_m3_max`;
- hardware model `Mac15,9`;
- macOS platform/build evidence from metadata;
- MLX 0.31.2 and mlx-lm 0.31.3 where captured;
- model names and revisions;
- int4 quantization, with group size 64 only where recorded;
- Apple SoC CPU + GPU + ANE package-power boundary;
- powermetrics telemetry;
- runtime-observed output count 512.

Expected explicit unknowns include, unless direct bundle inspection finds a
concrete recorded field:

- physical unit identifier beyond target/model;
- model artifact byte hash;
- tokenizer name/revision/class/vocabulary size;
- prompt source and BOS handling;
- sampler settings and runtime stop reason;
- batching/concurrency policy;
- kernel/attention implementation.

The figure names S1, and the report page places S1 immediately after T1. The
page also transcludes D-052’s single-unit limitation language.

---

## 5. Claims-index artifact and Phase-4 lint mode

### 5.1 Canonical and rendered forms

Canonical machine-readable row:

```text
analysis/rpt001-v1/claims_index.jsonl
```

Generated human view:

```text
docs/phase_4/claims_index.md
```

JSONL is canonical because Phase-4 checks require nested evidence, metric,
basis, waiver, and future verdict references that are unsafe to maintain in a
very wide Markdown table. The Markdown file remains the human-facing artifact
named by `phase_4_plan.md` and is regenerated from JSONL.

This is a deliberate deviation from the plan’s Markdown-as-source design, not
removal of the Markdown index.

### 5.2 RPT-001 row shape

The generated row has this shape and values:

```json
{
  "schema": "joulewise.claims_index.v1",
  "claim_id": "CLM-RPT001-LEGACY-L1-001",
  "claim_text": "Across three strict-valid legacy runs per exact stack, mean idle-subtracted request energy was 44.42591347410544 J for stack LEGACY-M3MAX-QWEN25-15B-MLX and 298.68731644234157 J for stack LEGACY-M3MAX-QWEN35-122B-A10B-MLX; these are separate stack-specific L1 observations, not a cross-stack comparison, efficiency ranking, or scaling claim.",
  "claim_level": "L1",
  "claim_role": "secondary",
  "status": "supported",
  "evidence_class": "legacy_l1_manual_review_pre_2m",
  "legacy_label": "legacy L1 (manual review; pre-2M)",
  "figure_ids": [
    "F1_legacy_l1_instrument_results"
  ],
  "table_ids": [
    "T1_legacy_l1_results",
    "S1_legacy_stack_identity"
  ],
  "analysis_function": "make_f1_legacy_l1_instrument_results",
  "dataset_filter": "artifact_version == rpt001-v1",
  "bundle_ids": [
    "example-mac-mlx-local__r1",
    "example-mac-mlx-local__r2",
    "example-mac-mlx-local__r3",
    "example-mac-mlx-qwen35-122b-512t__r1",
    "example-mac-mlx-qwen35-122b-512t__r2",
    "example-mac-mlx-qwen35-122b-512t__r3"
  ],
  "manifest_ids": [
    "example-mac-mlx-local",
    "example-mac-mlx-qwen35-122b-512t"
  ],
  "stack_ids": [
    "LEGACY-M3MAX-QWEN25-15B-MLX",
    "LEGACY-M3MAX-QWEN35-122B-A10B-MLX"
  ],
  "boundary_labels": [
    "Apple SoC CPU + GPU + ANE package power"
  ],
  "metrics": [
    {
      "metric": "gross_energy_j",
      "basis": "gross request",
      "unit": "J/request",
      "denominator_provenance": "request"
    },
    {
      "metric": "energy_request_j",
      "basis": "idle-subtracted request",
      "unit": "J/request",
      "denominator_provenance": "request"
    },
    {
      "metric": "energy_output_token_j",
      "basis": "idle-subtracted output-token companion",
      "unit": "J/runtime-observed output token",
      "denominator_provenance": "runtime_observed",
      "tokenizer_identity": "unknown (legacy bundle)"
    }
  ],
  "strict_validation": {
    "result": "passed",
    "mode": "strict",
    "legacy_allowlist": true
  },
  "quality_waivers": [
    {
      "scope": "example-mac-mlx-local__r2",
      "reason": "cooldown cap hit was recorded; the point is retained and visibly reported under the legacy manual-review carve-out"
    },
    {
      "scope": "token-normalized companion metrics",
      "reason": "legacy bundles predate captured tokenizer identity, sampler/output policy, and stop-reason provenance; values remain explicitly tokenizer-unknown L1 descriptors and support no ranking"
    }
  ],
  "floor_ref": {
    "status": "not_applicable_legacy_l1",
    "artifact": null,
    "row_id": null
  },
  "analysis_manifest_ref": null,
  "verdict_ref": {
    "schema": "joulewise.claim_verdict.v1",
    "status": "not_applicable_l1",
    "artifact": null,
    "sha256": null,
    "row_id": null,
    "contrast_id": null,
    "reason_codes": []
  },
  "claim_ceiling_reason_codes": [
    "legacy_pre_2m",
    "n3_below_l2_protocol",
    "no_interleaved_cross_condition_design",
    "no_detection_floor_artifact",
    "no_contrast_verdict",
    "tokenizer_identity_unavailable"
  ],
  "artifact_manifest": "analysis/rpt001-v1/artifact_manifest.json"
}
```

The row may gain additive source-hash fields during implementation. Required
field names and semantics above do not change without lead adjudication.

### 5.3 `claims_lint --mode phase4`

Extend `scripts/claims_lint.py` with:

```sh
python3 scripts/claims_lint.py \
  --mode phase4 \
  --claims-index analysis/rpt001-v1/claims_index.jsonl
```

`phase4` becomes part of default `all` only after the canonical file exists.

Hard errors:

- malformed JSONL or non-object row;
- wrong/unknown schema;
- missing or duplicate `claim_id`;
- invalid ladder level;
- invalid existing Phase-4 status
  (`supported`, `weak`, `refuted`, `out-of-data`);
- missing figure, table, manifest, bundle, or analysis reference;
- artifact path outside the repository;
- missing D-058 stack field or silent empty value;
- per-token metric without co-displayed request energy;
- per-token metric without denominator provenance;
- cross-tokenizer ranking language when tokenizer identity differs or is
  unknown;
- legacy input without the exact legacy label;
- L2/L3/L4 row with null P2-042 or P2-037 reference;
- L2/L3/L4 row whose claim level exceeds the verdict’s ceiling;
- a current L1 row with a directional/equivalence verdict;
- unknown verdict status or reason-code type;
- `status=supported` for a below-floor or not-estimable future verdict;
- claim text using comparative/ranking language not supported by its level;
- generated Markdown view diverging from canonical JSONL.

Warnings:

- unused figure/table;
- explicit unknown legacy stack values;
- one-sentence claim text longer than the configured readability threshold;
- quality waiver present, requiring lead review.

Warnings do not silently become passes in the generated report: every waiver
is rendered adjacent to the result.

---

## 6. Build commands and deterministic behavior

### 6.1 Commands

Full local real-bundle build:

```sh
python3 scripts/build_capstone.py \
  --profile rpt001 \
  --runs-root runs
```

Read-only comparison against committed output:

```sh
python3 scripts/build_capstone.py \
  --profile rpt001 \
  --runs-root runs \
  --check
```

Hosted-CI offline build:

```sh
python3 scripts/build_capstone.py \
  --profile rpt001 \
  --offline \
  --check
```

Independent analysis command:

```sh
python3 scripts/make_figures.py \
  --profile analysis/rpt001-v1/input_manifest.json \
  --runs-root runs
```

`--offline` is explicit; there is no silent fallback when bundles are missing.

### 6.2 Full-build order

`build_capstone.py` performs:

1. load report and analysis profiles;
2. run `make_figures.py` into a staging directory;
3. validate the six real bundles and regenerate dataset/aggregate artifacts;
4. render SVG and tables;
5. emit canonical claims JSONL;
6. run Phase-4 claims lint against staged artifacts;
7. render `docs/phase_4/claims_index.md`;
8. resolve contract/source includes;
9. validate citation keys;
10. generate `docs/report_src/generated/rpt001_vertical_slice.md`;
11. assemble the complete report Markdown under
    `build/capstone/rpt001/report.md`;
12. hash every versioned output;
13. write `artifact_manifest.json` last;
14. atomically replace only the owned output files.

A failed step publishes no partial tracked output.

### 6.3 Offline-build boundary

Offline mode:

- verifies the committed input and output manifests;
- uses the committed sealed `dataset.csv` and `aggregates.json`;
- regenerates figure, tables, claims row, claims view, report page, and
  assembled report;
- does not claim to revalidate or reread real bundles;
- prints:

```text
rpt001: offline artifact regeneration; real bundle ingestion not rerun
```

### 6.4 Byte-stability contract

Two consecutive builds over the same inputs and code must produce identical
bytes for every versioned output.

Required controls:

- sorted input/member/field order;
- fixed CSV and JSON serialization;
- JSON uses `indent=2`, `sort_keys=True`, UTF-8, and one trailing newline;
- JSONL rows use sorted keys and one newline per row;
- no wall-clock timestamp;
- no hostname, username, temp path, or absolute path;
- no dirty-tree marker in generated science artifacts;
- fixed display precision;
- fixed point offsets;
- no random seed because no randomness is used;
- stable SVG element/attribute order;
- no SVG metadata/date;
- generic font-family names only;
- normalized `\n` line endings;
- artifact manifest excludes its own hash.

`artifact_manifest.json` includes:

- schema and artifact version;
- input manifest SHA-256;
- each experiment-manifest SHA-256;
- all six bundle-tree digests;
- generator source-file SHA-256 values;
- every output relative path and SHA-256;
- explicit build mode (`real-bundles` or `offline-derived`);
- no creation time.

---

## 7. The report vertical-slice page

`docs/report_src/generated/rpt001_vertical_slice.md` must contain, in order:

1. heading: “Legacy vertical-slice instrument results”;
2. an explicit statement that the page tests the analysis/report path;
3. exact legacy-L1 label;
4. Figure F1 and its full caption;
5. Table T1;
6. quality-waiver paragraph;
7. Table S1;
8. D-052 single-unit limitation language;
9. D-058 tokenizer-scope limitation;
10. claims row ID `CLM-RPT001-LEGACY-L1-001`;
11. artifact regeneration command;
12. a link/path to `artifact_manifest.json`.

Forbidden on the page:

- “comparison” as a scientific result;
- “more/less efficient”;
- “scales with model size”;
- active-parameter interpretation;
- percent or ratio between stacks;
- significance language;
- floor-clearing language;
- “representative of M3 Max” beyond the exact physical unit;
- any implication that strict validation is physical calibration.

---

## 8. Implementation targets and order

### 8.1 New implementation files

- `docs/report_src/README.md`
- `docs/report_src/report.json`
- `docs/report_src/report.md`
- `docs/report_src/references.csl.json`
- `docs/report_src/source_map.json`
- all chapter and appendix files listed in §2.1
- `scripts/report_support.py`
- `scripts/make_figures.py`
- `scripts/build_capstone.py`
- `analysis/rpt001-v1/input_manifest.json`
- generated analysis/figure/report artifacts listed above
- `tests/test_make_figures.py`
- `tests/test_build_capstone.py`

### 8.2 Modified files

- `scripts/claims_lint.py`
- `tests/test_claims_lint.py`
- `.github/workflows/ci.yml`
- `docs/phase_4/claims_index.md` (new generated view at the plan’s named path)
- `docs/phase_4/related_work_draft.md` citation-source pointer
- `.gitignore` only as needed for `/build/`; do not repurpose ignored root
  `report/`
- bookkeeping files required by the repository process after implementation.

### 8.3 Files expected to remain unchanged

- `joulewise/report.py`
- `joulewise/aggregate.py`, unless an independently justified small public
  helper is needed; its statistical behavior must not change under RPT-001
- all six source bundles;
- both source experiment manifests;
- binding claim/normalization/scope contracts.

### 8.4 Order of work

1. Add tests for report profile, claims schema, deterministic SVG, and
   byte-stable assembly.
2. Implement `phase4` lint parsing and negative fixtures.
3. Add report-source skeleton and transclusion assembler.
4. Add bibliography and source mapping.
5. Add input manifest and bundle extraction.
6. Reuse `aggregate_experiment()` and generate the sealed dataset.
7. Generate SVG and tables.
8. Generate claims row and Markdown view.
9. Assemble report page and full report.
10. Run the full real-bundle command twice and compare hashes.
11. Run canonical tests in a normal writable environment.
12. Record lead review, queue/checklist state, and the run report.

---

## 9. Tests and CI obligations

### 9.1 `tests/test_make_figures.py`

Required tests:

- a synthetic six-bundle/two-experiment fixture renders successfully;
- strict-invalid input fails before any output;
- missing member fails;
- unlisted extra member fails;
- bundle-tree hash mismatch fails;
- experiment-manifest hash mismatch fails;
- source bundle bytes are unchanged after build;
- dataset has exactly six rows in pinned order;
- repository-relative paths only;
- `aggregate_experiment()` values feed the summary;
- raw point count is three per stack and metric;
- SVG contains mean and min–max, not “95% CI”;
- fixed point offsets are deterministic;
- request energy is rendered before and with greater salience than token
  energy;
- gross and idle-subtracted bases are both named;
- exact legacy label appears;
- boundary label and S1 reference appear;
- no comparative/ranking/scaling forbidden phrase appears;
- missing legacy stack fields render explicit unknown/unavailable;
- sample SD and golden means match §4.4;
- two independent output directories hash identically.

### 9.2 `tests/test_build_capstone.py`

Required tests:

- profile schema validation;
- chapter order;
- missing chapter failure;
- include path traversal rejection;
- missing/duplicate contract heading failure;
- all includes resolved in output;
- source manifest records included section hashes;
- all citation keys resolve;
- duplicate citation ID fails;
- generated page contains F1, T1, S1, claim ID, and build command;
- output has no timestamp or absolute path;
- unknown format adapter fails;
- `assembled_markdown` works without Pandoc or analysis extras;
- offline mode prints its evidence limitation;
- `--check` reports the first differing file and exits 2.

### 9.3 `tests/test_claims_lint.py`

Add positive and mutation-style negative tests for:

- valid legacy L1 row;
- duplicate claim ID;
- malformed JSONL;
- missing stack field;
- empty stack field;
- missing legacy label;
- token metric without request-energy companion;
- token metric without runtime-observed provenance;
- cross-tokenizer forbidden ranking;
- missing figure/table/artifact;
- L2 without analysis manifest;
- L2 without verdict;
- L1 with directional verdict;
- unknown verdict;
- claim-level ceiling violation;
- generated Markdown drift.

Each negative test must fail against a deliberate one-field mutation of the
known-good row.

### 9.4 Golden actual-data test

The real-corpus acceptance command verifies:

- six of six strict-valid;
- both manifests match;
- exact aggregate reference values in §4.4;
- one quality waiver for the recorded small-stack cooldown-cap condition;
- all current missing legacy identity fields remain explicit.

This gate is lead-run in the workspace containing the six bundles. It is not
silently skipped.

### 9.5 CI hook

Add after the normal unit-test step:

```yaml
- name: Capstone report vertical slice (stdlib, offline)
  run: |
    python scripts/claims_lint.py --mode phase4 \
      --claims-index analysis/rpt001-v1/claims_index.jsonl
    python scripts/build_capstone.py --profile rpt001 --offline --check
```

Run under both existing Python versions. No new package install is permitted
for this job.

The ordinary suite remains:

```sh
python3 -m unittest discover -s tests
```

---

## 10. Fences

1. **No measurements.** RPT-001 is `[AGENT]` work and performs no
   `[QUIET-MAC]` collection, powermetrics session, detection-floor run, or
   production campaign.

2. **No evidence mutation.** Source bundles and experiment manifests are
   immutable inputs.

3. **No claim upgrade.** The six bundles remain legacy L1; no L2/L3 result is
   emitted.

4. **No statistical comparison.** Do not calculate or display between-stack
   deltas, ratios, tests, effect sizes, or comparative intervals.

5. **No tokenizer-blind ranking.** Per-output-token values are companion
   descriptors only and always co-display request energy.

6. **No hidden quality flags.** The cooldown-cap flag and missing legacy
   provenance are rendered and indexed.

7. **No invented metadata.** Model names or revisions do not supply missing
   tokenizer identities, artifact hashes, sampler settings, or unit IDs.

8. **No P1-008 speculation.** Do not choose margins, page limits, institution
   branding, citation style, DOCX/PDF, demo expectations, or submission dates.
   Only the format-adapter seam is created.

9. **No P2-037 implementation.** Plotting consumes future verdicts; it does
   not calculate them.

10. **No P2-042 shadow manifest.** The legacy input manifest is provenance,
    not a contrast registry.

11. **No fixture-as-hardware representation.** Synthetic CI fixtures verify
    code only.

12. **No new breadth.** RPT-001 produces the minimum complete graded-artifact
    path and does not add research questions, campaign packs, or site features.

13. **No root `report/` repurposing.** Existing run-browser conventions remain
    intact.

14. **No manual edits to generated files.** Changes originate in source,
    profiles, or generators.

---

## 11. Acceptance checklist

RPT-001 passes only when all boxes are true:

- [ ] `docs/report_src/` exists with the complete chapter skeleton.
- [ ] Introduction, problem/scope, contribution, harness, and methodology
      contain substantive stable draft prose.
- [ ] D-052 contribution ladder maps visibly to report chapters.
- [ ] Binding blocks are transcluded, not copied.
- [ ] The eleven-source bibliography is canonical CSL JSON and builds offline.
- [ ] The related-work draft feeds the report without a second metadata mirror.
- [ ] The full command validates exactly six pinned real bundles.
- [ ] Source bundle bytes are unchanged.
- [ ] Dataset contains six rows and reconciles exactly with the two manifests.
- [ ] Aggregates reuse `aggregate_experiment()`.
- [ ] Figure F1 shows all raw points, means, and min–max ranges.
- [ ] No inferential error bar is used for n=3.
- [ ] Figure and T1 name gross/idle-subtracted bases.
- [ ] Request energy has equal or greater salience than per-token energy.
- [ ] Figure, T1, report page, and claims row carry the exact legacy-L1 label.
- [ ] S1 contains all eleven D-058 fields with concrete or explicit unknown
      values.
- [ ] Tokenizer-unknown limitation is visible.
- [ ] The cooldown-cap waiver is visible.
- [ ] One canonical claims JSONL row exists.
- [ ] `claims_lint --mode phase4` passes.
- [ ] The generated Markdown claims view matches JSONL.
- [ ] P2-042/P2-037 references are null and fail closed for the L1 slice.
- [ ] One command regenerates dataset, aggregate, figure, tables, claim row,
      report page, and assembled report.
- [ ] Two builds produce identical output hashes.
- [ ] Hosted CI passes without analysis extras.
- [ ] Hosted CI labels its offline evidence boundary.
- [ ] `python3 -m unittest discover -s tests` passes in a writable environment.
- [ ] Lead reviews the final diff and actual-data artifact manifest.
- [ ] No new measurement or claim upgrade occurred.

---

## 12. Deviations from earlier plans

### DEV-1: `docs/report_src/` rather than root `report/`

Accepted in this draft because root `report/` is already ignored and occupied
semantically by the static run browser. Revisit only if the existing command
changes its default output convention.

### DEV-2: Assembled Markdown rather than PDF as the RPT-001 gate

P1-008 is unknown. A renderer-neutral source is the smallest truthful
submission seam. A pinned final renderer becomes mandatory after P1-008, not
before.

### DEV-3: Stdlib SVG rather than matplotlib

Required for honest cross-version byte stability under the current no-extras
CI. This is scoped to the vertical slice, not a final Phase-4 plotting decree.

### DEV-4: Raw points + min–max rather than F1’s planned 95% CI

The original F1 plan targets the production corpus. For these n=3 sequential
legacy observations, raw points/range plus tabulated sample SD are more honest.
The aggregate artifact retains its t interval for audit.

### DEV-5: JSONL canonical claims index plus generated Markdown view

The Phase-4 plan names a Markdown table. D-059 and the future P2-037 seam need
structured nested references. The human artifact remains at the named Markdown
path, while JSONL prevents a second manually synchronized claim source.

### DEV-6: Two-tier real/local and offline/CI acceptance

The real bundles are ignored and approximately 110 MB. Claiming hosted CI
reruns them would be false. Local full ingestion plus hermetic CI downstream
regeneration is the defensible interim shape.

---

## 13. Open questions for lead adjudication

None blocks implementation.

1. Ratify `docs/report_src/` as the permanent source home.
2. Ratify the visible n=3 representation: raw points + mean + observed range,
   with sample SD only in T1.
3. Ratify JSONL as the canonical claims-index source and Markdown as its
   generated projection.
4. Ratify the stable stack IDs used in the example row.
5. Decide whether a future published bundle pack should become a separate
   full-real-corpus CI job. That belongs with REPRO-001 and does not block
   RPT-001.
6. P1-008 later selects the actual renderer/template. Do not resolve it in
   this implementation.

---

## CHECKS PERFORMED

Read-only repository inspection:

- targeted `RUN_STATE.md` intake sections;
- current queue and Do-Not-Do-Yet list;
- Mission M0 and orchestration guidance;
- C-027 whole-project review;
- NEGSPACE findings 2 and 5 and investment judgment;
- D-052, D-058, and proposed D-060;
- capstone scope, claims ladder, token normalization, methodology, run-bundle,
  adapter, and analysis-plan contracts;
- Phase-4 and Phase-5 plans;
- all eleven related-work citation entries and assembly notes;
- `joulewise/aggregate.py`, `joulewise/report.py`,
  `scripts/claims_lint.py`, CI, packaging, and dependency configuration;
- six legacy bundle configs, metadata, summaries, and both experiment
  manifests;
- `.gitignore` and tracked/untracked corpus state.

Commands/checks:

- all six `python3 -m joulewise validate-bundle --strict` commands passed;
- aggregate reference means, SDs, and current t-interval fields were
  recomputed with `aggregate_experiment()`;
- current AP/registry/pack claims-lint modes returned zero errors and zero
  warnings;
- canonical suite attempted: `Ran 877 tests`; 553 errors and 10 skips because
  the managed read-only environment exposed no writable temporary directory.
  The errors were `tempfile` setup failures, not observed assertion failures;
- file creation was attempted through `apply_patch` and rejected by the
  read-only sandbox before the target file was created;
- no hardware command, network call, measurement session, bundle mutation,
  or repository write was performed;
- final workspace check found the shared repository had changed externally
  from `c027-council-review` to `main` with `docs/specs/c027/` untracked.
  Those concurrent artifacts were left untouched.
```

No `RUN_STATE.md`, `TASK_QUEUE.md`, or run-report update was possible under the same read-only restriction.