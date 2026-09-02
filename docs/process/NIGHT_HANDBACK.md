# Night handback

This file is what the night courier reads first (`NIGHT_COURIER_PROMPT.md`).
The magistrate rewrites the three sections below before every armed night
(ruling R-9, `docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`)
and commits the rewrite with the night's plan. Between nights the sections
hold the standing template text, so a courier that reads this file on a
night nobody armed reports exactly that.

The courier does not decide anything from this file. The verdict, the chain
exit code, and every refusal reason come from the result record under the
night's custody root: `night/result.json`, then `night/receipt.json` or
`night/refusal.json` as `result.json` directs. If this file and the result
record disagree, the result record is right and the courier says so.

## Purpose of this night

STANDING TEMPLATE — no night is armed. If a courier is reading this text,
say in the email that the handback was not rewritten for the night and
report the result record on its own.

Per night the magistrate replaces this section with one paragraph: the plan
id, the plan class (`REHEARSAL_STUB` or `DIAGNOSTIC_NO_PACK`), what the
chain was meant to produce, and which kernel row the night serves.

## Where the results are

- Results branch: `night-results/<night-date>` on `origin` (pushed by the
  driver from a fresh shallow clone; readable from a phone).
- Custody root: `<custody_root>/night/` on the measurement machine —
  `result.json`, `receipt.json` or `refusal.json`, `chain.started`,
  `chain.exited`, `courier.json`, `night.log`.
- Per night the magistrate fills in the real custody root and the branch
  name here.

## Next lane

STANDING TEMPLATE — resume the standing loop
(`/loop` mandate; memory `unattended-loop-first`): read
`docs/process/state_kernel.json`, take the highest-ranked open row whose
dependencies are satisfied, and continue under the ordinary rules. A
refusal night's first item is to read the refusal reason and detail and
cure the cause before re-arming; never re-arm the same plan on the same
signature twice (standing escalation trigger). Once the handback is read,
run `scripts/install_night_agent.sh --plan <plan> --hour H --minute M
--uninstall` so the dead-man job stops firing every 07:00 (cold gate D1,
`docs/process_traces/2026-09-01-unattended/coldgate-d1-RULING.md`).

Per night the magistrate replaces this section with the named next lane
(for a `DIAGNOSTIC_NO_PACK` G2-a night: run the summarizer over the pushed
results, then the selection record, then unblock `RENDERER-V5-SUCCESSOR-01`).
