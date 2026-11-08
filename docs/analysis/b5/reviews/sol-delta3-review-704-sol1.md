# Sol delta-3 review of PR #704 — seat sol1

Date: 2026-11-08 PST. Branch: `b5rel/2026-11-08-sol-delta3-704-sol1`.
Reviewed: `131369801..c41ee4b09984c49a1e4f929ca00b6bd17f8a8a21`.
The tree started clean on the requested review branch. The task brief's four
lead dispositions govern this review. Both prior delta-2 reports were read
from the supplied `origin/b5rel/2026-11-08-sol-delta2-704-sol{1,2}` Git refs;
no network lookup was used.

## Verdict: ADMIT

No blocking finding in the reviewed delta. The unprinted-bound shortcut is
removed, every applicable within-bar form has an explicit undetermined row,
and comparator refusal outranks both disagreement and undetermined holds.
The inherited transport-usability proxy and legitimate permanent holds are
now disclosed accurately in DLE-5. All 127 targeted tests pass, with no skips
or expected failures. The eight new seat-sol1 witnesses are ordinary tests.

This verdict admits this comparator/release delta under the stated
dispositions. It supplies no evidence about actual Block-5 outcomes and no
unseal, publication, merge, or real-data execution authority.

## Disposition verification

1. **Inside the bar always holds; outside uses strict `>`.**
   `scripts/compare_b5_recompute.py:2211` retains the existing applicability
   conditions: a registered/allowed cell, a computed form with complete terms,
   and some nonzero admissible width. For each such form inside the inclusive
   `floor_j` bar, its derived state is `None`; printed diagnostic identity no
   longer decides it. `compare_point_diagnostics` records the form at the
   floor, claim evaluation, and applicable resolution scopes. `limit_undetermined`
   collects those keys, and CLI exit 0 requires the list to be empty.

   Both delta-2 seats' unprinted-bound/equality witnesses pass. The new
   `BarEndpointTests` uses the actual coded bars and a synthetic threshold of
   1,000,000 J, whose relative bar is exactly 1 J. It tests both exactly
   representable endpoints, equality, and the immediately adjacent binary64
   values outside the band, with and without printed diagnostics, on both
   forms of both decode cells. Endpoints produce four undetermined rows;
   the adjacent outside values are decided by strict `>`. The complete
   comparator probe with one uncertain form and three decisively limited
   forms records exactly its three scope keys and exits 1, despite all
   numeric rows agreeing. A wrong diagnostic number still fails and refuses
   through coverage; uncertainty does not conceal it.

2. **Exit precedence is refused (2), hold (1), agree (0).**
   Comparator `main` checks nonfinite/unmapped/absent coverage before its
   final disagreement/undetermined exit selection. Release
   `scripts/release_b5.py:408` now rejects any process status outside `{0, 1}`
   before classifying its summary as a semantic hold. The existing release
   witnesses exercise a real comparator exit 2 with family failures and
   preserve `comparator_refused`, release exit 2, and family counts.

   The new `ReleaseWitnesses` additionally runs the real comparator on four
   synthetic release-harness cases: agreement → 0; uncertainty alone → 1 /
   `within_bar_undetermined`; uncertainty plus a family disagreement → 1 /
   `comparator_disagreement`; uncertainty plus an unmapped disagreeing copy
   → 2 / `comparator_refused`. A separate mocked process/output matrix tests
   exit 2, signal status -15, and exit 70, each with/without family failures
   and undetermined rows: all remain refusals. These injected summaries test
   consistency handling; they are not asserted to be normal CLI outputs.
   Unreadable/vacuous output also remains a refusal via the earlier guards.

3. **Usability proxy is retained as a disclosed inherited limit.**
   `usable_arms` still uses a finite independent source-cell gate; it does not
   derive consumer transport eligibility. DLE-5's “Inherited limit” paragraph
   states that distinction, the absence of transport status in recompute
   output, its fail-closed consequence, and the registered `exact_stack_only`
   route's narrower scope. The sealed contrast manifest and plan §5 still
   specify that route; the producer's successfully bound request path supplies
   empty consumer stress (`joulewise/analysis_engine/inputs.py:4899`).

   Both delta-2 modules' actual-resolver transport probes pass. The new
   `test_transport_proxy_limit_already_has_numeric_disagreement` uses the
   existing pure fixture builder: the real resolver refuses consumer power
   outside its envelope while the source gate stays finite. Aggregate
   metadata is correctly absent; the proxy expects it and disagrees.
   Independently, null-vs-finite resolution-number rows already disagree.
   This is a disclosed limitation on general transport, not a demonstrated
   new false refusal on successfully bound registered Block-5 custody.
   Printed refusal statuses are not newly trusted to suppress checks.

4. **Legitimate permanent holds are disclosed.**
   DLE-5's “Disclosed consequence” paragraph states that correct nonlimited
   output at or just under the threshold can hold even when all numbers
   agree, immutable reruns cannot clear it, structural equality is possible,
   and there is no liveness guarantee. The new actual-estimator probe uses
   ten comparative synthetic values `[2, .01, ..., .01]` and widths
   `[0, .5, ..., .5]`: the zero-width maximum fixes the strict-test equality
   despite other positive widths. The actual producer is nonlimited, the
   real combined-floor function emits no diagnostics, and two identical
   comparisons record the same four undetermined aggregate rows with no
   failed rows. This intentional hold has no mechanical override here.
   Its real-data frequency is unknown; no probability is inferred from the
   bar's narrow width.

## Independence

`scripts/independent_recompute_b5.py` has no diff in the review range and its
SHA-256 is exactly:

`d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0`.

Direct hashing and the new independence witness agree. AST inspection of
that script and the comparator finds only absolute stdlib imports, no
`joulewise` import, and no calls to `exec`, `eval`, or `__import__`. Test
code deliberately imports the actual producer APIs to check their behavior;
the independently pinned recompute script is unchanged.

## Verification

Each unittest module ran **sequentially in its own process**, using:

```sh
JW_B5_SYNTHETIC_ONLY=1 nice -n 10 python3.13 -B -m unittest tests.independent_recompute.<module>
```

| Module | Tests | Result | Seconds |
|---|---:|---|---:|
| `test_floor_limit` | 37 | pass | 15.802 |
| `test_release_b5` | 31 | pass | 9.651 |
| `test_sol_delta_review_704` | 21 | pass | 167.059 |
| `test_sol_delta2_review_704_sol1` | 7 | pass | 2.531 |
| `test_sol_delta2_review_704_sol2` | 10 | pass | 0.484 |
| `test_sol_delta3_review_704_sol1` | 8 | pass | 3.396 |
| `test_rc_cmp11` | 13 | pass | 13.189 |
| **Total** | **127** | **pass** | **212.112** |

The wrapper prints `nice: setpriority: Operation not permitted`; Python
continues, so the requested wrapper was used but its priority change was
not enforced. Total unittest execution was about 3.5 minutes. Full/sharded
suite execution was intentionally excluded by the task's machine-load rule.
Focused source compilation and `git diff --check` pass.

Release-harness agreement cases mock the recompute output because their
small synthetic custody is shaped for comparator checks; custody verification
and comparator execution are real. The existing release module also exercises
the actual recompute on synthetic archives and expects a held verdict. These
are engineering witnesses, not live hardware or authenticated study evidence.

Python 3.11 was not run; lead/CI verification remains due for that interpreter.
No MLX code changed and this delta requires no new native Metal test.

## Handoff

Changed files: the new seat-sol1 witness module, this review report, and the
dated run-report pointer. Production code, coordination files, state kernel,
sealed artifacts, and prior witnesses were preserved. No nested seat was
launched. The session did not execute the Block-5 analysis pipeline, read real
measurement custody, use the network, download weights, run hardware
measurements, push, or inspect the running analysis job.

No unresolved blocking question or requested production fix. Remaining
uncertainty is the actual sealed data's agreement/boundary state and the
broader inherited comparator limitations already recorded in DLE-5 and the
coverage audit; this bounded review does not establish their absence.

Next exact step: the lead reviews/cherry-picks this local review commit,
adjudicates both independent delta-3 seat reports, and owns the separate
blinded release check. Any undetermined row remains held; Ed's explicit
unseal OK is still required before outcomes are opened.
