# 121 — Ed's rulings of 2026-09-10 ~03:30 PDT: arm recoverability, session kill, paper priority, remote control between windows

Recorded by the interactive magistrate (session `01MrRehZWopqKNDv5Uy466AC`) from Ed's messages in that session. The questions Ed
answered are quoted from the magistrate's message of ~03:15 PDT; Ed's answers are verbatim.

## The three recoverability proposals Ed was asked to grant (magistrate, ~03:15 PDT)

> Three things would make that cheaper, and all three are yours to grant with a sentence, which I would then record as a dated
> decision-log addendum:
> - Install windows more than once a day, so a missed arm slips hours, not a day. You already said quiet windows are any time; the
>   install window is the only remaining night-only constant.
> - A pre-authorized retry class: an arm abort whose cause is not physics (idle interactive session, stale notice hash, a clock tick)
>   may be retried in the same or next window without a cold gate, with only a notice email. Physics and evidence refusals stay hard.
> - A standing rule that idle interactive sessions do not count as foreign for the arm-time census of stub nights. I would not grant
>   this one myself: the runbook's "only-own census" was ruled for this specific night, and the same probe protects real nights.

## Ed's answers (verbatim, ~03:30 PDT)

> 1, yes to all 3
>
> 2. KILL as long as you can keep experimenting and have all the tools to keep running windows until you have a paper, i guess ill
> sacrifice perfect observability for the solution you posed earlier where i open github issues and shit
>
> 3. yeah that'l work fine i just want a minimum viable paper already
>
> 4. yeah get that working so inbetween windows you can relaunch and be accessible

Item 2 answers "Say KILL and I terminate both processes myself, this one included, right after PR #313 merges." Item 3 answers the
issues-versus-email expansion (the GitHub-issue directive channel, PR #313). Item 4 answers "The queued remote-control test is the only
way to get live steering between spans, and I would run it after this night."

## What was installed from these words

- Decision log **D-180** (three clauses = item 1; clause 4 = item 4; item 2 and item 3 recorded as standing direction).
- Kernel rows: `INSTALL-WINDOWS-MULTI-01`, `ARM-RETRY-CLASS-01`, `ARM-CENSUS-IDLE-INTERACTIVE-01`, `REMOTE-CONTROL-BETWEEN-WINDOWS-01`
  (all `agent` lane, queued; decided ≠ done — each lands under the normal gates; until each lands, the ruled 03:00–06:30 window, the
  cold-gate path for aborts, and the raw only-own census stand).
- The interactive sessions (pids 16371 and 17047) are terminated by the interactive magistrate after PR #313 merges and this record is
  pushed, so the resident activation can arm rehearsal-20260911 inside the 09-10 window.

## Limits stated at the time of recording

- Clause 3 (idle interactive sessions not foreign) applies to the ARM-TIME census of stub nights only. The plan span is unchanged:
  from t0 − 25 min until the chain exits, any agent process refuses the night (`night_refused_agent_present`), because the measurement
  counts every process. A session left open through t0 still kills the night even after clause 3 lands.
- Clause 2's retry class is enumerated in D-180; anything not enumerated stays on the cold-gate path.

## Ed's sequencing statement (verbatim, ~03:45 PDT), after the magistrate recommended shelving remote control

> Because it occurs to me that once the instrument is validated as useful, it's very important you're able to run experiments and for me to direct the experiments remotely. That way, I don't have to be at the machine, and we can do plenty of science. That is the goal.

Installed as: the four D-180 lanes stay queued (not shelved); REMOTE-CONTROL-BETWEEN-WINDOWS-01 depends on G2A-FIRST-WINDOW-01 and becomes p1 once a real window has validated the instrument; the next exact action after tonight's harvest is G2-a, not another rehearsal.
