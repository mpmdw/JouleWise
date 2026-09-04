ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: review
WRITE_SCOPE: []

# Refuter round on paper seat D (commits 3fca7d6b + 1baf8c4c): `scripts/issue_dg071_dg075_statistics.py`, `tests/test_issue_dg071_dg075_statistics.py`, issued artifact `docs/paper/round7/dg071-dg075-statistics.{json,md}`

Checkout: `/Users/edr/code/JouleWise-wt-paper-d` (branch head 1baf8c4c).
Read-only; write nothing under the checkout; `TMPDIR` = a subdirectory you
create under
`<scratchpad>/`.
Python `/Users/edr/code/JouleWise/.venv/bin/python`. You MAY run the named
test module (`python -m unittest tests.test_issue_dg071_dg075_statistics`)
and the producer with `--out` under your TMPDIR; never canonical discover;
everything under `runs*/` is retained evidence, READ-ONLY. No git writes.
The diff: `git diff a63d45bd 1baf8c4c`. The seat's brief with the magistrate
ruling R-167-1 is `scratchpad/run-paper-d2.md` (read it in full).

## Your lens: CONTRACT — ratification text vs implementation vs artifact

1. Specification chain: quote the defining sentences of
   `docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md`
   for DG-071 and DG-075 and the registry rows
   `docs/paper/results-fill-registry.md:640-648`; then verify the code
   implements EXACTLY those (which records are included; how duplicate
   timestamps are treated — the artifact says 1218 records, 406 distinct
   timestamps, 812 duplicates dropped, 405 differences: is dropping
   duplicates what the ratification/ruling says, or a seat choice? if the
   ratification says "consecutive unique timestamp differences" cite it);
   R-167-1's estimator (`statistics.median`; `_quantile` as in
   `scripts/paper_excursion_decomposition.py:246-259`; IQR=Q3−Q1;
   unrounded `*_s` of record + ms at 6 decimals). Cite code lines.
2. Recompute independently: with your own ~15-line snippet over the pinned
   `runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv`
   (sha256 must equal
   `6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9`),
   reproduce DG-071 median 0.12091851234436035 s / IQR
   0.005975008010864258 s and DG-075 median 0.12092232704162598 s / IQR
   0.005894899368286133 s. Report agree/disagree to the last digit.
3. Artifact custody: the JSON records the bundle path — is it ABSOLUTE
   (`/Users/edr/...`) where the registry's supplier convention is
   repo-relative (compare `docs/paper/round7/excursion-decomposition.json`
   and `anchor-correction-quantified.json`: what do THEY record)? Does the
   JSON's `script_sha256` equal sha256 of the committed script at 1baf8c4c
   (the artifact was produced at 3fca7d6b — did the script change between
   3fca7d6b and 1baf8c4c? `git diff 3fca7d6b 1baf8c4c -- scripts/`)? Does
   `git_commit` in the JSON match? Is the MD a faithful rendering of the
   JSON (every number identical)? Would `scripts/check_paper_replay_fence.py`'s
   conventions (self-pinning, refusal codes) be satisfied by this artifact,
   and what would a sibling fence (like the round-7 R7F planned for DX rows)
   need to check for this pair?
4. Refusals: does each guarded precondition (wrong sha, missing field,
   non-monotone timestamps, schema mismatch) actually refuse with a named
   reason and non-zero exit, and does a test bite each (name the assertion
   line)? Any guard with no biting test is a SHOULD-FIX.
5. Registry issuance text: draft the exact replacement text for the two
   registry rows (supplier = `docs/paper/round7/dg071-dg075-statistics.json`
   field path, sha256
   `5cc81fd74b39383d14aa5cc2df6ba13dc1fdb309ddecd0ff6d4ec0ab333e8c7a`,
   rendering rule, freeze status, sources) in the registry's own column
   format so the magistrate can land it verbatim on the dx-registry branch.

Severity: BLOCKER = value not reproducible / implementation contradicts the
ratification; SHOULD-FIX = custody gap (absolute path, stale script sha),
untested guard; NIT = wording. Report: envelope first
(`claude-codex-report/v1`, genre `review`), then under 90 lines.
