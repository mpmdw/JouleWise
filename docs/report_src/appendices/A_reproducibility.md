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

Release/packaging details land with REPRO-001.
