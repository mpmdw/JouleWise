# Fable 5.1 cold delta pass: block-5 measurement code a434e363d..821b58f8b

Reviewer: Fable 5.1, single foreground session, read-only in every repository. Worktree
`/Users/edr/code/JouleWise-wt-int5`, branch `integrate/2026-10-07-int5`, HEAD confirmed
`821b58f8ba5faa039bd1362f7e11e51686c78373` (`git rev-parse HEAD`). Diff reviewed:
`git diff a434e363d 821b58f8b -- joulewise scripts configs` (56 files, +3976/-367). Rule applied:
`REVIEW_BRIEF_RULE.md` (physics refuses; everything else is a flag), plus `neg8-council/RULING.md`.
Context read: `FROZEN_HEAD_2.md`, `INTEGRATION_TODO.md`, `cold-pass/REPORT.md`.

## Overall verdict: REFUSE (one DEFECT; everything else SOUND or SOUND WITH NOTE)

One input makes the survivors rule drop a whole window on a condition the ruling says it must survive: a
NEG-8 reference whose bundle exists but has no readable `summary_metrics.json` (the SIGKILL-escalated
timeout, a malformed summary, a crash that left undecodable metadata). The verdict writer treats it as a
present reference with no energy (`neg8_bracket_reference_invalid`), not as a lost one, and the harvest's
authenticity re-derivation refuses on the same bundle, so the window carries `neg8.screen_failed`
(EXCLUDE_WINDOW) although two or three survivors stand at every endpoint and the spare already ran. The
fix is small (D1 below) and I would pass the head with it applied; nothing else in the delta needs a round.

No input lets a wrong number into a claim. The pinned estimators are byte-identical. The step order the
ruling demanded (physics joins before the corpus drop and the screen) is in place.

Tests executed here (non-venv `/opt/homebrew/bin/python3.13 -B`, `TMPDIR=/private/tmp/coldpass2`, foreground):

- `tests.hazards.test_refusal_allowlist`: 23 OK, 11 s. `python -m tests.hazards.refusal_census`: clean
  (unlisted, stale, miscounted, guard_changed, scope_gaps all empty).
- `tests.test_neg8_survivors`: 39 OK, 23 s.
- `tests.test_agent_identity`, `tests.hazards.test_arm`: 30 OK, 3 s.
- `tests.test_hazard_whole_window_verdict`, `tests.test_controller_hazard_flags`: 78 OK, 169 s.
- Two probes of my own (scratchpad, outside the repository), results in D1.

No process I started is alive (checked with `ps`; the three `python`/`sleep` processes present belong to
other sessions' suite runners, parents 52062/52295/52499).

## Per-item table

| # | Item | Verdict | Where | Note |
|---|---|---|---|---|
| 5 | Pinned estimators byte-identical | SOUND | blob ids at a434e363d = 821b58f8b = HEAD: `reduce.py` 82449d58, `uncertainty_evidence.py` 202acfcb, `powermetrics_fiducial.py` d1bd5d4b, `adapters/powermetrics.py` 8fa6db3c; `git diff --stat` empty | |
| 1 | Count-adjusted bound and t-term; (3,3) byte replay | SOUND | `whole_window.py:1910-2050` (`neg8_count_adjusted_bound`, `neg8_family_endpoint_bound`); stored terms returned at (3,3) and (1,1); `_family_drift_record` 2087-2106 keeps the old path for `replicated_endpoints_with_midpoint`; test `test_planned_and_legacy_shapes_replay_the_stored_bound_bytes` | |
| 1 | Survivors screen: 2+2, midpoint optional, the two flags | SOUND WITH NOTE | `whole_window.py:2242-2264`, `2271-2283`, `2390-2432`; `harvest.py:4549-4610`, `_neg8_disclose` 4654-4685 | N2, N3 |
| 1 | Harvest step order: joins before the drop and the screen | SOUND | `harvest.py:7325-7328` (`monitor`, `meter`, `neg8_corpus_physics`, `neg8_screen`, then `exclusion_inputs`); `whole_window` only parks the row (`neg8_pending`, 4458-4461) | |
| 1 | Harvest drops physics-flagged references; corpus re-derive | DEFECT (D1); otherwise SOUND WITH NOTE | `_neg8_reference_losses` 4590-4625, `_neg8_rescreen` 4694-4815, `neg8_corpus_physics` 4817-4913; `run_campaign.py:7165-7180`; `whole_window._derived_neg8_decision` 4913-4950 | D1, N1, N9 |
| 1 | Spare-slot retry: chain, plan trees, sizing, `_min_valid` | SOUND | `chain.py:437-470`, `SPARE_RETRY_HELPER` 853-905, `spare_retry_lines` 1245-1308; `reference_spares.py`; `plan.py:769-776`; `size_b5_window.py:338-346`, `416-437`, `579-594`; `driver.py:1381-1398` | |
| 1 | Q: contaminated or lost reference reaching the screen or allowance | SOUND WITH NOTE | the screen: no (D1 aside, the loss map covers the 6.4 codes plus timeout, abort, strict); the allowance: the re-screened allowance lives in `withheld/neg8-rescreen-bracket.json`, the verdict row keeps the stored one | N4 |
| 1 | Q: survivor selection reading energy | SOUND | `_neg8_reference_losses` reads flag codes; `_derived_neg8_decision` reads `status` and `exclude_bundle_ids`; the writer reads `evaluation.status`; the spare helper reads `status`; `neg8_corpus_physics` reads flags. No energy on any of these paths | |
| 1 | Q: exactly (planned - succeeded) spares | SOUND | helper `count`: `min(max(planned - succeeded, 0), max_spares)`; `max_spares == expected_count` for every v5 reference stage; `case` dispatch to the committed set of that size; `horizon_allows` (physics) is the only skip; test `test_the_retry_runs_exactly_planned_minus_succeeded_spares_and_flags_them` | |
| 1 | Q: failed bundles immutable | SOUND | spares run under their own run ids into the same `--runs-dir`; the runner refuses existing bundles; the helper only reads | |
| 2 | A3: arm UNMEASURED = flag except the instrument; census stop removed | SOUND | `hazards/arm.py:191-203` (`refusals`), `UNMEASURED_REFUSES = {"instrument"}` 836, `_refusals` 942-947; `driver.py:800-836` (`normalize_decision`), 1278-1348 (`HazardCensus`, no `STOPPED_CENSUS_UNMEASURED` emitter) | |
| 2 | `normalize_decision`: GO only with instrument PASS and no REFUSE | SOUND | `driver.py:856-863`: `blocking` = REFUSE verdicts or instrument not PASS (UNMEASURED, NOT_EVALUATED, unreadable all count); `decision_go = go is True and not blocking` | |
| 2 | A5 pack-inventory refusal | SOUND WITH NOTE | `driver.py:2347-2349`, `2381-2387`; allowlist NUMBER_INTEGRITY entry present | N6 |
| 2 | A6 desk JSON = flag | SOUND | `reserve_calibration_window_bracket.py:1228-1272`; `_json_object`'s refusal kept on the legacy path only | |
| 2 | `monitor.restarted` | SOUND | `driver.py:902-905`, `941-954` (`on_restart`), `2404-2419` | |
| 2 | Reap identity (item 9) | SOUND | `driver.py:2494-2532` (`_ps_command_matches`: command tail plus start time within 5 s), `2949-2957`; never signals blind; `monitor.orphan_unverified` DISCLOSE | |
| 2 | Item 6: reducer barrier unchanged | SOUND | `environment_admission.py:543-567` (new early return only under the keyword, default False); callers setting True: `run_campaign.py:7093`, `7110`; `whole_window.py:5299`. `reduce.py` byte-identical; `current_environment_refusals` default False | |
| 3 | agent_identity census matcher | SOUND WITH NOTE | `agent_identity.py:269-287` (`is_agent`), `421-466` (`filter_census`: an undecided line is kept) | N5 |
| 3 | Malformed-flag handling, conservative exclusion | SOUND WITH NOTE | `harvest.py:1118-1157`, `6206-6248` (`_malformed_flag_line`, `_candidate_codes`), `_rebuild_unbuilt_flag` 6250-6282 | N7 |
| 3 | Torn-lock reclaim: lsof proof | SOUND | `run_campaign.py:4698-4740`: age >= 30 s, `lsof -t` exit 1 with no output, no LIVE/UNKNOWN registry entry for the root; any probe failure keeps the lock | |
| 3 | `instrument.binary_identity_rederived` | SOUND | `harvest.py:6063-6106`: same boot (casefold) plus digest equality on the recorded path (or `/usr/bin/powermetrics`); a differing or unreadable digest keeps the exclusion | |
| 3 | Battery accumulator under SMC coverage, parity | SOUND | `harvest.py:2817-2866` (`smc_covered=covered`, `covered = not smc_holes` 2576); `hazards/battery.py:973-984` (`smc_covered` from `smc_span_findings` 886); both route sign-inconsistent to `battery.accumulator_unavailable` only with coverage | |
| 3 | Monitor skew bound from the plan | SOUND | `driver.py:663-676` (`_plan_clock_step_ns`), `monitor.py:264-269`, `400`; the harvest uses the same `clock.window_skew_max_ns(clock_step_ns)` (`harvest.py:2976-2977`) | |
| 3 | G10 supervised wait | SOUND | `driver.py:2716-2743` (`_wait_supervised`: 5 s polls, supervision between polls, timeout re-raised as before); allowlist PHYSICS entry | |
| 3 | Model identity superseding | SOUND WITH NOTE | `harvest.py:5509-5536`, `IDENTITY_SUPERSESSION_CHECKS["model_identity"]` 512 | N8 |
| 3 | OS metadata files ignored | SOUND | `harvest.py:1459-1470` (`.DS_Store`, `.localized`, `._*`); applied at 5037, 5076, 7111 | |
| 3 | Bundle->run id mapping in `exclusions.compute` | SOUND | `flags/exclusions.py:151-159`, `202-208`: a member flag scoped by bundle id reaches its member instead of `unmatched` | |
| 4 | A1 `neg8.reference_member_excluded` removed | SOUND | no emitter remains (grep over joulewise, scripts, configs: comments only; `tests/test_harvest_b5_window.py:4593` asserts it is registered nowhere) | |
| 4 | hazard_refusals merges | SOUND | `verdict_absent` one combined NUMBER_INTEGRITY entry; `normalize_decision` PHYSICS guard `e4dded0bf6d10380`; `_wait_supervised` PHYSICS; allowlist test and census pass at 821b58f8b | |
| 4 | Suite fixes 821b58f8b | SOUND | `git show --stat`: three test files only; `PACK_SOURCE_COMMIT` c6309e1a -> 2011ec285 | |

## D1 (DEFECT): a reference with no readable summary is "invalid", not "lost"; the window is excluded

**Where.** `scripts/run_campaign.py:7165-7180` (the writer's loss test), `joulewise/whole_window.py:4913-4950`
(the re-derivation's loss test), `joulewise/b5/harvest.py:4772-4790` (`_neg8_rescreen`'s authenticity pass).

**What the ruling requires.** Registration 0.12 "Lost references": a reference is lost when "its bundle is absent,
its summary status is not `succeeded`, it fails strict validation, or any member-level physics exclusion fires";
decision 5 says the retry "covers admission aborts, timeouts and runtime errors (anything the runner marks failed
by stage end)".

**What the code does.** Both loss tests are `isinstance(status, str) and status != "succeeded"`. A bundle whose
`summary_metrics.json` is absent or unreadable has `status is None`, so:

- The writer appends it to `neg8_references[position]` with `_gross_energy_for(...) = None`
  (`run_campaign.py:7181-7190`); `_endpoint_point_summary` returns None; the bracket records
  `neg8_bracket_reference_invalid`, decision `failed`, no `reference_losses`, protocol
  `replicated_endpoints_with_midpoint`. Probe 1 (fixture members from
  `tests.test_run_campaign.IdleAdmissionCoreVerdictTests`, start r2 with `status=None, summary=None`):
  `decision: failed`, `conditions: ['neg8_bracket_reference_invalid']`, `reference_counts: None`,
  `reference_losses: None`.
- At harvest the member carries `member.timeout` (runner core flag, `run_campaign._hazard_flag_member_timeout`)
  and `member.strict_validation_failed` (`harvest.py:3808-3812`), both in `NEG8_REFERENCE_LOSS_CODES`, so
  `survivors` is true and `_neg8_rescreen` runs. Its first pass `rederive(None)` must succeed for authenticity
  (`harvest.py:4776-4790`). On a custody-bound bundle with no summary `_custody_strict_invalid(bundle_path, None)`
  is True (`custody_telemetry_identity`: `summary_class` None differs from `config_class`; confirmed by probe 2 on
  a bundle whose `metadata.config_sha256` binds its config: `True`), so `_derived_neg8_decision` returns
  `(None, "bundle_strict_invalid")` at `whole_window.py:4949`. Where that check is stubbed (the test fixture), the
  pass yields the same invalid bracket with `claim_families: {}`, and `_neg8_endpoints(stored)` is None, giving
  `rederivation_differs_from_stored_bracket`. Either way `screened = None` and `neg8.screen_failed` is emitted
  (`harvest.py:4580-4587`), EXCLUDE_WINDOW.
- The second pass `rederive(exclude)` would have worked: probe 2 with `exclude={"b5t-neg8-start-2":
  "member.timeout"}` gives protocol `replicated_endpoints`, counts `{start: 2, midpoint: 1, end: 3}`, the loss
  recorded. The machinery handles the case; only the two loss tests and the authenticity pass do not.

**Triggering input.** A window with the start triplet r1, r2, r3. r2's member child ignores SIGTERM at the 1,800 s
cap and is SIGKILLed after the grace (`kill_escalated`), so the controller's `_finalize_interrupted_run` never
runs and the bundle has `metadata.json` and `config.json` but no `summary_metrics.json`. The spare helper counts
r2 as not succeeded (`state()` gives `(False, None)`) and the chain runs `neg8-window-start-spare-1`, which
succeeds. Survivors are (3, 1, 3). Verdict: `neg8_bracket_reference_invalid`, failed. Harvest: `neg8.screen_failed`
with `problems: ["rederivation_failed:bundle_strict_invalid"]`. The window is excluded for a record shape, after
the physics (the hung-process cap) was already handled by the spare. The same path is taken by a malformed
summary (`summary_status` returns `(None, msg)`), by `_hazard_metadata_undecodable` (status None,
`run_campaign.py:2854-2870`), and by a summary without a string `status`. No test covers a summary-less reference
(`tests/test_neg8_survivors.py` writes `{"status": "failed"}` for every failed one).

**Minimal fix (three edits, one new reason string).**

1. `run_campaign.py:7171-7180`: lose a reference when `evaluation.status != "succeeded"` whether or not it is a
   string; reason `"status_not_succeeded"` when it is a string, `"summary_unreadable"` when it is None. (A
   reference whose bundle exists but reads no status has no energy to aggregate; this reads no energy.)
2. `whole_window.py:4915-4939`: in the `survivors` branch, make the reason `excluded[bundle_id]`, else
   `"status_not_succeeded"` if the status is a string other than succeeded, else `"summary_unreadable"` if
   `stored_summary` is not a Mapping or has no string `status`, else None. The `continue` then runs before
   `_custody_strict_invalid`, so the authenticity pass and the exclusion pass agree.
3. `harvest.py` `NEG8_STATUS_LOSS_CODES`: put `"member.timeout"` first and keep the fallback name, so
   `_neg8_lost_rows` names the member flag when the writer's reason is `summary_unreadable`. Add a test: a
   reference bundle with no `summary_metrics.json` in `VerdictWriterSurvivorTests` and in `ReplaySurvivorTests`
   (both passes), expecting protocol `replicated_endpoints`, counts (2, 1, 3) and the loss.

The frozen replay arms are untouched (`survivors = current and point_drift`); the planned (3, 1, 3) bracket keeps
its bytes because no loss is recorded there.

## Notes (no fix round needed; dispositions for the orchestrator)

**N1 (item 1, `harvest.py:4590-4603`).** When `verdict_neg8_sources` fails (a source manifest does not
authenticate, or the claim runs root is unknown), `_neg8_reference_losses` returns `{}` and "the stored screen
then stands". A physics-flagged reference's energy then stays in the stored screen and allowance. The window is
not released silently: `whole_window.verdict_unauthenticated` is in `L5_ONLY_CODES` (not in L4's draft), so it is
UNCLASSIFIED and blocks release until a cold erratum classifies it. When that classification is written it should
be EXCLUDE_WINDOW (the allowlist's `neg8.screen_failed` text already argues "the stored screen then still holds a
contaminated energy"), or `_neg8_reference_losses` should fall back to the roster's reference members (`role`
starting `neg8_daily_reference`) so the loss is still mapped and `neg8.screen_failed` emitted.

**N2 (item 1, `harvest.py:4654-4685`).** For a reference whose bundle is wholly absent, the writer's membership
resolver drops it (`terminal_absent`, `run_campaign.py:8027-8031`), the counts shrink to a survivor shape and the
bracket records no loss. `_neg8_disclose` then emits `neg8.reference_lost` with `lost: []`: the flag says fewer
references than planned but names none. The member carries `member.bytes_missing` (`harvest.py:3765-3767`).
Representation only. Fix when convenient: in `_neg8_lost_rows`, add a row for each roster reference member (by
`role`) absent from the screened members, reason `bundle_absent`.

**N3 (item 1, `whole_window.py:2409-2423`).** With two references absent (not failed) at one endpoint, the writer
sees counts (1, 1, 3) and no `neg8_lost`, so `survivor_shape` and `within_plan_after_losses` are both false: the
condition is `neg8_bracket_ambiguous_reference`, not `references_insufficient`. The window is excluded correctly
(fewer than two survivors); only the reason label differs from the ruling's. Representation.

**N4 (item 1, allowance).** The survivors' allowance (`drift_allowance_j` with bound(n_s, n_e)) exists only in
`withheld/neg8-rescreen-bracket.json`; `whole-window-verdict.json` keeps the writer's bracket, which for a
contamination found at harvest still includes the contaminated reference. L9 (the `exclusions.json` consumer, not
landed) must read the re-screened bracket's allowance when `derived/neg8-screen.json` records a rescreen, never
the verdict row's. Record this as an L9 requirement; not a defect at this head because no claim consumer exists.

**N5 (item 3, `agent_identity.py:281-286`).** Can a real agent be missed? One shape: a script interpreter whose
script token's basename is not an agent name, for example
`node /opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/cli.js -p ...` (the npm install invoked by its real
path rather than through the `claude` symlink): basename `cli.js`, `is_agent` False, the line is ignored although
pgrep listed it. The native binary (`claude/versions/<v>`), the symlink invocation (`node /opt/homebrew/bin/claude`),
`codex.js` and the desktop apps are all matched. Not a number hazard: the monitor measures the agent's CPU over
every member span regardless (`contention.request_overlap`). Fix: in the interpreter rule also match when any
directory component of the script path is `claude`, `claude-code`, `codex`, `@anthropic-ai` or `@openai`. Also
noted: a VS Code extension host whose argv contains `claude` is now ignored where it used to be a hit; the `claude`
child it spawns during a session is still matched, so an idle IDE no longer stops a window. That is the intended
reduction.

**N6 (item 2, `driver.py:2347-2349`).** `inventory_unusable` is decided by `type(error).__name__ ==
"LineagePublicationError" and str(error).startswith("pack inventory is unusable")`: a string match on an error
message. If the message is reworded the refusal silently becomes `records.lineage_formality` and the chain
launches hollow (every tagged member refuses). Fail-open toward launching, no number hazard. Fix: have
`publish_window_lineage` raise a subclass (`PackInventoryUnusableError`) and test the type.

**N7 (item 3, `harvest.py:6220-6232`, `_candidate_codes`).** A torn line salvaged with an empty code prefix
(`"code": "` then the tear) gives `code == ""`, which is not None, so the candidate set is every known code and
`records.malformed_flag_exclusion_possible` (EXCLUDE_WINDOW) fires. The docstring says a line that shows no code
is disclosed only. Needs a tear at exactly that byte of a flag file; rare. One-line fix: treat `code == ""` as no
code (`if not code: return`).

**N8 (item 3, `harvest.py:5509-5536`).** `model_identity` supersession requires every succeeded science member
compared with a pin (`science_complete`); reference and corpus members with a missing identity triple or no pin do
not block it, although their energies feed the bound and the allowance. A reference without a triple still gets
`model.identity_underivable` (EXCLUDE_MEMBER) but that code is not in `NEG8_REFERENCE_LOSS_CODES`, so it stays in
the screen while the arm's `model.identity_unmeasured` is lifted. Fix when convenient: count every succeeded
roster member whose unit has a pin, and add `model.identity_underivable` and `model.identity_mismatch` to the
reference-loss codes (number-integrity losses of the reference).

**N9 (item 1, `harvest.py:4866-4872`).** `neg8_corpus_physics` emits `neg8.bound_not_derived` (EXCLUDE_WINDOW)
when the corpus manifest bytes cannot be re-read (`corpus_manifest_bytes_unavailable`, `corpus_manifest_unreadable`).
The same bytes were read and validated moments earlier in `neg8_bound`, so the trigger is a source changing
mid-harvest, which `records.source_changed_during_harvest` also catches. Acceptable as NUMBER_INTEGRITY (no clean
bound can be built); noted so no one reads it as a physics code.

## Refusals and exclusions I checked against the rule and found in place

- New PHYSICS refusals: `normalize_decision` (REFUSE verdict or non-PASS instrument), the arm dwell and instrument
  finishes relabelled, `_wait_supervised`'s hung-process cap. New NUMBER_INTEGRITY: `night_refused_pack_inventory_unusable`,
  `roster.run_id_mismatch` (EXCLUDE_MEMBER), `records.malformed_flag_exclusion_possible` and
  `_member_exclusion_possible`, `whole_window.verdict_absent` relabelled, the `neg8.screen_failed` and
  `neg8.bound_not_derived` texts extended.
- Flags that used to refuse and now disclose, all correctly: `<module>.arm_unmeasured` (five modules), the in-window
  census unmeasured stop, the desk identity JSON, the campaign start identity without a start time, the torn lock
  (reclaimed with proof), `records.malformed_flag`, `records.operator_log_unreadable`, `records.flag_unbuilt`,
  `instrument.binary_identity_rederived`, `battery.accumulator_unavailable` under SMC coverage, `monitor.restarted`,
  `monitor.orphan_unverified`, `neg8.reference_lost`, `neg8.midpoint_lost`.
- The opposite failure (a physics or number hazard turned into a flag): none found. The instrument's UNMEASURED still
  refuses at arm; charging, AC loss, contention, thermal and clock-step exclusions are unchanged; the reducer's
  environment barrier is unchanged; a differing powermetrics digest still excludes.
