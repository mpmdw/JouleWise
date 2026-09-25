# Cold Fable ruling — A291-FINALPASS-01, run 2 (PR #409, S = c5cbfd9e)

Judge: Claude Fable 5.1 (claude-fable-5-1), cold, single non-interactive session, foreground only, no subagents, no background tasks.
Worktree: `/Users/edr/code/JouleWise-wt-coldgate-278ebc9e-final` at HEAD `370acb57` (detached, clean).
Session start 2026-09-25 04:07:25 PDT; ruling written ≈04:16 PDT (about 9 of the 45 minutes).
Packet directory: `docs/process_traces/2026-09-24-activation-278ebc9e/117-coldgate-packet-a291-finalpass/` (below, `P/`).

## 0. Disclosure of auto-loaded context

The harness injected three files before I acted, none requested: the global `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, and the memory index `MEMORY.md` (truncated by the harness). Nothing from any of them is used below. Not opened, by rule: CLAUDE.local.md (absent from this worktree), RUN_STATE.md, TASK_QUEUE.md, council logs, run reports, memory topic files, any `docs/process_traces` file outside `P/`. `P/20-refused-run1-ruling.md` sits inside `P/` and was read as the record of run 1; it is not used as authority. No sudo/launchctl/powermetrics/systemsetup; the discovery suite was not run; the only write is this file. Scratch copies were made under `/tmp/cg117-S`, `/tmp/cg117-old` (git archives) and `/tmp/cg117-clone` (a clone used for the merge probe, §2 item 1); none touches the canonical root or any custody path.

## 1. Trust-anchor verification (charter §9), recorded before any merits reading

Method: `python3 scripts/validate_gate_packet.py --packet P/00-charge.md --charter docs/process/coldgate_charter.md --expected-charter-sha256 <X> --expected-packet-sha256 1d92a428…bc9f91`, run twice as the convening message instructs, then an independent `shasum -a 256` on both files.

| Run | Expected charter sha | Observed charter sha | Result |
|---|---|---|---|
| 1 (deliberate typo) | `…c95d82` | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | REFUSE, rc=2, `charter_trusted_observed_mismatch` |
| 2 (correct anchor) | `…c95d81` | same | **PASS**, rc=0, schema `coldgate-validator-receipt/v2` |

Packet sha expected `1d92a428d54d136c8648fd4f47a8068df10a9b11f1684a866179321596bc9f91`; observed (validator and `shasum`) identical. Exhibit manifest sha `556f2bb4…66ef4`; all 31 manifest exhibits observed = expected, including `ex-03-regate-d2e751df.log.txt` (run 1's missing exhibit, now tracked) and `ex-10-validator-receipt.json`. `judge_handoff_bound: false`. The packet's own charter pin equals the trusted value. Merits opened only after run 2.

## 2. The ten items of A291-PREMERGE-01 §3 V3 — verification

Items 1–3 by my own execution, as the charge requires; 4–10 for presence and consistency with primary evidence.

| # | Item | Result | Deciding evidence (personally verified) |
|---|---|---|---|
| 1 | The sha | **VERIFIED** | `git log -1 --format=%H %P c5cbfd9e` = parents `b1913497` + `a50d098b` (= ex-01). `git merge-base origin/main S` = `25cde215` (= ex-01). `git diff --stat e0934a59...S` over the lane paths = the 15-file / +4256 −54 stat in ex-01, byte for byte. Blobs at S: `scored_packer.py` `b49e911a…`, `test_scored_packer.py` `2705fd80…`, `test_scored_ownership_forgery.py` `57012e9f…`; packer at `6e2504b1` and `3fb98469` both `56a43c86…` (all = ex-01). **Merge probe:** in a `/tmp` clone, `git checkout S; git merge 7c1c9caf` (the worktree's current `origin/main`, ahead of ex-01's `e0934a59`) merged with no conflicts; `python3 scripts/gen_state.py --check` rc=0 on the merged tree; packer and test blobs unchanged by the merge. The charge's "merges cleanly and `gen_state --check` passes" claim holds against main as of this session. |
| 2 | The diff | **VERIFIED** | `git show d2e751df`, `git show 37f47475`, `git show b1913497` are byte-identical to ex-02a/02b/02d (`diff` empty). ex-02c matches `git log` for `7c56aa33`/`72808d82` (a 2-line TASK_QUEUE regeneration and its exact revert; net zero). `git diff 6e2504b1 S -- joulewise/scored_packer.py` is byte-identical to ex-04's patch: exactly line 70 (`-> dict`) and the two conversion tuples at 170/293 gaining `RecursionError` last. `grep -c RecursionError` at S = 2. Lane-only diff `3fb98469..S` over the thirteen lane files = 4 files: `scored_packer.py` 6, `test_gen_state.py` 9, `test_scored_ownership_forgery.py` 2, `test_scored_packer.py` 32. ex-02-diff-note lists only three of these (finding N-1); the fourth is exhibited separately as ex-02d, so nothing is hidden. |
| 3 | Re-gate outputs | **VERIFIED by execution** in `git archive c5cbfd9e` under `/tmp/cg117-S` | (a) `python3 -B -m unittest tests.test_scored_packer tests.test_scored_packer_fuzz tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_named_seal_regressions tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_named_regressions` → `Ran 49 tests in 61.013s OK`, FUZZ census identical to ex-03 (`inv_52: 23` etc.), NAMED_SEAL line identical. (b) `test_a291_deep_nesting_refuses_inv_52_not_recursion_error` at S → OK (8.1 s); the same test with `git show 3fb98469:joulewise/scored_packer.py` swapped in → `ERROR … RecursionError: maximum recursion depth exceeded`, `FAILED (errors=1)`. FAIL-before / PASS-after reproduced. (c) The five AST tests in `tests/test_scored_packer.py` by name (`test_inv40_ast_seal_placement`, `test_r4c_derived_structure_ast`, `test_r5b_no_trusted_mutable_cache_ast`, `test_a291_parent_facts_and_conserve_read_the_view_ast`, `test_a291_packer_imports_nothing_from_tests_ast`) → `Ran 5 tests OK`. (d) ex-115b's patch-target test `test_checker_exception_is_failure` at S → OK under `python3 -m unittest tests.…` AND under `unittest discover -s tests -p test_scored_ownership_forgery.py -k …`; with the `3fb98469` forgery file swapped in, the discover style → `AssertionError: CheckerCrash not raised`, `FAILED (failures=1)`. b1913497 fixes a real hosted-CI defect. |
| 4 | Evidence transfer | **PRESENT and CONSISTENT** | ex-04 statement + patch; the patch equals `git diff 6e2504b1 S` (item 2). The changed lines (70, 170, 293) are outside the five mutated lines of ex-100b (81, 83, 86, 96, 98) and touch only the two `except` tuples, so no legal roster, digest or refusal code on the accepted path can change. The 49-test re-gate (item 3) is consistent with that. The 585 s forgery campaign, the mutation kills and the forger replays were NOT re-executed (ruling 112 V1(b) expressly excused them; see §5). |
| 5 | F-C replay evidence | **PRESENT** | ex-104-fc-replay.jsonl: `REPLAY CHECK` + nine lines, C1/C3/C5/C7/C8 `inv_38`, C2/C2b/C4/C6 `inv_39`, one per accepted candidate in ex-104-fc-adjudication.jsonl (9 ACCEPTED/OUT_OF_ROUND, 11 REFUSED). ex-106: 9 accepted OUT_OF_ROUND, 9 `REPLAY REFUSED inv_38`. Ruling 112 M3 is cured. Not reproducible here (the candidate constructors are not in the packet; ex-105 §P2 reproduced them at `6e2504b1`, whose packer differs from S only at the three ruled lines). |
| 6 | Full suite + hosted CI | **PRESENT; CI VERIFIED** | ex-06: 7,131 tests, 1 failure, 109 skipped at S, unpiped, epoch-pinned. The failing test `test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child` is a `subTest(exit_delay=…)` ladder asserting SIGTERM on a stuck child (`tests/test_sample_quiet_predicate_evidence.py` at S, lines 825–847); `git diff --stat 25cde215 S -- tests/test_sample_quiet_predicate_evidence.py` is empty, so the lane cannot have caused it. `gh run view 36098330718` (read-only): `headSha` = S, `status completed`, `conclusion success` — the six test shards, quick, fences, build, installed-wheel and both calibration-exclusive jobs all pass (ex-11 = gh). The separate `gate-ledger` workflow run 36098344851 is `failure` on S: expected, because ledger rows 7, 9 and 12 are still NOT-RUN in the PR body (charge item 6). I did not and may not run the discovery suite. |
| 7 | Lenses, counter-review, dispositions | **PRESENT and CONSISTENT** | ex-110a F1 (`-> dict`) → landed (item 2, line 70). ex-110b F1 (RecursionError) → landed two-site (item 3(b)). ex-111b R6-1 → V2 of ruling 112 (not this merge); R6-2/R6-3 → runner obligation + `A291-STRUCTURE-INDEX-01`; CI cost → `CI-A291-TIMINGS-01`; duplicated operators → follow-up. ex-113b CLEAN on d2e751df (its V3 ran the same six tests I ran, same OK); ex-114b two findings on 37f47475 (stale comments; hand count 245) dispositioned in ex-07; ex-115b CLEAN on b1913497 (both styles + mutant FAIL, reproduced by me). Every finding in ex-110a/110b/111b/113b/114b/115b has a row in ex-07; none is silently applied. |
| 8 | Entry-witness code note | **PRESENT and VERIFIED** | ex-07 row "108b F1", ex-107b table, ex-108b table state it. At S, `tests/test_scored_ownership_forgery.py` lines 180–221: `test_entry_path_witness_inv_23` asserts `'inv_38'`, `…inv_36` asserts `'inv_38'`, `…inv_37` asserts `'inv_11'` (grep of `.code`). This matches ruling 105 §3.3.5 (the rows are replay-owned; the packer has no `inv_23/36/37` codes). Recorded, not a defect of the merge. |
| 9 | R4-2 final text verbatim | **PRESENT** | ex-85 §4 carries R4-2 (a)–(e) verbatim with "(a) `def _ownership(registration, roster) -> dict`" and "(e) … Nothing else in the module changes; INV-37 code unchanged." ex-95 amends R4-3 items 2/4, R4-4 and R4-5 items 3/4 only; R4-2 stands as in ex-85. The `-> dict` claim is now true in code (line 70). The "nothing else changes" clause bound the round-3 landing; ruling 112 V1(b) (a governed verdict, charter §9) licensed the separately reviewed post-review commit, and I do not reopen that. Contract v4.1 (ex-89) row INV-52 (`code inv_52`, line 644) is the code the two-site cure raises. |
| 10 | Charter pin, validator receipt, PR ledger draft | **PRESENT** | ex-10: `PASS`, charter `099de884…c95d81`, packet `d40ab519…7610` (the packet as it stood before ex-10 and the §2.2 renames; a packet cannot pin its own final digest), 30 exhibits, `judge_handoff_bound false`. My own run (§1) is the binding check and PASSes on the final packet. ex-pr-ledger-draft.md carries the twelve rows; rows 7, 9, 11, 12 are NOT-RUN in the draft (finding M-1 on staleness of 9 and 11). |

All ten items are present; items 1–3 verify by my own execution. The condition of ruling 112 §3 ("MERGE only if items 1–3 verify by its own execution and items 4–9 are present") is met.

## 3. Verdict

**MERGE — PR #409 at head `c5cbfd9eeefe6aa3dc7f323f1da7f6593b069a59`, and at no other sha.** The cold final pass finds no BLOCKER and no MATERIAL defect in the merge candidate. The two post-review production changes (`-> dict`; `RecursionError` → `inv_52` at both conversion sites) are exactly the ruled texts of A291-PREMERGE-01 V1(a)/(b), reproduce FAIL-before/PASS-after, and leave every accepted-path behaviour and digest untouched (item 4). The CI patch-target fix (b1913497) cures a real discover-by-module defect that hosted CI would otherwise mask. The kernel retirement (37f47475) is docs/kernel only and `gen_state --check` passes on the tree merged with current main.

This verdict is the cold gate's row-7 result. It does not fill ledger rows 9, 11 and 12, which the ledger assigns to the lead and the magistrate; the magistrate's terminal review (row 12) of this exact sha remains a precondition of the merge under the ledger's own text. If the branch receives any further commit, this ruling does not transfer: a new sha needs a new final pass (a re-merge of main that changes only the merge commit and leaves `git diff main...S` over the lane files byte-identical is the one exception; K records the new sha and the unchanged lane diff in the record).

**Disagreements with the lead's labelled disposition:** none on the merits. Hygiene findings N-1..N-4 below. I concur with every row of ex-07-dispositions.md.

## 4. Ruled items (exact text for seats P and K)

**R-1 (AFFIRM the charge's disposition table, ex-07, in full).** No finding of ex-110a/110b/111b/113b/114b/115b is open against this merge. K's check: every `id` in those six exhibits appears in ex-07 column 1 (they do).

**R-2 (row 7 text — see §6).** AFFIRM MERGE; the exact ledger cell is in §6.

**R-3 (different text: rows 9 and 11 of the PR ledger).** The draft still says NOT-RUN for rows 9 and 11 although ex-06 and ex-11 exist. Before the PR body is finalised, P replaces them with:
- Row 9: `RUN docs/process_traces/2026-09-24-activation-278ebc9e/117-coldgate-packet-a291-finalpass/ex-06-fullsuite-summary.txt — 7131 tests at c5cbfd9e, 1 out-of-lane timing failure (test_sample_quiet_predicate_evidence, passes isolated and in hosted CI), 109 skipped`
- Row 11: `RUN https://github.com/mpmdw/JouleWise/actions/runs/36098330718 — conclusion success on c5cbfd9e (all six test shards, quick, fences, build, installed-wheel, both exclusive jobs); post-merge cross-unit review: <fill after merge>`
K's check: `gh pr view 409 --json body` contains no `NOT-RUN` in rows 9 and 11 before merge; row 12 is filled by the magistrate and nobody else.

**R-4 (different text: ex-01 and ex-02 refresh, record only, no re-convene).** In the gate record (not the sealed packet) P appends one line: `origin/main at ruling time 7c1c9caf; merge probe clean; gen_state --check rc=0` and one line: `lane-only diff 3fb98469..S: scored_packer.py 6, test_gen_state.py 9, test_scored_ownership_forgery.py 2 (b1913497), test_scored_packer.py 32`. These correct N-1/N-2 for the reader; the sealed exhibits stay as pinned.

**R-5 (request: ratification path for the R6-1 gate rule, not a merge condition).** Ruling 112 §2 proposed the "R6-1 gate" rule text; ex-07 records it as "proposed … for the cold gate/Ed". It is a process rule (charter §3.4) and has not been presented for ratification in this packet, so I neither ratify nor amend it here. Text for the record: `R6-1 gate rule (ruling 112 §2): PROPOSED, unratified as of 2026-09-25; must be ratified (magistrate + Ed, or a convened cold question) before the first registered-mode registration is armed; pilot-mode nights exempt.` K blocks any registered-mode arm packet that does not cite the ratification.

**R-6 (AFFIRM the follow-up lanes as named, unchanged).** `CI-A291-TIMINGS-01` (ruling 112 V1(c) text), `A291-STRUCTURE-INDEX-01` (V1(d) text), the finalize-path `_digest` hardening (112 M5). None gates this merge; each opens after merge with its own re-gate as ruled.

## 5. NOT EXECUTED (deliberately, by rule or by ruling 112's own excusal)

- Full discovery suite at S: forbidden to this judge; taken from ex-06 + hosted CI (verified via `gh`).
- `tests.test_scored_ownership_forgery` full campaign (585 s), mutation kills m1–m5, the F-B/F-C forger replays, `tests.test_scored_packer_stress`: not rerun; evidence transfers per item 4 (three exception-path lines outside every mutated line). This is the excusal ruling 112 V1(b) wrote, and my item-2/3 probes confirm its premise.
- R6-1 lever probe (ex-111b): not rerun; not a merge question.
- Contract v4.1 (ex-89, 62 KB) read only at the INV-52 row and the header; no ruling above depends on other contract text.

## 6. Findings (tiered; severity independent of verdict)

**No BLOCKER.**

**M-1 MATERIAL (PR body, not the code).** `ex-pr-ledger-draft.md` rows 9 and 11 read NOT-RUN while the packet carries their evidence (ex-06, ex-11). If the PR body is merged in that state the gate-ledger workflow stays red and the ledger misstates what was done. Cure: R-3 text. Row 12 must be filled by the magistrate after this ruling; row 7 by §7 text.

**N-1 NIT (hygiene).** `ex-02-diff-note.txt` ("Lane-only diff … 3 files changed") omits `tests/test_scored_ownership_forgery.py` (2 lines, b1913497). The change is exhibited as ex-02d and its blob is pinned in ex-01, so nothing is concealed, but the stat note was generated before b1913497 and no longer describes S. Cure: R-4.

**N-2 NIT (hygiene).** `ex-01-sha.txt` pins `origin/main` at `e0934a59`; at ruling time it is `7c1c9caf`. The charge discloses the drift and I re-ran the merge check (item 1). Cure: R-4.

**N-3 NIT (convening).** The convening message's code-anchor clause reads "`git show c5cbfd9e:<path>` or `git show c5cbfd9e:<path>`" (the same sha twice; run 1's template carried two different stale shas). Harmless; the charge governs. On future convenes name S and the named revisions (`3fb98469`, `d2e751df`) once each.

**N-4 NIT (record).** ex-10 is the receipt of the pre-rename packet (`d40ab519…`), as the charge states; the receipt for the final packet sha `1d92a428…` exists only in this ruling (§1) and in the convene script's pre-launch check. Acceptable under the charge's own rule ("your own validator run is the binding check"); K pastes this ruling's §1 table into the gate record so the final-packet PASS is recorded outside the judge's file.

**N-5 NIT (code, follow-up already named).** Ruling 112 M5 stands: `_seal(finalize=True)` on an unsealed roster with deep nesting in `events[-1].sha256` can still raise `RecursionError` at `_digest` (line 304, outside the try). Unreachable through any public entry (each runs `_seal(finalize=False)` first); follow-up as ruled, not a merge defect.

## 7. Gate-ledger row 7 — exact text to carry

```
| 7 | Apex Fable code-reading diff gate answering design-level questions; never skipped or downgraded | RUN docs/process_traces/2026-09-24-activation-278ebc9e/117-coldgate-packet-a291-finalpass/20-coldgate-fable-finalpass-ruling.md — cold Fable 5.1 final pass A291-FINALPASS-01 run 2 on c5cbfd9e: MERGE; items 1–3 verified by own execution (49 OK; deep-nesting test FAIL@3fb98469/PASS@S; patch-target test OK both styles, FAIL with 3fb98469 file; merge with 7c1c9caf clean, gen_state --check rc=0); items 4–10 present; 0 BLOCKER, 1 MATERIAL (PR ledger rows 9/11 stale), 5 NIT; run 1 REFUSE (gitignored ex-03) cured per its §2.2 |
```

Verdict line: MERGE — PR #409 at c5cbfd9e only; items 1–3 verified by execution, 4–10 present; no BLOCKER; fill ledger rows 9/11 (R-3) and row 12 before merging.
