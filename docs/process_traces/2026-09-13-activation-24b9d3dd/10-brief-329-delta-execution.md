# Delta re-audit brief — PR #329 DOCS-THIN-01 fix round 1, EXECUTION lens (Astra high; workspace-write sandbox for temp dirs, WRITE_SCOPE [])

SESSION_MODE: delegated
WRITE_SCOPE: []

You are in the detached review worktree at the PR #329 head after fix round 1 (`git rev-parse HEAD`; the fix-round delta is `git diff -M ae5b09e7..HEAD`; the PR base is `a4bb8838`). You may run commands and tests (temp dirs allowed) but must not edit tracked files; the tree must end clean. Never touch `/Users/edr/code/JouleWise` (read-only use of its `.venv/bin/python3` allowed), any `/Users/edr/JouleWise-measurement-*` directory, or `/Users/edr/night-custody`. No network.

The round claims to cure (fix contract `docs/process_traces/2026-09-13-activation-c5048879/10-brief-329-fix-round-1.md` in `/Users/edr/code/JouleWise-wt-bk-c5048879`, read-only; refuter reports 06 and 09 and triage 13 beside it; the seat report is `docs/process_traces/2026-09-13-activation-24b9d3dd/09-fix-329-round-1b-astra-report.md` in `/Users/edr/code/JouleWise-wt-bk-24b9d3dd`, read-only):
- FIX-1 (should-fix): `RUN_STATE.md:6-9` cited `docs/process_traces/RESUME-2026-07-2{6,7,8}.md` while 27/28 were archived; cure = archive the 26 sibling too (pure rename, byte-identical), README row + totals, sentence repaired.
- FIX-2 (should-fix): three live pointers repaired to `docs/legacy/...` targets.
- FIX-3 (nit): trailing whitespace on branch-added lines removed.
- FIX-4: dated resume note.

Try to BREAK the delta:
1. Rename purity: `git diff -M100% --diff-filter=R --name-status ae5b09e7..HEAD` shows exactly one R100 (the 26 sibling) and `git diff -M ae5b09e7..HEAD --stat` shows no content change to it; `git show HEAD:docs/legacy/process_traces/RESUME-2026-07-26.md | wc -c` = 13223 and equals the sha256 of `git show ae5b09e7:docs/process_traces/RESUME-2026-07-26.md`. Paste.
2. README arithmetic: recompute the move table's file count and byte total mechanically (sum the Size column; count the Files column) and compare with the header sentence (310 files, 83,134,998 bytes, 79.28 MiB = bytes / 1,048,576 rounded to 2 dp). Any mismatch is should-fix; paste the computation.
3. Live references, delta only: for the three repaired lines and the RUN_STATE sentence, `test -e` each new target from the repo root (and the HTML href relative to `docs/`). Then re-run the round-0 live-reference census (old paths of ALL moved files grepped as literals across `docs/` excluding `docs/legacy/` and dated `docs/process_traces/` records, `configs/`, `scripts/`, `joulewise/`, `tests/`, `.github/`, root docs, `docs/process/state_kernel.json`) and report every remaining hit with file:line and its classification (runtime path = blocker; living doc = should-fix; dated record = nit, accepted by policy `docs/legacy/README.md:16`).
4. Is `docs/process_traces/RESUME-2026-07-26.md` pinned anywhere (state_kernel.json, gen_state, tests, scripts)? `rg -n "RESUME-2026-07-26"` over the tree excluding `docs/legacy/`; a runtime pin is a blocker.
5. Run and paste tails: `python3 scripts/gen_state.py --check` rc; `python3 -m unittest tests.test_docs_freshness tests.test_gen_state`; `python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint tests.test_paper_comparison_placements tests.test_paper_reported_energy tests.test_paper_custody`; `git diff --check a4bb8838..HEAD` (must be rc 0 now); `git status --short` empty.
6. Non-docs fence: `git diff --stat a4bb8838..HEAD -- . ':!docs' ':!*.md'` still shows ONLY `tests/test_docs_freshness.py` (+2) — paste.

One line at the end: same signature as a round-0 finding (a live reading surface still pointing at a moved path)? YES/NO and why.

Report (claude-codex-report/v1, genre review) as your FINAL MESSAGE, findings severity-tiered with file:line, pasted evidence, the same-signature line, and "what the lead should double-check". Under 8000 bytes.
