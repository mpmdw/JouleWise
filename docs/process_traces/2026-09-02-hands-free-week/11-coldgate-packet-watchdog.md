# Cold-gate packet: the magistrate relaunch watchdog (2026-09-02)

Assembled by the magistrate at origin/main (commit named in the launch message). Seats read this packet, the manifest exhibits, and the code read-only. Atomic questions only.

## 1. Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## 2. Convening triggers (charter §3)
- Item 2: the design reinterprets ruling R-9 (exhibit 11a, "stand-down" clauses ~:159-168), which assigns stand-down to the magistrate and to Ed's behaviour, by moving the deadline and the force to a launchd-driven supervisor.
- Item 3: installing a standing launchd job that starts Claude sessions is a window-adjacent commitment.
- Item 4: the fence predicate, census scope and stand-down timings are process rules.

## 3. The object
The three designs (exhibits 03, 04, 09) answering brief 02, and the magistrate's proposal (exhibit 10 §2–§4). Controlling texts: exhibit 11a (R-3, R-7, R-9), exhibit 11b (D-171 verbatim), `docs/decision_log.md` D-127 and D-161 and D-169, `joulewise/night_gate.py` (`AGENT_CENSUS_ARGV` :34, `agent_census` ~:388-415, stale checks ~:594-609, census refusal ~:611-619), `scripts/run_night.py` (courier lock and dead-man), `scripts/install_night_agent.sh`, `configs/launchd/*.template`, `claude --help` at the bench (2.1.259).

## 4. Questions
**Q1.** Given D-171 (exhibit 11b, items 4 and 7) and R-9's text (exhibit 11a), may the stand-down DEADLINE and the FORCE (SIGTERM/SIGKILL of the session's own process group) be owned by a launchd supervisor, with the session's cooperative exit as the preferred path? Answer YES/NO and quote the R-9 clause you rely on or that blocks it.

**Q2.** Spawn mechanism: `claude --bg` (a persistent background session; exhibit 10 §2 row "Spawn") versus `claude -p` (one turn, stream-json). Which must the build use as its base, and what bench proof must precede install (state the exact command and the observable that proves it, e.g. a `--bg` session started from a launchd job with no TTY that survives its first turn and honours a scheduled wakeup)? Execute `claude --help` and `claude --bg --help` read-only; do not start a session.

**Q3.** Census scope: R-3 requires the watchdog to use the production census. Exhibit 10 §2 proposes requiring an EMPTY census only inside a plan's span [t0 − 20 min, completion] or while a chain runs, and otherwise launching whenever no owned child, no lock, no stop branch and no backoff. Is that narrowing consistent with R-3 and D-161? If not, give the rule you would install instead.

**Q4.** Stand-down timings: request file at t0 − 20 min; SIGTERM at t0 − 5 min; SIGKILL at t0 − 4 min. Verify against the chain's own pre-capture settle (find it in `scripts/`/`docs/phase_2/window_runbook.md`, quote the seconds) and the gate's census moment (`run_night.py`): is 5 minutes sufficient for the census to be empty and the machine quiet at t0? Give the minimum you would accept and why.

**Q5.** Kill switch as a GitHub branch `ops/stop-magistrate` probed by anonymous `git ls-remote --exit-code` each poll (exhibits 03 §8.3, 04 §8 item 8) versus a root file on main (exhibit 09). Execute the ls-remote probe read-only and paste the exit code. Which, and does the branch form need any authentication or rate consideration?

**Q6.** Session cwd = the canonical checkout `/Users/edr/code/JouleWise` (exhibit 10 §2 row "Session cwd") with a prompt-level ban on git operations there while a plan is armed, versus a dedicated worktree (exhibit 03 §8.6). Must the plan-pin change (pin `night_plan.json` to the measurement checkout's HEAD instead of the dev tree's, audit item cited in exhibit 10 §1) land BEFORE the watchdog installs, or may it follow? Answer for both the rehearsal-stub case and the first real window.

**Q7.** Install handoff (exhibit 10 §4): after the gauntlet and this gate, the magistrate emails Ed the install notice and installs without waiting for a reply, per D-171 item 4 (exhibit 11b). Is that reading of D-171 correct? Quote the words.

**Q8.** Packet hygiene (charter §6): complete and neutral? Name any missing exhibit or leading phrasing. Also state whether exhibit 10 (the magistrate's own synthesis) contaminated your reading of 03/04/09 — read those first if you can.

## 5. What the seats must not do
Do not read RUN_STATE.md, council_log.md, run reports, CLAUDE.local.md, session memory, scratchpads. Do not start any `claude` or `codex` session. Do not write under any checkout; do not touch `~/Library/LaunchAgents` or `~/night-custody`. Do not end mid-flight.

## 6. Exhibit manifest

```
3d0850e25b5b4d5c5a3690e6617f580387fa5f0111f673f3489a895770d935e3  02-watchdog-design-brief.md
615efa7ef62589a07ef249d4bf15e1ac74bf4e42bbed6547e475e3bbe914f2d2  03-watchdog-design-opus.md
5aebf065c1364a8c924e2faea505a2ac93c98cff04703d6e39d74702d44881b5  04-watchdog-design-blind-fable.md
4a0ffb1d2a70e7f7c9f179e116d9e7670f42b90e915c71c2feb2065324f016e7  09-watchdog-design-sol.md
8c10a929e430274b5618ca9c31e760bed88703e21f251c895e52b0bed925360e  10-watchdog-magistrate-synthesis.md
9f0e6be1beec32b0eb525886181e3704bf3d57343ac046bf84c8ec4322228611  11a-exhibit-ruling-unattended-stage1.md
cae85fe18bc96d7fbbdda1b2ea170879ea2c9096523eaab6ebff7cb013de520a  11b-exhibit-D-171-verbatim.md
```
