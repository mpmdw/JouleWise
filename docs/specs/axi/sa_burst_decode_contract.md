# AXI-SA burst-decode metric-semantics contract

Status: implementation-ready design; no implementation or live-evidence claim

Contract ID: `joulewise.axi_sa_burst_decode.v1`

Landing target: AXI-SA / S-A

Normative authorities: D-062, D-066, D-067, D-070; `docs/axi-handoff.md` §4 S-A
and §6; and the binding xhigh consult at
`docs/process_traces/2026-07-15-axi-xhigh-consult/response.md` §§1-2.

## 1. Scope and normative language

This document freezes the request-aware event, output, reducer, and
claim-admission contracts required before any JouleWise speculative-decode or
static-batch bundle may be created. It is a design document only. It makes no
claim that a runtime currently exposes the required hooks.

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT,
and MAY are normative.

The implementation MUST use these independent version axes:

| Axis | Frozen value for the new path | Compatibility meaning |
|---|---|---|
| This contract | `joulewise.axi_sa_burst_decode.v1` | Any semantic change to a frozen table or invariant requires a successor. |
| Config base schema | `0.1` | Remains `0.1`; AXI does not consume reserved config `0.2`. |
| Config extension | `joulewise.axi_decode_config.v1` | Present only on AXI request/burst configs and included in normalized `config.json` identity. |
| Event semantics | `joulewise.events.v2` | Recorded in `metadata.event_semantics_version`; absent means the historical event arm, never an inferred v2. |
| Summary reducer | `0.6.0` | First request/burst-aware reducer; `0.4.1`, `0.4.2`, and `0.5.0` retain exact frozen arms. |
| Generic analysis registry | `joulewise.analysis_registry.v2` | Sibling of the AP-2-specific v1 registry. |
| Generic analysis manifest | `joulewise.analysis_manifest.v2` | Sibling of AP-2 v1; it does not reinterpret v1 bytes. |
| Campaign attempt ledger | `joulewise.attempt_ledger.v1` | Complete deterministic attempt history for each generic-manifest Entry/cell. |
| Output-identity report | `joulewise.output_identity_report.v1` | Cross-bundle C-023-OUTPUT-IDENTITY gate. |

Historical event semantics are selected only by the historical dispatch rules.
No implementation may write `metadata.event_semantics_version` into a sealed
bundle, synthesize it into normalized metadata, or treat its absence as proof
of v2.

## 2. Normalized config identity

### 2.1 Scoped additive extension

An AXI config retains top-level `schema_version: "0.1"` and adds all three of
these top-level fields:

| Field | Type | Null/absence rule |
|---|---|---|
| `schema_extensions` | array of unique strings | REQUIRED for the AXI path and MUST contain exactly `"joulewise.axi_decode_config.v1"` for this extension. It is absent, not null, in non-AXI v0.1 configs. |
| `batch_policy` | BatchPolicy object | REQUIRED and non-null when the extension is declared; absent in non-AXI configs. |
| `speculation` | SpeculationPolicy object | REQUIRED and non-null when the extension is declared, including spec-off controls; absent in non-AXI configs. |

The normalized serializer MUST omit all three fields when the source config
does not declare the extension. That scoped omission preserves existing
normalized v0.1 config bytes. When declared, the fields are emitted in the
sorted-key normalized JSON and therefore participate in
`metadata.config_sha256`. Unknown extension names fail validation rather than
falling through the v0.1 warn-and-ignore policy.

Every new speculative-on, speculative-off, AP-SPEC control, and AP-BATCH
control—including B=1 controls—MUST declare this extension and MUST produce
`joulewise.events.v2` bundles.

### 2.2 BatchPolicy

| Field | Type | Null rule and frozen meaning |
|---|---|---|
| `mode` | enum string: `single_request` or `static_batch` | REQUIRED, never null. `continuous` is not a v1 value. |
| `requested_batch_size` | integer >= 1 | REQUIRED, never null. This is configured B, not an observed count. |
| `admission_policy` | enum string: `immediate` or `admit_roster_together` | REQUIRED, never null. |
| `synchronization_policy` | enum string: `none` or `barrier_before_prefill` | REQUIRED, never null. |
| `dispatch_policy` | enum string: `one_request_call` or `one_native_batch_call` | REQUIRED, never null. A Python loop over singleton calls is not a native static batch. |
| `request_roster_ref` | non-empty relative path string | REQUIRED, never null; points to a `joulewise.request_roster.v1` artifact. |
| `request_roster_sha256` | 64-character lowercase hexadecimal string | REQUIRED, never null; SHA-256 of the normalized roster bytes. |

Cross-field invariants:

1. `single_request` requires B=1, `immediate`, `none`, and
   `one_request_call`.
2. `static_batch` requires `admit_roster_together`,
   `barrier_before_prefill`, and `one_native_batch_call`. B MAY be 1 for
   the AP-BATCH B=1 control.
3. `requested_batch_size` equals the request count in the roster artifact.
4. A future continuous scheduler MUST use a successor extension; adding
   `continuous` to this enum is forbidden.

RequestRoster v1 is exact-keyed with
`schema_version: "joulewise.request_roster.v1"` and non-empty array
`requests`. Each request descriptor is exact-keyed:

| Field | Type | Null rule |
|---|---|---|
| `request_ordinal` | integer >= 0 | Required, unique, and contiguous from 0 in array order. |
| `request_input_id` | non-empty identifier string | Required and unique. |
| `prompt_source` | enum `prompt_text`, `token_ids`, or `dataset_item` | Required. |
| `prompt_sha256` | 64-character lowercase hexadecimal string | Required. The exact source-specific preimages are frozen below. |
| `output_policy_name` | non-empty string | Required. |
| `requested_output_tokens` | integer >= 0 or null | Null only for an unbounded/natural-EOS policy. |

The roster top-level exact field set is only `schema_version` and `requests`;
the descriptor exact field set is precisely the six rows above. JSON strings
are preserved as supplied: no trimming, newline conversion, case folding,
Unicode normalization, or escape-based semantic rewrite is allowed. Ordinals,
requested counts, and token IDs are JSON integers (booleans are rejected).
Objects are serialized with keys in lexicographic code-point order, two-space
indentation, `ensure_ascii=False`, UTF-8 encoding, and exactly one trailing
LF; arrays preserve declared order. The roster SHA-256 is over exactly those
normalized bytes. It is embedded at bundle root as `request_roster.json`; the
configured reference identifies the source, while the hash and embedded bytes
are evidence.

The request `prompt_sha256` preimage is selected only by `prompt_source`:

- `prompt_text`: UTF-8 bytes of `joulewise.request_prompt_text.v1\n` followed
  by the exact prompt string's UTF-8 bytes, with no added terminator;
- `token_ids`: UTF-8 bytes of `joulewise.prompt_token_ids.v1`, then one NUL
  byte, then compact canonical JSON of the ordered integer array using
  `sort_keys=True` and separators `(",", ":")`, matching the existing
  `prompt_token_ids_sha256` contract; or
- `dataset_item`: UTF-8 bytes of `joulewise.request_dataset_item.v1\n`
  followed by compact canonical JSON of the complete source-manifest row using
  sorted keys, separators `(",", ":")`, and `ensure_ascii=False`.

The source prompt, ordered token-ID array, or complete dataset row is the
producer input and MUST be available when the roster is authored. A
`prompt_sha256` is never null and MUST NOT be copied from an unverified source.

### 2.3 SpeculationPolicy

| Field | Type | Null rule and frozen meaning |
|---|---|---|
| `mode` | enum string: `off`, `draft_model`, or `native_mtp` | REQUIRED, never null. This discriminator is authoritative; a null draft identity does not mean off. |
| `max_proposed_tokens` | integer >= 1 or null | Null for `off`; required for both enabled modes. It is a configured cap, not `tokens_proposed`. |
| `draft_model_identity` | DraftModelIdentity object or null | Required for `draft_model`; null for `off` and `native_mtp`. |
| `native_mtp_identity` | NativeMTPIdentity object or null | Required for `native_mtp`; null for `off` and `draft_model`. |

DraftModelIdentity is exact-keyed:

| Field | Type | Null rule |
|---|---|---|
| `model_name` | non-empty string | Never null. |
| `model_revision` | non-empty string | Never null; use an immutable revision. |
| `model_artifact_sha256` | 64-character lowercase hexadecimal string | Never null; folded-directory identity is allowed. |
| `weight_format` | non-empty string | Never null. |
| `quantization` | non-empty string | Never null; use `none` when unquantized. |
| `runtime_backend` | non-empty string | Never null. |
| `runtime_version` | non-empty string | Never null. |
| `tokenizer` | TokenizerIdentity object | Never null. |

TokenizerIdentity is exact-keyed: `name`, `revision`, and `class` are
non-empty strings; `vocabulary_size` is an integer >= 1. None is nullable.

NativeMTPIdentity is exact-keyed:

| Field | Type | Null rule and invariant |
|---|---|---|
| `target_model_artifact_sha256` | 64-character lowercase hexadecimal string | Never null and MUST equal `metadata.runtime.target_model_artifact_sha256`, the runtime-observed target artifact identity defined in §3. |
| `head_count` | integer >= 1 | Never null. |
| `draft_depth` | integer >= 1 | Never null. |
| `head_configuration` | non-empty JSON object | Never null; contains runtime-native MTP/head configuration and MUST contain only JSON values. |
| `head_configuration_sha256` | 64-character lowercase hexadecimal string | Never null; SHA-256 of JouleWise canonical JSON bytes of `head_configuration`: `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")`. |

The normalized config contains requested identity. The runtime MUST record the
same identity in metadata and the validator MUST compare it to observed target
and adapter provenance. A config assertion alone is not live/runtime proof.

## 3. Bundle metadata

Every `joulewise.events.v2` bundle MUST have these top-level metadata fields:

| Field | Type | Null rule |
|---|---|---|
| `event_semantics_version` | string const `joulewise.events.v2` | REQUIRED, never null. It is independent of `config.schema_version`. |
| `batch` | BatchObservation object | REQUIRED, never null. |
| `speculation` | SpeculationPolicy object | REQUIRED, never null, and canonical-JSON equal to normalized config `speculation`. |
| `runtime.primary_source_identity` | non-empty string | REQUIRED, never null. The controller/runtime adapter produces it from the runtime/telemetry source binding selected to represent target execution; it is the exact source used for the primary decode-window metric. |
| `runtime.target_model_artifact_sha256` | 64-character lowercase hexadecimal string | REQUIRED, never null. The runtime adapter produces it from the artifact actually loaded: the file SHA-256 for one file or the repository's folded-directory SHA-256 for a directory. It is runtime evidence, not a copy accepted from config. |
| `runtime.target_tokenizer_identity` | TargetTokenizerIdentity object | REQUIRED, never null in a strict-valid v2 bundle. The runtime adapter produces it from the target tokenizer actually loaded; requested/config identity alone is insufficient. |

The two dotted paths above are required members of the existing top-level
`runtime` object; they are not literal dotted top-level keys. Every v2
request-scoped phase or decode event carries the same
`metadata.source_identity` as the telemetry source it describes. The primary
decode duration in §8 is the union for
`metadata.runtime.primary_source_identity`. Strict validation rejects a
missing source, a source with no unique telemetry/rail-manifest binding, or a
phase marker whose source cannot be resolved. For native MTP,
`config.speculation.native_mtp_identity.target_model_artifact_sha256`, the
canonical metadata speculation copy, and
`metadata.runtime.target_model_artifact_sha256` MUST be equal.

For a target directory, the folded hash is the existing D-033 identity:
enumerate the adapter's recognized loaded weight files, map each normalized
root-relative POSIX path to the lowercase SHA-256 of its exact file bytes,
compact-serialize that map with sorted keys and separators `(",", ":")`, then
SHA-256 the UTF-8 bytes of `joulewise.model_artifact_identity.v1`, one NUL byte,
and that JSON. Failure to observe/read a loaded target artifact makes a v2
bundle strict-invalid; the required runtime target hash is never null or
replaced by the requested config hash.

TargetTokenizerIdentity is exact-keyed:

| Field | Type | Null rule and producer |
|---|---|---|
| `name` | non-empty string | Required, never null; runtime-observed target tokenizer name. |
| `revision` | non-empty string | Required, never null; runtime-resolved immutable tokenizer revision. |
| `tokenizer_artifact_sha256` | 64-character lowercase hexadecimal string | Required, never null; runtime adapter hash of the loaded target tokenizer artifact set. |

For the artifact hash, map every loaded tokenizer artifact's normalized
root-relative POSIX path to the lowercase SHA-256 of its exact file bytes,
compact-serialize the non-empty map with sorted keys and separators
`(",", ":")`, then SHA-256 the UTF-8 bytes of
`joulewise.tokenizer_artifact_identity.v1`, one NUL byte, and that JSON. Name
and revision follow the stack-identity discipline in
`docs/contracts/token_normalization.md`: exact concrete evidence is required
for strict-valid v2; `unknown` or missing identity makes the bundle invalid but
remains representable as missing evidence in the cross-bundle report (§10).

BatchObservation is exact-keyed:

| Field | Type | Null rule and frozen meaning |
|---|---|---|
| `policy_schema_version` | string const `joulewise.axi_decode_config.v1` | Required. |
| `configured_batch_size` | integer >= 1 | Required; exact copy of config requested B. |
| `realized_batch_size` | integer >= 0 | Required; number of distinct requests actually admitted to the one static group, or 1/0 for a single-request run admitted/not admitted. |
| `submitted_request_count` | integer >= 0 | Required explicit count. |
| `admitted_request_count` | integer >= 0 | Required explicit count. |
| `terminal_request_count` | integer >= 0 | Required explicit count. |
| `batch_group_id` | non-empty string or null | Required string for `static_batch`; null for `single_request`. |
| `request_roster_sha256` | 64-character lowercase hexadecimal string | Required; equals config and embedded roster bytes. |

Configured and realized B MUST be read from config/metadata respectively.
Readers MUST NOT infer either from event-line count. Validators SHALL
cross-check the explicit observations against distinct request IDs in
`outputs/requests.jsonl`; cross-checking is not permission to synthesize a
missing field.

## 4. Event semantics

### 4.1 Stable top-level event shape and dispatch

The five existing top-level keys remain exact:
`timestamp_s`, `event_type`, `phase`, `message`, and `metadata`.
`request_id`, batching identity, and scheduler identity live only inside
`metadata`.

Historical `event_type: "token"` records remain singleton output-token
events. No reader may interpret one historical token event as N output tokens,
and no producer may add `emitted_count > 1` to a token event.

V2 adds `event_type: "decode_emission"`. It records one request's one
completed decode step and may commit one or more output tokens. A runtime
scheduler tick that completes decode work for k requests emits k separate
decode-emission records, never one record containing a request-ID list. An
active request not selected in the tick emits no decode-emission record.

When genuine per-token callbacks exist, a producer emits both:

- one `decode_emission` record for the step; and
- one singleton `token` record per committed output token.

The reducer counts output from decode-emission records. It consumes v2 token
records only as per-token timestamp/ID evidence and MUST reject inconsistent
duplicates rather than double-count them.

### 4.2 Common request metadata

Every v2 request-scoped event has:

| Field | Type | Null rule |
|---|---|---|
| `request_id` | non-empty string | REQUIRED, never null; unique within a bundle. |
| `request_ordinal` | integer >= 0 | REQUIRED, never null; stable configured-roster/submission-order index. |
| `request_input_id` | non-empty identifier string | REQUIRED, never null; equals the roster descriptor. |
| `request_event_ordinal` | integer >= 0 | REQUIRED, never null; starts at 0 and increases by exactly 1 across all events for that request. |
| `request_roster_sha256` | 64-character lowercase hexadecimal string | REQUIRED, never null. The controller copies the hash of the embedded normalized RequestRoster; it equals config and `metadata.batch.request_roster_sha256`. |
| `source_identity` | non-empty string | REQUIRED, never null. The runtime adapter/controller emits the resolved telemetry source binding for this event; primary runtime work uses `metadata.runtime.primary_source_identity`. |
| `batch_group_id` | non-empty string or null | REQUIRED key; same rule as BatchObservation. |
| `scheduler_step_id` | non-empty string or integer >= 0, or null | REQUIRED key. Its value is null when the runtime supplies no scheduler-step identity; it is never omitted and never replaces `request_id`. |

Equal timestamps are valid. For one request, `request_event_ordinal`, not
timestamp or global FIFO, establishes order. Global JSONL order MUST be
nondecreasing by `timestamp_s`; ties may interleave requests.

### 4.3 Lifecycle vocabulary

V2 uses:

| Event type / phase | Required additional metadata |
|---|---|
| `request_submitted` / `request` | none |
| `request_admitted` / `request` | `admitted_at_s`: finite number equal to event timestamp |
| `phase_start` or `phase_end` / named phase | `request_phase_ordinal`: integer >= 0, increasing within the request |
| `request_terminal` / `request` | `terminal_status`; `stop_reason`; `failure_reason`; `failure_message`; `realized_output_token_count`; and `cancelled_proposal_counters` as defined below |

Lifecycle-specific metadata fields are:

| Field | Type | Null rule |
|---|---|---|
| `admitted_at_s` | finite number | Required only on `request_admitted`; never null there and equal to event timestamp. Absent on other event types. |
| `request_phase_ordinal` | integer >= 0 | Required only on request-scoped `phase_start`/`phase_end`; never null there. Absent on other event types. |
| `terminal_status` | enum string `succeeded`, `failed`, `cancelled`, or `cancelled_after_proposal_before_output` | Required only on `request_terminal`; never null there. The fourth value is the explicit terminal outcome for enabled speculation that performed proposal/verification work but committed no output. |
| `stop_reason` | non-empty string or null | Required key only on `request_terminal`; non-null for succeeded, nullable for all failure/cancellation states. |
| `failure_reason` | non-empty string or null | Required key only on `request_terminal`; null for succeeded and non-null for all failure/cancellation states. |
| `failure_message` | string or null | Required key only on `request_terminal`; null or explanatory text for all failure/cancellation states and null for succeeded. |
| `realized_output_token_count` | integer >= 0 | Required key only on `request_terminal`, never null there. The controller produces it from the committed runtime result at terminalization; it equals the request output row and committed token evidence, including zero. |
| `cancelled_proposal_counters` | CancelledProposalCounters object or null | Required key only on `request_terminal`. It is non-null iff status is `cancelled_after_proposal_before_output`; otherwise null. The runtime adapter produces it from the completed proposal/verification work that did not commit output. |

CancelledProposalCounters is exact-keyed: `tokens_proposed` is an integer >= 1;
`tokens_accepted`, `target_emitted_count`, and `emitted_count` are integer
constants 0; and `acceptance_rate` is number constant 0.0. No member is
nullable. These retained counters are terminal evidence, not a
`decode_emission`, because no output was committed. A producer MUST NOT erase
the completed proposal work by replacing `tokens_proposed` with zero.

For a succeeded terminal status, `stop_reason` is required and both failure
fields are null. For any failure/cancellation status, `failure_reason` is
required; `stop_reason` and `failure_message` may be null. Status
`cancelled_after_proposal_before_output` additionally requires enabled
speculation, no decode-emission or singleton-token event, terminal realized
count zero, and the non-null retained counter object above.

An admitted request MAY have multiple non-overlapping paired windows for the
same phase, distinguished by `request_phase_ordinal`; this keeps later
pause/resume behavior additive. A static v1 producer normally emits one
prefill and one decode window, but the schema and validator do not require
that cardinality. Submission may precede prefill by any duration. Different
requests may overlap arbitrarily. No validator may require a shared prefill
boundary, shared decode boundary, or unequal timestamps.

### 4.4 DecodeEmission metadata

In addition to common request metadata, each `decode_emission` record has:

| Field | Type | Null rule and meaning |
|---|---|---|
| `decode_step_ordinal` | integer >= 0 | Required; begins at 0 and increases by exactly 1 for this request's emission records. |
| `output_token_start_ordinal` | integer >= 0 | Required; index of the first committed token represented by this event. |
| `emitted_count` | integer >= 1 | Required; all output tokens committed at this step. |
| `tokens_proposed` | integer >= 0 or null | Null iff speculation mode is off; otherwise actual candidate positions submitted to target verification. |
| `tokens_accepted` | integer >= 0 or null | Null iff speculation mode is off; otherwise proposed draft/MTP tokens committed unchanged. |
| `target_emitted_count` | integer >= 0 | Required for every mode; target-origin correction/bonus/ordinary tokens committed at this step. |
| `emitted_token_ids` | array of integers or null | REQUIRED key containing optional evidence. When non-null its length equals `emitted_count`; null means the runtime did not expose IDs. |
| `emitted_token_ids_sha256` | 64-character lowercase hex string or null | REQUIRED key containing optional evidence. Non-null only when strict validation can recompute it from the matching ordered request-token artifact slice. |

Both keys are always present. The four value combinations are exhaustive:
array/hash both null (no ID evidence), array non-null/hash null (inline only),
array null/hash non-null (artifact-backed slice hash only), or both non-null.
When both are non-null, the hash MUST match the array. When both are null,
count evidence remains valid but exact-token output identity may be
unassessable. The slice-hash input is UTF-8
`joulewise.request_output_token_ids_slice.v1\n` plus canonical JSON of the
ordered integer slice. A non-null slice hash requires non-null token IDs in
the corresponding request-token artifact rows so strict validation can
recompute it.

For enabled speculation:

`emitted_count = tokens_accepted + target_emitted_count`.

Every enabled-mode emission also requires
`tokens_proposed <= config.speculation.max_proposed_tokens`. The same bound
applies to `cancelled_proposal_counters.tokens_proposed`. A violation raises
the named strict-validator refusal
`proposal_count_exceeds_configured_cap`; it is never clipped, averaged, or
treated as a larger implicit configuration.

For speculation off, `tokens_accepted` remains null by contract; the
equivalent partition check is
`emitted_count = 0 + target_emitted_count`. The validator MUST NOT
materialize that conceptual zero into the nullable speculation field.

### 4.5 Singleton token metadata under v2

A v2 singleton `token` record has common request metadata plus:

| Field | Type | Null rule |
|---|---|---|
| `decode_step_ordinal` | integer >= 0 | Required; identifies its parent decode-emission step. |
| `output_token_ordinal` | integer >= 0 | Required and unique within request. |
| `token_id` | integer or null | REQUIRED key; null only when the callback exposes timing but not ID. |
| `timestamp_provenance` | enum string `runtime_per_token_callback` | Required. No synthesized or copied step timestamp is allowed. |

The token event timestamp MUST equal the matching request-token row timestamp.
All token ordinals covered by one emission are the contiguous range beginning
at `output_token_start_ordinal`.

## 5. Frozen counter contract

The following meanings are immutable at v1:

| Field | Per-emission and rollup meaning | Speculation-off rule | Enabled zero rule |
|---|---|---|---|
| `tokens_proposed` | Candidate token positions actually submitted to target verification; excludes unfilled slots and target correction/bonus tokens. Rollup is the sum of non-null emission values plus the retained terminal proposal count for `cancelled_after_proposal_before_output`. | null, never zero | zero when enabled work actually submits no candidates; cancellation after nonzero proposal work retains its positive terminal count |
| `tokens_accepted` | Proposed draft/MTP tokens committed unchanged to output; excludes all target-origin correction/bonus tokens. Rollup is the sum of non-null emission values plus retained terminal value 0 for the special cancellation state. | null, never zero | zero when no proposed token is accepted |
| `emitted_count` | All output tokens committed: accepted candidates plus target-origin tokens. Rollup is the sum of event values plus retained terminal value 0 and MUST match output evidence. | non-null observed count | zero is allowed only at request/bundle rollup or in the retained terminal counter object; an emission event itself has at least one |
| `acceptance_rate` | `sum(tokens_accepted) / sum(tokens_proposed)` over emission plus retained terminal counters; never the mean of event or request rates. | null | null when proposal total is zero; otherwise finite in [0,1], including 0.0 for proposal-work-then-cancelled-before-output |

The three nullable speculation fields are `tokens_proposed`,
`tokens_accepted`, and `acceptance_rate`; all three are null for spec-off.
`emitted_count` remains the observed output count, and off-mode
`target_emitted_count` equals it.

Native MTP and external draft-model modes use exactly the same proposal and
acceptance definitions. `max_proposed_tokens` is not an observed proposal
count. It is nevertheless a hard per-decode-attempt validation cap: every
emission and every retained cancelled proposal count MUST be no greater than
it. Target-origin tokens never enter either speculation counter.

## 6. Request-indexed output evidence

### 6.1 Artifacts

Every v2 bundle writes:

```text
request_roster.json
outputs/
  requests.jsonl
  request_tokens.jsonl
```

`requests.jsonl` has exactly one row per admitted request in
`request_ordinal` order. `request_tokens.jsonl` has exactly one row per
committed output token, ordered first by request ordinal and then output-token
ordinal. These files are immutable evidence.

For a B=1 v2 bundle, legacy `response.txt` and `tokens.jsonl` MAY be emitted
as compatibility mirrors, but they are not authoritative and strict
validation compares them to the request-indexed artifacts. B>1 bundles MUST
NOT collapse outputs into one response. Existing suite artifacts remain
separate and unchanged.

### 6.2 Request row schema

Each `requests.jsonl` row is exact-keyed:

| Field | Type | Null rule |
|---|---|---|
| `request_id` | non-empty string | Required, never null. |
| `request_ordinal` | integer >= 0 | Required, never null, unique, and equal to the configured roster ordinal. Admitted rows are sorted by ordinal but may have gaps when a request was not admitted. |
| `request_input_id` | non-empty identifier string | Required and equal to roster/event identity. |
| `prompt_sha256` | 64-character lowercase hex string | Required and equal to the roster prompt hash. |
| `request_roster_sha256` | 64-character lowercase hex string | Required and equal to config, metadata, embedded roster bytes, and every request-scoped event. |
| `batch_group_id` | non-empty string or null | Required; follows batch mode. |
| `terminal_status` | enum string `succeeded`, `failed`, `cancelled`, or `cancelled_after_proposal_before_output` | Required and equal to the terminal event. |
| `output_policy_name` | non-empty string | Required. |
| `requested_output_tokens` | integer >= 0 or null | Null only for a natural-EOS/unbounded policy. |
| `output_token_count` | integer >= 0 | Required realized committed count. |
| `stop_reason` | non-empty string or null | Required for success; may be null otherwise. |
| `failure_reason` | non-empty string or null | Null for success; required otherwise. |
| `response_text` | string or null | Null only when the runtime exposes no text. Empty string is distinct from null. |
| `response_text_sha256` | 64-character lowercase hex string or null | Required when response text is non-null and computed over exact UTF-8 bytes; null otherwise. |
| `emitted_token_ids_sha256` | 64-character lowercase hex string or null | Hash of the complete ordered non-null token-ID sequence using domain `joulewise.request_output_token_ids.v1`; null if any ID is unavailable. |
| `tokens_proposed` | integer >= 0 or null | Request rollup under the frozen counter rules, including retained proposal work from the special cancellation terminal. |
| `tokens_accepted` | integer >= 0 or null | Request rollup under the frozen counter rules, including retained terminal zero. |
| `target_emitted_count` | integer >= 0 | Required request rollup. |
| `acceptance_rate` | finite number in [0,1] or null | Ratio of request totals; off or zero proposals gives null. |

The token-ID hash input is UTF-8 bytes of
`joulewise.request_output_token_ids.v1\n` followed by canonical JSON of the
integer array. It is not a text hash and is meaningful only with the recorded
tokenizer identity.

### 6.3 Request-token row schema

Each `request_tokens.jsonl` row is exact-keyed:

| Field | Type | Null rule |
|---|---|---|
| `request_id` | non-empty string | Required. |
| `request_ordinal` | integer >= 0 | Required. |
| `request_input_id` | non-empty identifier string | Required and equal to the request row. |
| `output_token_ordinal` | integer >= 0 | Required, contiguous from 0 within request. |
| `decode_step_ordinal` | integer >= 0 | Required. |
| `token_id` | integer or null | Null when unavailable. |
| `timestamp_s` | finite number or null | Non-null only for a genuine per-token runtime timestamp. |
| `timestamp_provenance` | enum string `runtime_per_token_callback` or null | Required when timestamp is non-null; null otherwise. |

An event timestamp copied across every token in a burst is not genuine
per-token evidence and MUST be stored as null in the token rows.

## 7. Request lifecycle and strict-validation invariants

All invariants in this section are machine-testable. A missing required field
is an error; no reader may repair it from a nearby count.

### 7.1 Lifecycle completeness

For each distinct `request_id`:

1. There is exactly one `request_submitted` event.
2. There is zero or one `request_admitted` event.
3. Every admitted request has exactly one `request_terminal` event, even in
   a failed bundle. Its prefill/decode work may be incomplete, but the terminal
   event MUST select one of the four terminal states rather than leaving the
   request ambiguous; proposal work cancelled before output uses
   `cancelled_after_proposal_before_output`, not generic `cancelled`.
4. A submitted but non-admitted request MAY have a terminal failed/cancelled
   event but MUST NOT appear in `outputs/requests.jsonl`.
5. Every admitted request has exactly one request row, and no other request has
   a row.
6. `request_ordinal`, `request_input_id`, prompt/roster identity and hash,
   `batch_group_id`, terminal status, terminal realized output count, stop
   reason, and failure reason agree across roster, events, request rows, and
   metadata counts.
7. A bundle with top-level status `succeeded` requires every admitted request
   to terminate `succeeded`. Failed/unsupported bundles retain all evidence
   and explicit terminal outcomes.
8. Request event ordinals are unique, contiguous, and order submit before
   admit, admit before phase/emission work, and work before terminal.
9. Emission and token events fall inside that request's paired decode window.
10. No event for one request may satisfy a lifecycle or phase requirement for
    another request.

### 7.2 Phase pairing and overlap

For event semantics v2, the phase-pairing key is:

`(source_identity, request_id, phase, request_phase_ordinal)`.

The required event `metadata.source_identity` is the normalized telemetry
source-binding ID produced using the existing source selection precedence:
node ID/node identity, else non-null node role, else the configured default
source. Unlike historical arms, v2 persists the resolved non-null string and
does not re-infer it at reduction time. Start and end require the same full
key. Reversed or unmatched pairs fail closed.

Within one `(source_identity, request_id)` stream, same-phase windows MUST
NOT overlap. Prefill and decode for the same request MUST NOT overlap. Across
different request IDs, equal or overlapping phase windows are allowed.

For a group phase such as static-batch decode, the reducer MUST:

1. group paired windows by `(source_identity, phase)`;
2. form the mathematical union of all request intervals in that group,
   merging overlapping and boundary-touching intervals;
3. integrate each union segment exactly once on that source's power curve; and
4. sum energy only across distinct source identities.

It MUST NOT sum synchronized duplicate request windows. For example, B
requests each carrying decode `[1,3]` over the same source yield one
two-second decode interval, not B times that interval. Distinct identified
nodes retain the existing legitimate sum-across-meters rule.

If different phase names overlap on one source across requests (for example,
one request prefill while another decodes), each phase metric integrates its
own union and the phase metrics are explicitly non-additive attribution views.
Their sum MUST NOT be presented as a decomposition of gross energy.
`measurement_quality.phase_identifiability.group_phase_windows_overlap`
records true for that case; it does not invalidate request-lifecycle evidence.

### 7.3 Decode and output rollups

For every admitted request:

1. Decode-emission ordinals are unique and contiguous from 0.
2. `output_token_start_ordinal` equals the prior cumulative
   `emitted_count`; emission slices are gap-free and non-overlapping.
3. Sum of event `emitted_count` plus the special terminal retained
   `emitted_count` (always zero) equals:
   - the number of request-token rows;
   - request-row `output_token_count`;
   - terminal `realized_output_token_count`; and
   - the count of emitted token IDs whenever IDs are present.
4. Sum of event `target_emitted_count` equals the request-row value.
5. Enabled-mode proposal and acceptance sums include all emission values and,
   only for `cancelled_after_proposal_before_output`, the terminal retained
   counters; those sums equal their request-row values. Off-mode values are
   null in every event and row.
6. Enabled mode enforces, per event and at request rollup,
   `emitted_count = tokens_accepted + target_emitted_count`.
   Off mode enforces the conceptual-zero form defined in §4.4.
7. `tokens_accepted <= tokens_proposed` per event and at every rollup. Every
   individual emission and terminal retained proposal count is <= configured
   `max_proposed_tokens`; failure raises
   `proposal_count_exceeds_configured_cap`.
8. Acceptance rate is recomputed from totals; any stored mean-of-rates is
   invalid.
9. If emitted IDs/hashes are present in an event, they match the exact
   request-token ordinal slice. The full request hash matches the ordered
   concatenation.
10. A fixed-budget-exact successful request has
    `output_token_count == requested_output_tokens` and its stop reason says
    the requested tokens were emitted. Underruns use the existing incomplete
    policy and realized stop rather than claiming exactness.
11. `cancelled_after_proposal_before_output` requires output count zero, no
    emission/token rows, positive retained proposal count no greater than the
    configured cap, accepted/target/emitted counts zero, and request acceptance
    rate exactly 0.0. Collapsing those counters to zero raises
    `cancelled_proposal_evidence_lost`.

At bundle rollup, `emitted_count`, `tokens_proposed`,
`tokens_accepted`, and `target_emitted_count` are sums over request rows,
with off-mode proposal/acceptance remaining null. The bundle acceptance rate
is recomputed from bundle totals. The bundle emitted count MUST equal all
committed request-token rows, not event-line count.

### 7.4 Config, metadata, and batch observations

Strict validation additionally requires:

1. AXI config extension, metadata event version, and reducer 0.6.0 appear
   together; partial opt-in is invalid.
2. Metadata speculation identity equals config identity and satisfies the
   mode-specific null rules.
3. Draft-model and target stack identities are separately complete. Native
   MTP target hash equals `metadata.runtime.target_model_artifact_sha256` and
   its head config hash recomputes. The runtime target hash is produced from
   the observed loaded artifact; a matching config assertion is insufficient.
4. `metadata.runtime.target_tokenizer_identity` is present and exact-keyed;
   its artifact hash recomputes from the runtime-observed loaded tokenizer
   artifact map. Name, resolved revision, and artifact hash are concrete;
   config-only, `unknown`, or silently omitted target-tokenizer identity is
   invalid.
5. Metadata configured B equals config requested B.
6. Config, metadata, embedded roster, manifest entry, every request row, and
   every request-scoped event have the same roster hash; requested B equals
   roster length.
7. Metadata submitted/admitted/terminal counts equal distinct artifact/lifecycle
   identities. Metadata realized B equals the admitted roster size for this
   v1 single-group execution.
8. Every static request uses the one explicit batch-group ID; single-request
   events use null. Scheduler-step IDs, if present, may group work across
   requests but are never accepted as request identity.
9. Request submission, prefill, decode, and terminal timestamps need not align
   across requests. Any validator assumption that they share boundaries is a
   defect.
10. `metadata.runtime.primary_source_identity` is non-null, resolves to exactly
   one existing telemetry/rail-manifest source, and equals the source used for
   the primary decode-window union. Every event source identity resolves; it
   is never reconstructed from request or scheduler identity.

### 7.5 Output-evidence precedence

For v2, evidence precedence is:

1. immutable `outputs/request_tokens.jsonl` and
   `outputs/requests.jsonl`;
2. request-scoped lifecycle, emission, and singleton token events;
3. metadata rollups;
4. derived `summary_metrics.json`.

The validator proves agreement among levels 1-3. The reducer consumes only
strictly paired evidence. Summary is derived and remains the one sanctioned
post-finalize rewrite; it never overrides output evidence.

## 8. Reducer 0.6.0

### 8.1 Dispatch before interpretation

Version dispatch occurs before phase pairing, token counting, idle estimation,
or additive-field comparison. The exact arms are:

| Recorded reducer / bundle identity | Required behavior |
|---|---|
| Six frozen pre-D-033 identities without provenance | Preserve the existing provenance-less additive-absence arm exactly. Do not apply v2 semantics. |
| `0.4.1` | Preserve today's exact unweighted-idle code path, historical event/token interpretation, derived outputs, and current era-aware tolerant comparison behavior. Do not add 0.6.0 fields or broaden its current tolerated-absence set. |
| `0.4.2` | Preserve today's exact unweighted-idle code path, historical event/token interpretation, derived outputs, and current era-aware tolerant comparison behavior. Do not add 0.6.0 fields or broaden its current tolerated-absence set. |
| `0.5.0` | Preserve today's exact duration-weighted idle-v2 and historical event/token code path, derived outputs, and current comparison behavior, including its existing treatment of absent `idle_baseline.gpu_freq_mhz_mean`. Do not add a new 0.6.0 absence tolerance. |
| `0.6.0` + `metadata.event_semantics_version == "joulewise.events.v2"` | Use the request/burst path in this document, duration-weighted idle-v2, unioned group phase windows, request output artifacts, and new metrics. |
| `0.4.0`, `0.3.x`, recorded `0.2.x`, unknown versions, or incoherent version/event pairs | Unsupported; require explicit compatible re-reduction or report a structured refusal. Never guess. |

The implementation MUST keep the existing arms' code paths and outputs
unchanged. Expected behavior is first captured by observing the current
base-head arm, then transcribed into independently hand-authored golden files
and hand-checked against its formula, key presence, nulls, and
tolerant-comparison outcome; no reducer-produced output file is adopted as a
fixture. Those goldens
prove preservation of current behavior; they do not claim that re-reduction of
an older stored summary produces byte-identical historical bytes. A shared
helper may be used only where the current-behavior goldens remain exact.

No version-specific historical serializer is introduced by AXI-SA. New v2
fields live in a separate `SummaryMetricsV060` output shape and never enter the
existing SummaryMetrics paths. Only 0.6.0 receives a versioned serializer and
canonical byte-golden outputs. The old strict comparator's era-aware tolerated
absence sets remain byte-for-byte/code-path unchanged; adding 0.6-only keys to
those sets is forbidden.

A finalized bundle's `reduce` command defaults to the reducer version already
recorded in its summary, not the latest package constant. A not-yet-finalized
v2 bundle uses 0.6.0. Explicit migration to 0.6.0 is permitted only for a v2
bundle; historical event bundles cannot acquire burst semantics by
re-reduction. This prevents a package-version bump from forcing current-era
0.5.0 bundles through a new path.

`summary_provenance` under the new 0.6.0 serializer adds required string field
`event_semantics_version: "joulewise.events.v2"`. It is absent, not null, in
frozen earlier summaries.

### 8.2 Existing metrics stay frozen

- `energy_output_token_j` retains its historical idle-subtracted numerator
  and output-token denominator. It is not relabeled gross.
- `energy_request_j` remains a stored historical idle-subtracted field.
  Reader-facing headline selection follows D-067 and uses
  `gross_energy_j`; the stored field is not rewritten.
- The historical singleton scalar fields `energy_request_j`,
  `energy_token_j`, `energy_output_token_j`, `ttft_s`,
  `decode_latency_s`, `throughput_tokens_s`, and
  `inter_token_throughput_tokens_s` may be derived for a v2 B=1 bundle under
  their frozen meanings. They are all null for realized B>1, where one scalar
  would silently change a request/token-stream identity into a group identity.
  `idle_subtracted_energy_j` may still report the explicitly labeled
  secondary group-window basis; new group-safe fields carry the primary
  burst/batch results.
- `throughput_tokens_s` retains the historical N-over-first/last-token-span
  identity and legacy label.
- `inter_token_throughput_tokens_s` retains
  `(N-1)/(t_last-t_first)`. Under v2 B=1 it is non-null only when every
  committed output token in the reduction scope has a genuine
  `runtime_per_token_callback` timestamp, N >= 2, and the span is positive.
  A burst timestamp is not expanded into per-token timestamps. Any missing
  per-token timestamp censors this field to null.

No existing metric name changes numerator, denominator, window, or censoring
identity.

The frozen-arm compatibility guarantee is therefore: **existing arms' code
paths and outputs unchanged, proven by current-behavior goldens**. A test
called “spoofed version labels” is only a shape/dispatch test: for example, a
0.6.0-only event or summary shape relabeled `0.5.0` MUST be rejected before it
can enter a frozen arm. It is not, and MUST NOT be described as, proof that an
arbitrary version label has authentic provenance.

### 8.3 New summary schema

Reducer 0.6.0 adds these top-level fields to a succeeded v2 summary:

| Field | Type | Formula and censoring |
|---|---|---|
| `decode_counter_rollup` | DecodeCounterRollup object | Required, non-null; bundle totals under §5. |
| `batch_group_gross_energy_j` | finite number >= 0 or null | REQUIRED key. For `static_batch`, non-null group-gross energy over `gross_batch_group` and equal to the measured static group window. For `single_request`, null; this field is never request energy. |
| `gross_energy_per_committed_output_token_j` | finite number >= 0 or null | Single-request numerator is `gross_energy_j`; static-batch numerator is `batch_group_gross_energy_j`. Divide by bundle `emitted_count`; null when emitted count is zero or the mode-selected gross numerator is unavailable. |
| `gross_energy_per_accepted_draft_token_j` | finite number >= 0 or null | The same mode-selected gross numerator divided by `tokens_accepted`; null for spec-off and for enabled mode with zero accepted tokens. It is a mechanism-yield diagnostic, never the on/off efficiency denominator. |
| `decode_phase_output_throughput_tokens_s` | finite number >= 0 or null | total committed output tokens divided by duration of the unioned decode window on the primary runtime source; null for missing/invalid/nonpositive decode duration. A valid positive window with zero committed tokens yields 0.0. |
| `decode_emission_event_rate_events_s` | finite number >= 0 or null | number of decode-emission events divided by the same unioned decode duration; same duration censoring. |
| `decode_emission_burst_size_mean_tokens` | finite number >= 1 or null | arithmetic mean of `emitted_count` over decode-emission events; null when there are no emission events. |
| `decode_emission_burst_size_p50_tokens` | finite number >= 1 or null | type-7 sample quantile at p=0.50 over event emitted counts; null on empty set. |
| `decode_emission_burst_size_p95_tokens` | finite number >= 1 or null | type-7 sample quantile at p=0.95 over event emitted counts; null on empty set. |
| `decode_emission_burst_size_max_tokens` | integer >= 1 or null | maximum event emitted count; null on empty set. |
| `request_decode_metrics` | array of RequestDecodeMetric objects | Required; one row per admitted request in ordinal order. Contains no energy attribution. |

The existing `measurement_quality.phase_identifiability` object adds required
v2 field:

| Field | Type | Null rule |
|---|---|---|
| `group_phase_windows_overlap` | boolean | Required and non-null under reducer 0.6.0; true when unions for two different phase names overlap on one source, otherwise false. Absent, not null, in earlier reducer arms. |

`window_evidence_precheck` uses `gross_request` for
`batch_policy.mode == "single_request"` and adds
`gross_batch_group` for `static_batch`. The new
`gross_batch_group` object has the existing request-precheck field shape,
`metric_name: "batch_group_gross_energy_j"`, and
`window_class: "gross_batch_group"`; it is required for a succeeded static
bundle and absent, not null, in earlier arms. A static group MUST NOT be
misreported under the request window class.

DecodeCounterRollup is exact-keyed:

| Field | Type | Null rule |
|---|---|---|
| `emitted_count` | integer >= 0 | Required. |
| `tokens_proposed` | integer >= 0 or null | Null iff mode off. |
| `tokens_accepted` | integer >= 0 or null | Null iff mode off. |
| `target_emitted_count` | integer >= 0 | Required. |
| `acceptance_rate` | finite number in [0,1] or null | Off or zero proposal total gives null. |

RequestDecodeMetric is exact-keyed:

| Field | Type | Null rule |
|---|---|---|
| `request_id` | non-empty string | Required. |
| `request_ordinal` | integer >= 0 | Required. |
| `terminal_status` | enum string `succeeded`, `failed`, `cancelled`, or `cancelled_after_proposal_before_output` | Required. |
| `output_token_count` | integer >= 0 | Required. |
| `decode_duration_s` | finite number > 0 or null | Null if no valid paired decode window. |
| `ttft_s` | finite number >= 0 or null | Admission-to-first-genuine-output callback; null without a genuine first-output timestamp. |
| `decode_phase_output_throughput_tokens_s` | finite number >= 0 or null | Request output count / request decode duration; null when duration is null. This is latency/work-rate evidence, not per-request energy. |
| `decode_emission_event_count` | integer >= 0 | Required. |
| `decode_counter_rollup` | DecodeCounterRollup object | Required. |
| `burst_size_mean_tokens` | finite number >= 1 or null | Same event-set rule as bundle metric. |
| `burst_size_p50_tokens` | finite number >= 1 or null | Type-7 p50 or null on empty set. |
| `burst_size_p95_tokens` | finite number >= 1 or null | Type-7 p95 or null on empty set. |
| `burst_size_max_tokens` | integer >= 1 or null | Max or null on empty set. |

No first-to-last emission-span metric is introduced in v1. A future metric of
that kind requires a new name and version and MUST predeclare whether one-event
requests yield null or a zero-duration result; it may not reuse either existing
throughput field.

### 8.4 Group-gross energy and attribution boundary

For `single_request`, top-level `gross_energy_j` is gross request energy and
`batch_group_gross_energy_j` is null. For `static_batch`, the governed energy
metric is `batch_group_gross_energy_j`, gross energy of the measured static
batch-group window. The group is the unit of energy analysis. The existing
generic physical-window field `gross_energy_j` may remain populated for bundle
compatibility but MUST NOT be placed in a request-scoped object, called request
energy, or used as the static AP-SPEC estimand; its value MUST equal
`batch_group_gross_energy_j` when both are present.

The reducer MUST NOT divide overlapping trace energy among requests, apportion
by token count, or label `batch_group_gross_energy_j / B` as request energy.
No request-scoped field may carry group energy. Request
metrics provide lifecycle, latency, counts, and output evidence only. A future
per-request energy result requires a separately frozen attribution model.

Future continuous mode, if authorized, uses session gross energy per total
committed token at offered load. It does not inherit an invented per-request
trace division from this contract.

## 9. AP-SPEC front-freeze and sibling analysis manifests

### 9.1 AP-2 v1 preservation

The existing AP-2 implementation is a specific, frozen wire:

- `joulewise.analysis_manifest.v1`;
- `joulewise.analysis_registry.v1`;
- registry ID `slice_2m_ap2_v1`; and
- hard-coded AP-2 metric identity, including the existing
  `energy_request_j` ratio path and
  `runtime_observed_output_tokens` denominator.

AXI MUST NOT generalize by mutating that path. At the base head, preservation
anchors are:

| Artifact | SHA-256 |
|---|---|
| `joulewise/analysis_manifest.py` | `5b4ba3ff4962bb9941c64a7f7acad98e6128119c5b4b93ad686e104a746e8cc9` |
| `configs/analysis_registry/slice_2m_ap2.v1.json` | `9defb37454aec95ff8a40df60f50edcca8e45d17d03f35364f07571d31475b01` |

Implementation SHOULD add a sibling module rather than edit
`analysis_manifest.py`. At minimum, the AP-2 registry bytes and generated v1
manifest fixture bytes MUST remain byte-identical. Refactoring shared helpers
is allowed only after byte-parity tests prove those outputs and v1 validation
behavior unchanged.

### 9.2 Generic registry v2

The AP-SPEC registry lives in a new sibling file and uses
`schema_version: "joulewise.analysis_registry.v2"`. Its top-level exact keys
are:

| Field | Type | Null rule |
|---|---|---|
| `schema_version` | const string `joulewise.analysis_registry.v2` | Required. |
| `registry_id` | enum string `ap_spec_draft_front_v1`, `ap_spec_native_mtp_front_v1`, `ap_spec_draft_campaign_v1`, or `ap_spec_native_mtp_campaign_v1` | Required and mechanism/status-specific. A registry artifact never changes status or ID. |
| `freeze_status` | enum `front_frozen` or `frozen` | Required. `front_frozen` permits only the manifest-bound mock/schema campaign it names; `frozen` is required before claim-bearing execution. |
| `plan_id` | const string `AP-SPEC` | Required. |
| `family_id` | enum string `FAM-AXI-SPEC-DRAFT-MATCHED-OUTPUT` or `FAM-AXI-SPEC-NATIVE-MTP-MATCHED-OUTPUT` | Required; selected by the one enabled mechanism in scope. |
| `claim_role` | const string `primary` | Required. |
| `selection_scope` | non-empty string | Required; names one target stack, workload roster, output policy, batch policy, and the off/on speculation pair. |
| `batch_mode` | enum `single_request` or `static_batch` | Required, never null; fixes the execution unit and metric/window choices below. |
| `sampling_plan` | SamplingPlan object | Required. |
| `multiplicity` | Multiplicity object | Required. |
| `pairing` | PairingPolicy object | Required. |
| `estimands` | array of exactly three Estimand objects | Required in the frozen order below. |
| `contrast_ids` | array const `["primary_gross_energy","committed_output_gross_ratio"]` | Required in this order; no other claim-bearing contrast may cite the registry. |
| `contrasts` | array of exactly two ContrastSpec objects | Required in the same exhaustive order as `contrast_ids`; these are the complete claim-bearing selection opportunity. |
| `planned_manifest_id` | string matching `am-[0-9a-f]{64}` | Required, never null; equals the one permitted manifest's content-derived ID. |
| `planned_manifest_sha256` | 64-character lowercase hexadecimal string | Required, never null; SHA-256 of that manifest's normalized on-disk bytes. |
| `output_identity_gate` | OutputIdentityGate object | Required. |
| `floor_selector` | FloorSelector object | Required. |
| `divergence_disposition` | array of exactly four DivergenceDisposition objects | Required in the state order below. |
| `claim_ceiling` | const string `L2` | Required. |
| `forbidden_upgrade` | non-empty string | Required; forbids generic speculative-decoding, serving, hardware, or quality claims from one pair. |

SamplingPlan:

| Field | Type | Null rule |
|---|---|---|
| `design` | const string `paired_fixed_n` | Required. |
| `planned_n_blocks` | integer >= 2 | Required, never null, and immutable before any dispatch under this registry. Campaign-frozen n is selected from Window-A variance/MDE; a front-frozen mock registry also fixes its mock n. |
| `freeze_basis` | enum `mock_schema_exercise` or `window_a_variance_mde_before_campaign_execution` | Required. The former is required for `front_frozen`; the latter for `frozen`. |
| `allowed_replacement_reasons` | array const `["dispatch_failed_before_bundle_creation","strict_bundle_invalid"]` | Required in this lexicographic order. This is the complete closed technical-invalid reason set; no free-form or successor reason is accepted in v2. |

`front_frozen` is not a mutable precursor to `frozen`. A schema/mock registry
binds one mock manifest, complete contrasts, and a fixed mock n. After Window-A
sizing, claim-bearing work uses a newly authored `*_campaign_v1` registry and
new manifest with fixed campaign n and a bound floor. Neither artifact may be
rewritten in place, and no AP-SPEC bundle may be dispatched until its exact
manifest ID and byte digest are present in the already-frozen registry.
The `*_front_v1` IDs require `front_frozen`, `mock_schema_exercise`, and a
pending floor; the `*_campaign_v1` IDs require `frozen`, the Window-A freeze
basis, and a bound floor. Draft/native IDs require their matching family and
enabled mechanism. Any cross-combination is invalid.

Multiplicity:

| Field | Type | Null rule |
|---|---|---|
| `method` | const string `holm` | Required. |
| `alpha` | number const 0.05 | Required. |
| `q` | null | Required null. |
| `m` | integer const 2 | Required; the primary gross and committed-output companion on/off contrasts. The accepted-draft diagnostic is not an on/off contrast. |

ContrastSpec is exact-keyed:

| Field | Type | Null rule and frozen value |
|---|---|---|
| `contrast_id` | enum `primary_gross_energy` or `committed_output_gross_ratio` | Required and equal to its `contrast_ids` position. |
| `family_id` | one of the two AP-SPEC family IDs | Required and equal to registry `family_id`. |
| `claim_role` | enum `primary` or `companion` | Required: primary for `primary_gross_energy`, companion for `committed_output_gross_ratio`. |
| `estimand_id` | enum `execution_unit_gross_energy` or `gross_per_committed_output_token` | Required and position-matched. |
| `metric` | enum `gross_energy_j`, `batch_group_gross_energy_j`, or `gross_energy_per_committed_output_token_j` | Required. The primary is `gross_energy_j` for `single_request` and `batch_group_gross_energy_j` for `static_batch`; the companion uses the third value. |
| `window_class` | enum `gross_request` or `gross_batch_group` | Required and selected by registry `batch_mode` for both contrasts. |
| `cells` | array const `["spec_off","spec_on"]` | Required in this order. |
| `categories` | array const `["speculation_mode"]` | Required; no outcome-defined subgroup/category is permitted. |
| `models` | ModelScope object | Required, never null, and equal in both contrast rows. |
| `estimator` | enum `paired_mean_of_bundle_differences` or `ratio_of_arm_totals` | Required: paired mean for primary, ratio of totals for companion. |
| `coding` | enum `spec_on_minus_spec_off` or `spec_on_over_spec_off` | Required: difference coding for primary, ratio coding for companion. |
| `alpha` | number const 0.05 | Required. |
| `q` | null | Required null. |
| `multiplicity_method` | const string `holm` | Required. |
| `multiplicity_m` | integer const 2 | Required and equal to the complete `contrast_ids` cardinality. |

ModelScope is exact-keyed. `target_model_artifact_sha256` is lowercase 64-hex;
`enabled_mechanism` is `draft_model` or `native_mtp`; and
`enabled_mechanism_identity_sha256` is lowercase 64-hex over compact canonical
JSON of the complete DraftModelIdentity or NativeMTPIdentity object. All three
fields are required and never null. They MUST equal the off/on configs,
manifest entries, and runtime target/mechanism identities. Thus the contrast
enumerates its models rather than relying on a prose label or permitting a
post-outcome model subset.

These two rows exhaust the permitted claim-bearing contrasts for one registry.
The accepted-draft estimand is a spec-on mechanism diagnostic and therefore
MUST NOT acquire a `contrast_id`, enter Holm `m`, or be selected as a third
on/off contrast after outcomes are observed. A different target, mechanism,
batch mode, metric/window, model subset, estimator, or contrast set requires a
new prospective registry and manifest identity.

PairingPolicy:

| Field | Type | Null rule |
|---|---|---|
| `unit` | const string `bundle_pair_within_block` | Required. |
| `difference_orientation` | const string `spec_on_minus_spec_off` | Required. |
| `required_entry_fields` | array of strings | Required and exactly `pair_id`, `block_id`, `planned_rep_index`, `arm`, `counterpart_entry_id`, `pairing_projection_sha256`, and `request_roster_sha256`. |
| `allowed_config_difference_pointers` | array of strings | Required and exactly the four pointers below. |
| `order_policy` | const string `counterbalanced_within_block` | Required. |

The only config fields allowed to differ within a pair are:

1. `/speculation/mode`
2. `/speculation/max_proposed_tokens`
3. `/speculation/draft_model_identity`
4. `/speculation/native_mtp_identity`

Both configs declare the same extension and event version path. Remove exactly
those pointers, canonicalize the remainder as sorted-key compact UTF-8 JSON,
and SHA-256 it to obtain `pairing_projection_sha256`. The pair is invalid if
the hashes differ. This makes target model, quantization, runtime, telemetry,
prompt/request roster, sampler, output policy, and batch policy identical
without maintaining a second permissive allowlist.

The three Estimand objects have exact keys `estimand_id`, `role`,
`numerator`, `denominator`, `unit`, `aggregation`,
`zero_or_null_rule`, `eligible_arms`, and `contrast_form`. Strings are
non-empty; `denominator` and `contrast_form` may be null only as specified;
`eligible_arms` is a non-empty array of `spec_off`/`spec_on`.

| estimand_id | role | numerator | denominator | unit | aggregation | zero_or_null_rule | eligible_arms | contrast_form |
|---|---|---|---|---|---|---|---|---|
| `execution_unit_gross_energy` | `primary` | `gross_energy_j` iff `single_request`; `batch_group_gross_energy_j` iff `static_batch` | null | `J` | `paired_mean_of_bundle_differences` | `non_null_finite_required` | both arms | `spec_on_minus_spec_off` |
| `gross_per_committed_output_token` | `companion` | same mode-selected gross numerator | `decode_counter_rollup.emitted_count` | `J/committed_output_token` | `ratio_of_arm_totals` | `null_if_arm_denominator_zero` | both arms | `spec_on_over_spec_off_ratio` |
| `gross_per_accepted_draft_token` | `mechanism_diagnostic` | same mode-selected gross numerator | `decode_counter_rollup.tokens_accepted` | `J/accepted_draft_token` | `ratio_of_spec_on_totals` | `null_for_spec_off_or_zero_accepted` | spec-on only | null |

The primary on/off estimand is paired gross energy at the configured execution
unit: request for `single_request`, static batch group for `static_batch`.
Static energy is carried only by `batch_group_gross_energy_j` in the estimand;
no request-scoped name or object may carry it. Gross J per committed output
token is a token-normalized companion. Gross J per accepted draft token is
never substituted as the on/off efficiency denominator.
One registry/manifest instance contains exactly one enabled mode:
`draft_model` or `native_mtp`. The two mechanisms require distinct
registry IDs and contrast families and MUST NOT be pooled into one estimand.

OutputIdentityGate:

| Field | Type | Null rule |
|---|---|---|
| `gate_id` | const string `C-023-OUTPUT-IDENTITY` | Required. |
| `report_schema_version` | const string `joulewise.output_identity_report.v1` | Required. |
| `required_state_for_primary` | const string `exact_token_match` | Required. |
| `tokenizer_identity_rule` | const string `exact_name_revision_and_artifact_sha256` | Required. |
| `text_comparison_rule` | const string `exact_utf8_bytes` | Required. |

FloorSelector:

| Field | Type | Null rule |
|---|---|---|
| `status` | enum `pending_p2_015` or `bound` | Required. |
| `source_artifact_id` | non-empty string or null | Null only while pending; required before live execution. |
| `backend` | non-empty string or null | Null only while pending; when bound, exact telemetry backend/boundary. |
| `metric` | enum `gross_energy_j` or `batch_group_gross_energy_j` | Required and selected by registry `batch_mode`. |
| `window_class` | enum string `gross_request` or `gross_batch_group` | Required and selected by single-request versus static-batch mode. |
| `floor_field` | const string `max(floor_abs_j,floor_cmp_j)` | Required. |
| `condition_family_ids` | array of exactly `spec_off`, `spec_on` | Required. |
| `transport_rule_id` | non-empty string or null | Null only while pending; when bound, names the exact equal-or-harder request-window transport rule. |

No claim-bearing AP-SPEC run starts while the selector is pending. If no
P2-015 cell validly transports to the AP-SPEC request window, a dedicated
calibration cell is required; the analysis reports `not resolvable` rather
than borrowing an easier floor.

DivergenceDisposition objects have exact keys `state`,
`primary_claim_eligible`, `allowed_disposition`, and
`required_wording`. The boolean is never null and both strings are non-empty.
The four frozen rows are:

| state | primary_claim_eligible | allowed_disposition | required wording |
|---|---:|---|---|
| `exact_token_match` | true | `matched_decoded_work` | effect of speculative decoding on matched decoded work |
| `text_match_token_divergent` | false | `text_matched_descriptive_or_predeclared_quality_matched` | exact text matched but tokenizer-level work diverged; no matched-token efficiency claim |
| `output_divergent` | false | `descriptive_only` | outputs diverged; energy difference is not an efficiency contrast on matched work |
| `unassessable` | false | `refuse_efficiency_claim` | output identity could not be established |

A separately predeclared quality-equivalence design may support
quality-matched wording for divergent outputs. It does not change this report
state or retroactively create token identity.

### 9.3 Generic manifest v2

The generated sibling manifest uses
`schema_version: "joulewise.analysis_manifest.v2"` and these exact top-level
keys:

| Field | Type | Null rule |
|---|---|---|
| `schema_version` | const string `joulewise.analysis_manifest.v2` | Required. |
| `manifest_id` | string matching `am-[0-9a-f]{64}` | Required, hash-derived from all other canonical fields. |
| `freeze_status` | `front_frozen` or `frozen` | Required and equal to registry. |
| `registry` | RegistryReference object | Required. |
| `design` | Design object | Required. |
| `request_roster` | RequestRosterReference object | Required. |
| `entries` | non-empty array of Entry objects | Required. |
| `pairs` | non-empty array of Pair objects | Required. |
| `estimands` | exact copy of registry estimands | Required. |
| `contrast_ids` | exact copy of registry `contrast_ids` | Required. |
| `contrasts` | exact copy of registry `contrasts` | Required. |
| `output_identity_gate` | exact copy of registry gate | Required. |
| `floor_selector` | exact copy of registry selector | Required. |

RegistryReference is exact-keyed with required non-null `registry_id` and
relative `path` strings plus `semantic_sha256` as lowercase 64-hex. The
semantic digest is SHA-256 of compact JouleWise canonical JSON for the complete
registry after removing only `planned_manifest_id` and
`planned_manifest_sha256`. This non-cyclic projection includes every design,
selection, n, contrast, metric, gate, floor, and disposition field. Design
fields are:
`design_id: "axi_ap_spec_v1"`, `plan_id: "AP-SPEC"`,
`unit_of_analysis: "bundle_pair_within_block"`,
`difference_orientation: "spec_on_minus_spec_off"`,
`sampling_plan` copied exactly from registry, and
`order_policy: "counterbalanced_within_block"`; none is nullable.

RequestRosterReference is exact-keyed:
`schema_version: "joulewise.request_roster.v1"`, `path` as a non-empty
relative string, and `sha256` as lowercase 64-hex; none is nullable. Its
bytes follow §2.2, and every entry's `request_roster_sha256` equals this
hash.

Entry is exact-keyed:

| Field | Type | Null rule |
|---|---|---|
| `entry_id` | non-empty identifier string | Required, unique. |
| `pair_id` | non-empty identifier string | Required. |
| `block_id` | non-empty identifier string | Required. |
| `planned_rep_index` | integer >= 0 | Required. |
| `arm` | enum `spec_off` or `spec_on` | Required. |
| `counterpart_entry_id` | non-empty identifier string | Required. |
| `config` | non-empty relative path string | Required. |
| `config_sha256` | 64-character lowercase hex | Required. |
| `pairing_projection_sha256` | 64-character lowercase hex | Required and same within pair. |
| `request_roster_sha256` | 64-character lowercase hex | Required and same within pair. |
| `order_index` | integer >= 0 | Required, unique. |

Pair is exact-keyed:

| Field | Type | Null rule |
|---|---|---|
| `pair_id` | non-empty identifier string | Required, unique. |
| `block_id` | non-empty identifier string | Required. |
| `planned_rep_index` | integer >= 0 | Required. |
| `spec_off_entry_id` | non-empty identifier string | Required. |
| `spec_on_entry_id` | non-empty identifier string | Required. |
| `pairing_projection_sha256` | 64-character lowercase hex | Required. |
| `request_roster_sha256` | 64-character lowercase hex | Required. |
| `output_identity_report_id` | null | Required null before execution; the immutable post-execution report links back by manifest/pair ID rather than mutating the frozen manifest. |

Every pair contains exactly one arm of each kind. Counterpart references are
symmetric. The following additional invariants are mandatory:

1. `len(pairs) == registry.sampling_plan.planned_n_blocks`.
2. `len(entries) == 2 * planned_n_blocks`; each pair references exactly two
   entries, one `spec_off` and one `spec_on`, and every entry is referenced by
   exactly one pair.
3. Pair `planned_rep_index` values are unique and exactly the contiguous set
   `0..planned_n_blocks-1`. Both entries in a pair repeat that index and its
   `block_id`; no second pair may share it.
4. Entry `order_index` values are unique and exactly
   `0..(2 * planned_n_blocks)-1`. Counterpart references are reciprocal, and
   pair and entry projection/roster hashes agree.
5. Manifest `contrast_ids` and `contrasts` are byte-for-byte canonical-value
   copies of the registry and exhaust the analysis. Every claim-bearing result
   reports both contrast IDs over all fixed pairs; selecting a subset is
   forbidden.
6. Technical-invalid replacement attempts retain the same manifest entry,
   pair, planned replicate, arm, and config hashes and are recorded in the
   immutable AttemptLedger defined below. They do not add an entry or pair.
7. No outcome, effect estimate, p-value, confidence interval, acceptance rate,
   output divergence, energy value, or floor result may cause an added pair,
   replacement reason, alternate manifest, omitted pair, or “top-up.” The
   original fixed-n result is reported, including unresolved or invalid pairs.

#### 9.3.1 AttemptLedger v1

Each manifest Entry is one fixed analysis **cell**. The campaign writes one
canonical `attempt_ledger.jsonl` artifact with one AttemptLedgerRow for every
dispatch attempt, including attempts that never create a finalized bundle.
Rows are ordered by manifest Entry `order_index`, then `attempt_ordinal`; no
other ordering is valid. Each row is compact canonical JSON with sorted keys,
separators `(",", ":")`, `ensure_ascii=False`, UTF-8 encoding, and one trailing
LF; the ledger bytes are the concatenated rows in that order and their SHA-256
is the ledger identity. AttemptLedgerRow is exact-keyed:

| Field | Type | Null rule and frozen meaning |
|---|---|---|
| `schema_version` | const string `joulewise.attempt_ledger.v1` | Required, never null. |
| `manifest_id` | string matching `am-[0-9a-f]{64}` | Required, never null, and equal to the frozen manifest. |
| `entry_id` | non-empty identifier string | Required, never null; identifies the fixed cell. |
| `pair_id` | non-empty identifier string | Required, never null and equal to the Entry. |
| `arm` | enum `spec_off` or `spec_on` | Required, never null and equal to the Entry. |
| `attempt_ordinal` | integer >= 0 | Required, never null; unique and contiguous from 0 within `entry_id`. |
| `run_id` | non-empty string or null | Non-null iff a finalized run bundle exists for this attempt; null for `dispatch_failed_before_bundle_creation`. |
| `dispatch_receipt_sha256` | 64-character lowercase hexadecimal string | Required, never null; hashes the immutable dispatch receipt naming manifest, entry, arm, attempt ordinal, start status, process/transport status, and admitted-request count. |
| `technical_invalid_reason_code` | enum `dispatch_failed_before_bundle_creation`, `strict_bundle_invalid`, or null | Required key. Non-null only when its predicate below is true. Null means the attempt counts as eligible. |
| `reason_evidence_sha256` | 64-character lowercase hexadecimal string or null | Required key. Equals the dispatch-receipt hash for dispatch failure, the strict-validation-report hash for strict invalidity, and null when the reason code is null. |
| `eligible_for_analysis` | boolean | Required and mechanically derived: false iff a recognized non-null reason code has its predicate satisfied; true otherwise. |

DispatchReceipt is exact-keyed with required, non-null
`schema_version: "joulewise.dispatch_receipt.v1"`, `manifest_id`, `entry_id`,
`pair_id`, `arm`, and integer `attempt_ordinal`; required boolean
`dispatch_started`; `transport_status` enum `ok` or `failed`;
`process_exit_code` as integer or null; `admitted_request_count` as integer >=
0; and `finalized_run_id` as non-empty string or null. The identity fields
equal the AttemptLedgerRow. The receipt is finalized after dispatch handling,
serialized as sorted-key, two-space UTF-8 JSON with one trailing LF, and hashed
as `dispatch_receipt_sha256`.

StrictValidationAttemptEvidence is exact-keyed with required, non-null
`schema_version: "joulewise.strict_validation_attempt_evidence.v1"`, the same
manifest/entry/pair/arm/attempt identity, non-empty `run_id`, lowercase 64-hex
`validated_bundle_sha256`, boolean constant `valid: false`, and a unique lexicographically
sorted non-empty `validator_reason_codes` array of single-bundle validator reason enums.
It uses the same sorted-key/two-space/UTF-8/one-LF serialization; its byte hash
is `reason_evidence_sha256` for `strict_bundle_invalid`.

The only permitted ineligibility predicates are:

| Reason code | Machine-checkable predicate |
|---|---|
| `dispatch_failed_before_bundle_creation` | The hashed DispatchReceipt matches this manifest/entry/arm/attempt, has `dispatch_started == true`, has a nonzero `process_exit_code` or `transport_status == "failed"`, has `admitted_request_count == 0`, has `finalized_run_id == null`, and no finalized run bundle exists; therefore row `run_id` is null and `reason_evidence_sha256 == dispatch_receipt_sha256`. |
| `strict_bundle_invalid` | Row `run_id` names a finalized bundle; DispatchReceipt `finalized_run_id` equals it; and the hashed StrictValidationAttemptEvidence matches this manifest/entry/arm/attempt/run, has `valid == false`, and has a non-empty validator-reason array from single-bundle structural/integrity validation. C-023 state, energy value, effect direction, floor result, latency, throughput, proposal/acceptance rate, and other analysis outcomes are not strict-validation predicates and cannot satisfy this code. |

The closed enum is authoritative. A free-form, misspelled, future, or otherwise
unknown proposed reason is normalized to
`technical_invalid_reason_code: null`, has null reason evidence, and **counts
as eligible**. A recognized code whose predicate is false also counts as
eligible and raises `analysis_attempt_reason_predicate_mismatch`; it never
opens a retry opportunity.

Analysis uses the predeclared deterministic rule
`first_eligible_per_cell`: scan each Entry's rows by ascending
`attempt_ordinal` and consume exactly the first row with
`eligible_for_analysis == true`. Later attempts can never replace that row,
even if they are more favorable. Once a cell has an eligible attempt, any
later dispatch for it remains recorded but raises
`outcome_dependent_topup_forbidden`. If all recorded attempts for a cell
satisfy a permitted technical-invalid predicate, the cell is unresolved until
the next prospectively allowed technical replacement; it is never filled from
another cell or manifest.

Completeness is checked against dispatch receipts, finalized run IDs discovered
under the campaign output, manifest entries, and attempt ordinals. A missing row or receipt, duplicate or
gapped ordinal, misordered row, unrecorded run bundle, row/Entry mismatch, or omission of any
attempt raises the named refusal `analysis_attempt_ledger_gap` and refuses
analysis admission. The finalized ledger byte hash is its analysis-input
identity; the ledger rows are immutable and no selection-time rewrite is
permitted.

Manifest identity is constructed without a hash cycle:

1. compute RegistryReference `semantic_sha256` using the registry projection
   above;
2. construct the complete manifest with that reference and without
   `manifest_id`;
3. set `manifest_id` to `am-` plus SHA-256 of its compact canonical JSON;
4. serialize the complete manifest as sorted-key, two-space UTF-8 JSON with one
   trailing LF and compute its byte SHA-256; and
5. require those two values to equal the registry's already-present
   `planned_manifest_id` and `planned_manifest_sha256` before dispatch.

The registry semantic projection, manifest ID, manifest byte digest, configs,
and RequestRoster are therefore hash-bound before any mock or live AP-SPEC
bundle is dispatched. One registry authorizes exactly one manifest. A
validator raises `AnalysisManifestError` with one of these stable refusal
codes and refuses dispatch and analysis admission:

- `analysis_manifest_identity_mismatch` for an ID, byte digest, semantic
  registry digest, or registry-reference mismatch;
- `analysis_contrast_freeze_mismatch` for a missing, extra, reordered, or
  changed contrast or a multiplicity denominator not equal to the exhaustive
  set;
- `analysis_manifest_cardinality_mismatch` for any planned-n, pair, entry,
  replicate, order, coverage, or counterpart violation;
- `analysis_attempt_ledger_gap` for any missing, extra, duplicate, gapped,
  misordered, or mismatched attempt-ledger evidence;
- `analysis_attempt_reason_predicate_mismatch` for a recognized technical code
  whose frozen predicate is not satisfied; or
- `outcome_dependent_topup_forbidden` for an added/substituted manifest, pair,
  entry, attempt, or selection based on observed outcomes.

These are hard refusals, not exploratory demotions. A new prospective registry
may be authored only before executing the newly scoped campaign; it cannot be
used to rescue, pool, or top up outcomes from the refused campaign.

## 10. C-023-OUTPUT-IDENTITY cross-bundle gate

### 10.1 Separation of duties

Single-bundle strict validation proves count, hash, lifecycle, and output-policy
integrity. It cannot prove that two arms produced the same decoded work.
`joulewise.output_identity_report.v1` is a separate analysis gate that
compares one frozen AP-SPEC pair.

The report's exact top-level fields are:

| Field | Type | Null rule |
|---|---|---|
| `schema_version` | const string `joulewise.output_identity_report.v1` | Required. |
| `report_id` | string matching `oir-[0-9a-f]{64}` | Required, canonical content hash. |
| `manifest_id` | non-empty string | Required. |
| `pair_id` | non-empty string | Required. |
| `spec_off_bundle` | BundleReference object | Required. |
| `spec_on_bundle` | BundleReference object | Required. |
| `config_gate` | ConfigGate object | Required. |
| `target_tokenizer_comparison` | enum `exact_match`, `mismatch`, or `unassessable` | Required and mechanically derived from the two BundleReference identities; never producer-asserted. |
| `requests` | array of RequestComparison objects | Required in roster order; may be empty only when missing/malformed roster evidence prevents construction of a request key, which forces `unassessable`. |
| `overall_state` | one of the four report states | Required. |
| `claim_disposition` | one of `matched_decoded_work`, `text_matched_descriptive_or_predeclared_quality_matched`, `descriptive_only`, or `refuse_efficiency_claim` | Required and mechanically derived. |

The report ID is `oir-` plus SHA-256 of JouleWise canonical JSON for the
complete report with `report_id` removed.

Before that hash is computed, every `reason_codes`,
`missing_evidence_reasons`, and `unexpected_difference_pointers` array is
deduplicated and sorted ascending by Unicode code point. The on-disk report
MUST already use that order; validators reject unsorted or duplicate arrays
rather than silently reordering them. This ordering is part of report identity
and the hand-authored byte goldens.

BundleReference is exact-keyed:

| Field | Type | Null rule |
|---|---|---|
| `run_id` | non-empty string or null | Required key; null iff unavailable and reason `run_id_unavailable` is present. |
| `config_sha256` | 64-character lowercase hexadecimal string or null | Required key; null iff unavailable and reason `config_sha256_unavailable` is present. |
| `requests_artifact_sha256` | 64-character lowercase hexadecimal string or null | Required key; null iff missing/malformed and reason `requests_artifact_unavailable` is present. |
| `request_tokens_artifact_sha256` | 64-character lowercase hexadecimal string or null | Required key; null iff missing/malformed and reason `request_tokens_artifact_unavailable` is present. |
| `summary_sha256` | 64-character lowercase hexadecimal string or null | Required key; null iff missing/malformed and reason `summary_artifact_unavailable` is present. |
| `strict_validation_state` | enum `valid`, `invalid`, or `unavailable` | Required and derived from the single-bundle strict-validation report. Only `valid` satisfies the C-023 precondition. |
| `strict_validation_report_sha256` | 64-character lowercase hexadecimal string or null | Required key; non-null for `valid` or `invalid`; null iff state is `unavailable` and reason `strict_validation_report_unavailable` is present. |
| `target_tokenizer_identity` | TargetTokenizerIdentity object or null | Required key; exact copy of `metadata.runtime.target_tokenizer_identity` when valid, otherwise null with reason `target_tokenizer_identity_unavailable`. |
| `missing_evidence_reasons` | array of unique MissingEvidenceReason values | Required, lexicographically sorted, and empty iff none of this reference's fields is missing. |

ConfigGate exact fields:

| Field | Type | Null rule |
|---|---|---|
| `allowed_difference_pointers` | exact four-string array from §9.2 | Required. |
| `spec_off_projection_sha256` | 64-hex string or null | Required key; null when projection evidence is unavailable. |
| `spec_on_projection_sha256` | 64-hex string or null | Required key; null when projection evidence is unavailable. |
| `projections_equal` | boolean or null | Required key; null unless both projections are available. |
| `unexpected_difference_pointers` | array of unique strings | Required and lexicographically sorted by Unicode code point; empty when equal or comparison is unavailable. |
| `missing_evidence_reasons` | array of unique MissingEvidenceReason values | Required and lexicographically sorted; contains `config_projection_unavailable` iff either projection hash or the comparison is null. |

Any unexpected config difference or unavailable projection sets overall state
`unassessable` and disposition `refuse_efficiency_claim`, regardless of
coincidentally matching output.

RequestComparison exact fields:

| Field | Type | Null rule |
|---|---|---|
| `request_ordinal` | integer >= 0 or null | Required key; null iff reason `request_roster_key_unavailable` is present. |
| `request_input_id` | non-empty identifier string or null | Required key; null iff reason `request_roster_key_unavailable` is present. |
| `spec_off_request_id` | non-empty string or null | Required key; null with reason `spec_off_request_id_unavailable`. |
| `spec_on_request_id` | non-empty string or null | Required key; null with reason `spec_on_request_id_unavailable`. |
| `spec_off_token_ids_sha256` | 64-hex string or null | Required key; null iff reason `spec_off_token_ids_unavailable` is present. |
| `spec_on_token_ids_sha256` | 64-hex string or null | Required key; null iff reason `spec_on_token_ids_unavailable` is present. |
| `spec_off_text_sha256` | 64-hex string or null | Required key; null iff reason `spec_off_response_text_unavailable` is present. |
| `spec_on_text_sha256` | 64-hex string or null | Required key; null iff reason `spec_on_response_text_unavailable` is present. |
| `output_token_count_equal` | boolean or null | Required key; null iff reason `output_count_comparison_unavailable` is present. |
| `stop_reason_equal` | boolean or null | Required key; null iff reason `stop_reason_comparison_unavailable` is present. |
| `state` | one of the four report states | Required. |
| `missing_evidence_reasons` | array of unique MissingEvidenceReason values | Required and lexicographically sorted. Each nullable field has its corresponding reason iff null. |
| `reason_codes` | array of unique enum strings | Required, lexicographically sorted by Unicode code point; may be empty only for exact match. |

MissingEvidenceReason is one closed enum shared by BundleReference,
ConfigGate, and RequestComparison:
`config_projection_unavailable`, `config_sha256_unavailable`,
`output_count_comparison_unavailable`, `request_roster_key_unavailable`,
`request_tokens_artifact_unavailable`, `requests_artifact_unavailable`,
`run_id_unavailable`, `spec_off_request_id_unavailable`,
`spec_off_response_text_unavailable`, `spec_off_token_ids_unavailable`,
`spec_on_request_id_unavailable`, `spec_on_response_text_unavailable`,
`spec_on_token_ids_unavailable`,
`stop_reason_comparison_unavailable`, `strict_validation_report_unavailable`,
`summary_artifact_unavailable`, and
`target_tokenizer_identity_unavailable`. The enum spelling and this
lexicographic order are frozen. An object includes only applicable values, but
every null that represents missing evidence has exactly one applicable value;
unknown/free-form missing-evidence reasons are invalid.

Reason codes are frozen in lexicographic enum order:
`output_count_differs`, `request_roster_mismatch`,
`response_text_differs`, `response_text_unavailable`,
`single_bundle_invalid`, `stop_reason_differs`,
`target_tokenizer_identity_mismatch`,
`target_tokenizer_identity_unavailable`, `token_ids_differ`,
`token_ids_unavailable`, and `unexpected_config_difference`.

### 10.2 State algorithm

Target-tokenizer comparison uses the stack-identity evidence in each
BundleReference, never an asserted equality boolean:

- `exact_match` iff both TargetTokenizerIdentity objects are present and their
  `name`, `revision`, and `tokenizer_artifact_sha256` strings are pairwise
  byte-equal;
- `mismatch` iff both objects are present and valid but any of those three
  strings differs; and
- `unassessable` iff either object is null or malformed.

There is no case folding, alias resolution, revision-prefix matching, Unicode
normalization, display-name fallback, or config-only fallback. The artifact
hash plus exact name/revision is the comparator identity.

Missing evidence is mapped mechanically into request reason codes: a bundle
strict-validation state other than `valid` adds `single_bundle_invalid`; either
target-tokenizer identity missing adds
`target_tokenizer_identity_unavailable`; either token sequence missing adds
`token_ids_unavailable`; either response text missing adds
`response_text_unavailable`; a missing roster key adds
`request_roster_mismatch`; and any other field required for a request
comparison adds `single_bundle_invalid`. Tokenizer `mismatch` adds
`target_tokenizer_identity_mismatch`; config projection unequal or unavailable
adds `unexpected_config_difference`. The resulting array is then sorted by the
canonical rule above.

First, if either bundle is not strict-valid, roster pairing fails, the config
projection is not exactly true, or target-tokenizer comparison is `mismatch`
or `unassessable`, the affected request and overall comparison are
`unassessable`. Otherwise apply this ordered per-request classifier:

1. If stop reasons differ, return `output_divergent`.
2. If both exact response-text hashes are available and differ, return
   `output_divergent`.
3. If both exact response-text hashes are available and equal:
   - if both complete token-sequence hashes are available and equal, require
     equal output counts (strict-valid evidence makes a mismatch internally
     impossible) and return `exact_token_match`;
   - if both complete token-sequence hashes are available and differ, return
     `text_match_token_divergent` **whether the token counts are equal or
     different**; and
   - if either token sequence is unavailable, return `unassessable`.
4. If either exact text hash is unavailable but both complete token sequences
   are available and equal with equal counts, return `exact_token_match`.
5. Otherwise return `unassessable`; in particular, unequal token sequences
   without complete text cannot establish whether decoded text matched.

`output_token_count_equal` is required report evidence and adds reason code
`output_count_differs` when false, but a count difference alone is not the
definition of `output_divergent`. Exact equal text plus different complete
token sequences is tokenization divergence even when the sequences have
different lengths. The mechanical edge table is:

| Strict/roster/config/target-tokenizer preconditions | Exact text evidence | Complete token evidence | Counts | Stops | State |
|---|---|---|---|---|---|
| fail | any | any | any | any | `unassessable` |
| pass | equal | equal | equal | equal | `exact_token_match` |
| pass | equal | different | equal | equal | `text_match_token_divergent` |
| pass | equal | different | **different** | equal | `text_match_token_divergent` |
| pass | different | any | any | equal | `output_divergent` |
| pass | any | any | any | different | `output_divergent` |
| pass | equal | unavailable | any | equal | `unassessable` |
| pass | unavailable | equal | equal | equal | `exact_token_match` |
| pass | unavailable | different or unavailable | any | equal | `unassessable` |

The combination “equal complete token sequence, different count” contradicts
single-bundle strict-valid evidence and is handled by the precondition failure,
not assigned a fifth report state.

Request comparisons are joined by the frozen
`(request_ordinal, request_input_id)` roster key. Runtime `request_id`
values are reported for audit and may differ across bundles; they are never
used as the cross-bundle join key.

Global precondition failure or an empty `requests` array sets overall state
`unassessable` before request-state precedence. Otherwise, overall state is
`output_divergent` if any request diverges; otherwise
`unassessable` if any request is unassessable; otherwise
`text_match_token_divergent` if any request has that state; otherwise every
request is exact and overall state is `exact_token_match`.

Only overall `exact_token_match` passes the clean claim gate for “effect of
speculative decoding on matched decoded work.” All other dispositions follow
the frozen AP-SPEC table and remain visible in the report.

## 11. Exact contract amendment ledger

This section is the implementation edit script. “Old” text is quoted
verbatim from the current contract at the base head. “Replacement” is the
exact language to land. Additions that do not replace a clause are labeled
explicitly.

### 11.1 `docs/contracts/token_normalization.md`

#### TN-1 — replace the complete Primary Metric body

Old (lines 18-31):

> Request energy is the PRIMARY reader-facing energy metric.
>
> Request energy means idle-subtracted joules per request under a named
> measurement boundary. The boundary label is part of the metric identity, not
> caption garnish.
>
> Per-token metrics never replace request energy in a headline. They may appear
> as companion metrics when their tokenizer scope and denominator provenance are
> explicit.
>
> A headline means the primary reader-facing figure or table and any
> abstract-level claim, not only the title. In any reader-facing figure or
> table containing token-normalized metrics, request energy must be co-displayed
> with equal or greater salience.

Replacement (exact):

> Request energy is the PRIMARY reader-facing energy metric.
>
> Request energy means gross joules per request under a named measurement
> boundary. The basis and boundary labels are parts of the metric identity, not
> caption garnish. Gross energy retains idle, model-residency, and runtime
> overhead inside the measured interval and is the headline basis for every
> cross-device, cross-configuration, and split-versus-monolithic claim.
>
> Idle-subtracted joules per request remain a clearly labeled within-device
> secondary view of activity above the measured idle baseline. They are never
> used to rank devices or configurations. The stored historical field
> `energy_request_j` is not renamed or redefined; reader-facing gross request
> energy is `gross_energy_j`.
>
> Per-token metrics never replace gross request energy in a headline. They may
> appear as companion metrics when their tokenizer scope, energy basis, and
> denominator provenance are explicit.
>
> A headline means the primary reader-facing figure or table and any
> abstract-level claim, not only the title. In any reader-facing figure or
> table containing token-normalized metrics, gross request energy must be
> co-displayed with equal or greater salience. Every reported energy number
> states its basis and boundary; any cross-configuration number is gross-first.

This is the D-067 alignment. It changes reporting authority, not stored field
identity or sealed bundles.

#### TN-2 — replace the runtime-observed denominator bullet

Old (lines 41-43):

> - Per-token denominators must be runtime-observed token counts. This is the
>   D-037 claims-ladder rider; use `docs/contracts/claims_ladder.md` Global
>   Rules as the downgrade authority rather than restating it here.

Replacement (exact):

> - Per-token denominators must be runtime-observed token counts. Committed
>   output tokens and accepted draft/MTP tokens are distinct denominators and
>   must never be substituted for one another. For speculative-on/off
>   efficiency, gross joules per committed output token is the companion
>   denominator; gross joules per accepted draft token is a speculation-enabled
>   mechanism-yield diagnostic only and is undefined for spec-off. This is the
>   D-037 claims-ladder rider; use `docs/contracts/claims_ladder.md` Global
>   Rules as the downgrade authority rather than restating it here.

#### TN-3 — replace the batching/concurrency stack-identity row

Old (line 105):

> | Batching/concurrency policy | Always applicable: state explicit batch size/concurrency policy, `single-request sequential`, or `unavailable`. | Runtime adapter metadata, serving-stack configuration, run orchestration metadata, or explicit `unavailable` when not captured. |

Replacement (exact):

> | Batching/concurrency policy | Always applicable: state configured and realized batch size separately; mode, admission, synchronization, and dispatch policy; and `single-request` or explicit `unavailable`. Static batch-group identity and required-nullable scheduler-step identity never replace request identity. | Normalized `config.json.batch_policy`; `metadata.batch`; request-scoped `events.jsonl` metadata; or explicit `unavailable` only for historical compatibility. |

#### TN-4 — add burst/speculation companion rules after the existing J/Token requirements

Addition (exact):

> Burst-decode bundles use the counter meanings and null rules frozen by
> `docs/specs/axi/sa_burst_decode_contract.md`. Acceptance rate is the ratio
> of aggregate accepted to aggregate proposed tokens, never a mean of local
> rates, and is null when proposal total is zero. Spec-off proposal,
> acceptance, and acceptance-rate fields are null rather than zero.
>
> `inter_token_throughput_tokens_s` is eligible only when every committed
> output token in scope has a genuine per-token runtime timestamp. Burst-safe
> decode-phase output throughput and emission/burst metrics use their new names
> and must not be reported under either frozen throughput name.

#### TN-5 — add the static-batch group-gross naming boundary

Addition (exact):

> For an event-semantics-v2 static batch, the energy analysis unit is the
> complete batch group and its governed gross metric is
> `batch_group_gross_energy_j` on window class `gross_batch_group`. It must not
> appear in a request-scoped object or under a request-energy estimand name, and
> trace energy must not be divided among overlapping requests. Single-request
> gross energy remains `gross_energy_j` on `gross_request`.

#### TN-6 — add the event-v2 target-tokenizer evidence rule

Addition after the Tokenizer identity stack-identity row (exact):

> Event-semantics-v2 bundles record the actually loaded target tokenizer at
> `metadata.runtime.target_tokenizer_identity` with exact name, immutable
> revision, and `tokenizer_artifact_sha256`. C-023 compares all three strings
> byte-for-byte; it performs no case folding, alias resolution, revision-prefix
> matching, Unicode normalization, display-name fallback, or config-only
> fallback. Missing or malformed runtime identity is unassessable, never an
> asserted equality.

### 11.2 `docs/contracts/run_bundle_layout.md`

#### RB-1 — extend normalized-config identity without consuming v0.2

Old (lines 61-66):

> The bundle stores the normalized config as sorted-key JSON (`config.json`);
> its SHA-256 hash is recorded in `metadata.config_sha256` and identifies the
> configuration in later aggregation. Default bundle validation recomputes the
> SHA-256 over the on-disk `config.json` bytes and rejects a missing or
> mismatched `metadata.config_sha256`. Rationale and alternatives: decision
> D-001 in `docs/decision_log.md` (YAML input timing is D-007).

Replacement (exact):

> The bundle stores the normalized config as sorted-key JSON (`config.json`);
> its SHA-256 hash is recorded in `metadata.config_sha256` and identifies the
> configuration in later aggregation. Default bundle validation recomputes the
> SHA-256 over the on-disk `config.json` bytes and rejects a missing or
> mismatched `metadata.config_sha256`. AXI request/burst configs remain base
> schema `0.1` and declare scoped extension
> `joulewise.axi_decode_config.v1`; their typed `batch_policy` and
> `speculation` objects are normalized identity. The extension is absent from
> non-AXI configs and does not consume config schema `0.2`, which remains
> reserved for split runs. Rationale and alternatives: decision D-001 in
> `docs/decision_log.md` (YAML input timing is D-007).

#### RB-2 — extend the output directory shape

Old (lines 55-58):

>   outputs/
>     response.txt
>     tokens.jsonl
>     suite_items.jsonl        (suite runs only)

Replacement (exact):

>   outputs/
>     response.txt             (historical/B=1 compatibility)
>     tokens.jsonl             (historical/B=1 compatibility)
>     requests.jsonl           (event semantics v2)
>     request_tokens.jsonl     (event semantics v2)
>     suite_items.jsonl        (suite runs only)

#### RB-3 — replace the metadata minimum sentence

Old (lines 106-109):

> - `metadata.json`: a JSON object containing device, runtime, telemetry,
>   model, environment, clock, `config_sha256`, rail-manifest metadata, and
>   optional workload provenance. Valid JSON with any non-object top-level
>   shape is invalid in default validation.

Replacement (exact):

> - `metadata.json`: a JSON object containing device, runtime, telemetry,
>   model, environment, clock, `config_sha256`, rail-manifest metadata, and
>   optional workload provenance. Event-semantics-v2 bundles additionally
>   require top-level `event_semantics_version: "joulewise.events.v2"`,
>   typed `batch`, and typed `speculation` objects under
>   `docs/specs/axi/sa_burst_decode_contract.md`, plus non-null
>   `runtime.primary_source_identity` and
>   `runtime.target_model_artifact_sha256`, plus exact-keyed
>   `runtime.target_tokenizer_identity` with loaded tokenizer name, immutable
>   revision, and artifact hash. The source field binds the primary runtime
>   phase/telemetry source; the target hashes are produced from actually loaded
>   artifacts rather than config assertions. Event semantics is an
>   independent bundle metadata version and is not config schema `0.2`.
>   Valid JSON with any non-object top-level shape is invalid in default
>   validation.

#### RB-4 — replace the event artifact description

Old (lines 163-164):

> - `events.jsonl`: timestamped lifecycle, phase, token, transfer, and failure
>   events.

Replacement (exact):

> - `events.jsonl`: timestamped lifecycle, phase, token, decode-emission,
>   transfer, and failure events. Historical token events are singleton
>   emissions. Event semantics v2 adds one request-scoped
>   `decode_emission` record per completed request decode step and never
>   encodes multiple requests in one event.

#### RB-5 — replace the output-token event paragraphs

Old (lines 227-236):

> Output-token events are records with `event_type: "token"` in the `decode`
> phase. Prompt-side token provenance is recorded in `metadata.json`
> (`workload_provenance.prompt`) and must not be counted as output-token
> runtime evidence. When decode phase windows are present, output-token events
> used by reduction must fall inside a decode window.
> For single-prompt runs, `outputs/tokens.jsonl` rows may include additive
> `token_id` fields, and `metadata.workload_provenance.response.emitted_token_ids`
> records the emitted output token IDs in order when the runtime exposes them.
> For fixed-budget-exact single runs, the row, token-event, and emitted-token-ID
> counts are strict evidence and must equal the policy's `emitted_tokens`.

Replacement (exact):

> Under historical event semantics, output-token events remain records with
> `event_type: "token"` in the `decode` phase and each record means exactly
> one output token. They are never reinterpreted as burst counts.
>
> Event semantics v2 adds `event_type: "decode_emission"`: one request's one
> completed decode step with request ID, request-local event and decode-step
> ordinals, RequestRoster hash, explicit source identity,
> committed/proposed/accepted/target counts, and required-nullable token
> IDs/hash keys inside the existing `metadata` object. Required-nullable batch-group and
> scheduler-step IDs never replace request ID. When genuine per-token callbacks
> exist, singleton token events accompany the decode-emission event and carry
> request/output ordinals plus timestamp provenance; reducers count output from
> decode-emission records and use singleton token records only as timestamp/ID
> evidence.
>
> Every admitted v2 request has one terminal event with an explicit realized
> output count. Enabled proposal work cancelled before any output uses terminal
> state `cancelled_after_proposal_before_output` and retains its positive
> proposal counter in the terminal record; it is never collapsed to zero. Each
> observed proposal count is validated against configured
> `max_proposed_tokens`.
>
> Prompt-side token provenance is recorded in `metadata.json`
> (`workload_provenance.prompt`) and must not be counted as output-token
> runtime evidence. V2 output evidence is request-indexed in
> `outputs/requests.jsonl` and `outputs/request_tokens.jsonl`; all emission,
> artifact, stop-reason, policy, and required-nullable token-ID evidence must agree under
> `docs/specs/axi/sa_burst_decode_contract.md`.

#### RB-6 — replace phase pairing and energy paragraphs

Old (lines 243-264):

> Phase pairing and validation are one fail-closed operation shared by strict
> bundle validation, phase-energy attribution, and decode-token filtering. A
> pairing key is the phase name plus its phase-stream identity. Stream identity
> uses each non-null `metadata.node_id` and `metadata.node_identity` value. When
> neither is present, a non-null `metadata.node_role` is the stream identity, so
> role-only split markers remain distinct. Values are compared as canonical JSON
> so structured node identities remain stable. Markers with no node role or
> identity all belong to one default stream. A start and end must have the same
> full key. Unmatched starts or ends and reversed bounds invalidate the bundle
> and reduction with an explicit phase-marker reason.
>
> Phase energy is integrated separately per valid window and contributions with
> the same phase name are summed. Windows attributed to distinct identified
> nodes may overlap because each node has its own meter/source, so 2 W over
> `[1,3]` on one node plus 2 W over `[2,4]` on another legitimately sums to 8 J.
> Windows attributed to the same phase stream must not overlap, even when their
> phase names differ: overlap is marker corruption and fails closed with the
> named reason `same_source_phase_overlap`; it is never silently unioned (the
> union in the same 2 W example would be 6 J). Boundary-touching intervals are
> allowed. If any decode windows exist, a decode token is eligible only when its
> timestamp falls in a decode window with the token's same source identity;
> legacy bundles with no decode windows retain the event-only fallback.

Replacement (exact):

> Phase pairing and validation are one fail-closed operation shared by strict
> bundle validation, phase-energy attribution, and decode-token filtering.
> Historical reducer arms retain the existing phase-name plus phase-stream
> identity key and sum semantics exactly.
>
> For event semantics v2, the pairing key is source identity, request ID, phase,
> and request-phase ordinal. The producer persists a non-null
> `metadata.source_identity` resolved using the existing node-ID,
> node-identity, node-role, then default precedence; v2 reduction does not
> reconstruct it. Start and end must have the
> same full key; unmatched/reversed markers fail closed. Equal timestamps across
> requests and arbitrarily overlapping request windows are allowed. No
> validator requires shared prefill or decode boundaries.
>
> V2 group phase energy unions all request intervals for the same source and
> phase before integrating, so synchronized duplicate request windows are
> integrated once, not summed B times. Energy is summed only across distinct
> identified source/meter streams. The reducer does not divide overlapping
> trace energy among requests. Complete rules and overlap invariants are in
> `docs/specs/axi/sa_burst_decode_contract.md`.

#### RB-7 — replace reducer compatibility paragraph

Old (lines 477-489):

> Reducer `0.5.0` summaries use exact strict comparison except for the absence of
> `idle_baseline.gpu_freq_mhz_mean`, which was added during the already-live
> 0.5.0 era. Its absence is tolerated only for compatibility with stored
> pre-repair 0.5.0 summaries; when present, its value is compared exactly. All
> current-era summaries declaring reducer `0.4.1` or `0.4.2` are strictly
> re-derived through their frozen v1 unweighted idle estimator arm; they are
> never compared with relabelled v2 numbers. Their era-specific additive field
> absences remain tolerated, while present claims compare exactly. Reducer
> `0.4.0`, `0.3.x`, recorded `0.2.x`, and unknown reducer versions are
> unsupported and require explicit re-reduction. The frozen meanings are not
> rewritten.
> The six frozen legacy identities keep their provenance-less additive-absence
> tolerance unchanged.

Replacement (exact):

> Reducer dispatch occurs before event, phase, token, or idle interpretation.
> Reducer `0.6.0` is the request/burst arm and requires
> `metadata.event_semantics_version: "joulewise.events.v2"`. It uses
> request-indexed outputs, request-keyed phase pairing, unioned group windows,
> and the burst-safe metrics frozen by
> `docs/specs/axi/sa_burst_decode_contract.md`.
>
> Reducer `0.5.0` is frozen on the historical event path and duration-weighted
> idle-v2 formulas. Its code path, derived output, and current era-aware
> comparison behavior remain unchanged, including its existing treatment of
> absent `idle_baseline.gpu_freq_mhz_mean`. Reducers `0.4.1` and `0.4.2` retain
> their current v1 unweighted-idle code paths, derived outputs, historical event
> interpretation, and current era-aware tolerated-absence sets unchanged. No
> historical arm adds tolerance for 0.6.0-only fields, and no 0.6.0 field enters
> its SummaryMetrics path.
>
> Preservation is proved by independently hand-authored, hand-checked goldens
> transcribed from current behavior for each old arm. This guarantees existing
> arms' code paths and outputs are unchanged; it does not claim that fresh
> re-reduction of every historical summary is byte-identical. A versioned
> serializer and canonical byte goldens apply only to new reducer 0.6.0 output.
>
> Reducer `0.4.0`, `0.3.x`, recorded `0.2.x`, unknown versions, and
> incoherent reducer/event-version pairs are unsupported and require an
> explicitly compatible re-reduction. Historical event bundles cannot acquire
> burst semantics by re-reduction. The frozen meanings are not rewritten. The
> six frozen legacy identities keep their provenance-less additive-absence
> tolerance unchanged.

#### RB-8 — replace the inter-token summary-field row

Old (line 503):

> | `inter_token_throughput_tokens_s` | `summary_metrics.json` top level and aggregate metric entries | Governed steady-state decode/inter-token throughput: `(N - 1) / (t_last - t_first)`, where N is the runtime-observed output-token count and the timestamps are the first and last observed decode-token events. It is null when N is below two, fewer than two decode timestamps exist, or their span is zero. The frozen legacy `throughput_tokens_s` remains `N / (t_last - t_first)`: it counts N tokens across N−1 inter-token intervals, is retained for compatibility, and must not be relabeled as steady-state throughput. |

Replacement (exact):

> | `inter_token_throughput_tokens_s` | `summary_metrics.json` top level and aggregate metric entries | Governed steady-state decode/inter-token throughput: `(N - 1) / (t_last - t_first)`, where N is the runtime-observed output-token count and the timestamps are the first and last genuine per-token runtime callbacks. For event-semantics-v2 it retains this singleton-stream identity and is null for realized B>1. For B=1 it is null when N is below two, any committed token lacks a genuine per-token timestamp, fewer than two timestamps exist, or their span is zero. A burst event timestamp is never expanded into per-token timestamps. The frozen legacy `throughput_tokens_s` remains `N / (t_last - t_first)`: it counts N tokens across N−1 inter-token intervals, is retained for compatibility, and must not be relabeled as steady-state throughput. Burst-safe decode-phase output throughput and emission/burst metrics use new names from `docs/specs/axi/sa_burst_decode_contract.md`. |

#### RB-9 — add v2 output and summary clauses

Addition after the suite-output clause (exact):

> Event-semantics-v2 bundles use
> root-level `request_roster.json` as the normalized, hash-bound configured
> request roster and
> `outputs/requests.jsonl` and `outputs/request_tokens.jsonl` as immutable,
> request-indexed output evidence. Their exact schemas, lifecycle completeness,
> counter rollups, token-ID hash domain, and compatibility-mirror rules are
> frozen in `docs/specs/axi/sa_burst_decode_contract.md`. Configured and
> realized batch size are distinct explicit fields and neither is inferred from
> event count.

Addition after the governed summary table (exact):

> Reducer 0.6.0 succeeded summaries add request/burst counter rollups, gross
> energy per committed output token, `batch_group_gross_energy_j` for static
> batches, the spec-only gross energy per accepted
> draft token diagnostic, decode-phase output throughput, emission-event rate,
> burst-size distribution, and request decode metrics. Exact names, formulas,
> types, null/censoring rules, and the prohibition on per-request trace-energy
> division are frozen in
> `docs/specs/axi/sa_burst_decode_contract.md`. Existing metric names retain
> their historical identities. Static-batch gross energy is governed by
> `window_evidence_precheck.gross_batch_group`; it is not relabeled
> `gross_request`.

### 11.3 `docs/contracts/analysis_plans.md`

#### AP-0 — replace the metric/window-class requirement

Old (line 24):

> | Metric + exact window class | Metric name and exact window class: gross request, idle-subtracted request, phase window, item window, level window, or session window. |

Replacement (exact):

> | Metric + exact window class | Metric name and exact window class: gross request, idle-subtracted request, static-batch gross group, phase window, item window, level window, or session window. A static-batch group is not relabeled as a request, and request windows within an overlapping group carry no per-request energy attribution. |

#### AP-1 — replace the standing throughput rule

Old (lines 92-96):

> - Reader-facing steady-state decode-throughput claims use
>   `inter_token_throughput_tokens_s`, the N−1 inter-token-interval convention.
>   The frozen `throughput_tokens_s` N-over-span convention is retained only
>   for compatibility and explicitly labeled legacy wherever reported; it is
>   not eligible to stand in for the governed inter-token metric.

Replacement (exact):

> - Reader-facing steady-state decode-throughput claims use
>   `inter_token_throughput_tokens_s`, the N−1 inter-token-interval convention,
>   only when every committed output token in scope has a genuine per-token
>   runtime timestamp. If any burst lacks individual timestamps, that metric is
>   null. The frozen `throughput_tokens_s` N-over-span convention is retained
>   only for compatibility and explicitly labeled legacy wherever reported; it
>   is not eligible to stand in for the governed inter-token metric.
>   Request/burst bundles instead report the separately named decode-phase
>   committed-output throughput, emission-event rate, and burst-size
>   distribution defined by
>   `docs/specs/axi/sa_burst_decode_contract.md`.

#### AP-2 — add the AP-SPEC row without editing AP-2

No AP-2 clause is replaced. Add a new sibling seeded-plan section using this
exact field/value text:

> ### AP-SPEC: matched-output speculative-decode contrast
>
> | Field | Value |
> |---|---|
> | Plan ID / RQ consumer | AP-SPEC / C5-2.5 plus C-023-OUTPUT-IDENTITY; speculative-on versus speculative-off under matched output policy and exact config projection. |
> | family_id | One separately frozen family per mechanism: `FAM-AXI-SPEC-DRAFT-MATCHED-OUTPUT` or `FAM-AXI-SPEC-NATIVE-MTP-MATCHED-OUTPUT`; never pooled. |
> | claim_role | primary |
> | selection_scope | One frozen target stack, request roster, sampler/output policy, batch policy, paired spec-off/spec-on configuration, manifest digest, planned n, and exhaustive contrast-ID set; only the four speculation config pointers frozen by the AXI-SA contract may differ. |
> | multiplicity_rule | Holm at alpha 0.05 across the primary paired execution-unit gross-energy contrast and gross-per-committed-output-token companion; accepted-draft energy is a spec-on mechanism diagnostic, not an on/off contrast. |
> | Metric + exact window class | Primary `gross_energy_j` on `gross_request` for single-request mode or `batch_group_gross_energy_j` on `gross_batch_group` for static-batch mode; companion `gross_energy_per_committed_output_token_j`; diagnostic `gross_energy_per_accepted_draft_token_j` for spec-on only. Static group energy is never stored or analyzed under a request-scoped name. |
> | Unit of analysis + dependence structure | Paired bundle within counterbalanced block. Static B>1 energy is group-gross; request events provide latency/count/output evidence and are not independent energy replicates. |
> | Estimator/formula | Primary mean of paired `spec_on - spec_off` execution-unit gross-energy differences. Token companions use ratio of arm totals, never mean request/event ratios. |
> | Inclusion/exclusion + quality-flag waiver rules | Strict-valid event-semantics-v2 bundles only; exact config-projection match and a C-023 output-identity report are mandatory. Ordinary D-014/D-037 exclusions apply. |
> | Order/blocking/covariates | Counterbalanced on/off order within frozen blocks; pair ID, block ID, planned replicate, request roster, and counterpart entry are manifest-bound. |
> | Floor gate | pending-P2-015: `max(floor_abs_j, floor_cmp_j)` for the same `gross_request` or `gross_batch_group` window under an explicit equal-or-harder transport rule; otherwise a dedicated calibration cell is required. |
> | MDE/n sizing + predeclared top-up rule | Every v2 registry freezes non-null paired n and binds exactly one manifest ID and byte digest before dispatch. A front-frozen mock registry fixes its mock n; after Window-A variance/MDE, a new campaign-frozen registry fixes claim-bearing n. The manifest has exactly n pairs, 2n entries, and contiguous unique replicate indices. The closed technical-invalid set is `dispatch_failed_before_bundle_creation` and `strict_bundle_invalid`, each with the AXI-SA predicate; unknown reasons count eligible. Every attempt is ledgered, and analysis uses first-eligible-per-cell by ascending attempt ordinal. Any outcome-dependent added/substituted pair, manifest, attempt selection, or retry after eligibility is refused as `outcome_dependent_topup_forbidden`; AP-SPEC permits no post-hoc top-up or pair subset. |
> | Denominator provenance requirement | Runtime-observed committed output tokens for the on/off companion; runtime-observed accepted draft/MTP tokens for the spec-on diagnostic. Spec-off accepted-token denominator is null, never zero. |
> | Holdout cells (L3 only) | not applicable. |
> | Claim ceiling + exact forbidden upgrade | Ceiling L2. Forbidden upgrade: no generic speculative-decoding, serving, hardware, or quality conclusion from one stack/pair; no matched-decoded-work claim unless output state is `exact_token_match`. |
> | Disqualifiers + not-resolvable conditions | Output state other than exact token match, unexpected config difference, missing request evidence, pending/invalid floor selector, below-floor effect, zero committed denominator, or missing counter instrumentation forces the frozen divergence disposition, `not resolvable`, or L0/L1 wording. |
> | Linked manifests/bundle hashes | Registry `planned_manifest_id` and `planned_manifest_sha256`, the complete contrast-ID set, registry semantic digest, configs, and roster are hash-bound before any mock or live AP-SPEC dispatch; the canonical complete attempt-ledger hash, bundle hashes, and immutable execution/report links are filled post-execution without mutating the manifest. |

The implementation MUST prove that adding this section and v2 sibling code
does not alter AP-2 v1 registry bytes or generated-manifest bytes.

## 12. Staged implementation and verification plan

Each stage lands as a bounded review unit with focused tests green. Stages do
not create live claims and do not consume a quiet-machine window.

Every named stage MUST have an independent, hand-authored golden oracle for
the bytes or values it claims to verify. “Hand-authored” means the expected
artifact/formula was written and reviewed independently of the producer,
writer, reducer, validator, schema exporter, or mock under test. Capturing a
producer's output and approving it without independent field-by-field and
formula review is forbidden. Producer-generated fixtures and round-tripping an
artifact through the same implementation are supplemental smoke checks, never
the landing oracle.

### Stage 0 — front-freeze analysis identity first

Implement the sibling generic registry/manifest types, add the AP-SPEC
front-frozen registry, land the exact contract amendments in §11, and pin AP-2
v1 byte identity. Do not implement a speculative adapter yet.

Required tests:

- v2 registry exact-key/type/null validation, including all negative enum and
  cross-field cases;
- v2 manifest canonical ID/byte digest binding, exhaustive contrast copy,
  planned-n cardinality, counterpart symmetry, projection hash, roster hash,
  and front-frozen versus frozen n/floor rules;
- all three estimands' numerator/denominator/aggregation/zero rules;
- refusal-code goldens for manifest identity, contrast, cardinality, and
  outcome-dependent top-up violations;
- AttemptLedger exact schema, closed two-code predicates, complete contiguous
  ordinals, unknown-reason-counts-eligible behavior,
  `first_eligible_per_cell`, DispatchReceipt/strict-evidence byte hashes, and
  `analysis_attempt_ledger_gap` refusal;
- independently hand-authored canonical v2 registry/manifest byte goldens; and
- AP-2 registry and generated v1 fixture byte parity against the existing
  reviewed v1 oracle.

Verification:

```bash
python3 -m unittest tests.test_analysis_manifest tests.test_axi_analysis_manifest
shasum -a 256 configs/analysis_registry/slice_2m_ap2.v1.json
git diff --check
```

The AP-2 registry digest MUST remain
`9defb37454aec95ff8a40df60f50edcca8e45d17d03f35364f07571d31475b01`.
If the implementation touches the old module, its output-fixture byte test,
not the module source digest, is the landing authority.

### Stage 1 — typed config and wire schemas

Add `joulewise.axi_decode_config.v1`, BatchPolicy, SpeculationPolicy, the
identity objects, metadata blocks, event metadata validators, request-output
row schemas, and 0.6.0 summary schema. Preserve omission serialization for
non-AXI configs and normalized inclusion for AXI configs.

Required tests:

- old example configs serialize byte-identically;
- AXI config hash changes for every batch/speculation identity field;
- mode-specific null rules and config-v0.2 refusal;
- exact five-key event top level;
- token remains singleton and decode emission is request-scoped;
- all JSON schema exports accept emitted objects and reject missing/extra or
  wrong-type fields;
- independently hand-authored positive and negative config, metadata, event,
  target-tokenizer identity, terminal-cancellation, request-row, and
  summary-v0.6 JSON goldens; the
  serializer and schema exporter are compared to these files, not used to
  create them.

Verification:

```bash
python3 -m unittest tests.test_schemas tests.test_bundle tests.test_axi_schemas
python3 -m joulewise validate-config configs/examples/mock_local.json
git diff --check
```

### Stage 2 — request-aware reader and strict validator

Implement v2 dispatch in BundleReader/strict validation using hand-authored
fixtures. Add lifecycle pairing, request outputs, config/metadata checks,
counter/output invariants, genuine timestamp provenance, and request-keyed
phase pairing. Preserve all historical reader behavior.

Required tests:

- terminal outcome for every admitted request in succeeded and failed bundles;
- interleaved/equal-timestamp requests ordered by local ordinal;
- no shared-boundary requirement;
- configured versus realized B mismatch;
- nullable batch/scheduler identity values cannot substitute for request ID;
- required-nullable scheduler, token-ID, and token-hash keys reject omission
  and accept explicit null only in their frozen cases;
- every counter equality and null-versus-zero case;
- proposal-work-then-cancelled-before-output retains its positive proposal
  counter, and over-cap proposals refuse with
  `proposal_count_exceeds_configured_cap`;
- output artifacts, policy counts, IDs/hashes, and stops agree;
- target-tokenizer name, revision, and artifact hash are runtime-observed and
  strict validation rejects missing/malformed/config-only identity;
- malformed v2 evidence fails before reducer derivation;
- historical fixtures retain current behavior; and
- all expected lifecycle/rollup/hash outcomes come from independently
  hand-authored event/roster/artifact goldens, never controller output.

Verification:

```bash
python3 -m unittest tests.test_bundle_read tests.test_cli tests.test_axi_request_validation
python3 -m joulewise validate-bundle tests/fixtures/axi_valid_burst --strict
git diff --check
```

### Stage 3 — reducer 0.6.0 and frozen dispatch arms

Add explicit 0.6.0 dispatch, union-not-sum group phase windows, request
counter/latency rollups, new burst-safe metrics, and censoring. Make post-hoc
reduction select the recorded finalized-bundle version.

Required tests:

- independently hand-authored golden files transcribed from observed current
  behavior for 0.4.1, 0.4.2, and 0.5.0 remain exact, including key-presence,
  null, and tolerant-comparison outcomes; reducer-produced files are never
  fixtures, and this does not assert historical byte identity;
- a 0.6-only shape with a spoofed old label is rejected before frozen-arm
  dispatch; this checks shape/dispatch coherence, not provenance authenticity;
- missing version, unknown version, and event/reducer mismatch fail closed;
- synchronized B duplicate windows integrate once, while distinct meters sum;
- per-token fields are null when one burst token lacks a genuine timestamp;
- zero proposal, zero accepted, zero output, single emission, and positive
  duration censoring cases;
- group-gross metrics never expose per-request energy division;
- reducer output revalidates against immutable output evidence;
- an independent hand-calculated oracle covers union-window joules, counter
  sums, ratio-of-totals, type-7 p50/p95, zero/null censoring, and
  `batch_group_gross_energy_j`; and
- the new `SummaryMetricsV060` canonical serialized bytes match an independent
  hand-authored 0.6.0 golden. No byte-golden requirement is imposed on a fresh
  re-reduction of historical summaries.

Verification:

```bash
python3 -m unittest tests.test_reduce tests.test_bundle_read tests.test_axi_burst_reduce
python3 -m joulewise reduce tests/fixtures/axi_valid_burst
python3 -m joulewise validate-bundle tests/fixtures/axi_valid_burst --strict
git diff --check
```

### Stage 4 — executable C-023 cross-bundle gate

Implement `joulewise.output_identity_report.v1`, exact config projection, the
four-state request/overall algorithm, and analysis admission. Keep it separate
from single-bundle validation.

Required tests:

- exact token match;
- equal text with differing token sequences;
- equal exact text with token-divergent sequences of different counts returns
  `text_match_token_divergent`;
- exact-text or stop-reason divergence, plus unequal-count reason evidence that
  does not by itself force `output_divergent`;
- missing token evidence with equal text remains unassessable;
- exact target-tokenizer name/revision/artifact match, mismatch, and missing
  runtime identity with no asserted equality boolean;
- unexpected config difference despite equal output;
- malformed/missing bundle and request artifacts serialize as schema-valid
  `unassessable` reports with exact MissingEvidenceReason values;
- reason, missing-evidence, and unexpected-difference arrays reject duplicate
  or non-lexicographic order before report hashing;
- attempt-ledger analysis always selects first eligible attempt per cell,
  unknown reasons count eligible, and favorable later retries cannot replace
  it;
- worst-state rollup across multiple requests;
- each state produces exactly the frozen claim disposition; and
- canonical report bytes for all four states match independently hand-authored
  report goldens, including reason-code order and the different-count edge.

Verification:

```bash
python3 -m unittest tests.test_axi_output_identity tests.test_analysis_manifest
python3 -m joulewise output-identity-report \
  --manifest tests/fixtures/axi_ap_spec/analysis_manifest.json \
  --pair-id pair-000
git diff --check
```

### Stage 5 — controller/runtime emission seam

Add request-scoped runtime result interfaces and controller writers for
lifecycle, emissions, request artifacts, explicit batch observation, and
speculation and target-tokenizer identity. The campaign runner writes an
attempt identity before dispatch and finalizes one immutable DispatchReceipt
for every attempt after result handling. Use
deterministic fake runtime results in unit tests; do not claim a production
backend supports them.

Required tests:

- one emission event per request decode step, never a request-ID list;
- global interleaving with request-local ordinal continuity;
- terminal events survive structured runtime failure/cancellation;
- every started attempt retains a manifest/entry/arm/ordinal-bound dispatch
  receipt, including pre-bundle transport/process failure;
- loaded target-tokenizer name, revision, and artifact hash are emitted from
  runtime evidence rather than copied from config;
- artifact write/finalize immutability;
- no B inference from event count;
- v2 B=1 spec-off and spec-on controls use the same event semantics;
- old controller paths emit historical bytes/semantics unchanged;
- controller output is compared byte-for-byte with independent hand-authored
  JSONL/artifact goldens; fake-runtime output generated through the controller
  is not its own oracle.

Verification:

```bash
python3 -m unittest tests.test_interfaces tests.test_controller tests.test_axi_controller_events
git diff --check
```

### Stage 6 — mock spec adapter last

Only after Stages 0-5 are green, add a deterministic mock adapter that produces
spec-off, external-draft, native-MTP, and synchronized static-batch fixtures.
The mock must expose separately parameterized proposal, acceptance, target
emission, token-ID, and per-token timestamp behavior.

Required fixtures:

- enabled proposal total zero;
- proposal nonzero/acceptance zero;
- mixed accepted plus target correction;
- multi-token burst without individual timestamps;
- multi-token burst with genuine per-token timestamps;
- B>1 synchronized duplicate phase windows;
- failed/cancelled request with terminal evidence;
- proposal-work-then-cancelled-before-output with retained counters;
- all four output-identity report states;
- malformed/missing report evidence with frozen missing-evidence reasons;
- target-tokenizer exact/mismatch/unassessable comparator cases.

Verification:

```bash
python3 -m unittest tests.test_mock_adapters tests.test_axi_mock_spec
python3 -m joulewise run configs/examples/mock_axi_spec.json --runs-dir /tmp/jw-axi-sa
python3 -m joulewise validate-bundle /tmp/jw-axi-sa/example-mock-axi-spec --strict
python3 -m joulewise reduce /tmp/jw-axi-sa/example-mock-axi-spec
git diff --check
```

The run is fixture/mock evidence only and MUST retain a non-live label. Every
mock fixture is compared to an independent hand-authored expected event,
artifact, summary, and report oracle; strict validation of the mock writer's
own output is supplemental.

### Stage 7 — integration and landing gate

Run the focused suites above, canonical tests, schema round-trips, docs
freshness, strict mock-bundle validation, frozen-arm golden comparison, and a
final diff review. No adapter is promoted to live support by these checks.
Schema commands MUST be diffed against independently reviewed, hand-authored
tracked golden schema files; printing or round-tripping schemas alone is not a
verification oracle.

Verification:

```bash
python3 -m unittest discover -s tests
python3 -m joulewise print-config-schema | diff -u tests/goldens/config_schema.json -
python3 -m joulewise print-output-schema | diff -u tests/goldens/output_schema.json -
git diff --check
```

Landing requires the canonical suite green, all focused v2 tests green, AP-2
byte parity green, and explicit review of the freeze list below.

## 13. Non-goals

- No live hardware or runtime-support claim. Mock and fixture evidence remains
  L0/non-live; NVIDIA/vLLM remains PROVISIONAL until its existing live gate.
- No legacy re-dispatch, reinterpretation, metadata synthesis, sealed-bundle
  rewrite, or forced re-reduction. Historical token events stay singleton and
  existing metric names stay frozen.
- No continuous scheduler, offered-load generator, steady-state detector,
  coalescing optimum, per-token-at-offered-load campaign, or C5-2.6 scheduler
  claim. Continuous batching is a future successor contract.
- No per-request division of overlapping group/session energy without a
  separately frozen attribution model.
- No new idle-subtracted phase map; phase energy remains gross-only.
- No config schema 0.2 implementation or split-run semantics.
- No mutation of AP-2 v1 semantics or bytes.
- No quality-equivalence design beyond preserving the distinct divergence
  disposition hook. A future quality-matched AP is separately predeclared.
- No quiet-machine collection in AXI-SA and no site regeneration/deployment.

## 14. Explicit landing freeze

When the implementation lands, the following become immutable for
`joulewise.axi_sa_burst_decode.v1`. A change requires the named successor,
not a silent additive reinterpretation. Every normative field table, state
table, formula table, exact-key list, cross-field rule, and refusal code in
§§1-12 is covered by the corresponding item below; none is an extensible
registry within v1.

1. **Version table:** every axis and exact version value in §1.
2. **Normalized identity:** extension name; config field placement;
   BatchPolicy and SpeculationPolicy field sets, enums, types, null rules, and
   cross-field invariants; draft and native-MTP identity definitions; the
   RequestRoster exact two-key top level, exact six-field descriptor set,
   array/order and integer rules, string non-normalization rule, sorted-key
   two-space UTF-8-plus-one-LF bytes, roster SHA-256 input, and all three exact
   prompt-hash domains/preimages in §2.
3. **Metadata:** top-level event version, BatchObservation field set and
   configured/realized meanings, explicit-count/no-inference rule,
   `runtime.primary_source_identity`, and exact
   `runtime.target_model_artifact_sha256` path, plus the exact
   `runtime.target_tokenizer_identity` field set, artifact-hash domain, and
   runtime producer, including their types, non-null rules, and cross-checks in
   §3.
4. **Events:** stable five-key top level; singleton historical token meaning;
   `decode_emission` granularity; common request metadata; lifecycle
   vocabulary; ordinal bases; emission and v2 token schemas; required non-null
   event `request_roster_sha256` and `source_identity`; and the required-key
   presence matrix in §4. In particular, `batch_group_id` and
   `scheduler_step_id` are present-null where unavailable; decode-emission
   `emitted_token_ids` and `emitted_token_ids_sha256` are present-null where
   unavailable, with the exact four allowed null/non-null combinations in
   §4.4; singleton-token `token_id` is present-null when unavailable; omission
   is invalid. Event-type-inapplicable lifecycle fields remain absent, not null.
5. **Counters:** every meaning, inclusion/exclusion boundary, aggregation
   formula, off/zero/null rule, retained cancelled-proposal behavior,
   configured per-attempt cap, and named cap/evidence refusals in §§4-5 and 7.
6. **Outputs:** artifact names and authority order; both exact row schemas;
   roster hash, terminal realized-count agreement, token hash domain, and B=1
   compatibility mirror rules in §6.
7. **Validation:** every lifecycle, phase, overlap, rollup, output, identity,
   and config/metadata invariant in §7.
8. **Reducer compatibility:** dispatch-before-interpretation; exact 0.4.1,
   0.4.2, 0.5.0, legacy, and 0.6.0 arms; post-hoc version selection; all
   existing metric identities; the guarantee “existing arms' code paths and
   outputs unchanged, proven by current-behavior goldens”; unchanged existing
   tolerant-absence sets; and the restriction of versioned serializer/byte
   goldens to new 0.6.0 output in §8.
9. **New metrics:** field names, scope, formulas, aggregation sets, type-7
   quantiles, zero/null/censoring rules, exact
   `batch_group_gross_energy_j` identity, group-gross basis, and no
   per-request-energy attribution in §8.
10. **AP-SPEC:** AP-2 byte-preservation rule; registry/manifest version names;
    every v2 field table; exact pairing fields and allowed config pointers;
    registry-to-manifest semantic/ID/byte-digest binding; exhaustive two-ID
    contrast set; non-null planned n; exactly-n-pair/exactly-2n-entry,
    contiguous replicate/order, coverage and counterpart invariants; no subset,
    alternate manifest, or top-up; the AttemptLedger exact row schema and
    canonical bytes/order; DispatchReceipt and
    StrictValidationAttemptEvidence exact field sets/bytes; closed two-code
    technical-invalid set and predicates;
    unknown-reason-counts-eligible rule; complete attempt/ordinal coverage;
    `first_eligible_per_cell`; all six named refusal codes; three estimands;
    aggregation forms; floor selector; claim ceiling and forbidden upgrade in
    §9.
11. **Output identity:** report version, exact field tables, reason vocabulary,
    nullable BundleReference/ConfigGate/RequestComparison fields; closed
    MissingEvidenceReason enum and null/reason biconditionals; exact target
    tokenizer name/revision/artifact comparator with no asserted boolean; four
    states; state precedence; lexicographic `reason_codes`,
    `missing_evidence_reasons`, and `unexpected_difference_pointers`; canonical
    hash order; and claim dispositions in §10.
12. **Contract edits:** every exact old-to-new replacement and addition in §11.
13. **Verification oracles and delivery order:** the independent hand-authored,
    never-producer-generated oracle rule for every stage; manifest/front-freeze
    first; reader/validator/reducer before emitter integration; mock adapter
    last; and every stage gate in §12.
14. **Non-goals:** every boundary in §13.

Every registry freezes non-null `planned_n_blocks`, exhaustive contrasts, and
one manifest ID and byte digest before its first dispatch. A front-frozen mock
registry also fixes mock n. Claim-bearing n, floor artifact ID/backend, and
transport rule are frozen together in a new campaign registry after Window-A
evidence and before claim-bearing execution; no registry transitions or
mutates in place.

## 15. Definition index and acceptance trace

Every field referenced by a normative invariant is defined on one owning
surface:

| Reference family | Owning definition |
|---|---|
| Config extension, batch, RequestRoster normalization/hash domains, speculation, draft/MTP/tokenizer identity | §2 |
| Event version, configured/realized counts, primary source, runtime target model/tokenizer hashes and identities | §3 |
| Request IDs/ordinals/roster hash, source, phase/lifecycle/terminal realized count, emission/token fields | §4 |
| Proposal/acceptance/emission/rate semantics and cancelled-proposal retention | §§4-5 |
| Request/output/token artifact fields and hashes | §6 |
| Pairing, rollup, lifecycle, evidence precedence | §7 |
| Summary provenance, old/new reducer arms, metric fields and formulas | §8 |
| Registry, one-manifest binding, exhaustive contrasts, planned-n cardinality, pairing projection, deterministic attempt ledger, estimands, floor/divergence | §9 |
| Cross-bundle report, nullable bundle/config/request evidence, missing-evidence reasons, target-tokenizer comparator | §10 |

Council-review acceptance is met when:

- each schema table is implemented with positive and negative tests;
- every §7 invariant has at least one failing fixture and one passing fixture;
- 0.4.1/0.4.2/0.5.0 current-behavior golden outputs and AP-2 v1 bytes remain
  unchanged, while only 0.6.0 is subject to a new serializer byte golden;
- static duplicate windows prove union-not-sum and no test creates
  per-request energy by trace division;
- all four C-023 report states and dispositions are executable;
- attempt-ledger gaps refuse and first-eligible-per-cell selection is invariant
  to later attempt outcomes;
- malformed bundle evidence produces schema-valid unassessable reports, and
  canonical report arrays have frozen lexicographic order;
- the exact §11 amendments land without redefining stored legacy fields;
- the Stage 6 mock bundle is strict-valid and explicitly non-live; and
- the complete Stage 7 verification is green.
