codex
# U8 implementation plan — operator/readiness validation

## 1. Exact `WRITE_SCOPE`

Only these repository paths may change:

- [docs/phase_2/window_runbook.md](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/phase_2/window_runbook.md)
- [scripts/validate_frozen_plan_readiness.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/scripts/validate_frozen_plan_readiness.py)
- [tests/test_frozen_plan_readiness.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/tests/test_frozen_plan_readiness.py)

Explicitly excluded:

- D-117 campaign packs, generators, launchers, manifests, and extraction specs.
- `scripts/prewindow_check.sh`, ledger/bracketing modules, successor machinery, acceptance registry, reason-code producers/specification, operator packet, state files, and run reports.
- New committed fixture or schema files. Tests construct temporary fixtures at runtime.

If U5–U7 do not expose the required machine-readable plan/launch fields, or the reason-code unit has not landed, stop with `NEEDS_SCOPE`/`NEEDS_RULING`; do not weaken U8.

## 2. Dependencies and completion bar

Begin implementation only after:

1. U1’s two-slot session and exact binding interfaces are final.
2. U2 exposes the authenticated current-acceptance/registry verifier and pre-science successor probe.
3. U5–U7 freeze a common plan-tree and launch-command representation.
4. The reason-code item is resolved and tested: member verdict evidence has a structured `{member_id → reason_code}` mapping and emitted codes belong to the ratified vocabulary.
5. The reviewed integration head is clean.

U8 is complete when the validator refuses every stale, ambiguous, relative, occupied, self-attested, or mismatched readiness state; the runbook expresses the exact §5A order; focused and canonical suites pass.

## 3. Validator contract

### CLI

Use one primary interface:

```sh
.venv/bin/python scripts/validate_frozen_plan_readiness.py \
  --record /absolute/path/frozen-plan-readiness.json \
  --expected-record-sha256 <64-hex>
```

Test-only dependency injection may be exposed only through imported functions, not production CLI bypass flags.

Behavior:

- Set `sys.dont_write_bytecode = True`.
- Perform no filesystem writes, directory creation, locking, Git changes, or evidence repair.
- Emit one JSON receipt to stdout.
- Exit `0` only for `PASS`.
- Exit `2` for malformed arguments, check failures, or normalized internal refusal.
- `--help` remains informational exit `0`.
- No warning/flagged state: any unmet check is `REFUSE`.
- Collect all independently observable reason codes after the record parses; sort and deduplicate them.
- The receipt binds validation-time observations only. U1’s append operation must atomically recheck ledger head and identifier availability.

Receipt shape:

```json
{
  "schema_version": "joulewise.frozen_plan_readiness_receipt.v1",
  "status": "PASS",
  "record_sha256": "...",
  "plan_id": "...",
  "plan_sha256": "...",
  "reviewed_git_commit": "...",
  "ledger_head": {"sequence": 76, "head_digest": "..."},
  "acceptance": {"acceptance_id": "...", "artifact_sha256": "..."},
  "bracket_session_id": "...",
  "checks": [{"check_id": "...", "status": "pass"}],
  "reason_codes": []
}
```

### Strict readiness-record schema

Define `joulewise.frozen_plan_readiness.v1` in the script with exact-key validation. Required sections:

- `window_id`, `plan_id`, `reviewed_git_commit`.
- `plan`: plan path/SHA, SHA-sidecar path/SHA, plan-tree manifest path/SHA.
- `roots`: claim, bound, custody, quarantine, operator-log, pre/post calibration custody, and backup destinations.
- `ledger`: physical ledger, committed head-pin, expected sequence and digest.
- `acceptance`: registry, artifact path, acceptance ID/SHA, expected identity epoch.
- `waivers`: path and SHA.
- `environment_inventory`: policy, runtime, models/tokenizers, tool paths/hashes, identity epoch, charger/power requirements, storage requirements, and required live probes.
- `bracket_session`: session ID, pre/post attempt IDs, evidence-root ID, and exact custody locators.
- `launch_commands`: ordered command IDs with structured `argv` arrays.
- `toolchain_gate`: required reason-code contract/schema identifier and pin.

Repository inputs must be lexical relative paths contained beneath the clean checkout. Runtime/custody paths must be lexical absolute paths. Reject symlinks and path traversal. Read each authenticated file once and perform parsing and hashing from those captured bytes.

## 4. Checks and refusal semantics

| Check | Required behavior | Stable refusal codes |
|---|---|---|
| Record | Exact schema/keys; supplied digest equals captured bytes | `readiness_record_unreadable`, `readiness_record_invalid`, `readiness_record_sha256_mismatch` |
| Checkout | `HEAD` equals reviewed commit; measurement checkout clean, including untracked files | `readiness_checkout_head_mismatch`, `readiness_checkout_dirty` |
| Frozen plan | Frozen status and plan ID match; actual plan SHA equals record and sidecar; sidecar is exactly one GNU-style line naming the plan basename; plan-tree manifest authenticates every referenced config, manifest, policy, generator, launcher, and analysis/extraction input | `frozen_plan_invalid`, `frozen_plan_id_mismatch`, `frozen_plan_sha256_mismatch`, `frozen_plan_sidecar_invalid`, `frozen_plan_tree_invalid`, `frozen_plan_artifact_mismatch` |
| Fresh roots | All mutable roots are distinct literal absolute paths, safe types, non-symlinked, and fresh under the lead’s chosen absent/empty rule; `campaign.lock` absent; backup destinations exist and meet capacity | `readiness_path_not_absolute`, `readiness_path_unsafe`, `readiness_root_alias`, `readiness_root_not_fresh`, `readiness_campaign_lock_present`, `readiness_backup_unavailable` |
| Ledger | Load through the U1 reader; require committed pin bytes at Git `HEAD`, no malformed/pending/open state, and exact physical `(sequence,digest)` equality with both committed pin and readiness record | Propagate `calibration_ledger_*`; add `readiness_ledger_head_mismatch` for record disagreement |
| Acceptance | Resolve through U2’s authenticated registry, not a self-declared JSON object; require issued/claim-eligible role, exact artifact SHA and acceptance ID, valid parent/cutoff ancestry, cutoff present in ledger, and exact epoch match | `calibration_acceptance_invalid`, `calibration_acceptance_registry_mismatch`, `calibration_acceptance_id_mismatch`, `calibration_acceptance_sha256_mismatch`, `calibration_acceptance_cutoff_missing`, `calibration_acceptance_epoch_mismatch` |
| Waivers | File exists, hashes as recorded, and is the agreed canonical empty array; no launch argv contains `--waivers` or `--environment-override` | `readiness_waivers_invalid`, `readiness_waivers_nonempty`, `readiness_forbidden_override_argument` |
| Environment inventory | Closed required inventory; authenticate policy/runtime/model/tokenizer/tool bytes; reuse the repository environment probe for AC/external supply, high-power policy, low-power mode, thermal state, adapter identity/wattage, and disk; match OS/hardware/policy/protocol/estimator/cadence fields across plan, acceptance, environment, and bracket reservation | `readiness_environment_inventory_invalid`, `readiness_environment_artifact_missing`, `readiness_environment_artifact_mismatch`, `readiness_environment_probe_failed`, `readiness_environment_epoch_mismatch`, `readiness_environment_storage_insufficient` |
| Bracket identifiers | Validate with U1’s reservation-input helper; pre/post attempts distinct; session ID absent from every prior session; attempt IDs absent from ordinary receipts and all session slots; planned custody locations fresh | `readiness_bracket_session_id_claimed`, `readiness_bracket_attempt_id_duplicate`, `readiness_bracket_attempt_id_claimed`, `readiness_bracket_custody_claimed` |
| Launch commands | Require structured argv, complete expected command inventory, exact order, no shell fragments, and literal absolute values for every path-bearing operand, especially every collection and verdict `--runs-dir` | `readiness_launch_inventory_invalid`, `readiness_launch_command_missing`, `readiness_launch_order_mismatch`, `readiness_launch_path_not_absolute`, `readiness_launch_path_unresolved` |
| Reason-code gate | Require the reviewed head and frozen plan to pin the landed member-reason mapping schema/vocabulary; no prose-only failure evidence | `readiness_reason_code_gate_missing`, `readiness_reason_code_gate_mismatch` |

Any refusal means:

- Do not append the bracket session.
- Do not create or reuse a root.
- Do not arm or run calibration.
- Preserve the receipt and correct the desk/preflight state.
- Never “approve” a mismatch through a waiver or manual edit.

## 5. `window_runbook.md` §5A amendment

Amend §5A into the complete per-window operator bookend while retaining the existing clock explanation.

### Opening bookend

Order the steps exactly:

1. Run the frozen readiness validator and require exit `0`, `status: PASS`, and no reason codes.
2. Confirm the reviewed commit, plan/sidecar/tree hashes, acceptance artifact, empty waivers, fresh roots, environment inventory, and reason-code gate from the receipt.
3. Confirm physical ledger head equals the authenticated committed pin.
4. Correct the clock against the trusted source; record prior network-time state; disable network time.
5. Establish zero-agent and zero-output-streaming state, run the final prewindow check, then leave the machine untouched for ten minutes.
6. Append exactly one two-slot bracket capability using the readiness-bound session/pre/post identifiers. Record the capability receipt. Do not rerun ordinary readiness expecting physical/pin equality afterward—the governed open session intentionally advances the physical head.
7. Claim, capture, and finalize the `pre` slot.
8. Immediately run the U2 acceptance/trigger probe, before the bound corpus, references, or first science member.
9. Branch only as frozen:
   - Accepted under the current artifact: continue.
   - Range/count successor trigger: follow the lead-ratified session-state procedure, authenticate the successor, and revalidate before any member.
   - Identity change, systematic failure, malformed evidence, or unauthenticated successor: governed abort; no science.
10. Only after every gate is green, emit the single arm line and walk away.

### Closing bookend

Order the steps exactly:

1. Capture and finalize `post` before changing power, clock, network-time, or workload state.
2. If post cannot finalize, append the governed abort closure; never leave an unresolved session.
3. Emit the terminal head candidate; review and commit/authenticate the exact head pin.
4. Build the bracket binding and whole-window verdict from the same immutable terminal ledger snapshot.
5. Require the reason-coded member inventory and ordinary `status: passed`.
6. Run both verified backups and retain hashes/exit codes.
7. Restore network time only after measurement and custody closeout.

### R6/R7 hardening text

Add explicit operator rules:

- Every launch, verdict, extraction, backup, calibration, log, and custody command uses literal absolute paths. Relative paths, `~`, unresolved variables, and current-working-directory dependence are a readiness refusal.
- Never kill a running whole-window verdict. It may legitimately exceed two minutes and is serial/opaque today. Do not send interrupt/termination signals, remove its lock, or relaunch it while its PID is live.
- A dead or unreadable `campaign.lock` is preserved and diagnosed under the existing quarantine procedure; never blindly delete it.
- A verdict that ends naturally with a nonzero result is evidence to preserve, not permission to retry or rewrite.

## 6. Test list

All tests live in `tests/test_frozen_plan_readiness.py` and use temporary trees plus mocked Mac probes.

### Happy paths

- Valid alpha readiness record passes.
- Valid beta and gamma records pass through the same common contract.
- PASS receipt contains exact record/plan/ledger/acceptance/session identities.
- Validator performs no filesystem mutation.

### Record, checkout, and plan integrity

- Missing, malformed, duplicate-key, unknown-field, and wrong-record-SHA refusals.
- Wrong `HEAD`, dirty tracked file, and untracked-file refusals.
- Plan mutation, wrong plan ID, wrong recorded SHA, missing/ambiguous sidecar, wrong sidecar filename, and sidecar digest mismatch.
- Tree-manifest missing member, extra member, duplicate path, traversal, symlink, and referenced-byte substitution.
- Verify bytes are hashed and parsed from one captured read.

### Roots and launch paths

- Relative, `~`, `$RUNS_ROOT`, `${...}`, `..`, symlink, FIFO/device, aliasing, and ancestor-overlap paths refuse.
- Occupied claim/bound/calibration/custody root refuses.
- Live or stale `campaign.lock` refuses readiness; validator does not delete it.
- Missing/undersized backup destination refuses.
- Relative `--runs-dir` refuses separately for collection and whole-window verdict.
- Relative log, bound, calibration, backup, and plan-root operands refuse.
- Missing, reordered, duplicated, or shell-string launch commands refuse.

### Ledger and bracket IDs

- Clean physical head equal to committed pin passes.
- Missing/malformed/uncommitted pin, rollback, physical-ahead head, fork, pending ordinary attempt, and open prior bracket session refuse.
- Readiness-record head differing from authenticated head refuses.
- Reused session ID, reused ordinary attempt ID, reused session-slot attempt ID, identical pre/post IDs, and occupied custody locator refuse.
- Race regression: readiness passes, another writer claims the ID, then U1’s atomic reservation still refuses.

### Acceptance and successor ancestry

- Wrong SHA, wrong ID, unissued role, `claim_eligible=false`, missing registry entry, broken parent link, and cutoff absent from ledger refuse.
- Parameterized mismatch for all identity-epoch fields.
- Current issued artifact passes.
- Authenticated U2 successor passes.
- Self-consistent but unregistered successor refuses.

### Waivers, environment, and reason codes

- Missing, malformed, nonempty, noncanonical waiver file refuses.
- Any `--waivers` or `--environment-override` launch argument refuses.
- Missing inventory field, policy/tool/model hash mismatch, unavailable local model, wrong OS/hardware/power epoch, bad charger/wattage, low-power mode, thermal refusal, and insufficient storage refuse.
- Missing or mismatched reason-code schema/vocabulary pin refuses.
- Valid reason-code gate passes.

### Runbook contract checks

- Opening sequence ordering: readiness → ledger equality → clock → quiet idle → capability → pre finalization → successor probe → member one.
- Closing sequence ordering: post → terminal pin → binding/verdict → backups → clock restore.
- Runbook contains absolute-path mandate, pre-science successor placement, governed abort language, reason-code inventory requirement, and explicit never-kill-verdict rule.
- No example whole-window verdict uses a relative `--runs-dir`.

## 7. Verification

Run:

```sh
python3 -m unittest tests.test_frozen_plan_readiness
python3 scripts/validate_frozen_plan_readiness.py --help
python3 -m unittest discover -s tests
git diff --check
```

No quiet-machine capture or production campaign belongs in U8 verification. The lead later performs the real Mac readiness invocation from the clean measurement checkout.

## 8. Open questions for the lead

1. **Launcher integration:** U8’s three-file scope cannot insert the validator into U5–U7 `window-chain.zsh` files. Recommendation: require U5–U7 to generate the readiness call and structured launch manifest before pack freeze. Otherwise expand scope prospectively to the three launchers/generators and their plan tests.

2. **Plan-tree contract:** Which U5–U7 artifact is the single machine-readable transitive hash closure? Recommendation: one strict tree manifest per pack, with structured argv commands; do not infer closure by scanning directories.

3. **Absolute-path syntax:** Must commands contain literal absolute argv values, or may reviewed variables expand to absolute paths? Recommendation: require literals. If variables remain, require a closed expansion map and validate expanded argv without evaluating shell text.

4. **Fresh-root rule:** Does “fresh empty” mean nonexistent, or may an already-created empty directory pass? Recommendation: require nonexistent mutable roots; existing-empty roots cannot prove non-reuse as strongly.

5. **Successor with an open post slot:** May U2 authenticate/issue a successor while the original post slot remains open, or must the session be governed-aborted and a new predeclared capability used? Recommendation: follow the U2 state-machine proof; do not let U8 invent this transition.

6. **Reason-code closure:** What exact landed artifact/schema identifies the reconciled vocabulary and `{member_id → reason_code}` mapping? Recommendation: make it a hard pre-night dependency and expose a hashable machine-readable identifier for U8.

7. **Environment timing:** Which live properties must the validator sample, and what freshness limit applies before Ed’s final quiet/idle steps? Recommendation: validate stable identity/artifact/power facts immediately before §5A, then let `prewindow_check.sh` and per-invocation campaign admission own transient zero-agent/display/CPU state.

8. **Waiver canonical bytes:** Is semantic JSON `[]` sufficient, or must bytes be exactly `[]\n`? Recommendation: require the single canonical byte form to eliminate ambiguity.
tokens used
