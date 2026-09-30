RULING: REV6-25G83-01 ISSUED

# Cold registration gate REV6-25G83-01: Revision 6, the successor registration for back-to-back cap-evidence windows

Judge: Claude Fable 5.1, cold session, one foreground session, 2026-09-30 05:32–05:52 PDT (20 of the 75 budgeted minutes). Worktree `/Users/edr/code/JouleWise-wt-cg-rev6-ff50b201` at `0009b976`, which is main. I changed no repository file. My two outputs are this ruling and the sealable text `22-revision6-sealable.md` beside it (sha256 `3fe5153fcd254a048f2462ddeaa7ff9cf591b088595f06eb07dbd70335b37bb3`). Scratch: `/tmp/cg-rev6-ff50b201/` (`pilot.py` `91af1b78f8fcb9cf`, `pilot2.py` `4d37544159b74d7e`).

Inputs, sha256 first 16 characters, recomputed by me: draft `16f883831ba3bbd6` (equals the charge's anchor); sealed registration `81b65f08b19127a1`; cap ruling `a90b6e768a2137f1`; addendum A1 `6b4bcaeade3f9319`; addendum A2 `ccef94f0546cde88`; erratum E1 `070dc4f05b5665c5`; cadence audit `ba8d310ae320973d`; r1 candidate `dbad7cc782945691`; session record `3d79e76a03091f58`; decision log `5a0607c631c9ffb9`.

**Result in one paragraph.** The draft's structure is sound and most of it is sealed as written. Five things change. (1) The six-hour gap is replaced by start conditions that are physical; the idle-power condition is struck because nothing can enforce it and the window shape already gives more rest than it would check. (2) §9's test-gated "blocked Q99" with four unsized thresholds is replaced by one always-computed second value with no threshold, because the drafted formula is unstable at two windows (I simulated it) and because it corrected for the wrong comparison. (3) The count rule is capped at three counting windows plus one battery replacement, as A1 R9 and E1 say, not four plus one; its second trigger reads members, not valid rows. (4) A count shortfall no longer voids the campaign; only a real R9 failure does. (5) Small corrections that keep the sealed file parseable and its statements true. Nothing the owner approved is changed, so the seal needs no second ask.

## 0. Contamination disclosure

1. **Injected by the session harness before I could act, not opened by me:** the owner's global instruction file (skill names and a writing standard, which agrees with the charge's "each term defined at first use" and which I followed); the project instruction file of this worktree (notes on the model bridge); the one-line-per-entry index of the owner's memory store; a git status with five commit subjects. The index carries one-line summaries of owner directives, among them: the threat is a wrong number and not forgery; the Mac is dedicated and windows run back to back; gates must be sensible on science grounds; stop rules are anti-spiral. The charge states each of these itself, and I rely on the charge, record item 47 and D-186 for them. The index holds no B value.
2. **Not opened:** any memory file, any skill file, `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENTS.md`, any `CLAUDE*.md`.
3. **Read in full:** the draft; the sealed registration file (Revisions 1, 2, 3, 5 and A-R5b); the cap ruling; A1; A2; E1; the cadence audit. **Read in part:** session record items 32, 34, 46, 47 and 48 (by search); the body of D-186; `90-critical-path.md` §2 to §4; the first five lines of the charge file, which equal my instructions.
4. **Code read on main `0009b976`:** the bracket evaluation and the generation-row check in `joulewise/calibration_bracketing.py` (`:398–497`, `:2364–2440`, `:2540–2652`); the issuer at `:996–1018` and `:1760–1940`; `scripts/prewindow_check.sh:29–110`; `joulewise/night_gate.py:179–187, :1559–1612`; `scripts/gen_derivation_night.py:60–75, :150–165`; `tests/test_preregistration_chain_digest.py:20–60`; searches in `joulewise/calibration_dispositions.py` and `joulewise/battery_float.py`.
5. **Same model family.** I am Fable 5.1, as were the judges of every ruling this registration rests on. The draft's writer is Opus 5.5. I sat on none of the earlier steps.
6. **Values I have seen.** The eleven 2026-09-19 B values (printed in Revision 5). From r1: one member's B (printed by my first structure listing, member w1-d04), the minimum, the maximum, the range and the two predictions with their member identifiers, and the three operatives. From my own scripts, aggregates only: per-window medians, means and SDs, the pooled SDs, ICC, the rank correlations and the Kruskal–Wallis statistic. The charge permits this reading for sizing; §5 says how it was used. No B of any new window exists.
7. **Executed.** Read-only `git`, `grep`, `sed`, `shasum`, `ls`; two Python scripts in scratch that read the r1 file and the disposition registry, call the issuer's own `student_t_quantile`, and run a simulation on invented data (seed 20260930, 8,000 replications per row; the script's header line says 20,000, which is wrong). `pilot.py` stopped at a missing `scipy` import after printing window aggregates; `pilot2.py` is the complete run. One Python check that the sealed file plus the sealable text still parses under the issuer's `preregistration_epoch_pins` and the chain-pin test's patterns. No capture, no `powermetrics`, no `sudo`, no `systemsetup`, no test suite, no background task, no subagent.
8. **Files.** The gate directory already held the charge and an empty `21-judge-stdout.txt`; I touched neither.

## 1. Words used

Terms defined in the earlier rulings keep their meaning. The ones this ruling leans on:

- **Capture**: one 197-second recording of the power sampler while the machine runs 59 commanded one-second load pulses. **B**: the one timing-uncertainty number a capture yields, in seconds. **Member**: a capture whose B enters a calibration's limits. **Window**: one unattended run of 12 capture slots.
- **Bracket**: in a claim window, one workload measurement with a calibration capture before and after it. **Drift**: the absolute difference between those two captures' B.
- **S, C, Q99**: the three limits a calibration carries besides its level screen. S is the range of the members' B (floored at 0.010818 s). Q99 is t(0.995, n − 1) × sample SD × √2, the half-width inside which two independent fresh captures differ 99 % of the time. C is max(predecessor's C, Q99, S).
- **SD**: standard deviation. **df** (degrees of freedom): the count of independent pieces of information behind an SD. **t(p, df)**: the Student-t quantile, the multiplier that grows as df shrinks.
- **Counted capture**: rule R9's unit for the cap test: the estimator's cell search ran and the capture's median frame is in 100–150 ms.
- **Adverse window**: one whose battery-float verdict fails (A-R5b). **Counting window**: one that is not adverse.
- **Blind**: without reading B or anything computed from B.
- **Review**: a consult, a cold gate or the owner (D-186).

## 2. What I verified by running or reading it

| # | Fact | Where |
|---|---|---|
| V1 | The 12 set-aside identifiers in the draft (text block and JSON) equal the registry's 12 rows under the E1 decision, in order; the mechanism text is byte-identical; the registry has 23 rows (12 + 11) and sha256 `4a3d96da…`, equal to `DISPOSITION_REGISTRY_SHA256`. The 12 are exactly the valid W1/W2 rows in r1's prior set. | my script; `calibration_dispositions.py:13, :22` |
| V2 | **What C does.** A bracket whose first capture exceeds the level screen yields no number. A bracket whose drift exceeds C is refused (`instrument_calibration_mismatch`). Otherwise its bound is max(pre B, post B) + max(drift, S). C appears nowhere in the bound. | `calibration_bracketing.py:2573–2652` |
| V3 | The validator checks the ceiling by an exact equation, C == max(predecessor C, Q99, S), for the Revision 5 epoch. A new term in the maximum needs the validator changed in step. | `:478–495` |
| V4 | The corpus-doubling count is every valid row of the judged build not set aside by a declared decision, against 2 × n. | `:2364–2440` |
| V5 | The issuer reads the registration text with two patterns that must each match exactly one distinct value in the whole file (`os_build:` followed by a value; the phrase "/usr/bin/powermetrics sha256 in force is" followed by a digest), and requires the literal "# Revision 5 (". A test requires exactly one match of "chain digest" followed by a 64-hex value. Appending my sealable text to the sealed file keeps all of these at one match, before and after the pins are filled (executed). | issuer `:996–1018, :1775`; test `:26–48` |
| V6 | The issuer keys its Revision 5 rules on the epoch alone (`target_epoch == REVISION_FIVE_EPOCH`), and Revision 6 has the same epoch. It fixes {2, 3} sessions, W1 futility and the "W3 despite 12 valid" refusal in code, and accepts `--nights-ruling` and `--slot-count-ruling` overrides. | issuer `:1769–1877` |
| V7 | `scripts/prewindow_check.sh` checks a **named list** of nine background daemons against 5.0 % CPU, the one-minute load average against 2.0, and AC power, over a 600 s continuous dwell polled every 30 s. It does not check "every process outside an allow-list", as the draft said. | `:34–38, :67–99` |
| V8 | The night gate's start-time checks already refuse a window when the load average is above 2.0 or any `CPU_Speed_Limit` printed by `pmset -g therm` differs from 100. | `night_gate.py:179–187, :1559–1612` |
| V9 | The derivation chain has one 600 s settle and no idle-power reading. | chain script `:86, :121–122, :218` |
| V10 | The proposed session-id pattern contains none of the census substrings (`codex`, `claude`, `t3`) for any date and time, because the letter T is always followed by an hour digit 0, 1 or 2; and it passes the session-id character rule. | `gen_derivation_night.py:66–69, :154–162`; `battery_float.py:44` |
| V11 | No statistics library is installed in the project's Python (no `scipy`, no `numpy`). A Kruskal–Wallis p-value would need a chi-square tail function written and pinned for the issuer. | executed |
| V12 | Current digests on main: chain `b5beea46…` (unchanged), validator `3dc75857…`, `prewindow_check.sh` `12db61a1…`, templates `e62a461b…` and `1570b745…`. Orientation only; the seal takes the values then in force. | `shasum` |

## 3. Rulings on the open items

| Item | Ruling | Where the exact text is |
|---|---|---|
| **O-1** D1 thresholds (α, median-range ratio, p-value method) | **Replaced.** No test, no α, no ratio threshold, no p-value. The window statistics are recorded and gate nothing. Reasons in §5. | sealable §9; JSON `sampling_dependence` |
| **O-2** D2 thresholds (ρ_max, minimum pairs) and the pairing rule | **Replaced.** ρ1 is recorded with its pair count and gates nothing. Pairing rule: a pair is two members in **adjacent slots** of one window; a gap is not bridged. A pair across a missing slot is 1,200 s apart and would mix two different lags. | sealable §9, "What is recorded" |
| **O-3** the blocked Q99 formula and its extreme | **Replaced** by the window-blocked value Q99_within = t(0.995, n − K) × s_within × √2, always computed. It has no extreme: its df is n − K, never below 9 under this registration's floor, and it can exceed the plain Q99 by at most 15.7 %. The 0.36 s case cannot arise. No rule reads B to decide on a window. | sealable §9 |
| **O-4** is "the larger sets C" conservative | **Yes, in the sense that matters, with one limit stated.** C only decides whether a bracket is refused (V2). A larger C refuses fewer brackets and never shrinks a reported bound; a smaller C filters brackets by machine state, which is the harm the cap ruling exists to remove. The limit: a larger C is a weaker alarm for a changed instrument. The replacement keeps the second value within a few percent of the first, so the alarm is not weakened in any material way. | sealable §9, "Why the larger value is the safe choice" |
| **O-5** idle-power reference | **Struck.** Nothing in the derivation path measures idle power (V9), and measuring it would mean running the sampler between windows. It protects nothing the shape does not: the first capture of a window has at least 1,200 s of rest after the previous window's last pulse, against 403 s for every other capture. | sealable §6.2, "No idle-power reading is required" |
| **O-6** session-id pattern | **Confirmed** (V10). Added: every derivation-kind session opened after the pinned ledger head is a window of this registration and must be named; one whose id does not match refuses. Without this a window with no valid rows and a mistyped id could drop out of the R9 record unseen. | JSON `sessions` |
| **O-7** spacing | **The six-hour clause is superseded for these windows.** See §4. | sealable §6.2 |
| **O-8** H6 and restore-ON | **The draft's reading is confirmed.** D-186 is the owner's ratified decision and it postdates A1. "With H5 and H6 met" in R9 reads "with a settled OFF receipt for the window"; K3 and the restore are withdrawn. The 5 ms limit inside the estimator remains the guard. Added, at no cost: the R9 record lists every capture refused for clock movement or an empty clock fit, so the closing ruling can see whether OFF kept the clock still. C5 and C9 need the same re-reading at the closing ruling; that is not registration text. | sealable §5, network time |
| **O-9** number of windows | **Corrected to three counting windows, plus one battery replacement, four in all.** See §6. | sealable §7 |
| **O-10** which count the second trigger reads | **Members.** The issuance floor is on members. Reading valid rows can close a campaign that then cannot issue. Members are known blind (disposition, stored anchor outcome, median frame). The futility stop keeps Revision 5's word, valid. | sealable §7 |
| **O-11** cadence stop after every window | **Confirmed,** for every counting window. The cap rule's covered range ends at 150 ms and development blocks may fall between windows. It stops to review and removes no capture. | sealable §11 |
| **O-12** append or separate file | **Append.** The issuer requires "# Revision 5 (" in the file and parses it with single-match patterns; the appended text keeps them single (V5). | sealable, whole |
| **O-13** disclosed design inputs | **Cite by file and sha256; do not retype.** Under the stated threat (a wrong number, not a forged one), a retyped list is the riskier form. The 12 r1 values are cited by path, field and digest. The 8 cap-stop values and the seats are one path-and-digest slot, because I did not locate that record in my time. The aggregates this gate computed from the 12 are printed, since §9 was fixed with them known. | sealable §3, "Disclosed design inputs" |
| **O-14** R9's "every" | **Confirmed, literal.** Every capture whose cell search ran, in range or not, and in adverse windows too. | sealable §11; JSON `stop_lines` |
| **O-15** the redundant settle | **The chain is not changed.** Its one 600 s settle is Revision 1's shape, and an extra rest period cannot make a number false. The registration requires only that the OFF receipt be 600 s old at the first capture. If the receipt is taken before the chain starts, the chain's own settle supplies that age; whether the driver also waits is an implementation matter outside the pinned chain and may be removed at any time without touching this text. | sealable §6.1, last paragraph |
| **O-16** a control pair 6 h apart | **Not required.** It would bring calendar spacing back with no number to protect. The record states every start-to-start interval, and the per-window statistics of §9 let a reader compare windows that happened to be far apart. | sealable §9 |

## 4. The spacing conflict

**The texts.** Cap ruling §6 step 7, A1 §5 step 10 and E1 §4 step 12 each say "two non-claim windows of 12 slots, at least 6 hours apart". Revision 5 line 612 is where the phrase comes from. None of the three rulings argues for it; each copies the window shape then sealed. Revision 5 itself lists its physical barriers and does not put spacing among them ("Calendar-day spacing … not physical barriers for this epoch").

**The owner's words** (record item 47, verbatim): "im literally never using the machine, this macbook is completely dedicated to this science, so again, "nights" are metaphorical, a measurement window can take place in any cadence you see fit to do the science". The cadence audit's F1 found no measured thermal, battery or clock recovery that needs six hours. D-186 records the owner's statement that "all rules are in service of the science".

**Ruling.** The phrase "at least 6 hours apart" in E1 §4 step 12, and the same phrase in A1 §5 step 10 and cap ruling §6 step 7, is **superseded for the windows of Revision 6**. Everything else in those steps stands. The authority is twofold. The schedule of a dedicated machine is the owner's to set, and he set it on 2026-09-29. Whether a registration may drop a clause without harm to a number is a cold registration gate's question under the owner's rules of the same day, and this gate finds that it may: the clause was inherited and never justified, and §5 shows that closer windows cannot make C understate what it is used for. Revision 5's own gap stays sealed for W1 and W2.

**The start conditions of §6.2, as ruled** (exact text in the sealable file): (a) the previous window finished; (b) its blind checks done and the count rule says NEXT_WINDOW; (c) agent census zero; (d) no thermal throttling at t0, by the night gate's existing check; (e) battery float per A-R5b; (f) one settled network-time OFF receipt; (g) a 600 s clean dwell, worded as the script actually works (V7). No minimum gap, no maximum gap, no time of day. The idle-power condition is struck (O-5).

**What closer windows do cost, stated so nobody is surprised.** They sample fewer machine states. S and the level screen come from the states the windows saw. A later claim window in a state outside them is refused or marks the calibration stale. That is lost yield, never a wrong number. The owner's "Mix" blocks will spread the windows in practice.

## 5. The §9 thresholds: what I computed, and the rule that replaces them

**5.1 The drafted formula is unstable at two windows.** The draft computes an effective sample size from an estimated window share (ICC) and an estimated serial correlation, then a Q99 on that smaller df. With two windows the between-window variance rests on one degree of freedom, so the estimate swings wildly. I simulated the formula on invented data where the truth is known (independent normal values; `pilot2.py`):

| Truth | Windows × members | Draft's blocked Q99 ÷ plain Q99: median | 99th percentile | largest | share of campaigns above 1.5× |
|---|---|---:|---:|---:|---:|
| no dependence at all | 2 × 12 | 1.01 | 2.08 | 22.7 | 2.8 % |
| no dependence at all | 2 × 6 | 1.02 | 20.5 | 20.5 | 12.8 % |
| no dependence at all | 3 × 12 | 1.01 | 1.23 | 1.69 | 0.1 % |
| window share 0.3 | 2 × 12 | 1.20 | 22.7 | 22.7 | 35.1 % |
| window share 0.6 | 2 × 12 | 2.08 | 22.7 | 22.7 | 59.7 % |

So with nothing wrong, about 1 campaign in 35 at two full windows would have its C inflated by more than half, and some by a factor of 20 (the 0.36 s case the draft names). On the 12 W1/W2 values the formula gives an effective size of 6 and a blocked Q99 of 0.0247 s against the plain 0.0190 s, a 30 % rise, from a window difference that is not statistically distinguishable from chance (F = 2.05 on 1 and 10 df). A test gate in front of the formula does not cure this; it only decides how often the unstable number is used.

**5.2 The thresholds cannot be sized honestly before data.** The only data are 6 + 6 members filtered by the old cap, with network time ON. They give 6 adjacent-slot pairs (ρ1 = −0.20) and 10 consecutive-member pairs (ρ1 = −0.07). Under independence the scatter of ρ1 alone is about ±0.21 at two full windows and ±0.17 at three (simulated). No ρ_max or minimum pair count chosen from that would be more than a guess, and α is a convention, not a measurement. A p-value would also need new numerical code in the issuer (V11).

**5.3 The draft corrected for the wrong comparison.** C is compared with a bracket's drift, and a bracket's two captures are always in the same window (V2). A shift between windows never enters a drift. The plain SD of all members contains that shift, so a window effect makes the plain Q99 larger than the drift it must cover. Shrinking the df on account of a window effect inflates a value that was already erring large.

**5.4 The replacement rule** (exact text: sealable §9). One second value, always computed, no threshold:

- s_within = √( Σ over windows, Σ over that window's members, of (B − that window's mean)² ÷ (n − K) ), K = the number of counting windows that contribute a member.
- Q99_within = t(0.995, n − K) × s_within × √2, in the sealed arithmetic, with its quantile proof at df n − K.
- C = max(predecessor C, Q99, Q99_within, S).

This is the textbook pooled-variance prediction for two draws from one window. Its df is exact whatever the shift between windows. It needs no ICC and no correlation estimate.

**Bound, by algebra.** The total sum of squares is never below the within-window sum, so Q99_within ≤ Q99 × √((n − 1)/(n − K)) × t(0.995, n − K)/t(0.995, n − 1). With the issuer's own quantiles: 1.027 (n = 24, K = 2), 1.033 (n = 36, K = 3), 1.070 (n = 12, K = 2), 1.157 (n = 12, K = 3). The simulation agrees (largest ratio seen 1.027, 1.033, 1.070). C can never fall below Revision 5's value and can rise by a few percent at most.

**On the 12 W1/W2 values:** Q99 = 0.01902 s (equal to r1's stored 0.019020644…); s_within = 0.004137 s; Q99_within = 0.01854 s; Q99 is the larger.

**5.5 What stays recorded, gating nothing:** per-window member count, median, mean, SD, start time and interval; the range of window medians over S; ICC; ρ1 with its pair count; both Q99 values and which term set C.

**5.6 What is not corrected, and its direction.** Serial dependence is reported only. Neighbours that resemble each other make C err large. Neighbours that alternate make C err small, which can refuse a healthy bracket. Unequal spread between windows is visible in the per-window SDs. None of these can make a reported bound too small (V2), which is why none earns a gate.

**5.7 Consequence for the code** (for WI-13 and the closing branch): the issuer computes and records `prediction_99_within_window_two_draw_s` and its quantile proof; the successor's generation row carries it; the validator's exact equation (V3) gains the term for registration revision 6. An inequality in its place would let an invented ceiling through, as the code's own comment says.

## 6. The count rule

**Against A1 R9.** R9 says: "The windows are two of 12 declared slots; a third is permitted only if fewer than 24 captures counted … If fewer than 24 count after the third window, the test has not passed and the matter returns to council." E1 step 13 says: "a third window if either trigger of step 12 fires." Neither permits a fourth window. "Maximum 4" comes from the orchestrator's outline, which no gate ruled.

**Ruling: at most three counting windows, plus at most one replacement for an adverse window (A-R5b), four windows in all.** The only case a fourth counting window would serve is 24 or more counted with fewer than 12 members after 36 slots, meaning most captures whose search ran then failed a protocol gate. That is an instrument in trouble and belongs in review, not in a fourth unattended window.

**The block's semantics, fixed** (exact JSON in the sealable file; it parses):

- Three running totals over counting windows: **counted** (from the R9 record), **valid** (ledger; used only by the futility stop), **members** (valid, anchor resolved, frame in range).
- Decision order, first match wins: (1) a stop line fired → STOP_TO_REVIEW; (2) this window is adverse → NEXT_WINDOW, the one replacement; (3) counted ≥ 24 and members ≥ 12 → CLOSE_AND_DERIVE; (4) fewer than three counting windows done → NEXT_WINDOW; (5) counted < 24 → R9_COUNT_NOT_REACHED_TO_REVIEW; (6) otherwise → MEMBERS_SHORT_TO_REVIEW.
- T-count (counted < 24) and T-members (members < 12); either opens the next window; neither opens a fourth counting window.
- An adverse window adds nothing to any total. The cadence and futility stops do not read it. The three R9 stops **do** read it: A-R5b lists the stops an adverse window is exempt from and the R9 stops did not exist when it was written, and a cap stop is evidence about the cap whatever the battery did.
- Windows are labelled C1 to C4 in ledger order, adverse ones included; "first counting window" is the first that is not adverse.

**Two corrections to the draft's consequences.**

1. **A count shortfall does not void the campaign.** The draft voided on "R9_NOT_PASSED". The cap ruling §5 item 4 voids when "R9 fails"; A1 R9 says a shortfall means "the test has not passed and the matter returns to council". A shortfall with no stop is no evidence against the cap, and making up to 35 valid captures permanently unusable for it would be an irreversible loss with no number protected. Void attaches only to the three R9 stops. On a shortfall nothing issues, B stays unread, and the review decides.
2. **Continuation after a stop.** The draft's issuer check refuses any window after a stop or review decision, while D-186 says no stop is final. Both hold under this rule: a review may continue the campaign only by a sealed amendment that the issuer reads. The issuer's command-line ruling flags (V6) are not accepted for this registration.

**For WI-13:** the issuer must tell Revision 6 sessions from Revision 5's by the session-id pattern and the pinned ledger head, not by the epoch (V6); a mixture refuses.

## 7. Anything that could make a number false, or re-introduced machinery

| # | Finding | Disposition |
|---|---|---|
| 1 | §6.2(h) described the dwell as "no process other than the allow-listed ones above 5 % CPU". The script checks nine named daemons (V7). A registration that misstates its own condition is a false statement about how the data were taken. | Reworded to the script's actual test; the script's digest becomes a pin. |
| 2 | §6.2(e) idle power could not be enforced (V9). | Struck (O-5). |
| 3 | The Kish and serial-correlation machinery, the Kruskal–Wallis test and four thresholds: new machinery with no number-protecting effect, unstable at two windows. | Replaced (§5). |
| 4 | The draft's JSON carried `"status": "DRAFT"`, a field that would have needed an unlisted edit at the seal. | Removed; the seal state lives in the header. |
| 5 | The estimator pins were one slot for four values; the ledger pin one slot for two. | Split into named slots so the block parses after the seal and nothing is left to format by hand. |
| 6 | The draft's first seal step asked the cold gate to fill threshold slots, and its grep looked for a second token. No threshold slot remains. | §13 rewritten; one token. |
| 7 | The doubling paragraph named only an unresolved anchor as a valid non-member. Valid rows outside the frame range and valid rows of an adverse window also count. | Added. |
| 8 | "Custody is sealed" was used without a definition. | Replaced by what it means: every evidence file written and its digest in the ledger. |
| 9 | No estimator byte, protocol, membership rule, S rule or level-screen rule is touched. No B-based exclusion or top-up exists anywhere in the text. | Checked. |

**Seal notes for the lead** (not registration text): (i) add a test that the JSON block's `pins.chain_sha256` equals the tracked chain, beside the existing Revision 3 test; if the chain digest ever differs from Revision 3's, that older test's expectation must move too. (ii) Any edit before the seal must keep V5's single-match properties; never write "os_build:" followed by a value, the powermetrics phrase, or the words "chain digest" directly before a 64-hex value. (iii) The sealable file is appended whole and alone; this ruling is not appended.

## 8. Noticed, not ruled

1. **The successor will go stale fast in claim use.** The doubling count includes every valid capture of the build, so the calibration captures of claim brackets count (V4). A successor with n = 24 goes stale after about 24 more valid captures, roughly 12 brackets. That is the sealed D-102 design and no number is at risk, but it bounds claim throughput and argues for planning the first re-derivation before the claim windows start.
2. **I did not verify that the derivation arm path runs the clean dwell.** `prewindow_check.sh` is referenced by the claim-window path. If the derivation path does not produce its evidence, the condition of §6.2(g) must be wired before C1, or the arm must refuse.
3. **The closing conditions C5 and C9** still speak of H6 and the restore. They need D-186's reading at the closing ruling.

## 9. Left unchecked, stated plainly

- NOT EXECUTED: the issuer, the validator, the night gate, the chain, any test, any capture. Every statement about their behaviour is from reading the cited lines, except the parse check of V5, which I ran.
- NOT EXECUTED: a Decimal-exact computation of s_within at the issuer's presentation quantum. My figures for the 12 W1/W2 values are binary64, good to the digits printed.
- NOT LOCATED: the record that prints the 8 cap-stop diagnostic B values; it is a path-and-digest slot in §3 of the sealable text.
- NOT ESTABLISHED: how far apart a claim bracket's two captures are. §5 assumes a few minutes, as the rulings' definition of a bracket implies. If they are much further apart than the 600 s slot pitch, the statement "neighbours that resemble each other make C err large" weakens toward neutral; it does not reverse.
- NOT READ: NTP-THIN-01, the hold ruling, the D-138 design ruling, the WI-13 and WI-16 branches.
- The sealable text leaves 19 pin slots: the ruling digest, P8's two digests, the disclosed-inputs record, and 15 in the JSON block.

## Summary in three lines

1. Windows may now run back to back: the six-hour gap is replaced by physical start conditions (previous window finished and checked blind, no agents, no throttling, battery float, network time OFF for 600 s, a 600 s clean dwell), and the owner's words of 2026-09-29 are quoted as the authority.
2. The statistics for close windows are simpler and safer than drafted: one extra value computed from the spread inside windows, always taken into the maximum that sets C, with no threshold to choose; I showed the drafted formula could inflate C twentyfold by chance at two windows, and that C only ever decides whether a measurement is refused, never how small its reported uncertainty is.
3. The window count is two, a third if fewer than 24 captures counted or fewer than 12 are members, never a fourth, plus one replacement for a battery-confounded window; a shortfall goes to review without voiding the captures; the sealable text is complete with 19 digest slots left to fill, and nothing the owner approved was changed.
