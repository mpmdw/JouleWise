# 12 — Lead bench probe AFTER the packet freeze: the v3 anchor on the real envelope data with the two absolute caps lifted

NOT part of the sealed packet (sha 0e3dfe79…); the judge and the refuter did not receive it. Executed by the magistrate at 05:40 PDT 2026-09-22 in worktree `JouleWise-wt-mag-d9990b3c` (main `9b6b3f0e`), read-only over the harvest archive. It answers the question the packet left to the judge under Q2(b): whether the affine fit alone refuses the discrete `adjtime` slews once the pre-fit span cap and the post-fit bound cap no longer fire. Script: `12-lead-bench-probe-caps-lifted.py` (sha256 0a717ac7ff7fe03c803dee64f6e9f6a79488a20b7b6d9c4801a66d69b4725105); it sets `MAX_WALL_MINUS_MONOTONIC_SPAN_S` and `MAX_EFFECTIVE_CLOCK_ANCHOR_BOUND_S` to 1.0 s and changes nothing else.

```
ClockStamp fields: ['epoch_s', 'monotonic_before_s', 'monotonic_after_s', 'wall_resolution_s', 'monotonic_resolution_s']
envelope 01: frames=2547 parse+derive=5.4s status=unknown detail=affine_clock_fit_empty span_ms=nan H_ms=nan bound_ms=nan rate=[None,None]
envelope 02: frames=2535 parse+derive=7.6s status=bounded detail=None span_ms=0.416 H_ms=0.704 bound_ms=1.123 rate=[0.9999993074697832,0.9999993231523191]
envelope 07: frames=2488 parse+derive=5.3s status=unknown detail=rate_aware_native_set_empty span_ms=nan H_ms=nan bound_ms=nan rate=[None,None]
envelope 08: frames=2532 parse+derive=7.8s status=bounded detail=None span_ms=4.542 H_ms=0.532 bound_ms=5.077 rate=[0.9999923917810377,0.9999924075145893]
envelope 09: frames=2529 parse+derive=6.8s status=bounded detail=None span_ms=4.525 H_ms=0.821 bound_ms=5.348 rate=[0.9999923915281319,0.9999924053879551]
envelope 10: frames=2502 parse+derive=5.5s status=unknown detail=affine_clock_fit_empty span_ms=nan H_ms=nan bound_ms=nan rate=[None,None]
envelope 03: frames=2504 parse+derive=5.5s status=unknown detail=affine_clock_fit_empty span_ms=nan H_ms=nan bound_ms=nan rate=[None,None]
envelope 04: frames=2482 parse+derive=5.5s status=unknown detail=affine_clock_fit_empty span_ms=nan H_ms=nan bound_ms=nan rate=[None,None]
```

Reading (lead, labeled): every envelope that contained a discrete slew (01, 03, 04, 07, 10) is refused by the MODEL gates (`affine_clock_fit_empty`; 07 `rate_aware_native_set_empty`) with the caps out of the way — the caps were never what caught the slews. The only envelopes whose outcome the absolute caps change are the steady −7.6 ppm captures 08 and 09, which the fit resolves with rate windows [0.99999239, 0.99999241] and honest bounds 5.08 / 5.35 ms. Under Q1(a) (network time OFF for the span) no discrete slews occur; under Q2(b)/(c) the two steady-rate captures are bounded and their 5 ms bound is priced into `error_bound_j` at about 5 ms × 0.32 W × 2 ≈ 3 mJ each.
