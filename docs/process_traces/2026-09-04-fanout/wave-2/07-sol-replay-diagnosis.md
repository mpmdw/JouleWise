# Wave-2 replay diagnosis at `8222b114`

Date: 2026-09-04  
Seat: Sol, diagnosis + mechanical integration fix  
Requested tree: detached `8222b114f1b20b600d6b1680a9f8773feca7069f`

## Scope and method

The worktree was clean at intake. No full discovery was run. Each supplied
failing module was run alone with `python3 -m unittest tests.<module>`, in the
requested order-independent process shape. The literal history query was also
run:

```text
$ git log --no-merges --oneline origin/main..HEAD -- joulewise/whole_window.py tests/test_analysis_finalizer.py scripts/run_campaign.py
a2e88e02 fan-out CUSTODY-HARDEN-01: fix round 1 against the second-round refuter verdict
12ce38d3 fan-out CUSTODY-HARDEN-01 landing
```

`origin/main` moved during diagnosis (observed first at `eb3e3d85`, then at
`66f36ec2`) after the integration tree was cut; `c74c7e6a` is the integration
tree's mainline merge base (green PR #284). The same two non-merge commits
result when the query is anchored at that merge base. The equivalent
night-file query is empty, and
`git diff --exit-code c74c7e6a..8222b114 -- joulewise/night_gate.py
joulewise/night_plan_writer.py scripts/run_night.py tests/test_run_night.py
tests/test_install_night_agent.py` exits 0.

## Cluster to cause to cure

| Cluster | Isolated baseline | Root cause and classification | Cure | Isolated result |
|---|---:|---|---|---:|
| `test_d165_dominance_closeout` | 40 failures / 47 | Mechanical cross-landing fixture seam: CUSTODY-HARDEN-01 (`12ce38d3`, refined by `a2e88e02`) made NEG-8 file ingress authenticate the registered corpus, while the shared WO-CONSUMPTION-EDGE finalization fixture (`eabe853b`) still minted a self-asserted synthetic corpus. | Bind the shared fixture to the tracked settled-corpus bytes. | 47 OK |
| `test_check_window_provenance` | 25 failures / 35 | Same shared-fixture seam; all failures stopped at `production whole-window writer refused fixture` before provenance assertions. | Same shared cure. | 35 OK |
| `test_bracket_binding_cli` | 19 failures / 19 | Same shared-fixture seam; every CLI fixture failed before its target assertion. | Same shared cure. | 19 OK |
| `test_analysis_finalizer` | 14 failures / 15 | Same shared-fixture seam. | Same cure plus a regression pinning corpus id, condition, exact manifest digest, and ordered member ids. | 16 OK |
| `test_run_night` | 3 errors + 7 failures | Environment/load artifact. The replay executed first-parent v1 `night_gate.py` line 189 (the `PlanError` raise) while traceback linecache displayed merged-v2 line 189 (`measurement_root: str`). The simultaneous `PLAN_SCHEMA_VERSION` import error is the same mixed runtime/source snapshot. The stable tree has no night delta from green PR #284. | No code change; fresh isolated process. | 56 OK |
| `test_analysis_integration` | 6 failures / 116 | Same shared-fixture seam. | Same shared cure. | 116 OK |
| `test_pipeline_smoke_tail` | 4 failures / 4 | Same shared-fixture seam. | Same shared cure. | 4 OK, 1 skipped |
| `test_install_night_agent` discovery import | import error | Same environment/load artifact as `test_run_night`: new `night_plan_writer.py` observed a stale v1 `night_gate` module without `PLAN_SCHEMA_VERSION`. | No code change; fresh isolated process. | 11 OK |

The production boundary is at `joulewise/whole_window.py:1737-1742`; it now
requires corpus identity on file ingress. The repaired fixture is at
`tests/test_analysis_finalizer.py:377-405`, and its regression begins at line
607.

## Revert-in-place bisection

All experiment patches were restored before the fix was applied.

1. Reverse-applying only `a2e88e02`'s `whole_window.py` change left
   `test_analysis_finalizer` at 14 failures / 15. The follow-up did not
   introduce the break.
2. Reverse-applying the complete CUSTODY-HARDEN-01 `whole_window.py` delta
   relative to `c74c7e6a` made the unchanged module pass 15 / 15.
3. Source inspection identifies `12ce38d3` as the introducing landing: it made
   `load_neg8_drift_bound_artifact` call validation with
   `require_corpus_identity=True` but did not migrate the shared fixture.

## Verification tails

```text
$ python3 -m unittest tests.test_d165_dominance_closeout
Ran 47 tests in 9.731s
OK

$ python3 -m unittest tests.test_check_window_provenance
Ran 35 tests in 17.266s
OK

$ python3 -m unittest tests.test_bracket_binding_cli
Ran 19 tests in 16.175s
OK

$ python3 -m unittest tests.test_analysis_finalizer
Ran 16 tests in 21.629s
OK

$ python3 -m unittest tests.test_run_night
Ran 56 tests in 4.777s
OK

$ python3 -m unittest tests.test_analysis_integration
Ran 116 tests in 62.942s
OK

$ python3 -m unittest tests.test_pipeline_smoke_tail
Ran 4 tests in 4.665s
OK (skipped=1)

$ python3 -m unittest tests.test_install_night_agent
Ran 11 tests in 3.105s
OK
```

## Residual replay record

This does not claim a clean 5,016-test replay: the supplied log also contains
one `test_arm_readiness_evidence_t0` error and five
`test_window_status_guard` failures outside the named module set. They were
not run because the preflight rule exhaustively limited test execution to the
eight named modules.
