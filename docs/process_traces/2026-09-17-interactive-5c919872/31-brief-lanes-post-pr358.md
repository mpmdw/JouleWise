SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["docs/process/state_kernel.json","tests/test_gen_state.py","RUN_STATE.md","TASK_QUEUE.md"]
BASE_HEAD: b55909e3
BASELINE_MANIFEST: .codex-bridge/baselines/mag-5c919872-lanes-post358-0125.json
BASELINE_DIGEST: sha256:e0c2617981008264f113441016528833390ee1239c861002cd303e1b06efd9a6
LEASE_ID: lease-bb169e7869c34d48a5a88ff2aa498bad

# Seat brief — post-merge kernel bookkeeping for PR #358 (NIGHT-GATE-QUIET-ADMISSION-01 merged)

Worktree `/Users/edr/code/JouleWise-wt-bk-post358`, branch `bookkeeping/2026-09-18-post-pr358` at `b55909e3` (origin/main, the merge commit of PR #358). Do NOT commit (the lead commits by pathspec). Never touch `/Users/edr/code/JouleWise`, any other worktree, `/Users/edr/JouleWise-measurement-*`, `~/Library/LaunchAgents`, or `/Users/edr/night-custody`. No network. `RUN_STATE.md` and `TASK_QUEUE.md` may be changed ONLY inside their generator-owned marker fences and only by running `python3 scripts/gen_state.py`; hand-edit nothing else in those two files.

## Task

In `docs/process/state_kernel.json` (shape of the most recent registrations at ranks 231–234, `git show 0a95ad53 -- docs/process/state_kernel.json`; row vocabulary from ranks 222–234):

1. **Retire NIGHT-GATE-QUIET-ADMISSION-01 (rank 231) by removal**, the way merged lanes are retired (see the test comment convention: "closes … by removal"). Its merge: PR #358 → main `b55909e3`, head `fbee905d` (code identical to `13d53ce2`), full replay 6425/0/0 (`docs/process_traces/2026-09-17-interactive-5c919872/25-full-replay-13d53ce2.log.gz`), twelve-row ledger on the PR.

2. **Register THREE follow-up lanes** at ranks 235–237, authority label "registration by the magistrate (interactive session 5c919872), not a ruling", each glossing its terms at first use for a reader who has never seen the night driver:
   - Rank 235 — `BIND-REQUEST-PAYLOAD-CAP-01` (lane `agent`, status `queued`, priority `p3_hardening_candidates`). Goal: the bind loop's worker processes receive their request on the command line (`scripts/run_night.py` `_bind_argv`, the `--request` argument carrying the whole static receipt as JSON), the one uncapped payload crossing a process boundary in a design that caps the result frame at 256 KiB; a request over the kernel's argument-length limit fails closed to `night_probe_error`, which is not in D-182's eligible successor set, so such a night would get no successor. Acceptance: pass the request through a capped channel (the same framed pipe, or a bounded file the worker reads), refuse before launch when the request exceeds the cap with a distinct detail, regression with a synthetic oversized static receipt; existing supervision tests unchanged. Evidence: `docs/process_traces/2026-09-17-interactive-5c919872/29-opus-counter-review-13d53ce2.md` finding S1 (cite its lines).
   - Rank 236 — `QUIET-JOURNAL-REPLAY-CONTRACT-01` (lane `agent`, status `queued`, priority `p3_hardening_candidates`). Goal: the journal writer (`_BindJournal` in `scripts/run_night.py`) replays existing `quiet_samples.jsonl` bytes at start and seeds `samples_total` from them; that equals this night's count only because the v4 write-once record set refuses a rerun when the journal exists — load-bearing and undocumented. Acceptance: state the invariant in `docs/contracts/night_quiet_admission.md` (Supervision subsection) and in a code comment; a regression that plants a foreign journal in the night directory and asserts the driver refuses the rerun rather than counting foreign samples. Evidence: record 29 finding S2.
   - Rank 237 — `TEST-BIND-SUPERVISION-ENV-SENSITIVITY-01` (lane `agent`, status `queued`, priority `p3_tooling`). Goal: in the round-4 delta re-audit (`docs/process_traces/2026-09-17-interactive-5c919872/27-delta-reaudit-round-4-astra.md`, flag G1) two of the auditor's six-module runs hit the `journal_block` external watchdog at 178 s and 174 s when the inherited `PYTHONPYCACHEPREFIX` pointed under `/tmp`; unsetting it made the suite green; the lead's native runs never hit it. Acceptance: find the coupling (the FIFO/barrier fixture path or worker interpreter start-up under a cold bytecode cache), pin it so the test's outcome does not depend on the cache location, and record the measured start-up cost; existing tests unchanged. Evidence: record 27 flag G1; record 28 §G1.

3. Add a `status_note` to QUIET-PREDICATE-EVIDENCE-01 (rank 232): "2026-09-18 interactive 5c919872: the merged sampler's `--observation` mode is the driver's worker entry (needs `--job-id` and `--result-fd`, writes a framed envelope); sampling for this lane goes through the flagless smoke CLI (`python3 -B -m joulewise.quiet_admission --sample-interval-s 30`, whole-round observer cost 1.15 cpu-s per 30 s round on the desktop) or a harness that supplies the pipe; quote no observer floor from the worker mode (cold-gate ruling 71 Q5)."

4. Regenerate the fenced regions (`python3 scripts/gen_state.py`), prove `python3 scripts/gen_state.py --check` exits 0, and update the row-count assertion in `tests/test_gen_state.py` (currently 200) with the prepended comment in the existing convention: "2026-09-18 (interactive session 5c919872, PR #358 merged): retires NIGHT-GATE-QUIET-ADMISSION-01 by removal and registers BIND-REQUEST-PAYLOAD-CAP-01, QUIET-JOURNAL-REPLAY-CONTRACT-01 and TEST-BIND-SUPERVISION-ENV-SENSITIVITY-01: 200 − 1 + 3 = 202."

## Verification you must run and paste
1. `python3 scripts/gen_state.py` then `python3 scripts/gen_state.py --check; echo rc=$?` (must be 0).
2. `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_gen_state 2>&1 | tail -3`.
3. `git status --short` (only the four in-scope paths) and `git diff --stat`.

## Report
claude-codex-report/v1 envelope under 8000 bytes: changed files, the retirement and three ranks, the test tail, line numbers cited. Do not guess field values; if the schema rejects a field, report the validator message and stop.
