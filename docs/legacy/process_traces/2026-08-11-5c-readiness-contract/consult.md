```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Adopt a two-stage, append-only readiness contract: a pack-pinned freeze receipt plus an external arm-time GO receipt that binds the final committed pack and all live evidence without modifying frozen bytes.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "2e5b1d9e5fefc6523ce52c00da1fa0311cd290a7",
    "head_end": "2e5b1d9e5fefc6523ce52c00da1fa0311cd290a7",
    "upstream_end": "0977cfb8bd636ebf2d5e8c8388f79c9512f4a6b3",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "id": "F1",
        "action": "start_now",
        "basis": "Adopt the split freeze-receipt and arm-receipt lifecycle; it removes the plan-record hash cycle."
      },
      {
        "id": "F2",
        "action": "start_now",
        "basis": "Adopt one machine-readable three-plan row registry; UNKNOWN remains human commentary and never enters a receipt."
      },
      {
        "id": "F3",
        "action": "start_now",
        "basis": "Adopt exact-key schemas, deterministic derivation, committed-pack authentication, governed namespaces, and closed refusals."
      },
      {
        "id": "F4",
        "action": "start_now",
        "basis": "Adopt non-authorizing dry-run receipts with no freeze-row bypasses and a closed synthetic-domain list."
      },
      {
        "id": "IMPLEMENT",
        "action": "wait_for",
        "basis": "This session is read-only; implementation requires a lead-issued nonempty WRITE_SCOPE."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --porcelain=v1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --quiet",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The requested D-131 precedent is absent from the inspected detached HEAD; its proposed body and implementation exist on impl/u11-idpin-projection.",
      "needs": "Land or rebase the D-131/U11 branch before the readiness implementation is merged."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Irreducibly manual observations such as independent clock correctness remain single-authority operator attestations; hash binding proves consistency, not independent truth.",
      "needs": "Preserve the D-120 assurance qualifier in every readiness and evidence receipt."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| F1 lifecycle/hash topology | start_now | D-131 landing before merge | Current §5C creates a plan↔record hash cycle and contradicts arm-time attachment semantics. |
| F2 row sets | start_now | Registry before any pack freeze | ALPHA mixes freeze facts with unknowable T-0 facts; BETA/GAMMA matrices do not exist. |
| F3 schema/evidence | start_now | U11 and final pack profiles | Hand-entered verdicts, open keys, or operator-provided hashes would violate derive-never-enter and D-120. |
| F4 dry-run | start_now | Final reviewed HEAD | Synthetic success can otherwise be mistaken for live ARM authority. |
| Doctrine amendments | wait_for | Implementation WRITE_SCOPE | §5C, ALPHA, D-117, operator packet, and the 40-hour plan currently encode the old model. |
| Tests | wait_for | Implementation | The gate must prove cycles, stale receipts, namespace anomalies, and replay fail closed. |

**F1 — lifecycle and hash topology**

Adopt two receipts, with one final operator-visible fence:

1. At pack freeze, generate `joulewise.arm_readiness_freeze_receipt.v1` under:

   `PACK_ROOT/arm_readiness.freeze.receipts/freeze-0001.json`

   plus its GNU-style `.sha256` sidecar. The receipt contains only freeze-evaluable rows and always has `arm_disposition: NOT_APPLICABLE`. It cannot license a night.

2. The final `plan_tree.json` pins that freeze receipt’s relative path and SHA-256 and declares, but does not populate, the arm-receipt slot:

   `arm_attachments.arm_readiness = {contract_id, required_before_arm, row_registry, freeze_receipt, arm_receipt_namespace, pack_digest_algorithm}`.

   There is no final arm path or digest in frozen bytes.

3. After writing the freeze receipt, final plan tree, sidecars, U11 freeze receipt, and every other pack file, compute the arm-time pack digest from the committed pack. No pack file stores this digest.

4. At T-0, generate `joulewise.arm_readiness_receipt.v1` under:

   `CUSTODY_ROOT/PACK_ID/arm_readiness.receipts/arm-0001.json`

   plus its sidecar. It binds the completed pack digest, committed Git state, freeze receipt, final-head rehearsal, all live evidence, and the complete row set. It is external to the pack, so generating it cannot change frozen bytes.

5. Only an unsuperseded `receipt_kind: arm`, `status: PASS`, `arm_disposition: GO` receipt may satisfy §5C’s machine gate. It remains necessary but not sufficient: the lead verification and Ed’s physical foreground launch remain non-delegable.

The pack digest algorithm is `joulewise.committed_pack_tree_sha256.v1`:

```text
SHA256(
  b"joulewise.committed_pack_tree_sha256.v1\n" +
  concat_for_each_committed_file_sorted_by_raw_utf8_relative_path(
    path_utf8 + NUL +
    git_mode_ascii + NUL +
    byte_length_ascii + NUL +
    lowercase_sha256_of_file_bytes + LF
  )
)
```

It includes every committed file below `PACK_ROOT`, including `plan_tree.json`, its sidecar, U11 receipts, freeze/readiness evidence, and their sidecars. Only Git blob modes `100644` and `100755` are admitted. Symlinks, submodules, non-UTF-8 paths, untracked pack entries, missing disk entries, or disk/Git byte differences refuse. The external arm namespace is necessarily excluded because it is outside `PACK_ROOT`.

This explicitly breaks the cycle:

```text
freeze receipt ──SHA-pinned by──> final plan tree
final plan tree + all pack bytes ──hashed by──> arm receipt
arm receipt ──never referenced by──> frozen pack
```

Re-arming is append-only and semantic:

- Every new arm evaluation writes the next `arm-<4+ digits>.json`; no overwrite or deletion.
- A successor binds the prior receipt ID, path, digest, pack ID, and pack digest.
- Namespace scanning must refuse any malformed, unpaired, duplicate, or nonconforming entry rather than silently skip it.
- A stale receipt refuses if a valid semantic successor exists.
- A used bracket session, attempt ID, or launch capability is never reused.
- A changed pack, row registry, acceptance, freeze evidence, or identity projection requires a new pack ID and pack/custody root. A purely live pre-launch refusal may reuse unchanged pack bytes only through a new session and a superseding external arm receipt, if the frozen attempt policy permits it.

**F2 — row authority and row sets**

Create one normative registry:

`configs/arm_readiness/d117_row_registry_v1.json`

Its exact top-level keys are:

```text
schema_version, registry_id, plan_profiles, rows
```

Each profile has exactly:

```text
profile_id, window_kind, required_row_ids
```

Each row definition has exactly:

```text
row_id, evaluation_phase, applicability_rule,
predicate_id, required_evidence_kinds
```

Closed vocabularies:

- `window_kind`: `ALPHA | BETA | GAMMA`
- `evaluation_phase`: `FREEZE_AND_ARM | ARM_ONLY`
- `applicability_rule`: `ALWAYS | CLOCK_HELPER_ONLY | SUCCESSOR_ACCEPTANCE_ONLY`
- serialized applicability: `REQUIRED | NOT_APPLICABLE`
- row verdict: `PASS | REFUSE | NOT_APPLICABLE`
- receipt status: `PASS | REFUSE`
- arm disposition: `GO | NO_GO | NOT_APPLICABLE`

`UNKNOWN`, `PENDING`, and prose such as “GO conditionally” are forbidden in machine receipts. Missing live evidence becomes `REFUSE`, not UNKNOWN.

The freeze receipt contains all `FREEZE_AND_ARM` rows. The final arm receipt contains every profile row, re-evaluates the freeze rows from committed bytes, and evaluates every `ARM_ONLY` row from live receipts.

The normative registry replaces Markdown as row-set authority. ALPHA/BETA/GAMMA Markdown pages become generated or checked human views with stable row IDs. BETA and GAMMA pages must exist before their respective freeze, but their absence cannot alter the registry.

The complete v1 row set is:

| row_id | phase/applicability | exact source and derivation predicate |
|---|---|---|
| `desk.recovery_ledger_path` | F+A / always | Final-head verification receipt; PASS iff the recovery/ledger focused suite passed at the bound HEAD. |
| `desk.arming_procedure` | F+A / always | Committed hashes of runbook §§5, 5A, 5B, 5C, 6, 10 and the frozen launch recipe; all equal their pack doctrine pins. |
| `desk.mint_trust` | F+A / always | D-120 profile test receipt at the same HEAD and pack digest is PASS. |
| `desk.acceptance_owner` | F+A / always | Writer test proves the authenticated active acceptance artifact is the domain owner; copied scalar or unknown key refuses. |
| `desk.multicell_mint` | F+A / always | Pack pinsets and mint schemas byte-match committed sources and their focused integration receipt passes. |
| `desk.estimator_identity` | F+A / always | Estimator ID is derived from the frozen plan and admitted mint registry; no CLI value is accepted. |
| `desk.identity_pin_projection` | F+A / always | U11 freeze receipt is PASS at freeze; final arm also requires U11 arm re-verification PASS. All five D-131 reasons propagate. |
| `desk.receipt_oracle` | F+A / always | Re-derive from the committed ledger implementation and require exact equality with the pack oracle. |
| `desk.three_window_regression` | F+A / always | ALPHA/BETA/GAMMA live-ledger regression receipt is PASS at the same HEAD. |
| `desk.acceptance_successor` | F+A / successor only | N/A only for the issued D-079 artifact; otherwise the authenticated successor receipt must be PASS and selected before member one. |
| `desk.reason_code_plumbing` | F+A / always | Registry coverage test and rehearsal receipt prove every produced refusal has a closed code. |
| `desk.current_pack` | F+A / always | Pack generator `--check`, manifest/plan validators, extraction specification, attempt policy, and committed pack digest all pass. |
| `desk.pack_family` | F+A / always | All three pack receipts bind the same reviewed HEAD and mutually consistent floor/transport identities. |
| `desk.under_lease_rehearsal` | arm / always | Lead-owned dry-run receipt binds this exact HEAD/pack and contains the required reserve/writer events for both slots. |
| `desk.reviewed_checkout` | arm / always | Derived Git proof has `HEAD == main == origin/main`, exact tree equality, and empty status including untracked files. |
| `desk.terminal_review` | arm / always | Lead terminal-review evidence receipt binds the same HEAD tree and pack digest; later changes invalidate it. |
| `privilege.fresh_authorization` | arm / helper only | Installation receipt records the reviewed `sudo -k`/fresh-authorization sequence. |
| `privilege.installed_bytes` | arm / helper only | Installed file digests equal the pack-staged reviewed digests. |
| `privilege.isolated_interpreter` | arm / helper only | Installation probe proves the frozen isolated-interpreter contract. |
| `privilege.activation_fence` | arm / helper only | Receipt proves inactive installed state preceded the separate Ed-visible activation. |
| `clock.correct_and_prior_state` | arm / always | Exact-key operator/probe receipt contains the independent-clock attestation and captured prior `systemsetup` state. |
| `clock.network_time_off` | arm / always | Fresh system probe records network time off; no hand-entered row status. |
| `clock.restore_recipe` | F+A / always | Frozen close-out recipe hashes match the pack and order restore after verdict and both backups. |
| `t0.no_stray_keepawake` | arm / always | Fresh process-census receipt shows no stray keep-awake/agent/browser/monitor process. |
| `t0.power_path` | arm / always | Power receipt matches the frozen supply, negotiation, AC state, and policy. |
| `t0.background_quiet` | arm / always | Fresh maintenance census/closed operator observation receipt passes. |
| `t0.display_thermal_idle` | arm / always | `quiet_mac_prep` and completed `prewindow_check --wait` receipts prove display, screensaver, thermal, and idle predicates. |
| `t0.passwordless_powermetrics` | arm / always | Exact reviewed `sudo -n /usr/bin/powermetrics …` probe receipt exits 0. |
| `t0.offline_inputs` | arm / always | File inventory and U11 live derivation match the frozen model/tokenizer/config/runtime set; no network fetch occurred. |
| `t0.storage_backup_capacity` | arm / always | Backup preflight receipt proves both frozen destinations exist, are distinct, writable, and have required capacity. |
| `t0.fresh_roots_waivers` | arm / always | Roots derive from frozen leaves plus arm context, are absolute/distinct/empty, and the referenced waiver bytes decode exactly to `[]`. |
| `t0.campaign_lock_absent` | arm / always | Fresh root receipt proves no live or stale lock; unreadable locks refuse. |
| `t0.machine_readiness` | arm / always | Frozen `prewindow_check --wait` command receipt is `READY`, current, and bound to the same plan/roots. |
| `t0.ledger_reservation` | arm / always | Live diagnostic and real `--execute` reservation receipt bind the pack plan SHA and contain `calibration_pre_reserve_authorized` plus `status: reserved`. |
| `t0.single_launch_capability` | arm / always | Session/attempt IDs are unused, the exact launch command is frozen, and an atomic single-use capability is available. |

The final row is deliberately not “single foreground launch”: a pre-launch record cannot truthfully claim the launch already happened. The launcher must atomically consume the capability, write a no-clobber consumption receipt, recheck volatile predicates, and then execute once. Replay refuses.

**F3 — closed receipt schemas**

All JSON parsers reject duplicate keys, unknown keys, missing keys, NaN/infinity, invalid UTF-8, and non-lowercase digests. Generated bytes use sorted keys, two-space indentation, UTF-8, and one terminal LF. Receipts contain no self-hash; sidecars authenticate exact bytes.

Freeze receipt exact keys:

```text
schema_version, receipt_kind, receipt_id, status, arm_disposition,
issued_at_utc, pack_identity, row_registry, evidence, rows,
refusals, supersedes, assurance
```

Arm receipt exact keys:

```text
schema_version, receipt_kind, receipt_id, mode, status, arm_disposition,
issued_at_utc, valid_until_monotonic_ns, pack, reviewed_main,
arm_context, freeze_receipt, row_registry, evidence, rows,
refusals, supersedes, assurance
```

Dry-run receipt exact keys:

```text
schema_version, receipt_kind, receipt_id, mode, status, arm_disposition,
issued_at_utc, pack, synthetic_context, evidence, checks,
omitted_live_domains, refusals, assurance
```

Nested exact keys:

```text
pack_identity:
  pack_id, plan_id, window_id, pack_root, plan_path, plan_sha256

pack:
  pack_id, plan_id, window_id, pack_root,
  pack_digest_algorithm, pack_sha256,
  plan_tree_path, plan_tree_sha256,
  plan_tree_sidecar_path, plan_tree_sidecar_sha256

reviewed_main:
  head_commit, head_tree_oid, local_main_commit,
  origin_main_commit, clean, exact_match

arm_context:
  bracket_session_id, pre_attempt_id, post_attempt_id, clock_route,
  claim_runs_root, bound_runs_root, custody_root, quarantine_root,
  claim_backup_destination, bound_backup_destination, waiver_path

row_registry:
  registry_id, path, sha256, plan_profile

freeze_receipt:
  receipt_id, path, sha256

evidence item:
  evidence_id, receipt_kind, namespace, path,
  sha256, schema_version, status

row:
  row_id, evaluation_phase, applicability,
  verdict, predicate_id, evidence_ids

refusal:
  type, code, row_id, evidence_id

supersedes:
  receipt_id, receipt_path, receipt_sha256,
  pack_id, pack_sha256

assurance:
  model, independent_attestation

synthetic_context:
  rehearsal_id, root, ledger_path, backend

dry-run check:
  check_id, status, command_sha256,
  stdout_sha256, stderr_sha256, exit_code
```

`namespace` is only `PACK` or `WINDOW_CUSTODY`; its path is namespace-relative and may not escape. `assurance` is always:

```json
{
  "model": "single_authority_hash_bound_replay.v1",
  "independent_attestation": false
}
```

A generic domain evidence receipt may use exact keys:

```text
schema_version, evidence_id, kind, status, issued_at_utc,
valid_until_monotonic_ns, pack_sha256, head_commit,
facts, checks, reason_codes, assurance
```

Each fact has exactly:

```text
fact_id, value_type, value, source_kind, source_path, source_sha256
```

`source_kind` is `PROBE | PACK | GIT | OPERATOR_ATTESTATION`. Row verdicts are always derived from registered fact/check IDs. Operators may attest an irreducibly manual observation, but may never enter a row verdict, applicability, digest, identity pin, or PASS status.

Waiver evidence refers to the actual attempt-local `waivers.json`; it passes only if strict JSON parsing produces an empty array. Backup evidence in an arm record is preflight capacity/writability evidence. Successful postcollection backup receipts remain §11/§12 close-out evidence and cannot be fabricated or predeclared at arm.

**F4 — dry-run semantics and CLI**

CLI shape:

```text
python3 scripts/generate_arm_readiness.py freeze \
  --pack-root PACK_ROOT

python3 scripts/generate_arm_readiness.py dry-run \
  --pack-root PACK_ROOT \
  --window-custody-root CUSTODY_ROOT \
  --rehearsal-id REHEARSAL_ID \
  --synthetic-root SYNTHETIC_ROOT

python3 scripts/generate_arm_readiness.py arm \
  --pack-root PACK_ROOT \
  --arm-context ARM_CONTEXT_JSON \
  --window-custody-root CUSTODY_ROOT

python3 scripts/generate_arm_readiness.py verify \
  --pack-root PACK_ROOT \
  --arm-receipt ARM_RECEIPT
```

`freeze` is the only mode allowed to update the pack and plan-tree freeze-receipt reference. `dry-run`, `arm`, and `verify` are pack-read-only. Governed output paths are derived; there is no `--output`.

The CLI must reject options that supply row states, applicability, hashes, identity pins, evidence paths, or reason codes. `--arm-context` supplies only the exact-key attachment object; the generator derives all verdicts and digests.

Dry-run:

- Executes the real validator, real reservation CLI with `--execute`, and real writer entry points through both reserved calibration slots under the actual lease implementation.
- Has only `status: PASS | REFUSE`, `mode: dry_run`, and `arm_disposition: NOT_APPLICABLE`.
- May bypass no `FREEZE_AND_ARM` refusal.
- May synthetically substitute only these closed ARM-only domains: `LIVE_PRIVILEGE`, `LIVE_CLOCK`, `LIVE_MACHINE`, `LIVE_POWER`, `PRODUCTION_ROOTS`, `PRODUCTION_BACKUPS`, `PRODUCTION_LEDGER`, and `LAUNCH_CONSUMPTION`.
- Must enumerate every substitution in `omitted_live_domains`.
- Must bind the exact final reviewed HEAD and pack digest used at arm. Any subsequent byte or HEAD change makes it stale.
- May be hash-pinned by the arm receipt as rehearsal evidence, but its bytes may never occupy the plan’s arm-receipt slot, carry `GO`, or be accepted by the launcher.

**Closed readiness refusal vocabulary**

The readiness layer owns only these codes; upstream receipts retain their own closed detail codes.

- `STRUCTURE`: `readiness_schema_invalid`, `readiness_receipt_kind_invalid`, `readiness_unknown_key`, `readiness_row_registry_mismatch`, `readiness_row_set_incomplete`, `readiness_row_applicability_invalid`, `readiness_evidence_reference_invalid`, `readiness_usage_invalid`.
- `CUSTODY`: `readiness_pack_unreadable`, `readiness_pack_namespace_anomalous`, `readiness_pack_digest_mismatch`, `readiness_pack_not_committed`, `readiness_freeze_receipt_unreadable`, `readiness_freeze_receipt_mismatch`, `readiness_evidence_unreadable`, `readiness_evidence_digest_mismatch`, `readiness_receipt_namespace_anomalous`.
- `GIT`: `readiness_git_tree_dirty`, `readiness_reviewed_main_mismatch`, `readiness_terminal_review_missing`.
- `LIFECYCLE`: `readiness_receipt_superseded`, `readiness_record_expired`, `readiness_record_consumed`, `readiness_output_collision`, `readiness_lock_unavailable`, `readiness_dry_run_missing`, `readiness_dry_run_refused`, `readiness_dry_run_stale`, `readiness_dry_run_used_as_arm_record`.
- `POLICY`: `readiness_dependency_refused`, `readiness_waiver_source_invalid`, `readiness_waiver_set_nonempty`, `readiness_root_binding_invalid`, `readiness_root_not_fresh`, `readiness_backup_preflight_refused`, `readiness_machine_preflight_refused`, `readiness_clock_preflight_refused`, `readiness_ledger_preflight_refused`, `readiness_launch_capability_unavailable`.
- `IDENTITY`, imported exactly from D-131: `readiness_identity_artifact_unreadable`, `readiness_identity_environment_dirty`, `readiness_identity_projection_mint_divergence`, `readiness_identity_pinset_frozen_mismatch`, `readiness_identity_receipt_namespace_anomalous`.
- `ENVIRONMENT`: `readiness_io_error`, `readiness_internal_error`.

Every code only refuses. No reason spelling licenses ARM.

**Required doctrine amendments**

- `docs/phase_2/window_runbook.md`
  - §4: add the registry pin, freeze receipt, final pack digest definition, evidence namespaces, and dry-run rule.
  - §5A: require exact clock/operator receipts; correct the matrix wording that currently implies a separate hand-counted settle.
  - §5C entry gate: replace “arm record created and SHA-pinned at freeze” with the two-stage lifecycle and deterministic external arm namespace.
  - §5C lead verification: require the dry-run receipt at the same HEAD/pack rather than defer its evidence solely to §12.
  - §5C step 2: generate the final arm receipt only after machine readiness and live ledger reservation pass.
  - §5C step 3: require atomic consumption of the exact unsuperseded GO receipt.
  - §10 “Slot quarantine and supersession”: add readiness/session semantic supersession and no-reuse rules.
  - §12: record freeze, dry-run, arm, consumption, root, waiver, backup-preflight, and postcollection backup receipt digests separately.
- `docs/phase_2/alpha_arm_readiness.md`
  - Replace the introductory “generated at pack freeze and pinned by plan” statement.
  - Add the stable row IDs above.
  - Declare the JSON registry authoritative and the page a checked human view.
  - Split freeze-evaluable and arm-only gates.
  - Replace “Frozen readiness validator and record” with `desk.under_lease_rehearsal`.
  - Correct the clock-settle wording.
  - Replace “Single foreground launch” with `t0.single_launch_capability`.
  - Add the omitted `t0.ledger_reservation` row.
- Create `docs/phase_2/beta_arm_readiness.md` and `docs/phase_2/gamma_arm_readiness.md` as checked views before their freezes.
- `docs/decision_log.md`
  - Append the next available decision entry titled “Per-plan arm-readiness contract — adopt as proposed.”
  - Add a D-117 amendment clarifying that the frozen plan declares attachment slots without hashing future arm bytes.
  - Add the readiness refusal registry amendment.
  - Do not rewrite D-120; cite and compose with it.
- `docs/strategy/2026-08-07-three-night-operator-packet.md`
  - Correct the hard-gate and per-night ARM sequence to freeze receipt → reviewed-head dry run → T-0 arm receipt → atomic consumption.
- `docs/strategy/2026-08-08-40h-plan.md`
  - Phase B B2: distinguish U11 freeze projection from arm re-verification.
  - Phase B B5: require the non-authorizing dry-run receipt at the final reviewed HEAD.
- `docs/process/state_kernel.json`
  - Update the readiness fence wording; regenerate `RUN_STATE.md` and `TASK_QUEUE.md`.
- Preserve `docs/process_traces/2026-08-07-d117-plan-freeze/**` and the external T4 custody record as historical evidence; supersede by decision, never edit them in place.

**Test obligations**

- Exact-key, duplicate-key, UTF-8, number, digest, and canonical-byte tests for every schema.
- Deterministic double-generation and sidecar tests.
- Pack-digest mutation tests for bytes, path, mode, missing/extra file, untracked file, symlink, and namespace anomaly.
- Proof that adding the external arm receipt never changes pack bytes or digest.
- Registry completeness/uniqueness tests for all 35 rows and all three profiles; Markdown row-ID parity checks.
- Applicability mutation tests proving only the two registered conditional rules may produce `NOT_APPLICABLE`.
- Derive-never-enter API/CLI signature tests; unknown override options must refuse.
- Freeze receipts can never yield GO; missing ARM-only evidence must refuse.
- Dry-run receipts can never occupy the arm slot or be consumed by the launcher.
- Same-HEAD/pack binding tests for dry run, terminal review, evidence receipts, and final arm receipt.
- U11 integration tests propagating all five D-131 refusals.
- Empty-waiver, reused-root, root collision, stale/live campaign lock, and backup-destination tests.
- Governed-namespace tests including five-digit receipt numbers, malformed names, orphan sidecars, duplicates, and semantic successors.
- Atomic launch-capability race tests: exactly one consumer succeeds; replay and stale predecessors refuse.
- Complete real-CLI under-lease rehearsal test requiring pre-reserve plus both phase-correct writer events.
- ALPHA/BETA/GAMMA integration tests, including GAMMA’s four ordered U11 units.
- Focused readiness tests followed by `python3 -m unittest discover -s tests`.

## Critical path

The only cross-row dependency chain is:

```text
D-131/U11 landing
→ normative row registry and doctrine amendment
→ three pack profiles generated
→ freeze receipts inserted and final pack bytes committed
→ exact reviewed-main/terminal-review proof
→ same-head under-lease dry-run receipt
→ Ed’s §5A and T-0 domain receipts
→ live ledger reservation
→ final external arm GO receipt
→ atomic single-use launch consumption
```

BETA/GAMMA human views may be prepared in parallel, but their row IDs must come from the registry. No quiet-machine activity starts until the final arm receipt exists and the launcher can consume it.

1. **Adopt as proposed:** split readiness into a pack-pinned, non-authorizing freeze receipt and an external, pack-binding arm receipt.
2. **Adopt as proposed:** declare the future arm-receipt schema and governed namespace in frozen bytes, but never its future path/SHA value.
3. **Adopt as proposed:** make `d117_row_registry_v1.json` the sole row authority for ALPHA, BETA, and GAMMA; Markdown matrices are checked views.
4. **Adopt as proposed:** prohibit UNKNOWN in receipts; missing live evidence is REFUSE, while NOT_APPLICABLE is allowed only by registered predicates.
5. **Adopt as proposed:** use exact-key, no-self-hash receipts, committed-pack verification, semantic supersession, and D-120’s single-authority assurance qualifier.
6. **Adopt as proposed:** derive every row verdict, applicability, digest, identity pin, and evidence binding; operators may supply paths and irreducible attestations, never conclusions.
7. **Adopt as proposed:** treat dry-run PASS only as same-head rehearsal evidence; it bypasses no freeze refusal and can never be an arm record.
8. **Adopt as proposed:** add the live ledger-reservation row and replace the impossible pre-launch “single foreground launch” row with an atomically consumable single-launch capability.
9. **Adopt as proposed:** amend the enumerated live doctrine and append the decision/refusal entries while preserving historical process traces.
10. **Adopt as proposed:** require the full mutation, lifecycle, namespace, replay, U11-integration, three-profile, focused, and canonical-suite test obligations before any D-117 arm.