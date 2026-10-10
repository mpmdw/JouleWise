# Block 5, Erratum 2 (prospective): where the harvest takes a window's reference list from when the stored verdict records none

Drafted by the magistrate (activation cbe4230e, Opus 5.5) on 2026-10-10 and admitted with corrections the same
day by a cold gate under registration section 10 (one judge, Fable 5.1: `RULING.md` beside this file; one
refuter, Opus 5.5: `REFUTATION.md`). Sections 4 and 5 are the judge's admitted text, copied from section D of
the ruling without change; sections 1 to 3 are the draft's with the corrections the ruling orders. The first
draft is kept as `ERRATUM-draft1.md`. Structure only: no energy, power or duration, no member's name. Line
numbers of the registration are those of the sealed file of the second seal
(`configs/campaigns/v5_claim_25g83/registration_block5.md`, sha256 `c7b3fdf7…db3f`); code line numbers are
those of the pinned harvest program's commit `224a264c5faaae90cdf56118df37e773a932700b`, which contains
the sealed tree.

## 1. The terms this erratum uses

- **Reference.** A short run of one fixed small workload. Each window runs three at its start, one at its
  midpoint and three at its end. If the machine's energy cost of that fixed workload changed between
  start and end by more than a bound, the window drifted and is removed.
- **Bound.** The largest start-to-end change that noise alone explains, computed from the spread of the
  window's own corpus (18 further runs of the same workload at the window's start; the deciding bound
  uses the first 12 clean ones and needs at least 10).
- **Screen.** The comparison of the references' start-to-end change with the bound. It needs at least 2
  usable references at the start and 2 at the end; with 2 instead of 3 the bound is widened by a
  registered formula for the smaller count (registration 0.12, near line 1172).
- **Spare.** One extra reference, a byte copy of a stage's first reference under its own run id. After a
  reference stage in which a reference did not succeed, the chain runs the stage's spare once.
- **Campaign manifest.** Each stage of a window is one invocation of the campaign runner. The runner
  writes one manifest file per invocation into the runs root's `campaign_manifests/` directory, listing
  the members it handled and how (`invoked`, `existing`, `blocked_before_invoke`), and appends to the
  runs root's campaign log one attestation of that file's exact bytes.
- **Authenticated catalog.** The function `campaign_provenance.load_authenticated_campaign_catalog`
  (`joulewise/campaign_provenance.py`, near line 1040). For manifests of schema version 2, which is what
  the block-5 runner writes, it returns the manifests of a runs root only if every manifest file there
  matches exactly one attestation in the campaign log for its current bytes; if any one does not, it
  returns nothing. It accepts a manifest of the older schema version 1 with no attestation at all, which
  is why item 1 of the rule below admits schema version 2 only.
- **NEG-8.** The project's name for this drift check; codes that begin `neg8.` belong to it.
- **Claim runs root.** The directory that holds the bundles (one directory of recorded files per run) of a
  window's references and science runs, with its `campaign_manifests/` directory and its campaign log.
- **Strict validation and the custody triangle.** Two checks the harvest makes on a bundle before it reads
  an energy from it. Strict validation: the bundle's recorded files are complete and consistent under the
  current schema. The custody triangle: the bundle's `config.json`, `metadata.json` and summary name the
  same instrument, and the config is the registered one (registration near lines 1100 to 1103).
- **Loss codes.** The closed list of flag codes that make the harvest drop a reference
  (`harvest.NEG8_REFERENCE_LOSS_CODES`): a competing process, a battery or thermal event, a clock step
  inside the reference's measured span, and the validity codes of registration 6.3.
- **Pin, addendum, seal record.** The seal record is the document that names each sealed file by its
  SHA-256. An addendum is a section added to it later. A pin is one line of an addendum that names the one
  commit of the harvest program that may produce a deciding harvest.
- **Verdict writer and stored verdict.** After the window, the harvest starts the measurement clone's own
  sealed program (`scripts/run_campaign.py --whole-window-verdict`), which writes
  `whole-window-verdict.json` into the claim runs root. That file lists the manifests it was written from
  (`row_provenance.source_campaign_manifests`, each a path and a SHA-256) and holds its own result of the
  screen (the stored bracket).
- **Re-screen.** The harvest does not trust the stored bracket. On every window whose bound was derived
  it runs the screen again itself, over "the reference bundles the verdict names" (registration near
  lines 2892 to 2917), after dropping every reference that was lost: one that did not succeed, failed
  validation, or overlapped a physical disturbance found at the harvest. "The re-screen alone decides",
  and "a re-screen that cannot run leaves it failed" (line 2915).

## 2. What happened

BETA attempt 1 of the second seal (`v5-b5-beta-a1-20261010T0742Z`) ran its whole chain. One end reference
was aborted at idle admission at run time, so the chain ran the end spare. The spare's child process
refused within about ten seconds and left no bundle; the runner recorded the spare in its manifest as
`invoked`, with exit code 1. At the harvest one start reference was dropped for a competing process that
overlapped its request. The references that remain usable are 2 at the start, 1 at the midpoint and 2 at
the end: a shape the registered screen is defined for. The bound was derived and validated.

The harvest nevertheless removed the window with `neg8.screen_failed`, and the screen was never
evaluated. The chain of causes, each step proved from the code by a Sol 6.1 seat
(`/Users/edr/night-archive/b5-consults/beta-a1/fix/sol-fix.md`) and each fact on the window proved by a
count program that prints closed-list words and integers only (`seal2-beta-a1-consult.md`):

1. All 10 manifests of the runs root authenticate (9 stages and the spare invocation). Authentication
   checks a manifest's bytes against the log; it does not require an invoked member's bundle to exist.
2. The sealed verdict writer, when it resolves the window's members from the manifests, treats an
   `invoked` member with no bundle as `terminal_absent`, and on a block-5 runs root one such member makes
   it reject the manifests as its source altogether (`scripts/run_campaign.py` near lines 7580, 7884,
   8018). It falls back to the bundle directories that have summaries, which carry no roles, and writes
   an empty source list (near 8106 and 8590).
3. With no roles the writer finds no references, so the stored bracket is "missing" with no claim family.
4. The harvest's source selection returns `source_manifests_unrecorded` when the verdict's source list is
   empty (`joulewise/b5/harvest.py` near line 1127), and the re-screen does not run.

The same count on the first seal's ALPHA attempt 3, the only other window in which a spare ran, shows the
same thing: one invoked spare, no bundle, exit code 1, a recorded child refusal. So on the evidence so
far the spare never produces a bundle in a live window (2 of 2), and a window that loses a reference at
run time, and whose spare then runs and leaves no bundle, is removed by this path whatever its physics.
The writer's rule is not about references only: any `invoked` member that leaves no bundle, a science run
included, empties the source list the same way (`scripts/run_campaign.py` near lines 7884 to 7891 and
8043 to 8044). The registration's own estimate of that loss is 1
member in 37 (line 4638); with 7 references a window, roughly one window in six from references alone.

## 3. What the sealed text says, and why this is an erratum and not a program repair

The registration states an outcome and a mechanism, and in this case they disagree.

*The outcome rule.* "A lost reference never removes the window by itself" (lines 4041 to 4045); the window
is removed only when the re-screen fails or cannot run (lines 4144 to 4145). BETA attempt 1 lost two
references, kept enough at both endpoints, and was removed.

*The mechanism.* The re-screen runs over "the reference bundles the verdict names" (line 2895). It must
first reproduce the stored bracket's endpoints and estimand, and "if it does not … nothing is evaluated"
(lines 2906 to 2907). "A re-screen that cannot run leaves it failed" (lines 2916 to 2917). The passage near
lines 4053 to 4062 covers the neighbouring case, a verdict whose sources do not authenticate: there the
harvest reads the campaign manifests "as written (… unauthenticated, used only to name references, never
for an energy or a passing screen)". Nowhere does the text tell the harvest to take the reference list from
the authenticated catalog when the verdict records no sources. The passage at lines 1177 to 1180 says that
the two functions that evaluate the screen never see a reference that has no bundle; that is accurate
about those two functions and silent about the step before them, where the writer discards the manifests.

The mechanism is what the pinned harvest program implements. Replacing it removes the precondition at
lines 2906 to 2907, so this is a change of rule, not a repair of a program that departed from the text:
registration section 10, a prospective cold erratum. The fix seat, the refuter and the judge all read it
that way.

## 4. The change

**Terms used below.** The *stored verdict* is the one row of `whole-window-verdict.json` that the measurement clone's verdict writer writes into the claim runs root after the window. Its *source list* is the field `row_provenance.source_campaign_manifests`. The *catalog* is the set of campaign manifest files under the claim runs root's `campaign_manifests/`; it is *authenticated* when `campaign_provenance.load_authenticated_campaign_catalog(runs_root, runs_root / "campaign_log.jsonl")` returns a list: every manifest parses to a known schema, and every schema-v2 manifest's current bytes match exactly one writer attestation in the campaign log (a schema-v1 manifest is accepted by that function without any attestation, which item 1 forbids here). A *hazard root* is a runs root that carries the launch-lineage locator file `.joulewise-launch-lineage.json`, which every block-5 claim runs root does. The *evaluation basis* is the part of the stored verdict that binds it to its inputs: for each member the writer counted usable, the bundle path and the SHA-256 of its `config.json`, `metadata.json` and `summary_metrics.json`, plus the policy digest, the calibration pair, the drift bound and the launch lineage (`whole_window.build_evaluation_basis`). The *roster* is the sealed plan tree's list of planned members, in which each planned reference carries `neg8_slot` and each spare `spare_slot` (`harvest.build_roster`). The *clean bound* is the deciding drift bound of §5.3 as amended on 2026-10-09: built from the first 12 corpus members in committed order that are in the validated in-window bound and carry no physics code, at least 10. *Cannot run* means: the re-screen is not evaluated, the screen is failed, `neg8.screen_failed` removes the window, `rescreen.evaluated` is false and `rescreen.problems` names the reason, exactly as a re-screen that cannot run is treated today (REG 2915 to 2917).

**Rule, added to §0.12 ("Who applies the loss test" and "The screen on the survivors") and to §6.5 (`neg8.screen_failed`), for every attempt whose plan's `t0_epoch_s` is later than the admission time of section 5.** When the stored verdict's source list is absent or empty, the harvest takes the window's reference list from the authenticated catalog of the claim runs root and re-screens on it, under items 0 to 9. For every other verdict nothing changes.

0. **Trigger.** The recovery is attempted when, and only when, all six hold. (a) The source list of the stored verdict is absent or an empty list (the pinned program's problem `source_manifests_unrecorded`, H 1129 to 1131). (b) The claim runs root is a hazard root (`window_lineage.is_hazard_runs_root`). (c) The stored verdict records the writer's membership condition `whole_window_campaign_membership_unresolved`, does not record `whole_window_campaign_membership_ambiguous`, and records no occurrence refusal reason (RC 8108 to 8127 writes these). (d) At least one `invoked` member of the catalog has no bundle directory (no path from `whole_window.ordinary_present_bundle_paths(runs_root, bundle_id)`). (e) Every other `invoked` member of the catalog has exactly one bundle directory by the same function. (f) The campaign log holds no occurrence-supersession row. When (a) holds and any of (b) to (f) fails, the re-screen cannot run and `campaign_sources_problem` names the first failed condition in this order with one closed word: `runs_root_not_hazard`, `membership_condition_not_unresolved`, `no_absent_invoked_member`, `invoked_member_ambiguous`, `occurrence_supersession_present`. When (a) does not hold, the recovery is never entered, whatever else is true.

1. **The catalog must authenticate, completely and at schema v2.** `load_authenticated_campaign_catalog` must return a non-empty list, and every manifest in it must have `schema_version` v2. Failures, each "cannot run": the function returns nothing, `source_manifest_unauthenticated`; it returns an empty list, `source_manifests_unrecorded`; any manifest is schema v1, `source_manifest_schema_v1`.

2. **Policy and member checks, the same as for recorded sources.** The stored verdict's `campaign_policy.sha256` must be a registered bracket policy (`whole_window._registered_bracket_policy`); every manifest's `campaign_policy.sha256` must equal it; every manifest path must be `campaign_manifests/<name>` inside the runs root by `whole_window._safe_source_path`; every member bundle id must be a safe path inside the runs root; no bundle id may appear in two manifests or twice in one. Failures, each "cannot run": `policy_unregistered`, `source_manifest_policy_differs`, `source_manifest_path_invalid`, `source_manifest_members_invalid`.

3. **Which members are references.** A reference is a catalog member with `execution` equal to `invoked` whose `role` and `sentinel_position` resolve to `start`, `midpoint` or `end` by `whole_window._neg8_position`. Members with `existing` or `blocked_before_invoke` execution are not references and never enter a count. A spare carries its slot's role and position (`joulewise/b5/reference_spares.py`), so it is a reference of that endpoint. Every reference so found must be a planned reference or a spare of the sealed roster at the same slot (`neg8_slot` or `spare_slot` equal to its position); a reference that is not, "cannot run" with `reference_not_in_roster`. A member whose role and position disagree or resolve to none of the three positions is `neg8_bracket_reference_invalid` as today (REG 4125 to 4127, cause (c)), and the screen is failed.

4. **Losses: the rules of today and one more.** A reference is lost when its summary status is not `succeeded`; its summary cannot be read; it fails strict validation or the custody triangle; its energy cannot be read (`energy_unreadable`); or it carries one of the harvest's reference loss codes (`harvest.NEG8_REFERENCE_LOSS_CODES`, H 124 to 127), named in the precedence of REG 1125 to 1128. In addition, a reference with no bundle directory at `runs_root / <bundle id>` is lost with reason `bundle_absent`; it carries no other reason, because no flag can be computed for a bundle that does not exist. `bundle_absent` as a reference loss applies to references only; an absent science member is handled by the roster exactly as before this erratum. A lost reference's energy is never read, in either family.

5. **The clean bound is required.** The recovery runs only with the clean bound. Without it, "cannot run" with `clean_bound_unavailable`; the collected-subset bound and the stored bracket's bound are never used on this path.

6. **The registered evaluator decides, on the survivors, with the count-adjusted bound.** The harvest calls `whole_window._derived_neg8_decision` with `point_drift=True`, `current=True`, the clean bound as `drift_bound_artifact`, every loss of item 4 as `exclude_bundle_ids`, `unreadable_energy="lost"`, and `require_replicated_endpoints=True`; the evaluator is `whole_window.evaluate_neg8_point_drift` with bound(n_s, n_e) of §0.12. Accepted shapes: 2 or 3 surviving references at each endpoint and 0 or 1 at the midpoint. The outcome when the shape fails: fewer than 2 survivors at either endpoint gives `decision` `failed`, condition `neg8_bracket_reference_invalid`, `survivor_screen` `references_insufficient`, `reference_counts` the realised counts by slot, `planned_reference_counts` {start 3, midpoint 1, end 3}, `reference_losses` the losses of item 4, and `midpoint_lost` true exactly when no midpoint survives; more references than planned at any slot gives `failed` with `neg8_bracket_reference_invalid` as today; the legacy single pair (one start, one end, no midpoint, no loss recorded) is never accepted on this path. The outcome when the statistic exceeds the bound in either family is the family's condition (`neg8_bracket_abs_delta_exceeded`, `neg8_bracket_idle_sub_abs_delta_exceeded`) and `failed`, as today. The bound's freshness is judged as today (WW 5123 to 5145). A `failed` decision is `neg8.screen_failed`; a `passed` decision with no problem is a survivor re-screen that decides alone, and `derived/neg8-allowance.json` records `survivor_rescreen` with the withheld bracket's digest, exactly as for any survivor re-screen.

7. **The stored-bracket comparison cannot be made; three checks stand in its place, and the stored bracket decides nothing.** For recorded sources the harvest first re-derives the bracket without its own losses and requires the stored bracket's endpoints and estimand (REG 2906 to 2907); here the stored bracket is `missing` and has no endpoints. In its place: (a) item 1's all-or-nothing authentication; (b) the stored verdict's evaluation basis must validate (`whole_window._validated_evaluation_basis`; a verdict that carries a basis that does not validate is `evaluation_basis_invalid`, "cannot run", as today at H 1125 to 1127), and every *surviving* reference must be a `member_occurrences` entry of that basis whose `config_sha256`, `metadata_sha256` and `summary_sha256` equal fresh SHA-256s of the bundle's three files; a surviving reference that the basis does not list, or whose hashes differ, is "cannot run" with `reference_not_in_verdict_basis`; a lost reference need not be in the basis; (c) item 3's roster check. Every NEG-8 condition of the stored bracket (`neg8_bracket_missing`, `neg8_bracket_reference_invalid` and any other) is disregarded on this path; the re-derived bracket's conditions decide. No per-reference launch-lineage check is made or claimed; the common launch lineage is bound through the basis.

8. **Disclosure.** `derived/neg8-screen.json` records, under `rescreen.reference_source`, the object `{"source": "claim_campaign_manifests_authenticated", "verdict_sources_problem": "source_manifests_unrecorded"}` when the recovery ran, and `{"source": "claim_campaign_manifests_unauthenticated", "verdict_sources_problem": "source_manifests_unrecorded", "campaign_sources_problem": <the closed word of items 0 to 7>}` when it could not run; `rescreen.problems` carries the same word. A `neg8.screen_failed` flag emitted on this path carries the same object in `observed.reference_source`. `derived/neg8-allowance.json` carries the same object under `reference_source` beside its `source` field. The release's attempt table marks every window whose screen was decided on this path, reading `rescreen.reference_source.source`. No flag code is added or removed; `neg8.reference_lost` (DISCLOSE) fires as today whenever the realised counts are below (3, 1, 3), and its `observed.lost` names an absent spare with reason `bundle_absent` and its stage's retry as "spares measured 0, succeeded 0".

9. **The claim consumer.** A claim consumer given the harvest archive accepts the stored verdict row of a window whose `derived/neg8-screen.json` records `rescreen.reference_source.source` `claim_campaign_manifests_authenticated`, `rescreen.evaluated` true and `rescreen.decision` `passed`, by replaying items 0 to 7 in place of the row's source-manifest check (WW 6707 to 6708) and hazard-membership check (WW 6553 to 6580). The row's evaluation basis must still validate. The allowance is the withheld re-screen bracket's, through `whole_window.harvest_neg8_allowance_bracket`, as for any survivor re-screen; any mismatch gives no allowance, never the stored bracket. Lane L9-NEG8 implements this before any claim is computed (analysis plan §11); until it lands, no number of such a window is claimable, as is already true of every window released by a survivor re-screen (REG 1241 to 1243).

**Unchanged.** Every threshold; the bound and its formula; the endpoint minimum of 2; the corpus rule and the clean bound; the flag catalog and every code's effect (no code added or removed); the roster; the blinding rules; every file a window reads; the verdict writer; the measurement clone, the claim head and the seal commit. A verdict that records sources is handled exactly as before (gate: byte-identical derived output and equal flags against pin `224a264c5` on the real rehearsal copy and on the lane's fixtures). A verdict whose recorded sources do not authenticate is handled exactly as before (REG 4053 to 4062: manifests read as written, unauthenticated, the re-screen cannot run).

**Why it cannot let a drifting window pass.** The recovery changes only where the list of references comes from. The list is authenticated by the same function and the same log the writer uses (item 1), bound to the writer's own usable set (item 7b) and to the sealed roster (item 3); each reference meets the same loss rules (item 4); the screen is the same evaluator with the same bound and the same minimum (items 5 and 6). A window with fewer than 2 survivors at an endpoint, with a start-to-end change above the bound, with a manifest that does not authenticate, with a surviving reference the writer did not count usable, or without a clean bound is removed exactly as before.

**Registered deviation, added to the list in §10 as item 10.** In a live window the reference spare has left no bundle in 2 of 2 invocations (the first seal's ALPHA attempt 3 and the second seal's BETA attempt 1), each recorded `invoked` with exit code 1 and a child refusal whose recorded reason is not one of the nine closed-list reason codes the structural count recognises (`D/seal2-beta-a1-consult/spare_invoked_count.out`, `spare_refusal_reason.out`). No planned reference and no science member of those windows, or of the second seal's ALPHA attempt 1, was refused in that way, so the refusal is specific to the spare invocation (its own config directory and `--max-failures k`, §0.12); the cause is window code and is not changed here. Until a change to window code under §7.5, a reference lost at run time is therefore not replaced, and the passages describing a succeeding spare (REG 997 to 1003 and 1151 to 1170) describe the design, not the observed behaviour. What this costs, at the registered loss rate of 1 member in 37: on ALPHA and BETA a window is removed by run-time losses alone when two of its three references at one endpoint are lost, about 0.4% of windows (about 0.01% with a working spare), and a run-time loss is no longer buffered against a second loss found at harvest at the same endpoint; on GAMMA a single midpoint lost at run time removes the attempt through `neg8.midpoint_lost_primary`, about 2.7% of attempts against the registered 0.07% (REG 4637 to 4640).

**Worked example (synthetic; the shape of BETA attempt 1, no energies).** Planned (3, 1, 3). At run time one end reference is aborted at idle admission (its bundle exists with status `failed`), the chain runs the end spare, the spare's child refuses and leaves no bundle; the runner's tenth manifest records the spare `invoked`. The writer resolves the spare `terminal_absent`, rejects all ten manifests as its source, falls back to the directories that hold a summary, writes an empty source list and a `missing` bracket. At harvest one start reference overlaps a contender (`contention.request_overlap`). Item 0: (a) empty list, (b) hazard root, (c) `..._unresolved` recorded, (d) one absent invoked member (the spare), (e) every other invoked member has one directory, (f) no supersession row: the recovery is attempted. Items 1 and 2: ten v2 manifests authenticate, one policy, no duplicate id. Item 3: 3 + 1 + 4 references, each in the roster at its slot. Item 4: lost are the aborted end reference (`member.admission_aborted`), the spare (`bundle_absent`) and the contended start reference (`contention.request_overlap`). Item 5: the clean bound exists. Item 6: survivors (2, 1, 2), an accepted shape; bound(2, 2) decides. Item 7: the basis validates and lists the five survivors with matching hashes. Had a second end reference been lost, the shape would be (2, 1, 1): `failed`, `references_insufficient`, `midpoint_lost` false, and the window removed.

## 5. Mechanics

- **A separate document; the registration's bytes are not edited.** The registration digest every plan carries stays `c7b3fdf7…db3f`; no window input changes.
- **Addendum 3 to the seal record, written in two steps.** *Step 1, before the arm of any attempt this erratum governs:* the erratum's path and the SHA-256 of its admitted text as committed on main; the line `ERRATUM-2-ADMITTED-AT: <UTC time, ISO 8601>`, which is no earlier than that main commit's committer time and earlier than the next attempt's t0; and the pin-scoping paragraph below. *Step 2, before any governed attempt is harvested:* a `B5-HARVEST-PIN:` line with the implementing program's commit, its files and their SHA-256s, and the path of its gate record (an independent executing review, the module and the whole suite, CI, a cold Fable 5.1 pass, the real rehearsal-copy before/after comparison).
- **Pin scoping.** An attempt is *governed* by this erratum when its plan's `t0_epoch_s` is later than `ERRATUM-2-ADMITTED-AT`. Addendum 2's pin `224a264c5` remains the pin for every attempt that is not governed, which includes ALPHA attempt 1 and BETA attempt 1 of the second seal; the new pin governs only governed attempts. No attempt that is not governed is harvested by the new program for a deciding record; a run of the new program over such an attempt, if ever made after the release event, is exploratory, labelled so (REG 4844), and changes no verdict, `claim_usable`, cause key or attempt history. The analysis checks each attempt's recorded harvest commit against the pin that governs that attempt (analysis plan §2.2, applied per attempt).
- **Program gate.** The implementing program carries `ERRATUM-2-ADMITTED-AT` as a constant and refuses the recovery when the window plan's `t0_epoch_s` is not later than it: "cannot run" with `campaign_sources_problem` `recovery_predates_erratum`. The constant is checked against the addendum by the gates.
- **Arm before pin.** A governed attempt may be armed as soon as step 1 is on main. The admitted text is frozen at admission and is not amended for an armed attempt. The gated program is not run over a governed attempt's bytes before step 2 exists. If the gates find, from code and text alone, that no program can implement this text exactly, the attempt armed under it is harvested by pin `224a264c5` and judged under the sealed rule; a corrected erratum governs later attempts.
- **Release event.** The release event ties this erratum's SHA-256 beside those of the registration, the analysis plan and the catalog (REG 4842 to 4844).
- **BETA attempt 1** stays `neg8.screen_failed`, collected, not claim-usable, kept and disclosed, its energies never analysed; it counts toward §7.3's cause key for BETA.

## 6. Admission and implementation status

Admitted with corrections on 2026-10-10 (`RULING.md`, last line `RULING: ADMIT-WITH-CORRECTIONS`). In sections
4 and 5, `REG` is the sealed registration, `H` is `joulewise/b5/harvest.py`, `WW` is `joulewise/whole_window.py`,
`RC` is `scripts/run_campaign.py` and `CP` is `joulewise/campaign_provenance.py`, at lane head `0b23cf491`; `D`
is `docs/process_traces/2026-10-block5`. The admission time of section 5 is written in Addendum 3 of the seal
record: `ERRATUM-2-ADMITTED-AT: 2026-10-10T16:30:00Z`.

The judge's rulings on the draft's five questions: the rule is sound with the corrections; it is not applied to
BETA attempt 1, which stays removed and counts toward the cause key; a separate pinned document is enough and the
seal is not re-issued; the spare stays a registered deviation.

The judge's statement of what the implementation lacked at admission, copied unchanged:

**What the present diff (`224a264c5..0b23cf491`) does not yet implement, to be built and gated before step 2:** item 0 conditions (b) to (f) and their closed words; item 1's schema-v2 requirement and `source_manifest_schema_v1`; item 3's roster check and `reference_not_in_roster`; item 7(b)'s basis-membership check and `reference_not_in_verdict_basis`; item 6's `midpoint_lost` as the realised value (the diff hard-codes false, WW 5206 to 5217); item 8's `reference_source` in `derived/neg8-allowance.json`; the program gate constant and `recovery_predates_erratum`; and tests for each, plus the untested cases the refuter lists (an ambiguous second directory, a v1 manifest, a non-hazard root, a reference outside the roster, a reference outside the basis). Item 9 is lane L9-NEG8's, before any claim is computed, not this pin's. Already implemented: item 0(a), items 1 (except v2), 2, 3 (except the roster check), 4, 5, 6 (except `midpoint_lost`), 7(a), 8 (screen record and `observed`), and the byte-identity of recorded-source handling on fixtures.
