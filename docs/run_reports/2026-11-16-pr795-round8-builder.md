# PR #795 round-8 builder, 2026-11-16

Intake: direct user priority, branch align/2026-11-14-fit-interim, clean starting head
ac2e1ce33eb9612aa213132d02aba74ff699915e. M0: no active stop card, AGENT lane;
RUN_STATE targeted sections, TASK_QUEUE manual fences/current queue, plan map, playbook
and orchestration read. The latest direct request takes precedence over stale queue
pointers. Sole worktree writer. No real recordings/custody opened, MBP contact, quiet
measurement, merge or external message. Source authority: RL-166 and RL-173 E/E.1
read from origin/audit/2026-11-10-fable. Estimator constants and the pinned Step 3
arithmetic are unchanged.

Review: /Volumes/JW-EXT/scratch/sol-look-r7-gate/FINAL-MESSAGE.md; REPORT.md absent.
The linked full report was read at
/Volumes/JW-EXT/tmp/jw-pr795-cold.NRYKKd/worktree/docs/run_reports/2026-11-15-pr795-cold-review-ac2e1ce33.md.
Verdict REFUSE, three HIGH, no MED or LOW findings. Retained evidence is immutable.

## Dispositions

| ID | Severity | Disposition |
|---|---|---|
| R7-H1 GPU gaps split at segment boundaries | HIGH | Merge touching/overlapping fitted intervals before stage-1 gap judgment and the independent stage-2 backstop. Disjoint intervals remain disjoint. Same 2 s bound; 15 boundary holes cannot hide 45 s of missing support. |
| R7-H2 Step 3 timing substitution outside energy fit | HIGH | Verify every selected Step 3 trace's time-only digest against stage 1 before value loaders run, including included legs missing a start reading and therefore outside the energy fit. Step 3's exact loaded-code set includes the existing time reader. |
| R7-H3 committed verdict/source mismatch | HIGH | Replay the existing blind inclusion_34 rules on the current span before admission. Each committed type-A boolean is conjoined with the replay; a current failure excludes, and a committed exclusion stays excluded. Type-T fields remain unchanged and runtime unread. No new verdict format or inclusion criterion. |

## Regression and integration evidence

The initial four regression tests failed on the original source with six assertion
failures: 3 s and 2 s boundary holes printed as 1.5/1 s; stage-2 backstop accepted;
both committed abnormal-trailer/missing-journal cases admitted; Step 3 timing substitution
accepted. Same tests pass after the repairs (4 tests, 9.038 s). Logs:
/Volumes/JW-EXT/scratch/sol-look-r8/regressions-{before,after}.log.

Additional controls cover 15 repeated holes, disjoint fitted support and the real
committed Step 3 CLI refusing before a value-loader canary. Final focused, mutant,
twin, pins and hosted CI receipts will be recorded after the stable-tree run.

Fresh read-only delta audit (round8_delta_audit) caught an ambiguous new mutant anchor
before harness completion; it was corrected and all 137 anchors match exactly once.
It also identified cheap replay-input-map completeness: config.json and both optional
G0 fallback event files now join the operational source map. A separate regression
failed before that addition; the module's source-list documentation was corrected too.
The independent reviewer ran the seven initial regressions (all passed); root owns
adjudication and all final verification. Preliminary checks overlapped that follow-up;
only stable-tree runs below will be cited as final evidence.

The first focused run also caught the replay changing unused type-T verdict fields;
the existing exact level-R reconstruction regression failed. Replay application is now
restricted to type-A legs, preserving the ruled type-T exclusion/read boundary.
The original reconstruction test plus all eight new tests then passed (9 tests,
26.456 s). The fresh reviewer checked that narrow final code delta and reported no
new findings. This is a Sol delta audit, not the outstanding research/cross-model gate.
The preliminary mutation control also caught a compressed-stream diagnostic regression:
rule replay had preceded the existing span-meter layout gate. That gate now runs first,
preserving the named field-only refusal. The existing compressed-custody regression
discriminates this ordering; no energy or inclusion behavior is relaxed.
The broader focused run found the existing schema-minimal synthetic Step 3 fixture
has no span map. The new time guard now preserves that synthetic-only compatibility
path with a missing-map-safe lookup; non-synthetic missing custody still refuses in
the preceding operational check. Existing Step 3 committed/draft CLI tests cover it.
The combined new/Step 3/time-reader integration run then passed all 70 tests in
219.054 s. Earlier working-snapshot logs are retained as diagnostic evidence, not
claimed as stable-tree passes.

## Process evidence and gate yield

Four bounded turns of the same read-only `round8_delta_audit` agent are indexed in
[the invocation manifest](2026-11-16-pr795-round8-invocations.jsonl). Each row records
the exact prompt/output paths and hashes, stable task id, consumption and PR disposition.
Raw text stays in /Volumes/JW-EXT/scratch/sol-look-r8/audit; the committed report owns
the conclusions. No implementation, final verification, research ruling or merge
authority was delegated.

| Delegated unit | Altitude | Lead-assigned outcome | Catches / misses | Lead rework |
|---|---|---|---|---|
| Initial delta and docs sweep | Bounded judgment | Accepted | Caught ambiguous mutant anchor, replay-input map omission and source-list drift. Root suite subsequently caught T-field, compressed-diagnostic and synthetic-map compatibility cases. | 0 delegated-patch rework minutes; read-only advice, root authored all fixes |
| Type-T compatibility delta | Pinned invariant review | Accepted | Confirmed T stays unread/excluded and unused fields preserved; improved docs precision | 0 |
| Compressed-custody ordering delta | Pinned invariant review | Accepted | Confirmed the prior field-only refusal and replay-before-admission order | 0 |
| Minimal synthetic Step 3 delta | Pinned invariant review | Accepted | Generated-object check confirms missing synthetic span succeeds and missing real custody refuses | 0 |

No prompt-contract violation was identified. The missed compatibility cases show why
the read-only audit did not replace the full focused suite. New regressions caught all
three original number-affecting admission defects before repair. Integration caught
the compatibility cases above; the anchor census caught ambiguity before mutation
scoring. Final local mutation/twin results are recorded below; hosted CI and head receipts are recorded in PR #795 after push. The repository
worktree remained root-owned and quiescent apart from these authorized edits; tests and
the twin wrote private synthetic copies. Generated queue ranks and advisor-visible
project state did not change, so the state kernel and PROJECT_STATUS.md are unchanged.

Whole-repository discovery is excluded by the user's synthetic-only constraint: it
includes real-recording fixtures. No full-suite or live-hardware pass is claimed.

## Research-lead questions (no builder ruling)

Carry all round-7 questions from docs/run_reports/2026-11-15-pr795-round7-builder.md:
N3 clock-fit detector/bound (retain ruled 2 s); four malformed reader shapes; persisted
coefficient schema/code authentication; confirmation of non-admitting R reproduction
and stable fit custody provenance. The seven look-r6/HANDOFF.md questions remain:
clock-fit sign, sub-threshold hidden holes, energy-fit interval scope, unreadable-stream
span exclusions/compressed refusal, ruling ids for hash corrections, desk compression,
Q11 .08 application and the five-world sentence. Existing Q11 evidence is unchanged.
R7-H1 repairs splitting inside the existing fitted union; it does not settle the broader
interval-scope question. No new research decision is issued for these three repairs.

## Final stable-source verification

- Focused synthetic suite: **397 tests, OK (2 optional-dependency skips), 858.669 s**.
  Includes FreezeCommit, all look modules, prediction, the three regression modules,
  host-command guards and expected-failure census. Command and complete output:
  /Volumes/JW-EXT/scratch/sol-look-r8/focused-final3.{json,log}.
- Mutation harness: **137/137 killed, 0 survivors, 0 invalid**, after a passing
  unmodified control. `python3 -B tests/cadence/mutants_fit_interim.py --jobs 3`;
  1010.237 s total, output/receipt in sol-look-r8/mutants-final3.{json,log}.
  All four new guard deletions are killed; all 137 anchors match exactly once.
- Independent twin: **10/10 D/O/C/P/cross sets PASS** using the retained round-7
  independent code, copied without algorithm edits. Established tolerances and
  provenance exceptions are unchanged. Extra receipt custody-map and top-level
  soak_retries fields match exactly; every CLI exit is zero. Evidence:
  sol-look-r8/agreement/{compare.log,compare_result_r6.json,EXTRA-CHECKS.txt,verification.json}.
- Focused and mutation receipts record identical before/after source hashes. The
  twin ran at that same stable manifest SHA-256:
  `054a1402147d854e16b0a233fc56a65e1aff336586be857f60e764505513d9f7`.
- Manifest validate --repo: **ok, draft, 0 placeholders**. Dry pin: **0 changes**.
  `git diff --check`, `scripts/gen_state.py --check`, and process-pointer hashes pass.
  The estimator and committed Step 3 arithmetic files have no diff.

The exact focused command and runner are indexed in
/Volumes/JW-EXT/scratch/sol-look-r8/FINAL-LOCAL-COMMANDS.txt and the committed invocation
manifest. Stable-source results above supersede all working-snapshot/interrupted runs.
Those earlier logs remain as diagnostic evidence; none is counted as a final pass.
Canonical discovery and real-recording checks remain excluded by the user's blinding
constraint. This is synthetic package validation, not live validation or admission.

## Handoff

Local verification and root final diff review are complete. The builder commits with
`Co-Authored-By: Sol 6.1 via codex <noreply@openai.com>`, runs `git pull --rebase` before
push, verifies the exact head's hosted quick, updates sol-look-r8/pr-body.md through
`gh pr edit 795 --body-file`, then re-reads for exact equality. The PR body is the final
hosted-CI/head receipt; this tracked report records local evidence before that push.
No merge is authorized. Next lead action is the carried research questions above and
any quota-dependent final cross-model/research admission; no new Mythos/Claude seat was
started. Generated queue rankings and advisor-visible project state are unchanged.
