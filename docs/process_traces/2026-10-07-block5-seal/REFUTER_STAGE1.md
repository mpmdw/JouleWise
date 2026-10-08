REFUTER V5-CLAIM-25G83-B5: BREAK FOUND — 5 finding(s); worst: one NEG-8 reference whose energy cannot be read (for example its clock anchor is not `bounded`) is not treated as lost, fails the whole drift screen and removes a clean window (RF-1)
ON THE RULING: PENDING (replaced when section 6 is written)

Stage 1 of two. The output path is set by the dispatch note `STAGE1_DISPATCH.md`, which overrides the charge's
`REFUTER.md`. Attacked: revision 9 of the four documents and the code at commit `9b0c680ed`. Probe scripts are kept in
`/private/tmp/sealgate-refuter/probes/` (`p1` to `p12`); each finding names the one that produced its evidence.

## 1. Contamination disclosure

Written at 2026-10-07 16:16 PDT, after reading only the charge (`SEAL_GATE_CHARGE_REFUTER.md`) and the dispatch note
(`STAGE1_DISPATCH.md`), and before opening any other file. Completed at the end of the session (last part).

**(a) What was in my context when the charge arrived and that the charge did not supply.** I am a subagent session
(model: Opus 5.5) started by an orchestrator session through an agent harness. The harness injected the following
before my first action. I did not open them; I cannot un-see them.

1. `/Users/edr/.claude/CLAUDE.md` (the owner's global rules): a list of orchestration skill names and a writing
   standard for explainer prose (first-use test, why-chain, replication bar).
2. `/Users/edr/code/JouleWise/CLAUDE.md` (project notes): how the Codex bridge and MCP routes are configured. Nothing
   about block 5, the registration or the catalog.
3. `/Users/edr/code/JouleWise/CLAUDE.local.md` (the owner's private orchestration doctrine). This is the material
   contamination. It contains the team layout (Opus 5.5 orchestrates, Sol 6.1 is the default implementation seat,
   Fable 5.1 gives cold final passes), the gate list ("one refuter on a claim-path ruling; a disagreement settles in
   one erratum, not a chain"), and a section "Physics refuses; everything else is a flag (Ed, 2026-10-05)" with seven
   numbered items. That section is a longer, differently worded form of the paragraph the charge pastes in its
   section 4. Items in it that the charge does not state: arming refuses only on six named hazards measured directly;
   a contending process is one "above 5% CPU"; block 4 folds into block 5; a refusal path with no catch in three
   sessions is removed; "a lens or cold-pass finding that is only about representation is dispositioned 'flag, not
   refuse'"; owner-reserved steps are agent-run; and "Old rules don't bind the science". The charge's order 6 forbids
   reading any `CLAUDE*.md`; these three were injected, not opened.
4. A memory index (`MEMORY.md`, about 120 one-line entries; I opened none of the files it links). Lines that bear on
   this gate: "Checkpoint 2026-10-07 seal prep PAUSED ... int5 fe28e5a0c verified; reg rev 9 draft; nothing armed";
   "PR bodies can break blindness"; "Paper threat = hallucination, not forgery ... recompute every printed number";
   "Check the physics, not the proxy"; "Local whole-suite method ... NON-VENV homebrew python3.13"; "Attribution
   limit ... ~1 J"; "Threat-model prune (D-161)"; "No git fetch in canonical while armed".
5. A git status snapshot of `/Users/edr/code/JouleWise` (branch `main`, one untracked backup file) and its five most
   recent commit subjects (merge of pull request #484, a watchdog fix series). I did not open that pull request.
6. The owner's notification e-mail address, a list of tools and skills, and the names of deferred tools (mail,
   calendar, browser, computer use). I used none of them.
7. The list of agent types the harness offers. Order 2 forbids subagents; I started none.
8. A harness instruction to keep scratch files in its own session directory. The charge names
   `/private/tmp/sealgate-refuter/` and requires a path without `claude` in it; I followed the charge.

**(b) Whether this session, or anything I can see of earlier sessions, took part in writing, reviewing or auditing
the four documents or the code.** This session did not: its first action was reading the charge. I have no memory of
any earlier session. The memory index shows that earlier sessions of the same model family (Opus 5.5, as orchestrator
and as seats) wrote and reviewed this material, and the charge itself was written by an Opus 5.5 seat. I share their
weights and blind spots and none of their context beyond the lines quoted above.

**(c) What I already believed about this project that did not come from the charge.** From items 3 and 4: that the
owner regards most non-physical gates as over-engineering; that the instrument is described as attribution-limited at
about 1 J; that the machine is dedicated; that a head called int5 (`fe28e5a0c`) was verified before this stage. I
held no belief about any measured energy of any window, and I have seen no block-5 number, because none exists.

**Bias I name.** Item 3 pushes toward filing fewer findings of kind B2 and toward reading exclusions as suspect. The
charge's doctrine binds in both directions; of my five findings four are B1 and one is B2, so a reader should weigh
whether I under-hunted B2. Section 4 lists the B2 places I tried.

**Files read that section 6 of the charge does not list, and why.**

- `wave-1007b/seal-gate/STAGE1_DISPATCH.md`: the caller named it; it fills the markers.
- `wave-1007b/seal-gate/QUESTIONS.md`, lines 135 to 160 only (section 6, the pins table), as the dispatch directs. A
  `grep` for headings also showed me that file's eight section titles. I read nothing else of it.
- `wave-1007b/reg-fidelity/ORCHESTRATOR_RULINGS.md` in full and `REG_FIDELITY.md` in part (its heading list, entries
  A11 to A18 and all of List C), as the dispatch directs, so as not to rediscover known corrections.
- `cold-pass-2/REPORT.md` lines 8 to 20 and 76 to 96, `neg8-council/RULING.md` lines 24 to 41 (both are in the
  charge's section 6), read after I had formed RF-1 and RF-3, to see whether they were already known.
- Under `rehearsal-real/` (in the charge's section 6): the three `archive/derived/window_flags.json`, the
  contention, battery and NEG-8 flag records of `alpha-1` and `gamma-2` `archive/derived/flags.jsonl`, and the first
  lines of `alpha-1.console.log` and `alpha-1/rig.log`. All structure; no energy.
- **One read I should not have made.** The first 1,500 bytes of `rehearsal-real/alpha-1/overrides.jsonl`. It is not
  on the charge's banned list by name, but it holds what the banned `dry-arm.json` files hold: a census capture with
  another session's shell command line (a mock rehearsal of three packs run in parallel). It held no energy and
  nothing of the judge's. I stopped there. It told me only that the machine was busy during that rehearsal, which I
  use in RF-5 to say that the rehearsal's contention counts are not a rate.
- The directory listing of `/Users/edr/night-archive/gate-prune/` and of `seal-gate/` (names, sizes and times only).
  The second showed that `RULING_STAGE1.md` existed from 16:20; I did not open it before section 5 was written.
- Repository files beyond the charge's list, as the hunt directed: `joulewise/reduce.py`, `joulewise/flags/core.py`,
  `joulewise/flags/schema.py`, `joulewise/hazards/contention.py`, `joulewise/detection_floor.py`,
  `tests/test_harvest_b5_window.py`, `tests/fixtures/b5_harvest/README.md`.

## 2. Trust anchors

Session start 2026-10-07 16:16:04 PDT. Findings complete 16:45 PDT. No command ran longer than 50 s. Every probe ran
in the foreground with `/opt/homebrew/bin/python3.13 -B` from the worktree root with
`TMPDIR=/private/tmp/sealgate-refuter/tmp`. `git status --short` in the worktree was empty after the last probe.

Run in `/Users/edr/code/JouleWise-wt-seal-refuter`:

| What | Output | Equals the dispatch value |
|---|---|---|
| `git rev-parse HEAD` | `9b0c680ed79d5c7b72b4b39ed04b9fe51dd116d4` | yes |
| `git status --short` | no output | yes |
| `git merge-base --is-ancestor 9b0c680ed… HEAD; echo $?` | `0` | yes |
| registration | `12ac5c78876f09e7b7611ed7de91c4ba70048e6381169143d7a98e5ed41b1eef` | yes |
| analysis plan | `9f0ad06bfdab1bb2c1f153802084be1347bc9a2e3f9397f1d4bda37665c60154` | yes |
| flag catalog | `2b1595e488d1f52c9e10e7971f95e3d335bf34ab4f19bc5a75fdd97f93f21810` | yes |
| sealed inventory (stub) | `39433d47d6c80fc6f8360ff9afd18c6b118894ed675eddebd303353f421add9c` | yes |
| the 15 other files of `QUESTIONS.md` section 6 (`identity_pins.json`, `sizing_b5.json`, three plan trees, panel, policy, acceptance, three prefill-pin files, runbook, `hazard_refusals.json`, `agent_identity.py`, `exclusions.py`) | each recomputed with `shasum -a 256` | all 15 equal the table |

No anchor mismatched. No `FILL[…]` of the charge was left unfilled by the dispatch note except those it assigns to
stage 2.

## 3. Findings

Five findings of severity BREAK, most serious first, then notes. Terms are those of the charge's section 5.

### RF-1. B1. BREAK. A reference whose energy cannot be read fails the whole drift screen

**Where.** Registration §0.12 "Lost references" (line 535) lists what makes a reference lost; §6.5 (line 2412) says
"a lost reference never removes the window by itself"; §6.3 (line 2162) and §0.14 (line 731) say a member whose clock
anchor is not `bounded` is removed as one member. Code: `scripts/run_campaign.py` lines 6714 to 6744
(`_gross_energy_for`) and 7170 to 7209; `joulewise/whole_window.py` lines 4098 to 4130 and `evaluate_neg8_point_drift`;
`joulewise/reduce.py` lines 1805 and 3576 to 3604; `joulewise/b5/harvest.py` line 97 (`NEG8_REFERENCE_LOSS_CODES`).

**What a "not bounded" anchor is.** Each member's power records are placed on the machine's clock by a per-member
timing fit. The fit is `bounded` when the sampler stream is at least 60 s long and the fit's timing error is at most
5 ms (registration §0.14). When it is not, the reducer gives the member's energies no error envelope.

**Smallest input.** A window with all seven references measured and succeeded. One end reference's timing fit is not
`bounded`. Nothing else is wrong and the true drift is half the bound.

**What the documents say happens.** Nothing in §0.12 covers it: the reference has a bundle, status `succeeded`, a
readable summary, passes the strict check, has no §6.4 physics flag and the right model. So it is not lost. A science
member in the same state costs one unit (`member.anchor_not_bounded`).

**What does happen.** The verdict writer reads the reference's energy through `_gross_energy_for`, which returns
`None` when the summary has no envelope for `/gross_energy_j` (its comment: "A point without its admitted set cannot
establish drift stability and therefore refuses downstream"). The writer appends that `None` to the endpoint's
values; the evaluator then fails the whole screen. The replay path reads the same reference through
`_reference_energy_evidence`, which returns the problem `provenance` because the reducer stamps
`clock_anchor_unresolved` on the request prechecks.

- `p11_gross.py`: `_gross_energy_for` on a summary with the envelope returns the point; on a summary without it
  returns `None`; with a collection-integrity flag returns `None`.
- `p10_refnone.py`, the repository's `evaluate_neg8_point_drift` with the fixture's bound: all seven read gives
  conditions `['neg8_drift_bound_stale']` (the fixture passes no freshness record, so this one condition is in every
  row); end reference 3 handed over as `None` gives `['neg8_bracket_reference_invalid', 'neg8_drift_bound_stale']`;
  the same reference treated as lost gives `['neg8_drift_bound_stale']`, `reference_counts {'start': 3, 'midpoint':
  1, 'end': 2}`, `survivor_screen 'evaluated'`. The midpoint behaves the same way: handed over as `None` it adds
  `neg8_bracket_reference_invalid`, although §0.12 says the screen does not need the midpoint.
- `p9_refprecheck.py`, the replay evaluator `_derived_neg8_decision`: with one end reference aborted it returns a
  bracket with `reference_losses [('b5t-neg8-end-3', 'status_not_succeeded')]` and the harvest keeps the window
  (`neg8.screen_failed=False`, `neg8.reference_lost=True`); with the same reference succeeded but its energy evidence
  returning `provenance` it returns `problem='provenance'` and no bracket.
- `tests.test_harvest_b5_window.Neg8ScreenTests.test_every_neg8_condition_fails_the_screen` (ran, OK) holds that any
  such condition in the stored row becomes `neg8.screen_failed` (EXCLUDE_WINDOW).
- `p10` also prints that `member.anchor_not_bounded` is not in `NEG8_REFERENCE_LOSS_CODES`, so the harvest's
  survivors re-screen is not triggered.

Read, not executed: that a real bundle with a not-`bounded` fit carries no envelope (`reduce.py` line 1805 returns
the unresolved context for any status other than `bounded`; lines 3579 to 3581 compute envelopes only when the
context is resolved). The same lines make a reference unresolved when its calibration attachment is missing, stale
or mismatched. A real bundle in that state would settle it; I did not build one.

**At stake.** One whole window per occurrence, by a per-member event that the documents price at one unit. It is the
fourth member of one defect class: "one lost reference removes the window" (triple audit, Opus F1), "a reference
with no readable summary" (cold pass 2, D1), "a strict-invalid reference" (Sol delta audit A5), and now "a valid
reference with no readable energy". The documents give no rate for a not-`bounded` fit; they report block 3's
largest timing half-width as 3.598 ms against the 5 ms limit, and they register an END STATE rule for the case that
most fits are not bounded, so they expect the event. Any of 7 references (or a spare standing in) can carry it.

**This is fidelity item A14.** The fidelity sweep's A14 records that `neg8_bracket_reference_invalid` has a cause
"(b) a required start, end or present midpoint reference whose gross energy is not a finite, positive point", and the
orchestrator disposed of it as "text to the fact". The dispatch asks whether any such item should be a change to
code. This one should: writing the fact registers the exclusion of a clean window.

**Cure. Code, and it touches files that execute during a window.** In the writer's loop
(`run_campaign._idle_admission_core_evaluation`, the branch at line 7200) a reference whose `_gross_energy_for` or
`_idle_subtracted_energy_for` is `None` goes to `neg8_lost` with reason `energy_unreadable`, like the
`strict_invalid` branch above it. `whole_window._derived_neg8_decision` drops it the same way in the replay, and the
harvest maps it to a loss. `scripts/run_campaign.py` and `joulewise/whole_window.py` are in the sealed inventory and
are imported during a window, so by registration §7.5's definition (by file) this cannot be done by an erratum after
the seal. It lands before H_claim, or the seal-landing ruling must say that the verdict writer (a desk step,
`chain.DESK_KINDS`) is not collection code and assign it to lane L9-NEG8. Text to add to §0.12 "Lost references",
after the `summary_unreadable` clause: "its energy cannot be read although it succeeded and passed the strict check
(reason `energy_unreadable`: the reducer gave its request energy no envelope, as when its clock anchor is not
`bounded`, §0.14, or its calibration attachment does not verify);". If the code is not changed, the text must say:
"A reference that succeeded but whose energy cannot be read is not lost; it fails the screen and the window is
removed", and §6.5's "a lost reference never removes the window by itself" must carry that exception.

### RF-2. B1. BREAK. Lost midpoint: the pack that is removed is the one that still has interior references

**Where.** Registration §0.12 "A lost midpoint" (lines 627 to 635: "Because the midpoint is the only reference inside
the window, its loss leaves any excursion that reverts by the end unmeasured"), §0.16, §7.2, §14 Q11; analysis plan
§2.4 ("The midpoint is the only reference inside the window"; "*Scope.* Only GAMMA is affected"); allowlist entry
`neg8.midpoint_lost_primary` ("...a drift allowance with no interior-excursion evidence..."); code
`exclusions.PACK_SCOPED_WINDOW_REASONS`.

**Smallest input.** A window in which every member is clean and the only flag is `neg8.midpoint_lost`.

**What happens** (`p2_excl.py`, the exclusion function on the three real rosters with the sealed catalog):
ALPHA `claim_usable=True reasons=[]`; BETA the same; GAMMA `claim_usable=False
reasons=['neg8.midpoint_lost_primary']`.

**Why the premise is false on GAMMA.** The same probe prints the rosters' roles. GAMMA holds two more references
inside the window, `decode_midpoint_reference` and `prefill_midpoint_reference`; ALPHA and BETA hold none.
`p12_sg13.py` prints GAMMA's stage order from its plan tree: `gamma-reference-start` (3), science 20,
`gamma-reference-decode-midpoint` (1), science 20, `gamma-reference-arm-boundary` (1), science 20,
`gamma-reference-prefill-midpoint` (1), science 20, `gamma-reference-end` (3). Registration §0.12 line 503 says each
of the two is "the midpoint reference's config under its own run id". So when GAMMA loses its arm-boundary
midpoint, two measurements of the same workload inside the window remain, after science members 20 and 60. On ALPHA
and BETA nothing remains. The rule removes the window where interior evidence survives and keeps it where none does.

**The floor packs are affected too.** Analysis plan §4 step 4 puts half the allowance into every reported cell's
bound B (`E_whole_window_drift_allowance_j`), and §2.4's own forcing problem says that without the midpoint "the
allowance can only shrink". So "Only GAMMA is affected" contradicts §4 step 4: on ALPHA or BETA a lost midpoint can
understate B for the four paper cells, and that window is kept. Arithmetic on the registration's second example
(bound 0.40 J, start mean 20.10, end mean 20.35, midpoint 19.90): allowance 0.45 J with the midpoint, 0.40 J
without; each member carries 0.225 J against 0.200 J.

**At stake.** One GAMMA window per occurrence. The registered rate, (1/37)² ≈ 0.07%, counts only the case where the
midpoint and its spare both fail at run time; a physics flag found at harvest loses the midpoint with no spare, and
the text says "the block has no rate yet" for that. With RF-1 uncured, a midpoint with an unreadable energy removes
the window on every pack anyway.

**Cure (two consistent choices; the present text is neither).**

- *Keep the window.* Catalog and text only on the claim side, plus one deletion in desk code: delete GAMMA's entry
  from `exclusions.PACK_SCOPED_WINDOW_REASONS` and its allowlist entry (`joulewise/flags/exclusions.py` runs only at
  harvest), and register in analysis plan §7.1 step 5 that the analysis code of lane L9, not yet written, computes
  GAMMA's spread over the start mean, the end mean, the midpoint if it survived and each surviving interior
  reference. Replacement for the §0.12 sentence: "On ALPHA and BETA the midpoint is the only reference inside the
  window. GAMMA has two more, after science members 20 and 60; when its arm-boundary midpoint is lost, the spread of
  its contrasts' allowance is taken over the start mean, the end mean and the surviving interior references, and the
  attempt stays claim-usable. A GAMMA attempt that lost the midpoint and both interior references is not
  claim-usable (`neg8.midpoint_lost_primary`)."
- *Keep the rule.* Then correct the premise in §0.12, plan §2.4 and the allowlist entry (GAMMA keeps two interior
  references; the rule discards them), strike "Only GAMMA is affected", and state that a lost midpoint on ALPHA or
  BETA can understate the bound B of that pack's reported cells and is nevertheless only disclosed.

### RF-3. B1. BREAK. A damaged flag line removes the window for a code that only the harvest can emit

**Where.** Registration §6.2, lines 2124 to 2136, including its worked example: "a line torn after
`{"code": "calibration.capt` could have been `calibration.capture_invalid` (EXCLUDE_WINDOW) among seven candidates,
so the window is removed". Code: `harvest._malformed_flag_line`, `_candidate_codes`.

**Smallest input.** The controller writes its DISCLOSE flag `calibration.capture_battery_pair_unverified`
(registration §6.10, first table row) and the line is cut inside the code.

**What happens.** `p5_torn.py` runs the harvest on a synthetic window with the sealed catalog's effects (the
fixture's two documented deviations kept: `cell_unit_minimum` 1 and `member.cooldown_evidence_unverified`
DISCLOSE). The whole line (652 bytes, sealed effect DISCLOSE) adds no reason and is absorbed. The same line cut after
`"code":"calibration.capt` adds the reason `records.malformed_flag_exclusion_possible`, with `candidate_count 7` and
`excluding ['calibration.capture_battery_pair_failed', 'calibration.capture_battery_span',
'calibration.capture_battery_unmeasured', 'calibration.capture_invalid']`. Of the line's 650 cut positions, 33 remove
the window and 617 only disclose.

**Why no number is protected.** `p3_emitters.py` lists, for each of the catalog's 32 EXCLUDE_WINDOW codes, the files
under `joulewise/` and `scripts/` in which the literal occurs. For 22 of them it is `joulewise/b5/harvest.py` alone
(`cell.below_minimum`: `exclusions.py` alone; `instrument.precal_screen_failed`: none). All eleven `calibration.*`
codes are among the 22. The harvest reads flag files written before it started; it does not read its own flags from
disk, and it derives these codes again from the preserved bytes whatever any flag file says. So a damaged line cannot
have been one of them. The codes a program can write before the harvest are eight:
`code.executed_differs_from_sealed`, `code.identity_unmeasured`, `lineage.plan_tree_digest_differs`,
`model.identity_mismatch`, `model.identity_unmeasured`, `model.identity_unpinned`, `pack.identity_mismatch`,
`pack.identity_unmeasured`.

**At stake.** One window per occurrence, on a record defect, which the doctrine answers with "flag, not refuse". The
rate is low: it needs a writer that died inside a line, a full disk, or a marker line on a member's error output that
was interleaved or cut (those lines travel through a pipe, and a flag line here is longer than the 512 bytes a pipe
writes atomically on macOS). I give no number.

**Cure. Text now; harvest code before ALPHA-1's harvest (the harvest does not run during a window).** Replacement
for the rule sentence of §6.2: "…and lists every code it could have been among the codes that a program writing
flag files before the harvest can emit (`harvest.PRE_HARVEST_EXCLUDING_CODES`, held equal to those writers' code
tables by a test). A code that only the harvest emits is never a candidate: the harvest derives it again from the
preserved bytes, so a damaged line cannot have lost it." Replacement for the worked example: "a line torn after
`{"code": "calibration.capt` could only have been the controller's `calibration.capture_battery_pair_unverified`
(DISCLOSE): the four window-removing codes with that prefix are emitted by the harvest alone, so the line is
disclosed and removes nothing. A line torn after `{"code": "model.identity_m` could have been the arm collector's
`model.identity_mismatch` (EXCLUDE_WINDOW), so the window is removed."

### RF-4. B1. BREAK. `cell.below_minimum`: 8 of 10 removes clean windows for precision, and its rate rests on one cause

**Where.** Registration §6.6 (lines 2476 to 2488); catalog `rules.cell_unit_minimum` 8; `cell.below_minimum`
(EXCLUDE_WINDOW); allowlist entry.

**Smallest input.** ALPHA with 97 of 100 science members clean: one member aborted in each of three quads of the
decode cell.

**What happens** (`p2_excl.py`): `claim_usable=False reasons=['cell.below_minimum']`, kept units decode
`{'quad': 7, 'repeat': 10}`, prefill-p2048 `{'quad': 10, 'repeat': 10}`. Two lost quads keep the window.

**What the exclusion protects.** `p8_allow.py` prints the allowlist entry: category NUMBER_INTEGRITY, `protects`
"fewer valid members in a cell than the registered minimum (statistical power of the reported number)". Statistical
power is neither of the doctrine's two reasons: with 7 units no number is wrong and none is unattributable. The
repository's own estimator says where a number stops being computable: `detection_floor.small_sample_guard_factor`
returns 1.134, 1.225, 1.342 and 1.5 for n = 8, 7, 6 and 5 and raises "guard factor undefined below n=5" for 4.

**Rates** (`p4_arith.py`, and the last probe of the session). The registration's planning figure recomputes: with
each member lost independently with probability 1/37, a floor window is usable with probability 0.8486. So 15.1% of
floor windows are removed by chance, and in 14.5 of those 15.1 points exactly one of the two target cells is short
while the other is fully usable. The figure counts one cause, idle-admission aborts; forty codes remove a member.
The probability that a floor window is usable, by member loss rate p and by minimum:

| p | minimum 8 | 7 | 6 | 5 |
|---|---|---|---|---|
| 1/37 | 0.849 | 0.971 | 0.996 | 1.000 |
| 0.05 | 0.508 | 0.814 | 0.952 | 0.991 |
| 0.08 | 0.169 | 0.474 | 0.767 | 0.929 |

The price of a lower minimum is a wider interval, not a wrong one: the reported-cell half-width grows by at most
17% at 8, 29% at 7, 47% at 6 and 74% at 5 units per stratum.

Registration §14 Q3 says the contention rule "has never been applied to every process on this Mac during a
window". The only real windows the harvest has judged are the rehearsals of 2026-10-06: `contention.request_overlap`
fired on 13 of 13 measured members (alpha-1) and on 11 (gamma-2). That is not a rate for a quiet window: the census
was overridden and other sessions were running (the dominant offender is an outside `Python` at about 1.0 CPU-s/s).
It does mean that no measured rate of member loss exists except the 1/37 of one cause.

**At stake.** At the documents' own rate, about one window in six or seven per pack; if the true member loss rate
is 5%, one in two.

**Cure. Catalog and text; no code.** The exclusion function reads the rule from the catalog. Either (a)
`"rules": {"cell_unit_minimum": 5}`, with §6.6 "Why 8" replaced by "Why 5: below 5 units the floor guard is
undefined (`small_sample_guard_factor`), so the cell's floor cannot be computed; from 5 to 9 the guard and the
quantile t(0.975, n − 1) widen the result (2.776, 2.571, 2.447, 2.365, 2.306)", the quantiles for 4, 5 and 6 degrees
of freedom added to analysis plan §4 step 3 and §7.1 step 4, and the fixed sentence of plan §8.1 changed to "at
least 5 of 10"; or (b) keep 8 and say in §6.6 and in the allowlist entry what it is: a precision target chosen by
the owner, not number integrity, with the table above in place of the single planning figure. I recommend (a) with
7 or 6 if the judge wants a precision floor; the choice of number is the judge's.

### RF-5. B2. BREAK. A reference whose contention or battery evidence is unmeasured stays in the drift screen

**Where.** Registration §0.12, lines 596 to 598: "A reference whose physics is *unmeasured* (`contention.unmeasured`,
`battery.unmeasured`, `clock.unmeasured`) is **kept**: unknown evidence never authorises an omission". Registration
§6.4 and the catalog: `contention.unmeasured` and `battery.unmeasured` remove a science member. Code:
`harvest.NEG8_REFERENCE_LOSS_CODES`.

**The inconsistency.** The documents' test for a missing measurement is: when the evidence that would show a member
clean was never taken, its number cannot be attributed to a clean machine, and removing it is number integrity
(triple audit, Astra A4, kept on that ground). §0.12 applies the opposite to the seven references and the twelve
corpus members, whose energies decide whether the whole window's numbers stand and how wide every interval is.
`p8_allow.py` prints the loss codes (eleven; none is an `*.unmeasured` code) and the catalog effects
(`contention.unmeasured` EXCLUDE_MEMBER, `battery.unmeasured` EXCLUDE_MEMBER).

**Smallest input.** The contention journal has a gap over one start reference's request (a monitor restart), and a
background process runs in the gap. The window has really drifted.

**What happens** (`p4_arith.py`, with `whole_window.neg8_count_adjusted_bound` on the registration's own corpus).
bound(3, 3) = 0.5933 J. Start references 100.02, 99.91, 99.95 J and end references each 0.80 J higher give a screen
statistic of 0.800 J: the screen fails and the window is removed. With one start reference raised by 0.855 J (the
size of the contender's effect in the registration's own example, 101.08 J against about 100.22 J) the statistic is
0.515 J: the screen passes, the window is claim-usable, and its allowance is 0.5933 J. Had the same process been
seen, the reference would be lost and the survivors would fail the screen (bound(2, 3) = 0.6383 J against 0.83 J).

**Not executed.** I did not run a whole window through the harvest with a journal gap over a reference; the
harvest's constant and the registration's sentence agree that it is kept, and a fixture with reference bundles and a
contention journal gap would settle it. I also did not execute two measured cases that the loss list omits:
`env.member_quiet_state_violated` (a display awake or the screensaver running during the member, the contamination
decision D-078 item 4 closed for science members) and `battery.capture_pair_failed`. `p10` lists the thirty codes
that remove a science member and do not make a reference lost. For those two, which of two wrong outcomes follows
(the contaminated energy stays in the screen, or the screen fails as in RF-1) depends on whether the reducer marks
the request precheck; I report them as SUSPECTED.

**At stake.** The screen's pass and the drift allowance of one window, which reach every reported cell through B and
every contrast through D. The rate is the product of a monitor gap over one of 7 reference requests and a
background process in it; the documents give neither.

**Cure. Text and harvest code (not collection code).** Add `contention.unmeasured`, `battery.unmeasured`,
`env.member_quiet_state_violated` and `battery.capture_pair_failed` to `harvest.NEG8_REFERENCE_LOSS_CODES` and to the
corpus drop; the survivors rule then decides. Replacement for the §0.12 sentence: "A reference whose contention or
battery evidence is unmeasured (`contention.unmeasured`, `battery.unmeasured`) is lost, by the test §6.4 applies to
a science member: the evidence that would show it clean was never taken. `clock.unmeasured` and
`thermal.unmeasured` do not lose it, for the reasons §6.4 gives. The loss test still never reads an energy." The
cost is the mirror of the gain: a monitor outage over all three references of one endpoint then removes the window
(`references_insufficient`); the judge should weigh that against the case above.

### Notes (none is a break)

- **N-1. Flags the exclusion function drops without a flag.** `p2_excl.py`: an EXCLUDE_WINDOW flag whose
  `scope.attempt` or `scope.plan_id` differs from the roster's is skipped (`claim_usable=True`,
  `foreign_scope: 1`); an EXCLUDE_MEMBER flag at member level whose run id is null or not in the roster is skipped
  (`unmatched_member: 1`). Both leave a count in `exclusions.json` and nothing else. No writer I read produces
  either, so I file no break; a DISCLOSE flag for a nonzero count would make the drop visible.
- **N-2. `whole_window.verdict_unauthenticated` (hunt point 7).** `harvest._neg8_rescreen`'s docstring: "the harvest
  validates rows without a consumption session ... so no row is authentic here". The code therefore fires on every
  harvested window (it did in the rehearsal, `{"verdict_rows": 1}`) and carries no information; DISCLOSE is the only
  effect it can have. On the ordinary path (`neg8_screen` returns `stored_verdict`) the harvest takes the screen's
  decision from the row without re-deriving it. That row is written by the harvest's own run of the production
  writer on the same bytes minutes earlier, so I found no wrong number behind it. Registration §0.17's "re-derives
  every number-protecting check" should say this.
- **N-3. The two disclosed aggregate codes (hunt point 3).** I could not break them. G3 runs only on GAMMA
  (`g3.not_applicable` on floor packs). A disagreement between the stored row and G3 about the screen is disclosed
  only; both are computations on the same bytes, so a disagreement is a tooling fault.
- **N-4. Known, confirmed in passing.** The allowlist lists `g3.recompute_failed` under `window_exclusions` while
  the sealed catalog says DISCLOSE, and `tests.hazards.test_refusal_allowlist` passes (23 tests) all the same (F5).
  The two `extraction_spec.json` file digests in analysis plan §4 are stale: the files hash to `a6498f56…` and
  `2c0ee718…`, the plan prints `8b796985…` and `53e71b38…`; the two `registration_sha256` values inside them match
  (F1). "Re-tied at seal" (plan lines 206, 291, 366) is not done.
- **N-5. SG-13, for the judge.** `p12_sg13.py`, 200,000 trials each, normal errors, a quarter of the quad variance
  from member random error: the plain t interval covers 0.949, 0.951, 0.950 at n = 8, 9, 10; with the metrology term
  added, 0.980, 0.979, 0.978. The engine's interval has the stated coverage for error that is random from run to run.
- **N-6. A constraint on the text changes this gate will require.** The harvest parses the registration's own
  section "### 6.9 Harvest thresholds" (test
  `RegisteredThresholdTests.test_the_design_branch_registration_parses_to_the_registered_block`, ran, OK). An edit
  that moves or rewords that heading or its JSON block makes every harvest fault.
- **N-7. A fact for RF-4.** A window whose model identity the arm's collector already found mismatched still runs
  for its full length and is removed afterward, because the driver does not read flags. The desk collectors before
  scheduling are the only guard. That is the doctrine's design; I note the cost, one window, if the desk step is
  skipped.

## 4. What I attacked and could not break

| Place (charge section 8) | Probe | Result |
|---|---|---|
| Point 1, 8 of 10 | `p2`, `p4`, guard probe | RF-4 |
| Point 2, catalog effects as a whole | `p1` (192 codes: 120 DISCLOSE, 40 EXCLUDE_MEMBER, 32 EXCLUDE_WINDOW; one RESTRICTED); `p7` (every code of `harvest.CODES` 175, `DRAFT_CODES` 146, `CORE_FLAG_CODES` 19, `km003c_parse.CODES` 7, `FINDING_CODES` 17 is in the catalog; the only flag literal outside it is `collector.unmeasured`); `p8` (allowlist: 34 window entries, 30 NUMBER_INTEGRITY and 4 PHYSICS; 40 member entries; every sealed excluding code listed) | no break beyond RF-3, RF-4; counts in §6.11 recompute (2,749 entries, 3,869 sites; 30/31, 35/58, 91/117, 2,593/3,663) |
| Point 3, the two disclosed aggregate codes | read of `harvest.whole_window`, `neg8_screen`, `g3` | not broken (N-3) |
| Point 4, the sensitivity line | read only | NOT ATTEMPTED by execution; no defect seen in the rule as written |
| Point 5, lost midpoint by pack | `p2`, `p12` | RF-2 |
| Point 6, wrong model on a reference | `p2`: member-level `model.identity_mismatch` on a reference gives `claim_usable=False`; `model.identity_underivable` removes only the member | behaves as registered; not broken |
| Point 7, unauthenticated verdict row | read of `harvest.whole_window`, `_neg8_rescreen`; rehearsal flags | not broken (N-2) |
| Point 8, sealing with known NEG-8 defects | `p9`, `p10`, `p11` | RF-1: a fourth defect of the same class, this one in the writer and the replay, not in claim-time code |
| Point 9, battery-assist line for GAMMA | `p4`: 2.9625, 0.16850, 0.059574, 0.035355, 0.069276, [2.7987, 3.1263] | recomputes; not broken |
| Point 10, how the seal lands | none | NOT ATTEMPTED (the dispatch puts SG-10 in stage 2) |
| B1 method: each EXCLUDE_WINDOW code's mildest trigger | `p3` emitters; reading of §6.5 | RF-1, RF-2, RF-3, RF-4. Not examined one by one: the eleven `calibration.*` codes, `clock.systematic`, the identity codes |
| B1 method: EXCLUDE_MEMBER codes | `p2` (quad removal, bundle-level placement) | not broken; the thirty codes that do not lose a reference are in RF-5 |
| B2 method: results taken from a stored record | read of `neg8_screen` | N-2 |
| B2 method: journal gaps | reading of §6.4 against the catalog | RF-5 for references; for science members `contention.unmeasured` and `battery.unmeasured` exclude, `clock.unmeasured` and `thermal.unmeasured` disclose with a stated reason; not broken |
| B2 method: undecided but claim-usable | `p2`: an UNCLASSIFIED code gives `claim_usable=True release_blocked=True`; `first_claim_usable` returns `None` while the first usable attempt is blocked | behaves as registered |
| B2 method: re-arming reading an energy | read of `exclusions.py` (reads code, scope, interval, id, pack id) | not broken |
| B2 method: one process under the limit many times | read of `hazards/contention.py`: the rule in the window is per process, by process tree, not by name | as registered ("a contending process"); the summed outside CPU is journaled and not judged; not filed |
| B3: digests | `p6`: 43 distinct 64-character digests in the registration, 13 equal a tracked file at HEAD (all three plan trees, acceptance, both policies, sizing source, identity pins, sizing output, three prefill-pin files, pin registry); 6 record digests under `night-archive` recomputed and equal (four audit reports, `DRY_RECORDS.md`, `cooldown-join-check.json`); the rest are internal digests with no file to hash | no new mismatch (N-4 known) |
| B3: probabilities and worked examples | `p4`: §0.12 (s 0.2353; bound(3,3) 0.5933; bound(3,2) 0.6383; 0.2650; 0.5500), §6.6 (17%, 1.134, 0.85, 0.04), §7.2 (0.073%), plan §4 (10.16, 0.0022933, 0.10833; 10.13333, 10.12927, 0.11519, 6.3%), §7.2 ([2.8325, 3.1675], t 41.3, 0.0375), §8.1 (10.16222) | all recompute |
| B3: derivation checks | `size_b5_window.py --check`, `write_b5_identity_pins.py --check`, `joulewise.b5.reference_spares --check`, three `generate_configs.py --check` | all exit 0 |
| B4: catalog against text | `p7`, `p8`; reading of §6.2 to §6.8 | no new mismatch (the sweep's A13, C3, C7, C11 known) |
| B5: harvest step order | read of `harvest.harvest`: `model_identity`, `monitor`, `neg8_corpus_physics`, `neg8_screen` in that order | as registered |
| B5: a flag whose scope cannot be placed | `p2` | N-1; a stage or window-level member code with no interval removes every member (conservative, as the code comments say) |
| B5: verdict member reasons | `PROSPECTIVE_MEMBER_FAILURE_REASON_CODES` (13) against `WHOLE_WINDOW_MEMBER_FAILURE_REASONS` (11) | the two left out are the two §6.3 names |
| B5: thresholds of §4.3 and §6.9 | the registered-block parse test only | NOT ATTEMPTED against the hazard modules' constants |
| B5: chain deviations, agent census, import-graph test | none | NOT ATTEMPTED (census rule is rewritten in revision 10; A18 known) |
| SG-12 (restricted code by name) | none | NOT ATTEMPTED |

## 5. Summary

The four documents can be sealed only after five rules are changed or re-stated; none of the five lets a wrong
energy into a claim by itself, and four of them throw away a whole day of clean measurement for an event the same
documents elsewhere price at one lost unit or at nothing. The worst is in the drift check: one reference run whose
energy cannot be read is not treated as lost, so the check fails and the window is discarded, and curing it needs a
change to code that runs during a window, which must be made before the code is frozen. The fifth works the other
way: a reference run during which contention or the battery was not measured stays in the drift check, where a
background process can hide a real drift.
