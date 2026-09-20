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

Plan IDs retain `qpe01-pilot-n1-YYYYMMDD` for handbook/courier compatibility.
A preparation stamp includes local date/time, epoch and full H. Measurement
roots are `/Users/edr/JouleWise-measurement-<stamp>-qpe01-pilot-n1`, staging
is `/Users/edr/night-plan-staging/<plan_id>-<stamp>/`, and custody is
`/Users/edr/night-custody/<plan_id>-<stamp>/`. `--roots-under` replaces
`/Users/edr` for both measurement and custody; `--staging-under` replaces the
staging parent. These two overrides support isolated offline fixtures.
Symlink components, overlapping roots and locations inside Git worktrees are
refused, preserving canonical and other-checkout fences.

Preparation checkpoints selection before cloning, then:

1. Clone the remote without hardlinks, detach at H and verify main ancestry.
2. Build Python 3.13's `.venv`, install `.[mac]` and the three bench extras
   under `env/mac-measurement-lock.txt`, and compare the complete sorted
   non-comment lock with `pip freeze --exclude-editable`. Record interpreter
   path, version and binary SHA-256. An internal builder callable is the test
   seam together with an injected lock verifier; there is no CLI switch that
   skips the lock. Offline composition uses an interpreter symlink and does
   not establish that a real locked venv was installed.
3. Verify HEAD H, detached checkout and empty porcelain including untracked
   files. Author the v2 `DIAGNOSTIC_NO_PACK` plan with the clone's
   `write_night_plan`, repo-relative `PROTOCOL_PATH`, and 9000-second window.
4. Run the clone's real generator with `--render-only`. Per ruling 22a,
   it creates the custody root, wrapper, both sidecars and manifest. The
   boundary is **custody root exists without night_plan.json**. The plan
   remains in staging; prepare never publishes it.
5. Run the clone's real shell installer with the clone venv interpreter and
   `--render-only <staging>/render/`; obtain the driver's `schedule(plan)`.
6. Freeze `prepare.json`, including the triple, paths, all sealed digests,
   interpreter identity, timestamped step ledger, schedule and notice draft.
   Print that JSON and stop. The draft makes no acceptance/clearance claim.

`prepare.json` identifies owned work, and is atomically checkpointed after
completed steps. A staging lock serializes competing callers. Before resolving
`next` or omitted H again, find a single matching prior preparation (same
remote/location inputs and matching explicit selection inputs). Multiple
matches refuse. Completed reruns verify and print the saved record without
rewriting it, the plan, render outputs or custody artifacts. This preserves
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
preparation, lock mismatch, dirty or moved checkout, and sealed-byte drift.
Executor refusals propagate as a preparation refusal. Existing artifacts are
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
