# Calibration ledger append and recovery contract

Status: adopted, D-117 exit-completeness implementation (2026-08-08)
Policy revision: `d117-ledger-resident-v2`

## Scope and trust boundary

The calibration observation ledger is the sole authority for append recovery.
There is no redo journal, recovery payload file, or CLI-supplied replay source.
Every byte that recovery writes is either a canonical control receipt or the
target reconstructed from a valid in-ledger intent. Recovery never truncates,
overwrites, or deletes ledger bytes.

This protocol is tamper-evident inside the project's single-authority,
operator-attested trust model. It does not defend against a dishonest operator
who rewrites the ledger and every governing pin.

The issued D-116 ledger remains compatible. A ledger containing only the
original observation and bracket-session receipt schemas is reduced exactly as
before. Control receipts are additive and participate in the same sequence,
predecessor-digest, receipt-digest chain and terminal head pin.

This contract claims automated completeness only for physical append recovery.
Cross-layer exit completeness is owned by the immutable registry in
`joulewise/calibration_exits.py`, whose generated projection appears below.
Reservation, recovery, writer, and supervisor refusals are complete only when
their registry witness reaches its declared terminal result in a fresh public
CLI process. The Markdown projection is never a second policy authority.

## Canonical encoding and lineage

Every admitted physical record is canonical UTF-8 JSON followed by `LF`.
`receipt_digest` is SHA-256 of the canonical object with only
`receipt_digest` removed. Sequence numbers cover business and control receipts.

`ledger_id` is immutable after the first append intent. For an issued prefix it
is derived from the ledger schema, sequence-one digest, and sequence-one anchor.
For an empty lineage it is derived from the schema and the sequence-zero
genesis digest. Later intents repeat the first intent's identifier.

## `append-intent` control receipt

Schema: `joulewise.calibration_ledger_control.v1`  
Event: `append-intent`

In addition to the normal `ledger_schema`, `sequence`,
`predecessor_digest`, and `receipt_digest`, the receipt contains:

- `ledger_id`;
- `base_head`: exact intent-time `sequence`, `digest`, and physical
  `byte_offset`;
- `operation_key`: exactly `event`, `session_id`, `slot`, and `attempt_id`,
  with unavailable identities represented by JSON null;
- `target_schema_version` and `target_event`;
- `target_core`: the complete canonical semantic target excluding only
  `sequence`, `predecessor_digest`, and `receipt_digest`;
- `target_core_sha256`;
- `operation_id`, the canonical SHA-256 commitment over `ledger_id`,
  `base_head`, `operation_key`, and `target_core_sha256`.

The operation key contains the exact session/slot/attempt identity applicable
to the target type. The target schema validator, not diagnostic comparison,
validates session identity and the state transition.

An operation key may occur in only one intent. Retrying the exact same completed
operation returns its admitted target. Reusing the key with different semantic
content fails with `calibration_ledger_operation_conflict`.

## `abandon-tail` control receipt

Schema: `joulewise.calibration_ledger_control.v1`  
Event: `abandon-tail`

The receipt contains normal chain fields and:

- `abandoned_predecessor_sequence` and
  `abandoned_predecessor_digest`;
- `residue_start_offset`, `residue_length`, and `residue_sha256`;
- `receipt_offset` (the physical start of this control receipt);
- nonempty `reason_code`;
- `known_operation_id` and `known_target_core_sha256`, or null only when no
  valid intent is active;
- `actor_type` (`engine` or `operator`) and nonempty `actor_identity`;
- `policy_revision` and a nonempty `attestation_reason`;
- nullable `legacy_journal` metadata.

If malformed residue does not end in `LF`, the writer adds one framing `LF`
before the control record. The authenticated residue range excludes that
single framing byte; `receipt_offset` and the parser's exact zero-or-one-LF
invariant authenticate its location. Every other intervening byte is part of
the residue commitment.

The parser may cross non-admitted bytes only when the following abandonment
receipt has the expected sequence and predecessor, starts at its declared
offset, and authenticates the exact residue range and SHA-256. A crash while
writing abandonment leaves a larger residue; the next abandonment binds the
entire enlarged range. Earlier bytes remain unchanged.

`legacy_journal`, when present, contains the preserved path, byte length,
whole-file SHA-256, and the hex and SHA-256 of the observed final 64 bytes.
Legacy journal bytes are never parsed or replayed. Their only use is hashing
and custody recording; the file is preserved or archived.

## Physical parser and reducer

The physical parser starts at genesis and admits the maximal sequence/digest
chain. For each candidate record it applies these rules in order:

1. The schema, canonical self-digest, sequence, and predecessor must validate.
2. An intent must bind the immediately preceding physical head and its exact
   byte offset, use the lineage's `ledger_id`, commit a valid target schema,
   and describe a legal business-state transition.
3. While an intent is active, the only admissible business record is the exact
   target core reconstructed at the then-current sequence and predecessor.
4. An abandonment may bridge residue only through the exact range/SHA rule
   above. When an intent is active it must repeat that intent's operation and
   target commitments. It quarantines bytes; it does not revoke the intent.
5. A business receipt closes the active intent only when its complete semantic
   core matches. Control receipts are ignored by the observation and bracket
   reducers but remain in the physical chain and head pin.
6. An issued prefix with no control receipts remains admissible. The first
   admitted control receipt is the activation boundary; after it, every
   business receipt must close an active intent. A bare business receipt after
   activation is refused as `calibration_ledger_ungoverned_business` even when
   its shape, sequence, predecessor, and business transition would otherwise
   validate.

The maximal admitted chain defines the residue boundary. Every byte after that
boundary is residue, including a complete chain-shaped receipt preceded by
junk or any other byte that prevents it from extending the head. Such an
orphaned receipt is not a valid record and is included in one whole-range
abandonment. If an active intent commits that receipt's semantic target,
deterministic intent recovery takes precedence over operator abandonment.

An unresolved valid intent or terminal residue yields
`calibration_ledger_recovery_required`. Terminal reads and claim evaluation
refuse that state. A clean abandonment control receipt is evidence, not an
unresolved observation.

Terminal session status is determined from business receipts. Once the
session's POST finalization or governed business abort is terminal, any
authenticated trailing control receipts remain part of the physical head and
the emitted terminal pin pins that final physical control receipt. A later
business receipt is not a trailing-control extension and prevents terminal-pin
emission.

## State machine

| State | Durable condition | Legal action |
|---|---|---|
| clean | maximal chain ends without active intent or residue | append intent |
| intent | valid intent is admitted and no target bytes follow | construct target from intent |
| append | following bytes are absent or an exact target prefix | append only missing suffix and fsync |
| finalize | target schema, commitment, chain placement, and transition validate | admit target as head |
| abort | bytes cannot be admitted | append an exact abandonment receipt |

A valid intent is irrevocable. Zero target bytes always lead to deterministic
completion. If following bytes disagree, the engine first appends an
abandonment receipt, then reconstructs the committed target at the new physical
head. It never substitutes the mismatching bytes.

Every physical append-recovery refusal has one governed exit:

1. deterministic completion of a valid intent;
2. engine abandonment of mechanically unambiguous residue (an active-intent
   mismatch or a torn uncommitted final record); or
3. operator-attested `abandon-tail` for other terminal residue.

There is no deletion-based recovery state.

## Crash table

| Crash point | Durable state | Retry result |
|---|---|---|
| during intent write | torn, uncommitted control residue | engine abandonment; no business operation is inferred |
| after intent fsync | valid irrevocable intent, zero target bytes | exact target completion |
| during target write | exact target prefix or mismatching residue | missing-suffix completion, or abandonment then target |
| after target fsync | completed operation | exact idempotent return |
| during abandonment | enlarged residue after the same valid head | next abandonment binds the enlarged range |
| after abandonment fsync | valid intent remains active, residue governed | exact target completion |

All append stages fsync the ledger before advancing. One permanent dedicated
`<ledger>.lock` regular inode serializes recovery, reservation, claim,
countdown, capture, finalization, and abort. The writer acquires its
nonblocking kernel `flock` before recovery and holds the descriptor
continuously until finalization or governed abort. The inode is never deleted.
Only kernel lease ownership is a liveness discriminator; PID text, process
UUIDs, and exception substrings have no policy role.

## Stable bracket claim and pin relation

A bracket claim ID is the domain-separated canonical SHA-256 of policy
revision plus `(session_id, slot, attempt_id)`. It is stable across processes.
A per-process UUID never participates in durable equality. At retry, the
stable operation key and target commitment distinguish exact completion from
semantic conflict; the writer lease independently distinguishes a live holder
from a dead predecessor.

The machine gate reports one typed pin relation:

- `exact`: physical and committed heads match;
- `physical_ahead`: the committed head is an authenticated prefix and desk
  work is required;
- `physical_behind`: rollback; or
- `diverged`: the committed pin is not on the physical chain.

Only `scripts/recover_calibration_ledger.py advance-head-pin` may advance the
pin. It requires the exact authenticated candidate, operator identity,
attestation reason, a clean physical protocol with no legacy journal, and a
terminal session (or sessionless recovery-only control head). Execution is
desk-only: review the candidate and diff, run with `--execute`, commit the pin,
restore a clean checkout, and repeat readiness. There is no night-path
uncommitted-head override.

## Composite readiness gate

`inspection.state == "clean"` is diagnostic, never ARM authorization. The
machine readiness predicate additionally enforces absence of a legacy journal,
intent, residue, incompatible operation target, and live writer, plus the
phase-specific pin/session/custody relation:

- `pre-reserve`: exact committed pin, no open session, compatible reservation;
- `pre-slot`: exact governed open session and next slot, exact stable claim
  state, and custody requiring neither resume nor abort; and
- `terminal`: exact terminal session and authenticated terminal pin candidate.

The standalone CLI is early warning. The enforcing `pre-slot` predicate runs
only after the writer owns the lease and that descriptor remains held directly
through countdown, capture, and closure. A parser-clean result with a non-null
`legacy_journal_path` is blocked by the machine gate.

## Generated cross-layer refusal projection

<!-- BEGIN GENERATED: calibration-refusal-registry -->
| Code | Component | Phase | Exit ID | Terminal result | Night loss | Witness |
|---|---|---|---|---|---:|---|
| `calibration_ledger_missing` | ledger | operation | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_ledger_missing` |
| `calibration_ledger_malformed` | ledger | operation | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_ledger_malformed` |
| `calibration_ledger_chain_conflict` | ledger | operation | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_ledger_chain_conflict` |
| `calibration_ledger_attempt_conflict` | ledger | operation | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_ledger_attempt_conflict` |
| `calibration_ledger_bracket_session_conflict` | ledger | operation | `abort-session` | `session_aborted` | `true` | `witness.calibration_ledger_bracket_session_conflict` |
| `calibration_ledger_bracket_slot_claimed` | ledger | operation | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_ledger_bracket_slot_claimed` |
| `calibration_ledger_bracket_session_open` | ledger | operation | `abort-session` | `session_aborted` | `true` | `witness.calibration_ledger_bracket_session_open` |
| `calibration_ledger_content_conflict` | ledger | operation | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_ledger_content_conflict` |
| `calibration_ledger_pending` | ledger | operation | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_ledger_pending` |
| `calibration_ledger_head_uncommitted` | ledger | operation | `guarded-head-pin-advancement` | `night_stopped_preserved` | `true` | `witness.calibration_ledger_head_uncommitted` |
| `calibration_ledger_head_mismatch` | ledger | operation | `guarded-head-pin-advancement` | `night_stopped_preserved` | `true` | `witness.calibration_ledger_head_mismatch` |
| `calibration_ledger_rollback` | ledger | operation | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_ledger_rollback` |
| `calibration_ledger_recovery_required` | ledger | operation | `repair` | `operation_completed` | `false` | `witness.calibration_ledger_recovery_required` |
| `calibration_ledger_operation_conflict` | ledger | operation | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_ledger_operation_conflict` |
| `calibration_ledger_ungoverned_business` | ledger | operation | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_ledger_ungoverned_business` |
| `calibration_ledger_baseline_missing` | ledger | operation | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_ledger_baseline_missing` |
| `calibration_ledger_custody_invalid` | ledger | operation | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_ledger_custody_invalid` |
| `calibration_ledger_snapshot_required` | ledger | operation | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_ledger_snapshot_required` |
| `calibration_ledger_off_ledger_artifact` | ledger | operation | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_ledger_off_ledger_artifact` |
| `calibration_observation_unclassifiable` | ledger | operation | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_observation_unclassifiable` |
| `calibration_live_writer_contention` | lease | writer-lease | `live-writer-contention` | `operation_completed` | `false` | `witness.calibration_live_writer_contention` |
| `calibration_unsafe_lock_inode` | ledger | operation | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_unsafe_lock_inode` |
| `calibration_physical_ledger_unreadable` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_physical_ledger_unreadable` |
| `calibration_legacy_journal_unreadable` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_legacy_journal_unreadable` |
| `calibration_legacy_journal_archive_conflict` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_legacy_journal_archive_conflict` |
| `calibration_legacy_journal_archive_failed` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_legacy_journal_archive_failed` |
| `calibration_tail_requires_abandon` | recovery-cli | recovery | `abandon-tail-then-repair` | `operation_completed` | `false` | `witness.calibration_tail_requires_abandon` |
| `calibration_intent_target_malformed` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_intent_target_malformed` |
| `calibration_recovery_nonconvergent` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_recovery_nonconvergent` |
| `calibration_recovery_credentials_invalid` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_recovery_credentials_invalid` |
| `calibration_abandon_credentials_invalid` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_abandon_credentials_invalid` |
| `calibration_abandon_pin_mismatch` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_abandon_pin_mismatch` |
| `calibration_abandon_active_intent` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_abandon_active_intent` |
| `calibration_abandon_not_clean` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_abandon_not_clean` |
| `calibration_head_pin_unreadable` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_head_pin_unreadable` |
| `calibration_head_pin_malformed` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_head_pin_malformed` |
| `calibration_head_pin_not_committed` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_head_pin_not_committed` |
| `calibration_reservation_input_invalid` | reservation-cli | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_reservation_input_invalid` |
| `calibration_reservation_head_mismatch` | reservation-cli | pre-reserve | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_reservation_head_mismatch` |
| `calibration_reservation_identity_conflict` | reservation-cli | pre-reserve | `abort-session` | `session_aborted` | `true` | `witness.calibration_reservation_identity_conflict` |
| `calibration_reserved_slot_mismatch` | writer | pre-slot-or-capture | `abort-session` | `session_aborted` | `true` | `witness.calibration_reserved_slot_mismatch` |
| `calibration_session_not_found` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_session_not_found` |
| `calibration_session_not_open` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_session_not_open` |
| `calibration_slot_order_conflict` | writer | pre-slot-or-capture | `abort-session` | `session_aborted` | `true` | `witness.calibration_slot_order_conflict` |
| `calibration_claim_id_invalid` | writer | pre-slot-or-capture | `abort-session` | `session_aborted` | `true` | `witness.calibration_claim_id_invalid` |
| `calibration_finalization_binding_conflict` | writer | pre-slot-or-capture | `abort-session` | `session_aborted` | `true` | `witness.calibration_finalization_binding_conflict` |
| `calibration_session_not_terminal` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_session_not_terminal` |
| `calibration_session_terminal_not_head` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_session_terminal_not_head` |
| `calibration_custody_partial` | recovery-cli | recovery | `abort-session` | `session_aborted` | `true` | `witness.calibration_custody_partial` |
| `calibration_custody_unreadable` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_custody_unreadable` |
| `calibration_custody_complete_use_resume` | recovery-cli | recovery | `resume-finalize` | `operation_completed` | `false` | `witness.calibration_custody_complete_use_resume` |
| `calibration_plan_unreadable` | recovery-cli | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_plan_unreadable` |
| `calibration_plan_hash_mismatch` | recovery-cli | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_plan_hash_mismatch` |
| `calibration_pre_reserve_not_ready` | reservation-cli | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_pre_reserve_not_ready` |
| `calibration_pre_slot_not_ready` | writer | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_pre_slot_not_ready` |
| `calibration_terminal_not_ready` | ledger | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_terminal_not_ready` |
| `calibration_pin_advancement_not_needed` | recovery-cli | recovery | `guarded-head-pin-advancement` | `night_stopped_preserved` | `true` | `witness.calibration_pin_advancement_not_needed` |
| `calibration_pin_advancement_unsafe` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_pin_advancement_unsafe` |
| `calibration_pin_candidate_mismatch` | recovery-cli | recovery | `hard-stop-preserved` | `night_stopped_preserved` | `true` | `witness.calibration_pin_candidate_mismatch` |
| `calibration_reservation_json_invalid` | reservation-cli | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_reservation_json_invalid` |
| `calibration_writer_bracket_arguments` | writer | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_writer_bracket_arguments` |
| `calibration_writer_bracket_rederive_conflict` | writer | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_writer_bracket_rederive_conflict` |
| `calibration_frozen_protocol_invalid` | writer | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_frozen_protocol_invalid` |
| `calibration_rederive_output_required` | writer | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_rederive_output_required` |
| `calibration_rederive_failed` | writer | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_rederive_failed` |
| `calibration_output_requires_rederive` | writer | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_output_requires_rederive` |
| `calibration_quiet_mac_auth_required` | writer | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_quiet_mac_auth_required` |
| `calibration_power_policy_required` | writer | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_power_policy_required` |
| `calibration_display_arm_failed` | writer | pre-slot-or-capture | `abort-session` | `session_aborted` | `true` | `witness.calibration_display_arm_failed` |
| `calibration_sampler_never_ready` | writer | pre-slot-or-capture | `abort-session` | `session_aborted` | `true` | `witness.calibration_sampler_never_ready` |
| `pulse_calibration_rollover_gate_timeout` | writer | pre-slot-or-capture | `abort-session` | `session_aborted` | `true` | `witness.pulse_calibration_rollover_gate_timeout` |
<!-- END GENERATED: calibration-refusal-registry -->

This table is generated from `REFUSAL_INVENTORY`. Its exact freshness is a
test gate; edits belong in the Python registry and are projected here.

## Operator authority and CLI

`scripts/recover_calibration_ledger.py` exposes:

- `inspect`: read-only physical state;
- `repair`: deterministic ledger-only recovery;
- `abandon-tail`: an operator identity plus nonempty attestation reason;
- `explain <code>`: the registry-owned exit ID, ARM effect, and next command;
- `readiness`: phase-aware early warning, never ARM authorization;
- `session-status`: frozen-plan/ledger/custody progress from fresh state;
- `resume-finalize`: authenticate complete custody and finalize it;
- `abort-session`: preserve partial custody and close under the same lease; and
- `advance-head-pin`: guarded desk-only pin advancement.

The CLI accepts no payload, journal source, target JSON, or byte range.
`abandon-tail` always begins at the parser's first byte after the maximal valid
chain. Before appending, it verifies that the digest at the pin's exact
sequence equals the committed digest; a same-sequence sibling is not the
committed head. It refuses when that pinned head is absent or a valid intent is
active. Because the residue starts only after the maximal admitted chain, the
whole range may include later chain-shaped orphan bytes without crossing a
valid record. Operators cannot abandon a committed head, an admitted receipt,
or an irrevocable business operation.

The powermetrics writer calls the same `repair` implementation while holding
the writer lease, validates the exact slot under that lease, and uses the
stable claim identity. Automatic physical recovery is the normal path;
cross-layer disposition uses the registered public exit and never message
matching or in-memory lifecycle reuse.
