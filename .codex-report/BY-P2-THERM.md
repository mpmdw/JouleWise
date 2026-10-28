# BY-P2-THERM

## Summary

Built from `de35f6403` on `codex/2026-10-28-by-p2-therm`, under
`docs/registrations/bytes_pack_v1.md` §21 item 3. Read the cold judge's R1 report
from JouleWise-data `claude/by-thermal70-judge`, blob
`b0036548c19b142c1ef003aa1e5df1d89b2605c4`.

For pass-2 BYTES science members, only `thermal.os_level_nonzero` changes:
production `thermal_member_flags` and `in_force` evaluate
`[member_spans(...)["member"][0], member_spans(...)["request"][1]]`.
An absent request keeps the hull. Reference members, hull coverage holes,
powermetrics thermal pressure, battery, contention and clock keep their rules.
No flag code, effect, catalog digest, estimator or threshold changed.

The base code disagrees with the adopted §21 window by still applying the hull
to pass-2 science OS exclusions; this diff installs the registered change.
No additional authority/code discrepancy or science choice was found.

## Diff call sites

- `joulewise/b5/harvest.py:3062`: extracted the existing numeric-level / in-force
  nonzero-sample selection without its eight-sample display truncation.
- `joulewise/b5/harvest.py:3072`: production thermal function uses that same
  selection; coverage retains its original successful-numeric sample times.
- `joulewise/b5/harvest.py:3836`: initialize pass-2 selection to false.
- `joulewise/b5/harvest.py:3994`: read the preserved pack plan's registration
  values during roster construction.
- `joulewise/b5/harvest.py:4079`: enrich pass-2 assessments before sealing them.
- `joulewise/b5/harvest.py:4087`: store full-hull OS evidence per science member.
- `joulewise/b5/harvest.py:6231`: keep the hull join and replace only its OS
  flag with the production request-end OS result.
- `tests/test_harvest_b5_window.py:2322`: recognize `thermal.jsonl` as a filename
  in the emitted-code literal census; no catalog exemption or code was added.
- `tests/b6/test_bytes_p2_thermal_window.py`: production-journal unit tests,
  a deterministic 780-stream subset property, committed-plan selection checks,
  strict-valid synthetic harvest and base byte-identity replay.

## Decisions I made

- Use the preserved pack plan tree's `blinding_group == "bytes"` and
  `bytes_pass == 2`, in a block-six harvest. The generated trees already carry
  these registration values, so no pack-name inference or separately mutable
  registration lookup is needed. Selection is checked against all six pass-2
  trees, all six pass-1 trees and ALPHA/BETA/GAMMA.
- Preserve the full-hull production thermal call, then replace only its OS
  exclusion with the shortened production call's OS exclusion. In particular,
  shortened-window coverage cannot suppress a hull coverage hole.
- Full-hull evidence lives in `withheld/member-assessments.json`, at
  `members[run_id].thermal_os_level_nonzero_member_hull`. Its fields are
  `span_monotonic_ns`, `excluded`, all nonzero `samples` (each timestamp and
  level), and `journal_available`. Unknown hulls have `excluded: null`; a missing
  journal is explicit and still emits `thermal.unmeasured`. This is descriptive
  evidence, never an additional flag or an input to exclusions.
- Assessments are already sealed and referenced by flags before monitor joins.
  Read the thermal journal at assessment time to record the full-hull evidence
  before sealing; the later monitor join and source-stability check still run.
  The shared production sample selector prevents divergent evidence semantics.
- Keep all nonzero samples in the evidence record, including more than eight;
  the existing flag payload's eight-sample cap remains unchanged.
- The BYTES loop's `DeskLane.session_desk` calls `scripts/harvest_b6_session.py`,
  which imports `joulewise.b5.harvest.harvest`. The end-to-end test invokes that
  exact imported callable, with real input resolution, strict validation,
  reduction, roster, journals, exclusions and archive writers. It reuses
  `tests.test_harvest_b5_window.Window`, as existing b6 harvest tests do.
  Hardware/process liveness and audit provenance are seams. The fixture already
  supplies the desk verdict; the external desk-verdict child and G3 are disabled.
  The b6 wrapper module is tested separately through its CLI main function.
- The synthetic tail uses the controller's `idle_drift_sentinel` event stamps,
  so strict-valid clock evidence and request/telemetry bytes remain intact.
- Exact equality is the only comparison bar. No tolerance was introduced.
  Five-second polling and the single 5.3-second gap are requested stream shapes,
  not acceptance thresholds; coverage uses the existing registered 15-second bar.
- This is synthetic desk evidence, not hardware validation. No BYTES energy or
  production archive was read, and no quiet-Mac collection was run.

## NEEDS_RULING

None.

## End-to-end pass-1 byte identity

The test loads the base harvest module directly from
`git show de35f6403:joulewise/b5/harvest.py` into a separate Python module.
It runs base and changed code against the same input paths and bytes, at the
same output path, saving the first archive in memory before recreating it.
Every relative filename and every byte in the archive is compared exactly,
including harvest.json, flags, exclusions, member assessments, raw copies,
reductions and output digests. No output normalization or ignored files.

The audit clock, boot UUID and `harvest_checkout` record are fixed identically
for both executions: naturally those report the time and program identity, so
they otherwise change even when harvest behavior is identical. This does not
claim that two ordinary invocations at different program heads have identical
provenance. The fixture includes late nonzero thermal reads and a 5.3-second
poll gap. The same exact replay also covers a block-5 lane and a non-BYTES lane.
Final replay: all 177 archive files are byte-identical for pass 1. The same
177-file exact comparisons pass for block 5 and a non-BYTES block-six lane.
The manifest digest hashes sorted `relative_path + NUL + SHA256(file_bytes)`;
temporary absolute paths are present in the files, so it identifies this replay,
not a portable golden artifact.

```text
BYTE_IDENTITY pass1: 177 files, exact equality; manifest_sha256=fbd9cb7dba05cbfa6cc9c161195574672e96a43b1c0b1fc10f9039e75a14e2bd
BYTE_IDENTITY block5: 177 files, exact equality; manifest_sha256=dc11de3bb6809a8d24cb3cc8a65d1373963ca630487de86700002764379ed63b
BYTE_IDENTITY alpha: 177 files, exact equality; manifest_sha256=ed6e7ce27dc85f3f3743451d02c2aff5c058d09cda240fe2c3117a6c57120234
```

The pass-2 end-to-end case also passes: all six science bundles are strict-valid,
late-only OS levels produce no primary OS exclusion, and every member assessment
records the full-hull exclusion and its samples. The 780-stream subset check has
zero request-end-only OS exclusions.

## Test commands and output tails

All test commands run from the repository root with Python 3.13 and prefix
`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B -m unittest`.
Only the requested harvest/flag modules and the b6 session wrapper are run
locally; the full suite is left to CI as instructed.

1. `tests.test_harvest_b5_window tests.flags.test_flags_fx_regressions`
   (`/tmp/by-p2-step1.log`): `Ran 193 tests in 465.141s;
   FAILED (failures=1, skipped=11)`. The only failure was the emitted-code census,
   repaired by naming `thermal.jsonl` as a filename; all four census tests pass
   in command 6. All other tests in this run passed or were skipped.
2. `tests.b6.test_bytes_p2_thermal_window`, first development run:
   `Ran 9 tests in 2.988s; FAILED (errors=4)`. Synthetic metadata used the wrong
   clock-stamp key (`KeyError: telemetry_clock_stamps`); corrected the fixture.
3. Same command, second development run (`/tmp/by-p2-new.log`):
   `Ran 9 tests in 198.128s; FAILED (failures=1)`. Base comparisons passed for
   177 files in each lane; the pass-2 fixture failed strict validation after a
   clock-stamp edit. Replaced that edit with production sentinel events.
4. `tests.b6.test_bytes_p2_thermal_window.ThermalWindowTests`
   (`/tmp/by-p2-unit.log`): `Ran 9 tests in 0.329s; OK`.
5. `tests.test_harvest_b5_window.EmittedCodeTests.test_every_code_literal_in_the_harvest_is_listed`
   (`/tmp/by-p2-code-literals.log`): `Ran 1 test in 0.002s; FAILED (failures=1)`;
   only unexpected literal: `thermal.jsonl` (a filename).
6. `tests.test_harvest_b5_window.EmittedCodeTests`
   (`/tmp/by-p2-catalog.log`): `Ran 4 tests in 0.016s; OK` after filename fix.
7. `tests.b6.test_session_wrapper` (`/tmp/by-p2-wrapper.log`):
   `Ran 6 tests in 0.125s; OK`.
8. `tests.b6.test_bytes_p2_thermal_window` (`/tmp/by-p2-final-new.log`):
   `Ran 11 tests in 229.351s; FAILED (failures=1)`. The synthetic sentinel had
   been appended after `run_finalized`; strict validation requires finalization
   to be last. Moved the tail before that marker and updated its timestamp.
9. `tests.test_harvest_b5_window.EmittedCodeTests tests.b6.test_bytes_p2_thermal_window.ThermalWindowTests tests.b6.test_session_wrapper`
   (`/tmp/by-p2-final-focused.log`): `Ran 19 tests in 0.394s; OK`.
10. Direct fixture validation: `h.strict_problems(bundle, None)` on each of the
    six generated science bundles: all six returned `[]`. The first diagnostic
    attempt omitted the required cache argument and raised `TypeError`; the
    corrected command passed. Both used the same synthetic-only environment.
11. `tests.b6.test_bytes_p2_thermal_window` (`/tmp/by-p2-final-new2.log`):
    `Ran 11 tests in 231.111s; OK`. Final replay manifest lines are above.
12. `tests.test_harvest_b5_window tests.flags.test_flags_fx_regressions`
    (`/tmp/by-p2-final-regressions.log`):
    `Ran 193 tests in 462.897s; OK (skipped=11)`.

Final local results: requested existing regression modules green (193 tests,
11 skips); new unit/property/entry module green (11 tests); b6 wrapper green
(6 tests). The development failures above were fixture/census issues and are
resolved; no production-code correction was needed after the implementation
commit.

`git diff --check`: passed (empty output).
Catalog SHA-256, unchanged from base:
`01767fe4e75ed961798f4e6b68cf055a5b3946a474129e93d2b5e7c239a1dd0c`.

## CI

Draft PR [#594](https://github.com/mpmdw/JouleWise/pull/594), **CI only: BY-P2-THERM**,
targets `ci/2026-10-27-bytes-enddate`. No merge requested or performed.
CI for final code/test commit `a9f4617edfda44f85d8c7c5c5a24f39d6a012e11`
is **not green**:
[run 40681601271](https://github.com/mpmdw/JouleWise/actions/runs/40681601271),
[failed shard 6](https://github.com/mpmdw/JouleWise/actions/runs/40681601271/job/122794203445).
At the stop boundary, 13 jobs had succeeded, shard 6 had failed, and six shards
were still running. Build, fences, quick, installed-wheel, both crash-matrix jobs,
and the calibration-exit job passed. The gate-ledger workflow was skipped for the
draft PR. Earlier development runs were superseded by corrected fixtures.

The failed job's completed log was read. Its only error was:

```text
ERROR: test_bytes_drafts_never_enter_live_loop_despite_base_order
       (test_b6_loop.LoopTests.test_bytes_drafts_never_enter_live_loop_despite_base_order)
  File "tests/test_b6_loop.py", line 170, in test_bytes_drafts_never_enter_live_loop_despite_base_order
    rejected = self.loop.state["pack_not_open"]
KeyError: 'pack_not_open'
Ran 64 tests in 8.249s
FAILED (errors=1)
MODULE FAIL tests.test_b6_loop tests=64 failures=0 errors=1 skipped=0 seconds=8.249
SHARD SUMMARY index=6/12 modules=38 tests=1270 failures=0 errors=1 skipped=3 result=FAIL
```

### Scope boundary

**File needed: `tests/test_b6_loop.py`.** Its lines 149–173 still assume pass 2 is
`draft` and assert that all six pass-2 registration files are rejected as drafts.
The specified base `de35f6403` registers those packs; for example
`configs/b6/packs/bytes-s1-p2/registration.json:357` already has
`"status": "registered"`. The real registration gate therefore supplies no draft
rejections and the fixture's `pack_not_open` lookup fails. The test and loop
implementation are byte-unchanged from `de35f6403` (`git diff` for both is empty),
and the failing test uses fake lanes rather than this harvest implementation.
This is a base-registration/test expectation mismatch, not a thermal-window
failure. The requested scope excludes that test file, so it was neither edited
nor executed locally. Repair would make this test self-contained with explicit
draft registrations, or update its registered-pack expectations while preserving
a separate draft-refusal case. No registration or production-loop change is
needed to address this error.

Per the brief's exhaustive WRITE_SCOPE rule, stop here and request that exact
file if the stale CI expectation is to be repaired. All authorized implementation,
focused tests, byte-identity evidence and this report are complete. A final
report-only commit follows the tested code/test commit; pushing it may supersede
the still-running jobs, but the failed shard's result above is retained.
The required two executing reviews remain external to this build; no production
pass-2 harvest was opened.
