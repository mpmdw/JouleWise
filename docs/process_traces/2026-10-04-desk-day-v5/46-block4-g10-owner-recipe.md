# Ed's clock-anchor positive control, before measurement block 4

Status: software procedure prepared; **physical control not performed**. This
recipe supplies registration §5's mechanism, not a discharge or permission to
arm. The lead's round-2 ruling adopts exactly the existing arm-step resync
vector: `(*joulewise.network_time_off.OFF_ARGV[:-1], "on")`, as used by
`scripts/capture_t0_step.py::_arm_reference`. The helper imports that vector,
executes the reviewed passwordless `sudo -n` setter once, and polls the RAW
anchor for up to 120 seconds before finishing OFF through the existing receipt
producer in `finally`. No password prompt or new sudoers grant is needed under
the existing D-127 fragment. The privileged positive control remains Ed-owned
(D-176), with `performed_by="Ed"`. Normal clock-reference probes remain
report-only.

## When and why

Run this once before the isolated rehearsal (the registration calls it `r1`),
before its fresh time-zero sequence begins. Nothing may be armed, no capture
may be in progress, and no Claude or Codex agent seat may be running. Do not
run it between the three block occurrences or during a capture. Close every
agent seat before starting. The helper runs in your own terminal.

With automatic network time off for days, the wall clock can drift from true
time. Re-enabling network time and waiting for synchronization can step the wall
clock relative to the monotonic hardware counter. Their difference is the
clock anchor. The test succeeds only if the anchor moves by more than five
milliseconds and the real evidence author refuses that changed sequence.
Running the synchronization command without that movement does not qualify.

## Lead preparation, before handing over

Supply a clean, reviewed execution checkout containing this helper and the
real `scripts/author_arm_evidence_t0.py`, plus a committed control pack in that
same checkout. The author requires reviewed-main identity; a dirty feature
worktree cannot substitute. Prepare a separate, unused set of **real** author
inputs through the existing `scripts/capture_t0_step.py` workflow. Its six
captures, environment, launch manifest, OFF receipt and referenced inputs must
remain available at their original absolute paths. Do not invoke the author,
readiness authorization or launcher for that set. Do not use fixture bytes or
a production occurrence's namespace. Its first reference sample (called R0
by the author) must precede the control; the
author's 600–3600 second RAW span and reference quorum/order rules still apply.
Preparation must finish with network time OFF and without a running agent.

Lane B owns this input-preparation choreography. The helper snapshots the
input directory into new control custody before executing the ON command;
it does not generate replacements for the captures, shorten their dwell,
reserve a production bracket, or repair source inputs. The lead supplies the
following four exact paths in the handoff: checkout, pack, input directory,
and new control custody directory. Bind them before seal. They are runtime inputs, not values guessed in this recipe.

## What to type

In your own ordinary terminal, run this one command, substituting only the
four paths supplied by the lead:

```zsh
(cd '<reviewed execution checkout>' && .venv/bin/python scripts/ed_session/capture_t0_anchor_positive_control.py run \
  --pack-root '<committed control pack>' \
  --author-inputs '<real control arm_readiness.t0.inputs directory>' \
  --custody-root '<new isolated control custody directory>')
```

Read the prompt and type `OUTSIDE` only when no agent, armed window or capture
is running. The helper snapshots the inputs, stamps CLOCK_REALTIME and
CLOCK_MONOTONIC_RAW, then executes exactly:

```zsh
/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on
```

You see `Enabling network time once; polling RAW anchor for at most 120 s.`,
followed by the absolute anchor movement in nanoseconds on each poll. The
helper polls every five seconds, stopping as soon as movement is **greater
than** 5,000,000 ns or the deadline expires. The deadline includes the ON
command's execution; that command also has a maximum 30-second process timeout.
There is no separate synchronization command and no free command argument.
`--resync-timeout-s` defaults to 120 and accepts only 1–300 seconds; use the
default unless the lead explicitly supplies another bounded timeout.

If movement exceeds five milliseconds, the helper runs the real author once
on the preserved input sequence. Success requires exit 2, status `REFUSE`,
exactly `evidence_author_t0_clock_attestation_underivable`, and the detail
`R0-to-author RAW anchor delta exceeds 5000000 ns`. Neither the source nor
evidence publication namespace may exist. A different clock failure with the
same reason code is insufficient.

You then see `Finishing with network time OFF.` On success, failure or an
exception, the helper's `finally` calls
`joulewise.network_time_off.set_network_time_off`, which executes exactly:

```zsh
/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off
```

It retains the real result in the shared OFF receipt and reopens it with
`joulewise.network_time_off.read_receipt`. Exit 0 plus either normalized
`setUsingNetworkTime: Off` or `Network Time is already off` is admitted. OFF
has a 30-second process timeout and does not depend on a working anchor probe.
If the helper is forcibly terminated or OFF cannot be confirmed, run this same
OFF command manually, retain its output, and hand the failed custody to the
lead. Do not enter the block without an authenticated OFF receipt.

## Success, failure and evidence hand-back

Success is helper exit 0 with `status=DISCHARGED` and a path to
`positive-control.json`. This establishes the physical-control component;
the lead still authenticates lineage and combines it with the software
boundary controls for `evaluate_g10`. It is not rehearsal PASS or ARM authority.

If movement stays at or below five milliseconds through the deadline, the
author is not invoked. The helper completes OFF cleanup, records `NOT-DISCHARGED`, emits no positive
record and exits 2. Stop and tell the lead `NOT-DISCHARGED`, with the custody
path. **Do not retry.** The lead decides the next step; do not repeatedly
resynchronize or adjust the time by another method. Treat every other nonzero exit the
same way. Keep the complete directory, including failed attempts, immutable.

The output map, relative to the new control custody directory, is:

| Output | Contents / consumer |
|---|---|
| `before.json`, `after.json`, `anchor-movement.json` | Machine REALTIME/RAW/skew, ordinary monotonic time, boot, absolute anchor movement. |
| `author-custody/<pack-name>/arm_readiness.t0.inputs/**` | Exact copies of the real author input bytes; original absolute references remain unchanged. |
| `author-input-lineage.json` | Source/pack paths, R0 anchor, boot and real author code SHA-256s. |
| `polls/*.json` | Retained REALTIME/RAW/boot stamps for every resync poll. |
| `commands/on/**`, `commands/on.json` | Raw separated streams, actual ON return code, imported argv and machine start/end stamps. |
| `commands/off/**`, `commands/off.json` | OFF streams and admitted shared receipt, including exact argv, exit code, boot and completion clocks. |
| `author.stdout.json`, `author.stderr.txt`, `author-execution.json` | Real author's retained response, raw stderr, argv/exit/stamps and namespace absence census. |
| `network_time_off.json` | Existing `joulewise.network_time_off.v1` receipt, admitted by the shared reader; control identity only. |
| `positive-control.json` | Exact `joulewise.t0_unattended_anchor_positive_control.v1`, only after refusal and OFF admission. |
| `outcome.json`, `custody-manifest.json` | Structural discharge/failure and SHA-256 map of every supporting byte. No measurement metrics. |

The positive record has exactly eight keys: `schema_version`,
`performed_by="Ed"`, `outside_t0_sequence=true`,
`network_time_reenabled=true`, `forced_resync=true`, `anchor_before_ns`,
`anchor_after_ns`, `author_refusal_reason_code`. `forced_resync=true` requires
the ON command to exit 0 and the observed anchor movement to exceed five
milliseconds within the deadline; it is never recorded on a failed control.
The two anchor values are REALTIME minus RAW in nanoseconds. Supporting data belongs beside the record,
never in extra record keys. Lane B maps these authenticated bytes into the
rehearsal manifest's `positive_control` locator; its software falsifier record
remains separate. The lead fills the registration's record path/digest and
evidence map from the emitted files.

Leave network time OFF after this procedure. Every subsequent occurrence
gets a **new** OFF receipt on its own boot and completes at least 600 seconds
of settling on both clocks before its first capture/author boundary. Never
reuse the control's OFF receipt as an occurrence receipt or restore time ON
after a window.
