# Charge — cold gate A281A-RECUT-01: whether and how lane A281a proceeds after its class-iv stop (rule 11 mandatory triggers: a third fix round on the same defect class; the lane's own stop rule fired)

Assembled 2026-09-23 ~22:00 PDT by the resident magistrate (Opus 5.5, activation d8cc9c0a). Nothing is armed. The lead's dispositions below are ARGUMENT. Verify load-bearing claims against the code at `c0998fdb` (`git show c0998fdb:joulewise/scored_packer.py` and so on, or a `git archive c0998fdb` copy under /tmp).

## Terms in plain words

Lane A281a builds three pure Python modules for the headline experiment (energy per correct answer, 8B vs 1.7B model, five MATH difficulty levels). `scored_registration.py` is a frozen object holding every pre-registered parameter. `scored_packer.py` schedules fixed problem *blocks* into fixed-length power captures (*envelopes*) and re-queues blocks that overran their time budget (whole block, then single-problem pieces, then a terminal `ceiling_violation`). `scored_reduce.py` turns per-item rows and per-block energy windows into per-cell accuracy and joules. *Class iv* is the recurring defect class: a registered input or ruled guard that is missing, defaulted, overridden by a caller argument, ignored, or skipped on some code path. *M8* is the ruled spread rule: a cell (model, arm, level) spans at least 5 blocks in at least 5 distinct envelopes, and no two of its blocks share an envelope. *M12* (as amended in exhibit 08 and affirmed in exhibit 21-10) re-queues a twice-overrun block as single-problem blocks packed several per envelope by derived worst case.

## History

The previous cold gate (exhibit 21-10, with its paired refuter 21-11) affirmed a structural cure: one no-default Registration object. Fix round 2 (exhibits 26, 27) implemented it at `c0998fdb`: 13 tests pass and 350/350 operand-collapse mutants die. The delta re-audit (exhibits 34 Sol, 39 Opus) found four NEW class-iv instances: `item_set_sha256` is never compared; the M12 worst-case guard checks a caller number, not the roster's own prediction; the retry tail path skips M8's one-block-per-cell guard; and the spread minima accept 1. The lane stop rule fired (exhibit 37). Two blind consults followed (exhibits 40 Sol, 44 Opus). Opus 44's perturbation probe found two more carried-but-ignored fields (`ceiling_s`, `scorer_id`).

## Lead disposition (argument)

- **D1 Diagnosis:** both consults agree that the round-2 cure was input-side. It proves a value ARRIVES, never that it CONSTRAINS. Guards are spread across entry points, and the roster carries copies of registered values.
- **D2 Re-cut, do not patch:** both consults agree. The next implementation is **A281a′** (registration + packer + every retry transition), then **A281c** (reducer) against the sealed roster. The estimator stays A281b (behind exhibit 21-10's table entering the AP-5M text).
- **D3 A281a′ acceptance (Opus 44's four parts, with Sol 40's matrix):**
  - (1) One `_seal(registration, roster)` checks every ruled invariant on the EXECUTED roster before every public return of pack and requeue. An AST test proves every public return goes through it.
  - (2) Derive, never copy: no roster copies of registered values; no derivable registered fields.
  - (3) A machine-readable binding matrix as data in the test module. Each field row carries a witness, a second value (jointly re-derived for linked fields), and the expected effect (output changes or refusal), run for each path. Its rows are derived from the RULING TEXT, not the code, to avoid circular acceptance (Sol 40). Any no-effect field sits in a closed CARRIED list, ruled here, naming its consumer lane.
  - (4) A seeded stress run against an independent checker written from the ruling text.
  - Gate criterion (Opus 44): *"the perturbation sweep lists every registration field as either consumed with an executed witness or CARRIED with a named consumer lane, and the seal is on every exit."*
- **D4 Constants versus fields:** levels, merge_order, min_correct 3, holm_m 5, both spread minima 5, cap_bound_fraction 0.20, and retry_stages become module constants pinned by schema version, with a test asserting equality to the AP-5M text. Register `item_ids_by_level` and derive `item_set_sha256` and `n_per_level`. Derive `max_drift_lever_slots` from `budget_j / (delta_upper × blocks_per_cell)`. `ceiling_s`: delete it from A281a′, and let the runner lane decide whether it is a kill timeout (CARRIED). `failed_prediction_s` at the whole-block and split stages becomes OBSERVED `elapsed_s`, compared with the roster's own prediction. `predicted_decode_s` is bound: pack refuses values above the derived worst case and writes `predictions_sha256`, which in registered mode must match the sizing receipt. Item rows carry `scorer_id` and both digests; the reducer refuses a mismatch (A281c).
- **D5 M8 vs M12 on retry tails, the consults' split:**
  - Sol 40: M8 wins even within a parent, so sibling singles go to distinct envelopes.
  - Opus 44: M8 protects replicate independence; the PARENT block is the replicate (exhibit 08 F2(a) pairs on the parent), and the parent originally sat in one envelope. So sibling singles of one parent MAY share an envelope, and blocks of DIFFERENT parents of a cell never may.
  - Both: the five-block minimum counts parent blocks, so a split cannot manufacture replication.
  - **Lead: Opus.** Sibling separation buys no independence the original block did not have, and costs envelopes.
- **D6 Executed-roster rules:** M8b is evaluated on the executed roster with the parent as the unit. A parent lost to a terminal `ceiling_violation` after capture sets `spread_exceeded` for that cell, marking the claim unresolved rather than refusing. The drift lever uses the parent as the unit: each parent's position is the item-weighted mean envelope index of its executed windows (exhibit 39 S3: 5.47 per-block vs 2.8 item-weighted). Innocent requeues, where no item exceeded its worst case, are refused.

## Questions

- **Q1** AFFIRM / REJECT / AMEND D1–D2: re-cut into A281a′ then A281c. Or rule a different shape, including stopping the lane until something else lands.
- **Q2** Rule D3's acceptance shape and gate criterion. Give the closed CARRIED list: field → consumer lane.
- **Q3** Rule D4, field by field where it matters.
- **Q4** Rule D5 (siblings may share, or not) and D6. Give exact AP-5M sentences for M8 on retry tails, `spread_exceeded`, and the parent-unit drift lever.
- **Q5** Anything both consults missed that a fresh reviewer would find in the re-cut.

Tier findings BLOCKER / MATERIAL / NIT. Give exact text wherever a cure is ruled.

## Constraints on the judge

Read-only; nothing armed. Never run `sudo`, `launchctl`, `powermetrics` or `systemsetup`. Never touch `/Users/edr/code/JouleWise` (canonical root), `/Users/edr/night-custody`, any `/Users/edr/JouleWise-measurement-*`, or `~/Library/LaunchAgents`. Probes: `git show c0998fdb:<path>`; a `git archive c0998fdb` copy under /tmp; `python3 -B -m unittest tests.test_scored_registration tests.test_scored_packer tests.test_scored_reduce` inside that copy. Never run the discovery suite. Read only this packet directory and the code at c0998fdb. Ruling file: `10-coldgate-fable-ruling.md` in this directory. Under 14 KB.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
715952a0e7a0c51be1cff131b4868b2e6873a4aaf17a1a673a99e7469bbf5b6b  ex-08-a281-round1-synthesis-and-rulings.md
b8a66c41a1ede0e8df065956c176b2c86f2260110daf449853b3a13269050e2d  ex-21-10-coldgate-fable-ruling.md
02c55d4e5c135e90172deff0ca3307b0fa06dfa1267358716f0943b8ce88d2e0  ex-21-11-opus-contract-refuter.md
eb545ff1d46f55c71631c1a59976e6aea1ac162ded2d2b555150b25981d83f2c  ex-26-a281a-fix2-seat-brief.md
d1f594972f872e5b340924eb67e8ada9625fe7fbd0bb8062aa85fbe8156acd84  ex-27-a281a-fix2-seat-report.md
7b60f471dd0aed027afea504ac7d648b1e3cf94e6e22abc414e88f2656516d5d  ex-34-a281a-sol-delta.md
990fefbcce9df68de7fb6cd04937bbb6b1b909d7f1c6ec125885c46aa90042ba  ex-37-a281a-stop-and-consult-brief.md
ee9dcfb791471b8822fc004f99e2006bc6a8eb676dff16cd940e4e9ec5075b38  ex-39-a281a-opus-delta.md
56646e94c06416f02bcf07aba3a76a0ff0e06fdc953d13084da258e27de5e64d  ex-40-a281a-sol-consult2.md
e537969b733e7370e8bcb914d166a8e60f199ff1219bfc7eb42383f73254e211  ex-44-a281a-opus-consult2.md
```
