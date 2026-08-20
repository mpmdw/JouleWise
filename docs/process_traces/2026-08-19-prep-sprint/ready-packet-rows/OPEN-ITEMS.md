# OPEN ITEMS — what no repair addressed, and what could not be located

Honesty over completeness-theater. This list exists so no seat has to discover an absence by
accident. "EVIDENCE NOT LOCATED" means the assembler searched the named places and found nothing —
it is a reported fact about the repository at **4597ad4**, not a confession of a weak search. A
seat that locates the missing artifact should say so and strike the item.

Assembled read-only at `impl/r2-s0-mint-resolver` HEAD **4597ad4**; council audit baseline
**8937dec**; 214 commits between them.

---

## A. PROGRAM-LEVEL OPEN ITEMS (source: `rows/ROW-P-PROGRAM.md`)

### A-1. Ten of eleven evidence universes have never been independently re-enumerated
The verdict made independent re-enumeration of **every** universe plus a standing adversarial
coverage attack a condition of the READY-candidate re-audit (`council-verdict.md:18-22`). Only L2's
universe was re-enumerated (`docs/process_traces/2026-08-15-l2-reaudit/`, `0f886d3`). **No artifact
located** for the other ten, or for any coverage attack against this sitting. Coverage error was
conservative under NOT-READY; under READY it is fail-open.

**And the one re-enumeration that exists is already arithmetically stale.** The L2 assembler
verified three ways that the re-audit ran at `fac87d1` — **187 commits behind `4597ad4`** — and
reproduced its method: counting `def test_` across the exact eight modules it enumerated gives
**251 at `fac87d1`** (matching exactly) and **289 at the current head** (+38, +15.1%;
`test_powermetrics_fiducial` 46→75, `test_calibration_bracketing` 42→48, crash matrix 13→15). The
denominator that felled L2's READY has moved again, and nothing re-runs it. See `rows/ROW-L2.md`.

### A-2. The audit-baseline manifest has not been superseded — it pins a dead head and a two-generation-stale pack family
`docs/process/audit-baseline-manifest.json` has exactly one commit in its history (`694442c`). It
still pins `head_commit`/`origin_main` = `ac3fe1d…` and the three **_v1** pack digests, while the
live family is **_v3** under freeze-0003. **None** of the three ruled supersession fields
(`pack_digest_algorithm`, the chain-template coverage note, paths for all bindings) is present.
Charter amendment 12's final-head invalidation is therefore live against every 2026-08-15 lens
result.

### A-2b. The frozen `_v1` packs' committed bytes CHANGED after the freeze — the manifest's digest binding is broken (assembler-verified)
The L1 assembler found the three `_v1` `pack_digests` no longer reproduce at the current head. The
packet assembler verified the cause directly:

```
git diff --stat ac3fe1d..HEAD -- configs/campaigns/d117_floor_qwen25_1p5b_v1/
  .../d117_floor_qwen25_1p5b_v1/generate_configs.py | 648 +++++++++++++++---
  1 file changed, 576 insertions(+), 72 deletions(-)

git diff --stat ac3fe1d..HEAD -- .../d117_floor_qwen25_1p5b_v1/plan_tree.json
  (empty — plan_tree.json is unchanged)
```

All three `_v1` packs show the same single-file change, from commits `0cb9bf2`, `5292cf7`,
`07c12f3`, `3e780a1`, `54f990d`. **The nuance matters and the seat must rule on it:** `plan_tree.json`
— the receipt's `pack_identity` transitive closure under D-140/M-2 — is byte-unchanged, so the
D-134 freeze receipts may still authenticate. But `generate_configs.py` **is inside the committed
pack tree** that `joulewise.arm_readiness.committed_pack_tree_sha256` hashes, which is the digest the
audit-baseline manifest pins. So the audit baseline's integrity binding is broken even though the
freeze receipts' binding may be intact. Verdict Disposition 1 established byte-identical recompute
**at 8937dec**; that is no longer the state.

### A-3. The Phase-3 focused re-audit of L1, L5, L7 was never performed
Ordered at `council-verdict.md:102-104`. **EVIDENCE NOT LOCATED** — searched all 37
`docs/process_traces/` directories, the T9/T10/T12-T13 run reports, `TASK_QUEUE.md`, and
`docs/council_log.md`. The project's own queue rows (Q2–Q4) state the Phase-3 re-audit as a
precondition to this sitting.

### A-4. The charter file was never amended
The ENUMERATING vs READY-CANDIDATE sitting distinction (Opus S12) and the manifest-supersession
conditions (Opus S11) live only in `council-verdict.md`, `docs/council_log.md`, and the kernel/queue
clearance strings. `docs/process/instrument-readiness-audit-charter.md` is unchanged since
`6a7849c` and contains neither "READY-CANDIDATE" nor "ENUMERATING". The clearance line in
`state_kernel.json:9` cites the charter for language the charter does not contain.

### A-5. All three same-signature consequences are unhomed
(a) **No drafting-mechanic checklist document exists** — `grep -rln "drafting-mechanic"` over
`docs/` and `.claude/` hits only `docs/council_log.md` and the 2026-08-15 council directory; the
mechanical rule-11 trigger enumeration over the decision log therefore has no home, and the council
called it "the one consequence that would have caught this cycle's failure prospectively"
(`docs/council_log.md:3748`). (b) No output-keyed refuter-liveness protocol located. (c) No
standing record of the stop-signal timing rule outside the verdict. **A seat should ask whether
this packet itself was finalized without the trigger enumeration the council ordered.**

### A-6. The 23-finding consistency sweep remains formally UNVERIFIED as a body
Only sweep-B4 was adjudicated (REFUTED). Individual fixes landed (`76f6861`, `47d2645`, queue
closures) but **no per-finding verification ledger was located**. Under charter:66-68 an unverified
item is UNVERIFIED, and amendment 11 makes UNVERIFIED independently disqualifying. B7 — the paper's
floor-regime contradiction — is claim-bearing and P1.

### A-7. Four Phase-1 work orders are not closed on the state kernel, the declared sole work-selection authority
At `docs/process/state_kernel.json` (`updated: 2026-08-19`): **WO-CENSUS-SEMANTICS = blocked**
(hard dependency `ED-Q-L9-3`, `state: pending`); **WO-CONSUMPTION-EDGE = partial** (remaining: "the
production freeze (rides Phase 2) + the same-head production-pack L10 replay");
**WO-DETECT-PULSES-BUDGET = partial**; **WO-LAUNCH-BINDING = queued** (remaining: "stage 4
successor flag inside the transaction", note ends "**Launch stays NO-GO**").

### A-8. The kernel's own merge-state narrative is stale
The staged payload at `e22e658` **is** an ancestor of HEAD and is contained in `main`, yet the
kernel still describes it as "MERGE-STAGED for the atomic re-freeze". A stale record in the
declared sole work-selection authority is itself a finding.

### A-9. Phase-2's "ONCE, atomically, LAST among pack-byte changes" is not evidently satisfied
The freeze history since the council shows a `_v2` family frozen, **reverted, re-minted, reverted
again, and re-minted a third time**, followed by a whole `_v3` family and freeze-0003. Opus W2's
warning was that any earlier pack-byte change forces an extra baseline supersession and re-audit
round. Whether the current state satisfies the ordering is unadjudicated.

### A-10. No end-to-end T-0 pass at the exact reviewed head, and no successor arm packet
Opus W8 conditioned the successor arm packet on the T-0 repair passing end-to-end at the exact
reviewed head. **No such pass receipt and no successor arm packet located.**

### A-11. M-2 residues
Composed-verdict item 2d left an explicit **RULING-REQUIRED** row (the contrast pack's
PROPOSED-PENDING-LEAD-RATIFICATION / TODO(lead) / "EMPTY pending U11" markers, "likely
Ed-adjacent"). No ruling located. Also unconfirmed: whether freeze-0003 retired M-2 per its
per-pack retirement mechanism.

### A-12. This sitting's own form preconditions are unmet
No sealed packet custody under `docs/process_traces/<date>-readiness-council/` for the new sitting;
the mechanical extraction script is not yet committed beside the packet (required by the M-2 gate's
non-author-assembly protocol, since the reviewed party is the magistrate); **no fresh rule-11 cold
pairing convened**; `scripts/validate_gate_packet.py` remains unbuilt, so the cold judge's trust
anchor is manual.

### A-13. Queue rows name two pack generations in the same row
`TASK_QUEUE.md` Q2/Q3/Q4 name `_v1` pack ids in the task text and `_v3` ids in the acceptance
evidence. The arm path binds on exact pack identity; both cannot be right.

### A-14. D-149 removed the human margin the 2026-08-15 seats assumed
Under D-149 a standing READY-candidate verdict is **condition (1) of an automatic, unattended T-0
GO**; the other four conditions are machine-evaluated, and the per-window "separate perishable T-0
GO from Ed" fence is **explicitly superseded for no-hands windows**. The charter's separation
survives in letter; the human at the arm does not. No seat has audited the automation itself.

### A-15. Findings retired by risk acceptance rather than repair
D-139 A1 + D-148.6 accept the in-process-adversary family (recorder check-to-grant race, T-0
capture provenance, hostile same-UID injection, forged launch-context) as registered limitations;
WO-RECORDER-GRANT-IDENTITY was **retired without implementation**. This is legitimate risk-appetite
authority, not evidence that the instrument fails closed. The sitting should state explicitly
whether acceptance discharges these rows or merely relabels them.

---

## B. PER-SEAT OPEN ITEMS

Harvested verbatim from each row file's §6. See the row file for context and citations.

<!-- SEAT-OPEN-ITEMS -->
