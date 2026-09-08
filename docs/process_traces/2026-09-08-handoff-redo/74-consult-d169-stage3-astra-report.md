```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Stage 3 needs an authenticated pack GO producer and launch consumer, confirmation custody, and evidence-backed T-0 rehearsal closure; D-171 already delegates launch authority.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "1c83f2af48df5611c7bbf824bec818209c252d0d",
    "head_end": "1c83f2af48df5611c7bbf824bec818209c252d0d",
    "upstream_end": "1c83f2af48df5611c7bbf824bec818209c252d0d",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 5,
      "should_fix": 1,
      "nit": 0,
      "total": 6
    },
    "findings": [
      {
        "id": "R1",
        "severity": "blocker",
        "title": "Pack-bound preparation and D-149 GO issuance are absent",
        "locations": ["joulewise/night_gate.py:738", "scripts/run_night.py:1149", "joulewise/arm_readiness.py:8441"]
      },
      {
        "id": "R2",
        "severity": "blocker",
        "title": "Launch consumption does not require or bind a D-149 receipt",
        "locations": ["scripts/launch_window.py:239", "joulewise/arm_readiness.py:9573", "joulewise/t0_rehearsal.py:790"]
      },
      {
        "id": "R3",
        "severity": "blocker",
        "title": "The unattended confirmation-pair custody and inheritance route remains uninstalled",
        "locations": ["scripts/launch_window.py:126", "scripts/launch_window.py:274", "docs/phase_2/window_runbook.md:1448"]
      },
      {
        "id": "R4",
        "severity": "blocker",
        "title": "T-0 rehearsal still lacks authenticated producer evidence and a complete acceptance route",
        "locations": ["joulewise/t0_rehearsal.py:433", "joulewise/t0_rehearsal.py:710", "joulewise/t0_rehearsal.py:790", "joulewise/t0_rehearsal.py:1079"]
      },
      {
        "id": "R5",
        "severity": "blocker",
        "title": "Pack-class authorization must distinguish G2-b from the transaction it qualifies",
        "locations": ["docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md:97", "docs/process/state_kernel.json:6531", "docs/decision_log.md:10642"]
      },
      {
        "id": "R6",
        "severity": "should_fix",
        "title": "The stage-3 work graph and acceptance pointers need a ruling-backed reconciliation",
        "locations": ["docs/process/state_kernel.json:5455", "docs/process/state_kernel.json:6005", "docs/process/state_kernel.json:6531"]
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "rg -n 'night_refused_class_unbuilt|stage 3 not implemented' joulewise/night_gate.py && rg -n '^def (launch|_consume_launch_capability|evaluate_g7)|arm_disposition.*NO_GO.*GO' scripts/launch_window.py joulewise/arm_readiness.py joulewise/t0_rehearsal.py && git status --porcelain && git rev-parse HEAD refs/remotes/origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1c83f2af48df5611c7bbf824bec818209c252d0d",
          "1c83f2af48df5611c7bbf824bec818209c252d0d"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1c83f2af48df5611c7bbf824bec818209c252d0d"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The consult is complete, but stage-3 implementation requires decisions on receipt bindings, G2-b authorization, confirmation custody, rehearsal execution authority, and dependency installation.",
      "needs": "Assemble and cold-gate the ruling packet below before issuing implementation write scopes."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Read-only source and kernel inspection only. No repository-wide suite, live capture, privileged control, installer, or external-state verification was performed.",
      "needs": "Lead owns final-head verification and later quiet-machine acceptance."
    }
  ]
}
```

## Findings

The smallest sound design is **a pack-specific orchestration path in the existing night driver, one authenticated D-149 receipt contract, and enforcement inside the existing launch-capability consumer**. Retain the scheduler, watchdog, courier, atomic launch consumption, anonymous-FD handoff, and frozen pack chain.

D-171 already delegates E-10 invocation, transaction GO, and step-6 confirmation. Fresh per-window permission from Ed is not the missing mechanism. Its concrete installation and the remaining rehearsal obligations are.

### R1 — Pack preparation and D-149 issuance are missing

These are three distinct missing mechanisms:

| Mechanism | Current code-path evidence | Governing fence |
|---|---|---|
| Pack-bound night inputs and orchestration | `NightPlan` has chain/checkout/custody fields but no pack, ARM, manifest, readiness-authority, or confirmation binding: `joulewise/night_gate.py:183`. The driver evaluates a receipt before starting its chain: `scripts/run_night.py:1149`. | Stage-1 ruling R-1 and stage table reserve pack work for stage 3: `MAGISTRATE-RULING-UNATTENDED-STAGE1.md:46`, `:219`. |
| Actual `TRANSACTION_PACK` evaluation | `joulewise/night_gate.py:738` unconditionally refuses with `night_refused_class_unbuilt`. Removing that branch alone leaves C1/C2 unevaluated; the later C1 implementation is diagnostic-only at `:908`. | R-4 requires all five conditions PASS for packs; no `no_pack_by_design` exemption. |
| Evidence-backed D-149 GO production | `joulewise/arm_readiness.py:8441` produces **ARM** `arm_disposition: GO`. Its receipt contains pack/ARM evidence, not the D-149 five-condition authorization. `joulewise/t0_rehearsal.py:710` reads a different D-149 schema; it is not a producer. | D-149 requires a custodied receipt before capture. D-167 replaces the old council gate for v5 but preserves conditions 2–5. |

The T-0 clock producer itself is substantially implemented. Do not rebuild it: `author_arm_readiness_evidence_t0()` authors fifteen ARM_ONLY evidence receipts at `joulewise/arm_readiness_evidence_t0.py:2245`; its PROBE clock branch, R1-before-census enforcement, and exact-Off checks already exist.

**Minimum addition:** an explicit pack preparation phase, followed by evidence-backed C1–C5 issuance. Preparation must not itself receive a premature measurement GO merely to make the current driver’s ordering convenient.

### R2 — The sole launcher lacks the GO consumer and its durable binding

The concrete enforcement gap is:

- `scripts/launch_window.py:38`: no D-149 receipt input.
- `scripts/launch_window.py:239`: assemble inputs → install handoff → consume ARM capability → verify → `execve`.
- `joulewise/arm_readiness.py:9573`: `_consume_launch_capability()` has no GO-receipt parameter or authentication.
- `joulewise/arm_readiness.py:9451`: consumed-launch replay consequently cannot authenticate that authorization.
- `joulewise/t0_rehearsal.py:790`: G7 always returns `UNRULED`.

Thus a caller can reach the launcher’s consumption path without demonstrating D-149 C1–C5. The night-class refusal currently prevents the unattended driver from exploiting this gap; it does not install the missing launcher precondition.

The owning kernel row explicitly assigns this consumer to `UNATTENDED-LAUNCH-01`, including production rejection of an otherwise valid `T0_UNATTENDED_SUPERVISED_REHEARSAL` receipt. `S9-06-WINDOW-T0-GO-RECEIPT-GATE-01` describes the same missing mechanism and should close against the same implementation.

**Minimum addition:**

1. Authenticate the GO receipt and its evidence before capability consumption.
2. Recheck the supplied bytes and bindings inside `_consume_launch_capability()`, rather than trusting an earlier CLI check.
3. Record its identity/digest in the atomic consumption record.
4. Replay that binding through `verify_consumed_launch()` and lifecycle start.
5. Reject absent, stale, wrong-class, wrong-pack, wrong-ARM, incomplete, or condition-failing receipts before consumption and `execve`.

Use the existing ARM consumption as the single-use linearization point. A second independent “GO consumed” lock would add a crash-consistency problem without improving one-shot behavior.

The stage-1 ruling R-8 already selects the launch-family registration route for `launch_go_receipt_missing` and `launch_go_receipt_invalid`: family set at `arm_readiness.py:223`, D-078 amendment documentation, emission sites and regressions. These codes are separate from the readiness-row vocabulary; do not churn the frozen readiness registry simply to add launch refusals.

### R3 — Confirmation custody must reach the launcher and its child

D-171 §2 delegates `hC` custody but explicitly reserves its concrete route for the cold gate: `docs/decision_log.md:10637`.

The current launcher requires the confirmation pair during ARM verification (`scripts/launch_window.py:126`), consumption (`:244`), and child lifecycle start (`:274`). The runbook still identifies the missing child supply line at `docs/phase_2/window_runbook.md:1448`.

Passing flags to the launcher does not pass those flags to the manifest’s `execve` command.

**Recommendation for ruling:** use a mode-0600, create-once confirmation record in transaction custody, containing the previously confirmed table digest and table locator. Bind that record into the desk-frozen pack-night inputs. The launcher and lifecycle start read the same authenticated record.

Do not compute the expected digest from whatever table happens to be present at T-0. That would erase the distinction between confirmation and subsequent verification. Do not expand the exact `window.env` allowlist implicitly; the cold gate must choose and document the child’s supply route.

### R4 — T-0 rehearsal needs producers, authentication, and an executable acceptance route

The kernel’s historical “seven blockers / six self-declaration gates” description is a starting checklist, not a substitute for checking this head.

Current evidence gaps are concrete:

| Gate | Remaining mechanism |
|---|---|
| G1 | Execution evidence proving the complete governed sequence and descendants ran with fd 0 bound to `/dev/null`, completed, and neither prompted nor hung. The evaluator reads declared process fields at `t0_rehearsal.py:433`; the night child presently omits an explicit `stdin=DEVNULL` at `run_night.py:424`. |
| G2 | Bind the census to the **actual** pack/attempt T-0 namespaces. The CLI already crawls custody at `scripts/rehearse_t0_unattended.py:85`; the remaining issue is that the manifest chooses `t0_namespace` at `:137`. Do not describe this head as lacking any filesystem crawl. |
| G3 | A governed HID capture with argv, raw output, boot identity and an in-sequence timestamp. Current evaluation accepts a text artifact and compares its number to the span: `t0_rehearsal.py:511`. |
| G5 | Recompute C1–C5 from authenticated evidence. Current code checks declared PASS values and referenced hashes, not their semantics: `:719`. |
| G6 | Derive the production-root census independently and prove dedicated runs, custody, ledger and backup paths. Current roots come from the submitted manifest: `scripts/rehearse_t0_unattended.py:149`; the evaluator checks containment against that list at `t0_rehearsal.py:780`. |
| G7 | Invoke the real production consumer with an otherwise valid rehearsal receipt; preserve its **class-specific** refusal and prove no consumption/capture occurred. Currently hard-coded `UNRULED`: `:790`. |
| G8 | Authenticate timestamped process observations and use the production census predicate. The current token regex misses `codex-helper` and `claude-code`: `:57`; the evaluator trusts declared lineage at `:805`. Stage-1 R-3 allows the clean census timestamp to establish agent absence; do not invent an agent’s self-reported exit. |
| G9 | Produce and authenticate actual launch, consumption, capture, both backups, close-out and restoration records. Current COMPLETE labels plus artifact hashes are insufficient: `:859`. |
| G10 | Preserve the real software boundary checks, but replace positive-control booleans with governed raw evidence, boot/time bindings and observed refusal. Current physical-control checks consume self-declared fields: `:1079`. |

G4’s clock recomputation and G10’s real software boundary calls are useful existing seams. They need regression protection, not blanket replacement.

The controlling obligations remain the August 23 T-0 ruling’s ten-gate table and its dated D-170 amendment. The abandoned partial fix is explicitly starting material, not an applicable patch.

**What “T0 rehearsal obligation” means**

It means one isolated, non-claim, end-to-end rehearsal with:

- G1–G10 all PASS; no `UNRULED` counted as success.
- Zero operator action during T-0 and zero agent presence during T-0/capture.
- Real machine-authored clock evidence and a mechanically green D-149 evaluation.
- Dedicated rehearsal identity, custody, ledger, runs and backups.
- A successful rehearsal lifecycle, plus a separate production-entry rejection of that valid rehearsal authority.
- Software falsifier observations and the adjacent, outside-T-0 privileged anchor positive control required by the ruling.
- Launch/relaunch evidence satisfying the lifecycle row.

The positive control remains specifically Ed-owned under the cited T-0 ruling unless applicable authority explicitly amends it. This is a qualification obligation, not a requirement for Ed to attend every campaign launch.

**G2-a cannot discharge this obligation.** It intentionally has no frozen pack, ARM ceremony, pack launcher, or C2 PASS. It can supply genuine scheduler/capture/courier observations, but cannot establish pack authorization, confirmation transport, ARM consumption, clock-authoring acceptance, or G7.

It also cannot replace `NIGHT-REHEARSAL-01`: that row requires a **prior** launchd-started `REHEARSAL_STUB`, actual courier delivery, morning-before dead-man stand-down, and a fresh post-watchdog rehearsal. Coldgate D1 adds the morning-before case at `coldgate-d1-RULING.md:115`.

G2-b’s ARM-ABORT and one-block proof are a third, distinct qualification.

### R5 — C1 creates a bootstrap conflict unless explicitly ruled

The stage-1 table assigns `V5-TRANSACTION-GO-01` to C1 for every `TRANSACTION_PACK` night. G2-b is explicitly in that class.

But `V5-TRANSACTION-GO-01` depends on G2-b passing: `docs/process/state_kernel.json:6531`. Applying the table literally prevents the qualifying G2-b from running.

D-171 delegates who grants transaction GO; it does not by itself define a mechanically checkable G2-b-specific C1 contract.

**Recommendation:** keep G2-b on the full pack path, with an explicit purpose-bound authorization:

- **G2-b:** authenticated magistrate authorization for the registered, non-claim one-block shakedown.
- **Campaign:** authenticated transaction authorization after G2-b and the applicable readiness gates.

Both require full C2–C5. Bind purpose, exact pack/attempt, permitted chain, and claim eligibility into the receipt. Never obtain this distinction by labeling G2-b `DIAGNOSTIC_NO_PACK`.

A related ruling is necessary for the isolated T-0 rehearsal: specify the narrowly bounded rehearsal execution entry while the production entry rejects rehearsal authority. A general `--allow-rehearsal` switch on the production launcher would undermine G7.

### R6 — Reconcile scheduling and acceptance before implementation

The current graph has:

- `NIGHT-REHEARSAL-01` blocked on the post-watchdog rehearsal event.
- `T0-UNATTENDED-01` hard-start dependent on `NIGHT-REHEARSAL-01`.
- `UNATTENDED-LAUNCH-01` hard-start dependent on `T0-UNATTENDED-01`.
- Yet T0’s G7 acceptance requires the launch consumer.
- `T0-REHEARSAL-PRODUCERS-01` queued with a close dependency on T0.
- S9-06 queued as a separate description of the GO-consumer gap.

This is an acceptance/scheduling knot: waiting for complete T0 closure before building the consumer prevents complete T0 closure. The lead must install a staged build/qualification graph without declaring any unmet live obligation satisfied.

Also reconcile the acceptance reference to `REHEARSAL_PRODUCER_WORK_ORDER`: that symbol is absent from current `joulewise/t0_rehearsal.py`. Install an enumerated checklist in a ruled home or replace the stale pointer explicitly.

### Smallest proposed implementation

The following is a proposal for the cold gate, not an installed contract.

**Desk phase**

Freeze a versioned pack-night specification binding the reviewed driver and measurement heads, pack/freeze identity, purpose-specific authorization, exact chain/manifest/environment bytes, confirmation record, dedicated roots, and schedule. Preserve current diagnostic/stub schemas; their exact-key contracts should not change silently.

**Timer phase**

1. Reuse existing stale-plan, missed-fire, checkout, chain-identity, quiet-machine and once-only guards. Claim the attempt before any T-0 reservation or other side effect.
2. Run the existing six capture steps: clock-reference, clock-disable, quiet-mac-prep, prewindow-check, ledger-readiness, ledger-reservation.
3. Run `author_arm_evidence_t0.py`, then ARM as the next new process after author exit. Parse outputs in the already-running controller; do not insert `jq`, `cat`, or a census subprocess into that governed gap.
4. Verify ARM and issue the D-149 receipt from authenticated C1 authority, ARM/T-0 evidence, quiet census, boot/clock evidence and enforced no-retry state.
5. Invoke `launch_window.py` once with the receipt. It authenticates and binds GO at consumption, preserves FD 198, and `execve`s the manifest’s exact chain.
6. The night driver survives, monitors the child process group, and records its outcome. Reuse existing courier, result publication and dead-man machinery only after termination is proven.

Reuse `_run_chain_once()`’s command/monitoring seam (`run_night.py:401`) rather than adding another supervisor. Keep the authoritative pack chain distinct from any preparation wrapper; both must have explicit identities and roles.

**Timing fences stay separate**

- Continuous quiet dwell and R0→author RAW span: retain governed predicates.
- R1-before-census ordering and 30-second batch ceiling: unchanged.
- D-170 issuance liveness: ordinary monotonic, `0 ≤ origin − R1_finish ≤ 600 s`.
- RAW anchor: separate 5 ms gate; never added to the 0.5 s reference bound.
- Evidence horizons: 20 minutes volatile, six hours procedural.
- ARM lifetime: 300 seconds by default (`arm_readiness.py:8224`).

No GO timestamp refresh extends any underlying deadline. Budget preparation, capture and required close-out into the night’s deadline. Preserve coldgate D1’s pre-completion dead-man stand-down and the prohibition on couriering over a live or ambiguously terminated chain.

### Ordered implementation and replay plan

| Order / seat | Proposed scope | Required evidence |
|---|---|---|
| 1. Magistrate packet assembly; fresh cold adjudicator plus distinct contract refuter | Ruling, decision/kernel installation, exact acceptance maps; no implementation yet | Resolve the questions below and distinguish build dependencies from live closure. |
| 2. Launch/receipt implementer | `joulewise/night_gate.py`, `joulewise/arm_readiness.py`, `scripts/launch_window.py`; `tests/test_night_gate.py`, `tests/test_launch_window.py`, relevant ARM schema/integration tests | GO producer/validator contract; strict bindings; missing/stale/class refusals; atomic consumption binding; historical replay compatibility. Lead-owned refusal documentation lands before emission. |
| 3. Night orchestration implementer, after the interface is fixed | `scripts/run_night.py`, `tests/test_run_night.py`; installer files only if the ruled plan version requires changes | Producer-driven preparation→ARM→GO→launch integration, closed stdin, exact interpreter/root, one-shot failures, monitored process group and preserved reporting guards. |
| 4. T-0 evidence/rehearsal implementer | `joulewise/arm_readiness_evidence_t0.py`, `scripts/capture_t0_step.py`, `joulewise/t0_rehearsal.py`, `scripts/rehearse_t0_unattended.py`, their focused tests | Additive observational records; authenticated G1–G10 inputs; no changes to existing clock fact keys or horizons; actual G7 consumer rejection. |
| 5. Independent execution and contract reviewers | Read-only integrated candidate | Mutation-shaped audit; fix rounds followed by fresh delta review. Magistrate owns final contextual verification and D-118/D-121 closure. |
| 6. Lead-controlled qualification | Separate rehearsal custody and quiet-machine session | Harvest launchd stub acceptance; run isolated T-0 qualification; then real-pack G2-b ARM-ABORT and one-block proof. No agent active during capture. |
| 7. Magistrate close-out | Runbook, receipt template, kernel and reports under explicit scopes | Install E-10/confirmation instructions; close overlapping rows against shared evidence; preserve remaining campaign/claim gates. |

Every implementation brief needs the D-170 clause map: ruling clause → production site → biting assertion → counterfactual.

Focused replay must include:

- Missing GO, malformed/incomplete receipt, each failed C condition, expired evidence, wrong boot/head/pack/ARM/manifest/confirmation.
- A fully valid rehearsal receipt refused **by class**, before consumption.
- Mutation between CLI verification and callee consumption.
- Duplicate timers and crashes before/after consumption: at most one launch; no automatic re-arm.
- Confirmation transport through the real child start route.
- Agent-census exit 0, exit 1 with output, exit 2, timeout, and helper-name variants.
- Dead-man before the night, during preparation/capture, and with ambiguous termination; no premature courier.
- Producer-emitted rehearsal evidence only, with omitted/wrong namespace, stale HID evidence, arbitrary PASS labels, incomplete root census and fabricated positive-control fields rejected.
- Author/ARM timing boundaries and refusal codes, without substituting software fixtures for the physical positive control.
- Historical strict-schema replay and clean-clone pack proof at the final integrated head.

`T0-LIVENESS-BOUND-EMPIRICAL-01` separately requires at least three real rehearsal bundles with stated margins below 600 seconds, or a cold-gate reruling. One successful T0 rehearsal does not close that row. The packet should state whether it blocks launch qualification or remains the registered empirical limitation; do not silently promote or waive it.

### Cold-gate ruling packet skeleton

**Inputs:** exact revision; stage-1 R-1/R-3/R-4/R-8/R-10; coldgate D1; August 23 T0 ruling and D-170 amendment; D-149/D-167/D-169/D-171; current kernel rows; this refusal-site census; proposed receipt/consumption examples and explicit field bindings.

For artifact-equality claims, include the named-revision pair, JSON pointers and observed values. For behavior, include exact execution evidence or the refusing code path, as D-170 requires.

**Questions requiring dispositive answers before code:**

1. **C1 authority:** What exact artifact authorizes G2-b, campaigns, and isolated T0 rehearsal? How is G2-b authorized before transaction GO?
2. **Receipt contract:** Which versioned schema is authoritative? What binds purpose, pack, ARM ordinal/digest, manifest, heads, boot, evidence, custody and freshness?
3. **Consumption:** Confirm mandatory checking inside launch-capability consumption, durable GO binding, replay behavior, and refusal vocabulary. What is the historical compatibility rule?
4. **Confirmation:** Approve the concrete `hC` source and child supply line. What authenticates its original confirmation independently of the current table?
5. **Preparation ordering:** Approve the driver’s preparation state and monitored subprocess sequence, including ARM-next-process ordering and the deadline accounting.
6. **Rehearsal authority:** How does the isolated rehearsal exercise the shared lifecycle while production rejects its class? What mechanically prevents use of production roots/ledgers/backups?
7. **Rehearsal closure:** Name each G1–G10 producer and evaluator obligation; adjudicate census-timestamp lineage, positive-control evidence and any claimed prior qualification reuse.
8. **Scheduling:** Resolve the T0/launcher acceptance knot; assign S9-06 and producer-row ownership; state whether build may precede harvested `NIGHT-REHEARSAL-01` acceptance.
9. **Empirical liveness:** Is the three-bundle margin study a pre-launch gate or retained limitation? Preserve the current bound unless explicitly reruled.

Each answer should carry authority, selected option, rejected alternatives, exact installation paths, acceptance counterfactuals, and remaining live/Ed-owned obligations.

## Residual risk

Inspection was against clean detached head `1c83f2af`, with local `origin/main` equal to it. No files changed and no tests or hardware actions ran.

External rehearsal custody, actual courier delivery, privileged-control records, production pack estate, and feasible campaign-night budgets were not verified. This report establishes implementation gaps and a proposed design; it does not qualify a launch.