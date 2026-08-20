# 00-INDEX — READY-CANDIDATE COUNCIL PACKET (assembled 2026-08-19)

Mechanically assembled, read-only, against the 2026-08-15 council audit baseline **8937dec**.

**This packet grades nothing.** Every row carries the original finding verbatim, what changed with
exact pointers, a *candidate* disposition, and probes for a skeptical seat. Seats judge.

> ### TWO NOTES THE SITTING MUST READ BEFORE ANYTHING ELSE
>
> **1. The head moved during assembly, and it is not `main`.** This packet was commissioned at
> `4597ad4`; a sibling assembler brief pinned `d10881b`; the worktree tip was `b92b43d` mid-assembly
> and `7305e0d` at close. `main == origin/main == 0099382`, and the branch is **52 commits ahead of
> main while main holds 10 commits the branch lacks**. The entire Phase-2 transaction — the `_v3`
> family, freeze-0003, the D-146 claim barrier, D-149's kernel fences — is **branch-only, not in
> main**. Under charter amendment 12 (final-head invalidation) the sitting must rule which head its
> verdict attaches to before it rules anything else. See `rows/ROW-P-PROGRAM.md` **P-13**.
>
> **2. This directory holds TWO INDEPENDENT ASSEMBLIES of the same rows.** A sibling fleet
> (brief: `_ASSEMBLER-BRIEF.md`, pinned `d10881b`) produced the numbered files
> `10-…`–`20-…` plus the consolidated `30-ED-QUALIFICATION-rows.md`. This fleet produced
> `rows/ROW-L1…L11.md` plus `rows/ROW-P-PROGRAM.md`. Neither was derived from the other. That is a
> **feature for a council**: where two independent assemblies of the same finding disagree, the
> disagreement is itself evidence. The sibling set is missing L5; this set covers all eleven seats
> and adds the thirteen program-level rows. The sibling set's `30-ED-QUALIFICATION-rows.md` is the
> single best view of the ED gate and is treated here as the ED roll-up of record.

---

## Reading order

| # | File | What it is | Read when |
|---|---|---|---|
| 1 | `01-SESSION-BRIEF.md` | Charter form requirements; **amendments 11-12 verbatim**; the sitting-type amendment; anti-ritual discipline; what your seat must produce; form preconditions for any READY | **First, always** |
| 2 | `OPEN-ITEMS.md` | Everything no repair addressed + everything the assemblers could not locate | **Second** — read before the rows, so you read the rows knowing what is missing |
| 3 | `rows/ROW-P-PROGRAM.md` | The thirteen **program-level rows** (P-1…P-13): not-certified-complete, the un-superseded baseline manifest, the M-2 remand, the charter-amendment gap, the same-signature consequences, the sweep body, Phase-2 re-freeze ordering, the 23-row ED gate, this sitting's own form, Phase-1 completion state per the state kernel, the queue's stale pack identities + D-149's five auto-GO conditions, findings retired by risk acceptance, and **P-13: which head is this sitting about** | **Third** — several of these condition whether any seat row can aggregate to READY; **P-13 is logically prior to every seat row** |
| 3b | `30-ED-QUALIFICATION-rows.md` | Sibling-assembly consolidated walk of **all 23 ED-QUALIFICATION rows** with a summary tally. The clearance rule turns on this file | With ROW-P-PROGRAM P-8 |
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
| 15 | `10-…`–`20-…` numbered files | The **sibling independent assembly** of seats L1–L4, L6–L11 (no L5), pinned `d10881b` | As a cross-check on the `rows/` set — divergences are evidence |
| 16 | `raw/` | Assembler inputs: the mechanical `*-triage.md` extracts (verbatim findings/WOs/ED rows/unexecuted obligations per seat), `commits-since-baseline.txt`, `CHANGE-UNIVERSE-BRIEF.md`, `taskqueue-current-queue.txt`. The extraction logic that produced the `*-triage.md` files must be committed beside the sealed packet per the M-2 non-author-assembly protocol | On demand, to check an assembler |

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

---

## Assembly provenance (record it in the sealed packet)

- Assembled read-only in the worktree `…/scratchpad/wtS0`, branch `impl/r2-s0-mint-resolver`.
  `git status --porcelain` empty at close — the tree was never written.
- **Heads observed during assembly, in order:** `4597ad4` (commissioned) → `b92b43d` → `7305e0d` →
  `45e0229` → `48f337b` → **`2243137`** (at close). Six heads. Assemblers state per-row which head
  they verified at; where a count or digest was measured, the measuring head is named beside it.
- `main == origin/main == 0099382` throughout. Nothing in the Phase-2 transaction has merged.
- Commit `2243137` records the lead landing the sibling assembly's eleven row files into repo
  custody. The `rows/` set here (eleven seats + `ROW-P-PROGRAM.md`) is a **separate, independent**
  assembly and includes the L5 row the sibling set lacks and the thirteen program-level rows.
- The state-kernel WO statuses quoted in `ROW-P-PROGRAM.md` P-10 were re-verified at `2243137` and
  are unchanged.
- **Commit distance from the baseline grew during assembly**: 214 at commissioning (`4597ad4`),
  215 at `b92b43d`, **219 at close (`2243137`)**. Rows written early cite 214/215; the drift is
  documentary, not code — but every doc line number in this packet should be re-verified at sitting
  time. That a packet could not be assembled against a stable head is itself material to the
  Phase-3 pinned-head discipline.
- The sibling assembly's rows were landed into repo custody at `2243137` under
  `docs/process_traces/2026-08-19-prep-sprint/ready-packet-rows/`. The `rows/` set here is not yet
  in custody.
