# Fix-round brief — DOCS-THIN-01 round 1 (Fable review 65: seven unrepaired old-path links; two inaccurate claims in the resume note)

WRITE_SCOPE: ["CLAIMS_STATUS.md","docs/phase_2/three_night_freeze_manifest.md","docs/strategy/2026-08-09-extension-axes-roadmap.md","docs/strategy/2026-08-08-40h-plan.md","docs/strategy/2026-08-14-70h-plan.md","docs/strategy/2026-08-07-three-night-operator-packet.md","docs/process_traces/2026-09-10-side-threads/docs-thin-01-RESUME.md"]

Fix-round seat in the linked worktree you were started in (branch
`chore/2026-09-10-docs-thin`, HEAD 29dbc537 = the archive branch with main
merged). Docs only; NO file moves (a sandboxed seat cannot `git mv` here and
none is wanted); never move HEAD, never push, never touch
`/Users/edr/code/JouleWise`, `/Users/edr/JouleWise-measurement-20260913-derivation`,
or `/Users/edr/night-custody`. A full-suite replay is running in this
worktree in the background — do not run heavy modules; do not start another.
Read first: `../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/65-fable-review-docs-thin-01.md`
§2 and §5, and `docs/legacy/README.md` (the move table; the destination rule
is `docs/X -> docs/legacy/X`, root `Y.md -> docs/legacy/root/Y.md`).

## Work
1. Repair each live link the review lists in §2 "FIX" to the file's new
   location under `docs/legacy/` (verify each target exists with `ls` before
   writing; keep the link text, change only the path):
   `CLAIMS_STATUS.md` L68 and L161; `docs/phase_2/three_night_freeze_manifest.md`
   L52; `docs/strategy/2026-08-09-extension-axes-roadmap.md` L354/L546/L678;
   `docs/strategy/2026-08-08-40h-plan.md` L24/L33; `docs/strategy/2026-08-14-70h-plan.md`
   L20; `docs/strategy/2026-08-07-three-night-operator-packet.md` L6. Do NOT
   touch `docs/paper/**`, `docs/specs/axi/**`, `docs/project_critique_review.html`,
   RUN_STATE.md, TASK_QUEUE.md, decision_log, council_log (edit-excluded or
   "leave as record" per the review).
2. Correct the resume note: "376 git renames" → the true census (review §3:
   309 renames, 7 additions, 5 modifications — verify with
   `git diff --stat -M origin/main...HEAD | tail -1` and `git diff --name-status -M origin/main...HEAD | cut -c1 | sort | uniq -c`);
   and finding 3's "scanned set is byte-identical" → the truth from review §5
   (main scans 459 documents, the branch 402; the 57 dropped are archived
   `.md` files that were never under `process_traces/`, 52 of them in
   `docs/strategy/2026-08-07-paper-portfolio/`); add one sentence saying this
   is intended (archived history leaves the live reference scan) and that
   Ed may veto.
3. Verify: a read-only scan (script under /tmp) that every path you wrote
   exists; `python3 -m unittest tests.test_docs_freshness tests.test_gen_state -q`
   with `/Users/edr/code/JouleWise/.venv/bin/python3`; `python3 scripts/gen_state.py --check`;
   `git diff --check`. Do NOT commit; report `git status --short` and
   `git diff --stat`.

## Report (claude-codex-report/v1 envelope per --genre)
Each repaired link (old → new, file:line); the corrected sentences (quote);
the verification lines; anything unsure. Under 5000 bytes.
