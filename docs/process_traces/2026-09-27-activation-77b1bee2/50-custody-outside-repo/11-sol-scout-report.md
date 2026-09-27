```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "All 24 W1/W2 custody locators trigger the issuer's outside-repository refusal; a declared external custody root is the recommended repair.",
  "workspace": {
    "base_requested": "670756f3fbb366d9c40a7a128766c9afc5d331cf",
    "base_mode": "exact",
    "head_start": "670756f3fbb366d9c40a7a128766c9afc5d331cf",
    "head_end": "670756f3fbb366d9c40a7a128766c9afc5d331cf",
    "upstream_end": "670756f3fbb366d9c40a7a128766c9afc5d331cf",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "ISSUANCE-CUSTODY-OUTSIDE-REPO-01",
        "action": "needs_ruling",
        "reason": "Choose the portable custody-root representation before changing the issued artifact contract."
      },
      {
        "row": "Revision 5 prepare-candidate",
        "action": "wait_for",
        "wait_for": "Blind-reviewed repair and its defect-shaped regressions"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_issue_calibration_acceptance_generation.PrepareCandidateTest.test_custody_outside_the_repository_refuses",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 13.937s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "## HEAD \\(no branch\\)"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "A new external-custody artifact contract needs a blind authority decision before implementation or issuance.",
      "needs": "Rule the custody-root representation and authorize a separate implementation scope."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Outcome blindness prevented running prepare-candidate or inspecting W1/W2 value-dependent checks.",
      "needs": "Run those checks only at the governed issuance step."
    }
  ]
}
```

## Findings

**Certain refusal.** The W2 ledger contains 24 unique W1/W2 `custody_locator` paths, 12 beneath each external night root. Applying the issuer’s own `_repo_relative_custody` to every projected locator returned `outside_repo_refusal: 24`; none was accepted. The helper requires the resolved path to lie beneath `repo_root` and raises the stated refusal otherwise ([issuer:896](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:896), [call:1244](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:1244)). W2’s copy has the same helper and call at those lines. This is a **predicted** `prepare-candidate` result: I did not run that value-reading command. The earlier [refuter §A.5](/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-77b1bee2/40-refusal-branch/22-opus-refuter.md:131) identified the same failure.

**Consumers of `source_directory`.**

| Consumer | What it needs |
|---|---|
| Issuer | A path relative to its checkout; it stores that string with each member’s two primary-file digests ([issuer:1222](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:1222), [member table:2021](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:2021)). |
| Corpus verifier | A **readable directory under its supplied root**. It reopens both files, checks their SHA-256 digests, checks the embedded lexeme and prior-set link, then reconstructs statistics ([verifier:73](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/tests/verify_calibration_acceptance_corpus.py:73)). Its banked expectations currently cover issued IDs through r7 ([verifier:55](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/tests/verify_calibration_acceptance_corpus.py:55)). |
| Reissue candidate tool | A readable directory beneath `--corpus-root` (alias `--repo-root`), with basename equal to `member_id`; it checks both bytes, digests, lexeme, and prior link ([reissue:127](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/reissue_calibration_acceptance.py:127), [CLI:560](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/reissue_calibration_acceptance.py:560)). One root is supported, but no artifact-declared map selects external night roots. |
| Production loader | No member-directory I/O. It requires the current exact member key set and digest syntax, checks embedded derivation consistency, and accepts only an issued artifact whose whole-file bytes match its registry pin ([loader:871](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/joulewise/calibration_bracketing.py:871), [loader:1127](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/joulewise/calibration_bracketing.py:1127)). Thus a path-contract change needs a validator change and a new issued byte pin; the loader alone does not establish custody readability. |
| D-138 transaction and cold gate | The transaction installs the issued artifact and every dependent pin in one reviewed re-freeze ([D-138:10361](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/docs/decision_log.md:10361)). The cold packet receives the **whole candidate**, exclusion identities and digests, and diagnostics ([runbook:3117](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/docs/phase_2/derivation_night_runbook.md:3117)); its specified packet does not itself supply a member-directory resolver. Issuance is a later transaction ([runbook:3154](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/docs/phase_2/derivation_night_runbook.md:3154)). |

The existing tests explain the gap. The issuer fixture deliberately asserts repo-relative, re-resolvable paths **and expects external custody to refuse** ([test:1518](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/tests/test_issue_calibration_acceptance_generation.py:1518)). Reissue fixtures construct a synthetic corpus beneath one temporary root ([test:27](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/tests/test_reissue_calibration_acceptance.py:27)). A validator fixture likewise supplies a synthetic relative path ([test:3131](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/tests/test_calibration_bracketing.py:3131)). I found no issuance test using the two actual external-root topology; the passing tests establish the older contract.

**Historical custody and intent.** r6 and r7 store `runs_window_*/instrument_validation/<attempt>` paths ([r6:52](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:52), [r7:52](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:52)). Those paths are covered by [`.gitignore:34`](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/.gitignore:34), are not tracked, and the sampled directory is absent from both this checkout and W2. The r6 artifact also records use of an operator backup archive for raw custody ([r6:523](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:523)). By contrast, the derivation runbook expressly places night evidence at `/Users/edr/night-custody/<PLAN_ID>` ([runbook:226](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/docs/phase_2/derivation_night_runbook.md:226)), configures the generated chain’s runs root beneath that custody root ([runbook:1083](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/docs/phase_2/derivation_night_runbook.md:1083)), and says an unissued epoch’s custody root is never moved, relocated, or offloaded ([runbook:2569](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/docs/phase_2/derivation_night_runbook.md:2569)). The path conflict was therefore present in the planned layout. I found no issuance-side `CUSTODY_ROOTS`, archive map, or `--custody-root` resolver; the `--custody-root` uses found by broad search belong to other night/arm tools.

## Repair designs

**A — declared logical archive root (recommended).** Give the new corpus an artifact-level, generation-specific `source_root` descriptor, such as a stable logical ID for the two-night archive. Keep each `source_directory` relative to that root, including its W1 or W2 night directory. At preparation, add `--custody-root` for the *existing* `/Users/edr/night-custody` parent; replace `_repo_relative_custody` at [issuer:896](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:896), pass the declared root through [selection:1203](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:1203), emit its logical descriptor at [artifact:2201](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:2201), and add the CLI flag at [parser:2371](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:2371). Resolve and contain-check every path; keep the existing ledger-to-file digest authentication.

Make the [verifier:87](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/tests/verify_calibration_acceptance_corpus.py:87) and [reissue:142](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/reissue_calibration_acceptance.py:142) select that logical root from a caller-supplied archive location, while preserving repo-root resolution for r6/r7. Make the [production validator:850](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/joulewise/calibration_bracketing.py:850) accept only the declared generation-specific descriptor and canonical, contained relative paths. The production loader still need not open custody; it authenticates the issued bytes and digests. A reader with the repository plus the two night archives arranged under one chosen parent can rerun primary-file and statistical verification at any filesystem location. The descriptor enters the whole-artifact derivation digest; file paths are intentionally outside the narrower derivation-*input* seal ([issuer:2258](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:2258)). This requires issuer, verifier, reissue, validator, focused fixtures, and the D-138 pin transaction. It does **not** require touching either original custody tree.

**B — declared per-night roots.** Record a logical root ID for each registration session and bind each member to one ID, with `source_directory` relative to that night root. The issuer accepts two explicit ID-to-existing-directory mappings; verifier and reissue accept equivalent archive mappings and apply the same digest and containment checks. The loader validates the exact root-ID set and each member’s reference without opening directories. A reader can verify separately extracted W1 and W2 archives. Change the same code sites as A plus the member key set at [validator:873](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/joulewise/calibration_bracketing.py:873) and [member table:2021](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:2021). This avoids a shared archive-parent assumption but expands the artifact schema, CLI, and tests.

For either design, the defect-shaped RED test is a synthetic checkout with ledger locators in two sibling external night roots: current `prepare-candidate` refuses; after repair it emits contained relative locators and the verifier authenticates both primary-file digests from the declared archive root(s). Add GREEN refusal cases for an undeclared root, absolute or `..` member path, symlink escape, wrong member basename, missing primary file, and one-byte file mutation. Keep r6/r7 verification green. The cold packet should state the mapping and include its verification result before the lead’s D-138 transaction. **No root or member choice may depend on measured values**: derive it solely from the fixed session/locator topology and authenticate the bytes with existing per-member digests. Copying, symlinking, moving custody, or creating a Git repository above it is not a repair under the cited constraint.

## List B and executed evidence

The issuer explicitly names List B at [issuer:205](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:205). Value-blind results:

| List B check | Probe result |
|---|---|
| Predecessor | W2 r7 file exists and its SHA-256 matches the registered r7 byte pin; `ACTIVE_ACCEPTANCE_ID` is r7. Full value-reading loader validation was not run. |
| Registration-text pins | W2 preregistration SHA-256 is `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`; Revision 5 marker and launch-context commit/digest syntax are present, with no placeholder. Row `os_build`/powermetrics equality was not inspected under the ledger-field restriction. |
| Corpus floor | Recorded count-only dry run says 6 valid W1 + 6 valid W2, with `excluded=none`: it reaches the Revision 5 floor of 12 if the issuer’s member authentication agrees. |
| Night count/order; slot count; W1 futility; W3 rule | Two named nights are permitted by [issuer:1780](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:1780); W1 then W2 is the supplied order. Dry run reports 12 declared slots each and W1 valid count 6, meeting [futility:1801](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:1801). With no W3 named, its three-night check is inapplicable. |
| Member custody | **Certain failure:** all 24 projected locators raise the outside-repository refusal. |
| Plateau inset and screens | Value dependent; unprobed. Revision 5 bypasses the historical screen-challenge veto ([issuer:1851](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:1851), [issuer:1863](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:1863)). |

Executed evidence, with only allowed locator projections and count-only output displayed:

```text
rg -o '"custody_locator"...' W2/runs/calibration_observation_ledger.jsonl | sort -u
12 W1 locators; 12 W2 locators

issuer._repo_relative_custody(each projected locator, attempt_id, W2_root)
unique_locators 24 results {'outside_repo_refusal': 24}

rg -n '^d079-epoch-25g83-derivation-w[12]-20260927:|^registration admissible|^prefix pending' .../10-w2-harvest/check-w1w2.out
W1: battery=pass recorded=pass; terminal=yes declared=12 filled=12 valid=6 excluded=none
W2: battery=pass recorded=pass; terminal=yes declared=12 filled=12 valid=6 excluded=none
prefix pending or unresolved rows: 0
registration admissible for prepare-candidate: yes

PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_issue_calibration_acceptance_generation.PrepareCandidateTest.test_custody_outside_the_repository_refuses
Ran 1 test in 13.937s
OK
```

The displayed ledger command is abbreviated to keep the capture-field exclusion clear; its actual projection matched only `custody_locator` strings. Filesystem metadata found 12 attempt directories and both named primary files in each night root. Both repositories finished clean. No W1/W2 measured value was displayed or used for a recommendation.

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Blind custody-contract ruling | needs_ruling | Lead chooses A or B | Issued artifact schema and archive verification |
| Repair implementation | wait_for | Ruling and explicit write scope | Issuer, verifier, reissue, loader validator, fixtures |
| Candidate preparation | wait_for | Reviewed repair | Governed value-reading issuance step |
| D-138 issuance | wait_for | Candidate and cold science gate | Acceptance and dependent pins |

## Critical path

Rule the logical custody representation, implement and review its external-root regression without using W1/W2 outcomes, then prepare the candidate under the existing Revision 5 inputs. The cold science gate and lead-owned D-138 transaction follow only after that candidate exists.

SCOUT: COMPLETE