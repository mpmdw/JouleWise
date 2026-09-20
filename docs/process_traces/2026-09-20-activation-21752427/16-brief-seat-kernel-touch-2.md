SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["docs/process/state_kernel.json", "TASK_QUEUE.md", "RUN_STATE.md", "tests/test_gen_state.py"]

# Kernel touch 2 (activation 21752427): retire the two delivered lanes, register two successor lanes, refresh the pointer

Cwd is the linked worktree `/Users/edr/code/JouleWise-wt-kernel2-21752427` on branch `bookkeeping/2026-09-20-kernel-touch-2-21752427` at main `980f8d64` (contains every record cited). Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree. Interpreter `/Users/edr/code/JouleWise/.venv/bin/python`. No git commits/pushes (the lead commits by pathspec), no network, no launchctl. Do not end your turn before the report.

The previous kernel touch by this activation is the exact template: `git show a5ea3383 --stat` and `git show a5ea3383 -- docs/process/state_kernel.json tests/test_gen_state.py` (seat 04 + bench closure; brief `docs/process_traces/2026-09-20-activation-21752427/04-brief-seat-kernel-touch.md`, report `04-seat-kernel-touch-astra.md`). Follow the same conventions: retirement = removal (as history does); ranks/gaps as the kernel's convention; regenerate BOTH generated regions with `scripts/gen_state.py` (no arguments = generate; `--check` must exit 0 afterwards); update `EXPECTED_IDS` in `tests/test_gen_state.py` with a dated comment in the established form; `python -m unittest tests.test_gen_state -q` must pass (44 tests). RUN_STATE.md: touch ONLY its generated region (the generator does it) — never edit the hand-written blocks above it.

## Edits (facts bench-verified by the lead)
1. RETIRE `CENSUS-SELF-MATCH-01` (rank 0): delivered by PR #371, merge `980f8d64` (2026-09-20 05:46 PDT). Evidence: records 03/05/10/11/12/13/14/15 in `docs/process_traces/2026-09-20-activation-21752427/` (12 = diff gate + replay 6,614 tests + terminal review). Preserve closure evidence the way a5ea3383 did for 254/255 (a note on a dependent lane if the convention keeps one).
2. RETIRE `CI-LEGACY-FIXTURE-LINUX-01` (rank 259): delivered by PR #370, merge `d8e6761f` (05:00 PDT); post-merge matrix run 35509175943 SUCCESS incl. `test (3.11, 3)`. Evidence: records 02/06/07/08.
   After these two: 220 − 2 = 218 tasks before the additions below.
3. ADD `WATCHDOG-COURIER-PATH-HOLD-01` — priority `p3_tooling` (or the vocabulary's equivalent); lane `agent`. Goal: the night driver's own argv carries `--courier-bin /Users/edr/.local/share/claude/versions/…`, which the census regex matches from an INDEPENDENT producer (the watchdog's `production_census` inside the plan span → `HOLD_CENSUS` "production census non-empty inside plan span" at 00:43:45 PDT 09-20 on driver pid 79018; never fatal to the night, but a false hold/notice every night). Cure direction: census-safe courier configuration (a path or indirection that does not contain an agent name), not output filtering. Evidence: record 10 (refuter 10 F2) and record 01 §1. Status `queued`.
4. ADD `TEST-FIXTURE-HOST-PATHS-01` — priority `p3_tooling`; lane `agent`. Goal: remaining test fixtures that name host files: `tests/test_magistrate_watchdog_cli.py:198` `chain_path="/bin/true"` (latent: its module never reaches the installer's UTF-8 reader; refuter 06 item 4 executed a binary substitution, three tests still pass) and `tests/test_install_night_agent.py:110` fixed `chain_sha256_path="/tmp/install-night-agent-test.sha256"` (inert today per Opus 07 finding 1's executed trace). Acceptance: every plan fixture path lives under the test's temporary root. Evidence: records 06 and 07. Status `queued`.
   After the additions: 218 + 2 = 220 tasks.
5. `INSTRUMENT-CADENCE-25G83-01` (257): keep `blocked`; its dependency text now reads: the successor pilot night, which is armable once the operational precondition in RUN_STATE's 05:10 block is met (canonical checkout `/Users/edr/code/JouleWise` contains merge `980f8d64`; no stale resident supervisor) — cite record 12 §5 and record 14.
6. `updated` → 2026-09-20; `latest_report` → `docs/process_traces/2026-09-20-activation-21752427/12-diff-gate-census-self-match.md` with a label in the existing form ("T38n — 2026-09-20: census self-match cure merged (PR #371); pilot night one aborted, harvested, uninstalled").

## Verification (paste tails)
- `/Users/edr/code/JouleWise/.venv/bin/python -B scripts/gen_state.py` (generate) then `--check` → exit 0.
- `PYTHONDONTWRITEBYTECODE=1 …/python -B -m unittest tests.test_gen_state -q` → OK.
- Task count = 220; `git diff --stat`; the diff of `RUN_STATE.md` must be confined to the generated region (paste `git diff RUN_STATE.md | head -20`).

## Report
claude-codex-report/v1 envelope for --genre implementation; `pathspec` = files changed; NEEDS_RULING for any convention you cannot determine; JSON header under 800 bytes; total under 8 KB.
