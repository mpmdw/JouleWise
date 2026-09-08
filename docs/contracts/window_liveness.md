# Keep status work outside power measurements

## 1. The physical problem

A power measurement records the electricity used by the machine while it does
specified work. A status publisher is a program that writes a progress report
and sends it to another computer; here it runs Git, the program that records
file changes and transfers them over the network. That processor, disk, and
network work adds electricity use to the measurement. A **window** is the
scheduled period reserved for measurement, including preparation and pauses.
The publisher must stay out of that period. [P1]

A **process** is a running instance of a program. The old check searched all
process names and command arguments on the machine with `pgrep`, a program
that finds matching text in the process list. The **night driver** is the
program that executes the night's schedule. A
**child process** is a process started by another process; a **chain** is the
night driver's child running the whole sequence of measurements and pauses.
A **campaign** is one execution of the measurement runner, the program
controlling a set of measurement runs, within that sequence or separately.
A **test stub** is a substitute program used by a test;
a leaked stub keeps running after the test that started it. The name search
could mistake that stub for a measuring chain, and tripped when **test shards**,
separate portions of the test suite, ran at the same time. The replacement
checks records of particular processes instead of their command words. [P2]

A **custody parent** is the directory containing the directories that retain
each night's records. A **census** is an inventory made by reading those records
and checking their processes. **Liveness** means whether a recorded process is
still running; **indeterminate** means the available records or observations
cannot establish that answer. The **guard**, the check that can stop the status
script, refuses an update when it finds a recorded process still running or an
indeterminate observation. The detailed rules below implement the
[lead's decision](../process_traces/2026-09-08-handoff-redo/99ap-magistrate-terminal-review-window-liveness.md)
for chains, campaigns, and their custody records at Git revision `655b3368`
(the source version used by the final Code map). [P3]

## 2. Three facts about a process

The **kernel**, the operating system component that creates and tracks
processes, gives each process a positive integer **process ID**, or **PID**.
It also puts processes into a **process group**, a set that can be addressed
together, identified by a **PGID**. The kernel records when a process started;
`/bin/ps`, the system program that prints process information, prints that time
as **`lstart`**, a date and time with one-second precision. A **start token**
here is that printed date with **whitespace** (spaces, tabs or line breaks)
between fields replaced by one space and removed from the ends; for example,
`Tue Sep  8 01:41:58 2026` becomes `Tue Sep 8 01:41:58 2026`. A valid token
has an English three-letter weekday (`Mon` through `Sun`), an English
three-letter month (`Jan` through `Dec`), a one- or two-digit day, two-digit
hour/minute/second separated by colons, and a four-digit year, in that order.
These are spelling/shape requirements, not calendar checks: the code does not
check weekday/date agreement or numeric ranges within those digit widths.
An **identity** is the pair of PID and start token: the kernel can give a later
process the same PID, so the PID alone cannot identify the earlier process.
The chain writer records all three facts; campaigns record PID and start
token. [F1]

The **operator** is Ed or the lead responsible for the window. In that person's
shell (the program reading terminal commands), this exact command asks for the shell's PID, PGID, and start time:

```sh
LC_ALL=C LANG=C /bin/ps -o pid=,pgid=,lstart= -p "$$"
```

`$$` is the shell's own PID; `-p` selects it; `-o` chooses columns; `=` suppresses
column headings. `LC_ALL=C LANG=C` sets the language and date-format environment
to the fixed English form expected here. The output has **seven**
whitespace-separated fields: PID, PGID, and five date fields. The production
identity check below instead expects **six** fields: five date fields and one
process-state field, which describes whether the process is executing,
waiting, or ended. Do not interchange these two response formats. [F2]

**Historical fallback, not a fresh observation.** In this rewrite's **sandbox**, the environment restricting which system
operations commands may perform,
`/bin/ps -o pid=,pgid=,lstart= -p $$` was denied with
`operation not permitted: /bin/ps`. The retained
[2026-09-08 process capture](../process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/pass3-process-tree-keepalive.txt)
contains the following actual PID, parent PID (the process that launched it),
and date prefix; only the trailing command text is omitted:

```text
83086 83075 Tue Sep  8 01:41:58 2026
```

Removing the parent-PID column gives this **six-field historical extract**:

```text
83086 Tue Sep  8 01:41:58 2026
```

This extract is PID plus date, not the production response. The capture does
not contain PGID or process state; `83075` must not be relabeled PGID. Its
[matching saved record](../process_traces/2026-09-02-hands-free-week/21-activation-784a764e/magistrate.lock.json)
records PID `83086`, start token `Tue Sep 8 01:41:58 2026`, and launch time
`1788856918.677485`. It describes an agent process, not a measurement.

All following files and responses are **worked examples**, not claimed live
captures: they reuse those real PID/time values to show how a measurement
record would work, and explicitly supply example PGID, state, paths, and
random strings. For the example chain, PGID is `83086` because the driver
starts the child as the first process in a new group. [F3]

## 3. Record the chain before asking another program about it

A **marker** is a file whose name and contents record an event. `chain.started`
records the chain launch; `chain.exited` records its end. The driver stores
them under `night/` in the night's record directory, for example
`/Users/edr/night-custody/rehearsal-20260909/night/chain.started`.
It first **claims** the start filename: creates it only if no file already has
that name, using `O_CREAT | O_EXCL | O_WRONLY` (create, refuse an existing name,
and open for writing). The **file owner**, the user account that creates the
file, receives the access permissions below. The returned **descriptor** is the integer handle by
which the writer accesses that opened file; creation uses permissions `0o600`,
meaning only its owner can read or write it. An existing claim prevents a
second launch. [C1]

**JSON** is text containing named values: an **object** uses braces, names and
text values use double quotes, numbers are unquoted, and `null` means no value.
Names are also called **keys**; `true` and `false` are **booleans**, yes/no values
distinct from numbers.
**UTF-8** is the text-to-byte encoding used for these files. `epoch_s` counts
wall-clock seconds since 1970-01-01 00:00:00 Coordinated Universal Time (UTC),
the reference instant called
the **Unix epoch**; it is the time the marker is prepared, not the kernel's
process start time. After **spawning**, or starting, the child, the driver first
writes this complete example record, followed by a newline: [C2]

```json
{
  "epoch_s": 1788856918.677485,
  "pgid": 83086,
  "pid": 83086
}
```

`_write_all` keeps writing until every byte has been handed to the operating
system, then calls **`fsync`**, which requests that the file data be sent to
storage, and the caller closes the descriptor before the **probe**, the command
that asks the kernel about the PID. [C3]

Only then does the driver probe the child, add `start_time`, write and fsync
`chain.started.tmp` (a temporary replacement file), and call `os.replace`:
**atomic replacement** means that opening `chain.started` sees the old file
or the replacement file, rather than a file halfway through that replacement.
The example replacement is: [C4]

```json
{
  "epoch_s": 1788856918.677485,
  "pgid": 83086,
  "pid": 83086,
  "start_time": "Tue Sep 8 01:41:58 2026"
}
```

If the probe cannot supply a running process's start token, the replacement
contains `"start_time": null`. When neither exit check accepts an exit, the
census refuses any start object without a usable token before it probes the
PID, even if that PID has disappeared. The
initial empty or partially written file can still be seen between the claim
and completion of the first write; moving the probe after that write prevents
the probe's delay from extending that interval. The replacement has no
subsequent fsync of its containing directory, so this sequence does not promise
that the replacement name survives power loss. [C5]

In this diagram, each bracket names a driver action, each arrow means “next
in time,” and each `reader:` line names what a new reader can see at that
stage; the complete records are the two JSON objects above. [C6]

```text
[claim: create chain.started exclusively]
  reader: empty file
       | next in time
       v
[spawn: start child PID 83086 in group 83086]
  reader: empty file
       | next in time
       v
[first write: write PID/PGID/epoch, fsync, close]
  reader: possibly partial during write; complete first JSON after close
       | next in time
       v
[probe: ask /bin/ps about PID 83086]
  reader: complete first JSON, no start_time; census refuses
       | next in time
       v
[replace: write/fsync .tmp, then os.replace]
  reader: first JSON until replace; second JSON after replace
```

The separate **dead-man** is the scheduled recovery execution of the night
driver; it needs the group number even if the identity probe has not finished.
Once earlier courier-delivery checks (for the program that emails the night's
result) allow recovery to reach a start with no exit, it reads a positive integer `pgid` (excluding a JSON true/false value) and calls
`os.killpg(pgid, 0)`, an existence/permission check on that group that sends no
**signal**, an operating-system notification such as a termination request.
`ProcessLookupError` means no such group and permits an
exit record; `PermissionError` means access was denied and leaves the group
possibly alive, so recovery refuses. If the group value is missing, unreadable,
or unusable, recovery instead writes an exit with `exit_code: null` (no
integer result), `reaped_by: "dead-man"` (the recovery writer's name), and
`launch_failed: true` (classified as launch failure). [C7]

For example, after the first JSON is complete, recovery can check group
`83086` while the publisher still refuses for lack of `start_time`; no-such-group
lets recovery write an exit, but permission denial does not. This recovery
check is separate from the census's PID/start-token check. [C8]

An **exit code** is the integer returned when a process ends; `null` in an exit
record means no integer result was recorded. **`monotonic_ns`** is a clock
reading in nanoseconds from a clock that advances without wall-clock
adjustments; it is not a calendar timestamp. The driver records the child's
end after waiting for it, after successful termination and waiting, after
failure to spawn, or through the recovery paths just described; `reaped_by`
names recovery and `launch_failed` marks its launch-failure classification.
The census accepts an exit object precisely when `exit_code` is an integer
or null, `epoch_s` is an integer or floating-point (decimal) number, and `monotonic_ns`
is an integer, excluding true/false values for all those numeric checks;
extra keys are allowed and these checks impose no positivity or clock-order
requirement. [C9]

The exit-reading order matters: if `chain.started` is absent, the census ignores
`chain.exited` entirely; if a start exists and an acceptable exit is already
present, it returns without reading the start's contents. Otherwise it reads
the start as an object and checks once more for an exit before validating the
start token and PID. An unacceptable exit encountered at either exit check
refuses; a malformed start that fails to read as an object prevents reaching
the second exit check. [C10]

## 4. Ask about identity, then compare it

For PID `83086`, the production probe runs the exact command below with a
two-second **timeout**, the limit on how long the command may run; **stdout** is its normal text output, **stderr** its
separate diagnostic output, and **rc** its integer return code. [I1]

```sh
LC_ALL=C LANG=C /bin/ps -p 83086 -o lstart= -o stat=
```

`stat` is the process state printed by `ps`. This complete six-field **example**
response has rc `0` and empty stderr; `S` means sleeping, or waiting for work,
which still counts as an existing process: [I2]

```text
Tue Sep  8 01:41:58 2026 S
```

The **parser**, the code that separates and checks response fields, splits on
whitespace and requires exactly six fields. Its first five must form the valid
start token defined in F1. The sixth field must have one or more characters
drawn only from the following letters and symbols: letters
`A`–`Z`/`a`–`z`, digits `0`–`9`, or `+`, `<`, `-`; a state beginning `Z` is a
**zombie**, a process that has ended but whose parent has not yet collected its
exit result. [I3]

**LIVE** is the probe's result for an accepted non-zombie response, **DEAD**
for an absent PID or accepted zombie response, and **UNKNOWN** for an
insufficient observation. These labels describe the PID now; comparison with
the saved token is a second step. The ordered table below completely defines
the probe, including its error paths; **empty** means empty after trimming
whitespace from both output streams where specified. [I4]

| First applicable condition | Probe result |
|---|---|
| PID is not a positive integer, or is true/false | UNKNOWN; command not run |
| Command cannot execute, exceeds two seconds, fails to decode text, or raises an error while running the child command | UNKNOWN |
| rc 1, stdout empty, stderr empty | DEAD |
| rc 0, stdout empty, stderr empty | UNKNOWN: success without evidence |
| Any other nonzero rc, any nonempty stderr, or other than six stdout fields | UNKNOWN |
| Six fields but invalid date shape or invalid state characters | UNKNOWN |
| rc 0, empty stderr, accepted six fields, state starts `Z` | DEAD |
| rc 0, empty stderr, accepted six fields, state does not start `Z` | LIVE with the whitespace-adjusted five-field token |

The **recorded owner** is the process named by the saved PID and start token.
For a record whose PID is valid, a DEAD result contributes a **warning**,
a diagnostic that does not itself prohibit the update; for a LIVE result,
matching valid tokens contribute a **refusal**, which prohibits it. Two
different valid tokens mean a **reused PID**: the current process is not the
recorded one, so the old record contributes a warning. UNKNOWN, or LIVE without
two comparable valid tokens, is indeterminate and refuses. Chain records
add the earlier requirement that their token must be valid even before a DEAD
probe can be reached. A result is **clear** when it contains no refusals. [I5]

For example, saved token `Tue Sep 8 01:41:58 2026` and the six-field response
above give LIVE and then a matching-owner refusal. Response
`Tue Sep 8 01:41:58 2026 Z` gives DEAD; rc `1` with both streams empty also gives
DEAD; rc `1` with stderr `permission denied` gives UNKNOWN. A successful
six-field response `Tue Sep 8 02:12:35 2026 S` gives LIVE but a mismatch:
PID `83086` has been reused in this example, and its old record warns. [I6]

The identity flow below uses brackets for named operations and arrows labeled
with the result selecting the next operation; “record” means the saved PID and
start token, and all LIVE/DEAD/UNKNOWN rules are those in I4. [I8]

```text
[require positive integer PID; a chain also requires valid start token first]
  | invalid -> [refuse; do not probe]
  | valid
  v
[probe this PID using I4]
  | DEAD    -> [warn: recorded owner ended]
  | UNKNOWN -> [refuse: cannot decide]
  | LIVE
  v
[compare saved and observed start tokens]
  | either invalid -> [refuse: cannot compare]
  | both valid, equal -> [refuse: recorded owner still running]
  | both valid, unequal -> [warn: PID now belongs to a later process]
```

`JOULEWISE_IDENTITY_PROBE`, an environment setting, can replace `/bin/ps` with
one executable pathname receiving the same arguments; it does not accept a
shell command string. If set to `/usr/bin/true`, a program that exits
successfully without printing anything, the command returns rc `0` and no
process evidence. Treating that as DEAD would permit status work beside a
running measurement, so it must be UNKNOWN. Keep this override unset in
production; the removed `JOULEWISE_STATUS_PS_COMMAND` name-search setting is
not read by this guard. [I7]

## 5. Let a separate campaign leave a discoverable record

Campaigns may write their runs in different directories, so the publisher
needs a shared **registry**, a directory containing one registration file per
measurement-runner execution. Its path is the custody parent plus
`active-campaigns`. The parent is selected by `JOULEWISE_CUSTODY_PARENT`, default
`~/night-custody`, where `~` expands to the user's home directory; on Ed's
machine the default registry is `/Users/edr/night-custody/active-campaigns`.
Each entry's name is its PID, a hyphen, 48 lowercase **hexadecimal** characters
(digits `0`–`9` and letters `a`–`f` encoding 24 random bytes), and `.json`. [R1]

A **runs root** is the directory holding a campaign's runs. **`campaign.lock`**
is the file there that prevents two campaigns from taking that same runs root
at once; an **acquisition** is successfully creating that file exclusively.
A **nonce** is a random value distinguishing that acquisition, here 32 random
bytes encoded as 64 hexadecimal characters. The lock records the runner PID,
nonce, creation date and start token; the registry copies its nonce, with a
separately random filename suffix. The entry's `schema` is the exact string
identifying this record format. A **filesystem** is the operating system's
organization of stored files; a **link** here is a stored name pointing to
another location. The entry's `runs_root` is a **resolved absolute path**:
it starts at `/`, incorporates any parts relative to the current directory,
and follows those links to their target locations. [R2]

This fully specified example entry lives at
`/Users/edr/night-custody/active-campaigns/83123-0123456789abcdef0123456789abcdef0123456789abcdef.json`.
PID `83123` and its start date also occur in the historical capture, but this
registration, path and nonce are illustrative. The writer emits one JSON line
and a final newline: [R3]

```json
{"nonce": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef", "pid": 83123, "runs_root": "/Users/edr/JouleWise-window-custody/rehearsal-20260909/runs", "schema": "joulewise.active_campaign.v1", "start_time": "Tue Sep 8 01:41:59 2026"}
```

`scripts/run_campaign.py` publishes this kind of entry after taking the lock
and before launching a measurement child in both ordinary execution and
`run_axi_spec_campaign`, its alternate measurement execution function.
A **dry run**, which prints planned commands without executing measurements,
and acquisitions used only for maintenance or calculating results create no
registry entry. Publication requires a positive integer PID, a valid start
token, and a nonempty nonce; if the lock has no start token, publication probes
again, and an unavailable identity prevents launching measurements. [R4]

The writer creates the registry directories if needed and opens a new unique
entry with `xb`, meaning exclusive creation of a file written as bytes. A
file's **device number** identifies its filesystem, and its **inode number**
identifies the file object within that filesystem. The writer saves those
two numbers as the file's identity and writes the bytes using Python, the
programming language used here. It **flushes** buffered output (bytes held in
Python's memory) into the operating system, then fsyncs the file; if writing
fails, it removes the partial file only while it still has that original
device/inode pair. [R5]

Both measurement execution paths call `remove_campaign` in `finally`, Python's
cleanup block for normal return or an **exception**, an error interrupting
normal execution, before releasing the lock.
Removal reads the entry and compares device number, inode number and exact
bytes with those saved when it was created, then checks device/inode again
before **unlinking**, removing the directory's name for the file; an edited or
replaced entry is preserved. The status census never removes entries, and
it does not consult `campaign.lock`, so a missing lock does not clear an entry.
The runner has no `SIGTERM` handler, meaning no custom cleanup for the operating
system's termination request; that request or `SIGKILL`, forced termination,
can end it without this Python cleanup and leave both files. [R6]

For example, an unchanged entry with device `16777234`, inode `90123456` and
the exact R3 bytes is removable by its writer; if another file takes the same
name with inode `90123457`, removal preserves it. These numbers illustrate the
comparison, not filesystem evidence from this run. The ordering is below:
brackets name operations, arrows mean “next operation,” and the two labeled
branches name successful execution or an exception. [R7]

```text
[acquire campaign.lock] -> [publish registry entry] -> [run measurement children]
                                   | failure                 | return or exception
                                   v                         v
                           [do not launch children]   [finally: remove own entry]
                                   |                         |
                                   v                         v
                           [finally: release lock]    [finally: release lock]
```

Before probing a campaign entry, the reader requires a readable JSON object,
`schema` exactly `joulewise.active_campaign.v1`, a nonempty string `nonce`,
an absolute-path string `runs_root`, and a positive integer `pid` excluding
true/false. It does not require a particular nonce length, a filename pattern,
an existing runs directory or lock, or a `pgid` field. Only after those checks
does it probe: DEAD warns without validating `start_time`; LIVE needs two
valid tokens and warns if they differ; UNKNOWN or LIVE without valid tokens
refuses. Thus “malformed” must specify which check failed: a missing token in
an otherwise acceptable DEAD campaign is permitted, while a bad schema is
not. [R8]

A **stale entry** is one whose recorded process is gone (including a zombie),
or whose PID now belongs to a process with a different valid start token;
its age alone is irrelevant. For the example entry, `83123` absent with rc `1`
and no output warns; `Tue Sep 8 01:41:59 2026` saved versus
`Tue Sep 8 02:12:35 2026` observed also warns. Changing the saved token to null
still warns in the absent-PID case, but refuses in the running-PID case.
A dead runner can leave its child processes running, so a stale warning is
not proof that all measurement activity ended. [R9]

The operator repairs one stale registry entry between windows, after preventing new launches and
independently confirming that no measurement children remain. Use an updated
checkout (a local copy of the repository) and set `ENTRY` to the exact file
being inspected; the complete command below uses the example filename, which
must be replaced when repairing a different actual entry. The command uses
real `/bin/ps`, preserves entries that are live, unknown or fail R8's required
checks, and deliberately permits the DEAD/missing-token exception. Its saved
file identity and bytes make a later edit or replacement detectable by the
removal helper. It repairs only the registry, not the separate lock. [R10]

In the command, `env -u` removes the probe override, and
`PYTHONDONTWRITEBYTECODE=1` prevents Python from saving translated copies of
imported program files. `os` supplies environment and file-information calls;
`Path` represents a filesystem path. `RegistryEntry` holds the path, device
number, inode number and bytes just read; `_inspect_campaign` applies R8 and
I5, and `Census` collects its warnings and refusals. `custody_parent` selects
the configured parent, `observe_identity` performs I4, and `remove_campaign`
performs R6. A read/validation exception stops the command before removal.
For a different custody parent, change both the explicit parent and entry
path. Preserve chain markers; repair a leftover campaign lock through the
separate `quarantine_stale_lock` procedure (moving the lock aside after its
own checks) in the [G2 runsheet](../process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md).
Do not delete an unknown entry to force a publish decision. [R11]

```sh
ENTRY=/Users/edr/night-custody/active-campaigns/83123-0123456789abcdef0123456789abcdef0123456789abcdef.json \
JOULEWISE_CUSTODY_PARENT=/Users/edr/night-custody \
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


## 6. Read every selected parent until an error stops the census

A publisher and its measurement runners must use the same custody parent so
that the files the runners create are the files the publisher checks.
`JOULEWISE_ADDITIONAL_CUSTODY_PARENTS` supplies more parents as a JSON **array**,
an ordered list in square brackets; the default is `[]`, an empty list.
Every element must be a nonempty path string. The reader expands `~`, places
the primary parent first and the additional parents afterward, and removes
identical Python `Path` values while retaining first occurrence; it does not
resolve these parents to collapse different paths to the same filesystem
location. Invalid JSON or an unacceptable list refuses. [D1]

For each parent, the reader lists only its immediate children. A child named
`active-campaigns` is opened as a directory, and every entry is inspected,
regardless of extension; each other child that is a directory is inspected
at `child/night/chain.started`, without requiring a plan file. A missing
parent is empty, as are a missing registry and a night with no start marker.
A parent that is a file, a permission error, or an unreadable/invalid record
refuses. The first such unhandled error stops the outer traversal: later
parents need not have been inspected. [D2]

**Reconciliation** here means retrying a disappearing path once. A **wrapper**
is a helper surrounding an inspection to handle its errors; here, if inspection
raises `FileNotFoundError` (a path disappeared), the wrapper tests whether the relevant entry,
registry directory, or start marker still exists; if absent, it contributes
nothing, and if present, inspection is attempted one more time. Each wrapper
retries once; an entry's second disappearance can therefore
reach the enclosing registry wrapper, which may restart the whole registry
inspection once if the directory still exists. Only an error escaping all
applicable wrappers becomes indeterminate. Registry warnings/refusals
are accumulated separately and copied to the result only after that registry
inspection finishes, so an error can discard that registry's partial findings
while still making the overall census refuse. The census only reads; it does
not create, repair or remove custody files. [D3]

This traversal diagram uses brackets for named actions and arrows labeled
with the condition selecting the next action; “next” preserves parent order,
while child order is whatever the directory listing returned. [D6]

```text
[parse and deduplicate parent list as D1 describes]
  | invalid -> [add refusal; stop traversal]
  | valid
  v
[list next parent]
  | missing -> [advance to next parent, or finish if none remain]
  | other error -> [add refusal; stop traversal]
  | listing obtained
  v
[inspect each immediate child using the D3 retry wrappers]
  | named active-campaigns -> [inspect each entry by R8]
  | other directory -> [inspect its night/chain.started by C10]
  | other file or disappeared child -> [skip child]
  | error escaping wrappers -> [add refusal; stop traversal]
  | all children finished
  v
[advance to next parent, or finish if none remain]
```

For example, primary parent `/Users/edr/night-custody` plus additional list
`["/Users/edr/night-custody", "/private/tmp/liveness-other"]` gives two distinct
parents. In the diagram, indented names are filesystem children, each bracket
labels what is inspected, and arrows identify the next parent; the reader
does not search further directory levels beyond the shown record locations. [D4]

```text
/Users/edr/night-custody [first parent]
  rehearsal-20260909/ [night's record directory]
    night/chain.started [chain record]
    night/chain.exited  [exit record, checked only when start exists]
  active-campaigns/ [registry directory]
    83123-0123456789abcdef0123456789abcdef0123456789abcdef.json [campaign record]
        |
        | next selected parent, only if traversal has not raised an error
        v
/private/tmp/liveness-other [second parent; if missing, empty contribution]
```

If the second parent is absent and the first has no active records, the result
is clear. If listing the first parent fails with permission denied, the result
is indeterminate and the reader never reaches the second parent; if an entry
vanishes and is still absent at its existence recheck, that entry contributes
nothing. [D5]

## 7. Complete publish decision table

**Precedence rule:** first follow the start/exit read order in C10, then the
chain or campaign's required checks, then any probe and token comparison that
those checks permit; after that, any refusal anywhere overrides every clear
contribution and every warning. “Permit” below means only that this guard
allows the status script to proceed; it does not override separate operating
rules that keep agents out of measurements. [T1]

The requested marker categories have the following precise meanings. A
**complete** start is a readable object carrying the writer's PID/PGID/epoch
fields; for census acceptance only PID and start token are checked, so an
object lacking PGID/epoch follows the same rows when those two fields suffice.
**Malformed** means unreadable/non-object JSON or a failed required check as
specified in the row, not merely a missing optional field. **Not-run** means
no identity probe was called for this chain; the registry can still have its
own probes. All LIVE rows refer to the raw probe result, with token comparison
shown separately. [T2]

| Row | Marker/read condition | Chain probe | Chain contribution |
|---|---|---|---|
| A | Absent start; exit absent, valid or invalid is ignored | not-run | clear |
| M1 | Start present; invalid exit encountered at either exit check | not-run | refuse indeterminate |
| M2 | Malformed/unreadable/non-object start; no exit accepted before start read | not-run | refuse indeterminate |
| N | Complete-no-token, or object with missing/null/invalid token; no accepted exit | not-run | refuse indeterminate, even if PID would be DEAD |
| M3 | Valid token but missing, noninteger, true/false or nonpositive PID; no accepted exit | not-run | refuse indeterminate |
| L | Complete-with-token and valid PID; no accepted exit; observed token matches | LIVE | refuse live owner |
| U | Complete-with-token and valid PID; no accepted exit; observed valid token differs | LIVE | warn reused PID |
| D | Complete-with-token and valid PID; no accepted exit | DEAD | warn dead owner |
| Q | Complete-with-token and valid PID; no accepted exit | UNKNOWN | refuse indeterminate |
| E | Exited: start exists; valid exit accepted before start read, or after successful object read | not-run | clear, including malformed contents bypassed at first exit check |

There are no other reachable marker/probe pairings: A/M1/M2/N/M3/E do not call
the chain probe; L/U/D/Q require its call. An exit appearing only after a
malformed start has already failed cannot retroactively select E. An exit
appearing after the second exit check is not observed on that inspection. [T3]

For the next table, registry **empty** means no contributing entry;
**entry-live** means R8 passes and LIVE tokens match; **entry-dead** means R8's
pre-probe checks pass and the PID is DEAD (token may be missing/invalid) or
LIVE tokens differ; **entry-unknown** means those checks pass but the probe is
UNKNOWN or LIVE lacks comparable tokens; **malformed** means an entry fails
R8's pre-probe checks or cannot be read. Thus entry-dead describes the recorded
owner and includes a reused PID even though the raw probe is LIVE. For multiple
entries, apply each entry's row: any entry-live, entry-unknown or malformed
entry refuses. Parent/configuration/read errors likewise refuse independently
of this table. [T4]

Every reachable chain row is paired with all five registry categories below.
A row describes the combined decision if both records are observed; when an
earlier malformed record stops traversal, the unvisited record's contents
cannot change the already-established refusal.
“Warn; permit” retains a stale diagnostic while permitting the script;
“Refuse” wins even if the other contribution is only a warning or clear. [T5]

| Chain row (marker category) | Chain probe | Registry | Combined decision |
|---|---|---|---|
| A (absent) | not-run | empty | Permit |
| A (absent) | not-run | entry-live | Refuse |
| A (absent) | not-run | entry-dead | Warn; permit |
| A (absent) | not-run | entry-unknown | Refuse |
| A (absent) | not-run | malformed | Refuse |
| M1 (malformed exit) | not-run | empty | Refuse |
| M1 (malformed exit) | not-run | entry-live | Refuse |
| M1 (malformed exit) | not-run | entry-dead | Refuse |
| M1 (malformed exit) | not-run | entry-unknown | Refuse |
| M1 (malformed exit) | not-run | malformed | Refuse |
| M2 (malformed start) | not-run | empty | Refuse |
| M2 (malformed start) | not-run | entry-live | Refuse |
| M2 (malformed start) | not-run | entry-dead | Refuse |
| M2 (malformed start) | not-run | entry-unknown | Refuse |
| M2 (malformed start) | not-run | malformed | Refuse |
| N (complete-no-token) | not-run | empty | Refuse |
| N (complete-no-token) | not-run | entry-live | Refuse |
| N (complete-no-token) | not-run | entry-dead | Refuse |
| N (complete-no-token) | not-run | entry-unknown | Refuse |
| N (complete-no-token) | not-run | malformed | Refuse |
| M3 (malformed PID) | not-run | empty | Refuse |
| M3 (malformed PID) | not-run | entry-live | Refuse |
| M3 (malformed PID) | not-run | entry-dead | Refuse |
| M3 (malformed PID) | not-run | entry-unknown | Refuse |
| M3 (malformed PID) | not-run | malformed | Refuse |
| L (complete-with-token; match) | LIVE | empty | Refuse |
| L (complete-with-token; match) | LIVE | entry-live | Refuse |
| L (complete-with-token; match) | LIVE | entry-dead | Refuse |
| L (complete-with-token; match) | LIVE | entry-unknown | Refuse |
| L (complete-with-token; match) | LIVE | malformed | Refuse |
| U (complete-with-token; mismatch) | LIVE | empty | Warn; permit |
| U (complete-with-token; mismatch) | LIVE | entry-live | Refuse |
| U (complete-with-token; mismatch) | LIVE | entry-dead | Warn; permit |
| U (complete-with-token; mismatch) | LIVE | entry-unknown | Refuse |
| U (complete-with-token; mismatch) | LIVE | malformed | Refuse |
| D (complete-with-token) | DEAD | empty | Warn; permit |
| D (complete-with-token) | DEAD | entry-live | Refuse |
| D (complete-with-token) | DEAD | entry-dead | Warn; permit |
| D (complete-with-token) | DEAD | entry-unknown | Refuse |
| D (complete-with-token) | DEAD | malformed | Refuse |
| Q (complete-with-token) | UNKNOWN | empty | Refuse |
| Q (complete-with-token) | UNKNOWN | entry-live | Refuse |
| Q (complete-with-token) | UNKNOWN | entry-dead | Refuse |
| Q (complete-with-token) | UNKNOWN | entry-unknown | Refuse |
| Q (complete-with-token) | UNKNOWN | malformed | Refuse |
| E (exited) | not-run | empty | Permit |
| E (exited) | not-run | entry-live | Refuse |
| E (exited) | not-run | entry-dead | Warn; permit |
| E (exited) | not-run | entry-unknown | Refuse |
| E (exited) | not-run | malformed | Refuse |

The helper prints warnings with `WARN:` and refusals with `REFUSING:` to stderr,
and returns rc `0` exactly when it has no refusals, otherwise rc `1`. The shell
runs that helper before writing `WINDOW_STATUS.md` or doing Git work, and
returns rc `1` if the helper fails. `courier.sent`, the file recording delivery
of the night's handback message, is not inspected and cannot clear either
chain or campaign contributions. [T6]

A **commit-freeze sentinel** is a file whose presence suppresses Git work;
`JOULEWISE_COMMIT_FREEZE_SENTINEL` selects it, default
`/Users/edr/JouleWise-window-custody/COMMIT_FREEZE_OPEN`. **Staging** means adding
changes to Git's proposed next saved revision; **commit** means saving that
revision locally; **push** means sending it to the remote repository.
`JOULEWISE_STATUS_REPO` chooses the checkout holding the status file and used
for Git, default `/Users/edr/code/JouleWise`; the helper instead comes from
the invoked script's checkout, and custody selection stays independent. [T7]

| Census result | Sentinel | Subsequent shell action |
|---|---|---|
| Any refusal | Present or absent | rc 1 before status write or Git |
| No refusals | Present | Write status locally; rc 0 without Git |
| No refusals | Absent | Write status; stage; if no staged changes, rc 0; otherwise commit and attempt push |
| No refusals; commit succeeded but push fails | Absent | Warn that only the local commit exists; rc 0 |

These are the script's explicit branches; other unhandled command failures,
such as a failed write or commit, stop it under `set -e` (exit on an unhandled
failing command). A clear census is a **snapshot**, observations at the times
of its reads, not **mutual exclusion**, a lock preventing a new measurement
from starting during publication. Use updated driver-managed chains and
sequence publication and launch so they cannot overlap. A hand-run chain's
pauses, a collector (the launchd-run measurement collection program) without
registrations, an old checkout, surviving children
of a dead owner, or a new launch after inspection can escape this inventory;
start tokens also cannot distinguish reuse within the same printed second.
The watchdog (the agent-monitoring LaunchAgent that evaluates arming ticks)
has checks for agent processes and rules forbidding launch that remain separate. [T8]

## 8. Follow the numbers through refusal and publication

This example is a reconstruction exercise, not a live measurement or actual
publish. Keep launches stopped while checking or publishing. Use primary
parent `/Users/edr/night-custody` and additional parent
`/private/tmp/liveness-other`; suppose the latter is missing. The files and
process observations are exactly the examples above, changing only as each
row says. The chain's PID is `83086`; the campaign's PID is `83123`. [W1]

| Step | Observed chain evidence | Observed registry evidence | Apply table; result |
|---|---|---|---|
| 1 | At epoch 1788856918.677485, first C2 JSON has no token; no exit | empty | N/not-run + empty: refuse before any status write |
| 2 | Replacement C4 JSON; rc 0, empty stderr, `Tue Sep 8 01:41:58 2026 S` | empty | L/LIVE + empty: refuse throughout chain pauses too |
| 3 | Same chain | R3 entry; rc 0, empty stderr, `Tue Sep 8 01:41:59 2026 S` | L/LIVE + entry-live: refuse for both recorded owners |
| 4 | Exit object below accepted; chain probe not run | Same matching LIVE campaign | E/not-run + entry-live: refuse despite chain exit |
| 5 | Same accepted exit | PID 83123 returns rc 0 and no output because probe is `/usr/bin/true` | E/not-run + entry-unknown: refuse; empty success is no proof |
| 6 | Same accepted exit | Restore real probe; PID 83123 returns rc 1, stdout/stderr empty | E/not-run + entry-dead: warn, guard permits |
| 7 | Same accepted exit | Alternatively PID 83123 now returns rc 0, empty stderr, `Tue Sep 8 02:12:35 2026 S` | E/not-run + entry-dead: the two start tokens differ; warn, guard permits |
| 8 | Same accepted exit | Operator verifies no measurement children, runs repair command; registry becomes empty | E/not-run + empty: permit without stale warning |

For steps 4–8, this example `chain.exited` has the required types; the
monotonic value is illustrative and need not be converted to epoch time: [W2]

```json
{
  "epoch_s": 1788858755.0,
  "exit_code": 0,
  "monotonic_ns": 123456789000000
}
```

If the sentinel exists at step 6, `scripts/window_status.sh complete
"Example chain ended"` writes only local status after the warning; if absent,
it stages the status, commits if there is a staged change, and attempts push.
Running the same command at step 4 refuses even with a sentinel. If instead
the second parent exists but cannot be listed, steps 6–8 all refuse for that
read error; the first parent's stale/empty result cannot cancel it. These are
predicted outcomes from the source, not commands executed by this rewrite. [W3]

## Code map

All `file:line` references below are at `655b3368b34d173bda9c5660343c3a2753c0ee97`.
Paragraph IDs connect every mechanism statement, diagram and decision row to
its implementation; definitions and explicitly constructed numbers explain
those statements rather than claiming additional evidence of execution. Where a
paragraph contains several mechanism sentences, the mapping lists their
implementing lines in reading order. Historical problem/evidence claims are
identified separately instead of being attributed to current code.

| Text | Implementing location and correspondence |
|---|---|
| P1 | `scripts/window_status.sh:12`–`:19`: Git/network contamination and allowed call times; `:60`–`:94`: status write; `:101`–`:106`: Git staging/change check; `:107`–`:108`: commit/push |
| P2 | Historical failure: terminal review linked in P3, opening and Why; replacement: `joulewise/measurement_liveness.py:41`–`:68` and `scripts/window_status.sh:41`–`:47` |
| P3 | Parent: `joulewise/measurement_liveness.py:71`–`:72`; census: `:224`–`:263`; refusals: `:166`–`:201`, `:261`–`:272`; caller: `scripts/window_status.sh:41`–`:47` |
| F1, F3 | PID/token probe and one-second format: `joulewise/measurement_liveness.py:25`–`:68`; chain's PID/PGID: `scripts/run_night.py:373`–`:385`, `:431`–`:437`; campaign PID/token: `joulewise/measurement_liveness.py:113`–`:116`; reuse: `:175`–`:182` |
| F2 | Production argument/language distinction: `joulewise/measurement_liveness.py:53`–`:56`, `:62`–`:68`; operator column command is explanatory, not the production command; historical extract links above own its values |
| C1 | Names: `joulewise/measurement_liveness.py:185`–`:186`, `:259`; exclusive claim, permissions, existing-name return: `scripts/run_night.py:360`–`:369`; launch claim use: `:1247`–`:1266` |
| C2 | JSON encoding/newline: `scripts/run_night.py:102`–`:103`; child spawn: `:431`–`:437`; first record, write time: `:373`–`:380` |
| C3 | Complete writes/fsync: `scripts/run_night.py:109`–`:116`; close before probe: `:375`–`:380` |
| C4 | Probe, temporary write, replacement: `scripts/run_night.py:380`–`:385`; temporary exclusive write/fsync: `:116`–`:125` |
| C5 | Null: `scripts/run_night.py:382`; census token-before-PID: `joulewise/measurement_liveness.py:199`–`:201`; empty interval: `scripts/run_night.py:360`–`:380`; no directory fsync: `:382`–`:385`; accepted power-loss limitation: linked terminal review, Lead rulings |
| C6 | Entire timeline: `scripts/run_night.py:360`–`:385`, `:431`–`:452` |
| C7 | Earlier courier checks: `scripts/run_night.py:1358`–`:1385`; group parsing: `:1339`–`:1348`; missing group exit: `:1387`–`:1401`; zero-signal check and two exception meanings: `:1403`–`:1422` |
| C8 | Same example branches: `scripts/run_night.py:1389`–`:1422`; distinct census check: `joulewise/measurement_liveness.py:199`–`:201`, `:53`–`:68` |
| C9 | Exit fields: `scripts/run_night.py:312`–`:328`; termination/wait: `:331`–`:357`; launch failure: `:438`–`:450`; ordinary wait/exit: `:498`–`:499`; recovery: `:1387`–`:1422`; exact reader types: `joulewise/measurement_liveness.py:159`–`:163` |
| C10 | Each sentence follows `joulewise/measurement_liveness.py:187`–`:201` in execution order; object failure: `:144`–`:148` |
| I1 | Arguments, streams, timeout: `joulewise/measurement_liveness.py:49`–`:59` |
| I2, I3 | Six-field/date/state parsing: `joulewise/measurement_liveness.py:25`, `:34`–`:38`, `:62`–`:68`; sleeping-state example is accepted by `:66`–`:68` |
| I4 | Every probe-table row in order: `joulewise/measurement_liveness.py:49`–`:50`, `:51`–`:59`, `:60`–`:61`, `:62`–`:64`, `:63`–`:64`, `:65`–`:67`, `:68`, `:68` |
| I5, I6 | DEAD-before-token and comparisons: `joulewise/measurement_liveness.py:166`–`:182`; stricter chain: `:199`–`:201`; response examples: `:60`–`:68` |
| I8 | Named identity-flow branches: `joulewise/measurement_liveness.py:199`–`:201`, `:204`–`:212`, `:166`–`:182`; probe expansion: `:49`–`:68` |
| I7 | Single pathname override: `joulewise/measurement_liveness.py:23`, `:44`–`:56`; rc 0/empty UNKNOWN: `:62`–`:64`; old setting absent from current helper/caller; `/usr/bin/true` failure history: linked terminal review, Gauntlet R1 |
| R1 | Parent and expansion: `joulewise/measurement_liveness.py:71`–`:72`; registry path and suffix: `:111`–`:118`; shared-path reason: `:3`–`:7` |
| R2 | Runs-root resolution, lock, random nonce, identity fields: `scripts/run_campaign.py:3160`–`:3174`; collision: `:3175`–`:3184`; copied nonce and independent suffix: `joulewise/measurement_liveness.py:113`–`:117` |
| R3 | Exact output fields, sorted keys, newline: `joulewise/measurement_liveness.py:113`–`:117`; numbers taken from linked historical capture, other values labeled illustrative |
| R4 | Two publishers: `scripts/run_campaign.py:7281`–`:7288`, `:8246`–`:8261`; dry-run branches: `:7246`–`:7267`, `:8239`–`:8255`; other acquisitions do not call publisher: `:3572`, `:5987`, `:6176`, `:6993`, `:8125`, `:8186`; identity fallback and predicates: `joulewise/measurement_liveness.py:105`–`:110` |
| R5 | Directory and exclusive creation: `joulewise/measurement_liveness.py:111`–`:120`; write/flush/fsync and conditional partial cleanup: `:121`–`:130` |
| R6 | Finally order: `scripts/run_campaign.py:8030`–`:8035`, `:8952`–`:8957`; removal checks: `joulewise/measurement_liveness.py:83`–`:97`; missing lock irrelevant: `:211`–`:212`; no signal-handler installation anywhere in `scripts/run_campaign.py`, ordinary finally cleanup only at cited lines |
| R7 | Example device/inode comparison: `joulewise/measurement_liveness.py:88`–`:95`; diagram: R4/R6 locations; failed-write cleanup: `:125`–`:130` |
| R8 | Read-object requirement: `joulewise/measurement_liveness.py:144`–`:148`, `:205`; exact pre-probe campaign predicates: `:206`–`:212`, `:168`–`:171`; token exceptions/decisions: `:172`–`:182` |
| R9 | Gone/reused warnings and token exception: `joulewise/measurement_liveness.py:172`–`:180`; no age predicate: `:166`–`:182`; surviving-child limitation: `:5` |
| R10, R11 | Operator procedure composed here from `joulewise/measurement_liveness.py:75`–`:97` (saved identity/removal), `:204`–`:212` (classification), `:41`–`:68` (real probe); Python block supplies path restriction and warning-count check, not a separate shipped repair command; lock repair remains separate per `scripts/run_campaign.py:3175`–`:3184` and linked runsheet procedure |
| D1 | Shared parent requirement: `joulewise/measurement_liveness.py:3`–`:7`; additional JSON validation, expansion, ordering, Path deduplication: `:230`–`:235` |
| D2 | One-level iteration: `joulewise/measurement_liveness.py:235`–`:260`; missing parent: `:237`–`:240`; absent start: `:187`–`:188`; first error terminates traversal: `:229`, `:261`–`:262` |
| D3 | Single retry: `joulewise/measurement_liveness.py:215`–`:221`; entry/directory/start presence callbacks: `:246`–`:250`, `:259`–`:260`; temporary findings: `:243`–`:250`; no custody writes: `:224`–`:263` |
| D6 | Traversal flow and unsorted child enumeration: `joulewise/measurement_liveness.py:230`–`:262`; retry wrappers: `:215`–`:221`, `:246`–`:250`, `:259`–`:260` |
| D4, D5 | Diagram and all example paths/outcomes: `joulewise/measurement_liveness.py:230`–`:262`; disappearance: `:215`–`:221` |
| T1, T2 | Chain order/required checks: `joulewise/measurement_liveness.py:185`–`:201`; PID check: `:168`–`:170`; campaign checks: `:204`–`:212`; refusal precedence: `:139`–`:141`, `:272` |
| T2 marker table A, M1, M2, N, M3, L, U, D, Q, E | Respectively `joulewise/measurement_liveness.py:187`, `:189`–`:197`, `:193`, `:199`, `:168`–`:170`, `:182`, `:179`–`:181`, `:172`–`:174`, `:177`–`:178`, `:189`–`:198` |
| T3 | Probe reachability and exit arrival limits: `joulewise/measurement_liveness.py:187`–`:201` |
| T4, T5 | Registry categories: `joulewise/measurement_liveness.py:204`–`:212`, `:166`–`:182`; combination table: marker-table locations above plus `:139`–`:141`, `:261`–`:272` |
| T6 | Diagnostic prefixes and rc: `joulewise/measurement_liveness.py:266`–`:272`; shell ordering/failure: `scripts/window_status.sh:41`–`:47`; no courier override: `joulewise/measurement_liveness.py:185`–`:212` |
| T7 | Sentinel and status checkout defaults: `scripts/window_status.sh:32`–`:34`; helper checkout: `:41`–`:44`; local-only branch: `:96`–`:99`; stage/commit/push: `:99`–`:110` |
| T8 | Publish table branches: `scripts/window_status.sh:44`–`:47`, `:92`–`:110`; unhandled failures: `:30`; snapshot/coverage limits: `joulewise/measurement_liveness.py:3`–`:7`, `:47`; separate night agent check: `scripts/run_night.py:459`–`:460` |
| W1–W3 | Steps 1–8 use T2/T5 rows N, L, L, E, E, E, E, E and I4/I5; exit object: `joulewise/measurement_liveness.py:159`–`:163`; repair: R10/R11; missing/error parent: `:237`–`:240`, `:261`–`:262`; publish/refuse: `scripts/window_status.sh:44`–`:47`, `:92`–`:110` |
| Watchdog, handback, G2 pointer paragraphs | Helper call/refusal: `scripts/window_status.sh:41`–`:47`; shared custody: `joulewise/measurement_liveness.py:3`–`:7`; independent chain/campaign checks: `:185`–`:212`; operator repair: R10/R11; separate watchdog agent decisions: `scripts/run_night.py:459`–`:460` |
