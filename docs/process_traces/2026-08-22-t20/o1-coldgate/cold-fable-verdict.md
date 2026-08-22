# O-1 COLD-GATE VERDICT — cold Fable instance, 2026-08-22

Seat: cold Fable adjudicator (rule-11 topology; no loop context). Repo verified
read-only at main 1ba04a8. Every packet quote relied on below was checked
against primary sources: `tests/test_receipt_histsem.py` (byte-pin literal at
:31, pin test at :54-60, corpus counts at :92-103),
`scripts/verify_receipt_histsem.py` (no `--update` lane, confirmed),
`joulewise/arm_readiness.py` (:2712-2714 single hardcoded pinset path;
:3449-3508 HEAD-anchored gate reads exactly that one path; :2913-3011 row
schema), `docs/contracts/receipt_histsem_verifier.md`, and
`docs/process_traces/2026-08-20-go-session/rh-ruling.md` item 8 (verbatim
match at :65-78).

## VERDICT

**Option 1, precisely bounded: amend the ruled changed-set contract 112 → 113,
authorizing exactly `tests/test_receipt_histsem.py` as the 113th
pack-and-ordinal-exact path, with a one-time reviewed update of the byte-pin
literal AND the three co-traveling count assertions, landing in the SAME
post-mint commit as the three `_v4` pinset rows.** The contract-doc wording
change ("112th entry" → "112th and 113th entries") lands BEFORE candidate
derivation, keeping the post-derivation changed set at exactly 113.

Option 2 is REJECTED as cryptographically impossible under the repo's trust
model, and additionally as strictly weakening tamper-evidence for the three
new rows. Option 3 is REJECTED without further analysis; each waiver
contradicts a binding RH obligation.

## Why-chain

1. **Option 2's premise is unsatisfiable, not merely risky.** The packet asks
   for a construction whose "already-pinned bytes authenticate append-only
   `_v4` rows without the test file changing at transaction time." The `_v4`
   rows carry `head_commit`, `freeze_receipt.sha256`, per-receipt digests, and
   pack tree SHAs (row schema, arm_readiness.py:2940-3011) — bytes that come
   into existence only during the transaction. The repo's trust model is
   keyless repo-trust: the contract's own Truth-boundary section declares this
   mechanism DETECTABILITY, not integrity, with no signature material
   anywhere. Without a key, bytes committed before derivation cannot
   authenticate bytes created during derivation — full stop. Every candidate
   construction decomposes the same way:
   - *Subtree pin over the nine legacy rows:* the three new rows enter the
     gate's governing set with NO test-side authentication at transaction
     time, and — worse, permanently — the whole-file pin's protection against
     row ADDITION (a rogue governance row, or post-mint mutation of a `_v4`
     row) is forfeited for good. The freshest, claim-bearing rows get the
     weakest control. This directly answers the question posed to this seat:
     yes, option 2 weakens tamper-evidence for the three new rows, and the
     addition-detection loss also degrades the file as a whole.
   - *Chained seal (pin' = H(pin ‖ new_rows)):* the chain head is a new
     expected value that depends on the new rows' bytes; committing it IS a
     post-derivation test/authenticator change — the 113th path again, just
     renamed.
   - *New versioned pinset file (v2/`_v4` family):* leaves the v1 pin intact
     but requires a pre-derivation code delta (the library reads ONE hardcoded
     path, :2712, :3467-3484 — no multi-file lane), and the new file's bytes
     are still unknowable pre-derivation, so the new rows are unpinned at
     transaction time and their pin becomes a post-transaction retrofit — the
     exact "expected value nobody supplied" C1 shape RH-8 exists to forbid.
   There is no fourth construction; the packet missed no viable variant.

2. **Option 2 doesn't even deliver its headline property.** The test file also
   asserts `len(packs) == 9`, `sum(receipt_count) == 99` (:59-60) and corpus
   counts 9/99/108 (:94-103). Any growth of the governed set changes those
   assertions regardless of pin construction. "The test file doesn't change at
   transaction time" was never on offer.

3. **Option 1 is what the histsem contract itself prescribes.** The contract's
   operative sentence is: "There is no update, regenerate, repair, or
   auto-reseal lane; **a new governed value requires an explicit versioned
   change**." Read precisely, the byte-pin forbids an AUTOMATED lane (no
   `--update` flag — asserted at :57, preserved by this ruling), not growth
   itself; growth is routed through exactly one shape: a deliberate,
   reviewed, CI-visible commit that changes pinset and pin together. Option 1
   IS that lane. The byte-pin's protective intent — no code path quietly
   rewrites the pinset; any change trips CI unless co-reviewed — survives
   intact: between commits the pin binds fully, and the in-transaction actor
   was never inside the threat model (registered limitation, D-139 A1, Truth
   boundary).

4. **The 112 contract's protective intent survives the amendment.** Its
   purpose is exhaustive PRE-declaration of the post-derivation changed set.
   Adding one exact path NOW, before the transaction, by cold-gate ruling,
   preserves exhaustiveness completely; the candidate contract still refuses
   on missing/extra/unused (RH-8's own clause, re-proven by S-0's clone
   proof).

5. **Precedent risk inverts.** The 112 number is itself a COLD-PASS AMENDMENT:
   the 111 enumeration missed a co-traveling path (the pinset), and the cold
   pass repaired it by adding the exact path (RH-8, rh-ruling.md:70-73). O-1
   is the identical defect one level up — the enumeration missed that the
   pinset's own byte-pin co-travels with the pinset. Amending 112 → 113
   through this cold gate is the established, cold-ratified repair shape
   executing a second time; inventing a pre-transaction authentication
   redesign to avoid touching a ruled number would be the actual precedent
   novelty, at high implementation risk against a landed, cold-ratified,
   normatively-tested verifier days before the critical transaction.

## Obligations: preserved / amended

- **HISTSEM byte-pin (preserved, exercised as designed):** the literal SHA
  assertion over the entire pinset remains normative at every commit; the
  no-update-lane assertion (`assertNotIn("--update", ...)`) is untouched; the
  one-time update is the contract's "explicit versioned change."
- **RH-8 row-minting mandate (preserved):** three rows mint after
  freeze-0004 ×3, before Ed's exact-byte step-6, checked against the
  confirmation table; no retrofit.
- **r5 V-1 changed-set contract (explicitly amended).** Amendment sentence,
  verbatim for the record:

  > O-1 COLD-PASS AMENDMENT TO RH-8 / r5 V-1 (ruled by the O-1 cold gate,
  > 2026-08-22): the allowlist value goes 112 → 113, adding the exact path
  > `tests/test_receipt_histsem.py` (pack-and-ordinal-exact per V-1(v); never
  > a glob) — that file's pinset byte-pin literal and its pack-count,
  > receipt-count, and fact-count assertions co-travel with any pinset append
  > by construction, and their one-time reviewed update lands in the same
  > post-mint commit as the three `_v4` pinset rows, after freeze-0004 ×3 and
  > before Ed's exact-byte step-6. This is the histsem contract's "explicit
  > versioned change" lane, not an update lane: `scripts/verify_receipt_histsem.py`
  > gains no `--update` flag and the no-update-lane assertion is unchanged. A
  > later family (`_v5`) repeats this shape with its own exact entries, never
  > a glob, and re-enumerates its own count — 113 is per-transaction, not a
  > constant.

- **Contract doc (pre-derivation prose amendment, outside the changed set),**
  sentence for `docs/contracts/receipt_histsem_verifier.md` §`_v4` transaction
  sequencing:

  > The pinset path and `tests/test_receipt_histsem.py` are the
  > pack-and-ordinal-exact 112th and 113th entries in the whole-repository
  > changed-set allowlist: growing the governed set is the explicit versioned
  > change this contract requires, and it co-updates the byte-pin literal and
  > count assertions in the same reviewed post-mint commit — the verifier
  > itself still has no update lane.

## Implementation conditions (binding)

1. **Pre-derivation (outside the 113):** the contract-doc amendment above and
   the V-1 generator-script extension to emit the 113th entry land as reviewed
   changes BEFORE candidate derivation (same status as the U11-before-
   derivation precondition of the value).
2. **Atomicity:** pinset append + full test update
   (SHA literal; 9→12 packs; 99→99+n receipts, n from the confirmation table;
   corpus fact-count from the actual receipts) in ONE commit; the full suite
   is green at that commit. Between-commit states where the pin test fails
   must not exist on the transaction branch.
3. **Append-only proof at review (a reviewer who is NOT the implementing
   session — magistrate or a designated refuter):** mechanically verify
   (a) `git show <pre-commit>:configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json`
   parses to packs identical to `packs[0:9]` of the new file, byte-identical
   under `render_json`; (b) `packs[9:12]` match the transaction confirmation
   table row-for-row with independently recomputed digests; (c) the new test
   literal equals an independently recomputed SHA-256 of the new pinset bytes.
4. **Changed-set proof:** the 113-entry candidate contract still refuses on
   missing/extra/unused; S-0's clone proof extends per RH-8 (pinset present →
   arms cross; absent → refusal).
5. **Tamper-probe class (V-1(vi)):** the new path class
   `tests/test_receipt_histsem.py` gets its probe — tamper the literal in a
   clone and show CI fails against the true pinset; its authenticators of
   record are the test run itself plus the changed-set gate. Any probe
   failure reopens the mechanism question to the derived manifest (the
   standing tripwire, unchanged).
6. **Schema version:** the pinset `schema_version`
   (`joulewise.receipt_histsem_pinset.v1`) is unchanged by an append-only row
   addition; if the `_v4` rows need any schema deviation, that is a NEW
   question and returns to a cold gate — this ruling does not cover it.

## Dissent-worthy doubts (recorded, non-blocking)

- **Momentary self-attestation:** in the amending commit, the new pin attests
  bytes minted moments earlier by the same actor. This is identical to the v1
  pin's own minting (rh-impl-report trace) and inside the registered D-139 A1
  residual; the pin's value is downstream detectability, which resumes at the
  next commit boundary. Recorded so nobody later claims the pin covered the
  minting actor.
- **Recurrence:** every future governed-set growth repeats this amendment
  shape. The amendment text makes the count explicitly per-transaction to
  pre-empt treating 113 as ratified scripture next family.
- **Standing dissent preserved:** V-1(vii)'s derived, digest-authenticated
  manifest remains the recorded alternative; nothing here disturbs it, and the
  V-1(vi) tripwire can still route there.

---

# Round 2 — reply to the contract refutation

I re-verified the refuter's load-bearing citations before replying:
`_r1_changed_paths` at arm_readiness.py:3916-3964 and the subtraction
application (P1/P2 confirmed — the gate is set subtraction over
`derivation_commit..current_head`, both bounds hard); RH-2's K7-bootstrap
sentence (rh-ruling.md:22-26, verbatim); r4-3
(v4-plan-ruling-r4draft.md:46-61, verbatim); the runsheet failure semantics
(s0-runsheet.md:725, :830, verbatim); the freeze/arm gate entries
(arm_readiness.py:6255-6268, :6943-6961). All check out.

**Position: I CONCEDE Option 1 and adopt O-1-D, with the binding conditions
in §R2.4.** My Round-1 impossibility theorem stands (pre-committed bytes
cannot authenticate post-derivation bytes without a key — the refuter
concedes it and builds O-1-D around it), but two inferences I drew from it
were wrong: I treated the changed-set contract as a standing repository
invariant instead of a property of one derivation→arm window (the refuter's
§1.2 — r4-3's post-window lane exists and I missed it), and I never examined
the append-to-v1 premise, which no ruled sentence states (F3 — "the pinset's
exact path" does not say v1). This is a genuine refutation, not a
consistency contest.

## R2.1 — The coherent-substitution attack (Q1)

**Yes, the attack succeeds mechanically.** Walked at the code: in-window,
under Option 1, a commit altering the v1 pinset rows plus `PINSET_SHA256`
(and counts) to match yields changed set `{pinset, test}` — both subtracted
by :4041-4049's set subtraction; the rewritten test passes; K5/K12 verify
packs against the tampered rows (coherent → pass); K7 checks delta shape,
not row truth; neither path has an R1 manifest binding or a semantic-replay
authenticator (V-1(iv) enumerates the replay-covered four; these are not
among them); the S-0 exact checker compares the changed-path SET, not
content. No mechanical gate refuses. My Round-1 conditions 2-3 (one-commit
atomicity, independent review) are procedural custody, exactly as the
coordinator's framing suspects — an in-window committer is not bound by
them.

**Does D-139 A1 / the truth boundary make that acceptable? Only for the
byte-pin verifier — not for the allowlist mechanism.** The truth boundary
registers the in-process actor as the VERIFIER's residual. But the static
allowlist exists on a separately ratified basis: V-1(iii), "Sol conceded
back to the static list CONDITIONAL on independent authentication of all
allowed bytes" — an anti-substitution condition by its own words. A
test-source class has no manifest, no sidecar, no replay; and V-1(vi)'s own
fallback — digest-conditional subtraction — is unavailable for it, by my own
Round-1 theorem: the test's post-derivation bytes have no pre-derivation
digest source. So the class is unauthenticatable, and the runsheet's ruled
consequence (s0-runsheet.md:830, verified verbatim) is mechanism failure:
"The response is not 'fix a test expectation': derive an authenticated
manifest, remove every unauthenticated subtraction, rerun all of S-0."
Option 1's true cost was never 112→113; it was reopening V-1 to the derived
manifest. My Round-1 condition 5 ("authenticator = the test run itself plus
the changed-set gate") was circular — the tampered test authenticating
itself — and is withdrawn.

**Is "option 3 with better paperwork" right?** Overstated by one layer, and
I keep the distinction for the record: detectability survives Option 1
(forward-history visibility, Ed's step-6 table), so it is not a waiver of
the byte pin's detectability function. But at the mechanism layer the
refuter is correct, and the sharper differential is the NINE legacy rows:
Option 1 must allowlist the v1 path, so for the whole window the
already-pinned rows lose changed-set protection AND their pin moves; under
O-1-D the v1 path is NOT in the allowlist — any in-window touch of v1 is
mechanically refused at :4041-4049 — and the v1 literal never moves. Strict
mechanical dominance. Concession recorded. (Also conceded from F1: my
Round-1 conditions caught the three count assertions but missed the
`test_differential_self_test_all_nine_packs` method name and the fact that
in-window corpus runs pass only over the runsheet's locally forged
`origin/main` — both real, both undisclosed in my Round 1.)

## R2.2 — O-1-D adjudicated on its actual costs (Q2)

**(a) The fixation gap is longer than the refuter says, and still
acceptable — because every phase of it has a named control.** r4-3
(verified verbatim) requires "atomic publication → published-head suite with
zero further ordinary commits, then shakedown → windows with the checkout
pinned," with a commit-freeze on the measurement checkout's main from
attestation through window close. So the fixation commit cannot land "after
the final arm" as O-1-D §5.1 states — it must wait for WINDOW CLOSE. The
corrected gap, phase by phase:
  - mint → step-6: K7 bootstrap + the scripted confirmation-table check —
    mechanical, in-transaction;
  - step-6 → publication: Ed's exact-byte table — the same hand-published
    control the truth boundary already names as its detection anchor;
  - publication → window close: the r4-3 commit-freeze — any ordinary commit
    to the measurement checkout's main DISARMS T-0 (`exact_match=false`), a
    mechanical control that covers precisely the highest-value period;
  - window close → fixation: bounded by condition 3 below (first commit).
  Additionally, condition 2 below closes the in-window substitution residual
  at proof time: the successor's subtraction becomes DIGEST-CONDITIONAL —
  V-1(vi)'s own fallback, which WORKS here (unlike for Option 1's test file)
  because a digest source exists: the confirmation-table digest, derived at
  mint and confirmed at step-6. Registered as a named residual under the
  truth boundary; acceptable.

**(b) Absent-successor semantics — the walk, and the rule that survives
it.** `generate_freeze_receipt` gates the PREDECESSOR (:6255-6258,
predecessor mode; `_v4` packs are generation ≥ 2, :6274-6278);
`generate_arm_receipt` gates the pack being armed (:6950-6952). Through the
states:
  - **Freeze-0004 ×3 (successor never committed):** the gated pack is the
    `_v3` predecessor, governed by v1 rows; chain union = v1 alone;
    verifies. Refuse-on-absent MUST NOT fire here — otherwise deadlock (rows
    mint only after freeze ×3, freeze refuses without rows).
  - **Pinset commit (minted-unpinned):** successor at HEAD; union =
    v1 ∪ successor with cross-member identity uniqueness enforced
    (duplicates → `histsem_pinset_invalid`); subsequent gates verify `_v4`
    packs against successor rows (K5/K12 + K7 bootstrap).
  - **Post-window (fixated):** mutation refuses via row checks + red pin;
    deletion must refuse.
  The rule satisfying all three: **an enumerated chain member absent at HEAD
  refuses IFF it exists in HEAD's history (`git rev-list HEAD -- <path>`
  nonempty); never-yet-committed → absence-of-governance return.** Shallow
  history during that probe is already owned by `histsem_history_shallow`.
  **Answer to the refuter's item 4: the tightening is BLESSED — and it is
  not discretionary, it is entailed by RH-8 itself:** the clone proof
  demands "absent → the pinset-absent refusal"; in the S-0 clone the
  successor IS committed, so a committed deletion must refuse — plain
  absence-of-governance semantics would return ordinary readiness and
  violate RH-8's stated expectation. One hole recorded, charged to no
  option: a `_v4` arm attempted pre-mint would cross ungoverned (membership
  miss) — inherent to membership-based engagement under EVERY option
  including v1-append, and excluded procedurally by r4-3's order (arms only
  post-publication).

**(c) Chain-read vs the single-hardcoded-path finding: compatible — my
finding is the REASON the delta is required, not an argument against it.**
The delta: :2712's constant becomes an ordered enumerated tuple;
:3467-3484's gate loops members (ls-tree/show per member, union, uniqueness
across the union, plus the rev-list rule above); `_load_histsem_pinset`
mirrors it for worktree/CLI reads; the `--pinset` explicit-override
semantics used by the test fixtures are preserved; per-file `schema_version`
stays `joulewise.receipt_histsem_pinset.v1`. Modest, pre-derivation,
regression-tested. I withdraw my Round-1 "C1 retrofit" objection to
deferred fixation: RH-8's mischief is "an expected value nobody supplied,"
and under O-1-D the expected value is supplied three times before the pin
lands (confirmation table at mint, K7 bootstrap, Ed's step-6 table). I
concur with the refuter's item-3 reading: the retrofit prohibition binds
the ROWS, not their CI fixation.

## R2.3 — O-1-E (Q3)

**Dead, and r4-3 is the executioner.** At the published head the pinset
carries 12 rows while the untouched test asserts 9/99/108 plus the old SHA:
the "published-head suite" step of r4-3 is RED — the transaction cannot
complete its own ruled order. And the deferred test fix cannot land as "the
next commit": the commit-freeze runs from attestation through window close,
so the red normative state would span the entire window, not one commit.
O-1-E additionally allowlists the v1 path (legacy rows lose in-window
changed-set protection), makes the nine rows' pin stale in-window, and
inherits the forged-`origin/main` dependency. Rejected on all four.

## R2.4 — Final position and conditions

**VERDICT (revised): O-1-D — versioned-successor pinset with post-window
fixation — replacing my Round-1 Option 1.** Binding conditions:

1. **Pre-derivation reviewed candidate** carries: the contract amendment
   (governed pinset → closed, ordered, code-enumerated chain), the
   chain-read code delta with regression tests, the
   refuse-if-absent-but-in-history rule of R2.2(b), and the allowlist at
   **112** with the successor's exact path as the 112th entry (no ruled
   number amended).
2. **Digest-conditional subtraction for the successor class:** S-0 §4(d)'s
   exact check verifies the successor's committed bytes against the
   confirmation-table digest carried in transaction custody. V-1(vi) is
   exercised, not waived; the per-class probe list gains the successor
   class with this as its named authenticator.
3. **Fixation:** the FIRST commit after window close; adds the successor's
   SHA literal and row/receipt/fact counts as NEW assertions, touching no
   v1 assertion; reviewer (not the implementing session) independently
   recomputes the SHA and matches it against Ed's step-6 table.
4. **Residual registration:** the mint→fixation gap recorded as a named
   residual under the truth boundary / D-139 A1, with its phase-by-phase
   covering controls (R2.2(a)) listed in the registration.
5. **Family precedent:** `_v5` repeats the shape — its own successor
   artifact, its own exact allowlist entry, fixation post-window; the test
   file never enters any transaction window. Successor artifact naming
   drops the "legacy" misnomer (implementer choice, cold-reviewed).
6. **Out-of-scope defects endorsed for the record:** the refuter's item 5
   (the runsheet reads `freeze_evidence_lifecycle.irrelevant_path_allowlist`
   from a registry key that does not exist at 1ba04a8 — a precondition
   defect the reviewed candidate must author) and item 6 (record that the
   changed-set contract is a window property, not a standing invariant —
   the finding whose absence generated O-1, and my own Round-1 error).

**Dissent-worthy doubt retained:** the refuter's "option 1 ≈ option 3"
equivalence is overstated at the detectability layer (R2.1); if the
magistrate weighs precedent language, Option 1 should be recorded as
"refuted on V-1(iii)/(vi) mechanism grounds," not as a covert waiver of
detectability. My Round-1 file above stands as the record of the position
conceded, per the no-silent-rewrite convention.
