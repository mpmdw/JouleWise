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

Complete archives are compressed as `archive.tar.xz` without rewriting their bytes. `INDEX_ENTRY.json` preserves their original synthetic paths and indexed record digest. Normal loading extracts a private temporary copy, relocates its synthetic locators and rebinds the hashes covering those changes. The committed archive and index remain byte-identical. Temporary roots use the platform's default temporary directory; loading needs no `/private/tmp` directory or shared machine path.

## S0 closing rebuild, 2026-10-12

All ten cases were rebuilt with distinct ledger capture bounds and matching
bracket candidates. `POST_CAPTURE_BOUND_MARKER_S` is exactly `0.001` seconds;
ALPHA's pre/post pair is `0.025`/`0.026`. The `NOT_USABLE` case is a synthetic
BETA attempt and uses `0.026`/`0.027`. The operative value is computed by the
exported commit's real calibration bracket evaluator, never copied from an
endpoint. `PROGRAM_STRUCTURE.json` records the exported program's loss-code
list, allowing M4 to be checked at both pins.

Exact fresh export command, repository-root cwd (directory created first):

```sh
git archive 224a264c5faaae90cdf56118df37e773a932700b | tar -x -C .scratch-s0/pin2-close/
```

Copy `tests/b5_analysis/{__init__,fixtures}.py` and
`configs/analysis/b5/seal_pins.json` to their same paths in the export, then copy
`tests/{test_harvest_b5_window,test_harvest_b5_sources,test_harvest_b5_trigger_scope}.py`
to `tests/b5_analysis/support/`. These are added support files; every tracked
program file remains the pinned commit's bytes.

Exact rebuild command, cwd `.scratch-s0/pin2-close/`:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp JW_B5_SYNTHETIC_ONLY=1 B5_S0_EXPORT_PIN=224a264c5faaae90cdf56118df37e773a932700b /opt/homebrew/bin/python3.13 -m tests.b5_analysis.fixtures pin2 /Users/edr/code/JouleWise-wt-l9/tests/fixtures/b5_analysis/pin2 > /Users/edr/code/JouleWise-wt-l9/.scratch-s0/pin2-close-build.log 2>&1
```

The prior fixture-writing repository commit was
`88a3303accf1d392cac88412752c16a572dd9be3`. This rebuild is intentionally
uncommitted pending the lead's review.

Builder SHA-256 (the copied `tests/b5_analysis/fixtures.py`):
`e4d5e6068d8e92c127b0cb9f8800f9b1badbd2e82b94e870a65c6fa2fd3df291`.
