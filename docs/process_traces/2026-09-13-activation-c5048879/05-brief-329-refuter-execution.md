# Refuter brief — PR #329 DOCS-THIN-01, EXECUTION lens (Astra high, read-only on tracked files)

SESSION_MODE: delegated
WRITE_SCOPE: []

You are in a detached review worktree at HEAD `ae5b09e7` (PR #329's branch
`chore/2026-09-10-docs-thin` with origin/main `27957b60` merged in). The PR's
diff against main is `git diff 27957b60..HEAD` (use `-M` for renames). You may
run commands and tests (temp dirs allowed) but must not edit tracked files; the
tree must end clean. Never touch `/Users/edr/code/JouleWise` (read-only use of
its `.venv/bin/python3` allowed), any `/Users/edr/JouleWise-measurement-*`
directory, or `/Users/edr/night-custody`. `python3 -m unittest` only; no sudo;
no network.

Context: the PR archives 309 historical documents under `docs/legacy/` by one
mechanical rule (`docs/X -> docs/legacy/X`; repo-root `Y.md ->
docs/legacy/root/Y.md`), restores five trace items and `docs/stream_logs/`
because `docs/process/state_kernel.json` pins them, adds
`docs/legacy/README.md` as the archive front door with the full move table,
repairs live links to moved files, and makes ONE code change: two lines in
`tests/test_docs_freshness.py` so the live reference scan skips `docs/legacy/`.
The owner accepted "merge the archive as is". A prior Fable review (record 65)
and a fix round (67) exist under
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/`.

Try to BREAK it, in this order:
1. Non-docs fence: `git diff --stat 27957b60..HEAD -- . ':!docs' ':!*.md'` must
   show ONLY `tests/test_docs_freshness.py` (+2). Paste. Quote the two lines.
2. Pure renames: with `git diff -M100% --diff-filter=R --name-status
   27957b60..HEAD` count the 100%-similarity renames; then list every path in
   the diff that is NOT a 100% rename and is under `docs/legacy/` (a modified
   file that was also moved = content changed during archival: should-fix
   unless the change is a link repair the PR names). Compare the count with
   `docs/legacy/README.md`'s move table (count its rows mechanically).
3. Live references: build the list of moved SOURCE paths (old paths) and grep
   each, as a literal, across the non-legacy tree: `docs/` excluding
   `docs/legacy/`, `configs/`, `scripts/`, `joulewise/`, `tests/`, `.github/`,
   `AGENTS.md`, `CLAUDE.md`, `README.md`, `RUN_STATE.md`, `TASK_QUEUE.md`,
   `AGENT_PLAN.md`, `docs/process/state_kernel.json`. Exclude
   `docs/process_traces/` dated 2026-08-15 or later ONLY IF the PR's rule says
   dated records keep historical links (quote where it says so; else count
   them). Report every hit with file:line. A hit in the kernel, a contract, a
   runbook, `docs/process/NIGHT_HANDBACK.md`, `MAGISTRATE_RELAUNCH_PROMPT.md`,
   `NIGHT_COURIER_PROMPT.md`, `MAGISTRATE_WATCHDOG.md`, scripts or tests is a
   BLOCKER (a runtime path the machine reads); a hit in a living doc is
   should-fix; in a dated record, nit.
4. Rule fidelity: list any archived path that does NOT match the rule (a
   docs/process_traces directory dated ON or AFTER 2026-08-15; anything under
   docs/process/, docs/contracts/, docs/phase_2/; any file the kernel or
   `gen_state` reads). List any pre-2026-08-15 trace directory that was NOT
   archived and whether the PR names why (kernel pin).
5. Run: `python3 -m unittest tests.test_docs_freshness tests.test_gen_state`,
   `python3 scripts/gen_state.py --check`, and
   `python3 -m unittest discover -s tests -p 'test_doc*.py'` (if that pattern
   finds more modules) — capture to a file, paste the summary lines from the
   file; `git status --short` empty.
6. Merge hygiene: main moved after the PR's replay (a merge commit
   `ae5b09e7` brought in 09-12/09-13 records). Confirm the merge added no
   file under `docs/legacy/` and moved nothing new.

Report (claude-codex-report/v1, genre review) as your FINAL MESSAGE: findings
tiered blocker / should-fix / nit with citations and concrete failing
scenarios; explicit "no blocker found" plus a "checks performed" line if none.
Under 8000 bytes.
