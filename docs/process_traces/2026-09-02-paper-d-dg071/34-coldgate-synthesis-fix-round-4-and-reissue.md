# Cold gate on delta 3 — magistrate synthesis, fix round 4 (bench), re-issue (2026-09-02)

Inputs: packet 31; cold Fable ruling (file 32); Opus 5 contract-lens
refutation (file 33). The two seats split on one point (what B2's remedy is)
and the magistrate synthesises the split below — split verdicts are
synthesised, not majority-voted (rule 11). Neither seat's ruling is
overruled; where the synthesis goes beyond the cold seat's remedy it adopts
the refuter's, and the reason is written here so Ed sees it.

## Where the seats agree (adopted as ruled)

- **Q1.** B1 is not a recurrence of the escalated signature in rule 11's
  sense. Cold seat: the residual Sol 250 §Q2 named and file 26 accepted;
  Opus: the ruled shape's own clause 2 implemented at a size (2–8 records)
  that does not reach the cardinality the paper prints. Same conclusion,
  same cure.
- **Q2.** Closure (a), BOTH halves, with the CI-enforced widened
  differential as the load-bearing half and the bench-only retained-bundle
  pin as the corroboration (Opus's ordering; the cold seat also required
  both). No second consult (b); no limitation dodge (c).
- **Q3.** Brief 29 D4's "expect exact sha equality" was structurally
  impossible under the producer as it stood — a brief defect. The artifact's
  numbers are not defective.
- **Q4.** Terra was right to report D6 as an escalation under the definition
  it was handed; the definition's over-reach is the magistrate's. Convening
  the gate was mandatory (reinterpreting a seat's verdict), even though the
  resulting edits are bench-threshold work.
- **Q5.** B1 should-fix (lowered from blocker by both seats — the magistrate
  cannot lower a severity and did not); N1 nit.

## Where they split, and the synthesis

**B2's remedy.** The cold seat: not-a-defect in the producer; should-fix
against the prose — write the `git_commit = issuing-checkout HEAD`
convention down. Opus: the convention is "merely current", the producer's
definition of `git_commit` is the defect, and one function change (last
commit that changed the script, `git log -1 --format=%H -- scripts/…`)
makes byte-exact replay hold permanently at every commit that leaves the
script unchanged — including the commit that contains the artifact, which is
exactly the commit a reader checks out.

Synthesis: **adopt Opus's remedy.** The cold seat's prose fix documents a
property the artifact lacks; Opus's fix gives the artifact the property the
brief, the reader and the previous three reviewers all assumed it had. The
cost is one function, one gloss, and a re-issue (the producer's
`script_sha256` changes, so the artifact must be re-issued regardless of
whether `git_commit`'s recorded value would have changed). The cold seat's
"write it down" is also taken: the definition is now glossed at first use
in the Markdown header bullet, in a `Provenance.` paragraph in the Method
section, in the JSON `method.provenance` key, and in the docstring.

Opus's M1 (new, should-fix) is adopted with it:
`test_two_checkout_roots_produce_byte_identical_json` asserted a property the
producer did not have and passed only because both scratch repositories had
identical HEAD hashes. It is re-scoped to the property that now holds and
renamed `test_producer_commit_is_the_scripts_last_commit_not_head`: two
scratch repositories with an identical script commit and DIFFERENT heads
produce byte-identical JSON whose `git_commit` equals the script commit and
differs from each HEAD. The `git rev-parse HEAD` producer fails it (replayed
below).

**Re-audit shape.** Cold seat: one bounded delta re-audit by a model that
has not audited round 3 (Sol qualifies), scope = the test edits plus a mutant
replay. Opus: no fourth delta re-audit; bench mutation replay suffices under
the bench-vs-session threshold. Synthesis: the producer changed (the
provenance function), which makes this a post-review CODE commit;
operation-loop §5 requires a fresh pass over it before merge irrespective of
who typed it. That fresh pass IS the cold seat's bounded re-audit — Sol high,
`--write-scope '[]'`, scope limited to the fix-round-4 diff and the mutant
replay — and is not a fourth gauntlet. Opus's objection was to a fourth
delta seat as *adjudication*; the §5 pass is *gate ceremony* the PR needs
anyway.

## Dated addenda (corrections to custodied files; the files are not rewritten)

- **Addendum to packet 31, F3 (2026-09-02).** F3 says the magistrate "chose
  that range" for the differential's 2–8 records. The range is Sol 250 §Q1
  (file 25 line 175: "2–8-record valid bundles"), adopted by file 26 clause
  2; the magistrate's fix-round-3 brief C3 dictated "12 bundles of 2–8"
  *adopting* the consult's sizing. Opus's attribution is right; the
  magistrate is responsible for adopting the size without asking whether
  it reached the paper's cardinality, not for originating it.
- **Addendum to packet 31, Q1 premise and Q3 binary (2026-09-02).** Q1
  carried "no finite hermetic fixture set kills `values[:N]` for every N"
  as if it bore on closure; it does not — every value-changing cap has
  N < 406, and one bundle above 406 records kills that subclass in CI
  (Opus §1, replayed below). Q3 offered producer-defect vs brief-defect
  and excluded the answer taken above. Both are packet-drafting defects
  by the magistrate; both seats read past them.
- **Addendum to packet 31, evidence list (2026-09-02).** `_describe`'s sort
  is line 182 (179 is the `def`) at `6846363d`.
- **Addendum to brief 29, D4 (2026-09-02).** "Expect exact sha equality"
  at `6846363d` was impossible: the committed artifact carried the parent
  commit `6d30c105` by the then-current `rev-parse HEAD` definition. Under
  the fix-round-4 definition the expectation is now TRUE at every commit
  that leaves the script unchanged, including the commit containing the
  artifact — demonstrated under Executed evidence after the artifact
  commit.
- **Addendum to file 28, C7 (2026-09-02).** The "differ from the bench pair
  in exactly the `producer.git_commit` field" observation was a symptom of
  the same definition; it no longer arises for a committed script.

## Fix round 4 dispositions (bench, magistrate; commit `70147173`)

| Item | Edit | Status |
| --- | --- | --- |
| B1 primary (CI) | `test_differential_against_independent_reference`: bundle 0 draws 500 records (> 406), others 2–8; comment names the counterfactual | done |
| B1 secondary (bench) | `test_retained_bundle_values_of_record`: `skipTest` when `PINNED_BUNDLE_PATH` is absent (precedent `tests/test_env_locks.py:57`); asserts input sha, n 406/405, the eight rendered ms values, the eight exact s values, max tiling gap `0.0000004`, 100 nonzero boundaries, and the two stdout lines | done; runs at the bench, skips in CI |
| B2 (Opus remedy) | `_git_commit` → `git log -1 --format=%H -- scripts/issue_dg071_dg075_statistics.py`; empty output (uncommitted script) refuses `git_commit_invalid`; new refusal test `test_uncommitted_script_refusal_reaches_main` | done |
| B2 gloss (cold-seat remedy) | `PROVENANCE_DISCLOSURE` constant → JSON `method.provenance`, Markdown `Provenance.` paragraph, header bullet renamed "Producer commit (last commit that changed the producer; defined under Method)", docstring's "for a fixed checkout and input" replaced by the definition; golden expected dict carries the literal; method-disclosure test asserts all three surfaces | done |
| M1 | two-checkout test re-scoped and renamed as above | done |
| N1 | golden assertion uses the bound `golden_sha256` | done |
| Refusal count | unchanged at 16 codes; `git_commit_invalid` gains a second cause (empty `git log`) | — |

Not taken: a shallow-clone caveat. `git log -1 -- <path>` in a depth-1
clone returns the shallow boundary commit, not the true last-touch commit;
CI uses `fetch-depth: 0`, and the bench is a full clone, so the value of
record is unaffected; recorded here so a reader replaying from a shallow
clone knows why the commit line can differ while `script_sha256` matches.

## Executed evidence (this session; `TMPDIR=<scratchpad>/tmpbench4`)

Focused module at `70147173` (worktree `/Users/edr/code/JouleWise-wt-paper-d`):

```
$ python3 -m unittest tests.test_issue_dg071_dg075_statistics
Ran 27 tests in 0.424s
OK
$ python3 -m unittest -v … test_retained_bundle_values_of_record … test_producer_commit_is_the_scripts_last_commit_not_head
Pin the numbers the paper prints, on the retained bundle itself. ... ok
Two checkouts at DIFFERENT heads, same script commit: identical bytes. ... ok
```

Skip branch (bench check, `PINNED_BUNDLE_PATH` patched to a non-existent path):

```
test_retained_bundle_values_of_record ... skipped 'runs_window corpus absent (clean checkout without bundles)'
```

Mutant replay. Each `mut4-<name>` is a copy of the two modules under
`<scratchpad>` with one `git init` commit, a single-site replacement
(`assert count == 1`) committed on top, then the focused module:

```
base    : Ran 27 tests  OK
cap8    : FAILED (failures=2)  test_differential_against_independent_reference, test_retained_bundle_values_of_record      [sorted(values[:8])]
cap400  : FAILED (failures=2)  test_differential_against_independent_reference, test_retained_bundle_values_of_record      [sorted(values[:400])]
cap406  : FAILED (failures=1)  test_differential_against_independent_reference                                             [sorted(values[:406]) — a no-op on the retained bundle, so only the CI half can see it]
revparse: FAILED (failures=1)  test_producer_commit_is_the_scripts_last_commit_not_head                                   [_git_commit → git rev-parse HEAD]
```

Re-issue at `70147173`, twice, into `<scratchpad>/reissue-e` and `reissue-f`:

```
210bc591152d563d8e86fac1ffbf0534ac15c043713815638317fbedee6610f3  reissue-e/dg071-dg075-statistics.json
85410cb4d78ca95428f8c774387f43b22a1a327a17501bd6f96b5cff193e28c2  reissue-e/dg071-dg075-statistics.md
210bc591152d563d8e86fac1ffbf0534ac15c043713815638317fbedee6610f3  reissue-f/dg071-dg075-statistics.json
85410cb4d78ca95428f8c774387f43b22a1a327a17501bd6f96b5cff193e28c2  reissue-f/dg071-dg075-statistics.md
DG-071 median_ms=120.9186 iqr_ms=5.9508
DG-075 median_ms=120.9224 iqr_ms=5.8949
$ git diff --stat   (after copying into docs/paper/round7/)
 docs/paper/round7/dg071-dg075-statistics.json | 5 +++--
 docs/paper/round7/dg071-dg075-statistics.md   | 6 ++++--
```

The diff against `6846363d`'s artifact is exactly `producer.script_sha256`,
`producer.git_commit` (`6d30c105` → `70147173`), the new `method.provenance`
key, the renamed header bullet and the new Method paragraph. Values of record
UNCHANGED: DG-071 n 406, 116.9720 / 120.9186 / 122.9227 / 5.9508; DG-075
n 405, 117.0321 / 120.9224 / 122.9270 / 5.8949.

Replay at the commit that CONTAINS the artifact (the property fix round 4
makes true; appended after that commit exists):

```
$ git rev-parse --short HEAD
ebd947a0                      (the commit that adds docs/paper/round7/dg071-dg075-statistics.{json,md})
$ python3 scripts/issue_dg071_dg075_statistics.py --repository-root . --out <scratchpad>/reissue-g/dg071-dg075-statistics.json
$ cmp reissue-g/dg071-dg075-statistics.json docs/paper/round7/dg071-dg075-statistics.json && cmp reissue-g/…md docs/paper/round7/…md && echo BYTE-IDENTICAL
BYTE-IDENTICAL-AT-ebd947a0
$ grep -o '"git_commit": "[0-9a-f]*"' docs/paper/round7/dg071-dg075-statistics.json
"git_commit": "701471732488b56952beb47393e08c68285a5ea2"
```
