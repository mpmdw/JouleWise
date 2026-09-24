VERDICT: MERGE

# Cold Fable final pass — A294+A295, merge candidate 69fd5daf (base bd80d169)

Judge: Claude Fable 5.1, fresh non-interactive session, worktree `wt-a65fb4fa-fable-pr` (branch at bcd93668, record commits only; merge-base with 69fd5daf is bd80d169). Auto-loaded before the charge: global `~/.claude/CLAUDE.md`, project `CLAUDE.md`, and the harness memory index `MEMORY.md`. None was consulted for this ruling. CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, council logs and memory files were not read. No sudo, launchctl, powermetrics, networksetup; no canonical root, custody root, measurement clone or LaunchAgents touched. Read-only apart from this file and throwaway copies under /tmp.

## Method (all executed this session)
- `git diff bd80d169..69fd5daf`: 9 files, +371/-32. Production delta is confined to `_check_static_start` in `joulewise/night_gate.py` (one new probe block after the HEAD match), the timeout branch of `_probe_runner` in `scripts/run_night.py`, and one string in `joulewise/arm_retry.py`. No name, signature, constant or registry changes.
- `git archive` copies at /tmp/fp-base and /tmp/fp-head. The head copy was given a throwaway `git init` commit plus an objects alternates pointer into this worktree's object store so the legacy-regression test (`git show a90ab4e8:…`) and the kinds tests (which clone ROOT) could run. No write to any shared repository.
- Named modules at head: `tests.test_night_gate` + `tests.test_arm_retry` 133 OK; `tests.test_night_kinds` 14 OK (158 s); `tests.test_run_night` 232 OK (157 s) when run alone. A first run of `test_run_night` concurrently with `test_night_kinds` reported 1 failure; its name was not captured because the output was tailed. The solo rerun was clean. This is consistent with the charge's pre-existing load flake but I did not confirm the identity of the failing test.
- Real-git probes (`/tmp/fp-probe.py`) using `scripts.run_night.make_probes().run` and `.measurement_head` against a temp clone, run at BOTH trees:

| scenario | base bd80d169 | head 69fd5daf |
|---|---|---|
| clean clone | proceeds | proceeds; C5 `measurement_checkout_porcelain=[]`; status citation in C5 evidence |
| tracked edit ` M joulewise/mod.py` | proceeds (defect) | `night_plan_stale`, detail names root + line, probe in refusal evidence |
| untracked `?? joulewise/shadow.py` | proceeds (defect) | `night_plan_stale`, line named |
| only ignored `__pycache__/` residue | proceeds | proceeds (ignored files are not porcelain output) |
| corrupt `.git/index` (rev-parse HEAD still works) | proceeds | `night_probe_error`, exit 128, porcelain key `None` |
| `core.fsmonitor` hook that touches a marker | n/a | proceeds, marker NOT created; a plain `git status` in the same clone DOES create it (proves `-c core.fsmonitor=false` is what suppresses the hook) |
| status times out with partial invalid-UTF-8 stdout/stderr | n/a | `night_probe_error`, exit 124, stderr carries `�` + timeout text, stdout partial retained in evidence |

- Receipt identity: `evaluate_night(make_plan(), FakeProbeSource().probes())` at base and head → both GO; JSON identical after removing the two new C5 measured keys and the status citation. A full `evaluate_night` on a real REHEARSAL_STUB clone at both trees (refused at the live census because my own shell is a forbidden process, the same at both) is identical after the same projection plus the run-specific temp path, fixture commit id and census pids.
- Consumers of `night_plan_stale` (grep over joulewise/ and scripts/): the gate registry and ORDER (unchanged), `night_agent_install.py` (plan-age refusal at install time, unrelated to clone state), and `arm_retry.DISPOSITIONS` → `cold_gate`. `ZERO_CAPTURE_MACHINE_REFUSALS` does not contain it, so `terminal_zero_capture_refusal` returns `not_zero_capture_machine_refusal`; no automatic successor. The watchdog imports only `NightPlan, ProbeResult, PLAN_MAX_AGE_S, PlanError, agent_census` from night_gate and never evaluates the gate itself; all five names exist unchanged at head.
- Pack-night ordering: `_author_pack_arm` and `author_arm_readiness_evidence_t0` write only under `custody_root/<pack_id>/…` (arm_readiness_evidence_t0.py lines 2295-2379; run_night.py 1954-1987), and `night_dir = custody_root / "night"`. Nothing the driver writes before `evaluate_night` lands inside `measurement_root`, so the new probe cannot see driver residue. Rehearsal roots are required disjoint from production roots (night_gate 1117-1146). `evaluate_static` runs once per bind (phase starts at `'static'`, line 2597, and is never re-entered), so the check runs before the chain, never after it has written.

## Q1 — MERGE on 69fd5daf
Every scenario in the charge behaves as specified at head and every defect scenario passes silently at base. Refusal precedence is preserved: the status probe runs only after the HEAD match (`test_measurement_head_mismatch_skips_checkout_status`), the census is still the first command probe for the legacy evaluator only in the sense the driver caches it (run_night 3061-3066); the missed-fire guard remains the first probe of `_check_static_start`. The `except Exception` around the probe block correctly routes `_run`'s malformed-result `ProbeError` and any probe exception to `night_probe_error` with the accumulated evidence. `if checkout_status.stdout:` (not `porcelain`) means a stdout of bare whitespace would refuse; git never emits that, and refusing on unexpected bytes is the fail-closed direction.

## Q2 — reuse of `night_plan_stale`: correct and sufficient
The code already means "the plan no longer describes the machine it was armed for"; a dirty clone is exactly that. The arm_retry description, both code tables (NIGHT_HANDBACK.md and the runbook §appendix) and the runbook §0.8 passage now name the clone cause, the t0 mechanism (untracked files included, fsmonitor disabled), both codes, and the remedy (find the writer, re-cut; re-arming does not repair). Tests pin all three surfaces to the same sentence. Disposition `cold_gate` is the right automated behaviour: a clone written to after arm needs a human/cold look, not an auto-retry, and the receipt carries up to 50 porcelain lines so the cold gate can see what changed. One note, not a blocker: the runbook's arm-time command is still `git status --porcelain` (default untracked mode, which collapses whole untracked directories to one line). That is fine for an operator eye, and t0 uses `--untracked-files=all` for the record.

## Q3 — bench commit 69fd5daf: correct, no further delta pass needed
Test-only, 15 lines. The exact-50 boundary test asserts all 50 lines kept and no truncation key (kills `> 50 → >= 50`); the timeout test now writes `\xff`/`\xfe` on both streams and asserts `�` on each (kills strict decoding on either stream). I re-derived the same three mutants from the production code and each is now observable by the named tests; my own timeout probe independently reproduced the replacement-character path. Nothing in the bench commit touches production. The rule-11 bench fix is upheld: the finding class was already characterised by the delta re-audit, the fix is mechanical, and executed evidence exists.

## Q4 — watchdog and armed-night paths after merge
No break. The watchdog's import surface is unchanged and it does not call the gate. The driver's import list (`NIGHT_DRIVER_REASON_CODES, NIGHT_GATE_REASON_CODES, NightPlan, PlanError, ProbeResult, Probes, agent_census, evaluate_night`) is unchanged and the registry-overlap assertion still holds. A night armed against an older plan would only see the new probe at its t0; the magistrate's post-night porcelain on the five recent real clones (0 lines each, not repeated here) is the evidence that a healthy clone passes. Nothing is armed now.

## Q5 — anything missed
- The probe's stdout is retained in full in the refusal evidence (only the C5 `measured` copy is capped at 50 lines and the detail at 5). A pathological clone with thousands of untracked files would produce a large receipt; refusals are written once, so this is size, not correctness. Acceptable.
- A `GIT_DIR`/`GIT_WORK_TREE` environment leak into the driver would misdirect `git -C <root> status`; the pre-existing `measurement_head` probe has the identical exposure and would refuse first on HEAD mismatch. Not new.
- Ignored files (e.g. `*.egg-info/`, `__pycache__/`) inside the clone are invisible to the probe by design; the arm-time procedure and the D-127 clone recipe already cover them. A `.gitignore` edit in the clone would itself be a tracked edit and refuse.
- The `test_run_night` fake answers clean for any status argv on the planned root; that is a fake, so pack-night t0 behaviour against a REAL clone is proven only via `_check_static_start` real-git tests plus my probes, and via the write-location trace above. Sufficient for merge.

## Ruling
MERGE 69fd5daf into main as-is. No fix-first items. Post-merge: hosted CI as confirmation per the standing post-merge rule; the full-suite replay tail the magistrate is running belongs in the PR body.
