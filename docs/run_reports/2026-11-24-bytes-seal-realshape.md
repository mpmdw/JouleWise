# BYTES export seal on real-shaped rosters (cold review of PR #949)

Branch `ops/2026-11-24-bytes-seal-realshape`, cut from
`ops/2026-11-22-bytes-p1m1-base` at `35ef915048bfe38f9ff68d4ea96abe5225897013`
(PR #949 merged). The PR targets that base, not `main`.
`joulewise/bytes_analysis.py` is unchanged
(`18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`).

## Cold review (gate ledger rows 1 and 4)

The research lead's cold final review of PR #949 under RL-201 §4.2(1) was
taken at `35ef91504` on 2026-11-24. Its verdict is **HOLD**. Its record is
outside the repository, with scripts, logs and a tested diff in its seat
directory (`fable-bytes-p1m1-cold-1124`, `FINAL-MESSAGE.md` and `evidence/`).

- **Blocker.** The export seal reads `member["role"]` from session rosters
  (`joulewise/b6/bytes_integrity.py:337` at the base). The harvest writes roster
  members with `run_id`, `stage_id`, `kind` and `units` only
  (`joulewise/b5/harvest.py` `l4_exclusion_inputs`). So `capture` raises
  `KeyError: 'role'` on a real archive, and `bytes_stage1.py run` exits 1. Every
  sealed command after it refuses.
- **Narrow defect, same cause.** The twin's rule for a planned science run
  absent from the admitted rows (`scripts/bytes_twin.py:2077`) tested
  `role == "science"`, so it kept no run on a real roster. The library keys on
  units.
- **MED 1, worse than recorded.** With the seal repository inside the export
  directory, a table planted under `.git/` passed the shared check and the twin
  read it.
- **Desk.** The §4.2(2) re-fit is a stage-1 driver run with a separate seal
  repository, then `cmp` against the committed blobs. The twin's blinded-post
  call needs all twelve `--archive` roots. Later steps use the driver's own
  `released-keys` and `t-1.json`.

Row 1 is this cold review plus the audit that follows this PR, which the lead
runs. Row 4 is this cold review. Under the review's process note, the
re-review covers this delta only.

## Changes

| Finding | Change | Regression |
|---|---|---|
| Seal reads a roster role the harvest never writes | `_fit_run_ids` (the review's diff): the roster supplies each run's units, the table supplies the role. A row is authorized only if its run is a roster member, its cells equal that member's units, every cell is a fit cell, and a row with no cell carries a reference role. | `RealShapeFitRowTests` (the harvest's own writer on `bytes-s1-p1` and `bytes-s5-p1`, with the exporter's plan-walk roles; the review's eight accept and refuse cases); the seal fixtures, now harvest-shaped |
| Stage-1 driver cannot start on a real archive | Same change | `RunTests.test_pre_commit_sequence_writes_agreeing_predictions`: twelve harvest-shaped sessions, `READY_TO_COMMIT`, both seal commits present |
| Twin keeps no lost planned run on a real roster | `absent_science_rows` keys on units, as the library does (the review's diff) | `test_absent_planned_runs_follow_harvest_units_not_roles`; `test_all_invalid_members_skip_meter_joins_and_keep_refused_cells` with a harvest-shaped member; `test_planned_run_lost_from_withheld_rows_agrees_on_the_harvest_roster` (the review's absent-row probe) |
| MED 1: seal repository inside the export | Capture and every verification refuse a seal repository inside any sealed export directory. Capture no longer ignores `.git` or the manifest in a table root. The driver's `--export-seal-repo` is required, with no default. The review's `rglob` check stays: a sealed command given export directories refuses any table under them that the seal does not name. | `SealLocationTests`: capture refuses both layouts; a table or sidecar planted under `<export>/.git/` refuses both fit CLIs before any read; a seal in #949's default layout refuses at the location check, and with that check bypassed its planted table refuses at the `rglob` check; `test_seal_repository_is_required_and_outside_every_export_directory` |
| Synthetic rosters differ from real ones | One shared writer, `tests/fixtures/bytes/harvest_roster.py`, built on the harvest's own `l4_exclusion_inputs` and `write_json_once`. `campaign.py`, `twin_synth.py` and the BYTES seal, twin and availability fixtures write through it. No synthetic roster carries `role`. | `tests/test_bytes_roster_shape.py`: the harvest's shape on all twelve sub-packs (1,000 science and 300 auxiliary members, four keys); the shared writer reproduces the harvest's members for each; every roster both generators write carries only harvest keys; a planted `role` is reported |

**Reading the review's diff.** I applied it as tested, with two comments
reworded. One check of the original is gone: the roster role no longer has
to equal the table role. A real roster has no role, so that check cannot run
on real data. The table's roles come from the registered plan walk
(`joulewise/b6/acceptance.py` `_stage_roles`). A held-out science run cannot
pass in any role, because its roster units name a held-out cell. A
cell-less row passes only with a reference role, and only for a cell-less
roster member.

**Plan-walk roles in the fixtures.** Without roster roles, the campaign
fixture's export refused with `reference membership harvest roster`. The
exporter and `evidence_from_archive` take reference roles from the archived
plan tree and fall back to roster `role` (`export_runs.py:209`,
`acceptance.py:463`). A real archive has the tree. The fixture had none, so it
had relied on the fallback. `campaign.plan_tree` now gives the exporter a tree
in the registered shape: science rows, one external-input manifest per
reference stage under the registered input ids, and the stage graph. The
fixture passes it as the plan's `plan_tree`. Two availability tests that plant
plan-tree candidates now plant that tree in place of `{"stage_graph": []}`.
The smoke-witness control keeps the registered `bytes-s2-p1` graph. Its
member inputs now name the fixture's runs, as a real witness names its own;
it had emptied them.
I checked equivalence on a three-session campaign: `bytes-s1-p1`, `bytes-s5-p2`
and `bytes-s6-p1`. The visible and withheld tables had identical identity
columns under the base fixture and this one: run, stage, role, order, cells,
units, status, exclusions, flags and configuration. Only the blinded energy
columns differ, because of the random factors.

**Not converted, for the lead.** `tests/b6/*` exporter and acceptance
fixtures and `tests/test_bytes_gates.py` still write roster `role`, and some
write `status`. They exercise the exporter's fallbacks on purpose:
`tests/b6/test_export_runs.py` pops `role` to test its absence. The seal,
driver, twin and analysis do not read either key. On real archives the
exporter's fallbacks are inert, because the archived tree supplies every
role. Bringing those fixtures under the shape test is a B6-exporter test
change, not part of this fix.

## Failing first

On a base worktree (`35ef91504`) carrying only this PR's test and fixture
changes, all ten new or converted regressions fail. That is 22 subtest
errors and failures in total:
- `KeyError: 'role'` at capture and in the driver
- no refusal of a seal repository inside the export
- the twin dropping the lost run
- the lost-withheld-row campaign with 12 fields above the bar, which equals
  the review's count

On this head they pass.

## Verification

Local runs used Python 3.13 under `taskpolicy -c utility`, two processes at a
time, with a private `TMPDIR` each, on synthetic and real-shaped fixtures
only. Outcomes are in the PR body. Hosted CI runs the full suite on the merge
of this head into the PR base. The local runs skipped
`CampaignWordRates.test_twenty_production_shaped_campaigns_per_world`, a
60-campaign sweep, and the remaining agreement campaigns. Hosted CI runs
both.

## Desk

`docs/bytes/stage1/DESK-REFIT.md` is the magistrate's §4.2(2) runbook. It
contains:
- the exact command form on this head, with a separate seal repository and
  three `cmp` checks against commitment `569591e5…`
- what makes "same inputs" checkable
- the ordered refusals
- the twelve `--archive` roots for the twin's blinded-post call
- the driver's own `released-keys` and `t-1.json` for later steps

Paths not knowable from the repository are placeholders: the merged SHA, the
12 November stage-1 directory's date suffix, and seven session ids. The
magistrate fills them from the lead's hand-over and a names-only listing.
Before the run, the magistrate sends the lead names-only listings of the
export directory and `blinding-sessions`.

## Findings disposition (gate ledger row 5)

| Finding | Disposition |
|---|---|
| Seal role read (blocker) | Fixed, with regressions above |
| Twin absent-run rule | Fixed, with regressions above |
| MED 1 | Fixed in code and in the desk command form |
| MED 2 (commitment doc understates what verification opens) | Deferred to the lead. This PR adds only the seal-location paragraph to `docs/design/bytes_commitment.md`. |
| MED 3 (empty-flags matrix case accepts two matching refusals) | Deferred to the lead. It is confined to the generated fault matrix. |
| MED 4 (audit seat saw a published pilot threshold) | No action, per the review |
| #949's gate-ledger check failed after merge | This PR carries a filled ledger and waits for the check |
| Other BYTES-group bindings in `blinding-sessions` | Open. It needs the magistrate's names-only listing (`DESK-REFIT.md` step 1). |
| B6 exporter fixtures that still carry roster `role` | Deferred to the B6 exporter lane, as above |

## Blinding and seat

No custody, energy, power, meter, transcript, hazard, sealed, held-out or
stage-1 record content was opened. The real shape comes from the harvest's
writer run on registered configs. The worktree's Git directory was not
readable from this seat. The branch was built in a fresh HTTPS clone of the
PR base, whose tree was byte-identical to the assigned worktree.
