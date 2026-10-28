VERDICT: ACCEPT_WITH_FIXES

Executing delta review, 2026-10-28: `f059286bc..2ea99f51f03ae38a5f24e2ee8247e18cd4a110f0`.
**Both prior findings are closed; no finding above LOW.** No production edits.
Authority: gate policy and ED-RULING items 1/6 read from `origin/main` (absent at this head); [snapshot](l9-sol-rev-2/authority.log). Seat dispositions read from `origin/lane/2026-10-27-l9-2` as claims to test.

**LOW-1 — Cleanup can rethrow an already-classified observer setup failure.**
`joulewise/b5_analysis/deadline_observer.py:74`.
A real CPython audit hook rejecting `sys.monitoring.register_callback` makes installation raise `RuntimeError`, correctly handled at line 67. Cleanup nevertheless calls the rejected API again. Executed [probe](l9-sol-rev-2/observer_audit_probe.py), with real monitoring APIs and only synthetic dispatch steps:

```text
first_step: tooling_refusal / calibration_deadline_observer_unavailable
later: not_run
exit: uncaught RuntimeError (audit policy denies monitoring callbacks)
tools_after: all free
```

[Output](l9-sol-rev-2/observer-audit.log). Track successful setup and remove only installed callbacks/events. LOW because the classified record exists, no later work runs, and no number/admission changes; this requires an audit policy denying monitoring. It does not block gate-policy rule 4.

**Executed checks of the fixes.**

- **Prior MAJOR-1 closed**, `joulewise/whole_window.py:7110`, `:7137`, `joulewise/cli.py:507`. Reran an unchanged copy of `cache_metadata_probe.py` at this head: differing keys `[]`; gross `max_abs_delta_j` **0.3332955190828386** both ways; strict uncached/shared high-low **0/0**; real step-1 driver control/current both return **0**, step 1 `ok`. Zero deadline firings. Its legacy `assert differences` now fails as expected; this is the old defect assertion, not a failed current regression. [Output](l9-sol-rev-2/cache-metadata-probe.log).
- **Partition attacks passed.** Three bundles share one evidence hash. Their metadata bounds are the fresh bound **0.022708904442849103** and its immediate binary64 neighbors (`…ddda`, `…dddb`, `…dddc` in hexadecimal). Orders `(0,1,2)`, `(2,1,0)`, `(1,2,0)`, each followed by its reverse, preserve every strict result. Each store has three partitions and exactly three real refits. Shared reductions match uncached bytes. Invalid partition values decline sharing. [Probe](l9-sol-rev-2/delta_probes.py), [output](l9-sol-rev-2/boundary-probes.log).
- **Prior MINOR-1 closed**, `joulewise/b5_analysis/deadline_observer.py:43`. Reran `missing_monitoring.py`, adding only record-field printing: missing API and real competing reservation both return **2**, write step-0 `calibration_deadline_observer_unavailable`, and leave later steps `not_run`; competing tool preserved. [Output](l9-sol-rev-2/missing-monitoring.log). Historical printed `f059286bc` labels in both copied scripts mean their imported **current** `d.run`.
- **V2 behavior unchanged against exact `f059286bc` modules loaded from Git.** Two calls per mode, each version: implicit strict cache **19 inputs/88 reads**; explicit strict cache **19/88**; CLI reduce **17/50**. Outputs, reduction digest, every input digest/grammar/`read_count`, and subsequent metadata-change refusals match exactly. A guard forbidding ordinary metadata `read_bytes` admits both versions and kills an injected extra-read counterfactual. Partition selection uses already-read metadata (`cli.py:497`, `whole_window.py:1310`, `:1397`, `:6187`). [Comparison](l9-sol-rev-2/auth-comparison.log), [counterfactual](l9-sol-rev-2/extra-read-counterfactual.log).
- **All four governed `ESTIMATOR_CODE_PATHS` match `0576a734d` byte for byte**, including worktree bytes. [Hashes](l9-sol-rev-2/estimators.log).

**Verification:** requested four-module command **56/56 passed**, 233.325 s, exit 0 ([log](l9-sol-rev-2/targeted-tests.log)). All three selected new regressions fail with exact pre-fix production modules, discriminating cache poisoning, missing API and reservation race ([log](l9-sol-rev-2/counterfactual-tests.log)). `git diff --stat` records 11 files, +577/−328 ([baseline](l9-sol-rev-2/baseline.log)); `git diff --check` passes. Used Python 3.13, `PYTHONDONTWRITEBYTECODE=1`, `JW_B5_SYNTHETIC_ONLY=1`, `TMPDIR=/private/tmp/jwsolreview`. Full suite/full-size dry run not run: this is the requested bounded delta check. Synthetic fixtures only; no hardware validation.

**Scope:** baseline digest verified; HEAD and all 13 inherited dirty files unchanged. Writes only this report and its allowed evidence subtree. Scope helper marks every path `in_scope`, but returns `ATTRIBUTION_INDETERMINATE: no_governing_lease` for the proper subtree scope ([scope check](l9-sol-rev-2/scope-check.json)). The launch lease covers the directory as an exact path, not its descendants. No lease edits made.

**Next exact step:** lead dispositions LOW-1 and reconciles launch-lease subtree coverage, then combines the two family delta reviews and its remaining acceptance evidence. This review does not replace the lead's full-size/live gates.

| gate | ran | caught_number | caught_session_refusal | evidence |
|---|---|---|---|---|
| Sol delta executing review | yes | 0 new | 1 LOW cleanup exception after recorded refusal | observer-audit.log |
