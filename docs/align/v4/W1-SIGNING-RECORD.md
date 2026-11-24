# W1 signing record: the lead's records owed before the signing commit

2026-11-24. These are lead records that the research lead's rulings require to be on the W1 line before
the W1 receipt is signed. They are recorded under lead decision D2b of 2026-11-24 00:30 PST, which
authorized the integration owner (seat `opus-w1-integration-owner-1123`, Claude Opus 5.5) to record them.
`RLD:n` is `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md` at
`origin/audit/2026-11-10-fable` `d6ab64823`; RL-203 to RL-213 were committed there at `a2cb8bcc8`. PIN is
`b2e01464d`.

**Blind.** Only rulings, code, CI logs of synthetic tests and public pins were read.
`inputs.json` values, `r1_slots.json`, the planning release and every custody, energy, power, meter,
transcript, slot, hazard or sealed file stayed closed.

## 1. PR #813: RL-182b's four conditions (RL-203; RL-193 §3 item 3)

RL-182b (RLD:21486-21494) makes #813 sign-ready "when all four hold. The lead confirms them; none returns
to me." RL-203 (RLD:25470-25475) rules condition 1 met at `82542232d` and that no round 8 is owed.

| # | Condition (RLD:21489-21492) | Record at #813 `82542232d` |
|---|---|---|
| 1 | The change from `2fe705e73` touches only `TM`, `CB` and a run report | **Met (RL-203).** The diff from `2fe705e73` is seven files and nothing under `joulewise/` or `scripts/`. The four files beyond the two tests and the run report are review records no round judged: two rows in `configs/b6/executing_reviews.json`, the citation paper and Astra's round 5 and 6 reports. The rows exist because the append-only review-row test was red without them. The adapter's whole-file digest is still `578455fa…9336` |
| 2 | The new test carries the block digest and reads the file from disk | **Met.** `tests/align/test_measurement_core_boundary.py:67-78@82542232d` carries `85ffe1a3…45c5` and reads the bytes from disk (RL-203) |
| 3 | CI is green | **Met.** CI 21 green at `82542232d` (RL-203) |
| 4 | W1's hashes are refreshed after the change | **On the final tree** (RL-203). It is the W1 candidate's final regeneration and receipt (trial PR #958 runbook §9, steps 1 and 3), not a #813 commit |

The E1–E17 list (RL-193 item 3) is checked mechanically. `tests/align/test_rl182_registration.py` finds each of
the seventeen edits once at its ruled location. E2 is E2 as amended by RL-193 §7, and that clause is
PR #960 (RL-212). #813 folds into W1 at `82542232d`. PR #944 carries it by merge (`bef3ea87c`, lead L1),
and RL-206 accepts the resulting protocol text.

## 2. PR #826: the cause of the intermittent TERM test (RL-204)

RL-204 (RLD:25477-25482): "Before the signing commit the lead records one line on the cause: the test's
wait, or the runtime's bounded close."

**Cause: the test's wait, not the runtime's bounded close.** The test sends SIGTERM the moment
`align_thermal.jsonl` first exists (`tests/align/test_r1_runtime_e2e.py:109-114@1fc28324d`), and that
instant falls in the thermal sidecar's start-up in the runtime child (`thermal.py:131-142`). On the
failing run the close never wrote `session_end` (`thermal.py:193`). The 15 s forced close
(`TERM_TEARDOWN_S`, `r1_runtime.py:67`; watchdog `r1_runtime.py:1236`) did not fire.

Evidence for the line:
- In the one red run (ci [44301231408](https://github.com/mpmdw/JouleWise/actions/runs/44301231408) at
  `3dfeadc0c`), every assertion before the last held: rc 4, `world.mode == 0`, `r1_result.json` aborted,
  custody aborted with SIGTERM, and `summary_metrics.json` present. Only the last line's `kind` was
  `reading`.
- That module's time was 27.8 s. That is inside the range of the passing runs: 23.2 s to 35.2 s, in runs
  44332438937, 45320845308, 45338335723, 45340766338 and 45345268049. A forced close would add at least
  15 s.
- The test was observed red in 1 of these 6 CI runs. The ten sources are PIN's in all of them.

**Open, for the research lead if confirmed.** If a SIGTERM inside the member's `prepare` leaves the
sidecar unstopped, the gap is in one of the ten. `prepare` starts the thermal session and closes it only
on `except Exception` (`workload.py:243-254, 293-294@b2e01464d`), and `SystemExit` is a `BaseException`,
which those handlers do not catch. W1 members run the same `prepare`. RL-204 returns the question to the
research lead "only if the cause is in the ten and W1's abort path shares it". The mechanism has not been
reproduced, so this is named and not claimed. A member aborted this way is aborted in any case. No edit
to the ten.

## 3. The anti-hindsight list (RL-183 §2.7; RL-189 §2.5 items 3 and 4; RL-193 §3 item 4)

RL-183 §2.7 (RLD:20271): "every analysis rule changed since R1's record existed, each with its ruling id.
A change with no ruling id is a deviation and returns under the existing rule." The list goes to the
research lead.

**Reference point.** The first R1 session of 18 November: plan `align-r1-20261118T1445Z`, 06:45 PST.
The slot record's own session came later: plan `align-r1-20261118T2350Z`, t0 15:50 PST, item 440. Using
the earlier session covers both. Rulings from 01:08 to 04:57 on 18 November are listed below the table.
R1 sessions of 10–13 November also exist. If "R1's record" is meant to reach back to those, the list
extends back to RL-1xx. That is the research lead's call in the cold pass.

**The two lines RL-189 §2.5 requires**
- **The reduced cap (item 3).** The X-G contrast's G0 cap is 488 s against a nominal 600 s, and the R1
  record predeclares why. The contrast is a non-veto `INCONCLUSIVE`, which is the pinned rule, and it
  stays `INCONCLUSIVE` in every W1 print. No W1 report reads it as a pass or a fail (RL-189 §2 and
  §2.5 item 3, RLD:22176, 22190).
- **The two sessions (item 4).** The slot record is the session armed under item 440, fixed before it
  ran: plan `align-r1-20261118T2350Z`, t0 Wed 18 Nov 15:50:00 PST, under RUN_STATE item 444's ARM
  RECORD. The first session of 18 November (`align-r1-20261118T1445Z`) is superseded. No value was chosen
  between the two (RL-189 §2.5 item 4, RLD:22191).

**Analysis rules changed since the reference point**

| Ruling | Date (PST) | What changed | Where it lands |
|---|---|---|---|
| RL-189 §2 | Thu 19 Nov 14:11 | The X-G contrast is a non-veto `INCONCLUSIVE` with its G0 cap at 488 s, against a nominal 600 s (the first line above) | #886's fill; every W1 print |
| RL-193 §7, as amended by RL-212 | Fri 20 Nov 09:17; Mon 23 Nov 21:55 | A rank-deficient S fit publishes. The member stays eligible, enters Q and leaves S with `s_score_undefined`, cause `rank_deficient_design`. It is registered as E2's fourth cause | PR #960 (P4 B2, the amendment draft, the E2 fixture); C1's release script carries the cause word |
| RL-198 | Sat 21 Nov 23:21 | Option C is registered as four positive-control windows, P1 to P4 (B10). K's disclosure becomes the `k_positive_control_*` code | PR #944 |
| RL-198a | Sat 21 Nov 23:37 | Council table row 2 now names RUN_STATE 532 and B10 | PR #944 |
| RL-200 | Sun 22 Nov 00:22 | RL-198's four windows are kept. The dose run may move to calibration completion | PR #944 (B10) |

**Considered, no analysis rule changed**
- **RL-182b** (Wed 18 Nov 11:30): "This changes a test, and no score, level, field or rule".
- **RL-186** (07:30): #809's Part C replay contract and the ctl-01 kit.
- **RL-187** (14:55): PR #828, the cadence looks.
- **RL-206**: a text union of RL-198's K clause and RL-182 E11's S clause, both already ruled.
- **RL-207**: "No anti-hindsight line is owed".
- **RL-203 to RL-205, RL-208 to RL-211, RL-213 and RL-214**: process, census, suite, receipt, ctl-01 and
  `lm-interim-01` items.
- **The lane rulings with no v4 rule**: RL-188, RL-190 to RL-192, RL-194 to RL-197, RL-199, RL-201 and
  RL-202.

**Just before the reference point, 18 November**
- **RL-182** (01:08): seventeen edits, E1–E17.
- **RL-182a** (01:31): the decode-only row starts at `Turn.first_token_ns`.
- **RL-183** (01:46): the Part C evaluator and the packet.
- **RL-185** (04:53): the Part C soak ledger, and Q SHIFT with no defined percent.
- **RL-184** (04:57): freeze 2 and qualification.

These predate both 18 November sessions. They are listed so the cold pass can see the boundary.

## 4. Known limitation: the S6 registration shares `r1_slots.json` (lead D1)

Lead decision D1 (2026-11-24 00:30): no frozen-source change now. R1 is complete (RUN_STATE 459) and no
R1 re-run is planned, so the shared path harms no data.

> `r1_slots.json` now holds the R1 record; before ANY R1 re-run from this tree, split the ruled S6
> registration into `registration/r1_s6_registration.json` and rebind `r1_runtime` (cited rebind, new pin).

The mechanism: `joulewise/align/apple/r1_runtime.registered_s6()`, one of the ten frozen sources, reads
`configs/campaigns/align_v4/registration/r1_slots.json` as the ruled S6 registration. After PR #886's
fill, that file is the R1 hardware record, and its `s6_tuning` has no `from_c` or `to_c`. The synthetic
driver tests pin their own registration through `synthetic_s6_registration()` in
`tests/align/test_r1_rehearsal.py`, which PR #886 added at `8fc76a0b9`. That helper stays. The deviation
list carries the same row as `R1-S6-SHARED-PATH`.
