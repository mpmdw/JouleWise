# Cold-gate ruling: may the watchdog-owned headless magistrate arm a REHEARSAL_STUB night?

**Contamination disclosure.** Before reading the packet, my launch context carried the repo's tracked `CLAUDE.md` and an auto-memory index of one-line pointers about this project (magistrate/watchdog/cold-gate topology, Ed's standing directives on unattended windows, seat-launch rules). I did not open `RUN_STATE.md`, `AGENTS.md`, any memory file, or any doctrine beyond the packet, its six exhibits, the four decision-log rows exhibit F names, and the file:line cites below. I had no prior knowledge of plan `rehearsal-20260909`, activation 1ef89702, or the line-19 conflict.

Judge: cold Fable, 2026-09-08. Packet sha256 verified `f4521c89…ac7b2`.

## Executed evidence (this session, foreground)

1. `~/night-custody/*/night_plan.json` glob: empty. LaunchAgents matching joulewise: only `com.joulewise.magistrate.plist`.
2. `magistrate.lock`: activation `1ef89702-…`, pid 84232, status ACTIVE, start 2026-09-08 00:51:55. `state.json` state ACTIVE. `events.jsonl` seq 3 LAUNCHING, seq 4 ACTIVE, then `notice_acknowledged`.
3. `/private/tmp/joulewise-rehearsal-20260909-checkout`: does not exist.
4. `ae8f074f` exists and is on `origin/bookkeeping/2026-09-08-activation-evidence` only. Not on main.
5. `scripts/magistrate_watchdog.py:258-259`: the watchdog discovers plans by `root.parent.glob("*/night_plan.json")`. A new plan directory beside `magistrate/` is read on the next tick.
6. `joulewise/night_plan_writer.py:38-62`: `write_night_plan` writes a `0600` temp file, fsyncs, `os.replace`s, fsyncs the directory. Atomic; the watchdog can never observe a half-written plan.
7. `joulewise/night_gate.py:263-267`: `from_mapping` requires `measurement_root` to be absolute; it does not require it to exist. `scripts/install_night_agent.sh:80-95`: install refuses unless the driver checkout HEAD equals `repo_head` and the measurement checkout HEAD equals `measurement_head`.
8. `scripts/run_night.py:635-665`: courier argv is `claude -p <prompt> --output-format text --allowedTools …`, distinct from the magistrate launch. Exhibit E is right that magistrate email success is not courier evidence.
9. Decision-log rows 171, 172, 195, 215 read as exhibit F quotes them. NOT EXECUTED: Gmail thread `1a0800cdb282c3f1`; the arm email is taken as asserted.

## Findings

1. **The conflict is real but textual, not structural.** Lines 11-13 assign arming to this session; exhibit B line 73 says arming "remains outside this watchdog's charter and always uses the email-then-arm handback." D-128 and D-169 place the loop, including re-arms, on the magistrate without Ed present. The headless magistrate is the magistrate. Line 19's unqualified "plans" and "launchd configuration" over-reach the intent the charge states: no headless session may move watchdog-owned state or an already-armed plan.

2. **Failure-mode test passes.** Arming writes one new plan directory and two night LaunchAgents. It does not write `state.json`, `magistrate.lock`, `standdown.request`, `events.jsonl`, or `com.joulewise.magistrate.plist`, and there is no armed plan to move (glob empty). The watchdog then reads the new plan (evidence 5) and will fence and drain this very session at t0-25 min, which is line 12's intended consequence, not a bypass. A malformed plan would drain the session immediately (`HOLD_UNSAFE`); that is the designed fail-closed path, and evidence 6 makes it unreachable for a writer-authored plan.

3. **The interpretation should not stay an interpretation.** A later headless session will read line 19 cold and hit the same conflict. Amend the text.

4. **Condition (4) is impossible as written.** The arming session is itself an agent session. It must read "no other agent session," and it does not substitute for the driver's census, which D-169 fixes as the driver's first act.

5. **Pin durability gap.** The pinned commit lives only on a bookkeeping branch (evidence 4). Acceptable for a stub, but the branch must survive while the plan is armed, or the next relaunch prompt's frozen triple points at an unreachable head.

6. **/private/tmp question: no fence violated.** Exhibit D's fences concern email-before-arm, Ed's NO, honest receipt classes, and the census; none names a path. Exhibit B line 73 forbids reuse of a stub root by a real plan and requires stub roots be removed before any real plan; it does not forbid a real detached checkout at a `/private/tmp` path for a stub. Caveat, not a fence: macOS may purge `/private/tmp` on reboot or after prolonged non-access. Evidence 7 shows a vanished root is refused at night by the gate, so the failure mode is a refused stub, which the handback already classes as a finding to cure.

## Ruling: AMEND

Replace relaunch prompt line 19 with:

> Do not write, move, or delete watchdog-owned state (`state.json`, `magistrate.lock`, `watchdog.lock`, `standdown.request`, `events.jsonl`, `STOP`, `attempts/`) or `com.joulewise.magistrate` launchd configuration except through the heartbeat and notice-acknowledgment interfaces; do not alter, move, or delete any plan directory, night record, or night LaunchAgent belonging to a plan that is already armed except by the documented uninstall after that plan's completion. Authoring a new plan with `write_night_plan` and installing its two night agents under line 11 is arming, not an alteration under this line.

Conditions on this rehearsal, replacing the packet's four:

1. `NIGHT_HANDBACK.md` is committed with the real pins before the arm email. Satisfied at `ae8f074f`.
2. Both night agents install FROM `/private/tmp/joulewise-rehearsal-20260909-checkout` at `ae8f074f`; the installer's HEAD checks are the proof.
3. The arm email names t0, `measurement_root`, `measurement_head`, class REHEARSAL_STUB, and the courier deadline; no NO has arrived when the arm begins.
4. No agent session other than the arming session is alive at arm time; the driver's census remains its own first act.
5. `origin/bookkeeping/2026-09-08-activation-evidence` is not deleted or rewritten until the stub plan root and checkout are removed.
6. The arming session exits by `t0 - 25 min` per line 12, and the frozen triple enters the next relaunch prompt.

**Verdict: AMEND. Headless magistrate may arm rehearsal-20260909 under the six conditions; /private/tmp root violates no fence.**
