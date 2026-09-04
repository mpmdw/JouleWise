# Magistrate ruling — the paper custody-read seam (2026-09-04)

Inputs: three-seat consult (Sol 11, Opus 12, blind Fable 11-blind) and the adjudication packet 14. Trigger: three supplier lanes hit the same class three times each (caller-supplied documents self-sealed into claim-bearing prose). Packet recommendations Q-C-1..Q-C-9 are ADOPTED as follows.

1. **One seam.** `joulewise/paper_custody.py` exposes `open_paper_input(ref)` dispatching over five CLOSED family refs (D-123 reported-energy parents; D-165 close-out; whole-window verdict rows in `campaign_log.jsonl`; `claim_verdicts.v1` + `claim_side_bound.v1` sidecar; `transfer_fiducial_result.v1`). Raw readers and constructors are private. (Q-C-1)
2. **Authorization.** Governed files are authorized through clean Git blobs; generated files through receipts reached from a registered custody inventory; caller-supplied digests are PINS only, never authority. (Q-C-2) Receipts are required production inputs but count only as corroboration beside an independent anchor and a fresh validator replay. (Q-C-3)
3. **Whole-window stops stay blocked** until a typed authenticity/admission validator and a governed receipt producer both exist (`WHOLE-WINDOW-STOP-RECEIPT-01`). (Q-C-4)
4. **Outputs.** Five concrete frozen verified types; supplier-facing dicts, mappings, bytes, sequences, and pre-validated objects are prohibited at every supplier entry point. (Q-C-5) Refusals use the closed `paper_custody_*` namespace with nested validator codes that are never renderable. (Q-C-6)
5. **The one test.** An auto-census test per family covering raw byte mutation, full caller resealing, and replay-to-reopen replacement, each yielding the exact refusal code and zero rendered output. (Q-C-7)
6. **Bypass closure.** The lower floor-loader and campaign-log byte bypasses are closed in the same landing, with authentication-surface and signature guards. (Q-C-8)
7. **D-173 (provisional).** `docs/contracts/paper_supply_custody.md` is the single normative home; the decision-log entry is written PROVISIONALLY by the magistrate and goes before the next cold gate (the paper-supply packet) before any supplier merges; Ed is notified and may veto. (Q-C-9)

Mission: `PAPER-CUSTODY-SEAM-01` (Sol xhigh) builds 1–6 and the contract doc against fixtures only. Then D123, D165, GAMMA (whose floor-lineage authorization becomes a seam family read) and TRANSFER (B1) re-land ON the seam, deleting their private readers as the packet lists; each re-landing gets a delta and the Opus counter-review before the packet.
