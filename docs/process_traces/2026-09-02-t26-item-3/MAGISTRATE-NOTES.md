# T26 cold-gate item 3 (T-0 600 s liveness bound) — magistrate notes for the PR gate

Lane: install of T26 cold-gate verdict item 3, the T-0 600 s liveness bound.
Branch `feat/2026-09-02-t26-liveness`; PR #274.
Files 01–15 in this directory are the seat briefs, the sealed reports, the
bench texts, and the magistrate's delta disposition, in gauntlet order.

## Gauntlet record

| Round | Seat (model, effort if stated in the brief `EFFORT:`) | File | Audited head (as the brief names it) | Verdict |
| --- | --- | --- | --- | --- |
| Landing | sol (194); brief states no `EFFORT:` | 01, 02 | "@ 6075389a (main)" | envelope `"status": "blocked"`, `"completion": "partial"` |
| Refute, contract lens | luna (211); brief states no `EFFORT:` | 03, 04 | no single head sha named; brief says "detached at the head of branch `feat/2026-09-02-t26-liveness`, two commits over main 6075389a: Sol 194's landing `73fe1459` and one magistrate fixture commit" | no `VERDICT:` line in the report; envelope `"status": "findings"`, `"completion": "complete"` |
| Refute, execution lens | terra (212); brief states no `EFFORT:` | 05, 06 | — (brief says "DETACHED at the head of branch `feat/2026-09-02-t26-liveness`"; names no sha) | no `VERDICT:` line in the report; envelope `"status": "findings"`, `"completion": "complete"` |
| Refute, physics / causality lens | sol (213); brief states no `EFFORT:` | 07, 08 | no single head sha named; brief says "head = Sol 194 landing + one magistrate fixture commit over main 6075389a" | no `VERDICT:` line in the report; envelope `"status": "findings"`, `"completion": "complete"` |
| Fix round 1 | sol xhigh (224) | 09, 10 | "@ e40e7502" | envelope `"status": "clean"`, `"completion": "complete"` |
| Bench texts (drafted, **NOT YET APPLIED** — applied after `feat/2026-09-02-t26-install` merges) | magistrate (bench) | 11, 12 | — | — |
| Delta re-audit 1 | terra xhigh (229) | 13, 14 | "@ fea89b72" | `VERDICT: BLOCKER 1` |
| Magistrate disposition on terra 229 | magistrate | 15 | fea89b72 | — (disposition record; see the file) |
| Bench | magistrate (bench) | commit `4cf4346f` (below) | — | — |

## Bench commit (from `git show --stat`)

`4cf4346f` — "T26 item 3 delta (terra 229 DOC-ADDITIVITY-01): restore RF-04/RF-08
rows verbatim — the F-5 grep's '5 s' matched '0.5 seconds' (false positive), not
live 5 s policy; rewording a ruled table row to silence a grep is out of scope"

```
 .../2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md   | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)
```

## Commits on this branch

`git -C /Users/edr/code/JouleWise-wt-t26-b log --oneline main..HEAD`

```
4cf4346f T26 item 3 delta (terra 229 DOC-ADDITIVITY-01): restore RF-04/RF-08 rows verbatim — the F-5 grep's '5 s' matched '0.5 seconds' (false positive), not live 5 s policy; rewording a ruled table row to silence a grep is out of scope
fea89b72 T26 item 3: fix round 1 on the 600 s liveness landing (luna 211 / terra 212 / Sol 213 refuters)
e40e7502 T26 item 3 fixture (bench): sample EVIDENCE horizon R1 + 6 h + 1 s sits inside the ruled 600 s liveness window; sample ARM keeps 10**30 (arm consumption checked against the live monotonic clock)
73fe1459 T26 item 3 (Sol 194): 600 s liveness conjunct in _clock_probe_predicate_passes (ordinary monotonic clock; 11 post-R1 _fresh_probe sites × 45 s + 105 s = _MIN_IDLE_NS), boundary regressions at arm, issuance, and rehearsal sites, §6.3 dated disposition
```
