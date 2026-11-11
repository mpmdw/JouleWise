# Fable cold review: `w1-armcheck` (RL-53 W-1 and W-2, RL-54, RL-56)

Reviewer: Fable 5.2, state-machine lane lead, 2026-11-11 04:55 PST. Reviewed `efdf59705`
(`ops/2026-11-11-w1-armcheck`: Sol's rounds 1 to 3 with the two side branches merged), base the W1 line
`b4a6c217f`. Builder: Sol xhigh.

**Verdict: ADMIT-WITH-FIXES.** A-1 blocks: as built, the pre-install check would refuse every arm on a normal
session layout. Round 4 goes back to Sol.

## Scope check

- One bound file changes: `scripts/align_v4_session.py` (+324/-10). `joulewise/align/apple/powermode.py` is
  untouched. The PREQUAL harness `joulewise/align/w1_prequal.py` and all touched tests are not bound.
- No record changes except: one new key `watchdog_acceptance` in the arm record, one new key
  `host_privilege_preflight` in the prepare state, and in `dwell.json` the keys
  `watchdog_post_install_start_ns`, `watchdog_post_install_end_ns`, `watchdog_post_install`.
  `installer_end_ns` keeps its meaning.

## Against the rulings

| Requirement | Met? | Note |
|---|---|---|
| W-2 probes read and never set; sudo asked by listing | Yes | `/usr/bin/sudo -n -l <command>` for each rule taken from the owning constants; the network-time query runs only if its own rule lists. Mutant "drop `-l`" is killed by 8 tests. |
| W-1 pre-install before the meter probe and the dwell stamp | Yes | Ordering test asserts `watchdog, meter, write, stamp`. |
| W-1 post-install right after the installer, one function, one call site | Yes | `_watchdog_post_install`, called once in `_arm_and_install`. |
| Hard time limit; a timeout refuses and undoes | Yes | 30 s shared by the dry run and the discovery run. |
| Start and end stamped on the dwell clock | Yes | Written on every path, including refusal and undo failure. |
| Read-only; inside a span no network call | Yes inside the span. | Before `t0 - 180 s` a dry run can make the watchdog's ordinary remote stop probe (two bounded `git ls-remote` calls), as every 300 s tick of the installed watchdog does. Recorded as a finding in Sol's report; the watchdog is not edited. |
| RL-56: refuse on any hold, `STRANDED`, uncertain clock or network, unreadable plist or plan, timeout, failure; admit otherwise and record which case | Yes | All 25 state words are derived from the watchdog source by an AST test and each is classified. |
| RL-56 (1): inside the span only a fence is admitted | Yes | Boundary tests at `t0 - 180`, one second either side. |
| RL-56 (2): positive identification without editing the watchdog | **Not as built: A-1** | The discovery program imports the installed module and calls its `load_plans`; it never runs `main()`. |
| RL-56: PREQUAL trips a post-install hold and expects the undo | Yes | Named PREQUAL checks for the pre-install hold and the post-install hold with rollback. |
| A refusal after the install undoes the install | Yes | Uninstall through `install_night_agent.sh --uninstall`, both labels verified absent, host Automatic restored by the existing path; an undo failure says `install_undo_failed` and names what is left. |

## Findings

| # | Severity | Finding | Fix |
|---|---|---|---|
| A-1 | **Blocking** | Identification runs in both phases and requires this plan among the installed watchdog's `load_plans` result. Before the install the watchdog can only find a plan by its custody scan, `<watchdog custody root>/../*/night_plan.json` (`scripts/magistrate_watchdog.py:343-344`). A v4 session writes its plan to `<session_root>/custody/night_plan.json` (`scripts/bytes_h_session.py:360`), which that scan does not reach unless the session sits in one particular place. So pre-install would refuse "arm plan missing" on every normal arm. The tests put the plan where the scan finds it. The same gap means the dry run alone cannot show, before the install, that the installed watchdog can parse this plan, which is the 2026-11-08 and 2026-11-10 failure. | Pre-install asks the installed watchdog's own parser about this plan file directly (the per-plan steps of `load_plans`), and does not require the scan to have found it. Post-install keeps the `load_plans` rule. Tests for both layouts, run for real against the watchdog module, and one with a version-skewed parser that rejects an unknown key. |
| A-2 | Low | The arm record stores the dry run's whole stdout and stderr and the `sudo -l` output, unbounded. | Cap each stored stream at 8 KiB with a `truncated` flag. |
| A-3 | Low | The plist whitelist is tested with hand-built documents. | One test renders the repository's real magistrate plist template and passes it through the parser. |

## What I ran

- `tests.align.test_v4_arm_watchdog_check`: 31 tests, OK.
- Nine mutants on the W-1 and W-2 code, nine killed: `-l` dropped from the sudo listing; the network-time
  query run without its rule; an unreadable network-time state accepted; the prepare refusal removed; a nonzero
  watchdog exit accepted; any state word admitted; the inside-span fence rule removed; the span-start
  comparison removed; the pre-install refusal removed.
- Still owed, by me, on the final code: the test modules Sol could not finish under its time cap (54 at the
  end of round 3), run on the Air before the batch PR.

## Native checks owed after install (remote)

As listed in Sol's report, plus: a pre-install arm from a session whose custody directory is not under the
watchdog's scan, which is the case A-1 is about.
