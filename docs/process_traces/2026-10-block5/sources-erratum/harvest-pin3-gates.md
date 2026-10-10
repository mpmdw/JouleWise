# The harvest program for attempts governed by Erratum 2: gate record

Magistrate activation cbe4230e (Opus 5.5, headless), 2026-10-10. Structure only. The seats' full reports are
in `/Users/edr/night-archive/b5-consults/beta-a1/fix/` on the measurement Mac; the fix seat's first two
reports are also beside this file (`sol-fix.md`, `sol-fix2.md`).

The change is the desk side of Erratum 2 (`ERRATUM.md` beside this file, sections 4 and 5; cold ruling
`RULING.md`): when the stored verdict of a window records no source list, and only in the state item 0
defines, the harvest takes the window's reference list from the authenticated campaign catalog and runs
the registered drift screen on the surviving references. Branch `lane/2026-10-10-harvest-screen-sources`,
cut from the second harvest pin `224a264c5faaae90cdf56118df37e773a932700b`. Outside `tests/` it changes
`joulewise/b5/harvest.py` and `joulewise/whole_window.py`; `scripts/harvest_b5_window.py` is unchanged.
Like the earlier harvest lanes it is not merged into main.

## Who did what

| Step | Seat | Result |
|---|---|---|
| Root cause and first fix | Sol 6.1, effort xhigh (`sol-fix.md`), commit `0b23cf491` | mechanism proved from the sealed writer's code; registration read as a rule change, which sent the fix to the cold gate |
| Erratum: refuter and judge | Opus 5.5 refuter (`REFUTATION.md`), Fable 5.1 cold judge (`RULING.md`) | admitted with corrections; the judge wrote the rule text (items 0 to 9) |
| Round 2, the program brought to the admitted text | Sol 6.1, effort xhigh (`sol-fix2.md`), commit `d435547e2` | items 0 to 8 and the admission-time gate, each with tests; a comparison test on the real rehearsal copy |
| Cold final pass | Fable 5.1, new session (`FABLE-pass.md`), on `224a264c5..d435547e2` | last line `PASS`; no blocker; one test gap (F1); seven notes, recording only |
| Independent executing review | Opus 5.5 agent that wrote none of it, on `d435547e2` | `APPROVE WITH FIXES`; no blocker; four test gaps (S1 to S4); eight notes |
| Whole suite on the lane's tree | the CI shard runner, six shards and the two exclusive modules, non-venv Python 3.13 | see "The suite" |
| Round 3, tests only | Sol 6.1, effort high, commit `067f4deab` | F1 closed; the catalog call-site fence updated |
| Round 4, tests only | Sol 6.1, effort high | the reviewer's tests for S1 to S4, N1 and N4; one test hunk reverted (N6); see the last section |

## The cold pass (Fable 5.1)

Executed by the judge: the module `tests.test_harvest_b5_sources` (51 tests, OK); the rehearsal comparison
with `B5_REHEARSAL_COMPARE=1` (1 test, OK: derived bytes, withheld bytes and emitted flags identical under
the pinned and the changed program, and the derived bytes equal to the archive's own); the epoch of the gate
constant (`2026-10-10T16:30:00Z` is 1791649800); 20 mutation probes on a scratch copy, of which 19 were
killed by a test and 1 survived (F1).

Its statement: no way was found for the changed program to pass the screen, or to supply an allowance, that
the admitted text would remove; a verdict that records sources is handled byte for byte as under
`224a264c5`; the gate constant, its epoch and its place in the order are as the text says and fail closed;
the disclosure objects are exact.

- **F1 (should fix, tests only):** the fixture always required the clean bound, so deleting item 5's own
  clause went unnoticed. Fixed in `067f4deab`; the magistrate repeated the mutation on a scratch worktree
  and both clean-bound tests now fail under it.
- **N1 to N7 (recording only; flag, not refuse):** which closed word is recorded when two conditions fail
  together; a present but non-list source field stays on the old path (the stricter reading; the sealed
  writer always writes a list); a manifest member that is a roster reference under an unrecognised role
  fails the screen instead of counting as lost (stricter than item 3, cannot pass a drifting window);
  `campaign_sources_problem` can carry an evaluator word outside the erratum's closed list when the
  re-derivation itself fails (the window is removed in every such case); the rehearsal comparison is
  skipped unless its environment variable is set, so a gate record must quote an executed run.

## The independent executing review (Opus 5.5)

Item by item (0(a) to 0(f), 1 to 8, the gate): each implemented where the fix seat says and matching the
text. A real-shape check on the open rehearsal (counts only): a hazard root, 9 manifests all schema v2, no
supersession row, all 7 invoked references in the roster at their slot, all 35 invoked members with one
directory, the plan's t0 at top level; so items 0(b), 0(e), 0(f), 1 and 3 would not refuse a real window by
accident.

Mutation probes: 67, on scratch copies. 52 were killed by a test. Of the 15 that survived, 7 change no
outcome (a second check returns the same result) and 8 are the test gaps below.

- **S1** item 5 (the same gap as F1). **S2** item 6: `midpoint_lost` was tested only where it is true.
  **S3** item 7(b): hash equality was tested for the config file only, not the metadata or the summary, nor
  an unreadable file. **S4** item 3: a member whose role and position disagree was tested only in a window
  that failed for another reason as well. All four: the program is right, a test was missing; the reviewer
  wrote each test and verified it against the mutant.
- **Notes (recording only):** N1 present non-list source values untested; N2 word order; N3 non-closed
  words in `campaign_sources_problem`; N4 a `blocked_before_invoke` spare can be named in the loss list
  without entering any count; N5 the equivalent mutants; N6 a round-2 edit to `HarvestCheckoutTests`
  replaced an independent `git status` with the program's own captured one, needed only for an in-tree
  scratch directory (reverted in round 4); N7 the rehearsal comparison is opt-in and is not vacuous (four
  deliberate changes each made it fail); N8 no test drives a governed recovery through the whole `harvest()`
  entry point, only through the screen stage.
- The other edits to existing tests are justified by the text: three fixtures with no source list and no
  governed t0 now expect `recovery_predates_erratum`.

## The suite (lane tree at `d435547e2`, about 62 minutes while the review and the cold pass were running)

| Shard | Modules | Tests | Failures | Errors |
|---|---|---|---|---|
| 1 | 65 | 1701 | 3 | 0 |
| 2 | 65 | 1468 | 0 | 0 |
| 3 | 66 | 1383 | 0 | 0 |
| 4 | 65 | 1998 | 0 | 1 |
| 5 | 64 | 1811 | 2 | 0 |
| 6 | 65 | 1530 | 1 | 0 |

`tests.test_calibration_exits`: 48 tests, OK. `tests.test_calibration_writer_crash_matrix`: 20 tests, OK.
`git status --porcelain` after the run: 0 lines.

The seven failing tests, each run again alone afterwards:

- `tests.test_sample_quiet_predicate_evidence` (3, fixed wall-clock budgets under load): 96 tests, OK alone.
- `tests.test_harvest_b5_window.WorkerPoolTests` (1 error, a worker pool under load): OK alone.
- `tests.test_v5_s1_qualification` (1, a 5-second budget under load): 23 tests, OK alone.
- `tests.test_repin` (1): fails on every harvest lane by construction, alone as well; it compares
  `joulewise/whole_window.py` with the digest the sealed inventory holds, and the lane's copy is not the
  sealed one. The same failure is in the gate record of the second pin.
- `tests.test_analysis_integration`, `test_campaign_provenance_aggregation_call_site_fence` (1): a real
  consequence of the change. The test counts the production call sites of the catalog reader, and the
  harvest now has one (Erratum 2 item 1). The expected counts were updated in `067f4deab` with a comment
  naming the reason; the test still fails on any further call site.

## Findings and their disposition

| Finding | Disposition |
|---|---|
| F1 / S1, S2, S3, S4 (tests assert too little) | fixed, tests only (rounds 3 and 4) |
| The call-site fence | fixed, tests only (round 3) |
| N6 (a weakened provenance test) | fixed: the hunk is reverted (round 4) |
| Reviewer N1, N4 (untested recording cases) | tests added (round 4) |
| Word precedence; non-closed words on a failed re-derivation; stricter handling of a mislabelled roster reference; the opt-in rehearsal test; no end-to-end governed test | flag, not refuse: recording only, no fix round. The first governed harvest that takes this path is its own end-to-end run, and its record names the path taken |
| Item 9 of the erratum (the claim consumer) | deferred to lane L9-NEG8, before any claim is computed, as the erratum says |

No finding touches a number: no blocker from either pass, so no delta re-audit of production code was
needed after `d435547e2`; rounds 3 and 4 change tests only.

## Final state of the lane, and the pin

Lane head `0699abbb0881ce64b39c46ba07de568cc3848260` (pushed). Since the reviewed commit `d435547e2` only three
test files changed (`tests/test_analysis_integration.py`, `tests/test_harvest_b5_sources.py`,
`tests/test_harvest_b5_window.py`); the two program files are byte for byte those the cold pass and the
review read. `git diff --name-only be6525e5a 0699abbb0` lists, outside `tests/`, only
`joulewise/b5/harvest.py` and `joulewise/whole_window.py`. The head descends from the claim head
`c27485347`.

Program file digests at the pin: `joulewise/b5/harvest.py`
`96edd7ec6d57102060bef28c61561597d1c8144c412f6eb99d7d6d4cd0e9d463`; `joulewise/whole_window.py`
`2e03abc8b90088401df9fd86b511dcb783e4a67913e49ac441e326caa603b86b`; `scripts/harvest_b5_window.py`
`88ac1164e729691e4db249b77ebbd17072dbcd3f514499840a56f56576d66d45` (unchanged from both earlier pins).

Run by the magistrate at the final head, on a separate worktree, nothing else running:

- `tests.test_harvest_b5_sources`: 55 tests, OK.
- `tests.test_harvest_b5_window`: 205 tests, OK (513 s).
- At `067f4deab` (the program files are the same): `tests.test_analysis_integration` 116 tests OK,
  `tests.test_neg8_survivors` 89 tests OK, `tests.test_neg8_corpus_cap` 19 tests OK.
- The rehearsal comparison, `B5_REHEARSAL_COMPARE=1 … -m unittest tests.test_harvest_b5_rehearsal_compare`:
  `Ran 1 test in 1.359s`, `OK`, not skipped; `rehearsal_derived_byte_identity PASS`,
  `rehearsal_withheld_byte_identity PASS`, `rehearsal_emitted_flags_equal PASS`,
  `rehearsal_archived_derived_byte_identity PASS`, 4 derived records, 7 recorded reductions. The rehearsal is
  `/Users/edr/night-archive/gate-prune/rehearsal-real/corpus18-20261009T1949Z`, whose verdict records its
  sources.
- The F1 mutation (item 5's clause removed) on a scratch worktree: both clean-bound tests fail; restored.

The suite's logs: `/Users/edr/night-archive/b5-consults/beta-a1/fix/suite-d435547e2/`.

The program was not run over any governed attempt's bytes, and no seat that worked on it read a
claim-window energy. The gate constant in the program, `ERRATUM_2_ADMITTED_AT = "2026-10-10T16:30:00Z"`
(epoch 1791649800), equals the line in Addendum 3 step 1.

Pinned by Addendum 3 step 2 of the seal record: `B5-HARVEST-PIN: 0699abbb0881ce64b39c46ba07de568cc3848260`.
