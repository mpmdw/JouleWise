# Qwen4 experimental PLE pread variant — 2026-11-06

## Scope

Implemented MISSING-8 from Saturday kit head `97d780d5` (superseding the brief's
`6cacb2be5` base). No real weights were read or generated.

## Delivered

- `scripts/qwen4exp_ple_io_variant.py` verifies the source manifest pin, refuses
  cross-volume/non-APFS derivation, APFS-clones unchanged files without a copy or
  hardlink fallback, rewrites only `config.json`'s PLE I/O recipe, preserves
  known payload digests, emits derivation provenance, verifies the result, and
  prints its new manifest pin.
- `scripts/qwen4exp_mbp_live.py` binds `--ple-io` to verified configuration.
  mmap keeps mincore and the 21.5 GB residency cap; pread records per-pass
  `vm_stat` file-backed-page delta, `ru_inblock`, and table gather seconds, and
  explicitly marks that cap inapplicable because F_NOCACHE reads bypass cache.
- Fixture tests cover both pins and APFS-volume refusal. The native test derives
  through real clonefile, loads both pins, and compares mmap/pread gathers for
  identical IDs.

## Verification

- Focused suite: 35 tests, 5 skipped, all passing.
- Syntax and diff checks passed.
- Canonical discovery was started, reached unrelated B5 analysis coverage, and
  was manually stopped after more than ten minutes; one failure marker occurred
  before the long-running test, so it is not represented as passing evidence.

## Native handoff

On the Apple-silicon live-kit checkout with MLX, mlx-lm, torch, transformers,
and APFS available, run:

```bash
python3 -m unittest -v \
  tests.test_qwen4exp_ple_io_variant.NativeVariantTests \
  tests.test_qwen4exp_mbp_live.NativeMlxTests
```

Then run the two dry-run recipes and the fixture-focused suite before using any
real artifact. Real weights remain outside automated tests.
