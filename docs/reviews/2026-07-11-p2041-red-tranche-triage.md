# P2-041 RED-tranche deletion triage (gpt-5.6-sol xhigh, 2026-07-11)

> Context: impl/p2041 WIP [RED] snapshot d0bc777 pre-unioned main-post-#48 content
> INCOMPLETELY. This audit classifies every deletion region vs main as (A) intentional
> P2-041/C5-rename consequence, (B) pre-union artifact that would regress main, or
> (C) unadjudicated change needing a lead ruling. Commissioned by the C-028 lead
> before rebuilding the branch; the raw 'git diff 3cbe0a7' must NOT be applied wholesale.

The patch must not be applied wholesale. The ~4,909 deletions are dominated by pre-union artifacts: complete P2-038 production-evidence paths, P2-040 remainder behavior, their contracts, and their tests disappear without replacements.

Audit basis:

- `dee9c99` intentionally changed only seven files: `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/contracts/run_bundle_layout.md`, `docs/decision_log.md`, the P2-041 report, `scripts/run_campaign.py`, and `tests/test_run_campaign.py`.
- C5 legitimately expands that footprint, but only around `claim_eligibility` → `window_evidence_precheck`, reducer `0.4.0`, removal of the generic `request` alias, and corresponding tests/docs.
- Searches found no replacements for deleted `ClockStamp`, `TelemetryStopResult`, `derive_powermetrics_clock_evidence`, `ConfigKeyWarning`, `runtime_cleanup_ok`, production shakedown helpers, or their tests.
- The seven uncommitted `test_run_campaign.py` fixture corrections are valid composition fixes and should be retained.

## Verdict table: mixed files

| File | Deletion region(s) | Verdict and evidence | Required action |
|---|---|---|---|
| `RUN_STATE.md` | Header; active stop card; P2-038/P2-040/P2-042/RPT status; verification; workspace; next-step blocks | **B.** All deleted text records work already present in main. P2-041 only adds its own handoff; it has no business reverting the rest. | Start with main’s file. Re-add only the rebuilt P2-041 status, verification, and report pointer after verification. |
| `TASK_QUEUE.md` | P2-038, P2-040 remainder, RPT-001, P2-042, P2-043..048, CI-002, REPRO-002, P0-003 and shelf rows | **B.** These are post-#48 queue facts with no P2-041 replacements. | Keep main verbatim. |
|  | P2-041 `NEW` row replaced by WIP status | **A.** Necessary bookkeeping for the tranche, though final wording should describe the rebuilt head, not `d0bc777`. | Manually update this one row after rebuild. Also change P2-038 acceptance to `window_evidence_precheck.idle_subtracted_request.eligible`. |
| `docs/contracts/run_bundle_layout.md` | `metadata.config_warnings` at main ~48 | **B.** `ConfigKeyWarning` implementation was also deleted; C5 is unrelated. | Preserve main hunk. |
|  | Entire P2-038 production uncertainty section at ~256 | **B.** Clock/phase/drift evidence and raw post-idle sentinel are absent everywhere else. | Preserve main section; update its final “claim eligibility” wording to the C5 term. |
|  | `runtime_cleanup_ok` at ~308 | **B.** P2-040 remainder contract and production field are both otherwise lost. | Preserve main hunk. |
|  | Reducer `0.3.0/0.3.1` dispatch paragraph at ~333 | **A+B composition.** Bump to `0.4.0` is C5, but current text silently drops main’s frozen `0.3.1`/projected `0.3.0` history. | Re-derive: `0.4.0` exact; current-era `0.3.1` and `0.3.0` require re-reduction; retain historical version semantics. |
|  | `claim_eligibility` row/reasons and generic `request` alias at ~349 | **A.** Replaced at current ~311 by `window_evidence_precheck`, metric-specific request entries, and no new generic alias. | Apply C5 hunk. |
|  | Campaign provenance/verdict section | **A**, subject to the wire-name uncertainty below. | Apply after resolving `claim_readiness` vs `analysis_readiness`. |
| `docs/decision_log.md` | D-060 accepted/ratified → proposed, at table and D-060 body | **B.** This reverts an Ed-ratified main decision. | Preserve main. |
|  | D-030 P2-038 timestamp amendment and P2-040 `0.3.1` amendment replaced by C5 amendment | **A+B composition.** C5 amendment is additive; it must not erase either earlier amendment. | Keep both main amendments, then append the C5 `0.4.0` amendment. |
|  | P2-041 reason vocabulary | **A.** Matches `dee9c99`, with later hardening additions. | Append; do not replace adjacent decisions. |
| `docs/phase_2/detection_floor.md` | P2-038 sentinel runtime cost and landed-state tense | **B.** Reverts the post-#48 production path to “future work.” | Preserve main. |
|  | `claim_eligibility` field bullet | **A.** Exact C5 rename. | Change only this bullet to `window_evidence_precheck`. |
| `docs/specs/c027/analysis_engine_trio.md` | `claim_readiness` → `analysis_readiness` in C4/C7/C8 | **C.** `dee9c99` and main’s adjudicated spec use `claim_readiness`; this is a separate wire rename, not C5. | Lead must decide whether a second schema-name change was approved. If not, retain `claim_readiness`. |
|  | First-run exemption changed from first physical run per session to once across all resumes | **C.** Stronger fail-closed behavior, but not in `dee9c99`. | Confirm intended exemption identity: physical session or analysis-manifest lifetime. |
|  | Open H3 question replaced by implemented/re-derived cooldown evidence | **A.** P2-041 owns H3 and current runner contains the replacement. | Apply, once the exemption rule is settled. |
|  | `top_up_suspected:false` replaced by scoped scan/reasons | **C.** Sensible hardening, but from the uncorroborated round rather than `dee9c99`. | Confirm acceptance of `top_up_detection_scope_incomplete` and the changed v2 shape. |
| `docs/specs/c027/p2-038_production_uncertainty_evidence.md` | All claim-field/request-path occurrences | **A.** Exact C5 replacement lives at `window_evidence_precheck.idle_subtracted_request`. | Apply those textual replacements. |
|  | `idle_drift_guard` pending/null schema replaced by `0.0` and empty strings | **B.** Main’s P2-038/P2-039 handoff is silently weakened; unrelated to C5. | Keep main guard block exactly. |
| `docs/specs/c027/p2-040_reducer_gate_correctness.md` | Closing-fence/newline hunk | **A/neutral.** No semantic main content is deleted. | Apply the C5 supersession note; retain the historical P2-040 spellings below it. |
| `joulewise/cli.py` | P2-038 imports and `_strict_uncertainty_evidence_problems` (~779–988); current-era raw reconstruction (~997+) | **B.** Entire strict re-derivation path disappears with no replacement. | Preserve main imports/functions and both legacy/current raw-anchor arms. |
|  | Strict field names and reducer dispatch | **A+B composition.** C5 requires `window_evidence_precheck` and `0.4.0`; runtime-cleanup output must remain, while `0.3.x` current-era summaries should be rejected for re-reduction. | Re-derive this hunk manually; do not copy either side wholesale. |
| `joulewise/reduce.py` | Helper/object names and removal of generic `request` alias (~445–588) | **A.** Replacement helpers exist as `_window_evidence_precheck*`; metric-specific entries remain. | Apply C5 hunks. |
|  | `runtime_cleanup_ok=reader.runtime_cleanup_ok()` at main ~902 | **B.** C5 does not remove cleanup evidence. | Restore this argument in the `0.4.0` summary. |
| `joulewise/schemas.py` | `ConfigKeyWarning`, key tables, warning emission/serialization | **B.** P2-040 remainder implementation vanishes without replacement. | Preserve main machinery. |
|  | `SUMMARY_REDUCER_VERSION`, summary field/schema rename | **A.** Exact C5 migration to `0.4.0` and `window_evidence_precheck`. | Apply. |
|  | `MeasurementQuality.runtime_cleanup_ok` and JSON Schema property | **B.** Independent P2-040 governed field. | Preserve under `0.4.0`. |
| `scripts/run_campaign.py` | Member `quality_flags`, `verdict_for`, legacy verdict JSON/console | **A.** Replaced by `collection_integrity_flags`, `claim_evidence_flags`, `collection_verdict_for`, and separate readiness at current ~1050 and ~2240+. | Apply the verdict-split implementation. |
|  | P2-042 `CONFIG_SIDECAR_NAMES`/discovery lines | **A composition.** Replacement `NON_CONFIG_SIDECARS` still excludes both order and analysis manifests, and the loader calls P2-042’s authoritative validator. | Retain the replacement; do not restore the old name. |
|  | `--shakedown-gate`, `ShakedownGateError`, P2-038 assertion/execution helpers (~271, ~455–640), and both run-loop shakedown branches | **B.** Entire production shakedown is deleted; no replacement exists. | Restore main’s helpers and flow, then change its request lookup to `window_evidence_precheck.idle_subtracted_request`. |
|  | `backup_runs` return value | **B.** P2-038 uses the exit code to fail its backup gate. | Retain main’s integer return. |
| `tests/test_cli_run.py` | Claim-field paths, reducer version expectations | **A.** Update to `0.4.0`/`window_evidence_precheck`; old current-era summaries should require re-reduction. | Apply C5 expectations. Add an explicit `0.3.1` rejection case as well as `0.3.0`. |
|  | Runtime-cleanup absence/exactness and tampered-summary tests | **B.** Production field remains required in `0.4.0`; tamper coverage has no equivalent replacement. | Restore tests and adapt their expected version to `0.4.0`. |
| `tests/test_p2038_production_path.py` | Entire file | **B**, with a required C5 edit. The 286-line production-path suite has no replacement. | Take main’s file, then replace its three `claim_eligibility.request` lookups with `window_evidence_precheck.idle_subtracted_request`. |
| `tests/test_run_campaign.py` | Main fixtures generalized for frozen manifest/config identity and the seven local stale-fixture fixes | **A.** Replacement helpers carry `config_path`, preserve repetition identity, and the focused/canonical runs were reported green. | Retain these fixture changes. |
|  | Old verdict/waiver/quality assertions | **A.** Replaced by collection/readiness assertions and new mutation tests. | Apply P2-041 test tranche. |
|  | P2-038 imports, shakedown CLI option, and final three shakedown tests (~2136–2228) | **B.** No replacement. | Restore and adapt to the C5 shakedown path. |
| `tests/test_schemas.py` | Reducer version assertion | **A.** Expected version becomes `0.4.0`. | Apply. |
|  | `runtime_cleanup_ok` nullable-schema test | **B.** Field remains required as an optional governed property. | Restore unchanged. |
| `tests/test_uncertainty_p2029.py` | All `claim_eligibility` helper/object references and generic request assertions | **A.** Exact replacements exist throughout as `window_evidence_precheck`; generic alias checks become `assertNotIn("request", ...)`. | Apply the worktree version. |

## Verdict table: pure artifact deletions

Every region below is **B**. Exact restoration action: do not apply any deletion hunk; take the file from fresh `origin/main`.

| File(s) | Deleted content and evidence |
|---|---|
| `configs/campaigns/p2_015_smoke/production_shakedown/order_manifest.json` | Entire P2-038 shakedown order. |
| `configs/campaigns/p2_015_smoke/production_shakedown/p2038_production_shakedown.json` | Entire production shakedown config. |
| `docs/JouleWise_Hardening_Proposal.md` | Entire 940-line received proposal. |
| `docs/contracts/measurement_methodology.md` | P2-040 post-warmup settling and cleanup-quality methodology. |
| `docs/milestones.md` | Ratified D-060 activation reverted to proposed. |
| `docs/phase_2/phase_2_exit_checklist.md` | P2-040 evidence row. |
| `docs/phase_2/phase_2_plan.md` | Implemented `warmup_seconds` and cleanup-quality lifecycle. |
| `docs/reviews/2026-07-10-hardening-adjudication.md` | Entire adjudication record. |
| `docs/risk_register.md` | P0-003/R-016 mitigation and D-060 state reverted. |
| `docs/run_reports/2026-07-10-p2038-fix-round.md` | Entire P2-038 fix report. |
| `docs/run_reports/2026-07-10-p2038-production-uncertainty.md` | Entire production-evidence report. |
| `docs/run_reports/2026-07-10-p2040-remainder.md` | Entire P2-040 remainder report. |
| `docs/run_reports/2026-07-10-p2040-versioning-fix.md` | Entire reducer-version report. |
| `docs/specs/c027/p2-039_floor_artifact.md` | `idle_drift_guard` schema member. |
| `joulewise/__init__.py` | `ConfigKeyWarning` export. |
| `joulewise/adapters/powermetrics.py` | Clock stamps, bounded stop evidence, post-idle sentinel, modern raw reconstruction, executable injection, and all P2-038 metadata. |
| `joulewise/bundle_read.py` | `runtime_cleanup_ok()` reader. |
| `joulewise/clock.py` | `ClockStamp`, `stamp()`, and wall/monotonic envelope information. |
| `joulewise/controller.py` | P2-038 evidence lifecycle plus P2-040 settling/config warnings. |
| `joulewise/interfaces.py` | `TelemetryStopResult`, `BoundedTelemetryAdapter`, and `IdleDriftEvidenceProvider`. |
| `joulewise/uncertainty_evidence.py` | Entire 291-line P2-038 derivation module. |
| `tests/fixtures/fake_powermetrics_process.py` | Entire production-shaped fake process. |
| `tests/test_audit_schema_edges.py` | Unknown-key warning contract tests. |
| `tests/test_bundle_read.py` | Runtime-cleanup reader tests. |
| `tests/test_clock.py` | Clock-stamp tests. |
| `tests/test_controller.py` | Warmup, cleanup, clock-bound, and post-idle controller coverage. |
| `tests/test_reduce.py` | Runtime-cleanup propagation tests. |
| `tests/test_uncertainty_evidence.py` | Entire P2-038 derivation suite. |

All generated site deletion hunks are also **B as patch artifacts**:

- `docs/site/adapter_contracts.html`
- `docs/site/council_log.html`
- `docs/site/decision_log.html`
- `docs/site/latest_run_report.html`
- `docs/site/library.html`
- `docs/site/measurement_methodology.html`
- `docs/site/record.html`
- `docs/site/roadmap.html`
- `docs/site/run_state.html`
- `docs/site/status.html`
- `docs/site/task_queue.html`

Take main initially, then regenerate the site once the source composition is final. Do not cherry-pick generated HTML hunks individually.

## C5 same-line composition findings

There is no direct C5/P2-042 same-line conflict.

P2-042 commit `3784b0a` changed only these `run_campaign.py` regions:

- `ANALYSIS_MANIFEST_NAME` and config-sidecar exclusion;
- `discover_configs()` excluding `analysis_manifest.json`;
- the corresponding exclusion test.

C5 touches reducer-summary fields, not those lines. P2-042 fix commit `12cb4e0` did not touch `run_campaign.py`.

There is a P2-041/P2-042 integration point that must be retained: `load_analysis_manifest()` must use `joulewise.analysis_manifest.validate_analysis_manifest`, while discovery must still exclude both sidecars.

The actual same-line re-derivations are:

- C5 × P2-038:
  - `scripts/run_campaign.assert_production_uncertainty`;
  - `tests/test_p2038_production_path.py`;
  - P2-038 spec/queue acceptance text;
  - restored run-bundle contract wording.
- C5 × P2-040:
  - `joulewise/cli.py` version dispatch and strict field paths;
  - `joulewise/reduce.py`;
  - `joulewise/schemas.py`;
  - `tests/test_cli_run.py`, `tests/test_schemas.py`, and `tests/test_uncertainty_p2029.py`.
  - The resulting `0.4.0` summary must still contain `measurement_quality.runtime_cleanup_ok` and main’s other P2-040 output fields.

## Mechanical vetted-diff recipe

Current `origin/main` was observed at `a1025a2`, a descendant of the requested `3cbe0a7` anchor.

1. Create the reconstruction branch from current main:

```bash
git switch -c impl/p2041-vetted origin/main
```

2. Apply directly from the worktree only these clean files:

```text
docs/run_reports/2026-07-10-p2041-campaign-verdict-split.md
docs/specs/c027/p2-040_reducer_gate_correctness.md
tests/test_analysis_manifest.py
tests/test_uncertainty_p2029.py
```

A mechanical form that includes worktree changes is:

```bash
git -C /Users/edr/code/JouleWise-wt/p2041 diff --binary 3cbe0a7 -- \
  docs/run_reports/2026-07-10-p2041-campaign-verdict-split.md \
  docs/specs/c027/p2-040_reducer_gate_correctness.md \
  tests/test_analysis_manifest.py \
  tests/test_uncertainty_p2029.py |
git apply -3
```

3. Leave every pure-B file above untouched from main.

4. Perform manual hunk composition, always starting from main’s file, for:

```text
RUN_STATE.md
TASK_QUEUE.md
docs/contracts/run_bundle_layout.md
docs/decision_log.md
docs/phase_2/detection_floor.md
docs/specs/c027/analysis_engine_trio.md
docs/specs/c027/p2-038_production_uncertainty_evidence.md
joulewise/cli.py
joulewise/reduce.py
joulewise/schemas.py
scripts/run_campaign.py
tests/test_cli_run.py
tests/test_p2038_production_path.py
tests/test_run_campaign.py
tests/test_schemas.py
```

5. Resolve the three C questions before freezing the wire contract:

- `claim_readiness` or `analysis_readiness`;
- first-run exemption per physical session or once per analysis manifest across resumes;
- whether scoped top-up detection and cooldown trace v2 hardening are approved parts of this landing.

6. Regenerate site files only after source docs are settled.

7. Verify:

```bash
git diff --check
python3 -m unittest \
  tests.test_run_campaign \
  tests.test_analysis_manifest \
  tests.test_p2038_production_path \
  tests.test_uncertainty_evidence \
  tests.test_uncertainty_p2029 \
  tests.test_cli_run \
  tests.test_controller \
  tests.test_reduce \
  tests.test_schemas \
  tests.test_audit_schema_edges \
  tests.test_bundle_read \
  tests.test_clock
python3 -m unittest discover -s tests
rg -n '_window_claim_eligibility|_windows_claim_eligibility' joulewise scripts tests
```

The final `rg` should return no private old helper names. Remaining `claim_eligibility` occurrences should be limited to explicit legacy compatibility or historical documentation.

No files were changed during this audit, and no quiet-Mac measurement was run.