# Magistrate ruling — the week after `_v4` (D-163; 2026-08-28)

Three blind seats (Sol xhigh, Opus 5, Fable 5) converge on every load-
bearing number. Ed decides the go/no-go; this ruling fixes what is
prepared at the desk during the campaign so the choice is executable.

## The arithmetic (converged)
- Nights: floor pack ≈ 6.3–6.5 h (decode-only ≈ 3.1–3.2 h); contrast
  pack ≈ 5.2 h (decode-only 2.8 h); per-night fixed overhead ~70–84 min
  that never amortises. Decode-only, REUSING `_v4`'s 1.5B/7B floors and
  its 1.5–7 contrast: **3-point ladder (0.5/1.5/7) = 1 floor night + 1
  contrast night ≈ 2 nights**; 4-size (+3B) ≈ 2–3; 5-size (+14B) ≈ 3–4
  decode-only, 7–9 with prefill. `fixed_n = 10` stays (D-062; n=5 widens
  every floor ×1.5).
- Effects: adjacent decode steps at 512 tokens are 6–10× the floor —
  resolvable, and therefore NOT a demonstration of the paper's thesis
  (attribution dominance); prefill steps below 3B refuse by design (the
  only instrument-exercising content a ladder would add).
- Models: 0.5B is mirrored and tokenizer-identical (`a8506e71…`) — a
  one-desk-day D-016 admission; 3B/14B are absent and unpinned (fresh
  mirror, revision SHA, provenance, D-074 battery each).
- Code: a claim-bearing ladder needs `analysis_manifest_v5.py` as the next
  frozen sibling (the v3 validator pins 4 slots / 2 contrasts / 10 blocks /
  80 members) plus a generator and a 0.5B floor pack: 2–3 Sol-days
  (Sol) to 6–10 (Opus, with the C-028 gauntlet). Council + cold gate: it
  is a contract change.
- Calendar: `_v4` closes ≈ Sun 09-06; TRANSFER-FIDUCIAL-01 owns the first
  post-campaign diagnostic window by ruling (< 1 night); earliest `_v5`
  night Mon/Tue 09-07/08 → 3-point results ≈ 09-10.

## Rulings
R-1. **Impressiveness per night, ratified:** (1) the inserted-gap
fiducial — closes §7 Limitation 1, the paper's stated #1 weakness, in
under a night, no new manifest/floor/model; (2) the 3-point ladder
0.5/1.5/7 decode-only, ~2 nights, reusing `_v4` floors; (3) quantization
(C5-1.12) ≈ 4 nights with open gates; the 4/5-size ladder last.
R-2. **Prepared at the desk during `_v4` regardless of Ed's answer:**
TRANSFER-FIDUCIAL-01 implementation (stream already running; parked
until close). **Prepared only on Ed's GO:** the 3-point ladder —
`analysis_manifest_v5.py` sibling (per-manifest slot/contrast/count
derivation; Holm family m = new contrast count; estimator and Holm
untouched), a decode-only `d117_ladder_v1` contrast pack (0.5B vs 1.5B),
a decode-only `d117_floor_qwen25_0p5b_v1` pack, the 0.5B D-016 pin with a
tokenizer-hash regression, council + cold gate, freeze, clone proof.
3B/14B are NOT attempted in this window.
R-3. The ladder's honest sentence, if run: "512-token decode energy for
4-bit Qwen2.5 at 0.5B, 1.5B and 7B, each gated by its own independently
minted cell floor, was ordered by parameter count with every adjacent
pairwise contrast resolved" — C5-1.1 in its permitted pairwise form,
never a scaling law; RQ-SHAPE-ENERGY untouched.

## Custody
`00-brief.md`, `01-sol-seat.md`, `02-opus-seat.md`, `03-fable-seat.md`.
