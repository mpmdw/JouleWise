# Appendix A: Reproducibility

Every number in the results chapter derives from the six pinned legacy
bundles under `runs/` via committed, versioned artifacts:

- Input pinning: `analysis/rpt001-v1/input_manifest.json` (experiment
  manifest hashes + per-bundle tree digests).
- Sealed dataset: `analysis/rpt001-v1/dataset.csv` (one row per bundle).
- Aggregates: `analysis/rpt001-v1/aggregates.json` (verbatim
  `aggregate_experiment()` output, Student-t fields preserved for audit).
- Output hashes: `analysis/rpt001-v1/artifact_manifest.json`.

Full regeneration (requires the local bundle corpus; ~110 MB, not in Git):

```sh
python3 scripts/build_capstone.py --profile rpt001 --full --offline \
  --runs-root /Users/edr/code/JouleWise/runs
```

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
