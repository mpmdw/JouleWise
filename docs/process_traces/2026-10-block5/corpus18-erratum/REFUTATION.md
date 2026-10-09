# Refutation of the draft erratum "an 18-member NEG-8 corpus"

Written 2026-10-09 by the refuter seat (Opus 5.5) for the cold judge. Subject: `ERRATUM.md` in this directory.
This seat wrote this one file. It changed no code and no configuration, started no agent, made no network
request, ran no test and no generator, and ran no git command that changes anything. Structure only: this
file holds no energy, power or duration of a member of a claim window, no name of a member that failed, and
no error text. Every energy below is synthetic (random normal draws, or the draft's own synthetic list).

**Count: 3 BLOCKER, 7 MAJOR, 9 MINOR.** BLOCKER means the erratum's text must change before it is ruled.
MAJOR means the judge must decide the point. MINOR is a correction the builder can carry.

## Terms used here that the draft does not define

The draft's section 0 defines window, attempt, member, corpus, bound, screen, drift allowance, mint, harvest,
physics drop, seal, H_claim, sealed inventory and measurement clone; this file uses them as defined there.
Four more:

- **Envelope** and **repeatability term**: the two quantities whose larger is the bound (draft section 2.4).
  The envelope is the mean of the three largest kept corpus energies minus the mean of the three smallest.
  The repeatability term is t × s × √(2/3), with s the sample standard deviation of the kept energies and t
  the two-sided 95% Student multiplier for n − 1 degrees of freedom.
- **σ**: the true standard deviation of one reference member's energy when nothing drifts. The **screen
  statistic** is |end-triplet mean − start-triplet mean|; with no drift its standard deviation is σ × √(2/3).
- **Route 1 and route 2**: the two ways the harvest can accept a bound (draft finding F2). Route 1: the core
  reader `whole_window.load_neg8_drift_bound_artifact` accepts it against one fixed file. Route 2: the harvest
  validates it against the window's own list of collected members and runs the screen again itself.
- **Clean bound**: the bound that the harvest already builds, today, from the in-window bound's recorded
  member energies after it has removed the members on which a physics code fired
  (`joulewise/b5/harvest.py`, harvest pin, lines 5338 to 5438, method `neg8_corpus_physics`). It needs no
  re-measurement and no re-reduction: it re-applies the bound formula to a subset.
- **Desk code** is code that runs after the window, at the desk (the harvest, the analysis). **Collection
  code** is code that a window executes. Registration section 7.5 treats them differently: a desk defect is
  fixed and the harvest is run again on the same bytes; a collection-code change after a completed window
  supersedes the block.

## What this seat executed

- Read: the brief's rules and file-access passage; the draft, whole; the ruling, whole; the sealed
  registration (main, 6,173 lines) at lines 748 to 757, 990 to 1030, 2032 to 2035, 2848 to 2862, 3521 to
  3534, 4600 to 4650, 4960 to 5015 and by pattern search; the analysis plan by pattern search; magistrate
  brief section 9, whole; `joulewise/whole_window.py` (main) 125 to 160, 1540 to 1600, 1688 to 1730, 1823 to
  1845, 4179 to 4260, 4397 to 4405, 4439 to 4732, 6795 to 6830, 7310 to 7365; `joulewise/b5/chain.py` 40 to
  75, 176 to 275, 495 to 640, 800 to 875; `joulewise/b5/harvest.py` (harvest pin) 4275 to 4365, 4560 to 4995,
  5085 to 5135, 5215 to 5445; `joulewise/b5/driver.py` 1370 to 1416; `joulewise/b5/plan.py` 760 to 780, 872
  to 884; `scripts/run_night.py` 2100 to 2215, 4486 to 4515; `scripts/size_b5_window.py` 100 to 116, 578 to
  620, 672 to 690; `scripts/run_campaign.py` 1300 to 1385, 3105 to 3135, 8311 to 8345;
  `scripts/rehearse_b5_real.py` 90 to 102, 285 to 317; the seal's `make_sealed_inventory.py`, whole;
  `tests/test_b5_seal_landing.py` by pattern; the floor generator and the contrast generator at the lines of
  draft finding F1; `scripts/write_b5_identity_pins.py` 500 to 535; `joulewise/identity_pins.py` 262 to 273;
  `joulewise/aggregate.py` 36 to 80; the ALPHA plan tree's stage graph and external inputs; the corpus
  directory.
- Computed: an independent simulation of the bound (200,000 synthetic corpora at each size, my own script,
  a different seed); the detection power of the screen at three corpus sizes; the draft's synthetic example,
  binomial table, spans, deadlines and disk figures; SHA-256 of the two settled-corpus manifests and the two
  order manifests; `git merge-base --is-ancestor` for the harvest pin and for H_claim against main; `git diff
  --stat` of H_claim against main and against the harvest pin.
- Window files opened: the plan-time `night_plan.json` of ALPHA attempts 1 and 3 (two integers, `t0_epoch_s`
  and `window_max_s`), and the contention journal of attempts 1 and 3, by a program that printed interval
  counts, interval offsets and the process names of at most eight intervals. Nothing else under a custody
  root, a runs root or an archive.
- **Not executed:** any test; any generator; the sizer; a chain render; the reducer (so finding 3 rests on
  the registration's words, not on a trace of the precheck code); the runner lines the draft cites for the
  retry (the judge verified them in the ruling); the draft's test list of section 4.7 (not checked line by
  line). The scratch scripts were under `/tmp/refuter_c18/` and are deleted.

---

## Findings

### 1. BLOCKER. Question J1 leaves out the option that restores the sealed bound with no change to any code a window executes

**What the draft says.** J1 offers (a) the bound from every kept member, n from 10 to 18; (b) the bound from
the first 12 kept, which "needs code in the chain's prune helper (collection code) and in the harvest's
subset test and physics drop"; (c) a smaller corpus.

**What is wrong.** Option (b) does not need the chain. Under draft finding F2 (which I confirm, finding 11)
no block-5 window can be judged by route 1: the bound the chain writes in the window is authenticated by
nobody but the harvest, and the harvest's own re-screen decides every window. So the in-window bound is
already a diagnostic. The bound that decides can be built at the desk, and the harvest already has the
machinery: `neg8_corpus_physics` takes the in-window bound's recorded members, removes the flagged ones,
writes the reduced manifest to `derived/neg8-clean-corpus.json`, calls
`whole_window.build_neg8_drift_bound_artifact` on the rest, validates the result against the reduced manifest
and hands it to the re-screen (`harvest.py`, harvest pin, 5387 to 5424); the allowance consumer already
authenticates such a bound against its own manifest (`whole_window.py` 7337 to 7359, the
`corpus_physics_clean` branch).

**The missing option, call it (d).** All 18 members run, the chain prunes and mints exactly as under (a),
and no collection code changes. At the desk the harvest removes the members on which a physics code fired,
as now, and then keeps **the first 12 of the remaining members in committed order**; if fewer than 12
remain it keeps all of them (10 or 11), and below 10 the window is removed, as now. The clean bound is built
from those. Membership is decided by committed position, status, the mint's five reasons and the six physics
codes, never by an energy beyond what the sealed rule already allows (finding 3). "Pulling the next member
in" after a physics drop, which the draft lists as new logic, is free: the cap is applied after the drop.
The code change is in one desk method (run the clean-bound path always, not only when a member was flagged;
truncate the kept list and the manifest rows to 12; record the members beyond position 12 in
`derived/neg8-corpus-physics.json`). No flag code is added, so the catalog does not change.

**Why it matters.** My simulation (below) gives the first 12 of 18 a mean bound of 2.36 σ and a
no-drift failure rate of 1.3%, the sealed rule's operating point, against 2.82 σ and 0.3% for all 18. And the
choice between (a) and (d) changes no byte a window produces, so it does not enlarge the collection-code
diff, the seal or the first arm's risk. A defect in it is a desk defect, cured by a re-harvest on identical
bytes (registration 7.5, third bullet).

**Fix.** Add option (d) to J1 with its true cost, and correct the cost stated for (b).

### 2. BLOCKER. The seal steps cannot be carried out as written: the sealed text names H_claim, and the draft assigns the text edits to no commit

**Evidence.** The sealed registration names H_claim by its commit hash at lines 1650 and 5542, the three
plan-tree digests at lines 750 to 756, the digest of `identity_pins.json` at lines 2523, 2524 and 5690, and
the digest of `sizing_b5.json` at lines 3026 and 3027. The new H_claim is the merge commit of the build, so
its hash does not exist until after the merge, and a file cannot name the commit that contains it
(`make_sealed_inventory.py`, docstring). The first seal solved this by putting the sealed text into the seal
commit: `ab7b21e57` has H_claim as its only parent and changes three files, the inventory, the registration
and the analysis plan (`git show --stat`). The draft says the opposite twice: section 4.3 row 22 and section
7 item 4 have the inventory "committed alone as the seal commit". Its section 4.5 edit list does not contain
lines 750 to 756, 1650, 2523, 2524, 5542 or 5690. Magistrate brief section 9 step 2 also says "commit that
one file", but that step was written for a cure that leaves the registration's text alone.

**Consequence.** Followed literally, the build seals a registration that still names the old H_claim and the
old plan-tree digests, or it edits the registration after the seal commit, which the landing test's rule
(the seal commit is the last commit that changed the inventory, and its only parent is the head it names;
`tests/test_b5_seal_landing.py` 97 to 110) does not forbid but the seal record's pin of the text would then
miss.

**Fix.** State that the new seal commit carries three files, as the first one did: the regenerated inventory
and the two amended documents, with every self-referential value (H_claim, the three plan-tree digests, the
sizing digest, the identity-pins digest) written at that point. Add the missing lines to section 4.5. Say
that this departs from the brief's "that one file" and why. The inventory's roots do not include
`configs/campaigns/v5_claim_25g83/` except the flag catalog (`scripts/rehearse_b5_real.py` 285 to 290), so
the landing test accepts a three-file seal commit, as it did on 2026-10-08.

### 3. BLOCKER. "No step looks at a member's energy to decide whether it stays" is not true of the sealed rule, and 18 members widen the room

**What the draft says.** Section 2.2: "No step looks at a member's energy to decide whether it stays."
Section 3: "None of these reads the size of a member's energy."

**Evidence.** One of the mint's five registered reasons for leaving a succeeded corpus member out is
`precheck_ineligible`: "the fresh re-reduction's gross or idle-subtracted precheck is not eligible"
(registration 5.3, line 2860; `whole_window.py` 4037, 4125, 4397 to 4405). The registration says elsewhere
that a precheck can depend on an energy: "a precheck can turn on an energy test" (line 2034); "whether a
precheck is eligible can turn on the energy envelope" (line 3532); the test is named at line 3525,
`anchor_energy_envelope_exceeds_quarter_metric`, which compares a member's timing-uncertainty envelope with a
quarter of its energy. A member with a smaller energy fails such a test more easily. I did not trace the
reducer to see which precheck tests a corpus member's gross and idle-subtracted gates include; the
registration's own sentences are the evidence, and the builder or the judge should settle it by reading
`whole_window._reference_energy_evidence_detail` (line 4049 onward).

**Why 18 matters.** Under the sealed rule at most two members can be left out, for all reasons together,
before the window is removed. Under the new rule eight can. If `precheck_ineligible` removes low-energy
members more often than others, it trims the low end of the corpus, the envelope shrinks, and the bound and
the drift allowance with it. That direction is not the cautious one for the allowance. The registered guard
against a selected corpus (a succeeded member left out for any other reason removes the window) does not
touch this, because this reason is on the accepted list.

**Fix.** Replace the two sentences with the true one: membership is decided by status, by the mint's five
validity reasons, one of which (`precheck_ineligible`) can depend on the member's own energy relative to its
timing uncertainty, and by the six physics codes. Add to the analysis plan's disclosures, for after the
release event: for each window, the number of corpus members left out by each reason. Add a rule the judge
can accept or strike: a window in which `precheck_ineligible` left out more than two corpus members is
disclosed as such beside its allowance. Under option (d) of finding 1 the exposure is the same as under (a),
so this finding does not choose between them.

### 4. MAJOR. Section 2.5 is right, and the ruling's "it tightens" is wrong; the draft understates what the wider screen costs

**The formula.** Registration 0.12, lines 1001 to 1008, states the bound exactly as the draft's section 2.4
does. The code that computes it is `whole_window.build_neg8_drift_bound_artifact`, inner function
`family_estimator` (`whole_window.py` 1559 to 1579): `replicated_range` is the mean of the last three minus
the mean of the first three of the sorted energies (1567 to 1570), `replicated_prediction` is t × s × √(2/3)
(1571 to 1575), and the bound is the larger (1576). For other endpoint counts `neg8_count_adjusted_bound`
does the same with the realised counts (1945 to 1956). The multiplier comes from `aggregate.py` 41 to 59;
2.262, 2.201 and 2.110 are its entries for 9, 11 and 17 degrees of freedom. The draft's formula is the
registered and the coded one.

**The simulation, independently.** 200,000 corpora at each size, draws from a normal distribution with
standard deviation σ = 1, Python `random.Random(4242).gauss`, the table's multipliers:

| n kept | mean envelope | mean repeatability term | mean bound | envelope is the larger term | bound ÷ (σ√(2/3)) | a no-drift window fails |
|---|---|---|---|---|---|---|
| 10 | 2.130 σ | 1.796 σ | 2.131 σ | 99.1% | 2.61 | 2.64% |
| 11 | 2.251 σ | 1.774 σ | 2.251 σ | 99.9% | 2.76 | 1.85% |
| 12 | 2.357 σ | 1.755 σ | 2.357 σ | 100.0% | 2.89 | 1.37% |
| 14 | 2.540 σ | 1.729 σ | 2.540 σ | 100.0% | 3.11 | 0.73% |
| 15 | 2.620 σ | 1.720 σ | 2.620 σ | 100.0% | 3.21 | 0.59% |
| 16 | 2.693 σ | 1.711 σ | 2.693 σ | 100.0% | 3.30 | 0.48% |
| 18 | 2.824 σ | 1.698 σ | 2.824 σ | 100.0% | 3.46 | 0.27% |

Every cell of the draft's table is reproduced to the printed digit. Its synthetic example is reproduced
too (0.5933, 0.6233 and 0.5367 J), and so is its binomial table.

**What the draft does not show: the screen's power.** The chance that a true shift of the end triplet by δ
fails the screen (60,000 corpora per cell, same script):

| true shift δ | n = 10 | n = 12 | n = 18 |
|---|---|---|---|
| 1.5 σ | 26% | 19% | 8% |
| 2.0 σ | 45% | 36% | 19% |
| 2.5 σ | 65% | 56% | 37% |
| 3.0 σ | 82% | 75% | 58% |
| 3.5 σ | 92% | 88% | 76% |
| 4.0 σ | 97% | 95% | 89% |

A shift of three standard deviations of one member, which a 12-member window removes three times in four,
passes an 18-member window more than four times in ten.

**A second effect the draft does not show.** A drift inside the corpus itself widens the envelope, and more
so for a longer corpus, because 18 members span half as much time again as 12. With a linear drift of 0.1 σ
per member the mean bound is 2.51 σ at n = 12 and 3.20 σ at n = 18; at 0.2 σ per member, 2.92 σ and 4.13 σ
(40,000 corpora per cell). So a drifting instrument relaxes its own screen, and under (a) it relaxes it
faster.

**Does the allowance fully compensate?** By the registration's text, yes for validity. The allowance is
max(spread, bound(n_s, n_e)) (lines 1021 to 1024); the window passes only when the screen statistic is at
most the bound; so a drift that passes is never larger than the allowance; each member carries half of the
allowance and a contrast carries it once in total (lines 1024, 1025); and the allowance uses the
realised-count bound on passing windows too (line 1025). No claim becomes false because the screen passed a
drift that a 12-member corpus would have caught. What is not compensated is sharpness and comparability:
every claim of every window carries a floor of about 2.8 σ in place of 2.4 σ whether or not anything drifted;
GAMMA's decisions are made on a quantity that contains the allowance (analysis plan line 132), so a real
difference is harder to show; and the screen's level now depends on how many members the window lost, so
three windows of one block are screened at three different levels. Option (a) buys nothing for this price:
the extra six members exist to absorb losses, not to change the bound.

**Fix.** Keep section 2.5. Add the power table and the in-corpus drift sentence. In the fourth bullet of
"What this means", replace "The claims stay honest; they get less sharp" by the two-part statement above.

### 5. MAJOR. "May lose up to eight members" holds only for three kinds of loss; one member of a fourth kind still removes the window

**Evidence.** The mint keeps, omits or refuses. A member whose evidence cannot be classified is
*indeterminate* and is kept, and a corpus with any indeterminate member derives no bound
(`whole_window.py` 4669 to 4674). A member with a launch-lineage fault, a configuration that is not the
canonical one, no recorded calibration identity, or an invalid file inventory is a *refusal*, and one
refusal raises (`_raise_on_refusals`, 4588, called at 4667; the reasons at 4498 to 4541). In the chain, when
the mint's drop function raises, the prune helper falls back to the status-only rule
(`chain.py` 603 to 612) and the derivation stage then fails. So the margin of eight covers a member that did
not succeed, a member omitted for one of the five reasons, and a member dropped for physics. It does not
cover an indeterminate or refused member, and with 18 members there are half again as many chances of one.

**Fix.** In the new title of registration 5.3 and in draft section 2.1 item 3, say which losses the eight
absorb and that a single indeterminate or refused member still gives `neg8.bound_not_derived`. Neither chain
so far showed one (attempt 1 derived a bound; attempt 3 failed on the count). The rehearsal of finding 9 is
the desk check.

### 6. MAJOR. Under the draft's own answer to J6, the harvest that will judge the windows is not the harvest the build tests

**Evidence.** I confirm the draft's facts: H_claim `a64000884` is an ancestor of main; the harvest pin
`7e6158d66` is not; main differs from H_claim under `joulewise/`, `scripts/` and `configs/` in the three
seal documents only; the harvest pin differs from main by 598 diff lines in `joulewise/b5/harvest.py` and by
80 added lines in `joulewise/whole_window.py`, all in the reference-loss path
(`_neg8_writer_reference_energy`, `_derived_neg8_decision`) and none in the mint. So if the new H_claim is
built on main, main's `harvest.py` is the pre-lane version, and the draft's "tests to add" (ii) and (iii)
(section 4.7), which test the harvest, and its edits to `tests/test_harvest_b5_window.py`, would run against
a harvest that will never judge a block-5 window. The lane's copy of that test file has 644 more lines, so
the edits will also conflict when the lane takes the new seal.

**Fix.** Keep the draft's recommendation (the new H_claim keeps H_claim's two files; the window's code stays
byte-identical to what ran), and add to section 7: the harvest lane merges the new seal commit; the harvest
tests for 18 members, and option (d) if ruled, are written and run on that lane; the whole suite runs on that
desk tree as well; and the harvest pin addendum is written **before the first arm**, not "before the new
ALPHA attempt 1 is harvested", so that the rehearsal of finding 9 is harvested by the pinned program.

### 7. MAJOR. No gate checks the amended sealed text against the ruled erratum

**Evidence.** Section 4.5 lists about thirty hand edits to a 6,173-line registration and one to the
analysis plan, and (finding 2 and minor 12) the list is incomplete. Section 7 gates the code and the inputs.
It names no reader for the text. The draft's own preamble shows the hazard: the ruling quoted line numbers
from an unsealed draft of the registration. Registration section 10 requires that a rule or roster change
be "a prospective cold erratum"; the erratum is this file, but what binds the windows is the edited
registration.

**Fix.** Add one gate: before the seal commit, the cold Fable pass of item 1 is given the diff of the two
documents and checks it against the ruled erratum, edit by edit, plus a search of both documents for every
remaining statement of 12, 119, 101, 126, 108 and the old digests. One reader, one pass; it needs no new
seat.

### 8. MAJOR. Question J5 should be answered the other way: leave `chain.py` alone

**Evidence.** With J3 as the draft assumes and J6 as it recommends, the three strings of J5 are the only
edit to a file that a window executes. `DEVIATIONS` is a tuple of adjacent string literals
(`chain.py` 245 to 275), where a dropped comma merges two entries without an error, and line 1198 is text
rendered into the shell script that runs the window. The tuple and the helpers travel inside the chain's
bytes, so the chain's digest changes. The gain is a true sentence in a comment. The draft's J3 makes the
opposite trade for the calibration plans (keep the bytes, register the stale value as a deviation), and the
doctrine it cites for J7 (a finding about how something is recorded is a flag, not a fix) applies here in
the same way.

**Fix.** Leave `chain.py` byte-identical. Register a deviation: the chain script's comments and the plan's
`chain_deviations` text still say 12, 10 and 11; the stage graph says 18. Then the collection-code diff of
this supersession is: generated plan trees, corpus files, generator source that no window runs, and
nothing else. The sizer's two source strings may be edited or left; the sizer is desk code and its output is
regenerated in any case.

### 9. MAJOR. The path that will judge every window has never run to a pass on real bundles; the rehearsal of J9 must be required and must go through the harvest

**Evidence.** With F2, every window is judged like this: the chain mints a bound from the collected
members; the desk verdict writer finds no bound and stores a failed screen with the two "bound underived"
conditions; the harvest validates the bound against the collected manifest, re-derives the stored bracket,
requires that its re-derivation reproduce the stored one, and screens again
(`harvest.py`, harvest pin, 4915 to 4944 and 5229 to 5300). On real bundles this has run once, in ALPHA
attempt 1, and stopped before the re-screen because a physics drop left nine members. The draft reports that
both real-model rehearsals kept one corpus member and their derivation stage returned 2. So the re-screen
has never passed, or failed, on real data, and the in-window prune and mint have never read more than 12
real bundles. The two sizing charges of F4 rest on an estimate the registration calls "never measured live".

**Fix.** Rule J9 "required", and widen it: all 18 corpus members, the full start triplet, midpoint and end
triplet, harvested by the pinned harvest program until its record shows the re-screen evaluated. Record the
wall time of the prune and of the derivation. It is a rehearsal under `REH-` ids, not a claim window.

### 10. MAJOR. Section 6 lets an open-ended runner fix into this seal

**Evidence.** Step 4 of the reproduction plan says a fix in the runner "rides in this same seal if it is
needed". The runner is collection code that both completed chains executed. The defect removed nothing in
either window (the harvest kept every unit). Its cause is not known, so the size of the fix is not known,
and the draft sets no limit on the search (step 3 widens it to two more full stages).

**Fix.** Bound it. The reproduction is the one rehearsal of finding 9 with the stage kept whole (20 more
member cycles). The runner is changed in this seal only if the cause is shown to alter a byte or a status
that the harvest reads; otherwise the wrong log row is registered as a known wrong record with its
explanation, and the arm does not wait for it. Say so in section 6 and make it part of J7.

### 11. MINOR (confirmation). F2 is true, and it does not break the claim path

The core reader's path is the historical directory (`whole_window.py` 150 to 157, used at 1710 to 1713 when
no bytes are passed; `load_neg8_drift_bound_artifact` passes none, 1841 to 1843). The two manifests are
byte-identical today (both `74ccdaec…`, computed here). The whole-window verdict is a desk step, not a chain
stage (`chain.py` 147, `DESK_KINDS`; the ALPHA plan tree's stage 15), so no code a window executes reads the
bound through the core reader, and the mint binds the bound to the bytes it was given (4697 to 4724). When
nothing is dropped the collected manifest is the committed file byte for byte (`chain.py` prune helper,
"if dropped: raw = render(...)"), and the harvest's subset test accepts an equal list. `whole_window.not_passed`
is disclosed only and is already expected on most windows, because any one member's admission failure sets
it (`harvest.py` 4862 to 4864). Three things to add to the text: (i) on the collected-subset route with no
harvest loss, the stored bracket must carry no NEG-8 condition other than the two "underived" ones, or the
re-screen is not evaluated (`harvest.py` 5234, 5235); (ii) the allowance consumer checks a collected-subset
bound's arithmetic and its digest against the harvest's record but not its corpus identity
(`whole_window.py` 7332 to 7336), which is the sealed behaviour for 10 and 11 members and now applies to
every window; (iii) lane L9-NEG8 part (c), claim-time code that does not exist yet (analysis plan line
729), becomes a condition of every contrast as it already is of every floor. None of the three loses a
window.

### 12. MINOR. Section 4.5 misses lines

Beyond finding 2: line 88 ("only 10 or 11 of them"), 3094 and 3110 (the two worked sums "119 × 236.5" and
"119 × 136.3"), 4498 ("the 101 run ids"), 5773 (Q1, "corpus of 10 or 11"), 6123 and 6153 (119 and 101 run
ids in the record of the seal's checks; leave as history and say so). Found by one pattern search of the
sealed text; the gate of finding 7 should repeat it.

### 13. MINOR. F1, F3 and F4 hold; two descriptive fields are treated inconsistently

F1: the literals are where the draft says (floor generator 241, 246 to 248, 727, 1818, 2851; contrast
generator 2056, 2365; the twin differs at line 21 only). The contrast generator reads the manifest's own
count and digests (2177 to 2180, 3383 to 3388). No Python file under `joulewise/`, `scripts/`, the
generators or the tests holds the corpus id or the order manifest's id as a literal (searched), so the new
names of J8 break no comparison. F3: no file under `joulewise/` or `scripts/` reads `planned_bound_bundles`
or `bound_count` (searched). But the draft leaves the first at 12 and changes the second to 18, and the
plan tree's planning estimate beside `bound_count` stays computed for 12. Either leave both and register
both, or say that `bound_count` changes because the plan tree changes anyway and the estimate is stale. F4:
the sizer's logic takes the corpus count from the stage rows (585 to 598) and the two 320 s constants are
the only values chosen for 12 (112, 113).

### 14. MINOR. `identity_pins.json` and the sealed inventory, as the draft describes them

The reference identity unit is built from the window-reference directory (20 configurations), not from the
corpus, so six more corpus files change nothing in it; the draft's row 21 is right that only the plan-tree
digests change. Regenerating it needs the same 30 reference bundles and the same interpreter as on
2026-10-07; a changed package version would change `runtime_versions_sha256`. Section 0 says the sealed
inventory "lists the SHA-256 of each code and pack file"; it does not list the corpus directory
(`rehearse_b5_real.py` 286). The corpus files are pinned through the plan trees' `external_inputs`, which
are in the inventory. Say so, so that nobody expects the six new files in the inventory.

### 15. MINOR. The dead-man job's daily firing time moves

The dead-man is the scheduled job that stops a window which overran. Its schedule keeps only the hour and
the minute of t0 + `window_max_s` + 3,900 s (`run_night.py` 2105 to 2110 and 2206, 2207), so it fires every
day at that clock time and stands down when it is early (4499 to 4506). First firing after t0, computed
here: ALPHA 19,680 s under the old seal and 27,720 s under the new; BETA 22,080 s and 30,120 s; GAMMA 8,520 s
and 16,560 s. For ALPHA and BETA the firing moves from about the end of the chain to well after it on the
projected basis. For GAMMA it stays inside the chain and moves toward its end (the projected chain is
18,244 s). One observation says an early firing is harmless: in ALPHA attempt 1 the journal interval that
contains second 19,680 lists no outside process over the limit. Desk check before GAMMA: compare 16,560 s
with the rendered stage order and confirm it does not fall in the end triplet; if it does, shift t0 by a few
minutes.

### 16. MINOR. What 18 members do to the first hour

The start triplet begins 14 to 24 minutes later (the draft's own figures) and the corpus spans about 41
minutes of member cycles in place of 27. In attempt 3 every run of four or more dirty intervals ended by
interval 326, minute 54. So the start triplet and the first science stage move out of the dirty hour, which
helps them. Thermal state: six more identical small-model members precede the start triplet under the same
cooldown rule; I see no mechanism by which that harms the science members. The collection deadline, the
24-hour calibration horizon, `window_max_s` and free disk are not at risk (the draft's arithmetic in section
4.6 reproduces: 106,890 and 110,220 s; 109,290 and 112,620 s; 95,754 and 99,060 s; 25,190,989,824 bytes).

### 17. MINOR. Gates of section 7 compared with the ruling and the brief

Present and required: the six merge keys, the diff-scoped #416 re-audit (registration 7.5 requires it), the
new inventory and seal commit, `tests.test_b5_seal_landing`, the new clone with ledger and pin, the desk
seal check, the dry render. Missing: the text gate (finding 7); the harvest-lane gate (finding 6); the
ruling's Q2 (ii) checks after the restart (the three disabled agents, no such process, changed boot time,
watchdog loaded); a check that the macOS build is unchanged after the restart, because registration 7.5
requires one build for all three windows. Unnecessary: none, but the independent executing review and the
diff-scoped re-audit have the same object if finding 8 is accepted (generated plan trees and generator
source); one brief can serve both.

### 18. MINOR. Procedure item (a) invents a threshold

"Below about 100 entries and 1 GiB it passes" is not in the ruling, which asks for the entry count after the
scratch is removed. A threshold with "about" in it cannot be applied. Either give two exact numbers and
their reason, or keep the ruling's wording. The draft also records that the scratch could not be moved, so
the fallback (no span containing 00:00 local) is in force until the restart; say that in the arm procedure,
not in a parenthesis.

### 19. MINOR. Supersession and attempt numbering

Section 5 applies registration 7.5 correctly: both completed chains executed the plan tree and the corpus
manifest that change, so the block is superseded, and section 10 requires the prospective cold erratum.
Add one sentence on the re-arm rule: whether the three superseded attempts count when rule 1 of the brief
compares the causes of two attempts of a pack. They should not count toward it and should all be printed in
the attempt history.

---

## Answers to J1 to J10

**J1.** Rule option (d) of finding 1: all 18 run; the deciding bound is built at the desk from the first 12
members, in committed order, that succeeded, passed the mint and carry no physics code (10 or 11 if fewer
remain; below 10 the window is removed). Reasons, option by option:

- *(a), all kept, n 10 to 18.* A valid rule and the cheapest build. As an estimator of "the largest
  start-to-end difference repeatability could produce" it is the worst of the four, because its level is
  not fixed: the envelope is an extreme of the sample, so it grows with n (2.13 σ to 2.82 σ) and the
  no-drift failure rate falls from 2.6% to 0.3% with it. It selects nothing on an energy. It is biased only
  in the sense that n, and so the bound, depends on how disturbed the first hour was. Its cost is a drift
  allowance about 20% larger in every claim and a screen with much less power (finding 4).
- *(b), first 12 kept, built in the chain.* The same estimator as (d), with a collection-code change that
  (d) shows to be unnecessary. Highest build risk. Do not rule it.
- *(c), 15 members.* Pays both prices in part: bound 2.62 σ, and by the draft's formula 0.93 chance of
  keeping 10 at the observed loss rate against 0.994 for 18, with room for about two bursts where 18 has
  four. Do not rule it.
- *(d).* Keeps the sealed operating point (2.36 σ, 1.4%) whenever 12 clean members exist, and uses the six
  extra members only for what they were added for. Membership by committed position, status, validity and
  physics; no more exposure to an energy than (a) has (finding 3). Cost: one desk method and its tests, on
  the harvest lane; no change to the seal, the clone or the window. The first 12 are also exactly the
  sealed corpus when nothing is lost, so the continuity with the registered rule is complete.
- *Not recommended now:* dropping the envelope and screening on the repeatability term alone. It is the
  only term with a fixed 95% level and it does tighten with n, but it changes the registered formula in the
  core and would fail about 5% of clean windows in each of the two energy families.

If the judge will accept no new desk logic before the first harvest, then (a), with the power table printed
in the registration and n beside every window. The first arm does not depend on this choice.

**J2.** Yes: route 2 for every window, no change to `whole_window.py`. The core reader is not on any
in-window path, the route is the registered one for 10 and 11 members, and a core change would alter a file
both completed chains executed for no gain in what is measured. Condition: finding 9.

**J3.** Yes, leave `planned_bound_bundles` at 12 as a registered deviation. Nothing reads it, and 280
science configurations that are byte-identical to the ones already run are worth more than a true
descriptive field. Treat `bound_count` consistently (finding 13).

**J4.** Yes, leave both constants at 320 s. The span has more than 70,000 s of margin and the wall budget is
1,800 s for each. Add: the rehearsal measures both times, and a measured time above 1,200 s for either goes
to a consult before the arm.

**J5.** Leave `chain.py` alone and disclose (finding 8). The opposite of the draft's recommendation.

**J6.** The second choice: the new H_claim keeps H_claim's `harvest.py` and `whole_window.py`, and the desk
gets a new harvest pin built on the new seal. It is the safer one because the code a window executes stays
byte-identical to what ran in two full chains. Conditions in finding 6.

**J7.** Leave the driver's count; record it as a flag. It touches no number. Bound the larger defect of
section 6 as in finding 10.

**J8.** Accept the three names. No program compares the corpus id, the manifest id or the manifest's
`plan_id` with a fixed string (searched), the harvest compares the collected header with the committed one
and both will carry the new id, and the historical directory keeps the old id for the old 12.

**J9.** Required, and through the harvest (finding 9).

**J10.** Yes, attempt 1, with the three superseded attempts listed separately. Keep the plan-id pattern the
tools already produce (the time stamp makes it unique); I did not check whether any program parses a block
marker, so do not add one without that check.

## The three most likely ways the first arm from a new clone fails, and the cheapest desk check for each

1. **The window runs its whole span and is removed for `code.executed_differs_from_sealed`.** A new H_claim,
   a regenerated inventory, a three-file seal commit and a new clone are each done by hand for the second
   time ever, and the brief says the ledger carry-over has never been rehearsed. Check: in the new clone,
   run `tests.test_b5_seal_landing`, then recompute every digest in the inventory from the clone's working
   tree (not from git objects) and compare; run the desk seal check; confirm the clone's interpreter gives
   the pinned `runtime_versions_sha256` (hand-off runbook step 4, lines 339 to 342). Minutes, no load.
2. **The corpus stage or the derivation fails in the first hour.** Six hand-made configurations, two
   hand-edited manifests and hand-edited generator literals feed the first collection stage; the mint has
   never read 18 real bundles; one refused or indeterminate member removes the bound (finding 5). Check: the
   rehearsal of finding 9, run **from the new clone**, with all 18 members. It exercises the runner on rows
   13 to 18, the prune, the mint and the two wall budgets.
3. **The window collects cleanly and the harvest cannot pass it.** Route 2 has never reached a re-screen on
   real data, the harvest lane must take a new seal and a new inventory, and option (d), if ruled, is new.
   This does not lose the window's bytes (a desk defect is cured and the harvest is run again), but it
   holds the next arm. Check: harvest the same rehearsal with the pinned harvest program and read its
   record down to "re-screen evaluated".

A fourth, cheaper than any of these to check: the arm refuses because some pinned digest was not
regenerated (the pin registry, the sizing file's plan-tree digests, the identity pins). It costs no window,
and each generator's `--check` in section 4.4 of the draft catches it, provided the builder records every
exit code as the draft asks.
