# Synthesis — D-079 issuance cold gate (2026-08-06, Fable magistrate)

## Why a cold gate

Executing the D-079 acceptance-artifact issuance is an IRREVERSIBLE
write to the claim-authentication anchor (the calibration ledger + the
acceptance artifact all future floor-mint claims authenticate against).
Rule 11 makes any irreversible action a mandatory cold-eyes trigger.
Ed pre-authorized the issuance DECISION overnight; the magistrate still
owns getting the assembled artifact CORRECT. Two distinct lenses on a
mechanically-assembled packet: a fresh Fable instance (correctness) +
a Sol xhigh contract-lens (conformance), for cross-model diversity.

## Split verdict → synthesis (lead decides, not majority vote)

- **Fable cold instance: PROCEED.** Independently reproduced the head
  `08456d50…@76`, verified the B1 systematic-invalid ruling against
  D-102 primary evidence (member `491995f3`'s exact bound appears
  verbatim in D-102 as a systematic failure; the corpus-ceiling valid
  member `901c5c13` sits at 0.03355875667989999, just under the
  0.033558756679900 screen — no missed or over-flagged call), and
  found the iCloud custody provenance sound (integrity rests on the
  committed hash chain, not the custody pointer). Its lens was the
  ledger/head/disposition — all correct.
- **Sol contract-lens: HOLD (two blockers).** Its lens was the plan vs
  the LANDED CONSUMER CODE, and it found the issuance plan incomplete:
  - **F1 (blocker):** `joulewise/calibration_bracketing.py` only
    accepts the genesis unissued fixture (`artifact_role=
    schema_fixture_unissued`, byte-pinned, production evaluation
    unconditionally refuses anything else). There is NO consumer path
    that authenticates an ISSUED acceptance artifact against a ledger
    cutoff. Flipping the JSON to `issued` makes it UNLOADABLE.
  - **F2 (blocker):** `derivation_sha256` is defined over the ENTIRE
    artifact core, not just the n=19 table. Flipping `artifact_role`
    alone changes it `3cece3b2…` → `a0b98acf…` (lead-reproduced).
    Keeping the old digest yields an INVALID artifact; the packet's
    (and the verification report's) assumption "n=19 preserved ⇒
    digest preserved" is FALSE.
  - **F3 (should-fix):** the physical ledger target is
    `runs/calibration_observation_ledger.jsonl` (CLI + writer default),
    not the `configs/calibration/...` path the packet named.
  - **F4:** confirms all 38 custody locators are iCloud paths (packet
    said 22) — non-blocking, matches the Fable advisory.

**MAGISTRATE RULING: HOLD UPHELD.** The two lenses do not conflict —
Fable verified the ledger is RIGHT; Sol verified the issuance PLAN is
INCOMPLETE. Both are true. Executing the packet as written would have
written the irreversible ledger AND left the acceptance artifact in a
state production code refuses (worse than not issuing). The cold gate
did exactly its job. No dissent recorded (the magistrate upholds the
HOLD, does not overrule it).

## Corrected issuance scope (issuance is IMPLEMENTATION, not an edit)

D-079 issuance now requires, IN ORDER, each gated:

1. **Consumer-side implementation (design-bearing, full gauntlet):**
   an ISSUED-acceptance-artifact loader in `calibration_bracketing.py`
   that (a) accepts `artifact_role=issued`, (b) authenticates the
   artifact's cutoff `(sequence, head_digest)` against the committed
   ledger head pin and the import-marked prefix, (c) verifies
   `prior_observation_set` equals the ledger's import-marked cutoff
   prefix, (d) retires the fixture byte-pin + the unconditional
   unissued refuse, (e) sets `claim_eligible` per the issued state.
2. **The issued artifact BUILT correctly:** `derivation_sha256`
   recomputed under the whole-core definition; `prior_observation_set`
   = all 38 content-distinct members with epoch + disposition (30/2/6);
   cutoff = `(76, 08456d50…)`; role/status/claim_eligible/
   `production_issuance_blocked` flipped. Ideally the bootstrap or a
   sibling tool EMITS this artifact deterministically for review,
   rather than a hand-edit.
3. **Re-cold-review** of the EXACT final artifact bytes + new canonical
   digest + new checked-in byte pin + a production-path test over the
   real 76-receipt prefix (Sol residual-risk requirement).
4. **THEN** the irreversible `--execute` (→
   `runs/calibration_observation_ledger.jsonl`) + head-pin commit.
5. **THEN** D-116, recording: all-38 iCloud custody; R2.8's "six
   further" superseded to "eight further" under the 30-valid ruling
   (both `trigger_now=false`); the split-verdict cold gate.

D-110(c) (evidence_root_id widening) is ON main (PR #105,
`detection_floor.py` pinset-derived path) — Sol's "not on main" note
was mistaken; that validator is separate from the acceptance loader.
The re-mint remains blocked on issuance COMPLETING, not on (c).
