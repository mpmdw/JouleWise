# 06 — Registration of REFUSAL-FAST-RETRY-01 (2026-09-16 ~00:08 PDT, activation `08ca8197`)

## Source

At ~00:05 PDT the interactive session `b0ae8462` (Ed at the machine) relayed
Ed's remark on the cost of a t0 refusal (about three hours per refusal),
quoted by that session as verbatim:

> "how have we not made this a lower cost to pay"

Not a directive issue (`gh issue list --label directive` empty before this
slice). Registered as relayed.

## Facts re-read by this activation (main at `45f88f55`)

- `scripts/magistrate_watchdog.py:718` — span end `= plan.t0_epoch_s +
  plan.window_max_s + COURIER_DEADLINE_S`; `:721` `plan_span_active`; used by
  the launch predicate at `:817` and the active-plan filter at `:1411`. A
  refused night therefore holds the magistrate away for the whole programmed
  span (9000 s window + courier deadline) although nothing ran.
- `joulewise/night_gate.py:103-109` — the refusal codes:
  `night_refused_agent_present`, `night_refused_class_unbuilt`,
  `night_refused_hid_idle`, `night_refused_not_quiet`,
  `night_refused_boot_clock`, `night_refused_registration`.
- Kernel: `ARM-RETRY-CLASS-01` blocked (rank 172), `INSTALL-WINDOWS-MULTI-01`
  queued (rank 0), `LEAD-MARGIN-01` blocked (rank 210).

## What was registered

Kernel row `REFUSAL-FAST-RETRY-01`, rank 212, `p1_phase_gate`, lane `agent`,
status `blocked` with hard start dependencies on `ARM-RETRY-CLASS-01` and
`INSTALL-WINDOWS-MULTI-01`. Kernel 185 → 186 rows; `TASK_QUEUE.md`
regenerated; `tests/test_gen_state.py` updated. Registration only; no code
changed.

Part (b) of the lane (treating a zero-capture machine-state refusal as a
pre-authorized retry) is a process rule. Under rule 11 it is not this
activation's or the lieutenant's to ratify: the row records it as waiting for
Ed's ruling (or the cold gate's with Ed's sight), to be installed as a dated
decision-log addendum plus NIGHT_HANDBACK / runbook §1.4a prose. Parts (a)
(span accounting) and (c) (tests) are mechanism. The D-161 evidence fence and
every t0 gate stay untouched.

## Amendment (2026-09-16 ~00:40 PDT) — part (b) ruled

The interactive session relayed Ed's ruling of 00:35 PDT, quoted as verbatim:

> "unless there's a scientific reason that's an unsound decision absolutely
> reduce the hours to 20 min"

Applied to the row: part (b) is RULED, not ruling-gated. A zero-capture t0
refusal on machine state (`night_refused_not_quiet`,
`night_refused_agent_present`, `night_refused_hid_idle`,
`night_refused_boot_clock`; `refusal.json` present, no receipt, no
`chain.started`) is a pre-authorized retry in the ARM-RETRY-CLASS-01 shape.
Registration and class refusals and any refusal after a capture started stay
on the cold-gate path. The one exception the ruling admits is a scientific
reason that the retry is unsound; the seat must state it if it finds one.
The ruling arrived by relay, not as a directive issue; the lane's
decision-log addendum is where it is recorded for the doctrine. Still
registration only; nothing changed in code.
