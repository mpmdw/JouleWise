# Refutation of draft Erratum 3 (block 5): which calibration events in the ledger may fail a later window's bracket

Refuter: Opus 5.5, 2026-10-11, for the cold gate of registration section 10. Structure only: this file holds no
energy, no power, no duration of a workload and no member's name. Times in milliseconds are alignment bounds from
the calibration ledger.

**Verdict in one paragraph.** The direction is right and the registered alternative is worse science. The draft
cannot be admitted as written. Three defects each lose the next window or leave the pin open to being held
unlawful (findings 1 to 3), and six more weaken a protection or leave the rule unfinished (findings 4 to 9). All
nine are cured by text. I recommend ADMIT-WITH-CORRECTIONS, with the corrections of the last section.

## Abbreviations, as in the draft

REG is the sealed registration (`registration_block5.md`, SHA-256 `c7b3fdf7…db3f`, recomputed by me). AP is the
analysis plan beside it. BRK, H, WW and CL are `joulewise/calibration_bracketing.py`, `joulewise/b5/harvest.py`,
`joulewise/whole_window.py` and `joulewise/calibration_ledger.py` in the desk checkout at commit `0699abbb0`
(checked: `git rev-parse HEAD`). RC is `scripts/run_campaign.py` in the measurement clone. PRE is the calibration
pre-registration `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` in the clone. VPF is the clone's
capture tool, `scripts/validate_powermetrics_fiducial.py`. "Governed", "screen", "padding", "operative bound",
"stale", "stored verdict" and "claim consumer" have the meanings the draft's section 1 builds.

## What I executed

1. `shasum -a 256` on the registration, the analysis plan, the flag catalog, the acceptance file, and both copies
   of BRK. All match the draft; the two BRK copies are identical (`ddb7db11…4037`).
2. A program over the live ledger printing sequence, event, class, slot, session suffix and alignment bound for
   entries 377 to 478. It confirms 18 post-cutoff captures, one of class `systematic-invalid` (entry 456), and
   seven finalized sessions. From those bounds I recomputed the seven operative bounds of the draft's section 6
   item 3; they agree.
3. The pinned bracket evaluation (desk BRK, the clone's interpreter, flags `-I -B`, nothing written) over the live
   ledger for BETA attempt 5's own session, with its real binding, in three forms: as pinned; with only the early
   return of BRK 2589 to 2602 disabled in memory; and with that return disabled and the three names also removed
   from the failing set of BRK 2713 to 2718. Printed: status words, reason codes, trigger names, and whether
   endpoints and a bound exist. Results are in finding 1.
4. A program printing each flag catalog code's effect and family, and the list of all 32 window-removing codes.
5. A program counting flags by code (unrestricted codes only) in the `derived/flags.jsonl` of three archives:
   ALPHA attempt 1 of the second seal, BETA attempt 4 (`-r2`) and BETA attempt 5.
6. A program printing the key names of entry 456's evidence record, then, for each of the 18 post-cutoff
   captures, how many of its 59 pulses have a timing-interval end above the screen.
7. `harvest.json` of BETA attempt 5: the permitted fields only.

**One breach of my own blinding brief, disclosed.** One probe of step 6 printed, for three captures, three
per-pulse timing values in milliseconds beside the counts. They are calibration timing diagnostics of capture
files under a restricted root, not energies, powers or workload durations, but they are more than counts. They are
not reproduced here and nothing below rests on them; the counts alone are used.

## Findings

### 1. BLOCKER. Item 3(a), implemented as written, does not cure the stale state

*Evidence.* Item 3(a) says the function "does not take the early return at BRK 2589 to 2602" and "goes on to
select and compare the window's endpoints". It also says the function appends the trigger name "as it does today".
For events (b) and (c) the draft adds "The name is no longer in the set that fails the bracket at BRK 2709 to
2728". For (a) it does not. That set (BRK 2713 to 2718) contains
`new_systematic_failure_challenges_preflight_screen`. Executed (step 3), on BETA attempt 5's session:

| Form | status | reason | endpoints selected | bound |
|---|---|---|---|---|
| pinned | `failed` | `calibration_acceptance_bound_stale` | no | none |
| early return disabled only (item 3(a) read literally) | `failed` | `calibration_acceptance_bound_stale` | yes | none |
| early return disabled and the three names out of the failing set | `passed` | none | yes | present |

The worked example and item 6 show what was meant. An item-by-item check of a program against item 3(a) cannot
show it. A second problem sits in the same place: the one trigger name is raised by two different events (another
session's capture at BRK 2577 to 2584; the window's own pre bound at BRK 2697 to 2700). A rule that sorts by name
cannot say which event fails.

*Required text, replacing item 3(a) and the first sentence of item 6.* "(a) With `"window_evidence"`, an
observation of BRK 2577 to 2584 that is not the window's own is recorded: its ledger sequence is added to
`other_session_systematic_sequences`, and the name is appended to `observed_triggers` as today. It causes neither
the return at BRK 2589 to 2602 nor a failure at BRK 2709 to 2728. With `"window_evidence"` the set of names that
fails the bracket at BRK 2709 to 2728 is exactly `{"protocol_or_estimator_byte_change"}`. The window's own pre
bound above the screen fails as today through the return at BRK 2697 to 2707, which does not depend on that set.
Failing is decided by event, never by trigger name."

### 2. BLOCKER. The change leaves the files REG section 11 item 4 allows, and the draft amends only one of the three sealed texts that state the rule

*Evidence, files.* REG 5522 to 5526 names what the harvest lane may change: `joulewise/b5/harvest.py`,
`joulewise/whole_window.py` (two functions), `scripts/harvest_b5_window.py`, tests and fixtures, "and nothing the
chain or the members execute". All three earlier pins stayed inside that list (seal record, Addenda 1 to 3, each
with a `git diff --name-only` statement). Erratum 2's ruling made admission rest on it (J4: "the diff stays inside
the files §11 item 4 allows"). Draft Erratum 3 changes `joulewise/calibration_bracketing.py`, which is outside the
list and which the chain does execute from the clone (VPF imports it). The draft cites REG 4777 to 4779 only. That
passage says such a desk change is not collection code; its last clause sends the reader to section 11 item 4 for
what the lane may change.

*Evidence, texts.* The consequence "brackets stop passing" is stated in three sealed places: REG 4.6 item 2; PRE
880 to 883 ("the validator reports the trigger …, brackets stop passing, and a re-derivation is due"); and the
acceptance file's own key `prospective_rederivation`, whose five names the evaluation labels `mandatory_triggers`
(BRK 2295). The draft amends REG 4.6 item 2 and REG 6.5 only.

*Does it need a new seal? No.* No file a window reads changes. I checked the one in-window reader of the
acceptance: VPF 372 to 500 tests the protocol and estimator bytes and the identity epoch, and derives the screen.
It does not evaluate the doubling count, the range or another session's class. So no in-window step acts on the
three triggers, and a window's bytes are the same under either rule. Section 7.5 does not bite: the clone's copy of
BRK stays byte-identical, so no collection code that a completed window executed differs. REG 2600 ("A change to
any item after the seal needs a prospective cold erratum before the next arm") and section 10 cover a rule change.

*Required text, added to section 5.* "This erratum amends REG section 11 item 4 for this lane only: the lane may
also change `joulewise/calibration_bracketing.py`, in the desk checkout only, and only as section 4 item 1
describes. With `trigger_scope` `"sealed"` the desk copy's two functions must return, on every fixture of the
lane and on the rehearsal copy, exactly what the clone's copy returns; a test in the lane asserts it. For governed
attempts of block 5 this erratum also supersedes the sentence of PRE 880 to 883 that brackets stop passing after a
doubling, and the reading of the acceptance's `prospective_rederivation.triggers` as events that fail a bracket.
The acceptance's bytes, its rule `judge_under_prior_artifact_never_self_fit` and PRE 253 to 259 stand: entry 456
was judged under the prior acceptance, it failed its own window, and it enters no threshold."

### 3. BLOCKER. "Arm before pin" turns any defect in the text into a lost window, and lets the fallback be chosen with the window's captures known

*Evidence.* Section 5 copies Erratum 2's clause: if the gates find that no program can implement the text exactly,
the armed attempt "is harvested by pin `0699abbb0` and judged under the sealed rule, which removes it". Under
Erratum 2 the fallback only erred toward removal. Here it removes the window with certainty, because entry 456
stays in the ledger. Finding 1 is a defect of exactly the kind that clause is written for. The clause also buys no
time: no agent may run while a window runs, so the gates and the window are sequential in either order. And the
window's two alignment bounds are in the released ledger as soon as it ends, so anyone deciding whether the text
"can be implemented exactly" can compute by hand what each reading would do to that window. The decision record's
own next-action list already puts the pin (steps 3 and 4) and a pre-arm probe run from the new pin (step 5) before
the arm (step 7).

*Required text, replacing the "Arm before pin" paragraph.* "Pin before arm. No governed attempt is armed until
Addendum 4 step 2 is on main. If the gates find that the admitted text cannot be implemented exactly, a corrected
erratum is admitted before any governed attempt is armed."

### 4. MAJOR. The claim-consumer rule must be admitted now (option C1), and item 10 is not yet a rule

*Verified.* The consumption session loads the ledger from the importing checkout's default paths when handed none
(WW 521 to 536; CL 107 to 111), as does the analysis engine (`analysis_engine/inputs.py` 1758 to 1772 and 3282 to
3296). It re-evaluates the bracket with the default scope (WW 707 to 735) and refuses the window when no bound
results (WW 738 to 748). `calibration_acceptance_bound_stale` is a refusal (`analysis_engine/claims.py` 64; WW
261). My step 3 shows the pinned function returning stale on the live ledger. So at release time, on the live
ledger, ALPHA attempt 1 and every governed window are refused.

*Why now.* REG 4627 to 4629: a pack is never armed again after a claim-usable attempt. A governed attempt that the
harvest calls claim-usable and that no consumer may lawfully read ends its pack with no number. Erratum 2's ruling
upheld the same point as a BLOCKER: the consumer rule "must be in the admitted text now, not written after the
windows that take this path are known". The code can follow in a named lane before the release event, because
consumers never run during collection. Option C2 is rejected for that reason. Option C3 is rejected because it
removes the consumer's independent re-derivation.

*What item 10 lacks.*

- It lists four code sites. There are more: the mint reads the stored basis's calibration pair
  (`scripts/mint_floor_artifact.py` 1180), as do WW 5713 and WW 5911; a non-empty stored condition list is itself a
  refusal (WW 5513 to 5515). A list of sites will be incomplete; the rule must be stated by what a consumer may
  take from where.
- The analysis engine takes one ledger snapshot for all the windows of a run (`inputs.py` 1754, 3289). One
  snapshot cannot serve ALPHA (sealed scope, 432 entries) and a governed window together.
- It removes the comparison of the stored bracket with the consumer's own (WW 5560 to 5566) and puts nothing in
  its place. The natural replacement is the harvest's own evaluation, but its digest is not bound: H 4593 writes
  `withheld/bracket-evaluation.json` and discards the returned SHA-256, where H 4458, 4497 and 4578 store theirs
  in `outputs`.

*What must be true of the bytes.* The window itself writes nothing that depends on the rule (finding 2). The
stored verdict is another matter: the sealed writer's row is create-once and its campaign-log row is append-only
(H 5718 to 5731), so a governed window's stored verdict lacks the calibration pair, the operative bound and the
launch lineage for good. A later lane can still analyse the window if, and only if, the harvest archive holds,
each with its SHA-256 in `harvest.json`: the ledger copy through the window's terminal entry, the terminal pin,
the bracket binding, and the harvest's bracket evaluation. The first three are bound today. The fourth is not.
The launch lineage needs no record: it is a function of the member bundles, the two capture files and the bound
artifact (WW 3054 to 3120), whose bytes the archive inventory already binds.

*Required text, replacing item 10.* "10. **Claim consumers.** (i) A consumer evaluates each window's calibration
bracket over that window's archived ledger copy and terminal pin, with that window's `derived/bracket-binding.json`,
and with `trigger_scope` `"window_evidence"` exactly when the attempt is governed. A consumer that reads several
windows evaluates each against its own archive; one snapshot for several windows is not admissible. Each archived
ledger copy must be a byte prefix of the ledger at the release event. (ii) For a governed window no consumer
takes the calibration pair, the operative bound, the allowance, the launch lineage or the bracket's conditions
from the stored verdict or its evaluation basis. It takes them from its own evaluation, which must equal the
harvest's `withheld/bracket-evaluation.json` assessment, authenticated by the SHA-256 in `harvest.json`; any
difference refuses the window. It recomputes the common launch lineage from the member bundles, the two captures
and the bound artifact against that bracket. It disregards the stored condition
`calibration_acceptance_bound_stale` and no other. (iii) The membership, provenance and physics checks stay
independent. (iv) Lane L9-BRACKET of AP section 11 implements this before any claim is computed; until it lands no
number of a governed window is claimable." And in item 8: "`harvest.json` `outputs` gains
`withheld/bracket-evaluation.json` with its SHA-256."

### 5. MAJOR. "Every check of the window's own evidence stays as sealed" is false as drafted

*Evidence.* REG 2493 to 2496 makes a window's own valid capture outside the range of the 24 a trigger ("A
window's own pre and post captures are captures of this kind"). Item 3(b) demotes it "whether it belongs to the
window or to another session", and item 5 gives the case (a pre or post below 21.93 ms). The amendment's headline,
the paragraph "Why this cannot let a window with a bad bracket pass", and section 6 item 1 all say own-evidence
checks are untouched. The decision record carries the same contradiction. A low own capture is not a physical
hazard, so I would admit the relaxation; but it lowers the operative bound below anything the acceptance has
produced (two captures of 20 ms give 34.5 ms, under the 36.46 ms minimum), and that is the direction that
understates a timing bound. Finding 7's sensitivity value covers it.

*Required text.* Headline: "Every check of the window's own evidence stays as sealed, with one exception stated
in item 5: the window's own valid capture below 21.93 ms is recorded and no longer fails the bracket." Section 6
item 1 gains: "For a governed window this includes its own capture below the range of the 24; such a window's
operative bound can be below 36.46 ms, and the paper marks it."

### 6. MAJOR. The one thing the systematic trigger protected that own captures do not is replaced by nothing

*What each trigger protected, and what protects it afterwards.*

| Trigger | What it protected | After the erratum |
|---|---|---|
| doubling at 48 | nothing measured: it schedules a re-derivation by a count of captures, whatever they read (PRE 880 to 900, which says of the choice of which captures count: "The choice changes when re-derivation is due. It changes no number") | item 11 (due before the next block's seal). Sufficient |
| valid capture outside the range | the padding, which is the range of the 24 | the high side cannot occur for a valid capture (the post slot is classed against the same screen: CL 6112 to 6121 refuses to finalize a bracket slot without one, checked). The low side: finding 5 |
| systematic capture of another session | (i) the level now; (ii) a stop when the instrument has left the state the 24 describe | (i) the window's own pre and post against the same screen, which is a direct measurement where the trigger was a proxy. (ii) nothing |

On (ii): if the instrument did shift, windows would still be kept whenever their own two captures happened to
read low. Kept windows would then be the ones with two lucky draws, and their operative bounds would be biased
low. The draft's only answer is the drafter's dissent 1, outside the rule.

*Required text, a new item of section 4, a rule for the lead and not a program refusal.* "13. **A repeat.** When
the ledger holds two or more post-cutoff captures of the judged epoch with class `systematic-invalid`, the lead
arms no further window until a consult of two blind seats has read those captures' per-pulse counts and the
monitor's contention journals and recorded a decision; it may authorise unchanged arming. Two such captures in
succession, with no valid capture between them, go to a cold gate. Before every arm the lead runs the pinned
bracket evaluation over the live ledger for the last finalized session and records freshness, the trigger names,
the doubling count and the systematic sequences." (Under exchangeable captures a second exceedance among the
first 24 post-cutoff captures has probability 24×23/(48×47) = 24.5%, so a consult, not a stop, is the
proportionate response.)

### 7. MAJOR. Q-A: the draft leaves the choice open; the judge should take A1′ for all three quantities, fix its bound now, and reject A1, A2 and A3

*Is the padding plus the window's own two captures enough?* For what the registered bound claims, yes, and no
less than for ALPHA attempt 1, whose protection was the same two captures and the same padding. No whole-ledger
trigger ever measured anything about the window being judged. An excursion that begins and ends between a
window's two captures is unseen under the sealed rule and under the erratum alike; only a capture inside the
window would see it, and that is window code for the next block. Against its neighbours entry 456 sits 12.97 ms
above the capture 46 minutes later (inside the 14.531 ms padding) and 16.95 ms above the capture before it
(outside the padding and above the 15.502 ms drift ceiling). So the padding does not provably cover a repeat, and
the paper must say so with a number.

*Evidence on what entry 456 is* (step 6; counts from the per-pulse interval ends in each capture's evidence
record; my statistic tracks but does not exactly reproduce the registered bound, so the lane should recount with
the estimator's own function before this is printed). In entry 456, 2 of the 59 pulses exceed the screen and
1 pulse stands alone within 2 ms of the capture's largest. In the other 17 post-cutoff captures, 0 of 1,003
pulses exceed it. That is a short event on one or two edges, not a level that held through the capture. REG 949
to 953 defines the bound as a 95/95 bound, so a rare single-edge exceedance is inside what the bound already
allows. This argues against treating 44.38 ms as the instrument's standing bound.

*Ruling I recommend.*

- **A2 (compose): reject.** It makes a later window's numbers depend on another session's capture. It breaks a
  registered refusal: `registered_common_mode_operative_bound` (`joulewise/detection_floor.py` 757) refuses unless
  the bound equals the endpoint maximum plus the allowance embedded once (AP 313). It gives BETA and GAMMA a
  different bound rule from ALPHA, whose floors GAMMA's contrasts are judged against "once and identically"
  (AP 316 to 317). And it adopts a sample maximum as a bound, the statistic that stopped this block.
- **A1: reject.** It prints a wider value for the windows that happen to follow entry 456 and not for ALPHA, on
  the same instrument.
- **A3: reject.** The paper would carry a measured counter-example with no number.
- **A1′, extended to quantities (i), (ii) and (iii): admit.** Only (ii) and (iii) can change an interval or turn
  a contrast `not_resolvable`, so a floor-only value cannot tell the reader whether any conclusion depends on the
  excursion. The consumption session already re-reduces every member under a bound in memory (REG 863 to 868), so
  a second pass under a wider bound is the same code.

*Required text, a new item of section 4.* "14. **Sensitivity bound.** Primary numbers of every window are
computed under the registered operative bound. For every analysed window of block 5, governed or not, the
analysis also prints, labelled as a sensitivity value and never composed into a primary number, each attribution
floor, each interval and each contrast's verdict recomputed under b_sens = max(operative bound, B_max). B_max is
the largest alignment bound among the captures of the judged epoch whose class is `valid` or
`systematic-invalid`, over the 24 and every ledger entry up to the terminal entry of the block's last analysed
window. The definition is fixed by this erratum. Its text in the analysis plan and its code are lane L9-BRACKET's,
written blind before the release event." (The draft's "at the release event" leaves the ledger extent open; later
calibration sessions could move it.)

### 8. MAJOR. A whole-ledger path that still removes a governed window, which section 3.2 says does not exist

*Evidence.* Section 3.2 says everything but the three triggers "is computed from the window's own two captures".
It is not. Candidate discovery reloads every valid capture of every finalized session from the custody path the
ledger recorded, and returns nothing at all if one fails to load (BRK 1984 to 1989, 1809 to 1849). The evaluation
then refuses (BRK 2358 to 2359; `calibration_ledger_custody_invalid` at BRK 2877 to 2887). Item 4 keeps this "as
sealed". The check is sound (it stops a caller from withholding captures), but it means that moving or offloading
the capture directory of any earlier attempt, including the removed BETA attempts whose captures sit under their
attempt roots, removes every later window and refuses every consumer of finding 4. My step 3 loaded all 14
candidates today.

*Required text.* Section 3.2: replace the sentence with "The completeness check of the candidate list (BRK 2358
to 2385) also reads every earlier valid capture; it stays as sealed." Section 5 gains: "Retention. The capture
directory of every post-cutoff capture stays at the path the ledger records, unmoved, until the release event.
The pre-arm run of item 13 proves it before each arm."

### 9. MAJOR. Erratum 2's recovery in the stale state is untested and one sentence of Erratum 2 becomes false

*Evidence.* Erratum 2 item 7 ends: "the common launch lineage is bound through the basis". On a governed window
the stored basis has no launch lineage, because the writer builds it from the bracket's pre endpoint (WW 2638 to
2678) and the stale bracket has none. Nothing at harvest then binds a recovered reference to the launch. By
reading, the recovery itself is not disturbed: its trigger (item 0(c)) reads membership conditions only, and the
screen reads only conditions that begin `neg8_` (H 4939 to 4943). But Erratum 2's ruling put that path at about
17.5% of windows, and every governed window is in the stale state, so about one governed window in six will take
a combination that has never run. If it misbehaves the result is `neg8.screen_failed`, a lost window. GAMMA adds
one known effect: the desk provenance checker runs with the default scope, so `g3.recompute_failed` will be
recorded on every governed GAMMA window. The catalog classes it `DISCLOSE` (checked), so it removes nothing, but
the one independent recompute of the verdict is lost for those windows.

*Required text.* Item 9 gains: "On a window governed by this erratum and by Erratum 2, the last sentence of
Erratum 2 item 7 does not hold; the launch lineage is recomputed by the consumer under item 10(ii)." Section 5,
gates: "plus an executed fixture of a stale ledger with a verdict that records no sources, and an executed
fixture of a GAMMA-shaped window in the stale state, each showing the window-removing codes that result." Section
6 gains the GAMMA sentence above.

### 10. MINOR. Item 4 misdescribes the window's own post capture above the screen

`build_calibration_bracket_binding` raises when either slot is not `valid` (BRK 1472 to 1488), so the harvest
records `calibration.binding_failed` and returns before the call (H 4568 to 4576); `calibration.capture_invalid`
fires too (H 4514 to 4518). Both are window-removing (checked). The function is never called, so it takes no
"early return", and with a validated binding (which requires both slots valid, BRK 1591) every
`systematic-invalid` observation is another session's. The outcome in the draft is right. Correct the bullet, and
the worked example's first variant, to say `evaluated` is false and name the two codes.

### 11. MINOR. Field and class names in item 2 and section 1

A ledger entry carries `session_id`; `bracket_session_id` is the attribute of the loaded observation. The ledger
has four final classes, not three: `abandoned` also exists (CL 122 to 124) and reads as `unresolved`, which fails
at BRK 2531 to 2536. Say both.

### 12. MINOR. `harvest.json` will not carry the digest of the file that now decides

`harvest_checkout.files` lists three files (read from attempt 5's `harvest.json`); `calibration_bracketing.py` is
not among them. The commit and the clean status bind it indirectly. Add it to the list in the new pin.

### 13. MINOR. The run over attempt 5's bytes

The decision record plans an exploratory run of the new program over attempt 5 before release. Erratum 2's
admitted text allowed such a run only "after the release event"; the draft's item 12 drops those words without
saying so. A real stale ledger is the right test, and step 3 above shows the bracket evaluation alone can be
exercised on it. Limit the pre-release run to the bracket evaluation, printing status, reasons and trigger names,
and never a `claim_usable` for attempt 4 or 5.

### 14. MINOR. Disclosures

Section 6 item 6 should add that the choice of which triggers to demote was made with all 18 post-cutoff
alignment bounds known. Section 6 item 2 should carry the pulse counts of finding 7 once recounted. Section 3.3's
probabilities assume exchangeable captures; back-to-back captures may not be, and the text should say the figures
are illustrative.

## Points attacked with no finding

- **Selection on a science outcome.** With finding 3 corrected I find no path. The governing test is the plan's
  `t0_epoch_s` against a constant (the same test as H 5221 to 5227). Attempts 4 and 5 are excluded whatever they
  hold, and item 12 keeps them from the new program, which also closes REG 4696 to 4700 (a re-harvest that turns
  an earlier attempt into the analysed one). The scheduler still reads only `claim_usable`.
- **Q-B.** Confirmed. The writer computes member failures and the NEG-8 bracket before, and apart from, the
  calibration bracket (RC 7067 to 7157, 7340 to 7362, then 7363 to 7398). Catalog effects on the path:
  `whole_window.not_passed`, `whole_window.verdict_unauthenticated`, `whole_window.producer_failed` and the three
  `g3.*` codes are `DISCLOSE`; `whole_window.verdict_absent` and `whole_window.member_failures_unreadable` are
  window-removing and did not fire. Step 5: BETA attempts 4 and 5, both in the stale state, carry the same codes
  on this path as fresh ALPHA attempt 1, plus the one `calibration.bracket_acceptance_failed`; none carries a
  member failure from the verdict, `neg8.screen_failed` or `cell.below_minimum`.
- **The doubling count crossing 48 inside a governed window.** Determinate: the count is taken on the ledger
  through the window's terminal entry, its own two captures included, and a longer ledger refuses on the pin.

## Is the registered cure, or a narrower erratum, better science?

**The registered cure is not.** It gives up a claim-usable ALPHA window for no physical reason and takes two to
three days. The new acceptance would carry the same triggers: with 24 members, six further captures (three
windows) all stay inside the range with probability 24×23/(30×29) = 63%, before any retry. It would probably go
stale again inside the block, so the rule would have to change anyway, by the slower route. What a new seal would
buy is real but belongs to the next block: a capture inside the window, a screen with stated coverage, and a
verdict writer that agrees with the harvest (the desk-only route leaves every governed window with a stored
verdict that reads failed, which is the cost findings 4 and 9 manage).

**A narrower erratum is not.** Demoting only the systematic trigger leaves the block to stop at a count of 48
after three more finished windows, and at 8% per capture on the range, so a second erratum would follow, against
section 10's "settled in one erratum". Keeping the window's own low capture as a failure removes about 8% of
windows for a reading that is better than any of the 24.

## What I would admit

Admit Erratum 3 with these corrections, in this shape:

1. Scope and governing condition as drafted (items 0, 1, 2, 12), with finding 11's names.
2. Item 3 with finding 1's text: failing is decided by event; with `"window_evidence"` the failing set of names
   is the byte-change name alone.
3. Items 4 and 5 with findings 5 and 10: the headline states the one own-evidence relaxation; the own-post case
   names the codes that remove it.
4. Items 6 to 9 as drafted, with the bracket evaluation's digest in `harvest.json` and
   `calibration_bracketing.py` in `harvest_checkout.files` (findings 4, 12), and the Erratum 2 sentence (finding 9).
5. Item 10 replaced by finding 4's text (option C1, stated as a rule).
6. Item 11 as drafted.
7. New item 13: the lead's rule for a repeat and the pre-arm run (finding 6).
8. New item 14: the sensitivity bound for all analysed windows and all three quantities (finding 7); A1, A2 and
   A3 rejected.
9. Section 5: the amendment of REG section 11 item 4 and the PRE sentence (finding 2); pin before arm (finding
   3); retention of capture directories (finding 8); the two added fixtures (finding 9); the limited pre-release
   run over attempt 5 (finding 13).
10. Section 6 with the disclosures of findings 5, 9 and 14.

Not verified by me: the amended function (it does not exist); the estimator's own per-pulse computation (finding
7's counts are indicative); Erratum 2's recovery in the stale state (read, not run); a GAMMA harvest in the stale
state (read, not run); why entry 456 read high.
