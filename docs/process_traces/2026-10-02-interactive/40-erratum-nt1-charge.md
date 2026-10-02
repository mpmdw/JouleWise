# Cold erratum E-NT1: the network-time OFF receipt's wording, and the chain of two successors before C1

You are a COLD judge (Fable 5.1): fresh session, no loop context. Do not read RUN_STATE.md,
TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination
disclosure first** (what you read before ruling, and anything outside this charge's list).

You are one non-interactive session: every command in the foreground, no background task, no
subagent. Ending your turn before your output file exists is a protocol failure. Read-only
except your output file and scratch `/tmp/cg-ent1-d138/`. Never run sudo, systemsetup,
launchctl or powermetrics. No git fetch/pull/checkout/commit. Budget 45 minutes.

Working directory: this fresh detached worktree. Interpreter: `python3`, or the measurement
clone's `/Users/edr/night-custody/measurement/JouleWise-measurement-20261001T2252Z-r6-c2/.venv/bin/python`.

## Why this erratum exists

The sealed registration `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`
(Revision 6, sealed at commit `46643f1d`, 2026-09-30 15:09 PDT; file sha256
`d0034003a7e61683696b88662825d909dc4bb8ad23678edad6bbc8dfd4877b78`) says in §5 "Network time"
that a window is admitted by one settled OFF receipt whose standard output "is exactly
`setUsingNetworkTime: Off`", and its §7 JSON carries `"stdout_exact": "setUsingNetworkTime: Off"`.

Both counting windows of block 1 (sessions `d079-epoch-25g83-r6-20261001T0617Z` and
`d079-epoch-25g83-r6-20261001T2252Z`) recorded, in `night/network_time_off.json`, exit 0 and
stdout `Network Time is already off.\n`. They were admitted by the recognizer
`joulewise/network_time_off.py` (`ADMITTED_OFF_STATEMENTS`, `off_stdout_admitted`), widened in
commit `2431dcaa` (2026-09-30 21:13 PDT) after the seal and after the first C1 attempt
(`...-c1-20261001T0137Z`) was refused at t0 on the one-wording check. The registration text was
not amended. The owner's standing route for exactly this case (Ed, 2026-09-30, commit
`835aaba3`, refusal route R3) is: "If the fix makes code disagree with the sealed
registration's text, write an erratum record and convene one cold Fable gate on it, then
proceed on its ruling." That gate was not convened at the time. This is it.

The cold science gate on the block 1 candidate (ADMIT) and its refuter (AGREE) both asked for
an erratum or a written ruling before issuance. Read their words:
`docs/process_traces/rev6-derivation-block1/packet/RULING-judge.md` §6 items 1 and 3, and
`docs/process_traces/rev6-derivation-block1/packet/REFUTER-on-ruling.md` (search "network",
"successor", "0555Z", "0137Z").

The owner's rules that bind: numbers must be true (the threat is a wrong number, not
forgery); network time stays OFF on this Mac for good (decision D-186); windows run back to
back. Ruling-findings settle in ONE erratum, not a chain.

## Question 1 (E-NT1): does the OFF receipt condition admit `Network Time is already off.`?

Decide whether the sealed text's purpose is met by the two receipts, and if so, adopt erratum
text that makes the registration say what the admitted receipts are. A proposal you may adopt,
amend or reject:

> **E-NT1.** In Revision 6 §5 "Network time", the condition "its standard output is exactly
> `setUsingNetworkTime: Off`" reads: "its standard output states the OFF end state: after
> trimming surrounding whitespace, one trailing period and letter case, it equals either
> `setUsingNetworkTime: Off` (the setting was ON and is now OFF) or `Network Time is already
> off.` (the setting was already OFF)". The §7 JSON key `stdout_exact` is read the same way.
> Every other receipt condition (exit status 0, the tolerated stderr diagnostic, same boot,
> at least 600 s before the first capture on both clocks, one receipt per window) is unchanged.
> No number, member, statistic or operative changes.

Checks you must execute (record each command and its result):

1. Read both windows' receipts and the refused attempt's receipt:
   `/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0617Z/night/network_time_off.json`,
   `/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c2-20261001T2252Z/night/network_time_off.json`,
   `/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0137Z/night/network_time_off.json`.
   Confirm exit status, stdout, stderr, boot identity and the age before the first capture on
   both clocks, from the receipts and the first capture's evidence (the first slot `d01` under
   `runs/instrument_validation/`), by your own arithmetic.
2. Read `joulewise/network_time_off.py` and `git show 2431dcaa` (code and tests). State exactly
   what the comparator admits and refuses (run it on the receipt bytes and on: `setUsingNetworkTime: On`,
   the empty string, `Network Time: Off` (the getter form), `You need administrator access to
   run this tool... exiting!`). Your adopted text must describe what the code does, or you must
   say where they differ.
3. Read Revision 6 §5 "Network time" and the §7 JSON `network_time_off_receipt` entry. Decide
   whether a literal reading ("exactly `setUsingNetworkTime: Off`") is consistent with the
   rest of §5 (network time "stays OFF"; the ON-then-OFF resync is optional "allowed only in
   the window's arm step").
4. Find every place the issuer (`scripts/issue_calibration_acceptance_generation.py`) or the
   R9 record checks the receipt, and say whether issuance reads the stdout at all.

## Question 2 (the RULING-judge §6 item 3 chain): is a chain of two successors before C1 within D-182 and A-R5b?

Before the admitted C1 session (`...-c1-20261001T0617Z`), two
attempts at the label C1 refused with zero capture:

- `...-c1-20261001T0137Z`: published and armed; refused at t0 with `night_probe_error`,
  "network time OFF receipt not admitted" (the wording above). Custody:
  `/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0137Z/` (`night/result.json`,
  `night/refusal.json`, `night/network_time_off.json`, `night.log`).
- `...-c1-20261001T0555Z`: refused at the bench's step 0 battery gate (InstantAmperage
  −447 mA) before anything was published. Record:
  `docs/process_traces/2026-09-30-activation-e4df3b93/00-session-record.md` items 2 and 3, and
  `docs/process_traces/2026-09-30-activation-e4df3b93/c1-rearm/battery-refused-0555Z-attempt.txt`.

The rules: decision D-182 (`docs/decision_log.md`, section "## D-182", the rule and its
"Terms" paragraph only), amendment A-R5b's "Admission" paragraph and Revision 6 §7's
null-session text and `STOP-NULL-REPEAT` (in the registration), and the owner's 2026-09-30
refusal route, which reads in full:

> R1. Which refusals. A *pre-start refusal* is one where `night/result.json` has `verdict`
> REFUSED, `chain_exit_code` null and `chain_sha256` null, no `chain.started` record exists,
> and no session id was opened. Nothing was measured, and the registration gives such a window
> no label (Revision 6 section 7, clause [0]), so the same label (C1, C2 or C3) is armed again.
> [...]
> R3. Cure. If the cause is machine state (an agent or app alive, battery not floating,
> thermal), cure it or wait for physics, then re-arm. If the cause is code, config, the recipe
> or a bench script: fix it [...] If the fix makes code disagree with the sealed
> registration's text, write an erratum record and convene one cold Fable gate on it, then
> proceed on its ruling. [...]
> R4. Re-arm. Run recipe sections 1, 3, 4, 5 for the same label with a new plan id [...]
> R5. Bounds. The same refusal signature (reason plus detail) twice in a row goes to Ed as a
> consult with the diagnosis; never a third arm on one signature. The registration's own stop
> after two consecutive null sessions also halts. [...]

Decide: were these two attempts each within the terms under which a zero-capture refusal may
be followed by a new plan, so that the C1 that ran is an admissible window of this
registration? Specifically: (a) did either attempt open a ledger session (check the ledger
`/Users/edr/night-custody/measurement/JouleWise-measurement-20261001T2252Z-r6-c2/runs/calibration_observation_ledger.jsonl`
for any row naming either plan or a session other than the two admitted ones after the pinned
head), so that either is a session or a null session under §7; (b) can either attempt have
selected on any measured value; (c) does anything in D-182, A-R5b or Revision 6 bound the
number of successive zero-capture refusals before a label's window runs, and was that bound
respected.

## Output

Write `docs/process_traces/2026-10-02-interactive/41-erratum-nt1-ruling.md` in this worktree.
Its **first line** is exactly one of:

- `ERRATUM E-NT1: ADOPT <the adopted erratum text, one line>`
- `ERRATUM E-NT1: REFUSE`

Its **second line** is exactly one of:

- `CHAIN: WITHIN TERMS`
- `CHAIN: OUTSIDE TERMS — <one-line consequence>`

Then: the contamination disclosure; a table of every executed check (command, result); your
reasoning for each question; whether either answer bears on any member, statistic, operative
or the admission of either counting window; and a 3-line plain summary at the end. If the
receipts do not meet the registration under your reading, say so in a line beginning
`RECEIPTS DO NOT MEET THE REGISTRATION:`.
