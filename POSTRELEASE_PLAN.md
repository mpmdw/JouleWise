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

## b. Eager whole-window deadline accounting — NEEDS-LEAD (plan only)

- What/where: `joulewise/whole_window.py:2159–2190` calls
  `member_map` with default `account=True`, then consumes the results;
  `joulewise/analysis_member_pool.py:466–579` reports the entire batch before
  consumption. The compatibility rule is explicit at
  `joulewise/analysis_member_pool.py:68–73` and
  `tests/b5_analysis/test_vdl_sol_hunt.py:209–235`.
- Why: an unconsumed worker's deadline firing or unavailable observer can
  replace an earlier authentication refusal. The lead retained that r1
  behavior for r2 equivalence. Correcting it changes refusal decisions or
  ordering protected by D-188; no production or existing test change here.
- Proposed fix: at this whole-window call site use `member_map(...,
  account=False)` and `consume(..., account=True)` at each dominated
  member's serial position. Account the current consumed outcome even when
  read-census replay raises; never account a later, unconsumed outcome.
  Keep idempotent reporting, poison rules, and the defect side channel.
  Do not change the pool's default globally or mutate historical records.
- Proposed tests: first-member census refusal followed by (separately) a
  deadline-firing and an observer-unavailable worker; neither later outcome
  changes the first refusal, observation count or physics/store state.
  A consumed firing still counts once; a consumed unavailable observer
  still fails closed. Exercise the real whole-window caller and compare
  serial and pooled results on synthetic bundles.
- Ruling needed: authorize consumption-based accounting for a named future
  analysis version, with the refusal-order deviation disclosed, or retain
  eager accounting. Recommendation: consumption-based accounting after
  release, under a successor ruling to D-188. Blocked work: code and tests
  that would replace the explicitly retained compatibility policy.

## c. L3 entries on temporary bracket copies — IMPLEMENT (cache lifetime)

- What/where: `joulewise/b5_analysis/bracket.py:468` destroys the copied
  member tree after evaluation, but nested strict validation can leave
  `L3_reduce_dict` entries in the run store. That leaf is intentionally
  path-bound (`joulewise/analysis_verified_store.py:1225`); those entries
  cannot be reused on the next copy and can be exported after deletion.
- Why: retaining dead entries grows the store without avoiding work.
  Making all L3 entries path-free would be unsafe: failure text can contain
  the caller's path (`tests/b5_analysis/test_vdl_sol_hunt3.py:338`).
- Fix: evict only path-bound L3 entries rooted in this private member tree
  as the tree's context exits, including exceptional exits. Preserve L1/L4
  content-based entries, ordinary L3 entries, counters, defects and poison.
- Test: synthetic store entries in a temporary member tree, a sibling
  with the same name prefix and an ordinary tree; check exit and exception
  cleanup, export omission, and preservation of other leaves and poison.
- Semantics: cache retention only. No key, reduced value or decision changes.
- Verification: `python3 -m unittest tests.b5_analysis.test_postrelease_bracket_copies -q`
  passed (2 tests; no worker pool or bundle reads).

## d. Bracket bypass snapshot hardening — IMPLEMENT

- What/where: `joulewise/b5_analysis/bracket.py:278–309` normalizes
  `ledger_snapshot.ledger_path` before handing arguments to the store.
  `joulewise/analysis_verified_store.py:1675–1690` can bypass the store and
  call the supplied function with those normalized arguments. The existing
  `tests/b5_analysis/test_leaf_bracket.py:298` records this behavior.
- Why: key normalization should not alter arguments observed by a bypass,
  including a wrapped callable or disabled store. The genuine frozen leaf
  does not read that field; the existing test pins this assumption.
- Fix: project this single scalar field only while encoding L4's key,
  including the post-fill scalar check. Always execute the callable with
  the caller's original snapshot. Remove normalization from the wrapper.
- Test: synthetic snapshots and wrapped callables, store absent/off/on,
  rejected and non-servable hits, and normalized-key equality across
  distinct temporary parent paths. Other snapshot fields still change the
  key; the original snapshot identity reaches fallback calls unchanged.
- Semantics: same L4 key and frozen callable behavior; bypass arguments are
  hardened. No ledger contents or numeric quantities change.
- Verification: `python3 -m unittest tests.b5_analysis.test_postrelease_bracket_snapshot -q`
  passed (5 tests, synthetic scalar snapshots; no processes spawned).
