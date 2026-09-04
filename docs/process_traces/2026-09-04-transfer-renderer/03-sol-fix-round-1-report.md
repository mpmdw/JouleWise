# TRANSFER-RESULT-RENDERER-01 — Sol fix round 1

Date: 2026-09-04

Base: `7e8ff8ee01de2b66501a453485e141d02b828f3a` (exact)

Ruling: R3 in `docs/process_traces/2026-09-04-paper-i/06-magistrate-contract-rulings.md`

Inputs: `02-refuter-execution.md`, `02-refuter-contract.md`

## Ruling reconciliation

No refuter finding contradicts R3 or an existing registered contract. CR-02
narrows R3's source binding to the already-registered EXISTING estimator
revision and source digest; this agrees with the TRANSFER-FIDUCIAL-01 kernel
fence that a changed estimator voids the comparison. CR-04 closes a vocabulary
gap that R3 deliberately left as a closed ordered list; it does not replace a
previously registered enum. The capture producer on `d67ee56c` remains
unreviewed and unadopted under R3's fence.

## Finding → cure → evidence

| Finding | Cure | File:line |
|---|---|---|
| Execution F1 / Contract CR-01 — selected witness did not prove the 20-edge maximum or tie-break | Added an authenticated `edge_records` inventory; every interval-plus-anchor composed bound replays; records follow bundle order with falling before rising; the global maximum and first-in-order tie winner must equal the public maximum and selected witness. Regressions cover a larger nonselected edge, bad per-edge arithmetic, missing/duplicate/swapped records, nonwinner selection, and both bundle/edge tie losers. | `joulewise/results_fill_transfer.py:62-76,316-434`; `tests/test_results_fill_transfer.py:225-280`; `tests/fixtures/results_fill_transfer/supported.json:15-174` |
| Execution F2 / Contract CR-03 — complete census plus incomplete reason rendered, while truthful shortfall refused | Registered counts stay 10/20; observed counts may be authenticated shortfalls only on `not_evaluated`; bundle/edge inventory lengths bind to observed counts; run and edge reason codes are iff predicates; incomplete coverage requires null global maximum/witness. Added truthful 9/18 and 10/19 acceptances, false-complete refusal, and combined-shortfall checks. | `joulewise/results_fill_transfer.py:269-313,475-574`; `tests/test_results_fill_transfer.py:370-437`; `tests/fixtures/results_fill_transfer/not_evaluated.json:2-95` |
| Contract CR-02 — arbitrary estimator revision/source digest accepted after reissue | Bound v1 to `joint_loss_sublevel_interval_branch_v2` and SHA-256 `386e8254…bab92`, matching the registered producer constant and current `joulewise/powermetrics_fiducial.py` bytes. Freshly reissued changes now STOP_FILL. | `joulewise/results_fill_transfer.py:44-47,203-221`; `tests/test_results_fill_transfer.py:215-223` |
| Contract CR-04 — reason vocabulary/semantics existed only in implementation | Registered the exact four-code ordered enum and reason-to-field invariants in TR-01, then made the validator and acceptance test consume that closed contract. No number or reason is inferred/defaulted. | `docs/paper/results-fill-registry.md:923-950`; `joulewise/results_fill_transfer.py:49-56,437-451`; `tests/test_results_fill_transfer.py:103-116,339-437` |

## Counterfactual red → green

Red, replayed against the pre-fix implementation using the execution refuter's
embedded counterfactual:

```text
COUNTEREXAMPLE same_capture_tie_bundle_retarget=accepted
COUNTEREXAMPLE same_capture_tie_edge_retarget=accepted
COUNTEREXAMPLE false_complete_census_with_incomplete_reason=accepted
COUNTEREXAMPLE actual_incomplete_census_refusal=STOP_FILL
```

Red, CR-02 freshly reissued mutation:

```text
arbitrary_estimator_errors= []
```

Red, CR-04 registry inspection at `HEAD`: no registered reason-code or
estimator literal matched.

Green, fixture-shaped in-memory replay after the cure (the same cases are
permanent assertions in `test_transfer_result_contract_table`):

```text
COUNTERFACTUAL nonselected_larger=STOP_FILL
COUNTERFACTUAL tie_bundle_retarget=STOP_FILL
COUNTERFACTUAL tie_edge_retarget=STOP_FILL
COUNTERFACTUAL false_complete_census=STOP_FILL
COUNTERFACTUAL truthful_run_shortfall=accepted
COUNTERFACTUAL truthful_edge_shortfall=accepted
COUNTERFACTUAL changed_estimator=STOP_FILL
COUNTERFACTUAL changed_estimator_digest=STOP_FILL
```

Green, CR-04 registry inspection now finds the exact estimator identity at
lines 932–936 and exact reason enum/semantics at lines 938–950.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_transfer`
  — `Ran 1 test in 0.026s`, `OK`.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_powermetrics_fiducial.ActiveCaptureMethodTests.test_capture_clock_dispatch_emits_active_schema_and_tracks_registry tests.test_powermetrics_fiducial.EvidenceTests.test_valid_evidence_carries_bindings_and_bound tests.test_powermetrics_fiducial.FrozenProtocolTests.test_estimator_byte_drift_refuses_acceptance_as_stale`
  — `Ran 3 tests in 0.511s`, `OK`.
- `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint`
  — `Ran 13 tests in 2.728s`, `OK`.
- `git diff --check -- joulewise/results_fill_transfer.py tests/test_results_fill_transfer.py tests/fixtures/results_fill_transfer docs/paper/results-fill-registry.md`
  — exit 0, no output.

The canonical discovery suite was intentionally not run: the prompt's
PREFLIGHT RULE restricts this fix round to the renderer test, the named
validator/producer checks, and the two registry tests. An initial whole-module
validator invocation returned only partial progress output without a usable
exit status; it is not counted above, and the three ruling-relevant named tests
were rerun cleanly.

## Residual risk

This remains fixture-only. It proves the adopted public projection/renderer
contract but does not accept, run, or validate the unreviewed capture producer
at `d67ee56c`, and it issues no measurement value or claim.
