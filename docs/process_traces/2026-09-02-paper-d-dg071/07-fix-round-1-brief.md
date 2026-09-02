ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: implementation
WRITE_SCOPE: ["scripts/issue_dg071_dg075_statistics.py", "tests/test_issue_dg071_dg075_statistics.py"]

# Fix round 1 on paper seat D — DG-071/DG-075 producer (luna refuter 178: three custody findings; statistics themselves reproduce to the last digit)

Checkout: `/Users/edr/code/JouleWise-wt-paper-d` (branch
`feat/2026-09-02-paper-d` at 1baf8c4c, clean). Two files only; do NOT edit
or regenerate `docs/paper/round7/dg071-dg075-statistics.{json,md}` — the
magistrate re-issues the artifact after this round. Do not commit, stash,
checkout, or push. `runs*/` is retained evidence, READ-ONLY. `TMPDIR` = a
subdirectory you create under
`<scratchpad>/`.
Python `/Users/edr/code/JouleWise/.venv/bin/python`. Named test module only.
Read `scratchpad/out/178-luna-paper-d-contract.md` and the seat brief
`scratchpad/run-paper-d2.md` (ruling R-167-1 binds; do not change any
statistic, estimator, or rounding).

## Findings to cure (all accepted by the magistrate)

1. SHOULD-FIX — `input_bundle.path` in the JSON is ABSOLUTE
   (`/Users/edr/code/JouleWise/runs_window_a10_20260725/...`). The registry
   supplier convention is repo-relative (the excursion artifact uses
   `capture_relative_path`). Cure: record the bundle path RELATIVE to the
   repository root, POSIX-separated, exactly
   `runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv`;
   keep the absolute-path comparison for the refusal check but never write
   an absolute path into the artifact. Counterfactual input for the test:
   invoke the producer from a repository root that is a symlink or a
   different mount (or simply assert on the real artifact dict) and assert
   the recorded `path` equals that literal relative string and does not
   start with `/`. Production call site: the function that assembles the
   artifact dict around `scripts/issue_dg071_dg075_statistics.py:293`.
   The artifact's determinism must now hold across checkouts at different
   absolute locations (that is the point) — add that as a test: two runs
   with `--repository-root` pointing at two directories that both contain
   the same fixture bundle produce byte-identical JSON except for nothing.
2. SHOULD-FIX — the `record_field_missing` refusal branch has no biting
   test. Cure: a fixture record lacking `interval_end_s` (the counterfactual)
   must refuse with that named reason and the same non-zero exit the other
   guards use; assert the reason string and exit code.
3. NIT — the Markdown rendering omits `q1_ms` / `q3_ms`; render them
   (six decimals, like the other ms fields) so every JSON number is in the
   MD.

## Verification

`TMPDIR=<yours> PYTHONDONTWRITEBYTECODE=1 python -m unittest
tests.test_issue_dg071_dg075_statistics` (report the tail); then run the
producer ONCE for real with `--out` under your TMPDIR and report: the
recorded `input_bundle.path`, both statistics (must be unchanged:
DG-071 median 0.12091851234436035 s / IQR 0.005975008010864258 s; DG-075
median 0.12092232704162598 s / IQR 0.005894899368286133 s), and the new
artifact sha256.

## Report

Envelope first (`claude-codex-report/v1`, genre `implementation`), then
under 50 lines.
