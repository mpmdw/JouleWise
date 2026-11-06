# Block 5 steps 9 and 9b speed review

Date: 2026-11-06.  Scope: synthetic/static analysis only; no experiment,
archive, night-custody, or restricted external path was accessed.

## Profile and static findings

Step 9 constructs the evidence-root mapping at `joulewise/b5_analysis/dry_run.py:1305`
and step 9b constructs the identical mapping at `joulewise/b5_analysis/dry_run.py:1568`.
Step 11 is a third consumer at `joulewise/b5_analysis/dry_run.py:1726`.  Before this
change, every call to `RunState.evidence_roots` reread the floor artifact and the two
extraction reports and reran `_evidence_roots` (`dry_run.py` previously had only the
two statements now at lines 840-841).  Those inputs and `self.windows` are sealed by
this point in the ordered driver.  The implemented per-run cache therefore removes
two of three identical derivations on the happy path.  The equality test measures
one derivation and exactly three `RunState.read` calls across two consumers, rather
than two derivations and six reads; it also mutates the first returned mapping and
proves that the second consumer receives unchanged bytes/paths.

Step 9b's structural eligibility pass built the registered contrast IDs as a list,
then performed `subject not in registered` for every verdict contrast.  This is
quadratic when the finalized manifest and verdict have *C* distinct contrasts.
The new code retains the list for the original ordered validation and duplicate
check, then freezes it to a set for membership.  No ordering-dependent output is
created by this predicate.

The following synthetic membership microbenchmark used best-of-three `timeit`
runs on this host.  It isolates the changed operation (all registered verdict IDs
looked up in the manifest IDs); it is not a full Block 5 runtime claim.

| contrasts | list lookup | frozenset lookup | speedup |
|---:|---:|---:|---:|
| 10 | 1.823 us | 0.888 us | 2.05x |
| 100 | 94.803 us | 5.017 us | 18.90x |
| 1,000 | 8,422.372 us | 53.019 us | 158.86x |
| 5,000 | 200,805.335 us | 263.217 us | 762.89x |

Command (synthetic identifiers only):

```bash
python3 -u - <<'PY'
import timeit
for n,loops in ((10,5000),(100,1000),(1000,50),(5000,5)):
    names=[f'contrast-{i}' for i in range(n)]; wanted=list(names); frozen=frozenset(names)
    old=min(timeit.repeat('all(x in wanted for x in names)', globals=locals(), number=loops, repeat=3))/loops
    new=min(timeit.repeat('all(x in frozen for x in names)', globals=locals(), number=loops, repeat=3))/loops
    print(f'n={n} old_us={old*1e6:.3f} new_us={new*1e6:.3f} speedup={old/new:.2f}x loops={loops}')
PY
```

## Changes and equivalence argument

1. `RunState.evidence_roots` now memoizes its first derived mapping and returns a
   fresh shallow copy on every call.  Mapping keys, `Path` values, sorting in step
   9, and the step 9b request comprehension are unchanged.  Defensive copies mean
   a caller cannot alter the cached mapping.
2. `claim_side_bound_not_issuable` still validates IDs in manifest order, rejects
   empty/invalid/duplicate IDs identically, and only then creates the frozenset.
   `_first_condition_is_outcome` is otherwise unchanged.
3. The equality test sends one issuable and all six registered non-issuable
   synthetic shapes through both the former list-backed lookup and new set-backed
   lookup and asserts identical booleans.  The existing step-9b tests additionally
   assert exact sidecar bytes on issuance and the exact no-output outcome row on
   every registered non-issuance shape.

## Verification

Focused equality tests:

```text
python3 -m unittest \
  tests.b5_analysis.test_dry_run.ClaimSideBoundStep9bTests \
  tests.b5_analysis.test_dry_run.Step9EvidenceRootCacheTests -v
```

The canonical repository suite was also run with `python3 -m unittest discover -s
tests`.  Results are recorded in the final handoff for the commit containing this
report.
