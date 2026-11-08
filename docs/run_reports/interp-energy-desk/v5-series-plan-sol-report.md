Committed `3517820e3` on `align/2026-11-08-v5-series-plan`. Working tree clean; no push.

Added:

- [Series plan](docs/align/squeeze/SERIES-PLAN.md): seven calibration windows, T1–T3 interleaving, physics night, seed allocations, exclusion arithmetic and 207.25-hour baseline budget.
- [Four planning templates](configs/campaigns/align_v4/series/README.md) requiring KM003C capture and sealed reasoning transcripts. They are non-armable; capture enforcement is not implemented here.
- [Handoff report](docs/align/squeeze/fanout/series-plan.md) with assumptions, uncertainties and native follow-up.

Targeted checks passed:

- `python3.13 -B -m unittest tests.test_align_v4_series_plan` — 10 tests.
- `python3.13 -B -m unittest tests.align.test_v4_w1_plan` — 12 tests.
- `python3.13 -B -m unittest tests.align.test_protocol_v4_doc` — 5 tests.

JSON, syntax, links and diff checks passed. No full suite, network, measurements or MLX execution.

Before arming, the lead must resolve the physics roster mismatch, admit the D8 reserve, and settle calibration/test score comparability and adversary threshold access. Native capture/injection qualification remains outstanding.