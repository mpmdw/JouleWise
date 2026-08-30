# Manifest-Surface Test Adjacency Policy

Mandatory minimum adjacency for every `analysis_manifest_v3.py` change:

```text
tests.test_analysis_manifest_v3
tests.test_analysis_finalizer
tests.test_analysis_integration
tests.test_pipeline_smoke_tail
tests.test_collector_analysis_manifest_id
```

For arm-vocabulary/generator changes, also require:

```text
tests.test_d117_contrast_v5_pack
tests.test_d117_gamma_d139a2_families
```

The AP-2/mock family is a mandatory shape in any manifest-surface change. “No authorized changed path in the traceback” is not evidence of unrelatedness.
