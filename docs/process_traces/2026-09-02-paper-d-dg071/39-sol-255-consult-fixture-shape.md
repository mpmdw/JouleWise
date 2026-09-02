# Sol xhigh consult (255) — fixture-shape packet (file 38), verbatim

Seat: gpt-5.6-sol, xhigh, `--genre review`, workspace-write with empty write scope, read-only on `/Users/edr/code/JouleWise-wt-paper-d2` at `73417fee`. Envelope 3.3 KB, `findings`, `complete`, rc=0. Scratchpad paths redacted to `<scratchpad>`.

---

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The provenance regression remains under-specified, and the proposed property-derived linear fixture still admits globally wrong Git queries; pinning the published command directly is the smaller closure.",
  "workspace": {
    "base_requested": "73417feebcfc389acf4112a3b27e5d5f65b68983",
    "base_mode": "exact",
    "head_start": "73417feebcfc389acf4112a3b27e5d5f65b68983",
    "head_end": "73417feebcfc389acf4112a3b27e5d5f65b68983",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 1,
      "nit": 1
    },
    "findings": [
      {
        "id": "G1-SF1",
        "severity": "should_fix",
        "title": "Neither the current fixture nor the proposed linear property fixture closes the published Git-command contract"
      },
      {
        "id": "G1-N1",
        "severity": "nit",
        "title": "The current fixture still admits its tuned HEAD~2 lookup"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PROBE_TMP=<scratchpad>/dg071-provenance-sol/unittest-tmp; mkdir -p \"$PROBE_TMP\"; TMPDIR=\"$PROBE_TMP\" /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 27 tests in 0.527s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 27 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python <scratchpad>/dg071-provenance-sol/replay_results.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "counter-all-refs     same_as_reference=False",
          "counter-first-parent same_as_reference=False",
          "counter-follow       same_as_reference=False"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "counter-follow\\s+same_as_reference=False"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical discovery suite was not run, as expressly prohibited; the allowed focused module passed.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The Git experiments cover the proposed linear history and selected merge, rename, and extra-ref counterexamples, not every Git topology or history-rewriting feature.",
      "needs": ""
    }
  ]
}
```

## Findings

### G1-SF1 — should-fix

The current test has the reported ADD-only and directory-pathspec holes. The proposed H1–H3 fixture kills those holes, but it does not close the class claimed in Q2: `--first-parent`, `--follow`, and three additional wrong queries all pass both proposed linear repositories and P1/P2′/P3.

### G1-N1 — nit

`HEAD~2` still passes one current-shape repository. Different post-producer depths kill the fixed-depth family across the pair, but this is only one symptom of the broader specification problem.

## Q1 — Diagnosis

I reject the diagnosis as the complete explanation.

Mutant enumeration caused the repeated repairs, but the deeper problem is trying to prove a globally specified Git query from black-box outputs on finitely many linear histories. The existing equality to the known script commit already expresses the desired result for its fixture. Adding P1/P2′/P3 to that same fixture explains why the expected SHA is right; it does not make an implementation that returns that SHA correct on other repositories.

P2′ is also not equivalent to the reference command on every full-history DAG. In a scratch merge where two incomparable branches both changed the script to identical current bytes:

- Reference `git log -1 … -- <path>` returned `d9a910fe…`.
- `<reference>..HEAD` contained `da31f91d…`, which independently changed the path.
- Thus literal “no commit in the range changes the path” rejects the reference result.
- Using another path-filtered `git log` to check P2′ hides that side commit through Git history simplification, but then the purported property check merely repeats the behavior being tested.

The test should exist: `git_commit` is a published provenance field, and prose plus `script_sha256` are reader-verification material rather than executable regression protection. But the test should pin the published command contract, not claim that two fixture histories prove all Git histories.

## Q2 — Cure shape

The proposed fixture was built as two repositories with:

- add producer, then modify producer;
- later change to `scripts/other.py`;
- two versus four commits after the producer modification;
- equality to the known modification commit plus P1/P2′/P3 checks.

`PASS` means the command returned the known commit and satisfied all three checks in that repository.

| Implementation | Candidate A | Candidate B | Classification |
|---|---:|---:|---|
| Reference path-scoped log | PASS | PASS | Correct |
| `rev-parse HEAD` | FAIL | FAIL | Named wrong implementation |
| `rev-parse HEAD^` | FAIL | FAIL | Named wrong implementation |
| `rev-parse HEAD~2` | PASS | FAIL | Named wrong implementation |
| Unscoped `git log -1` | FAIL | FAIL | Named wrong implementation |
| `git log … -- scripts/` | FAIL | FAIL | Named wrong implementation |
| `git log … --diff-filter=A … <path>` | FAIL | FAIL | Named wrong implementation |
| `git log --first-parent … <path>` | PASS | PASS | Wrong outside the fixture |
| `git log --follow … <path>` | PASS | PASS | Wrong outside the fixture |
| `git log --diff-filter=M … <path>` | PASS | PASS | Own mutant; wrong outside fixture |
| `git log --no-merges … <path>` | PASS | PASS | Own mutant; wrong outside fixture |
| `git log --all … <path>` | PASS | PASS | Own mutant; wrong outside fixture |

Executed counterexamples:

| Survivor | Counterexample | Reference | Survivor |
|---|---|---|---|
| `--first-parent` | Script changed only on a merged side branch | side-branch change `2bfc9eb8…` | older first-parent change `294dc3d0…` |
| `--follow` | Conflicting script edits resolved by the merge | merge resolution `e9deaae1…` | parent change `dde88a6d…` |
| `--diff-filter=M` | Script was added but never subsequently modified | add commit `d0288bdb…` | empty result |
| `--no-merges` | Latest script bytes were created by merge resolution | merge resolution `e9deaae1…` | parent change `dde88a6d…` |
| `--all` | An unmerged ref has a later script edit | reachable main commit `7ee72fdf…` | unreachable branch commit `b615646a…` |

Therefore neither `--first-parent` nor `--follow` counts as correct for the stated full-history reference. Both merely coincide on the linear fixture. `--follow` also coincided on a pure rename probe, but diverged on merge histories.

The simpler cure is to test the exact command already published in `PROVENANCE_DISCLOSURE`, while retaining one real-Git integration smoke:

```python
def test_git_commit_uses_the_disclosed_path_query(self) -> None:
    expected_commit = "a" * 40
    completed = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=f"{expected_commit}\n",
        stderr="",
    )

    with mock.patch.object(
        ISSUER.subprocess,
        "run",
        return_value=completed,
    ) as run:
        self.assertEqual(ISSUER._git_commit(self.root), expected_commit)

    run.assert_called_once_with(
        [
            "git",
            "log",
            "-1",
            "--format=%H",
            "--",
            ISSUER.SCRIPT_REPOSITORY_PATH,
        ],
        cwd=self.root,
        check=True,
        capture_output=True,
        text=True,
    )
```

This is intentionally implementation-specific because the exact invocation is part of the artifact’s published contract. It kills every command substitution in the table without another fixture escalation. P1/P2′/P3 may remain as fixture self-audits or artifact validation, but they should not be described as proving equivalence on every repository.

## Q3 — Merge gating

Merge #276 now and record the exact-command test as a should-fix kernel row on main.

A reader loses no current artifact evidence: the producer uses the disclosed reference command, the recorded script hash matches, and the artifact has already replayed byte-identically. Landing another fixture repair in-PR adds no new fact about the paper’s values or current provenance; it strengthens protection against a future edit and triggers another test-only fresh-pass cycle.

Merging now leaves a maintenance risk—someone could change the command before the kernel row lands—but not a defect in the paper artifact the reader receives. That distinction makes this should-fix, not a merge blocker.

## Q4 — Severity

- **G1-SF1: should-fix, affirmed.** Directory-wide and ADD-only lookups are plausible mistakes, and the current regression does not kill them. The artifact is nevertheless correct and independently replayed.
- **G1-N1: nit, affirmed.** `HEAD~2` is fixture-tuned rather than a plausible general implementation. It is useful diagnostic evidence but does not increase artifact risk.

## Q5 — Process

File 36’s `SF1 ≠ M1` reasoning was not correct; the trigger should have fired at SF1.

For Ed reading the record, both defects have the same operational signature:

- M1: a wrong `HEAD` implementation passed because the two fixture HEADs were accidentally identical.
- SF1: a wrong `HEAD^` implementation passed because the expected producer commit was accidentally HEAD’s parent.

“Asserted a property the producer lacked” versus “discrimination incomplete” does not separate them: M1 escaped precisely because the fixture’s discrimination was incomplete. Both cures changed fixture history to prevent an accidental equality.

Rule 11 triggers on the second fix round for the same defect, not on discovery of a third mutant. M1’s repair was the first fixture-shape round; repairing SF1 was the second. File 36’s prospective “third survivor” rule therefore moved the trigger one round later than the charter. Its analogy to the earlier accepted arithmetic residual was also inapposite: no prior ruling had accepted HEAD-relative provenance lookups as an unavoidable residual.

## Residual risk

The exact-command test closes the command-substitution class, not the larger question of whether Git’s default merge-history simplification is the ideal semantic definition of “last changed.” If a semantic rather than command-defined provenance field is desired later, merges, renames, multiple parents, shallow history, replacement objects, and unreachable refs require an explicit contract.

## What this consult did NOT check

- Did not run the prohibited canonical suite.
- Did not independently replay the artifact, recompute its values, or revisit producer correctness.
- Did not inspect anything outside the packet’s authorized evidence set.
- Did not exhaust all Git versions, octopus merges, shallow clones, grafts, replacement objects, or path mode/type changes.
- Wrote nothing under the checkout; all constructed repositories and probe material remained under the authorized scratch directory.