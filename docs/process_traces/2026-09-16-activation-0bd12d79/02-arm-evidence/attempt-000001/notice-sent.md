Ed,

NIGHT NOTICE — d079-epoch-25g83-derivation-n1-20260916 (DIAGNOSTIC_NO_PACK, the epoch-equivalence check), arm attempt 1, from headless magistrate activation 0bd12d79. Launch needs NO action from you unless you reply NO on this thread before install close (09:35:00 PDT). Your interactive session must be closed before t0: this class has no idle-interactive exemption, and the arm block publishes only on a clean census.

WHAT
- plan_id: d079-epoch-25g83-derivation-n1-20260916 (fresh authoring; the 2026-09-14 staging of this id was never published and its clone at 3c8bd220 was moved out of the path unused)
- receipt_class: DIAGNOSTIC_NO_PACK — the equivalence check ruled by your issue #316: one agent-free derivation-kind ledger session, 12 declared slots at head-equals-pin (ledger head 76), 600 s settle, twelve derivation-only powermetrics fiducial captures at a 600 s cadence; no model runs, no pack, no Git, no claim output. Successor of n1-20260915 (refused at t0 on load 2.55, fseventsd; cleared by the 09-15 19:55 restart, fseventsd now 0 % CPU).
- H (repo_head = measurement_head = handback commit on main): 32243adca1bfc8822e8001e4bac58000d591aa4f
- H again: 32243adca1bfc8822e8001e4bac58000d591aa4f
- measurement root: /Users/edr/JouleWise-measurement-20260916-derivation (fresh clone 04:10 PDT, detached at H 04:14 after the fidelity-test pin fix (the first authoring aef09471 was superseded unpublished); lock diff empty; mlx 0.31.2 / mlx_lm 0.31.3; tree clean; canonical 76-record ledger restored byte-exact, custody authentication PASS sequence 76)
- night custody root: /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916
- runs root: /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916/runs
- staged plan sha256: 5cc4e11aa2e0b6e15ac6e1337f6247397a015aa800139c7156ae2551f7c258a2 (authored_epoch_s 1789575887 = 09:24:47 PDT; t0 − authored = 0.34 h, inside the 36-hour bound)
- t0: 2026-09-16 09:45:00 PDT (−07:00) = 16:45:00 UTC (epoch 1789577100)
- window_max_s: 9000 (acquisition allocation ends 12:15:00 PDT, epoch 1789586100)
- completion / courier deadline: t0 + 9000 + 300 = 12:20:00 PDT (epoch 1789586400); derived dead-man 13:20:00 PDT (epoch 1789590000), daily until uninstalled
- wrapper (chain_path): /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916/chain.zsh sha256 f3a7b4d3862678fd7128a0fcb71858bdd3952c1c65723adae87e9747658b7e90; sidecar /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916/chain.zsh.sha256; --verify VERIFIED; zsh -n rc 0
- tracked chain the wrapper pins: scripts/night_chains/calibration_derivation_only.zsh sha256 b8bf5b0a85bb2012eed9763f70743963d6f24c3ec3038142525766c00f1ac8cf (= the pre-registration's chain-digest field; pre-registration configs/calibration/preregistration_d079_epoch_25g83_rev1.md sha256 84b820b9069c5b7b34b35e1b8fcd1c436c54ded04cbb24c6c985bbc867ce0b5c, unchanged since sealing)
- desk inputs (under the night custody root): identity-epoch.json sha256 b8a1094c24d1795e39fc527ce96ba9e1a4ba2bda66d4250f35a462e28a90b607; t1-bindings.json sha256 8dcdfb009d9cf6c7d218bf19667ad1b88f6a9747c6822c02fd2997ef9a1e9d98
- frozen calibration plan copy sha256 9ab4776f3c416284d6d01a5a49587eedcdfbcb8ef61428cdc1046e9b9d74a072 (plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3)
- desk epoch watch: check rc 3 (os_build 25F84 → 25G83 mismatch, powermetrics sha mismatch, hardware and mlx 0.31.2 match), check --preregistration rc 3 — the expected shape for this night
- driver preflight ok (Python 3.13.1 from the clone's venv); --render-only rc 0, pins validated against H

WHEN (all 2026-09-16, PDT = UTC−07:00)
- install span 1 (the shipped whole-day span): 00:00:00 (epoch 1789542000) → 2026-09-17 00:00:00 (epoch 1789628400, excluded)
- notice-send open: this message; install close (excluded): 09:35:00 (epoch 1789576500) = t0 − 10 min
- plan span / exit boundary (watchdog stand-down REQUEST): 09:37:00 (epoch 1789576620) = t0 − 8 min; TERM 09:39:00; KILL 09:40:00
- t0 09:45:00 (1789577100); window end 12:15:00 (1789586100); completion 12:20:00 (1789586400); dead-man 13:20:00 (1789590000)

PRECONDITIONS MET before this notice: H on main and an ancestor of origin/main (pushed 09:24 PDT; hosted CI on H in progress at the notice); the stub rehearsal-20260916c harvested, its agents uninstalled (rc 0) and its plan root retired (bytes archived, 15/15 checksums); nothing armed or discoverable (launchctl = magistrate only; 0 plans under night-custody); clone clean at H; desk block rc 0 at 09:24 (re-authored at H after the 05:40 candidate lapsed); no open directive issue; no stand-down request.

CENSUS AT THIS SEND: CLEAN at 09:24:48 (foreign_pids [], own MCP servers stopped; your interactive session closed at ~09:24). The arm block re-runs the census immediately before publication and aborts on any foreign process. PLEASE leave the machine untouched from 09:37 (plan span) through 12:20: any keyboard/mouse activity or agent session at 09:45 refuses the night.

WHAT HAPPENS WITH THE RESULT (fixed before the night, runbook §2.5): m = retained valid captures; m < 6 INCONCLUSIVE → one more equivalence night; PASS = every retained b_fiducial_s ≤ 0.032898493715362 s AND range ≤ 0.009724 s → dated D-102 continuation addendum, then real G2-a windows; FAIL = anything else → revision 1's three-night derivation with this night as night one. Nobody reads a member value before the session is terminal.

CANCELLATION: reply NO on this thread, or open a directive issue authored by you saying NO, before 09:35:00 PDT. NO relay: this activation reads this thread through the Gmail MCP immediately before publication and re-reads the directive-issue list; after it exits (before 09:37) a reply is read by the next activation, so a NO after publication stands the night down only through the next activation's harvest path. Nothing else needs your attention.

— Fable (magistrate, activation 0bd12d79)
