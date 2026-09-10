# Calibration observation ledger

The canonical calibration ledger is an immutable SHA-256 receipt chain under
`joulewise.calibration_observation_ledger.v1`. D-109 R1 and R2 are controlling.
The ledger closes workflow omission, unregistered evidence, and rollback or
stale-head consumption; it does not defend against a malicious trusted writer
or an authority that rewrites both Git and the complete ledger history.

Live capture remains reservation-first: a `reservation` receipt with
`disposition=pending` precedes hardware state, and exactly one `finalization`
receipt closes that attempt. The repository-committed **head pin**, a file
naming the trusted receipt count and last digest, is independent authority
over the physical ledger head (the actual last receipt). Claim evaluation requires their exact
agreement and one immutable snapshot threaded through every consumer.

## Derivation sessions and epoch bootstrap

An **identity epoch** is the six-field vector {os_build, hardware_model,
power_policy, sampling_interval_ms, estimator_revision, pulse_protocol_id}.
An **acceptance** is the issued artifact whose calibration statistics govern
measurement admission; a **generation** is one registered version of it.
Its **prior set** (`prior_observation_set`) lists every ledger observation
through its cutoff receipt. Its **corpus** (`derivation_corpus`) is the subset
used to compute those statistics. **Derivation-only** means capture to build
a future acceptance, never to license a measurement.

A **session** is a ledger capability reserving several attempts at once while
the committed head pin stays fixed. A **slot** is one declared, ordered place
for an attempt in that session. An ordinary `bracket`-kind session reserves
the `pre` and `post` endpoints around a measured window. A `derivation`-kind
session reserves N declared slots for one registered derivation night. It
opens only at head-equals-pin, fills unused slots in declared order, and
permits no foreign extension or second open session. Derivation-only capture
requires a derivation-kind slot; standalone and bracket-kind use refuse.
The last declared slot's finalization closes the session. If the window ends
first, `abort_calibration_session` with reason `window_exhausted` closes it;
already finalized slots remain observations and unused slots are not replaced.
The night never commits Git. The terminal pin candidate is reviewed and
committed at the desk before the next session opens. Claim consumers continue
to refuse during the uncommitted derivation extension.

Bootstrap observations of the new epoch remain non-claim-bearing until an
issued successor names them in its prior set and eligible corpus. Even then,
they serve only to derive prospective acceptance: they are **never bracket
endpoints**, including after issuance. Both candidate discovery and the
registered-valid endpoint universe skip derivation-kind sessions, while their
evidence remains in permanent authenticated ledger custody. The successor
judges only subsequent ordinary captures. D-102 clause 2 still judges a trigger
observation under the PRIOR artifact, never under a threshold incorporating
that observation. Nothing here licenses G2-a or weakens a physics or evidence
refusal (D-161).

## Historical import

Historical import is the one genesis-only exception that registers already
captured, hash-authenticated observations. It is not a second writer or an
ordinary capture route. New-epoch bootstrap uses the live derivation sessions
above, not another historical import. Version 1 has the following fixed decisions.

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
   this ordering/custody contract into every receipt digest. Every reservation
   also carries `historical_import_input_sha256`, whose exact
   `disposition_table` and `custody_manifest` digests bind the authenticated
   raw input bytes into the chain. The terminal digest therefore transitively
   binds the complete ordered member set and the exact input-digest pair;
   semantically identical reserialization produces a different chain.
   Omitting a summary keeps the existing two-transition attempt model and
   yields sequence `2 * member_count`.

Consumers must not treat an import-marked finalization as a fresh post-cutoff
observation or bracket endpoint. Production candidate discovery checks the
marker directly, and prospective trigger subtraction uses
`CalibrationLedgerSnapshot.post_cutoff_live_observations()`. At consumption,
the acceptance artifact's prior set must exactly equal the observation prefix
at its generation-registered cutoff (attempt ID, content ID, classification
disposition, and epoch). A content ID is the canonical hash derived from the
manifest and instrument-evidence byte hashes, independent of custody path.
The registered `prior_prefix_mode: import_only` keeps the import-only fence
for historical generations, including r3–r6; any live row there refuses.
Only a generation registered `prior_prefix_mode: import_plus_live` may include
finalized live observations with content IDs, including finalized slots of
abort-closed sessions. Pending or `abandoned` (classified `unresolved`)
attempts refuse; omission, addition, duplicate, or mismatched binding also
refuses. The generation registers its epoch catalog, prior-observation count
and cutoff sequence; a mixed prefix does not use the historical two-receipts-
per-observation shortcut.

For `import_plus_live`, every corpus member must carry the target epoch and
belong to a session of this registration. Every valid target-epoch prior-set
observation of that registration must be a member or have a registered
mechanism exclusion in `derivation_notes.excluded_members`; a valid
same-epoch observation outside the registration refuses issuance rather than
being absorbed. The currently registered replay exclusion is
`affine_clock_fit_empty` (no feasible affine clock fit). Exclusion entries
carry `member_id`, `manifest_sha256`, and `instrument_evidence_sha256`; prior
rows are matched by the content ID derived from those two hashes. The r6
analogue is `excluded_predecessor_members`; its bytes and historical validation
rules do not change. Membership is never trimmed by observed bound values.

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
resume against an old, unlinked ledger inode. Both append and bootstrap open
the lock through the same audited helper with `O_NOFOLLOW|O_CREAT|O_RDWR`, then
`fstat` the descriptor and refuse unless it is a regular file with link count
one. If the ledger exists, the lock's `(st_dev, st_ino)` must also differ from
the ledger's. Symlinked locks and hardlink aliases therefore fail closed.

Execution prepares and canonicalizes the entire chain in memory, obtains the
stable lock, rechecks the genesis pin and physical ledger by path, and
immediately re-opens all five artifacts for every member through contained
no-follow descriptors. Every hash must still equal the prepared plan. It then
writes and fsyncs the complete payload to a sibling staging file and atomically
replaces the empty ledger. Until replacement, readers see only genesis; after
replacement, readers see only the complete chain. A write, staging-file fsync,
reauthentication, or replacement failure leaves zero reader-visible receipts.
Process death mid-stage likewise leaves a retryable genesis ledger.

`os.replace` is the transaction commit point. After replacement, publication
performs exactly one parent-directory fsync on the held descriptor. Any error
makes the chain **committed with durability uncertain**;
it is never reported as an atomic-append failure. The CLI still emits every
canonical receipt and the full summary, whose machine-readable `outcome` is
`committed_durability_uncertain`, then exits `3`. The operator must rerun the
identical `--execute` invocation before updating the head pin.

**Amended 2026-08-09 (fail-closed durability correction):** the former
retry-then-trust promise was unsound because a later successful fsync cannot
prove that the failed durability decision persisted the committed directory
entry. Initial publication is therefore single-shot and performs no redundant
second directory sync. The idempotent confirmation path opens the directory
fresh and also makes exactly one fsync attempt; any error remains uncertain
and recovery belongs to another byte-exact external invocation.

While the committed pin remains genesis, such a rerun recomputes the complete
plan from the authenticated table, manifest, and custody bytes under the same
rules. Under the stable lock, it compares the physical ledger byte-for-byte
with `plan.ledger_bytes`; matching bytes enter the idempotent confirm path,
which re-fsyncs the parent directory without replacing or appending and emits
the same receipt chain and head/input-digest summary with `outcome=committed`.
Because the input-digest pair is inside the reservation bytes, reserializing
either authenticated input makes this byte comparison fail. Any other nonempty
ledger refuses with the ordinary empty-ledger error. Once the reviewed head
pin is updated away from genesis, a further invocation refuses at the normal
genesis-pin gate.

The importer never writes the head pin. After execution, claim evaluation is
expected to refuse until the lead has reviewed and committed the exact printed
pin, preserving D-109 R1.4's anti-rollback boundary.

## Issued D-079 acceptance artifact

The historical genesis issuance below records two exact-byte roles. The retained genesis
test fixture uses schema
`joulewise.calibration_acceptance_bound.v2.fixture.v1`, role
`schema_fixture_unissued`, and file SHA-256
`9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb`.
It remains useful only to pre-issuance tests and production evaluation always
refuses it. The deterministic issued document uses schema
`joulewise.calibration_acceptance_bound.v2`, role `issued`, and exact emitted
file SHA-256
`316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`.
For this historical generation no other role, schema, or file bytes are
accepted, even when its internal whole-core digest is self-consistent.
Later issued generations authenticate against their own registered byte pins
and derivation rules; registering a successor never rewrites a historical pin.

Issued-artifact authentication is conjunctive and fail-closed:

1. The file must match the issued byte pin and its `derivation_sha256` must be
   the canonical SHA-256 of every top-level key except `derivation_sha256`.
2. The one threaded `CalibrationLedgerSnapshot` must have authenticated the
   physical ledger against the repository-committed current head pin. Missing
   ledger bytes, an uncommitted pin, rollback, a fork, or any physical/pinned
   head mismatch refuses before the artifact can become claim-eligible.
3. The artifact cutoff is passed to the snapshot loader as its baseline. The
   exact digest must occur at the exact sequence in that authenticated chain,
   and the evaluator rechecks the snapshot's baseline fields against the
   artifact. A later committed live extension is permitted by D-109 R1.4; it
   does not change the historical issuance cutoff.
4. `prior_observation_set` must equal the complete generation-registered observation
   prefix through the cutoff, member for member by attempt ID, path-independent
   content ID, classification disposition, and identity epoch. `import_only`
   refuses non-import rows; `import_plus_live` admits only the finalized live
   extension described above. Any omission, addition, duplicate, unresolved
   attempt, or epoch-catalog mismatch refuses. Corpus purity and registration
   completeness are additional requirements for the prospective generation.

The artifact's stored `issuance.claim_eligible=true` is necessary but not
sufficient. The evaluation result reports effective `claim_eligible=true`
only after all four checks pass and a non-genesis ledger head is present.
Before that point it reports false. The historical genesis-issued D-079 state is sequence 76 at
head
`08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`,
with 38 import-marked, content-distinct observations: 30 valid, 2
systematic-invalid, and 6 ordinary-invalid. The threshold-producing
`derivation_corpus` remains n=19. The issued whole-core
`derivation_sha256` is
`4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`.
That 76-row prefix, the r6 artifact and every historical generation remain
byte-identical. A prospective successor advances its cutoff to the
authenticated head after the last bootstrap row and names the complete
history through that cutoff, not just the retained corpus. Until issuance,
bootstrap rows supply no claim authority; after issuance they still cannot
become bracket endpoints.

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

Issued-artifact preparation is a separate explicit mode over the same
authenticated `HistoricalImportPlan`. `--prepare-issued-artifact` adds one
`issued-acceptance-artifact` NDJSON record before the final bootstrap summary
and performs no artifact write. The record contains the full artifact, its
whole-core derivation digest, the exact pretty-printed file content, and the
file-byte digest. `--acceptance-artifact` selects the current exact-byte
fixture or already-issued template; its default is
`configs/calibration/calibration_acceptance_d079_v2.json`.

The issuance source is authenticated against the exact byte pin selected by
its role before any issued document is built. Structural validity or a
self-consistent recomputed `derivation_sha256` is not source authority. The
builder normalizes from that authenticated pinned document, rather than from
caller mapping insertion order, and uses the frozen schema-field order and
fixed JSON separators. Consequently a top-level key-order variant of the same
authenticated mapping produces byte-identical issued content at the reviewed
`316113960c…` pin.

`--emit-issued-artifact [PATH]` is the only artifact-writing switch. Omitting
`PATH` selects that default acceptance path. The emitted observations are
copied in ledger-prefix order only from
`historical-import-v1-finalization` receipts; the tool does not rediscover or
reclassify the corpus. It refuses unless the plan is exactly the ruled
76-receipt head and 30/2/6 inventory, preserves the n=19 derivation corpus,
sets the issued role/status/eligibility state, and recomputes the whole-core
digest. This switch never writes the ledger head pin. A dry-run without the
switch therefore remains fully read-only, including the acceptance artifact.

Emission never truncates the destination in place. It writes the complete
issued bytes to a sibling staging file, flushes and fsyncs that file, and then
uses `os.replace` to atomically publish it. A staging write or fsync failure
therefore leaves the prior destination bytes intact, or leaves the destination
absent when it did not previously exist.

When issuance preparation or emission is combined with `--execute`, ordering
is validate then commit. Before the irreversible ledger call, the tool
authenticates the source, builds and structurally validates the artifact,
recomputes its whole-core digest, verifies its cutoff equals the prepared
import head, verifies its prior set exactly equals the complete import prefix,
checks the final issued byte pin, and completes any requested atomic artifact
emission. Any failure in those steps exits `2` without creating or writing the
ledger. Only then may `bootstrap_historical_import(execute=True)` run; no
artifact preparation or artifact write occurs after that call. If the ledger
commit instead reaches `committed_durability_uncertain`, the already-prepared
artifact is included in the full receipt/summary output and the CLI preserves
exit `3`.

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
the commit point; and `3` means the ledger committed but the single
parent-directory durability decision failed. Exit `3` is not permission
to repeat the import as a new transaction: only the byte-exact idempotent
confirm invocation described above is permitted.
