ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: []
GENRE: review
EFFORT: xhigh
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# DELTA RE-AUDIT — T26 item 3 liveness fix round 1 (detached worktree @ fea89b72)

READ-ONLY refuter. DETACHED WORKTREE `/Users/edr/code/JouleWise-wt-t26-b2` @
fea89b72 (the fix-round-1 landing, committed). Never run a nap, arm,
night-custody or `[QUIET-MAC]` action; never touch the night custody root
or `runs*/`. Write NOTHING inside the worktree except transient mutation
probes that you restore (`cp <file> $TMPDIR/orig-<name>`, edit, test,
restore); confirm `git status --porcelain` is EMPTY before writing the
report — non-empty is a protocol failure, say so and stop. Never
`git checkout`, `stash`, `commit`, or canonical `unittest discover`.
Tests: `python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas tests.test_arm_readiness_integration`
(~4 min; Sol reported 180 OK skipped=12) and
`python3 -m unittest tests.test_docs_freshness`.

AUTHORITY (in this order; all on this checkout):
1. `docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`
   item 3 — the 5 s bound STRUCK, the 600 s liveness bound RULED (number and
   inclusive `<=` are ruled values; this round may move neither).
2. The three refuter reports on the e40e7502 landing (read-only):
   `/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/out/211-luna-t26b-contract.md`
   (F1/F2/F5/G2), `.../212-terra-t26b-exec.md` (F1/F2/F3; M2/M9/M8 survived),
   `.../213-sol-t26b-physics.md` (PHYS-1/PHYS-2).
3. The fix brief F-1…F-8 at
   `/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/fix-t26-b.md`
   and Sol 224's landing report with clause map at
   `.../scratchpad/out/224-sol-t26b-fix1.md` (both read-only). Per the S2
   rule: enumerate the closures each refuter demanded YOURSELF from the
   three refuter reports BEFORE opening Sol's clause map; then reconcile.

The delta is `git diff e40e7502 fea89b72` (7 files, +166/−12).

## Lenses (report each separately)

A. CONTRACT — for each of F-1…F-8: production/doc `file:line` at
   fea89b72, biting test `file:line` (or "doc — verified by grep"),
   verdict INSTALLED / PARTIAL / MISSING with counterfactual. Specifically:
   - F-1: are the three exactly-600 s tests exercising the PRODUCTION
     comparator at `joulewise/arm_readiness.py` (the `<=` site) and the
     issuance/rehearsal paths, or a local re-implementation? Cite the call
     chain for each.
   - F-2: where is the Vocabulary-B registry; does the extended census scan
     BOTH `arm_readiness_evidence.py` and `arm_readiness_evidence_t0.py`
     for `"evidence_author_t0_[a-z0-9_]+"` literals; does it fail on a
     literal that is produced but unregistered AND on a registered code
     that is never produced (or only the former — say which and whether
     the brief demanded the latter).
   - F-4/F-5: the ruling docs were amended by marker + addendum, never in
     place — verify by `git diff e40e7502 fea89b72 -- docs/` that every
     removed line (`-`) is re-emitted verbatim in the same hunk (only
     insertions), and list any removed text that did not survive.
   - F-8: the production comment was replaced (4 lines → 1); confirm no
     other production change in `joulewise/` (diffstat + the hunk).
   - Sol's flag B1: skipped=12 vs the brief's expected skipped=7 — count
     the skips per module at fea89b72 and at e40e7502 and say whether any
     skip is NEW in this delta (a new skip in a test that should bite is a
     finding).

B. EXECUTION — run at the bench (paste command + output + exit line):
   1. the five-module command and docs_freshness;
   2. mutations M2, M9, M8, M10 from the brief — re-run yourself, name the
      killing test(s) or SURVIVED;
   3. THREE of your own: (a) the equality test's constant read from the
      wrong module (patch `_MIN_IDLE_NS` and the liveness constant by the
      SAME +1 — does anything else catch the pair moving together? report
      honestly; the brief did not require it); (b) remove ONE of the three
      `_passes_at_exactly_600s` tests' assertion (assertTrue→pass) and check
      M2 is still killed by the other two; (c) drop the
      `arm_readiness_evidence_t0.py` file from the census scan — does the
      census still kill a mutant literal placed there? (if that file
      produces no such literal today, say so and mark N/A);
   4. the F-5 grep `grep -n '5 s\|≤5\|<=5\|35 s' docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md`
      with your own classification of every hit (superseded/marked block,
      quote in the resolved paragraph, or LIVE — a LIVE hit is a finding).

C. PHYSICS — re-derive §6.3.1's worst-case successful-path number from
   `arm_readiness_evidence_t0.py` and `identity_pins.py` yourself (cite
   each timeout site); state whether Sol's figure and yours agree; state
   whether the limitation text says what the code proves and nothing more.
   Check the two bench texts at
   `/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/tmp224/bench-kernel-row.md`
   and `.../tmp224/bench-coldgate-addendum.md` (read-only): does the
   addendum's arithmetic reproduce (0.499 + 3.68e-6 × 1830; × 22 230), and
   does the kernel row's acceptance make fixture receipts non-satisfying?

## Report

Severity-tiered findings (BLOCKER / SHOULD-FIX / NIT) with file:line,
counterfactual, observed output. `## Executed evidence` with every command
and exit line. One-line VERDICT: `CLEAN` / `SHOULD-FIX n` / `BLOCKER n`.
Same-signature statement: first delta on this landing; classify any
finding as test-gap / documentation-consistency / registered-limitation
and confirm no ruled number moved. End with `git status --porcelain`
(must be empty).
