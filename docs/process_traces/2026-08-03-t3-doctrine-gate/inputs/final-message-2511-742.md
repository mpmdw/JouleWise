# Final assistant message — thread 2511-7420-b623-a7ffa1950d44

Source rollout: /Users/edr/.codex/sessions/2026/08/03/rollout-2026-08-03T20-11-23-019fcac1-2511-7420-b623-a7ffa1950d44.jsonl
sha256: 16b03d0381747a4599906d100dde4f13d822f4c4fafe086417cc1628b54f7e99

---

## Positions

T3 should be the presentation/control plane, never the compliance plane. Activity, checkpoints, shell streams, and phone approvals improve supervision; envelopes, leases, manifests, scope checks, and gauntlet results remain authoritative.

### Ranked adaptations

| Rank | Adaptation | Benefit / effort | Position |
|---|---|---|---|
| 1 | Visibility-aware routing and correlated activity names | Very high / **small** | Add operator visibility to §4 routing, while retaining the adopted four axes. |
| 2 | One mutating process stage per T3 turn | Very high / **bench** | Align fix rounds and decision-bearing gauntlet stages with checkpoints. |
| 3 | Separate UI state from governance state; fence checkpoint reverts | Very high / **small** | Prevent visible completion or convenient revert from bypassing audit/leases. |
| 4 | Tier lenses between in-process activities and sibling threads | High / **bench**, audited sibling adapter **WO** | Use sibling threads only where independence/full visibility earns the ingestion cost. |
| 5 | Event-derived fleet status in the lead thread | High / **bench**; optional watcher **small** | Replace routine `ps`/mtime inspection, but retain it as recovery forensics. |
| 6 | Hash-bound approval-wave cards | Medium-high / **bench**; executor **WO** | Batch semantic authorization, without batching scope or lease authority. |
| 7 | Sealed, lead-mediated packet exchange | Medium / **small** specification; helper **WO** | Useful for cold/sibling handoffs; explicitly not a peer chat channel. |
| 8 | Bidirectional polled peer inbox | Negative / **do not build** | It obscures authority, consumption, wake state, and failure recovery. |

### 1. Routing and route (b)

Visibility should become an explicit §4 selection input, but not a fifth authority axis and not another meaning for `owner_kind`. Add:

- `operator_visibility_required`: `none | lifecycle | shell_stream | full_turn`
- Resolved `visibility_class`: `opaque_process | subagent_lifecycle | full_turn`
- `checkpoint_coverage`: `thread_worktree | external_worktree | none`

Record these beside the adopted `control_plane`, `transport`, `authority_class`, and `governance` fields. If T3 exposes stable thread/activity identifiers, bind them to `invocation_id`; otherwise leave them null—never infer them by timestamps.

Route (b) should be the default for substantial **background or parallel** delegated rounds launched from a Claude lead thread, not for every substantial call:

- Interactive/short: direct MCP.
- Single foreground evidence-heavy run: audited CLI/Bash remains cheaper and its shell is attachable.
- Background/parallel audited round needing phone-visible lifecycle: tracked Claude `codex` subagent wrapping the audited CLI.
- Full native Codex sibling: full UX, but governed-ingestion advisory only and never gate-bearing under the adopted authority ceiling.

The route-(b) subagent should be a thin dispatch/presentation steward, not a stream director: receive an immutable prompt/receipt, launch one audited ceremony, report lifecycle and pointers, and make no implementation or adjudication decisions. Correlate:

`T3 activity → bridge invocation → lease → Sol session → envelope → consumption event`

This avoids reviving the expensive subagent-director topology rejected in [orchestration](/Users/edr/code/JouleWise/docs/orchestration.md:285).

The cost is real: an extra Fable invocation, extra context, another failure layer, and additional spend/cadence accounting. It must count as a subagent invocation under current policy; do not silently deduplicate it from D-080. Pilot the conditional default for two arcs and record whether Ed actually used the activity view, wrapper failures, latency, and Fable overhead.

### 2. Turn/checkpoint alignment

Adopt this rule:

> One T3 turn may contain at most one mutating fix round or decision-bearing gauntlet stage, and no background writer may survive the turn boundary.

Read-only lenses may run concurrently inside one turn. Do not manufacture empty turns for every test command.

Every stage ends with a compact receipt containing:

- `stage_id` and invocation IDs
- Worktree and base/end HEAD
- Lease disposition and scope verdict
- `checkpoint_coverage`
- Diff or patch digest when the worktree is external
- Verification and next gate

For multi-worktree work, the native checkpoint is complete only when the T3 thread is rooted in that worktree. Otherwise it is merely the lead workspace’s checkpoint; emit a content-addressed stage diff for the external worktree. A checkpoint must never be cited as D-064 evidence.

T3 revert is a human/control-plane mutation. Require writers to stop, resolve active leases, capture the current manifest/diff, record the revert, and rebaseline before delegation resumes.

### 3. Fleet view

The lead thread’s Activity stream becomes a good fleet dashboard once substantial background work uses labeled subagent activities. It covers that thread’s fleet, not sibling threads.

A long-lived conversational “operations agent” cannot replace cross-thread evidence because it cannot observe sibling activity natively. Prefer:

- State-transition `STATUS_V1` lines in the controlling lead thread at dispatch, worker finish, envelope validation, consumption, wait, and failure.
- For cross-thread fleets, an optional operations thread hosting a dumb shell watcher over the common-dir epoch bookkeeper and canonical bridge events.
- Output only transitions and alerts: unmatched starts, retained leases, `waiting_lead`, malformed envelopes, and finished-but-unconsumed runs.
- Keep `ps`/mtime inspection as crash/recovery forensics.

The important visible distinction is:

`RUNNING → WORKER_FINISHED_UNVALIDATED → SCOPE_OK → CONSUMED → GATE_ACCEPTED`

T3 Activity can prove only the early lifecycle states.

### 4. Phone approvals

Use one semantic approval card per merge or permission wave, binding:

- Exact PR/head SHAs and expected base
- Ordered actions
- Plan SHA-256
- Lease/scope effects
- Stop-on-mismatch conditions
- Recovery path

One phone approval may authorize that fixed wave, but it does not combine contract §6 obligations. Each delegated invocation retains its own session ceremony; scope expansions remain prospective; lease conflicts and overrides remain explicit; and any changed head or failed gate stops the wave.

Do not concatenate opaque shell commands merely to reduce prompts, and never interpret a T3 permission approval as merge, scope, methodology, or ruling authority. Supervised/Auto remain the only permitted modes; Full access stays prohibited.

A declarative wave executor is a **WO**, not a quick convenience tool: [orchestration §8](/Users/edr/code/JouleWise/docs/orchestration.md:240) requires a named failure, budget, applicability predicate, and retirement condition.

### 5. Lens placement

- Routine/light lenses: in-process Claude subagents. They are already live-visible and cheapest to consume.
- Substantial Sol review/fix rounds: conditional route (b), preserving the audited child run.
- Independent/final-head lenses: fresh audited instances, still represented as separate visible activities.
- Cold Fable gate or D-080 sweep: a fresh sibling T3 Claude thread is worthwhile for independence and full visibility only after it receives a sealed mechanical packet and its start, output hash, status, and lead consumption are recorded in the tracked manifest.
- Native T3 Codex sibling: supplemental exploratory/design lens only. Material conclusions require governed ingestion; it does not satisfy a cold gate, mandatory rotating lens, final-head review, or merge license.

Until a sibling-thread audit adapter exists, the existing audited cold launcher remains the gate-bearing route.

### 6. Filesystem communication

Do not build `.codex-bridge/peer-inbox/` as a polled chat bus. Polling supplies no wake guarantee and creates stale-message, dual-writer, authority-bypass, and unaudited-conversation failure modes.

Keep only a sealed, one-shot packet exchange:

- Content-addressed immutable request
- Explicit sender, recipient authority class, objective, base HEAD/worktree, expiry, and prompt digest
- One immutable response bound to the request
- `NEEDS_SCOPE` and `NEEDS_RULING` return to the lead
- Lead-authored consumption/disposition event
- Tracked process-trace pointer whenever materially consumed

Raw packets may live under `.codex-bridge/`; D-064 compliance still requires the tracked pointer/event surface described in [D-064](/Users/edr/code/JouleWise/docs/decision_log.md:3304).

## Disagreements

- Route (b) is not full Sol visibility: it exposes subagent lifecycle and a nested shell, not Sol’s internal activities.
- A T3 checkmark is not a valid envelope, scope verdict, consumption event, or gate result.
- Hidden checkpoint refs are not audit evidence and their revert affordance is not lease-safe by default.
- A general operations thread cannot infer sibling health from per-thread Activity.
- A native Codex sibling does not become gate-bearing merely because Ed can see more of it.
- Phone batching must not collapse lease, scope-expansion, or adjudication boundaries.
- A direct peer inbox would weaken the deliberately lead-mediated topology.

## Open questions

None blocking. The two provisional calibration points are route-(b) Fable overhead/value after two arcs and whether cross-thread concurrency becomes frequent enough to justify the small fleet watcher.

## Recommendation

Land the adaptations in three increments:

1. **Bench:** stage-per-turn discipline, labeled lifecycle statuses, conditional route-(b) policy, lens-tier placement, and hash-bound approval cards.
2. **Small:** route/manifest visibility fields, activity-to-invocation correlation, checkpoint coverage, and recorded revert safety.
3. **WO only after evidence:** sibling-thread audit adapter, fleet watcher, packet helper, or approval-wave executor.

This extracts T3’s visibility and phone ergonomics while keeping [bridge envelopes and leases](/Users/edr/code/JouleWise/docs/contracts/bridge_protocol.md:132), WRITE_SCOPE, D-050/D-064 auditability, and every gauntlet layer authoritative.

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Ranked a T3-aware bridge adaptation set: visibility-aware routing with conditional route-(b), stage-aligned turns, governance-safe checkpoints and approvals, tiered sibling use, event-derived fleet status, and rejection of a polled peer inbox.","pathspec":[],"verification":["Read bridge_protocol.md §§1-10, .claude/skills/codex/SKILL.md, .claude/agents/codex.md, docs/orchestration.md invocation-manifest/topology/guardrails, and decision log D-050/D-064/D-080","Verified repository HEAD equals BASE_HEAD 0182962ef49beb558fd0403dc10ba73213077e2d","Read-only discussion; no files changed"],"flags":["no_edits","terminal_hop","t3_ux_review"]}
