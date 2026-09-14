# Record 36 — fresh-eyes final-head review of the record-35 increment (gate row 10)

- Reviewer: Opus 5 (1M context), read-only seat.
- Target: single commit `92ada005` ("Paper-N follow-up (fresh-eyes 35 S1-S3/N1) …").
- Worktree: `/Users/edr/code/JouleWise-wt-paper-n`, branch `fix/2026-09-12-paper-n-binary64-gloss`,
  HEAD `92ada00509bfac70d9091c35c1c223cc802a7be7` (verified this session with `git rev-parse HEAD`).
- Session date: 2026-09-12 17:11 PDT. Python 3.14.7.
- Write scope honoured: this file only. No other file in the worktree was created, edited, or deleted.
  All probes ran `python3 -B` against copies of text held in the probe script; nothing was written to
  `docs/` or `tests/`.

## 0. Contamination disclosure

I am **not** a blind reviewer of the prior round. The launch brief told me, before I opened anything:

- that record 35 raised S1 (member-envelope integral sum status), S2 (deterministic bound is not
  audience vocabulary; defined at protocol ~357 after first use at ~273), S3 (no glossed entries in
  the audience class list) and N1 (`any` → `all`);
- what the commit claims to have done about each.

So my per-item verdicts are **confirmations of a stated hypothesis**, not independent discovery, and
they should be weighted as such. What is independent: I did **not** read the body of record 35
(`35-followup-final-head-fresh-eyes-opus.md`, 337 lines — I saw only its name and line count in
`git show --stat`), nor records 31/33/34 beyond their one-line commit subjects in `git log`. The two
findings below (F1, and the residue items) were reached by reading the post-commit files and running
probes, not by reading a prior reviewer's list. I also did not run the full suite (a replay runs
separately); I ran only the two modules named in the brief.

## 1. Per-item table

| Item | Claim | Verdict | Evidence |
|---|---|---|---|
| S1 | member-envelope integral sum status → `glossed-at-first-use` | **Correct** | Status now matches the header definition; disposition prose lags (see N-a) |
| S2 | "deterministic bound" glossed at its first protocol use; row → `glossed-at-first-use` | **Correct, no conflict with ~357** | Quotes below |
| S3 | audience class list reduced to bare expressions | **Correct in the prose; the new test guard does not enforce it** | F1 |
| N1 | `any` → `all` in the membership check | **Correct and load-bearing** | Counterfactual probe below |
| Draft untouched | — | **Confirmed** | `git diff --stat 92ada005^ 92ada005 -- docs/paper/draft-v2-skeleton.md` is empty; the commit touches exactly 4 files, none of them the draft |
| No other consumer pins protocol line 273 | — | **Confirmed** | greps below |
| Named tests green | — | **Confirmed**, 27 tests OK | tail pasted in §4 |

### S1 — member-envelope integral sum

The header's own definitions are the test:

> `built-before` means the body constructs the referent from physical inputs before its first named use.
> `glossed-at-first-use` means the first named use supplies a plain-word definition or an equivalent
> calculation in the same sentence or paragraph.

The prose, `docs/paper/draft-v2-skeleton.md:1370-1376` (first named use is the bolded term itself):

```
1370: between 1 and the next larger representable number. The **member-envelope
1371: integral sum** is
1372: \(\sum_{m\in\{A_1,B_1,B_2,A_2\}}|c_m|\int_{\mathrm{start}_m-b}^{\mathrm{end}_m+b}P_m(t)\,dt\),
1373: where \(c_m=(-1/2,+1/2,+1/2,-1/2)\) and \(P_m(t)\) is member \(m\)'s
1374: interval-average-power trace, held at each record's reported average across
1375: that record's time interval. This nonnegative joule sum supplies a scale
1376: large enough to cover all four member integrals before their signed contrast
```

The name arrives **first** and the defining sum is in the **same sentence**. That is precisely
`glossed-at-first-use`, and it is precisely **not** `built-before` (nothing constructs the referent
ahead of the name). The correction is right. `grep -rn "member-envelope" docs/paper/ tests/` confirms
1370 is the first occurrence in the tested reading order (the two later uses are 1378 and 1399; the
figures README hit at `docs/paper/figures/README.md:48` says "member-envelope integrals", not the
term, and the fixture hits are the frozen pre-cure snapshot).

### S2 — deterministic bound

First protocol use, `docs/paper/protocol/prospective-comparison-protocol.md:272-274`:

```
272: \(A_k=\max(0.6,0.4)=0.6\) J. This empirical allowance samples the registered
273: reference epochs; it is not a deterministic bound (a non-random maximum displacement) on arbitrary unobserved
274: excursions between them. It is a joule quantity and is distinct from the
```

Fuller definition, same file, `357-358`:

```
357: deterministic bounds. A deterministic bound is a
358: non-random maximum displacement carried in the authenticated block record.
```

**No conflict.** The gloss is a literal prefix of the later definition; ~357 adds provenance
("carried in the authenticated block record") that a reader at 273 does not need, because 273 is a
denial ("it is **not** a deterministic bound"), and the ledger row says so explicitly: "the first use
denies such a guarantee for unobserved between-reference excursions." The heading at line 238 is
`### Adding publication safeguards after the ratio`, which is the row's declared home, so
`test_first_occurrence_is_in_exact_home_section` still binds the right section.

The term does not appear earlier in the article: the draft's near-misses are
`draft-v2-skeleton.md:267` ("deterministic future-error bound") and `:1228` ("deterministic
out-of-sample guarantee"), neither of which is the ledger term.

**No consumer pins line 273.** Searches run this session:

- `grep -rn "not a deterministic bound" tests/ scripts/ joulewise/` → no matches.
- `grep -rn "empirical allowance\|arbitrary unobserved\|non-random maximum" tests/ docs/ --include="*.py" --include="*.md"`
  → the only test-side hit is `tests/test_paper_first_use_ledger.py:546`, which pins the *ledger row*
  (`"deterministic bound": ("Adding publication safeguards after the ratio", "non-random maximum displacement")`),
  not the protocol sentence; the other hits are the frozen fixture
  `tests/fixtures/paper_first_use_pre_cure.md:769,1670` (a pre-cure snapshot that must not move) and
  protocol `:358`.

### N1 — `any` → `all` (bench-verified counterfactual)

The change is not cosmetic. Counterfactual: delete one alternative ("random scatter") from the header
class list while the row `repeatability / repetition / random scatter` still claims
`audience-vocabulary`. Probe output, run this session against the live ledger and the live
`_alternatives` helper:

```
alts: ('repeatability', 'repetition', 'random scatter')
  any()-guard (old) flags row? False
  all()-guard (new) flags row? True
```

The old guard let a partly-listed grouped row through; the new one does not. Real mutant, killed.

## 2. Findings

### Tier 1 — blockers

None. Nothing in this commit makes a false statement about the prose, orphans a term, or changes a
number.

### Tier 2 — should fix before landing

**F1. The new "no glosses in the class list" guard does not fire on the exact header this commit
removed.** `tests/test_paper_first_use_ledger.py:517-522`:

```python
listed = {
    re.sub(r"\s*\(.*?\)\s*$", "", item).strip().casefold()
    for item in re.split(r",\s*(?:and\s+)?", header_match.group(1).replace("\n", " "))
}
glossed_in_class = sorted(item for item in listed if "(" in item)
self.assertEqual(glossed_in_class, [], "the audience class must list bare expressions, never glosses")
```

`listed` is built by **stripping** any trailing parenthetical, and the guard then searches the
already-stripped items. A trailing gloss — the shape that was actually present — never reaches the
check. Mutation probe, the new guard applied verbatim to the **pre-commit** header string:

```
MUTATION PROBE: new guard applied to the PRE-COMMIT header
  glossed_in_class = []
  guard fires? False
  'measurement interval' in listed: True
  'deterministic bound' in listed: True
  comma-in-gloss variant fires? True
```

The guard fires only when a gloss happens to contain a comma (which makes the split leave an unclosed
"(" in a fragment). The commit message's claim "with the test forbidding glosses" is therefore not
installed: the prose was cured by hand, and the regression that would re-introduce it is not caught.

Minimal cure (one line, at the same site, before `listed` is built):

```python
self.assertNotIn("(", header_match.group(1), "the audience class must list bare expressions, never glosses")
```

and then delete the now-dead `glossed_in_class` pair, or keep it as a belt-and-braces check. The cure
must ship with the probe above re-run against the pre-commit header text, showing it now fires —
otherwise the same weakness is being re-asserted rather than fixed (see §3).

### Tier 3 — nits, no blocking force

**N-a. The member-envelope row's disposition is still written in `built-before` vocabulary.**
`docs/paper/protocol/first-use-audit-ledger.md:142` now reads:

```
| member-envelope integral sum | A.3 Formal calibration algorithms | glossed-at-first-use | Built in Appendix A.3.10 from the four member integrals with absolute contrast weights before its two uses there. |
```

Status and evidence column disagree in wording: "Built … before its two uses there" is the sentence a
`built-before` row would carry. It is not false (the formula does precede lines 1378 and 1399), but
the audit artifact should not describe a glossed row in built-before terms. Minimal cure — replace the
disposition with: "Defined at its first named use by the displayed four-member weighted integral sum;
a nonnegative joule scale covering the member integrals before the signed contrast." Compare the
sibling `binary64` row, which gets this right ("Glossed at its first main-text use as …").

**N-b. The class list still over-declares (pre-existing, adjacent to the edited sentence).** The header
says the class "is exactly" 27 expressions, but two of them — `threshold` and `exact equality` — are
claimed by no `audience-vocabulary` row; their own row at `first-use-audit-ledger.md:135` is

```
| threshold / exact equality | Bracketed pulse-train algorithm | glossed-at-first-use | A numerical cutoff; Section 2 first uses it for the quiet-record power check. |
```

so the header asserts the professor needs no definition for two expressions the ledger says the draft
glosses. The test only checks rows ⊆ list, never list ⊆ rows, so nothing catches it. Probe output:
`listed but claimed by no audience row: ['exact equality', 'threshold']`. This predates 92ada005 and is
out of its scope, but the S3 pass rewrote exactly this sentence and could have caught it. Minimal cure
(later, not now): drop `threshold, exact equality` from the header list.

**N-c. Cosmetic.** Line 273 is now 109 characters against the file's ~76-column prose wrap, and the
gloss splits the phrase "bound … on arbitrary unobserved excursions". Nothing enforces a wrap (29
lines in the file already exceed 100, mostly tables and captions), so this is optional. If re-wrapped,
prefer em-dashes to keep the object next to its preposition: "it is not a deterministic bound — a
non-random maximum displacement — on arbitrary unobserved excursions between them."

## 3. Same-signature statement vs records 31/34/35

**Prose signature: no repeat.** The class that ran 31 → 34 → 35 was *ledger statuses drifting from
what the prose actually does*, one term per round (binary64, member-envelope integral sum,
deterministic bound). This commit closes the last of those, and I re-derived every one of the 16
`audience-vocabulary` rows plus both corrected rows against the header definitions and found no
further status/prose mismatch. That vein looks worked out.

**Mechanism signature: yes, twice in a row.** Record 34 installed the closed-class check with
`any(...)` — weaker than the property it advertised, caught in 35 as N1. Record 35 installs
`glossed_in_class` — also weaker than the property it advertises, caught here as F1. Same signature:
*the new mechanical guard is weaker than the invariant it claims to enforce, and no counterfactual
probe was run against it before landing*. Under the standing escalation trigger (two consecutive
rounds failing with the same signature), a third round of hand-written guard text without a probe is
the wrong next spend. The cure is one line, well below the bench-vs-session threshold, so the
correction itself is bench work; what should not be decided at the bench is the process rule it
suggests — "every new ledger-test guard lands with a recorded counterfactual probe showing it fires on
the defect that motivated it". That is a process rule, so it is magistrate/cold-gate territory, and I
flag it rather than propose installing it.

## 4. Command tail

```
$ cd /Users/edr/code/JouleWise-wt-paper-n && R7F_CORPUS_ROOT=/Users/edr/code/JouleWise \
  PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= \
  python3 -B -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
...........................
----------------------------------------------------------------------
Ran 27 tests in 3.849s

OK
```

The pre-existing untracked files in the worktree are six
`docs/process_traces/2026-09-12-paper-n/*-report.manifest.jsonl` manifests from earlier seats; none
were touched by me and none are mine.

## 5. Recommendation

**One more bench edit, then land.** The prose in this commit is correct on all four items and the
tests are green; the only thing not actually installed is S3's mechanical guard (F1), whose cure is a
single `assertNotIn("(", …)` line at `tests/test_paper_first_use_ledger.py:521` plus the re-run probe
pasted into the commit or record. N-a is a one-sentence ledger tidy that can ride along; N-b and N-c
are residue for a later pass. Do not open a third guard-writing round without the probe — that is the
same-signature repeat called out in §3.
