# Magistrate disposition of Sol 256 (file 19) — the §5 fresh pass over `7488a3c0`, 2026-09-02

Sol 256 returned 0 blockers, 2 should-fix, 0 nits, plus five answered
questions. Nothing is lowered; both should-fix findings are cured at the
bench in the commit that carries this file. Because that commit changes a
test, one more §5 fresh pass is owed over it (operation-loop §5); the pass
is scoped to the delta below.

| Finding | Severity | Disposition |
| --- | --- | --- |
| F1 census test counts direct syntax only — an alias (`probe_alias = _fresh_probe`), a stored callback, `globals()["_fresh_probe"]`, or an attribute lookup adds a governed probe the census cannot see | should_fix | **CURED at the bench** in `tests/test_arm_readiness_evidence_t0.py::test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census`: the test now asserts that direct calls are the ONLY references to `_fresh_probe` in the module — every `ast.Name` `_fresh_probe` that is not a `Call.func`, every `ast.Attribute` with that attr, and every string constant equal to it fails the test; and that exactly one `FunctionDef` of that name exists. Mutation probe (counterfactual inputs per the mutation-cure rule; run against mutated COPIES of the source, checkout untouched): Sol's exact alias mutant, a `globals()[...]` mutant, a stored-callback mutant, and a plain twelfth direct call are all KILLED; the unmutated source passes. Executed evidence below. NOT cured, recorded: the census does not prove reachability or ordering (a direct call moved before R1 still counts as post-R1); that is a limitation of a static census and the ruled derivation is by site count, not by trace — the empirical row (F2) is the instrument for the runtime question. |
| F2 the empirical kernel row `T0-LIVENESS-BOUND-EMPIRICAL-01` required a `validity_origin_monotonic_ns` receipt field that no producer emits and the exact key set forbids | should_fix | **CURED at the bench** in `docs/process/state_kernel.json` (+ regenerated `TASK_QUEUE.md`): acceptance route A now recovers the origin EXACTLY as `valid_until_monotonic_ns − _validity_horizon_ns(kind)` from any evidence receipt (the author computes `valid_until = validity_origin + horizon`, `joulewise/arm_readiness_evidence_t0.py` `_assemble_receipt` call inside the derived-row loop) and reads `r1_batch_finished_monotonic_ns` from the `clock.correct_and_prior_state` row's fact payload; no producer or schema change is needed. Sol's proposed correction adopted as written. |
| G1(a) the brief named `joulewise/arm_readiness.py` as the censused file; the test parses `t0.__file__` = `joulewise/arm_readiness_evidence_t0.py` | brief error | Recorded. The census count of 11 and the R1 exclusion were independently confirmed by the seat. |
| G1(c) the 105 s term is a bare literal in the test | recorded | The 105 s is the cold gate's ruled allowance (T26 item 3), not a code-derived quantity; the test pins the ruled arithmetic, which is what the ruling asked. The seat's stronger point — §6.3.1 shows 220 s of fixed Git ceilings alone, so the 105 s is not a runtime envelope — is exactly the PHYS-1 correction already appended to the ruling and routed to the empirical row. No further action. |
| G2 addendum + correction | clean | Number, comparison, labelling, clock typing unchanged; the correction contradicts the withdrawn premise explicitly; slug resolves. The brief's link path lacked `impl/`; the actual document is `docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md`. |
| G3 kernel row + queue | clean | `gen_state --check` and `test_gen_state`/`test_docs_freshness` green; the remaining "deliberately NOT implemented" sentence is explicitly historical. |
| G4 comments | clean | Both true; `sample_arm` has no evidence/rows, liveness conjunct never executes against it (seat patched the predicate to raise and validated the fixture: 0 calls). |
| G5 module run | clean | 149 tests OK (skipped=7). |

## Executed evidence (bench, this session, `/Users/edr/code/JouleWise-wt-t26-b` with the cures applied, `TMPDIR` under the scratchpad)

```
$ python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census
Ran 1 test in 0.034s
OK
$ python3 <mutation probe: census() re-implemented from the test body, applied to the unmutated source and to four in-memory mutants inserted at the top of _derive_power>
base 11 []
mutant alias: post_r1=11 indirect=[('Name', 1834)] -> KILLED
mutant globals: post_r1=11 indirect=[('Constant', 1834)] -> KILLED
mutant callback: post_r1=11 indirect=[('Name', 1834)] -> KILLED
mutant direct: post_r1=12 indirect=[] -> KILLED
$ python3 scripts/gen_state.py && python3 scripts/gen_state.py --check && echo CHECK-OK
CHECK-OK
$ python3 -m unittest tests.test_gen_state tests.test_docs_freshness
OK
```

The full `tests.test_arm_readiness_evidence_t0` module run over the cured
test is in the next fresh pass's evidence (the census test is the only
test changed).
