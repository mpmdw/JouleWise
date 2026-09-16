# 02 — Lane registration: NOTICE-TRANSPORT-FALLBACK-01 (from Ed's directive issue #349)

Registered by activation `83d93f5a` at 02:53 PDT 2026-09-16. Registration,
not a ruling: the authority is Ed's owner-authored `directive` issue.

## Authority, verbatim (issue #349, author `mpmdw`, filed ~02:34 PDT)

> DIRECTIVE (Ed, owner, at the machine, 2026-09-16 ~02:40 PDT). Standing ruling; applies to tonight's REHEARSAL_STUB and to every window after it.
>
> ## Ruling — notice transport fallback
>
> When the Gmail connector is unavailable to the magistrate (session expired, connector "Server not found", or no send tool exposed), the arm notice may be posted as a new issue on this repository with the label `directive-notice`, carrying exactly the content the email would carry (plan id, sha, t0, install close, dead-man, clone H, span list). GitHub emails me on new issues, so the no-objection window and my NO channel are unchanged: a comment or a directive issue from me saying NO before install close stops the arm. The arm record names the transport used. Email remains the primary transport when it works.
>
> ## Implementation
>
> Register lane NOTICE-TRANSPORT-FALLBACK-01 to make the fallback durable in NIGHT_HANDBACK and the runbook (docs + test), with this issue as authority. Tonight: re-plan the stub to the earliest whole-minute t0 the margins allow, send the notice by issue, arm.

## What the lane does

Docs: NIGHT_HANDBACK (the `arm_transport` row and the notice procedure) and
runbook §1.4 name the issue transport, its label, its required content, the
unchanged NO channel, and the rule that the arm record and `notice.json` name
the transport. Code: the notice-evidence writer (today
`notice-json.py` in the stage directory, to be promoted with the lane) accepts
an issue number + URL in place of a Gmail message id + thread id; the arm
block's notice precondition accepts either. Test: an issue-transport
notice-evidence record carries the same plan pins as the email form; a missing
transport field fails closed. No t0 gate, census, or retry cause changes.

## Tonight's application

The fallback was NOT needed: the Gmail connector worked in this activation
(launch email 02:46, notice 02:50:06), so the notice for `rehearsal-20260916c`
went by email and the arm record names EMAIL as the transport. The "send the
notice by issue" clause was read as the fallback for a down connector, per the
ruling's own first paragraph ("Email remains the primary transport when it
works").
