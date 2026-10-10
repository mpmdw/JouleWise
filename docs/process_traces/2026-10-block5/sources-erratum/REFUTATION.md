# Refutation of draft Erratum 2 (Opus 5.5 refuter)

(Returned as the agent's final message on 2026-10-10; written to this file by the magistrate, activation
cbe4230e, without change of substance. The refuter read the draft with SHA-256 `d7a49be8…33e5`.)

**Overall position: ADMIT WITH CORRECTIONS.** The root cause is right and the rule is needed, but two blockers must be fixed in the text before admission and before any arm that relies on it. Do not apply it to BETA attempt 1.

Paths: `REG` = `/Users/edr/code/JouleWise-wt-harvest-sources/configs/campaigns/v5_claim_25g83/registration_block5.md`; `H` = `joulewise/b5/harvest.py`, `WW` = `joulewise/whole_window.py`, `RC` = `scripts/run_campaign.py`, `CP` = `joulewise/campaign_provenance.py`, all in `/Users/edr/code/JouleWise-wt-harvest-sources` at lane head `0b23cf491`.

Executed: `PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_sources` gave 19 tests, OK. Everything else is from reading code; I wrote no file and opened no blinded path. The spare's execution state is taken from `seal2-beta-a1-consult/spare_invoked_count.out` in the records worktree.

## A. Root cause: confirmed, but the trigger is wider than the draft says

The mechanism is what the sealed writer does:
- `RC:7594-7597`: an invoked id with no present directory resolves to `terminal_absent`.
- `RC:8018, 8043-8044`: outside salvage semantics, `elif absent: continue` rejects the whole candidate.
- `RC:8103-8127`: the fallback is the directories that hold a summary, with no roles and `source_manifests=()`.
- `RC:8589-8595`: the empty list is serialized into the row.
- `H:1130-1131`: the harvest returns `source_manifests_unrecorded`.
- On the window: `spare_invoked_count.out` shows BETA attempt 1 with 4 invoked end references, 1 invoked reference absent, exit code 1, and a recorded child refusal. ALPHA attempt 3 of the first seal shows the same.

## Findings

### BLOCKER 1. "Prospective only" is not enforced, and the pin rules would flip BETA attempt 1 whatever the judge rules on J2

- **Claim.** Section 4 says the rule holds "for every attempt armed after this erratum is admitted".
- **Evidence.**
  - `H:5165-5180` (`_neg8_sources`) applies the recovery to any window; there is no arm-time or plan gate anywhere in the diff.
  - `REG:5542-5544` and `analysis_plan_block5.md:80` say an attempt whose recorded harvest commit is not the pinned one is harvested again by the pinned program.
  - `REG:4696-4700` says a re-harvest that makes an attempt claim-usable makes it the analysed attempt if it is the pack's first.
  - Addendum 2 of the seal record scopes its pin only as "for windows of the second seal".
  - So once a third pin lands, the registered rules send BETA attempt 1 through the new program, and attempt 2 becomes "not analysed".
- **Correction.** Add to section 5:
  > "Addendum 2's pin `224a264c5` remains the pin for every attempt armed before this erratum's admission time (ALPHA attempt 1 and BETA attempt 1 of the second seal). The new pin governs only attempts armed after it. No attempt armed before admission is harvested by the new program for a deciding record. The analysis checks each attempt's harvest commit against the pin that governs that attempt."
- Preferably also make the program refuse the recovery when the plan's arm time precedes an admission time passed on the command line, recording the problem `recovery_predates_erratum`.

### BLOCKER 2. The erratum is silent on the claim consumer; a rescued window can be claim-usable and unusable

- **Claim.** "Unchanged … every file a window reads"; a rescued window is simply claim-usable.
- **Evidence.**
  - `WW:6707-6708`: the row validator marks a row with an empty source list `whole_window_verdict_provenance_invalid`.
  - `WW:6553-6580`: on a hazard root the validator also requires `window_membership.membership_id`, which the fallback row lacks (`RC:8577`, `RC:8120-8127`).
  - `WW:7638-7646`: `whole_window_drift_allowances` returns `absent` when no row validates.
  - `REG:1234-1243` assigns to lane L9-NEG8 only the "stored screen failed" case, not a row with no sources and no membership id.
  - `REG:4628-4629`: a pack is never armed again after a claim-usable attempt.
- **Consequence.** A rescued BETA window stops BETA arming and then has no allowance for any floor. GAMMA's contrasts need BETA's floors (`REG:4779-4781`).
- **Why now.** The consumer rule is a rule in its own right (`REG:1216-1233`). Writing it later, once it is known which windows took this path, is the same forking path the draft is trying to avoid.
- **Correction.** Add item 9:
  > "A claim consumer given the harvest archive accepts the row of a window whose `derived/neg8-screen.json` records `rescreen.reference_source.source` = `claim_campaign_manifests_authenticated` by replaying items 1 to 7 in place of the row's source-manifest check and hazard-membership check. The row's evaluation basis must still validate. The allowance is the withheld re-screen bracket's, as for any survivor re-screen. Lane L9-NEG8 implements this before any claim is computed; until then no number of such a window is claimable."

### MAJOR 3. The recovery rescues every route to an empty source list

- **Claim.** Sections 2 and 4 diagnose one cause (an absent invoked member) but trigger "when, and only when" the list is empty.
- **Evidence.** The writer also empties the list when:
  - an id is `ambiguous` (two present directories, or malformed or multiple supersession rows: `RC:7590-7624`, `RC:8019-8021`);
  - an id is `unresolved` (`RC:7598-7601`);
  - a group is `selection_invalid` (`RC:7928-7929`, `RC:7936-7937`);
  - the root is not a hazard root, so null-identity reference manifests are rejected (`RC:7759-7762`, `RC:8022-8023`).
  - `claim_neg8_sources` (`H:1173-1215`) checks none of these. A search of the function for `ordinary_present_bundle_paths`, `is_hazard_runs_root` and the row's membership condition found nothing. It reads `runs_root/<id>` directly (`WW:5260`).
- **Why it matters.** The writer refused those cases on purpose (`RC:8108-8112` distinguishes `…_ambiguous` from `…_unresolved`).
- **Correction.** Add item 1a:
  > "The recovery runs only when all of the following hold; otherwise the re-screen cannot run. (i) The claim runs root carries the hazard lineage locator. (ii) The stored row's conditions include `whole_window_campaign_membership_unresolved` and not `whole_window_campaign_membership_ambiguous`, and the row lists no occurrence refusal reason. (iii) The harvest finds at least one invoked catalog member with no present directory. (iv) Every other invoked member has exactly one present directory by `whole_window.ordinary_present_bundle_paths`. (v) The campaign log holds no occurrence-supersession row."

### MAJOR 4. "Authenticated catalog" is weaker than section 1 defines it

- **Claim.** Section 1: the catalog returns manifests "only if every manifest file there matches exactly one attestation".
- **Evidence.** `CP:1063-1069` and `CP:1015-1016`: a schema-v1 manifest is accepted with no attestation, and a catalog of only v1 manifests never reads the log.
- **Correction.** Add to item 1: "Every catalog manifest must be schema v2; a v1 manifest means the re-screen cannot run." Fix the definition in section 1 to say the attestation applies to v2 only.

### MAJOR 5. Item 7's replacement does not cover what the comparison protected, and one named check does not exist

- **What the comparison protected.** Agreement between the sealed writer and the desk program on which references are read and what their endpoints are. `REG:1108-1113` says a disagreement between their validity predicates "is an exclusion, never a pass". In recovery, only the desk program (which the lane may change) decides (`H:5388-5397`), so that disagreement can now pass.
- **"The window's launch lineage" is not a per-reference check.** Bundle lineage findings are disclose-only (`H:485-493`), are absent from `NEG8_REFERENCE_LOSS_CODES` (`H:124-127`), and `_derived_neg8_decision` checks no lineage on a reference (`WW:4964-5122`).
- **A real substitute exists and the draft ignores it.** The fallback row still carries a sealed-writer evaluation basis: every usable bundle with SHA-256 of its config, metadata and summary (`RC:8130-8149`, `RC:8529-8541`), plus the common launch lineage (`REG:1222-1224`). The harvest has already validated that basis before the recovery starts (`H:1125-1127`, `WW:5881-5961`).
- **Correction.** Replace the last sentence of item 7 with:
  > "In its place: (a) the catalog's all-or-nothing authentication (item 1); (b) every surviving reference must be a member occurrence of the stored row's validated evaluation basis, which binds that bundle's config, metadata and summary by SHA-256 and was written by the sealed program over a set with one launch lineage. A reference that the harvest finds succeeded and valid but that the basis does not list means the re-screen cannot run (`reference_not_in_verdict_basis`). (c) Every catalog reference must be a planned reference or spare of the sealed roster at its slot's position."
- Delete "the window's launch lineage" from the list of per-bundle checks. The code needs the same additions; neither (b) nor (c) is implemented or tested.

### MAJOR 6. Section 3 argues one side only

- **Evidence for the other reading.** The registered outcome rule contradicts the outcome here:
  - `REG:4041-4045`: "a lost reference never removes the window by itself".
  - `REG:4144-4145`: the window is removed only when the re-screen fails or cannot run.
  - `REG:1177-1180`: asserts the writer "never see[s] a reference that has no bundle". That is false for an invoked one (`RC:7594`), so the text misdescribes the sealed code.
- **Evidence that it is still a rule change.** `REG:2906-2907` makes the stored-bracket comparison a registered precondition ("if it does not … nothing is evaluated"), `REG:2895` says the re-screen runs over "the reference bundles the verdict names", and `REG:2916-2917` fails a re-screen that cannot run.
- **My reading.** It is a rule change, because the recovery deletes that precondition.
- **Correction.** Add both sets of citations to section 3, and state: "The registered outcome rule and the registered mechanism disagree in this case; the mechanism is what the pinned program implements, and replacing it deletes the precondition at lines 2906 to 2907, so this is a rule change."

### MAJOR 7. The registered deviation understates its cost on GAMMA

- **Claim.** "The consequence for the screen is only a smaller margin."
- **Evidence.** `REG:4637-4639` puts a lost GAMMA midpoint at (1/37)² ≈ 0.07% because the midpoint has one spare. With a spare that never produces a bundle, one run-time midpoint loss removes the GAMMA attempt (`neg8.midpoint_lost_primary`): 1/37 ≈ 2.7%.
- **Correction.** Add: "On GAMMA a single midpoint lost at run time now removes the attempt (about 2.7% of attempts at the recorded rate, against the registered 0.07%). On every pack a run-time loss is no longer buffered against a second loss found at harvest at the same endpoint."

### MAJOR 8. Section 2 misstates the scope of the defect

- **Claim.** "Every window that loses a reference at run time is removed by this path."
- **Evidence.** Any invoked member with no bundle triggers it, science members included (`RC:7884-7891` adds every invoked member; `sol-fix.md` cites `RC:11220` and `RC:11404` for the generic no-bundle path). Pre-bundle refusals are a registered category (`REG:4727-4729`). The counts on record cover references only.
- **Correction.** Say "any invoked member that leaves no bundle". State that item 4's `bundle_absent` loss applies only to references; an absent science member is handled by the roster as before.

### MINOR 9. Text and implementation disagree

- **Item 3 omits the `invoked` filter.** The code takes only `execution == "invoked"` members (`H:5103`, `WW:4974`). A re-implementer following the text would count `existing` and `blocked_before_invoke` members.
- **Item 8 names the wrong field.** The record is written at `rescreen.reference_source`, as an object `{source, verdict_sources_problem}` (`H:5323-5324`, `H:5441`), not as a top-level word.
- **Stored conditions are discarded without the text saying so.** The recovery clears every stored NEG-8 condition without a "real loss" (`H:4969`, `H:4984-4985`). Addendum 2 states the opposite as the standing rule. Add: "Every NEG-8 condition of the stored bracket is disregarded; the re-derived bracket's conditions decide."
- **An existing word gets a second meaning.** If the catalog fails, the source word becomes `claim_campaign_manifests_unauthenticated`, with a new key `campaign_sources_problem` (`H:5170-5175`). Name both in item 8.
- **The legacy-pair guard overwrites a field.** The override hard-codes `midpoint_lost: False` (`WW:5206-5217`), replacing what the evaluator computed. This affects failed screens only.
- **Untested.** Ambiguous second directory, v1 manifest, non-hazard root, a reference outside the roster, a reference outside the basis.
- **"Byte for byte" rests on synthetic fixtures.** `sol-fix.md` flag F2 says the real rehearsal-copy comparison was not run. Require it before the pin.

### MINOR 10. Pedagogy

- **Used without being defined in section 1:** NEG-8, custody triangle, strict validation, claim runs root, policy digest and registered bracket policy, sentinel position, estimand, endpoints, the clean bound's "corpus cap rule", count-adjusted bound, the "older protocol", launch lineage, loss codes, idle admission, desk code, pin, addendum, seal record, magistrate, activation.
- **Missing why-chain elements:** no worked example and no diagram. A synthetic one in the style of `REG:1244-1264` would do: (3,1,3) planned, one end reference aborted, a spare with no bundle, one start reference lost at harvest, giving (2,1,2) and bound(2,2).
- **Not re-implementable from the text:** items 3 and 7 as written, and the precedence among loss reasons (`REG:1126-1128`).

## J1. Is the rule sound, and is item 7 adequately replaced?

- Sound in direction: same evaluator, same bound, same minimum, and stricter on the legacy pair (`WW:5206`).
- Bound freshness is unchanged: on a hazard root it is judged at the latest surviving end reference's measured end (`WW:5123-5145`).
- Counts cannot inflate through `existing` members or duplicates (`H:1203`, `WW:3886-3897`), and more than three at an endpoint fails in the evaluator.
- Item 7 is not adequately replaced as drafted. It needs corrections 3, 4 and 5.

## J2. BETA attempt 1

- **For applying it.**
  - No decision-maker saw an energy, and the rule reads none.
  - The removal has no physical cause.
  - `REG:4696-4700` contemplates a repaired program changing a completed attempt's `claim_usable`.
  - `REG:4041-4045` states the outcome the rule restores.
  - `REG:4816-4820`: selection on the science outcome is impossible either way.
- **Against.**
  - It is a rule change (finding 6), and `REG:5144` is categorical.
  - The rule's open design choices (trigger breadth, the item 7 substitute, the legacy-pair refusal, the clean-bound requirement) are being settled now with this window's exact structure known: (2,1,2), a derived bound, one absent spare.
  - The saving is smaller than it looks. No agent may run during a window, so the program's gates and a new window are sequential either way.
- **Conclusion.** Not applied. BETA attempt 1 stays `neg8.screen_failed`, kept, disclosed and never analysed; BETA attempt 2 is armed. This needs BLOCKER 1's scoping, or the pin rules apply the rule anyway. A post-release run of the new screen on attempt 1 would be exploratory and labelled so (`REG:4844`).

## J3. Does BETA attempt 1 count toward "same cause twice"?

Yes. The cause key is the family of the window-removing codes, built mechanically (`REG:4711-4722`); the text has no exception by reason within a family. A second NEG-8-family removal sends the next spend to a consult, which is not a cap. Exempting attempt 1 would itself change section 7 for a completed attempt.

## J4. Mechanics

- **A separate pinned document is adequate.**
  - No window input changes.
  - The registration digest in plans is untouched; `REG:4845-4847` shows why its bytes must not change.
  - The harvest's code-identity comparison concerns the measurement checkout only.
  - `check_seal_record.py:119-139` tolerates an additional harvest addendum, and an unfilled pin placeholder.
  - The diff stays inside the files `REG:5524-5526` allows.
- **No re-issue of the seal is needed.**
- **Required additions.**
  - The pin scoping of BLOCKER 1.
  - The release event must also tie the erratum's SHA-256 (`REG:4842-4844` names only three documents).
  - The erratum's digest must be on main before the arm. The `B5-HARVEST-PIN` line comes later, so the addendum is written in two steps.
- **Arm before pin is sound only if the rule text is frozen at admission.** Add: "If the gated program cannot implement this text exactly, the attempt armed under it is judged by pin `224a264c5`; the text is not amended for an armed attempt."

## J5. The spare

- **Registered deviation now; do not fix window code first.**
- **Cost of leaving it, at the registration's 1/37 and with the erratum in force:**
  - An ALPHA or BETA window is lost to run-time losses alone only when two of three references at one endpoint are lost: about 0.4% per window. A working spare would make that about 0.01%.
  - GAMMA: about 2.7% per attempt (finding 7).
  - Over the remaining BETA and GAMMA attempts that is roughly 0.03 to 0.04 expected windows, plus an unquantified term for harvest-found losses.
- **Cost of the fix.** The spare path is collection code that completed windows executed, so the cure supersedes the block and restarts at ALPHA (`REG:4801-4803`). That costs the claim-usable ALPHA window with certainty, plus a re-seal and its audit.
- **Without the erratum** the loss is 1 − (36/37)^7 ≈ 17.5% per window, which is why the erratum should go first.
- **One condition.** Before the next arm, run one more structure-only count that classifies the two recorded child refusals by closed-list reason. It costs no window. "The cause is not established" should not go into a registered deviation when the record already holds it. If the reason is not specific to the spare configs, send it to a consult before arming.

## H. What changes the next arm

- BLOCKER 1 and BLOCKER 2 must be in the admitted text.
- Findings 3 to 5 should be in the text before the arm, because they are rule content and the rule cannot be amended for an armed attempt.
