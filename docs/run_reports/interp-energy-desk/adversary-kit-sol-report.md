Committed locally as `a29cded84` on `align/2026-11-07-adversary-kit`. Working tree clean; nothing pushed.

Added six hashed instruction variants, seven hidden-decode dose configs, exact private token accounting, config validation, and synthetic tests. Files span `joulewise/align/squeeze/`, `configs/align/squeeze/`, tests, the overlay checker, and documentation.

Verification:

- `python3.13 -B -m unittest tests.align.test_squeeze_config` — 8 passed.
- `python3.13 -B -m unittest tests.align.test_squeeze_control` — 8 passed.
- `python3.13 -B scripts/check_squeeze_overlay.py` — 7 passed against the pinned actual runner.
- Config validation, targeted compilation, and diff checks passed.
- Native MLX test skipped because MLX is absent; the lead must run `tests.align.test_squeeze_native` outside this sandbox.

The addendum’s class mapping remains provisional because its definitions weren’t available locally. Positive controls work through the generic runner; the Apple campaign driver still needs a reviewed endpoint hook. These desk checks establish no squeeze efficacy result.

[Kit documentation](/Users/edr/code/CapstoneProject/jw-wt/sol-adversary-kit/docs/align/squeeze/ADVERSARY-KIT.md) · [Run report and complete file/test inventory](/Users/edr/code/CapstoneProject/jw-wt/sol-adversary-kit/docs/run_reports/2026-11-07-adversary-kit.md)

No network, sealed-data access, full suite, real model runs, measurements, or protected coordination-file edits.