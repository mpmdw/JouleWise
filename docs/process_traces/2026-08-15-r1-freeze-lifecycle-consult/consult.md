```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Adopt a hybrid: content-bound durable freeze evidence plus a governed successor-family tool for real semantic changes, never routine time-based refresh.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "head_end": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "upstream_end": "c0b7068d774b1e82bd97165d081333552fa86760",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "C_CONTENT_BOUND_PLUS_SUCCESSOR_LIFECYCLE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "summary": "The 24-hour policy misclassifies content-bound freeze proofs as perishable even though passage of time does not invalidate what they attest."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "summary": "A successor-pack tool remains mandatory for genuine pack, registry, evidence, or projection changes and for the one-time migration from the expired v1 packs."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "summary": "Freshness must be governed per row or homogeneous receipt class, with temporal evidence checked against an arm-to-consume budget and volatile predicates rechecked at consumption."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git show 15d00d2:docs/process_traces/2026-08-15-readiness-council/council-verdict.md | rg -n 'Phase 0|Phase 2|Phase 3|R1 freeze-evidence'; git show 15d00d2:docs/process_traces/2026-08-15-readiness-council/refuter-outputs/refuter-verdicts.md | sed -n '3,15p;81,90p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Phase 0 orders the R1 lifecycle ruling before code.",
          "Phase 2 orders one atomic last-pack-byte re-freeze.",
          "Both refuter lenses reduce cluster A to one expiry/lifecycle defect."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "CLUSTER A ADJUDICATED"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -n '^_EVIDENCE_VALIDITY_NS|^_VOLATILE_EVIDENCE_VALIDITY_NS|^_NONVOLATILE_EVIDENCE_VALIDITY_NS|^EVIDENCE_RECEIPT_KEYS|^def _freeze_evidence_for_arm|^def generate_freeze_receipt|evidence_expirations =|valid_until = min' joulewise/arm_readiness.py joulewise/arm_readiness_evidence.py joulewise/arm_readiness_evidence_t0.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Generic evidence uses an implementation-only 86400-second horizon.",
          "T-0 evidence separately uses 20-minute and 6-hour horizons.",
          "ARM inherits the minimum deadline from evidence receipts."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "valid_until = min"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD; git rev-parse origin/main; git symbolic-ref --short -q HEAD || true",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
          "c0b7068d774b1e82bd97165d081333552fa86760"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "c0b7068d774b1e82bd97165d081333552fa86760"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Implementation must wait for the R1 contract amendment and its ordered cold gate.",
      "needs": "Magistrate rules the freshness classes and successor-family contract; Ed approves the irreversible Phase-2 successor publication."
    },
    {
      "id": "B1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The detached worktree is the council-audited 8937dec code head; the later council records were inspected from immutable commit 15d00d2, which is an ancestor of current upstream.",
      "needs": "Recheck implementation targets against current main before code lands."
    }
  ]
}
```

## Findings

### F1 — Blocker: adopt C, not A or B verbatim

My recommendation is a hybrid:

> Freeze evidence is valid according to the state it attests, not according to elapsed time. Content-bound evidence remains valid until a named dependency changes or a semantic successor exists. A governed successor-pack lifecycle handles those real changes. Only T-0 observations of mutable state receive short horizons.

I disagree with A’s remaining boot-session binding for stable desk evidence. Rebooting does not alter a doctrine digest, plan identity, registry binding, or test result tied to unchanged dependencies. Keeping the boot constraint would preserve a smaller version of the same operational defect.

The current 33 receipts are eleven generic receipts in each of three packs. Their derivations in [arm_readiness_evidence.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/joulewise/arm_readiness_evidence.py:504) attest committed artifacts, frozen structures, deterministic derivations, or focused test executions—not live T-0 machine state.

| Freshness class | Evidence | What can actually make it stale |
|---|---|---|
| `CONTENT_BOUND` | All 33 generic receipts: `ACCEPTANCE_OWNER`, `DOCTRINE_PIN`, `ESTIMATOR_IDENTITY`, `MINT_TRUST`, `MULTICELL_MINT`, `PACK_AUTHENTICATION`, `PACK_FAMILY`, `REASON_CODE_COVERAGE`, `RECEIPT_ORACLE`, `RECOVERY_LEDGER_TEST`, `THREE_WINDOW_REGRESSION` | Relevant pack bytes, registry, source/dependency digests, normalized plan projection, or semantic successor changes |
| `CONTENT_BOUND` specialized | `IDENTITY_PIN_PROJECTION`, `TERMINAL_REVIEW`, `OFFLINE_INPUT_INVENTORY`, same-head `DRY_RUN_REHEARSAL` | Bound commit/content changes, inventory bytes change, or supersession |
| `TIME_BOUND` | `CLOCK_ATTESTATION`, `CLOCK_PROBE`, maintenance/process/machine/power/powermetrics/backup snapshots | The observed live condition can drift after observation; same boot and a short horizon bound TOCTOU |
| `SESSION_STATE_BOUND` | `LEDGER_RESERVATION`, root freshness, launch/session bindings | Reservation, root, lock, session or capability state changes; these need semantic revalidation, not merely a clock |
| `TEMPORAL_CAPABILITY` | ARM receipt | Live state drift, reboot, supersession or consumption; keep the short same-boot deadline and single-use rule |

The 24-hour generic horizon at [arm_readiness_evidence.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/joulewise/arm_readiness_evidence.py:35) does not detect any of the content invalidators above. Conversely, it does not protect against a relevant dependency or environment change made five minutes after authorship. It is therefore both overinclusive and underprotective.

Content-bound validation should compare dependencies, not exact current HEAD alone. The derivation commit may remain an ancestor while unrelated council or baseline documents land. At ARM, the validator should:

- Authenticate the final committed pack and freeze receipt.
- Parse the evidence source manifest.
- Compare every relevant current Git blob and executed-file digest with the recorded dependency manifest.
- Support a narrowly specified normalized binding for `plan_tree.json`, because the D-134 freeze-receipt slot necessarily changes after evidence authorship.
- Refuse any relevant dependency mismatch or semantic successor.
- Ignore elapsed time and reboot for content-bound receipts.

This also closes a weakness the 24-hour timeout only obscures: the current ARM replay authenticates source bytes but does not freshly compare every recorded primary/executed dependency with current reviewed bytes.

#### Required contract deltas

- **D-131 clause 4 — lifecycle and successor:** retain immutable successor reissue, but add that elapsed time or reboot alone is not a pack mutation and cannot require reissue. A successor is required only for a named content, registry, projection, evidence-policy or semantic change.
- **D-134 clause 1:** distinguish content-bound FREEZE evidence from temporal/state-bound ARM evidence.
- **D-134 clause 3:** extend the row registry from sole row authority to sole freshness-policy authority. Each row should name a governed policy ID.
- **D-134 clause 5:** introduce an exact-key `joulewise.arm_readiness_content_evidence_receipt.v1`. It omits `boot_session_id` and `valid_until_monotonic_ns`; it carries a freshness-policy ID, derivation commit, pre-freeze pack binding, and authenticated dependency-manifest binding.
- **D-134 clause 6:** “derive-never-enter” applies to freshness class, dependency inventory, observation time, boot ID and deadline.
- **D-134 clause 8:** retain same-boot, short-horizon, atomically consumable ARM capability semantics.
- **D-134 clauses 9–10:** add the content-validity, temporal-budget, reboot, successor-chain and crash-publication runbook/test obligations.
- **D-137:** clarify that boot identity is mandatory only for schemas carrying temporal validity. Content-bound receipts must carry neither boot identity nor a deadline. Existing v1 generic receipt bytes remain historical and are not reinterpreted.
- **D-078:** add `readiness_temporal_budget_insufficient`; ARM must refuse before writing an unusable receipt when the remaining temporal lifetime cannot cover the declared arm-to-consume budget.
- **D-117 attachment amendment:** the pinned registry digest also commits the freshness-policy table; frozen bytes still declare slots rather than future receipt hashes.

No D-120 change is needed: its single-authority limitation remains accurate.

### F2 — Should fix: successor lifecycle is still required

Choosing durable evidence does not eliminate successors. It eliminates routine, time-triggered successors.

The implementation should add one family-level reissue operation, not three loosely coordinated copy commands. `PACK_FAMILY` cross-authenticates ALPHA, BETA and GAMMA, so independent publication can expose a mixed-generation family.

Recommended shape:

- Add `generate_arm_readiness.py reissue-family`.
- Inputs are predecessor-family manifest and a new destination root; conclusions, hashes, receipt numbers and supersession bindings are derived.
- Require a clean exact reviewed checkout, three committed frozen predecessors, unused successor pack IDs, and unused custody roots.
- Stage all three successor packs together.
- Regenerate truthful freeze-aware status text, addressing M-2 forward-only.
- Reissue identity projections with predecessor bindings.
- Author content-bound evidence.
- Write successor freeze receipts whose numbers derive from the predecessor chain—e.g. predecessor `freeze-0001` produces successor `freeze-0002`, even though it lives under a new pack root.
- Bind predecessor pack ID/final digest, predecessor freeze receipt, predecessor identity receipt and predecessor evidence-set root.
- Publish through a family completion manifest/marker so partial multi-directory publication always refuses.
- Preserve predecessor directories byte-for-byte.

A freeze-receipt v2 is appropriate because the current `supersedes` object does not fully bind the old freeze, identity and evidence roots required by D-131.

The ordinary pre-arm lane then becomes:

1. Validate durable pack evidence and list any changed dependency.
2. Capture fresh T-0 inputs.
3. Refuse before ARM if the earliest temporal deadline cannot cover the arm-to-consume budget.
4. Create the ARM receipt.
5. Verify and atomically consume-to-launch.
6. If only live T-0 state failed or expired, use a new bracket session and T-0 custody namespace—not a new pack.

### F3 — Should fix: Phase-2 execution and rejected-option failures

#### Phase-2 re-freeze under this design

The existing v1 packs cannot be repaired in place. Their exact-key receipts really are expired under their issued schema, and D-131 forbids rewriting those bytes.

The one-time execution should be:

1. Cold-gate the R1 amendment before implementation.
2. Finish all Phase-1 pack-byte changes, including the T-0 producer and plan-path repair.
3. At the exact reviewed head, stage one ALPHA/BETA/GAMMA successor-family transaction.
4. Allocate three new pack IDs and custody roots; never alter the current `_v1` roots.
5. Produce content-bound receipts, successor identity projections and `freeze-0002` successor freeze receipts.
6. Verify every predecessor link, new final pack digest, cross-family identity and generator check.
7. Commit the whole family atomically from Git’s perspective; synchronize the canonical measurement checkout only through the governed reviewed-head procedure.
8. Run the repaired T-0 author→ARM→verify→consume rehearsal against the successor family.
9. Issue the successor operator packet only after that rehearsal passes.

This is the single Phase-2 re-freeze ordered by the council. Future window slips do not repeat it.

#### Baseline supersession

The old audit baseline remains immutable. Phase 3 creates a semantic successor manifest that binds:

- The predecessor baseline manifest and digest.
- The successor-family paths and final committed pack digests.
- `joulewise.committed_pack_tree_sha256.v1`.
- All freeze, identity, content-evidence and successor-chain binding paths.
- The council-required chain-template coverage note.
- The exact reviewed/effective head convention.

Because content validity is dependency-based, the later baseline-supersession commit does not invalidate the packs merely by advancing HEAD. Any relevant blob change still refuses. L1/L5/L7 and the adversarial universe re-enumeration then run over the superseding baseline.

#### Why B is rejected as the steady state

- It turns clock passage into false semantic change.
- Every window would mint new pack IDs, custody roots and baseline supersessions despite identical evidence.
- Each cycle moves the audit target and can force repeated focused re-audits before READY.
- “Less than 24 hours old” does not establish that power, clock, process or root state is still true at launch.
- It increases multi-pack chain, naming and operator-error surface precisely at the quiet-window boundary.

The successor tooling proposed by B is still necessary; its every-night schedule is not.

#### Why A as written is rejected

- Boot-binding immutable desk facts has no corresponding threat.
- A reboot would still force a successor even when every relevant byte is unchanged.
- Simply deleting the deadline without dependency replay would allow genuinely stale evidence to persist indefinitely.
- A global “durable” rule risks accidentally blessing live T-0 snapshots.

#### Rulings reserved to Ed or the magistrate

- Approve the three freshness semantics and the exact per-row mapping.
- Rule the short horizons, arm-to-consume safety margin, and which volatile predicates must be re-probed at consumption.
- Decide whether focused-test evidence binds a controlled execution-environment fingerprint or is treated solely as reviewed-byte proof. A time limit is not a substitute for that decision.
- Select successor pack IDs and approve cross-chain `freeze-000N` numbering.
- Approve freeze-receipt v2’s predecessor binding set and the family publication marker.
- Approve the irreversible one-time successor-family publication and exact Phase-3 baseline manifest identity.

## Residual risk

This was read-only design review; no suite or live ARM flow was run. The council traces were absent from detached HEAD but were inspected from immutable descendant commit `15d00d2`; the code inspected is the council-audited `8937dec` baseline. Current-main implementation should recheck all affected schemas and lifecycle paths before the cold gate.