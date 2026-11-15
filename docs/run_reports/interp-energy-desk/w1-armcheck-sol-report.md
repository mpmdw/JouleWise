Implemented W-1/W-2 on `ops/2026-11-11-w1-armcheck`. Working tree is clean; nothing pushed.

- Changed the arm helper, 14 test modules, timing map, and [run report](/Volumes/JW-EXT/jw-wt/sol-w1-armcheck/docs/run_reports/2026-11-11-w1-armcheck.md). `powermode.py` is unchanged.
- Failing-first evidence is committed. Completed verification: **278 tests passed**, including 19 new tests and all 36 closure/registration tests.
- The test-time cap interrupted `test_r11_delta4_sol2`; **42 modules remain unverified**, listed in the report.
- Commits: `7fbd21e1d`, `084e41d9f`, `77127ac17`, `6c9378b5b`.

**NEEDS_RULING:** May scope expand to adapt `joulewise/align/w1_prequal.py`’s synthetic watchdog fixture? I recommend that adapter; your allowlist excludes the helper. The post-install/dwell conflict also needs the lead’s ruling before integration. Cold review and remote native checks remain pending.

Disclosure: the report records an overly broad ruling read that exposed unrelated B5 prose, and an initial test fixture’s denied host-directory creation attempt. No real custody files were opened.