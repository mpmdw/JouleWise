# R1 READY record (item 397): native steps 1 to 4, magistrate c6a5728a as interim lead (item 388 fallback 6)

Run 2026-11-17 14:26-14:28 PST, nothing armed (F0 run 8 closed 12:24:12, Check item 392; F0 run 9 not yet launched). Script: item 397's Start-and-check zsh block extracted verbatim from RUN_STATE at `3cd9a09ed` (custody `r1-ready-c6a5728a/steps1-4.zsh`, sha256 `be0770fbef049744b4c189f6df03f0a927457d3783a161736958304bbb1b68b5`), run with `R0=/Users/edr/night-custody/magistrate/standing-f0/r0-restore-ade002e9/r0.json` (item 377's restore) and `PARTC_VERDICT=/Users/edr/code/jw-wt/partc-c3f4/.desk/r1-partc2-c3f4-20261115T052325Z/part-c/smoke_part_c.json` (item 328's run, OUT named in `CHECK-de565739.md`; not packed, so no archive extraction and no deviation). Exit 0. Full output: custody `r1-ready-c6a5728a/out.txt`.

| step | result |
|---|---|
| pin | W1-line head `b2e01464d` by ls-remote; package commit `05fd23160` present locally (no fetch); SOURCES.sha256 and stage_mbp_r1.sh sha256 equal to the item |
| 1. staging (B01) | dry run ended `SOURCE STAGED ONLY (dry-run 1)`; real run ended `SOURCE STAGED ONLY (dry-run 0) 2026-11-17 14:27:04 PST`; worktree `/Users/edr/code/jw-wt/r1-slot-b2e01464d` detached, HEAD `b2e01464d6d4…`, tree `c904864e46879a4adfbdf0b467d4da1ee5928285`, clean; preparation `/Users/edr/r1-preparation/r1-slot-b2e01464d` |
| 2. imports (B02) | established interpreter: `0.31.2 0.31.3 5.12.1`; worktree `.venv/bin/python`: `0.31.2 0.31.3 5.12.1` |
| 3. 60-key check (A14) | ok true, 60 keys, die 16, heatsink 44, problems [], r0 sha256 `e6231a8f…769b`, config sha256 `272aecb8…2f46`; tree still clean |
| 4. G1 re-read (RL-175 D.2) | T = 2; start-state rows 4 = 2T; released G0 rows 1; released G1 rows ['1']; first-reading rows ['0','1']; unrecognised []; **G1 COUNT OK** |
| 4(b) by hand | the one G1 (`gate_waits_s.G1`, release sample turn 1) is turn 1, an admitted turn after the first |
| 4(d) by hand | `members.d_bank.gate_waits_s`: G0 102.80012677 s + G1 99.905027417 s = 202.705154187 s = `gate_time.gates_plus_holds_s` 202.705154187 s (bar 1e-6 s absolute: the 1e-6 column-unit agreement bar of the no-silly-numbers rule; D has no holds) |
| 5. network time, frequency word | Network Time: Off; `ntp_adjtime` rc 0, freq word 0, status 0x2081 (re-read at the arm) |

Item 328's Part C is marked **"G1 complete (RL-175 re-read)"**. Signed: magistrate c6a5728a as interim lead (item 388 fallback 6). By item 397, R1 is READY from this record with the effective condition unchanged: effective from `dev-05-s02`'s launch record, not before. Until then every gate reads `SESSION_READY=no`.

## Item 396: G1 re-read of every Part C run on this host (same code as step 4, plus the 4(d) sum; custody `r1-ready-c6a5728a/f0-g1-reread.txt`)

| t0 epoch | run | T | rows | G0 | G1 turns | G1 count | G0+G1 = gate_time (s) |
|---|---|---|---|---|---|---|---|
| 1794703426 | item 319 | 2 | 4 | 1 | ['1'] | OK | 201.666474730 = 201.666474730 |
| 1794720205 | item 325 (Check item 328; the counted Part C) | 2 | 4 | 1 | ['1'] | OK | 202.705154187 = 202.705154187 |
| 1794777374 | F0 run 1 | 2 | 4 | 1 | ['1'] | OK | 200.498899603 = 200.498899603 |
| 1794791845 | F0 run 2 | 2 | 4 | 1 | ['1'] | OK | 201.520994084 = 201.520994084 |
| 1794806327 | F0 run 3 | 2 | 4 | 1 | ['1'] | OK | 203.633972959 = 203.633972959 |
| 1794835956 | F0 run 4 | 2 | 4 | 1 | ['1'] | OK | 198.471443000 = 198.471443000 |
| 1794857683 | F0 run 5 | 2 | 4 | 1 | ['1'] | OK | 203.596947439 = 203.596947439 |
| 1794881765 | F0 run 6 | 2 | 4 | 1 | ['1'] | OK | 196.477042770 = 196.477042770 |
| 1794925412 | F0 run 7 | 2 | 4 | 1 | ['1'] | OK | 200.350774145 = 200.350774145 |
| 1794939913 | F0 run 8 | 2 | 4 | 1 | ['1'] | OK | 199.491423144 = 199.491423144 |

No missing G1 in any run; nothing goes to the lead as a missing G1, and no verdict changes.
