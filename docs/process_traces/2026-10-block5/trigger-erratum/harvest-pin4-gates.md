# The harvest program for attempts governed by Erratum 3: gate record

Magistrate activation bab1c330 (Opus 5.5, headless), 2026-10-11. Structure only. The seats' reports are
beside this file (`sol-impl.md`, `sol-tests2.md`, `FABLE-pass.md` with its charge, `REVIEW.md`); logs and
probes are under `/Users/edr/night-archive/b5-consults/beta-a5-stale/` on the measurement Mac. Clock times in
the records of this activation written before 10:00 PDT are approximate (some are up to twenty minutes late).

The change is the desk side of Erratum 3 (`ERRATUM.md` beside this file, sections 4 and 5; cold ruling
`RULING.md`): the bracket evaluation takes an argument `trigger_scope`; for an attempt whose plan t0 is later
than `2026-10-11T17:00:00Z`, three events elsewhere in the calibration ledger are recorded and do not fail the
window's bracket, and `harvest.json` gains the object `calibration_bracket`. Branch
`lane/2026-10-11-harvest-trigger-scope`, cut from the third harvest pin
`0699abbb0881ce64b39c46ba07de568cc3848260`. Outside `tests/` it changes `joulewise/b5/harvest.py` and
`joulewise/calibration_bracketing.py`. Like the earlier harvest lanes it is not merged into main.

## Who did what

| Step | Seat | Result |
|---|---|---|
| Implementation | Sol 6.1, effort xhigh (`sol-impl.md`), commit `e4b4145a0` | items 0 to 8 of section 4, each with tests; 497 targeted tests OK (29 skipped); one question on item 6 |
| Cold final pass | Fable 5.1, new session, own worktree (`FABLE-pass.md`), on `0699abbb0..e4b4145a0` | last line `PASS`; no blocker; one should-fix scoped to GAMMA (F3); six notes |
| Independent executing review | Opus 5.5 agent that wrote none of it, own worktree (`REVIEW.md`) | `APPROVE WITH FIXES (S1, S2, S3)`; no blocker; three test gaps; twelve notes |
| Whole suite on the lane's tree | the CI shard runner, six shards and the two exclusive modules, non-venv Python 3.13, at `e4b4145a0` | see "The suite" |
| Round 2, tests only | Sol 6.1, effort high (`sol-tests2.md`), commit `b039c0257` | the reviewer's three tests, each shown to fail under its mutation |

## The cold pass (Fable 5.1)

Executed by the reviewer: the lane's new module (26 tests, OK); 17 mutation probes on scratch copies, every
one detected by a test; the sealed-identity probe against the pinned source (SHA-256 `ddb7db11…4037`); the
epoch of the constant (1791738000 is `2026-10-11T17:00:00Z`); the live calibration ledger's shape (row 456
carries attempt 3's session id, so the own-session comparison has real data on both sides).

Its statement: no path was found by which a governed bracket passes that the admitted text would fail; every
check of item 4 is in place, unweakened and in the sealed order; with `trigger_scope` omitted or `"sealed"`
nothing differs from the pinned program; an attempt with t0 at or before the constant cannot reach the new
scope, and the harvest's one call is the only caller that passes it.

## The independent executing review (Opus 5.5)

Item by item (0 to 8): each implemented where the builder says and matching the text. Its own differential,
with the pinned file loaded as a separate module: equal results on 752 evaluator inputs and 28 wrapper inputs,
early refusals and the real stale ledger included. 38 mutants: 33 killed, 2 equivalent, 3 test gaps (S1, S2 and
one inert with a single judged epoch). A real-shape probe on the live ledger, with candidates rebuilt from
ledger rows because its blinding rule kept it out of the capture directories: 14 valid finalized captures;
bound to attempt 5's session under the new scope it records the systematic trigger, the doubling count 41 of
48 and the sequence list `[456]`. It wrote the pre-arm snippet (its section 3.3).

## The suite (lane tree at `e4b4145a0`, about 80 minutes while the review and the cold pass were running)

| Shard | Modules | Tests | Failures | Errors |
|---|---|---|---|---|
| 1 | 65 | 1795 | 3 | 0 |
| 2 | 65 | 1469 | 0 | 0 |
| 3 | 65 | 1559 | 2 | 0 |
| 4 | 66 | 1757 | 0 | 1 |
| 5 | 65 | 1676 | 0 | 0 |
| 6 | 65 | 1665 | 0 | 0 |

`tests.test_calibration_exits`: 48 tests, OK. `tests.test_calibration_writer_crash_matrix`: 20 tests, OK.
`git status --porcelain` after the run: 0 lines. The six failing tests, each run again alone afterwards:

- `tests.test_sample_quiet_predicate_evidence` (3, fixed wall-clock budgets under load): 96 tests, OK alone.
- `tests.test_harvest_b5_window.WorkerPoolTests` (1 error, a worker pool under load): OK alone.
- `tests.test_repin` (1): fails on every harvest lane by construction, alone as well (the lane's program
  files are not the sealed ones). The same failure is in the gate records of the second and third pins.
- `tests.hazards.test_refusal_allowlist` (1): a consequence of the change, and it stays failing on this
  lane. The test counts every `raise` on the window path against `configs/gates/hazard_refusals.json`. The
  two unlisted sites are the `ValueError` for an unknown `trigger_scope` value in the two functions, which
  item 1 of the admitted text requires ("any other value raises"); nothing else is unlisted, stale or
  miscounted. The allowlist is a file under `configs/`, which this lane may not change, and it describes the
  measurement clone's copy of the code, which is unchanged. The harvest passes one of two literals, so the
  raise is reached only by a programming error. Disposition below.

## Run by the magistrate

- The lane's new module at the final head `b039c0257`: `Ran 28 tests in 122.613s`, `OK`.
- The before/after comparison on the real rehearsal copy
  (`/Users/edr/night-archive/gate-prune/rehearsal-real/corpus18-20261009T1949Z`, not a claim window), two parts.
  (1) `B5_REHEARSAL_COMPARE=1 … -m unittest tests.test_harvest_b5_rehearsal_compare` at `e4b4145a0`: 1 test, OK,
  not skipped; the four lines `rehearsal_derived_byte_identity`, `rehearsal_withheld_byte_identity`,
  `rehearsal_emitted_flags_equal`, `rehearsal_archived_derived_byte_identity` all `PASS`. That test replays
  the drift screen. (2) For the function this lane changes: `rehearsal_bracket_dump.py` calls
  `calibration_bracket_for_bundles` exactly as the harvest does, over the rehearsal archive's ledger copy,
  terminal pin, binding and member list, once from the pinned desk checkout `0699abbb0` and twice from the
  lane (argument omitted; `"sealed"`). The three outputs are byte-identical (SHA-256 `73ad0a3a…f3b4`, status
  `passed`, freshness `fresh`, 34 members) and equal to the archive's own `withheld/bracket-evaluation.json`.
  A whole second harvest of the rehearsal was not run: `derived/exclusions.json` carries the harvest
  checkout's head and file list, which differ between any two pins by item 8(iii).
- The limited exploratory run of item 12 over BETA attempt 5's archived ledger copy, terminal pin and
  binding (`item12_bracket_only.py`, output `item12_beta-a5.out`; labelled exploratory; it changes no verdict,
  `claim_usable`, cause key or attempt history): 99 members passed to the evaluation; `"sealed"`: `failed`,
  `calibration_acceptance_bound_stale`, `stale`, the four new keys absent; `"window_evidence"`: `passed`, no
  reason, `fresh`, observed and recorded-only trigger `new_systematic_failure_challenges_preflight_screen`,
  doubling `{"count": 41, "threshold": 48}`, sequences `[456]`.
- The constant in the program, `ERRATUM_3_ADMITTED_AT_EPOCH_S = 1791738000`, equals the line
  `ERRATUM-3-ADMITTED-AT: 2026-10-11T17:00:00Z` of Addendum 4 step 1.
- The two stale-state fixtures (in `tests/test_harvest_b5_trigger_scope.py`): Erratum 2's recovery with a
  stored verdict that records no sources, governed: the list of window-removing codes is empty. The
  GAMMA-shaped window: the stale state adds `g3.recompute_failed` and `whole_window.not_passed`, both
  disclosed only; the three window-removing codes it shows come from gaps of the synthetic fixture, a fresh
  control carries the same three with equal payloads (the reviewer's S3).

## Findings and their disposition

| Finding | Disposition |
|---|---|
| Builder's question: `corpus_doubling` is null when an evaluation is refused before an authenticated count exists | ruled by the orchestrator: null (item 8 types the field `{...}|null`; no decision reads it); confirmed by the cold pass (F2) and the reviewer (section 7) |
| S1, S2, S3 (tests assert too little) | fixed, tests only (round 2, `b039c0257`) |
| F3 (cold pass): the real provenance checker and the sealed verdict writer were not run over a GAMMA-shaped window in the stale state | deferred to a named gate **before a governed GAMMA attempt is armed**: on the rehearsal copy with a ledger that holds a systematic capture of another session, run the sealed writer and the real checker and print the window-removing codes. It does not hold BETA: the G3 step runs only for a pack whose root holds `analysis_manifest_v3.json`, and of the three packs only GAMMA's does (checked in the clone). By reading, every outcome of that step is a disclosed code |
| `tests.hazards.test_refusal_allowlist` fails on the lane | flag, not refuse: by construction on a desk-only lane, as `tests.test_repin`; the two rows are added to the allowlist when this code reaches a sealed tree (the next block's registration) |
| F1 / N2: under the new scope `freshness.status` reads `stale` on every failed check of item 4, where the sealed word is `fresh` for some | flag, not refuse: representation; the bracket fails in every such case and no decision reads the word |
| N1: without a validated binding the four keys are written with empty lists | flag, not refuse; the harvest always passes a binding. The pre-arm run passes one and asserts it validated |
| F4, F6, F7, N3 to N6, N8 to N12 | recording only |
| N7: a byte comparison of a whole second harvest must exempt the checkout record | met by the two-part comparison above |
| Items 10 and 14 of the erratum (claim consumers; the sensitivity bound) | deferred to lane L9-BRACKET, before any claim is computed, as the erratum says |

No finding touches a number: no blocker from either pass, so no delta re-audit of production code was needed
after `e4b4145a0`; round 2 changes one test file.

## Final state of the lane, and the pin

Lane head `b039c0257d1b1d407ee9598222db3f78f6ad7beb` (pushed). Since the reviewed commit `e4b4145a0` only
`tests/test_harvest_b5_trigger_scope.py` changed; the program files are byte for byte those the cold pass and
the review read. `git diff --name-only 0699abbb0 b039c0257` lists `joulewise/b5/harvest.py`,
`joulewise/calibration_bracketing.py` and two paths under `tests/`. Against the claim head `c27485347`,
outside `tests/` and the three seal documents, the lane differs in `joulewise/b5/harvest.py`,
`joulewise/calibration_bracketing.py`, `joulewise/whole_window.py` and `scripts/harvest_b5_window.py`. The
head descends from the claim head.

Program file digests at the pin: `joulewise/b5/harvest.py`
`68d219478edb3d40a1d1a0a4cfd2fb7100421f09b5c8e681ec48c6acab0c73af`; `joulewise/calibration_bracketing.py`
`5474902deb5c3b834bffe11da6698f40216ba978248a8457f09db0077eaaf3ff`; `joulewise/whole_window.py`
`2e03abc8b90088401df9fd86b511dcb783e4a67913e49ac441e326caa603b86b` (unchanged from the third pin);
`scripts/harvest_b5_window.py` `88ac1164e729691e4db249b77ebbd17072dbcd3f514499840a56f56576d66d45` (unchanged
from all earlier pins).

The program was not run over any governed attempt's bytes (none exists), and no seat that worked on it read a
claim-window energy.
