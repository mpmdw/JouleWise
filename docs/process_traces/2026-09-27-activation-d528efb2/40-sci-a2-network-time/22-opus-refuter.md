REFUTER: DISSENT

# Opus 5.5 refuter on cold addendum SCI-25G83-CANDIDATE-01-A2 (`21-ruling.md`)

Refuter: Opus 5.5, paired contract-lens seat, 2026-09-27 ≈18:25–19:10 PDT. Read-only everywhere; no capture, no power sampler, no system setting changed; no git writes. Scratch: `/tmp/cg-scia2-d528efb2/opus-refuter/`.

**Scope of the dissent.** I concur with the verdict **PROCEED** for the D-138 issuing transaction, and with the ruling's core findings on questions 1 and 3. I dissent on one binding condition (H6, one BLOCKER) and on the D8 text and evidence handling (SHOULD-FIX). None of my findings changes a member, a B value, S, C or the level screen.

Terms follow the ruling's §1 glossary. Two terms I add:
- **Anchor stamps**: the five paired wall/monotonic readings the clock-fit code uses (`pre_spawn`, `first_parse`, `sampling_started`, `post_parse`, `sampling_stopped`). The code requires one straight line to pass within about 1 µs of each of them. There is no 250 µs allowance on these five.
- **Log rotation**: macOS deletes old unified-log entries. After deletion, a `log show` query over that period still exits 0 and still prints the column header. It just returns no entries.

## What I re-executed, and where I agree

| Claim in the ruling | My independent result | Agree? |
|---|---|---|
| 42 applied corrections, 00:00–03:00 and 08:30–11:30 (8 ms-size, 34 µs-size) | `/usr/bin/log show --info --debug --style syslog --predicate 'process == "timed"'`: 42 `cmd,apply` lines (pulls `log_w1.txt` `73661a94…`, `log_w2.txt` `a40cd6bf…`) | Yes |
| Per-member table §3.1 (interval, corrections inside, moved/predicted, excess, departure) | `recon.py` (`2c900088…`) uses 129 paired readings per capture and the `ntp_adjtime` frequency lines. Every member matches the ruling to within 0.5 µs: W1-d12 excess +40.1, departure 17.6; W2-d01 excess −11.5, departure 8.2; the other ten have excess between −0.6 and +1.0 µs and departure ≤3.7 µs | Yes |
| No step and no ms-size correction inside any member | Confirmed. Nearest is W1-d04: a −12.579 ms slew 175.4 s before its start, measured excess −0.1 µs | Yes |
| The drift term covers the two touched members | W1-d12: moved 1529.5 µs, charged 1536.8 µs. W2-d01: moved 1171.5 µs, charged 1173.0 µs. In both, the correction pushed the same way as the frequency drift, so the five-stamp range contains the whole movement | Yes |
| Member evidence digests | 12/12 `instrument_evidence.json` and `manifest.json` match the candidate | Yes |
| Statistics and the 8.9 µs counterfactual | `cf.py` (`23cf5af8…`): range 13,701.5 µs, Q99 19,020.6 µs. With the two excesses removed, Q99 = 19,029.6 µs (+8.9 µs) | Yes |
| The four NTP losses; the 8 work-cap exclusions are unrelated | The 8 capped captures have departure ≤4.4 µs and no correction inside. W2-d12's +38.8 ms slew came 236 s before its start and leaves about 0.02 µs | Yes |
| §7.1 code map | Verified `run_night.py:1982`; `arm_readiness_evidence_t0.py:1225–1256`; `arm_readiness.py:104`; `d117_row_registry_v2.json` row `clock.network_time_off` (`volatile_20m`); `scheduler_c4_network_time_on` declared at `scheduler_gates.py:94` and produced nowhere. The derivation chain, `night_gate.py` and the derivation runbook have zero relevant hits (the generator's 2 hits are `argparse`). Only `quiet_predicate_campaign.py` calls `establish_network_time_off`, `attest_network_time` and `restore_network_time` | Yes |
| `systemsetup -getusingnetworktime` is untrustworthy | Ran it: prints "You need administrator access…" and exits 0. `sudo -n -l` grants only the two set forms | Yes |

Question 3: no exclusion is selective on B. What triggers each of the four clock exclusions is the timing of a `timed` correction. That timing is set by `timed`'s own scheduler and cannot see the power trace. I concur.

## BLOCKER

### B1. H6 lets the log query run at harvest. After log rotation, that query returns a result that passes as clean.

H6 says: "The query may be run at harvest; the log was still complete 16 hours after W1 … An output that lacks the log's column header is a failed query, not a clean one."

Executed:
- The oldest `timed` line still stored on this machine is at **2026-09-26 13:06:41**. That is about 29 h before this session.
- I queried `timed` over periods older than that:
  - 2026-09-22 20:40–23:30
  - 2026-09-22 23:13–09-23 02:00 (network time back ON from 23:13:51, when `timed` would normally sync)
  - 2026-09-23 06:40–09:30 and 09:14–12:00
  - 2026-09-26 00:00–03:00

  Every query **exited 0 and printed exactly the syslog column header plus zero entries**.
- Other processes do still have sparse entries for those times: 70 lines in 30 s at 09-22 22:00, against 7,634 at 09-26 14:00. So the `timed` entries were deleted. The query did not fail.

**Consequence.** A query run after rotation passes H6's header guard, counts zero corrections, and would certify a capture whose clock history can no longer be known. H6 applies to "every capture of every window", so this includes claim-bearing captures. That is a false-clean path in exactly the evidence that decides whether a number is true.

**H6 also contradicts the ratified method it would sit beside.** The evidence chain's `attest_network_time` (`joulewise/quiet_predicate_campaign.py:695–714`, A267/A269 rulings) says to "Run immediately after the collector exits … because the log store is rotated -- never deferred to harvest". Its query window is `epoch_monotonic_union_v1`: the capture interval ±1 s, with no 300 s lead (lines 610–636). The ruling's §8 lists this lead as NOT EXECUTED. I checked: there is no lead. As written, H6 would change a cold-gate-ratified claim-path method through an addendum about a calibration candidate.

**Required change to H6 before it is installed:**
- Strike "may be run at harvest". Require the query immediately after each capture, as the ratified chain already does.
- Or require positive proof that the log still covers the window. Example: a `timed` entry retained from before the window start, with its timestamp recorded. A header-only result is then "unattested", never "clean".
- Any change to the evidence chain's window (the 300 s lead) goes through its own gate.

This does not block PROCEED. It blocks H6 as a binding condition in its current words.

## SHOULD-FIX

### S1. (Time-critical) The primary log evidence for D8 is not in the tracked record, and the system log will delete it within hours.

- The ruling cites its two full log pulls only by digest (`aac85b47…`, `14ca9501…`). Both files are in `/tmp/cg-scia2-d528efb2/`.
- The tracked record holds:
  - `timed.txt`: 82 lines, 4 `cmd,apply`, 6 `ntp_adjtime`.
  - `applies.txt`: 26 of the 42 corrections, and **no** frequency (`ntp_adjtime`) lines.
- The frequency lines are the basis of every "predicted movement" and "excess" in §3.1, and of the "42" in D8.
- At about 29 h retention, the W1 entries (from 00:02) will be deleted around 05:00–06:00 PDT on 2026-09-28.

**Remedy:** copy both full pulls (the judge's, or mine: `log_w1.txt` `73661a94…`, `log_w2.txt` `a40cd6bf…`) into this directory before then, and before D-138 starts.

The per-member finding that each member's clock is clean survives either way, because each capture's 129 paired readings are permanent in custody. The excess figures and the correction count do not.

### S2. D8 overstates the rule: "the clock method requires network time OFF only of claim-bearing captures".

What the sources actually say:
- The method's docstring (`uncertainty_evidence.py:902–909`):
  - OFF is what makes the straight-line model admissible.
  - A capture with network time ON or unknown "is validation-only material".
  - "Per-member network-time provenance therefore travels with every record derived by this method."
- The docstring says nothing about calibration members either way.
- The only precedent (r7, `derivation_notes.network_time_provenance`) excused **historical** unknown-state material. W1 and W2 are **prospective** captures.

The hazard was already known in the project five days earlier:
- `README.md:17` and `docs/process/state_kernel.json:7620` record the 2026-09-22 pilot night: `timed` "slewed the wall clock by 4 to 22 ms at its ~30 min NTP syncs", and 7 of 12 envelopes were lost.
- The A267 cold gate that day (`docs/process_traces/2026-09-22-activation-d9990b3c/01-coldgate-packet-a267-clock-discipline-anchor/10-coldgate-fable-ruling.md` Q1) ruled OFF-before-settle for the evidence chain. It did not reach the derivation chain.
- The instrument guide §4.7/§5 (`docs/guides/instrument-guide.md:760–770, 930–933, 970–977`) says the OFF window is what makes the model "admissible". It also records two earlier corpus refusals caused by exactly this steering.

So "no registered rule was breached" is true. But the addendum's framing is not: the ruling says the cause is newly found and closes H4's "cause is sought" as "found". The science gate's "unknown cause" was itself a miss of a mechanism the project had diagnosed on 09-22.

**Remedy.** D8 should replace the quoted clause with words to this effect:

> No registered rule required it. The clock method's model assumes network time OFF, and its only precedent excused historical material. These were prospective captures, taken five days after the mechanism was diagnosed (A267, 2026-09-22). The derivation chain was never brought under that control. These members' admissibility rests on the post-hoc clock measurement in this addendum, not on the structural control.

### S3. D8 reports only the 8.9 µs effect. The ON-versus-OFF sensitivity the ruling computed itself is about 60 times larger, and on-disk OFF evidence contradicts one of its premises.

**The sensitivity.**
- Under ON, `timed` reset the frequency setting 8 times, so members' drift terms ranged from 741 to 1,537 µs.
- Under OFF, the frequency is frozen, so the drift term is constant within a window.
- Replacing each member's drift term with any constant gives S +505.0 µs (14,206.5) and C +554.4 µs (19,575.0). This holds for any constant (`cf.py`).
- The level screen moves by (constant − 741 µs).
- The ruling reports these numbers in §3.4, then dismisses them because "turning network time OFF does not remove it … 7.24 and 7.60 ppm … about 1.4 to 1.5 ms".

**The OFF evidence already on disk.** It was available read-only, and the ruling lists it as NOT ESTABLISHED:
- Nights `qpe01-pilot-n1-20260922-2100…` and `…20260923-0700…` both carry `network_time_control.json` with an exact `Off` receipt.
- All 24 envelopes (about 600 s each) are `network_time_provenance.state = off`, attestation `authenticated`, `matched_lines = 0`.
- The wall-versus-monotonic rate was constant within each night to ±0.003 ppm, at **3.62 ppm** and **2.90 ppm**. That is a drift term of 719 µs and 577 µs per 198.6 s capture, not 1.4–1.5 ms.
- So the drift term under OFF is window-constant, and its level is whatever `timed` last set.
- Zero corrections in about 4 h of OFF capture windows, against 11 push-notification triplets in about 6.5 h under ON, is strong evidence that OFF also silences the µs corrections (the ruling's open item (ii)).

**Direction.** The issued S, C and level screen are stricter (smaller) than the constant-drift counterfactual. That costs yield. It does not make the calibration less conservative. So this does not threaten PROCEED.

**Remedy.** D8 should state the magnitude and direction:

> The ON regime's changing frequency setting made S and C 505 and 554 µs (2.9 %) smaller than a constant-drift regime would. OFF nights on record held a constant drift of 577–720 µs per capture.

H7 stays as the measurement at 25G83.

### S4. W1-d01's refusal mechanism is mis-stated. The conclusion stands.

- §5.1 says a 345 µs departure "from the best line" exceeds the 250 µs allowance, "so the fit was rightly refused". But 345 µs is the largest residual from the least-squares line. The best (minimax) straight line through the 129 readings departs by only **170.2 µs**, under 250 (`minimax.py`, `0810fe1f…`).
- The actual cause is that the five anchor stamps cannot lie on one line:

| Stamp | Time after `pre_spawn` | Off the `pre_spawn`→`post_parse` line |
|---|---:|---:|
| `first_parse` | 1.03 s | −27.9 µs |
| `sampling_started` | 1.86 s | −47.9 µs |

  The slew tail was moving the clock about 30 µs/s during those first two seconds.
- In code, the native-record rows are feasible, and adding the stamp rows (about 1 µs resolution, no allowance) makes the set empty. That gives `affine_clock_fit_empty` (`uncertainty_evidence.py:1228–1232`).
- W1-d01 is still the fourth NTP loss. The finding is stronger than stated: the stamps catch a tail at capture start at µs scale.
- Recommendation (i) proposes thresholding the least-squares departure. That is not what the code tests. Any registered diagnostic should be the stamp non-collinearity or the minimax residual.

### S5. H6's zero-tolerance rule with a 300 s lead would have excluded half of this candidate, including the member that sets the level screen.

Applying H6 to the 12 members (`cf.py`), these six have a `cmd,apply` line in the window from 300 s before start to the end of capture:
- W1-d04: ms slew 175 s before
- W1-d12: inside
- W2-d01: 22 s before
- W2-d04: 218 s before
- W2-d05: 214 s before
- **W2-d10**: 133 s before; this member sets the level screen

The ruling itself finds all six clean, with a margin of at least 6× against the allowance.

Problems:
- A count above zero is not a tolerance sized to the instrument.
- Future generations would be selected by a different rule from this one. That muddies H7's comparison and any pooling.
- Under H5 (OFF plus the 600 s settle, which A267 Q1 rule 1 relies on to absorb in-flight slews) the lead is largely redundant.

**Remedy:** a size-based criterion registered before use (for example, the tail left at capture start from the applied amount and the elapsed time, against a stated µs bound), or keep the ratified ±1 s window.

### S6. Provenance has to travel with the artifact, and the ruling must say whether ON and OFF members may be pooled.

- The method says per-member provenance "travels with every record derived by this method". The predecessor r7 carried a `network_time_provenance` block. The ruling leaves adding one optional.
- Anyone who reads the issued JSON will not see D8.
- The candidate registers a corpus-doubling trigger (12→24). A successor corpus would mix these 12 ON-state members with OFF-state captures.

**Remedy:**
- Require the block in `derivation_notes`, if the gate confirms it changes no member, statistic, operative number or pinned estimator digest. Otherwise require the issued notes to bind D8 by digest.
- Rule now whether ON and OFF members may be pooled, and if so how the state is recorded per member.

## NIT

- N1. Line 6 says the addendum "adds two conditions … (H5, H6)", and line 212 says "H5 and H6 below now govern". There are three (H5–H7).
- N2. §7.2 says that without `--info --debug` "the correction lines are dropped". Here they are not. The same W1 query without the flags returns the same 331 lines and 20 `cmd,apply` lines, because they are Default-level entries. Keeping the flags is harmless; the stated reason is wrong.
- N3. D8's "within ±7.5 parts per million": the setting at 01:07:12 was −7.503 ppm, and −8.678 ppm was in force until 09:00:03, during W2's settle.
- N4. Of the "34 of microsecond size, in groups of three … from APNS" (Apple's push-notification service), one (01:53:09.225, +41.6 µs) is the slew that accompanied the step. The count is 11 triplets plus 1.
- N5. The p = 0.31 chance calculation counts only corrections inside a capture, while the fourth loss was a tail. It is fine as an illustration, but it is post hoc.

## Summary

1. PROCEED stands. I reproduced every member-level clock finding, the 12 digests, the statistics and the 8.9 µs counterfactual. No exclusion selects on B.
2. BLOCKER on H6: `timed` log entries are deleted after about 29 h, and a query over the deleted period exits 0 with its header, so a harvest-time query can certify a capture as clean. Keep the ratified "query immediately after capture, never at harvest" rule.
3. SHOULD-FIX:
   - Copy the full log pulls into the record before about 05:00 PDT on 09-28.
   - Correct D8's "OFF only for claim-bearing" framing: the hazard was diagnosed and ruled on 09-22.
   - Disclose the 505/554 µs ON-versus-OFF drift sensitivity, using the on-disk OFF nights (constant 2.90 and 3.62 ppm).
   - Restate W1-d01's mechanism (non-collinear anchor stamps, not the 250 µs allowance).
   - Resize H6 (as written it would drop 6 of 12 members).
   - Require provenance in the artifact and a ruling on pooling ON and OFF members.
