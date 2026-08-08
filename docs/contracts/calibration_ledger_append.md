# Calibration ledger append and recovery contract

Status: adopted, D-117 recovery-shape implementation (2026-08-07)  
Policy revision: `d117-ledger-resident-v1`

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

Every refusal has one governed exit:

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

All append stages fsync the ledger before advancing. The dedicated lock inode
serializes parsing, recovery, intent creation, and target finalization.

## Operator authority and CLI

`scripts/recover_calibration_ledger.py` exposes only:

- `inspect`: read-only physical state;
- `repair`: deterministic ledger-only recovery;
- `abandon-tail`: an operator identity plus nonempty attestation reason.

The CLI accepts no payload, journal source, target JSON, or byte range.
`abandon-tail` always begins at the parser's first byte after the maximal valid
chain. Before appending, it verifies that the digest at the pin's exact
sequence equals the committed digest; a same-sequence sibling is not the
committed head. It refuses when that pinned head is absent or a valid intent is
active. Because the residue starts only after the maximal admitted chain, the
whole range may include later chain-shaped orphan bytes without crossing a
valid record. Operators cannot abandon a committed head, an admitted receipt,
or an irrevocable business operation.

The ordinary powermetrics writer calls the same `repair` implementation before
slot validation and makes one outer retry with the same stable operation
identity. Automatic recovery is the normal path; operator abandonment is the
emergency custody exit.
