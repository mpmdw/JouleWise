# Publication Privacy Contract

Status: binding for REPRO-002 public-pack preparation (2026-07-11)

This contract gates every public run-bundle release. A strict-valid run bundle
is private, immutable evidence. It is never copied verbatim into a publication
pack. Publication uses the fail-closed audit and transformed projection in
`joulewise/publication_privacy.py`, integrated by
`scripts/package_bundle_pack.py`.

The public projection is deliberately not byte-identical to its private source
and is not a strict-valid replacement for that source. A publisher must not
describe it as raw evidence, an independently re-reducible private bundle, or
a byte-identical copy. Its valid claims are narrower: the pack's public file
set passed the governed privacy transformation, and both the private-source
hash inventory and public-output hash inventory are bound by the pack
manifests.

## Fail-closed rule

Every source path must match one reviewed path class. Structured publication
surfaces use frozen key inventories. The audit refuses, before creating the
pack output directory, when it encounters:

- an unknown bundle-relative path;
- a symlink or non-file artifact;
- an unknown config field at the root or in any config section;
- an unknown top-level metadata field;
- an event whose top-level keys differ from the exact five-key event contract;
- an unknown summary top-level field;
- an unknown `measurement_quality` field;
- a power-trace column other than
  `timestamp_s,power_w,source,rail`, or an unreviewed source/rail value; or
- malformed JSON, JSONL, or retained CSV.

An entire subtree may be classified as redacted or omitted. Descendants of
such a subtree are not copied, so an additive nested field cannot escape merely
because its key was new. A new field intended for public retention requires a
policy amendment, tests, and review; it must not be made public by relaxing the
default refusal.

## Path and field classification

| Private source surface | Classification | Public operation | Public result |
|---|---|---|---|
| `config.json` | reviewed structured configuration | transform JSON | Public pseudonym replaces `run_id`; model/dataset/suite/generator paths, prompt text, target host/id, operator/project/tags, and free-form notes are redacted. Absolute path-shaped retained strings are redacted. Unknown root/section fields refuse. |
| `metadata.json` governed hash/bound fields | reviewed scalar provenance | retain validated values | Config SHA-256, Git commit, and governed clock/sample/drift numeric bounds remain. Version/platform and all complex metadata surfaces are redacted so unexpected strings cannot pass through. |
| `metadata.run_id` | user/host-derived identifier risk | pseudonymize | Matches the public config id `public-<source-tree-hash-prefix>`. The private run id is absent from both pack manifests. |
| `metadata.platform`, `metadata.machine` | host identifier | redact | Identity marker only. |
| `metadata.environment` | environment, user, host, path, and secret risk | redact entire subtree | No environment member is copied. This includes package/probe errors and any additive environment values. |
| `metadata.connection` | remote host/user risk | redact entire subtree | No transport address or login identity is copied. |
| `metadata.adapters` | runtime/telemetry and remote-worker risk | redact entire subtree | Covers worker metadata, worker environment, remote state paths, server-log tails, adapter messages, prepare/cleanup metadata, and clock-alignment records. |
| `metadata.extra` | runner and cleanup risk | redact entire subtree | Covers `node_cleanup` paths, success flags, and cleanup-failure strings, plus caller-supplied additive metadata. |
| `metadata.model`, `device`, `config_warnings`, `quantization`, `clock`, `idle_baseline`, `thermal_*`, `uncertainty_evidence`, `workload_observed`, `workload_provenance`, and `suite` | identifiers, paths, prompt/response provenance, or nonessential private detail | redact entire subtree | Only an explicit redaction record remains at the top-level key. Prompt/response hashes and token provenance do not leak through metadata. |
| `events.jsonl.timestamp_s`, `event_type`, `phase` | reviewed lifecycle fields | retain | Event ordering and coarse lifecycle remain. |
| `events.jsonl.message` | free-form failure/log string | redact | Covers cleanup exceptions and other failure strings. |
| `events.jsonl.metadata` | open runtime/worker payload | redact entire subtree | Covers prompts, responses, user/host ids, paths, environment, worker data, and cleanup metadata. Unknown event top-level fields refuse. |
| `summary_metrics.json` top-level scalar metrics | derived measurement | retain | Status, scalar energy/latency/throughput values (including governed `inter_token_throughput_tokens_s`), uncertainty-status enum, and structured failure reason remain. The inter-token metric must be finite numeric or null. Unknown top-level fields refuse. |
| `idle_mean_uncertainty` | governed derived idle-power statistics | retain exact reviewed object | All 16 governed members are retained: the frozen status/method/source-artifact/correlation values; finite numeric-or-null statistics; nonnegative integer-or-null counts; lowercase SHA-256-or-null; and frozen reason-code values. `source_artifact` is the fixed bundle-relative `raw/powermetrics_idle.plist`, not a private absolute path. `source_sha256` may remain because the transformation manifest already records hashes for omitted raw artifacts; the hash discloses no prompt, path, host, or user identity. Unknown/missing members or unreviewed reason codes refuse. |
| `idle_baseline`, `uncertainty`, `phase_energy_j`, `suite_metrics`, energy term maps, `claim_eligibility`, `window_evidence_precheck`, and `summary_provenance` | nested/dynamic derived fields, including per-item identifiers and hashes | omit (`null`) | Top-level scalar results and the public trace remain; nested/open keys cannot carry unreviewed identifiers. `window_evidence_precheck` is classified as a whole subtree, so additive descendants are not copied. |
| `summary_metrics.failure_message` | free-form failure string | redact | `failure_reason` remains as its structured enum. |
| `measurement_quality.remote_cleanup_failed` | remote cleanup paths (post-PR #49) | redact each list entry | List cardinality remains; every path becomes `[REDACTED:REMOTE_CLEANUP_PATH]`. |
| `measurement_quality.runtime_cleanup_ok` | retained local cleanup union field | retain boolean/null | This field is distinct from remote cleanup paths and remains a useful quality signal. |
| Other reviewed `measurement_quality` fields | derived measurement quality | retain governed scalar/enum values | Unknown quality fields or unknown source-enum values refuse; the dynamic `phase_identifiability` map is set to null. |
| `power_trace.csv` | reviewed numeric projection | retain bytes | Exact header plus governed sources `mock`, `powermetrics`, `nvidia_smi` and rails `mock`, `cpu_power`, `gpu_power`, `ane_power`, `gpu_board` (or empty) only. Unknown columns/source/rail refuse. |
| `suite_manifest.json` | prompt/source content | omit | Source file hash and omission are recorded. |
| `outputs/response.txt`, `outputs/tokens.jsonl`, `outputs/suite_items.jsonl` | prompt/response/token content | omit | Source hashes and omissions are recorded. |
| `logs/controller.log`, `runtime.log`, `telemetry.log` | free-form log content | omit | Source hashes and omissions are recorded. |
| `logs/task-{runtime,telemetry}-<operation>-NNN_worker.log` and controlled `nvidia-smi-<operation>_worker.log` / `vllm-<operation>_worker.log` fallbacks | remote worker log content | omit | Exact governed filename classes only; other log paths refuse. |
| Known backend-native files under `raw/` | raw payload and worker-content risk | omit | Covers mock samples, powermetrics pre/run/post plists, NVIDIA run/idle CSV, and vLLM worker events/response/tokens. Other raw paths refuse. |
| `rich_telemetry*.jsonl` | open backend-native derived telemetry | omit | Source hashes and omissions are recorded. |
| Any other path or governed structured field | unknown | refuse | No output directory survives. |

The broad redaction of remote adapter and environment subtrees is deliberate.
It satisfies the post-#49 inventory amendment without trying to predict which
worker environment variable, log tail, state path, or cleanup string might be
sensitive. `remote_cleanup_failed` is handled separately in the summary so its
quality signal remains visible without its paths. The retained
`runtime_cleanup_ok` union is never confused with that list.

## Transformation and hash manifest

A public pack uses schema `joulewise.public_bundle_pack.v2` and contains:

```text
MANIFEST.json
TRANSFORMATION_MANIFEST.json
README.md
bundles/public-<source-tree-hash-prefix>/
```

The transformation manifest uses schema
`joulewise.publication_transformation.v1`. For each source file it records:

- reviewed relative path and classification;
- operation (`retain_bytes`, `transform_json`, `transform_jsonl`, or `omit`);
- source SHA-256 and source byte size;
- output SHA-256 and output byte size, or `null` for an omission; and
- the per-file `byte_identical` result.

Each bundle entry also records the private source-tree SHA-256, public
output-tree SHA-256, `byte_identical_to_private_source: false`, and
classification counts. The top-level transformation and pack manifests repeat
the non-byte-identity assertion. `MANIFEST.json` hashes the transformation
manifest; it also records the exact public file list and hashes. No private
absolute source path or private run id is serialized.

The tree hash is a SHA-256 fold over sorted relative path, file SHA-256, and
byte size. The transformer inventories the private tree before writing and
audits it again afterward. If the source changes during transformation, the
new public directory is deleted and the operation fails. Private files are
never opened for writing.

## Verification and tamper behavior

`python3 scripts/package_bundle_pack.py --verify <pack>` verifies:

- README and transformation-manifest hashes;
- exact pack-root and public-bundle file sets;
- every public file hash and size;
- source/output transformation records and their cross-manifest agreement;
- public output-tree hashes and explicit non-byte-identity; and
- the public privacy invariants, including the cleanup-field treatment.

Changing a public file and merely rehashing `MANIFEST.json` is insufficient:
the independently bound transformation output hash disagrees. Changing the
transformation manifest without updating its pack-manifest hash also fails.
The verifier does not have private bytes and therefore cannot recompute private
source hashes; those hashes are integrity commitments recorded at the
controlled transformation boundary.

## Publication boundary

This contract and tooling do not authorize a release, upload, tag, or external
message. The lead still owns source selection, final privacy review, release
approval, and the REPRO-001 external protocol. Because the public projection
omits private raw evidence, its verifier is a transformation-integrity and
privacy verifier, not the old strict re-reduction command. Any future public
raw-evidence/re-reduction capsule needs a separately reviewed privacy class and
must preserve this fail-closed default.
