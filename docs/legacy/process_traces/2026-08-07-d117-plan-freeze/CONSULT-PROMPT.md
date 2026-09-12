DESIGN CONSULT — plan-freeze packet for the three prospective claim windows (D-117).

You are designing, not implementing. Argue the tradeoffs before you specify; you have
explicit license to disagree with any shape proposed here. Emit the design memo as your
FINAL MESSAGE.

GOVERNING CONTEXT (read these first; named decisions win over any conflicting text —
flag conflicts): docs/decision_log.md entry D-117 (at the end of the file; the adopted
ruling) and its referenced trace `docs/process_traces/2026-08-06-d110-remint-fork/`
(esp. CONSULT-RESPONSE.md §3-4 — your predecessor's own desk-queue sketch);
docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md (prefill scope:
floor cells ride both floor windows; contrast decode-only default; 256-tok arm is an
open Ed option — design must keep it ATTACHABLE without re-freezing the base plans).

DESIGN THE COMPLETE PLAN-FREEZE PACKET for:
- W-alpha: fresh 1.5B decode floor window (from the proven 10-absolute/40-null design —
  find the proven plan/config lineage in the repo, e.g. the a10-era plan configs and
  campaign packs, and say exactly which files you treat as the proven template);
- W-beta: fresh 7B decode floor window (budget ~2.6-3.0 h class incl. 20% margin);
- W-gamma: fresh 1.5B-vs-7B decode contrast window (ABBA, frozen metric
  phase_energy_j.decode).
(Names W-alpha/beta/gamma are placeholders — YOU propose the immutable identifier
scheme; "Window D" and C/D terminology are unavailable per D-117 cl.5.)

FOR EACH WINDOW: member schedule (stages, counts, order manifest shape), runtime budget
arithmetic (member times from historical evidence you locate, calibration bracket,
3/1/3 references, cooldowns, settling, ≥20% failure margin, 2-4 h envelope check),
prefill floor cell definition riding the same members (what must be pre-registered for
phase_energy_j.prefill to be claim-eligible), evidence-root id, extraction spec shape,
and what the §5A operator bookends require.

CROSS-CUTTING DESIGNS:
1. Generalized mint pinsets: the D-084 hard literal 7.377086 refuses any corrected
   mint; closure is per-plan pin supply via the generalized path. Locate the current
   mint pinset mechanism and specify exactly what per-plan artifacts/literals each
   window's mint needs, and at what point the six-decimal literals get frozen
   (they cannot exist before collection — design the two-stage freeze honestly).
2. Live-ledger bracketing: each window's pre/post calibration receipts append to the
   issued ledger (D-116 regime) — specify the receipt flow and what the synthetic
   THREE-WINDOW live-ledger integration regression must exercise (fixtures, the
   candidate-discovery import-exclusion boundary, causal bracketing of all three
   windows, refusal vectors).
3. D-102 successor-artifact packet: what must be pre-built so a range-expanding live
   observation cannot strand the campaign mid-window.
4. Contrast manifest for W-gamma incl. how the optional 256-token prefill arm would
   attach later WITHOUT invalidating the frozen base (or state why clean attachment is
   impossible and it must be its own fourth window plan).
5. Freeze order and gate points: which artifacts freeze at desk time vs at §5A arm
   time, and where the lead gates sit.

DELIVERABLE: a design memo with (a) ranked open design decisions you made + rejected
alternatives, (b) the per-window plan tables, (c) the cross-cutting specs, (d) a
WORK-ORDER LIST decomposing implementation into enforced-WRITE_SCOPE units (per unit:
files, invariants, test obligations, which units are independent vs sequential), (e)
"what the lead should double-check". READ-ONLY: no writes anywhere. If any repo fact
contradicts this prompt, the repo wins — flag it.
