# Evidence night entry: preparation and lifecycle (slices A and B1)

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

1. Clone the remote without hardlinks, detach at H,
   run `git -C R fetch -q origin main`, then verify main ancestry.
2. Probe `python3.13 --version` (inside the venv builder, so an injected
   offline builder needs no python3.13; a missing interpreter therefore
   surfaces after the clone, with the clone checkpoint recorded and
   resumable), then build Python 3.13's `.venv`, install `.[mac]` and the three bench extras
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

The installer's render-only path itself runs the driver preflight
(`scripts/run_night.py preflight --plan`, refused as "night driver preflight
failed"), so the bench step-2 preflight is exercised without a separate call.
The bench scripts' hard 40-minute floor at authoring is superseded by the
runway warning (consult 18: a planning default, not a gate). Further
refusals not listed below, all sealed-state checks on resume: "unknown or
uncheckpointed staging output", "unknown or missing render output",
"published, invoked or unknown custody output", "interpreter identity
drift". The exclusive-install-close refusal runs last, after the clone and
venv; a candidate prepared too late still pays that cost before refusing.

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
never overwritten to recover. `prepare` has no mail, launchctl, probe, chain,
collector, power sampler, install or automatic publication operation here.

The adopted KEEP inventory remains binding at its owning lifecycle phase:
root ownership/retention and fences; raw bracketed census and workload review;
locked environment, pinned source/manifest and ruled registration; v2/no-pack,
plan age/schedule/records and job-state checks; receipt identity/freshness and
cleanup/consent checks; full `arm_retry` refusal routing. This slice delegates
render validation to unchanged executors. Slice B1 below supplies pre-arm
discovery, census, canonical ancestry/supervisor checks, publication,
probe/install/verification and uninstall recovery. B2 below supplies the notice
draft and mechanical veto checks; Gmail transport and mailbox reading remain
magistrate obligations. No exact-four-root gate,
calendar restriction, attempt cap,
notice delay, calibration ledger or epoch input is introduced.

Fixture preparation and lifecycle tests prove composition only; evidence stays
PROVISIONAL until the owning live gates pass.

## Slice B1: checks and the installer façade

```
python -m joulewise.evidence_night check --candidate STAGING
python -m joulewise.evidence_night publish-install --candidate STAGING --notice-accepted MESSAGE_ID
python -m joulewise.evidence_night verify --candidate STAGING
python -m joulewise.evidence_night uninstall --candidate STAGING
```

Authority: consult 18; records 19 §1, **21** (superseding the latest-HEAD-move
predicate), 26 §4, 27 and 28; `NIGHT_HANDBACK` Census and ARM-RETRY-POLICY;
record 17 steps 0, 4, 5 and `evidence-checks.py`. The installer, census,
retry policy and driver remain unchanged. B1 is a mechanical façade for the
lead's bench procedure. `armable` means the implemented checks passed at the
recorded observation time; it is not notice/veto clearance or quiet-machine
validation. The lead must review workloads, stop/directive channels and all
readable NO relays, then leave with every owned helper before REQUEST.

All four lifecycle commands expose the installer's `--launchctl-bin`
seam. `check`, `publish-install` and `verify` record `launchctl_bin`; any value
other than literal `launchctl` records `fake_launchctl: true`. A fake-launchctl
run is a **rehearsal, never armable**: check sets `armable: false`,
`rehearsal_ready: true` only when its checks pass; publication requires that
matching fake executable and records `outcome: rehearsal_installed`,
`installed: false`. Such records cannot authorize a real arm.

Each successful subcommand except `notice` prints one JSON object and exits 0;
`notice` prints To and Subject headers, a blank line, then the sendable body. A known
refusal prints one `REFUSED:` line and exits 2; an unexpected defect prints
`ERROR:` plus its traceback and exits 1. Installer refusals retain their
captured return codes and output in the attempt journal. A nonblocking flock
on `<staging_under>/.locks/<candidate-name>.lock` serializes both preparation
and lifecycle operations for a candidate (one lock domain).
No command fast-forwards or repairs a checkout.

`check` first verifies all sealed digests, render inventory, detached clean H,
locked environment, interpreter identity and the clone's wrapper/manifest/
registration checks. It checks plan identity, age and exclusive install close
with the clone's code. It then writes verdicts and evidence for:

0. Refuse ANY loaded `com.joulewise.night*` label, using label discovery and
   the clone installer's typed liveness for both fixed labels and discovered
   labels; UNKNOWN refuses. Any night plist or retained `.plist.prior` sidecar
   under `~/Library/LaunchAgents` refuses, including symlinks. Paths come from
   the installer's `LABELS` and `Target` methods. Cause:
   `REFUSED: night agents already loaded or plists present: …`.
1. Candidate H contains `980f8d6452fb6923644bdac1e243ce0a344c881f`.
   The canonical checkout contains **candidate H** and has empty
   `git --no-optional-locks status --porcelain -uno`. Untracked canonical
   files do not fail that check; tracked modifications and observation errors do.
2. `/Users/edr/night-custody/magistrate/state.json` supplies
   `resident_session.supervisor_pid`. Null, an absent PID, or a reused PID
   whose command no longer names `magistrate_watchdog.py` is clear.
   Records 19/21 govern `CENSUS_FIX` and this predicate: **every arm needs a
   supervisor started after the canonical fast-forward**. A live
   supervisor must have started strictly after the oldest reflog entry from
   which HEAD continuously contains H. Walk newest to oldest and stop at the
   first non-containing entry; a rewind/re-add starts a new interval. Missing,
   unparseable or unreadable evidence refuses. A start equal to arrival refuses.
3. `shutil.which("claude")` finds the courier executable required by the
   unchanged installer. This checks availability; it never invokes the courier.
4. Every `<roots_under>/night-custody/*/night_plan.json` is inventoried and
   must be a regular non-symlink file; directories and special files refuse.
   A root whose `night/chain.started` is a regular file without a regular
   `night/chain.exited` is ACTIVE and refuses. Otherwise an existing regular
   `night/courier.sent`, `night/result.json`, `night/chain.exited`, or any
   regular file matched by `run_night._refusal_paths` (`refusal.json`,
   `refusal-N.json`, `calibration-refusal.json`,
   `calibration-refusal.json.*.json`) classifies its root as retained; the
   record lists every marker found. Otherwise it is UNKNOWN and refuses.
   A retained root whose plan span is still active by the watchdog's rule
   (`scripts/magistrate_watchdog.plan_span_active`, evaluated on that root's
   own `night_plan.json` at observation time) is ACTIVE and refuses; a root
   whose plan does not parse, or whose `custody_root` is not its own
   directory, is UNKNOWN and refuses. Each row records its reason.
   Discovery never removes a root, and has no fixed root count. Retention
   classification does not certify process liveness or completed delivery.
5. The exact raw bracketed `night_gate.AGENT_CENSUS_ARGV` result is retained
   alongside `arm_census.observe_arm_census` and `classify_arm_census` evidence.
   The argv derivation and ancestry classification execute inside the clone's
   `P -B -c` interpreter, with JSON out; test observers inject data only.
   Every raw PID must resolve to owned, foreign, workload or unknown evidence.
   An absent raw PID triggers one re-observation, then
   `REFUSED: unresolved raw census hit pid N`; unknown evidence also refuses.
   A raw row without a parseable PID refuses as
   `REFUSED: unresolved raw census row: …`.
   Any FOREIGN PID, observed workload or unresolved observation diagnostic
   refuses. Real-class `publication_blocked == False` is not clearance.
   Owned ancestry PIDs are listed with the departure instruction.
6. Existing `<staging>/lifecycle/attempts.json`,
   `<staging>/lifecycle/arm-attempts/*/attempts.json` and B1 install journals
   are inventoried through `arm_retry.classify_abort` inside the clone's
   `P -B -c` interpreter, with JSON in/out and cwd set to the clone. Unknown or
   cold-gate causes refuse. A bare installer nonzero is **not** relabeled
   `arm_transport`. This is refusal routing, not a call to `retry_allowed`:
   fresh notice and veto evidence for that function belongs to B2/the bench.
   A non-list attempt inventory refuses as `malformed attempt inventory: …`;
   notice-reuse discovery refuses unreadable or malformed attempt records as
   `malformed attempt journal: …`.

Lifecycle artifacts are under `<staging>/lifecycle/`: `check.json`,
`install.json`, `uninstall.json`, `attempts.json`, and `arm-attempts/`.
Retry inventory and prior-notice discovery read attempt records only from this
directory. Candidate-root `attempts.json` and `arm-attempts/` (the bench
§1.4a journal location) are never read: `check`, `publish-install` and the
notice-reuse check refuse "attempt records at the candidate root" (fail
closed, naming the lifecycle home), and their presence makes `prepare` refuse with
`unknown or uncheckpointed staging output`. `prepare` owns and ignores
this mutable directory; it is not sealed, so `prepare → check → prepare`
continues to verify and print the preparation record. Besides the shared lock,
`check` writes only its lifecycle verdict, including a failing verdict. Every
lifecycle JSON write uses a fsynced temporary file plus `os.replace`, sharing
preparation's checkpoint helper.
Sealed-byte failure stops host probes. It preserves `prepare.json` and all
sealed bytes/mtimes. Python callers may inject a canonical fixture repository,
supervisor state path, subprocess probe runner, census observer/caller PID and
lock verifier. These are offline test seams, not CLI clearance overrides.

`publish-install` requires `check.json` bound to the current `prepare.json`,
literal `armable: true`, matching literal `launchctl`, and an mtime strictly
newer than `prepare.json` and every sealed artifact. Both the recorded finish
time and file age must be at most 60 minutes (future finish times refuse).
Sealed state is checked before freshness stats: a missing staged plan after
publication is a known refusal (exit 2), never an uncaught missing-file error.
It rechecks sealed state and the time boundary. It
requires a nonblank notice acceptance ID. A notice ID present in a prior
attempt of this candidate or any same-date-prefix candidate under
`<staging_under>` refuses with `notice id already used by attempt …`.
**The ID is recorded verbatim and is not verified.** B1 sends no mail and
reads no notice thread. B2 observes network directives both in `veto` and
immediately before publication. The caller retains responsibility for the
handbook observations;
passing an ID must not be represented as proof that they occurred. `publish-install` repeats the veto observation and the loaded-jobs probe at the publication boundary and requires a fresh `check` record; the lead re-runs `check` after any change.

The staged plan and custody root must be on one filesystem. A published
`night_plan.json`, including a dangling symlink, refuses. Publication uses
`os.replace(staged_plan, custody/night_plan.json)`, then checks byte equality.
From the clone, the façade calls `scripts/install_night_agent.sh --plan
PUBLISHED --python CLONE/.venv/bin/python --launchd-probe`, then the same
command without `--launchd-probe` to install, then verifies. Probe and install
are separate executor operations. The unchanged installer validates the
evidence receipt's identity, cleanup and freshness (less than six hours),
including `probe_label(plan_id)`, before admission. B1 records its SHA-256.

Each publication attempt gets an exclusively created
`lifecycle/arm-attempts/NNNNNN/` directory, exact `plan.json` snapshot and
`install.json` journal. `lifecycle/install.json` is the latest view; prior terminal journals
are preserved. Records contain notice ID/verification status, timestamps,
command argv/return codes/output, plist paths, probe receipt digest,
verification and recovery outcome. The record includes pre-publication typed
liveness for both labels, repeats step 0 immediately before publication, and
durably records phase `publishing` before the plan rename. Phase transitions
and parseable installer refusal `cause` are persisted atomically. There is no
automatic retry loop or inference of a retry-eligible cause; interrupted/failed
records go to the lead.

| Phase | Operation about to run or just completed |
|---|---|
| `prepared` | Attempt snapshot recorded; loaded-jobs probe must clear. |
| `observing-veto` | Boundary veto observation in progress; no publication intent yet. |
| `publishing` | Boundary veto cleared with required provenance; durable intent immediately before the plan rename. |
| `published` | Plan rename acknowledged. |
| `probing` / `probe_finished` | Installer probe in progress / returned. |
| `installing` / `install_finished` | Installation in progress / returned. |
| `verifying` | Installed-state verification in progress. |
| `recovering` | Post-publication recovery in progress. |
| `complete` | Successful installation or completed restoration. |

A refused or timed-out boundary veto leaves phase `observing-veto` and outcome
`not_published`; it never reaches `publishing`.

Recovery never uninstalls jobs it did not install. The unchanged installer
transaction's rc 2/3 means refused or rolled back: retained teardown overrides
these with rc 1/4. In particular `night_agent_already_loaded`, pre-bootstrap
refusals, successful rollback and probe-only failures do **not** invoke
`--uninstall`; the journal says `foreign_jobs_preserved` and names the retained
pre-publication state. Only confirmed successful installation (rc 0) followed
by a failure permits the clone's `--uninstall`, whose exit must be 0.
Unknown/interrupted install ownership or failed rollback retains state for the
lead without destructive cleanup, refusing as
`installer ownership/rollback unknown; jobs and plists preserved`.
Only when published bytes still equal the
saved bytes and the original staged path is absent may `os.replace` restore
them to staging. Changed/missing bytes, conflicting staged output or failed
cleanup retain state and name paths in the refusal. Probe evidence remains.
An exception before publication never runs uninstall. Hard process death
can leave a nonterminal journal; recovery is lead-controlled, never presumed.

`verify` checks the published sealed candidate (ruling 30a). It executes the clone's
`LaunchctlAdapter.print` for both labels and requires typed LOADED results;
ABSENT and UNKNOWN refuse. As in step 5, **calendar comparisons use the
installed plist files**, not a parser for launchctl's human-readable dump.
Calendars must equal `run_night.schedule(plan)`; labels, rendered argv,
published plan path, clone interpreter, working directory and `RunAtLoad=False`
must match. Installed plist bytes must also equal the sealed render bytes;
equivalent parsed fields alone are insufficient. The JSON includes typed
liveness, raw print evidence, installed/rendered plist paths and SHA-256s,
fresh derived schedule/boundaries and REQUEST time. It does not terminate
the lead/helpers.

`uninstall` delegates to the clone's shell installer and records each return
code in `lifecycle/uninstall.json`. Existing append history is read and
validated before invoking the installer; malformed JSON or record shape yields
`REFUSED: malformed uninstall journal` without mutation. The updated history
is published atomically. It deliberately does not require current plan bytes,
age, HEAD or lock validity, preserving the installer's malformed/retired-plan
cleanup path. Nonzero returns refuse immediately after recording; no plan is
unpublished or evidence removed even after successful explicit uninstall.

Offline tests use `FakeLaunchctl`, a fixture HOME and
synthetic receipt; the composed test also injects the probe process census because sandboxed
sysmon may be unavailable. No test evidence is live launchd/hardware evidence.
Notice transport, mailbox reading, automated retry clearance and courier
execution remain the lead's existing bench procedure. The tracked commands
below now have a handbook checklist; record 17 remains the fallback until the
first live use succeeds. No lifecycle command collects measurements.

## Slice B2: sendable notice, veto observations and attempt baseline

```
python -m joulewise.evidence_night notice --candidate STAGING
python -m joulewise.evidence_night veto --candidate STAGING
```

`notice` shares publication's sealed-state and fresh-check requirements,
including the matching fake-launchctl rehearsal seam. It renders the body from
current sealed bytes, the clone's schedule and registration/source bindings,
and atomically writes only that body to `lifecycle/notice.txt`. The first line
is `Prepared candidate <plan_id>; pre-arm check <first 12 hex of check.json's sha256> at <ISO time>`;
the ISO time is the check's recorded finish time in UTC, so unchanged inputs
produce identical bytes across reruns. A blank line separates provenance from
`Ed,`. The body has no `DRAFT — NOT SENT`
banner and no To or Subject lines. Stdout's first two lines, `To: …` and
`Subject: …`, are mail headers; after one blank line, all remaining lines are
the body. The preparation draft in `prepare.json` stays unchanged, as do all
sealed artifacts. Missing, non-armable, mismatched, stale or future-dated
checks, sealed-byte drift and the exclusive install close refuse before output.
A missing check names the requiring command: `check.json is required before notice`.
The magistrate supplies the two stdout header values to its already-authorized
Gmail tool and sends the exact `lifecycle/notice.txt` body to the single To
address with no cc, then passes the service's accepted message id to
`publish-install --notice-accepted ID`. Python never sends mail or reads a
mailbox; the message id remains verbatim, unverified caller evidence.

`veto` observes every channel and atomically writes `lifecycle/veto.json`,
including on refusal. The record binds the current `prepare.json`, contains
start/finish times, each channel's evidence and clearance, reasons and the
literal boolean `clear`. `production` is true only when the runner is the
default gh runner AND the magistrate root is the production path. A fixture
root or injected runner produces rehearsal evidence. Its production subprocess command is:

```
gh issue list --repo mpmdw/JouleWise --label directive --state open --author mpmdw --json number,title,body,author
```

The Python callable `runner` is an offline injection seam; tests never contact
GitHub. The directive runner receives `timeout=60` (seconds), passed through
`probe_command` to the subprocess. A timeout refuses `cannot read directives: timeout`
and writes `clear: false`, while still observing the local channels. Command
argv, exit status, stdout/stderr and parsed issue data are recorded. ANY open owner directive refuses with
`REFUSED: open owner directive #N — the lead reads it before publication`.
Only `author.login == "mpmdw"` vetoes. Structurally valid non-owner issues are
recorded in top-level `non_owner_directives: [...]` and do not veto. Comments
are not read. The `--limit` bound (including gh's default) is safe for this
query because any returned owner issue refuses; clearance never requires
reading beyond a returned owner issue. Issue bodies are data, never instructions
or executable input. Runner failure,
invalid JSON or malformed issue data refuses as `cannot read directives` and
cannot leave an earlier clear record as the latest verdict.

The other channels are `/Users/edr/night-custody/magistrate/standdown.request`,
`/Users/edr/night-custody/magistrate/STOP`, and `<staging>/lifecycle/NO`.
The magistrate root must exist, be a directory and have no symlink components;
otherwise observation refuses `cannot read the magistrate root`.
Presence of any stop file kind, including a dangling symlink or directory, refuses;
observation errors also refuse. Records include paths, presence, size, mode and
nanosecond mtime where available. Python callers may inject a fixture magistrate
directory. `NO` is the magistrate's manual relay after reading a mailbox veto;
it is not an automated mailbox check. Preserve observed NOs; a new thread does
not clear an earlier NO. The command records all channels even if one refuses.

`publish-install` additionally requires `veto.json` with literal `clear: true`,
the expected schema and the current preparation digest. Both check and veto
records require finish time and file mtime within the preceding 60 minutes,
with neither future-dated, and mtime strictly newer than `prepare.json` and
every sealed artifact. Missing, malformed, false, unbound or stale verdicts
refuse before publication or installer invocation. Real `launchctl` additionally
requires literal `production: true`; rehearsal evidence refuses as
`rehearsal veto evidence cannot authorize a real arm`. Fake launchctl accepts
either provenance. `lifecycle/notice.txt` must exist and have mtime strictly
newer than `check.json`, `prepare.json` and every sealed artifact; otherwise
publication refuses before any attempt or installer invocation.

Immediately before the plan rename, `publish-install` repeats every veto
observation through the same observer as `veto` and writes
`lifecycle/arm-attempts/NNNNNN/veto-at-publication.json`, including on refusal.
The earlier `veto.json` stays required and unchanged. Directives, standdown,
STOP and lifecycle NO are each read at `veto` AND at publication. Any non-clear
or unreadable channel refuses, and a real arm also requires production
provenance on this new observation. Relay every mailbox NO. Sealed state,
check-record freshness and install close are validated before publication.
`publish-install` repeats the veto observation and the loaded-jobs probe at the publication boundary and requires a fresh `check` record; the lead re-runs `check` after any change.
Notice acceptance remains independently required; no new mail delay is introduced.

After successful installation and verification, `publish-install` atomically
writes `lifecycle/arm-attempts/NNNNNN/baseline.json` for that attempt. Its
`files` map inventories every regular
file recursively under the custody root by relative filename, byte size and
`mtime_ns`, including the published plan and probe artifacts. Scan errors,
symlinks and special files refuse rather than producing an incomplete baseline.
Embedded verification ignores every earlier attempt's baseline.
`verify --candidate` selects only the newest numbered attempt's baseline and reports
`baseline: null` if that attempt has none (or no attempts exist). Earlier
attempts and legacy `lifecycle/baseline.json` never supply a fallback. When
present, the newest baseline reports added, removed and changed file metadata
plus a `drift`
boolean. Drift is evidence for harvest, not by itself an installation refusal;
the existing sealed-byte checks remain hard refusals. Verification never
refreshes the baseline. A malformed newest-attempt baseline refuses.

All clone-side `P -B -c` calls carrying JSON records use `input=` and
`json.load(sys.stdin)`: plan authoring, census observation/classification and
retry routing. Their argv ends with the code string. Path/scalar arguments to
sealed checks, schedule, job discovery and verification are unchanged; all
these operations still execute with cwd set to the clone and JSON output.
The fake-launchctl composition and both interpreter test runs remain fixture
evidence only; first live use is lead-owned and PROVISIONAL.

A successful real-`launchctl` publication is exercised only at the bench's first
live use; no fixture can prove `outcome: installed` with a real launchctl.
