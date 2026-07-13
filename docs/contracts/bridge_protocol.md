# Claude ↔ Codex Bridge Protocol

`bridge-protocol/v1`

This contract defines the task, return, scope, concurrency, continuation, and
reverse-consult protocols used when Claude and Codex collaborate on JouleWise.
Its goals are bounded authority, machine-detectable outcomes, recoverable
threads, attribution-aware workspace writes, and concise peer discussion.
Repository safety rules and lead authority remain controlling.

Provenance: co-designed by the Fable lead and gpt-5.6-sol over the MCP bridge
itself (3 rounds, 2026-07-13; thread recorded in
`docs/run_reports/2026-07-13-bridge-v1.md`).
The five in-draft choices were adjudicated by the lead at review.

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

`ROLE` MUST NOT combine implementation, independent review, and final
adjudication.

Each `WRITE_SCOPE` entry is an object with `path` and `match`. `match` is
`exact`, `subtree`, or `all`; paths are normalized repository-relative paths.
`{"path": "*", "match": "all"}` is the only whole-repository form.

A delegated worker MUST NOT infer additional scope from tests, generated
files, repository instructions, or work believed necessary for completion.

Read-only sessions (`WRITE_SCOPE: []`) MAY omit `BASELINE_MANIFEST` and
`BASELINE_DIGEST`; `BASE_HEAD` remains required.

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

The first line is the literal sentinel. The second line is one minified JSON
object with exactly these required fields:

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

Malformed or missing envelopes MUST NOT be interpreted as successful
completion, regardless of preceding prose.

For `GENRE: discussion`, the human-readable body uses this order:

1. `Positions`
2. `Disagreements`
3. `Open questions`
4. `Recommendation`

Sections with no content MAY say `None`.

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
- `host` and optional caller-supplied `pid`
- Event timestamp
- Optional `expires_at`
- Optional `note`
- For overrides: conflicting lease ids, approver, reason, and resulting
  attribution policy

Conflict detection and acquisition MUST occur under one exclusive lock:
`.codex-bridge/bridge.lock` held via a Python standard-library `fcntl.flock`
exclusive lock. The critical section reads active events, resolves stale
state, checks conflicts, appends and flushes the event, then releases the
lock.

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

Lease and thread events use separate logs and join through `invocation_id`.

Human edits remain a weak edge because a human can modify the workspace
without acquiring a lease. Whole-project audits SHOULD therefore use a pinned
clean commit or isolated worktrees, hold compatible `snapshot_read` leases,
and defer writes until adjudication.

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

`scope-check` MUST receive the prompt-supplied digest through the required
`--expect-digest sha256:...` argument, verify the manifest self-digest, and
verify equality with that external anchor before using the manifest. A missing
or mismatched anchor is `CHECK_ERROR`.

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

The consult remains one-shot because persistence would weaken independence,
invite bridge recursion, and blur decision ownership. Fable provides advice;
the top-level Codex caller adjudicates and verifies it.

Transport or protocol failure MUST return or synthesize `status: FAILED`; it
MUST NOT be consumed as peer approval.

A successful one-shot consult may end only `DISCUSSION` or `NEEDS_RULING`.
Any other well-formed child status is a protocol deviation: the adapter passes
through the child text, appends a synthesized `FAILED` envelope flagged
`protocol_deviation`, and returns `isError: true`.

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

Authoritative contract:

- `docs/contracts/bridge_protocol.md`

Tracked implementation:

- `scripts/bridge`: leases, baseline manifests, scope checks, and thread
  registry
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
