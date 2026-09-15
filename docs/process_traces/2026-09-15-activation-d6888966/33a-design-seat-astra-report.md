```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend B: an explicit transaction state machine, conservative liveness adapter, immutable commit, and absence-gated teardown.",
  "workspace": {
    "base_requested": "073a9763",
    "base_mode": "exact",
    "head_start": "073a976320f84dc408098b41975574cd5ca5e166",
    "head_end": "073a976320f84dc408098b41975574cd5ca5e166",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": ["DESIGN-BRIEF-33.md"],
  "verdict": {
    "rows": [
      {"row": "Design adjudication", "action": "start_now"},
      {"row": "Implementation", "action": "wait_for", "wait_for": "Lead adoption and explicit write scope"},
      {"row": "Landing", "action": "wait_for", "wait_for": "Independent regression, mutation and twelve-row gate evidence"},
      {"row": "Operational installation", "action": "do_not_start"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "/bin/launchctl print gui/501/com.joulewise.design-consult-missing-073a9763",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 113,
        "tail": [
          "Bad request.",
          "Could not find service \"com.joulewise.design-consult-missing-073a9763\" in domain for user gui: 501"
        ]
      },
      "expected": {
        "exit_code": 113,
        "tail_regex": "^Bad request\\.\\nCould not find service \"com\\.joulewise\\.design-consult-missing-073a9763\" in domain for user gui: 501\\n?$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The specified activation's records 28-* and lt-21 are absent from this checkout. Their history is attributed to the supplied brief, not independently inspected.",
      "needs": "Include those records in the landing packet."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Design inspection and the missing-service probe only; no test modules or live mutations executed. The read-only sandbox rejected the first probe's heredoc temporary file; the probe succeeded without temporary files.",
      "needs": "Execute the proposed regression and mutation matrix in the authorized implementation lane."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Adopt Q1–Q3 design | start_now | — | Transaction and adapter contracts |
| Implement installer and documentation | wait_for | Lead adoption; write scope | Shell, Python engine, tests, recovery instructions |
| A204 verified uninstall | wait_for | Shared adapter contract | Magistrate installer and its tests |
| Twelve-row landing gate | wait_for | Integrated implementation and missing records | Exact candidate head |
| Operational installation | do_not_start | Completed landing and separate operational authority | Real launchd and custody state |

### Q1 — Recommend B, with construction rules beyond “use Python”

Use `scripts/night_agent_install.py`: a stdlib transaction engine with a `LaunchctlAdapter`, injected clock/filesystem seams, explicit states, and one irreversible commit transition. Keep the shell as argument/interpreter selection followed by `exec`, without mutation or cleanup traps.

The **successful install path must contain no bootout**. Admission refuses either occupied or unknown label. This also eliminates the current unnecessary dead-man bootout before loading it again ([installer:369](/Users/edr/code/JouleWise-wt-design-iw/scripts/install_night_agent.sh:369)), avoiding I2’s prohibition on successful exit with an attempted-bootout label still loaded.

Construction rules:

- Only the engine owns the adapter; callers cannot issue extra mutations.
- Every adapter call returns an explicit outcome and captured diagnostics.
- Bootstrap requires both published plists.
- Removal/restoration requires confirmed absence and no unresolved operation capable of loading a job.
- Commit permanently disables launchd mutation and rollback.
- Exit status does not determine whether commit occurred.

**Reject A as scoped.** A shared predicate repairs the observed liveness error, including admission at [installer:302](/Users/edr/code/JouleWise-wt-design-iw/scripts/install_night_agent.sh:302), but leaves I1/I3 dependent on shell call sites, traps and subsequent statements. The current final `print` remains after the clock gate ([installer:386](/Users/edr/code/JouleWise-wt-design-iw/scripts/install_night_agent.sh:386)).

A sufficiently redesigned shell state machine could enforce the same rules; Python alone proves nothing. B makes exhaustive outcomes and restricted transitions easier to inspect and test.

**Reject C as another supervisor, timer, or arming declaration.** It introduces a second authority without closing I1/I2. The adopted design explicitly excluded per-span timers, per-plan labels and an arming declaration ([FIX contract:27](/Users/edr/code/JouleWise-wt-design-iw/docs/process_traces/2026-09-15-activation-d6888966/lt-03-fix-round-1.md:27)).

### Q2 — State machine, commit and teardown

Serialize cooperating install/uninstall processes with one lock for the GUI-domain label pair, held through reconciliation. A lock is mutual exclusion, not evidence consumed by the fence.

| State | Permitted transition | Failure or signal leaves |
|---|---|---|
| **VALIDATING** | Validate CLI, interpreter, plan, pins, records, schedule | Priors untouched |
| **ADMITTED** | Both labels confirmed absent; freeze selected span; snapshot prior files | Priors untouched |
| **PREPARED** | Render and validate both temporary plists; backups complete | Priors untouched; temporary artifacts may remain |
| **PUBLISHED** | Atomically replace each destination, then confirm both expected files | Complete published files or prior files; no new job yet |
| **LOADING** | Bootstrap night, then dead-man, recording each attempt before invocation | Both current plists present; enter teardown |
| **VERIFIED** | Both labels confirmed loaded; expected files still present | Both files remain until teardown proves absence |
| **COMMITTED** | Single commit predicate passes | Installed files stay; no rollback or launchctl calls |
| **TEARDOWN** | Reconcile attempted jobs, then restore/remove only when allowed | Exact prior state or explicitly retained conservative state |

Publish through same-directory atomic replacement; never truncate a destination or unlink it before replacement. Reject unsupported file types before mutation. Keep prior snapshots until restoration completes. Atomic publication of the *pair* is unnecessary: no bootstrap is allowed before both files exist.

**Single commit predicate**

After all bootstrap calls and verification reads:

`both confirmed LOADED ∧ both expected plists present ∧ no pending mutation/cancellation ∧ selected_open ≤ fresh_now < min(selected_close, install_close)`

The clock sample must follow the last launchd mutation. Record mutation sequence and sample ordering, not a predicted duration. The selected interval never changes to a later interval. Earlier checks remain useful refusals, but cannot authorize success.

Transition to `COMMITTED` under deferred signal handling. Thereafter output, flushing and backup disposal cannot invoke teardown. A reporting failure or signal may produce a nonzero exit with a committed installation; the files remain visible. Clock advance during post-commit housekeeping does not invalidate I1.

**One teardown routine**, shared by install abort and uninstall:

1. Freeze forward progress. Settle any in-flight invocation before reconciling it. If completion/order cannot be established, preserve both plists even if a subsequent sample says absent.
2. Attempt bootout of relevant labels while their files remain.
3. Query both labels explicitly. Any `LOADED` or `UNKNOWN` means **restore nothing, remove nothing**, retain backups, report both outcomes and paths, exit 4.
4. Only confirmed absence with no unresolved possible load permits atomic restoration of prior bytes or removal of newly created files.
5. Restoration/removal failure retains remaining files and backups and returns nonzero. Re-entry after completed teardown is a no-op.

Signal handlers set cancellation state rather than throwing asynchronously through file operations. Repeated signals do not restart teardown. For an uncatchable kill, safety comes from ordering: any potentially loaded job already has its plist; deletion occurs only after absence is established.

**Loaded priors:** refuse before publication or bootout, preserving their bytes and loaded-ness exactly. Do not unload and then “restore” loaded-ness by bootstrapping in cleanup. Existing unloaded priors are restored after confirmed removal of this attempt’s jobs; otherwise retain this attempt’s plists so the fence reads the correct plan. The fence follows each plist’s `--plan` reference ([fence:726](/Users/edr/code/JouleWise-wt-design-iw/scripts/magistrate_watchdog.py:726)).

**Reject automatic prior-job replacement/reloading.** It adds rollback mutations after the deadline and cannot promise restoration of launchd’s complete prior state.

**Proof boundary:** these guarantees preserve an initially fence-visible state under exclusive ownership. No installer can guarantee literal I2 for an already fileless loaded job if killed before its first repair, or against an unrelated process deleting files/reloading labels. Such inherited violations require explicit recovery; a successful refusal must not be presented as repairing them.

### Q3 — Executed liveness semantics

The direct probe in V1 returned **113**, stdout empty, with this stderr verbatim:

```text
Bad request.
Could not find service "com.joulewise.design-consult-missing-073a9763" in domain for user gui: 501
```

Use separate process and liveness outcomes:

| Observation | Liveness |
|---|---|
| Normal exit 0 | `LOADED` |
| Exit 113, empty stdout, exact missing-service diagnostic matching the requested label and GUI domain | `ABSENT` |
| Any other code/output combination, spawn failure, interruption, decoding failure or incomplete response | `UNKNOWN` |

Preserve raw return code/stdout/stderr. Match the full service/domain diagnostic, not merely “Bad request” or a substring. Unexpected platform wording safely becomes unknown.

`may_be_loaded = state != ABSENT` governs admission and deletion. **Successful verification requires `state == LOADED`; UNKNOWN must never satisfy it.**

The fake launchctl must maintain loaded state independently of its response:

- Loaded: marker/state present, print returns 0.
- Absent: state absent, print returns 113 and the matching diagnostic.
- Unknown: print returns 9, malformed 113, interruption, etc., **without changing loaded state**.
- Mutators independently model their return code and actual effect: failed bootstrap may load; successful bootout may leave loaded; an interrupted invocation may complete later.

Both current fixtures incorrectly use exit 1 for absence ([basic fixture:79](/Users/edr/code/JouleWise-wt-design-iw/tests/test_install_night_agent.py:79), [teardown fixture:866](/Users/edr/code/JouleWise-wt-design-iw/tests/test_install_night_agent.py:866)).

**Reject “every nonzero means absent,” and reject bare `113 ⇒ ABSENT`.** Neither distinguishes a proven missing service from a query failure.

### Q4 — Migration and landing requirements

**Preserve the public CLI and schedule JSON.** Continue deriving install/render Python from the measurement venv or explicit `--python`, including minimum-version and clean-environment preflight checks. Keep uninstall usable without that venv, courier or valid pins: its engine path must be stdlib-only and compatible with the available system interpreter, without importing the driver first ([installer:43](/Users/edr/code/JouleWise-wt-design-iw/scripts/install_night_agent.sh:43), [handback:419](/Users/edr/code/JouleWise-wt-design-iw/docs/process/NIGHT_HANDBACK.md:419)).

Make render and uninstall mutually exclusive; reject their combination before any launchctl call. Render mode must never construct/use the adapter, including failure cleanup.

`scripts/run_night.py schedule` remains an advisory derivation command with its existing keys and refusal behavior ([schedule:1037](/Users/edr/code/JouleWise-wt-design-iw/scripts/run_night.py:1037)). Callers may continue using it for notices and plist comparisons. They must not treat its historical `install_spans_today` as installation authorization; the transaction selects its interval from a fresh admission-time date and freezes it.

Update together:

- **Runbook §1.3:** replace unconditional rollback claims at [1405](/Users/edr/code/JouleWise-wt-design-iw/docs/phase_2/derivation_night_runbook.md:1405) with committed/restored/retained outcomes and unknown-query behavior.
- **Runbook §1.4:** make recovery commands explicitly conditional on successful uninstall and comparison. The current sequential example can proceed to unpublish the plan after failed uninstall ([1601](/Users/edr/code/JouleWise-wt-design-iw/docs/phase_2/derivation_night_runbook.md:1601)).
- **NIGHT_HANDBACK:** document the final commit observation, retained-state recovery, and that exit 4 stops retirement/unpublication.
- **Courier prompt:** extend its handback continuation at [20](/Users/edr/code/JouleWise-wt-design-iw/docs/process/NIGHT_COURIER_PROMPT.md:20): retained/unknown state stops uninstall-dependent cleanup and successor arming; report the recorded outcome and preserved paths.

Preserve these refusal tokens and current exit codes:

`install_span_closed`, `install_outside_span`, `plan_t0_in_the_past`, `night_agent_already_loaded`, `plan_outside_custody_root`, `night_plan_malformed`, `plan_schedule_unrepresentable`, `install_spans_unresolvable_on_day`, `plan_t0_not_minute_aligned`, `plan_t0_ambiguous_local_time`.

For unknown admission, retain `night_agent_already_loaded` with `state=unknown` and raw query diagnostics; update its documented predicate. Preserve existing bootstrap/verification failure prefixes, but emit “rolled back” only after verified restoration.

**Regression matrix**

| Axis | Required cases |
|---|---|
| Clock | Advance before/after every filesystem and adapter step; during both verification reads; exact close; either limiting bound; adjacent spans, gaps, midnight, DST; post-commit advance |
| Signals | INT/TERM/HUP at every state and during each operation; repeated signal during teardown; KILL snapshots and late child completion |
| Priors | Neither/one/both files; unloaded/loaded/unknown labels; byte-identical restoration; publication/restore failure |
| Launchctl | Each label independently loaded/absent/unknown; error with and without mutation; false-success bootout; unresolved invocation |
| Modes | Install, uninstall, render success/failure; conflicting modes; zero launchctl calls throughout render |
| Oracle | Exit/result, independently stored job state, exact file bytes, backups, operation ordering and actual fence result at relevant plan times |

**Mutation must-die set:** remove/move final clock read; `>=`→`>`; collapse either `min` operand; reselect a later span; admit/verify/delete on UNKNOWN; accept mismatched 113; unlink before verified absence; skip either label; restore old bytes under a possibly loaded new job; omit pending-operation protection; bootout admitted priors; permit mutation/rollback after commit; route render through launchctl.

Carry forward earlier constant, DST, calendar, arithmetic and documentation mutants. Use state/operation ordering assertions, not exact shell call counts.

The existing twelve-row ledger requires independent contract/execution lenses, dictated dispositions, delta audits and same-signature statements, fresh counter-review, lead design/prune gates, replay, final-head review, CI/integration review and terminal review ([ledger:16](/Users/edr/code/JouleWise-wt-design-iw/docs/process_traces/2026-09-15-activation-d6888966/lt-90-gate-ledger-draft.md:16)). Bind new evidence to the exact landing head. Replay relevant modules individually during implementation; reserve the required full replay for the authorized lead lane. The gate must include baseline reproduction and isolated mutant failure, not merely green tests.

**Reject a caller rewrite that bypasses the shell contract, and reject treating a green legacy fixture as liveness evidence.**

### Q5 — A204 and shipped spans

**Cover A204’s uninstall now through the same adapter and absence-gated removal primitive**, as a separately scoped change. It is the one-label case; it needs no night timing policy. Its current unconditional removal after ignored bootout failure is directly exposed ([magistrate installer:191](/Users/edr/code/JouleWise-wt-design-iw/scripts/install_magistrate_watchdog.sh:191)). Require its own fake-launchctl matrix before use.

**Reject postponing this known uninstall defect merely because the night engine changes language.** Also reject expanding this landing into a redesign of the magistrate’s adoption/lock-seeding installation workflow.

Keep `INSTALL_SPANS = (("00:00", "24:00"),)` and both 3600-second constants unchanged ([constants:67](/Users/edr/code/JouleWise-wt-design-iw/scripts/run_night.py:67)). Whole-day defaults still have midnight and plan-close boundaries and do not protect against failed cleanup. Reject narrowing spans or introducing a duration ceiling as a substitute.

### Q6 — Preserve contracts and counterexamples; discard incidental mechanisms

Preserve:

- The post-mutation commit observation and frozen selected close.
- Bootout-before-removal **plus confirmed absence**, group retention on uncertainty, and no bootstrap in teardown.
- Render-only’s complete launchctl exemption.
- All FIX-1..10 counterexamples: selected-span crossing; failed-install restoration/fencing; schedule representability; watchdog arithmetic handling; minute/fold rejection; resolved DST-span validation; mutation strength; same-day naming; adoption wording; documented refusal literals. Their mapping is recorded in [FIX contract:13](/Users/edr/code/JouleWise-wt-design-iw/docs/process_traces/2026-09-15-activation-d6888966/lt-03-fix-round-1.md:13).
- Post-commit housekeeping failure/clock-advance preservation ([tests:1043](/Users/edr/code/JouleWise-wt-design-iw/tests/test_install_night_agent.py:1043)).
- Existing pins, calendar shapes, constants, schemas, write-once records and scientific registration constraints.

Discard shell EXIT/errexit dependence, `bootout || true` as evidence, boolean print predicates, direct destination writes, redundant successful-path bootout, and exit-code-derived commit state.

**Reject preserving obsolete shell implementation details verbatim.** Preserve refusal tokens, governed behavior and counterexamples; explicitly disposition fixture changes such as shell-function extraction, command counts and synthetic exit-1 absence. Atomic rendering changes where an I/O fault occurs, so retain the failure scenario through an equivalent injected operation failure rather than silently dropping it.

## Critical path

Lead adoption of Q1–Q3 → explicit implementation scope → engine, adapter, fixtures and recovery documentation → independent regression/mutation evidence → twelve-row gate on the exact candidate.

A204 depends on the shared adapter/removal contract, then its own tests. Operational installation depends on completed landing and separate authority. Records `28-*` and `lt-21` must join the landing packet before its historical closure claims are accepted.