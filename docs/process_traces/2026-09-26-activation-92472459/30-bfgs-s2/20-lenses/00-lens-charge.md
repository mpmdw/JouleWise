# BFG-S S2 review lenses (round 1) on `4ea4b26b`

**Candidate.** Branch `feat/2026-09-26-bfgs-s2-qpe-collector` @ `4ea4b26b` = main `1417c0c4` + the S2 seat commit `fcf9cfd9` (Sol 6.0 xhigh, committed unchanged) + one lead bench commit (the sweep assertion admits `quiet_pre/quiet_post`). Read-only worktree for lenses: `/Users/edr/code/JouleWise-wt-s2lens-92472459` (detached @ `4ea4b26b`). Diff: `git diff 1417c0c4 4ea4b26b`.

**Authority** (absolute paths under `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/`): the seat brief `2026-09-26-activation-92472459/30-bfgs-s2/10-seat-brief.txt` lists every ruled text S2 implements, with paths: Final texts v1.1 texts 5, 6, 15 and §E/§F; addendum-2 amendment 20; addendum-3 erratum amendments 32, 33, 34 (and 30 as merged context); QPE-SHAPE3 erratum ruling §5 (amendment 35 restated, rows T6-f to T6-v) and §3 B-6 (row X-1). The seat's report is `30-bfgs-s2/11-seat-report.md`.

**Standing constraints to check:** custody is never a status (every `CustodyFailure`/`CustodyUnreadable` propagates; no summary written on a custody raise); authentication precedes every exclusion decision except amendment 32 item (1)'s no-record carve-out; `joulewise/battery_float.py`, `joulewise/evidence_night.py`, `joulewise/night_gate.py`, `configs/campaigns/quiet_predicate_evidence_01/**`, `scripts/night_chains/**` byte-identical to base; registration digest `69321c69…` unchanged; no exclusion reason added or removed; the collector adds no new exit path.

**Output.** Findings tiered BLOCKER / SHOULD-FIX / NIT, each with executed evidence (command + exact output tail), the production call site, and an exact closure shape. State "no findings" per ruled item where that is your result. Edit no repository file; scratch under `/tmp`.
