ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: []
GENRE: review
EFFORT: xhigh
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# DELTA RE-AUDIT — T26 items 1+4 fix round 1 + bench commit (detached worktree @ d8451daa)

READ-ONLY refuter. DETACHED WORKTREE `/Users/edr/code/JouleWise-wt-t26-a2` @
d8451daa. Write NOTHING inside the worktree except transient mutation
probes that you restore (`cp <file> $TMPDIR/orig-<name>`, edit, test,
restore — for `docs/process/state_kernel.json` probes ALSO restore
`TASK_QUEUE.md` and any file `scripts/gen_state.py` regenerates); confirm
`git status --porcelain` is EMPTY before writing the report — non-empty is a
protocol failure, say so and stop. Never `git checkout`, `stash`, `commit`,
or canonical `unittest discover`. Tests:
`python3 -m unittest tests.test_gen_state tests.test_docs_freshness` (65
tests, ~2 s) and `python3 scripts/gen_state.py --check; echo EXIT=$?`.

AUTHORITY (in this order; all on this checkout — main was merged in at
d243445d, so the coldgate trace dir is present):
1. `docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md`
   §B1–§B4 — the dictated closures for items 1 and 4 (B1 filename-trigger
   selectors + two-shape Executed-evidence test; B2 `DECISION_RULE_FLOOR`
   and the four-limb item-1 test with the B2 dependency object; B3 terminal
   decisions carry no pending dependency + status-token union; B4 dangling
   decision-reference scan, no allowlist). Note its dated addendum at the
   end (a site correction for the OTHER lane; irrelevant here).
2. `docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`
   — item 1 (D-170 status) and item 4 (executed-evidence duty), including
   the `## Addendum 2026-09-02 — item 4 enforcement (dx cold gate B1)`
   appended in this delta.
3. The two refuter reports on the 2d24ef70 landing (read-only):
   `/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/out/209-luna-t26a-contract.md`
   and `.../210-opus-t26a-exec.md`.
4. The fix brief F-1…F-8 at `.../scratchpad/fix-t26-a.md` and luna 226's
   landing report at `.../scratchpad/out/226-luna-t26a-fix1.md` (read-only).
   Per the S2 rule: enumerate the ruling's B1–B4 clauses YOURSELF before
   opening luna's clause map; then reconcile.

The delta is TWO commits: `git diff 2d24ef70 1d254bb1` (the seat landing,
4 files) and `git diff d243445d d8451daa` (the MAGISTRATE's bench commit:
kernel edits via gen_state, the decision-reference regex boundaries, and
four test-expectation moves). Audit the bench commit with the SAME rigour
as the seat's — the magistrate is not exempt; in particular:
- the regex change `(?<![0-9A-Za-z])D-\d{3}[a-z]?(?![0-9A-Za-z])` — does it
  still catch every real reference shape used in this repo (`D-170`,
  `D-170a`, `(D-170)`, `D-170.`, `D-170/D-171`, `D-170:`) and reject the
  UUID case `B09C8BDD-187C-4740`? Probe each through `re` and paste.
- the "only V5 carries D-170 dependency" subtest was turned from a live-
  kernel probe into a counterfactual that strips the installer's D-170
  dependency; confirm limb 2 fires on exactly that input and that the
  live kernel now PASSES limb 2 with the B2 dependency object byte-equal
  to the ruling's dictated shape (`kind`, `scope: close`, `state: pending`,
  `strength: hard`, `target: D-170`, `evidence: null`).
- M6c's regex was widened to accept either pending-dependency task name;
  confirm that `_assert_terminal_decisions` reports a pending dependency
  on D-170 from BOTH `T26-RULING-INSTALL-01` and `V5-TRANSACTION-01` when
  D-170 is flipped to `adopted` (or only the first — say which, and
  whether the ruling requires all to be listed).
- the dated-rulings exact set now lists both 2026-09-02 rulings: verify
  both files pass `_has_executed_evidence` on the REAL shape (command line
  + exit line, or existing `file:line`), citing the lines that satisfy it.
- `D110-MINT-DEP-RECONCILE-01` row: valid pointer, existing authority
  paths, rank 20 unique, and the fence rule text does not contradict B3.

## Lenses

A. CONTRACT — per B1–B4 clause: production `file:line` at d8451daa,
   biting test `file:line`, INSTALLED / PARTIAL / MISSING + counterfactual.
   For B1 specifically: selector (a) `**/*MAGISTRATE-RULING*.md` ≥
   2026-08-29 with the single named exclusion, selector (b) `**/*RULING*.md`
   ≥ 2026-09-03 excluding `NEEDS-RULING-*`, dated component at ANY depth,
   non-empty union; evidence shape (1) `^\$ .+` AND a different line
   matching the exit pattern, or (2) `path:N` with the path existing.
B. EXECUTION — run and paste: the two-module suite; `gen_state.py --check`;
   the brief's mutations (M7, M8, `$ echo exit`, `.md:48`-only,
   `gen_state.py:63` passes, nonexistent-path citation fails, positive
   control at both depths, NEEDS-RULING excluded; M4, only-V5,
   missing-start, M13; M6c, unknown `decided`; D-999; M6b) — re-run each
   yourself: KILLED by <test> / SURVIVED; plus THREE of your own on the
   NEW gen_state rule (satisfied decision dependency requires a `tests/`
   path whose label names an existing `def test_`): (a) label naming a
   non-existent test, (b) path outside `tests/`, (c) evidence pointer with
   an anchor instead of a path.
C. SAME-SIGNATURE — first delta on this landing; classify each finding as
   test-gap / documentation-consistency / kernel-state; state whether any
   ruled value (floor 170, the B2 dependency shape, the selectors' dates)
   moved.

## Report

Severity-tiered findings (BLOCKER / SHOULD-FIX / NIT) with file:line,
counterfactual, observed output. `## Executed evidence` with every command
and exit line. One-line VERDICT: `CLEAN` / `SHOULD-FIX n` / `BLOCKER n`.
End with `git status --porcelain` (must be empty).
