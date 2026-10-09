# Block 5, ALPHA attempt 3: consult, cold ruling and decision

Magistrate activation 1aed44f9 (Opus 5.5, headless), 2026-10-09. Structure only. This record follows
`alpha-a3-window.md`. The papers are in `alpha-a3-consult/` beside this file: `BRIEF-body.md` (the brief
both seats had), `sol-consult.md`, `opus-consult.md`, `JUDGE-CHARGE.md`, `RULING.md`, `q1_count.py` and
`q1_count.out`.

## Why a consult

The harvest gave ALPHA attempt 3 the window reasons `neg8.bound_not_derived` and `neg8.screen_failed`.
Brief section 6 sends either code to two blind seats at once. Attempt 1 had also carried
`neg8.bound_not_derived`.

## The two seats (05:35 to 05:46 PDT)

- **Sol 6.1**, effort high, through `codex-run-v3`, empty write scope. Recommendation (b): hold ALPHA
  attempt 4 for the owner's restart, arm nothing meanwhile, and first count why the three corpus members
  failed. As on attempt 1, the launcher exited rc=65 (`run_status=ACCEPTANCE_FAILED`, the report's JSON
  header did not pass its parse); the body is complete and was read as a consult answer, and the parse
  failure is recorded here as a protocol failure of the envelope.
- **Opus 5.5** agent, read-only. Recommendation (c): enlarge the committed NEG-8 corpus from 12 members
  to 18 with the minimum of 10 unchanged, under a new seal; never arm across 00:00 local; ask the owner
  to restart without holding an arm for it.

What both found: the three corpus members that did not succeed can only have been lost before their
request, and the chain's one corpus retry measured nothing, because the runner never launches a member
whose bundle already exists (131 attempts seen = 119 planned + 12 rows the retry logged). With 9 kept
the bound cannot be derived, and the screen failure follows from the missing bound; neither is a harvest
defect. Opus identified the `find` process in the journal as the macOS job `com.apple.tmp_cleaner`,
which starts at 00:00 local every day and walks `/tmp`; the magistrate verified the job's calendar and
its two `find` lines, and measured `/private/tmp` at 149 GiB in 1,226 entries.

## Cold ruling (Fable 5.1, new session, about 05:55 to 06:03 PDT)

The seats disagreed, so the question went to a cold judge. Last line:
`RULING: BUILD-CORPUS-CHANGE-NO-WINDOW-UNDER-OLD-SEAL`.

- Q1 (the count): neither seat's program runs as written; one program, printed in the ruling, may run
  once. It prints fixed labels, code names from closed lists, process names from the open journal and
  integers.
- Q2 (the next arm): build the corpus change now; spend no window under the old seal; do not hold
  anything for the owner's restart, but ask him to do it during the build. The rule: 18 committed
  members, every member runs in every window in the committed order, the bound is derived from every
  member that succeeded and that the mint and the harvest's physics drop keep, the minimum stays 10, the
  one retry stays. The six new members are new run ids with the scientific content of the existing
  twelve, under a new corpus id. Gates: one prospective cold erratum before the build (a Fable 5.1 judge
  and an Opus 5.5 refuter; registration section 10), then the merge gates for code a window executes,
  a new seal and a new measurement clone (registration section 7.5; brief section 9). The block restarts
  at ALPHA; no ALPHA attempt was claim-usable, so no analysed data is lost.
- Two procedure items, adopted now, which change no file a window reads: (a) before every arm,
  `/private/tmp` must be small (the scratch of this project's agent sessions is deleted; the entry count
  is recorded), which removes the cause of the midnight burst; "never arm across 00:00 local" is the
  fallback only if the tree cannot be kept small. (b) A settling wait of 60 minutes, with the display
  asleep (`pmset displaysleepnow`), between any daemon restart, Wi-Fi toggle or owner login and the arm.
- Q3: no error in either seat that changes the ruling. One open defect to explain in the erratum lane:
  the stage `alpha-science-prefill-p2048-abba-06-10` returned rc 1 with 20 of 20 succeeded in both
  chains; it removed nothing.
- Q4: nothing here needs an answer from the owner.

## The count (the ruling's program, run once at about 06:04 PDT, output verbatim)

`q1_count.py` sha256 `06b4cc6d833a768c6e14ae9b150332d0d6db94c60c5e9fce7303394882177667`, extracted from
the ruling by program; arguments: the bound runs root, the claim runs root, the contention journal.

```
bound.admission.attempt1.cpu_busy_ratio_p95_exceeded 3
bound.admission.attempt1.processor_combined_power_w_p95_exceeded 1
bound.admission.attempt2.cpu_busy_ratio_p95_exceeded 3
bound.admission.attempt2.processor_combined_power_w_p95_exceeded 1
bound.admission.attempts.2 3
bound.admission.decision.abort 3
bound.bundles 12
bound.failure_phase.idle_baseline 3
bound.failure_reason.unknown_error 3
bound.join.clock_check.ok 1
bound.join.not_succeeded.baseline_overlaps_over_limit 3
bound.join.offenders_in_not_succeeded_baselines.corespotlightd 2
bound.join.offenders_in_not_succeeded_baselines.find 1
bound.join.offenders_in_not_succeeded_baselines.fseventsd 1
bound.join.offenders_in_not_succeeded_baselines.mds 1
bound.join.offenders_in_not_succeeded_baselines.mds_stores 1
bound.join.offenders_in_not_succeeded_baselines.signpost_reporte 2
bound.join.offenders_in_not_succeeded_baselines.spindump 1
bound.join.succeeded.baseline_clean 7
bound.join.succeeded.baseline_overlaps_over_limit 2
bound.status.failed 3
bound.status.succeeded 9
claim.admission.attempt1.cpu_busy_ratio_p95_exceeded 1
claim.admission.attempt2.cpu_busy_ratio_p95_exceeded 1
claim.admission.attempts.2 1
claim.admission.decision.abort 1
claim.bundles 107
claim.failure_phase.idle_baseline 1
claim.failure_reason.unknown_error 1
claim.join.clock_check.ok 1
claim.join.not_succeeded.baseline_overlaps_over_limit 1
claim.join.offenders_in_not_succeeded_baselines.IMTransferAgent 1
claim.join.offenders_in_not_succeeded_baselines.bird 1
claim.join.offenders_in_not_succeeded_baselines.corespotlightd 1
claim.join.offenders_in_not_succeeded_baselines.deleted 1
claim.join.offenders_in_not_succeeded_baselines.duetexpertd 1
claim.join.offenders_in_not_succeeded_baselines.fileproviderd 1
claim.join.offenders_in_not_succeeded_baselines.mds 1
claim.join.offenders_in_not_succeeded_baselines.mobileassetd 1
claim.join.succeeded.baseline_clean 84
claim.join.succeeded.baseline_overlaps_over_limit 22
claim.status.failed 1
claim.status.succeeded 106
```

Read as the ruling says: the three corpus losses and the one loss in the claim root are idle-admission
aborts (failure phase `idle_baseline`, decision `abort`, a threshold condition on both attempts), and
every aborted baseline overlapped an over-limit interval of the journal. No runner, runtime or telemetry
fault appears. Cause key of ALPHA attempt 3 (registration 7.3): `neg8.bound_not_derived` and
`neg8.screen_failed`, from three physical admission aborts in the corpus stage.

## Decision

The ruling is carried out. Nothing is armed, and no window is armed from the present measurement clone
again. The email to Ed (Gmail message `1a120c4169df6206`, about 06:04 PDT) carries the window's outcome,
the watchdog's pending yield notice, the ruling, and the request to run the Spotlight disable and restart
the Mac during the build; `notice.ack` was written after Gmail accepted it. Correction to one figure in
that email: it says the science stages lost 4 of 200 runs across the two chains; the count is 3 of 200,
and the fourth loss is a start-reference member. The next email to Ed carries the correction.

## Next action (in order; each step is durable before the next begins)

1. Delete this project's scratch under `/private/tmp`, keeping any directory that holds unpushed or
   uncommitted git work and the live session's own task directory; record the entry count after.
2. The prospective cold erratum for the 18-member corpus: its packet is the ruling's Q2 (iii) and (v),
   the count above, and this record. A Fable 5.1 judge and an Opus 5.5 refuter. Its record goes beside
   this file as `corpus18-erratum/`.
3. Build in a linked worktree on a branch from main: six member configurations, the order manifest,
   `derivation/settled_corpus.json` with a new corpus id, each pack's plan tree, the sizing output,
   registration sections 0.12, 5.3 and 5.5; a dry render of each pack's chain showing the corpus stage's
   expected count of 18; an explanation of the rc 1 on the last prefill stage, reproduced on the
   real-model rehearsal archive. Then the merge gates, the new seal commit, the new clone with the ledger
   and pin carried over, a new fixed-values file, and the desk seal check (brief section 9, steps 1 to 4).
4. After the owner's login, if he restarts: `launchctl print-disabled gui/501` lists the two
   photo-analysis agents and `com.apple.corespotlightd` as disabled; `pgrep -x` finds none of the three,
   again after ten minutes; `sysctl -n kern.boottime` has changed; then the 60-minute settle.
5. Arm ALPHA attempt 1 under the new seal by brief section 5, whether or not he has restarted.

An activation that finds this record and no `corpus18-erratum/` directory starts at step 1 or 2,
whichever is not done (step 1 is done when `/private/tmp` holds fewer than about 100 entries).

## Step 1, outcome (06:20 PDT): not done; the fallback is in force

A survey of `/private/tmp` found 654 directories and 572 files of this user, none open by any process
other than this session, no registered git worktree among them, and 121 directories holding git
checkouts (review, mutation and suite scratch of sessions since 2026-09-25). Rather than delete, the
magistrate tried to move the directories to `/Users/edr/night-archive/tmp-parked-20261009` (a rename on
the same volume, which loses nothing). The session's permission check refused the command (reason given:
shared scratch sweep). It was not worked around; the command is logged in
`/Users/edr/night-plan-staging/b5-bench/permission-blocks.log`.

So the ruling's fallback holds until the tree is small: **no window is armed whose span contains 00:00
local.** Two things make the tree small without this session: macOS empties `/private/tmp` at every
boot, so the owner's restart does it; and the midnight job itself deletes files not used for three days.
The check before every arm is the entry count and size of `/private/tmp` (`ls /private/tmp | wc -l`,
`du -sg /private/tmp`); below about 100 entries and 1 GiB the fallback is lifted. No separate email was
sent for this block: the restart already asked of the owner cures it.

Slip to record: after the RUN_STATE hold block was pushed to main (`3f564499e`) and the canonical root
fast-forwarded, this activation ran `git worktree remove` and `git branch -D` for its own temporary
worktree with `-C /Users/edr/code/JouleWise`. Both touch only shared repository metadata and no plan was
armed, but the standing rule allows only the fast-forward there; later worktree commands are run from
the records worktree.

## Step 2, status (06:50 PDT): the erratum is drafted and refuted; the judge is convened

- `corpus18-erratum/ERRATUM.md`: the draft (an Opus 5.5 seat). It verifies that no code a window executes
  fixes the number 12, finds that the three configuration generators do, and corrects the attempt-3
  ruling on one point of science: the drift bound is the larger of two terms, the larger one grows with
  the number of kept members, and the bound is about 20% wider at 18 kept than at 12. It puts ten
  questions to the judge (J1 to J10).
- `corpus18-erratum/REFUTATION.md`: an Opus 5.5 refuter. 3 blockers, 7 majors, 9 minors. It confirms the
  widening by its own simulation and proposes a fourth rule: all 18 run, and the harvest derives the
  deciding bound from the first 12 members in committed order that succeeded, passed the mint and carry
  no physics code, which keeps the bound at its sealed width with a change to desk code only.
- `corpus18-erratum/JUDGE-CHARGE.md`: the charge. A cold Fable 5.1 judge is running on it from the
  worktree `/Users/edr/code/JouleWise-wt-harvest`; it writes `corpus18-erratum/RULING.md`, whose last
  line is `ERRATUM: ADMIT`, `ADMIT-WITH-CORRECTIONS`, `RETURN` or `REFUSED`.

Next action for whichever activation finds this: if `corpus18-erratum/RULING.md` is absent and no
`claude -p --model fable` process is alive, convene the judge again with the same charge (the command is
`claude -p "$(cat JUDGE-CHARGE.md)" --output-format text --permission-mode auto --model fable --effort high --allowedTools "Read,Glob,Grep,Bash,Write"`
run from that worktree). If the ruling exists: commit it; on `ADMIT` or `ADMIT-WITH-CORRECTIONS` apply
the listed corrections to the erratum text and start the build (step 3) in a new linked worktree on a
branch from main, with a Sol 6.1 seat at effort xhigh as the builder and the corrected erratum plus the
ruling as its whole specification; on `RETURN`, redraft what the ruling names and convene once more; a
`REFUSED` goes to Ed by email.

## Step 2 done, step 3 started (07:10 PDT)

- `corpus18-erratum/RULING.md`: `ERRATUM: ADMIT-WITH-CORRECTIONS`. The rule is the refuter's fourth option
  (the ruling's section B): all 18 members run in every window in committed order and nothing else changes
  in the window; at the desk the harvest always builds the deciding bound from the first 12 members, in
  committed order, that succeeded, passed the mint and carry none of the six physics codes (all of them
  if 10 or 11 remain; `neg8.bound_not_derived` below 10). The bound keeps its sealed width. The earlier
  ruling's reason for "all kept" (that it tightens the screen) is withdrawn: the bound's larger term
  grows with the number of members.
- Ed was sent the correction (Gmail `1a120f77842431d2`, on the thread of `1a120c4169df6206`): the rule
  above in place of "all that survive", and 3 of 200 in place of 4 of 200.
- An Opus 5.5 seat is applying the ruling's 14 corrections to `corpus18-erratum/ERRATUM.md` and writes
  `corpus18-erratum/CORRECTIONS-APPLIED.md`.
- Build worktree `/Users/edr/code/JouleWise-wt-corpus18`, branch `lane/2026-10-09-corpus18`, cut from main
  `3f564499e`. A Sol 6.1 seat at effort xhigh is building the window side (the ruling's section D, gates
  1 and 2): brief, report and status in `/Users/edr/night-archive/b5-consults/corpus18-build/`
  (`BRIEF-sol-window-side.md`, `sol-window-side.md`, `sol-window-side.status`). It commits nothing.

Next action, in the ruling's order of gates (section D):
1. When the builder's status file no longer reads `RUNNING`: read its report, verify the per-pack
   `git diff --stat` and the `--check` exit codes yourself, commit the work on the lane branch and push
   it. If the worktree is dirty and no `codex` process is alive, the seat died: inspect, keep what
   passes its checks, and relaunch the same brief for the rest.
2. Gate 3: an independent executing review (Sol 6.1, a new seat), the whole suite on the merged tree
   (the shard runner with Homebrew `python3.13`, not the project environment), CI green, a cold Fable
   pass, findings dispositioned, the Impact statement; merge; the merge commit is the new claim head.
3. Gate 4: the seal commit (three files; the two documents edited from the corrected erratum's section
   4.5 by an Opus seat), the seal landing test, the text gate, the seal record's new section.
4. Gate 5: the harvest lane merges the new seal commit and implements the desk rule with the ruling's
   tests; whole suite; cold Fable pass; the pin addendum; the desk root moved.
5. Gates 6 to 8: the new clone and fixed-values file; the 18-member rehearsal and its harvest; the
   pre-arm checks; then the RUN_STATE top block is rewritten and ALPHA attempt 1 is armed by brief
   section 5.

## Step 3, status (07:40 PDT)

- Desk side (ruling gate 5), started early because it does not depend on the window side: worktree
  `/Users/edr/code/JouleWise-wt-harvest-cap`, branch `lane/2026-10-09-harvest-corpus-cap` (pushed), cut
  from the harvest pin `7e6158d66`. First builder (Sol 6.1 xhigh) done: commit `05897b24c`, one
  production method changed (`neg8_corpus_physics`, 40 lines added, 12 removed), 13 new tests, six
  modules green. It disclosed that the always-on clean bound lets a stored NEG-8 condition clear on the
  re-screen where the sealed text (lines 2838 to 2841) says the screen stays failed. A second Sol seat
  (`BRIEF-sol-desk-fix1.md`, report `sol-desk-fix1.md`, both in
  `/Users/edr/night-archive/b5-consults/corpus18-build/`) is correcting that and reviewing the diff. It
  commits nothing: when its status file no longer reads `RUNNING`, read the report, run the six modules,
  commit and push.
- Window side: the first builder is still running (`sol-window-side.status`).
- The corrected erratum is `corpus18-erratum/ERRATUM.md` (the ruling's 14 corrections applied;
  `CORRECTIONS-APPLIED.md` maps them and holds the lead's seven decisions).
- Still to do on the desk side after the fix: merge the new seal commit into this lane, the whole suite,
  a cold Fable pass, the pin addendum, the desk root moved (ruling section D gate 5).

## Step 3, status (07:50 PDT): the window side is built and in its merge gates

- Window side: branch `lane/2026-10-09-corpus18`, head `985d0722d` (pushed), pull request #492. Verified by
  the lead: per-pack diff is the generator, `plan_tree.json` and `plan_tree.sha256` only; no file under
  `joulewise/` or `scripts/` changed. New digests: order manifest `9cad9987…f36f`, settled corpus
  `c957880a…3304`; plan trees ALPHA `2ec3625a…2809`, BETA `e77e4f6e…0707`, GAMMA `da802897…85bc`; sizing
  `a8e8d530…cfad`; identity pins `513d7d4a…841d` (regenerated by the lead with the recorded default
  arguments; only the three plan-tree digests differ from the sealed file; the pre-arm comparison of
  brief 5.1 with the clone's interpreter passes against it). Sizer: members 125, 125, 107; spans
  106,890, 109,290, 95,754 s; deadlines 110,220, 112,620, 99,060 s.
- Running now, all read-only on that head; papers in `/Users/edr/night-archive/b5-consults/corpus18-build/`:
  the whole suite by the shard method (`suite-window-985d0722d/`, ends with `ALLDONE`); an independent
  executing review (Sol 6.1 high, `sol-window-review.md`, worktree
  `/Users/edr/code/JouleWise-wt-corpus18-review`); the cold Fable pass (`FABLE-window-pass.md`); CI on #492.
- Desk side: the second Sol seat (`sol-desk-fix1`) is still correcting the re-screen guard.

Next action: when all four window-side gates have reported, disposition every finding (fix, defer to a
named lane, or reject with a reason; a recording-only finding is a flag), fill the ledger of #492, and
merge it with a merge commit: that commit is the new claim head. A gate whose output file is missing and
whose process is gone is run again with the brief or charge in the same directory.

## Step 3, status (08:55 PDT)

Window side (`lane/2026-10-09-corpus18`, pull request #492):
- Independent executing review (Sol 6.1 high): `PASS-WITH-FINDINGS`, four findings, all recording-only.
  Cold Fable pass: `FABLE PASS: PASS-WITH-FINDINGS`, one minor (a narrowed blinding assertion in a test)
  and seven recording-only. Reports: `sol-window-review.md`, `sol-window-review.full-report.md`,
  `FABLE-window-pass.md` in `/Users/edr/night-archive/b5-consults/corpus18-build/`.
- Dispositions so far. Fixed: the narrowed assertion (boundary match restored, local commit `94a60fff4`,
  not yet pushed); the CI quick tier's one failure, a G2-b dispatch test that counts the corpus (23 to
  29, pushed as `8c6e95029`); the block-4 replay test that pins the GAMMA pack's bytes (it now allows
  exactly the erratum's three files; in `94a60fff4`). Flags, no fix round: the stale strings of
  deviation 9; the pin registry catching up with an unchanged census program; the disk module's default
  (the plan supplies its own figure: an arm now needs 90.4 GiB for ALPHA and BETA, 80.8 GiB for GAMMA);
  the more negative recorded deadline margin; the seal landing test still authenticating the old seal
  until the new one exists. Deferred to the pre-GAMMA desk check the ruling already orders: the review's
  finding that moving t0 moves the dead-man job by the same amount, so its firing time inside the chain
  (16,560 s after t0 for GAMMA) is fixed relative to the stages.
- Whole suite on `985d0722d` (shard method): not green yet. Failures that are consequences of the change
  and are fixed or being fixed: the two tests above; four tests of `tests.test_neg8_survivors`, whose
  synthetic windows are built from the committed corpus and so now hold 18 members. A Sol seat
  (`BRIEF-sol-window-testfix.md`, report `sol-window-testfix.md`) is establishing the cause of each and
  updating the tests without loosening them; it also reruns alone the wall-clock modules that failed
  under load (`test_sample_quiet_predicate_evidence`, `test_v5_s1_qualification`, one worker-pool test).
  It commits nothing.

Desk side (`lane/2026-10-09-harvest-corpus-cap`, head `49265927d`, pushed): the second seat restored the
re-screen guard (the cap alone never clears a stored NEG-8 condition) and closed a second gap it found
(an unavailable clean bound fell back to the uncapped one); six modules green, 367 tests. A cold Fable
pass on the desk diff is running (`FABLE-desk-pass.md`).

Seal text: an Opus seat is applying the corrected erratum's section 4.5 (39 registration edits, 4
analysis-plan edits) to the two documents in the worktree `/Users/edr/code/JouleWise-wt-corpus18-seal`
(branch `seal/2026-10-09-corpus18-text`, cut from main; it commits nothing) and writes
`corpus18-erratum/SEAL-TEXT-EDITS.md`. The edited files are carried onto the merge commit of #492 as the
seal commit, with the regenerated inventory, after the placeholders are filled.

Next action: when the test-fix seat reports, commit and push the lane, run the whole suite again on the
new head (`/Users/edr/night-archive/b5-consults/corpus18-build/suite-window-985d0722d/` holds the runner;
make a new directory for the new head), wait for CI, fill the ledger of #492 and merge it.

## Step 3, status (10:20 PDT): the window side has passed every gate but CI on its last head

- Pull request #492, head `778e52b0db4822a17efd3d246f34faf56b51fae2`. Its ledger is filled. The gate record
  and the suite summary are on the lane (`docs/process_traces/2026-10-block5/corpus18-erratum/pr492-gates.md`,
  `pr492-suite-summary.txt`) with the dry-render record (`DRY-RENDER.md`, sha256 `7bb10119…f3c2`). The whole
  suite on `a5ae00c46` passed except three wall-clock modules that pass alone. CI was green on
  `a5ae00c46` apart from the ledger check; the two commits since add records only, and CI is running on
  the new head.
- Desk side, head `273fc48db` (pushed): cold Fable pass `PASS-WITH-FINDINGS` (`FABLE-desk-pass.md`); its
  one major finding (a failure disclosure lost when the re-screen does not run) and its minor one (a
  wrong count in a record after an order-check failure) are fixed by a Sol seat (`sol-desk-fix2.md`),
  six modules green, 369 tests. Still owed on the desk side: merge the new seal commit into the lane, the
  whole suite on that tree, a cold Fable pass on that tree (it covers the delta of the fix), the pin
  addendum, the desk root moved.
- Seal text: prepared on branch `seal/2026-10-09-corpus18-text` (`8ce450ad5`, pushed), record
  `corpus18-erratum/SEAL-TEXT-EDITS.md`. The text gate (an Opus reader, one pass) is running on it and
  writes `corpus18-erratum/TEXT-GATE.md`; it edits the two files in the worktree
  `/Users/edr/code/JouleWise-wt-corpus18-seal` and commits nothing.

Next action, exactly:
1. `gh pr checks 492 --repo mpmdw/JouleWise`: when every check passes, `gh pr merge 492 --repo
   mpmdw/JouleWise --merge`. The merge commit is the new claim head. (No night job is loaded and no plan
   is armed.) Do not fast-forward the canonical root yet: the RUN_STATE hold stays as it is until the new
   clone exists.
2. The seal commit, as the merge commit's only child, on a branch cut from it: copy the two documents from
   the seal-text worktree (after `TEXT-GATE.md` ends `TEXT GATE: PASS` and its edits are committed there),
   fill `<NEW_H_CLAIM>` with the merge commit, `<SEAL_DATE>` with the date, `<REGISTRY_SHA256>` with
   `shasum -a 256 configs/pins/registry.json` at the merge commit; generate the inventory from a clean
   checkout of the merge commit (`/opt/homebrew/bin/python3.13 -B
   docs/process_traces/2026-10-07-block5-seal/bench/make_sealed_inventory.py <checkout> <out.json>`);
   commit the three files; `python3.13 -m unittest tests.test_b5_seal_landing` must pass; push it to
   main as a fast-forward of the merge commit (the first seal did the same); add the new digests to the
   seal record.
3. Then the desk side's remaining gates, the new clone, the rehearsal and the pre-arm checks, as the
   ruling's section D gates 5 to 8 list them.

## Step 3, status (11:00 PDT): the new claim head exists; the second seal is in its pull request

- Pull request #492 merged at 10:42 PDT with every gate recorded. **New claim head (H_claim):
  `c27485347c9629b857df81665b5b1b8d10dcd36a`.**
- **New seal commit: `be6525e5a6511adf882282e404e163e14dbb738b`**, only parent the claim head, three files.
  Registration sha256 `c7b3fdf7…db3f`, analysis plan `23ef67f5…4859`, sealed inventory `80852d98…c4dc`
  (682 files). The seal landing test and the pin census test pass there. The text gate passed after 17
  corrections (`corpus18-erratum/TEXT-GATE.md`). The full digests are in the new section "Erratum 1: the
  second seal" of `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md`.
- Pull request #493 (branch `seal/2026-10-09-corpus18`, worktree
  `/Users/edr/code/JouleWise-wt-corpus18-sealcommit`): the seal commit, a merge of this records branch,
  and a record commit. Its ledger is filled; CI is running. **When every check passes:
  `gh pr merge 493 --repo mpmdw/JouleWise --merge`.** After that merge, new records are committed in this
  worktree as before; this branch is then merged to main again at the next records step.
- The clone consult (Sol 6.1 xhigh) has answered: `/Users/edr/night-archive/b5-consults/corpus18-build/
  sol-clone-consult.md`. Its findings that bind the next steps: the new seal's tree carries pin 402, so
  the new clone's first commit after checkout is a byte copy of the old clone's committed pin (sequence
  422, head digest `1ae51d38…f717`) made with `git commit --only`, with the ledger file copied from the
  old clone (422 rows, file sha256 `0af3448c…aa69`); the plan writer, the installer and the harvest's
  code-identity comparison accept that shape (proved on a scratch clone); the environment needs the lock
  file's packages offline (a wheelhouse whose completeness it could not verify); the rehearsal runs from
  a private clone with its own ledger copy. Its section 2 has the ordered commands; read all of it
  before gate 6.
- Desk side: the seal commit is merged into the harvest lane (`d58913476`, not yet pushed with its test
  fixes). Outside `tests/`, the lane differs from the seal commit in exactly the three harvest program
  files. A Sol seat (`BRIEF-sol-desk-merge.md`, report `sol-desk-merge.md`) is making the lane's tests true
  for the 18-member committed corpus; it commits nothing.

Next action after #493 merges and the desk seat reports: commit and push the lane; the whole suite on it;
a cold Fable pass on `git diff be6525e5a..<lane head>` (the three program files and tests; charge
`FABLE-desk-pass-charge.md` adapted to the new range); a pull request for the lane with the
`B5-HARVEST-PIN:` addendum to the seal record (Addendum 2) in it; merge; move the desk root to the lane
head; then gate 6 from the clone consult's commands.

## Status (11:40 PDT): second seal on main, second clone built, the desk side in its last gates

- Pull request #493 merged at 11:14 PDT (`2823f4b88`); the seal commit `be6525e5a` is on main and the
  canonical root is fast-forwarded. `B5-ARM-RELEASED:` still reads `none`.
- The second measurement clone is built and verified: `second-clone.md` beside this file. The
  fixed-values file names it.
- Desk side, branch `lane/2026-10-09-harvest-corpus-cap`, head `224a264c5` (pushed): the seal commit is
  merged in; the lane's tests use the committed 18-member corpus (a Sol seat, no production change).
  Program file digests at that head: `joulewise/b5/harvest.py` `8aaaf96f…dd2a`,
  `joulewise/whole_window.py` `ee107b1e…25a5`, `scripts/harvest_b5_window.py` `88ac1164…6d45` (the last
  two are unchanged from the first harvest pin). Running now: the whole suite
  (`suite-desk-224a264c5/` in `/Users/edr/night-archive/b5-consults/corpus18-build/`, ends `ALLDONE`) and
  the cold Fable pass (`FABLE-desk-pass2.md`, charge `FABLE-desk-pass2-charge.md`).
- The rehearsal's first run was refused by the arm's sampler-cadence check because the machine was busy
  with tests; it is run again when the suite has finished (`second-clone.md`).

Next action, exactly:
1. When the suite and the cold pass have reported: disposition the findings (a number-integrity finding
   gets a Sol fix seat and a delta check; a recording-only one is a flag). Then, in the lane's worktree
   `/Users/edr/code/JouleWise-wt-harvest-cap`: append "Addendum 2" to
   `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md` with the line `B5-HARVEST-PIN: <the commit
   the desk root will be checked out at>` (the lane head that holds the program; the addendum commit
   itself comes after it and changes documents only), the three digests, and the paths of the review and
   the cold pass; add a gate record; open the pull request with the ledger; merge when CI is green; then
   `git -C /Users/edr/code/JouleWise pull --ff-only`.
2. Move the desk root: `git -C /Users/edr/night-custody/desk/b5-harvest fetch --no-tags
   /Users/edr/code/JouleWise <pin commit> && git -C /Users/edr/night-custody/desk/b5-harvest checkout -q
   --detach <pin commit>`; then the pin test of brief 4.5 must print `HARVEST_PINNED`. The test takes the
   last `B5-HARVEST-PIN:` line that names the desk head; the first seal's line stays in the record.
3. The rehearsal: a new base under `/Users/edr/night-archive/gate-prune/rehearsal-real/`, `prepare` and
   `run` as in `second-clone.md`, from `/Users/edr/code/JouleWise-wt-seal2-rig`, with no test suite
   running; then the private pin advance and the harvest by the pinned program (clone consult section 5).
4. Pre-arm (ruling gate 8), then rewrite the RUN_STATE top block, set `B5-ARM-RELEASED: alpha beta gamma`,
   and arm ALPHA attempt 1 by brief section 5 from the new clone. `/private/tmp` still holds this
   project's scratch, so until it is small (under 1,000 entries by `find /private/tmp -mindepth 1 | wc
   -l` and under 1 GiB) no window is armed whose span contains 00:00 local: with a span of about nine
   hours that means an arm between 00:10 and about 14:30 local.
