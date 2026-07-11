# REPRO-002 Publication Privacy Run Report

Date: 2026-07-11  
Branch/base: `impl/repro002` at `f4fd36e41a68`  
Lane: `[AGENT]` (no quiet-machine measurement)  
Disposition: implementation complete in worktree; no commit, release, upload,
or shared-state bookkeeping performed

## Planning reflection and intake

Goal: implement the adjudicated C2 fail-closed publication privacy audit and a
transformed public-pack path without changing private bundles.

The run began with Mission M0. I read the active stop card, Current Project
Status, Known Workspace State, What Is Next, the Current Queue and Do-Not-Do-
Yet list, the agent-plan source map, and the planning-reflection protocol. The
active stop card authorizes the Ed-directed REPRO-002 stream; the scheduling
scout marks it START-NOW and disjoint from p2041/p2037. I then read the C2
adjudication, REPRO-001/DOC-009 spec, run-bundle contract, existing packer and
tests, and the REPRO-002 scheduling/delegation contract including its post-#49
amendment.

The task ranks ahead of ordinary queue work because REPRO-002 is a P1 gate
required before any public bundle release and the user explicitly assigned its
isolated worktree. Evidence required was: fail-closed source/path inventory,
immutable-source transformation, a source/operation/output hash chain,
secret-bearing tests, refusal mutations, pack tamper detection, focused tests,
and the canonical suite.

Inherited assumptions:

- strict-valid private bundles remain the full raw-evidence authority;
- public output may be transformed and must never be described as byte-
  identical;
- unknown public surfaces fail closed rather than being copied optimistically;
- no private corpus content belongs in fixtures; synthetic markers only;
- no CLI/reducer/schema/shared-state/generated-site changes and no `runs/`
  writes are permitted; and
- the lead owns final diff review, integration, commit, and publication acts.

Nonblocking failures would be recorded as refusal verdicts. A field/path that
cannot be classified is therefore a successful privacy failure, not a reason
to weaken the policy. This run intentionally did not change live measurement
methods, schemas, retained bundles, or public release state.

## Implementation

### Fail-closed audit and transformation

Added `joulewise/publication_privacy.py` with:

- an exact source artifact-path inventory;
- frozen config, metadata-top-level, event-top-level, summary-top-level, and
  `measurement_quality` field inventories;
- exact retained power-trace columns plus governed source/rail values;
- source tree hashing before and after transformation;
- deterministic public ids derived from the private source-tree hash, without
  serializing the private run id;
- structured JSON/JSONL redaction for config, metadata, events, summary, paths,
  identities, prompt/response content, failure strings, and open/dynamic
  summary subtrees;
- omission of prompts/responses/token streams, suite source manifests, logs,
  worker logs, raw backend captures, and rich telemetry, with each omission
  hash-accounted;
- an explicit `remote_cleanup_failed` path-redaction rule while preserving the
  `runtime_cleanup_ok` boolean/null union; and
- post-write public privacy verification plus fail-and-delete behavior if the
  private source changes concurrently.

The source tree is only read. Transformation creates a fresh destination and
removes it on any failure.

### Packer integration

`scripts/package_bundle_pack.py` now creates
`joulewise.public_bundle_pack.v2` packs. It still requires every private input
to be strict-valid and succeeded, then requires the privacy audit before
claiming the output directory.

The pack contains `MANIFEST.json`, `TRANSFORMATION_MANIFEST.json`, `README.md`,
and pseudonymous public bundle directories. For every private source file the
transformation manifest records relative path, classification, operation,
source SHA-256/size, output SHA-256/size or null, and `byte_identical`. Bundle
and top-level records explicitly assert non-byte-identity and bind private and
public tree hashes. Neither private source paths nor private run ids are
serialized.

Verification checks the exact root/bundle file sets, both manifest chains,
source-inventory and public-tree folds, path-policy/classification/operation
  agreement, classification counts, public-id derivation, every output hash and
size, per-file byte-identity flags, and public privacy invariants. A test
changes a public trace and rehashes the ordinary pack manifest; verification
still fails against the independently bound transformation record.

The generated README no longer instructs strict validation or re-reduction of
the transformed projection. It states that omitted private evidence prevents
that claim.

## Classification summary

| Class | Included surfaces | Public result |
|---|---|---|
| Retain reviewed measurement | `power_trace.csv` with exact columns and governed sources/rails | Byte-retained numeric projection |
| Transform reviewed structure | config, metadata, events, summary | Pseudonymize/redact governed values; retain only reviewed scalar metrics/hashes/bounds; null open summary subtrees; unknown governed fields refuse |
| Omit prompt/response/token content | suite manifest and all output payloads | No public file; source hash/size and omission recorded |
| Omit controller/worker logs | three controller logs and exact remote-worker log filename class | No public file; source hash/size and omission recorded |
| Omit backend-native/rich telemetry | known raw mock/powermetrics/NVIDIA/vLLM files and rich telemetry | No public file; source hash/size and omission recorded |
| Refuse unknown | any other path, config field, metadata top field, event top field, summary top field, quality field, trace column/source/rail, symlink, or non-file | Pack is not created (or partial output is deleted) |

The full field/path table is in `docs/contracts/publication_privacy.md`.
Post-#49 coverage is explicit: environment and remote adapter/worker subtrees
(including worker environment, paths, and log tails) are redacted wholesale;
worker logs are omitted; cleanup strings in events/metadata/summary are
redacted; remote cleanup paths are redacted per entry; `runtime_cleanup_ok`
remains visible.

## Tests and evidence

Mission M0 baseline command (unpiped to sandbox file):

```sh
python3 -m unittest discover -s tests > /private/tmp/repro002-m0-baseline.log 2>&1
```

Exact tail:

```text
----------------------------------------------------------------------
Ran 1041 tests in 69.885s

OK (skipped=13)
```

Required-case command (synthetic secrets, fail-closed mutations, concurrent
source mutation, and transformed-pack tamper):

```sh
python3 -m unittest tests.test_publication_privacy.PublicationPrivacyTests.test_secret_bearing_bundle_is_transformed_without_mutating_source tests.test_publication_privacy.PublicationPrivacyTests.test_unknown_fields_and_paths_fail_closed tests.test_publication_privacy.PublicationPrivacyTests.test_source_mutation_during_transform_refuses_and_removes_output tests.test_package_bundle_pack.BundlePackTests.test_verify_pack_catches_tamper_even_if_pack_manifest_is_rehashed > /private/tmp/repro002-required-cases-final.log 2>&1
```

Exact tail:

```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.099s

OK
```

Focused privacy/packer command:

```sh
python3 -m unittest tests.test_publication_privacy tests.test_package_bundle_pack > /private/tmp/repro002-focused-final2.log 2>&1
```

Exact tail:

```text
....................
----------------------------------------------------------------------
Ran 20 tests in 1.321s

OK
```

Canonical command (unpiped to the required sandbox file):

```sh
python3 -m unittest discover -s tests > /private/tmp/repro002-canonical-final2.log 2>&1
```

Exact tail (the earlier lines include the expected retained-corpus and
socket-sandbox skips plus the existing expected make-figures negative-test
message):

```text
----------------------------------------------------------------------
Ran 1045 tests in 69.559s

OK (skipped=13)
```

Additional checks:

```text
python3 -m py_compile joulewise/publication_privacy.py scripts/package_bundle_pack.py
git diff --check
```

Both passed with no output.

The synthetic fixture uses conspicuously fake markers only. It covers prompt,
response, absolute model/dataset/worker paths, user and host ids, controller
and remote-worker logs, environment and worker-environment values, adapter
worker metadata, cleanup paths, cleanup-failure strings,
`remote_cleanup_failed`, and `runtime_cleanup_ok`. It asserts none of the
markers occur in public bytes and every private source file hash is unchanged.
The refusal test mutates config, metadata, measurement quality, events, and the
artifact path surface.

## Files changed

- `joulewise/publication_privacy.py` (new)
- `scripts/package_bundle_pack.py`
- `tests/test_publication_privacy.py` (new)
- `tests/test_package_bundle_pack.py`
- `docs/contracts/publication_privacy.md` (new)
- `docs/report_src/appendices/A_reproducibility.md`
- `docs/run_reports/2026-07-11-repro002-publication-privacy.md` (new)

No file under `runs/`, no CLI/reducer/schema file, no generated site, and no
private fixture data changed. Per the explicit task constraint and scheduling
scout, `RUN_STATE.md` and `TASK_QUEUE.md` were not edited; the lead owns that
shared bookkeeping.

## Flagged uncertainties and integration notes

1. The privacy-safe public projection omits backend-native raw evidence,
   prompt/response/token payloads, and suite manifests. It therefore cannot
   satisfy the old REPRO-001 claim of strict external re-reduction. This is
   documented rather than hidden. A future public raw-evidence capsule needs a
   separate privacy classification and review; the fail-closed transformed
   path must remain the default.
2. The transformation verifier can recompute the source-tree commitment from
   the recorded per-file source inventory, but cannot re-read private source
   bytes on an external machine. The controlled creation step provides that
   source-byte check before and after transformation.
3. The branch is still based at the user-pinned `f4fd36e`; at final inspection
   it was three commits behind the moving `origin/main`. No rebase or merge was
   attempted. Lead integration should review any post-base bundle-layout field
   additions against the fail-closed inventory; an unknown addition will
   refuse rather than leak.
4. No publication or release was attempted. REPRO-001 external selection,
   release, and attestation remain lead/user-controlled.

## Next exact step

Lead reviews these seven paths by pathspec, rebases/merges only after checking
post-base bundle-field additions against the classification contract, reruns
the focused and canonical commands, then commits by pathspec. Shared-state
queue/run-state closure and any publication decision follow separately.
