# Window liveness and status-publication contract

This contract describes the measurement-owner census: a read-only inventory of
recorded processes that may still be collecting data. The **guard** is
`scripts/window_status.sh` calling `joulewise/measurement_liveness.py` before
writing `WINDOW_STATUS.md` or running Git. It refuses publication if any owner
is live or any observation is indeterminate (insufficient to decide safely).
It does not inspect command-line words or signal processes.

Authority: the [terminal review and lead rulings](../process_traces/2026-09-08-handoff-redo/99ap-magistrate-terminal-review-window-liveness.md)
settle the implementation at `ac092ccd`; [Opus R4](../process_traces/2026-09-08-handoff-redo/99s-ref-liveness-opus-contract-review.md)
assigns this operational documentation. The [design consult](../process_traces/2026-09-08-handoff-redo/94-consult-window-guard-astra-report.md)
owns the two independent chain and campaign rules.

## Discovery and campaign ownership

The **custody parent**, the directory containing individual night-plan custody
roots (directories retaining each night's records), is selected by
`JOULEWISE_CUSTODY_PARENT`, default `~/night-custody`. The campaign registry,
a directory of process-ownership records, is its direct child:

```text
<custody-parent>/active-campaigns/<pid>-<48 lowercase hex characters>.json
<custody-parent>/<plan-directory>/night/chain.started
<custody-parent>/<plan-directory>/night/chain.exited
```

The registry is a sibling of plan roots, outside their sealed evidence trees
and outside campaign run directories. A **PID** is the operating system's
process identifier. The filename suffix comes from 24 random bytes encoded as
48 hexadecimal characters; it is independent of the payload's nonce. Each
entry is a UTF-8 JSON object followed by a newline:

| Field | Writer value and meaning |
|---|---|
| `schema` | `joulewise.active_campaign.v1`, the record format identifier |
| `pid` | Positive integer PID of the campaign owner |
| `start_time` | Normalized `lstart` token, the process creation time defined below |
| `runs_root` | Resolved absolute path to the campaign's run directory |
| `nonce` | Nonempty random ownership value from this acquisition's `campaign.lock` |

An **acquisition** is a successful taking of `campaign.lock`, the existing
exclusive lock that prevents concurrent campaigns on one runs root.
`scripts/run_campaign.py` publishes an entry after acquiring that lock and
before dispatching any measurement child, on both ordinary execution and
`run_axi_spec_campaign` (the separate speculative-decoding campaign path). Dry runs and
maintenance/verdict-only lock acquisitions publish no entry. Publication
requires a usable start identity; failure prevents dispatch and returns a
refusal. The lock gains an additive `start_time` field; its ownership rules
and manual stale-lock repair remain unchanged.

`publish_campaign` creates the registry directory if needed, opens a unique
entry with exclusive creation (`xb`, which refuses an existing name), writes
the payload, flushes it, and calls `fsync` to flush file data to storage. A
write failure removes only the partial file still owned by that writer.
Both execution paths call `remove_campaign` in `finally`, Python's cleanup
block on normal return or exception, before releasing the campaign lock.
Removal checks the original device number, inode (filesystem object identity),
and exact payload bytes, then rechecks the inode before unlinking the file.
A replaced or edited entry is preserved. The entry itself governs liveness:
a missing referenced `campaign.lock` does not clear it.

The census lists each parent's direct children, inspecting every entry in
`active-campaigns` and `night/chain.started` under every other direct directory;
it does not require a valid plan file to discover a chain. Additional parents
come from `JOULEWISE_ADDITIONAL_CUSTODY_PARENTS`, a JSON array of nonempty path
strings, default `[]`. Paths expand `~`; identical Path values are deduplicated
and all selected parents are inspected. A missing custody parent is an empty
census, as is an absent registry. Permission errors, a parent that is not a
directory, malformed additional-parent JSON, and unreadable entries refuse.
Disappearance during inspection gets one reread/reconciliation; unresolved
errors refuse. The reader creates, removes, and rewrites nothing.

## Chain start and exit markers

A **chain** is the night driver's child session covering the whole sequence,
including settling and gaps between campaigns. `scripts/run_night.py` claims
`chain.started` with `O_CREAT | O_EXCL`, exclusive creation that enforces a
once-only launch. After launching the child in a new session, it first writes
and fsyncs a complete JSON record containing `pid`, `pgid`, and `epoch_s`, then
closes the descriptor. **PGID** means process-group identifier; this child is
the group leader, so `pgid == pid`. `epoch_s` is wall-clock seconds since the
Unix epoch. These are the child's identifiers, not the driver's.

Only after that complete record is readable does the driver probe identity.
It adds `start_time` (or null if unavailable), writes and fsyncs
`chain.started.tmp`, and uses `os.replace` to atomically replace
`chain.started`: readers see the old complete file or the new complete file.
An open chain marker without a valid `start_time` is indeterminate and refuses,
even if its PID is dead. Never derive a token from `epoch_s`. The pre-existing
interval between exclusive creation and the first write can still expose an
empty marker; the identity subprocess no longer widens it. There is no parent
directory fsync after replacement; power-loss durability is outside the
accepted guard threat model.

The **dead-man**, the separately scheduled night-driver recovery path, can read
`pgid` before the start token exists. For a usable recorded group it closes the
chain only when the group probe raises `ProcessLookupError` (no such process
group), not on permission failure. Its separate missing/unreadable-group
launch-failure path remains as implemented. The census does not use that group
probe: it uses the identity rules below.

A valid `chain.exited` closes the chain rule without probing the start PID.
It must be a JSON object with `exit_code` an integer or null, `epoch_s` a
number, and `monotonic_ns` an integer (a monotonic-clock nanosecond reading).
The driver writes it on completion or its recovery/launch-failure paths;
optional `reaped_by` and `launch_failed` fields explain recovery. The census
checks for an exit both before and after reading the start marker. An invalid
exit refuses. `courier.sent`, the handback-delivery marker, closes neither
measurement rule. Campaign entries remain independently evaluated even after
a valid chain exit. Preserve chain markers as night evidence; stale-registry
repair below never deletes them.

## Identity probe and worked example

An **identity** is PID plus the **start token**, the process creation timestamp
reported by real `/bin/ps` as `lstart`. A token has five fields: weekday, month,
day, `HH:MM:SS`, and year. Whitespace is collapsed to single spaces. The probe
uses `LC_ALL=C` and `LANG=C` to fix English date formatting, a two-second timeout,
and exactly these arguments for the requested PID:

```sh
LC_ALL=C LANG=C /bin/ps -p "$pid" -o lstart= -o stat=
```

`stat` is the operating system process-state field. The parser requires six
whitespace-separated fields: the five-field date and a state matching
`[A-Za-z+<Ns0-9-]+`. **LIVE** means a successfully observed non-zombie process;
a **zombie** is an exited process awaiting reaping, identified by state starting
`Z`, and is classified DEAD. For an absent PID, **DEAD** requires return code
(**rc**, the command's exit status) 1 and empty stdout (standard output) and stderr (diagnostic output) after
trimming whitespace. In particular, rc 0 plus empty output is **UNKNOWN**, never DEAD.
Other exit codes, stderr output, malformed text, timeout, execution failure,
invalid PID, or decoding failure are UNKNOWN and refuse publication. A valid
zombie response is the separate DEAD case, not an absent-PID response.

`JOULEWISE_IDENTITY_PROBE` can substitute a single executable pathname receiving
those same arguments for tests; it is not shell text. Production uses real
`/bin/ps`; keep that override unset. The removed command-text classifier and
its `JOULEWISE_STATUS_PS_COMMAND` setting grant no permission to publish.

For a real recorded example, the [2026-09-08 process-table capture](../process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/pass3-process-tree-keepalive.txt)
contains this PID, parent PID, and `lstart` prefix (command text omitted):

```text
83086 83075 Tue Sep  8 01:41:58 2026
```

The [matching ownership record](../process_traces/2026-09-02-hands-free-week/21-activation-784a764e/magistrate.lock.json)
records PID `83086` and token `Tue Sep 8 01:41:58 2026`. This is a historical
agent process, used only to demonstrate token normalization, not a measurement
registration or evidence that it is live now. For a measurement marker with
that PID/token pair, a fresh successful non-zombie observation with the same
token refuses publication. A different valid token means the PID was reused
and the recorded owner is stale; rc 1 with empty output also makes it stale.
UNKNOWN refuses. To obtain a fresh real PID/token line in an operator shell,
run `LC_ALL=C LANG=C /bin/ps -p "$$" -o pid= -o lstart= -o stat=`; `$$` selects
that shell. Do not feed the extra PID column to the production parser.

## Stale entries and operator repair

A **stale registry entry** is a structurally valid registration whose recorded
owner is DEAD, or whose PID is now LIVE with a different valid start token.
It produces WARN and does not itself block publication. Age alone never makes
an entry stale. For campaign entries, a positively DEAD PID can warn before
checking `start_time`; a present PID without a comparable token is indeterminate.
The stricter chain rule always requires a start token before probing.

There is no SIGTERM handler in `run_campaign.py`: SIGTERM is the operating
system termination signal and can end the process without its Python cleanup;
SIGKILL forcibly ends it and cannot be handled. Both can leave a registry entry
and a campaign lock. The design deliberately relies on observable ownership
and explicit operator repair instead of adding signal-handling or automatic
lock-reclamation semantics to the acquisition lifecycle. Stale entries remain
until repaired; the census never deletes them. A dead owner can leave living
children, so a stale warning is not proof that all collection has stopped.

The **operator** (Ed or the lead operating the window) owns repair, between
windows after stopping launches and independently confirming no surviving
measurement children. For one exact stale registry entry, set `ENTRY` to its
absolute path and run this command from the updated checkout. It refuses live,
indeterminate, malformed, and unexpected-path records, then uses the existing
inode-and-byte ownership check to remove only the inspected entry:

```sh
ENTRY="${ENTRY:?Set ENTRY to one exact absolute active-campaigns entry}" \
env -u JOULEWISE_IDENTITY_PROBE PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import os
from pathlib import Path
from joulewise.measurement_liveness import (
    Census, RegistryEntry, _inspect_campaign, custody_parent,
    observe_identity, remove_campaign,
)
path = Path(os.environ["ENTRY"])
if not path.is_absolute() or path.parent != custody_parent() / "active-campaigns":
    raise SystemExit("REFUSE: select an entry under this custody parent's registry")
with path.open("rb") as handle:
    st = os.fstat(handle.fileno())
    entry = RegistryEntry(path, st.st_dev, st.st_ino, handle.read())
result = Census()
_inspect_campaign(path, result, observe_identity)
if result.refusals or len(result.warnings) != 1:
    raise SystemExit("REFUSE: entry is not positively stale")
print(result.warnings[0])
remove_campaign(entry)
if path.exists():
    raise SystemExit("REFUSE: entry changed; preserve and reinspect")
print("Removed the inspected stale registry entry")
PY
```

For an additional custody parent, set `JOULEWISE_CUSTODY_PARENT` to that parent
for repair. This command does not repair `campaign.lock`. A leftover lock still
refuses a subsequent acquisition and needs the separately documented operator
workflow (for example, `quarantine_stale_lock` in the
[G2 runsheet](../process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md)).
Do not delete an unknown entry to obtain permission to publish; preserve it
and resolve the missing identity with the lead.

## Guard publication decision table

Each applicable chain and campaign contributes independently. Any refusal wins
over all warnings and clear observations. The helper prints `WARN:` and
`REFUSING:` diagnostics to stderr and exits 0 only with no refusals. The shell
exits 1 on a failed helper, before status-file or Git mutation.

| Observation | Guard decision |
|---|---|
| Open chain with matching live PID/token | REFUSE |
| Registered campaign with matching live PID/token, even with no lock | REFUSE |
| Valid chain exit | Clear chain rule without probe; still inspect campaigns |
| Valid open-chain identity or campaign record with DEAD owner | WARN; permit if nothing else refuses |
| Live PID with a different valid start token | WARN reused PID; permit if nothing else refuses |
| Open chain missing/invalid start token, including null | REFUSE indeterminate, even for dead PID |
| Malformed/unreadable marker, invalid exit, UNKNOWN probe, or unresolved read error | REFUSE indeterminate |
| No start marker, missing registry, or missing custody parent | Empty contribution; permit if nothing else refuses |
| Invalid additional-parent configuration or unreadable/non-directory parent | REFUSE indeterminate |
| Any refusal plus commit-freeze sentinel | REFUSE before even a local status write |
| Clear census plus commit-freeze sentinel | Write status locally, exit 0, no Git |
| Clear census without commit-freeze sentinel | Write status, stage and commit changes, then attempt push |

The **commit-freeze sentinel** is a file whose presence suppresses Git:
`JOULEWISE_COMMIT_FREEZE_SENTINEL`, default
`/Users/edr/JouleWise-window-custody/COMMIT_FREEZE_OPEN`. With no staged change,
the shell exits 0 without committing; a failed push warns and leaves the local
commit, also exiting 0. `JOULEWISE_STATUS_REPO` selects only the status/Git
checkout; the helper comes from the invoked script's checkout and custody
selection remains independent.

This is a snapshot guard, not mutual exclusion (a lock preventing launch and
publication from overlapping). Use updated measurement and publication
checkouts sharing the same custody-parent settings, driver-managed chains,
and sequential launch/publication. Hand-run chains are covered only while a
registered campaign runs; their settling and inter-campaign gaps, direct
collectors, old uninstrumented checkouts, and surviving children of dead owners
can escape this inventory. Start tokens have one-second precision. A clear
snapshot does not authorize quiet-machine collection during an agent session
or replace the watchdog's separate agent census and launch fences.
