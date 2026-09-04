# Cold Fable ruling - packet 17 (plan-pin + built watchdog), 2026-09-04

**Contamination.** Auto-loaded: `~/.claude/CLAUDE.md`, `JouleWise/CLAUDE.md`, `CLAUDE.local.md` (doctrine 1-11), memory index `MEMORY.md`. None used.
**Charter digest.** Expected (launch msg) = observed `shasum -a 256` = `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` MATCH; registry `:16`. Checkouts `6936b190` / planpin `90698150` / watchdog `953a1645` match packet; clean before and after.
**Validator** rc=0 (full JSON in scratch `validator-receipt.json`): `result PASS`, v2 receipt, packet `8be2c69e..ec68`, manifest `9eb2efa7..6f69`, 17/17 exhibits match, `judge_handoff_bound false`. Forbidden docs not read; no session started.

## Executed
| # | Probe | Result |
|---|---|---|
|E1|planpin 3 modules|Ran 111 OK|
|E2|`from_mapping`: LF-head / rel root / v1 / valid|`night_plan_malformed` exit 3 x3; valid ok|
|E3|`install_night_agent.sh --render-only` same four|exit 3 x3, same detail, nothing rendered; valid exit 0, both plists|
|E4|watchdog module at 953a1645|Ran 36 OK; 17h/17l regressions present|
|E5|7 scratch mutations, each killed by its named test|pos-control ignored; belt `<`; request dropped (2 tests); TERM 17 m; ladder 7199; glob narrowed; ack after poll|
|E6|17i §2 boundaries|-1500 REQUEST/-960 TERM/-900 KILL exact; span closes dm+FRESH+1; belt and 07:00 half-open; glob hits `stop-magistrat`; 429->usage; argv `-p`, cwd canonical|
|E7|**integrated tree** (planpin + 6 watchdog files), same module|**FAILED errors=12**, all `PlanError .. v1 is retired` (fixture `tests:102` v1)|
|E8|integrated `--dry-run` beside copy of real `rehearsal-20260903` plan|**`HOLD_UNSAFE`**; no sibling -> `LAUNCHING`|
|E9|`~/night-custody/*/night_plan.json`|both v1; v2 parser refuses; no joulewise LaunchAgent loaded|
|E10|`ps`|1536 parents daemon 19312; **4394 `claude --bg-pty-host` ppid 1**; 5 `codex-run-v3` trees at ppid 1|

## Verdicts
| Q | Verdict | Authority / evidence |
|---|---|---|
|Q1|**AFFIRM**|R-6 `11a:117-118` "A plan older than 36 h or whose `repo_head` is not the checkout's HEAD refuses with `night_plan_stale`"; R-7 `11a:130-132` "never by checking out a branch in the development tree (that would move the HEAD R-6 binds to)". Intent = identity pin on the checkout that measures; v2 keeps 36 h (`night_gate.py:612-617`), pins `measurement_head` (`:620,633-645`), order window->age->probes->census (`:581-647`). Installer = gate: `install_night_agent.sh:55` calls `NightPlan.from_mapping` on raw JSON (E2=E3); one stricter-only extra (`:56-60`) - NIT.|
|Q2|**AFFIRM object at 953a1645** (packet pin `63d12162` stale - MATERIAL)|Rows 1-11 + 09-04 amendments at `wd:60,64-74,333-395,491-547,849-882,1087-1121,1157-1218,1269`; installer `:60-113,168-194`; prompt `:2-11,15-16`; E4-E6. Amendments AFFIRMED (glob superset; 300 s = file 14 Q5's ~12/h, keeps C4-a). **BLOCKER B-1:** not installable from a post-planpin checkout (E7/E8).|
|Q3|**AFFIRM authority; REJECT "recovery path" as labeled**|D-171 item 4 `11b:30-32` "install AUTHORIZED .. once it passes the gauntlet and a cold gate"; item 7 margin. D-171 silent on the twin kill - rests on file 15 row 10, affirmed as R-9(3) by force. Install reversible (`--uninstall`, STOP, `ops/stop*`; stale lock cleared `wd:757-760`). Twin kill irreversible; recovery = first launchd-spawned `-p`, which has NO launchd proof (17g ran from Python in a Terminal session; 17f Owed 1) - M-1. pid 4394 outside the tree, row 5 forbids killing -> `HOLD_CENSUS`/refused night with Ed away - M-2.|
|Q4|**REJECT as written**|"merge plan-pin -> install" yields a tick whose `glob_plans` (`wd:222,479-488`) reads both v1 custody plans -> `HOLD_UNSAFE` every tick (E8) and a resident that writes `standdown.request "malformed plan"` to the adopted twin (`wd:1179-1184`). Cure: before install, move both `night_plan.json` out of the glob AND re-author fixture `tests:99-110` + doc plans `MAGISTRATE_WATCHDOG.md:111,197` to v2; then consistent with 14 Q6 if night agents install FROM the measurement checkout (prompt `:11`, doc `:88`).|
|Q5|**AFFIRM R-9 limb with cures; REFUSE D-127 + lieutenant-list limbs** (no exhibit)|(a) cwd canonical (`wd:1269`), Bash allowed; prompt `:9` names only the canonical tree - under v2 the exposure is the **measurement** checkout: add "nor any armed plan's `measurement_root`". (b) `:19` never names process rules: add "never ratify/amend a process rule or charter". (c) shell-snapshot children sit at ppid 1 (E10) and escape the walk (`wd:849-874`) -> census hit at t0; force cannot reach them - M-3. Arming via `:10` is stood down at t0-25 - fits R-9(3).|
|Q6|**AFFIRM with text**|R-6: "recorded in the census row and never refuses" -> "recorded in C5 (`night_gate.py:624-631`); inequality never refuses, a failed probe still refuses `night_probe_error`; 36 h limb unchanged and precedes both probes"; append "installer validates the raw plan with `NightPlan.from_mapping` before any git probe". R-7: append "moving the measurement checkout between arm and completion refuses `night_plan_stale`; the fast-forward precedes authoring". R-9: append "outside a plan, STOP/branch/clock-uncertainty drains the owned tree: request, TERM +9 min, KILL +10 min (`wd:70-71,1139-1152`); no network I/O in the resident loop; remote stop within one 300 s tick; glob `refs/heads/ops/stop*`"; wake-source sentence names both LaunchAgents.|
|Q7|Findings|(1) **no integration-tree evidence** though both objects share `NightPlan` - effect B-1. (2) Q2 pin stale. (3) 17b(5)/17a §Compat stale. (4) 17g != the launchd proof 14 Q2 required. (5) Q5 cites D-127/list without exhibit. (6) File 15 amendments post-date 17m - labeled, ruled. (7) 11a/11b verbatim; Q1 leading, Q3 compound.|

**Severity:** BLOCKER B-1. MATERIAL M-1 launchd `-p` unproven before twin kill; M-2 orphan 4394; M-3 ppid-1 children; M-4 prompt gaps; M-5 Q2 pin; M-6 addenda text. NIT: installer stricter than gate; wake-source sentence; stale 17b lines.
**Disagreements with labeled disposition:** Q3, Q4. Else concur with conditions.
