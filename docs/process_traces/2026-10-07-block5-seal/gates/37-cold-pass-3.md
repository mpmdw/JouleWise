# Fable 5.1 cold re-verification (pass 3): int5 821b58f8b..43ac12d0c after the pass-2 REFUSE

Reviewer: Fable 5.1, single foreground session, read-only in every repository. Worktree
`/Users/edr/code/JouleWise-wt-int5`, branch `integrate/2026-10-07-int5`, HEAD confirmed
`43ac12d0ce554813278619b8e8e2331c9eb35be2` (`git rev-parse HEAD`; working tree clean, no `__pycache__` under
`configs`). Diff reviewed: `git diff 821b58f8b 43ac12d0c -- joulewise scripts configs` (9 files, +234/-37) plus the
test-only commit 43ac12d0c. Rule applied: `REVIEW_BRIEF_RULE.md` in both directions. Context: my pass-2 report
(`cold-pass-2/REPORT.md`, REFUSE on D1, notes N1-N9), `FROZEN_HEAD_3.md`.

Interpreter `/opt/homebrew/bin/python3.13 -B` (non-venv), `TMPDIR=/private/tmp/coldpass3`, every run foreground.
Probes written to my scratchpad only (`/private/tmp/claude-501/.../scratchpad/`), never into a repository.

## Overall verdict: PASS WITH NOTES

D1 is fixed on all three paths and the original trigger now ends as the ruling requires. Each note fix is correct;
none adds a non-physics refusal or a wrong-number path. Q11 reads only the roster's pack id and the flag's code. N8
is a correct reference-loss rule, with one scope note for the seal (N-A). The pinned estimators are byte-identical to
a434e363d on disk and in git. No defect; the notes below are dispositions for the orchestrator, not fix rounds.

## Per-item table

| # | Item | Verdict | Where (43ac12d0c) | Evidence |
|---|---|---|---|---|
| 1 | D1 on the verdict writer | SOUND | `scripts/run_campaign.py:7172-7186` | `evaluation.status != "succeeded"` whether or not it is a string; reason `summary_unreadable` when None. Probe 1 (my pass-2 trigger: start r2 `status=None, summary=None`): protocol `replicated_endpoints`, decision passed, counts (2,1,3), loss `[neg8-start-r2: summary_unreadable]`. Was: `neg8_bracket_reference_invalid`, failed, no losses. |
| 1 | D1 on the re-derivation | SOUND | `joulewise/whole_window.py:4933-4969` | Loss test (`excluded` > `summary_unreadable` if status not a string > `status_not_succeeded`) runs before `_custody_strict_invalid` (4970). Probe 2: authenticity pass `problem=None`, (2,1,3), loss `summary_unreadable`; exclusion pass `problem=None`, loss `member.timeout`. `probe_custody`: the real `_custody_strict_invalid(start-2, None)` still returns True, and the pass still yields `problem=None`, so the ordering is what fixed it. |
| 1 | D1 on the harvest | SOUND | `joulewise/b5/harvest.py:4608-4617`, `4724-4726`, `97-99` (`NEG8_STATUS_LOSS_CODES`, timeout first) | The writer already dropped the reference, so `new_losses` is empty, no re-screen is needed and `_neg8_lost_rows` names `member.timeout`. `tests/test_neg8_survivors.py::HarvestSurvivorTests::test_a_sigkilled_reference_with_no_summary_is_lost_and_the_window_kept` runs the real harvest with the real custody check on the summary-less bundle: with the spare succeeded (3,1,3), without (2,1,3), no `neg8.screen_failed` in either. My shapes probe through the writer: D1 + succeeded spare gives (3,1,3) passed with the loss recorded; two unreadable at one endpoint with no spare gives `references_insufficient`, failed. |
| 1 | D1 precondition: real summaries carry a string status | SOUND | `joulewise/schemas.py:1834-1836` (`status` required, enum) | On disk: `g2a-large-p1024-r01` and `example-mac-mlx-local__r1` read `'succeeded'`; the real NEG-8 reference bundles `p2015-neg8-reference-start/end` read `'succeeded'`. The frozen replay arm is untouched (`continue` at 4932 precedes the status read). |
| 2 | N1: losses mapped when sources do not authenticate | SOUND | `harvest.py:4671-4681`, `856-875` | Fallback names references only (never an energy, never a passing screen); `neg8_reference_source` recorded in the flag. Not a new refusal in practice: such a window already carries `whole_window.verdict_unauthenticated`; the fallback adds `neg8.screen_failed` only when a loss flag hits a named reference (the stored screen then holds a contaminated energy: NUMBER_INTEGRITY). Tests `..._mapped_when_the_verdict_sources_do_not_authenticate`, `..._no_loss_flag_leave_the_stored_screen`. |
| 2 | N2: absent reference named | SOUND (representation) | `harvest.py:1638-1662` (`neg8_slot`), `4733-4747` | The new `build_roster` loop keys `members` by the same manifest rows the existing loop at 1611-1619 already keys on, so no new raise exposure. `derived/roster.json` is written (7138) and compared with no sealed digest, so the roster shape change cannot refuse. Tests `..._wholly_absent_reference_is_named_by_the_roster`, `SpareRosterAndYieldTests::test_the_harvest_roster_marks_each_planned_reference_with_its_slot`. |
| 2 | N3: never-run references read `references_insufficient` | SOUND | `whole_window.py:2392-2405`, `2424-2427`, `2443`; `run_campaign.py:7228-7236` | Shapes probe through the real writer: (3,1,3) and (1,0,1) keep their protocol and record no survivor fields; (0,1,0), (0,0,3), (3,0,0), (1,1,1), (1,1,3) all end `references_insufficient`, failed, none raises; (2,0,2) evaluated, passed. `within_plan_after_losses` for a full (3,1,3) now true but only feeds `ambiguous` and `reference_shape_valid`, both already true. Tests `test_the_planned_shape_keeps_its_historical_bytes`, `test_a_full_trajectory_keeps_the_historical_bracket`, `test_planned_and_legacy_shapes_replay_the_stored_bound_bytes`. |
| 2 | N5: npm package path is an agent | SOUND | `joulewise/agent_identity.py:60-62`, `121-134` | Exact directory-part match (`claude-code`; `@anthropic-ai/claude*`; `@openai/codex*`); `PurePosixPath` imported (51). Wider only by the real install path; a false hit needs those exact directory names in a node script path. Test `test_an_agent_package_script_run_by_its_real_path_is_an_agent`. |
| 2 | N6: typed A5 exception | SOUND | `joulewise/window_lineage.py:204-209`, `961`; `joulewise/b5/driver.py:2214-2217` | Type test, no message match. Allowlist row retyped NUMBER_INTEGRITY with the same guard `119167ca70e14e48` (not BASELINE, as the rule requires). Tests `test_b5_driver_p2.py:383,402`, `test_window_lineage.py:838`. |
| 2 | N7: empty salvaged prefix names no code | SOUND | `harvest.py:6316`, `6335` | `if not code` in both places; `records.malformed_flag` (DISCLOSE) still emitted. |
| 3 | Q11: GAMMA `neg8.midpoint_lost_primary` | SOUND | `joulewise/flags/exclusions.py:152-153`, `220-223` | `compute` reads `roster["pack_id"]` and `flag["code"]` only, inside the DISCLOSE branch. `pack_id` is `pack_root.name` (`harvest.py:1736`), passed at 3544; the GAMMA pack directory is `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` = `GAMMA_PACK_ID`. `first_claim_usable` (417-435) passes over a `claim_usable: False` attempt. Allowlist `window_exclusions` entry present. Tests `test_the_rule_is_registered_for_gamma_only`, `test_gamma_with_a_lost_midpoint_is_not_claim_usable_and_a_later_clean_attempt_is_analysed`, `test_a_foreign_attempts_flag_does_not_exclude_gamma`. |
| 4 | N8: identity codes are reference losses | SOUND WITH NOTE | `harvest.py:97-99`; `model_identity` step 7409 before `neg8_screen` 7418; emitters 5604, 5614 | Both codes fire only on succeeded members (5592) from the member's own config and metadata; a mismatch needs a pin for the member's unit (5608-5614), so no false mismatch on an unpinned auxiliary. The real reference bundles on disk derive an identity (`derive_model_runtime_config_from_metadata` on `p2015-neg8-reference-start/end`: OK), so N8 does not drop real references wholesale. NUMBER_INTEGRITY by the rule's text ("model that differs from the sealed one"; a number that cannot be attributed). Note N-A on scope. Tests `test_a_reference_of_another_model_is_dropped_and_named`, `test_two_references_of_another_model_at_one_endpoint_fail_as_references_insufficient`. |
| 4 | Manifest ruling: `agent_identity.py` in `MANIFEST_PATHS` | SOUND | `joulewise/quiet_predicate_campaign.py:68`, `133-135` | `manifest_for` records each listed file's digest per plan; a record, not a gate. `test_night_kinds` 15 OK, `test_gen_evidence_night` 10 OK, `test_quiet_predicate_campaign` 167 OK (4 skipped). |
| 5 | Pinned estimators byte-identical to a434e363d | SOUND | blob ids at a434e363d = on-disk `git hash-object`: `reduce.py` 82449d58, `uncertainty_evidence.py` 202acfcb, `powermetrics_fiducial.py` d1bd5d4b, `adapters/powermetrics.py` 8fa6db3c | `git diff a434e363d 43ac12d0c` empty for all four. |
| - | Suite fixes 43ac12d0c | SOUND | three test files, +20/-6 | Synthetic reference summaries given `"status": "succeeded"` as the reducer writes; `test_hazard_neg8_mint_verdicts` patches `_read_json_object` to return a summary with status. No assertion weakened: the removed lines are the fixtures' old shapes and the N6 exception type. `tests/hazards/refusal_baseline_frozen.txt` untouched. |
| - | Rule check by hand (shapes the test cannot see) | SOUND | `whole_window.py:4969` (`continue`), `harvest.py:4742` (`continue`), `856-875` (`return`/`continue`) | 4969 is the loss the ruling requires and mirrors the writer; 4742 is representation; the fallback's early returns only shrink an unauthenticated name list. No new call to a raising function in an admission or selection path. `test_refusal_allowlist` 23 OK; `refusal_census` clean (unlisted, stale, miscounted, guard_changed, scope_gaps all empty). |

## Tests executed here

| Module | Result |
|---|---|
| `tests.test_neg8_survivors` | 52 OK, 33 s |
| `tests.hazards.test_refusal_allowlist`; `python -m tests.hazards.refusal_census` | 23 OK; clean |
| `tests.flags.test_flags_exclusions` | 31 OK |
| `tests.test_agent_identity`; `tests.hazards.test_arm` | 8 OK; 23 OK |
| `tests.test_window_lineage` | 48 OK |
| `tests.test_whole_window_selection` | 57 OK |
| `tests.test_hazard_neg8_mint_verdicts` | 14 OK |
| `tests.test_night_kinds` | 15 OK |
| `tests.test_harvest_b5_window` | 176 OK, 478 s |
| `tests.test_b5_driver_p2` | 46 OK |
| `tests.test_hazard_whole_window_verdict` | 20 OK |
| `tests.test_controller_hazard_flags` | 58 OK, 160 s |
| `tests.test_run_campaign.IdleAdmissionCoreVerdictTests` | 77 OK |
| `tests.test_aggregate` | 28 OK |
| `tests.test_quiet_predicate_campaign` | 167 OK (4 skipped) |
| `tests.test_gen_evidence_night` | 10 OK |

About 900 tests plus the census. Four probes of my own (the two pass-2 probes rerun unchanged, a writer shapes probe,
an N8 harness probe), results quoted above and in N-A.

No process I started is alive (`ps`: the `-B` interpreters I launched have all exited; the `unittest` processes
present belong to other sessions' shard runners, started without `-B` or with `-v`, and were not touched).
`/private/tmp/coldpass3` was removed at the end (it held only the harvest suite's 68 MB template cache).

## Notes (dispositions for the orchestrator; no fix round)

**N-A (item 4, N8 scope versus the catalog).** The N8 ruling says a mismatched reference "is dropped, and the
survivors rule decides". For `model.identity_mismatch` that outcome is pre-empted: the code's effect is
EXCLUDE_WINDOW in `DRAFT_CODES` and in the harvest fixture catalog, and `exclusions.compute` applies EXCLUDE_WINDOW at
any scope level (`exclusions.py:224-226`, before the member-level branch), so the window is excluded by the
reference's own flag whatever the survivors screen says. Confirmed through the real harness (the N8 test's window):
with `model.identity_mismatch` on `b5t-neg8-end-3`, `neg8.screen_failed` is absent (the survivors pass) but
`exclusions()["reasons"]` contains `model.identity_mismatch` and `claim_usable` is False. The N8 test asserts only on
`neg8.screen_failed`, so it does not see this. Direction is conservative and the classification predates this delta,
so it is not a defect here. For the ruling's outcome to obtain, the L6 seal must give `model.identity_mismatch` a
member-scoped effect for auxiliary members (the science members' identities are checked by the same step; a
reference running another model does not make a science member's number wrong), or the ruling should be reworded to
say the window is excluded. A cold-gate catalog question for the seal, not code. Also noted: `model.identity_underivable`
is one of the 46 harvest codes absent from `DRAFT_CODES` (UNCLASSIFIED under the draft; EXCLUDE_MEMBER in the fixture),
so under the draft a window with an underivable reference is release-blocked until the seal classifies it; the N8
loss mapping is unaffected (it reads the flag code, not the effect).

**N-B (item 2, N1 and `whole_window.verdict_unauthenticated`).** Still absent from `DRAFT_CODES` (UNCLASSIFIED;
DISCLOSE in the fixture), as in pass-2 N1. N1 makes the contaminated case safe (EXCLUDE_WINDOW through
`neg8.screen_failed`); the clean case leaves the stored screen standing on an unauthenticated row. The seal's
classification of this code decides whether that clean case is DISCLOSE or EXCLUDE_WINDOW; N1 removed the only path
where DISCLOSE would have released a contaminated energy.

**N-C (item 1, `summary_unreadable` without a member flag).** A reference whose summary is malformed with no timeout
or abort flag is lost for a record cause and named `summary_unreadable` (`_neg8_lost_rows` falls back to the writer's
reason). No other disposition is possible: the reference has no energy to aggregate. It removes a window only when
fewer than two survive at an endpoint, and then no NEG-8 screen can exist (NUMBER_INTEGRITY). Disposition: as is.

## Refusals and exclusions checked against the rule in this delta

- New window reasons: `neg8.midpoint_lost_primary` (GAMMA only, NUMBER_INTEGRITY, allowlisted). New refusals: none;
  the A5 raise is the same site retyped (NUMBER_INTEGRITY, same guard).
- Conditions that stopped refusing: a summary-less reference no longer fails the authenticity re-derivation
  (`bundle_strict_invalid`) or the writer's bracket; never-run references no longer read
  `neg8_bracket_ambiguous_reference`.
- The opposite failure (a physics or number hazard turned into a flag): none. The loss codes still include every 6.4
  physics exclusion, timeout, abort and strict failure; the count-adjusted bound, the harvest step order (physics joins
  before the corpus drop and the screen) and the pinned estimators are unchanged from pass 2.
