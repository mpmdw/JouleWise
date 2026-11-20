# Row 11 · C1 arm receipt predicate

Tier 2. Draft stacked on PR #836. Item 471 keeps W1 at the issued R1
pin. All execution evidence below is synthetic.

## Public pins

| Role | Commit |
|---|---|
| W1 and condition-13 reference | `b2e01464d6d4fbf2901ff4d4154df9455104a12a` |
| PR base, `align/2026-11-18-c1-series-release` | `3649cfd191e231fe059d4a3460e62368917babe8` |
| Acceptance freeze | `90ef1741907e01db89f1463c1d855c032836c4f2` |
| Predicate implementation | `0122a86bba0d479e6cef8be6c7fed383dfd6dd1c` |
| PR #813, scorer and W1 inventory | `82542232dbb7459b0320c37380925e9372afb7e8` |
| PR #831, row builder from PR #787 | `b38cef8286c7772e970760103debf187174fbad6` |
| PR #826, desk seal | `1fc28324d51f8057fa6228e6e7d42b5ea331d52c` |
| Research rulings | `c39ec79931db9da0155cc39623ca9f581e4aebb7` |
| Pipeline §3 and §4 | `2e4ab984fc51febc9ef14e01e73c79a5307e3501` |

Prepare authenticates the selected manifest window and admission before
choosing receipt coverage. Recheck binds the selected window to the
staged kit and repeats the manifest, admission, kit and registration
checks before host operations. W1 admits either exact inventory.
Post-W1 selections require the full union of the W1 and release
inventories, including the shared restore-manifest dependency. Both
option paths use the same receipt validator and the same Git and working
byte comparisons. The direct registration API retains its W1-only
default and the explicit release option retains its expanded requirement.

## Frozen acceptance and findings

Executed at the freeze and at the implementation:

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_registration.C1ArmReceiptTests
```

The freeze exited 1 after 10 tests, with 18 subtest or assertion failures and
four errors. A valid expanded receipt failed at the ordinary kit with
`registration_receipt artifact set incomplete`. A legacy-only
receipt reached the C1 stager. The W1 gate-alias fixture with a null
artifact digest also reached the stager. The expanded receipt guard
masked several more specific negative assertions on the freeze tree.
The implementation exited 0 after 10 tests. The freeze test module is
byte-identical between the freeze and implementation.

| Author verification of baseline | Severity and root cause | Implementation and named regression |
|---|---|---|
| The ordinary C1 path used a W1-only receipt check. A legacy receipt reached staging and the C1 recheck had no expanded check. | HIGH, `integration-seam` | `0122a86bb`, `test_legacy_w1_receipt_only_admits_w1`, `test_every_c1_executable_binding_is_checked_at_prepare`, `test_every_c1_executable_is_rechecked_for_working_byte_drift`, `test_recheck_refuses_legacy_substitution_and_selected_window_downgrade` all PASS. |
| Both ordinary kit entry points refused the valid combined receipt. | MED, `integration-seam`, also reported against PR #836 | `0122a86bb`, `test_combined_receipt_admits_w1_and_c1`, `test_two_receipts_bind_distinct_git_identities_before_c1` both PASS. |
| A gate path could overwrite a conflicting inventory digest. | MED, `impl-bug` | `0122a86bb`, `test_gate_report_cannot_override_an_inventoried_digest` PASS for W1 and C1. |

The fixture commits distinct inert bytes for the four executable paths
and the complete inventory in disposable Git repositories. The
collection-plan comparisons, selected-window checks, real validator,
gate report, U3 and executed-source checks run. Host probes, restore,
staging and installer operations use doubles. Legacy W1→W1, combined→W1
and combined→C1 reached the fake installer. Every binding deletion,
null, wrong SHA-256 and current-byte mutation refused. Each of the four
post-prepare mutations refused in both direct recheck and ordinary
install with zero installer calls. A missing or nonexistent commit, a
mismatched gate, a missing shared dependency and an arbitrary extra
artifact key refused. An invalid expanded receipt on W1 refused with
its digest error. The committed SHA-256 remained required when working
bytes matched the forged receipt.

Additional author-head compatibility checks passed 11 tests:

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest \
  align.test_v4_registration.RegistrationTests.test_receipt_binds_every_artifact_and_both_gate_reports \
  align.test_v4_registration.RegistrationTests.test_install_rechecks_generated_kit_before_host_operations \
  align.test_v4_receipt_tiers \
  align.test_v4_executed_closure.ExecutedClosureBindingTests.test_every_executed_module_and_script_is_in_the_receipt_artifact_set
```

## Condition 13 and write scope

`git rev-parse <commit>:<path>` returned these identical blob IDs at
issued W1, the PR base and the author head. There are zero inherited
absences or mismatches in the ten paths.

| Path | Blob |
|---|---|
| `scripts/align_r1_rehearsal.py` | `33c6876e6a988bee93fc49a0ba554f7c2c3bf277` |
| `scripts/align_r1_runtime.py` | `96b249a6eb44c4de2887aeeadff089c3040d8cfa` |
| `joulewise/align/apple/r1_runtime.py` | `261761f1a5e39220614b74d53d125022278502db` |
| `joulewise/align/apple/r1_runtime_contract.py` | `1ef822bee6d3b4951ad24cd1991ea31741d30161` |
| `joulewise/align/apple/smc_enumeration.py` | `8a1a96dcb10ebb16809717af15918d5366b0d31c` |
| `joulewise/align/apple/thermal_gates.py` | `b46769d70df02de09dbeb07e4c0020c472477dcb` |
| `configs/align/v4/r1_runtime.json` | `bf8479b26774b4d6a7bb3d44c6e2d662ddeb199e` |
| `joulewise/align/apple/r1_phase_table.py` | `e412bb4389aae4e4239b47842512db178d4b53a2` |
| `joulewise/align/apple/workload.py` | `ff30c29178ad9ccceab96140c569b8f14afa16e9` |
| `joulewise/align/apple/thermal.py` | `e7cbd6808c5a407524e3a85254090a46c33fa910` |

The registration subtree Git ID is
`668a55639e6864378963aae259a65b3d4002f754` at all three pins. The diff consists of the
three implementation files, the frozen test module and this report.
`RUN_STATE.md`, `TASK_QUEUE.md`, signed records and the release CLI are
outside the delta. The stacked base itself lacks the two scorer modules
and row builder. The separate dependency projection supplies them for
synthetic contract checks.

## Dependency contracts

The code and test projection used sparse checkout at `0122a86bb`.
For each dependency in order #813, #831, #826, the seat piped
`git diff --binary b2e01464d..<dependency> -- joulewise scripts tests`
into `git apply --3way`. The index tree is
`f26a73b053a248f6c17de27dd5237f3289c40464`. The checkout includes the
prospective frozen series manifest for U3 and the mock-local example
for the release fixtures. Initial runs with those files absent errored
at fixture setup. The checkout omits the signed registration directory.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest \
  align.test_v4_registration.C1ArmReceiptTests align.test_rl176 align.test_s_rows \
  align.test_v4_next_arm_packet.UnpackReceiptTests

PYTHONPATH=tests:. python3.13 -B -m unittest \
  align.test_align_v4_series_release.SeriesReleaseTests.test_stored_series_through_787_and_release_script_s_signature_at_102_not_101_of_154 \
  align.test_align_v4_series_release.SeriesReleaseTests.test_receipt_from_after_t3_cannot_replace_the_c1_predecessors_receipt \
  align.test_align_v4_series_release.SeriesReleaseTests.test_each_executing_release_binding_is_required_before_loading_members \
  align.test_align_v4_series_release.SeriesReleaseTests.test_receipt_covers_static_release_import_closure \
  align.test_align_v4_series_release.SeriesReleaseTests.test_finalized_validator_refusal_precedes_ledger_and_scoring
```

The first command exited 0 with 108 tests and four opt-in skips.
It includes all ten frozen Row 11 methods and the three desk-seal
unpack-receipt tests.
The second exited 0 with five tests. The stored-series release printed
`S SIGNATURE` at 102 of 154 and withheld it at 101. The post-T3 receipt
substitution exited 1 and left no report. The executable binding,
static closure and finalized-validator refusal tests passed.

## Two-receipt witness for the release owner

On the projection, the ordinary kit verified the earlier W1 receipt
and the later combined receipt. The latter reached the C1 install
double. Deleting either scorer binding from the W1-only inventory
refused in ordinary W1 prepare.

| Invented receipt | Reviewed bytes pin | Receipt commit | Receipt blob |
|---|---|---|---|
| W1-only | `179bc853e6a7b7b2196987560bdbfd72485bbf4d` | `4b1244ecfaf8c2ebd9d45f978dc62bfd0bcd1c96` | `50d45a0e28102038245345f4008269867c328041` |
| Combined | `4b1244ecfaf8c2ebd9d45f978dc62bfd0bcd1c96` | `f47560620b090f94afebfa79e2fe3088b9be5bbc` | `138907d905b5701b515a78c6f2bb22ee4343d850` |

The witness used `test_two_receipts_bind_distinct_git_identities_before_c1`
with `GIT_AUTHOR_DATE=2026-11-19T12:00:00Z` and
`GIT_COMMITTER_DATE=2026-11-19T12:00:00Z`. The fixture commits and
blobs exist only in disposable repositories.

For the predecessor check, a scratch driver wrapped
`stored_series(..., legacy_receipt=True)` from the release owner's
fixtures. It added the expanded receipt either immediately before or
immediately after committing `records/W1` and left the returned W1
record pointer intact. In both histories the expansion validated and
was committed before C1's record. The real `bound_history` accepted
the first history and refused the second with
`source SHA-256 mismatch: configs/campaigns/align_v4/registration/registration_receipt.json`.
The predecessor keeps its original receipt blob in each history.

In the refusing history, the immutable W1 record was
`7c7b853bec088a687c65e5d55807cfa8ab9c8795` with receipt blob
`8e434332ac6532d6a64b059a2f800a33123e8753`. The later expanded receipt
commit `10e5d3c1b65b8c1ce1e2f087749544f552bcad9e` carried blob
`5abeb9a577f786e34103f88c1c7a0fd49554e18a` and was an ancestor of C1
record `b6d9e21db8349dc400ddec9c3470baf28a083479`. The scratch driver
exited 0 after asserting the acceptance and the refusal.

## NEEDS_SPEC and acceptance

**Row 11, RL-182 §1.5 (RLD 19785–19787 and 20896), release predecessor
read at `scripts/align_v4_series_release.py:247–256`.** When W1 clears
under the W1-only receipt and its immutable predecessor has already been
bound, must the signing owner arrange the C1 reissue before that
predecessor is bound, or may C1 authenticate a separate prospective
expansion commit after the bound W1 record? The smallest failing history
is W1-only receipt → immutable W1 record → valid combined receipt →
C1 record pointing to the same W1 record. Ordinary registration
accepts the complete form before C1, and release refuses the differing
receipt at the immutable predecessor. The decision owner is the lead
with the signing and release owners. A distinct prospective binding
would require their rule and must preserve the post-T3 substitution
refusal. No predecessor evidence or signing relationship was altered.

| Review stage | Verified HIGH / MED / LOW | Root cause and disposition |
|---|---|---|
| Author baseline and integration reproduction | 2 / 2 / 0 | One HIGH integration seam and two MED defects are covered by the frozen tests. The second HIGH is the predecessor timing contract conflict above. Return that part to spec under PIPELINE §3. |
| Independent executing cross-family round 1 | Pending | The dispatcher or lead records the reviewer disposition on the exact candidate. |
| Integration owner and lead | Pending | The integration owner accepts the composed candidate. The lead rules on the timing conflict and retains W1 promotion and landing authority under item 471. |

Remain draft pending the ruling, executing review, both owner
dispositions and green canonical sharded CI on the accepted integration
head. The stacked draft's CI belongs to its own SHA, which still has the
base-level scorer and row-builder absences. The local fixture orphan
census command `python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans`
exited 2 because `ps` was denied. The census count is unknown.
