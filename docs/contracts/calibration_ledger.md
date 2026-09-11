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
over the physical ledger head, the actual last receipt. Claim evaluation
requires their exact agreement and one immutable snapshot threaded through
every consumer.

## Derivation sessions for a new identity epoch

Status: **Ruled by cold gate 46 and its dated addendum 11 (2026-09-10); Ed
veto window open; LANDED in code.** Both facts hold at once: the mechanism
below is implemented and running, and Ed may still veto or amend the rules it
implements. This section and the generation-keyed clauses under [Historical
import](#historical-import) name shipped behaviour, not a plan. The code
sites, by symbol: `SESSION_KIND_DERIVATION` in
`joulewise/calibration_ledger.py` is the session kind a derivation session's
open receipt carries; `_is_derivation_kind_observation` in
`joulewise/calibration_bracketing.py` is the predicate that keeps those rows
out of every claim-bearing use; `prior_prefix_mode` is the key on the
registered generation row that selects which prefix fence that generation is
validated under; `scripts/validate_powermetrics_fiducial.py` takes
`--derivation-only` for the writer mode; and
`scripts/issue_calibration_acceptance_generation.py` is the issuer that
derives a successor acceptance candidate from a derivation corpus.

**Terms.** An **identity epoch** is the six-field vector {`os_build`,
`hardware_model`, `power_policy`, `sampling_interval_ms`,
`estimator_revision`, `pulse_protocol_id`} that an issued acceptance binds;
any field changing makes that acceptance stale (D-102 clause 2). An
**acceptance** is the issued artifact whose corpus statistics set the two
thresholds a later capture is judged against: the *level screen*, the corpus
maximum, and the *bracket screen*, the corpus range. A **generation** is one
registered version of that artifact, carrying its own registered derivation
rules. An acceptance's **prior set** (`prior_observation_set`) is every ledger
observation through its cutoff receipt; its **corpus**
(`derivation_corpus`) is the subset of that prior set whose values the
statistics are computed from. A **session** is a ledger capability that
reserves several attempts under one open receipt while the committed head pin
stays where it is; a **slot** is one declared, ordered place for an attempt
inside a session. **Head-equals-pin** means the physical head, the actual
receipt count and last receipt digest, matches the committed head pin exactly.
A **derivation-only capture** is an observation taken to build a future
acceptance, never to license a measurement.

**The forcing problem.** When the identity epoch changes — a macOS build bump,
for instance — the issued acceptance goes stale by design, and every threshold
that exists belongs to the retired epoch. A new acceptance needs a corpus of
new-epoch observations, yet those observations have to be captured before any
acceptance of their own epoch exists to judge them. Derivation sessions are
how the ledger records that new-epoch corpus without letting any of it
license a measurement.

**Why one session, not repeated standalone reservations.** A standalone
reservation refuses `RESERVATION_HEAD_MISMATCH` unless the physical head
equals the committed pin. One observation writes two receipts, a reservation
then a finalization, so after the first standalone capture of a night the head
sits two receipts past the pin and the next reservation refuses. Advancing the
pin is desk work under Git review and never runs inside an agent-free window.
A session removes the obstacle without weakening it: head-equals-pin is
checked once, when the session's open receipt is appended, and deliberately
not re-checked while that session's already-reserved slots are claimed and
finalized.

**Session kinds.** A `bracket`-kind session reserves the two endpoints (`pre`,
`post`) around one measured window. A `derivation`-kind session reserves N
declared slots — N fixed in the capture registration before any data exists —
for one derivation night. A bracket session records no `session_kind` and no
`declared_slots`; the absence of both fields IS the bracket kind, which is why
every receipt written before derivation kinds existed reads back unchanged. An
explicit `session_kind: "bracket"` in an open receipt refuses, so one session
shape has exactly one byte representation. A derivation session records both
fields. That encoding rule binds receipts only: the reservation tool run
without `--execute` — a dry run, which validates the inputs and writes nothing
— prints a JSON summary rather than a receipt, and that summary reports
`session_kind` and `declared_slots` explicitly for both kinds. A derivation
session opens at head-equals-pin; its slots are claimed and finalized in
declared order; no receipt belonging to another session may sit in the
reserved tail; and at most one session is open at a time.
Derivation-only capture requires a derivation-kind slot, so a standalone
attempt (one reserved directly against the pin, outside any session) and a
bracket-kind slot both refuse. The session closes when its last declared slot
finalizes, or when `abort_calibration_session` closes it with reason
`window_exhausted` because the window ran out first. Slots already finalized
remain observations; slots never reached are recorded unused, never compressed
or replaced. The night commits nothing to Git. The desk reviews the terminal
head-pin candidate the closed session emits and commits it before the next
session opens.

**Recovery finalizes a declared slot, never a free string.** When a crash
leaves a claimed slot unfinalized, the desk finishes it with the recovery
tool, naming the slot in a `--slot` argument. Slot names are no longer the
fixed pair `pre`/`post`, so the tool cannot enumerate the legal values in its
own argument parser; it reads the ordered list the session's open receipt
declared and refuses any `--slot` outside that list with
`RESERVED_SLOT_MISMATCH` (reason `slot_not_declared`), naming the slot given
and the declared list. A mistyped or invented slot name therefore cannot
finalize a place the session never reserved.

**Claim consumers refuse while a session is open.** From the open receipt
until that terminal pin is committed, the physical head is ahead of the
committed pin. Claim evaluation requires their exact agreement, so every claim
consumer refuses for the duration of the derivation night. That refusal is the
design, not a fault to be worked around.

**Derivation rows are non-claim-bearing, and never bracket endpoints.** A
derivation row carries no claim authority until an issued successor names it
in that successor's prior set and corpus. Even then it only derives
thresholds: it can never serve as a bracket endpoint, before or after
issuance. Two sites enforce this and must move together. Candidate discovery
skips derivation-kind sessions, and so does the `registered_valid` universe —
the complete enumeration of valid, non-import, pipeline-clean observations
that are either standalone or in a finalized session. A caller's supplied
candidate set must equal that universe exactly or evaluation refuses
`calibration_ledger_off_ledger_artifact`; this anti-withholding equality is
what stops a caller narrowing the universe to a favourable subset, and it is
why skipping at one site only is a defect rather than a partial fix.
Derivation rows are also a permanent obligation: once the successor issues,
its prior set must keep equalling the ledger prefix at its cutoff, so every
derivation row must stay in the ledger carrying the attempt ID, content ID,
classification disposition, epoch, and session ID that the prefix matcher
compares, for as long as that acceptance is consumed. The custody manifest is therefore pinned
and backed up before the issuance transaction. The successor acceptance judges
only ordinary captures taken after it. D-102 clause 2 stands unchanged: a
trigger observation is judged under the PRIOR artifact, never under a
threshold that incorporates that observation. Nothing in this section licenses
a measurement window or weakens a physics or evidence refusal (D-161).

**The issuer refuses a candidate whose registration does not match the machine
or the file.** Three fences are installed in the issuer,
`scripts/issue_calibration_acceptance_generation.py`, on its
`prepare-candidate` subcommand, so a mismatch stops the run before any corpus
statistic is computed rather than being caught in review afterwards.

- **Epoch match.** `prepare-candidate` refuses when the pre-registration's
  recorded `os_build` differs from the registration's target identity epoch,
  or when any registration row's recorded T1 bindings carry a
  `/usr/bin/powermetrics` SHA-256 other than the pre-registered one (the
  sampler digest is a T1 binding, not one of the six identity-epoch fields,
  so it is checked on every row rather than once). A machine
  that has moved off the declared epoch since the text was written would
  otherwise contribute rows to a corpus the registration never governed.
- **Registration shape.** It refuses when the registration is not exactly
  three sessions of twelve declared slots — the shape the pre-registration
  fixes before capture — unless a written ruling names the departure. A
  campaign that quietly ran a fourth night, or nights of a different slot
  count, is a different experiment from the pre-registered one, and the
  corpus size alone cannot reveal the substitution.
- **File identity.** It refuses when the SHA-256 of the pre-registration file
  it was handed differs from the digest the caller passes as
  `--preregistration-sha256`, so the authority the candidate cites is the
  text the caller meant, byte for byte, rather than whatever now sits at that
  path.

These three fences are installed on the issuer's `prepare-candidate`
subcommand, whose flags are `--preregistration` (the file), `--preregistration-sha256`
(its pinned digest), `--registration-session-id` (repeated, one per night), and the
two written-ruling escapes `--nights-ruling` and `--slot-count-ruling`; the
`check` subcommand's optional `--preregistration` compares the machine's
sampler-binary digest against the pre-registered one and leaves the watch
output byte-identical when the flag is absent.

## Historical import

Historical import is the one genesis-only exception that registers already
captured, hash-authenticated observations. It is not a second writer or an
ordinary capture route. A new identity epoch is served instead by the live
derivation sessions described above, never by a second historical import.
Version 1 has the following fixed decisions.

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
at the cutoff the artifact itself declares in `ledger_cutoff`, member for
member. A prior-set row carries four per-row bindings — attempt ID, content
ID, classification disposition, and identity epoch — and a generation
registered `import_only` refuses a row carrying any fifth key. A content ID is
the canonical hash derived from an observation's manifest and
instrument-evidence byte hashes, so it names the same observation from any
custody path.

Which rows that prefix may contain is a per-generation registration, not a
global rule (ruled 2026-09-10, Ed veto window open; landed as the
`prior_prefix_mode` key that `_prior_set_matches_import_cutoff_prefix` in
`joulewise/calibration_bracketing.py` reads off the registered generation row;
see [Derivation sessions for a new identity
epoch](#derivation-sessions-for-a-new-identity-epoch)). A
generation registered `prior_prefix_mode: import_only` keeps the genesis fence
exactly as written above — any live row in its prefix refuses — and that is
how generations r3 through r6 keep validating byte-identically. Only a
generation registered `prior_prefix_mode: import_plus_live` may hold finalized
live observations carrying content IDs, including the finalized slots of a
session that an abort closed. A pending attempt, or an `abandoned` one
(classified `unresolved`), refuses in either mode, as does any omission,
addition, duplicate, or mismatched binding.

A generation registered `import_plus_live` carries a FIFTH per-row binding,
`session_id`, compared against the ledger row's `bracket_session_id`; the
session it names must be derivation-kind. The reason is that a registration
has to be ledger-bound rather than self-asserted. The purity and completeness
checks below both range over "rows of this registration", and without this
binding the artifact would be the only thing saying which rows those are: it
could name a convenient subset, or disown a row the ledger recorded, and the
check would be judging the artifact against the artifact's own claim. Binding
each row to the ledger's recorded session is what keeps D-102 clause 2's rule
— nothing judges itself — true of registration membership as well as of
thresholds. Generations registered `import_only` keep the exact four-key row
shape and refuse when a `session_id` key appears, so no historical generation
changes. (Ruled 2026-09-10, Ed veto window open; landed. On the validator
side, `_prior_set_matches_import_cutoff_prefix` in
`joulewise/calibration_bracketing.py` appends the row's `session_id` to the
four expected bindings only when the mode is `import_plus_live`, compares it
against the ledger observation's `bracket_session_id`, and separately requires
every id in the row's `registration_session_ids` to resolve to a session whose
kind is `SESSION_KIND_DERIVATION`. On the issuer side,
`scripts/issue_calibration_acceptance_generation.py` writes
`prior_prefix_mode: import_plus_live` and `registration_session_ids` onto the
generation row it emits.)

Two EXPECTED numbers are registered per generation for the same reason:
`prior_observation_count` and `cutoff_sequence` (the genesis generation
registers 38 and 76). The cutoff itself is always the one the artifact
declares in `ledger_cutoff`; the registered numbers are what that declaration
must agree with. An all-import prefix holds exactly two receipts per
observation, a reservation and a finalization, so its cutoff sequence is twice
its observation count; a prefix that also holds a session's open and closing
receipts breaks that arithmetic, so neither number may be recomputed from a
literal. The generation likewise registers the epoch identifiers it permits
(`epoch_catalog_ids`) rather than relying on the single literal `d079_epoch`.

The generation also registers, under `screen_rule`, the NAME of the rule its
bracket screen was derived under. Two names are registered.
`range_equals_screen` is the rule the six issued generations were derived
under: the bracket screen IS the corpus range quantized to 0.000001 s under
ROUND_HALF_EVEN (ties go to the even final digit).
`floored_range_envelope_screen` is the D-125 envelope rule: that same
quantized range raised to a floor, so the check is
`screen == max(quantized range, floor)`, where the floor is
`D125_SCREEN_FLOOR_S` = 0.010818 s, the screen of the n = 19 genesis corpus.
The floor exists so no later lineage can characterise the instrument against
a looser screen than the first one it was characterised against.
`_registered_generation_row_is_complete` and the operative recomputation in
`joulewise/calibration_bracketing.py` both dispatch on the registered name,
and an unregistered name refuses rather than defaulting to either rule.

The name describes the PRE-REGISTERED RULE, never the branch the data took: a
generation derived under the envelope registers
`floored_range_envelope_screen` whether the range exceeded the floor or the
floor bound the screen. Naming it by the realized branch would make the
registered rule a function of the data, which is exactly what registering a
rule before capture exists to prevent — and it would misfile the ordinary
case, because a corpus at the n = 19 size floor has a range just BELOW
0.010818 s and takes the floor arm. A generation registered
`floored_range_envelope_screen` must additionally carry the `d125_ruling`
reference that authorised the envelope; the six issued rows predate the
envelope, carry no such reference, and are unaffected.

For `import_plus_live` two further checks apply, and together they are the
corpus-membership fence. Purity: every corpus member's ledger row carries the
target epoch. Completeness: every prior-set row that is valid, carries the
target epoch, and belongs to a session of this registration is either a corpus
member or is listed in `derivation_notes.excluded_members` with a registered
mechanism reason. A valid same-epoch row outside the registration refuses
issuance rather than being quietly absorbed. The one registered exclusion
mechanism today is `affine_clock_fit_empty`, the anchor-v3 replay result
meaning no feasible affine clock fit exists for that capture. An exclusion
entry carries `member_id`, `manifest_sha256`, and
`instrument_evidence_sha256` and no content ID, so its prior-set row is
matched by the content ID derived from those two hashes. The
predecessor-shaped analogue in the r6 artifact is
`excluded_predecessor_members`; its bytes and its validation rules do not
change. Membership is never trimmed by the observed bound values themselves:
an outcome-based exclusion would fit the new screen to the old one.

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

For the genesis D-079 generation the acceptance consumer recognizes two
exact-byte roles. The retained genesis test fixture uses schema
`joulewise.calibration_acceptance_bound.v2.fixture.v1`, role
`schema_fixture_unissued`, and file SHA-256
`9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb`.
It remains useful only to pre-issuance tests and production evaluation always
refuses it. The deterministic issued document uses schema
`joulewise.calibration_acceptance_bound.v2`, role `issued`, and exact emitted
file SHA-256
`316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`.
For that generation no other role, schema, or file bytes are accepted, even
when the internal whole-core digest is self-consistent. A later generation
authenticates against its own registered byte pin and its own registered
derivation rules; registering a successor never rewrites a predecessor's pin
or its recorded bytes.

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
4. `prior_observation_set` must equal the complete observation prefix
   through the artifact's declared `ledger_cutoff`, member for member by
   attempt ID, path-independent content ID, classification disposition, and
   identity epoch, plus, for a generation registered `import_plus_live`, the
   row's `session_id` against the ledger row's `bracket_session_id`. A
   generation registered `import_only` refuses every non-import row; one
   registered `import_plus_live` admits only the finalized live rows
   described above. Any omission, addition, duplicate, unresolved attempt,
   or epoch outside the generation's registered catalog refuses. A
   generation deriving a corpus from live rows must also pass the purity and
   completeness checks of the corpus-membership fence.

The artifact's stored `issuance.claim_eligible=true` is necessary but not
sufficient. The evaluation result reports effective `claim_eligible=true`
only after all four checks pass and a non-genesis ledger head is present.
Before that point it reports false. The genesis-issued D-079 state is
sequence 76 at head
`08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`,
with 38 import-marked, content-distinct observations: 30 valid, 2
systematic-invalid, and 6 ordinary-invalid. The threshold-producing
`derivation_corpus` remains n=19. The issued whole-core
`derivation_sha256` is
`4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`.
That 76-row prefix, the r6 artifact, and every historical generation keep
validating byte-identically under their own registered rules. A prospective
successor declares a `ledger_cutoff` at the authenticated head after its last
derivation row, because every corpus member's content ID must lie inside the
prior set and the prior set stops at the cutoff; it therefore names the
complete history through that cutoff, not only the retained corpus. Until
that successor issues, its derivation rows supply no claim authority; after
it issues they still cannot become bracket endpoints.

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
