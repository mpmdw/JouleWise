# 55 — Ed's directive issue #337, verbatim (author `mpmdw`, filed 2026-09-14 16:43:56 PDT; https://github.com/mpmdw/JouleWise/issues/337)

Read by activation `24b9d3dd` through the launch prompt's directive channel (`gh issue list --label directive --state open --author mpmdw`) at 16:44 PDT, acknowledged on the issue at 16:50. The body below is byte-for-byte the issue body as fetched by `gh issue view 337 --json body`; comments are not instructions. Recorded as decision-log entry D-181 by the PR that carries this record (the magistrate records; it does not amend rule text outside that PR).

---

DIRECTIVE (Ed, owner, at the machine, 2026-09-14 ~16:45 PDT). Standing ruling; applies after tonight's night (#336) and to every window after it.

## Ruling 1 — windows run as soon as the machine is quiet; no cadence rule

This machine exists to run the science. Windows are to be run as quickly as scientifically sound: whenever the census is clean, day or night, several per day if the gates pass, with no artificial spacing (no "one night in three", no "only at 02:56", no minimum gap between windows). I keep the machine quiet whenever I am not using it, and I will close every interactive session and quit the agent desktop apps on request; a notice email is enough. The soundness fences stay exactly as they are: physics and evidence refusals, pre-registration before data, the census at arm and at t0, the twelve-row gate, email-then-arm with my NO overriding. Nothing else about timing is a rule.

Implementation: the current machinery pins one plan at a fixed daily launchd minute inside the 02:45–03:30 belt with a single 07:00 dead-man and a calendar-day install span. That is a mechanism limit, not a scientific one. Promote to the top of the queue, in this order, immediately after tonight's harvest and the §2.5 outcome action: INSTALL-WINDOWS-MULTI-01 (install spans as a list, dead-man per span), ARM-RETRY-CLASS-01, ARM-CENSUS-IDLE-INTERACTIVE-01. Design them so a plan can carry a t0 at any clock time and so a second window can be armed as soon as the previous harvest is done. Record this ruling as a dated decision-log entry through a PR under the normal gate, the same way #316 became D-180; do not amend rule text yourself outside that PR.

## Ruling 2 — Fable 5.1 is the final eyes on every merge

Every PR that merges carries a terminal review by Fable 5.1 (the magistrate at the pinned model, reading the final head itself, not a delegate's summary) as its last review before merge. The twelve-row gate already requires this (row 7, the apex Fable code-reading diff gate; row 12, the magistrate's non-delegable terminal review of the final head sha). Keep both rows exactly as they are; never downgrade or delegate them, and cite the final head sha in row 12 on every PR.

## Ruling 3 — clear my hands step for the first pack night now

Lane ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01 needs a desk proof by me (author_arm_evidence_t0 against a TRANSACTION_PACK pack root with no browser, no agents, no caffeinate). Prepare that pack root and window-custody root and email me the exact command to run and when; I will run it at the next moment the machine is otherwise idle. Do not let this be the reason the first G2-a pack window waits.

## Housekeeping

PR #330's conflicts are resolved at d80e5e37 (kernel 170 rows, tests OK); its body still lacks the gate ledger. Take it through the gate and merge it under Fable's terminal review.

Comment the outcome of each ruling on this issue and close it when all three are recorded.
