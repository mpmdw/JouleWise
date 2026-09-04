# File 20 — cold Fable seat ruling on packet 19 (F-B / F-N), 2026-09-02

Custodied verbatim from the seat's final message (Agent tool, model fable, read-only, packet + primary evidence only; scratchpad paths redacted). Seat scratch scripts referenced below live outside the checkout.

---

# Cold-gate seat F — decode-identity lane, packet 19 (F-B / F-N)

**Charter digest:** `sha256(docs/process/coldgate_charter.md)` = `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`; registry line 16 carries the same value. **MATCH.**
**Disclosure:** the harness auto-loaded `CLAUDE.md`, `CLAUDE.local.md` and the memory index into my context; I read no other process doc. Checkout `b9b55e90`; `git diff --stat 9e4b7c35 b9b55e90 -- joulewise tests` is empty, so the code and tests I executed are the packet's code head. Checkout left clean (`git diff --exit-code` after every run, pasted below). No file under any checkout was written; the `if False:` counterfactual was applied by re-`exec`ing the function's source into the live module namespace, not by editing `inputs.py`.

---

## Q1 — classification of F-B, and the defect-shaped fixture

**Rule applied.** A fix round "closes" a defect only if it lands both the cure and a test that fails when the cure is removed (the mutation-cure counterfactual rule: the brief must name the counterfactual input, and today's-artifact cures kill nothing). Round 1's brief itself named the regression ("the tampered-pack test"); Sol 214's clause map named `…refuse_stale_receipt_bytes` as biting the removal of the digest comparison. That claim is false (verified below), so round 1 did not close F-B — it landed half a closure and mis-reported the other half. A second round to finish what round 1 claimed to have finished is, by definition, **a second fix round on the same defect. Rule-11 trigger MET.** It is not a fresh first-round finding: the defect identity (F-B: "the gate trusts the pack tree without authenticating it against the lineage") is unchanged; what changed is only that we now know round 1's evidence for it was non-biting. Classifying it as "new finding against the mutation-cure rule" would let a mis-reported closure reset the round counter, which is exactly the sunk-cost move rule 11 exists to prevent.

Severity of the residual: **should-fix, not blocker** — the production check is present and correct (verified: it refuses the forgery), so the paper-facing mechanism is sound today; what is missing is the test that keeps it sound.

**Verification that the named test does not bite.** With the comparison replaced by `if False:`, the whole class (now 10 tests at `b9b55e90`, including the four round-1b label tests) passes:

```
$ python3 $TMPDIR/run_class_disabled.py 2>&1 | tail -5
----------------------------------------------------------------------
Ran 10 tests in 12.052s

OK
PACK-TREE CHECK DISABLED via exec; running FrozenConsumerIdentitySetTests
$ git log --format='%h %ad %s' --date=short -L3898,3899:joulewise/analysis_engine/inputs.py | grep -E "^[0-9a-f]{8} "
3ac6cffb 2026-09-02 Decode-identity fix round 1 (Sol 214): ruling 171a R-1..R-8 closures F-A..F-L, F-N..F-P
CHECKOUT-CLEAN
```

**Is the defect-shaped fixture buildable? YES.** Reading the gate (`inputs.py:3860–4048`) and both validators (`identity_pins.py:500–680`): every check after line 3898 is *internal* to the pack — receipt bytes vs. the sha the plan tree/freeze receipt carry, sidecars vs. those shas, projection `config_set_sha256` vs. receipt `config_set_sha256`, inventoried config bytes vs. inventory sha, re-derived identity set vs. `config_set_sha256`. Validators are structural (exact keys, fixed constants, hex shapes). Nothing but line 3898 ties the pack to anything *outside* the pack (the lineage's `pack_sha256`). So a forger who rewrites the whole chain consistently is refused only by line 3898.

**Fixture (built from `_generated_frozen_gate_pack`, 14 write steps, script `$TMPDIR/forgery_probe.py`, sha256 `7e5f4804…e4fa`):**
1. Build the honest pack; build the consumer case so the lineage records the **honest** committed tree digest (this is what a real launch stamps on the bundle).
2. Drift consumer bundle 0's scientific identity (append tag `identity-drift`, the same perturbation `test_production_refuses_identity_outside_authenticated_set…` uses). Honest gate → `consumer_identity_undeclared`.
3. Forge the pack so `A/decode` *declares* the drifted identity: overwrite `config_inventory[0]`'s config bytes with the drifted config; update that row's sha in the receipt AND in the plan-tree projection; recompute `config_set_sha256` from the re-derived set and write it to both the receipt unit and the projection unit; re-render the U11 receipt with `identity_pins._render_json` (canonical); rewrite its `.sha256` sidecar; update `plan_tree.projection_receipt.sha256`; update the U8 freeze receipt's `u11-freeze-projection` evidence sha; re-render the freeze receipt + sidecar; update `plan_tree.arm_readiness.freeze_receipt.sha256`; `write_identity_tree` (plan_tree + plan_tree.sha256); **commit**.
4. What stays: lineage `pack_root` and `pack_sha256` (honest). What differs: the committed tree digest.

**Run A — check present (production source):**
```
=== RUN A: check PRESENT ===
PACK-TREE CHECK: PRESENT (production source)
[control] honest pack, honest consumers      floor_request_for_evidence=REQUEST production status='refused' reasons=('cell_missing', 'consumer_term_unknown')
[drift]   honest pack, DRIFTED consumer0     floor_request_for_evidence=None    production status='refused' reasons=('consumer_identity_undeclared',)
lineage pack_sha256 (honest) = 8ecb3cd21e7a8a951d30d10563326b31cd2fb36f2c92a08a29f743a67a9d5822
committed tree after forgery = 796c6ee479e1beda5cba8312697bedd78cd4a2d64bdd1e7ec43c8cb4f8050c3f
tree differs from lineage    = True
drifted identity in forged declared set = True
[FORGERY] forged pack, DRIFTED consumer0     floor_request_for_evidence=None    production status='refused' reasons=('consumer_identity_set_unauthenticated',)
[FORGERY/exact-cell] forged pack, honest lineage, drifted consumer+cell -> status='refused' reasons=('consumer_identity_set_unauthenticated',)
```
**Run B — check replaced by `if False:`:**
```
=== RUN B: check DISABLED ===
PACK-TREE CHECK: DISABLED (if False:) via exec into module namespace
[FORGERY] forged pack, DRIFTED consumer0     floor_request_for_evidence=REQUEST production status='refused' reasons=('cell_missing', 'consumer_term_unknown')
[FORGERY/exact-cell] forged pack, honest lineage, drifted consumer+cell -> status='exact' reasons=()
CHECKOUT-CLEAN
```
(The transport-case `cell_missing`/`consumer_term_unknown` in the control row is the fixture's known shape — `_generated_transport_case` is built for the `floor_request_for_evidence` seam, which is the seam the existing stale-bytes test asserts on; the gate's verdict is the `REQUEST`/`None` column. The exact-cell seam gives the unambiguous end-to-end bite: **`exact` with empty reasons** for a forged declaration.)

That is the bite: with the check, the forgery is refused with the round-1b label; without it, an identity the freeze never declared resolves a floor as `exact`. The round-2 test is exactly steps 1–4 with two assertions (`floor_request_for_evidence(*case) is None` and `resolution.reason_codes == ("consumer_identity_set_unauthenticated",)`), and — to prove it is defect-shaped rather than another sidecar catch — a control assertion that the forged pack with a *re-stamped* lineage (`pack_sha256 = forged tree`) is accepted. Note one trap I hit building it: `_generated_exact_case` re-reads the config from the (now forged) inventory, so the drift tag must not be applied twice.

---

## Q2 — F-N residual and terra F2

**Rule applied:** the writing standard's first-use test — a term of art is built or glossed at its first *use as a term*, or deleted. An identifier string is a fixed literal, not a use of the term; a reader does not need to know what "U11" *means* to copy `D117-U11-IDPIN-PROJECTION` into a field whose only requirement is byte equality (`validate_identity_pin_projection` line 502 compares it to a constant).

**luna's F-N residual (`U11` inside `D117-U11-IDPIN-PROJECTION` at line 184/222/650):** NOT a first-use violation. The token appears only inside a quoted fixed value; the doc says nothing about it there and the reader is asked to do nothing with it. Adding a gloss at line 184 ("…where U11 is the work-unit label; see Analysis-gate definitions") is harmless and cheap, but it is a nit, not a should-fix, and I would not count a round on it. **No fix required; optional one-clause cross-reference.**

**terra F2 (lines 602–613, round 1b's new paragraph):** this is **new text with a new defect, not a second round on F-N**. F-N was "ordering of definitions before the analysis-gate prose" and round 1 cured it with the definitions block (563–579), which precedes the paragraph. terra's complaint is different: the *new* paragraph coins "U11 receipt" (a composite the definitions block never forms — it defines U11 as a *subsystem and evidence row*, and separately "frozen identity receipt" at line 588) and "frozen declaration" (never defined anywhere; grep shows its only occurrence is line 613), and it leans on "the authentication sequence above". Under the standard: "U11 receipt" fails (a) and (b) — the reader cannot map it to a file; "frozen declaration" fails outright. Same *class* of defect as F-N (first-use), different text, different terms, written by a different round — the rule-11 trigger reads "same defect", and I do not stretch it to "same defect class on adjacent text". **Classification: first-round should-fix on round 1b's text.** (But see Q3: the fact that two rounds in a row produced first-use defects on the same section IS the standing escalation signature and should be named in the round-2 brief as a structural instruction, not just another item.)

**What closes each:**
- F-N residual: nothing required; optional gloss.
- F2: a standalone rewrite of 602–613 that a reader can rebuild both labels from without "above". Concretely: replace "U11 receipt" with "the frozen identity receipt (the file `projection_receipt.path` names)"; replace "frozen declaration" with "an authenticated frozen member-identity set" or delete the clause; replace "cannot finish the authentication sequence above" with an enumerated list of the exits in gate order (lineage rows → pack tree digest vs. `pack_sha256` → plan tree → projection state → U8 freeze receipt bytes+sidecar → its `u11-freeze-projection` row equals the plan's `projection_receipt` → frozen identity receipt bytes+sidecar → one unit for the family → config bytes → re-derived set digest). The paragraph already half-lists these; make the list *the* definition instead of an "example". Gloss in place is insufficient for "authentication sequence above"; reorder is irrelevant.

---

## Q3 — composition of round 2

All five items may land as ONE fix round with one delta re-audit by a different model. None requires a ruling first: the semantics of every item are already ruled or code-fixed — the F-B check exists (semantics = "committed tree equals lineage digest"), the two labels exist and their mapping to `floor_transport_inapplicable` is a pin of *current* behaviour (terra F1), F-G and F-COUPLING are test-shape items. I would refuse to let the magistrate brief only one thing without a ruled semantics: **terra F1's mapping pin must pin the mapping the magistrate actually wants**, not whatever the default branch does today. If nobody has ruled that `consumer_identity_set_unauthenticated` → `floor_transport_inapplicable` is the intended engine-reason (rather than, say, a distinct reason), a pin of the default-branch behaviour freezes an accident. That is a one-line ruling ("the two labels map to X"), not a cold-gate matter, but it must be stated in the brief.

Two brief-level constraints for round 2, both from this seat's evidence: (i) the F-B test must assert the *lineage-vs-tree* refusal with a re-stamped-lineage control, per Q1, and the brief must name the fixture steps — otherwise round 2 risks another sidecar-caught "tamper" test; (ii) the standing-escalation signature applies to prose: two consecutive rounds wrote first-use defects into §Analysis consumption, so round 2's prose item goes to a *writer* seat under the writing standard with the first-use test run mechanically, and the delta re-audit must check pedagogy as its own dimension (the standard says fidelity review does not catch these).

---

## Q4 — what a consumer loses until round 2 lands

Nothing, mechanically. The production check is present at `inputs.py:3898` and Run A shows it refusing a fully self-consistent forgery whose only tell is the tree/lineage digest mismatch. A forger who can rewrite the committed pack cannot make the gate return a set the freeze never declared; the only forgeries that pass are those whose committed tree equals the digest the launch stamped on the bundle — i.e. the honest pack. What is lost is *durability*: any future refactor of the gate that drops or short-circuits line 3898 passes the whole suite (Run B, 10/10 OK) and silently reopens the Opus-204 F1 hole (forged declaration → `exact` floor). The exposure is to the next edit, not to today's output.

---

## Findings against the packet (charter §6)

1. **Presupposes the forgery shape without having built it (should-fix in the packet, not the code).** The packet asserts the counterfactual "remove the digest comparison" is defect-shaped and asks the seat to confirm; it correctly does not claim to have built it. Fine — but it *transcribes* the class-passes-with-`if False:` evidence from a run at `3ac6cffb` (6 tests) while the checkout it names is `7c87fa71`/`b9b55e90` (10 tests). The claim generalises (verified: 10/10 pass with the check disabled), but the packet should have re-run at the head it hands the seats.
2. **Line citations are accurate** (3896–3899; test 751–766; definitions 565–579; terra quote 602–609). The terra quote is elided with "…" mid-sentence; the elision drops nothing load-bearing. Minor.
3. **Omits the seam distinction.** The packet does not say that `_generated_transport_case` cannot reach `exact`/`transported` through `_production_floor_resolution` (control row is `cell_missing`), so a round-2 author copying the label tests' seam for the transport fixture will get a non-diagnostic refusal. The brief needs to name the seam per fixture (transport → `floor_request_for_evidence`; exact-cell → `_production_floor_resolution`). Should-fix in the brief.
4. **Q2 framing slightly loads the answer** ("or is an identifier not a use of the term?") — it names the seat's likely out. Acceptable under §6 since the seat is asked to state its rule; noting it.
5. **The "Other open findings" section is accurate to what it lists** but does not surface that F1's mapping pin needs a stated intended mapping (Q3 above). Omission, should-fix in the brief.
6. No transcribed-as-pasted evidence found; the pasted block reads as genuine command output.

---

## Verdict

- **Q1:** Second fix round on F-B — rule-11 trigger met; round 1 claimed a closure whose named regression does not exercise the cure. Residual severity **should-fix** (production check present and verified biting). The defect-shaped fixture **is buildable** from `_generated_frozen_gate_pack` (14-step self-consistent re-render + commit, honest lineage retained); executed: check present → `consumer_identity_set_unauthenticated`; check disabled → `exact`, reasons `()`. Rule: a closure counts only with a test that fails on removal of the cure; a mis-reported closure does not reset the round count.
- **Q2:** luna's F-N residual is **not a violation** — a fixed identifier literal is not a use of the term; optional gloss only. terra F2 is a **new first-round should-fix on round 1b's text**, not a second round on F-N; cure is a standalone rewrite of 602–613 enumerating the exits in gate order, defining "frozen identity receipt" by file and deleting "frozen declaration". Rule: first-use test applies to terms doing technical work, not to opaque literals; "same defect" in rule 11 means the same defect, not the same defect class on new text.
- **Q3:** One fix round is permitted for all five items plus prose, with a different-model delta re-audit. Precondition: the brief states the intended engine-reason mapping for terra F1, names the F-B fixture steps and the re-stamped-lineage control, names the seam per fixture, and routes the prose to a writer seat with a pedagogy lens in the re-audit (two consecutive first-use defects on one section is the standing-escalation signature).
- **Q4:** No present loss — the check refuses the forgery; the exposure is that any future edit dropping line 3898 passes the suite and reopens forged-declaration → `exact` floor.

Scratch artifacts (outside all checkouts): `<scratchpad>/tmp-coldF/forgery_probe.py`, `run_class_disabled.py`.
