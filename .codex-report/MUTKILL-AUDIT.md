# MUTKILL-AUDIT

Date: 2026-10-23 UTC. Branch: report/2026-10-22-mutkill-audit. **INCOMPLETE: execution blocked by cloud environment startup failure.**

All 93 added test methods across the four drafts were inventoried and statically reviewed by four independent reviewers, then reconciled by the lead. **Zero baseline passes, zero independently verified mutant kills, and zero empirical duplicate confirmations.** The PR authors' 135 claimed kills are claims, not this audit's evidence. No production or test file was changed.

The complete per-test map, all 135 claimed mutant IDs, inferred defect shapes, numerical derivations and provisional kept/drop/fix rationale are in [static-inventory.md](mutkill-audit/static-inventory.md). Every row is explicitly unexecuted. This report must not be used as a mutation-audit pass or merge approval.

## Per-PR provisional disposition

Counts are test methods, not mutant IDs. “Kept” means provisionally worth retaining if baseline/mutant replay and production-shaped reachability succeed.

| PR / branch suffix | Head | Added methods | Claimed kills | Kept | Fix | Drop | Command evidence |
|---|---|---:|---:|---:|---:|---:|---|
| [#564](https://github.com/mpmdw/JouleWise/pull/564), calib → main | c865d3856d9e1ed691998b7c98ac3c0d2ac1ba1e | 32 | 34 | 20 | 7 | 5 | NOT RUN: no execution environment |
| [#569](https://github.com/mpmdw/JouleWise/pull/569), harvest → main | 5e50e1c4f848c2fa1137c5aad86705cf732ac83c | 10 | 13 | 8 | 2 | 0 | NOT RUN: no execution environment |
| [#566](https://github.com/mpmdw/JouleWise/pull/566), l9 → lane/2026-10-07-l9-analysis | 1a347eb7c21f6a9e7a9961da29865de329b39e5e | 27 | 33 | 21 | 5 | 1 | NOT RUN: no execution environment |
| [#570](https://github.com/mpmdw/JouleWise/pull/570), bytes → lane/2026-10-22-bytes-pass1 | b83f0719cae2b222ed2fe7100f064f325a915788 | 24 | 55 | 21 | 2 | 1 | NOT RUN: no execution environment |
| Total | | 93 | 135 | 70 | 16 | 7 | No pass/fail replay evidence |

The lead compared the complete test-name inventory against fetched PR diffs: calib 32, harvest 10, L9 27, BYTES 24; no missing or invented method names. Changed-file lists contain only 16 new test modules: five calibration, one harvest, eight L9, two BYTES. No changed existing test method was shown in these fetched diffs.

## Findings that need attention

1. **Tests whose targeted change has no identified production output effect.** Calibration test_negative_mean_zero_width_corner_helper (M00589) explicitly states that the public floor is unchanged because another maximum masks the helper. BYTES test_ols_return_widens_both_statistical_endpoints (Ac2c4c25bf7, A7b840b5bc6) pins initial ols endpoint fields that h2 rewrites before consuming them; the other identified ols call consumes coefficients. Both are provisional DROP. The lead read the relevant source, but dynamic public-output identity remains unverified.
2. **Likely calibration duplicates.** New test_exactly_two_launch_lineages_refuse (M01411) repeats the two-full-lineage case already covered by test_absolute_cell_refuses_marker_legacy_or_full_lineage_mix. New test_uncertainty_dominated_cell_keeps_its_label (M01508) repeats the exact floor_conditions assertion in test_zero_scatter_with_nonzero_admissible_width_is_labelled_extraction, which uses real synthetic bundles. Both are provisional DROP pending replay of old and new selectors against the same mutant.
3. **Unreachable or incidental witnesses.** Calibration's inconsistent-session test constructs contradictory fields that the real whole_window session populates from the same bracket value. Its 8192-character progress locator is not a production-shaped filesystem locator. Its fake Process teardown asserts method calls instead of actual process ownership. L9 tests bypass S0 count validation or replace extraction/transport with fabricated closures; the early-1970 epoch test lacks a real L9 consumer witness. Details and fixes are listed per test in the inventory.
4. **Weak numerical oracles.** Harvest's idle-baseline fallback checks only presence and integer shape, so a wrong two-integer interval can pass. Its empty post_request record assertion needs a demonstrated downstream numerical or selection consequence. Calibration's n=16 corner-cap test should assert a derived floor as well as successful admission.
5. **Bars without derivation.** BYTES test_named_primary_coefficients uses absolute 1e-6 for expected-zero rho. A 1e-6 relative fallback does not derive an absolute zero bar. test_positive_resident_effect_is_not_labelled_adds_nothing additionally asserts lower>3 without deriving 3. No tolerance or bar was changed. Most other new arithmetic assertions use exact integers/dyadics, printed precision, or explicitly stated 1e-6 relative fallback; the inventory records the hand arithmetic.

A static DROP is not an empirical “kills nothing” result. No test was executed, so this audit cannot certify either a survivor or a kill. Likewise, naming the same mutant in two complementary protocol cases does not establish that both tests are redundant; the inventory recommends combining those cases and tracing their consuming consequence.

## Commands run with exact tails

The managed environment was selected but never became usable during this session. The initial wait_for_environment call remained pending through repeated waits, then returned a definitive startup failure. The platform notification reported “failed to query executor configuration capabilities” for the selected environment. The final wait returned exactly:

```text
Environment `ccarenv_b64_Y2NhcmVudl9hYWEwZjliNGYyYTg4MTkxYTdkMTA3MjY2YWE2ZmI4ZQ` failed to start: exec-server connection attempt failed: environment unavailable: Environment provisioning failed during container_creation. Cause: snapshot_materialization_failed. Reason: gateway_unavailable.
```

A subsequent environment_status observation was `observed_phase=failed`, `connectivity=offline`, `failure.code=environment_startup_failed`, `failure.message="Environment startup failed. Check the configuration, retry, or contact support."`. These are recorded observations, not an additional root-cause diagnosis. At 2026-10-23 05:20:01 UTC, environment_status reported:

```json
{
  "time": "2026-10-23 05:20:01 UTC",
  "phase": "starting",
  "connectivity": "offline",
  "failure": null,
  "observations_current": true
}
```

The only shell command attempted was `pwd`, with workdir `/workspace`, attempted twice. Neither attempt launched a shell process; both exec_command calls returned exactly:

```text
No usable execution environment is available. Wait for an environment to become available before using this tool.
```

There is no shell exit code or test tail to report. The following requested commands/work were **NOT RUN**: seat_setup; git fetch; git checkout; scratch-copy creation; mutation application; baseline tests; mutant tests; duplicate-selector tests; production-shaped synthetic end-to-end execution; local git commit/push. No test process ran, so no process lacking JW_B5_SYNTHETIC_ONLY=1 or its own existing TMPDIR was started.

Read-only connected GitHub operations did succeed:

- github_fetch_pr for #564/#569/#566/#570 and list_pr_changed_filenames; read the complete new-test diffs and relevant production/existing test sources at the pinned PR heads.
- github_fetch_file for AGENTS.md, targeted RUN_STATE.md sections, TASK_QUEUE.md, AGENT_PLAN.md, Mission M0 in docs/agent_playbook.md, docs/orchestration.md and docs/process/pruning_list_2026-10-14.md. ACTIVE_STOP_CARD=NONE and global work-selection gates=NONE. TASK_QUEUE content was empty in the returned snapshot.
- Lookup of tools/cloud/seat_setup.sh on main and on report-base 7c23ea4b71622f7a898617a66da48868e20562a3 returned HTTP404; the fetched base root directory also has no tools directory. It therefore appears absent on that remote base, but no local startup script could be run.
- environment_diagnostics returned history_status=not_found, records=[], failure detail absent. No secret values were inspected or printed.

Report persistence used the connected GitHub API because shell/Git execution was unavailable. This is disclosed as a substitute, not a claim that the prescribed CLI commands ran. The only remote branch written is report/2026-10-22-mutkill-audit; no PR was opened, no force update was requested, and main and all four draft branches were left unchanged.

- Read current main via GET /repos/mpmdw/JouleWise/branches/main: 7c23ea4b71622f7a898617a66da48868e20562a3.
- Verified the report branch did not exist, then created it from that exact SHA.
- Created .codex-report/mutkill-audit/static-inventory.md with commit message “docs: inventory mutkill tests and provisional audit findings”; resulting remote commit 5a1fec5e8b6070bda57325e3f8bd4d2e75cb5dec.
- Fetched that file back and compared its complete contents: equal; blob bb194a176bb7fd01dcaa60a098f37ad00aa571f9.
- Final report write is this file; its resulting commit SHA and branch-diff verification are reported in the final response/tool record, avoiding a self-referential commit pin.

PR metadata reported main base abd9f1597f7244a23a95e0512655fbee14319032 for calib/harvest, L9 base 730842e05301a90af743873e3356bfa0c5a17181 and BYTES base da27be7b965088b7d2e6697ca48c98512a9b442b. The separately fetched current-main branch response was 7c23ea4b71622f7a898617a66da48868e20562a3. These remote responses are recorded as observed; local fetch/merge-base verification remains outstanding. Test review is pinned to the four explicit head SHAs above.

## Decisions I made

- Preserved all authorized static work through the connected GitHub tools rather than lose it while startup remained pending. The fallback created only report files on the authorized branch.
- Applied the user's exhaustive WRITE_SCOPE over normal repository bookkeeping; RUN_STATE.md, TASK_QUEUE.md, registries, production code and tests were not edited.
- Used four independent reviewers, one per PR, as requested. They performed read-only remote inspection and wrote no local files; the lead owned the final report reconciliation and all remote writes. No scratch trees were created, so there was no shared-tree writer overlap.
- Kept source observations separate from runtime findings. PR-author verification claims, inferred mutant shapes and static duplicate analysis were never promoted to independently executed evidence.
- Treated exact identity/count/printed-precision properties differently from numerical agreement. Flagged unexplained bars without changing them; made no choice about which measured data count or what number the paper prints.
- Deferred production/test fixes because this seat is report-only. No physical check was relaxed and no live hardware or recorded measurement data were accessed.
- Did not request a science ruling for an operational runtime blocker. NEEDS_RULING: none in this report; no data-selection or printed-number choice was made.

## Open work and exact next step

A usable execution environment is required to finish the requested audit. Resume by fetching this report branch and all four test branches; preserve these report commits when checking out the authorized branch. Inspect status and the selected executor's network policy, run setup if it exists on the actual base, compute merge bases, and locate the original solwave5/MUT-* mutation catalogs/mutoverlay.py. Those catalogs were referenced in PR bodies but not supplied by the remotely inspected patches; their local availability could not be checked.

Then, for every inventory row, save each actual one-site production patch in an isolated scratch tree under .codex-report/mutkill-audit/, run the unmodified test and its mutant target with JW_B5_SYNTHETIC_ONLY=1 and a unique existing TMPDIR, record the exact command/exit code/tail and assertion, restore the source, and verify restoration. Use only the audited focused modules; replay the two focused existing extraction selectors to determine redundancy. Add real production-shaped synthetic end-to-end witnesses where mocks currently hide reachability. Resolve all provisional labels and replace this incomplete status only after those results exist.

Only the report inventory/readback checks caught anything this session: complete 93-method coverage, two likely duplicate tests, dead/private-output targets, weak or mocked witnesses, and two unsupported BYTES bars. They did not establish a changed numerical output under any mutant. No claim of “135/135 killed” is made.
