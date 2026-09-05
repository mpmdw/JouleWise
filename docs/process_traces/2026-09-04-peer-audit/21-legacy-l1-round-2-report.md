# Legacy L1 void cure — round 2 implementation report

Date: 2026-09-04  
Branch: `feat/2026-09-04-legacy-l1`  
Base: `a02e424e00424a51a010b04b9cbd09113e1150fa`

## Outcome

- Repaired the three stale vertical-slice expectations to assert the round-1
  VOID disposition. The `test_defaults_and_artifact_version_are_v2` error was
  caused by assertions for `FIGURE_REL` and `REGEN_COMMAND`, two constants
  intentionally removed when the producer stopped rendering and advertising
  regeneration of the voided corpus. The replacement assertions pin the VOID
  label, the source-only check command, and the absence of both retired
  constants.
- Preserved and strengthened the pristine-clone `--check` coverage: it still
  proves producer/generated-page equality, then mutates the generated page and
  requires exit 2 with the named drift diagnostic.
- Corrected the methodology to make gross per-request energy the headline
  basis and idle-subtracted energy a within-device secondary view.
- Reframed every targeted report reference to the historical corpus as
  permanently VOIDED for claim use, linked to the root README disposition, and
  stated that it supplies no report observations or energy values.
- The producer did not change in round 2, so regeneration was unnecessary. The
  committed generated page remains byte-aligned with the producer.

## Verification

All commands ran one at a time. The discovery suite was not run.

```text
$ python3 -m unittest tests.test_build_capstone
..
----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

```text
$ python3 -m unittest tests.test_rpt001_report_slice
.....s...s..s......
----------------------------------------------------------------------
Ran 19 tests in 0.239s

OK (skipped=3)
```

```text
$ python3 -m unittest tests.test_claims_index_lint
.............................
----------------------------------------------------------------------
Ran 29 tests in 2.132s

OK
```

```text
$ python3 scripts/build_capstone.py --profile rpt001 --offline --check
build_capstone: check OK (no drift)
```

`git diff --check` passed. A targeted source scan found none of the retired
`legacy L1 evidence`, `legacy L1 observations`, or idle-subtracted-primary
wording, nor any of the previously rendered corpus energy values under
`docs/report_src`.

## Handoff

No commit was created. Final review and commit remain lead-owned.
