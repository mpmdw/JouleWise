# Identity-pin projection receipt contract

In plain words: before a measurement campaign is collected, a script checks
that the model weights, tokenizer, runtime, and configuration files on disk
are the exact ones the campaign registered. That check is the
**identity-pin projection**; the file it writes recording what it checked
and found is the **receipt**; this document is the contract that fixes
both. Each term is built from its physical inputs in §1.

Status: executable contract for
`joulewise.identity_pin_projection_receipt.v1`. The implementation in
`joulewise/identity_pins.py` is authoritative when this text and code differ.

## 1. Purpose and forcing problem

An **identity-pin projection** is a machine-produced record of four physical
inputs to a collection: the model artifact bytes loaded as weights; the
**tokenizer behavior**, meaning the token IDs produced from each registered
prompt by the collection tokenizer; the **runtime behavior**, meaning the
selected runtime adapter that loads and invokes the model plus the telemetry
adapter that identifies the power sensor and measurement boundary; and the raw
configuration-file bytes. Its three **identity pins** use **SHA-256**, the
byte-hashing algorithm whose result is written as 64 lowercase hexadecimal
characters, to digest the model bytes, runtime identity, and **normalized
scientific configuration**. That last value is the schema-validated
configuration after
`run_id` is removed; tags starting with `analysis-replacement-of=`,
`analysis-replacement-reason=`, `calibration-plan-sha256=`,
`calibration-abba-block-id=`, `calibration-abba-label=`, or
`calibration-abba-sequence-index=` are removed; tags whose whole value matches
`rep[0-9]+` are removed; and other `run_metadata` keys are discarded when tags
are normalized.

A **campaign pack** is the directory containing `plan_tree.json`, its
configuration files, and its evidence files. At desk review those bytes may be
correct; before physical collection, a model weight can be replaced, a
tokenizer file can change, a runtime package can resolve differently, or the
same prompt text can become a different token sequence. The GPU would then
measure a workload other than the one reviewed. The later **floor mint**, the
program that converts accepted evidence into a JSON floor artifact containing
the minimum effect sizes that evidence may support, would recompute different
pins and refuse the otherwise expensive collection.

This contract prevents that loss by **freezing**: it changes an `unprojected`
pack, whose three pins and receipt are null, into a `frozen` pack whose derived
pins and receipt binding this operation will never overwrite. It derives the
same facts again immediately before collection. Each act leaves an
authenticated **receipt**, a JSON record of its inputs, outputs, and checks;
the receipt's SHA-256 is stored in `plan_tree.json`, and a sibling text file
repeats that digest and the receipt filename so the receipt bytes can be checked
before their JSON is trusted.

## 2. Vocabulary

- A **scientific workload** is the schema-validated configuration after
  `run_id` is removed and bookkeeping tags are filtered. When `run_metadata`
  is an object and `run_metadata.tags` is an array, the implementation keeps a
  tag only when this exact predicate is true:

  ```python
  not tag.startswith("analysis-replacement-of=")
  and not tag.startswith("analysis-replacement-reason=")
  and not tag.startswith((
      "calibration-plan-sha256=",
      "calibration-abba-block-id=",
      "calibration-abba-label=",
      "calibration-abba-sequence-index=",
  ))
  and re.fullmatch(r"rep[0-9]+", tag) is None
  ```

  Thus only the two shown analysis-replacement prefixes, the four shown
  calibration prefixes, and a whole-string match of `rep` followed by one or
  more decimal digits are removed. Other tags remain. When this tag
  normalization runs, every other `run_metadata` key is discarded and the
  normalized object is exactly `{"tags": <remaining tags>}`.
- An **identity unit** is one ordered pack entry whose configurations all
  declare one model, hardware target, runtime, telemetry backend, and
  quantization (the policy for representing the model's numeric weights).
  Its configurations have either one exact scientific workload or one common
  workload profile plus a declared closed set of suite manifests. It is the
  loop unit in `_derive_projection_units`.
- A **declaration** is the eight-field claim copied from the pack for one
  identity unit: hardware target, runtime backend, telemetry backend, model
  name, model source, model revision, quantization, and workload profile.
- A **common workload profile** is a typed configuration's workload profile
  after only `suite_manifest_ref` and `suite_manifest_sha256` are removed.
  Every other typed key and value, including schema-inserted JSON nulls,
  remains.
- A **declared manifest member** is an object with exactly
  `suite_manifest_ref`, `suite_manifest_sha256`, and
  `declared_member_count`. The reference is one nonempty relative POSIX path;
  the digest is one lowercase SHA-256; and the count is a positive integer
  that is not a Boolean. A **declared manifest set** is the nonempty ordered
  `suite_manifest_set` array of those objects. Its references are unique and
  its digests are unique. It is stored beside the common workload fields
  inside `declared_identity.workload_profile`; it is never folded into one
  synthetic manifest.
- A **manifest class** is every emitted configuration in one identity unit
  whose typed workload binds the same `suite_manifest_sha256`. Each member of
  the class must also use the reference paired with that digest in the
  declared manifest set. The **emitted census** maps each declared manifest
  digest to the number of emitted configurations in that class.
- A **member scientific identity** is the SHA-256 of one normalized scientific
  configuration. The **distinct member identity set** is the mathematical set
  of those hashes for one identity unit. Configurations in one manifest class
  must have exactly one member scientific identity, and the number of distinct
  member identities must equal the number of declared manifest members.
- The **unit config-set digest** is the value written as
  `config_set_sha256`. Section 4 defines its byte preimage for both the
  one-identity and several-identity cases.
- A **configuration inventory** is the list of pack-relative configuration
  paths, meaning paths measured from the pack directory, and each file's
  raw-byte SHA-256. The list is **lexically sorted**: path strings are ordered
  from smallest to largest by Python string comparison.
- A **model-file inventory** is the same lexical ordering of recognized local
  weight files. Every row carries the path written in the model tree, the
  absolute resolved path reached on disk, the byte count, the SHA-256 of the
  bytes reached by following the path, and `symlink`, which is true when the
  model-tree path is a symbolic link (a filesystem entry that redirects to
  another path).
- A **runtime probe** performs three named operations once for an identity
  unit: `prepare` loads the configured runtime and model; the probe asks that
  prepared runtime for the workload identity it would collect and asks the
  telemetry adapter which power device and physical boundary it would read;
  `cleanup` releases the prepared runtime. It does not execute or record a
  measured campaign member.
- A **prompt expectation** is the four-key object stored in such a typed
  workload: schema version; token hash domain, the fixed string placed before
  token bytes to separate this hash from other uses of SHA-256; token count,
  which must be an integer greater than zero and not a Boolean; and lowercase
  token-ID digest. An **expectation-bearing configuration** is a configuration
  that contains that object.
- A **prompt realization** is what the loaded collection tokenizer actually
  makes from the registered prompt: positive token count, token-ID digest, and
  token hash domain. It is an observation, not an operator-entered value.
- **Canonical JSON** here means UTF-8 JSON with object keys sorted, no spaces
  between tokens, Unicode emitted directly rather than ASCII-escaped, and
  non-finite numbers forbidden.
- The **projection input** is the ordered JSON array assembled from every
  identity unit's declaration, raw-file inventories, model identity, and live
  probe metadata. `projection_input_sha256` is the lowercase SHA-256 digest of
  that array's canonical JSON bytes.
- **Freeze** is the sole `unprojected` to `frozen` transition: derive the
  values, write a receipt, and place its path and digest plus the derived
  three-pin value in the pack.
- **Arm re-verification** means deriving the same live values again immediately
  before the readiness decision. **Arm** is the readiness ceremony that may
  issue a launchable receipt; it is not the later process launch.
- Receipt status **PASS** means every required comparison succeeded; **REFUSE**
  means at least one named reason code blocked readiness.
- **Drift** means a current value has the required type and shape but differs
  from the registered or frozen value. **Dirty** is the refusal classification
  for that difference, including an uncommitted repository change.
- **Unreadable** means the mechanism cannot obtain or type-check a required
  fact. A present string such as `"4"` is unreadable as a token count because
  it is not the required integer, even though a human can read it.
- **Custody** is the directory boundary in which authenticated receipt bytes
  are retained. Pack custody holds freeze receipts; window custody, outside
  the pack, holds arm receipts.
- A **check** is a four-key receipt row containing an identifier, status,
  expected value, and observed value. A **shared-mint projection** is the
  derived three-pin value made by the same functions used by the floor mint:
  model artifact digest, runtime identity digest, and scientific-config
  digest.
- **Re-derive** means execute the inventories and probes again from current
  physical files and the current loaded adapters. **Replay** means authenticate
  and consume already-written receipt bytes without executing those probes.
- **Idempotent** means a second successful operation over the identical frozen
  state writes no bytes and returns the same binding. It does not mean that a
  changed environment is accepted.
- A **sidecar** is the small text file beside a JSON receipt that states the
  receipt's SHA-256 and filename, letting a reader authenticate the JSON bytes
  before parsing them.

## 3. Initial `unprojected` envelope

Before freeze, `plan_tree.json` must contain an
`arm_attachments.identity_pin_projection` object with exactly these eight
keys: `work_order`, `mode`, `state`, `required_before_arm`,
`derivation_contract`, `identity_units`, `projection_receipt`, and
`supersedes`. Their fixed values are:

- `work_order` is `D117-U11-IDPIN-PROJECTION`;
- `mode` is `derive_never_operator_enter`, which means the operator supplies
  declarations and file bindings but never supplies any of the three pins;
- `state` is `unprojected` before the first freeze, `frozen` after a successful
  freeze, or `superseded` after this pack has been replaced;
- `required_before_arm` is the JSON Boolean `true`;
- `derivation_contract` is `joulewise.identity_pin_derivation.v1`;
- `identity_units` is a nonempty stored-order array of unique unit IDs;
- `projection_receipt` is `null` while unprojected and otherwise has exactly a
  nonempty `path` and lowercase 64-hex `sha256`; and
- `supersedes` is an array. Each row has exactly `pack_id`, a nonempty string,
  and three lowercase 64-hex digests: `pack_sha256`,
  `projection_receipt_sha256`, and `readiness_sha256`. Pack IDs in the array
  are unique.

Each unit has exactly `identity_unit_id`, `producer_plan_reference`,
`consumer_bindings`, `declared_identity`, `config_inventory`, and
`model_runtime_config`. The unit ID is a nonempty unique string.
`producer_plan_reference` has exactly nonempty string `plan_id` and `path`.
`consumer_bindings` is nonempty; each row has exactly nonempty string `arm`,
`family`, and `measurement_arm`. `declared_identity` has exactly the eight
declaration fields listed in section 2. `config_inventory` is a nonempty
lexically sorted array of exact `path`/`sha256` objects with unique
pack-relative paths. `model_runtime_config` has exactly
`model_artifact_sha256`, `runtime_identity_sha256`, and `config_set_sha256`.
While `state` is `unprojected`, all three values and `projection_receipt` must
be JSON `null`. For every other state they must be lowercase 64-hex digests and
a two-key receipt binding.

The following is a minimal valid projection object for the first raw config in
section 8. It can be pasted as the value of
`arm_attachments.identity_pin_projection` in a plan tree whose pack contains
that exact `configs/member-1.json`, while the model bytes and adapter outputs
shown in section 8 are present, then frozen. The declaration is the typed value
of that config rather than an operator-supplied pin:

```json
{
  "work_order": "D117-U11-IDPIN-PROJECTION",
  "mode": "derive_never_operator_enter",
  "state": "unprojected",
  "required_before_arm": true,
  "derivation_contract": "joulewise.identity_pin_derivation.v1",
  "identity_units": [{
    "identity_unit_id": "toy/prefill",
    "producer_plan_reference": {"plan_id": "toy-plan", "path": "producer_contract.json"},
    "consumer_bindings": [{"arm": "A", "family": "toy-family", "measurement_arm": "prefill"}],
    "declared_identity": {
      "hardware_target": "example-mac",
      "runtime_backend": "mlx",
      "telemetry_backend": "powermetrics",
      "model_name": "toy-model",
      "model_source": "/models/toy.safetensors",
      "model_revision": "r1",
      "quantization": {"bits": 4, "group_size": null, "name": "int4"},
      "workload_profile": {"dataset_ref": null, "name": "toy-prefill", "output_tokens": 1, "prompt_text": "ABCD", "prompt_token_expectation": {"schema_version": "joulewise.prompt_token_expectation.v1", "token_count": 4, "token_hash_domain": "joulewise.prompt_token_ids.v1", "token_ids_sha256": "10e6c1854858d7cdd278400c11706ebd2a43fe79ffa241bd5c1d0f6fe665a9fe"}, "prompt_tokens": null, "repetitions": 1, "warmup_runs": 1}
    },
    "config_inventory": [{"path": "configs/member-1.json", "sha256": "5bee74bfc11a663e7b4c364d24c33883930438a60d126d99ab400a4e7cfa9805"}],
    "model_runtime_config": {"model_artifact_sha256": null, "runtime_identity_sha256": null, "config_set_sha256": null}
  }],
  "projection_receipt": null,
  "supersedes": []
}
```

## 4. Projection input and `projection_input_sha256`

Before the unit object is constructed, `model_artifact_identity` returns one
of two complete successful shapes. For a single model file it contains
`status: "ok"`, `kind: "single_file"`, `algorithm: "sha256"`, `sha256`,
`path`, and a one-row `inventory`. For a model directory it contains
`status: "ok"`, `kind: "file_set"`, `algorithm: "sha256"`,
`folded_sha256`, `files`, `inventory`, and `root`. `files` maps each path
relative to the model root, written with `/` separators in POSIX form, to its
raw-file digest. Every `inventory` row contains exactly `path`,
`resolved_path`, `sha256`, `size_bytes`, and `symlink`. Directory links are
not traversed; file links retain the path written in the model tree but hash
the bytes reached by following the link.

The folded digest is SHA-256 over the UTF-8 bytes
`joulewise.model_artifact_identity.v1`, one NUL byte (a byte whose value is
zero), and the compact, sorted-key JSON of `files` produced with the JSON
encoder's default ASCII
escaping. A failed or changing inventory refuses before an input is hashed
(`joulewise/provenance.py:72-143,176-267`).

The runtime probe defined in section 2 returns `probe_metadata` with these
top-level fields:

- `platform` and `machine`, from `platform.platform()` and
  `platform.machine()`;
- `device`, the entire mapping returned by the configured telemetry adapter's
  `device_metadata`; for powermetrics this includes the device, telemetry
  name, rail manifest, physical boundary label, timestamp derivation, power
  units, and powermetrics executable/probe metadata;
- `quantization`, the complete JSON object formed from every named field in
  the typed configuration's quantization record;
- `adapters.runtime.name` and `adapters.telemetry.name`;
- `adapters.runtime.prepare_metadata`, containing only prepare keys that are
  present from this closed allowlist, meaning the only permitted keys:
  `adapter`, `version`, `mlx_version`,
  `mlx_lm_version`, `kernel_library`, `quantization`, and
  `batching_concurrency_policy`;
- `workload_provenance`, the entire mapping from the representative runtime's
  `identity_projection_metadata`; for MLX it contains `model` (`name`,
  `source`, `revision`, and complete `artifact_identity`), `tokenizer`
  (`backend`, `identifier`, `revision`, `class`, `vocab_size`), `sampler`
  (`kind`, `temperature`, `pinned`, `api`, `parameter`), and `output_policy`
  (`name`, `requested_tokens`, `stop_condition`). It also contains the
  representative configuration's `prompt_realization` triple when that
  configuration contains a prompt expectation; and
- `prompt_realizations`, only when at least one configuration in the unit is
  expectation-bearing. Its rows stay in lexically sorted configuration order
  and contain exactly `config_path`, `token_count`, `token_ids_sha256`, and
  `token_hash_domain`. Configurations without an expectation produce no row.

`_derive_projection_units` walks `projection.identity_units` in stored order.
It emits one projection-input object per unit, with exactly these seven
top-level fields in the constructed object:

| Field | Exact content placed in the hash input |
|---|---|
| `identity_unit_id` | The unit's nonempty string ID. |
| `producer_plan_reference` | Object with exactly `plan_id` and `path`, both nonempty strings. |
| `consumer_bindings` | Nonempty array; every object has exactly `arm`, `family`, and `measurement_arm`, all nonempty strings. |
| `declared_identity` | Object with exactly `hardware_target`, `runtime_backend`, `telemetry_backend`, `model_name`, `model_source`, `model_revision`, `quantization`, and `workload_profile`. For a legacy one-identity unit it must equal the value re-derived from every typed configuration. For a declared manifest set, every non-workload field must equal every typed configuration, and the declared common workload profile must equal every typed workload after its two per-member manifest fields are removed. |
| `config_inventory` | Lexically sorted array of objects with exactly `path` and lowercase `sha256`. The digest covers the raw configuration file bytes, so even fields omitted from scientific identity remain byte-bound here. |
| `model_artifact_identity` | The complete successful single-file or file-set result defined immediately above. |
| `probe_metadata` | The complete runtime-probe result defined immediately above. |

The current code deliberately does not impose an exact-key validator—a rule
that rejects missing or additional object keys—on the whole `device` or
`workload_provenance` mapping; their complete adapter-returned mappings are
hashed. Reproduction therefore uses the selected adapter output, not a
hand-written subset.

The projection input deliberately excludes the final receipt, final plan tree,
receipt sidecars, receipt observations, derived check rows,
`realized_stack_identity`, and the derived `model_runtime_config`. Those are
outputs or envelopes; including them would create a self-reference or hash a
derivative twice. Pack ID, plan ID, window ID, and reviewed Git commit are
stored separately in `receipt.pack`. Function names and source-file digests
are stored separately in `receipt.derivation`.

The full `runtime.prepare()` metadata is also deliberately excluded. In
particular, `transformers_version`, model-load wall time, memory snapshots,
absolute model-source diagnostics, weight format, and model-config diagnostics
do not cross the seven-key allowlist at
`joulewise/identity_pins.py:1375-1387`. A packaging-version change is therefore
not by itself workload drift. If it changes tokenizer identity, realized token
IDs, the selected runtime version, or any other value in the hashed adapter
output, that changed output is already hashed. Model source, revision, and
bytes are bound elsewhere in the same unit.

Finally, serialize the ordered unit array with
`json.dumps(value, sort_keys=True, separators=(",", ":"),
ensure_ascii=False, allow_nan=False).encode("utf-8")`, apply SHA-256 to those
bytes, and render the 32-byte result as 64 lowercase hexadecimal characters
(`joulewise/identity_pins.py:184-195,1676-1696`).

The three shared-mint pins are derived beside this input:

1. `model_artifact_sha256` is the single-file digest or folded file-set digest.
2. Derive each member scientific identity by applying the exact
   scientific-workload normalization predicate printed in section 2 and then
   applying SHA-256 to its canonical JSON. That predicate removes only
   `analysis-replacement-of=`, `analysis-replacement-reason=`,
   `calibration-plan-sha256=`, `calibration-abba-block-id=`,
   `calibration-abba-label=`, and
   `calibration-abba-sequence-index=` prefixes, plus a full-string
   `rep[0-9]+`; when tags are normalized, all other `run_metadata` keys are
   discarded.

   Let `H` be the lexically sorted distinct member identity set. `H` must be
   nonempty. If `H` contains one hash, `config_set_sha256` is that hash
   unchanged. This preserves every existing single-identity receipt byte for
   byte. If `H` contains two or more hashes, form this UTF-8 byte string with
   no NUL bytes and no final line feed:

   ```text
   joulewise.identity_unit_config_set.v1\n<smallest hash>\n<next hash>...
   ```

   In formula form, the preimage is the literal domain string
   `joulewise.identity_unit_config_set.v1`, one line-feed byte, and
   `"\n".join(sorted(H))`. `config_set_sha256` is the lowercase SHA-256 of
   that complete preimage. Duplicate occurrences do not enter the preimage;
   their required counts are enforced by the emitted census instead.
3. `runtime_identity_sha256` is SHA-256 over
   `joulewise.stack_identity.v1`, one NUL byte, and canonical JSON of exactly
   these eleven fields:

   ```text
   hardware_unit, os_version, runtime_version, kernel_library,
   model_artifact_sha256, quantization, tokenizer_identity,
   sampler_output_policy, batching_concurrency_policy,
   measurement_boundary_label, telemetry_backend
   ```

   These are `STACK_IDENTITY_FIELDS` in
   `joulewise/identity_pins.py:48-60,313-345`.

The runtime probe may use the first lexically inventoried configuration as its
representative only after every member has passed the common model, hardware,
runtime, telemetry, quantization, and workload checks. The representative
selects no unit-level config value: the unit config-set digest comes only from
the sorted distinct member identity set. The projection also derives the model
artifact and runtime identity pins for every member from the probe metadata and
refuses unless every member produces the same two pins and the same complete
stack identity.

## 5. Prompt realization

The **encoder**, the loaded MLX collection-tokenizer entry point that converts
text to integer token IDs, is reached through
`MlxRuntimeAdapter._prompt_for_workload`. For a registered `prompt_text`, that
path calls `_encode(tokenizer, prompt_text, add_special_tokens=True)`
(`joulewise/adapters/mlx_runtime.py:940-946`). `_encode` first calls
`tokenizer.encode(text, add_special_tokens=True)`; if that API raises
`TypeError`, the Python signal that this tokenizer method rejects that keyword,
it calls `tokenizer.encode(text)` exactly as the
collection path does (`joulewise/adapters/mlx_runtime.py:1109-1114`). Thus the
projection reproduces collection behavior; it does not introduce a second
tokenizer implementation.

For token IDs `[i0,i1,...]`, the count is `len(token_ids)`. The token digest is
SHA-256 over the UTF-8 string `joulewise.prompt_token_ids.v1`, one NUL byte,
and the no-space JSON array of decimal integers. The returned domain is the
literal `joulewise.prompt_token_ids.v1`
(`joulewise/provenance.py:12,58-60,318-324`). These three values are copied as
`token_count`, `token_ids_sha256`, and `token_hash_domain` by
`identity_projection_metadata` (`joulewise/adapters/mlx_runtime.py:315-349`).

`token_count` must be a Python integer greater than zero and must not be a
Boolean. A digit string such as `"4"` is ill-typed, so
`_prompt_realization_triple` refuses it as
`readiness_identity_artifact_unreadable`
(`joulewise/identity_pins.py:1256-1279`). A different positive integer such as
`5` is readable evidence; comparison with the registered `4` then refuses it
as `readiness_identity_environment_dirty`, naming every differing field
(`joulewise/identity_pins.py:1516-1550`). Missing rows, extra or missing row
keys, wrong paths, and wrong row counts are unreadable at
`joulewise/identity_pins.py:1489-1515`.

For one identity unit, runtime preparation occurs exactly once using the first
configuration. The already-prepared runtime projects the representative and
then every other expectation-bearing configuration in inventory order.
Telemetry metadata is read once, and cleanup occurs exactly once in the Python
`finally` block, which runs even if a projection fails
(`joulewise/identity_pins.py:1310-1374`). This is
once per identity unit, not once for the entire pack and not once per config.

## 6. Lifecycle: freeze, arm, and launch

### Freeze

`freeze_projection(pack_root)` authenticates the plan tree and the optional
**producer contract**, the producer's JSON declaration of the plan that this
pack consumes. It validates an `unprojected` or already `frozen` projection,
derives all units, obtains the **mint Git anchor** (the repository root and
reviewed commit selected by the floor mint), and records the **derivation code
identity** (the contract ID, function-name list, and SHA-256 of every source
file defining those functions).

For each identity unit, freeze performs the following comparison before it
probes runtime metadata or writes anything:

1. It reads every inventoried configuration's raw bytes, requires their
   SHA-256 to equal that inventory row's digest, and parses each as a JSON
   object. Typing through `BenchmarkConfig` happens later, per
   configuration, inside the comparison of steps 2–3.
2. When `suite_manifest_set` is absent, the legacy rule applies: every complete
   typed declaration must equal the stored declaration and every configuration
   must have the same member scientific identity.
3. When `suite_manifest_set` is present, freeze validates every exact
   three-field declared member, removes only `suite_manifest_set` from the
   stored workload to obtain the declared common workload profile. It then
   resolves each declared member's `suite_manifest_ref` — a
   repository-relative path, of which only the part after the pack directory's
   name is kept — as a regular, non-symlink file whose resolved path stays
   below the pack root, reads it, and requires its SHA-256 to equal the
   member's declared `suite_manifest_sha256`. A reference that cannot be
   resolved that way, a file that cannot be read, or a digest that differs
   refuses with reason code `readiness_identity_environment_dirty` ("declared
   suite manifest is unauthenticated") before any configuration's declaration
   is compared. It removes only `suite_manifest_ref` and
   `suite_manifest_sha256` from each typed emitted workload to obtain its
   observed common workload profile. Every observed common profile and every
   non-workload declaration field must equal the declaration.
4. Each emitted configuration's manifest digest must name one declared member,
   and its manifest reference must equal the reference paired with that digest.
   Freeze constructs the emitted census without dropping duplicate
   occurrences, then requires every declared digest to occur exactly its
   `declared_member_count`. An extra digest, missing digest, missing occurrence,
   or extra occurrence refuses.
5. For each manifest class, the set of member scientific identities must have
   cardinality one. The distinct member identity set for the unit must have
   cardinality equal to the declared manifest set. Thus an unfiltered changed
   tag or note on one repeated member refuses even when its manifest binding
   and common workload are unchanged.
6. Only after those comparisons pass does freeze use the representative
   configuration for the runtime probe. It derives every member's stack pins
   through the shared mint path with that metadata, requires all member model
   artifact pins, runtime identity pins, and complete stack identities to be
   equal, and supplies the unit config-set digest defined in section 4, never a
   hash selected by set iteration.

The identity projection therefore authenticates two kinds of bytes inside the
campaign-pack directory (the pack root) before it compares any declaration:
every inventoried configuration's raw bytes against its inventory digest (step
1) and, when a suite-manifest set is declared, every declared manifest member's
file against its declared digest (step 3). Within this contract, an
unauthenticated manifest binding means either a declared manifest member whose
reference cannot be resolved below the pack root, whose file cannot be read, or
whose file bytes do not hash to its declared `suite_manifest_sha256` — each
refuses in step 3 with `readiness_identity_environment_dirty` — or a
configuration whose manifest digest and reference are not present as the exact
declared pair, which refuses in step 4.

On the first successful freeze it writes:

- `identity_pin_projection.receipts/projection-NNNN.json`, where `NNNN` is the
  next zero-padded number beginning at `0001`;
- the sibling `projection-NNNN.sha256`, whose bytes use the GNU `sha256sum`
  text form: `<receipt-sha256><two spaces>projection-NNNN.json\n`;
- `plan_tree.json` and `plan_tree.sha256`, with state `frozen`, receipt path and
  digest, and each unit's derived three-pin value; and
- when present, `producer_contract.json` carrying the same frozen projection,
  plus its updated digest in the plan tree.

All derivation and receipt rendering occurs before the write set is staged.
A derivation refusal therefore leaves pack bytes unchanged. Writes are staged,
flushed from the process to durable storage, atomically replaced, and followed
by a durable-storage flush of each containing directory
(`joulewise/identity_pins.py:1937-1965,1988-2097`). Repeating freeze on an
identical frozen projection authenticates the existing receipt, re-derives the
environment, checks derivation identity, input digest, and pins, and returns
`mutated: false` without creating `projection-0002.json`. A differing frozen
state refuses; it is never overwritten.

### Arm re-verification

`verify_frozen_projection(pack_root, window_custody_root,
bracket_session_id)` requires a **path-safe session ID**: one nonempty path
component for which Python's POSIX path parser reports
`PurePosixPath(value).name == value`, with no backslash, and with a value other
than `.` or `..`. It also requires a frozen PASS receipt. It authenticates that
receipt and sidecar against the **committed checkout**, the versions of those
files stored in the reviewed Git commit rather than merely the current disk. It
then rejects a **committed successor**, meaning another committed pack whose
active passing freeze receipt names this pack ID and this freeze-receipt digest
in its `supersedes` array and whose receipt is later or tied-latest in Git
history. Finally it compares the executable derivation identity and re-derives
every unit from current files and adapters. It never writes inside the pack.

It writes the external receipt and sidecar at:

```text
<window_custody_root>/<pack_id>/receipts/<bracket_session_id>/
    identity-pin-arm-verify.json
    identity-pin-arm-verify.sha256
```

Identical existing custody bytes make the write idempotent; different existing
bytes refuse. On PASS, `reason_codes` is empty and the check list contains, in
unit order:

1. `<identity_unit_id>:shared_mint_projection`, status `PASS`, with the derived
   three-pin value equal in `expected` and `observed`;
2. for every expectation-bearing config,
   `<identity_unit_id>:<config_path>:shared_mint_projection:prompt_realization`,
   status `PASS`, with the registered triple in `expected` and the live triple
   in `observed`.

On a caught re-derivation failure, one final check is appended with ID
`frozen_projection_reverification`, status `REFUSE`, and the frozen input
digest and pins in `expected`. If `_derive_projection_units` raised before it
returned, no partial PASS checks or partial digest escape that function: the
receipt retains the frozen units/digest and `observed` adds the error's
structured detail. If full derivation returned and the later frozen-versus-live
comparison failed, all returned PASS checks precede the final REFUSE check and
the current digest is available. The receipt status is `REFUSE` and carries the
sorted refusal code. Errors raised before the frozen receipt can be
authenticated escape to the readiness layer that maps projection evidence into
the arm decision. That layer maps the same code into readiness refusal but may
have no arm receipt to bind (`joulewise/identity_pins.py:2100-2234`;
`joulewise/arm_readiness.py:5681-5729`).

Arm re-verification calls the same `_derive_projection_units` comparison, so
the common-profile equality, declared manifest membership, exact census, and
one-identity-per-manifest rules are re-run against current configuration bytes.
The frozen receipt remains the expected side of the comparison; the live
derivation never edits its declaration or census.

### Analysis-gate definitions

- **U8** is the arm-readiness mapper and record that authenticates the pack's
  required freeze evidence before any launch can be authorized.
- **U11** is the identity-pin projection subsystem and its projection-evidence
  row inside the U8 freeze receipt.
- **Launch lineage** is the authenticated receipt chain from a collected bundle
  back to the consumed arm authorization and its exact pack digest.
- The **exact-cell route** directly selects a bound floor cell only when the
  consumer has one scientific identity and the cell carries that same identity
  and runtime stack.
- **Condition-family transport** is the ruled path from calibrated source cells
  to a compatible consumer condition family without requiring exact scientific
  identity equality.
- A **transport group** is the floor artifact's declaration of the bound source
  cells, compatible consumer families, runtime stack, and admissible stress
  envelope used by condition-family transport.

### Analysis consumption

For successor packs, every accepted bundle carries an authenticated launch
lineage that resolves one pack root. The analysis input gate follows that
already-authenticated root to the plan-pinned U8 readiness freeze receipt,
authenticates its sidecar, requires its one
`u11-freeze-projection` evidence binding to equal the plan's frozen projection
binding, and authenticates the bound frozen identity receipt and sidecar. The
gate selects the one receipt unit whose `consumer_bindings.family` equals the
requested condition-family ID. It authenticates that unit's inventoried config
bytes, re-derives their distinct member identity set, and checks the resulting
unit config-set digest against the receipt.

That root is the machine-absolute pack path recorded when the arm was consumed.
Bundle loading authenticates the launch lineage before any evidence row exists:
it replays the consumed arm and resolves the recorded pack root strictly, as it
resolves the consumption receipt, the launch manifest, the window root and the
lifecycle receipts, so a bundle whose arming-time paths no longer exist is
refused at input loading (`launch_binding_mismatch`, or
`launch_consumption_missing` when the consumption receipt itself is gone) and
never reaches this gate. Analysis of successor-lineage bundles therefore runs
on the filesystem that armed them; making the lineage relocatable is a separate
design lane, not a property of this gate. Called directly with a lineage whose
pack root does not resolve, the gate refuses with
`consumer_identity_set_unauthenticated`, the same label as any pack it cannot
authenticate.

The evidence member identities must be nonempty and a subset of that frozen
set. Any outside identity or unreadable binding returns no floor request. A
single evidence identity may use the exact-cell route. Two or more evidence
identities skip the exact-cell route entirely and may bind only through a
declared condition-family transport group. Legacy evidence without successor
launch lineage retains the historical single-identity route; it cannot use the
multi-identity route.

The analysis output distinguishes two identity failures by which step of the
gate fails.

The gate refuses with `consumer_identity_set_unauthenticated` when successor
launch lineage exists but any one of the following steps, taken in this order,
fails: (1) every evidence row carries a launch-lineage record, and all rows
name the same pack root and the same 64-hex pack digest; (2) the pack root
exists and the digest of its committed file tree (the sha256 over the pack's
committed files — each path, Git mode, byte length and content digest in path
order — computed by `committed_pack_tree_sha256`, which itself fails, and so
refuses here, if any file under the pack root is untracked, missing, or differs
from its committed bytes) equals that pack digest, which is the same digest the
launch lineage recorded at arm time; (3) the plan tree names a frozen
projection (`state` is `frozen`) with a freeze-receipt reference of exactly
`path` and `sha256`; (4) the U8 freeze receipt at that path has status `PASS`,
its bytes hash to the referenced digest, its sidecar matches, and it carries
exactly one `u11-freeze-projection` evidence row (namespace `PACK`, status
`PASS`) whose `path` and `sha256` equal the plan's `projection_receipt`
binding; (5) the frozen identity receipt at that path hashes to that digest,
its sidecar matches, and it validates as a `freeze_projection` receipt with
status `PASS`; (6) exactly one receipt unit has a consumer binding whose
`family` equals the requested condition family, and exactly one projection unit
carries that unit's ID with the same `config_set_sha256`; (7) every inventoried
config file of that unit hashes to its inventory digest and parses as a JSON
object; (8) the set of scientific identities re-derived from those configs is
nonempty and folds to the unit's `config_set_sha256`. A parse or validation
error at any step is the same refusal. Steps (3)–(8) read only files inside the
pack root, so step (2) is what binds the pack to the launch: without it, an
internally consistent pack the launch never consumed would authenticate.

When all eight steps pass, the gate holds a nonempty frozen set of scientific
identities. It then hashes each evidence row's scientific identity and refuses
with `consumer_identity_undeclared` if any hash is outside that set. The same
label is used for legacy evidence (no successor launch lineage) that contains
two or more scientific identities, because no frozen set exists to declare
them.

### What happens after arm

The ordinary launch step authenticates and replays the arm receipt, pack
digest, **launch manifest** (the JSON declaration of the reviewed command and
its inputs), and **one-use consumption record** (the durable proof that this
launch authorization has been spent exactly once). It does not call
`verify_frozen_projection`, `_derive_projection_units`, runtime `prepare`, or
the tokenizer (`scripts/launch_window.py:102-167,239-280`). Therefore a model,
runtime, or tokenizer change after arm and before `execve`—the point where the
launcher process replaces itself with the reviewed collection command—is not
re-derived by the launch step. The scheduled work row
`V5-LAUNCH-REALIZATION-RECHECK-01` is specifically responsible for moving this
boundary by re-deriving after consumed-launch verification and before bundle
creation.

If collection nevertheless produces a **succeeded bundle**, the completed run
directory whose status says collection succeeded, the bundle reader later
compares the registered triple with coherent realized prompt evidence
and reports missing, inconsistent, or mismatching realization evidence
(`joulewise/bundle_read.py:931-1077`). That is a post-hoc catch: it can reject
the bundle after work occurred, but cannot prevent the physical night. Because
assurance language must stay no stronger than the evidence named with it, the
present mechanism is therefore described as freeze-and-arm detection, not
continuous launch-time assurance.

## 7. Receipt schema and refusal vocabulary

A receipt has exactly this top-level key set; no receipt self-hash is allowed:

```text
checks, derivation, identity_units, observations, pack, reason_codes,
receipt_id, receipt_kind, schema_version, status, supersedes, work_order
```

`schema_version` is `joulewise.identity_pin_projection_receipt.v1`;
`work_order` is `D117-U11-IDPIN-PROJECTION`; `receipt_kind` is exactly
`freeze_projection` or `arm_reverification`; and `status` is exactly `PASS` or
`REFUSE`. A PASS has no reason codes. A REFUSE has at least one. Reason codes
are unique, sorted, and drawn only from the table below.
Receipt JSON is rendered with two-space indentation, sorted keys, direct
Unicode, non-finite numbers forbidden, and one final newline; its sidecar hashes
those rendered file bytes, not canonical re-rendered JSON
(`joulewise/identity_pins.py:743-755`). Freeze receipt IDs are
`<pack_id>/projection-NNNN`; arm receipt IDs are
`<pack_id>/<bracket_session_id>/identity-pin-arm-verify`.

`receipt.pack` has exactly this key set:

```text
pack_id, plan_id, projection_input_sha256, reviewed_git_commit, window_id
```

The three IDs are nonempty strings. `reviewed_git_commit` is 40 or 64 lowercase
hexadecimal characters, and `projection_input_sha256` is 64 lowercase
hexadecimal characters (`joulewise/identity_pins.py:551-588`).

Each receipt identity unit has exactly `identity_unit_id`,
`producer_plan_reference`, `consumer_bindings`, `declared_identity`,
`config_inventory`, `model_file_inventory`, `realized_stack_identity`, and
`model_runtime_config`. The realized stack has exactly the eleven governed
stack fields. The runtime config has exactly `model_artifact_sha256`,
`runtime_identity_sha256`, and `config_set_sha256`. Each check has exactly
`check_id`, `status`, `expected`, and `observed`. `observations` has exactly
`identity_unit_count`, `platform`, and `machine`. `derivation` has exactly
`contract_id`, `callables`, `source_file_sha256`, and `git_commit`; its contract
ID is `joulewise.identity_pin_derivation.v1`. `supersedes` is an array whose
rows have exactly `pack_id`, `pack_sha256`, `projection_receipt_sha256`, and
`readiness_sha256` (`joulewise/identity_pins.py:97-156,589-740`).

No receipt or runtime-config key is added for manifest rotation. The receipt
copies the declaration unchanged into its existing `declared_identity` field,
so a rotating unit stores its common workload keys and `suite_manifest_set`
inside `declared_identity.workload_profile`. The existing config inventory
stores every occurrence, including repeated manifest classes. The existing
`config_set_sha256` stores the section 4 unit config-set digest. A legacy or
new unit with one distinct member identity therefore stores that identity hash
unchanged; a unit with several stores the domain-separated set digest.

The derivation callable list names the shared model enumerator, typed-config
constructor, scientific-config normalizer, stack builder and hasher, three-pin
derivers, adapter resolvers, powermetrics device probe, private runtime probe,
and MLX identity probe. `source_file_sha256` hashes every repository source
file that defines those callables. Arm compares contract ID, callable list,
and source-file digests; `git_commit` is provenance and is deliberately not
part of that executable-identity equality (`joulewise/identity_pins.py:1148-1210`).

| Reason code | One-sentence meaning |
|---|---|
| `readiness_identity_artifact_unreadable` | A required pack, config, model, repository, adapter, receipt, sidecar, or prompt observation cannot be read or does not have the required type or shape. |
| `readiness_identity_environment_dirty` | Current readable bytes or live runtime observations differ from the pack declaration or frozen values, including a dirty Git working tree. |
| `readiness_identity_projection_mint_divergence` | The projection cannot use the same derivation code or obtain the same model/config result as the shared mint path. |
| `readiness_identity_pinset_frozen_mismatch` | Frozen pack state, pins, receipt bytes, receipt binding, successor state, or idempotent re-derivation disagree. |
| `readiness_identity_receipt_namespace_anomalous` | The committed projection-receipt directory contains a nonconforming entry or another namespace condition that could hide or collide with a receipt. |

No new refusal code is needed. A well-shaped declaration whose common profile,
manifest membership, emitted census, per-manifest identity, or distinct
identity count differs from emitted configurations uses
`readiness_identity_environment_dirty`. A malformed `suite_manifest_set`,
member row, relative reference, digest, or count uses
`readiness_identity_artifact_unreadable`. A derived unit config-set digest or
representative runtime pin that disagrees with the shared derivation uses
`readiness_identity_projection_mint_divergence`.

The generic code preserves identity-unit order and requires unique nonempty
IDs, but does not itself enforce a pack-specific alpha/beta/gamma roster or
unit count (`joulewise/identity_pins.py:497-538`). Pack-specific producers and
validators must supply that policy.

## 8. Worked two-config example

Suppose `ToyTokenizer.encode("ABCD", add_special_tokens=True)` returns the four
integers `[11,22,33,44]`. The exact token-hash preimage is the UTF-8 byte string
`joulewise.prompt_token_ids.v1\0[11,22,33,44]`, where `\0` is one byte of value
zero. Its SHA-256 is:

```text
10e6c1854858d7cdd278400c11706ebd2a43fe79ffa241bd5c1d0f6fe665a9fe
```

One identity unit has two configs, `configs/member-1.json` and
`configs/member-2.json`. Each of the next two fences is the complete raw file:
one compact JSON line followed by exactly one line-feed byte (`0a` hexadecimal).
The first file is:

```json
{"hardware_target":{"id":"example-mac","runtime_backend":"mlx","telemetry_backend":"powermetrics","transport":"local"},"interconnect":{"name":"local"},"model":{"family":"toy","name":"toy-model","revision":"r1","source":"/models/toy.safetensors","weight_format":"mlx"},"quantization":{"bits":4,"name":"int4"},"run_id":"run-1","run_metadata":{"operator":"reader","project":"example","tags":["phase2","rep1"]},"sampling":{"idle_seconds":1.0,"power_hz":10.0},"schema_version":"0.1","workload_profile":{"name":"toy-prefill","output_tokens":1,"prompt_text":"ABCD","prompt_token_expectation":{"schema_version":"joulewise.prompt_token_expectation.v1","token_count":4,"token_hash_domain":"joulewise.prompt_token_ids.v1","token_ids_sha256":"10e6c1854858d7cdd278400c11706ebd2a43fe79ffa241bd5c1d0f6fe665a9fe"},"repetitions":1,"warmup_runs":1}}
```

The second file is:

```json
{"hardware_target":{"id":"example-mac","runtime_backend":"mlx","telemetry_backend":"powermetrics","transport":"local"},"interconnect":{"name":"local"},"model":{"family":"toy","name":"toy-model","revision":"r1","source":"/models/toy.safetensors","weight_format":"mlx"},"quantization":{"bits":4,"name":"int4"},"run_id":"run-2","run_metadata":{"operator":"reader","project":"example","tags":["phase2","rep2"]},"sampling":{"idle_seconds":1.0,"power_hz":10.0},"schema_version":"0.1","workload_profile":{"name":"toy-prefill","output_tokens":1,"prompt_text":"ABCD","prompt_token_expectation":{"schema_version":"joulewise.prompt_token_expectation.v1","token_count":4,"token_hash_domain":"joulewise.prompt_token_ids.v1","token_ids_sha256":"10e6c1854858d7cdd278400c11706ebd2a43fe79ffa241bd5c1d0f6fe665a9fe"},"repetitions":1,"warmup_runs":1}}
```

SHA-256 over those exact bytes gives, respectively,
`5bee74bfc11a663e7b4c364d24c33883930438a60d126d99ab400a4e7cfa9805`
and `bca6b55f312abf6783a5eed1297c9d45de2f86e9197f60394d4f16dca95400b0`.
Both files normalize through the real typed constructor and the section 2 tag
predicate to this identical canonical scientific-identity JSON:

```json
{"hardware_target":{"device_kind":null,"host":null,"id":"example-mac","notes":null,"runtime_backend":"mlx","telemetry_backend":"powermetrics","transport":"local"},"interconnect":{"link_speed_mbps":null,"name":"local","notes":null},"model":{"context_window":null,"family":"toy","name":"toy-model","revision":"r1","source":"/models/toy.safetensors","weight_format":"mlx"},"quantization":{"bits":4,"group_size":null,"name":"int4"},"run_metadata":{"tags":["phase2"]},"sampling":{"idle_seconds":1.0,"power_hz":10.0,"warmup_seconds":0.0},"schema_version":"0.1","workload_profile":{"dataset_ref":null,"name":"toy-prefill","output_tokens":1,"prompt_text":"ABCD","prompt_token_expectation":{"schema_version":"joulewise.prompt_token_expectation.v1","token_count":4,"token_hash_domain":"joulewise.prompt_token_ids.v1","token_ids_sha256":"10e6c1854858d7cdd278400c11706ebd2a43fe79ffa241bd5c1d0f6fe665a9fe"},"prompt_tokens":null,"repetitions":1,"warmup_runs":1}}
```

Its SHA-256 is
`95367df3b83bf6995b5d054f5d21114744b14614b999071a801b3189c107c019`.
The raw files differ only in `run-1`/`run-2` and `rep1`/`rep2`; `run_id` is
removed, and the full-match repetition tags are removed by the stated
predicate.

The four model bytes are `TOY\n`, whose SHA-256 is
`6361d8e661d28948e82e68ed04a7d5becdc39bc6a94176bd805003b90991fdfb`.
The complete eleven-field canonical stack JSON is:

```json
{"batching_concurrency_policy":"single-request sequential","hardware_unit":{"config_id":"example-mac","device":"example-mac","machine":"arm64"},"kernel_library":"metal-x","measurement_boundary_label":{"boundary":"example package","rails":["cpu_power","gpu_power"]},"model_artifact_sha256":"6361d8e661d28948e82e68ed04a7d5becdc39bc6a94176bd805003b90991fdfb","os_version":"ExampleOS-1","quantization":{"bits":4,"group_size":null,"name":"int4"},"runtime_version":{"adapter":"mlx_runtime","name":"mlx","version":"1.2.3"},"sampler_output_policy":{"output_policy":{"name":"fixed_budget_exact","requested_tokens":1,"stop_condition":"requested_tokens_emitted"},"sampler":{"api":"mlx_lm.make_sampler","kind":"greedy","parameter":"temp","pinned":true,"temperature":0.0}},"telemetry_backend":"powermetrics","tokenizer_identity":{"backend":"mlx","class":"ToyTokenizer","identifier":"tokenizer.json","revision":"r1","vocab_size":256}}
```

SHA-256 over `joulewise.stack_identity.v1`, one NUL byte, and that stack line
is `e2dc2bd8a10f4f4029443d824ed21756d5d3146671998b12324d7791685c4e36`.

The realization row for member 2 is:

```json
{"config_path":"configs/member-2.json","token_count":4,"token_hash_domain":"joulewise.prompt_token_ids.v1","token_ids_sha256":"10e6c1854858d7cdd278400c11706ebd2a43fe79ffa241bd5c1d0f6fe665a9fe"}
```

For exact replication, the complete canonical projection-input byte string is
the following single UTF-8 line; the displayed newline after it belongs to the
Markdown fence, not to the hash input:

```json
[{"config_inventory":[{"path":"configs/member-1.json","sha256":"5bee74bfc11a663e7b4c364d24c33883930438a60d126d99ab400a4e7cfa9805"},{"path":"configs/member-2.json","sha256":"bca6b55f312abf6783a5eed1297c9d45de2f86e9197f60394d4f16dca95400b0"}],"consumer_bindings":[{"arm":"A","family":"toy-family","measurement_arm":"prefill"}],"declared_identity":{"hardware_target":"example-mac","model_name":"toy-model","model_revision":"r1","model_source":"/models/toy.safetensors","quantization":{"bits":4,"group_size":null,"name":"int4"},"runtime_backend":"mlx","telemetry_backend":"powermetrics","workload_profile":{"dataset_ref":null,"name":"toy-prefill","output_tokens":1,"prompt_text":"ABCD","prompt_token_expectation":{"schema_version":"joulewise.prompt_token_expectation.v1","token_count":4,"token_hash_domain":"joulewise.prompt_token_ids.v1","token_ids_sha256":"10e6c1854858d7cdd278400c11706ebd2a43fe79ffa241bd5c1d0f6fe665a9fe"},"prompt_tokens":null,"repetitions":1,"warmup_runs":1}},"identity_unit_id":"toy/prefill","model_artifact_identity":{"algorithm":"sha256","inventory":[{"path":"toy.safetensors","resolved_path":"/models/toy.safetensors","sha256":"6361d8e661d28948e82e68ed04a7d5becdc39bc6a94176bd805003b90991fdfb","size_bytes":4,"symlink":false}],"kind":"single_file","path":"/models/toy.safetensors","sha256":"6361d8e661d28948e82e68ed04a7d5becdc39bc6a94176bd805003b90991fdfb","status":"ok"},"probe_metadata":{"adapters":{"runtime":{"name":"mlx","prepare_metadata":{"adapter":"mlx_runtime","batching_concurrency_policy":"single-request sequential","kernel_library":"metal-x","quantization":"int4","version":"1.2.3"}},"telemetry":{"name":"powermetrics"}},"device":{"boundary":"example package","device":"example-mac","rail_manifest":["cpu_power","gpu_power"],"telemetry":"powermetrics"},"machine":"arm64","platform":"ExampleOS-1","prompt_realizations":[{"config_path":"configs/member-1.json","token_count":4,"token_hash_domain":"joulewise.prompt_token_ids.v1","token_ids_sha256":"10e6c1854858d7cdd278400c11706ebd2a43fe79ffa241bd5c1d0f6fe665a9fe"},{"config_path":"configs/member-2.json","token_count":4,"token_hash_domain":"joulewise.prompt_token_ids.v1","token_ids_sha256":"10e6c1854858d7cdd278400c11706ebd2a43fe79ffa241bd5c1d0f6fe665a9fe"}],"quantization":{"bits":4,"group_size":null,"name":"int4"},"workload_provenance":{"model":{"artifact_identity":{"algorithm":"sha256","inventory":[{"path":"toy.safetensors","resolved_path":"/models/toy.safetensors","sha256":"6361d8e661d28948e82e68ed04a7d5becdc39bc6a94176bd805003b90991fdfb","size_bytes":4,"symlink":false}],"kind":"single_file","path":"/models/toy.safetensors","sha256":"6361d8e661d28948e82e68ed04a7d5becdc39bc6a94176bd805003b90991fdfb","status":"ok"},"name":"toy-model","revision":"r1","source":"/models/toy.safetensors"},"output_policy":{"name":"fixed_budget_exact","requested_tokens":1,"stop_condition":"requested_tokens_emitted"},"prompt_realization":{"token_count":4,"token_hash_domain":"joulewise.prompt_token_ids.v1","token_ids_sha256":"10e6c1854858d7cdd278400c11706ebd2a43fe79ffa241bd5c1d0f6fe665a9fe"},"sampler":{"api":"mlx_lm.make_sampler","kind":"greedy","parameter":"temp","pinned":true,"temperature":0.0},"tokenizer":{"backend":"mlx","class":"ToyTokenizer","identifier":"/models/tokenizer.json","revision":"r1","vocab_size":256}}},"producer_plan_reference":{"path":"producer_contract.json","plan_id":"toy-plan"}}]
```

SHA-256 over that line is
`6d3a16628cdda16cfd1b0bc3fba680b600e5e25e15f606986aa9ed92967fd1cd`.
The derived three-pin value is:

```json
{"config_set_sha256":"95367df3b83bf6995b5d054f5d21114744b14614b999071a801b3189c107c019","model_artifact_sha256":"6361d8e661d28948e82e68ed04a7d5becdc39bc6a94176bd805003b90991fdfb","runtime_identity_sha256":"e2dc2bd8a10f4f4029443d824ed21756d5d3146671998b12324d7791685c4e36"}
```

### Two-manifest decode extension

The following values are computed example values, not production campaign
pins. Let the exact example manifest bytes be `example decode manifest one`
plus one line-feed byte and `example decode manifest two` plus one line-feed
byte. Their real SHA-256 digests are, respectively:

```text
ea6cbc2e9870340c7b9ec85d64ec861ce53b7ca6f927bf72eff73add97f36732
f6130adccb590d06e952c8034fc36e080884980444a1ce441ee1c303cac58c3b
```

Starting from the canonical scientific identity shown earlier in this section,
replace only its `workload_profile`. Member 1 uses this exact canonical
workload object:

```json
{"dataset_ref":null,"name":"toy-rotating-decode","output_tokens":null,"prompt_text":null,"prompt_tokens":null,"repetitions":1,"suite_manifest_ref":"manifests/decode-1.json","suite_manifest_sha256":"ea6cbc2e9870340c7b9ec85d64ec861ce53b7ca6f927bf72eff73add97f36732","warmup_runs":1}
```

Member 2 uses:

```json
{"dataset_ref":null,"name":"toy-rotating-decode","output_tokens":null,"prompt_text":null,"prompt_tokens":null,"repetitions":1,"suite_manifest_ref":"manifests/decode-2.json","suite_manifest_sha256":"f6130adccb590d06e952c8034fc36e080884980444a1ce441ee1c303cac58c3b","warmup_runs":1}
```

All other canonical scientific-identity fields remain byte-for-byte those in
the earlier example. SHA-256 over the two complete canonical scientific
identities gives these member scientific identities:

```text
3303662e78c6c9ac83a48d7c719a67e005d21c82ad0760ad745cdacc382873f9
cb04695ea87d9a1eb91da89305a8d999d21285e9434c61f306e75ca1756959a1
```

The declaration removes the two per-member manifest fields, retains every
other typed workload field, and appends the ordered declared manifest set:

```json
{"dataset_ref":null,"name":"toy-rotating-decode","output_tokens":null,"prompt_text":null,"prompt_tokens":null,"repetitions":1,"suite_manifest_set":[{"declared_member_count":1,"suite_manifest_ref":"manifests/decode-1.json","suite_manifest_sha256":"ea6cbc2e9870340c7b9ec85d64ec861ce53b7ca6f927bf72eff73add97f36732"},{"declared_member_count":1,"suite_manifest_ref":"manifests/decode-2.json","suite_manifest_sha256":"f6130adccb590d06e952c8034fc36e080884980444a1ce441ee1c303cac58c3b"}],"warmup_runs":1}
```

The exact unit config-set preimage is the following three UTF-8 lines with no
line-feed after the last hash:

```text
joulewise.identity_unit_config_set.v1
3303662e78c6c9ac83a48d7c719a67e005d21c82ad0760ad745cdacc382873f9
cb04695ea87d9a1eb91da89305a8d999d21285e9434c61f306e75ca1756959a1
```

Its SHA-256, and therefore this example unit's `config_set_sha256`, is
`7462f88bc7188c4630ab27e554a1be4a59aeae310a5fe16936b320c505caf4c9`.
Reversing input order produces the same digest because the two member hashes
are sorted before joining; changing either manifest binding produces a
different member identity and therefore a different set digest.

The member-2 PASS check and the relevant freeze-receipt fragment are:

```json
{
  "pack": {
    "projection_input_sha256": "6d3a16628cdda16cfd1b0bc3fba680b600e5e25e15f606986aa9ed92967fd1cd"
  },
  "checks": [{
    "check_id": "toy/prefill:configs/member-2.json:shared_mint_projection:prompt_realization",
    "status": "PASS",
    "expected": {"token_count": 4, "token_hash_domain": "joulewise.prompt_token_ids.v1", "token_ids_sha256": "10e6c1854858d7cdd278400c11706ebd2a43fe79ffa241bd5c1d0f6fe665a9fe"},
    "observed": {"token_count": 4, "token_hash_domain": "joulewise.prompt_token_ids.v1", "token_ids_sha256": "10e6c1854858d7cdd278400c11706ebd2a43fe79ffa241bd5c1d0f6fe665a9fe"}
  }]
}
```

This is a fragment, not a standalone receipt; section 7 gives the mandatory
complete key set.

Now swap only the tokenizer result for member 2 to `[11,22,33,45]`. Its exact
preimage ends in `[11,22,33,45]` and hashes to
`62a91911d641748e89ca36775d31747c0e83ce6ea0e9ba6c794b52ef65933b35`.
At freeze, `scripts/project_identity_pins.py` prints this exact stable refusal
payload and exits 2:

```json
{
  "message": "config configs/member-2.json registered prompt realization differs for token_ids_sha256",
  "observed": {
    "config_path": "configs/member-2.json",
    "differing_fields": ["token_ids_sha256"],
    "expected": {"token_count": 4, "token_hash_domain": "joulewise.prompt_token_ids.v1", "token_ids_sha256": "10e6c1854858d7cdd278400c11706ebd2a43fe79ffa241bd5c1d0f6fe665a9fe"},
    "observed": {"token_count": 4, "token_hash_domain": "joulewise.prompt_token_ids.v1", "token_ids_sha256": "62a91911d641748e89ca36775d31747c0e83ce6ea0e9ba6c794b52ef65933b35"}
  },
  "reason_codes": ["readiness_identity_environment_dirty"],
  "status": "REFUSE"
}
```

At arm the same difference is captured in the external REFUSE receipt and in
its `frozen_projection_reverification` check; the pack remains byte-identical.

For a second non-happy path, leave both configs and the frozen pack unchanged
but replace the single model byte `Y` with `Z`, so the model file becomes the
four bytes `TOZ\n`. The real SHA-256 of those bytes is
`89da779ae2224b826aee3408c1a107cede3bc2e3c4089c80ea81bfde592eb14f`.
At arm, the re-derived `model_artifact_sha256` is that new digest rather than
the frozen `6361d8...fdfb`, so `verify_frozen_projection` writes a REFUSE arm
receipt with `reason_codes` equal to
`["readiness_identity_environment_dirty"]`. The changed external model bytes
remain untouched by arm; only the external custody receipt is written.

## 9. Freeze-to-launch timeline

```text
[BOX D — DESK]
reviewed pack + configs + model/tokenizer/runtime environment
        |
        | ARROW F — freeze_projection:
        | RE-DERIVE model, config, stack, and every registered prompt
        v
[BOX F — FROZEN PACK]
plan_tree + frozen three-pin values + PACK-CUSTODY freeze receipt/sidecar
        |
        | ARROW A — verify_frozen_projection during arm:
        | RE-DERIVE again; write only to WINDOW CUSTODY
        v
[BOX A — ARM RESULT]
PASS or REFUSE arm-reverification receipt/sidecar
        |
        | ARROW L — launch_window:
        | REPLAY/AUTHENTICATE receipt and consumption bindings;
        | DO NOT RE-DERIVE model, runtime, tokenizer, or prompt
        v
[BOX L — LAUNCHED COLLECTION]
execve of the reviewed window command; physical energy is collected
        |
        | ARROW B — succeeded-bundle validation:
        | compare bundle-recorded prompt evidence after physical work
        v
[BOX B — POST-HOC BUNDLE GATE]
PASS, evidence-missing, evidence-inconsistent, or realization-mismatch
```

Every box is named `D`, `F`, `A`, `L`, or `B`; every arrow is named `F`, `A`,
`L`, or `B`. Only arrows F and A re-derive. Arrow L only replays authenticated
bytes. Arrow B is too late to save the night, which is the interval owned by
`V5-LAUNCH-REALIZATION-RECHECK-01`.

## 10. Tests that pin the clauses

| Clause | Pinning test |
|---|---|
| Shared-mint three-pin equality | `tests.test_identity_pins.SharedDerivationTests.test_synthetic_pack_triple_equals_generalized_mint_rederivation` |
| Sorted multi-identity set digest and unchanged single-identity case | `tests.test_identity_pins.SharedDerivationTests.test_identity_unit_set_digest_uses_sorted_distinct_hashes` |
| Common workload projection removes only the two manifest fields | `tests.test_identity_pins.SharedDerivationTests.test_common_profile_projection_removes_only_member_manifest_binding` |
| Committed v3 single-identity digest remains byte-identical | `tests.test_identity_pins.SharedDerivationTests.test_single_identity_set_digest_matches_committed_v3_receipt` |
| Lexical model inventory and file-link behavior | `tests.test_identity_pins.SharedDerivationTests.test_directory_inventory_is_lexical_and_file_symlink_records_target` |
| Exact receipt, sidecar binding, freeze mutation, and idempotence | `tests.test_identity_pins.ProjectionLifecycleTests.test_freeze_writes_authenticated_exact_key_receipt_and_is_idempotent` |
| Arm is pack-read-only and custody emission is idempotent | `tests.test_identity_pins.ProjectionLifecycleTests.test_verify_is_pack_read_only_and_writes_custody_receipt` |
| One changed model byte changes the pin and refuses | `tests.test_identity_pins.ProjectionLifecycleTests.test_one_byte_model_perturbation_changes_hash_and_refuses_dirty` |
| No expectation means the exact legacy probe/check key sets | `tests.test_identity_pins.PromptRealizationProjectionTests.test_legacy_projection_probe_and_checks_keep_exact_key_sets` |
| Every registered config is checked; refusal preserves pack bytes | `tests.test_identity_pins.PromptRealizationProjectionTests.test_freeze_checks_every_registered_config` |
| All three differing prompt fields are named | `tests.test_identity_pins.PromptRealizationProjectionTests.test_freeze_mismatch_names_all_differing_fields` |
| Each arm-time count/hash/domain drift yields REFUSE | `tests.test_identity_pins.PromptRealizationProjectionTests.test_arm_reverification_refuses_each_prompt_realization_drift` |
| Missing row or runtime hook is artifact-unreadable | `tests.test_identity_pins.PromptRealizationProjectionTests.test_projection_refuses_unavailable_registered_realization` |
| Check ID shape, PASS status, equality, and four-key envelope | `tests.test_identity_pins.PromptRealizationProjectionTests.test_projection_check_ids_carry_shared_mint_projection` |
| Digit-string count is unreadable at freeze and arm | `tests.test_identity_pins.PromptRealizationProjectionTests.test_digit_string_token_count_refused_at_freeze_and_arm_reverification` |
| One prepare, all config projections, one cleanup | `tests.test_identity_pins.PromptRealizationProjectionTests.test_runtime_probe_prepares_and_cleans_up_once_for_two_configs` |
| Realization rows are inside `projection_input_sha256` and the receipt | `tests.test_identity_pins.PromptRealizationProjectionTests.test_projection_input_sha256_binds_realization_rows` |
| Generated v5 manifest rotation freezes and arm-verifies | `tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_generated_v5_pack_freezes_and_verifies` |
| Declared manifest file bytes are authenticated at freeze and arm re-verification | `tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_generated_v5_pack_refuses_tampered_declared_manifest_bytes` and `test_generated_v5_verify_refuses_tampered_declared_manifest_bytes` |
| Unlisted manifest, wrong census, old retyped declaration, and drifted member tag refuse | `tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_generated_v5_pack_refuses_unlisted_decode_manifest`, `test_generated_v5_pack_refuses_declared_census_off_by_one`, `test_generated_v5_pack_refuses_retyped_decode_declaration`, and `test_generated_v5_pack_refuses_drifted_member_tag` |
| Analysis reaches the U8-bound frozen set and admits only subset-bound multi-identity transport | `tests.test_analysis_inputs.FrozenConsumerIdentitySetTests.test_u8_freeze_receipt_reaches_committed_v3_member_identity_set` and `test_multi_identity_transport_requires_declared_subset_and_skips_exact_cell` |
| Analysis labels a directly missing pack root, unauthenticated declarations, and undeclared identities on the production path, with an authenticated control | `tests.test_analysis_inputs.FrozenConsumerIdentitySetTests.test_missing_pack_root_refuses_with_unauthenticated_label`, `test_production_refuses_unauthenticated_frozen_identity_set_with_named_reason`, `test_production_refuses_identity_outside_authenticated_set_with_named_reason`, `test_production_refuses_legacy_multi_identity_without_declaration_with_named_reason`, and `test_production_accepts_same_authenticated_fixture_without_receipt_perturbation` |
| Operator cannot pass or serialize identity overrides | `tests.test_identity_pins.DerivationOnlyArmPathTests.test_cli_and_public_arm_callables_accept_no_identity_values`, `test_cli_refuses_unknown_identity_override_options`, and `test_unprojected_pack_refuses_serialized_operator_pin_values` |
| Closed five-code vocabulary | `tests.test_identity_pins.DerivationOnlyArmPathTests.test_projection_reason_vocabulary_is_closed` and `test_projection_reasons_are_registered_in_d078_decision_vocabulary` |
| Every projection refusal code becomes an arm-readiness row refusal | `tests.test_arm_readiness_integration.ArmReadinessIntegrationTests.test_all_five_u11_refusals_propagate_through_identity_row` |
| Refusal registry covers dynamically propagated projection codes | `tests.test_arm_readiness_integration.ArmReadinessIntegrationTests.test_refusal_registry_coverage_and_defensive_unreachable_justifications` |
| Launch does not re-derive after arm | No test in these two modules pins this negative boundary; the executable evidence is `scripts/launch_window.py:102-167,239-280`, and `V5-LAUNCH-REALIZATION-RECHECK-01` is the named follow-up. |

The launch boundary is scheduled to move under that final row: the named
follow-up will re-derive after `verify_consumed_launch` and before
`RunBundleWriter.create`.

## 11. Provenance of these rules

The preceding sections are self-contained; the labels here only trace their
policy sources. Rulings 44c and 150a R-150-4 are the source of the seven-key
projection-input allowlist and the exclusion of packaging versions that do not
change a hashed output. Ruling 150a R-150-2 owns the scheduled launch-time
recheck. D-119 is the source of the rule that assurance wording may be no
stronger than the evidence named with it. D-131 is the broader pack-specific
alpha/beta/gamma roster policy; the `_v5` GAMMA generator enforces its exact
ordered four-unit roster in addition to the generic validator.
