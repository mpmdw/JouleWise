# Opus contract-lens refuter — cold gate #3 (A267 + A269 merge transaction)

Charter digest expected `099de884…c95d81` (convening prompt + packet pin);
observed by `shasum -a 256 docs/process/coldgate_charter.md`: identical. All
eight manifest digests recomputed, all MATCH. Permitted module run at
`489b0953` in `JouleWise-wt-a267-review2`:
`tests.test_quiet_predicate_campaign` → `Ran 98 tests in 9.254s OK`. I did not
open the paired cold ruling.

**Verdicts. Q1** shape licensed / r7-as-prepared REJECT (BLOCKER 1). **Q2**
licensed but amend. **Q3** AFFIRM (b), invariant corrected. **Q4** AFFIRM
outcome, reject the framing. **Q5** AFFIRM all seven, item 5 extended. **Q6**
AFFIRM on re-executed evidence. **Q7** REJECT (BLOCKER 2). Silence =
concurrence.

## Re-executed exhibit-C checks (four; three required)

1. **r6→r7 field diff**, own leaf walk at `e52c7fbc`: 428 leaves each, none
   added/removed, **3 changed** — `.acceptance_id`, `.derivation_sha256`,
   `…estimator_code_sha256.joulewise/uncertainty_evidence.py`
   (`257cda08…`→`b583f35a…`). **AGREE.**
2. **Four estimator digests at `489b0953`** all equal r7's pins; r7 file digest
   `14c891eb…` equals `ANCHOR_V3_R7_ACCEPTANCE_BOUND_SHA256`
   (`calibration_bracketing.py:141`). **AGREE with C1, C5.**
3. **Header guard**: all sixteen C3/C3b cells reproduce, incl.
   `now=True/prop=False` on the compact header alone. **AGREE.**
4. **The check the packet did not run** (Q6): `timed_log_matches` over both
   191-line bodies → **10 events each**, 0 unparsed moments.

## Q1 — transaction shape; r7's admissibility

**Shape (a): LICENSED.** D-138 (B1, `docs/decision_log.md:10372-10374`)
requires merging "ONLY inside the atomic Phase-2 successor re-freeze
transaction that re-issues the acceptance artifact and every dependent pin".
"Atomic" qualifies the *transaction*; the text says nothing of commit count,
and one merge commit leaves no state on main where the feature landed and r7
did not. (c) is forbidden by that sentence; clause (2) at `:10375-10378`
("Follow-on work … RIDES THE SAME BRANCH") affirmatively supports the rebase.

**By-hand r7: LICENSED; the stale reissue script is a non-issue.** Clause (3),
`:10378-10379`: "The re-issue and pin update remain **lead-owned** inside the
re-freeze." By-hand lead preparation IS the ruled shape; no cited authority
conditions issuance on a generator.

**BLOCKER 1 — r7 as prepared is NOT admissible: it misdescribes its own
delta.** r7's `derivation_notes.reissue_delta.changed_estimator_pins` is
byte-identical to r6's and states `uncertainty_evidence.py` → `{predecessor
67e34a1a…, reissued 257cda08…}` plus a `reduce.py` rotation. `257cda08…` is
**r6's** pin — r7's live pin is `b583f35a…` — and `reduce.py` did not rotate
in r7 at all. Sibling `science_neutrality_evidence` still describes "the full
19-member corpus … reproduced the r4 derivation record": r6's sentence, not
r7's proof. **Failure scenario:** an auditor authenticating a future pack reads r7's own
reissue record, expects `257cda08…`, finds `b583f35a…` on disk, and cannot
distinguish a pin-rotation error from a tampered artifact — defeating the
accidental-estimator-drift invariant (`:10368-10369`) inside the artifact
meant to carry it. **Cure:** rewrite `reissue_delta` for
`uncertainty_evidence.py` only, `257cda08…`→`b583f35a…`; replace
`science_neutrality_evidence` with r7's own; recompute `derivation_sha256`,
the file digest and the registry pin; re-run C1/C2/C5.

**MATERIAL 1 — the packet's evidence design cannot see BLOCKER 1.** Exhibit A's
diff answers "what changed", never "does the artifact describe itself
correctly", and the packet uses 3-of-428 affirmatively ("a pure pin delta") —
the number that *proves* the defect, since the 425 unchanged leaves include
the block that had to change. Add **(viii) every `derivation_notes` field
naming a pin, corpus or predecessor is checked against r7's own pin block and
against the evidence executed for r7.** **NIT 1:** item (vi) should require the
seven-module run clean at the rebased head, no flake allowance.

## Q2 — the header guard

**Option (a): LICENSED but OVER-FIT.** Ruling 14 R4 (B2 `:23`) fixes the argv
verbatim including `--style syslog`, so (c) would amend a sealed ruling for a
fixture's convenience; (b) is correctly rejected; nothing forbids (a).

**MATERIAL 2 — the constant pins column widths no authority fixes.** It carries
23 literal spaces; syslog column widths are an undocumented `logd` rendering
detail of Darwin 25.6.0, not a ruled interface. **Failure scenario:** an OS
update widens the PID column by one space; the guard returns `False` on all
twelve envelopes of a ~3 h night; all become `network_time_unattested`;
`minimum_retained` 8 is unmeetable; the loss surfaces only at harvest.
Fail-closed for *claims*, fail-open for *windows* — the trade the lead's own
Q3 reasoning calls the other way. **Better option (a′), not offered:**
`" ".join(first.split()) == "Timestamp (process)[PID]"` — rejects every C3b
counterfactual (compact collapses to `Timestamp Ty Process[PID:TID]`), accepts
both live captures, survives column drift. **Missing option (a″), stronger:**
run the real ruled argv once at dry-check time and refuse to arm unless the
guard accepts its output, turning a silent total loss at harvest into a pre-t0
refusal. The option set is asymmetric: three variants of one mechanism, none
of them detection-before-t0.

**MATERIAL 3 — the fix list under-enumerates, exactly as the packet notes for
Q3.** `tests/test_quiet_predicate_campaign.py:20` @ `489b0953` defines
`TIMED_LOG_HEADER = "Timestamp               Ty Process[PID:TID]\n"` with a
comment asserting it is what `--style syslog` prints — the compact header
duplicated test-side, used at `:1288` and in the `("header only", …,
"authenticated")` row at `:1295`, which **inverts to `asserted`** under (a).
R2.1–R2.5 name fixtures and regressions, not this constant. **Failure
scenario:** the round lands, the module goes red, and the cheapest exit is
relaxing the new guard. **NIT 2:** `quiet_predicate_campaign.py:443-445`
states the same false fact and must be rewritten under any option.

## Q3 — the attestation bound

**Option (b): LICENSED; it amends nothing sealed.** The 15 s formula is brief
06 item 1 (B6 `:16`) — magistrate dictation, which this gate outranks. Ruling
14 R4 fixes no timeout; its only timing constraint is "within ten minutes of
the envelope" (B2 `:23`), satisfied a fortiori, and A269 Q4(ii) (B4 `:40`)
already calls it "met by construction (gap ≤ 20 s)". On the merits 5 s is
licensed by a sealed ruling's own arithmetic: A269 ruling 10 Q1 (B3 `:15`)
accepts "worst attestation of 1.45 s", and
`quiet_predicate_campaign.py:572-576` records 0.70–1.45 s *over one envelope's
window* — 5 s is 3.4× the worst accepted figure.

**MATERIAL 4 — the lead's rationale is false in general, and R3.3 is written
over the three protocols that hide it.** With `cleanup_budget_s = max(1,
gap−5)` and (b) = `max(5, gap − cleanup_budget_s)`, the two sum to the gap
**only when gap ≥ 6**; at gap = 3, cleanup 1 + attestation 5 = 6 > 3.
`validate_protocol` must reject `slot_pitch_s < envelope_s` (A269 Q1 A2, B3
`:15`) but not a sub-floor gap, and R3.3 asserts the invariant only for v2
(20), SCALED (6) and pitch 700 (100) — all ≥ 6. **Failure scenario:** a
registration with a 4 s gap passes validation, both budgets over-claim it, and
the regression written to make over-claiming impossible is green. **Cure:**
state the invariant with its precondition, or reject
`gap < ATTESTATION_TIMEOUT_FLOOR_S + 1` in `validate_protocol` and assert R3.3
as a property over arbitrary valid protocols.

**MATERIAL 5 — hygiene: the seat's reconciliation is omitted from Q3's Facts.**
The packet frames 15 s as an unresolved self-contradiction, but exhibit A
`:593-597` carries the seat's reasoned defence: 15+15 exceeding 20 is
"deliberate and visible", because the next spawn trips `start_drift_abort_s`
and the night ends at a named abort. The Facts quote the comment the bound
contradicts and not the docstring that answers it. I still rule for (b) —
refusing a ~3 h night to save one envelope is the worse fail-closed outcome —
but the argument belonged in the Facts.

**Agreement:** the five-pin enumeration is right, the dictation's "two test
pins" wrong (`:1259`, `:1260` SCALED unchanged, `:1262`, `:1267`, `:1269`,
`:1274`).

## Q4 — the two window keys

**AFFIRM the outcome; REJECT the label.** A269 Q4(i) (B4 `:39`) rules
`window_epoch_s` to be the union window; brief 06 item 14 (B6 `:29`)
re-assigns it. A magistrate brief cannot amend a sealed cold ruling, so item
14 was **void to that extent** and the seat was never licensed to follow it.
"A seat deviation to ratify" sets the wrong precedent — that seats depart from
briefs by grace, rather than that briefs cannot override rulings. Record it as
a **correction of brief 06 item 14**, plus the rule the episode earns: where a
brief and a sealed ruling conflict the ruling governs; the seat follows it or
returns NEEDS_RULING.

**MATERIAL 6 — exhibit D2 §N4 is factually wrong and the packet reproduces it
unflagged.** Verified at `489b0953`: `window_epoch_s` still carries
`attestation_window(stamps)` (`:641`); `window_argv_epoch_s` is a **new** key
(`:642`). Nothing was renamed. The packet flags five divergences and not this
one, while quoting D2's characterisation in Q4's Facts.

**AFFIRM the null-initialisation.** The skeleton at `:618-622` has
`window_epoch_s: None` and no `window_argv_epoch_s`, so the `blocked` and
`capture window unavailable` returns omit the key.

## Q5 — the seven items

All verified at `489b0953`, **AFFIRMED as dictated**: item 1
(`record_attestation:691-692` returns `False` with `state` untouched — the cure
propagates, since `execute` reads `attestation["state"]` at `:1112` *after*
calling `record_attestation` at `:1109`); item 2 (`:700-713`, no `unlink`);
item 3 (`:1159`); item 4 (`:411-412`); item 6 (`:604` default); item 7.

**NIT 3 — item 5 is under-scoped.** `timed_log_moment` (`:481-489`) matches
only `\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+` and `strptime`s it naive-local,
**discarding the `-0700` offset `--style syslog` supplies** (compact has none;
the live capture has `02:28:08.335838-0700`). The daylight-saving ambiguity
item 5 documents exists at this second call site too, where the ruled style
hands the code the disambiguating information and the code drops it. NIT only
because the 1 s window is a *grouping* tolerance and any nonzero count
excludes the envelope. Extend item 5's sentence to `timed_log_moment`.

## Q6 — the already-sealed A267 gate

**AFFIRM — no sealed finding need be re-opened — but on evidence the packet did
not supply.** Ruling 14 R3 regression 12 is "the scanner over exhibit D returns
10 matches"; the scanner is `timed_log_matches`, not `timed_log_marker_lines`.
The packet's parity argument rests entirely on `timed_log_marker_lines` =
30/30 (C3) — a different function, whose agreement does not entail the
other's, because `timed_log_matches` calls `timed_log_moment`, which *parses*
each line and is the only style-sensitive step. I ran the ruled one: **10
events on the compact fixture and 10 on the live syslog capture, zero unparsed
moments on either.** Regression 12's bar holds in both styles. **MATERIAL 7:**
substituting a proxy for the ruled function in the only exhibit answering Q6
is an evidence defect; cure by adding the `timed_log_matches` row to C3.

**NIT 4 — a second style artefact, unmentioned.** `--style syslog` renders **no
level field**: `grep -c ' Df '` and `grep -c '<Debug>'` over the live capture
both return **0**, while the compact fixture shows ` Df `, so ruling 14 R4's
cited evidence ("the apply lines are `Df`") is unobservable under the ruled
argv. The **substance survives**, and I verified why: `--info --debug` govern
which entries are *retrieved*, not how they render; the live capture, taken
under the ruled argv, carries all ten `cmd,apply,src,` receipts, and both
flags are pinned at `tests/test_quiet_predicate_campaign.py:768`. The ruling's
illustration is style-bound; its holding is not.

## Q7 — may the next pilot night be armed

**REJECT. BLOCKER 2.** A269 Q3's replacement R6 clause (B4 `:35`) requires,
before the night is *prepared*: cure Q1(c) landed under v2; then "a daytime
bench replay — real `execute` and real collector with an injected recorder
replaying an archived plist, no sudo, no measurement, never labeled R6
evidence — shows chain-level `start_drift_s` ≤ 0.5 s on every slot"; only then
is the night itself the live check. A269 Q2 (B3b `:27`) adds that both A267
Part 3 and A269 must merge first.

The lead substitutes "the tracked entry point's dry check". Not the same:
`scripts/gen_evidence_night.py` renders and seals a wrapper and "Never install
or collect" (module docstring), with no occurrence of `dry`, `replay`, `drift`
or `check`. A grep for an injected-recorder replay
(`injected recorder|inject_recorder|--recorder|replay`) across `scripts/*.py`,
`joulewise/*.py` and `scripts/night_chains/` returns nothing of the kind; the
only `0.5` in `joulewise/arm_readiness.py` is `reference_bound_seconds`
(`:6817`), unrelated. **No tracked artifact implements the ruled replay, and no
exhibit claims one was run.**

The substitution is also far cheaper than what was ruled, which is the point:
the ruled replay is a real-time `execute` over twelve slots — 600 + 11×620 +
600 ≈ **8020 s ≈ 2 h 14 min of daytime bench time** — while the dry check runs
in seconds. **Failure scenario:** the arm proceeds, the drift cure is
incomplete, the in-chain abort fires at envelope 02 (≈ 21 min by the ruling's
own costing), and the window is spent for nothing — exactly what the ≤ 0.5 s
precondition buys off *before* a window is committed. **Minimum cure:**
execute and record the replay by name as a tracked artifact carrying per-slot
chain-level `start_drift_s` for all twelve slots, the archived-plist source
for the injected recorder, and an explicit "not R6 evidence" label. No arm
until it exists and every slot is ≤ 0.5 s. **NIT 5:** Q7's Facts say the
equivalence "is not established"; the ruled replay has no implementation at
all.

## Charter §6 packet hygiene

Clean where §6 looks first: generator-produced exhibits, D1–D3 labelled
argument twice (`:3`, `:128`), the D2/D3 naming collision pre-empted (`:5`),
contrary evidence included (step 22, `:23`), five divergences self-reported
(`:17`). Misses: **H1** the only Q6 exhibit substitutes a proxy for the ruled
`timed_log_matches` — cheap, not run (MATERIAL 7); **H2** no exhibit tests
r7's self-description against its own pins, and the field diff is framed
affirmatively, hiding BLOCKER 1 (MATERIAL 1); **H3** Q2's options are three
variants of one mechanism, with no detection-before-t0 option and (a)'s own
OS-update failure mode unstated (MATERIAL 2); **H4** Q3's Facts omit the
seat's reconciliation at exhibit A `:593-597` while quoting the comment it
answers (MATERIAL 5); **H5** D2 §N4's "rename of a ruled field" is reproduced
unflagged in a packet that flags five smaller divergences (MATERIAL 6);
**H6** the magistrate ran the real `/usr/bin/log show` twice to make the
captures and recorded no wall time — the cheapest direct measurement of the
quantity Q3 bounds, free at capture, and unobtainable by a judge forbidden the
real `log`; **H7** Q1 and Q2 are compound as posed — I answered the sub-parts
separately, and a REFUSE on one must not carry the others.

None of these defeats a question.
