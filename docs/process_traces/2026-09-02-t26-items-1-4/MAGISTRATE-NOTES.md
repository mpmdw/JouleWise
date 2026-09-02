# T26 cold-gate items 1 and 4 (install) — magistrate notes for the PR gate

Lane: install of T26 cold-gate verdicts items 1 and 4 plus the D-170 entry, and
the Q1/Q2 process-rule install.
Branch `feat/2026-09-02-t26-install`; PR #273.
Files 01–19 in this directory are the seat briefs and the sealed reports, in
gauntlet order.

## Gauntlet record

| Round | Seat (model, effort if stated in the brief `EFFORT:`) | File | Audited head (as the brief names it) | Verdict |
| --- | --- | --- | --- | --- |
| Landing | sol (193); brief states no `EFFORT:` | 01, 02 | "@ 300ca7f2" | envelope `"status": "findings"`, `"completion": "complete"` |
| Refute, contract lens | luna (209); brief states no `EFFORT:` | 03, 04 | "head 2d24ef70" | no `VERDICT:` line in the report; envelope `"status": "findings"`, `"completion": "complete"` |
| Refute, execution lens | opus (210); brief states no `EFFORT:` | 05, 06 | "DETACHED at 2d24ef70" | no `VERDICT:` line and no ```json envelope in the report (Opus seat, prose report); it ends "No fixes applied." |
| Cold gate | custodied on `main` — not copied here | `docs/process_traces/2026-09-02-coldgate-dx-t26a/`, §B1–B4 | — | see that directory's `MAGISTRATE-RULING-coldgate-dx-t26a.md` |
| Fix round 1 | luna xhigh (226) | 07, 08 | "@ 2d24ef70" | envelope `"status": "findings"`, `"completion": "complete"` |
| Bench | magistrate (bench) | commit `d8451daa` (below) | — | — |
| Delta re-audit 1 | sol xhigh (230) | 09, 10 | "@ d8451daa" | `VERDICT: SHOULD-FIX 2` |
| Bench | magistrate (bench) | commit `f84be217` (below) | — | — |
| Pre-merge fresh pass | terra high (231) | 11, 12 | "@ f84be217" | `VERDICT: SHOULD-FIX 1` (F3: B1 existence check is worktree-based, not HEAD-based) |
| Magistrate disposition on terra 231 | magistrate | 13 | f84be217 | F3 ACCEPTED AS LIMITATION, not fixed — reasons in the file (CI clean checkout ≡ HEAD; D-161; rule-11 second-fix trigger not justified by materiality) |
| Opus counter-review (gate item 6) | Opus 5 (Agent tool, read-only) | 14, 14b | 10845c14 | `SHOULD-FIX 5`, `NIT 10` + one observation; disposition in 14b (SF1–SF5, NIT1–5, NIT9 accepted; NIT6/7/8/10 recorded; observation carried to the next cold-gate packet) |
| S9 rows draft (SF1 kernel half) | sol high (236), detached worktree | 15 (brief, report, draft JSON) | 10845c14 | envelope `"status": "clean"`, `"completion": "complete"`; seven rows drafted — two of them (S9-04, S9-12) turned out to pre-exist; see the dated addendum on the cold-gate ruling |
| Fix round 2 (Opus findings) | terra xhigh (235) | 16 (brief, report) | "@ 10845c14" | envelope `"status": "clean"`, `"completion": "complete"`; wrapper `run_status=SCOPE_VIOLATION rc=77 scope_action=failed_preserved` caused ONLY by the magistrate's untracked files 14/14b in the worktree (`unowned_dirty`); the seat's edits are all inside its six-file scope and were used as landed |
| Bench | magistrate (bench) | commit `c05cf181` (below; the luna 238 cures + custody 17/17b land as `162049bd`) | — | kernel: five S9 rows registered, D-170 dep applied in place to GAMMA-UNIT-ROSTER-GUARD-01 / L10-SACRIFICIAL-REHEARSAL-SCHEDULE-01, R7F-DX-PROSE-SCAN-01 registered (126 tasks); comment chain in `tests/test_gen_state.py` reconstructed from kernel commit counts; M6c regex + "no start dependency" mutant made multi-row; dated addendum on the cold-gate ruling (B4 site correction, PD-1 evidence) |
| Delta re-audit 2 | luna xhigh (238) | 17 (brief, report), 17b | "@ c05cf181" | `VERDICT: SHOULD-FIX 2` + 1 nit (date gloss names the wrong date source; addendum evidence block not replayable; stale WAVE-ROWS provenance) — all three cured at the bench per 17b; execution lens clean (luna's own mutants), kernel lens clean |
| Final-head fresh pass | sol high (241), detached worktree | 18 (brief, report), 18b | "@ 162049bd" | `SHOULD-FIX 2` + 1 nit (stale `file:line` anchors in the process-rules README; incomplete bench-commit ledger in this file; wrong packet basename in the process-rules ruling) — all three replicated and cured at the bench per 18b (durable anchors, ledger completed, dated addendum) |
| Delta re-audit 3 (§5 pass over the Sol 241 cure commit) | luna high (242), detached worktree | 19 (brief, report) | "@ b2b26c86" | `VERDICT: CLEAN` (envelope `semantic_status=clean`, `completion=complete`, wrapper `run_status=OK rc=0`): all three cures replicated, ledger/stat blocks match, addendum replays, `test_docs_freshness` + `test_gen_state` + `gen_state.py --check` pass. The commit landing file 19 is custody-only. |

## Bench commits (from `git show --stat`)

`d8451daa` — "T26 items 1+4 bench: install the B2 dependency, D110 reconcile row,
evidence[1] correction; scan boundaries"

```
 TASK_QUEUE.md                  |  6 +++--
 docs/process/state_kernel.json | 52 ++++++++++++++++++++++++++++++++++++++++--
 tests/test_docs_freshness.py   | 28 ++++++++++++++++++-----
 tests/test_gen_state.py        |  4 +++-
 4 files changed, 79 insertions(+), 11 deletions(-)
```

`f84be217` — "T26 items 1+4 delta (Sol 230 F1/F2): Executed-evidence citation must
be repo-relative (absolute or '..' escape rejected, mutation-proven);
T26-RULING-INSTALL-01 acceptance names the single ruled B2 dependency, not 'four'"

```
 TASK_QUEUE.md                  |  4 ++--
 docs/process/state_kernel.json |  2 +-
 tests/test_docs_freshness.py   | 28 +++++++++++++++++++++++++++-
 3 files changed, 30 insertions(+), 4 deletions(-)
```

`10845c14` — custody only: gauntlet files 01-13 + this notes file.

`c05cf181` — "T26 items 1+4 fix round 2 (Opus counter-review, terra 235) + bench"
(terra 235's six-file scope + the kernel/gen_state/addendum bench work + custody 14-16)

```
 TASK_QUEUE.md                                      |  20 +-
 docs/agent_playbook.md                             |   2 +-
 docs/contracts/bridge_protocol.md                  |  29 +-
 docs/decision_log.md                               |  24 +-
 docs/process/state_kernel.json                     | 277 ++++++++++-
 .../MAGISTRATE-RULING-T0-UNATTENDED.md             |   2 -
 .../MAGISTRATE-RULING-coldgate-dx-t26a.md          |  51 ++
 .../14-opus-counter-review.md                      | 527 +++++++++++++++++++++
 ...b-magistrate-disposition-opus-counter-review.md |  35 ++
 .../15-s9-kernel-rows-draft.json                   | 306 ++++++++++++
 .../2026-09-02-t26-items-1-4/15-s9-rows-brief.md   |  93 ++++
 .../15-sol-236-s9-rows-report.md                   | 138 ++++++
 .../16-fix-round-2-brief.md                        | 149 ++++++
 .../16-terra-235-fix-round-2.md                    | 160 +++++++
 .../2026-09-02-t26-items-1-4/MAGISTRATE-NOTES.md   |   6 +-
 tests/test_docs_freshness.py                       |  87 +++-
 tests/test_gen_state.py                            |  21 +-
 17 files changed, 1873 insertions(+), 54 deletions(-)
```

`162049bd` — "T26 items 1+4 delta 2 (luna 238) cures at the bench" (C1 date
gloss, K1 replayable census, K2 provenance; custody 17/17b)

```
 docs/contracts/bridge_protocol.md                  |   5 +-
 .../MAGISTRATE-RULING-coldgate-dx-t26a.md          |  15 +--
 .../2026-09-02-t26-items-1-4/17-delta-2-brief.md   |  56 +++++++++++
 .../17-luna-238-delta-2.md                         | 109 +++++++++++++++++++++
 .../17b-magistrate-disposition-luna-238.md         |  21 ++++
 .../2026-09-02-t26-items-1-4/MAGISTRATE-NOTES.md   |   3 +-
 6 files changed, 200 insertions(+), 9 deletions(-)
```

The commit that lands the Sol 241 fresh-pass cures (files 18/18b, this
ledger, the process-rules README anchors, the process-rules ruling addendum)
could not name its own hash when it was written; it landed as `b2b26c86`,
and the luna 242 custody landed as `ad22ec83` (both recorded below in the
commit that carries the terminal review, which likewise cannot name itself).

`b2b26c86` — "T26 items 1+4 fresh pass (Sol 241) cures at the bench" (F1
durable anchors, F2 ledger, F3 packet-basename addendum; custody 18/18b)

```
 .../MAGISTRATE-RULING-process-rules.md             |   8 +
 .../2026-09-02-process-rules/README.md             |   4 +-
 .../18-fresh-pass-brief.md                         |  42 ++++
 .../18-sol-241-fresh-pass.md                       | 212 +++++++++++++++++++++
 .../18b-magistrate-disposition-sol-241.md          |  38 ++++
 .../2026-09-02-t26-items-1-4/MAGISTRATE-NOTES.md   |  53 +++++-
 6 files changed, 353 insertions(+), 4 deletions(-)
```

`ad22ec83` — custody only: file 19 (luna 242 delta re-audit 3, CLEAN) + the
notes row.

```
 .../2026-09-02-t26-items-1-4/19-delta-3-brief.md   |  32 +++++
 .../19-luna-242-delta-3.md                         | 138 +++++++++++++++++++++
 .../2026-09-02-t26-items-1-4/MAGISTRATE-NOTES.md   |   3 +-
 3 files changed, 172 insertions(+), 1 deletion(-)
```

## Magistrate terminal review (gate item 12) — merge candidate `ad22ec83`

Read at the bench on 2026-09-02, after luna 242 returned CLEAN over
`b2b26c86` and `ad22ec83` added only custody. The review covers the whole
branch-vs-main diff outside `docs/process_traces/`:

```
$ git -C /Users/edr/code/JouleWise-wt-t26-a diff --stat main...ad22ec83 -- . ':!docs/process_traces'
 TASK_QUEUE.md                     |  32 +-
 docs/agent_playbook.md            |   4 +
 docs/contracts/bridge_protocol.md |  30 ++
 docs/decision_log.md              | 145 +++++++-
 docs/process/state_kernel.json    | 466 +++++++++++++++++++++++++-
 scripts/gen_state.py              |  30 ++
 tests/test_docs_freshness.py      | 689 +++++++++++++++++++++++++++++++++++++-
 tests/test_gen_state.py           |  76 ++++-
 8 files changed, 1452 insertions(+), 20 deletions(-)
```

What was read and the judgment on each:

- `scripts/gen_state.py` — the only production-code change: a satisfied
  `kind: decision` dependency must carry `evidence.path` matching
  `tests/[A-Za-z0-9_/]+\.py` and an `evidence.label` naming a `test_*`
  method defined in that file. Fail-closed, bounded to the new dependency
  kind, no effect on any existing row (the `--check` and the 126-task
  regeneration are byte-stable). Sound.
- `docs/decision_log.md` — status set closed and glossed; the `open
  (installs via <TASK-ID>)` form defined before first use; D-170 records the
  four AMEND verdicts by pointer and quotation (no reinterpretation), names
  the three installing branches, and stays OPEN until all three land. The
  D-150a/D-150b index rows are reordered to match body order only. Sound.
- `docs/contracts/bridge_protocol.md` §1 clause map + §10 ONE-home row;
  `docs/agent_playbook.md` M0 line — pointers only, each names its home.
  Sound.
- `TASK_QUEUE.md` — regenerated surface: the D-170 hard-start dependency now
  appears on `V5-TRANSACTION-01`, the two pre-existing S9 rows and the five
  new S9 rows; `T26-RULING-INSTALL-01` reads `PARTIAL; READY; GATES close:
  D-170`; `R7F-DX-PROSE-SCAN-01` and the two Ed items E1/E2 registered.
  Matches the kernel (`gen_state.py --check` exit 0 is item 7 on the
  ledger). Sound.
- `docs/process/state_kernel.json`, `tests/test_docs_freshness.py`,
  `tests/test_gen_state.py` — reviewed at each bench commit as they were
  written (`d8451daa`, `f84be217`, `c05cf181`, `162049bd`) and re-audited
  by Sol 230, terra 231, Opus (14), luna 238, Sol 241, luna 242; not re-read
  line by line here. The prospective S1/S2 shape tests and the census
  `assertIn` form (terra 235 SF2) are the ones that bit on integration and
  were confirmed passing on the integration tree (item 9).

Verdict: MERGE at `ad22ec83`. No finding. Open follow-ups carried by the
kernel, not by this branch: `R7F-DX-PROSE-SCAN-01` (registered here),
`D110-MINT-DEP-RECONCILE-01` (Ed call, NIT8), and the post-merge kernel
batch that moves D-170 to `adopted` once the liveness and gate-ledger
branches land.

## Commits on this branch

`git -C /Users/edr/code/JouleWise-wt-t26-a log --oneline main..HEAD`

```
# executed at 162049bd (before the Sol 241 cure commit)
162049bd T26 items 1+4 delta 2 (luna 238) cures at the bench: S1 date gloss names the dated directory component (C1); addendum census re-executed replayably (K1); S9-04/S9-12 provenance = commit d01fd4c5, WAVE-ROWS:18 named stale (K2); custody files 17/17b
c05cf181 T26 items 1+4 fix round 2 (Opus counter-review, terra 235) + bench: header-indexed clause-map shape test with cell-count contract (SF3), census assertIn (SF2), D-170 cites the dated addendum (SF5), ruling paths/glosses/NOT PINNED scope (NIT1-3), duplicate T-0 amendment paragraph removed (NIT4), evidence-pointer grammar in How-To (NIT5), accepted gloss (NIT9); bench: five S9 rows + R7F-DX-PROSE-SCAN-01 registered, D-170 hard/start/pending dep applied in place to the two pre-existing S9-04/S9-12 rows (126 tasks), test_gen_state comment chain reconstructed, multi-row mutants; dated addendum on the cold-gate ruling (B4 site correction); custody files 14-16
10845c14 t26-items-1-4 trace: gauntlet files 01-13 (briefs, sealed seat reports 193/209/210/226/230/231, terra 231 disposition) + MAGISTRATE-NOTES
f84be217 T26 items 1+4 delta (Sol 230 F1/F2): Executed-evidence citation must be repo-relative (absolute or '..' escape rejected, mutation-proven); T26-RULING-INSTALL-01 acceptance names the single ruled B2 dependency, not 'four'
d8451daa T26 items 1+4 bench: install the B2 dependency, D110 reconcile row, evidence[1] correction; scan boundaries
d243445d Merge branch 'main' into feat/2026-09-02-t26-install
1d254bb1 T26 items 1+4: fix round 1 on the install landing (dx/t26-a cold gate B1-B4)
2d24ef70 Process-rules cold gate 2026-09-02 (terra 201): Q1 clause map installed in bridge_protocol §1 (+§10 row, M0 pointer, S1 prospective shape test, S2 pin), Q2 cross-artifact equality exhibit as D-160 amendment, D-170 custody paragraph, trace README
deafe328 Custody: cold gate 2026-09-02 on the two proposed process rules (packet, sealed cold-Fable 196 + Opus refuter 197, magistrate ruling with executed evidence)
b180b426 decision index: order D-150/D-150a/D-150b rows to match body order (exposed by the D-\d{3}[a-z]? widening)
38a7de0a T26 items 1+4 (Sol 193): D-170 entry + D-118/D-160 pointers, How-To closed status set + 'open (installs via)' form, four docs_freshness tests, T-0 Horizon AMENDED line, M0 line, trace README
300ca7f2 T26-RULING-INSTALL-01: kernel rows for installing the uninstalled T26 cold-gate verdicts (+ Ed items E1/E2, transaction decision dependency)
```
