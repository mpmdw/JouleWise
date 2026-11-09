# Harvest-off confirmation — Sol, 2026-11-08

**Verdict: HOLD.** The four original final-seat failure cases are repaired, but
the new `session` classification introduces one reproducible functional restore
regression. No implementation fix is made by this confirmation seat.

Reviewed `2cfafa198..d2e512a53` on the pre-created, initially clean branch
`align/2026-11-08-hoff-confirm-sol`. Authority: the confirmation brief, both
DELTA2 reports, HARVEST-OFF-AGREEMENT, the final-round lead rulings in
HARVEST-OFF-MERGED, and `origin/main:docs/perf/SPEED-TOOLBOX.md`.

| Requested confirmation | Result |
| --- | --- |
| `runs/` exemption | Original bypass closed. The real CLI binds selected uncovered files as declared inputs; an unresolvable plan selects `declared_directory_mode=bind`, binding the directory's bytes and membership. Both seats' CLI witnesses and honest ledger restores pass. |
| Classify link chains before realpath | Original external-alias retarget bypass closed. Hop texts and the resolved target are now bound, including class `session`. The unchanged two-hop session alias restores; the three-hop case below regresses. |
| Ignored-directory membership | Original added-file bypass closed. Bound directories carry sorted names/sizes and verification re-enumerates; declared ledger sizes are excluded from membership, preserving prefix restoration. The original added-file and honest ledger witnesses pass. |
| Refuse `..` | Original symlink-parent/`..` witness passes by refusal. The new declared-input control also refuses. No lexical `normpath` remains in `_link_chain`. |

## MEDIUM — unchanged session chain cannot restore

An ordinary operator alias can have this layout, with **no changed receiver
bytes or links**:

`S/selected.json → external/operator-current → S/current.json → data.json`

Finalize and pack succeed. Finalize records
`/closure/links/selected.json/class = "session"`, target `S/data.json`, and three
hop texts. At unpack, `S` is correctly absent while the snapshot is in sibling
staging. `_link_chain` (`harvest_offload.py:217`) calls `lstat` on the absent
`S/current.json`, stops with two hops, and reports target `S/current.json`.
`_verify_closure` (`:475–483`) recognizes the restore namespace for classification
but does not map filesystem inspection into staging. It refuses the honest
restore before publication.

`test_unchanged_external_alias_to_session_symlink_restores` reproduces this as
an ordinary failing assertion, alongside passing direct-alias and declared-`..`
controls. A separate synthetic comparison loaded the offload source from each
named revision: `2cfafa198` restored the unchanged layout; `d2e512a53` refused it.
Log: `/private/tmp/hoff-confirm-sol-baseline.log`. This establishes an introduced
availability failure, not changed scientific output or an adversarial race.
Whether a native session currently uses this nested alias is unknown.

## Verification

Every unittest process selected only one module; processes ran sequentially.
Common environment:

```sh
env TMPDIR=/private/tmp PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
  JW_B5_SYNTHETIC_ONLY=1 JW_WP22_FULL=1 JOULEWISE_BACKUP_ROOTS= \
  GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 PIP_CONFIG_FILE=/dev/null \
  python3.13 -B -m unittest -v <selection>
```

Brace notation below expands the selections in the repository's zsh shell.
Logs: `/private/tmp/hoff-confirm-sol-<log>.log`.

| Selection | Result | Seconds | Log |
| --- | --- | ---: | --- |
| `tests.align.test_hoff_delta2_sol1` | 9 pass | 4.381 | delta2-sol1 |
| `tests.align.test_hoff_delta2_sol2` | 11 pass | 3.214 | delta2-sol2 |
| `tests.align.test_harvest_off_review_sol2.{ArchiveEqualityTests,MemoTests}` | 4 pass | 39.838 | equality-memo |
| `tests.align.test_v4_next_arm_packet.{ArmOrderWitness,ArmRebuildTests,R17ReviewFinalityTests}` | 13 pass | 39.024 | dwell-finality |
| `tests.align.test_harvest_off.{DocumentMemoTests,MemberDedupeEqualityTests,R17ReviewCustodyTests,RunnerTests,SyntheticV4SessionE2ETests,WorkerSizingTests}` | 21 pass | 12.099 | integration |
| `tests.align.test_hoff_delta_sol2` | 13 pass | 2.288 | prior-delta |
| `tests.align.test_hoff_confirm_sol` | 2 pass, 1 failure | 0.069 | confirm |

The 177-file serial/no-memo versus pooled/memo archive is byte-identical without
projection. Memo isolation, changed-byte misses, failure retry and member scope
pass. Dwell order, including the ruled installer-end rewrite, passes. Final
selections total 74 tests: 73 pass, one failure, 100.913 seconds. A preliminary
three-test probe took 0.106 seconds and exposed the same nested-chain refusal.
All fenced modules report zero forbidden custody accesses. New test AST parsing
and `git diff --check` pass.

The required observational `python3.13 -B scripts/fixture_orphan_census.py
--fail-on-orphans` exits 2: `PermissionError: [Errno 1] Operation not permitted:
'ps'`. Census count/rows are unavailable; no process was changed.

## Handoff

Changed only this report and `tests/align/test_hoff_confirm_sol.py`, committed
locally on the requested branch; no push. Coordination state is untouched.
No network, real measurement/custody reads, analysis pipeline, weights, native
MLX execution or quiet-window work ran. The full suite was prohibited and was
not run; total test time stayed below two minutes.

Next exact step: the lead repairs session-chain inspection against staging while
preserving canonical restore targets and external-hop bindings, then reruns the
new witness and both DELTA2 modules. Native N1 census/finalize timing, N2
cross-host equality, representative RSS and real installer/quiet-dwell gates
remain lead-owned outside this sandbox. No new scientific ruling is requested.
