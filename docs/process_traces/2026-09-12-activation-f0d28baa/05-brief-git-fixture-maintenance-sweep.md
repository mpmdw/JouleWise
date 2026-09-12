# Seat brief — GIT-FIXTURE-MAINTENANCE-SWEEP-01 (kernel rank 99)

WRITE_SCOPE: ["tests/**"]

You are an implementation seat in the linked worktree you were started in
(branch `fix/2026-09-12-git-fixture-maintenance-sweep`, from origin/main
`ace4cc3c`). Fixture hygiene ONLY: no product code (`joulewise/`, `scripts/`)
and no change to any test's assertions (kernel fence). Never run git commands
that move HEAD, never push, never touch `/Users/edr/code/JouleWise` or
`/Users/edr/JouleWise-measurement-20260913-derivation` (a measurement night is
armed there; both are fenced). Two sibling seats are live in other worktrees;
to avoid merge collisions do NOT edit these files even though they are inside
WRITE_SCOPE: `tests/test_calibration_exits.py` (also excluded by the kernel
fence: its two sites at ~:2125-2130 and ~:2660-2668 deliberately force
maintenance ON), `tests/test_controller.py`,
`tests/fixtures/fake_powermetrics_process.py`, `tests/test_run_campaign.py`,
`tests/test_idle_admission.py`. If one of those contains an unhygienic git
init site, LIST it in the report under "deferred sites" instead of editing.

## Problem (kernel row GIT-FIXTURE-MAINTENANCE-SWEEP-01)

Fourth member of one failure family: a detached git maintenance child still
holds a fixture repository when `TemporaryDirectory.cleanup()` /
`shutil.rmtree` removes it. Prior members: EVIDENCE-AUTHOR-GIT-TEARDOWN-01,
PLANTEST-RGLOB-RACE-01 (a28b55bf), the identity-pins teardown race (PR #203).
Read `docs/process_traces/2026-08-26-t26-ci-reliability/README.md` §"What
this cure does NOT cover, and the row that would" first; it enumerates the
still-unhygienic `git init` sites (test_d117_decode_contrast_plan,
test_arm_readiness_pack_digest, test_calibration_bracketing,
test_calibration_live_three_window, test_arm_readiness_evidence, test_bridge,
test_family_marker, and others) and names the existing shared helper that
already applies the tuple.

## Acceptance (kernel)

"The detached-git-maintenance teardown race cannot regrow from any tests/
fixture repository." Evidence: (1) an enumeration test fails if a tests/
module creates a git fixture repository without the four-key tuple, so the
class cannot regrow; (2) every touched module green three consecutive times
at the bench; (3) one green hosted run (the magistrate handles CI).

## Work

1. Enumerate every `git init` call site under `tests/` (subprocess argv
   lists, shell strings, helper wrappers) that creates a repository later
   removed. Paste the list with file:line. Identify the ONE existing shared
   helper that applies the tuple (`maintenance.auto=false`, `gc.auto=0`,
   `maintenance.autoDetach=false`, `gc.autoDetach=false`) — grep for
   `autoDetach` — and route every site through it; do not copy the tuple
   into modules. If no helper exists yet or it lives outside `tests/`, say
   so (NEEDS_SCOPE naming the path if it must change).
2. Add the enumeration guard test (a new module under `tests/`, e.g.
   `tests/test_git_fixture_hygiene.py`): statically scan `tests/**/*.py` for
   git-init sites and assert each is routed through the helper or carries
   the tuple; the two excluded calibration-exits sites are allowlisted BY
   NAME with the fence citation. Killed cut: temporarily strip the tuple
   from one migrated site → guard FAILS; restore bytes (sha256 before/after)
   → PASS. Paste both result lines.
3. Run each touched module three consecutive times (`python -m pytest
   <module> -q`, or unittest if the module needs it); paste the three result
   lines per module. `git diff --check`. Do NOT commit; report
   `git status --short` and `git diff --stat`.

## Report (final message, claude-codex-report/v1 envelope per --genre)

Site enumeration; helper cited (file:line); guard design in two sentences;
killed-cut evidence; per-module 3× results; deferred sites; any
NEEDS_SCOPE/NEEDS_RULING; anything unsure. Under 8000 bytes.
