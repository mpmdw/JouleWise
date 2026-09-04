```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Mapped every launch-lineage location dependency and proposed a digest-preserving relocation carrier; production work awaits the required three-seat ruling and cold gate.",
  "workspace": {
    "base_requested": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "base_mode": "exact",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-LINEAGE-RELOCATABLE-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/LINEAGE-RELOCATABLE-01/01-sol-report.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_arm_readiness.LaunchConsumptionV2Tests.test_start_settle_completion_form_one_authenticated_lineage tests.test_arm_readiness.ArmPackReplayComparisonTests.test_successor_replay_accepts_same_repository_relative_relocation",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 2.124s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests in [0-9.]+s[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 - <<'PY'\nimport json\nfrom pathlib import Path\nrow = json.loads(Path('docs/process/state_kernel.json').read_text())['tasks']['LINEAGE-RELOCATABLE-01']\nprint(row['id'], row['lane'], row['status'], len(row['dependencies']))\nprint(row['acceptance']['summary'])\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "LINEAGE-RELOCATABLE-01 agent queued 0",
          "A ruled design for authenticating a launch lineage from a relocated checkout exists, with the consult that produced it on record."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^LINEAGE-RELOCATABLE-01 agent queued 0[\\s\\S]*A ruled design for authenticating a launch lineage from a relocated checkout exists, with the consult that produced it on record\\.$"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --no-index --check /dev/null docs/process_traces/2026-09-04-fanout/LINEAGE-RELOCATABLE-01/01-sol-report.md >/dev/null; test $? -eq 1",
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
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_analysis_integration.MintLaunchLineageAuthenticationTests.test_copied_lineage_without_source_receipts_refuses tests.test_launch_window.CeremonySkipConsumerTests.test_analysis_input_refuses_missing_launch_consumption",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 0.003s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests in [0-9.]+s[\\s\\S]*OK"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "python3 - <<'PY'\nimport json\nfrom pathlib import Path\npath = Path('docs/process_traces/2026-09-04-fanout/LINEAGE-RELOCATABLE-01/01-sol-report.md')\ntext = path.read_text(encoding='utf-8')\nassert text.startswith('```json\\n')\nend = text.index('\\n```', len('```json\\n'))\nraw = text[len('```json\\n'):end]\nvalue = json.loads(raw)\nassert len(raw.encode('utf-8')) <= 8192\nassert value['schema'] == 'claude-codex-report/v1'\nassert value['genre'] == 'implementation'\nprint(f\"report envelope: {value['schema']} {value['genre']} {value['status']}\")\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "report envelope: claude-codex-report/v1 implementation blocked"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^report envelope: claude-codex-report/v1 implementation blocked$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The kernel acceptance requires a three-seat consult and a ruled design; this report is one seat and cannot adjudicate its own proposal.",
      "needs": "Magistrate must synthesize three independent seats and rule NEEDS_RULING items NR-1 through NR-3 before a resumed implementation brief."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "No counterfactual regression was added because doing so would first install an unruled relocation format and authority boundary.",
      "needs": "After the ruling, add the end-to-end moved-source regression and its tamper legs before changing production authentication."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The contract paragraph cited by acceptance exists on the unmerged decode-identity branch, not at this worktree head.",
      "needs": "The magistrate should preserve the durable on-main quotation in the evidence index and sequence the decode-identity merge before any contract amendment."
    }
  ]
}
```

## Change

This report supplies one consult seat for kernel row
`LINEAGE-RELOCATABLE-01`. The row has no dependency and is marked for agent
work, but its acceptance is a *ruled design*, not an implementer-selected wire
format. The controlling S3 ruling says that changing only the campaign-pack
path is inadequate because the consumption record, launch manifest, window
root, and lifecycle records are also reached through absolute paths
([evidence index](../../2026-09-03-kernel-batch/02-evidence-index.md#source-a--decode-identity-trace-file-32-s3-ruling)).
The starting contract statement is on branch
`fix/2026-09-02-decode-identity-set` at commit
`d6805473bf868eb076a92a2d4e8fe40ec8c150e6`,
`docs/contracts/identity_pin_projection.md:646-690`: analysis currently runs
on the filesystem that armed and launched the collection, and relocation is a
separate design decision. It is not present at this worktree head, so this
report cites it through the on-main evidence index rather than pretending it
has landed here.

### Finding and decision table

| ID | Finding or decision | Evidence | Disposition |
|---|---|---|---|
| F-ROOT | Current validation requires absolute artifact paths, an absolute manifest window root, and absolute arm-context roots. | `joulewise/arm_readiness.py:2540-2705`, especially `_validate_launch_artifact_reference`, `validate_launch_manifest`, `validate_launch_lifecycle_receipt`, and `validate_arm_context` | Confirmed forcing problem. |
| F-ORDER | Bundle authentication opens the absolute consumption path before it can authenticate the arm and discover the pack identity. It then strictly resolves the arm-recorded pack path before reading the manifest, window files, and lifecycle records. | `joulewise/arm_readiness.py:10130-10250` | A pack-only fallback cannot work end to end. |
| F-DIGEST | The campaign-pack security identity already separates content from machine location for successor packs: it authenticates the Git-committed tree digest and compares the repository-relative suffix. | `joulewise/arm_readiness.py:2737-2825`, `:7038-7107` | Reuse after a ruler chooses the relocation carrier; do not weaken. |
| F-CARRIER | The run-root locator is itself location-bound: `root_path` must resolve to the selected directory, while the bundle stores that locator's digest. | `joulewise/arm_readiness.py:10389-10447`, `:10646-10673` | Relocation must distinguish recorded location from the selected input directory. |
| F-SCOPE | Arm-context roots, the prewindow command, and T0 launch-recipe source paths remain authenticated historical facts, but post-hoc bundle admission does not need to dereference all of them. Live launch replay does. | `joulewise/arm_readiness.py:9307-9436`, `:10183-10189`, `scripts/launch_window.py:88-176` | Recommend a post-hoc-only relocation mode; preserve live behavior. |
| D-SAFE | No production or test edit is mechanically safe before the ruling. Even a resolver signature chooses authority, discovery, path grammar, and refusal semantics. | S3 ruling and orchestration requirement that the lead adjudicate design | Report only; resume after ruling. |

### Scoped design

**Forcing problem.** A **launch lineage** is the chain from a collected bundle
through the one-use record that spent its launch authorization, the arm record
that granted that authorization, and the records written as the launched
window started and settled. A SHA-256 digest authenticates bytes, but the
current reader also treats the original machine location as identity. Copying
the same Git-committed campaign pack and the same receipt bytes to another
checkout therefore fails before those bytes can be authenticated. Blindly
replacing a path prefix is not sufficient: several records repeat paths, and
their cross-record equality is part of the evidence. A **digest sidecar** below
means the neighboring file that records the expected SHA-256 of a receipt.

**Options.** Generic prefix substitution is small, but it lets an operator
declare arbitrary source-to-target rewrites and makes nested or overlapping
prefixes ambiguous. A new family of relative-path arm, consumption, manifest,
lifecycle, and locator schemas is clean for future launches, but it changes
issued bytes, frozen command records, and exact-key validators; it also cannot
make an existing lineage portable without a separately authenticated migration
record. Doing nothing retains today's honest refusal but does not satisfy the
row's clone-authentication goal.

The recommended option is an explicit **relocation carrier**: a small
canonical JSON file that is location metadata, never evidence authority. It
names repository-relative target directories for the copied custody tree and
window-plan tree, plus the campaign-pack directory inside the selected Git
checkout. It also names the source locator digest, preventing accidental use
with another lineage. The carrier is resolved relative to its own directory;
absolute target paths, parent traversal, symbolic links, automatic filesystem
search, and environment-variable fallback are refused.

The reader must keep each original reference object unchanged for digest and
cross-record comparisons. A resolver returns a separate target path used only
for input/output access. The target bytes still have to pass the existing
sidecar, SHA-256, schema, identity, temporal-order, pack-tree, and
repository-relative-location checks. Thus the carrier can select where to
look, but cannot make different evidence pass.

| Recorded absolute hop | Relocation rule in post-hoc analysis | Authentication retained |
|---|---|---|
| Locator `root_path` | Read the locator beside the selected bundle; compare its recorded role and source path to the arm context without requiring the source directory to exist. | Bundle-stamped locator digest, locator sidecar, exact role, and identical embedded lineage. |
| Lineage `consumption` | Construct the target only as `custody_pack_root/arm_readiness.consumptions/<recorded basename>`. | Original reference SHA-256, sidecar, schema, consumption identifier, and fixed namespace. |
| Arm `pack.pack_root` | Use the explicitly selected pack inside the clone. | Same pack identifier, same repository-relative location, same Git-committed tree digest, same plan and window identities. |
| Consumption `launch_manifest` | Construct the target only as `custody_pack_root/arm_readiness.t0.inputs/launch-manifest.json`. | Original reference SHA-256 and the original consumption-to-manifest identity. |
| Manifest `window_plan_root` | Use the carrier's relative window-plan target while retaining the original root string as historical evidence. | Manifest bytes remain unchanged; environment and chain must be direct children in both the recorded and target layouts. |
| Consumption environment and chain references | Read only `window_plan_root/window.env` and `window_plan_root/window-chain.zsh` at the target. | Each original digest and the unchanged manifest/consumption command arrays. |
| Lineage start, settle, and optional completion | Construct targets only in `custody_pack_root/arm_readiness.launch_lifecycle/` from the authenticated consumption identifier and event name. | Original reference digests, sidecars, receipt kinds, predecessor links, monotonic order, and identity equality. |
| Lifecycle `consumption`, `predecessor`, and `window_chain` | Compare the original reference objects byte-for-byte; use already selected target files for reads. | No reference rewriting and no relaxed equality. |
| Arm-context roots and prewindow command | Preserve as historical facts. In relocated post-hoc mode, use only the locator role/path relationship; do not dereference unrelated live-operation roots. | Live campaign and launch APIs remain absolute and unchanged. |
| T0 launch-recipe paths | Preserve in the arm-attested receipt chain. Do not replay live arm semantics in relocated post-hoc mode. | The immutable arm and consumption bytes prove that launch-time reconciliation already passed; live replay remains unchanged. |

The relocation context must be an explicit immutable argument threaded through
`authenticate_launch_lineage`, `authenticate_bundle_launch_lineage`, and the
analysis consumers that directly reopen embedded lineages. It must not be
process-global state, an environment variable, or implicit search. Absence of
the argument keeps today's behavior exactly.

**Worked example.** Suppose a launch recorded source checkout
`/source/repository`, campaign pack
`/source/repository/configs/campaigns/example_v5`, custody directory
`/source/custody/example_v5`, and window directory `/source/window`. A reviewer
clones the repository at `/review/repository`, places the copied custody and
window trees below a carrier directory, and selects
`/review/repository/configs/campaigns/example_v5` as the pack. The reader first
opens the bundle-local locator, then obtains the consumption record from the
carrier's custody target. After authenticating that record and its arm, it
checks the selected clone pack at the same repository-relative location and
with the recorded committed-tree digest. It then opens only the fixed manifest,
window-file, and lifecycle locations shown above. Deleting the source tree does
not matter. Changing one copied byte, committing a different pack byte, moving
the pack to another repository-relative directory, swapping a lifecycle
record, or inserting a symbolic link still refuses.

### NEEDS_RULING and exact continuation checklist

| Item | Question and options | Recommendation | Work blocked |
|---|---|---|---|
| NR-1 | Choose the authority model: generic prefix map; new relative receipt schemas; explicit non-authoritative relocation carrier over immutable issued bytes; or retain the current non-relocatable design. | Choose the explicit carrier. It makes existing lineages reviewable without rewriting evidence and keeps every digest binding. | Resolver API, carrier schema, contract text, and production tests. |
| NR-2 | Choose the operating boundary: permit relocation in live launch/campaign replay, or only in post-hoc analysis when an explicit carrier is supplied. | Post-hoc analysis only. Live replay depends on boot, current checkout, and operator roots; accepting relocation there would change the physical launch gate. | Which callers receive the relocation argument and which remain absolute. |
| NR-3 | Choose the cold-gate and refusal contract: preserve the existing artifact-specific reason codes, or add a relocation-specific reason code. A **cold gate** here means an independent, clean-state review and execution pass before the changed acceptance rule may land. | Preserve existing codes and require a cold gate proving every newly accepted state is same-byte/same-pack relocation. A carrier error should be a binding mismatch, not a new scientific verdict. | Counterfactual suite and final implementation landing. |

After the magistrate synthesizes all required seats and issues these rulings,
resume with an implementation brief that authorizes the resulting contract
and decision record. Then, in order: add a failing end-to-end fixture that
creates a genuine consumption/start/settle lineage, copies the checkout and
custody inputs, deletes the source roots, and authenticates the copied bundle;
add byte-change, committed-pack-change, repository-relative-move, swapped-chain,
traversal, and symbolic-link refusal legs; implement the carrier validator and
dual logical-path/target-path resolver; thread an immutable relocation context
through every post-hoc caller; update the contract; execute the named
counterfactual by removing the relocation dispatch and show that the positive
clone test fails; then run only the touched focused modules. The lead must run
the cold gate and final diff review. No hardware collection is required.

No change was made to `docs/process/state_kernel.json`, `TASK_QUEUE.md`,
`RUN_STATE.md`, `docs/decision_log.md`, or
`docs/paper/draft-v2-skeleton.md`. After the ruling, the magistrate will need to
record the design decision and eventually change the kernel row status; those
updates remain lead-owned under the prompt.

## Verification notes

The focused tests were run only after the first report edit, as required by the
preflight rule. They confirm the existing intact-lineage and
repository-relative pack behavior, and the current refusal when copied lineage
cannot reopen source receipts. They do not verify the proposed carrier because
the required design ruling has not issued. The repository-wide test suite was
not run.

## Residual risk

This is one consult seat, not the required three-seat synthesis. The recommended
carrier has not been adversarially reviewed or exercised end to end. The source
contract paragraph is also on an unmerged branch, so implementation must not
amend the current contract as though that merge had already occurred.
