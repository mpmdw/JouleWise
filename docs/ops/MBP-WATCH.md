# MBP span watcher in GitHub Actions (RL-173 C) and the off-host desk (RL-173 B)

Workflow: `.github/workflows/mbp-watch.yml`. Script: `scripts/mbp_watch.py` (`init-log`, `arm`, `close`,
`watch`, `read`). Tests: `tests/test_mbp_watch.py`. Ruling: RL-173 C makes a GitHub Actions watcher satisfy
RL-149 §2.8 line 7, permanently, so the alarm works when the Air and the lead are both away.

## The span log (the MBP side)

The watcher does not infer the running span from a pointer. Each span declares itself, and its close, in
one append-only branch, `refs/heads/span-watch/log`:

```sh
# Before the launch, after every other Start-and-check line; if it fails, do not launch:
python3.13 -B scripts/mbp_watch.py arm --plan "$PLAN" --t0 "$LAUNCH_EPOCH" --deadline "$DEADLINE"
# In the span's Check, after the receipt (CLOSED_OK only for a clean close; otherwise the stop's status):
python3.13 -B scripts/mbp_watch.py close --plan "$PLAN" --status CLOSED_OK --close-epoch "$RECEIPT_ENDED"
```

- Each record is one commit that **adds** one file: `arms/<plan>.json` (plan id, the attempt from the plan
  id's required `-a<N>` suffix, t0, and the **runner's deadline**, the `--deadline` the runner is given) or
  `closes/<plan>.json` (plan id, one of `CLOSED_OK`, `STOPPED`, `REFUSED`, `FAULT`, `STRANDED`,
  `CLOSE_UNPROVEN`, close time). Pushes never force; a concurrent record is re-read and retried.
- A second, different record for the same plan is refused (`RECORD_EXISTS`); the same bytes again (a retry
  after a lost acknowledgement) is a no-op. `close` refuses without an arm, before the arm's t0, or more
  than 300 s ahead. Epoch arguments must be finite and in 2026-2029.
- Both run from the checkout the magistrate already pushes RUN_STATE from (`--remote` overrides the origin
  URL), at the arm boundary and in the Check, never during a measurement.
- **The log is the only results ref this watcher reads.** A controller that pushes desk bundles (PR #800)
  must push `close` too; a bundle alone resolves nothing here. Desk holds (`cadence-desk-final`) are the
  controller's own arm gate under line 9, not line 7, so this watcher does not read verdicts; nothing it
  reports can be lost by deleting a ref outside the protected log.

**Why one log, and the rule that protects it.** Every run re-reads the log's whole history: the root commit
must hold only `README`, and every later commit must have one parent and add exactly one new
`arms/` or `closes/` file. Anything else, a modified or removed record, or a path removed and added again,
is `RESULT_UNREADABLE LOG_REWRITTEN`, and the first addition of every record still counts. Deleting or force-moving the branch
is blocked by a repository ruleset, and the watcher fails its run (so every arm's read refuses) unless
`GET /repos/mpmdw/JouleWise/rules/branches/span-watch/log` shows active `deletion` and `non_fast_forward`
rules on that exact branch, or if the branch is missing. The lead, once:

```sh
python3.13 -B scripts/mbp_watch.py init-log            # the root commit
gh api -X POST repos/mpmdw/JouleWise/rulesets --input - <<'JSON'
{"name": "span log: no deletion, no rewrite", "target": "branch", "enforcement": "active",
 "conditions": {"ref_name": {"include": ["refs/heads/span-watch/log"], "exclude": []}},
 "rules": [{"type": "deletion"}, {"type": "non_fast_forward"}]}
JSON
```

Because closes live in the same protected log, a recovered span cannot lose its recovery evidence, so a
silence filed once never needs re-filing.

## What the watcher does

Every 10 minutes (cron `3-59/10`, off the hour's peak; GitHub does not guarantee punctual schedules) and on
`workflow_dispatch`, it fetches the log and reads only its records.

| Code | When | Detail |
|---|---|---|
| `SPAN_SILENT` | an arm with no close visible by its deadline + 1,200 s (C.1). "Visible" is the later of the close's own time and its **server-side push time**, read from GitHub's repository activity API (`GET /repos/mpmdw/JouleWise/activity?ref=refs/heads/span-watch/log&activity_type=push&time_period=quarter`, all pages): each record is pushed alone, so its own push row is its publication time (fractional seconds kept); without one, a later record's push is only an upper bound. So a close that finished late, was pushed late, or arrived between two delayed polls is still filed. A close the API does not show yet counts as visible only at this observation (conservative). GitHub's own push row is honoured at any age. A close older than the activity window with no row left is judged by its own time: every watcher run while it was inside the window judged it with exact evidence, and a run that follows a gap in the watcher's own runs files `WATCHER_GAP` (below), so a close first seen after an outage is never accepted silently | `NO_RESULTS_REF` |
| `SPAN_STOP` | a close with a status other than `CLOSED_OK` | the status |
| `WATCHER_GAP` | no other successful run of this workflow started in the 2 h before this one (an outage, or the very first run; keyed by this run, so every recovery is its own issue): whatever the log gained meanwhile was not judged as it happened. The lead reads the log's records for that time and closes the issue; the arm's read refuses until then | `NO_RECENT_RUN` |
| `RESULT_UNREADABLE` | a malformed arm or close, a close without an arm, or a log commit that is not one addition | `ARM_RECORD`, `CLOSE_RECORD`, `LOG_REWRITTEN` |

- **No age limit.** An obligation lasts as long as the log, which cannot be deleted or rewritten; there is no
  lookback that can drop a stop the watcher has not seen. Legacy `night-results/*` refs are not read here:
  the Air's `night_results_watch.py` keeps covering them.
- **Issues (C.2, C.3).** One `mbp-alarm` issue per event, titled `mbp-alarm <CODE> <span> <detail> <sha12>`,
  assigned to the repository owner and opening with an `@owner` mention. The issue holds closed-vocabulary
  codes and details, the span id, the log ref, a record id (hex), times and the run link, and a hidden key
  `CODE:span:detail:id`; no other field of a record is copied. The span id is the one producer string that
  reaches the issue: `arm` accepts only the campaign form `cq-<lower-case words>-a<N>` (at most 64
  characters), and producers must use the registered, public span ids.
- **Episodes.** A stop or an unreadable record is keyed by the commit that carries it, so a new record is
  a new event and the same one is never filed twice. A silence is keyed by the arm's commit, so it is
  filed once per launch. Closing an issue is the lead's acknowledgement that the event is handled. An open
  issue that was created without the label or the assignee (found by its creator, `github-actions[bot]`, and its hidden key) is repaired on the next run, and the run fails
  until GitHub confirms both.
- **Fail loud.** A failed listing, fetch or issue read, a missing log or ruleset, or an issue that GitHub
  does not return with the label and the assignee, fails the run. A run that files an alarm succeeds; the
  arm's read then refuses on the open issue.
- **Who is notified (C.3).** Ed: GitHub notifies the owner of the assignment and the mention (mail and the
  app, per the owner's notification settings). The lead: the Air watcher agent
  (`scripts/air/air_watch_agent.py`, the installed `com.joulewise.air-watch`) polls every open `mbp-alarm`
  issue (all pages) on its 900 s CI tick (`mbp_watch.alarm_poll`, public API, no token) and posts one macOS
  notification per issue, `ALARM MBP_ALARM issue-<n>/<code>/<span>` (identity first: the banner keeps 80 characters), logged to
  `~/Library/Logs/JouleWise/air-watch.log`. An issue is acknowledged only after the notifier reports success;
  a failed banner is retried at the next tick. It takes effect when the lead updates the agent's checkout to
  this merge. When the Air is off, the lead sees the alarm at its next session and at every arm through
  `read`. A failed scheduled run is reported by GitHub to the user who last changed the schedule, subject
  to settings; it is not a guaranteed channel, which is why the arm's read refuses on a failed or missing run.
- **Schedules are not punctual.** GitHub can delay or drop scheduled runs. A silence is filed at the first
  run after the limit, or reconstructed later from a late result; a watcher that stops running cannot alarm,
  and the arm's `read` refuses stale evidence instead.

## The arm's read (C.4)

```sh
python3 scripts/mbp_watch.py read --repo mpmdw/JouleWise --after-epoch "$PREVIOUS_CLOSE_EPOCH"
```

It enumerates every completed run of the workflow on `main` created in the last 31 days, GitHub's re-run
horizon (`GET /repos/mpmdw/JouleWise/actions/workflows/mbp-watch.yml/runs?branch=main&status=completed&created=<day>..<day+1>`,
one window per day, each paginated and checked against its `total_count`). The latest is the most recently
started execution among them (a re-run counts with its own start; ties by `run_number`, then `run_attempt`),
so a newer failed re-run of an old run is the latest and refuses. The workflow also fails every re-run on
purpose (its first step), so a re-run can only ever refuse an arm, never pass one. Exit 0 only if the latest
succeeded, started after the previous span's close and within `--max-age-s` (default 7,200 s), and no
`mbp-alarm` issue is open. 20: no such run yet (wait; schedules can be late); 21: an alarm is open; 22: the
latest run failed; 2: API or usage error, including any malformed answer and a start more than 300 s in the
future (clock skew up to 300 s is accepted). A success stays usable for at most `--max-age-s`; it is bounded
evidence, not proof that the watcher is still running.
The read makes about 65 API calls (two pages for each of 32 day windows at 144 runs a day, and the issue list), so it needs `GH_TOKEN` (any token that can read this public repository;
on the MBP, `gh auth token` in the GUI context); unauthenticated, GitHub allows 60 an hour per address and
the read then fails closed. **The remaining caller work (RL-173 Owners: the controller builder owns "the watcher read").** PR #800
already reads the Actions API at each arm (`read_watcher_run`), but it checks only the run, not open
`mbp-alarm` issues, and it does not publish `arm`/`close`. Before this watcher replaces the hand-stamped one
for a span, the arm path must (1) push `arm` before launch, (2) push `close` in the Check, and (3) run
`scripts/mbp_watch.py read` (or the same three checks, open alarms included). Until the controller does,
the magistrate runs the three lines by hand.

## Install

Nothing to install on either Mac beyond the checkout the magistrate already uses. The schedule starts when the
workflow is on `main`. Then:
1. `init-log` and the ruleset above (the lead, once).
2. Update the Air agent's checkout to this merge (it then polls `mbp-alarm`), so step 4's banner can appear.
3. `gh workflow run mbp-watch.yml --repo mpmdw/JouleWise`, then `gh run list --workflow mbp-watch.yml`: the
   run must succeed (it fails while the log or the ruleset is missing, or if the activity API answers in
   another shape than the tests assume). The first run files `WATCHER_GAP` (there was no earlier run):
   close it once the log is checked. The workflow needs `actions: read` for that check.
4. A delivery check, synthetic only: `scripts/mbp_watch.py arm --plan cq-notify-test-a1 --t0 <now-7200>
   --deadline <now-3600>` from the Air, dispatch the workflow, confirm the owner received the
   `mbp-alarm SPAN_SILENT cq-notify-test-a1` notification and the Air agent posted its banner, then
   `close --plan cq-notify-test-a1 --status CLOSED_OK --close-epoch <now>` and close the issue. The records
   stay in the log; the silence is already filed, so it never alarms again.
5. Add the `arm` and `close` lines to the magistrate's launch and Check procedures, and the `read` line to
   the arm checklist (a lead item), until the controller carries them.

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
   the `cadence-desk` line. FORMAT section 6 lets each desk use its own signed record history; record which
   history snapshot each desk used and rely on `agreement_view`'s exclusions of history-dependent terms. The signer lines are public keys; no secret is needed.
4. **The comparison.** PR #799 already has `desk_final.agreement_view` and `compare_verdicts`, which compare the
   automatic part of two verdicts and exclude later hand inputs (`HAND_TABLE_DUE` against a hand-completed
   verdict is not a disagreement). The Actions desk should use them, not a new comparison. A disagreement
   files `mbp-alarm DESK_DISAGREES <plan>` (a new closed code), which the arm's read already refuses on.
5. **Coverage.** Every bundle must be checked once, retried after a failed run, and marked checked, with no
   time lookback. The receipt must bind the bundle commit, both compared verdict commits, the desk code's
   commit and the exact history snapshot, and a re-judgment or a code or history change needs a new check: a
   plan-only "checked" mark is not enough. Writing such a receipt (for example a `desk-recheck/<plan>` ref)
   needs `contents: write`, which this watcher deliberately does not have: a separate, narrowly scoped writer
   job, or another durable receipt, has to be chosen.
6. **Routing to the research lead.** RL-173 B says a disagreement "comes to me". An owner issue alone does
   not reach the research lead; the lead relays it as a ruling request. The hold must also reach the arm:
   `read` refuses on an open `mbp-alarm`, but PR #800's own API gate does not read issues (see above).
7. **The MBP verdict's transport.** FORMAT section 6 (PR #800 and PR #799) already settles the MBP desk: it
   signs as `cadence-controller` into the local-only `refs/heads/cadence-desk-mbp/<plan>`, and the
   comparison is `compare_verdicts(mbp, offhost)`. Because that ref is local, the Actions job cannot see the
   MBP verdict or the MBP's history. Missing: an authenticated, public-safe push of the exact MBP verdict
   (and the history snapshot it used), or an explicit rule that Actions compares against the Air's
   `cadence-desk-final` verdict instead.
8. **Who publishes.** FORMAT section 6 has the off-host desk publish a verdict signed as `cadence-desk` and
   compare it with the MBP's. An Actions job reads with public keys only and holds no signing key, so it can
   report agreement but cannot be that signed producer; and the MBP's local `cadence-controller` verdict is
   not the signed off-host verdict either. Which host produces the signed off-host verdict, and how the MBP
   verdict reaches it, is an open contract decision for PR #799/#800 and the research lead.
