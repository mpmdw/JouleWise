SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["docs/process/state_kernel.json", "TASK_QUEUE.md", "tests/test_gen_state.py"]

# Kernel registration 2 (bookkeeping) — activation d0b83820, 2026-09-19 afternoon

Cwd is a detached worktree at the bookkeeping branch head (`git log -1`). Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree. Do not commit; the lead copies the files back and commits. Follow the precedent commits `7b667147` + `95c82e59` + `272d39ff` (this morning's registration): edit `docs/process/state_kernel.json` (source of truth), run `python3 scripts/gen_state.py` (default mode regenerates the marker regions) then `python3 scripts/gen_state.py --check` (must print nothing / exact), and — the step this morning's seat missed — add the new ids to `EXPECTED_IDS` in `tests/test_gen_state.py` with a dated comment block and update the `assertEqual(len(self.tasks), N)` line with the running-count sentence (211 → 213). Run `python -m unittest tests.test_gen_state tests.test_docs_freshness` and paste the tail. Ed's plain register: a technical reader with no project grounding; define every term at first use; no bare lane ids or record numbers in description text.

## Register (next free ranks)

1. `STAGE-A-EVIDENCE-EXECUTOR-01` — P1 Phase Gate — ACTIVE [AGENT]. The evidence campaign for the night gate's quiet-admission cutoff (the busy-core threshold no ruling has yet activated) needs an unattended executor: cold gate packet 10 (records `docs/process_traces/2026-09-19-activation-d0b83820/10-coldgate-packet-stage-a-executor/`, adjudication `10a-…`) ruled a separate evidence payload under an unchanged v2 diagnostic plan, a digest-keyed ruled-registration table in the night gate bound by the chain-source digest, a typed evidence probe receipt dispatched by one `NIGHT_PAYLOAD_KIND` export (a contract amendment to `docs/process/NIGHT_HANDBACK.md` and the runbook's verify-only probe row), a new authoring tool `scripts/gen_evidence_night.py`, and a frozen idle-only pilot protocol (twelve 600 s envelopes with a 480 s interior, δ = 1 J, block two sized from the upper confidence bound on the paired spread, a pre-registered "no cutoff qualifies" branch). Implementation is on branch `feat/2026-09-19-stage-a-evidence-executor` (parts 1–2 landed; part 3 = the sizing statistic); next = refuters, delta re-audit, counter-review, full replay, PR, then pilot night one under NIGHT_HANDBACK.
2. `CI-SHARD-RUNNER-FILE-BASED-01` — P3 Tooling — READY [AGENT]. The hosted continuous-integration shard runner feeds its test script to Python on standard input, so any test that starts a worker with multiprocessing's spawn method fails on Linux (`FileNotFoundError: '<stdin>'`: spawn re-imports the main script, which is not a file). Two macOS bench tests were guarded darwin-only as a fix-forward (PR #363); a file-based or importable shard runner would let hosted Linux exercise the load worker's join ladder and pipe cleanup. Deliverable: extract the inline runner to a file, preserve shard selection and exit behaviour, validate on hosted Linux.

## Notes (append a dated note)

- `QUIET-PREDICATE-EVIDENCE-01` (A232): 2026-09-19 afternoon — harness merged (PR #360, main `0c529f99`); the executor lane above carries the campaign; the harness now records the OS build and per-round AC/thermal probe results in every row (part 1 of the executor branch).
- `GENERATOR-HEAD-FILE-BYTE-PIN-01` (A244): 2026-09-19 — RETIRE by removal: PR #362 merged (main `42d3849e`) — the two live floor v5 generators bind to the acceptance cutoff by the D-109 prefix relation; frozen generators unchanged. (Retire = remove the row; count 211 − 1 + 2 = 212.)
- `TEST-WRITES-PAPER-BUILD-ARTIFACT-01` (A247): 2026-09-19 — observed again in every delegated seat this activation (the artifact is untracked/ignored; the seat wrapper flags it as unowned dirty).

Count line: 211 − 1 + 2 = 212 (one retired, two registered).

## Report

`claude-codex-report/v1` envelope for `--genre implementation`; ranks assigned; `gen_state.py --check` exact; the two test modules' tails; `git diff --stat`.
