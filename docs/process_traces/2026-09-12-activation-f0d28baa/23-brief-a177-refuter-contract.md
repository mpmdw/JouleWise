# Refuter brief — A177 landing (PR #324), CONTRACT lens

SESSION_MODE: delegated
WRITE_SCOPE: []

Read-only refuter (you may run tests; never edit tracked files; tree must end
clean). Branch `fix/2026-09-12-fixture-sentinel-controller`, HEAD `c85a171d`,
one commit over origin/main `ace4cc3c`: `git diff ace4cc3c..HEAD`. The
execution-lens refuter already passed it (report 10) — do NOT repeat that
lens. Reports beside this brief in
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/`:
03 (seat brief), 04 (seat report), 10 (execution refuter). Root cause:
`docs/process_traces/2026-09-10-activation-96bfeca7/19-rootcause-controller-idle-drift-local-astra-report.md`;
the prior cure: PR #310 / consult 87. Never touch `/Users/edr/code/JouleWise`
or `/Users/edr/JouleWise-measurement-20260913-derivation` (fenced).
`python3 -m unittest` only.

Your lens is the CONTRACT: kernel row FIXTURE-SENTINEL-CONTROLLER-01 in
`docs/process/state_kernel.json` (goal, acceptance, fences) and consult 87's
ruling on the bounded `--no-sleep` policy.
1. Quote the kernel row's acceptance text and map each clause to the diff
   (file:line) or say "not met". "third instance of the host-timing fixture
   class (87, 99, 19) recorded" — where must that record live per the row
   (a comment in the test? a process doc?) and is the comment at
   `tests/test_controller.py` ~:1631 sufficient?
2. Consult 87 / PR #310: find its ruling text (grep `consult 87` /
   `no-sleep` in docs/) and confirm the policy the adapter override now
   encodes (append `--no-sleep` only when `count is not None`) is the SAME
   policy consult 87 ruled, not a widening (e.g. does consult 87 restrict
   the cure to campaign tests only, or to the retry fixture generally?).
   A widening beyond the ruling is a blocker.
3. Does any contract doc or decision-log entry describe fixture sentinel
   behaviour, `FAKE_POWERMETRICS_SLEEP_SCALE`, or the stress floor 3.5, such
   that the test's `patch.dict` pin needs a ONE-home citation? cite or say
   none.
4. Fence: "production deadlines and strict comparisons unchanged" —
   `git diff ace4cc3c..HEAD --stat -- joulewise scripts` must be empty
   (paste).
5. Is the removed campaign-helper patch's explanatory comment (the "delta
   re-audit 79 F1 refuted the round-1 pin" history) preserved anywhere, or
   is provenance lost? A lost provenance note is a nit with the exact
   sentence to restore.

Report (claude-codex-report/v1, genre review): findings tiered
blocker / should-fix / nit with citations; explicit "no blocker found" if
none. Under 8000 bytes.
