Ed,

Stage-1 night notice (NIGHT-REHEARSAL-01 acceptance item 4) and NIGHT_HANDBACK notice, sent BEFORE the plan is published. Launch needs no action from you unless you reply NO on this thread; a NO stands the night down.

PLAN
- plan_id: d079-epoch-25g83-derivation-n1-20260913
- class: DIAGNOSTIC_NO_PACK (twelve derivation-only powermetrics fiducial captures, no model, no pack, no Git, no claim output)
- purpose: the epoch-equivalence check you ruled in issue 316 (pre-registration revision 2): is the 25G83 build inside the r6 envelope? m < 6 INCONCLUSIVE (one more night); PASS = every retained b_fiducial_s <= 0.032898493715362 s and range <= 0.009724 s (D-102 continuation addendum, then real G2-a); FAIL = revision 1's three nights with this one as night one.
- t0: 2026-09-13 02:56:00 PDT (epoch 1789293360) = 2026-09-13 09:56:00 UTC
- window_max_s: 9000 (acquisition allocation ends 05:26:00 PDT, epoch 1789302360)
- courier deadline: t0 + 9000 + 300 = 05:31:00 PDT (epoch 1789302660); next 07:00 dead-man 07:00:00 PDT (epoch 1789308000), 89 min of slack

PINS
- H (repo_head = measurement_head = handback commit): f90cb8c016662f8af6faa73d905fc472443432ab (twice, deliberately: f90cb8c016662f8af6faa73d905fc472443432ab)
- measurement root: /Users/edr/JouleWise-measurement-20260913-derivation (fresh GitHub clone detached at H; venv Python 3.13 from env/mac-measurement-lock.txt, lock diff empty; canonical 76-record ledger restored byte-exact and custody-authenticated at pin 76)
- night custody root: /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260913
- runs root: /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260913/runs
- wrapper (plan chain_path): /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260913/chain.zsh sha256 569daedae03126d9eb819abd3b132baf860597dbe926a0db87311643a854df45; sidecar chain.zsh.sha256
- tracked chain the wrapper pins: scripts/night_chains/calibration_derivation_only.zsh sha256 b8bf5b0a85bb2012eed9763f70743963d6f24c3ec3038142525766c00f1ac8cf
- desk inputs: identity-epoch.json sha256 b8a1094c24d1795e39fc527ce96ba9e1a4ba2bda66d4250f35a462e28a90b607; t1-bindings.json sha256 8dcdfb009d9cf6c7d218bf19667ad1b88f6a9747c6822c02fd2997ef9a1e9d98 (both in the night root)
- pre-registration configs/calibration/preregistration_d079_epoch_25g83_rev1.md at H: sha256 84b820b9069c5b7b34b35e1b8fcd1c436c54ded04cbb24c6c985bbc867ce0b5c (five commit-time fields filled in H)
- session id: d079-epoch-25g83-derivation-n1-20260913; evidence root id: evidence-d079-epoch-25g83-derivation-n1-20260913 (registered by this arm; no prior record named one)
- frozen calibration plan (identity binding only): configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json copied to the night root
- epoch watch at the desk: check rc 3 with os_build and the ledger's last sampler digest MISMATCH (expected), pre-registered powermetrics sha256 b762e5bf...: match

TIMELINE
- planned install span: today 2026-09-12 03:00–06:30 PDT, both agents installed FROM the clone with --python <clone>/.venv/bin/python; the 07:00 dead-man today stands down with one log line (expected)
- exit boundary: this activation exits after recording the arm; the watchdog's stand-down for the plan span lands 2026-09-13 02:31:00 PDT (t0 − 25 min)
- harvest: the next activation after the courier, per derivation_night_runbook.md §2; the equivalence tool runs twice and the verdict is recorded before any action

CANCEL
Reply NO on this thread. Before publication I re-read this thread (METADATA_ONLY) and the directive issues; after publication a NO still stands the night down under NIGHT_HANDBACK (the next activation uninstalls). Headless note: I can read this thread only while alive; I cannot certify a reply arriving after I exit went seen until the next activation.

Fable 5.1, activation b58fb582
