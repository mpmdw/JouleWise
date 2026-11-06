# Qwen4Exp synthetic artifact implementation — 2026-11-06

## Scope and outcome

Implemented MISSING-1 from Saturday-kit head `97d780d59`: a deterministic
canonical-v2, full-shape artifact builder; strict synthetic/real probe
admission; synthetic report labelling; and focused tests. No official weight
file was fetched, opened, or generated from.

The sandbox has neither NumPy nor MLX/Metal. The dependency-free admission and
report tests pass; three MLX tests skip deliberately. The canonical module was
not modified and remains SHA-256
`f4ec75d16f0af0517b63e202abeef704c9a775e9111949ab003250d51d982c37`.

## Native gate (lead, pinned Saturday venv on the M3 Max)

Run these before building the full artifact:

```bash
JW_QWEN4EXP_OFFICIAL_CONFIG=/path/to/pinned/de4b8e4d/config.json \
  python -B -m unittest -v \
  tests.test_qwen4exp_synthetic_artifact.SyntheticArtifactTests.test_tiny_inventory_file_sizes_and_manifest_match_real_conversion \
  tests.test_qwen4exp_synthetic_artifact.SyntheticArtifactTests.test_official_config_prediction_is_within_half_percent_of_size_model

JW_RUN_METAL_SYNTHETIC=1 python -B -m unittest -v \
  tests.test_qwen4exp_synthetic_artifact.SyntheticArtifactTests.test_native_metal_load_and_one_forward
```

These use only tiny random fixtures plus the official *configuration*, never
official weights. The size gate's targets are the converter's own plan for the
pinned config: maxfit 210.4 GB, maxfit5 195.3 GB (decimal; 5-bit/g64 routed
experts are 5.5 bits per weight against 6.5, i.e. 15.1 GB smaller, matching the
memory model's 112.7 - 97.6 GB peak delta). An earlier 203 GB maxfit5 target
was a size-model error, not a converter error; checked against
`/private/tmp/jwsol/hf-flashnext/config.json` on 2026-11-06. Then build and probe with the externally recorded manifest
pin:

```bash
python -B scripts/qwen4exp_synthetic_artifact.py build \
  --profile maxfit --config /path/to/pinned/de4b8e4d/config.json \
  --small-files /path/to/pinned-small-files \
  --out /Volumes/JW-EXT/flashnext/models/synthetic-maxfit --seed 0

python -B scripts/qwen4exp_mbp_live.py memory --synthetic --validation-only \
  --artifact /Volumes/JW-EXT/flashnext/models/synthetic-maxfit \
  --manifest-sha256 MANIFEST_SHA256 --out /Volumes/JW-EXT/flashnext/runs/synthetic-memory.json

python -B scripts/qwen4exp_mbp_live.py performance --synthetic --validation-only \
  --prefill-step 512 --artifact /Volumes/JW-EXT/flashnext/models/synthetic-maxfit \
  --manifest-sha256 MANIFEST_SHA256 --out /Volumes/JW-EXT/flashnext/runs/synthetic-performance-512.json
```

The normal Saturday gates still apply: measurement agents unloaded, APFS
volume identity checked, no pre-existing swap, and no concurrent jobs.

## Checks run here

* `python -m unittest -v tests.test_qwen4exp_synthetic_artifact`: 6 tests,
  3 passed and 3 skipped without MLX.
* `python -m unittest -v tests.test_qwen4exp_mbp_live.ReportTests tests.test_qwen4exp_mbp_live.SourceTests`:
  9 passed.
* `python -m py_compile ...`, `git diff --check`, and the canonical-module
  SHA-256 check passed.

No quiet-machine measurement or claim-bearing gate ran. The checks caught one
CI portability issue (NumPy imported eagerly), which was corrected by making
the builder's NumPy imports lazy.
