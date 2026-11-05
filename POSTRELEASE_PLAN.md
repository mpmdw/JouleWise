# Block-5 post-release fixes

Base: cached `origin/main` (`92026c1849c0f053e56bdac6110c079211db2c31`).
Branch: `lane/2026-11-05-b5-post-release-fixes`. Preparation only; do not
merge or use for the release analysis. No measurement data is needed.
Authority: D-178, D-188–D-190 and
`docs/process_traces/2026-11-04-d188-retrospective/RETROSPECTIVE.md:78`.
Line references below identify the base unless stated otherwise.

## a. Step-4 parallel exception cleanup — IMPLEMENT

- What/where: `joulewise/b5_analysis/dry_run.py:1138–1171`,
  `_step_4_parallel`. Only a later `AnalysisRefusal` during reauthentication
  cleans up speculative child files; exceptions during output registration,
  token reading or classification leave later outputs/logs and the advanced
  log counter behind.
- Why: those later children would never have run serially. Their files must
  not remain attached to an interrupted prefix.
- Fix: on any exception during ordered consumption, discard children after
  the last consumed one and restore the counter, then propagate the original
  exception. Retain the current child's files and account only the consumed
  prefix. Dispatch failures without returned results remain a separate limit.
- Test: synthetic child results and fault injection at registration,
  classification and the next child's reauthentication, including a
  `BaseException`; verify surviving files, counter and deadline observations.
- Semantics: custody cleanup only; extraction and classification stay intact.
- Verification: `python3 -m unittest tests.b5_analysis.test_postrelease_step4 -q`
  passed (5 tests; no processes spawned). Pytest is unavailable in both
  installed Python versions; no packages were installed or downloaded.
