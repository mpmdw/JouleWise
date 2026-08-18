# Phase-2 atomic re-freeze — execution runsheet (staged 2026-08-17)

The ordered execution document for the transaction. Authority: the plan
consult (docs/process_traces/2026-08-16-phase2-plan-consult/) as adopted;
D-138/D-139; the R1 ruling. Every input is gauntleted (delta-ACCEPT) at the
pinned heads below. The executor follows this order; any deviation, failed
verification, or science-facing delta STOPS the transaction (F3
stop-condition → cold review).

**EXECUTION STATUS (2026-08-18 morning):** steps 1-3 and 5 EXECUTED
(twice for 3/5: the D-143 budget correction re-ran the reissue and
re-froze the family — receipts at the measurement checkout, confirmation
head d3aa15f); step 4 (R1 registry install) NEEDS_RULING on Ed-reserved
values (five items, see the morning packet); step 6 = the packet's
exact-byte table awaiting Ed; step 7 pending publication.

**Amended 2026-08-18** — freeze-semantics cold gate (D-140/D-141; record
`docs/process_traces/2026-08-18-freeze-semantics-coldgate/`, composed verdict
`14-composed-verdict.md`). This is a living operational document, so the steps
below are edited in place; what changed and why:

- **Step 1 gains two lanes** — `impl/freeze-numbering-profile-maps`
  (WO-FREEZE-NUMBERING plus the profile-map supersession) and the generator
  stream advanced to `07c12f3` (rounds 6–7: option-(d) freeze-neutral
  wording). Both were authored after this runsheet was staged and both are
  transaction inputs.
- **Step 4's "NO code edits (delta-proven installable)" claim is REMOVED — it
  was false** (verdict holding 7). D-139 A3's chain-monotonic `freeze-0002`
  with predecessor bindings could not be minted by the code as staged (the
  freeze number was hardwired to 1), which is precisely why
  WO-FREEZE-NUMBERING exists; it has landed and been audited, and the registry
  value install proceeds after it.
- **Step 5 gains the freeze-invocation particulars** (`--predecessor-pack-root`
  for each of the three v1 roots; singleton `freeze-0002` per pack; pack bytes
  immutable after mint) and the family-marker construction rule, which is a
  reserved Ed ruling.
- **Step 5 gains the preserve-mode custody note** — the post-freeze default
  `--check` fail-closes on a frozen successor identity (operator trap, verdict
  holding 8).
- **New step 8** carries the M-2(b) informational operator note into the
  successor packet before the arm gate (verdict holding 2, M-2 clause (b)).

## Pinned inputs (all delta-ACCEPTED)

| Lane | Branch | Head |
|---|---|---|
| Estimator payload (budget + flake + calib stage-2) | impl/wo-detect-pulses-budget | e22e658 |
| R1 freeze-evidence lifecycle | impl/r1-freeze-lifecycle | (delta-2 head, origin) |
| D-079 reissue tooling | impl/d079-reissue-prep | e83a61f |
| Successor generators | impl/successor-generator-repairs | 07c12f3 (was 6ddeb7d; rounds 6–7 option-(d) wording, amended 2026-08-18) |
| Freeze numbering + profile-map supersession | impl/freeze-numbering-profile-maps | 9574fda (WO-FREEZE-NUMBERING through delta-10; added 2026-08-18) |
| Docs/paper currency | PR #158 | (merge on green) |

## Order of execution

1. **Merge the lanes to main**, in order: #158 docs → R1 → generators (at
   `07c12f3`) → freeze numbering + profile maps
   (`impl/freeze-numbering-profile-maps`, WO-FREEZE-NUMBERING and the
   profile-map supersession) → D-079 tooling → the estimator payload branch
   (this is the D-138 moment: the canonical suite's acceptance-staleness
   fan-out APPEARS here and is cured at step 3 — the two steps land in one
   push window, never separately CI-gated). Integration tree first if any
   merge conflicts.
2. **Generate the `_v2` successor family** (generators, successor mode,
   preserve OFF for the new IDs only): d117_floor_qwen25_1p5b_v2,
   d117_floor_qwen25_7b_v2, d117_contrast_qwen25_1p5b_vs_7b_v2 — with
   launch_lineage_required, plan.path reconciliation, and self-consistent
   embedded identity (all delta-proven).
3. **Reissue D-079**: run scripts/reissue_calibration_acceptance.py against
   the merged head; require 19/19 + PROCEED (any STOP → halt, cold review);
   strip the candidate marker via the issuance step; update every dependent
   pin + test in the same commit (the tooling's member-delta report is the
   license record).
4. **Install the D-139-approved reserved values** via the R1 registry
   (uniform `_v2` IDs; freeze-0002 chain-monotonic with predecessor
   bindings; existing operational horizons). This step follows
   WO-FREEZE-NUMBERING: chain-monotonic `freeze-0002` was NOT mintable by the
   staged code (freeze number hardwired to 1), so the required
   `arm_readiness.py` work landed and was audited first, and the registry
   value install proceeds after it.
5. **Freeze the family**: fresh receipts (freeze-0002) + R1 content-bound
   evidence, one atomic family transaction, NO grandfathering. Each freeze
   invocation carries `--predecessor-pack-root` naming that pack's v1 sibling
   (the three v1 roots); exactly one `freeze-0002` per pack (singleton); all
   pack bytes are immutable after mint (D-140). The **family marker is
   EXTERNAL to the pack roots** — created only after every pack's bytes are
   final, binding the final pack digests plus the receipt hashes. Its schema,
   path, and activation predicate are an **ED RULING (reserved)**, put to him
   in the confirmation packet at step 6.
   - **Post-freeze custody note (operator trap, cold-gate holding 8):** the
     custody `--check` invocation after freeze must pass explicit preserve
     mode. The default fail-closes on a frozen successor identity ("current
     frozen identity requires preserve mode"), which reads as a defect to an
     operator who does not know to expect it.
6. **ED CONFIRMATION (the irreversible point):** present Ed the exact-byte
   summary (pack tree hashes, receipt hashes, the family marker bytes);
   publish the marker ONLY on his explicit yes. Until then everything is
   revertible.
7. **Post-publication:** canonical suite green at the published head
   (staleness fan-out must be GONE); Phase-3 baseline-manifest SUPERSESSION
   (+pack_digest_algorithm + chain-template note) as its own follow-up —
   NOT inside the publication step (plan F5).
8. **Before the arm gate — M-2(b) informational operator note.** The successor
   packet carries exactly one informational note, in the M-2 clause (b) shape:
   a pack's serialized descriptive status wording is NOT the freeze state; the
   D-134 freeze receipt and its plan-tree pin are the authority, and committed
   pack bytes are never repaired to agree with them (D-140). No arm packet
   cites the 2026-08-13 override — clause (d) bars it, and clause (a)'s
   "overrode a NO-GO reading" premise is stricken. This note retires at
   successor freeze per M-2 clause (c), whose condition the option-(d)
   freeze-aware wording satisfies.

## Then

Phase-3 focused re-audit (adversarial coverage re-enumeration) →
READY-candidate council (fresh cold pairing; requires Ed's qualification
rows from tonight's checklist) → D-139 shakedown runs → claim windows.
