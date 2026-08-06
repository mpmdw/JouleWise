# Quiet Guard Commit-1 Contract

Status: implemented but deliberately inactive. This contract covers only
QUIET-GUARD-01 Commit 1, the root-owned lease engine and inactive installer.
It does not authorize a quiet window, modify a launcher, drain or relaunch T3,
run a chain, characterize a watcher, or project status into Git.

> **BINDING DECISION — D-115 (ADJUDICATED):** Quiet-guard Q2 setup
> authority is a fixed installation capability, not general root authority.
> Its fresh-authorization, authenticated-content, and interpreter-isolation
> conditions are mandatory for this installer and helper.

## Safety boundary

Production guard state is `/Library/Application Support/JouleWise/quiet-guard/`.
Every engine path is parameterized so tests use a temporary fake state root,
but fixture initialization is accepted only beneath the process temp directory
with a `joulewise-quiet-guard-test-` top-level sandbox name. Non-test arbitrary
roots and the production root in test mode are canonical refusals.
The runtime never writes `.codex-bridge/**`, a run bundle, a manifest,
`RUN_STATE.md`, `TASK_QUEUE.md`, a decision log, or any scientific/audit
artifact. Guard-local `config.json`, `state.json`, and `control.lock` are the
only Commit-1 mutable runtime files.

The installation is non-armable:

- `live_promotion` is `false` at setup and no Commit-1 command can change it.
- No production method can create a lease-bearing transition. Transition
  execution is fixture-only and rejects the production root.
- `quiet_guard arm` refuses before invoking sudo with canonical cause
  `t3_char_pair_verdict_missing`. Commit 1 has no command or installation path
  that can add a passing reference, so the CLI has no second refusal branch.
- The pinned future per-arm capability probe is represented exactly as
  `/usr/bin/sudo -n /usr/bin/powermetrics -n 1 -i 100`; this commit records and
  validates that argv but never executes it.
- No Commit-1 command launches, quits, signals, or measures anything. No test
  invokes sudo or reads the real process table.

Production promotion will remain conjunctively gated on a lead-installed
passing `T3-CHAR-PAIR-01` verdict reference, the watcher-negligibility gate,
Ed-confirmed launch-perimeter coverage, and the real non-measurement T3
app-death exercise. Fixture evidence cannot satisfy any live gate.

## State machine

The state names are:

- `idle`: no quiet lease is held or pending.
- `handoff_pending`: an initiating T3 session requested handoff. New agent
  launch routes must be blocked in the later perimeter commit, but the quiet
  lease is not held.
- `quiet_held`: reserved for the future detached watcher after the initiating
  session identity is absent, the durable registry is empty, and an
  independent census is zero.
- `recovery_required`: custody is retained and ordinary agent-launch routes
  must refuse until the non-agent recovery path proves zero processes.

The transition table is the sole legal-edge authority:

| From | To | Actor | Lease action |
|---|---|---|---|
| `idle` | `handoff_pending` | `initiating_session` | create |
| `handoff_pending` | `quiet_held` | `watcher` | retain |
| `handoff_pending` | `recovery_required` | `watcher` | retain |
| `quiet_held` | `recovery_required` | `watcher` | retain |
| `idle` | `recovery_required` | `engine` | retain |
| `handoff_pending` | `recovery_required` | `engine` | retain |
| `quiet_held` | `recovery_required` | `engine` | retain |
| `quiet_held` | `idle` | `watcher` | clear |
| `recovery_required` | `idle` | `recovery` | clear |

Every other state/actor combination refuses as `invalid_transition`. In
particular, an initiating session may enter only `handoff_pending`; it can
never enter `quiet_held`. The `recovery_required` → `idle` table edge is not a
general transition capability: it is reachable only through `recover()` after
the acknowledgment and zero-proof checks below.

There is no timeout, expiry field, TTL, or clock-based release. A lease stays
pending/held/recovery-required until an evidenced legal transition clears it.
Drain timing and signal behavior belong to the later T3-family commit.

## Durable formats and bindings

All JSON is UTF-8, canonicalized with sorted keys and compact separators, and
newline terminated. Validators require exact field sets; unexpected fields
fail closed instead of becoming ambient capabilities.

`config.json` uses `joulewise.quiet_guard.config/v1` and contains:

```text
schema, host_id, live_promotion, t3_char_pair_verdict, powermetrics_probe
```

The optional verdict reference, when a later lead-owned installation path
exists, must use `joulewise.t3_char_pair_verdict_ref/v1`, task id
`T3-CHAR-PAIR-01`, verdict `passed`, and a `sha256:<64 lowercase hex>` digest.

`state.json` uses `joulewise.quiet_guard.state/v1` and contains:

```text
schema, host_id, boot_id, epoch, state, registry, lease, events
```

It is one crash-atomic document: the current state, registry, lease, and event
history cannot be committed at different epochs. `epoch` is a nonnegative,
strictly increasing integer. The event array length equals the epoch, event
epochs are exactly `1..epoch`, the first event begins at `idle`, every event
begins at the prior event's target, and the final event target equals the
current state.

The embedded registry uses `joulewise.quiet_guard.registry/v1`:

```text
schema, host_id, boot_id, epoch, entries
```

Every PID is unique. Each entry is a complete exact process identity as
specified below. The embedded lease uses
`joulewise.quiet_guard.lease/v1`:

```text
schema, host_id, boot_id, epoch, lease_id, owner, created_epoch
```

`lease_id` is a UUID, `owner` is an exact process identity, and
`created_epoch <= epoch`. `handoff_pending` and `quiet_held` require a lease.
No lease schema admits an expiry or TTL. The semantic invariant for `idle` is
strict: its registry is empty and its lease is null; persisted bytes that
violate either half refuse canonically as `registry_invalid` or `lease_invalid`.

Each event uses `joulewise.quiet_guard.event/v1`:

```text
schema, host_id, boot_id, epoch, from_state, to_state, actor, cause,
lease_id, evidence
```

The transition triple must exist in the table above. Recovery evidence keeps
the acknowledgment, acknowledger, exact abandoned identities, their absent or
PID-reused classifications, and the independent census count.

Config is host-bound. State, registry, lease, and every event are host- and
boot-bound. A schema, host, boot, event-sequence, registry epoch, or lease epoch
mismatch refuses every normal path. `status` strictly validates persisted
bytes against their original bindings and reports a current-binding mismatch
as recoverable. Only `recover` with the exact acknowledgment, a nonempty
operator, and zero-process proofs may re-bind. It replaces stale state with a
fresh continuous `idle -> recovery_required -> idle` history on the current
host/boot, records the prior state digest and abandoned identities, rewrites
inactive config, and never creates or retains a lease.

## Locking and atomic durability

Every mutation takes an exclusive nonblocking `flock` on `control.lock`.
Contention returns canonical cause `lock_unavailable`; callers do not wait and
then reinterpret stale state.

A document update is written to a unique mode-0600 temporary file in the
destination directory, flushed, `fsync`ed, atomically installed with
`os.replace`, and followed by a directory `fsync`. A failure before replace
preserves the prior document and removes the temporary file. A directory
`fsync` failure is propagated: the caller is not told the update is durable.
Inactive initialization is retry-idempotent across its two documents: if an
interruption leaves one valid expected document, retry validates it and writes
the missing peer; if both expected documents landed, retry returns the same
inactive state without rewriting either. Every successful invocation, including
that no-rewrite retry, re-fsyncs the state directory and its parent; either
failure is propagated. Unexpected existing content refuses.

## Exact process identity and census

`joulewise.quiet_guard.process_identity/v1` contains:

```text
schema, pid, start_time, executable, argv_digest, ancestry
```

`argv_digest` is SHA-256 over a domain-separated, length-prefixed true argument
vector. On Darwin, start time is the microsecond-resolution
`kinfo_proc.kp_proc.p_starttime` returned by `KERN_PROC_PID`; executable and the
true argv vector come from `KERN_PROCARGS2`. Display-oriented `ps comm` and
`command` values never define identity. `/bin/ps` supplies only parent linkage
and the PID list for census. Ancestry is ordered nearest-parent first; every
link contains its PID, start time, executable, and argv digest. Duplicate or
cyclic PIDs are invalid.

The production observer reads every kernel-backed row twice and, after walking
ancestry, re-reads the child and every collected link. A positively absent PID
is `ABSENT`; interface failure, malformed payload, failed parent linkage, or a
torn/changed ancestry observation is `UNOBSERVABLE`. Neither produces a partial
identity, and `UNOBSERVABLE` is never reinterpreted as absence. On non-Darwin
or when required sysctls are unavailable observation refuses. Census enumerates
independently and refuses if any listed PID is unobservable rather than
silently omitting it and reporting a false zero. The recovery caller passes
the exact registered identities as the protected set. A transient unobservable
unprotected PID restarts the complete PID snapshot once and may be dropped if
it is positively absent from the replacement snapshot. A protected PID that
was unobservable may never be smoothed into absence: it must become observable
on the bounded retry or the complete census refuses. A second unobservable
attempt also refuses, so protected observation failure never becomes absence.
Before action, callers compare the complete durable identity. Same PID with a
different start time, executable, argv digest, or ancestry is `pid_reused`,
never a match. Family discovery and the later T3 adapter must derive identities
from the exact bundle/session ancestry on every request; process-name patterns
and shared-helper exceptions are forbidden. An unlinked helper or
`cloudflared` is an unknown survivor that blocks promotion and is never killed.

## Stale recovery

Registry audit independently re-observes every exact identity. An absent
identity yields `stale_registry`; a changed identity yields
`pid_reuse_detected`; an unobservable identity yields
`process_observation_unavailable`. All three enter or retain
`recovery_required`; the lease is never released because a timeout elapsed.

`recovery_required` blocks all later agent-launch routes. The fixed root helper
exposes a non-agent `recover` command. It may inspect exact identities and
append only guard-local recovery evidence. Clearing requires all of:

1. the exact acknowledgment text
   `I acknowledge quiet-guard recovery and exact-identity abandonment`;
2. a nonempty Ed/lead operator identity;
3. every registered exact identity revalidates as absent or PID-reused, never
   as a match or unobservable; and
4. the independently observed family census is zero.

Only then may recovery record each exact abandoned identity, clear registry
and lease, increment the epoch, and return to `idle`. The privileged helper
performs its own full PID enumeration; it does not accept caller-supplied census
rows. Commit 1 selects exact registered identities and their descendants from
that enumeration. The later T3-family commit must broaden the family derivation
before live promotion can be enabled.

Watcher supervision loss in the later commit is not a safe completion signal:
the exact chain/process group must be terminated when identity remains
provable; otherwise the state stays `recovery_required` and retains custody.

## Canonical failures

Failures use `joulewise.quiet_guard.failure/v1` with fields `schema`, `cause`,
`signature`, and `detail`. The detail is diagnostic and does not define retry
identity. The canonical signature is the literal
`quiet_guard/<cause>/v1`. Commit 1 pins these causes:

```text
t3_char_pair_verdict_missing     live_promotion_disabled
schema_mismatch                  host_mismatch
boot_mismatch                    malformed_json
lock_unavailable                 invalid_transition
epoch_regression                 registry_invalid
lease_invalid                    identity_mismatch
stale_registry                   pid_reuse_detected
recovery_acknowledgment_missing  processes_remain
independent_census_nonzero       privileged_command_refused
process_observation_unavailable
```

Changing prose cannot reset a same-cause counter because consumers compare the
canonical cause/signature, not `detail`.

## Privilege model and installation

`scripts/setup_quiet_guard.sh` is the only interactive-sudo artifact and is
operator-run, never agent-run. It:

- invalidates cached sudo authorization with `/usr/bin/sudo -k` before a fresh
  interactive `/usr/bin/sudo -v` grant;
- pins literal SHA-256 digests for the reviewed engine, process observer, and
  privileged-helper artifacts in the installer; after root staging, one
  isolated validator compares every staged byte sequence to its pin before
  parsing or installation, and the tests bind each literal to repository bytes;
- validates the authenticated Python source without importing or writing bytecode;
- stages each mutable repository artifact once in a root-owned mode-0700
  directory, validates those exact staged bytes, and installs only from them;
- uses the authenticated staged engine for a write-free preflight of any
  existing config/state; an absent state root returns without creating the
  directory or `control.lock`, and a validation refusal never creates either;
- immediately before the first installed-artifact write, acquires
  `control.lock`, revalidates current host/boot and fresh or retryable initial
  history under that lock, and holds the same acquisition continuously across
  every package-module, helper, and sudoers replacement;
- creates root-owned mode-0700 state, install, and credential directories;
- installs root-owned package modules and the fixed helper;
- validates and installs identical staged sudoers bytes for only exact
  `status` and exact fixed-acknowledgment `recover` argv; and
- invokes the setup-only, non-sudoers `install-inactive` command, which writes
  `live_promotion=false` and no lease.

All runtime calls from the unprivileged client are `/usr/bin/sudo -n` only.
The helper's fixed shell/Python bootstrap executes `/usr/bin/python3 -I -S`, so
environment hooks, user-site, and site initialization are disabled before any
Python code runs. At its installed path it resolves `joulewise` only from the
root-owned private library and standard-library roots, never cwd, repository,
environment-selected, or site-package paths. Setup also verifies that
`/usr/local/libexec` is a real root-owned directory without group/other write
permission.
The helper allowlist is exactly `install-inactive`, `status`, and `recover`;
the setup-only command is not granted through sudoers. There is no arbitrary
root command, daemon, `systemsetup` authority, child exec, process signal, or
user-selected production state root.

Commit 1 also pins the privilege-drop primitive required before a later agent
child could execute. The root parent resolves the invoking account and groups,
then applies supplementary groups, primary gid, and uid; changes to the
validated cwd; clears the inherited environment; and installs a small
credential-free environment with fixed PATH and selected locale/terminal
fields. Loader hooks, Python paths, sudo variables, tokens, and credentials are
not inherited. No agent-exec command is exposed in this commit.
