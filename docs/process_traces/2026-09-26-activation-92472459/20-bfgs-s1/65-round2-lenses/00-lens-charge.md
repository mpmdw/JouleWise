# BFG-S S1 round 2 review lenses on `21213be7`

**Candidate.** `feat/2026-09-26-bfgs-s1-bundles` @ `21213be7`. Round 2's delta: `git diff b859317c 21213be7`. Read-only worktree `/Users/edr/code/JouleWise-wt-s1cg-92472459` (detached @ `21213be7`). Base `1417c0c4`.

**Authority:** the round-2 brief `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/20-bfgs-s1/60-round2/10-seat-brief.txt` lists every ruled text with paths: Final texts v1.1 texts 9, 10, 12 (and §E/§F rows T9, T10, T12); amendments 24, 25, 27 where they reach these files; amendment 26 as amended by 42; amendment 36's round-2 rule; amendment 41's round-2 note. The seat report is `60-round2/11-seat-report.md`.

**Check especially:**
- Does every one of text 12's eight consumers call `bundle_read.authenticate_window_members` on exactly the ruled member set, before any energy is read, and propagate `CustodyFailure` without catching it (by name or `except Exception`) and without importing `battery_float` (amendment 36's round-2 rule)?
- Does the AST sweep find every direct read of a bundle's energy files outside the gated paths, with no allowlist row beyond what text 12 and amendment 41 permit? Mutate: add an ungated read in a new module; widen an allowlist row.
- Text 9: can the scored reducer produce a number from a window with a non-pass member? Text 10: can bracketing select a confounded or custody-failed calibration capture, and is the historical cutoff exactly as ruled?
- The 14th guard row: is `CalibrationCandidate` proven, and does the guard stay exact?
- Protected paths byte-identical (FT §E excluded list, `battery_float.py`); no number changes for a pass-verdict or historical bundle (differential: run a representative consumer on committed historical bundles at base and head).

**Output.** Findings tiered BLOCKER / SHOULD-FIX / NIT, each with executed evidence (command + exact tail), production call site, and closure shape; "no findings" per text where so. Edit no repository file; scratch under `/tmp`.
