ADDENDUM: SCI-25G83-CANDIDATE-01-A3 ISSUED — PROCEED

# Cold addendum SCI-25G83-CANDIDATE-01-A3 — ruling on the paired refuter's dissent from addendum A2

Judge: cold Fable 5.1 seat, one foreground session, 2026-09-27 18:34–18:49 PDT (15 of the 40 budgeted minutes).

**Verdict.** PROCEED stands. The refuter's one BLOCKER is adopted: condition H6 of addendum A2 is withdrawn and replaced. Of the six SHOULD-FIX findings, one is already cured, four are adopted with changes, and one is adopted in full. This addendum gives the final text of D8, D1, D3, H5, H6 and H7 (§4), and requires a network-time block in the issued file (§4.7). It changes no member, no B value, no statistic and no operative number.

Inputs, by sha256 as I read them:

| Input | sha256 |
|---|---|
| Addendum A2 `21-ruling.md` | `b35d072bb58f25eda711b6a0db1bbfc480781dd139cb144faa877d906391ba9c` |
| Refuter `22-opus-refuter.md` | `3c2a5b4e1166a42be912da03cea10ba876c2ebf891bb71ad2eb07b52916ee0a1` |
| This addendum's charge `30-addendum-charge.md` | `357589117eff9a284b151417c52ab035f88d470e37960fcea1f1defe9981a77f` |
| A2's charge `00-charge.md` | `92b86e3a763573a9bee821fc877b07fd309f1ba22a7ad5a0e6afd7c126d8fd3f` |
| Candidate `candidate_acceptance_25g83.json` | `dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2` |
| Preserved full log pull, plain text after `gunzip` | `2f9bf739fde57accdce86e27a9494303585c976132e5dc5063a2cd31a5880b5c` |
| `joulewise/uncertainty_evidence.py` (code checkout) | `b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8` |
| `joulewise/quiet_predicate_campaign.py` (code checkout) | `9dbb2d20411cb1f640bb7104db005967d9e6257117a926acb17faa4e4b71cb18` |

## 0. Contamination disclosure

1. **Preloaded context I did not choose.** Before my first action the session harness injected the owner's global instruction file (a writing standard and a list of skill names), the project instruction file of the judge worktree (notes on the model bridge), the one-line index of the owner's memory store, and the five most recent commit subjects. I opened none of those files, and none of `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENTS.md`, memory files or skill files. The index carries owner directives, among them that tolerances should be sized to the instrument and that anything bearing on whether a number is true is mandatory. One commit subject says the refuter dissented on H6. I took the writing standard as form. I took no fact and no instruction from the rest: every ruling below rests on a file I read or a command I ran, named where it is used.
2. **Same model family.** I am Fable 5.1, as was the judge of addendum A2. I sat on no earlier step.
3. **Made after the values were known.** A2 and the refuter print every member's B. Nothing I rule selects or changes a member.
4. **Read beyond the packet, on purpose.** The design ruling `11-d138-design/21-coldgate-fable-ruling.md`, to learn how the issued file consumes these texts. I did not re-judge it.
5. **Re-use of another seat's code.** For two checks (the constant-drift statistics and the best-line fit of W1-d01) I re-ran the refuter's own scripts after reading them. They are re-executions, not independent implementations. My own independent checks are marked "own" in §2.
6. **Files.** I changed no file in any repository or custody directory. This ruling is one new file at the path the charge names. Scratch is `/tmp/cg-scia3-d528efb2/` (`offnights.py` `720f419d…`, `d01.py` `9966f9d9…`, query outputs `q_deleted.txt` `da1b28ef…`, `q_flags.txt` and `q_noflags.txt` both `655dd7bb…`, `q_window.txt` `5eaba849…`). I ran no capture and no power sampler and changed no system setting. Every command ran in the foreground.
7. **A difference from the charge.** The code checkout's HEAD is `c772b019`, not `e7c8bcc6`. A2 recorded the same; the two files I cite have the digests above.

## 1. Words used

Terms defined in A2 §1 are used in the same sense. The ones this ruling leans on, restated so that it can be read alone:

- **Capture**: one 198-second recording of the power sampler while the machine runs 59 commanded load pulses. **Window**: one session of 12 captures, one every 600 s, after a quiet wait of 600 s called the **settle**.
- **B**: the one number a capture contributes, in seconds: its timing uncertainty. **Member**: a capture whose B enters the calibration. **S, C, level screen**: the three operative numbers computed from the 12 members' B values (13,701.5 µs; 19,020.6 µs; 38,078.6 µs).
- **Wall clock**: the machine's time of day, which software may move. **Monotonic clock**: a counter of elapsed time that nothing moves. A **paired reading** is one reading of each, taken together.
- **Network time**: the macOS setting "set time automatically". While it is ON, the time daemon **`timed`** reads the time from the network and corrects the wall clock. A **correction** is either a **step** (the clock is set at once) or a **slew** (the kernel feeds the amount in gradually; the part not yet delivered is the **tail**).
- **Standing rate**: a rate, in parts per million (ppm), at which the wall clock gains or loses against the monotonic clock. `timed` resets it with each millisecond-size correction. At 7.5 ppm the wall clock moves 1.49 ms in one capture.
- **Drift term**: how far "wall minus monotonic" moved between a capture's first and last paired readings. It is added in full to B. With no correction in the capture it equals standing rate × duration.
- **Straight-line model** and **allowance**: the clock method assumes that within one capture the wall clock is a straight line against the monotonic clock. It tolerates a departure of up to 250 µs and charges that allowance in full to every capture.
- **Anchor readings**: the five paired readings the clock fit uses, three in the capture's first two seconds and two at its end. The fit requires one straight line to pass through all five to within their own resolution, a few µs. The 250 µs allowance does not apply to them.
- **Marker**: a log line that `timed` writes whenever it moves the clock. It contains one of `cmd,apply,src,`, `ntp_adjtime`, `settimeofday`.
- **Evidence chain**: the program that runs idle-measurement nights (`joulewise/quiet_predicate_campaign.py`). It already sets network time OFF and checks the log after every capture. **Derivation chain**: the program that ran W1 and W2 to take calibration captures. It does neither.
- **Registration**: the sealed document, written before the captures, that fixes which captures become members and which are excluded.
- **Claim-bearing**: a capture whose numbers will be reported as results. W1 and W2 are not.
- All times are Pacific Daylight Time.

## 2. What I executed

| # | Contested fact | What I ran | Result |
|---|---|---|---|
| E1 | A query over a deleted period looks clean | `/usr/bin/log show --info --debug --style syslog --predicate 'process == "timed"'` over 2026-09-26 00:00–03:00, at 18:35 on 09-27 | Exit 0. Output is one line, the column header. **Confirmed.** |
| E2 | The log is deleted oldest first, at about 29 hours | Same query over 09-26 12:00–16:00 and 13:00–14:30; then compared the refuter's pull `log_pre.txt`, taken earlier the same evening, with the preserved full pull taken later (own) | In my live queries the oldest `timed` line is 09-26 13:34:30.500472, 29.0 h old, and the preserved full pull begins at the same line. The refuter's pull began at 13:06:41. The 38 lines it holds that are older than the new oldest line are all gone; its 1,188 lines of 09-26 from that line onward are all in the later pull, none missing. The cut is sharp. **Confirmed.** |
| E3 | Deletion removes markers too | Same comparison (own) | Among the deleted lines are applied corrections, for example the slew logged at 09-26 13:06:41.771809. A correction that happened is no longer in the log. |
| E4 | The evidence chain forbids a harvest-time query and uses ±1 s | Read `quiet_predicate_campaign.py:609–636, 695–770` | "Run immediately after the collector exits … because the log store is rotated -- never deferred to harvest." The window is the capture ±1 s, each end read from both clocks. No lead. **Confirmed.** |
| E5 | The chain really runs the query at once | Read the 24 capture records of the two OFF nights in custody (own, `offnights.py`) | Each query ran 7 to 10 s after its capture ended. |
| E6 | OFF nights: state, markers, standing rate | Same script, nights `qpe01-pilot-n1-20260922-2100…` and `…20260923-0700…` (own) | Both carry a receipt with the exact output `setUsingNetworkTime: Off`. All 24 captures: state `off`, attestation `authenticated`, 0 markers. Standing rate 3.583–3.587 ppm on the first night and 2.873–2.875 ppm on the second. The refuter reports 3.62 and 2.90; the 1 % difference is a difference of method that I did not resolve. D8 says "about 3.6 and 2.9". |
| E7 | `timed` keeps writing to the log while OFF | Read the saved per-capture logs of the first OFF night (own) | Yes. It still fetches network time about every 10 to 25 minutes and logs it; it applies nothing. 13 of the 24 capture logs hold such lines, 11 hold only the header. |
| E8 | How often corrections occur with network time ON | Counted the preserved full pull, 28.5 h (own) | 183 applied-correction lines in 91 events: 47 of millisecond size, 44 of microsecond size. At that rate 4.0 h holds 12.8 events. The two OFF nights hold none in 4.0 h of captures; the chance of that, were OFF to change nothing, is 3 in a million. |
| E9 | The 42 corrections of D8 | Counted from the preserved full pull (own) | 42 in 00:00–03:00 and 08:30–11:30: 1 step, 7 millisecond slews, 34 microsecond slews. The 34 are eleven groups of three, each following a "Received time … from APNS" line (33 such lines), plus one slew of +41.6 µs that accompanied the step. The refuter's nit N4 is **confirmed**. |
| E10 | Standing rate outside ±7.5 ppm | Read the `ntp_adjtime` lines (own; ppm = `freq_scaled` ÷ 65,536) | The eight corrections set −3.96, −7.50, +6.24, +7.50, −5.86, +6.20, −3.73, +6.08. The rate in force from 08:13:39 to 09:00:03 was −8.68. Nit N3 **confirmed**. |
| E11 | The flags `--info --debug` | Ran the same query with and without them over 09-27 09:00–11:00 (own) | Identical output, same sha256, 48 marker lines each. In the compact listing every marker line has level `Df`, which is "default", a level `log show` always prints. Nit N2 **confirmed**. The comment in `quiet_predicate_campaign.py:48–52` that reads `Df` as a level "plain `log show` drops" is wrong in its reason; the flags are harmless. |
| E12 | The constant-drift statistics | Re-ran the refuter's `cf.py` | Issued: range 13,701.5, Q99 19,020.6. With every member's drift term replaced by one constant (tried 0, 1,252.9, 1,434 and 1,505 µs): range 14,206.5 (+505.0), Q99 19,575.0 (+554.4), the same for every constant. **Confirmed.** |
| E13 | W1-d01's loss mechanism | Own computation from its five anchor readings (`d01.py`); re-ran the refuter's `minimax.py`; read `uncertainty_evidence.py:1225–1232` | The second and third anchor readings, 1.03 s and 1.86 s in, sit 27.8 and 47.8 µs off the line through the first and the last. The readings resolve 0.2 to 3.5 µs. No line fits, and the code returns `affine_clock_fit_empty` at the step that adds the anchor readings. The best line through all 129 readings departs by 170.2 µs, under the allowance. **Confirmed**: the allowance was not what refused it. |
| E14 | Which members H6 of A2 would have set aside | Re-ran `cf.py` against the log | Six with a 300 s lead: W1-d04 (175 s before), W1-d12 (inside), W2-d01 (22 s), W2-d04 (218 s), W2-d05 (214 s), W2-d10 (133 s). Four with a 180 s lead: the same less W2-d04 and W2-d05. **Confirmed.** |
| E15 | The hazard was on record before W1 | Read `README.md:17` and the A267 ruling of 2026-09-22 in the code checkout | The README describes the time daemon moving the clock at each network-time sync on the 09-22 pilot night. The A267 ruling (rule 1) puts the OFF command "BEFORE" the settle in the evidence chain "so the 600 s settle also absorbs any in-flight adjtime slew". **Confirmed.** |
| E16 | The registration's exclusions | Read `preregistration_d079_epoch_25g83_rev1.md:165–168` | `affine_clock_fit_empty` is "the ONLY exclusion mechanism registered at this step: an unresolved anchor carrying any other reason refuses issuance instead of quietly excluding the member". |
| E17 | The preserved evidence | `shasum`, `git ls-files` in the judge worktree | The judge's two pulls (`aac85b47…`, `14ca9501…`), the refuter's two (`73661a94…`, `a40cd6bf…`) and the full pull (`2f9bf739…` after `gunzip`) are present and tracked at commit `81e4055f`. |
| E18 | Cost of a whole-window query | Timed a query over 3.5 h | 2.3 s. |

Not re-executed by me, and accepted on two agreeing seats: the per-member clock table, the 12 member digests, the +8.9 µs counterfactual, A2's map of the arm path, and the behaviour of `systemsetup -getusingnetworktime`.

## 3. Rulings on the refuter's findings

### B1 (BLOCKER) — H6 can certify a capture whose log is gone. **ADOPTED.**

Every fact the refuter states is confirmed (E1–E4). H6 as A2 wrote it accepts a header with no rows as clean and lets the query run at harvest. After deletion that is what every query returns. E3 is the sharpest form of the defect: corrections I can see in an earlier pull are already absent from the live log.

The refuter offers two cures: run the query at once, or demand positive proof that the log still covers the period. I require the proof and recommend the promptness, for this reason. Promptness makes a deleted log unlikely. It does not make it impossible: the store is limited by size as well as age, and a query can be re-run late after a crash. Proof makes the verdict safe whenever the query runs. The proof is possible because of two executed facts: deletion is strictly oldest first (E2), and `timed` writes to the log every 10 to 31 minutes in either state (E7; the longest silence in the 28.5 h pull is 1,881 s). So a query that reaches back one hour before the window and finds a `timed` line there has shown that nothing later was deleted. H6 in §4.5 is built on that. The line must be older than everything the verdict depends on, which is why H6 asks for it before the first capture's lead and not merely before the first capture.

The refuter is also right that an addendum about a calibration must not rewrite the approved method of the evidence chain. The new H6 does not touch that chain's per-capture query. It adds one query per window beside it.

### S1 — preserve the log. **ALREADY CURED.**

E17. The evidence is tracked. D8 now cites it.

### S2 — D8 overstates the rule and omits that the hazard was known. **ADOPTED, with my own wording.**

E15 and E16, and the method's text, which I read in full (`uncertainty_evidence.py:890–957`). That text requires an authenticated OFF state "of prospective claim-bearing captures", calls a capture with network time ON or unknown "validation-only material", and says that no fitted rate "may be treated as a substitute for that environmental control". It does not exempt calibration members. A2's sentence "the clock method requires network time OFF only of claim-bearing captures" reads an exemption into silence.

A2's finding that no registered rule was breached stands. What changes is the account of why the captures ran with network time ON: the project had diagnosed the mechanism five days earlier and installed the control in one chain only. D8 now says so, and says that the members' fitness rests on measurement after the fact.

### S3 — disclose the larger sensitivity and the OFF nights. **ADOPTED, with one correction to the refuter.**

E12 and E6. A2 computed the 505 and 554 µs and set them aside because the drift term exists with network time OFF too. That is half right. With OFF the standing rate is frozen (E6: constant to 0.003 ppm through each night), so within one window every capture carries the same drift term and the spread that `timed` created among the members vanishes. Between windows the frozen rate differs (about 3.6 and 2.9 ppm on the two nights; 7.24 and 7.60 ppm on earlier nights according to a code comment I did not re-measure), so a calibration built from several OFF windows would still carry some spread. The 505 and 554 µs are therefore the upper end of the effect, not its expected size. D8 states them as such.

Direction: the issued S and C are the smaller, stricter values. A stricter screen can refuse a good measurement; it cannot pass a bad one. One consequence for yield, stated so that nobody meets it later as a surprise: the level screen (38,078.6 µs) was set by member W2-d10, whose drift term was 741 µs. A capture otherwise identical to it, taken with OFF at a frozen rate of 7.5 ppm, would have a drift term of 1,490 µs and a B of 38,828 µs, and the level screen would refuse it.

### S4 — W1-d01's mechanism. **ADOPTED.**

E13. W1-d01 remains the fourth capture lost to a network-time correction; the count in D1 does not change. D8 now names the real mechanism. A2's recommendation (i), to record each capture's largest departure from a least-squares line, is amended: the quantity to record is how far the anchor readings sit off one line, because that is what the code tests.

Two executed points size the fit's sensitivity to a tail. W1-d01's tail of 470 µs put the anchor readings 48 µs off the line and the fit refused. W2-d01's tail of 11.6 µs put them 1.0 µs off and the fit passed. Roughly a tenth of a tail shows up at the anchor readings, which resolve a few µs. So the fit refuses tails of several tens of µs and more, and the tails it lets through are well below the 250 µs allowance. This is an estimate from two points, not a tested bound.

### S5 — H6's zero tolerance with a 300 s lead. **ADOPTED IN PART.**

E14. I shorten the lead to 180 s and keep the rule that one marker excludes.

- *The lead.* A2 chose 300 s and in the same sentence gave the reason for 180 s: the largest correction on record, 53.2 ms, fading by a factor e every 16.5 s, falls below 1 µs after 180 s (53,200 × e^(−180/16.5) = 0.97 µs). 180 s is the size the physics gives.
- *Why one marker of any size still excludes.* The refuter's objection is that a 27 µs slew 133 s before a capture leaves 0.009 µs and harms nothing. That is true of W1 and W2, where network time was ON and corrections were routine. H6 never applies to such a window: H5 requires OFF. With OFF, no marker is expected at all (E6, E8). A marker then is not a small disturbance to be sized. It is evidence that the OFF control failed, and a capture taken under a failed control does not have the state its record claims.
- *Why not a rule on the predicted size of the tail.* It would make membership depend on a decay constant fitted to four cases.
- *The refuter's point that future members would be selected by a different rule than these 12* is correct and unavoidable: H5 already changes the state. H7 is the comparison that measures the difference.

### S6 — provenance in the issued file, and pooling. **ADOPTED.**

The network-time block is required in the issued file (§4.7). The design ruling had already placed it; I give its content. On pooling, H7 now rules: each member's state is recorded, and ON-state and OFF-state members are combined only under a rule registered before the OFF-state captures are taken.

One interaction the lead must handle. The candidate registers the trigger `corpus_doubles_from_12_to_24`, and network-time state is not one of its identity fields, so under the registration as it stands OFF-state captures would count toward the same corpus. H7's pooling rule therefore has to enter the registration by amendment before the next window that takes calibration captures. So do H5 and H6, because the registration names a single exclusion mechanism (E16) and an exclusion it does not name is not available. The registration has been amended this way before (its amendment at line 650 adds "one outcome-independent, mechanism-named exclusion decided from instrument state alone").

### Nits

| Nit | Ruling |
|---|---|
| N1. A2 says two conditions; there are three | Adopted. H5, H6, H7. |
| N2. The flags' stated reason | Adopted (E11). The flags stay in the command because the approved command has them. |
| N3. "within ±7.5 ppm" | Adopted (E10). D8 reworded. |
| N4. 34 = eleven groups of three plus one | Adopted (E9). D8 reworded. |
| N5. The chance calculation (p = 0.31) is after the fact | Adopted as a caveat. It illustrates; nothing rests on it. |

## 4. Final texts

The consumer copies these verbatim. Each is written to be read alone.

### 4.1 D8 (replaces A2's D8 in full)

> **D8. Network time was ON during both capture windows.** "Network time" is the macOS setting "set time automatically". While it is ON, the time daemon `timed` corrects the machine's wall clock from time servers, either at once (a step) or gradually over about two minutes (a slew), and resets the rate at which the clock runs (the standing rate). It was ON throughout W1 and W2 on 2026-09-27. Between 00:00–03:00 and 08:30–11:30 PDT the system log records 42 applied corrections: 8 of millisecond size (1.3 to 53.2 ms; one step and seven slews, 27 to 46 minutes apart) and 34 of microsecond size (under 0.1 ms; eleven groups of three, each following a time reading from Apple's push-notification service, and one that accompanied the step). The eight set the standing rate to values between −7.50 and +7.50 parts per million; from 08:13:39 to 09:00:03 it was −8.68. **Captures lost.** Four of the 12 excluded captures were lost to these corrections: W1-d08 (+53.2 ms step during the capture), W1-d11 (+4.39 ms slew during the capture), W2-d07 (−35.9 ms slew during the capture), and W1-d01 (a −1.26 ms slew applied 16 s before the capture; 0.47 ms of it arrived during the capture, so that the five paired clock readings the clock fit uses cannot lie on one straight line: the two taken 1.0 and 1.9 s into the capture sit 28 and 48 µs off the line through the other three, and no clock fit exists). **Members.** Ten of the 12 members had no correction during the capture, and their wall clock followed a straight line against the monotonic clock to within 4 µs. Two were touched: W1-d12 (three slews of +23.5, +34.0 and +39.8 µs applied 28 s into the capture; the clock moved +40.1 µs) and W2-d01 (the tail, −11.6 µs, of a −45.3 µs slew applied 22 s before the capture). Both movements lie inside the 250 µs allowance that the clock method adds in full to every capture, and inside each capture's charged drift term (the clock movement between a capture's first and last readings, which is part of B). **Effect on the operative numbers, two sizes.** (a) The two movements: S and the level screen are unaffected; C is 8.9 µs (0.05 %) smaller than with the movements removed. (b) The changing standing rate: because `timed` reset the rate between captures, the members' drift terms differ, from 0.74 to 1.54 ms. Had all 12 carried one and the same drift term, of any size, S would be 505 µs (3.7 %) and C 554 µs (2.9 %) larger. The issued S and C are therefore the stricter values. With network time OFF the rate stays fixed through a window: the two nights in custody taken with it OFF (2026-09-22 and 2026-09-23, 24 idle captures of 600 s) ran at about 3.6 and 2.9 parts per million, each constant to 0.003, with no correction applied. The rate differs from one such window to the next, so 505 and 554 µs are the upper end of the effect. **What was required.** No registered rule required network time OFF for these captures: the registration, the runbook and the capture chain do not mention network time. The clock method's straight-line model nevertheless assumes OFF. Its text requires an authenticated OFF state of claim-bearing captures, calls a capture with network time ON or unknown "validation-only material", and does not exempt calibration captures. The one precedent, the previous calibration, excused historical captures of unknown state; these were new captures. The mechanism had been diagnosed in this project on 2026-09-22 (ruling A267), and the control installed then covered the chain that takes idle measurements and not the chain that takes calibration captures. The words "unknown cause" in the first science ruling were a miss. **What the members rest on.** Their fitness rests on measurement after the fact (129 paired clock readings per capture, and the log of every correction), not on the OFF control. **What is not measured.** This calibration was derived with network time ON and will be applied to captures taken with it OFF. That the two states give the same population of B is inferred, and is measured by H7. Evidence: `docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/21-ruling.md` and `31-addendum-ruling.md`; the log itself, which the system deletes after about 29 hours, is preserved in `evidence/` beside them (full pull, sha256 of the plain text `2f9bf739fde57accdce86e27a9494303585c976132e5dc5063a2cd31a5880b5c`).

### 4.2 D1 (unchanged from A2)

> **D1 (replaces the second sentence).** The 12 others: 8 stopped by the 165,000-cell work cap, and 4 lost to network-time corrections of the wall clock, of which 3 are recorded as a wall-clock movement above 5 ms during capture and 1 as an infeasible clock fit.

### 4.3 D3 (replaces A2's addition)

> **D3 (adds).** The cause of the three movements is known: corrections applied by the time daemon with network time ON (D8). W1-d01, recorded under the registered class, has the same cause. The mechanism was on record in this project from 2026-09-22; it was not newly discovered on 2026-09-27.

### 4.4 H4 of addendum A1 and H5

> **H4 of addendum A1 (its last clause is discharged).** "The cause of the steps is sought before claim-bearing windows run": the cause is network-time corrections (D8). The rest of H4 stands, and H5, H6 and H7 now govern.

> **H5. Network time OFF for every window.** "Network time" is the macOS setting "set time automatically"; while it is ON the time daemon `timed` moves the wall clock. For every window at 25G83, claim-bearing or not, network time is set OFF at least 600 s before the first capture's first clock reading, with `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off`. The window starts only if that command exits 0 and prints exactly `setUsingNetworkTime: Off`. The command's arguments, exit status, exact output and the time on both clocks are saved in the window's custody. After the last capture's last clock reading network time is set back ON, and that receipt is saved too. The read form of the command (`-getusingnetworktime`) is not evidence: without administrator rights it prints a refusal and still exits 0. Reasons: the clock method's straight-line model assumes OFF; with it ON, 4 of the 24 captures of W1 and W2 were lost to clock corrections; calibration captures should be taken in the state of the captures they will screen; and captures of unrecorded state cannot later be told apart. Setting the state from the arming session, outside the capture chain, satisfies H5 and changes no pinned file. For a window that takes calibration captures, H5 and H6 are written into the registration the window runs under before it is armed.

### 4.5 H6 (replaces A2's H6 in full)

The mechanism, drawn. Time runs left to right.

```
        W          OFF                  capture 1            capture 2    ...    capture n      Q
        |           |                  |=========|          |=========|         |=========|     |
        |           |<--- settle ----->|                                                        |
        |                        |<-L->|               |<-L->|             |<-L->|              |
  S |<------------------------ range of the window query ------------------------------->| E
```

Every element named:
- `|=========|` is one capture, from its first paired clock reading to its last.
- `OFF` is the moment the H5 command set network time OFF. `settle` is the 600 s wait after it.
- `L` is the lead, the 180 s before each capture. The first capture's lead lies inside the settle.
- `S` and `E` are the start and end of the window query: `S` is 3,600 s before the first capture's first reading, `E` is 1 s after the last capture's last reading.
- `Q` is the moment the window query is run.
- `W` is the coverage witness: a line `timed` wrote before the first capture's lead began, found in the query's output. It must lie to the left of the first `L`, because the verdict depends on the lead too.

> **H6. Every capture is attested from the `timed` log, by a query that cannot pass on a deleted log.**
> *Why.* The system deletes log lines oldest first, after about 29 hours on this machine. A query over a deleted period exits 0 and prints the column header and nothing else, which is exactly what a period without corrections prints. An empty answer therefore proves nothing by itself.
> *The window query.* Once per window, as soon as the last capture has ended, run `/usr/bin/log show --info --debug --style syslog --predicate 'process == "timed"' --start S --end E`, where S is 3,600 s before the first capture's first paired clock reading and E is 1 s after the last capture's last paired clock reading. Save the arguments, the exit status, the full output, its sha256 and the time the query ran on both clocks.
> *The coverage witness.* The output must contain at least one line written by `timed` in the log category `[com.apple.timed:data]` whose timestamp is earlier than 180 s before the first capture's first paired clock reading. Because deletion is oldest first, a log that still holds that line still holds everything `timed` wrote after it, and that includes every capture of the window and the 180 s before each. The witness line's timestamp is saved.
> *Markers.* A marker is a line containing `cmd,apply,src,`, `ntp_adjtime` or `settimeofday`. `timed` writes one whenever it moves the clock.
> *Verdict for each capture.* The capture is attested clean only if all four hold: (1) the query exited 0; (2) the first line of the output is the syslog column header; (3) the coverage witness is present; (4) no marker lies between 180 s before the capture's first paired clock reading and 1 s after its last, each end taken from both clocks and the wider reading used. If (4) fails, the capture is recorded `network_time_slew_attested`. If (1), (2) or (3) fails, or no query was run, every capture of the window is recorded `network_time_unattested`. A capture with either record is not a calibration member, not a bracket capture and not claim-bearing.
> *Sizes.* The 180 s lead exists because a slew keeps moving the clock after its log line, fading by a factor e every 16.5 s: the largest correction on record, 53.2 ms, needs 180 s to fall below 1 µs. One marker of any size excludes because with network time OFF (H5) none is expected: the two OFF nights in custody show none in 24 captures, where the ON state would have produced about 13. A marker therefore means the OFF control failed.
> *Scope.* Where a chain also runs its own query right after each capture (the chain that takes idle measurements does, over the capture ±1 s), that query stays exactly as approved, and a capture is clean only if both queries find it clean. The window query may be repeated later, for instance after a crash; a run is valid if it meets the four conditions and no run is valid without the witness. H6 was not applied to W1 and W2, which their sealed registration governs; with network time ON it would have set aside 4 of the 12 members.

**Worked example.** Take the first OFF night in custody. OFF was set at 21:00:01. Capture 1 ran 21:10:03–21:20:02. Its own log holds only the header (E6, E7): `timed` wrote nothing in those ten minutes. Under A2's H6 that header is "clean", and it would be just as clean if the log had been deleted. Under the new H6 the window query would start at 20:10:03 and the witness would have to be older than 21:07:03, the start of capture 1's lead. Network time was ON until 21:00:01, and in the 28.5 h of log I hold `timed` never went more than 31 minutes without writing, so a `[com.apple.timed:data]` line between 20:10:03 and 21:07:03 is to be expected. (I cannot show it: that night's system log is deleted.) With that line as witness, the empty ten minutes are a real finding of no correction. Run the same query two days later, as I did in E1 for another period: the output is the header alone, no witness exists, condition (3) fails, and all 12 captures are recorded `network_time_unattested`.

**Tests the implementation must carry**, each with the wrong behaviour it catches:

| Input | Expected | Catches |
|---|---|---|
| Output is the header alone | all captures unattested | accepting an empty answer (the defect of A2's H6) |
| Output has `timed` lines, none earlier than the first capture | all unattested | a witness taken from inside the window |
| The only earlier line is 100 s before the first capture's first reading | all unattested | a witness taken from inside the first lead |
| The only earlier line is in category `[com.apple.timed:text]` | all unattested | a witness from a kind of line that may be kept longer than markers |
| A marker 179 s before a capture's first reading | that capture `network_time_slew_attested` | a lead that was dropped |
| A marker 181 s before | clean | a lead that was lengthened |
| A real query over a period older than the log (live, on the bench) | all unattested | a test that only ever saw invented text |

### 4.6 H7 (replaces A2's H7 in full)

> **H7. First comparison of the two states, and no pooling before a registered rule.** For the first window at 25G83 taken with network time OFF, three things are recorded for every capture: its network-time state, with the H5 receipt and the H6 verdict; the standing rate (how fast the wall clock gains or loses against the monotonic clock, in parts per million); and the drift term. The captures' drift term and B are compared with those of the 12 members of this calibration, the number of captures set aside by H6 is stated, and the comparison is reported with the first claim-bearing results. This measures what D8 says is inferred. What the record leads one to expect: with OFF the standing rate is frozen, so every capture of a window carries the same drift term (about 0.6 and 0.7 ms per capture at the rates of the two OFF nights in custody; an earlier record gives 1.4 to 1.5 ms), where the 12 members' drift terms range from 0.74 to 1.54 ms. Every later calibration records each member's network-time state. Members captured with network time ON are combined with members captured with it OFF only under a rule written into a registration that is sealed before the OFF-state captures are taken. Without such a rule they are not combined.

### 4.7 What else the issued file must carry

1. **The network-time block is required.** `derivation_notes.network_time_provenance`, with this content:

```
"network_time_provenance": {
  "per_member_state": "on",
  "state_source": "after the fact, from the timed log and each capture's paired clock readings",
  "authenticated_off_admission": false,
  "members_with_correction_during_capture": [ <member id of W1-d12> ],
  "members_with_correction_tail_during_capture": [ <member id of W2-d01> ],
  "disclosure_id": "D8",
  "source_rulings": [ {A2: path, file sha256}, {A3: path, file sha256 as landed} ],
  "preserved_log": { "relative_path": <the .gz in evidence/>, "plain_text_sha256": "2f9bf739fde57accdce86e27a9494303585c976132e5dc5063a2cd31a5880b5c" },
  "text": <D8 verbatim>
}
```

   Member ids are the strings the candidate's `derivation_corpus` uses. The design ruling established that an added note block changes the whole-file seal and the file digest, which do not exist yet, and nothing else (its V6 and V9). I rely on that; I did not re-run it.
2. **This ruling joins the list of rulings** in `issuance_record.rulings`, as a fourth entry with id `SCI-25G83-CANDIDATE-01-A3` and the digest of this file as landed on main.
3. **Holds.** `issuance_record.holds` carries H1, H5, H6 and H7, with H5 to H7 in the text above. D1, D3 and D8 are as in §4.1 to §4.3.
4. Bindings B1 to B4 of addendum A1 continue to apply.

## 5. Does PROCEED stand?

**Yes.** The refuter concurs, having reproduced every member-level finding. My own checks add nothing against it and two things for it: the 42 corrections are reproducible from evidence that is now tracked (E9, E17), and the larger sensitivity the refuter raised runs in the strict direction (§3, S3).

What this addendum changes is text and future conditions. The candidate's 12 members, their B values, S, C and the level screen are untouched.

H5, H6 and H7 are conditions on future windows, not on the issuance. Their enforcement must land before the next window of any kind at 25G83. Today no chain meets H6. The evidence chain meets H5. The arm step of claim-bearing nights sets OFF but, by A2 §7.1, saves no restore receipt and checks nothing afterwards. The derivation chain does nothing.

## 6. What needs the owner

Nothing for the issuance.

One item before the next window that takes calibration captures: H5, H6 and the pooling rule of H7 must enter the registration by amendment (§3, S6). Amending a sealed registration adds an exclusion rule to a pre-registered study. If the project's practice is that the owner signs such amendments, this is the owner's to sign. I did not read the project's rules on that and so cannot say whether it is required.

For the owner's information, not for action: the captures ran with network time ON although the project had diagnosed the hazard five days earlier, because the control was installed in one capture chain and not the other. Four captures of 24 were lost to it. No number is wrong because of it.

## 7. Left unchecked, stated plainly

- NOT EXECUTED: any implementation of the new H6. §4.5 is a design with its tests named. Its two premises are executed (deletion is oldest first, E2; `timed` writes in both states, E7), each on one machine over one day.
- NOT ESTABLISHED: whether lines of different kinds are kept for different lengths of time. `timed` writes at three levels (in the retained log: 2,940 default, 136 error, 111 info). Every query over a deleted period returned no `timed` line of any level, so all appear to go together, but to be safe H6 takes its witness only from the category and level the markers have.
- NOT ESTABLISHED: whether switching network time OFF or back ON itself writes a marker. The system log of the OFF nights is deleted and their saved logs cover captures only. H5 puts both switches outside every capture and outside every lead.
- NOT RESOLVED: the 1 % difference between my standing rates for the OFF nights (3.58, 2.87 ppm) and the refuter's (3.62, 2.90).
- NOT EXECUTED: a re-fit of the 16.5 s decay. I used A2's value. My one check of it is W1-d01: a 470 µs tail predicts 46 µs at the third anchor reading; measured 47.8.
- NOT EXECUTED: a re-run of the estimator, of the arm path, or of the promotion tool.
- NOT RE-VERIFIED by me: A2's §7.1 map of where the arm path enforces OFF. Two seats agree on it.
- ESTIMATE ONLY: that the clock fit refuses every tail too large for the allowance (§3, S4). Two points support it. H6's lead does not depend on it.

## Summary for the owner

1. Proceed with issuance: the dissent changes no number; it changes the wording of the disclosure and the conditions on future windows, and the refuter agrees the verdict stands.
2. The refuter's blocker was right: the Mac deletes its clock log after about 29 hours and a query over a deleted period looks exactly like a clean one, so the new check must find a log line from before the window before it may call any capture clean.
3. Before the next window, network time must be set OFF and the new log check installed, and the rule must be added to the registration; the record now also says plainly that the clock hazard was known five days earlier and had been fixed in only one of the two capture programs.
