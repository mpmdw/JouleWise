# Lead rulings on the v4 council review: round 1 (2026-11-06)

Laptop lead (interactive session 359dce51, Opus 5.5). These settle two questions that the implementing reviewers raised against CHAIR.md.

## L1. Ruling 1(f) is restated

As written, ruling 1(f) (`I_D + 1.13544·T_dead + max_R1_tail + 60 ≤ 1800`) can never pass, because `require_ready` already sets `T_dead = (1750 − I_D)/1.13544`.

Its intent is that a worst-case D member fits under the 1,800 s member cap. Restated:

    T_dead = min( (1750 − I_D)/1.13544 , (1800 − I_D − max_R1_tail − 10)/1.13544 )

- `max_R1_tail` is the largest post-deadline tail R1 observes (`r1_slots.max_r1_tail_s`).
- The kit asserts `I_D + 1.13544·T_dead + max_R1_tail + 10 ≤ 1800` using the T_dead it froze.
- With the R1 tail ≤ 40 s, the first term governs and nothing changes.

## L2. The U5 constant c (ruling 6) is fixed before R1

The U5 bar is `|β_T|_90 × δ_slow ≤ c·σ_pair`, with **c = 1.0**.
- In words: across the allowed release band, the state-induced energy shift must be no larger than one SD of identical-work pair noise.
- σ_pair is the R1 replay-pair SD, combined with 2.97 J (pilots 4-5) as max(observed, 2.97 J).
- Inconclusive when the 90 % upper bound exceeds the bar while the point estimate is within it.

## L3. bf16 reference for quantization quality

The live gold stream (`/private/tmp/jwgold-run-a2`) runs DEFAULT_PROMPTS (17 positions of arbitrary token ids), so its head unit is no quality reference. It stays as the layer-parity validation.

A second streamed pass on the laptop then captures the reference on real text:
- the 12 hosted-reference prompts plus short natural-text continuations taken from fixed reference text, never from maxfit's own greedy output;
- each prompt ≤ 512 tokens;
- `--prompts-json`, head unit only plus the chain it needs.

It runs after the parity pass completes. The two pass rules (the e2e maxfit thresholds and the quant-quality POLICY) are merged into one table. The quant-quality POLICY is primary, and e2e reports against it.
