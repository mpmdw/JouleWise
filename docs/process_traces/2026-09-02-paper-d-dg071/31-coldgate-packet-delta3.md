# Cold-gate packet — delta re-audit 3 blockers on the DG-071/DG-075 producer (2026-09-02)

Trigger (rule 11, mandatory, not discretionary): terra 252's delta re-audit
3 (file 30) reports BLOCKER 2 and states under D6 that the same-signature
defect class recurs. Acting on either blocker would be a further fix round
on a defect class that has already had two rounds and one consult, and the
magistrate's own reading of B1 (below) would be a reinterpretation of a
seat's verdict. Both are cold-gate triggers. The magistrate is a party here
(it wrote the brief whose parameters both blockers turn on) and does not
rule.

Seats: one COLD Fable instance (fresh session, this packet and the primary
evidence only, no loop context) and one Opus 5 contract-lens refuter, run
in parallel, read-only. The magistrate may overrule the cold ruling only
with written dissent that Ed sees.

## Primary evidence (read these; nothing else is needed)

All paths are in the checkout `/Users/edr/code/JouleWise-wt-paper-d` at
`6846363d` (the PR #276 candidate head). Read-only. Trace directory
`docs/process_traces/2026-09-02-paper-d-dg071/`:

- `30-terra-252-delta-3.md` — the report under adjudication (B1, B2, N1, D1–D7).
- `29-delta-3-brief.md` — the brief terra answered (D4's stated sha expectation; D6's signature definition).
- `25-sol-250-coverage-consult.md` §Q1, §Q2 (the not-killed table) and §Q4.
- `26-coverage-consult-ruling.md` — what the magistrate adopted from the consult.
- `23-opus-249-disposition.md` §"Same-signature statement" — the prior escalation reading.
- `28-fix-round-3-disposition-and-reissue.md` — the round-3 disposition and the bench mutant replay.
- `18-fix-round-2-disposition-and-reissue.md` — the earlier re-issue, for the provenance convention (re-issue at `29181d6c`, committed as `8096cb80`).
- `scripts/issue_dg071_dg075_statistics.py` — `_describe` (line 179: `ordered = sorted(values)`), `build_payload`, the `producer` provenance block.
- `tests/test_issue_dg071_dg075_statistics.py` — `test_golden_bundle_pins_every_reported_field`, `test_differential_against_independent_reference` (line 478: `rng.randint(2, 8)` records per bundle), `_independent_reference`.
- `docs/paper/round7/dg071-dg075-statistics.json` — the committed artifact (`producer.git_commit` = `6d30c105…`).
- Precedent for corpus-absent skipping: `/Users/edr/code/JouleWise/tests/test_env_locks.py` line 57 (`self.skipTest("runs/ corpus absent …")`).

Facts the seats may take as given (each is checkable from the files above):

F1. The retained bundle `runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv`
    is gitignored (`/runs_window_*/` in `.gitignore`); CI checkouts and
    linked worktrees do not have it. It exists at
    `/Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv`
    (read-only, sha256 `6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9`),
    406 sampler records.
F2. The test module is hermetic: every test writes its own fixture under
    `TMPDIR` and patches `PINNED_BUNDLE_PATH`/`PINNED_BUNDLE_SHA256`. No test
    runs the producer on the retained bundle. The largest fixture is the
    eight-record golden; the differential draws 2–8 records per bundle.
F3. The brief for fix round 3 (summarised in file 26; C3) dictated the
    differential's "2–8 records". The magistrate chose that range.
F4. The artifact's `producer.git_commit` is the HEAD at issue time. An
    artifact re-issued at commit X and committed in commit Y (Y = X + the
    artifact) necessarily carries X; replaying at Y yields Y. File 18
    recorded this for `29181d6c`/`8096cb80` without objection from terra 248
    or Opus 249. Brief 29 D4 nevertheless told terra to "expect exact sha
    equality" at `6846363d`.

## Questions for the cold seat (rule on each; plain words; cite the file)

Q1. **B1.** Is terra's `sorted(values[:400])` survivor a RECURRENCE of the
    escalated signature (a reported field with no value-pinning test on an
    input where the wrong computation differs), or the residual class Sol
    250 §Q2 named and the ruling (file 26) accepted ("a computation mutant
    that happens to agree on all current fixed cases … including
    potentially on the retained bundle")? Note that no finite hermetic
    fixture set kills `values[:N]` for every N; only a test at the retained
    bundle's own cardinality (or above) discriminates the class at the
    cardinality that matters for the paper.
Q2. **Closure of B1, if any.** Choose ONE and say why the others lose:
    (a) add a value-of-record pin test on the retained bundle (n and the
        eight rendered ms values as literals; `skipTest` when the corpus is
        absent, as `test_env_locks.py` does — so it runs at the bench, not
        in CI) AND widen the differential to include at least one bundle
        above 406 records; a bench fix round, then a delta re-audit by a
        model that has not yet audited this producer's round 3;
    (b) declare the coverage shape itself inadequate and convene another
        consult (this would be the second consult on the same class);
    (c) accept B1 as a registered limitation (the class is named in file
        25 §Q2 and the values of record have been replicated independently
        four times: terra 248, Opus 249, luna 251, terra 252) and merge with
        no further test;
    (d) something else, specified.
    If (a): does a bench-only (CI-skipped) pin satisfy the signature's
    "value-pinning test", given the paper's values of record are exactly
    the numbers it pins? Or must the fix ALSO land a synthetic bundle at
    ≥ 406 records so CI enforces something at that cardinality?
Q3. **B2.** Is the failed D4 expectation a defect in the producer/artifact
    (the artifact should be reproducible byte-for-byte at the PR head), or
    a defect in the brief (the magistrate asked for something structurally
    impossible under the F4 convention)? If the latter, say whether the
    convention "`producer.git_commit` = the commit whose producer issued
    the artifact" needs to be written into the artifact's Method or
    provenance text so a reader is not misled the way the brief was.
Q4. **Process.** Was terra right to call D6 an escalation? Was the
    magistrate right to bring this here rather than adding the test at the
    bench under the bench-vs-session threshold? One paragraph each.
Q5. **Severity.** State each blocker's severity as YOU read it (blocker /
    should-fix / nit / not-a-defect) with one sentence. The magistrate
    cannot lower a severity; you can.

## The magistrate's position (a party's statement, not evidence)

B1 is the residual Sol 250 named, made visible because the magistrate set
the differential's range at 2–8; the class cannot be closed hermetically,
but the value-of-record pin (Q2a) is the direct test of exactly the numbers
the paper prints and costs ten literals. B2 is a brief error; the F4
convention is correct and should be stated in one sentence in the
provenance text. The magistrate would take (a) with the CI-enforced synthetic
bundle as well, then a fourth delta re-audit by Sol (not yet used on round
3) — and records that it is aware this is what a continuation-prone agent
would say.

## Report shape

Cold seat: `## Ruling` with Q1–Q5 answered in order, each with the citation;
`## Executed evidence` only for anything you ran (commands + output tails;
you may run `python3 -m unittest tests.test_issue_dg071_dg075_statistics`
and mutant copies under a scratch directory; never edit the checkout).
Opus refuter: `## Refutation` — attack the cold seat's likely reasoning
AND the magistrate's position with the contract lens (what do files 25/26
and rule 11 actually commit the process to?), then your own Q1–Q5 answers,
then `## What I did not check`.
