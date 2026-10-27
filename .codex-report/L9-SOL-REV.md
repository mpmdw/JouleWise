VERDICT: REJECT

Executing review, 2026-10-27: `0576a734d..f059286bc4d411008002bac62c5cc76cc8c50026`.
The supplied baseline digest matches. Policy/ruling/brief are absent at the reviewed head; read from local `main` at `64ceaa4f74e1e7914a89c01b15d6a5677cca3853`. No production changes made.

**MAJOR-1 — Shared cache changes no-firing outputs and strict admission.**
`joulewise/cli.py:507`, `joulewise/cli.py:1954`, `joulewise/b5_analysis/dry_run.py:1212`.
The newly shared dictionary caches an *effective* bound that depends on bundle metadata, under a key containing only the calibration evidence hash. The unchanged reducer accepts metadata `b_fiducial_s` within `1e-12` of the artifact (`joulewise/reduce.py:1400`), then caches `max(metadata_bound, fresh_bound)` (`:1590`). Therefore equal artifact hashes do not guarantee interchangeable cached values.

Executed `cache_metadata_probe.py`: copy one synthetic S10 member, increase only its metadata bound by `5e-13`, and regenerate its stored summary through real `reduce`. Both bundles individually pass real strict validation. Seed the shared cache with the higher-bound bundle, then reduce/validate the original:

```text
CLI statuses plain/seed/shared: 0 0 0
wall-deadline firings: 0
strict uncached high/low: 0 0
strict shared high/low: 0 2
gross max_abs_delta_j: 0.3332955190828386 -> 0.333295519090143
```

Three summary sections differ: `energy_anchor_shift_envelopes`, `energy_bound_terms_j`, `window_evidence_precheck`. The real step-1 dispatch also reproduces the regression: baseline `run()` control returns 0 with step 1 `ok`; reviewed `run()` returns 2 with `kept_bundle_strict_validation_failed` and every later step `not_run`. Archive preparation and other steps are explicit stubs in that comparison. Point energies remain unchanged; the byte-identity and admission requirements fail. No claim that real block-5 archives contain this metadata variation.

Evidence: [script](l9-sol-rev/cache_metadata_probe.py), [executed output](l9-sol-rev/cache-metadata-probe.log), [numeric differences](l9-sol-rev/cache-metadata-differences.json). Partition/restrict cross-call reuse using every input to the effective bound; preserve frozen estimator bytes and exact comparisons.

**MINOR-1 — Observer setup failures bypass the classified refusal.**
`joulewise/b5_analysis/deadline_observer.py:38`, `:51`; initialization is outside the step exception handler at `joulewise/b5_analysis/dry_run.py:1213`.
Executed `missing_monitoring.py`:

```text
baseline, missing API: return 0, record_exists=true
reviewed, missing API: AttributeError, record_exists=false
reviewed, tool-ID registration race: ValueError "tool 0 is already in use", record_exists=false
```

The race uses a real competing tool registration scheduled between availability lookup and reservation. Missing-API reproduction deletes only `sys.monitoring` on Python 3.13; Python 3.11 is not installed here, although `pyproject.toml:9` permits it. Handle API absence and reservation failure through `calibration_deadline_observer_unavailable`. Evidence: [script](l9-sol-rev/missing_monitoring.py), [output](l9-sol-rev/missing-monitoring.log). No BLOCKER or NIT findings.

**Required answers.**

- **Can a wall-deadline firing produce an `ok` step with changed outputs? No such escape found on the current synchronous dry-run path.** Forced real 59-pulse detections at all 13 driver boundaries, including 5 and 9b, became `calibration_wall_deadline_fired`; earlier outputs matched and later steps were `not_run`. Thread, nested-observer, swallowed-exception and occupied-tool tests passed. Removing observation admits a changed toy numeric output, proving discrimination. Real site tests cover reduction, NEG-8 strict/energy replay and bracket candidate loading. Reachable strict calls use one worker; the spawned pool is collection-only. See [dispatch log](l9-sol-rev/dispatch-probes.log), [site log](l9-sol-rev/real-site-probes.log), [call-path audit](l9-sol-rev/call-path-audit.log).
- **Does the shared cache change any printed output without a deadline? Yes.** MAJOR-1 changes numeric reduction JSON and strict-validation diagnostics; the driver changes from `ok` to a tooling refusal. The unmodified single-member cold/warm control has identical stdout, stderr and summary bytes, but does not exercise differing metadata bounds.
- **Governed estimator sources are byte-identical to `0576a734d`: confirmed** for all four requested paths, including current worktree bytes. SHA-256 values and diff stat are in [baseline-and-estimators.log](l9-sol-rev/baseline-and-estimators.log).

**Verification.** Python 3.13; all commands below used `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp/jwsolreview JW_B5_SYNTHETIC_ONLY=1`, plus `PYTHONPATH=.` for scripts.

```sh
python3.13 -m unittest -v tests.b5_analysis.test_deadline_observer tests.b5_analysis.test_deadline_tripwire tests.b5_analysis.test_shared_physics_cache tests.b5_analysis.test_bracket tests.b5_analysis.test_frozen_files
python3.13 .codex-report/l9-sol-rev/review_probes.py DispatchProbes
python3.13 .codex-report/l9-sol-rev/review_probes.py RealSiteProbes
python3.13 .codex-report/l9-sol-rev/cache_metadata_probe.py
python3.13 .codex-report/l9-sol-rev/missing_monitoring.py
```

Requested modules: **79/79 passed** (14/7/7/48/3), 525.628 s, exit 0; [log](l9-sol-rev/targeted-tests.log). Independent probes: **8/8 passed**, both reproduction scripts exit 0. Full suite/full-size joined driver were not run: this is the requested bounded executing review, with the full-size run reserved to the lead. Synthetic evidence only; no hardware validation.

Scope verification: `git diff --check` passes; HEAD unchanged; every persistent changed path is inside the supplied allowlist. The bridge helper reports `ATTRIBUTION_INDETERMINATE` (exit 4), solely `no_governing_lease`; all 13 path dispositions are `in_scope`. See [scope-check.json](l9-sol-rev/scope-check.json). No lease records were changed.

Next exact step: lead fixes MAJOR-1 and observer setup handling, runs these discriminating reproducers against the fix, then requests both reviewers' delta checks. MAJOR-1 blocks acceptance. Lead also reconciles the missing launch lease.

| gate | ran | caught_number | caught_session_refusal | evidence |
|---|---|---|---|---|
| Sol executing review | yes | 1 (uncertainty bytes) | 2 (cache admission; observer setup) | two reproductions above |
