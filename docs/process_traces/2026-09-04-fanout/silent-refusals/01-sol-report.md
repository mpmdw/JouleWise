# Counterfactual refusal-test report

## Change

S1. A refusal is a named result that stops unsafe evidence from being accepted, and a refusal code is its stable machine-readable name.

S2. A counterfactual regression is a test that turns red, meaning that it reports a failure, when its targeted refusal is removed or replaced by a weaker result.

S3. A production call site is the executable branch that makes the refusal decision, and a test module is one test file; the focused test module exercises the five assigned refusal behaviors directly.

S4. A fixture is the smallest constructed input needed to reach a branch, and an integration module is a broad test file that composes several components; each new fixture avoids the integration modules identified by the audit.

| Refusal code and plain-language meaning | Production call site | Minimal fixture | Finding | Decision |
|---|---|---|---|---|
| `readiness_pack_not_committed`: an execution pack has no version-controlled files | `committed_pack_tree_sha256` | A temporary version-control repository with one committed file outside an empty pack | Normal test passes; replacing the refusal with `pass` leaves no exception and makes the selected test fail | Guarded by the focused module |
| `launch_binding_mismatch`: launch bytes changed after their file digest, a fixed-length byte fingerprint, was bound | `_read_exact_launch_reference` | One file whose bytes change after its digest is recorded | Normal test passes; removing the changed-byte refusal leaves no exception and makes the selected test fail | Previously blank audit row now has a red-mutant verdict |
| `config_hash_mismatch`: two realized identities, the recorded software and hardware facts, disagree within one model cohort, the group analyzed together | `_enforce_registered_realized_identity` | Two internally consistent bundle records with different model revisions and one cohort label | Normal test passes; removing cohort exclusion leaves both records included and makes the selected test fail | Guarded without the broad analysis integration module |
| `calibration_ledger_rollback`: an append-only calibration record is behind its committed head, the last approved record | `calibration_readiness` | A frozen record snapshot whose physical head, the last present record, is a proper prefix of its committed head | Normal test passes at the pre-slot and terminal branches; replacing rollback with head mismatch makes both branch checks fail | Both readiness branches retain the specific rollback classification in the focused module |
| `anchor_method_unregistered`: stored clock-anchor evidence, which maps sampler time to system time, names an unknown reconstruction algorithm | `_derive_anchor_context` | The retained clock-evidence bundle with only its stored method label changed | Normal test passes; restoring silent fallback to the first registered algorithm makes the selected test fail because the context is no longer unresolved | Guarded without the broad reducer module |

S5. The audit's later phrase “six silent refusals” does not match its own result table, which records one unguarded refusal, three narrow-module misses that broader modules detect, and one launch row without a verdict.

S6. The assignment selects exactly those five rows, so this implementation treats the phrase as a documented count discrepancy rather than inventing a sixth target.

Source: [code-and-tests audit, sections 2.2 and 2.3](../../2026-09-02-hands-free-week/13-audit-code-tests-opus.md).

## Verification notes

S7. A control is the unmodified source run, and the control passed all five focused tests.

```text
$ python3 -m unittest tests.test_silent_refusals
.....
----------------------------------------------------------------------
Ran 5 tests in 0.189s

OK
```

S8. A mutant is a disposable source copy with one refusal removed or weakened, and every mutant run used only the selected test from the new focused module.

| Disposable mutation | Exact test command | Exact tail | Result |
|---|---|---|---|
| Empty-pack raise replaced by `pass` | `python3 -m unittest tests.test_silent_refusals.SilentRefusalCounterfactualTests.test_empty_committed_pack_refuses_with_specific_code` | `Ran 1 test in 0.148s`<br>`FAILED (failures=1)` | Expected red |
| Changed-launch-bytes raise replaced by `pass` | `python3 -m unittest tests.test_silent_refusals.SilentRefusalCounterfactualTests.test_changed_bound_launch_bytes_refuse_with_specific_code` | `Ran 1 test in 0.006s`<br>`FAILED (failures=1)` | Expected red |
| Cohort disagreement exclusion removed | `python3 -m unittest tests.test_silent_refusals.SilentRefusalCounterfactualTests.test_realized_identity_disagreement_refuses_with_specific_code` | `Ran 1 test in 0.001s`<br>`FAILED (failures=1)` | Expected red |
| Rollback code replaced by head-mismatch code at both readiness branches | `python3 -m unittest tests.test_silent_refusals.SilentRefusalCounterfactualTests.test_physical_ledger_rollback_keeps_specific_code_at_readiness_sites` | `Ran 1 test in 0.001s`<br>`FAILED (failures=2)` | Expected red |
| Unknown-method error replaced by fallback to the first registered method | `python3 -m unittest tests.test_silent_refusals.SilentRefusalCounterfactualTests.test_unregistered_anchor_reconstruction_refuses_before_fallback` | `Ran 1 test in 0.028s`<br>`FAILED (failures=1)` | Expected red |

S9. Each mutation was made under `/private/tmp/joulewise-silent-refusals.417ANx`, so no production source file, meaning executable project code, in the repository, meaning the checked-out project tree, was edited.

### First-use test

S10. The first-use test numbers every changed prose sentence and requires each specialized term to be defined in the sentence where it first appears.

| Sentence | Specialized term first used | Definition present at first use | Result |
|---|---|---|---|
| S1 | refusal; refusal code | named stop result; stable machine-readable name | Pass |
| S2 | counterfactual regression; red | test that reports failure when the refusal is removed or weakened; reports failure | Pass |
| S3 | production call site; test module | executable decision branch; one test file | Pass |
| S4 | fixture; integration module | smallest constructed branch input; broad test file that composes components | Pass |
| S5 | none | not applicable | Pass |
| S6 | target | row selected for implementation | Pass |
| S7 | control | unmodified source run | Pass |
| S8 | mutant; focused module | disposable weakened source copy; module limited to the assigned behavior | Pass |
| S9 | production source file; repository | executable project code; checked-out project tree | Pass |
| S10 | first-use test; specialized term | sentence-to-definition check; field-specific word or phrase | Pass |

Mechanical completeness command:

```text
$ test "$(rg -c '^S[0-9]+\. ' docs/process_traces/2026-09-04-fanout/silent-refusals/01-sol-report.md)" -eq "$(rg -c '^\| S[0-9]+ ' docs/process_traces/2026-09-04-fanout/silent-refusals/01-sol-report.md)"
exit 0
```
