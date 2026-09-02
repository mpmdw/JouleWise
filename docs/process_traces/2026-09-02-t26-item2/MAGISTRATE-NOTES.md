# T26 item 2 (gate ledger) — magistrate notes for the PR gate

Branch `feat/2026-09-02-t26-gateledger`; ruling: T26 cold gate item 2
(`docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`,
D-170). Files 01–12 in this directory are the seat briefs and the sealed
reports, in gauntlet order.

## Gauntlet record

| Stage | Seat | File | Outcome |
| --- | --- | --- | --- |
| Landing | terra xhigh (195) | 01, 02 | report `status: blocked`, `completion: partial` — NEEDS_SCOPE on `.github/workflows/gate-ledger.yml` (a second workflow file, so `ci.yml`'s untyped `pull_request` trigger does not re-run the matrix on every body edit); template + checker + tests landed by the seat; the workflow was written AT THE BENCH from the report's `minimal_change` spec and committed with the seat's work in `b36d6c2d` (Sol 233 SF3 corrected this row, which had read as if the seat delivered all four) |
| Refute, contract lens | luna xhigh (199) | 03, 04 | findings (merge-ref ≠ head, `_check_pointer` parity, labels-as-doctrine) |
| Refute, execution lens | sol xhigh (200) | 05, 06 | findings (naive pipe split, traversal coverage, malformed RUN, item-12 non-sha, input-error traceback) |
| Fix round 1 | Sol xhigh (205) | 07, 08 | nine dictated closures applied; commit `1529b09a` |
| Delta re-audit 1 | terra xhigh (208) | 09, 10 | all nine closures CONFIRMED; seven round-1 classes KILLED; one should-fix **I1** |
| Fix round 2 (bench) | magistrate | commit `2983cdd4` | `_split_table_row` guard: a backslash-escaped backtick outside a code span is a literal, never a span opener; test `test_escaped_backtick_outside_code_span_does_not_open_a_span` |
| Delta re-audit 2 | luna xhigh (215) | 11, 12 | CLEAN; classification **NEW** (agrees with the magistrate's); seven adversarial edge cases traced against GFM cell boundaries, all correct |
| Cold gate | Fable cold seat (222), Sol (221), Opus 207b counter-review | 13, 13b, 13c, 14, 15, 16 | L1 ADOPT (Opus's GFM reading; "NEW" overturned), L2 option (c) splitter + arity refusal, L3 same class / structural cure |
| Fix round 3 | terra xhigh (223) | commit `5ed6f1e9` | L2/L3 verbatim + Opus S1–S5, N1–N9; M1–M5 KILLED |
| Bench fix | magistrate | commit `55bf9f73` | F-9 regression bites (luna 227 SF1): numbered key after the indented heading; mutant `line.startswith("## ")` FAILS the test |
| Bench fix | magistrate | commit `c01c39bb` | `tests/test_check_gate_ledger.py` `setUpClass`: `os.environ["TMPDIR"]` → `os.environ.get("TMPDIR")` — CI `pr-fast (2)` failed with `KeyError: 'TMPDIR'` (runner exports none); found independently by luna 232's sibling census on the dx lane (`docs/process_traces/2026-09-02-dx-registry/18-luna-232-fresh-pass.md` F1); verified OK with and without TMPDIR |
| Pre-merge fresh pass | sol high (233) | 17b, 18 | over `55bf9f73` + `d14a818d`: `VERDICT: SHOULD-FIX 3` — SF1 `:N`/`#anchor` policy not enforced when such a file exists; SF2 two `_valid_path` parity probes non-biting (absolute-path and URL guards); SF3 landing row overstated file 02 (corrected above). F-9 repair CONFIRMED to bite (numbered probe FAILS under the `startswith("## ")` mutant, bold probe passes); all shas/seat numbers/verdicts in this table verified against the files |
| Bench fix | magistrate | commit `8207364c` | SF1: syntactic refusal of `:` / `#` in the RUN target BEFORE the existence check (`_valid_path` stays a verbatim `_check_pointer` copy, parity intact); regression creates real files named `evidence.txt:12` and `evidence.txt#anchor`. SF2: the absolute and URL fixtures now EXIST at their join-under-root spellings, so the syntax guards are the sole refusers on both sides of the parity. Mutants executed at the bench: drop the `:`/`#` refusal → `FAILED (failures=2)`; drop the `/` guard → `FAILED (failures=2)`; drop the `://` guard → `FAILED (failures=1)`; restored, `git diff --check` clean; module OK with and without TMPDIR |
| Delta re-audit 3 | luna xhigh (227) | 17 | `_split_table_row` models nothing beyond the pipe rule; B1 (D-170 absent on this branch) is a sibling-branch artefact — D-170 lands on `feat/2026-09-02-t26-install`, which merges first; SF1 fixed at the bench |

## Same-signature judgment on the test-quality class (magistrate, 2026-09-02)

"Regression that does not bite" has now appeared in two consecutive audit
rounds on this lane: luna 227 SF1 (one probe; cured `55bf9f73`) and Sol 233
SF2 (two probes; cured at the bench above). Rule 11 says the next spend is a
consult, not a third fix round. Disposition: the structural question — WHICH
probes in the module are inert, and WHY — is answered in Sol 233's
exhaustive table (22 rejection/ignore tests, each paired with the permissive
mutant that would let its row through; exactly two do not bite, both for the
same cause: the fixture never existed, so `os.path.isfile` refused it
before the guard under test could). That table is the consult's deliverable;
a separate consult seat would reproduce it. The SF2 cure therefore acts on
the class (make the fixture exist so only the guard refuses), not on one
probe, and the delta re-audit of this bench commit (a different model)
verifies the class claim, not just the two edits. No production splitter
code changed. If a THIRD round surfaces another inert probe, that is a cold
gate, not a bench fix.

## I1 same-signature classification (magistrate, confirmed by luna 215) — SUPERSEDED

> SUPERSEDED 2026-09-02 by the cold gate `16-MAGISTRATE-RULING-gateledger-splitter.md`
> §L1: the classification below ("NEW") was wrong at the class level. Round
> 1's cure INVENTED a code-span model that GFM's table pre-pass does not have
> (GFM §4.10: cell splitting consumes `\|` before inline parsing, so a raw
> pipe splits even inside backticks); round 2 patched a defect internal to
> that invention. Both rounds share the class "hand-rolled cell model ≠ GFM's
> one rule", the STANDING ESCALATION TRIGGER fired, and the cold gate ruled
> L2/L3 (Opus's splitter, refuse on arity). The text below is kept as the
> record of the wrong call. Item 8's "nothing to prune" verdict is likewise
> superseded: the code-span scanner WAS the prune target (removed in round 3).

Round 1's defect class was "representation-blind pipe split" (a naive
`line.split("|")`). The round-1 cure REPLACED it with a stateful GFM scanner;
I1 (`gate \` literal tick` swallowed the evidence cell) is an edge case of
that NEW scanner's escape handling, not a survivor of the naive split.
Signature: NEW. No STANDING ESCALATION TRIGGER (two rounds, same signature)
fired; round 2 was a bench fix under the bench-vs-session threshold (a
7-line guard + one specified test), with the counterfactual executed
against the pre-fix script: new test `FAILED (failures=1)` → with the
guard `Ran 21 tests OK` (`tests.test_check_gate_ledger tests.test_docs_freshness`).

## Apex code-reading gate (item 7) — design-level questions answered

1. **Is the checker's acceptance set the ruled one?** Yes: items 1–11
   `RUN <repo-relative path>` (rules copied from `scripts/gen_state.py`
   `_check_pointer`: no leading `/` or `~`, no `..` segment, no `://`, must be a
   regular file at the PR head) or `RUN <commit sha>` (`git cat-file -e
   <sha>^{commit}` in the checkout); item 12 sha-only and a prefix of the
   PR head; `NOT-RUN`, empty, missing, duplicate keys and malformed cells
   refused with one stable message each; input errors (missing body/root)
   exit 1 without a traceback.
2. **Does the workflow test the right object?** It checks out
   `github.event.pull_request.head.sha` with `fetch-depth: 0` (earlier
   branch commits named as evidence resolve; the merge ref is not the head)
   and passes the body through the environment, never interpolated into the
   shell line. Fires on `opened, synchronize, edited, ready_for_review` —
   `edited` is required because the ledger is filled by body edits after the
   review rounds. It is ADVISORY (own workflow, not a required check; the
   promotion is Ed's branch-protection change, kernel row
   ED-BRANCH-PROTECTION-E1-01); D-072's self-merge condition binds
   independently.
3. **Threat model.** Targets the MISTAKE class (a forgotten row). A
   deliberately pasted `RUN README.md` block is out of the threat model
   (D-161: the operator is not the adversary); the ledger's value is that
   the twelve keys must each be answered with a resolving pointer under a
   reviewer's eyes.
4. **Prune (item 8).** Nothing to prune: 171 lines of stdlib checker, 191 of
   defect-shaped tests, a 28-line template, a 60-line workflow whose header
   comment is the ONE explanation of why it is a separate file, and one
   pointer line in `docs/orchestration.md` (labels are keys; the doctrine
   text stays in D-118/D-121/D-170).

## Full-suite replay (item 9)

Run at the bench on this branch at `2983cdd4` (worktree `JouleWise-wt-t26-c`,
no seat active, fresh output file). Tail recorded in `suite-tail.txt` in
this directory.
