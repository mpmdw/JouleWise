# Synthetic fixture provenance — pin2

Program commit: `224a264c5faaae90cdf56118df37e773a932700b`. The program files match the digests in the seal record.

Export command, from the repository root:

```sh
git archive 224a264c5faaae90cdf56118df37e773a932700b | tar -x -C .scratch-s0/pin2/
```

The current `tests/b5_analysis/fixtures.py` and `configs/analysis/b5/seal_pins.json` are copied into that export. Current synthetic helper sources are added under `tests/b5_analysis/support/`; tracked program and test files remain the exported commit's bytes. The helpers execute against the export's `joulewise` and `scripts` modules.

Build command, with cwd `.scratch-s0/pin2/`:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp JW_B5_SYNTHETIC_ONLY=1 B5_S0_EXPORT_PIN=224a264c5faaae90cdf56118df37e773a932700b /opt/homebrew/bin/python3.13 -m tests.b5_analysis.fixtures pin2 /Users/edr/code/JouleWise-wt-l9/tests/fixtures/b5_analysis/pin2
```

`harvest_checkout.head` is supplied by the synthetic checkout seam because `git archive` omits `.git`; its file hashes are actual reads of the pinned program and are checked before construction. The real desk verdict writer (`run_campaign.main`) and the real pinned harvest execute; no record is converted into another pin's shape.

All member bundles use the committed mock runtime seed, with shifted synthetic stamps. Collection observers, admission observations, calibration-candidate discovery and the synthetic projection's verdict authentication are explicit test seams. This is synthetic shape evidence, not hardware or claim validation.

Complete archives are compressed as `archive.tar.xz` without rewriting their bytes. `INDEX_ENTRY.json` preserves their original synthetic paths and indexed record digest. The loader restores only the builder-owned `/private/tmp/b5-s0-*` original roots, preserving absolute-path bindings.
