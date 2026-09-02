```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"clean",
  "completion":"complete",
  "summary":"DELTA CLEAN: all luna-178 findings are cured at production call sites; recorded-producer replay is byte-identical.",
  "workspace":{"base_requested":"1baf8c4c","base_mode":"exact","head_start":"a3dadadd","head_end":"a3dadadd","upstream_end":"a3dadadd","branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"decision":"DELTA CLEAN","findings":[]},
  "verification":[
    {"id":"V1","kind":"smoke","cmd":"git clone --no-checkout <checkout> <TMPDIR>/producer-681f30ce; git -C <TMPDIR>/producer-681f30ce checkout 681f30ce; /Users/edr/code/JouleWise/.venv/bin/python <TMPDIR>/producer-681f30ce/scripts/issue_dg071_dg075_statistics.py --repository-root <TMPDIR>/producer-681f30ce --out <TMPDIR>/producer-681f30ce/replay/dg071-dg075-statistics.json; cmp -s replay/…json docs/paper/round7/…json; cmp -s replay/…md docs/paper/round7/…md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["cmp json exit: 0","cmp md exit: 0"]},"expected":{"exit_code":0,"tail_regex":"cmp json exit: 0\\ncmp md exit: 0"}},
    {"id":"V2","kind":"test","cmd":"TMPDIR=<TMPDIR> PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 8 tests in 0.117s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 8 tests in .*\\n\\nOK"}}
  ],
  "flags":[{"id":"F1","kind":"verification_gap","level":"nonblocking","text":"The cross-checkout test compares JSON only; Markdown path rendering is not cross-checkout-compared.","needs":""}]
}
```

## Findings

- luna SF-1 — cured: production emits the repo-relative locator at [issue_dg071_dg075_statistics.py:276](scripts/issue_dg071_dg075_statistics.py:276); both committed artifacts render it at [JSON:5](docs/paper/round7/dg071-dg075-statistics.json:5) and [Markdown:3](docs/paper/round7/dg071-dg075-statistics.md:3).
- luna SF-2 — cured: the re-issued artifact records its actual producer commit and script digest at [JSON:16](docs/paper/round7/dg071-dg075-statistics.json:16)-[19](docs/paper/round7/dg071-dg075-statistics.json:19); replaying that producer commit is byte-identical.
- luna SF-3 — cured: `record_field_missing` is raised in production at [issue_dg071_dg075_statistics.py:167](scripts/issue_dg071_dg075_statistics.py:167)-[172](scripts/issue_dg071_dg075_statistics.py:172). The test supplies a blank `interval_end_s`, calls `main`, asserts exit 2 and the named refusal at [test_issue_dg071_dg075_statistics.py:182](tests/test_issue_dg071_dg075_statistics.py:182)-[199](tests/test_issue_dg071_dg075_statistics.py:199).
- luna NIT-1 — cured: Q1/Q3 milliseconds are rendered at [issue_dg071_dg075_statistics.py:326](scripts/issue_dg071_dg075_statistics.py:326)-[341](scripts/issue_dg071_dg075_statistics.py:341), visible at [dg071-dg075-statistics.md:15](docs/paper/round7/dg071-dg075-statistics.md:15)-[18](docs/paper/round7/dg071-dg075-statistics.md:18).

The absolute path remains an intentional execution refusal pin ([issue_dg071_dg075_statistics.py:240](scripts/issue_dg071_dg075_statistics.py:240)-[249](scripts/issue_dg071_dg075_statistics.py:249)); a checkout whose bundle exists only elsewhere cannot issue. That is correct for the exact-path custody contract; the artifact locator is portable provenance, not an alternate input-resolution mechanism.

The cross-checkout test does bite its stated JSON regression: distinct fixture paths are used at [test_issue_dg071_dg075_statistics.py:125](tests/test_issue_dg071_dg075_statistics.py:125)-[161](tests/test_issue_dg071_dg075_statistics.py:161), then JSON bytes are compared at [163](tests/test_issue_dg071_dg075_statistics.py:163). The missing-field test exercises `main`/argparse and its exit-2 handler, not merely `issue_artifacts`; it does not spawn a separate Python process.

Recorded-producer replay output:

```text
cmp json exit: 0
cmp md exit: 0
0ba0efafbdd8d2ec48ea55d08ef3c8121bb139e4fdadc35d0bb1b914c7e148f9  .../replay/dg071-dg075-statistics.json
0ba0efafbdd8d2ec48ea55d08ef3c8121bb139e4fdadc35d0bb1b914c7e148f9  .../docs/paper/round7/dg071-dg075-statistics.json
28423488767d03a381f3c8682b9998ad2af4b271147cb9f4ae214e8a0e3bf43d  .../replay/dg071-dg075-statistics.md
28423488767d03a381f3c8682b9998ad2af4b271147cb9f4ae214e8a0e3bf43d  .../docs/paper/round7/dg071-dg075-statistics.md
```

```text
Ran 8 tests in 0.117s

OK
```

Replacement draft rows:

```markdown
| DG-071 — Section 6 sampling-record interval width, line 256 | 120.918512 ms (IQR 5.975008 ms) | `docs/paper/round7/dg071-dg075-statistics.json#statistics.DG-071.median_s` and `#statistics.DG-071.iqr_s`; artifact SHA-256 `0ba0efafbdd8d2ec48ea55d08ef3c8121bb139e4fdadc35d0bb1b914c7e148f9`; producer `scripts/issue_dg071_dg075_statistics.py`, commit `681f30ce6c4f2afd5325cc944150643f63739185`, script SHA-256 `6efc3ec75ca6f59a86b8a68ff1049abbb5fba4cdf4500cb585ee3b13ead62f51`; render seconds ×1000 to 6 decimals, retaining unrounded `*_s` | historical a10 diagnostic / resolvability example | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, DF, PROJ, SYN |
| DG-075 — Section 6 record spacing, line 256 | 120.922327 ms (IQR 5.894899 ms) | `docs/paper/round7/dg071-dg075-statistics.json#statistics.DG-075.median_s` and `#statistics.DG-075.iqr_s`; artifact SHA-256 `0ba0efafbdd8d2ec48ea55d08ef3c8121bb139e4fdadc35d0bb1b914c7e148f9`; producer `scripts/issue_dg071_dg075_statistics.py`, commit `681f30ce6c4f2afd5325cc944150643f63739185`, script SHA-256 `6efc3ec75ca6f59a86b8a68ff1049abbb5fba4cdf4500cb585ee3b13ead62f51`; render seconds ×1000 to 6 decimals, retaining unrounded `*_s` | historical a10 diagnostic / resolvability example | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, DF, PROJ, SYN |
```

## Residual risk

A replay at later HEAD necessarily changes `producer.git_commit` ([issue_dg071_dg075_statistics.py:296](scripts/issue_dg071_dg075_statistics.py:296)-[299](scripts/issue_dg071_dg075_statistics.py:299)); reproduce the committed artifact from its recorded producer commit.