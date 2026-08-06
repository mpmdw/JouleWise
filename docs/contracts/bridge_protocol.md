# Claude ↔ Codex Bridge Protocol

`bridge-protocol/v1.1`

This contract defines the task, return, scope, concurrency, continuation, and
reverse-consult protocols used when Claude and Codex collaborate on JouleWise.
Its goals are bounded authority, machine-detectable outcomes, recoverable
threads, attribution-aware workspace writes, and concise peer discussion.
Repository safety rules and lead authority remain controlling.

Provenance: co-designed by the Fable lead and gpt-5.6-sol over the MCP bridge
itself (3 rounds, 2026-07-13; thread recorded in
`docs/run_reports/2026-07-13-bridge-v1.md`).
The five in-draft choices were adjudicated by the lead at review.

Provenance for v1.1: amendments co-designed by the lead and a Sol xhigh
consult on 2026-07-13, thread
`019f5d1d-b681-7db1-8714-812fdd2f198b`.

### Changes from v1

Version 1.1 adds the read-only discussion lane, fail-closed session wrappers,
tolerant single-line envelopes, per-call reverse-consult effort, peer channels
and bounded proposal diffs, and a single-envelope protocol-deviation path.

## 1. Prompt contract

Every delegated prompt MUST begin with a machine-readable task header: a
`BRIDGE_TASK_V1` sentinel line, one JSON object, and an `END_BRIDGE_TASK_V1`
sentinel line. JSON gives the tracked helper and future adapters one
unambiguous representation.

Required fields:

- `TASK_SHAPE`: Interaction shape; one of `interactive`, `bounded`, or
  `autonomous`.
- `GENRE`: Work genre; one of `discussion`, `implementation`, `review`, or
  `diagnosis`.
- `ROLE`: One bounded worker role or review lens.
- `OBJECTIVE`: One concrete requested outcome.
- `AUTHORITY`: Ordered authority pointers and inline rulings; highest
  authority first.
- `WRITE_SCOPE`: Exhaustive repository write allowlist; `[]` means read-only.
- `BASE_HEAD`: Full Git HEAD object id at launch.
- `BASELINE_MANIFEST`: Repository-relative path to the immutable launch
  manifest.
- `BASELINE_DIGEST`: SHA-256 of the canonical baseline manifest.
- `ACCEPTANCE`: Observable conditions required for completion.
- `VERIFICATION`: Checks or commands expected before completion.
- `EARLY_RETURN`: Permitted decision returns; normally `NEEDS_SCOPE` and
  `NEEDS_RULING`.
- `OUTPUT_PROTOCOL`: Required return protocol; `bridge-report/v1`.

`AUTHORITY` SHOULD point to durable repository sources instead of reproducing
large files. Inline context SHOULD contain only the current ruling, unstable
facts, and small controlling excerpts.

Future gate packets MUST give source line ranges for their citations. Text
labelled `verbatim` MUST be reproduced verbatim; paraphrase, ellipsis, or other
editing MUST be labelled as such rather than presented as a verbatim excerpt.

`ROLE` MUST NOT combine implementation, independent review, and final
adjudication.

Each `WRITE_SCOPE` entry is an object with `path` and `match`. `match` is
`exact`, `subtree`, or `all`; paths are normalized repository-relative paths.
`{"path": "*", "match": "all"}` is the only whole-repository form.

A delegated worker MUST NOT infer additional scope from tests, generated
files, repository instructions, or work believed necessary for completion.

Read-only sessions (`WRITE_SCOPE: []`) MAY omit `BASELINE_MANIFEST` and
`BASELINE_DIGEST`; `BASE_HEAD` remains required.

### Read-only discussion lane

For an interactive MCP turn with `GENRE: discussion` that is read-only, the
required header fields reduce to `TASK_SHAPE`, `GENRE`, `ROLE`, `OBJECTIVE`,
`AUTHORITY`, and `OUTPUT_PROTOCOL`. `WRITE_SCOPE` MAY be omitted and then means
`[]`; `EARLY_RETURN` MAY be omitted and then means `["NEEDS_RULING"]`.

`BASE_HEAD` is REQUIRED whenever the advice depends on repository state,
including code review, diagnosis, or any turn expected to carry a proposal
diff. It MAY be omitted only for repository-independent discussion.
`ACCEPTANCE`, `VERIFICATION`, `BASELINE_MANIFEST`, and `BASELINE_DIGEST` are
omitted in this lane.

The discussion context capsule SHOULD provide section-level authority anchors
rather than bare file paths; current HEAD plus dirty-path and concurrent-writer
state when repository-dependent; and the settled decisions, rejected
alternatives, and remaining challengeable questions.

A same-thread peer-channel continuation MAY use a compact delta prompt. It
inherits `ROLE`, `GENRE`, `AUTHORITY`, and `OUTPUT_PROTOCOL` from the opening
header and states only new rulings and repository changes since the previous
turn. A change of role, authority, scope, or objective class REQUIRES a fresh
full header and usually a fresh thread under §5.

The full header remains mandatory whenever `WRITE_SCOPE` is nonempty or
`TASK_SHAPE` is `autonomous`.

Compact example:

```text
BRIDGE_TASK_V1
{
  "TASK_SHAPE": "bounded",
  "GENRE": "implementation",
  "ROLE": "focused bridge-tool implementer",
  "OBJECTIVE": "Implement lease acquisition and release with focused tests.",
  "AUTHORITY": [
    "docs/contracts/bridge_protocol.md",
    "AGENTS.md",
    "User ruling: overlapping write leases hard-block by default."
  ],
  "WRITE_SCOPE": [
    {"path": "scripts/bridge", "match": "exact"},
    {"path": "tests/test_bridge.py", "match": "exact"}
  ],
  "BASE_HEAD": "0123456789abcdef0123456789abcdef01234567",
  "BASELINE_MANIFEST": ".codex-bridge/baselines/inv-123.json",
  "BASELINE_DIGEST": "sha256:0123456789abcdef",
  "ACCEPTANCE": [
    "Overlapping write leases fail unless a lead override is recorded.",
    "Release and abandoned states are distinguishable."
  ],
  "VERIFICATION": [
    "python3 -m unittest tests.test_bridge"
  ],
  "EARLY_RETURN": ["NEEDS_SCOPE", "NEEDS_RULING"],
  "OUTPUT_PROTOCOL": "bridge-report/v1"
}
END_BRIDGE_TASK_V1
```

## 2. Return envelope

Protocol layering is intentional: `claude-codex-report/v1` (D-064) remains
the canonical full session report for audited CLI runs made through
`codex-run-v3 --genre`, while `bridge-report/v1` is the lightweight final-lines
envelope REQUIRED for MCP turns and the reverse consult. An audited CLI run
carrying a valid `claude-codex-report/v1` body is exempt from the trailer.

Every successful MCP turn or reverse consult MUST end with exactly two
nonempty lines:

> `BRIDGE_REPORT_V1`
> `{"status":"DONE","summary":"Lease support implemented.","pathspec":["scripts/bridge","tests/test_bridge.py"],"verification":["python3 -m unittest tests.test_bridge: OK"],"flags":[]}`

The first line is the literal sentinel. The second line is one JSON object on
one physical line with these required fields:

- `status`: One status from the enum below.
- `summary`: Concise outcome or blocker summary.
- `pathspec`: Repository paths changed by this worker; `[]` for read-only
  turns.
- `verification`: Checks actually performed and their results, not planned
  checks.
- `flags`: Machine-consumable strings such as `route_cli`, `no_edits`, or
  `verification_incomplete`.

Statuses:

- `DONE`: The requested outcome and acceptance conditions are complete.
- `PARTIAL`: Useful bounded work is complete, but requested work remains.
- `DISCUSSION`: A read-only design or judgment turn completed.
- `NEEDS_SCOPE`: Progress requires additional write authority.
- `NEEDS_RULING`: Progress requires a lead-owned decision.
- `BLOCKED`: An external or technical prerequisite prevents progress and is
  not resolved solely by scope or a design ruling.
- `FAILED`: Execution failed or the worker cannot provide a trustworthy
  result.

The envelope is a protocol failure if its sentinel is absent, duplicated,
malformed, or not final. No non-whitespace content may follow its JSON line.
Interior whitespace on the JSON line is allowed. Unknown additional object
keys are tolerated and ignored for forward compatibility; the five required
fields and the status enum remain mandatory. Normatively, `status` and
`summary` are JSON strings, `summary` is nonempty, and `pathspec`,
`verification`, and `flags` are JSON arrays whose elements are strings.

Malformed or missing envelopes MUST NOT be interpreted as successful
completion, regardless of preceding prose.

For a substantive, multi-issue `GENRE: discussion` turn, the human-readable
body uses this order:

1. `Positions`
2. `Disagreements`
3. `Open questions`
4. `Recommendation`

Sections with no content MAY say `None`. A trivial single-question discussion
MAY answer directly without these headings. The final envelope is always
required.

## 3. Early returns

A worker MUST return early instead of guessing when authority or a lead-owned
decision is missing.

A `NEEDS_SCOPE` body MUST contain:

- `Requested paths`: Exact additional paths and match semantics.
- `Reason`: Why each path is necessary.
- `Completed`: Independent authorized work already completed.
- `Blocked work`: Work that cannot proceed without expansion.

A `NEEDS_RULING` body MUST contain:

- `Question`: One decision the lead must make.
- `Options considered`: Material alternatives and consequences.
- `Recommendation`: The worker's preferred option and reason.
- `Blocked work`: Work awaiting the ruling.

The lead SHOULD continue the same thread after answering either early return.

Scope approval is prospective only. It does not legitimize an earlier
out-of-scope write.

Before resuming with expanded scope, the lead MUST update `WRITE_SCOPE` and
atomically acquire the corresponding workspace lease or use `lease-expand` to
expand it prospectively.

## 4. Task-shape routing

Reasoning effort does not determine transport. Interaction shape does.

| Work shape | Preferred path | Examples |
|---|---|---|
| Interactive | MCP | Discussion, rulings, follow-up questions, short diagnosis |
| Bounded | MCP when short; CLI when evidence-heavy | Focused edit, narrow review, small fix round |
| Autonomous | Audited CLI | Broad audit, long test run, multi-file implementation, subagent work |
| Durable evidence required | Audited CLI | D-050/D-064 run, timeout-sensitive work, mechanically enforced scope |
| Independent review | Fresh MCP or CLI thread | Adversarial lens, final-head review, counterreview |

An xhigh discussion MAY use MCP. A long high-effort mechanical run SHOULD use
CLI.

### T3-mediated presentation, routing, and provenance

T3 is the preferred presentation plane when it is in use. It is neither a
mandatory nor an exclusive bridge plane, and it never becomes the compliance
plane. These t3-specific rules apply only to t3-mediated activity. A plain
Claude Code session remains first-class and carries no t3-specific ceremony.

For a t3-mediated invocation, the tracked provenance record MUST distinguish
four axes: `control_plane`, `transport`, `authority_class`, and `governance`
(implementation follow-on: `T3-PROV-SCHEMA-01` in
`docs/process_traces/2026-08-05-t3-amend/AMENDMENT-MAP.md`).
The selected task-shape route in the table above is the authoritative
transport record. A rollout's `session_meta.originator` MAY be recorded beside
that set only as a provenance hint. It is never the sole discriminator and
never authority-bearing. The observed values `t3code_desktop` and
`codex_cli_rs` are version-bound observations from CLI version `0.146.0`, not
a closed enum or a compatibility promise. Classification authority comes from
the §4 launch route and the lease event's §6 `owner_kind`. Absence of the
optional hint never disables a route or classification. If the hint is present,
an unknown value or a value contradictory to those authoritative fields fails
closed: it does not establish native, wrapped, delegated, top-level, approval,
or gate status.

T3 `Full access` mode is prohibited for this repository; t3-mediated work uses
only Supervised or Auto. The prohibition does not depend on an asserted
UI-to-CLI flag mapping. In Auto, phone cards are post-hoc notifications and
never approval evidence. Thread-side reports are inadmissible on approval
semantics because the model is blind to the harness approval layer. Anything
requiring Ed's eyes uses Supervised, and a claim that Supervised held or
blocked an action requires harness-event evidence rather than the thread's own
account.

T3-native Codex threads are Ed-direct only. They MUST NOT receive
lead-delegated or gate-bearing work. If their output is materially consumed,
the lead MUST append a tracked ingestion event that binds the native session
identity, output digest, lead disposition, and tracked process-trace location
(implementation follow-on: `T3-PROV-SCHEMA-01` in
`docs/process_traces/2026-08-05-t3-amend/AMENDMENT-MAP.md`). A t3 activity
marker or thread transcript alone is not that event.

The tracked Codex subagent route is limited to substantial background or
parallel Sol rounds that require operator-visible lifecycle state. It is a
thin dispatch and presentation steward, not an implementation or adjudication
authority, and the audited child ceremony remains controlling. Each wrapper
invocation counts as a subagent invocation for D-080 accounting and MUST NOT be
silently deduplicated from the child run. This conditional route is a two-arc
pilot; each arc records whether Ed used the activity view, wrapper failures,
latency, and Fable overhead before the default is retained or changed through
its owning process.

TUI operation remains available only outside `[QUIET-MAC]` work. Claim-bearing
runs use an ordinary guarded shell with zero agent sessions; t3 availability
does not relax the repository's zero-agent doctrine.

If MCP work expands beyond a short bounded turn, the worker SHOULD stop at a
safe boundary and return:

- `status: PARTIAL`
- `flags` containing `route_cli`
- A body stating completed work, remaining work, verification state, and an
  exact CLI handoff

The worker MUST NOT use routing as implicit authority to broaden scope.

## 5. Thread semantics

Continue an existing thread for:

- A ruling requested by that thread
- A prospective scope expansion
- Fixes to the same implementation
- Questions about that thread's result
- Delta review of the same worker's changes
- Completion of the same objective after a bounded interruption

Start a fresh thread for:

- A new objective or workstream
- A different role or review lens
- Independent or adversarial review
- Materially different authority or privilege
- A completed thread receiving unrelated work
- Repository assumptions too stale to repair with a compact continuation
  prompt

`resume_policy` values:

- `preferred`: Same-thread continuation preserves useful task state.
- `allowed`: Continuation is safe, but a fresh thread is also reasonable.
- `fresh_required`: Independence, changed authority, or context degradation
  requires a new thread.

Thread states:

- `pending`: MCP call started; thread id not yet returned.
- `waiting_lead`: Worker returned an early question or partial result.
- `active`: Continued work is running.
- `complete`: Objective finished.
- `abandoned`: Thread intentionally closed or superseded.
- `lost_before_return`: Blocking call ended without exposing a thread id.

Thread events MUST include:

- `schema`, `event`, `invocation_id`, and timestamp
- `thread_id`, nullable until bind
- `task`, `role`, `genre`, and `task_shape`
- `state`, `resume_policy`, and `resume_reason`
- `base_head` and `baseline_digest`
- `write_scope_digest`
- Last bridge status
- Prompt and output paths or hashes when available

Long threads degrade through stale repository facts, accumulated rejected
approaches, reduced instruction salience, and role drift. Continuation
prompts MUST restate current rulings and changed repository state rather than
assuming the old context remains current.

## 6. Workspace leases

Workspace leases are cooperative concurrency controls recorded in
`.codex-bridge/workspace-lease-events.jsonl`.

Lease events MUST include:

- `schema`: `bridge-lease-event/v1`
- `event`: `acquire`, `expand`, `release`, `abandon`, or `override`
- `lease_id`
- `invocation_id`
- `owner_id`
- `owner_kind`: `claude-thread`, `codex-mcp`, `codex-cli`, or `human`
- `access`: `write` or `snapshot_read`
- Canonical `paths`
- `base_head`
- `baseline_manifest`
- `baseline_digest`
- `task`, `role`, and optional `thread_id`
- `host`
- Optional process-identity fields `pid`, `process_start_time`, and
  `process_ancestry` (an ordered ancestry record)
- Event timestamp
- Optional `expires_at`
- Optional `note`
- For overrides: conflicting lease ids, approver, reason, and resulting
  attribution policy

`owner_kind` is an authoritative launch-route field, not a value inferred from
rollout metadata. When a t3-mediated record also carries §4 `originator`, the
two fields MUST be retained separately. Absence of the optional hint never
disables a route or classification. A present unknown or contradictory hint
cannot override `owner_kind` and fails closed for any classification that would
confer authority.

Conflict detection and acquisition MUST occur under the exclusive
`.codex-bridge/bridge.lock`, held via a Python standard-library `fcntl.flock`.
The inner critical section reads active events, resolves stale state, checks
conflicts, appends and flushes the event, then releases the lock.

Every public command that mutates bridge state -- `lease-acquire`,
`lease-expand`, `lease-release`, `lease-abandon`, `baseline`, `thread-record`,
`session-open`, and `session-close` -- MUST also acquire the exclusive
`.codex-bridge/session.lock` as its outer lock before reading bridge state.
The fixed order is always `session.lock` outer, then `bridge.lock` inner.
The wrappers hold `session.lock` across their complete ceremony and set
`BRIDGE_SESSION_LOCK_HELD=1` for every primitive subprocess they invoke; that
trusted-local delegation tells a wrapper child not to reacquire the outer lock
while still taking `bridge.lock` for its own critical sections. The environment
flag is a local lock-ownership convention, not general permission to bypass
serialization.

The read-only `lease-list`, `thread-list`, and `scope-check` commands do not
take `session.lock` when invoked standalone. A `scope-check` subprocess invoked
by `session-close` inherits the same held-lock environment convention and runs
inside the wrapper's already-held outer lock.

Overlapping active write leases hard-block acquisition.

`lease-expand --lease-id ID --paths ...` is the atomic prospective-expansion
mechanism: it preserves the lease owner and invocation, appends one `expand`
event under the same lock, never conflicts with itself, and hard-blocks paths
overlapping any other incompatible lease.

A lead MAY override a conflict explicitly. The override event MUST name the
conflicting leases, approver, reason, and timestamp. Unless isolation
otherwise proves attribution, overridden overlap makes the affected scope
check `ATTRIBUTION_INDETERMINATE`.

Malformed override events MUST be rejected before append. Any malformed
override already present makes the lease log unhealthy: conflict operations
fail closed and `scope-check` returns `CHECK_ERROR`, never `SCOPE_OK`.

Multiple `snapshot_read` leases MAY overlap when they identify the same
pinned repository state.

A write lease conflicts with an overlapping `snapshot_read` lease. This
prevents mutation beneath an audit or other stable read.

Ordinary read-only discussions need no lease unless they require a stable
repository snapshot.

Time expiry alone warns but does not abandon a lease. On the recorded host, a
missing recorded process may be marked `abandoned` under the bridge lock.
Human leases and leases without a process require explicit lead abandonment.

Stale leases become `abandoned`, never silently `released`.

No pattern-kills; kill only manifest-recorded PIDs verified by start-time + ancestry.

A t3 checkpoint revert is forbidden in the main tree. In a worktree it is a
workspace mutation: stop writers; capture the current manifest and diff;
record the intended revert; resolve every active bridge lease by explicit
release or abandonment; and perform the revert. Delegation MUST NOT resume
until a fresh invocation has acquired a fresh lease and captured a fresh
baseline. A t3 checkpoint reference is never audit evidence, and a t3
checkmark is never a bridge return envelope.

Lease and thread events use separate logs and join through `invocation_id`.

Human edits remain a weak edge because a human can modify the workspace
without acquiring a lease. Whole-project audits SHOULD therefore use a pinned
clean commit or isolated worktrees, hold compatible `snapshot_read` leases,
and defer writes until adjudication.

### Session wrappers

The preferred workspace-write ceremony layers two wrappers over the recovery
primitives above:

```text
scripts/bridge session-open --invocation-id ID --owner-id OWNER \
  --owner-kind KIND --access write --paths P... \
  [--task ... --role ... --genre ... --task-shape ... --expires-in ... --note ...]
scripts/bridge session-close --invocation-id ID --status STATUS \
  [--lease-id ...] [--expect-digest sha256:...]
```

The session wrappers support write-access sessions only in v1.1.
Snapshot-stable audits use the `snapshot_read` lease, baseline, scope-check,
and terminal lease primitives directly under §6. Read-only advice turns need
neither a lease nor a session wrapper.

`session-open` MUST execute `lease-acquire`, `baseline`, and
`thread-record --state pending` in that order and fail closed. If baseline
capture, thread recording, or receipt creation fails after acquisition, it
MUST abandon the lease with a recorded reason before returning nonzero. A hard
process crash MAY leave the lease active; explicit recovery is then required.
The invocation-id uniqueness check and the complete open ceremony are
serialized by `session.lock`. Before acquiring a lease, `session-open` MUST
refuse an invocation id already present in receipts, baseline manifests, the
lease log, or the thread log. Every fresh attempt requires a new invocation
id, including recovery after an abandoned pre-receipt attempt.

On success it MUST create, without overwrite, an immutable
`.codex-bridge/receipts/<invocation-id>.json` receipt with schema
`bridge-session-receipt/v1`. The receipt binds the invocation and lease ids,
base HEAD, baseline manifest and digest, canonical write-scope path specs and
their digest, owner, and timestamps. An existing receipt is a hard error; a
fresh attempt requires a fresh invocation id. Standard output contains the
receipt plus a `header_fragment` with `BASE_HEAD`, `BASELINE_MANIFEST`,
`BASELINE_DIGEST`, and `WRITE_SCOPE` ready for the task header.

`session-close` MUST serialize its entire body under `session.lock`, beginning
before receipt, lease, or terminal-thread reads and ending after its final
output. After taking the lock it re-reads terminal state. It MUST load the
receipt-bound lease's current canonical paths from the authoritative lease
event chain, independently validate the receipt binding, and verify that the
receipt scope is a subset of the current lease scope; a mismatch is a
`CHECK_ERROR`-style hard error. Close scope is therefore the receipt scope plus
recorded prospective `lease-expand` events on that same lease. The wrapper
passes those current paths and their canonical digest to `scope-check` and to
the closing thread event.

The receipt's stored baseline digest, or an explicitly supplied
`--expect-digest`, is the only external digest anchor; the wrapper MUST NOT
rediscover an expected digest from the manifest being checked. It handles
outcomes as follows:

- For `SCOPE_OK` with `DONE`, it records `complete` and the last bridge
  status, then releases the lease.
- `session-close` refuses `--status DISCUSSION` unconditionally with a hard
  error: no terminal thread event is appended and the lease is retained.
  Advice turns use the read-only discussion lane without wrappers.
- For `NEEDS_SCOPE`, `NEEDS_RULING`, `PARTIAL`, `BLOCKED`, or `FAILED`, it
  records `waiting_lead` and the actual bridge status and retains the lease.
  Scope-check still runs; a non-OK verdict still exits nonzero.
- For `SCOPE_VIOLATION`, `ATTRIBUTION_INDETERMINATE`, or `CHECK_ERROR`, it
  records the verdict in a `waiting_lead` thread event, retains the lease, and
  exits nonzero. A non-OK verdict never causes automatic release; release or
  abandonment after adjudication is an explicit lead action.

Closing is idempotent for every outcome. If the most recent thread event
already records the same state, last bridge status, current scope verdict, and
current canonical write-scope digest, and the lease disposition is unchanged,
another close is a no-op notice with the exit status that outcome normally
has. A changed scope digest requires a new event even when the other fields
match. A different status against an existing `complete` event is refused, and
the wrapper MUST never append a contradictory terminal event. Standard output
reports the scope-check verdict, recorded thread state, and observed lease
disposition. Close observes the receipt-bound lease before validating optional
argument consistency where possible, and after any subsequent error performs a
best-effort locked re-read; errors therefore report the current `active` as
`retained`, `released`, or `abandoned` state rather than a stale or unknown
disposition.

## 7. Baseline and scope check

Before every workspace-write session, `scripts/bridge baseline` MUST create
an immutable baseline manifest.

`baseline` MUST refuse an existing invocation id and manifest path; every
fresh capture requires a new invocation id.

The manifest MUST contain:

- Schema version and invocation id
- Repository root and Git common directory
- Capture timestamp
- Full HEAD object id
- Base64 representation of raw `git status --porcelain=v2 -z
  --untracked-files=all`
- Base64 representation of raw `git ls-files --stage -z`
- For each baseline-dirty or untracked path:
  - Repository-relative path
  - Entry type
  - File mode
  - Content SHA-256, symlink-target hash, or submodule object id as
    applicable
- Canonical manifest SHA-256

Canonical JSON uses UTF-8, sorted keys, compact separators, and no
insignificant whitespace. Raw NUL-delimited Git output is base64-encoded so
arbitrary records remain lossless.

The prompt MUST provide `BASE_HEAD`, `BASELINE_MANIFEST`, and
`BASELINE_DIGEST`.

A future native-write acceptance-gate exercise MUST be predeclared before the
write. Its evidence MUST bind the native session identity and authoritative
launch route to the governing manifest, baseline digest, declared scope,
output digest, and resulting artifact or commit. A later narrative or
retroactive route designation cannot establish the gate. This requirement is
forward-looking; it does not reopen the one previously accepted exercise:
commit `97d6e3d`, the isolated one-file `RUN_STATE.md` native-write gate exercise
recorded in `RUN_STATE.md`'s T3 gate/probe log and accepted in
`docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md` under
“Acceptance-gate dispositions.”

`scope-check` MUST receive the prompt-supplied digest through the required
`--expect-digest sha256:...` argument, verify the manifest self-digest, and
verify equality with that external anchor before using the manifest. A missing
or mismatched anchor is `CHECK_ERROR`.

When `scope-check` is invoked through `session-close`, that external anchor
comes from the immutable open receipt (or an explicit close argument), never
from the manifest being validated.

After a workspace-write session, `scripts/bridge scope-check` compares
persistent path-state changes against the baseline, declared scope, and lease
history.

Verdicts:

- `SCOPE_OK`: Every persistent attributable delta is within declared scope;
  no attribution-invalidating overlap or state change exists; and one active
  or properly released write lease, selected by matching invocation id or an
  explicit `--lease-id`, covers the complete declared scope. Without that
  governing lease the verdict is `ATTRIBUTION_INDETERMINATE` with reason
  `no_governing_lease`.
- `SCOPE_VIOLATION`: At least one persistent attributable delta is outside
  declared scope, or the worker made an unauthorized HEAD change. Violating
  paths and reasons are listed.
- `ATTRIBUTION_INDETERMINATE`: The checker observes relevant changes but
  cannot attribute them soundly because of overlapping writers, unexplained
  repository movement, an invalid baseline relationship, or equivalent
  ambiguity. Candidate paths and reasons are listed.
- `CHECK_ERROR`: The checker could not acquire required state, parse the
  manifest or logs, or complete Git inspection. The result MUST NOT be
  accepted.

Known concurrent leases with provably non-overlapping scopes do not
invalidate attribution.

HEAD movement rules:

- If commits were not explicitly authorized, worker-owned HEAD movement is
  `SCOPE_VIOLATION`.
- If commits were authorized and ownership is proven, committed and remaining
  worktree deltas are scope-checked normally.
- If HEAD movement is external, concurrent, or unexplained, the verdict is
  `ATTRIBUTION_INDETERMINATE`.
- No HEAD movement may produce `SCOPE_OK` merely because the final worktree
  is clean.

Scope checking proves final persistent state only. It cannot detect an
out-of-scope file modified and restored before the final snapshot.

Git-visible checking also does not prove the history of ignored files or
writes outside the repository.

`.codex-bridge/**` is bridge-internal state exempt from task `WRITE_SCOPE`,
but only `scripts/bridge` and bridge launchers may write it. This is a
protocol boundary, not filesystem enforcement.

## 8. Reverse consult: `consult_fable`

`consult_fable` is available only to a top-level Codex lead for one bounded,
read-only peer judgment.

In the represented steady state, top-level status is established by the
authoritative §4 launch route and §6 `owner_kind`; the optional §4 `originator`
hint cannot establish or elevate that status. Its absence never disables a
consult, while a present unknown or contradictory value fails closed.

**Normative rule.** Only an actually top-level Codex lead may invoke a reverse
consult; a Claude-originated or delegated session is ineligible.

**TRANSITIONAL — convention, not enforcement.** Until the four-axis provenance
record, including its `authority_class` field, is representable through the
implementation follow-on `T3-PROV-SCHEMA-01` in
`docs/process_traces/2026-08-05-t3-amend/AMENDMENT-MAP.md`, the adapter has no
authoritative signal for the caller's launch route or delegated status: it
validates only the caller-supplied `BRIDGE_ORIGIN: codex` and
`BRIDGE_HOPS_REMAINING: 0` lines, which neither prove top-level status nor
create authority. **Mechanical acceptance of the caller-supplied header tuple is
not proof of top-level status and does not establish reverse-consult
authority.** During the transition the normative rule is therefore a
best-effort convention, not a mechanically enforced eligibility test: a caller
known or visibly marked delegated MUST NOT invoke, and a *present* unknown or
contradictory delegated/origin marker fails closed — but wholly-absent status
does not disable the consult (mirroring the §4 provenance rule; see §9,
"Convention versus enforcement," for which properties are mechanically enforced
versus convention-bound). **Fail closed at consumption:** a transitional
consult result is non-authority-bearing advice — it cannot prove caller
eligibility, satisfy an independent-review or approval requirement, establish
gate status, expose privileged data, or displace lead adjudication. The
transition ends only when `T3-PROV-SCHEMA-01` both represents the four-axis
record (including `authority_class`) AND makes admission consume the
authoritative §4 launch-route and §6 `owner_kind` evidence with rejection
tests; merely defining or persisting the schema does not end it. Once that
lands, the authoritative §4/§6 record supersedes this transitional convention.

The caller's prompt MUST begin with:

```text
BRIDGE_ORIGIN: codex
BRIDGE_HOPS_REMAINING: 0
```

The request MUST provide:

- `Decision question`
- `Current Sol position`
- `Alternatives`
- `Evaluation criteria`
- `Settled constraints`
- `Authority order`
- `Repository pointers`
- `Requested counterargument`
- `Requested output shape`

Large repository context SHOULD be supplied as exact file pointers because
Fable has read/search access.

The adapter MUST:

1. Validate the caller-supplied bridge headers.
2. Reject a Claude-originated or nonzero-hop request.
3. Strip the caller headers.
4. Inject one canonical header and the read-only peer role.
5. Launch Fable with the configured read-only, no-MCP, no-persistence
   boundary.
6. Require a `bridge-report/v1` return envelope.

The adapter MUST NOT pass duplicate origin headers to Fable.

The tool input MAY include `effort`, whose only accepted values are `high` and
`xhigh`. Unsupported values are rejected with a synthesized `FAILED`
`protocol_failure` envelope and are never silently coerced; `ultra` is not
exposed. The process default comes from `CLAUDE_BRIDGE_EFFORT` only when that
environment value is `high` or `xhigh`; every other value falls back to
`high`. The effective default remains `high` to bound latency under the tool
timeout.

For reproducibility, the adapter MUST pass the selected effort explicitly and
prefix returned child-result text with `[consult effort: <effort>]` as its
first line. This prefix precedes the child output; the envelope-final rule
still binds the end of the combined text.

The consult remains one-shot because persistence would weaken independence,
invite bridge recursion, and blur decision ownership. Fable provides advice;
the top-level Codex caller adjudicates and verifies it.

Transport or protocol failure MUST return or synthesize `status: FAILED`; it
MUST NOT be consumed as peer approval.

A successful one-shot consult may end only `DISCUSSION` or `NEEDS_RULING`.
Any other well-formed child status is a protocol deviation: the adapter strips
the child's trailing sentinel and JSON line, passes through the remaining
child text, names the claimed status in diagnostic prose, and appends one
synthesized `FAILED` envelope flagged `protocol_deviation`. The returned text
therefore contains exactly one sentinel, and the adapter returns
`isError: true`.

## Peer channels and proposal diffs

A peer channel is a long-lived `GENRE: discussion` thread scoped to one
coherent design objective or workstream. A new objective, changed role, or
independent or adversarial review requires a fresh thread under §5. A peer
channel MUST NOT be presented or counted as independent review.

A `DISCUSSION` turn MAY carry a proposal diff as a unified diff in its body.
The proposal is advice, not a write: the worker's `pathspec` stays `[]`, no
workspace lease or baseline is involved, and the lead applies it at the bench
and owns verification. The applying session MUST keep a durable run report or
equivalent change record containing the thread id, the proposal diff or its
SHA-256, the `BASE_HEAD` revision anchor, the proposer, changes the lead made
while applying it, and the verification performed. A commit-message citation
supplements but never substitutes for that durable record.

Proposal diffs are bounded in aggregate per objective, not per turn, to about
three files and 200 changed lines. Splitting a larger implementation across
nominal discussion turns is prohibited. Regardless of size, generated
artifacts, dependency or lock files, migrations, renames, broad mechanical
rewrites, and security- or concurrency-sensitive implementation MUST route to
a leased write session. The governing test is whether the lead can fully
understand, apply, and verify the proposal at the bench without effectively
rubber-stamping delegated implementation.

## 9. Known limitations

- Lost blocking calls: Claude records `pending` before MCP invocation, but if
  the call is lost before return, its Codex thread id may be unrecoverable.
  Record `lost_before_return`; do not guess by timestamp.
- Correlated reviewers: Sol and Fable are not statistically independent
  evidence sources. Shared training, shared repository context, and shared
  prompt framing can correlate errors.
- Transient-write blindness: Final-state scope checks cannot detect files
  modified and restored during the invocation.
- Human lease non-compliance: A human or ungoverned process may edit without
  acquiring a lease, defeating cooperative attribution.
- Ignored and external writes: Git-based manifests do not comprehensively
  observe ignored files, external paths, or side effects in external systems.
- Convention versus enforcement: Prompt and envelope rules are mechanically
  validated only where a helper or adapter performs validation.
- Installed MCP ceiling: The project does not control `codex mcp-server`
  internals, so adapter-level persistence of a not-yet-returned thread id is
  unavailable.

## 10. Implementation and consumption pointers

### Clause-by-clause consumption inventory

This inventory is the deduplication boundary. A `pointer` consumer names the
canonical home but does not restate its procedure. An `enforcement` consumer
keeps the applicable boundary text locally because prompt text is part of the
guard. Configuration and invocation identify how to enter the bridge; they do
not become alternate wire contracts.

| Clause | Canonical home | Consumer treatment |
|---|---|---|
| Effort selection | `.claude/skills/codex/SKILL.md` §Effort selection | `CLAUDE.md`, the Claude agent, and the `/codex` command point to the skill; they do not repeat triggers. |
| Claude-to-Sol operating sequence and config override shape | `.claude/skills/codex/SKILL.md` §Primary MCP path | The agent and command invoke the skill; `CLAUDE.md` supplies clean-clone discovery only. |
| Full and discussion prompt headers | Contract §1 | Pointer only outside the contract; exhaustive scope remains an explicit enforcement boundary. |
| MCP and audited-CLI return envelopes | Contract §2 | Pointer only outside the contract; failure-is-not-success remains an explicit enforcement boundary. |
| Scope and ruling early returns | Contract §3 | Pointer only outside the contract; `AGENTS.md` retains receiver stop/ask rules. |
| MCP-versus-CLI routing | Contract §4 | The operating skill performs the selection by reference to §4. |
| Thread reuse, independence, and peer-channel continuity | Contract §§5 and 8 | Pointer only outside the contract; callers retain only the invocation fact that a returned thread can be continued. |
| Leases, wrappers, baselines, and scope checks | Contract §§6-7 | Pointer only outside the contract; invocation docs may name the wrapper command but do not restate state transitions. |
| Reverse-consult request, adapter, and status rules | Contract §8 | `CLAUDE.md` and the reverse skill point here; the reverse skill remains a receiver boundary outside WO-020 by lead ruling. |
| Proposal-diff eligibility, ceiling, and provenance | Contract §8 | Pointer only outside the contract. |
| Exhaustive write scope | Contract §§1, 3, and 7 | Explicit canonical enforcement snippet at every WO-020 in-scope entry surface; `AGENTS.md` keeps its fuller receiver rules. |
| Quiet-machine exclusion | Repository machine-state policy plus contract safety boundary | Explicit canonical enforcement snippet at every WO-020 in-scope entry surface. |
| Sandbox and approval bypass prohibition | Repository safety policy | Explicit canonical enforcement snippet at every WO-020 in-scope entry surface. |
| One-hop prohibition | Contract §8 plus adapter boundary | Explicit canonical enforcement snippet at every WO-020 in-scope entry surface. |
| Envelope failure is not success | Contract §2 | Explicit canonical enforcement snippet at every WO-020 in-scope entry surface. |

Surface disposition is therefore:

| Surface | Invocation/configuration retained | Normative policy form |
|---|---|---|
| `CLAUDE.md` | Clean-clone MCP and audited-CLI discovery | Contract/skill pointers plus canonical enforcement snippets |
| `AGENTS.md` | Receiver authority and repository intake | Contract/skill pointers plus canonical enforcement snippets and fuller receiver rules |
| `.claude/agents/codex.md` | Agent role and handoff | Contract/skill pointers plus canonical enforcement snippets |
| `.claude/commands/codex.md` | Slash-command dispatch | Contract/skill pointers plus canonical enforcement snippets |
| `.claude/skills/codex/SKILL.md` | Effort policy and operating sequence | Operating home; wire details remain contract pointers; canonical enforcement snippets stay local |
| `.agents/skills/claude-consult/SKILL.md` | Reverse-consult invocation | Receiver boundary pointing to contract §8; previously excluded from WO-020 edits by lead ruling, then amended by T3-AMEND-01 |

### Canonical enforcement snippets

The following manifest defines the snippets before any byte-identity check is
applied. Each listed consumer MUST contain each snippet exactly once as plain
UTF-8 prose. Changes begin here, then propagate atomically to every listed
consumer. Explanatory policy must not be added around these snippets as a new
normative home.

<!-- BEGIN BRIDGE CONSUMER DRIFT MANIFEST -->
```json
{
  "schema": "bridge-consumer-drift/v1",
  "snippets": {
    "scope_authority": "`WRITE_SCOPE` is exhaustive; never infer additional scope from tests, generated files, repository instructions, or work believed necessary for completion.",
    "quiet_mac": "Never start or continue a `[QUIET-MAC]` measurement while an agent session is active.",
    "no_bypass": "Never use `danger-full-access` or sandbox/approval bypass flags.",
    "one_hop": "Bridge depth is one hop: a Claude-originated Sol session must not call Claude by MCP, `claude -p`, or any other launcher.",
    "envelope_failure": "A missing, duplicated, malformed, or non-final required envelope is protocol failure, never success."
  },
  "consumers": {
    "CLAUDE.md": ["scope_authority", "quiet_mac", "no_bypass", "one_hop", "envelope_failure"],
    "AGENTS.md": ["scope_authority", "quiet_mac", "no_bypass", "one_hop", "envelope_failure"],
    ".claude/agents/codex.md": ["scope_authority", "quiet_mac", "no_bypass", "one_hop", "envelope_failure"],
    ".claude/commands/codex.md": ["scope_authority", "quiet_mac", "no_bypass", "one_hop", "envelope_failure"],
    ".claude/skills/codex/SKILL.md": ["scope_authority", "quiet_mac", "no_bypass", "one_hop", "envelope_failure"]
  }
}
```
<!-- END BRIDGE CONSUMER DRIFT MANIFEST -->

Authoritative contract:

- `docs/contracts/bridge_protocol.md`

Tracked implementation:

- `scripts/bridge`: session wrappers, leases, baseline manifests, scope checks,
  and thread registry
- `.codex-bridge/receipts/`: immutable local session-open receipts
- `scripts/codex-bridge` + `scripts/codex-app-bridge.mjs`: audited
  Claude-to-Sol script route and optional desktop-owned turn transport; the
  latter is what gives the native pet real running-conversation state
- `scripts/claude-bridge-mcp.mjs`: guarded reverse consult
- `.mcp.json`: Claude-to-Codex server configuration
- `.codex/config.toml`: Codex-to-Fable server registration
- `scripts/codex-bridge`: audited tracked CLI bridge
- `tests/test_bridge.py`: focused bridge state and scope tests
- `tests/test_claude_bridge_mcp.py`: reverse-adapter tests

Claude-side consumers:

- `.claude/skills/codex/SKILL.md`
- `.claude/agents/codex.md`
- `.claude/commands/codex.md`
- `CLAUDE.md`

Codex-side consumers:

- `AGENTS.md`
- `.agents/skills/claude-consult/SKILL.md`

Orchestration and audited-wrapper consumers:

- `docs/orchestration.md`
- `~/.local/bin/codex-run-v3` when installed

Repository-local pointers SHOULD summarize and link this contract rather than
duplicate its normative rules.
