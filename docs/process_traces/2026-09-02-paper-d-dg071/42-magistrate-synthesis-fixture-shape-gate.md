# Magistrate synthesis — the fixture-shape gate (files 38–41), 2026-09-02

Three seats ruled on packet 38 in parallel, read-only at `73417fee`: a cold
Fable seat (file 40), an Opus 5 contract-lens refuter (file 41), and a Sol
xhigh consult (file 39). Each built its own fixtures and mutant tables. The
magistrate synthesizes; it lowers no severity and overrules nothing below.

## Where the three seats agree (adopted without synthesis)

| Question | Unanimous answer |
| --- | --- |
| Q1 diagnosis | Enumeration is real but incomplete: ALL discrimination is carried by the fixture history; adding P1/P2′/P3 assertions to the same history adds no power (the test already knows the correct sha by construction). The test should exist — `git_commit` is a published field and an add-commit producer would make the reader's own `git show` check raise a false alarm |
| Q2 closure | The packet's H1–H3 shape does NOT close the class. Opus: H1 REGRESSES a kill the committed fixture has (`--diff-filter=M` dies today because the script's only change is its add; it survives H1–H3), and `--all` passes with P3 asserted and green. Cold seat: `--all`, `--first-parent` and "start from `HEAD^`" all pass H1–H3. Sol: `--first-parent`, `--follow`, `--diff-filter=M`, `--no-merges`, `--all` all pass. **The magistrate's candidate cure is withdrawn** |
| `--first-parent` | WRONG. The cold seat proved it on the real repository: PRs land as merge commits, and for `docs/paper/round7/fill-checklist.md` on main the reference returns `7fc87a7f` while `--first-parent` returns the merge `31de700a`. After #276 merges, a first-parent producer would record the merge commit |
| Q3 merge gating | #276 merges now; the cure is test-only, changes no artifact byte, and lands on main under a kernel row as its own small PR that touches ONLY the test file (any producer edit moves the reference's answer and voids byte-identical replay) |
| Q4 severities | G1-SF1 should-fix, G1-N1 nit, both affirmed. Opus: SF1 is if anything understated (the committed fixture admits eight of its thirteen candidates; `--all` is the one with a reader consequence — it can record a commit absent from the reader's clone) |
| Q5 process | File 36's "SF1 ≠ M1" was wrong when written; the trigger should have fired at SF1. Sol 253 had classed SF1 as "the same fixture-construction class as its predecessor" (file 35 line 171 — bench-verified this session) and file 36 recorded that and ruled the other way without a reason. Opus: file 36 cited file 32 Q1 for a proposition broader than its holding — the actual text is "a residual that the ruling enumerated and accepted is not a recurrence; a recurrence is the same defect class appearing where the process believed it had closed it" (bench-verified this session) — and `HEAD^` was never enumerated; and cited file 33 Q1 for a principle that section does not contain (file 33 §1 is about the hermetic-closure premise) |

## The one split, and its synthesis

**Cure shape.** Three shapes were offered:

- Sol (file 39): pin the disclosed command itself — mock `subprocess.run`
  and assert the exact argv `["git","log","-1","--format=%H","--",SCRIPT_REPOSITORY_PATH]`
  with `cwd=repository_root` — plus one real-git smoke. Kills every argv
  substitution by construction because the argv IS the published contract
  (`PROVENANCE_DISCLOSURE` names the command, not a property).
- Cold seat (file 40): an axis-derived history pair F2 — shared prefix
  root → add → L (modify to on-disk bytes); repository A stops at L so L IS
  HEAD (kills every `HEAD~k` and "start from `HEAD^`"); repository B merges
  L `--no-ff` (kills `--first-parent`), changes `scripts/other.py`, adds an
  empty commit, and carries a later producer change on a ref HEAD does not
  reach (kills `--all`); every commit gets a distinct pinned timestamp so
  no result depends on tie-breaking; the shape facts are asserted with git
  so a simplified fixture fails loudly. Code in file 40. Residual: `--diff-filter=M`
  (nit).
- Opus (file 41): a seeded generated-history differential against a
  12-line oracle (newest commit whose blob at the path differs from its
  parent's) — no mutant named anywhere; 8 histories ≈ 1.7 s; or, if too
  costly, a six-shape single-repository set (script only added; modified
  after add; near-miss sibling; abandoned ref; producer == HEAD; merge).

**Ruling.** The kernel row carries **Sol's argv pin as the contract test
AND the cold seat's F2 pair as the real-git integration fixture**, with the
add-only repository shape retained so the `--diff-filter=M` kill is not
lost (Opus finding 1). Reasoning: the argv pin closes the whole
command-substitution class — including `--follow`, `--first-parent`,
`--diff-filter=M`, glob pathspecs and anything not yet named — without the
test having to classify any of them as right or wrong, because the
disclosure names the command; F2 then exercises the real code path against
real git (the `cwd`/`repository_root` binding, refusal on empty output, the
producer-is-HEAD shape that Opus finding 5 shows the current `≠HEAD`
assertion mishandles). Opus's differential is recorded as the NEXT spend if
F2 ever yields a survivor: the row states that a survivor of the combined
shape is not a prompt for a fourth fixture feature.

**`--follow`.** The seats split three ways (Sol: wrong under conflicting
edits resolved by merge; cold seat: equivalent at `-1` except when a
merge's parents share a timestamp — a synthetic artefact; Opus: identical
by construction at `-n 1`, verified under a real rename). The magistrate
does not rule on git's merge-walk semantics: under the argv pin the
question is moot, and no fixture is to be engineered to kill `--follow`.
Sol's counterexample used unpinned timestamps and may be the tie artefact
the cold seat found; this is recorded, not decided.

## Findings against the packet (charter §6 hygiene), accepted

- Opus finding 8: Q3 asked for the answer "in terms of what a reader loses",
  a quantity provably identical across both alternatives (test-only cure).
  The frame steered toward a manufactured harm. Accepted against the
  magistrate; the discriminant was regression exposure over the interval
  vs. a forbidden fourth same-signature round.
- Cold seat: the packet's fixture list did not test its own P3, and the
  packet asserted `--first-parent`/`--follow` "indistinguishable" without
  a merge history. Accepted.
- Opus finding 10: the packet's `head2: FAILED` row was a two-commit
  scratch-root artefact, disclosed in the packet, but the evidence block was
  therefore not a clean replay of the finding under adjudication. Accepted.
- Cold seat: no charter §9 expected digest was supplied to the seat
  independently of the packet. Accepted; the seat verified it against the
  registry itself.

## Process proposals for Ed (NOT installed — rule 11 reserves process rules)

1. Cold seat: "a survivor the cure's own record named in advance is a
   residual; a survivor it did not name is a recurrence, and two unnamed
   survivors in a row fire the trigger."
2. Opus: "the party proposing to continue should not be the party
   classifying the defect against a written trigger" — classification
   belongs with the finder or a cold seat.

Both go in the Ed follow-up email alongside the file 36 statement they
correct. The magistrate's own view: both are the same rule seen from two
sides and (2) is the enforceable form.

## Kernel row installed on this branch

`DG071-PROVENANCE-TEST-01` (see `docs/process/state_kernel.json`): test-only
PR on main after #276; shape = argv pin + F2 pair + add-only repository;
acceptance evidence = the mutant table (every named candidate in files
39–41 killed except `--follow`, which is not a target); fallback → Opus's
differential, never another fixture feature.

## What changes in this PR

Nothing in code. Files 39–42 and the kernel row. The producer, the test,
and the artifact are as at `6b6deb2f` / `2eea71fe`; the eight values of
record are unchanged.
