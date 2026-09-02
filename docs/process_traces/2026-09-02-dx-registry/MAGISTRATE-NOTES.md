# DX registry rows + round-7 artifact fence (R7F) — magistrate notes for the PR gate

Lane: DX registry / round-7 artifact fence (ruling 168a).
Branch `feat/2026-09-02-dx-registry`; PR #272.
Files 01–22a in this directory are the seat briefs, the sealed reports, and the
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
| Opus counter-review (gate item 6) | Opus 5 (Agent tool, read-only) | 19, 19b | 73f7fcc2 | `SHOULD-FIX 2`, `NIT 4`; "What I would not merge as-is: nothing". Disposition in 19b: SF2(a)/(b), NIT3, NIT4 to a luna fix round; SF1 checklist half at the bench, test half deferred to the fill-batch PR; NIT1/NIT2 recorded (D-161 prune) |
| Fix round 3 (Opus findings) | luna high (237) | brief in scratchpad, report `19c` | "@ 73f7fcc2" | envelope `"status": "clean"`, `"completion": "complete"`; wrapper `run_status=SCOPE_VIOLATION rc=77 scope_action=failed_preserved` caused ONLY by the magistrate's untracked files 19/19b in the worktree (`unowned_dirty`); the seat's edits are all inside its two-file scope and were used as landed |
| Delta re-audit 3 | terra xhigh (239) | 20 (brief, report), 20b | "@ 7fc87a7f" | `VERDICT: SHOULD-FIX 1` (docstring over-specifies the UNAVAILABLE detail as a path; doc-only, cured at the bench per 20b; contract arithmetic, AS-branch flattening, env-override isolation and scope all confirmed) |
| Bench | magistrate (bench) | commit 9be7a229 | — | docstring: the UNAVAILABLE detail is the preflight resolved path OR the producer's flattened output (terra 239 SF cure) |
| Final-head fresh pass | sol high (240) | 21 (brief, report) | "@ 9be7a229" | `VERDICT: SHOULD-FIX 1` — the same docstring sentence a THIRD time (silent exit-3 producer falls back to the resolved corpus root, not documented). Full module Ran 45, OK (472 s); literals-only 181 / 0; CI clean-checkout skip path confirmed statically. Charter §3 trigger 1 (second fix round on the same defect) — COLD GATE convened, packet in `docs/process_traces/2026-09-02-coldgate-r7f-unavailable/`; no further edit to the sentence until it rules |
| Cold gate ruling (r7f-unavailable) | cold Fable instance + Opus 5 contract-lens refuter, blind, parallel | `../2026-09-02-coldgate-r7f-unavailable/` (00-PACKET, 01, 02, MAGISTRATE-RULING) | packet @ 4c88b941; cure = 3efa807e | Both seats ADOPT (a): docstring-only, enumeration derived from the closed three-site `ArtifactsUnavailable` census; Opus refutations R-A1–R-A4 (directory entry, root-only resolve, AS exit 3 discards collected XD/F4 comparisons, sha256 drift is producer exit 3) bench-verified and folded into the operative text; behaviour questions registered as `R7F-EXIT3-SEMANTICS-01` (post-merge kernel batch). No code or test change |
| Final-head fresh pass 2 (§5, over the cold-gate commit) | terra high (243 → protocol failure; 244 → consumed), detached worktree | 22 (brief, report), 22a (the 243 report) | "@ 3efa807e" | 243: content CLEAN but the JSON envelope was 8459 bytes > the wrapper's 8192-byte cap → `report_parse=invalid`, `run_status=ACCEPTANCE_FAILED rc=65` — protocol failure under the contract, NOT consumed; relaunched as 244 with the size rule in the brief. 244: `VERDICT: CLEAN`, envelope 2119 bytes valid; `co_code` identical between 4c88b941 and 3efa807e (docstring-only); full module `Ran 45`, `OK` (482 s) via `R7F_CORPUS_ROOT`; full replay `R7F PLACED 0/16`, `R7F COMPARED 184 / MISMATCHES 0`; literals-only 181 / 0; census closure confirmed (class, three raises, one catch); ruling evidence replays; custody sha256 of files 01/02 match the ruling |

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

## Terminal review (gate item 12) — 2026-09-02, magistrate, full session context

Merge candidate: the head carrying this note; commits after the terra 244
fresh pass are `c3cdd486` (item-9 replay custody, text only) and this note.
Reviewed at the bench with the merge-base diff (`403998e1...HEAD`): the
branch is additive — `scripts/check_paper_round7_artifacts.py` (+1040) and
its 44-test module, `docs/paper/results-fill-registry.md` (+60, bench-only
registry), `docs/paper/round7/fill-checklist.md`, and one behavioural change
to `scripts/paper_anchor_correction_quantified.py` (`PopulationUnavailable`
→ message on stderr, exit 3, per the r7f-unavailable cold-gate ruling;
`8d084abc` replayed the executed-evidence block). The two-dot diff shows
main files the branch predates (projection-02 trace, night driver,
identity pins) as deletions; the three-dot diff and the integration tree
858f553e confirm the merge keeps them. Item 9: 858f553e ran the canonical
suite: Ran 4820, OK (skipped=125), file 23 (file 16, the earlier R7F replay
at 8efbb200, is superseded for item 9 by file 23). Verdict: MERGE, third in
the wave, after t26-c.
