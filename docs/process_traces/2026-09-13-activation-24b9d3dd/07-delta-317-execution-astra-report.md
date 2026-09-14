```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"Docs coverage remains incomplete: 15 ordinary documentation-asserting modules and one exclusive module are omitted; concurrency is repaired.",
  "workspace":{"base_requested":"f5f2403e","base_mode":"exact","head_start":"8819cb5fd8ee33daaf06d28302867be2464e3f56","head_end":"8819cb5fd8ee33daaf06d28302867be2464e3f56","upstream_end":null,"branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"findings":[
    {"id":"R1","severity":"blocker","file":".github/workflows/ci.yml","line":171,"summary":"Literal-prefix regex misses documentation assertions using joined paths or imported path constants."},
    {"id":"R2","severity":"blocker","file":".github/workflows/ci.yml","line":176,"summary":"Exclusive exclusion removes test_calibration_exits, which asserts Markdown content; its exclusive job skips docs-only runs."},
    {"id":"R3","severity":"nit","file":".github/workflows/ci.yml","line":130,"summary":"Missing detector output enables both docs-readers and the full matrix, duplicating work."}
  ]},
  "verification":[
    {"id":"V1","kind":"inspection","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 /private/tmp/ci317-audit.py --imports","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["IMPORTS 48 / 48 PASS Python 3.14.7"]},"expected":{"exit_code":0,"tail_regex":"IMPORTS 48 / 48 PASS"}},
    {"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /private/tmp/ci317-import-venv/bin/python -B /private/tmp/ci317-counterexamples.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["CENSUS 15 ordinary omissions + 1 exclusive omission confirmed"]},"expected":{"exit_code":0,"tail_regex":"CENSUS 15 ordinary"}},
    {"id":"V3","kind":"lint","cmd":"git diff --check f5f2403e..8819cb5f","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V4","kind":"inspection","cmd":"git status --short","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags":[
    {"id":"F1","kind":"verification_gap","level":"nonblocking","text":"Offline review: scheduling and expression behavior modeled locally; no hosted execution or GitHub API queries.","needs":"Lead should verify the final candidate on hosted runners and inspect required checks."}
  ]
}
```

## Findings

**R1 — blocker: incomplete selection, `.github/workflows/ci.yml:171–177`.** Runtime derivation does not make this regex complete. Joined paths and imported constants bypass it. These 15 ordinary modules assert documentation content yet are absent from the selected set.

The census command is V2 above; its output includes each cited read/assertion. Paths below are under `tests/`; paired lines identify the read/path and assertion.

| Unselected module file | Evidence and content assertion |
|---|---|
| `test_build_capstone.py:51,53` | Joined docs path; committed generated Markdown must equal builder output |
| `test_claims_index_lint.py:382,388,559` | Imported `DEFAULT_AP_PATH` / `DEFAULT_CLAIMS_LADDER_PATH`; all-mode CLI must return zero |
| `test_dependence_sensitivity.py:614,620` | Reads document; requires documented worked-example row |
| `test_gen_derivation_night.py:1003,1004` | `GEN.RUNSHEET_PATH.read_text()`; generated region must occur in runsheet |
| `test_gen_g2_phase_d.py:52,56` | Reads runsheet; pins fenced-shell block inventory |
| `test_midcampaign_cure_generation_docs.py:35,38` | Reads transaction record; pins non-configuration cure definition |
| `test_modularity.py:226,227` | Parses joined `analysis_plans.md` path; asserts AP-2 selection semantics |
| `test_paper_build.py:95,103` | Runs Markdown checker on real draft; asserts success, independently of optional renderer |
| `test_paper_renumber_refs.py:136,140` | Pins real draft digest and reference mapping |
| `test_paper_replay_fence.py:64,95` | Reads skeleton; pins historical-arithmetic wording |
| `test_paper_round7_artifacts.py:1324,1334,1359` | Reads checklist/skeleton; asserts their prose relationship |
| `test_render_results_fills.py:273,290,297` | Imported template/registry paths; lints template and checks registry rows |
| `test_results_prose_template.py:20,30` | Reads `LINTER.TEMPLATE_PATH`; real template must pass semantic lint |
| `test_schemas.py:630,637,690` | Reads adapter contract/decision log; asserts documented vocabulary |
| `test_workload_sizing.py:17,20` | Joined Markdown path; pins retirement authority |

Imported-path evidence:

```text
scripts/claims_lint.py:37:DEFAULT_AP_PATH = Path("docs/contracts/analysis_plans.md")
scripts/claims_lint.py:40:DEFAULT_CLAIMS_LADDER_PATH = Path("docs/contracts/claims_ladder.md")
scripts/gen_derivation_night.py:50:
    REPO_ROOT / "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"
docs/process_traces/2026-08-07-plan-factory/lint_results_prose_template.py:13:
    TEMPLATE_PATH = Path(__file__).with_name("DRAFT-RESULTS_PROSE.md")
```

V2 ran the real workload-sizing assertion before and after intercepting only its Markdown read. No tracked file was changed:

```text
tests.test_workload_sizing selected=False baseline=PASS docs-mutation=AssertionError
```

Other unselected readers inspected:

- `test_env_locks.py:81` reads a docs-resident **JSON** receipt; `test_run_night.py:1248` reads `cold_start.json`. Those changes already trigger the matrix.
- `test_check_gate_ledger.py:253,399` reads `.github/pull_request_template.md`; that nested path triggers the matrix.
- `test_issue_dg071_dg075_statistics.py:115,344,575` reads generated temporary Markdown, not committed documentation.
- Comment-only references, such as `test_detection_floor.py:4` and `test_git_fixture_maintenance.py:32`, are harmless mentions.
- The `rg` sweep for `glob`, `rglob`, joins and suffix checks found no additional unselected Markdown glob/suffix-scan reader. The `.md` `with_suffix` cases above concern temporary artifacts.

**R2 — blocker: exclusive documentation assertions disappear, `.github/workflows/ci.yml:176,287`.** `exclusive_modules` contains:

```text
tests.test_calibration_exits
tests.test_calibration_writer_crash_matrix
```

`test_calibration_exits.py:1503` reads `calibration_ledger_append.md`; line 1527 asserts generated registry equality. Lines 1528–1533 read `window_runbook.md` and assert amendment anchors. Even a broader regex would still exclude this module.

V2 output:

```text
tests.test_calibration_exits selected=False baseline=PASS docs-mutation=AssertionError
Tracked docs were never written; mutation was in-memory only
CENSUS 15 ordinary omissions + 1 exclusive omission confirmed
```

No documentation-content assertion was found in `test_calibration_writer_crash_matrix`; importing a helper from `test_calibration_exits` does not execute that module’s tests.

**R3 — nit: duplicate fallback work, `.github/workflows/ci.yml:130,197`.** This follows the fix contract, but contradicts “runs only when the matrix does not.” Missing output satisfies both inequalities.

V1 parsed the YAML and modeled the expressions:

| Detector/workflow outcome | docs-readers | test | exits-exclusive | crash-exclusive |
|---|---:|---:|---:|---:|
| `code == 'true'` | No | Yes | Yes | Yes |
| `code == 'false'` | Yes | No | No | No |
| Failed detector, missing output | Yes | Yes | Yes | Yes |
| Workflow cancelled | No | No | No | No |
| Dependency alone cancelled, workflow not cancelled, output missing | Yes | Yes | Yes | Yes |

The explicit status function prevents the implicit `success()` prerequisite from defeating failure fallback. Workflow cancellation intentionally stops execution; no non-cancelled missing-output coverage gap was found.

V1 YAML job listing, abbreviating the two printed expressions as D/F:

```text
D = ${{ !cancelled() && needs.changes.outputs.code != 'true' }}
F = ${{ !cancelled() && needs.changes.outputs.code != 'false' }}
job                                      needs    if
changes                                  -        -
fences                                   -        -
docs-readers                             changes  D
test                                     changes  F
calibration-exits-exclusive               changes  F
calibration-writer-crash-matrix-exclusive  changes  F
build                                    -        -
installed-wheel                          build    -
```

**Full selected list**, from executing the YAML Python through partition estimation, before `run_units`:

```text
DOCS READERS selected=48 of 230
tests.test_analysis_manifest
tests.test_arm_readiness_dry_run
tests.test_arm_readiness_evidence_author
tests.test_arm_readiness_registry
tests.test_arm_readiness_schemas
tests.test_bridge
tests.test_build_site_parsers
tests.test_capture_t0_step
tests.test_check_window_provenance
tests.test_claims_lint
tests.test_coldgate_charter_v3
tests.test_d078_reason_registry
tests.test_d117_contrast_v5_pack
tests.test_d117_decode_contrast_plan
tests.test_d117_floor_qwen25_1p5b_plan
tests.test_d117_floor_qwen25_7b_plan
tests.test_d117_gamma_d139a2_families
tests.test_d165_dominance_closeout
tests.test_d165_rationale_census
tests.test_docs_freshness
tests.test_floor_extraction
tests.test_gen_state
tests.test_identity_pins
tests.test_launcher_argv_regression
tests.test_magistrate_watchdog
tests.test_mint_floor_artifact
tests.test_night_gate
tests.test_pack_capsule
tests.test_package_bundle_pack
tests.test_paper_comparison_placements
tests.test_paper_custody
tests.test_paper_first_use_ledger
tests.test_paper_reported_energy
tests.test_paper_successor_migration
tests.test_paper_terms_lint
tests.test_partial_record_enclosure
tests.test_preflight
tests.test_quiet_guard
tests.test_receipt_histsem
tests.test_rpt001_report_slice
tests.test_rpt002_related_work
tests.test_s0_line_audit_guard
tests.test_select_outcome_branches
tests.test_single_count_discipline_census
tests.test_single_count_discipline_matrix
tests.test_validate_powermetrics_fiducial
tests.test_whole_window_selection
tests.test_window_env_allowlist
DOCS READERS SHARD ESTIMATES 692.141,692.149
```

**Environment/API checks.** V1 compared parsed steps: checkout v5/depth 0, compileall, and zsh guard are identical. Both use `SHARD_INDEX`; neither installs Python packages or defines additional job/workflow environment. Docs uses Python 3.11; test uses 3.11/3.14.

Fresh `venv --without-pip` environments ran `[python, '-B', '-c', 'import '+module]` separately for every selected module:

```text
IMPORTS 48 / 48 PASS Python 3.14.7
IMPORTS 48 / 48 PASS Python 3.11.15
BASH SYNTAX 21/21 PASS
```

`scripts/shard_tests.py` definitions at lines 104,142,512,547,701, with multiline signatures joined:

```python
def load_timing_map(path: Path | str = DEFAULT_TIMINGS_PATH) -> dict[str, float]:
def conservative_unknown_weight(path: Path | str = DEFAULT_TIMINGS_PATH) -> float:
def partition_modules(modules, timings: dict[str, float], shard_count: int, *, unknown_weight: float | None = None) -> tuple[tuple[str, ...], ...]:
def partition_totals(partitions, timings: dict[str, float], *, unknown_weight: float | None = None) -> tuple[float, ...]:
def run_units(units, shard_count: int, shard_index: int) -> int:
```

All call shapes match. Estimates are about 11.54 minutes each, leaving roughly 348 minutes against six hours; these are estimates, not hosted measurements.

**Concurrency repaired, `ci.yml:11–12`.** `&&`/`||` returns operands. For push, the comparison is false, so the expression returns `github.run_id`. For PR, nonempty `github.ref` wins. V1 model output:

```text
CONCURRENCY push 101 ci-101 cancel=False
CONCURRENCY push 102 ci-102 cancel=False
CONCURRENCY pull_request 103 ci-refs/pull/317/merge cancel=True
CONCURRENCY pull_request 104 ci-refs/pull/317/merge cancel=True
```

Two main pushes have distinct groups and cannot evict each other through this concurrency setting. Two updates to one PR share a group; the newer replaces pending work and cancels active work. PR classification uses the cumulative base-to-head range.

`git diff --check f5f2403e..8819cb5f` and final `git status --short`: exit 0, empty output. HEAD unchanged; no repository writes.

Same signature: YES — documentation-asserting tests still do not execute on docs-only runs; the queued-code-push eviction signature is repaired.

## Residual risk

No full suite or hosted workflow was executed. Static dependency inspection cannot establish completeness for arbitrary dynamic readers.

**What the lead should double-check:** remedy both joined/imported-path selection and exclusive-module coverage, then validate the integrated candidate on hosted runners. GitHub APIs would have been used to inspect actual job conclusions and branch-protection/ruleset requirements; none were queried.