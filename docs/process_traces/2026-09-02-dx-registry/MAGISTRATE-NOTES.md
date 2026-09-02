# DX registry rows + round-7 artifact fence (R7F) — magistrate notes for the PR gate

Lane: DX registry / round-7 artifact fence (ruling 168a).
Branch `feat/2026-09-02-dx-registry`; PR #272.
Files 01–17 in this directory are the seat briefs, the sealed reports, and the
bench replay records, in gauntlet order.

## Gauntlet record

| Round | Seat (model, effort if stated in the brief `EFFORT:`) | File | Audited head (as the brief names it) | Verdict |
| --- | --- | --- | --- | --- |
| Landing | sol (174); brief states no `EFFORT:` | 01, 02 | "@ a63d45bd" | envelope `"status": "clean"`, `"completion": "complete"` |
| Refute | luna (189); brief states no `EFFORT:` | 03, 04 | "@ 2a6d3841" | envelope `"verdict": "NOT CLEAN"` |
| Fix round 1 | sol (191); brief states no `EFFORT:` | 05, 06 | "@ 2a6d3841" | envelope `"status": "clean"`, `"completion": "complete"` |
| Delta re-audit 1 | terra (198); brief states no `EFFORT:` | 07, 08 | "fix commit 3f1677b7 over 2a6d3841" | envelope `"verdict": "NOT CLEAN"` |
| Fix round 2a | sol xhigh (216) | 09, 10 | "@ 3f1677b7" | envelope `"status": "blocked"`, `"completion": "partial"` |
| Cold gate | custodied on `main` — not copied here | `docs/process_traces/2026-09-02-coldgate-dx-t26a/` | — | see that directory's `MAGISTRATE-RULING-coldgate-dx-t26a.md` |
| Fix round 2b | sol xhigh (225) | 11, 12 | "@ 781c8d78" | envelope `"status": "findings"`, `"completion": "complete"` |
| Delta re-audit 2b | terra xhigh (228) | 13, 14 | "@ 8efbb200" | `VERDICT: CLEAN` |
| Bench replay | magistrate (bench) | 15, 16 | 8efbb200 | — (raw replay/test output; no verdict line) |
| Pre-merge fresh pass | luna high (232) | 17, 18 | "@ c8ea9e95" | `VERDICT: SHOULD-FIX 1` — the one finding is on the SIBLING branch (`tests/test_check_gate_ledger.py` hard-required `TMPDIR`, a CI KeyError on `feat/2026-09-02-t26-gateledger`), cured there at c01c39bb; the c8ea9e95 delta itself: "No blocker or nit findings apply" |

## Commits on this branch

`git -C /Users/edr/code/JouleWise-wt-dx log --oneline main..HEAD`

```
c8ea9e95 R7F test: resolve the scratch root in test_absent_corpus_exits_three_and_names_path — the fence prints the resolved corpus root, so a symlinked TMPDIR (macOS /var -> /private/var) failed the exact last-line assertion (bench, found on full-module replay under default TMPDIR)
8efbb200 R7F fence: fix round 2b (dx cold gate A1/A2) — typed scalar reads + placement census
781c8d78 R7F: re-pin AS producer sha after fix round 2a (bench; payload unchanged)
b36d1e85 R7F fix round 2a (Sol 216): Opus 207 B1/B2/S3/N1-N5 closures
3f1677b7 dx-registry fix round 1: R7F refusal-bucket partition, exact-integer rendering, exact F4 replay command, signed DX-027 (four defect-shaped regressions)
2a6d3841 dx-registry: Sol 174 landing — 19 DX rows, round-7 artifact fence (R7F) + tests, checklist placement (seat landing, pre-review)
```
