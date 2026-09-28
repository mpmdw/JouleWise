REFUTER: DISSENT

# Opus 5.5 contract-lens refuter on cold ruling CAP-COUNCIL-25G83-01

Ruling under test: `21-coldgate-fable-ruling.md`. I recomputed its sha256 prefix as `a90b6e768a2137f1`. The charge and seat digests match what the ruling lists: `286ed102…`, `ccefaad5…`, `f059a50a…`, `6f3bf12c…`, `8f13b894…`, `b0195359…`.
Code tree: `/Users/edr/code/JouleWise-wt-d138-scout-d528efb2` at `c772b019`. I checked that main `e7c8bcc6` is an ancestor. The four estimator digests and the registration digest (`81b65f08…`) match the ruling.
Scratch: `/tmp/cg-cap-d528efb2/opus-refuter/`. It holds `replay.py` (the judge's `mytiming2.py`, copied unchanged, `f4f8e424…`), `cells_all.py` (`8c0bbbf5…`) and `replay-results.txt` (`8f0e0398…`).

**Disclosure.**
- I read the owner's memory note for directive #416 and its repository record (cited under B4). The cold judge was barred from both; I was not.
- I have seen the B values printed in the gate ruling and in the registration. I also saw one historical B printed in an August record (probe 6, 67.2 ms; see B2).
- My replays print cell counts, frame lengths and times, plus a true/false flag for "stored B reproduced". They print no B.
- I modified no repository file, ran no capture and no powermetrics, and changed no setting. `sudo -n -l` only lists permissions; it executes nothing.

## What I verified and found as the ruling states

- **Stopping at the cap changes no number.**
  - `consume_cell` only counts and raises (`joulewise/powermetrics_fiducial.py:533–550`).
  - The wall-clock budget starts before pulse fitting (`:976–979`).
  - Partial fits are discarded (`:992–1010`).
  - The split is binary, from a 1.5 s square (`FIT_HALF_RANGE_S = 0.75`, `:75`) down to 0.1 ms (`:686–695`). That gives 2^14 per axis, so 2^28 leaves and about 5.4×10^8 cells in all.
- **Replays.** I re-ran w1-d03 with the cap lifted: 170,965 cells, 129.645 ms median frame. I re-ran n1-d01: 47,383 cells, 244.286 ms, stored B reproduced. Both equal the ruling's §2 table.
- **Time-daemon log.** `/tmp/cg-cap-d528efb2/timed-mine.txt` holds 70 applied corrections, 18 of them ≥ 1 ms. The +53.198 ms (01:53:09), +4.386 ms (02:20:42) and −35.939 ms (10:11:29) corrections are present. The −1.262 ms correction at 00:39:52 is also present.
- **Registration.** Line 612 is a window-level stop at 150 ms. Lines 620–628 are per-interval (single-frame) statistics.
- **Clock-method code.** `uncertainty_evidence.py:40` sets the 5 ms span limit. Lines `:74–81` hold the separate 15 ms v3.1 backstop. Lines `:891–909` state the one-rate model and require network time OFF.
- **Writer staleness check.** The capture writer refuses a stale artifact (`scripts/validate_powermetrics_fiducial.py:397–402`). The ruling's inference in §5 item 2, which it did not execute, is therefore correct: new windows need an artifact whose pins name the running code.
- **Seat positions.** The §4.2 table represents each seat's position faithfully.

## BLOCKER

**B1. R5 (the stop-time check) gives different verdicts for the same bytes, depending on machine load.** It cannot serve as a pre-registered refusal rule.

- **Measured.**
  - The judge measured 11.11 µs per cell and 12.56 s outside the cell loop. On those figures, R5 reads 31.6 s and passes (§4.3, worked example).
  - I replayed w1-d03 on the same machine 20 minutes later, at load average 15. I measured 27.32 µs per cell and 33.23 s outside the loop. R5 then reads 33.23 + 1,710,000 × 27.32 µs = **79.9 s > 60 s, so the rule refuses** (`replay-results.txt`).
  - The ruling says that "any factor from about 5 to 25 passes both" checks (§4.2 item 5). On my figures, factor 10 fails and factor 5 passes by 3 s.
  - R5 names neither the load condition nor a repetition rule. Re-running the timing until it passes is therefore allowed. That is a forking path inside a rule meant to fix the value.
- **Registered design intent.**
  - The decision log says the cell count is "the primary deterministic mechanism; the deadline is only a host-safety backstop". It sizes that backstop at "about 440x per-cell slowdown" before the deadline can preempt the cap (`docs/decision_log.md:10162–10174`).
  - R5 keeps a 2× margin at best. Under load, a flat-surface capture at 1.71 M cells would take about 80 s against a 120 s deadline, a 1.5× margin. A runaway could then end on the wall deadline, whose record is marked `reproducible: false` (`powermetrics_fiducial.py:1536–1539`).
- **Change.**
  - Measure t and T under a stated condition. Either use the timings the window writer records in the R9 windows (a quiet machine, the real operating condition), or use a named benchmark with a fixed repeat count and a named statistic. Commit the conditions with the rule.
  - Add a synthetic flat-surface stop-time test at the new value, as the Opus seat's (g) did. R6's cited test uses an injected budget of 31 cells.
  - Either justify, in writing, giving up D-078's backstop margin, or pick a factor that keeps a margin of an order of magnitude under the stated load.

**B2. The ruling misses a prior magistrate ruling and a recorded capture that sit exactly on its design choice.**

- **The prior ruling.** On 2026-08-18 the magistrate ruled "OPTION B — 165,000 UNCHANGED … rationale: budget exists to admit corpus-grade captures; the family screen refuses probe-6-class captures regardless; Option A's 1.55M makes the 120 s wall the binding guard → host-dependent failures" (`docs/process_traces/2026-08-18-t10-t11-working-notes/trace-notes.md:405–411`). That rationale is carried into every issued n17 artifact (`configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:525–526`).
  - The ruling's 10× cap (1.71 M) is the rejected Option A, give or take 10 %.
  - The ruling's §4.1 says "the cap exists for one reason" (a runaway guard). The record gives a second reason, and the ruling neither cites it nor overrules it.
  - The charge asked for the cap's purpose "in code and history".
- **The recorded capture.** Validation probe `20260818T182149-a7e8b412` ("probe 6") resolves its anchor, needs **1,282,827 cells** and printed B = 67.2 ms, 2× out of family.
  - It is the one datum between healthy work (about 10^5 cells) and a flat pulse (about 5×10^8). The §4.1 scale diagram omits it.
  - Under the new cap it would fit, at 0.75 of the cap, and trip R8.
  - It is not on the R2 roster, and R2 does not say why. If it were, N_max would be 1,282,827, the cap 12.83 M, and R5 would refuse (12.83 M × 11.1 µs ≈ 142 s).
  - So the roster boundary, chosen after the counts were known, decides whether the rule works.
- **Change.**
  - Write the roster's inclusion principle before replay. One option: "every retained protocol-v3 capture on this host whose anchor resolves, validation-only probes included / excluded, because …".
  - Confront Option B explicitly: overrule it with reasons, or adopt its admission purpose.
  - State what the successor corpus does with probe-6-class captures that now finish. They raise S (the spread of the members' B values), and the Revision 5 arithmetic has no predecessor screen veto.

**B3. The order in §6 contradicts R1, and the rule for admitting waiting branches breaks D-138.**

- **Order.**
  - R1 requires the four files frozen "before any replay", with "the frozen bytes … the bytes that will ship".
  - §6 step 3 runs the roster replay and computes the value. Step 4 then builds the branch and admits waiting estimator branches.
  - Two of those branches change `powermetrics_fiducial.py` (`bda7ffe0`, `ea10e3c8`; 62 and 63 changed lines against `e7c8bcc6`). The value would therefore be computed on bytes that do not ship.
  - Step 5's "repeat step 3's replay if a pinned byte moved" covers audit fixes only, not step 4.
- **Admission test.** Step 4 admits "each waiting estimator branch that passes this test" (member B values identical, dispositions unchanged).
  - D-138 consequence (1) requires each such branch to "complete [its] C-028 gauntlet normally" (`docs/decision_log.md:10371–10374`).
  - The branches' own commit subjects say they are not ready:
    - `bda7ffe0`: "unreviewed; refuter pending".
    - `aeea07b6`: "UNREVIEWED, magistrate review before any merge".
    - `ea10e3c8`: "Acceptance v4 + rev 4". That is the never-sealed Revision 4 fallback (registration:602), not a change meant to ship.
    - `5135c1d2`: "WIP [RED context] … uncorroborated".
  - A test that B does not move is not a review.
- **Change. Reorder:**
  1. The council names the branch set by commit. Only gauntlet-complete branches intended to ship are eligible.
  2. Build and freeze the combined bytes, leaving only the constant to be set.
  3. Run the roster replay and compute the value.
  4. Run the B-identity test as an extra check, not as the admission test.

**B4. C6 and step 9 do not meet directive #416 as the repository records it.**

- **The directive's binding text.**
  - The audit runs "AFTER W1/W2 pass and BEFORE any claim-bearing run".
  - Its trigger is "CLAIM-RUN WORK COMPLETE": the calibration is issued, the headline pipeline is frozen, and the audit runs at that exact commit.
  - It "includes an independent re-derivation of the calibration from the raw bundles".
  - Sources: `docs/process_traces/2026-09-25-activation-152c9255/00-activation-record.md:282,297`; `docs/process_traces/2026-09-27-activation-77b1bee2/00-activation-record.md:26–32`.
- **The ruling.**
  - Its full audit (step 5) runs before the successor calibration exists, so it cannot re-derive that calibration.
  - Its post-issuance pass (step 9) is "limited to what changed since step 5".
  - C6 closes the HOLD on "the record" of those two audits, with no pass criterion.
  - The sequence never mentions the freeze of the headline pipeline.
  - The judge did not read #416 (§9). The directive text is in the repository.
- **Change.**
  - Step 9 becomes the #416 audit at the frozen claim-run commit: full scope, three families, with an independent re-derivation of the successor calibration from its raw bundles.
  - Step 5 stays optional, as an early check that protects the new corpus from going stale.
  - C6 becomes: "the #416 audit record at commit <sha> equal to the claim-run head, every BLOCKER verified cleared."
  - Insert "headline pipeline frozen" before step 9.
  - §8 item 4 then needs no question to Ed.

## SHOULD-FIX

**S1. §8 item 1 is wrong: no owner action is needed.** The passwordless network-time switch is already installed. What is missing is engineering.

- **Installed.**
  - `/etc/sudoers.d/joulewise-network-time` is present, dated 2026-08-17. Its 296 bytes match the size of `scripts/joulewise-network-time.sudoers`.
  - `sudo -n -l` lists `(root) NOPASSWD: /usr/sbin/systemsetup -setusingnetworktime off, … on`.
- **Code that already exists.** `joulewise/quiet_predicate_campaign.py:343–395` (`establish_network_time_off`, `restore_network_time`) and `:695` (`attest_network_time`, which reads the `timed` log per capture).
- **What enforces it today (question 5): not the derivation path.**
  - `scripts/night_chains/calibration_derivation_only.zsh` has no network-time control. The registration pins its chain digest.
  - The pack-bearing arm path has a `clock.network_time_off.v1` row (`joulewise/arm_readiness.py:967–970`).
  - The 09-22 record says that row "did not govern the evidence-night entry point" (`docs/process_traces/2026-09-22-activation-22666c9f/01-qpe01-pilot-n1-20260922-0217-harvest-record.md:185–197`).
- **Change.**
  - Replace §8 item 1 with an engineering lane before step 7. Wire the existing functions into the derivation chain and into the claim-window arm path, with a refusal when network time is not OFF. The chain digest will change, so the successor registration pins the new one.
  - Add "K2 refusal implemented and tested" to the closing conditions.
  - Asking Ed to do this manufactures an owner stop the agent can remove itself.

**S2. K3's 250 µs threshold reopens the gap that the method closes structurally.**

- The method says the one excursion its arithmetic cannot see is "a NON-affine wall excursion of at most ~250 us … excluded STRUCTURALLY, not statistically, by the authenticated network-time-OFF admission" (`uncertainty_evidence.py:902–909`). A threshold "of 250 µs or more" admits exactly that class.
- `timed` also changes the clock's rate, not only its offset. In the extract, `freq_scaled` moves from −491,728 to +409,149 at 01:53:09, about 13.7 ppm, inside W1-d08.
- **Change.** K3 becomes: "zero `timed` `apply` or `ntp_adjtime` events of any size, offset or frequency, inside any capture interval". With network time OFF the expected count is zero.

**S3. R8, R9 and C3 read per-capture cell counts that the evidence does not store, and the replay harness R0 relies on is not pinned.**

- **Not stored.**
  - Healthy evidence carries no cell count, by design: "Healthy serialized evidence remains byte-identical to the pre-budget implementation" (`powermetrics_fiducial.py:1525–1545`).
  - W1-d06's `instrument_evidence.json` has no `detection_projection` key. All six valid W1 captures read `cells []`.
- **Not pinned.**
  - `rederive_detection_from_artifacts` takes no budget argument (`:1095–1103`). Every replay therefore depends on patching the module at run time.
  - The judge's harness does not set the 3,600 s deadline that R0 prescribes.
- **Change.**
  - R0 names a committed replay harness by digest. It changes only the two budget arguments and prints no B. It is cited in C1.
  - R8 and R9 say the counts come from that harness at harvest. Alternatively, recording counts for healthy captures goes into the frozen branch before R1. That choice is a pinned-file change and may need a D-078 registry amendment.

**S4. The §2 "new finding" compares two launch contexts, not two frame lengths.**

- **The confound.**
  - The 09-19 captures ran in launch context D, where launchd uses its default process type. The registration lists them as "D, n1 night 09-19", median 247.9 ms (registration:628).
  - The issuer disposes of them for exactly that reason (`scripts/issue_calibration_acceptance_generation.py:517–520`).
  - The registration says "Launch context sets the sampler cadence; this condition is part of the registered experiment" (:608). Calling them "this same epoch" is misleading.
- **What it can support.**
  - The 440× miss shows only that no law carries across contexts.
  - It says nothing about 130–150 ms inside the registered Interactive context, which is the gap R4 covers "by the factor of ten".
- **Cost of the Opus seat's check.** On the illustration it passes: 2 × 170,965 × (150/130.2)^7.55 ≈ 0.995 M, which is ≤ 1.71 M.
- **Change.** Reword §2 and §4.2 reason 2. Either keep the Opus check as an extra refusal gate, or drop it for a reason other than the D-context data.
- **Roster.** R2 also sizes the cap from captures that R4 and R7 place outside the covered range. My replays of the two excursion captures, n1-d05 and n2-d11, need 56,289 and 52,367 cells, so they do not set N_max today. State before replay that out-of-range captures enter only as a conservative addition.

**S5. The existing issuer will refuse the successor issuance.**

- `_foreign_rows` blocks issuance when valid observations of the same epoch exist outside the registration and have no disposition (`issue_calibration_acceptance_generation.py:1430–1443,1482,1558–1562`).
- For the successor registration, W1/W2's 12 valid rows are exactly such rows.
- The disposition registry is pinned to a single decision id and mechanism: the D-context one (`:511–520`).
- §5 items 3–4 and §6 step 9 are not implementable as written.
- **Change.** Before sealing, name the route. Either the successor registration declares the W1/W2 sessions as excluded owners, or a new registered disposition is added, with its code change reviewed. Say so in §5.

**S6. No branch if the A2 addendum voids `dbad7cc7`.**

- The ruling refers the network-time question to A2 (§0 item 8, §6 step 1). A2 may rule that the 12 members are validation-only.
- In that case there is no "same 12" interim artifact.
- The writer's staleness refusal (S1 above, `validate_powermetrics_fiducial.py:397–402`) would still require some issued artifact pinning the new code before any successor window. Today the active default is r7 (`joulewise/calibration_bracketing.py:199`).
- **Change.** Add the contingency: which artifact is re-pinned inside the cap transaction if `dbad7cc7` does not issue.

**S7. Not every closing condition can be checked mechanically, and two are missing.**

- **C1.** A commit order cannot prove that the replay ran after the rule was committed. Require the replay record to embed the rule digest, the roster digest and the harness digest, in a descendant commit.
- **C3.**
  - Name both zero-stop counts: cell count and wall deadline.
  - Say whether out-of-range captures count toward the 24, and whether a cap stop among them fails the test.
  - Make "before any B is read" checkable: the acceptance record's commit is an ancestor of every commit that carries a B from those windows.
- **C6.** No pass criterion; see B4.
- **C7.** "A rule in the window report" names nothing. It must name a report field and its test.
- **Missing.** Add conditions that (i) R8's per-capture reporting and the R7 flag are implemented and tested, and (ii) the K2 arm refusal is implemented and tested (S1).

**S8. R8 leaves open the window in which a stop happens.** R8 only halts later windows. By R7's logic and A1 §5.1, a cap or deadline stop inside a claim window re-creates the filter for that window. Hold that window's claim status whole, as R7 does.

**S9. R9 has no end state.** If fewer than 24 captures ran the search after the permitted third window, R9 does not say what happens. Add "returns to council".

## NIT

- **N1. Summary item 1** says the rule was "fixed by a rule written before the value is computed". The ruling itself computes 1,710,000 in §4.3. Say "B-blind; the value was foreseeable from printed counts".
- **N2. R6's test citation.** R6 cites `tests/test_powermetrics_fiducial.py:641–660`, which uses an injected budget of 31. The test at the production value is `:606–639`. The D-143 pin tests `:573–605` (`RULED_DETECTION_CELL_BUDGET`, `OBSERVED_CORPUS_MAX_CELLS`) must also be re-keyed. That is permitted: they are constants, not fixtures.
- **N3. §5 item 2's source.** It rests on registration lines 149–150, which name `n17_r6`. That text is stale: r6 pins a different `uncertainty_evidence.py` (`257cda08…`). Cite the writer check `validate_powermetrics_fiducial.py:397–402` instead.
- **N4. August figures.** §4.1's August range (112,205–137,189) is the anchor-v2 sweep. The v3-anchor basis that amended D-143 has a maximum of 137,535 (`trace-notes.md:405–407`; n17 artifacts :525). This changes no value.

## Verdict

**DISSENT.**

- **What stands.**
  - Route R, the 5 ms span limit, a constant cap, the flag-and-hold rule outside the range, and the membership logic (8 never, interim, then fresh) all stand.
  - The network-time diagnosis is verified.
  - The rule text reads no B.
- **What must change before this is adopted.**
  - B1 and B2: the sizing rule's refusal check depends on machine load, and the ruling neither engages the recorded 1.55 M rejection nor the 1.28 M-cell capture.
  - B3: the sequence computes the value on bytes that will not ship, and admits unreviewed branches by a B-identity test.
  - B4: the HOLD could close without the #416 audit as the owner wrote it.
