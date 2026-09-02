ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: review
EFFORT: xhigh
WRITE_SCOPE: []

# Delta re-audit 3 (execution lens) — DG-071/DG-075 producer after fix round 3 (luna 251)

Checkout: `/Users/edr/code/JouleWise-wt-paper-d2` (detached at `6846363d`,
PR #276 candidate head). Read-only: write NOTHING under the checkout.
`TMPDIR` = a subdirectory you create under
`<scratchpad>/`.
Python `/Users/edr/code/JouleWise/.venv/bin/python`. Do NOT run canonical
`python3 -m unittest discover`; you MAY run
`python -m unittest tests.test_issue_dg071_dg075_statistics` (25 tests) and
mutant/scratch copies under TMPDIR. The retained bundle (read-only) is at
`/Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv`
(sha256 `6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9`).

## What changed since delta 2 (terra 248) and the Opus 249 counter-review

`git diff 8ab397b5...6846363d -- scripts/issue_dg071_dg075_statistics.py tests/test_issue_dg071_dg075_statistics.py docs/paper/round7/`
is the delta under audit. Round 3 was shaped by a ruled consult (Sol 250,
`docs/process_traces/2026-09-02-paper-d-dg071/25-sol-250-coverage-consult.md`,
ruling in `26-coverage-consult-ruling.md`), implemented by luna 251
(`27-luna-251-fix-round-3.md`), dispositioned in
`28-fix-round-3-disposition-and-reissue.md`. Read the brief's closure shapes
as summarised in file 26 and the P1–P7 prose the magistrate dictated (file
28 §C4 names the keys; the prose is now in the artifact and docstring).

## Lens: EXECUTION. Answer each with executed evidence (commands + output tails)

D1. **Golden bundle credibility.** Rebuild the golden CSV from the test's
    literals (not by running the producer), hash it, and re-derive by hand or
    with your OWN ≤ 30-line Decimal script every value in the literal
    expected dict: sorted widths, h positions, the four quantile equations,
    the DG-075 spacings, the renderings, the gap list, max gap, nonzero
    count. Any expected value that you cannot reproduce from the literals is
    a BLOCKER (it would mean the golden was derived by running the producer).
D2. **Differential reference independence.** Is `_independent_reference`
    truly independent of the producer (no shared helper, no shared constant
    that could carry the same defect)? Which mutants would it AGREE with the
    producer on (i.e. not catch)? Name at least the classes and say whether
    each can change a published digit.
D3. **Mutant replay.** Independently apply the six mutants (half-up incl.
    the import; drop `len(starts) != 1`; IQR as rendered difference; nonzero
    count via tolerance; drop `abs`; `>` → `>=`) to copies under TMPDIR and
    report failing test names. Then add TWO mutants of your own choosing that
    change a published digit or a refusal outcome and report whether the
    suite kills them. Survivors are SHOULD-FIX at minimum.
D4. **Values of record.** Replay the producer twice into TMPDIR (patch the
    pins the way the existing tests do, or via the CLI with `--bundle`);
    confirm byte-identity to each other and to
    `docs/paper/round7/dg071-dg075-statistics.{json,md}` except
    `producer.git_commit`/`script_sha256` if your checkout differs (it
    should NOT differ — you are at 6846363d — so expect exact sha equality:
    JSON `dda89609054742b66501ef3acfe822a20e3e7da5d5882349f5d5b255ed7b0caf`,
    MD `a7bd11e5228716cd7242d3436ff2f7897e32869cf4d151220a1369141065f647`).
    Values of record must be UNCHANGED: DG-071 n 406, 116.9720 / 120.9186 /
    122.9227 / 5.9508; DG-075 n 405, 117.0321 / 120.9224 / 122.9270 / 5.8949.
D5. **Replication from the Method section alone.** Write a fresh script from
    the artifact's `## Method` text ONLY (do not read the producer while
    writing it) and reproduce all eight rendered ms values and both header
    tiling numbers. Report line count and any sentence you had to guess at
    — an ambiguity forcing a guess is a SHOULD-FIX against the prose.
D6. **Same-signature statement (mandatory, one paragraph).** Delta 2 and the
    counter-review each found surviving value-changing mutants. State
    explicitly whether THIS round still exhibits that signature (a reported
    field with no value-pinning test where a plausible wrong computation
    differs). If yes, that is an escalation, not a fix request — say so.
D7. **Prune check.** Anything in the two modules that is now write-only,
    dead, or duplicated after round 3 (e.g. the golden test binds
    `golden_sha256` then repeats the literal — nit or not?). Nits only
    unless something is unreachable.

## Report shape (protocol, mandatory)

Return the `claude-codex-report/v1` envelope FIRST (fenced ```json, nothing
before it, UNDER 8192 BYTES): `verdict` = `{"counts": {"blocker": n,
"should_fix": n, "nit": n}, "findings": [{"id": "...", "severity": "...",
"title": "..."}]}` only — all reasoning, tables, scripts and command output
in the Markdown body after the fence, sections D1–D7, then "What this audit
did NOT check".
