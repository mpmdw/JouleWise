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

## Standing transaction handoff

A frozen experiment pack is an immutable set of reviewed measurement inputs.
An unattended transaction night is a scheduled measurement that uses one
such pack without a person at the keyboard. The arming step is
the preparation that checks that pack. An arm receipt is its one-use record
that the pack passed those checks. The arming step must place the confirmed
SHA-256 digest, a cryptographic fingerprint called `hC`, in the plan's custody
root, the protected directory named by the night plan, as
`085-ed-step6-confirmed-sha256.txt`. That custody file must be a regular file
rather than a symbolic link, a filesystem pointer to another path; must have
owner-only read and write permissions (filesystem mode `0600`); and must
contain only the lowercase digest followed by one newline.

The night gate is the pre-launch check that evaluates every required launch
condition. It creates a GO receipt, the record that those conditions passed,
only after it authenticates the arm receipt and the frozen launch inputs with
the digest stored in custody. The night driver is the program started by the
schedule. The reviewed launcher is the program that consumes the one-use arm
receipt as one indivisible operation and starts the frozen measurement chain,
the immutable sequence of measurement commands. The arm-readiness
custody root is the protected directory that holds the arm records. The launch
manifest is the authenticated record of the exact frozen command. The step-6
confirmation table is the published record of the pack-family confirmation.
When the receipt says GO, the night driver calls the reviewed launcher once
and supplies those records and paths. A missing input, an altered digest, an
insecure custody-file mode, or any launcher refusal ends that attempt without
a retry.

This is the narrow amendment to the earlier instruction that `hC` must never
be stored in an environment file: automation may store `hC` in the protected
custody file above, but it still must not store `hC` in an environment file or
derive it again from the confirmation table at launch time.

## Purpose of this night

Plan `rehearsal-20260903`, class `REHEARSAL_STUB`, armed by the magistrate
(Fable, standing loop, the morning of 2026-09-02; RE-ARMED the evening of
2026-09-02 — a fresh audit caught that the magistrate's own daytime pulls
had moved the canonical checkout HEAD past the plan's pinned `repo_head`,
so the gate would have refused `night_plan_stale`; the plan was re-pinned
to the re-arm commit and both plists re-rendered, which also refreshed the
courier binary pin past a same-day claude self-update) for 02:56 local on
2026-09-03 with a 900 s window. The chain is the driver's built-in stub
(`sleep 2; echo REHEARSAL`); no pack, no model, no measurement, no sudo.
This is the "installed the morning before" stand-down rehearsal ruled by
the cold gate D1 R-7 amendment
(`docs/process_traces/2026-09-01-unattended/coldgate-d1-RULING.md`): the
agents were installed around 03:30 on 2026-09-02, so the dead-man's
07:00 firing on 2026-09-02 lands BEFORE the armed night, and the ruled
observable is its stand-down — one `night.log` line ("dead-man fired
before the night's completion epoch …; standing down"), exit GO, no other
writes. The night itself then fires from launchd at 02:56 on 2026-09-03 as
a second end-to-end rehearsal. The gate receipt may again refuse
`night_refused_agent_present` if the standing loop's own sessions are
alive at 02:56 — acceptable for a `REHEARSAL_STUB` (it can never carry
GO); any OTHER refusal reason is a finding. Serves kernel row
`NIGHT-REHEARSAL-01` (the R-7 stand-down rehearsal case). The first
launchd rehearsal (`rehearsal-20260902`) completed 2026-09-02: verdict
`REHEARSAL_ONLY`, chain exit 0, courier message id `1a0618d143537010`,
branch `night-results/20260902`.

## Where the results are

- Stand-down observable (from the 2026-09-02 07:00 dead-man firing):
  the "standing down" line in
  `/Users/edr/night-custody/rehearsal-20260903/night.log`.
- Results branch: `night-results/20260903` on `origin` (pushed by the
  driver from a fresh shallow clone; readable from a phone).
- Custody root: `/Users/edr/night-custody/rehearsal-20260903/night/` on the
  measurement machine — `result.json` (expected verdict `REHEARSAL_ONLY`,
  `chain_exit_code` 0), `receipt.json`, `chain.started`, `chain.exited`,
  `censuses.jsonl`, `night.log`.

## Next lane

Resume the standing loop (`/loop` mandate; memory `unattended-loop-first`):
the magistrate harvests the custody root AND the stand-down log line,
records both under `NIGHT-REHEARSAL-01`, then runs
`scripts/install_night_agent.sh --plan /Users/edr/night-custody/rehearsal-20260903/night_plan.json --hour 2 --minute 56 --uninstall`
at the SAME commit the plan was RE-armed on (the re-arm commit that
rewrote this file; the installer checks `repo_head` before the uninstall
branch — after PR #268 the uninstall path no longer needs `claude` on
PATH), so the dead-man job stops firing at 07:00. The canonical checkout
must not be pulled or moved between the re-arm and the night's
completion — the gate compares the plan's `repo_head` to the CANONICAL
checkout HEAD, and the original arming of this plan was invalidated by
exactly such a daytime pull (stage-2 finding: morning-before arming plus
an active canonical checkout guarantees `night_plan_stale`). Then the last stage-1 item: the stage-1 plan email to Ed (first
armed date; launches unless he replies NO) before any `DIAGNOSTIC_NO_PACK`
plan is armed. Ed was emailed the arming notice for THIS night before it
was armed (cold gate coldgate-e10 (b)); if Ed replied NO on that thread,
stand the night down instead of harvesting. A refusal other than
`night_refused_agent_present` on this night is a finding: cure the cause
before re-arming; never re-arm the same plan on the same signature twice.
