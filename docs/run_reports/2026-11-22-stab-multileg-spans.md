# Stability fillers, three legs per soak, 2026-11-22

RL-200a resolved the preflight and authorizes the existing pins. The lead
also tightened pin A's multi-leg admission to keep every leg start out of
02:00–02:35. The branch fast-forwarded to the remote audit base
`08624dbc9b7ef650ac085e99aa513af505f57975` before implementation.

The generator adds 336 W2 and 777 W3 alternatives, one file per possible
start and length. The magistrate uses the existing issued and Check records
to determine which positions are unrun at dispatch. Each week's README lists
the SHA-256 of every queue. [W2 queue index](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/fillers-w2/README.md)
· [W3 queue index](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/fillers-w3/README.md)

## Clock admission

Under RUN_STATE 463, pin A tries `02:00-02:35` then `13:14-13:15`
for each candidate. At 23:30 PST the primary argument admits one leg and
refuses two and three. The alternate admits all three lengths. Pin B omits
the argument. At 00:00 PST an explicitly supplied `02:00-02:35` admits one
leg only, and omitting it admits all three lengths. See
[A `scripts/launch_cadence_span.py:58–72`](https://github.com/mpmdw/JouleWise/blob/2d347f721552fe03bdd19f113e7bad7a7c24908e/scripts/launch_cadence_span.py#L58-L72),
[A `joulewise/cadence/legs.py:305–322`](https://github.com/mpmdw/JouleWise/blob/2d347f721552fe03bdd19f113e7bad7a7c24908e/joulewise/cadence/legs.py#L305-L322), and
[B `scripts/launch_cadence_span.py:60–72`](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/launch_cadence_span.py#L60-L72).

With those permitted arguments and the RUN_STATE 507 soak rule, all lengths
share the following clock bands before the lead's final pin-A tightening
(PST, inclusive).

| Pin | Admitted `t0` |
| --- | --- |
| A | 00:00:00–01:27:30, 02:35:00–10:50:00, 13:15:00–23:59:59 |
| B | 00:00:00–01:27:30, 02:35:00–23:59:59 |

The dated-block rule is an additional scheduling check. A filler must leave
each pending dated block enough time to take its remaining starts by
23:59:59 after the filler and its close. For synthetic starts at 21:20 on
pin A or 20:50 on pin B, the configured fence plus a synthetic 1,200 s close
allowance leaves room for a counted start at 23:59:59 after one filler leg.
Two and three legs both miss that cutoff. An ordinary filler can cross
midnight when there is no dated block to protect. See
[RL-179 F-1 and RL-200 §2.2](../research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#f-1-the-date-rules),
[RUN_STATE 463](../../RUN_STATE.md#L2201), and
[RUN_STATE 507](../../RUN_STATE.md#L1213).

### Pinned planner bounds and the pin A start check

All times are PST. The `23:59:59` columns subtract the stated work duration
or configured fence from the deadline. A dated block's earlier starts and
any separate close or handoff time can move its actual cutoff earlier.
Apply the queue's date gate and expiry separately, including its midday
expiry on the final date.
The explicit-band column is the latest admitted start before the 02:00 band when
the explicit `02:00-02:35` argument is supplied. Pin B's such column is
diagnostic because RUN_STATE 463 omits the argument there. Under the
permitted arguments on both pins, RUN_STATE 507's 1,950 s soak reaches 02:00
at a latest pre-band `t0` of 01:27:30 for all three lengths. The final
column gives the stricter pin-A multi-leg cutoff with the alternate ARG.

| Pin | Legs | Worst-case work (s) | Pinned launch minimum (s) | Configured fence (s) | Latest `t0` for work by 23:59:59 | Latest `t0` for fence by 23:59:59 | Latest `t0` before 02:00 with explicit band | Latest `t0` before 02:00 with pin A alternate and start rule |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A | 1 | 5,850 | 6,410 | 7,310 | 22:22:29 | 21:58:09 | 23:48:10 previous day | 01:27:30 (soak only) |
| A | 2 | 8,550 | 9,110 | 10,010 | 21:37:29 | 21:13:09 | 23:03:10 previous day | 23:13:10 previous day |
| A | 3 | 11,250 | 11,810 | 12,710 | 20:52:29 | 20:28:09 | 22:18:10 previous day | 22:28:10 previous day |
| B | 1 | 5,850 | 8,360 | 9,260 | 22:22:29 | 21:25:39 | 00:22:30 | — |
| B | 2 | 8,550 | 11,060 | 11,960 | 21:37:29 | 20:40:39 | 23:37:30 previous day | — |
| B | 3 | 11,250 | 13,760 | 14,660 | 20:52:29 | 19:55:39 | 22:52:30 previous day | — |

Use the pin-A fence as a conservative upper bound on leg starts. The
pinned plan gives duration caps and estimates. With the alternate ARG,
require the half-open interval from actual `t0` to the armed fence deadline
to clear every local 02:00–02:35 band for lengths two and three. The runner
reserves cleanup before that deadline. The primary ARG's 01:50 fence limit
is stricter. In the evening, pin A may choose three legs through 22:28:10,
two legs through 23:13:10, then one where the other checks pass. Lengths two
and three resume at 02:35. Recheck using the actual planned fence immediately
before launch. [A `scripts/cadence_legs_runner.py:327–331`](https://github.com/mpmdw/JouleWise/blob/2d347f721552fe03bdd19f113e7bad7a7c24908e/scripts/cadence_legs_runner.py#L327-L331)

Pin A's fence includes 1,460 s beyond work and its explicit band adds a
600 s lead. Pin B budgets one 1,950 s soak retry plus 560 s of reserves
in the launch minimum. The configured deadline adds a further 900 s.
Pin B's explicit batch overlap test uses the work bound. See
[A `scripts/cadence_legs_runner.py:835–843`](https://github.com/mpmdw/JouleWise/blob/2d347f721552fe03bdd19f113e7bad7a7c24908e/scripts/cadence_legs_runner.py#L835-L843),
[B `scripts/cadence_legs_runner.py:125–133`](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L125-L133), and
[B `joulewise/cadence/legs.py:350–362`](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/joulewise/cadence/legs.py#L350-L362).

## Receipt position

The synthetic two- and three-leg runs returned rc 0 on both pins. Each
`runner_receipt.json` contained the submitted `roster` in order and the
corresponding `legs` rows in that order. Stage 1 can enumerate `roster`
from one and classify position one as cold and later positions as warm.
Both pins' per-leg records lack explicit position and class fields. Pin A
also lacks a top-level `span_id`. Pin B writes `span_id` when supplied.
See [A `scripts/cadence_legs_runner.py:318–323`](https://github.com/mpmdw/JouleWise/blob/2d347f721552fe03bdd19f113e7bad7a7c24908e/scripts/cadence_legs_runner.py#L318-L323),
[A `scripts/cadence_legs_runner.py:395–398`](https://github.com/mpmdw/JouleWise/blob/2d347f721552fe03bdd19f113e7bad7a7c24908e/scripts/cadence_legs_runner.py#L395-L398),
[B `scripts/cadence_legs_runner.py:448–455`](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L448-L455), and
[B `scripts/cadence_legs_runner.py:527–530`](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L527-L530).

## Draft RUN_STATE item for the lead

**Stability filler spans under RL-200 and RL-200a, starting with the next eligible launch**

- At the first stability rung of each local date, take the cold leg of the
  lowest-numbered base kit (01–14) with an unrun position. Its span may
  have two further legs, which are warm and count as rank 4. Preserve the
  existing higher rungs. A ready, admitted finite registered product,
  including ctl-01 or W1 native smoke, ranks above rank-4 stability.
- In the eligible kit, start at the next unrun position in kit order.
  Try three consecutive unrun legs, then two, then one. Use the longest
  whose actual-t0 plan and close pass the dated-block check and all other
  start checks. Limit stability to one leg while a READY record or a
  pre-notice is in hand. A leg that started is spent. A leg whose span
  refused before it started stays unrun, and a span may not include a
  spent position or skip an intervening position.
- Use `fillers-w2/` for kits 01–16 through the queue expiry
  `2026-12-08T12:35:29-08:00`. For successor kits 17–53, use
  `fillers-w3/` from local 2026-11-26 through
  `2026-12-15T12:35:29-08:00`, after the applicable predecessor is
  exhausted. Pin A serves 01–14 and 17–48. Pin B serves 15–16 and 49–53.
  Keep item 464's pin-B fallback for 15–16 and the successor admission gates.
  For two or three legs use
  `queues-Nleg/<kit>-<lowercase-leg-id>-<lowercase-leg-id>[-<lowercase-leg-id>].json`,
  with all the selected legs in order and `N` replaced by 2 or 3.
  For one leg use W2 `queues-1leg/<kit>.json` at the selected `seq`,
  or W3 `queues-1leg/<kit>-<lowercase-leg-id>.json`. Match each queue
  digest to the week's README and check kit digest, pin, dates, and roster.
  Use PR #858 and item 447's validation and issue procedure for the
  selected single-span queue.
- On pin A try ARG `02:00-02:35` and then `13:14-13:15` under item 463
  for each candidate length. With the alternate ARG, every pin-A multi-leg
  candidate must clear the physical batch for leg starts. If its actual
  `[t0, fence_end)` overlaps 02:00–02:35, cede to the next shorter
  candidate. On pin B omit ARG. On both pins the soak must also clear the
  band under item 507. Replan at actual t0. If the issued roster or ARG
  no longer fits, cede the attempt and issue the newly selected one with
  its own typed fields before launch.
- Name the legs and add the line “RL-200 §2: leg 1 cold, legs 2 to N warm;
  `lm-stab-01` reads cold base legs only.” Report each leg's disposition
  on its own line in Check. Stage 1 takes the index from the receipt's
  ordered `roster`, even if an earlier leg failed to qualify. Require the
  `legs` rows to be a same-order prefix of `roster`. A leg with no row
  stays unrun.

### Typed fields in each actual dispatch item

Post the ordinary v1 header through `run_state_add.py` as ISSUED at actual
issue time. Put one JSON record in the item body with the following typed
fields for RL-200a rows 1–6. The body is how the posting tool can carry this
record because the v1 header has a closed field set. The example values
below illustrate field content and are for a synthetic dispatch.

```json
{
  "schema": "joulewise.cadence_span_dispatch.v1",
  "attempt_id": "cq-f2-stab-17-l004-l005-l006-a1",
  "campaign_id": "f2-stab-17",
  "kit_sha256": "8e7c099646b61571ac6430d5243607bc5a2c5056dc5218c184e21e43973b752f",
  "frozen_pin": "2d347f721552fe03bdd19f113e7bad7a7c24908e",
  "roster": ["L004", "L005", "L006"],
  "kit_positions": [4, 5, 6],
  "issued_epoch_s": 1795737540,
  "arg": "02:00-02:35",
  "batch_windows": ["02:00-02:35"]
}
```

The attempt ID equals the create-once receipt directory basename. Use full
kit SHA-256 and full frozen commit. The ordered roster and its one-based
positions must match the selected queue and the kit. On pin B use JSON
`null` for `arg` and `[]` for `batch_windows`. Where the pin B launch
supplies `--span-id`, it must equal the attempt ID. Stage 1 takes the ID
from `receipt.span_id` when present, and otherwise from the issued
`attempt_id` under the full match. The `issued_epoch_s` must equal the
typed header and bound receipt `started` at or after issue and at or
before Check. The record's `batch_windows` must equal the receipt and
be legal under the selected pin's ARG. Bind the actual attempt in the
issue pointer and wait for its terminal result or refusal at the
recorded deadline. A pre-chain refusal goes through the existing
refusal branch. Keep unstarted positions eligible for future selection.

### Check item addition for row 7

Item 491 requires full offload-manifest and encrypted-copy digests. Add
the full 64-hex SHA-256 of the exact `runner_receipt.json` independently
to the Check item under the field name `receipt_sha256`, alongside the
existing digests. Name the same attempt ID and post at the actual Check
time. Stage 1 requires one ISSUED item and one matching receipt per
attempt and unique started leg rows within the kit. Any absent required field,
ambiguous match, failed match row, or roster-prefix mismatch produces a
typed refusal naming the span and failed row. Its legs stay pending.
[RUN_STATE 491](../../RUN_STATE.md#L1568) ·
[RL-200a](../research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md)

## Verification

PR #858 and RUN_STATE 447 supply the two-leg instrument precedent. The
preflight and final alternate-ARG checks use synthetic clocks and pinned
planner functions. The mock receipts use synthetic runner dependencies.
Local checks are targeted to the generator, queue artifacts, and dispatch
evidence because the runtime and pins are frozen.

| Finding | Regression | Result |
| --- | --- | --- |
| Pin clock parity with allowed arguments and the soak band, before the lead's tightening | 1,440 minute samples per length on `04` and `15`, plus 16 exact times × 3 lengths × 4 kits (`04`, `15`, `17`, `49`) | PASS |
| A dated block may shorten an admitted span | Both pins admit the one-leg fence plus close and cede longer lengths in the synthetic case | PASS |
| Receipt position by roster order | Two- and three-leg synthetic runs at each pin, four receipts total | PASS |
| Generated queues and digests | Six focused generator tests and byte-for-byte `--stability-spans --check` | PASS |
| Pinned queue shape and work bounds | All 1,113 generated queues loaded with their pinned validator and planned at a synthetic t0 (966 pin A, 147 pin B) | PASS |
| Tightened pin-A alternative | Pinned fence on each new cutoff, the next second, and at reopening | PASS |
| Typed issue body | Canonical posting in a synthetic state and comparison with the sample W3 queue, frozen kit, and kit positions | PASS |
