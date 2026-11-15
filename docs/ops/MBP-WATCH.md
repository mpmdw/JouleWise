# MBP span watcher in GitHub Actions (RL-173 C) and the off-host desk (RL-173 B)

Workflow: `.github/workflows/mbp-watch.yml`. Script: `scripts/mbp_watch.py` (`arm`, `close`, `watch`,
`read`). Tests: `tests/test_mbp_watch.py`. Ruling: RL-173 C makes a GitHub Actions watcher satisfy RL-149
§2.8 line 7, permanently, so the alarm works when the Air and the lead are both away.

## The span's two records (the MBP side)

The watcher does not infer the running span from a pointer. Each span declares itself on a durable ref:

```sh
# Before the launch, after every other Start-and-check line; if it fails, do not launch:
python3.13 -B scripts/mbp_watch.py arm --plan "$PLAN" --t0 "$LAUNCH_EPOCH" --deadline "$DEADLINE"
# In the span's Check, after the receipt (CLOSED_OK only for a clean close; otherwise the stop's status):
python3.13 -B scripts/mbp_watch.py close --plan "$PLAN" --status CLOSED_OK --close-epoch "$RECEIPT_ENDED"
```

- `arm` pushes a parentless commit to `refs/heads/span-watch/<plan>` with `arm.json`: plan id, t0 and the
  **runner's deadline** (the `--deadline` the runner is given). It is create-only: a second arm for the same
  plan id is rejected by the remote, because the push never forces.
- `close` adds `close.json` (plan id, one of `CLOSED_OK`, `STOPPED`, `REFUSED`, `FAULT`, `STRANDED`,
  `CLOSE_UNPROVEN`, close time) as a fast-forward child. A second close is refused.
- Both records hold operational fields only. They run from the same checkout the magistrate already pushes
  RUN_STATE from (`--remote` overrides the origin URL). Run them at the arm boundary and in the Check, never
  during a measurement.
- When the PR #800 controller pushes `desk-bundles/<plan>`, a bundle whose `transition.json` is bound to the
  arm (same plan id, `t0_epoch` within [arm t0 - 900 s, arm deadline]) also resolves the span; `close` stays
  the magistrate's own record either way.

## What the watcher does

Every 10 minutes (cron `3-59/10`, off the hour's peak; GitHub does not guarantee punctual schedules) and on
`workflow_dispatch`, it lists `span-watch/*`, `desk-bundles/*` and `cadence-desk-final/*` live, fetches all
tips in one round trip and reads only `arm.json`, `close.json`, `transition.json` and `desk_verdict.json`.

| Code | When | Detail |
|---|---|---|
| `SPAN_SILENT` | an arm record with no close record and no bound bundle after its deadline + 1,200 s (C.1) | `NO_RESULTS_REF` |
| `SPAN_STOP` | a close record or bound bundle with a status other than `CLOSED_OK` | the status |
| `DESK_HOLD` | a verdict with `next_arm_hold: true` | the hold code from the FORMAT's code list, `UNKNOWN_HOLD`, `MULTIPLE` or `UNNAMED` |
| `RESULT_UNREADABLE` | a malformed arm, close, transition or verdict record, or a bundle not bound to the arm | `ARM_RECORD`, `CLOSE_RECORD`, `TRANSITION`, `TRANSITION_MISBOUND`, `DESK_VERDICT` |

- **No age limit.** An obligation lasts as long as its ref; there is no lookback that can drop a stop the
  watcher has not seen. Deleting a `span-watch` ref deletes its obligation: only the lead deletes refs.
- **Issues (C.2, C.3).** One `mbp-alarm` issue per event, titled `mbp-alarm <CODE> <span> <detail> <sha12>`,
  assigned to the repository owner and opening with an `@owner` mention. Every word comes from the closed
  vocabularies in `scripts/mbp_watch.py`; a record's own strings are never copied (an unknown hold code
  prints as `UNKNOWN_HOLD`). The body holds the span id, code, detail, ref, short sha, times and run link,
  and a hidden key `CODE:span:detail:sha`.
- **Episodes.** The key includes the ref's commit, so a later commit on the same span (for example a close
  after a silence) is a new event, and the same commit is never filed twice. Closing an issue is the lead's
  acknowledgement that the event is handled.
- **Fail loud.** A failed listing, fetch or issue read, or an issue that GitHub does not return with the
  label and the assignee, fails the run. A run that files an alarm succeeds; the arm's read then refuses on
  the open issue.
- **Who is notified.** GitHub notifies the owner of the assignment and the mention (mail and the app, per the
  owner's notification settings). The lead is not notified by GitHub as a separate person: the lead sees open
  alarms at each arm through `read`, and should add `gh issue list --label mbp-alarm --state open` to its own
  Air watcher (not built here). A failed scheduled run is reported by GitHub to the user who last changed the
  schedule, subject to that user's settings; it is not a guaranteed channel, which is why the arm's read
  refuses on a failed or missing run.

## The arm's read (C.4)

```sh
python3 scripts/mbp_watch.py read --repo mpmdw/JouleWise --after-epoch "$PREVIOUS_CLOSE_EPOCH"
```

It reads `GET /repos/mpmdw/JouleWise/actions/workflows/mbp-watch.yml/runs?branch=main&status=completed`. The
latest completed run is the one with the highest `run_number` (then `run_attempt`). Exit 0 only if it
succeeded, started after the previous span's close and within `--max-age-s` (default 7,200 s), and no
`mbp-alarm` issue is open. 20: no such run yet (wait; schedules can be late); 21: an alarm is open; 22: the
latest run failed; 2: API or usage error, including any malformed answer and a start time in the future.
No token is needed for this public repository (60 requests an hour per address); `GH_TOKEN` is used when
set. The PR #800 controller must call it at every arm (RL-173 Owners: the controller builder owns "the
watcher read"); until then the magistrate runs it as an arm line.

## Install

Nothing to install on either Mac beyond the checkout the magistrate already uses. The schedule starts when the
workflow is on `main`. Then:
1. `gh workflow run mbp-watch.yml --repo mpmdw/JouleWise` once, and `gh run list --workflow mbp-watch.yml`
   to see the first completed run.
2. A delivery check, synthetic only: `scripts/mbp_watch.py arm --plan cq-notify-test-a1 --t0 <now-7200>
   --deadline <now-3600>` from the Air, dispatch the workflow, confirm the owner received the
   `mbp-alarm SPAN_SILENT cq-notify-test-a1` notification, then `close --plan cq-notify-test-a1 --status
   CLOSED_OK --close-epoch <now>`, close the issue and delete the `span-watch/cq-notify-test-a1` ref.
3. Add the `arm` and `close` lines to the magistrate's launch and Check procedures, and the `read` line to
   the arm checklist (a lead item).

## The off-host desk in Actions (RL-173 B): not built here

RL-173 B asks for the deterministic desk to re-check every span in GitHub Actions from the pushed bundle.
**This PR does not build it, and RL-173 B stays open.** Checked 2026-11-15 15:16 PST:
`git ls-remote origin 'refs/heads/desk-bundles/*' 'refs/heads/cadence-desk-final/*'
'refs/heads/night-results/cq-*'` returns nothing, so no bundle exists to re-check.

What is missing, in order:
1. **The push.** Spans today run on the runner pin `b4b6aeb19`, armed by hand. The runner writes
   `OUT/desk-bundle/` but pushes nothing, and `cq-*` plans never go through `run_night`'s results
   publisher. The controller close step that packs, signs (`cadence-controller`) and pushes
   `refs/heads/desk-bundles/<plan>` is PR #800 (`desk_transport.sign_bundle`), not merged.
2. **The desk command** `scripts/air/cadence_desk.py final --bundle-ref ...` is PR #799, not merged. The job
   must run it at the commit the Air's desk runs, pinned in a small config on `main`.
3. **Authenticated inputs.** `final` needs `--kit` (the kit file the queue entry pins, checked by hash), the
   queue at `queue.commit:queue.path` from the transition (verified against `queue.sha256`), the
   `cadence-controller` allowed-signers line, and for `--history-prefix` the earlier signed verdict refs with
   the `cadence-desk` line. Both desks must use the same history snapshot (pin the history refs' commits),
   or a later verdict manufactures a disagreement. The signer lines are public keys; no secret is needed.
4. **The comparison.** PR #799 already has `desk_final.agreement_view` and `compare_verdicts`, which compare the
   automatic part of two verdicts and exclude later hand inputs (`HAND_TABLE_DUE` against a hand-completed
   verdict is not a disagreement). The Actions desk should use them, not a new comparison. A disagreement
   files `mbp-alarm DESK_DISAGREES <plan>` (a new closed code), which the arm's read already refuses on.
5. **Coverage.** Every bundle must be checked once, retried after a failed run, and marked checked (for
   example a `desk-recheck/<plan>` ref holding the agreement result), so a missed schedule never skips a
   span; no time lookback.
6. **Routing to the research lead.** RL-173 B says a disagreement "comes to me". An owner issue alone does
   not reach the research lead; the lead relays it as a ruling request.
7. **A question for the research lead.** RL-173 B lets the MBP run the desk in the close interval and count
   it for line 9. PR #799's CLI already has `publish --principal` (naming `cadence-controller` for an MBP desk),
   `--no-push` and `--history-principal`, while FORMAT section 3 says verdicts are signed by `cadence-desk` on
   the Air. Which principal the MBP desk signs with, and which verdict the Actions re-check compares against
   when both exist, is not settled by the ruling text.
