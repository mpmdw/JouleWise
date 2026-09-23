# Exhibit F — authorities, verbatim, with file:line

Every extract below is the text at the merged head `4f8bc36d` (main, PR #382).
The judge reproduces any of them with
`git show 4f8bc36d:<path> | sed -n '<a>,<b>p'`.
Nothing here is paraphrased; the assembler's notes are marked *Assembler note*
and are separated from the quoted text.

---

## F1 — the ruled precondition itself: cold gate #3 ruling 10, §Q7

`docs/process_traces/2026-09-22-activation-59857fe5/08-coldgate-packet-a267-merge-transaction/10-coldgate-fable-ruling.md:90-92`

```
### Q7 — REJECT the lead's disposition. Extra precondition named.

B4 :35 is exact: before the re-run night is *prepared*, a daytime bench replay ("real `execute` and real collector with an injected recorder replaying an archived plist, no sudo, no measurement, never labeled R6 evidence") must show chain-level `start_drift_s` ≤ 0.5 s on **every** slot. No code path at `489b0953` implements such a replay under a "dry check" name, and no artifact in this packet records one. "The tracked entry point's dry check" is not shown to be that replay. Ruled precondition: **(P7.1)** the bench replay is executed after merge, at the merged head, and recorded as a tracked artifact `docs/process_traces/2026-09-22-activation-59857fe5/<nn>-bench-replay-start-drift.md` carrying the merged sha, the archived plist's sha256, the twelve `start_drift_s` values from `evidence_envelopes.jsonl` (chain-level), the maximum, and the statement `max ≤ 0.5 s`; **(P7.2)** it is linked from the arm notice; **(P7.3)** B3b's ordering (both A267 Part 3 and A269 merged; v2 exclusion list complete on main) is evidenced by the merge sha. Only then NIGHT_HANDBACK. If the replay exceeds 0.5 s on any slot, no arm; the night refuses on the 2 s rule only *after* the 0.5 s bench bar is met — the two bars are sequential, not alternatives.
```

*Assembler note (Q1):* P7.1's own words for the figure are "the twelve
`start_drift_s` values from `evidence_envelopes.jsonl` (chain-level)" and the
statement it requires is `max ≤ 0.5 s`. The words "anchor", "interior",
"cleanup" and "exit" do not appear in §Q7.

---

## F2 — the clause §Q7 enforces: A269 cold gate ruling 10, §Q3 replacement R6 clause

`docs/process_traces/2026-09-22-activation-e4b4ead6/03-coldgate-packet-a269-start-drift/10-coldgate-fable-ruling.md:35`

```
Replacement R6 final clause (exact text, replaces "live-installer dry check … or names a new cause."): "the pilot night re-run is prepared only after lane A269 has landed cure Q1(c) (`slot_pitch_s: 620`) under registration v2 and a daytime bench replay — real `execute` and real collector with an injected recorder replaying an archived plist, no sudo, no measurement, never labeled R6 evidence — shows chain-level `start_drift_s` ≤ 0.5 s on every slot; the re-run night is itself the live check: the chain refuses the night at the first envelope whose chain-level start drift exceeds `start_drift_abort_s` (2 s), before that envelope's capture; a night that completes with every envelope's session-level `start_drift_s` ≤ 2 s satisfies this precondition and counts; the re-run then yields at least eight bounded envelopes with none excluded for `start_drift`, or names a new cause." Options (a), (b), (d) REJECTED as strictly costlier with no rigor gain: (c) keeps rules-before-data (threshold pinned in v2 before t0).
```

*Assembler note (Q1):* within this one clause the bench bar reads "chain-level
`start_drift_s` ≤ 0.5 s on every slot"; the in-chain abort reads "chain-level
start drift exceeds `start_drift_abort_s` (2 s)"; and the night's own
completion test reads "every envelope's **session-level** `start_drift_s` ≤ 2 s".
Three bars, two levels, in the same sentence.

---

## F3 — A269 cold gate ruling 10, §Q1 amendment A1 (the session-level bar)

`docs/process_traces/2026-09-22-activation-e4b4ead6/03-coldgate-packet-a269-start-drift/10-coldgate-fable-ruling.md:17`

```
Amendments (MATERIAL): (A1) the 2 s bar of R6 is assessed on the **session-level** `start_drift_s` (the larger figure, line 361 takes the max), i.e. envelope 01's 0.318 s is the reference, not 0.160. (A2) `execute` gains an up-front total-window check before the first spawn: `settle_s + (envelopes−1) × slot_pitch_s + envelope_s ≤ window_max_s` (8020 ≤ 9000, C1); the per-slot check at line 480 stays as written (it correctly uses `envelope_s`, the capture length — D1's remark that line 481 "must learn pitch" is a NIT, not a defect). `validate_protocol` must reject `slot_pitch_s < envelope_s` and any CLI override, fail-closed.
```

*Assembler note (Q1):* A1 names "the 2 s bar of R6", and is the amendment that
moved THAT bar to the session-level figure. It does not mention 0.5 s.

---

## F4 — the lane brief's artifact deliverable: brief 10, D8

`docs/process_traces/2026-09-22-activation-59857fe5/10-bench-replay-start-drift-brief.md:20`

```
D8. **Artifact** `docs/process_traces/<activation>/<nn>-bench-replay-start-drift.md` + raw `bench-replay.json`: merged sha (+ `git merge-base --is-ancestor <transaction merge>`), clean tree, bench script sha256 and argv, registration sha, per slot: `scheduled_mono_s`, `actual_mono_s`, chain `start_drift_s`, session `start_drift_s`, `collector_exit`, `cleanup_proven`, cleanup wall, attestation state and `network_time_attestation_wall_s`, anchor status, tail; `max(chain) ≤ 0.5 s` stated; `max(session)` stated (a chain-pass/session-fail split is ESCALATED, never passed); `recorder_kind: replay`; `summary.status`; machine state (`uptime`, `pgrep -c claude`) at start and end. Extra daytime load lengthens the tail: a pass under load is a fortiori; a fail under load is retried census-clean.
```

*Assembler note:* D8 is the magistrate's brief, not a ruling. It is the origin
of "a chain-pass/session-fail split is ESCALATED, never passed" — the sentence
X1 implements.

---

## F5 — X1 and X2, the two added driver requirements

**Correction to the charge (assembler):** the charge locates X1/X2 in "brief 10
… its X1/X2 addendum lines". They are not in brief 10. Brief 10's only dated
addendum (`:34-43`, 12:20 PDT) carries items C1–C6 from the A267 round-2 delta
lenses. X1 and X2 are items of the BENCH-REPLAY FIX-ROUND-1 brief, record 16:

`docs/process_traces/2026-09-22-activation-59857fe5/16-bench-replay-fix-round-1-brief.md:34-35`

```
X1 (17b B1, BLOCKER). `verdict()` gains a third status `ESCALATE` (neither PASS nor FAIL) whenever chain passes and the session-level figure fails the same bar; `markdown()`'s headline prints it; `main()` returns non-zero (use 3) for ESCALATE and 1 for FAIL. Regression: a journal with chain max 0.4 s and session max 0.7 s → status ESCALATE, rc 3, headline `**ESCALATE**` (counterfactual at 3e299b85: PASS, rc 0 — the lens's live smoke hit it).
X2 (17b B2, BLOCKER). `verdict()` admits a slot only if `collector_exit == 0`, `cleanup_proven` is True, `anchor_status == "bounded"` and `interior_complete_support` is True; any other slot makes the verdict FAIL with the offending slot and field named (the tail the bench times — parse, anchor derive, integration, interior reduction — must actually have run). The SMOKE (60 s envelopes) is exempt from the anchor/interior requirement ONLY under `--smoke`, and its markdown must say the anchor cannot resolve at that envelope length. Regression: rows with one `collector_exit 1`, one `cleanup_proven False`, one `anchor_status unknown` → FAIL naming each (counterfactual at 3e299b85: PASS).
```

*Assembler note (Q2, Q3):* X2 is the whole of the anchor/interior admissibility
requirement, and it was written by the magistrate in a fix-round brief. No cold
ruling contains it. X1 is the ESCALATE status. Both are downstream of the
execution lens below, not of §Q7.

---

## F6 — the execution lens that prompted X1/X2: record 17b, B1, B2, and S3

`docs/process_traces/2026-09-22-activation-59857fe5/17b-bench-replay-execution-lens-opus.md:7` (B1)

```
**B1 — a chain-pass / session-fail split exits 0 and prints `PASS`.** `scripts/bench_replay_start_drift.py:311-312` sets `status = "PASS"` and then records `escalate` as a *separate boolean*; `:343` renders the headline `**PASS**`; `:510` returns `0` whenever `status == "PASS"`. Brief D8 is explicit: "a chain-pass/session-fail split is ESCALATED, never passed."
```

`…/17b-bench-replay-execution-lens-opus.md:12` (B2)

```
**B2 — `verdict()` admits slots whose finalisation tail never happened.** `verdict()` (`:302-322`) reads only `chain_start_drift_s` / `session_start_drift_s`. It never consults `collector_exit`, `cleanup_proven`, `anchor_status` or `interior_complete_support`, all of which `slot_rows()` already collects. Executed probe (`bench.verdict` on rows with `collector_exit=1` on slot 5, `cleanup_proven=False` on slot 6, `anchor_status="unknown"` and `interior_complete_support=False` on all twelve) → `status = PASS`, `escalate = False`.
```

`…/17b-bench-replay-execution-lens-opus.md:21` (S3 — bears on the attestation criterion in Q2 option (a))

```
**S3 — network time is never actually off, so the bench attests a different log.** The stub toggles nothing, so `timed` keeps applying corrections; my slot 2 came back `slew_attested` — a real, live slew, not reproducible in a night. The artifact quotes these attestation walls as the first measurement of the A267 B1 residual; it must say they are live-log-with-slews costs and that `slew_attested` slots in the full run are expected, not a defect.
```

*Assembler note (Q2):* B2's stated rationale is "the tail the bench times —
parse, anchor derive, integration, interior reduction — must actually have
run", i.e. the anchor field is a PROXY for the tail having executed, not a
quantity the ruled bar names. Q2 turns on whether that proxy is the only way to
establish what it stands for.

---

## F7 — the risk the lane recorded BEFORE the run: record 19b, RISK paragraph

`docs/process_traces/2026-09-22-activation-59857fe5/19b-bench-replay-fix-round-1-delta-execution-lens-opus.md:109-113`

```
**RISK, not a defect — X2's bar is unproven satisfiable.** Nothing executed shows a 600 s
replay slot reaching `anchor_status == "bounded"` and `interior_complete_support == True`;
the only live run (60 s smoke) had both false and is exempt. If the anchor cannot resolve
on the full run, the bench FAILs by construction. `slot_rows:266-287` does emit all five
admission fields, so no spurious `None` defect.
```

*Assembler note (Q2, Q3):* "If the anchor cannot resolve on the full run, the
bench FAILs by construction" was written and accepted before either attempt ran.
It is the reviewer's own warning that X2's bar might be unsatisfiable in replay.

---

## F8 — the skipped tail, measured on the archived night (the 0–2.3 s figure)

The A269 packet's exhibit C2 is the per-envelope serial tail from the archive's
own stamps. The column `end-postparse` is the anchor-derive + integration +
interior-reduction tail — exactly the work an unresolved-anchor slot skips.

`docs/process_traces/2026-09-22-activation-e4b4ead6/03-coldgate-packet-a269-start-drift/exhibit-C-executed-evidence.md:25-41`

```
## C2 — per-envelope serial tail from the archive stamps (monotonic seconds)
```
evidence_envelopes.jsonl sha256 9c5a9c12d23d42bfe3181e9ba57f2d156041cce14f9c9b20f8abfd858120df3e
env chain_drift sess_drift stop-sched postparse-stop end-postparse nextpre-end groups  anchor_status  excluded(summary)
summary.json sha256 9121f080c97e4b2f8f01261d0a2f9f407840dea9a6c8ca4468406617403d6f04
  1       0.160      0.318    600.150          4.983         0.011       2.869    113  unknown       ['clock_anchor_unresolved', 'incomplete_interior_support']
  2       7.892      8.014    600.150          4.936         2.122        3.02    113  bounded       []
  3      10.112     10.228    600.082          4.881         0.074       2.777    113  unknown       ['clock_anchor_unresolved', 'incomplete_interior_support', 'start_drift']
  4       7.698      7.814    600.150          4.847         0.106        2.79    113  unknown       ['clock_anchor_unresolved', 'incomplete_interior_support']
  5       7.777      7.893    600.142          4.971          2.13       2.934    113  bounded       ['incomplete_interior_support']
  6      10.061     10.177    600.150          4.893         1.552       2.939    113  bounded       ['incomplete_interior_support', 'start_drift']
  7       9.419      9.534    600.150          4.913         0.011       2.673    113  unknown       ['clock_anchor_unresolved', 'incomplete_interior_support']
  8       7.632      7.747    600.150          5.010         2.291       2.612    113  unknown       ['clock_anchor_unresolved', 'incomplete_interior_support']
  9       9.946     10.063    600.150          5.072         1.338       2.676    113  unknown       ['clock_anchor_unresolved', 'incomplete_interior_support', 'start_drift']
 10       9.120      9.236    600.150          4.896         0.011       2.789    113  unknown       ['clock_anchor_unresolved', 'incomplete_interior_support']
 11       7.730      7.846    600.150          4.904         1.697       2.853    113  bounded       ['incomplete_interior_support']
 12       9.488      9.603    600.150          5.018         1.702                113  bounded       []
```

The A269 ruling reads the same column and states its range in its own words —
`docs/process_traces/2026-09-22-activation-e4b4ead6/03-coldgate-packet-a269-start-drift/10-coldgate-fable-ruling.md:15`
(last sentence):

```
Deciding evidence: the only ≤ 2 s figure in the record that is *measured* rather than budgeted is envelope 01 (P1: 0.160 s chain, 0.318 s session), the one slot with no predecessor (P2 line 490 shows why every other slot inherits the tail). Cure 2 makes every slot an envelope-01 by construction; worst observed tail 10.23 s + worst attestation 1.45 s = 11.7 s < 20 s gap. Options (a) and (b) rest on budgets: (a) 2.5–4.8 s serial per both seats (fails); (b) 0.6–0.9 s session-level is D2's arithmetic, unmeasured, and it places the 113-group census and `log show` (real work in `logd`, outside `observer_cpu_s` = SELF + reaped CHILDREN) inside slot i+1's capture — unattributed observer energy in a recorded window, even if outside the interior. (d) declined: it leaves the harness overrunning its own schedule and blinds the only tail-regression detector. Serial budget I accept as evidence: C2 stamps (postparse−stop 4.85–5.07, derive 0.01–2.29, nextpre−end 2.61–3.02), C5, C6.
```

*Assembler verification (Q2), executed this session:* the twelve `end-postparse`
values in C2 are 0.011, 2.122, 0.074, 0.106, 2.130, 1.552, 0.011, 2.291, 1.338,
0.011, 1.697, 1.702 s. **min 0.011 s, max 2.291 s** — the charge's "0–2.3 s" is
correct, and the ruling's own "derive 0.01–2.29" at `:15` agrees. Reproduce:
`git show 4f8bc36d:…/exhibit-C-executed-evidence.md | sed -n '30,41p' | awk '{print $6}' | sort -n`.

**Correction to the charge (assembler):** the charge glosses the figure as
"0–2.3 s anchor derive/integrate, **only when the fit completes**". The
qualifier is not supported by C2: envelope 08 (`anchor_status unknown`) spent
2.291 s — the LARGEST tail in the table — and envelope 09 (`unknown`) spent
1.338 s, while envelope 12 (`bounded`) spent 1.702 s. The tail is therefore
not confined to fit-completing slots; the 0–2.3 s bound itself stands
regardless, and it bounds the tail across BOTH statuses, which is if anything
the stronger reading for the charge's purpose.

---

## F9 — the archived night's anchor statuses: two different projections

The charge's §Facts cites the v3.1 forward projection. That is a different
column from C2's `anchor_status`, which is the night's own recorded status. The
judge should not read the two as contradicting each other.

`docs/process_traces/2026-09-22-activation-e4b4ead6/01-launch-and-resume-record.md:29` (step 10):

```
10. 07:45 — v3.1 forward projection over the twelve fixtures at `447fd6bf` (executed): bounded {02, 05, 06, 08, 09, 11, 12} = 7; 01/03/04/10 `affine_clock_fit_empty` (slew inside the capture); 07 backstop. Consequence: my addendum 16's "9 retained / 3 pairs" over-cured; ruling 14 R6's "(5 retained / 1 pair)" was correct on the night's data. Correction 16b issued (commit 56391dd0); p1 stands on both projections.
```

*Assembler note:* the v3.1 projection at `447fd6bf` gives bounded
{02, 05, 06, 08, 09, 11, 12}; C2's recorded column gives bounded
{02, 05, 06, 11, 12} with 08 and 09 `unknown`. The difference is v3.1's
method selector, not a disagreement about the data. Step 9 of the same record
(`:28`, item (e)) is also on point for the charge's backstop hypothesis:

```
9. 07:35 — A267 seat head `447fd6bf` (Parts 1–4 committed, tree clean). Magistrate verification in the detached review worktree `JouleWise-wt-a267-review`: three brief modules **158 tests OK** (from 126). Production diff read in full (chain +289, sampler +175, deriver +9). Findings: (a) form deviation — `timed_log_matches` counts applied-correction EVENTS (receipt lines plus ungrouped syscall lines within a 1 s grouping window) so exhibit D yields the ruled 10, and records the raw 30 marker lines as `matched_marker_lines`; any nonzero count still excludes, so admission is unaffected (accepted, recorded); (b) NIT — `reduce_interior` maps the interior to ns once but `integrate` re-derives ns from the float seconds it is handed; bench probe of 200,000 epoch-scale values and the twelve archive interior starts: zero round-trip mismatches, so exact today, but the integer path should accept ns directly (deferred to the A269 seat's Part C scope or a later NIT); (c) `execute` returns 3 on a failed restore even when the outcome was refused (rc 2 masked; both facts are in `evidence_outcome.json`; accepted); (d) attestation window is still R4's ±1 s (the A269 Q4(i) union amendment is in brief 04); (e) under ruling 14 R1's check order envelope 07 trips the 15 ms backstop (`wall_minus_monotonic_span_exceeded`, 22.36 ms) before the rate check — brief 03 regression 3's expected detail is therefore superseded by the ruling's order; the seat's report must show which it asserted.
```

*Assembler note (Q2):* this is the only executed evidence in the record that
`wall_minus_monotonic_span_exceeded` — the 15 ms backstop — fires at all, and
it fired on envelope 07 of the archived night at 22.36 ms, under the ruling's
check order, BEFORE the rate check. So the backstop is a real mechanism of the
archived data, reached on a real night with no feeder in the picture.

**F9 is the authority for Q2 option (a).** The bounded set at `:29` —
{02, 05, 06, 08, 09, 11, 12}, with 01/03/04/10 `affine_clock_fit_empty` and 07
the backstop — is the fixed per-envelope CLASS mapping option (a) asks the
replay to match, and it is the constant compiled into
`exhibit-E-generator.py` (`ARCHIVED_V31_CLASS`). Note what it means: the
archived night ITSELF left five of twelve envelopes' anchors unresolved,
because five of its captures contain real slews or trip the backstop. The
driver's X2, which demands `bounded` on all twelve, therefore asks a faithful
replay of THIS archive to produce an anchor outcome the archive never had.

*Assembler note on the superseded hypothesis:* the charge's first draft carried
a magistrate hypothesis that feeder pacing jitter makes `bounded` unreachable
in replay on every slot. Attempt 2's slot 2 refutes it (executed, 18:06 PDT:
`bounded`, `interior_complete_support` true, under the same 0.084/0.242/0.356 s
jitter as slot 1). The refutation is stated in the charge's §Facts and is the
reason Q2's options are a fidelity test rather than a limitation waiver. The
same refutation is visible in exhibit E's own fidelity column: attempt 1
MISMATCHED on slot 2 (archived `bounded`, replayed unresolved — the causality
defect), attempt 2 MATCHES it.

*Assembler note on envelope 08 (Q2's deciding case):* 08 is the only slot in
attempt 2's first eight where the replay and the archived class disagree. Read
F8 and F9 together to see why it is the marginal one and not a surprise. In
C2's recorded column (F8, line 37) 08 is `anchor_status unknown` — the night's
OWN v3.0 derivation did not resolve it — and it carries the largest
`end-postparse` tail in the table, 2.291 s. It becomes `bounded` only in the
v3.1 projection at F9, under rate-aware caps. So the class the replay is being
asked to reproduce for 08 is the product of a re-derivation, not of the night's
own recorded verdict, and the replay derives from archived labels paced against
live stamps. Q2(d) is the rule the lead offers for exactly this case; Q2(a)
would fail the run on it.
