ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: []
GENRE: review
EFFORT: xhigh
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# DELTA RE-AUDIT — round-7 artifact fence fix round 2b (detached worktree @ 8efbb200)

READ-ONLY refuter. DETACHED WORKTREE `/Users/edr/code/JouleWise-wt-dx2` @
8efbb200 (the fix-round-2b landing, committed). Write NOTHING inside the
worktree except transient mutation probes that you restore; scratch files go
to `$TMPDIR` only; never `git checkout`, `stash`, `commit`, or canonical
`unittest discover`. `runs*/` are immutable corpora; `docs/paper/draft-v1.md`
is byte-frozen; never open either for writing. Do NOT run the full replay
(`python3 scripts/check_paper_round7_artifacts.py` without `--literals-only`)
— the magistrate runs it at the bench. Tests run as
`python3 -m unittest tests.test_paper_round7_artifacts.RegistryAndDigestTests tests.test_paper_round7_artifacts.RefusalTests tests.test_paper_round7_artifacts.TypedArtifactCliTests tests.test_paper_round7_artifacts.InvocationTests`
(43 tests; the one omitted class is the corpus replay) and the fence as
`python3 scripts/check_paper_round7_artifacts.py --literals-only; echo EXIT=$?`.
Mutation probes: `cp <file> $TMPDIR/orig-<name>`, edit, test, restore, and
confirm `git status --porcelain` is EMPTY before writing the report; a
non-empty porcelain at report time is a protocol failure — say so and stop.

AUTHORITY (read in this order; these live on main, NOT on this checkout —
absolute paths, read-only):
1. `/Users/edr/code/JouleWise/docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md`
   §A1 (dictated code shapes A1.1 loader, A1.2 comparison, A1.3 resolver),
   §A2 (placement census), the P1–P4 CLI regressions, and the dated addendum
   at the end of the file (site correction: the SVG attribute reads stay
   `float()`; the artifact read at the per-pulse site is the cure).
2. `/Users/edr/code/JouleWise/docs/process_traces/2026-09-02-coldgate-dx-t26a/seat-cold-fable-220.md`
   §A1 — the reference `_typed` resolver and regression table.
3. `/Users/edr/code/JouleWise/docs/process_traces/2026-09-02-coldgate-dx-t26a/207-opus-counter-review.md`.
The fix brief (F-1…F-8, mutations M1–M7, acceptance greps) is at
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/fix-dx-2b.md`
and Sol 225's landing report with its clause map at
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/out/225-sol-dx-fix2b.md`
(both read-only). Per the S2 rule: enumerate the ruling's A1/A2 clauses
YOURSELF from the ruling BEFORE opening Sol's clause map; then reconcile.

The delta is `git diff 781c8d78 8efbb200` (3 files, +464/−73).

## Lenses (all three; report each separately)

A. CONTRACT — for each ruling clause (A1.1, A1.2, A1.3 incl. the full
   regression table, addendum geometry rule, P1, P2, P3, P4, A2 census
   incl. the 16-id set from the parsed registry, the `PLACED` line order,
   the two fill-checklist sentences, F-7 `--outt`): production `file:line`
   at 8efbb200, biting test `file:line`, verdict INSTALLED / PARTIAL /
   MISSING with the counterfactual input. Check the resolver against the
   seat-220 reference line by line: `number` must accept `int` (not bool)
   and `Decimal` and return `Decimal`; `int` must reject `Decimal("15.0")`;
   `bool` must be exactly `bool`. Check that the ruling's message shape
   `f"{field}: expected {kind}, found {type(value).__name__}: {value!r}"`
   is byte-exact.

B. EXECUTION — run at the bench (paste command + output + exit line):
   1. the four-class test command and the literals-only fence (expect
      `R7F PLACED 0/16` then `R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0`, EXIT=0);
   2. `grep -n 'Decimal(str(' scripts/check_paper_round7_artifacts.py` (must
      be empty) and `grep -n 'float(' scripts/check_paper_round7_artifacts.py`
      (only `shape.attrib` lines, `float("nan")`, and the body of `_geometry`);
   3. the scalar-read census
      `grep -n 'artifacts\[\|pulse\[\|resolve_field(' scripts/check_paper_round7_artifacts.py`
      — classify EVERY hit as (i) inside `_typed`-guarded code, (ii) dict/list
      navigation feeding a `_typed` call, or (iii) an UNGUARDED scalar read
      (a finding of the ruled class);
   4. mutations M1–M7 from the fix brief, re-run yourself (KILLED by
      <test name> / SURVIVED), plus THREE of your own targeting the new
      code: (a) `_typed` `number` branch accepting `bool`; (b) `check_gates`
      REFUSED branch swallowed (return match=True on ValueError); (c) the
      `PLACED` line printed AFTER the `COMPARED` tail;
   5. Sol's F-2 claim "no legitimate call-site normalization was required"
      — verify by listing every `_comparison(` call site and the types of
      its two arguments; any site where a `Path` is compared to a `str`, an
      `int` to a `Decimal`, or a `Decimal` to a `str` under the new
      type-strict rule is a finding (it would flip a passing comparison to
      MISMATCH on the full replay, which the magistrate is running now).

C. SAME-SIGNATURE — the ruling classified round 2b as the rule-11 SECOND
   round on the family "scalar reads coerce instead of refuse". State
   whether a THIRD round on that family is now structurally impossible
   (every artifact-scalar read goes through `_typed`), or name the read
   that still coerces. If any, that is a BLOCKER and triggers the standing
   escalation (consult, not round 3) — say so in those words.

## Report

Severity-tiered findings (BLOCKER / SHOULD-FIX / NIT), each with file:line,
counterfactual input, and exact observed output. Then `## Executed
evidence` with every command and its exit line. Then a one-line VERDICT:
`CLEAN` / `SHOULD-FIX n` / `BLOCKER n`. End with `git status --porcelain`
output (must be empty).
