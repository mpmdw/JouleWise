# CAP-RULE-25G83-1 pre-registration record (session ff50b201, 2026-09-30)

Written BEFORE the recorded roster replay (cap council ruling §… step 3: pre-register, then replay). An earlier exploratory replay was run at 07:0x PDT before this record existed; its output is superseded by the replay recorded after this commit and is disclosed here. The rule text below was fixed by the cold rulings of 2026-09-27 and is not changed.

- Rule: CAP-COUNCIL-25G83-01 R0–R12 as amended by addendum A1 (/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/20-cap-council/31-addendum-ruling.md, sha256 6b4bcaeade3f93199fddf0451f89e0e45c44ed55ad9873ab5bef8e938a92a4bf) and by A2/E1 (/Users/edr/code/JouleWise-wt-bk-ff50b201/docs/process_traces/2026-09-29-interactive-ff50b201/40-cap-a2/21-coldgate-fable-ruling.md sha256 ccef94f0546cde883665d6e9cda0b0b01f9609cd56484d9a264b63ff46b89897; /Users/edr/code/JouleWise-wt-bk-ff50b201/docs/process_traces/2026-09-29-interactive-ff50b201/40-cap-a2/31-coldgate-erratum-ruling.md sha256 070dc4f05b5665c5365c19b18e1424fdd5c9b6fbabfea4b60d971aac216a1f20). R3: Cap = 10 × N_max (largest need in the sizing set R2a), rounded up to the next multiple of 10,000. R5: T* = 45 s, 35 µs per cell, limit 120 s (largest admissible cap 2,142,857).
- R1 (cap rides alone): no other estimator change rides with the cap transaction; main at 0009b97657d6ef794410a89fbd5a063912a3b957.
- Frozen estimator files (the four pinned files, main 0009b97657d6ef794410a89fbd5a063912a3b957):
  - `joulewise/powermetrics_fiducial.py` 386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92
  - `joulewise/uncertainty_evidence.py` b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8
  - `joulewise/adapters/powermetrics.py` 70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4
  - `joulewise/reduce.py` 7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc
- Harness: `scripts/cap_replay_harness.py` at 26222126cb539bbcb4db107ee93ae126e6654fc8, sha256 1386a92f6c0dd667b6798560344e477084ebc1fd8b4d60fc57856dfef5b66ba2
- Roster: /Users/edr/code/JouleWise-wt-bk-ff50b201/docs/process_traces/2026-09-29-interactive-ff50b201/130-cap-roster.md sha256 d8fbb403f291e8e9bfb26b6a3eb92551ddc7655b92f08aa0e767d41cdb8a75e7 (100 captures: sizing set R2a 88, check set R2b 12)
- Interpreter: 3.14.7, /opt/homebrew/bin/python3
