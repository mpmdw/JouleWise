# PR #749 cold review and disposition

Copied from the PR comments (6837628405, 6837684724) so the gate ledger can cite a repo path.

## Cold review: PR #749 (head 977ec087d)

**Verdict: ADMIT-WITH-FIXES.** Nothing here is blocking. The installer is safe and correct as written. Three MEDIUM findings concern alarms that never reach anyone in the unattended case this agent exists for. Fix them before Ed runs the installer for real.

### Verified
- `python3.13 -m unittest tests.test_air_watch_agent tests.test_night_results_watch` (TMPDIR on JW-EXT): 65 tests, OK.
- I ran `--dry-run` and `--uninstall --dry-run` with the **real** HOME. Both exit 0 and only print. The mtime of `~/Library/LaunchAgents` did not change, no plist was written, `~/Library/Logs/JouleWise` was not created, and launchctl was not invoked.
- Rendered plist checks out: `Label`, `KeepAlive` true, `RunAtLoad`, `ThrottleInterval` 60, absolute `/opt/homebrew/bin/python3.13` (used both as the interpreter and as `--python`), the agent path, `WorkingDirectory` = checkout, stdout and stderr both going to `~/Library/Logs/JouleWise/air-watch.log`, and `PATH` covering `gh` and `git`. No `@TOKEN@` is left unrendered.
- No SSH, no measurement data. The child watcher keeps its HTTPS/file-only Git boundary (`GIT_SSH_COMMAND=/usr/bin/false`, `protocol.allow=never`). `main_ci_watch` reads only run ids, job names and conclusions through the `gh` API, never logs. A notification carries only `level code subject`, filtered to `[A-Za-z0-9_:./-]` and capped at 80 characters, so AppleScript quote injection is blocked (tested).
- MAIN_CI_RED fires once per run id, and the state survives restart (tested). It stays quiet when the newest completed run is green, when only in-progress runs exist, and when the list is empty. When `gh` is missing or unauthenticated it emits one `INFO GH_UNAVAILABLE`, stays quiet afterwards, and re-arms after `gh` recovers. Main pushes are not cancel-in-progress, so a superseded run does not cause a false red.

### Findings

1. **MEDIUM: a failed child exits silently and the agent crash-loops.** When the watcher exits non-zero, `run()` just returns that status. Causes include `INVALID_CURRENT`, `WATCH_ERROR`, a failed notifier subprocess, or `ORIGIN_PROTOCOL_NOT_ALLOWED`. launchd then restarts the agent every 60 s forever. The only trace is an `INFO WATCH_ERROR` line in the log, and INFO lines are never notified. The main-CI check also runs on every restart (about every 60 s instead of every 900 s). **Fix:** in `run()`, when `status not in (0, 20)`, call `notify("… ALARM WATCHER_EXIT agent status=N")` from inside the agent process before returning. Rate-limit it through the CI state file (for example, once per hour per status), so a crash loop gives one banner rather than 60 an hour.

2. **MEDIUM: an unmounted SSD means total silent failure (Q5).** The script, the notifier (`--notify-cmd python3.13 /Volumes/JW-EXT/.../air_watch_agent.py notify`) and `WorkingDirectory` all live on JW-EXT.
   - **Unmounted while the agent is running:** `git -C` fails, so the watcher raises `SILENCE` after about 10 minutes. The notifier process can't open its script and exits 2. The watcher's `subprocess.run(..., check=True)` raises `CalledProcessError`, so the watcher exits `WATCH_ERROR`. The one alarm that matters is never delivered.
   - **Unmounted at login or after the crash:** launchd fails to spawn the job (missing cwd or script) every 60 s, and nothing tells anyone.
   - **Side effect:** while the agent runs it holds its working directory on the volume, so a normal eject of JW-EXT is refused as "in use".

   **Fix:** finding 1's in-process notify covers the mid-run case, because `osascript` lives on `/usr/bin` and the agent's modules are already imported. For the rest, either install onto the internal disk or document the limit:
   - The installer could create a small dedicated clone under `~/Library/Application Support/JouleWise/air-watch/checkout` (for example `--filter=blob:none` plus a sparse checkout of `scripts/air` and `docs/process`) and render that path. This is a few MB with negligible I/O, so it does not conflict with the SSD-first rule.
   - If you keep the SSD path, say in the README that an unmounted SSD gives no alarm.

3. **MEDIUM: the agent reads a stale `docs/process/CURRENT.json` (Q4). This is not acceptable for an unattended agent.** `CURRENT.json` is regenerated several times a day (8 commits in recent `git log` on main), and the `armed`/`wait` blocks it holds are the only inputs to `ARMED_NO_RESULT_PAST_LATEST_END` and `DEADLINE_PASSED`. A detached checkout never moves, so a newly armed window gets no overdue alarm. That is the R1-stranding class of miss. A stale `wait` deadline can also raise one false `DEADLINE_PASSED`.

   **Fix:** read CURRENT from origin through the existing Git boundary:
   - Add a `Git.fetch_main()` that runs `fetch --no-tags origin +refs/heads/main:refs/air-watch/main`.
   - Then read the file with `cat-file blob refs/air-watch/main:docs/process/CURRENT.json` and pass the bytes to the existing `read_current` validation.
   - This keeps HTTPS only, does not mutate the working tree, and does not auto-update running code. Do it every poll, or every N polls.
   - On a fetch failure, fall back to the local file and emit `INFO CURRENT_STALE`.

   Don't `git pull` the agent's own checkout from inside the agent.

4. **LOW: the plist cannot pass armed timing.** The installer renders no `--watch-arg`, so `--min-expected-s` is 0 and `RESULT_EARLY` can never fire. The README example this PR replaces used 3600. **Fix:** add a `JW_AIR_WATCH_ARGS` value, or an installer flag, that renders `<string>--watch-arg=--min-expected-s</string><string>--watch-arg=3600</string>` entries. The README's advice to pass timing with `--watch-arg` currently means hand-editing the installed plist, which the plist's own header comment forbids.

5. **LOW: `--uninstall` skips `bootout` when the plist file is gone but the job is still loaded,** for example after a manual `rm`. The agent keeps running. **Fix:** always run `bootout … || true`. It is already idempotent, and the dry run prints it already.

6. **LOW: reinstall race.** A `bootout` followed immediately by `bootstrap` can fail with `Bootstrap failed: 5: Input/output error` while the old job is still tearing down. Under `set -e` the installer then exits with the new plist written but not loaded. Separately, `--dry-run` does not print the `bootout` line that a real install runs. **Fix:** after bootout, poll `launchctl print "$DOMAIN/$LABEL"` until it fails (at most about 10 s), and print the bootout line in the dry run.

7. **LOW: sed escaping misses backslash.** The rejected-character set covers `& < > " @ #` but not `\`, which sed interprets in the replacement text. **Fix:** add `\\` to the case pattern.

8. **LOW: a re-run of the same run id never re-alarms.** Deduplication is on `databaseId`, so if a manual re-run (attempt 2) of a red run fails again, it stays silent. **Fix:** add `attempt` to the `--json` fields (confirmed available) and dedupe on `(databaseId, attempt)`. A manually cancelled main run counts as red; that is acceptable, but say so in the docstring.

9. **LOW: narrow exception net in the agent's CI call.** `run()` catches only `(OSError, ValueError)`. Odd `gh` JSON (for example a non-list from `run list`) raises `TypeError` and kills the agent. launchd then reaps the child and restarts. **Fix:** catch `Exception` around `main_ci_watch.run_once` and log `INFO MAIN_CI_WATCH_ERROR`.

10. **INFO: delivery can't be verified.** `osascript display notification` returns 0 even when notifications for Script Editor/osascript are turned off, so `NOTIFY ok` does not mean a banner was shown. Suggest a one-time `air_watch_agent.py notify "… ALARM INSTALL_TEST air"` in the install step, with Ed confirming that he saw it.

Ed's approval is still required for a real install. I did not run launchctl against real labels.


## Disposition

Cold-review fixes applied in 5a8b03369:

- **M1 WATCHER_EXIT:** when the child watcher exits with a status other than 0/10/20, or cannot spawn, the agent posts its own `ALARM WATCHER_EXIT agent status=N`. It is rate-limited to once per status per hour, with state in `.../air-watch/agent-exit.json`. Tested.
- **M2 SSD unmount:** the plist now runs an internal-disk wrapper, `~/Library/Application Support/JouleWise/air-watch/air-watch-run.sh`, which is also the WorkingDirectory. If the checkout is missing, the wrapper posts `WATCHER_EXIT repo_missing` hourly through `/usr/bin/osascript` and logs it. The missing-repo path is tested. The notifier now uses `/usr/bin/osascript`, and gh runs with cwd set to the checkout. The README documents that you must run `--uninstall` (or `bootout`) before ejecting JW-EXT.
- **M3 CURRENT freshness:** the new `--current-from-origin` flag, which the agent passes, fetches `+refs/heads/main:refs/air-watch/main` through the existing HTTPS/file-only Git boundary and reads CURRENT with `cat-file`. If that fails, it uses the local file and prints `INFO CURRENT_STALE` once per stale spell. Tested against a local bare repo (the working tree stays untouched and no FETCH_HEAD is written), plus a CLI test that `CURRENT_STALE` prints once.
- **LOWs:** L5 `--uninstall` always runs bootout. L6 the installer polls `launchctl print` (up to 10 s) before bootstrap, and the dry run prints the bootout. L7 `\` and `'` are rejected in rendered paths. L9 the supervisor catches any exception from the CI check. I10 the README adds a one-time `INSTALL_TEST` banner check.
- **Not done:** L4 (installer flag for `--watch-arg` timing) and L8 (dedupe on `(databaseId, attempt)`).

`tests.test_air_watch_agent` + `tests.test_night_results_watch`: 69 OK. `gen_state --check` passes, and `--dry-run` output passes `plutil -lint`. Still not installed; Ed runs the installer. Not merging.

