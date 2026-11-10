# Delta review: `ops/2026-11-10-watchdog-v5-installed` fix round (Opus 5.5)

Date: 2026-11-10 12:03 PST (from `date`). Reviewer: Opus 5.5, the same seat as `wdv5-rev-opus.md`.
Delta: `85612ccc2..b1be29e08` (`2181b000e` fixes, `c9b10b30a` report, `b1be29e08` Sol desk report).
Clone: `jw-wt/opus-wdv5-rev`, with `b1be29e08` checked out detached. TMPDIR `/private/tmp/opus-wdv5-delta`.
All custody, HOME, LaunchAgents and process rows were synthetic. Every probe ran the script in
dry-run mode only, so it never invoked launchctl. I signalled only processes I had started
(`sleep` holders). I read no real custody, archive or restricted path.

## Verdict: ADMIT-WITH-FIXES

F2, F3, F4 and F5 are closed. F1 is closed for every wrapper except `caffeinate`. Its failure
mode is fail-closed, so it is LOW. The delta introduces one CI-red regression (N1). It is a
one-line fix that I verified in a scratch worktree. N1 is the only required fix.

## New findings

### N1 (REQUIRED, CI-red): the new driver guard uses a literal reason code at its call site
`tests.test_run_night.NightDriverTests.test_driver_reason_codes_are_registered_and_are_not_literal_call_sites`
fails on `b1be29e08` and passes on `85612ccc2`:

```
AssertionError: Lists differ: ['        raise PlanError("night_ac_powermode_unenforced_on_this_head",'] != []
```

The driver's rule is that every reason code goes through the `_CODES` map, which is keyed by the code
without its `night_` prefix (`scripts/run_night.py:181`). Sol did not run `test_run_night`, so it missed
this. Fix (`scripts/run_night.py:2075`):

```diff
-        raise PlanError("night_ac_powermode_unenforced_on_this_head",
+        raise PlanError(_CODES["ac_powermode_unenforced_on_this_head"],
```

Verified in a scratch worktree at `b1be29e08` with this one line applied (since removed): `test_run_night`
292 OK (126.5 s), `test_night_ac_powermode` 6 OK. Note that `_CODES["night_ac_..."]` (with the prefix)
raises `KeyError`, so the key must be written without it.

### N2 (LOW, fail-closed, new with the F3 fix): a short relative literal argument matches almost everything
The literal argument is added to `custody_names` as given and matched by substring. Probe n10 ran
`cd <custody>; post_window_unstrand.sh .` on a quiet Air with real `/bin/ps`. It gave rc 1, "a chain,
driver or window process is still present", because nearly every argv contains `.`. A plain relative
name (`n-custody` from the parent, probe n11) passes, so the problem is limited to very short
literals such as `.`, `./` or `..`. The failure is safe but surprising. Fix: add the logical
absolute spelling instead of the raw literal,
`literal_custody="$(CDPATH= cd -L -- "$custody" >/dev/null && pwd -L)"`. That keeps the symlink-alias
coverage that F3 wanted.

## F1 to F5

### F1 (ancestor exclusion): CLOSED except caffeinate (LOW, fail-closed)
The script reads `pid=,ppid=,command=` once and builds a map from that single snapshot. It walks from
`$$` to pid 1 and exempts only that chain plus the embedded Python. It refuses when a parent is missing
from the table, on a cycle, when pid 1 is absent, on a non-decimal or negative pid or ppid, on a
duplicate pid row and on an empty-command row. A sibling, an orphan or a descendant of the script
that names custody still refuses. There is no mid-walk pid-reuse window, because the walk runs over
one snapshot and macOS reparents an orphan to launchd, so a ppid cannot point at a reused pid inside
the snapshot.

| Probe | Result |
|---|---|
| n1 direct argv, real ps | rc 0 |
| n2 `zsh -c 'cd /; …; exit $?'` (old a2, which failed) | **rc 0** |
| n4 `time` + nested `zsh -c` | rc 0 |
| n9 ancestor argv names custody, `night_chains/` and `run_night.py` | rc 0 (exempt) |
| n5 sibling under the same wrapper names custody (real ps) | rc 1 |
| n6 orphan reparented to launchd names custody (real ps) | rc 1 |
| s2 parent missing / s3 script row missing / s4 ppid cycle / s11 no pid 1 | rc 1 "ancestry is unproven" |
| s5 non-decimal ppid / s6 duplicate pid / s10 negative pid | rc 1 "absence is unproven" |
| s7 descendant of the script names custody / s8 sibling (stub) | rc 1 |
| **n3 `/usr/bin/caffeinate -i <script> … <custody>`** | **rc 1 (still refuses)** |

Why n3 fails: on macOS, `caffeinate -i UTIL` forks, and the **parent** execs UTIL. The process that
holds the assertion is therefore a **child** of the script. The ancestry dump shows bash 3817
(ppid zsh 3816), and `/usr/bin/caffeinate -i …` is pid 3818 with ppid 3817. Its argv names custody,
and it is not an ancestor. `sudo`, `ssh` and `time` do sit in the ancestry (n4 confirms `time`).
The original F1 named caffeinate explicitly. Fix: also exempt **descendants of `$$`**. That is sound,
because the script spawns only python, ps and, in this case, the caffeinate helper, and no outside
process can become a child of `$$`. Add a `caffeinate -i` test. Workaround until then: do not wrap
the script in caffeinate.

INFO: ancestors are exempt from the *pattern* match as well as the custody match (s9: a
`run_night.py` ancestor passes). That is acceptable, because the driver or chain cannot be an
ancestor of an operator's recovery shell.

### F2 (ac_powermode 2 in driver and installer): CLOSED
- The parser is not narrowed. The delta touches `night_gate.py` only to add the reason code to
  `NIGHT_DRIVER_REASON_CODES`. `_plan_ac_powermode` and `_PLAN_KEYS` are unchanged. `probe_wdv5.py`
  re-ran with 5 OK. The R1 lane-shape plan parses in installed and discovered placement. The 20
  mutations all hold. The discovered, installed and both timelines are identical, and an open chain
  never releases.
- Guards: `run_night` `preflight` (exit 3), `run --dry-arm` (exit 3 before the HAZARD_PACK check, no night
  record), `run` and `rehearse` (after the existing-record check and before the HAZARD_PACK branch.
  The guard writes a registered refusal and `result.json`, couriers, and launches no chain or hazard
  arm), and the installer's `validate_install` (Refused(3), before git probes). Install, `--render-only`
  and `--launchd-probe` all pass through `validate_install`. `dead-man`, `probe`, `schedule` and `g7-control`
  are not admissions.
- The documented reason matches the code. `night_ac_powermode_unenforced_on_this_head` appears in
  `NIGHT_DRIVER_REASON_CODES`, `COLD_GATE_CODES` and `INSTALLER_REFUSALS`, and in the runbook and
  NIGHT_HANDBACK tables, which `test_arm_retry` checks byte-exact. The runbook installer row says exit 3,
  which matches `Refused(3)`. The driver's `EXIT_REFUSED` is 3. Values absent and 0 keep their behaviour.
- Merge note (INFO): `git merge-tree` against `origin/lane/2026-11-08-r1-arm-fixes` auto-merges the installer,
  dry-arm and preflight guards silently. Only the run-path guard conflicts. The lane's `test_run_night`
  exercises `ac_powermode` 2, and this branch's `test_night_ac_powermode` asserts the refusal, so CI will
  force whoever merges the lane to remove all four guards and the registry rows together. Make that an
  explicit checklist item on the lane merge.

### F3 (alias matching): CLOSED (see N2)
The match now covers the resolved path, the literal argument, the plan's declared `custody_root` and
`night_chains/`. n8, a symlinked argument with a live sibling naming the link path (old b1, which was
missed), now gives rc 1. n7, an inner `night_chains/align_r1_rehearsal.zsh` alone (old b3, which was missed),
gives rc 1. s12, a process naming only the declared root, gives rc 1. A declared root that is not a
string gives rc 1 (s13). A plan that is a JSON list gives rc 1 (s14). A plan without `custody_root` still
works (s15). An alias that is none of the four spellings is still missed. That is acceptable defence in
depth.

### F4 (ps, CDPATH, follower exit): CLOSED
- `/bin/ps` is absolute by default. A hostile `ps` earlier on PATH is not used (f1: rc 0, and the
  substitute never ran). `UNSTRAND_PS` is an environment seam. An empty value refuses (s16), and so
  does a missing path (Sol's test). It is still an operator-settable variable, which I accept as a
  test seam. (`python3` is still resolved from PATH, as on base. INFO only.)
- CDPATH: a relative custody with CDPATH pointing at a decoy now resolves correctly (f2, old e1:
  rc 0). A directory named `-dash` works (f3). `--dash` is still usage (f4, rc 2).
- Follower: a dry-run follower failure gives a nonzero exit with "watchdog event follower failed" (f5).
  After a verified `--go`, a follower crash leaves rc 0 with the warning. Sol's test covers that path
  with stub launchctl and passes natively. In bash, `$?` at the head of the `else` arm is the
  condition's status, so `follower_rc` is correct.

### F5 (usage text): CLOSED
`--bogus` gives rc 2, and the usage text says "Completed windows only: a window refused before its
chain started is not covered." (f6).

### Blinding
No probe output contained the `BLINDED` marker payload (`leak=False` on all 33 rows). The only new
read is `night_plan.json`, which is a plan and not a blinded record.

## Tests (native, this Air, `python3.13` 3.13.18, one module per command, cwd = `b1be29e08`)

| Module | Result |
|---|---|
| test_magistrate_watchdog | 155 OK |
| test_magistrate_watchdog_cli | 8 OK |
| test_magistrate_watchdog_b6 | 9 OK |
| test_magistrate_watchdog_span | 24 OK |
| test_magistrate_watchdog_yield | 20 OK (5.8 s). Sol's three sandbox failures pass natively. |
| test_magistrate_watchdog_v5 | 4 OK |
| test_install_magistrate_watchdog | 10 OK |
| test_magistrate_desk_fence | 42 OK |
| test_night_gate | 113 OK |
| test_night_plan_writer | 11 OK |
| test_arm_retry | 36 OK |
| test_post_window_unstrand | 19 OK, 0 skipped (the native-ps wrapped-zsh test ran) |
| test_night_ac_powermode (new) | 6 OK |
| **test_run_night** | **292 run, 1 FAIL (N1)**; 292 OK with the N1 line applied |
| test_night_agent_install | 85 OK (597 s) |
| test_install_night_agent | 67 OK |
| test_evidence_night | 168 OK |
| test_issue_calibration_acceptance_generation | 156 OK |

Total: 1225 run, 1224 OK, 1 failed (N1). The last six modules exercise code that the delta changed,
or check the runbook and NIGHT_HANDBACK. No PR or CI run exists for the branch yet.

Probes are in the session scratchpad and are not committed: `probe_wdv5.py` (5 OK) and
`probe_unstrand_delta.py` (33 checked rows: 31 PASS, 2 findings, n3 caffeinate and n10 `.`, plus 1 INFO usage row).
I ran the native rows only after the test runner had finished. The test suite's own `run_night.py` and
`chain.zsh` children trip the system-wide pattern scan, which is correct behaviour but makes concurrent
probe runs noisy.

## Required before merge
1. N1: `_CODES["ac_powermode_unenforced_on_this_head"]` at `scripts/run_night.py:2075`, then re-run `test_run_night`.

Recommended (fail-closed, may ride along): exempt descendants of `$$` and add a caffeinate test
(F1 residual), and use the logical absolute literal (N2). Add the four-guard removal to the R1 lane's
merge checklist.
