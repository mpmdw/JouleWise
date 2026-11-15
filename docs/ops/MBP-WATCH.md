# MBP span watcher in GitHub Actions (RL-173 C) and the off-host desk (RL-173 B)

Workflow: `.github/workflows/mbp-watch.yml`. Script: `scripts/mbp_watch.py` (`watch` and `read`). Tests:
`tests/test_mbp_watch.py`. Ruling: RL-173 C makes a GitHub Actions watcher satisfy RL-149 §2.8 line 7,
permanently, so the alarm works when the Air and the lead are both away.

## What the watcher does

Every 10 minutes (and on `workflow_dispatch`) on `main`:

| Code | When | Detail |
|---|---|---|
| `SPAN_SILENT` | `docs/process/CURRENT.json` names an armed span and no results ref (`desk-bundles/<plan>` or `night-results/<plan>`) exists after its deadline plus 1,200 s (C.1) | `NO_RESULTS_REF` |
| `SPAN_STOP` | `desk-bundles/<plan>`: `transition.json` status other than `CLOSED_OK`; `night-results/<plan>`: fault, a non-zero chain exit or an outcome other than `COMPLETE` | the status, `FAULT`, `CHAIN_EXIT_<n>` or `OUTCOME_<word>` |
| `DESK_HOLD` | `cadence-desk-final/<plan>`: `desk_verdict.json` has `next_arm_hold: true` | the hold code, or `MULTIPLE` |
| `RESULT_UNREADABLE` | one of those records is missing or malformed | which record |
| `CURRENT_INVALID` | CURRENT.json cannot be read | `POINTER` |

- **Which spans.** The armed span, and every `cq-*` plan whose ref commit is under 48 h old. All tips are
  fetched in one round trip; only the three named files are read.
- **The deadline** is the pointer's `wait.deadline_epoch_s`, or `armed.latest_end_epoch_s` when there is none.
- **Issues (C.2, C.3).** One `mbp-alarm` issue per event, titled `mbp-alarm <CODE> <span> <detail> [<sha12>]`,
  assigned to the repository owner and opening with an `@owner` mention, so the owner is notified by
  GitHub (mail and app). The lead sees it the same way (the Air watcher's `gh` reads, or any session).
  The body holds the span id, the code, the ref and short sha, the times (UTC and epoch) and the run link.
  Every value is checked against a fixed pattern first; no record text is copied. An event already
  filed (open or closed) is not filed again.
- **Fail loud.** A git or API failure fails the run (GitHub mails the workflow's owner on a failed
  scheduled run), and the arm's read refuses on it.

## The arm's read (C.4)

Each arm runs, before arming:

```sh
python3 scripts/mbp_watch.py read --repo mpmdw/JouleWise --after-epoch "$PREVIOUS_CLOSE_EPOCH"
```

It reads `GET /repos/mpmdw/JouleWise/actions/workflows/mbp-watch.yml/runs?branch=main&status=completed`.
Exit 0 only if the latest completed run succeeded **and** started after the previous span's close, and no
`mbp-alarm` issue is open. 20: no such run yet (wait; the next run is at most about 10 min away, more when
GitHub delays schedules); 21: an alarm is open (it holds until the lead closes it); 22: the latest run
failed; 2: API or usage error. The repository is public, so no token is needed (60 requests an hour
per address); `GH_TOKEN` is used when set. On the MBP this is one HTTPS request, no `gh` keychain.

## What the pointer must carry (process change for the lead)

The watcher learns the running span only from CURRENT.json on `main`. Today's pre-launch items (for
example item 345) carry no `pointer` block, so the watcher would see no armed span and could not alarm
on silence. For line 7 to hold:

- the **pre-launch record** carries a pointer block naming the span:
  `armed: <plan id>`, `host: mbp`, `t0: <launch, ISO with offset>`, `latest_end: <the runner's DEADLINE>`,
  `wait: results_branch_exists`, `deadline: <the runner's DEADLINE>`, plus `owner`, `next_observable` and
  `on_early_or_refused`; then `scripts/gen_current.py` and CURRENT.json in the same commit;
- the **Check record** after the close carries a pointer block without `armed`, which clears the span.

Until the controller pushes `desk-bundles/<plan>` (PR #800), a span publishes no results ref at all (see
below), so silence is "the armed pointer is still there after the deadline plus the grace": the
magistrate's Check item is what clears it. Stops are then reported by the magistrate's own Check mail;
the watcher adds `SPAN_STOP` and `DESK_HOLD` once the bundle and verdict refs exist.

## Install

Nothing to install on either Mac. The schedule starts when the workflow is on `main`. Run it once by
hand to make the first completed run and the label:
`gh workflow run mbp-watch.yml --repo mpmdw/JouleWise`, then `gh run list --workflow mbp-watch.yml`.
To check delivery once: push a scratch branch whose CURRENT.json arms a synthetic span id (for example
`cq-notify-test-a1`) with a past deadline, run `gh workflow run mbp-watch.yml --ref <that branch>` (a
dispatch reads the branch's files), confirm the owner got the `mbp-alarm SPAN_SILENT cq-notify-test-a1`
notification, then close the issue and delete the branch. GitHub pauses
schedules in a repository with no activity for 60 days; this repository is active daily.

## The off-host desk in Actions (RL-173 B): what is missing

RL-173 B asks for the deterministic desk to re-check every span in GitHub Actions from the pushed bundle.
**The bundle is not a pushed ref yet**, so this PR does not build it. Checked 2026-11-15 15:16 PST:
`git ls-remote origin 'refs/heads/desk-bundles/*' 'refs/heads/cadence-desk-final/*'
'refs/heads/night-results/cq-*'` returns nothing.

What is missing, in order:
1. **The push.** Spans today run on the runner pin `b4b6aeb19`, armed by hand. The runner writes
   `OUT/desk-bundle/` but pushes nothing, and `cq-*` plans never go through `run_night`'s results
   publisher. The controller that packs, signs (`cadence-controller` SSH key) and pushes
   `refs/heads/desk-bundles/<plan>` is PR #800 (`desk_transport.sign_bundle` and the close step,
   FORMAT section 1), not merged.
2. **The desk command.** `scripts/air/cadence_desk.py final --bundle-ref ...` and its library are PR #799,
   not merged. The Actions job must run it at the commit the Air's desk runs (RL-173 B), so that commit
   has to be pinned somewhere the workflow reads (a small config on `main`).
3. **Public keys.** The `cadence-controller` allowed-signers line (to verify bundles) and the
   `cadence-desk` line (for `--history-signers`) must be committed or set as repository variables. They
   are public keys; no secret is needed.
4. **Where the Actions verdict goes, and what "disagree" means.** `verdict_sha256` covers `built_at` and
   the host, so two desks never match byte for byte. Proposal: compare `desk_final`, `next_arm_hold`, the
   sorted hold and stop codes and `summary_sha256` with the tip of `cadence-desk-final/<plan>`; a
   difference opens `mbp-alarm DESK_DISAGREES <plan>`, which the arm's read already refuses on. The
   verdict itself stays a run artifact (no new ref, no signing key in Actions).
5. **A research-lead question.** RL-173 B lets the MBP run the desk in the close interval and count it
   for line 9. Under FORMAT section 3 the verdict ref is signed by `cadence-desk`, whose key is on the
   Air. Whether the MBP's desk signs with its own principal, and which verdict the Actions re-check
   compares against, is not settled by the ruling text.

When 1 to 3 exist, the job is a scheduled step beside the watcher: fetch new `desk-bundles/*` tips, run
`cadence_desk.py final` at the pinned commit with no hand table (a `HAND_TABLE_DUE` pending is expected
and is not a disagreement), and compare as in 4.
