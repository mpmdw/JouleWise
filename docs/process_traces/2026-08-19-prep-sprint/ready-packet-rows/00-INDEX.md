# 00-INDEX — READY-CANDIDATE COUNCIL PACKET (assembled 2026-08-19)

Mechanically assembled, read-only, at `impl/r2-s0-mint-resolver` HEAD **4597ad4** against the
2026-08-15 council audit baseline **8937dec** (214 commits apart).

**This packet grades nothing.** Every row carries the original finding verbatim, what changed with
exact pointers, a *candidate* disposition, and probes for a skeptical seat. Seats judge.

---

## Reading order

| # | File | What it is | Read when |
|---|---|---|---|
| 1 | `01-SESSION-BRIEF.md` | Charter form requirements; **amendments 11-12 verbatim**; the sitting-type amendment; anti-ritual discipline; what your seat must produce; form preconditions for any READY | **First, always** |
| 2 | `OPEN-ITEMS.md` | Everything no repair addressed + everything the assemblers could not locate | **Second** — read before the rows, so you read the rows knowing what is missing |
| 3 | `rows/ROW-P-PROGRAM.md` | The ten **program-level rows** (P-1…P-10): not-certified-complete, the un-superseded baseline manifest, the M-2 remand, the charter-amendment gap, the same-signature consequences, the sweep body, Phase-2 re-freeze ordering, the 23-row ED gate, this sitting's own form, and Phase-1 completion state per the state kernel | **Third** — several of these condition whether any seat row can aggregate to READY |
| 4 | `rows/ROW-L1.md` | L1 AUTHORITY PLANE (xhigh, gating) — the control plane audited as a component | Then the seat rows, in fleet order |
| 5 | `rows/ROW-L2.md` | L2 CALIBRATION ACQUISITION (xhigh, gating) — **the falsely-clean case**: self-reported READY, refuted; carries a distinct UNVERIFIED on coverage | |
| 6 | `rows/ROW-L3.md` | L3 CAPTURE + TELEMETRY (xhigh, gating) — sampler lifecycle, child supervision, parser, channel census | |
| 7 | `rows/ROW-L4.md` | L4 QUANTITATIVE CLAIM PIPELINE (xhigh, gating) — reducer, verdicts, floors, mint, claim consumption | |
| 8 | `rows/ROW-L5.md` | L5 PACK / READINESS / CUSTODY (xhigh, gating) — frozen bytes, U11, freeze/arm/consume receipts | |
| 9 | `rows/ROW-L6.md` | L6 PRODUCER-CONSUMER SEAM A (high, gating, **contract** lens) | Read L6 and L7 together |
| 10 | `rows/ROW-L7.md` | L7 PRODUCER-CONSUMER SEAM B (high, gating, **execution** lens) | — the pair is deliberately independent |
| 11 | `rows/ROW-L8.md` | L8 OPERATOR + RECOVERY HUMAN FACTORS (xhigh, gating) — **15 findings, 4 sudo ED rows**; the heaviest row | |
| 12 | `rows/ROW-L9.md` | L9 ENVIRONMENTAL CONTROLS CENSUS (high, gating) — hazard register; ED-Q-L9-3 hard-gates WO-CENSUS-SEMANTICS | |
| 13 | `rows/ROW-L10.md` | L10 SACRIFICIAL FULL LIFECYCLE (xhigh, gating) — the after-window path proven before a window is spent | |
| 14 | `rows/ROW-L11.md` | L11 RETAINED CHARACTERIZATION BASIS (high, **NON-GATING**) — a9/a10 publication basis, charter amendment 13 | Last of the seat rows |
| 15 | `raw/` | Assembler inputs: the mechanical `*-triage.md` extracts (verbatim findings/WOs/ED rows/unexecuted obligations per seat), `commits-since-baseline.txt`, `CHANGE-UNIVERSE-BRIEF.md`, `taskqueue-current-queue.txt` | On demand, to check an assembler |

## Row anatomy (identical in every row file)

0. Seat identity and 2026-08-15 result
1. **FINDINGS — original text verbatim, with citation**
2. **WHAT CHANGED SINCE** — commit SHAs, PR numbers, custody paths, decision IDs
3. **ED-QUALIFICATION ROWS** — verbatim row text + located closure evidence, or an explicit
   "EVIDENCE NOT LOCATED — searched: …"
4. **CANDIDATE DISPOSITIONS** — assembled, not adjudicated
5. **WHAT A SKEPTICAL SEAT SHOULD PROBE**
6. **OPEN ITEMS FROM THIS ROW**

## The eleven verdict rows and the ED universe

The 2026-08-15 sitting recorded **0 READY / 11 NOT-READY** (ten gating seats + the non-gating L11
basis seat), with L2 additionally **UNVERIFIED** on coverage. The fleet emitted **23
ED-QUALIFICATION rows**: L1×2, L2×2, L3×4, L4×1, L5×1, L6×2, L7×3, L8×4, L9×3, L10×1, L11×0.
Under charter:77-83 as amended, a READY-CANDIDATE sitting requires **no NOT-READY, no UNVERIFIED,
and every ED-QUALIFICATION row closed with evidence**; only T0 (perishable) rows may remain open.

## Sources of record (not duplicated into this packet)

- The 2026-08-15 sitting custody: `docs/process_traces/2026-08-15-readiness-council/`
  (`council-verdict.md` is authoritative for the aggregate — **the sealed packet's §2 seat table is
  stale and shows the wrong result**).
- The charter: `docs/process/instrument-readiness-audit-charter.md` (v2, `6a7849c`).
- The audit-baseline manifest: `docs/process/audit-baseline-manifest.json` (`694442c`, **not
  superseded**).
- The state kernel: `docs/process/state_kernel.json` — declared sole work-selection authority;
  holds `WINDOW-COUNCIL-GATE` and the Phase-1 WO statuses.
