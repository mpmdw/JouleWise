# Findings dispositions, PR #465 (lane G2A-B3-RETRY-BACKOFF-01)

Reviewed head `ccca0b3c`; fixes in `68bf2301`.

| Source | Finding | Disposition |
|---|---|---|
| Sol lane report (11), residual risk | A longer stream can trip the active v3 clock anchor's 5 ms cap (synthetic 8 ppm: bounded at 151 s, refused at 751 s) | **Fixed in `ccca0b3c` by the lead**: block-3 backoff 600 → 300 s; clock-anchor tests added. Ruling changed in record 00 §1. |
| Sol executing review (12) F1 MAJOR | The 60 s remainder in the stream budget is not conservative (large-model decode alone needs 103 s at the code's worst-case 5 tok/s) | **Fixed in `68bf2301`**: budget = 2 × 104 s idle + 300 + 45 s guards + 2 × 10 s prefill + 516/5 s decode + 6 s = 683 s; bound ≈4.5 ms at block 2's drift and widest half-width; 600 s exceeds. |
| Fable final pass (21) 1 MAJOR (non-blocking, fail-closed) | Sizing understated stream length and ignored the anchor half-width; real block-2 drift ≈3.2 ppm, half-widths to 2.31 ms, idle attempt ≈104 s | **Fixed in `68bf2301`** (same change as Sol F1, with Fable's real inputs). Registration §4 item 3 states the sizing by reference. |
| Fable 2 MINOR | Harvest accepts any policy file in `configs/campaign_policies/` the inventory names | **Fixed in `68bf2301`**: harvest refuses unless production profile, bracket required, admission enabled and aborting (`campaign_policy_not_claim_grade`); two schema-valid non-claim-grade policies tested. |
| Fable 3 NIT | Retry budget uses 75 s idle; a recorded attempt takes ≈102 s | **Rejected**: 4 × ≈27 s ≈ 108 s, inside the per-member allowances (240 s small, 300 s large against ≈112 s of non-idle work); the generator sizes from code, not bundle timing (its own rule). |
| Fable 4 NIT | Strict-bundle subtest labelled 600 loads the 300 s file | **Fixed in `68bf2301`**. |
| Fable 5 NIT | `environment_admission.retry_backoff` is recorded but never validated | **Rejected**: audit-only by design; the controller is its only writer, and the attempt timestamps (validated for order) already show the gap. |
