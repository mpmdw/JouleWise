```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Use one shared issuance-policy guard at command dispatch and independently callable issuing APIs; neither hashing helpers nor writer leases are a sufficient universal boundary.",
  "workspace": {
    "base_requested": "20cd559f",
    "base_mode": "exact",
    "head_start": "20cd559ff55ad02e060e77628b494f386eea9fc9",
    "head_end": "20cd559ff55ad02e060e77628b494f386eea9fc9",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 3, "nit": 0},
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "joulewise/calibration_ledger.py",
        "line": 5431,
        "title": "Issuance refusal is not an entry-point invariant",
        "evidence": "Eight reservation, claim, recovery, abort, and pin-advancement APIs lack a direct override guard. The fiducial lifecycle and rederivation gaps in the supplied delta report remain visible in source.",
        "recommendation": "Make refusal an explicit command-entry and public issuing-function precondition using one shared helper."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "path": "scripts/validate_powermetrics_fiducial.py",
        "line": 441,
        "title": "Import-time authentication precedes a proposed main-entry guard",
        "evidence": "The module initializes PREFLIGHT_SYSTEMATIC_SCREEN_S by authenticating acceptance evidence and checking protocol and estimator hashes before main runs.",
        "recommendation": "Defer this initialization behind issuing dispatch; preserve an explicit lazy read-only derivation for consumers."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "path": "joulewise/calibration_ledger.py",
        "line": 4684,
        "title": "Existing predicate does not mean non-empty environment value",
        "evidence": "any(value.split(os.pathsep)) accepts ':' and '::' on this platform although both environment values are non-empty.",
        "recommendation": "Under the requested rule, test os.environ.get('JOULEWISE_BACKUP_ROOTS', '') != ''; do not parse or normalize roots in the issuing guard."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD; git diff --exit-code",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)", "20cd559ff55ad02e060e77628b494f386eea9fc9"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "20cd559ff55ad02e060e77628b494f386eea9fc9"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This was a static, read-only consult. All scripts/*.py and joulewise/**/*.py were AST-parsed, relevant implementations and callers inspected, and the supplied delta report read. No runtime regression, canonical suite, live capture, or iCloud probe was executed.",
      "needs": "Lead must execute the proposed temporary-filesystem regression matrix and final verification after implementation."
    }
  ]
}
```

## Findings

### F1 — Make issuance refusal an entry contract

**There is no single existing function through which every issuer passes.** The structural solution is **one policy implementation, invoked once at each issuing command boundary, plus the same precondition on independently callable issuing APIs**.

Expose `refuse_if_custody_override_active()` from `joulewise/calibration_ledger.py`, replacing the private helper at line 4681. It should perform only an environment-string check and raise `CalibrationLedgerError("custody_locator_override_mint_forbidden")`.

For a script with only issuing operations, call it at the beginning of `main`, inside the refusal handler. Argument parsing may precede it if parsing performs no filesystem work. For mixed scripts, parse the command and invoke it at **one dispatch location**, conditional on the issuing operation, before loading inputs or invoking handlers.

Do not put the policy in:

- `probe_custody`, authentication sessions, candidate loading, or validators: these must support relocation.
- `CalibrationWriterLease.acquire:3067`: `writer_lease_is_live:3358` uses it for status/readiness, called at lines 4880 and 4968.
- `_locked_append:4025` alone: callers can already have read, hashed, acquired leases, or written state.
- A module-wide import guard: importing replay helpers must remain possible.

All line numbers below refer to the inspected HEAD and identify function definitions unless stated otherwise.

### Entry-point table: calibration issuance and recovery

| Process/function entry | Modes and effects | Guard placement |
|---|---|---|
| `scripts/validate_powermetrics_fiducial.py:1523 main` | Ordinary capture, bracket pre/post capture, `--rederive-from`; reservations and evidence emission | One unconditional issuing guard before crash-authorization configuration, protocol checks, launch authentication, or capture setup. Address F2 as well. |
| Same file, `:1099 rederive_artifact` | Reads and hashes primary custody bytes; creates instrument evidence | First operation after docstring, before constructing/reading input paths. |
| Same file, `:1258 _CaptureLedgerLifecycle.__init__`, `:1303 begin` | Creates capture lifecycle state; acquires lease, repairs ledger, reserves/claims | Guard constructor before state initialization; guard `begin` before slot validation or stage callbacks. `begin` remains necessary if environment changes after construction. |
| Same file, `:1406 abandon`, `:1438 finalize` | Closes ordinary/bracket attempts; hashes evidence and appends receipts | Same API-entry precondition. Preserve lease release on every refusal; never allow a new guard to bypass existing cleanup. |
| `scripts/reserve_calibration_window_bracket.py:95 main` | Validates prospective reservation; `--execute` reserves bracket | One conditional guard immediately after parsing for `--execute`, before crash authorization, JSON reads, plan hashing, or lease acquisition. Validation-only mode may retain override. |
| `scripts/calibration_ledger_bootstrap.py:384 main` | Generates custody manifest/import plan; prepares/emits issued acceptance; bootstraps ledger | One unconditional guard before disposition-table read. Even non-execute modes construct issuance material with locators. |
| `scripts/calibration_ledger_backfill.py:120 main` | Discovers candidates, hashes custody, emits candidate set | One unconditional guard before discovery; current refusal through `artifact_hashes` is too late and does not cover an empty candidate census. |
| Same file, `:90 build_candidate_set` | Independently callable candidate-generation API | First operation, before walking roots. |
| `scripts/recover_calibration_ledger.py:224 main` | Mixed read/write command dispatcher | One conditional guard immediately inside `try`, before dispatch, for `repair`, `abandon-tail`, `resume-finalize`, `abort-session`, and head advancement. Guard head advancement even without `--execute`: its API acquires a lease. |

Recovery commands that remain available with the override: `explain`, `inspect`, `audit`, `audit-observations`, `session-status`, `session-refusal`, `validate-slot`, `terminal-pin`, and `readiness`.

### Independently callable ledger entry points

Each row needs the shared precondition as its first operational statement. Existing guarded APIs retain it.

| `joulewise/calibration_ledger.py` entry | Why the API itself needs the precondition |
|---|---|
| `:273 artifact_hashes` | Issuance hash vector; already guarded. |
| `:2537 generate_historical_custody_manifest` | Discovers/hashes locator-bearing issuance inputs; already guarded. |
| `:2595 prepare_historical_import` | Constructs import receipts and plan; already guarded. |
| `:3439 bootstrap_historical_import` | Reauthenticates and publishes genesis payload; already guarded. |
| `:3911 repair_calibration_ledger` | Can create directories and append recovery/control receipts. |
| `:3956 abandon_calibration_ledger_tail` | Issues abandonment/control evidence. |
| `:4194 append_bracket_session_receipt` | Issues bracket reservation capability. |
| `:4286 claim_bracket_session_slot` | Issues slot claim. |
| `:4385 finalize_bracket_session_slot` | Issues terminal slot receipt; already guarded. |
| `:4499 abort_bracket_session` | Issues session-abort receipt. |
| `:5108 advance_calibration_head_pin` | Acquires lease, authenticates custody, optionally publishes head pin. |
| `:5202 resume_finalize_bracket_session` | Acquires lease, repairs, hashes, claims/finalizes; already guarded. |
| `:5362 abort_calibration_session` | Acquires lease and repairs before aborting. |
| `:5431 append_pending_receipt` | Issues ordinary pending reservation. |
| `:5535 finalize_attempt_receipt` | Issues terminal ordinary receipt; already guarded. |

The shared mutation primitive `_locked_append:4025` can additionally assert the policy **before its `mkdir`**. That is defence in depth, not a replacement for these entry preconditions.

### Broader custody-bound issuance census

A repository-wide interpretation of “every issuing entry point” extends beyond calibration-ledger writers. These producer boundaries should follow the same rule; their reusable verification/reconstruction helpers should not acquire blanket guards.

| Script entry | Issuing operations and callable boundaries | Placement |
|---|---|---|
| `scripts/build_bracket_binding.py:416 main` | Publishes authenticated bracket binding | Before `_custody_root` or input authentication. Keep `joulewise/calibration_bracketing.py:865 build_calibration_bracket_binding` available for reconstruction: `whole_window.py:599` calls it while evaluating evidence. |
| `scripts/mint_floor_artifact.py:2144 main` | Floor issuance | Before input loading. Also guard `:2010 mint_floor_artifact`, `:1500 mint_authenticated_artifact`, and `:1981 write_outputs_exclusive` for direct callers. |
| `scripts/mint_floor_artifact_generalized.py:4260 main` | Single/multicell floor issuance, including replay sidecar accompanying mint | Before pinset/input reads. Also guard `:1750 mint_floor_artifact`, `:3983 mint_multi_cell_floor_artifact`, `:1684 mint_authenticated_artifact`, and `:3344 mint_multi_cell_authenticated_artifact`. Keep `:1720 validate_floor_artifact` available. |
| `scripts/finalize_analysis_manifest.py:42 main` | Publishes finalized analysis manifest | Before dispatch; also `joulewise/analysis_manifest_v3.py:4045 finalize_prospective_analysis_manifest_v3`, before authentication. |
| `scripts/run_campaign.py:8941 main` | Campaign capture, provenance repair, supersession, drift-bound mint, whole-window verdict publication | One conditional dispatch guard for these producing operations; preserve prompt-hash checking. Direct entries: `:8019 run_campaign`, `:7190 run_axi_spec_campaign`, `:3547 run_repair_campaign_provenance`, `:5971 run_record_supersession`, `:6126 run_derive_neg8_drift_bound`, `:6160 run_whole_window_verdict`, `:1947 run_authenticated_campaign_child`. Guard before locks/logs/child execution. |
| `scripts/launch_window.py:294 main` | Consumes launch capability and records lifecycle evidence | Before dispatch; also `:239 launch`, `:270 lifecycle`, `joulewise/arm_readiness.py:9573 _consume_launch_capability`, `:9925 record_launch_lifecycle_event`. |
| `scripts/run_night.py:1467 main` | Runs/rehearses persisted night lifecycle; dead-man recovery | Before plan loading or result/refusal-file creation; also `:1074 run_night`, `:1343 dead_man`. Rehearsal uses a writing driver and is not a read-only validator. |
| `scripts/author_arm_readiness_evidence.py:39 main` | Authors generic readiness evidence | Before dispatch; also `joulewise/arm_readiness_evidence.py:3303 author_arm_readiness_evidence`. |
| `scripts/author_arm_evidence_t0.py:30 main` | Authors T-0 receipts | Before dispatch; also `joulewise/arm_readiness_evidence_t0.py:2245 author_arm_readiness_evidence_t0`. |
| `scripts/capture_t0_step.py:859 main` | Captures a T-0 evidence step | Before dispatch; also `:827 capture_step`, before dependency dispatch. |
| `scripts/generate_arm_readiness.py:119 main` | Freeze/arm receipt generation; also verification/rehearsal modes | One conditional guard for `freeze`/`arm`, before `_pack_snapshot` or input reads. Also `joulewise/arm_readiness.py:7419 generate_freeze_receipt`, `:8219 generate_arm_receipt`. Preserve `verify`; treat synthetic `dry-run` as replay rather than live authorization. |
| `scripts/build_family_marker.py:37 main` | Publishes family marker | Before dispatch; also `joulewise/arm_readiness.py:11351 build_family_publication_marker`. |
| `scripts/record_window_duration_margins.py:25 main` | Appends authenticated duration-margin receipt | Before dispatch; also `joulewise/window_duration_margins.py:1223 record_window_duration_margins`. Preserve the separate derivation/verification functions. |
| `scripts/issue_g2a_prefill_prompt_pin.py:519 main` | Issues selected prompt pin | Before input loading; also `:413 issue_pin`. |
| `scripts/generate_g2a_probe_inputs.py:1318 main` | `bind-window` produces ledger/acceptance-bound window inputs | One conditional guard for `bind-window`; also `:846 bind_window`. Preserve `check_inputs:1146` and unbound probe generation. |

There is also a non-`scripts/*.py` capture entrance: `joulewise/cli.py:2365 main`. Apply the same dispatch distinction to run/experiment commands, with library preconditions on `joulewise/controller.py:238 run_benchmark` and `:2794 run_experiment`. Otherwise a guarded campaign parent would not cover direct CLI/library capture.

This broader table identifies policy coverage, **not reproduced false-locator defects in every listed producer**.

### Read/replay classification

Keep the override in `probe_custody:4727`, `load_calibration_ledger_snapshot:1966`, custody verification, `load_calibration_candidate:1081`, bracket evaluation, floor binding/validation, and paper replay.

The following searched paths produce reports, reconstructions, preparations, or copied fixture material rather than issuing new calibration observations or authorizing capture:

- `reissue_calibration_acceptance.py:577 main` produces an explicitly marked candidate; its `derive_candidate_artifact:249` and `write_candidate_artifact:306` do not promote it to issued evidence.
- `extract_detection_floors.py:48 main`, `summarize_g2a_prefill_probe.py:558 main`, compatibility/reconciliation receipt scripts, paper diagnostic scripts, and verification scripts are replay/report consumers.
- `build_v4_histsem_pinset.py:325 main`, `refresh_receipt_histsem_pinset.py:654 main`, and estate/source-pin tools operate on versioned source/history coordinates.
- Fixture packaging/hydration and prospective campaign generators are not live custody issuance.

**Writing a replay report does not itself make a validator a minting entry point.** Conversely, `rederive_artifact` explicitly emits new instrument evidence and therefore is issuing despite its name.

`joulewise/receipt_oracle.py:66 derive_bracket_session_receipt_oracle` is a special case: it replays production receipt writers inside a temporary tree and writes an initial head pin before calling them. Preserve its replay affordance by running the synthetic writer replay in an isolated subprocess with the override removed. Do not temporarily change the parent process environment or add a production bypass flag. Tests constructing fixtures should likewise clear the variable only during synthetic issuance, then restore/set it for read/replay assertions.

### F2 — Refusal must precede import-time authentication

`validate_powermetrics_fiducial.py:441` computes `PREFLIGHT_SYSTEMATIC_SCREEN_S` during import. That reaches acceptance authentication and protocol/estimator hashing before `main`.

A guard added only at `main:1523` therefore cannot satisfy the literal “before any hashing” requirement. Make this derivation lazy:

1. Issuing dispatch refuses first.
2. Accepted issuing execution derives its comparator.
3. Recovery’s `resume-finalize` obtains the comparator explicitly after its own guard.
4. Read-only consumers may explicitly request the same authenticated derivation.

Do not replace the authenticated derivation with a copied constant or make importing the module refuse.

### F3 — Use the requested literal non-empty predicate

The existing helper parses the value:

```python
any(os.environ.get("JOULEWISE_BACKUP_ROOTS", "").split(os.pathsep))
```

The requested contract is:

```python
os.environ.get("JOULEWISE_BACKUP_ROOTS", "") != ""
```

Thus unset and `""` permit issuance; `/replacement`, relative roots, whitespace, `:`, and `::` refuse. Root interpretation remains exclusively in the read/replay locator code.

### Regression shape

Use a table-driven `unittest` matrix with **one case per callable entry and one case per issuing command mode**.

For each case:

1. Construct valid synthetic prerequisites under a temporary root with the override unset.
2. Snapshot the entire root: relative paths, object types, symlink targets, file bytes, and relevant metadata. Include original custody, mapped custody, ledger parent, lock sidecars, head pins, output directories, and capture-state locations.
3. Set a non-empty override and invoke the real entry.
4. Assert the exact refusal reason; CLI cases must exit nonzero and emit no successful evidence payload.
5. Assert the tree is unchanged, including no newly created directories or sidecars.
6. Add tripwires on downstream authentication, hashing, lease acquisition, stage callbacks, and subprocess/capture launch. Tree equality alone cannot detect a read/hash or a create-then-delete.
7. Exercise a missing output parent and an existing pending/open ledger separately.

Run additional parameter rows for unset, empty, a replacement path, a relative replacement, separator-only values, and whitespace. Unset/empty are positive controls; do not accidentally require their ordinary operation to succeed with invalid fixtures.

For the two reported gaps, cover ordinary lifecycle, bracket pre/post lifecycle, and direct `rederive_artifact`. For import ordering, use a fresh interpreter; importing modules before patching helpers would conceal F2.

Keep relocation-positive tests for validators and replay. Existing coverage at `tests/test_calibration_ledger_custody.py:263` is useful, but the current four-lambda issuance test at line 48 does not establish command-entry or zero-write coverage.

**Keep round-1 guards.** Rename/delegate them to the shared helper rather than maintaining multiple predicates. They protect direct library callers and later environment changes. Remove only an exact duplicate within the same entry function after the entry precondition is established; do not delete existing guards merely because the CLI is now guarded.

## Residual risk

Private writers and generic serialization primitives remain callable by trusted Python code. Examples include bootstrap payload publication, `_locked_append`, raw bundle writers, and manifest serializers. The CLI guard is not a security sandbox against arbitrary imports or direct filesystem writes.

Document those as internal sinks whose callers must enter through an issuing API; retain a shared-policy assertion at mutation sinks where it does not interfere with replay. A universal guard on every serializer would break legitimate reconstruction and fixture work.

An environment check also cannot establish how an already-created in-memory snapshot was authenticated earlier. Do not promise historical provenance tracking from this change. Avoid changing `JOULEWISE_BACKUP_ROOTS` during a production issuing process.

## SEAT BRIEF

Implement the custody override as an issuance-entry invariant using one shared `refuse_if_custody_override_active()` helper. This is a proposed implementation brief; the present consult authorizes no writes.

WRITE_SCOPE: ["joulewise/calibration_ledger.py", "joulewise/receipt_oracle.py", "joulewise/analysis_manifest_v3.py", "joulewise/arm_readiness.py", "joulewise/arm_readiness_evidence.py", "joulewise/arm_readiness_evidence_t0.py", "joulewise/window_duration_margins.py", "joulewise/controller.py", "joulewise/cli.py", "scripts/validate_powermetrics_fiducial.py", "scripts/reserve_calibration_window_bracket.py", "scripts/calibration_ledger_bootstrap.py", "scripts/calibration_ledger_backfill.py", "scripts/recover_calibration_ledger.py", "scripts/build_bracket_binding.py", "scripts/mint_floor_artifact.py", "scripts/mint_floor_artifact_generalized.py", "scripts/finalize_analysis_manifest.py", "scripts/run_campaign.py", "scripts/launch_window.py", "scripts/run_night.py", "scripts/author_arm_readiness_evidence.py", "scripts/author_arm_evidence_t0.py", "scripts/capture_t0_step.py", "scripts/generate_arm_readiness.py", "scripts/build_family_marker.py", "scripts/record_window_duration_margins.py", "scripts/issue_g2a_prefill_prompt_pin.py", "scripts/generate_g2a_probe_inputs.py", "tests/test_calibration_ledger_custody.py", "tests/test_custody_override_issuance.py"]

Apply the command/function placements in this review. The helper must inspect only whether the raw environment value is non-empty and raise the existing refusal string. Preserve that string through each CLI’s existing refusal protocol.

Refuse before input authentication, hashing, leases, reservations, capture state, output creation, or child launch. Defer fiducial import-time authentication. Preserve read/replay commands and shared reconstruction functions. Keep existing guards as defence in depth. Preserve lease cleanup when lifecycle methods refuse.

Add the per-entry/per-mode temporary-tree regression matrix, downstream-operation tripwires, literal non-empty edge cases, and relocated-read positive controls. Isolate receipt-oracle synthetic issuance from the parent override without adding a production bypass.

Do not modify evidence, historical receipts, pins, generated artifacts, reports, or bookkeeping. If required compatibility tests or authenticated tool pins need changes outside this allowlist, finish independent authorized work and return `NEEDS_SCOPE` with exact paths.

Run focused tests and `python3 -m unittest discover -s tests` under a controlled environment. No live capture, quiet-machine measurement, or real iCloud probing. Return changed files, exact verification evidence, unresolved compatibility issues, and a valid runner envelope.