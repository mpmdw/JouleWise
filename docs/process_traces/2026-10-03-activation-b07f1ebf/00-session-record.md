# Activation b07f1ebf (headless magistrate, Opus 5.5), 2026-10-02 23:10 PDT

Launch: notice_pending empty; no unread owner mail; open directives are the
standing #405-#422 set (no new instruction); nothing armed; canonical root
fast-forwarded 56faf8a1 -> 4205713c (records only).

Step: block-2 handoff item 1, arm `w1` (recipe 40).

- §1: t0 1791013320 (2026-10-03 00:42 PDT), WINDOW_MAX_S 19980.
- §2 bench created at /Users/edr/night-plan-staging/g2a-bench.
- §3 fill: H 4205713c5314cef2d99c849db9d1473ac449a462, REG 8e45a0e0...a5b8,
  ledger seed C2 clone ledger sha 3c9b6844...72fb.
- step0 PASS (battery gate PASS); step1 PASS (head == pin, sequence 376).
- step2 stopped twice at the argv-only chain inspection (nothing published,
  no agent installed, no notice sent):
  1. `FAIL measurement_head must be a full 40-character lowercase SHA-1`:
     the recipe ran the chain without `MEASUREMENT_HEAD`, which the driver
     supplies (`scripts/run_night.py` `_chain_environment`). Recipe defect;
     the step2 line now passes `MEASUREMENT_HEAD="$H"`.
  2. `calibration_plan.json: No such file` under
     `/Users/edr/night-g2a/d117-g2a-prefill-probe-20261003T0742ZT0742Z`: the
     generator (`integrated_g2a_chain`) pinned `G2A_ROOT` and then renamed
     the runsheet window id inside every `G2A_*` export; the real root
     contains the plan id, which begins with that id, so its suffix was
     doubled. At t0 the chain would have failed its input assertions (a
     NULL window). Fixed by renaming first, then pinning; regression test
     with the production id/root shape fails on the old code.
- R3: one full-tier PR carries both fixes and this record; re-arm `w1` with a
  new t0 at the merged head (the abandoned attempt's unpublished directories
  for plan d117-g2a-prefill-probe-20261003T0742Z are left in place).
