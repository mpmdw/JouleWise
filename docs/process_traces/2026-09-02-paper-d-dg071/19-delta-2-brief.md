ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: review
EFFORT: xhigh
WRITE_SCOPE: []

# Delta re-audit 2 (EXECUTION lens) — DG-071/DG-075 producer fix round 2 at `8096cb80` (branch `feat/2026-09-02-paper-d`)

Checkout: `/Users/edr/code/JouleWise-wt-paper-d2` (detached at `8096cb80`).
Read-only: write NOTHING under the checkout. `TMPDIR` = a subdirectory you
create under
`<scratchpad>/`.
Python `/Users/edr/code/JouleWise/.venv/bin/python`. Do NOT run canonical
`python3 -m unittest discover`; you MAY run
`python -m unittest tests.test_issue_dg071_dg075_statistics` (22 tests
expected) and any one-off computation under TMPDIR. Mutants go in a copy
under TMPDIR (`git clone --no-checkout` + checkout, or copy the two files),
never in the checkout.

The retained bundle is NOT in this worktree. Read it at
`/Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv`
(read-only, never modify; verify SHA-256
`6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9` first).

## What changed and why (the delta you are auditing)

Fix round 2 (`git diff b298ffe5..29181d6c -- scripts tests`) cured four
defects found by two refuters and ruled by the dated addendum at the END of
`docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md`
("## Addendum 2026-09-02", items 1–4 — read it; it is the contract). The
fix brief with dictated closure shapes C1–C7 is
`docs/process_traces/2026-09-02-paper-d-dg071/16-fix-round-2-brief.md`; the
implementer's report is `17-sol-247-fix-round-2.md`; the magistrate's
disposition and re-issue evidence is `18-fix-round-2-disposition-and-reissue.md`.
The re-issued artifact is `docs/paper/round7/dg071-dg075-statistics.{json,md}`
(commit `8096cb80`, producer commit `29181d6c`).

Prior rounds for context only (do not repeat their lens):
`12-sol-245-physics-refute.md`, `13-opus-246-physics-refute.md`,
`15-blind-fable-seat-ruling.md`.

## Your lens: EXECUTION — does the code do what the addendum says, under real and adversarial inputs? Fix rounds introduce defects; assume this one did until you have executed evidence otherwise.

D1. **Closure verification, each by execution not by reading.** For each of
    C1–C7 in file 16, state the executed check that proves it closed at
    `29181d6c` (command + output tail). Where the report in file 17 claims a
    number, reproduce it independently (your own Decimal computation from
    the CSV, not the producer's).
D2. **Independent replication of the four values of record per row.** From
    the CSV with your own code (Decimal, type-7), produce Q1/median/Q3/IQR
    for DG-071 (406 widths) and DG-075 (405 spacings) in exact seconds AND
    the four-decimal round-half-even ms renderings; compare byte-for-byte
    to the JSON's `*_s` and `*_ms` strings. Any digit differs → BLOCKER.
D3. **Population refusals under adversarial fixtures you build**: a record
    with a fourth rail; a record with two `cpu_power` rows and no `ane_power`;
    three rails with one differing `interval_start_s` literal; a timestamp
    group split by another group (A A A B B B A A A); a bundle whose rows
    are sorted by rail then timestamp (all cpu rows, then all gpu rows…).
    For each: which refusal fires, and does the reader-facing message name
    the actual defect? Is the ordering of checks (contiguity vs monotone vs
    rail-set) such that the FIRST refusal named is the true cause?
D4. **Tiling refusal edge cases**: gap exactly `0.000001` (must pass —
    "≤"), gap `0.0000011` (must refuse), `interval_end_s` numerically equal
    but literal-different from `timestamp_s` (e.g. trailing zero) — the
    addendum says literal equality; is that what the code does, and is it
    what the addendum MEANS (state your view; do not resolve — flag for the
    magistrate if you think literal equality is the wrong test).
D5. **Numeric edge cases in `_quantile`/`_describe`**: n = 2, n = 3, n = 4
    samples with hand-computable quartiles; a sample where h is an exact
    integer at p = 0.25 (n = 5); ties; renderings that sit exactly on a
    half (`…x5` at the fifth decimal of ms) — confirm ROUND_HALF_EVEN both
    directions with two fixtures.
D6. **Nit carried from the disposition (file 18):** two distinct
    `timestamp_s` literals that are numerically equal (`1784978889.1000000`
    then `1784978889.10000000`) pass the strict-`<` monotone check and yield
    a zero DG-075 spacing. Build the fixture, show what the producer emits,
    and rule severity (nit / should-fix). Also: does `records_do_not_tile`
    catch it? (`interval_end_s` literal must equal `timestamp_s` literal per
    record — trace it.)
D7. **Mutation adequacy beyond the two dictated mutants.** Pick THREE
    further mutants of your choice among: replace `ROUND_HALF_EVEN` with
    `ROUND_HALF_UP`; change `Decimal(len(ordered) - 1)` to
    `Decimal(len(ordered))` (type-6-ish); drop the `len(starts) != 1` clause;
    change `>` to `>=` in the tiling tolerance; skip the first record in
    widths. Run the 22 tests against each mutant copy; report which
    survive. A surviving mutant that changes a value of record is a
    SHOULD-FIX (name the missing test); one that changes only a message is
    a NIT.
D8. **Artifact ↔ producer consistency**: `script_sha256` in the JSON equals
    `shasum -a 256 scripts/issue_dg071_dg075_statistics.py` at `29181d6c`
    (note: the file at `8096cb80` is identical — confirm with `git diff
    29181d6c 8096cb80 --stat`); `git_commit` is `29181d6c…`; replay the
    producer twice into TMPDIR with `--repository-root` pointing at a
    `git clone --no-checkout` of the checkout at `29181d6c` and `cmp` against
    the committed artifact (the terra-185 recipe in file 10 V1).
D9. **Method section replication bar**: from the Markdown's `## Method`
    ALONE (do not read the code for this item), write a ≤30-line script
    that reproduces the DG-071 median and IQR strings. If you needed
    anything the section does not state, that is a SHOULD-FIX naming the
    missing sentence.

## Report shape (protocol, mandatory)

Return the `claude-codex-report/v1` envelope FIRST (fenced ```json, nothing
before it). **The JSON envelope must be under 8192 bytes**: `verdict` =
`{"counts": {"blocker": n, "should_fix": n, "nit": n}, "findings": [{"id",
"severity", "title", "file", "line"}]}` only — ALL evidence, command output,
numbers and reasoning go in the Markdown body after the fence. `severity` ∈
{blocker, should_fix, nit}. Body: a `VERDICT:` line (`CLEAN` or `BLOCKER n /
SHOULD-FIX n / NIT n`), one section per D1–D9 with executed evidence, then
"What this review did NOT check".
