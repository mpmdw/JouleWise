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
2. **Custody selection:** import authority is a reviewed, raw-byte-SHA-256-
   pinned custody manifest mapping every table content ID to one exact absolute
   locator. The importer uses exactly that locator; invocation roots have no
   selection authority. A missing or hash-incomplete pinned copy, a locator or
   governed artifact reached through a symlink, or a manifest/table content-set
   mismatch refuses. Optional roots are a strict cross-check: every pinned
   locator must be discovered, and the discovered hash-complete content set
   must equal the manifest set. `--emit-custody-manifest` is the only place the
   lexicographically smallest POSIX checkout-relative rule selects locators;
   it prints review bytes and writes nothing.
3. **Transaction representation:** every member has exactly two receipts,
   `historical-import-v1-reservation` immediately followed by
   `historical-import-v1-finalization`. There is no summary receipt. The
   versioned event marker distinguishes these rows from live capture and binds
   this ordering/custody contract into every receipt digest. The terminal
   digest transitively binds the complete ordered member set. Omitting a
   summary keeps the existing two-transition attempt model and yields sequence
   `2 * member_count`.

Consumers must not treat an import-marked finalization as a fresh post-cutoff
observation or bracket endpoint. Production candidate discovery checks the
marker directly, and prospective trigger subtraction uses
`CalibrationLedgerSnapshot.post_cutoff_live_observations()`. At consumption,
the acceptance artifact's `prior_observation_set` must exactly equal the
import-marked ledger prefix at its cutoff (attempt ID, content ID,
classification disposition, and epoch); any omission, addition, or live row in
that prefix refuses.

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
      "disposition": "valid | systematic-invalid | ordinary-invalid"
    }
  ]
}
```

The table's exact raw bytes are authenticated by required
`--expected-table-sha256`, and that digest is recorded in the prepared plan and
bootstrap summary. The table member order is non-authoritative. The importer
requires unique attempt and content IDs, a complete five-artifact hash map, a
content ID that is exactly the canonical hash of the manifest/evidence byte
hashes, and one importable disposition. `abandoned`, `unresolved`, and every
other disposition outside the three values above refuse.

The reviewed custody manifest shape is:

```json
{
  "schema_version": "joulewise.calibration_historical_import_custody_manifest.v1",
  "ledger_schema": "joulewise.calibration_observation_ledger.v1",
  "members": {
    "content-id-64-lowercase-hex": "/exact/absolute/custody/locator"
  }
}
```

Its exact raw-byte digest is authenticated by required
`--expected-custody-manifest-sha256` and reported in the bootstrap summary.

For every manifest-pinned custody directory the importer opens contained
no-follow descriptors, reads the actual bytes, recomputes all five hashes and
the content ID, verifies the manifest's complete artifact table, verifies the
evidence document's raw/events/trace hashes, extracts the six-field epoch and
full T1 binding from the authenticated evidence, and preserves the source
numeric lexemes for capture time and bound.
The authenticated manifest content set must equal the table exactly. Every
selected attempt ID and artifact hash must equal its table row. Any mismatch,
missing member, extra member, malformed primary document, or absent
hash-complete custody copy refuses.

### Genesis and atomicity gates

Dry-run requires:

- an empty physical ledger (an absent or zero-byte file), and
- a well-formed repository-committed head pin at sequence `0` with the
  all-zero genesis digest.

Execution requires the same genesis pin. It normally also requires an absent
or empty physical ledger. Its sole nonempty exception is the idempotent
durability-confirm path described below.

Every ledger writer locks the dedicated adjacent
`<ledger-filename>.lock` file. That lock file is created if absent and is never
replaced. A writer acquires it before opening or re-opening the ledger path,
and holds it through every append or replacement. The replaceable ledger inode
is never the lock object, so a writer that waited during replacement cannot
resume against an old, unlinked ledger inode.

Execution prepares and canonicalizes the entire chain in memory, obtains the
stable lock, rechecks the genesis pin and physical ledger by path, and
immediately re-opens all five artifacts for every member through contained
no-follow descriptors. Every hash must still equal the prepared plan. It then
writes and fsyncs the complete payload to a sibling staging file and atomically
replaces the empty ledger. Until replacement, readers see only genesis; after
replacement, readers see only the complete chain. A write, staging-file fsync,
reauthentication, or replacement failure leaves zero reader-visible receipts.
Process death mid-stage likewise leaves a retryable genesis ledger.

`os.replace` is the transaction commit point. After replacement, the importer
fsyncs the parent directory and retries that directory fsync once if it fails.
If both attempts fail, the chain is **committed with durability uncertain**;
it is never reported as an atomic-append failure. The CLI still emits every
canonical receipt and the full summary, whose machine-readable `outcome` is
`committed_durability_uncertain`, then exits `3`. The operator must rerun the
identical `--execute` invocation before updating the head pin.

While the committed pin remains genesis, such a rerun recomputes the complete
plan from the authenticated table, manifest, and custody bytes under the same
rules. Under the stable lock, it compares the physical ledger byte-for-byte
with `plan.ledger_bytes`; matching bytes enter the idempotent confirm path,
which re-fsyncs the parent directory without replacing or appending and emits
the same receipt chain and head/input-digest summary with `outcome=committed`.
Any other nonempty ledger refuses with the ordinary empty-ledger error. Once
the reviewed head pin is updated away from genesis, a further invocation
refuses at the normal genesis-pin gate.

The importer never writes the head pin. After execution, claim evaluation is
expected to refuse until the lead has reviewed and committed the exact printed
pin, preserving D-109 R1.4's anti-rollback boundary.

### Bootstrap CLI

`scripts/calibration_ledger_bootstrap.py` is dry-run unless `--execute` is
present. Both dry-run and execution require `--disposition-table`,
`--expected-table-sha256`, `--custody-manifest`, and
`--expected-custody-manifest-sha256`. Zero or more run,
`instrument_validation`, or custody roots may be supplied only as the strict
cross-check described above. `--checkout-root` supplies the relative ordering
base for manifest generation/cross-check discovery; `--ledger` and `--head-pin`
override repository defaults.

Manifest generation requires `--emit-custody-manifest`, the authenticated
disposition table, `--checkout-root`, and all review roots. It prints one
pretty, key-sorted JSON manifest to stdout, prints the SHA-256 of those exact
bytes to stderr, and performs no ledger or pin write. The reviewed stdout bytes
and printed digest then become the required normal-mode inputs.

Dry-run creates no ledger or pin. Standard output is byte-stable NDJSON: one
canonical `receipt` record for every receipt, followed by one
`bootstrap-summary` containing both input digests, the receipt count, final
sequence/head, head-pin object, and exact pretty-printed head-pin file content.
The summary also carries `outcome`: `planned` for dry-run, `committed` for a
successful initial execution or idempotent durability confirmation, and
`committed_durability_uncertain` for the post-commit condition above.
`--execute` prints the same chain after the single atomic append, with
`executed=true`; it still does not write the pin.

CLI exit codes are distinct transaction outcomes: `0` means planned or
committed as reported in the summary; `2` means refusal or a failure before
the commit point; and `3` means the ledger committed but parent-directory
durability remains uncertain after the one retry. Exit `3` is not permission
to repeat the import as a new transaction: only the byte-exact idempotent
confirm invocation described above is permitted.
