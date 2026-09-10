SESSION_MODE: delegated
WRITE_SCOPE: ["docs/process/state_kernel.json", "TASK_QUEUE.md", "RUN_STATE.md", "docs/process/EXPECTED_IDS.md", "tests/test_gen_state.py", "docs/process_traces/2026-09-10-activation-96bfeca7/13-activation-checklist-2026-09-11.md"]
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Kernel + checklist bookkeeping: the OS-build epoch blocker (gpt-6-astra, high, genre implementation)

Worktree: this one, branch `bookkeeping/2026-09-10-kernel-lanes` (main + activation records). Authority: consult 38 and lead record 39 in
`docs/process_traces/2026-09-10-activation-96bfeca7/` (read both). Facts: macOS updated 2026-09-02 (25F84 → 25G83, new powermetrics binary);
the issued calibration acceptance binds 25F84; `bind-window` refuses `acceptance_artifact_epoch_mismatch`; no installed new-epoch bootstrap route
(the live writer requires a matching issued acceptance before capture); D-102 cl.2 makes re-derivation mandatory; a blind three-seat design consult on
the bootstrap mechanism is running (brief 40); Ed emailed 08:05 PDT (Gmail `1a08bd6ccb79ea1d`) with two decisions and stated defaults.

## Kernel edits (copy the row shape of existing rows; append ranks after the current maximum; keep every generated region regenerated)

1. NEW lane `ACCEPTANCE-EPOCH-25G83-01`, `lane: agent`, `priority: p1_phase_gate`, `status: queued` (or the kernel's active/in-progress value if
   other p1 rows use one). Goal: issue a successor D-079 calibration acceptance under identity epoch os_build 25G83 (and the new powermetrics
   binary) through a governed new-epoch bootstrap: (1) cold-gate ruling on the derivation-only capture route, ledger representation, and the
   pre-registered corpus design (brief 40; Ed owns the scientific rules); (2) implementation under the gauntlet; (3) an agent-free quiet-window
   corpus capture night; (4) derivation + cold science gate; (5) the D-138 atomic successor transaction (carrying the staged R2 patch,
   GATE-R2-COVERAGE-ULP-01); (6) regenerate G2-a inputs and prove `bind-window`/`check` at the desk. Acceptance summary: `bind-window` and `check`
   pass in a fresh clone at the transaction head with the live epoch; the successor's generation is registered in
   `tests/verify_calibration_acceptance_corpus.py`; every prior artifact unchanged; corpus design pre-registered before the first capture; every
   consumer refusal intact. Authority path: record 39. status_note: "2026-09-10: found by the desk dry run in the fresh clone (record 39);
   blocks G2A-FIRST-WINDOW-01; design consult in flight (brief 40, seats 41/42 + Opus); earliest credible calendar per consult 38: corpus night
   09-12, first G2-a 09-14."
2. `G2A-FIRST-WINDOW-01`: add a hard `start` dependency on task `ACCEPTANCE-EPOCH-25G83-01` (state pending) and a dated status_note: "2026-09-10:
   BLOCKED — the 09-12 02:56 arm is off; runbook 68 / checklist 13 arm steps superseded until the successor acceptance is issued (record 39)."
3. `GATE-R2-COVERAGE-ULP-01`: status_note append: "2026-09-10: rides the ACCEPTANCE-EPOCH-25G83-01 D-138 transaction."
4. `NIGHT-REHEARSAL-01`: status_note append: "2026-09-10 08:10: the 09-11 activation still harvests and closes items 5/6 and retires the stub;
   no real plan follows it until ACCEPTANCE-EPOCH-25G83-01."
5. `CLONE-READINESS-01`: status_note append: "2026-09-10: provisional clone re-cut at d84da72e (clean, lock diff empty, ledger authenticated with
   custody replay); the final cut waits for the transaction head."

## Checklist 13 edit (`13-activation-checklist-2026-09-11.md`)

Insert, directly under the title block, a dated SUPERSESSION banner: steps 1–4 (launch email; harvest and inventory `night/` BEFORE 07:00 with the
item-5 predicate §3a; items 5/6 decision; uninstall the stub FROM its checkout and remove checkout + plan root) STAND; steps 5–10 (H, clone, runbook
68, email-then-arm for 09-12) are SUPERSEDED by record 39 — do NOT author, notice or arm any G2-a plan; instead, after step 4, read the newest
activation records (`ls docs/process_traces/2026-09-10-activation-96bfeca7/ | tail`) for the ACCEPTANCE-EPOCH-25G83-01 ruling and, if it is ruled and
implemented, prepare the corpus-capture night per that ruling's runbook; otherwise remain resident on desk work and exit on the watchdog's request.
Keep the rest of the file unchanged.

## RUN_STATE (hand-written region only, above the generated region): add checkpoint `T38j`

Header sentence replacing "**Current checkpoint: T38i …**" and a T38j paragraph: the OS-build finding (record 39), the lane, the superseded arm,
the three-seat design consult in flight, Ed emailed 08:05 with defaults, rehearsal-20260911 still armed and untouched, this activation exits on the
02:31 request; NEXT EXACT ACTION: (this activation) synthesize the design memos → cold-gate ruling packet → implementation seats under the gauntlet
if the ruling and time allow; (09-11 activation) checklist 13 steps 1–4 then the ACCEPTANCE-EPOCH-25G83-01 route. Keep every prior checkpoint verbatim.
Also append one UPDATE line to `docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md` — NOT in your WRITE_SCOPE: STOP with NEEDS_SCOPE
for that one file and the lead will add it; do everything else.

Verification: `python3 scripts/gen_state.py` then `--check` (rc 0), `python3 -m unittest tests.test_gen_state tests.test_docs_freshness` gated on the
process rc. No git commit. Report claude-codex-report/v1, genre implementation, header < 8192 bytes.
