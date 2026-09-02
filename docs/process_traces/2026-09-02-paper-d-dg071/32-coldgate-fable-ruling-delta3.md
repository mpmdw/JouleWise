# Cold-gate ruling — cold Fable seat on the delta-3 blockers (2026-09-02)

Seat: fresh Fable instance (`Agent`, general-purpose, no loop context), read-only
on `/Users/edr/code/JouleWise-wt-paper-d2` detached at `5f105823` (code and
artifact identical to `6846363d`), packet = file 31. Scratch under
`<scratchpad>/coldgate-delta3-fable/`. The text below is the seat's report
verbatim (only the scratchpad path is redacted).

---

## Ruling

**Q1 — B1 is the residual class Sol 250 §Q2 named, not a recurrence of the escalated signature.**

The escalated signature (file 23 lines 15–17; brief 29 D6) is "a reported field with no value-pinning test where a plausible wrong computation differs." Read literally, `sorted(values[:400])` fits those words, and terra 252 (file 30 §D6) applied them honestly. But the two prior rounds that produced the signature were about *fields and arithmetic rules with no pinning example at all*: IQR-from-rendered-quartiles, tolerance-counted boundaries, half-up ties, the dropped rail guard (file 23 lines 11–15; file 25 §Q4). Every one of those is now killed by the golden or the differential — I replayed the class boundary myself: `values[:7]` dies (golden + differential), `values[:8]` and above survive. What survives is exactly the row Sol 250 §Q2 line 221 wrote down in advance: "A computation mutant that happens to agree on all current fixed cases — Yes, including potentially on the retained bundle." File 26 lines 18–21 adopted that residual by name and accepted the 2–8 differential as its only secondary. A residual that the ruling enumerated and accepted is not a *recurrence*; a recurrence is the same defect class appearing where the process believed it had closed it. Nobody believed a hermetic 8-record fixture closed input-size-conditional behaviour at 406 — file 25 says so, file 26 adopts it, and the packet's own note that no finite fixture set kills `[:N]` for every N is correct (my `[:406]` mutant survives everything, including a retained-bundle pin, because at n = 406 it is a no-op).

The honest defect here is narrower than terra's framing: the consult-ruled coverage shape has *no test at the cardinality the paper prints*, so the differential's "input-conditional coincidence" safeguard (file 25 line 175) does not reach the input that matters. That is a gap in the ruled shape, not a third failure of the same kind that produced rounds 1–2.

**Q2 — Closure: (a), with a specific shape. Both halves, and both are one-line-scale.**

Take (a). The value-of-record pin on the retained bundle, `skipTest` when the corpus is absent exactly as `/Users/edr/code/JouleWise/tests/test_env_locks.py` line 57 does, PLUS widening the differential to include one bundle above 406 records. I bench-built both in scratch (not the checkout) and measured them:

- Retained-bundle pin (ten literals + three header fields): kills `[:8]`, `[:400]`, `[:405]`; passes clean; skips cleanly with the corpus absent; `[:406]` survives *and must* — it does not change any paper number.
- Differential widened by changing `tests/test_issue_dg071_dg075_statistics.py` line 478 `rng.randint(2, 8)` to draw one 500-record bundle: kills `[:8]`, `[:400]`, `[:406]` through the already-independent `_independent_reference`; the unmutated copy stays 25/25 OK. Cost: one line, no new oracle, no new fixture literals, CI-enforced.

Why the others lose. (b) loses because the consult already named this residual; a second consult would ask a question whose answer is on file (file 25 line 221) and would be the ceremonial spend rule 11 warns against. (c) loses because the paper's eight numbers are the whole point of this producer and a ten-literal test that asserts them directly is cheaper than the paragraph registering the limitation; four independent replications (files 18, 28, 30 §D4/§D5, plus my fifth via the test's own oracle) show the numbers are right *today* — a pin is what keeps them right after the next edit. (d) — nothing better; the magistrate's "CI-enforced synthetic bundle" is the widened differential above, not a third fixture.

On the sub-question: a bench-only (CI-skipped) pin **does** satisfy the signature's "value-pinning test" for the paper's values of record — it pins precisely the numbers printed, on precisely the input they come from, and it runs wherever the artifact can be issued at all (the producer refuses without the retained bundle, so CI could never issue the artifact anyway). But the fix must ALSO widen the differential, because a CI-skipped test is invisible to the PR gate and the widened differential costs one line; landing only the skip-pin would leave CI blind to the class. Then one delta re-audit by a model that has not audited round 3 (Sol qualifies; luna implemented it, terra audited it). The magistrate should NOT run a fourth full gauntlet — the re-audit scope is the two test edits and a mutant replay of `[:8]`/`[:400]`/`[:406]`, nothing wider.

**Q3 — B2 is a brief defect, not a producer/artifact defect. The convention should be stated in the provenance text.**

The artifact carries `producer.git_commit = 6d30c105` (`docs/paper/round7/dg071-dg075-statistics.json` line 27). `git show --stat 6d30c105` is the code landing (script + tests only); `6846363d` is the commit that adds the artifact and custody files. An artifact that contains its own committing hash is impossible unless the hash is forged; the producer reads `git rev-parse HEAD` (script lines 377–395), so the artifact necessarily carries the parent. I replayed at `6d30c105` in a scratch worktree: **byte-identical** to both committed files (`dda89609…` / `a7bd11e5…`). Replay at the packet HEAD differs in exactly one line per file, the commit hash — which is what file 18 lines 90–101 recorded for `29181d6c`/`8096cb80` without objection. The artifact is byte-reproducible at the commit it names; brief 29 D4 lines 55–58 asked for equality at a commit it cannot name. Terra's report is accurate about what it observed; the expectation was wrong.

Yes, write the convention down. The artifact's provenance currently says only "- Git commit: `…`" (`render_markdown`, script line 588) and the JSON has no gloss. One sentence in the Markdown header or Method, and one `method`/`producer` key or docstring line, saying: "`git_commit` is the checkout HEAD at issue time; the commit that adds this artifact is therefore its child, and a byte-identical replay is obtained by checking out `git_commit`, not the artifact's own commit." A reader — and the next brief-writer — was misled exactly this way; the fix is prose, not code, and can ride with the Q2 test edits so the artifact is re-issued once.

**Q4 — Process.**

Terra was right to write the D6 paragraph as an escalation. Brief 29 D6 lines 66–70 handed terra a literal definition and told it "if yes, that is an escalation, not a fix request — say so." Terra found an input where the words of the definition held, said so, and flagged it `lead_ruling`/`blocking` (file 30 F1) rather than quietly proposing a fixture. That is the seat behaving as briefed; an auditor who softens a briefed trigger because it suspects the trigger over-reaches is doing the magistrate's job. The over-reach is in the definition the brief supplied, which does not distinguish "an uncovered field" from "an enumerated, accepted residual" — a distinction the cold seat exists to draw and has drawn above.

The magistrate was right to bring it here rather than pin at the bench, but only narrowly. The bench-vs-session threshold (rule 9) would have covered the *edit* — ten literals plus a one-line range change is smaller than any brief. What it does not cover is the *reinterpretation*: to pin at the bench the magistrate would first have had to rule that terra's "recurrence" was really a residual, which is reading a seat's verdict down, and rule 11 names that as a mandatory trigger regardless of how small the ensuing edit is. The magistrate's own packet says it knows a continuation-prone agent would say "just add the test"; the correct response to that awareness is what happened. With this ruling in hand, the edits themselves are bench-threshold work and need no further brief to *make*, only the bounded re-audit to *check*.

**Q5 — Severities.**

- **EXEC-R3-B1: should-fix** (lowered from blocker). The retained-bundle values are correct and independently replicated five times; the surviving mutant is the residual the consult ruling accepted by name; the gap is that no test reaches the paper's cardinality, and it is closed by ten literals plus one line, both bench-verified above. It is not a merge-blocker on soundness; it is a required fix before the PR merges because it is nearly free and closes a gap in the ruled shape.
- **EXEC-R3-B2: not-a-defect** in the producer or artifact; **should-fix** against the provenance prose (one sentence stating the `git_commit` = issuing-checkout-HEAD convention) and a correction to brief 29 D4 by dated addendum so the trace does not carry a false expectation.
- **EXEC-R3-N1: nit**, unchanged (`tests/test_issue_dg071_dg075_statistics.py` lines 255–261 bind `golden_sha256` and then repeat the literal); fix in passing or ignore.
- Packet housekeeping (not a finding): the packet cites `_describe`'s sort at line 179; it is line 182 (179 is the `def`).

## Executed evidence

All scratch under `<scratchpad>/coldgate-delta3-fable/`; nothing under `/Users/edr/code` was edited (`git status --short | wc -l` → 0 at the end). One caveat: the replay at `6d30c105` used `git worktree add --detach` into scratch, which writes git metadata under the repo's `.git/worktrees`; it was removed immediately (`git worktree list | grep -c coldgate` → 0).

Checkout state:
```
$ git rev-parse HEAD → 5f105823158b33a92d67a21026acbc7fb01a6f93
$ git diff --stat 6846363d HEAD → only 29-delta-3-brief.md, 30-terra-252-delta-3.md, 31-coldgate-packet-delta3.md, MAGISTRATE-NOTES.md (498 insertions)
$ git show --stat 6d30c105 → scripts/issue_dg071_dg075_statistics.py | tests/test_issue_dg071_dg075_statistics.py only
$ git show --stat 6846363d → docs/paper/round7/dg071-dg075-statistics.{json,md} + files 27, 28
```

Baseline and `values[:N]` mutants (single-site replacement at script line 182, `assert count == 1`, each in its own `git init` copy):
```
== baseline ==                Ran 25 tests in 0.293s  OK
== mutant values[:7] ==       FAILED (failures=2)  differential + golden
== mutant values[:8] ==       Ran 25 tests  OK
== mutant values[:9] ==       Ran 25 tests  OK
== mutant values[:400] ==     Ran 25 tests  OK
== mutant values[:405] ==     Ran 25 tests  OK
== mutant values[:406] ==     Ran 25 tests  OK
```

Retained bundle (sha256 `6945160964bc…3e06e9` confirmed) through the mutants:
```
[:400]  DG-071 (400, '120.9390', '5.7079')  DG-075 (400, '120.9391', '5.7079')
[:405]  DG-071 (405, '120.9224', '5.8949')  DG-075 (405, '120.9224', '5.8949')
[:406]  DG-071 (406, '120.9186', '5.9508')  DG-075 (405, '120.9224', '5.8949')   ← no-op on the paper's input
```

B2 replay:
```
replay ×2 at HEAD 5f105823 → BYTE-IDENTICAL to each other
diff committed JSON vs replay:  27c27  "git_commit": "6d30c105…"  →  "5f105823…"   (only line)
diff committed MD   vs replay:  12c12  - Git commit: `6d30c105…`  →  `5f105823…`   (only line)
replay at 6d30c105 (scratch worktree) → cmp JSON && cmp MD → "replay at 6d30c105 BYTE-IDENTICAL to committed artifacts"
committed: dda89609…0caf (JSON)  a7bd11e5…f647 (MD); script sha c745bcf5…5386
```

Candidate fix 1 — widened differential (scratch test copy, line 478 → `500 if bundle_number == 0 else rng.randint(2, 8)`):
```
on mut-cap400 → FAILED (failures=1) test_differential_against_independent_reference
on mut-cap406 → FAILED (failures=1) test_differential_against_independent_reference
on mut-cap8   → FAILED (failures=1) test_differential_against_independent_reference
on UNMUTATED  → Ran 25 tests in 0.288s  OK
```

Candidate fix 2 — retained-bundle value-of-record pin (scratch file `test_retained_pin_scratch.py`, ten literals + 3 header fields, `skipTest` when `PINNED_BUNDLE_PATH` is not a file):
```
against clean checkout → OK
against mut-cap8       → FAILED  {'DG-071': (8, '117.3810', '123.1338', …)} != {'DG-071': (406, '116.9720', '120.9186', …)}
against mut-cap400     → FAILED  {'DG-071': (400, '117.2236', '120.9390', …)} != …
against mut-cap405     → FAILED  {'DG-071': (405, '117.0321', '120.9224', …)} != …
against mut-cap406     → OK   (no-op mutant; correctly indistinguishable)
corpus-absent simulation (PINNED_BUNDLE_PATH patched to /nonexistent) → OK (skipped=1) "runs_window corpus absent (clean checkout without bundles)"
```

Fifth independent replication of the values of record, via the test module's `_independent_reference` (not the producer) on the retained bundle:
```
DG-071 406 116.9720 120.9186 122.9227 5.9508
DG-075 405 117.0321 120.9224 122.9270 5.8949
tiling 0.0000004 100
```
