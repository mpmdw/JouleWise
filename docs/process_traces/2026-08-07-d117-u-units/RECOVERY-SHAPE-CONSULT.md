# Recovery-shape escalation consult — response of record (2026-08-07)

Sol xhigh (fast tier), read-only, run via scripts/codex-bridge (audit rows
in .codex-bridge/invocation_manifest.jsonl). Charge: ESCALATION-U1-RECOVERY.md.

**MAGISTRATE ADOPTION (Fable, 2026-08-07): the recommended shape is
ADOPTED** — the sidecar redo-journal is removed; recovery becomes a
ledger-resident intent/finalize/abandon protocol (intent receipts bind
ledger lineage + exact head + operation key + content commitment;
abandonment is an append-only receipt over exact residue ranges; no
recovery_required state without a governed exit). F1 is retained as a
LEDGER-ONLY recovery/inspection/abandonment entry point with a new
contract; the three rounds of sidecar work are discarded, not patched.
Legacy .append-journal files are archived via abandonment receipt, never
replayed. Implementation is a NEW work order (contract + ledger + recovery
script + writer integration + tests + runbook), sequenced AFTER the
F2/F4/F5/F6a night-fix split lands (shared file surface), under the full
D-118 gate; its delta must run the consult's closure regression and the
seven-point future-delta checklist.

---

## Positions

1. **Remove the sidecar redo journal.** Adopt a ledger-resident intent protocol: the ledger remains the sole recovery authority and permanently records intent, completion, and abandonment.
2. **Keep append-only semantics physically and logically.** Recovery never truncates, deletes, or overwrites ledger bytes.
3. **Preserve the adjudicated trust model.** This remains single-authority and operator-attested, with machine-checked consistency and tamper evidence—not protection from a dishonest operator.

The current mechanics explain the recurring defect. `_locked_append` atomically writes and fsyncs a sidecar, renames it, directory-fsyncs, appends/fsyncs the ledger, then unlinks and directory-fsyncs the sidecar. The sidecar is therefore the only durable statement of intended content. Its self-hashed `operation_id` proves internal integrity, not that it belongs to this target operation. `_journal_completed_raw` proves only shared head plus payload-prefix agreement, while `_validate_reconstructed_append` validates the foreign operation only **after** its missing bytes have been written. More fields in that free-floating file relocate the ambiguity unless an already-durable ledger record authenticates them.

## Disagreements

- **Reject direct truncation of torn JSONL.** Even if the last line is visibly incomplete, truncation removes custody bytes and leaves no receipt.
- **Reject “just add session ID/operation ID/head hash” to the sidecar.** A coherent journal copied from a same-head fork can carry all those self-asserted fields. A sidecar is conclusively bound only when an in-ledger intent record commits to its identity and content.
- **Reject raw-line-only recovery without durable intent.** It can safely quarantine a torn line, but cannot reconstruct a PRE/POST finalization after a partial append, increasing night-loss probability.
- **A retained journal can be sound only as a cache subordinate to an in-ledger intent.** At that point it is redundant and adds rename, cleanup, stale-file, and reader-consistency states.

## Open questions

None requiring a ruling. Schema spellings and exact CLI acknowledgement text are implementation details; the architectural decision is complete.

## Recommendation

### Adopt a ledger-native intent/finalize/abandon protocol

All future physical records—including transport-control records—participate in the existing sequence/digest chain and therefore in the terminal head pin.

#### Binding fields

An `append-intent` control receipt must contain:

- Immutable `ledger_id`, derived from the ledger lineage.
- Exact intent-time physical head: sequence, digest, and byte offset.
- Stable business-operation key: event plus exact session/slot/attempt identity.
- Exact target schema/event and canonical semantic `target_core`.
- `target_core_sha256`.
- `operation_id = H(ledger_id, base head, operation key, target-core commitment)`.
- Its normal sequence, predecessor digest, and receipt digest.

The semantic target core excludes physical sequence/predecessor fields so recovery can still finalize it after recording unexpected residue. Session identity is validated as part of the target schema, not merely compared as diagnostic metadata.

This combination terminates the class: ledger lineage + exact head binds the target location; the operation key binds the transition; the content commitment binds what may be written; and the intent receipt makes those bindings durable before recovery can act.

### State machine

| State | Durable condition | Legal next action |
|---|---|---|
| `clean` | Valid chain, no active intent or residue | Append intent |
| `intent` | Complete, valid intent is chain head | Append its deterministically constructed target receipt |
| `append` | Target bytes are absent or an exact prefix | Append only the committed missing suffix and fsync |
| `finalize` | Complete target receipt matches intent and validates state transition | Accept it as the new chain head |
| `abort` | Bytes after the maximal valid head cannot be admitted | Append an abandonment control receipt binding their exact range and SHA |

A durable valid intent is **irrevocable**: neither an operator nor recovery may abandon its semantic operation. Zero target bytes therefore cause deterministic completion, not refusal. If bytes after a valid intent disagree with the committed target, recovery first quarantines those bytes with an abandonment receipt and then writes the exact committed target.

A torn or malformed intent is not a valid custody transition. It may be abandoned because no authenticated business operation exists.

### Append-only abandonment

The parser identifies the maximal valid physical chain. Any remaining bytes are non-admitted tail residue. Under the stable lock, abandonment appends a canonical control receipt containing:

- predecessor sequence/digest;
- residue start offset, length, and SHA-256;
- reason code;
- known intent/operation commitment, if any;
- engine or operator identity;
- policy revision and nonempty attestation reason.

The parser may cross malformed bytes only when the following abandonment receipt exactly authenticates that byte range and chains from the prior valid head. Repeated crashes while writing the abandonment receipt remain recoverable: the next receipt binds the enlarged residue. No byte is removed.

Operator abandonment is permitted only from the first byte after the maximal valid chain. It cannot cover a complete intent, finalized receipt, committed/pinned head, or earlier custody claim. This is not an operator-privileged rewrite channel.

Every append-recovery refusal must resolve to one of:

1. deterministic completion of a valid intent;
2. engine-classified abandonment of mechanically unambiguous residue; or
3. explicit operator-attested `abandon-tail`.

There must be no `recovery_required` state whose only exit is deletion.

### Files

- **New contract:** `docs/contracts/calibration_ledger_append.md`—schemas, reducer, crash table, and operator authority.
- **`joulewise/calibration_ledger.py`:** remove sidecar journal/recovery-evidence logic; add intent and abandonment control receipts, parser support, idempotent operation-key handling, and ledger-only recovery.
- **`scripts/recover_calibration_ledger.py`:** `inspect`, deterministic `repair`, and governed `abandon-tail`; accepts no payload or journal source.
- **`scripts/validate_powermetrics_fiducial.py`:** call ledger-only recovery before slot validation; exact completed operations are idempotent.
- **Tests:** `tests/test_calibration_ledger.py` and `tests/test_powermetrics_fiducial.py`.
- **Runbook:** stage automatic recovery before reserve/PRE/POST and an outer one-shot retry for unattended execution.

Legacy `.append-journal` files must never be replayed by the new implementation. If one exists at migration, record its SHA and observed tail in a ledger abandonment receipt and preserve/archive the file; do not delete or consume its payload.

### Night-loss ranking

1. **Ledger-resident intent with automatic recovery — recommended.** Lowest sound night-loss probability: a complete intent reconstructs the exact transition; cleanup cannot wedge the ledger; standard recovery requires no operator.
2. **Ledger-anchored sidecar.** Custody-sound if fully anchored, but retains additional rename/fsync/unlink and stale-artifact states.
3. **Raw receipt plus tail tombstone, without intent.** Custody-sound but loses reconstructability when PRE/POST finalization tears.
4. **Current free-floating sidecar.** Reject: foreign replay and permanent refusal remain possible.

The readiness gate must verify no unresolved intent, residue, or legacy sidecar before arming each window. Recognized recovery should be automatic; the operator command is the durable emergency exit, not the normal night path.

### Closure regression

From one identical ledger head:

1. Create operations A and B with different operation identities but receipt bytes sharing a positive prefix.
2. Persist A’s in-ledger intent.
3. Place zero bytes, one shared byte, several shared bytes, and `len(A)-1` bytes after it; separately inject B’s fragment and complete bytes.
4. Recover.
5. Assert the only admitted business receipt is the exact semantic target committed by A’s intent; B never appears.
6. For mismatching bytes, assert an abandonment receipt binds their exact range/SHA before A finalizes.
7. Assert no sidecar payload is read and no byte is deleted.
8. Mutation checks must fail when intent/content binding is removed or abandonment is allowed to cover a valid intent.

Crash-boundary tests must kill the process during intent write, after intent fsync, during target write, after target fsync, during abandonment, and after abandonment fsync. Every retry must converge to either the exact committed operation or a durable abandonment receipt.

A future delta audit must verify:

- recovery obtains target bytes only from the locked ledger;
- no CLI, temp file, or sidecar can supply replay content;
- operation-key conflicts fail closed;
- abandonment cannot cross a valid record or intent;
- head pins authenticate control receipts;
- zero-, positive-prefix-, and complete-foreign variants all remain dead;
- deleting the binding checks makes the foreign-fork regression fail.

### F1 disposition

**Keep the standalone recovery capability, but replace its implementation and contract.** Delete the journal-oriented `recover_calibration_ledger_append` behavior. F1 becomes a ledger-only recovery/inspection/abandonment entry point, and the ordinary writer invokes the same deterministic repair path before validation.

The three rounds of sidecar recovery work should be discarded rather than patched a fourth time.

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Adopted shape: remove the free-floating redo sidecar and use ledger-resident intent, finalization, and append-only abandonment receipts; retain F1 only as a ledger-only recovery entry point.","pathspec":[],"verification":["Read escalation and trust-model authorities","Inspected impl/d117-u1-gate-debt at 98b8e0b and main...branch recovery diff","Walked append/fsync/rename, writer-retry, positive-prefix, and abandonment interleavings","git diff --check main...impl/d117-u1-gate-debt: OK","git status --short --branch: clean"],"flags":["no_edits","journal_free_shape","operator_attested","fourth_fix_forbidden"]}
