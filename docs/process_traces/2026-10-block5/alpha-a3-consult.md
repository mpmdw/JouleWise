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
