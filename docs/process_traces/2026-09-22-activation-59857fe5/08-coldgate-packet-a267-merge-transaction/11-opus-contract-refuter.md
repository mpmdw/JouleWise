# Opus contract-lens refuter — cold gate #3 (A267 + A269 merge transaction)

Charter digest: expected `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`
(convening prompt / packet §Charter pin); observed, by `shasum -a 256
docs/process/coldgate_charter.md` at the bookkeeping head: identical. Exhibit
manifest: all eight digests recomputed, all eight MATCH. Module run (the one
permitted): `tests.test_quiet_predicate_campaign` at `489b0953` in
`JouleWise-wt-a267-review2` → `Ran 98 tests in 9.254s OK`.

## Part 2 first — exhibit C re-executions (four, three required)

1. **r6→r7 recursive field diff.** My own leaf walk over `e52c7fbc`'s two
   artifacts: 428 leaves each, none added, none removed, **3 changed** —
   `.acceptance_id`, `.derivation_sha256`,
   `.prospective_rederivation.estimator_code_sha256.joulewise/uncertainty_evidence.py`
   (`257cda08…` → `b583f35a…`). **AGREE** with exhibit A.
2. **Four estimator digests at `489b0953`.** `git show 489b0953:<path> | shasum
   -a 256` for all four: `70f47086…`, `386e8254…`, `7b9c0d28…`, `b583f35a…` —
   all four equal r7's pins. r7 file digest `14c891eb…` equals
   `ANCHOR_V3_R7_ACCEPTANCE_BOUND_SHA256` at `calibration_bracketing.py:141`.
   **AGREE** with C1 and C5.
3. **Header guard over the saved bodies.** Re-implemented
   `timed_log_has_header` and the proposed constant, run over all eight bodies
   of C3/C3b. Every one of the sixteen cells reproduces, including
   `now=True / prop=False` on the compact header alone and
   `now=False / prop=True` on the 51-byte zero-match capture. **AGREE** with
   C3 and C3b.
4. **The check the packet did not run (see Q6).** `timed_log_matches` — the
   function ruling 14 R3 regression 12 actually names — over both 191-line
   bodies: **10 events on each** (10 `applied`, 20 `syscalls`, **0 unparsed
   moments** on both). The packet exhibited `timed_log_marker_lines` (30/30)
   instead.

## Q1 — transaction shape and r7's admissibility

**Shape (a): LICENSED.** D-138 (exhibit B1, `docs/decision_log.md:10372-10374`
@ `c8812172`) says such branches "merge ONLY inside the atomic Phase-2
successor re-freeze transaction that re-issues the acceptance artifact and
every dependent pin". "Atomic" qualifies the *transaction*, and nothing in the
text speaks to commit count; a single merge commit from one branch carrying
both deltas leaves main with no state in which the feature landed and r7 did
not. (c) is forbidden by that same sentence. Clause (2) ("Follow-on work …
RIDES THE SAME BRANCH", `:10375-10378`) affirmatively supports rebasing r7
onto the feature head rather than a second branch. C4's empty path
intersection (which I did not re-run) means the rebase is textually trivial.

**By-hand r7: LICENSED, and the stale reissue script is a non-issue.** D-138
clause (3) at `:10378-10379` reads "The re-issue and pin update remain
**lead-owned** inside the re-freeze". Lead-owned by-hand preparation is the
ruled shape, not a deviation from it; no authority in the packet conditions
issuance on a generator.

**BLOCKER 1 — r7 as prepared is NOT admissible: the artifact misdescribes its
own delta.** `derivation_notes.reissue_delta.changed_estimator_pins` in r7 (at
`e52c7fbc`) is byte-identical to r6's and says:
`joulewise/uncertainty_evidence.py` → `{predecessor 67e34a1a…, reissued
257cda08…}` and `joulewise/reduce.py` → `{predecessor 1da45a47…, reissued
7b9c0d28…}`. But `257cda08…` is **r6's** pin; r7's live pin is `b583f35a…`.
And `reduce.py` did not rotate in r7 at all. The sibling field
`science_neutrality_evidence` likewise still describes "the full 19-member
corpus … reproduced the r4 derivation record exactly" — r6's evidence
sentence, not r7's 17-member/38-member proof. **Failure scenario:** an auditor
authenticating a future pack reads r7's own reissue record, believes the
governed deriver bytes are `257cda08…`, finds `b583f35a…` on disk, and cannot
tell a pin-rotation error from a tampered artifact — the exact
"accidental estimator drift" invariant D-138 `:10368-10369` exists to protect,
defeated inside the artifact that is supposed to carry it. **Minimum cure:**
rewrite `reissue_delta` to name only `uncertainty_evidence.py` `257cda08…` →
`b583f35a…`, replace `science_neutrality_evidence` with r7's own evidence,
then recompute `derivation_sha256`, the file digest and
`ANCHOR_V3_R7_ACCEPTANCE_BOUND_SHA256`, and re-run C1/C2/C5.

**MATERIAL 1 — the packet's evidence design cannot see BLOCKER 1.** Exhibit
A's field diff answers "what changed"; no exhibit asks "does the artifact
describe itself correctly". The packet then uses the 3-of-428 result
affirmatively ("a pure pin delta", §Q1 Facts) — the same number that is the
*proof* of the defect, since the 425 unchanged leaves include the block that
had to change. The lead's pre-merge proof set (i)–(vii) inherits the blind
spot and must gain: **(viii) every `derivation_notes` field that names a pin,
a corpus or a predecessor is checked against r7's own pin block and against
the evidence actually executed for r7.**

**NIT 1.** The packet's step-22 contention-flake classification is correctly
labelled as argument, but the lead's proof set (vi) does not say the
seven-module run must come back clean at the rebased head *without* a flake
allowance. State that it must.

## Q2 — the header guard

**Option (a): LICENSED but OVER-FIT.** Ruling 14 R4 (exhibit B2,
`14-coldgate-fable-rebuttal-ruling.md:23`) fixes the argv verbatim, including
`--style syslog`; option (c) would amend a sealed ruling to suit a fixture and
is correctly rejected. (b) is correctly rejected. Nothing forbids (a).

**MATERIAL 2 — the frozen constant pins column widths no authority fixes.**
The proposed constant carries 23 literal spaces between `Timestamp` and
`(process)`. `log show --style syslog` column widths are an undocumented
`logd` rendering detail of Darwin 25.6.0, not a ruled interface. **Failure
scenario:** a macOS point update widens the PID column by one space; the guard
returns `False` on every envelope of a ~3 h night; all twelve become
`asserted` with `network_time_unattested`; `minimum_retained` 8 is unmeetable;
the night yields nothing and the loss is discovered only at harvest. That is
fail-closed in the safe direction for *claims* and fail-open in the costly
direction for *windows* — precisely the trade the lead's own Q3 reasoning
calls the wrong way round ("losing one envelope's claim-bearing state is
strictly cheaper than refusing a ~3 h measurement window"). **Better option
(a′), which the packet does not offer:** compare the first line with
whitespace collapsed — `" ".join(first.split()) == "Timestamp (process)[PID]"`.
It rejects every counterfactual C3b rejects (compact collapses to `Timestamp
Ty Process[PID:TID]`), accepts both live captures, and survives column drift.
**Missing option (a″), stronger still:** run the real ruled argv once at
dry-check time and refuse to arm unless the guard accepts its output. That
converts a silent total loss at harvest into a pre-t0 refusal, and the Q7
dry-check hook already exists. The packet's option set is asymmetric: all
three options are "choose a string test"; none is "detect the mismatch before
t0".

**MATERIAL 3 — the fix list under-enumerates, in the same way the packet
itself names for Q3.** `tests/test_quiet_predicate_campaign.py:20` @
`489b0953` defines `TIMED_LOG_HEADER = "Timestamp               Ty
Process[PID:TID]\n"` with a comment asserting it is "What `log show --style
syslog` prints" — the compact header again, duplicated test-side, with three
call sites (`:1288`, and the `("header only", TIMED_LOG_HEADER,
"authenticated")` row at `:1295`). Under option (a) that row inverts to
`asserted`. R2.1–R2.5 name fixtures and regressions but not this constant.
**Failure scenario:** the fix round lands, the module goes red, and the
cheapest way out is to relax the new guard.

**NIT 2.** The module comment at `quiet_predicate_campaign.py:443-445` states
the false fact ("`log show --style syslog` prints … `Ty Process[PID:TID]`");
it must be rewritten under any option, and the packet does not say so.

## Q3 — the attestation bound

**Option (b): LICENSED; it amends nothing sealed.** The 15 s formula is
brief 06 item 1 (exhibit B6, `06-a267-fix-round-1-brief.md:16`) — magistrate
dictation, not a cold ruling, and this gate outranks it. Ruling 14 R4 fixes no
timeout; its only timing constraint is "the query runs within ten minutes of
the envelope" (B2 `:23`), which 5 s satisfies a fortiori, and A269 ruling 10
Q4(ii) (B4 `:40`) says the ten-minute constraint is "met by construction (gap
≤ 20 s)". 5 s is also licensed on the merits by the sealed ruling's own
accepted arithmetic: A269 ruling 10 Q1 (B3 `:15`) accepts "worst attestation
of 1.45 s", and `quiet_predicate_campaign.py:572-576` @ `489b0953` records
0.70–1.45 s over *one envelope's window*. 5 s is 3.4× the worst figure a
sealed ruling accepts.

**MATERIAL 4 — the lead's rationale for (b) is false in general, and R3.3 is
written over the three protocols that hide it.** `cleanup_budget_s = max(1,
gap−5)`; option (b) is `max(5, gap − cleanup_budget_s)`. The two sum to the
gap **only when gap ≥ 6**. At gap = 3: cleanup 1, attestation 5, sum 6 > 3.
`validate_protocol` is required by A269 Q1 A2 (B3 `:15`) to reject
`slot_pitch_s < envelope_s` — it is not required to reject a sub-floor gap.
R3.3 asserts the invariant for v2 (20), SCALED (6) and pitch 700 (100) — every
one ≥ 6. **Failure scenario:** a future registration with a 4 s gap passes
validation, both budgets over-claim it, and the "defect-shaped regression"
that was supposed to make over-claiming impossible is green. **Cure:** either
state the invariant with its precondition, or have `validate_protocol` reject
`slot_pitch_s − envelope_s < ATTESTATION_TIMEOUT_FLOOR_S + 1` and then assert
R3.3 as a property over arbitrary valid protocols.

**MATERIAL 5 — packet hygiene: the seat's own reconciliation is omitted from
Q3's Facts.** The packet frames 15 s as an unresolved self-contradiction
("Two bounds, each claiming 15 s of the same 20 s gap"). Exhibit A
`:593-597` contains the seat's explicit, reasoned defence — 15+15 exceeding 20
is "deliberate and visible", because the next spawn then trips
`start_drift_abort_s` and the night ends at a named abort. The Facts paragraph
quotes the comment the 15 s bound contradicts and not the docstring that
answers it. I still rule for (b) — refusing a ~3 h night to avoid losing one
envelope is the worse of two fail-closed outcomes — but the judge is entitled
to the seat's argument in the Facts, not buried in exhibit A.

**Agreement:** the packet's five-pin enumeration is right and the dictation's
"two test pins" is wrong. I read `:1259`, `:1260` (SCALED, unchanged under
(b)), `:1262`, `:1267`, `:1269`, `:1274` and confirm.

## Q4 — the two window keys

**AFFIRM the outcome; REJECT the label.** A269 ruling 10 Q4(i) (B4 `:39`)
rules `window_epoch_s` to be the union window. Brief 06 item 14 (B6 `:29`)
re-assigns it. A magistrate brief cannot amend a sealed cold ruling, so item
14 was **void to that extent** and the seat was not licensed to follow it.
Calling this a "seat deviation to ratify" sets the wrong precedent — that
seats depart from briefs by grace, rather than that briefs cannot override
rulings. Record it as a **correction of brief 06 item 14**, and add the
standing rule the episode earns: where a brief and a sealed ruling conflict,
the ruling governs and the seat returns NEEDS_RULING or follows the ruling.

**MATERIAL 6 — exhibit D2 §N4 is factually wrong and the packet reproduces it
unflagged.** I verified at `489b0953`: `window_epoch_s` still carries
`attestation_window(stamps)` (`:641`) and `window_argv_epoch_s` is a **new**
key (`:642`). Nothing was renamed. The packet names five other divergences
between dictation and evidence but not this one, in a §Q4 Facts paragraph that
quotes D2's characterisation verbatim.

**AFFIRM the null-initialisation.** `attestation` is built at `:618-622` with
`window_epoch_s: None` and no `window_argv_epoch_s`; the `blocked` and
`capture window unavailable` returns therefore omit the key. Adding it to the
skeleton is correct and costless.

## Q5 — the seven fix-round-2 items

All seven verified against `489b0953` and **AFFIRMED as dictated**: item 1
(`record_attestation:691-692` returns `False` with `state` untouched — and the
cure propagates, because `execute` reads `attestation["state"]` at `:1112`
*after* calling `record_attestation` at `:1109`); item 2 (`:700-713`, no
`unlink`); item 3 (`:1159`); item 4 (`:411-412`); item 6 (`:604` default);
item 7 (no change needed).

**NIT 3 — item 5 is under-scoped.** `timed_log_moment` (`:481-489`) matches
only `\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+` and `strptime`s it naive-local,
**discarding the `-0700` offset that `--style syslog` actually supplies** (the
compact fixture has no offset; the live capture does —
`02:28:08.335838-0700`). So the daylight-saving ambiguity item 5 documents at
one call site exists at a second one, where the syslog style hands the code
the disambiguating information and the code throws it away. Severity is NIT
only because `TIMED_LOG_EVENT_WINDOW_S` is a 1 s *grouping* tolerance and any
nonzero count excludes the envelope. Extend item 5's docstring sentence to
`timed_log_moment`, or parse the offset.

## Q6 — the already-sealed A267 gate

**AFFIRM — no sealed finding need be re-opened — but on evidence the packet
did not supply.** Ruling 14 R3 regression 12 is "the scanner over exhibit D
returns 10 matches"; the scanner is `timed_log_matches`, not
`timed_log_marker_lines`. The packet's parity argument rests entirely on
`timed_log_marker_lines` = 30/30 (C3) — a different function, and one whose
agreement does not entail the other's, because `timed_log_matches` calls
`timed_log_moment`, which *parses* each line and is the only style-sensitive
step. I ran the right one: **10 events on the compact fixture and 10 on the
live syslog capture, with zero unparsed moments on either.** Regression 12's
bar holds in both styles. **MATERIAL 7:** substituting the wrong function for
the ruled one in the only exhibit that answers Q6 is an evidence defect, not a
merits defect; the cure is to add the `timed_log_matches` row to C3 so the
record shows the ruled bar, not a proxy for it.

**NIT 4 — a second style artefact the packet does not mention.** `--style
syslog` renders **no level field at all**: `grep -c ' Df '` and `grep -c
'<Debug>'` over the live capture both return **0**, while the compact fixture
shows ` Df `. Ruling 14 R4's cited evidence ("the apply lines are `Df`", B2
`:23`) and the judge's probe note at `14-…-ruling.md:7` ("exhibit D grep
(`cmd,apply,src,adjtime` × 10, level `Df`)") are therefore unobservable in the
output the ruled argv produces. The **substance survives**, and I verified
why: `--info --debug` govern which entries are *retrieved*, not how they are
rendered, and the live syslog capture — taken under the ruled argv — does
carry all ten `cmd,apply,src,` receipts. The argv's two flags are
independently pinned at `tests/test_quiet_predicate_campaign.py:768`. No
re-opening is required; the ruling's *illustration* is style-bound, its
*holding* is not.

## Q7 — may the next pilot night be armed

**REJECT the lead's disposition. BLOCKER 2.** A269 ruling 10 Q3's replacement
R6 clause (B4 `:35`) requires, before the night is *prepared*: (i) cure Q1(c)
landed under registration v2; (ii) "**a daytime bench replay — real `execute`
and real collector with an injected recorder replaying an archived plist, no
sudo, no measurement, never labeled R6 evidence — shows chain-level
`start_drift_s` ≤ 0.5 s on every slot**"; only then (iii) the night is the
live check. A269 Q2 (B3b `:27`) adds that both A267 Part 3 and A269 must be
merged first.

The lead substitutes "the tracked entry point's dry check". I checked whether
those are the same thing and they are not: `scripts/gen_evidence_night.py`
renders and seals a wrapper and explicitly "Never install or collect" (its
module docstring); it contains no occurrence of `dry`, `replay`, `drift` or
`check`. A repository-wide grep for an injected-recorder replay
(`injected recorder|inject_recorder|--recorder|replay`) over `scripts/*.py`,
`joulewise/*.py` and `scripts/night_chains/` returns nothing of the kind, and
the only `0.5` in `joulewise/arm_readiness.py` is `reference_bound_seconds`
(`:6817`), unrelated. **No tracked artifact implements the ruled bench
replay, and no exhibit in the packet claims one was run.**

The substitution is also materially cheaper than what was ruled, which is why
it matters: the ruled replay is a real-time `execute` over twelve slots —
settle 600 s + 11 × 620 s + 600 s ≈ **8020 s ≈ 2 h 14 min of daytime bench
time** — and the lead's formulation would let the arm proceed on a dry check
measured in seconds. **Failure scenario:** the arm proceeds; the start-drift
cure is in fact incomplete; the in-chain abort fires at envelope 02
(≈ 21 min by the ruling's own costing) and the window is spent for nothing —
which is exactly the outcome the ≤ 0.5 s precondition exists to buy off
*before* a window is committed. **Minimum cure:** execute and record the
replay by name, with a tracked artifact carrying per-slot chain-level
`start_drift_s` for all twelve slots, the injected recorder's archived-plist
source, and an explicit "not R6 evidence" label; the arm is not licensed until
that artifact exists and every slot is ≤ 0.5 s.

**NIT 5.** The packet's Q7 Facts do not state that the ruled replay has no
implementation, only that the equivalence "is not established". The assembler
flagged the gap honestly; it understated its size.

## Part 4 — charter §6 packet-hygiene check

The packet is unusually clean on the dimensions §6 names first: exhibits are
generator-produced, D1–D3 are labelled argument in the header and again at
`:128`, the naming collision is pre-empted at `:5`, contrary evidence (the
step-22 failure) is included at `:23`, and five dictation/evidence divergences
are self-reported at `:17`. The misses:

- **H1 (→ Q6).** The only exhibit answering Q6 substitutes
  `timed_log_marker_lines` for `timed_log_matches`, the function the ruled
  regression names. Cheap to run; not run. (MATERIAL 7.)
- **H2 (→ Q1).** No exhibit tests r7's self-description against r7's own
  pins; the field diff is presented affirmatively in a way that conceals it.
  (MATERIAL 1, and it hides BLOCKER 1.)
- **H3 (→ Q2).** Asymmetric option construction: three variants of one
  mechanism, no pre-t0 detection option, and no statement of (a)'s own failure
  mode under an OS update. (MATERIAL 2.)
- **H4 (→ Q3).** The Facts paragraph omits the seat's reconciliation at
  exhibit A `:593-597` while quoting the comment it answers. (MATERIAL 5.)
- **H5 (→ Q4).** Exhibit D2 §N4's "rename of a ruled field" is reproduced in
  the Facts unflagged, in a packet that flags five smaller divergences.
  (MATERIAL 6.)
- **H6 (→ Q3).** The magistrate ran the real `/usr/bin/log show` twice to
  produce the two captures and did not record the wall time — the single
  cheapest direct measurement of the quantity Q3 bounds, obtainable at zero
  marginal cost, and unavailable to the judge, who is forbidden the real `log`.
- **H7 (→ Q1, Q2).** Q1 and Q2 are compound as posed (Q1: shape + r7
  admissibility + the re-execution set; Q2: constant + fixtures +
  regressions). Each sub-part is separable and I have answered them
  separately; a REFUSE on one should not carry the others.

None of these defeats a question. My verdicts: **Q1 licensed as to shape,
REJECT as to r7-as-prepared (BLOCKER 1); Q2 licensed but amend to (a′) plus
the pre-t0 self-test; Q3 AFFIRM (b) with the invariant corrected; Q4 AFFIRM
the outcome, reject the "ratification" framing; Q5 AFFIRM all seven, item 5
extended; Q6 AFFIRM on re-executed evidence; Q7 REJECT (BLOCKER 2).**

Where I am silent, read concurrence with the lead.
