# REPORT-G — Paper seat G: outcome branches (Abstract, §7 "What the finding changes", §10)

## Bridge adjudication (Claude-side, Fable 5.1 — written by the lead, not the seat)

- Route: audited CLI, `~/.local/bin/codex-run-v3 --genre implementation --effort xhigh` (brief-named tier), model gpt-5.6-sol, `CODEX_SERVICE_TIER=default`, sandbox `workspace-write` rooted at `/Users/edr/code/JouleWise-wt-paper-g`, approvals never. Bridge session `paper-g-20260902-outcome-branches-01`, lease `lease-79ade14d758849ad816f1fdb2ed0612c`, base head `33290b8b`.
- Audit trail: `<scratchpad>/bridge-g/` (prompt.md, out.md = final message, out.log, out.manifest.jsonl, out.status). Manifest final row: run_key=20260903T035214Z-5028-out, model=gpt-5.6-sol, reasoning_effort=xhigh, transport_status=OK.
- Seat envelope: `claude-codex-report/v1`, status **blocked / completion partial**, verdict implementation=implemented, acceptance=ready. Blocking flag F1: the sandbox cannot create the linked worktree's index lock under the common `.git` directory, so the seat could not commit. Non-blocking F2: the `/private/tmp` report write was rejected, so the report body came back in the final message (reproduced verbatim below). Neither flag is a defect in the work; both are structural to seats in linked worktrees under workspace-write.
- Wrapper verdict: `run_status=OK`, `scope_action=passed`. `scripts/bridge session-close --status DONE`: verdict `SCOPE_OK`, three paths `in_scope`, head unchanged at close, thread `complete`, lease released. `docs/paper/results-fill-registry.md` was in scope but needed no edit (every new marker maps to an existing issued row).
- Commit made by the lead after replay (the launch authorized the commit; the seat physically could not): **`a548b958eda24dd09ec999181acd0010c729ef34`** on `feat/2026-09-02-paper-g`, tree clean, not pushed.

### Lead-replayed checks (executed this session in the worktree, on the uncommitted tree the seat left)

| Check | Seat observed | Lead observed |
|---|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_paper*'` | Ran 68 tests in 624.041s, OK (skipped=3) | Ran 68 tests in 629.745s, OK (skipped=3), rc=0 |
| `python3 -m unittest tests.test_paper_first_use_ledger` | Ran 3, OK | Ran 3 tests in 0.608s, OK |
| `git diff --check` | clean | clean, rc=0 |
| `python3 -m unittest tests.test_paper_round7_artifacts` | Ran 45 tests in 3.326s, OK (skipped=1) (static portion) | OK, real 627.81 s (includes the replay-fence portion under a loaded machine) |
| `python3 -m unittest tests.test_paper_terms_lint` | (inside V1) | OK, real 1.04 s |
| Selector `--outcome A|B|REFUSAL` into fresh `/tmp` copies | all three selected | rc=0 ×3; 1722 lines each; 0 `OUTCOME-BRANCH` markers; 0 bold labels; §7 heading = A "What a twofold boundary contribution changes", B "What a below-two ratio changes", REFUSAL "What an unevaluable comparison establishes" |
| Selector refusals | reuse refused | `--output already exists` rc=2; `--output must differ from --source` rc=2 |
| Diff confinement | authorized regions only | hunks at old lines 25-80 (Abstract :23-80), 998-1004 (§7), 1224-1230 (§10 :1222-1230); no other hunk |
| FILL → registry | 6 markers, all existing rows | `[FILL:DG-050/051/052]` → registry lines 622/623/624 (DERIVE, authenticated diagnostic); `[FILL:DG-067/068/069]` → 639/640/641 (MEASURED, issued); all numeric; grep-confirmed |

### Deviations and open items flagged for the magistrate (not fixed at the bench; none blocks the commit)

1. **Refusal heading wording vs retensing plan H04-C.** Plan H04 rules the §7 heading forms: A and B are used verbatim; C is "What excluded comparison evidence establishes". The seat wrote "What an unevaluable comparison establishes" because it matched the skeleton's `:788-808` Refusal predicate (ratio missing / unauthenticated / zero denominator), which is not the plan's Outcome C (evidence excluded before comparison). That skeleton-vs-plan divergence pre-dates this seat; the brief named the skeleton convention as the one to match. Needs a ruling: adopt the H04-C heading verbatim, or record that the skeleton's Refusal predicate supersedes plan Outcome C for these three sections.
2. **Branch label form.** `:788-808` uses `**A — every required ratio passes:**`; the seat used one-word labels `**A:**` / `**B:**` / `**Refusal:**` plus HTML selection markers, stating that descriptive labels would disturb the existing first-use ledger and that the bold-label + blockquote body form is preserved. The selector depends on the one-word labels. Acceptable to the bridge; recorded as a deliberate deviation from "match it exactly".
3. **Qwen-pair verdict placement dropped from the Abstract and §10.** The old build notes carried the non-numeric stopped placements (DS-28..33, PG-01..08) and "give the fixed Qwen3 pair decision". Under the brief's "NUMERIC markers only" rule the seat describes the decision rule without a verdict slot. When DS-32 / PG-08 verdict tokens issue, the fill must add a verdict sentence to the selected Abstract and Conclusion branch; no marker now points there.
4. **Outcome D.** Deliberately not inserted in these three sections; `branch-selection.md` asserts the plan's placement (§4/§6 null-row sites only). Bridge agrees with the reading (plan line 28; H27/H28/H29 carry only A/B forms).
5. **Selector nit.** `_select_group` returns `... + "\n" + after.lstrip("\n")`, so a selected paragraph is immediately followed by the next `##` heading with no blank line (renders correctly as an ATX heading; cosmetic). One-line fix (`"\n\n"`) if wanted.
6. **Process note.** Two seats in a row (this one and, by the same mechanism, any seat in a linked worktree under workspace-write) cannot commit; the lead commits after replay. Worth recording in the codex seat launch rules so briefs stop demanding a seat-side commit.

---

# Seat report (Sol, verbatim from the audited final message)

## Report body (fallback)

The requested report file could not be written because the managed writer rejected the external `/private/tmp` path.

### Branch table

| Section | Outcome | Branch range | Reader content |
|---|---|---:|---|
| Abstract | A | `draft-v2-skeleton.md:26-30` | paragraph 29 |
| Abstract | B | `draft-v2-skeleton.md:32-36` | paragraph 35 |
| Abstract | Refusal | `draft-v2-skeleton.md:38-42` | paragraph 41 |
| Section 7 | A | `draft-v2-skeleton.md:962-968` | heading 965; paragraph 967 |
| Section 7 | B | `draft-v2-skeleton.md:970-976` | heading 973; paragraph 975 |
| Section 7 | Refusal | `draft-v2-skeleton.md:978-984` | heading 981; paragraph 983 |
| Section 10 | A | `draft-v2-skeleton.md:1206-1210` | paragraph 1209 |
| Section 10 | B | `draft-v2-skeleton.md:1212-1216` | paragraph 1215 |
| Section 10 | Refusal | `draft-v2-skeleton.md:1218-1222` | paragraph 1221 |

The zero-context diff contains exactly the authorized original skeleton regions: Abstract lines 25–80, Section 7 lines 998–1004, and Conclusion lines 1224–1230.

Outcome D was not inserted into these sections. The retensing plan places it only where the identical-workload characterization row is discussed—Sections 4 and 6. The procedure records that D remains a prefix combined with A, B, or Refusal, never a fourth exclusive outcome.

### FILL → registry mapping

| Marker | New placement | Registry line | Status |
|---|---|---:|---|
| `[FILL:DG-050]` | Section 7, all branches | 622 | numeric DERIVE; authenticated diagnostic |
| `[FILL:DG-051]` | Section 7, all branches | 623 | numeric DERIVE; authenticated diagnostic |
| `[FILL:DG-052]` | Section 7, all branches | 624 | numeric DERIVE; authenticated diagnostic |
| `[FILL:DG-067]` | Abstract and Conclusion, all branches | 639 | numeric MEASURED; issued result |
| `[FILL:DG-068]` | Abstract and Conclusion, all branches | 640 | numeric MEASURED; issued result |
| `[FILL:DG-069]` | Abstract and Conclusion, all branches | 641 | numeric MEASURED; issued result |

Other numbers were not computed at the desk:

- The cutoff 2 and zero-denominator rule come from the retensing plan and D-165 registry contract.
- The four-run comparison comes from that issued plan.
- Qwen3-1.7B and Qwen3-8B trace to V5-ID-001 and V5-ID-002.

### Executed evidence

#### Mechanical first-use table

Every added reader-facing sentence is enumerated below; repeated sentences are grouped but every instance is named.

| Sentence IDs | Technical work | Construction or gloss | Result |
|---|---|---|---|
| Abs-A1, Abs-B1, Abs-R1 | boundary ambiguity; power sample | Same sentence builds the averaging span, movable energy, and unchanged request total. | PASS |
| Abs-A2, Abs-B2, Abs-R2 | pulse-derived limit and transfer | Same sentence names pulse source, model-work destination, and untested edge behavior. | PASS |
| Abs-A3 | within-model and between-model quantities | Same sentence defines variation among repeats and the difference between models before comparing limits. | PASS |
| Abs-B3 | quotient and component quantities | Quotient is glossed as the second limit divided by the first; both quantities are named first. | PASS |
| Abs-B4 | twofold boundary contribution | The preceding sentence constructs the quotient and its below-2 result. | PASS |
| Abs-R3 | stopped comparison; zero denominator | Same sentence enumerates source failure, zero division, and the resulting stop. | PASS |
| Abs-R4 | model direction | Plain consequence of the preceding stop. | PASS |
| Abs-A4, Abs-B5 | decision rule; uncertainty range | Same sentence defines both checks and the no-direction alternative. | PASS |
| Abs-A5, Abs-B6, Abs-R5 | overlap sufficiency and scope | Same sentence explains too few versus enough samples and limits the result’s configuration. | PASS |
| S7-A1 | independent-edge ratio; shared-error ratio; cell | Built in Sections 1 and 4. | PASS |
| S7-A2 | point-only component; decision behavior | Built in Sections 4 and 6. | PASS |
| S7-A3, S7-B3, S7-R3 | historical diagnostic ratios | Same sentence labels them non-claim history and says they did not select the campaign result. | PASS |
| S7-A4, S7-B4 | inserted-gap check and transfer | Built in Section 4; the sentence preserves the condition. | PASS |
| S7-B1 | below-two criterion and component reporting | Ratio and cutoff built in Section 4; per-component consequence stated. | PASS |
| S7-B2 | repeats versus boundary movement | Physical distinction built in Sections 1 and 4. | PASS |
| S7-R1 | absent, unverified, or zero-denominator ratio | All refusal conditions built in Section 4. | PASS |
| S7-R2 | usable cell, quotient, and direction | Cell, admission, quotient, and direction checks built earlier. | PASS |
| S7-R4 | untested transfer | Pulse source, inference destination, and non-result are explicit. | PASS |
| C-A1, C-B1, C-R1 | false phase-energy difference and bound construction | Mechanism built in Sections 1–4. | PASS |
| C-A2, C-B2, C-R2 | ratio outcome or refusal | Complete rules built in Section 4. | PASS |
| C-A3, C-B3, C-R3 | fixed-pair decision and overlap diagnostic | Built in Section 6; scaling is explicitly denied. | PASS |
| C-A4, C-B4, C-R4 | configuration scope and transfer condition | Both built before the Conclusion. | PASS |
| Section 7 headings A/B/Refusal | twofold, below-two, unevaluable | Immediately following selected paragraph states the predicate and consequence. | PASS |

The shipped ledger initially caught the exact Appendix term “commanded pulses” appearing early in the new Conclusion. It was replaced with the physical description “deliberately started graphics-processor work”; the skeleton and all three selected drafts then passed.

#### Mechanical selection

The selector successfully produced A, B, and Refusal working copies. Each output contained:

- The appropriate Section 7 heading.
- No unselected branch.
- No `OUTCOME-BRANCH` marker.
- No bold branch label.

All three selected outputs independently passed the first-use ledger:

```text
...
----------------------------------------------------------------------
Ran 3 tests in 0.504s

OK
```

Attempting to reuse an output correctly refused:

```text
select_outcome_branches.py: error: --output already exists: /private/tmp/paper-g-selected-A-final.md
exit 2
```

#### Test tails

Required paper suite, including the configured replay-fence test:

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_paper*'
............
----------------------------------------------------------------------
Ran 68 tests in 624.041s

OK (skipped=3)
```

Pre-edit comparison: 68 tests passed in 617.375 seconds with the same three skips.

Shipped first-use ledger:

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger
...
----------------------------------------------------------------------
Ran 3 tests in 0.534s

OK
```

Static round-7 artifact check:

```text
....................................s........
----------------------------------------------------------------------
Ran 45 tests in 3.326s

OK (skipped=1)
```

`git diff --check` exited 0 with no output.

### Changed files

- `docs/paper/draft-v2-skeleton.md`
- `docs/paper/fill-rehearsal/branch-selection.md`
- `docs/paper/fill-rehearsal/select_outcome_branches.py`

`docs/paper/results-fill-registry.md` was inspected but did not require modification.

### Commit blocker and exact next step

`git add` failed with:

```text
fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-paper-g/index.lock': Operation not permitted
```

Final state:

```text
## feat/2026-09-02-paper-g
 M docs/paper/draft-v2-skeleton.md
?? docs/paper/fill-rehearsal/branch-selection.md
?? docs/paper/fill-rehearsal/select_outcome_branches.py
```

```text
33290b8b NIGHT_HANDBACK: rehearsal-20260903 RE-ARM (fresh audit: daytime pulls moved canonical HEAD past the pinned repo_head — gate would refuse night_plan_stale; plan re-pinned to this commit, plists re-rendered, courier pin refreshed)
b81a2ac5 Merge pull request #274 from mpmdw/feat/2026-09-02-t26-liveness
711ac0b6 RUN_STATE: T30 durable-pause pointer to trace file 39 (decode-identity branch)
```

From this worktree, in an environment that can write the common Git directory:

```sh
git add docs/paper/draft-v2-skeleton.md \
  docs/paper/fill-rehearsal/branch-selection.md \
  docs/paper/fill-rehearsal/select_outcome_branches.py
git commit -m 'paper: prewrite outcome branches' \
  -m 'Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>'
git status --short --branch
git log --oneline -3
```