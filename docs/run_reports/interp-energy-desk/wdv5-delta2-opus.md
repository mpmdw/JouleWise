# Delta-2 review: `ops/2026-11-10-watchdog-v5-installed` fix round 2 (Opus 5.5)

Date: 2026-11-10 12:45 PST (from `date`). Reviewer: Opus 5.5, the same seat as `wdv5-delta-opus.md`.
Delta: `b1be29e08..d42835ac4`. Code: `scripts/post_window_unstrand.sh`, `scripts/run_night.py`,
`tests/test_post_window_unstrand.py`. The other two files are Sol's reports.
Clone: `jw-wt/opus-wdv5-rev`, with `d42835ac4` checked out detached. The branch was not modified.
Everything was synthetic: custody, HOME, LaunchAgents and process rows. Every script run was a dry
run, so launchctl was never invoked. I signalled only the `sleep` holders I had started, and my
leftover check counted 0. I read no real custody, archive or restricted path.

## Verdict: ADMIT-WITH-FIXES

N1, N2 and the caffeinate remainder of F1 are closed. The new descendant exemption is broader than
caffeinate needs, and it opens a fail-open hole (D1, below). My previous review wrongly said that
"no outside process can become a child of `$$`". A wrapper that `exec`s the script keeps the
children it already had, and they become children of `$$`. That is the same mechanism caffeinate
relies on. One required fix, about 7 lines, verified in a scratch copy. There are also two LOW test
and coverage items.

## Closures

| Item | Status | Evidence |
|---|---|---|
| N1 literal reason code at the `PlanError` call site | CLOSED | `_CODES["ac_powermode_unenforced_on_this_head"]` resolves to `night_ac_powermode_unenforced_on_this_head`. `test_run_night` 292 OK, including the registry and literal-call-site test. `test_night_ac_powermode` 6 OK. |
| N2 `.` matched every process | CLOSED | `logical_custody` is now `cd -L; pwd -L` (absolute). Old probe n10 (`.` from inside custody, real ps): rc 0. New n2a (`.` with correct PWD): rc 0. n2b (`.` with stale PWD in env): rc 0. Sol's dotted-commands test passes natively. |
| F1 remainder (caffeinate) | CLOSED | Old probe n3 `/usr/bin/caffeinate -i <script>` real ps: **rc 0** (was rc 1). h5: rc 0. Native test `test_native_ps_clean_completed_window_under_caffeinate` ran (not skipped) and passed. |

## New finding

### D1 (REQUIRED, fail-open): the descendant exemption exempts pre-existing children of an exec'ing wrapper
The fix exempts every descendant of `$$` found in the snapshot. `$$` is a pid, not a fresh process.
If the script is reached by `exec`, for example `zsh -c '… & exec post_window_unstrand.sh …'`, or by
`exec` at the end of a wrapper script or from an interactive shell that has background jobs, every
child the wrapper already had becomes a "descendant". That includes a live chain or worker. It is
exactly how the caffeinate helper itself becomes our child. Native repros (real `/bin/ps`, Air):

| Probe | Shape | Expected | Got |
|---|---|---|---|
| h1 | `zsh -c "sh -c 'sleep 20' <custody>/night/align-r1 & …; exec <script> <custody>"` | refuse | **rc 0, DRY RUN** |
| h2 | same, child named `/m/scripts/night_chains/chain.zsh` | refuse | **rc 0, DRY RUN** |
| h3 | control: same worker as a sibling, no exec | refuse | rc 1 |
| h4 | orphan reparented to launchd | refuse | rc 1 |
| h6 | caffeinate wrapper + sibling worker | refuse | rc 1 |
| s7 (old stub row) | child of the script names custody | refuse | **rc 0** (intended by the delta, and it is the same hole) |

A reparented orphan is **not** wrongly exempted. macOS reparents orphans to launchd (pid 1), not to
`$$`, and h4 refuses. A chain started by the real LaunchAgent has launchd as its parent, so the hole
needs a manual or kit wrapper that starts the chain or a worker and then `exec`s the unstrand.
It is unlikely, but this guard is the last check before it uninstalls the night jobs. The new
unit test `test_caffeinate_child_and_other_script_descendants_are_exempt` asserts the over-broad
behaviour (a `helper.py --plan` grandchild is exempt).

Fix (verified on a scratch copy of the script; diff against `d42835ac4`):

```diff
-    # becomes our child. Walk the same snapshot, excluding siblings/orphans.
-    descendants = {script_pid}
-    pending = [script_pid]
-    while pending:
-        for child in children.get(pending.pop(), ()):
-            if child not in descendants:
-                descendants.add(child)
-                pending.append(child)
-    exempt = ancestors | descendants | {os.getpid()}
+    # becomes our child. Exempt only that childless helper, never other
+    # children: a wrapper that execs this script keeps its earlier children.
+    helpers = {child for child in children.get(script_pid, ())
+               if processes[child][1].startswith("/usr/bin/caffeinate ")
+               and "post_window_unstrand.sh" in processes[child][1]
+               and not children.get(child)}
+    exempt = ancestors | helpers | {os.getpid()} | set(children.get(os.getpid(), ()))
```

With it applied, native probes: h1 rc 1, h2 rc 1, h3 rc 1, h4 rc 1, **h5 caffeinate clean rc 0**,
h6 rc 1, n2a rc 0, n2b rc 0. Tests to change with it:
(a) in `test_caffeinate_child_and_other_script_descendants_are_exempt`, drop the grandchild row so
the test asserts only the childless caffeinate helper;
(b) add a refusal case where a child of `{script}` is a plain worker that names custody, or is
`chain.zsh`, or where the caffeinate row has a child.

## LOW items (not required for admission)

- **L1 (test is TMPDIR-sensitive; one subtest is a pre-existing gap).** With the default macOS
  `TMPDIR` (`/var/folders/...`, under the `/var -> /private/var` symlink),
  `test_symlink_literal_and_declared_custody_aliases_refuse` fails 3 subtests natively:
  - `(alias.name, custody, alias)`: new in this delta. The relative argument runs under a stale
    `PWD` env from `subprocess(cwd=…)`. bash then drops to the physical path, so the
    `/var/...`-spelled alias in the process row is not matched. A real shell sets PWD correctly:
    probe a2 refuses.
  - `(custody, alias, alias)`: a cascade. The previous subtest's `--go` left `launchctl.log`, and
    the subtests never reset it.
  - `(alias, alias, custody)`: pre-existing. It also fails at `b1be29e08` with default TMPDIR. A
    process that names the canonical directory through a symlinked *prefix* (`/var/...`) matches
    none of `pwd -P`, `pwd -L` or the declared path. Native probe a1 also gets rc 0.

  With `TMPDIR=/private/tmp/...`, the module is 23 OK with 0 skipped. Real custody
  (`~/night-custody`, `/Volumes/JW-EXT`) has no symlinked prefix, and the chain, driver and
  monitor names are still caught by the regex and `night_chains/`. Fix: in the test, `.resolve()`
  the temporary root, pass `PWD=cwd` in `run_script`, and unlink the log per subtest. Optionally,
  the script could also add `os.path.realpath` of each absolute argv token to the match.
- **L2.** `children` and the exemption are built from the same single snapshot, so there is no
  pid-reuse window. That is unchanged and fine.

## Tests (native, `python3.13 -B -m unittest`, one module per command, without PYTHONNOUSERSITE, cwd = `d42835ac4`)

| Module | Result |
|---|---|
| tests.test_run_night | 292 OK (121.4 s) |
| tests.test_post_window_unstrand | default TMPDIR: 23 run, **3 failures** (L1). With `TMPDIR=/private/tmp/opus-wdv5-delta2`: **23 OK, 0 skipped**, and both native-ps tests (zsh and caffeinate) ran |
| tests.test_night_ac_powermode | 6 OK |
| tests.test_magistrate_watchdog_yield | 20 OK (Sol's 3 sandbox failures pass natively) |
| tests.test_magistrate_watchdog | 155 OK |

## Probes (native rows run after the suite finished)

- `probe_unstrand_delta.py`: 33 rows checked, 32 PASS. n3 caffeinate and n10 `.` now pass. The only
  FAIL is s7, the descendant stub, which is the expected flip and is D1.
- `probe_wdv5.py`: 5 OK. The discovered, installed and both timelines are identical, and an open
  chain never releases.
- `probe_delta2.py` (new): h1 and h2 FAIL (D1); h3 to h6, n2a and n2b PASS; a1 FAIL (L1,
  pre-existing); a2 PASS. With the D1 fix: everything passes except a1.

No regressions elsewhere in the delta. The `run_night.py` change is the one-line N1 fix. The test
seam's `{script}`/`{parent}` substitution touches only `TEST_PS_EXTRA_ROWS`.
