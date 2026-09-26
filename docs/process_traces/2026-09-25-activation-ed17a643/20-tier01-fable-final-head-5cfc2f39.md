# Fable final-head pass (gate-ledger row 7) — TIER-01 installation, merge candidate 5cfc2f39 (PR #419)

**Contamination disclosure.** Automatically present at session start, before any action of mine: the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and the auto-memory index `MEMORY.md` (one-line pointers only; I opened no memory file). Beyond the charge I read: the full `git diff 7c9dadc4 5cfc2f39`; the four records the charge names (40, 43, 50, 51); the Opus lens 41 (M-table, §T3, and the M1 decision-log block) and the Sol lens 42 (finding F2) to check the two new lanes' citations; `docs/decision_log.md` lines 8120–8135 and 11138–11146; the head of `.github/workflows/gate-ledger.yml` and the tail of `scripts/check_gate_ledger.py`. The generated region of `TASK_QUEUE.md` only through the diff. A grep of every changed file for absolute paths incidentally printed one pre-existing `TASK_QUEUE.md` row (E233, unrelated); I did not read that file otherwise. I did not open `RUN_STATE.md`, any council log, activation record, or the ruling file COUNCIL-407-01. GitHub was queried read-only once (`gh pr view 419`). Judge: Claude Fable 5.1, cold, single foreground session, no subagents or background tasks; repository read-only except this file. Wall ≈ 15 min; 2026-09-25 15:21 PDT at writing.

## Verdict: MERGE

5cfc2f39 is the exact head of PR #419 (verified live: `state OPEN`, `headRefOid 5cfc2f39…`, base `main`, `mergedAt null`). No BLOCKER, no MATERIAL. Every text my 7c9dadc4 pass dictated is installed; the one departure (the `#419` fill) is what the dictated instruction asked for. Both new kernel lanes are accurate to their cited sources, with one labelling nit. `gen_state --check` and the two named test modules pass at this head. Nothing has been introduced since 7c9dadc4 that a full-tier merge should not carry. This pass is the final-head read that the 7c9dadc4 ruling required for the post-review commits; no further round is needed.

| # | Severity | Finding |
| --- | --- | --- |
| N1 | NIT | `TIER01-PATH-GUARD-01` is labelled "Opus 41 §T3 design" but its acceptance summary is Sol 42 F2's allow-list (NUL-delimited merge-base-to-head list; light-eligible = `tests/**`, `docs/**` minus `docs/paper/**`, `docs/report_src/**`, `docs/site/**`, plus four root bookkeeping files). Opus 41 §T3 and my 40 §T3 are deny-lists. The allow-list is the strictest of the three (README.md, `env/`, `figures/` and everything unlisted force full by default), so the installed text is the safe direction; only the authority label is off. Fix at the lane's next touch, not in this PR. |
| N2 | NIT (time-conditional) | "Installed at the merge of the installation PR #419 on 2026-09-25" and "day-30 review 2026-10-25" (orchestration §5 and the defect log) are forward-dated to a merge today. Accurate if #419 merges before midnight PDT. If it slips, the magistrate's row-12 read moves both dates in the merge bookkeeping, exactly as 51 already records. Not a merge condition. |
| N3 | NIT | F6 attribution wording is paraphrased across comment lines in `gate-ledger.yml` and in orchestration §5. I marked F6 "optional wording"; the meaning is installed at all three sites. Accepted. |
| N4 | NIT (observation) | `origin/main` has advanced one commit past the candidate's merge base (c126b0f8, battery-float observation). It touches none of the seventeen files in this diff and leaves the kernel, queue and test count untouched; `git merge-tree --write-tree origin/main 5cfc2f39` merges clean. The 257 pin therefore survives the merge. Hosted CI on the merge commit is post-merge confirmation, as standing. |

## (1) Dictated texts vs installed (executed)

Read in full: `git diff 7c9dadc4 5cfc2f39` (17 files, +815/−16). The six substantive files and what they carry:

- **F1 (MATERIAL) rule header, `docs/orchestration.md`.** Installed byte-exact: `**Rule TIER-01 (cold-gated by COUNCIL-407-01 §G5 on 2026-09-24; endorsed by Ed in GitHub issue #415 on 2026-09-25).**`
- **F2 (MATERIAL) install date, both files.** Dictated: "Installed at the merge of the installation PR on 2026-09-25 (set the PR number here at merge)." Installed: "Installed at the merge of the installation PR #419 on 2026-09-25." The parenthetical was an instruction to the lead, not text for the reader; filling `#419` and removing the instruction is the instruction carried out. The number is stable (PR #419 exists and is the candidate's PR), so filling it before the merge commit is not premature. Defect-log paragraph likewise, with `#419`. Day-30 = 2026-10-25 in both files. The lead's disposition of Sol delta F1 (51) is correct.
- **Rule items 1–6 unchanged.** `diff` of the six numbered items between the two heads: byte-identical (item 1 md5 `4783436e…` on both sides). The installed rule text is still the §G5 text; only the header and the closing paragraph moved.
- **F5 (NIT) D-170 dated addendum.** Installed byte-exact at the dictated position (directly after the "Until Ed makes it required, `gate-ledger` stays ADVISORY" paragraph, now `docs/decision_log.md:11144`). No other decision-log line changed; no D-118 amendment and no D-185 row were authored (rule 11 respected; the Opus M1 dissent is carried by lane, see (2)).
- **F6 (NIT) attribution.** Paraphrased, meaning installed (N3).
- **F3 (NIT) success-line predicate.** `main()` now uses the identical list comprehension as `check()` line 141 (`line.startswith("Tier:")`, stripped, `== ["Tier: light"]`). Regression `test_indented_light_tier_line_reports_full_twelve_rows` added; Sol's delta (43 V2) mutation-checked it RED on the old predicate. `.github/pull_request_template.md` is unchanged in this range.

## (2) The two kernel lanes (executed)

`docs/process/state_kernel.json` gains exactly two task objects; `TASK_QUEUE.md` gains exactly the two generated rows (A306, A307) in both tables; `tests/test_gen_state.py` adds both ids to `EXPECTED_IDS` and moves the count pin 255 → 257 with a dated reason. A305 is `JCORRECT-NULL-CALIBRATION-WINDOWS-01` (pre-existing), so ranks 306/307 are the next free ranks with no new collision. Priority `p3_hardening_candidates` and lane `agent` are existing vocabulary.

- **TIER01-PATH-GUARD-01.** Goal quotes #415's ask correctly. Evidence cites 41 §T3 (exists; a deny-list design), 42 SF-2/F2 (exists; F2 is the allow-list the summary reproduces nearly verbatim), and 40 (my ruling that the path check is a follow-up: correct). Every path the summary names exists at HEAD (`docs/site`, `docs/paper`, `docs/report_src`, `RUN_STATE.md`, `PROJECT_STATUS.md`, `AGENT_PLAN.md`). Acceptance names defect-shaped tests (light + `joulewise/**` refuses; light + `docs/**` passes; missing input refuses light), a full-tier gate, and the day-30 deadline: all consistent with what 40, 41 and 50 ruled. Mislabelled authority only (N1).
- **TIER01-D118-RECONCILE-01.** Goal quotes D-118 accurately (`docs/decision_log.md:8127–8128`: "any item marked NOT-RUN blocks the merge. A PR without a complete gate ledger is not merge-eligible"). Evidence cites 41 M1 (verified MATERIAL in the Opus table) and 40 F5 (verified NIT). Authority 50 records the dissent and the rule-11 reason the lead did not author the line. Acceptance correctly leaves the ruling to a cold gate and permits "not needed" as an outcome. Accurate.

```
$ python3 scripts/gen_state.py --check ; echo rc=$?
rc=0
$ python3 -m unittest tests.test_check_gate_ledger tests.test_gen_state
Ran 83 tests in 6.294s
OK
$ git diff --check 7c9dadc4 5cfc2f39 ; echo rc=$?
rc=0
```

## (3) Anything a merge should not carry (executed)

- The eleven remaining files are review records under `docs/process_traces/2026-09-25-activation-817355d2/02-tier01-review/` (charge, three lenses, my pass and its stdout, the Sol delta, two triages). Grep of every added line for secrets, tokens or key material: none. Absolute `/tmp/` and `/Users/edr/…` paths appear only inside the review records as evidence locations, which is the repository's existing practice for seat records.
- No production code under `joulewise/` changes in this range; the only executable change is the three-line `main()` predicate in `scripts/check_gate_ledger.py`, covered by the new regression. The PR remains FULL tier per §G5 item 4 (it installs the gate itself), so all twelve rows apply and row 12 must name `5cfc2f39`.
- Main drift: clean merge simulation, no overlapping files (N4).

## Not executed

- The GitHub Actions `gate-ledger` run on the PR body (the body is not in the repository); the local checker invocation is the same command line.
- Full test discovery (charge forbids); only the two named modules.
- Enumeration of other open PRs beyond `origin/main` itself.

## Merge instruction

Merge 5cfc2f39 as the head of PR #419 under the full twelve-row ledger with row 12 = `5cfc2f39`. No text change is required before merge. If the merge lands after 2026-09-25 PDT, move the two installation dates and the two day-30 dates in the merge bookkeeping (N2). Correct the `TIER01-PATH-GUARD-01` authority label at that lane's next touch (N1).
