```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"partial","summary":"Execution review found six bench-fidelity and reuse gaps.","workspace":{"base_requested":"bd17126b","base_mode":"exact","head_start":"bd17126b","head_end":"bd17126b","upstream_end":"bd17126b","branch":"feat/2026-09-20-evidence-night-entry"},"pathspec":[],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"should_fix"},{"id":"F2","severity":"should_fix"},{"id":"F3","severity":"should_fix"},{"id":"F4","severity":"should_fix"},{"id":"F5","severity":"should_fix"},{"id":"F6","severity":"nit"}]},"verification":[],"flags":[{"id":"A1","kind":"verification_gap","level":"nonblocking","text":"Brief 22 and ruling 22a absent.","needs":"Lead reconciles authority."}]}
```

## Findings

No confirmed blocker. Repository unchanged; HEAD and upstream remained `bd17126b`.

**F1 — should_fix — Preparation accepts a candidate guaranteed to be stale at t0.**  
`joulewise/evidence_night.py:318–339` checks current age but drops step 2’s upper bound `t0-authored <= 129600`. Executed preparation accepted a **133184-second** interval and recorded `complete`. Evaluating that exact plan at t0 with probe functions that forbid hardware access returned **`REFUSED night_plan_stale`**. Restore the upper planning bound before sealing. This finding does not reinstate the separately retired 40-minute publication gate.

**F2 — should_fix — Lost ownership evidence is bypassed by `--t0 next`.**  
At `evidence_night.py:201–225`, discovery considers only existing `prepare.json` files. Executed: prepare with `next`, delete its record, advance the parent clock 120 seconds, repeat the same request. It **created another complete candidate**, selecting `1789917300` instead of `1789917180`, while the orphaned plan and custody artifacts remained. With explicit t0/H, deletion correctly refuses. Detect unidentified matching preparations before resolving a replacement default.

**F3 — should_fix — Same-filesystem publication check disappeared.**  
Step 2 and its helper compare staging/custody `st_dev`; preparation and delegated render validation do not. Executed differential fault injection: make staging’s `Path.stat().st_dev` differ, then resume. Preparation returned `complete`; the original bench helper refused **`same-device atomic publication`**. This was a simulated device mismatch, not a mounted second filesystem. Restore the check before declaring the candidate prepared.

**F4 — should_fix — No shell syntax validation of the sealed wrapper.**  
`evidence_night.py:330–344` omits step 2’s `/bin/zsh -n`. Executed generator-output fault injection appended `)` and updated the wrapper sidecar before checkpointing. Real installer render-only accepted it; preparation recorded **`complete`**. The original syntax check returned exit 1, **`parse error near ')'`**. Hash consistency and manifest validation do not replace syntax validation.

**F5 — should_fix — Stamped directories preserve a downstream identity collision.**  
`evidence_night.py:123–130` gives different same-day candidates the same `plan_id`. Executed candidates had distinct custody roots but both mapped to **`night-results/qpe01-pilot-n1-20260920`**. `scripts/run_night.py:1059–1100` derives both its results branch and destination directory solely from that ID; the courier likewise promises one results branch per plan. Record 01 already identifies retained results under this date’s ID. Directory stamping therefore fixes local collisions without fixing result identity. A successor could encounter a conflicting results branch; no push was attempted. Lead should reconcile unique successor IDs with the claimed courier compatibility.

**F6 — nit — Remaining step-1 procedural omissions are undocumented.**  
The observed argv omit `python3.13 --version` and the bench’s **post-build `git fetch origin main`**. Interpreter identity is still returned correctly, and ancestry is checked against the clone’s fetched `origin/main`, so these are narrower visibility/freshness differences. Document the intentional substitutions or retain the bench operations.

**Fidelity and successful checks.** Executing the original step-2 authoring heredoc with identical inputs/time produced **exactly the same JSON fields and values**: v2/schema version 2, `DIAGNOSTIC_NO_PACK`, repo-relative protocol, 9000-second window, heads, roots, chain paths, and authored time. There are no new plan fields. Both serialize `authored_epoch_s` as **float**, because `NightPlan.from_mapping` converts the integer authoring input. Entry and installer interpreter identities were equal.

The Python 3.13 venv recipe, constrained editable `.[mac]` install, three extras, and sorted complete freeze comparison match the bench recipe. The 40-minute lower bound is no longer enforced at authoring: explicit ~20-minute and simulated slow-build ~37.6-minute candidates completed. Consult 18 makes 40 minutes a planning default; this is an intentional policy difference, unlike F1’s missing upper bound.

**Custody consumers.** Stamped names themselves passed:

- `NightPlan.from_mapping`, driver preflight/schedule, manifest/registration checks, publication-safe bench checks, and installer render validation.
- Installer admission refused the staged path with `plan_outside_custody_root`, then admitted the scratch-published plan at the stamped custody path.
- Watchdog `Storage.glob_plans()` found nothing before scratch publication, then found the stamped plan; `load_plans()` returned one plan and no errors.
- Courier argv contained the actual stamped custody root.

Watchdog discovery uses `root.parent.glob("*/night_plan.json")`; installed-plan inspection also reads plist `--plan`. The v2 gate does not require custody basename to equal `plan_id`. Record 17’s exact retained-root listing would reject additional roots, but consult 18 expressly replaces that gate. Records 01/85 provide manual harvest conventions, not a basename validator; F5 is the concrete remaining identity issue.

**Resume, clocks, fences.** The executed matrix confirmed:

- Completed rerun: identical record, digests, mtimes, and authored time.
- One changed chain byte: `sealed-byte drift`.
- Deleted record with explicit selection: foreign/uncheckpointed-output refusal.
- Partial clone and removed `.git/HEAD`: refusal without adoption.
- Two overlapping invocations: second refused `concurrent preparation`; first completed.
- Both Los Angeles DST-fold occurrences refused; `next` skipped to 02:00. Spring-gap selection advanced to 03:00. Exactly now+2400 seconds was accepted.
- Driver install close was t0−600. Resume exactly at close refused `exclusive install close has passed` **without changing the completed record**. This correctly refuses reuse; it does not invalidate or rewrite the historical record.
- Literal `/tmp/...` refused because `/tmp` is a symlink. Tests pass because they call `.resolve()`, yielding `/private/tmp/...`.
- Roots inside the scratch checkout refused. The default fence examines destination ancestors, not cwd; invoking from a worktree does not itself fence `/Users/edr`.

**Executed evidence and argv inventory.** Artifacts are retained under [the scratch evidence directory](/private/tmp/enreview.nigteCS0). The focused suite passed **12 tests**:

```sh
env PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_night
```

Cwd: `/private/tmp/enreview.nigteCS0/copy`. Additional executed scripts: `review.py`, `extra.py`, `finalchecks.py`, `intercept.py`, and `real.py`; corresponding logs preserve observations.

The complete injected-builder run recorded **46 interception events, 25 distinct normalized argv**. Parent/descendant Python audit hooks and forbidden-command PATH shims observed no launchctl, mail, chain execution, collector, or power process. Exact argv, including full `-c` bodies, are in [all-argv.jsonl](/private/tmp/enreview.nigteCS0/all-argv.jsonl). With `R=measurement_root`, `S=staging`, `P=R/.venv/bin/python`, `M=local remote`, and `H=pinned HEAD`, they were:

```text
git ls-remote M refs/heads/main
git clone -q --no-hardlinks M R
git -C R checkout -q --detach H
git -C R merge-base --is-ancestor H refs/remotes/origin/main
git -C R rev-parse HEAD
git -C R rev-parse --abbrev-ref HEAD
git -C R status --porcelain=v1 --untracked-files=all
P -B -c <interpreter identity code>
P -B -c <plan authoring code> <state JSON>
P -B scripts/gen_evidence_night.py --plan S/night_plan.json --render-only
P -B -c <plan age validation code> S/night_plan.json
R/scripts/install_night_agent.sh --plan S/night_plan.json --python P --render-only S/render
P -B - R/scripts/run_night.py P
P -B -m joulewise.night_agent_install --plan S/night_plan.json --python P --render-only S/render
/usr/bin/git -C R rev-parse HEAD
P -B R/scripts/run_night.py preflight --plan S/night_plan.json
P -B -c <schedule/boundaries code> S/night_plan.json
/usr/bin/git -C R show H:<file>
```

The last form occurred separately for eight files: pilot protocol JSON; `scripts/night_chains/quiet_predicate_evidence.zsh`; `scripts/sample_quiet_predicate_evidence.py`; `joulewise/quiet_admission.py`; `joulewise/quiet_predicate_campaign.py`; `joulewise/night_gate.py`; `joulewise/night_agent_install.py`; `scripts/run_night.py`.

Builder argv, separately captured in `recipe-argv.json`:

```text
python3.13 -m venv .venv
P -B -m pip install -q -c env/mac-measurement-lock.txt -e .[mac]
P -B -m pip install -q -c env/mac-measurement-lock.txt charset-normalizer requests urllib3
P -B -m pip freeze --exclude-editable
```

The real offline builder executed the first two and refused after 4.15 seconds because cached build dependencies lacked `setuptools>=61`. Extras/freeze recipe capture used an intercepted runner; no real locked-environment success is claimed.

**Same-signature statement:** The class **“the entry point silently diverges from the bench procedure it replaces” is present**: F1/F3/F4 have differential failure evidence; F6 records narrower procedural drift. I cannot establish a repeated post-fix occurrence from this first reviewed slice. Next step: lead adjudicates these findings and the missing authorities, then requires differential regressions against the bench checks.

## Residual risk

Brief 22 and ruling 22a were absent from the allowed worktree, so authority reconciliation remains incomplete. No other worktree was inspected. Real-builder descendants were not comprehensively traced after pip failed; successful process interception covered the injected-builder composition. No full canonical suite, live hardware validation, launchd operation, email, network access, or result publication was performed.