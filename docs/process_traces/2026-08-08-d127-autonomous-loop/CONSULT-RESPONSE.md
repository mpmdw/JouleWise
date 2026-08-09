# D-127 autonomous window loop — design consult response of record (2026-08-08)

Sol xhigh (fast tier), read-only, via scripts/codex-bridge. Charge:
D-127/D-128 (decision log) — the scoped time-toggle + verified
relaunch harness for multi-day unattended window loops.

**MAGISTRATE ASSESSMENT (Fable, 2026-08-08): SOUND ON FULL READ;
formal adoption DEFERRED to the build session per Ed's checkpoint
directive (no new launches after stream wrap).** Load-bearing
amendments over the magistrate's framing, endorsed on read: BOTH
clock toggles live in the detached supervisor (never either Claude
session); the existing chain shell IS the supervisor (no polling
watcher); kernel wake.lock over claim files; launchd interval derived
from the frozen pack (14400s vs 225-min hard stop), watchdog-not-
periodic; two-stage liveness (SessionStart bootstrap-claim + first
tool-call agent-claim); three TOTAL launch attempts shared with the
fallback; PARKED_AUTH/quota park immediately, no churn; supervisor
never advances head pins (desk-only per the recovery ruling); no
third same-signature re-arm unattended. Two hard conditions bind
production activation: residual §5A physical/agent-route boundaries
are NOT closed by D-127 (charger/cable attestation, alternate launch
routes), and recovery must land first (D-127 consumes its public CLI
surfaces). Build sequence §5 (11 steps; 1-8 unprivileged/dry-run) is
the plan of record for the build session.

---

The D-127 loop is viable with two hard conditions:

1. The detached supervisor—not either Claude session—must own both network-time toggles, capture lifecycle, custody close, and wake-up.
2. D-127 does not by itself close every alternate agent-launch route or automate the physical charger/cable attestation. Production activation must remain blocked until those residual §5A boundaries are explicitly satisfied.

This design follows [D-127](/Users/edr/code/JouleWise/docs/decision_log.md:7992), its D-128 ratification and morning-surface requirement, the [recovery exit ruling](/Users/edr/code/JouleWise/docs/process_traces/2026-08-08-recovery-exits-escalation/CONSULT-RESPONSE.md:1), and [D-125 Phase C](/Users/edr/code/JouleWise/docs/strategy/2026-08-08-40h-plan.md:87).

## 1. Sudoers slice

Invoking account: `edr`, uid 501. The supervisor runs as `edr`; it remains unprivileged except when invoking these two commands through `sudo -n`.

Exact file bytes:

```sudoers
# JouleWise D-127: fixed network-time toggle capability for operator edr.
Cmnd_Alias JOULEWISE_NETWORK_TIME = /usr/sbin/systemsetup -setusingnetworktime off, /usr/sbin/systemsetup -setusingnetworktime on
Defaults!JOULEWISE_NETWORK_TIME !requiretty
edr ALL=(root) NOPASSWD: JOULEWISE_NETWORK_TIME
```

SHA-256, including final newline:

```text
7dfe980be89a7912d69c6e72b5582649fc4c50db88bf709bcfbb4a1c34e4406d
```

Properties:

- Exact Apple binary `/usr/sbin/systemsetup`; exact, case-sensitive argv.
- No wildcard, regex, shell, environment-setting tag, or other `systemsetup` operation.
- `!requiretty` is command-scoped. Local sudo 1.9.17p2 defaults `requiretty` off, but the explicit override protects launchd/headless use.
- No command digest in sudoers: an OS update changing Apple’s binary must block the next arm in harness preflight, not unexpectedly disable the safety-critical restore operation.
- The rule is account-wide: any process running as `edr` can invoke these two commands. Sudoers cannot securely constrain them to one caller executable. This is a recorded residual risk.

Why no privileged helper: a helper adds root-executed parsing, interpreter, installation, dispatch, and update surfaces. Directly authorizing two argv vectors against a root-owned Apple binary is the smaller TCB.

### Installer release artifacts Ed inspects

The release should contain exactly:

1. `configs/sudoers/joulewise-network-time` — the four bytes-pinned lines above.
2. `docs/process_traces/<D127-release>/INSTALL-MANIFEST.json` — reviewed commit, source/target, SHA-256, operator `edr`, uid 501, target owner `root:wheel`, mode `0440`, `/usr/sbin/systemsetup` identity, and installer command digest.
3. `docs/process_traces/<D127-release>/INSTALL.txt` — the exact command below and expected terminal output.
4. `docs/process_traces/<D127-release>/D118-GATE-LEDGER.md` — complete D-118 items 1–11 plus D-121 terminal item 12, final test receipt, and final-head SHA.

No repository Python or shell script should execute as root. Ed runs:

```sh
/usr/bin/sudo -k
/usr/bin/sudo /usr/bin/env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin \
  /bin/sh -ceu '
src=$1
expected=$2
target=/etc/sudoers.d/joulewise-network-time
stage=$(/usr/bin/mktemp -d /private/tmp/joulewise-network-time.XXXXXX)
tmp_target=
cleanup() {
  if [ -n "$tmp_target" ] && [ -e "$tmp_target" ]; then
    /bin/rm -f -- "$tmp_target"
  fi
  if [ -f "$stage/rule" ]; then
    /bin/rm -f -- "$stage/rule"
  fi
  if [ -d "$stage" ]; then
    /bin/rmdir -- "$stage"
  fi
}
trap cleanup EXIT HUP INT TERM

/usr/bin/install -o root -g wheel -m 0600 "$src" "$stage/rule"
observed=$(/usr/bin/shasum -a 256 "$stage/rule")
observed=${observed%% *}
[ "$observed" = "$expected" ] || {
  echo "reviewed-artifact digest mismatch" >&2
  exit 1
}

/usr/sbin/visudo -cf "$stage/rule"
/usr/sbin/visudo -c

if [ -e "$target" ] || [ -L "$target" ]; then
  echo "refusing existing target: $target" >&2
  exit 1
fi

tmp_target=$(/usr/bin/mktemp /etc/sudoers.d/.joulewise-network-time.XXXXXX)
/usr/bin/install -o root -g wheel -m 0440 "$stage/rule" "$tmp_target"
/bin/ln "$tmp_target" "$target"
/bin/rm -f -- "$tmp_target"
tmp_target=

/usr/sbin/visudo -c
/usr/bin/stat -f "%Su %Sg %Sp %N" "$target"
' sh \
  /Users/edr/code/JouleWise/configs/sudoers/joulewise-network-time \
  7dfe980be89a7912d69c6e72b5582649fc4c50db88bf709bcfbb4a1c34e4406d
```

This gives D-115 fresh authorization, root-owned one-copy staging, literal digest authentication, empty-environment interpreter isolation, syntax validation, and non-overwriting atomic target creation.

### Abuse and evidence

The capability cannot set an arbitrary time, timezone, server, startup disk, or other `systemsetup` option. It can still:

- Leave network time off indefinitely.
- Re-enable it during a capture and induce a slew.
- Toggle repeatedly, impair wall-clock ordering, TLS/auth, timestamps, or scheduled jobs.
- Be invoked by another compromised `edr` process outside the harness.

The existing evidence chain detects active wall-versus-monotonic slews, discrete discontinuities that cross governed stamps, calibration drift, custody/hash changes, and ledger-order conflicts. It does **not** prove absolute time correctness while NTP is off: as [§5A already states](/Users/edr/code/JouleWise/docs/phase_2/window_runbook.md:267), the wall/monotonic check then passes largely by construction.

The supervisor must additionally record:

- Cycle/contract SHA, boot identity, supervisor PID/start/executable, uid.
- Exact sudo argv, start/end monotonic timestamps, advisory UTC timestamps, exit status, stdout/stderr hashes.
- SNTP offset immediately before disable; refuse if unavailable or outside the frozen limit.
- A `(wall − continuous-clock)` anchor at disable and before restore, yielding free-run drift.
- SNTP offset before restore and after convergence.
- `/usr/sbin/systemsetup` hash/stat identity.
- The expected logical state (`off` or `on`) and every failed attempt.

D-127 deliberately authorizes no privileged `-getusingnetworktime`. Therefore command success plus output is the postcondition; an independent privileged read would require a third sudoers command and a new ruling.

## 2. Cycle state machine

Both toggles live in the detached supervisor. The agent never turns time off and is not responsible for restoration.

| State | Owner | Required transition |
|---|---|---|
| `DESK_ACTIVE` | Claude | Harvest prior cycle, verify/mint, judge, freeze next pack. |
| `HANDOFF_FROZEN` | Claude | Write immutable contract; supervisor preflight passes. |
| `HANDOFF_PENDING` | Supervisor | Arm delayed launchd fallback; register initiating agent; request its exit. |
| `ZERO_AGENT_PROVED` | Supervisor | Exact initiating identity absent; quiet-guard registry and independent census zero; named apps/routes fenced. |
| `CLOCK_OFF` | Supervisor | SNTP precheck passes; exact `sudo -n ... off`; receipt durable. |
| `QUIET_SETTLING` | Supervisor | Governed 180-second admin settle plus untouched daemon-idle interval. |
| `ARM_READY` | Supervisor/writer | Recovery CLI pre-reserve readiness passes; reservation created. Calibration writer repeats enforcing pre-slot readiness while holding its writer lease. |
| `CAPTURING` | Existing chain shell | Capture under quiet lease. Resident shell blocks; no polling, network, Git, model, or periodic launchd process. |
| `CUSTODY_CLOSING` | Supervisor | Finalize post slot or governed abort; preserve and verify a raw backup. |
| `CLOCK_RESTORED` | Supervisor | Exact `sudo -n ... on`; drift/convergence receipt; quiet lease released. |
| `WAKE_PENDING` | Supervisor | Invoke shared launch primitive with bounded attempts. |
| `AGENT_CLAIMED` | Fresh Claude | First governed action claims the cycle and begins the frozen `next_action_id`. |
| `PARKED` | Neither | Durable cause and required human/lead decision; no re-arm. |

Do not create a new polling Python watcher. Extend the existing detached chain shell so it is the supervisor, with helper CLIs invoked only at phase boundaries. During capture it blocks in the same process shape as the proven foreground chain. Otherwise the old watcher-negligibility problem returns.

### Frozen files

Runtime authority belongs outside Git, for example:

```text
~/Library/Application Support/JouleWise/window-loop/v1/cycles/<cycle-id>/
├── cycle-contract.json
├── cycle-state.json
├── events.jsonl
├── supervisor-receipt.json
├── bootstrap-claim.json
├── agent-claim.json
├── heartbeat.json
└── morning.md
```

`cycle-contract.json` is immutable canonical JSON and must contain:

- Cycle/predecessor IDs and contract SHA.
- Exact repository commit, clean-worktree predicate, pack/plan/config hashes.
- Window, evidence-root, ledger session, slot and attempt IDs.
- Exact command vectors—never shell strings—for capture, verdict, backup, toggle, and wake.
- Runs/custody/backup roots and minimum free-byte predicates.
- Expected runtime, 225-minute current hard stop, and fallback interval.
- Claude realpath, version/hash, settings/prompt hashes, preallocated session ID.
- Autonomous decision permissions, refusal counters, and exact `next_action_id`.
- Required machine/app/charger attestations and their expiry conditions.

`cycle-state.json` is crash-atomic and epoch-increasing. It records current phase, dual timestamps, boot/host identity, exact supervisor/capture/Claude process identities, quiet and calibration lease states, toggle receipts, custody results, launch attempts, refusal signature, and next action. `events.jsonl` is hash-chained.

`RUN_STATE.md` is not runtime authority. Once awake, Claude promotes `morning.md` into a one-page dated run report and makes RUN_STATE point to it.

### §5/§5A items

Automatable:

- Exact packs/hashes, clean head, fresh roots, disk/backup capacity.
- Existing powermetrics capability.
- SNTP correctness and both toggles.
- AC/wattage/power policy, thermal/display/screensaver probes.
- Time Machine/indexing/update/cloud-activity detection: refuse while active; do not autonomously disable system services.
- Ten-minute untouched idle and 180-second settles.
- Agent/process census.
- Calibration readiness, reservation, slot status, resume-finalize/abort.
- Backup and hash verification.

Must be quit or fenced:

- T3 Code Alpha (`com.t3tools.t3code`).
- Claude desktop and every Claude CLI session.
- ChatGPT/Codex desktop (`com.openai.codex`) and Codex CLIs.
- Browser-automation sessions and their helper descendants.
- Scheduled/cloud/remote routes capable of materializing a local agent.
- The D-127 launchd fallback until its safe not-before boundary.

Still physical or ruling-bound:

- Approved cable, charger and port identity beyond machine-readable wattage.
- “Nobody nearby touches the Mac.”
- Revalidation following a move, cable/power disturbance, reboot, OS/tool update, or unreadable physical seal.

D-127 did not revive `SEC5A-REMOTE-01`; these cannot be silently replaced with an agent attestation.

## 3. Relaunch and watchdog

Current observed Claude is `/Users/edr/.local/bin/claude`, version `2.1.225`. Each cycle freezes its realpath, hash and version rather than treating that observation as permanent.

Preflight:

1. Binary identity and `claude --version`.
2. `claude auth status --json`; require logged-in and an accepted auth method.
3. Before quiet handoff, a minimal no-tools/no-persistence online canary. Local auth status alone cannot prove the server accepts the credential or quota remains.
4. Disk predicates, exact frozen head, quiet-guard idle state, no recovery-required state.
5. Recovery `readiness --phase pre-reserve` and synthetic arm rehearsal already passed.
6. No live calibration writer, campaign lock, incompatible session, or stale launchd job.

Launch uses a preallocated UUID through `--session-id`, normal permission mode—never bypass—and stream JSON for classified failure evidence.

Liveness is two-stage:

- A frozen `SessionStart` hook writes `bootstrap-claim.json`, proving the correct CLI/session/settings reached bootstrap.
- The prompt’s first model tool call runs the claim CLI and atomically writes `agent-claim.json`. The launcher does not stand down on process existence or hook execution alone.

`agent-claim.json` contains:

```text
schema
cycle_id
contract_sha256
launch_attempt_id
claude_session_id
next_action_id
state_epoch_observed
boot_id
continuous_time_ns
wall_utc_advisory
clock_restore_receipt_sha256
pid / ppid / executable / argv_digest / start_time
claude_version
```

Continuous time and boot identity are authoritative; wall UTC is advisory until the restore-convergence receipt exists. `heartbeat.json` then carries session/cycle IDs, state epoch, current action, monotonic timestamp, last durable artifact, and whether a successor handoff exists.

Retries: three total attempts shared by primary and launchd—initial, then 30-second and 120-second backoffs, each with a 120-second claim deadline. The fallback does not reset the counter or gain a fourth try. Auth-expired, quota-exhausted, unobservable live-process, and integrity failures park immediately.

### Launchd fallback

For current alpha/beta/gamma packs, arm a per-cycle LaunchAgent with:

```text
StartInterval = 14400
```

That is four hours from handoff versus the maximum frozen 194.4-minute beta budget. The cycle contract declares a 225-minute valid-capture hard stop, leaving launchd fifteen minutes beyond the point where an in-flight capture is already non-claim-bearing. Future intervals are derived from the frozen pack, never a standing periodic constant.

The job does not run periodically during a potentially valid capture. Once it starts, it stays alive as the independent watchdog until the cycle becomes terminal, preventing launchd from starting overlapping instances.

Primary supervisor and fallback use the same never-deleted `wake.lock`. The lock is held across spawn and claim verification; the supervisor continues holding it while the Claude child is live. Claim files supplement the kernel lock but never replace it.

### Failure dispositions

| Failure | Disposition |
|---|---|
| Supervisor dies before/during capture | Launchd waits until the safe boundary. If the exact chain remains after the hard stop, the night is lost; terminate only an exactly identified group, otherwise enter `recovery_required`. Restore/wake only after zero-process proof. |
| Claude auth expired | Do not churn retries. Record `PARKED_AUTH`, preserve custody, leave time on. Ed reauthenticates. |
| Quota exhausted mid-run | Preserve all repo/runtime state. Supervisor detects child exit; park rather than starting a second agent that may repeat side effects. Resume only after quota returns from the same cycle contract. |
| Capture exists when timer fires | No agent launch. Check quiet lease, calibration writer lease, exact capture identity and campaign lock. Before the hard stop, reschedule; after it, mark the window lost and run exact-identity recovery. |
| Two launchers race | One kernel lock winner. The loser checks exact live PID/start identity and current launch generation; it never trusts a claim file alone. |
| Restore command fails | Release the quiet lease after custody preservation, mark `closed_degraded`, attempt agent recovery, and block every later arm until an authenticated `on` receipt exists. |
| Post slot leaves `needs_pin_commit` | Preserve/backup, restore time and wake Claude. The supervisor must not auto-advance or commit the head pin; the recovery ruling makes that desk-only reviewed work. |

## 4. Judgment boundaries

| Unattended session may do | Must park/escalate |
|---|---|
| Run frozen packs and deterministic governed tools. | Change estimand, membership, retry cap, cadence, or process mechanism. |
| Harvest, validate, back up, extract and mint through existing contracts. | Waive/refashion an admission, refusal, floor or custody rule. |
| Execute registered `repair`, `resume-finalize`, and `abort-session` exits. | Use an uncommitted-pin override, edit ledger bytes, or improvise an unregistered exit. |
| Re-arm after one weather/process refusal when a named cause was removed, the governed exit completed, and plan semantics remain frozen. | Blindly re-run for a better outcome or after an unidentified cause. |
| Draft conservative claim language under D-119. | Publish/release claims, make irreversible changes, or decide Ed-owned scope/funding/spec questions. |
| Build/fix/merge only through the full existing gate. | Change or skip D-118/D-121. |

After a second same-signature window refusal: park and convene the existing escalation path. No third unattended re-arm. Because exact counter semantics are themselves process policy, the implementation contract should explicitly bind this mapping to the magistrate’s ratification rather than silently inventing a cadence.

Ed’s morning artifact is one page containing what ran, exact hashes, what passed/refused and why, clock/toggle receipts, backup/verdict/mint status, launch health, next night’s exact window, and parked questions. Normal path: dated run report linked from RUN_STATE. Degraded no-agent path: the host-local `window-loop/.../morning.md`; D-114 already accepted that a total relaunch failure may lack remote notification.

## 5. Build and test sequence

1. Land recovery first. D-127 consumes the branch’s public `readiness`, `session-status`, `resume-finalize`, `abort-session`, `explain`, and terminal-pin surfaces; it must not duplicate their logic.
2. Freeze the autonomous-loop contract, schemas, refusal vocabulary, hard deadlines, and threat model.
3. Implement the pure state engine and crash-atomic file contracts using temporary roots.
4. Implement toggle command generation with a fake `systemsetup`; test exact argv, refusal of all extra/missing/case-variant arguments, restore-on-every-exit behavior, and sudoers digest/`visudo`.
5. Implement supervisor and full crash matrix: every transition, capture timeout, backup failure, toggle failure, reboot/boot mismatch, retained quiet lease, and recovery CLI refusal.
6. Implement fake-Claude and fake-launchd tests: no claim, stale claim, late claim, auth/quota exits, supervisor death, two-launcher race, shared retry count, capture-at-timer.
7. Run an entirely unprivileged synthetic end-to-end rehearsal, including the enforcing pre-slot writer gate under its real writer lease.
8. Full D-118/D-121 gauntlet and canonical suite.
9. Ed-present installation using the command above.
10. Non-measurement live exercise: off → receipt → immediate on → convergence, then real Claude relaunch/claim and launchd fallback without a claim capture.
11. Only then admit one real quiet window.

Everything through step 8 is testable without the sudoers rule. Dry-run mode must never invoke `sudo`, real `systemsetup`, launch a model, mutate production quiet-guard state, or touch scientific custody.

Minimal implementation surface:

- One contract document.
- One deterministic `joulewise/window_loop.py` engine.
- One CLI/supervisor entry point.
- One literal sudoers file.
- One launchd plist template.
- State/crash-matrix, relaunch/race, and sudoers/installer tests.
- One D-118/D-121 gate ledger plus final integration receipt.

## What survives from shelved commits 2–4

Survives:

- Commit 1’s durable no-TTL quiet lease, exact process identity, `handoff_pending → quiet_held` only after agent disappearance, and `recovery_required`.
- Atomic check/spawn/claim for the D-127-owned Claude and launchd routes.
- Exact process-group supervision and custody-preserving failure behavior.
- Three-total-attempt discipline and durable degraded-close reporting.

Does not survive:

- T3 residency, app-adjacent characterization, T3 watcher/relaunch, README projection, unattended Git credentials, banner commits, or remote push.
- A polling resident watcher; use the existing chain shell as supervisor.
- Commit 4’s 5/15-second local-app retry schedule; network/auth launch failures need 30/120-second spacing.
- Any broad all-launcher interception claim unless D-114 is explicitly reopened.

## Explicit rejections

- I reject putting either toggle in an agent process.
- I reject RUN_STATE as the runtime state machine.
- I reject a broad privileged helper.
- I reject claim-file-only mutual exclusion.
- I reject a periodic launchd waker that can start during a valid capture.
- I reject treating wall/monotonic anchor success as independent evidence while NTP is off.
- I reject supervisor-driven terminal-pin Git commits; the recovery contract makes those reviewed desk work.
- I reject blind or third same-signature re-arms.
- I reject claiming D-127 closes every alternate agent launch route.
- I reject claiming full autonomous §5A completion without a fresh physical-state authority for charger/cable/port and nearby-human conditions.
- I reject adding `-getusingnetworktime` implicitly; that would be a third privileged command.
- I reject letting launchd retries reset the primary retry budget.

Checks performed: repository clean at `main`/`origin/main`; D-114/115/118/125/127/128, runbook §§5/6/10, recovery branch CLI/diff, and shelved packet inspected; proposed sudoers parsed `OK` by `visudo 1.9.17p2`; exact rule SHA-256 reproduced; installer body passed `sh -n`; Claude 2.1.225 binary/auth/session surfaces inspected; no files changed and no live/quiet measurement run.