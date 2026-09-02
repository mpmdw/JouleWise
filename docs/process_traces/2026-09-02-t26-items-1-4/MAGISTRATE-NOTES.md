# T26 cold-gate items 1 and 4 (install) — magistrate notes for the PR gate

Lane: install of T26 cold-gate verdicts items 1 and 4 plus the D-170 entry, and
the Q1/Q2 process-rule install.
Branch `feat/2026-09-02-t26-install`; PR #273.
Files 01–11 in this directory are the seat briefs and the sealed reports, in
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

## Commits on this branch

`git -C /Users/edr/code/JouleWise-wt-t26-a log --oneline main..HEAD`

```
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
