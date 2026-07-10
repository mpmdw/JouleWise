# DOC-008: Process Architecture v2, Stage 1 — State Kernel

Status: ADJUDICATED 2026-07-09 (C-028) — rulings in `ADJUDICATION.md` in this directory AMEND this spec wherever they conflict with its body text

Authority: D-063 (binding architecture and staging), D-061 (process-layer evaluation semantics), C-027 review §5-Q1 and disposition table, C-027 counterreview position Q1, and `docs/reviews/c027/lens-meta.md` findings 1, 5, 8, and 9 plus its design-judgment table. Where this draft makes a migration choice not fixed by those authorities, it labels the choice as design judgment.

Purpose: make work-selection state a single hand-edited, machine-readable source and make the two current next-work views deterministic projections of that source. This is the smallest vertical slice that closes the demonstrated same-day `RUN_STATE.md` drift without attempting D-063 Stage 2 ledgers or later semantic policy-document generation.

## 1. Binding outcomes, premise corrections, and fences

### 1.1 Required outcomes

DOC-008 is complete only when all of the following are true:

1. `docs/process/state_kernel.json` is the only editable source for live task ordering, lane, queue status, dependencies, task authority, task acceptance, and active stop-card pointers.
2. `scripts/gen_state.py` deterministically generates the `RUN_STATE.md` intake/restart region and the `TASK_QUEUE.md` Current Queue region.
3. CI fails when the kernel is invalid, non-canonical, or either generated region differs by one byte from generator output.
4. `RUN_STATE.md` contains one restart surface. It has no second “What Is Next,” historical session list, cleared-stop-card narrative, or prior verification history.
5. The live queue contains only nonterminal task records. The six completed rows currently mixed into Current Queue are moved, without substantive rewriting, to the existing Completed Queue Items table.
6. `docs/planning_reflection_protocol.md` is a redirect stub; its useful task fields live in the kernel and its procedural/reporting duties live in their existing owners.
7. `docs/orchestration.md` contains the exact two-writer and credential-boundary procedures in §7.
8. `PROJECT_STATUS.md` is compacted by the lead to the structure in §8, with historical update prose moved to `docs/project_status_history.md`.
9. `docs/agent_playbook.md`, `AGENT_PLAN.md`, and `README.md` no longer require the retired reflection protocol or repeat conflicting intake rules.

### 1.2 Premise corrections and authority reconciliation

- `E0` and `E1` are display ranks, not machine-state lanes. Both map to `[ED-EXTERNAL]`. The three lanes remain `[AGENT]`, `[QUIET-MAC]`, and `[ED-EXTERNAL]`.
- D-023 and D-063 are compatible only if kernel `status` is queue/work-selection state, not phase-item completion state. Exit checklists remain the only authority that a phase item is complete. A completed task leaves the live kernel only after its acceptance pointer/checklist supports closure.
- `P2-006` is labeled `UNBLOCKED` while its row says it runs after P2-015. “Implementation-unblocked” is not “ready to execute.” Migration normalizes it to `blocked` until P2-015 closes; the old nuance may remain in `status_note`.
- Current display rank `1` for P2-015 precedes `1a` for P2-015-SMOKE even though the smoke must happen first. Lane-local ranks put the smoke first.
- `REPRO-001` names `[AGENT prep, ED-EXTERNAL tail]`, violating the one-lane task invariant. Stage 1 assigns environment-lock/pack-prep work to `REPRO-001` `[AGENT]` and makes existing `P2-027` `[ED-EXTERNAL]` own publication and uninvolved-party re-reduction.
- `P2-004` and `P2-005` lack explicit lane tags. Migration assigns both to `[AGENT]`; P1-001 and P1-006 remain external closure/live-promotion gates. These are migration inferences for lead adjudication.
- Retiring the reflection protocol is not an automatic “zero catches means delete” application. D-061 forbids that shortcut. D-063 records the council’s explicit adjudication after four observed exposures.
- D-050’s visible stop-card override remains in `RUN_STATE.md`, but D-063 makes the visible wrapper generated from a kernel pointer. Rich stop-card content moves to a dedicated referenced Markdown file.

### 1.3 Fences

- Do not edit, compact, reorder, or generate content in `docs/decision_log.md` or `docs/council_log.md`.
- Do not rewrite dated run reports, completed-task evidence, decision history, council history, or Git history.
- Do not implement D-063 Stage 2 findings/invocation ledgers and do not generate `current_policy.md`.
- Do not generate any part of `PROJECT_STATUS.md`. Its compacted current content remains lead-authored.
- Do not treat fixture or mock evidence as hardware validation, remove PROVISIONAL labels, or run `[QUIET-MAC]` measurements while implementing DOC-008.
- Do not hand-edit text between generated markers. Missing or invalid markers are fatal.

## 2. Kernel architecture and file targets

### 2.1 File targets

| File | Stage-1 role |
|---|---|
| `docs/process/state_kernel.json` | One hand-edited live-state kernel for all lanes. |
| `docs/process/state_kernel.schema.json` | Draft 2020-12 editor/tooling schema; no runtime `jsonschema` dependency. |
| `docs/stop_cards/README.md` | D-050 stop-card template and lifecycle. Future rich cards live as `docs/stop_cards/<card-id>.md`. |
| `scripts/gen_state.py` | Stdlib-only validation, canonicalization, rendering, marker replacement, and `--check`. |
| `tests/test_gen_state.py` | Schema/invariant, rendering, drift, marker-safety, and byte-stability tests. |
| `tests/fixtures/state_kernel/` | Minimal valid/invalid kernels and exact expected fragments. |
| `RUN_STATE.md` | Hand-authored current facts around one generated intake/restart region. |
| `TASK_QUEUE.md` | Hand-authored policy/history around one generated live-queue region. |

### 2.2 JSON, not YAML

Use JSON.

The core repository and CI are stdlib-only under D-009. JSON requires no optional parser, has no implicit scalar typing, and can be canonicalized byte-for-byte with `json.dumps`. YAML is easier to annotate, but comments would become an unvalidated shadow state and PyYAML would add an avoidable dependency. Human rationale belongs in `status_note`, `fences`, the owning spec, or the run report.

Use one kernel file, not one file per lane. Cross-lane gates are first-class: P0-003 `[ED-EXTERNAL]` gates retained Window-A evidence in `[QUIET-MAC]`, and P1-006 `[ED-EXTERNAL]` gates live promotion of P2-005 `[AGENT]`. One file makes those edges and lane-rank uniqueness validate atomically.

The kernel is hand-edited; views are generated. Generating the kernel from Markdown is rejected because it would preserve Markdown as the hidden authority.

## 3. Exact kernel schema

### 3.1 Top-level object

`docs/process/state_kernel.schema.json` must set `additionalProperties: false` at every object level. `scripts/gen_state.py` must enforce the same constraints using only the Python standard library.

| Field | Type | Required | Contract |
|---|---|---:|---|
| `schema` | string | yes | Exact value `docs/process/state_kernel.schema.json`. |
| `schema_version` | integer | yes | Exact value `1`. Changed meaning requires a new version and migration. |
| `updated` | string | yes | Explicit `YYYY-MM-DD`; never generated from wall-clock time. |
| `latest_report` | Pointer | yes | Latest substantial handoff report. |
| `active_stop_card` | Pointer or null | yes | Null when no card is active; otherwise points to `docs/stop_cards/<id>.md`. |
| `tasks` | object keyed by task ID | yes | Live nonterminal tasks only. Object order has no meaning. |

### 3.2 Pointer

A `Pointer` has:

| Field | Type | Required | Contract |
|---|---|---:|---|
| `path` | string | yes | Repo-relative POSIX path; no absolute path, `..`, URL, or symlink escape. Target must exist. |
| `label` | string | yes | Nonempty generated-link label. |
| `anchor` | string | no | GFM heading fragment without `#`; mutually exclusive with `json_pointer`. |
| `json_pointer` | string | no | RFC 6901 pointer beginning `/`; mutually exclusive with `anchor`. |

The generator verifies target paths and locators. A path-only pointer is permitted. HTTP links may remain in authority documents, but live state points first to repository evidence.

### 3.3 Task

Every value under `tasks` is a `Task`. The object key and `Task.id` must match.

| Field | Type | Required | Contract |
|---|---|---:|---|
| `id` | string | yes | Pattern `[A-Za-z0-9][A-Za-z0-9.-]*`. |
| `lane` | enum | yes | `agent`, `quiet_mac`, or `ed_external`. |
| `rank` | integer | yes | Nonnegative and unique within a lane. Lower sorts first. Gaps are allowed. |
| `priority` | enum | yes | `p0_safety`, `p1_phase_gate`, `p2_next_slice`, `p3_research_expansion`, or `p4_polish`. |
| `status` | enum | yes | `queued`, `active`, `partial`, `blocked`, or `shelved`. Terminal `done` is absent. |
| `status_note` | string | no | Current nuance only; no independent completion claim. |
| `goal` | string | yes | Bounded outcome suitable for the generated Task cell. |
| `dependencies` | Dependency array | yes | May be empty; canonical sort applies. |
| `authority` | Pointer | yes | Primary authority that permits/defines the task. |
| `acceptance` | Acceptance | yes | Kernel-owned completion test and evidence shape. |
| `fences` | Fence array | yes | May be empty. |
| `fallback` | Fallback or null | yes | Bounded alternative when the preferred route fails. |
| `flags` | enum array | yes | Unique values from the controlled vocabulary below. |
| `stop_card` | Pointer or null | yes | If non-null, equals top-level `active_stop_card`. |

Allowed flags:

- `pre_window_a_gate`
- `blocked_post_2m`
- `provisional_until_live`
- `lead_only`
- `mixed_lane_migrated`
- `migration_inferred_lane`

Table-rendered strings must be one paragraph and contain neither literal newlines nor `|`. Detailed prose belongs in pointer targets.

### 3.4 Dependency

| Field | Type | Required | Contract |
|---|---|---:|---|
| `kind` | enum | yes | `task`, `artifact`, `decision`, `external`, or `event`. |
| `target` | string | yes | Task ID for `task`; stable identifier otherwise. |
| `required` | string | yes | Human-readable satisfied condition. |
| `state` | enum | yes | `pending` or `satisfied`. |
| `strength` | enum | yes | `hard` or `advisory`. |
| `scope` | enum | yes | `start`, `retain_evidence`, `interpret`, `close`, or `live_promotion`. |
| `evidence` | Pointer or null | yes | Required when satisfied; null when pending. |
| `note` | string | no | One-line explanation, not another authority. |

Pending task dependencies must name live tasks. Satisfied task dependencies may name tasks removed from the kernel, but must carry closure evidence.

Dependencies sort by:

```text
(scope, strength, kind, target, required)
```

For non-shelved tasks, `status=blocked` if and only if at least one pending, hard `scope=start` dependency exists. Shelved tasks may retain pending trigger dependencies but are never restart-eligible.

A queued, active, or partial task may carry pending later-scope gates; these appear in the view without hiding preparatory work.

Priority is not a dependency. C-027’s P2-040 → P2-038 → P2-039 → RPT-001 → P2-042 → P2-041 → P2-037 sequence is lane rank. The causal P2-042 → P2-037 edge is a dependency. Turning all priority relationships into dependencies would falsely prohibit safe independent work.

### 3.5 Acceptance, Fence, and Fallback

`Acceptance`:

- `summary`: required pass/fail criterion rendered in the queue.
- `pointer`: required owning checklist/spec/contract pointer. If the current queue cell is the only owner, use `docs/process/state_kernel.json#/tasks/<id>/acceptance`.
- `evidence`: required nonempty string array naming artifacts, commands, measurements, or approvals expected at closure.

`Fence`:

- `rule`: required prohibited scope, claim, mutation, or execution.
- `authority`: required decision/contract pointer.

`Fallback`:

- `condition`: required observable trigger.
- `action`: required bounded fallback or structured verdict.
- `pointer`: required owning plan/decision.

### 3.6 Cross-record invariants

The generator rejects the kernel unless:

1. IDs match object keys; lane ranks are unique; no unknown fields exist.
2. No task has terminal status.
3. For non-shelved tasks, `blocked` exactly matches hard pending start dependencies.
4. Pending task dependencies resolve; no self-dependency exists; pending hard task edges are acyclic across all scopes.
5. Every satisfied dependency has evidence; pending dependencies do not.
6. Pointer targets and locators resolve.
7. If `active_stop_card` is null, every task `stop_card` is null. If active, at least one active/blocked task points to it.
8. `blocked_post_2m` requires a P2-006 dependency and a binding authority that establishes the post-2M gate. P2-022 and P2-023 must specifically resolve to D-041.
9. `quiet_mac` tasks are labeled lead-controlled; generator execution never authorizes measurement work.

### 3.7 Normative example

```json
{
  "acceptance": {
    "evidence": [
      "Focused fixtures include the paired [100..500] versus [101..501] counterexample",
      "Canonical unit suite passes"
    ],
    "pointer": {
      "json_pointer": "/tasks/P2-037/acceptance",
      "label": "P2-037 acceptance",
      "path": "docs/process/state_kernel.json"
    },
    "summary": "Consume the frozen P2-042 analysis manifest and emit fail-closed contrast and claim verdicts."
  },
  "authority": {
    "anchor": "5-council-positions-adopted-after-bounded-discussion",
    "label": "C-027 §5",
    "path": "docs/reviews/2026-07-09-c027-whole-project-review.md"
  },
  "dependencies": [
    {
      "evidence": null,
      "kind": "task",
      "note": "P2-037 consumes this manifest.",
      "required": "frozen analysis manifest accepted",
      "scope": "start",
      "state": "pending",
      "strength": "hard",
      "target": "P2-042"
    }
  ],
  "fallback": null,
  "fences": [],
  "flags": [],
  "goal": "Implement the D-053/D-054 contrast and fail-closed claim-analysis engine.",
  "id": "P2-037",
  "lane": "agent",
  "priority": "p2_next_slice",
  "rank": 8,
  "status": "blocked",
  "status_note": "Required before any P2-006 L2 interpretation.",
  "stop_card": null
}
```

The actual kernel uses two-space indentation, sorted object keys, UTF-8, `ensure_ascii=False`, and exactly one trailing LF.

## 4. Generator and generated regions

### 4.1 Command contract

`scripts/gen_state.py` is stdlib-only and supports:

- `python3 scripts/gen_state.py`: validate, canonicalize the kernel, render both regions in memory, and atomically replace marker interiors.
- `python3 scripts/gen_state.py --check`: read-only validation of schema, invariants, canonical bytes, markers, and rendered output. Exit `1` for drift, `2` for invalid input/markers, and `0` only for exact agreement.
- `python3 scripts/gen_state.py --stdout run-state|queue`: render one fragment without modifying files.

Optional `--kernel`, `--run-state`, and `--queue` paths exist only for tests. Production defaults are fixed.

Rendering must not depend on current date, locale, Git state, environment variables, network, randomness, filesystem enumeration order, or input object insertion order.

### 4.2 `RUN_STATE.md` region

Replace the cleared stop-card prose and hand-written restart block with one region after the manual Last updated line:

```markdown
<!-- BEGIN GENERATED: state-kernel run-state-intake -->
## ACTIVE_STOP_CARD

...

## Restart By Machine-State Lane

...
<!-- END GENERATED: state-kernel run-state-intake -->
```

When no card is active, `ACTIVE_STOP_CARD` says `Status: NONE` and links to D-050/D-063. Cleared-card narrative is not retained.

When a card is active, restart output contains only:

- the card link;
- affected task IDs; and
- notice that normal lane selection is suspended.

With no active card, render `[ED-EXTERNAL]`, `[QUIET-MAC]`, and `[AGENT]` in that order:

1. If tasks are active, render all active IDs by rank as `CONTINUE`.
2. Otherwise choose the lowest-rank queued/partial task with no hard start blocker as `READY`.
3. If none is ready, show the lowest-rank blocked task and its blockers.
4. If no live task exists, show `NONE`.

The region includes the kernel and `latest_report` links.

Delete during migration:

- `Start Here For Every Big Run`; playbook M0 owns procedure.
- cleared stop-card prose;
- hand-written `RESTART HERE`;
- `Session History`;
- prior verification-history bullets, retaining only the latest canonical suite/head statement and report pointer;
- `What Is Next`; and
- `Open Decisions And Blockers`, whose live gates belong in the kernel/queue and risks in the risk register.

Compact, but do not generate, Current Project Status and Known Workspace State. They must contain no ranked next-work lists.

### 4.3 `TASK_QUEUE.md` region

Keep the `## Current Queue` heading and place one generated region beneath it:

```markdown
<!-- BEGIN GENERATED: state-kernel current-queue -->
...
<!-- END GENERATED: state-kernel current-queue -->
```

The region contains:

1. A source/generation warning.
2. Lane tables in `[ED-EXTERNAL]`, `[QUIET-MAC]`, `[AGENT]` order.
3. A final Shelved task records table.

Columns:

| Rank | ID | Priority | Queue state | Task | Evidence / Acceptance |
|---|---|---|---|---|---|

Rank renders as `E<n>`, `Q<n>`, or `A<n>`.

Queue state renders as:

- `ACTIVE`;
- `READY`;
- `PARTIAL; READY`;
- `BLOCKED — <dependencies>`; or
- later-scope `GATES <scope>: <labels>` annotations.

Task renders `goal`. Evidence/Acceptance renders the acceptance summary, authority and acceptance links, and compact task-specific fences.

Keep outside the region:

- Priority Scale;
- ranking rationale;
- machine-lane explanation;
- Completed Queue Items;
- disposition shelf;
- Do-Not-Do-Yet policy list; and
- Queue Maintenance.

Condense the duplicated Intake Rule to a pointer to M0 and the generated restart. Do not generate Do-Not-Do-Yet in Stage 1 because it contains semantic policy and supersession judgments.

### 4.4 Determinism and marker safety

- Fixed lane order; tasks sort by `(rank, id)`.
- Flags sort lexically; dependencies and fences use normative sort keys.
- Output uses LF, no trailing spaces, fixed blank-line rules, and one LF before the end marker.
- A second generation changes neither bytes nor mtimes.
- Missing, duplicate, reversed, overlapping, or nested markers are fatal.
- Bytes outside marker interiors must remain unchanged.
- `--check` is read-only even on failure.

## 5. Exact migration of the current queue

### 5.1 Migration notation

`K(ID)` means:

- current Task cell → `goal`;
- current Evidence/Acceptance cell → `acceptance.summary` and `acceptance.evidence`; and
- acceptance pointer → `/tasks/ID/acceptance` in the kernel unless another owner is named.

Text may be tightened only to remove status/history from the goal. Prohibitions move to `fences`; they do not disappear.

Shorthand:

- `C027`: `docs/reviews/2026-07-09-c027-whole-project-review.md`
- `DF`: `docs/phase_2/detection_floor.md`
- `AP`: `docs/contracts/analysis_plans.md`
- `P1X`, `P2X`, `P3X`: corresponding phase exit checklist
- `RQ`: registry, bank, or specifically named candidate design

### 5.2 Terminal rows removed from live state

These do not become kernel records. Move them to Completed Queue Items with current completion/task/evidence text preserved:

| Current rank | ID | Disposition |
|---|---|---|
| 0 | P2-015-PREP | Completed ledger; DF, D-054, PR #31, Wave-1 report. |
| 0a | P2-029 | Completed ledger; D-057 and Wave-2 report. |
| 0b | P2-030 | Completed ledger; D-056 and Wave-2 report. |
| 0c | P2-031 | Completed ledger; D-058, token contract, Wave-2 report. |
| 0d | P2-032 | Completed ledger; campaign packs and PR #36. |
| 0e | P2-034 | Completed ledger; broad packs, PR #39, P2-034 report. |

DOC-008 begins as active A11. At final close-out it moves to Completed Queue Items and leaves the live kernel. Ranks are not renumbered.

### 5.3 `[AGENT]` records

| Old rank | ID → new state | Dependencies/flags | Authority → acceptance |
|---|---|---|---|
| 0f | P2-035 → A0 `blocked` | hard start P2-015 | candidate variance design → registry rules + K |
| 0g | P2-036 → A1 `shelved` | trigger P2-023 | import-family pack → K |
| 0h | P2-040 → A2 `queued` | none | C027 ARC-3/5/6/8 and STA-5/6/7/8/11 → K |
| 0i | P2-038 → A3 `queued` | `pre_window_a_gate` | C027 RIG-3/RIG-7 → K |
| 0j | P2-039 → A4 `queued` | `pre_window_a_gate`; freeze-before-data fence | D-054 + C027 STA-4/RIG-6 → DF + K |
| 0k | RPT-001 → A5 `queued` | none | C027 NEG-2/5 and ARC-9 → K |
| 0l | P2-042 → A6 `queued` | none | C027 STA-10 → K |
| 0m | P2-041 → A7 `queued` | none | D-057 + C027 STA-2/9/11 → K |
| 0n | P2-037 → A8 `blocked` | hard start P2-042; rank follows P2-041 | D-053/D-054 + C027 → K |
| 0o | SPLIT-AP → A9 `queued` | blocks later split execution | D-048/D-049 + C027 → split pack/AP + K |
| 0p | AP-EDIT → A10 `queued` | none | D-062 + C027 → AP + K |
| 0q | DOC-008 → A11 `active`, then archive | none | D-063 → this spec |
| 0r | DOC-009 → A12 `queued` | none | D-023 + C027 TOP-5/REV-8 → K |
| 0s | MET-001 → A13 `queued` | append-only/history fences | D-031/D-050 + C027 → K |
| 0t | RETRO-001 → A14 `queued` | none | C027 B6/REV-2 → K |
| 0u | REPRO-001 → A15 `queued` | `mixed_lane_migrated`; ends at lockfiles + publication-ready pack | C027 NEG-9 → K; tail to P2-027 |
| 3 | P3-000 → A16 `blocked` | hard external R-003 approval for 3.0.2 | D-035/D-036 + P3X/KV feasibility → P3X |
| 8 | P2-022 → A17 `blocked` | hard P2-006; satisfied P2-010a; `blocked_post_2m` | D-041 → adapter contract + K |
| 9 | P2-023 → A18 `blocked` | hard P2-006 and P2-022; `blocked_post_2m` | D-041 → RQ bank + K |
| 10 | P2-024 → A19 `blocked` | hard P2-015 and P2-006 reductions | C-015/RQ → K |
| 11e | P2-028 → A20 `queued` | none | CP-6 record → K |
| 11d | P3-001b → A21 `blocked` | hard P2-006 coefficients | D-048/D-049 → phase-3 plan/AP + K |
| 15 | P2-004 → A22 `partial` | hard `close` P1-001; `migration_inferred_lane` | D-016 → P1X + K |
| 16 | P2-005 → A23 `partial` | hard `live_promotion` P1-006; inferred/provisional flags | hardware guide → live checklist + K |
| 17 | P2-016 → A24 `blocked` | hard start P2-006; P2-005 live gate for 2K subitems; `blocked_post_2m` | C-011 ledger/report → K |

P2-016 is an umbrella with heterogeneous gates. Stage 1 conservatively blocks the parent rather than inventing child IDs. A later owning session may split P2-016a..i through normal intake.

### 5.4 `[QUIET-MAC]` records

| Old rank | ID → new state | Dependencies/flags | Authority → acceptance |
|---|---|---|---|
| 1a | P2-015-SMOKE → Q0 `blocked` | hard P0-003 and P2-038; `pre_window_a_gate`, `lead_only` | DF Ordering Preconditions → K |
| 1 | P2-015 → Q1 `blocked` | hard P0-003, SMOKE, P2-038, P2-039; gate/lead flags | D-054 + DF → P2X + K |
| 2 | P2-006 → Q2 `blocked` | hard start P2-015; hard `interpret` P2-037 and P2-041; `lead_only` | phase-2 plan/AP → P2X + K |
| 4 | P2-010 → Q3 `blocked` | hard P2-015; quiet-window-tail note; `lead_only` | AP-5 + affine stream log → K |
| 5 | P2-019 → Q4 `blocked` | hard P2-006; `lead_only` | AP-1 + phase-2 plan → K |
| 6 | P2-020 → Q5 `blocked` | hard P2-006; `lead_only` | AP-6 + D-046 → K |
| 7 | P2-012 → Q6 `blocked` | hard P2-006; `lead_only` | AP-4 + D-039/D-040 → K |

P0-003 applies because these rows create or retain new irreplaceable evidence. It does not block agent correctness work, report drafting, or generator implementation.

### 5.5 `[ED-EXTERNAL]` records

| Old rank | ID → new state | Dependencies/flags | Authority → acceptance |
|---|---|---|---|
| E0 | P0-003 → E0 `queued` | none | R-016/C027 escalation → restore evidence + K |
| E1 | P1-008 → E1 `queued` | none | milestones/R-012 → milestones + scope notes |
| 11c | P2-027 → E2 `blocked` | hard REPRO-001 publication-ready environment/pack | C-020/C027 NEG-9 → published pack + external reduction |
| meta | P1-001 → E3 `queued` | none | R-001 → P1X approval/scope notes |
| 12 | P1-003 → E4 `queued` | none | D-018/C-003 → P1X wall-meter decision |
| 13 | P1-004 → E5 `queued` | none | R-011 → P1X topology evidence |
| 14 | P1-006 → E6 `queued` | none | remote gate/NV-GATE-2 → P1X access evidence |

### 5.6 Migration verification

Tests hold an explicit expected set of 39 pre-close live IDs and 38 after DOC-008 archives. Missing or extra IDs fail.

Tests separately assert:

- the six old terminal IDs are absent from the kernel and present in Completed Queue Items;
- P2-037 hard-start depends on P2-042;
- P2-041 ranks before P2-037;
- P2-015 depends on P0-003, SMOKE, P2-038, and P2-039;
- P2-006 starts after P2-015 and cannot be interpreted at L2 before P2-037 and P2-041;
- P2-022/P2-023 carry `blocked_post_2m`, and P2-023 depends on P2-022;
- P2-016 remains conservatively post-2M at parent level;
- P2-027 is the external successor to REPRO-001; and
- E0/P0-003 sorts before E1/P1-008.

## 6. Retirement of `docs/planning_reflection_protocol.md`

### 6.1 Start-of-run questions

| Existing question | Stage-1 disposition |
|---|---|
| Exact goal | Required `Task.goal`. |
| Prior state inspected | Retired as a task field. M0 owns targeted intake; authority, dependencies, and latest report identify required state. |
| Inherited assumptions | Binding assumptions become fences, dependencies, or authority text. Other reasoning stays in the owning spec/report. |
| Checklist items moved closer | Acceptance/checklist pointer; D-023 forbids another status mirror. |
| Evidence proving done | `acceptance.summary` and `acceptance.pointer`. |
| Commands/files/measurements/approvals | `acceptance.evidence`. |
| Nonblocking failure and recording | Optional `fallback`; structured verdicts remain in owning plans. |
| What must not change | `fences`. |

Step Planning Quality Bar mapping:

- Objective → `goal`
- Inputs → dependencies/authority
- Actions → owning plan/spec
- Evidence/acceptance → `acceptance`
- Fallback → `fallback`

The Phase Exit Rule remains operative through D-023, exit checklists, and M0 close-out.

### 6.2 End-of-run fields

| Existing field | New owner |
|---|---|
| What changed | Dated run report |
| How work was ranked | Kernel lane/rank; report explains overrides |
| What was verified | Run report and checklist evidence |
| What failed/remains uncertain | Run report plus live dependency/fallback state |
| Whether plan was accurate | Optional run-report analysis |
| Planning gaps | New/revised kernel tasks plus report rationale |
| Next exact step/evidence | Generated restart plus selected acceptance |

### 6.3 Exact redirect stub

```markdown
# Planning Reflection Protocol (retired)

Status: RETIRED by D-063 (C-027 process architecture v2, Stage 1).

This path remains as a compatibility pointer; it is not an independent intake
or close-out checklist.

- Intake and close-out procedure: `docs/agent_playbook.md`, Mission M0 and
  “After Any Mission.”
- Live goal, lane, rank, status, dependencies, authority, acceptance,
  evidence shape, fences, and fallback: `docs/process/state_kernel.json`.
- Detailed actions and design rationale: the task’s owning plan/spec/decision
  pointer.
- Phase completion evidence: `docs/phase_N/phase_N_exit_checklist.md` (D-023).
- Session outcomes and reflection: dated files under `docs/run_reports/`.

Do not add new protocol requirements here. Amend the owning artifact and cite
the binding decision.
```

Update inbound references in `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/agent_playbook.md`, `AGENT_PLAN.md`, and `README.md` in the same change. Keep the stub indefinitely.

## 7. Exact orchestration text

Add these subsections to `docs/orchestration.md` after the decomposition/per-stream description and before lead live gates.

### 7.1 Two-writer rule

```markdown
### One writer per working tree (the two-writer rule)

At most one process may write a working tree at a time. The lead counts as a
writer: lead bookkeeping, cleanup, formatting, conflict resolution, and
“small” post-review edits may not overlap a worker that can modify the same
tree. Parallel writers require separate worktrees/branches and disjoint
expected diff footprints. Review-only readers may overlap only when their
tools are guaranteed read-only.

Before taking write ownership, the writer must identify the tree and branch,
wait for every prior writer to finish or be explicitly stopped, inspect
`git status --short --branch`, and preserve all pre-existing changes. Before
lead bookkeeping begins, the lead must declare the tree quiescent. No cleanup
or generated-file refresh may run over another writer’s uncommitted work.

If overlap is discovered, stop new writes; capture the branch, HEAD, status,
and diffs for both owners; preserve both versions; and let the lead reconcile
them. Never resolve an ownership collision by discarding or reverting work by
inference.

Writer separation and reviewer separation are distinct. The author of a
change or test may not be its sole fresh reviewer/auditor. Any lead or worker
content edit after the last fresh review creates a new final-head review
obligation. Lead-owned live/hardware gates remain lead-owned and are not a
writer-separation violation.
```

### 7.2 Credential-boundary push procedure

```markdown
### Credential-boundary push handoff

“Push green commits promptly” is an outcome, not permission to copy or bypass
credentials. If the current environment cannot authenticate, it must hand the
exact reviewed commit to a named authenticated pusher instead of accumulating
silent local-only state.

The blocked environment must: (1) finish the authorized local checks; (2)
record the repository, branch, remote, exact commit SHA, clean/dirty status,
and review/CI state; (3) name the authenticated pusher and an explicit
ISO-8601 deadline no later than the next dependent session or any claim of
remote/advisor freshness; and (4) record the handoff in the run report and the
live queue. If missing remote state makes restart unsafe, create an active stop
card. Credentials themselves are never transferred.

The authenticated pusher must verify that the received branch resolves to the
recorded SHA, rerun any environment-bound required gate, push that exact SHA to
the named remote/ref, and record the remote ref/SHA confirmation. If the SHA
changes, normal review and final-head rules reapply before push or merge.

Until remote confirmation exists, status must say `LOCAL_ONLY — PUSH PENDING`;
the project must not claim that GitHub, a PR, a deployment, or an advisor-facing
snapshot contains the change. A missed deadline becomes an explicit
`[ED-EXTERNAL]` blocker, not an informal “push when convenient” note.
```

This procedure does not expand commit, push, merge, or deployment authority.

## 8. `PROJECT_STATUS.md` compaction structure

This is a structure specification for the lead. The DOC-008 implementer must not author or generate current advisor-facing claims.

### 8.1 Archive target

Create `docs/project_status_history.md` with a preface:

> Historical snapshots; non-operative; current status lives in `PROJECT_STATUS.md`; dated evidence lives in run reports.

Move verbatim, in current order:

- all Previous Update sections;
- Update Ledger;
- Evolution From The Original Architecture Sketch; and
- the retired long Process Note, labeled as a historical snapshot with `docs/orchestration.md` owning current procedure.

Do not rewrite moved prose to look current. Existing correction/supersession annotations move with it. Dated reports remain untouched.

### 8.2 Target current structure

Maximum seven H2 sections and a target of 1,400 words excluding compact tables:

1. `Current Claim And Scope`
2. `Measured Evidence`
3. `Gate Matrix`
4. `Artifact State`
5. `Advisor Decisions And Risks`
6. `Next Milestone`
7. `Evidence Links`

Remove standalone full architecture, methodology, experiment-plan, phase-plan, timeline, deliverables, repository-map, and process-essay bodies only after the lead preserves any advisor-essential sentence in the compact structure and links its owner.

No Previous Update, volatile decision count, manual test count, or agent-ranked next-work list remains.

### 8.3 Acceptance

- An advisor can identify the current scientific claim, measured evidence, hard gates, required advisor action, and next milestone without scrolling through history.
- The archive contains every removed dated update verbatim.
- Current quantitative statements retain evidence/stack pointers.
- The lead signs off final prose and diff; generation tests do not bless semantic claims.

## 9. Intake and procedure reconciliation

### 9.1 `docs/agent_playbook.md`

Make M0 the sole short procedural intake owner:

1. Read the generated RUN_STATE intake/restart region. If a stop card is active, follow only its pointer.
2. Read the selected kernel/queue row and manual Do-Not-Do-Yet list.
3. Read the task authority, acceptance, and targeted mission/plan pointers.
4. Read `AGENT_PLAN.md` only for phase/structure changes, the risk register on existing triggers, and the latest report when selected state points to it.
5. For delegation, review, or multiple streams, read `docs/orchestration.md` before writes.
6. Inspect workspace state and run task-proportionate baseline checks.

Replace:

> One mission per session unless the first finishes early and cleanly.

With:

> A session may execute one task or multiple genuinely independent task records. Multiple writers require orchestration’s separate-worktree and two-writer rules; rank may be bypassed only by an active stop card, explicit user direction, or a recorded safety emergency.

Update After Any Mission so close-out edits the kernel and runs `scripts/gen_state.py`; generated regions are never hand-edited. Preserve canonical suite and D-023 closure requirements.

### 9.2 Other procedure surfaces

- `RUN_STATE.md`: remove procedure lists; point to M0.
- `TASK_QUEUE.md`: replace the nine-step intake duplicate with an M0 pointer and kernel-source statement.
- `AGENT_PLAN.md`: replace reflection-protocol references with kernel/M0 pointers.
- `README.md`: replace the reflection recommendation with the playbook/kernel/checklist route.
- `docs/orchestration.md`: say the kernel owns live state, TASK_QUEUE is the generated detailed view, and RUN_STATE is the generated restart plus compact handoff facts.

Named decisions win: missions do not override dependencies, ranks do not override active stop cards, and neither silently overrides decision-log fences.

## 10. Test and CI obligations

### 10.1 Focused tests

`tests/test_gen_state.py` covers:

1. valid minimal and migrated kernels;
2. missing/unknown fields and enums;
3. ID mismatch, duplicate lane rank, invalid pointers/paths, self-dependency, dangling task, and cycles;
4. blocked/status consistency and later-scope gates;
5. satisfied-dependency evidence;
6. active stop-card override;
7. deterministic ordering;
8. exact migration ID set and §5.6 assertions;
9. golden fragments for card/no-card, ready, blocked, partial, shelved, and empty lanes;
10. invalid marker refusal;
11. preservation outside markers and no partial writes;
12. double generation byte stability and no second write;
13. one-byte drift detection with read-only failure;
14. rejection of terminal live tasks;
15. `blocked_post_2m` invariants; and
16. manual-validator/schema enum and required-field synchronization.

### 10.2 CI

Add before unit tests:

```yaml
- name: State kernel and generated-view drift
  run: python scripts/gen_state.py --check
```

It may run in both supported Python jobs.

Required local checks:

```bash
python3 -m unittest tests.test_gen_state -v
python3 scripts/gen_state.py --check
python3 -m unittest discover -s tests
```

PROJECT_STATUS prose still requires semantic link/claim review. Generator success is not claim validation.

## 11. Staged landing plan

Use one D-031 feature branch/PR. Each stage is a reviewable commit and each working tree has one writer.

1. **Kernel mechanics:** schema, generator, fixtures, tests, CI. Use fixture paths; do not switch live Markdown.
2. **Live-state migration:** seed kernel, move six terminal rows, add markers, generate views, and apply RUN_STATE deletions.
3. **Procedure consolidation:** retire reflection protocol, repair inbound references, reconcile M0, and add orchestration procedures.
4. **Lead-authored status compaction:** lead creates history archive and authors compact PROJECT_STATUS. No concurrent writer touches the tree.
5. **Close-out:** generate, run focused/full tests, run docs consistency review, move DOC-008 to Completed Queue Items, remove it from the live kernel, regenerate, rerun all checks, and perform final-head review.

Do not close DOC-008 before PROJECT_STATUS compaction and the CI drift gate exist. If lead authorship is deferred, DOC-008 remains active/partial unless the lead explicitly splits its acceptance.

## 12. DEVIATIONS / OPEN QUESTIONS

### 12.1 Deliberate deviations from D-063’s minimum fields

- The schema adds rank, priority, goal, evidence shape, fences, fallback, flags, status note, and latest-report pointer. These are required for generation and for folding in useful reflection fields; they remain live state, not history or policy.
- Completed tasks are excluded even though six appear in Current Queue. This follows the adopted counterreview’s explicit instruction not to migrate completed rows.
- Marker-fenced regions are generated instead of whole files. Whole-file generation would absorb lead-authored factual prose and violate staged migration.
- Stop-card bodies move to `docs/stop_cards/` while their visible override remains generated in RUN_STATE.

### 12.2 Lead adjudication requested; defaults specified

1. **Mixed-lane REPRO work:** default is REPRO-001 agent prep plus P2-027 external tail. Multi-lane tasks are rejected.
2. **P2-004/P2-005 lane inference:** default `[AGENT]` with later-scope external gates.
3. **P2-016 granularity:** default conservative parent block; child split is deferred.
4. **P2-006 interpretation gate:** default requires both P2-037 and P2-041 before L2 interpretation. P2-037 remains mandatory even if the lead rules P2-041 to be rank-only.

No other implementation choice remains open. JSON, one kernel, marker fences, terminal-row exclusion, and mandatory CI drift failure are fixed if this spec is accepted.

## CHECKS PERFORMED

- Read targeted RUN_STATE stop-card, status, workspace, and next-work sections; the stop card is cleared.
- Read TASK_QUEUE Current Queue, Do-Not-Do-Yet, DOC-008, completed ledger, and all 45 current rows.
- Ran read-only workspace checks. The final observed branch was `c027-spec-wave`; no worktree changes were reported. Git emitted sandboxed `/tmp/xcrun_db` cache warnings.
- Read D-023, D-031, D-041, D-050, D-061, and D-063.
- Read C-027 §5-Q1 and the corrected queue sequence, lens-meta findings 1/5/8/9 and design judgment, counterreview Q1, reverse-review credential/two-writer findings, and topdocs compaction judgment.
- Inspected the planning-reflection protocol, agent M0/selection/close-out text, orchestration artifact/stop-card rules, PROJECT_STATUS structure, CI workflow, and generated-artifact test patterns.
- Attempted to create `docs/specs/c027/doc-008_state_kernel.md` with `apply_patch`; the managed read-only sandbox rejected the write. The target file remains absent and no repository file was changed.
- No hardware, network, quiet-machine measurement, tests, commit, push, merge, deployment, decision/council-log edit, or history rewrite was performed.