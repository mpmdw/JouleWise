# Exit-completeness escalation consult — response of record (2026-08-08)

Sol xhigh (fast tier), read-only, via scripts/codex-bridge. Charge:
ESCALATION.md beside this file (ungoverned-refusal class at count 2
across layers).

**MAGISTRATE ADOPTION (Fable, 2026-08-08): ADOPTED IN FULL as one
integrated structural round — explicitly not licensed as a fourth site
fix.** The four ranked elements bind: (1) deterministic claim identity
+ held kernel writer lease (dual discriminator: stable operation
key/target commitment for crash-vs-conflict, live lease for
concurrency; random-token mismatch may never discriminate), plus the
fresh-process resume/abort CLI and the writer crash matrix; (2)
operation-aware, phase-aware ARM readiness with the ENFORCING check
held under the writer lease through countdown (a standalone check is
early warning only); (3) the cross-layer refusal registry-at-raise
with exact-set gates and EXECUTED exit witnesses (a mapped exit nobody
executed is the same defect one level up); (4) section-local D-117
runbook amendments in §5/§6/§10 per the D-100 convention, the §13
not-in-force copy deleted, and the guarded head-pin advancement
procedure (uncommitted-pin override REJECTED and pruned). S1/S2/S4
dispositioned per the memo; the arming blocker stays OPEN until all
four land together and the writer crash matrix passes from fresh
processes.

---

## Positions

### 1. Exit-completeness is a merge-blocking composition invariant

**Ruling:** the unattended calibration path is exit-complete only when every expected refusal emitted by the reservation CLI, ledger, recovery CLI, writer, and bracket supervisor has:

1. a stable machine-readable refusal code;
2. exactly one governed exit classification;
3. a public CLI route or named runbook procedure;
4. a regression that first reproduces the refusal from durable state, then reaches the declared exit from a fresh process without retained ephemeral state; and
5. a terminal result of `operation_completed`, `ready_to_arm`, `session_aborted`, or `night_stopped_preserved`.

Manual deletion, ledger editing, undocumented Python calls, and reuse of an in-memory lifecycle object are not exits.

The canonical inventory should live in a new cross-layer module such as `joulewise/calibration_exits.py`, **not** inside `calibration_ledger.py` and not primarily in Markdown. A ledger-owned registry would repeat the layer-boundary defect. Use an immutable tuple keyed by an enum, with fields equivalent to:

- refusal code and emitting component/phase;
- retry class;
- exit kind and CLI command ID;
- runbook anchor;
- arm-blocking effect;
- whether the state is reachable after a prior crash;
- witness ID and expected terminal result;
- whether the exit necessarily loses the night.

The contract contains a generated projection of this registry; it is not a second authority. The recovery CLI should expose `explain <code>` and emit structured JSON containing `code`, `exit_id`, `arm_blocked`, and the applicable next command.

The initial exit families must include, with separate codes wherever the exit differs:

| Refusal/state family | Governed exit |
|---|---|
| Durable intent or exact target prefix | `repair`: deterministic completion |
| Mechanically unambiguous torn record or intent mismatch | `repair`: engine abandonment, then completion |
| Other terminal residue | `abandon-tail`, then `repair` |
| Active legacy `.append-journal` | `repair`: record and archive; unreadable/archive-conflict variants hard-stop and preserve |
| Exact completed logical operation from a dead predecessor | Idempotent return/resume; this must not be a refusal |
| Live writer contention | Wait for or intentionally stop the live holder; never abort underneath it |
| Complete capture artifacts without finalization | Fresh-process deterministic finalization |
| Partial capture artifacts | `abort-session`, preserving the custody directory |
| Open session with a semantic binding/order conflict | `abort-session`, or named no-arm escalation if abort would violate custody |
| Recovery advanced the physical head beyond the committed pin | Desk-only head-pin advancement and commit procedure |
| Malformed ledger, unsafe lock inode, unreadable custody, or nonconvergent recovery | Named no-arm/preserve/escalate procedure |
| Sampler-never-ready or rollover failure after a claim | Automatic governed session abort |
| Invocation/configuration/protocol refusal | Correct the named preflight defect; no arm |

These are exit families, not permission for a catch-all code. Every concrete operational refusal site gets its own registered code. Mapping a new refusal to generic “stop” requires explicit review and must record `night_loss=true`; prior-crash states may not use generic stop as a shortcut.

**Enforcement: registry-at-raise, not reflection alone.**

- Replace free-form operational `CalibrationLedgerError("text")` with a coded refusal carrying optional diagnostic context.
- Prohibit substring marker lists such as the writer’s current `"exclusive writer claim"` / `"operation key conflicts"` tuple.
- An AST check over the scoped modules rejects direct free-form refusal construction, `print("refusing: ...")`, or nonzero operational exits not routed through the registry.
- An exact-set test requires `RefusalCode == inventory keys == discovered witness codes`.
- The generated contract table and runbook anchors are checked for freshness.
- Each witness must use a public subprocess CLI: construct durable state, observe the exact refusal code, discard process state, invoke the mapped exit, and assert the declared terminal result.
- A stable `proof_id` string alone is not evidence. The test harness must discover and execute a corresponding witness.

Machine checks prove reachability; they cannot prove intellectual independence. The repository’s writer≠reviewer process remains mandatory: a fresh test author or auditor must review the witness corpus. Do not claim that CI can establish reviewer independence merely because a field names a reviewer.

### 2. Extend the crash matrix to the writer and supervisor layers

Create a dedicated `tests/test_calibration_writer_crash_matrix.py`. Keep ordinary lifecycle unit tests in `tests/test_powermetrics_fiducial.py`; the new matrix should use real subprocesses and `SIGKILL`, as the ledger matrix now does.

Use an exact `WriterStage` enum and require every stage to have a crash witness. Parameterize PRE and POST independently. Required semantic boundaries are:

1. before and after pre-reserve readiness;
2. during reservation intent, after intent fsync, during target, after target fsync, and after reservation returns;
3. before and after acquiring the live-writer lease;
4. after repair;
5. after exact slot validation;
6. during claim intent, after claim-intent fsync, during claim target, after target fsync, and after claim returns but before `begun`;
7. after `begun`, before and after exit-handler registration;
8. after custody-directory creation and after opening the event stream;
9. after sampler spawn, sampler readiness, and rollover readiness;
10. during capture;
11. after sampler teardown and during each non-atomic artifact class: raw/events, trace, evidence, and manifest;
12. after all artifacts are complete but before finalization;
13. during finalization intent, after intent fsync, during target, after target fsync, and after finalization returns but before `closed`;
14. after `closed` but before unregistering the exit handler;
15. after PRE finalization but before the supervisor records or dispatches the next phase;
16. before POST dispatch;
17. after POST finalization but before terminal-pin derivation;
18. after terminal-pin derivation but before output/persistence.

Equivalent in-capture points may share a witness only when the test proves their durable projections are identical. Torn writes need their own cases.

After every kill, launch a fresh process with no inherited lifecycle, UUID, environment token, or shell variable. It must derive progress from the frozen plan, ledger, and custody paths and reach completion or one governed exit. This requires a resumable `session-status`/`resume-finalize`/`abort-session` CLI surface; the current shell-local `PRE_CAL_DIR` and “latest directory” logic is not sufficient across supervisor death.

Also retain a real two-subprocess concurrency test: exactly one process acquires the writer lease, the other receives the coded live-contention refusal, and after the winner is killed a fresh process can resume.

### 3. Make `claim_id` stable, but move liveness to a real lease

**Ruling:** derive the durable `claim_id` deterministically as a domain-separated hash of `(session_id, slot, attempt_id)` and policy revision. A per-process UUID must not participate in durable idempotency equality.

Determinism alone is unsafe: two concurrent processes would compute the same ID and both treat the completed claim as idempotent. Therefore acquire a kernel-enforced, nonblocking writer lease before recovery/claim and hold its file descriptor continuously through countdown, capture, finalization, or abort. A single dedicated writer lock per calibration ledger is preferable to a slot-local lock because the quiet path permits no useful writer concurrency. Never delete the lock inode; stale metadata is diagnostic only, while `flock` ownership is authoritative.

The recovery CLI’s `abort-session` must acquire the same lease before aborting. It must refuse while a writer is live. After `SIGKILL`, the kernel releases the lease and the next process can repair and accept the deterministic durable claim.

Option costs:

- **Deterministic claim only:** fixes crash replay but loses concurrent-writer exclusion. Rejected alone.
- **Ignore a random claim in equality:** also fixes replay but silently accepts a concurrent second process. Rejected alone.
- **Keep random mismatch as a distinct refusal:** preserves concurrency but still needs a liveness oracle and takeover exit; otherwise it merely renames the permanent wedge.
- **Stable claim plus kernel lease — adopted:** fresh-process idempotency and real live-writer exclusion are both preserved.

### 4. Fail-fast classification may not include prior-crash ambiguity

**Ruling:** no fail-fast marker may cover a refusal whose cause can be a prior crash of the same logical operation.

At refusal time, discriminate using:

1. the stable operation key and target commitment; and
2. the live writer lease.

The outcomes are:

- lease held by another process → genuine live conflict;
- lease acquired and durable target exactly matches → prior completion/death; resume idempotently;
- lease acquired and the same operation key has different stable semantic content → durable semantic conflict;
- partial custody after acquiring the lease → finalize if complete and authenticated, otherwise governed `abort-session`.

PID text, UUID mismatch, and error-message substrings are not valid discriminators. Retry behavior belongs in the refusal registry as typed policy.

### 5. Move the runbook procedure into force and make ARM readiness atomic

There should be no omnibus D-117 amendment under §13. Split it by the section it amends:

- `### D-117 §5 amendment — calibration-ledger readiness before arming`
- `### D-117 §6 amendment — durable bracket dispatch and slot resume`
- `### D-117 §10 amendment — calibration-ledger refusals and governed exits`

The operational recovery commands belong under §10, matching the D-100 §9/§10 convention. Delete the not-in-force §13 copy rather than duplicating it.

Section §5 must add checklist items requiring the operator to:

- run the machine readiness command against the exact frozen reservation plan;
- require structured `status: ready`, not infer readiness from `inspection.state`;
- confirm the committed pin relation appropriate to the phase;
- confirm no active legacy journal, intent, residue, operation conflict, or live writer;
- read the named §10 D-117 procedure and have operator identity/attestation values prepared;
- understand that a required head-pin commit is desk work and ends a 2 a.m. attempt rather than licensing an uncommitted-pin override.

Section §10 must contain code-keyed rows for `repair`, `abandon-tail`, `abort-session`, live-writer contention, pin advancement, and hard-stop integrity failures. The CLI should print the exact registered exit instead of requiring the operator to recognize prose.

Readiness must be operation-aware and phase-aware:

- `pre-reserve`: clean physical protocol, no active legacy journal, no open session, physical head exactly equals the committed pin, and the proposed reservation operation has no incompatible durable target;
- `pre-slot`: clean physical protocol, exact governed open session and next slot, deterministic claim absent or exactly completed, no incompatible idempotency target, no partial custody requiring disposition, and no other live writer;
- terminal: exact terminal session and a valid terminal head-pin candidate.

A `clean` parser state with `legacy_journal_path != null` is blocked. A `clean` ledger with an incompatible completed operation is blocked. Existing `inspect` remains diagnostic and must never itself authorize ARM.

The final pre-slot readiness check must occur while holding the writer lease and continue directly through countdown and capture. A standalone check followed by lease release leaves a check-to-arm race. The §5 check is an early warning; the under-lease check is the enforcing gate.

Recovery that appends control records before reservation can leave the physical head ahead of the committed pin. The CLI must report `needs_pin_commit`, provide an authenticated candidate, and expose a guarded head-pin advancement command. The runbook then requires review, commit, a clean checkout, and a repeated readiness pass. `--allow-uncommitted-head-pin` remains test-only and is never a night procedure.

### Should-fix dispositions

- **S1 contract-overstating-automation — accepted.** The existing contract may claim completeness only for physical append recovery. Its cross-layer claim is false until the registry, CLI exits, and fresh-process witnesses land. Amend it to reference the cross-layer inventory rather than saying the writer automatically resolves every refusal.
- **S2 pin-invalidation procedure — accepted.** `clean` after recovery does not imply reserve-ready when the physical head moved beyond the committed pin. Add the typed pin relation, guarded advancement command, and desk-only commit procedure.
- **S4 clean-vs-journal gate — accepted.** Readiness is a composite predicate; `inspection.state == "clean"` is insufficient. The machine gate, not operator field inspection, must enforce journal absence.

## Disagreements

- Reject another isolated `claim_id` comparison patch.
- Reject a contract-only refusal table without registry-at-raise enforcement.
- Reject reflection over exception text as the primary census.
- Reject proof references that are not executed witnesses.
- Reject any “fail fast” category based on random-token mismatch.
- Reject aborting a session while the live-writer lease is held.
- Reject treating `inspect: clean` as permission to arm.
- Reject head-pin repair through an uncommitted-pin override.
- Reject leaving any D-117 procedure under §13’s “not in force” banner.

## Open questions

None. Schema spelling may vary, but the decisions above are complete: cross-layer registry, executed exit witnesses, writer crash matrix, deterministic claim plus live lease, no crash-ambiguous fail-fast marker, section-local runbook amendments, and an operation-aware under-lease ARM gate.

## Recommendation

Implement this as one integrated structural round; none of the following is permission to land a fourth site fix alone. Ranked by near-term night-loss probability:

1. **Stable claim + held writer lease + fresh-process resume/abort CLI + writer crash matrix.** This closes the demonstrated permanent wedge while preserving concurrent-writer refusal.
2. **Mandatory operation-aware readiness at pre-reserve and under the lease immediately before ARM.** This catches legacy journals, residue, stale pins, and idempotency wedges before quiet time is spent.
3. **Cross-layer refusal registry with exact-set and executed-witness gates.** This prevents the class from reappearing at the next composition boundary.
4. **Move the D-117 procedure into §5/§6/§10 and add the pin-advancement procedure.** This makes every machine-proved exit reachable by the actual operator.

The arming blocker remains open until all four land together and the new writer crash matrix passes from fresh processes.

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Ruled exit-completeness as a cross-layer registry-at-raise invariant with executed fresh-process exit witnesses; adopted deterministic claim identity plus a held kernel writer lease, a full writer crash matrix, operation-aware under-lease ARM readiness, section-local D-117 runbook amendments, and explicit S1/S2/S4 closures.","pathspec":[],"verification":["Read the escalation record from origin/main commit 03977be; its bytes remain unchanged at current origin/main","Inspected impl/d117-ledger-recovery at c0e0257: writer lifecycle, claim idempotency, ledger recovery/abort machinery, recovery and reservation CLIs, focused tests, append contract, and runbook sections 5/6/10/13","Read RECOVERY-SHAPE-CONSULT.md, bridge-protocol/v1.1, repository intake state, Mission M0, and orchestration writer-reviewer requirements","git status --short --branch: clean on impl/d117-ledger-recovery","git diff --check: OK"],"flags":["no_edits","read_only_consult","exit_completeness","fourth_site_fix_forbidden","arming_blocker_remains_open"]}
