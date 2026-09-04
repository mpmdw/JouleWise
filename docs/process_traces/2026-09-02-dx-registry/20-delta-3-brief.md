ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: []
GENRE: review
EFFORT: xhigh
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# DELTA RE-AUDIT 3 — dx-registry lane, DETACHED worktree `/Users/edr/code/JouleWise-wt-dx2` @ 7fc87a7f

READ-ONLY. Write nothing inside the repository (scratch under $TMPDIR only);
no commit/checkout/stash/rebase; never canonical `unittest discover`.
`python3 -m unittest tests.test_paper_round7_artifacts` costs ~8 min on this
machine (retained-corpus replay); run the non-replay classes
(`RegistryAndDigestTests RefusalTests TypedArtifactCliTests InvocationTests`)
as needed and the full module at most once. Linked worktrees lack the
retained corpus for the fence CLI — pass
`--corpus-root /Users/edr/code/JouleWise` if you invoke the full replay.

## What you audit
Fix-round-3 commit `7fc87a7f` over `73f7fcc2` (`git diff 73f7fcc2..7fc87a7f`),
curing the Opus counter-review at
`docs/process_traces/2026-09-02-dx-registry/19-opus-counter-review.md`
per the magistrate's disposition `19b-...md`; seat brief `19c-fix-round-3-brief.md`,
seat report `19c-luna-237-fix-round-3.md`. The bench half (the
`docs/paper/round7/fill-checklist.md` "placement-dependent tail" paragraph)
is the magistrate's own and gets the SAME scrutiny.

## Lenses
1. CONTRACT: each accepted finding (SF2a, SF2b, NIT3, NIT4; SF1 checklist
   half) installed exactly as dictated; every sentence added to a docstring
   or the checklist TRUE of the code now. In particular: is the checklist's
   arithmetic (`181 + one per placed DX literal + 3 in full replay`; 184 / 181
   / 200) correct against `scripts/check_paper_round7_artifacts.py` —
   count the comparisons the fence emits per placed literal and in the
   replay half (XD, AQ, F4 byte identities — is it exactly three?). Opus's
   probe observed `R7F PLACED 16/16, LITERALS-ONLY COMPARED 197` — consistent?
2. EXECUTION: the new regression
   `test_multiline_producer_unavailable_is_flattened_to_last_line` — does it
   exercise BOTH exit-3 sites (`:897`, `:926` region) or only the XS one? If
   only one, is the AS site covered by construction (same helper) — state
   whether that is sufficient or a finding. Does `_producer_unavailable_message`
   change behaviour for the single-line case (exact bytes of the printed
   line before/after)? Run `python3 scripts/check_paper_round7_artifacts.py
   --literals-only` and paste the tail. Does `R7F_CORPUS_ROOT` interact with
   `REGISTRY_PATH`/`ROOT` in any way that could make the replay test run
   against the wrong tree?
3. SCOPE: `git diff --stat 73f7fcc2..7fc87a7f` — anything outside the seat's
   two files plus the checklist and the `docs/process_traces/2026-09-02-dx-registry/`
   custody files is a finding.

## Report
`VERDICT: CLEAN | SHOULD-FIX n | BLOCKER n` first line after the envelope;
per-lens findings with `file:line`, severity, executed evidence.
claude-codex-report/v1 envelope FINAL. Do not end the turn before all
lenses are done.
