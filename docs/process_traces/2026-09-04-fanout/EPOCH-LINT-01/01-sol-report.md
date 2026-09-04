```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented the read-only epoch-lint executor, counterfactual tests, and exact historical replays; permanent runsheet-revision wiring awaits a ruling on the complete obligation census and step-created heads.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-EPOCH-LINT-01"
  },
  "pathspec": [
    "configs/process/epoch_lint_b1_join_replay.json",
    "configs/process/epoch_lint_f0_f3_replay.json",
    "configs/process/epoch_lint_post_cure_replay.json",
    "docs/process_traces/2026-09-04-fanout/EPOCH-LINT-01/01-sol-report.md",
    "scripts/lint_runsheet_epoch.py",
    "tests/test_lint_runsheet_epoch.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "zsh -o pipefail -c 'python3 -m unittest -v tests.test_lint_runsheet_epoch 2>&1 | tail -n 1'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "zsh -c 'out=$(mktemp); python3 scripts/lint_runsheet_epoch.py configs/process/epoch_lint_f0_f3_replay.json > $out; rc=$?; jq -c \"{status,finding_count,kinds:[.findings[].kind]}\" $out; test $rc -eq 1'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"status\":\"REFUSE\",\"finding_count\":3,\"kinds\":[\"symbol_existence\",\"contract_required_cli_inputs\",\"file_line_coordinates\"]}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "REFUSE.*finding_count.*3.*symbol_existence.*contract_required_cli_inputs.*file_line_coordinates"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "zsh -c 'out=$(mktemp); python3 scripts/lint_runsheet_epoch.py configs/process/epoch_lint_b1_join_replay.json > $out; rc=$?; jq -c \"{status,finding_count,detail:.findings[0].detail}\" $out; test $rc -eq 1'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"status\":\"REFUSE\",\"finding_count\":1,\"detail\":\"cites scripts/generate_arm_readiness.py:28-186; definitions span 28-192\"}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "REFUSE.*28-186.*28-192"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "zsh -o pipefail -c 'python3 scripts/lint_runsheet_epoch.py configs/process/epoch_lint_post_cure_replay.json | jq -c \"{status,finding_count,check_count}\"'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"status\":\"PASS\",\"finding_count\":0,\"check_count\":3}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS.*finding_count.*0.*check_count.*3"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "No cited authority selects how a future runsheet revision declares a complete symbol, command-input, and line-coordinate obligation census, nor how a pre-ratification lint names a commit created only while the runsheet executes.",
      "needs": "Rule the declaration location and the representation of step-created source states; then complete the census, wire the lint into revision ratification, and record the clean transcript."
    }
  ]
}
```

## Change

The new checker reads only committed Git objects. A contract names the runsheet revision and the source head that a step executes. It checks Python definitions through the abstract syntax tree, confines required command-line options to the same logical command, and compares cited coordinates with complete definition boundaries. It exits zero only when every declared obligation is clean, one for findings, and two for invalid inputs. It never edits a runsheet.

Three issued replay contracts provide concrete evidence:

- The fixation-family replay at `7d586a691f3c97054b474ee0223558438f24d67e` reports the nonexistent test method, both missing confirmation inputs, and the stale test-method coordinates.
- The joint-head replay reads the runsheet at `7c068e606fae450316996b52aba33c35a681a5cd` against the command-line implementation at `558007f0a123641c3419152b3e3888e8cc6f2549`; it reports the recorded `28-186` versus `28-192` drift.
- The post-cure replay reads the runsheet at `9fd5baceba0ce78a94e4d8c35d74e79daf36a2d4` against the command-line implementation at `43525fb9b45638e25798f486af1351c4cec252bf`; all three dependency kinds pass.

The focused tests are counterfactual-shaped: one test removes a referenced method and a required option, then moves the executing source by one line. The single run must report all three dependency kinds. Separate tests prove that an option in another fenced block, or another command in the same block, cannot satisfy the checked invocation; uncommitted working-tree content also cannot satisfy a check against a named Git object.

| Finding or decision | Evidence | Disposition |
|---|---|---|
| The three required dependency checks are mechanically executable. | V1 and V2; state-kernel acceptance pointer `/tasks/EPOCH-LINT-01/acceptance`. | Implemented. |
| Both motivating failures replay against the recorded pre-cure objects. | V2 and V3; D-153 synthesis ruling R-5 and the joint re-audit blocker B1. | Implemented. |
| A corrected three-kind contract is clean against the recorded post-cure objects. | V4. | Implemented as replay evidence. |
| A complete future-revision census and ratification wire have no settled representation. | The D-153 synthesis fixes the three meanings but does not define declaration ownership or a source-state model. | NEEDS_RULING; the historical runsheet was not edited. |

### Scoped design requiring a ruling

Forcing problem: shell text alone cannot reveal which commands are post-mint consumers, which authenticator inputs their execution state requires, or which Git object contains a symbol created by an authenticated patch later in the runsheet. Inferring these facts would recreate the silent false-pass class that this row exists to remove.

Options considered:

- **Inline obligation declaration in the runsheet — recommended.** Put a machine-readable declaration beside each executing block or cited mechanics group. The declaration names the source state, Python symbol boundary, command anchor, and required options. Ratification requires a clean result and a census check proving that every declared executable block and coordinate citation is accounted for. This keeps the specification and the instrument revision in one reviewed object.
- **Separate manifest bound by a digest from the runsheet.** This is easier JSON to review and can reuse the existing symbol-range machinery in `scripts/derive_estate_anchors.py`, but it creates two revision surfaces. A stale or omitted digest link becomes another producer-consumer dependency.
- **Infer obligations from Markdown and shell syntax.** Reject. Conditional authenticator requirements depend on transaction state, and a symbol may be introduced by a later patch. Neither fact is present in the command grammar.

Worked example: the block anchored by `capture 101-ordinary` invokes the `freeze` command after the allowlist-contract closure. Its declaration must say that the same logical invocation carries `--step6-confirmation-table` and `--expected-confirmation-digest`. The checker then examines only that invocation; a comment or neighboring command cannot discharge it. For the immutable command-line audit, the declaration names `_parser` as the first definition and `main` as the last, so adding lines to `main` changes the derived end coordinate and refuses the old range.

NEEDS_RULING:

- Choose inline declarations (recommended) or a digest-bound sidecar as the authoritative complete census.
- For a symbol introduced by the authenticated fixation patch, choose an authenticated patch overlay on a named base (recommended), or require ratification to name a previously materialized preview commit. Restricting checks to already-existing heads cannot reproduce the recorded nonexistent-method defect before execution and is not recommended.

After that ruling, the exact remaining work is: encode the complete S-0 runsheet census; add a test that removing any declaration or the ratification command fails; edit the runsheet-revision procedure to require the clean command; run it at the ruled named source states; and preserve its clean JSON output as transcript evidence.

## Verification notes

The repository-wide unit-test suite was not run, as the preflight instruction explicitly prohibited it. Only the focused module added here and the three exact replay contracts were run.

## Residual risk

The executor proves only obligations present in its input contract. Until the lead rules and installs the complete census, an omitted obligation remains invisible; therefore the state-kernel acceptance item requiring every future revision to be ratified by a clean run is not yet discharged.
