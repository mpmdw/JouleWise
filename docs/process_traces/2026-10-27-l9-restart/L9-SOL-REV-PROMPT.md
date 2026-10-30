BRIDGE_TASK_V1
{
 "BASELINE_DIGEST": "sha256:aa0eb6954c10a6c72818de45ab6c48b8cf7df12d83cead6dd378ba22d2b9c83c",
 "BASELINE_MANIFEST": ".codex-bridge/baselines/l9-sol-rev-1.json",
 "BASE_HEAD": "f059286bc4d411008002bac62c5cc76cc8c50026",
 "WRITE_SCOPE": [
  ".codex-report/L9-SOL-REV.md",
  ".codex-report/l9-sol-rev/"
 ],
 "TASK_SHAPE": "autonomous",
 "GENRE": "review",
 "ROLE": "execution-lens executing reviewer (Sol half of gate-policy rule 3 two parallel cross-family reviews)",
 "OBJECTIVE": "Return a verdict ACCEPT / ACCEPT_WITH_FIXES / REJECT on the L9 block-5 dry-run driver changes 0576a734d..f059286bc, backed by executed evidence.",
 "AUTHORITY": [
  "docs/process/gate_policy.md (binding)",
  "docs/process_traces/2026-10-27-l9-restart/ED-RULING.md items 1 and 6 (option (c): any 120 s calibration wall-deadline firing must end the run as a classified tooling refusal, never a changed number or a silently dropped unit)",
  "docs/process_traces/2026-10-27-l9-restart/BRIEF.md",
  "docs/contracts/bridge_protocol.md"
 ],
 "ACCEPTANCE": [
  "Report at .codex-report/L9-SOL-REV.md with a verdict line, findings ranked BLOCKER/MAJOR/MINOR/NIT each with file:line and an executed reproduction or a stated reason none is possible",
  "Every claim of a defect is backed by a command you ran and its output",
  "Explicit answer: can any wall-deadline firing anywhere in a dry run (steps 1-11, including NEG-8 replay, bracket refit, step-5 mint, step-2 re-reduction) produce an ok step whose outputs differ from a no-firing run?",
  "Explicit answer: does the shared calibration cache (b5df45a) make any printed output differ from an uncached run when no deadline fires?",
  "Confirm the governed ESTIMATOR_CODE_PATHS (joulewise/powermetrics_fiducial.py, joulewise/reduce.py, joulewise/uncertainty_evidence.py, joulewise/adapters/powermetrics.py) are byte-identical to 0576a734d"
 ],
 "VERIFICATION": [
  "git diff --stat 0576a734d f059286bc",
  "Run targeted short modules: tests.b5_analysis.test_deadline_observer, test_deadline_tripwire, test_shared_physics_cache, test_bracket, test_frozen_files, plus any you write under .codex-report/l9-sol-rev/",
  "Use TMPDIR under /private/tmp with no float-like token in the path (dry_run._FLOAT_TOKEN scans paths)",
  "Do NOT run the full-size tests.b5_analysis.test_dry_run with JW_B5_S10_REAL_PROGRAMS=1: the lead runs that separately on this machine"
 ],
 "EARLY_RETURN": [
  "NEEDS_SCOPE",
  "NEEDS_RULING"
 ],
 "OUTPUT_PROTOCOL": "bridge-report/v1"
}
END_BRIDGE_TASK_V1

Origin: Claude Code lead (laptop). Hop depth 1: do not call Claude by MCP, claude -p, or any launcher.

Context. L9 is the block-5 blind dry-run driver (joulewise/b5_analysis/dry_run.py, steps 0-11). Real block-5 data is
blinded: never open or search for real block-5/6/BYTES data; synthetic fixtures only. The change under review adds
(1) one shared instrument-calibration physics cache per driver run, (2) a step-2 tripwire refusing a re-reduction whose
calibration-dependent summary fields differ from the stored bundle, (3) a run-scoped sys.monitoring observer
(joulewise/b5_analysis/deadline_observer.py) on powermetrics_fiducial.detect_pulses that turns any
projection_budget_trigger == "wall_deadline" into the tooling refusal calibration_wall_deadline_fired for the current
step with no later step running, (4) small fixes (bracket strict validation shares the cache; failed reduce leaves no
output; mint consumption refusal classified). Seat notes are in .codex-report/L9-2.md; read them as claims to test,
not facts. Another reviewer from a different model family is reviewing in parallel; you do not see their result.

Look hard for: paths where a firing is not observed (other callers of the projection, subprocesses or spawned
workers where sys.monitoring does not reach, threads, a monitoring tool id collision, exceptions swallowed before the
step ends); cache key collisions or stale entries that could return another calibration's physics; outputs of a
refused step leaking into later steps or into the unrestricted custody tree; behaviour changes to the no-firing path.
Prefer forcing a firing at a site and showing the outcome over argument. Keep the report short and concrete.
