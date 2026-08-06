# Calibration observation ledger

The canonical calibration ledger is an immutable SHA-256 receipt chain under
`joulewise.calibration_observation_ledger.v1`. D-109 R1 and R2 are controlling.
The ledger closes workflow omission, unregistered evidence, and rollback or
stale-head consumption; it does not defend against a malicious trusted writer
or an authority that rewrites both Git and the complete ledger history.

Live capture remains reservation-first: a `reservation` receipt with
`disposition=pending` precedes hardware state, and exactly one `finalization`
receipt closes that attempt. The repository-committed head pin is independent
authority over the physical ledger head. Claim evaluation requires their exact
agreement and one immutable snapshot threaded through every consumer.

## Historical import

Historical import is the one genesis-only exception that registers already
captured, hash-authenticated observations. It is not a second writer or an
ordinary capture route. Version 1 has the following fixed decisions.

1. **Ordering:** members are ordered by ascending `attempt_id`, then ascending
   `content_id`. Attempt IDs are required to be unique; the content-ID
   secondary key only makes collision diagnosis deterministic, after which a
   collision refuses rather than inventing a new attempt identity.
2. **Custody selection:** among all hash-complete checkout copies of one
   content ID, select the lexicographically smallest POSIX checkout-relative
   custody path. The selected copy's resolved absolute path is stored in both
   receipts, preserving the v1 live-receipt custody semantics; the relative
   spelling is used only as the deterministic comparison key. Incomplete
   copies do not outrank a complete copy; absence of any complete copy refuses.
3. **Transaction representation:** every member has exactly two receipts,
   `historical-import-v1-reservation` immediately followed by
   `historical-import-v1-finalization`. There is no summary receipt. The
   versioned event marker distinguishes these rows from live capture and binds
   this ordering/custody contract into every receipt digest. The terminal
   digest transitively binds the complete ordered member set. Omitting a
   summary keeps the existing two-transition attempt model and yields sequence
   `2 * member_count`.

Consumers must not treat an import-marked finalization as a fresh post-cutoff
observation. `LedgerObservation.is_historical_import` exposes the marker, and
`CalibrationLedgerSnapshot.post_cutoff_live_observations()` performs the safe
filtered enumeration.

### Ruled disposition table

The bootstrap takes dispositions only from an explicit JSON table; stored
evidence `status` fields have no authority and are not consulted. The table
shape is:

```json
{
  "schema_version": "joulewise.calibration_historical_import_table.v1",
  "ledger_schema": "joulewise.calibration_observation_ledger.v1",
  "identity_epoch": {
    "os_build": "...",
    "hardware_model": "...",
    "power_policy": "...",
    "sampling_interval_ms": 100,
    "estimator_revision": "...",
    "pulse_protocol_id": "..."
  },
  "members": [
    {
      "attempt_id": "...",
      "content_id": "64 lowercase hex characters",
      "artifact_sha256": {
        "raw/powermetrics.plist": "...",
        "events.jsonl": "...",
        "power_trace.csv": "...",
        "instrument_evidence.json": "...",
        "manifest.json": "..."
      },
      "disposition": "valid | systematic-invalid | ordinary-invalid | abandoned"
    }
  ]
}
```

The table member order is non-authoritative. The importer requires unique
attempt and content IDs, a complete five-artifact hash map, a content ID that
is exactly the canonical hash of the manifest/evidence byte hashes, and one
final disposition.

For every supplied custody directory the importer reads the actual bytes,
recomputes all five hashes and the content ID, verifies the manifest's complete
artifact table, verifies the evidence document's raw/events/trace hashes,
extracts the six-field epoch and full T1 binding from the authenticated
evidence, and preserves the source numeric lexemes for capture time and bound.
The authenticated exact-epoch content set must equal the table exactly. Every
selected attempt ID and artifact hash must equal its table row. Any mismatch,
missing member, extra member, malformed primary document, or absent
hash-complete custody copy refuses.

### Genesis and atomicity gates

Both dry-run and execution require:

- an empty physical ledger (an absent or zero-byte file), and
- a well-formed repository-committed head pin at sequence `0` with the
  all-zero genesis digest.

Execution prepares and canonicalizes the entire chain in memory, obtains the
exclusive ledger lock, rechecks both genesis conditions, appends the whole
chain in one write, flushes, and fsyncs once. A write or fsync exception rolls
the ledger back to zero bytes and refuses. A crash that defeats rollback still
cannot be mistaken for success: the genesis pin disagrees with any complete
physical extension, while a partial JSONL append is malformed. Retrying after
a successful import refuses because the ledger is nonempty.

The importer never writes the head pin. After execution, claim evaluation is
expected to refuse until the lead has reviewed and committed the exact printed
pin, preserving D-109 R1.4's anti-rollback boundary.

### Bootstrap CLI

`scripts/calibration_ledger_bootstrap.py` is dry-run unless `--execute` is
present. Required inputs are `--disposition-table`, `--checkout-root`, and one
or more run, `instrument_validation`, or custody roots. `--ledger` and
`--head-pin` override their repository defaults.

Dry-run creates no ledger or pin. Standard output is byte-stable NDJSON: one
canonical `receipt` record for every receipt, followed by one
`bootstrap-summary` containing the receipt count, final sequence/head, head-pin
object, and exact pretty-printed head-pin file content. `--execute` prints the
same chain after the single atomic append, with `executed=true`; it still does
not write the pin.
