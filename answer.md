# ALIGN v4 WP2 + WP3 handoff

Branch: `lane/2026-11-05-align-v4-wp2-657`, based on `c8ef6b2f6`. Local commits only; no push.

Code commits:

- `4c8616da8` — default checkpoint limits to `None`, omit unset identity fields, retain trial fix-up items 4/5.
- `54b8a624d` — move checkpoint prefill into ALIGN's stream observer using an explicit runtime view; restore the complete MLX adapter to `83e2dac59` bytes.

The v3 plan, identity pins, verification receipt, and generator are byte-identical to `83e2dac59`. None of the 42 tracked `align_pilot_v3` files contains `hybrid_checkpoint_limit`. Trial fix-up items 1–3 were unnecessary.

Final selected tests: **201 selected, 191 passed, 10 skipped, zero failures/errors**. Final module runs were sequential. No full suite, network, analysis pipeline, or live measurement was run.

Each module below used `python3.13 -B -m unittest <module>` with the offline Jinja2/MarkupSafe overlay and native opt-ins disabled. Exact environment, the blinded KitTests wrapper, preliminary failures, and logs are documented in the [dated report](docs/run_reports/2026-11-05-align-v4-wp2-wp3.md).

| Module / class | Passed | Skipped |
|---|---:|---:|
| `tests.align.test_cache_checkpoint` | 16 | 0 |
| `tests.align.test_cache_checkpoint_native` | 0 | 5 |
| `tests.align.test_pilot3.KitTests` (blinded wrapper) | 3 | 1 |
| `tests.align.test_pilot3_cache` | 12 | 0 |
| `tests.align.test_pilot4` (includes its KitTests) | 17 | 1 |
| `tests.align.test_decode_budget` | 20 | 1 |
| `tests.align.test_history_rendering` | 7 | 2 |
| `tests.align.test_xml_tool_calls` | 21 | 0 |
| `tests.align.test_measurement_core_boundary` | 4 | 0 |
| `tests.align.test_apple_endpoint` | 9 | 0 |
| `tests.align.test_thermal_gate` | 31 | 0 |
| `tests.test_mlx_runtime` | 43 | 0 |
| `tests.test_mlx_runtime_detokenizer` | 8 | 0 |

`compileall`, `git diff --check`, and `align_pilot_kit.py --check` pass. The four lead-owned coordination files are unchanged.

Files touched: `workload.py`, `endpoint.py`, new `generation.py` under `joulewise/align/apple/`; restored `joulewise/adapters/mlx_runtime.py`; three ALIGN test files; `docs/align/hybrid_cache_checkpoints.md`; this handoff and the dated report.

Lead next steps: run the native checkpoint, MLX deadman, and pinned-tokenizer history gates; obtain the independent Opus executing-review paper and cite it in WP5's `0ba413d40` row. The two external-source kit gates were not exercised here. Native correctness/overhead and production readiness remain PROVISIONAL. No new Ed ruling is requested. Full standalone survey papers outside the allowed tree were not independently inspected; the supplied synthesis, patch, local trial bundle, and in-repo implementation records were used.

---

# WP4b handoff — R0 wall time

Continued `lane/2026-11-05-align-v4-wp4-r0` from `4727f2d01`; local commits only:

- `610bcb228` — `fix(align): fail fast and record R0 phase budgets`.
- The subsequent commit containing this handoff — `docs: record WP4b R0 scheduling verification`.

Implemented canonical order `host,disk,load,template,generated,memory,smc,ladder,long-decode`, including prerequisites and checkpoint receipts. Failed/inconclusive checks save both reports and stop by default; `--keep-going` continues diagnostics while preserving prerequisite/census gates. The model is closed before SMC and lazily reloaded afterward. Check criteria, token budgets, rung bars, SMC profile and per-attempt timeouts are unchanged.

The existing xhigh-first/first-pass and retry-on-failed-verdict behaviors were retained. Skipped D rungs now explicitly say **"not run: higher rung passed"**. Long decode runs once on success; `--long-decode-attempts 1` disables the optional metadata retry (`2` is the default maximum). Existing exception/timeout behavior remains: it fails the check immediately, without a retry. Reports show phase `check_seconds` and run `total_seconds`, including failed/refused phases and backend cleanup in the total.

Runbook budget: **3–4 h expected on all-pass**, unmeasured. A worst-case full-token-budget calculation at 10 decode tok/s is **about 7.3 h plus prefill, inventory and setup overhead**; slower hosts can take longer. There is no total-run deadline or demonstrated speedup here.

Each test module ran separately, one at a time, using exactly `python3.13 -B -m unittest MODULE`:

| Module (`tests.align.` prefix) | Tests | Result |
|---|---:|---|
| `test_r0_scheduling` (new) | 12 | PASS |
| `test_r0_checks` | 28 | PASS |
| `test_r0_host` | 20 | PASS |
| `test_r0_mlx` | 5 | PASS |
| `test_r0_integration` | 3 | PASS |
| `test_r0_progress` | 3 | PASS |
| `test_r0_documentation` | 3 | PASS |
| `test_r0_step` | 12 | PASS |

**86/86 final-module tests passed; 0 failures, 0 skips.** Including baseline/iterative repeats: **181 passing test executions**, under 10 seconds of reported unittest time. Compileall and diff checks passed. `python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans` exited 2: sandbox denied `ps` (`PermissionError`); rows/count are unknown, not a clean census. No full suite, quick-suite expansion, network, real measurement data, analysis pipeline or native test was run.

Lead next step: review/apply `610bcb228` after WP4 on the integration lane, obtain the planned executing review, and run `python -B -m unittest tests.align.test_r0_mlx_native` in the pinned native MLX/Metal venv outside this sandbox. The real SMC profile, unload/reload lifecycle, timing target, Linux/CI and Python 3.11 remain unverified. Any live R0 must be lead-controlled with zero active agents. Re-run the fixture census outside the sandbox. No new Ed/lead policy ruling is requested; existing WP2/WP10/WP11/WP14 gates remain with their owners.

Files: `joulewise/align/r0_runner.py`, `joulewise/align/r0.py`, `tests/align/test_r0_scheduling.py`, `docs/align/r0_desk_runbook.md`, this file and the [WP4b run report](docs/run_reports/2026-11-05-align-v4-wp4b-r0-wall-time.md). The CLI script is a thin delegate to the updated runner and required no separate change. Protected coordination files were preserved. Prior WP4 handoff follows for its historical test evidence.

---

# WP4 handoff — ALIGN v4 R0 (prior run)

Implemented WP4 (a)–(e) on `lane/2026-11-05-align-v4-wp4-r0`, from `c8ef6b2f6`. No push.

Commits:

- `0ab2ad16e5b66a84dd6b10b8715db6b7e9b9f288` — `fix(align): repair R0 policy, inventories, and storage gates`.
- The subsequent commit containing this file (`HEAD` at handoff) — `docs: record WP4 R0 verification and lead handoff`.

Changes:

- Applied the supplied lock-path patch; added an occupied-lock regression.
- Corrected SMC source to `58525031a`; labeled R0's re-ranked choices PROVISIONAL.
- Removed the endpoint's separate effort argument. R0 uses `chat_template_kwargs`; default effort remains omitted. The real R0 session path now has a regression proving effort changes its hashed identity policy.
- Inventories hash resolved HF snapshot blobs within the hub root, retaining snapshot-relative filenames. Escapes, directory links, loops, missing blobs and restricted components refuse. No model copy.
- R0 disk results are diagnostic-only and never inspect W1 offloads. Added `w1_disk_gate` for the 80 GB post-R0 floor and every configured offload hash; labels are config-driven. Updated Markdown, runbook and example config.

Verification used this prefix, with modules run individually, one at a time:

```sh
TMPDIR=/private/tmp/jwsol/v4-wp4/tmp JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest MODULE
```

| Module (`tests.align.` prefix) | Tests | Result |
|---|---:|---|
| `test_r0_checks` | 28 | PASS |
| `test_r0_host` | 20 | PASS |
| `test_r0_mlx` | 5 | PASS |
| `test_r0_integration` | 3 | PASS |
| `test_r0_progress` | 3 | PASS |
| `test_r0_documentation` | 3 | PASS |
| `test_r0_step` | 12 | PASS |
| `test_apple_endpoint` | 9 | PASS |
| `test_xml_tool_calls` | 21 | 14 passed, 7 skipped (Jinja2 absent) |
| `test_r0_mlx_native` | 1 | 1 skipped (MLX absent) |
| `test_history_rendering` | 9 | 5 passed, 1 pre-existing failure, 3 skipped |

Required WP4 modules: **74/74 passed, no skips**. Across all final module results: 114 distinct tests, 102 passed, 1 failed, 11 skipped. Earlier iterative passes (excluded from that tally): checks 27, host 20, integration 3, documentation 3. The 66 GB/no-offloads completion test mocks host, SMC and native construction; it is not live evidence. The existing injected-backend test still refuses to claim live completion.

The history failure is `test_implicit_xml_history_is_recorded_and_legacy_json_identity_stays_unset`: the existing default contributes `execution_policy: {hybrid_checkpoint_limit: 0}`. Reproduced on a code-only archive of untouched `c8ef6b2f6` under `/private/tmp/jwsol/v4-wp4/baseline`: 9 tests, the same 1 failure and 3 skips. WP2 owns the None/default fix; no WP2 files were changed here.

Also passed: `python3.13 -m compileall -q joulewise tests`, `git diff --check`, example-config validation, and resolved-TMPDIR verification. No full suite, network, measurement-data access, analysis pipeline or live capture was run.

Lead follow-up / uncertainties:

- Apply after WP2/WP3, obtain the planned Opus executing review, and rerun targeted integration checks. CI/Linux/Python 3.11 remain unverified here.
- Outside the sandbox, run `python -B -m unittest tests.align.test_r0_mlx_native` in the pinned MLX/Metal venv. Run the skipped real-template tests with Jinja2 and the history native gates with `JW_ALIGN_NATIVE_TESTS=1` plus the lead's local `JW_ALIGN_QWEN38_MODEL`. Live SMC checks require a clean, lead-controlled session; no native qualification is claimed.
- W1's arm caller must consume `w1_disk_gate(validated_config)` and reject a failing result. This implements the inherited 80 GB storage floor and configured receipts, not W1's complete sizing/authorization workflow. An empty offload list requests no receipt checks; the lead/Ed owns the actual offload plan.
- WP10/WP11 still own the headless launcher/fence and final launch instructions. WP14 owns sensor-policy reconciliation; current selections remain PROVISIONAL. No new Ed ruling is requested by this implementation.

Changed files and intake details: [dated run report](docs/run_reports/2026-11-05-align-v4-wp4-r0.md). Coordination state was preserved as instructed.

---

# ALIGN v4 WP5b: b6 review rows

The three review papers and rows are committed. **Five-module verification is
incomplete**: 19 tests passed, 1 was interrupted at the time cap, and 23 did not
start; no assertion failures were reported.

## Changes and commits

Continued `lane/2026-11-05-align-v4-wp5-b6` from `4344a1174`.
Implementation commit: `3bf81ba5312482c9bd64aa14937ad065175ee8a1`
(`docs(b6): record three retroactive ALIGN runtime reviews`).
The final report-only commit follows it on this branch; its hash is in the
final delivery message and Git history. Nothing was pushed.

Files changed in WP5b:

- `configs/b6/executing_reviews.json`: appended exactly three retroactive rows
  from the papers' section 5, preserving all 53 prior rows and the schema.
  Each cites the committed paper and its SHA-256 in `covered`.
- `docs/align/reviews/2026-11-05-retro-executing-review-dc2204dba.md`
- `docs/align/reviews/2026-11-05-retro-executing-review-b29c25c59.md`
- `docs/align/reviews/2026-11-05-retro-executing-review-0ba413d40.md`
  (all three copied byte for byte from the supplied `/private/tmp` papers).
- `tests/b6/test_audit_record_fixes.py`: retained text-only historical archive
  citations and added repository-paper existence, containment and digest
  validation. Append-only, uniqueness and HEAD history coverage checks remain.
- `answer.md` and
  `docs/run_reports/2026-11-05-align-v4-wp5b-b6-review-rows.md`: handoff evidence.

`git merge-base --is-ancestor 0ba413d40 HEAD` passed. The commit is in this
branch through integration `c8ef6b2f6` / the #657 merge. The first two papers
are ADMIT. `0ba413d40` is **ADMIT_WITH_FIXES, admitted for limit None/0 only**:
F2 must be fixed and E4 rerun before any limit > 0 cell. Recording a row does
not enforce that runtime condition.

## Verification

The two attempted modules used this exact prefix, sequentially in the table's
order:

```sh
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5b/tmp python3.13 -B -m unittest -v <module>
```

| Module | Passed | Failed | Skipped | Interrupted | Not started | Result / elapsed |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `tests.b6.test_audit_record_fixes` | 8 | 0 | 0 | 0 | 0 | exit 0; wrapper 76.413 s; unittest 75.842 s |
| `tests.b6.test_cold_pass_fixes` | 11 | 0 | 0 | 1 | 2 | exit -2; budget timeout; wrapper 1114.800 s; no final unittest timer |
| `tests.b6.test_loop_round_desk` | 0 | 0 | 0 | 0 | 6 | not started; not run |
| `tests.b6.test_desk_resume_finalize` | 0 | 0 | 0 | 0 | 6 | not started; not run |
| `tests.b6.test_capture_screen_reachability` | 0 | 0 | 0 | 0 | 9 | not started; not run |

Totals: 19 passed, 0 failed, 0 skipped, 1 interrupted, 23 not started.
Sequential wrapper wall time: **1191.213 s**. The 1,190 s cap interrupted its own test process group. A partially completed test or subtest is not counted as passed. The five-module acceptance is incomplete.

Additional checks passed: `git diff --check`; all three source/copy byte and
SHA-256 comparisons; append-only/schema/unique-commit checks; and:

```sh
env PYTHONPYCACHEPREFIX=/private/tmp/jwsol/v4-wp5b/tmp/pycache python3.13 -m compileall -q joulewise tests
```

## Limits, risks and next step

The full five-module acceptance is still open because the standing test-time
cap was reached. The gamma test was interrupted;
these two cold-pass tests never started:

- `FullRoundTests.test_lost_start_reference_without_spare_counts`
- `FullRoundTests.test_physical_and_opening_no_bound_stops_rotate`

The interrupted case was
`FullRoundTests.test_gamma_lost_midpoint_counts_and_overrides_b5_claim`.
The other three modules have 21 tests not started. Earlier part-1 results are
historical evidence and are not counted as fresh WP5b passes.

Next exact step: the lead reviews the implementation commit, then runs the
four incomplete/unrun modules sequentially in a sufficiently long authorized
test window before claiming the WP5 acceptance gate is green:

```sh
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5b/tmp python3.13 -B -m unittest -v tests.b6.test_cold_pass_fixes
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5b/tmp python3.13 -B -m unittest -v tests.b6.test_loop_round_desk
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5b/tmp python3.13 -B -m unittest -v tests.b6.test_desk_resume_finalize
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5b/tmp python3.13 -B -m unittest -v tests.b6.test_capture_screen_reachability
```

The full suite was forbidden by the machine-load rule. No native MLX test was
attempted or counted as a skip. The papers' native results are supplied review
evidence, not independently reproduced here. The lead's WP3/WP6 native gate
includes:

```sh
JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_cache_checkpoint_native
```

The lead must retain limit None/0 or close F2 before any positive-limit cell.
Optional hardening findings remain documented in the papers. The WP14 commit
`a17ed96c8` is not locally available, so copies were checked against the supplied
source files, not that commit. The original archive citations were treated only
as text. The copied 0ba paper retains its author's process note about an
upstream archive listing; any disposition of that note remains lead-owned.
No new Ed ruling is requested for these record changes.

No network, real measurement inputs, block-5 pipeline, or live capture was
used. The four protected coordination files were unchanged. The part-1 dated
report is unchanged; the earlier detailed `answer.md` remains available via
`git show 4344a1174:answer.md`.

---

# WP16 handoff — ALIGN v4 kit skeleton

Branch: `lane/2026-11-05-align-v4-wp16-kit`, from `c8ef6b2f6`.
Implementation commit: `edac8cc7a50494f414fae4625713d246718500d1`
(`Build fail-closed ALIGN v4 W1 kit skeleton and acceptance tests`). This
handoff and the dated run report are committed separately. Nothing pushed.

Implemented the 18-member A1 roster, independent seed/turn-seed witnesses,
ABBA/BAAB position and predecessor balance, midpoint after ordinal 9, pinned
pilot-7 contrast sources, and prospective fit-rule helper. All four original
anchor configs are byte-identical to `83e2dac59`, including their run IDs.
D configs carry the required sampler/history/family/XML selection, explicit
checkpoint zero, neutral warmup, heavy/G1/hold policy shape and pending limits.
Added kit/pack/schema parameters to the shared session runner and a guarded
v4 wrapper. V3 generator and committed kit bytes remain unchanged.

Files: `scripts/align_v4_kit.py`, `scripts/align_v4_session.py`,
`scripts/align_pilot_session.py`, `tests/align/test_v4_kit.py`, and the committed
kit under `configs/campaigns/align_v4/`. Detailed evidence and limitations:
`docs/run_reports/2026-11-05-align-v4-wp16-kit.md`.

## Verification

Each unittest command ran alone, with `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp`.

| Exact command | Final result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_v4_kit` | **31 tests, 31 passed**, 5.047 s |
| `python3.13 -B -m unittest tests.test_align_pilot_session` | **15 tests: 14 passed, 1 failed**, 134.689 s |
| `JW_ALIGN_NATIVE_TESTS=0 python3.13 -B -m unittest tests.align.test_history_rendering` | **9 tests: 5 passed, 1 failed, 3 skipped**, 0.064 s |
| `python3.13 -B -m unittest tests.align.test_xml_tool_calls.XmlToolCallTests` | **14 tests, 14 passed**, 0.027 s |
| `python3.13 -B -m compileall -q joulewise tests scripts/align_v4_kit.py scripts/align_v4_session.py scripts/align_pilot_session.py` | Exit 0 |
| `python3.13 -B scripts/align_v4_kit.py` | Exit 0, generated skeleton |
| `python3.13 -B scripts/align_v4_kit.py --check` | **Expected exit 1**, names pending WP11/WP18/R0/R1/WP15 inputs |
| `git diff --check` / `git diff --cached --check` | Exit 0 |

Both legacy failures are in unchanged code: the supplied integration base
serializes `hybrid_checkpoint_limit: 0` on legacy paths. They are the WP2
default-None repair, not fixed here. History skips: one optional-Jinja2 test
and two native tokenizer/MLX tests. Two development runs of the new tests
found timing-fixture errors; both were corrected before the final 31/31 run.
All unittest attempts together took about 161.5 s. No full suite was run.

## Blockers, uncertainty and next step

This is an intentionally unarmable skeleton. WP11 D identity pins/inventory/
verification and WP18 historical X/Y max_turns/fixture digests are null.
R0 effort and R1 budget/intercept/deadman/thermal slots are also null. The
placeholder test proves `--check`, prepare and install refuse them; no model
or measurement path was followed. There is no arm-compatible `sizing_b5.json`.

The window-plan draft at `40c569cfd` chooses D index **101**. Synthesized WP16
and A1 instead require **1**, with development **91–93** and held-out from **2**;
implemented the latter. A1's conditional checkpoint enablement is superseded
by the synthesized ruling: D stays explicitly **0** throughout the series.
No new Ed ruling is requested for this skeleton.

Lead next: review/cherry-pick the implementation onto the repaired integration
lane, obtain the non-author Opus review, and rerun the legacy modules after
WP2. WP15 must implement the launcher and member-5 reference custody; its
input field is only a placeholder, not runtime wiring. WP17 must consume R1
evidence, apply/requalify any fit-rule changes and generate real sizing. The
builder currently emits the full 18-member skeleton; the fit helper returns
prospective ordinals/budget, not a silently changed committed roster. WP21
still owns the complete v4 desk. Merely replacing nulls is not arm admission.

MLX/Metal, real tokenizer IDs, historical token replay, holds, sensor selection,
and local D identity authentication were **not validated** here. Lead must run
the pinned-stack native history, checkpoint, thermal/lookahead and R0 memory
modules outside the sandbox, one at a time; SMC and R0/R1 hardware gates need
the clean measurement Mac. Exact command pointers are in the dated report.
