```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"partial","summary":"Recovery destroys pre-existing jobs.","workspace":{"base_requested":"b678b1dc","base_mode":"exact","head_start":"b678b1dc","head_end":"b678b1dc","upstream_end":"b678b1dc","branch":"feat/2026-09-20-evidence-night-lifecycle"},"pathspec":[],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"blocker"},{"id":"F2","severity":"should_fix"},{"id":"F3","severity":"should_fix"}]},"verification":[],"flags":[{"id":"E1","kind":"environment","level":"nonblocking","text":"Sandbox denies live ps.","needs":"Lead to verify supervisor."}]}
```

## Findings

**F1 — blocker — Recovery destroys pre-existing jobs.** `evidence_night.py:874` unconditionally uninstalls after publication failure; step 0’s existing-job/plist gate is absent. Executed: two foreign plists/loaded labels → check armable → probe rc0 → install rc3 (`night_agent_already_loaded`) → recovery uninstall rc0. Both prior labels AND plists disappeared; journal reported `restored_unpublished`. Require relevant conflicts absent before publication and preserve unowned jobs during recovery. [Evidence](/tmp/jw-b1-extra.log).

**F2 — should_fix — Uninstall loses its outcome on corrupt history.** Lines 899–903 invoke cleanup before reading `uninstall.json`. Injecting `{broken` removed both loaded jobs, then raised `JSONDecodeError`; history stayed corrupt and the new rc was unrecorded. Validate/reserve journaling before mutation. Evidence: same log.

**F3 — should_fix — Raw census hits need not be resolved.** Lines 648–654 use raw census rc but classify a second discovery. Raw `456 /bin/claude foreign-session`, rc0, followed by an observation lacking 456 yielded `armable:true`, `foreign_pids:[]`. Resolve raw-hit ancestry/disappearance or refuse. [Evidence](/tmp/jw-b1-raw.log). Classified foreign/workload/unknown cases correctly refuse despite real-class rc0.

**Bench fidelity crosswalk** (record 17 line numbers):

| Checks | Disposition |
|---|---|
| Step 0:4–12: loaded labels/prior plists | Relevant ownership/conflict replacement missing: F1. |
| Step 0:13–25: four regular nonsymlink retained plans | Discovery/result-or-courier markers replace exact count; UNKNOWN refuses; never deletes. Missing explicit plan-is-regular check. |
| Step 0:26–86: canonical and resident | Preserved; adds H contains census fix; oldest continuous reflog interval. |
| Step 0:87–109; step 4:35–42: census/review/departure | Classifier refusals retained, except F3. Caller repeats check before publication and handles departure. |
| Step 4:7–13,27–42,53–66: stop files twice, directives empty, notice evidence, attempt/history/template fields, retry_allowed | Explicit bench/B2 deferral. ID unverified; classify_abort only routes. Still required outside these commands. |
| Step 4:14–26,33,75–78: clone/H, fresh remote ancestry, snapshot/wrapper checks, rerender | Clone/seals rechecked. Fetch/remote ancestry only at prepare. Sealed render + real preflight/probe replace rerender. |
| Step 4:68–83: target/runway/move/candidate/receipt | Absence/symlinks/device/bytes/close retained; repeated 40min removed as ruled. Real validator retains kind/bindings/label/cleanup/verify-only/no-load/no-collect/<6h. |
| Step 5:5–38: both labels/calendar/argv/plan/interpreter/root/RunAtLoad | All enforced; typed print/plist reads replace list/plutil; schedule comparison follows 30a. |
| Step 5:39–48: baseline/hashes/departure | Digests/deadline returned; night-directory filename/size/mtime baseline omitted. No termination claimed. |

Candidate assertions remain through preparation/seals/clone executors: v2/no-pack, identities/window/class, wrapper/digests/payload, manifest/source/registration, age/schedule. Derived identities replace environment equalities; authoring 40min becomes a default.

Added: owned-candidate/flock, detached clone, lock/interpreter rechecks, full seal/render inventory, prepare SHA, check mtimes, UNKNOWN root/retry refusals, exact plist bytes. Justified by brief/sealing/30a; mtimes are copy-sensitive.

**Executed evidence:** `/tmp` only; source checkout unchanged/clean.

- Focused suite: `/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_night`, cwd `/tmp/jw-b1-review`: **44 tests, OK**. [Log](/tmp/jw-b1-suite.log).
- Live canonical `0959e613` → `canonical checkout does not contain candidate H`. State PID80188; supervisor check → `PermissionError: Operation not permitted: ps`. Injected prompt start + live Git → `canonical checkout does not contain H for supervisor freshness` before reflog; explicitly hybrid evidence. [Log](/tmp/jw-b1-live.log).
- Synthetic canonical contains H at arrival and again +100s: start arrival−1 refuses; arrival+1 passes using oldest arrival. Equality/rewind/re-add tests also pass.
- Wrong-kind and 21,601s-old receipts: real `[probe 0, install 2, uninstall 0]`, then matching-byte restoration. Changed publication: same sequence, `outcome:retained`, `published plan bytes changed or missing`, retained paths named.
- SIGKILL just after rename: publication retained, staging absent, journal `not_published`, commands empty. Resume publication stops without mutation via `FileNotFoundError` (CLI error 1 rather than refusal 2); resumed check refuses sealed state. Lead recovery required.
- Both labels tested: one absent → `is ABSENT`; equivalent binary plist → `installed plist bytes differ from render`; minute+1 → `calendar differs`; RunAtLoad true → `RunAtLoad differs`; staged plan → `arguments differ`. All refuse. [Exact tails and recovery records](/tmp/jw-b1-harness.log).
- Touch after check → `check.json is not newer than every sealed artefact`: **mtime_ns** ordering, with separate digest validation. Removing line804 guard kills `LifecycleTests.test_publish_requires_check_armable_freshness_notice_and_sealed_bytes:673` (`"newer" does not match ...`); restored test passes. [Mutant](/tmp/jw-b1-mutant.log).
- Real fixture check adds only check.json; prior bytes/mtimes unchanged. Successful uninstall retains plan; nonzero-only-record regression passes.

**Argv inventory:** [76 exact lifecycle phase/argv records, including Python bodies](/tmp/jw-b1-lab/argv-distinct.jsonl); [normalized list](/tmp/jw-b1-lab/argv-summary.txt). Captured via parent/child subprocess hooks:

- Common: Git HEAD/branch/clean-status; eight tracked-file `git show` queries; Python identity/fingerprint/seal/schedule code; `zsh -n chain.zsh`.
- Check: census-fix/H/canonical ancestry, canonical `--no-optional-locks status --porcelain -uno`, bracketed `pgrep -lf`. Supervisor probes additionally use `ps -o pid=,lstart=,command= -p 80188`, reflog and per-entry ancestry.
- Publish/install: installer shell `--plan P --python PY --launchctl-bin F`, with/without `--launchd-probe`; driver `preflight`; fake probe print/bootstrap/bootout; both job bootstraps/prints; verification code. Recovery adds uninstall.
- Verify: common checks plus verification code and both fake label prints.
- Uninstall: installer `--plan P --uninstall --launchctl-bin F`; fake bootout/print of both jobs and probe lookup.

No real launchctl/mail/network/collection. Observer/probe-census/lock verification injected. Replay `/tmp/jw-b1-{harness,extra,trace,live}.py` with supplied interpreter, cwd `/tmp/jw-b1-review`, fresh absolute `JW_B1_LAB` under `/tmp`.

**Same-signature statements:** “entry point silently diverges from bench procedure”: **OPEN**, F1/F3. “Evidence-affecting side effect without a refusal path”: **OPEN**, F1 destroys unowned jobs despite refusing; F2 loses cleanup outcome. Lead should scope fixes and replay before approval.

## Residual risk

Live supervisor start remains unverified: sandbox denies ps. Brief30/30a absent; supplied authority used. Fixtures prove composition only. Full canonical suite not run for this bounded read-only review.