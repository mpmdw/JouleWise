ADDENDUM: SCI-25G83-CANDIDATE-01-A2 ISSUED — PROCEED

# Cold addendum SCI-25G83-CANDIDATE-01-A2 — ruling on network time being ON during the W1 and W2 captures

Judge: cold Fable 5.1 seat, one foreground session, 2026-09-27, started 18:06 PDT (budget 40 minutes).
The verdict of the science-gate ruling, PROCEED TO ISSUANCE, is unchanged. This addendum adds one disclosure (D8), rewrites the wording of two earlier disclosures (D1, D3), closes one open item of addendum A1 (H4, "the cause of the steps is sought"), and adds two conditions on every future window (H5, H6). It changes no member, no statistic and no operative number.

Inputs, by sha256 as I read them:

| Input | sha256 |
|---|---|
| Candidate `candidate_acceptance_25g83.json` | `dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2` |
| Registration `preregistration_d079_epoch_25g83_rev1.md` | `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1` |
| Seat's log copy `timed.txt` | `b03075f45eb8e3ffb19883fa0a6458ea9d83cf68cf2ffd5bd70100b66fe0c8ed` |
| Seat's list `applies.txt` | `9aa1ae9e19dffd2226b26dea054637bfb9c2f563d3be84e292c270663416d203` |
| Charge `00-charge.md` | `92b86e3a763573a9bee821fc877b07fd309f1ba22a7ad5a0e6afd7c126d8fd3f` |
| `joulewise/uncertainty_evidence.py` in the code checkout | `b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8` (equals the digest the candidate pins) |
| My own log pull, 00:00–03:00 PDT | `aac85b4762dda3ae2f485b4adb42eda843535a203645b9c5b25f2f4fc17c1b4f` |
| My own log pull, 08:30–11:30 PDT | `14ca9501825686b80d9e9606caf165eef2b345e4e71f4def44b7ecf13db74d61` |

## 0. Contamination disclosure

1. **Preloaded context I did not choose.** Before my first action the session harness injected the owner's global instruction file, the project instruction file of the judge worktree, and the one-line index of the memory store. I opened none of those files, and none of `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENTS.md`, memory files or skill files. The index carries owner directives and status lines; one of them says the candidate "cleared" and that D-138 is next. I took no instruction and no fact from the index. It holds no B value.
2. **Same model family.** I am Fable 5.1, as were the two judges whose rulings I am amending. I sat on no earlier step of this activation.
3. **Made after the values were known.** I read the science-gate ruling and addendum A1 in full. Both print every B value of W1 and W2. Everything I rule here is therefore ruled with the outcome known. To limit what that can do, each of my findings on the clock rests on clock readings and log lines only; none needs a B value until the last step (§3.4), where I measure how far the finding could move the statistics.
4. **Values I created.** None that is a B. I created a table of clock movements per capture (§2) and three counterfactual statistics (§3.4). They are diagnostics.
5. **Files.** I changed no file in any repository or custody directory. This ruling is one new file at the path the charge names. Scratch is `/tmp/cg-scia2-d528efb2/` (`intervals.py` `120bc3ba…`, `offsets.py` `8e599dab…`, `tau.py` `c0973ab9…`, `counterfactual.py` `33fd523a…`, `offsets.json` `d7051120…`). I ran no capture and no power sampler and changed no system setting. Every command ran in the foreground.
6. **A difference from the charge.** The charge says the code checkout is at main `e7c8bcc6`. Its HEAD is `c772b019`; `e7c8bcc6` is an ancestor, and the commits between are record-keeping. The estimator file I cite has the pinned digest (table above). The checkout also holds one untracked directory that was there before I arrived.

## 1. Words used

- **Capture**: one 198-second recording of the power sampler while the machine runs 59 commanded one-second GPU load pulses. W1 and W2 each ran 12, one every 600 s.
- **B**: the one number a capture contributes, in seconds: the largest timing uncertainty of any pulse edge plus the uncertainty of placing the capture on the wall clock.
- **Member**: a capture recorded valid whose clock alignment resolved. The candidate has 12. **S**, **C**, **level screen**: the three operative numbers computed from the members' B values (S = range of B, 0.013701 s; C = 0.019021 s, a 99 % prediction width; level screen = largest B, 0.038079 s).
- **Wall clock**: the machine's time of day. Software may move it. **Monotonic clock**: a counter of elapsed time since boot that nothing moves. A **paired reading** is one reading of each, taken together. The difference "wall minus monotonic" stays constant if nothing touches the wall clock.
- **Network time**: the macOS setting "set time automatically". When it is ON, the time daemon **`timed`** asks time servers on the network what time it is (the protocol is NTP) and corrects the wall clock to match.
- **Correction**: one act of `timed` moving the wall clock. It comes in two kinds. A **step** sets the clock to the new time at once. A **slew** tells the kernel an amount, and the kernel feeds it in gradually over the next minute or two.
- **Frequency setting**: a third thing `timed` sets: a standing rate, in parts per million (ppm), by which the wall clock runs faster or slower than the monotonic clock. At −7.5 ppm the wall clock loses 7.5 µs every second, 1.49 ms over one capture.
- **Straight-line model**: the clock method's assumption that, during one capture, wall time is a straight line against monotonic time: one rate, no jump. The method tolerates a departure from the line of up to 250 µs, the **allowance**, and adds that allowance in full to every capture's uncertainty whether or not a departure was seen.
- **Drift term** (the code's `wall_minus_monotonic_span_s`): how far "wall minus monotonic" moved between a capture's first and last paired readings. It is added in full to the capture's uncertainty. A capture whose drift term exceeds 5 ms is refused.
- **Clock-alignment bound** (`effective_clock_anchor_bound_s`): the uncertainty of placing the capture on the wall clock. It is the sum of the drift term, the half-width of the fitted starting point, and two small fixed terms. It is one of the two parts of B.
- **Claim-bearing capture**: one whose numbers will be reported as results. The W1 and W2 captures are not: they were taken only to build the calibration.
- **Settle**: the quiet 600 s a window waits before its first capture.
- **The issuing transaction**: the single reviewed change, governed by decision D-138, that turns the candidate into the calibration in force.
- All times are Pacific Daylight Time on 2026-09-27.

## 2. What I executed

**2.1 The log, pulled again by me.** I ran `/usr/bin/log show --info --debug --predicate 'process == "timed"'` over 00:00–03:00 and 08:30–11:30. It returns 42 applied corrections (lines containing `cmd,apply`). All 26 lines of the seat's `applies.txt` are in my pull with the same time, kind and size. The new fact is verified.

The 42 corrections are of two sizes.

*Eight of millisecond size*, each following a fresh reading from NTP servers:

| Time | Kind | Size | Next one after |
|---|---|---:|---:|
| 00:39:52 | slew | −1.262 ms | 27.3 min |
| 01:07:12 | slew | −12.579 ms | 45.9 min |
| 01:53:09 | step | +53.198 ms | 27.5 min |
| 02:20:42 | slew | +4.386 ms | (end of W1) |
| 09:00:03 | slew | +10.688 ms | 34.7 min |
| 09:34:47 | slew | +44.194 ms | 36.7 min |
| 10:11:29 | slew | −35.939 ms | 44.8 min |
| 10:56:16 | slew | +38.818 ms | (end of W2) |

The charge says "about every 27 minutes"; the measured spacing is 27 to 46 minutes. The charge calls the three known exclusions "steps"; one was a step and two were slews. With each of these eight, `timed` also changed the frequency setting. The settings in force were −3.96, −7.50, +6.24 and +7.50 ppm through W1, and −5.86, +6.20, −3.73 and +6.08 ppm through W2.

*Thirty-four of microsecond size* (under 0.1 ms each), in groups of three within a tenth of a second. The log shows what triggers them: a coarse time reading from Apple's push-notification service ("Received time … ±35.00 from APNS"), after which `timed` re-applies its current estimate. They leave the frequency setting unchanged.

`timed` states its own uncertainty for each network reading (`unc_s`): 0.016 to 0.022 s. The millisecond corrections are the same size as that uncertainty. They are mostly the noise of reading time over a network, not real error in the machine's clock.

**2.2 Each capture's clock, reconstructed from its own readings.** The alignment uses five paired readings per capture. The capture's event file holds 124 more: one for every pulse command. I did not know this from the charge; I found it in custody. With 129 paired readings spread through each capture I computed, for all 24 captures:

- how far "wall minus monotonic" moved in total;
- how far the frequency setting in force predicts it should have moved (setting × duration);
- the largest departure of any reading from the best straight line.

Worked example, member W1-d04: the setting in force was −7.503 ppm and the readings span 198.07 s, so the prediction is −7.503 × 198.07 = −1486.2 µs. Measured: −1486.1 µs. No reading departs from the straight line by more than 3.1 µs.

In the 18 captures that no correction touched, measured and predicted movement agree within 1.0 µs and the largest departure from the line is 2.3 to 4.3 µs. That is the noise of this measurement. The two clocks, the log and the custody readings tell one consistent story.

**2.3 How a slew unfolds.** Fitted to the two large slews that fell inside captures (W1-d11 and W2-d07): the kernel feeds in the remaining amount at a rate that falls by a factor e every **16.5 s**. After 64 s a slew is 98 % delivered; after 112 s, 99.9 %. So a slew affects the clock for about two minutes *after* its log line. A capture that starts shortly after a correction can still catch its tail.

The same thing seen in member W1-d12 (µs scale). Rows, top to bottom: the time axis in seconds after the capture's first reading; the capture itself (the bar of `=`); the moment of the correction (the `^`); and the measured distance of the wall clock from the line its frequency setting predicts.

```
seconds after start :  0       10       20    27.8 31       40       50       61       70  ...  198.6
capture             :  |=============================================================== ... =====|
correction          :                          ^ three slews: +23.5, +34.0, +39.8 µs
wall clock moved, µs:  0.0     0.5      0.4    0.6  6.2     21.5     30.5     35.1     37.7 ...  40.7
```

The three slews do not add up to 97 µs. Each replaces the one before; the clock ends 40.1 µs from where it would have been.

**2.4 The code passages the seat cited.** Verified, word for word, in `joulewise/uncertainty_evidence.py` at the pinned digest. Lines 902–909: a departure from the straight line of up to about 250 µs between readings is the one thing the arithmetic cannot see, and it is excluded "by the authenticated network-time-OFF admission required of prospective claim-bearing captures"; "a capture with network time ON or unknown is validation-only material". Lines 952–957: for evidence nights the OFF state "is established by the chain before settle and attested per envelope from the `timed` unified log".

## 3. Question 1 — the 12 members

### 3.1 Table

"Inside" means between the capture's first and last paired readings. Movements are in µs. "Excess" is measured movement minus the movement the frequency setting predicts; it is what corrections added.

| Member | Capture interval | Corrections inside | Nearest earlier correction | Measured / predicted movement | Excess | Largest departure from line | Drift term charged | Alignment bound | B (µs) |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| W1-d04 | 01:10:07.9–01:13:26.0 | none | −12.579 ms slew, 175 s before | −1486.1 / −1486.2 | +0.1 | 3.1 | 1487.7 | 2872.8 | 36109.1 |
| W1-d05 | 01:20:08.5–01:23:27.0 | none | same, 776 s before | −1489.4 / −1489.2 | −0.2 | 2.9 | 1490.4 | 2022.5 | 24730.0 |
| W1-d06 | 01:30:08.2–01:33:26.9 | none | same, 1376 s before | −1490.6 / −1490.5 | −0.1 | 2.9 | 1492.3 | 2276.5 | 26267.1 |
| W1-d07 | 01:40:08.9–01:43:26.9 | none | −11.8 µs slew, 352 s before | −1486.3 / −1485.9 | −0.4 | 3.2 | 1487.7 | 2298.1 | 29309.2 |
| W1-d10 | 02:10:10.4–02:13:28.9 | none | +53.198 ms step, 1021 s before | +1240.7 / +1239.7 | +1.0 | 2.7 | 1246.0 | 2310.1 | 24377.1 |
| **W1-d12** | 02:30:10.3–02:33:28.9 | **three slews: 02:30:38.154 +23.5 µs; 02:30:38.204 +34.0 µs; 02:30:38.260 +39.8 µs** (27.8 s after start) | +4.386 ms slew, 568 s before | +1529.5 / +1489.4 | **+40.1** | 17.6 | 1536.8 | 2322.0 | 26493.1 |
| **W2-d01** | 09:10:11.0–09:13:28.9 | none | **three slews, 09:09:48.903–49.013: −7.5, −7.9, −45.3 µs, 22 s before start** | −1171.6 / −1160.0 | **−11.6** | 8.2 | 1173.0 | 2545.7 | 32030.5 |
| W2-d03 | 09:30:11.4–09:33:29.9 | none | −45.3 µs slew, 1222 s before | −1162.5 / −1163.5 | +1.0 | 3.6 | 1164.9 | 1790.8 | 27705.7 |
| W2-d04 | 09:40:11.1–09:43:30.0 | none | +61.4 µs slew 218 s before; +44.194 ms slew 324 s before | +1233.6 / +1233.1 | +0.5 | 2.8 | 1239.5 | 2424.5 | 32459.0 |
| W2-d05 | 09:50:11.1–09:53:30.0 | none | −21.1 µs slew, 214 s before | +1233.3 / +1232.5 | +0.8 | 3.2 | 1234.8 | 1737.0 | 28014.8 |
| W2-d09 | 10:30:11.8–10:33:30.0 | none | −35.939 ms slew, 1122 s before | −739.1 / −739.2 | +0.1 | 2.9 | 741.0 | 1873.4 | 29524.8 |
| W2-d10 | 10:40:11.6–10:43:29.9 | none | +27.4 µs slew, 133 s before | −739.1 / −739.5 | +0.4 | 2.7 | 741.0 | 1545.1 | 38078.6 |

Each member's evidence file has the digest the candidate records for it (12 of 12 checked).

### 3.2 Findings

- **No member had a step inside its capture. No member had a millisecond-size correction inside its capture or close enough before it to leave a measurable tail.** The closest call is W1-d04: a −12.579 ms slew began 175 s before it. At a decay of e per 16.5 s, 175 s leaves 12,579 × e^(−10.6) = 0.3 µs. Measured excess: +0.1 µs.
- **Ten members were untouched.** Their wall clock followed a straight line to within 3.6 µs, the measurement noise.
- **Two members were touched, at microsecond size.** W1-d12 had three slews inside; its clock moved +40.1 µs. W2-d01 had none inside, but caught the tail of a −45.3 µs slew applied 22 s before its start; its clock moved −11.6 µs. The decay law predicts 45.3 × e^(−22/16.5) = 11.9 µs; measured 11.6.
- The seat's report that "the 12 members saw only µs-scale adjustments" is confirmed and sharpened: ten saw none, two saw 40 µs and 12 µs.

### 3.3 Does each member's clock-alignment bound cover the effect?

Yes, for all 12, on two separate grounds, both measured.

1. *The drift term charges the whole movement.* The drift term is measured from the capture's first and last readings, so any correction delivered between them is inside it. For W1-d12 the clock moved 1529.5 µs in total, the 40.1 µs included; the drift term charged is 1536.8 µs. For W2-d01: 1171.6 µs moved, 1173.0 µs charged. For the other ten the same holds with nothing to cover.
2. *The allowance covers the bend.* A correction bends the straight line. The largest bend any member shows is 40.1 µs (W1-d12), against an allowance of 250 µs that every member is charged in full. The margin is a factor of six.

The clock method's own warning (§2.4) is that a bend *between readings* is invisible to its arithmetic, and that network time OFF is what rules it out. Network time was ON, so that guarantee was absent. In its place I have a measurement: 129 readings per capture, none more than 6.5 s from the next, and a log of every correction. They show no bend above 40.1 µs in any member. The bound holds for these 12 captures as a matter of measured fact, not of design.

### 3.4 Effect on B and on the operative numbers

The corrections entered B through the drift term, in the safe direction: W1-d12's B is about 40 µs larger (0.15 %) and W2-d01's about 12 µs larger (0.04 %) than they would have been. This is an estimate from the drift term; I did not re-run the estimator on an altered trace.

I recomputed the statistics with those two amounts removed. First I reproduced the issued values from the 12 B values (range 13,701.5 µs; mean 29,591.6; SD 4,330.5; Q99 19,020.6), which match the candidate.

| Quantity | As issued | With the two movements removed | Change |
|---|---:|---:|---:|
| Smallest B (W1-d10) | 24,377.1 µs | 24,377.1 µs | 0 |
| Largest B = level screen (W2-d10) | 38,078.6 µs | 38,078.6 µs | 0 |
| Range = S | 13,701.5 µs | 13,701.5 µs | 0 |
| C (= Q99) | 19,020.6 µs | 19,029.6 µs | +8.9 µs (0.05 %) |

S and the level screen are set by two members that were untouched. C as issued is 8.9 µs smaller than the counterfactual. For scale: one sampler frame is 128,000 µs, and the science-gate ruling measured a sampling difference of 1,900 µs in the same quantity between the 12-member and the 20-capture sets. 8.9 µs is not a defect in a number.

One further fact, stated so nobody finds it later and takes it for a defect. The drift term is 1.9 % to 6.0 % of each member's B, and it is set by whatever frequency setting `timed` last chose (0.74 to 1.54 ms here). If every member had carried the same drift term, S would be 505 µs larger and C 554 µs larger (2.9 %). This is a property of how B is defined, and turning network time OFF does not remove it: the code records that captures taken with network time OFF ran at 7.24 and 7.60 ppm (`uncertainty_evidence.py:57–58`; I read the comment, I did not re-measure those captures), which is a drift term of about 1.4 to 1.5 ms.

## 4. Question 2 — was network time OFF required for these captures?

**No.** Executed by search and by reading:

| Source | What it says about network time |
|---|---|
| Registration (digest above) | Nothing. Zero occurrences of "network time". For this class of night (`DIAGNOSTIC_NO_PACK`, a night that runs no measurement) it requires that "the transaction-authorization, quiet-census, boot/clock, and no-retry conditions must still pass" (lines 75–78). |
| Runbook `docs/phase_2/derivation_night_runbook.md` | Nothing. Zero occurrences. |
| The chain that ran the captures, `scripts/night_chains/calibration_derivation_only.zsh`, and its generator | Nothing. Zero occurrences. |
| The gate receipts of W1 and W2 | The "boot/clock" condition (C4) is a boot-session identifier plus one paired clock reading. It passed in both. It does not look at network time. |
| W1 and W2 custody | No file mentions network time. The state was neither set nor recorded. |
| The clock method (`uncertainty_evidence.py:902–909, 952–957`) | OFF is "required of prospective claim-bearing captures". A capture with network time ON or unknown "is validation-only material". |

The W1 and W2 captures are not claim-bearing. Each evidence file says `derivation_only: true`, each sits under `runs/instrument_validation/`, the candidate says `claim_eligible: false`, and the registration defines a derivation-only capture as one "taken to build a future acceptance, never to license a measurement" (lines 44–45). So the method's requirement does not reach them, and its own label for them, validation-only material, is what they are.

There is a precedent. The calibration in force before this one (`calibration_acceptance_d079_v2_n17_r7.json`, lines 620–625) records that none of its 17 members carries any network-time record, and rules: "historical unknown-state material supports this corpus derivation, but every PROSPECTIVE claim-bearing capture requires an authenticated network-time-OFF admission."

**It is not a protocol deviation.** Two things are nevertheless wrong and are cured by D8:

1. *A missing record.* The method says "per-member network-time provenance therefore travels with every record derived by this method". The predecessor file carried a `network_time_provenance` block. The candidate carries none (I searched every key and every string). The state is now known, per member, from the log; D8 is that provenance.
2. *A calibration made in one state and applied in another.* The members were captured with network time ON. The claim-bearing captures they will screen must be taken with it OFF. That the two states give the same population of B is supported by §3 (ten members with clocks as straight as OFF would give; the drift term of the same size in both states). It is an inference. It has not been measured at this epoch.

**What follows: proceed with a new disclosure.** Not stop: no number is wrong and no rule was broken. Not re-derive: nothing would be re-derived differently, since the members, their stored B values and the registered arithmetic are unchanged, and addendum A1 §3.3 already established that no route exists by which this corpus changes.

## 5. Question 3 — does any exclusion become outcome-selective?

**No.** But the count and the description of the exclusions change.

**5.1 A fourth exclusion has the same cause.** W1-d01 was recorded with the registered class `affine_clock_fit_empty` (no straight line fits the readings). Its cause is the −1.262 ms slew applied at 00:39:52, 16 s before its first reading at 00:40:08. My reconstruction shows its wall clock bending by 470.7 µs over the capture's first minute, with a largest departure from the best line of 345 µs. The decay law predicts 1,262 × e^(−16/16.5) = 478 µs. The allowance is 250 µs, so the fit was rightly refused. Neither earlier ruling knew this.

So four of the 12 exclusions are network-time corrections: W1-d08 (+53.198 ms step inside), W1-d11 (+4.386 ms slew inside), W2-d07 (−35.939 ms slew inside), and W1-d01 (tail of the −1.262 ms slew). The other eight are the work cap.

**5.2 Why the cause does not make them selective.** An exclusion selects on outcome if the thing that triggers it is tied to B. What triggers these four is the moment at which `timed` applies a millisecond correction, relative to the capture.

- *The moment* is set by `timed`'s own timer. The log shows it scheduling each next reading from the last one ("Want active time in 26.55min"). The captures start every 600 s by plan. Neither schedule reads the power trace.
- *The size* is set by a network reading whose stated uncertainty (±16 to 22 ms) is as large as the corrections themselves.
- *By count*: six millisecond corrections fell between the first and last capture of the two windows. A capture occupies 198 s of each 600 s slot. By chance one expects 6 × 0.33 = 2.0 to land inside a capture; three did. The probability of three or more by chance is 0.31.
- Every capture runs the same 59 pulses, so no capture loads the machine differently from another in a way that could steer the clock.

What I cannot do is compare the B of the four with the members': a capture with no clock alignment has no B under the registered estimator. That was already so in the science-gate ruling (§2.3) and is unchanged.

**5.3 What the cause does change.** The science-gate ruling called the clock steps "of unknown cause" and A1's H4 called them "a machine event". They are neither random nor mysterious: they are a machine setting, they are avoidable with one command, and at this rate they cost one capture in six. The filter they apply is benign in direction: it removes captures whose clock broke the method's model and keeps captures whose clock is as clean as OFF would make it. The reading of the registration under which the three were excluded (science-gate ruling §2.4, the "structural reading") does not depend on the cause and stands.

## 6. Question 4 — verdict for the D-138 issuing transaction

**PROCEED.** The candidate's 12 members, their B values, S, C and the level screen are what the sealed registration prescribes. Network time ON broke no registered rule, put no step and no millisecond correction inside any member, and moved the clock of two members by 40 µs and 12 µs, amounts that each member's uncertainty already covers six times over. The largest effect on an operative number is 8.9 µs on C.

The transaction adds the following to its record and to any text that reports this calibration. It changes no member, statistic or operative number on account of this addendum, and bindings B1 to B4 of addendum A1 continue to apply.

**D8, exact text:**

> **D8. Network time was ON during both capture windows.** The macOS time daemon `timed` was correcting the wall clock from network time throughout W1 and W2 on 2026-09-27. Between 00:00–03:00 and 08:30–11:30 PDT the system log records 42 applied corrections: 8 of millisecond size (1.3 to 53.2 ms; one immediate step and seven gradual slews, 27 to 46 minutes apart, each also changing the clock's standing rate within ±7.5 parts per million) and 34 of microsecond size (under 0.1 ms). Four of the 12 excluded captures were lost to these corrections: W1-d08 (+53.2 ms step during the capture), W1-d11 (+4.39 ms slew during the capture), W2-d07 (−35.9 ms slew during the capture), and W1-d01 (a −1.26 ms slew applied 16 s before the capture, of which 0.47 ms was delivered during it). Of the 12 members, ten had no correction during the capture, and their wall clock followed a straight line against the monotonic clock to within 4 µs. Two were touched: W1-d12 (three slews of +23.5, +34.0 and +39.8 µs applied 28 s into the capture; the clock moved +40.1 µs) and W2-d01 (the tail, −11.6 µs, of a −45.3 µs slew applied 22 s before the capture). Both movements lie inside the 250 µs allowance that the clock method adds in full to every capture, and inside each capture's charged drift term. S and the level screen are unaffected, because the members that set them were untouched; C is 8.9 µs (0.05 %) smaller than it would be with the two movements removed. No registered requirement was breached: the registration, the runbook and the capture chain say nothing about network time, and the clock method requires network time OFF only of claim-bearing captures. This calibration was therefore derived with network time ON and will be applied to captures taken with network time OFF. That the two states give the same population of B is inferred from the clock readings and has not been measured. The candidate file carries no network-time provenance field; this disclosure is that provenance, per member. Evidence: `docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/21-ruling.md`.

**Rewording of earlier disclosures and holds:**

> **D1 (replaces the second sentence).** The 12 others: 8 stopped by the 165,000-cell work cap, and 4 lost to network-time corrections of the wall clock, of which 3 are recorded as a wall-clock movement above 5 ms during capture and 1 as an infeasible clock fit.
>
> **D3 (adds).** The cause of the three movements is known: corrections applied by the time daemon with network time ON (D8). W1-d01, recorded under the registered class, has the same cause.
>
> **H4 of addendum A1 (its last clause is discharged).** "The cause of the steps is sought before claim-bearing windows run": found. The rest of H4 stands, and H5 and H6 below now govern.

Whether the issued file itself should carry a `network_time_provenance` block, as its predecessor did, is for the issuing transaction's gate. It may be added only if doing so changes no member value, no statistic, no operative number and none of the four pinned estimator files. The transaction's record carries D8 in either case.

## 7. Question 5 — what must be true before any future window at 25G83

### 7.1 What the code does today (read, not run)

| Kind of window | Is network time OFF enforced? | Where |
|---|---|---|
| Non-claim window (night class `DIAGNOSTIC_NO_PACK`; the class W1 and W2 ran under) | **No.** Not set, not checked, not recorded. | `scripts/night_chains/calibration_derivation_only.zsh` and `scripts/gen_derivation_night.py`: zero occurrences. `joulewise/night_gate.py`: zero occurrences; its clock condition C4 is boot session plus one paired reading. |
| Claim-bearing measurement night ("pack night") | **At arm time only.** The arm step runs the OFF command and refuses unless the command exits 0 and prints exactly `setUsingNetworkTime: Off`. | `scripts/run_night.py:1982` calls the evidence author; `joulewise/arm_readiness_evidence_t0.py:1225–1256` (`_derive_clock_probe`); expected output at `joulewise/arm_readiness.py:104`; the row `clock.network_time_off` is required by `configs/arm_readiness/d117_row_registry_v2.json` (phase `ARM_ONLY`, freshness 20 minutes). |
| Per-capture check of the `timed` log | **Only in a different chain.** | `joulewise/quiet_predicate_campaign.py`: OFF before settle (line 1626), log query and count (lines 472–483, 752), exclusion reasons `network_time_slew_attested` and `network_time_unattested` (lines 55–56), restore to ON (line 1767). Nothing in the pack-night path or the derivation chain calls these. |
| Scheduler refusal `scheduler_c4_network_time_on` | **Declared, never produced.** | `joulewise/scheduler_gates.py:94` lists the code. No file under `joulewise/` or `scripts/` emits it. |

So a claim-bearing night sets network time OFF when it arms, and then nothing checks that it stayed OFF or that no correction was applied during any capture. A non-claim night does nothing at all.

### 7.2 Which query attests the state

- **Not `systemsetup -getusingnetworktime`.** I ran it. Without administrator rights it prints "You need administrator access to run this tool... exiting!" and still exits with status 0, so neither its output nor its exit status can be trusted by an unattended process. The passwordless permission installed on this machine (`scripts/joulewise-network-time.sudoers`) grants the two *set* forms only, not the read form.
- **The set command's own output** attests the state at one moment: `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off` must exit 0 and print exactly `setUsingNetworkTime: Off`.
- **The `timed` log** attests what happened to the clock during a capture, which is the fact that matters. It must be read with `/usr/bin/log` by absolute path and with `--info --debug`: without those flags the correction lines are dropped and an empty answer would look like a clean one.
- **The capture's own paired readings** (§2.2) are an independent check that needs no log and no privilege.

### 7.3 Conditions

> **H5. Network time OFF for every window.** Before any window at 25G83 is armed, claim-bearing or not, network time is set OFF before settle begins, by the set command above, and the command's arguments, exit status, exact output and time are saved in the window's custody. After the last capture network time is set back ON and that receipt is saved too. For claim-bearing windows this is the clock method's existing requirement. For non-claim windows it is new, for three reasons: with it ON one capture in six is lost to a cause one command removes; calibration captures should be taken in the state of the captures they will be applied to; and captures of unrecorded state cannot later be told apart. Setting the state from the arming session, outside the capture chain, satisfies H5 and changes no pinned file.
>
> **H6. Per-capture attestation from the log.** For every capture of every window, the `timed` log is queried from 300 s before the capture's first paired reading to 1 s after its last, with `/usr/bin/log show --info --debug --style syslog --predicate 'process == "timed"'`, and the query, its output digest and the count of applied corrections (lines containing `cmd,apply,src,`, `ntp_adjtime` or `settimeofday`) are saved with the capture. The 300 s lead is required because a correction keeps moving the clock after its log line: at a decay of e per 16.5 s, a 53 ms correction takes 180 s to fall below 1 µs. The query may be run at harvest; the log was still complete 16 hours after W1. A capture with a count above zero, or with no readable log, is not a calibration member, not a bracket capture and not claim-bearing; it is recorded with its named reason. An output that lacks the log's column header is a failed query, not a clean one.
>
> **H7. First comparison of the two states.** The first calibration captures taken with network time OFF at 25G83 are compared with the 12 members on two quantities, the drift term and B, and the comparison is reported with the first claim-bearing results. This measures what D8 says is inferred.

Two recommendations, not conditions. (i) Record for every capture the largest departure of its 129 paired readings from a straight line; untouched captures here show 2.3 to 4.3 µs, the two touched members 8.2 and 17.6 µs, the four lost captures 345 µs and more. Any threshold on it must be registered before it is used. (ii) Confirm from the first H6 outputs that the OFF setting also silences the microsecond corrections triggered by the push-notification time source; I could not test that without changing a system setting.

H5 to H7 are conditions on future windows. They are not conditions on the issuance.

## 8. Left unchecked, stated plainly

- NOT EXECUTED: a re-run of the estimator on any capture. §3.4's 40 µs and 12 µs effects on B are read from the drift term. The two earlier judges reproduced all 12 stored B values from raw bytes.
- NOT EXECUTED: any run of the arm path, the pack-night path or the quiet-predicate chain. §7.1 is from reading code and searching for text.
- NOT EXECUTED: whether the existing log query in `quiet_predicate_campaign.py` includes a lead before the capture. H6 states the lead as a requirement either way.
- NOT EXECUTED: reading the refusal-branch statement or decision D-138. I rely on addendum A1's quotations of them.
- NOT ESTABLISHED: the current network-time setting of the machine. The read command needs rights I do not have. The log shows `timed` still applying corrections between 17:00 and 18:30 today (6 found), so it was ON as of this session.
- NOT ESTABLISHED: whether network time OFF stops the push-notification-triggered corrections, and whether the frequency setting persists unchanged while OFF. The second rests on a code comment.
- UNVERIFIED beyond its two fits: the 16.5 s decay. It fits W1-d11 to 43 µs and W2-d07 to 417 µs root-mean-square, and predicts the W2-d01 and W1-d01 tails to within 0.3 µs and 8 µs.
- NOT ESTABLISHABLE: the B of the four captures lost to corrections.

## Summary for the owner

1. Proceed with issuance: network time was ON, but no clock jump fell inside any of the 12 members; two members' clocks moved by 40 and 12 millionths of a second, which their stated uncertainty already covers six times over, and the largest effect on any operative number is 9 millionths of a second on C.
2. No rule was broken, because only claim-bearing captures are required to have network time OFF; but four captures, not three, were lost to network-time corrections (W1-d01 is the fourth), and the record must say so in the new disclosure D8.
3. Before any further window, network time must be set OFF before the quiet wait and each capture checked against the system log; today the code does this at arm time for measurement nights only, never for calibration nights, and never per capture.
