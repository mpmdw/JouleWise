# D165-OUTCOME-RENDERER-01 — Sol fix round 1

Date: 2026-09-04  
Seat: Sol xhigh implementation  
Ruling: `docs/process_traces/2026-09-04-paper-i/06-magistrate-contract-rulings.md` R4  
Base/head at intake: `c93745072f06e501aa2d9330456bfc9dbe3bac9b`  
Branch: `feat/2026-09-04-d165-outcome-renderer`

## Outcome

Fixed refuter B1 and F1–F4 without issuing a measurement value or wiring the
frozen paper renderer. OB-01 and OR-01 now compare to exact strings registered
independently in the two owning registry rows. Before-comparison inputs are
exact bytes paired with a typed, source- and manifest-digest-bound result from
the named owning validator; the old normalized-dictionary and caller
precedence channels no longer exist. The fixed Qwen3 names and revisions gate
every fill. A wrong pair or revision returns both fills as `STOP_FILL` and
records `identity_not_v5` in non-paper stop metadata.

The five fixture cases now use fresh Qwen3-1.7B-4bit / Qwen3-8B-4bit copies of
the landed D-165 builders. Floor stack identities and their digests are
resealed with the fixture manifest, so the D-165 validator still authenticates
the complete 8+4 census.

## Finding dispositions

| Finding | Cure | Biting regression |
|---|---|---|
| B1 | OB-01/OR-01 rows register exact templates and five exact fixture-oracle strings; the acceptance test reads those bytes from the registry rather than treating its fixture as the oracle. | `test_b1_registered_bytes_are_the_independent_acceptance_oracle` |
| F1 | `BeforeComparisonValidationResult` binds exact source and manifest digests, validator identity, and the validator's complete tuple. Whole-window issued reason must equal the validator result; claim-verdict validation must be error-free. Caller mappings, wrong validators, changed bytes, and caller-rehashed reasons stop. | `test_f1_before_comparison_requires_digest_bound_source_bytes_and_result` |
| F2 | Removed `precedence` and `before_comparison_stops`. Registered stage order selects before-comparison evidence; a sole close-out renders directly; dual-stage input retains the top-level close-out reason as `_secondary_closeout_reason`. | `test_f2_registered_stage_order_has_no_precedence_channel` |
| F3 | OR-01 copies the authenticated top-level close-out reason. Refused ratio records supply affected components: the census refusal names its refused component, while the source refusal with no refused record renders exact `none recorded`. | `test_f3_top_level_closeout_reason_renders_without_matching_ratio` |
| F4 | Every arm's realized model `{name, revision, family}` must belong to the exact two-member `_v5` set. Both the old Qwen2.5 pair and a one-revision mutation stop with `identity_not_v5`. | `test_f4_v5_identity_gate_precedes_every_fill` |

## RED / GREEN evidence

The first post-regression run was RED:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_outcome
Ran 6 tests in 1.734s
FAILED (failures=2, errors=7)
```

Its failures exposed the missing byte/result channel (F1), live precedence
parameter (F2), absent top-level rendering/oracle (F3/B1), and missing identity
gate (F4). A focused B1/F2/F3/F4 replay then produced seven expected failures,
including all four absent registry oracles and Qwen2.5 rendering instead of a
stop.

Final permitted implementation/close-out suite:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_outcome tests.test_d165_dominance_closeout
Ran 53 tests in 10.952s
OK
```

Final permitted registry checks:

```text
R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
Ran 13 tests in 2.696s
OK
```

The repository-wide suite was not run because the brief's preflight rule
exhaustively limited test modules.

## Mutation proofs

An in-memory harness compiled one production-site mutant at a time and ran
only the owning `tests.test_results_fill_outcome` method. No repository file
was changed by the harness.

| Finding | One-site counterfactual | Observed |
|---|---|---|
| B1 | Append one byte to registry oracle `branch_b` at read time. | `B1_MUTANT_KILLED failures=1` |
| F1 | Delete the exact-source SHA-256 comparison. | `F1_MUTANT_KILLED failures=1` |
| F2 | Allow the before-stage branch only when no close-out is supplied. | `F2_MUTANT_KILLED failures=1` |
| F3 | Restore the old `STOP_FILL` when no refused ratio record is present. | `F3_MUTANT_KILLED failures=1` |
| F4 | Bypass `identity_not_v5` and continue with an empty model map. | `F4_MUTANT_KILLED failures=1` |

## Clause map delta

| R4 proposition | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| B1 — registry carries exact professor-facing bytes | `docs/paper/results-fill-registry.md:919,921` | `tests/test_results_fill_outcome.py:234` | Change a registered oracle byte while leaving the fixture/rendering unchanged. |
| F1 — governed source bytes plus validator result | `joulewise/results_fill_outcome.py:50,138` | `tests/test_results_fill_outcome.py:263` | Delete the source-digest comparison or accept a caller mapping. |
| F2 — no precedence channel; before stage wins | `joulewise/results_fill_outcome.py:306,356` | `tests/test_results_fill_outcome.py:350` | Reintroduce `precedence` or make dual-stage evidence select close-out. |
| F3 — top-level reason; affected components or none | `joulewise/results_fill_outcome.py:281` | `tests/test_results_fill_outcome.py:375` | Require a ratio-local reason equal to the top-level reason. |
| F4 — exact `_v5` pair and revisions before fill | `joulewise/results_fill_outcome.py:36,183,346` | `tests/test_results_fill_outcome.py:393` | Remove the identity stop or compare names without revisions. |

## Scope and handoff

All writes are within the exhaustive allowlist. No commit was created. The
future successor adapter must construct `BeforeComparisonValidationResult`
from the actual named owning validator result and pass the exact bytes it
validated; this seat deliberately did not wire the frozen paper renderer.
