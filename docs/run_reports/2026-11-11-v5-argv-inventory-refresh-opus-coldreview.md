# Cold review: `826f90e04` (v5 qualification argv inventory follows 99a90e9c6)

Independent Opus subagent, read-only, 2026-11-11. **Verdict: ADMIT.** No findings.

1. `99a90e9c6` turns `run_night` into a closer-managing wrapper around `_run_night` (`scripts/run_night.py:4755`,
   `:4831`); both argv assignments (`['/bin/zsh', '-c', 'sleep 2; echo REHEARSAL']`, `['/bin/zsh', str(chain_path)]`)
   now live in `_run_night` and none in `run_night`.
2. One file, 10 lines in and 10 out: all other keys unchanged; the two rows are renamed and moved to the emitted
   order; JSON formatting preserved (`json.dumps(indent=2)` plus trailing newline).
3. `governed_callsite_inventory()` now differs from the fixture only by the two courier rows
   (`_publish_terminal_result` and its nested `run`, `c80d4d638`, `scripts/run_night.py:1630, 1643`), which stay
   unlisted because they belong to the three governed calls parked for the research lead (P3).
