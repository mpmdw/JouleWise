# Lane L9 (the block-5 analysis code): the design phase is finished; the rulings come next

Magistrate activation 76a41dde (Opus 5.5, headless), 2026-10-12, after block 5 collection closed
(`seal2-gamma-a1-window.md`). No repository code was written. No claim-window energy and no restricted file
was opened by this session or by any seat (each seat's report says so; each brief carried the fence).

## What was found

The design workflow of 2026-10-07 had stopped half-way: fifteen map files and the NEG-8 decision
(`L9NEG8_DESIGN.md`) existed; the architect's `L9_DESIGN.md`, which RUN_STATE named as the build's source,
had never been written. The worktree `/Users/edr/code/JouleWise-wt-l9` was removed on 2026-10-11 with the
other clean worktrees; the local branch `lane/2026-10-07-l9-analysis` holds no lane commit (it is contained
in main) and was never pushed.

## What was done (papers under `/Users/edr/night-archive/gate-prune/wave-1007b/l9/`)

| Step | Seat | File | sha256 |
|---|---|---|---|
| Architect | Opus 5.5, with eight read-only Sonnet 5.5 seats checking the maps against today's code | `L9_DESIGN.r0.md` (2,278 lines) | `ebee8d10f341a3954b44bacdfe85e96818bbd7a9eac122fd4a0d27484a074986` |
| Critic, plan conformance | Opus 5.5 | `critic-conformance.md` | in the directory |
| Critic, numerics | Fable 5.1 | `critic-numerics.md` | in the directory |
| The one revision | Opus 5.5 | `L9_DESIGN.md` (2,943 lines), `REVISION.md` | `3465acf918bc920ff3eb9f0b81f173c8c545650487c18f2304e7ef1158b32e7d` |

- The architect's audit of the 10-07 maps against main and the sealed texts: 50 stale statements, 23 of them
  consequential. The three that matter most: (1) every block-5 stored verdict reads failed (Erratum 1, and
  Erratum 3 item 9 on governed windows), so finalization, the mint and both validator vetoes refuse every
  window as the code stands; (2) one archive or one ledger for several windows is inadmissible (Erratum 3
  item 10(i)), and BETA's and GAMMA's consumers must evaluate the calibration bracket themselves with the
  scope that exists only on the unmerged harvest lane; (3) the archives the pins wrote are not the shape
  main's harvest writes. Main's registration and plan are byte-identical to the seal commit `be6525e5a`.
- Conformance critic: 1 blocker (attempt selection could not read the not-claim-usable attempts it must
  read), 19 should-fix, 9 notes; 123 obligations listed, 33 missed; about 76 code citations checked, 4 wrong.
- Numerics critic: no blocker, 5 should-fix, 10 notes; every worked example recomputed digit for digit; the
  small-sample factor g(n) is 1.5, 1.3416, 1.2247, 1.1339, 1.0607 and 1 at n = 5 to 10.
- Revision: all 25 blocker and should-fix findings confirmed against text or code and applied; none declined.
  The stage graph is unchanged (twelve stages, S0 to S11).

## What needs a ruling before code (section 8 of `L9_DESIGN.md`)

A cold judge (a fresh Fable 5.1 session with no loop context), because each changes a number, a drift
allowance, or which windows or members can bear a claim:

- J1: which conditions of a stored failed verdict a claim consumer may set aside (member conditions, adapter
  continuity, and the membership condition that Erratum 2's recovered-source rows always carry). Without an
  answer no window yields a number: BETA and GAMMA each lost members.
- J2: whether a reference run whose config bytes are not its registered config is lost.
- J3: whether a science member whose custody records disagree is removed, which would need a new harvest pin.
- J4: whether the harvest stays exactly as pinned for the one-predicate work (no re-harvest of the three
  analysed windows).
- J5: whether the comparative floor carries the floor window's drift allowance (the plan's sentence at lines
  133 to 135 says no; the code and the 10-09 erratum's reading say yes).
- J6: the scope of Erratum 3's sensitivity bound. J7: the ledger copy's digest that `harvest.json` does not
  record. J8: one leave-one-out case that can change a ceiling.

Settled by the sealed text (the design now follows it): eight items, T1 to T8. The orchestrator's: sixteen
items, O1 to O16, each with a recommendation; O2 is the two-seat design round (Sol 6.1 and Fable 5.1) that
plan line 744 requires on the design's sections 3.5 and 4.5 before stage S3's code.

## One point this session adds for the judge's packet

The revised attempt reader (`L9_DESIGN.md` section 3.2) has the analysis program read
`derived/exclusions.json` and `derived/window_flags.json` of every attempt. The magistrate brief (section 6,
seal gate ruling SG-12) says nobody opens those two files before the release event, "except a program that
prints structure only". Whether attempt selection run before the release event is such a program, or must
wait for the release, is put to the judge with J1.

## Not verified

Nothing was executed against the repository; every code statement in the design is a reading. The revised
document was not re-read end to end by its reviser. `REVISION.md` ends with the reviser's own list.

## Next action

1. Build the judge packet from section 8.1 of `L9_DESIGN.md` (J1 to J8 and the point above) and convene the
   cold gate. J1 first if they must be split.
2. Consult O2. Decide O1 and O3 to O16 and record them.
3. Recreate the worktree for branch `lane/2026-10-07-l9-analysis` from main and build stage S0; then the
   stages in the order of section 5, through the full merge gates with a cold Fable 5.1 pass.
