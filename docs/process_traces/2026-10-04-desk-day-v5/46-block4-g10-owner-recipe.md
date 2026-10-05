# Ed's clock-anchor positive control, before measurement block 4

Status: software procedure prepared; **physical control not performed**. This
recipe supplies registration §5's mechanism, not a discharge or permission to
arm. The lead must review and pin the forced-resync vector and its deadline
before handing this recipe to Ed. The repository contains the reviewed
ON/OFF setter vectors in `scripts/joulewise-network-time.sudoers` and
`joulewise/network_time_off.py`; no existing reviewed forced-resync vector was
found. The proposed vector from the lane brief is
`/usr/bin/sudo /usr/bin/sntp -sS time.apple.com`. Its approval and timeout are
still lead inputs, required explicitly by the helper. This creates no new
passwordless privilege. Normal clock-reference probes remain report-only.

## When and why

Run this once before the isolated rehearsal (the registration calls it `r1`),
before its fresh time-zero sequence begins. Nothing may be armed, no capture
may be in progress, and no Claude or Codex agent seat may be running. Do not
run it between the three block occurrences or during a capture. Close every
agent seat before starting. The helper runs in your own terminal.

With automatic network time off for days, the wall clock can drift from true
time. Re-enabling network time and forcing synchronization can step the wall
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
input directory into new control custody before presenting any ON command;
it does not generate replacements for the captures, shorten their dwell,
reserve a production bracket, or repair source inputs. The lead supplies the
following five exact values in the handoff: checkout, pack, input directory,
new control custody directory, and approved resync timeout/vector. Bind them
before seal. They are runtime inputs, not values guessed in this recipe.

## What to type

1. Open two ordinary terminals. In the first, substitute only the paths and
   values supplied by the lead, then run:

   ```zsh
   cd '<reviewed execution checkout>'
   .venv/bin/python scripts/ed_session/capture_t0_anchor_positive_control.py run \
     --pack-root '<committed control pack>' \
     --author-inputs '<real control arm_readiness.t0.inputs directory>' \
     --custody-root '<new isolated control custody directory>' \
     --reviewed-resync-argv '<lead-approved JSON argv>' \
     --resync-timeout-s '<lead-approved seconds>'
   ```

   For example, the **proposed, awaiting review** JSON argv is
   `["/usr/bin/sudo","/usr/bin/sntp","-sS","time.apple.com"]`.
   The helper also accepts the identical vector with `-n` immediately after
   `sudo`, if that is the vector the lead reviews. There is no default command
   or default resync timeout; the explicit timeout must be 1–300 seconds.
   Never add a different clock-setting command.

2. Read the first prompt and type `OUTSIDE` only when no agent, armed window
   or capture is running. The helper snapshots inputs and takes its before
   CLOCK_REALTIME/CLOCK_MONOTONIC_RAW stamps. It then prints a complete shell
   block for the second terminal. Copy that entire block there, unchanged.
   The first privileged command is exactly:

   ```zsh
   /usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on
   ```

   The surrounding printed commands record machine start/end stamps, separate
   stdout and stderr, and the actual shell return code. Type `DONE` in the
   first terminal only after the block finishes. Each setter has a 30-second
   admission deadline. If a command hangs past its printed deadline, interrupt
   it in the second terminal and preserve its failed transcript; do not rerun.
   These deadlines are checked from stamps; the helper cannot interrupt a
   privileged command it did not launch.

3. The helper prints the reviewed forced-resync block. Copy that entire block
   to the second terminal once, then type `DONE` in the first terminal. Enter
   a sudo password there if the approved vector requires it. The helper never
   calls sudo. It samples the after anchor and computes its absolute movement.

4. Let the helper continue. If movement exceeds 5,000,000 nanoseconds, it runs
   the real author once on the preserved input sequence. Success requires exit
   2, status `REFUSE`, exactly
   `evidence_author_t0_clock_attestation_underivable`, and the specific detail
   `R0-to-author RAW anchor delta exceeds 5000000 ns`. Neither the source nor
   evidence publication namespace may exist. A different clock failure with
   the same reason code is insufficient.

5. On every attempted ON path, including a failed control, the helper prints
   the OFF cleanup block. Run the entire block in the second terminal, then
   type `DONE` in the first:

   ```zsh
   /usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off
   ```

   The helper serializes Ed's retained result through the existing OFF-receipt
   producer using an injected, non-executing runner, then reopens it with
   `joulewise.network_time_off.read_receipt`. Exit 0 plus either normalized
   `setUsingNetworkTime: Off` or `Network Time is already off` is admitted.
   If the helper is interrupted or OFF cannot be confirmed, run this same OFF
   command manually, retain its output, and hand the failed custody to the
   lead. Do not enter the block without an authenticated OFF receipt.

## Success, failure and evidence hand-back

Success is helper exit 0 with `status=DISCHARGED` and a path to
`positive-control.json`. This establishes the physical-control component;
the lead still authenticates lineage and combines it with the software
boundary controls for `evaluate_g10`. It is not rehearsal PASS or ARM authority.

If movement is at or below five milliseconds, the author is not invoked. The
helper completes OFF cleanup, records `NOT-DISCHARGED`, emits no positive
record and exits 2. Stop and return the custody path to the lead. The lead
decides the next step; do not repeatedly resynchronize, adjust the time by
another method, or retry inside a window. Treat every other nonzero exit the
same way. Keep the complete directory, including failed attempts, immutable.

The output map, relative to the new control custody directory, is:

| Output | Contents / consumer |
|---|---|
| `before.json`, `after.json`, `anchor-movement.json` | Machine REALTIME/RAW/skew, ordinary monotonic time, boot, absolute anchor movement. |
| `author-custody/<pack-name>/arm_readiness.t0.inputs/**` | Exact copies of the real author input bytes; original absolute references remain unchanged. |
| `author-input-lineage.json` | Source/pack paths, R0 anchor, boot and real author code SHA-256s. |
| `commands/{on,resync,off}/**`, `commands/{on,resync,off}.json` | Raw separated streams, actual return codes, exact argv and machine start/end stamps. |
| `author.stdout.json`, `author.stderr.txt`, `author-execution.json` | Real author's retained response, raw stderr, argv/exit/stamps and namespace absence census. |
| `network_time_off.json` | Existing `joulewise.network_time_off.v1` receipt, admitted by the shared reader; control identity only. |
| `positive-control.json` | Exact `joulewise.t0_unattended_anchor_positive_control.v1`, only after refusal and OFF admission. |
| `outcome.json`, `custody-manifest.json` | Structural discharge/failure and SHA-256 map of every supporting byte. No measurement metrics. |

The positive record has exactly eight keys: `schema_version`,
`performed_by="Ed"`, `outside_t0_sequence=true`,
`network_time_reenabled=true`, `forced_resync=true`, `anchor_before_ns`,
`anchor_after_ns`, `author_refusal_reason_code`. The two anchor values are
REALTIME minus RAW in nanoseconds. Supporting data belongs beside the record,
never in extra record keys. Lane B maps these authenticated bytes into the
rehearsal manifest's `positive_control` locator; its software falsifier record
remains separate. The lead fills the registration's record path/digest and
evidence map from the emitted files.

Leave network time OFF after this procedure. Every subsequent occurrence
gets a **new** OFF receipt on its own boot and completes at least 600 seconds
of settling on both clocks before its first capture/author boundary. Never
reuse the control's OFF receipt as an occurrence receipt or restore time ON
after a window.
