# 08j — Round 8b ruling: the commit latch (magistrate b0ae8462, 2026-09-15 23:25 PDT)

Round 8 (08i) found the adopted design self-contradictory at one point: `_commit` polled at entry and `_enter(COMMITTED)`
polled again after the clock read, so a signal recorded during the clock read raised at the second poll while the
design's cell 4 expected COMMITTED/0. Ruling: `_commit` = predicate on the clock read → the LAST poll (latch) → direct
assignment of COMMITTED (no `_enter`). A signal recorded during the clock read rolls the verified-but-uncommitted
install back with the signal's code (D6 protects only COMPLETED results); a signal after the latch is ignored. Cell 4
splits into 4a (clock hook → ROLLED_BACK, signal code) and 4b (after the latch → COMMITTED 0). Round 8b also carries
the Opus seat's extras (handlers installed in `main()` before `parse_args`; zero `pthread_sigmask` calls pinned by grep;
CLI returncode ≥ 0 cell; PEP 475 cell; child-mask cell; seam × signal product; must-die 1–8). The Astra consult seat
(13/04) agreed on record-and-poll and CLI SIG_IGN through exit but kept a mask variant; not adopted (2 of 3 seats plus
the child-inherited-mask finding).
