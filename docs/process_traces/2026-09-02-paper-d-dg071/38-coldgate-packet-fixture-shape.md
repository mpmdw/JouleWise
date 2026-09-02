# Cold-gate packet — the provenance test's fixture-shape class, third occurrence (2026-09-02)

Assembled by the magistrate for a cold Fable seat (packet-only, no loop
context), an Opus 5 contract-lens refuter, and a Sol xhigh consult, all
read-only on `/Users/edr/code/JouleWise-wt-paper-d2` at the PR #276 head
(`e6687638`). The seats read this packet and the primary evidence it names;
they do not read the loop.

## Why this gate is convened (mandatory, not discretionary)

Rule 11 makes two things mandatory here and the magistrate is not asking
whether they apply:

1. **Standing escalation trigger.** File 36 (`36-fresh-pass-disposition-and-reissue.md`,
   §Escalation-trigger statement) committed in writing: *"If the next pass
   finds a third survivor of this class the standing trigger fires and the
   next spend is a consult, not a fix."* The next pass (terra 254, file 37)
   found two.
2. **Second fix round on the same defect.** The defect "the provenance test
   passes wrong implementations because of fixture shape" has now been
   fixed twice at the bench: M1 (fix round 4, `70147173`, file 34) and SF1
   (`6b6deb2f`, file 36). File 36 argued SF1 was a different defect from M1
   (property absent vs. discrimination incomplete). The magistrate withdraws
   that distinction for the purpose of this gate: by any reading, SF1 and
   G1-SF1 share a signature, so a third bench fix would be a second fix
   round on the same defect, which rule 11 reserves to a cold gate.

The producer itself is not in question: the committed artifact replays
byte-identical at `dfe69194` (terra G3), the recorded `script_sha256`
equals `git show 6b6deb2f:scripts/issue_dg071_dg075_statistics.py |
shasum -a 256` (terra G2, both `d657d75f…`), and the eight values of
record are unchanged (terra G4). What is under-built is the TEST's power
to distinguish the correct `_git_commit` from wrong ones.

## The three occurrences (primary evidence)

| Round | File | Finding | Wrong implementation that passed | Cure applied |
| --- | --- | --- | --- | --- |
| Cold gate on delta 3 | 33 (Opus M1) | the two-checkout test asserted a property the producer lacked; passed because both scratch repos had identical HEADs | `git rev-parse HEAD` | re-scoped test: two repos, same producer commit, different HEADs (`70147173`) |
| Fresh pass 1 | 35 (Sol 253 SF1) | history was producer → one empty HEAD commit | `git rev-parse HEAD^` | history root → producer → unrelated → later; asserts ≠ HEAD and ≠ HEAD^ (`6b6deb2f`) |
| Fresh pass 2 | 37 (terra 254 G1-SF1, G1-N1) | producer never modified after add; no other file under `scripts/` ever changes | `git log -1 --format=%H -- scripts/`; `git log --format=%H --diff-filter=A -1 -- <path>`; (nit) `git rev-parse HEAD~2` | none — this gate |

The test as it stands: `tests/test_issue_dg071_dg075_statistics.py:653`
(`test_producer_commit_is_the_scripts_last_commit_not_head`). The function
under test: `scripts/issue_dg071_dg075_statistics.py:398` (`_git_commit`,
`git log -1 --format=%H -- scripts/issue_dg071_dg075_statistics.py`).

## The magistrate's diagnosis (offered, not ruled — the seats may reject it)

Each cure added the fixture feature that kills the newest NAMED wrong
command. The space of wrong commands is open-ended, so a test built by
enumerating them can always be met by one more. The test asserts
`git_commit == <the sha the fixture knows>`; it never states WHAT
property the recorded commit must have. The property, as the Method prose
now defines it (`PROVENANCE_DISCLOSURE`, script line ~116), has three
parts:

- P1 — the commit CONTAINS the recorded bytes: `git show <git_commit>:<path>`
  hashes to `script_sha256`;
- P2′ — the commit itself CHANGES `<path>` (its tree differs from its
  parent's at `<path>`) and no commit in `<git_commit>..HEAD` changes
  `<path>`. The first half matters: a commit that leaves the script
  untouched still satisfies P1 (`git show` at it hashes equal), so P1 plus
  "no later change" alone would accept the directory-pathspec and
  unscoped-log implementations;
- P3 — it is reachable from HEAD.

A wrong implementation fails one of these on any history that has, at
minimum: (H1) the script modified after it was added (the add-commit
implementation then fails P1); (H2) a different file under `scripts/`
changed AFTER the script's last change (the directory-pathspec and
unscoped-log implementations then fail P2′'s first half); (H3) commits
after the script's last change, with a DIFFERENT number of them in the
two scratch repositories (every fixed-depth `HEAD~k` then fails in one
repository or the other — the whole family at once, not one k at a time).

The magistrate's candidate cure is therefore: (i) restate the test's
assertions as P1 / P2′ / P3 checked with git against the scratch
repository, alongside the existing equality to the known sha; (ii) build
the fixture from H1–H3 (the failure modes of the property), not from the
list of mutants seen so far; (iii) record, in the test's comment, that
the fixture is derived from the property's failure modes, so a future
survivor is evidence the property statement is wrong, not a prompt for
another fixture feature. The magistrate does NOT know whether this closes
the class or merely enlarges the fixture once more — that is Q2.

## Questions

- **Q1 — Diagnosis.** Is the structural problem the one diagnosed above
  (mutant enumeration instead of a property statement), or something else
  (e.g. the provenance definition itself is the wrong thing to test this
  way; or the test should not exist and `script_sha256` + the `git show`
  comparison in the Method prose already give the reader everything)?
- **Q2 — Cure shape.** Does the P1/P2′/P3 + H1–H3 shape close the class
  (every implementation that passes is correct on every full-history
  repository), or name a wrong implementation that passes it. Name a
  simpler shape if one exists. State whether `--follow` and
  `--first-parent` variants count as correct (the magistrate's bench
  replay finds both indistinguishable from the reference on this fixture).
- **Q3 — Merge gating.** The artifact and producer are correct; the test's
  discrimination is incomplete. Does #276 merge with the cure landed
  in-PR (a fourth fix round on the test, then a §5 fresh pass), or does
  #276 merge now with the cure as a kernel row on main? Give the reason in
  terms of what a reader of the paper's artifact loses in each case.
- **Q4 — Severity of terra's G1-SF1 and G1-N1** as graded (should-fix,
  nit). The magistrate may not lower either.
- **Q5 — Process.** Was file 36's "SF1 ≠ M1" reasoning correct at the time
  it was written, or should the trigger have fired at SF1? Answer for Ed,
  who reads the trigger statements.

## Executed evidence (magistrate, this session; `TMPDIR=<scratchpad>/tmpbench4`)

Mutant replay at `e6687638` (`mut6-<name>` copies of the two modules, one
`git init` commit, single-site replacement in `_git_commit`, focused
module):

```
base        : OK                                   [reference command]
dirpath     : OK   ← survives                      [git log -1 --format=%H -- scripts/]
addonly     : OK   ← survives                      [git log --format=%H --diff-filter=A -1 -- <path>]
head2       : FAILED (failures=2, errors=7)        [git rev-parse HEAD~2 — dies here only because the mutant repo has two commits; terra's replay in the full-history worktree passed: a fixture-tuned constant, sensitive in both directions]
firstparent : OK                                   [--first-parent variant; equal to the reference on this fixture]
follow      : OK                                   [--follow variant; equal to the reference on this fixture]
```

Terra 254's own replay (file 37, table under G1): HEAD, HEAD^, unscoped
log killed; HEAD~2, `scripts/` pathspec, `--diff-filter=A` survive.

Hash comparison (terra V3, re-run at the bench):
`git show 6b6deb2f:scripts/issue_dg071_dg075_statistics.py | shasum -a 256`
→ `d657d75fc4bfa36dbfc12249b791a73541ae6e043eb861e4050c297e537f46d9`,
equal to the artifact's `producer.script_sha256`.

## Files the seats may read

31–37 in this directory; `tests/test_issue_dg071_dg075_statistics.py`;
`scripts/issue_dg071_dg075_statistics.py`;
`docs/paper/round7/dg071-dg075-statistics.{json,md}`;
`docs/process/coldgate_charter.md`. Nothing else is needed; the loop's
briefs and transcripts are not evidence.
