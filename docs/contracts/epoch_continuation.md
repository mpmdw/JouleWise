# Calibration epoch continuation

A **calibration acceptance** is the issued, byte-pinned artifact supplying the
screens used to judge calibration captures and measurement brackets. A
**screen** is a numerical comparator. The **level screen** limits the bound of
an individual calibration capture. The **bracket screen** limits the spread
between bounds, where spread means maximum minus minimum. **Operatives** are
the precise decimal comparators registered for an acceptance, as distinct from
its raw corpus statistics or rounded presentation values.

An **identity epoch** is the six-field vector `os_build`, `hardware_model`,
`power_policy`, `sampling_interval_ms`, `estimator_revision`, and
`pulse_protocol_id`. An **epoch continuation** is a separate issued artifact
authorizing the same acceptance to judge an additional identity epoch after an
equivalence night passes the rule below. A **judged epoch** is either the
acceptance's original epoch or an authenticated continued epoch.

This implements the PASS route of [directive issue 316](https://github.com/mpmdw/JouleWise/issues/316)
and its dated D-102 addendum. It creates no acceptance generation and changes
no operative, derivation corpus, historical prior set, acceptance file hash,
derivation hash, or campaign pin. The `EPOCH_CONTINUATION_REGISTRY` in
`joulewise/calibration_bracketing.py` starts empty. Issuance and registration
belong to a later governed transaction; generating a candidate grants no
authority to capture or measure.

## Evidence and the fixed equivalence rule

A **derivation session** is the ledger reservation of a calibration night,
with an ordered list of declared slots. A slot is one reserved capture
opportunity. A session is **terminal** when finalized or aborted. A finalized
slot has a ledger observation, an attempt ID identifying the attempt, and a
content ID derived from the hashes of its `manifest.json` and
`instrument_evidence.json` primary files. The session must declare twelve
slots, including opportunities that were not used before an abort.

The issuer loads a committed, authenticated ledger snapshot in `read_replay`
mode with custody verification disabled at that loading step. It then reads
and authenticates the two primary files of **every finalized slot**, using
the existing acceptance issuer's `_read_member_evidence`. It recomputes each
content ID and checks exact agreement between the stored `b_fiducial_s`
decimal lexeme and the ledger's `exact_bound_lexeme_s`. A **lexeme** is the
original decimal text; numerically equal spellings are not interchangeable
for this check. Primary-byte, content-ID, and lexeme disagreement refuse the
whole operation.

If any finalized row is `systematic-invalid`, preparation refuses with
`night_contains_systematic_failure` naming its slot, exits 3, and writes
nothing. Such a continuation would be stale on arrival: the desk reports the
failure to Ed under D-102's systematic-failure trigger.

**Anchor-v3 resolution** is the outcome returned by the acceptance issuer's
`anchor_v3_replay_outcome` from the authenticated, stored clock-anchor
record. This replays the recorded result; it does not perform a new raw-trace
fit. A **retained value** is a finalized observation classified `valid` whose
anchor-v3 result is resolved. Every retained observation must carry the same
identity epoch, differing from the acceptance's original epoch in at least
one field. Unresolved and invalid observations are recorded and excluded from
the retained statistics; their exclusion is never based on the magnitude of
a bound. The envelope must hold over every disclosed valid bound, resolved
or not; `m` counts the resolved. Invalid rows do not enter the envelope.
Every `valid` row with `anchor_v3_resolved: false` must name a non-empty
`anchor_v3_detail`; null or empty detail refuses with
`slots.anchor_v3_detail_required`. The reader enforces this audit trail but
cannot replay anchor resolution from the ledger alone; the issuer owns that
primary-evidence check.

The shared `envelope_holds_over_all_valid` check applies the level screen to
each disclosed `valid` bound and the bracket screen to the maximum minus
minimum of **all** such bounds, including unresolved rows. Every valid row
must therefore supply a finite, nonnegative decimal bound; a null bound refuses
with `slots.<slot>.b_fiducial_s_required_for_valid_row` in both preparation and
loading. The check has no minimum count; the empty valid set satisfies it vacuously. The loader cannot
replay anchor resolution, so resolution remains file-asserted. Without this
independent envelope check, re-labelling an over-screen row as unresolved
could turn a FAIL into a PASS. Resolution can now reduce `m` but cannot
produce a FAIL→PASS flip. A hand-written, registry-pinned file can still promote
an inside-envelope unresolved row to resolved, raising `m` and turning an
INCONCLUSIVE night into a PASS; no published number can change, and the tool
prevents that promotion by deriving resolution from authenticated primary bytes.
The loader cannot replay those bytes, so owner registration review remains the
boundary for that file-asserted resolution claim.

If the all-valid envelope fails, preparation unconditionally refuses with
`unresolved_valid_row_exceeds_envelope`, names the unresolved slots (or says
`none (all valid rows resolved)`), exits 3, and writes nothing; the desk reports
it to Ed for a written ruling. This refusal also applies below the retained-count
minimum. The loader requires the all-valid envelope before recomputing retained statistics
and refuses a violating continuation with detail
`unresolved_valid_row_exceeds_envelope`, with or without a ledger snapshot.
The retained-statistics function still computes FAIL and INCONCLUSIVE as below;
the prepare envelope gate now refuses every screen violation before that
calculation.

Let `m` be the number of retained values. Let `L` be the acceptance's registered
`preflight_level_screen_s`, and `S` its registered `bracket_screen_s`. Both
must equal their corresponding entries in
`decimal_derivation.ratified_operatives`. The shared decimal calculation is:

1. If `m < 6`, the verdict is `inconclusive`.
2. Otherwise, the verdict is `pass` exactly when every retained value is
   `<= L` and `max(values) - min(values) <= S`.
3. Any other result is `fail`.

Both equalities pass. Calculations preserve decimal text and use enough
working precision to subtract its represented places without rounding. An
empty retained set has null extrema and range. For a nonempty inconclusive
set the continuation tool reports descriptive extrema and range but does not
grant a PASS. The S9 witness format reports null extrema when inconclusive;
the witness cross-check preserves that format's distinction.

## Artifact schema and authentication

The JSON object has these fields. All hashes are lowercase SHA-256 hex. Its
schema is `joulewise.calibration_epoch_continuation.v1`.

| Field | Meaning |
| --- | --- |
| `schema_version` | The schema identifier above. |
| `continuation_id` | Opaque stable ID used as the continuation registry key. The preparer prefixes `epoch-continuation-` to the canonical hash of the independently derived record before adding this ID, the candidate marker, and the derivation hash. |
| `decision_ids` | Exactly `["D-102"]`. |
| `acceptance_id` | The unchanged acceptance being continued. |
| `acceptance_file_sha256` | Its registered exact-file hash. |
| `acceptance_derivation_sha256` | Its unchanged derivation hash. |
| `continued_identity_epoch` | Exactly the six identity fields, with the same field types as the original epoch. |
| `ruling` | `channel: "directive issue 316"`, an ISO `d102_addendum_date`, and `authority: "owner"`. Preparation records the supplied date; it does not enact a ruling. |
| `rule` | Decimal strings `level_screen_s`, `operative_bracket_screen_s`; integer `m_minimum: 6`; `source: "ratified_operatives of the acceptance"`. |
| `evidence.ledger` | `ledger_schema`, `head_sequence`, and `head_digest` of the authenticated preparation snapshot. |
| `evidence.session_id` | The adjudicated derivation session. |
| `evidence.session_kind` | Exactly `derivation`. |
| `evidence.session_state` | `finalized` or `aborted`. |
| `evidence.declared_slots` | The ordered twelve slot names, not just their count. |
| `evidence.slots` | Twelve records in declared order, detailed below. |
| `evidence.acknowledged_attempt_ids` | Exactly the finalized attempts, in declared order, including invalid or unresolved attempts. |
| `evidence.m` | Number of valid, resolved values retained. |
| `evidence.retained_min_s`, `retained_max_s`, `retained_range_s` | Decimal-text extrema and their difference. |
| `verdict` | Only `pass` is accepted for issuance. |
| `candidate_not_issued` | Present on candidates; its presence, even with value `false`, forbids loading as issued. |
| `derivation_sha256` | Canonical SHA-256 of every other top-level key, including any candidate marker. |

Each slot record contains exactly `slot`, `attempt_id`, `content_id`,
`manifest_sha256`, `instrument_evidence_sha256`, `disposition`,
`anchor_v3_resolved`, `anchor_v3_detail`, and `b_fiducial_s`. Extra or missing
keys refuse with `slots.keys`, including on unfinalized records. An unfinalized
slot has null attempt ID, content ID, hashes and bound, and false resolution.
Its disposition is `window_exhausted` for an abort with that reason, otherwise
`no_row`. These labels describe absent captures; they are not ledger
classifications. Unfinalized slots enter neither retention nor acknowledgment.

Canonical hashing uses the acceptance's `_canonical_sha256` recipe: JSON with
sorted keys, separators `(',', ':')`, Unicode preserved, nonfinite numbers
forbidden, encoded as UTF-8. Removing a candidate marker therefore requires
recomputing the derivation hash before registering the issued file's byte
hash. Neither hash can be reused from the marked candidate.

`load_epoch_continuations(acceptance_artifact, ledger_snapshot)` returns only
valid continuations. Every registered entry supplies `path`, `relative_path`,
and `file_sha256`. Loading rejects unreadable or malformed JSON, duplicate
keys, wrong byte pins, any candidate marker, non-PASS verdicts, and a wrong
schema or derivation hash. It reauthenticates the supplied acceptance and
requires agreement on **all three** of acceptance ID, acceptance file hash,
and acceptance derivation hash. The continued epoch must differ from the
original. The rule, retained count, extrema, range and verdict must reproduce.

With a ledger snapshot, the reader refuses integrity failures with
`ledger_snapshot_invalid`. The only state reasons tolerated are enumerated in
`SNAPSHOT_STATE_REFUSALS`: `calibration_ledger_bracket_session_open` covers an
open bracket or derivation session; `calibration_ledger_head_mismatch` is tolerated
only when `is_governed_open_bracket_extension` proves the physical/pinned gap
belongs to one governed open session. An unproven head mismatch, custody failure,
uncommitted pin, malformed chain, pending attempt, or any unknown reason still
refuses. This tolerance lets a capture in flight cross-check an earlier terminal
continuation; it never licenses the continuation's own session to remain open.

The reader also requires the cited session to exist, have derivation kind, be terminal in the recorded state, and declare the
recorded slots. The snapshot cannot precede the recorded head sequence.
The file's finalized `(slot, attempt_id)` pairs must equal the session's
`finalized_slots` pairs, or it refuses with `ledger_finalized_slots_mismatch`.
A file slot marked unfinalized must be absent from that ledger index; hiding
a finalized row behind an unused-slot label refuses with
`hidden_finalized_row`. Every ledger observation belonging to the session
must also appear in the file, including invalid and unresolved rows; an
undisclosed observation refuses with `hidden_finalized_row` even if absent
from the session index. Every acknowledged attempt must be present in
the observation lookup with the same content ID, disposition, and bound
lexeme. Thus `m` cannot exceed the ledger session's valid-row count. Retained
attempts must carry the continued epoch. Additional ledger
observations remain eligible for future trigger evaluation; a continuation
never acknowledges an entire future epoch.

Invalid entries are ignored individually. Callers may collect named refusal
details through `refusal_details`. An `OSError` detail contains only its exception
class and the registry's `relative_path` (falling back to the file path relative
to the repository root); OS messages and absolute filenames never enter that
detail or the hashed capture artifacts that carry it. Bracket evaluation records
these as
`acceptance.continuation_refusals` only when non-empty, with reason
`calibration_epoch_continuation_invalid` and the precise failed field. The
field is absent otherwise, preserving stable receipt hashes and the
pre-continuation evaluation record when no continuation is registered. If no
judged epoch matches, freshness is stale and carries that reason; the existing
claim refusal `calibration_acceptance_bound_stale` remains the outer result.
A bad continuation does not revoke the acceptance's original epoch or another
valid continuation. The diagnostic is registered in the governing
[D-078 reason amendment](d078_reason_registry_amendment.md).

When `ledger_snapshot=None`, only the session cross-check is skipped; all file,
acceptance, schema, and arithmetic checks still run. A returned continuation
then says `ledger_cross_check: "skipped_no_ledger_snapshot"`; with a snapshot
it says `verified_terminal_derivation_session` only after all completeness and
row checks above hold. This weaker path is available
for identity-only preflight consumers that do not own a snapshot. Claim-time
bracket evaluation always requires a valid snapshot and never uses it.

The capture writer's ordinary and derivation-only preflight helpers accept a
ledger snapshot and pass it to `acceptance_judged_epochs`. The CLI loads its
custody-verified snapshot before identity preflight and records `ledger_snapshot`
for both ordinary and derivation-only captures. It reuses that snapshot for the
early slot-reservation check and reloads under the writer lease before capture.
Identity-only helper callers (G2-a vectors, derivation-night desk inputs, and the
historical import-time screen constant) have no snapshot and retain the explicitly
labelled `registry_pins_only` path.
The full `acceptance_preflight` and `screen_basis` artifact key lists and
authentication-basis labels have one home in the
[powermetrics artifact contract](powermetrics_fiducial.md#derivation-only-capture-for-a-new-identity-epoch).

Derivation-only captures record the same fields in `screen_basis`, alongside
the prior acceptance's original `epoch` and level screen. A planned epoch
equal to **any** judged epoch refuses with
`calibration_derivation_only_epoch_unchanged`, because the ordinary capture
screen already judges that epoch. Continued epochs are no longer new epochs
for this guard. G2-a vector generation delegates to the same ordinary
preflight and therefore applies the same registry-pins-only identity check.

## Freshness and prospective triggers

The **prospective triggers** are conditions in the unchanged acceptance that
require a new derivation when later evidence challenges it. The continued
acceptance applies the following four rules:

1. **Identity freshness.** The observed six-field vector must equal one judged
   epoch exactly. A continuation match reports `basis: "epoch_continuation"`,
   its ID and file hash, session ID, `m`, verdict, and ledger cross-check.
   `expected_identity_epoch` names the matched vector, so `stale_fields` is
   empty. Without a match, the existing stale refusal remains.
2. **Corpus doubling.** Count distinct valid contents separately for every
   judged epoch, including the acknowledged night's valid observations.
   Trigger when any one epoch reaches twice the acceptance's corpus size.
   Never sum across epochs.
3. **Range expansion.** A later valid observation from any judged epoch
   challenges the acceptance if its value is below the original corpus
   minimum or above its maximum. Exempt exactly the acknowledged attempt IDs
   of authenticated continuations.
4. **Systematic failure.** Every `systematic-invalid` observation from every
   judged epoch challenges the level screen, including the equivalence
   night's acknowledged rows. No acknowledgment exemption applies. Future
   derivation sessions participate too.

The exemption is asymmetric because the equivalence rule compared retained
values against the envelope; it never examined a systematic failure.
Acknowledgment therefore exempts range expansion only. D-102's
systematic-failure trigger keeps its say, and preparation refuses a night
containing such a failure rather than producing a continuation already stale
under that trigger. Acknowledged valid rows still count toward corpus doubling.

Protocol and estimator byte-change checks, custody, endpoint eligibility, the
unclassifiable-observation refusal, the trigger-name vocabulary, and all
operative arithmetic remain binding. A continuation never makes derivation
captures into measurement-bracket endpoints.

For a worked example, r6 has a corpus size of 17, an operative level screen
`0.032898493715362` seconds and operative bracket screen `0.009724` seconds.
Its raw corpus maximum is `0.03289849371536248`, minimum
`0.02317490442656863`, and range `0.00972358928879385` seconds. The operatives
are the comparators; their differing final decimal places are deliberate.

Suppose a twelve-slot night on 25G83 retains these hypothetical bounds, in
seconds: `0.020`, `0.021`, `0.022`, `0.023`, `0.024`, `0.025`, `0.026`,
`0.027`, `0.028`, `0.027`, `0.026`, `0.025`. Here `m=12`, maximum `0.028`,
minimum `0.020`, and range `0.008`. All values meet the level screen and the
range meets the bracket screen, so the night passes. Once its continuation
is issued and authenticated, a matching 25G83 identity is fresh. The low
`0.020` attempt does not immediately trigger range expansion because that
exact attempt was acknowledged under the equivalence rule.

If there are 30 valid 25F84 contents and these 12 valid 25G83 contents, neither
epoch reaches r6's doubling threshold of 34. Two ordinary 25G83 endpoint
captures bring the second count to 14, still below 34; pooling the epochs
would incorrectly stale the acceptance. Twenty more distinct valid 25G83
contents bring that epoch to 34 and trigger doubling. Independently, a new
ordinary 25G83 attempt at `0.020` triggers range expansion immediately, and a
new systematic-invalid attempt triggers systematic failure. The same applies
to attempts in a later derivation session. Only the specifically acknowledged
night is exempt from range expansion; systematic failures trigger even there.

## Commands and consumer census

`scripts/issue_epoch_continuation.py prepare-candidate` requires `--session-id`,
`--ledger`, `--head-pin`, `--acceptance`, `--repo-root`,
`--d102-addendum-date`, and `--out`. PASS writes a marked candidate and exits
0. INCONCLUSIVE prints the derived record and exits 5 without writing a
candidate. Envelope and integrity refusals exit 3 without writing a candidate.
Exit 4 remains the statistics FAIL mapping, but every screen violation now
hits the unconditional envelope refusal before that mapping. Output under any
resolved `configs/calibration` directory is forbidden. Existing output refuses
without `--force`. Repeating identical inputs produces identical bytes.

Optional `--equivalence-record` accepts an S9
`joulewise.epoch_equivalence_check.v1` witness. The issuer independently
reconstructs the session, slot outcomes, retained lexemes, count, extrema,
range, comparison operands and booleans, reference operatives and raw
statistics, and verdict. Any disagreement names the precise field and exits
3. The witness's acceptance path is provenance, not an authority or input
path. The witness never supplies a bound, comparator, or retention decision.
Recognized additional science fields, including a ledger head or return code,
are also cross-checked. Unknown fields refuse; only the explicitly identified
path and tool/publication provenance may be ignored.

`check --candidate PATH` uses the same authentication function as the loader,
refuses a marker or missing registry pin, and prints the judged epochs. With
`--ledger`, supply its `--head-pin` and `--repo-root` for the session check;
without a ledger the output explicitly labels the skipped cross-check.

The production identity-comparison census is:

| Consumer | Disposition |
| --- | --- |
| `calibration_bracketing.evaluate_calibration_bracket` | Uses judged epochs for freshness and all three identity-scoped evidence triggers. |
| `scripts/validate_powermetrics_fiducial._derive_preflight_systematic_screen_s` | Passes an optional ledger snapshot to `acceptance_judged_epochs`; the CLI supplies its custody-verified snapshot; identity-only callers omit it and explicitly skip the session cross-check. |
| The same writer's derivation-only branch | Refuses when the planned epoch is already judged; its screen basis lists all judged epochs. |
| `arm_readiness._issued_d079` | Checks an acceptance ID, not machine identity; unchanged r6 already routes as issued. No continuation comparison is needed. |
| `generate_g2a_probe_inputs._derive_live_vectors` | Delegates epoch preflight to the writer above; no independent acceptance-epoch comparison. Its later inventory comparison binds planned inputs to each other and remains unchanged. |
| `write_derivation_night_inputs._stale_identity_fields` | Delegates to the writer without a snapshot; an authenticated continued epoch is an ordinary night, so derivation-night inputs refuse. |
| `issue_calibration_acceptance_generation.check` | Desk-only historical epoch watch remains unchanged; it can report the original epoch mismatch after continuation. It authorizes no capture. |
| Ledger reservations, prior-set catalog purity and member bindings | Compare evidence to its own reserved or historical identity, rather than machine applicability to an acceptance. They remain exact and unchanged. |

An issued continuation and its registered byte pin remain requirements for
production continuation; the implementation itself grants no continued epoch.
