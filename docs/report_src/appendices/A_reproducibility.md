# Appendix A: Reproducibility

The legacy energy corpus is permanently voided. The report retains only its
input identity and explicit void artifacts:

- Input pinning: `analysis/rpt001-v2/input_manifest.json` (experiment
  manifest hashes + per-bundle tree digests).
- Void dataset placeholder: `analysis/rpt001-v2/dataset.csv`.
- Void aggregate placeholder: `analysis/rpt001-v2/aggregates.json`.
- Output hashes: `analysis/rpt001-v2/artifact_manifest.json`.

## Source-only assembly and check

Source-only assembly and `--check` are reproducible from a pristine clone:

```sh
python3 scripts/build_capstone.py --profile rpt001 --offline --check
```

This command uses tracked report and analysis sources, compares the committed
generated projection, and validates the full report assembly in memory. It
does not require the private bundles or an existing untracked build product.

## Controlled/internal full input authentication

The full route requires controlled access to the internal six-bundle corpus
(~110 MB, not in Git) so it can authenticate the pinned inputs:

```sh
python3 scripts/build_capstone.py --profile rpt001 --full --offline \
  --runs-root runs
```

After authentication, the route emits only the void placeholders and voided
claims-index row; it does not extract, aggregate, or reproduce measurements.
The corpus is not supplied by a pristine clone, so the full command is not
claimed as external full reproducibility.

## Publication privacy boundary (REPRO-002)

The six retained bundles are private, immutable evidence. Public packaging no
longer copies them verbatim. `scripts/package_bundle_pack.py` first requires a
strict-valid succeeded private source, then applies the fail-closed policy in
`docs/contracts/publication_privacy.md` to a new, transformed public
projection. Unknown fields or artifact paths refuse publication.

The public pack records a private source-tree hash, a separate public
output-tree hash, and per-file source hash, operation, output hash, byte size,
and byte-identity result in `TRANSFORMATION_MANIFEST.json`. The manifests state
that the public bundle is not byte-identical to its private source. Private
source paths and private run ids are not serialized.

Prompts, responses, token streams, logs (including remote worker logs), suite
source manifests, backend-native raw captures, rich telemetry, environment and
remote-worker subtrees, user/host identifiers, absolute paths, and free-form
cleanup/failure strings are redacted or omitted. The post-PR #49 quality-field
union is handled explicitly: `measurement_quality.remote_cleanup_failed` keeps
only redacted list entries, while the boolean/null `runtime_cleanup_ok` signal
is retained.

Consequently, the transformed pack verifies publication privacy,
transformation provenance, and public-file integrity; it is not a strict-valid
replacement for the private bundle and must not be claimed as byte-identical
or independently re-reducible raw evidence. The private corpus remains the
authority for full strict re-reduction. REPRO-001 release and external acts
remain separately gated and lead/user controlled.

A re-reducible evidence-handoff pack is only a possible future owner opt-in,
pending an affirmative privacy ruling. No such handoff is currently specified
or supplied.
