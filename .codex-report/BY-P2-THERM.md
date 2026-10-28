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
- `tests/test_harvest_b5_window.py:2321`: recognize `thermal.jsonl` as a filename
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
Final replay results are recorded below when complete.

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
8. `tests.b6.test_bytes_p2_thermal_window` (`/tmp/by-p2-final-new.log`): running
   the corrected strict-valid fixture and all 11 final tests.

`git diff --check`: passed (empty output).
Catalog SHA-256, unchanged from base:
`01767fe4e75ed961798f4e6b68cf055a5b3946a474129e93d2b5e7c239a1dd0c`.

## CI

Draft PR [#594](https://github.com/mpmdw/JouleWise/pull/594), **CI only: BY-P2-THERM**,
targets `ci/2026-10-27-bytes-enddate`. No merge requested or performed.
CI for test-fix commit `fb0f901de` is running:
[run 40680943678](https://github.com/mpmdw/JouleWise/actions/runs/40680943678).
The earlier test-development runs are superseded by the corrected fixtures.
