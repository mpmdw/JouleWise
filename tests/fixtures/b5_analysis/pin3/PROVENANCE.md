# Synthetic fixture provenance — pin3

Program commit: `0699abbb0881ce64b39c46ba07de568cc3848260`. The program files match the digests in the seal record.

Export command, from the repository root:

```sh
git archive 0699abbb0881ce64b39c46ba07de568cc3848260 | tar -x -C .scratch-s0/pin3/
```

The current `tests/b5_analysis/fixtures.py` and `configs/analysis/b5/seal_pins.json` are copied into that export. Current synthetic helper sources are added under `tests/b5_analysis/support/`; tracked program and test files remain the exported commit's bytes. The helpers execute against the export's `joulewise` and `scripts` modules.

Build command, with cwd `.scratch-s0/pin3/`:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp JW_B5_SYNTHETIC_ONLY=1 B5_S0_EXPORT_PIN=0699abbb0881ce64b39c46ba07de568cc3848260 /opt/homebrew/bin/python3.13 -m tests.b5_analysis.fixtures pin3 /Users/edr/code/JouleWise-wt-l9/tests/fixtures/b5_analysis/pin3
```

`harvest_checkout.head` is supplied by the synthetic checkout seam because `git archive` omits `.git`; its file hashes are actual reads of the pinned program and are checked before construction. The real desk verdict writer (`run_campaign.main`) and the real pinned harvest execute; no record is converted into another pin's shape.

All member bundles use the committed mock runtime seed, with shifted synthetic stamps. Collection observers, admission observations, calibration-candidate discovery and the synthetic projection's verdict authentication are explicit test seams. This is synthetic shape evidence, not hardware or claim validation.

These are attempt-reader excerpts: `harvest.json`, exclusions, flags, and (when emitted) the structural NEG-8 screen. Full source bundles and withheld data are intentionally omitted. `WRITER_STRUCTURE.json` records only writer status, conditions and named failures.

The corrected no-collection fixture was regenerated with the same command plus `--case NO_COLLECTION`; the input is a chain-stage journal ending before collection, not merely absent bundles.
