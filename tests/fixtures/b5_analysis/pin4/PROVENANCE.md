# Synthetic fixture provenance — pin4

Program commit: `b039c0257d1b1d407ee9598222db3f78f6ad7beb`.
All four governing files remain the commit's exported bytes. The builder
checks their SHA-256 digests against `configs/analysis/b5/seal_pins.json`
before every producer build.

Export command, repository-root cwd (directory created first):

```sh
mkdir -p .scratch-fixtures/pin4/
git archive b039c0257d1b1d407ee9598222db3f78f6ad7beb | tar -x -C .scratch-fixtures/pin4/
```

Copy `tests/b5_analysis/{__init__,fixtures}.py` and
`configs/analysis/b5/seal_pins.json` to their same paths in the export.
Copy `tests/{test_harvest_b5_window,test_harvest_b5_sources,test_harvest_b5_trigger_scope}.py`
into `tests/b5_analysis/support/`. Those added support files execute with
virtual locations resolving fixture data inside the export; imports of
`joulewise` and `scripts` resolve to the exact pinned program on disk.
Tracked production and test files from the pin are never overwritten.

Build command, cwd `.scratch-fixtures/pin4/`:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp JW_B5_SYNTHETIC_ONLY=1 B5_S0_EXPORT_PIN=b039c0257d1b1d407ee9598222db3f78f6ad7beb /opt/homebrew/bin/python3.13 -m tests.b5_analysis.fixtures pin4 /Users/edr/code/JouleWise-wt-l9-s3/tests/fixtures/b5_analysis/pin4
```

The `--case` option can select comma-separated case names for an incremental
rebuild. `BETA_STD` was built first with `--case BETA_STD`; the remaining
cases were built by the same pinned program, selecting their names below.

`harvest_checkout.head` is supplied by the synthetic checkout seam because
`git archive` omits `.git`; file hashes are actual reads of pinned files.
The real verdict writer (`run_campaign.main`), harvest, exclusions function
and registered calibration-bracket arithmetic execute. Mock runtime bundles,
collection observers, admission observations, calibration-candidate discovery,
and projection authentication are explicit synthetic seams. This is fixture
shape evidence, never live hardware or claim validation.

Complete archives, including synthetic raw streams, are compressed as
`archive.tar.xz` without rewriting their bytes. `INDEX_ENTRY.json` retains
original synthetic paths and the record digest. Normal tests load those
committed bytes without calling git or executing the current tree's writer.
Each handle restores a private temporary copy, relocates its synthetic
locators and rebinds the hashes covering those changes. The committed archive
and index remain byte-identical. Temporary roots use the platform's default
temporary directory; loading needs no `/private/tmp` directory or shared
machine path. Each handle cleans up only its own root.

The minimal full-window case set is:

- `BETA_STD`
- `BETA_REPEAT6_REMOVED`
- `BETA_QUAD_MEMBER_REMOVED`
- `BETA_SIX_QUADS_REMOVED`
- `BETA_FIVE_QUADS_REMOVED`
- `BETA_WRITER_DROPPED_SCIENCE_MEMBER`
- `BETA_WRITER_DROPPED_REFERENCE`
- `BETA_STORED_NEG8_PASSED`
- `BETA_SOURCES_RECOVERED`
- `BETA_SOURCES_RECOVERED_REFERENCES_INSUFFICIENT`
- `GAMMA_STD`
- `GAMMA_MIDPOINT_LOST`
- `BETA_STD_S3B_ROSTER`
- `BETA_SOURCES_RECOVERED_S3B_ROSTER`

S1 structural counterfactuals, S2 ledger/capture variants, and S3 validator
counterfactuals continue to edit loaded bases in memory or disposable copies.
Every capture pair differs by the exact `0.001` second marker: BETA uses
`0.026`/`0.027`, GAMMA uses `0.027`/`0.028`. Operative bracket bounds are
computed by the pinned evaluator, never copied from an endpoint.

## Builder source receipts, 2026-10-12

`BETA_STD` builder SHA-256: `cfa11065dd06dea196020f18f647fe50db826edc8e0d482c51d362c4e644e613`.

Remaining eleven cases builder SHA-256: `aa70ba760e80731873e8bbdcbb554fb7c121a797df3bff8174e82f4b9c895301`.

Between builds, loader lifetime handling, hash-fence placement and exporter case selection were refined; successful window construction and all pinned program bytes were preserved. The later structural-helper change affects reader counterfactuals only.

## S3 part B roster-input variants, 2026-10-12

Both additional archives are written by the same program commit
`b039c0257d1b1d407ee9598222db3f78f6ad7beb`. The regeneration-only
`S3B_ROSTER` variant preserves the former `fixtures_s3b.prepare_pack_inputs`
preparation: standard inputs gain three reference-slot retry stages; both
standard and recovered-source inputs gain the planned, uninvoked
`s3b-end-spare-uninvoked` config in the end retry slot and the sealed/executed
file maps. Recovered-source inputs retain S0's retry stages and its invoked,
bundleless start spare. These inputs are prepared before the real pinned
writer and harvest run. No archived output is patched.

Fresh export command, repository-root cwd (directory created first):

```sh
mkdir -p .scratch-fixtures/pin4-s3b/
git archive b039c0257d1b1d407ee9598222db3f78f6ad7beb | tar -x -C .scratch-fixtures/pin4-s3b/
```

Copy the builder, seal pins, and the three support helpers exactly as above.
No part B helper or production file overlay is needed. Build command, cwd
`.scratch-fixtures/pin4-s3b/`:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp JW_B5_SYNTHETIC_ONLY=1 B5_S0_EXPORT_PIN=b039c0257d1b1d407ee9598222db3f78f6ad7beb /opt/homebrew/bin/python3.13 -m tests.b5_analysis.fixtures pin4 /Users/edr/code/JouleWise-wt-l9-s3/tests/fixtures/b5_analysis/pin4 --case BETA_STD_S3B_ROSTER,BETA_SOURCES_RECOVERED_S3B_ROSTER
```

Part B retains its public base names; `cached()` maps them to these committed
roster variants through `s0.build_named()`. Normal loading neither invokes
Git nor creates or reads `.scratch-s3b`.

S3B builder SHA-256: `bc1c63c2aa4d290fc4b7fef79da37bd53ba43d425f0d67babe63780205d8f5ee`.
