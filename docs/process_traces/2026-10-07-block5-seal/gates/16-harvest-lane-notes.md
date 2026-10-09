# Harvest lane notes (author seat, Opus 5.5)

Worktree `/Users/edr/code/JouleWise-wt-harvest`, branch `lane/2026-10-07-harvest-lane`, base
`9395cecfbc40fb93e87a7657ec0ba5da0ca9ef3a`. Fence: `joulewise/b5/harvest.py`, `joulewise/whole_window.py`
(`_derived_neg8_decision` and its private helpers only), `scripts/harvest_b5_window.py`, `tests/`.
Tests: `/opt/homebrew/bin/python3.13 -B`, `TMPDIR=/private/tmp/w1007-harvest-lane/tmp`.

## Status (updated as each item lands)

| Item | State | Commit |
|---|---|---|
| K-4 | done | 8b186fc9d |
| K-5 | done | aba9a2f32 |
| K-6 | done | b12b41a06 |
| K-7 | done | d072b7952 |
| H-8 | done | 2ed4358bd |
| H-9 | done | 36ccd798c |
| H-10 | done | 339a15d76 |
| H-11 | done | e75a31152 |
| H-12 | done | 71386deac |
| H-13 | done | c10257418 |

## Design decisions taken while reading (each is reported in the return)

- K-4. "Energy unreadable" is the writer's own test on the stored `summary_metrics.json`:
  `run_campaign._gross_energy_for` is None or `_idle_subtracted_energy_for` is None. It is mirrored by one private
  helper in `whole_window.py` (built from `_gross_fields` and `_finite_number`, which hold the same arithmetic); a
  test drives the real writer functions against the mirror. `_derived_neg8_decision` gains one keyword,
  `unreadable_energy`: `"refuse"` (default, the row validator: unchanged behaviour), `"writer_entry"` (the harvest's
  authenticity pass: the reference is appended as the writer appended it, gross None) and `"lost"` (the harvest's
  exclusion pass: lost as `energy_unreadable`, its energy never read). The row validator's own replay is not changed
  (lane L9-NEG8 part (c)).
- K-4. The synthetic reference bundles of the test harness had a summary of `{"status": "succeeded"}` only, so by the
  writer's test every one of them had an unreadable energy. The fixtures now write the stored energies a real
  summary carries.
- K-5. A torn line that still shows its whole code keeps that code as its only candidate (the line shows it). The
  narrowing applies to a prefix.
- K-6. The four codes go into the reference list only, after the six physics codes; `NEG8_PHYSICS_LOSS_CODES` (which
  also drives the corpus drop) is not changed: the ruling left the corpus rule as registered.
- H-8. Driver checkout: a differing code file is a difference. Its porcelain is replayed in the scope the driver
  checkout executes: a tracked edit to a path that is a window input by the head classifier, or an untracked file
  under `joulewise/` or `scripts/`. Other dirty paths are recorded only (refusal rule: representation only).
- H-12. The three claim packs are a constant held equal to `sizing_b5.json` by a test.

## Next command

See the last line of this file.

## After the ten commits (head c10257418, pushed)

In flight: the lane's test modules on the final head (logs `/private/tmp/w1007-harvest-lane/tests-final-*.log`) and
the base-versus-lane harvest of the rehearsal archive (`/private/tmp/w1007-harvest-lane/ab/`, script `run_ab.sh`,
base worktree `/private/tmp/w1007-harvest-lane/base` at 9395cecfb, to be removed with `git worktree remove`).
Next command if the session stops: rerun the two, then compare with `ab/compare_ab.py`.

## Final state (head c10257418a9d7d2173bec306c0b1deb38e144343, pushed, worktree clean)

All ten items are committed, one commit each (table above). `git diff --name-only 9395cecfb..HEAD` lists
`joulewise/b5/harvest.py`, `joulewise/whole_window.py`, `scripts/harvest_b5_window.py` and three files under
`tests/`. The four pinned estimator files, `scripts/prewindow_check.sh`, `scripts/run_campaign.py` and
`joulewise/flags/collect.py` have the same git blob at the base and at the head.

Tests on the final head (`/opt/homebrew/bin/python3.13 -B`, `TMPDIR=/private/tmp/w1007-harvest-lane/tmp`):
`tests.test_harvest_b5_window` 202 OK (551 s); fourteen small modules (seal landing, refusal allowlist, the
`tests.flags` modules, three census and chain modules) 224 OK; `tests.test_neg8_survivors`, `tests.test_whole_window`,
`tests.test_whole_window_selection`, `tests.test_hazard_neg8_mint_verdicts`, `tests.test_harvest_b5_p2harv`,
`tests.test_harvest_b5_p3harv`, `tests.test_gate_prune_integration` 287 OK. Also run, finished after this was first written:
`tests.test_floor_extraction`, `tests.test_mint_floor_artifact_generalized`, `tests.test_run_campaign`
(log `/private/tmp/w1007-harvest-lane/tests-final-B3.log`).

Base-versus-lane harvest of the 2026-10-06 rehearsal window (`ab-compare.log` here): two new window flags and
nothing else in flags; every withheld file identical. `code.executed_differs_from_sealed` (H-8: the rehearsal's
driver checkout lists the untracked `scripts/rehearse_b5_real.py`) and `code.identity_unmeasured` (H-10: the
rehearsal's sealed inventory names no head). `exclusions.json` and `harvest.json` gain `harvest_checkout` (K-7);
`code-identity.json` gains the driver checkout's status fields (H-8) and `own_pack` with
`changed_paths_in_other_claim_packs` (H-12).

Scratch: `/private/tmp/w1007-harvest-lane/` (test TMPDIR, A/B archives, logs). The two snapshot worktrees
(`snap-k4`, `base`) were removed with `git worktree remove`.

`tests.test_floor_extraction`, `tests.test_mint_floor_artifact_generalized`, `tests.test_run_campaign`: 488 OK
(2 skipped), 324 s. No process of this lane is left running. Nothing is in flight. Next step is the
orchestrator's: an independent executing review and the cold Fable pass, then the addendum to the seal record.
