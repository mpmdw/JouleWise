# Evidence night entry: prepare (PR 1, slice A)

`python -m joulewise.evidence_night prepare --kind quiet_predicate_evidence
--t0 <epoch|next> [--head H] [--remote URL] [--roots-under DIR]
[--staging-under DIR]`

Authority: consult 18, record 19 §1 and ruling 22a in
`docs/process_traces/2026-09-20-activation-21752427/`. This is preparation
only; successful preparation is neither notice acceptance nor arm clearance.

The only scientific selection inputs are kind, t0 and H. The default remote
is `https://github.com/mpmdw/JouleWise`; omitted H is resolved once by
`git ls-remote REMOTE refs/heads/main`. H must be a full 40-character Git SHA
and reachable from remote main. Explicit epochs must be future, whole,
unambiguous local minutes. `next` selects the first unambiguous local minute
at least 40 minutes away; 40 minutes is a planning default, never an extra
publication gate. The unchanged installer retains its schedule/age refusals.

Plan age has two preparation checks (ruling 25a). Before creating any clone
directory, the running entry checkout's `joulewise.night_gate.PLAN_MAX_AGE_S`
rejects `t0 - now > PLAN_MAX_AGE_S`. At authoring inside the clone, H's
`night_gate.PLAN_MAX_AGE_S` rejects `t0 - authored_epoch_s > PLAN_MAX_AGE_S`
before writing the plan, using the exact authoring timestamp stored in it.
**The clone-side authoring check binds.** Both checks refuse with
`REFUSED: t0 is beyond the plan's maximum age at authoring`. The constant is
currently 129600 seconds; completed resumes retain the existing sealed-plan
age check without reauthoring.

Plan IDs are `qpe01-pilot-n1-YYYYMMDD-HHMM` (local t0), giving same-day
candidates distinct courier results branches and probe labels.
A preparation stamp includes local date/time, epoch and full H. Measurement
roots are `/Users/edr/JouleWise-measurement-<stamp>-qpe01-pilot-n1`, staging
is `/Users/edr/night-plan-staging/<plan_id>-<stamp>/`, and custody is
`/Users/edr/night-custody/<plan_id>-<stamp>/`. `--roots-under` replaces
`/Users/edr` for both measurement and custody; `--staging-under` replaces the
staging parent. These two overrides support isolated offline fixtures.
Symlink components, overlapping roots and locations inside Git worktrees are
refused, preserving canonical and other-checkout fences. Staging and custody
parents must have equal `st_dev` for atomic publication; parents are created
before comparing, before cloning.

Preparation checkpoints selection before cloning, then:

1. Run `python3.13 --version`, clone the remote without hardlinks, detach at H,
   run `git -C R fetch -q origin main`, then verify main ancestry.
2. Build Python 3.13's `.venv`, install `.[mac]` and the three bench extras
   under `env/mac-measurement-lock.txt`, and compare the complete sorted
   non-comment lock with `pip freeze --exclude-editable`. Record interpreter
   path, version and binary SHA-256 using the clone’s
   `night_agent_install.interpreter_identity` via its interpreter. An internal builder callable is the test
   seam together with an injected lock verifier; there is no CLI switch that
   skips the lock. Offline composition uses an interpreter symlink and does
   not establish that a real locked venv was installed.
3. Verify HEAD H, detached checkout and empty porcelain including untracked
   files. Author the v2 `DIAGNOSTIC_NO_PACK` plan with the clone's
   `write_night_plan`, repo-relative `PROTOCOL_PATH`, and 9000-second window.
4. Run the clone's real generator with `--render-only`. Per ruling 22a,
   it creates the custody root, wrapper, both sidecars and manifest. The
   boundary is **custody root exists without night_plan.json**. The plan
   remains in staging; prepare never publishes it. Before checkpointing the
   wrapper and on every sealed resume, run checks with `P -B -c` in the clone:
   wrapper SHA equals sidecar; manifest equals `manifest_for(plan)` and its
   wrapper binding; source literal equals tracked chain bytes at H; the ruled
   registration binds that source; plan-path literal names the published
   custody plan; `/bin/zsh -n` succeeds. H’s code judges H’s artifacts.
5. Run the clone's real shell installer with the clone venv interpreter and
   `--render-only <staging>/render/`; obtain the driver's `schedule(plan)`.
6. Freeze `prepare.json`, including the triple, paths, all sealed digests,
   interpreter identity, timestamped step ledger, schedule and notice draft.
   Print that JSON and stop. The draft includes registration and source digests,
   local/UTC/epoch install-span boundaries, and attempt N derived as one plus
   the number of other records sharing the date prefix. It lists prior
   candidates; it does not infer earlier aborts or acceptance/clearance.

`prepare.json` identifies owned work, and is atomically checkpointed after
completed steps. A nonblocking flock at
`<staging_under>/.locks/<plan_id>-<stamp>.lock` precedes the first candidate
staging write; contention refuses as `concurrent preparation`. Before resolving
`next` or omitted H again, find a single matching prior preparation (same
remote/location inputs and matching explicit selection inputs). Multiple
matches refuse. Staging candidate directories without readable `prepare.json`
and unpublished custody roots not referenced by any record refuse as
`unidentified prior preparation output: <path>` before resolving defaults.
Completed reruns verify and print the saved record only until the exclusive
install close; after that close, reuse refuses without altering the record.
Verification never rewrites the plan, render outputs or custody artifacts. This preserves
`authored_epoch_s`, digests and mtimes. Every checkpointed output is verified
before any next step. HEAD, clean status, exact lock and interpreter identity
are checked again. No reauthoring or regeneration repairs drift.

An interrupted step with no outputs can resume. Uncheckpointed conflicting
outputs (including a partial clone, venv, plan, generator or installer render)
refuse; preserve them for lead inspection. Never adopt an unknown directory
or silently delete partial evidence. A published plan, any custody additions
or invocation records end preparation reuse. State is local ownership evidence,
not an authenticated defense against deliberate alteration of the state file.

Refusals exit 2 with one `REFUSED:` line: invalid/unresolved kind, malformed H,
H unavailable from remote main, invalid/non-minute/ambiguous/past t0, foreign
root or staging, symlink/path collisions, unknown prior ownership, concurrent
preparation, lock mismatch, dirty or moved checkout, sealed-byte drift,
`exclusive install close has passed`, `sealed plan stale or future-authored`,
`unknown prior-preparation step ledger`, cross-filesystem publication,
unidentified prior output, and `sealed candidate failed <check>`.
Executor refusals propagate as a preparation refusal. Unexpected exceptions
exit 1 with `ERROR: <type>: <message>` and a traceback on stderr. A runway
below 2400 seconds prints `WARNING: runway below the 40-minute planning default`
and continues; this warning is not a refusal. Existing artifacts are
never overwritten to recover. There is no mail, launchctl, probe, chain,
collector, power sampler, install or automatic publication operation here.

The adopted KEEP inventory remains binding at its owning lifecycle phase:
root ownership/retention and fences; raw bracketed census and workload review;
locked environment, pinned source/manifest and ruled registration; v2/no-pack,
plan age/schedule/records and job-state checks; receipt identity/freshness and
cleanup/consent checks; full `arm_retry` refusal routing. This slice delegates
render validation to unchanged executors. Pre-arm discovery, census, canonical
ancestry/supervisor checks, readable NO/directives/STOP, notice acceptance,
publication, launchd probe/install/verification and uninstall recovery remain
bench obligations. No exact-four-root gate, calendar restriction, attempt cap,
notice delay, calibration ledger or epoch input is introduced.

Slice B owns the lifecycle façade, handbook/runbook replacement and pre-arm
checks. Fixture preparation proves composition only; evidence stays PROVISIONAL
until the owning live gates pass.
