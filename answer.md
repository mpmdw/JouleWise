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
