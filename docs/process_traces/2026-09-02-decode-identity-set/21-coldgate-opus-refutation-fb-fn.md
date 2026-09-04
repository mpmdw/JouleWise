# File 21 — Opus 5 contract-lens refutation on packet 19 (F-B / F-N), 2026-09-02

Custodied verbatim from the seat's final message (Agent tool, model opus, read-only, packet + primary evidence only; scratchpad paths redacted). Note: the seat's finding P1 (files 07 and 13 carried swapped filenames) was verified and the two files were renamed by `git mv` in the same commit that carries this file; the seat's citations below refer to the names as they were BEFORE the rename.

---

---

## Disclosure

**Contamination:** NOT CLEAN. This session's harness auto-loaded `/Users/edr/.claude/CLAUDE.md`, `/Users/edr/code/JouleWise/CLAUDE.local.md` (the full orchestration doctrine, rules 1–11 including the rule-11 trigger text), and the path-keyed session memory index — all present at launch, none suppressed. Per charter §"Convening procedure" cl.2 this ruling is not void per se, but the magistrate must weigh that I read rule 11's own wording before classifying against it, and read the 2026-08-19 writing standard before applying it. I have read nothing else in the repo beyond the packet, the files it names, the charter/registry, and the code/tests the questions require.

**Charter digest — verified independently:**
```
$ shasum -a 256 docs/process/coldgate_charter.md
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  docs/process/coldgate_charter.md
$ registry docs/process/coldgate_charter_registry.md, "Operative charter" table:
| sha256 | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` |
```
Match. Status RATIFIED.

---

## Q1 — F-B classification, and the biting fixture

**Classification: FIRST-ROUND finding against the mutation-cure rule. Rule 11's "second fix round on the same defect" is NOT met.**

Argued from the documents' own words. F-B entered as Opus 204 F1 and was dictated in the round-1 brief (**file 07 line 46**, not file 13 — see Finding P1) as: *"Closure: authenticate the pack inside the gate ... by re-verifying the pack digest ... BEFORE any field is trusted; a mismatch returns the gate's refusal. **Regression (F-D below) is the tampered-pack test.**"* The brief therefore named the regression by **cross-reference to F-D**, whose own clause reads: *"add un-mocked tests ... (1) tampered pack (one receipt byte flipped after freeze, sidecars left stale) → returns None ... Then confirm by a scratch mutation (revert after) that `return frozenset()` in the gate now fails at least one of them."* Read as a contract, the brief asked for a mutation confirmation of **`return frozenset()` at the top of the gate** — not of the pack-tree comparison. Sol 214's clause map obeyed that literal contract: it lists `inputs.py:3898` under both F-B and F-D and names `test_analysis_inputs.py:547` as the biting test, and the F-D row's counterfactual is `Replace consumer gate with return frozenset()` — which genuinely is killed.

So Sol 214 did not fail a stated obligation twice. It satisfied a brief whose named regression was **under-specified**: the brief's "tampered pack" fixture (one receipt byte flipped, sidecars stale) is caught upstream by the receipt's own byte-digest sidecar, so it can never reach line 3898's decision. The clause map's "Counterfactual" column then recorded an edit (*"Remove committed-pack digest comparison"*) that nobody executed — the map claims a counterfactual, it does not evidence one.

**Does a closure "with a named biting test that does not bite" satisfy the brief?** No — but the clause it violates is the brief's own §"Clause map (mandatory)": *"biting test `file:line`, counterfactual (the one-site edit that test fails on) **or `NOT PINNED: <reason>`**."* The brief offered an honest escape hatch and Sol used it correctly four times (F-L, F-M, F-N). For F-B it asserted a pin instead. That is a **false clause-map entry** — one defect, discovered once, never previously briefed as its own item. Rule applied: rule 11's trigger counts **fix rounds on a defect**, and this is round one for *"F-B's check has no biting test."* The counterfactual-input rule (`mutation-cure-counterfactual-rule`: *"fix-round briefs must name the counterfactual input + production call site"*) is the rule the round-1 brief broke, and it stands on its own without rule 11.

**The magistrate should not take comfort from that.** Classifying this as first-round is correct and also nearly irrelevant: the standing escalation trigger (same signature two rounds running) fires elsewhere — see Q2.

### Independent verification, at the CURRENT head (stronger than the packet's claim)

The packet ran at `3ac6cffb` (6 tests). I ran at `b9b55e90` = `9e4b7c35` + docs, i.e. **after round 1b added four production-label tests to the same class**:

```
$ shasum -a 256 <scratch>/inputs.py.orig
42423f08c38d3aba7f7f42ec0b4b6a4bc3d17ca046493c24878247d493aa4ca1
$ python3 -  # replace inputs.py:3898 comparison with `if False:`  (assert count==1)
MUTATED
$ git diff --stat
 joulewise/analysis_engine/inputs.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

$ TMPDIR=<scratch> python3 -m unittest tests.test_analysis_inputs.FrozenConsumerIdentitySetTests
..........
----------------------------------------------------------------------
Ran 10 tests in 12.497s

OK

$ TMPDIR=<scratch> python3 -m unittest tests.test_analysis_inputs
...............
----------------------------------------------------------------------
Ran 15 tests in 12.419s

OK

$ cp <scratch>/inputs.py.orig joulewise/analysis_engine/inputs.py
$ git diff --exit-code; echo rc=$?
rc=0
$ git status --short
(empty)
```

The whole module — including all four `test_production_*` label tests round 1b wrote — is green with the check dead. **Round 1b did not accidentally close F-B.** The packet's claim is true and understated.

### The defect-shaped fixture — buildable, executed

The reason no fixture bites is structural and visible in one line: every test computes the lineage value as `"pack_sha256": committed_pack_tree_sha256(pack)` (`tests/test_analysis_inputs.py:456, 534, 723`) — **the two sides of the comparison are made equal by construction**, and `committed_pack_tree_sha256` hashes *committed* blobs (`arm_readiness.py:2750`, `git ls-tree HEAD`), so every existing tamper (working-tree byte flips) is invisible to it.

The biting shape: capture the lineage digest, **then commit** a change inside the pack, then resolve with the now-stale lineage. Nothing the gate reads downstream changes, so line 3898 is the only check that can refuse. Executed from the existing helpers (`_generated_frozen_gate_pack` → `_generated_transport_case` → `_production_floor_resolution`), ~15 lines, scratch module, no checkout file created:

```
# CHECK PRESENT
CONTROL (untampered) status = refused reasons = ('cell_missing', 'consumer_term_unknown')
lineage pack_sha256 = f1919653d740de8f018d9b173b7b6f796a54f9f2a47ddc318cfb0932c81a8186
committed now       = 4c39e3921d031558e232a8e6b8f98102c56934d8fa0f26f2a1ccb1b195efe50e
TAMPERED status = refused reasons = ('consumer_identity_set_unauthenticated',)

# CHECK DISABLED (`if False:` at 3898)
CONTROL (untampered) status = refused reasons = ('cell_missing', 'consumer_term_unknown')
TAMPERED status = refused reasons = ('cell_missing', 'consumer_term_unknown')

$ cp <scratch>/inputs.py.orig joulewise/analysis_engine/inputs.py
$ git diff --exit-code; echo rc=$?
rc=0
```

`assertEqual(resolution.reason_codes, ("consumer_identity_set_unauthenticated",))` bites exactly and only the pack-tree comparison. **Nothing is missing** — the fixture is buildable today with no new plumbing. Round 2 should additionally make it *defect-shaped* rather than merely discriminating, by committing the Opus 204 forgery itself (re-point `plan_tree`'s `identity_pin_projection.projection_receipt` at the prefill unit's receipt, re-render receipt + sidecar + both `plan_tree` refs, commit) — same assertion, and it demonstrates the returned set would otherwise be the wrong unit's. My marker-key variant is the cheap floor; the forgery variant is the one that matches the origin story.

---

## Q2 — the two prose findings, read as a first-time reader

**Terra F2 is a NEW first-use defect on NEW text, not a second round on F-N.** F-N (round 1) was an **ordering** defect over an enumerated list of six already-existing terms (`U8`, `U11`, launch lineage, exact-cell route, condition-family transport, transport group), with a dictated closure: *"reorder or add a short definitions block BEFORE the analysis-gate section."* That closure landed at 563–579 and works — I checked each of the six. Terra F2 is about a paragraph that did not exist when F-N was written (R-M5, round 1b), and about **different terms coined in that paragraph**. Different text, different terms, different failure mode. Rule 11 not triggered.

First-use audit of 602–614, mechanically, as instructed:

| Term at 602–614 | First use | Defined? |
|---|---|---|
| launch lineage / successor | 603 | 569 ✓ (as "launch lineage"; "successor **pack**" used at 583, never glossed — minor) |
| pack digest | 604 | 570, inside the lineage definition ✓ (weak but present) |
| U8 freeze receipt | 605 | U8 at 565 + "readiness freeze receipt" at 585 ✓ |
| sidecar | 605 | prior sections ✓ (terra confirms) |
| **U11 receipt** | 605 | ✗ **fails.** 567 defines U11 as "the identity-pin projection **subsystem** and its projection-evidence **row** inside the U8 freeze receipt." 588 calls the artifact "the bound **frozen identity receipt** and sidecar." "U11 receipt" is a third name for an object the doc has already named twice differently, and the reader cannot tell which of the three things at 567/588 failed to authenticate. |
| projection is not frozen / selected unit / inventoried config bytes / re-derived set / unit config-set digest | 606–608 | earlier sections and 590–592 ✓ |
| **frozen declaration** | 613 | ✗ **fails.** Fourth synonym for "the frozen set" (used at 594 and 609), coined in the paragraph's final clause. Unpaid work: the reader must equate it with the set to parse the sentence. |

Terra is right on both, and only those two. Its added complaint that the paragraph *"is not standalone as requested"* is **not** a requirement R-M5 stated — R-M5 asked for "ONE plain-language paragraph ... built from the mechanism," not a self-contained one — and "the authentication sequence above" resolves to the paragraph immediately above (583–592), which does spell the sequence out. That half of F2 should be rejected.

**Luna's F-N residual — `work_order` is `D117-U11-IDPIN-PROJECTION` at line 184: NOT a first-use violation.** The standard governs *"every term of art, criteria word, or verb doing technical work."* At 184 the string is a **value the reader must reproduce byte-for-byte**, not a term whose meaning the reader must hold; no claim in that bullet depends on decomposing it, and replication is unimpaired by not knowing what U11 means. Treating substrings of opaque identifiers as uses is unfalsifiable and would force glossing `u11-freeze-projection`, `desk.identity_pin_projection.v1`, and `joulewise.identity_unit_config_set.v1` at every occurrence. Contrast 605, where the reader *must* resolve "U11" to know which artifact failed — that is a use. **Close luna F-N as NO CHANGE with that reasoning recorded**; do not spend a fix round on it. (If the magistrate wants belt-and-braces, a five-word parenthetical at 184 is free — but it is a courtesy, not a defect cure.)

**What closes each:**
- Terra F2 half 1 (`U11 receipt`) → **gloss in place**, one edit: replace with "the frozen identity-pin projection receipt (the U11 receipt bound by that U8 evidence row)" at 605, and add "also called the **U11 receipt**" to the 567 definition. Not a rewrite.
- Terra F2 half 2 (`frozen declaration`) → **one-word substitution** at 613: "when no frozen set has been declared." Uses the term already in the paragraph.
- Terra F2 half 3 (standalone) → **reject**.
- Luna F-N residual → **reject / no change**.

**But the signature fires.** Round 1's prose closure produced a first-use residual; round 1b's prose closure produced two more, in the same contract section, from the same seat under the same instruction ("no term used before it is glossed"). That is the standing escalation trigger — *same defect class, another failed formulation* — and the next spend must not be a third "Sol, write the paragraph again." The formulation has to change: the magistrate dictates the sentences (dictated-fills), or the brief carries a **mechanical checklist the seat must execute and paste** — enumerate every noun phrase in the new text, give line-of-first-use and line-of-definition for each, and paste that table in the report. Neither round asked for that; both rounds failed the same way. That is the finding the magistrate should act on, more than F2 itself.

---

## Q3 — composition of fix round 2

**May land as ONE fix round: F-B's biting test, F-COUPLING's unmocked test, terra F1's mapping pin, and the prose cures.** All four are additive (three test methods + two prose edits); none touches production semantics; the only shared file is `tests/test_analysis_inputs.py`, which one seat writes serially. WRITE_SCOPE: `tests/test_analysis_inputs.py`, `tests/test_analysis_engine.py` (or wherever `_floor_engine_reasons` is testable), `docs/contracts/identity_pin_projection.md`. Delta re-audit by a model other than luna/terra.

**Terra F1 needs no new ruling.** R-M3 already ruled the semantics with a default — *"decide whether the two new codes should map there (default: yes, they are transport-inapplicable) and state it; do not add a new engine reason"* — and Sol 258 stated it and executed it (`consumer_identity_set_unauthenticated -> floor_transport_inapplicable`). Pinning a ruled default is mechanical. One line of magistrate ratification in the brief ("the R-M3 default is now the pinned semantics") is sufficient and is not a ruling round.

**F-G is the one clause I would refuse to let the magistrate brief without a ruled semantics.** The round-1 brief's own F-G clause says the mismatch state *"is hard to reach under the preceding checks"* and dictated the closure Sol delivered: *"extract the cardinality check into a pure helper ... and unit-test a synthetic mismatch."* Sol did exactly that. Luna's F-G is therefore a finding **against the ruling**, not against the implementation, and it poses a question the ruling never answered: is the cardinality check **dominated** (unreachable given the preceding checks — in which case the correct cure is a documented defensive-unreachable justification, a pattern this repo already has at `tests.test_arm_readiness_integration...test_refusal_registry_coverage_and_defensive_unreachable_justifications`), or is it genuinely reachable? Briefing "add a production-path test" without settling that invites a seat to **weaken a preceding check** to manufacture reachability — a real regression risk on a fail-closed path. Rule the semantics first, in one sentence, then brief. Until then F-G stays out of round 2 or enters as "document the dominance" only.

---

## Q4 — what a consumer loses today, in the mechanism's terms

**Nothing, right now — and no guarantee that stays true.** The check is present and, as executed above, a committed post-arm pack tamper is refused with `("consumer_identity_set_unauthenticated",)`. A self-consistent forgery of the Opus 204 kind is stopped at line 3898 before any `plan_tree.json` field is trusted.

What is missing is the mechanism that keeps it present. The entire `tests.test_analysis_inputs` module is green with the comparison dead, so any future edit that removes it — a refactor of the `try:` block, a change to how `pack_root` is resolved, a merge that drops two lines — lands green and unremarked. The exposure that would return is precisely the one the check was added to close: `_frozen_consumer_identity_set` would read `plan_tree.json` out of a pack **that is not the pack the arm authorization consumed**, and return that pack's declared set. Opus 204's demonstration returned the prefill unit's set `365b4a41…` where the decode unit's `604f6e22…` belonged — i.e. an evidence row would be checked for membership in the **wrong unit's** declared identity set, and a floor row transported into a decode claim on the strength of a prefill unit's declaration, presented as authenticated.

There is a compounding second-order loss the packet does not name. `consumer_identity_set_unauthenticated` is the label round 1b existed to create — the label that makes an authentication failure legible in the analysis artifact rather than collapsing into `consumer_term_unknown`. My mutated run shows exactly that collapse: with 3898 dead, the tampered pack came back `('cell_missing', 'consumer_term_unknown')` — indistinguishable from an ordinary no-match. So a silent regression at 3898 does not merely re-open F-B; **it silently re-opens F-M**, undoing round 1b's entire benefit with no test anywhere going red.

---

## Findings against the packet (charter §6)

**P1 — Mis-citation of the round-1 brief. SHOULD-FIX.** Packet line 16 names *"round-1 brief `13-…`"*. File 13's content is the **original implementation brief** (R-1..R-8, "FIX — decode-unit identity under prompt rotation", authority ruling 171a). The actual round-1 fix brief — the one carrying the F-A..F-P closures, headed "FIX round 1 — decode-identity set (branch ... @ `1a608089`)" and citing luna 202 / Opus 204 / terra 206 — is **file 07**, filed as `07-implementation-brief-192.md`. The two files' contents are swapped relative to their filenames, and custody commit `7c87fa71`'s message repeats the wrong mapping ("landing 192 ... fix rounds 1 and 1b briefs"). The packet then cites *"brief file 07 line 46"* for F-B's origin — correct by content, contradicting its own header. A seat obeying the header reads file 13 and finds **no mention of F-B at all**, and no F-D cross-reference — which is the exact evidence needed to classify Q1. Fix the packet line and rename the two trace files; the wrong labels outlive this gate.

**P2 — Embedded conclusion in Q1's stem. SHOULD-FIX.** Q1 opens *"The F-B production check exists and is correct"* while the packet's header states the magistrate *"does NOT classify."* "Exists" is verifiable from the quoted lines; **"is correct" is a judgment the seats were convened to test** — it forecloses the possibility that the check is present but circular or mis-targeted. It happens to be true (I confirmed it refuses), but it should have arrived as evidence, not as a premise handed to the classifier.

**P3 — Transcription presented as pasted output. NIT.** §"Executed evidence" is a reconstructed listing, not a terminal transcript: `<scratch>` placeholders, a hand-written `REVERTED-CLEAN` echo, and a `unittest` tail that omits the `----` separator line Python actually prints between the dots and `Ran 6 tests`; the `git log -L` line shows a grep's output labelled as the command's. Named because this same packet asks seats to distinguish a *named* test from a *biting* one — the standard should apply to the packet's own evidence.

**P4 — Counterfactual not re-run at the head being decided. NIT.** The evidence is from `3ac6cffb`; the lane head is `9e4b7c31`/`b9b55e90`, where round 1b added four tests to the same class. One command would have confirmed the defect is still open at the head the seats are ruling on. It is (10/10, 15/15 above), so nothing was misstated — hence nit, not should-fix.

**P5 — Omission: the packet never asks what authenticates `pack_sha256`. NIT.** F-B's closure compares a digest computed from the pack against a value **read off the evidence row**. That is authentication only if the lineage is itself authenticated upstream; the contract asserts it at 569–570, and `joulewise/bundle.py:87–147` does call `authenticate_campaign_launch_lineage` at write time with the lineage writer-owned and caller-supply rejected (`bundle.py:1056–1062`). So the chain exists — but neither refuter examined it, and a seat asked to bless "the pack is now authenticated inside the gate" should have been shown it. One packet line.

**P6 — Omission: no reachability question posed for F-G.** Folded into Q3; severity carried there, not double-counted.

---

## Verdict block

**Q1 — FIRST-ROUND finding; rule 11 NOT triggered.** The round-1 brief named F-B's regression only by cross-reference to F-D's `return frozenset()` mutation, which is killed; the non-biting pack-tree entry is a false clause-map row, discovered once, never previously briefed as its own defect. *Rule applied:* rule 11 counts fix rounds on a defect, not fix rounds in a lane; the broken rule is the mutation-cure counterfactual rule, which stands alone. **Verified by execution at the current head:** 10/10 class and 15/15 module tests pass with the comparison disabled; a biting fixture IS buildable from the existing helpers and discriminates cleanly (`('consumer_identity_set_unauthenticated',)` present-vs-disabled). Checkout byte-identical, `git diff --exit-code` rc=0.

**Q2 — Terra F2 is a NEW first-use defect on NEW text; not a second round on F-N.** Two of its three limbs hold (`U11 receipt` undefined composite at 605; `frozen declaration` coined at 613); the "not standalone" limb is rejected because R-M5 never required it. **Luna's F-N residual is NOT a violation** — a token inside a fixed identifier is a value to be reproduced, not a term whose meaning the reader must hold; close it no-change. *Rule applied:* the first-use test governs terms doing technical work, not substrings of opaque literals. **Escalation trigger fires on signature:** two consecutive rounds of prose closure produced first-use defects in the same section; round 2's prose brief must change formulation (dictated sentences or a mandatory pasted first-use table), not repeat the instruction a third time.

**Q3 — F-B's test, F-COUPLING's test, terra F1's mapping pin, and the two prose edits may land as ONE round.** All additive; terra F1's semantics is already ruled by R-M3's stated default and needs only one line of ratification. **F-G must not be briefed as written:** its round-1 closure was delivered exactly as ruled, so luna's finding is against the ruling, and the unanswered question — dominated check (document it) vs reachable (build the fixture) — must be ruled first, or a seat may weaken a preceding fail-closed check to manufacture reachability. *Rule applied:* the lieutenant/seat may not improvise a semantics the ruling left open.

**Q4 — A consumer loses no protection today, only its durability.** The check refuses a committed post-arm tamper right now; with it dead, the analysis gate would read the frozen identity set from a pack other than the one the arm authorization consumed and admit an evidence row against the wrong unit's declaration (Opus 204: prefill `365b4a41…` for decode `604f6e22…`). **Compounding loss:** the refusal collapses to `('cell_missing', 'consumer_term_unknown')` — executed above — so a silent regression at `inputs.py:3898` silently re-opens F-M as well, with nothing in the suite going red.

**Packet findings:** 2 should-fix (P1 mis-citation of the round-1 brief and the swapped trace filenames; P2 embedded "is correct" in Q1's stem), 3 nits (P3 transcribed evidence, P4 counterfactual not re-run at the decided head, P5 lineage-authentication omission). None of these voids the packet; P1 should be corrected on disk before this trace is cited again.
