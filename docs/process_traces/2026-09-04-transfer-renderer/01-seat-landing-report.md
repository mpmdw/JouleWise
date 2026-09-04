# TRANSFER-RESULT-RENDERER-01 landing report

Date: 2026-09-04

Seat: Sol xhigh implementation

Branch: `feat/2026-09-04-transfer-result-renderer`

Exact starting HEAD: `85b75cf21297af016d402625be0c4ed0857f412a`

Disposition: complete; no commit requested or made

## Change

The seat defines the closed, content-addressed
`joulewise.transfer_fiducial_result.v1` projection and a fail-closed TR-01
renderer. The renderer accepts exact issued bytes plus an independently
authenticated raw-file SHA-256; it deliberately has no caller-authored object
channel. It validates the empty-ID `tfr-` content identifier, every source and
bundle binding, the exact ten-run/twenty-edge census, the selected raw interval
and anchor replay, the `b_fiducial_s` pulse-bound source, outcome arithmetic,
closed ordered refusal reasons, and the diagnostic/non-claim flags. Any
failure returns `STOP_FILL` at all nine sites.

The three hand-built JSON fixtures are synthetic protocol arithmetic only.
They issue no measurement value or claim and contain no bytes imported from
the unreviewed capture branch. The registry amendment changes only TR-01: it
names the new token, public fields, raw witness/source binding, exact three
sentence templates, nine-copy rule, and continuing `VALUE_UNISSUED` state.

## Field → row → string mapping

| Authenticated issued field(s) | Registry row / token | String effect |
|---|---|---|
| Raw result SHA-256 and `result_id` | TR-01 / `[TRANSFER_FIDUCIAL_RESULT]` | Admit the projection; mismatch yields `STOP_FILL` at every site. |
| `source_capture` digests, commits, estimator revision, ten ordered bundle digests; `census` | TR-01 admission | Authenticate the reviewed-source projection and exact 10-run/20-edge coverage; never printed. |
| `largest_inserted_gap_edge.fitted_residual_interval_s`, `effective_clock_anchor_bound_s`, `largest_composed_edge_residual_bound_s` | TR-01 `<R>` | Replay `max(abs(lower), abs(upper)) + anchor`; print the authenticated public maximum to six decimals only for comparable outcomes. |
| `source_capture.pulse_derived_timing_bound_source.{field,artifact_sha256}` and `pulse_derived_timing_bound_s` | TR-01 `<B>` | Require source field `b_fiducial_s`; print the authenticated public bound to six decimals only for comparable outcomes. |
| `support_outcome=supported` with empty reasons and `R <= B` | TR-01 supported template | Exact `Diagnostic only: ... no greater than ... supports ... but ... does not mint a floor or license a claim.` sentence. |
| `support_outcome=not_supported` with empty reasons and `R > B` | TR-01 not-supported template | Exact `Diagnostic only: ... exceeding ... does not support ... and does not mint a floor or license a claim.` sentence. |
| `support_outcome=not_evaluated` and ordered `reason_codes` | TR-01 refusal template | Exact `Diagnostic only: ... not evaluated (issued reasons: ...); ... remains unestablished.` sentence. |
| `diagnostic=true`, `claim_bearing=false` | TR-01 admission | Mandatory non-claim fence; neither flag is caller prose. |

The selected sentence maps byte-for-byte to, in order:
`abstract.{outcome_a,outcome_b,refusal}`,
`section_7.{outcome_a,outcome_b,refusal}`, and
`section_10.{outcome_a,outcome_b,refusal}`.

## Red-then-green and verification tails

The acceptance module first ran before the production module existed:

```text
$ python3 -m unittest tests.test_results_fill_transfer
ModuleNotFoundError: No module named 'joulewise.results_fill_transfer'
----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

Final focused acceptance run:

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_transfer
.
----------------------------------------------------------------------
Ran 1 test in 0.006s

OK
```

Final registry census/lint run:

```text
$ R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
.............
----------------------------------------------------------------------
Ran 13 tests in 2.706s

OK
```

Per the runner preflight, no whole-suite discovery or unlisted test module was
run.

## Clause map

The magistrate adopted R3 at
`docs/process_traces/2026-09-04-paper-i/06-magistrate-contract-rulings.md:19-21`;
the exact adopted schema, prose, fixture, and mutation clauses are at
`docs/process_traces/2026-09-04-paper-i/02-consult-sol-contracts.md:269-314`.

| Clause | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| Closed content-addressed v1 projection | `joulewise/results_fill_transfer.py:20-23,61-140,341-411` | `tests/test_results_fill_transfer.py:97-121,153-184` | Change any schema/source digest without the issued content ID; all nine sites become `STOP_FILL`. |
| Reviewed-source hashes and exact 10-run/20-edge census | `joulewise/results_fill_transfer.py:183-269` | `tests/test_results_fill_transfer.py:153-209` | Change any capture/plan/receipt/estimator/bundle digest or any census field; the assertion fails if any prose escapes. |
| Public maximum, raw-interval witness, and anchor replay | `joulewise/results_fill_transfer.py:272-320,364-370` | `tests/test_results_fill_transfer.py:207-245` | Change the public maximum, interval endpoint, or anchor after reissuing the content ID; replay refuses. |
| Pulse public name bound to source `b_fiducial_s` | `joulewise/results_fill_transfer.py:204-226,371-373` | `tests/test_results_fill_transfer.py:227-229` plus digest loop `:153-184` | Rename the source field to `b_pulse_s` or alter its artifact digest; every site stops. |
| Enum and unrounded `<=` / `>` split | `joulewise/results_fill_transfer.py:375-401` | `tests/test_results_fill_transfer.py:211-217,274-291` | Mark equality `not_supported`, swap a comparable outcome, or use `exceeds_bound`; every site stops. |
| Diagnostic-only/non-claim flags | `joulewise/results_fill_transfer.py:356-359` | `tests/test_results_fill_transfer.py:219-225` | Set `diagnostic=false` or `claim_bearing=true`; every site stops. |
| Exact six-decimal professor-facing prose | `joulewise/results_fill_transfer.py:431-460` | `tests/test_results_fill_transfer.py:33-51,106-121,274-289` | Change wording, punctuation, or six-decimal formatting; the exact sentence assertion fails. |
| Nine byte-identical, branch-independent copies | `joulewise/results_fill_transfer.py:28-38,428,493` | `tests/test_results_fill_transfer.py:102,119-121` | Remove or specialize one A/B/Refusal site; the ordered-site or repeated-byte assertion fails. |
| Exact issued bytes only; malformed/object channels fail closed | `joulewise/results_fill_transfer.py:463-493` | `tests/test_results_fill_transfer.py:125-150,293-298` | Infer the expected digest from the candidate, accept a dict, duplicate key, NaN, or malformed JSON; the fail-closed assertion fails. |

## Residual risk

The renderer is fixture-proved only. It does not accept the unreviewed capture
producer, issue the live transfer result, or integrate the token into the
lead-owned successor renderer. Those remain separate review/live gates.
